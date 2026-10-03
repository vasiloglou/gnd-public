"""Feedback v4 is separate from frozen projections and from authenticity."""
import json
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

from gnd.assurance import AssuranceBlockV1
from gnd.exp.session_contract import SessionCase
from gnd.exp.session_eval import (
    AssuranceFeedback,
    AttemptEvaluation,
    CaseEvaluation,
    CaseFeedbackV4,
    _case_feedback,
    normalized_verifier_signature,
)
from gnd.exp.session_store import _retained_wire
from gnd.report import CurrentReportVersion

CORPUS = Path(__file__).resolve().parent / 'fixtures/v6-assurance'

def fixture_case(semantic=False):
    case = json.loads((CORPUS / 'legacy-feedback/case.json').read_text())
    if semantic:
        case['acceptance'] = {'mode': 'constraint-satisfaction', 'coverage': [{'fact_type': 'expense', 'min_facts': 1}]}
        case.pop('expected_outputs')
    return SessionCase.model_validate(case)

def evaluation():
    return CaseEvaluation.model_validate_json((CORPUS / 'legacy-feedback/evaluation.json').read_bytes())

def test_nonsemantic_feedback_has_an_explicit_null():
    row = _case_feedback(evaluation(), case=fixture_case(), schema_version=4)
    assert isinstance(row, CaseFeedbackV4)
    assert row.model_dump(mode='json')['assurance'] is None
    legacy = _case_feedback(evaluation(), case=fixture_case(), schema_version=3).model_dump(mode='json')
    assert {k: v for k, v in row.model_dump(mode='json').items() if k != 'assurance'} == legacy

def test_semantic_feedback_never_authenticates_an_imported_evaluation():
    row = _case_feedback(evaluation(), case=fixture_case(True), schema_version=4)
    assert row.assurance.model_dump(mode='json') == AssuranceBlockV1('accept').as_dict()

def test_legacy_feedback_refuses_an_assurance_key():
    from gnd.exp.session_eval import CaseFeedbackV3
    legacy = _case_feedback(evaluation(), case=fixture_case(), schema_version=3).model_dump(mode='json')
    legacy['assurance'] = AssuranceBlockV1('accept').as_dict()
    with pytest.raises(ValidationError):
        CaseFeedbackV3.model_validate(legacy)

def test_imported_badge_checks_relations_without_minting_capabilities():
    wire = AssuranceBlockV1('accept').as_dict()
    parsed = AssuranceFeedback.model_validate(wire)
    assert parsed.assurance_level == 'none'
    with pytest.raises(ValidationError):
        AssuranceFeedback.model_validate({**wire, 'assurance_level': 'proof-backed'})

@pytest.mark.parametrize('model_version,allowed', [(5, {3, 5, 7}), (6, {4, 6, 7})])
def test_current_session_retained_versions_are_selected_by_the_model(model_version, allowed):
    expected = CurrentReportVersion(model_version)
    for candidate in (3, 4, 5, 6, 7, True, 7.0):
        selected = _retained_wire(json.dumps({'schema_version': candidate}).encode(), {'case': expected}, 'case')
        assert selected == (candidate if type(candidate) is int and candidate in allowed else 7)
    assert _retained_wire(b'{"schema_version":5}', {'case': 7}, 'case') == 7

def live_execution(surface):
    from gnd import assurance, checker, report, transition
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.semantic_registry import capture_branches
    domain = {'snapshot': 'expense-approval', 'derivation': 'recommendation-completeness', 'transition': 'separation-of-duties'}[surface]
    root = CORPUS / 'cases' / domain / 'conforming'
    model = load_model(root / 'model.orm.yaml')
    steps = None
    with capture_branches() as trace:
        if surface == 'transition':
            populations = [load_population(root / name, model=model) for name in ('pre.json', 'post.json')]
            steps = transition.validate_steps(transition.read_steps_document(root / 'steps.json'), model)
            result = transition.evaluate(model, *populations, steps)
            band = transition.band(result)
            report.build_transition_payload(band, 'model.orm.yaml', evaluated=True, transition_report=result, schema_version=7)
        else:
            populations = [load_population(root / 'population.json', model=model)]
            result = checker.check(model, populations[0])
            band = checker.band(result)
            report.build_check_payload(band, 'model.orm.yaml', 'population.json', report=result, schema_version=7, structured=surface == 'derivation')
    return assurance._mint_execution(model, populations, result, band, trace, steps=steps)

def test_proof_availability_never_changes_the_retry_signature(monkeypatch):
    from types import SimpleNamespace

    from test_v6_phase6_execution import synthetic_evidence

    from gnd import assurance, assurance_evidence
    from gnd.exp.session_eval import AttemptEvaluation, normalized_verifier_signature
    case = fixture_case(True)
    result = evaluation()
    execution = live_execution('snapshot')
    result.__pydantic_private__['_assurance_execution'] = execution
    result.__pydantic_private__['_assurance_binding'] = (result.case_id, result.candidate_sha256, result.contract_sha256, result.raw_payload_sha256, result.payload_exit)
    attempt = AttemptEvaluation(attempt_index=1, candidate_sha256=result.candidate_sha256, contract_sha256=result.contract_sha256, results=(result,))
    contract = SimpleNamespace(cases=(case,))
    scope = assurance.derive_assurance_scope(execution, consumer='feedback')
    samples = [('proof-backed', synthetic_evidence(scope)), ('partial', synthetic_evidence(scope, coverage=[min(scope.applicable_scope_ids)])), ('none', assurance_evidence._capability())]
    signatures = set()
    business_rows = []
    for level, evidence in samples:
        monkeypatch.setattr(assurance_evidence, 'load_assurance_evidence', lambda evidence=evidence: evidence)
        row = _case_feedback(result, case=case, schema_version=4)
        assert row.assurance.assurance_level == level
        business_rows.append(row.model_dump(mode='json', exclude={'assurance'}))
        signatures.add(normalized_verifier_signature(contract, attempt, schema_version=4))
    assert len(signatures) == 1
    assert business_rows[0] == business_rows[1] == business_rows[2]

@pytest.fixture(autouse=True)
def _owned_feedback_helper_alias(request, monkeypatch):
    if request.node.name == 'test_feedback_v5_signature_excludes_assurance':
        monkeypatch.setitem(sys.modules, 'test_v6_phase6_feedback', sys.modules[__name__])


def test_feedback_v5_signature_excludes_assurance(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace

    from test_v6_phase6_execution import synthetic_evidence
    from test_v6_phase6_feedback import evaluation, fixture_case, live_execution

    from gnd import assurance, assurance_evidence
    case = fixture_case(True)
    result = evaluation()
    execution = live_execution('snapshot')
    result.__pydantic_private__['_assurance_execution'] = execution
    result.__pydantic_private__['_assurance_binding'] = (result.case_id, result.candidate_sha256, result.contract_sha256, result.raw_payload_sha256, result.payload_exit)
    attempt = AttemptEvaluation(attempt_index=1, candidate_sha256=result.candidate_sha256, contract_sha256=result.contract_sha256, results=(result,))
    contract = SimpleNamespace(cases=(case,))
    scope = assurance.derive_assurance_scope(execution, consumer='feedback')
    signatures = set()
    for evidence in (synthetic_evidence(scope), assurance_evidence._capability()):
        monkeypatch.setattr(assurance_evidence, 'load_assurance_evidence', lambda evidence=evidence: evidence)
        signatures.add(normalized_verifier_signature(contract, attempt, schema_version=5))
    assert len(signatures) == 1
