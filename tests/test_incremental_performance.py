"""IE6 bookkeeping controls; reduced work cannot relax existing cache safety."""
from dataclasses import dataclass
from types import MappingProxyType

import pytest

from gnd import incremental_state as state
from gnd.incremental_state import ReuseState
from tests.test_incremental_state import model


def _helper():
    return [1]


def _large_policy():
    return tuple((f'helper-{index}', _helper) for index in range(160))


def test_prepared_policy_tree_is_measured_once_for_many_misses(monkeypatch):
    m = model()
    owner = ReuseState(m)
    visited = []
    original = state._children

    def children(value):
        visited.append(value)
        return original(value)

    monkeypatch.setattr(state, '_children', children)
    with owner.transaction(m):
        policy = owner.prepare_policy(_large_policy())
        for index in range(12):
            assert owner.reuse('work', index, (), _helper, policy=policy) == [1]
        for snapshot in ((), ('dirty',), ('dirty',)):
            for index in range(12):
                assert owner.reuse('work', index, snapshot, _helper, policy=policy) == [1]
    # The exact normalized policy root was already bounded during preparation.
    assert sum(item is policy.key for item in visited) == 1
    assert _policy_pair_visits(visited) == 160
    assert owner.stats()['misses'] == 24
    assert owner.stats()['hits'] == 24
    assert owner.stats()['entries'] == 12


def test_builtin_size_walk_skips_dataclass_introspection(monkeypatch):
    original = state.dataclasses.is_dataclass
    inspected = []

    def observed(value):
        inspected.append(type(value))
        return original(value)

    monkeypatch.setattr(state.dataclasses, 'is_dataclass', observed)
    assert state._measure({'a': [1, True, None, 2.0], 'b': (2, 'x')}, 10**6)
    assert not inspected


def test_cached_footprint_charges_full_policy_and_private_values():
    m = model()
    owner = ReuseState(m)
    with owner.transaction(m):
        policy = owner.prepare_policy(_large_policy())
        for index in range(3):
            owner.reuse('unit', index, ('input',), lambda: [[n] for n in range(20)], policy=policy)
    for key, entry in owner._entries.items():
        actual = state._measure((key, entry.signature, entry.value, entry.branches), 10**8)
        assert actual is not None
        assert entry.size >= actual + state.ENTRY_METADATA_BYTES
    assert owner.stats()['bytes'] >= sum(entry.size for entry in owner._entries.values())


@pytest.mark.parametrize('bound,value', [('MAX_NODES', 20), ('MAX_DEPTH', 4)])
def test_prepared_policy_metadata_cannot_bypass_enclosing_work_limits(monkeypatch, bound, value):
    m = model()
    owner = ReuseState(m)
    with owner.transaction(m):
        policy = owner.prepare_policy(_large_policy())
        monkeypatch.setattr(state, bound, value)
        assert owner.reuse('unit', 'one', (), _helper, policy=policy) == [1]
    assert owner.stats()['entries'] == 0
    assert owner.stats()['bypasses'] > 0


def test_prepared_policy_memory_boundary_is_conservative():
    m = model()
    owner = ReuseState(m)
    with owner.transaction(m):
        policy = owner.prepare_policy(_large_policy())
        owner.reuse('unit', 'one', (), _helper, policy=policy)
    size = owner.stats()['bytes']
    exact, under = ReuseState(m, max_bytes=size), ReuseState(m, max_bytes=size-1)
    for candidate in (exact, under):
        with candidate.transaction(m):
            policy = candidate.prepare_policy(_large_policy())
            candidate.reuse('unit', 'one', (), _helper, policy=policy)
    assert exact.stats()['entries'] == 1
    assert under.stats()['entries'] == 0


def test_collision_equal_hash_cannot_replace_structural_policy_comparison():
    class Colliding(type):
        def __hash__(self):
            return 1

    class First(metaclass=Colliding):
        pass

    class Second(metaclass=Colliding):
        pass

    m = model()
    owner = ReuseState(m)
    calls = []

    def calculate():
        calls.append(1)
        return len(calls)

    for kind in (First, Second, Second):
        with owner.transaction(m):
            policy = owner.prepare_policy((kind,))
            result = owner.reuse('unit', 'one', (), calculate, policy=policy)
    assert result == 2
    assert len(calls) == 2


