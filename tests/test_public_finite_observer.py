"""Complete original selected finite-policy and reader/feedback coordinates."""
import pytest
import test_public_finite_observer_support as finite_observer
from test_public_finite_observer_support import CORPUS, read

ROWS=read(CORPUS / "matrix.json")["rows"]
ANSWERS=read(CORPUS / "answers/expected.json")["cases"]

@pytest.mark.parametrize(
    "row",
    [row for row in ROWS if row["kind"] in {"reader", "legacy-feedback"}],
    ids=lambda row: row["case_id"],
)
def test_live_reader_and_legacy_feedback_coordinates(row):
    observe = finite_observer.reader if row["kind"] == "reader" else finite_observer.legacy_feedback
    assert observe(row) == ANSWERS[row["case_id"]]
