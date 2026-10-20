"""Corpus-first IE1 cases; story entrypoint and answers are separate artifacts."""
from __future__ import annotations

import copy
import json
import time
from pathlib import Path
from threading import Thread

import pytest

from gnd import checker
from gnd.errors import UnvalidatedPopulationError
from gnd.incremental_state import ReuseRefused, ReuseState, active_state, affected_heads
from gnd.model import Model, load_model
from gnd.model_index import ModelIndex, index_scope
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT/'tests/fixtures/incremental_evaluation'
ANSWERS = json.loads((FIXTURE/'state-answers.json').read_text())
STORIES = json.loads((FIXTURE/'state-stories.json').read_text())


def model():
    return load_model(FIXTURE/'model.orm.json')


def test_corpus_has_all_named_branches():
    assert {r['id'] for r in STORIES} == set(ANSWERS) == {f'C{i}' for i in range(1,16)}
    assert all(r['story'] for r in STORIES)


def test_c1_positive_and_unrelated():
    assert sorted(affected_heads(model(), {'left'})) == ANSWERS['C1']


def test_c2_negative_and_aggregate_edges():
    doc = json.loads((FIXTURE/'model.orm.json').read_text())
    doc['fact_types'][2]['derivation_rule']['negate'] = [{'fact_type':'right','bind':{'item':'$i'}}]
    changed = Model.model_validate(doc)
    negative = affected_heads(changed, {'right'})
    aggregate = load_model(ROOT/'tests/fixtures/v62-phase4/models/aggregates.orm.yaml')
    aggregated = affected_heads(aggregate, {'observation'})
    assert ('left_copy' in negative and 'scenario_count' in aggregated and 'scenario_sum' in aggregated) == ANSWERS['C2']


def test_c3_recursive_component():
    recursive = load_model(ROOT/'tests/fixtures/v70-phase4/recursive.orm.yaml')
    assert sorted(affected_heads(recursive, {'reaches'})) == ANSWERS['C3']
    assert affected_heads(recursive, {'edge'}) == frozenset(ANSWERS['C3'])


def test_c4_unknown_scope_conservative():
    assert sorted(affected_heads(model(), {'@instances:item'})) == ANSWERS['C4']


def cache_calls(state, m, snapshots, *, options=()):
    calls = []
    def compute():
        calls.append(1)
        return {'values':[1]}
    for snapshot in snapshots:
        with state.transaction(m, options=options):
            state.reuse('test','unit',snapshot,compute,rows=1)
    return len(calls)


def test_c5_model_mutation_cold_resets():
    m=model(); state=ReuseState(m); calls=[]
    def compute(): calls.append(1); return [1]
    with state.transaction(m): state.reuse('n','u',{},compute)
    m.source['confidence']='high'
    with state.transaction(m): state.reuse('n','u',{},compute)
    assert len(calls)==ANSWERS['C5']


def test_c6_outer_scope_is_not_a_stale_proof():
    m=model(); state=ReuseState(m); seen=[]
    with index_scope():
        original=ModelIndex.for_model(m).digest
        with state.transaction(m): seen.append(ModelIndex.for_model(m).digest)
        m.operations=[]
        with state.transaction(m): seen.append(ModelIndex.for_model(m).digest)
        assert ModelIndex.for_model(m).digest==original
    assert (seen[0]==original and seen[1]!=original)==ANSWERS['C6']


def test_c7_delete_replace_reorder_are_not_set_hits():
    m=model();state=ReuseState(m)
    assert cache_calls(state,m,[[1,2],[2,1],[1],[3]])==ANSWERS['C7']
    assert cache_calls(state,m,[True,1])==2


def test_c8_options_roster_covers_reference_keys():
    m=model();state=ReuseState(m)
    assert cache_calls(state,m,[{'roster':[]},{'roster':['new']},{'covers':[]},{'reference':'new'}])==4
    calls=[]
    def compute(): calls.append(1);return 1
    for options in [(),('compiled',),('compiled',)]:
        with state.transaction(m,options=options):state.reuse('n','u',{},compute)
    assert (len(calls)==2)==ANSWERS['C8']


def test_c9_cache_cannot_mint_a_population_marker():
    m=model();p=load_population(FIXTURE/'initial.pop.json',model=m);state=ReuseState(m)
    p.facts['left'].append({'item':'unvalidated'})
    with pytest.raises(UnvalidatedPopulationError),state.transaction(m):checker.check(m,p)
    assert (state.stats()['generation']==0 and not p.matches_validation_marker(m))==ANSWERS['C9']


