"""RED corpus harness for the owner-marked v7.1 Phase 1 calendar contract.

Inputs and independently authored answers live in separate files. Each case is
executed against the public surface or the named model validator; a refusal
case first proves the unmodified temporal control is accepted, so an absent
feature cannot accidentally satisfy a negative answer.
"""

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import time
from copy import deepcopy
from pathlib import Path

import pytest
from ruamel.yaml import YAML

from gnd.model import load_model
from gnd.transition import model_digest, operations_digest

ROOT = Path(__file__).resolve().parents[1]
CORPUS = ROOT / "tests/fixtures/v71/phase1"
LEGACY = ROOT / "tests/fixtures/v71"
INPUTS = json.loads((CORPUS / "inputs.json").read_text())["cases"]
ANSWERS = {row["id"]: row for row in json.loads((CORPUS / "answers.json").read_text())["cases"]}
yaml = YAML(typ="safe")


def test_phase1_corpus_manifest() -> None:
    manifest = json.loads((CORPUS / "manifest.json").read_text())
    assert manifest["schema_version"] == 1
    listed = manifest["files"]
    assert len(listed) == len(set(listed))
    actual = {
        path.relative_to(CORPUS).as_posix()
        for path in CORPUS.rglob("*")
        if path.is_file() and path.name != "manifest.json"
    }
    assert set(listed) == actual
    for relative, metadata in listed.items():
        path = CORPUS / relative
        assert path.is_file() and not path.is_symlink()
        content = path.read_bytes()
        assert len(content) == metadata["bytes"]
        assert hashlib.sha256(content).hexdigest() == metadata["sha256"]
    ids = [case["id"] for case in INPUTS]
    assert len(ids) == len(set(ids))
    assert set(ids) == set(ANSWERS)
    assert {case["branch"] for case in INPUTS} == {f"B{n:02d}" for n in range(1, 44)}


def _load(domain: str) -> tuple[dict, dict]:
    model = yaml.load((CORPUS / domain / "model.orm.yaml").read_text())
    population = json.loads((CORPUS / domain / "population.pop.json").read_text())
    return model, population


def _pointer(document: dict, path: str) -> tuple[object, str]:
    parts = [part.replace("~1", "/").replace("~0", "~") for part in path.split("/")[1:]]
    cursor: object = document
    for part in parts[:-1]:
        cursor = cursor[int(part)] if isinstance(cursor, list) else cursor[part]
    return cursor, parts[-1]


def _edit(document: dict, edit: dict) -> None:
    parent, key = _pointer(document, edit["path"])
    operation = edit["op"]
    if operation == "set":
        parent[int(key) if isinstance(parent, list) else key] = deepcopy(edit["value"])
    elif operation == "append":
        collection = parent[int(key) if isinstance(parent, list) else key]
        assert isinstance(collection, list)
        collection.append(deepcopy(edit["value"]))
    elif operation == "remove":
        if isinstance(parent, list):
            del parent[int(key)]
        else:
            del parent[key]
    else:
        raise AssertionError(f"unknown corpus edit {operation}")


def _write(tmp_path: Path, model: dict, population: dict) -> tuple[Path, Path]:
    tmp_path.mkdir(parents=True, exist_ok=True)
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.pop.json"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population_path.write_text(json.dumps(population, ensure_ascii=False) + "\n")
    return model_path, population_path


def _cli(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "gnd", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
        timeout=20,
    )


def _json_result(result: subprocess.CompletedProcess[str]) -> dict:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise AssertionError(f"no JSON payload: {result.stdout}\n{result.stderr}") from error


def _temporal_control(domain: str, tmp_path: Path) -> None:
    model, population = _load(domain)
    model_path, population_path = _write(tmp_path, model, population)
    result = _cli("check", str(model_path), str(population_path), "--format", "json")
    assert result.returncode == 0, result.stdout + result.stderr
    payload = _json_result(result)
    assert payload["exit_code"] == 0
    assert payload["schema_version"] == 11


