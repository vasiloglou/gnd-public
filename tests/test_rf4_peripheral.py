"""RF4 current-byte graph, compatibility, patch and source closure gates."""
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import subprocess
from pathlib import Path

import pytest
from test_rf1_layering import arch

ROOT = Path(__file__).resolve().parents[1]
MILESTONE = ROOT / '.gnd-planning/milestones/code-refactoring'
MOVES = json.loads((MILESTONE / 'evidence/RF4/moves.json').read_text())
BASE = json.loads((MILESTONE / 'notes/phase-RF4-approval.json').read_text())['base']


@pytest.fixture(scope='module')
def metrics():
    return arch.measure(ROOT, ROOT / 'tools/gnd_layers.json')


def assert_architecture(result):
    modules = {row['module']: row for row in result['modules']}
    cohorts = (
        {'gnd.api', 'gnd.diff'},
        {'gnd.assurance', 'gnd.assurance_claims', 'gnd.assurance_evidence',
         'gnd.assurance_inheritance', *[m for m in modules if m.startswith('gnd.assurance.')]},
        {'gnd.synth.assemble', 'gnd.synth.mutate',
         *[m for m in modules if m.startswith('gnd.synth.oracle')]},
    )
    for cycle in result['sccs']['runtime']:
        assert not any(set(cycle) & cohort for cohort in cohorts), cycle
    assert not result['layering']['wrong_way']
    layers = json.loads((ROOT / 'tools/gnd_layers.json').read_text())
    assert set(modules) == set(layers['modules'])
    assert not layers['allow_list']
    from support.rf9_ci_sources import coupling_sites
    baseline = json.loads((MILESTONE / 'evidence/metrics-RF4-base.json').read_text())
    cohort = {row['module'] for row in baseline['modules']}
    assert len(baseline['private_imports']) == 198
    assert sum(row['from'] in cohort for row in coupling_sites(result)) < 198
    assert not [edge for edge in result['edges']
                if edge['to'] == 'gnd.install' and layers['modules'][edge['from']].get('lane')]
    assert not [edge for edge in result['private_imports']
                if edge['from'] == 'gnd.synth.boundary' and edge['to'] == 'gnd.synth.mutate']


def test_graph_targets(metrics):
    assert_architecture(metrics)


@pytest.mark.parametrize('dirty', ['cycle', 'wrong-way', 'lane-install', 'private-oracle', 'unmapped'])
def test_graph_predicate_is_live(metrics, dirty):
    import copy

    assert_architecture(metrics)
    result = copy.deepcopy(metrics)
    if dirty == 'cycle':
        result['sccs']['runtime'].append(['gnd.synth.oracle.state', 'gnd.synth.assemble'])
    elif dirty == 'wrong-way':
        result['layering']['wrong_way'].append({'from': 'gnd.population', 'to': 'gnd.api'})
    elif dirty == 'lane-install':
        result['edges'].append({'from': 'gnd.synth.boundary', 'to': 'gnd.install'})
    elif dirty == 'private-oracle':
        result['private_imports'].append({'from': 'gnd.synth.boundary', 'to': 'gnd.synth.mutate'})
    else:
        result['modules'].append({'module': 'gnd.unmapped'})
    with pytest.raises(AssertionError):
        assert_architecture(result)


@pytest.mark.parametrize('move', MOVES['names'], ids=lambda m: f"{m['old']}:{m['name']}")
def test_old_name_is_same_object(move):
    old = importlib.import_module(move['old'])
    new = importlib.import_module(move['new'])
    assert getattr(old, move['name']) is getattr(new, move['name'])


def _source(module):
    file = ROOT / 'src' / Path(*module.split('.')).with_suffix('.py')
    return file if file.is_file() else file.with_suffix('') / '__init__.py'


def _definition(source, name):
    for node in ast.parse(source).body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and node.name == name:
            return node
    return None


def _import_bindings(node):
    return sorted(a.asname or (a.name.split('.')[0] if isinstance(n, ast.Import) else a.name)
                  for n in ast.walk(node) if isinstance(n, (ast.Import, ast.ImportFrom))
                  for a in n.names)


@pytest.mark.parametrize('changed', ['binding', 'removed'])
def test_body_import_control_is_live(changed):
    before = ast.parse('def f():\n    from gnd.model import load_model\n    return load_model("x")').body[0]
    after = ast.parse('def f():\n    from gnd.model import load_model\n    return load_model("x")').body[0]
    if changed == 'binding':
        after.body[0].names[0].asname = 'other'
    else:
        del after.body[0]
    assert _algorithm(before) == _algorithm(after)
    assert _import_bindings(before) != _import_bindings(after)


