"""Public controls for GW0 guarded-rule diagnostics."""
import json

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML
from support.cli_runner import run_main
from support.repository import REPO_ROOT

from gnd.report import load_report_schema

EXAMPLE = REPO_ROOT / "src/gnd/examples/rule_check"
ANSWERS = json.loads((REPO_ROOT / (
    ".gnd-planning/milestones/guarded-rule-workflows/corpus/GW0/expected.json"
)).read_text())
AREA = "component_is_in_area"
IMPORT = "component_imports_component"


def _atom(area):
    return {"fact_type": AREA, "bind": {"component": "$c", "area": area}}


def _write(tmp_path, cases, *, empty=None):
    yaml = YAML(typ="safe")
    model = yaml.load((EXAMPLE / "model.orm.yaml").read_text())
    population = yaml.load((EXAMPLE / "head.population.yaml").read_text())
    model["fact_types"][0].pop("constraints")
    shared = {"source": "user-supplied", "status": "confirmed", "modality": "alethic",
              "provenance": {"user_quote": "Catalog control."}}
    domain = dict(shared, id="area_domain", type="value", object_type="area", allowed=["core", "legacy"])
    model["constraints"] = [domain]
    antecedents = {
        "antecedent_typo": [_atom("legaccy")],
        "join_loss": [_atom("legacy"), {
            "fact_type": IMPORT, "bind": {"importer": "$i", "imported": "$c"},
        }],
    }
    for case in cases:
        model["constraints"].append(dict(
            shared, id=case, type="guarded", antecedent=antecedents.get(case, [_atom("legacy")]),
            consequent={"absence": _atom({
                "consequent_typo": "legaccy", "active_fail": "legacy",
            }.get(case, "core"))},
        ))
    if empty:
        population["facts"][AREA] = []
        if empty == "omitted":
            population["population"]["covers"].remove(AREA)
    for name, doc in (("model.orm.yaml", model), ("population.yaml", population)):
        (tmp_path / name).write_text(json.dumps(doc))


@pytest.mark.parametrize(("case", "empty", "exit_code"), [
    ("active_pass", None, 0), ("active_fail", None, 1), ("antecedent_typo", None, 0),
    ("join_loss", None, 0), ("consequent_typo", None, 0),
    ("covered_empty", "covered", 2), ("omitted_empty", "omitted", 2),
])
def test_diagnostics_corpus(tmp_path, case, empty, exit_code):
    _write(tmp_path, [case], empty=empty)
    result = run_main(
        ["check", "model.orm.yaml", "population.yaml", "--guarded-diagnostics", "--format", "json"],
        cwd=tmp_path,
    )
    assert result.returncode == exit_code
    report = json.loads(result.stdout)
    Draft202012Validator(load_report_schema()).validate(report)
    assert report["schema_version"] == 16
    row = next(row for row in report["verdicts"] if row["address"] == f"constraint:{case}")
    assert {"verdict": row["verdict"], **row["guarded_antecedent"]} == ANSWERS[case]
    assert all("guarded_antecedent" not in item for item in report["verdicts"] if item is not row)


def test_validation_diagnoses_both_typo_sites(tmp_path):
    _write(tmp_path, ["antecedent_typo", "consequent_typo"])
    result = run_main(["validate", "model.orm.yaml", "--format", "json"], cwd=tmp_path)
    expected = ANSWERS["validate_typos"]
    assert result.returncode == expected["exit"]
    findings = json.loads(result.stdout)["warnings"]
    assert [row["path"].removeprefix("$.") for row in findings if row["rule_id"] == expected["warning"]] == expected["paths"]


def test_populated_antecedent_without_coverage_keeps_exact_count(tmp_path):
    _write(tmp_path, ["active_fail", "join_loss"])
    path = tmp_path / "population.yaml"
    population = json.loads(path.read_text())
    del population["population"]["covers"]
    path.write_text(json.dumps(population))
    args = ["check", "model.orm.yaml", "population.yaml"]
    result = run_main([*args, "--guarded-diagnostics", "--format", "json"], cwd=tmp_path)
    legacy = run_main([*args, "--rule-ids", "--format", "json"], cwd=tmp_path)
    assert result.returncode == legacy.returncode == 1
    report = json.loads(result.stdout)
    assert [
        row.pop("guarded_antecedent")
        for row in report["verdicts"]
        if row["constraint_type"] == "guarded"
    ] == [{"binding_count": 1, "first_empty_atom_index": None},
          {"binding_count": 0, "first_empty_atom_index": 1}]
    report["schema_version"] = 15
    assert report == json.loads(legacy.stdout)
    text = run_main([*args, "--guarded-diagnostics"], cwd=tmp_path)
    assert b"GUARDED constraint:join_loss: bindings=0 (first empty antecedent atom 1)" in text.stdout


