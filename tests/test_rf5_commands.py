"""RF5 identity, algorithm and current defining-scope controls."""
from __future__ import annotations

import ast
import hashlib
import importlib
import inspect
import json
from pathlib import Path

import pytest
from support.repository import REPO_ROOT as ROOT

from gnd import cli

EVIDENCE = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF5'
HOMES = json.loads((EVIDENCE.parent / 'RF9-repair/cli-homes.json').read_text())
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
    # RF7 deliberately changes decoder admission; every other AST node remains pinned.
    class ReaderSeam(ast.NodeTransformer):
        def visit_Attribute(self, child):
            if (isinstance(child.value, ast.Name) and child.value.id == '_rf7_input'
                    and child.attr in ('loads', 'load', 'JSONDecoder')):
                child.value.id = 'json'
            return self.generic_visit(child)
    node = ReaderSeam().visit(node)
    from support.rf8_sources import portable_dump
    from support.rf9_ci_sources import body_successor
    successor = body_successor('RF5', name, 'gnd.cli')
    if successor:
        assert successor['home'] == HOMES[name] and successor['reason']
        assert hashlib.sha256(portable_dump(DEFINITIONS[name]).encode()).hexdigest() == successor['before']['algorithm_sha256']
        assert hashlib.sha256(portable_dump(node).encode()).hexdigest() == successor['after']['algorithm_sha256']
    else:
        assert portable_dump(node) == portable_dump(DEFINITIONS[name])
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


def architecture():
    import importlib.util
    spec = importlib.util.spec_from_file_location('rf5_arch', ROOT / 'tools/gnd_arch.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_bootstrap_ceiling_and_single_parse_dispatch():
    source = (ROOT / 'src/gnd/cli.py').read_text()
    from support.rf5_sources import assert_cli_ceiling
    assert_cli_ceiling(source)
    oversized = source + "\n# RF5 ceiling countercheck" * (1501 - len(source.splitlines()))
    with pytest.raises(AssertionError, match="bootstrap exceeds"):
        assert_cli_ceiling(oversized)
    main = next(node for node in ast.parse(source).body if isinstance(node, ast.FunctionDef) and node.name == 'main')
    assert sum(isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == 'parse_args' for node in ast.walk(main)) == 1
    assert not any(isinstance(node, ast.Name) and node.id.startswith('_cmd_') for node in ast.walk(main))
    assert ast.unparse(main.body[-1]) == 'return args.handler(args)'


def test_all_parser_paths_receive_command_handlers(monkeypatch):
    from test_rf1_cli_pins import _root, _walk
    parsers = {}
    _walk(_root(monkeypatch), ('gnd',), parsers)
    assert len(parsers) == 55  # IK5 adds `gnd export ilp` and `gnd import ilp-rules`
    for path in parsers:
        if path != 'gnd':
            assert callable(parsers[' '.join(path.split()[:2])].get_default('handler')), path
    cases = json.loads((ROOT / 'tests/fixtures/rf5-handlers/cases.json').read_text())
    for case in cases:
        args = parsers['gnd'].parse_args([arg.replace('<repo>', str(ROOT)) for arg in case['argv']])
        assert callable(args.handler), case['id']


def test_entrypoint_rule_covers_all_groups_and_rejects_forbidden_imports():
    import copy
    arch = architecture()
    metrics = arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    policy = json.loads((ROOT / 'tools/gnd_entrypoints.json').read_text())
    result = arch.entrypoint_rule(metrics, policy)
    assert len(result['scope']) == 20  # IK4 adds gnd.commands.discover
    assert result['violations'] == []
    for source, target in [('gnd.commands.verify', 'gnd.cli'), ('gnd.commands.verify', 'gnd.checker')]:
        altered = copy.deepcopy(metrics)
        altered['edges'].append({'from': source, 'to': target, 'kind': 'module', 'line': 1})
        assert len(arch.entrypoint_rule(altered, policy)['violations']) == 1
    incomplete = copy.deepcopy(policy)
    incomplete['scope'].remove('gnd.commands.verify')
    with pytest.raises(ValueError, match='incomplete RF5'):
        arch.entrypoint_rule(metrics, incomplete)
    omitted = copy.deepcopy(metrics)
    omitted['modules'] = [row for row in omitted['modules'] if row['module'] != 'gnd.commands.verify']
    with pytest.raises(ValueError, match='incomplete RF5'):
        arch.entrypoint_rule(omitted, policy)
    added = copy.deepcopy(metrics)
    added['modules'].append({'module': 'gnd.commands.unscanned', 'layer': 'entry'})
    with pytest.raises(ValueError, match='incomplete RF5'):
        arch.entrypoint_rule(added, policy)
    incomplete = copy.deepcopy(policy)
    incomplete['service_targets'].append('gnd.cli')
    with pytest.raises(ValueError, match='invalid entry-point service'):
        arch.entrypoint_rule(metrics, incomplete)
