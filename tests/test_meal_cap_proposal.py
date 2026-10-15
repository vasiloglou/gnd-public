"""The tutorial links the generated project and reports its actual drift."""
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / 'src/gnd/examples/expense'
HELPER = EXAMPLE / 'prepare_meal_cap.py'


def run(*args, cwd):
    return subprocess.run([sys.executable, *map(str, args)], cwd=cwd,
                          capture_output=True, text=True, check=False, timeout=60)


def test_meal_cap_links_project_and_observes_drift(tmp_path):
    shutil.copytree(EXAMPLE, tmp_path / 'demo')
    model = 'demo/model.orm.json'
    generated = run('-m', 'gnd', 'codegen', model, '--out', 'project', cwd=tmp_path)
    assert generated.returncode == 0, generated.stderr
    shutil.copytree(EXAMPLE / 'project', tmp_path / 'project', dirs_exist_ok=True)
    proposal_path = tmp_path / 'proposal.json'
    prepared = run(HELPER, '--model', model, '--project', 'project', '--cap', '50',
                   '--output', proposal_path, cwd=tmp_path)
    assert prepared.returncode == 0, prepared.stderr
    proposal = json.loads(proposal_path.read_text())
    assert len(proposal['linked_projects']) == 1
    assert proposal['linked_projects'][0]['tracked_roster']['paths']
    preview = run('-m', 'gnd', 'evolve', 'preview', model, 'proposal.json', '--workspace', '.',
                 '--records', 'records', '--out', 'preview.json', cwd=tmp_path)
    assert preview.returncode == 0, preview.stderr
    applied = run('-m', 'gnd', 'evolve', 'apply', model, 'proposal.json', '--workspace', '.',
                 '--records', 'records', '--preview', 'preview.json', cwd=tmp_path)
    assert applied.returncode == 13, applied.stdout + applied.stderr
    assert 'conformance-exit: 13' in applied.stdout
    assert run('-m', 'gnd', 'codegen', model, '--out', 'project', cwd=tmp_path).returncode == 0
    checked = run('-m', 'gnd', 'conformance', model, 'project', cwd=tmp_path)
    assert checked.returncode == 0, checked.stdout + checked.stderr


@pytest.mark.parametrize('cap', [-1, 0, 75, 100])
def test_meal_cap_refuses_non_reductions(tmp_path, cap):
    result = run(HELPER, '--model', EXAMPLE / 'model.orm.json', '--project', 'unused',
                 '--cap', cap, '--output', 'proposal.json', cwd=tmp_path)
    assert result.returncode == 2
    assert 'between 1 and' in result.stderr
    assert not (tmp_path / 'proposal.json').exists()
