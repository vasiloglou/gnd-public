"""TP1 (transition-check-performance): one ModelIndex key per public call, under CR-01.

Spec: .gnd-planning/milestones/transition-check-performance/notes/phase-TP1-spec.md, T1-T8.
"""
from __future__ import annotations

import importlib.util
import json
import sys
import threading
from pathlib import Path

import pytest

from gnd import api, model_index
from gnd.model import load_model
from gnd.model_index import ModelIndex
from gnd.population import load_population

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "src/gnd/examples/plan_apps/course"
BASELINE = ROOT / ".gnd-planning/milestones/transition-check-performance/evidence/TP0/digests.json"
if "measure_transition_cost" in sys.modules:
    tool = sys.modules["measure_transition_cost"]
else:
    _SPEC = importlib.util.spec_from_file_location(
        "measure_transition_cost", ROOT / "tools/measure_transition_cost.py")
    tool = importlib.util.module_from_spec(_SPEC)
    sys.modules["measure_transition_cost"] = tool
    _SPEC.loader.exec_module(tool)


def _course():
    model = load_model(COURSE / "model.orm.json")
    return model, load_population(COURSE / "state.pop.json", model=model)


@pytest.fixture
def used_digests(monkeypatch):
    """Record the digest of every index for_model hands out."""
    seen: list[str | None] = []
    original = ModelIndex.__dict__["for_model"].__func__

    def recording(cls, model):
        index = original(cls, model)
        seen.append(index.digest)
        return index

    monkeypatch.setattr(ModelIndex, "for_model", classmethod(recording))
    return seen


def _operation_mutation_digests(model, population, seen):
    seen.clear()
    first = api.check(model, population)
    before = set(seen)
    model.operations[0]["reading"] = "changed between calls"
    assert population.matches_validation_marker(model)
    seen.clear()
    with tool.counting() as counts:
        second = api.check(model, population)
    return first, second, before, set(seen), counts


def test_t1_reporter_and_course_bounds():
    run = tool.replay("reporter")
    run()
    with tool.counting() as counts:
        run()
    assert counts["model_index_key_paths"] == 26
    assert counts["model_dumps_other"] <= 457
    assert counts["checker_runs"] == 25
    course = tool.replay("course")
    course()
    with tool.counting() as walk:
        course()
    assert (walk["model_index_key_paths"], walk["checker_runs"]) == (2, 5)


def test_t2b_operation_mutation_between_calls_gets_a_fresh_index(used_digests):
    model, population = _course()
    first, second, before, after, counts = _operation_mutation_digests(model, population,
                                                                       used_digests)
    assert first["exit_code"] == second["exit_code"] == 0
    assert counts["model_index_key_paths"] >= 1
    assert before and after and before.isdisjoint(after)


@pytest.mark.parametrize("mutate", [
    lambda m: m.constraints[0].__setitem__("note", "changed between calls"),
    lambda m: m.fact_types[0]["roles"][0].__setitem__("note", "changed between calls"),
], ids=["a-constraint", "c-fact-type"])
def test_t2ac_marker_visible_mutations_get_a_fresh_index(mutate, used_digests):
    model, population = _course()
    api.check(model, population)
    before = ModelIndex.for_model(model).digest
    mutate(model)
    assert not population.matches_validation_marker(model)
    assert ModelIndex.for_model(model).digest != before
    reloaded = load_population(COURSE / "state.pop.json", model=model)
    used_digests.clear()
    with tool.counting() as counts:
        result = api.check(model, reloaded)
    assert result["exit_code"] == 0
    assert counts["model_index_key_paths"] >= 1
    assert before not in set(used_digests)


def test_t3_identity_keyed_mutant_is_caught(used_digests):
    model, population = _course()
    token = model_index._SCOPE.set({})  # a scope that outlives every call: identity memo
    try:
        _, _, before, after, _ = _operation_mutation_digests(model, population, used_digests)
    finally:
        model_index._SCOPE.reset(token)
    assert not before.isdisjoint(after)  # the mutant serves the stale index; T2b would fail


