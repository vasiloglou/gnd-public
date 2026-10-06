"""RF6 source ownership, aliases and complete safety observers."""
import ast
import hashlib
import importlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import test_measure_offline as scans

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.gnd-planning/milestones/code-refactoring/evidence/RF6'


def test_primitive_move_aliases_and_bodies():
    for row in json.loads((EVIDENCE / 'primitive-moves.json').read_text()):
        def resolve(name):
            module, symbol = name.rsplit('.', 1)
            return getattr(importlib.import_module(module), symbol)
        assert resolve(row['old']) is resolve(row['new'])
        p = ROOT / ('src/' + row['new'].rsplit('.', 1)[0].replace('.', '/') + '.py')
        s = p.read_text()
        n = next(n for n in ast.parse(s).body if isinstance(n, ast.FunctionDef)
                 and n.name == row['new'].rsplit('.', 1)[1])
        assert hashlib.sha256(''.join(s.splitlines(keepends=True)[n.lineno-1:n.end_lineno])
                              .encode()).hexdigest() == row['body_sha256']


def assert_scanned(homes):
    visited = set()
    original = Path.read_text
    def observe(path, *args, **kwargs):
        visited.add(path)
        return original(path, *args, **kwargs)
    with patch.object(Path, 'read_text', observe):
        for run in (scans.test_no_network_library_is_reachable_from_the_measure_lane,
                    scans.test_no_network_library_is_reachable_from_the_extraction_lane,
                    scans.test_no_network_library_is_reachable_from_the_generation_lane,
                    scans.test_no_provider_client_anywhere_in_the_package):
            visited.clear()
            run()
            assert homes <= visited, sorted(homes - visited)


def test_actual_source_observers_cover_new_query_homes():
    homes = {ROOT / 'src/gnd/model_queries.py'}
    for name in ('model_index.py', 'constraint_families.py'):
        homes.add(ROOT / 'src/gnd' / name)
    assert_scanned(homes)


def test_source_observer_omission_is_red(monkeypatch):
    original = scans._module_path
    monkeypatch.setattr(scans, '_module_path',
                        lambda name: None if name == 'gnd.model_queries' else original(name))
    with pytest.raises(AssertionError):
        assert_scanned({ROOT / 'src/gnd/model_queries.py'})
