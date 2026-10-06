"""Shared family registry: extension reaches all six hooks and missing hooks refuse."""
from dataclasses import replace
from types import SimpleNamespace

import pytest

from gnd import checker, semantic_adapter, semantic_spec, universe
from gnd.documents import Model


def empty_model():
    return Model(version=1, object_types=[], fact_types=[])


def test_fake_family_changes_only_registry_entry(monkeypatch):
    from gnd.constraint_families import FAMILIES, Family
    reached = []
    def adapter(base, source, model, host):
        reached.append('adapter')
        return replace(base, expression='adapted')
    def evaluator(constraint, snapshot):
        reached.append('evaluator')
        return 1, []
    def witness(rows):
        reached.append('witness')
        return ['projected']
    def message(*args):
        reached.append('message')
        return 'fake message'
    def scope(*args):
        reached.append('scope')
        return ['fake subject']
    def shape(*args):
        reached.append('implemented')
        return True
    entry = Family(adapter, evaluator, witness, message, scope, True, shape=shape)
    monkeypatch.setitem(FAMILIES, 'rf6-fake', entry)
    model = empty_model()
    raw = {'type': 'rf6-fake', 'modality': 'alethic'}
    adapted = semantic_adapter.adapt_constraint(raw, None, 'constraints[0]', model)
    assert adapted.refused == '' and adapted.expression == 'adapted'
    assert adapted.scope_fact_types == ('fake subject',)
    assert semantic_spec.snapshot_family_result(adapted, None) == (1, [])
    assert checker._plain_projected_witness('rf6-fake', []) == ['projected']
    finding = SimpleNamespace(constraint_type='rf6-fake', verdict='pass',
                              reason_code=None, scope_id='fake')
    assert checker._correspondence_message(raw, None, finding, [], model, None) == 'fake message'
    assert set(reached) == {'adapter', 'evaluator', 'witness', 'message', 'scope', 'implemented'}


def test_every_production_entry_resolves_all_hooks():
    from gnd.constraint_families import FAMILIES, resolve_hook
    assert set(FAMILIES) == set(semantic_adapter._FAMILIES)
    for entry in FAMILIES.values():
        for field, owner in [('adapter', semantic_adapter), ('evaluator', semantic_spec),
                             ('witness', checker), ('message', checker), ('scope', universe),
                             ('shape', universe)]:
            assert callable(resolve_hook(getattr(entry, field), vars(owner)))
        assert type(entry.implemented) is bool


@pytest.mark.parametrize('hook', ['missing', 7, None])
def test_invalid_hook_is_loud(hook):
    from gnd.constraint_families import resolve_hook
    with pytest.raises(RuntimeError, match='not callable'):
        resolve_hook(hook, {})


def test_unknown_and_unimplemented_preserve_refusals():
    raw = {'type': 'unknown', 'modality': 'alethic'}
    adapted = semantic_adapter.adapt_constraint(raw, None, 'constraints[0]', empty_model())
    assert adapted.refused == 'unregistered-family' and adapted.modality == 'alethic'
    assert semantic_spec.snapshot_family_result(adapted, None) == (-1, [])
    assert not universe.is_implemented(raw, None)
    assert not universe.is_implemented({'type': 'textual'}, None)
    textual = semantic_adapter.adapt_constraint({'type': 'textual', 'modality': 'alethic',
                                                'expression': 'hello'}, None, 'c', empty_model())
    assert textual.refused == '' and textual.expression == 'hello'


@pytest.mark.parametrize('value', [None, [], True, 3, 'bad', {'type': []}])
def test_hostile_adapter_remains_total(value):
    assert semantic_adapter.adapt_constraint(value, None, 'c', empty_model()).refused