def test_t4_hits_cost_no_dump_and_the_scope_is_capped():
    model, _ = _course()
    with tool.counting() as counts, model_index.index_scope():
        for _ in range(1000):
            ModelIndex.for_model(model)
    assert (counts["model_index_key_paths"], counts["model_dumps_other"]) == (1, 0)
    models = [load_model(COURSE / "model.orm.json") for _ in range(9)]
    with model_index.index_scope():
        for each in models:
            ModelIndex.for_model(each)
        assert len(model_index._SCOPE.get()) == model_index._SCOPE_LIMIT == 8
        with tool.counting() as evicted:
            ModelIndex.for_model(models[0])
        with tool.counting() as kept:
            ModelIndex.for_model(models[-1])
    assert evicted["model_index_key_paths"] == 1
    assert kept["model_index_key_paths"] == 0


def test_t5_type_error_first_inside_a_scope():
    with model_index.index_scope(), pytest.raises(TypeError):
        ModelIndex.for_model("not a model")


def test_t6_no_leaks_and_nested_scopes_join():
    model, _ = _course()
    with model_index.index_scope():
        ModelIndex.for_model(model)
    assert model_index._SCOPE.get() is None
    with tool.counting() as after_exit:
        ModelIndex.for_model(model)
    assert after_exit["model_index_key_paths"] == 1

    with pytest.raises(RuntimeError), model_index.index_scope():
        ModelIndex.for_model(model)
        raise RuntimeError("leave the scope through an exception")
    assert model_index._SCOPE.get() is None

    seen_in_thread = {}
    with model_index.index_scope():
        ModelIndex.for_model(model)

        def other_thread():
            seen_in_thread["scope"] = model_index._SCOPE.get()

        worker = threading.Thread(target=other_thread)
        worker.start()
        worker.join()
        with tool.counting() as nested, model_index.index_scope():
            ModelIndex.for_model(model)
    assert seen_in_thread["scope"] is None
    assert nested["model_index_key_paths"] == 0


def test_t7_parity_with_the_tp0_baseline():
    baseline = json.loads(BASELINE.read_text())
    for workload in ("reporter", "course"):
        measured = tool.measure(workload)["surfaces"]
        expected = baseline["workloads"][workload]
        assert set(measured) >= set(expected)
        for name, row in expected.items():
            assert measured[name]["payload_digest"] == row["payload_digest"], name
            assert measured[name]["trace_digest"] == row["trace_digest"], name
            assert measured[name]["exit_code"] == row["exit_code"], name
    cli = tool.cli_surfaces()
    for name, row in baseline["cli"].items():
        payload = cli[name]["payload"] if name == "cli.batch" else {
            k: v for k, v in cli[name].items() if k != "_process_exit"}
        assert tool.normalized_digest(payload) == row["payload_digest"], name


# Review successors (TP1 diff review). F1: each entry point's own scope has a counted case,
# so removing any single decorator fails a test. F2: D3 (uncacheable snapshots are reused
# within a scope) has a case.


def _key_paths(call) -> int:
    with tool.counting() as counts:
        call()
    return counts["model_index_key_paths"]


@pytest.mark.parametrize("route", ["load_population", "load_population_bytes", "api.check",
                                   "api.transition", "checker.check", "batch"])
def test_review_f1_each_entry_point_opens_its_own_scope(route, tmp_path):
    from gnd import checker
    from gnd.batch import check_population_directory
    from gnd.population import load_population_bytes

    model, population = _course()
    state = COURSE / "state.pop.json"
    steps = tool._course_steps("attempt-3.steps.json")
    for index in range(3):
        (tmp_path / f"p{index}.json").write_bytes(state.read_bytes())
    calls = {
        "load_population": lambda: load_population(state, model=model),
        "load_population_bytes": lambda: load_population_bytes(
            state.read_bytes(), source="state.pop.json", model=model),
        # Path inputs: the model and population load inside _run_check, so its own scope
        # is what joins them; loaded inputs would be covered by _check_dispatch alone.
        "api.check": lambda: api.check(COURSE / "model.orm.json", state),
        "api.transition": lambda: api.transition(model, population, steps),
        "checker.check": lambda: checker.check(model, population),
        "batch": lambda: check_population_directory(COURSE / "model.orm.json", tmp_path),
    }
    assert _key_paths(calls[route]) == 1


def test_review_f2_uncacheable_snapshot_is_reused_within_a_scope():
    model, _ = _course()
    model.source["cycle"] = model.source  # cyclic metadata: uncacheable, digest None
    with model_index.index_scope():
        first = ModelIndex.for_model(model)
        with tool.counting() as counts:
            second = ModelIndex.for_model(model)
    assert first.digest is None
    assert second is first and counts["model_index_key_paths"] == 0
