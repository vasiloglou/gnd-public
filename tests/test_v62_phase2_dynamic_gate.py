from __future__ import annotations

import copy

import pytest
from support.v62_phase2_corpus import FIXTURE, population, write_steps

from gnd import transition as transition_module
from gnd.api import transition
from gnd.model import load_model

MODEL = FIXTURE / 'models/dynamic.orm.yaml'
TICKET = 'SECRET-TICKET-314159'

def _derived_rule_verdicts(*, old=1, new=2, modality='alethic', model=None):
    model = model or load_model(MODEL)
    operation = copy.deepcopy(next(row for row in model.operations if row['id'] == 'raise_score'))
    operation['dynamic_rules'][0]['modality'] = modality
    old_rows = [] if old is None else [{'ticket': TICKET, 'score': old}]
    new_rows = [] if new is None else [{'ticket': TICKET, 'score': new}]
    return transition_module._evaluate_derived_dynamic_rules(1, operation, {'ticket': TICKET, 'new_score': new}, model, {'ticket_score': old_rows}, {'ticket_score': new_rows}, frozenset({'evidence_score'}), frozenset({'ticket_score'}), {}, {})

def test_i01_dependency_touch_and_delta_grades_the_derived_subject() -> None:
    payload = transition(MODEL, population('pre_open'), FIXTURE / 'walks/ticket.steps.json', post=None, unredacted=True)
    score_step = payload['transition']['steps'][1]
    assert score_step['derived_changes']
    assert not [row for row in score_step['verdicts'] if row['verdict'] == 'fail']

def test_i03_unrelated_touch_does_not_refresh_or_grade(tmp_path) -> None:
    model = load_model(MODEL)
    focused = write_steps(tmp_path, model, [{'op': 'annotate', 'bindings': {'ticket': TICKET}}])
    payload = transition(MODEL, population('pre_open'), focused, post=None, unredacted=True)
    step = payload['transition']['steps'][0]
    assert 'derived_changes' not in step
    assert not [row for row in step['verdicts'] if row['kind'] == 'dynamic-rule']

def test_i02_another_subjects_delta_does_not_grade_this_binding() -> None:
    model = load_model(MODEL)
    operation = next(row for row in model.operations if row['id'] == 'raise_score')
    verdicts = transition_module._evaluate_derived_dynamic_rules(1, operation, {'ticket': 'absent-ticket', 'new_score': 2}, model, {'ticket_score': [{'ticket': 'other-ticket', 'score': 1}]}, {'ticket_score': [{'ticket': 'other-ticket', 'score': 2}]}, frozenset({'evidence_score'}), frozenset({'ticket_score'}), {}, {})
    assert verdicts == []

def test_b02_decreasing_derived_value_fails_alethically() -> None:
    [verdict] = _derived_rule_verdicts(old=2, new=1)
    assert (verdict.verdict, verdict.scope_id) == ('fail', 'transition:dynamic-rule:derived-comparison:violated:alethic')

@pytest.mark.parametrize(('old', 'new', 'scope'), [(1, None, 'transition:dynamic-rule:derived-no-new:vacuous'), (None, 1, 'transition:dynamic-rule:derived-no-old:vacuous')], ids=['B03', 'B05'])
def test_missing_derived_comparison_side_is_vacuous(old, new, scope) -> None:
    [verdict] = _derived_rule_verdicts(old=old, new=new)
    assert (verdict.verdict, verdict.scope_id) == ('vacuous', scope)

def test_b04_nonfunctional_derived_subject_is_unchecked(tmp_path) -> None:
    from support.v62_phase2_corpus import write_model

    def remove_uniqueness(doc) -> None:
        score = next(row for row in doc['fact_types'] if row['id'] == 'ticket_score')
        score['constraints'] = []
    model = load_model(write_model(tmp_path, remove_uniqueness))
    [verdict] = _derived_rule_verdicts(model=model)
    assert (verdict.verdict, verdict.reason_code) == ('unchecked', 'transition:dynamic-subject-not-functional')

def test_b06_decreasing_derived_value_warns_deontically() -> None:
    [verdict] = _derived_rule_verdicts(old=2, new=1, modality='deontic')
    assert (verdict.verdict, verdict.scope_id) == ('warning', 'transition:dynamic-rule:derived-comparison:violated:deontic')
