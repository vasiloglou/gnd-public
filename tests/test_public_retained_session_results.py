"""Retained v1 result-wire decoder parity; archived outcomes confer no live authority."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from gnd.artifacts import canonical_json_bytes
from gnd.exp.session_store import SessionResult

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]

# Original labels address two retained result wires only, never whole private sessions.
PINNED_CENSUSES = {'EXP-001-live-approval-chain': None, 'EXP-002-contract-acceptance': None}
RESULT_WIRES = {'EXP-001-live-approval-chain': '{"attempt_count":1,"best_attempt":1,"best_attempt_manifest_sha256":"1fa08ea514abebbfd98060b9b00bbeec36876f0a3d6a37114c13094a2989f588","best_candidate_sha256":"537fb23fb056bfe68e439865a537bdd8f506dfc0e78fc941efe9683ea5d7890c","disposition":"accepted","referenced_evidence_digests":{"attempt_manifest_sha256":"1fa08ea514abebbfd98060b9b00bbeec36876f0a3d6a37114c13094a2989f588"},"run_id":"run-0001","schema_version":1,"terminal_reason":"all required cases accepted"}\n', 'EXP-002-contract-acceptance': '{"attempt_count":1,"best_attempt":1,"best_attempt_manifest_sha256":"9bed8d4f44ad392f58f5c64e11844e8a9ee568f15271e98e4afa820ef2ed5f1a","best_candidate_sha256":"953d772394f78ee20bd657725ebc8b6ad8c79e4748e8f6b9662655f61692ec22","disposition":"accepted","referenced_evidence_digests":{"attempt_manifest_sha256":"9bed8d4f44ad392f58f5c64e11844e8a9ee568f15271e98e4afa820ef2ed5f1a"},"run_id":"run-0001","schema_version":1,"terminal_reason":"all required cases accepted"}\n'}

@pytest.fixture(autouse=True)
def _public_retained_result_wires(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(globals(), "REPOSITORY_ROOT", tmp_path)
    for label, text in RESULT_WIRES.items():
        result_path = tmp_path / "examples" / "expense-tracker" / label / "runs" / "run-0001" / "result.json"
        result_path.parent.mkdir(parents=True)
        result_path.write_bytes(text.encode("utf-8"))

@pytest.mark.parametrize("experiment_id", sorted(PINNED_CENSUSES))
def test_both_validation_entry_points_read_retained_v1_evidence_identically(
    experiment_id: str,
) -> None:
    """The dispatcher is not bypassable by holding bytes instead of a dict.

    ``model_validate_json`` is a SEPARATE pydantic entry point rather than a
    decode in front of ``model_validate``, so a class that dispatches on
    ``schema_version`` in the latter alone is only version-aware for callers
    that happen to parse first. The test above reads through
    ``model_validate(json.loads(...))`` and therefore could never see the
    difference — which is exactly how the bypass survived: parsed directly
    against :class:`SessionResult`, a v1 document takes the v2
    ``acceptance_modes`` default and reds on the canonical-wire validator, so
    the frozen v1 reader retained for THESE two runs never executes.

    Asserted as equality of the two entry points rather than as "v1 parses",
    because the claim that matters is that a caller cannot pick a weaker
    reader by accident.
    """
    root = REPOSITORY_ROOT / "examples" / "expense-tracker" / experiment_id
    result_bytes = (root / "runs" / "run-0001" / "result.json").read_bytes()

    from_document = SessionResult.model_validate(json.loads(result_bytes))
    from_bytes = SessionResult.model_validate_json(result_bytes)

    assert from_bytes == from_document
    assert from_bytes.schema_version == 1
    assert from_bytes.acceptance_modes == ()
    assert canonical_json_bytes(from_bytes) == result_bytes

