"""PL4: the recorder refuses to run unauthorized, and the key wrapper imports exactly one name."""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDER = ROOT / 'tools/record_pyrel_sessions.py'
WRAPPER = ROOT / 'tools/agent_with_env_key.py'


def _run(argv, **kwargs):
    return subprocess.run([sys.executable, *map(str, argv)], capture_output=True, text=True, timeout=120,
                          check=False, **kwargs)


def test_recorder_refuses_without_a_gate_record(tmp_path):
    missing = _run([RECORDER, '--authorized-by', tmp_path / 'absent.md', '--dry-run'])
    assert missing.returncode == 2 and 'gate record' in missing.stderr
    unrelated = tmp_path / 'note.md'
    unrelated.write_text('# A note about nothing\n')
    assert _run([RECORDER, '--authorized-by', unrelated, '--dry-run']).returncode == 2


def test_recorder_dry_run_lists_the_plan():
    gate = ROOT / '.gnd-planning/milestones/pyrel-agent-loop/005-recording-gate.md'
    run = _run([RECORDER, '--authorized-by', gate, '--dry-run', '--agents', 'codex', '--runs', '1'])
    assert run.returncode == 0
    assert run.stdout.count('would run') == 4  # 2 domains x 2 variants x 1 run
    assert 'claude' not in run.stdout


def test_wrapper_imports_exactly_one_name(tmp_path):
    env_file = tmp_path / 'keys.env'
    env_file.write_text('OTHER_KEY=do-not-import\nexport DEMO_KEY="value-123"\n')
    probe = tmp_path / 'probe.py'
    probe.write_text('import os, sys\nprint(os.environ.get("DEMO_KEY"), os.environ.get("OTHER_KEY"))\n')
    env = {'PATH': os.environ['PATH'], 'HOME': os.environ.get('HOME', '')}
    run = _run([WRAPPER, '--env-file', env_file, '--name', 'DEMO_KEY', '--', sys.executable, str(probe)], env=env)
    assert run.returncode == 0 and run.stdout.strip() == 'value-123 None'


def test_wrapper_refuses_a_missing_or_empty_key(tmp_path):
    env_file = tmp_path / 'keys.env'
    env_file.write_text('DEMO_KEY=\n')
    run = _run([WRAPPER, '--env-file', env_file, '--name', 'DEMO_KEY', '--', sys.executable, '-c', 'pass'])
    assert run.returncode == 1 and 'empty' in run.stderr
    env_file.write_text('SOMETHING_ELSE=x\n')
    run = _run([WRAPPER, '--env-file', env_file, '--name', 'DEMO_KEY', '--', sys.executable, '-c', 'pass'])
    assert run.returncode == 1 and 'not set' in run.stderr


def test_wrapper_refuses_an_oversized_env_file(tmp_path):
    env_file = tmp_path / 'keys.env'
    env_file.write_bytes(b'A=' + b'x' * (64 * 1024) + b'\n')
    run = _run([WRAPPER, '--env-file', env_file, '--name', 'A', '--', sys.executable, '-c', 'pass'])
    assert run.returncode == 1 and 'larger' in run.stderr


def test_wrapper_version_probe_needs_no_key(tmp_path):
    run = _run([WRAPPER, '--env-file', tmp_path / 'absent.env', '--name', 'DEMO_KEY', '--', sys.executable, '--version'])
    assert run.returncode == 0 and run.stdout.startswith('Python')
