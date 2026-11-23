"""Publish the positive contextual assertions selected by saved judgments."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import re
import sys
import tempfile
from collections import deque
from pathlib import Path, PurePosixPath
from typing import Any

from gnd.anchors import read_regular_path, strict_json
from gnd.artifacts import ArtifactError, canonical_json_bytes, publish_directory_once, sha256_hex
from gnd.disclosure import ENVIRONMENT as DISCLOSURE_ENV
from gnd.process import ProcessLimits, run_bounded_process
from gnd.synth.identity import scalar_identity

from .assurance_report import Refusal

SCHEMA = "literature-assertion-admission/1"
SHAPED_SCHEMA = "literature-assertion-admission/2"
SHAPE_FORMAT = "literature-assertion-shape/1"
MAX_ROWS, MAX_ROWS_CEILING = 16384, 65536
RULES_FORMAT = "literature-admission-rules/1"
MAX_REQUIREMENTS = 64
RULE_NAME = re.compile(r"[a-z][a-z0-9-]{0,63}\Z")
STATEMENT = "assertion_statement"
WORK = "assertion_names_work"
PASSAGE = "assertion_names_passage"
MODEL, RAW, POLICY, RECEIPTS = "model.orm.yaml", "raw.population.json", "policy.json", "receipts.json"
REPORT, ADMITTED, RECORD = "judgment-report.json", "admitted.population.json", "admission.json"
CAP = 10 << 20
REPORT_CAP = 16 << 20
MAX_TARGETS = 1024
ABSENT_CONDITIONS = frozenset({"unspecified", "none", "n/a"})
ROLES = {
    "passage", "work", "version", "predicate", "actor", "actor_kind", "object", "object_kind",
    "qualification", "condition", "regime", "experiment", "polarity", "attribution",
}
TAGS = {
    "actor_kind": ("sense", "mention"), "object_kind": ("sense", "mention"),
    "qualification": ("conditional", "unqualified"), "polarity": ("asserts", "negates"),
    "attribution": ("own-finding", "baseline-comparison", "speculation", "cites-other-work"),
}
DEFAULT_RULES = {"format": RULES_FORMAT, "requirements": [
    {"id": "positive", "fact_type": STATEMENT, "role": "polarity", "admissible": ["asserts"],
     "reasons": [{"value": "negates", "reason": "negated"}]},
    {"id": "own-finding", "fact_type": STATEMENT, "role": "attribution", "admissible": ["own-finding"],
     "reasons": [{"value": value, "reason": value}
                 for value in ("baseline-comparison", "speculation", "cites-other-work")]},
]}
LIMITS = ProcessLimits(timeout_seconds=90, terminate_grace_seconds=1, stdin_limit_bytes=0,
                       stdout_limit_bytes=REPORT_CAP, stderr_limit_bytes=128 << 10,
                       total_output_limit_bytes=REPORT_CAP + (128 << 10))


def _rows(value: Any, roles: set[str]) -> list[dict]:
    if not isinstance(value, list) or len(value) > MAX_TARGETS:
        raise Refusal("input:invalid-contextual-population")
    for row in value:
        if (not isinstance(row, dict) or set(row) != roles
                or not all(isinstance(item, str) and item.strip() for item in row.values())):
            raise Refusal("input:invalid-contextual-population")
    return value


def _identities(works: list[dict], passages: list[dict]) -> dict[tuple[str, str], str]:
    work_by_id = {row["assertion"]: row["work"] for row in works}
    passage_by_id = {row["assertion"]: row["passage"] for row in passages}
    if len(work_by_id) != len(works) or len(passage_by_id) != len(passages) or work_by_id.keys() != passage_by_id.keys():
        raise Refusal("input:assertion-identities")
    by_location = {(work, passage_by_id[identifier]): identifier for identifier, work in work_by_id.items()}
    if len(by_location) != len(work_by_id):
        raise Refusal("input:assertion-identities")
    return by_location


def _targets(items: Any, count: int) -> dict[int, dict]:
    if not isinstance(items, list) or len(items) > MAX_TARGETS:
        raise Refusal("judgments:invalid-result")
    by_index = {}
    for item in items:
        if not isinstance(item, dict) or item.get("fact_type") != STATEMENT:
            raise Refusal("judgments:invalid-result")
        index, judgments = item.get("index"), item.get("judgments")
        if (type(index) is not int or not 0 <= index < count or index in by_index
                or type(item.get("admitted")) is not bool or not isinstance(judgments, list) or len(judgments) > 32
                or not all(isinstance(j, dict) and j.get("verdict") in ("approve", "reject", "abstain", "missing")
                           for j in judgments)):
            raise Refusal("judgments:invalid-result")
        by_index[index] = item
    return by_index


def _target_reason(target: dict | None) -> str | None:
    """Map one target's judgment to a support reason; None when it is admitted."""
    if target is None:
        return "missing"
    if target["admitted"]:
        return None
    verdicts = {item["verdict"] for item in target["judgments"]}
    for verdict, reason in (("missing", "missing"), ("reject", "rejected"), ("abstain", "abstained")):
        if verdict in verdicts:
            return reason
    return "approval-or-mechanical-floor"


