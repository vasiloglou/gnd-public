"""GC1 public comparison expectations exercised against the normal CLI."""
from __future__ import annotations

import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML
from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
EXPECTED = json.loads(
    (ROOT / ".gnd-planning/milestones/guarded-rule-clauses/corpus/GC1/expected.json").read_bytes()
)
BASE = ROOT / "tests/fixtures/models/guarded_minimal.orm.yaml"


def _direct(operator="in", right=None):
    model = YAML(typ="safe").load(BASE)
    model["constraints"] = model["constraints"][:1]
    model["constraints"][0]["consequent"]["comparison"] = {
        "operator": operator,
        "left": "$a",
        "right": [1000, 1500.0] if right is None else right,
    }
    return model


def _existential(model):
    rule = model["constraints"][0]
    witness = rule["antecedent"].pop()
    comparison = rule["consequent"]["comparison"]
    rule["consequent"] = {"exists": {"atoms": [witness], "where": [comparison]}}


def _derived(model):
    rule = model["constraints"].pop()
    model["fact_types"].append({
        "id": "eligible_expense",
        "reading": "{Expense} is eligible",
        "roles": [{"object_type": "expense", "role_name": "expense"}],
        "derivation": "derived",
        "derivation_rule": {
            "body": rule["antecedent"],
            "where": [rule["consequent"]["comparison"]],
            "head": {"expense": "$e"},
        },
    })


def _write_json(tmp_path, name, document):
    path = tmp_path / name
    path.write_text(json.dumps(document), encoding="utf-8")
    return str(path)


@pytest.mark.parametrize(("case", "transform"), [
    ("guarded_numeric_membership", None),
    ("guarded_exists_membership", _existential),
    ("derivation_where_membership", _derived),
])
def test_validation_admits_membership_at_comparison_sites(tmp_path, case, transform):
    model = _direct()
    if transform is not None:
        transform(model)
    path = _write_json(tmp_path, "model.orm.json", model)
    result = run_main(["validate", path, "--format", "json"])
    assert result.returncode == EXPECTED["validation"][case], (result.stdout, result.stderr)


@pytest.mark.parametrize(("case", "right"), [
    ("guarded_empty_list", []),
    ("guarded_oversized_list", list(range(1025))),
    ("guarded_variable_member", ["$a"]),
    ("guarded_nested_member", [[1500]]),
    ("guarded_mixed_nonnumeric_members", [1500, "other"]),
    ("guarded_incompatible_left", [True, False]),
])
def test_validation_refuses_malformed_membership(tmp_path, case, right):
    path = _write_json(tmp_path, "model.orm.json", _direct(right=right))
    result = run_main(["validate", path, "--format", "json"])
    assert result.returncode == EXPECTED["validation"][case], (result.stdout, result.stderr)


@pytest.mark.parametrize(("case", "operator", "amount"), [
    ("in_contains", "in", 1500),
    ("in_excludes", "in", 2000),
    ("not_in_contains", "not in", 1500),
    ("not_in_excludes", "not in", 2000),
])
@pytest.mark.parametrize("shape", ["direct", "exists"])
def test_guarded_membership_verdicts(tmp_path, case, operator, amount, shape):
    model = _direct(operator)
    if shape == "exists":
        _existential(model)
    model_path = _write_json(tmp_path, "model.orm.json", model)
    pop = {
        "population": {
            "model": "model.orm.json",
            "model_id": model["model_id"],
            "source": "fixture",
            "covers": ["expense_in_category", "expense_has_amount"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": amount}],
        },
    }
    population_path = _write_json(tmp_path, "population.json", pop)
    run = run_main(["check", model_path, population_path, "--format", "json"])
    expected = EXPECTED["check"][case]
    assert run.returncode == expected["exit"], (run.stdout, run.stderr)
    report = json.loads(run.stdout)
    assert [row["verdict"] for row in report["verdicts"] if row["constraint_type"] == "guarded"] == [
        expected["guarded"],
    ]


@pytest.mark.parametrize("operator", ["in", "not in"])
def test_synth_membership_constructs_both_reachable_verdicts(tmp_path, operator):
    path = _write_json(tmp_path, "model.orm.json", _direct(operator))
    output = tmp_path / "cases"
    result = run_main(["synth", path, "--guarded-cases", "--out", str(output)])
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((output / "guarded-cases.json").read_bytes())
    assert manifest["schema_version"] == EXPECTED["synth"]["manifest"]
    rule, = manifest["rules"]
    assert rule["reason"] is None
    assert sorted(case["kind"] for case in rule["cases"]) == EXPECTED["synth"]["reachable"]
    assert all(case["binding_count"] > 0 for case in rule["cases"])


@pytest.mark.parametrize(("operator", "reason_key"), [
    ("in", "in_covers_boolean_domain"),
    ("not in", "not_in_covers_boolean_domain"),
])
def test_synth_membership_proves_an_exhausted_boolean_domain(tmp_path, operator, reason_key):
    model = _direct(operator, [True, False])
    amount_type = next(item for item in model["object_types"] if item["id"] == "amount")
    amount_type["primitive"] = "Boolean"
    path = _write_json(tmp_path, "model.orm.json", model)
    output = tmp_path / "cases"
    result = run_main(["synth", path, "--guarded-cases", "--out", str(output)])
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((output / "guarded-cases.json").read_bytes())
    rule, = manifest["rules"]
    assert rule["reason"] == EXPECTED["synth"][reason_key]
    assert rule["cases"] == []
