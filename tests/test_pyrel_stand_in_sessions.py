"""PL3: the shipped stand-in agents are refused once with the pinned witness, then accepted."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'

DOMAINS = {
    'bookrec': {'model': 'model.orm.yaml', 'subject': 'recommendation.population.json', 'coverage': 'recommendation',
                'owned': ('recommendation',), 'witness': {'$b': 'night', '$u': 'ada'}, 'rule': 'constraints[1]',
                'accepted_rows': ('recommendation', [{'user': 'ada', 'book': 'map'}, {'user': 'ben', 'book': 'night'},
                                                     {'user': 'ada', 'book': 'cosmos'}])},
    'expense': {'model': 'model.orm.json', 'subject': 'approvals.population.json', 'coverage': 'expense_approved_by_chain',
                'owned': ('expense_is_approved', 'expense_approved_by_chain'), 'witness': {'$a': 800, '$e': 102},
                'rule': 'constraints[10]',
                'accepted_rows': ('expense_approved_by_chain', [{'expense': 103, 'chain': 'finance'},
                                                                {'expense': 102, 'chain': 'finance'}])},
}


def _gnd(*args, cwd):
    return subprocess.run([sys.executable, '-I', '-m', 'gnd', *args], cwd=cwd, capture_output=True,
                          text=True, timeout=600, check=False)


def _session(tmp_path, domain):
    spec = DOMAINS[domain]
    home = tmp_path / f'{domain}-native'
    shutil.copytree(str(files('gnd').joinpath('examples', domain)), home)
    experiment = tmp_path / ('EXP-003-recommend-ada' if domain == 'bookrec' else 'EXP-004-approve-102')
    assert _gnd('exp', 'init', experiment.name, '--out', '.', '--kind', 'data-driven',
                '--question', 'Q1=Does the stand-in converge?', cwd=tmp_path).returncode == 0
    (experiment / 'input').mkdir()
    (experiment / 'candidate').mkdir()
    shutil.copy(home / spec['model'], experiment / spec['model'])
    shutil.copy(home / 'seed.population.json', experiment / 'input/seed.population.json')

    def bound(path):
        data = (experiment / path).read_bytes()
        return {'path': path, 'media_type': 'application/json', 'encoding': 'utf-8',
                'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}

    contract = {'schema_version': 6, 'experiment_id': experiment.name, 'max_attempts': 3, 'wall_seconds': 300.0,
                'adapter': {'policy_id': 'local-command', 'parameters': {'model': None}},
                'cases': [{'case_id': 'required', 'role': 'required', 'inputs': [bound('input/seed.population.json')],
                           'acceptance': {'mode': 'constraint-satisfaction',
                                          'coverage': [{'fact_type': spec['coverage'], 'min_facts': 2}]},
                           'verify': {'command': 'check', 'model': bound(spec['model']), 'subject': spec['subject']}}]}
    (experiment / 'session.contract.json').write_text(json.dumps(contract, indent=2))
    policy = {'schema_version': 1, 'policy_id': 'local-command', 'kind': 'command', 'executable': sys.executable,
              'argv': [str(home / 'stand_in_agent.py')], 'version_argv': ['--version'],
              'prompt_transport': 'stdin', 'environment_allowlist': ['PATH', 'HOME', 'TMPDIR', 'LANG', 'LC_ALL']}
    (tmp_path / 'agent.policy.json').write_text(json.dumps(policy, indent=2))
    return home, experiment


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_stand_in_is_refused_then_accepted(tmp_path, domain):
    spec = DOMAINS[domain]
    _home, experiment = _session(tmp_path, domain)
    run = _gnd('exp', 'run', experiment.name, '--adapter-policy', 'agent.policy.json', cwd=tmp_path)
    assert run.returncode == 0, run.stderr + run.stdout
    result = json.loads((experiment / 'runs/run-0001/result.json').read_text())
    assert result['disposition'] == 'accepted' and result['attempt_count'] == 2
    first = json.loads((experiment / 'runs/run-0001/attempts/0001/feedback.json').read_text())
    violations = first['required'][0]['acceptance']['violations']
    assert first['disposition'] == 'retry' and first['payload_exit'] == [['required', 1]]
    assert [(v['constraint_ref'], v['offending_facts']) for v in violations] == [(spec['rule'], [spec['witness']])]
    second = json.loads((experiment / 'runs/run-0001/attempts/0002/feedback.json').read_text())
    assert second['disposition'] == 'accepted' and second['required'][0]['acceptance']['violations'] == []
    fact_type, rows = spec['accepted_rows']
    candidate = json.loads((experiment / 'runs/run-0001/attempts/0002/candidate' / spec['subject']).read_text())
    assert candidate['facts'][fact_type] == rows
    # The repaired value does not appear in the attempt-1 feedback: it names the offending facts only.
    repaired_value = 'cosmos' if domain == 'bookrec' else 'finance'
    assert repaired_value not in json.dumps(first)


@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_stand_in_version_probe_and_missing_feedback(tmp_path, domain):
    script = Path(str(files('gnd').joinpath('examples', domain, 'stand_in_agent.py')))
    probe = subprocess.run([sys.executable, str(script), '--version'], capture_output=True, text=True, timeout=30, check=False)
    assert probe.returncode == 0 and 'stand-in' in probe.stdout
    # No feedback at all: the first attempt obeys the request literally.
    (tmp_path / 'input').mkdir()
    (tmp_path / 'candidate').mkdir()
    shutil.copy(str(files('gnd').joinpath('examples', domain, 'seed.population.json')), tmp_path / 'input/seed.population.json')
    run = subprocess.run([sys.executable, str(script)], input='{"prompt": "x"}', cwd=tmp_path / 'candidate',
                         capture_output=True, text=True, timeout=30, check=False)
    assert run.returncode == 0, run.stderr
    candidate = json.loads((tmp_path / 'candidate' / DOMAINS[domain]['subject']).read_text())
    literal = {'user': 'ada', 'book': 'night'} if domain == 'bookrec' else {'expense': 102, 'chain': 'team-lead'}
    assert literal in candidate['facts'][DOMAINS[domain]['accepted_rows'][0]]
    # Without the seed, the stand-in says where it looked instead of a traceback.
    bare = subprocess.run([sys.executable, str(script)], input='{"prompt": "x"}', cwd=tmp_path,
                          capture_output=True, text=True, timeout=30, check=False)
    assert bare.returncode == 1 and 'expected the seed' in bare.stderr


@pytest.mark.pyrel_oracle
@pytest.mark.parametrize('domain', sorted(DOMAINS))
def test_accepted_candidate_passes_the_pyrel_app(tmp_path, domain):
    from gnd.export.applications import check_proposal, execute_application

    spec = DOMAINS[domain]
    home, experiment = _session(tmp_path, domain)
    assert _gnd('exp', 'run', experiment.name, '--adapter-policy', 'agent.policy.json', cwd=tmp_path).returncode == 0
    candidate = experiment / 'runs/run-0001/attempts/0002/candidate' / spec['subject']
    first = experiment / 'runs/run-0001/attempts/0001/candidate' / spec['subject']
    if domain == 'bookrec':
        accepted = check_proposal(home / spec['model'], home / 'seed.population.json', candidate,
                                  tmp_path / 'accepted.json', native_python=NATIVE, owned_relations=spec['owned'])
        refused = check_proposal(home / spec['model'], home / 'seed.population.json', first,
                                 tmp_path / 'refused.json', native_python=NATIVE, owned_relations=spec['owned'])
    else:
        accepted = execute_application(home / spec['model'], candidate, tmp_path / 'accepted.json',
                                       native_python=NATIVE, query_script=home / 'native_query.py',
                                       query_args=('report', '', ''))
        refused = execute_application(home / spec['model'], first, tmp_path / 'refused.json',
                                      native_python=NATIVE, query_script=home / 'native_query.py',
                                      query_args=('report', '', ''))
    assert accepted['exit_code'] == 0 and accepted['accepted']
    if domain == 'bookrec':
        assert sum(v['status'] == 'warning' for v in accepted['policy']['verdicts']) == 1
    else:
        assert accepted['calculation']['report']['approved'] == 2
    assert refused['exit_code'] == 1 and not refused['accepted']
    violated = [v for v in refused['policy']['verdicts'] if v['status'] == 'violated']
    assert [v['witnesses'] for v in violated] == [[spec['witness']]]
