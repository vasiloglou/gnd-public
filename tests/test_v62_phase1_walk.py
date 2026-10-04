

from __future__ import annotations

import pytest
from support.v62_phase1_corpus import ANSWERS, CASES, FIXTURE, population, steps

from gnd.api import transition


@pytest.mark.parametrize("case_id", ["E01", "E02", "E03", "E04", "E05"])
def test_walk_case(case_id: str) -> None:
    case = CASES[case_id]
    payload = transition(
        FIXTURE / "models/static.orm.yaml",
        population(case["pre"]),
        steps(),
        population(case["post"]),
    )
    answer = ANSWERS[case_id]
    assert payload["exit_code"] == answer["exit"]
    assert payload["transition"]["evaluated"] is True
    verdicts = payload["transition"]["steps"][0]["verdicts"]
    preconditions = [row for row in verdicts if row["kind"] == "precondition"]
    if "precondition" in answer:
        observed = "fail" if preconditions else "pass"
        assert observed == answer["precondition"]
    if "dynamic_verdicts" in answer:
        dynamic = [row for row in verdicts if row["kind"] == "dynamic"]
        assert len(dynamic) == answer["dynamic_verdicts"]


def test_supplied_view_mutation_is_detected_by_e02() -> None:
    payload = transition(
        FIXTURE / "models/static.orm.yaml",
        population("pre_fail"),
        steps(),
        population("post_exact"),
    )
    verdicts = payload["transition"]["steps"][0]["verdicts"]
    assert any(row["kind"] == "precondition" and row["verdict"] == "fail" for row in verdicts)
