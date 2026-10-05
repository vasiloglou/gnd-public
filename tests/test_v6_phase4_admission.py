"""Phase 4 T09 -- every trusted admission row refuses or admits exactly."""

import json

import pytest
from support.v6_transition_corpus import ANSWERS, BY_ID, CORPUS, assert_answer, observe

ROWS = [
    row
    for row in json.loads((CORPUS / "matrix.json").read_text())["rows"]
    if row["claim_family"] == "trusted-admission"
]


@pytest.mark.parametrize("row", ROWS, ids=lambda row: row["scope_id"])
def test_trusted_admission_rows(row, tmp_path):
    actual = observe(BY_ID[row["case_id"]], tmp_path)
    assert_answer(actual, ANSWERS[row["case_id"]])
    assert row["scope_id"] in actual.get("branches", []) or any(
        issue["rule_id"] == row["scope_id"] for issue in actual.get("issues", [])
    )
