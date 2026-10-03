from __future__ import annotations

import copy
import importlib
import json
import math
import subprocess
import sys
from pathlib import Path
from types import MappingProxyType
from typing import Any

import pytest

import gnd.api
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / 'tests/fixtures/v61-phase4'
CASES = json.loads((FIXTURE / 'cases.json').read_text(encoding='utf-8'))
ANSWERS = json.loads((FIXTURE / 'answers.json').read_text(encoding='utf-8'))
MODEL = FIXTURE / 'models/role-declaration.orm.yaml'
VIOLATING = FIXTURE / 'populations/01-violating.yaml'
TRANSITION_PRE = FIXTURE / 'populations/transition-pre.yaml'
TRANSITION_STEPS = FIXTURE / 'steps/binding-only.json'
FLOW_MODEL = FIXTURE / 'models/operation-flow-declarations.orm.yaml'
WITNESS_MODEL = FIXTURE / 'models/witness-declarations.orm.yaml'
WITNESS_POPULATION = FIXTURE / 'populations/witness-cycle-and-derivation.yaml'
_TIMING_PROBE = '\nimport copy\nimport json\nimport sys\nimport time\n\nfrom jsonschema import Draft202012Validator\n\nfrom gnd import checker, report, transition\nfrom gnd.exp.session_contract import MAX_SESSION_CASES\nfrom gnd.model import load_model\nfrom gnd.population import load_population\nfrom gnd.redaction import RedactionPolicy, project_output\n\nmodel_path, population_path = sys.argv[1:]\nmodel = load_model(model_path)\npopulation = load_population(population_path, model=model)\nsemantic = checker.check(model, population)\nbase = report.build_check_payload(\n    0,\n    model_path,\n    population_path,\n    schema_version=7,\n    model_digest=transition.model_digest(model),\n    report=semantic,\n)\npolicy = RedactionPolicy.from_model(model)\n\n# Build and validate the inputs before starting the clock.  Two hundred legal\n# warning records bring the report just below the ordinary 10 MiB input cap\n# without committing a multi-megabyte golden to the repository.\nrow_count = 200\ntarget_bytes = 9_700_000\nempty_warning = {\n    "path": "$.facts.seed[0].item",\n    "message": "",\n    "rule_id": "phase4:timing-public-padding",\n    "severity": "warning",\n}\nlarge = copy.deepcopy(base)\nlarge["warnings"] = [dict(empty_warning) for _ in range(row_count)]\noverhead = len(json.dumps(large, allow_nan=False).encode("utf-8"))\nmessage_size = (target_bytes - overhead) // row_count\nfor index, warning in enumerate(large["warnings"]):\n    warning["message"] = f"public-{index:03d}:" + "x" * (message_size - 11)\nlarge_bytes = len(json.dumps(large, allow_nan=False).encode("utf-8"))\nDraft202012Validator(report.load_report_schema()).validate(large)\n\n# The list is already allocated when timing begins.  Its cardinality is the\n# product\'s actual session-contract maximum, not a duplicated test constant.\nsession_inputs = [copy.deepcopy(base) for _ in range(MAX_SESSION_CASES)]\n\nstarted = time.perf_counter()\nlarge_projected = project_output("check", large, policy=policy, mode="applied")\nlarge_rendered = json.dumps(large_projected, allow_nan=False)\nsession_projected = [\n    project_output("check", item, policy=policy, mode="applied")\n    for item in session_inputs\n]\nsession_rendered = json.dumps(session_projected, allow_nan=False)\nelapsed = time.perf_counter() - started\n\nschema = Draft202012Validator(report.load_report_schema())\nschema.validate(large_projected)\nschema.validate(session_projected[0])\nschema.validate(session_projected[-1])\nprint(json.dumps({\n    "elapsed_seconds": elapsed,\n    "input_bytes": large_bytes,\n    "output_bytes": len(large_rendered.encode("utf-8")),\n    "session_cases": MAX_SESSION_CASES,\n    "session_output_bytes": len(session_rendered.encode("utf-8")),\n    "projection_calls": 1 + len(session_projected),\n}))\n'

def _redaction() -> Any:
    return importlib.import_module('gnd.redaction')

def _policy() -> Any:
    return _redaction().RedactionPolicy.from_model(load_model(MODEL))

def _contains(value: Any, expected: Any) -> bool:
    if value == expected:
        return True
    if isinstance(value, dict):
        return any(_contains(child, expected) for child in value.values())
    if isinstance(value, (list, tuple)):
        return any(_contains(child, expected) for child in value)
    return False

