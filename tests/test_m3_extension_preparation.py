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
        model.source['confidence'] = 'high'
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
    actual = ext._relation_facts
    def branch_body(*args, **kwargs):
        ext.record_branch("derivation:extension:derived:exact-applied")
        return actual(*args, **kwargs)
    monkeypatch.setattr(ext, "_relation_facts", branch_body)
    with scope(model, population):
        with capture_branches() as first_trace:
            first = ext._evaluate_stratified_extensions(model, relations, exact=True)
        before = len(counts)
        first.extensions.pop('top')
        with capture_branches() as second_trace:
            second = ext._evaluate_stratified_extensions(model, relations, exact=True)
        assert len(counts) == before
        assert 'top' in second.extensions
        assert first_trace and first_trace == second_trace
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


def test_cached_unavailable_binding_is_an_independent_mapping() -> None:
    model,population,_ = inputs()
    with scope(model,population):
        owner = ext.current_scope()
        result = ext.ExactExtensionResult(
            ext.ExactExtensions({},unavailable={'top': ext.RelationUnavailable('top','term:div-zero',{'$i': 'alpha'})}),
            ext.ExactJoinWork(),
        )
        first=owner.calculate(('unit',),(),lambda:result,ext._clone_prepared_calculation,ext.record_branch)
        first.extensions.unavailable['top'].binding['$i']='poison'
        second=owner.calculate(('unit',),(),lambda:result,ext._clone_prepared_calculation,ext.record_branch)
        assert second.extensions.unavailable['top'].binding['$i']=='alpha'


def test_failed_calculation_does_not_cache_and_restores_branch_capture(monkeypatch):
    model,population,relations=inputs()
    original=ext._clause_bindings
    def fail(*args,**kwargs):raise RuntimeError('calculation failure')
    with scope(model,population):
        monkeypatch.setattr(ext,'_clause_bindings',fail)
        with pytest.raises(RuntimeError,match='calculation failure'):
            ext._evaluate_stratified_extensions(model,relations)
        assert not ext.current_scope().records
        monkeypatch.setattr(ext,'_clause_bindings',original)
        assert ext._evaluate_stratified_extensions(model,relations).extensions['top'].rows


def test_cache_entry_character_and_reference_trace_limits_fall_back(monkeypatch):
    from gnd import extension_preparation as prepared
    model,population,relations=inputs();counts=body_counter(monkeypatch)
    with scope(model,population):
        token=ext.REFERENCE_PRESENTATION_WORK.set(object())
        try:
            ext._evaluate_stratified_extensions(model,relations)
            before=len(counts)
            ext._evaluate_stratified_extensions(model,relations)
            assert len(counts)>before
        finally:ext.REFERENCE_PRESENTATION_WORK.reset(token)
    monkeypatch.setattr(prepared,'MAX_PREPARED_CALCULATIONS',0)
    with scope(model,population):
        ext._evaluate_stratified_extensions(model,relations)
        before=len(counts)
        ext._evaluate_stratified_extensions(model,relations)
        assert len(counts)>before
    monkeypatch.setattr(prepared,'MAX_FINGERPRINT_CHARACTERS',2)
    assert prepared.fingerprint('abc') is None
    assert prepared.fingerprint(1<<24) is None
    assert prepared.fingerprint([[[[object()]]]]) is None


def test_review_aggregate_budget_charges_hits_and_failed_attempts(monkeypatch):
    from gnd import extension_preparation as prepared
    model,population,_=inputs()
    monkeypatch.setattr(prepared,'MAX_FINGERPRINT_NODES',12)
    calls=[]
    with scope(model,population) as owner:
        for _ in range(3):
            owner.calculate(('unit',),{'x': (1,2,3)},lambda:calls.append(1) or 1,lambda v:v,ext.record_branch)
        assert len(calls)==2
        assert owner.nodes==12
    with scope(model,population) as owner:
        owner.calculate(('unsupported',),{'x':object()},lambda:1,lambda v:v,ext.record_branch)
        assert owner.nodes>0


def test_review_warm_helper_patch_invalidates_result(monkeypatch):
    model,population,relations=inputs()
    with scope(model,population):
        assert ext._evaluate_stratified_extensions(model,relations).extensions['top'].rows
        monkeypatch.setattr(ext,'derivation_strata',lambda document:[])
        assert not ext._evaluate_stratified_extensions(model,relations).extensions


def test_review_public_scope_spans_compose_and_joins_checker(monkeypatch):
    from gnd import compiled_obligations
    from gnd import extension_preparation as prepared
    fixture=Path(__file__).parent/'fixtures/compiled-snapshot'
    model=load_model(fixture/'model.orm.json');population=load_population(fixture/'numeric.pop.json',model=model)
    owners=[];original=ext._evaluate_derivations
    def observed(*args,**kwargs):
        owners.append(prepared.current_scope())
        return original(*args,**kwargs)
    monkeypatch.setattr(ext,'evaluate_derivations',observed)
    compose_owners=[];original_compose=compiled_obligations.compose
    def compose(*args,**kwargs):
        compose_owners.append(prepared.current_scope())
        return original_compose(*args,**kwargs)
    monkeypatch.setattr(compiled_obligations,'compose',compose)
    for _ in range(2):
        before=len(owners)
        api.check(model,population,compiled_operations=True)
        found=owners[before:]
        assert len(found)>=2 and all(owner is found[0] for owner in found)
        assert found[0] is not None and compose_owners[-1] is found[0]
    assert compose_owners[0] is not compose_owners[1]
    with scope(model,population) as owner, scope(model,population) as nested:
        assert nested is owner


def test_review_public_real_calculation_reuse_matches_uncached_report(monkeypatch):
    from gnd import extension_preparation as prepared
    fixture=Path(__file__).parent/'fixtures/compiled-snapshot'
    model=load_model(fixture/'model.orm.json');population=load_population(fixture/'numeric.pop.json',model=model)
    counts=body_counter(monkeypatch)
    with monkeypatch.context() as disabled:
        disabled.setattr(prepared,'MAX_PREPARED_CALCULATIONS',0)
        baseline=api.check(model,population,compiled_operations=True)
    before=len(counts)
    assert before>0
    candidate=api.check(model,population,compiled_operations=True)
    assert len(counts)-before<before
    assert candidate==baseline


def test_failed_fingerprint_charged_before_nested_fallback(monkeypatch):
    from gnd import extension_preparation as prepared
    model,population,_=inputs()
    monkeypatch.setattr(prepared,'MAX_FINGERPRINT_NODES',3)
    with scope(model,population) as owner:
        def fallback():
            return owner.calculate(('nested',),1,lambda:1,lambda v:v,ext.record_branch)
        owner.calculate(('unsupported',),{'x':object()},fallback,lambda v:v,ext.record_branch)
        assert owner.nodes==3
