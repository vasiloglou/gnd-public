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


def test_membership_runtime_keeps_typed_values_and_unavailable_terms_distinct():
    from gnd.terms import compare_terms

    assert compare_terms("in", 1, [1.0], {}).value is True
    assert compare_terms("in", {"date": "2024-02-29"}, [{"date": "2024-02-29"}], {}).value is True
    assert compare_terms("in", {"duration_days": 1}, [{"duration_days": 1}], {}).value is True
    for left, right in (
        (True, [1]),
        ("2024-02-29", [{"date": "2024-02-29"}]),
        ("1", [1]),
        (1, [{"duration_days": 1}]),
    ):
        result = compare_terms("not in", left, right, {})
        assert result.value is None
        assert result.reason == "term:values-not-comparable"
    assert compare_terms("in", "$missing", [1], {}).reason == "term:unbound-variable"
    assert compare_terms("=", True, 1, {}).value is True


def test_membership_validation_warns_at_duplicate_and_outside_domain_paths(tmp_path):
    from gnd.model import load_model

    model = _direct(right=[1500, 1500.0, 2500])
    model["constraints"].append({
        "type": "value", "object_type": "amount", "allowed": [1500],
        "source": "explicit", "modality": "alethic", "status": "confirmed",
        "provenance": {"user_quote": "The amount must be 1500."},
    })
    loaded = load_model(_write_json(tmp_path, "model.orm.json", model))
    warnings = {(item.rule_id, item.path) for item in loaded.warnings}
    assert ("semantic:membership-duplicate", "$.constraints[0].consequent.comparison.right") in warnings
    assert ("semantic:guarded-literal-outside-domain", "$.constraints[0].consequent.comparison.right[2]") in warnings


def test_membership_precompiles_for_many_bindings():
    from time import perf_counter

    from gnd.terms import compare_terms, compile_membership

    started = perf_counter()
    members = compile_membership(list(range(1024)))
    assert members is not None
    for index in range(10_000):
        verdict = compare_terms("in", "$x", members, {"x": index})
        assert verdict.value is (index < 1024)
        assert verdict.operations == 1
    assert perf_counter() - started < 5.0


@pytest.mark.parametrize("operator", ["in", "not in"])
def test_membership_matches_independent_covered_helper(tmp_path, operator):
    from random import Random

    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population

    native_model = _direct(operator, [1000, 1500])
    helper_model = _direct(operator, [1000, 1500])
    rule = helper_model["constraints"][0]
    helper_rule = {
        "id": "eligible_expense",
        "reading": "{Expense} is eligible",
        "roles": [{"object_type": "expense", "role_name": "expense"}],
        "derivation": "semiderived",
        "derivation_rule": {
            "clauses": [
                {
                    "body": [
                        {"fact_type": "expense_has_amount", "bind": {"expense": "$e", "amount": literal}},
                    ],
                    "head": {"expense": "$e"},
                }
                for literal in (1000, 1500)
            ],
        },
    }
    helper_model["fact_types"].append(helper_rule)
    rule["consequent"] = {
        "atom" if operator == "in" else "absence": {
            "fact_type": "eligible_expense", "bind": {"expense": "$e"},
        },
    }
    models = [
        load_model(_write_json(tmp_path, filename, document))
        for filename, document in (("native.orm.json", native_model), ("helper.orm.json", helper_model))
    ]
    rng = Random(195)
    observed = set()
    for _ in range(200):
        amounts = [rng.choice((1000, 1500, 1700, 2900)) for _ in range(4)]
        facts = {
            "expense_in_category": [{"expense": i, "category": "travel"} for i in range(1, 5)],
            "expense_has_amount": [{"expense": i, "amount": amount} for i, amount in enumerate(amounts, 1)],
        }

        def verdict(model, facts):
            covered = set(facts)
            if model is models[1]:
                covered.add("eligible_expense")
            population_path = _write_json(tmp_path, "population.json", {
                "population": {
                    "model": "model.orm.json", "model_id": model.model_id,
                    "source": "fixture", "covers": sorted(covered),
                },
                "instances": {},
                "facts": facts,
            })
            population = load_population(population_path, model=model)
            assert covered == set(population.covers)
            report = check(model, population)
            result, = [row for row in report.verdicts if row.constraint_type == "guarded"]
            assert result.binding_count == 4
            return result.verdict, {
                row["$e"] for row in (result.offending_facts or [])
            }

        first = verdict(models[0], facts)
        assert first == verdict(models[1], facts)
        observed.add(first[0])
    assert observed == {"pass", "fail"}


@pytest.mark.parametrize("shape", ["direct", "exists", "derived"])
def test_pyrel_rules_refuses_unsupported_membership_without_a_traceback(tmp_path, shape):
    from gnd.export.pyrel_rules import ExportInputError, render

    model = _direct()
    if shape != "direct":
        (_existential if shape == "exists" else _derived)(model)
    filename = _write_json(tmp_path, "model.orm.json", model)
    with pytest.raises(ExportInputError, match="^membership-unsupported$"):
        render(Path(filename), "duckdb")


def test_guarded_membership_verbalizes_the_ordered_values():
    from gnd.model_verbalization import _guarded_cnl

    first = _direct("in", [1, 3])["constraints"][0]
    second = _direct("not in", [3, 1])["constraints"][0]
    assert "then $a is one of 1, 3." in _guarded_cnl(first)
    assert "then $a is none of 3, 1." in _guarded_cnl(second)


