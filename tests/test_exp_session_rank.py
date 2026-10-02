

from __future__ import annotations

import itertools

from gnd.exp.session_contract import DataDrivenContract
from gnd.exp.session_eval import (
    AttemptEvaluation,
    CaseEvaluation,
    ExpectedOutputObservation,
    best_key,
)

CONTRACT_SHA = "c" * 64
EXPECTED_SHA = "1" * 64


def _case(
    case_id: str,
    *,
    candidate: str,
    accepted: bool = False,
    failures: int = 0,
    indeterminate: int = 0,
    role: str = "required",
) -> CaseEvaluation:
    exit_code = 0 if accepted else (1 if failures else 4 if indeterminate else 3)
    outcome = {0: "accepted", 1: "violated", 3: "ill_formed", 4: "indeterminate"}[
        exit_code
    ]
    return CaseEvaluation(
        payload_valid=True,
        case_id=case_id,
        role=role,
        candidate_sha256=candidate,
        contract_sha256=CONTRACT_SHA,
        raw_payload_sha256=(case_id[0].lower() if case_id[0].isalpha() else "f") * 64,
        process_exit=exit_code,
        payload_exit=exit_code,
        outcome=outcome,
        acceptance_ready=accepted,
        counts={
            "pass": int(accepted),
            "fail": failures,
            "warning": 0,
            "unchecked": indeterminate,
            "vacuous": 0,
        },
        coverage={},
        issues=(),
                                                                             
                                                                             
                                    
        expected_outputs=(
            ExpectedOutputObservation(
                output_id=f"{case_id}-out",
                expected_sha256=EXPECTED_SHA,
                observed_sha256=EXPECTED_SHA if accepted else None,
                state="matched" if accepted else "absent",
            ),
        ),
        alethic_failure_count=failures,
        alethic_indeterminate_count=indeterminate,
    )


def _attempt(index: int, candidate: str, *cases: CaseEvaluation) -> AttemptEvaluation:
    return AttemptEvaluation(
        attempt_index=index,
        candidate_sha256=candidate,
        contract_sha256=CONTRACT_SHA,
        results=cases,
    )


def _exact_contract(*attempts: AttemptEvaluation) -> DataDrivenContract:
    bound = {
        "path": "input.json",
        "media_type": "application/json",
        "encoding": "utf-8",
        "sha256": EXPECTED_SHA,
        "size_bytes": 1,
    }
    cases: dict[str, CaseEvaluation] = {}
    for attempt in attempts:
        for result in attempt.results:
            cases.setdefault(result.case_id, result)
    return DataDrivenContract.model_validate(
        {
            "schema_version": 2,
            "experiment_id": "EXP-rank-exact",
            "max_attempts": 10,
            "cases": [
                {
                    "case_id": case_id,
                    "role": result.role,
                    "inputs": [bound],
                    "acceptance": {
                        "mode": "exact-bytes",
                        "expected_outputs": [
                            {
                                **bound,
                                "path": f"expected/{case_id}.json",
                                "output_id": f"{case_id}-out",
                                "candidate_path": f"{case_id}.json",
                                "comparison": "exact-bytes",
                            }
                        ],
                    },
                    "verify": {
                        "command": "check",
                        "model": {**bound, "path": "model.orm.yaml"},
                        "subject": "candidate.json",
                    },
                }
                for case_id, result in sorted(cases.items())
            ],
        }
    )


def _constraint_contract(*case_ids: str, minimum: int = 1) -> DataDrivenContract:
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
            "experiment_id": "EXP-rank-constraint",
            "max_attempts": 10,
            "cases": [
                {
                    "case_id": case_id,
                    "role": "required",
                    "inputs": [bound],
                    "acceptance": {
                        "mode": "constraint-satisfaction",
                        "coverage": [{"fact_type": "fact", "min_facts": minimum}],
                    },
                    "verify": {
                        "command": "check",
                        "model": {**bound, "path": "model.orm.yaml"},
                        "subject": "candidate.json",
                    },
                }
                for case_id in case_ids
            ],
        }
    )


def _constraint_case(
    case_id: str,
    *,
    candidate: str,
    band: int,
    facts: int = 1,
    role: str = "required",
) -> CaseEvaluation:
    outcome = {0: "accepted", 1: "violated", 2: "inadequate", 3: "ill_formed", 4: "indeterminate"}[band]
    return CaseEvaluation(
        payload_valid=True,
        case_id=case_id,
        role=role,
        candidate_sha256=candidate,
        contract_sha256=CONTRACT_SHA,
        raw_payload_sha256="d" * 64,
        process_exit=band,
        payload_exit=band,
        outcome=outcome,
        acceptance_ready=band == 0,
        counts={
            "pass": int(band == 0),
            "fail": int(band == 1),
            "warning": 0,
            "unchecked": int(band == 4),
            "vacuous": int(band == 2),
        },
        coverage=(
            {"fact": {"declared": "declared", "facts": facts}} if band == 0 else {}
        ),
        issues=(),
        expected_outputs=(),
        alethic_failure_count=int(band == 1),
        alethic_indeterminate_count=int(band == 4),
    )


