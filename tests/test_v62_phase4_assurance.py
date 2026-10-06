from __future__ import annotations

import contextlib
import io
import json
from copy import deepcopy
from pathlib import Path

from ruamel.yaml import YAML
from support.v62_phase4_corpus import CASES_DOC, FIXTURE, document, population_document

import gnd.api as api_module
from gnd import checking_service
from gnd.assurance import (
    CorrespondenceDigests,
    _assurance_policy,
    derive_assurance_scope,
    phase3_scope_ids,
)
from gnd.assurance_evidence import AuthenticatedAssuranceEvidence
from gnd.checker import check
from gnd.cli import main
from gnd.model import Model
from gnd.population import load_population, load_population_bytes
from gnd.semantic_registry import applicable_scope_ids, branch, capture_branches

AGGREGATE_EVENTS = {'aggregate-applied': 'applied', 'aggregate-group-absent': 'filtered', 'aggregate-post-filter-false': 'filtered', 'aggregate-unavailable-origin': 'unchecked', 'aggregate-unavailable-propagated': 'unchecked'}


def test_k08_aggregate_execution_branches_are_registered_and_applicable() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    applicable = set(applicable_scope_ids(model, population))
    for event, outcome in AGGREGATE_EVENTS.items():
        scope_id = f'derivation:extension:derived:{event}'
        row = branch(scope_id)
        assert row.outcome == outcome
        assert row.production_owner == 'gnd.checker._exact_extension_calculator'
        assert scope_id in applicable
    for event in ('pass', 'fail', 'unchecked'):
        scope_id = f'snapshot:guarded:aggregate:{event}'
        assert branch(scope_id).outcome == event
        assert scope_id in applicable

