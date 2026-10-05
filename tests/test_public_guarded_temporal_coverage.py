"""Regression for temporal IDs omitted by the original guarded coverage table."""
from __future__ import annotations

from copy import deepcopy

import test_model_guarded as original
from support.public_guarded_temporal_cases import P3_TEMPORAL_REJECTING_CASES, with_duration

from gnd.model import load_model_bytes


def test_current_guarded_table_names_all_three_added_temporal_rejections():
    covered = {rule for _, _, rule in original.REJECTING_CASES}
    assert {row[2] for row in P3_TEMPORAL_REJECTING_CASES} <= covered


def test_duration_extension_is_a_valid_green_control_before_each_mutation():
    base = original._load_yaml(original.GUARDED_MINIMAL)
    green = deepcopy(base)
    with_duration(green)
    import json
    loaded = load_model_bytes(json.dumps(green).encode(), source="public-duration-green-control")
    assert loaded.version == 3
    assert not loaded.warnings
