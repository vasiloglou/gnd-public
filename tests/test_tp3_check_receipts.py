"""TP3: receipt minting, ordered refusals and pre-state reuse."""
from __future__ import annotations

import importlib.util
import json
import pickle
import sys
from pathlib import Path

import pytest

from gnd import api
from gnd.branches import capture_branches
from gnd.model import load_model
from gnd.population import load_population, load_population_bytes

ROOT = Path(__file__).resolve().parents[1]
COURSE = ROOT / "src/gnd/examples/plan_apps/course"
if "measure_transition_cost" in sys.modules:
    tool = sys.modules["measure_transition_cost"]
else:
    _SPEC = importlib.util.spec_from_file_location(
        "measure_transition_cost", ROOT / "tools/measure_transition_cost.py")
    tool = importlib.util.module_from_spec(_SPEC)
    sys.modules["measure_transition_cost"] = tool
    _SPEC.loader.exec_module(tool)


def course():
    model = load_model(COURSE / "model.orm.json")
    return model, load_population(COURSE / "state.pop.json", model=model)


def observed(call):
    with capture_branches() as branches, tool.counting() as counts:
        payload = call()
    return payload, tool.trace_digest(branches), counts["checker_runs"]


def test_t1_minting_parity_and_one_check():
    model = load_model(tool.REPORTER / "steps.orm.json")
    inputs = [(model, load_population(tool.REPORTER / c["population"], model=model))
              for c in tool.reporter_calls() if c["call"] == "check"]
    inputs.append(course())
    assert len(inputs) == 8
    for model, population in inputs:
        expected, trace, runs = observed(lambda m=model, p=population: api.check(m, p))
        minted, receipt_trace, receipt_runs = observed(
            lambda m=model, p=population: api.check_with_receipt(m, p))
        payload, receipt = minted
        assert tool.normalized_digest(payload) == tool.normalized_digest(expected)
        assert receipt_trace == trace
        assert runs == receipt_runs == 1
        assert receipt.reusable
        assert receipt.model is model
        assert receipt.options == ()
        with pytest.raises(TypeError):
            pickle.dumps(receipt)
    with pytest.raises(TypeError):
        api.CheckReceipt()
    with pytest.raises(TypeError):
        api.check_with_receipt(COURSE / "model.orm.json", inputs[-1][1])
    with pytest.raises(TypeError):
        api.check_with_receipt(inputs[-1][0], COURSE / "state.pop.json")


def test_t2_reporter_replay():
    plain, trace, runs = observed(tool.replay("reporter"))
    reused, reused_trace, reused_runs = observed(tool.replay("reporter-receipts"))
    assert runs == 25
    assert reused_runs == 19
    assert len(plain) == len(reused) == 13
    assert [tool.normalized_digest(p) for p in plain] == [
        tool.normalized_digest(p) for p in reused]
    assert trace == reused_trace
    # Compare each call's trace too, rather than only their union.
    model = load_model(tool.REPORTER / "steps.orm.json")
    receipt = None
    for call in tool.reporter_calls():
        population = load_population(tool.REPORTER / call["population"], model=model)
        if call["call"] == "check":
            normal = observed(lambda m=model, p=population: api.check(m, p))
            minted = observed(lambda m=model, p=population: api.check_with_receipt(m, p))
            payload, receipt = minted[0]
            assert minted[1] == normal[1]
            assert tool.normalized_digest(payload) == tool.normalized_digest(normal[0])
        else:
            steps = json.loads((tool.REPORTER / call["steps"]).read_text())
            normal = observed(lambda p=population, s=steps: api.transition(model, p, s))
            reused = observed(lambda p=population, s=steps, r=receipt: api.transition(model, p, s, pre_receipt=r))
            assert normal[1] == reused[1]
            assert tool.normalized_digest(normal[0]) == tool.normalized_digest(reused[0])


def refused(reason, model, population, receipt, **kwargs):
    with tool.counting() as counts, pytest.raises(api.ReceiptRefused) as error:
        api.transition(model, population, {}, pre_receipt=receipt, **kwargs)
    assert error.value.reason == reason
    assert str(error.value) == reason
    assert counts["checker_runs"] == 0


def test_t3_refusals_and_order():
    model, population = course()
    _, receipt = api.check_with_receipt(model, population)
    refused("foreign", COURSE / "model.orm.json", population, object(), references=object())
    forged = object.__new__(api.CheckReceipt)
    refused("foreign", model, population, forged)
    refused("path-inputs", COURSE / "model.orm.json", population, receipt, references=object())
    refused("path-inputs", model, COURSE / "state.pop.json", receipt)
    other, _ = course()
    refused("options", other, population, receipt, references=object())
    refused("model-object", other, population, receipt)
    model.operations[0]["reading"] = "edited"
    assert population.matches_validation_marker(model)
    refused("model-changed", model, population, receipt)
    model, population = course()
    _, receipt = api.check_with_receipt(model, population)
    lost = population.model_copy()
    lost._validated_digest = None
    refused("population-unvalidated", model, lost, receipt)
    population.facts["course_credits"][0]["credits"] = 5
    refused("population-unvalidated", model, population, receipt)
    document = json.loads((COURSE / "state.pop.json").read_text())
    document["facts"]["course_credits"][0]["credits"] = 5
    changed = load_population_bytes(json.dumps(document).encode(), source="edited.json", model=model)
    assert changed.matches_validation_marker(model)
    refused("population-changed", model, changed, receipt)
    # This duplicate breaks uniqueness while remaining structurally valid.
    document = json.loads((COURSE / "state.pop.json").read_text())
    document["facts"]["course_credits"].append({"course": "CS101", "credits": 3})
    failing = load_population_bytes(json.dumps(document).encode(), source="bad.json", model=model)
    payload, bad = api.check_with_receipt(model, failing)
    assert payload["exit_code"] == 1
    assert not bad.reusable
    refused("not-reusable", other, failing, bad, references=object())
    equal = load_population(COURSE / "state.pop.json", model=model)
    steps = tool._course_steps("attempt-3.steps.json")
    assert api.transition(model, equal, steps, pre_receipt=receipt) == api.transition(model, equal, steps)


