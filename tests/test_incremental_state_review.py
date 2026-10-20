"""Independent IE1 review reproductions, written before repairs."""
import sys
from contextvars import copy_context
from types import MappingProxyType

import pytest

from gnd import incremental_state as state_module
from gnd.incremental_state import ReuseRefused, ReuseState, affected_heads
from tests.test_incremental_state import model


def test_expired_context_cannot_join_later_transaction():
    m = model()
    state = ReuseState(m)
    with state.transaction(m):
        saved = copy_context()
    with pytest.raises(ReuseRefused, match='not-active'):
        saved.run(state.discard)
    with state.transaction(m), pytest.raises(ReuseRefused, match='not-active'):
        saved.run(state.discard)


def test_options_cannot_escape_budget_and_close_releases_binding():
    m = model()
    state = ReuseState(m, max_bytes=64)
    with state.transaction(m, options=('x' * 100_000,)):
        pass
    assert state._binding is None
    state.close()
    assert state._binding is None


def test_proxy_accounts_for_owned_backing_dictionary():
    value = MappingProxyType({i: i for i in range(10_000)})
    shallow = sys.getsizeof(value) + sum(sys.getsizeof(i) for i in value)
    cap = shallow + sys.getsizeof(dict(value)) // 2
    assert state_module._measure(value, cap) is None


def test_shared_policy_has_cumulative_work_bound(monkeypatch):
    monkeypatch.setattr(state_module, 'MAX_NODES', 1000)
    value = (0,)
    for _ in range(3):
        value = (value,) * 30
    with pytest.raises(state_module._Unsupported):
        state_module._policy(value)


def test_malformed_dependency_body_refuses_clean_selection():
    m = model()
    doc = m.model_dump()
    doc['fact_types'][2]['derivation_rule']['body'] = {'fact_type': 'left'}
    malformed = type(m).model_validate(doc)
    with pytest.raises(ReuseRefused, match='incomplete-dependencies'):
        affected_heads(malformed, {'left'})


def test_expired_copied_index_scope_cannot_hide_model_mutation():
    from gnd.model_index import ModelIndex

    m = model()
    state = ReuseState(m)
    with state.transaction(m):
        saved = copy_context()
        before = ModelIndex.for_model(m).digest
    m.source['confidence'] = 'high'
    assert saved.run(ModelIndex.for_model, m).digest != before


def test_copied_live_context_cannot_authorize_another_thread():
    from threading import Thread

    m = model()
    state = ReuseState(m)
    observed = []

    def invoke():
        try:
            state.discard()
        except ReuseRefused as error:
            observed.append(error.reason)

    with state.transaction(m):
        saved = copy_context()
        thread = Thread(target=lambda: saved.run(invoke))
        thread.start()
        thread.join(timeout=2)
        assert not thread.is_alive()
    assert observed == ['not-active']


def test_accounting_measures_the_private_clone():
    m = model()
    state = ReuseState(m)

    def calculate():
        return [[n] for n in range(1000)]

    with state.transaction(m):
        state.reuse('clone', 'lists', (), calculate)
    key, entry = next(iter(state._entries.items()))
    actual = state_module._measure((key, entry.signature, entry.value, entry.branches), 10**8)
    assert entry.size >= actual + state_module.ENTRY_METADATA_BYTES


def test_changed_binding_charges_committed_entries_before_yield():
    m = model()
    state = ReuseState(m, max_bytes=12_000)

    def calculate():
        return 'v' * 7000

    with state.transaction(m):
        state.reuse('n', 'u', (), calculate)
    assert state.stats()['entries'] == 1
    with state.transaction(m, options=('x' * 7000,)):
        assert state._disabled


def test_opaque_rule_cannot_prove_clean_dependency_selection():
    m = model()
    m.fact_types[2]['derivation_rule'] = 'An opaque rule may depend on left.'
    with pytest.raises(ReuseRefused, match='incomplete-dependencies'):
        affected_heads(m, {'left'})
