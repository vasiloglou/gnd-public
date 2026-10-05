from __future__ import annotations

import json

import pytest
from support.v62_phase4_corpus import CASES_DOC, FIXTURE, document, population_document

from gnd.checker import band as check_band
from gnd.checker import check, exact_extension_envelope, structured_extension_view
from gnd.model import Model, derivation_classifications, load_model, semantic_validate
from gnd.population import load_population, load_population_bytes
from gnd.transition import (
    band,
    evaluate,
    evaluate_plan,
    model_digest,
    operations_digest,
    read_steps_document,
    validate_steps,
)


def _dynamic_model() -> Model:
    model_document = document()
    model_document['operations'].append({'id': 'add_sample', 'reading': 'add a sample', 'parameters': [{'name': 'scenario', 'object_type': 'scenario'}, {'name': 'sample', 'object_type': 'sample'}, {'name': 'rb', 'object_type': 'integer'}], 'effects': [{'assert': {'fact_type': 'observation', 'bind': {'scenario': '$scenario', 'sample': '$sample', 'rb': '$rb'}}}], 'frame': {'modality': 'alethic'}, 'source': 'user-supplied', 'status': 'confirmed', 'provenance': {'user_quote': 'A sample can be added.'}})
    assert semantic_validate(model_document) == []
    return Model.model_validate(model_document)

def _add_sample_steps(model: Model) -> list[dict]:
    return validate_steps({'steps_schema': 1, 'model': 'aggregates.orm.yaml', 'model_digest': model_digest(model), 'operations_digest': operations_digest(model.operations), 'steps': [{'op': 'add_sample', 'bindings': {'scenario': 'north', 'sample': 'north-4', 'rb': 80}}]}, model)

def test_f01_f03_t01_static_aggregate_is_ready_before_precondition() -> None:
    model = load_model(FIXTURE / CASES_DOC['model'])
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    classifications = {row.fact_type: row.stability for row in derivation_classifications(model.model_dump())}
    assert classifications['scenario_mean_ok'] == 'static'
    steps = validate_steps(read_steps_document(FIXTURE / CASES_DOC['steps']), model)
    result = evaluate_plan(model, population, steps)
    assert band(result.report) == 0
    assert result.report.steps[0].verdicts == []
    assert result.computed_post['facts']['scenario_acceptance'] == [{'scenario': 'north'}]

def test_f04_t02_t04_t06_t07_t08_dynamic_aggregate_recomputes_grounded_delta_before_checks() -> None:
    model = _dynamic_model()
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    classifications = {row.fact_type: row.stability for row in derivation_classifications(model.model_dump())}
    assert classifications['scenario_count'] == 'dynamic'
    assert classifications['scenario_sum'] == 'dynamic'
    result = evaluate_plan(model, population, _add_sample_steps(model))
    assert band(result.report) == 0
    changes = {change.fact_type: change for change in result.report.steps[0].derived_changes}
    assert changes['scenario_count'].added == [{'scenario': 'north', 'count': 4}]
    assert changes['scenario_count'].removed == [{'scenario': 'north', 'count': 3}]
    assert changes['scenario_sum'].added == [{'scenario': 'north', 'sum': 400}]
    assert changes['scenario_sum'].removed == [{'scenario': 'north', 'sum': 320}]
    assert not [verdict for verdict in result.report.steps[0].verdicts if verdict.kind == 'frame']
    assert not {'scenario_count', 'scenario_sum'}.intersection(result.computed_post['facts'])
    assert result.computed_post['facts']['observation'][-1] == {'rb': 80, 'sample': 'north-4', 'scenario': 'north'}
    assert 'scenario_count' not in result.computed_post['facts']
    assert 'scenario_sum' not in result.computed_post['facts']
    assert {change.fact_type for change in result.report.steps[0].derived_changes} >= {'scenario_count', 'scenario_sum'}
    assert not any(verdict.kind == 'derived-change' for verdict in result.report.steps[0].verdicts)
    assert any(row.derivation_ref == 'derivation:scenario_count' for row in result.report.post_snapshot.derivations)

def test_t03_selective_refresh_names_aggregate_heads_and_preserves_untouched() -> None:
    model = _dynamic_model()
    before = load_population(FIXTURE / CASES_DOC['population'], model=model)
    initial = structured_extension_view(model, before)
    after_document = population_document()
    after_document['facts']['observation'].append({'scenario': 'north', 'sample': 'north-4', 'rb': 80})
    after = load_population_bytes(json.dumps(after_document).encode(), source='after-aggregate.json', model=model)
    refreshed = structured_extension_view(model, after, previous=initial.facts, refresh=('scenario_count', 'scenario_sum'))
    assert refreshed.recomputed == ('scenario_count', 'scenario_sum')
    assert refreshed.facts['scenario_count'] == ({'scenario': 'north', 'count': 4}, {'scenario': 'south', 'count': 1})
    assert refreshed.facts['scenario_sum'] == ({'scenario': 'north', 'sum': 400}, {'scenario': 'south', 'sum': 180})
    assert refreshed.facts['scenario_min'] == initial.facts['scenario_min']
    assert refreshed.work.selected_heads == 2

