"""Public guarded antecedent outcomes for GC2."""
import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

BASE = Path(__file__).resolve().parent / "fixtures/models/guarded_minimal.orm.yaml"


def _case(tmp_path, *, cover=True, statuses=(), where=(), negative=True):
    model = YAML(typ="safe").load(BASE)
    rule = model["constraints"][0]
    model["constraints"] = [rule]
    if negative:
        rule["negate"] = [{
            "fact_type": "expense_has_status",
            "bind": {"expense": "$e", "status": "exempt"},
        }]
    if where:
        rule["where"] = list(where)
    covered = ["expense_in_category", "expense_has_amount"]
    facts = {
        "expense_in_category": [{"expense": 1, "category": "travel"}],
        "expense_has_amount": [{"expense": 1, "amount": 2500}],
    }
    if cover:
        covered.append("expense_has_status")
        facts["expense_has_status"] = list(statuses)
    pop = {
        "population": {
            "model": "model.orm.json",
            "model_id": model["model_id"],
            "source": "fixture",
            "covers": covered,
        },
        "instances": {},
        "facts": facts,
    }
    paths = [tmp_path / "model.orm.json", tmp_path / "population.json"]
    for path, content in zip(paths, (model, pop), strict=True):
        path.write_text(json.dumps(content), encoding="utf-8")
    return tuple(map(str, paths))


@pytest.mark.parametrize(("coverage", "matches", "verdict", "count"), [
    (True, False, "fail", 1),
    (True, True, "vacuous", 0),
    (False, False, "unchecked", 0),
])
def test_negative_relation_uses_actual_coverage(tmp_path, coverage, matches, verdict, count):
    rows = [{"expense": 1, "status": "exempt"}] if matches else []
    paths = _case(tmp_path, cover=coverage, statuses=rows)
    run = run_main(["check", *paths, "--guarded-diagnostics", "--format", "json"])
    report = json.loads(run.stdout)
    guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == verdict
    assert guard["guarded_antecedent"] == {
        "binding_count": count, "first_empty_atom_index": None,
    }


def test_definite_where_exclusion_wins_over_unknown_negation(tmp_path):
    paths = _case(tmp_path, cover=False, where=[{"operator": "in", "left": "$a", "right": [100]}])
    run = run_main(["check", *paths, "--guarded-diagnostics", "--format", "json"])
    report = json.loads(run.stdout)
    guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == "vacuous"
    assert guard["guarded_antecedent"]["binding_count"] == 0


def test_unsafe_negative_binding_is_refused(tmp_path):
    model_path, _ = _case(tmp_path)
    path = Path(model_path)
    model = json.loads(path.read_text())
    model["constraints"][0]["negate"][0]["bind"]["expense"] = "$unbound"
    path.write_text(json.dumps(model), encoding="utf-8")
    run = run_main(["validate", model_path, "--format", "json"])
    assert run.returncode == 3
    assert b"semantic:guarded-filter-unbound" in run.stdout
