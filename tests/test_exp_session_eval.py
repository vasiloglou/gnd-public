

from __future__ import annotations

import asyncio
import hashlib
import inspect
import json
import os
import stat
import subprocess
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

import gnd.artifacts as artifact_module
import gnd.exp.session_store as session_store_module
from gnd.agent_cli import (
    AgentAdapterId,
    InvocationResult,
    InvocationStatus,
    build_agent_argv,
    invoke_agent,
)
from gnd.exp.session import run_session
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import (
    AttemptEvaluation,
    AttemptFeedback,
    CaseDecision,
    CaseEvaluation,
    CoverageGap,
    ExpectedOutputObservation,
    SessionRedaction,
    VerifierPayloadError,
    best_key,
    build_attempt_feedback,
    canonical_feedback,
    case_decision,
    contract_accepts,
    normalized_verifier_signature,
    observe_expected_outputs,
    validate_verifier_payload,
)
from gnd.exp.session_store import SessionResult, SessionStore
from gnd.report import PAYLOAD_SCHEMA_VERSION, load_report_schema

CANDIDATE_SHA = "a" * 64
CONTRACT_SHA = "b" * 64
RAW_SUBJECT = "candidate/output.json"
EXPECTED_SHA = "1" * 64
OTHER_SHA = "7" * 64


def _verdict(
    verdict: str,
    *,
    modality: str = "alethic",
    constraint_ref: str = "constraints[0]",
) -> dict[str, Any]:
    return {
        "constraint_ref": constraint_ref,
        "constraint_type": "mandatory",
        "modality": modality,
        "source": "explicit",
        "status": "confirmed",
        "verdict": verdict,
        "message": f"fixture {verdict}",
        "offending_facts": [],
        "reason_code": "unsupported" if verdict == "unchecked" else None,
    }


def _payload(
    *,
    exit_code: int = 0,
    command: str = "check",
    verdicts: list[dict[str, Any]] | None = None,
    subject: str = RAW_SUBJECT,
) -> dict[str, Any]:
    outcomes = {
        0: "accepted",
        1: "violated",
        2: "inadequate",
        3: "ill_formed",
        4: "indeterminate",
        70: "internal_error",
    }
    rows = (
        verdicts
        if verdicts is not None
        else ([] if exit_code in {3, 70} else [_verdict("pass")])
    )
    counts = {
        name: sum(row["verdict"] == name for row in rows)
        for name in ("pass", "fail", "warning", "unchecked", "vacuous")
    }
    extraction: dict[str, Any] = {}
    if command == "verify":
        extraction = {
            "state": "ran",
            "reason": None,
            "sidecar": "candidate/output.extraction.json",
            "population_sha256": "c" * 64,
            "model_sha256": "d" * 64,
            "projection_sha256": "e" * 64,
            "document": "candidate/input.md",
            "document_sha256": "f" * 64,
            "skill": "gnd-extract",
            "skill_version": "1",
            "executing_model": "fixture-model",
        }
    return {
        "schema_version": PAYLOAD_SCHEMA_VERSION,
        "tool": "gnd",
        "command": command,
        "outcome": outcomes[exit_code],
        "exit_code": exit_code,
        "acceptance_ready": exit_code == 0,
        "model": "model.orm.yaml",
        "population": subject,
        "counts": counts,
        "verdicts": rows,
        "coverage": (
            {} if exit_code in {3, 70} else {"fixture": {"declared": "declared", "facts": 1}}
        ),
        "extraction": extraction,
        "issues": [],
        "issues_total": 0,
        "issues_truncated": False,
        "warnings": [],
        "error": (
            {"type": "RuntimeError", "message": "fixture"} if exit_code == 70 else None
        ),
        
        
        
        "transition": None,
    }


def _raw(payload: dict[str, Any]) -> bytes:
    return (
        json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def _observation(
    case_id: str = "required-a",
    *,
    state: str = "matched",
    output_id: str | None = None,
    observed_sha256: str | None = None,
) -> ExpectedOutputObservation:


    if observed_sha256 is None:
        observed_sha256 = {
            "matched": EXPECTED_SHA,
            "differs": OTHER_SHA,
            "absent": None,
        }[state]
    return ExpectedOutputObservation(
        output_id=output_id or f"{case_id}-out",
        expected_sha256=EXPECTED_SHA,
        observed_sha256=observed_sha256,
        state=state,
    )


def _validate(
    payload: dict[str, Any],
    *,
    case_id: str = "required-a",
    role: str = "required",
    process_exit: int | None = None,
    expected_command: str | None = None,
    candidate_sha256: str = CANDIDATE_SHA,
    contract_sha256: str = CONTRACT_SHA,
    evidence_candidate_sha256: str = CANDIDATE_SHA,
    evidence_contract_sha256: str = CONTRACT_SHA,
    expected_model: str | None = None,
    expected_outputs: tuple[ExpectedOutputObservation, ...] | None = None,
) -> CaseEvaluation:
    return validate_verifier_payload(
        _raw(payload),
        case_id=case_id,
        role=role,
        process_exit=payload["exit_code"] if process_exit is None else process_exit,
        expected_command=expected_command or payload["command"],
        expected_model=expected_model,
        expected_subject=RAW_SUBJECT,
        candidate_sha256=candidate_sha256,
        contract_sha256=contract_sha256,
        evidence_candidate_sha256=evidence_candidate_sha256,
        evidence_contract_sha256=evidence_contract_sha256,
        require_extraction=payload["command"] == "verify",
        expected_outputs=(
            (_observation(case_id),) if expected_outputs is None else expected_outputs
        ),
    )


def _contract(*, output_digests: dict[str, str] | None = None) -> DataDrivenContract:







    digests = output_digests or {}
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": EXPECTED_SHA,
        "size_bytes": 1,
    }
    model = {**bound, "path": "model.orm.yaml", "sha256": "2" * 64}

    def case(case_id: str, role: str) -> dict[str, Any]:
        return {
            "case_id": case_id,
            "role": role,
            "inputs": [bound],
            "expected_outputs": [
                {
                    **bound,
                    "path": f"expected/{case_id}.json",
                    "sha256": digests.get(case_id, EXPECTED_SHA),
                    "output_id": f"{case_id}-out",
                    "candidate_path": f"{case_id}.json",
                    "comparison": "exact-bytes",
                }
            ],
            "verify": {
                "command": "check",
                "model": model,
                "subject": RAW_SUBJECT,
            },
        }

    return DataDrivenContract.model_validate(
        {
            "schema_version": 1,
            "experiment_id": "EXP-001-session",
            "max_attempts": 1,
            "wall_seconds": 5.0,
            "cases": [
                case("required-a", "required"),
                case("required-b", "required"),
                case("diagnostic-a", "diagnostic"),
            ],
        }
    )


