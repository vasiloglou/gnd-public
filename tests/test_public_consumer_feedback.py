"""Registered consumer acceptance, refusal and verdict composition guards."""
from __future__ import annotations

import pytest
import test_public_consumer_feedback_support as cases

from gnd.exp import session_eval as consumer
from gnd.semantic_registry import REGISTRY, capture_branches


def test_feedback_registry_has_observable_acceptance_and_refusal_cases():
    contract = cases._contract()
    good = cases._validate(cases._payload())
    bad = cases._validate(cases._payload(), expected_outputs=(cases._observation(state="differs"),))
    constraint = cases._constraint_contract()
    assurance_owned = {
        row.scope_id
        for row in REGISTRY
        if row.surface == "experiment-feedback" and row.family == "assurance"
    }
    assert assurance_owned == {
        f"experiment-feedback:assurance:{surface}:projected"
        for surface in ("snapshot", "derivation", "transition")
    }
    required = {
        row.scope_id
        for row in REGISTRY
        if row.surface == "experiment-feedback"
        and row.family not in {"verifier-derivation", "assurance"}
    }
    with capture_branches() as reached:
        assert consumer.case_decision(contract.required_cases[0], good).accepted
        assert not consumer.case_decision(contract.required_cases[0], bad).accepted
        untrusted = good.model_copy(update={"payload_valid": False})
        assert not consumer.case_decision(contract.required_cases[0], untrusted).accepted
        assert consumer.case_decision(constraint.required_cases[0], good).accepted
        gap = cases._constraint_contract(coverage=(("fixture", 2),))
        decision = consumer.case_decision(gap.required_cases[0], good)
        assert not decision.accepted
        assert [(g.required, g.observed) for g in decision.coverage_gaps] == [(2, 1)]

        second = cases._validate(cases._payload(), case_id="required-b")
        assert consumer.contract_accepts(contract, cases._attempt(good, second))
        for event, owner, attempt in (
            # No-required-cases is an in-process defensive path: contract
            # admission normally refuses this shape.
            ("no-required-cases", contract.model_copy(update={"cases": ()}), cases._attempt()),
            ("missing-case", contract, cases._attempt(good)),
            (
                "stale-candidate",
                contract,
                cases._attempt(good.model_copy(update={"candidate_sha256": "c" * 64}), second),
            ),
            (
                "stale-contract",
                contract,
                cases._attempt(good.model_copy(update={"contract_sha256": "c" * 64}), second),
            ),
            ("rejected-case", contract, cases._attempt(bad, second)),
        ):
            with capture_branches() as route:
                assert not consumer.contract_accepts(owner, attempt)
            assert f"experiment-feedback:contract:n-a:{event}" in route
            assert "experiment-feedback:contract:n-a:accept" not in route

        for version, event in ((1, "legacy-v1"), (2, "current-v2"), (3, "derivation-v3")):
            with capture_branches() as route:
                row = consumer._case_feedback(
                    good, case=contract.required_cases[0], schema_version=version
                )
            assert row.case_id == good.case_id
            assert f"experiment-feedback:projection:n-a:{event}" in route
        row = consumer._case_feedback(good, case=constraint.required_cases[0], schema_version=2)
        assert row.acceptance.mode == "constraint-satisfaction"
        with pytest.raises(ValueError, match="unsupported feedback schema version"):
            consumer._case_feedback(good, case=contract.required_cases[0], schema_version=99)

        base = {
            "run_id": "registry-feedback",
            "contract": contract,
            "contract_sha256": cases.CONTRACT_SHA,
            "invocation": cases._invocation(),
            "evaluation": cases._attempt(good, second),
            "disposition": "accepted",
        }
        feedback = consumer.build_attempt_feedback(**base)
        assert feedback.acceptance_ready
        assert "scope_id" not in consumer.canonical_feedback(feedback)[0].decode()
        for event, updates, message in (
            (
                "evaluation-contract-mismatch",
                {"contract_sha256": "c" * 64},
                "evaluation contract digest",
            ),
            ("missing-contract", {"contract": None}, "requires the normalized contract"),
            ("contract-id-mismatch", {"contract_id": "wrong"}, "contract_id disagrees"),
            (
                "undeclared-case",
                {"evaluation": cases._attempt(good.model_copy(update={"case_id": "unknown"}))},
                "not declared",
            ),
            (
                "case-role-mismatch",
                {"evaluation": cases._attempt(good.model_copy(update={"role": "diagnostic"}))},
                "wrong case role",
            ),
            (
                "case-candidate-mismatch",
                {
                    "evaluation": cases._attempt(
                        good.model_copy(update={"candidate_sha256": "c" * 64})
                    )
                },
                "stale candidate",
            ),
            (
                "case-contract-mismatch",
                {
                    "evaluation": cases._attempt(
                        good.model_copy(update={"contract_sha256": "c" * 64})
                    )
                },
                "stale contract",
            ),
        ):
            with capture_branches() as route, pytest.raises(ValueError, match=message):
                consumer.build_attempt_feedback(**{**base, **updates})
            assert f"experiment-feedback:attempt:n-a:{event}" in route
            assert "experiment-feedback:attempt:n-a:built" not in route
    assert required <= reached, sorted(required - reached)

def observe_public_constraint_compositions():
    """Replay the five authored input cases for both local and shipment gates."""
    required = {row.scope_id for row in REGISTRY if row.family == "verifier-verdict"}
    with capture_branches() as reached:
        for outcome, modality, band in (
            ("pass", "alethic", 0),
            ("fail", "alethic", 1),
            ("warning", "deontic", 0),
            ("unchecked", "alethic", 4),
            ("vacuous", "alethic", 2),
        ):
            result = cases._validate(
                cases._payload(
                    exit_code=band, verdicts=[cases._verdict(outcome, modality=modality)]
                )
            )
            assert result.payload_exit == band
            assert result.counts[outcome] == 1
    assert required <= reached, sorted(required - reached)
    assert not any(
        scope.startswith(("snapshot:", "applicability:", "derivation:")) for scope in reached
    )

def test_public_constraint_rows_are_consumer_inputs_not_snapshot_execution():
    observe_public_constraint_compositions()
