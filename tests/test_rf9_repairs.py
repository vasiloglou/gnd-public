"""RF9 repairs: real evidence mutations and live observer dirty controls."""
from __future__ import annotations

import ast
import copy
import hashlib
import importlib
import json
import os
import runpy
import subprocess
import sys
from pathlib import Path
from typing import get_type_hints

import pytest
from support.rf8_sources import predecessor_body

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture
def failing_work_session(tmp_path, monkeypatch):
    from test_rf1_session_pins import _contract, build_v7, run_main

    monkeypatch.setenv('PATH', str(ROOT / '.venv/bin') + os.pathsep + os.environ['PATH'])
    built = build_v7(tmp_path, monkeypatch)
    spec = built.root / 'SPEC.md'
    spec.write_text(spec.read_text().replace('kind: data-driven', 'kind: work'))
    policy = json.loads(Path(built.argv[built.argv.index('--adapter-policy') + 1]).read_text())
    plan_path = Path(policy['argv'][1])
    plan = json.loads(plan_path.read_text())
    plan[1] = copy.deepcopy(plan[0])
    plan_path.write_text(json.dumps(plan))
    assert run_main(built.argv, cwd=tmp_path).returncode == 15
    run = built.root / 'runs/run-0001'
    result_path = run / 'result.json'
    result = json.loads(result_path.read_text())
    assert result['disposition'] == 'stagnation'
    return built, _contract(built), run, result_path, result


def test_forged_terminal_acceptance_is_refused(failing_work_session):
    from gnd.artifacts import canonical_json_bytes
    from gnd.exp import close
    from gnd.exp.spec import read_spec

    built, _, _, result_path, result = failing_work_session
    spec_path = built.root / 'SPEC.md'
    spec = read_spec(spec_path)
    assert close._work_findings(spec, spec_path)
    result_path.write_bytes(canonical_json_bytes(
        dict(result, disposition='accepted', terminal_reason='all required cases accepted')))
    assert close._work_findings(spec, spec_path), 'forged acceptance opened the work gate'


def test_missing_best_is_a_finding_not_a_traceback(failing_work_session, tmp_path):
    from gnd.artifacts import canonical_json_bytes
    from gnd.exp import close

    built, contract, run, result_path, result = failing_work_session
    for name in ('attempts', 'launches', 'best.json'):
        (run / name).rename(tmp_path / ('removed-' + name))
    result_path.write_bytes(canonical_json_bytes(
        dict(result, disposition='accepted', terminal_reason='all required cases accepted')))
    findings = close._declared_case_findings(
        close._SessionRun(1, run, result_path, False), built.root, result_path.read_bytes(),
        experiment_id=contract.experiment_id)
    assert findings


def test_contract_serialization_and_copy_preserve_equality(tmp_path):
    from test_exp_session_contract import _v2_exact_contract_document

    from gnd.exp.session_contract import DataDrivenContract

    parsed = DataDrivenContract.model_validate(_v2_exact_contract_document(tmp_path))
    fields = {name: getattr(parsed, name) for name in type(parsed).model_fields}
    first = DataDrivenContract(**fields)
    second = DataDrivenContract(**fields)
    assert first == second
    first_dump = first.model_dump(mode='json')
    assert first == second
    assert first.profile is second.profile
    assert first == second
    assert second.model_dump(mode='json') == first_dump
    assert first.model_copy() == first
    copied = first.model_copy(update={'schema_version': 8})
    same = DataDrivenContract(**dict(fields, schema_version=8))
    copied.profile
    assert copied == same
    assert copied.profile.judgments and not first.profile.judgments


@pytest.mark.parametrize('name,type_name', [('_content_digest', 'Population'), ('_model_digest', 'Model')])
def test_population_digest_annotations_resolve(name, type_name):
    from gnd import population
    from gnd.documents import Model

    expected = population.Population if type_name == 'Population' else Model
    assert get_type_hints(getattr(population, name)) == {
        'population' if type_name == 'Population' else 'model': expected, 'return': str}


