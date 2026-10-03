from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd.exp.session_eval import VerifierPayloadError, validate_verifier_payload

CORPUS = Path(__file__).parent / 'fixtures' / 'phase3-consumers'
CANDIDATE = 'a' * 64
CONTRACT = 'b' * 64

def _raw(name: str) -> bytes:
    return (CORPUS / name).read_bytes()

def _validate(raw: bytes, *, subject: str, process_exit: int, expected_version: int):
    return validate_verifier_payload(raw, case_id='eligibility-derivation', role='required', process_exit=process_exit, expected_command='check', expected_subject=subject, expected_model='eligibility.orm.yaml', candidate_sha256=CANDIDATE, contract_sha256=CONTRACT, evidence_candidate_sha256=CANDIDATE, evidence_contract_sha256=CONTRACT) if expected_version is None else validate_verifier_payload(raw, case_id='eligibility-derivation', role='required', process_exit=process_exit, expected_command='check', expected_subject=subject, expected_model='eligibility.orm.yaml', candidate_sha256=CANDIDATE, contract_sha256=CONTRACT, evidence_candidate_sha256=CANDIDATE, evidence_contract_sha256=CONTRACT, expected_schema_version=expected_version)

def test_a_derivation_only_band_one_payload_validates_with_the_block() -> None:
    raw = _raw('check-v4.incomplete.payload.json')
    evaluation = _validate(raw, subject='eligibility.incomplete.population.yaml', process_exit=1, expected_version=4)
    assert evaluation.payload_exit == 1
    assert evaluation.counts['fail'] == 1
    assert evaluation.verdicts == ()
    row, = evaluation.derivation_feedback
    assert row.kind == 'derived-extension-incomplete'

def test_the_exact_payload_validates_and_carries_no_repair_rows() -> None:
    evaluation = _validate(_raw('check-v4.exact.payload.json'), subject='eligibility.exact.population.yaml', process_exit=0, expected_version=4)
    assert evaluation.acceptance_ready
    assert evaluation.derivation_feedback == ()

def test_version_mismatch_is_refused_in_both_directions() -> None:
    with pytest.raises(VerifierPayloadError, match='must be current version 3'):
        _validate(_raw('check-v4.exact.payload.json'), subject='eligibility.exact.population.yaml', process_exit=0, expected_version=3)
    v3_payload = json.loads(_raw('check-v4.exact.payload.json'))
    v3_payload['schema_version'] = 3
    del v3_payload['derivations']
    with pytest.raises(VerifierPayloadError, match='must be current version 4'):
        _validate(json.dumps(v3_payload).encode('utf-8'), subject='eligibility.exact.population.yaml', process_exit=0, expected_version=4)

def test_exit_three_must_not_carry_derivation_obligations() -> None:
    payload = json.loads(_raw('check-v4.incomplete.payload.json'))
    payload['exit_code'] = 3
    payload['outcome'] = 'ill_formed'
    payload['acceptance_ready'] = False
    payload['counts'] = {'pass': 0, 'fail': 0, 'warning': 0, 'unchecked': 0, 'vacuous': 0}
    payload['verdicts'] = []
    payload['coverage'] = {}
    payload['issues'] = [{'rule_id': 'population:type-mismatch', 'severity': 'error', 'path': '$.facts', 'message': 'synthetic'}]
    payload['issues_total'] = 1
    with pytest.raises(VerifierPayloadError, match='must not carry derivation obligations'):
        _validate(json.dumps(payload).encode('utf-8'), subject='eligibility.incomplete.population.yaml', process_exit=3, expected_version=4)

def test_a_malformed_derivation_ref_is_refused_at_the_schema() -> None:
    payload = json.loads(_raw('check-v4.incomplete.payload.json'))
    payload['derivations'][0]['derivation_ref'] = 'fact_type:book_is_eligible'
    raw = json.dumps(payload).encode('utf-8')
    with pytest.raises(VerifierPayloadError) as caught:
        _validate(raw, subject='eligibility.incomplete.population.yaml', process_exit=1, expected_version=4)
    assert any('derivation' in issue for issue in caught.value.issues)

@pytest.mark.parametrize('version', [4, 6])
def test_a_structured_result_with_an_erased_derivations_block_is_refused(version: int) -> None:
    payload = json.loads(_raw('check-v4.exact.payload.json'))
    payload['derivations'] = []
    payload['counts'] = {'pass': 0, 'fail': 0, 'warning': 0, 'unchecked': 0, 'vacuous': 0}
    if version == 6:
        payload['schema_version'] = 6
        payload['model_digest'] = 'sha256:' + 'a' * 64
    with pytest.raises(VerifierPayloadError, match='at least one derivation obligation'):
        _validate(json.dumps(payload).encode('utf-8'), subject='eligibility.exact.population.yaml', process_exit=0, expected_version=version)

def test_exit_seventy_must_not_carry_derivation_obligations() -> None:
    payload = json.loads(_raw('check-v4.incomplete.payload.json'))
    payload['exit_code'] = 70
    payload['outcome'] = 'internal_error'
    payload['acceptance_ready'] = False
    payload['counts'] = {'pass': 0, 'fail': 0, 'warning': 0, 'unchecked': 0, 'vacuous': 0}
    payload['verdicts'] = []
    payload['coverage'] = {}
    payload['error'] = {'type': 'RuntimeError', 'message': 'synthetic'}
    with pytest.raises(VerifierPayloadError, match='must not carry derivation obligations'):
        _validate(json.dumps(payload).encode('utf-8'), subject='eligibility.incomplete.population.yaml', process_exit=70, expected_version=4)
