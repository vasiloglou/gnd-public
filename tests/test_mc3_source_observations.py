"""MC3 actual-base fidelity does not replace the five historical known-red pins."""
import ast
import hashlib
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EVIDENCE = ROOT / '.gnd-planning/milestones/model-composition/evidence/MC3'


def _successor_raw(name, raw):
    """Follow registered body successors from RAW (reviewed-vocabulary-growth VG3).

    The observations stay as recorded; a body changed later is admitted only
    through an exact, chained successor row naming its raw bytes.
    """
    from support.rf9_ci_sources import PHASE_SUCCESSORS

    for path in PHASE_SUCCESSORS:
        for row in json.loads(path.read_text())['successors']:
            before, after = row.get('before'), row.get('after')
            if (row.get('name') == name and isinstance(before, dict) and isinstance(after, dict)
                    and before.get('raw_sha256') == raw and 'raw_sha256' in after):
                raw = after['raw_sha256']
    return raw


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
        expected = _successor_raw(row['name'], row['after_raw_sha256'])
        assert hashlib.sha256(ast.get_source_segment(source, node).encode()).hexdigest() == expected


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
