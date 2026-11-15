"""Publish the positive contextual assertions selected by saved judgments."""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

from gnd.anchors import read_regular_path, strict_json
from gnd.artifacts import ArtifactError, canonical_json_bytes, publish_directory_once, sha256_hex
from gnd.disclosure import ENVIRONMENT as DISCLOSURE_ENV
from gnd.process import ProcessLimits, run_bounded_process

from .assurance_report import Refusal

SCHEMA = "literature-assertion-admission/1"
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


def _support(row: dict, target: dict | None) -> str | None:
    missing = row["condition"].strip().casefold() in ABSENT_CONDITIONS
    if row["qualification"] == "conditional" and missing:
        return "missing-condition"
    if row["qualification"] == "unqualified" and not missing:
        return "qualification-mismatch"
    if target is None:
        return "missing"
    if target["admitted"]:
        return None
    verdicts = {item["verdict"] for item in target["judgments"]}
    for verdict, reason in (("missing", "missing"), ("reject", "rejected"), ("abstain", "abstained")):
        if verdict in verdicts:
            return reason
    return "approval-or-mechanical-floor"


def project(subject: Any, targets: Any) -> tuple[dict, dict]:
    """Project accepted positive occurrences and their original identity links."""
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
        if effective is None and (row["polarity"], row["attribution"]) != ("asserts", "own-finding"):
            effective = "negated" if row["polarity"] == "negates" else row["attribution"]
        for stage, reason in (("semantic-support", support), ("positive-own-findings", effective)):
            stages[stage].append({"index": index, "status": "pass" if reason is None else "fail", "reason": reason})
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


def _judgments(snapshots: dict[str, bytes], trusted_root: Path) -> tuple[dict, bytes]:
    """Run the standard judgment route with the immutable input snapshot."""
    with tempfile.TemporaryDirectory(prefix="gnd-assertions-") as folder:
        cwd = Path(folder).resolve()
        for name, raw in snapshots.items():
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


def admit(model: Path, raw: Path, policy: Path, receipts: Path, trusted_root: Path, out: Path) -> dict:
    """Check saved opinion bytes, project supported rows and publish one bound result."""
    out = out.absolute()
    if out.exists() or out.is_symlink():
        raise Refusal("output:exists")
    snapshots = {
        name: read_regular_path(path, label=name, max_bytes=(1 << 20) if name == POLICY else CAP)
        for name, path in ((MODEL, model), (RAW, raw), (POLICY, policy), (RECEIPTS, receipts))
    }
    judgment, report_raw = _judgments(snapshots, trusted_root)
    subject = strict_json(snapshots[RAW], max_bytes=CAP, too_large="input:population-cap")
    population, stages = project(subject, judgment.get("targets"))
    admitted_raw = canonical_json_bytes(population)
    record = {
        "schema": SCHEMA, "model_sha256": sha256_hex(snapshots[MODEL]), "raw_sha256": sha256_hex(snapshots[RAW]),
        "policy_sha256": sha256_hex(snapshots[POLICY]), "receipts_sha256": sha256_hex(snapshots[RECEIPTS]),
        "judgment_report_sha256": sha256_hex(report_raw), "admitted_sha256": sha256_hex(admitted_raw), "stages": stages,
    }
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
