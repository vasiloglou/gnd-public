from __future__ import annotations

from support.v62_phase2_corpus import ANSWERS, FIXTURE, population, steps

from gnd.api import transition

MODEL = FIXTURE / 'models/dynamic.orm.yaml'

def _run(post: str='post_resolved', *, unredacted: bool=True) -> dict:
    return transition(MODEL, population('pre_open'), steps(), population(post), unredacted=unredacted)

def test_m01_clean_ticket_lifecycle() -> None:
    payload = _run()
    assert payload['exit_code'] == ANSWERS['M01']['exit']
    report = payload['transition']
    assert report['evaluated'] is True
    assert len(report['steps']) == 3
    precondition_findings = [row for row in report['steps'][2]['verdicts'] if row['kind'] == 'precondition']
    assert precondition_findings == []

def test_a01_refresh_consequences_precede_the_later_read() -> None:
    payload = _run()
    first = payload['transition']['steps'][0]
    assert first['derived_changes'] == [{'fact_type': 'resolvable', 'added': [{'ticket': 'SECRET-TICKET-314159'}], 'removed': []}, {'fact_type': 'ready', 'added': [{'ticket': 'SECRET-TICKET-314159'}], 'removed': []}]
    assert payload['transition']['steps'][2]['verdicts'] == []

def test_b01_derived_subject_compares_old_and_new_extensions() -> None:
    payload = _run()
    score_step = payload['transition']['steps'][1]
    assert score_step['derived_changes'] == [{'fact_type': 'ticket_score', 'added': [{'ticket': 'SECRET-TICKET-314159', 'score': 2}], 'removed': [{'ticket': 'SECRET-TICKET-314159', 'score': 1}]}]
    assert not [row for row in score_step['verdicts'] if row['kind'] == 'dynamic-rule']

def test_f02_the_later_precondition_reads_the_refreshed_upper_stratum() -> None:
    payload = _run()
    final_step = payload['transition']['steps'][2]
    assert not [row for row in final_step['verdicts'] if row['kind'] == 'precondition']