def _constraint_contract(
    *,
    coverage: tuple[tuple[str, int], ...] = (("fixture", 1),),
) -> DataDrivenContract:
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": EXPECTED_SHA,
        "size_bytes": 1,
    }
    return DataDrivenContract.model_validate(
        {
            "schema_version": 2,
            "experiment_id": "EXP-constraint-session",
            "max_attempts": 1,
            "wall_seconds": 5.0,
            "cases": [
                {
                    "case_id": "required-a",
                    "role": "required",
                    "inputs": [bound],
                    "acceptance": {
                        "mode": "constraint-satisfaction",
                        "coverage": [
                            {"fact_type": fact_type, "min_facts": minimum}
                            for fact_type, minimum in coverage
                        ],
                    },
                    "verify": {
                        "command": "check",
                        "model": {
                            **bound,
                            "path": "model.orm.yaml",
                            "sha256": "2" * 64,
                        },
                        "subject": RAW_SUBJECT,
                    },
                }
            ],
        }
    )


def _attempt(
    *results: CaseEvaluation,
    candidate_sha256: str = CANDIDATE_SHA,
) -> AttemptEvaluation:
    return AttemptEvaluation(
        attempt_index=1,
        candidate_sha256=candidate_sha256,
        contract_sha256=CONTRACT_SHA,
        results=results,
    )


def test_valid_payload_is_schema_and_digest_bound_before_acceptance() -> None:
    payload = _payload()
    raw = _raw(payload)
    evaluation = _validate(payload)

    assert evaluation.payload_valid is True
    assert evaluation.case_id == "required-a"
    assert evaluation.process_exit == evaluation.payload_exit == 0
    assert evaluation.acceptance_ready is True
    assert evaluation.candidate_sha256 == CANDIDATE_SHA
    assert evaluation.contract_sha256 == CONTRACT_SHA
    assert evaluation.raw_payload_sha256 == hashlib.sha256(raw).hexdigest()
    assert evaluation.validation_errors == ()


@pytest.mark.parametrize(
    ("mutation", "kwargs", "needle"),
    [
        pytest.param(
            lambda payload: payload.update(schema_version=PAYLOAD_SCHEMA_VERSION - 1),
            {},
            "schema_version",
            id="unsupported-version",
        ),
        pytest.param(
            lambda payload: payload.update(tool="other"),
            {},
            "tool",
            id="wrong-tool",
        ),
        pytest.param(
            lambda payload: payload.update(command="verify"),
            {"expected_command": "check"},
            "command",
            id="wrong-command",
        ),
        pytest.param(
            lambda payload: payload.update(population="prior-candidate.json"),
            {},
            "subject",
            id="wrong-subject",
        ),
        pytest.param(
            lambda payload: payload.update(model="prior-model.orm.yaml"),
            {"expected_model": "model.orm.yaml"},
            "model",
            id="wrong-model",
        ),
        pytest.param(
            lambda payload: None,
            {"process_exit": 1},
            "process exit",
            id="process-payload-exit-mismatch",
        ),
        pytest.param(
            lambda payload: payload.update(outcome="violated"),
            {},
            "outcome",
            id="exit-outcome-mismatch",
        ),
        pytest.param(
            lambda payload: payload.update(acceptance_ready=False),
            {},
            "acceptance_ready",
            id="acceptance-mismatch",
        ),
        pytest.param(
            lambda payload: payload["counts"].update({"pass": 0}),
            {},
            "counts",
            id="stale-counts",
        ),
        pytest.param(
            lambda payload: (
                payload.update(verdicts=[_verdict("fail")]),
                payload.update(
                    counts={
                        "pass": 0,
                        "fail": 1,
                        "warning": 0,
                        "unchecked": 0,
                        "vacuous": 0,
                    }
                ),
            ),
            {},
            "band",
            id="schema-valid-checker-band-contradiction",
        ),
        pytest.param(
            lambda payload: payload.update(extra=True),
            {},
            "schema",
            id="unknown-field",
        ),
        pytest.param(
            lambda payload: payload.pop("coverage"),
            {},
            "schema",
            id="missing-field",
        ),
        pytest.param(
            lambda payload: None,
            {"evidence_candidate_sha256": "9" * 64},
            "candidate",
            id="stale-candidate-binding",
        ),
        pytest.param(
            lambda payload: None,
            {"evidence_contract_sha256": "8" * 64},
            "contract",
            id="stale-contract-binding",
        ),
    ],
)
def test_every_schema_cross_field_and_binding_mutation_is_rejected(
    mutation, kwargs: dict[str, Any], needle: str
) -> None:
    payload = _payload()
    mutation(payload)

    with pytest.raises(VerifierPayloadError) as caught:
        _validate(payload, **kwargs)

    assert caught.value.issues
    assert needle in " ".join(caught.value.issues).lower()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("constraint_ref", "/private/model.orm.yaml"),
        ("constraint_type", "provider prose"),
    ],
)
def test_verdict_feedback_identifiers_reject_paths_and_prose(
    field: str,
    value: str,
) -> None:
    payload = _payload()
    payload["verdicts"][0][field] = value

    with pytest.raises(VerifierPayloadError, match="machine identifiers"):
        _validate(payload)


def test_coverage_feedback_identifier_rejects_paths() -> None:
    payload = _payload()
    payload["coverage"] = {"/private/fact": {"declared": "declared", "facts": 1}}

    with pytest.raises(VerifierPayloadError, match="machine identifiers"):
        _validate(payload)


