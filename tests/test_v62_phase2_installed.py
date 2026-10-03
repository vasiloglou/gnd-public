from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest
from support.v62_phase2_corpus import FIXTURE, ROOT, population, steps


@pytest.mark.distribution
def test_i05_installed_wheel_runs_walk_and_asserted_only_plan(tmp_path: Path) -> None:
    dist = tmp_path / 'dist'
    subprocess.run(['uv', 'build', '--wheel', '--out-dir', str(dist)], cwd=ROOT, check=True)
    wheel = next(dist.glob('*.whl'))
    venv = tmp_path / 'venv'
    subprocess.run(['uv', 'venv', '--python', sys.executable, str(venv)], check=True)
    python = venv / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    subprocess.run(['uv', 'pip', 'install', '--python', str(python), str(wheel)], check=True)
    base = [str(python), '-m', 'gnd', 'check', str((FIXTURE / 'models/dynamic.orm.yaml').resolve()), '--pre', str(population('pre_open').resolve()), '--steps', str(steps().resolve()), '--format', 'json', '--unredacted']
    walk = subprocess.run([*base, '--post', str(population('post_resolved').resolve())], cwd=tmp_path, capture_output=True, check=False, text=True)
    assert walk.returncode == 0, walk.stderr
    walk_payload = json.loads(walk.stdout)
    assert walk_payload['transition']['steps'][0]['derived_changes']
    plan = subprocess.run(base, cwd=tmp_path, capture_output=True, check=False, text=True)
    assert plan.returncode == 0, plan.stderr
    plan_payload = json.loads(plan.stdout)
    facts = plan_payload['transition']['computed_post']['facts']
    assert not {'ready', 'ticket_score'}.intersection(facts)
    assert facts['resolvable'], 'authored semiderived surplus remains asserted state'
