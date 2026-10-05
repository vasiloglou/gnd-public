import copy
import json
from pathlib import Path
from typing import Literal, get_args, get_origin

import pytest
from pydantic import ValidationError

from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import AttemptFeedback
from gnd.exp.session_store import AttemptRecord, SessionResult

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v61-phase4'
CASES = json.loads((FIXTURE / 'cases.json').read_text(encoding='utf-8'))
ANSWERS = json.loads((FIXTURE / 'answers.json').read_text(encoding='utf-8'))
SESSION = json.loads((FIXTURE / CASES['session']['answers']).read_text(encoding='utf-8'))
CONTRACT = json.loads((FIXTURE / CASES['session']['contract']).read_text(encoding='utf-8'))
PHASE3_SESSION = json.loads((ROOT / 'tests/fixtures/v61-phase3/session-v4-answers.json').read_text(encoding='utf-8'))

def _literal_values(annotation: object) -> set[object]:
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    values: set[object] = set()
    for argument in get_args(annotation):
        values.update(_literal_values(argument))
    return values

def _json_tokens(value: object) -> str:
    return json.dumps(value, allow_nan=False, sort_keys=True, separators=(',', ':'))

def _session_redaction() -> dict[str, object]:
    return {'mode': 'applied', 'declarations': copy.deepcopy(SESSION['declarations'])}

def _feedback_v6() -> dict[str, object]:
    document = copy.deepcopy(PHASE3_SESSION['feedback_v5'])
    document['schema_version'] = SESSION['feedback_schema_version']
    document['redaction'] = _session_redaction()
    return document

def _result_v4() -> dict[str, object]:
    document = copy.deepcopy(PHASE3_SESSION['result_v3'])
    document['schema_version'] = SESSION['result_schema_version']
    document['acceptance_modes'] = SESSION['successor_shapes']['result']['acceptance_modes']
    document['redaction'] = _session_redaction()
    return document

def test_session_fixture_is_closed_and_case_scoped() -> None:
    assert SESSION['schema_version'] == 1
    assert CONTRACT['schema_version'] == SESSION['contract_schema_version'] == 4
    assert [case['case_id'] for case in CONTRACT['cases']] == SESSION['case_ids']
    assert {row['case_id'] for row in SESSION['declarations']} == set(SESSION['case_ids'])
    assert all(row['roles'] == ['code'] for row in SESSION['declarations'])
    assert SESSION['successor_shapes'] == {'feedback': {'schema_version': 6, 'redaction_mode': 'applied'}, 'attempt': {'schema_version': 6, 'feedback_schema_version': 6, 'redaction_mode': 'applied'}, 'result': {'schema_version': 4, 'acceptance_modes': ['constraint-satisfaction', 'transition'], 'redaction_mode': 'applied'}}

def test_feedback_attempt_result_successors() -> None:
    feedback = AttemptFeedback.model_validate(_feedback_v6())
    assert feedback.schema_version == SESSION['feedback_schema_version']
    assert SESSION['attempt_schema_version'] in _literal_values(AttemptRecord.model_fields['schema_version'].annotation)
    assert SESSION['attempt_schema_version'] in _literal_values(AttemptRecord.model_fields['feedback_schema_version'].annotation)
    result = SessionResult.model_validate(_result_v4())
    assert result.schema_version == SESSION['result_schema_version']
    assert ANSWERS['wire_versions'] == {'report': 9, 'batch': 2, 'measurement': 3, 'feedback': 6, 'attempt': 6, 'result': 4, 'contract': 4}

def test_mixed_session_declarations_are_case_scoped() -> None:
    case_ids = SESSION['case_ids']
    declarations = SESSION['declarations']
    assert [row['case_id'] for row in declarations] == case_ids
    assert all(row['case_id'] is not None for row in declarations)
    assert len({_json_tokens(row) for row in declarations}) == len(case_ids)
    assert all(row['fact_type'] == 'optional_code' for row in declarations)

def test_contract_cannot_select_unredacted() -> None:
    serialized = _json_tokens(CONTRACT)
    for field in SESSION['forbidden_contract_fields']:
        assert f'"{field}"' not in serialized
    parsed = DataDrivenContract.model_validate(CONTRACT)
    assert parsed.schema_version == 4
    for field in SESSION['forbidden_contract_fields']:
        dirty = copy.deepcopy(CONTRACT)
        dirty['cases'][0][field] = True
        with pytest.raises(ValidationError):
            DataDrivenContract.model_validate(dirty)

def test_session_predecessor_relabels_refuse() -> None:
    assert SESSION['cross_version_relabels_refuse'] == [[6, 5], [5, 6], [4, 3]]
    assert _literal_values(AttemptFeedback.model_fields['schema_version'].annotation) >= {1, 2, 3, 4, 5, 6}
    assert _literal_values(AttemptRecord.model_fields['schema_version'].annotation) >= {1, 2, 3, 4, 5, 6}
    assert _literal_values(SessionResult.model_fields['schema_version'].annotation) >= {1, 2, 3, 4}
    relabeled_feedback = _feedback_v6()
    relabeled_feedback['schema_version'] = 5
    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate(relabeled_feedback)
    predecessor_feedback = copy.deepcopy(PHASE3_SESSION['feedback_v5'])
    predecessor_feedback['schema_version'] = 6
    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate(predecessor_feedback)
    relabeled_result = _result_v4()
    relabeled_result['schema_version'] = 3
    with pytest.raises(ValidationError):
        SessionResult.model_validate(relabeled_result)

def test_answer_free_session_surface_names_every_forbidden_token() -> None:
    assert set(SESSION['forbidden_feedback_tokens']) == {'P4_SECRET_CODE_01', 'P4_SECRET_BINDING_ONLY', 'bindings', 'witnesses', 'offending_facts'}
    assert set(SESSION['forbidden_feedback_tokens']) <= set(ANSWERS['canaries']['selected']) | {'bindings', 'witnesses', 'offending_facts'}
