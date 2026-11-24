"""GO3: the part of a proposal no gate refused, as a new proposal (#227).

Spec: .gnd-planning/milestones/growth-round-outcomes/notes/phase-GO3-spec.md (§8, T1-T6, and
§13's seeded-root case).
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import pytest
import test_evolve_additive_policy as policy
import test_go2_operation_outcomes as go2
from support.cli_runner import run_main

from gnd.discover.narrow import narrow_proposal
from gnd.evolve import (
    CommittedText,
    EvolutionError,
    EvolutionOutcomeReport,
    OperationOutcome,
    OutcomeRefusal,
)

TEXT = go2.TEXT


def _report(tmp_path: Path, operations: tuple[Any, ...], **options: Any) -> tuple[Any, EvolutionOutcomeReport]:
    proposal = policy._proposal(TEXT, operations)
    error = go2._refused(tmp_path, operations, **options)
    return proposal, error.outcome_refusal.report(exit_code=3, message=str(error))


def _write(path: Path, proposal: Any) -> None:
    path.write_text(json.dumps(proposal.model_dump(mode="json"), indent=2, sort_keys=True) + "\n", encoding="utf-8")


# --- T1 (GO3-C1): from GO2-C1's report, a proposal that previews and applies --------------------


def test_t1_the_narrowed_proposal_previews_and_applies(tmp_path: Path) -> None:
    operations = (go2.ADD_OBJECT, go2.ADD_FACT, go2._invalid_object("bad", "op-bad"),
                  go2._constraint(status="confirmed"))
    proposal, report = _report(tmp_path / "report", operations)
    narrowed, reasons = narrow_proposal(proposal, report)
    assert [operation.operation_id for operation in narrowed.operations] == ["op-object", "op-fact", "op-constraint"]
    assert reasons == ("2 op-bad refused-by-validation",)
    paths = policy._cli_workspace(tmp_path / "cli", (go2.ADD_OBJECT,))
    _write(paths["proposal"], narrowed)
    result = run_main(policy._preview_argv(paths))
    assert result.returncode == 0, result.stderr
    result = run_main(policy._apply_argv(paths))
    assert result.returncode == 0, result.stderr
    published = paths["model"].read_text(encoding="utf-8")
    assert "order_ships_to_region" in published and '"bad"' not in published


# --- T2 (GO3-C2): a dependent is dropped with the refused operation --------------------------------


def test_t2_a_constraint_on_a_refused_fact_type_is_dropped_with_it(tmp_path: Path) -> None:
    broken = dict(policy.NEW_FACT, roles=[{"object_type": "nowhere", "role_name": "region"},
                                          {"object_type": "order", "role_name": "order"}])
    operations = (go2.ADD_OBJECT, go2._op("add", policy._element("fact_types", go2.HOST), broken, "op-fact"),
                  go2._constraint(status="confirmed"))
    proposal, report = _report(tmp_path, operations)
    narrowed, reasons = narrow_proposal(proposal, report)
    assert [operation.operation_id for operation in narrowed.operations] == ["op-object"]
    assert reasons == ("1 op-fact refused-by-validation", "2 op-constraint dropped-with")


def test_t2_the_closure_is_recomputed_over_any_outcome_list(tmp_path: Path) -> None:
    """A host that passes back rows marking only the fact type refused still loses its constraint."""
    operations = (go2.ADD_OBJECT, go2.ADD_FACT, go2._constraint(status="confirmed"))
    proposal = policy._proposal(TEXT, operations)
    rows = tuple(OperationOutcome(operation_index=i, operation_id=op.operation_id, reference=op.locator.reference(),
                                  verdict="refused-by-policy" if i == 1 else "admitted", detail="cell" if i == 1 else "")
                 for i, op in enumerate(operations))
    report = _bare_report(proposal, rows)
    narrowed, reasons = narrow_proposal(proposal, report)
    assert [operation.operation_id for operation in narrowed.operations] == ["op-object"]
    assert reasons == ("1 op-fact refused-by-policy", "2 op-constraint dropped-with")


def _bare_report(proposal: Any, rows: tuple[Any, ...], before: str = TEXT) -> EvolutionOutcomeReport:
    return EvolutionOutcomeReport(
        proposal_id=proposal.proposal_id, proposal_sha256=proposal.proposal_sha256,
        before_model=CommittedText.from_text(before, media_type="application/yaml"),
        refusal=OutcomeRefusal(gate="policy", exit=3, message="refused"), operation_outcomes=rows)


# --- T3 (GO3-C3): identity, origin, and the original preview -----------------------------------------


def test_t3_identity_origin_and_the_original_preview(tmp_path: Path) -> None:
    refused = go2._op("add", policy._constraint_locator(policy.POPULATED, None, "mandatory"),
                      policy.NEW_CONSTRAINT, "op-p")
    paths = policy._cli_workspace(tmp_path / "a", (go2.ADD_OBJECT, refused))
    original_bytes = paths["proposal"].read_bytes()
    assert b"narrowed_from" not in original_bytes
    assert run_main([*policy._preview_argv(paths, "--policy", "additive"), "--operation-outcomes"]).returncode == 3
    from gnd.evolve import read_evolution_preview, read_evolution_proposal

    proposal = read_evolution_proposal(paths["proposal"])
    preview = read_evolution_preview(paths["preview"])
    narrowed, reasons = narrow_proposal(proposal, preview)
    assert narrowed.proposal_id == f"{proposal.proposal_id}-narrowed"
    assert narrowed.narrowed_from.proposal_id == proposal.proposal_id
    assert narrowed.narrowed_from.proposal_sha256 == proposal.proposal_sha256
    assert reasons == ("1 op-p refused-by-policy",)
    assert paths["proposal"].read_bytes() == original_bytes
    # Narrowing writes nothing: the original preview is refused at apply as today (its policy issues).
    today = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert today.returncode == 3, today.stderr
    narrowed_paths = {**paths, "proposal": paths["workspace"] / "narrowed.json",
                      "preview": paths["workspace"] / "narrowed-preview.json"}
    _write(narrowed_paths["proposal"], narrowed)
    assert run_main(policy._preview_argv(narrowed_paths, "--policy", "additive")).returncode == 0
    assert run_main(policy._apply_argv(narrowed_paths, "--policy", "additive")).returncode == 0
    # After the narrowed proposal is applied, the original preview is a stale model.
    stale = run_main(policy._apply_argv(paths, "--policy", "additive"))
    assert stale.returncode == 11, stale.stderr


def test_t3_a_proposal_without_the_field_keeps_its_bytes() -> None:
    proposal = policy._proposal(TEXT, (go2.ADD_OBJECT,))
    document = proposal.model_dump(mode="json")
    assert "narrowed_from" not in document
    from gnd.evolve import canonical_sha256, read_evolution_proposal_document

    assert proposal.proposal_sha256 == canonical_sha256(document)
    assert read_evolution_proposal_document(document) == proposal


# --- T4 (GO3-C4): nothing kept ---------------------------------------------------------------------


def test_t4_nothing_kept_returns_no_proposal(tmp_path: Path) -> None:
    operations = (go2._invalid_object("bad", "op-1"), go2._invalid_object("worse", "op-2"))
    proposal, report = _report(tmp_path, operations)
    narrowed, reasons = narrow_proposal(proposal, report)
    assert narrowed is None
    assert reasons == ("0 op-1 refused-by-validation", "1 op-2 refused-by-validation")


# --- T5: refusals, in order --------------------------------------------------------------------------


def test_t5_what_narrowing_refuses_and_in_which_order(tmp_path: Path) -> None:
    proposal, report = _report(tmp_path, (go2.ADD_OBJECT, go2._invalid_object("bad", "op-bad")))
    with pytest.raises(TypeError, match="EvolutionProposal"):
        narrow_proposal(proposal.model_dump(mode="json"), report)
    with pytest.raises(TypeError, match="EvolutionPreview or an EvolutionOutcomeReport"):
        narrow_proposal(proposal, report.model_dump(mode="json"))
    other = policy._proposal(TEXT, (go2.ADD_OBJECT,), proposal_id="another")
    with pytest.raises(ValueError, match="not this proposal's"):
        narrow_proposal(other, report)
    moved = report.model_copy(update={"before_model": CommittedText.from_text(TEXT + "# x\n",
                                                                              media_type="application/yaml")})
    with pytest.raises(ValueError, match="before model"):
        narrow_proposal(proposal, moved)
    preview = policy._service(tmp_path / "plain", TEXT).preview(policy._proposal(TEXT, (go2.ADD_OBJECT,)))
    with pytest.raises(ValueError, match="no operation_outcomes"):
        narrow_proposal(policy._proposal(TEXT, (go2.ADD_OBJECT,)), preview)


# --- T6: linear in the operations ---------------------------------------------------------------------


def test_t6_two_thousand_operations_half_refused() -> None:
    n = 2_000
    operations = tuple(go2._op("add", policy._element("object_types", f"t{i}"),
                               {"id": f"t{i}", "name": f"T{i}", "kind": "value", "primitive": "String"}, f"op-{i}")
                       for i in range(n))
    proposal = policy._proposal(TEXT, operations)
    rows = tuple(OperationOutcome(operation_index=i, operation_id=f"op-{i}", reference=op.locator.reference(),
                                  verdict="refused-by-validation" if i % 2 else "admitted",
                                  detail="r" if i % 2 else "")
                 for i, op in enumerate(operations))
    start = time.perf_counter()
    narrowed, reasons = narrow_proposal(proposal, _bare_report(proposal, rows))
    assert time.perf_counter() - start < 1.0
    assert len(narrowed.operations) == n // 2 and len(reasons) == n // 2


# --- §13: a seeded unattended root with no documents key ----------------------------------------------


def test_t1_a_seeded_root_first_round_narrows_and_previews(tmp_path: Path) -> None:
    import test_vg4_seeded_growth_rounds as vg4

    root = vg4._undocumented(tmp_path / "ws")
    bad = go2._invalid_object("bad", "bad")
    operations = (vg4._first_document(), *vg4._owned_round()[:1], bad)
    proposal = vg4._proposal(root, operations)
    with pytest.raises(EvolutionError) as caught:
        vg4._service(root).preview(proposal, operation_outcomes=True)
    report = caught.value.outcome_refusal.report(exit_code=3, message=str(caught.value))
    narrowed, reasons = narrow_proposal(proposal, report)
    assert reasons and narrowed is not None
    assert [operation.operation_id for operation in narrowed.operations] == ["doc", "author"]
    preview = vg4._service(root).preview(narrowed, policy="additive")
    assert preview.policy_issues == ()


# --- Diff review r1 (notes/reviews/phase-GO3-GO5-r1/FINDINGS.md) ----------------------------------


def test_r1_f1_rows_must_be_the_proposals_operations_in_order() -> None:
    second = go2._op("add", policy._element("object_types", "color"),
                     {"id": "color", "name": "Color", "kind": "value", "primitive": "String"}, "op-color")
    operations = (go2.ADD_OBJECT, second)
    proposal = policy._proposal(TEXT, operations)
    swapped = (OperationOutcome(operation_index=0, operation_id="op-color", reference=second.locator.reference(),
                                verdict="refused-by-validation", detail="r"),
               OperationOutcome(operation_index=1, operation_id="op-object",
                                reference=go2.ADD_OBJECT.locator.reference(), verdict="admitted"))
    with pytest.raises(ValueError, match="not this proposal's operations"):
        narrow_proposal(proposal, _bare_report(proposal, swapped))