def test_exactly_one_json_document_is_required() -> None:
    payload = _payload()
    raw = _raw(payload)
    common = {
        "case_id": "required-a",
        "role": "required",
        "process_exit": 0,
        "expected_command": "check",
        "expected_subject": RAW_SUBJECT,
        "candidate_sha256": CANDIDATE_SHA,
        "contract_sha256": CONTRACT_SHA,
        "evidence_candidate_sha256": CANDIDATE_SHA,
        "evidence_contract_sha256": CONTRACT_SHA,
    }

    for malformed in (raw + raw, raw + b"garbage", b"", b"[]\n"):
        with pytest.raises(VerifierPayloadError):
            validate_verifier_payload(malformed, **common)


def test_verify_requires_a_ran_extraction_while_check_requires_the_empty_channel() -> None:
    verify_payload = _payload(command="verify")
    assert _validate(verify_payload).acceptance_ready is True

    verify_payload["extraction"]["state"] = "skipped"
    with pytest.raises(VerifierPayloadError, match="extraction"):
        _validate(verify_payload)

    check_payload = _payload(command="check")
    check_payload["extraction"] = _payload(command="verify")["extraction"]
    with pytest.raises(VerifierPayloadError, match="schema"):
        _validate(check_payload)


def test_alethic_failure_indeterminacy_and_deontic_warning_stay_distinct() -> None:
    failed = _validate(_payload(exit_code=1, verdicts=[_verdict("fail")]))
    indeterminate = _validate(_payload(exit_code=4, verdicts=[_verdict("unchecked")]))
    warning = _validate(
        _payload(
            exit_code=0,
            verdicts=[_verdict("warning", modality="deontic")],
        )
    )

    assert failed.alethic_failure_count == 1
    assert failed.alethic_indeterminate_count == 0
    assert indeterminate.alethic_failure_count == 0
    assert indeterminate.alethic_indeterminate_count == 1
    assert warning.alethic_failure_count == 0
    assert warning.alethic_indeterminate_count == 0
    assert warning.acceptance_ready is True


def test_case_decision_records_are_closed_and_frozen() -> None:
    gap = CoverageGap(
        fact_type="fixture",
        required=2,
        observed=1,
        checker_declared=True,
    )
    decision = CaseDecision(accepted=False, raw_band=0, coverage_gaps=(gap,))

    assert decision.model_dump(mode="json") == {
        "accepted": False,
        "raw_band": 0,
        "coverage_gaps": [
            {
                "fact_type": "fixture",
                "required": 2,
                "observed": 1,
                "checker_declared": True,
            }
        ],
    }
    with pytest.raises(ValidationError, match="frozen"):
        decision.accepted = True
    with pytest.raises(ValidationError, match="extra_forbidden"):
        CaseDecision.model_validate(
            {
                "accepted": False,
                "raw_band": 0,
                "coverage_gaps": [],
                "prose": "not decision vocabulary",
            }
        )


@pytest.mark.parametrize(
    ("payload", "expected_band"),
    [
        pytest.param(_payload(), 0, id="accepted"),
        pytest.param(
            _payload(exit_code=1, verdicts=[_verdict("fail")]),
            1,
            id="violated",
        ),
        pytest.param(
            _payload(exit_code=2, verdicts=[_verdict("vacuous")]),
            2,
            id="inadequate",
        ),
        pytest.param(_payload(exit_code=3, verdicts=[]), 3, id="ill-formed"),
        pytest.param(
            _payload(exit_code=4, verdicts=[_verdict("unchecked")]),
            4,
            id="indeterminate",
        ),
    ],
)
def test_constraint_decision_preserves_every_raw_checker_band(
    payload: dict[str, Any], expected_band: int
) -> None:
    contract = _constraint_contract()
    result = _validate(payload, expected_outputs=())

    decision = case_decision(contract.cases[0], result)

    assert decision.raw_band == expected_band
    assert decision.accepted is (expected_band == 0)
    assert decision.coverage_gaps == ()


@pytest.mark.parametrize(
    ("mutation", "kwargs", "needle"),
    [
        pytest.param(
            lambda payload: payload.update(command="verify"),
            {"expected_command": "check"},
            "command",
            id="check-command",
        ),
        pytest.param(
            lambda payload: None,
            {"process_exit": 1},
            "process exit",
            id="process-exit",
        ),
        pytest.param(
            lambda payload: payload.update(outcome="violated"),
            {},
            "outcome",
            id="outcome",
        ),
        pytest.param(
            lambda payload: payload.update(acceptance_ready=False),
            {},
            "acceptance_ready",
            id="readiness",
        ),
        pytest.param(
            lambda payload: (
                payload.update(verdicts=[_verdict("fail")]),
                payload.update(
                    counts={
                        "pass": 0,
                        "fail": 1,
                        "warning": 0,
                        "unchecked": 0,
                        "vacuous": 0,
                    }
                ),
            ),
            {},
            "checker band",
            id="recomputed-band",
        ),
        pytest.param(
            lambda payload: None,
            {"evidence_candidate_sha256": "9" * 64},
            "candidate",
            id="candidate-binding",
        ),
        pytest.param(
            lambda payload: None,
            {"evidence_contract_sha256": "8" * 64},
            "contract",
            id="contract-binding",
        ),
    ],
)
def test_constraint_mode_requires_every_validated_checker_oracle_relation(
    mutation, kwargs: dict[str, Any], needle: str
) -> None:
    payload = _payload()
    mutation(payload)

    with pytest.raises(VerifierPayloadError) as caught:
        _validate(payload, expected_outputs=(), **kwargs)

    assert needle in " ".join(caught.value.issues).lower()