def test_t05_semiderived_authored_aggregate_surplus_is_inert() -> None:
    model_document = document()
    model_document['fact_types'][1]['derivation'] = 'semiderived'
    model = Model.model_validate(model_document)
    population_document_ = population_document()
    population_document_['facts']['scenario_count'].append({'scenario': 'north', 'count': 999})
    population = load_population_bytes(json.dumps(population_document_).encode(), source='surplus-aggregate.json', model=model)
    view = structured_extension_view(model, population)
    assert view.facts['scenario_count'] == ({'scenario': 'north', 'count': 3}, {'scenario': 'south', 'count': 1})

def _undefined_count_model() -> Model:
    model_document = document()
    model_document['fact_types'][1]['derivation_rule']['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
    return Model.model_validate(model_document)

def test_u01_u03_u05_unavailable_origin_reaches_claim_and_guarded_constraint() -> None:
    model = _undefined_count_model()
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    envelope = exact_extension_envelope(model, population)
    assert envelope['unavailable']['scenario_count']['reason'] == 'term:mod-zero'
    report = check(model, population)
    assert check_band(report) == 4
    assert ('derivation:scenario_count', 'unchecked', 'term:mod-zero') in {(row.derivation_ref, row.verdict, row.reason_code) for row in report.derivations}
    assert ('constraints[0]', 'unchecked', 'term:mod-zero') in {(row.constraint_ref, row.verdict, row.reason_code) for row in report.verdicts}

def test_u04_upper_aggregate_keeps_origin_and_source_relation() -> None:
    model_document = document()
    count_rule = model_document['fact_types'][1]['derivation_rule']
    count_rule['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
    sum_rule = model_document['fact_types'][2]['derivation_rule']
    sum_rule['body'] = [{'fact_type': 'scenario_count', 'bind': {'scenario': '$scenario', 'count': '$count'}}]
    sum_rule['aggregate'] = {'fn': 'sum', 'of': '$count', 'over': ['$scenario'], 'as': '$sum'}
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    envelope = exact_extension_envelope(model, population)
    upper = envelope['unavailable']['scenario_sum']
    assert upper['reason'] == 'term:mod-zero'
    assert upper['source_relation'] == 'scenario_count'

def test_u06_u08_u09_unavailable_average_precondition_and_snapshots_are_unchecked() -> None:
    model_document = document()
    model_document['fact_types'][5]['derivation_rule']['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    steps = validate_steps(read_steps_document(FIXTURE / CASES_DOC['steps']), model)
    result = evaluate_plan(model, population, steps)
    assert band(result.report) == 4
    assert ('unchecked', 'term:mod-zero') in {(verdict.verdict, verdict.reason_code) for step in result.report.steps for verdict in step.verdicts if verdict.kind == 'precondition'}
    declared = evaluate(model, population, population, steps)
    assert declared.post_snapshot is not None
    assert ('unchecked', 'term:mod-zero') in {(row.verdict, row.reason_code) for row in declared.post_snapshot.derivations}

def test_u10_selective_refresh_never_reinterprets_prior_unavailable_as_empty() -> None:
    model = _undefined_count_model()
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    baseline = structured_extension_view(model, population)
    assert baseline.unavailable['scenario_count'].reason == 'term:mod-zero'
    refreshed = structured_extension_view(model, population, previous=baseline.facts, previous_unavailable=baseline.unavailable, refresh=('scenario_sum',))
    assert refreshed.unavailable['scenario_count'] == baseline.unavailable['scenario_count']
    with pytest.raises(ValueError, match='requires previous_unavailable'):
        structured_extension_view(model, population, previous=baseline.facts, refresh=('scenario_sum',))

def test_u07_dynamic_aggregate_unavailability_reaches_intermediate_snapshot() -> None:
    model_document = _dynamic_model().model_dump(exclude={'warnings'})
    model_document['fact_types'][1]['derivation_rule']['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
    model = Model.model_validate(model_document)
    assert {row.fact_type: row.stability for row in derivation_classifications(model.model_dump())}['scenario_count'] == 'dynamic'
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    result = evaluate_plan(model, population, _add_sample_steps(model))
    assert band(result.report) == 4
    assert ('constraints[0]', 'unchecked', 'term:mod-zero') in {(row.constraint_ref, row.verdict, row.reason_code) for row in result.report.steps[0].intermediate.verdicts}
