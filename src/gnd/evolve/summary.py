"""GO5 (#227): one summary per growth round that a host can log and compare.

A round is a host's round file (what the reply reused, what the host dropped
and why) plus, when the round produced them, the proposal, its preview or
outcome report, and the evolution record of the applied round. Elements added
come from the record only: a round that was previewed and never applied adds
nothing. The fields are defined in the evolution contract, "Round summary".
"""

from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Annotated, Any, Literal

from pydantic import Field, StringConstraints, ValidationError, model_validator

from gnd import input_policy as _rf7_input

from .models import (
    ElementLocator,
    EvolutionOperationKind,
    EvolutionOutcomeReport,
    EvolutionPreview,
    EvolutionProposal,
    EvolutionRecord,
    StableId,
    _ClosedFrozenModel,
    canonical_sha256,
)

#: A round file is host-written JSON; the cap applies to the read.
MAX_ROUND_FILE_BYTES = 1024 * 1024

#: The host's own text, kept exactly as written (never stripped): GND reports it, never edits it.
HostText = Annotated[str, StringConstraints(min_length=1)]


class RoundFileError(ValueError):
    """A round file or a round artifact the summary refuses, by name."""


class ReusedElement(_ClosedFrozenModel):
    collection: Literal["object_types", "fact_types"]
    id: StableId


class HostDrop(_ClosedFrozenModel):
    """Something the host dropped before the proposal; GND reports it, never judges it."""

    kind: HostText = Field(max_length=64)
    id: HostText = Field(max_length=256)
    reason: HostText = Field(max_length=2000)


class RoundFile(_ClosedFrozenModel):
    """``gnd-round/1``: what the host knows about a round that no artifact holds."""

    schema_version: Literal[1]
    round: StableId
    document: HostText = Field(max_length=512)
    reused: tuple[ReusedElement, ...] = ()
    host_drops: tuple[HostDrop, ...] = ()

    @model_validator(mode="after")
    def _reused_once(self) -> RoundFile:
        keys = [(item.collection, item.id) for item in self.reused]
        if len(set(keys)) != len(keys):
            raise ValueError("reused names each element once")
        return self


class RoundSummary(_ClosedFrozenModel):
    """``gnd-round-summary/1``."""

    schema_version: Literal[1] = 1
    kind: Literal["gnd-round-summary"] = "gnd-round-summary"
    round: StableId
    document: HostText
    reused: dict[str, tuple[str, ...]]
    host_drops: tuple[HostDrop, ...]
    proposed: dict[str, Any]
    outcomes: dict[str, int] | None
    shape_matches: int | None
    added: dict[str, tuple[str, ...]]
    narrowed_from: str | None
    bindings: dict[str, str]


def read_round_file(path: str | Path) -> RoundFile:
    """Read one round file: bounded, strict JSON (no NaN, duplicate key or deep
    nesting), closed shape. Every refusal is a ``RoundFileError`` by name."""
    try:
        with open(path, "rb") as handle:
            raw = handle.read(MAX_ROUND_FILE_BYTES + 1)
    except OSError as error:
        raise RoundFileError(f"round file {path} could not be read: {error}") from None
    if len(raw) > MAX_ROUND_FILE_BYTES:
        raise RoundFileError(f"round file {path} exceeds {MAX_ROUND_FILE_BYTES} bytes")
    try:
        document = _rf7_input.loads(raw)
    except (ValueError, RecursionError) as error:
        raise RoundFileError(f"round file {path} is not strict JSON: {error}") from None
    try:
        return RoundFile.model_validate(document)
    except ValidationError as error:
        raise RoundFileError(f"round file {path} is malformed: {error.error_count()} error(s), "
                             f"first at {'.'.join(map(str, error.errors()[0]['loc'])) or '<root>'}") from None


def _collection(operation: Any) -> str:
    locator = operation.locator
    return locator.collection if isinstance(locator, ElementLocator) else locator.locator_kind