def _support(row: dict, target: dict | None) -> str | None:
    missing = row["condition"].strip().casefold() in ABSENT_CONDITIONS
    if row["qualification"] == "conditional" and missing:
        return "missing-condition"
    if row["qualification"] == "unqualified" and not missing:
        return "qualification-mismatch"
    return _target_reason(target)


def _rules(value: Any, roles: dict[str, set[str]]) -> list[dict]:
    """Check a rules document against the fact types its requirements may name, and normalize it."""
    if (not isinstance(value, dict) or set(value) != {"format", "requirements"} or value["format"] != RULES_FORMAT
            or not isinstance(value["requirements"], list) or not 1 <= len(value["requirements"]) <= MAX_REQUIREMENTS):
        raise Refusal("rules:invalid")
    requirements, ids = [], set()
    for item in value["requirements"]:
        if (not isinstance(item, dict) or set(item) != {"id", "fact_type", "role", "admissible", "reasons"}
                or not isinstance(item["id"], str) or RULE_NAME.fullmatch(item["id"]) is None or item["id"] in ids
                or not isinstance(item["fact_type"], str) or not isinstance(item["role"], str)
                or not isinstance(item["admissible"], list) or not item["admissible"]
                or not isinstance(item["reasons"], list)):
            raise Refusal("rules:invalid")
        ids.add(item["id"])
        admissible = [_identity(entry) for entry in item["admissible"]]
        reasons = {}
        for entry in item["reasons"]:
            if (not isinstance(entry, dict) or set(entry) != {"value", "reason"}
                    or not isinstance(entry["reason"], str) or RULE_NAME.fullmatch(entry["reason"]) is None):
                raise Refusal("rules:invalid")
            reasons[_identity(entry["value"])] = entry["reason"]
        if len(set(admissible)) != len(admissible) or len(reasons) != len(item["reasons"]) or set(reasons) & set(admissible):
            raise Refusal("rules:invalid")
        if item["fact_type"] not in roles:
            raise Refusal("rules:unknown-fact-type")
        if item["role"] not in roles[item["fact_type"]]:
            raise Refusal("rules:unknown-role")
        requirements.append({"id": item["id"], "fact_type": item["fact_type"], "role": item["role"],
                             "admissible": frozenset(admissible), "reasons": reasons})
    return requirements


def _evaluate_rules(requirements: list[dict], rows_of) -> str | None:
    """The one evaluator: the first requirement an assertion fails gives its reason; None when it passes all.

    An assertion satisfies a requirement when it has at least one row of the named fact type and every
    such row has an admissible value; the reason is the one declared for the offending value, else the
    requirement's ID.
    """
    for requirement in requirements:
        rows = rows_of(requirement["fact_type"])
        if not rows:
            return requirement["id"]
        for row in rows:
            key = _identity(row[requirement["role"]])
            if key not in requirement["admissible"]:
                return requirement["reasons"].get(key, requirement["id"])
    return None


