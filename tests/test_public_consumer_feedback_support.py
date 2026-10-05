"""Exact synthetic session consumer fixtures; no provider invocation."""
from __future__ import annotations

import json
from typing import Any

from gnd.agent_cli import AgentAdapterId, InvocationResult, InvocationStatus
from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import (
    AttemptEvaluation,
    CaseEvaluation,
    ExpectedOutputObservation,
    validate_verifier_payload,
)
from gnd.report import PAYLOAD_SCHEMA_VERSION

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
        # Phase 2 (v2.0) made this key required on every payload: a
        # verifier that is not auditing a walk says so with null, so a
        # consumer never has to infer "not a transition run".
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
    """One expected-output observation for the case ids `_contract` declares."""

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
    """The fixture contract; `output_digests` declares real expected bytes.

    Each case declares one expected output at candidate-relative
    ``{case_id}.json``.  Tests that drive a real candidate tree pass the
    digests those bytes actually hash to; unit tests keep the placeholder.
    """

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
