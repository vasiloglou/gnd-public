"""IE5 pre-implementation capability/configuration policy-key corpus."""
import pytest

from gnd.incremental_state import ReuseState
from tests.test_incremental_baseline import tool


def test_prepared_policy_normalizes_once_with_same_results(monkeypatch):
    from gnd import incremental_state

    m, _ = next(tool.localized_inputs())
    owner = ReuseState(m)
    original = incremental_state._policy
    calls = []

    def observed(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(incremental_state, '_policy', observed)
    with owner.transaction(m):
        policy = owner.prepare_policy((len, ('limit', 3)))
        for _ in range(3):
            assert owner.reuse('unit', 'one', (), lambda: 7, policy=policy) == 7
    assert len(calls) == 1
    assert owner.stats()['hits'] == 2


def test_prepared_policy_expired_and_foreign_compute_fresh():
    m, _ = next(tool.localized_inputs())
    owner, foreign = ReuseState(m), ReuseState(m)
    calls = []

    def calculate():
        calls.append(1)
        return len(calls)

    with owner.transaction(m):
        policy = owner.prepare_policy((calculate,))
        assert owner.reuse('unit', 'one', (), calculate, policy=policy) == 1
    with owner.transaction(m):
        assert owner.reuse('unit', 'one', (), calculate, policy=policy) == 2
    with foreign.transaction(m):
        assert foreign.reuse('unit', 'one', (), calculate, policy=policy) == 3
    assert owner.stats()['bypasses'] > 0
    assert foreign.stats()['entries'] == 0


def test_prepared_policy_checks_live_code_and_mutable_configuration(monkeypatch):
    m, _ = next(tool.localized_inputs())
    owner = ReuseState(m)

    def helper():
        return 1

    def alternate():
        return 2

    config = {'limit': 1}
    with owner.transaction(m):
        policy = owner.prepare_policy((helper, config))
        assert owner.reuse('unit', 'one', (), helper, policy=policy) == 1
        monkeypatch.setattr(helper, '__code__', alternate.__code__)
        assert owner.reuse('unit', 'one', (), helper, policy=policy) == 2
        config['limit'] = 2
        assert owner.reuse('unit', 'two', (), lambda: config['limit'], policy=policy) == 2
        assert owner.stats()['bypasses'] >= 2


def test_unsupported_prepared_policy_keeps_full_fallback_and_bounds():
    m, _ = next(tool.localized_inputs())
    owner = ReuseState(m, max_bytes=1)
    with owner.transaction(m):
        policy = owner.prepare_policy((object(),))
        assert owner.reuse('unit', 'one', (), lambda: 9, policy=policy) == 9
    assert owner.stats()['entries'] == 0
    with pytest.raises(ValueError, match='active'):
        owner.prepare_policy(())


def test_whole_call_fallback_diagnostic_is_not_unit_bypass_rate():
    from gnd import api

    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    p.facts['left'].append({'item': 'lost-marker'})
    actual = owner.check(p, references=object())
    assert actual['exit_code'] not in (0, 1, 2)
    stats = owner.stats()
    assert stats['session_calls'] == 1
    assert stats['session_fresh_calls'] == 1
    assert stats['bypasses'] == 0  # admission refused before any unit lookup


def test_context_diagnostics_stay_outside_public_payload():
    from gnd import api
    from tests.test_incremental_sessions import same_payload

    m, p = next(tool.localized_inputs())
    owner = api.EvaluationSession(m)
    same_payload(owner.check(p), api.check(m, p))
    stats = owner.stats()
    assert stats['extension_context_calls'] > 0
    assert stats['constraint_calls'] > 0
    assert stats['constraint_fallbacks'] >= 0
    assert stats['extension_context_fallbacks'] >= 0


@pytest.mark.parametrize('route', ['callable', 'string'])
def test_unknown_registry_hook_with_unclassified_global_dependency_is_fresh(tmp_path, monkeypatch, route):
    from dataclasses import replace

    import test_public_branch_runtime as corpus

    from gnd import api, semantic_spec
    from gnd.constraint_families import FAMILIES
    from tests.test_incremental_sessions import same_payload

    m, p = corpus._build('P2-039', tmp_path)
    monkeypatch.setitem(globals(), '_test_hook_state', 1)

    def evaluator(constraint, snapshot):
        return _test_hook_state, []  # noqa: F821 -- installed global is the unclassified dependency

    # IK4 gave frequency a production fast path; disable it so both routes still
    # reach the pure evaluator this test replaces.
    monkeypatch.setitem(FAMILIES, 'frequency', replace(FAMILIES['frequency'], production=None))
    if route == 'callable':
        monkeypatch.setitem(FAMILIES, 'frequency', replace(FAMILIES['frequency'], evaluator=evaluator))
    else:
        monkeypatch.setattr(semantic_spec, '_family_result_frequency', evaluator)
    owner = api.EvaluationSession(m)
    same_payload(owner.check(p), api.check(m, p))
    monkeypatch.setitem(globals(), '_test_hook_state', 0)
    same_payload(owner.check(p), api.check(m, p))


def test_fallback_evaluator_failure_is_not_retried(tmp_path, monkeypatch):
    from dataclasses import replace

    import test_public_branch_runtime as corpus

    from gnd import api
    from gnd.constraint_families import FAMILIES
    from tests.test_incremental_sessions import same_payload

    m, p = corpus._build('P2-039', tmp_path)
    calls = []

    def evaluator(constraint, snapshot):
        calls.append(1)
        if len(calls) == 1:
            raise RuntimeError('first evaluator failure')
        return 1, []

    # IK4 gave frequency a production fast path; disable it so this test still
    # exercises the pure evaluator it replaces.
    monkeypatch.setitem(
        FAMILIES, 'frequency', replace(FAMILIES['frequency'], evaluator=evaluator, production=None)
    )
    expected = api.check(m, p)
    assert expected['exit_code'] == 70 and len(calls) == 1
    calls.clear()
    actual = api.EvaluationSession(m).check(p)
    same_payload(actual, expected)
    assert len(calls) == 1


def test_lookup_denominator_counts_once_even_when_miss_also_bypasses():
    m, _ = next(tool.localized_inputs())
    owner = ReuseState(m, max_rows=0)
    with owner.transaction(m):
        assert owner.reuse('unit', 'cap', (), lambda: 7, rows=1) == 7
    stats = owner.stats()
    assert stats['misses'] == stats['bypasses'] == 1
    assert stats['lookups'] == 1
    assert stats['hits'] + stats['misses'] + stats['bypasses'] > stats['lookups']
