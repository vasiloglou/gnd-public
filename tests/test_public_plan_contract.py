from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator
from test_exp_session_e2e import _write_fake_agent
from test_public_transition_walks import CORPUS

import gnd.api
from gnd.report import load_report_schema

ROOT = CORPUS
PHASE3 = Path(__file__).parent / "fixtures/public-plan-contract"
CASES = json.loads((PHASE3 / "plan-cases.json").read_text(encoding="utf-8"))
ANSWERS = json.loads((PHASE3 / "plan-answers.json").read_text(encoding="utf-8"))
MODEL = ROOT / CASES["model"]
WALKS = ROOT / CASES["walk_root"]


@pytest.mark.parametrize('case', [row for row in CASES['plan_cases'] if 'injection' not in row], ids=lambda row: row['id'])
def test_plan_cli_selects_version_8_and_approved_band(case: dict[str, object]) -> None:
    walk = WALKS / str(case['walk'])
    completed = subprocess.run([sys.executable, '-m', 'gnd', 'check', str(MODEL.relative_to(ROOT)), '--pre', str((walk / 'pre.pop.yaml').relative_to(ROOT)), '--steps', str((walk / 'steps.json').relative_to(ROOT)), '--format', 'json'], cwd=ROOT, capture_output=True, check=False)
    assert completed.returncode == case['expected_band']
    payload = json.loads(completed.stdout)
    assert payload['schema_version'] == 8
    assert payload['post'] == 'computed'
    assert payload['transition']['evaluated'] is case['evaluated']

def test_clean_plan_projects_the_approved_computed_population() -> None:
    walk = WALKS / 'clean-walk'
    payload = gnd.api.transition(MODEL, walk / 'pre.pop.yaml', walk / 'steps.json', post=None)
    assert payload['exit_code'] == 0
    assert payload['transition']['computed_post'] == ANSWERS['computed_post_clean']
    assert payload['transition']['frame_status'] == 'not-applicable'
    assert payload['transition']['frame_verdicts'] is None

def test_plan_internal_fault_returns_payload_shaped_70(monkeypatch: pytest.MonkeyPatch) -> None:
    import gnd.transition as transition_module
    monkeypatch.setattr(transition_module, 'evaluate_plan', lambda *_: (_ for _ in ()).throw(RuntimeError('phase3-plan-pin')))
    walk = WALKS / 'clean-walk'
    payload = gnd.api.transition(MODEL, walk / 'pre.pop.yaml', walk / 'steps.json', post=None)
    assert payload['exit_code'] == 70
    assert payload['error']['type'] == 'RuntimeError'

@pytest.mark.parametrize('case', [row for row in CASES['plan_cases'] if row.get('evaluated')], ids=lambda row: f"honest-{row['id']}")
def test_plan_band_matches_the_existing_honest_post(case: dict[str, object]) -> None:
    walk = WALKS / str(case['walk'])
    plan = gnd.api.transition(MODEL, walk / 'pre.pop.yaml', walk / 'steps.json', post=None)
    full = gnd.api.transition(MODEL, walk / 'pre.pop.yaml', walk / 'steps.json', walk / 'post.pop.yaml')
    assert plan['exit_code'] == full['exit_code'] == case['expected_band']

def test_report_v8_computed_post_is_a_closed_population() -> None:
    plan_cases = json.loads((PHASE3 / 'plan-cases.json').read_text(encoding='utf-8'))
    walk = ROOT / plan_cases['walk_root'] / 'clean-walk'
    payload = gnd.api.transition(ROOT / plan_cases['model'], walk / 'pre.pop.yaml', walk / 'steps.json', post=None)
    validator = Draft202012Validator(load_report_schema())
    validator.validate(payload)
    payload['transition']['computed_post'] = {}
    assert list(validator.iter_errors(payload))

def test_computed_population_always_emits_model_id() -> None:
    plan_cases = json.loads((PHASE3 / 'plan-cases.json').read_text(encoding='utf-8'))
    walk = ROOT / plan_cases['walk_root'] / 'clean-walk'
    payload = gnd.api.transition(ROOT / plan_cases['model'], walk / 'pre.pop.yaml', walk / 'steps.json', post=None)
    assert 'model_id' in payload['transition']['computed_post']['population']

