"""Exact original mutation-control bodies over reviewed public inputs."""
import json
from itertools import pairwise
from pathlib import Path

from support import public_adapter_cases as corpus

from gnd import correspondence
from gnd import semantic_adapter as adapter
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[2]

def test_scalar_identity_and_order_are_separate():
    integer = adapter.canonical_scalar(1, "Integer")
    floating = adapter.canonical_scalar(1.0, "Float")
    boolean = adapter.canonical_scalar(True, "Boolean")
    string = adapter.canonical_scalar("1", "String")
    assert integer == floating
    assert len({(value.identity_kind, value.token) for value in (integer, boolean, string)}) == 3
    decimal = adapter.canonical_scalar(0.1, "Number")
    assert (decimal.num, decimal.den) == (3602879701896397, 36028797018963968)
    left = adapter.canonical_scalar("2026-09-07T07:00:00-05:00", "DateTime")
    right = adapter.canonical_scalar("2026-09-07T12:00:00Z", "DateTime")
    assert left.kind == right.kind == "datetime-aware"
    assert left.num == right.num and left.den == right.den == 1
    assert left.token != right.token
    assert left.identity_kind == right.identity_kind == "string"
    date = adapter.canonical_scalar("2026-09-07", "Date")
    assert date.identity_kind == "string" and date.token == "2026-09-07"
    assert adapter.canonical_scalar("2026-09-07T12:00:00", "DateTime").kind == "datetime-naive"

def test_numeric_order_uses_value_not_text():
    two = adapter.canonical_scalar(2, "Integer")
    ten = adapter.canonical_scalar(10, "Integer")
    assert two.num * ten.den < ten.num * two.den

def test_role_order_multiplicity_covers_and_explicit_instances(tmp_path):
    import test_subtype_universe as universe

    model = universe._model(tmp_path, universe.VEHICLE_TYPES, universe.VEHICLE_FACTS)
    population = universe._population(
        tmp_path,
        model,
        covers=["car_has_colour"],
        facts={"car_has_colour": [{"car": "C1", "colour": "red"} for _ in range(2)]},
        instances={"vehicle": ["V1", "V1"], "car": ["C2"]},
    )
    result = adapter.adapt_snapshot(model, population)
    assert result.covers == ("car_has_colour",)
    assert [(row.id, row.declared) for row in result.fact_types] == [
        ("car_has_colour", True),
        ("vehicle_has_plate", False),
    ]
    fact = result.fact_types[0]
    assert [(role.name, role.object_type, role.primitive) for role in fact.roles] == [
        ("car", "car", "String"),
        ("colour", "colour", "String"),
    ]
    assert [tuple(cell.token for cell in row) for row in result.relations[0].rows] == [
        ("C1", "red"),
        ("C1", "red"),
    ]
    assert [
        (row.object_type, tuple(value.token for value in row.members))
        for row in result.explicit_rosters
    ] == [("vehicle", ("V1", "V1")), ("car", ("C2",))]

def test_subtype_closure_retains_grandchildren(tmp_path):
    import test_subtype_universe as universe

    model = universe._model(
        tmp_path,
        [*universe.VEHICLE_TYPES, universe._subtype("electric", "Electric", ["car"])],
        universe.VEHICLE_FACTS,
    )
    population = universe._population(tmp_path, model, instances={"electric": ["E1"]})
    result = adapter.adapt_snapshot(model, population)
    types = {row.id: row for row in result.object_types}
    assert types["vehicle"].subtypes == ("car", "electric", "vehicle")
    assert types["car"].subtypes == ("car", "electric")
    assert types["electric"].primitive == "String"
    rosters = {row.object_type: row for row in result.rosters}
    assert tuple(value.token for value in rosters["vehicle"].members) == ("E1",)

def test_reference_universe_widens_only_from_values_to_entities():
    root = ROOT / "tests/fixtures/adversarial"
    model = load_model(root / "models/reference_value_type.orm.yaml")
    population = load_population(
        root / "populations/reference_value_type.out_of_range.yaml", model=model
    )
    snapshot = adapter.adapt_snapshot(model, population)
    types = {row.id: row for row in snapshot.object_types}
    rosters = {row.object_type: row for row in snapshot.rosters}
    assert types["movie_id"].denoting == ("movie",)
    assert types["movie"].denoting == ()
    assert types["movie"].primitive == "Integer"
    assert [scalar.num for scalar in rosters["movie_id"].members] == [999999, 999999]

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

