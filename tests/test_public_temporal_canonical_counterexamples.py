from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pytest

FIXTURE = Path(__file__).parent / "fixtures/public-temporal-canonical-counterexamples.json"
DOCUMENT = json.loads(FIXTURE.read_text(encoding="utf-8"))
CASES = {"cases": DOCUMENT["cases"]}
EXPECTED = DOCUMENT["answers"]

@pytest.mark.parametrize(
    "case", [row for row in CASES["cases"] if row["kind"] == "temporal"], ids=lambda row: row["id"]
)
def test_temporal_source_counterexamples(case):
    expected = EXPECTED[case["id"]]
    left, right = case["left"], case["right"]
    a, b = datetime.fromisoformat(left), datetime.fromisoformat(right)
    assert (a > b) - (a < b) == expected["instant_comparison"]
    assert (left > right) - (left < right) == expected["lexical_comparison"]
    assert (left == right) == expected["identity_equal"]


def test_canonical_source_counterexample():
    case = next(row for row in CASES["cases"] if row["kind"] == "canonical")
    expected = EXPECTED[case["id"]]

    def codec(value):
        return json.dumps(["number", [value, 1]], separators=(",", ":")).encode("utf-8")

    assert sorted(case["values"]) == expected["snapshot_order"]
    assert sorted(case["values"], key=codec) == expected["derivation_codec_order"]
