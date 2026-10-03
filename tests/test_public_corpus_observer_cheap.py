"""Complete original provider-free census, exclusion/witness/resource controls."""
import pytest
import test_public_corpus_observer_support as corpus_observer
from test_public_corpus_observer_support import ANSWERS, ROWS


def test_all_provider_free_coordinates_match_the_frozen_answers():
    selected = [row for row in ROWS if row["kind"] in {"policy", "reader", "legacy-feedback", "resource"}]
    assert len(selected) == 275
    for row in selected:
        assert corpus_observer.cheap(row) == ANSWERS[row["case_id"]], row["case_id"]

def test_exclusion_is_derived_from_release_row_status():
    rows = [row for row in ROWS if row["kind"] == "exclusion"]
    manifest = {
        "rows": [{"scope_id": row["recipe"]["scope_id"], "status": "excluded"} for row in rows]
    }
    for row in rows:
        assert corpus_observer.cheap(row, manifest=manifest) == ANSWERS[row["case_id"]]

def test_witness_control_compares_a_live_semantic_projection():
    row = next(row for row in ROWS if row["case_id"] == "witness:expense-approval:oracle")
    semantic = {
        "band": 1,
        "projection": {"verdicts": [{}, {"verdict": "fail", "witness": row["recipe"]["before"]}]},
    }
    assert corpus_observer.witness(row, semantic) == ANSWERS[row["case_id"]]

def test_document_cap_observation_calls_the_production_reader(monkeypatch):
    class ReaderReached(RuntimeError):
        pass

    row = next(row for row in ROWS if row["case_id"] == "resource:document-cap:0")

    def reached(*_args, **_kwargs):
        raise ReaderReached

    monkeypatch.setattr(corpus_observer.assurance_evidence, "_read", reached)
    with pytest.raises(ReaderReached):
        corpus_observer.resource(row)

def test_disabled_bundle_guard_changes_the_over_limit_observation(monkeypatch):
    row = next(row for row in ROWS if row["case_id"] == "resource:bundle-cap:1")
    monkeypatch.setattr(
        corpus_observer.assurance_evidence,
        "enforce_bundle_limits",
        lambda *_args, **_kwargs: None,
    )
    assert corpus_observer.resource(row) != ANSWERS[row["case_id"]]
