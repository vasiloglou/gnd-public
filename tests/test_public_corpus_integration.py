"""Original internal-error and required-seat status unit controls."""
import pytest
import test_public_corpus_integration_support as corpus_observer
from test_public_corpus_integration_support import ANSWERS, ROOT, ROWS


@pytest.fixture(autouse=True)
def _generic_root(monkeypatch):
    monkeypatch.chdir(ROOT)

def test_internal_error_and_all_required_seat_outcomes_use_live_owners():
    selected = [
        row
        for row in ROWS
        if row["kind"] == "integration"
        and row["recipe"]["execution"] in {"cli-error-injection", "required-seat-validator"}
    ]
    assert len(selected) == 7
    for row in selected:
        assert corpus_observer.integration(row) == ANSWERS[row["case_id"]]