def _algorithm(node):
    """Only declared dependency imports may differ; every other AST node binds."""
    class ImportSeams(ast.NodeTransformer):
        def visit_Import(self, node):
            return None

        def visit_ImportFrom(self, node):
            return None

    import copy

    from support.rf8_sources import portable_dump
    return portable_dump(ImportSeams().visit(copy.deepcopy(node)))


@pytest.mark.parametrize('move', [m for m in MOVES['names'] if not m['name'].isupper()],
                         ids=lambda m: f"{m['old']}:{m['name']}")
def test_moved_algorithm_preserves_base_body(move):
    path = 'src/' + move['old'].replace('.', '/') + '.py'
    original = subprocess.check_output(['git', 'show', f'{BASE}:{path}'], cwd=ROOT, text=True)
    before = _definition(original, move['name'])
    if before is None:
        return  # constants/imported aliases are covered by identity rather than an algorithm claim
    after = _definition(_source(move['new']).read_text(), move['name'])
    assert after is not None
    assert _import_bindings(before) == _import_bindings(after)
    from support.rf9_ci_sources import body_successor
    successor = body_successor('RF4', move['name'], move['old'])
    if successor:
        assert successor['reason']
        assert hashlib.sha256(_algorithm(before).encode()).hexdigest() == successor['before']['algorithm_sha256']
        assert hashlib.sha256(_algorithm(after).encode()).hexdigest() == successor['after']['algorithm_sha256']
    else:
        assert _algorithm(before) == _algorithm(after)


def test_provider_scan_covers_all_new_homes(monkeypatch):
    import test_measure_offline as scans

    seen = set()
    actual = scans._forbidden_hit

    def tracked(source, needles):
        seen.add(hashlib.sha256(source.encode()).hexdigest())
        return actual(source, needles)

    monkeypatch.setattr(scans, '_forbidden_hit', tracked)
    scans.test_no_provider_client_anywhere_in_the_package()
    expected = {hashlib.sha256(_source(m).read_bytes()).hexdigest() for m in MOVES['new_modules']}
    assert expected <= seen


def test_public_oracle_imports_match_original_fixed_cohort():
    original = subprocess.check_output(['git', 'show', f'{BASE}:src/gnd/synth/boundary.py'], cwd=ROOT, text=True)
    old = next(n for n in ast.parse(original).body if isinstance(n, ast.ImportFrom)
               and n.module == 'gnd.synth.mutate')
    current = ast.parse((ROOT / 'src/gnd/synth/boundary.py').read_text())
    public_names = [a for n in current.body if isinstance(n, ast.ImportFrom)
                    and n.module == 'gnd.synth.oracle' for a in n.names]
    assert len([n for n in old.names if n.name.startswith('_')]) == 47
    assert {(n.name.lstrip('_'), n.name) for n in old.names} == {(n.name, n.asname or n.name) for n in public_names}
    assert all(not n.name.startswith('_') for n in public_names)


def test_actual_process_and_adapter_patch_seams(monkeypatch, tmp_path):

    from gnd import agents, process

    async def runner(*args, **kwargs):
        raise RuntimeError('RF4 runner intercepted')

    monkeypatch.setattr(agents, 'run_bounded_process', runner)
    import asyncio
    import sys

    monkeypatch.setattr(agents.shutil, 'which', lambda *_args, **_kwargs: sys.executable)
    with pytest.raises(RuntimeError, match='runner intercepted'):
        asyncio.run(agents.invoke_agent(agents.AgentAdapterId.codex, prompt='pin', cwd=tmp_path,
                                      timeout_seconds=1))
    assert process.run_bounded_process.__globals__['__name__'] == 'gnd.process'


def test_installer_and_lane_filesystem_lookup_seams(monkeypatch):
    from gnd import install, safefs
    from gnd.codegen import manifest

    def refusal(*args, **kwargs):
        raise RuntimeError('RF4 filesystem intercepted')

    monkeypatch.setattr(safefs, '_descend', refusal)
    with pytest.raises(RuntimeError, match='filesystem intercepted'):
        install._atomic_write(Path('/unused'), 'leaf', b'data')
    assert manifest.__name__ == 'gnd.codegen.manifest'
