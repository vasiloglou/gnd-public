"""Explicit RF7 restriction successors; all other RF1 goldens remain binding."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from support import rf1_pins

ROOT = Path(__file__).resolve().parents[2]
SUCCESSORS = ROOT / 'tests/fixtures/rf7-restrictions/successors.json'


def assert_golden(lane, key, observed):
    document = json.loads(SUCCESSORS.read_text())
    assert document['input_sha256'] == hashlib.sha256((rf1_pins.PINS_ROOT / 'cases.json').read_bytes()).hexdigest()
    rows = document['rows']
    assert len({(r['lane'], r['stem']) for r in rows}) == len(rows)
    row = next((r for r in rows if (r['lane'], r['stem']) == (lane, rf1_pins.key_file(key))), None)
    if row is None or rf1_pins._capture_dir() is not None:
        return rf1_pins.assert_golden(lane, key, observed)
    assert row['reason'] and row['changes']
    before = (ROOT / row['before_path']).read_bytes()
    after = (ROOT / row['after_path']).read_bytes()
    assert hashlib.sha256(before).hexdigest() == row['before_sha256']
    assert hashlib.sha256(after).hexdigest() == row['after_sha256']
    assert rf1_pins.canonical(observed) == after, f'RF7 restriction successor changed: {lane}/{key}'
