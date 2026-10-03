"""Approved first-user stories: real CLI/API agreement, no provider/native tools."""
import json
import shutil
import subprocess
import sys
from importlib.resources import files

import pytest
from gnd import api


@pytest.mark.parametrize('domain', ['dispatch', 'release'])
@pytest.mark.parametrize('case,expected', [('validate', 0), ('seed', 1), ('repaired', 0), ('missing_reference', 3)])
def test_example(domain, case, expected, tmp_path):
    source = files('gnd') / 'examples' / domain
    shutil.copytree(str(source), tmp_path / domain)
    root = tmp_path / domain
    model = root / 'model.orm.json'
    if case == 'validate':
        args = ['validate', str(model), '--format', 'json']
        payload = api.validate(model)
    else:
        pop = root / ('seed.pop.json' if case == 'seed' else 'repaired.pop.json')
        if case == 'missing_reference':
            next((root / 'references').iterdir()).unlink()
        args = ['check', str(model), str(pop), '--admission', '--format', 'json']
        payload = api.check(model, pop, admission=True)
    run = subprocess.run([sys.executable, '-m', 'gnd', *args], capture_output=True, text=True, timeout=30)
    assert run.returncode == expected, run.stdout + run.stderr
    assert payload['exit_code'] == expected
    cli = json.loads(run.stdout)
    assert cli['exit_code'] == payload['exit_code']
    if case == 'seed':
        assert domain + '_deadline' in run.stdout
        assert domain + '_deadline' in json.dumps(payload)
