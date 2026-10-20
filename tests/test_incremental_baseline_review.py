"""Regression controls for reproduced IE0 independent review findings."""
import copy
import json
import time
from collections import Counter

import pytest
from test_incremental_baseline import tool

from gnd import api, correspondence, extensions
from gnd.semantic_adapter import adapt_snapshot_observed


def test_r1_count_evaluators_not_finding_labels():
    m, p = next(tool.localized_inputs())
    adapted = adapt_snapshot_observed(m, p)
    constraint = adapted.snapshot.constraints[0]
    with tool.count_work() as counts:
        for _ in range(2):
            correspondence._inline_uniqueness_result(constraint, adapted.snapshot)
        before = counts['constraint_evaluations']
        correspondence._finding_scope(constraint, adapted.snapshot, 'pass', None, 'evaluate', variant='inline')
    assert before == 2
    assert counts['constraint_evaluations'] == before


def test_r2_zero_and_multiple_body_calls():
    m, p = next(tool.localized_inputs())
    facts = extensions._relation_facts(extensions.base_relations(m, p))
    with tool.count_work() as counts:
        assert counts['derivation_body_evaluations'] == 0
        for _ in range(3):
            extensions._clause_bindings(m.fact_types[2]['derivation_rule'], facts, extensions.JoinWork())
        assert counts['derivation_body_evaluations'] == 3
    # A genuine no-derivation public check keeps the registered counter enabled.
    from gnd.model import Model
    from gnd.population import load_population_bytes
    doc = m.model_dump()
    doc['fact_types'] = doc['fact_types'][:2]
    no_rules = Model.model_validate(doc)
    pop = json.loads((tool.FIXTURE/'initial.pop.json').read_text())
    pop['facts'] = {k: v for k, v in pop['facts'].items() if k in ('left', 'right')}
    pop['population']['covers'] = ['left', 'right']
    admitted = load_population_bytes(json.dumps(pop).encode(), source='no-rules.json', model=no_rules)
    with tool.count_work() as counts:
        assert api.check(no_rules, admitted)['exit_code'] in (0, 2)
    assert counts['derivation_body_evaluations'] == 0


def accepted_document():
    def mode(checks):
        return {'calls': 13, 'totals': {'checker_runs': checks, 'public_check_calls': 7, 'receipt_mints': 0, 'public_transition_calls': 6, 'derivation_body_evaluations': 4878, 'constraint_evaluations': 100}, 'payload_digests': ['x']*13, 'branches': ['branch'], 'per_call': [{'semantics': {k: ['ok'] for k in ('extensions', 'lineage', 'unavailable', 'possible')}} for _ in range(13)], 'semantic_replay': {k: ([2]*13 if k == 'exit' else ['ok']) for k in tool.SURFACES}}
    return {'source_head': 'source', 'identities': tool.identities(), 'work': {'reporter': {'full': mode(25), 'receipts': mode(19), 'fresh_full': mode(25)}}, 'parity': [{'case': 'control', 'exit': 0, 'expected_exit': 0, 'mismatches': []}], 'receipt_probe': {}, 'new_workload': 'not supplied'}


def test_r3_wrong_denominators_and_dead_counters_refuse():
    original = accepted_document()
    assert tool.validate_evidence(original)
    for field, value in [('calls', 1), ('checker_runs', 1), ('derivation_body_evaluations', 0), ('constraint_evaluations', 0)]:
        changed = copy.deepcopy(original)
        row = changed['work']['reporter']['receipts']
        (row if field == 'calls' else row['totals'])[field] = value
        assert not tool.validate_evidence(changed)


@pytest.mark.parametrize('surface', ['branches', 'lineage', 'possible'])
def test_r4_transition_semantic_corruption_refuses(surface):
    document = accepted_document()
    changed = document['work']['reporter']['fresh_full']
    changed['semantic_replay'][surface] = ['wrong']
    assert not tool.validate_evidence(document)
    document = accepted_document()
    document['work']['reporter']['receipts']['branches'] = ['wrong']
    assert not tool.validate_evidence(document)


def test_r5_partial_patterns_are_live():
    _, m, p = next(row for row in tool.extra_controls() if row[0] == 'partial')
    observed = tool.observation(m, p, compiled=True)
    assert observed['possible']
    changed = copy.deepcopy(observed)
    changed['possible']['reaches'][0][1]['coordinate'] = ['different-origin', 999, 'target']
    assert tool.compare_results(observed, changed) == ['possible']


def test_r6_equal_errors_are_not_acceptance():
    document = accepted_document()
    document['parity'][0]['exit'] = 70
    assert not tool.validate_evidence(document)


def test_r7_executed_inputs_have_identities():
    identities = tool.identities()
    for path in [tool.previous.COURSE/'state.pop.json', tool.ROOT/'tests/fixtures/v62-phase4/populations/aggregate-input.pop.yaml', tool.ROOT/'tools/measure_transition_cost.py']:
        assert str(path.relative_to(tool.ROOT)) in identities