def _bulk(population: dict, count: int) -> None:
    """Deterministically expand one dispatch case; no expected answer is computed here."""
    for key in (
        "dispatch_shipment_origin",
        "dispatch_shipping_deadline",
        "dispatch_pickup_on",
        "dispatch_allowance_days",
    ):
        population["facts"][key] = []
    # Keep the retained non-deadline facts inside the expanded shipment roster.
    for rows in population["facts"].values():
        for row in rows:
            if row.get("shipment") == "SHIP-17":
                row["shipment"] = "SHIP-BULK-00000"
    for index in range(count):
        shipment = f"SHIP-BULK-{index:05d}"
        population["facts"]["dispatch_shipment_origin"].append(
            {"shipment": shipment, "warehouse": "WH-A"}
        )
        population["facts"]["dispatch_shipping_deadline"].append(
            {"shipment": shipment, "deadline": "2026-10-04"}
        )
        population["facts"]["dispatch_pickup_on"].append(
            {"shipment": shipment, "pickup": "2026-10-02"}
        )
        population["facts"]["dispatch_allowance_days"].append({"shipment": shipment, "days": 2})


def _forbidden_site(model: dict, site: str) -> None:
    date_term = {"fn": "date_add", "args": ["$pickup", {"duration_days": 1}]}
    # Remove the admitted guarded use; otherwise a broken site-specific check
    # could be masked by the ordinary temporal path.
    model["constraints"][0]["consequent"]["comparison"]["left"] = "$pickup"
    if site in {"derivation-head", "derivation-where"}:
        rule = {
            "body": [
                {
                    "fact_type": "dispatch_pickup_on",
                    "bind": {"shipment": "$shipment", "pickup": "$pickup"},
                }
            ],
            "head": {"shipment": "$shipment", "day": "$pickup"},
        }
        if site == "derivation-head":
            rule["head"]["day"] = date_term
        else:
            rule["where"] = [{"operator": "<=", "left": date_term, "right": "$pickup"}]
        model["fact_types"].append(
            {
                "id": "dispatch_computed_day",
                "reading": "{DispatchShipment} has computed day {DispatchCalendarDay}",
                "roles": [
                    {"object_type": "dispatch_shipment", "role_name": "shipment"},
                    {"object_type": "dispatch_calendar_day", "role_name": "day"},
                ],
                "derivation": "derived",
                "derivation_rule": rule,
            }
        )
    elif site == "operation-binding":
        model["operations"] = [
            {
                "id": "reschedule",
                "reading": "{DispatchShipment} reschedules",
                "parameters": [
                    {"name": "shipment", "object_type": "dispatch_shipment"},
                    {"name": "pickup", "object_type": "dispatch_calendar_day"},
                ],
                "preconditions": [],
                "effects": [
                    {
                        "assert": {
                            "fact_type": "dispatch_pickup_on",
                            "bind": {"shipment": "$shipment", "pickup": date_term},
                        }
                    }
                ],
                "frame": {"modality": "alethic"},
                "source": "user-supplied",
                "status": "confirmed",
                "provenance": {"user_quote": "A reschedule changes pickup."},
            }
        ]
    else:
        model["constraints"][0]["consequent"] = {
            "exists": {
                "atoms": [
                    {
                        "fact_type": "dispatch_pickup_on",
                        "bind": {"shipment": "$shipment", "pickup": "$witness"},
                    }
                ],
                "where": [{"operator": "<=", "left": date_term, "right": "$witness"}],
            }
        }


