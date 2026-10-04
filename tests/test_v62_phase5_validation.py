from __future__ import annotations

import copy

from support.v62_phase5_corpus import document

from gnd.model import Model, _layer1_structural, semantic_validate


def test_g01_g06_story_model_validates_cleanly() -> None:
    assert semantic_validate(document()) == []
    assert _layer1_structural(document()) == []
    Model.model_validate(document())

def test_g08_haversine_wrong_arity_refused_by_the_meta_schema() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_serving_distance_km':
            haversine_term = fact_type['derivation_rule']['head']['distance_km']['args'][0]
            haversine_term['args'] = haversine_term['args'][:3]
    issues = _layer1_structural(mutated)
    assert any(issue.rule_id == 'jsonschema:oneOf' for issue in issues)

def test_g09_unknown_function_name_refused() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_margin_sqrt':
            fact_type['derivation_rule']['head']['margin_sqrt']['args'][0] = {'fn': 'log', 'args': ['$margin']}
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:term-function-name' in issues

def test_g07_round_digit_not_integer_refused_at_validate() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_margin_sqrt':
            fact_type['derivation_rule']['head']['margin_sqrt']['args'][1] = 2.5
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:term-argument-type' in issues

def test_q01_unquantized_float_head_refused() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_serving_distance_km':
            wrapped = fact_type['derivation_rule']['head']['distance_km']
            fact_type['derivation_rule']['head']['distance_km'] = wrapped['args'][0]
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:derivation-float-head-unquantized' in issues
    assert 'semantic:derivation-head-needs-round' not in issues

def test_exact_tier_head_still_uses_the_original_rule_id() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_margin_sqrt_doubled':
            fact_type['derivation_rule']['head']['margin_sqrt_doubled'] = {'fn': 'mul', 'args': ['$margin_sqrt', 2]}
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:derivation-head-needs-round' in issues
    assert 'semantic:derivation-float-head-unquantized' not in issues

def test_q02_round_wrapped_head_accepted() -> None:
    doc = document()
    rules = {row['id']: row['derivation_rule'] for row in doc['fact_types'] if isinstance(row.get('derivation_rule'), dict)}
    assert rules['sample_serving_distance_km']['head']['distance_km']['fn'] == 'round'
    assert semantic_validate(doc) == []

def test_q03_avg_bare_head_refused() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'scenario_avg_rb':
            fact_type['derivation_rule']['head']['mean_rb'] = '$mean'
    issues = {issue.rule_id for issue in semantic_validate(mutated)}
    assert 'semantic:aggregate-head-needs-round' in issues

def test_q04_avg_round_wrapped_head_accepted() -> None:
    doc = document()
    rules = {row['id']: row['derivation_rule'] for row in doc['fact_types'] if isinstance(row.get('derivation_rule'), dict)}
    assert rules['scenario_avg_rb']['head']['mean_rb'] == {'fn': 'round', 'args': ['$mean', 1]}
    assert semantic_validate(doc) == []

def test_q05_q06_floor_ceil_bind_a_head_directly_with_no_round_wrapper() -> None:
    doc = document()
    rules = {row['id']: row['derivation_rule'] for row in doc['fact_types'] if isinstance(row.get('derivation_rule'), dict)}
    assert rules['sample_rate_floor']['head']['rate_floor']['fn'] == 'floor'
    assert rules['sample_rate_ceil']['head']['rate_ceil']['fn'] == 'ceil'
    assert semantic_validate(doc) == []

def test_q07_where_clause_is_free_of_quantization() -> None:
    mutated = copy.deepcopy(document())
    for fact_type in mutated['fact_types']:
        if fact_type['id'] == 'sample_handover_close':
            assert fact_type['derivation_rule']['where'][0]['left'] == '$distance_km'
    assert semantic_validate(mutated) == []

def test_q08_guarded_comparison_embeds_a_float_term() -> None:
    doc = document()
    comparison = doc['constraints'][0]['consequent']['comparison']
    assert comparison['left'] == {'fn': 'div', 'args': ['$rb', '$duration']}
    assert semantic_validate(doc) == []
