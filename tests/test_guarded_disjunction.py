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
    ordinary, diagnosed = (json.loads(reply.stdout) for reply in (plain, opted))
    assert ordinary["schema_version"] == 15
    assert diagnosed["schema_version"] == 17
    assert "guarded_alternatives" not in ordinary["verdicts"][0]
    rows = diagnosed["verdicts"][0]["guarded_alternatives"]
    assert len(rows) == 1
    assert rows[0]["binding"] == {"$e": 1, "$a": 1500}
    assert [
        (row["index"], row["reason"]) for row in rows[0]["alternatives"]
    ] == [(0, "false-comparison"), (1, "false-comparison")]


def _read(path):
    return json.loads(Path(path).read_text())


def _write(path, value):
    Path(path).write_text(json.dumps(value), encoding="utf-8")


def _status(status, expense="$e"):
    return {"fact_type": "expense_has_status", "bind": {"expense": expense, "status": status}}


def _check_and_reference(paths):
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.semantic_adapter import adapt_snapshot
    from gnd.semantic_spec import verdict_of

    run = run_main(["check", *paths, "--guarded-diagnostics", "--format", "json"])
    payload = json.loads(run.stdout)
    verdict, = [row for row in payload["verdicts"] if row["constraint_type"] == "guarded"]
    model = load_model(paths[0])
    population = load_population(paths[1], model=model)
    snapshot = adapt_snapshot(model, population)
    constraint, = snapshot.constraints
    reference_verdict, reference_reason, _ = verdict_of(constraint, snapshot)
    assert (reference_verdict, reference_reason) == (verdict["verdict"], verdict["reason_code"])
    return payload, verdict


@pytest.mark.parametrize("coverage", [False, True])
@pytest.mark.parametrize("amount", [1500, 2600])
def test_nonempty_and_unavailable_existential_siblings(tmp_path, coverage, amount):
    witness = {
        "fact_type": "expense_has_amount", "bind": {"expense": 2, "amount": "$n"},
    }
    exists = {"exists": {
        "atoms": [witness, _status("review", 2)],
        "where": [{"operator": "=", "left": {"fn": "mod", "args": [6, "$n"]}, "right": 0}],
    }}
    paths = _case(tmp_path, [exists, HIGH], amount)
    population = _read(paths[1])
    population["facts"]["expense_has_amount"] += [
        {"expense": 2, "amount": 3}, {"expense": 2, "amount": 0},
    ]
    if coverage:
        population["population"]["covers"].append("expense_has_status")
        population["facts"]["expense_has_status"] = [{"expense": 2, "status": "review"}]
    _write(paths[1], population)
    _, verdict = _check_and_reference(paths)
    assert verdict["verdict"] == ("pass" if amount == 2600 else "unchecked")


def test_diagnostics_distinguish_each_unmet_form_and_joint_failure(tmp_path):
    from importlib.resources import files

    import jsonschema

    paths = _case(tmp_path, [
        LOW, {"atom": _status("review")}, {"absence": _status("blocked")},
        {"exists": {"atoms": [_status("$local"), _status("$local", 2)]}},
        {"exists": {"atoms": [_status("delivered"), _status("confirmed", 2)]}},
    ], 1500)
    population = _read(paths[1])
    population["population"]["covers"].append("expense_has_status")
    population["facts"]["expense_has_status"] = [
        {"expense": 1, "status": "blocked"}, {"expense": 2, "status": "confirmed"},
    ]
    _write(paths[1], population)
    payload, verdict = _check_and_reference(paths)
    jsonschema.validate(payload, json.loads(files("gnd").joinpath("report.schema.json").read_text()))
    assert verdict["guarded_alternatives"] == [{
        "binding": {"$e": 1, "$a": 1500},
        "alternatives": [
            {"index": 0, "reason": "false-comparison", "fact_types": [], "atom_indexes": []},
            {"index": 1, "reason": "missing-required-fact", "fact_types": ["expense_has_status"], "atom_indexes": []},
            {"index": 2, "reason": "present-forbidden-fact", "fact_types": ["expense_has_status"], "atom_indexes": []},
            {"index": 3, "reason": "no-joint-witness", "fact_types": [], "atom_indexes": []},
            {"index": 4, "reason": "missing-exists-atom", "fact_types": ["expense_has_status"], "atom_indexes": [0]},
        ],
    }]
    population["facts"]["expense_has_status"].append({"expense": 2, "status": "blocked"})
    _write(paths[1], population)
    _, verdict = _check_and_reference(paths)
    assert verdict["verdict"] == "pass"


