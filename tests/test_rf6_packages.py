"""RF6b predecessor imports, body pins and complete split ownership."""
from __future__ import annotations

import ast
import hashlib
import importlib
import json
import pickle
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
E = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF6'


def runtime_baseline(subject):
    path = E / f'RF6b-{subject}-py{sys.version_info.major}{sys.version_info.minor}.json'
    if not path.exists():
        assert sys.version_info[:2] == (3, 14)
        path = E / f'RF6b-{subject}.json'
    return path


def inventory():
    return json.loads((E / 'RF6b-definition-baseline.json').read_text())


def homes():
    path = E / 'RF6b-moves.json'
    return {(r['module'], r['name']): r['home'] for r in json.loads(path.read_text())} if path.exists() else {}


def assert_bindings(baseline):
    producers = {(r['module'], r['name']): r['home'] for r in json.loads((E / 'RF6b-binding-homes.json').read_text())} if (E / 'RF6b-binding-homes.json').exists() else homes()
    for module, rows in baseline.items():
        facade = importlib.import_module(module)
        for row in rows:
            value = getattr(facade, row['name'])
            assert type(value).__name__ == row['kind'], row
            if callable(value):
                assert getattr(value, '__module__', None) == row['module'], row
                assert getattr(value, '__qualname__', None) == row['qualname'], row
            if row['kind'] == 'module':
                assert value.__name__ == row['module'], row
            if 'value' in row:
                assert value == row['value'], row
            if (module, row['name']) in producers:
                assert value is getattr(importlib.import_module(producers[module, row['name']]), row['name'])


def test_all_predecessor_import_bindings_and_metadata():
    baseline = json.loads(runtime_baseline('import-baseline').read_text())
    assert {k: len(v) for k, v in baseline.items()} == {'gnd.model': 238, 'gnd.checker': 230}
    assert_bindings(baseline)


def test_deleted_binding_is_observed(monkeypatch):
    baseline = json.loads(runtime_baseline('import-baseline').read_text())
    import gnd.model
    monkeypatch.delattr(gnd.model, 'semantic_validate')
    with pytest.raises(AttributeError):
        assert_bindings(baseline)


@pytest.mark.parametrize('row', inventory(), ids=lambda r: r['module'] + '.' + r['name'])
def test_original_definition_body_is_verbatim(row):
    module = homes().get((row['module'], row['name']), row['module'])
    relative = module.replace('.', '/')
    path = ROOT / 'src' / (relative + '.py')
    if not path.is_file():
        path = ROOT / 'src' / relative / '__init__.py'
    source = path.read_text()
    definitions = [n for n in ast.parse(source).body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == row['name']]
    assert len(definitions) == 1
    node = definitions[0]
    start = min([node.lineno] + [d.lineno for d in node.decorator_list])
    body = ''.join(source.splitlines(keepends=True)[start-1:node.end_lineno])
    assert hashlib.sha256(body.encode()).hexdigest() == row['sha256']
    value = getattr(importlib.import_module(row['module']), row['name'])
    assert pickle.loads(pickle.dumps(value)) is value


def test_actual_predecessor_validation_and_checker_patches_have_effect(monkeypatch):
    from gnd import checker, model
    from gnd.documents import Model
    from gnd.population import Population
    validation = importlib.import_module(model.semantic_validate.__code__.co_filename.endswith('/_validation.py') and 'gnd.model._validation' or 'gnd.model')
    seen = []
    monkeypatch.setattr(validation, '_SEMANTIC_RULES', (lambda doc: seen.append(doc) or [],))
    doc = {'object_types': [], 'fact_types': []}
    assert model.semantic_validate(doc) == []
    assert seen == [doc]
    core = importlib.import_module('gnd.checker._core' if Path(checker.check.__code__.co_filename).name == '_core.py' else 'gnd.checker')
    sentinel = object()
    monkeypatch.setattr(core, '_check_dispatch', lambda *args: sentinel)
    m = Model(version=1, object_types=[], fact_types=[])
    p = Population.model_construct(fact_types={})
    assert checker.check(m, p) is sentinel


def split_homes():
    return {ROOT / 'src/gnd' / name for name in (
        'model/__init__.py', 'model/_validation.py', 'model/_operations.py',
        'checker/__init__.py', 'checker/_reports.py', 'checker/_core.py')}


def assert_complete_homes(actual):
    assert actual == split_homes()
    assert all(p.is_file() for p in actual)


def test_new_package_scope_is_complete():
    actual = set((ROOT / 'src/gnd/model').rglob('*.py')) | set((ROOT / 'src/gnd/checker').rglob('*.py'))
    assert_complete_homes(actual)
    with pytest.raises(AssertionError):
        assert_complete_homes(actual - {ROOT / 'src/gnd/model/_operations.py'})


def test_package_size_targets_and_over_ceiling_negative():
    model_sizes = {p.name: len(p.read_text().splitlines()) for p in (ROOT / 'src/gnd/model').glob('*.py')}
    checker_sizes = {p.name: len(p.read_text().splitlines()) for p in (ROOT / 'src/gnd/checker').glob('*.py')}
    def check(m, c):
        assert m and c
        assert max(m.values()) <= 5000  # strictly below measured5385
        assert max(c.values()) <= 2400  # strictly below measured2469
        assert m['__init__.py'] <= 900 and c['__init__.py'] <= 400
    check(model_sizes, checker_sizes)
    with pytest.raises(AssertionError):
        check({**model_sizes, '_validation.py': 5001}, checker_sizes)


def test_actual_source_observers_cover_all_package_homes():
    from test_rf6_moves import assert_scanned
    assert_scanned(split_homes())


def test_source_observer_package_omission_is_red(monkeypatch):
    import test_measure_offline as scans
    from test_rf6_moves import assert_scanned
    original = scans._module_path
    monkeypatch.setattr(scans, '_module_path', lambda name: None if name == 'gnd.model._operations' else original(name))
    with pytest.raises(AssertionError):
        assert_scanned(split_homes())


def test_predecessor_class_method_metadata_is_preserved():
    baseline = runtime_baseline('method-metadata')
    rows = json.loads(baseline.read_text())
    assert rows
    for row in rows:
        owner = getattr(importlib.import_module(row['module']), row['owner'])
        value = owner.__dict__[row['name']]
        if row['accessor']:
            value = getattr(value, row['accessor'])
        assert (value.__module__, value.__qualname__, value.__name__) == (
            row['defining_module'], row['qualname'], row['function_name'])


def test_split_metric_has_complete_homes_and_no_new_cycles():
    metric = json.loads((E.parent / 'metrics-RF6.json').read_text())
    def check(data):
        expected = {'gnd.model', 'gnd.model._validation', 'gnd.model._operations',
                    'gnd.checker', 'gnd.checker._reports', 'gnd.checker._core'}
        assert expected <= {row['module'] for row in data['modules']}
        assert not data['layering']['wrong_way']
        for scope in ('runtime', 'module_only'):
            assert not any(len(component) > 1 and expected.intersection(component)
                           for component in data['sccs'][scope])
    check(metric)
    metric['sccs']['runtime'].append(['gnd.model', 'gnd.model._validation'])
    with pytest.raises(AssertionError):
        check(metric)


def test_original_module_documentation_is_preserved():
    for name, doc in json.loads((E / 'RF6b-module-docs.json').read_text()).items():
        assert importlib.import_module(name).__doc__ == doc