def _custom_model(case: dict, model: dict, population: dict) -> None:
    surface = case["surface"]
    if surface == "forbidden-site":
        _forbidden_site(model, case["parameters"]["site"])
    elif surface == "cross-primitive-binding":
        model["object_types"].append(
            {"id": "dispatch_integer", "kind": "value", "primitive": "Integer"}
        )
        model["fact_types"].append(
            {
                "id": "dispatch_integer_days",
                "reading": "{DispatchShipment} has integer days {DispatchInteger}",
                "roles": [
                    {"object_type": "dispatch_shipment", "role_name": "shipment"},
                    {"object_type": "dispatch_integer", "role_name": "days"},
                ],
            }
        )
        model["constraints"][0]["antecedent"].append(
            {
                "fact_type": "dispatch_allowance_days",
                "bind": {"shipment": "$shipment", "days": "$same"},
            }
        )
        model["constraints"][0]["antecedent"].append(
            {
                "fact_type": "dispatch_integer_days",
                "bind": {"shipment": "$shipment", "days": "$same"},
            }
        )
        population["population"]["covers"].append("dispatch_integer_days")
        population["facts"]["dispatch_integer_days"] = [{"shipment": "SHIP-17", "days": 2}]
    elif surface == "direct-duration" or case["parameters"].get("untagged_integer"):
        model["constraints"][0]["antecedent"].append(
            {
                "fact_type": "dispatch_allowance_days",
                "bind": {"shipment": "$shipment", "days": "$days"},
            }
        )
        if case["parameters"].get("integer"):
            model["object_types"].append(
                {"id": "dispatch_integer", "kind": "value", "primitive": "Integer"}
            )
            model["fact_types"].append(
                {
                    "id": "dispatch_integer_days",
                    "reading": "{DispatchShipment} has integer days {DispatchInteger}",
                    "roles": [
                        {"object_type": "dispatch_shipment", "role_name": "shipment"},
                        {"object_type": "dispatch_integer", "role_name": "days"},
                    ],
                }
            )
            model["constraints"][0]["antecedent"].append(
                {
                    "fact_type": "dispatch_integer_days",
                    "bind": {"shipment": "$shipment", "days": "$other"},
                }
            )
            population["population"]["covers"].append("dispatch_integer_days")
            population["facts"]["dispatch_integer_days"] = [{"shipment": "SHIP-17", "days": 2}]
        else:
            model["constraints"][0]["antecedent"].append(
                {
                    "fact_type": "dispatch_allowance_days",
                    "bind": {"shipment": "$shipment", "days": "$other"},
                }
            )
            if case["parameters"].get("larger"):
                population["facts"]["dispatch_allowance_days"].append(
                    {"shipment": "SHIP-17", "days": 3}
                )
        model["constraints"][0]["consequent"]["comparison"] = {
            "operator": ">=",
            "left": "$days",
            "right": 2 if case["parameters"].get("untagged_integer") else "$other",
        }
    elif surface == "duration-range":
        model["constraints"][0]["consequent"]["comparison"]["left"] = "$pickup"
        endpoint = case["parameters"].get("invalid_endpoint", 3)
        model["constraints"].append(
            {
                "type": "value",
                "range": {"min": 0, "max": endpoint},
                "object_type": "dispatch_allowance",
                "source": "user-supplied",
                "status": "confirmed",
                "modality": "alethic",
                "provenance": {"user_quote": "An allowance is within the declared interval."},
            }
        )
        if case["parameters"].get("outside"):
            population["facts"]["dispatch_allowance_days"][0]["days"] = 4
        elif "invalid_endpoint" not in case["parameters"]:
            population["facts"]["dispatch_allowance_days"].extend(
                [{"shipment": "SHIP-17", "days": 0}, {"shipment": "SHIP-17", "days": 3}]
            )
    elif surface == "deep-term":
        term: object = "$pickup"
        for _ in range(case["parameters"]["levels"]):
            term = {"fn": "date_add", "args": [term, {"duration_days": 0}]}
        model["constraints"][0]["consequent"]["comparison"]["left"] = term


def _command(
    case: dict, model_path: Path, population_path: Path, tmp_path: Path
) -> tuple[str, ...]:
    surface = case["surface"]
    if surface in {"check", "bulk-check", "direct-duration", "duration-range"}:
        return ("check", str(model_path), str(population_path), "--format", "json")
    if surface in {"validate", "deep-term", "forbidden-site", "cross-primitive-binding"}:
        return ("validate", str(model_path), "--format", "json")
    if surface == "synth":
        return ("synth", str(model_path), "--out", str(tmp_path / "synth"), "--seed", "1")
    if surface == "measure":
        return ("measure", str(model_path), "--populations", str(tmp_path / "populations"))
    if surface == "codegen":
        return ("codegen", str(model_path), "--out", str(tmp_path / "project"))
    if surface == "conformance":
        return ("conformance", str(model_path), str(tmp_path / "project"))
    if surface == "diff":
        return ("diff", str(model_path), str(model_path), "--format", "json")
    if surface == "extract":
        return ("extract", str(model_path), "--out", str(tmp_path / "extract"))
    if surface == "doccheck":
        return (
            "doccheck",
            str(model_path),
            str(tmp_path / "manifest.json"),
            "--artifacts",
            str(tmp_path),
        )
    if surface == "export-pyrel":
        return ("export", "pyrel", str(model_path), "--out", str(tmp_path / "artifact.py"))
    raise AssertionError(f"no public command for {surface}")


