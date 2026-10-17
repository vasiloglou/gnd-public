"""TP0 (transition-check-performance): the issue #24 workload, its counters and parity oracle.

Spec: .gnd-planning/milestones/transition-check-performance/notes/phase-TP0-spec.md, T1-T7.
Runtime code is unchanged; these tests pin the baseline that TP1-TP3 must preserve.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import re
import signal
import sys
from pathlib import Path

import pytest

from gnd import api
from gnd.branches import capture_branches
from gnd.model import load_model
from gnd.model_index import ModelIndex
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests/fixtures/transition_cost"
_SPEC = importlib.util.spec_from_file_location(
    "measure_transition_cost", ROOT / "tools/measure_transition_cost.py")
tool = importlib.util.module_from_spec(_SPEC)
sys.modules["measure_transition_cost"] = tool
_SPEC.loader.exec_module(tool)

#: Spec D5 (amended in TP1): a hang guard, never a performance gate. 120 s fired on the
#: 77 s tool test when another process loaded the machine, so it is 600 s.
HANG_GUARD_SECONDS = 600


@pytest.fixture(autouse=True)
def _hang_guard():
    if not hasattr(signal, "SIGALRM"):
        yield
        return

    def expired(_signum, _frame):
        raise TimeoutError(f"exceeded the {HANG_GUARD_SECONDS}s hang guard")

    previous = signal.signal(signal.SIGALRM, expired)
    signal.alarm(HANG_GUARD_SECONDS)
    try:
        yield
    finally:
        signal.alarm(0)
        signal.signal(signal.SIGALRM, previous)

ALLOWED_MODEL_ID = "urn:gnd-fixture:steps@1"
ALLOWED_USER_NOTES = {"Sealed step programs."}
#: (exit code, nonzero counts) per call, pinned at import (evidence/TP0/import.json).
PINNED = {
    0: (2, {"pass": 65, "vacuous": 36}),
    **{i: (2, {}) for i in (1, 3, 5, 7, 9, 11)},
    **{i: (2, {"pass": 72, "vacuous": 29}) for i in (2, 4, 6, 8, 10)},
    12: (2, {"pass": 73, "vacuous": 28}),
}


def _user_notes(value):
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "user_note":
                yield item
            else:
                yield from _user_notes(item)
    elif isinstance(value, list):
        for item in value:
            yield from _user_notes(item)


def test_t1_fixture_integrity_and_neutral_values():
    model = load_model(FIXTURE / "steps.orm.json")
    assert len(model.operations) == 6 and len(model.constraints) == 36
    calls = tool.reporter_calls()
    assert [c["call"] for c in calls].count("check") == 7
    assert [c["call"] for c in calls].count("transition") == 6
    for call in calls:
        population = load_population(FIXTURE / call["population"], model=model)
        assert population.model_id == ALLOWED_MODEL_ID
        if call["call"] == "transition":
            steps = json.loads((FIXTURE / call["steps"]).read_text())
            assert steps["model"] == "steps.orm.json" and len(steps["steps"]) == 1
    rows = re.findall(r"^\| `([^`]+)` \| `[0-9a-f]{64}` \| `([0-9a-f]{64})` \|$",
                      (FIXTURE / "PROVENANCE.md").read_text(), re.MULTILINE)
    committed = sorted(p.name for p in FIXTURE.glob("*.json"))
    assert sorted(name for name, _ in rows) == committed
    for name, digest in rows:
        assert hashlib.sha256((FIXTURE / name).read_bytes()).hexdigest() == digest, name
    for name in committed:
        document = json.loads((FIXTURE / name).read_text())
        if isinstance(document, dict):
            header = document.get("population") or {}
            model_id = document.get("model_id", header.get("model_id"))
            assert model_id in (None, ALLOWED_MODEL_ID), name
        assert set(_user_notes(document)) <= ALLOWED_USER_NOTES, name


def test_t2_replay_pins_and_course_exits():
    payloads = tool.replay("reporter")()
    for index, payload in enumerate(payloads):
        exit_code, counts = PINNED[index]
        assert payload["exit_code"] == exit_code, index
        assert {k: v for k, v in payload["counts"].items() if v} == counts, index
    rows = dict(tool.surfaces("course"))
    assert rows["attempt-3.transition"]()["exit_code"] == 0
    assert rows["attempt-1.transition"]()["exit_code"] == 1
    assert rows["attempt-2.transition"]()["exit_code"] == 1


def test_t3_batch_and_cli_match_api():
    cli = tool.cli_surfaces()
    batch = cli["cli.batch"]
    assert batch["exit_code"] == 2
    assert batch["payload"]["summary"]["outcomes"]["violated"] == 0
    assert batch["payload"]["summary"]["projections"] == 7
    rows = dict(tool.surfaces("reporter"))
    pairs = (("cli.check.00", "00.check"), ("cli.transition.01", "01.transition.post"))
    for cli_name, api_name in pairs:
        payload = {k: v for k, v in cli[cli_name].items() if k != "_process_exit"}
        assert cli[cli_name]["_process_exit"] == payload["exit_code"] == 2
        assert tool.normalized_digest(payload) == tool.normalized_digest(rows[api_name]())


def test_t4_counter_liveness_both_directions():
    run = tool.replay("reporter")
    with tool.counting() as counts:
        run()
    assert counts["checker_runs"] == 25
    assert all(counts[key] > 0 for key in tool.COUNTER_KEYS), counts
    model = load_model(FIXTURE / "steps.orm.json")
    population = load_population(FIXTURE / "00-check-population.json", model=model)
    with tool.counting() as extra:
        api.check(model, population)
    assert extra["checker_runs"] == 1

    index = ModelIndex.for_model(model)
    raw = model.model_dump(exclude={"warnings"}, warnings=False)["fact_types"]

    def nodes(value) -> int:
        if isinstance(value, dict):
            return 1 + sum(nodes(k) + nodes(v) for k, v in value.items())
        if isinstance(value, (list, tuple)):
            return 1 + sum(nodes(item) for item in value)
        return 1

    with tool.counting() as copies:
        copied = index.fact_types
    assert len(copied) == len(raw)
    assert copies["deepcopy_calls"] == 1
    assert copies["deepcopy_nodes"] == nodes(raw)

    course = tool.replay("course")
    with tool.counting() as walk:
        course()
    assert walk["checker_runs"] == 5


def test_t5_cr01_baseline_marker_and_index_key():
    model = load_model(FIXTURE / "steps.orm.json")
    population = load_population(FIXTURE / "00-check-population.json", model=model)
    assert population.matches_validation_marker(model)
    before = ModelIndex.for_model(model).digest
    model.operations[0]["reading"] = "changed by the CR-01 baseline test"
    assert population.matches_validation_marker(model)
    assert ModelIndex.for_model(model).digest != before
    model.constraints[0]["id"] = model.constraints[0]["id"] + "_mutated"
    assert not population.matches_validation_marker(model)


def test_t6_parity_oracle_is_stable_and_live(monkeypatch):
    first = tool.measure("course")["surfaces"]
    second = tool.measure("course")["surfaces"]
    assert {n: (r["payload_digest"], r["trace_digest"]) for n, r in first.items()} == \
        {n: (r["payload_digest"], r["trace_digest"]) for n, r in second.items()}

    from gnd.checker import _core

    original = _core._check_dispatch

    def flipped(model, population):
        report = original(model, population)
        verdict = report.verdicts[0]
        modality = "deontic" if verdict.modality == "alethic" else "alethic"
        return report.model_copy(update={"verdicts": [verdict.model_copy(
            update={"modality": modality}), *report.verdicts[1:]]})

    monkeypatch.setattr(_core, "_check_dispatch", flipped)
    mutated = dict(tool.surfaces("course"))["pre.check"]()
    monkeypatch.undo()
    assert tool.normalized_digest(mutated) != first["pre.check"]["payload_digest"]

    from gnd import branches

    with capture_branches() as reached:
        dict(tool.surfaces("course"))["pre.check"]()
    dropped = min(reached)
    original_record = branches.record_branch

    def dropping(scope_id, **kwargs):
        if scope_id == dropped:
            return scope_id
        return original_record(scope_id, **kwargs)

    for module in [m for n, m in list(sys.modules.items()) if n.split(".")[0] == "gnd"]:
        for name, value in list(vars(module).items()):
            if value is original_record:
                monkeypatch.setattr(module, name, dropping)
    with capture_branches() as fewer:
        dict(tool.surfaces("course"))["pre.check"]()
    monkeypatch.undo()
    assert dropped not in fewer
    assert tool.trace_digest(fewer) != first["pre.check"]["trace_digest"]


def test_t7_tool_writes_schema_tagged_files(tmp_path):
    assert tool.main(["--out", str(tmp_path), "--repeat", "1"]) == 0
    counters = json.loads((tmp_path / "counters.json").read_text())
    digests = json.loads((tmp_path / "digests.json").read_text())
    timings = json.loads((tmp_path / "timings.json").read_text())
    assert counters["schema"] == "transition-cost-counters/1"
    assert digests["schema"] == "transition-cost-digests/1"
    assert timings["schema"] == "transition-cost-timings/1"
    assert counters["workloads"]["reporter"]["replay"]["checker_runs"] == 25
    assert counters["workloads"]["course"]["replay"]["checker_runs"] == 5
    surfaces = set(digests["workloads"]["reporter"])
    for suffix in ("check", "check.compiled", "check.admission"):
        assert {f"{i:02d}.{suffix}" for i in (0, 2, 4, 6, 8, 10, 12)} <= surfaces
    for suffix in ("transition", "transition.post"):
        assert {f"{i:02d}.{suffix}" for i in (1, 3, 5, 7, 9, 11)} <= surfaces
    assert set(digests["cli"]) == {"cli.check.00", "cli.course.check.pre", "cli.transition.01",
                                   "cli.batch"}
    assert digests["cli"]["cli.batch"]["payload_digest"].startswith("sha256:")
    assert {"pre.check", "pre.check.compiled", "pre.check.admission",
            "attempt-3.transition"} <= set(digests["workloads"]["course"])


# Review successors (TP0 diff review, F1-F7). Each kills a mutant or a defect the reviewer
# reproduced; the approved T1-T7 meanings are unchanged.


def test_review_f3_key_path_attribution():
    model = load_model(FIXTURE / "steps.orm.json")
    with tool.counting() as via_index:
        ModelIndex.for_model(model)
    assert (via_index["model_index_key_paths"], via_index["model_dumps_other"]) == (1, 0)
    with tool.counting() as direct:
        model.model_dump()
    assert (direct["model_index_key_paths"], direct["model_dumps_other"]) == (0, 1)


def test_review_f4_trace_digest_covers_identity_not_count():
    assert tool.trace_digest({"a", "b"}) != tool.trace_digest({"a", "c"})
    assert tool.trace_digest({"b", "a"}) == tool.trace_digest({"a", "b"})


def test_review_f5_counting_restores_the_classmethod():
    model = load_model(FIXTURE / "steps.orm.json")
    original = ModelIndex.__dict__["for_model"]
    with tool.counting():
        pass
    assert ModelIndex.__dict__["for_model"] is original
    assert isinstance(ModelIndex.__dict__["for_model"], classmethod)
    assert ModelIndex.for_model(model).digest is not None


def test_review_f7_top_level_calls_only_from_gnd_frames():
    import copy

    with tool.counting() as counts:
        copy.deepcopy({"a": [1, 2, {"b": 3}]})
    assert counts["deepcopy_calls"] == 0  # called from this test, not from GND code
    assert counts["deepcopy_nodes"] == 8  # dict, "a", list, 1, 2, inner dict, "b", 3


def test_review_f1_f2_course_surfaces_and_batch_digest(tmp_path):
    names = {name for name, _ in tool.surfaces("course")}
    assert {"pre.check", "pre.check.compiled", "pre.check.admission",
            "attempt-1.transition", "attempt-2.transition", "attempt-3.transition"} <= names
    cli = tool.cli_surfaces()
    assert cli["cli.course.check.pre"]["exit_code"] == 0
    course_pre = dict(tool.surfaces("course"))["pre.check"]()
    payload = {k: v for k, v in cli["cli.course.check.pre"].items() if k != "_process_exit"}
    assert tool.normalized_digest(payload) == tool.normalized_digest(course_pre)
    assert tool.normalized_digest(cli["cli.batch"]["payload"]) == \
        tool.normalized_digest(tool.cli_surfaces()["cli.batch"]["payload"])
