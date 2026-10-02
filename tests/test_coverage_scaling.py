from __future__ import annotations

import json
import statistics
import time
from collections.abc import Callable
from pathlib import Path

import pytest

from gnd.checker import CheckReport, CoverageEntry
from gnd.coverage import build_coverage
from gnd.model import Model
from gnd.report import build_check_payload

SMALL = 500
LARGE = 2000
MAX_RATIO = 8.0
REPETITIONS = 5

def _case(root: Path, size: int) -> tuple[Model, Path]:
    fact_types = [{'id': f'fact_{index}', 'reading': '', 'roles': [], 'constraints': []} for index in range(size)]
    model = Model(version=2, object_types=[], fact_types=fact_types)
    report = CheckReport(coverage={f'fact_{index}': CoverageEntry(declared='declared', facts=1) for index in range(size)})
    payload = build_check_payload(0, f'synthetic-{size}.orm.yaml', f'synthetic-{size}.population.yaml', report=report)
    evidence = root / f'check-{size}.json'
    evidence.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False), encoding='utf-8')
    return (model, evidence)

def _median_seconds(operation: Callable[[], object]) -> float:
    operation()
    timings: list[float] = []
    for _ in range(REPETITIONS):
        started = time.perf_counter()
        operation()
        timings.append(time.perf_counter() - started)
    return statistics.median(timings)

def _build(model: Model, evidence: Path) -> object:
    return build_coverage(model, model_path='synthetic.orm.yaml', experiments=[], check=[evidence], verify=[], conformance=[], transition=[])

def _quadratic_match(elements: int, rows: int) -> int:
    matches = 0
    for element in range(elements):
        for row in range(rows):
            matches += element == row
    return matches

def _assert_within_ceiling(small_seconds: float, large_seconds: float) -> None:
    ratio = large_seconds / small_seconds
    assert ratio <= MAX_RATIO, f'4x inputs cost {ratio:.3f}x ({small_seconds:.9f}s -> {large_seconds:.9f}s), over the fixed {MAX_RATIO:.1f}x ceiling'

@pytest.mark.slow
def test_build_coverage_scales_below_the_predeclared_8x_ceiling(tmp_path: Path) -> None:
    small_model, small_evidence = _case(tmp_path, SMALL)
    large_model, large_evidence = _case(tmp_path, LARGE)
    small_seconds = _median_seconds(lambda: _build(small_model, small_evidence))
    large_seconds = _median_seconds(lambda: _build(large_model, large_evidence))
    ratio = large_seconds / small_seconds
    print(f'T-28 linear: E=R={SMALL} {small_seconds:.9f}s; E=R={LARGE} {large_seconds:.9f}s; ratio={ratio:.6f}')
    _assert_within_ceiling(small_seconds, large_seconds)

@pytest.mark.slow
def test_the_scaling_guard_rejects_a_deliberately_quadratic_matcher() -> None:
    small_seconds = _median_seconds(lambda: _quadratic_match(SMALL, SMALL))
    large_seconds = _median_seconds(lambda: _quadratic_match(LARGE, LARGE))
    ratio = large_seconds / small_seconds
    print(f'T-28 quadratic control: E=R={SMALL} {small_seconds:.9f}s; E=R={LARGE} {large_seconds:.9f}s; ratio={ratio:.6f}')
    with pytest.raises(AssertionError):
        _assert_within_ceiling(small_seconds, large_seconds)
    assert ratio > MAX_RATIO