def project(subject: Any, targets: Any, *, requirements: list[dict] | None = None,
            policy_status: str = "fail") -> tuple[dict, dict]:
    """Project accepted positive occurrences and their original identity links.

    ``requirements`` default to the packaged rules (polarity, then attribution); ``policy_status`` is the
    status of a supported statement that fails one, ``fail`` in a ``/1`` record and ``policy-refused`` in a
    ``/2`` record.
    """
    requirements = _rules(DEFAULT_RULES, {STATEMENT: ROLES}) if requirements is None else requirements
    if not isinstance(subject, dict) or not isinstance(subject.get("population"), dict):
        raise Refusal("input:invalid-contextual-population")
    facts = subject.get("facts")
    if not isinstance(facts, dict) or set(facts) != {STATEMENT, WORK, PASSAGE}:
        raise Refusal("input:invalid-contextual-population")
    statements = _rows(facts[STATEMENT], ROLES)
    works = _rows(facts[WORK], {"assertion", "work"})
    passages = _rows(facts[PASSAGE], {"assertion", "passage"})
    identities = _identities(works, passages)
    locations = {(row["work"], row["passage"]) for row in statements}
    if locations != identities.keys() or len(locations) != len(statements):
        raise Refusal("input:assertion-identities")
    verified = _targets(targets, len(statements))
    stages: dict[str, list[dict]] = {"semantic-support": [], "positive-own-findings": []}
    kept, included = [], set()
    for index, row in enumerate(statements):
        if any(row[tag] not in allowed for tag, allowed in TAGS.items()):
            raise Refusal("input:invalid-contextual-population")
        support = _support(row, verified.get(index))
        effective = support
        if effective is None:
            effective = _evaluate_rules(requirements, lambda name, row=row: [row] if name == STATEMENT else [])
        stages["semantic-support"].append(
            {"index": index, "status": "pass" if support is None else "fail", "reason": support})
        stages["positive-own-findings"].append({
            "index": index, "status": "pass" if effective is None else "fail" if support is not None else policy_status,
            "reason": effective})
        if effective is None:
            kept.append(row)
            included.add(identities[row["work"], row["passage"]])
    return {
        **({"format_version": subject["format_version"]} if "format_version" in subject else {}),
        "population": {**subject["population"], "source": "tool-output", "producer": SCHEMA,
                       "covers": [STATEMENT, WORK, PASSAGE]},
        "instances": {},
        "facts": {
            STATEMENT: kept,
            WORK: [row for row in works if row["assertion"] in included],
            PASSAGE: [row for row in passages if row["assertion"] in included],
        },
    }, stages


def _shape(value: Any) -> tuple[str, tuple[str, ...]]:
    if (not isinstance(value, dict) or set(value) != {"format", "assertion", "follow"}
            or value["format"] != SHAPE_FORMAT or not isinstance(value["assertion"], str)
            or not isinstance(value["follow"], list)
            or not all(isinstance(name, str) for name in value["follow"])
            or len(set(value["follow"])) != len(value["follow"]) or value["assertion"] in value["follow"]):
        raise Refusal("shape:invalid")
    return value["assertion"], tuple(value["follow"])


def _max_rows(value: Any) -> int:
    if value is None:
        return MAX_ROWS
    if type(value) is not int or not 1 <= value <= MAX_ROWS_CEILING:
        raise Refusal("input:max-rows")
    return value


def _include_paths(model_bytes: bytes) -> list[str]:
    """The relative paths of the includes a model root declares."""
    from gnd.model._includes import bytes_declare_includes
    from gnd.model._parsing import parse_model_document

    if not bytes_declare_includes(model_bytes, source=MODEL):
        return []
    document = parse_model_document(model_bytes, source=MODEL)
    entries = document.get("includes", []) if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise Refusal("input:include-path")
    paths = []
    for entry in entries:
        path = entry.get("path") if isinstance(entry, dict) else None
        parts = PurePosixPath(path).parts if isinstance(path, str) else ()
        if (not parts or PurePosixPath(path).is_absolute() or ".." in parts or "\\" in path
                or path in (MODEL, RAW, POLICY, RECEIPTS) or path in paths):
            raise Refusal("input:include-path")
        paths.append(path)
    return paths


def _model_document(snapshots: dict[str, bytes], includes: dict[str, bytes]) -> dict:
    """The model the judgment route checks, as plain data, composed for an include root."""
    from gnd.model import (
        ModelLoadError,
        ModelValidationError,
        load_model_bytes,
        load_model_bytes_composed,
    )

    with tempfile.TemporaryDirectory(prefix="gnd-assertion-model-") as folder:
        root = Path(folder).resolve()
        try:
            if includes:
                for name, raw in includes.items():
                    (root / name).parent.mkdir(parents=True, exist_ok=True)
                    (root / name).write_bytes(raw)
                loaded = load_model_bytes_composed(snapshots[MODEL], source=MODEL, root=root, bind_references=False)
            else:
                loaded = load_model_bytes(snapshots[MODEL], source=MODEL)
        except (ModelLoadError, ModelValidationError, ValueError, TypeError, OSError) as error:
            raise Refusal("input:model") from error
    return loaded.model_dump(mode="json", exclude_none=True)


def _identity(value: Any) -> tuple:
    """A handle's identity as the checker keeps it: booleans, numbers and strings apart, 1 and 1.0 one."""
    if isinstance(value, (dict, list)):
        return ("json", canonical_json_bytes(value))
    return scalar_identity(value)


