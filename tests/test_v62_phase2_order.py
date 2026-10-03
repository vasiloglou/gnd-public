from __future__ import annotations

from support.v62_phase2_corpus import FIXTURE, population, steps, write_model, write_steps

from gnd import transition as transition_module
from gnd.api import transition
from gnd.model import load_model

MODEL = FIXTURE / 'models/dynamic.orm.yaml'

def test_a01_refresh_precedes_consequences_rules_and_intermediate(monkeypatch) -> None:
    events: list[str] = []
    original_view = transition_module.structured_extension_view
    original_changes = transition_module._derived_changes
    original_rules = transition_module._evaluate_derived_dynamic_rules
    original_intermediate = transition_module._load_intermediate

    def view(*args, **kwargs):
        if kwargs.get('refresh'):
            events.append('refresh')
        return original_view(*args, **kwargs)

    def changes(*args, **kwargs):
        events.append('changes')
        return original_changes(*args, **kwargs)

    def rules(*args, **kwargs):
        events.append('rules')
        return original_rules(*args, **kwargs)

    def intermediate(*args, **kwargs):
        events.append('intermediate')
        return original_intermediate(*args, **kwargs)
    monkeypatch.setattr(transition_module, 'structured_extension_view', view)
    monkeypatch.setattr(transition_module, '_derived_changes', changes)
    monkeypatch.setattr(transition_module, '_evaluate_derived_dynamic_rules', rules)
    monkeypatch.setattr(transition_module, '_load_intermediate', intermediate)
    payload = transition(MODEL, population('pre_open'), steps(), population('post_resolved'), unredacted=True)
    assert payload['exit_code'] == 0
    first_refresh = events.index('refresh')
    assert events[first_refresh:first_refresh + 4] == ['refresh', 'changes', 'rules', 'intermediate']

def test_f01_current_step_precondition_reads_the_old_extension() -> None:
    payload = transition(MODEL, population('pre_open'), steps(), population('post_resolved'), unredacted=True)
    first = payload['transition']['steps'][0]
    assert not [row for row in first['verdicts'] if row['kind'] == 'precondition']

def test_i06_mixed_rule_lanes_keep_original_source_indices(tmp_path) -> None:

    def mutate(doc):
        operation = next(row for row in doc['operations'] if row['id'] == 'raise_score')
        operation['dynamic_rules'].append({'id': 'asserted_score_never_decreases', 'subject': {'fact_type': 'evidence_score', 'value_role': 'score', 'bind': {'ticket': '$ticket'}}, 'op': '>=', 'modality': 'alethic', 'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'user_quote': 'Asserted score never decreases.'}})
    model_path = write_model(tmp_path, mutate)
    model = load_model(model_path)
    focused = write_steps(tmp_path, model, [{'op': 'raise_score', 'bindings': {'ticket': 'SECRET-TICKET-314159', 'new_score': 0}}])
    payload = transition(model_path, population('pre_open'), focused, post=None, unredacted=True)
    locators = [row['locator'] for row in payload['transition']['steps'][0]['verdicts'] if row['kind'] == 'dynamic-rule']
    assert '$.steps[1].dynamic_rules[1]' in locators
