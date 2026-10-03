"""Original compatibility, projection and semantic transition row selectors."""
import json

import pytest
from support.v6_transition_corpus import ANSWERS, BY_ID, CORPUS, assert_answer, observe

ROWS = [
    row
    for row in json.loads((CORPUS / "matrix.json").read_text())["rows"]
    if row["claim_family"] == "compatibility"
]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["scope_id"])
def test_compatibility_rows(row, tmp_path):
    actual = observe(BY_ID[row["case_id"]], tmp_path)
    assert_answer(actual, ANSWERS[row["case_id"]])


ROWS = [
    row
    for row in json.loads((CORPUS / "matrix.json").read_text())["rows"]
    if row["scope_id"].startswith(("composition:band:transition:", "report:transition:"))
]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["scope_id"])
def test_band_and_projection_rows(row, tmp_path):
    actual = observe(BY_ID[row["case_id"]], tmp_path)
    assert_answer(actual, ANSWERS[row["case_id"]])
    assert row["scope_id"] in actual["branches"]


ROWS = [
    row
    for row in json.loads((CORPUS / "matrix.json").read_text())["rows"]
    if row["claim_family"] == "semantic-result"
    and row["scope_id"].startswith(
        (
            "transition:assert-",
            "transition:compiled-",
            "transition:create-",
            "transition:dynamic-",
            "transition:frame-",
            "transition:intermediate-",
            "transition:precondition:",
            "transition:retract-",
        )
    )
]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["scope_id"])
def test_semantic_row_reaches_named_branch(row, tmp_path):
    actual = observe(BY_ID[row["case_id"]], tmp_path)
    assert_answer(actual, ANSWERS[row["case_id"]])
    assert row["scope_id"] in actual["branches"]

