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
    assert next(q.iter_constraints())[1]['role'] == 'x'
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


def test_non_string_keys_do_not_alias_string_key_cache():
    integer_key = built()
    integer_key.source[1] = 'value'
    string_key = built()
    string_key.source['1'] = 'value'
    assert index(integer_key) is not index(string_key)
    assert index(integer_key).digest is None


def test_legacy_non_model_query_shapes_keep_results():
    from types import SimpleNamespace

    from gnd import universe
    raw = SimpleNamespace(fact_types=[{'id': 'F', 'roles': [{'role_name': 'x', 'object_type': 'T'}]}])
    assert universe.fact_type_by_id(raw, 'F') is raw.fact_types[0]
    assert universe.role_object_type(raw, 'F', 'x') == 'T'


def test_range_public_name_keeps_old_callable_and_answers():
    from gnd.synth import value_domain
    assert value_domain.in_range is value_domain._in_range
    assert value_domain.in_range.__name__ == '_in_range'
    assert value_domain.in_range(3, {'min': 3, 'max': 3})
    assert not value_domain.in_range(3, {'min': 3, 'min_inclusive': False})
    assert not value_domain.in_range('x', {'min': 3})


def test_shared_maps_keep_non_model_and_malformed_model_shapes():
    from types import SimpleNamespace

    from gnd import popvalidate, universe
    from gnd.synth import assemble, poolfile
    raw = SimpleNamespace(object_types=[{'id': 'T'}],
                          fact_types=[{'id': 'F', 'roles': [{'role_name': 'x', 'object_type': 'T'}]}])
    for helper in (popvalidate._role_object_types, assemble._role_object):
        assert helper(raw) == {'F': {'x': 'T'}}
    for helper in (popvalidate._object_types_by_id, assemble._object_types_by_id,
                   poolfile._object_types_by_id):
        assert helper(raw) == {'T': {'id': 'T'}}
        malformed = Model.model_construct(version=1, object_types=[None], fact_types=[])
        with pytest.raises(AttributeError):
            helper(malformed)
    assert universe.scope_fact_types({'object_type': []}, 'value', built(), None) == []


@pytest.mark.parametrize('site', ['popvalidate', 'assemble', 'poolfile'])
def test_malformed_model_object_map_retains_predecessor_error(site):
    from gnd import popvalidate
    from gnd.synth import assemble, poolfile
    helper = {'popvalidate': popvalidate._object_types_by_id,
              'assemble': assemble._object_types_by_id,
              'poolfile': poolfile._object_types_by_id}[site]
    malformed = Model.model_construct(version=1, object_types=[None], fact_types=[])
    with pytest.raises(AttributeError):
        helper(malformed)


def test_raw_scope_unhashable_target_retains_empty_result():
    from gnd import universe
    assert universe.scope_fact_types({'object_type': []}, 'value', built(), None) == []


def test_historical_query_aliases_keep_original_row_identity():
    from gnd import popvalidate, universe
    from gnd.synth import assemble, poolfile
    model = built()
    assert universe.fact_type_by_id(model, 'F') is model.fact_types[0]
    for helper in (popvalidate._object_types_by_id, assemble._object_types_by_id,
                   poolfile._object_types_by_id):
        assert helper(model)['Code'] is model.object_types[0]
