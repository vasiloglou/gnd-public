from __future__ import annotations

import hashlib
import importlib
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from gnd import cli

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = json.loads((ROOT / 'tests/fixtures/v63-phase4/answers.json').read_text(encoding='utf-8'))['cases']

def _cli_runner():
    return importlib.import_module('support.cli_runner')

def _repository():
    return importlib.import_module('support.repository')

def _documents():
    return importlib.import_module('support.documents')

def _parity():
    return importlib.import_module('support.phase4_parity')

def _timeout_observation() -> dict[str, object]:
    _cli_runner()
    driver = "import subprocess, sys\nfrom support.cli_runner import run_process\ntry:\n    run_process([sys.executable, '-c', 'import time;time.sleep(10)'], timeout=0.05)\nexcept subprocess.TimeoutExpired:\n    print('TimeoutExpired')\nelse:\n    print('NO_TIMEOUT')\n"
    environment = {**os.environ, 'PYTHONPATH': str(ROOT / 'tests')}
    completed = subprocess.run([sys.executable, '-c', driver], cwd=ROOT, env=environment, capture_output=True, text=True, check=False, timeout=ANSWERS['H04']['outer_timeout_seconds'])
    assert completed.returncode == 0, completed.stderr
    return {'exception': completed.stdout.strip(), 'outer_timeout_seconds': ANSWERS['H04']['outer_timeout_seconds']}