def _attached_roles(model: dict, shape: Any) -> dict[str, set[str]]:
    """The role names of each fact type a shape's assertion type plays a role in."""
    assertion, _ = _shape(shape)
    return {item["id"]: {role["role_name"] for role in item["roles"]} for item in model.get("fact_types", [])
            if any(role["object_type"] == assertion for role in item["roles"])}


def project_shaped(subject: Any, targets: Any, model: dict, shape: Any, max_rows: int = MAX_ROWS, *,
                   requirements: list[dict] | None = None) -> tuple[dict, dict]:
    """Admit the assertions of a caller-named entity type, with every attached and followed row they keep."""
    assertion, follow = _shape(shape)
    kinds = {item["id"]: item["kind"] for item in model.get("object_types", [])}
    if kinds.get(assertion) != "entity":
        raise Refusal("shape:unknown-assertion")
    if any(kinds.get(name) != "entity" for name in follow):
        raise Refusal("shape:unknown-follow")
    fact_types = model.get("fact_types", [])
    if any(item.get("objectified_as") == assertion for item in fact_types):
        raise Refusal("shape:objectified-assertion")
    roles = {item["id"]: [(role["role_name"], role["object_type"]) for role in item["roles"]] for item in fact_types}
    attached = [name for name, pairs in roles.items() if any(kind == assertion for _, kind in pairs)]
    if not attached:
        raise Refusal("shape:no-attached-facts")
    followed = set(follow)
    attached_names = set(attached)
    covers = [name for name, pairs in roles.items()
              if name in attached_names or any(kind in followed for _, kind in pairs)]
    if not isinstance(subject, dict) or not isinstance(subject.get("population"), dict):
        raise Refusal("input:invalid-contextual-population")
    facts = subject.get("facts")
    if not isinstance(facts, dict):
        raise Refusal("input:invalid-contextual-population")
    rows = {}
    for name in covers:
        value = facts.get(name, [])
        names = {role for role, _ in roles[name]}
        if not isinstance(value, list) or not all(isinstance(row, dict) and set(row) == names for row in value):
            raise Refusal("input:invalid-contextual-population")
        rows[name] = value
    if sum(map(len, rows.values())) > max_rows:
        raise Refusal("input:row-cap")
    if not isinstance(targets, list) or len(targets) > MAX_TARGETS:
        raise Refusal("judgments:invalid-result")
    seen, by_assertion, order, owned = set(), {}, {}, {}
    holders = {name: [role for role, kind in roles[name] if kind == assertion] for name in covers}
    for name in attached:
        for row in rows[name]:
            for role in holders[name]:
                key = _identity(row[role])
                order.setdefault(key, (len(order), row[role]))
                owned.setdefault((key, name), []).append(row)
    for item in targets:
        if not isinstance(item, dict) or item.get("fact_type") not in roles:
            raise Refusal("judgments:invalid-result")
        name, index, judgments = item["fact_type"], item.get("index"), item.get("judgments")
        if name not in attached_names:
            raise Refusal("judgments:target-outside-shape")
        if (type(index) is not int or not 0 <= index < len(rows[name]) or (name, index) in seen
                or type(item.get("admitted")) is not bool or not isinstance(judgments, list) or len(judgments) > 32
                or not all(isinstance(j, dict) and j.get("verdict") in ("approve", "reject", "abstain", "missing")
                           for j in judgments)):
            raise Refusal("judgments:invalid-result")
        seen.add((name, index))
        for role in holders[name]:
            by_assertion.setdefault(_identity(rows[name][index][role]), []).append(item)
    reasons, policy = {}, {}
    for key in sorted(order, key=lambda item: order[item][0]):
        found = by_assertion.get(key)
        reasons[key] = "missing" if not found else next(
            (reason for reason in map(_target_reason, found) if reason is not None), None)
        if reasons[key] is None and requirements is not None:
            policy[key] = _evaluate_rules(requirements, lambda name, key=key: owned.get((key, name), []))
    admitted = {key for key, reason in reasons.items() if reason is None and policy.get(key) is None}
    index = {}
    for name in covers:
        for position, row in enumerate(rows[name]):
            for role, kind in roles[name]:
                if kind in followed:
                    index.setdefault((kind, _identity(row[role])), []).append((name, position))
    kept, queue = set(), deque()

    def keep(name, position):
        row = rows[name][position]
        if (name, position) in kept or any(_identity(row[role]) not in admitted for role in holders[name]):
            return
        kept.add((name, position))
        queue.extend((kind, _identity(row[role])) for role, kind in roles[name] if kind in followed)

    for name in attached:
        for position in range(len(rows[name])):
            keep(name, position)
    visited = set()
    while queue:
        instance = queue.popleft()
        if instance in visited:
            continue
        visited.add(instance)
        for name, position in index.get(instance, ()):
            keep(name, position)
    population = {
        **({"format_version": subject["format_version"]} if "format_version" in subject else {}),
        "population": {**subject["population"], "source": "tool-output", "producer": SHAPED_SCHEMA, "covers": covers},
        "instances": {},
        "facts": {name: [row for position, row in enumerate(rows[name]) if (name, position) in kept] for name in covers},
    }
    stages = {"semantic-support": [{"assertion": order[key][1], "status": "pass" if reason is None else "fail",
                                    "reason": reason} for key, reason in reasons.items()]}
    if requirements is not None:
        stages["admission-rules"] = [
            {"assertion": order[key][1], "status": "fail", "reason": reason} if reason is not None
            else {"assertion": order[key][1], "status": "pass" if policy[key] is None else "policy-refused",
                  "reason": policy[key]}
            for key, reason in reasons.items()]
    return population, stages


