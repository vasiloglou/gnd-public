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
    for index in (1, 3):
        payload = json.loads((path / f"payload-{index}.json").read_bytes())
        assert payload["original_producer_calls"] == EXPECTED["full_calls"][EXPECTED["stages"][index]]
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
    if scenario == "budget":
        assert report["revisit"] == []
        assert report["read_denominator"] == {"scheduled": 5, "attempted": 0, "omitted": 5, "unavailable": 0}
    else:
        assert report["read_denominator"] == {"scheduled": 5, "attempted": 4, "omitted": 0, "unavailable": 1}


def test_fidelity_recall_cases(fresh):
    _, report = fresh
    assert report["fidelity"] == EXPECTED["fidelity"]
    assert report["absence"]["status"] == "qualified"
    assert report["absence"]["below_floor_status"] == "unavailable"


def test_replay_validates_coverage_after_a_coordinated_repin(fresh, tmp_path, monkeypatch):
    import shutil

    from gnd.artifacts import canonical_json_bytes, sha256_hex
    from gnd.examples.literature import reading

    original, _ = fresh
    run = tmp_path / "copied"
    shutil.copytree(original, run)
    monkeypatch.setattr(reading.SavedProducer, "produce", lambda *_: pytest.fail("replay invoked producer"))
    assert reading.replay(run)["producer_calls"] == EXPECTED["replay_calls"]
    coverage = run / "coverage.json"
    manifest = run / "run.json"
    value = json.loads(coverage.read_bytes())
    value["rows"].pop()
    raw = canonical_json_bytes(value)
    coverage.write_bytes(raw)
    index = json.loads(manifest.read_bytes())
    index["artifacts"][coverage.name] = sha256_hex(raw)
    manifest.write_bytes(canonical_json_bytes(index))
    with pytest.raises(reading.ExampleError, match="re-derived reading evidence differs"):
        reading.replay(run)
    coverage.unlink()
    code, report = _cli("replay", run)
    assert code == 3 and report["status"] == "incomplete"


@pytest.mark.parametrize("defect", ["empty", "duplicate", "unknown-target", "cycle", "path", "oversized"])
def test_input_roster_refuses_before_a_producer_runs(tmp_path, monkeypatch, defect):
    import shutil

    from gnd.examples.literature import reading

    fixture = tmp_path / "fixture"
    shutil.copytree(reading.FIXTURE, fixture)
    path = fixture / "roster.json"
    roster = json.loads(path.read_bytes())
    if defect == "empty":
        roster["questions"] = []
    elif defect == "duplicate":
        roster["questions"].append(roster["questions"][0])
    elif defect == "unknown-target":
        roster["questions"][0]["superseded_by"] = "absent"
    elif defect == "cycle":
        roster["questions"][0]["superseded_by"] = "system"
    elif defect == "path":
        roster["sources"][0]["path"] = "../study.txt"
    path.write_text(" " * (128 * 1024 + 1) if defect == "oversized" else json.dumps(roster))
    monkeypatch.setattr(reading.SavedProducer, "produce", lambda *_: pytest.fail("admitted invalid roster"))
    with pytest.raises((reading.ArtifactError, reading.ExampleError)):
        reading.run(tmp_path / "out", fixture=fixture)


def test_absence_requires_all_four_exact_inputs_and_rejects_low_recall(fresh):
    from gnd.artifacts import sha256_hex
    from gnd.examples.literature import reading

    run, _ = fresh
    bound = {name: (run / name).read_bytes() for name in ("scope.json", "closure.json", "coverage.json")}
    bound["fidelity.json"] = (run / "fidelity-high.json").read_bytes()
    pins = {name: sha256_hex(raw) for name, raw in bound.items()}
    assert reading.absence_status(bound, pins) == "qualified"
    for name, raw in bound.items():
        reduced = {key: value for key, value in bound.items() if key != name}
        assert reading.absence_status(reduced, pins) == "unavailable"
        assert reading.absence_status({**bound, name: raw + b" "}, pins) == "unavailable"
    low = (run / "fidelity-low.json").read_bytes()
    assert reading.absence_status({**bound, "fidelity.json": low},
                                  {**pins, "fidelity.json": sha256_hex(low)}) == "unavailable"


def test_repeated_inspections_charge_both_actual_reads():
    from gnd.examples.literature import reading

    inputs = reading.ReadingInputs(reading.FIXTURE)
    producer = reading.SavedProducer(inputs)
    selected = "study-opening"
    size = len(inputs.source_range(inputs.sections[selected]))
    payload, remaining = reading._inspect(
        inputs, "broad-extraction", [selected, selected], size * 2, producer, {},
    )
    assert len(payload["attempts"]) == 2
    assert producer.calls["broad-extraction"] == 2
    assert remaining == 0


def test_reported_violation_round_trip_is_available(fresh):
    run, report = fresh
    retained = json.loads((run / "reported-conflict.population.json").read_bytes())
    labels = retained["facts"]["subject_label"]
    assert len(labels) == 2 and labels[0]["subject"] == labels[1]["subject"]
    assert labels[0]["label"] != labels[1]["label"]
    assert report["public_routes"]["reported-conflict"] == EXPECTED["violation_exits"]
    assert report["read_denominator"] == {"scheduled": 5, "attempted": 5, "omitted": 0, "unavailable": 0}
    assert report["productivity"]["new_facts_per_byte"] == {
        "numerator": 2, "denominator": report["reading_bytes"],
    }


def test_source_review_refuses_changed_semantics_before_check(tmp_path, monkeypatch):
    import shutil

    from gnd.examples.literature import reading

    fixture = tmp_path / "fixture"
    shutil.copytree(reading.FIXTURE, fixture)
    saved = fixture / "responses.json"
    doc = json.loads(saved.read_bytes())
    doc["study-methods"]["facts"]["approximation"][0]["value"] = "An unreviewed integrator"
    saved.write_text(json.dumps(doc))
    monkeypatch.setattr(reading, "_public_results", lambda *_: pytest.fail("admitted stale semantic review"))
    with pytest.raises(reading.ExampleError, match="stale semantic reading review"):
        reading.run(tmp_path / "out", fixture=fixture)


def test_maximum_question_roster_is_bounded(tmp_path):
    import shutil
    import time

    from gnd.examples.literature import reading

    fixture = tmp_path / "fixture"
    shutil.copytree(reading.FIXTURE, fixture)
    path = fixture / "roster.json"
    roster = json.loads(path.read_bytes())
    for index in range(reading.ROSTER_LIMIT - len(roster["questions"])):
        roster["questions"].append({
            **roster["questions"][0], "id": f"bounded-{index}", "required": False,
        })
    path.write_text(json.dumps(roster))
    started = time.monotonic()
    assert len(reading.ReadingInputs(fixture).questions) == reading.ROSTER_LIMIT
    assert time.monotonic() - started < 5
