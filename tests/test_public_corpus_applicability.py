"""Exact seven original execution capability mutation guards."""
import test_public_corpus_applicability_support as corpus_observer
from test_public_corpus_applicability_support import ANSWERS, ROWS


def test_every_applicability_control_is_rejected_by_the_live_policy():
    from gnd import assurance, assurance_evidence

    rows = [row for row in ROWS if row["kind"] == "applicability"]
    case = corpus_observer.narratives()[rows[0]["recipe"]["narrative_id"]]
    execution = corpus_observer.live_execution(case)
    scope = assurance.derive_assurance_scope(execution, consumer="report")
    evidence = assurance_evidence._capability(
        manifest={
            "rows": [
                {"scope_id": key, "status": "proved"}
                for key in sorted(scope.applicable_scope_ids | scope.required_infrastructure_ids)
            ],
            "scope_digest": "a" * 64,
            "semantics_digest": "b" * 64,
            "production_roster_digest": scope.production_roster_digest,
            "proof_digest": "c" * 64,
            "toolchain_digest": "d" * 64,
            "assumptions": [],
        }
    )
    for row in rows:
        assert corpus_observer.applicability(row, execution, evidence) == ANSWERS[row["case_id"]]
