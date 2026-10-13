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


@pytest.mark.parametrize('damage', ['negative-coverage', 'head-coverage', 'missing-head-list'])
def test_unknown_relations_refuse_even_when_positive_is_empty(damage):
    namespace, _ = compiler()
    model, pop = model_and_population()
    pop['facts']['raw'] = []
    if damage == 'negative-coverage':
        pop['population']['covers'].remove('blocked_result')
    elif damage == 'head-coverage':
        pop['population']['covers'].remove('available_result')
    else:
        del pop['facts']['available_result']
    report = namespace['acceptance_document'](model, pop, model_sha256='a' * 64, population_sha256='b' * 64)
    assert report['exit_code'] == 2 and not report['accepted']
    assert all(row['status'] == 'incomplete' and row['computed'] is None for row in report['derivations'])


@pytest.mark.pyrel_oracle
def test_native_derivation_work_and_result_limits(tmp_path):
    cases = []
    model, pop = model_and_population()
    pop['facts']['raw'] = [{'label': f'a{i}', 'score': 7} for i in range(500)]
    pop['facts']['blocked_input'] = [{'label': f'b{i}', 'score': 8} for i in range(500)]
    pop['facts']['blocked_result'] = []; pop['facts']['available_result'] = []
    cases.append({'model': model, 'population': pop})
    model, pop = model_and_population()
    model['fact_types'][2]['derivation_rule'] = {
        'body': [{'fact_type': 'raw', 'bind': {'label': '$x'}},
                 {'fact_type': 'blocked_input', 'bind': {'score': '$n'}}],
        'head': {'label': '$x', 'score': '$n'}}
    pop['facts'] = {'raw': [{'label': f'a{i}', 'score': 7} for i in range(101)],
                    'blocked_input': [{'label': 'b', 'score': i} for i in range(101)],
                    'blocked_result': [], 'available_result': []}
    cases.append({'model': model, 'population': pop})
    reports = execute_cases(tmp_path, cases)
    assert all(report['exit_code'] == 2 and not report['accepted'] for report in reports), reports
    assert reports[0]['derivations'][0]['reason'] == 'derivation-join-work-limit'
    assert reports[1]['derivations'][0]['reason'] == 'native-result-tuple-limit'


@pytest.mark.pyrel_oracle
def test_native_computed_rows_preserve_inline_key_multiplicity(tmp_path):
    model, pop = model_and_population()
    model['fact_types'][2]['derivation_rule']['body'][0]['fact_type'] = 'raw'
    model['fact_types'][2]['constraints'] = [{'type': 'uniqueness', 'roles': ['label']}]
    pop['facts']['raw'] = [{'label': 'a', 'score': 7}, {'label': 'a', 'score': 8}]
    pop['facts']['blocked_result'] = copy.deepcopy(pop['facts']['raw'])
    pop['facts']['available_result'] = []
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['status'] == 'rejected' and report['exit_code'] == 1, report
    assert report['verdicts'][0]['status'] == 'violated'
    assert all(row['status'] == 'satisfied' for row in report['derivations'])


@pytest.mark.pyrel_oracle
def test_native_literal_and_repeated_variables_in_rule_body(tmp_path):
    model, pop = model_and_population()
    model['fact_types'][2]['derivation_rule']['body'][0]['fact_type'] = 'raw'
    model['fact_types'][2]['derivation_rule']['body'].append({'fact_type': 'blocked_input', 'bind': {'label': '$x', 'score': 8}})
    pop['facts']['blocked_result'] = [{'label': 'b', 'score': 8}]
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['accepted'], report
    assert report['derivations'][0]['computed'] == [{'label': 'b', 'score': 8}]


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('family', ['mandatory', 'value'])
def test_native_computed_entity_universe_cannot_omit_new_subtype_members(tmp_path, family):
    from gnd.api import check
    model = {'version': 2, 'model_id': 'entity-derived',
             'object_types': [{'id': 'name', 'kind': 'value', 'primitive': 'String'},
                              {'id': 'party', 'kind': 'entity', 'reference': {'mode': 'popular', 'value_type': 'name'}},
                              {'id': 'person', 'kind': 'entity', 'subtype_of': ['party'], 'inherits_reference': True}],
             'fact_types': [{'id': 'seen', 'reading': '{party} was seen', 'roles': [{'role_name': 'who', 'object_type': 'party'}]},
                            {'id': 'active', 'reading': '{person} is active', 'roles': [{'role_name': 'who', 'object_type': 'person'}],
                             'derivation': 'derived', 'storage': 'computed',
                             'derivation_rule': {'body': [{'fact_type': 'seen', 'bind': {'who': '$p'}}], 'head': {'who': '$p'}}},
                            {'id': 'tagged', 'reading': '{person} is tagged', 'roles': [{'role_name': 'who', 'object_type': 'person'}]}],
             'constraints': []}
    constraint = {'type': family, 'source': 'explicit', 'status': 'confirmed', 'modality': 'alethic',
                  'provenance': {'user_quote': 'Entity universe regression.'}}
    if family == 'mandatory':
        constraint['role'] = 'who'
        model['fact_types'][2]['constraints'] = [constraint]
    else:
        constraint.update(object_type='person', allowed=['b'])
        model['constraints'] = [constraint]
    pop = {'population': {'model': 'model.json', 'model_id': 'entity-derived', 'source': 'synthetic',
                          'covers': ['seen', 'active', 'tagged']},
           'facts': {'seen': [{'who': 'a'}], 'active': [{'who': 'a'}], 'tagged': [{'who': 'b'}]}}
    source = tmp_path / 'model.json'; population = tmp_path / 'population.json'
    source.write_text(__import__('json').dumps(model)); population.write_text(__import__('json').dumps(pop))
    gnd_result = check(source, population)
    assert gnd_result['exit_code'] == 1, gnd_result
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['exit_code'] == 1 and not report['accepted'], report
    assert report['verdicts'][0]['status'] == 'violated'
    assert all(row['status'] == 'satisfied' for row in report['derivations'])


@pytest.mark.pyrel_oracle
def test_duplicate_derived_key_claims_cannot_false_accept(tmp_path):
    import json

    from gnd.api import check
    model, pop = model_and_population()
    constraint = {'type': 'uniqueness', 'roles': ['label', 'score'], 'source': 'explicit',
                  'status': 'confirmed', 'modality': 'alethic',
                  'provenance': {'user_quote': 'Derived key regression.'}}
    model['fact_types'][3]['constraints'] = [constraint]
    for fact in model['fact_types']:
        fact['reading'] = '{text} has {number}'
    pop['population'].update(model='model.json', source='synthetic')
    pop['facts']['available_result'] *= 2
    source = tmp_path / 'model.json'; population = tmp_path / 'population.json'
    source.write_text(json.dumps(model)); population.write_text(json.dumps(pop))
    gnd_result = check(source, population)
    assert gnd_result['exit_code'] == 1, gnd_result
    assert any(row['constraint_type'] == 'uniqueness' and row['verdict'] == 'fail' for row in gnd_result['verdicts'])
    report = execute_cases(tmp_path, [{'model': model, 'population': pop}])[0]
    assert report['exit_code'] == 2 and not report['accepted'], report
    assert report['derivations'][0]['reason'] == 'duplicate-derived-key-claims'