def _transition_case(case: dict, model: dict, population: dict, tmp_path: Path) -> tuple[str, ...]:
    """Build a bound walk from the authored operation and population values."""
    late = case["parameters"]["mutation"] == "late"
    operation = {
        "id": "reschedule" if late else "mark_label",
        "reading": "{DispatchShipment} reschedules"
        if late
        else "{DispatchShipment} receives {DispatchLabel}",
        "parameters": (
            [
                {"name": "shipment", "object_type": "dispatch_shipment"},
                {"name": "old_pickup", "object_type": "dispatch_calendar_day"},
                {"name": "new_pickup", "object_type": "dispatch_calendar_day"},
            ]
            if late
            else [
                {"name": "shipment", "object_type": "dispatch_shipment"},
                {"name": "label", "object_type": "dispatch_label"},
            ]
        ),
        "preconditions": [],
        "effects": (
            [
                {
                    "retract": {
                        "fact_type": "dispatch_pickup_on",
                        "bind": {"shipment": "$shipment", "pickup": "$old_pickup"},
                    }
                },
                {
                    "assert": {
                        "fact_type": "dispatch_pickup_on",
                        "bind": {"shipment": "$shipment", "pickup": "$new_pickup"},
                    }
                },
            ]
            if late
            else [
                {
                    "assert": {
                        "fact_type": "dispatch_packaging_label",
                        "bind": {"shipment": "$shipment", "label": "$label"},
                    }
                }
            ]
        ),
        "frame": {"modality": "alethic"},
        "source": "user-supplied",
        "status": "confirmed",
        "provenance": {"user_quote": "The declared step changes only its effect."},
    }
    model["operations"] = [operation]
    pre = deepcopy(population)
    post = deepcopy(population)
    if late:
        post["facts"]["dispatch_pickup_on"][0]["pickup"] = "2026-10-03"
    else:
        pre["facts"]["dispatch_pickup_on"][0]["pickup"] = {"$opaque": "pickup"}
        post["facts"]["dispatch_pickup_on"][0]["pickup"] = {"$opaque": "pickup"}
        pre["population"]["covers"].append("dispatch_packaging_label")
    pre_path = tmp_path / "pre.json"
    post_path = tmp_path / "post.json"
    pre_path.write_text(json.dumps(pre) + "\n")
    if not late:
        post["facts"]["dispatch_packaging_label"] = [{"shipment": "SHIP-17", "label": "READY"}]
        post["population"]["covers"].append("dispatch_packaging_label")
    post_path.write_text(json.dumps(post) + "\n")
    model_path, _ = _write(tmp_path, model, population)
    loaded = load_model(model_path)
    steps = {
        "steps_schema": 1,
        "model": "model.orm.yaml",
        "model_digest": model_digest(loaded),
        "operations_digest": operations_digest(loaded.operations),
        "steps": [
            {
                "op": operation["id"],
                "bindings": (
                    {"shipment": "SHIP-17", "old_pickup": "2026-10-02", "new_pickup": "2026-10-03"}
                    if late
                    else {"shipment": "SHIP-17", "label": "READY"}
                ),
            }
        ],
    }
    steps_path = tmp_path / "steps.json"
    steps_path.write_text(json.dumps(steps) + "\n")
    return (
        "check",
        str(model_path),
        "--pre",
        str(pre_path),
        "--steps",
        str(steps_path),
        "--post",
        str(post_path),
        "--format",
        "json",
    )