def test_alternative_cannot_read_another_alternatives_local_variable(tmp_path):
    local = {"exists": {"atoms": [_status("$local")]}}
    escapes = {"comparison": {"operator": "=", "left": "$local", "right": "approved"}}
    paths = _case(tmp_path, [local, escapes], 1500)
    result = run_main(["validate", paths[0], "--format", "json"])
    assert result.returncode == 3
    assert any(
        issue["rule_id"] == "semantic:guarded-consequent-ground"
        and issue["path"] == "$.constraints[0].consequent.any_of[1].comparison.left"
        for issue in json.loads(result.stdout)["issues"]
    )


def test_work_ceiling_has_precedence_even_with_true_alternative(tmp_path, monkeypatch):
    from gnd import semantic_spec

    paths = _case(tmp_path, [LOW, HIGH], 500)
    monkeypatch.setattr(semantic_spec, "_GUARDED_DISJUNCTION_WORK_LIMIT", 1)
    _, verdict = _check_and_reference(paths)
    assert (verdict["verdict"], verdict["reason_code"]) == ("unchecked", "guarded-disjunction-work-limit")
    assert verdict["guarded_antecedent"]["binding_count"] == 1
    assert "guarded_alternatives" not in verdict


def test_mixed_disjunction_synthesizes_and_verbalizes(tmp_path):
    from gnd.model_verbalization import _guarded_cnl

    paths = _case(tmp_path, [
        LOW, {"absence": _status("blocked")}, {"atom": _status("review")},
        {"exists": {"atoms": [_status("ready"), _status("confirmed", 2)]}},
    ], 1500)
    sentence = _guarded_cnl(_read(paths[0])["constraints"][0])
    assert sentence.count(".") == 1
    assert "at least one of these alternatives must hold" in sentence
    assert "joint assignment" in sentence
    generated = tmp_path / "generated"
    run = run_main(["synth", paths[0], "--guarded-cases", "--out", str(generated), "--seed", "195"])
    assert run.returncode == 0, (run.stdout, run.stderr)
    manifest = _read(generated / "guarded-cases.json")
    rule, = manifest["rules"]
    assert rule["reason"] is None
    assert {case["verdict"] for case in rule["cases"]} == {"fail", "pass"}
    assert all(case["binding_count"] > 0 for case in rule["cases"])


def test_covered_disjunction_and_semiderived_union_agree_on_seeded_populations(tmp_path):
    from random import Random

    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population_bytes
    from gnd.semantic_adapter import adapt_snapshot
    from gnd.semantic_spec import verdict_of

    paths = _case(tmp_path, [LOW, {"atom": _status("review")}], 1500)
    document = _read(paths[0])
    rule = document["constraints"][0]
    status = _status("review")
    antecedent = rule["antecedent"]
    document["fact_types"].append({
        "id": "expense_acceptable",
        "reading": "{Expense} is acceptable at {Amount}",
        "roles": [
            {"role_name": "expense", "object_type": "expense"},
            {"role_name": "amount", "object_type": "amount"},
        ],
        "derivation": "semiderived",
        "derivation_rule": {
            "head": {"expense": "$e", "amount": "$a"},
            "clauses": [
                {"body": antecedent, "where": [LOW["comparison"]]},
                {"body": [*antecedent, status]},
            ],
        },
    })
    rule["consequent"] = {"atom": {
        "fact_type": "expense_acceptable", "bind": {"expense": "$e", "amount": "$a"},
    }}
    helper_path = tmp_path / "helper.orm.json"
    _write(helper_path, document)
    native, helper = load_model(paths[0]), load_model(helper_path)
    case = _read(paths[1])
    case["population"]["covers"].append("expense_has_status")
    rng = Random(195)
    observed = set()
    for _ in range(200):
        facts = case["facts"]
        facts["expense_in_category"] = [{"expense": e, "category": "travel"} for e in range(1, 4)]
        facts["expense_has_amount"] = [{"expense": e, "amount": rng.choice([500, 1500])} for e in range(1, 4)]
        facts["expense_has_status"] = [{"expense": e, "status": "review"} for e in range(1, 4) if rng.randrange(2)]
        encoded = json.dumps(case).encode()
        results = []
        for model in (native, helper):
            population = load_population_bytes(encoded, source="sample.json", model=model)
            assert set(population.covers) == set(facts)
            verdict, = [row for row in check(model, population).verdicts if row.constraint_type == "guarded"]
            assert verdict.binding_count == 3
            results.append((verdict.verdict, {(row["$e"], row["$a"]) for row in verdict.offending_facts}))
            if model is native:
                snapshot = adapt_snapshot(model, population)
                state, reason, witness = verdict_of(snapshot.constraints[0], snapshot)
                assert reason is None
                assert (state, {tuple(cell.num for cell in row) for row in witness}) == results[-1]
        assert results[0] == results[1]
        observed.add(results[0][0])
    assert observed == {"pass", "fail"}


