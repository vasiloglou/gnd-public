"""RF8 graph, move/shim and source observer liveness controls."""
import ast
import copy
import hashlib
import importlib
import importlib.util
import json
from pathlib import Path

import pytest
from support.rf8_sources import predecessor_body

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF8'
HOMES = {'session_profile', 'session_environment', 'session_control', 'session_records',
         'session_replay', 'session_runtime'}


def assert_graph(metrics):
    layers = json.loads((ROOT / 'tools/gnd_layers.json').read_text())
    assert set(layers['modules']) == {r['module'] for r in metrics['modules']}
    assert not metrics['layering']['wrong_way']
    assert not metrics['entrypoints']['violations']
    assert not metrics['sccs']['runtime']
    assert {'gnd.exp.' + name for name in HOMES} <= set(layers['modules'])


def test_graph_and_each_dirty_direction():
    spec = importlib.util.spec_from_file_location('rf8_arch', ROOT / 'tools/gnd_arch.py')
    arch = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(arch)
    metrics = arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')
    assert_graph(metrics)
    for kind in ('cycle', 'edge', 'entry', 'missing'):
        dirty = copy.deepcopy(metrics)
        if kind == 'cycle':
            dirty['sccs']['runtime'].append(['gnd.exp.session_records', 'gnd.exp.session'])
        elif kind == 'edge':
            dirty['layering']['wrong_way'].append({'from': 'gnd.exp.session_records', 'to': 'gnd.cli'})
        elif kind == 'entry':
            dirty['entrypoints']['violations'].append({'from': 'gnd.commands.exp', 'to': 'gnd.exp.session'})
        else:
            dirty['modules'] = [r for r in dirty['modules'] if r['module'] != 'gnd.exp.session_records']
        with pytest.raises(AssertionError):
            assert_graph(dirty)


def test_v7_is_only_compatibility_strategy_hooks():
    source = (ROOT / 'src/gnd/exp/session_v7.py').read_text()
    assert len(source.splitlines()) <= 60
    assert all(isinstance(n, (ast.Import, ast.ImportFrom, ast.Expr)) for n in ast.parse(source).body)
    from gnd.exp import session_replay, session_runtime, session_v7
    assert session_v7.run is session_runtime.run
    assert session_v7.reconstruct is session_replay.reconstruct


def test_unchanged_moved_bodies_and_shim_identity():
    rows = json.loads((EVIDENCE / 'moves-predecessor.json').read_text())
    for row in rows:
        source = (ROOT / row['new']).read_text()
        candidates = [n for n in ast.parse(source).body
                      if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                      and n.name == row['name']]
        node = next((n for n in candidates if hashlib.sha256(predecessor_body(copy.deepcopy(n)).encode()).hexdigest() == row['ast_sha256']), candidates[-1])
        # Run's public identity lookup intentionally changes; its end-to-end matrix is G3.
        if row['name'] != 'run':
            assert hashlib.sha256(predecessor_body(node).encode()).hexdigest() == row['ast_sha256'], row['name']
        old = importlib.import_module(row['old'][4:-3].replace('/', '.'))
        new = importlib.import_module(row['new'][4:-3].replace('/', '.'))
        assert getattr(old, row['name']) is getattr(new, row['name'])


def test_reader_body_observer_can_fail():
    rows = json.loads((EVIDENCE / 'reader-base.json').read_text())['functions']
    for row in rows:
        source = (ROOT / row['physical_path']).read_text()
        node = next(n for n in ast.walk(ast.parse(source))
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == row['function'])
        assert hashlib.sha256(predecessor_body(copy.deepcopy(node)).encode()).hexdigest() == row['ast_sha256']
        node.body.append(ast.parse('raise RuntimeError("dirty")').body[0])
        assert hashlib.sha256(predecessor_body(node).encode()).hexdigest() != row['ast_sha256']


def test_new_homes_have_no_inline_contract_version_switches():
    for name in ('session_replay', 'session_runtime'):
        tree = ast.parse((ROOT / f'src/gnd/exp/{name}.py').read_text())
        assert not any(isinstance(n, ast.Attribute) and n.attr == 'schema_version'
                       and isinstance(n.value, ast.Name) and n.value.id == 'contract'
                       for n in ast.walk(tree))


def test_all_v7_predecessor_bindings_remain_importable():
    from gnd.exp import session_v7
    rows = json.loads((EVIDENCE / 'v7-bindings.json').read_text())
    assert len(rows['names']) == 47
    assert all(hasattr(session_v7, name) for name in rows['names'])
