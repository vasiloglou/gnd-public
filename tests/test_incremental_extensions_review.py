"""IE2 independent-review reproductions written before repairs."""
from dataclasses import replace
from types import MappingProxyType

import pytest

from gnd import extensions as ext
from gnd import terms
from gnd.incremental_state import ReuseState
from gnd.model import load_model
from gnd.population import load_population
from tests.test_incremental_extensions import envelope, tool


def exact_inputs(*, clean=False):
    root = tool.ROOT / 'tests/fixtures/v62-phase3'
    m = load_model(root / 'models/exact-terms.orm.yaml')
    p = load_population(root / ('populations/term-clean.pop.yaml' if clean else 'populations/term-input.pop.yaml'), model=m)
    return m, ext.base_relations(m, p)


def test_defining_helper_mutation_cannot_reuse_old_exact_result(monkeypatch):
    m, relations = exact_inputs()
    state = ReuseState(m)
    with state.transaction(m):
        ext._exact_extension_calculator(m, relations)
    monkeypatch.setattr(terms, '_too_wide', lambda *args: True)
    expected = ext._exact_extension_calculator(m, relations)
    with state.transaction(m):
        actual = ext._exact_extension_calculator(m, relations)
    assert envelope(actual) == envelope(expected)


@pytest.mark.parametrize('exact', [False, True])
def test_opaque_dictionary_subclass_preserves_possible_rows(exact):
    class Opaque(dict):
        pass

    m, p = next(tool.localized_inputs())
    relations = dict(ext.base_relations(m, p))
    relations['left'] = replace(relations['left'], rows=((Opaque({'$opaque': 'unknown'}),),),
                                row_lineage=((),))
    expected = ext._evaluate_stratified_extensions(m, relations, exact=exact)
    state = ReuseState(m)
    with state.transaction(m):
        actual = ext._evaluate_stratified_extensions(m, relations, exact=exact)
    assert envelope(actual) == envelope(expected)


def test_unrelated_malformed_relation_still_refuses_on_warm_hit():
    m, relations = exact_inputs(clean=True)
    state = ReuseState(m)
    with state.transaction(m):
        ext._exact_extension_calculator(m, relations)
    malformed = dict(relations, unused=replace(relations['ticket_status'],
                                                    fact_type='unused',
                                                    rows=(('one', 'two', 'three'),),
                                                    row_lineage=((),)))
    with pytest.raises(ValueError):
        ext._exact_extension_calculator(m, malformed)
    with pytest.raises(ValueError), state.transaction(m):
        ext._exact_extension_calculator(m, malformed)


@pytest.mark.parametrize('field', ['roles', 'identity_codec_version', 'fact_type', 'bool-int'])
def test_differential_oracle_discriminates_complete_typed_metadata(field):
    m, p = next(tool.localized_inputs())
    first = ext._python_extension_calculator(m, ext.base_relations(m, p))
    values = dict(first.extensions)
    relation = values['left_copy']
    if field == 'bool-int':
        first = replace(first, extensions=MappingProxyType(dict(values,
                        left_copy=replace(relation, rows=((True,),)))))
        relation = replace(relation, rows=((1,),))
    else:
        relation = replace(relation, **{field: {'roles': (('renamed', 'Integer'),),
                           'identity_codec_version': 'other', 'fact_type': 'other'}[field]})
    second = replace(first, extensions=MappingProxyType(dict(values, left_copy=relation)))
    assert envelope(first) != envelope(second)


def test_live_term_default_limits_are_part_of_policy(monkeypatch):
    m, relations = exact_inputs(clean=True)
    state = ReuseState(m)
    with state.transaction(m):
        ext._exact_extension_calculator(m, relations)
    modified = dict(terms.evaluate_term.__kwdefaults__)
    modified['limits'] = replace(terms.DEFAULT_LIMITS, max_value_bits=1)
    monkeypatch.setattr(terms.evaluate_term, '__kwdefaults__', modified)
    fresh = ext._exact_extension_calculator(m, relations)
    with state.transaction(m):
        actual = ext._exact_extension_calculator(m, relations)
    assert envelope(actual) == envelope(fresh)


def test_object_map_lookup_policy_cannot_reuse_stale_roles(monkeypatch):
    from gnd.model_index import ModelIndex
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    with state.transaction(m):
        ext._python_extension_calculator(m, relations)
    monkeypatch.setattr(ModelIndex, 'object_map', staticmethod(lambda model: {}))
    fresh = ext._python_extension_calculator(m, relations)
    with state.transaction(m):
        actual = ext._python_extension_calculator(m, relations)
    assert envelope(actual) == envelope(fresh)


def test_reuse_only_index_failure_preserves_ordinary_calculation(monkeypatch):
    from gnd.model_index import ModelIndex
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)

    def broken(cls, model):
        raise RuntimeError('injected reuse-only index failure')

    monkeypatch.setattr(ModelIndex, 'for_model', classmethod(broken))
    fresh = ext._python_extension_calculator(m, relations)
    with state.transaction(m):
        actual = ext._python_extension_calculator(m, relations)
    assert envelope(actual) == envelope(fresh)


def test_reuse_only_classifier_failure_preserves_ordinary_calculation(monkeypatch):
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)

    def broken(*args):
        raise RuntimeError('injected reuse-only classification failure')

    monkeypatch.setattr(ext, 'derivation_classifications', broken)
    fresh = ext._python_extension_calculator(m, relations)
    with state.transaction(m):
        actual = ext._python_extension_calculator(m, relations)
    assert envelope(actual) == envelope(fresh)
