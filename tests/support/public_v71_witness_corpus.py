"""Materialize the independently authored v7.1 witness corpus in temporary paths.

No certificate constructor here calls a witness producer or replay kernel. Existing
loaders are used only to bind pre-feature model/population identities.
"""

from __future__ import annotations

import copy
import hashlib
import importlib
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from ruamel.yaml import YAML

from gnd import api
from gnd.artifacts import canonical_json_bytes
from gnd.model import load_model
from gnd.population import load_population
from gnd.references import reference_model_digest

ROOT = Path(__file__).resolve().parents[2]
# The complete frozen generic corpus is unpacked without changing its member bytes.
import gzip
import tempfile

_CORPUS_TEMP = tempfile.TemporaryDirectory(prefix="gnd-v71-witness-")
_CORPUS_ARCHIVE = ROOT / "tests/fixtures/public-v71-witness/corpus.json.gz"
if _CORPUS_ARCHIVE.stat().st_size > 65536:
    raise ValueError("witness corpus archive exceeds its original closure bound")
with gzip.open(_CORPUS_ARCHIVE, "rb") as _stream:
    _raw = _stream.read(262145)
if len(_raw) > 262144 or hashlib.sha256(_raw).hexdigest() != "397d66a09359a1a2b0cc63817a740424e1e2f5f1f7717601cae51d85d8a2d8f8":
    raise ValueError("witness corpus closure mismatch")
_members = json.loads(_raw)
if set(_members) != {'dispatch/recursive.witness.json', 'inputs.json', 'dispatch/direct.witness.json', 'answers.json', 'manifest.json', 'release/legacy-check.json', 'dispatch/model.orm.yaml', 'dispatch/candidate.pop.json', 'release/candidate.pop.json', 'release/direct.witness.json', 'release/references/links.pop.json', 'answers.md', 'dispatch/references/links.pop.json', 'release/targets.json', 'dispatch/legacy-check.json', 'release/recursive.witness.json', 'release/model.orm.yaml', 'README.md', 'dispatch/targets.json'}:
    raise ValueError("witness corpus member roster mismatch")
CORPUS = Path(_CORPUS_TEMP.name) / "tests/fixtures/v71/phase3"
for _relative, _text in _members.items():
    _path = CORPUS / _relative
    _path.parent.mkdir(parents=True, exist_ok=True)
    _path.write_bytes(_text.encode("utf-8"))
INPUTS = json.loads((CORPUS / "inputs.json").read_text())
ANSWERS = {r["id"]: r for r in json.loads((CORPUS / "answers.json").read_text())["cases"]}


def scalar(value: object, primitive: str = "String") -> dict:
    return {"primitive": primitive, "value": value}


def write_json(path: Path, document: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document, ensure_ascii=False, indent=2) + "\n")


def edit(document: dict, changes: list[dict]) -> None:
    for change in changes:
        parts = change["path"].split("/")[1:]
        cursor = document
        for key in parts[:-1]:
            cursor = cursor[int(key)] if isinstance(cursor, list) else cursor[key]
        key = int(parts[-1]) if isinstance(cursor, list) else parts[-1]
        if change.get("remove"):
            del cursor[key]
        else:
            cursor[key] = copy.deepcopy(change["value"])


def bundle(domain: str, root: Path) -> dict[str, Any]:
    original = CORPUS / domain
    root = root.resolve()
    root.mkdir(parents=True, exist_ok=True)
    return {
        "root": root,
        "ids": copy.deepcopy(INPUTS["domains"][domain]),
        "model": YAML(typ="safe").load((original / "model.orm.yaml").read_text()),
        "candidate": json.loads((original / "candidate.pop.json").read_text()),
        "reference": json.loads((original / "references/links.pop.json").read_text()),
        "certificate": json.loads((original / "recursive.witness.json").read_text()),
        "request": json.loads((original / "targets.json").read_text()),
    }


def save(b: dict, *, bind: bool = True) -> None:
    root = b["root"]
    if b["model"].get("reference_populations"):
        write_json(root / "references/links.pop.json", b["reference"])
        digest = hashlib.sha256((root / "references/links.pop.json").read_bytes()).hexdigest()
        b["model"]["reference_populations"][0]["sha256"] = digest
    write_json(root / "model.orm.yaml", b["model"])
    write_json(root / "candidate.pop.json", b["candidate"])
    write_json(root / "targets.json", b["request"])
    if bind:
        m = load_model(root / "model.orm.yaml")
        p = load_population(root / "candidate.pop.json", model=m)
        b["certificate"]["binding"] = {
            "model_digest": reference_model_digest(m),
            "candidate_digest": "sha256:"
            + hashlib.sha256(canonical_json_bytes(p.model_dump(mode="json"))).hexdigest(),
            "references": [
                {"id": d["id"], "raw_sha256": d["sha256"]}
                for d in b["model"].get("reference_populations", [])
            ],
        }
    (root / "certificate.json").write_text(
        json.dumps(b["certificate"], ensure_ascii=False, separators=(",", ":")) + "\n"
    )


