"""RED runtime cases for the owner-authored Phase 3 answer key."""

from __future__ import annotations

import copy
import json
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd import api
from gnd.report import load_report_schema

FIXTURE = Path(__file__).parent / "fixtures/v70-phase3"
CASES = {row["id"]: row for row in json.loads((FIXTURE / "cases.json").read_text())["cases"]}
ANSWERS = json.loads((FIXTURE / "answers.json").read_text())["cases"]


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


def run_case(case_id: str, tmp_path: Path) -> dict[str, Any]:
    case = CASES[case_id]
    expected = ANSWERS[case_id]
    model = YAML(typ="safe").load(
        (FIXTURE / case.get("model_file", "model.orm.yaml")).read_text()
    )
    population = json.loads(
        (FIXTURE / case.get("population_file", "population.pop.json")).read_text()
    )
    if case.get("legacy_model"):
        for fact_type in model["fact_types"]:
            fact_type.pop("depends_on", None)
    model = _patch(model, case.get("model_edits", []))
    population = _patch(population, case.get("population_edits", []))
    model_path = tmp_path / "model.orm.yaml"
    population_path = tmp_path / "population.pop.json"
    with model_path.open("w") as stream:
        YAML().dump(model, stream)
    population_path.write_text(json.dumps(population, ensure_ascii=False))
    if case["admission"]:
        payload = api.check(model_path, population_path, admission=True)
    else:
        payload = api.check(model_path, population_path)
    assert payload["exit_code"] == expected["exit"], case_id
    assert payload["schema_version"] == expected["schema_version"], case_id
    verdicts = [
        {key: row[key] for key in ("constraint_ref", "verdict", "reason_code")}
        for row in payload["verdicts"]
    ]
    assert verdicts == expected["verdicts"], case_id
    if "derivations" in expected:
        derivations = [
            {key: row[key] for key in ("derivation_ref", "verdict", "reason_code")}
            for row in payload["derivations"]
        ]
        assert derivations == expected["derivations"], case_id
    if case["admission"]:
        assert payload["admission"] == expected["admission"], case_id
    else:
        assert "admission" not in payload
    from jsonschema import Draft202012Validator

    assert not list(Draft202012Validator(load_report_schema()).iter_errors(payload)), case_id
    return payload


OPAQUE_CASES = [
    case_id for case_id in CASES if case_id.startswith(("J", "L", "M", "O"))
]


@pytest.mark.parametrize("case_id", OPAQUE_CASES)
def test_opaque_and_format_cases_match_author_answer(case_id: str, tmp_path: Path) -> None:
    run_case(case_id, tmp_path)
