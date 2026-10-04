from __future__ import annotations

import copy
import hashlib
import json
import shutil
from pathlib import Path
from typing import Literal, get_args, get_origin

import pytest
from pydantic import ValidationError

from gnd.exp import close as close_module
from gnd.exp import session_eval
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import AttemptEvaluation, AttemptFeedback, CaseEvaluation
from gnd.exp.session_store import AttemptRecord, SessionResult

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/public-walk-floor"
PHASE3 = {'schema_version': 1, 'contract_v4': {'schema_version': 4, 'experiment_id': 'EXP-v61-phase3-plan', 'max_attempts': 3, 'wall_seconds': 300.0, 'cases': [{'case_id': 'expense-plan', 'role': 'required', 'inputs': [{'path': 'input/pre.pop.yaml', 'media_type': 'application/yaml', 'encoding': 'utf-8', 'sha256': '7188dbb065dc7a33e6c8ef779b7e63baaff471fc510279684416913d8cc4812d', 'size_bytes': 1047}], 'acceptance': {'mode': 'transition'}, 'verify': {'command': 'transition', 'model': {'path': 'model.orm.yaml', 'media_type': 'application/yaml', 'encoding': 'utf-8', 'sha256': '2c6ef90365b5c9e4c4531d78bdce9e3ca9e1394fb498a655ee6c9ade05d0784e', 'size_bytes': 26838}, 'pre': 'input/pre.pop.yaml', 'steps': 'plan/steps.json', 'post': None}}]}, 'feedback_v5': {'schema_version': 5, 'run_id': 'run-v61-phase3', 'contract_id': 'EXP-v61-phase3-plan', 'contract_sha256': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa', 'source_attempt_index': 1, 'candidate_sha256': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'case_payload_sha256s': [['expense-plan', 'cccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccccc']], 'normalized_verifier_signature': 'dddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddddd', 'process_exit': 1, 'payload_exit': [['expense-plan', 1]], 'acceptance_ready': False, 'required': [{'case_id': 'expense-plan', 'role': 'required', 'command': 'transition', 'band': 1, 'steps': [{'index': 1, 'operation_id': 'approve_expense', 'outcome': 'accepted'}, {'index': 2, 'operation_id': 'submit_expense_to_workday', 'outcome': 'violated'}]}], 'diagnostic': [], 'disposition': 'retry'}, 'attempt_v5': {'base': 'a valid immutable attempt-v4 document', 'exact_changes': {'schema_version': 5, 'feedback_schema_version': 5}, 'required_preserved_fields': ['assurance_receipts', 'invocation', 'evaluation', 'feedback', 'evidence_digests'], 'forbidden_new_fields': ['bindings', 'witnesses', 'messages', 'expected_values']}, 'result_v3': {'schema_version': 3, 'run_id': 'run-v61-phase3', 'disposition': 'accepted', 'terminal_reason': 'all required cases accepted', 'attempt_count': 1, 'best_attempt': 1, 'best_attempt_manifest_sha256': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee', 'best_candidate_sha256': 'bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb', 'referenced_evidence_digests': {'attempts/0001/attempt.json': 'eeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee'}, 'acceptance_modes': ['transition']}, 'step_outcomes': ['accepted', 'violated', 'inadequate', 'indeterminate'], 'bands': [0, 1, 2, 3, 4, 70], 'feedback_forbidden_tokens': ['SECRET-BINDING-314159', 'SECRET-WITNESS-271828', 'bindings', 'witnesses', 'offending_facts', 'message']}
CASES = {'schema_version': 1, 'accepted': [{'id': 'S-01', 'shape': 'transition-plan', 'post': None}, {'id': 'S-02', 'shape': 'transition-full', 'post': 'plan/post.pop.yaml'}, {'id': 'S-03', 'shape': 'mixed', 'modes': ['exact-bytes', 'tests', 'transition']}], 'refused': [{'id': 'S-04', 'mutation': 'transition-acceptance-with-check-verifier'}, {'id': 'S-05', 'mutation': 'transition-verifier-with-exact-acceptance'}, {'id': 'S-06', 'mutation': 'missing-pre-input'}, {'id': 'S-07', 'mutation': 'duplicate-pre-input'}, {'id': 'S-08', 'mutation': 'steps-also-bound-input'}, {'id': 'S-09', 'mutation': 'post-also-bound-input'}, {'id': 'S-10', 'mutation': 'unsafe-candidate-path'}, {'id': 'S-11', 'mutation': 'missing-candidate-file'}, {'id': 'S-12', 'mutation': 'cross-version-relabel'}], 'private_canaries': ['SECRET-BINDING-314159', 'SECRET-WITNESS-271828']}
ANSWERS = {**PHASE3, **json.loads((FIXTURE / "answers.json").read_text(encoding="utf-8"))}
CONTRACT_DOCUMENT = json.loads((FIXTURE / "session/contract-v5.json").read_text(encoding="utf-8"))
CONTRACT_BYTES = (FIXTURE / "session/contract-v5.json").read_bytes()
STEPS = json.loads((FIXTURE / "session/candidate/steps.json").read_text(encoding="utf-8"))["steps"]
PHASE4_SESSION = json.loads((ROOT / "tests/fixtures/v61-phase4/session/answers.json").read_text(encoding="utf-8"))
PHASE4_CONTRACT = json.loads((ROOT / "tests/fixtures/v61-phase4/session/contract-v4.json").read_text(encoding="utf-8"))


