"""Bounded current successor for Phase 2 CLI/API and assurance contracts."""
import json
import subprocess
from pathlib import Path

import pytest
from test_public_distribution import package_probe

ROOT = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize('case', ['C0','C1','C2','C3','C4','C5','C6','C7','C8','C9','C10'])
def test_installed_behavior(package_probe, case):
    probe = package_probe
    run = subprocess.run([str(probe['python']), str(ROOT/'tests/support/public_probe.py'),
                          str(ROOT/'tests/fixtures/public-launch-phase-2'), case],
                         cwd=probe['outside'], env=probe['env'], capture_output=True,
                         text=True, timeout=60)
    assert run.returncode == 0, run.stdout + run.stderr
    payload = json.loads(run.stdout)
    assert payload['case'] == case and payload['exit'] == 0
    assert Path(payload['gnd_file']).is_relative_to(probe['venv'])


def test_installed_import_help_and_api_surface(package_probe):
    probe = package_probe
    for args in [['--help'], ['check','--help'], ['review','--help']]:
        run = subprocess.run([str(probe['venv']/'bin/gnd'), *args], cwd=probe['outside'],
                             env=probe['env'], capture_output=True, text=True, timeout=60)
        assert run.returncode == 0, run.stderr
    code = "from gnd import api; import importlib.util; assert api.__all__ == ('validate','check','transition','verbalize','diff','witness','replay'); assert importlib.util.find_spec('faker') is None; assert importlib.util.find_spec('pytest') is None"
    run = subprocess.run([str(probe['python']), '-c', code], cwd=probe['outside'],
                         env=probe['env'], capture_output=True, text=True, timeout=60)
    assert run.returncode == 0, run.stderr
