"""Original-source RF5 handler observations; unchanged answers after moves."""
from __future__ import annotations

import importlib
import json
import sys
from pathlib import Path

import pytest
from support.cli_runner import run_main
from support.repository import REPO_ROOT
from support.rf5_sources import HOMES

CORPUS = REPO_ROOT / 'tests/fixtures/rf5-handlers'
CASES = json.loads((CORPUS / 'cases.json').read_text())
ANSWERS = json.loads((CORPUS / 'answers.json').read_text())


def observe(case, tmp_path, monkeypatch):
    monkeypatch.setenv('HOME', str(tmp_path / 'home'))
    monkeypatch.setenv('PATH', str(Path(sys.executable).parent))
    monkeypatch.setenv('COLUMNS', '80')
    monkeypatch.setenv('NO_COLOR', '1')
    (tmp_path / 'home').mkdir(exist_ok=True)
    argv = [part.replace('<repo>', str(REPO_ROOT)) for part in case['argv']]
    result = run_main(argv, cwd=tmp_path)

    def clean(raw):
        decoded = raw.decode('utf-8', errors='surrogatepass')
        if case['id'] == 'doctor':
            decoded = decoded.replace(str(Path(sys.executable).parent), str(REPO_ROOT / '.venv/bin'))
        return (decoded
                .replace(str(tmp_path), '<case>')
                .replace(str(REPO_ROOT), '<repo>')
                .replace(str(Path(sys.executable)), '<python>'))

    return {'exit': result.returncode, 'stdout': clean(result.stdout), 'stderr': clean(result.stderr)}


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_original_handler_bytes(case, tmp_path, monkeypatch):
    assert observe(case, tmp_path, monkeypatch) == ANSWERS[case['id']]


@pytest.mark.parametrize('case', CASES, ids=lambda case: case['id'])
def test_handler_disabling_control_changes_the_observation(case, tmp_path, monkeypatch):
    module, name = case['target'].rsplit('.', 1)
    if module == 'gnd.cli':
        module = HOMES[name]
    monkeypatch.setattr(importlib.import_module(module), name,
                        lambda *args, **kwargs: {'outcome': 0} if case['id']=='judgments check' else 0)
    assert observe(case, tmp_path, monkeypatch) != ANSWERS[case['id']], 'pin missed its actual handler'