@pytest.mark.parametrize("case", INPUTS, ids=lambda row: row["id"])
def test_phase1_corpus(case: dict, tmp_path: Path, request: pytest.FixtureRequest) -> None:
    answer = ANSWERS[case["id"]]
    surface = case["surface"]
    if surface in {"legacy-diff", "legacy-numeric", "legacy-date"}:
        if surface == "legacy-diff":
            path = LEGACY / "dispatch/model.orm.yaml"
            result = _cli("diff", str(path), str(path), "--format", "json")
        elif surface == "legacy-numeric":
            base = ROOT / "tests/fixtures/v62-phase3"
            result = _cli(
                "check",
                str(base / "models/exact-terms.orm.yaml"),
                str(base / "populations/term-clean.pop.yaml"),
                "--format",
                "json",
            )
        else:
            result = _cli(
                "check",
                str(LEGACY / "dispatch/model.orm.yaml"),
                str(LEGACY / "dispatch/population.pop.json"),
                "--format",
                "json",
            )
        assert result.returncode == answer["expected_exit"], result.stdout + result.stderr
        if surface == "legacy-diff":
            assert hashlib.sha256(result.stdout.encode()).hexdigest() == answer["stdout_sha256"]
        else:
            portable = json.loads((LEGACY / "phase1-portable-stdout.json").read_text())
            # Only the two checked operator coordinates vary between checkouts.
            payload = json.loads(result.stdout)
            assert payload["model"] == str(path if surface == "legacy-diff" else (
                base / "models/exact-terms.orm.yaml" if surface == "legacy-numeric"
                else LEGACY / "dispatch/model.orm.yaml"
            ))
            assert payload["population"] == str(
                base / "populations/term-clean.pop.yaml" if surface == "legacy-numeric"
                else LEGACY / "dispatch/population.pop.json"
            )
            assert result.stdout.count(str(ROOT)) == 2
            normalized = result.stdout.replace(str(ROOT), "<PROJECT_ROOT>")
            assert hashlib.sha256(normalized.encode()).hexdigest() == portable[case["id"]]
        return
    if surface == "package-pins":
        canonical = ROOT / "src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json"
        vendored = ROOT / "src/gnd/schema/orm-meta.schema.json"
        assert canonical.read_bytes() == vendored.read_bytes()
        schema = json.loads(canonical.read_text())
        assert "Duration" in schema["$defs"]["object_type"]["properties"]["primitive"]["enum"]
        assert "date_add" in canonical.read_text()
        return
    if surface == "report-version":
        legacy = _cli(
            "check",
            str(LEGACY / "dispatch/model.orm.yaml"),
            str(LEGACY / "dispatch/population.pop.json"),
            "--format",
            "json",
        )
        assert legacy.returncode == 0
        assert _json_result(legacy)["schema_version"] == 7
        _temporal_control(case["domain"], tmp_path)
        return

    model, population = _load(case["domain"])
    for edit in case["edits"]:
        _edit(model if edit["target"] == "model" else population, edit)
    _custom_model(case, model, population)
    if surface == "bulk-check":
        _bulk(population, case["parameters"]["count"])
    model_path, population_path = _write(tmp_path, model, population)

    if case["id"] not in {"B01-dispatch-equal", "B02-release-equal"}:
        _temporal_control(case["domain"], tmp_path / "control")

    command = (
        _transition_case(case, model, population, tmp_path)
        if surface == "transition"
        else _command(case, model_path, population_path, tmp_path)
    )
    started = time.monotonic()
    result = _cli(*command)
    elapsed = time.monotonic() - started
    assert result.returncode == answer["expected_exit"], result.stdout + result.stderr
    if surface == "bulk-check":
        request.node.user_properties.append(("temporal_cli_seconds", elapsed))
        assert elapsed < 5, f"temporal work limit took {elapsed:.2f}s"
    if command[-1] == "json" and result.stdout.startswith("{"):
        payload = _json_result(result)
        assert payload["exit_code"] == answer["expected_exit"]
        if answer["expected_exit"] in (0, 1, 2, 4) and surface in {
            "check",
            "bulk-check",
            "direct-duration",
            "duration-range",
        }:
            assert payload["schema_version"] == 11
        if "expected_verdict" in answer:
            rows = payload["verdicts"]
            if surface == "transition":
                rows = payload["transition"]["post_snapshot"]["verdicts"]
            ref = answer.get("expected_constraint_ref", "constraints[0]")
            target = next(row for row in rows if row["constraint_ref"] == ref)
            assert target["verdict"] == answer["expected_verdict"]
            if "expected_reason_code" in answer:
                assert target["reason_code"] == answer["expected_reason_code"]
        if "overall_deciding_ref" in answer:
            deciding = next(
                row
                for row in payload["verdicts"]
                if row["constraint_ref"] == answer["overall_deciding_ref"]
            )
            assert deciding["verdict"] == "fail"
    if surface in {
        "synth",
        "measure",
        "codegen",
        "conformance",
        "diff",
        "extract",
        "doccheck",
        "export-pyrel",
    }:
        assert "temporal" in (result.stdout + result.stderr).lower()
        assert not (tmp_path / "project").exists()
        assert not (tmp_path / "artifact.py").exists()
