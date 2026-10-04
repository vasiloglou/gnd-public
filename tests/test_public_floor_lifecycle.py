from __future__ import annotations

import asyncio
import atexit
import hashlib
import importlib.util
import json
import tempfile
from pathlib import Path

import pytest

from gnd.exp import close as close_module

PUBLIC = Path(__file__).parent / 'fixtures/public-walk-floor'
CONTRACT = {'driver': 'tests/fixtures/v61-phase5/installed/driver.py', 'required_observations': ['contract-v5', 'feedback-v7', 'attempt-v7', 'result-v5', 'accepted-floor', 'deficient-floor', 'accepted-parent-exit', 'deficient-parent-exit', 'close-accepted', 'close-refused', 'evidence-not-current']}
BINDINGS = {'model.orm.yaml': {'sha256': '0f63a6d97778d55322a303977494e3f999d86ac69cb1d85dd9f93a63f7e29f5c', 'bytes': 2174}, 'input/pre.pop.yaml': {'sha256': '721b02fc5a6e047d1da2c0a9f4b116398a217213b9b90ccc4c1d0dd2c14974dc', 'bytes': 224}, 'contract-v5.json': {'sha256': '4daa5d64d486e7640643912a5de9c498afd1c4f47816c6a2ebb05273ea6e02a1', 'bytes': 2053}, 'candidate/steps.json': {'sha256': '16bcf394a717693a6b5ec5a455754266dd63d2bbfee7996fb756573b2a4b576f', 'bytes': 460}}

def _materialize():
    temporary = tempfile.TemporaryDirectory(prefix='gnd-public-floor-lifecycle-')
    root = Path(temporary.name)
    fixture = root / 'tests/fixtures/v61-phase5/session'
    for relative, expected in BINDINGS.items():
        source = PUBLIC / 'session' / relative
        assert source.is_file() and not source.is_symlink()
        with source.open('rb') as stream:
            data = stream.read(8193)
        assert len(data) == expected['bytes'] <= 8192
        assert hashlib.sha256(data).hexdigest() == expected['sha256']
        path = fixture / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        path.chmod(0o644)
    source = PUBLIC / 'runner.py'
    assert source.is_file() and not source.is_symlink()
    with source.open('rb') as stream:
        data = stream.read(32769)
    assert len(data) <= 32768
    assert hashlib.sha256(data).hexdigest() == 'a60f1bb36c284644bd86c1a69e8d1a8ca5f72a5b79cf4cf7d12c9fc31b6ebf8e'
    driver = root / CONTRACT['driver']
    driver.parent.mkdir(parents=True, exist_ok=True)
    driver.write_bytes(data)
    driver.chmod(0o644)
    return temporary, root

_TEMPORARY, ROOT = _materialize()
atexit.register(_TEMPORARY.cleanup)


def _load_driver():
    path = ROOT / CONTRACT['driver']
    spec = importlib.util.spec_from_file_location('v61_phase5_installed_driver', path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def test_review_05_refused_walk_persists_and_replays_as_nonaccepted() -> None:
    with tempfile.TemporaryDirectory(prefix='gnd-phase5-refused-') as temporary:
        result, _feedback, _attempt = asyncio.run(_load_driver()._run(ROOT, Path(temporary), refused=True))
    assert result.disposition.value != 'accepted'

def test_review_06_result_rows_are_sorted_independently_of_contract_order() -> None:
    with tempfile.TemporaryDirectory(prefix='gnd-phase5-reordered-') as temporary:
        result, _feedback, _attempt = asyncio.run(_load_driver()._run(ROOT, Path(temporary), reordered=True))
    assert [row.case_id for row in result.walk_floors] == ['a-floor', 'z-floor']

CONTRACT_BYTES = (PUBLIC / "session/contract-v5.json").read_bytes()
ANSWERS = json.loads((PUBLIC / "answers.json").read_text(encoding="utf-8"))

def test_k01_result_v5_accounts_for_exact_declaration_and_closes(tmp_path: Path) -> None:
    result, _feedback, _attempt = asyncio.run(_load_driver()._run(ROOT, tmp_path))
    experiment = tmp_path / 'accepted'
    (experiment / 'session.contract.json').write_bytes(CONTRACT_BYTES)
    run_root = experiment / 'runs/run-0001'
    run = close_module._SessionRun(index=1, root=run_root, result=None, launched=True)
    assert result.schema_version == ANSWERS['versions']['result'] == 5
    assert close_module._declared_case_findings(run, experiment, (run_root / 'result.json').read_bytes()) == []

ANSWERS.update({'accepted_parent_exit': 0, 'deficient_parent_exit': 15, 'close_accepted_exit': 0, 'close_refused_exit': 14})

def test_installed_driver_observes_successor_wires_and_both_floor_outcomes() -> None:
    observations = _load_driver().observe(ROOT)
    assert set(observations) == set(CONTRACT['required_observations'])
    assert observations['contract-v5'] == 5
    assert observations['feedback-v7'] is True
    assert observations['attempt-v7'] is True
    assert observations['result-v5'] is True
    assert observations['accepted-floor'] is True
    assert observations['deficient-floor'] is True
    assert observations['accepted-parent-exit'] == ANSWERS['accepted_parent_exit']
    assert observations['deficient-parent-exit'] == ANSWERS['deficient_parent_exit']
    assert observations['close-accepted'] == ANSWERS['close_accepted_exit']
    assert observations['close-refused'] == ANSWERS['close_refused_exit']

def test_installed_answer_negative_control_rejects_one_changed_exit() -> None:
    observations = _load_driver().observe(ROOT)
    dirty = dict(observations)
    dirty['close-refused'] = 0
    with pytest.raises(AssertionError):
        assert dirty['close-refused'] == ANSWERS['close_refused_exit']
