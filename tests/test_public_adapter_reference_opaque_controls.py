import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tests"))
from gnd import semantic_adapter as adapter
from gnd.model import load_model
from gnd.population import load_population


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


def test_opaque_rules_and_object_derivation_kind_are_retained(tmp_path):
    import test_subtype_universe as universe

    directory = ROOT / "tests/fixtures/derivation-evaluation/cases/obligation-opaque-mixed-listed"
    model = load_model(directory / "model.orm.yaml")
    population = load_population(directory / "population.yaml", model=model)
    result = adapter.adapt_snapshot(model, population)
    legacy = next(row for row in result.fact_types if row.id == "legacy_result")
    assert legacy.opaque_rule == "A human-owned legacy rule."
    assert legacy.derivation == "derived" and not legacy.structured_rule
    assert legacy.relation_source == "claimed"
    objects = [dict(row) for row in universe.VEHICLE_TYPES]
    car = next(row for row in objects if row["id"] == "car")
    car.update(derivation="semiderived", derivation_rule="Cars listed by an external registry.")
    model = universe._model(tmp_path, objects, universe.VEHICLE_FACTS)
    population = universe._population(tmp_path, model, instances={"car": ["C1"]})
    result = adapter.adapt_snapshot(model, population)
    car = next(row for row in result.object_types if row.id == "car")
    assert (
        car.derivation == "semiderived"
        and car.opaque_rule == "Cars listed by an external registry."
    )
