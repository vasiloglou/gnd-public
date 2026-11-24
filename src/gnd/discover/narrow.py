"""GO3 (#227): the part of a proposal no gate refused, as a new proposal.

`gnd evolve apply` stays whole (a reviewed preview is applied exactly as
reviewed); a host that wants the admitted part of a round narrows the
proposal here and previews and applies the narrowed one like any other. The
contract is in the evolution contract, "Narrowing a proposal".
"""

from __future__ import annotations

from typing import Any

from gnd.evolve import (
    CommittedText,
    EvolutionOutcomeReport,
    EvolutionPreview,
    EvolutionProposal,
    NarrowedFrom,
)
from gnd.evolve import outcomes as _outcomes

from .output import candidate_document, candidate_text

#: Verdicts whose operation is dropped; every other operation is kept.
_DROPPED = frozenset({"refused-by-policy", "refused-by-validation", "refused-by-d12", "dropped-with"})


def narrow_proposal(
    proposal: EvolutionProposal, outcomes: EvolutionPreview | EvolutionOutcomeReport
) -> tuple[EvolutionProposal | None, tuple[str, ...]]:
    """Keep the operations GO2 did not refuse; return the narrowed proposal, or
    ``None`` when none is kept, and one value-free line per dropped operation.

    Refused, in this order: anything but a proposal and a preview or outcome
    report; outcomes of another proposal, or a preview without outcomes; a
    before model whose sha256 is not the proposal's expected model identity;
    rows that are not the proposal's operations, one per operation in order."""
    if not isinstance(proposal, EvolutionProposal):
        raise TypeError("narrowing reads an EvolutionProposal")
    if not isinstance(outcomes, (EvolutionPreview, EvolutionOutcomeReport)):
        raise TypeError("narrowing reads an EvolutionPreview or an EvolutionOutcomeReport")
    if outcomes.proposal_sha256 != proposal.proposal_sha256:
        raise ValueError("the outcomes are not this proposal's: proposal_sha256 differs")
    rows = outcomes.operation_outcomes
    if rows is None:
        raise ValueError("the preview carries no operation_outcomes; preview with --operation-outcomes")
    if outcomes.before_model.sha256 != proposal.expected_model_sha256:
        raise ValueError("the outcomes' before model is not the proposal's expected model")
    if len(rows) != len(proposal.operations) or any(
        row.operation_index != position or row.operation_id != operation.operation_id
        or row.reference != operation.locator.reference()
        for position, (row, operation) in enumerate(zip(rows, proposal.operations, strict=True))
    ):
        raise ValueError("the outcome rows are not this proposal's operations, one per operation in order")

    refused = {row.operation_index: (row.verdict, row.detail) for row in rows if row.verdict in _DROPPED}
    # The closure again, over the kept set: total over any outcome list a host passes back.
    recomputed = _outcomes.outcomes(proposal.operations, refused)
    kept = tuple(operation for operation, row in zip(proposal.operations, recomputed, strict=True)
                 if row.verdict not in _DROPPED)
    reasons = tuple(f"{row.operation_index} {row.operation_id} {row.verdict}"
                    for row in recomputed if row.verdict in _DROPPED)
    if not kept:
        return None, reasons

    before = _before_document(outcomes.before_model)
    narrowed = EvolutionProposal(
        schema_version=proposal.schema_version,
        proposal_id=f"{proposal.proposal_id}-narrowed",
        expected_model_sha256=proposal.expected_model_sha256,
        candidate_model=CommittedText.from_text(
            candidate_text(candidate_document(before, kept)),
            media_type=proposal.candidate_model.media_type,
        ),
        operations=kept,
        rationale=proposal.rationale,
        audit=proposal.audit,
        linked_projects=proposal.linked_projects,
        artifacts=proposal.artifacts,
        narrowed_from=NarrowedFrom(proposal_id=proposal.proposal_id, proposal_sha256=proposal.proposal_sha256),
    )
    return narrowed, reasons


def _before_document(before_model: CommittedText) -> dict[str, Any]:
    """The before model as the evolve replay reads it: parsed by the model's
    parser and brought to the JSON domain, refusing a value JSON cannot spell."""
    from gnd.model import json_document, parse_model_document

    return json_document(parse_model_document(before_model.text.encode("utf-8"), source="model.orm.yaml"))