def test_guard_consequents_and_variants_remain_distinct(tmp_path):
    root = ROOT / "tests/fixtures/guarded"
    model = load_model(root / "models/alethic.orm.yaml")
    population = load_population(root / "cases/a-a1.yaml", model=model)
    result = adapter.adapt_snapshot(model, population)
    assert [row.consequent_kind for row in result.constraints] == ["comparison", "atom", "absence"]
    assert result.constraints[0].operator == "<="
    assert result.constraints[1].consequent[0].fact_type == "expense_has_status"
    assert dict(result.constraints[1].consequent[0].bindings)["status"].literal.token == "review"
    assert dict(result.constraints[2].consequent[0].bindings)["status"].literal.token == "blocked"
    model, _ = corpus._build("P2-004", tmp_path)
    host = model.fact_types[0]
    for variant in ("acyclic", "irreflexive", "symmetric"):
        constraint = adapter.adapt_constraint(
            {
                "type": "ring",
                "modality": "alethic",
                "variant": variant,
                "roles": [role["role_name"] for role in host["roles"]],
            },
            host,
            "ring",
            model,
        )
        assert not constraint.refused
        assert constraint.variant == variant

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

def test_semiderived_claims_are_retained_without_computing_extensions(monkeypatch):
    root = ROOT / "tests/fixtures/derivation-evaluation/cases/obligation-semiderived-surplus"
    model = load_model(root / "model.orm.yaml")
    population = load_population(root / "population.yaml", model=model)

    def forbidden(*args, **kwargs):
        raise AssertionError("preserve rules and claims without calculating their meaning")

    monkeypatch.setattr(adapter.checker, "_python_extension_calculator", forbidden)
    result = adapter.adapt_snapshot(model, population)
    assert any(
        row.derivation == "semiderived" and row.relation_source == "computed-extension"
        for row in result.fact_types
    )
    for relation in result.relations:
        assert len(relation.rows) == len(population.facts.get(relation.fact_type, []))
    assert result.derivations and result.derivation_order

def test_dependency_graph_and_bare_dollar_literal_are_preserved(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("the adapter must not evaluate constraints or derive extensions")

    for name in ("check", "_python_extension_calculator", "_derivation_obligation"):
        monkeypatch.setattr(adapter.checker, name, forbidden)
    monkeypatch.setattr(correspondence, "evaluate_snapshot", forbidden)
    root = ROOT / "tests/fixtures/derivation-evaluation/cases"
    directory = root / "cost-chain-counted"
    model = load_model(directory / "model.orm.yaml")
    population = load_population(directory / "population.yaml", model=model)
    snapshot = adapter.adapt_snapshot(model, population)
    assert snapshot.derivation_order == ("low", "middle", "top")
    assert {row.fact_type: row.dependencies for row in snapshot.derivations} == {
        "low": ("seed",),
        "middle": ("low",),
        "top": ("middle",),
    }
    assert all(row.components == (("i",),) for row in snapshot.derivations)
    directory = root / "eval-bare-dollar-literal"
    model = load_model(directory / "model.orm.yaml")
    population = load_population(directory / "population.yaml", model=model)
    snapshot = adapter.adapt_snapshot(model, population)
    terms = dict(snapshot.derivations[0].body[0].bindings)
    assert terms["tag"].kind == "literal" and terms["tag"].raw_literal.token == "$"

def test_date_coordinates_preserve_calendar_order_and_leap_days():
    expected = (
        ("1900-02-28", 693654),
        ("1900-03-01", 693655),
        ("2000-02-28", 730178),
        ("2000-02-29", 730179),
        ("2000-03-01", 730180),
    )
    scalars = [adapter.canonical_scalar(value, "Date") for value, _ in expected]
    assert [(item.num, item.den, item.ordered) for item in scalars] == [
        (ordinal, 1, True) for _, ordinal in expected
    ]
    assert all(a.num * b.den < b.num * a.den for a, b in pairwise(scalars))

def test_structured_derived_relation_selection_preserves_coverage(tmp_path):
    from ruamel.yaml import YAML

    directory = (
        ROOT
        / "tests/fixtures/derivation-evaluation/cases/obligation-unlisted-derived-empty-computed"
    )
    model = load_model(directory / "model.orm.yaml")
    document = YAML(typ="safe").load((directory / "population.yaml").read_text())
    for covers, selected in ((["seed"], "empty"), (["seed", "result"], "claimed")):
        document["population"]["covers"] = covers
        population_path = tmp_path / "population.json"
        population_path.write_text(json.dumps(document))
        population = load_population(population_path, model=model)
        snapshot = adapter.adapt_snapshot(model, population)
        row = next(row for row in snapshot.fact_types if row.id == "result")
        assert row.structured_rule and row.derivation == "derived"
        assert row.relation_source == selected

def test_datetime_coordinates_retain_every_instant_component():
    expected = (
        ("2000-01-01T00:00:00Z", 63082281600000000),
        ("2024-02-29T12:34:56.123456Z", 63844806896123456),
        ("2024-02-29T12:34:56.123456+05:30", 63844787096123456),
        ("2024-02-29T12:34:56.123456-03:15:45.250000", 63844818641373456),
    )
    for spelling, microseconds in expected:
        value = adapter.canonical_scalar(spelling, "DateTime")
        assert (value.num, value.den) == (microseconds, 1)
        assert value.kind == "datetime-aware" and value.token == spelling
    naive = adapter.canonical_scalar("2024-02-29T12:34:56.123456", "DateTime")
    assert naive.kind == "datetime-naive" and naive.num == 63844806896123456
