"""RF3 relocation controls; original answers remain separate and immutable."""
from __future__ import annotations

import ast
import hashlib
import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import test_measure_offline as scans

ROOT = Path(__file__).resolve().parents[1]
MOVES = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF3-moves.json'


def rows():
    return json.loads(MOVES.read_text())


def resolve(name):
    module, name = name.replace('/', '.').rsplit('.', 1)
    return getattr(importlib.import_module(module), name)


def test_all_old_names_resolve_to_same_objects():
    moved = rows()
    assert len(moved) >= 232
    for row in moved:
        assert resolve(row['old']) is resolve(row['new']), row
        if row['kind'] in ('FunctionDef', 'ClassDef'):
            assert resolve(row['old']).__module__ == row['old'].replace('/', '.').rsplit('.', 1)[0]


def assert_move_bodies(sources):
    for row in rows():
        if row['kind'] not in ('FunctionDef', 'ClassDef'):
            continue
        name = row['old'].rsplit('.', 1)[1]
        module = row['new'].rsplit('.', 1)[0]
        source = sources[module]
        node = next(n for n in ast.parse(source).body
                    if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name == name)
        start = min([node.lineno, *(d.lineno for d in node.decorator_list)])
        segment = ''.join(source.splitlines(keepends=True)[start-1:node.end_lineno])
        assert hashlib.sha256(segment.encode()).hexdigest() == row['body_sha256'], row


def move_sources():
    modules = {r['new'].rsplit('.', 1)[0] for r in rows()}
    return {m: (ROOT / ('src/' + m.replace('.', '/') + '.py')).read_text() for m in modules}


def test_move_bodies_are_verbatim():
    assert_move_bodies(move_sources())


def test_known_dirty_body_is_rejected():
    sources = move_sources()
    sources['gnd.values'] = sources['gnd.values'].replace('return ("boolean", value)', 'return ("number", value)', 1)
    with pytest.raises(AssertionError):
        assert_move_bodies(sources)


def test_real_scan_closures_visit_every_new_home():
    homes = {ROOT / ('src/' + r['new'].rsplit('.', 1)[0].replace('.', '/') + '.py') for r in rows()}
    visited = set()
    original = Path.read_text

    def observe(path, *args, **kwargs):
        visited.add(path)
        return original(path, *args, **kwargs)

    with patch.object(Path, 'read_text', observe):
        scans.test_no_network_library_is_reachable_from_the_measure_lane()
        scans.test_no_network_library_is_reachable_from_the_extraction_lane()
        scans.test_no_network_library_is_reachable_from_the_generation_lane()
        assert homes <= visited, sorted(homes - visited)
        visited.clear()
        scans.test_no_provider_client_anywhere_in_the_package()
        assert homes <= visited


def test_scan_coverage_rejects_missing_home(monkeypatch):
    original = scans._module_path
    monkeypatch.setattr(scans, '_module_path', lambda name: None if name.startswith('gnd.universe') else original(name))
    with pytest.raises(AssertionError):
        test_real_scan_closures_visit_every_new_home()


def test_real_scan_rejects_planted_network_import(monkeypatch):
    original = Path.read_text

    def dirty(path, *args, **kwargs):
        text = original(path, *args, **kwargs)
        return text + '\nimport socket\n' if path == ROOT / 'src/gnd/universe.py' else text

    monkeypatch.setattr(Path, 'read_text', dirty)
    with pytest.raises(AssertionError, match='universe.py'):
        scans.test_no_network_library_is_reachable_from_the_measure_lane()
