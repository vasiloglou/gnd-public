"""IE2 corpus-first differential and actual-work controls."""
from dataclasses import replace

import pytest

from gnd import extensions as ext
from gnd.branches import capture_branches
from gnd.incremental_state import ReuseState
from tests.test_incremental_baseline import tool


def envelope(result):
    return tool.calculation_envelope(result.extensions), tool.packed(result.counted_operations)


@pytest.mark.parametrize('exact', [False, True])
def test_component_noop_and_independent_work(exact):
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    calculate = ext._evaluate_stratified_extensions if exact else ext._python_extension_calculator
    kwargs = {'exact': True} if exact else {}
    state = ReuseState(m)
    with capture_branches() as expected_branches:
        expected = calculate(m, relations, **kwargs)
    for attempt in range(2):
        with state.transaction(m), tool.count_work() as work, capture_branches() as branches:
            actual = calculate(m, relations, **kwargs)
        assert envelope(actual) == envelope(expected)
        assert branches == expected_branches
        if attempt:
            assert work['derivation_body_evaluations'] == 0
    altered = dict(relations)
    altered['left'] = replace(relations['left'], rows=(), row_lineage=())
    fresh = calculate(m, altered, **kwargs)
    with state.transaction(m), tool.count_work() as work:
        actual = calculate(m, altered, **kwargs)
    assert envelope(actual) == envelope(fresh)
    # left_copy and its transitive head may execute; right_copy must be reused.
    assert state.stats()['hits'] > 0
    assert work['derivation_body_evaluations'] < 6


def test_all_local_mutations_have_complete_parity():
    state = None
    for m, p in tool.localized_inputs():
        if state is None:
            state = ReuseState(m)
        relations = ext.base_relations(m, p)
        expected = ext._python_extension_calculator(m, relations)
        with state.transaction(m):
            actual = ext._python_extension_calculator(m, relations)
        assert envelope(actual) == envelope(expected)


def test_exact_recursive_deletion_and_tamper():
    from gnd.model import load_model
    from gnd.population import load_population
    # Use the repository's bounded recursive acceptance fixture.
    root = tool.ROOT / 'tests/fixtures/v70-phase4'
    m = load_model(root / 'recursive.orm.yaml')
    p = load_population(root / 'recursive.pop.json', model=m)
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    for modified in [relations, relations, dict(relations, edge=replace(relations['edge'], rows=(), row_lineage=()))]:
        fresh = ext._evaluate_stratified_extensions(m, modified, exact=True)
        with state.transaction(m):
            actual = ext._evaluate_stratified_extensions(m, modified, exact=True)
        assert envelope(actual) == envelope(fresh)
        actual.extensions.clear()
    assert state.stats()['hits'] > 0


@pytest.mark.parametrize(('model_name', 'population_name'), [
    ('v62-phase3/models/exact-terms.orm.yaml', 'v62-phase3/populations/term-input.pop.yaml'),
    ('v62-phase4/models/aggregates.orm.yaml', 'v62-phase4/populations/aggregate-input.pop.yaml'),
])
def test_exact_unavailability_and_aggregate_dirty_inputs(model_name, population_name):
    from gnd.model import load_model
    from gnd.population import load_population
    m = load_model(tool.ROOT / 'tests/fixtures' / model_name)
    p = load_population(tool.ROOT / 'tests/fixtures' / population_name, model=m)
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    base = next(name for name in relations if name not in {
        str(row['id']) for row in m.fact_types if isinstance(row.get('derivation_rule'), dict)
    })
    empty = dict(relations, **{base: replace(relations[base], rows=(), row_lineage=())})
    for current in [relations, relations, empty, relations]:
        with capture_branches() as expected_branches:
            fresh = ext._exact_extension_calculator(m, current)
        with state.transaction(m), capture_branches() as branches:
            actual = ext._exact_extension_calculator(m, current)
        assert envelope(actual) == envelope(fresh)
        assert branches == expected_branches
    assert state.stats()['hits'] > 0


def test_tiny_bound_and_witness_fallback_are_semantic():
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    expected = ext._python_extension_calculator(m, relations)
    state = ReuseState(m, max_bytes=1)
    for _ in range(2):
        with state.transaction(m), tool.count_work() as counts:
            actual = ext._python_extension_calculator(m, relations)
        assert envelope(actual) == envelope(expected)
        assert counts['derivation_body_evaluations'] > 0
    assert state.stats()['entries'] == 0
