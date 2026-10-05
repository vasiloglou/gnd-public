"""Regression controls for the acceptance instrument's reproduced review gaps."""
import ast
import inspect
import tarfile
import zipfile

import pytest
import test_release_acceptance as acceptance
from _pytest.reports import CollectReport
from _pytest.reports import TestReport as RunReport


def test_missing_referenced_skill_resource_is_refused(tmp_path):
    for origin in ['release', 'comparison']:
        folder = tmp_path / origin
        folder.mkdir()
        with zipfile.ZipFile(folder / 'candidate.whl', 'w') as archive:
            for path in (acceptance.ROOT / 'src/gnd').rglob('*'):
                if path.is_file() and '__pycache__' not in path.parts:
                    name = path.relative_to(acceptance.ROOT / 'src').as_posix()
                    if name != 'gnd/skills/gnd-review-panel/references/review-contract.md':
                        archive.write(path, name)
            archive.writestr('candidate.dist-info/licenses/LICENSE', 'test')
            archive.writestr('candidate.dist-info/licenses/NOTICE', 'test')
    with tarfile.open(tmp_path / 'release/candidate.tar.gz', 'w:gz'):
        pass
    with pytest.raises(AssertionError):
        acceptance.test_retained_candidate_identity(tmp_path)


def test_installed_gate_observes_collection_skip():
    function = ast.parse(inspect.getsource(acceptance.installed_pytest)).body[0]
    program = next(n.value.value for n in function.body if isinstance(n, ast.Assign)
                   and any(isinstance(t, ast.Name) and t.id == 'program' for t in n.targets))
    gate = next(n for n in ast.parse(program).body if isinstance(n, ast.ClassDef))
    namespace = {}
    exec(compile(ast.Module(body=[gate], type_ignores=[]), '<shipped-gate>', 'exec'), namespace)  # noqa: S102 -- trusted shipped class only
    plugin = namespace['Gate']()
    manager = pytest.PytestPluginManager()
    manager.register(plugin)
    manager.hook.pytest_collectreport(report=CollectReport(
        nodeid='test_optional.py', outcome='skipped',
        longrepr=('test_optional.py', 1, 'dependency unavailable'), result=[]))
    manager.hook.pytest_runtest_logreport(report=RunReport(
        nodeid='test_ok.py::test_ok', location=('test_ok.py', 1, 'test_ok'),
        keywords={}, outcome='passed', longrepr=None, when='call'))
    assert plugin.passed == 1
    assert plugin.skips == ['test_optional.py']


def test_installed_console_script_is_on_the_selected_environment_path(tmp_path):
    import os
    import shutil
    bin_dir = tmp_path / 'dev/bin'
    bin_dir.mkdir(parents=True)
    executable = bin_dir / 'gnd'
    executable.write_text('#!/bin/sh\nexit 0\n')
    executable.chmod(0o755)
    _checkout, python, env, _prefix = acceptance.dev_environment(
        (tmp_path, tmp_path / 'checkout', None, None, {'PATH': '/usr/bin'}, []))
    assert shutil.which('gnd', path=env['PATH']) == str(executable)
    assert env['PATH'].split(os.pathsep)[0] == str(python.parent)
