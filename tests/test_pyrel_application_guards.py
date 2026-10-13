"""PA4 source-bound application guard envelopes, distinct from process exits."""
import inspect
import json

import pytest
from test_pyrel_application_publication import application, run_simulated, simulated_child


@pytest.mark.parametrize('damage', [None, 'binding', 'schema', 'code', 'kind', 'reason', 'mixed', 'extra', 'default'])
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