@pytest.mark.parametrize(
    ("coverage", "minimum", "expected_gap"),
    [
        pytest.param(
            {},
            1,
            ("fixture", 1, 0, False),
            id="missing-row-observes-zero",
        ),
        pytest.param(
            {"fixture": {"declared": "declared", "facts": 0}},
            1,
            ("fixture", 1, 0, True),
            id="declared-zero",
        ),
        pytest.param(
            {"fixture": {"declared": "undeclared", "facts": 1}},
            2,
            ("fixture", 2, 1, False),
            id="fact-count-deficient",
        ),
        pytest.param(
            {"fixture": {"declared": "declared", "facts": 2}},
            2,
            None,
            id="floor-met",
        ),
    ],
)
def test_constraint_coverage_gaps_use_only_checker_reported_fact_counts(
    coverage: dict[str, Any],
    minimum: int,
    expected_gap: tuple[str, int, int, bool] | None,
) -> None:
    payload = _payload()
    payload["coverage"] = coverage
    raw_before = _raw(payload)
    result = _validate(payload, expected_outputs=())
    case = _constraint_contract(coverage=(("fixture", minimum),)).cases[0]

    decision = case_decision(case, result)

    assert decision.raw_band == payload["exit_code"] == 0
    assert _raw(payload) == raw_before
    if expected_gap is None:
        assert decision.accepted is True
        assert decision.coverage_gaps == ()
    else:
        assert decision.accepted is False
        assert len(decision.coverage_gaps) == 1
        gap = decision.coverage_gaps[0]
        assert (gap.fact_type, gap.required, gap.observed, gap.checker_declared) == (
            expected_gap
        )


def test_constraint_coverage_gaps_are_sorted_and_run_only_after_band_zero() -> None:
    contract = _constraint_contract(coverage=(("zeta", 3), ("alpha", 2)))
    accepted_payload = _payload()
    accepted_payload["coverage"] = {
        "zeta": {"declared": "declared", "facts": 1},
        "alpha": {"declared": "declared", "facts": 0},
    }
    band_zero = case_decision(
        contract.cases[0],
        _validate(accepted_payload, expected_outputs=()),
    )
    violated = case_decision(
        contract.cases[0],
        _validate(
            _payload(exit_code=1, verdicts=[_verdict("fail")]),
            expected_outputs=(),
        ),
    )

    assert [gap.fact_type for gap in band_zero.coverage_gaps] == ["alpha", "zeta"]
    assert violated.raw_band == 1
    assert violated.accepted is False
    assert violated.coverage_gaps == ()


def test_constraint_feedback_canonicalizes_mixed_declared_coverage_gaps() -> None:
    contract = _constraint_contract(coverage=(("alpha", 2), ("zeta", 3)))
    payload = _payload()
    payload["coverage"] = {
        "alpha": {"declared": "declared", "facts": 1},
    }

    document = _feedback_document(
        contract,
        _validate(payload, expected_outputs=()),
    )

    assert document["required"][0]["acceptance"]["coverage_gaps"] == [
        {
            "fact_type": "zeta",
            "required": 3,
            "observed": 0,
            "checker_declared": False,
        },
        {
            "fact_type": "alpha",
            "required": 2,
            "observed": 1,
            "checker_declared": True,
        },
    ]


def test_contract_accepts_delegates_constraint_mode_to_the_case_decision() -> None:
    contract = _constraint_contract(coverage=(("fixture", 2),))
    payload = _payload()
    payload["coverage"]["fixture"]["facts"] = 2
    accepted = _validate(payload, expected_outputs=())
    deficient = accepted.model_copy(
        update={"coverage": {"fixture": {"declared": "declared", "facts": 1}}}
    )

    assert contract_accepts(contract, _attempt(accepted)) is True
    assert contract_accepts(contract, _attempt(deficient)) is False


def test_case_decision_keeps_the_exact_mode_output_match_conjunct() -> None:
    case = _contract().cases[0]
    matched = _validate(_payload(), case_id=case.case_id)
    differing = _validate(
        _payload(),
        case_id=case.case_id,
        expected_outputs=(_observation(case.case_id, state="differs"),),
    )

    assert case_decision(case, matched).accepted is True
    assert case_decision(case, differing).accepted is False
    assert case_decision(case, differing).raw_band == 0
    assert case_decision(case, differing).coverage_gaps == ()


def test_acceptance_uses_the_contracts_exact_required_set_not_a_result_subset() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(_payload(), case_id="required-b")
    diagnostic = _validate(
        _payload(exit_code=1, verdicts=[_verdict("fail")]),
        case_id="diagnostic-a",
        role="diagnostic",
    )

    assert contract_accepts(contract, _attempt(a, b, diagnostic)) is True
    assert contract_accepts(contract, _attempt(a)) is False
    assert contract_accepts(contract, _attempt(a, diagnostic)) is False


def test_diagnostic_success_cannot_replace_a_required_failure() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b_failed = _validate(
        _payload(exit_code=4, verdicts=[_verdict("unchecked")]),
        case_id="required-b",
    )
    diagnostic = _validate(_payload(), case_id="diagnostic-a", role="diagnostic")

    assert contract_accepts(contract, _attempt(a, b_failed, diagnostic)) is False


def test_prior_candidate_or_contract_results_cannot_enter_the_current_gate() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(_payload(), case_id="required-b")

    stale_candidate = b.model_copy(update={"candidate_sha256": "9" * 64})
    stale_contract = b.model_copy(update={"contract_sha256": "8" * 64})
    assert contract_accepts(contract, _attempt(a, stale_candidate)) is False
    assert contract_accepts(contract, _attempt(a, stale_contract)) is False


def test_a_diagnostic_role_cannot_spoof_a_required_case_id() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(_payload(), case_id="required-b")

    assert (
        contract_accepts(contract, _attempt(a, b.model_copy(update={"role": "diagnostic"})))
        is False
    )


def test_declared_expected_output_differing_bytes_is_not_accepted() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(
        _payload(),
        case_id="required-b",
        expected_outputs=(_observation("required-b", state="differs"),),
    )

    
    assert b.acceptance_ready is True
    assert b.process_exit == b.payload_exit == 0
    assert contract_accepts(contract, _attempt(a, b)) is False


def test_declared_expected_output_never_produced_is_not_accepted() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(
        _payload(),
        case_id="required-b",
        expected_outputs=(_observation("required-b", state="absent"),),
    )

    assert b.acceptance_ready is True
    assert b.expected_outputs[0].observed_sha256 is None
    assert contract_accepts(contract, _attempt(a, b)) is False


