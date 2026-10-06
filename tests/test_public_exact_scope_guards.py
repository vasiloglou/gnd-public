from __future__ import annotations

from support.v62_phase3_corpus import FIXTURE

import gnd.api as api_module
from gnd import checking_service
from gnd.assurance import CorrespondenceDigests, _assurance_policy, derive_assurance_scope
from gnd.assurance_evidence import AuthenticatedAssuranceEvidence
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_registry import applicable_scope_ids, branch


def test_operation_without_dynamic_rules_owes_no_dynamic_rule_scope() -> None:
    model = load_model(FIXTURE / 'models/exact-terms.orm.yaml')
    population = load_population(FIXTURE / 'populations/term-clean.pop.yaml', model=model)
    assert not any(scope_id.startswith('transition:dynamic-rule:') for scope_id in applicable_scope_ids(model, population))

def test_exact_success_false_and_transitive_routes_are_distinct_applicable_identities() -> None:
    model = load_model(FIXTURE / 'models/exact-terms.orm.yaml')
    population = load_population(FIXTURE / 'populations/term-clean.pop.yaml', model=model)
    scopes = set(applicable_scope_ids(model, population))
    assert {'derivation:extension:derived:exact-applied', 'derivation:extension:derived:exact-where-false', 'derivation:extension:derived:exact-head-computed', 'derivation:extension:derived:exact-origin-propagated', 'snapshot:guarded:comparison:exact-success'} <= scopes

def test_exact_execution_rows_pin_declared_metadata_vocabulary() -> None:
    expected = {'exact-applied': 'applied', 'exact-where-false': 'filtered', 'exact-head-computed': 'projected', 'exact-origin-propagated': 'unchecked'}
    for event, outcome in expected.items():
        row = branch(f'derivation:extension:derived:{event}')
        assert row.obligation_kind == 'execution'
        assert row.semantic_branch == event
        assert row.outcome == outcome
        assert row.production_owner == 'gnd.checker._exact_extension_calculator'

def test_mixed_legacy_coverage_plus_exact_uncovered_is_partial_never_proof_backed() -> None:
    model = load_model(FIXTURE / 'models/exact-terms.orm.yaml')
    population = load_population(FIXTURE / 'populations/term-clean.pop.yaml', model=model)
    applicable = frozenset(applicable_scope_ids(model, population))
    exact = frozenset(scope_id for scope_id in applicable if scope_id.startswith('derivation:extension:') and ':exact-' in scope_id)
    covered = applicable - exact
    assert exact and covered
    assert _assurance_policy(applicable, covered, required=frozenset(), proved_infrastructure=frozenset(), guards_valid=True) == 'partial'

def test_k06_authenticated_mixed_result_is_partial_never_proof_backed(monkeypatch) -> None:
    model_path = FIXTURE / 'models/exact-terms.orm.yaml'
    population_path = FIXTURE / 'populations/term-clean.pop.yaml'
    baseline = api_module._run_check_raw(model_path, population_path)
    assert baseline.execution is not None
    scope = derive_assurance_scope(baseline.execution, consumer='report')
    legacy_scope = next(scope_id for scope_id in sorted(scope.applicable_scope_ids) if ':exact-' not in scope_id and (not scope_id.endswith(':exact-success')))
    covered = frozenset({legacy_scope, *scope.required_infrastructure_ids})
    evidence = object.__new__(AuthenticatedAssuranceEvidence)
    for name, value in {'available': True, 'covered_scope_ids': covered, 'declared_scope_ids': covered, 'digests': CorrespondenceDigests(scope_digest='1' * 64, semantics_digest='2' * 64, production_roster_digest=baseline.execution.production_roster_digest, proof_digest='3' * 64, toolchain_digest='4' * 64), 'assumptions': (), 'reason': None}.items():
        object.__setattr__(evidence, name, value)
    monkeypatch.setattr(checking_service, 'load_assurance_evidence', lambda: evidence)
    payload = api_module.check(model_path, population_path, unredacted=True)
    assert payload['assurance']['assurance_level'] == 'partial'
    assert payload['assurance']['assurance_level'] != 'proof-backed'
    assert payload['assurance']['uncovered_applicable_scope_ids']
