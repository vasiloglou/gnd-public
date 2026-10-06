"""Typed siblings and guarded variable primitive preservation."""
import json

import pytest
from support import public_adapter_cases as corpus

from gnd import checker
from gnd import semantic_adapter as adapter
from gnd.model import load_model
from gnd.population import load_population


@pytest.mark.parametrize(
    "primitive,right,verdict", (("String", "z", "pass"), ("Number", 2, "unchecked"))
)
def test_inline_untyped_role_preserves_the_typed_sibling_fallback(
    tmp_path, primitive, right, verdict
):
    document, data = corpus._documents("P2-161")
    document["constraints"] = []
    fact = document["fact_types"][0]
    document["object_types"].append(
        {"id": "compared", "name": "Compared", "kind": "value", "primitive": primitive}
    )
    fact["roles"][2]["object_type"] = "compared"
    fact["reading"] = "in {Mode}, {Opaque} is compared with {Compared}"
    fact["constraints"] = [
        {
            "type": "value-comparison",
            "operator": "<",
            "role_a": "left",
            "role_b": "right",
            "modality": "alethic",
            "source": "explicit",
            "status": "confirmed",
            "provenance": {"user_quote": "Left precedes right."},
        }
    ]
    data["facts"]["observed_pair"][0].update(left="a", right=right)
    model_path, population_path = tmp_path / "model.orm.yaml", tmp_path / "population.json"
    model_path.write_text(json.dumps(document))
    population_path.write_text(json.dumps(data))
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    observed = checker.check(model, population).verdicts[0]
    assert observed.verdict == verdict
    if primitive == "String":
        correspondence = adapter.adapt_snapshot_observed(model, population)
        assert any(
            row.reason == "untyped-string-ordering"
            for row in correspondence.observation.refusals
        )
    if verdict == "unchecked":
        assert observed.reason_code == "values-not-comparable"
    constraint = adapter.adapt_snapshot(model, population).constraints[0]
    assert tuple(operand.primitive for operand in constraint.operands) == ("", primitive)
    assert constraint.refused == ""


def test_guarded_variables_retain_their_own_primitives(tmp_path):
    document, data = corpus._documents("P2-161")
    document["constraints"] = [document["constraints"][0]]
    document["object_types"].append(
        {"id": "stamp", "name": "Stamp", "kind": "value", "primitive": "DateTime"}
    )
    fact = document["fact_types"][0]
    fact["roles"][2]["object_type"] = "stamp"
    fact["reading"] = "in {Mode}, {Opaque} is compared with {Stamp}"
    data["facts"]["observed_pair"][0].update(
        left="2026-09-07T07:00:00-05:00",
        right="2026-09-07T12:00:00Z",
    )
    model_path, population_path = tmp_path / "model.orm.yaml", tmp_path / "population.json"
    model_path.write_text(json.dumps(document))
    population_path.write_text(json.dumps(data))
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    assert checker.check(model, population).verdicts[0].verdict == "pass"
    constraint = adapter.adapt_snapshot(model, population).constraints[0]
    assert tuple(term.primitive for term in constraint.operands) == ("", "DateTime")
    assert constraint.refused == "untyped-string-ordering"