def test_unsupported_exports_refuse_disjunction_by_name(tmp_path):
    from gnd.export.lean import render_lean
    from gnd.export.pyrel_rules import ExportInputError, render
    from gnd.export.souffle import render_souffle

    model, population = (Path(path) for path in _case(tmp_path, [LOW, HIGH], 1500))
    with pytest.raises(ExportInputError, match="^guarded-disjunction-unsupported$"):
        render(model, "duckdb")
    assert render_souffle(
        model.read_bytes(), population.read_bytes(), model_format="json",
    ).reason == "guarded-disjunction-unsupported"
    assert render_lean(
        model.read_bytes(), population.read_bytes(), toolchain="leanprover/lean4:v4.19.0",
    ).reason == "guarded-disjunction-unsupported"


def test_alternatives_cover_different_bindings_in_one_rule(tmp_path):
    paths = _case(tmp_path, [LOW, {"atom": _status("review")}], 500)
    population = _read(paths[1])
    population["population"]["covers"].append("expense_has_status")
    population["facts"]["expense_in_category"].append({"expense": 2, "category": "travel"})
    population["facts"]["expense_has_amount"].append({"expense": 2, "amount": 1500})
    population["facts"]["expense_has_status"] = [{"expense": 2, "status": "review"}]
    _write(paths[1], population)
    _, verdict = _check_and_reference(paths)
    assert verdict["verdict"] == "pass"
    assert verdict["guarded_antecedent"]["binding_count"] == 2


def test_indexed_disjunction_handles_wide_consequent_with_shared_budget(tmp_path):
    from time import perf_counter

    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population

    paths = _case(tmp_path, [LOW, {"atom": _status("review")}], 1500)
    population = _read(paths[1])
    population["population"]["covers"].append("expense_has_status")
    count = 6000
    population["facts"]["expense_in_category"] = [
        {"expense": expense, "category": "travel"} for expense in range(count)
    ]
    population["facts"]["expense_has_amount"] = [
        {"expense": expense, "amount": 1500} for expense in range(count)
    ]
    population["facts"]["expense_has_status"] = [
        {"expense": expense, "status": "review"} for expense in range(count)
    ]
    _write(paths[1], population)
    model = load_model(paths[0])
    admitted = load_population(paths[1], model=model)
    start = perf_counter()
    verdict, = check(model, admitted).verdicts
    assert verdict.binding_count == count and verdict.verdict == "pass"
    assert perf_counter() - start < 5


def test_temporal_comparison_alternative_uses_calendar_arithmetic(tmp_path):
    temporal = {"comparison": {
        "operator": "=",
        "left": {"fn": "date_add", "args": ["$a", {"duration_days": 1}]},
        "right": {"date": "2024-02-29"},
    }}
    paths = _case(tmp_path, [temporal, {"atom": _status("review")}], "2024-02-28")
    document = _read(paths[0])
    document["version"] = 3
    next(item for item in document["object_types"] if item["id"] == "amount")["primitive"] = "Date"
    _write(paths[0], document)
    result = run_main(["check", *paths, "--format", "json"])
    assert result.returncode == 0, result.stdout
    assert json.loads(result.stdout)["verdicts"][0]["verdict"] == "pass"
