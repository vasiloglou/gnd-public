"""RF6 index: freshness, detached views and historical query semantics."""
from __future__ import annotations

import time

import pytest

from gnd.documents import Model


def built():
    return Model(version=1, object_types=[
        {'id': 'Code', 'kind': 'value', 'primitive': 'String'},
        {'id': 'Base', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'Code'}},
        {'id': 'Child', 'kind': 'entity', 'subtype_of': ['Base'], 'inherits_reference': 'yes'},
    ], fact_types=[{'id': 'F', 'roles': [{'role_name': 'x', 'object_type': 'Child'}],
                    'constraints': [{'type': 'mandatory', 'role': 'x'}]}],
       constraints=[{'type': 'textual', 'expression': 'hello'}])


def index(model):
    from gnd.model_index import ModelIndex
    return ModelIndex.for_model(model)


def test_lookup_closure_variants_and_missing():
    q = index(built())
    assert q.fact_type('F')['id'] == 'F'
    assert q.fact_type('absent') is None
    assert q.object_type('Code')['primitive'] == 'String'
    assert q.object_type('absent') is None
    assert q.role_object_type('F', 'x') == 'Child'
    assert q.role_object_type('F', 'absent') is None
    assert q.role_object_type('absent', 'x') is None
    assert q.supertype_closure('Child') == frozenset({'Base'})
    assert q.primitive('Child', variant='truthy') == 'String'
    assert q.primitive('Child', variant='strict') is None
    with pytest.raises(ValueError, match='variant'):
        q.primitive('Code', variant='bad')


def test_cache_equal_models_detached_views_and_canonical_refs():
    m = built()
    q = index(m)
    assert index(m) is q
    assert index(built()) is q
    q.fact_type('F')['roles'].clear()
    q.object_types_by_id()['Code']['primitive'] = 'Integer'
    rows = list(q.iter_constraints())
    assert [row[0] for row in rows] == ['fact_types[F].constraints[0]', 'constraints[0]']
    rows[0][1]['role'] = 'broken'
    assert q.role_object_type('F', 'x') == 'Child'
    assert q.primitive('Code', variant='strict') == 'String'
    assert list(q.iter_constraints())[0][1]['role'] == 'x'
    assert m.fact_types[0]['roles']
    with pytest.raises((AttributeError, TypeError)):
        q.digest = 'changed'


@pytest.mark.parametrize('section', ['fact_types', 'object_types', 'constraints', 'operations',
                                      'reference_populations', 'source'])
def test_all_query_inputs_mutated_never_serve_stale(section):
    m = built()
    old = index(m)
    value = getattr(m, section)
    if isinstance(value, list):
        value.append({'id': 'added', 'type': 'textual', 'expression': 'new'})
    else:
        value['changed'] = 'new'
    current = index(m)
    assert current is not old
    assert current.digest != old.digest
    if section == 'fact_types':
        assert current.fact_type('added') is not None
        assert old.fact_type('added') is None


def test_cycles_and_duplicate_predecessor_lookup():
    m = built()
    m.object_types.extend([{'id': 'A', 'kind': 'entity', 'subtype_of': ['B'], 'inherits_reference': True},
                           {'id': 'B', 'kind': 'entity', 'subtype_of': ['A'], 'inherits_reference': True}])
    m.fact_types.append({'id': 'F', 'roles': [{'role_name': 'y', 'object_type': 'Code'}]})
    q = index(m)
    assert q.role_object_type('F', 'x') == 'Child'
    assert q.role_object_type('F', 'y') is None
    assert q.supertype_closure('A') == frozenset({'A', 'B'})
    assert q.primitive('A', variant='strict') is None


def test_cache_bounded_and_noncanonical_bypass():
    from gnd.model_index import cache_info
    m = built()
    m.source['nonfinite'] = float('nan')
    assert index(m) is not index(m)
    assert index(m).role_object_type('F', 'x') == 'Child'
    for i in range(40):
        m = built()
        m.source['sequence'] = i
        index(m)
    assert cache_info()['size'] <= 32


def test_large_index_work_is_bounded():
    m = built()
    m.fact_types.extend({'id': f'F{i}', 'roles': [{'role_name': 'x', 'object_type': 'Code'}]}
                        for i in range(5000))
    started = time.monotonic()
    q = index(m)
    assert q.role_object_type('F4999', 'x') == 'Code'
    assert len(list(q.iter_constraints())) == 2
    assert time.monotonic() - started < 5
