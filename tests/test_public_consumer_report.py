"""Public report routing and pure synthetic prototype projection controls."""
from __future__ import annotations

from pathlib import Path

import pytest

from gnd.semantic_registry import REGISTRY, capture_branches


def test_report_routes_describe_the_fields_actually_published():
    import test_v6_phase1_production as phase1

    from gnd.checker import band, check
    from gnd.model import load_model
    from gnd.population import load_population
    from gnd.report import build_check_payload, build_transition_payload
    from gnd.transition import TransitionReport

    root = Path(__file__).parent / "fixtures"
    assurance_owned = {
        row.scope_id for row in REGISTRY if row.surface == "report" and row.family == "assurance"
    }
    assert assurance_owned == {
        f"report:assurance:{surface}:projected"
        for surface in ("snapshot", "transition", "derivation")
    }
    required = {
        row.scope_id for row in REGISTRY if row.surface == "report" and row.family != "assurance"
    }
    with capture_branches() as reached:
        with capture_branches() as phase1_route:
            payload = phase1._public(phase1.IN_SCOPE_IDS[0])
        assert payload["counts"] == phase1.EXPECTED[phase1.IN_SCOPE_IDS[0]]["counts"]
        assert "report:check:phase1:counts" in phase1_route
        assert "report:check:n-a:counts" not in phase1_route
        model_path = root / "checker/misc.orm.yaml"
        population_path = root / "checker/population.misc_pass.yaml"
        model = load_model(model_path)
        report = check(model, load_population(population_path, model=model))
        assert report.phase1_trace is None
        payload = build_check_payload(
            band(report), str(model_path), str(population_path), report=report
        )
        assert payload["counts"] == report.counts()
        assert len(payload["verdicts"]) == len(report.verdicts)
        assert payload["coverage"] == report.model_dump()["coverage"]
        directory = root / "derivation-evaluation/cases/obligation-opaque-mixed-listed"
        model = load_model(directory / "model.orm.yaml")
        report = check(model, load_population(directory / "population.yaml", model=model))
        assert report.derivations
        with pytest.raises(ValueError, match="cannot hide derivation obligations"):
            build_check_payload(band(report), "model", "population", report=report)
        payload = build_check_payload(
            band(report), "model", "population", report=report, schema_version=4
        )
        assert len(payload["derivations"]) == len(report.derivations)
        assert all(
            "scope_id" not in row and "fact_type" not in row for row in payload["derivations"]
        )
        payload = build_transition_payload(3, "model", evaluated=False)
        assert payload["transition"]["evaluated"] is False
        assert payload["transition"]["steps"] is None
        payload = build_transition_payload(
            0, "model", evaluated=True, transition_report=TransitionReport()
        )
        assert payload["transition"]["evaluated"] is True
        assert payload["transition"]["steps"] == []
        from gnd.redaction import RedactionPolicy, _project_transition

        exact_model = load_model(root / "v62-phase3/models/exact-terms.orm.yaml")
        _project_transition(
            {
                "steps": [
                    {
                        "operation": "approve",
                        "bindings": {},
                        "verdicts": [],
                        "derived_changes": [
                            {
                                "fact_type": "ticket_status",
                                "added": [{"ticket": "SECRET", "status": "approved"}],
                                "removed": [],
                            }
                        ],
                    }
                ]
            },
            RedactionPolicy.from_model(exact_model),
        )
    assert required <= reached, sorted(required - reached)

def test_certification_trace_matches_the_prototype_projection():
    from gnd.assurance import CorrespondenceDigests, ValidatedScopeWalk, certify_snapshot
    from gnd.correspondence import SnapshotDecision
    from gnd.proof_bridge import project_phase1_result

    assurance_owned = {
        row.scope_id
        for row in REGISTRY
        if row.surface == "certification" and row.family == "assurance" and row.variant != "phase1"
    }
    assert assurance_owned == {
        f"certification:assurance:{surface}:{level}"
        for surface in ("snapshot", "transition", "derivation")
        for level in ("none", "partial", "proof-backed")
    }
    required = {
        row.scope_id
        for row in REGISTRY
        if row.surface == "certification"
        and not (row.family == "assurance" and row.variant != "phase1")
    }
    digests = CorrespondenceDigests(*(f"{index:064x}" for index in range(5)))
    with capture_branches() as reached:
        for band, current, decision, assurance in (
            (0, 0, "accept", "none"),
            (1, 1, "refuse", "partial"),
            (4, 2, "indeterminate", "proof-backed"),
        ):
            projected = project_phase1_result(
                (), band=band, coverage=(), applicable=2, current=current, in_scope=True
            )
            certified = certify_snapshot(
                SnapshotDecision((), band, band == 0, decision),
                scope=ValidatedScopeWalk(
                    ("scope-a", "scope-b"),
                    ("scope-a", "scope-b")[:current],
                    digests,
                    (),
                    True,
                    True,
                ),
                extraction_route="authenticated",
            )
            assert projected["phase1_assurance"]["semantic_decision"] == certified.semantic_decision
            assert projected["phase1_assurance"]["assurance_level"] == certified.assurance_level
            assert certified.semantic_decision == decision
            assert certified.assurance_level == assurance
    assert required <= reached, sorted(required - reached)
