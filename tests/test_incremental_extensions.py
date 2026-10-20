"""IE2 corpus-first differential and actual-work controls."""
from dataclasses import replace

import pytest

from gnd import extensions as ext
from gnd.branches import capture_branches
from gnd.incremental_state import ReuseState
from tests.test_incremental_baseline import tool


def envelope(result):
    return tool.complete_calculation_key(result)


@pytest.mark.parametrize('exact', [False, True])
def test_component_noop_and_independent_work(exact):
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    calculate = ext._evaluate_stratified_extensions if exact else ext._python_extension_calculator
    kwargs = {'exact': True} if exact else {}
    state = ReuseState(m)
    with capture_branches() as expected_branches:
        expected = calculate(m, relations, **kwargs)
    # The profiler also wraps public lookup seams. Keep those policy identities
    # stable for the entire paired replay instead of reinstalling them per call.
    with tool.count_work() as work:
        for attempt in range(2):
            before = work['derivation_body_evaluations']
            with state.transaction(m), capture_branches() as branches:
                actual = calculate(m, relations, **kwargs)
            assert envelope(actual) == envelope(expected)
            assert branches == expected_branches
            if attempt:
                assert work['derivation_body_evaluations'] - before == 0
        altered = dict(relations)
        altered['left'] = replace(relations['left'], rows=(), row_lineage=())
        fresh = calculate(m, altered, **kwargs)
        before = work['derivation_body_evaluations']
        with state.transaction(m):
            actual = calculate(m, altered, **kwargs)
        assert envelope(actual) == envelope(fresh)
        assert state.stats()['hits'] > 0
        assert work['derivation_body_evaluations'] - before < 2


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


def test_negation_blocker_insert_delete():
    from gnd.model import Model
    from gnd.population import load_population
    base, _ = next(tool.localized_inputs())
    document = base.model_dump()
    document['fact_types'][2]['derivation_rule']['negate'] = [
        {'fact_type': 'right', 'bind': {'item': '$i'}}]
    m = Model.model_validate(document)
    p = load_population(tool.FIXTURE / 'initial.pop.json', model=m)
    relations = ext.base_relations(m, p)
    blocked = dict(relations, right=replace(relations['right'], rows=(('alpha',),), row_lineage=((),)))
    state = ReuseState(m)
    for current, expected_rows in [(relations, (('alpha',), ('beta',))),
                                   (blocked, (('beta',),)), (relations, (('alpha',), ('beta',)))]:
        fresh = ext._python_extension_calculator(m, current)
        with state.transaction(m):
            actual = ext._python_extension_calculator(m, current)
        assert envelope(actual) == envelope(fresh)
        assert actual.extensions['left_copy'].rows == expected_rows


def test_reordered_base_origins_do_not_reuse_old_lineage():
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    changed = dict(relations, left=replace(relations['left'], rows=relations['left'].rows[::-1],
                                         row_lineage=relations['left'].row_lineage))
    outputs = []
    for current in [relations, changed]:
        fresh = ext._python_extension_calculator(m, current)
        with state.transaction(m):
            actual = ext._python_extension_calculator(m, current)
        assert envelope(actual) == envelope(fresh)
        outputs.append(actual.extensions['left_copy'])
    assert outputs[0].rows == outputs[1].rows
    assert outputs[0].row_lineage != outputs[1].row_lineage
    assert state.stats()['misses'] == 3


def test_helper_policy_mutation_and_foreign_nested_model(monkeypatch):
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    with state.transaction(m):
        ext._python_extension_calculator(m, relations)
    original = ext._clause_bindings
    calls = []

    def changed(*args, **kwargs):
        calls.append(1)
        return original(*args, **kwargs)

    monkeypatch.setattr(ext, '_clause_bindings', changed)
    with state.transaction(m):
        ext._python_extension_calculator(m, relations)
    assert len(calls) == 2
    other, population = next(tool.localized_inputs())
    with state.transaction(m):
        expected = ext._python_extension_calculator(other, ext.base_relations(other, population))
        assert len(expected.extensions) == 2
        assert not state._candidate