def test_t3_anchored_and_uncacheable():
    model, population = course()
    model.fact_types[0].setdefault("constraints", []).append({"type": "anchored"})
    population = load_population(COURSE / "state.pop.json", model=model)
    with tool.counting() as counts:
        payload, receipt = api.check_with_receipt(model, population)
    assert counts["checker_runs"] == 1
    assert payload == api.check(model, population)
    assert not receipt.reusable
    refused("not-reusable", model, population, receipt)
    model, population = course()
    # Source metadata with a non-JSON value prevents a canonical index key.
    model.source["uncacheable"] = object()
    population = load_population(COURSE / "state.pop.json", model=model)
    _, receipt = api.check_with_receipt(model, population)
    assert receipt.model_key is None
    refused("not-reusable", model, population, receipt)


def test_t4_course_parity():
    model, pre = course()
    steps = tool._course_steps("attempt-3.steps.json")
    _, receipt = api.check_with_receipt(model, pre)
    plain = observed(lambda: api.transition(model, pre, steps))
    reused = observed(lambda: api.transition(model, pre, steps, pre_receipt=receipt))
    assert plain[:2] == reused[:2]
    assert (plain[2], reused[2]) == (5, 4)


def test_t5_stored_branches_and_report_are_used():
    model, pre = course()
    _, receipt = api.check_with_receipt(model, pre)
    steps = tool._course_steps("attempt-3.steps.json")
    # Capture only the shared pre/step spine with no steps: later checks cannot
    # mask the receipt's branch contribution in the union of observed ids.
    from gnd.transition import _evaluate_to_state

    full = observed(lambda: _evaluate_to_state(model, pre, [], pre_receipt=receipt))
    branches = receipt.branches
    object.__setattr__(receipt, "branches", frozenset())
    empty = observed(lambda: _evaluate_to_state(model, pre, [], pre_receipt=receipt))
    assert full[1] != empty[1]
    object.__setattr__(receipt, "branches", branches)
    original = api.transition(model, pre, steps, pre_receipt=receipt)
    report = receipt.report.model_copy(deep=True)
    verdict = report.verdicts[0]
    verdict.modality = "deontic" if verdict.modality == "alethic" else "alethic"
    object.__setattr__(receipt, "report", report)
    changed = api.transition(model, pre, steps, pre_receipt=receipt)
    assert tool.normalized_digest(original) != tool.normalized_digest(changed)


def test_finding_unvalidated_population_mints_like_api_check():
    """TP3 finding 2: a population that lost its marker takes the normal api.check route.

    The payload equals api.check's (a refusal band), the receipt is not reusable, and a
    transition presented with it refuses before evaluating anything."""
    model = load_model(COURSE / "model.orm.json")
    population = load_population(COURSE / "state.pop.json", model=model)
    model.constraints.append({"id": "tp3_unvalidated", "type": "textual", "expression": "x"})
    assert not population.matches_validation_marker(model)
    expected = api.check(model, population)
    payload, receipt = api.check_with_receipt(model, population)
    assert tool.normalized_digest(payload) == tool.normalized_digest(expected)
    assert payload["exit_code"] == expected["exit_code"] >= 3
    assert receipt.reusable is False
    steps = tool._course_steps("attempt-3.steps.json")
    with pytest.raises(api.ReceiptRefused) as refused, tool.counting() as counts:
        api.transition(model, population, steps, pre_receipt=receipt)
    assert refused.value.reason == "not-reusable"
    assert counts["checker_runs"] == 0


def test_finding_receipt_is_immutable():
    model = load_model(COURSE / "model.orm.json")
    population = load_population(COURSE / "state.pop.json", model=model)
    _, receipt = api.check_with_receipt(model, population)
    for name, value in (("reusable", False), ("population_digest", "x"), ("report", None)):
        with pytest.raises(AttributeError):
            setattr(receipt, name, value)
    with pytest.raises(AttributeError):
        del receipt.model
    assert receipt.reusable is True


def test_review_b1_mint_certifies_against_the_same_trace_as_api_check(monkeypatch):
    """TP3 review B1: the assurance trace and its execution completeness must match api.check.

    Release evidence is not installed in development checkouts, so the payload alone cannot
    show the difference; the certification inputs are compared directly."""
    from gnd import checking_service

    seen = []
    original = checking_service._certify_assurance

    def spy(model, populations, result, band, trace, **kwargs):
        block, execution = original(model, populations, result, band, trace, **kwargs)
        seen.append((frozenset(trace), getattr(execution, "complete", None)))
        return block, execution

    monkeypatch.setattr(checking_service, "_certify_assurance", spy)
    model = load_model(COURSE / "model.orm.json")
    population = load_population(COURSE / "state.pop.json", model=model)
    api.check(model, population)
    plain = seen[-1]
    api.check_with_receipt(model, population)
    minted = seen[-1]
    assert plain[1] is True
    assert minted == plain