def test_agent_producing_the_contracted_output_is_accepted() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(_payload(), case_id="required-b")

    assert [entry.state for entry in b.expected_outputs] == ["matched"]
    assert contract_accepts(contract, _attempt(a, b)) is True


def test_a_result_carrying_no_observation_cannot_satisfy_a_declared_output() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    b = _validate(_payload(), case_id="required-b", expected_outputs=())

    assert b.expected_outputs == ()
    assert contract_accepts(contract, _attempt(a, b)) is False


def test_an_observation_naming_an_undeclared_output_cannot_satisfy_the_case() -> None:
    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    fabricated = _validate(
        _payload(),
        case_id="required-b",
        expected_outputs=(_observation("required-b", output_id="invented-out"),),
    )

    assert contract_accepts(contract, _attempt(a, fabricated)) is False


@pytest.mark.parametrize(
    ("states", "accepted"),
    [
        pytest.param(("matched", "matched"), True, id="both-matched"),
        pytest.param(("matched", "differs"), False, id="one-differs"),
        pytest.param(("matched", "absent"), False, id="one-absent"),
        pytest.param(("differs", "absent"), False, id="none-matched"),
    ],
)
def test_acceptance_and_ranking_agree_on_every_expected_output_fixture(
    states: tuple[str, str], accepted: bool
) -> None:
    contract = _contract()
    required = tuple(
        _validate(
            _payload(),
            case_id=case_id,
            expected_outputs=(_observation(case_id, state=state),),
        )
        for case_id, state in zip(("required-a", "required-b"), states, strict=True)
    )
    diagnostic = _validate(_payload(), case_id="diagnostic-a", role="diagnostic")
    attempt = _attempt(*required, diagnostic)
    required_count = len(contract.required_cases)

    assert contract_accepts(contract, attempt) is accepted
    assert (best_key(contract, attempt)[0] == -required_count) is accepted


def test_best_key_uses_the_contracts_declared_output_identity() -> None:


    contract = _contract()
    a = _validate(_payload(), case_id="required-a")
    fabricated = _validate(
        _payload(),
        case_id="required-b",
        expected_outputs=(_observation("required-b", output_id="invented-out"),),
    )
    attempt = _attempt(a, fabricated)

    assert [entry.state for entry in fabricated.expected_outputs] == ["matched"]
    assert contract_accepts(contract, attempt) is False
    assert best_key(contract, attempt)[0] == -1


def test_best_key_prefers_the_attempt_that_matched_every_declared_output() -> None:
    matched = AttemptEvaluation(
        attempt_index=1,
        candidate_sha256=CANDIDATE_SHA,
        contract_sha256=CONTRACT_SHA,
        results=(
            _validate(_payload(), case_id="required-a"),
            _validate(_payload(), case_id="required-b"),
        ),
    )
    unmatched = AttemptEvaluation(
        attempt_index=1,
        candidate_sha256=CANDIDATE_SHA,
        contract_sha256=CONTRACT_SHA,
        results=tuple(
            _validate(
                _payload(),
                case_id=case_id,
                expected_outputs=(_observation(case_id, state="differs"),),
            )
            for case_id in ("required-a", "required-b")
        ),
    )

    contract = _contract()
    assert best_key(contract, matched)[0] == -2
    assert best_key(contract, unmatched)[0] == 0
    assert best_key(contract, matched) < best_key(contract, unmatched)


def test_expected_output_state_changes_the_normalized_verifier_signature() -> None:
    matched = _attempt(_validate(_payload(), case_id="required-a"))
    differing = _attempt(
        _validate(
            _payload(),
            case_id="required-a",
            expected_outputs=(_observation("required-a", state="differs"),),
        )
    )

    contract = _contract()
    assert normalized_verifier_signature(contract, matched) != normalized_verifier_signature(
        contract, differing
    )


def _feedback_document(
    contract: DataDrivenContract,
    result: CaseEvaluation,
) -> dict[str, Any]:
    feedback = build_attempt_feedback(
        run_id="run-feedback-v2",
        contract=contract,
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(),
        evaluation=_attempt(result),
        disposition="retry",
    )
    encoded, _ = canonical_feedback(feedback)
    return json.loads(encoded)


def test_schema_v2_exact_feedback_is_answer_free_and_version_dispatched() -> None:
    contract = _contract()
    result = _validate(
        _payload(),
        expected_outputs=(_observation(state="differs"),),
    )

    document = _feedback_document(contract, result)
    acceptance = document["required"][0]["acceptance"]

    assert document["schema_version"] == 2
    assert acceptance == {
        "mode": "exact-bytes",
        "outputs": [{"output_id": "required-a-out", "state": "differs"}],
    }
    rendered = json.dumps(document, sort_keys=True)
    for forbidden in (
        "expected_outputs",
        "expected_sha256",
        "observed_sha256",
        "size_bytes",
        "expected/required-a.json",
        EXPECTED_SHA,
        OTHER_SHA,
    ):
        assert forbidden not in rendered

    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate({**document, "schema_version": 1})
    with pytest.raises(ValidationError):
        AttemptFeedback.model_validate({**document, "schema_version": 99})


def test_schema_v6_feedback_admits_a_snapshot_only_redacted_session() -> None:
    contract = _contract()
    result = _validate(_payload(), expected_outputs=(_observation(),))
    redaction = SessionRedaction.model_validate(
        {
            "mode": "applied",
            "declarations": [
                {
                    "case_id": "required-a",
                    "source": "role",
                    "fact_type": "optional_code",
                    "roles": ["code"],
                }
            ],
        }
    )

    feedback = build_attempt_feedback(
        run_id="run-feedback-v6",
        contract=contract,
        contract_sha256=CONTRACT_SHA,
        invocation=_invocation(),
        evaluation=_attempt(result),
        disposition="retry",
        schema_version=6,
        redaction=redaction,
    )

    assert feedback.schema_version == 6
    assert feedback.redaction == redaction
    assert feedback.required[0].case_id == "required-a"


