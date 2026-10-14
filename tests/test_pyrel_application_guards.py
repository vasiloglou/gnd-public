"""PA4 source-bound application guard envelopes, distinct from process exits."""
import inspect
import json

import pytest
from test_pyrel_application_publication import application, run_simulated, simulated_child


@pytest.mark.parametrize('damage', [None, 'binding', 'schema', 'code', 'kind', 'reason', 'long-reason',
                                   'reason-type', 'mixed', 'extra', 'default'])
def test_source_bound_guard_refusal_has_closed_interface(monkeypatch, tmp_path, damage):
    module = application()
    assert 'allowed_guard_kinds' in inspect.signature(module.execute_application).parameters, 'guard-envelope interface is absent'
    def envelope(proposal):
        refusal = {'schema_version': 1, 'binding': proposal['binding'],
                   'guard_refusal': {'exit_code': 1, 'kind': 'unknown-expense', 'reason': 'no submission fact'}}
        if damage == 'binding':
            refusal['binding'] = {}
        elif damage == 'schema':
            refusal['schema_version'] = True
        elif damage == 'code':
            refusal['guard_refusal']['exit_code'] = True
        elif damage == 'kind':
            refusal['guard_refusal']['kind'] = 'invented'
        elif damage == 'reason':
            refusal['guard_refusal']['reason'] = ''
        elif damage == 'long-reason':
            refusal['guard_refusal']['reason'] = 'x' * 301
        elif damage == 'reason-type':
            refusal['guard_refusal']['reason'] = 1
        elif damage == 'mixed':
            refusal['candidate'] = proposal['candidate']
        elif damage == 'extra':
            refusal['guard_refusal']['invented'] = True
        return json.dumps(refusal).encode()
    simulated_child(module, monkeypatch, proposal_damage=envelope)
    _, output, result = run_simulated(module, tmp_path, allowed_guard_kinds=() if damage == 'default' else ('unknown-expense',))
    assert not result['accepted'] and not result['published'] and not output.exists() and result['policy'] is None
    if damage is None:
        assert result['exit_code'] == 1 and result['application_refusal']['kind'] == 'unknown-expense', result
        assert result['application_refusal']['reason'] == 'no submission fact'
    else:
        assert result['exit_code'] == 3, result


@pytest.mark.parametrize('kinds', [('duplicate', 'duplicate'), ('UPPER',), tuple('k'+str(i) for i in range(17)), 'unknown-expense'])
def test_invalid_guard_declarations_refuse_before_child(monkeypatch, tmp_path, kinds):
    module = application()
    called = []; monkeypatch.setattr(module, '_child', lambda *args: called.append(args))
    _, output, result = run_simulated(module, tmp_path, allowed_guard_kinds=kinds)
    assert result['exit_code'] == 3 and not output.exists() and called == []
    assert 'guard kinds must be distinct bounded declarations' in result['reason']


def test_crashed_query_cannot_classify_leftover_guard(monkeypatch, tmp_path):
    from types import SimpleNamespace

    module = application()
    simulated_child(module, monkeypatch, proposal_damage=lambda p: json.dumps(
        {'schema_version': 1, 'binding': p['binding'],
         'guard_refusal': {'exit_code': 1, 'kind': 'unknown-expense', 'reason': 'no submission fact'}}).encode())
    original = module._child
    def crash(argv, home):
        original(argv, home)
        return SimpleNamespace(return_code=1, stderr=b'query crash')
    monkeypatch.setattr(module, '_child', crash)
    _, output, result = run_simulated(module, tmp_path, allowed_guard_kinds=('unknown-expense',))
    assert result['exit_code'] == 70 and not output.exists() and result['policy'] is None
    assert 'application_refusal' not in result