def _check_feedback(document: dict[str, object]) -> None:
    assert document['schema_version'] == 5
    assert document['disposition'] in {'accepted', 'retry', 'agent-failure', 'verifier-failure', 'stagnation', 'oscillation', 'budget-exhausted'}
    for row in [*document['required'], *document['diagnostic']]:
        assert set(row) == {'case_id', 'role', 'command', 'band', 'steps'}
        assert row['command'] == 'transition'
        assert row['band'] in ANSWERS['bands']
        for step in row['steps']:
            assert set(step) == {'index', 'operation_id', 'outcome'}
            assert step['outcome'] in ANSWERS['step_outcomes']
    encoded = json.dumps(document, sort_keys=True, separators=(',', ':'))
    for token in ANSWERS['feedback_forbidden_tokens']:
        assert token not in encoded

def _literal_values(annotation: object) -> set[object]:
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    values: set[object] = set()
    for argument in get_args(annotation):
        values.update(_literal_values(argument))
    return values

def test_session_corpus_is_closed_and_answer_free() -> None:
    assert {row['id'] for row in CASES['accepted']} == {'S-01', 'S-02', 'S-03'}
    assert {row['id'] for row in CASES['refused']} == {f'S-{index:02d}' for index in range(4, 13)}
    contract = ANSWERS['contract_v4']
    assert contract['schema_version'] == 4
    case = contract['cases'][0]
    assert case['acceptance'] == {'mode': 'transition'}
    assert case['verify']['command'] == 'transition'
    assert case['verify']['post'] is None
    assert case['verify']['pre'] == case['inputs'][0]['path']
    _check_feedback(ANSWERS['feedback_v5'])

def test_feedback_checker_rejects_secret_and_extra_field() -> None:
    dirty = copy.deepcopy(ANSWERS['feedback_v5'])
    dirty['required'][0]['bindings'] = {'expense': 'SECRET-BINDING-314159'}
    with pytest.raises(AssertionError):
        _check_feedback(dirty)

def test_contract_v4_is_version_dispatched() -> None:
    parsed = DataDrivenContract.model_validate(ANSWERS['contract_v4'])
    assert parsed.schema_version == 4
    assert parsed.cases[0].acceptance.mode == 'transition'
    assert parsed.cases[0].verify.command == 'transition'

def test_feedback_v5_is_version_dispatched() -> None:
    parsed = AttemptFeedback.model_validate(ANSWERS['feedback_v5'])
    assert parsed.schema_version == 5
    assert parsed.required[0].band == 1

def test_attempt_v5_can_bind_feedback_v5() -> None:
    assert 5 in _literal_values(AttemptRecord.model_fields['schema_version'].annotation)
    assert 5 in _literal_values(AttemptRecord.model_fields['feedback_schema_version'].annotation)

def test_terminal_result_v3_names_transition_acceptance() -> None:
    parsed = SessionResult.model_validate(ANSWERS['result_v3'])
    assert parsed.schema_version == 3
    assert parsed.acceptance_modes == ('transition',)

def test_cross_version_relabeling_is_not_accepted() -> None:
    relabeled = copy.deepcopy(ANSWERS['contract_v4'])
    relabeled['schema_version'] = 3
    with pytest.raises(ValidationError):
        DataDrivenContract.model_validate(relabeled)

def _feedback() -> dict[str, object]:
    document = copy.deepcopy(PHASE3['feedback_v5'])
    document['schema_version'] = 7
    document['redaction'] = None
    document['required'][0]['band'] = 0
    document['payload_exit'] = [['expense-plan', 0]]
    document['required'][0]['steps'] = [{'index': 1, 'operation_id': 'approve_expense', 'outcome': 'accepted'}]
    document['required'][0]['unmet_walk_floors'] = [{'kind': 'required-op-missing', 'operation_id': 'approve_expense'}]
    return document