def test_guarded_diagnostics_and_baseline_share_ratchet(tmp_path):
    _write(tmp_path, ["active_fail"])
    args = ["check", "model.orm.yaml", "population.yaml", "--baseline", "population.yaml", "--format", "json"]
    new = run_main([*args, "--guarded-diagnostics"], cwd=tmp_path)
    old = run_main(args, cwd=tmp_path)
    assert new.returncode == old.returncode == 0
    report = json.loads(new.stdout)
    assert report["schema_version"] == 16
    assert report["baseline"] == json.loads(old.stdout)["baseline"]
    Draft202012Validator(load_report_schema()).validate(report)


def test_literal_domain_work_exhaustion_is_visible(tmp_path, monkeypatch):
    from gnd.model import _validation

    _write(tmp_path, ["antecedent_typo"])
    model = json.loads((tmp_path / "model.orm.yaml").read_text())
    monkeypatch.setattr(_validation, "_GUARDED_LITERAL_DOMAIN_WORK", 1)
    findings = _validation._rule_guarded_literal_domain(model)
    assert len(findings) == 1
    assert findings[0].rule_id == "semantic:guarded-literal-domain-work-limit"


def test_domain_walk_tolerates_non_atom_and_rejects_only_excluded_range_literals(tmp_path):
    from gnd.model import _validation

    _write(tmp_path, ["antecedent_typo", "active_pass"])
    model = json.loads((tmp_path / "model.orm.yaml").read_text())
    model["object_types"][2]["primitive"] = "Integer"
    domain, typo, allowed = model["constraints"]
    del domain["allowed"]
    domain["ranges"] = [{"min": 3, "max": 6, "min_inclusive": False}, {"min": 9}]
    typo["antecedent"] = [42, _atom(3)]
    typo["consequent"]["absence"] = _atom(9)
    allowed["antecedent"] = [_atom(5)]
    allowed["consequent"]["absence"] = _atom(4)
    findings = _validation._rule_guarded_literal_domain(model)
    assert [issue.path for issue in findings] == ["$.constraints[1].antecedent[1].bind[area]"]


def test_available_antecedent_with_unavailable_exists_consequent(tmp_path):
    _write(tmp_path, ["active_pass"])
    model_path = tmp_path / "model.orm.yaml"
    model = json.loads(model_path.read_text())
    owner_fact = "component_has_owner"
    model["constraints"][-1]["consequent"] = {"exists": {"atoms": [
        {"fact_type": owner_fact, "bind": {"component": "$c", "owner": "$o"}},
    ]}}
    model_path.write_text(json.dumps(model))
    population_path = tmp_path / "population.yaml"
    population = json.loads(population_path.read_text())
    population["population"]["covers"].remove(owner_fact)
    population_path.write_text(json.dumps(population))
    result = run_main(
        ["check", "model.orm.yaml", "population.yaml", "--guarded-diagnostics", "--format", "json"],
        cwd=tmp_path,
    )
    assert result.returncode == 4, result.stdout
    row = next(row for row in json.loads(result.stdout)["verdicts"] if row["constraint_type"] == "guarded")
    assert row["verdict"] == "unchecked"
    assert row["guarded_antecedent"] == {"binding_count": 1, "first_empty_atom_index": None}


def test_literal_domain_applies_only_to_declared_role(tmp_path):
    from gnd.model import _validation

    _write(tmp_path, ["antecedent_typo"])
    model = json.loads((tmp_path / "model.orm.yaml").read_text())
    domain, _ = model["constraints"]
    domain["role_ref"] = {"fact_type": "component_ships_in_release", "role": "release"}
    assert not _validation._rule_guarded_literal_domain(model)
    domain["role_ref"] = {"fact_type": AREA, "role": "area"}
    assert len(_validation._rule_guarded_literal_domain(model)) == 1