def target(b: dict, values: list, primitive: str = "String") -> dict:
    return {"fact_type": b["ids"]["reach"], "tuple": [scalar(v, primitive) for v in values]}


def set_proof(b: dict, nodes: list[dict], values: list, primitive: str = "String") -> None:
    for index, node in enumerate(nodes):
        node["id"] = index
    b["certificate"]["nodes"] = nodes
    b["certificate"]["results"] = [
        {
            "request_index": 0,
            "target": target(b, values, primitive),
            "status": "proved",
            "reason": None,
            "root": len(nodes) - 1,
        }
    ]
    b["request"] = {"version": 1, "targets": [target(b, values, primitive)]}


def require_lane() -> None:
    assert callable(getattr(api, "witness", None)), "Phase 3 witness API is absent"
    assert callable(getattr(api, "replay", None)), "Phase 3 replay API is absent"


def replay(b: dict) -> dict:
    save(b, bind=False)
    return api.replay(
        b["root"] / "model.orm.yaml",
        b["root"] / "candidate.pop.json",
        b["root"] / "certificate.json",
        reference_root=b["root"],
    )


def produce(b: dict) -> dict:
    save(b, bind=False)
    return api.witness(
        b["root"] / "model.orm.yaml",
        b["root"] / "candidate.pop.json",
        b["root"] / "targets.json",
        reference_root=b["root"],
    )


def payload_observation(payload: dict) -> tuple[int, list[str]]:
    assert isinstance(payload, dict)
    assert type(payload["exit_code"]) is int
    if payload.get("kind") == "derivation-witness-view":
        assert payload["replayable"] is False
        if payload["exit_code"] == 4:
            assert payload["reason"] == "work-limit"
            return 4, ["resource-refused"]
        return payload["exit_code"], []
    assert "results" in payload, "public witness/replay envelope must enumerate results"
    return payload["exit_code"], [r["status"] for r in payload["results"]]


def assert_answer(payload: dict, answer: dict) -> None:
    exit_code, statuses = payload_observation(payload)
    assert exit_code == answer["exit_code"]
    if statuses:
        assert answer["status"] in statuses
    else:
        assert answer["status"] in {None, "input-refused"}
    for index, row in enumerate(payload.get("results", [])):
        assert row["request_index"] == index
        if row["status"] == "proved":
            assert row["reason"] is None
        else:
            assert isinstance(row["reason"], str) and row["reason"]


def direct(b: dict) -> None:
    b["certificate"] = json.loads((CORPUS / b["domain"] / "direct.witness.json").read_text())
    b["request"]["targets"] = [copy.deepcopy(b["certificate"]["results"][0]["target"])]


def baseline(b: dict) -> None:
    save(b)
    assert_answer(produce(b), {"exit_code": 0, "status": "proved"})
    assert_answer(replay(b), {"exit_code": 0, "status": "proved"})


def no_evaluator(monkeypatch) -> None:
    from gnd import checker, extensions, terms

    def forbidden(*args, **kwargs):
        raise AssertionError("replay invoked a production evaluator/comparison primitive")

    for name in (
        "check",
        "structured_extension_view",
        "structured_extension_facts",
        "_python_extension_calculator",
        "_exact_extension_calculator",
        "_evaluate_stratified_extensions",
        "_compare",
        "_typed_comparison_values",
    ):
        if hasattr(checker, name):
            monkeypatch.setattr(checker, name, forbidden)
        for target in (name, name.removeprefix("_")):
            if hasattr(extensions, target):
                monkeypatch.setattr(extensions, target, forbidden)
    for name in ("evaluate_term", "guarded_operand_evaluator", "materialize_scalar"):
        if hasattr(terms, name):
            monkeypatch.setattr(terms, name, forbidden)
        if hasattr(extensions, name):
            monkeypatch.setattr(extensions, name, forbidden)


