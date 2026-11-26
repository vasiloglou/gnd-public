"""gnd diff without the optional synth extra (issue 323).

`gnd diff` synthesizes populations by default. Without the extra, the synthetic-value
generator raises SynthDependencyError, which reached the CLI as an internal error
(exit 70). The reference's contract is that unsupported synthesis is recorded in
`not_derivable`, so a missing extra is recorded there too, naming the extra.
"""
import json
from pathlib import Path

import pytest
from support.cli_runner import run_main

ROOT = Path(__file__).resolve().parents[1]
#: A model whose synthesis succeeds with the extra (it has no guarded or structured rule).
MODEL = ROOT / "src/gnd/skills/gnd-model-from-text/examples/movie_catalog.orm.yaml"
#: The refunds model the Ossie how-to page diffs: its synthesis is not derivable either way.
REFUNDS = ROOT / "src/gnd/examples/refunds/model.orm.yaml"


def _diff(model=MODEL):
    return run_main(["diff", str(model), str(model), "--format", "json"])


@pytest.fixture
def no_synth_extra(monkeypatch):
    from gnd.synth import values

    def unavailable():
        raise values.SynthDependencyError()

    monkeypatch.setattr(values, "_require_faker", unavailable)


def test_issue_323_diff_without_the_extra_records_synthesis_as_not_derivable(no_synth_extra):
    with_extra_missing = _diff()
    assert with_extra_missing.returncode != 70, with_extra_missing.stdout
    report = json.loads(with_extra_missing.stdout)
    rows = [row for row in report["not_derivable"] if row["kind"] == "synthesis"]
    assert [row["source"] for row in rows] == ["a", "b"]
    assert all("synth" in row["reason"] and row["subject"] == "model" for row in rows)
    assert not [row for row in report["populations"] if str(row.get("origin", "")).startswith("synth-")]
    assert report["entailment"], "the rule comparison does not need the extra"


def test_issue_323_the_same_diff_with_the_extra_synthesizes():
    run = _diff()
    report = json.loads(run.stdout)
    assert not [row for row in report["not_derivable"] if "synth' extra" in row["reason"]]
    assert [row for row in report["populations"] if str(row.get("origin", "")).startswith("synth-")]
    assert run.returncode == 0


@pytest.mark.parametrize("model", [MODEL, REFUNDS], ids=["movie-catalog", "refunds"])
def test_issue_323_the_exit_does_not_depend_on_the_extra(model, monkeypatch):
    present = _diff(model)
    from gnd.synth import values

    def unavailable():
        raise values.SynthDependencyError()

    monkeypatch.setattr(values, "_require_faker", unavailable)
    absent = _diff(model)
    assert absent.returncode == present.returncode, absent.stdout
