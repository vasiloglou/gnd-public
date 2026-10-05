from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path

from support.v62_phase5_corpus import FIXTURE, document

from gnd.coverage import _element_universe
from gnd.model import Model
from gnd.model_verbalization import render_model_verbalization


def test_s01_synth_reports_a_named_unsupported_reason_not_a_crash_or_hang() -> None:
    model_path = FIXTURE / "models" / "floats.orm.yaml"
    with tempfile.TemporaryDirectory() as out_dir:
        result = subprocess.run([sys.executable, "-m", "gnd", "synth", str(model_path), "--out", out_dir, "--class", "conforming", "--seed", "42", "--format", "json"], cwd=Path(__file__).resolve().parent.parent, capture_output=True, text=True, timeout=60, check=False)
    payload = json.loads(result.stdout)
    assert result.returncode == 5
    assert payload["command"] == "synth"
    assert payload["exit_code"] == 5
    assert "term-generation-did-not-converge" in payload["error"]
    assert "term:haversine-coordinate-range" in payload["error"]

def test_d8_verbalization_renders_every_float_function_generically() -> None:
    rendered = render_model_verbalization(Model.model_validate(document()))
    assert 'round(haversine($serving_lat, $serving_lon, $neighbor_lat, $neighbor_lon), 3)' in rendered
    assert 'round(div($rb, $duration), 2)' in rendered
    assert 'floor(div($rb, $duration))' in rendered
    assert 'ceil(div($rb, $duration))' in rendered
    assert 'round(sqrt($margin), 4)' in rendered

def test_d8_coverage_addressing_gives_one_rule_level_address_per_float_derivation() -> None:
    model = Model.model_validate(document())
    universe, _positional = _element_universe(model)
    addresses = [address for address, _kind, _mode in universe]
    for derivation_id in ('sample_rate_kbps', 'sample_margin_sqrt', 'sample_serving_distance_km', 'scenario_avg_rb'):
        assert addresses.count(f'derivation:{derivation_id}') == 1
        assert not any(address.startswith(f'derivation:{derivation_id}:') for address in addresses)
