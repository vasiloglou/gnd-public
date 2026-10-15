"""The PL17 recordings: real models behind the five plan apps, every run kept (offline checks)."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / 'src/gnd/examples/plan_apps'
RECORDINGS = APPS / 'recordings'
MODELS = ['claude-haiku', 'claude-default', 'llama-3.1-8b', 'gemma-3-4b', 'llama-3.2-3b']
EXAMPLES = ['course', 'access', 'lease', 'clinic', 'trip']
RESULTS = json.loads((RECORDINGS / 'results.json').read_text(encoding='utf-8'))


def _module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


sys.path.insert(0, str(APPS))
core = _module('plan_apps_core', APPS / 'core.py')
bot = _module('plan_app_bot', ROOT / 'tools/plan_app_bot.py')
recorder = _module('record_plan_apps', ROOT / 'tools/record_plan_apps.py')


def test_the_manifest_binds_every_recorded_file():
    manifest = json.loads((RECORDINGS / 'manifest.json').read_text(encoding='utf-8'))
    on_disk = {str(p.relative_to(RECORDINGS)) for p in RECORDINGS.rglob('*') if p.is_file()} - {'manifest.json', 'README.md', 'CAVEATS.md'}
    assert set(manifest['files']) == on_disk
    for name, digest in manifest['files'].items():
        assert hashlib.sha256((RECORDINGS / name).read_bytes()).hexdigest() == digest, name


def test_every_run_is_reported_in_recording_order():
    rows = RESULTS['runs']
    assert RESULTS['attempts_per_run'] == 3 and RESULTS['runs_per_model_and_example'] == 5
    assert [(r['model'], r['example'], r['run']) for r in rows] == [
        (m, e, n) for m in MODELS for e in EXAMPLES for n in range(1, 6)]
    for row in rows:
        folder = RECORDINGS / row['model'] / row['example'] / f"run-{row['run']}"
        assert (folder / 'session.txt').is_file()
        assert len(list(folder.glob('reply-*.json'))) == len(row['attempts']), folder


def test_no_recorded_file_holds_a_key_or_a_local_path():
    for path in RECORDINGS.rglob('*'):
        if path.is_file():
            text = path.read_text(encoding='utf-8')
            for needle in ('/Users/', '/private/', '/home/', '/var/folders/', '/tmp/', 'sk-or-', 'sk-ant-'):
                assert needle not in text, (path, needle)


def _attempts():
    for row in RESULTS['runs']:
        folder = RECORDINGS / row['model'] / row['example'] / f"run-{row['run']}"
        for n, attempt in enumerate(row['attempts'], 1):
            reply = json.loads((folder / f'reply-{n:02d}.json').read_text(encoding='utf-8'))
            yield row, n, attempt, reply


@pytest.mark.parametrize('example', EXAMPLES)
def test_gnd_gives_every_recorded_plan_the_recorded_exit(example, tmp_path):
    """The recording was checked by the PyRel program; GND re-checks each plan from the same state."""
    app = core.Example(APPS / example)
    checked = 0
    for row, n, attempt, reply in _attempts():
        if row['example'] != example:
            continue
        steps, reason = core.parse_answer(bot.plan_text(reply['reply']))
        if steps is None:
            assert attempt['unusable'], (row['model'], row['run'], n)
            continue
        if not steps:
            assert attempt['declined'] == reason, (row['model'], row['run'], n)
            continue
        plan = tmp_path / f"{row['model']}-{row['run']}-{n}.steps.json"
        plan.write_text(json.dumps(core.steps_document(app, steps)), encoding='utf-8')
        result = core.check(app, app.state, plan, 'gnd', None)
        assert result['exit'] == attempt['exit'], (row['model'], row['run'], n, result['failures'])
        checked += 1
    assert checked


def test_the_replay_choice_is_the_first_run_refused_on_a_rule_then_accepted():
    """A1: the docs replay the first run, in results.json order, refused with a rule and then accepted."""
    chosen = recorder.replay_choice(RESULTS['runs'])
    readme = (RECORDINGS / 'README.md').read_text(encoding='utf-8')
    if chosen is None:
        assert 'No run was refused and then accepted.' in readme
    else:
        assert f"Replayed run: `{chosen['model']}/{chosen['example']}/run-{chosen['run']}`" in readme


# ---------------------------------------------------------------- PL17 review B1: the index follows from the files

def _folder(row):
    return RECORDINGS / row['model'] / row['example'] / f"run-{row['run']}"


def test_each_row_is_the_summary_of_its_session():
    for row in RESULTS['runs']:
        session = (_folder(row) / 'session.txt').read_text(encoding='utf-8')
        assert recorder.summary(session) == row['attempts'], row['model'] + '/' + row['example'] + str(row['run'])
        assert len(re.findall(r'^attempt \d+$', session, re.M)) == len(row['attempts'])


def test_acceptance_and_app_exit_follow_from_the_attempts():
    for row in RESULTS['runs']:
        exits = [a['exit'] for a in row['attempts']]
        accepted = next((i for i, e in enumerate(exits, 1) if e == 0), None)
        assert row['accepted_at'] == accepted
        assert row['app_exit'] == (0 if accepted else 1), row
        assert accepted is None or accepted == len(exits)   # the loop stops at acceptance


def test_each_reply_answers_its_attempt_and_its_plan_is_the_one_printed():
    for row in RESULTS['runs']:
        session = (_folder(row) / 'session.txt').read_text(encoding='utf-8')
        blocks = re.split(r'^attempt \d+\n', session, flags=re.M)[1:]
        for n, (attempt, block) in enumerate(zip(row['attempts'], blocks), 1):
            reply = json.loads((_folder(row) / f'reply-{n:02d}.json').read_text(encoding='utf-8'))
            assert reply['attempt'] == n
            steps, reason = core.parse_answer(bot.plan_text(reply['reply']))
            printed = [line[len('  plan  '):] for line in block.splitlines() if line.startswith('  plan  ')]
            shown = [f"{s['op']}({', '.join(f'{k}={v!r}' for k, v in s['bindings'].items())})" for s in steps or []]
            assert printed == shown, (row['model'], row['example'], row['run'], n)
            assert (steps is None) == attempt['unusable']
            # printed verbatim by the recorded core, on one line by the current one
            said = {reason, ' '.join(reason.split())} if steps is not None and reason else {None}
            assert (attempt['declined'] if steps == [] else attempt['note']) in said, (row['model'], row['run'], n)


def test_each_reply_was_served_by_the_model_its_lane_names():
    for row in RESULTS['runs']:
        for reply in sorted(_folder(row).glob('reply-*.json')):
            data = json.loads(reply.read_text(encoding='utf-8'))
            served = data.get('served_model', data.get('model'))
            served = served if isinstance(served, list) else [served]
            if row['provider'] == 'openrouter':
                assert served == [row['model_id']], (reply, served)
            else:
                prefix = 'claude-haiku' if row['model'] == 'claude-haiku' else 'claude-'
                assert served and all(m.startswith(prefix) for m in served), (reply, served)
            assert sorted(set(served)) == sorted(set(served) & set(row['served_models']))


def test_the_readme_table_is_rebuilt_from_results():
    readme = (RECORDINGS / 'README.md').read_text(encoding='utf-8').splitlines()
    table = [line for line in readme if line.startswith('|')]
    assert table == recorder.readme_table(RESULTS['runs'])


def test_the_recording_names_its_checker_and_gate():
    assert RESULTS['backend'] == 'pyrel'
    assert RESULTS['gate'] == '.gnd-planning/milestones/pyrel-agent-loop/018-recording-gate-PL17.md'
    assert {r['question'] for r in RESULTS['runs']} == set(recorder.QUESTIONS.values())


def test_every_changed_source_is_declared():
    """B2: a source that changed since the recording is listed, with what changed, in the manifest and README."""
    manifest = json.loads((RECORDINGS / 'manifest.json').read_text(encoding='utf-8'))
    readme = (RECORDINGS / 'README.md').read_text(encoding='utf-8')
    for source, digest in manifest['sources'].items():
        if hashlib.sha256((ROOT / source).read_bytes()).hexdigest() != digest:
            assert source in manifest.get('drift', {}), source
            assert f'`{source}`' in readme, source
