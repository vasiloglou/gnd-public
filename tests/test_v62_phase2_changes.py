from __future__ import annotations

from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'
TICKET = 'SECRET-TICKET-314159'

def _run() -> dict:
    return transition(MODEL, population('pre_open'), steps(), post=None, unredacted=True)

def test_c01_additions_are_consequences_not_frame_verdicts() -> None:
    payload = _run()
    first = payload['transition']['steps'][0]
    assert first['derived_changes'] == [{'fact_type': 'resolvable', 'added': [{'ticket': TICKET}], 'removed': []}, {'fact_type': 'ready', 'added': [{'ticket': TICKET}], 'removed': []}]
    assert not [row for row in first['verdicts'] if row['kind'] == 'frame']

def test_c02_replacement_reports_removed_and_added_identity_rows() -> None:
    payload = _run()
    score = payload['transition']['steps'][1]['derived_changes']
    assert score == [{'fact_type': 'ticket_score', 'added': [{'ticket': TICKET, 'score': 2}], 'removed': [{'ticket': TICKET, 'score': 1}]}]

def test_c03_no_delta_omits_the_optional_field() -> None:
    payload = _run()
    assert 'derived_changes' not in payload['transition']['steps'][2]
