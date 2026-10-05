"""The required PR check must reject failed, skipped and missing acceptance jobs."""
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('state', ['success', 'failure', 'cancelled', 'skipped', 'missing'])
@pytest.mark.parametrize('job', ['candidate', 'regression', 'installed'])
def test_required_check_fails_closed(job, state):
    workflow = YAML(typ='safe').load((ROOT / '.github/workflows/development.yml').read_text())
    gate = workflow['jobs']['phase2']
    assert set(gate['needs']) == {'candidate', 'regression', 'installed'}
    assert gate['if'] == 'always()'
    results = {name: {'result': 'success'} for name in gate['needs']}
    if state == 'missing':
        del results[job]
    else:
        results[job]['result'] = state
    script = gate['steps'][0]['run'].split("python - <<'PY'\n", 1)[1].rsplit('\nPY', 1)[0]
    run = subprocess.run([sys.executable, '-c', script], capture_output=True, check=False,
                         env={**os.environ, 'RESULTS': json.dumps(results)}, timeout=10)
    assert (run.returncode == 0) == (state == 'success')


def test_contribution_policy_requires_pull_requests():
    for name in ['AGENTS.md', 'CONTRIBUTING.md']:
        text = (ROOT / name).read_text()
        assert 'submit a pull request' in text
        assert 'Never push directly to main' in text


def test_installed_jobs_consume_same_candidate_without_rebuilding():
    workflow = YAML(typ='safe').load((ROOT / '.github/workflows/development.yml').read_text())
    installed = workflow['jobs']['installed']
    assert installed['needs'] == 'candidate'
    assert installed['strategy']['matrix']['include'] == [
        {'os': 'ubuntu-latest', 'python': '3.11'}, {'os': 'macos-latest', 'python': '3.13'}]
    scripts = '\n'.join(step.get('run', '') for step in installed['steps'])
    assert 'uv build' not in scripts
    assert 'candidate/SOURCE_COMMIT' in scripts
    assert 'tests/test_release_acceptance.py' in scripts
    assert any(step.get('with', {}).get('name') == 'candidate-${{ github.run_id }}'
               and step.get('uses', '').startswith('actions/download-artifact@')
               for step in installed['steps'])