def test_witness_and_partial_callbacks_fall_back():
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)

    class Witness:
        def charge(self, *args):
            pass

        def row(self, *args):
            pass

    token = ext.WITNESS_TRACE.set(Witness())
    try:
        with state.transaction(m), tool.count_work() as counts:
            ext._evaluate_stratified_extensions(m, relations, exact=True)
        assert counts['derivation_body_evaluations'] > 0 and state.stats()['entries'] == 0
    finally:
        ext.WITNESS_TRACE.reset(token)
    opaque = dict(relations, left=replace(relations['left'], rows=(({'$opaque': 'unknown'},),),
                                         row_lineage=((),)))
    expected = ext._evaluate_stratified_extensions(m, opaque, exact=True)
    for _ in range(2):
        with state.transaction(m):
            actual = ext._evaluate_stratified_extensions(m, opaque, exact=True)
        assert envelope(actual) == envelope(expected)
        assert state.stats()['entries'] == 0


@pytest.mark.parametrize('exact', [False, True])
def test_stratified_unavailable_origin_propagates_even_without_public_metadata(exact):
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.ROOT / 'tests/fixtures/v62-phase3'
    m = load_model(root / 'models/exact-terms.orm.yaml')
    p = load_population(root / 'populations/term-input.pop.yaml', model=m)
    relations = ext.base_relations(m, p)
    fresh = ext._evaluate_stratified_extensions(m, relations, exact=exact)
    state = ReuseState(m)
    for _ in range(2):
        with state.transaction(m):
            actual = ext._evaluate_stratified_extensions(m, relations, exact=exact)
        assert envelope(actual) == envelope(fresh)


@pytest.mark.parametrize(('folder', 'model_name', 'pop_name'), [
    ('v70-phase4', 'recursive.orm.yaml', 'recursive.pop.json'),
    ('pyrel-rules-derivations', 'mutual.orm.json', 'mutual-exact.population.json'),
])
def test_recursive_alternate_support_deletion_and_complete_removal(folder, model_name, pop_name):
    from gnd.model import load_model
    from gnd.population import load_population
    root = tool.ROOT / 'tests/fixtures' / folder
    m = load_model(root / model_name)
    p = load_population(root / pop_name, model=m)
    relations = ext.base_relations(m, p)
    edge = relations['edge']
    state = ReuseState(m)
    if folder == 'v70-phase4':
        edge = replace(edge, rows=edge.rows + (('A', 'C'),),
                       row_lineage=edge.row_lineage + ((('facts', 'edge', 2),),))
        relations = dict(relations, edge=edge)
    altered = dict(relations, edge=replace(edge, rows=edge.rows[1:], row_lineage=edge.row_lineage[1:]))
    empty = dict(relations, edge=replace(edge, rows=(), row_lineage=()))
    for current in [relations, relations, altered, empty, relations]:
        fresh = ext._evaluate_stratified_extensions(m, current, exact=True)
        with state.transaction(m):
            actual = ext._evaluate_stratified_extensions(m, current, exact=True)
        assert envelope(actual) == envelope(fresh)
        if current is empty:
            assert all(not rel.rows for rel in actual.extensions.values())
        if folder == 'v70-phase4' and current is altered:
            assert ('A', 'C') in actual.extensions['reaches'].rows
            assert ('A', 'B') not in actual.extensions['reaches'].rows
    assert state.stats()['hits'] > 0


def test_late_component_failure_does_not_publish_candidate(monkeypatch):
    m, p = next(tool.localized_inputs())
    relations = ext.base_relations(m, p)
    state = ReuseState(m)
    with state.transaction(m):
        ext._python_extension_calculator(m, relations)
    before = state.stats()['generation']
    original = ext._clause_bindings

    def fail_right(rule, *args, **kwargs):
        if rule['body'][0]['fact_type'] == 'right':
            raise KeyboardInterrupt
        return original(rule, *args, **kwargs)

    with monkeypatch.context() as patch:
        patch.setattr(ext, '_clause_bindings', fail_right)
        with pytest.raises(KeyboardInterrupt), state.transaction(m):
            ext._python_extension_calculator(m, relations)
    assert state.stats()['generation'] == before
    hits = state.stats()['hits']
    with state.transaction(m):
        ext._python_extension_calculator(m, relations)
    assert state.stats()['hits'] == hits + 2
