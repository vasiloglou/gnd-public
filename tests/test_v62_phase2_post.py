from __future__ import annotations

from support.v62_phase2_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'

def _run(post: str) -> dict:
    return transition(MODEL, population('pre_open'), steps(), population(post), unredacted=True)

def test_d02_matching_computed_final_claim_passes() -> None:
    payload = _run('post_resolved')
    assert payload['exit_code'] == ANSWERS['D02']['exit']
    assert not [row for row in payload['transition']['post_snapshot']['derivations'] if row['verdict'] != 'pass']

def test_d01_declared_post_cannot_self_justify_its_claim() -> None:
    payload = _run('post_self_justifying')
    failures = [row for row in payload['transition']['post_snapshot']['derivations'] if row['fact_type'] == 'ticket_score' and row['verdict'] == 'fail']
    assert failures, 'the declared score 99 must be compared with computed-final score 2'
    assert payload['exit_code'] == ANSWERS['D01']['exit']
    assert payload['transition']['frame_verdicts'], 'frame and claim are separate families'

def test_declared_post_does_not_change_plan_state() -> None:
    payload = _run('post_resolved')
    assert payload['transition']['computed_post'] is None
