from __future__ import annotations

import time
from pathlib import Path

import pytest
from test_public_binding_rosters import EXPECTED


@pytest.mark.slow
def test_the_roster_snapshot_scales_within_the_declared_bound(tmp_path: Path) -> None:
    """INTENDED RED (T3.7, roster half). Timed at N and 4N with medians."""
    from gnd.artifacts import snapshot_tracked_roster
    answer = EXPECTED['scaling']

    def median_seconds(count: int) -> float:
        root = tmp_path / f'n{count}'
        root.mkdir()
        paths = []
        for index in range(count):
            name = f'leaf-{index:05d}.txt'
            (root / name).write_text(f'{index}\n', encoding='utf-8')
            paths.append(name)
        paths.sort()
        samples = []
        for _ in range(3):
            started = time.perf_counter()
            snapshot_tracked_roster(root, paths, label='scaling')
            samples.append(time.perf_counter() - started)
        return sorted(samples)[1]
    small = median_seconds(250)
    large = median_seconds(1000)
    assert large < answer['max_seconds_for_larger_run']
    assert large / max(small, 1e-06) < answer['max_median_growth']
