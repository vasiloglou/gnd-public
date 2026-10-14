"""PL1: the PyRel interpreter defaults from GND_PYREL_PYTHON; CLIs drop two flags."""
from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from importlib.resources import files
from pathlib import Path

import pytest

from gnd.export import applications

BOOKREC = Path(str(files('gnd').joinpath('examples', 'bookrec')))
EXPENSE = Path(str(files('gnd').joinpath('examples', 'expense')))


def _env(**extra):
    env = {k: v for k, v in os.environ.items() if k not in {'PYTHONPATH', 'PYTHONHOME', 'GND_PYREL_PYTHON'}}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    env.update(extra)
    return env


def test_seam_without_interpreter_reports_the_variable(tmp_path, monkeypatch):
    monkeypatch.delenv('GND_PYREL_PYTHON', raising=False)
    result = applications.check_proposal(BOOKREC / 'model.orm.yaml', BOOKREC / 'seed.population.json',
                                         BOOKREC / 'adult-for-minor.population.json', tmp_path / 'out.json',
                                         owned_relations=('recommendation',))
    assert result['exit_code'] == 70 and not result['accepted']
    assert result['reason'].endswith('no PyRel interpreter: pass native_python or set GND_PYREL_PYTHON')
    monkeypatch.setenv('GND_PYREL_PYTHON', '')
    result = applications.execute_application(EXPENSE / 'model.orm.json', EXPENSE / 'seed.population.json',
                                              tmp_path / 'out2.json', query_script=EXPENSE / 'native_query.py',
                                              query_args=('report', '', ''))
    assert result['exit_code'] == 70
    assert result['reason'].endswith('no PyRel interpreter: pass native_python or set GND_PYREL_PYTHON')


@pytest.mark.parametrize('value', ['relative/python', '/definitely/not/a/file/python'])
def test_seam_rejects_unusable_interpreter_values(tmp_path, monkeypatch, value):
    monkeypatch.setenv('GND_PYREL_PYTHON', value)
    result = applications.check_proposal(BOOKREC / 'model.orm.yaml', BOOKREC / 'seed.population.json',
                                         BOOKREC / 'adult-for-minor.population.json', tmp_path / 'out.json',
                                         owned_relations=('recommendation',))
    assert result['exit_code'] == 70
    assert result['reason'].endswith('explicit native interpreter is unavailable')


def test_explicit_argument_wins_over_the_variable(tmp_path, monkeypatch):
    monkeypatch.setenv('GND_PYREL_PYTHON', sys.executable)
    result = applications.check_proposal(BOOKREC / 'model.orm.yaml', BOOKREC / 'seed.population.json',
                                         BOOKREC / 'adult-for-minor.population.json', tmp_path / 'out.json',
                                         native_python='relative/python', owned_relations=('recommendation',))
    assert result['reason'].endswith('explicit native interpreter is unavailable')


def test_variable_reaches_the_native_child(tmp_path, monkeypatch):
    # sys.executable is a real absolute file without PyRel: the seam must get past the
    # interpreter check and fail later, inside the child, for a different reason.
    monkeypatch.setenv('GND_PYREL_PYTHON', sys.executable)
    result = applications.check_proposal(BOOKREC / 'model.orm.yaml', BOOKREC / 'seed.population.json',
                                         BOOKREC / 'adult-for-minor.population.json', tmp_path / 'out.json',
                                         owned_relations=('recommendation',))
    assert result['exit_code'] in {2, 70} and not result['accepted']
    assert 'interpreter' not in str(result.get('reason', ''))


def _bookrec(tmp_path, *args, env=None):
    home = tmp_path / 'bookrec'
    if not home.exists():
        shutil.copytree(BOOKREC, home)
    return subprocess.run([sys.executable, str(home / 'app.py'), *args], cwd=tmp_path,
                          env=env or _env(), capture_output=True, text=True, timeout=120, check=False)


def _expense(tmp_path, *args, env=None):
    home = tmp_path / 'expense'
    if not home.exists():
        shutil.copytree(EXPENSE, home)
    return subprocess.run([sys.executable, str(home / 'project' / 'app.py'), *args], cwd=tmp_path,
                          env=env or _env(), capture_output=True, text=True, timeout=120, check=False)


def test_bookrec_cli_names_the_variable_in_its_usage_error(tmp_path):
    run = _bookrec(tmp_path, 'recommend', '--user', 'ada', '--model', 'bookrec/model.orm.yaml',
                   '--input', 'bookrec/seed.population.json', '--output', 'ada.json', '--backend', 'pyrel')
    assert run.returncode == 2
    assert '--backend pyrel needs the PyRel interpreter: pass --pyrel-python PATH or export GND_PYREL_PYTHON=PATH' in run.stderr
    assert not (tmp_path / 'ada.json').exists()


def test_expense_cli_names_the_variable_in_its_usage_error(tmp_path):
    run = _expense(tmp_path, 'report', '--model', 'expense/model.orm.json',
                   '--population', 'expense/seed.population.json', '--backend', 'pyrel')
    assert run.returncode == 2
    assert '--backend pyrel needs the PyRel interpreter: pass --pyrel-python PATH or export GND_PYREL_PYTHON=PATH' in run.stderr


def test_format_defaults_to_text_under_pyrel_and_json_otherwise(tmp_path):
    env = _env(GND_PYREL_PYTHON=sys.executable)
    text = _bookrec(tmp_path, 'recommend', '--user', 'ada', '--model', 'bookrec/model.orm.yaml',
                    '--input', 'bookrec/seed.population.json', '--output', 'ada.json', '--backend', 'pyrel', env=env)
    assert text.returncode != 0 and 'Policy check:' in text.stdout
    with pytest.raises(json.JSONDecodeError):
        json.loads(text.stdout)
    as_json = _bookrec(tmp_path, 'recommend', '--user', 'ada', '--model', 'bookrec/model.orm.yaml',
                       '--input', 'bookrec/seed.population.json', '--output', 'ada2.json', '--backend', 'pyrel',
                       '--format', 'json', env=env)
    assert json.loads(as_json.stdout)['exit_code'] == as_json.returncode
    gnd_default = _bookrec(tmp_path, 'recommend', '--user', 'ada', '--model', 'bookrec/model.orm.yaml',
                           '--input', 'bookrec/seed.population.json', '--output', 'ada3.json')
    assert gnd_default.returncode == 0 and json.loads(gnd_default.stdout)['exit_code'] == 0
    bad = _bookrec(tmp_path, 'recommend', '--user', 'ada', '--model', 'bookrec/model.orm.yaml',
                   '--input', 'bookrec/seed.population.json', '--output', 'ada4.json', '--format', 'text')
    assert bad.returncode == 2 and '--format text requires --backend pyrel' in bad.stderr


def test_expense_format_default_and_report_json(tmp_path):
    env = _env(GND_PYREL_PYTHON=sys.executable)
    text = _expense(tmp_path, 'report', '--model', 'expense/model.orm.json',
                    '--population', 'expense/seed.population.json', '--backend', 'pyrel', env=env)
    assert text.returncode != 0 and 'Policy check:' in text.stdout
    plain = _expense(tmp_path, 'report', '--model', 'expense/model.orm.json',
                     '--population', 'expense/seed.population.json')
    assert plain.returncode == 0 and json.loads(plain.stdout)['submitted'] == 3
    bad = _expense(tmp_path, 'report', '--model', 'expense/model.orm.json',
                   '--population', 'expense/seed.population.json', '--format', 'text')
    assert bad.returncode == 2 and '--format text requires --backend pyrel' in bad.stderr
