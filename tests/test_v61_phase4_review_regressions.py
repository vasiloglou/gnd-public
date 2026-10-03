from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

import gnd.api
from gnd.exp.session_eval import VerifierPayloadError, validate_verifier_payload
from gnd.model import load_model
from gnd.report import load_report_schema

ROOT = Path(__file__).resolve().parents[1]
PHASE4 = ROOT / 'tests/fixtures/v61-phase4'
SETFAM = ROOT / 'tests/fixtures/checker'

def test_top_level_constraint_witness_is_redacted_and_schema_valid() -> None:
    model = load_model(SETFAM / 'setfam.orm.yaml')
    fact_type = next(row for row in model.fact_types if row['id'] == 'booking_of_room')
    next(role for role in fact_type['roles'] if role['role_name'] == 'room')['redact'] = True
    payload = gnd.api.check(model, SETFAM / 'population.setfam_fail.yaml')
    verdict = next(row for row in payload['verdicts'] if row['constraint_ref'] == 'constraints[0]')
    encoded = json.dumps(verdict, allow_nan=False, sort_keys=True)
    assert payload['schema_version'] == 9
    assert 'R1' not in encoded
    Draft202012Validator(load_report_schema()).validate(payload)

def test_malformed_parent_binding_container_is_redacted(tmp_path: Path) -> None:
    canary = 'P4_SECRET_BINDING_ONLY'
    steps = json.loads((PHASE4 / 'steps/binding-only.json').read_text(encoding='utf-8'))
    steps['steps'][0]['bindings'] = [canary]
    api_payload = gnd.api.transition(PHASE4 / 'models/role-declaration.orm.yaml', PHASE4 / 'populations/transition-pre.yaml', steps, post=None)
    assert api_payload['exit_code'] == 3
    assert canary not in json.dumps(api_payload, allow_nan=False)
    steps_path = tmp_path / 'malformed-steps.json'
    steps_path.write_text(json.dumps(steps), encoding='utf-8')
    for output_format in ('json', 'text'):
        completed = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(PHASE4 / 'models/role-declaration.orm.yaml'), '--pre', str(PHASE4 / 'populations/transition-pre.yaml'), '--steps', str(steps_path), '--format', output_format], cwd=ROOT, capture_output=True, check=False)
        assert completed.returncode == 3
        assert canary.encode() not in completed.stdout + completed.stderr

def test_session_refuses_unredacted_v9_verifier_bytes() -> None:
    payload = gnd.api.check(PHASE4 / 'models/role-declaration.orm.yaml', PHASE4 / 'populations/01-violating.yaml', unredacted=True)
    raw = (json.dumps(payload, allow_nan=False, sort_keys=True) + '\n').encode()
    digest = 'a' * 64
    with pytest.raises(VerifierPayloadError, match='redaction mode'):
        validate_verifier_payload(raw, case_id='snapshot-secret', role='required', process_exit=payload['exit_code'], expected_command='check', expected_model=payload['model'], expected_subject=payload['population'], candidate_sha256=digest, contract_sha256=digest, evidence_candidate_sha256=digest, evidence_contract_sha256=digest, expected_schema_version=9)

@pytest.mark.parametrize('output_format', ['json', 'text'])
def test_measure_post_model_failure_is_marker_bearing_and_data_free(tmp_path: Path, output_format: str) -> None:
    canary = 'P4_SECRET_MEASURE_FAILURE'
    missing = tmp_path / canary
    completed = subprocess.run([sys.executable, '-m', 'gnd', 'measure', str(PHASE4 / 'models/role-declaration.orm.yaml'), '--populations', str(missing), '--format', output_format], cwd=ROOT, capture_output=True, check=False)
    raw = completed.stdout + completed.stderr
    assert completed.returncode == 3
    assert canary.encode() not in raw
    assert b'applied' in raw
