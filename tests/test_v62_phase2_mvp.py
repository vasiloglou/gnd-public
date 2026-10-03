from __future__ import annotations

from support.v62_phase2_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'

def test_m01_walk_composes_dynamic_views_end_to_end() -> None:
    payload = transition(MODEL, population('pre_open'), steps(), population('post_resolved'), unredacted=True)
    assert payload['exit_code'] == ANSWERS['M01']['exit']
    assert payload['transition']['evaluated'] is True
    assert len(payload['transition']['steps']) == 3

def test_m03_plan_publishes_only_durable_asserted_state() -> None:
    payload = transition(MODEL, population('pre_open'), steps(), post=None, unredacted=True)
    assert payload['exit_code'] == ANSWERS['M03']['exit']
    facts = payload['transition']['computed_post']['facts']
    assert not {'ready', 'ticket_score'}.intersection(facts)
    assert facts['resolvable'] == [{'ticket': 'authored-surplus'}]