def test_r9_alternate_support_survives_deletion():
    rows = {n: tool.semantic_envelope(m, p) for n, m, p in tool.extra_controls() if n.startswith('recursive')}
    assert rows['recursive-alternate']['extensions']['reaches'] != []
    after = rows['recursive-alternate-delete']
    assert ['A', 'C'] in after['extensions']['reaches']
    assert ['B', 'C'] not in after['extensions']['reaches']
    assert after['lineage'] != rows['recursive-alternate']['lineage']


def test_r10_partial_work_is_counted():
    _, m, p = next(row for row in tool.extra_controls() if row[0] == 'partial')
    token = extensions.PARTIAL_OPAQUE.set(True)
    try:
        with tool.count_work() as counts:
            extensions.evaluate_derivations(m, p)
        assert counts['partial_body_evaluations'] > 0
        assert counts['partial_join_candidates'] > 0
    finally:
        extensions.PARTIAL_OPAQUE.reset(token)


@pytest.mark.parametrize('workload,expected', [('course', 3), ('localized', 6)])
def test_r11_receipt_arm_uses_receipts(monkeypatch, workload, expected):
    calls = Counter()
    mint = api.check_with_receipt
    transition = api.transition
    def counted_mint(*a, **k):
        calls['mint'] += 1
        return mint(*a, **k)
    def counted_transition(*a, **k):
        calls['consume'] += k.get('pre_receipt') is not None
        return transition(*a, **k)
    monkeypatch.setattr(api, 'check_with_receipt', counted_mint)
    monkeypatch.setattr(api, 'transition', counted_transition)
    tool.replay_full(workload, receipts=True)
    assert calls['mint'] == expected
    assert calls['consume'] == (3 if workload == 'course' else 0)


def test_r12_timing_split(monkeypatch):
    def replay(*a, **k):
        time.sleep(.01)
        tool.public_call(lambda: {'exit_code': 0})
    monkeypatch.setattr(tool, 'replay_full', replay)
    result = tool.measure_modes('localized', repeat=1)
    assert result['loading_and_driver_samples']['A'][0] >= .01
    assert result['public_evaluation_samples']['A'][0] < .01


def test_r13_consumed_receipt_probe():
    result = tool.receipt_probe()
    assert result['reusable']
    assert not result['transition_changed']  # IE3 protects the authoritative receipt report


def test_r6_materialized_controls_do_not_share_mutable_models():
    rows = tool.parity_checks()
    assert all(row['exit'] == row['expected_exit'] for row in rows)


def test_r9_live_reference_and_option_changes():
    rows = tool.reference_and_option_controls()
    assert [row['exit'] for row in rows] == [0, 1, 4]
    assert all(not row['mismatches'] for row in rows)


def test_r2_constant_counter_mutant_is_rejected(monkeypatch):
    from contextlib import contextmanager
    @contextmanager
    def constant():
        yield Counter({'derivation_body_evaluations': 1, 'constraint_evaluations': 1})
    monkeypatch.setattr(tool, 'count_work', constant)
    with pytest.raises(AssertionError):
        test_r2_zero_and_multiple_body_calls()


def test_confirmation_receipt_semantics_cannot_be_deleted_or_corrupted():
    for delete in (False, True):
        document = accepted_document()
        semantics = document['work']['reporter']['receipts']['semantic_replay']
        if delete:
            del semantics['lineage']
        else:
            semantics['lineage'] = ['changed-only-in-receipt-arm']
        assert not tool.validate_evidence(document)


def test_confirmation_course_expected_exit_is_binding():
    document = accepted_document()
    modes = document['work'].pop('reporter')
    for row in modes.values():
        row['calls'] = 3
        row['payload_digests'] = ['same'] * 3
        row['totals']['public_check_calls'] = 3
        row['totals']['public_transition_calls'] = 3
        row['per_call'] = row['per_call'][:3]
        row['semantic_replay']['exit'] = [1, 1, 0]
    document['work']['course'] = modes
    assert tool.validate_evidence(document)
    for row in modes.values():
        row['semantic_replay']['exit'] = [1, 1, 1]
    assert not tool.validate_evidence(document)


def test_confirmation_missing_one_executed_identity_refuses():
    document = accepted_document()
    document['identities'] = tool.identities()
    del document['identities']['tools/measure_transition_cost.py']
    assert not tool.validate_evidence(document)


def test_course_pair_has_the_same_explicit_public_precheck(monkeypatch):
    calls = Counter()
    check = api.check
    transition = api.transition
    def counted_check(*a, **k):
        calls['check'] += 1
        return check(*a, **k)
    def counted_transition(*a, **k):
        calls['transition'] += 1
        return transition(*a, **k)
    monkeypatch.setattr(api, 'check', counted_check)
    monkeypatch.setattr(api, 'transition', counted_transition)
    tool.replay_full('course', receipts=False)
    assert calls == {'check': 3, 'transition': 3}
