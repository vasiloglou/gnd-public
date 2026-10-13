"""One transition's admitted PRE preparation preserves the complete walk."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd import api
from gnd import extension_preparation as preparation
from gnd import extensions as ext
from gnd import transition as walk
from gnd.branches import capture_branches
from gnd.correspondence import ReferenceJoinWork
from gnd.model import load_model
from gnd.population import load_population

FIXTURE = Path(__file__).parent / "fixtures/v70-phase4"


def inputs():
    model = load_model(FIXTURE / "recursive.orm.yaml")
    pre = load_population(FIXTURE / "recursive.pop.json", model=model)
    steps = json.loads((FIXTURE / "visit.steps.json").read_text())
    steps["model_digest"] = walk.model_digest(model)
    steps["operations_digest"] = walk.operations_digest(model.operations)
    assert ext._requires_fixpoint(model)
    return model, pre, steps


def body_counter(monkeypatch):
    calls = []
    original = ext._clause_bindings

    def counted(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(ext, "_clause_bindings", counted)
    return calls


def test_shared_pre_omits_body_and_preserves_full_public_report_trace_and_work(monkeypatch):
    model, pre, steps = inputs()
    calls = body_counter(monkeypatch)
    initial = []
    original = walk.structured_extension_view

    def observed(actual_model, population, **kwargs):
        before = len(calls)
        view = original(actual_model, population, **kwargs)
        if population is pre and not kwargs:
            initial.append((len(calls) - before, view))
        return view

    monkeypatch.setattr(walk, "structured_extension_view", observed)
    with monkeypatch.context() as disabled:
        disabled.setattr(preparation, "MAX_PREPARED_CALCULATIONS", 0)
        with capture_branches() as baseline_trace:
            baseline = api.transition(model, pre, steps)
    baseline_work, baseline_view = initial.pop()
    with capture_branches() as candidate_trace:
        candidate = api.transition(model, pre, steps)
    candidate_work, candidate_view = initial.pop()
    assert candidate == baseline
    assert candidate_trace == baseline_trace and candidate_trace
    assert candidate_view == baseline_view
    assert candidate["exit_code"] == 0
    assert candidate["transition"]["computed_post"]["facts"]["visited"] == [
        {"source": "A", "target": "C"}
    ]
    assert candidate["transition"]["steps"][0]["verdicts"] == []
    assert baseline_work > 0
    # Unlike a whole-call count comparison, this isolates the missing reuse:
    # phase11 already optimizes the checker's own internal requests.
    assert candidate_work == 0
    assert preparation.current_scope() is None


def test_owner_spans_public_dispatches_and_closes_before_step_and_refresh(monkeypatch):
    model, pre, steps = inputs()
    seen = []
    original_check = walk.check
    original_compiled = walk._compiled_verdicts_for_dynamic_walk
    original_view = walk.structured_extension_view
    original_step = walk._evaluate_step

    def checked(actual_model, population, **kwargs):
        if population is pre:
            seen.append(("check", preparation.current_scope()))
        return original_check(actual_model, population, **kwargs)

    def compiled(actual_model, population):
        seen.append(("standing", preparation.current_scope()))
        return original_compiled(actual_model, population)

    def viewed(actual_model, population, **kwargs):
        seen.append(("initial" if population is pre else "refresh", preparation.current_scope()))
        return original_view(actual_model, population, **kwargs)

    def stepped(*args, **kwargs):
        seen.append(("step", preparation.current_scope()))
        return original_step(*args, **kwargs)

    monkeypatch.setattr(walk, "check", checked)
    monkeypatch.setattr(walk, "_compiled_verdicts_for_dynamic_walk", compiled)
    monkeypatch.setattr(walk, "structured_extension_view", viewed)
    monkeypatch.setattr(walk, "_evaluate_step", stepped)
    assert api.transition(model, pre, steps)["exit_code"] == 0
    initial = [owner for stage, owner in seen if stage in ("check", "standing", "initial")]
    assert len(initial) == 3 and initial[0] is not None
    assert all(owner is initial[0] for owner in initial)
    assert initial[0].model is model and initial[0].population is pre
    assert any(stage == "step" for stage, _owner in seen)
    assert all(owner is None for stage, owner in seen if stage in ("step", "refresh"))
    assert preparation.current_scope() is None


def test_public_preparation_exception_restores_scope_and_existing_internal_exit(monkeypatch):
    model, pre, steps = inputs()
    seen = []

    def explode(actual_model, population, **kwargs):
        seen.append(preparation.current_scope())
        raise RuntimeError("initial structured view control")

    monkeypatch.setattr(walk, "structured_extension_view", explode)
    result = api.transition(model, pre, steps)
    assert result["exit_code"] == 70
    assert preparation.current_scope() is None
    assert seen and seen[0] is not None
    assert seen[0].model is model and seen[0].population is pre


def test_unrelated_owner_is_restored_instead_of_joined(monkeypatch):
    model, pre, steps = inputs()
    seen = []
    original = walk.structured_extension_view

    def observed(actual_model, population, **kwargs):
        if population is pre:
            seen.append(preparation.current_scope())
        return original(actual_model, population, **kwargs)

    monkeypatch.setattr(walk, "structured_extension_view", observed)
    with preparation.calculation_scope(object(), object()) as unrelated:
        assert api.transition(model, pre, steps)["exit_code"] == 0
        assert preparation.current_scope() is unrelated
        assert seen[0] is not unrelated
        assert seen[0].model is model and seen[0].population is pre
    assert preparation.current_scope() is None


def test_pre_mutation_is_refused_even_after_check_warmed_scope(monkeypatch):
    model, pre, steps = inputs()
    seen = []
    original = walk.structured_extension_view

    def changed(actual_model, population, **kwargs):
        if population is pre:
            seen.append(preparation.current_scope())
            pre.facts["edge"].pop()
        return original(actual_model, population, **kwargs)

    monkeypatch.setattr(walk, "structured_extension_view", changed)
    result = api.transition(model, pre, steps)
    assert result["exit_code"] == 70
    assert not pre.matches_validation_marker(model)
    assert preparation.current_scope() is None
    assert seen[0] is not None


@pytest.mark.parametrize(
    "barrier", ["partial-policy", "reference-work", "prior-possible", "selective"]
)
def test_ineligible_initial_calculation_is_fresh_without_changing_walk(monkeypatch, barrier):
    model, pre, steps = inputs()
    baseline = api.transition(model, pre, steps)
    calls = body_counter(monkeypatch)
    seen = []
    original = walk.structured_extension_view

    def observed(actual_model, population, **kwargs):
        if population is not pre or kwargs:
            return original(actual_model, population, **kwargs)
        owner = preparation.current_scope()
        before = len(calls)
        if barrier == "partial-policy":
            token = ext.PARTIAL_OPAQUE.set(True)
            try:
                view = original(actual_model, population)
            finally:
                ext.PARTIAL_OPAQUE.reset(token)
        elif barrier == "reference-work":
            token = ext.REFERENCE_PRESENTATION_WORK.set(ReferenceJoinWork())
            try:
                view = original(actual_model, population)
            finally:
                ext.REFERENCE_PRESENTATION_WORK.reset(token)
        elif barrier == "prior-possible":
            view = original(actual_model, population, previous_possible={})
        else:
            prior = original(actual_model, population)
            before = len(calls)
            view = original(actual_model, population, previous=prior.facts, refresh=("reaches",))
        seen.append((owner, len(calls) - before))
        return view

    monkeypatch.setattr(walk, "structured_extension_view", observed)
    assert api.transition(model, pre, steps) == baseline
    assert seen[0][1] > 0
    assert seen[0][0] is not None
    assert seen[0][0].model is model and seen[0][0].population is pre
    assert preparation.current_scope() is None