def _exact_observation(case_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> dict[str, object]:
    if case_id == 'H01':
        argv = (sys.executable, '-c', "import sys;sys.stdout.buffer.write(bytes.fromhex('cea10d0a'));sys.stderr.buffer.write(bytes.fromhex('ff0a'))")
        result = _cli_runner().run_process(argv)
        assert result.argv == argv
        return {'exit': result.returncode, 'stdout_hex': result.stdout.hex(), 'stderr_hex': result.stderr.hex()}
    if case_id == 'H02':
        argv = (sys.executable, '-c', "import sys;sys.stdout.buffer.write(b'partial\\n');sys.stderr.buffer.write(b'problem\\n');sys.exit(7)")
        result = _cli_runner().run_process(argv)
        assert result.argv == argv
        return {'exit': result.returncode, 'stdout_hex': result.stdout.hex(), 'stderr_hex': result.stderr.hex()}
    if case_id == 'H04':
        return _timeout_observation()
    if case_id == 'H07':

        def usage_error(_argv: object) -> int:
            print('usage', file=sys.stderr)
            raise SystemExit(64)
        monkeypatch.setattr(cli, 'main', usage_error)
        result = _cli_runner().run_main(['bad'])
        return {'exit': result.returncode, 'stderr_hex': result.stderr.hex()}
    if case_id == 'H11':
        documents = _documents()
        model = documents.write_model(tmp_path, 'mødel\n')
        population = documents.write_population(tmp_path, bytes.fromhex('00ff0a'))
        assert model == tmp_path / ANSWERS['H11']['model_name']
        assert population == tmp_path / ANSWERS['H11']['population_name']
        with pytest.raises(FileNotFoundError) as error:
            documents.write_model(tmp_path / 'missing', 'x')
        return {'model_name': model.name, 'model_hex': model.read_bytes().hex(), 'population_name': population.name, 'population_hex': population.read_bytes().hex(), 'missing_parent_exception': type(error.value).__name__}
    raise AssertionError(f'unknown exact case: {case_id}')

@pytest.mark.parametrize('case_id', ('H01', 'H02', 'H04', 'H07', 'H11'))
def test_exact_answer(case_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    assert _exact_observation(case_id, tmp_path, monkeypatch) == ANSWERS[case_id]

@pytest.mark.parametrize('case_id', ('H01', 'H02', 'H04', 'H07', 'H11'))
def test_one_answer_mutation_is_detected(case_id: str, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    actual = _exact_observation(case_id, tmp_path, monkeypatch)
    assert actual == ANSWERS[case_id]
    changed = dict(ANSWERS[case_id])
    field = next(iter(changed))
    changed[field] = 'deliberately-wrong'
    with pytest.raises(AssertionError):
        assert actual == changed

def test_h03_cwd_env_and_stdin(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv(ANSWERS['H03']['env_name'], 'inherited')
    script = "import hashlib,os,sys;print(os.getcwd());print(os.environ['GND_PHASE4_SENTINEL']);print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())"
    argv = [sys.executable, '-c', script]
    supplied = bytes.fromhex(ANSWERS['H03']['stdin_hex'])
    explicit = _cli_runner().run_process(argv, cwd=tmp_path, env={**os.environ, ANSWERS['H03']['env_name']: ANSWERS['H03']['env_value']}, stdin=supplied)
    assert explicit.returncode == 0
    assert explicit.stdout.decode().splitlines() == [str(tmp_path), ANSWERS['H03']['env_value'], hashlib.sha256(supplied).hexdigest()]
    inherited = _cli_runner().run_process(argv)
    assert inherited.returncode == 0
    assert inherited.stdout.decode().splitlines() == [os.getcwd(), 'inherited', hashlib.sha256(b'').hexdigest()]

def test_h05_spawn_error(tmp_path: Path) -> None:
    with pytest.raises(OSError) as error:
        _cli_runner().run_process([str(tmp_path / 'absent-program')])
    assert ANSWERS['H05']['exception'] in {base.__name__ for base in type(error.value).__mro__}

def test_h06_main_success_restores_cwd(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original = Path.cwd()

    def success(_argv: object) -> int:
        assert Path.cwd() == tmp_path
        print('ok')
        print('note', file=sys.stderr)
        return 0
    monkeypatch.setattr(cli, 'main', success)
    result = _cli_runner().run_main(['example'], cwd=tmp_path)
    assert Path.cwd() == original
    assert result.returncode == ANSWERS['H06']['exit']
    assert result.stdout.hex() == ANSWERS['H06']['stdout_hex']
    assert result.stderr.hex() == ANSWERS['H06']['stderr_hex']

def test_h08_main_exception_restores_process_state(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    original_cwd = Path.cwd()
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    def crash(_argv: object) -> int:
        assert Path.cwd() == tmp_path
        raise RuntimeError('sentinel')
    monkeypatch.setattr(cli, 'main', crash)
    with pytest.raises(RuntimeError) as error:
        _cli_runner().run_main(['example'], cwd=tmp_path)
    assert type(error.value).__name__ == ANSWERS['H08']['exception']
    assert Path.cwd() == original_cwd
    assert sys.stdout is original_stdout
    assert sys.stderr is original_stderr

def test_h12_root_and_explicit_alternate_git_root(tmp_path: Path) -> None:
    repository = _repository()
    assert repository.REPO_ROOT == ROOT
    imported = subprocess.run([sys.executable, '-c', 'from support.repository import REPO_ROOT; print(REPO_ROOT)'], cwd=tmp_path, env={**os.environ, 'PYTHONPATH': str(ROOT / 'tests')}, capture_output=True, text=True, check=True)
    assert imported.stdout.strip() == str(ROOT)
    subprocess.run(['git', 'init', '-q', str(tmp_path)], check=True)
    (tmp_path / 'blob.txt').write_bytes(bytes.fromhex(ANSWERS['H12']['alternate_blob_hex']))
    subprocess.run(['git', '-C', str(tmp_path), 'add', 'blob.txt'], check=True)
    subprocess.run(['git', '-C', str(tmp_path), '-c', 'user.name=Phase Four', '-c', 'user.email=phase4@example.invalid', 'commit', '-qm', 'fixture'], check=True)
    assert repository.git_blob('HEAD', 'blob.txt', root=tmp_path).hex() == ANSWERS['H12']['alternate_blob_hex']

def test_h14_parity_reports_changed_fields() -> None:
    parity = _parity()
    before = parity.NodeObservation('node', 'default', 'failed', 'AssertionError', '<1s')
    after = parity.NodeObservation('node', 'default', 'failed', 'ValueError', '1--10s')
    deltas = parity.compare_nodes({'node': before}, {'node': after})
    assert sorted(delta.field for delta in deltas) == ANSWERS['H14']['changed_fields']
    missing = parity.compare_nodes({'node': before}, {})
    assert any(delta.nodeid == 'node' for delta in missing)
    extra = parity.compare_nodes({}, {'node': after})
    assert any(delta.nodeid == 'node' and delta.field == 'nodeid' for delta in extra)

def test_text_projection_matches_subprocess_text_mode() -> None:
    runner = _cli_runner()
    argv = [sys.executable, '-c', "import sys;sys.stdout.buffer.write(bytes.fromhex('cea10d0a'));sys.stderr.buffer.write(b'warning\\r\\n')"]
    expected = subprocess.run(argv, capture_output=True, text=True, check=False)
    actual = runner.completed_text(runner.run_process(argv))
    assert actual.args == expected.args
    assert (actual.returncode, actual.stdout, actual.stderr) == (expected.returncode, expected.stdout, expected.stderr)
    undecodable = [sys.executable, '-c', "import sys;sys.stdout.buffer.write(bytes.fromhex('ff0a'))"]
    with pytest.raises(UnicodeDecodeError):
        subprocess.run(undecodable, capture_output=True, text=True, check=False)
    with pytest.raises(UnicodeDecodeError):
        runner.completed_text(runner.run_process(undecodable))

def test_gnd_text_runner_preserves_success_and_usage_failure() -> None:
    runner = _cli_runner()
    for arguments in (('--help',), ('not-a-command',)):
        expected = subprocess.run([sys.executable, '-m', 'gnd', *arguments], cwd=ROOT, capture_output=True, text=True, check=False)
        actual = runner.run_gnd_text(*arguments)
        assert (actual.args, actual.returncode, actual.stdout, actual.stderr) == (expected.args, expected.returncode, expected.stdout, expected.stderr)

def test_run_main_preserves_surrogate_text(monkeypatch: pytest.MonkeyPatch) -> None:

    def surrogate(_argv: object) -> int:
        sys.stdout.write(chr(56575))
        return 0
    monkeypatch.setattr(cli, 'main', surrogate)
    result = _cli_runner().run_main(['surrogate'])
    assert result.stdout.decode('utf-8', errors='surrogatepass') == chr(56575)
