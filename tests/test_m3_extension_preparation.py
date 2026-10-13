"""Scoped derivation controls over existing fixtures and algorithm shapes."""
from contextlib import nullcontext
from dataclasses import replace
from pathlib import Path

import pytest

from gnd import api, checker
from gnd import extensions as ext
from gnd.branches import capture_branches
from gnd.model import load_model
from gnd.population import load_population

ROOT = Path(__file__).parent / "fixtures/derivation-evaluation/cases/cost-chain-counted"


def inputs():
    model = load_model(ROOT / "model.orm.yaml")
    population = load_population(ROOT / "population.yaml", model=model)
    return model, population, ext.base_relations(model, population)


def scope(model, population):
    factory = getattr(ext, "calculation_scope", None)
    return factory(model, population) if factory else nullcontext()


def body_counter(monkeypatch):
    counts = []
    original = ext._relation_facts
    def counted(*args, **kwargs):
        counts.append(1)
        return original(*args, **kwargs)
    monkeypatch.setattr(ext, "_relation_facts", counted)
    return counts


def test_identical_full_calculation_once_with_fresh_consumer_work(monkeypatch):
    model, population, relations = inputs()
    counts = body_counter(monkeypatch)
    with scope(model, population):
        first = ext._evaluate_stratified_extensions(model, relations)
        before = len(counts)
        assert before > 0
        expected = first.counted_operations.atom_role_terms_read
        first.counted_operations.atom_role_terms_read = -100
        second = ext._evaluate_stratified_extensions(model, relations)
        assert len(counts) == before
        assert first.extensions == second.extensions
        assert second.counted_operations.atom_role_terms_read == expected
        assert first.counted_operations is not second.counted_operations
    with scope(model, population):
        ext._evaluate_stratified_extensions(model, relations)
    assert len(counts) > before


def test_relation_and_model_content_and_policy_changes_do_not_reuse(monkeypatch):
    model, population, relations = inputs()
    counts = body_counter(monkeypatch)
    with scope(model, population):
        ext._evaluate_stratified_extensions(model, relations)
        before = len(counts)
        changed = dict(relations)
        changed['seed'] = replace(relations['seed'], rows=())
        result = ext._evaluate_stratified_extensions(model, changed)
        assert len(counts) > before and not result.extensions['top'].rows
        before = len(counts)
        ext._evaluate_stratified_extensions(model, relations, exact=True)
        assert len(counts) > before
        before = len(counts)
        token = ext.PARTIAL_OPAQUE.set(True)
        try: ext._evaluate_stratified_extensions(model, relations)
        finally: ext.PARTIAL_OPAQUE.reset(token)
        assert len(counts) > before
        before = len(counts)
        model.source = {**model.source, 'confidence': 'high'}
        ext._evaluate_stratified_extensions(model, relations)
        assert len(counts) > before


def test_nested_scopes_and_exception_cleanup(monkeypatch):
    model, population, relations = inputs()
    other_model, other_population, other_relations = inputs()
    counts = body_counter(monkeypatch)
    with scope(model, population):
        ext._evaluate_stratified_extensions(model, relations)
        with scope(other_model, other_population):
            ext._evaluate_stratified_extensions(other_model, other_relations)
        before = len(counts)
        ext._evaluate_stratified_extensions(model, relations)
        assert len(counts) == before
    with pytest.raises(RuntimeError), scope(model, population):
        ext._evaluate_stratified_extensions(model, relations)
        raise RuntimeError('owner failure')
    before = len(counts)
    with scope(model, population):ext._evaluate_stratified_extensions(model, relations)
    assert len(counts) > before


def test_trace_and_exact_metadata_are_retained_and_isolated(monkeypatch):
    model, population, relations = inputs()
    counts = body_counter(monkeypatch)
    with scope(model, population):
        with capture_branches() as first_trace:
            first = ext._evaluate_stratified_extensions(model, relations, exact=True)
        before = len(counts)
        first.extensions.pop('top')
        with capture_branches() as second_trace:
            second = ext._evaluate_stratified_extensions(model, relations, exact=True)
        assert len(counts) == before
        assert 'top' in second.extensions
        assert first_trace == second_trace
        assert second.extensions.unavailable == {}
        assert second.extensions['top'].row_lineage


def test_selective_prior_observer_and_witness_fall_back(monkeypatch):
    model, population, relations = inputs()
    counts = body_counter(monkeypatch)
    with scope(model, population):
        for kwargs in [{'heads': ('top',)}, {'prior_possible': {}}, {'prior_unavailable': {}},
                       {'observe_partial': lambda *args: None}]:
            ext._evaluate_stratified_extensions(model, relations, **kwargs)
            before = len(counts)
            ext._evaluate_stratified_extensions(model, relations, **kwargs)
            assert len(counts) > before
        class Witness:
            def charge(self,*args):pass
            def row(self,*args):pass
        token = ext.WITNESS_TRACE.set(Witness())
        try:
            ext._evaluate_stratified_extensions(model, relations)
            before = len(counts)
            ext._evaluate_stratified_extensions(model, relations)
            assert len(counts) > before
        finally: ext.WITNESS_TRACE.reset(token)


def test_public_and_direct_checker_own_scopes(monkeypatch):
    from gnd import extension_preparation as prepared
    model,population,_ = inputs()
    observed = []
    original = ext._python_extension_calculator
    def watched(*args,**kwargs):
        observed.append(prepared.current_scope())
        return original(*args,**kwargs)
    monkeypatch.setattr(ext,'_python_extension_calculator',watched)
    for _ in range(2):
        payload=api.check(model,population,compiled_operations=True)
        assert payload['exit_code'] in (1,2)
        assert prepared.current_scope() is None
    assert observed and all(value is not None for value in observed)
    observed.clear()
    checker.check(model,population,compiled_operations=True)
    assert observed and all(value is not None for value in observed)
    assert prepared.current_scope() is None


def test_fingerprint_totality_and_bound_bypass(monkeypatch):
    from gnd import extension_preparation as prepared
    cycle=[];cycle.append(cycle)
    assert prepared.fingerprint(cycle) is None
    assert prepared.fingerprint(object()) is None
    assert prepared.fingerprint({'x': [True, 1, 1.0]}) != prepared.fingerprint({'x': [1, 1, 1]})
    monkeypatch.setattr(prepared,'MAX_FINGERPRINT_NODES',1)
    assert prepared.fingerprint({'x': [1]}) is None
    model,population,relations=inputs();counts=body_counter(monkeypatch)
    with scope(model,population):
        ext._evaluate_stratified_extensions(model,relations)
        before=len(counts)
        ext._evaluate_stratified_extensions(model,relations)
        assert len(counts)>before
