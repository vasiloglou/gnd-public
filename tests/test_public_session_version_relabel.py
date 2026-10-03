from __future__ import annotations

import pytest
from pydantic import ValidationError

from gnd.exp.session_eval import AttemptFeedback
from gnd.exp.session_store import SessionResult


def test_feedback_v5_cannot_be_a_relabeled_v4_document() -> None:
    document = {
        "schema_version": 5,
        "run_id": "run-x",
        "contract_id": "EXP-001-session",
        "contract_sha256": "b" * 64,
        "source_attempt_index": 1,
        "candidate_sha256": "a" * 64,
        "case_payload_sha256s": [["required-a", "c" * 64]],
        "normalized_verifier_signature": "d" * 64,
        "process_exit": 0,
        "payload_exit": [["required-a", 0]],
        "acceptance_ready": False,
        "required": [
            {
                "case_id": "required-a",
                "role": "required",
                "command": "check",
                "process_exit": 0,
                "payload_exit": 0,
                "outcome": "accepted",
                "acceptance_ready": True,
                "counts": {
                    "passed": 1,
                    "fail": 0,
                    "warning": 0,
                    "unchecked": 0,
                    "vacuous": 0,
                },
                "coverage": [
                    {"fact_type": "fixture", "declared": "declared", "facts": 1}
                ],
                "issues_total": 0,
                "issues_truncated": False,
                "extraction": {
                    "state": None,
                    "population_sha256": None,
                    "model_sha256": None,
                    "projection_sha256": None,
                    "document_sha256": None,
                },
                "acceptance": {
                    "mode": "exact-bytes",
                    "outputs": [{"output_id": "required-a-out", "state": "differs"}],
                },
                "alethic_failure_count": 0,
                "alethic_indeterminate_count": 0,
                "derivations": [],
                "assurance": None,
            }
        ],
        "diagnostic": [],
        "disposition": "retry",
    }
    with pytest.raises(ValidationError, match="transition"):
        AttemptFeedback.model_validate(document)


def test_result_v3_cannot_be_a_relabeled_v2_document() -> None:
    document = SessionResult(
        run_id="run-x",
        disposition="budget-exhausted",
        terminal_reason="attempt bound reached",
        attempt_count=1,
        referenced_evidence_digests={},
        acceptance_modes=("exact-bytes",),
    ).model_dump(mode="json")
    document["schema_version"] = 3
    with pytest.raises(ValidationError, match="transition"):
        SessionResult.model_validate(document)