def _assert_projection_answers(cases: dict[str, Any], answers: dict[str, Any]) -> None:
    marker = answers['marker']
    assert marker == {'redacted': True, 'roles': ['optional_code.code']}
    assert marker['roles'] == sorted(set(marker['roles']))
    assert answers['instance_text_marker'] == '[REDACTED INSTANCE DETAIL]'
    assert not set(answers['canaries']['selected']) & set(answers['canaries']['public_controls'])
    expected = {row['id']: row['expected_exit'] for row in cases['snapshot_cases'] + cases['transition_cases'] if 'expected_exit' in row}
    assert expected == answers['expected_bands']
    assert {row['id'] for row in cases['witness_cases']} == {'P-03A', 'P-03B'}
    assert {(row['id'], row['selected_origin'], row['parameter']) for row in cases['transition_cases'] if row['id'].startswith('P-02')} == {('P-02A', 'precondition', 'authorized_code'), ('P-02B', 'effect', 'emitted_code'), ('P-02C', 'dynamic-subject', 'item')}
    assert {f'P-{index:02d}' for index in range(1, 7)} <= set(cases['branch_ids'])

def _marker_contract(marker: dict[str, Any]) -> None:
    assert set(marker) == {'redacted', 'roles'}
    assert marker['redacted'] is True
    assert marker['roles']
    assert marker['roles'] == sorted(set(marker['roles']))

def test_projection_corpus_contract_and_checker_are_live() -> None:
    _assert_projection_answers(CASES, ANSWERS)
    _marker_contract(ANSWERS['marker'])
    dirty = copy.deepcopy(ANSWERS['dirty_controls']['marker'])
    with pytest.raises(AssertionError):
        _marker_contract(dirty)
    dirty_answers = copy.deepcopy(ANSWERS)
    dirty_answers['expected_bands']['SN-00'] = 1
    with pytest.raises(AssertionError):
        _assert_projection_answers(CASES, dirty_answers)

def test_population_roles_project_by_origin(tmp_path: Path) -> None:
    steps = json.loads(TRANSITION_STEPS.read_text(encoding='utf-8'))
    equal_value = 'P4_PUBLIC_EQUAL_VALUE'
    steps['steps'][0]['bindings'] = {'item': equal_value, 'code': equal_value}
    equal_steps = tmp_path / 'equal-value-steps.json'
    equal_steps.write_text(json.dumps(steps), encoding='utf-8')
    payload = gnd.api.transition(MODEL, TRANSITION_PRE, equal_steps, post=None)
    fact = next(row for row in payload['transition']['computed_post']['facts']['optional_code'] if row['item'] == equal_value)
    assert fact == {'item': equal_value, 'code': ANSWERS['marker']}
    assert equal_value in json.dumps(payload, allow_nan=False)

def test_step_parameters_follow_all_operation_role_uses() -> None:
    policy = _redaction().RedactionPolicy.from_model(load_model(FLOW_MODEL))
    assert policy.redacted_parameters == {'apply_authorized_code': frozenset({'authorized_code', 'emitted_code', 'item'})}

def test_tuple_cycle_derivation_and_transition_witnesses_replace_whole() -> None:
    snapshot = gnd.api.check(MODEL, VIOLATING)
    failed = next(row for row in snapshot['verdicts'] if row['verdict'] == 'fail')
    assert failed['offending_facts'] == [ANSWERS['marker']]
    witnesses = gnd.api.check(WITNESS_MODEL, WITNESS_POPULATION)
    cycle = next(row for row in witnesses['verdicts'] if row['constraint_type'] == 'ring')
    assert cycle['offending_facts'] == [{'redacted': True, 'roles': ['node_links_to.to']}]
    finding = witnesses['derivations'][0]['findings'][0]
    assert finding['witness'] == {'redacted': True, 'roles': ['derived_secret.node']}
    transition = gnd.api.transition(MODEL, TRANSITION_PRE, TRANSITION_STEPS, post=None)
    assert transition['transition']['steps'][0]['bindings']['code'] == ANSWERS['marker']
    assert not _contains(transition['transition'], 'P4_SECRET_BINDING_ONLY')