@pytest.mark.parametrize(
    ("payload", "coverage", "expected_field", "expected_row"),
    [
        pytest.param(
            _payload(exit_code=1, verdicts=[_verdict("fail")]),
            (("fixture", 1),),
            "violations",
            {
                "constraint_ref": "constraints[0]",
                "constraint_type": "mandatory",
                "modality": "alethic",
                "reason_code": "violated",
                "message": "fixture fail",
                "offending_facts": [],
            },
            id="band-1-violation",
        ),
        pytest.param(
            {
                **_payload(exit_code=3, verdicts=[]),
                "issues": [
                    {
                        "path": "fact_types.expense_has_amount.facts[0]",
                        "message": "amount row is malformed",
                        "rule_id": "population:shape",
                        "severity": "error",
                    }
                ],
                "issues_total": 1,
            },
            (("fixture", 1),),
            "population_issues",
            {
                "path": "$.fact_types.expense_has_amount.facts[0]",
                "message": "amount row is malformed",
                "rule_id": "population:shape",
                "severity": "error",
            },
            id="band-3-population-issue",
        ),
        pytest.param(
            _payload(exit_code=2, verdicts=[_verdict("vacuous")]),
            (("fixture", 1),),
            "vacuity_findings",
            {
                "constraint_ref": "constraints[0]",
                "constraint_type": "mandatory",
                "message": "fixture vacuous",
                "offending_facts": [],
            },
            id="band-2-vacuity",
        ),
        pytest.param(
            _payload(exit_code=4, verdicts=[_verdict("unchecked")]),
            (("fixture", 1),),
            "unchecked_alethic",
            {
                "constraint_ref": "constraints[0]",
                "reason_code": "unsupported",
            },
            id="band-4-unchecked",
        ),
        pytest.param(
            _payload(),
            (("fixture", 2),),
            "coverage_gaps",
            {
                "fact_type": "fixture",
                "required": 2,
                "observed": 1,
                "checker_declared": True,
            },
            id="band-0-floor-gap",
        ),
    ],
)
def test_schema_v2_constraint_feedback_exposes_the_locked_band_specific_record(
    payload: dict[str, Any],
    coverage: tuple[tuple[str, int], ...],
    expected_field: str,
    expected_row: dict[str, Any],
) -> None:
    contract = _constraint_contract(coverage=coverage)
    result = _validate(payload, expected_outputs=())

    document = _feedback_document(contract, result)
    acceptance = document["required"][0]["acceptance"]

    assert acceptance["mode"] == "constraint-satisfaction"
    assert acceptance[expected_field] == [expected_row]
    assert set(acceptance) == {
        "mode",
        "violations",
        "population_issues",
        "vacuity_findings",
        "unchecked_alethic",
        "coverage_gaps",
    }


