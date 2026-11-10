"""Explicitly selected historical census; ordinary phase gates exclude this lane."""
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / '.gnd-planning/milestones/model-composition/evidence/MC1/baseline-census.json'
pytestmark = pytest.mark.census


def producer():
    spec = importlib.util.spec_from_file_location('mc1_census', ROOT / 'tools/mc1_model_census.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_observations(actual, baseline):
    assert set(baseline) <= set(actual), 'baseline members disappeared'
    changed = [(path, observable) for path, row in baseline.items()
               for observable in row if row[observable] != actual[path].get(observable)]
    assert not changed, changed[:20]


def test_T23_T24_frozen_census():
    baseline = json.loads(BASELINE.read_text())
    module = producer()
    paths = module.tracked_paths()
    actual = module.collect(paths)
    print(f'baseline_members={len(baseline)} added_members={len(set(paths)-set(baseline))}')
    assert len(baseline) == 400
    assert_observations(actual, baseline)


def test_census_dirty_control():
    clean = {'model.orm.json': {'model_identity': {'value': 'old'}}}
    dirty = {'model.orm.json': {'model_identity': {'value': 'changed'}}}
    with pytest.raises(AssertionError, match='model_identity'):
        assert_observations(dirty, clean)
    with pytest.raises(AssertionError, match='disappeared'):
        assert_observations({}, clean)
