"""Live feedback projection controls with synthetic unit-test evidence."""
import pytest
from test_public_assurance_feedback import live_execution


@pytest.mark.parametrize("surface", ["snapshot", "derivation", "transition"])
def test_live_feedback_requires_its_own_projection_for_every_surface(monkeypatch, surface):
    from test_v6_phase6_execution import synthetic_evidence

    from gnd import assurance, assurance_evidence
    from gnd.exp.session_eval import project_assurance_feedback
    from gnd.semantic_registry import capture_branches

    execution = live_execution(surface)
    assert execution.complete and execution.surface == surface
    scope = assurance.derive_assurance_scope(execution, consumer="feedback")
    assert scope.valid
    evidence = synthetic_evidence(scope)
    monkeypatch.setattr(assurance_evidence, "load_assurance_evidence", lambda: evidence)
    with capture_branches() as trace:
        backed = project_assurance_feedback(execution)
    assert backed.assurance_level == "proof-backed"
    assert f"experiment-feedback:assurance:{surface}:projected" in trace
    evidence = synthetic_evidence(
        scope, omit=[f"experiment-feedback:assurance:{surface}:projected"]
    )
    withheld = project_assurance_feedback(execution)
    assert withheld.assurance_level == "none"
    assert withheld.semantic_decision == backed.semantic_decision
    report_scope = assurance.derive_assurance_scope(execution, consumer="report")
    assert (
        assurance.certify_result(execution, scope=report_scope, evidence=evidence).assurance_level
        == "proof-backed"
    )
