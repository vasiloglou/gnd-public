"""Synthetic-intermediate grading contract for v6.2 Phase 2."""

from __future__ import annotations

from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd import transition as transition_module
from gnd.api import transition
from gnd.model import load_model
from gnd.population import load_population

MODEL = FIXTURE / "models/dynamic.orm.yaml"


def test_h01_intermediates_grade_no_derivation_claim() -> None:
    payload = transition(MODEL, population("pre_open"), steps(), post=None, unredacted=True)
    for step in payload["transition"]["steps"]:
        assert step["intermediate"]["derivations"] == []


def test_h03_supplied_pre_claim_is_still_graded() -> None:
    payload = transition(MODEL, population("pre_open"), steps(), post=None, unredacted=True)
    assert payload["transition"]["pre_snapshot"]["derivations"]


def test_unloadable_final_effective_state_does_not_replace_post_claims(monkeypatch) -> None:
    monkeypatch.setattr(transition_module, "_load_intermediate", lambda *args: (None, None))
    model = load_model(MODEL)
    pre = load_population(population("pre_open"), model=model)
    post = load_population(population("post_self_justifying"), model=model)
    document = transition_module.read_steps_document(steps())
    walk = transition_module.evaluate(model, pre, post, document["steps"])
    score = next(row for row in walk.post_snapshot.derivations if row.fact_type == "ticket_score")
    assert score.verdict == "pass"
