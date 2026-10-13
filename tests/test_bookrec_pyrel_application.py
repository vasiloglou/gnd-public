"""Red-first actual native application outcomes, separate from checker-only tests."""
import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
NATIVE = ROOT / 'tutorials/runtimes/.venv/bin/python'
pytestmark = pytest.mark.pyrel_oracle


@pytest.mark.parametrize('mode,expected', [('advisory', 0), ('strict', 1), ('preferred', 0),
                                          ('complete', 0), ('unknown', 3), ('limit', 2)])
def test_native_bookrec_cli_outcomes_and_pairs(tmp_path, mode, expected):
    home = tmp_path / 'bookrec'
    shutil.copytree(str(files('gnd').joinpath('examples', 'bookrec')), home)
    model = 'complete.orm.yaml' if mode == 'complete' else ('strict.orm.yaml' if mode in {'strict', 'preferred'} else 'model.orm.yaml')
    output = tmp_path / 'result.json'; source = home / 'seed.population.json'
    before = source.read_bytes()
    args = ['complete' if mode == 'complete' else 'recommend', '--model', str(home / model),
            '--input', str(source), '--output', str(output), '--backend', 'pyrel', '--pyrel-python', str(NATIVE)]
    if mode != 'complete':
        args += ['--user', 'nobody' if mode == 'unknown' else 'ada', '--limit', '0' if mode == 'limit' else '2']
    if mode == 'preferred':
        args.append('--preferred-only')
    help_run = subprocess.run([sys.executable, '-m', 'bookrec.cli', '--help'], cwd=home / 'extension',
                              capture_output=True, text=True, timeout=20, check=False)
    assert '--backend' in help_run.stdout and '--pyrel-python' in help_run.stdout, 'native application interface is absent'
    completed = subprocess.run([sys.executable, '-m', 'bookrec.cli', *args], cwd=home / 'extension',
                               env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'}, capture_output=True,
                               text=True, timeout=150, check=False)
    assert completed.returncode == expected, completed.stderr + completed.stdout
    assert source.read_bytes() == before
    if expected:
        assert not output.exists()
        return
    candidate = json.loads(output.read_text()); report = json.loads(completed.stdout)
    assert report['published'] and report['accepted']
    pairs = {(row['user'], row['book']) for row in candidate['facts']['recommendation']}
    if mode == 'advisory':
        assert pairs == {('ada', 'cosmos'), ('ada', 'map'), ('ben', 'night')}
        assert report['policy']['status'] == 'accepted_with_warnings'
        assert report['calculation']['selected_pairs'] == [{'user': 'ada', 'book': 'cosmos'}, {'user': 'ada', 'book': 'map'}]
    elif mode == 'preferred':
        assert pairs == {('ada', 'map'), ('ada', 'river'), ('ben', 'night')}
    else:
        assert pairs == {('ada', 'map'), ('ada', 'river'), ('ben', 'map'), ('ben', 'night'), ('ben', 'river')}
        assert {(row['user'], row['book']) for row in candidate['facts']['book_is_eligible']} == pairs
        assert candidate['facts']['book_is_blocked_for'] == [{'book': 'night', 'user': 'ada'}]