def _evaluation(steps: list[dict[str, object]]) -> AttemptEvaluation:
    result = CaseEvaluation(payload_valid=True, case_id='expense-walk', role='required', candidate_sha256='1' * 64, contract_sha256='2' * 64, raw_payload_sha256='3' * 64, command='transition', process_exit=0, payload_exit=0, outcome='accepted', acceptance_ready=True, counts={'pass': 0, 'fail': 0, 'warning': 0, 'unchecked': 0, 'vacuous': 0}, coverage={}, alethic_failure_count=0, alethic_indeterminate_count=0)
    result = session_eval.attach_walk_floor_steps(result, steps)
    return AttemptEvaluation(attempt_index=1, candidate_sha256='1' * 64, contract_sha256='2' * 64, results=(result,))

def test_f01_f04_feedback_v7_has_exact_answer_free_keys_and_nullable_redaction() -> None:
    document = _feedback()
    parsed = AttemptFeedback.model_validate(document)
    assert parsed.schema_version == ANSWERS['versions']['feedback'] == 7
    row = document['required'][0]
    assert set(row) == {'case_id', 'role', 'command', 'band', 'steps', 'unmet_walk_floors'}
    assert row['unmet_walk_floors'] == [{'kind': 'required-op-missing', 'operation_id': 'approve_expense'}]

def test_f05_feedback_never_emits_expected_binding_canary() -> None:
    encoded = json.dumps(_feedback(), sort_keys=True, separators=(',', ':'))
    assert ANSWERS['canary'] not in encoded
    assert 'bindings_subset' not in encoded
    assert 'expected_value' not in encoded

def test_f06_recurrence_signature_changes_on_kind_and_operation_only() -> None:
    contract = DataDrivenContract.model_validate(CONTRACT_DOCUMENT)
    missing = [step for step in STEPS if step['op'] != 'approve_expense']
    forbidden = [*STEPS, {'op': 'pay_without_approval', 'bindings': {'expense': 41}}]
    signatures = {session_eval.normalized_verifier_signature(contract, _evaluation(steps), schema_version=7) for steps in (missing, forbidden)}
    assert len(signatures) == 2
    for signature in signatures:
        assert ANSWERS['canary'] not in signature

def test_f07_attempt_v7_binds_feedback_v7() -> None:
    assert 7 in _literal_values(AttemptRecord.model_fields['schema_version'].annotation)
    assert 7 in _literal_values(AttemptRecord.model_fields['feedback_schema_version'].annotation)

@pytest.mark.parametrize('field', ['bindings_subset', 'expected_value', 'message'])
def test_f08_secret_bearing_or_extra_floor_fields_refuse(field: str) -> None:
    document = _feedback()
    document['required'][0]['unmet_walk_floors'][0][field] = ANSWERS['canary']
    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate(document)

def _feedback_v6() -> dict[str, object]:
    document = copy.deepcopy(PHASE3['feedback_v5'])
    document['schema_version'] = 6
    document['redaction'] = {'mode': 'applied', 'declarations': copy.deepcopy(PHASE4_SESSION['declarations'])}
    return document

def _result_v4() -> dict[str, object]:
    document = copy.deepcopy(PHASE3['result_v3'])
    document['schema_version'] = 4
    document['acceptance_modes'] = ['constraint-satisfaction', 'transition']
    document['redaction'] = {'mode': 'applied', 'declarations': copy.deepcopy(PHASE4_SESSION['declarations'])}
    return document

def test_v01_v04_predecessor_readers_and_serializers_remain_byte_exact() -> None:
    documents = [DataDrivenContract.model_validate(PHASE3['contract_v4']), DataDrivenContract.model_validate(PHASE4_CONTRACT), AttemptFeedback.model_validate(PHASE3['feedback_v5']), AttemptFeedback.model_validate(_feedback_v6()), SessionResult.model_validate(PHASE3['result_v3']), SessionResult.model_validate(_result_v4())]
    expected = [PHASE3['contract_v4'], PHASE4_CONTRACT, PHASE3['feedback_v5'], _feedback_v6(), PHASE3['result_v3'], _result_v4()]
    assert [item.model_dump(mode='json') for item in documents] == expected

@pytest.mark.parametrize('reader,document,version', [(DataDrivenContract, PHASE3['contract_v4'], 5), (AttemptFeedback, _feedback_v6(), 7), (SessionResult, _result_v4(), 5)])
def test_v05_v08_cross_version_relabeling_refuses(reader, document, version: int) -> None:
    dirty = copy.deepcopy(document)
    dirty['schema_version'] = version
    with pytest.raises(ValidationError):
        reader.model_validate(dirty)

def test_existing_report_cli_api_versions_are_not_widened() -> None:
    assert PHASE4_SESSION['successor_shapes']['feedback']['schema_version'] == 6
    assert PHASE4_SESSION['successor_shapes']['result']['schema_version'] == 4

