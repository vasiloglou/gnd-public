"""PL17 review hardening: the recorder and the bot adapter (offline; no model is called)."""
from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECORDINGS = ROOT / 'src/gnd/examples/plan_apps/recordings'


def _recorder():
    spec = importlib.util.spec_from_file_location('record_plan_apps_t', ROOT / 'tools/record_plan_apps.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_h1_rebind_refuses_a_recording_that_does_not_match_its_manifest(tmp_path):
    copy = tmp_path / 'rec'
    shutil.copytree(RECORDINGS, copy)
    session = copy / 'gemma-3-4b/clinic/run-1/session.txt'
    session.write_text(session.read_text().replace('pyrel check: exit 1', 'pyrel check: exit 0 (accepted)', 1))
    run = subprocess.run([sys.executable, str(ROOT / 'tools/record_plan_apps.py'), '--authorized-by', 'x', '--out',
                          str(copy), '--rebind', '--env-file', str(tmp_path / 'none.env')],
                         capture_output=True, text=True, timeout=120, check=False)
    assert run.returncode != 0 and 'does not match its manifest' in run.stderr, run.stdout + run.stderr


def test_h1_rebind_of_an_unchanged_recording_records_nothing(tmp_path):
    copy = tmp_path / 'rec'
    shutil.copytree(RECORDINGS, copy)
    recorder = _recorder()
    before = (copy / 'manifest.json').read_text()
    assert recorder.rebind(copy, None) == 0
    assert (copy / 'manifest.json').read_text() == before


def test_h4_a_failed_call_is_logged_under_its_attempt(tmp_path):
    prompt = {'question': 'q', 'rules': 'r', 'operations': [], 'state': {}, 'attempts': [
        {'plan': None, 'failures': []}]}
    env = {'PATH': '/usr/bin:/bin', 'HOME': str(tmp_path)}   # no OPENROUTER_API_KEY: the call fails
    run = subprocess.run([sys.executable, str(ROOT / 'tools/plan_app_bot.py'), '--provider', 'openrouter',
                          '--model', 'm', '--log', str(tmp_path / 'log')], input=json.dumps(prompt),
                         capture_output=True, text=True, timeout=60, env=env, check=False)
    assert run.returncode != 0
    record = json.loads((tmp_path / 'log/reply-02.json').read_text())
    assert record['attempt'] == 2 and 'OPENROUTER_API_KEY' in record['error'] and record['requested_model'] == 'm'


def test_h7_linux_temporary_paths_are_redacted_and_searched(tmp_path):
    recorder = _recorder()
    assert recorder.redact('/tmp/gnd-plan-abc123/plan.steps.json: refused', []) == '<tmp>/plan.steps.json: refused'
    (tmp_path / 'a.txt').write_text('see /tmp/other/file')
    assert recorder.leaks(tmp_path, None) == ['a.txt']


def test_h3_summary_keeps_warnings_unchecked_rules_and_refusal_codes():
    recorder = _recorder()
    session = ('attempt 1\n  plan  x(a=1)\n  pyrel check: exit 3\n'
               '    plan  refused  refused  <tmp>/p.json: refused: [transition:binding-type] step 1.a\n'
               'attempt 2\n  plan  x(a=1)\n  pyrel check: exit 0 (accepted)\n'
               '    state 1  late  warning  [["a"]]\n'
               '    states 0-1  judgement  not checked  a textual rule\n')
    first, second = recorder.summary(session)
    assert first['refusals'] == ['transition:binding-type'] and first['failures'] == [['refused', 'refused']]
    assert second['exit'] == 0 and second['failures'] == [['judgement', 'not checked'], ['late', 'warning']]