@pytest.mark.parametrize('field', ['fact_types', 'roles'])
def test_literal_getattr_is_visible_to_exact_query_policy(field):
    import test_rf6_query_policy as guard

    policy = json.loads(guard.POLICY.read_text())
    found = guard.reads(guard.sources())
    assert_policy = guard.assert_policy
    assert_policy(found, policy)
    dirty = guard.reads({'src/gnd/injected.py':
                        f'def injected(model):\n    return getattr(model, "{field}", ())\n'})
    assert sum(dirty.values()) == 1
    with pytest.raises(AssertionError):
        assert_policy(found + dirty, policy)


def replay_node():
    source = (ROOT / 'src/gnd/exp/session_replay.py').read_text()
    return next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == 'reconstruct')


@pytest.mark.parametrize('damage', ['early', 'duplicate', 'moved'])
def test_early_or_repeated_cache_write_cannot_hide_in_body_observer(damage):
    node = replay_node()
    expected = hashlib.sha256(predecessor_body(copy.deepcopy(node)).encode()).hexdigest()
    assignment = ast.parse('store._best_identity = identity').body[0]
    identity_at = next(i for i, n in enumerate(node.body) if isinstance(n, ast.Assign)
                       and ast.unparse(n.targets[0]) == 'identity')
    if damage == 'moved':
        node.body = [n for n in node.body if ast.unparse(n) != 'store._best_identity = identity']
    if damage in ('early', 'moved'):
        node.body.insert(identity_at + 1, assignment)
    else:
        node.body.insert(len(node.body) - 1, assignment)
    try:
        observed = hashlib.sha256(predecessor_body(node).encode()).hexdigest()
    except ValueError:
        return  # Explicitly refusing the unauthorized shape is also protective.
    assert observed != expected


@pytest.mark.parametrize('module', [
    'gnd.codegen.service', 'gnd.exp.cli_service', 'gnd.export.verification_service',
    'gnd.extract.service', 'gnd.fidelity.doccheck_service', 'gnd.fidelity.service', 'gnd.review.service',
])
def test_lane_service_import_does_not_initialize_commands(module):
    code = f'import importlib,sys; importlib.import_module({module!r}); assert "gnd.commands" not in sys.modules'
    result = subprocess.run([sys.executable, '-c', code], cwd=ROOT,
                            env={**os.environ, 'PYTHONDONTWRITEBYTECODE': '1'},
                            capture_output=True, text=True, timeout=10, check=False)
    assert result.returncode == 0, result.stderr


def test_architecture_observes_implicit_parent_layer_violation(tmp_path):
    from test_gnd_arch import make_tree

    arch = runpy.run_path(str(ROOT / 'tools/gnd_arch.py'))
    root, map_path = make_tree(tmp_path, {
        'src/gnd/__init__.py': '', 'src/gnd/entry/__init__.py': '"entry"',
        'src/gnd/entry/shared.py': '', 'src/gnd/lane.py': 'from gnd.entry.shared import value\n',
    }, layers={'gnd.entry': 'entry', 'gnd.lane': 'lanes'})
    metrics = arch['measure'](root, map_path)
    assert any(e['from'] == 'gnd.lane' and e['to'] == 'gnd.entry'
               for e in metrics['implicit_parent_edges'])
    assert any(e['from'] == 'gnd.lane' and e['to'] == 'gnd.entry'
               for e in metrics['layering']['wrong_way'])


@pytest.mark.parametrize('source', [
    'from urllib import request\n', 'from urllib import request as r\n',
    'import math, urllib.request as r\n',
])
def test_offline_scan_detects_import_spellings(source):
    import test_measure_offline as guard

    assert guard._forbidden_hit(source, guard._NETWORK_LIBS) == ['urllib.request']


def test_generation_closure_rejects_from_import_in_actual_runtime(monkeypatch):
    import test_measure_offline as guard

    target = ROOT / 'src/gnd/exp/session_runtime.py'
    read = Path.read_text
    visited = []

    def dirty(path, *args, **kwargs):
        source = read(path, *args, **kwargs)
        if path == target:
            visited.append(path)
            source += '\ndef rf9_dirty():\n    from urllib import request\n    return request.urlopen("https://invalid.example")\n'
        return source

    monkeypatch.setattr(Path, 'read_text', dirty)
    with pytest.raises(AssertionError, match='network library'):
        guard.test_no_network_library_is_reachable_from_the_generation_lane()
    assert visited
