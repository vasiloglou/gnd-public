"""Initial disjunctive guarded consequent decision table for GC3."""
import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

BASE = Path(__file__).resolve().parent / "fixtures/models/guarded_minimal.orm.yaml"
LOW = {"comparison": {"operator": "<=", "left": "$a", "right": 1000}}
HIGH = {"comparison": {"operator": ">=", "left": "$a", "right": 2500}}
UNKNOWN = {
    "comparison": {"operator": "=", "left": {"fn": "mod", "args": ["$a", 0]}, "right": 0}
}


def _case(tmp_path, alternatives, amount):
    model = YAML(typ="safe").load(BASE)
    rule = model["constraints"][0]
    model["constraints"] = [rule]
    rule["consequent"] = {"any_of": alternatives}
    population = {
        "population": {
            "model": "model.orm.json", "model_id": model["model_id"],
            "source": "fixture", "covers": ["expense_in_category", "expense_has_amount"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": amount}],
        },
    }
    paths = [tmp_path / "model.orm.json", tmp_path / "population.json"]
    for path, content in zip(paths, (model, population), strict=True):
        path.write_text(json.dumps(content), encoding="utf-8")
    return tuple(map(str, paths))


@pytest.mark.parametrize(("alternatives", "amount", "wanted"), [
    ([LOW, HIGH], 500, "pass"),
    ([LOW, HIGH], 2600, "pass"),
    ([LOW, HIGH], 1500, "fail"),
    ([UNKNOWN, HIGH], 2600, "pass"),
    ([UNKNOWN, HIGH], 1500, "unchecked"),
])
def test_any_of_uses_three_valued_disjunction(tmp_path, alternatives, amount, wanted):
    paths = _case(tmp_path, alternatives, amount)
    outcome = run_main(["check", *paths, "--format", "json"])
    payload = json.loads(outcome.stdout)
    verdict, = [row for row in payload["verdicts"] if row["constraint_type"] == "guarded"]
    assert verdict["verdict"] == wanted


@pytest.mark.parametrize("alternatives", [[LOW], [{"any_of": [LOW, HIGH]}, HIGH]])
def test_any_of_refuses_insufficient_arity_and_nesting(tmp_path, alternatives):
    model, _ = _case(tmp_path, alternatives, 1500)
    result = run_main(["validate", model, "--format", "json"])
    assert result.returncode == 3


def test_any_of_opt_in_reports_each_failed_alternative(tmp_path):
    paths = _case(tmp_path, [LOW, HIGH], 1500)
    plain = run_main(["check", *paths, "--rule-ids", "--format", "json"])
    opted = run_main(["check", *paths, "--guarded-diagnostics", "--format", "json"])
    ordinary, diagnosed = map(lambda reply: json.loads(reply.stdout), (plain, opted))
    assert ordinary["schema_version"] == 15
    assert diagnosed["schema_version"] == 17
    assert "guarded_alternatives" not in ordinary["verdicts"][0]
    rows = diagnosed["verdicts"][0]["guarded_alternatives"]
    assert len(rows) == 1
    assert rows[0]["binding"] == {"$e": 1, "$a": 1500}
    assert [
        (row["index"], row["reason"]) for row in rows[0]["alternatives"]
    ] == [(0, "false-comparison"), (1, "false-comparison")]