def test_best_prefers_more_accepted_required_cases_before_other_criteria() -> None:
    candidate_a = "a" * 64
    candidate_b = "b" * 64
    one_accepted = _attempt(
        1,
        candidate_a,
        _case("a", candidate=candidate_a, accepted=True),
        _case("b", candidate=candidate_a, failures=0),
    )
    two_accepted_with_diagnostic_failure = _attempt(
        2,
        candidate_b,
        _case("a", candidate=candidate_b, accepted=True),
        _case("b", candidate=candidate_b, accepted=True),
        _case("diagnostic", candidate=candidate_b, failures=99, role="diagnostic"),
    )

    contract = _exact_contract(one_accepted, two_accepted_with_diagnostic_failure)
    assert best_key(contract, two_accepted_with_diagnostic_failure) < best_key(
        contract, one_accepted
    )


def test_best_then_prefers_fewer_required_alethic_failures_then_indeterminate() -> None:
    candidate = "a" * 64
    failed = _attempt(1, candidate, _case("a", candidate=candidate, failures=1))
    indeterminate = _attempt(
        2, candidate, _case("a", candidate=candidate, indeterminate=1)
    )
    ill_formed = _attempt(3, candidate, _case("a", candidate=candidate))

    contract = _exact_contract(failed, indeterminate, ill_formed)
    assert best_key(contract, ill_formed) < best_key(contract, indeterminate) < best_key(
        contract, failed
    )


def test_equal_rank_uses_earliest_attempt_without_replacing_evidence_identity() -> None:
    candidate_a = "a" * 64
    candidate_b = "b" * 64
    first = _attempt(1, candidate_a, _case("a", candidate=candidate_a, failures=1))
    later = _attempt(9, candidate_b, _case("a", candidate=candidate_b, failures=1))

    contract = _exact_contract(first, later)
    assert best_key(contract, first) < best_key(contract, later)
    assert min((later, first), key=lambda attempt: best_key(contract, attempt)) is first


def test_session_same_score_different_candidate_is_stably_ranked_not_conflated() -> None:


    candidate_a = "a" * 64
    candidate_b = "b" * 64
    first = _attempt(4, candidate_a, _case("a", candidate=candidate_a, failures=1))
    second = _attempt(5, candidate_b, _case("a", candidate=candidate_b, failures=1))

    contract = _exact_contract(first, second)
    assert best_key(contract, first) != best_key(contract, second)
    assert min(
        (first, second), key=lambda attempt: best_key(contract, attempt)
    ).candidate_sha256 == candidate_a


def test_best_key_is_independent_of_case_construction_order() -> None:
    candidate = "a" * 64
    cases = (
        _case("a", candidate=candidate, accepted=True),
        _case("b", candidate=candidate, failures=2),
        _case("c", candidate=candidate, indeterminate=3),
    )
    attempts = tuple(
        _attempt(7, candidate, *permutation) for permutation in itertools.permutations(cases)
    )
    contract = _exact_contract(*attempts)
    keys = {best_key(contract, attempt) for attempt in attempts}

    assert keys == {(-1, 2, 3, 7)}


def test_constraint_key_uses_locked_band_precedence_and_attempt_tie_breaker() -> None:
    candidate = "a" * 64
    contract = _constraint_contract("required-a")
    attempts = {
        band: _attempt(
            band,
            candidate,
            _constraint_case("required-a", candidate=candidate, band=band),
        )
        for band in (1, 2, 3, 4)
    }

    assert best_key(contract, attempts[2]) < best_key(contract, attempts[4])
    assert best_key(contract, attempts[4]) < best_key(contract, attempts[1])
    assert best_key(contract, attempts[1]) < best_key(contract, attempts[3])
    assert best_key(contract, attempts[3]) == (0, 1, 0, 0, 0, 0, 3)


def test_constraint_key_counts_acceptance_then_floor_shortfall_and_excludes_diagnostics() -> None:
    candidate = "a" * 64
    contract = _constraint_contract("required-a", minimum=3)
    deficient = _attempt(
        2,
        candidate,
        _constraint_case("required-a", candidate=candidate, band=0, facts=1),
        _constraint_case(
            "diagnostic", candidate=candidate, band=3, role="diagnostic"
        ),
    )
    covered = _attempt(
        9,
        candidate,
        _constraint_case("required-a", candidate=candidate, band=0, facts=3),
    )

    assert best_key(contract, deficient) == (0, 0, 0, 0, 0, 2, 2)
    assert best_key(contract, covered) == (-1, 0, 0, 0, 0, 0, 9)
    assert best_key(contract, covered) < best_key(contract, deficient)


def test_constraint_key_is_invariant_to_result_construction_order() -> None:
    candidate = "a" * 64
    contract = _constraint_contract("a", "b", "c", minimum=2)
    cases = (
        _constraint_case("a", candidate=candidate, band=3),
        _constraint_case("b", candidate=candidate, band=1),
        _constraint_case("c", candidate=candidate, band=0, facts=1),
    )

    keys = {
        best_key(contract, _attempt(5, candidate, *permutation))
        for permutation in itertools.permutations(cases)
    }

    assert keys == {(0, 1, 1, 0, 0, 1, 5)}