def test_mixed_cli_run_evaluates_tests_snapshot_and_transition(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    from gnd.cli import main
    experiment_id = 'EXP-611-mixed-transition'
    root = tmp_path / experiment_id
    candidate = root / 'candidate'
    candidate.mkdir(parents=True)
    (root / 'SPEC.md').write_text(f'---\nid: {experiment_id}\nkind: data-driven\ntitle: Exercise every mixed verifier lane\nquestions:\n  - id: Q1\n    text: Does one attempt satisfy all declared verifier kinds?\nfollows: []\ncovers: []\n---\n\n# Exercise every mixed verifier lane\n', encoding='utf-8')
    plan_cases = json.loads((PHASE3 / 'plan-cases.json').read_text(encoding='utf-8'))
    walk = ROOT / plan_cases['walk_root'] / 'clean-walk'
    model_bytes = (ROOT / plan_cases['model']).read_bytes()
    pre_bytes = (walk / 'pre.pop.yaml').read_bytes()
    post_bytes = (walk / 'post.pop.yaml').read_bytes()
    steps_bytes = (walk / 'steps.json').read_bytes()
    (root / 'model.orm.yaml').write_bytes(model_bytes)
    (root / 'input').mkdir()
    (root / 'input/pre.pop.yaml').write_bytes(pre_bytes)
    (candidate / 'plan').mkdir()
    (candidate / 'plan/steps.json').write_bytes(steps_bytes)
    (candidate / 'post.pop.yaml').write_bytes(post_bytes)
    test_bytes = b'def test_pass():\n    assert True\n'
    (candidate / 'test_mixed.py').write_bytes(test_bytes)

    def bound(path: str, data: bytes, media_type: str) -> dict[str, object]:
        return {'path': path, 'media_type': media_type, 'encoding': 'utf-8', 'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}
    test_argv = [sys.executable, '-m', 'pytest', '-q', 'test_mixed.py', '--junitxml=results.xml']
    argv_sha = hashlib.sha256(json.dumps(test_argv, ensure_ascii=False, separators=(',', ':')).encode()).hexdigest()
    model = bound('model.orm.yaml', model_bytes, 'application/yaml')
    pre = bound('input/pre.pop.yaml', pre_bytes, 'application/yaml')
    contract = {'schema_version': 4, 'experiment_id': experiment_id, 'max_attempts': 1, 'wall_seconds': 30.0, 'cases': [{'case_id': 'exact', 'role': 'required', 'inputs': [pre], 'acceptance': {'mode': 'exact-bytes', 'expected_outputs': [{'media_type': 'application/yaml', 'encoding': 'utf-8', 'sha256': hashlib.sha256(post_bytes).hexdigest(), 'output_id': 'post', 'candidate_path': 'post.pop.yaml', 'comparison': 'exact-bytes'}]}, 'verify': {'command': 'check', 'model': model, 'subject': 'post.pop.yaml'}}, {'case_id': 'tests', 'role': 'required', 'acceptance': {'mode': 'tests', 'required_tests': ['test_mixed.py::test_pass'], 'results_path': 'results.xml', 'results_format': 'junit-xml', 'protected': [bound('test_mixed.py', test_bytes, 'text/x-python')], 'test_argv_sha256': argv_sha}}, {'case_id': 'transition', 'role': 'required', 'inputs': [pre], 'acceptance': {'mode': 'transition'}, 'verify': {'command': 'transition', 'model': model, 'pre': 'input/pre.pop.yaml', 'steps': 'plan/steps.json', 'post': None}}]}
    (root / 'session.contract.json').write_text(json.dumps(contract, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n', encoding='utf-8')
    bin_dir = tmp_path / 'bin'
    bin_dir.mkdir()
    _write_fake_agent(bin_dir, 'codex')
    monkeypatch.setenv('PATH', f"{bin_dir}{os.pathsep}{os.environ.get('PATH', '')}")
    exit_code = main(['exp', 'run', str(root), '--adapter', 'codex', *[f'--test-argv={word}' for word in test_argv]])
    output = capsys.readouterr().out
    assert exit_code == 0, output
    result = json.loads(output)
    assert result['acceptance_modes'] == ['exact-bytes', 'tests', 'transition']
    feedback = json.loads((root / 'runs/run-0001/attempts/0001/feedback.json').read_text(encoding='utf-8'))
    assert feedback['schema_version'] == 5
    assert {row['case_id'] for row in feedback['required']} == {'exact', 'tests', 'transition'}
