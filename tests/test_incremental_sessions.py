"""IE3 corpus-first public session and private receipt controls."""

import pytest

from gnd import api
from gnd.branches import capture_branches
from tests.test_incremental_baseline import tool


def session(model, **kwargs):
    return api.EvaluationSession(model, **kwargs)


def test_explicit_facade_and_noop_evaluator_zero():
    m, p = next(tool.localized_inputs())
    owner = session(m)
    with capture_branches() as expected_branches:
        expected = api.check(m, p)
    with tool.count_work() as counts:
        for attempt in range(2):
            before = dict(counts)
            with capture_branches() as branches:
                actual = owner.check(p)
            assert actual == expected
            assert branches == expected_branches
            if attempt:
                assert counts['constraint_evaluations'] == before['constraint_evaluations']
                assert counts['derivation_body_evaluations'] == before['derivation_body_evaluations']
    assert owner.stats()['hits'] > 0
    owner.reset()
    assert owner.stats()['entries'] == 0
    owner.close()
    with pytest.raises(ValueError, match='closed'):
        owner.check(p)


def test_localized_full_payload_and_result_detachment():
    owner = None
    for m, p in tool.localized_inputs():
        if owner is None:
            owner = session(m)
        expected = api.check(m, p)
        with capture_branches() as branches:
            actual = owner.check(p)
        assert actual == expected
        actual.clear()
    assert owner.stats()['hits'] > 0


def test_session_bounds_preserve_full_fallback():
    m, p = next(tool.localized_inputs())
    owner = session(m, max_bytes=1)
    for _ in range(2):
        assert owner.check(p) == api.check(m, p)
        assert owner.stats()['entries'] == 0


def test_receipt_public_report_mutation_cannot_change_transition():
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.previous.COURSE
    m = load_model(root / 'model.orm.json')
    p = load_population(root / 'state.pop.json', model=m)
    steps = tool.previous._course_steps('attempt-3.steps.json')
    _, receipt = api.check_with_receipt(m, p)
    assert receipt.reusable
    expected = api.transition(m, p, steps, pre_receipt=receipt)
    assert receipt.report.verdicts
    receipt.report.verdicts[0].message = 'Public receipt mutation probe'
    assert api.transition(m, p, steps, pre_receipt=receipt) == expected


def test_session_declared_and_computed_walks_preserve_payloads():
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.previous.COURSE
    m = load_model(root / 'model.orm.json')
    p = load_population(root / 'state.pop.json', model=m)
    owner = session(m)
    steps = tool.previous._course_steps('attempt-3.steps.json')
    for _ in range(2):
        expected = api.transition(m, p, steps)
        assert owner.transition(p, steps) == expected


def test_mutation_error_does_not_advance_generation():
    m, p = next(tool.localized_inputs())
    owner = session(m)
    owner.check(p)
    before = owner.stats()['generation']
    p.facts['left'].append({'item': 'new'})
    assert owner.check(p) == api.check(m, p)
    assert owner.stats()['generation'] == before


def test_trusted_semantic_records_have_bounded_typed_keys(monkeypatch):
    from gnd import extension_preparation as preparation
    from gnd.semantic_ir import Scalar
    integer = Scalar('number', '', 1, 1, True, 'number')
    boolean = Scalar('boolean', 'true', 0, 1, False, 'boolean')
    assert preparation.fingerprint(integer) is not None
    assert preparation.fingerprint(integer) != preparation.fingerprint(boolean)
    monkeypatch.setattr(preparation, 'MAX_FINGERPRINT_NODES', 1)
    assert preparation.fingerprint(integer) is None


def test_independent_inline_constraint_executes_no_right_evaluator(monkeypatch):
    from gnd import correspondence
    from gnd.population import load_population
    m, p = next(tool.localized_inputs())
    current = session(m)
    calls = []
    original = correspondence._inline_uniqueness_result

    def observed(constraint, snapshot):
        result = original(constraint, snapshot)
        if result is not None:
            calls.append(constraint.fact_type)
        return result

    monkeypatch.setattr(correspondence, '_inline_uniqueness_result', observed)
    current.check(p)
    calls.clear()
    changed = load_population(tool.FIXTURE / 'insert.pop.json', model=m)
    expected = api.check(m, changed)
    calls.clear()
    assert current.check(changed) == expected
    assert 'left_copy' in calls
    assert 'right_copy' not in calls
