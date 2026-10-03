

from __future__ import annotations

import json

import pytest
from support.v62_phase1_corpus import ANSWERS, CASES, FIXTURE, population, steps

from gnd.api import transition


@pytest.mark.parametrize("case_id", ["G01", "G02", "G03", "G04"])
def test_coverage_case(case_id: str) -> None:
    case = CASES[case_id]
    post = population(case["post"]) if "post" in case else population("post_exact")
    payload = transition(
        FIXTURE / "models/static.orm.yaml",
        population(case["pre"]),
        steps(),
        post,
    )
    answer = ANSWERS[case_id]
    assert payload["exit_code"] == answer["exit"]
    if "rule_id" in answer:
        assert payload["issues"][0]["rule_id"] == answer["rule_id"]
        assert "final_eligible" in payload["issues"][0]["message"]
        assert (
            answer["dependency"] in payload["issues"][0]["message"]
            if "dependency" in answer
            else True
        )
    if "forbidden" in answer:
        assert answer["forbidden"] not in json.dumps(payload, sort_keys=True)