def comparison(b: dict, parameters: dict) -> None:
    primitive = parameters["primitive"]
    prefix = b["domain"]
    obj = prefix + "_value"
    base = prefix + "_observed"
    out = b["ids"]["reach"]
    left = parameters["left"]
    b["model"] = {
        "version": 4,
        "model_id": f"urn:gnd-fixture:v71-{prefix}-comparison@1",
        "source": {"kind": "text-conversation", "confidence": "standard", "mode": "one-shot"},
        "object_types": [{"id": obj, "name": "Value", "kind": "value", "primitive": primitive}],
        "fact_types": [
            {
                "id": base,
                "reading": "{Value} is observed",
                "roles": [{"role_name": "value", "object_type": obj}],
            },
            {
                "id": out,
                "reading": "{Value} qualifies",
                "roles": [{"role_name": "value", "object_type": obj}],
                "derivation": "derived",
                "derivation_rule": {
                    "body": [{"fact_type": base, "bind": {"value": "$v"}}],
                    "where": [
                        {
                            "operator": parameters["operator"],
                            "left": "$v",
                            "right": parameters["right"],
                        }
                    ],
                    "head": {"value": "$v"},
                },
            },
        ],
        "constraints": [],
        "rejected_proposals": [],
    }
    b["candidate"] = {
        "population": {
            "model": "model.orm.yaml",
            "source": "fixture",
            "model_id": b["model"]["model_id"],
            "covers": [base, out],
        },
        "instances": {},
        "facts": {base: [{"value": left}], out: []},
    }
    binding = {"v": scalar(left, primitive)}
    if primitive in {"Date", "DateTime"}:
        b["model"]["fact_types"][0]["roles"].append({"role_name": "limit", "object_type": obj})
        b["model"]["fact_types"][0]["reading"] = "{Value} is bounded by {Value}"
        r = b["model"]["fact_types"][-1]["derivation_rule"]
        r["body"][0]["bind"]["limit"] = "$limit"
        r["where"][0]["right"] = "$limit"
        b["candidate"]["facts"][base][0]["limit"] = parameters["right"]
        binding["limit"] = scalar(parameters["right"], primitive)
    nodes = [
        {
            "kind": "base",
            "fact_type": base,
            "tuple": [scalar(left, primitive)],
            "origin": {"kind": "candidate", "reference_id": None, "fact_index": 0},
        },
        {
            "kind": "comparison",
            "rule_fact_type": out,
            "clause_index": 0,
            "where_index": 0,
            "bindings": copy.deepcopy(binding),
            "premises": [],
        },
        {
            "kind": "rule",
            "fact_type": out,
            "clause_index": 0,
            "tuple": [scalar(left, primitive)],
            "bindings": copy.deepcopy(binding),
            "premises": [0, 1],
        },
    ]
    if primitive in {"Date", "DateTime"}:
        nodes[0]["tuple"].append(scalar(parameters["right"], primitive))
    if parameters.get("bool_mutation"):
        nodes[2]["bindings"]["v"] = scalar(True, "Boolean")
    if parameters.get("drop_where"):
        nodes.pop(1)
        nodes[-1]["premises"] = [0]
    set_proof(b, nodes, [left], primitive)


def kernel(b: dict, cert: object | None = None) -> dict:
    module = importlib.import_module("gnd.witness.kernel")
    reference_inputs = ()
    if b["model"].get("reference_populations"):
        reference_inputs = (("links", (b["root"] / "references/links.pop.json").read_bytes()),)
    result = module.replay_witness(
        b["model"],
        b["candidate"],
        b["certificate"] if cert is None else cert,
        reference_inputs=reference_inputs,
    )
    return result if isinstance(result, dict) else result.model_dump(mode="json")


def cli(*args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *args],
        cwd=ROOT,
        capture_output=True,
        text=True,
        timeout=15,
        check=False,
    )


