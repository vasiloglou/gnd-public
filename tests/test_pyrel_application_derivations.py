"""Red-first generic structured-rule integration controls for PA2."""
import copy
import runpy

import pytest
from test_pyrel_application_acceptance import RUNTIME
from test_pyrel_application_native import execute_cases


def model_and_population():
    model = {'version': 2, 'model_id': 'generic-derived',
             'object_types': [{'id': 'text', 'kind': 'value', 'primitive': 'String'},
                              {'id': 'number', 'kind': 'value', 'primitive': 'Integer'}],
             'fact_types': [{'id': name, 'roles': [{'role_name': 'label', 'object_type': 'text'},
                                                 {'role_name': 'score', 'object_type': 'number'}]}
                            for name in ['raw', 'blocked_input', 'blocked_result', 'available_result']],
             'constraints': []}
    model['fact_types'][2].update(derivation='derived', storage='computed',
                                 derivation_rule={'body': [{'fact_type': 'blocked_input', 'bind': {'label': '$x', 'score': '$n'}}],
                                                  'head': {'label': '$x', 'score': '$n'}})
    model['fact_types'][3].update(derivation='derived', storage='computed',
                                 derivation_rule={'body': [{'fact_type': 'raw', 'bind': {'label': '$x', 'score': '$n'}}],
                                                  'negate': [{'fact_type': 'blocked_result', 'bind': {'label': '$x', 'score': '$n'}}],
                                                  'head': {'label': '$x', 'score': '$n'}})
    pop = {'population': {'model_id': 'generic-derived', 'covers': [f['id'] for f in model['fact_types']]},
           'facts': {'raw': [{'label': 'a', 'score': 7}, {'label': 'b', 'score': 8}],
                     'blocked_input': [{'label': 'b', 'score': 8}],
                     'blocked_result': [{'label': 'b', 'score': 8}],
                     'available_result': [{'label': 'a', 'score': 7}]}}
    return model, pop


def compiler():
    namespace = runpy.run_path(str(RUNTIME))
    function = namespace.get('_profile_derivations')
    assert callable(function), 'structured derivation admission is absent from standalone runtime'
    return namespace, function


def test_negative_dependency_order_is_not_declaration_order():
    namespace, function = compiler()
    model, _ = model_and_population()
    model['fact_types'].reverse()
    ordered = function(namespace['admit_model'](model))
    assert ordered == ['blocked_result', 'available_result']


@pytest.mark.parametrize('damage', ['cycle', 'opaque', 'clauses', 'unsafe-negative', 'unbound-head',
                                   'missing-head-role', 'unknown-fact', 'unknown-role', 'body-limit',
                                   'negative-limit', 'bad-rule', 'bad-body', 'bad-head', 'head-literal',
                                   'typed-head', 'v1', 'semiderived', 'stored-derived'])
def test_derivation_grammar_refuses_before_native_import(damage):
    namespace, function = compiler()
    model, _ = model_and_population()
    fact = model['fact_types'][3]; rule = fact['derivation_rule']
    if damage == 'cycle':
        model['fact_types'][2]['derivation_rule']['body'][0]['fact_type'] = 'available_result'
    elif damage == 'opaque':
        fact['derivation_rule'] = 'business prose'
    elif damage == 'clauses':
        rule['clauses'] = []
    elif damage == 'unsafe-negative':
        rule['negate'][0]['bind']['label'] = '$unsafe'
    elif damage == 'unbound-head':
        rule['head']['label'] = '$unbound'
    elif damage == 'missing-head-role':
        del rule['head']['score']
    elif damage == 'unknown-fact':
        rule['body'][0]['fact_type'] = 'missing'
    elif damage == 'unknown-role':
        rule['body'][0]['bind']['unknown'] = '$x'
    elif damage == 'body-limit':
        rule['body'] *= 9
    elif damage == 'negative-limit':
        rule['negate'] *= 9
    elif damage == 'bad-rule':
        fact['derivation_rule'] = []
    elif damage == 'bad-body':
        rule['body'] = None
    elif damage == 'bad-head':
        rule['head'] = []
    elif damage == 'head-literal':
        rule['head']['label'] = 'literal'
    elif damage == 'typed-head':
        rule['head']['score'] = '$x'
    elif damage == 'v1':
        model['version'] = 1
    elif damage == 'semiderived':
        fact['derivation'] = 'semiderived'
    else:
        fact['storage'] = 'stored'
    with pytest.raises(namespace['ProfileRefusal']):
        function(namespace['admit_model'](model))


@pytest.mark.pyrel_oracle
def test_native_computed_claims_and_negative_dependency_are_generic(tmp_path):
    cases = []
    for damage in ['clean', 'reverse', 'missing', 'extra', 'blocked-forgery', 'empty-negative', 'empty-positive', 'duplicate-claims']:
        model, pop = model_and_population()
        if damage == 'reverse':
            model['fact_types'].reverse()
        elif damage == 'missing':
            pop['facts']['available_result'] = []
        elif damage == 'extra':
            pop['facts']['available_result'].append({'label': 'b', 'score': 8})
        elif damage == 'blocked-forgery':
            pop['facts']['blocked_result'] = []
        elif damage == 'empty-negative':
            pop['facts']['blocked_input'] = []; pop['facts']['blocked_result'] = []
            pop['facts']['available_result'] = copy.deepcopy(pop['facts']['raw'])
        elif damage == 'empty-positive':
            pop['facts'] = {name: [] for name in pop['facts']}
        elif damage == 'duplicate-claims':
            pop['facts']['available_result'] *= 2
        cases.append({'model': model, 'population': pop})
    reports = execute_cases(tmp_path, cases)
    assert [r['status'] for r in reports] == ['accepted', 'accepted', 'rejected', 'rejected', 'rejected', 'accepted', 'accepted', 'accepted'], reports
    for report in reports:
        assert {r['derivation_ref'] for r in report['derivations']} == {'derivation:blocked_result', 'derivation:available_result'}
    rows = {r['fact_type']: r for r in reports[2]['derivations']}
    assert rows['available_result']['missing'] == [{'label': 'a', 'score': 7}]
    rows = {r['fact_type']: r for r in reports[3]['derivations']}
    assert rows['available_result']['extra'] == [{'label': 'b', 'score': 8}]
    rows = {r['fact_type']: r for r in reports[4]['derivations']}
    assert rows['available_result']['computed'] == [{'label': 'a', 'score': 7}]
    assert rows['blocked_result']['missing'] == [{'label': 'b', 'score': 8}]