def _judgments(snapshots: dict[str, bytes], trusted_root: Path) -> tuple[dict, bytes]:
    """Run the standard judgment route with the immutable input snapshot."""
    with tempfile.TemporaryDirectory(prefix="gnd-assertions-") as folder:
        cwd = Path(folder).resolve()
        for name, raw in snapshots.items():
            (cwd / name).parent.mkdir(parents=True, exist_ok=True)
            (cwd / name).write_bytes(raw)
        argv = (sys.executable, "-m", "gnd", "judgments", "check", MODEL, RAW,
                "--policy", POLICY, "--receipts", RECEIPTS, "--trusted-root", str(trusted_root.absolute()),
                "--format", "json")
        environment = ({} if DISCLOSURE_ENV not in os.environ else {DISCLOSURE_ENV: os.environ[DISCLOSURE_ENV]})
        done = asyncio.run(run_bounded_process(argv, cwd=cwd, env=environment, limits=LIMITS,
                                               disclosed_names=frozenset({DISCLOSURE_ENV})))
    if done.return_code not in (0, 1) or done.stdout_truncated or not done.process_group_cleaned:
        raise Refusal("judgments:refused")
    report = strict_json(done.stdout, max_bytes=REPORT_CAP, too_large="judgments:report-cap")
    if (not isinstance(report, dict) or report.get("command") != "judgments"
            or type(report.get("outcome")) is not int or report["outcome"] != done.return_code
            or report.get("error") is not None or not isinstance(report.get("judgment_policy"), dict)):
        raise Refusal("judgments:invalid-result")
    judgment = report["judgment_policy"]
    if judgment.get("verification_contract") != "consumer-pinned-bytes-v1":
        raise Refusal("judgments:consumer-pins-required")
    _verify_report_inputs(judgment, snapshots)
    return judgment, done.stdout


def _verify_report_inputs(judgment: dict, snapshots: dict[str, bytes]) -> None:
    policy = strict_json(snapshots[POLICY], max_bytes=1 << 20, too_large="input:policy-cap")
    receipt_bytes = snapshots[RECEIPTS]
    receipts = strict_json(receipt_bytes, max_bytes=CAP, too_large="input:receipt-cap")
    if not receipts["receipts"]:
        receipt_bytes = canonical_json_bytes({"schema_version": 1, "receipts": []})
    targets = judgment.get("targets")
    if (judgment.get("policy_sha256") != sha256_hex(snapshots[POLICY])
            or judgment.get("receipts_sha256") != sha256_hex(receipt_bytes)
            or not isinstance(targets, list)
            or not all(isinstance(item, dict) for item in targets)
            or [{"fact_type": item.get("fact_type"), "index": item.get("index")} for item in targets] != policy["targets"]):
        raise Refusal("judgments:binding-mismatch")