def execute(row: dict, tmp_path: Path, monkeypatch, *, measurement: dict | None = None) -> dict:
    require_lane()
    b = bundle(row["domain"], tmp_path / "case")
    b["domain"] = row["domain"]
    baseline_started = time.monotonic()
    baseline(b)
    if measurement is not None:
        measurement["baseline_seconds"] = time.monotonic() - baseline_started
    if measurement is not None:
        from gnd import model as model_intake
        from gnd import population as pop_intake
        from gnd import references as ref_intake
        from gnd.witness import io as witness_io

        measurement.update(fixture_seconds=0.0, inherited_intake_seconds=0.0)
        depths = {"fixture": 0, "intake": 0}

        def timed(original, kind):
            def wrapped(*args, **kwargs):
                outer = depths[kind] == 0 and (kind == "fixture" or depths["fixture"] == 0)
                depths[kind] += 1
                started = time.monotonic()
                try:
                    return original(*args, **kwargs)
                finally:
                    depths[kind] -= 1
                    if outer:
                        measurement[
                            "fixture_seconds" if kind == "fixture" else "inherited_intake_seconds"
                        ] += time.monotonic() - started

            return wrapped

        monkeypatch.setattr(sys.modules[__name__], "save", timed(save, "fixture"))
        for module, name in (
            (model_intake, "load_model_bytes"),
            (pop_intake, "_build_population"),
            (pop_intake, "_parse_document_bytes"),
            (ref_intake, "validate_declarations"),
            (witness_io, "load_model_bytes"),
            (witness_io, "_build_population"),
            (witness_io, "_parse_document_bytes"),
            (witness_io, "validate_declarations"),
        ):
            monkeypatch.setattr(module, name, timed(getattr(module, name), "intake"))
    mode, p = row["mode"], row["parameters"]
    vals = b["ids"]["values"]
    ft = b["model"]["fact_types"][-1]
    clauses = ft["derivation_rule"]["clauses"]
    if mode in {"replay", "mutate"}:
        if p.get("certificate") == "direct":
            direct(b)
        if mode == "mutate":
            edit(b["certificate"], p["edits"])
        return replay(b)
    if mode == "alternative":
        direct(b)
        clauses.append(copy.deepcopy(clauses[0]))
        b["certificate"]["nodes"][-1]["clause_index"] = 2
        save(b)
        return replay(b)
    if mode == "mutual":
        direct(b)
        alias = copy.deepcopy(ft)
        alias["id"] += "_alias"
        alias["derivation_rule"] = {
            "body": [{"fact_type": ft["id"], "bind": {"source": "$x", "target": "$y"}}],
            "head": {"source": "$x", "target": "$y"},
        }
        b["model"]["fact_types"].append(alias)
        clauses.append(
            {
                "body": [{"fact_type": alias["id"], "bind": {"source": "$x", "target": "$y"}}],
                "head": {"source": "$x", "target": "$y"},
            }
        )
        save(b)
        return replay(b)
    if mode in {"claimed-base", "cycle"}:
        direct(b)
        root = b["certificate"]["nodes"][-1]
        if mode == "claimed-base":
            b["certificate"]["nodes"][0] = {
                "id": 0,
                "kind": "base",
                "fact_type": ft["id"],
                "tuple": root["tuple"],
                "origin": {"kind": "candidate", "reference_id": None, "fact_index": 0},
            }
        elif p["two"]:
            root["clause_index"] = 1
            root["premises"] = [0, 2]
            other = copy.deepcopy(root)
            other["id"] = 2
            other["premises"] = [0, 1]
            b["certificate"]["nodes"].append(other)
            b["certificate"]["results"][0]["root"] = 2
        else:
            root["clause_index"] = 1
            root["premises"] = [0, 1]
        return replay(b)
    if mode == "stale":
        if p["subject"] == "model":
            b["model"]["model_id"] += "-changed"
            b["candidate"]["population"]["model_id"] = b["model"]["model_id"]
            b["reference"]["population"]["model_id"] = b["model"]["model_id"]
        elif p["subject"] == "candidate":
            b["candidate"]["population"]["label"] = "boundary"
        else:
            b["reference"]["facts"][b["ids"]["edge"]][0]["target"] = vals[3]
        return replay(b)
    if mode in {"raw-input", "hostile"}:
        if mode == "raw-input":
            raw = p["raw"]
        else:
            variant = p["variant"]
            if variant == "non-object":
                return kernel(b, [])
            if variant == "stale-object":
                return kernel(b, {"version": 1})
            if variant == "bool-index":
                b["certificate"]["nodes"][0]["id"] = True
                return replay(b)
            raw = {
                "nan": '{"version":NaN}',
                "infinity": '{"version":Infinity}',
                "duplicate-key": '{"version":1,"version":2}',
                "deep": "[" * 65 + "0" + "]" * 65,
                "giant-integer": '{"version":' + "9" * 5000 + "}",
            }[variant]
        save(b, bind=False)
        (b["root"] / "certificate.json").write_text(raw)
        return api.replay(
            b["root"] / "model.orm.yaml",
            b["root"] / "candidate.pop.json",
            b["root"] / "certificate.json",
            reference_root=b["root"],
        )
    if mode == "order":
        b["certificate"]["binding"]["model_digest"] = "sha256:" + "0" * 64
        b["certificate"]["nodes"][-1]["clause_index"] = 99
        result = replay(b)
        assert result["reason"] == "binding-stale"
        return result
    if mode == "produce-target":
        if p["target"] == "missing":
            b["request"]["targets"][0]["tuple"][-1]["value"] = vals[0]
        else:
            b["reference"]["facts"][b["ids"]["edge"]].append(
                {"source": "OPAQUE-START", "target": {"$opaque": "hidden"}}
            )
            if p["target"] == "opaque":
                b["request"]["targets"][0]["tuple"] = [scalar("OPAQUE-START"), scalar("OPAQUE-END")]
            b["reference"]["format_version"] = 2
            save(b)
        return produce(b)
    if mode == "bad-target":
        t = b["request"]["targets"][0]
        if p["variant"] == "unknown-fact":
            t["fact_type"] = "absent"
        elif p["variant"] == "arity":
            t["tuple"].pop()
        else:
            t["tuple"][0]["primitive"] = "Integer"
        return produce(b)
    if mode == "batch":
        t = copy.deepcopy(b["request"]["targets"][0])
        if p["variant"] == "empty":
            b["request"]["targets"] = []
        elif p["variant"] == "duplicates":
            b["request"]["targets"] = [t, copy.deepcopy(t)]
        else:
            missing = copy.deepcopy(t)
            missing["tuple"][-1]["value"] = vals[0]
            b["request"]["targets"] = [t, missing, copy.deepcopy(t)]
        result = produce(b)
        if p["variant"] != "empty":
            assert len(result["results"]) == len(b["request"]["targets"])
            assert [r["target"] for r in result["results"]] == b["request"]["targets"]
        return result
    if mode in {"unsupported", "temporal"}:
        construct = p.get("construct", "temporal")
        if construct == "negative":
            clauses[0]["negate"] = [copy.deepcopy(clauses[0]["body"][0])]
        elif construct == "semiderived":
            ft["derivation"] = "semiderived"
        elif construct == "opaque-rule":
            ft["derivation_rule"] = "An operator says this tuple follows."
        elif construct in {"float", "datetime"}:
            comparison(
                b,
                {
                    "primitive": "Float" if construct == "float" else "DateTime",
                    "operator": "=",
                    "left": 1.5 if construct == "float" else "2024-01-01T00:00:00",
                    "right": 1.5 if construct == "float" else "2024-01-01T00:00:00",
                },
            )
        elif construct in {"exact-head", "exact-where"}:
            comparison(b, {"primitive": "Integer", "operator": "=", "left": 5, "right": 5})
            r = b["model"]["fact_types"][-1]["derivation_rule"]
            expression = {"fn": "add", "args": ["$v", 0]}
            if construct == "exact-head":
                r["head"]["value"] = expression
            else:
                r["where"][0]["left"] = expression
        elif construct == "aggregate":
            comparison(b, {"primitive": "Integer", "operator": "=", "left": 5, "right": 5})
            r = b["model"]["fact_types"][-1]["derivation_rule"]
            r.pop("where")
            r["aggregate"] = {"fn": "count", "of": 1, "over": ["$v"], "as": "$count"}
            r["head"]["value"] = "$count"
        else:
            comparison(
                b,
                {"primitive": "Date", "operator": "=", "left": "2024-02-29", "right": "2024-02-29"},
            )
            b["model"]["fact_types"][-1]["derivation_rule"]["where"][0]["left"] = {
                "fn": "date_add",
                "args": ["$v", {"duration_days": 1}],
            }
            save(b, bind=False)
            result = produce(b)
            assert replay(b)["exit_code"] == result["exit_code"]
            return result
        save(b)
        result = produce(b)
        assert replay(b)["exit_code"] == result["exit_code"]
        return result
    if mode == "comparison":
        comparison(b, p)
        # Unsupported ordering is validated by the witness support classifier;
        # ordinary model validation may already refuse this admitted site.
        save(b)
        if p.get("sentinel"):
            no_evaluator(monkeypatch)
        return kernel(b) if p.get("unsupported") else replay(b)
    if mode == "independent":
        import ast
        import inspect

        module = importlib.import_module("gnd.witness.kernel")
        tree = ast.parse(inspect.getsource(module))
        forbidden = {
            "gnd.checker",
            "gnd.terms",
            "gnd.semantic_adapter",
            "gnd.semantic_spec",
            "gnd.witness.producer",
            "duckdb",
            "subprocess",
        }
        imports = set()
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                imports.update(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                imports.add(node.module or "")
                imports.update((node.module or "") + "." + alias.name for alias in node.names)
        assert not imports & forbidden
        no_evaluator(monkeypatch)
        return replay(b)
    if mode in {"deterministic", "rename"}:
        if mode == "rename":
            encoded = json.dumps(
                [b["model"], b["candidate"], b["reference"], b["certificate"], b["request"]]
            )
            encoded = encoded.replace(b["domain"] + "_", "renamed_")
            b["model"], b["candidate"], b["reference"], b["certificate"], b["request"] = json.loads(
                encoded
            )
            save(b)
        first, second = produce(b), produce(b)
        assert canonical_json_bytes(first["certificate"]) == canonical_json_bytes(
            second["certificate"]
        )
        return first
    if mode in {"legacy", "optional-sentinel"}:
        if mode == "optional-sentinel":

            def forbidden(*args, **kwargs):
                raise AssertionError("ordinary checking started an optional tool")

            monkeypatch.setattr(subprocess, "run", forbidden)
        # The frozen legacy report names these exact caller coordinates. Use
        # the immutable fixture inputs rather than unrelated temporary paths.
        legacy_root = Path("tests/fixtures/v71/phase3") / row["domain"]
        actual = api.check(legacy_root / "model.orm.yaml", legacy_root / "candidate.pop.json")
        expected = json.loads((CORPUS / row["domain"] / "legacy-check.json").read_text())
        assert actual == expected
        if mode == "optional-sentinel":
            monkeypatch.undo()
        return replay(b)
    if mode == "delivery":
        from jsonschema import Draft202012Validator

        canonical = ROOT / "src/gnd/schema/witness.schema.json"
        packaged = ROOT / "src/gnd/skills/gnd-export/references/witness.schema.json"
        assert canonical.read_bytes() == packaged.read_bytes()
        schema = json.loads(canonical.read_text())
        Draft202012Validator.check_schema(schema)
        validator = Draft202012Validator(schema)
        validator.validate(b["certificate"])
        dirty = copy.deepcopy(b["certificate"])
        dirty["trusted_axiom"] = True
        assert list(validator.iter_errors(dirty))
        for relative in [
            "SKILL.md",
            "references/witness-contract.md",
            "references/export-contract.md",
        ]:
            assert (ROOT / "src/gnd/skills/gnd-export" / relative).is_file()
        help_result = cli("--help")
        assert help_result.returncode == 0
        for command in ["witness", "replay", "witness-view"]:
            assert command in help_result.stdout
        return replay(b)
    if mode == "privacy":
        return privacy(b, p)
    if mode in {"input-limit", "work-limit", "diamond", "view-limit", "batch-priority"}:
        return limit_case(b, mode, p)
    raise AssertionError(f"unhandled corpus mode: {mode}")


def privacy(b: dict, p: dict) -> dict:
    view = importlib.import_module("gnd.witness.view")
    raw = view.witness_view(b["certificate"], raw=True)
    assert raw["replayable"] is True
    redacted = view.witness_view(b["certificate"])
    assert redacted["kind"] == "derivation-witness-view"
    assert redacted["replayable"] is False
    text = json.dumps(redacted)
    secrets = b["ids"]["values"] + list(b["certificate"]["binding"].values())[:2]
    assert all(secret not in text for secret in secrets)
    if p["variant"] == "redacted":
        return kernel(b, redacted)
    if p["variant"] == "dirty":
        dirty = copy.deepcopy(redacted)
        dirty["leak"] = b["ids"]["values"][0]
        assert any(secret in json.dumps(dirty) for secret in secrets)
    if p["variant"] == "overwrite":
        destination = b["root"] / "already-exists.json"
        destination.write_text("protected\n")
        result = cli(
            "witness",
            str(b["root"] / "model.orm.yaml"),
            str(b["root"] / "candidate.pop.json"),
            "--targets",
            str(b["root"] / "targets.json"),
            "--reference-root",
            str(b["root"]),
            "--raw",
            "--out",
            str(destination),
        )
        assert result.returncode == 3
        assert destination.read_text() == "protected\n"
        return {"exit_code": 3, "results": []}
    before = {path: path.read_bytes() for path in b["root"].rglob("*") if path.is_file()}
    result = replay(b)
    assert all(path.read_bytes() == content for path, content in before.items())
    if p["variant"] == "raw":
        destination = b["root"] / "export.json"
        run = cli(
            "witness",
            str(b["root"] / "model.orm.yaml"),
            str(b["root"] / "candidate.pop.json"),
            "--targets",
            str(b["root"] / "targets.json"),
            "--reference-root",
            str(b["root"]),
            "--raw",
            "--out",
            str(destination),
        )
        assert run.returncode == 0, run.stderr
        assert json.loads(destination.read_text())["kind"] == "derivation-witness"
    return result


def wide_proof(b: dict, count: int) -> None:
    """A single connected positive rule needs count distinct base occurrences."""
    ids = b["ids"]
    first = b["ids"]["values"][0]
    last = b["ids"]["values"][-1]
    ft = b["model"]["fact_types"][-1]
    ft["derivation_rule"] = {
        "body": [
            {"fact_type": ids["edge"], "bind": {"source": "$x", "target": f"N{i}"}}
            for i in range(count)
        ],
        "head": {"source": "$x", "target": last},
    }
    rows = [{"source": first, "target": f"N{i}"} for i in range(count)]
    b["reference"]["facts"][ids["edge"]] = rows
    b["candidate"]["facts"][ids["reach"]] = []
    nodes = [
        {
            "kind": "base",
            "fact_type": ids["edge"],
            "tuple": [scalar(first), scalar(r["target"])],
            "origin": {"kind": "reference", "reference_id": "links", "fact_index": i},
        }
        for i, r in enumerate(rows)
    ]
    nodes.append(
        {
            "kind": "rule",
            "fact_type": ids["reach"],
            "clause_index": 0,
            "tuple": [scalar(first), scalar(last)],
            "bindings": {"x": scalar(first)},
            "premises": list(range(count)),
        }
    )
    set_proof(b, nodes, [first, last])


def fan_proof(b: dict, edge_count: int, *, two_layers: bool = False) -> None:
    direct(b)
    ft = b["model"]["fact_types"][-1]
    if two_layers:
        first = edge_count // 2
        helper = copy.deepcopy(ft)
        helper["id"] += "_fan"
        helper["derivation_rule"] = copy.deepcopy(ft["derivation_rule"]["clauses"][0])
        helper["derivation_rule"]["body"] *= first
        b["model"]["fact_types"].insert(-1, helper)
        ft["derivation_rule"] = {
            "body": [{"fact_type": helper["id"], "bind": {"source": "$x", "target": "$y"}}]
            * (edge_count - first),
            "head": {"source": "$x", "target": "$y"},
        }
        node = b["certificate"]["nodes"][-1]
        node["fact_type"] = helper["id"]
        node["premises"] = [0] * first
        root = copy.deepcopy(node)
        root["fact_type"] = ft["id"]
        root["premises"] = [1] * (edge_count - first)
        set_proof(b, [b["certificate"]["nodes"][0], node, root], b["ids"]["values"][:2])
    else:
        ft["derivation_rule"] = copy.deepcopy(ft["derivation_rule"]["clauses"][0])
        ft["derivation_rule"]["body"] *= edge_count
        b["certificate"]["nodes"][-1]["premises"] = [0] * edge_count


def depth_proof(b: dict, depth: int) -> None:
    direct(b)
    vals, edge, reach = b["ids"]["values"], b["ids"]["edge"], b["ids"]["reach"]
    b["reference"]["facts"][edge].append({"source": vals[0], "target": vals[0]})
    base_index = len(b["reference"]["facts"][edge]) - 1
    nodes = [
        b["certificate"]["nodes"][0],
        {
            "kind": "base",
            "fact_type": edge,
            "tuple": [scalar(vals[0]), scalar(vals[0])],
            "origin": {"kind": "reference", "reference_id": "links", "fact_index": base_index},
        },
        b["certificate"]["nodes"][1],
    ]
    nodes[2]["premises"] = [0]
    for _ in range(depth - 2):
        nodes.append(
            {
                "kind": "rule",
                "fact_type": reach,
                "clause_index": 1,
                "tuple": [scalar(vals[0]), scalar(vals[1])],
                "bindings": {"x": scalar(vals[0]), "middle": scalar(vals[0]), "y": scalar(vals[1])},
                "premises": [1, len(nodes) - 1],
            }
        )
    # For depth two, the self-edge base is not reachable and must be omitted.
    if depth == 2:
        nodes = [nodes[0], nodes[2]]
    set_proof(b, nodes, vals[:2])


def binding_proof(b: dict, cells: int) -> None:
    """2 base nodes + 9,997 shared-clause instances + one 30/31-cell root."""
    ids = b["ids"]
    obj = ids["node"]
    base = ids["edge"]
    wide = base + "_wide"
    helper = ids["reach"] + "_helper"
    extra = cells - 9997 * 10 - 10
    roles10 = [{"role_name": f"a{i}", "object_type": obj} for i in range(10)]
    roles_extra = [{"role_name": f"b{i}", "object_type": obj} for i in range(extra)]
    rows10 = {r["role_name"]: f"A{i}" for i, r in enumerate(roles10)}
    rows_extra = {r["role_name"]: f"B{i}" for i, r in enumerate(roles_extra)}
    bind10 = {r: "$" + r for r in rows10}
    bind_extra = {r: "$" + r for r in rows_extra}
    all_rows = rows10 | rows_extra
    all_bind = bind10 | bind_extra

    def fact(name, roles, rule=None):
        result = {
            "id": name,
            "roles": roles,
            "reading": " ".join(
                "{Warehouse}" if b["domain"] == "dispatch" else "{Service}" for _ in roles
            ),
        }
        if rule:
            result.update(derivation="derived", derivation_rule=rule)
        return result

    b["model"]["fact_types"] = [
        fact(base, roles10),
        fact(wide, roles_extra),
        fact(helper, roles10, {"body": [{"fact_type": base, "bind": bind10}], "head": bind10}),
        fact(
            ids["reach"],
            roles10 + roles_extra,
            {
                "body": [{"fact_type": helper, "bind": bind10}] * 9997
                + [{"fact_type": wide, "bind": bind_extra}],
                "head": all_bind,
            },
        ),
    ]
    b["model"].pop("reference_populations")
    b["candidate"]["population"]["covers"] = [base, wide, ids["reach"]]
    b["candidate"]["facts"] = {base: [rows10], wide: [rows_extra], ids["reach"]: []}
    typed10 = [scalar(v) for v in rows10.values()]
    nodes = [
        {
            "kind": "base",
            "fact_type": ft,
            "tuple": [scalar(v) for v in row.values()],
            "origin": {"kind": "candidate", "reference_id": None, "fact_index": 0},
        }
        for ft, row in [(base, rows10), (wide, rows_extra)]
    ]
    for _ in range(9997):
        nodes.append(
            {
                "kind": "rule",
                "fact_type": helper,
                "clause_index": 0,
                "tuple": typed10,
                "bindings": {k: scalar(v) for k, v in rows10.items()},
                "premises": [0],
            }
        )
    nodes.append(
        {
            "kind": "rule",
            "fact_type": ids["reach"],
            "clause_index": 0,
            "tuple": [scalar(v) for v in all_rows.values()],
            "bindings": {k: scalar(v) for k, v in all_rows.items()},
            "premises": list(range(2, 9999)) + [1],
        }
    )
    set_proof(b, nodes, list(all_rows.values()))
    assert sum(len(n.get("bindings", {})) for n in nodes) == cells


def join_population(b: dict, over: bool) -> None:
    ids = b["ids"]
    m, n = (11, 9090) if over else (10, 9999)
    assert m + m * n == (100001 if over else 100000)
    model = b["model"]
    model.pop("reference_populations")
    left, right = ids["edge"], ids["edge"] + "_right"
    roles = copy.deepcopy(model["fact_types"][0]["roles"])
    model["fact_types"] = [
        {
            "id": left,
            "roles": roles,
            "reading": "{Warehouse} links {Warehouse}"
            if b["domain"] == "dispatch"
            else "{Service} links {Service}",
        },
        {
            "id": right,
            "roles": roles,
            "reading": "{Warehouse} links {Warehouse}"
            if b["domain"] == "dispatch"
            else "{Service} links {Service}",
        },
        {
            "id": ids["reach"],
            "roles": roles,
            "reading": "{Warehouse} reaches {Warehouse}"
            if b["domain"] == "dispatch"
            else "{Service} reaches {Service}",
            "derivation": "derived",
            "derivation_rule": {
                "body": [
                    {"fact_type": left, "bind": {"source": "$x", "target": "$z"}},
                    {"fact_type": right, "bind": {"source": "$y", "target": "$z"}},
                ],
                "where": [{"operator": "=", "left": "$x", "right": "NO-MATCH"}],
                "head": {"source": "$x", "target": "$y"},
            },
        },
    ]
    b["candidate"]["population"]["covers"] = [left, right, ids["reach"]]
    b["candidate"]["facts"] = {
        left: [{"source": f"L{i}", "target": "SHARED"} for i in range(m)],
        right: [{"source": f"R{i}", "target": "SHARED"} for i in range(n)],
        ids["reach"]: [],
    }
    b["request"]["targets"] = [target(b, ["L0", "R0"])]


def limit_case(b: dict, mode: str, p: dict) -> dict:
    if mode == "input-limit":
        cap, amount = p["cap"], p["value"]
        if cap == "bytes":
            io = importlib.import_module("gnd.witness.io")
            types = importlib.import_module("gnd.witness.types")
            raw = json.dumps(b["certificate"]).encode()
            assert len(raw) < amount
            path = b["root"] / "sized.json"
            path.write_bytes(raw + b" " * (amount - len(raw)))
            if p["over"]:
                try:
                    io.load_certificate(path, limits=types.DEFAULT_LIMITS)
                except types.WitnessInputError:
                    return {"exit_code": 3, "results": []}
                raise AssertionError("oversize certificate read was admitted")
            loaded = io.load_certificate(path, limits=types.DEFAULT_LIMITS)
            return kernel(b, loaded)
        if cap == "container_depth":
            io = importlib.import_module("gnd.witness.io")
            types = importlib.import_module("gnd.witness.types")
            document: object = 0
            for _ in range(amount):
                document = [document]
            if p["over"]:
                try:
                    io.validate_witness_structure(document)
                except types.WitnessInputError:
                    return {"exit_code": 3, "results": []}
                raise AssertionError("excessive nesting was admitted")
            io.validate_witness_structure(document)
            return {"exit_code": 0, "results": []}
        if cap == "targets":
            b["request"]["targets"] *= amount
            result = produce(b)
            if not p["over"]:
                assert len(result["results"]) == amount
            return result
        if cap == "numeric_digits":
            comparison(
                b,
                {
                    "primitive": "Integer",
                    "operator": "=",
                    "left": int("9" * amount),
                    "right": int("9" * amount),
                },
            )
        else:
            direct(b)
            old = b["ids"]["values"][0]
            value = "X" * amount
            for key in ("candidate", "reference", "certificate", "request"):
                b[key] = json.loads(json.dumps(b[key]).replace(old, value))
        save(b)
        return replay(b)
    if mode == "work-limit":
        cap, amount = p["cap"], p["value"]
        if cap == "nodes":
            wide_proof(b, amount - 1)
        elif cap == "edges":
            fan_proof(b, amount, two_layers=True)
        elif cap == "binding_cells":
            binding_proof(b, amount)
        elif cap == "proof_depth":
            depth_proof(b, amount)
        else:
            join_population(b, p["over"])
            save(b)
            return produce(b)
        save(b)
        return replay(b)
    if mode == "batch-priority":
        depth_proof(b, 129)
        bad = copy.deepcopy(b["certificate"]["results"][0])
        bad["request_index"] = 1
        bad["target"]["tuple"][-1]["value"] = "WRONG-CONCLUSION"
        b["certificate"]["results"].append(bad)
        save(b)
        return replay(b)
    if mode == "diamond":
        direct(b)
        ft = b["model"]["fact_types"][-1]
        recursive = ft["derivation_rule"]["clauses"][1]
        recursive["body"] = [{"fact_type": ft["id"], "bind": {"source": "$x", "target": "$y"}}] * 2
        nodes = b["certificate"]["nodes"]
        for _ in range(18):
            previous = len(nodes) - 1
            root = copy.deepcopy(nodes[-1])
            root["clause_index"] = 1
            root["premises"] = [previous, previous]
            root["bindings"].pop("middle", None)
            nodes.append(root)
        set_proof(b, nodes, b["ids"]["values"][:2])
        save(b)
        result = replay(b)
        assert len(nodes) == 20
        return result
    fan_proof(b, p["visits"] - 1)
    save(b)
    view = importlib.import_module("gnd.witness.view")
    result = view.witness_view(b["certificate"], raw=True, expand=True)
    assert result["replayable"] is False
    assert result["exit_code"] == (4 if p["over"] else 0)
    if not p["over"]:
        assert result["work"]["node_visits"] == p["visits"]
    return result
