from __future__ import annotations

import copy
from pathlib import Path

import pytest

from gnd.extract import projection as projection_module
from gnd.extract.projection import ProjectionGateError, audit_allowlist, project
from gnd.model import load_model

FIXTURES = Path(__file__).parent / 'fixtures'
FULL_VOCAB = FIXTURES / 'models' / 'full_vocabulary.orm.yaml'

def _fact_items(schema: dict) -> dict:
    return schema['properties']['facts']['properties']['employee_has_name']['items']

def _fact_array(schema: dict) -> dict:
    return schema['properties']['facts']['properties']['employee_has_name']
_KEYWORD_CASES = [('minimum', lambda s: _fact_items(s)['properties']['employee'].__setitem__('minimum', 0)), ('uniqueItems', lambda s: _fact_array(s).__setitem__('uniqueItems', True)), ('pattern', lambda s: s['$defs']['scalar']['anyOf'][0].__setitem__('pattern', '^x')), ('minItems', lambda s: _fact_array(s).__setitem__('minItems', 1)), ('maxLength', lambda s: s['$defs']['scalar']['anyOf'][0].__setitem__('maxLength', 5)), ('multipleOf', lambda s: _fact_items(s)['properties']['employee'].__setitem__('multipleOf', 2)), ('enum', lambda s: _fact_items(s)['properties']['name'].__setitem__('enum', ['a'])), ('const', lambda s: _fact_items(s)['properties']['employee'].__setitem__('const', 1)), ('x-vendor-hint', lambda s: s.__setitem__('x-vendor-hint', True))]

@pytest.mark.parametrize(('keyword', 'mutate'), _KEYWORD_CASES, ids=[k for k, _ in _KEYWORD_CASES])
def test_projection_allowlist_fails_closed_on_unlisted_keyword(keyword: str, mutate, monkeypatch) -> None:
    model = load_model(str(FULL_VOCAB))
    schema = project(model)
    mutate(schema)
    violations = audit_allowlist(schema)
    assert any((v[1] == keyword for v in violations)), 'Assertion did not hold.'
    monkeypatch.setattr(projection_module, '_build_projection', lambda _model: schema)
    with pytest.raises(ProjectionGateError, match=keyword.replace('$', '\\$')):
        project(model)

def test_projection_required_is_role_arity_only() -> None:
    model = load_model(str(FULL_VOCAB))
    schema = project(model)
    assert audit_allowlist(schema) == []
    subset = copy.deepcopy(schema)
    _fact_items(subset)['required'] = ['employee']
    assert any((v[1] == 'required' for v in audit_allowlist(subset))), 'Assertion did not hold.'
    superset = copy.deepcopy(schema)
    _fact_items(superset)['required'] = ['employee', 'name', 'phantom']
    assert any((v[1] == 'required' for v in audit_allowlist(superset))), 'Assertion did not hold.'