def test_observation_is_derived_from_the_inventory_and_never_from_the_filesystem(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    contract = _contract()
    case = contract.cases[0]
    declared = case.expected_outputs[0]
    monkeypatch.chdir(tmp_path)
    
    
    on_disk = tmp_path / declared.candidate_path
    on_disk.write_bytes(b"")
    assert observe_expected_outputs(case, {})[0].state == "absent"

    
    matched = observe_expected_outputs(case, {declared.candidate_path: declared.sha256})
    differing = observe_expected_outputs(case, {declared.candidate_path: OTHER_SHA})
    assert [entry.state for entry in matched] == ["matched"]
    assert matched[0].output_id == declared.output_id
    assert matched[0].expected_sha256 == declared.sha256
    assert [entry.state for entry in differing] == ["differs"]
    assert differing[0].observed_sha256 == OTHER_SHA
    assert "open(" not in inspect.getsource(observe_expected_outputs)


def test_observation_order_follows_the_contracts_declared_order() -> None:
    contract = _contract()
    case = contract.cases[0]
    doubled = case.model_copy(
        update={
            "expected_outputs": (
                case.expected_outputs[0],
                case.expected_outputs[0].model_copy(
                    update={"output_id": "second-out", "candidate_path": "second.json"}
                ),
            )
        }
    )

    observations = observe_expected_outputs(doubled, {"second.json": OTHER_SHA})

    assert [entry.output_id for entry in observations] == [
        case.expected_outputs[0].output_id,
        "second-out",
    ]
    assert [entry.state for entry in observations] == ["absent", "differs"]


def test_expected_output_evidence_stays_out_of_the_verifier_claim_families() -> None:
    result = _validate(_payload())

    assert "expected_outputs" in set(CaseEvaluation.model_fields)
    assert "expected_output" not in json.dumps(load_report_schema())
    assert "expected_output" not in json.dumps(result.counts)
    assert "expected_output" not in json.dumps(result.coverage)
    assert result.outcome == "accepted"
    assert result.acceptance_ready is True


def test_attempt_evaluation_refuses_duplicate_case_results() -> None:
    result = _validate(_payload())
    with pytest.raises(ValidationError, match="duplicate"):
        _attempt(result, result)


def _invocation(
    *,
    status: InvocationStatus = InvocationStatus.succeeded,
    stdout: bytes = b"agent stdout\n",
    stderr: bytes = b"agent stderr\n",
) -> InvocationResult:
    return InvocationResult(
        adapter=AgentAdapterId.codex,
        status=status,
        executable="/usr/local/bin/codex",
        version="codex fixture 1",
        argv=("codex", "exec", "<prompt:sha256=fixture>"),
        cwd="candidate",
        termination="exited",
        exit_code=0 if status == InvocationStatus.succeeded else 1,
        started_monotonic=1.0,
        ended_monotonic=2.0,
        stdout_observed_bytes=len(stdout),
        stdout_retained_bytes=len(stdout),
        stdout_truncated=False,
        stderr_observed_bytes=len(stderr),
        stderr_retained_bytes=len(stderr),
        stderr_truncated=False,
        environment=({"name": "PATH", "provenance": "inherited"},),
        stdout=stdout,
        stderr=stderr,
    )


def test_attempt_pointer_result_and_experiment_closure_are_separate_claims() -> None:
    attempt_fields = set(session_store_module.AttemptRecord.model_fields)
    result_fields = set(SessionResult.model_fields)

    assert {
        "candidate_inventory",
        "candidate_snapshot",
        "agent_stdout",
        "agent_stderr",
        "raw_verifier_payloads",
        "evaluation",
    } <= attempt_fields
    assert "candidate_inventory" not in result_fields
    assert {
        "disposition",
        "best_attempt_manifest_sha256",
        "referenced_evidence_digests",
    } <= result_fields
    assert "resolves" not in result_fields and "closed" not in result_fields


def test_store_publishes_raw_evidence_before_manifest_and_separate_pointers(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "agent.py").write_text("print('candidate')\n", encoding="utf-8")
    raw = _raw(_payload())
    contract = _contract()
    store = SessionStore(
        tmp_path / "run",
        run_id="run-1",
        contract_id=contract.experiment_id,
    )
    candidate_sha256 = store.inventory_candidate(candidate).tree_sha256
    evaluation = _attempt(
        _validate(
            _payload(),
            candidate_sha256=candidate_sha256,
            evidence_candidate_sha256=candidate_sha256,
        ),
        candidate_sha256=candidate_sha256,
    )

    order: list[str] = []
    original = artifact_module._write_new_file_at

    def recording_write(root_fd, parts, data, **kwargs) -> None:
        order.append(parts[-1])
        original(root_fd, parts, data, **kwargs)

    monkeypatch.setattr(artifact_module, "_write_new_file_at", recording_write)
    staged = store.stage_candidate(attempt_index=1, candidate_root=candidate)
    prompt_sha256 = hashlib.sha256(b"store-fixture-prompt").hexdigest()
    invocation = _invocation().model_copy(
        update={
            "argv": ("codex", "exec", f"<prompt:sha256={prompt_sha256}>"),
            "prompt_sha256": prompt_sha256,
        }
    )
    store.publish_launch_intent(
        attempt_index=1,
        contract_sha256=CONTRACT_SHA,
        policy_sha256="a" * 64,
        adapter=invocation.adapter,
        base_prompt_sha256=prompt_sha256,
        controller_prompt_sha256=prompt_sha256,
        effective_prompt_sha256=prompt_sha256,
        feedback_sha256=None,
        candidate_root=candidate,
    )
    store.publish_feedback(
        attempt_index=1,
        feedback=build_attempt_feedback(
            run_id="run-1",
            contract=contract,
            contract_sha256=CONTRACT_SHA,
            invocation=invocation,
            evaluation=evaluation,
            disposition="retry",
        ),
        staged_candidate=staged,
    )
    record = store.publish_attempt(
        attempt_index=1,
        candidate_root=candidate,
        invocation=invocation,
        verifier_payloads={"required-a": raw},
        evaluation=evaluation,
        contract=contract,
        best_eligible=True,
        staged_candidate=staged,
    )

    attempt_dir = store.attempt_path(1)
    assert order[-1] == "attempt.json", "the attempt manifest is the last staged write"
    assert (attempt_dir / "candidate" / "agent.py").is_file()
    assert (attempt_dir / "agent.stdout").read_bytes() == b"agent stdout\n"
    assert (attempt_dir / "agent.stderr").read_bytes() == b"agent stderr\n"
    assert (attempt_dir / "verifier" / "required-a.json").read_bytes() == raw
    attempt_doc = json.loads((attempt_dir / "attempt.json").read_text(encoding="utf-8"))
    assert "stdout" not in attempt_doc["invocation"]
    assert "stderr" not in attempt_doc["invocation"]

    candidate.joinpath("agent.py").write_text("mutated later\n", encoding="utf-8")
    assert (attempt_dir / "candidate" / "agent.py").read_text(encoding="utf-8") == (
        "print('candidate')\n"
    )

    best = store.publish_best(record)
    best_doc = json.loads(best.read_text(encoding="utf-8"))
    attempt_bytes = (attempt_dir / "attempt.json").read_bytes()
    assert best_doc["attempt_manifest_sha256"] == hashlib.sha256(attempt_bytes).hexdigest()
    assert best_doc["candidate_sha256"] == record.candidate_inventory.tree_sha256
    assert stat.S_ISREG(best.lstat().st_mode)

    result = SessionResult(
        run_id="run-1",
        disposition="accepted",
        terminal_reason="all required cases accepted",
        attempt_count=1,
        best_attempt=1,
        best_attempt_manifest_sha256=best_doc["attempt_manifest_sha256"],
        best_candidate_sha256=best_doc["candidate_sha256"],
        referenced_evidence_digests={
            "attempt_manifest_sha256": best_doc["attempt_manifest_sha256"]
        },
    )
    result_path = store.publish_result(result)
    assert result_path.name == "result.json"
    assert result_path != best
    assert result_path != attempt_dir / "attempt.json"

    with pytest.raises(FileExistsError):
        store.publish_attempt(
            attempt_index=1,
            candidate_root=candidate,
            invocation=_invocation(),
            verifier_payloads={"required-a": raw},
            evaluation=evaluation,
            contract=contract,
            best_eligible=True,
        )
    with pytest.raises(FileExistsError):
        store.publish_result(result)


def test_candidate_inventory_rejects_symlinks_and_nonregular_files(
    tmp_path: Path,
) -> None:
    candidate = tmp_path / "candidate"
    candidate.mkdir()
    outside = tmp_path / "outside.py"
    outside.write_text("outside\n", encoding="utf-8")
    (candidate / "linked.py").symlink_to(outside)
    store = SessionStore(tmp_path / "run", run_id="run-1")

    with pytest.raises(ValueError, match="symlink"):
        store.inventory_candidate(candidate)


def test_adapter_builders_are_closed_and_do_not_accept_an_executable() -> None:
    prompt = "repair the candidate"
    claude = build_agent_argv(AgentAdapterId.claude, prompt)
    codex = build_agent_argv(AgentAdapterId.codex, prompt)

    assert claude[0] == "claude"
    assert codex[0] == "codex"
    assert "--print" in claude
    assert "exec" in codex and "--sandbox" in codex and "workspace-write" in codex
    assert prompt == claude[-1] == codex[-1]
    with pytest.raises(ValueError):
        build_agent_argv("codex --dangerously-bypass-approvals", prompt)  


def _write_fake_cli(path: Path) -> None:
    path.write_text(
        """#!/usr/bin/env python3
import os
import pathlib
import subprocess
import sys
import time

if "--version" in sys.argv:
    print("fake-agent 1.0")
    raise SystemExit(0)

prompt = sys.argv[-1]
if prompt.startswith("flood"):
    os.write(1, b"o" * 50000)
    os.write(2, b"e" * 60000)
    raise SystemExit(0)
if prompt.startswith("descendant:"):
    marker = prompt.split(":", 1)[1]
    child = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(30)"])
    pathlib.Path(marker).write_text(str(child.pid))
    time.sleep(30)
raise SystemExit(0)
""",
        encoding="utf-8",
    )
    path.chmod(path.stat().st_mode | stat.S_IXUSR)


def test_agent_transport_caps_both_streams_and_never_records_environment_values(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = tmp_path / "codex"
    _write_fake_cli(fake)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")
    monkeypatch.setenv("GND_SECRET_SHOULD_NOT_LEAK", "super-secret-value")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt="flood",
            cwd=tmp_path,
            timeout_seconds=5.0,
            output_limit_bytes=4096,
        )
    )

    assert result.status == InvocationStatus.succeeded
    assert result.stdout_observed_bytes == 50000
    assert result.stderr_observed_bytes == 60000
    assert result.stdout_retained_bytes == result.stderr_retained_bytes == 4096
    assert result.stdout_truncated is result.stderr_truncated is True
    assert len(result.stdout) == len(result.stderr) == 4096
    evidence = json.dumps(result.model_dump(mode="json"), sort_keys=True)
    assert "super-secret-value" not in evidence
    assert "GND_SECRET_SHOULD_NOT_LEAK" not in evidence
    assert "flood" not in evidence, "the prompt is represented only by a digest"
    source = inspect.getsource(invoke_agent)
    assert "create_subprocess_exec" in source
    assert "create_subprocess_shell" not in source


