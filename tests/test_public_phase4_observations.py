"""Full ordinary transition corpus observation and discriminating controls."""
from __future__ import annotations

import copy

import pytest
from test_public_phase4_transition_support import (
    ANSWERS,
    BY_ID,
    CASES,
    assert_answer,
    corrupt_answer,
    observe,
)

ORDINARY = [case for case in CASES if case["kind"] != "order"]

@pytest.mark.parametrize("case", ORDINARY, ids=lambda c: c["id"])
def test_authored_answer_and_matcher_negative_control(case, tmp_path):
    actual = observe(case, tmp_path)
    assert_answer(actual, ANSWERS[case["id"]])
    with pytest.raises(AssertionError):
        assert_answer(actual, corrupt_answer(ANSWERS[case["id"]]))

def test_wrong_witness_is_rejected_with_band_and_verdict_unchanged(tmp_path):
    actual = observe(BY_ID["threshold-cut"], tmp_path)
    correct = ANSWERS["threshold-cut"]
    assert_answer(actual, correct)
    wrong = copy.deepcopy(correct)
    wrong["exact_verdicts"][0]["offending_facts"][0]["new"] = 301
    assert wrong["exit"] == correct["exit"]
    assert wrong["exact_verdicts"][0]["verdict"] == correct["exact_verdicts"][0]["verdict"]
    with pytest.raises(AssertionError, match="exact witness"):
        assert_answer(actual, wrong)

def test_deleted_dispatch_operator_is_rejected(tmp_path, monkeypatch):
    from gnd import transition

    case = next(c for c in CASES if c["kind"] == "dispatch")
    assert_answer(observe(case, tmp_path), ANSWERS[case["id"]])
    monkeypatch.delitem(transition._COMPARISONS, "!=")
    with pytest.raises(AssertionError):
        assert_answer(observe(case, tmp_path), ANSWERS[case["id"]])
