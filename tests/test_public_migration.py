"""Owner-approved migration instrument cases; synthetic identities only."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

CORPUS = Path(__file__).parent / "fixtures/public-launch-phase-3"
CASES = json.loads((CORPUS / "inputs.json").read_text())["cases"]
ANSWERS = {row["id"]: row for row in json.loads((CORPUS / "answers.json").read_text())["cases"]}


@pytest.mark.parametrize("case", CASES, ids=lambda row: row["id"])
def test_approved_instrument_case(case):
    try:
        from support.public_migration import MigrationRefusal, validate_acceptance_packet
    except ModuleNotFoundError:
        pytest.fail("P3 migration instrument is absent")
    answer = ANSWERS[case["id"]]
    try:
        validate_acceptance_packet(case["packet"])
        observed = (0, None)
    except MigrationRefusal as error:
        observed = (1, error.reason)
    assert observed == (answer["exit"], answer["reason"])
