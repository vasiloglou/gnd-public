from __future__ import annotations

from support.v62_phase4_corpus import CASES_DOC, FIXTURE, document

from gnd.checker import structured_extension_facts
from gnd.model import Model
from gnd.population import load_population
from gnd.redaction import RedactionPolicy, _project_transition


def test_r01_tainted_of_reaches_aggregate_value_only() -> None:
    policy = RedactionPolicy.from_model(Model.model_validate(document()))
    assert ('scenario_sum', 'sum') in policy.effective_roles
    assert ('scenario_sum', 'scenario') not in policy.effective_roles

def test_r02_tainted_over_reaches_aggregate_value() -> None:
    model_document = document()
    for role in model_document['fact_types'][0]['roles']:
        role['redact'] = role['role_name'] == 'sample'
    policy = RedactionPolicy.from_model(Model.model_validate(model_document))
    assert ('scenario_count', 'count') in policy.effective_roles

def test_r03_sensitive_group_key_taints_aggregate_value() -> None:
    model_document = document()
    observation = model_document['fact_types'][0]
    for role in observation['roles']:
        role['redact'] = role['role_name'] == 'scenario'
    policy = RedactionPolicy.from_model(Model.model_validate(model_document))
    assert ('scenario_count', 'scenario') in policy.effective_roles
    assert ('scenario_count', 'count') in policy.effective_roles

def test_r04_post_aggregate_where_implicitly_taints_emitted_group_role() -> None:
    policy = RedactionPolicy.from_model(Model.model_validate(document()))
    assert ('scenario_mean_ok', 'scenario') in policy.effective_roles

def test_r05_aggregate_taint_reaches_upper_stratum_fixed_point() -> None:
    model_document = document()
    model_document['fact_types'].append({'id': 'accepted_summary', 'reading': '{Scenario} has an accepted summary', 'roles': [{'object_type': 'scenario', 'role_name': 'scenario'}], 'derivation': 'derived', 'derivation_rule': {'body': [{'fact_type': 'scenario_mean_ok', 'bind': {'scenario': '$scenario'}}], 'head': {'scenario': '$scenario'}}})
    policy = RedactionPolicy.from_model(Model.model_validate(model_document))
    assert ('scenario_mean_ok', 'scenario') in policy.effective_roles
    assert ('accepted_summary', 'scenario') in policy.effective_roles

def test_r06_real_groups_stay_distinct_before_projection() -> None:
    model_document = document()
    for role in model_document['fact_types'][0]['roles']:
        role['redact'] = role['role_name'] == 'scenario'
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    rows = [dict(row) for row in structured_extension_facts(model, population)['scenario_count']]
    assert rows == [{'scenario': 'north', 'count': 3}, {'scenario': 'south', 'count': 1}]
    payload = {'computed_post': {'facts': {'scenario_count': rows}}}
    _project_transition(payload, RedactionPolicy.from_model(model))
    projected = payload['computed_post']['facts']['scenario_count']
    assert len(projected) == 2
    assert {row['count']['redacted'] for row in projected} == {True}
    assert 'north' not in str(projected) and 'south' not in str(projected)

def test_r07_public_group_role_stays_public_when_only_of_is_sensitive() -> None:
    policy = RedactionPolicy.from_model(Model.model_validate(document()))
    assert ('scenario_sum', 'scenario') not in policy.effective_roles
