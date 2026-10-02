






































from __future__ import annotations

from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

from gnd.checker import _denoting_types, _instance_values_of, _instances_of, check
from gnd.model import Model, load_model
from gnd.population import Population, load_population
from gnd.popvalidate import resolve_primitive, resolve_reference_value_type

_SOURCE = {"kind": "text-conversation", "confidence": "standard", "mode": "guided"}
_PROVENANCE = {"user_quote": "fixture"}


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


def _subtype(
    object_id: str, name: str, supertypes: list[str], *, inherits: bool = True
) -> dict[str, Any]:
    return {
        "id": object_id,
        "name": name,
        "kind": "entity",
        "subtype_of": supertypes,
        "inherits_reference": inherits,
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


def _constraint(**fields: Any) -> dict[str, Any]:
    return {
        "source": "explicit",
        "status": "confirmed",
        "modality": "alethic",
        "provenance": dict(_PROVENANCE),
        **fields,
    }


def _model(
    tmp_path: Path,
    object_types: list[dict[str, Any]],
    fact_types: list[dict[str, Any]],
    constraints: list[dict[str, Any]] | None = None,
) -> Model:
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
    header["facts"] = facts if facts is not None else {}
    if instances is not None:
        header["instances"] = instances
    return load_population(_write(tmp_path / "population.yaml", header), model=model)




MOVIE_TYPES = [
    _entity("movie", "Movie", "movie_id"),
    _value_type("movie_id", "MovieId", "Integer"),
    _value_type("title", "Title", "String"),
]

MOVIE_FACTS = [
    _binary(
        "movie_has_title",
        "{Movie} has title {Title}",
        [("movie", "movie"), ("title", "title")],
    )
]


def test_a_value_playing_an_entity_typed_role_is_an_instance_of_its_reference_value_type(
    tmp_path,
):





    model = _model(tmp_path, MOVIE_TYPES, MOVIE_FACTS)
    population = _population(
        tmp_path,
        model,
        covers=["movie_has_title"],
        facts={"movie_has_title": [{"movie": 999999, "title": "Alpha"}]},
    )
    universe = _instances_of("movie_id", model, population)
    assert 999999 in universe, (
        f"the value identifying a Movie is a MovieId — the loader type-checked "
        f"it as one — so it must be in MovieId's universe, got {sorted(universe)!r}"
    )


def test_an_entity_roster_entry_is_an_instance_of_its_reference_value_type(tmp_path):




    model = _model(tmp_path, MOVIE_TYPES, MOVIE_FACTS)
    population = _population(tmp_path, model, instances={"movie": [7]})
    universe = _instances_of("movie_id", model, population)
    assert 7 in universe, (
        f"an instances: roster entry for Movie is a MovieId, got {sorted(universe)!r}"
    )


def test_the_widening_does_not_run_in_the_entity_direction(tmp_path):








    model = _model(tmp_path, MOVIE_TYPES, MOVIE_FACTS)
    population = _population(
        tmp_path,
        model,
        covers=["movie_has_title"],
        facts={"movie_has_title": [{"movie": 3, "title": "Alpha"}]},
    )
    assert _instances_of("movie", model, population) == {3}
    assert _instances_of("title", model, population) == {"Alpha"}, (
        "an unrelated value type must not collect identifying values — only the "
        "value type an entity's reference scheme actually resolves to"
    )


def test_an_identifying_value_is_collected_once_per_occurrence(tmp_path):









    types = [*MOVIE_TYPES, _value_type("year", "Year", "Integer")]
    facts = [
        *MOVIE_FACTS,
        _binary(
            "movie_released_in",
            "{Movie} was released in {Year}",
            [("movie", "movie"), ("year", "year")],
        ),
    ]
    model = _model(tmp_path, types, facts)
    population = _population(
        tmp_path,
        model,
        covers=["movie_has_title", "movie_released_in"],
        facts={
            "movie_has_title": [
                {"movie": 1, "title": "Alpha"},
                {"movie": 2, "title": "Beta"},
            ],
            "movie_released_in": [{"movie": 1, "year": 1999}],
        },
    )
    values = _instance_values_of("movie_id", model, population)
    assert sorted(values) == [1, 1, 2], (
        f"three movie-typed role occurrences must yield three MovieId values, "
        f"got {sorted(values)!r}"
    )
    assert _instances_of("movie_id", model, population) == {1, 2}


def test_a_subtype_inheriting_its_reference_reaches_the_same_value_type(tmp_path):







    types = [*MOVIE_TYPES, _subtype("short_film", "ShortFilm", ["movie"])]
    facts = [
        *MOVIE_FACTS,
        _binary(
            "short_film_has_title",
            "{ShortFilm} has title {Title}",
            [("short_film", "short_film"), ("title", "title")],
        ),
    ]
    model = _model(tmp_path, types, facts)
    population = _population(
        tmp_path,
        model,
        covers=["short_film_has_title"],
        facts={"short_film_has_title": [{"short_film": 500, "title": "Gamma"}]},
    )
    assert resolve_reference_value_type("short_film", model) == "movie_id"
    assert 500 in _instances_of("movie_id", model, population)


def test_denoting_types_names_exactly_the_types_the_reference_scheme_resolves(tmp_path):


    types = [*MOVIE_TYPES, _subtype("short_film", "ShortFilm", ["movie"])]
    facts = [*MOVIE_FACTS]
    model = _model(tmp_path, types, facts)
    assert _denoting_types({"movie_id"}, model) == {"movie", "short_film"}
    assert _denoting_types({"title"}, model) == set()





def test_the_value_type_id_and_the_primitive_come_from_the_same_walk(tmp_path):

    model = _model(tmp_path, MOVIE_TYPES, MOVIE_FACTS)
    for object_type_id, expected_id, expected_primitive in [
        ("movie", "movie_id", "Integer"),
        ("movie_id", "movie_id", "Integer"),
        ("title", "title", "String"),
    ]:
        assert resolve_reference_value_type(object_type_id, model) == expected_id
        assert resolve_primitive(object_type_id, model) == expected_primitive


def test_multiple_inheritance_still_resolves_a_shared_primitive(tmp_path):










    types = [
        _entity("left", "Left", "left_id"),
        _value_type("left_id", "LeftId", "Integer"),
        _entity("right", "Right", "right_id"),
        _value_type("right_id", "RightId", "Integer"),
        _subtype("both", "Both", ["left", "right"]),
        _value_type("note", "Note", "String"),
    ]
    facts = [
        _binary("both_has_note", "{Both} has note {Note}", [("both", "both"), ("note", "note")])
    ]
    model = _model(tmp_path, types, facts)
    assert resolve_primitive("both", model) == "Integer"
    assert resolve_reference_value_type("both", model) is None, (
        "two distinct identifying value types cannot collapse to one id"
    )





@pytest.mark.parametrize(
    ("movie_value", "expected_verdict"),
    [(999999, "fail"), (42, "pass")],
    ids=["out-of-range-identifying-value-fails", "conforming-identifying-value-passes"],
)
def test_a_value_constraint_on_a_reference_value_type_is_actually_evaluated(
    tmp_path, movie_value, expected_verdict
):






    model = _model(
        tmp_path,
        MOVIE_TYPES,
        MOVIE_FACTS,
        [_constraint(type="value", object_type="movie_id", range={"min": 1, "max": 100})],
    )
    population = _population(
        tmp_path,
        model,
        covers=["movie_has_title"],
        facts={"movie_has_title": [{"movie": movie_value, "title": "Alpha"}]},
    )
    report = check(model, population)
    assert [v.verdict for v in report.verdicts] == [expected_verdict]
    assert ("— satisfied" in report.verdicts[0].message) == (expected_verdict == "pass")


def test_a_cardinality_constraint_on_a_reference_value_type_counts_what_is_there(tmp_path):


    model = _model(
        tmp_path,
        MOVIE_TYPES,
        MOVIE_FACTS,
        [
            _constraint(
                type="cardinality", scope="object", object_type="movie_id", bound={"max": 2}
            )
        ],
    )
    population = _population(
        tmp_path,
        model,
        covers=["movie_has_title"],
        facts={
            "movie_has_title": [
                {"movie": index, "title": f"Movie {index}"} for index in range(1, 5)
            ]
        },
    )
    report = check(model, population)
    assert [v.verdict for v in report.verdicts] == ["fail"]
    assert "4 observed" in report.verdicts[0].message, (
        f"the count must be the population's, not zero: {report.verdicts[0].message!r}"
    )