@pytest.mark.skipif(os.name != "posix", reason="process-group assertion is POSIX-specific")
def test_timeout_kills_and_drains_descendants_before_returning(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fake = tmp_path / "codex"
    marker = tmp_path / "descendant.pid"
    _write_fake_cli(fake)
    monkeypatch.setenv("PATH", f"{tmp_path}{os.pathsep}{os.environ.get('PATH', '')}")

    result = asyncio.run(
        invoke_agent(
            AgentAdapterId.codex,
            prompt=f"descendant:{marker}",
            cwd=tmp_path,
            
            
            
            
            timeout_seconds=2.0,
            output_limit_bytes=4096,
            terminate_grace_seconds=0.1,
        )
    )
    asyncio.run(asyncio.sleep(0.7))

    assert result.status == InvocationStatus.timed_out
    assert result.spawned is True
    assert result.termination in {"terminated", "killed"}
    assert marker.exists(), "the timed invocation did not start its descendant"
    child_status = subprocess.run(
        ["ps", "-p", marker.read_text(), "-o", "stat="],
        capture_output=True,
        text=True,
        check=False,
    )
    assert child_status.returncode != 0 or child_status.stdout.strip().startswith("Z"), (
        "invoke_agent returned before its descendant was dead"
    )


def test_programmatic_one_attempt_controller_accepts_without_touching_closure(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import gnd.exp.session as session_module

    candidate = tmp_path / "candidate"
    candidate.mkdir()
    (candidate / "agent.py").write_text("print('candidate')\n", encoding="utf-8")
    
    
    produced = {}
    for case_id in ("required-a", "required-b", "diagnostic-a"):
        data = f'{{"case":"{case_id}"}}\n'.encode()
        (candidate / f"{case_id}.json").write_bytes(data)
        produced[case_id] = hashlib.sha256(data).hexdigest()
    contract = _contract(output_digests=produced)
    experiment = tmp_path / "EXP-001-session"
    experiment.mkdir()
    conclusions = experiment / "CONCLUSIONS.md"
    conclusions.write_text("untouched closure evidence\n", encoding="utf-8")

    async def fake_invoke(*args, **kwargs) -> InvocationResult:
        prompt = kwargs["prompt"]
        feedback_sha256 = kwargs["feedback_sha256"]
        effective_prompt = prompt
        if feedback_sha256 is not None:
            effective_prompt = (
                f"{prompt}\n\nCurrent attempt feedback SHA-256: {feedback_sha256}\n"
                "Canonical current-attempt feedback is supplied byte-for-byte on stdin."
            )
        effective_sha256 = hashlib.sha256(effective_prompt.encode("utf-8")).hexdigest()
        return _invocation().model_copy(
            update={
                "argv": (
                    *build_agent_argv(AgentAdapterId.codex, effective_prompt)[:-1],
                    f"<prompt:sha256={effective_sha256}>",
                ),
                "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
                "feedback_sha256": feedback_sha256,
            }
        )

    async def fake_verify(case, snapshot: Path) -> tuple[int, bytes]:
        assert snapshot != candidate
        assert snapshot.joinpath("agent.py").is_file()
        return 0, _raw(_payload(subject=case.verify.subject))

    monkeypatch.setattr(session_module, "invoke_agent", fake_invoke)
    result = asyncio.run(
        run_session(
            contract,
            contract_sha256=CONTRACT_SHA,
            adapter_id=AgentAdapterId.codex,
            prompt="trusted caller prompt",
            candidate_root=candidate,
            run_root=experiment / "runs" / "run-1",
            verifier=fake_verify,
        )
    )

    assert result.disposition == "accepted"
    assert result.attempt_count == 1
    assert (experiment / "runs" / "run-1" / "attempts" / "0001" / "attempt.json").is_file()
    assert (experiment / "runs" / "run-1" / "best.json").is_file()
    assert (experiment / "runs" / "run-1" / "result.json").is_file()
    assert conclusions.read_text(encoding="utf-8") == "untouched closure evidence\n"
