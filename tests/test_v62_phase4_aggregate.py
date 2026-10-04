from __future__ import annotations

import copy
from fractions import Fraction

import pytest
from support.v62_phase4_corpus import CASES_DOC, FIXTURE, document

from gnd import checker
from gnd.checker import (
    _aggregate_bindings,
    _ExactJoinWork,
    exact_extension_envelope,
    structured_extension_facts,
    structured_extension_view,
)
from gnd.model import Model
from gnd.population import load_population
from gnd.terms import DEFAULT_LIMITS, compare_terms


def test_c07_noninjective_function_of_keeps_distinct_over_bindings() -> None:
    model_document = copy.deepcopy(document())
    rule = model_document['fact_types'][1]['derivation_rule']
    rule['aggregate']['of'] = {'fn': 'mod', 'args': ['$rb', 2]}
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    rows = structured_extension_facts(model, population)['scenario_count']
    assert [dict(row) for row in rows] == [{'scenario': 'north', 'count': 3}, {'scenario': 'south', 'count': 1}]

def test_e08_nonintegral_average_binding_survives_undefined_post_filter() -> None:
    model_document = copy.deepcopy(document())
    rule = model_document['fact_types'][5]['derivation_rule']
    rule['where'] = [{'operator': '>', 'left': '$mean', 'right': 0}, {'operator': '=', 'left': {'fn': 'mod', 'args': [1, 0]}, 'right': 0}]
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    envelope = exact_extension_envelope(model, population)
    failure = envelope['unavailable']['scenario_mean_ok']
    assert failure['reason'] == 'term:mod-zero'
    assert failure['binding']['$mean'] == '["number",[320,3]]'

def test_e04_average_comparison_cross_product_obeys_exact_width_limit() -> None:
    mean = Fraction((1 << DEFAULT_LIMITS.max_value_bits) - 1, 2)
    result = compare_terms('<', '$mean', 1 << DEFAULT_LIMITS.max_value_bits - 1, {'mean': mean}, bound_cross_product=True)
    assert not result.available
    assert result.reason == 'term:exact-value-too-wide'
    assert result.max_value_bits == DEFAULT_LIMITS.max_value_bits + 1

def test_e04_successful_aggregate_comparison_counts_two_cross_products() -> None:
    result = compare_terms('<', '$mean', 1, {'mean': Fraction(1, 3)}, bound_cross_product=True)
    assert result.available and result.value is True
    assert result.operations == 2

def test_k04_aggregate_free_comparison_keeps_phase3_wide_float_behavior() -> None:
    result = compare_terms('>', (1 << 65535) - 1, 5e-324, {})
    assert result.available and result.value is True

def test_u02_wide_aggregate_value_is_unavailable_without_exception() -> None:
    rule = {'aggregate': {'fn': 'sum', 'of': '$value', 'over': ['$id'], 'as': '$sum'}, 'head': {'group': '$group', 'sum': '$sum'}}
    rows = [{'group': 'north', 'id': 'one', 'value': 1 << 65535}, {'group': 'north', 'id': 'two', 'value': 1 << 65535}]
    collapsed, unavailable = _aggregate_bindings(rule, rows, _ExactJoinWork())
    assert collapsed == []
    assert unavailable is not None
    assert unavailable.reason == 'term:exact-value-too-wide'

def test_q01_tiny_sum_oracle_reports_exact_counted_work() -> None:
    rule = {'aggregate': {'fn': 'sum', 'of': '$value', 'over': ['$id'], 'as': '$sum'}, 'head': {'group': '$group', 'sum': '$sum'}}
    rows = [{'group': 'north', 'id': 'one', 'value': 2}, {'group': 'north', 'id': 'two', 'value': 3}]
    work = _ExactJoinWork()
    collapsed, unavailable = _aggregate_bindings(rule, rows, work)
    assert unavailable is None
    assert collapsed == [{'group': 'north', 'sum': 5}]
    assert work.aggregate_candidate_bindings == 2
    assert work.aggregate_contribution_terms == 2
    assert work.aggregate_identity_tokens == 6
    assert work.aggregate_distinct_contributions == 2
    assert work.aggregate_group_lookups == 2
    assert work.aggregate_groups == 1
    assert work.aggregate_exact_operations == 2
    assert work.aggregate_maximum_value_bits == 3

def test_q01_aggregate_work_survives_public_extension_view() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    work = structured_extension_view(model, population).work
    assert work.aggregate_candidate_bindings > 0
    assert work.aggregate_contribution_terms > 0
    assert work.aggregate_identity_tokens > 0
    assert work.aggregate_distinct_contributions > 0
    assert work.aggregate_group_lookups > 0
    assert work.aggregate_groups > 0
    assert work.aggregate_exact_operations > 0
    assert work.aggregate_maximum_value_bits > 0

def test_u02_intermediate_overflow_is_unavailable_despite_cancellation() -> None:
    rule = {'aggregate': {'fn': 'sum', 'of': '$value', 'over': ['$id'], 'as': '$sum'}, 'head': {'group': '$group', 'sum': '$sum'}}
    wide = (1 << 65536) - 1
    rows = [{'group': 'north', 'id': 'a', 'value': wide}, {'group': 'north', 'id': 'b', 'value': wide}, {'group': 'north', 'id': 'c', 'value': -wide}]
    for permutation in (rows, [rows[0], rows[2], rows[1]]):
        collapsed, unavailable = _aggregate_bindings(rule, permutation, _ExactJoinWork())
        assert collapsed == []
        assert unavailable is not None
        assert unavailable.reason == 'term:exact-value-too-wide'

