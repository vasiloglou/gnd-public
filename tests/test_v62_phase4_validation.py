from __future__ import annotations

import json
from copy import deepcopy

import pytest
from support.v62_phase4_corpus import document, population_document

from gnd.checker import structured_extension_facts
from gnd.model import Model, _layer1_structural, analyze_aggregate, semantic_validate
from gnd.population import load_population_bytes


def _count_rule() -> dict:
    return deepcopy(document()['fact_types'][1]['derivation_rule'])

@pytest.mark.parametrize('case_id', ['A01', 'A02', 'A03', 'A04', 'A05'])
def test_a01_a05_all_five_aggregate_functions_are_schema_admitted(case_id: str) -> None:
    functions = {'A01': 'count', 'A02': 'sum', 'A03': 'min', 'A04': 'max', 'A05': 'avg'}
    model_document = deepcopy(document())
    rule = model_document['fact_types'][1]['derivation_rule']
    rule['aggregate']['fn'] = functions[case_id]
    assert _layer1_structural(model_document) == []

@pytest.mark.parametrize(('case_id', 'mutation'), [('A06', lambda rule: rule['aggregate'].update({'unexpected': True})), ('A07', lambda rule: rule['aggregate'].pop('of')), ('A08', lambda rule: rule['aggregate'].update({'over': []})), ('A09', lambda rule: rule['aggregate'].update({'over': ['$sample', '$sample']})), ('A10', lambda rule: rule.update({'second_aggregate': deepcopy(rule['aggregate'])}))])
def test_a06_a10_aggregate_shape_refusals_have_layer_one_gate(case_id, mutation) -> None:
    model_document = deepcopy(document())
    mutation(model_document['fact_types'][1]['derivation_rule'])
    assert {issue.rule_id for issue in _layer1_structural(model_document)} == {'jsonschema:oneOf'}, case_id

@pytest.mark.parametrize('mutation', [lambda rule: rule['aggregate'].update({'fn': 'median'}), lambda rule: rule['aggregate'].update({'over': ['sample']})])
def test_other_aggregate_shape_refusals_remain_closed(mutation) -> None:
    model_document = deepcopy(document())
    mutation(model_document['fact_types'][1]['derivation_rule'])
    assert {issue.rule_id for issue in _layer1_structural(model_document)} == {'jsonschema:oneOf'}

@pytest.mark.parametrize('field', ['as', 'over'])
def test_a_closed_aggregate_variable_grammar_rejects_uppercase(field: str) -> None:
    model_document = deepcopy(document())
    aggregate = model_document['fact_types'][1]['derivation_rule']['aggregate']
    if field == 'as':
        aggregate['as'] = '$Bad'
        model_document['fact_types'][1]['derivation_rule']['head']['count'] = '$Bad'
    else:
        aggregate['over'] = ['$Bad']
    assert {issue.rule_id for issue in _layer1_structural(model_document)} == {'jsonschema:oneOf'}

@pytest.mark.parametrize(('case_id', 'mutation', 'issue'), [('B01', lambda rule: rule['aggregate'].update({'of': '$missing'}), 'semantic:aggregate-of-unbound'), ('B02', lambda rule: rule['aggregate'].update({'over': ['$missing']}), 'semantic:aggregate-over-unbound'), ('B03', lambda rule: rule['aggregate'].update({'as': '$sample'}), 'semantic:aggregate-as-not-fresh'), ('B06', lambda rule: rule['head'].update({'count': '$missing'}), 'semantic:aggregate-head-scope'), ('B07', lambda rule: rule.update({'where': [{'operator': '=', 'left': '$rb', 'right': 0}]}), 'semantic:aggregate-where-scope'), ('B12', lambda rule: rule['aggregate'].update({'fn': 'median', 'over': ['$missing']}), 'semantic:aggregate-function')])
def test_b_aggregate_analyzer_refusals_are_named(case_id, mutation, issue) -> None:
    rule = _count_rule()
    mutation(rule)
    result = analyze_aggregate(rule, {'scenario': 'String', 'sample': 'String', 'rb': 'Integer'})
    assert result is not None
    assert result.issue == issue, case_id

def test_b04_b05_group_key_discovery_includes_direct_and_nested_head_reads() -> None:
    rule = _count_rule()
    direct = analyze_aggregate(rule, {'scenario': 'String', 'sample': 'String', 'rb': 'Integer'})
    assert direct is not None and direct.group_variables == ('scenario',)
    rule['head']['scenario'] = {'fn': 'add', 'args': ['$scenario', 0]}
    nested = analyze_aggregate(rule, {'scenario': 'Integer', 'sample': 'String', 'rb': 'Integer'})
    assert nested is not None and nested.group_variables == ('scenario',)

