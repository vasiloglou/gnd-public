"""Live execution binding and policy, with explicitly synthetic evidence fixtures."""

from pathlib import Path

import pytest

from gnd import assurance, checker, report
from gnd.assurance_evidence import _capability
from gnd.model import load_model
from gnd.population import load_population
from gnd.semantic_registry import capture_branches

ROOT = Path(__file__).resolve().parents[1]


def execution(case="conforming", omit_trace=False):
    root = ROOT / "tests/fixtures/v6-assurance/cases/expense-approval" / case
    model = load_model(root.parent / "conforming/model.orm.yaml")
    population = load_population(root / "population.json", model=model)
    with capture_branches() as trace:
        result = checker.check(model, population)
        band = checker.band(result)
        report.build_check_payload(band, "model.orm.yaml", "population.json", report=result)
    return assurance._mint_execution(model, [population], result, band, () if omit_trace else trace)


def synthetic_evidence(scope, *, omit=(), coverage=None):
    covered = scope.applicable_scope_ids if coverage is None else frozenset(coverage)
    covered = (covered | scope.required_infrastructure_ids) - set(omit)
    return _capability(
        manifest={
            "rows": [{"scope_id": key, "status": "proved"} for key in sorted(covered)],
            **{
                name: "a" * 64
                for name in (
                    "scope_digest",
                    "semantics_digest",
                    "production_roster_digest",
                    "proof_digest",
                    "toolchain_digest",
                )
            },
            "production_roster_digest": scope.production_roster_digest,
            "assumptions": ["synthetic-unit-test-evidence"],
        }
    )


@pytest.mark.parametrize("case,decision", [("conforming", "accept"), ("violating", "refuse")])
def test_fully_covered_actual_result_is_independent_of_acceptance(case, decision):
    run = execution(case)
    scope = assurance.derive_assurance_scope(run, consumer="report")
    assert scope.valid
    result = assurance.certify_result(run, scope=scope, evidence=synthetic_evidence(scope))
    assert result.semantic_decision == decision and result.assurance_level == "proof-backed"
    assert result.uncovered_applicable_scope_ids == ()


def test_scope_contains_opposite_outcomes_not_only_executed_branches():
    run = execution()
    scope = assurance.derive_assurance_scope(run, consumer="report")
    opposite = "snapshot:mandatory:phase1-inline:violated:alethic"
    assert opposite not in run.trace and opposite in scope.applicable_scope_ids
    result = assurance.certify_result(
        run, scope=scope, evidence=synthetic_evidence(scope, omit=[opposite])
    )
    assert result.assurance_level == "partial"
    assert result.uncovered_applicable_scope_ids == (opposite,)


@pytest.mark.parametrize("level", ["none", "partial", "proof-backed"])
def test_even_unexecuted_certification_outcome_is_a_prerequisite(level):
    run = execution()
    scope = assurance.derive_assurance_scope(run, consumer="report")
    result = assurance.certify_result(
        run,
        scope=scope,
        evidence=synthetic_evidence(scope, omit=[f"certification:assurance:snapshot:{level}"]),
    )
    assert result.assurance_level == "none"


def test_incomplete_trace_cannot_be_certified():
    run = execution(omit_trace=True)
    scope = assurance.derive_assurance_scope(run, consumer="report")
    assert not scope.valid
    assert (
        assurance.certify_result(
            run, scope=scope, evidence=synthetic_evidence(scope)
        ).assurance_level
        == "none"
    )


def test_scope_from_another_actual_result_cannot_be_reused():
    first, second = execution(), execution("violating")
    scope = assurance.derive_assurance_scope(first, consumer="report")
    assert (
        assurance.certify_result(
            second, scope=scope, evidence=synthetic_evidence(scope)
        ).assurance_level
        == "none"
    )


def test_plain_json_is_not_an_execution_scope_or_evidence_capability():
    with pytest.raises(TypeError):
        assurance.AuthenticatedExecution(complete=True)
    with pytest.raises(TypeError):
        assurance.AssuranceScope(valid=True)
    with pytest.raises(TypeError):
        assurance.derive_assurance_scope({"complete": True}, consumer="report")
    run = execution()
    scope = assurance.derive_assurance_scope(run, consumer="report")
    with pytest.raises(TypeError):
        assurance.certify_result(run, scope=scope, evidence={"available": True})


def test_a_registered_but_unexplained_consumer_event_invalidates_scope():
    from dataclasses import asdict

    run = execution()
    fields = asdict(run)
    fields["trace"] = run.trace | {"experiment-feedback:attempt:n-a:built"}
    mutated = assurance._internal_value(assurance.AuthenticatedExecution, **fields)
    scope = assurance.derive_assurance_scope(mutated, consumer="report")
    assert not scope.valid
    assert (
        assurance.certify_result(
            mutated, scope=scope, evidence=synthetic_evidence(scope)
        ).assurance_level
        == "none"
    )


def test_unreadable_producer_identity_withholds_evidence_but_preserves_scope(monkeypatch):
    from gnd import assurance_evidence

    def unavailable():
        raise OSError("source unavailable")

    monkeypatch.setattr(assurance_evidence, "production_identity", unavailable)
    run = execution()
    scope = assurance.derive_assurance_scope(run, consumer="report")
    block = assurance.certify_result(run, scope=scope, evidence=assurance_evidence._capability())
    assert run.band == 0 and block.semantic_decision == "accept"
    assert block.assurance_level == "none" and block.uncovered_applicable_scope_ids
