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


def test_unknown_where_and_filter_only_empty_have_distinct_outcomes(tmp_path):
    paths = _case(
        tmp_path, negative=False,
        where=[{"operator": "=", "left": {"fn": "mod", "args": ["$a", 0]}, "right": 1}],
    )
    run = run_main(["check", *paths, "--format", "json"])
    report = json.loads(run.stdout)
    guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == "unchecked"
    assert guard["reason_code"] == "guarded-filter-term-unavailable"


def test_synthesis_excludes_a_binding_that_would_otherwise_fail(tmp_path):
    model, _ = _case(tmp_path)
    out = tmp_path / "generated"
    result = run_main(["synth", model, "--guarded-cases", "--out", str(out), "--seed", "19"])
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((out / "guarded-cases.json").read_bytes())
    rule, = manifest["rules"]
    assert rule["reason"] is None
    cases = {case["kind"]: case for case in rule["cases"]}
    assert {key: row["verdict"] for key, row in cases.items()} == {
        "failing": "fail", "passing": "pass",
    }
    assert cases["passing"]["binding_count"] > 0
    passing = out / cases["passing"]["population"]
    original = json.loads(Path(model).read_text())
    original["constraints"][0].pop("negate")
    Path(model).write_text(json.dumps(original), encoding="utf-8")
    run = run_main(["check", model, str(passing), "--format", "json"])
    report = json.loads(run.stdout)
    guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == "fail"


