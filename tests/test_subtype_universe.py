"""Subtype-closed object universes (CORE-06, D-13 clause 2).

In ORM 2 subtypehood IS population subsethood: ``pop(S) subset-of pop(A)``
whenever ``S subtype_of A``. So a value playing an S-typed role, or listed in
S's ``instances:`` roster, is an instance of every supertype of S — transitively
— and every constraint declared over a supertype must see it.

Before this, ``checker._instances_of`` matched ``role.object_type`` EXACTLY, and
``checker._check_value`` hand-rolled the same walk with the same exact-match
test. A car with no plate therefore satisfied an alethic ``mandatory(vehicle)``
constraint, affirmatively: *"Each vehicle must play the 'vehicle' role in
'vehicle_has_plate' — satisfied"* (01.1-CONTEXT.md probe #5). Fixing only
``_instances_of`` would have moved the hole one function over rather than
closing it, so both sites are asserted here.

The direction matters as much as the closure: a supertype value must NOT appear
in a subtype's universe. A test that only proves the union grew would pass just
as happily against a walk that merged the two populations in both directions,
which would manufacture false alethic failures instead of false passes.

Discipline, matching ``test_checker_families.py`` and ``test_vacuity.py``: every
population reaches the checker ONLY through ``gnd.population.load_population``
with ``model=``, so layer-2 structural validation (CORE-04) actually runs and
the D-02 marker is stamped. No YAML/JSON parsing of population documents happens
in this module — documents are written out and read back through the loaders,
which also makes every model here proof that it validates.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd.checker import _descendant_closure, _instance_values_of, _instances_of, check
from gnd.model import Model, load_model
from gnd.population import Population, load_population

_SOURCE = {"kind": "text-conversation", "confidence": "standard", "mode": "guided"}


def _write(path: Path, doc: dict[str, Any]) -> Path:
    with path.open("w", encoding="utf-8") as handle:
        YAML().dump(doc, handle)
    return path


def _entity(object_id: str, name: str, value_type: str) -> dict[str, Any]:
    return {
        "id": object_id,
        "name": name,
        "kind": "entity",
        "reference": {"mode": "popular", "value_type": value_type},
    }


def _value_type(object_id: str, name: str, primitive: str = "String") -> dict[str, Any]:
    return {"id": object_id, "name": name, "kind": "value", "primitive": primitive}


def _subtype(object_id: str, name: str, supertypes: list[str]) -> dict[str, Any]:
    return {
        "id": object_id,
        "name": name,
        "kind": "entity",
        "subtype_of": supertypes,
        "inherits_reference": True,
        "derivation": "asserted",
    }


def _binary(fact_type_id: str, reading: str, roles: list[tuple[str, str]]) -> dict[str, Any]:
    return {
        "id": fact_type_id,
        "reading": reading,
        "roles": [
            {"object_type": object_type, "role_name": role_name}
            for object_type, role_name in roles
        ],
    }


def _model(
    tmp_path: Path,
    object_types: list[dict[str, Any]],
    fact_types: list[dict[str, Any]],
    constraints: list[dict[str, Any]] | None = None,
) -> Model:
    """Write a model document and load it through the guarded loader.

    Loading rather than constructing ``Model(...)`` in memory means every model
    in this module is also an assertion that it validates: a subtype graph that
    ``gnd validate`` would reject cannot silently become the basis of a claim
    about checker behaviour.
    """
    doc: dict[str, Any] = {
        "version": 1,
        "source": dict(_SOURCE),
        "object_types": object_types,
        "fact_types": fact_types,
    }
    if constraints:
        doc["constraints"] = constraints
    return load_model(_write(tmp_path / "model.orm.yaml", doc))


def _population(
    tmp_path: Path,
    model: Model,
    *,
    covers: list[str] | None = None,
    facts: dict[str, list[dict[str, Any]]] | None = None,
    instances: dict[str, list[Any]] | None = None,
) -> Population:
    header: dict[str, Any] = {
        "population": {
            "model": "model.orm.yaml",
            "source": "fixture",
            "label": "conforming",
        }
    }
    if covers is not None:
        header["population"]["covers"] = covers
    #: `facts` is a REQUIRED key in population.schema.json — a roster-only
    #: population still declares it, empty.
    header["facts"] = facts if facts is not None else {}
    if instances is not None:
        header["instances"] = instances
    return load_population(
        _write(tmp_path / "population.yaml", header), model=model
    )


# --- the universe grows upward ---


VEHICLE_TYPES = [
    _entity("vehicle", "Vehicle", "vehicle_id"),
    _value_type("vehicle_id", "VehicleId"),
    _value_type("plate", "Plate"),
    _value_type("colour", "Colour"),
    _subtype("car", "Car", ["vehicle"]),
]

VEHICLE_FACTS = [
    _binary("car_has_colour", "{Car} has colour {Colour}", [("car", "car"), ("colour", "colour")]),
    _binary(
        "vehicle_has_plate",
        "{Vehicle} has plate {Plate}",
        [("vehicle", "vehicle"), ("plate", "plate")],
    ),
]


def test_a_value_playing_a_subtype_typed_role_is_an_instance_of_the_supertype(tmp_path):
    """The role route. Nothing in `car_has_colour` mentions `vehicle` at all,
    which is exactly why the exact-match walk never saw "C1"."""
    model = _model(tmp_path, VEHICLE_TYPES, VEHICLE_FACTS)
    population = _population(
        tmp_path,
        model,
        covers=["car_has_colour"],
        facts={"car_has_colour": [{"car": "C1", "colour": "red"}]},
    )
    universe = _instances_of("vehicle", model, population)
    assert "C1" in universe, (
        f"a value playing the car-typed role must be a vehicle instance "
        f"(pop(car) subset-of pop(vehicle)), got {sorted(universe)!r}"
    )


def test_a_subtype_roster_entry_is_an_instance_of_the_supertype(tmp_path):
    """The roster route. population-format.md names both routes, so closing only
    the role one would leave half the defect open."""
    model = _model(tmp_path, VEHICLE_TYPES, VEHICLE_FACTS)
    population = _population(tmp_path, model, instances={"car": ["C2"]})
    universe = _instances_of("vehicle", model, population)
    assert "C2" in universe, (
        f"an instances: roster entry for the subtype must be a supertype "
        f"instance, got {sorted(universe)!r}"
    )


def test_a_supertype_value_is_not_an_instance_of_the_subtype(tmp_path):
    """The direction guard, and the reason this is a closure and not a merge.

    Membership propagates UPWARD only: a vehicle is not thereby a car. A walk
    that unioned in both directions would satisfy every other test in this
    module while manufacturing false alethic FAILURES — the opposite defect,
    equally disqualifying.
    """
    model = _model(tmp_path, VEHICLE_TYPES, VEHICLE_FACTS)
    population = _population(
        tmp_path,
        model,
        covers=["car_has_colour", "vehicle_has_plate"],
        facts={
            "car_has_colour": [{"car": "C1", "colour": "red"}],
            "vehicle_has_plate": [{"vehicle": "V1", "plate": "AAA-111"}],
        },
    )
    vehicles = _instances_of("vehicle", model, population)
    cars = _instances_of("car", model, population)

    assert vehicles == {"C1", "V1"}, f"vehicle universe: {sorted(vehicles)!r}"
    assert cars == {"C1"}, (
        f"the car universe must NOT absorb the supertype's own instances; "
        f"got {sorted(cars)!r}"
    )


def test_subtype_closure_is_transitive_across_a_two_level_chain(tmp_path):
    """`racer subtype_of car subtype_of vehicle`: a racer is a vehicle."""
    model = _model(
        tmp_path,
        [*VEHICLE_TYPES, _subtype("racer", "Racer", ["car"])],
        [
            *VEHICLE_FACTS,
            _binary(
                "racer_has_colour",
                "{Racer} has colour {Colour}",
                [("racer", "racer"), ("colour", "colour")],
            ),
        ],
    )
    population = _population(
        tmp_path,
        model,
        covers=["racer_has_colour"],
        facts={"racer_has_colour": [{"racer": "R1", "colour": "green"}]},
    )

    assert _descendant_closure("vehicle", model) == {"vehicle", "car", "racer"}
    assert "R1" in _instances_of("vehicle", model, population), (
        "membership must propagate through the whole chain, not one level"
    )
    assert "R1" in _instances_of("car", model, population)
    assert _instances_of("racer", model, population) == {"R1"}


def test_multiple_inheritance_places_a_value_in_every_supertype_universe(tmp_path):
    """`subtype_of` is a list, so a type joins the closure when ANY declared
    supertype is in it — multiple inheritance needs no special case."""
    model = _model(
        tmp_path,
        [
            *VEHICLE_TYPES,
            _entity("boat", "Boat", "vehicle_id"),
            _subtype("amphibian", "Amphibian", ["vehicle", "boat"]),
        ],
        [
            *VEHICLE_FACTS,
            _binary(
                "amphibian_has_colour",
                "{Amphibian} has colour {Colour}",
                [("amphibian", "amphibian"), ("colour", "colour")],
            ),
        ],
    )
    population = _population(
        tmp_path,
        model,
        covers=["amphibian_has_colour"],
        facts={"amphibian_has_colour": [{"amphibian": "A1", "colour": "blue"}]},
    )

    assert "A1" in _instances_of("vehicle", model, population)
    assert "A1" in _instances_of("boat", model, population)
    assert _descendant_closure("boat", model) == {"boat", "amphibian"}


def test_a_subtype_cycle_terminates_rather_than_looping_without_bound(tmp_path):
    """T-01.1-07. Acyclicity CANNOT be assumed: no `semantic:` rule forbids a
    subtype cycle today, so `a subtype_of [b]` + `b subtype_of [a]` validates at
    exit 0 (verified in plan 01.1-03, logged in deferred-items.md). The fixpoint
    is what makes this terminate; without it the call never returns and the
    whole suite hangs rather than failing."""
    model = _model(
        tmp_path,
        [
            {
                "id": "a",
                "name": "A",
                "kind": "entity",
                "subtype_of": ["b"],
                "inherits_reference": True,
            },
            {
                "id": "b",
                "name": "B",
                "kind": "entity",
                "subtype_of": ["a"],
                "inherits_reference": True,
            },
            _value_type("tag", "Tag"),
        ],
        [_binary("a_has_tag", "{A} has tag {Tag}", [("a", "a"), ("tag", "tag")])],
    )

    assert _descendant_closure("a", model) == {"a", "b"}, (
        "each member of a cycle is reachable from the other, and the walk must "
        "say so exactly once"
    )

    population = _population(
        tmp_path,
        model,
        covers=["a_has_tag"],
        facts={"a_has_tag": [{"a": "X1", "tag": "t"}]},
    )
    assert _instances_of("b", model, population) == {"X1"}


# --- the parallel blind spot: _check_value ---


def test_a_value_constraint_on_a_supertype_catches_subtype_only_values(tmp_path):
    """RESEARCH Pitfall 8: `_check_value` hand-rolled the identical exact-match
    walk, so a `value` constraint declared on a SUPERTYPE was blind to subtype
    rosters and subtype-typed roles. Both offending values here are reachable
    only through the subtype — one by roster, one by role."""
    model = _model(
        tmp_path,
        VEHICLE_TYPES,
        VEHICLE_FACTS,
        constraints=[
            {
                "type": "value",
                "object_type": "vehicle",
                "allowed": ["V1"],
                "source": "explicit",
                "status": "confirmed",
                "modality": "alethic",
                "provenance": {"user_quote": "The only vehicle on file is V1."},
            }
        ],
    )
    population = _population(
        tmp_path,
        model,
        covers=["car_has_colour", "vehicle_has_plate"],
        facts={
            "car_has_colour": [{"car": "ROLE-BAD", "colour": "red"}],
            "vehicle_has_plate": [{"vehicle": "V1", "plate": "AAA-111"}],
        },
        instances={"car": ["ROSTER-BAD"]},
    )

    report = check(model, population)
    verdict = next(v for v in report.verdicts if v.constraint_ref == "constraints[0]")
    assert verdict.verdict == "fail", (
        f"a value constraint on the supertype must see subtype-only values, got "
        f"{verdict.verdict!r}: {verdict.message}"
    )
    assert "ROSTER-BAD" in verdict.message, verdict.message
    assert "ROLE-BAD" in verdict.message, verdict.message


def test_one_traversal_two_shapes_list_keeps_duplicates_set_does_not(tmp_path):
    """Why `_instance_values_of` returns a list and `_instances_of` wraps it in
    a set: `_check_value` reports one offending entry per OCCURRENCE, so
    swapping the set in directly would have deduped user-visible messages for a
    reason unrelated to this phase."""
    model = _model(tmp_path, VEHICLE_TYPES, VEHICLE_FACTS)
    population = _population(
        tmp_path,
        model,
        covers=["car_has_colour"],
        facts={
            "car_has_colour": [
                {"car": "C1", "colour": "red"},
                {"car": "C1", "colour": "blue"},
            ]
        },
    )
    values = _instance_values_of("vehicle", model, population)
    assert values == ["C1", "C1"], f"duplicates must survive the list shape: {values!r}"
    assert _instances_of("vehicle", model, population) == {"C1"}


@pytest.mark.parametrize("object_type_id", ["vehicle_id", "plate", "colour"])
def test_a_type_with_no_subtypes_closes_to_itself(tmp_path, object_type_id):
    """The no-op case, asserted so the closure cannot quietly widen a universe
    it has no business widening — research measured the blast radius at zero."""
    model = _model(tmp_path, VEHICLE_TYPES, VEHICLE_FACTS)
    assert _descendant_closure(object_type_id, model) == {object_type_id}
