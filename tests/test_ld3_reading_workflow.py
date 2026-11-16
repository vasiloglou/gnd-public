"""Test the reading workflow through its ordinary entry points."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

EXPECTED = json.loads((Path(__file__).parent / "fixtures/ld3-reading/expected.json").read_bytes())


def _cli(*args):
    proc = subprocess.run(
        [sys.executable, "-m", "gnd.examples.literature.reading", *map(str, args)],
        capture_output=True, check=False, timeout=90,
    )
    assert proc.stdout, proc.stderr.decode()
    return proc.returncode, json.loads(proc.stdout)


@pytest.fixture(scope="module")
def fresh(tmp_path_factory):
    path = tmp_path_factory.mktemp("reading") / "run"
    code, report = _cli("run", "--out", path)
    assert code == 0, report
    return path, report


def test_six_stages_and_no_call_replay(fresh):
    path, report = fresh
    assert [row["stage"] for row in report["stages"]] == EXPECTED["stages"]
    assert report["producer_calls"] == EXPECTED["full_calls"]
    before = (path / "run.json").read_bytes()
    code, replay = _cli("replay", path)
    assert code == 0, replay
    assert replay["producer_calls"] == EXPECTED["replay_calls"]
    assert replay["evidence_sha256"] == report["evidence_sha256"]
    assert (path / "run.json").read_bytes() == before


def test_reading_outcomes_and_actual_checks(fresh):
    _, report = fresh
    assert report["stop"] == EXPECTED["stop"]["full"]
    assert {row["question"]: row["state"] for row in report["coverage"]} == EXPECTED["coverage"]
    assert {row["id"]: row["outcome"] for row in report["questions"]} == EXPECTED["question_outcomes"]
    assert report["revisit"] == EXPECTED["revisit"]
    assert "approximation" not in report["broad_fact_types"]
    assert "approximation" in report["targeted_fact_types"]
    assert report["public_routes"]["targeted"] == {"verify": 0, "check": 0}
    assert report["public_routes"]["reported-conflict"] == EXPECTED["violation_exits"]
    assert report["attempt_counts"] == {"accepted": 3, "empty": 1, "refused": 1}
    assert report["reading_bytes"] == sum(row["end"] - row["start"] for row in report["inspections"])


@pytest.mark.parametrize(("scenario", "args"), [
    ("unavailable", ["--scenario", "unavailable"]), ("budget", ["--budget-bytes", "0"]),
])
def test_other_stop_reasons(tmp_path, scenario, args):
    code, report = _cli("run", "--out", tmp_path / "run", *args)
    assert code == 0
    assert report["stop"] == EXPECTED["stop"][scenario]
    assert report["absence"]["status"] == "unavailable"


def test_fidelity_recall_cases(fresh):
    _, report = fresh
    assert report["fidelity"] == EXPECTED["fidelity"]
    assert report["absence"]["status"] == "qualified"
    assert report["absence"]["below_floor_status"] == "unavailable"
