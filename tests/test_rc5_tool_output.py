"""RC5 (rule-check-adoption): population source tool-output and its producer.

The corpus under tests/fixtures/rc5-tool-output is the phase's approval
instrument; its README tells each case and expected/answers.json holds the
answers.
"""

from __future__ import annotations

import json

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT

CORPUS = REPO_ROOT / "tests" / "fixtures" / "rc5-tool-output"
ANSWERS = json.loads((CORPUS / "expected" / "answers.json").read_text())


def _check(case: str):
    return run_main(
        ["check", "models/catalog.orm.yaml", f"populations/{case}.pop.yaml", "--format", "json"], cwd=CORPUS
    )


@pytest.mark.parametrize("case", sorted(ANSWERS))
def test_case_matches_answer_key(case: str) -> None:
    result = _check(case)
    payload = json.loads(result.stdout)
    assert result.returncode == ANSWERS[case]["exit"]
    assert [[issue["rule_id"], issue["path"]] for issue in payload["issues"]] == ANSWERS[case]["issues"]
    if ANSWERS[case]["exit"] == 0:
        control = json.loads(_check("fixture-control").stdout)
        control["population"] = payload["population"]
        assert payload == control


@pytest.mark.parametrize("case", sorted(case for case, answer in ANSWERS.items() if answer["exit"] == 0))
def test_the_loaded_population_keeps_its_label(case: str) -> None:
    from gnd.model import load_model
    from gnd.population import load_population

    model = load_model(CORPUS / "models" / "catalog.orm.yaml")
    population = load_population(CORPUS / "populations" / f"{case}.pop.yaml", model=model)
    assert population.source == "tool-output"
    if "producer" in ANSWERS[case]:
        assert population.producer == ANSWERS[case]["producer"]
    if "producer_length" in ANSWERS[case]:
        assert len(population.producer) == ANSWERS[case]["producer_length"]


# --- Direct tests (spec §8) -----------------------------------------------------------


def _schema_sources() -> list[str]:
    schema = json.loads((REPO_ROOT / "src" / "gnd" / "schema" / "population.schema.json").read_text())
    return schema["properties"]["population"]["properties"]["source"]["enum"]


def test_t2_the_schema_is_the_one_spelling_of_the_source_enum() -> None:
    from typing import get_args

    from gnd.extract.projection import project
    from gnd.model import load_model
    from gnd.population import Population

    assert list(get_args(Population.model_fields["source"].annotation)) == _schema_sources()
    projected = project(load_model(CORPUS / "models" / "catalog.orm.yaml"))
    extraction = projected["properties"]["population"]["properties"]["source"]["enum"]
    # The extraction projection is a pinned subset (spec D2): an agent's output is never tool output.
    assert set(extraction) <= set(_schema_sources())
    assert extraction == ["agent-output", "synthetic", "fixture"]


def test_t3_the_reference_binder_keeps_the_producer() -> None:
    from gnd.model import load_model
    from gnd.population import _combine_validated_populations, load_population

    model = load_model(CORPUS / "models" / "catalog.orm.yaml")
    population = load_population(CORPUS / "populations" / "tool-output-producer.pop.yaml", model=model)
    combined = _combine_validated_populations(
        model,
        (population,),
        {
            "format_version": 1,
            "population": {"model": population.model, "model_id": population.model_id,
                           "source": population.source, "producer": population.producer,
                           "covers": population.covers},
            "facts": population.facts,
            "instances": population.instances,
        },
    )
    assert combined.producer == population.producer


def test_t4_a_producer_needs_tool_output_even_when_built_directly() -> None:
    import pydantic

    from gnd.population import Population

    with pytest.raises(pydantic.ValidationError, match="only with source tool-output"):
        Population(model="m", source="fixture", producer="x")
    with pytest.raises(pydantic.ValidationError, match="1 to 200"):
        Population(model="m", source="tool-output", producer="x" * 201)
    assert Population(model="m", source="tool-output", producer="x" * 200).producer == "x" * 200


def test_t5_a_population_without_producer_keeps_its_digest() -> None:
    from gnd.population import Population
    from gnd.values import _content_digest

    population = Population(model="m", source="fixture", covers=["uses"])
    payload = population.model_dump(exclude={"warnings", "producer"})
    import hashlib

    assert _content_digest(population) == hashlib.sha256(repr(payload).encode()).hexdigest()


@pytest.mark.parametrize(("header", "valid"), [
    ({}, True), ({"producer": "x"}, True), ({"producer": "x" * 200}, True), ({"producer": "\U0001f60a" * 200}, True),
    ({"producer": ""}, False), ({"producer": "x" * 201}, False), ({"producer": "\U0001f60a" * 201}, False),
    ({"source": "fixture", "producer": "x"}, False), ({"source": "fixture"}, True),
])
def test_t6_the_loader_fast_path_agrees_with_draft_on_the_producer(header, valid) -> None:
    """The positive-only fast path accepts only what Draft 2020-12 accepts, and every valid header."""
    from jsonschema import Draft202012Validator

    from gnd import population
    from gnd.population_shape import accepts_shape

    schema = population._prepared_population_schema(population._load_population_schema())
    doc = {"population": {"model": "m", "source": "tool-output", "covers": [], **header}, "facts": {}}
    draft = not list(Draft202012Validator(schema).iter_errors(doc))
    assert draft is valid
    assert accepts_shape(doc, schema) is valid
