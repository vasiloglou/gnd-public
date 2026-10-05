from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest
from ruamel.yaml import YAML

REPO_ROOT = Path(__file__).resolve().parent.parent
CORPUS = Path(__file__).parent / 'fixtures' / 'adversarial'
MANIFEST = CORPUS / 'manifest.yaml'

def _cases() -> list[dict[str, Any]]:
    doc = YAML(typ='safe').load(MANIFEST.read_text(encoding='utf-8'))
    return list(doc['cases'])
CASES = _cases()

def _argv(case: dict[str, Any]) -> list[str]:
    command = str(case.get('command', 'check'))
    argv = [sys.executable, '-m', 'gnd', command, str(CORPUS / case['model'])]
    if command == 'check':
        argv.append(str(CORPUS / case['population']))
    return [*argv, '--format', 'json']

def _context(case: dict[str, Any], result: subprocess.CompletedProcess[str]) -> str:
    return f"\nWhy this case exists: {case['why']}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"

def _payload(case: dict[str, Any], result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        pytest.fail(f"{case['id']}: expected a --format json payload on stdout, but it could not be parsed ({error}). The payload is absent or malformed." + _context(case, result))

@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_adversarial_case(case: dict[str, Any]) -> None:
    result = subprocess.run(_argv(case), capture_output=True, text=True, check=False, cwd=REPO_ROOT)
    assert result.returncode == case['expected_exit'], f"{case['id']}: expected exit {case['expected_exit']}, got {result.returncode}." + _context(case, result)
    expected_rule_ids = list(case.get('expect_rule_ids') or [])
    expected_reason_codes = list(case.get('expect_reason_codes') or [])
    if not expected_rule_ids and (not expected_reason_codes):
        return
    payload = _payload(case, result)
    observed_rule_ids = [issue.get('rule_id') for issue in payload.get('issues') or []]
    for rule_id in expected_rule_ids:
        assert rule_id in observed_rule_ids, f"{case['id']}: expected rule_id {rule_id!r} in issues[], got {observed_rule_ids!r} — the exit code may be right for the wrong reason." + _context(case, result)
    observed_reason_codes = [verdict.get('reason_code') for verdict in payload.get('verdicts') or []]
    for reason_code in expected_reason_codes:
        assert reason_code in observed_reason_codes, f"{case['id']}: expected reason_code {reason_code!r} in verdicts[], got {observed_reason_codes!r} — the exit code may be right for the wrong reason." + _context(case, result)