def _collapsed(function: str, rows: list[dict], *, of: object='$value', over: list[str] | None=None, group: bool=True) -> list[dict]:
    rule = {'aggregate': {'fn': function, 'of': of, 'over': over or ['$id'], 'as': '$result'}, 'head': {**({'group': '$group'} if group else {}), 'result': '$result'}}
    collapsed, unavailable = _aggregate_bindings(rule, rows, _ExactJoinWork())
    assert unavailable is None
    return collapsed

def test_c01_c02_c03_c04_body_creates_only_nonempty_groups() -> None:
    rows = [{'group': 'north', 'id': 'one', 'value': 2}, {'group': 'south', 'id': 'two', 'value': 3}]
    assert _collapsed('count', rows) == [{'group': 'north', 'result': 1}, {'group': 'south', 'result': 1}]
    assert _collapsed('count', rows, group=False) == [{'result': 2}]
    assert _collapsed('count', []) == []
    assert _collapsed('count', [], group=False) == []

def test_c05_c06_duplicate_proofs_deduplicate_but_equal_values_do_not() -> None:
    first = {'group': 'north', 'id': 'one', 'value': 7}
    second = {'group': 'north', 'id': 'two', 'value': 7}
    assert _collapsed('sum', [first, first, second]) == [{'group': 'north', 'result': 14}]
    assert _collapsed('count', [first, first, second]) == [{'group': 'north', 'result': 2}]

def test_c08_over_order_is_preserved_in_contribution_identity(monkeypatch: pytest.MonkeyPatch) -> None:
    seen: list[object] = []
    original = checker._aggregate_identity_token

    def recording_token(value: object) -> bytes:
        seen.append(value)
        return original(value)
    monkeypatch.setattr(checker, '_aggregate_identity_token', recording_token)
    row = {'group': 'north', 'id': 'one', 'other': 'two', 'value': 7}
    assert _collapsed('count', [row], over=['$id', '$other'])[0]['result'] == 1
    assert seen == ['north', 'one', 'two', 7]
    seen.clear()
    assert _collapsed('count', [row], over=['$other', '$id'])[0]['result'] == 1
    assert seen == ['north', 'two', 'one', 7]

@pytest.mark.parametrize(('case_id', 'function', 'expected'), [('D01', 'count', 3), ('D02', 'sum', 3), ('D03', 'min', -2), ('D04', 'max', 4), ('D05', 'avg', 1)])
def test_d01_d05_all_functions_evaluate_negative_integer_rows(case_id, function, expected) -> None:
    rows = [{'group': 'north', 'id': 'one', 'value': -2}, {'group': 'north', 'id': 'two', 'value': 1}, {'group': 'north', 'id': 'three', 'value': 4}]
    assert _collapsed(function, rows) == [{'group': 'north', 'result': expected}], case_id

def test_d06_d07_d08_exact_wide_sum_order_and_string_count() -> None:
    rows = [{'group': 'z', 'id': 'one', 'value': 1 << 2048}, {'group': 'a', 'id': 'two', 'value': 3}]
    assert _collapsed('sum', rows) == [{'group': 'a', 'result': 3}, {'group': 'z', 'result': 1 << 2048}]
    assert _collapsed('count', rows, of='$group') == [{'group': 'a', 'result': 1}, {'group': 'z', 'result': 1}]

def test_d10_integer_aggregate_head_is_materialized_without_rounding() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    rows = structured_extension_facts(model, population)['scenario_sum']
    assert [dict(row) for row in rows] == [{'scenario': 'north', 'sum': 320}, {'scenario': 'south', 'sum': 180}]
    assert all(type(row['sum']) is int for row in rows)

def test_e01_e02_average_post_filter_has_true_and_false_groups() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    rows = structured_extension_facts(model, population)['scenario_mean_ok']
    assert [dict(row) for row in rows] == [{'scenario': 'north'}]
    assert 'south' not in [row['scenario'] for row in rows]

def test_e03_e04_average_is_exact_one_third() -> None:
    rows = [{'group': 'north', 'id': 'one', 'value': 0}, {'group': 'north', 'id': 'two', 'value': 0}, {'group': 'north', 'id': 'three', 'value': 1}]
    result = _collapsed('avg', rows)[0]['result']
    assert result == Fraction(1, 3)
    assert result != 1 / 3

def test_e05_native_float_division_mutant_changes_exact_average_identity() -> None:
    rows = [{'group': 'north', 'id': 'one', 'value': 0}, {'group': 'north', 'id': 'two', 'value': 0}, {'group': 'north', 'id': 'three', 'value': 1}]
    exact = _collapsed('avg', rows)[0]['result']
    native_division_mutant = sum(row['value'] for row in rows) / len(rows)
    assert exact == Fraction(1, 3)
    assert exact != native_division_mutant

def test_e07_e08_post_aggregate_where_order_controls_undefinedness() -> None:
    model_document = copy.deepcopy(document())
    count_rule = model_document['fact_types'][1]['derivation_rule']
    false = {'operator': '=', 'left': 0, 'right': 1}
    undefined = {'operator': '=', 'left': {'fn': 'mod', 'args': [1, 0]}, 'right': 0}
    count_rule['where'] = [false, undefined]
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    filtered = exact_extension_envelope(model, population)
    assert filtered['relations']['scenario_count'] == []
    assert 'scenario_count' not in filtered['unavailable']
    count_rule['where'] = [undefined, false]
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    unavailable = exact_extension_envelope(model, population)
    assert unavailable['unavailable']['scenario_count']['reason'] == 'term:mod-zero'
