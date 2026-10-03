

from __future__ import annotations

from copy import deepcopy

import pytest
from support.v62_phase2_corpus import population as phase2_population
from support.v62_phase2_corpus import write_model as write_phase2_model
from support.v62_phase2_corpus import write_steps as write_phase2_steps
from support.v62_phase3_corpus import FIXTURE

from gnd import checker as checker_module
from gnd import transition as transition_module
from gnd.api import transition
from gnd.checker import RelationUnavailable, structured_extension_view
from gnd.model import Model, load_model
from gnd.population import load_population
from gnd.transition import (
    _unavailable_dynamic_rule_verdicts,
    band,
    evaluate,
    evaluate_plan,
    read_steps_document,
    validate_steps,
)


def _validated(population_name: str):
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations" / population_name, model=model)
    return model, population


def test_t01_t05_static_exact_precondition_and_asserted_only_plan_state() -> None:
    model, population = _validated("term-clean.pop.yaml")
    document = read_steps_document(FIXTURE / "walks/approve.steps.json")
    document["steps"] = document["steps"][:1]

    result = evaluate_plan(model, population, validate_steps(document, model))

    assert result.report.steps[0].verdicts == []
    assert result.computed_post["facts"]["ticket_status"] == [
        {"status": "approved", "ticket": "negative"}
    ]
    assert not {"residue", "doubled_residue", "permitted"}.intersection(
        result.computed_post["facts"]
    )


def test_t02_t03_exact_dynamic_refresh_precedes_consumers_and_stale_mutation_reds(
    tmp_path, monkeypatch
) -> None:
    def add_exact_head(document):
        ticket_score = next(row for row in document["fact_types"] if row["id"] == "ticket_score")
        ticket_score["derivation_rule"]["head"]["score"] = {
            "fn": "add",
            "args": ["$score", 0],
        }

    model_path = write_phase2_model(tmp_path, add_exact_head)
    model = load_model(model_path)
    focused = write_phase2_steps(
        tmp_path,
        model,
        [
            {
                "op": "raise_score",
                "bindings": {"ticket": "SECRET-TICKET-314159", "new_score": 2},
            }
        ],
    )
    baseline = transition(
        model_path,
        phase2_population("pre_open"),
        focused,
        post=None,
        unredacted=True,
    )
    original = transition_module.structured_extension_view

    def stale(model_arg, population_arg, **kwargs):
        if kwargs.get("refresh") is not None:
            return checker_module.StructuredExtensionView(
                facts=kwargs.get("previous") or {},
                recomputed=(),
                work=checker_module.DynamicRefreshWork(),
                unavailable=kwargs.get("previous_unavailable") or {},
                possible=kwargs.get("previous_possible") or {},
            )
        return original(model_arg, population_arg, **kwargs)

    monkeypatch.setattr(transition_module, "structured_extension_view", stale)
    mutant = transition(
        model_path,
        phase2_population("pre_open"),
        focused,
        post=None,
        unredacted=True,
    )

    baseline_step = baseline["transition"]["steps"][0]
    mutant_step = mutant["transition"]["steps"][0]
    assert baseline_step["derived_changes"] == [
        {
            "added": [{"score": 2, "ticket": "SECRET-TICKET-314159"}],
            "fact_type": "ticket_score",
            "removed": [{"score": 1, "ticket": "SECRET-TICKET-314159"}],
        }
    ]
    assert "derived_changes" not in mutant_step


def test_w02_unavailable_precondition_and_intermediate_are_band_four() -> None:
    model = load_model(FIXTURE / "models/exact-terms.orm.yaml")
    population = load_population(FIXTURE / "populations/term-input.pop.yaml", model=model)
    document = read_steps_document(FIXTURE / "walks/approve.steps.json")
    result = evaluate_plan(model, population, validate_steps(document, model))
    assert band(result.report) == 4
    assert [
        verdict.reason_code
        for step in result.report.steps
        for verdict in step.verdicts
        if verdict.kind == "precondition"
    ] == ["term:mod-zero", "term:mod-zero"]
    assert all(
        verdict.verdict == "unchecked"
        for step in result.report.steps
        for verdict in step.intermediate.verdicts
    )
    assert all(not step.derived_changes for step in result.report.steps)


def test_u05_dynamic_rule_reads_unavailability_as_unchecked() -> None:
    model, _population = _validated("term-input.pop.yaml")
    operation = {
        "id": "adjust",
        "effects": [{"assert": {"fact_type": "input", "bind": {}}}],
        "dynamic_rules": [
            {
                "id": "residue_increases",
                "modality": "alethic",
                "subject": {"fact_type": "residue", "value_role": "residue"},
            }
        ],
    }
    verdicts = _unavailable_dynamic_rule_verdicts(
        1,
        operation,
        model,
        {"residue": RelationUnavailable("residue", "term:mod-zero", {"value": 7, "divisor": 0})},
    )
    assert [(row.verdict, row.reason_code) for row in verdicts] == [("unchecked", "term:mod-zero")]


