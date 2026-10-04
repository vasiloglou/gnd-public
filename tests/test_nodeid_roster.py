from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from gnd.exp.junit import read_junit
from gnd.exp.tests_runner import _project_case_read, _pytest_nodeids

REPO_ROOT = Path(__file__).resolve().parents[1]
MODULE_SOURCE = '"""One row, so the identity has something to be about."""\n\n\ndef test_row() -> None:\n    assert True\n'
ARRANGEMENTS = ('A1', 'A2', 'A3', 'A4', 'A5')

class _Acceptance:

    def __init__(self, required_tests: tuple[str, ...]) -> None:
        self.required_tests = required_tests

def _arrange(root: Path, arrangement: str) -> tuple[Path, list[str]]:
    project = root / 'project'
    (project / 'suite').mkdir(parents=True)
    (project / 'suite' / 'test_row.py').write_text(MODULE_SOURCE, encoding='utf-8')
    config = '[pytest]\n'
    if arrangement in {'A2', 'A4'}:
        (project / 'pytest.ini').write_text(config, encoding='utf-8')
    if arrangement in {'A3', 'A4'}:
        (root / 'pytest.ini').write_text(config, encoding='utf-8')
    if arrangement == 'A5':
        return (project, ['--rootdir', str(root)])
    return (project, [])

def _run(project: Path, extra_argv: list[str], report: Path) -> tuple[str, ...]:
    argv = [sys.executable, '-m', 'pytest', '-q', '-p', 'no:randomly', 'suite/test_row.py', f'--junit-xml={report}', *extra_argv]
    result = subprocess.run(argv, cwd=project, check=False, capture_output=True, text=True, env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'})
    assert result.returncode == 0, result.stdout + result.stderr
    return tuple(_identifiers(report))

def _identifiers(report: Path) -> list[str]:
    import xml.etree.ElementTree as ET
    tree = ET.parse(report)
    found = []
    for case in tree.iter('testcase'):
        classname = case.get('classname') or ''
        name = case.get('name') or ''
        found.append(f'{classname}::{name}' if classname else name)
    return found

@pytest.mark.parametrize('arrangement', ARRANGEMENTS)
def test_the_declared_identity_resolves_under_every_arrangement(tmp_path: Path, arrangement: str) -> None:
    root = tmp_path / arrangement
    root.mkdir()
    project, extra_argv = _arrange(root, arrangement)
    report = root / 'report.xml'
    _run(project, extra_argv, report)
    declared = 'suite/test_row.py::test_row'
    scratch_fd = os.open(root, os.O_RDONLY)
    try:
        read_result = read_junit(scratch_fd, 'report.xml', [declared])
    finally:
        os.close(scratch_fd)
    assert read_result.reason is None, read_result.reason
    projected = _project_case_read(read_result, _Acceptance((declared,)), ['suite/test_row.py::test_row'])
    resolved = {item.identifier for item in projected.mapped_tests}
    assert declared in resolved, f'{arrangement}: the declared identity did not resolve; the report carried {sorted(resolved)}'

def test_the_roster_is_non_vacuous_because_the_node_ids_really_do_differ(tmp_path: Path) -> None:
    emitted: dict[str, tuple[str, ...]] = {}
    for arrangement in ARRANGEMENTS:
        root = tmp_path / arrangement
        root.mkdir()
        project, extra_argv = _arrange(root, arrangement)
        report = root / 'report.xml'
        emitted[arrangement] = _run(project, extra_argv, report)
    assert all(emitted.values()), emitted
    assert len(set(emitted.values())) > 1, f'every arrangement emitted identical identifiers, so this roster proves nothing about rootdir independence: {emitted}'

def test_a_deeper_rootdir_matches_only_on_a_dot_boundary() -> None:
    from gnd.exp.junit import _JUnitEventState
    ambiguous = _JUnitEventState(['a/test_x.py::t', 'b/a/test_x.py::t'])
    assert len(ambiguous._candidates_for(('root.b.a.test_x', 't'))) == 2, 'two declared ids matching one testcase must remain a collision the caller refuses, never a silently chosen first candidate'
    single = _JUnitEventState(['suite/test_row.py::test_row'])
    assert single._candidates_for(('other_suite.test_row', 'test_row')) == []
    assert single._candidates_for(('project.suite.test_row', 'test_row')) == ['suite/test_row.py::test_row']
    assert single._candidates_for(('suite.test_row', 'test_row')) == ['suite/test_row.py::test_row']
    assert single._candidates_for(('project.suite.test_row', 'test_other')) == []

def test_the_argv_selector_only_accepts_python_node_ids() -> None:
    argv = ['suite/test_row.py::test_row', '-k', 'not::a::nodeid', 'pkg/mod.py', 'dir::name', 'other/test_two.py::test_b']
    assert _pytest_nodeids(argv) == ('suite/test_row.py::test_row', 'other/test_two.py::test_b')
