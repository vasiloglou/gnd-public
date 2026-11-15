"""Profile boundaries for the guarded clause syntax."""
import json
from pathlib import Path

import pytest
from ruamel.yaml import YAML

BASE = Path(__file__).resolve().parent / "fixtures/models/guarded_minimal.orm.yaml"


def _model(tmp_path, shape):
    model = YAML(typ="safe").load(BASE)
    rule = model["constraints"][0]
    model["constraints"] = [rule]
    if shape == "membership":
        rule["consequent"]["comparison"].update(operator="in", right=[1500, 1600])
    elif shape == "filters":
        rule["negate"] = [{
            "fact_type": "expense_has_status",
            "bind": {"expense": "$e", "status": "exempt"},
        }]
        rule["where"] = [{"operator": ">=", "left": "$a", "right": 1000}]
    elif shape == "disjunction":
        rule["consequent"] = {"any_of": [
            rule["consequent"], {"comparison": {"operator": ">=", "left": "$a", "right": 2600}},
        ]}
    path = tmp_path / "model.orm.json"
    path.write_text(json.dumps(model))
    return path


@pytest.mark.parametrize("shape", ["membership", "filters"])
def test_readable_rules_translate_supported_guarded_clauses(tmp_path, shape):
    from gnd.export.pyrel_rules import render

    model = _model(tmp_path, shape)
    for target in ("duckdb", "lqp"):
        program = render(model, target)
        compile(program, "export.py", "exec")
        assert "policy_limit_travel" in program


@pytest.mark.parametrize(("shape", "reason"), [
    ("membership", "membership-unsupported"),
    ("filters", "guarded-antecedent-filters-unsupported"),
    ("disjunction", "guarded-disjunction-unsupported"),
])
def test_embedded_checker_refuses_unsupported_guarded_clauses(tmp_path, shape, reason):
    from gnd.export.emit import render_pyrel
    from gnd.export.pyrel_runtime import ExportInputError

    with pytest.raises(ExportInputError, match=reason):
        render_pyrel(_model(tmp_path, shape))


@pytest.mark.parametrize(("shape", "reason"), [
    ("membership", "membership-unsupported"),
    ("filters", "guarded-antecedent-filters-unsupported"),
    ("disjunction", "guarded-disjunction-unsupported"),
])
def test_ossie_identifies_rule_left_in_its_source_sidecar(tmp_path, shape, reason):
    from gnd.export.ossie import OssieInputError, render_ossie

    model = _model(tmp_path, shape)
    rendered = render_ossie(model, output_format="json")
    loss = json.loads(rendered.loss_report)
    assert any(row["pointer"] == "/constraints/0" and row["reason"] == reason for row in loss["dispositions"])
    with pytest.raises(OssieInputError, match=reason):
        render_ossie(model, output_format="json", strict=True)
