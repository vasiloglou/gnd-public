

from __future__ import annotations

import pytest
from support.v62_phase1_corpus import ANSWERS, CASES, FIXTURE, population, steps

from gnd.api import transition


@pytest.mark.parametrize("case_id", ["P01", "P02", "P03"])
def test_post_case(case_id: str) -> None:
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
    if "frame_verdicts" in answer:
        assert len(payload["transition"]["frame_verdicts"]) == answer["frame_verdicts"]
    if answer.get("post_recomputed"):
        assert payload["transition"]["post_snapshot"] is not None


def test_stale_pre_extension_mutation_is_detected_by_p03() -> None:
    payload = transition(
        FIXTURE / "models/static.orm.yaml",
        population("pre_clean"),
        steps(),
        population("post_drift"),
    )
    assert payload["exit_code"] == ANSWERS["P03"]["exit"]
    assert payload["transition"]["frame_verdicts"] == []