def round_summary(
    round_file: RoundFile,
    *,
    proposal: EvolutionProposal | None = None,
    preview: EvolutionPreview | None = None,
    report: EvolutionOutcomeReport | None = None,
    record: EvolutionRecord | None = None,
) -> RoundSummary:
    """The round's summary. Artifacts are bound to each other before anything
    is counted: a preview or report of another proposal, or a record of
    another preview, is refused."""
    if not isinstance(round_file, RoundFile):
        raise RoundFileError("the summary reads a RoundFile")
    if preview is not None and report is not None:
        raise RoundFileError("a round has a preview or an outcome report, not both")
    if (preview is not None or report is not None or record is not None) and proposal is None:
        raise RoundFileError("a preview, an outcome report or a record needs its proposal")
    for name, claim in (("preview", preview), ("outcome report", report)):
        if claim is not None and claim.proposal_sha256 != proposal.proposal_sha256:
            raise RoundFileError(f"the {name} is not this proposal's")
    if record is not None:
        if preview is None:
            raise RoundFileError("a record needs the preview it applied")
        if record.preview_sha256 != preview.preview_sha256 or record.proposal_sha256 != proposal.proposal_sha256:
            raise RoundFileError("the record is not this preview's")
    rows = (preview.operation_outcomes if preview is not None
            else report.operation_outcomes if report is not None else None)
    if rows is not None and (len(rows) != len(proposal.operations) or any(
        row.operation_index != position or row.operation_id != operation.operation_id
        or row.reference != operation.locator.reference()
        for position, (row, operation) in enumerate(zip(rows, proposal.operations, strict=True))
    )):
        raise RoundFileError("the outcome rows are not the proposal's operations, one per operation in order")

    operations = proposal.operations if proposal is not None else ()
    by_kind = Counter(operation.kind.value for operation in operations)
    by_collection = Counter(_collection(operation) for operation in operations)
    # A round with no proposal is zero in every count (GO5-C2); a proposal whose
    # preview carries no outcomes or no shape report leaves that count null.
    outcomes = ({} if proposal is None else None) if rows is None else dict(
        sorted(Counter(row.verdict for row in rows).items()))
    shapes = ((0 if proposal is None else None) if preview is None or preview.shape_matches is None
              else len(preview.shape_matches))
    added: dict[str, list[str]] = {"object_types": [], "fact_types": [], "constraints": []}
    for operation in record.operations if record is not None else ():
        if operation.kind is not EvolutionOperationKind.ADD:
            continue
        locator = operation.locator
        if isinstance(locator, ElementLocator) and locator.collection in added:
            added[locator.collection].append(locator.element_id)
        elif locator.locator_kind == "constraint":
            added["constraints"].append(operation.operation_id)
    reused: dict[str, list[str]] = {"object_types": [], "fact_types": []}
    for item in round_file.reused:
        reused[item.collection].append(item.id)
    # Each artifact read, by its own identity: the proposal's and the preview's
    # digests as apply binds them, every other document's canonical sha256.
    bindings = {"round_file_sha256": canonical_sha256(round_file)}
    if proposal is not None:
        bindings["proposal_sha256"] = proposal.proposal_sha256
    if preview is not None:
        bindings["preview_sha256"] = preview.preview_sha256
    for name, claim in (("outcome_report_sha256", report), ("record_sha256", record)):
        if claim is not None:
            bindings[name] = canonical_sha256(claim)
    narrowed = getattr(proposal, "narrowed_from", None)
    return RoundSummary(
        round=round_file.round,
        document=round_file.document,
        reused={key: tuple(sorted(value)) for key, value in reused.items()},
        host_drops=round_file.host_drops,
        proposed={"total": len(operations), "by_kind": dict(sorted(by_kind.items())),
                  "by_collection": dict(sorted(by_collection.items()))},
        outcomes=outcomes,
        shape_matches=shapes,
        added={key: tuple(sorted(value)) for key, value in added.items()},
        narrowed_from=None if narrowed is None else narrowed.proposal_id,
        bindings=bindings,
    )
