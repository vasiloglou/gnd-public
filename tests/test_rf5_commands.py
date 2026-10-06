"""RF5 identity, algorithm and current defining-scope controls."""
from __future__ import annotations

import ast
import importlib
import inspect
import json
from pathlib import Path

import pytest
from support.repository import REPO_ROOT as ROOT

from gnd import cli

EVIDENCE = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF5'
HOMES = json.loads((EVIDENCE / 'planned-homes.json').read_text())
PREDECESSOR = ast.parse((EVIDENCE / 'predecessor-cli.py.txt').read_text())
DEFINITIONS = {node.name: node for node in PREDECESSOR.body
               if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name != 'main'}


@pytest.mark.parametrize('name', HOMES)
def test_historical_cli_name_is_the_defining_object(name):
    defining = importlib.import_module(HOMES[name])
    assert getattr(cli, name) is getattr(defining, name)


@pytest.mark.parametrize('name', sorted(DEFINITIONS))
def test_relocated_algorithm_and_qualification_are_unchanged(name):
    value = getattr(importlib.import_module(HOMES[name]), name)
    if inspect.isclass(value):
        path = ROOT / 'src' / Path(*HOMES[name].split('.')).with_suffix('.py')
        node = next(node for node in ast.parse(path.read_text()).body
                    if isinstance(node, ast.ClassDef) and node.name == name)
    else:
        node = ast.parse(inspect.getsource(value)).body[0]
    assert ast.dump(node, include_attributes=False) == ast.dump(DEFINITIONS[name], include_attributes=False)
    assert value.__module__ == 'gnd.cli'


def test_defining_scan_scope_is_complete_and_live():
    visited = set()
    for module in set(HOMES.values()):
        path = ROOT / 'src' / Path(*module.split('.')).with_suffix('.py')
        assert path.is_file(), module
        ast.parse(path.read_text())
        visited.add(module)
    assert visited == set(HOMES.values())
    missing = visited - {HOMES['_cmd_codegen']}
    assert missing != set(HOMES.values()), 'scope omission countercheck must refute completeness'


def test_source_scan_rejects_an_omitted_defining_home():
    from support.rf5_sources import cli_source_paths, cli_sources
    paths = cli_source_paths()
    assert cli_sources(paths)
    omitted = ROOT / 'src/gnd/codegen/service.py'
    with pytest.raises(AssertionError, match='incomplete CLI'):
        cli_sources([path for path in paths if path != omitted])


@pytest.mark.parametrize('name', sorted(name for name in DEFINITIONS if isinstance(DEFINITIONS[name], ast.ClassDef)))
def test_historical_class_pickling_resolves_the_same_class(name):
    import pickle
    value = getattr(cli, name)
    assert pickle.loads(pickle.dumps(value)) is value


def test_predecessor_import_bindings_still_exist():
    imports = [node for node in PREDECESSOR.body if isinstance(node, (ast.Import, ast.ImportFrom))]
    for node in imports:
        for alias in node.names:
            assert hasattr(cli, alias.asname or alias.name.split('.')[0])