def test_raw_policy_and_unhashable_calculator_remain_safe():
    class Unhashable:
        __hash__ = None

        def __call__(self):
            return [1]

    m = model()
    owner = ReuseState(m)
    with owner.transaction(m):
        assert owner.reuse('unit', 'one', (), Unhashable()) == [1]
        assert owner.reuse('raw', 'one', (), _helper, policy=({'limit': 1},)) == [1]
    assert owner.stats()['bypasses'] == 1
    assert owner.stats()['entries'] == 1


def test_custom_record_proxy_cycle_and_nonfinite_still_measured():
    @dataclass
    class Record:
        values: list

    Record.__module__ = 'gnd.test'
    value = Record([1, 2])
    assert state._measure(value, 10**6) > state.sys.getsizeof(value)
    proxy = MappingProxyType({str(n): n for n in range(100)})
    assert state._measure(proxy, state.sys.getsizeof(proxy)) is None
    cycle = []
    cycle.append(cycle)
    for bad in (cycle, float('inf'), object()):
        assert state._measure(bad, 10**6) is None


def test_raw_policy_warm_hits_do_not_repeat_admission_tree_walk(monkeypatch):
    m = model()
    owner = ReuseState(m)
    traversals = []
    original = state._children

    def children(value):
        traversals.append(value)
        return original(value)

    monkeypatch.setattr(state, '_children', children)
    with owner.transaction(m):
        for _ in range(5):
            assert owner.reuse('raw', 'one', (), _helper, policy=_large_policy()) == [1]
        assert owner.reuse('raw', 'one', ('dirty',), _helper, policy=_large_policy()) == [1]
    assert owner.stats()['hits'] == 4
    assert sum(type(value) is tuple and len(value) == 160 for value in traversals) == 2
    assert _policy_pair_visits(traversals) == 320


def test_prepared_policy_rechecks_live_hashability(monkeypatch):
    class MutableHash(type):
        pass

    class PolicyClass(metaclass=MutableHash):
        pass

    m = model()
    owner = ReuseState(m)
    calls = []

    def calculate():
        calls.append(1)
        return len(calls)

    with owner.transaction(m):
        policy = owner.prepare_policy((PolicyClass,))
        assert owner.reuse('unit', 'one', (), calculate, policy=policy) == 1
        monkeypatch.setattr(MutableHash, '__hash__', None)
        assert owner.reuse('unit', 'one', (), calculate, policy=policy) == 2
    assert owner.stats()['bypasses'] == 1


def test_custom_metaclass_equality_cannot_hide_record_dictionary():
    class Meta(type):
        __hash__ = type.__hash__

        def __eq__(cls, other):
            return cls is other or other is type(None)

    @dataclass
    class Record(metaclass=Meta):
        values: list

    Record.__module__ = 'gnd.test'
    value = Record([])
    minimum = sum(state.sys.getsizeof(item) for item in (value, value.__dict__, value.values))
    assert state._measure(value, minimum-1) is None


def _policy_pair_visits(visited):
    return sum(type(value) is tuple and len(value) == 2 and type(value[0]) is tuple
               and len(value[0]) == 2 and value[0][0] == 'str'
               and type(value[0][1]) is str and value[0][1].startswith('helper-')
               for value in visited)


@pytest.mark.parametrize('value', [None, 'value', 123, True, 1.5])
def test_scalar_fastpath_preserves_size_and_root_limits(monkeypatch, value):
    size = state.sys.getsizeof(value)
    assert state._measure(value, size) == size
    assert state._measure(value, size-1) is None
    assert state._measure(value, None) is None
    monkeypatch.setattr(state, 'MAX_NODES', 0)
    assert state._measure(value, 10**6) is None
    monkeypatch.setattr(state, 'MAX_NODES', 100_000)
    monkeypatch.setattr(state, 'MAX_DEPTH', -1)
    assert state._measure(value, 10**6) is None
