from __future__ import annotations

import copy

from support.v62_phase2_corpus import FIXTURE, population, steps

from gnd import checker
from gnd import transition as runtime
from gnd.api import transition
from gnd.model import load_model
from gnd.population import load_population

MODEL = FIXTURE / 'models/dynamic.orm.yaml'
TICKET = 'SECRET-TICKET-314159'

def _payload(post='post_resolved'):
    return transition(MODEL, population('pre_open'), steps(), population(post), unredacted=True)

def _score_rule(model):
    return copy.deepcopy(next(row for row in model.operations if row['id'] == 'raise_score'))

def _score_verdicts(model, old, new, touched=frozenset({'evidence_score'})):
    return runtime._evaluate_derived_dynamic_rules(1, _score_rule(model), {'ticket': TICKET, 'new_score': new}, model, {'ticket_score': [{'ticket': TICKET, 'score': old}]}, {'ticket_score': [{'ticket': TICKET, 'score': new}]}, touched, frozenset({'ticket_score'}), {}, {})

def test_mutation_a_refresh_after_consumers_is_killed(monkeypatch) -> None:
    baseline = _payload()
    original = runtime.structured_extension_view

    def stale(model, pop, *, previous=None, previous_unavailable=None, previous_possible=None, refresh=None):
        if refresh is not None:
            return checker.StructuredExtensionView(facts=previous, recomputed=(), work=checker.DynamicRefreshWork(), unavailable=previous_unavailable or {}, possible=previous_possible or {})
        return original(model, pop, previous=previous, previous_unavailable=previous_unavailable, previous_possible=previous_possible, refresh=refresh)
    monkeypatch.setattr(runtime, 'structured_extension_view', stale)
    mutant = _payload()
    assert baseline['transition']['steps'][0].get('derived_changes')
    assert not mutant['transition']['steps'][0].get('derived_changes')

def test_mutation_b_compare_new_with_new_is_killed(monkeypatch) -> None:
    model = load_model(MODEL)
    baseline = _score_verdicts(model, 2, 1)
    original = runtime._compare_values
    monkeypatch.setattr(runtime, '_compare_values', lambda op, new, old: original(op, new, new))
    mutant = _score_verdicts(model, 2, 1)
    assert [row.verdict for row in baseline] == ['fail']
    assert mutant == []

def test_mutation_c_drop_consequence_delta_is_killed(monkeypatch) -> None:
    baseline = _payload()
    monkeypatch.setattr(runtime, '_derived_changes', lambda *args, **kwargs: [])
    mutant = _payload()
    assert baseline['transition']['steps'][0].get('derived_changes')
    assert 'derived_changes' not in mutant['transition']['steps'][0]

def test_mutation_d_declared_post_self_justification_is_killed(monkeypatch) -> None:
    baseline = _payload('post_self_justifying')
    original = runtime.derivation_claims_against
    monkeypatch.setattr(runtime, 'derivation_claims_against', lambda model, post, final: original(model, post, post))
    mutant = _payload('post_self_justifying')
    baseline_rows = baseline['transition']['post_snapshot']['derivations']
    mutant_rows = mutant['transition']['post_snapshot']['derivations']
    assert any(row['fact_type'] == 'ticket_score' and row['verdict'] == 'fail' for row in baseline_rows)
    assert not any(row['fact_type'] == 'ticket_score' and row['verdict'] == 'fail' for row in mutant_rows)

def test_mutation_e_skip_coverage_is_killed(monkeypatch, tmp_path) -> None:
    from tests.test_v62_phase2_coverage import _without_cover
    missing = _without_cover(tmp_path, 'blocked')
    baseline = transition(MODEL, missing, steps(), population('post_resolved'))
    monkeypatch.setattr(runtime, 'assert_dynamic_derivation_coverage', lambda *args, **kwargs: None)
    mutant = transition(MODEL, missing, steps(), population('post_resolved'))
    assert baseline['exit_code'] == 3
    assert mutant['transition']['evaluated'] is True

def test_mutation_f_read_precondition_after_effects_is_killed() -> None:
    model = load_model(MODEL)
    pre = load_population(population('pre_open'), model=model)
    operation = copy.deepcopy(next(row for row in model.operations if row['id'] == 'add_evidence'))
    operation['preconditions'] = [{'id': 'must_be_absent_before_add', 'require': [{'fact_type': 'evidence', 'bind': {'ticket': '$ticket'}}], 'modality': 'alethic'}]
    state = runtime._state_of(pre)
    baseline, after = runtime._evaluate_step(1, {'bindings': {'ticket': TICKET}}, operation, model, state, pre)
    mutant, _ = runtime._evaluate_step(1, {'bindings': {'ticket': TICKET}}, operation, model, after, pre)
    assert any(row.kind == 'precondition' for row in baseline.verdicts)
    assert not any(row.kind == 'precondition' for row in mutant.verdicts)

def test_mutation_g_feed_semiderived_surplus_upward_is_killed() -> None:
    model = load_model(MODEL)
    pre = load_population(population('pre_open'), model=model)
    baseline = checker.structured_extension_view(model, pre).facts
    mutant_ready = tuple({'ticket': row['ticket']} for row in pre.facts['resolvable'])
    assert baseline['ready'] == ()
    assert mutant_ready == ({'ticket': 'authored-surplus'},)

def test_mutation_h_retain_intermediate_claims_is_killed(monkeypatch) -> None:
    monkeypatch.setattr(runtime, '_without_derivation_claims', lambda report: report)
    mutant = _payload()
    assert any(step['intermediate']['derivations'] for step in mutant['transition']['steps'])

def test_mutation_i_direct_touch_gate_is_killed() -> None:
    model = load_model(MODEL)
    baseline = _score_verdicts(model, 2, 1)
    mutant = _score_verdicts(model, 2, 1, touched=frozenset({'ticket_score'}))
    assert [row.verdict for row in baseline] == ['fail']
    assert mutant == []
