"""Correspondence decision and refusal controls on reviewed generic inputs.
Synthetic digest/trust structures exercise policy functions only; these tests
neither renew certification nor assert assurance for any installed evidence.
"""
from __future__ import annotations

from pathlib import Path

import pytest
from test_public_branch_runtime import _build

from gnd import checker as checker_module
from gnd import correspondence as correspondence_module
from gnd import semantic_spec
from gnd.assurance import (
    PHASE2_TRUST_ASSUMPTIONS,
    CorrespondenceDigests,
    CorrespondenceEvidence,
    certify_snapshot,
    phase3_scope_ids,
    walk_snapshot_scope,
)
from gnd.checker import band, check
from gnd.correspondence import correspond_snapshot
from gnd.semantic_adapter import PRODUCTION_DIMENSIONS


def test_observation_carries_the_closed_production_dimension_vocabulary(tmp_path: Path) -> None:
    model, population = _build("P2-001", tmp_path)
    adapted, _decision = correspond_snapshot(model, population)
    assert adapted.observation.production_dimensions == PRODUCTION_DIMENSIONS
    assert len(PRODUCTION_DIMENSIONS) == 14
    assert len(set(PRODUCTION_DIMENSIONS)) == 14


@pytest.mark.parametrize("phase2_case_id", ["P2-001", "P2-002", "P2-003"])
def test_indexed_inline_uniqueness_matches_the_proved_specification(
    phase2_case_id: str, tmp_path: Path
) -> None:
    """The scalable correspondence path preserves clean/fail/warning and witness order."""
    model, population = _build(phase2_case_id, tmp_path)
    adapted, decision = correspond_snapshot(model, population)
    constraint = next(
        row
        for row in adapted.snapshot.constraints
        if row.family == "uniqueness" and row.variant == "inline"
    )
    finding = next(row for row in decision.findings if row.constraint_id == constraint.ref)
    assert (finding.verdict, finding.reason_code, finding.witness) == semantic_spec.verdict_of(
        constraint,
        adapted.snapshot,
    )


@pytest.mark.parametrize(
    ("phase2_case_id", "constraint_ref", "expected_verdict", "expected_witness"),
    [
        (
            "P2-058",
            "fact_types[rel_acyclic].constraints[0]",
            "fail",
            [[1, 2, 3, 1]],
        ),
        (
            "P2-059",
            "fact_types[rel_acyclic].constraints[0]",
            "warning",
            [[1, 2, 3, 1]],
        ),
        ("P2-084", "fact_types[rel_reflexive].constraints[0]", "pass", []),
        ("P2-144", "constraints[1]", "fail", [[30], [3], [20]]),
        ("P2-145", "constraints[1]", "warning", [[30], [3], [20]]),
    ],
)
def test_approved_authority_deltas_reach_check(
    phase2_case_id: str,
    constraint_ref: str,
    expected_verdict: str,
    expected_witness: list[object],
    tmp_path: Path,
) -> None:
    model, population = _build(phase2_case_id, tmp_path)
    report = check(model, population)
    verdict = next(row for row in report.verdicts if row.constraint_ref == constraint_ref)
    assert verdict.verdict == expected_verdict
    assert verdict.offending_facts == expected_witness
    assert report.snapshot_projection is not None
    assert band(report) == report.snapshot_projection.band


def test_certification_cannot_upgrade_stale_or_skipped_evidence(tmp_path: Path) -> None:
    model, population = _build("P2-001", tmp_path)
    adapted, decision = correspond_snapshot(model, population)
    declared = phase3_scope_ids()
    current = CorrespondenceDigests(*(f"{index:064x}" for index in range(1, 6)))
    fresh_scope = walk_snapshot_scope(
        adapted,
        decision,
        CorrespondenceEvidence._from_authenticated(
            declared,
            declared,
            current,
            PHASE2_TRUST_ASSUMPTIONS,
        ),
    )
    assert (
        certify_snapshot(decision, scope=fresh_scope, extraction_route="skipped").assurance_level
        == "none"
    )
    assert (
        certify_snapshot(
            decision, scope=fresh_scope, extraction_route="authenticated"
        ).assurance_level
        == "proof-backed"
    )


def test_missing_trust_assumptions_and_uncovered_rows_cannot_upgrade(tmp_path: Path) -> None:
    model, population = _build("P2-001", tmp_path)
    adapted, decision = correspond_snapshot(model, population)
    declared = phase3_scope_ids()
    digests = CorrespondenceDigests(*(f"{index:064x}" for index in range(1, 6)))
    missing_assumption = walk_snapshot_scope(
        adapted,
        decision,
        CorrespondenceEvidence._from_authenticated(declared, declared, digests, ()),
    )
    assert not missing_assumption.currency_valid
    assert (
        certify_snapshot(
            decision, scope=missing_assumption, extraction_route="authenticated"
        ).assurance_level
        == "none"
    )

    applicable = set(adapted.observation.applicable_scope_ids) & set(declared)
    covered = tuple(scope_id for scope_id in declared if scope_id in applicable)
    partial = walk_snapshot_scope(
        adapted,
        decision,
        CorrespondenceEvidence._from_authenticated(
            covered[:-1],
            declared,
            digests,
            PHASE2_TRUST_ASSUMPTIONS,
        ),
    )
    assert (
        certify_snapshot(decision, scope=partial, extraction_route="authenticated").assurance_level
        == "partial"
    )


def test_retired_snapshot_decision_sites_are_absent() -> None:
    retired = {
        "_phase1_verdict_or_none",
        "_verdict_for",
        "_evaluate",
        "_check_uniqueness",
        "_check_mandatory",
        "_check_frequency",
        "_check_ring",
        "_check_guarded",
        "_check_value_comparison",
        "_check_subtype_partition",
        "_check_cardinality",
    }
    assert not {name for name in retired if hasattr(checker_module, name)}


def test_check_delegates_semantic_outcomes_to_correspondence(monkeypatch, tmp_path: Path) -> None:
    model, population = _build("P2-002", tmp_path)
    baseline = check(model, population)
    assert any(row.verdict == "fail" for row in baseline.verdicts)
    from test_measure_negative_control import _ALWAYS_PASS

    monkeypatch.setattr(correspondence_module, "evaluate_snapshot", _ALWAYS_PASS)
    report = check(model, population)
    assert not any(row.verdict == "fail" for row in report.verdicts)
    assert band(report) != 1


def test_message_rendering_cannot_rewrite_semantic_fields(monkeypatch, tmp_path: Path) -> None:
    model, population = _build("P2-002", tmp_path)
    baseline = check(model, population)
    monkeypatch.setattr(
        checker_module,
        "_correspondence_message",
        lambda *_args, **_kwargs: "presentation-only mutation",
    )
    mutated = check(model, population)
    assert [row.message for row in mutated.verdicts] == ["presentation-only mutation"] * len(
        mutated.verdicts
    )

    def semantic_fields(row):
        values = row.model_dump()
        values.pop("message")
        return values

    assert [semantic_fields(row) for row in baseline.verdicts] == [
        semantic_fields(row) for row in mutated.verdicts
    ]
    assert band(mutated) == band(baseline)