@pytest.mark.parametrize(("primitive", "left", "right", "value"), [
    ("Date", "$a", [{"date": "2024-02-29"}], "2024-02-29"),
    ("Date", {"fn": "date_add", "args": ["$a", {"duration_days": 1}]},
     [{"date": "2024-02-29"}], "2024-02-28"),
    ("Duration", "$a", [{"duration_days": 1}], 1),
])
@pytest.mark.parametrize("shape", ["direct", "exists"])
def test_membership_temporal_terms_follow_the_declared_domain(tmp_path, primitive, left, right, value, shape):
    model = _direct("in", right)
    model["version"] = 3
    amount = next(item for item in model["object_types"] if item["id"] == "amount")
    amount["primitive"] = primitive
    model["constraints"][0]["consequent"]["comparison"]["left"] = left
    if shape == "exists":
        _existential(model)
    model_path = _write_json(tmp_path, "model.orm.json", model)
    pop_path = _write_json(tmp_path, "population.json", {
        "population": {
            "model": "model.orm.json", "model_id": model["model_id"], "source": "fixture",
            "covers": ["expense_in_category", "expense_has_amount"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": value}],
        },
    })
    run = run_main(["check", model_path, pop_path, "--format", "json"])
    assert run.returncode == 0, run.stdout
    report = json.loads(run.stdout)
    assert [row["verdict"] for row in report["verdicts"] if row["constraint_type"] == "guarded"] == ["pass"]


@pytest.mark.parametrize("clauses", [False, True])
def test_derivation_where_membership_checks_the_computed_extension(tmp_path, clauses):
    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population

    document = _direct()
    _derived(document)
    if clauses:
        fact_type = document["fact_types"][-1]
        fact_type["derivation_rule"] = {"clauses": [fact_type["derivation_rule"]]}
    model = load_model(_write_json(tmp_path, "model.orm.json", document))
    good = _write_json(tmp_path, "population.json", {
        "population": {
            "model": "model.orm.json", "model_id": model.model_id,
            "source": "fixture", "covers": ["expense_in_category", "expense_has_amount", "eligible_expense"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}, {"expense": 2, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": 1500}, {"expense": 2, "amount": 2500}],
            "eligible_expense": [{"expense": 1}],
        },
    })
    population = load_population(good, model=model)
    report = check(model, population)
    assert [(row.fact_type, row.verdict) for row in report.derivations] == [("eligible_expense", "pass")]


def test_untyped_runtime_variable_cannot_inherit_date_kind_from_list():
    from gnd.terms import compare_terms

    comparison = compare_terms(
        "in", "$value", [{"date": "2024-02-29"}], {"value": "2024-02-29"}
    )
    assert comparison.reason == "term:values-not-comparable"


def test_pyrel_membership_preserves_reference_refusal_order(tmp_path, monkeypatch):
    from gnd.export import pyrel_rules

    def refuse_reference(*args):
        raise pyrel_rules.ExportInputError("missing reference fixture")

    monkeypatch.setattr(pyrel_rules, "_bind_reference", refuse_reference)
    path = Path(_write_json(tmp_path, "model.orm.json", _direct()))
    with pytest.raises(pyrel_rules.ExportInputError, match="^missing reference fixture$"):
        pyrel_rules.render(path, "duckdb")


@pytest.mark.parametrize("exporter", ["lean", "souffle"])
def test_finite_exporters_refuse_guarded_membership_explicitly(exporter):
    from gnd.export.lean import render_lean
    from gnd.export.souffle import render_souffle

    model = _direct()
    population = {
        "population": {
            "model": "model.orm.json", "model_id": model["model_id"], "source": "fixture",
            "covers": ["expense_in_category", "expense_has_amount", "expense_has_status"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": 1500}],
            "expense_has_status": [],
        },
    }
    raw_model, raw_population = (json.dumps(value).encode() for value in (model, population))
    if exporter == "lean":
        result = render_lean(raw_model, raw_population, toolchain="leanprover/lean4:v4.34.0")
    else:
        result = render_souffle(raw_model, raw_population, model_format="json")
    assert (result.exit_code, result.reason) == (2, "membership-unsupported")


def test_derivation_compiles_and_charges_members_under_declared_temporal_type(tmp_path):
    from gnd.extensions import structured_extension_view
    from gnd.model import load_model
    from gnd.population import load_population

    model_doc = _direct("in", [{"date": "2024-02-29"}, {"date": "2024-03-01"}])
    model_doc["version"] = 3
    next(ot for ot in model_doc["object_types"] if ot["id"] == "amount")["primitive"] = "Date"
    _derived(model_doc)
    model = load_model(_write_json(tmp_path, "model.orm.json", model_doc))
    population_path = _write_json(tmp_path, "population.json", {
        "population": {
            "model": "model.orm.json", "model_id": model.model_id, "source": "fixture",
            "covers": ["expense_in_category", "expense_has_amount"],
        },
        "instances": {},
        "facts": {
            "expense_in_category": [{"expense": 1, "category": "travel"}],
            "expense_has_amount": [{"expense": 1, "amount": "2024-02-29"}],
        },
    })
    population = load_population(population_path, model=model)
    view = structured_extension_view(model, population)
    assert [row["expense"] for row in view.facts["eligible_expense"]] == [1]
    assert view.work.term_operations == 3


def test_synth_accepts_a_float_spelling_in_an_integer_membership_list(tmp_path):
    path = _write_json(tmp_path, "model.orm.json", _direct("in", [1500.0]))
    output = tmp_path / "cases"
    result = run_main(["synth", path, "--guarded-cases", "--out", str(output)])
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((output / "guarded-cases.json").read_bytes())
    rule, = manifest["rules"]
    assert rule["reason"] is None
    assert sorted(case["kind"] for case in rule["cases"]) == EXPECTED["synth"]["reachable"]
    for case in rule["cases"]:
        checked = run_main(["check", path, str(output / case["population"]), "--format", "json"])
        report = json.loads(checked.stdout)
        guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
        assert guard["verdict"] == case["verdict"]
