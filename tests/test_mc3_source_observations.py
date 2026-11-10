"""MC3 actual-base fidelity does not replace the five historical known-red pins."""
import ast
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.gnd-planning/milestones/model-composition/evidence/MC3'


def observed_bodies():
    data = json.loads((EVIDENCE / 'actual-base-body-observations.json').read_text())
    predecessor = ROOT / data['predecessor']
    assert hashlib.sha256(predecessor.read_bytes()).hexdigest() == data['predecessor_sha256']
    old = {(row['path'], row['name']): row['raw_sha256'] for row in json.loads(predecessor.read_text())['rows']}
    assert len(data['rows']) == len(old) == 5
    for row in data['rows']:
        assert row['before_raw_sha256'] == old[row['path'], row['name']]
        source = (ROOT / row['path']).read_text()
        node = next(n for n in ast.parse(source).body if isinstance(n, ast.FunctionDef) and n.name == row['name'])
        assert hashlib.sha256(ast.get_source_segment(source, node).encode()).hexdigest() == row['after_raw_sha256']


def test_actual_base_bodies_are_exact():
    observed_bodies()


def test_actual_base_observation_rejects_changed_body(monkeypatch):
    original = Path.read_text
    def changed(path, *args, **kwargs):
        source = original(path, *args, **kwargs)
        if path == ROOT / 'src/gnd/evolve/cli_service.py':
            source = source.replace('previous_includes=history', 'previous_includes=None')
        return source
    monkeypatch.setattr(Path, 'read_text', changed)
    with pytest.raises(AssertionError):
        observed_bodies()
