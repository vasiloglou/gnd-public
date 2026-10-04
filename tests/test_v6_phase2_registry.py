

import importlib

import pytest


@pytest.fixture
def registry():
    return importlib.import_module("gnd.semantic_registry")


def test_unknown_branch_cannot_be_constructed(registry):
    from gnd.checker import ConstraintVerdict

    with pytest.raises(registry.UnregisteredBranchError):
        ConstraintVerdict(
            scope_id="snapshot:invented:n-a:clean",
            constraint_ref="constraints[0]",
            constraint_type="mandatory",
            modality="alethic",
            source="explicit",
            status="confirmed",
            verdict="pass",
            message="test",
        )


def test_registered_id_cannot_describe_a_different_outcome(registry):
    from gnd.checker import ConstraintVerdict

    with pytest.raises(registry.UnregisteredBranchError):
        ConstraintVerdict(
            scope_id="snapshot:mandatory:inline:clean",
            constraint_ref="constraints[0]",
            constraint_type="mandatory",
            modality="alethic",
            source="explicit",
            status="confirmed",
            verdict="fail",
            message="test",
        )


def test_all_required_surfaces_have_owned_rows(registry):
    surfaces = {row.surface for row in registry.REGISTRY}
    assert surfaces == {
        "snapshot",
        "transition",
        "derivation",
        "applicability",
        "composition",
        "report",
        "experiment-feedback",
        "certification",
    }
    assert all(row.production_owner.startswith("gnd.") for row in registry.REGISTRY)
    assert len(registry.REGISTRY) == len({row.scope_id for row in registry.REGISTRY})


def test_every_production_owner_names_an_actual_callable(registry):
    for owner in sorted({row.production_owner for row in registry.REGISTRY}):
        module_name, attribute = owner.rsplit(".", 1)
        module = importlib.import_module(module_name)
        assert callable(getattr(module, attribute, None)), owner


def test_trace_is_nested_and_context_local(registry):
    one = "snapshot:mandatory:inline:clean"
    two = "snapshot:frequency:internal:clean"
    with registry.capture_branches() as outer:
        registry.record_branch(one)
        with registry.capture_branches() as inner:
            registry.record_branch(two)
        assert inner == {two}
    assert outer == {one, two}
    with registry.capture_branches() as later:
        assert later == set()


def test_registry_membership_does_not_accept_arbitrary_ids(registry):
    for scope_id in ("", "snapshot:mandatory:inline:typo", "not-a-scope", "💥"):
        assert not registry.is_registered(scope_id)
        with pytest.raises(registry.UnregisteredBranchError):
            registry.branch(scope_id)


def test_unknown_modality_cannot_become_a_deontic_violation(registry):
    with pytest.raises(registry.UnregisteredBranchError):
        registry.violated_branch("mandatory", "inline", "typo")


def test_scope_identity_never_reaches_public_verdict_bytes(registry):
    from gnd.checker import ConstraintVerdict

    row = ConstraintVerdict(
        scope_id="snapshot:mandatory:inline:clean",
        constraint_ref="constraints[0]",
        constraint_type="mandatory",
        modality="alethic",
        source="explicit",
        status="confirmed",
        verdict="pass",
        message="test",
    )
    assert row.scope_id == "snapshot:mandatory:inline:clean"
    assert "scope_id" not in row.model_dump()
    assert "scope_id" not in row.model_dump_json()


def test_lookup_does_not_fabricate_execution(registry):
    with registry.capture_branches() as reached:
        registry.branch("snapshot:mandatory:inline:clean")
        registry.is_registered("snapshot:mandatory:inline:clean")
        registry.violated_branch("mandatory", "inline", "alethic")
    assert not reached


def test_invalid_outcome_is_not_recorded(registry):
    with registry.capture_branches() as reached, pytest.raises(registry.UnregisteredBranchError):
        registry.record_branch("snapshot:mandatory:inline:clean", outcome="fail")
    assert not reached


def test_a_known_derivation_branch_cannot_impersonate_a_snapshot(registry):
    from gnd.checker import ConstraintVerdict

    with registry.capture_branches() as reached, pytest.raises(
        registry.UnregisteredBranchError, match="cannot construct a constraint verdict"
    ):
        ConstraintVerdict(
            scope_id="derivation:extension:derived:clean",
            constraint_ref="constraints[0]",
            constraint_type="mandatory",
            modality="alethic",
            source="explicit",
            status="confirmed",
            verdict="pass",
            message="test",
        )
    assert not reached














































def test_a_registered_refusal_cannot_carry_another_reason(registry):
    from gnd.checker import ConstraintVerdict

    with pytest.raises(registry.UnregisteredBranchError):
        ConstraintVerdict(
            scope_id="snapshot:mandatory:inline:unchecked-role-unresolved",
            constraint_ref="constraints[0]",
            constraint_type="mandatory",
            modality="alethic",
            source="explicit",
            status="confirmed",
            verdict="unchecked",
            message="test",
            reason_code="family-unimplemented",
        )


def test_derivation_requires_a_registered_scope(registry):
    from gnd.checker import DerivationVerdict

    with pytest.raises(registry.UnregisteredBranchError):
        DerivationVerdict(
            scope_id="derivation:invented:n-a:clean",
            derivation_ref="derivation:result",
            fact_type="result",
            derivation="derived",
            verdict="pass",
            message="test",
        )

























































def test_transition_requires_a_registered_scope(registry):
    from gnd.transition import TransitionVerdict

    with pytest.raises(registry.UnregisteredBranchError):
        TransitionVerdict(
            scope_id="transition:invented:n-a:violated:alethic",
            family="step",
            locator="$.steps[1]",
            kind="precondition",
            modality="alethic",
            verdict="fail",
            message="test",
        )


































































































