"""Public derivation payload shape and consumer route controls."""
from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest
import test_public_consumer_feedback_support as cases

from gnd.exp import session_eval as consumer
from gnd.semantic_registry import REGISTRY, capture_branches


def test_public_derivation_rows_preserve_shape_without_claiming_evaluation():
    corpus = Path(__file__).parent / "fixtures/phase3-consumers"
    seed = json.loads((corpus / "check-v4.incomplete.payload.json").read_text())
    required = {row.scope_id for row in REGISTRY if row.family == "verifier-derivation"}
    with capture_branches() as reached:
        for variant in ("derived", "semiderived"):
            for outcome, reason, band in (
                ("pass", None, 0),
                ("fail", None, 1),
                ("unchecked", "derivation-not-covered", 4),
                ("unchecked", "derivation-rule-opaque", 4),
            ):
                payload = copy.deepcopy(seed)
                row = payload["derivations"][0]
                row.update(derivation=variant, verdict=outcome, reason_code=reason)
                if outcome != "fail":
                    row["findings"] = []
                payload.update(
                    exit_code=band,
                    acceptance_ready=band == 0,
                    outcome={0: "accepted", 1: "violated", 4: "indeterminate"}[band],
                    counts={key: int(key == outcome) for key in payload["counts"]},
                )

                def validate(document, band=band, subject=payload["population"]):
                    return consumer.validate_verifier_payload(
                        cases._raw(document),
                        case_id="required-a",
                        role="required",
                        process_exit=band,
                        expected_command="check",
                        expected_subject=subject,
                        candidate_sha256=cases.CANDIDATE_SHA,
                        contract_sha256=cases.CONTRACT_SHA,
                        evidence_candidate_sha256=cases.CANDIDATE_SHA,
                        evidence_contract_sha256=cases.CONTRACT_SHA,
                        expected_schema_version=4,
                    )

                result = validate(payload)
                assert result.payload_exit == band
                assert result.counts[outcome] == 1
                broken = copy.deepcopy(payload)
                broken["counts"][outcome] += 1
                with pytest.raises(consumer.VerifierPayloadError, match="counts"):
                    validate(broken)
    assert required <= reached, sorted(required - reached)
    assert not any(scope.startswith(("snapshot:", "derivation:")) for scope in reached)