def test_ground_negated_atom_has_global_scope(tmp_path):
    model, pop = _case(tmp_path, statuses=[{"expense": 1, "status": "exempt"}])
    document = json.loads(Path(model).read_text())
    document["constraints"][0]["negate"][0]["bind"]["expense"] = 1
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    run = run_main(["check", model, pop, "--guarded-diagnostics", "--format", "json"])
    report = json.loads(run.stdout)
    guard, = [row for row in report["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == "vacuous"


def test_filters_verbalize_and_pyrel_refuses_them(tmp_path):
    from gnd.export.pyrel_rules import ExportInputError, render
    from gnd.model_verbalization import _guarded_cnl

    model, _ = _case(tmp_path, where=[{"operator": ">=", "left": "$a", "right": 100}])
    document = json.loads(Path(model).read_text())
    line = _guarded_cnl(document["constraints"][0])
    assert "$a is at least 100, unless " in line
    assert 'status = "exempt"' in line
    with pytest.raises(ExportInputError, match="^guarded-antecedent-filters-unsupported$"):
        render(Path(model), "duckdb")


@pytest.mark.parametrize(("covered", "claimed", "verdict"), [
    (True, True, "vacuous"),
    (True, False, "fail"),
    (False, False, "unchecked"),
])
def test_negation_reads_a_covered_derived_claim_separately_from_its_consistency(tmp_path, covered, claimed, verdict):
    statuses = [{"expense": 1, "status": "exempt"}] if claimed else []
    model, pop = _case(tmp_path, cover=covered, statuses=statuses)
    document = json.loads(Path(model).read_text())
    relation = next(fact for fact in document["fact_types"] if fact["id"] == "expense_has_status")
    relation["derivation"] = "derived"
    relation["derivation_rule"] = {
        "body": [{"fact_type": "expense_in_category", "bind": {"expense": "$e", "category": "travel"}}],
        "head": {"expense": "$e", "status": "exempt"},
    }
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population

    loaded = load_model(model)
    checked = check(loaded, load_population(pop, model=loaded))
    guard, = [row for row in checked.verdicts if row.constraint_type == "guarded"]
    assert guard.verdict == verdict
    derived, = [row for row in checked.derivations if row.fact_type == "expense_has_status"]
    assert derived.verdict == ("pass" if claimed else "fail" if covered else "unchecked")


def test_filtered_guard_matches_the_covered_helper_and_reference_over_seeded_cases(tmp_path):
    from random import Random

    from gnd.checker import check
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.semantic_adapter import adapt_snapshot
    from gnd.semantic_spec import verdict_of

    comparison = {"operator": ">=", "left": "$a", "right": 100}
    model_path, pop_path = _case(tmp_path, where=[comparison])
    native_doc = json.loads(Path(model_path).read_text())
    helper_doc = json.loads(Path(model_path).read_text())
    rule = helper_doc["constraints"][0]
    helper_doc["fact_types"].append({
        "id": "expense_to_review",
        "reading": "{Expense} has a screened amount {Amount}",
        "roles": [
            {"role_name": "expense", "object_type": "expense"},
            {"role_name": "amount", "object_type": "amount"},
        ],
        "derivation": "semiderived",
        "derivation_rule": {
            "body": rule["antecedent"], "negate": rule.pop("negate"),
            "where": rule.pop("where"), "head": {"expense": "$e", "amount": "$a"},
        },
    })
    rule["antecedent"] = [{"fact_type": "expense_to_review", "bind": {"expense": "$e", "amount": "$a"}}]
    model_files = [tmp_path / "native.orm.json", tmp_path / "helper.orm.json"]
    for path, document in zip(model_files, (native_doc, helper_doc), strict=True):
        path.write_text(json.dumps(document), encoding="utf-8")
    models = [load_model(path) for path in model_files]
    population = json.loads(Path(pop_path).read_text())
    rng = Random(195)
    verdicts = set()

    def checked(model, *, reference=False):
        loaded = load_population(pop_path, model=model)
        assert set(loaded.covers) >= {"expense_in_category", "expense_has_amount", "expense_has_status"}
        report = check(model, loaded)
        decision, = [row for row in report.verdicts if row.constraint_type == "guarded"]
        if reference:
            snapshot = adapt_snapshot(model, loaded)
            constraint, = snapshot.constraints
            assert verdict_of(constraint, snapshot)[0] == decision.verdict
        return decision.verdict, {row["$e"] for row in decision.offending_facts or []}

    for _ in range(200):
        facts = population["facts"]
        facts["expense_in_category"] = [{"expense": e, "category": "travel"} for e in range(1, 4)]
        facts["expense_has_amount"] = [
            {"expense": e, "amount": rng.choice([50, 500, 2500])} for e in range(1, 4)
        ]
        facts["expense_has_status"] = [
            {"expense": e, "status": "exempt"} for e in range(1, 4) if rng.randrange(2)
        ]
        Path(pop_path).write_text(json.dumps(population), encoding="utf-8")
        direct = checked(models[0], reference=True)
        assert direct == checked(models[1])
        verdicts.add(direct[0])
    assert verdicts == {"pass", "fail", "vacuous"}


def test_synthesis_uses_membership_in_antecedent_where(tmp_path):
    model, _ = _case(
        tmp_path, negative=False,
        where=[{"operator": "in", "left": "$a", "right": [1500, 2500]}],
    )
    out = tmp_path / "generated"
    result = run_main(["synth", model, "--guarded-cases", "--out", str(out), "--seed", "11"])
    assert result.returncode == 0, (result.stdout, result.stderr)
    manifest = json.loads((out / "guarded-cases.json").read_bytes())
    rule, = manifest["rules"]
    assert rule["reason"] is None
    assert {case["verdict"] for case in rule["cases"]} == {"pass", "fail"}


def test_negation_index_covers_wide_relation_and_refuses_excess_work(tmp_path, monkeypatch):
    from time import perf_counter

    from gnd import semantic_spec
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.semantic_adapter import adapt_snapshot

    model_path, pop_path = _case(tmp_path)
    model = load_model(model_path)
    population = json.loads(Path(pop_path).read_text())
    count = 10_000
    population["facts"] = {
        "expense_in_category": [{"expense": i, "category": "travel"} for i in range(count)],
        "expense_has_amount": [{"expense": i, "amount": 2500} for i in range(count)],
        "expense_has_status": [{"expense": i, "status": "exempt"} for i in range(1, count, 2)],
    }
    Path(pop_path).write_text(json.dumps(population), encoding="utf-8")
    snapshot = adapt_snapshot(model, load_population(pop_path, model=model))
    constraint, = snapshot.constraints
    from gnd.correspondence import _indexed_guarded_bindings

    valid, names, rows, _ = _indexed_guarded_bindings(constraint, snapshot)
    assert valid and len(rows) == count
    started = perf_counter()
    survivors, reason = semantic_spec.guarded_filtered_bindings(constraint, snapshot, names, rows)
    assert perf_counter() - started < 5.0
    assert reason is None and len(survivors) == count // 2
    monkeypatch.setattr(semantic_spec, "_GUARDED_FILTER_WORK_LIMIT", 100)
    assert semantic_spec.guarded_filtered_bindings(constraint, snapshot, names, rows) == (
        (), "guarded-filter-work-limit",
    )


def test_unavailable_semiderived_negation_does_not_use_a_raw_claim(tmp_path):
    model, pop = _case(tmp_path, statuses=[{"expense": 1, "status": "exempt"}])
    document = json.loads(Path(model).read_text())
    relation = next(fact for fact in document["fact_types"] if fact["id"] == "expense_has_status")
    relation["derivation"] = "semiderived"
    relation["derivation_rule"] = {
        "body": [{"fact_type": "expense_has_amount", "bind": {"expense": "$e", "amount": "$a"}}],
        "where": [{"operator": "=", "left": {"fn": "mod", "args": ["$a", 0]}, "right": 0}],
        "head": {"expense": "$e", "status": "exempt"},
    }
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    run = run_main(["check", model, pop, "--format", "json"])
    payload = json.loads(run.stdout)
    verdict, = [row for row in payload["verdicts"] if row["constraint_type"] == "guarded"]
    assert verdict["verdict"] == "unchecked"
    assert verdict["reason_code"] == "guarded-filter-coverage-missing"


def test_duration_literals_can_bind_negative_roles(tmp_path):
    model, pop = _case(tmp_path, statuses=[{"expense": 1, "status": 1}])
    document = json.loads(Path(model).read_text())
    document["version"] = 3
    status = next(item for item in document["object_types"] if item["id"] == "status")
    status["primitive"] = "Duration"
    document["constraints"][0]["negate"][0]["bind"]["status"] = 1
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    run = run_main(["check", model, pop, "--format", "json"])
    payload = json.loads(run.stdout)
    guard, = [row for row in payload["verdicts"] if row["constraint_type"] == "guarded"]
    assert guard["verdict"] == "vacuous"


def test_partial_negative_atom_refuses_before_applying_filters(tmp_path):
    model, _ = _case(tmp_path, where=[{"operator": "=", "left": "$a", "right": -1}])
    document = json.loads(Path(model).read_text())
    document["constraints"][0]["negate"][0]["bind"].pop("status")
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    run = run_main(["validate", model, "--format", "json"])
    assert run.returncode == 3
    assert b"semantic:guarded-role-claim" in run.stdout


def test_filter_and_consequent_can_both_use_temporal_terms(tmp_path):
    model, pop = _case(tmp_path, cover=True)
    document = json.loads(Path(model).read_text())
    document["version"] = 3
    next(item for item in document["object_types"] if item["id"] == "amount")["primitive"] = "Date"
    term = {"fn": "date_add", "args": ["$a", {"duration_days": 1}]}
    comparison = {"operator": "=", "left": term, "right": {"date": "2024-02-29"}}
    document["constraints"][0]["where"] = [comparison]
    document["constraints"][0]["consequent"] = {"comparison": comparison}
    population = json.loads(Path(pop).read_text())
    population["facts"]["expense_has_amount"][0]["amount"] = "2024-02-28"
    Path(model).write_text(json.dumps(document), encoding="utf-8")
    Path(pop).write_text(json.dumps(population), encoding="utf-8")
    run = run_main(["check", model, pop, "--format", "json"])
    assert run.returncode == 0, run.stdout
    guard = json.loads(run.stdout)["verdicts"][0]
    assert guard["verdict"] == "pass"
    assert "bindings=1" in guard["message"]


def test_exhausted_filter_does_not_publish_a_known_zero_count(tmp_path, monkeypatch):
    from gnd import semantic_spec

    monkeypatch.setattr(semantic_spec, "_GUARDED_FILTER_WORK_LIMIT", 1)
    paths = _case(tmp_path)
    run = run_main(["check", *paths, "--guarded-diagnostics", "--format", "json"])
    guard = json.loads(run.stdout)["verdicts"][0]
    assert guard["verdict"] == "unchecked"
    assert guard["reason_code"] == "guarded-filter-work-limit"
    assert guard["guarded_antecedent"] == {"binding_count": None, "first_empty_atom_index": None}


def test_where_membership_incompatible_list_has_one_validation_issue(tmp_path):
    paths = _case(tmp_path, where=[{"operator": "in", "left": "$a", "right": ["x", "x"]}])
    result = run_main(["validate", paths[0], "--format", "json"])
    assert result.returncode == 3
    issues = json.loads(result.stdout)["issues"]
    assert [
        item["path"] for item in issues if item["rule_id"] == "semantic:membership-list"
    ] == ["$.constraints[0].where[0].right"]