def admit(model: Path, raw: Path, policy: Path, receipts: Path, trusted_root: Path, out: Path, *,
          shape: dict | None = None, rules: dict | None = None, max_targets: int | None = None,
          max_rows: int | None = None) -> dict:
    """Check saved opinion bytes, project supported rows and publish one bound result.

    With ``shape`` (``{"format": SHAPE_FORMAT, "assertion": ENTITY, "follow": [ENTITY, ...]}``) the
    assertions are the instances of a caller-named entity type, identified by their own handle, and a
    ``literature-assertion-admission/2`` record is written; without it, the packaged shape. ``rules``
    (``literature-admission-rules/1``) replace the packaged comparison, and ``max_targets`` (1 to 1,024)
    lowers the target cap; either one also writes ``/2``.
    """
    out = out.absolute()
    if out.exists() or out.is_symlink():
        raise Refusal("output:exists")
    if shape is None and max_rows is not None:
        raise Refusal("input:max-rows")
    if shape is not None:
        _shape(shape)
    rows_cap = _max_rows(max_rows)
    if max_targets is not None and (type(max_targets) is not int or not 1 <= max_targets <= MAX_TARGETS):
        raise Refusal("input:max-targets")
    shaped = any(value is not None for value in (shape, rules, max_targets, max_rows))
    try:
        snapshots = {
            name: read_regular_path(path, label=name, max_bytes=(1 << 20) if name == POLICY else CAP)
            for name, path in ((MODEL, model), (RAW, raw), (POLICY, policy), (RECEIPTS, receipts))
        }
    except (ArtifactError, OSError) as error:
        if shape is None:
            raise
        raise Refusal("input:read") from error
    includes = {}
    if shape is not None:
        base = Path(model).absolute().parent
        try:
            includes = {path: read_regular_path(base / path, label="include", max_bytes=CAP)
                        for path in _include_paths(snapshots[MODEL])}
        except (ArtifactError, OSError) as error:
            raise Refusal("input:include-read") from error
    document = _model_document(snapshots, includes) if shape is not None else None
    requirements = None
    if rules is not None:
        allowed = {STATEMENT: ROLES} if shape is None else _attached_roles(document, shape)
        requirements = _rules(rules, allowed)
    if max_targets is not None:
        targets = strict_json(snapshots[POLICY], max_bytes=1 << 20, too_large="input:policy-cap")
        if not isinstance(targets, dict) or not isinstance(targets.get("targets"), list) \
                or len(targets["targets"]) > max_targets:
            raise Refusal("input:max-targets")
    judgment, report_raw = _judgments({**snapshots, **includes}, trusted_root)
    subject = strict_json(snapshots[RAW], max_bytes=CAP, too_large="input:population-cap")
    if shape is None:
        population, stages = project(subject, judgment.get("targets"), requirements=requirements,
                                     policy_status="policy-refused" if shaped else "fail")
    else:
        population, stages = project_shaped(subject, judgment.get("targets"), document, shape, rows_cap,
                                            requirements=requirements)
    admitted_raw = canonical_json_bytes(population)
    record = {
        "schema": SCHEMA, "model_sha256": sha256_hex(snapshots[MODEL]), "raw_sha256": sha256_hex(snapshots[RAW]),
        "policy_sha256": sha256_hex(snapshots[POLICY]), "receipts_sha256": sha256_hex(snapshots[RECEIPTS]),
        "judgment_report_sha256": sha256_hex(report_raw), "admitted_sha256": sha256_hex(admitted_raw), "stages": stages,
    }
    if shaped:
        record.update({
            "schema": SHAPED_SCHEMA, "includes": {path: sha256_hex(raw) for path, raw in includes.items()},
            "shape": "packaged" if shape is None else "caller",
            "shape_sha256": None if shape is None else sha256_hex(canonical_json_bytes(shape)),
            "rules_sha256": None if rules is None else sha256_hex(canonical_json_bytes(rules)),
            "max_targets": MAX_TARGETS if max_targets is None else max_targets,
            "max_rows": None if shape is None else rows_cap,
        })
    publish_directory_once(
        out.parent, out.name, {RAW: snapshots[RAW], REPORT: report_raw, ADMITTED: admitted_raw,
                               RECORD: canonical_json_bytes(record)},
        manifest_name=RECORD, max_file_bytes=REPORT_CAP, max_total_bytes=4 * REPORT_CAP,
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for label in ("model", "raw", "policy", "receipts", "trusted_root"):
        parser.add_argument(label, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        admit(args.model, args.raw, args.policy, args.receipts, args.trusted_root, args.out)
    except Refusal as error:
        print(json.dumps({"exit_code": 3, "reason": error.reason}))
        return 3
    except (ArtifactError, OSError, ValueError, UnicodeError, RecursionError):
        print(json.dumps({"exit_code": 3, "reason": "input-or-output:invalid"}))
        return 3
    print(json.dumps({"exit_code": 0}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
