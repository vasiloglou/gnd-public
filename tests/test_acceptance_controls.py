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


# -- release-0.5.0 RW2 probes review r1, F1: a README command counts only as a line of a shell block --

COUNT_README = acceptance.ROOT / 'src/gnd/examples/literature/count_fixture'
GROWTH_README = acceptance.ROOT / 'src/gnd/examples/seeded_growth'


def test_readme_commands_accepts_the_packaged_readmes():
    assert acceptance.readme_commands(COUNT_README, acceptance.COUNT_COMMANDS) == acceptance.COUNT_COMMANDS
    assert acceptance.readme_commands(GROWTH_README, acceptance.GROWTH_COMMANDS) == acceptance.GROWTH_COMMANDS


@pytest.mark.parametrize('folder, commands', [(COUNT_README, acceptance.COUNT_COMMANDS),
                                              (GROWTH_README, acceptance.GROWTH_COMMANDS)], ids=['count', 'growth'])
@pytest.mark.parametrize('change', ['other-executable', 'commented', 'html-comment', 'outside-block', 'removed'])
def test_readme_commands_refuses_a_command_the_readme_no_longer_documents(tmp_path, folder, commands, change):
    text = (folder / 'README.md').read_text(encoding='utf-8')
    line = 'gnd ' + ' '.join(commands[0]) + '\n'
    assert text.count(line) == 1
    replacement = {
        'other-executable': 'other-' + line,
        'commented': '# ' + line,
        'html-comment': '',
        'outside-block': '',
        'removed': '',
    }[change]
    text = text.replace(line, replacement)
    if change == 'html-comment':
        text += '\n<!--\n' + line + '-->\n'
    elif change == 'outside-block':
        text += '\n' + line
    (tmp_path / 'README.md').write_text(text, encoding='utf-8')
    with pytest.raises(AssertionError):
        acceptance.readme_commands(tmp_path, commands)


def test_program_constants_reads_both_forms_without_running_the_program(tmp_path):
    import json
    rules = [{'id': 'a#0', 'info': {'note': 'a "quoted" word'}}]
    program = tmp_path / 'program.py'
    program.write_text('\n'.join([
        'import json',
        f'RULES = json.loads({json.dumps(rules)!r})',
        "FLATTENING_RECORD_SHA256 = 'ab'",
        "MODEL_INCLUDES = (('seed', 'seed.orm.yaml', 'cd'),)",
        "raise SystemExit('the program ran')",
        '']), encoding='utf-8')
    assert acceptance.program_constants(program, 'RULES', 'FLATTENING_RECORD_SHA256', 'MODEL_INCLUDES') == {
        'RULES': rules, 'FLATTENING_RECORD_SHA256': 'ab', 'MODEL_INCLUDES': (('seed', 'seed.orm.yaml', 'cd'),)}
    with pytest.raises(AssertionError):
        acceptance.program_constants(program, 'UNCHECKED')   # a constant the program lacks
