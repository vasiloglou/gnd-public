"""Admitted scalar, literal, range and immutable adapter controls."""
import dataclasses
import json
import math

import pytest
from support import public_adapter_cases as corpus

from gnd import semantic_adapter as adapter
from gnd import semantic_ir as ir
from gnd.model import load_model
from gnd.population import load_population


def test_admitted_yaml_numeric_literals_are_representable(tmp_path):
    model, population = corpus._build("P2-035", tmp_path)
    snapshot = adapter.adapt_snapshot(model, population)
    by_ref = {constraint.ref: constraint for constraint in snapshot.constraints}
    ranges = by_ref["constraints[2]"]
    assert ranges.refused == ""
    assert [(row[0].num, row[1].num) for row in ranges.ranges] == [(0, 10), (90, 100)]
    literal = by_ref["fact_types[item_has_score].constraints[1]"]
    assert literal.refused == ""
    assert literal.operands[1].literal.num == 0


def test_untyped_numeric_ordering_is_not_blanket_refused(tmp_path):
    model, _ = corpus._build("P2-161", tmp_path)
    _, document = corpus._documents("P2-161")
    for row in document["facts"]["observed_pair"]:
        row.update(left=1, right=2)
    path = tmp_path / "numbers.yaml"
    path.write_text(json.dumps(document))
    population = load_population(path, model=model)
    snapshot = adapter.adapt_snapshot(model, population)
    assert snapshot.constraints[0].refused == ""
    assert snapshot.constraints[0].operands[0].primitive == ""


def test_source_mutation_cannot_change_an_existing_ir(tmp_path):
    model, population = corpus._build("P2-004", tmp_path)
    snapshot = adapter.adapt_snapshot(model, population)
    before = hash(snapshot)
    population.facts.clear()
    model.fact_types[0]["roles"].reverse()
    assert hash(snapshot) == before
    with pytest.raises(dataclasses.FrozenInstanceError):
        snapshot.finite = False


def test_tagged_and_legacy_literals_keep_syntax_and_interpretation(tmp_path):
    model, _ = corpus._build("P2-004", tmp_path)
    host = next(row for row in model.fact_types if row["id"] == "item_has_score")
    seed = dict(host["constraints"][0])
    tagged = adapter.adapt_constraint({**seed, "role_b": {"literal": "10"}}, host, "tagged", model)
    legacy = adapter.adapt_constraint({**seed, "role_b": "10"}, host, "legacy", model)
    assert not tagged.refused and not legacy.refused
    assert tagged.operands[1].tagged and not tagged.operands[1].valid
    assert tagged.operands[1].raw_literal.token == "10"
    assert not legacy.operands[1].tagged and legacy.operands[1].valid
    assert legacy.operands[1].literal.num == 10 and legacy.operands[1].raw_literal.token == "10"


def test_untyped_guard_literal_is_preserved_as_uninterpretable(tmp_path):
    model, _ = corpus._build("P2-161", tmp_path)
    source = {
        **model.constraints[0],
        "consequent": {"comparison": {"operator": "=", "left": "$left", "right": 10}},
    }
    result = adapter.adapt_constraint(source, None, "constraint", model)
    assert result.refused == ""
    assert result.operands[1].raw_literal.num == 10
    assert not result.operands[1].valid


def test_bound_operator_modality_and_operand_order_survive(tmp_path):
    model, _ = corpus._build("P2-004", tmp_path)
    host = next(row for row in model.fact_types if row["id"] == "item_has_score")
    source = {
        **host["constraints"][0],
        "modality": "deontic",
        "operator": ">",
        "role_a": {"literal": 4},
        "role_b": {"role": "score"},
    }
    comparison = adapter.adapt_constraint(source, host, "comparison", model)
    assert not comparison.refused
    assert (comparison.modality, comparison.operator) == ("deontic", ">")
    assert [item.kind for item in comparison.operands] == ["literal", "role"]
    assert comparison.operands[0].literal.num == 4
    source = {
        **model.constraints[2],
        "ranges": [{"min": 1, "max": 10, "min_inclusive": False, "max_inclusive": True}],
    }
    ranged = adapter.adapt_constraint(source, None, "range", model)
    assert not ranged.refused
    assert ranged.ranges[0][2:] == (False, True)
    assert ranged.flags[2:] == (False, True)


def test_admitted_untyped_overflow_retains_cell_position_and_refuses(tmp_path, monkeypatch):
    model, _ = corpus._build("P2-161", tmp_path)
    _, document = corpus._documents("P2-161")
    document["facts"]["observed_pair"][0]["left"] = "OVERFLOW"
    path = tmp_path / "overflow.json"
    # Standard JSON exponent syntax overflows Python's float parser. D-05
    # leaves this role untyped; RF7 now refuses overflow at JSON admission.
    path.write_text(json.dumps(document).replace('"OVERFLOW"', "1e999"))
    from gnd.errors import PopulationLoadError
    with pytest.raises(PopulationLoadError):
        load_population(path, model=model)
    path.write_text(json.dumps(document).replace('"OVERFLOW"', '1'))
    population = load_population(path, model=model)
    population.facts["observed_pair"][0]["left"] = float('inf')
    assert math.isinf(population.facts["observed_pair"][0]["left"])
    # RF7 refuses serialized overflow. Isolate the adapter's in-memory defense;
    # the genuine validation marker correctly rejects this changed population.
    assert not population.matches_validation_marker(model)
    monkeypatch.setattr(type(population), 'matches_validation_marker', lambda *_: True)
    snapshot = adapter.adapt_snapshot(model, population)
    relation = next(row for row in snapshot.relations if row.fact_type == "observed_pair")
    assert len(relation.rows) == 1 and len(relation.rows[0]) == 3
    assert relation.rows[0][1] is None
    assert relation.refusals == (ir.IRRefusal("facts[observed_pair][0].left", "non-finite-number"),)
    assert snapshot.finite is False
    assert all(row.refused for row in snapshot.constraints)


def test_guard_literal_interpretation_failure_does_not_need_string_order(tmp_path):
    model_document, population_document = corpus._documents("P2-161")
    model_document["constraints"][0]["consequent"] = {
        "comparison": {"operator": ">", "left": "$left", "right": 10}
    }
    model_path, population_path = tmp_path / "model.orm.yaml", tmp_path / "population.yaml"
    model_path.write_text(json.dumps(model_document))
    population_path.write_text(json.dumps(population_document))
    model = load_model(model_path)
    population = load_population(population_path, model=model)
    result = adapter.adapt_snapshot(model, population).constraints[0]
    assert not result.operands[1].valid
    assert result.refused == ""


