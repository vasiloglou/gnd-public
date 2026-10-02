"""RED runtime checks against the separately approved Phase 4 answer key."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd import api
from gnd.model import load_model
from gnd.transition import model_digest, operations_digest

FIXTURE = Path(__file__).parent / "fixtures/v70-phase4"
CASES = {row["id"]: row for row in json.loads((FIXTURE / "cases.json").read_text())["cases"]}
ANSWERS = json.loads((FIXTURE / "answers.json").read_text())["cases"]


def _canonical_payload(payload: dict, paths: dict[str, Path]) -> str:
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    for label, path in paths.items():
        raw = raw.replace(str(path), f"<{label}>")
    return raw + "\n"


def _patch(document: Any, edits: list[dict]) -> Any:
    result = copy.deepcopy(document)
    for edit in edits:
        segments = edit["path"].split("/")[1:]
        parent = result
        for segment in segments[:-1]:
            parent = parent[int(segment)] if isinstance(parent, list) else parent[segment]
        last = segments[-1]
        if isinstance(parent, list):
            if edit["op"] == "add":
                parent.insert(len(parent) if last == "-" else int(last), copy.deepcopy(edit["value"]))
            elif edit["op"] == "replace":
                parent[int(last)] = copy.deepcopy(edit["value"])
            else:
                parent.pop(int(last))
        elif edit["op"] == "remove":
            parent.pop(last)
        else:
            parent[last] = copy.deepcopy(edit["value"])
    return result


def _stage(case_id: str, tmp_path: Path) -> tuple[Path, Path, Path | None]:
    case = CASES[case_id]
    model_doc = YAML(typ="safe").load((FIXTURE / case["model"]).read_text())
    population_doc = json.loads((FIXTURE / case["population"]).read_text())
    model_doc = _patch(model_doc, case.get("model_edits", []))
    population_doc = _patch(population_doc, case.get("population_edits", []))
    model_path = tmp_path / case["model"]
    with model_path.open("w") as stream:
        YAML().dump(model_doc, stream)
    population_path = tmp_path / case["population"]
    population_path.write_text(json.dumps(population_doc, ensure_ascii=False) + "\n")
    if "steps" not in case:
        return model_path, population_path, None
    model = load_model(model_path)
    steps_doc = json.loads((FIXTURE / case["steps"]).read_text())
    steps_doc["model_digest"] = model_digest(model)
    steps_doc["operations_digest"] = operations_digest(model.operations)
    steps_path = tmp_path / case["steps"]
    steps_path.write_text(json.dumps(steps_doc, ensure_ascii=False) + "\n")
    return model_path, population_path, steps_path


@pytest.mark.parametrize("case_id", [case_id for case_id in CASES if not case_id.startswith("T")])
def test_check_case_matches_owner_answer(case_id: str, tmp_path: Path) -> None:
    case = CASES[case_id]
    expected = ANSWERS[case_id]
    model, population, _ = _stage(case_id, tmp_path)
    payload = api.check(model, population, admission=case["admission"])
    assert payload["exit_code"] == expected["exit"], case_id
    assert payload["schema_version"] == expected["schema_version"], case_id
    assert len(payload["derivations"]) == 1, case_id
    actual = payload["derivations"][0]
    wanted = expected["derivations"][0]
    assert actual["verdict"] == wanted["verdict"], case_id
    assert actual["reason_code"] == wanted["reason_code"], case_id
    assert [row["kind"] for row in actual["findings"]] == wanted["findings"], case_id
    if "witnesses" in wanted:
        assert [row["witness"] for row in actual["findings"]] == wanted["witnesses"], case_id
    if case["admission"]:
        assert "admission" in payload, case_id
    else:
        assert "admission" not in payload, case_id
    if case_id == "P01-scalar-control":
        legacy = api.check(model, population)
        assert _canonical_payload(legacy, {"model": model, "population": population}) == (
            FIXTURE / "legacy-v7.json"
        ).read_text(), case_id


@pytest.mark.parametrize("case_id", [case_id for case_id in CASES if case_id.startswith("T")])
def test_walk_case_matches_owner_answer(case_id: str, tmp_path: Path) -> None:
    expected = ANSWERS[case_id]
    model, population, steps = _stage(case_id, tmp_path)
    assert steps is not None
    payload = api.transition(model, population, steps)
    assert payload["exit_code"] == expected["exit"], case_id
    preconditions = [
        row for row in payload["transition"]["steps"][0]["verdicts"]
        if row["kind"] == "precondition"
    ]
    if expected["precondition"] is None:
        assert preconditions == [], case_id
    else:
        assert len(preconditions) == 1, case_id
        assert {key: preconditions[0][key] for key in ("verdict", "reason_code")} == expected["precondition"], case_id
    visited = payload["transition"]["computed_post"]["facts"]["visited"]
    assert {"source": "A", "target": "C"} in visited, case_id
    if case_id == "T02-walk-scalar-control":
        assert _canonical_payload(payload, {"model": model, "population": population, "steps": steps}) == (
            FIXTURE / "legacy-v8.json"
        ).read_text(), case_id
