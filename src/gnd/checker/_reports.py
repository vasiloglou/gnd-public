"""Existing checker reports section; historical facade retained."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Literal

from pydantic import BaseModel, Field, ValidationInfo, model_validator

from gnd.branches import UnregisteredBranchError, branch, record_branch
from gnd.extensions import DerivationVerdict
from gnd.proof_kernel import SliceInput, SliceVerdict

Verdict = Literal["pass", "fail", "warning", "unchecked", "vacuous"]

class ConstraintVerdict(BaseModel):
    """One verdict for one constraint."""

    scope_id: str = Field(exclude=True)
    constraint_ref: str
    constraint_type: str
    modality: str
    #: The constraint's own declared provenance origin (R-01) — read straight
    #: from the constraint dict, whose meta-schema requires it. Deliberately NO
    #: default: a silent ``""`` is how the second construction site
    #: (measure/promote.py) would drift out of sync (P-4). PANEL-3 scoping:
    #: only ``source`` + ``status`` are surfaced into reports; the full
    #: ``provenance`` block (user_quote etc.) is deliberately NOT copied.
    source: str
    #: The constraint's confirmation status (R-01) — same rules as ``source``:
    #: no default, threaded from the constraint at both construction sites,
    #: and the only other provenance field PANEL-3 admits into the payload.
    status: str
    verdict: Verdict
    message: str
    offending_facts: list[Any] = Field(default_factory=list)
    fact_refs: list[dict[str, Any]] = Field(default_factory=list, exclude=True)
    #: Machine-readable reason a constraint could not be evaluated (D-12).
    #: Non-null if and only if ``verdict == "unchecked"`` — a machine-readable
    #: sibling of ``message``, never a replacement for it. "Unimplemented
    #: family", "join disconnected" and "no reference clock" are different
    #: problems, and a retry loop must be able to tell them apart.
    reason_code: str | None = None

    @model_validator(mode="after")
    def _registered_branch(self, info: ValidationInfo) -> ConstraintVerdict:
        row = branch(self.scope_id)
        if row.surface not in {"snapshot", "applicability", "composition"} or (
            row.surface == "composition"
            and row.family not in {"oracle-verdict", "verifier-verdict"}
        ):
            raise UnregisteredBranchError("branch cannot construct a constraint verdict")
        if row.surface == "snapshot" and row.family != self.constraint_type:
            raise UnregisteredBranchError("snapshot branch names another constraint family")
        if row.modality != "any" and row.modality != self.modality:
            raise UnregisteredBranchError("snapshot branch names another modality")
        if row.surface != "composition" and row.reason_code != self.reason_code:
            raise UnregisteredBranchError("verdict reason disagrees with its registered branch")
        if not (isinstance(info.context, dict) and info.context.get("branch_already_recorded")):
            record_branch(self.scope_id, outcome=self.verdict)
        return self


class CoverageEntry(BaseModel):
    """Declared-coverage status and fact count for one fact type."""

    declared: Literal["declared", "undeclared"]
    facts: int


@dataclass(frozen=True)
class Phase1Trace:
    """The v6.0 Phase 1 evidence lane for one complete in-scope result.

    Present only when EVERY constraint of the checked model fell inside the
    bounded slice, because a partial trace cannot carry a whole-result
    assurance and pretending otherwise is the defect r2 A6 names. Excluded from
    the report's serialization: Phase 1 adds no public wire field (section 8),
    and the evidence runner is the only consumer.
    """

    rows: tuple[tuple[SliceInput, SliceVerdict], ...]
    coverage: tuple[tuple[str, str, int], ...]
    applicable: int
    slice_decided: int


class CheckReport(BaseModel):
    """The full set of per-constraint verdicts for one (model, population) pair."""

    verdicts: list[ConstraintVerdict] = Field(default_factory=list)
    #: v6.0 Phase 1, spec section 5.4. Excluded, internal, and never a public
    #: assurance field in this phase.
    phase1_trace: Phase1Trace | None = Field(default=None, exclude=True)
    #: A14.4's refusal ledger: one (constraint_ref, reason) row per constraint
    #: the Phase 1 slice REFUSED to certify -- a decision the evidence lane
    #: records, never an absence (O7; review finding R12). Excluded from the
    #: public wire exactly like the trace.
    phase1_refusals: tuple[tuple[str, str], ...] = Field(default=(), exclude=True)
    #: v6.0 Phase 3 authoritative snapshot result.  This is internal evidence;
    #: the public payload continues to serialize the stable CheckReport fields.
    snapshot_projection: Any = Field(default=None, exclude=True)
    admission_projection: Any = Field(default=None, exclude=True)
    assurance_input_scope_ids: tuple[str, ...] = Field(default=(), exclude=True)
    # Ordinary and nested model_dump calls deliberately retain the v3 shape.
    # The v4 payload builder serializes this excluded field explicitly.
    derivations: list[DerivationVerdict] = Field(default_factory=list, exclude=True)
    coverage: dict[str, CoverageEntry] = Field(default_factory=dict)

    @property
    def has_alethic_fail(self) -> bool:
        return any(v.verdict == "fail" and v.modality == "alethic" for v in self.verdicts) or any(
            verdict.verdict == "fail" for verdict in self.derivations
        )

    @property
    def has_vacuous(self) -> bool:
        return any(v.verdict == "vacuous" for v in self.verdicts)

    @property
    def has_unevaluated_alethic(self) -> bool:
        # D-07: an ALETHIC constraint the checker never mechanically evaluated
        # means acceptance cannot be claimed — distinct from "decided, no
        # subjects" (vacuous). Deontic constraints are feedback-only, so an
        # unchecked deontic one never affects the band. The acceptance rule
        # lives HERE and nowhere else: the CLI router, the JSON emitter and the
        # corpus all read this one property, because a duplicated comprehension
        # is how exit bands drift apart.
        return any(
            v.verdict == "unchecked" and v.modality == "alethic" for v in self.verdicts
        ) or any(verdict.verdict == "unchecked" for verdict in self.derivations)

    def counts(self) -> dict[str, int]:
        totals = {"pass": 0, "fail": 0, "warning": 0, "unchecked": 0, "vacuous": 0}
        for verdict in self.verdicts:
            totals[verdict.verdict] += 1
        for verdict in self.derivations:
            totals[verdict.verdict] += 1
        return totals


def band(report: CheckReport) -> int:
    """Verdicts -> exit band, precedence 3 > 1 > 4 > 2 > 0 (D-08).

    Band 3 (load/model-relative rejection) returns earlier from the CLI's load
    arms, so it never reaches here. This is the ONE implementation of the exit-band
    rule: the CLI router, the JSON emitter, and the Phase 2/4 measurement harness
    all delegate to it, because a duplicated comprehension is how exit bands drift
    apart (see :attr:`CheckReport.has_unevaluated_alethic`). Each predicate lives on
    :class:`CheckReport`, never as a comprehension in a caller.
    """
    if report.snapshot_projection is not None:
        result = int(report.snapshot_projection.band)
        if any(row.verdict == "fail" for row in report.derivations):
            result = 1
        elif result != 1 and any(row.verdict == "unchecked" for row in report.derivations):
            result = 4
    elif report.has_alethic_fail:
        result = 1
    elif report.has_unevaluated_alethic or any(
        row.verdict == "unchecked" and row.reason_code == "reference-join-work-limit"
        for row in report.verdicts
    ):
        result = 4
    elif report.has_vacuous:
        result = 2
    else:
        result = 0
    routes = ("n-a", "phase1") if report.phase1_trace is not None else ("n-a",)
    for selected_route in routes:
        prefix = f"composition:band:{selected_route}:"
        event = {1: "alethic-fail", 4: "alethic-unchecked", 2: "vacuous", 0: "clean"}[result]
        record_branch(prefix + event)
        if result == 1 and report.has_unevaluated_alethic and report.has_vacuous:
            record_branch(prefix + "fail-over-unchecked-over-vacuous")
        if result == 4 and report.has_vacuous:
            record_branch(prefix + "unchecked-over-vacuous")
        if result == 2 and any(row.verdict == "pass" for row in report.verdicts):
            record_branch(prefix + "vacuous-over-clean")
        if any(row.modality == "deontic" and row.verdict == "warning" for row in report.verdicts):
            record_branch(prefix + "deontic-warning-keeps-band")
        if any(row.modality == "deontic" and row.verdict == "unchecked" for row in report.verdicts):
            record_branch(prefix + "deontic-unchecked-keeps-band")
    return result



ConstraintVerdict.__module__ = 'gnd.checker'
CoverageEntry.__module__ = 'gnd.checker'
Phase1Trace.__module__ = 'gnd.checker'
CheckReport.__module__ = 'gnd.checker'
band.__module__ = 'gnd.checker'
ConstraintVerdict.__dict__['_registered_branch'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__hash__'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__init__'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__repr__'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__eq__'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__setattr__'].__module__ = 'gnd.checker'
Phase1Trace.__dict__['__delattr__'].__module__ = 'gnd.checker'
CheckReport.__dict__['has_alethic_fail'].fget.__module__ = 'gnd.checker'
CheckReport.__dict__['has_vacuous'].fget.__module__ = 'gnd.checker'
CheckReport.__dict__['has_unevaluated_alethic'].fget.__module__ = 'gnd.checker'
CheckReport.__dict__['counts'].__module__ = 'gnd.checker'
