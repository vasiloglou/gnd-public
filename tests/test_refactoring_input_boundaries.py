"""Successor input and output contracts for #301 and #302."""
import time

import pytest

from gnd import input_policy
from gnd.errors import (
    ModelLoadError,
    ModelValidationError,
    PopulationLoadError,
    PopulationValidationError,
)
from gnd.model import load_model_bytes
from gnd.output import _canonical_payload
from gnd.population import load_population_bytes


@pytest.mark.parametrize(("reader", "error", "schema_error"), [
    (load_model_bytes, ModelLoadError, ModelValidationError),
    (load_population_bytes, PopulationLoadError, PopulationValidationError),
])
def test_public_yaml_depth_before_construction(reader, error, schema_error):
    limit = input_policy.MAX_DEPTH
    def nested(n):
        return b"[" * n + b"0" + b"]" * n

    # At the limit a YAML sequence is parsed and rejected by the schema layer.
    with pytest.raises(schema_error) as within:
        reader(nested(limit), source="sample.yaml")
    assert "depth cap" not in str(within.value)
    for n in (limit + 1, 1000):
        started = time.monotonic()
        with pytest.raises(error, match="YAML depth cap exceeded"):
            reader(nested(n), source="sample.yaml")
        assert time.monotonic() - started < 5


@pytest.mark.parametrize("value", [float("nan"), float("inf"), float("-inf")])
def test_panel_summary_requires_finite_json(value):
    with pytest.raises(ValueError, match="Out of range float"):
        _canonical_payload({"nested": [value]})
    assert _canonical_payload({"z": 0.25, "a": "é"}) == '{"a":"é","z":0.25}'


def test_legacy_candidate_mime_follows_the_host_table(monkeypatch):
    import mimetypes

    from gnd.exp.session_records import _classify
    for media in ("application/x-host-a", "text/x-host-b"):
        monkeypatch.setattr(mimetypes, "guess_type", lambda path, strict, m=media: (m, None))
        assert _classify("sample.example", b"hello") == (media, "utf-8")


@pytest.mark.parametrize(("reader", "error"), [
    (load_model_bytes, ModelLoadError),
    (load_population_bytes, PopulationLoadError),
])
def test_first_yaml_budget_violation_stops_scan(reader, error):
    deep = b"[" * 65 + b"0" + b"]" * 65
    with pytest.raises(error, match="depth cap"):
        reader(b"- " + deep + b"\n- &a 1\n- *a", source="sample.yaml")
    with pytest.raises(error, match="alias"):
        reader(b"- &a 1\n- *a\n- " + deep, source="sample.yaml")
