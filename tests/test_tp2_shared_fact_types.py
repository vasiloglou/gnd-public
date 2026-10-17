"""TP2: shared internal fact-type rows preserve detached public queries and parity."""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

from gnd.model import load_model
from gnd.model_index import ModelIndex

ROOT = Path(__file__).resolve().parents[1]
BASELINE = ROOT / ".gnd-planning/milestones/transition-check-performance/evidence/TP0/digests.json"
if "measure_transition_cost" in sys.modules:
    tool = sys.modules["measure_transition_cost"]
else:
    _SPEC = importlib.util.spec_from_file_location(
        "measure_transition_cost", ROOT / "tools/measure_transition_cost.py")
    tool = importlib.util.module_from_spec(_SPEC)
    sys.modules["measure_transition_cost"] = tool
    _SPEC.loader.exec_module(tool)


def test_t1_reporter_copy_bound():
    run = tool.replay("reporter")
    run()
    with tool.counting() as counts:
        run()
    assert counts["deepcopy_nodes"] <= 1_380_197
    assert counts["model_index_key_paths"] == 26
    assert counts["checker_runs"] == 25


def _refuse(*_args, **_kwargs):
    raise TypeError("a shared fact-type row was written")


class _FrozenDict(dict):
    """A dict that refuses writes. It stays a dict, so ``isinstance(row, dict)`` readers
    behave exactly as in production (TP2 finding: a MappingProxyType changed results)."""

    __setitem__ = __delitem__ = clear = pop = popitem = setdefault = update = _refuse
    __ior__ = _refuse


class _FrozenList(list):
    """A list that refuses writes, for the same reason."""

    __setitem__ = __delitem__ = __iadd__ = __imul__ = _refuse
    append = clear = extend = insert = pop = remove = reverse = sort = _refuse


def _freeze(value):
    if isinstance(value, dict):
        return _FrozenDict({key: _freeze(item) for key, item in value.items()})
    if isinstance(value, list):
        return _FrozenList(_freeze(item) for item in value)
    return value


def _assert_payload(payload, expected, name):
    assert tool.normalized_digest(payload) == expected["payload_digest"], name
    assert payload["exit_code"] == expected["exit_code"], name


def test_t2_frozen_readers(monkeypatch):
    original = ModelIndex.iter_fact_types_shared

    def frozen(self):
        return (_freeze(row) for row in original(self))

    monkeypatch.setattr(ModelIndex, "iter_fact_types_shared", frozen)
    model = load_model(tool.COURSE / "model.orm.json")
    row = next(ModelIndex.for_model(model).iter_fact_types_shared())
    with pytest.raises(TypeError):
        row["id"] = "changed"
    with pytest.raises(TypeError):
        row["roles"][0]["role_name"] = "changed"

    baseline = json.loads(BASELINE.read_text())["workloads"]
    calls = tool.reporter_calls()
    payloads = tool.replay("reporter")()
    assert len(payloads) == len(calls)
    for call, payload in zip(calls, payloads, strict=True):
        name = f'{call["index"]:02d}.{call["call"]}'
        _assert_payload(payload, baseline["reporter"][name], name)
    [payload] = tool.replay("course")()
    _assert_payload(payload, baseline["course"]["attempt-3.transition"], "course replay")
    # Surfaces include every course walk and every reporter compiled/admission check.
    for workload in ("reporter", "course"):
        surfaces = tool.surfaces(workload)
        assert {name for name, _ in surfaces} == set(baseline[workload])
        for name, run in surfaces:
            _assert_payload(run(), baseline[workload][name], name)


@pytest.mark.parametrize("accessor", ["fact_types", "iter_fact_types"])
def test_t3_public_rows_remain_detached(accessor):
    model = load_model(tool.COURSE / "model.orm.json")
    index = ModelIndex.for_model(model)
    before = list(index.iter_fact_types_shared())
    expected = json.loads(json.dumps(before))
    rows = index.fact_types if accessor == "fact_types" else index.iter_fact_types()
    row = next(iter(rows))
    row["id"] = "changed"
    row["roles"][0]["role_name"] = "changed"
    assert list(index.iter_fact_types_shared()) == expected
    assert next(index.iter_fact_types_shared()) is before[0]


def test_t4_parity_with_the_tp0_baseline():
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
            key: value for key, value in cli[name].items() if key != "_process_exit"}
        assert tool.normalized_digest(payload) == row["payload_digest"], name


def test_review_f1_frozen_rows_on_anchored_and_partial_paths():
    """TP2 review F1: the anchored and partial-report readers are outside the workloads, so
    the suites that reach them run with every shared row refusing writes."""
    import os
    import subprocess

    env = {**os.environ, "PYTHONPATH": str(ROOT / "tests")}
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "-p", "_tp2_freeze_plugin",
         "tests/test_v70_phase4_constraints.py", "tests/test_rf1_semantic_pins.py"],
        cwd=ROOT, env=env, capture_output=True, text=True, check=False)
    assert result.returncode == 0, result.stdout[-2000:]
    served = int(result.stdout.split("tp2-freeze-all: ")[1].split()[0])
    assert served > 0
