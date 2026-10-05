from __future__ import annotations

import json
import time
from pathlib import Path

import pytest
from test_public_binding_reports import REPORTS, _corpus_relative, _run_cli

EXPECTED = {'scaling': {'growth_factor': 4, 'max_median_growth': 6.0, 'max_seconds_for_larger_run': 5.0, 'timed_surfaces': ['report-indexing', 'roster-snapshot']}}


@pytest.mark.slow
def test_report_indexing_scales_within_the_declared_bound(tmp_path: Path) -> None:
    """CONTROL (T3.7, report half). Timed at N and 4N with medians."""
    answer = EXPECTED['scaling']
    source = json.loads((REPORTS / 'legacy-v3.json').read_text(encoding='utf-8'))
    model = _corpus_relative(REPORTS / 'models' / 'nonstructured.orm.yaml')

    def median_seconds(count: int) -> float:
        directory = tmp_path / f'n{count}'
        directory.mkdir()
        argv = ['coverage', model]
        for index in range(count):
            path = directory / f'check-{index:04d}.json'
            path.write_text(json.dumps(source) + '\n', encoding='utf-8')
            argv.extend(['--check', str(path)])
        argv.extend(['--format', 'json'])
        samples = []
        for _ in range(3):
            started = time.perf_counter()
            code, _stdout, _stderr = _run_cli(argv)
            samples.append(time.perf_counter() - started)
            assert code == 0
        return sorted(samples)[1]
    small = median_seconds(8)
    large = median_seconds(8 * answer['growth_factor'])
    assert large < answer['max_seconds_for_larger_run']
    assert large / max(small, 1e-06) < answer['max_median_growth']