def test_c10_fresh_and_hit_outputs_are_detached():
    m=model();state=ReuseState(m);calls=[]
    def compute():calls.append(1);return {'values':[1]}
    with state.transaction(m):first=state.reuse('n','u',{},compute)
    first['values'].append('poison')
    with state.transaction(m):second=state.reuse('n','u',{},compute);second['values'][0]='poison'
    with state.transaction(m):third=state.reuse('n','u',{},compute)
    assert (third=={'values':[1]} and len(calls)==1)==ANSWERS['C10']


def test_c11_exception_and_cancellation_rollback():
    m=model();state=ReuseState(m)
    def compute():return [1]
    with state.transaction(m):state.reuse('n','u',{},compute)
    for exception in [RuntimeError('abort'),KeyboardInterrupt('cancel')]:
        generation=state.stats()['generation']
        with pytest.raises(type(exception)),state.transaction(m):
            state.reuse('n','u',{'changed':True},compute)
            raise exception
        assert state.stats()['generation']==generation
    with state.transaction(m):assert state.reuse('n','u',{},compute)==[1]
    assert (active_state() is None)==ANSWERS['C11']


def test_c12_reset_and_close():
    m=model();state=ReuseState(m)
    assert cache_calls(state,m,[{},{}])==1
    state.reset();assert state.stats()['entries']==0
    assert cache_calls(state,m,[{}])==1
    state.close();state.close()
    with pytest.raises(ReuseRefused,match='closed'):state.reset()
    with pytest.raises(ReuseRefused,match='closed'),state.transaction(m):pass
    assert (state.stats()['entries']==0)==ANSWERS['C12']


def test_c13_overlap_and_independent_nested_contexts():
    m=model();outer=ReuseState(m);inner=ReuseState(m);errors=[]
    def overlapping():
        try:
            with outer.transaction(m):pass
        except ReuseRefused as exc:errors.append(exc.reason)
    with outer.transaction(m):
        with pytest.raises(ReuseRefused,match='busy'),outer.transaction(m):pass
        thread=Thread(target=overlapping);thread.start();thread.join(timeout=2)
        assert not thread.is_alive()
        with inner.transaction(m):assert active_state() is inner
        assert active_state() is outer
    assert (errors==['busy'] and active_state() is None)==ANSWERS['C13']


def test_c14_limits_include_both_generations_and_fallback():
    m=model();state=ReuseState(m,max_rows=1)
    assert cache_calls(state,m,[{},{}])==1
    assert state.stats()['rows']==1
    assert cache_calls(state,m,[{'new':True}])==1
    assert state.stats()['entries']==0  # old + new would exceed the one-row cap
    tiny=ReuseState(m,max_bytes=1)
    assert cache_calls(tiny,m,[{},{}])==2
    assert tiny.stats()['entries']==0
    warm=ReuseState(m);assert cache_calls(warm,m,[{}])==1
    size=warm.stats()['bytes'];assert size>0
    exact=ReuseState(m,max_bytes=size);assert cache_calls(exact,m,[{},{}])==1
    under=ReuseState(m,max_bytes=size-1);assert cache_calls(under,m,[{},{}])==2
    assert (tiny.stats()['bypasses']>0)==ANSWERS['C14']


def test_c15_unsupported_cycles_deep_and_bounded_layer():
    m=model();state=ReuseState(m);cycle=[];cycle.append(cycle)
    deep=[];current=deep
    for _ in range(100):current.append([]);current=current[0]
    before=time.perf_counter()
    for value in [cycle,deep,object(),float('nan')]:assert cache_calls(state,m,[value,value])==2
    assert time.perf_counter()-before<2
    def compute():return object()
    with state.transaction(m):state.reuse('n','object',{},compute)
    assert (state.stats()['entries']==0)==ANSWERS['C15']


def test_policy_and_compute_code_change_are_not_reuse_proofs():
    m=model();state=ReuseState(m)
    def first():return [1]
    def second():return [2]
    with state.transaction(m):assert state.reuse('n','u',{},first,policy=(False,))==[1]
    with state.transaction(m):assert state.reuse('n','u',{},second,policy=(False,))==[2]
    with state.transaction(m):assert state.reuse('n','u',{},first,policy=(0,))==[1]
    with pytest.raises(ReuseRefused,match='model-object'),state.transaction(model()):pass