def _result(*, discharged: bool=True) -> dict[str, object]:
    document = copy.deepcopy(PHASE3['result_v3'])
    document.update(schema_version=5, redaction=None, contract_sha256=hashlib.sha256(CONTRACT_BYTES).hexdigest(), walk_floors=[{'case_id': 'expense-walk', 'role': 'required', 'required_ops': 1, 'forbidden_ops': 1, 'discharged': discharged}])
    return document

def _findings(tmp_path: Path, result: dict[str, object]) -> list[object]:
    experiment = tmp_path / 'experiment'
    shutil.copytree(FIXTURE / 'session', experiment)
    (experiment / 'session.contract.json').write_bytes(CONTRACT_BYTES)
    run_root = experiment / 'runs/run-0001'
    run_root.mkdir(parents=True)
    run = close_module._SessionRun(index=1, root=run_root, result=None, launched=True)
    return close_module._declared_case_findings(run, experiment, json.dumps(result, sort_keys=True, separators=(',', ':')).encode())

def test_review_03_close_refuses_unbound_hand_authored_discharge(tmp_path: Path) -> None:
    findings = _findings(tmp_path, _result())
    assert findings and findings[0].kind == 'unaccepted-session'

@pytest.mark.parametrize('mutation', [lambda d: d.update(contract_sha256='0' * 64), lambda d: d['walk_floors'].clear(), lambda d: d['walk_floors'].append({'case_id': 'extra', 'role': 'diagnostic', 'required_ops': 0, 'forbidden_ops': 1, 'discharged': True}), lambda d: d['walk_floors'][0].update(required_ops=2), lambda d: d['walk_floors'][0].update(discharged=False)])
def test_k02_k05_k07_close_refuses_stale_or_incomplete_floor_accounting(tmp_path: Path, mutation) -> None:
    document = _result()
    mutation(document)
    findings = _findings(tmp_path, document)
    assert findings and {finding.kind for finding in findings} == {'unaccepted-session'}
    assert 'expense-walk' in ' '.join(finding.message for finding in findings)

def test_k06_unreadable_contract_is_a_close_refusal(tmp_path: Path) -> None:
    document = _result()
    _findings(tmp_path, document)
    experiment = tmp_path / 'experiment'
    (experiment / 'session.contract.json').write_text('{', encoding='utf-8')
    run_root = experiment / 'runs/run-0001'
    run = close_module._SessionRun(index=1, root=run_root, result=None, launched=True)
    findings = close_module._declared_case_findings(run, experiment, json.dumps(document).encode())
    assert findings and findings[0].kind == 'unaccepted-session'

def test_result_v5_refuses_a_secret_bearing_floor_row() -> None:
    document = _result()
    document['walk_floors'][0]['bindings_subset'] = {'expense': 41}
    with pytest.raises(ValidationError):
        SessionResult.model_validate(document)

def test_transition_verify_requires_explicit_nullable_post() -> None:
    document = copy.deepcopy(ANSWERS['contract_v4'])
    document['cases'][0]['verify'].pop('post')
    with pytest.raises(ValidationError, match='post'):
        DataDrivenContract.model_validate(document)


_HAPPY_TESTS_CONTRACT = '{\n  "schema_version": 3,\n  "experiment_id": "EXP-303-tests-mode",\n  "max_attempts": 1,\n  "wall_seconds": 2,\n  "cases": [\n    {\n      "case_id": "gate",\n      "role": "required",\n      "acceptance": {\n        "mode": "tests",\n        "required_tests": [\n          "test_gate.py::test_pass"\n        ],\n        "results_path": "results/results.xml",\n        "results_format": "junit-xml",\n        "protected": [\n          {\n            "path": "test_gate.py",\n            "media_type": "text/x-python",\n            "encoding": "utf-8",\n            "sha256": "0000000000000000000000000000000000000000000000000000000000000000",\n            "size_bytes": 0\n          }\n        ],\n        "test_argv_sha256": "0000000000000000000000000000000000000000000000000000000000000000"\n      }\n    }\n  ]\n}\n'

@pytest.fixture(autouse=True)
def _owned_transition_contract_refusal(request, tmp_path, monkeypatch):
    if request.node.name != 'test_v4_contract_requires_a_transition_case':
        return
    destination = tmp_path / 'tests/fixtures/tests_mode/cases/happy/contract.json'
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(_HAPPY_TESTS_CONTRACT.encode('utf-8'))
    destination.chmod(0o644)
    monkeypatch.setattr(__import__('sys').modules[__name__], 'ROOT', tmp_path)


def test_v4_contract_requires_a_transition_case() -> None:
    document = json.loads((ROOT / 'tests/fixtures/tests_mode/cases/happy/contract.json').read_text(encoding='utf-8'))
    document['schema_version'] = 4
    with pytest.raises(ValidationError, match='transition'):
        DataDrivenContract.model_validate(document)
