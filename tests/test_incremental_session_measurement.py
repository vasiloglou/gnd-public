"""IE5 measurement preparation: balanced modes and complete typed oracle."""
from tests.test_incremental_baseline import tool


def test_session_timing_uses_balanced_uninstrumented_distinct_modes(monkeypatch):
    reached = []

    def replay(workload, *, receipts, incremental=False):
        reached.append((receipts, incremental))
        return []

    monkeypatch.setattr(tool, 'replay_full', replay)
    result = tool.measure_session_modes('localized', repeat=3)
    assert result['order'] == ['ABC', 'BCA', 'CAB']
    assert result['positionally_balanced']
    assert all(len(rows) == 3 for rows in result['samples'].values())
    assert reached[3:] == [(False, False), (True, False), (True, True),
                           (True, False), (True, True), (False, False),
                           (True, True), (False, False), (True, False)]


def test_complete_calculation_key_rejects_typed_metadata_mutation():
    from dataclasses import replace

    from gnd import extensions

    m, p = next(tool.localized_inputs())
    original = extensions._python_extension_calculator(m, extensions.base_relations(m, p))
    key = tool.complete_calculation_key(original)
    relation = original.extensions['left_copy']
    changed = dict(original.extensions)
    changed['left_copy'] = replace(relation, roles=tuple(reversed(relation.roles)) + ('wrong',))
    assert key != tool.complete_calculation_key(replace(original, extensions=changed))


def test_mode_comparison_rejects_corrupted_semantic_surfaces():
    from copy import deepcopy

    import pytest
    from measure_evaluation_sessions import compare_modes

    row = {'payload': 'typed-payload', 'exit': 2, 'branches': ['registered'],
           'calculations': ['typed-complete-envelope']}
    modes = {mode: {'calls': [deepcopy(row)]} for mode in 'ABC'}
    compare_modes(modes)
    for key, value in [('payload', 'wrong'), ('exit', 1), ('branches', []),
                       ('calculations', ['wrong'])]:
        corrupted = deepcopy(modes)
        corrupted['C']['calls'][0][key] = value
        with pytest.raises(ValueError):
            compare_modes(corrupted)


def test_observed_calculations_preserve_order_and_multiplicity(monkeypatch):
    from contextlib import contextmanager

    @contextmanager
    def calculations():
        yield ['first', 'first', 'second']

    monkeypatch.setattr(tool, 'capture_complete', calculations)
    rows = []
    token = tool.COMPLETE_CALL_SINK.set(rows)
    try:
        tool.public_call(lambda: {'exit_code': 0})
    finally:
        tool.COMPLETE_CALL_SINK.reset(token)
    assert rows[0]['calculations'] == ['first', 'first', 'second']


def test_all_matching_errors_cannot_satisfy_frozen_workload():
    from copy import deepcopy

    import pytest
    from measure_evaluation_sessions import compare_modes

    row = {'payload': 'same-error', 'exit': 70, 'branches': ['registered'],
           'calculations': ['same-envelope']}
    modes = {mode: {'calls': [deepcopy(row) for _ in range(3)]} for mode in 'ABC'}
    # The original comparator accepted these three common failures. The
    # required workload-aware entry point must reject them.
    with pytest.raises(ValueError):
        compare_modes(modes)


def test_session_timing_refuses_profiled_measurements(monkeypatch):
    import pytest

    monkeypatch.setattr(tool.sys, 'getprofile', lambda: object())
    with pytest.raises(ValueError, match='instrument'):
        tool.measure_session_modes('localized', repeat=3)


def test_complete_observer_uses_one_outer_boundary_including_cached_returns():
    from gnd import extensions
    from gnd.extension_preparation import calculation_scope
    from gnd.incremental_state import ReuseState
    from gnd.model import load_model
    from gnd.population import load_population

    root = tool.ROOT / 'tests/fixtures/v70-phase4'
    model = load_model(root / 'recursive.orm.yaml')
    population = load_population(root / 'recursive.pop.json', model=model)
    relations = extensions.base_relations(model, population)
    with calculation_scope(model, population), tool.capture_complete() as full:
        for _ in range(2):
            extensions._exact_extension_calculator(model, relations)
    owner = ReuseState(model)
    with owner.transaction(model), calculation_scope(model, population), tool.capture_complete() as reused:
        for _ in range(2):
            extensions._exact_extension_calculator(model, relations)
    assert len(full) == len(reused) == 2
    assert full == reused


def test_ordered_trace_comparison_rejects_delete_duplicate_permutation():
    from copy import deepcopy

    import pytest
    from measure_evaluation_sessions import compare_modes

    row = {'payload': 'same', 'exit': 2, 'branches': ['registered'],
           'calculations': ['first', 'first', 'second']}
    modes = {mode: {'calls': [deepcopy(row) for _ in range(13)]} for mode in 'ABC'}
    for changed in (['first', 'second'], ['first', 'first', 'second', 'second'],
                    ['second', 'first', 'first']):
        mutant = deepcopy(modes)
        mutant['C']['calls'][0]['calculations'] = changed
        with pytest.raises(ValueError):
            compare_modes(mutant)
