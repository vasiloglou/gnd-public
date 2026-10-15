"""PL1: the shipped examples are one-copy projects whose duplicates stay byte-identical."""
from __future__ import annotations

import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

BOOKREC = Path(str(files('gnd').joinpath('examples', 'bookrec')))
EXPENSE = Path(str(files('gnd').joinpath('examples', 'expense')))
ROOT = Path(__file__).resolve().parents[1]

TWINS = [
    (EXPENSE / 'project/cli/expense_cli.py', EXPENSE / 'extension.py'),
    (EXPENSE / 'project/cli/reporting.py', EXPENSE / 'reporting.py'),
    (EXPENSE / 'project/cli/native_query.py', EXPENSE / 'native_query.py'),
    (EXPENSE / 'project/architecture.contract.yaml', EXPENSE / 'architecture.contract.yaml'),
    (EXPENSE / 'project/model.orm.json', EXPENSE / 'model.orm.json'),
    (EXPENSE / 'project/seed.population.json', EXPENSE / 'seed.population.json'),
]


@pytest.mark.parametrize('copy,source', TWINS, ids=[c.name for c, _ in TWINS])
def test_ready_project_files_are_byte_twins(copy, source):
    assert copy.is_file() and source.is_file()
    assert copy.read_bytes() == source.read_bytes(), f'{copy} drifted from {source}'


def test_ready_project_has_a_package_marker():
    assert (EXPENSE / 'project/cli/__init__.py').is_file()


@pytest.mark.parametrize('launcher,argv', [(BOOKREC / 'app.py', ['--help']),
                                            (EXPENSE / 'project/app.py', ['report', '--help'])])
def test_launchers_run_from_any_directory(tmp_path, launcher, argv):
    run = subprocess.run([sys.executable, str(launcher), *argv], cwd=tmp_path,
                         capture_output=True, text=True, timeout=60, check=False)
    assert run.returncode == 0, run.stderr
    assert '--backend' in run.stdout


def test_source_twins_in_the_checkout_match_the_installed_copies():
    # The wheel is built from src/; a drift between checkout and import path means a stale install.
    for installed, relative in [(BOOKREC / 'app.py', 'bookrec/app.py'),
                                (EXPENSE / 'project/app.py', 'expense/project/app.py')]:
        source = ROOT / 'src/gnd/examples' / relative
        assert source.is_file(), source
        assert source.read_bytes() == installed.read_bytes(), relative