def test_b03_integrated_validation_rejects_result_bound_only_in_body() -> None:
    model_document = deepcopy(document())
    rule = model_document['fact_types'][1]['derivation_rule']
    rule['body'][0]['bind']['rb'] = '$count'
    assert 'semantic:aggregate-as-not-fresh' in {issue.rule_id for issue in semantic_validate(model_document)}

def test_c02_global_aggregate_contribution_component_is_used() -> None:
    model_document = deepcopy(document())
    count_fact = model_document['fact_types'][1]
    count_fact['reading'] = '{Integer} is the observation count'
    count_fact['roles'] = [role for role in count_fact['roles'] if role['role_name'] == 'count']
    count_fact['derivation_rule']['head'] = {'count': '$count'}
    model_document['fact_types'] = [model_document['fact_types'][0], count_fact]
    model_document['constraints'] = []
    model_document['operations'] = []
    assert semantic_validate(model_document) == []
    population = population_document()
    population['population']['covers'] = ['observation', 'scenario_count']
    population['facts'] = {'observation': population['facts']['observation'], 'scenario_count': [{'count': 4}]}
    model = Model.model_validate(model_document)
    loaded = load_population_bytes(json.dumps(population).encode(), source='global-aggregate.json', model=model)
    assert structured_extension_facts(model, loaded)['scenario_count'] == ({'count': 4},)

def test_b08_b09_input_type_and_count_any_scalar() -> None:
    rule = _count_rule()
    count = analyze_aggregate(rule, {'scenario': 'String', 'sample': 'String', 'rb': 'Integer'})
    assert count is not None and count.issue is None
    rule['aggregate']['fn'] = 'sum'
    summed = analyze_aggregate(rule, {'scenario': 'String', 'sample': 'String', 'rb': 'Integer'})
    assert summed is not None and summed.issue == 'semantic:aggregate-input-type'

def test_b10_f02_aggregate_dependency_cycle_is_refused() -> None:
    model_document = deepcopy(document())
    rule = model_document['fact_types'][1]['derivation_rule']
    rule['body'] = [{'fact_type': 'scenario_count', 'bind': {'scenario': '$scenario', 'count': '$sample'}}]
    issues = semantic_validate(model_document)
    assert {issue.rule_id for issue in issues} == {'semantic:derivation-unstratified'}
    assert all('aggregate edge' in issue.message and 'dependency cycle' in issue.message for issue in issues)

def test_d09_nonnumeric_sum_is_refused_before_evaluation() -> None:
    rule = _count_rule()
    rule['aggregate'].update({'fn': 'sum', 'of': '$sample'})
    analyzed = analyze_aggregate(rule, {'scenario': 'String', 'sample': 'String', 'rb': 'Integer'})
    assert analyzed is not None
    assert analyzed.issue == 'semantic:aggregate-input-type'

def test_e06_average_head_needs_round_refusal() -> None:
    model_document = deepcopy(document())
    rule = model_document['fact_types'][5]['derivation_rule']
    rule['head']['scenario'] = '$mean'
    assert 'semantic:aggregate-head-needs-round' in {issue.rule_id for issue in semantic_validate(model_document)}

def test_b11_schema_shape_precedes_aggregate_graph_checks() -> None:
    model_document = deepcopy(document())
    rule = model_document['fact_types'][1]['derivation_rule']
    rule['aggregate']['over'] = []
    rule['body'][0]['fact_type'] = 'scenario_count'
    assert {issue.rule_id for issue in _layer1_structural(model_document)} == {'jsonschema:oneOf'}

@pytest.mark.parametrize('where', [1, True, 'bad', {'left': '$v'}])
def test_aggregate_analyzer_refuses_non_list_where(where: object) -> None:
    rule = {'aggregate': {'fn': 'count', 'of': '$x', 'over': ['$x'], 'as': '$v'}, 'head': {'n': '$v'}, 'where': where}
    result = analyze_aggregate(rule, {'x': 'String'})
    assert result is not None
    assert result.issue == 'semantic:aggregate-where-scope'

def test_aggregate_analyzer_refuses_non_mapping_variable_primitives() -> None:
    rule = {'aggregate': {'fn': 'count', 'of': '$x', 'over': ['$x'], 'as': '$v'}, 'head': {'n': '$v'}}
    result = analyze_aggregate(rule, ['x'])
    assert result is not None
    assert result.issue == 'semantic:aggregate-shape'

@pytest.mark.parametrize('of', [{'fn': [], 'args': []}, {'fn': 'add', 'args': [{'fn': [], 'args': []}, 1]}])
def test_aggregate_analyzer_is_total_for_unhashable_term_function(of: object) -> None:
    rule = {'aggregate': {'fn': 'count', 'of': of, 'over': ['$x'], 'as': '$v'}, 'head': {'n': '$v'}}
    result = analyze_aggregate(rule, {'x': 'String'})
    assert result is not None
    assert result.issue == 'semantic:aggregate-of-unbound'