def test_instance_text_and_derived_identity_are_data_free() -> None:
    snapshot = gnd.api.check(MODEL, VIOLATING)
    failed = next(row for row in snapshot['verdicts'] if row['verdict'] == 'fail')
    assert failed['message'] == ANSWERS['instance_text_marker']
    payload = gnd.api.check(WITNESS_MODEL, WITNESS_POPULATION)
    cycle = next(row for row in payload['verdicts'] if row['constraint_type'] == 'ring')
    finding = payload['derivations'][0]['findings'][0]
    assert cycle['message'] == ANSWERS['instance_text_marker']
    assert finding['message'] == ANSWERS['instance_text_marker']
    rendered = json.dumps(payload, allow_nan=False)
    for canary in ('P4_SECRET_CYCLE_A', 'P4_SECRET_CYCLE_B', 'P4_SECRET_DERIVATION_EXTRA'):
        assert canary not in rendered
    assert ANSWERS['instance_text_marker'] in rendered

@pytest.mark.parametrize('value', [{'value': 10 ** 10000}, {'value': math.inf}, {'value': math.nan}, {'value': {'wrong', 'container'}}, MappingProxyType({'value': ('read-only',)})], ids=('huge-int', 'infinity', 'nan', 'wrong-container', 'read-only'))
def test_projection_is_total_and_nonmutating(value: Any) -> None:
    redaction = _redaction()
    original_keys = set(value)
    original_leaf = value['value']
    original_nested = set(original_leaf) if isinstance(original_leaf, set) else None
    try:
        projected = redaction.project_output('check', value, policy=_policy(), mode='applied')
    except redaction.RedactionProjectionError:
        pass
    else:
        assert isinstance(projected, dict)
        assert projected is not value
    assert set(value) == original_keys
    if original_nested is not None:
        assert value['value'] == original_nested
    elif isinstance(original_leaf, float) and math.isnan(original_leaf):
        assert math.isnan(value['value'])
    else:
        assert value['value'] == original_leaf

def test_projection_is_total_over_deep_input_and_nonmutating() -> None:
    redaction = _redaction()
    source: dict[str, Any] = {'leaf': 'P4_SECRET_CODE_00'}
    for _ in range(300):
        source = {'next': source}
    before_ids: list[int] = []
    cursor = source
    while 'next' in cursor:
        before_ids.append(id(cursor))
        cursor = cursor['next']
    before_ids.append(id(cursor))
    try:
        projected = redaction.project_output('check', source, policy=_policy(), mode='applied')
    except redaction.RedactionProjectionError:
        pass
    else:
        assert isinstance(projected, dict)
        assert projected is not source
    after_ids: list[int] = []
    cursor = source
    while 'next' in cursor:
        after_ids.append(id(cursor))
        cursor = cursor['next']
    after_ids.append(id(cursor))
    assert after_ids == before_ids
    assert cursor == {'leaf': 'P4_SECRET_CODE_00'}

def test_projection_fault_fails_closed(monkeypatch: pytest.MonkeyPatch) -> None:
    redaction = _redaction()
    canary = 'P4_SECRET_CODE_01'

    def explode(*_args: Any, **_kwargs: Any) -> Any:
        raise redaction.RedactionProjectionError(canary)
    monkeypatch.setattr(redaction, 'project_output', explode)
    api_redaction = getattr(gnd.api, 'redaction_module', None)
    if api_redaction is not None:
        monkeypatch.setattr(api_redaction, 'project_output', explode)
    if hasattr(gnd.api, 'project_output'):
        monkeypatch.setattr(gnd.api, 'project_output', explode)
    payload = gnd.api.check(MODEL, VIOLATING)
    assert payload['exit_code'] == 70
    assert payload['redaction'] == ANSWERS['applied_redaction']
    assert payload['error']['type'] == 'RedactionProjectionError'
    assert canary not in json.dumps(payload, allow_nan=False)

def test_projection_time_ceiling_in_fresh_process() -> None:
    completed = subprocess.run([sys.executable, '-c', _TIMING_PROBE, str(MODEL), str(FIXTURE / 'populations/00-clean.yaml')], cwd=ROOT, capture_output=True, text=True, timeout=30, check=False)
    assert completed.returncode == 0, completed.stderr
    observed = json.loads(completed.stdout)
    assert 9 * 1024 * 1024 <= observed['input_bytes'] < 10 * 1024 * 1024
    assert observed['output_bytes'] > 0
    assert observed['session_cases'] > 0
    assert observed['session_output_bytes'] > 0
    assert observed['projection_calls'] == observed['session_cases'] + 1
    assert observed['elapsed_seconds'] <= ANSWERS['projection_time_ceiling_seconds']
