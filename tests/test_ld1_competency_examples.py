"""Check the literature depth example through its packaged entry point."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

EXPECTED = json.loads(
    (Path(__file__).parent / "fixtures" / "ld1-competency" / "expected.json").read_bytes()
)


@pytest.fixture(scope="module")
def report(tmp_path_factory):
    output = tmp_path_factory.mktemp("ld1").resolve() / "out"
    run = subprocess.run(
        [sys.executable, "-m", "gnd.examples.literature.depth", "--out", str(output)],
        capture_output=True,
        text=True,
        check=False,
        timeout=60,
    )
    assert run.returncode == 0, run.stderr
    return json.loads((output / "report.json").read_bytes())


@pytest.mark.parametrize("case", EXPECTED["questions"])
def test_competency_questions(report, case):
    assert report["format"] == "literature-depth/1"
    observed = report["cases"][case]["questions"]
    assert [[row["id"], row["status"], list(row["facts"])] for row in observed] == EXPECTED["questions"][case]
    assert all(row["evidence"] for row in observed)
    if case == "dynamics":
        assert observed[0]["claim_kind"] == "reported-equation"


def test_experiment_comparisons(report):
    assert {row["id"]: [row["status"], row["fields"]] for row in report["comparisons"]} == EXPECTED["comparison"]


def test_three_quantity_probes_are_reported(report):
    assert [row["axis"] for row in report["quantities"]] == EXPECTED["quantities"]
    assert all(row["observed"] and type(row["opens_ld2"]) is bool for row in report["quantities"])