def test_u05_unavailable_dynamic_rule_is_emitted_by_the_public_walk_path() -> None:
    original, _population = _validated("term-input.pop.yaml")
    document = deepcopy(original.model_dump(exclude={"warnings"}))
    operation = document["operations"][0]
    operation["effects"].insert(
        0,
        {"retract": {"fact_type": "input", "bind": {"ticket": "$ticket"}}},
    )
    operation["dynamic_rules"] = [
        {
            "id": "residue_never_decreases",
            "subject": {
                "fact_type": "residue",
                "value_role": "residue",
                "bind": {"ticket": "$ticket"},
            },
            "op": ">=",
            "modality": "alethic",
            "source": "user-supplied",
            "status": "confirmed",
            "provenance": {"user_quote": "Residue never decreases."},
        }
    ]
    model = Model.model_validate(document)
    population = load_population(FIXTURE / "populations/term-input.pop.yaml", model=model)
    steps = validate_steps(read_steps_document(FIXTURE / "walks/approve.steps.json"), model)

    result = evaluate_plan(model, population, steps)
    assert [
        (verdict.verdict, verdict.reason_code)
        for step in result.report.steps
        for verdict in step.verdicts
        if verdict.kind == "dynamic-rule"
    ] == [("unchecked", "term:mod-zero")]


def test_u07_declared_final_post_retains_unavailable_derivation_findings() -> None:
    model, population = _validated("term-input.pop.yaml")
    steps = validate_steps(read_steps_document(FIXTURE / "walks/approve.steps.json"), model)

    report = evaluate(model, population, population, steps)

    assert report.post_snapshot is not None
    assert {(row.verdict, row.reason_code) for row in report.post_snapshot.derivations} == {
        ("unchecked", "term:mod-zero")
    }


def test_unavailable_dynamic_rule_stays_silent_when_its_dependencies_are_untouched() -> None:
    model, _population = _validated("term-input.pop.yaml")
    operation = {
        "id": "annotate",
        "effects": [{"assert": {"fact_type": "ticket_status", "bind": {}}}],
        "dynamic_rules": [
            {
                "id": "residue_increases",
                "modality": "alethic",
                "subject": {"fact_type": "residue", "value_role": "residue"},
            }
        ],
    }

    assert (
        _unavailable_dynamic_rule_verdicts(
            1,
            operation,
            model,
            {"residue": RelationUnavailable("residue", "term:mod-zero", {"divisor": 0})},
        )
        == []
    )


def test_t02_selective_refresh_evaluates_only_requested_exact_strata() -> None:
    model, population = _validated("term-clean.pop.yaml")
    baseline = structured_extension_view(model, population)

    untouched = structured_extension_view(model, population, previous=baseline.facts, refresh=())
    assert untouched.facts == baseline.facts
    assert untouched.work.strata_evaluated == 0

    refreshed = structured_extension_view(
        model,
        population,
        previous=baseline.facts,
        refresh=("residue", "doubled_residue"),
    )
    assert refreshed.recomputed == ("residue", "doubled_residue")
    assert refreshed.work.selected_heads == 2
    assert refreshed.work.strata_evaluated == 2
    assert refreshed.facts == baseline.facts


def test_t02_selective_refresh_preserves_prior_unavailability() -> None:
    model, population = _validated("term-input.pop.yaml")
    baseline = structured_extension_view(model, population)

    refreshed = structured_extension_view(
        model,
        population,
        previous=baseline.facts,
        previous_unavailable=baseline.unavailable,
        refresh=("doubled_residue",),
    )

    assert refreshed.facts == baseline.facts
    assert refreshed.unavailable == baseline.unavailable
    assert refreshed.unavailable["doubled_residue"] == RelationUnavailable(
        "doubled_residue",
        "term:mod-zero",
        baseline.unavailable["residue"].binding,
        "residue",
    )


def test_selective_refresh_refuses_an_incomplete_prior_envelope() -> None:
    model, population = _validated("term-input.pop.yaml")
    baseline = structured_extension_view(model, population)

    with pytest.raises(ValueError, match="requires previous_unavailable"):
        structured_extension_view(
            model,
            population,
            previous=baseline.facts,
            refresh=("doubled_residue",),
        )

    with pytest.raises(ValueError, match="incomplete prior envelope"):
        structured_extension_view(
            model,
            population,
            previous=baseline.facts,
            previous_unavailable={},
            refresh=("doubled_residue",),
        )

    with pytest.raises(ValueError, match="requires previous_unavailable"):
        structured_extension_view(
            model,
            population,
            previous=baseline.facts,
            refresh=(),
        )
