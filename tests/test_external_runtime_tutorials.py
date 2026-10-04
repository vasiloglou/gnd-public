"""Focused controls for lane selection and the supplied governance views."""
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

from gnd.api import check, validate

ROOT = Path(__file__).resolve().parents[1]
RESOURCES = ROOT / 'src/gnd/examples/release_governance'
spec = importlib.util.spec_from_file_location('tutorial_lanes', ROOT / 'tools/run_tutorials.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


def page(tmp_path, text):
    path = tmp_path / 'lesson.md'
    path.write_text(text)
    return path


@pytest.mark.parametrize('lane', ['unknown', 'all'])
def test_unknown_block_lane_refused(tmp_path, lane):
    lesson = page(tmp_path, f'<!-- gnd-run expect=0 lane={lane} -->\n```python\npass\n```')
    with pytest.raises(AssertionError, match='unknown executable lane'):
        runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable))


def test_offline_skips_native_without_calling_preflight(tmp_path, monkeypatch, capsys):
    lesson = page(tmp_path, '<!-- gnd-run expect=0 -->\n```python\nfrom pathlib import Path\nPath("ready").touch()\n```\n<!-- gnd-run expect=0 lane=lean -->\n```python\nraise RuntimeError("must not execute")\n```')
    monkeypatch.setattr(runner, 'require_runtime', lambda *a: pytest.fail('offline called a tool'))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable)) == 1
    assert 'Native lanes not executed: lean' in capsys.readouterr().out


@pytest.mark.parametrize('lane', ['pyrel', 'souffle', 'lean', 'all'])
def test_native_executes_prerequisite_first(tmp_path, monkeypatch, lane):
    chosen = 'pyrel' if lane == 'all' else lane
    lesson = page(tmp_path, f'<!-- gnd-run expect=0 -->\n```python\nfrom pathlib import Path\nPath("ready").touch()\n```\n<!-- gnd-run expect=0 lane={chosen} -->\n```python\nfrom pathlib import Path\nassert Path("ready").exists()\nPath("native").touch()\n```')
    calls = []
    monkeypatch.setattr(runner, 'require_runtime', lambda *a: calls.append(a[0]))
    assert runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable), lane) == 2
    assert calls == [chosen] and (tmp_path / 'work/native').is_file()


def test_missing_tool_is_failure_not_skip(tmp_path, monkeypatch):
    lesson = page(tmp_path, '<!-- gnd-run expect=0 lane=lean -->\n```python\npass\n```')
    monkeypatch.setattr(runner.shutil, 'which', lambda *a, **k: None)
    with pytest.raises(AssertionError, match='required tool absent'):
        runner.run_pages([lesson], tmp_path / 'work', Path(sys.executable), 'lean')


@pytest.mark.parametrize('lane,output', [('lean', 'Lake version 4.33.0'), ('souffle', 'Version: 2.4\nWord size: 64 bits'), ('souffle', 'Version: 2.5\nWord size: 32 bits'), ('pyrel', 'PyRel 1.34.0'), ('pyrel', 'PyRel 1.30.1\nDuckDB 1.5.4')])
def test_wrong_runtime_version_refused(monkeypatch, lane, output):
    monkeypatch.setattr(runner.shutil, 'which', lambda *a, **k: '/tool')
    monkeypatch.setattr(runner.subprocess, 'run', lambda *a, **k: SimpleNamespace(returncode=0, stdout=output, stderr=''))
    with pytest.raises(AssertionError, match='required'):
        runner.require_runtime(lane, Path(sys.executable), {'PATH': '/bin'})


def test_separate_pyrel_interpreter_selected(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(runner.subprocess, 'run', lambda argv, **kwargs: calls.append(argv) or SimpleNamespace(returncode=0, stdout='PyRel 1.30.1\nDuckDB 1.5.5', stderr=''))
    runner.require_runtime('pyrel', Path('/gnd/python'), {'PATH': '/bin', 'GND_TUTORIAL_PYREL_PYTHON': '/pyrel/python'})
    assert calls[0][0] == '/pyrel/python'


@pytest.mark.parametrize('profile', ['policy', 'dependencies', 'approval-proof'])
def test_named_views_validate(profile):
    assert validate(RESOURCES / profile / 'model.orm.json')['exit_code'] == 0


def test_policy_failures_and_repair():
    root = RESOURCES / 'policy'
    bad = check(root / 'model.orm.json', root / 'invalid.pop.json', unredacted=True)
    assert bad['exit_code'] == 1
    assert [row['constraint_type'] for row in bad['verdicts']] == ['mandatory', 'uniqueness', 'subset']
    assert bad['verdicts'][0]['offending_facts'] == ['REL-103']
    assert bad['verdicts'][2]['offending_facts'] == [['Alice'], ['Zoe']]
    assert check(root / 'model.orm.json', root / 'repaired.pop.json')['exit_code'] == 0


@pytest.mark.parametrize('variant', ['repaired', 'patched', 'cycle'])
def test_derivation_snapshots_check_actual_results(variant):
    root = RESOURCES / 'dependencies'
    result = check(root / 'model.orm.json', root / f'{variant}.pop.json')
    assert result['exit_code'] == 0 and result['counts']['pass'] == 6


def test_model_views_map_supplied_business_facts():
    scenario = json.loads((RESOURCES / 'scenario-repaired.json').read_text())
    policy = json.loads((RESOURCES / 'policy/repaired.pop.json').read_text())['facts']
    graph = json.loads((RESOURCES / 'dependencies/repaired.base.pop.json').read_text())['facts']
    proof = json.loads((RESOURCES / 'approval-proof/repaired.pop.json').read_text())['facts']
    assert [[r['release'], r['service'], r['requester']] for r in policy['request']] == scenario['requests']
    assert [[r['release'], r['reviewer']] for r in policy['approval']] == scenario['approvals']
    assert [[r['service'], r['dependency']] for r in graph['dependency']] == scenario['dependencies']
    assert [r['release'] for r in proof['approved']] == [r for r, _ in scenario['approvals']]
    assert [r['release'] for r in proof['reviewed']] == scenario['reviewed']


@pytest.mark.parametrize('name', ['pyproject.toml', 'uv.lock'])
def test_packaged_runtime_lock_matches_maintained_project(name):
    assert (RESOURCES / 'runtime-environment' / name).read_bytes() == (ROOT / 'tutorials/runtimes' / name).read_bytes()


def test_checkpoint_identities_and_semantic_outputs():
    root = RESOURCES / 'checkpoints'
    manifest = json.loads((root / 'manifest.json').read_text())
    for relative, digest in manifest['inputs'].items():
        assert hashlib.sha256((RESOURCES / relative).read_bytes()).hexdigest() == digest
    for relative, digest in manifest['outputs'].items():
        assert hashlib.sha256((root / relative).read_bytes()).hexdigest() == digest
    good = json.loads((root / 'pyrel-repaired.json').read_text())
    assert [r['status'] for r in good['verdicts']] == ['satisfied'] * 3
    graph = json.loads((root / 'souffle-repaired.json').read_text())
    assert sorted(r[0]['value'] for r in graph['extensions']['affected']) == ['checkout', 'identity', 'ledger', 'payments']
