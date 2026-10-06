"""RF4 source-base successors; existing RF1 answers remain frozen."""
from __future__ import annotations

import json
import os
from pathlib import Path
from types import SimpleNamespace

import pytest

from gnd import artifacts, checker, diff
from gnd.model import load_model

ROOT = Path(__file__).resolve().parents[1]
ANSWERS = ROOT / 'tests/fixtures/rf4-premove.json'
CASES = json.loads((ROOT / 'tests/fixtures/rf1-pins/cases.json').read_text())['corpus']['checker_pairs']


def test_directory_identity_refuses_enumeration_change(tmp_path, monkeypatch):
    """RF1 owed nested comparator: stable control then changed stat must refuse."""
    (tmp_path / 'leaf').write_bytes(b'pinned')
    arguments = {'label': 'RF4 pin', 'max_entries': 10, 'max_bytes': 100}
    assert artifacts.tree_sha256_from_directory(tmp_path, **arguments)
    real_listdir, real_fstat = os.listdir, os.fstat
    enumerated = False

    def listdir(fd):
        nonlocal enumerated
        result = real_listdir(fd)
        enumerated = True
        return result

    def fstat(fd):
        info = real_fstat(fd)
        if not enumerated:
            return info
        values = {name: getattr(info, name) for name in dir(info) if name.startswith('st_')}
        values['st_mtime_ns'] += 1
        return SimpleNamespace(**values)

    monkeypatch.setattr(os, 'listdir', listdir)
    monkeypatch.setattr(os, 'fstat', fstat)
    with pytest.raises(artifacts.ArtifactError, match='directory changed while enumerated'):
        artifacts.tree_sha256_from_directory(tmp_path, **arguments)


def observations():
    rows = {}
    for model_path, population_path in CASES:
        model = load_model(ROOT / model_path)
        raw = (ROOT / population_path).read_bytes()
        key = f'{model_path}|{population_path}'
        rows[key] = diff.compare_population(model, model, raw, source=population_path,
                                             population_ref=population_path)
    return rows


def test_diff_source_base_observations():
    assert observations() == json.loads(ANSWERS.read_text())


@pytest.mark.parametrize('failure', ['checker', 'admission'])
def test_diff_fail_closed_source_base(failure, monkeypatch):
    from gnd import admission
    model_path, population_path = CASES[0]
    model = load_model(ROOT / model_path)
    raw = (ROOT / population_path).read_bytes()

    def refuse(*_args, **_kwargs):
        raise RuntimeError('RF4 pinned failure')

    if failure == 'checker':
        monkeypatch.setattr(checker, 'check_partial', refuse)
    else:
        monkeypatch.setattr(admission, 'build_admission', refuse)
    result = diff.compare_population(model, model, raw, source=population_path,
                                     population_ref=population_path)
    assert result['a']['band'] == result['b']['band'] == 70
    assert result['a']['verdicts'] == result['b']['verdicts'] == []
    assert result['a_to_b'] == result['b_to_a'] == []


def test_diff_population_refusal_source_base():
    model = load_model(ROOT / CASES[0][0])
    result = diff.compare_population(model, model, b'{', source='bad.json', population_ref='bad')
    assert result['a'] == result['b'] == {'state': 'not_comparable', 'rule': 'PopulationLoadError'}


def test_directory_identity_pin_detects_disabled_comparator(tmp_path, monkeypatch):
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(artifacts.tree_sha256_from_directory))
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef) and node.name == 'directory_identity':
            node.body = [ast.Return(ast.Tuple(elts=[], ctx=ast.Load()))]
    ast.fix_missing_locations(tree)
    namespace = dict(artifacts.tree_sha256_from_directory.__globals__)
    exec(compile(tree, '<RF4-negative-control>', 'exec'), namespace)  # noqa: S102 -- test-owned AST mutant
    monkeypatch.setattr(artifacts, 'tree_sha256_from_directory', namespace['tree_sha256_from_directory'])
    with pytest.MonkeyPatch.context() as control_patch, pytest.raises(pytest.fail.Exception, match='DID NOT RAISE'):
        test_directory_identity_refuses_enumeration_change(tmp_path, control_patch)