def test_k08_w01_w02_w03_aggregate_guarded_pass_fail_unchecked_are_real_trace_events() -> None:
    for mode, expected in (('pass', 'snapshot:guarded:aggregate:pass'), ('fail', 'snapshot:guarded:aggregate:fail'), ('unchecked', 'snapshot:guarded:aggregate:unchecked')):
        model_document = deepcopy(document())
        if mode == 'fail':
            model_document['constraints'][0]['consequent']['comparison']['right'] = 3
        elif mode == 'unchecked':
            model_document['fact_types'][1]['derivation_rule']['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
        model = Model.model_validate(model_document)
        population = load_population(FIXTURE / CASES_DOC['population'], model=model)
        with capture_branches() as reached:
            check(model, population)
        assert expected in reached

def test_k08_aggregate_group_absent_and_filter_false_are_real_trace_events() -> None:
    model = Model.model_validate(document())
    empty_document = population_document()
    empty_document['facts']['observation'] = []
    population = load_population_bytes(json.dumps(empty_document).encode(), source='empty-aggregate.json', model=model)
    with capture_branches() as reached:
        check(model, population)
    assert 'derivation:extension:derived:aggregate-group-absent' in reached
    populated = load_population(FIXTURE / CASES_DOC['population'], model=model)
    with capture_branches() as reached:
        check(model, populated)
    assert 'derivation:extension:derived:aggregate-post-filter-false' in reached
    assert 'derivation:extension:derived:aggregate-applied' in reached

def test_k08_aggregate_origin_and_propagation_are_distinct_trace_events() -> None:
    model_document = deepcopy(document())
    count_rule = model_document['fact_types'][1]['derivation_rule']
    count_rule['aggregate']['of'] = {'fn': 'mod', 'args': [1, 0]}
    sum_rule = model_document['fact_types'][2]['derivation_rule']
    sum_rule['body'] = [{'fact_type': 'scenario_count', 'bind': {'scenario': '$scenario', 'count': '$count'}}]
    sum_rule['aggregate'] = {'fn': 'sum', 'of': '$count', 'over': ['$scenario'], 'as': '$sum'}
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    with capture_branches() as reached:
        check(model, population)
    assert 'derivation:extension:derived:aggregate-unavailable-origin' in reached
    assert 'derivation:extension:derived:aggregate-unavailable-propagated' in reached

def test_k06_mixed_covered_predecessor_and_uncovered_aggregate_is_partial() -> None:
    model = Model.model_validate(document())
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    applicable = frozenset(applicable_scope_ids(model, population))
    aggregate = frozenset(scope for scope in applicable if ':aggregate-' in scope)
    covered = applicable - aggregate
    assert aggregate and covered
    assert _assurance_policy(applicable, covered, required=frozenset(), proved_infrastructure=frozenset(), guards_valid=True) == 'partial'

def test_k06_public_check_reports_exact_mixed_aggregate_scope(monkeypatch) -> None:
    model_path = FIXTURE / CASES_DOC['model']
    population_path = FIXTURE / CASES_DOC['population']
    baseline = api_module._run_check_raw(model_path, population_path)
    assert baseline.execution is not None
    scope = derive_assurance_scope(baseline.execution, consumer='report')
    aggregate = {scope_id for scope_id in scope.applicable_scope_ids if ':aggregate-' in scope_id}
    legacy_scope = next(scope_id for scope_id in sorted(scope.applicable_scope_ids) if scope_id not in aggregate)
    covered = frozenset({legacy_scope, *scope.required_infrastructure_ids})
    evidence = object.__new__(AuthenticatedAssuranceEvidence)
    for name, value in {'available': True, 'covered_scope_ids': covered, 'declared_scope_ids': covered, 'digests': CorrespondenceDigests(scope_digest='1' * 64, semantics_digest='2' * 64, production_roster_digest=baseline.execution.production_roster_digest, proof_digest='3' * 64, toolchain_digest='4' * 64), 'assumptions': (), 'reason': None}.items():
        object.__setattr__(evidence, name, value)
    monkeypatch.setattr(checking_service, 'load_assurance_evidence', lambda: evidence)
    payload = api_module.check(model_path, population_path, unredacted=True)
    assurance = payload['assurance']
    assert aggregate
    assert assurance['assurance_level'] == 'partial'
    assert assurance['uncovered_applicable_scope_ids'] == sorted(set(scope.applicable_scope_ids) - covered)
    assert legacy_scope not in assurance['uncovered_applicable_scope_ids']

def test_w04_guarded_failure_witness_has_only_group_and_aggregate_value() -> None:
    model_document = deepcopy(document())
    model_document['constraints'][0]['consequent']['comparison']['right'] = 3
    model = Model.model_validate(model_document)
    population = load_population(FIXTURE / CASES_DOC['population'], model=model)
    report = check(model, population)
    failure = next(row for row in report.verdicts if row.constraint_ref == 'constraints[0]')
    assert failure.verdict == 'fail'
    assert failure.offending_facts == [{'$scenario': 'north', '$count': 3}, {'$scenario': 'south', '$count': 1}]
    assert 'SECRET-AGGREGATE-271828' not in str(failure)

def test_w05_guarded_witness_text_json_agree_without_contributors(tmp_path: Path) -> None:
    model_document = deepcopy(document())
    model_document['constraints'][0]['consequent']['comparison']['right'] = 3
    model_path = tmp_path / 'aggregate-failure.orm.yaml'
    with model_path.open('w', encoding='utf-8') as stream:
        YAML().dump(model_document, stream)
    outputs: dict[str, str] = {}
    for output_format in ('text', 'json'):
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            assert main(['check', str(model_path), str(FIXTURE / CASES_DOC['population']), '--format', output_format]) == 1
        outputs[output_format] = stream.getvalue()
    parsed = json.loads(outputs['json'])
    witness = next(row for row in parsed['verdicts'] if row['constraint_ref'] == 'constraints[0]')
    assert witness['verdict'] == 'fail'
    assert witness['offending_facts'] == [{'$scenario': 'north', '$count': 3}, {'$scenario': 'south', '$count': 1}]
    for output in outputs.values():
        assert 'north' in output and 'south' in output
        assert 'north-1' not in output
        assert 'SECRET-AGGREGATE-271828' not in output

def test_current_correspondence_scope_excludes_aggregate_branches() -> None:
    assert not any(":aggregate:" in scope_id for scope_id in phase3_scope_ids())
