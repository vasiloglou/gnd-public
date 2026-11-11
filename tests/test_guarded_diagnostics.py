"""Public controls for GW0 guarded-rule diagnostics."""
import json

import pytest
from jsonschema import Draft202012Validator
from ruamel.yaml import YAML

from gnd.report import load_report_schema
from support.cli_runner import run_main
from support.repository import REPO_ROOT

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
