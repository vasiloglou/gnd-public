"""Deterministic constraint checker with the 5-state verdict lattice.

``check(model, population)`` walks every inline and top-level constraint and
assigns each exactly one verdict from {pass, fail, warning, unchecked, vacuous}:

- Unimplemented constraint families are reported ``unchecked`` — never silently
  passed (D-02).
- A constraint whose subject fact types contain zero facts is ``vacuous``
  (D-12); guarded conjunctions use the stricter any-antecedent-empty rule.
- A violated constraint yields ``fail`` when its modality is alethic and
  ``warning`` when deontic (VER-01 semantics).

Object-type populations follow closed-world semantics (SKELETON.md): the
instance set of object type T is every value playing a T-typed role across all
facts, extended by the explicit ``instances[T]`` roster.

Every verdict message is rendered from the CNL templates in
:mod:`gnd.verbalize`.
"""

from __future__ import annotations

import math
from collections.abc import Callable, Collection, Iterable, Mapping, Sequence
from collections.abc import Set as AbstractSet
from contextvars import ContextVar
from dataclasses import dataclass, field, replace
from datetime import UTC, date, datetime
from decimal import Decimal
from fractions import Fraction
from graphlib import CycleError, TopologicalSorter
from types import MappingProxyType
from typing import Any, Literal, NamedTuple, Protocol

from pydantic import BaseModel, Field, ValidationInfo, model_validator

from gnd import verbalize
from gnd.address import derivation_address, positional_constraint_ref
from gnd.atoms import atom_bind, atom_has_bind
from gnd.model import (
    AggregateAnalysis,
    Model,
    _derivation_variable,
    analyze_declared_aggregate,
    body_components,
    derivation_classifications,
    derivation_dependencies,
    derivation_strata,
    iter_derivation_clauses,
)
from gnd.population import Population
from gnd.popvalidate import resolve_primitive, resolve_reference_value_type
from gnd.proof_bridge import adapt_phase1_slice, phase1_refusal_reason
from gnd.proof_kernel import (
    MAX_SLICE_CONSTRAINTS,
    SliceInput,
    SliceVerdict,
    phase1_decide,
)
from gnd.references import BoundReferenceContext
from gnd.semantic_registry import (
    UnregisteredBranchError,
    branch,
    constraint_variant,
    record_branch,
    time_relative_operand,
)
from gnd.terms import (
    DEFAULT_LIMITS,
    compare_terms,
    evaluate_term,
    is_function_term,
    materialize_scalar,
    term_variables,
)

Verdict = Literal["pass", "fail", "warning", "unchecked", "vacuous"]
DerivationKind = Literal[
    "derived-extension-incomplete",
    "derived-extension-unsound",
    "derived-extension-unresolved",
]
DerivationReason = Literal[
    "derivation-not-covered",
    "derivation-rule-opaque",
    "opaque-value",
    "derived-unknown",
    "term:mod-zero",
    "term:exact-value-too-wide",
    "term:dependency-unavailable",
    "term:div-zero",
    "term:sqrt-negative",
    "term:haversine-coordinate-range",
    "term:float-overflow",
]

DERIVATION_REASON_CODES: tuple[DerivationReason, ...] = (
    "derivation-not-covered",
    "derivation-rule-opaque",
    "opaque-value",
    "derived-unknown",
)

EXACT_DERIVATION_REASON_CODES: tuple[DerivationReason, ...] = (
    "derived-unknown",
    "term:mod-zero",
    "term:exact-value-too-wide",
    "term:dependency-unavailable",
    "term:div-zero",
    "term:sqrt-negative",
    "term:haversine-coordinate-range",
    "term:float-overflow",
)

#: Constraint families the checker implements (all others -> unchecked, D-02).
IMPLEMENTED_FAMILIES = {
    "anchored",
    "uniqueness",
    "mandatory",
    "mandatory-disjunctive",
    "value",
    "frequency",
    "ring",
    "subset",
    "equality",
    "exclusion",
    "exclusive-or",
    "value-comparison",
    "cardinality",
    "subtype-partition",
    "guarded",
}

#: Combined ring variants -> their component variants (each evaluated).
_RING_COMPONENTS = {
    "asymmetric-intransitive": ("asymmetric", "intransitive"),
    "acyclic-intransitive": ("acyclic", "intransitive"),
    "symmetric-irreflexive": ("symmetric", "irreflexive"),
    "symmetric-intransitive": ("symmetric", "intransitive"),
}

_RING_VARIANTS = {
    "irreflexive",
    "asymmetric",
    "intransitive",
    "antisymmetric",
    "acyclic",
    "symmetric",
    "purely-reflexive",
    "reflexive",
    "transitive",
} | set(_RING_COMPONENTS)


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


class DerivationFinding(BaseModel):
    """One missing or offending row in a structured derivation claim."""

    kind: DerivationKind
    message: str
    witness: dict[str, Any]


class DerivationVerdict(BaseModel):
    """One alethic comparison obligation for one derived fact type."""

    scope_id: str = Field(exclude=True)
    derivation_ref: str
    fact_type: str
    derivation: Literal["derived", "semiderived"]
    modality: Literal["alethic"] = "alethic"
    verdict: Literal["pass", "fail", "unchecked"]
    message: str
    findings: list[DerivationFinding] = Field(default_factory=list)
    reason_code: DerivationReason | None = None

    @model_validator(mode="after")
    def _closed_shape(self) -> DerivationVerdict:
        if self.derivation_ref != derivation_address(self.fact_type):
            raise ValueError("derivation_ref must address fact_type")
        if self.verdict == "pass" and (self.findings or self.reason_code is not None):
            raise ValueError("pass derivations have neither findings nor a reason")
        if self.verdict == "fail":
            if not 1 <= len(self.findings) <= 3 or self.reason_code is not None:
                raise ValueError("fail derivations have one to three findings and no reason")
            kinds = [finding.kind for finding in self.findings]
            canonical = [
                kind
                for kind in (
                    "derived-extension-incomplete",
                    "derived-extension-unsound",
                    "derived-extension-unresolved",
                )
                if kind in kinds
            ]
            if kinds != canonical or len(kinds) != len(set(kinds)):
                raise ValueError("derivation findings must be unique and canonically ordered")
        if self.verdict == "unchecked" and (
            self.reason_code not in (*DERIVATION_REASON_CODES, *EXACT_DERIVATION_REASON_CODES)
            or (self.findings and (
                self.reason_code != "derived-unknown"
                or len(self.findings) != 1
                or self.findings[0].kind != "derived-extension-unresolved"
            ))
            or (self.reason_code == "derived-unknown" and not self.findings)
        ):
            raise ValueError("unchecked derivations require a closed reason and matching findings")
        row = branch(self.scope_id)
        if (row.surface, row.family) not in {
            ("derivation", "extension"),
            ("experiment-feedback", "verifier-derivation"),
        } or row.variant != self.derivation:
            raise UnregisteredBranchError("derivation branch names another obligation")
        if row.reason_code != self.reason_code:
            raise UnregisteredBranchError("derivation reason disagrees with its branch")
        record_branch(self.scope_id, outcome=self.verdict)
        return self


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


class UnvalidatedPopulationError(Exception):
    """:func:`check` was called with a population that never passed layer-2
    (model-relative) validation against *this* model object (D-02).

    Skipping CORE-04 is made structurally impossible rather than merely
    discouraged: a population whose facts do not have the shape the model
    declares makes ``_project`` filter them out, so uniqueness sees an empty
    projection and mandatory an empty universe — and the checker then
    affirmatively reports both as satisfied. Documentation could not prevent
    that; this precondition can.

    From the CLI this path is unreachable by construction (``cli.py`` always
    loads with ``model=``), so it is NOT dead code — it guards the Phase 2
    generator, the Phase 4 retry loop, and every future in-process caller. The
    CLI's existing catch-all maps it to exit 70 (EX_SOFTWARE), which is the
    right band: arriving here unvalidated is a harness/programming bug, not a
    model or population signal, and 70 never masquerades as a band verdict.
    """

    def __init__(self, population: Population, model: Model | None = None):
        if population.validated_against is None:
            state = "it was never validated (validated_against=nothing)"
        elif model is not None and population.validated_against is not model:
            state = "it was validated against a DIFFERENT model object"
        else:
            state = (
                "it WAS validated against this model, but its content has changed "
                "since — the recorded content digest no longer matches. Mutating a "
                "loaded population (assigning to a field, appending to "
                "population.facts[...], or model_copy(update={...})) re-opens the "
                "very hole layer 2 closes (CR-01); re-load or re-validate the "
                "mutated content instead"
            )
        super().__init__(
            "check() was called with a population that was not validated against "
            "this model. Load it via load_population(path, model=model), which "
            "runs layer-2 structural validation (CORE-04) and stamps the result. "
            "There is deliberately no bypass (D-18). If you deep-copied a "
            "validated population, the marker's identity was lost — re-load or "
            "re-stamp it; the copy fails closed on purpose. "
            f"(population declares model={population.model!r}; {state})"
        )


def check_legacy(model: Model, population: Population) -> CheckReport:
    """Check a population against every constraint in the model.

    Precondition (D-02): ``population`` must carry the layer-2 validation marker
    for THIS model object AND still hold the content that was validated, or
    :class:`UnvalidatedPopulationError` is raised.
    """
    # Both halves live in Population.matches_validation_marker: model identity
    # (`is`, never equality — two independent load_model() calls on one file
    # compare equal) AND a re-derived content digest, so a population that was
    # loaded cleanly and then mutated is refused rather than checked against
    # facts layer 2 never saw (CR-01). One predicate, one place, because a
    # precondition split across two call sites is how the first half survives a
    # refactor without the second.
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)

    extensions, derivations = _evaluate_derivations(model, population)
    constraint_population: Population | _RuledFactView = population
    if extensions:
        constraint_population = _constraint_view(model, population, extensions)

    constraint_inputs: dict[str, tuple[dict[str, Any], dict[str, Any] | None]] = {}
    trace_rows: list[tuple[SliceInput, SliceVerdict]] = []
    refusal_rows: list[tuple[str, str]] = []
    aliases: dict[str, str] = {}

    for fact_type in model.fact_types:
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            ref = positional_constraint_ref(str(fact_type.get("id")), index)
            constraint_inputs[ref] = (constraint, fact_type)
            _observe_phase1_compatibility(
                constraint,
                ref,
                model,
                constraint_population,
                fact_type,
                trace_rows,
                refusal_rows,
                aliases,
            )

    for index, constraint in enumerate(model.constraints):
        ref = positional_constraint_ref(None, index)
        constraint_inputs[ref] = (constraint, None)
        _observe_phase1_compatibility(
            constraint,
            ref,
            model,
            constraint_population,
            None,
            trace_rows,
            refusal_rows,
            aliases,
        )

    from gnd.correspondence import correspond_snapshot, project_snapshot

    adapted, decision = correspond_snapshot(
        model,
        population,
        effective_facts=constraint_population.facts,
        effective_lineage=(
            constraint_population.lineages
            if isinstance(constraint_population, _RuledFactView)
            else None
        ),
        variant_aliases=aliases,
    )
    projection = project_snapshot(decision, adapted.observation)
    from gnd.correspondence import ReferenceJoinLimit, project_reference_limit

    projected_findings = projection.findings
    retained_findings = []
    presentation_refused = False
    verdicts: list[ConstraintVerdict] = []
    for finding in projected_findings:
        constraint, fact_type = constraint_inputs[finding.constraint_id]
        witness = _plain_projected_witness(finding.constraint_type, finding.witness)
        try:
            message = _correspondence_message(
                constraint, fact_type, finding, witness, model, constraint_population
            )
        except ReferenceJoinLimit:
            finding = project_reference_limit(finding, adapted.observation)
            witness = []
            message = "Guarded binding production exceeded reference work ceiling 100000."
            presentation_refused = True
        retained_findings.append(finding)
        verdict_payload = {
            "scope_id": finding.scope_id,
            "constraint_ref": finding.constraint_id,
            "constraint_type": finding.constraint_type,
            "modality": finding.modality,
            "source": str(constraint.get("source", "")),
            "status": str(constraint.get("status", "")),
            "verdict": finding.verdict,
            "message": message,
            "offending_facts": witness,
            "reason_code": finding.reason_code,
        }
        verdicts.append(
            ConstraintVerdict.model_validate(
                verdict_payload,
                context={"branch_already_recorded": True},
            )
        )

    if presentation_refused:
        vocabulary = ("pass", "fail", "warning", "unchecked", "vacuous")
        result_band = 1 if projection.band == 1 else 4
        projection = replace(
            projection,
            findings=tuple(retained_findings),
            counts=tuple(
                (name, sum(row.verdict == name for row in retained_findings)) for name in vocabulary
            ),
            band=result_band,
            acceptance_ready=False,
            semantic_decision="refuse" if result_band == 1 else "indeterminate",
        )

    coverage = {
        str(fact_type.get("id")): CoverageEntry(
            declared=(
                "declared" if str(fact_type.get("id")) in population.covers else "undeclared"
            ),
            facts=len(population.facts.get(str(fact_type.get("id")), [])),
        )
        for fact_type in model.fact_types
    }
    return CheckReport(
        verdicts=verdicts,
        derivations=derivations,
        coverage=coverage,
        phase1_trace=_compatibility_trace(verdicts, trace_rows, derivations, coverage),
        phase1_refusals=tuple(refusal_rows),
        snapshot_projection=projection,
        assurance_input_scope_ids=adapted.observation.applicable_scope_ids,
    )


def _observe_phase1_compatibility(
    constraint: dict[str, Any],
    ref: str,
    model: Model,
    population: _FactView,
    fact_type: dict[str, Any] | None,
    rows: list[tuple[SliceInput, SliceVerdict]],
    refusals: list[tuple[str, str]],
    aliases: dict[str, str],
) -> None:
    """Retain the old evidence trace without giving it snapshot authority."""
    value = adapt_phase1_slice(model, population, constraint, fact_type, ref)
    if value is not None:
        verdict = phase1_decide(value)
        if verdict is not None:
            rows.append((value, verdict))
            aliases[ref] = {
                "mandatory": "phase1-inline",
                "frequency": "phase1-internal",
                "textual-refusal": "phase1",
            }[value.family]
            return
    reason = phase1_refusal_reason(model, population, constraint, fact_type, ref)
    if reason is not None:
        refusals.append((ref, reason))
        record_branch(f"applicability:refusal:n-a:{reason}")


def _plain_projected_witness(constraint_type: str, witness: Sequence[Any]) -> list[Any]:
    """Translate the uniform semantic witness into the existing public shapes."""
    rows = [dict(row) if isinstance(row, dict) else list(row) for row in witness]
    if constraint_type in {"mandatory", "mandatory-disjunctive", "value", "cardinality"}:
        return [row[0] for row in rows]
    return rows


def _correspondence_message(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    finding: Any,
    witness: list[Any],
    model: Model,
    population: _FactView,
) -> str:
    """Render the non-semantic envelope from one authoritative finding.

    This function may inspect admitted data to describe a result; it never
    chooses a verdict, reason, witness, count, or band.
    """
    family = finding.constraint_type
    verdict = finding.verdict
    reason = finding.reason_code
    scope_id = finding.scope_id

    if verdict == "vacuous":
        if scope_id.endswith(":coverage-omission"):
            subjects = _scope_fact_types(constraint, family, model, fact_type)
            return verbalize.coverage_omission_message(
                [subject for subject in subjects if subject not in population.covers]
            )
        if ":no-observable-subjects" in scope_id:
            subject = str(constraint.get("object_type") or constraint.get("supertype") or family)
            return verbalize.no_observable_subjects_message(subject)
        if scope_id.endswith(":zero-row-join"):
            sequences = _joining_subject_sequences(constraint, family, fact_type)
            labels = [", ".join(_ref_labels(sequence)) for sequence in sequences]
            return verbalize.no_joined_rows_message(labels)
        return verbalize.vacuous_message(_scope_fact_types(constraint, family, model, fact_type))

    if verdict == "unchecked":
        consequent = constraint.get("consequent")
        has_exists_consequent = (
            isinstance(consequent, Mapping) and isinstance(consequent.get("exists"), Mapping)
        )
        if family == "guarded" and has_exists_consequent and reason == "guarded-exists-coverage-missing":
            exists = consequent.get("exists") or {}
            missing = list(
                dict.fromkeys(
                    str(atom.get("fact_type"))
                    for atom in exists.get("atoms") or []
                    if isinstance(atom, Mapping)
                    and str(atom.get("fact_type")) not in population.covers
                )
            )
            return (
                "Existential consequent was NOT evaluated — source population coverage is "
                f"missing for witness relation(s): {', '.join(missing)}."
            )
        if family == "guarded" and reason == "reference-join-work-limit":
            return (
                "Guarded join was not evaluated: reference combined work ceiling 100000 exceeded."
            )
        if family == "guarded" and has_exists_consequent and reason == "guarded-exists-work-limit":
            return (
                "Existential consequent was NOT evaluated — deterministic work ceiling "
                f"{200_000} was exceeded."
            )
        if (
            family == "guarded"
            and has_exists_consequent
            and isinstance(reason, str)
            and reason.startswith("term:")
        ):
            return (
                "Existential consequent was NOT evaluated because a reached candidate's "
                f"exact term is unavailable: {reason}; partial witnesses are suppressed."
            )
        if reason == "textual-not-mechanical":
            return verbalize.textual_unchecked_message(str(constraint.get("expression", "")))
        if reason == "family-unimplemented":
            return verbalize.unchecked_message(family)
        if reason == "join-disconnected":
            return verbalize.join_disconnected_message(
                _scope_fact_types(constraint, family, model, fact_type)
            )
        if reason == "join-anchor-ambiguous":
            return (
                "Shared-entity join is ambiguous — reported as unchecked until "
                "an explicit join mapping selects one."
            )
        if reason == "ring-not-binary":
            return verbalize.ring_not_binary_message(
                str(constraint.get("variant")),
                str((fact_type or {}).get("id")),
                len((fact_type or {}).get("roles") or []),
            )
        if reason == "role-unresolved":
            return verbalize.unresolved_role_message(
                str(constraint.get("role")), str((fact_type or {}).get("id"))
            )
        if reason == "subject-type-ambiguous":
            refs = list(constraint.get("role_refs") or [])
            return verbalize.disjunctive_subject_type_message(
                _ref_labels(refs),
                [
                    str(_role_object_type(model, str(ref.get("fact_type")), str(ref.get("role"))))
                    for ref in refs
                ],
            )
        if reason == "xor-disjunctive-undefined":
            sequences = [list(row or []) for row in constraint.get("role_seqs") or []]
            return verbalize.exclusive_or_multirole_unchecked_message(
                [", ".join(_ref_labels(row)) for row in sequences]
            )
        if reason == "no-reference-clock":
            return verbalize.value_comparison_unchecked_message(
                time_relative_operand(constraint, fact_type) or "current time"
            )
        if family == "guarded" and reason in {
            "values-not-comparable",
            "literal-type-ambiguous",
        }:
            atoms = [dict(atom) for atom in constraint.get("antecedent") or []]
            bindings = _guarded_bindings(atoms, population)
            comparison = (constraint.get("consequent") or {}).get("comparison") or {}
            operator = str(comparison.get("operator"))
            left = comparison.get("left")
            right = comparison.get("right")
            variables = (_guarded_variable(left), _guarded_variable(right))
            primitives_by_variable = _guarded_variable_primitives(atoms, model)
            primitives = (
                primitives_by_variable.get(variables[0]) if variables[0] is not None else None,
                primitives_by_variable.get(variables[1]) if variables[1] is not None else None,
            )
            comparison_primitives = [primitives[0], primitives[1]]
            prepared = [left, right]
            if variables[0] is None and variables[1] is not None:
                prepared[0] = _literal(left, primitives[1], legacy=False)
                comparison_primitives[0] = primitives[1]
            if variables[1] is None and variables[0] is not None:
                prepared[1] = _literal(right, primitives[0], legacy=False)
                comparison_primitives[1] = primitives[0]
            if reason == "literal-type-ambiguous":
                literal = left if prepared[0] is _INVALID_LITERAL else right
                primitive = primitives[1] if prepared[0] is _INVALID_LITERAL else primitives[0]
                return verbalize.guarded_literal_unchecked_message(
                    literal, primitive, len(bindings)
                )
            undecidable: list[dict[str, Any]] = []
            offending: list[dict[str, Any]] = []
            for binding in bindings:
                values = [
                    binding[variable] if variable is not None else value
                    for variable, value in zip(variables, prepared, strict=True)
                ]
                outcome = _compare(
                    values[0],
                    operator,
                    values[1],
                    comparison_primitives[0],
                    comparison_primitives[1],
                )
                if outcome is None:
                    undecidable.append(binding)
                elif not outcome:
                    offending.append(binding)
            return verbalize.guarded_not_comparable_message(
                operator, len(bindings), undecidable, offending
            )
        if reason == "values-not-comparable" and family == "value-comparison":
            label_a, label_b, pairs = _value_comparison_message_inputs(
                constraint, fact_type, model, population
            )
            operator = str(constraint.get("operator"))
            undecidable = [
                pair for pair in pairs if _compare(pair[0], operator, pair[1], None, None) is None
            ]
            offending = [
                pair for pair in pairs if _compare(pair[0], operator, pair[1], None, None) is False
            ]
            return verbalize.values_not_comparable_message(
                label_a, operator, label_b, undecidable, offending
            )
        if reason == "bound-type-mismatch" and family == "value":
            object_type = str(constraint.get("object_type"))
            role_ref = constraint.get("role_ref")
            if isinstance(role_ref, dict):
                values = [
                    value
                    for (value,) in _project(
                        population,
                        str(role_ref.get("fact_type")),
                        [str(role_ref.get("role"))],
                    )
                ]
            else:
                values = _instance_values_of(object_type, model, population)
            ranges = list(constraint.get("ranges") or [])
            if not ranges:
                ranges = [constraint.get("range") or {}]
            primitive = resolve_primitive(object_type, model)
            undecidable: list[Any] = []
            offending: list[Any] = []
            for value in values:
                outcomes = [_in_range(value, bounds, primitive) for bounds in ranges]
                if any(outcome is True for outcome in outcomes):
                    continue
                if any(outcome is None for outcome in outcomes):
                    undecidable.append(value)
                else:
                    offending.append(value)
            return verbalize.bound_type_mismatch_message(
                object_type, ranges, undecidable, offending
            )
        if reason == "partition-asserts-nothing":
            return verbalize.subtype_partition_no_assertion_message(
                str(constraint.get("supertype")),
                [str(row) for row in constraint.get("subtypes") or []],
            )
        if reason == "subtype-derivation-only":
            object_types = {str(row.get("id")): row for row in model.object_types}
            for subtype in [str(row) for row in constraint.get("subtypes") or []]:
                declaration = object_types.get(subtype, {})
                if declaration.get("derivation") in {"derived", "semiderived"}:
                    return verbalize.subtype_partition_unchecked_message(
                        subtype, str(declaration.get("derivation_rule", ""))
                    )
        return f"Constraint {family!r} was NOT evaluated — reported as unchecked: {reason}."

    violated = verdict in {"fail", "warning"}
    if family == "guarded" and scope_id.endswith(":clean-zero-bindings"):
        consequent = constraint.get("consequent") or {}
        kind = next(
            (name for name in ("comparison", "atom", "absence", "exists") if name in consequent),
            "guarded",
        )
        return verbalize.guarded_zero_bindings_message(kind)
    if family == "ring":
        variant = str(constraint.get("variant"))
        return verbalize.ring_message(
            variant,
            str((fact_type or {}).get("id")),
            [(variant, tuple(row)) for row in witness] if violated else [],
        )
    if family == "mandatory":
        role = str(constraint.get("role"))
        object_type = _role_object_type(model, str((fact_type or {}).get("id")), role) or role
        return verbalize.mandatory_message(
            object_type, role, str((fact_type or {}).get("id")), witness if violated else []
        )
    if family == "mandatory-disjunctive":
        refs = list(constraint.get("role_refs") or [])
        first = refs[0] if refs else {}
        object_type = (
            _role_object_type(model, str(first.get("fact_type")), str(first.get("role")))
            or "object"
        )
        return verbalize.mandatory_disjunctive_message(
            object_type, _ref_labels(refs), witness if violated else []
        )
    if family == "uniqueness":
        if fact_type is not None:
            roles = [str(row) for row in constraint.get("roles") or []]
            groups = _identity_counts(
                tuple(fact[role] for role in roles)
                for fact in population.facts.get(str(fact_type.get("id")), [])
                if all(role in fact for role in roles)
            )
            offending = [(tuple(value), count) for value, count in groups.values() if count > 1]
            return verbalize.uniqueness_message(roles, str(fact_type.get("id")), offending)
        refs = list(constraint.get("role_refs") or [])
        groups = _identity_counts(_join_rows(model, population, refs))
        offending = [(tuple(value), count) for value, count in groups.values() if count > 1]
        return verbalize.uniqueness_external_message(_ref_labels(refs), offending)
    if family == "value":
        subject = str(constraint.get("object_type"))
        offending = witness if violated else []
        if constraint.get("allowed") is not None:
            return verbalize.value_enum_message(
                subject, list(constraint.get("allowed") or []), offending
            )
        if constraint.get("ranges") is not None:
            return verbalize.value_ranges_message(
                subject, list(constraint.get("ranges") or []), offending
            )
        bounds = constraint.get("range") or {}
        return verbalize.value_range_message(
            subject, bounds.get("min"), bounds.get("max"), offending
        )
    if family == "frequency":
        bound = constraint.get("bound") or {}
        if fact_type is not None:
            roles = [str(row) for row in constraint.get("roles") or []]
            values = _project(population, str(fact_type.get("id")), roles)
            subject = f"{', '.join(roles)} in {fact_type.get('id')}"
        else:
            refs = list(constraint.get("role_refs") or [])
            values = _join_rows(model, population, refs)
            subject = ", ".join(_ref_labels(refs))
        groups = _identity_counts(values)
        keys = {_identity_key(tuple(row)) for row in witness}
        offending = [
            (tuple(value), count) for identity, (value, count) in groups.items() if identity in keys
        ]
        return verbalize.frequency_message(subject, bound.get("min"), bound.get("max"), offending)
    if family in {"subset", "equality", "exclusion"}:
        seq_a = list(
            constraint.get("subset_role_seq")
            if family == "subset"
            else constraint.get("role_seq_a") or []
        )
        seq_b = list(
            constraint.get("superset_role_seq")
            if family == "subset"
            else constraint.get("role_seq_b") or []
        )
        tuples = [tuple(row) for row in witness] if violated else []
        if family == "subset":
            return verbalize.subset_message(_ref_labels(seq_a), _ref_labels(seq_b), tuples)
        if family == "exclusion":
            return verbalize.exclusion_message(_ref_labels(seq_a), _ref_labels(seq_b), tuples)
        actual_a = _IdentitySet(_role_seq_tuples(model, population, seq_a))
        only_a = [row for row in tuples if row in actual_a]
        only_b = [row for row in tuples if row not in actual_a]
        return verbalize.equality_message(_ref_labels(seq_a), _ref_labels(seq_b), only_a, only_b)
    if family == "exclusive-or":
        sequences = [list(row or []) for row in constraint.get("role_seqs") or []]
        labels = [", ".join(_ref_labels(row)) for row in sequences]
        if all(len(row) == 1 for row in sequences):
            refs = [row[0] for row in sequences]
            first = refs[0] if refs else {}
            object_type = (
                _role_object_type(model, str(first.get("fact_type")), str(first.get("role")))
                or "object"
            )
            populations = [
                _IdentitySet(_role_seq_tuples(model, population, row)) for row in sequences
            ]
            both: list[Any] = []
            neither: list[Any] = []
            for row in witness if violated else []:
                value = row[0] if isinstance(row, list) and len(row) == 1 else row
                if sum((value,) in values for values in populations) > 1:
                    both.append(value)
                else:
                    neither.append(value)
            return verbalize.exclusive_or_message(object_type, labels, both, neither)
        return verbalize.exclusive_or_exclusion_violated_message(
            labels, [tuple(row) for row in witness]
        )
    if family == "value-comparison":
        left = constraint.get("role_a")
        right = constraint.get("role_b")
        labels = _ref_labels([left, right]) if isinstance(left, dict) else [str(left), str(right)]
        return verbalize.value_comparison_message(
            labels[0],
            str(constraint.get("operator")),
            labels[1],
            [tuple(row) for row in witness] if violated else [],
        )
    if family == "cardinality":
        bounds = constraint.get("bound") or {}
        if constraint.get("scope") == "object":
            object_type = str(constraint.get("object_type"))
            subject = f"{object_type} instance"
            count = len(_instances_of(object_type, model, population))
        else:
            role_ref = constraint.get("role_ref") or {}
            fact_type_id = str(role_ref.get("fact_type"))
            role_name = str(role_ref.get("role"))
            subject = f"distinct player of {fact_type_id}.{role_name}"
            count = len(_IdentitySet(_project(population, fact_type_id, [role_name])))
        return verbalize.cardinality_message(
            subject, bounds.get("min"), bounds.get("max"), count, violated
        )
    if family == "subtype-partition":
        subtypes = [str(row) for row in constraint.get("subtypes") or []]
        member_sets = {subtype: _instances_of(subtype, model, population) for subtype in subtypes}
        values = [row[0] for row in witness] if violated else []
        both = [
            value
            for value in values
            if constraint.get("exclusive")
            and sum(value in members for members in member_sets.values()) > 1
        ]
        neither = [value for value in values if value not in both]
        return verbalize.subtype_partition_message(
            str(constraint.get("supertype")),
            subtypes,
            both,
            neither,
        )
    if family == "guarded":
        kind = next(
            (
                key
                for key in ("comparison", "atom", "absence", "exists")
                if key in (constraint.get("consequent") or {})
            ),
            "consequent",
        )
        from gnd.terms import is_temporal_node, temporal_nodes

        if any(is_temporal_node(node) for _, node in temporal_nodes(constraint.get("consequent"))):
            return verbalize.temporal_guarded_message(kind, witness if violated else [])
        bindings = _guarded_bindings(list(constraint.get("antecedent") or []), population)
        if model.reference_populations and len(bindings) > 100_000:
            from gnd.correspondence import ReferenceJoinLimit

            raise ReferenceJoinLimit("binding producer escaped reference work budget")
        return verbalize.guarded_message(kind, len(bindings), witness if violated else [])
    return verbalize.constraint_message(
        family,
        verdict,
        fact_type_id=str((fact_type or {}).get("id")) or None,
        detail=(f"witness={witness!r}" if witness else ""),
    )


def _value_comparison_message_inputs(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    model: Model,
    population: _FactView,
) -> tuple[str, str, list[tuple[Any, Any]]]:
    """Presentation labels and admitted pairs for a value-comparison finding."""
    left = constraint.get("role_a")
    right = constraint.get("role_b")
    if fact_type is None:
        refs = [dict(left or {}), dict(right or {})]
        labels = _ref_labels(refs)
        if refs[0].get("fact_type") == refs[1].get("fact_type"):
            pairs = _project(
                population,
                str(refs[0].get("fact_type")),
                [str(refs[0].get("role")), str(refs[1].get("role"))],
            )
        else:
            pairs = _join_rows(model, population, refs)
        return labels[0], labels[1], [(row[0], row[1]) for row in pairs]

    role_names = {str(role.get("role_name")) for role in fact_type.get("roles") or []}
    operands = [left, right]
    labels: list[str] = []
    pairs: list[tuple[Any, Any]] = []
    for operand in operands:
        if isinstance(operand, str) and operand in role_names:
            labels.append(operand)
        elif isinstance(operand, dict) and operand.get("role") in role_names:
            labels.append(str(operand.get("role")))
        else:
            labels.append(str(operand.get("literal") if isinstance(operand, dict) else operand))
    for fact in population.facts.get(str(fact_type.get("id")), []):
        values: list[Any] = []
        for operand in operands:
            role = (
                str(operand.get("role"))
                if isinstance(operand, dict) and operand.get("role") in role_names
                else operand
                if isinstance(operand, str) and operand in role_names
                else None
            )
            if role is not None:
                if role not in fact:
                    values = []
                    break
                values.append(fact[role])
            else:
                values.append(operand.get("literal") if isinstance(operand, dict) else operand)
        if len(values) == 2:
            pairs.append((values[0], values[1]))
    return labels[0], labels[1], pairs


def _compatibility_trace(
    verdicts: list[ConstraintVerdict],
    rows: list[tuple[SliceInput, SliceVerdict]],
    derivations: list[DerivationVerdict],
    coverage: dict[str, CoverageEntry],
) -> Phase1Trace | None:
    """The trace, or None when the checked model is not wholly inside the slice.

    "Wholly" is measured, not assumed: one constraint the slice refused, one
    derivation obligation, or an empty model all withhold the trace, because
    each of them is a result-producing branch the slice did not decide.
    """
    if not verdicts or derivations or len(rows) != len(verdicts):
        return None
    # A14.1 admits at most three constraints, and the in-scope predicate sees
    # one SliceInput at a time, so the count is decided here -- the one place
    # that sees them all (review finding R4: a four-constraint model carried
    # the whole-result claim before this gate existed).
    if len(verdicts) > MAX_SLICE_CONSTRAINTS:
        return None
    return Phase1Trace(
        rows=tuple(rows),
        coverage=tuple(
            (fact_type_id, entry.declared, entry.facts) for fact_type_id, entry in coverage.items()
        ),
        applicable=len(verdicts),
        slice_decided=len(rows),
    )


#: Families whose subjects are an OBJECT TYPE's population rather than a fact
#: type's, and which therefore can reach evaluation with an empty scope. The
#: field naming the subject differs per family, hence the mapping.
_OBJECT_TYPE_SCOPED = {
    "value": "object_type",
    "cardinality": "object_type",
    "subtype-partition": "supertype",
}


def _no_observable_subjects_message(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    population: Population,
) -> str | None:
    """The vacuity message for a constraint whose subject universe is empty.

    Returns ``None`` — meaning "not vacuous, keep the evaluated verdict" —
    whenever the universe holds anything, or whenever the family's subject is
    not an object-type population at all. The universe is
    :func:`_instance_values_of`, the same one walk the family checks read, so
    this can never disagree with what was actually evaluated.
    """
    subject_field = _OBJECT_TYPE_SCOPED.get(constraint_type)
    if subject_field is None:
        return None
    object_type_id = constraint.get(subject_field)
    if object_type_id is None:
        return None
    if _instance_values_of(str(object_type_id), model, population):
        return None
    return verbalize.no_observable_subjects_message(str(object_type_id))


class _JoinSubjectRow(NamedTuple):
    """One family's join-scoped subject description (F-05).

    Every field is required, so a future edit that adds a family but forgets the
    ``quantifier`` fails at table-construction time (a positional NamedTuple
    argument), never with a silent default — the quantifier is DATA, not a
    comment that a later edit can leave stale.
    """

    #: The constraint fields naming this family's subject role sequence(s).
    subject_fields: tuple[str, ...]
    #: ``any`` -> vacuous when the (single) subject sequence yields zero rows;
    #: ``all`` -> vacuous only when EVERY subject sequence yields zero rows.
    quantifier: Literal["any", "all"]
    #: True when the subject fields are single refs assembled into ONE combined
    #: sequence evaluated by a single join (cross-fact ``value-comparison``,
    #: whose cross form is one ``_join_rows([ref_a, ref_b])`` at checker.py:1695).
    combined: bool
    #: Why this family is in the table and with this quantifier.
    reason: str


#: Families that can reach `pass` over a ZERO-ROW JOIN and must be downgraded to
#: `vacuous` (F-05). The table matches the task-1 probe sweep EXACTLY — a family
#: is present iff its probe showed `pass` over a zero-row join. Two deliberate
#: absences, each with the population that established it:
#:
#: - `subset`: ABSENT. `∅ ⊆ X → pass` (checker.py:1242, offending = sub - sup)
#:   is a ratified decided containment — Halpin, and 01.1-VERIFICATION.md's
#:   residual-routes table — proven by the `subset_subject_zero_row` probe. The
#:   SUPERSET-side zero-row case stays `fail`. Adding `subset` here would convert
#:   the legitimate ∅⊆X `pass` into `vacuous` on the multi-fact path while a
#:   single-fact empty subset stayed `pass` — a projection-vs-join split on
#:   identical state, which is the very F-05 shape and a D-13 semantics change.
#:   Plan 03's degeneracy gate is made positive instead of waiting for this
#:   `vacuous`.
#: - `exclusive-or`: ABSENT. The multi-role branch returns `unchecked`
#:   (`xor-disjunctive-undefined`, checker.py) before it can reach `pass`; the
#:   single-role branch quantifies over `_instances_of`, an object-type universe,
#:   not a join.
_JOIN_SUBJECT_SEQS: dict[str, _JoinSubjectRow] = {
    "uniqueness": _JoinSubjectRow(
        ("role_refs",),
        "any",
        False,
        "external UC subject is one joined sequence; an empty join has no tuples "
        "to check for duplicates (top-level form only — inline uses `roles`)",
    ),
    "frequency": _JoinSubjectRow(
        ("role_refs",),
        "any",
        False,
        "external frequency subject is one joined sequence; an empty join has no "
        "occurring groups, so a `min` bound is silently never violated",
    ),
    "value-comparison": _JoinSubjectRow(
        ("role_a", "role_b"),
        "any",
        True,
        "the cross form joins [role_a, role_b] as ONE combined sequence "
        "(checker.py:1695); an empty join has no pairs to compare (C8)",
    ),
    "equality": _JoinSubjectRow(
        ("role_seq_a", "role_seq_b"),
        "all",
        False,
        "equality is decided when either side has rows (only_a/only_b make it "
        "`fail`); vacuous only when BOTH joins are empty",
    ),
    "exclusion": _JoinSubjectRow(
        ("role_seq_a", "role_seq_b"),
        "all",
        False,
        "one empty side is a real decision (∅ ∩ X = ∅ → `pass`, 01.1-ratified); "
        "vacuous only when BOTH joins are empty",
    ),
}


def _joining_subject_sequences(
    constraint: dict[str, Any],
    constraint_type: str,
    fact_type: dict[str, Any] | None,
) -> list[list[dict[str, Any]]]:
    """The constraint's SUBJECT role sequences, per :data:`_JOIN_SUBJECT_SEQS`.

    Not every sequence a constraint mentions — only the ones whose emptiness means
    "no subjects". A ``combined`` row assembles its single refs into ONE sequence
    (the cross-fact ``value-comparison`` join); a non-combined row yields one
    sequence per subject field. Inline forms carry no subject field here (inline
    uniqueness/frequency use ``roles``), so they return nothing and never trip the
    join-vacuity clause.
    """
    row = _JOIN_SUBJECT_SEQS.get(constraint_type)
    if row is None:
        return []
    if row.combined:
        sequence = [
            ref
            for subject_field in row.subject_fields
            if isinstance((ref := constraint.get(subject_field)), dict)
        ]
        return [sequence] if sequence else []
    sequences: list[list[dict[str, Any]]] = []
    for subject_field in row.subject_fields:
        value = constraint.get(subject_field)
        if isinstance(value, list):
            sequence = [ref for ref in value if isinstance(ref, dict)]
            if sequence:
                sequences.append(sequence)
    return sequences


def _no_joined_rows_message(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    population: Population,
    fact_type: dict[str, Any] | None,
) -> str | None:
    """The vacuity message for a join-scoped constraint whose JOIN yielded zero
    rows, or ``None`` — "keep the evaluated verdict" — when a required subject
    sequence produced rows.

    At least one subject sequence must span MORE THAN ONE fact type: this clause
    is about the JOIN universe, and single-fact emptiness alone is
    :func:`_vacuity_message`'s job, decided before evaluation. Every subject
    sequence is evaluated with :func:`_role_seq_tuples` — the SAME function the
    family check ran, never a re-implemented join — so this can never disagree with
    what was actually evaluated. The row's ``quantifier`` decides ANY vs ALL
    emptiness (see :data:`_JOIN_SUBJECT_SEQS`):

    - ``any`` families carry ONE subject sequence, and it is a join — vacuous when
      that join is empty.
    - ``all`` families (``equality``, ``exclusion``) carry two sides — vacuous only
      when EVERY subject sequence is empty. A NON-empty single-fact projection side
      keeps the constraint decided (``∅ ∩ X = ∅`` is a real ``pass``), so the
      single-fact side is counted for emptiness even though it is skipped for the
      "is this a join at all?" gate. Dropping it before the ALL check would demote
      a decided one-empty-side ``pass`` to vacuity — the exact over-correction the
      ``exclusion_one_side_zero_row`` control guards against.
    """
    row = _JOIN_SUBJECT_SEQS.get(constraint_type)
    if row is None:
        return None
    sequences = _joining_subject_sequences(constraint, constraint_type, fact_type)
    spans_join = [
        len({str(ref.get("fact_type")) for ref in sequence}) > 1 for sequence in sequences
    ]
    if not any(spans_join):
        return None
    empties = [not _role_seq_tuples(model, population, sequence) for sequence in sequences]
    vacuous = any(empties) if row.quantifier == "any" else all(empties)
    if not vacuous:
        return None
    labels = [
        ", ".join(_ref_labels(sequence))
        for sequence, joined, empty in zip(sequences, spans_join, empties, strict=True)
        if joined and empty
    ]
    return verbalize.no_joined_rows_message(labels)


def _is_implemented(constraint: dict[str, Any], fact_type: dict[str, Any] | None) -> bool:
    constraint_type = constraint.get("type")
    if constraint_type not in IMPLEMENTED_FAMILIES:
        return False
    if constraint_type == "anchored":
        return fact_type is not None
    if constraint_type == "uniqueness":
        if fact_type is not None:
            return isinstance(constraint.get("roles"), list)
        return constraint.get("scope") == "external" and bool(constraint.get("role_refs"))
    if constraint_type == "mandatory":
        return fact_type is not None and constraint.get("role") is not None
    if constraint_type == "value":
        forms = [key for key in ("allowed", "range", "ranges") if constraint.get(key) is not None]
        return constraint.get("object_type") is not None and len(forms) == 1
    if constraint_type == "mandatory-disjunctive":
        return bool(constraint.get("role_refs"))
    if constraint_type == "frequency":
        return bool(constraint.get("bound")) and (
            bool(constraint.get("roles")) or bool(constraint.get("role_refs"))
        )
    if constraint_type == "subset":
        return bool(constraint.get("subset_role_seq")) and bool(constraint.get("superset_role_seq"))
    if constraint_type in ("equality", "exclusion"):
        return bool(constraint.get("role_seq_a")) and bool(constraint.get("role_seq_b"))
    if constraint_type == "exclusive-or":
        return bool(constraint.get("role_seqs"))
    if constraint_type == "ring":
        return fact_type is not None and constraint.get("variant") in _RING_VARIANTS
    if constraint_type == "value-comparison":
        return (
            constraint.get("operator") is not None
            and constraint.get("role_a") is not None
            and constraint.get("role_b") is not None
        )
    if constraint_type == "guarded":
        antecedent = constraint.get("antecedent")
        consequent = constraint.get("consequent")
        exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
        exists_atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
        return (
            isinstance(antecedent, list)
            and bool(antecedent)
            and all(atom_has_bind(atom) for atom in antecedent)
            and isinstance(consequent, dict)
            and sum(key in consequent for key in ("comparison", "atom", "absence", "exists")) == 1
            and all(
                isinstance(consequent.get(key), dict)
                for key in ("comparison", "atom", "absence", "exists")
                if key in consequent
            )
            and (
                "exists" not in consequent
                or (
                    isinstance(exists_atoms, list)
                    and bool(exists_atoms)
                    and all(atom_has_bind(atom) for atom in exists_atoms)
                )
            )
        )
    if constraint_type == "subtype-partition":
        return constraint.get("supertype") is not None and bool(constraint.get("subtypes"))
    # cardinality
    if not constraint.get("bound"):
        return False
    if constraint.get("scope") == "object":
        return constraint.get("object_type") is not None and constraint.get("role_ref") is None
    if constraint.get("scope") == "role":
        return constraint.get("role_ref") is not None and constraint.get("object_type") is None
    return False


# --- scope / vacuity ---


def _constraint_role_refs(constraint: dict[str, Any]):
    """Yield every ``{fact_type, role}`` reference a constraint carries."""
    for reference_field in (
        "role_refs",
        "subset_role_seq",
        "superset_role_seq",
        "role_seq_a",
        "role_seq_b",
    ):
        for ref in constraint.get(reference_field) or []:
            if isinstance(ref, dict):
                yield ref
    for sequence in constraint.get("role_seqs") or []:
        for ref in sequence or []:
            if isinstance(ref, dict):
                yield ref
    for reference_field in ("role_ref", "role_a", "role_b"):
        ref = constraint.get(reference_field)
        if isinstance(ref, dict):
            yield ref


def _scope_fact_types(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    fact_type: dict[str, Any] | None,
) -> list[str]:
    """The fact types a constraint ranges over (for vacuity detection)."""
    if fact_type is not None:
        return [str(fact_type.get("id"))]
    if constraint_type == "guarded":
        antecedent = constraint.get("antecedent")
        if not isinstance(antecedent, list):
            return []
        referenced = [
            str(atom.get("fact_type"))
            for atom in antecedent
            if isinstance(atom, dict) and atom.get("fact_type") is not None
        ]
        return list(dict.fromkeys(referenced))
    referenced = [str(ref.get("fact_type")) for ref in _constraint_role_refs(constraint)]
    if referenced:
        return list(dict.fromkeys(referenced))
    if constraint_type in ("value", "cardinality"):
        target = constraint.get("object_type")
        return [
            str(ft.get("id"))
            for ft in model.fact_types
            if any(role.get("object_type") == target for role in ft.get("roles") or [])
        ]
    if constraint_type == "subtype-partition":
        targets = {constraint.get("supertype"), *(constraint.get("subtypes") or [])}
        return [
            str(ft.get("id"))
            for ft in model.fact_types
            if any(role.get("object_type") in targets for role in ft.get("roles") or [])
        ]
    return []


#: Families that quantify universally over object-type instances: for these,
#: omitting a subject fact type from ``covers`` makes the verdict vacuous even
#: when facts are present (D-12 second clause).
_MANDATORY_RELEVANT = {"mandatory", "mandatory-disjunctive"}


def _vacuity_message(
    constraint_type: str, scope: list[str], population: Population
) -> tuple[str, str] | None:
    """The vacuity branch identity and rendered message, or None.

    Two D-12 clauses:
    - Coverage omission: a mandatory-relevant constraint whose subject fact
      type is absent from ``covers`` cannot be evaluated against a population
      that does not claim completeness for it.
    - Empty subject: every subject fact type carries zero facts (declared or
      not — an omitted-and-empty fact type must never yield a silent pass).

    An EMPTY scope is not decided here. "No fact type ranges over this
    constraint" is not the same claim as "this constraint has no subjects": a
    ``value`` constraint on an object type no fact type mentions can still be
    populated by an ``instances:`` roster, and a ``cardinality`` ``min`` bound is
    genuinely decided — and violated — by a universe of zero. Answering vacuous
    here would convert both of those into exit 2. The empty-scope case is
    therefore settled AFTER evaluation, in :func:`_verdict_for`, where the only
    verdict it can overturn is a ``pass`` (F-02).
    """
    if not scope:
        return None
    if constraint_type in _MANDATORY_RELEVANT:
        omitted = [ft for ft in scope if ft not in population.covers]
        if omitted:
            return (
                "applicability:vacuity:n-a:coverage-omission",
                verbalize.coverage_omission_message(omitted),
            )
    empty = [not population.facts.get(fact_type_id) for fact_type_id in scope]
    if (constraint_type == "guarded" and any(empty)) or all(empty):
        scope_id = (
            "applicability:vacuity:guarded:empty-subject-any"
            if constraint_type == "guarded"
            else "applicability:vacuity:n-a:empty-subject-all"
        )
        return scope_id, verbalize.vacuous_message(scope)
    return None


# --- shared machinery: projection, join, instance derivation ---


class JoinDisconnectedError(Exception):
    """The referenced fact types cannot be chained through shared anchor object
    types — evaluating would silently degrade to a cross join and produce
    provably wrong counts/verdicts (CR-02). Surfaced as an ``unchecked``
    verdict by :func:`_verdict_for`, never silently evaluated.
    """

    def __init__(self, fact_type_ids: list[str]):
        self.fact_type_ids = list(fact_type_ids)
        super().__init__(
            "role references span fact types with no shared anchor object type: "
            + ", ".join(self.fact_type_ids)
        )


class JoinAmbiguousError(Exception):
    """A fact type offers multiple same-type candidates for one join anchor."""

    def __init__(self, fact_type_id: str, object_type_id: str, role_names: list[str]):
        self.fact_type_id = fact_type_id
        self.object_type_id = object_type_id
        self.role_names = list(role_names)
        super().__init__(
            f"{fact_type_id} has ambiguous {object_type_id} anchors: {', '.join(role_names)}"
        )


def _fact_type_by_id(model: Model, fact_type_id: str) -> dict[str, Any] | None:
    for fact_type in model.fact_types:
        if str(fact_type.get("id")) == fact_type_id:
            return fact_type
    return None


def _role_object_type(model: Model, fact_type_id: str, role_name: str) -> str | None:
    fact_type = _fact_type_by_id(model, fact_type_id)
    for role in (fact_type or {}).get("roles") or []:
        if role.get("role_name") == role_name:
            return str(role.get("object_type"))
    return None


def _project(population: Population, fact_type_id: str, role_names: list[str]) -> list[tuple]:
    """Role-sequence projection over one fact type, preserving duplicates."""
    return [
        tuple(fact[role] for role in role_names)
        for fact in population.facts.get(str(fact_type_id), [])
        if all(role in fact for role in role_names)
    ]


def _identity_key(value: Any) -> tuple[Any, ...]:
    """Canonical ORM scalar/tuple identity, independent of Python coercions.

    Booleans are a separate scalar domain from numbers even though Python makes
    ``True == 1`` and gives them the same hash. Integers and floats share the
    numeric domain because Float/Number roles deliberately accept either JSON
    rendering (``1`` and ``1.0``).
    """
    if isinstance(value, bool):
        return ("boolean", value)
    if isinstance(value, (int, float)):
        return ("number", value)
    if isinstance(value, str):
        return ("string", value)
    if value is None:
        return ("null",)
    if isinstance(value, tuple):
        return ("tuple", *(_identity_key(item) for item in value))
    return (f"python:{type(value).__qualname__}", repr(value))


class _IdentitySet(AbstractSet[Any]):
    """Set semantics over :func:`_identity_key`, yielding original values."""

    def __init__(self, values: Iterable[Any] = ()):
        self._values = {_identity_key(value): value for value in values}

    def __contains__(self, value: object) -> bool:
        return _identity_key(value) in self._values

    def __iter__(self):
        return iter(self._values.values())

    def __len__(self) -> int:
        return len(self._values)


def _identity_counts(values: Iterable[Any]) -> dict[tuple[Any, ...], tuple[Any, int]]:
    counts: dict[tuple[Any, ...], tuple[Any, int]] = {}
    for value in values:
        identity = _identity_key(value)
        original, count = counts.get(identity, (value, 0))
        counts[identity] = (original, count + 1)
    return counts


def _join_rows(
    model: Model, population: Population, role_refs: list[dict[str, Any]]
) -> list[tuple]:
    """Join the referenced fact types on shared-object-type anchor roles.

    Returns one tuple per joined row, holding the referenced role values in
    ``role_refs`` order. Anchor roles are the non-referenced roles of each fact
    type; rows join when anchor values of the same object type are equal (the
    shared-entity join used by external uniqueness/frequency constraints).
    """
    by_fact_type: dict[str, list[tuple[int, str]]] = {}
    order: list[str] = []
    for slot, ref in enumerate(role_refs):
        fact_type_id = str(ref.get("fact_type"))
        if fact_type_id not in by_fact_type:
            by_fact_type[fact_type_id] = []
            order.append(fact_type_id)
        by_fact_type[fact_type_id].append((slot, str(ref.get("role"))))

    _require_joinable(model, by_fact_type, order)

    rows: list[tuple[dict[str, Any], dict[int, Any]]] = [({}, {})]
    for fact_type_id in order:
        fact_type = _fact_type_by_id(model, fact_type_id)
        ref_roles = {role for _, role in by_fact_type[fact_type_id]}
        anchor_roles = [
            (str(role.get("role_name")), str(role.get("object_type")))
            for role in (fact_type or {}).get("roles") or []
            if str(role.get("role_name")) not in ref_roles
        ]
        new_rows: list[tuple[dict[str, Any], dict[int, Any]]] = []
        for anchors, outputs in rows:
            for fact in population.facts.get(fact_type_id, []):
                if any(role not in fact for role, _ in anchor_roles):
                    continue
                if any(role not in fact for _, role in by_fact_type[fact_type_id]):
                    continue
                merged = dict(anchors)
                compatible = True
                for role_name, object_type in anchor_roles:
                    value = fact[role_name]
                    identity = _identity_key(value)
                    if object_type in merged and merged[object_type] != identity:
                        compatible = False
                        break
                    merged[object_type] = identity
                if not compatible:
                    continue
                new_outputs = dict(outputs)
                for slot, role_name in by_fact_type[fact_type_id]:
                    new_outputs[slot] = fact[role_name]
                new_rows.append((merged, new_outputs))
        rows = new_rows

    return [tuple(outputs[slot] for slot in range(len(role_refs))) for _, outputs in rows]


def _require_joinable(
    model: Model,
    by_fact_type: dict[str, list[tuple[int, str]]],
    order: list[str],
) -> None:
    """Raise :class:`JoinDisconnectedError` when the referenced fact types do
    not form one connected component under shared anchor object types.

    The check is structural (model-only, population-independent): fact types
    are nodes; an edge exists when two fact types share at least one anchor
    object type. A disconnected component means at least one fact type would
    contribute a Cartesian product to the join — silently wrong (CR-02).
    """
    if len(order) <= 1:
        return
    anchor_types: dict[str, set[str]] = {}
    for fact_type_id in order:
        fact_type = _fact_type_by_id(model, fact_type_id)
        ref_roles = {role for _, role in by_fact_type[fact_type_id]}
        candidates: dict[str, list[str]] = {}
        for role in (fact_type or {}).get("roles") or []:
            if str(role.get("role_name")) in ref_roles:
                continue
            candidates.setdefault(str(role.get("object_type")), []).append(
                str(role.get("role_name"))
            )
        for object_type_id, role_names in candidates.items():
            if len(role_names) > 1:
                raise JoinAmbiguousError(fact_type_id, object_type_id, role_names)
        anchor_types[fact_type_id] = {
            str(role.get("object_type"))
            for role in (fact_type or {}).get("roles") or []
            if str(role.get("role_name")) not in ref_roles
        }
    component = {order[0]}
    remaining = set(order) - component
    grew = True
    while grew and remaining:
        grew = False
        for fact_type_id in sorted(remaining):
            if any(anchor_types[fact_type_id] & anchor_types[member] for member in component):
                component.add(fact_type_id)
                remaining.discard(fact_type_id)
                grew = True
    if remaining:
        raise JoinDisconnectedError(order)


def _role_seq_tuples(
    model: Model, population: Population, seq: list[dict[str, Any]]
) -> list[tuple]:
    """Tuples of a role sequence: projection within one fact type, join across."""
    fact_type_ids = {str(ref.get("fact_type")) for ref in seq}
    if len(fact_type_ids) == 1:
        fact_type_id = next(iter(fact_type_ids))
        return _project(population, fact_type_id, [str(ref.get("role")) for ref in seq])
    return _join_rows(model, population, seq)


def _descendant_closure(object_type_id: str, model: Model) -> set[str]:
    """``object_type_id`` plus every transitive SUBTYPE of it (cycle-safe).

    Direction is upward-propagating membership. In ORM 2 subtypehood IS
    population subsethood — ``pop(S) subset-of pop(A)`` whenever
    ``S subtype_of A`` — so a value playing an S-typed role is an instance of A,
    transitively. The reverse does NOT hold: a vehicle is not thereby a car,
    which is why this walk collects descendants and never ancestors.

    Multiple inheritance falls out of the fixpoint rather than needing a case:
    ``subtype_of`` is a list, so a type joins the closure as soon as ANY of its
    declared supertypes is already in it.

    Cycle safety is load-bearing here, not defensive. No ``semantic:`` rule
    forbids subtype cycles today (verified: ``a subtype_of [b]`` plus
    ``b subtype_of [a]`` validates at exit 0; the missing rule is recorded in
    the phase's ``deferred-items.md``). The fixpoint terminates because it only
    ever adds to a subset of a finite set of declared ids.

    Kept as its own helper rather than parameterising ``model._ancestor_closure``
    (the same shape walking the opposite edge direction): both directions are
    live in this phase, and one function taking a direction argument is one call
    site away from being handed the wrong one.
    """
    parents = {
        str(object_type.get("id")): [str(s) for s in object_type.get("subtype_of") or []]
        for object_type in model.object_types
        if object_type.get("id") is not None
    }
    members = {object_type_id}
    changed = True
    while changed:
        changed = False
        for declared_id, supertypes in parents.items():
            if declared_id not in members and members.intersection(supertypes):
                members.add(declared_id)
                changed = True
    return members


def _denoting_types(covered: set[str], model: Model) -> set[str]:
    """Object types whose instances are DENOTED by values of ``covered`` (F-01).

    An ORM reference scheme means an entity type's instances are denoted by
    values of its reference value type: ``population-format.md`` — *"Entity
    values in facts use the entity's reference-scheme value … ``movie: 1`` means
    the Movie whose MovieId is 1"*. So ``movie: 999999`` IS an occurrence of
    MovieId in the population, and the universe of MovieId must contain it.

    The loader already draws exactly this inference. ``popvalidate`` walks
    ``entity -> reference.value_type`` (following ``inherits_reference`` up
    ``subtype_of``) in order to TYPE-CHECK ``999999`` as a MovieId, and rejects
    the population at exit 3 when it is not one. Having asserted that the value
    IS a MovieId, declining to range-check the same value as a MovieId is
    incoherent — one value cannot be a MovieId for typing and not a MovieId for
    constraints. Before this closure, an alethic ``value``/``cardinality``
    constraint on a reference value type reported ``pass`` — *"— satisfied"* —
    at exit 0 over a population that visibly contained violating values, and the
    ``cardinality`` message stated its own blindness out loud (*"at most 2 —
    satisfied (0 observed)"* over four). That is the affirmative false
    certification this phase exists to eliminate, one relation over from the
    subtype direction CORE-06 named.

    The resolution walk is :func:`popvalidate.resolve_reference_value_type` —
    the loader's own traversal, not a second notion of it, because two
    inferences about "which value type denotes this entity" is how the typing
    answer and the constraint answer drift apart again.

    Types already in ``covered`` are excluded so a role can contribute at most
    once, which keeps ``offending`` one entry per OCCURRENCE rather than per
    occurrence per route.
    """
    return {
        str(object_type.get("id"))
        for object_type in model.object_types
        if object_type.get("id") is not None
        and str(object_type.get("id")) not in covered
        and resolve_reference_value_type(str(object_type.get("id")), model) in covered
    }


def _instance_values_of(object_type_id: str, model: Model, population: Population) -> list[Any]:
    """Closed-world instance values of an object type, DUPLICATES PRESERVED.

    The one closed-world walk (SKELETON.md semantics), extended by CORE-06 to
    every transitive subtype: the ``instances:`` roster of the type or any of
    its subtypes, plus every value playing a role typed to the type or any of
    its subtypes. Both routes are required because subtype membership is
    observable both ways (``population-format.md``: "via ``instances:`` rosters
    for the subtype or via subtype-typed roles played in facts").

    For a ``kind: value`` object type the walk additionally collects the values
    that DENOTE instances of every entity type whose reference scheme resolves
    to it (:func:`_denoting_types`, F-01) — by both routes again, since an
    entity's roster holds its identifying values just as its facts do. The
    widening is confined to value types: it says what an identifying value IS,
    and an entity type is never one.

    Returns a LIST because ``_check_value`` reports one offending entry per
    OCCURRENCE, while :func:`_instances_of` needs a set — one traversal, two
    shapes. The exact-match blind spot this closure fixes was previously written
    out twice, in two functions, which is precisely how two copies of one rule
    drift apart (RESEARCH Pitfall 8).

    The target type's own roster is emitted first and the others' in sorted id
    order, so the offending list is deterministic and unchanged for every object
    type that has neither subtypes nor entity types referencing it.
    """
    covered = _descendant_closure(object_type_id, model)
    if _kind_of(object_type_id, model) == "value":
        collected = covered | _denoting_types(covered, model)
    else:
        collected = covered
    values: list[Any] = []
    for collected_id in [object_type_id, *sorted(collected - {object_type_id})]:
        values.extend(population.instances.get(collected_id, []))
    for fact_type in model.fact_types:
        typed_roles = [
            role.get("role_name")
            for role in fact_type.get("roles") or []
            if str(role.get("object_type")) in collected
        ]
        if not typed_roles:
            continue
        for fact in population.facts.get(str(fact_type.get("id")), []):
            for role_name in typed_roles:
                if role_name in fact:
                    values.append(fact[role_name])
    return values


def _kind_of(object_type_id: str, model: Model) -> str | None:
    for object_type in model.object_types:
        if str(object_type.get("id")) == object_type_id:
            kind = object_type.get("kind")
            return str(kind) if kind is not None else None
    return None


def _instances_of(object_type_id: str, model: Model, population: Population) -> _IdentitySet:
    """Closed-world instance SET of an object type (SKELETON.md semantics),
    including every instance of its transitive subtypes (CORE-06).

    Before the closure, a car with no plate satisfied ``mandatory(vehicle)`` —
    affirmatively, with a "satisfied" message — because the universe was derived
    by matching ``role.object_type`` exactly (CONTEXT.md probe #5).
    """
    return _IdentitySet(_instance_values_of(object_type_id, model, population))


def _ref_labels(role_refs: list[dict[str, Any]]) -> list[str]:
    return [f"{ref.get('fact_type')}.{ref.get('role')}" for ref in role_refs]


def _violation_verdict(modality: str) -> Verdict:
    return "fail" if modality == "alethic" else "warning"


# --- family checks ---


def _orderable(a: Any, b: Any) -> bool:
    """Whether two operands admit a total order under Python's operators.

    Exactly two families qualify: two numbers, or two strings. Anything else —
    a number against a string, a string against None — has no ordering, and
    Python raises rather than inventing one.

    ``bool`` is excluded from the numeric family DELIBERATELY, and the exclusion
    must not be simplified away: ``isinstance(True, int)`` is ``True`` in
    Python, and ``True == 1``, so without it a boolean would order against a
    numeric bound and land silently INSIDE a ``1..100`` range. That is the
    ``typed-range-bool-for-integer`` defect, which CORE-04 pins at the loader
    (``population:type-mismatch``) and which this guard must not re-open behind
    it. Declining to order a boolean is the honest answer here; deciding
    whether a boolean is a valid Integer is the loader's job, not this one's.

    ``NaN`` is excluded for the same reason and by the same shape (CR-04).
    IEEE 754-2019 §5.11: every ordered comparison involving NaN is *unordered*,
    so ``min <= x <= max`` is false, never true — but ``_in_range`` derives its
    answer from the NEGATION (``not (below or above)``), and both ``nan < min``
    and ``nan > max`` are ``False``, so a NaN came out INSIDE every range and
    the constraint reported "— satisfied" at exit 0. Python does not raise on
    ``nan < 60``, so unlike every other unorderable pairing here this one had no
    crash to notice. ``popvalidate._is_number`` now rejects non-finite values at
    the loader; this is the defense-in-depth twin for the D-05 residual path,
    where the role's object type has no resolvable primitive and no type check
    ever runs. ``inf`` is NOT excluded: it orders totally and correctly against
    finite bounds, so declining to order it would trade a false pass for a false
    ``unchecked``.
    """
    numeric = (int, float)

    def _numeric(value: Any) -> bool:
        return (
            isinstance(value, numeric)
            and not isinstance(value, bool)
            and not (isinstance(value, float) and math.isnan(value))
        )

    return (_numeric(a) and _numeric(b)) or (isinstance(a, str) and isinstance(b, str))


def _in_range(value: Any, bounds: dict[str, Any], primitive: str | None = None) -> bool | None:
    """Whether ``value`` lies within ``bounds`` — or ``None`` when undecidable.

    Defense in depth (D-13 clause 4, T-01.1-15): CORE-04's model-relative type
    validation is what normally prevents an unorderable pairing from reaching
    the checker at all — a String in an Integer-typed role is rejected at load
    with ``population:type-mismatch`` (exit 3) and never arrives here. This
    guard exists for the residual path D-05 deliberately leaves open: when a
    role's object type has NO resolvable primitive (a unit-based or external
    reference mode, an ambiguous multiple inheritance), the type check is
    skipped silently and correctly, and its values arrive intact.

    Returns ``None`` rather than raising because the caller evaluates over a
    COLLECTION: a raise would discard the verdicts for every well-typed value
    alongside the one ill-typed member. Reporting "could not decide" mirrors the
    :class:`JoinDisconnectedError` precedent at a finer grain — when a
    computation is not soundly decidable, say so instead of returning a
    plausible verdict.
    """
    minimum = bounds.get("min")
    maximum = bounds.get("max")
    min_inclusive = bounds.get("min_inclusive", True)
    max_inclusive = bounds.get("max_inclusive", True)
    below = False
    if minimum is not None:
        below = _compare(value, "<" if min_inclusive else "<=", minimum, primitive, primitive)
        if below is None:
            return None
    above = False
    if maximum is not None:
        above = _compare(value, ">" if max_inclusive else ">=", maximum, primitive, primitive)
        if above is None:
            return None
    return not (below or above)


def _find_cycle(pairs: list[tuple]) -> list | None:
    """Cycle members of the directed graph induced by binary pairs, or None.

    Primary path: stdlib ``graphlib.TopologicalSorter`` — its ``CycleError``
    carries the cycle path in ``args[1]`` (RESEARCH A1, confirmed by unit
    test). If that shape ever yields fewer than two members, a ~20-line DFS
    fallback recovers the cycle path.
    """
    graph: dict[Any, set[Any]] = {}
    for a, b in pairs:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())
    try:
        TopologicalSorter(graph).prepare()
        return None
    except CycleError as error:
        members = list(error.args[1]) if len(error.args) > 1 else []
        if len(set(members)) >= 2:
            return members
        return _dfs_cycle(graph)


def _dfs_cycle(graph: dict[Any, set[Any]]) -> list | None:
    """Iterative DFS fallback returning an explicit cycle path."""
    visiting: set[Any] = set()
    visited: set[Any] = set()
    for start in graph:
        if start in visited:
            continue
        stack: list[tuple[Any, list[Any]]] = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if node in visiting:
                continue
            visiting.add(node)
            for successor in graph.get(node, ()):
                if successor in path:
                    return path[path.index(successor) :] + [successor]
                if successor not in visited:
                    stack.append((successor, path + [successor]))
            visited.add(node)
    return None


def _ring_component_violations(
    component: str, pair_set: set[tuple], elements: set[Any]
) -> list[tuple]:
    """Offending witnesses for one primitive ring variant (Halpin semantics)."""
    if component == "irreflexive":
        return sorted(((a, b) for a, b in pair_set if a == b), key=repr)
    if component == "asymmetric":
        return sorted(((a, b) for a, b in pair_set if (b, a) in pair_set), key=repr)
    if component == "antisymmetric":
        return sorted(((a, b) for a, b in pair_set if a != b and (b, a) in pair_set), key=repr)
    if component == "symmetric":
        return sorted(((a, b) for a, b in pair_set if (b, a) not in pair_set), key=repr)
    if component == "intransitive":
        return sorted(
            (
                (a, b, c)
                for a, b in pair_set
                for b2, c in pair_set
                if b2 == b and (a, c) in pair_set
            ),
            key=repr,
        )
    if component == "transitive":
        return sorted(
            (
                (a, b, c)
                for a, b in pair_set
                for b2, c in pair_set
                if b2 == b and (a, c) not in pair_set
            ),
            key=repr,
        )
    if component == "purely-reflexive":
        return sorted(((a, b) for a, b in pair_set if a != b), key=repr)
    if component == "reflexive":
        return sorted(((a,) for a in elements if (a, a) not in pair_set), key=repr)
    # acyclic
    cycle = _find_cycle(sorted(pair_set, key=repr))
    return [tuple(cycle)] if cycle else []


_COMPARATORS = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "!=": lambda a, b: a != b,
}


def _typed_comparison_values(
    value_a: Any,
    value_b: Any,
    primitive_a: str | None,
    primitive_b: str | None,
) -> tuple[Any, Any] | None:
    """Coerce role values into their declared common comparison domain."""
    if primitive_a is None or primitive_b is None:
        return value_a, value_b
    numeric = {"Integer", "Float", "Number"}
    if primitive_a in numeric and primitive_b in numeric:
        return value_a, value_b
    if primitive_a != primitive_b:
        return None
    if primitive_a == "Date":
        try:
            return date.fromisoformat(value_a), date.fromisoformat(value_b)
        except (TypeError, ValueError):
            return None
    if primitive_a == "DateTime":
        try:
            parsed = []
            for value in (value_a, value_b):
                normalized = value[:-1] + "+00:00" if value[-1:] in ("Z", "z") else value
                parsed.append(datetime.fromisoformat(normalized))
        except (TypeError, ValueError):
            return None
        aware = [value.utcoffset() is not None for value in parsed]
        if aware[0] != aware[1]:
            return None
        if aware[0]:
            parsed = [value.astimezone(UTC) for value in parsed]
        return parsed[0], parsed[1]
    return value_a, value_b


def _compare(
    value_a: Any,
    operator: str,
    value_b: Any,
    primitive_a: str | None = None,
    primitive_b: str | None = None,
) -> bool | None:
    """Evaluate one comparison — or return ``None`` when it cannot be decided.

    Equality and inequality stay TOTAL across types and are answered first:
    Python's ``==`` / ``!=`` are well defined for any two objects and never
    raise, so ``1 != "a"`` has a correct answer and must keep getting one. D-14
    targets ORDERING only, which is why this early return survives it.

    For an ordering operator the operands must be orderable. D-14 removed the
    former fallback, which rendered both operands as text and compared those
    instead: it evaluated ``1 < "a"`` as ``"1" < "a"`` and returned ``True`` —
    a CONFIDENT WRONG ANSWER
    indistinguishable to the caller from a real evaluation — strictly worse than
    the crash it was presumably added to avoid. ``None`` is the honest third
    answer, and the caller turns it into an ``unchecked`` verdict carrying
    ``values-not-comparable``.
    """
    if (
        operator in ("=", "!=")
        and primitive_a is not None
        and primitive_b is not None
        and primitive_a != primitive_b
        and not {primitive_a, primitive_b} <= {"Integer", "Float", "Number"}
    ):
        equal = _identity_key(value_a) == _identity_key(value_b)
        return equal if operator == "=" else not equal

    typed = _typed_comparison_values(value_a, value_b, primitive_a, primitive_b)
    if typed is None:
        return None
    value_a, value_b = typed
    comparator = _COMPARATORS[operator]
    if operator in ("=", "!="):
        equal = _identity_key(value_a) == _identity_key(value_b)
        return equal if operator == "=" else not equal
    if primitive_a == primitive_b and primitive_a in ("Date", "DateTime"):
        return bool(comparator(value_a, value_b))
    if not _orderable(value_a, value_b):
        return None
    # Two numbers, or two strings — the latter compare lexically, which is what
    # makes ISO-8601 dates order correctly (and why popvalidate format-checks
    # Date/DateTime values at load).
    return bool(comparator(value_a, value_b))


_INVALID_LITERAL = object()


def _literal(operand: Any, primitive: str | None, *, legacy: bool) -> Any:
    """Interpret a literal in the compared role's declared primitive domain."""
    if primitive in ("String", "Binary", "Date", "DateTime"):
        return operand if isinstance(operand, str) else _INVALID_LITERAL
    if primitive == "Boolean":
        if isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str) and operand.lower() in ("true", "false"):
            return operand.lower() == "true"
        return _INVALID_LITERAL
    if primitive == "Integer":
        if isinstance(operand, int) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return int(operand)
            except ValueError:
                return _INVALID_LITERAL
        return _INVALID_LITERAL
    if primitive in ("Float", "Number"):
        if isinstance(operand, (int, float)) and not isinstance(operand, bool):
            return operand
        if legacy and isinstance(operand, str):
            try:
                return float(operand)
            except ValueError:
                return _INVALID_LITERAL
        return _INVALID_LITERAL
    return _INVALID_LITERAL


def _guarded_variable(term: Any) -> str | None:
    """Return a guarded variable name; every other scalar is literal data."""
    return term if isinstance(term, str) and term.startswith("$") else None


Scalar = str | int | float | bool
IdentityCodecVersion = Literal["gnd-identity-json/1"]
FactPath = tuple[str | int, ...]
RowLineage = tuple[FactPath, ...]


@dataclass(frozen=True)
class _TypedRelation:
    fact_type: str
    roles: tuple[tuple[str, str | None], ...]
    rows: tuple[tuple[Scalar, ...], ...]
    row_lineage: tuple[RowLineage, ...] = ()
    identity_codec_version: IdentityCodecVersion = "gnd-identity-json/1"


@dataclass
class _JoinWork:
    atom_role_terms_read: int = 0
    positive_candidate_rows_emitted: int = 0
    join_candidates_indexed: int = 0
    join_left_bindings_probed: int = 0
    join_matches_merged: int = 0
    component_product_rows_emitted: int = 0
    negation_rows_indexed: int = 0
    negation_bindings_probed: int = 0
    head_cells_projected: int = 0


@dataclass
class _ExactJoinWork(_JoinWork):
    term_nodes_visited: int = 0
    term_operations: int = 0
    max_exact_value_bits: int = 0
    aggregate_candidate_bindings: int = 0
    aggregate_contribution_terms: int = 0
    aggregate_identity_tokens: int = 0
    aggregate_distinct_contributions: int = 0
    aggregate_group_lookups: int = 0
    aggregate_groups: int = 0
    aggregate_exact_operations: int = 0
    aggregate_maximum_value_bits: int = 0


@dataclass
class _FixpointJoinWork(_ExactJoinWork):
    fixpoint_iterations: int = 0
    canonical_insertions: int = 0


def _count_term_work(work: _ExactJoinWork, result: Any) -> None:
    work.term_nodes_visited += int(getattr(result, "nodes", 0))
    work.term_operations += int(getattr(result, "operations", 0))
    work.max_exact_value_bits = max(
        work.max_exact_value_bits,
        int(getattr(result, "max_value_bits", 0)),
    )


@dataclass(frozen=True)
class _ExtensionResult:
    extensions: Mapping[str, _TypedRelation]
    counted_operations: _JoinWork


@dataclass(frozen=True)
class RelationUnavailable:
    relation: str
    reason: str
    binding: Mapping[str, Scalar]
    source_relation: str | None = None


class _ExactExtensions(dict[str, _TypedRelation]):
    """Extension mapping carrying relation-level unavailability out of band."""

    def __init__(
        self,
        *args: Any,
        unavailable: Mapping[str, RelationUnavailable] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.unavailable = MappingProxyType(dict(unavailable or {}))


@dataclass(frozen=True)
class _Wildcard:
    primitive: str | None
    coordinate: tuple[str, int, str]


class _PartialTermFailure(Exception):
    def __init__(self, reason: str, binding: Mapping[str, Any]) -> None:
        self.reason = reason
        self.binding = MappingProxyType(dict(binding))


class _PartialExtensions(_ExactExtensions):
    """Definite extension rows plus finite possible patterns, kept internal."""

    def __init__(
        self, *args: Any,
        possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.possible = MappingProxyType(dict(possible))


_PARTIAL_OPAQUE: ContextVar[bool] = ContextVar("gnd_partial_opaque", default=False)


def _symbolic_value(value: Any, primitive: str | None, coordinate: tuple[str, int, str]) -> Scalar | _Wildcard:
    if isinstance(value, dict) and set(value) == {"$opaque"}:
        return _Wildcard(primitive, coordinate)
    return value


def _partial_token(value: Scalar | _Wildcard) -> bytes:
    if isinstance(value, _Wildcard):
        return repr(("wildcard", value.primitive, value.coordinate)).encode()
    return _identity_token(value)


def _partial_compatible(left: Scalar | _Wildcard, right: Scalar | _Wildcard) -> bool:
    if isinstance(left, _Wildcard) and isinstance(right, _Wildcard):
        return left.primitive == right.primitive or None in (left.primitive, right.primitive)
    if isinstance(left, _Wildcard):
        return left.primitive is None or _scalar_primitive_compatible(right, left.primitive)
    if isinstance(right, _Wildcard):
        return right.primitive is None or _scalar_primitive_compatible(left, right.primitive)
    return _identity_token(left) == _identity_token(right)


def _scalar_primitive_compatible(value: Scalar, primitive: str) -> bool:
    if primitive in {"String", "Binary", "Date", "DateTime"}:
        return isinstance(value, str)
    if primitive == "Boolean":
        return isinstance(value, bool)
    if primitive == "Integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if primitive in {"Float", "Number"}:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def _partial_merge(left: Scalar | _Wildcard, right: Scalar | _Wildcard) -> Scalar | _Wildcard:
    if isinstance(left, _Wildcard):
        return right if not isinstance(right, _Wildcard) else min((left, right), key=_partial_token)
    return left


def _partial_row_facts(
    roles: tuple[tuple[str, str | None], ...],
    rows: Sequence[tuple[Scalar | _Wildcard, ...]],
) -> tuple[dict[str, Scalar | _Wildcard], ...]:
    return tuple(dict(zip((name for name, _ in roles), row, strict=True)) for row in rows)


def _partial_binding_shape(binding: Mapping[str, Scalar | _Wildcard]) -> tuple[Any, ...]:
    """Equivalent symbolic rows cover the same may-bindings regardless of source cell."""
    names: dict[tuple[str, int, str], int] = {}
    result = []
    for role, value in sorted(binding.items()):
        if isinstance(value, _Wildcard):
            ordinal = names.setdefault(value.coordinate, len(names))
            result.append((role, "wildcard", value.primitive, ordinal))
        else:
            result.append((role, "scalar", _partial_token(value)))
    return tuple(result)


def _partial_bindings(
    atoms: Sequence[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    work: _FixpointJoinWork,
    *,
    compact: bool = True,
) -> list[dict[str, Scalar | _Wildcard]]:
    bindings: list[dict[str, Scalar | _Wildcard]] = [{}]
    for atom in atoms:
        candidates: list[dict[str, Scalar | _Wildcard]] = []
        binds = atom_bind(atom)
        for fact in facts.get(str(atom.get("fact_type")), ()):
            candidate: dict[str, Scalar | _Wildcard] = {}
            for role, term in binds.items():
                work.atom_role_terms_read += 1
                if role not in fact:
                    break
                value = fact[role]
                variable = _derivation_variable(term)
                if variable is None:
                    if not _partial_compatible(value, term):
                        break
                elif variable in candidate:
                    if not _partial_compatible(candidate[variable], value):
                        break
                    candidate[variable] = _partial_merge(candidate[variable], value)
                else:
                    candidate[variable] = value
            else:
                candidates.append(candidate)
                work.positive_candidate_rows_emitted += 1
        if compact:
            candidates = list({
                _partial_binding_shape(candidate): candidate for candidate in candidates
            }.values())
        joined: list[dict[str, Scalar | _Wildcard]] = []
        seen: set[tuple[Any, ...]] = set()
        shared = tuple(name for name in candidates[0] if name in bindings[0]) if candidates and bindings else ()
        index: dict[tuple[bytes, ...], list[dict[str, Scalar | _Wildcard]]] = {}
        wildcard_candidates: list[dict[str, Scalar | _Wildcard]] = []
        if shared:
            for candidate in candidates:
                if any(isinstance(candidate[name], _Wildcard) for name in shared):
                    wildcard_candidates.append(candidate)
                else:
                    key = tuple(_partial_token(candidate[name]) for name in shared)
                    index.setdefault(key, []).append(candidate)
                    work.join_candidates_indexed += 1
        for left in bindings:
            if shared and all(not isinstance(left[name], _Wildcard) for name in shared):
                key = tuple(_partial_token(left[name]) for name in shared)
                probes = [*index.get(key, ()), *wildcard_candidates]
            else:
                probes = candidates
            work.join_left_bindings_probed += 1
            for right in probes:
                _witness_charge()
                if any(name in left and not _partial_compatible(left[name], value)
                       for name, value in right.items()):
                    continue
                merged = dict(left)
                for name, value in right.items():
                    merged[name] = _partial_merge(merged[name], value) if name in merged else value
                shape = _partial_binding_shape(merged) if compact else ()
                if not compact or shape not in seen:
                    seen.add(shape)
                    joined.append(merged)
                    work.join_matches_merged += 1
        bindings = joined
        if not bindings:
            break
    return bindings


def _partial_negation(
    bindings: list[dict[str, Scalar | _Wildcard]],
    atoms: Sequence[dict[str, Any]],
    blockers: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    *,
    definite: bool,
) -> list[dict[str, Scalar | _Wildcard]]:
    for atom in atoms:
        retained = []
        for binding in bindings:
            blocked = False
            for fact in blockers.get(str(atom.get("fact_type")), ()):
                values: list[tuple[Scalar | _Wildcard, Scalar | _Wildcard]] = []
                for role, term in atom_bind(atom).items():
                    variable = _derivation_variable(term)
                    if role not in fact or (variable is not None and variable not in binding):
                        break
                    values.append((fact[role], binding[variable] if variable is not None else term))
                else:
                    # A concrete blocker excludes a concrete candidate.
                    # A symbolic candidate may still describe other values.
                    if all(_partial_compatible(a, b) for a, b in values) and (
                        definite or all(not isinstance(b, _Wildcard) for _a, b in values)
                    ):
                        blocked = True
                        break
            if not blocked:
                retained.append(binding)
        bindings = retained
    return bindings


# Opt-in capture for finite derivation witnesses. Ordinary checking has no trace.
_WITNESS_TRACE: ContextVar[Any] = ContextVar("gnd_witness_trace", default=None)


def _witness_charge(amount: int = 1) -> None:
    trace = _WITNESS_TRACE.get()
    if trace is not None:
        trace.charge(amount)


def _witness_row(fact_type, clause, binding, row) -> None:
    trace = _WITNESS_TRACE.get()
    if trace is not None:
        trace.row(fact_type, clause, binding, row)


def _partial_clause_rows(
    model: Model,
    fact_type: dict[str, Any],
    clause: dict[str, Any],
    must_facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    may_facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    must_lineages: Mapping[str, tuple[RowLineage, ...]],
    work: _FixpointJoinWork,
    *,
    definite: bool,
) -> list[tuple[tuple[Scalar | _Wildcard, ...], RowLineage]]:
    source = must_facts if definite else may_facts
    bindings = _partial_bindings(clause.get("body") or (), source, work, compact=not definite)
    bindings = _partial_negation(
        bindings, clause.get("negate") or (), may_facts if definite else must_facts,
        definite=definite,
    )
    aggregate = clause.get("aggregate")
    if isinstance(aggregate, dict):
        analysis = analyze_declared_aggregate(model, clause)
        group_names = analysis.group_variables
        result_name = analysis.result_variable or str(aggregate.get("as", "")).removeprefix("$")
        if definite:
            possible_bindings = _partial_negation(
                _partial_bindings(clause.get("body") or (), may_facts, work),
                clause.get("negate") or (), must_facts, definite=False,
            )
            bindings = [
                binding for binding in bindings
                if not any(
                    any(isinstance(value, _Wildcard) for value in candidate.values())
                    and all(_partial_compatible(binding[name], candidate[name]) for name in group_names)
                    for candidate in possible_bindings
                )
            ]
            bindings, failure = _aggregate_bindings(clause, bindings, work, analysis)
            if failure is not None:
                raise _PartialTermFailure(failure.reason, failure.binding)
        else:
            grouped: dict[tuple[bytes, ...], list[dict[str, Scalar | _Wildcard]]] = {}
            for binding in bindings:
                key = tuple(_partial_token(binding[name]) for name in group_names)
                grouped.setdefault(key, []).append(binding)
            collapsed = []
            for members in grouped.values():
                if any(isinstance(value, _Wildcard) for member in members for value in member.values()):
                    representative = {name: members[0][name] for name in group_names}
                    representative[result_name] = _Wildcard(
                        None, (str(fact_type.get("id")), 0, result_name)
                    )
                    collapsed.append(representative)
                else:
                    exact_rows, failure = _aggregate_bindings(clause, members, work, analysis)
                    if failure is not None:
                        raise _PartialTermFailure(failure.reason, failure.binding)
                    collapsed.extend(exact_rows)
            bindings = collapsed
    if clause.get("where"):
        filtered = []
        for binding in bindings:
            keep = True
            for comparison in clause["where"]:
                used = set(term_variables(comparison.get("left"))) | set(term_variables(comparison.get("right")))
                if any(isinstance(binding.get(name), _Wildcard) for name in used):
                    if definite:
                        keep = False
                    continue
                result = compare_terms(
                    str(comparison.get("operator")), comparison.get("left"),
                    comparison.get("right"), binding,
                    bound_cross_product=bool(clause.get("aggregate")),
                )
                if not result.available:
                    raise _PartialTermFailure(str(result.reason), binding)
                if result.available and result.value is not True:
                    keep = False
                    break
            if keep:
                filtered.append(binding)
        bindings = filtered
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or ()]
    proofs = (
        _binding_lineages(clause, bindings, must_facts, must_lineages)
        if definite and not clause.get("aggregate")
        else tuple(() for _ in bindings)
    )
    rows = []
    for binding, proof in zip(bindings, proofs, strict=True):
        row = []
        for role in role_names:
            term = clause["head"][role]
            variable = _derivation_variable(term)
            if variable is not None:
                row.append(binding[variable])
            elif is_function_term(term):
                if any(isinstance(value, _Wildcard) for value in binding.values()):
                    row.append(_Wildcard(_relation_roles(model, fact_type)[len(row)][1],
                                         (str(fact_type.get("id")), 0, role)))
                else:
                    result = evaluate_term(term, binding)
                    if result.available:
                        try:
                            row.append(materialize_scalar(result.value))
                        except ValueError:
                            raise _PartialTermFailure("term:head-non-integral", binding) from None
                    else:
                        raise _PartialTermFailure(str(result.reason), binding)
            else:
                row.append(term)
            work.head_cells_projected += 1
        if len(row) == len(role_names) and (not definite or not any(isinstance(v, _Wildcard) for v in row)):
            if definite:
                _witness_row(fact_type, clause, binding, tuple(row))
            rows.append((tuple(row), proof))
    return rows


@dataclass(frozen=True)
class _ExactExtensionResult:
    extensions: _ExactExtensions
    counted_operations: _JoinWork


ExtensionCalculator = Callable[
    [Model, Mapping[str, _TypedRelation]],
    _ExtensionResult,
]
VariableResolver = Callable[[Any], str | None]


class _FactView(Protocol):
    covers: Sequence[str]
    instances: Mapping[str, Sequence[Scalar]]
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]]


@dataclass(frozen=True)
class _RuledFactView:
    covers: tuple[str, ...]
    instances: Mapping[str, tuple[Scalar, ...]]
    facts: Mapping[str, tuple[Mapping[str, Scalar], ...]]
    lineages: Mapping[str, tuple[RowLineage, ...]]


def _identity_token(value: Scalar) -> bytes:
    """Canonical scalar identity from representation-format.md."""
    import json

    if isinstance(value, bool):
        payload: list[Any] = ["boolean", value]
    elif isinstance(value, int):
        payload = ["number", [value, 1]]
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite values have no identity token")
        numerator, denominator = value.as_integer_ratio()
        payload = ["number", [numerator, denominator]]
    elif isinstance(value, str):
        payload = ["string", value]
    else:
        raise TypeError(f"unsupported identity scalar: {type(value).__name__}")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()


def _joined_atom_candidates(
    atom: dict[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    *,
    variable_of: VariableResolver,
    work: _JoinWork | None,
) -> list[dict[str, Scalar]]:
    """Match one antecedent atom without a seed binding.

    Each returned mapping is one fact's internally consistent variable
    assignment.  In particular, a variable repeated in one atom must have the
    same identity at every role before the fact becomes a candidate.
    """
    fact_type_id = str(atom.get("fact_type"))
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return []
    candidates: list[dict[str, Scalar]] = []
    rows = facts.get(fact_type_id, ())
    for fact in rows:
        if not isinstance(fact, Mapping):
            continue
        candidate: dict[str, Scalar] = {}
        matches = True
        for role_name, term in binds.items():
            if work is not None:
                work.atom_role_terms_read += 1
            if role_name not in fact:
                matches = False
                break
            value = fact[role_name]
            variable = variable_of(term)
            if variable is None:
                if _identity_key(value) != _identity_key(term):
                    matches = False
                    break
            elif variable in candidate:
                if _identity_key(value) != _identity_key(candidate[variable]):
                    matches = False
                    break
            else:
                candidate[variable] = value
        if matches:
            candidates.append(candidate)
            if work is not None:
                work.positive_candidate_rows_emitted += 1
    return candidates


_REFERENCE_PRESENTATION_WORK: ContextVar[Any] = ContextVar(
    "reference_presentation_work", default=None
)


def _joined_bindings(
    atoms: list[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    *,
    variable_of: VariableResolver,
    work: _JoinWork | None,
) -> list[dict[str, Scalar]]:
    """Enumerate one connected atom component with indexed hash joins."""
    if not atoms:
        return []
    variable_order = list(
        dict.fromkeys(
            variable
            for atom in atoms
            for term in atom_bind(atom).values()
            if (variable := variable_of(term)) is not None
        )
    )
    variables = [
        {
            variable
            for term in atom_bind(atom).values()
            if (variable := variable_of(term)) is not None
        }
        for atom in atoms
    ]

    # Choose the earliest atom that connects to the variables bound so far.
    # This preserves declaration order among available atoms while avoiding an
    # intermediate cross product when a later atom is the connecting bridge.
    order = [0]
    bound_variables = set(variables[0])
    remaining = list(range(1, len(atoms)))
    while remaining:
        next_index = next(
            (index for index in remaining if variables[index] & bound_variables),
            None,
        )
        if next_index is None:
            raise JoinDisconnectedError([str(atom.get("fact_type")) for atom in atoms])
        order.append(next_index)
        bound_variables |= variables[next_index]
        remaining.remove(next_index)

    candidates = [
        _joined_atom_candidates(
            atom,
            facts,
            variable_of=variable_of,
            work=work,
        )
        for atom in atoms
    ]
    bindings = candidates[order[0]]
    _witness_charge(len(bindings))
    seen_variables = set(variables[order[0]])
    for atom_index in order[1:]:
        shared = [
            variable
            for variable in atom_bind(atoms[atom_index]).values()
            if variable_of(variable) in seen_variables
        ]
        shared = list(
            dict.fromkeys(
                variable_of(variable) for variable in shared if variable_of(variable) is not None
            )
        )
        index: dict[tuple[tuple[Any, ...], ...], list[dict[str, Any]]] = {}
        for candidate in candidates[atom_index]:
            key = tuple(_identity_key(candidate[variable]) for variable in shared)
            index.setdefault(key, []).append(candidate)
            if work is not None:
                work.join_candidates_indexed += 1

        joined: list[dict[str, Any]] = []
        for binding in bindings:
            if work is not None:
                work.join_left_bindings_probed += 1
            key = tuple(_identity_key(binding[variable]) for variable in shared)
            for candidate in index.get(key, []):
                _witness_charge()
                reference_work = _REFERENCE_PRESENTATION_WORK.get()
                if reference_work is not None:
                    reference_work.charge()
                if any(
                    variable in binding and _identity_key(binding[variable]) != _identity_key(value)
                    for variable, value in candidate.items()
                ):
                    continue
                merged = dict(binding)
                for variable, value in candidate.items():
                    merged.setdefault(variable, value)
                joined.append(merged)
                if work is not None:
                    work.join_matches_merged += 1
        bindings = joined
        seen_variables |= variables[atom_index]
    return [
        {variable: binding[variable] for variable in variable_order if variable in binding}
        for binding in bindings
    ]


def _guarded_bindings(atoms: list[dict[str, Any]], population: Population) -> list[dict[str, Any]]:
    """Preserve the guarded disconnection policy through the shared join core."""
    from gnd.correspondence import ReferenceJoinWork

    token = _REFERENCE_PRESENTATION_WORK.set(
        ReferenceJoinWork() if getattr(population, "_reference_combined", False) else None
    )
    try:
        return _joined_bindings(
            atoms,
            population.facts,
            variable_of=_guarded_variable,
            work=None,
        )
    finally:
        _REFERENCE_PRESENTATION_WORK.reset(token)


def _relation_facts(
    relations: Mapping[str, _TypedRelation],
) -> Mapping[str, Sequence[Mapping[str, Scalar]]]:
    return MappingProxyType(
        {
            fact_type_id: tuple(
                MappingProxyType(
                    {
                        role_name: value
                        for (role_name, _primitive), value in zip(relation.roles, row, strict=True)
                    }
                )
                for row in relation.rows
            )
            for fact_type_id, relation in relations.items()
        }
    )


def _relation_roles(model: Model, fact_type: dict[str, Any]) -> tuple[tuple[str, str | None], ...]:
    roles: list[tuple[str, str | None]] = []
    for role in fact_type.get("roles") or []:
        object_type = str(role.get("object_type"))
        roles.append((str(role.get("role_name")), resolve_primitive(object_type, model)))
    return tuple(roles)


def _rows_from_facts(
    roles: tuple[tuple[str, str | None], ...],
    facts: Sequence[Mapping[str, Scalar]],
) -> tuple[tuple[Scalar, ...], ...]:
    return tuple(tuple(fact[role_name] for role_name, _primitive in roles) for fact in facts)


def _base_relations(model: Model, population: Population) -> Mapping[str, _TypedRelation]:
    relations: dict[str, _TypedRelation] = {}
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        roles = _relation_roles(model, fact_type)
        rule = fact_type.get("derivation_rule")
        rows = (
            ()
            if isinstance(rule, dict)
            else _rows_from_facts(roles, population.facts.get(fact_type_id, ()))
        )
        row_lineage = (
            ()
            if isinstance(rule, dict)
            else tuple((("facts", fact_type_id, index),) for index, _row in enumerate(rows))
        )
        relations[fact_type_id] = _TypedRelation(fact_type_id, roles, rows, row_lineage=row_lineage)
    return MappingProxyType(relations)


def _component_atoms(rule: dict[str, Any]) -> list[list[dict[str, Any]]]:
    components = body_components(rule)
    grouped: list[list[dict[str, Any]]] = [[] for _component in components]
    for index, atom in enumerate(rule.get("body") or []):
        variables = {
            variable
            for term in atom_bind(atom).values()
            if (variable := _derivation_variable(term)) is not None
        }
        if variables:
            component_index = next(
                slot for slot, component in enumerate(components) if variables <= component
            )
        else:
            marker = f"\u0000grounded:.body[{index}]"
            component_index = next(
                slot for slot, component in enumerate(components) if marker in component
            )
        grouped[component_index].append(atom)
    return grouped


def _component_product(
    component_bindings: Sequence[Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    product: list[dict[str, Scalar]] = [{}]
    for component_index, bindings in enumerate(component_bindings):
        next_product: list[dict[str, Scalar]] = []
        for left in product:
            for right in bindings:
                if component_index:
                    _witness_charge()
                if any(
                    variable in left and _identity_key(left[variable]) != _identity_key(value)
                    for variable, value in right.items()
                ):
                    continue
                merged = dict(left)
                merged.update(right)
                next_product.append(merged)
                work.component_product_rows_emitted += 1
        product = next_product
    return product


def _apply_negation(
    bindings: list[dict[str, Scalar]],
    atoms: Sequence[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    remaining = bindings
    for atom in atoms:
        binds = atom_bind(atom)
        role_names = tuple(str(role_name) for role_name in binds)
        index: set[tuple[bytes, ...]] = set()
        for fact in facts.get(str(atom.get("fact_type")), ()):
            if all(role_name in fact for role_name in role_names):
                index.add(tuple(_identity_token(fact[role_name]) for role_name in role_names))
                work.negation_rows_indexed += 1
        survivors: list[dict[str, Scalar]] = []
        for binding in remaining:
            values: list[Scalar] = []
            resolvable = True
            for term in binds.values():
                variable = _derivation_variable(term)
                if variable is None:
                    values.append(term)
                elif variable in binding:
                    values.append(binding[variable])
                else:
                    resolvable = False
                    break
            work.negation_bindings_probed += 1
            if not resolvable or tuple(_identity_token(value) for value in values) not in index:
                survivors.append(binding)
        remaining = survivors
    return remaining


def _clause_bindings(
    rule: Mapping[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    """Retain the production component/product/negation sequence for every caller."""
    components = [
        _joined_bindings(atoms, facts, variable_of=_derivation_variable, work=work)
        for atoms in _component_atoms(rule)
    ]
    bindings = _component_product(components, work)
    return _apply_negation(bindings, rule.get("negate") or [], facts, work)


def _project_extension(
    fact_type: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    work: _JoinWork,
) -> tuple[tuple[Scalar, ...], ...]:
    rule = fact_type["derivation_rule"]
    head = rule["head"]
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
    unique: dict[tuple[bytes, ...], tuple[Scalar, ...]] = {}
    for binding in bindings:
        row: list[Scalar] = []
        for role_name in role_names:
            term = head[role_name]
            variable = _derivation_variable(term)
            row.append(binding[variable] if variable is not None else term)
            work.head_cells_projected += 1
        typed_row = tuple(row)
        unique.setdefault(tuple(_identity_token(value) for value in typed_row), typed_row)
    return tuple(unique[key] for key in sorted(unique))


def _binding_lineages(
    rule: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    fact_lineages: Mapping[str, tuple[RowLineage, ...]],
) -> tuple[RowLineage, ...]:
    """Retain one deterministic, row-exact positive proof for each binding."""
    indexes: list[tuple[dict[str, Any], dict[tuple[bytes, ...], RowLineage]]] = []
    for atom in rule.get("body") or ():
        fact_type_id = str(atom.get("fact_type"))
        binds = atom_bind(atom)
        role_names = tuple(str(role_name) for role_name in binds)
        row_lineages = fact_lineages.get(fact_type_id, ())
        index: dict[tuple[bytes, ...], RowLineage] = {}
        for row_index, fact in enumerate(facts.get(fact_type_id, ())):
            if not all(role_name in fact for role_name in role_names):
                continue
            key = tuple(_identity_token(fact[role_name]) for role_name in role_names)
            lineage = row_lineages[row_index] if row_index < len(row_lineages) else ()
            index.setdefault(key, lineage)
        indexes.append((binds, index))

    result: list[RowLineage] = []
    for binding in bindings:
        support: set[FactPath] = set()
        for binds, index in indexes:
            values: list[Scalar] = []
            for term in binds.values():
                variable = _derivation_variable(term)
                values.append(binding[variable] if variable is not None else term)
            support.update(index[tuple(_identity_token(value) for value in values)])
        result.append(tuple(sorted(support, key=lambda path: tuple(map(str, path)))))
    return tuple(result)


def _project_lineage(
    fact_type: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    binding_lineages: Sequence[RowLineage],
) -> tuple[RowLineage, ...]:
    """Mirror extension de-duplication while retaining its selected proof rows."""
    head = fact_type["derivation_rule"]["head"]
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
    unique: dict[tuple[bytes, ...], RowLineage] = {}
    for binding, lineage in zip(bindings, binding_lineages, strict=True):
        row = []
        for role_name in role_names:
            term = head[role_name]
            variable = _derivation_variable(term)
            row.append(binding[variable] if variable is not None else term)
        unique.setdefault(tuple(_identity_token(value) for value in row), lineage)
    return tuple(unique[key] for key in sorted(unique))


def _python_extension_calculator(
    model: Model,
    relations: Mapping[str, _TypedRelation],
) -> _ExtensionResult:
    """Evaluate the structured rule language defined in representation-format.md."""
    if _requires_fixpoint(model) or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in relations.values() for row in relation.rows for value in row
    ):
        return _evaluate_stratified_extensions(model, relations, exact=False)
    # Materialize the asserted view once. Each completed stratum then contributes
    # only its own relation. Rebuilding every prior relation for every stratum is
    # quadratic in the number of structured fact types before a single join is
    # evaluated, and that work used to sit outside the advertised counters.
    facts = dict(_relation_facts(relations))
    fact_lineages = {
        fact_type_id: relation.row_lineage for fact_type_id, relation in relations.items()
    }
    extensions: dict[str, _TypedRelation] = {}
    work = _JoinWork()
    fact_types = {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}
    for component in derivation_strata(model.model_dump()):
        fact_type_id = component[0]
        fact_type = fact_types[fact_type_id]
        rule = fact_type["derivation_rule"]
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        binding_lineages = _binding_lineages(rule, bindings, fact_view, fact_lineages)
        projected_rows = _project_extension(fact_type, bindings, work)
        projected_lineage = _project_lineage(fact_type, bindings, binding_lineages)
        relation = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            projected_rows,
            row_lineage=projected_lineage,
        )
        facts[fact_type_id] = _relation_facts({fact_type_id: relation})[fact_type_id]
        fact_lineages[fact_type_id] = relation.row_lineage
        extensions[fact_type_id] = relation
    return _ExtensionResult(MappingProxyType(extensions), work)


def _rule_uses_exact_terms(rule: Any) -> bool:
    if not isinstance(rule, dict):
        return False
    return any(
        "where" in clause or "aggregate" in clause
        or (isinstance(clause.get("head"), dict) and any(
            is_function_term(term) for term in clause["head"].values()
        ))
        for clause in iter_derivation_clauses(rule)
    )


def _aggregate_identity_token(value: Scalar | Fraction) -> bytes:
    """Exact numeric identity for aggregate contributions only.

    The predecessor identity encoder is pinned; aggregate arithmetic also
    produces Fraction values and may encounter integers past Python's decimal
    string conversion guard.
    """
    if isinstance(value, (int, Fraction)) and not isinstance(value, bool):
        rational = Fraction(value)
        return (
            '["number",['
            + str(Decimal(rational.numerator))
            + ","
            + str(Decimal(rational.denominator))
            + "]]"
        ).encode()
    return _identity_token(value)


def _aggregate_bindings(
    rule: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    work: _ExactJoinWork,
    analysis: AggregateAnalysis | None = None,
) -> tuple[list[dict[str, Any]], RelationUnavailable | None]:
    """Collapse body bindings into exact aggregate groups.

    The distinct contribution token deliberately contains both the ordered
    ``over`` binding and the evaluated ``of`` value.  It prevents duplicate
    proof paths from changing an aggregate while retaining distinct rows whose
    ``of`` term happens to have the same value.
    """
    aggregate = rule.get("aggregate")
    if not isinstance(aggregate, dict):
        return [dict(binding) for binding in bindings], None
    if analysis is not None and analysis.issue is None:
        over = analysis.over_variables
        result_name = analysis.result_variable or ""
        function = analysis.function or ""
        group_names = analysis.group_variables
    else:
        over = tuple(str(item)[1:] for item in aggregate.get("over", ()) if isinstance(item, str))
        result_name = str(aggregate.get("as", ""))[1:]
        function = str(aggregate.get("fn"))
        head = rule.get("head")
        group_names = tuple(
            sorted(
                {
                    variable
                    for term in head.values()
                    for variable in term_variables(term)
                    if variable != result_name
                }
            )
            if isinstance(head, dict)
            else ()
        )
    groups: dict[tuple[tuple[str, bytes], ...], list[Mapping[str, Scalar]]] = {}

    def too_wide(value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            bits = value.bit_length()
        elif isinstance(value, Fraction):
            bits = max(value.numerator.bit_length(), value.denominator.bit_length())
        else:
            return False
        work.max_exact_value_bits = max(work.max_exact_value_bits, bits)
        work.aggregate_maximum_value_bits = max(work.aggregate_maximum_value_bits, bits)
        return bits > DEFAULT_LIMITS.max_value_bits

    for binding in bindings:
        work.aggregate_candidate_bindings += 1
        if any(too_wide(binding[name]) for name in group_names if name in binding):
            return [], RelationUnavailable(
                "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(binding))
            )
        key = tuple(
            (name, _aggregate_identity_token(binding[name]))
            for name in group_names
            if name in binding
        )
        work.aggregate_identity_tokens += len(key)
        work.aggregate_group_lookups += 1
        groups.setdefault(key, []).append(binding)
    work.aggregate_groups += len(groups)

    collapsed: list[dict[str, Any]] = []
    for key in sorted(groups):
        members = groups[key]
        contributions: dict[tuple[bytes, ...], Any] = {}
        for binding in members:
            work.aggregate_contribution_terms += 1
            value = evaluate_term(
                analysis.value_term
                if analysis is not None and analysis.issue is None
                else aggregate.get("of"),
                binding,
            )
            _count_term_work(work, value)
            if not value.available:
                return [], RelationUnavailable(
                    "<aggregate>", str(value.reason), MappingProxyType(dict(binding))
                )
            if too_wide(value.value) or any(too_wide(binding[name]) for name in over):
                return [], RelationUnavailable(
                    "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(binding))
                )
            token = tuple(_aggregate_identity_token(binding[name]) for name in over) + (
                _aggregate_identity_token(value.value),
            )
            work.aggregate_identity_tokens += len(token)
            contributions.setdefault(token, value.value)
        # A contribution is a set member. Fold in canonical token order so
        # population row order cannot change bounded-width availability.
        values = [contributions[token] for token in sorted(contributions)]
        work.aggregate_distinct_contributions += len(values)
        if function == "count":
            result: Any = len(values)
            work.aggregate_exact_operations += 1
        else:
            numbers: list[Fraction] = []
            for value in values:
                if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
                    return [], RelationUnavailable(
                        "<aggregate>",
                        "aggregate:non-integer-input",
                        MappingProxyType(dict(members[0])),
                    )
                numbers.append(Fraction(value))
            if function == "sum":
                result = Fraction()
                for number in numbers:
                    result += number
                    work.aggregate_exact_operations += 1
                    if too_wide(result):
                        return [], RelationUnavailable(
                            "<aggregate>",
                            "term:exact-value-too-wide",
                            MappingProxyType(dict(members[0])),
                        )
            elif function == "min":
                result = min(numbers)
                work.aggregate_exact_operations += max(0, len(numbers) - 1)
            elif function == "max":
                result = max(numbers)
                work.aggregate_exact_operations += max(0, len(numbers) - 1)
            elif function == "avg":
                result = Fraction()
                for number in numbers:
                    result += number
                    work.aggregate_exact_operations += 1
                    if too_wide(result):
                        return [], RelationUnavailable(
                            "<aggregate>",
                            "term:exact-value-too-wide",
                            MappingProxyType(dict(members[0])),
                        )
                result /= len(numbers)
                work.aggregate_exact_operations += 1
            else:
                return [], RelationUnavailable(
                    "<aggregate>", "aggregate:unknown-function", MappingProxyType(dict(members[0]))
                )
            if isinstance(result, Fraction) and result.denominator == 1:
                result = result.numerator
            if too_wide(result):
                return [], RelationUnavailable(
                    "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(members[0]))
                )
        representative = {name: members[0][name] for name in group_names}
        representative[result_name] = result
        collapsed.append(representative)
    return collapsed, None


def _model_uses_exact_derivations(model: Model) -> bool:
    return any(_rule_uses_exact_terms(item.get("derivation_rule")) for item in model.fact_types)


def _requires_fixpoint(model: Model) -> bool:
    if any(
        "clauses" in rule
        for item in model.fact_types
        if isinstance(rule := item.get("derivation_rule"), dict)
    ):
        return True
    dependencies = derivation_dependencies(model.model_dump())
    return any(head in children for head, children in dependencies.items()) or any(
        len(component) > 1 for component in derivation_strata(model.model_dump())
    )


def _evaluate_stratified_extensions(
    model: Model,
    relations: Mapping[str, _TypedRelation],
    *,
    heads: Collection[str] | None = None,
    prior_unavailable: Mapping[str, RelationUnavailable] | None = None,
    prior_possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] | None = None,
    observe_partial: Callable[[str, frozenset[tuple[bytes, ...]], frozenset[tuple[bytes, ...]]], None] | None = None,
    exact: bool = False,
) -> _ExactExtensionResult | _ExtensionResult:
    """Evaluate each SCC to its least finite extension from one relation snapshot.

    A selective evaluation recomputes complete requested SCCs from empty
    computed relations. Previously completed lower strata remain available.
    """
    document = model.model_dump()
    strata = derivation_strata(document)
    selected = None if heads is None else {str(head) for head in heads}
    if selected is not None:
        selected = {
            member for component in strata if selected.intersection(component)
            for member in component
        }
    fact_types = {str(row.get("id")): row for row in model.fact_types}
    state = dict(relations)
    extensions: dict[str, _TypedRelation] = {}
    unavailable: dict[str, RelationUnavailable] = dict(prior_unavailable or {})
    work = _FixpointJoinWork()
    partial = any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in state.values() for row in relation.rows for value in row
    ) or any(
        isinstance(value, _Wildcard)
        for rows in (prior_possible or {}).values() for row in rows for value in row
    )
    possible: dict[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] = {}
    if partial:
        for fact_type_id, relation in tuple(state.items()):
            possible[fact_type_id] = tuple(
                tuple(
                    _symbolic_value(value, primitive, (fact_type_id, index, role))
                    for (role, primitive), value in zip(relation.roles, row, strict=True)
                )
                for index, row in enumerate(relation.rows)
            )
            retained = [
                (row, lineage)
                for row, lineage in zip(relation.rows, relation.row_lineage, strict=True)
                if not any(isinstance(value, dict) and set(value) == {"$opaque"} for value in row)
            ]
            state[fact_type_id] = _TypedRelation(
                fact_type_id, relation.roles,
                tuple(row for row, _ in retained),
                row_lineage=tuple(lineage for _, lineage in retained),
            )
        possible.update(prior_possible or {})
    for component in strata:
        if selected is not None and not selected.intersection(component):
            continue
        for head_id in component:
            fact_type = fact_types[head_id]
            state[head_id] = _TypedRelation(head_id, _relation_roles(model, fact_type), ())
            unavailable.pop(head_id, None)
            if partial:
                possible[head_id] = ()
        facts = dict(_relation_facts(state))
        lineages = {head_id: relation.row_lineage for head_id, relation in state.items()}
        for head_id in component:
            facts[head_id] = []
            lineages[head_id] = []
        delta_facts: dict[str, tuple[Mapping[str, Scalar], ...]] = {
            head_id: () for head_id in component
        }
        delta_lineages: dict[str, tuple[RowLineage, ...]] = {
            head_id: () for head_id in component
        }
        accumulated: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {
            head_id: {} for head_id in component
        }
        iteration = 0
        while True:
            work.fixpoint_iterations += 1
            if partial:
                must_facts = dict(_relation_facts(state))
                may_facts = {
                    fact_type_id: _partial_row_facts(state[fact_type_id].roles, rows)
                    for fact_type_id, rows in possible.items()
                }
                must_lineages = {
                    fact_type_id: relation.row_lineage for fact_type_id, relation in state.items()
                }
                next_must: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {}
                next_may: dict[str, dict[tuple[bytes, ...], tuple[Scalar | _Wildcard, ...]]] = {}
                partial_failure: RelationUnavailable | None = None
                for head_id in component:
                    head = fact_types[head_id]
                    next_must[head_id] = {
                        tuple(_partial_token(value) for value in row): (row, lineage)
                        for row, lineage in zip(state[head_id].rows, state[head_id].row_lineage, strict=True)
                    }
                    next_may[head_id] = {
                        tuple(_partial_token(value) for value in row): row
                        for row in possible[head_id]
                    }
                    for clause in iter_derivation_clauses(head["derivation_rule"]):
                        dependency = next((
                            str(atom.get("fact_type"))
                            for key in ("body", "negate")
                            for atom in clause.get(key) or ()
                            if str(atom.get("fact_type")) in unavailable
                        ), None)
                        if dependency is not None:
                            origin = unavailable[dependency]
                            partial_failure = RelationUnavailable(
                                head_id, origin.reason, origin.binding, dependency
                            )
                            break
                        for definite in (True, False):
                            try:
                                produced = _partial_clause_rows(
                                    model, head, clause, must_facts, may_facts, must_lineages,
                                    work, definite=definite,
                                )
                            except _PartialTermFailure as failure:
                                partial_failure = RelationUnavailable(
                                    head_id, failure.reason, failure.binding
                                )
                                break
                            for row, proof in produced:
                                key = tuple(_partial_token(value) for value in row)
                                if definite:
                                    next_must[head_id].setdefault(key, (row, proof))
                                next_may[head_id].setdefault(key, row)
                        if partial_failure is not None:
                            break
                    if partial_failure is not None:
                        break
                if partial_failure is not None:
                    for head_id in component:
                        unavailable[head_id] = RelationUnavailable(
                            head_id, partial_failure.reason, partial_failure.binding,
                            partial_failure.source_relation,
                        )
                        state.pop(head_id, None)
                        possible.pop(head_id, None)
                    break
                changed = False
                for head_id in component:
                    old_must = {
                        tuple(_partial_token(value) for value in row)
                        for row in state[head_id].rows
                    }
                    old_may = {
                        tuple(_partial_token(value) for value in row)
                        for row in possible[head_id]
                    }
                    changed |= old_must != set(next_must[head_id]) or old_may != set(next_may[head_id])
                    ordered_must = [next_must[head_id][key] for key in sorted(next_must[head_id])]
                    state[head_id] = _TypedRelation(
                        head_id, _relation_roles(model, fact_types[head_id]),
                        tuple(row for row, _ in ordered_must),
                        row_lineage=tuple(proof for _, proof in ordered_must),
                    )
                    possible[head_id] = tuple(next_may[head_id][key] for key in sorted(next_may[head_id]))
                    work.canonical_insertions += len(set(next_must[head_id]) - old_must)
                    work.canonical_insertions += len(set(next_may[head_id]) - old_may)
                    if observe_partial is not None:
                        observe_partial(
                            head_id, frozenset(next_must[head_id]), frozenset(next_may[head_id])
                        )
                if not changed:
                    extensions.update({head_id: state[head_id] for head_id in component})
                    break
                iteration += 1
                continue
            additions: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {
                head_id: {} for head_id in component
            }
            failure: RelationUnavailable | None = None
            for head_id in component:
                fact_type = fact_types[head_id]
                derivation = str(fact_type.get("derivation"))
                for clause in iter_derivation_clauses(fact_type["derivation_rule"]):
                    dependency = next((
                        str(atom.get("fact_type"))
                        for key in ("body", "negate")
                        for atom in clause.get(key) or ()
                        if str(atom.get("fact_type")) in unavailable
                    ), None)
                    if dependency is not None:
                        origin = unavailable[dependency]
                        failure = RelationUnavailable(head_id, origin.reason, origin.binding, dependency)
                        record_branch(f"derivation:extension:{derivation}:exact-origin-propagated")
                        break
                    recursive_atoms = [
                        str(atom.get("fact_type")) for atom in clause.get("body") or ()
                        if str(atom.get("fact_type")) in component
                    ]
                    if (iteration == 0 and recursive_atoms) or (iteration > 0 and not recursive_atoms):
                        continue
                    # One recursive atom reads only the preceding delta. A
                    # multi-recursive body retains the full snapshot until its
                    # atom-specific delta variants are needed.
                    if len(recursive_atoms) == 1:
                        recursive_id = recursive_atoms[0]
                        fact_view = {**facts, recursive_id: delta_facts[recursive_id]}
                        lineage_view = {
                            **lineages, recursive_id: delta_lineages[recursive_id]
                        }
                    else:
                        fact_view = facts
                        lineage_view = lineages
                    bindings = _clause_bindings(clause, fact_view, work)
                    aggregate = isinstance(clause.get("aggregate"), dict)
                    if aggregate:
                        analysis = analyze_declared_aggregate(model, clause)
                        bindings, aggregate_failure = _aggregate_bindings(
                            clause, bindings, work, analysis
                        )
                        if aggregate_failure is not None:
                            failure = RelationUnavailable(
                                head_id, aggregate_failure.reason, aggregate_failure.binding
                            )
                            record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-origin")
                            break
                        if not bindings:
                            record_branch(f"derivation:extension:{derivation}:aggregate-group-absent")
                    filtered = []
                    for binding in bindings:
                        keep = True
                        for comparison in clause.get("where") or ():
                            result = compare_terms(
                                str(comparison.get("operator")), comparison.get("left"),
                                comparison.get("right"), binding, bound_cross_product=aggregate,
                            )
                            _count_term_work(work, result)
                            if not result.available:
                                failure = RelationUnavailable(
                                    head_id, str(result.reason), MappingProxyType(dict(binding))
                                )
                                break
                            if result.value is not True:
                                record_branch(f"derivation:extension:{derivation}:exact-where-false")
                                keep = False
                                break
                        if failure is not None:
                            break
                        if keep:
                            filtered.append(binding)
                    if failure is not None:
                        break
                    proofs = (
                        tuple(() for _ in filtered) if aggregate
                        else _binding_lineages(clause, filtered, fact_view, lineage_view)
                    )
                    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
                    for binding, proof in zip(filtered, proofs, strict=True):
                        row = []
                        for role_name in role_names:
                            result = evaluate_term(clause["head"][role_name], binding)
                            _count_term_work(work, result)
                            if not result.available:
                                failure = RelationUnavailable(
                                    head_id, str(result.reason), MappingProxyType(dict(binding))
                                )
                                break
                            try:
                                row.append(materialize_scalar(result.value))
                            except ValueError:
                                failure = RelationUnavailable(
                                    head_id, "term:head-non-integral", MappingProxyType(dict(binding))
                                )
                                break
                            work.head_cells_projected += 1
                        if failure is not None:
                            break
                        typed_row = tuple(row)
                        _witness_row(fact_type, clause, binding, typed_row)
                        key = tuple(_identity_token(value) for value in typed_row)
                        if key not in accumulated[head_id]:
                            additions[head_id].setdefault(key, (typed_row, proof))
                    if failure is not None:
                        break
                    if aggregate:
                        record_branch(f"derivation:extension:{derivation}:aggregate-applied")
                if failure is not None:
                    break
            if failure is not None:
                for head_id in component:
                    unavailable[head_id] = RelationUnavailable(
                        head_id, failure.reason, failure.binding, failure.source_relation
                    )
                    state.pop(head_id, None)
                break
            changed = False
            next_delta: dict[str, list[Mapping[str, Scalar]]] = {
                head_id: [] for head_id in component
            }
            next_lineages: dict[str, list[RowLineage]] = {
                head_id: [] for head_id in component
            }
            for head_id in component:
                role_names = [str(role.get("role_name")) for role in fact_types[head_id].get("roles") or []]
                for key, row in sorted(additions[head_id].items()):
                    if key not in accumulated[head_id]:
                        accumulated[head_id][key] = row
                        work.canonical_insertions += 1
                        changed = True
                        values, proof = row
                        next_delta[head_id].append(MappingProxyType(dict(zip(role_names, values, strict=True))))
                        next_lineages[head_id].append(proof)
                facts[head_id].extend(next_delta[head_id])
                lineages[head_id].extend(next_lineages[head_id])
            if not changed:
                for head_id in component:
                    rows = [accumulated[head_id][key] for key in sorted(accumulated[head_id])]
                    state[head_id] = _TypedRelation(
                        head_id, _relation_roles(model, fact_types[head_id]),
                        tuple(row for row, _lineage in rows),
                        row_lineage=tuple(lineage for _row, lineage in rows),
                    )
                extensions.update({head_id: state[head_id] for head_id in component})
                break
            delta_facts = {head_id: tuple(rows) for head_id, rows in next_delta.items()}
            delta_lineages = {head_id: tuple(rows) for head_id, rows in next_lineages.items()}
            iteration += 1
    if partial:
        return _ExactExtensionResult(
            _PartialExtensions(
                extensions, unavailable=unavailable,
                possible={head: possible[head] for head in extensions},
            ),
            work,
        ) if exact else _ExtensionResult(
            _PartialExtensions(
                extensions, possible={head: possible[head] for head in extensions},
            ),
            work,
        )
    if exact:
        return _ExactExtensionResult(_ExactExtensions(extensions, unavailable=unavailable), work)
    return _ExtensionResult(MappingProxyType(extensions), work)


def _exact_extension_calculator(
    model: Model,
    relations: Mapping[str, _TypedRelation],
    *,
    heads: Collection[str] | None = None,
    prior_unavailable: Mapping[str, RelationUnavailable] | None = None,
) -> _ExactExtensionResult:
    """Evaluate term-bearing derivations without changing the pinned calculator."""
    if _requires_fixpoint(model) or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in relations.values() for row in relation.rows for value in row
    ):
        return _evaluate_stratified_extensions(
            model, relations, heads=heads, prior_unavailable=prior_unavailable, exact=True
        )
    facts = dict(_relation_facts(relations))
    fact_lineages = {
        fact_type_id: relation.row_lineage for fact_type_id, relation in relations.items()
    }
    extensions: dict[str, _TypedRelation] = {}
    unavailable: dict[str, RelationUnavailable] = dict(prior_unavailable or {})
    work = _ExactJoinWork()
    fact_types = {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}
    selected = None if heads is None else frozenset(str(head) for head in heads)
    if selected is not None:
        for head in selected:
            unavailable.pop(head, None)
    for component in derivation_strata(model.model_dump()):
        fact_type_id = component[0]
        if selected is not None and fact_type_id not in selected:
            continue
        fact_type = fact_types[fact_type_id]
        rule = fact_type["derivation_rule"]
        derivation = str(fact_type.get("derivation"))
        uses_exact = _rule_uses_exact_terms(rule)
        uses_aggregate = isinstance(rule.get("aggregate"), dict)
        if uses_exact:
            record_branch(f"derivation:extension:{derivation}:exact-applied")
        dependency = next(
            (
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or ()
                if str(atom.get("fact_type")) in unavailable
            ),
            None,
        )
        if dependency is not None:
            origin = unavailable[dependency]
            unavailable[fact_type_id] = RelationUnavailable(
                fact_type_id,
                origin.reason,
                origin.binding,
                dependency,
            )
            if uses_exact or dependency in unavailable:
                record_branch(f"derivation:extension:{derivation}:exact-origin-propagated")
            if uses_aggregate:
                record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-propagated")
            continue
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        aggregate_analysis = analyze_declared_aggregate(model, rule) if uses_aggregate else None
        bindings, aggregate_failure = _aggregate_bindings(rule, bindings, work, aggregate_analysis)
        if aggregate_failure is not None:
            unavailable[fact_type_id] = RelationUnavailable(
                fact_type_id,
                aggregate_failure.reason,
                aggregate_failure.binding,
            )
            if uses_aggregate:
                record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-origin")
            continue
        if uses_aggregate and not bindings:
            record_branch(f"derivation:extension:{derivation}:aggregate-group-absent")
        filtered: list[dict[str, Scalar]] = []
        failed: RelationUnavailable | None = None
        for binding in bindings:
            keep = True
            for comparison in rule.get("where") or ():
                result = compare_terms(
                    str(comparison.get("operator")),
                    comparison.get("left"),
                    comparison.get("right"),
                    binding,
                    bound_cross_product=uses_aggregate,
                )
                _count_term_work(work, result)
                if not result.available:
                    failed = RelationUnavailable(
                        fact_type_id,
                        str(result.reason),
                        MappingProxyType(dict(binding)),
                    )
                    break
                if result.value is not True:
                    if uses_exact:
                        record_branch(f"derivation:extension:{derivation}:exact-where-false")
                    if uses_aggregate:
                        record_branch(
                            f"derivation:extension:{derivation}:aggregate-post-filter-false"
                        )
                    keep = False
                    break
            if failed is not None:
                break
            if keep:
                filtered.append(binding)
        if failed is not None:
            unavailable[fact_type_id] = failed
            continue

        binding_lineages = (
            tuple(() for _ in filtered)
            if isinstance(rule.get("aggregate"), dict)
            else _binding_lineages(rule, filtered, fact_view, fact_lineages)
        )
        head = rule["head"]
        role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
        unique_rows: dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]] = {}
        for binding, lineage in zip(filtered, binding_lineages, strict=True):
            row: list[Scalar] = []
            for role_name in role_names:
                result = evaluate_term(head[role_name], binding)
                _count_term_work(work, result)
                if not result.available:
                    failed = RelationUnavailable(
                        fact_type_id,
                        str(result.reason),
                        MappingProxyType(dict(binding)),
                    )
                    break
                try:
                    value = materialize_scalar(result.value)
                except ValueError:
                    failed = RelationUnavailable(
                        fact_type_id,
                        "term:head-non-integral",
                        MappingProxyType(dict(binding)),
                    )
                    break
                row.append(value)
                work.head_cells_projected += 1
            if failed is not None:
                break
            typed_row = tuple(row)
            key = tuple(_identity_token(value) for value in typed_row)
            unique_rows.setdefault(key, (typed_row, lineage))
            if uses_exact:
                record_branch(f"derivation:extension:{derivation}:exact-head-computed")
        if failed is not None:
            unavailable[fact_type_id] = failed
            continue
        ordered = [unique_rows[key] for key in sorted(unique_rows)]
        relation = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            tuple(item[0] for item in ordered),
            row_lineage=tuple(item[1] for item in ordered),
        )
        facts[fact_type_id] = _relation_facts({fact_type_id: relation})[fact_type_id]
        if uses_aggregate:
            record_branch(f"derivation:extension:{derivation}:aggregate-applied")
        fact_lineages[fact_type_id] = relation.row_lineage
        extensions[fact_type_id] = relation
    return _ExactExtensionResult(
        _ExactExtensions(extensions, unavailable=unavailable),
        work,
    )


def structured_extension_facts(
    model: Model,
    population: Population,
) -> Mapping[str, tuple[Mapping[str, Scalar], ...]]:
    """Return the computed structured extensions as fact-shaped rows.

    This is the transition layer's deliberately small adapter to the checker-owned
    extension calculator.  It keeps one derivation implementation while exposing
    neither the calculator's typed-relation internals nor its proof bookkeeping.
    """
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    calculated = (
        _exact_extension_calculator(model, _base_relations(model, population))
        if _model_uses_exact_derivations(model)
        else _python_extension_calculator(model, _base_relations(model, population))
    )
    return MappingProxyType(
        {
            fact_type_id: tuple(rows)
            for fact_type_id, rows in _relation_facts(calculated.extensions).items()
        }
    )


def exact_extension_envelope(model: Model, population: Population) -> dict[str, Any]:
    """Canonical parity envelope for exact relations and unavailability."""
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    calculated = _exact_extension_calculator(model, _base_relations(model, population))
    heads = [
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]
    relations: dict[str, list[list[str]]] = {}
    unavailable: dict[str, dict[str, Any]] = {}
    for head in heads:
        failure = calculated.extensions.unavailable.get(head)
        if failure is not None:
            unavailable[head] = {
                "reason": failure.reason,
                "binding": {
                    "$" + variable: _aggregate_identity_token(value).decode("utf-8")
                    for variable, value in sorted(failure.binding.items())
                },
                "source_relation": failure.source_relation,
            }
            continue
        relation = calculated.extensions.get(head)
        relations[head] = (
            sorted(
                [[_identity_token(value).decode("utf-8") for value in row] for row in relation.rows]
            )
            if relation is not None
            else []
        )
    return {"relations": relations, "unavailable": unavailable}


@dataclass(frozen=True, slots=True)
class DynamicRefreshWork:
    fixpoint_iterations: int = 0
    canonical_insertions: int = 0
    selected_heads: int = 0
    strata_evaluated: int = 0
    body_atoms_evaluated: int = 0
    projected_rows: int = 0
    atom_role_terms_read: int = 0
    positive_candidate_rows_emitted: int = 0
    join_candidates_indexed: int = 0
    join_left_bindings_probed: int = 0
    join_matches_merged: int = 0
    component_product_rows_emitted: int = 0
    negation_rows_indexed: int = 0
    negation_bindings_probed: int = 0
    head_cells_projected: int = 0
    term_nodes_visited: int = 0
    term_operations: int = 0
    max_exact_value_bits: int = 0
    aggregate_candidate_bindings: int = 0
    aggregate_contribution_terms: int = 0
    aggregate_identity_tokens: int = 0
    aggregate_distinct_contributions: int = 0
    aggregate_group_lookups: int = 0
    aggregate_groups: int = 0
    aggregate_exact_operations: int = 0
    aggregate_maximum_value_bits: int = 0


@dataclass(frozen=True, slots=True)
class StructuredExtensionView:
    facts: Mapping[str, tuple[Mapping[str, Scalar], ...]]
    recomputed: tuple[str, ...]
    work: DynamicRefreshWork
    unavailable: Mapping[str, RelationUnavailable] = field(
        default_factory=lambda: MappingProxyType({})
    )
    possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )


def _public_refresh_work(
    work: _JoinWork,
    *,
    selected_heads: int,
    strata_evaluated: int,
    body_atoms_evaluated: int,
    projected_rows: int,
) -> DynamicRefreshWork:
    return DynamicRefreshWork(
        fixpoint_iterations=int(getattr(work, "fixpoint_iterations", 0)),
        canonical_insertions=int(getattr(work, "canonical_insertions", 0)),
        selected_heads=selected_heads,
        strata_evaluated=strata_evaluated,
        body_atoms_evaluated=body_atoms_evaluated,
        projected_rows=projected_rows,
        atom_role_terms_read=work.atom_role_terms_read,
        positive_candidate_rows_emitted=work.positive_candidate_rows_emitted,
        join_candidates_indexed=work.join_candidates_indexed,
        join_left_bindings_probed=work.join_left_bindings_probed,
        join_matches_merged=work.join_matches_merged,
        component_product_rows_emitted=work.component_product_rows_emitted,
        negation_rows_indexed=work.negation_rows_indexed,
        negation_bindings_probed=work.negation_bindings_probed,
        head_cells_projected=work.head_cells_projected,
        term_nodes_visited=int(getattr(work, "term_nodes_visited", 0)),
        term_operations=int(getattr(work, "term_operations", 0)),
        max_exact_value_bits=int(getattr(work, "max_exact_value_bits", 0)),
        aggregate_candidate_bindings=int(getattr(work, "aggregate_candidate_bindings", 0)),
        aggregate_contribution_terms=int(getattr(work, "aggregate_contribution_terms", 0)),
        aggregate_identity_tokens=int(getattr(work, "aggregate_identity_tokens", 0)),
        aggregate_distinct_contributions=int(getattr(work, "aggregate_distinct_contributions", 0)),
        aggregate_group_lookups=int(getattr(work, "aggregate_group_lookups", 0)),
        aggregate_groups=int(getattr(work, "aggregate_groups", 0)),
        aggregate_exact_operations=int(getattr(work, "aggregate_exact_operations", 0)),
        aggregate_maximum_value_bits=int(getattr(work, "aggregate_maximum_value_bits", 0)),
    )


def _extension_fact_map(
    extensions: Mapping[str, _TypedRelation],
) -> Mapping[str, tuple[Mapping[str, Scalar], ...]]:
    return MappingProxyType(
        {fact_type_id: tuple(rows) for fact_type_id, rows in _relation_facts(extensions).items()}
    )


def structured_extension_view(
    model: Model,
    population: Population,
    *,
    previous: Mapping[str, tuple[Mapping[str, Scalar], ...]] | None = None,
    previous_unavailable: Mapping[str, RelationUnavailable] | None = None,
    previous_possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] | None = None,
    refresh: Collection[str] | None = None,
) -> StructuredExtensionView:
    """Compute all structured rows or selectively refresh named strata.

    Selective evaluation starts from asserted relations plus the prior complete
    extension map. Requested heads are replaced in dependency order; every
    unrequested structured relation remains byte-for-byte equivalent to the
    supplied prior view.
    """
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    classifications = {row.fact_type: row for row in derivation_classifications(model.model_dump())}
    strata = derivation_strata(model.model_dump())
    ordered = tuple(head for component in strata for head in component)
    if any(row.stability == "dynamic" for row in classifications.values()):
        record_branch("composition:derivation-view:dynamic:applied")

    if _requires_fixpoint(model) or previous_possible or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for rows in population.facts.values() for row in rows for value in row.values()
    ):
        exact = _model_uses_exact_derivations(model)
        requested = set(ordered) if refresh is None else {str(head) for head in refresh}
        unknown = requested - set(ordered)
        if unknown:
            raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
        incomplete = sorted(head for head in requested if not classifications[head].complete)
        if incomplete:
            raise ValueError(f"incomplete structured refresh head(s): {incomplete}")
        if refresh is not None and previous is None:
            raise ValueError("selective structured refresh requires a previous complete view")
        missing_prior_heads = set(ordered) - set(previous or {}) - set(previous_unavailable or {})
        if refresh is not None and missing_prior_heads:
            raise ValueError(
                "selective structured refresh received an incomplete prior envelope; "
                f"missing structured head(s): {sorted(missing_prior_heads)}"
            )
        selected = {
            head for component in strata if requested.intersection(component) for head in component
        }
        if refresh is not None and not selected:
            return StructuredExtensionView(
                facts=MappingProxyType(dict(previous or {})), recomputed=(),
                work=DynamicRefreshWork(),
                unavailable=MappingProxyType(dict(previous_unavailable or {})),
                possible=MappingProxyType(dict(previous_possible or {})),
            )
        relations = dict(_base_relations(model, population))
        fact_types = {str(row.get("id")): row for row in model.fact_types}
        for head, rows in (previous or {}).items():
            if head in fact_types and head in ordered:
                roles = _relation_roles(model, fact_types[head])
                relations[head] = _TypedRelation(
                    head, roles, _rows_from_facts(roles, rows),
                    row_lineage=tuple(() for _row in rows),
                )
        calculated = _evaluate_stratified_extensions(
            model, relations, heads=selected if refresh is not None else None,
            prior_unavailable=previous_unavailable, prior_possible=previous_possible,
            exact=exact,
        )
        facts = dict(previous or {})
        computed = _extension_fact_map(calculated.extensions)
        for head in selected:
            if head in computed:
                facts[head] = computed[head]
            else:
                facts.pop(head, None)
        possible = dict(previous_possible or {})
        for head in selected:
            possible.pop(head, None)
        possible.update(getattr(calculated.extensions, "possible", {}))
        return StructuredExtensionView(
            facts=MappingProxyType(facts),
            recomputed=tuple(head for head in ordered if head in selected),
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(selected), strata_evaluated=len(selected),
                body_atoms_evaluated=sum(
                    len(clause.get("body") or []) + len(clause.get("negate") or [])
                    for head in selected
                    for clause in iter_derivation_clauses(fact_types[head]["derivation_rule"])
                ),
                projected_rows=sum(len(computed.get(head, ())) for head in selected),
            ),
            unavailable=getattr(calculated.extensions, "unavailable", MappingProxyType({})),
            possible=MappingProxyType(possible),
        )

    if refresh is None:
        calculated = (
            _exact_extension_calculator(model, _base_relations(model, population))
            if _model_uses_exact_derivations(model)
            else _python_extension_calculator(model, _base_relations(model, population))
        )
        facts = _extension_fact_map(calculated.extensions)
        return StructuredExtensionView(
            facts=facts,
            recomputed=ordered,
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(ordered),
                strata_evaluated=len(ordered),
                body_atoms_evaluated=sum(
                    len((fact_type.get("derivation_rule") or {}).get("body") or [])
                    + len((fact_type.get("derivation_rule") or {}).get("negate") or [])
                    for fact_type in model.fact_types
                    if str(fact_type.get("id")) in classifications
                ),
                projected_rows=sum(len(rows) for rows in facts.values()),
            ),
            unavailable=getattr(calculated.extensions, "unavailable", MappingProxyType({})),
        )

    if _model_uses_exact_derivations(model):
        requested = frozenset(str(head) for head in refresh)
        unknown = requested - set(classifications)
        if unknown:
            raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
        incomplete = [head for head in requested if not classifications[head].complete]
        if incomplete:
            raise ValueError(f"incomplete structured refresh head(s): {sorted(incomplete)}")
        if previous is None:
            raise ValueError("selective structured refresh requires a previous complete view")
        missing_prior_heads = set(ordered) - set(previous)
        if missing_prior_heads and previous_unavailable is None:
            raise ValueError(
                "selective exact refresh requires previous_unavailable when the prior "
                f"fact view omits structured head(s): {sorted(missing_prior_heads)}"
            )
        incomplete_prior_heads = missing_prior_heads - set(previous_unavailable or {})
        if incomplete_prior_heads:
            raise ValueError(
                "selective exact refresh received an incomplete prior envelope; "
                f"missing structured head(s): {sorted(incomplete_prior_heads)}"
            )
        if not requested:
            return StructuredExtensionView(
                facts=MappingProxyType(dict(previous)),
                recomputed=(),
                work=DynamicRefreshWork(),
                unavailable=MappingProxyType(dict(previous_unavailable or {})),
            )
        fact_types = {str(row.get("id")): row for row in model.fact_types}
        relations = dict(_base_relations(model, population))
        for head in ordered:
            if head not in previous:
                continue
            fact_type = fact_types[head]
            roles = _relation_roles(model, fact_type)
            relations[head] = _TypedRelation(
                head,
                roles,
                _rows_from_facts(roles, previous[head]),
            )
        calculated = _exact_extension_calculator(
            model,
            relations,
            heads=requested,
            prior_unavailable=previous_unavailable,
        )
        current = dict(previous or {})
        exact_facts = _extension_fact_map(calculated.extensions)
        for head in requested:
            if head in exact_facts:
                current[head] = exact_facts[head]
            else:
                current.pop(head, None)
        return StructuredExtensionView(
            facts=MappingProxyType(current),
            recomputed=tuple(head for head in ordered if head in requested),
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(requested),
                strata_evaluated=len(requested),
                body_atoms_evaluated=sum(
                    len((fact_type.get("derivation_rule") or {}).get("body") or [])
                    + len((fact_type.get("derivation_rule") or {}).get("negate") or [])
                    for fact_type in model.fact_types
                    if str(fact_type.get("id")) in requested
                ),
                projected_rows=sum(len(exact_facts.get(head, ())) for head in requested),
            ),
            unavailable=calculated.extensions.unavailable,
        )

    requested = frozenset(str(head) for head in refresh)
    unknown = requested - set(classifications)
    if unknown:
        raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
    incomplete = [head for head in requested if not classifications[head].complete]
    if incomplete:
        raise ValueError(f"incomplete structured refresh head(s): {sorted(incomplete)}")
    if previous is None:
        raise ValueError("selective structured refresh requires a previous complete view")
    missing_previous = set(classifications) - set(previous)
    if missing_previous:
        raise ValueError(f"previous structured view omits head(s): {sorted(missing_previous)}")
    if not requested:
        return StructuredExtensionView(
            facts=MappingProxyType(
                {head: tuple(rows) for head, rows in previous.items() if head in classifications}
            ),
            recomputed=(),
            work=DynamicRefreshWork(),
        )

    fact_types = {str(row.get("id")): row for row in model.fact_types}
    relations = dict(_base_relations(model, population))
    for head in ordered:
        fact_type = fact_types[head]
        roles = _relation_roles(model, fact_type)
        relations[head] = _TypedRelation(
            head,
            roles,
            _rows_from_facts(roles, previous[head]),
        )
    facts = dict(_relation_facts(relations))
    work = _JoinWork()
    recomputed: list[str] = []
    body_atoms_evaluated = 0
    projected_rows = 0
    for head in ordered:
        if head not in requested:
            continue
        fact_type = fact_types[head]
        rule = fact_type["derivation_rule"]
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        rows = _project_extension(fact_type, bindings, work)
        relation = _TypedRelation(head, _relation_roles(model, fact_type), rows)
        relations[head] = relation
        facts[head] = _relation_facts({head: relation})[head]
        recomputed.append(head)
        body_atoms_evaluated += len(rule.get("body") or []) + len(rule.get("negate") or [])
        projected_rows += len(rows)

    extension_relations = MappingProxyType({head: relations[head] for head in ordered})
    return StructuredExtensionView(
        facts=_extension_fact_map(extension_relations),
        recomputed=tuple(recomputed),
        work=_public_refresh_work(
            work,
            selected_heads=len(requested),
            strata_evaluated=len(recomputed),
            body_atoms_evaluated=body_atoms_evaluated,
            projected_rows=projected_rows,
        ),
    )


def derivation_claims_against(
    model: Model,
    claimed: Population,
    computed_from: Population,
) -> list[DerivationVerdict]:
    """Compare one population's claims with another population's extension."""
    if not claimed.matches_validation_marker(model):
        raise UnvalidatedPopulationError(claimed, model)
    if not computed_from.matches_validation_marker(model):
        raise UnvalidatedPopulationError(computed_from, model)
    calculated = (
        _exact_extension_calculator(model, _base_relations(model, computed_from))
        if _model_uses_exact_derivations(model)
        else _python_extension_calculator(model, _base_relations(model, computed_from))
    )
    return [
        _exact_derivation_obligation(
            fact_type,
            claimed,
            calculated.extensions.get(str(fact_type.get("id"))),
            getattr(calculated.extensions, "unavailable", {}).get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]


def _rows_by_identity(relation: _TypedRelation) -> dict[tuple[bytes, ...], tuple[Scalar, ...]]:
    return {tuple(_identity_token(value) for value in row): row for row in relation.rows}


def _witness(
    relation: _TypedRelation,
    row: Sequence[Scalar],
) -> dict[str, Scalar]:
    return {
        role_name: value for (role_name, _primitive), value in zip(relation.roles, row, strict=True)
    }


def _derivation_obligation(
    fact_type: dict[str, Any],
    population: Population,
    computed: _TypedRelation | None,
    possible: tuple[tuple[Scalar | _Wildcard, ...], ...] | None = None,
) -> DerivationVerdict:
    import json

    fact_type_id = str(fact_type.get("id"))
    derivation = str(fact_type.get("derivation"))
    common: dict[str, Any] = {
        "derivation_ref": derivation_address(fact_type_id),
        "fact_type": fact_type_id,
        "derivation": derivation,
    }
    if fact_type_id not in population.covers:
        return DerivationVerdict(
            **common,
            verdict="unchecked",
            message=f"No derivation claim was made for '{fact_type_id}'.",
            reason_code=DERIVATION_REASON_CODES[0],
            scope_id=f"derivation:extension:{derivation}:unchecked-not-covered",
        )
    if computed is None:
        return DerivationVerdict(
            **common,
            verdict="unchecked",
            message=f"The derivation rule for '{fact_type_id}' is opaque.",
            reason_code=DERIVATION_REASON_CODES[1],
            scope_id=f"derivation:extension:{derivation}:unchecked-rule-opaque",
        )

    claimed = _TypedRelation(
        fact_type_id,
        computed.roles,
        _rows_from_facts(computed.roles, population.facts.get(fact_type_id, ())),
    )
    computed_rows = _rows_by_identity(computed)
    opaque_claims = [row for row in claimed.rows if any(isinstance(v, dict) for v in row)]
    claim_patterns = [
        tuple(_symbolic_value(value, primitive, (fact_type_id, index, role))
              for (role, primitive), value in zip(claimed.roles, row, strict=True))
        for index, row in enumerate(opaque_claims)
    ]
    concrete_claimed = _TypedRelation(
        fact_type_id, claimed.roles,
        tuple(row for row in claimed.rows if not any(isinstance(v, dict) for v in row)),
    )
    claimed_rows = _rows_by_identity(concrete_claimed)
    missing = sorted(
        key for key in set(computed_rows) - set(claimed_rows)
        if not any(all(_partial_compatible(a, b) for a, b in zip(
            computed_rows[key], pattern, strict=True)) for pattern in claim_patterns)
    )
    surplus = sorted(
        key for key in set(claimed_rows) - set(computed_rows)
        if possible is None or not any(
            all(_partial_compatible(left, right) for left, right in zip(claimed_rows[key], pattern, strict=True))
            for pattern in possible
        )
    )
    unresolved = sorted(
        key for key in set(claimed_rows) - set(computed_rows)
        if possible is not None and any(
            all(_partial_compatible(left, right) for left, right in zip(claimed_rows[key], pattern, strict=True))
            for pattern in possible
        )
    )
    findings: list[DerivationFinding] = []
    if missing:
        record_branch(f"derivation:finding:{derivation}:incomplete")
        witness = _witness(computed, computed_rows[missing[0]])
        rendered = json.dumps(witness, ensure_ascii=False, separators=(",", ":"))
        findings.append(
            DerivationFinding(
                kind="derived-extension-incomplete",
                message=verbalize.derivation_incomplete_message(fact_type_id, rendered),
                witness=witness,
            )
        )
    if surplus and derivation == "derived":
        record_branch("derivation:finding:derived:unsound")
        witness = _witness(claimed, claimed_rows[surplus[0]])
        rendered = json.dumps(witness, ensure_ascii=False, separators=(",", ":"))
        findings.append(
            DerivationFinding(
                kind="derived-extension-unsound",
                message=verbalize.derivation_unsound_message(fact_type_id, rendered),
                witness=witness,
            )
        )
    if unresolved or opaque_claims:
        record_branch(f"derivation:finding:{derivation}:unresolved")
        witness = (_witness(claimed, claimed_rows[unresolved[0]]) if unresolved
                   else {role: None if isinstance(value, dict) else value
                         for (role, _primitive), value in zip(
                             claimed.roles, opaque_claims[0], strict=True)})
        findings.append(
            DerivationFinding(
                kind="derived-extension-unresolved",
                message=f"The claimed row in '{fact_type_id}' may follow from the derivation: "
                        + json.dumps(witness, ensure_ascii=False, separators=(",", ":")),
                witness=witness,
            )
        )
    if findings:
        if all(finding.kind == "derived-extension-unresolved" for finding in findings):
            return DerivationVerdict(
                **common,
                verdict="unchecked",
                message=f"The derivation claim for '{fact_type_id}' has unresolved membership.",
                findings=findings,
                reason_code="derived-unknown",
                scope_id=f"derivation:extension:{derivation}:unchecked-derived-unknown",
            )
        return DerivationVerdict(
            **common,
            verdict="fail",
            message=f"The derivation claim for '{fact_type_id}' differs from its extension.",
            findings=findings,
            scope_id=f"derivation:extension:{derivation}:violated:alethic",
        )
    return DerivationVerdict(
        **common,
        verdict="pass",
        message=f"The derivation claim for '{fact_type_id}' matches its extension.",
        scope_id=f"derivation:extension:{derivation}:clean",
    )


def evaluate_derivations_legacy(
    model: Model,
    population: Population,
    *,
    calculator: ExtensionCalculator = _python_extension_calculator,
) -> tuple[Mapping[str, _TypedRelation], list[DerivationVerdict]]:
    structured = [
        fact_type
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]
    if not structured:
        return MappingProxyType({}), []
    calculated = calculator(model, _base_relations(model, population))
    obligations = [
        _derivation_obligation(
            fact_type,
            population,
            calculated.extensions.get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]
    return calculated.extensions, obligations


def constraint_view_legacy(
    model: Model,
    population: Population,
    extensions: Mapping[str, _TypedRelation],
) -> _RuledFactView:
    facts: dict[str, tuple[Mapping[str, Scalar], ...]] = {}
    lineages: dict[str, tuple[RowLineage, ...]] = {}
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        rule = fact_type.get("derivation_rule")
        if not isinstance(rule, dict):
            selected = population.facts.get(fact_type_id, ())
            selected_lineage = tuple(
                (("facts", fact_type_id, index),) for index, _row in enumerate(selected)
            )
        elif fact_type.get("derivation") == "semiderived":
            selected = _relation_facts({fact_type_id: extensions[fact_type_id]})[fact_type_id]
            selected_lineage = extensions[fact_type_id].row_lineage
        elif fact_type_id in population.covers:
            selected = population.facts.get(fact_type_id, ())
            selected_lineage = tuple(
                (("facts", fact_type_id, index),) for index, _row in enumerate(selected)
            )
        else:
            selected = ()
            selected_lineage = ()
        facts[fact_type_id] = tuple(MappingProxyType(dict(row)) for row in selected)
        lineages[fact_type_id] = selected_lineage
    instances = MappingProxyType(
        {object_type: tuple(values) for object_type, values in population.instances.items()}
    )
    return _RuledFactView(
        tuple(population.covers),
        instances,
        MappingProxyType(facts),
        MappingProxyType(lineages),
    )


_PHASE3_LEGACY_EVALUATE_DERIVATIONS = evaluate_derivations_legacy
_PHASE3_LEGACY_CONSTRAINT_VIEW = constraint_view_legacy


def _exact_derivation_obligation(
    fact_type: dict[str, Any],
    population: Population,
    computed: _TypedRelation | None,
    unavailable: RelationUnavailable | None,
) -> DerivationVerdict:
    fact_type_id = str(fact_type.get("id"))
    if unavailable is None or fact_type_id not in population.covers:
        return _derivation_obligation(fact_type, population, computed)
    derivation = str(fact_type.get("derivation"))
    event = {
        "term:mod-zero": "unchecked-mod-zero",
        "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
        "term:dependency-unavailable": "unchecked-dependency-unavailable",
        "term:div-zero": "unchecked-div-zero",
        "term:sqrt-negative": "unchecked-sqrt-negative",
        "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
        "term:float-overflow": "unchecked-float-overflow",
    }.get(unavailable.reason, "unchecked-dependency-unavailable")
    reason = unavailable.reason
    if reason not in EXACT_DERIVATION_REASON_CODES:
        reason = "term:dependency-unavailable"
    return DerivationVerdict(
        derivation_ref=derivation_address(fact_type_id),
        fact_type=fact_type_id,
        derivation=derivation,
        verdict="unchecked",
        message=(
            f"The derivation for '{fact_type_id}' is unavailable: {unavailable.reason}; "
            f"binding={dict(unavailable.binding)!r}."
        ),
        reason_code=reason,
        scope_id=f"derivation:extension:{derivation}:{event}",
    )


def _evaluate_derivations_dispatch(
    model: Model,
    population: Population,
    *,
    calculator: ExtensionCalculator = _python_extension_calculator,
) -> tuple[Mapping[str, _TypedRelation], list[DerivationVerdict]]:
    opaque_sources = {
        fact_type_id
        for fact_type_id, rows in population.facts.items()
        if any(
            isinstance(value, dict) and set(value) == {"$opaque"}
            for row in rows for value in row.values()
        )
    }
    if opaque_sources and _PARTIAL_OPAQUE.get():
        calculated = (
            _exact_extension_calculator(model, _base_relations(model, population))
            if _model_uses_exact_derivations(model)
            else _python_extension_calculator(model, _base_relations(model, population))
        )
        possible = getattr(calculated.extensions, "possible", {})
        unavailable = getattr(calculated.extensions, "unavailable", {})
        obligations = []
        for fact_type in model.fact_types:
            if fact_type.get("derivation") not in ("derived", "semiderived") or fact_type.get("derivation_rule") is None:
                continue
            head = str(fact_type.get("id"))
            if head in unavailable:
                obligations.append(_exact_derivation_obligation(
                    fact_type, population, calculated.extensions.get(head), unavailable[head]
                ))
            else:
                obligations.append(_derivation_obligation(
                    fact_type, population, calculated.extensions.get(head), possible.get(head, ())
                ))
        return calculated.extensions, obligations
    if opaque_sources:
        dependencies = derivation_dependencies(model.model_dump())
        affected = set(opaque_sources)
        while True:
            new = {
                head for head, sources in dependencies.items()
                if sources & affected
            } - affected
            if not new:
                break
            affected.update(new)
        safe_facts = {
            fact_type_id: [
                row for row in rows
                if not any(
                    isinstance(value, dict) and set(value) == {"$opaque"}
                    for value in row.values()
                )
            ]
            for fact_type_id, rows in population.facts.items()
        }
        safe_population = population.model_copy(update={"facts": safe_facts})
        safe_extensions, safe_verdicts = _evaluate_derivations_dispatch(
            model, safe_population, calculator=calculator,
        )
        verdicts: list[DerivationVerdict] = []
        for verdict in safe_verdicts:
            if verdict.fact_type not in affected:
                verdicts.append(verdict)
                continue
            verdicts.append(DerivationVerdict(
                derivation_ref=verdict.derivation_ref,
                fact_type=verdict.fact_type,
                derivation=verdict.derivation,
                verdict="unchecked",
                message=f"The derivation for '{verdict.fact_type}' read an opaque role.",
                reason_code="opaque-value",
                scope_id=f"derivation:extension:{verdict.derivation}:unchecked-opaque-value",
            ))
        return MappingProxyType({
            key: value for key, value in safe_extensions.items() if key not in affected
        }), verdicts
    if not _model_uses_exact_derivations(model):
        return evaluate_derivations_legacy(
            model,
            population,
            calculator=calculator,
        )
    calculated = _exact_extension_calculator(model, _base_relations(model, population))
    obligations = [
        _exact_derivation_obligation(
            fact_type,
            population,
            calculated.extensions.get(str(fact_type.get("id"))),
            calculated.extensions.unavailable.get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]
    return calculated.extensions, obligations


def _constraint_view_dispatch(
    model: Model,
    population: Population,
    extensions: Mapping[str, _TypedRelation],
) -> _RuledFactView:
    unavailable = getattr(extensions, "unavailable", {})
    if not unavailable:
        return constraint_view_legacy(model, population, extensions)
    completed = dict(extensions)
    fact_types = {str(item.get("id")): item for item in model.fact_types}
    for fact_type_id in unavailable:
        fact_type = fact_types[fact_type_id]
        completed[fact_type_id] = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            (),
        )
    return constraint_view_legacy(model, population, MappingProxyType(completed))


# B1: the pinned FunctionDefs above remain byte-identical. Public lookup is
# rebound only through new-key dispatch, and term-free models delegate directly
# to the aliased legacy callables.
_evaluate_derivations = _evaluate_derivations_dispatch
_constraint_view = _constraint_view_dispatch


def _guarded_variable_primitives(
    atoms: list[dict[str, Any]], model: Model
) -> dict[str, str | None]:
    """Resolve each variable through its first antecedent binding site."""
    primitives: dict[str, str | None] = {}
    for atom in atoms:
        fact_type_id = str(atom.get("fact_type"))
        binds = atom_bind(atom)
        for role_name, term in binds.items():
            variable = _guarded_variable(term)
            if variable is None or variable in primitives:
                continue
            object_type = _role_object_type(model, fact_type_id, str(role_name))
            primitives[variable] = (
                resolve_primitive(object_type, model) if object_type is not None else None
            )
    return primitives


def _guarded_ground_atom(
    atom: dict[str, Any], binding: dict[str, Any]
) -> tuple[str, list[str], tuple[tuple[Any, ...], ...]] | None:
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return None
    role_names: list[str] = []
    values: list[tuple[Any, ...]] = []
    for role_name, term in binds.items():
        variable = _guarded_variable(term)
        if variable is not None:
            if variable not in binding:
                return None
            term = binding[variable]
        role_names.append(str(role_name))
        values.append(_identity_key(term))
    return str(atom.get("fact_type")), role_names, tuple(values)


def _guarded_atom_index(
    atom: dict[str, Any], population: Population
) -> tuple[str, list[str], set[tuple[tuple[Any, ...], ...]]] | None:
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return None
    fact_type_id = str(atom.get("fact_type"))
    role_names = [str(role_name) for role_name in binds]
    rows: set[tuple[tuple[Any, ...], ...]] = set()
    facts = population.facts.get(fact_type_id, [])
    if not isinstance(facts, Sequence):
        return fact_type_id, role_names, rows
    for fact in facts:
        if isinstance(fact, Mapping) and all(role_name in fact for role_name in role_names):
            rows.add(tuple(_identity_key(fact[role_name]) for role_name in role_names))
    return fact_type_id, role_names, rows


_PHASE3_LEGACY_CHECK = check_legacy


def _guarded_term_failure(
    constraint: Mapping[str, Any], population: Population | _RuledFactView
) -> RelationUnavailable | None:
    """Return the first exact-term failure in an admitted guarded comparison."""
    consequent = constraint.get("consequent")
    comparison = consequent.get("comparison") if isinstance(consequent, Mapping) else None
    if not isinstance(comparison, Mapping):
        return None
    operands = (comparison.get("left"), comparison.get("right"))
    from gnd.terms import is_temporal_node, temporal_nodes

    if any(is_temporal_node(node) for operand in operands for _, node in temporal_nodes(operand)):
        return None  # The streaming correspondence evaluator owns temporal failures.
    if not any(is_function_term(operand) for operand in operands):
        return None
    antecedent = constraint.get("antecedent")
    if not isinstance(antecedent, list):
        return None
    for binding in _guarded_bindings(antecedent, population):
        exact_binding = {variable.removeprefix("$"): value for variable, value in binding.items()}
        for operand in operands:
            result = evaluate_term(operand, exact_binding)
            if not result.available:
                return RelationUnavailable(
                    "<guarded>",
                    str(result.reason),
                    MappingProxyType(dict(exact_binding)),
                )
        record_branch("snapshot:guarded:comparison:exact-success")
    return None


def _term_unavailable_constraint_verdict(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    ref: str,
    unavailable: RelationUnavailable,
) -> ConstraintVerdict:
    family = str(constraint.get("type"))
    reason = unavailable.reason
    if reason not in EXACT_DERIVATION_REASON_CODES:
        reason = "term:dependency-unavailable"
    event = {
        "term:mod-zero": "unchecked-mod-zero",
        "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
        "term:dependency-unavailable": "unchecked-dependency-unavailable",
        "term:div-zero": "unchecked-div-zero",
        "term:sqrt-negative": "unchecked-sqrt-negative",
        "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
        "term:float-overflow": "unchecked-float-overflow",
    }[reason]
    return ConstraintVerdict(
        constraint_ref=ref,
        constraint_type=family,
        modality=str(constraint.get("modality")),
        source=str(constraint.get("source", "")),
        status=str(constraint.get("status", "")),
        verdict="unchecked",
        message=(
            f"Constraint '{ref}' is unavailable because exact term evaluation failed: "
            f"{unavailable.reason}; binding={dict(unavailable.binding)!r}."
        ),
        reason_code=reason,
        scope_id=f"snapshot:{family}:{constraint_variant(constraint, fact_type)}:{event}",
    )


def _record_aggregate_guarded_outcomes(model: Model, verdicts: Sequence[ConstraintVerdict]) -> None:
    """Trace guarded verdicts whose antecedent reads an aggregate head."""
    aggregate_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and isinstance(rule.get("aggregate"), dict)
    }
    if not aggregate_heads:
        return
    by_ref = {verdict.constraint_ref: verdict for verdict in verdicts}
    for index, constraint in enumerate(model.constraints):
        if constraint.get("type") != "guarded" or not any(
            isinstance(atom, dict) and str(atom.get("fact_type")) in aggregate_heads
            for atom in constraint.get("antecedent") or []
        ):
            continue
        verdict = by_ref.get(positional_constraint_ref(None, index))
        if verdict is not None and verdict.verdict in {"pass", "fail", "unchecked"}:
            record_branch(f"snapshot:guarded:aggregate:{verdict.verdict}")


def _partial_constraint_report(
    model: Model, population: Population, report: CheckReport,
) -> CheckReport:
    if not _PARTIAL_OPAQUE.get() or not model.constraints and not any(
        fact_type.get("constraints") for fact_type in model.fact_types
    ):
        return report
    calculated = _evaluate_stratified_extensions(
        model, _base_relations(model, population), exact=_model_uses_exact_derivations(model)
    )
    possible = getattr(calculated.extensions, "possible", {})
    uncertain_heads = {
        head for head, rows in possible.items()
        if any(isinstance(value, _Wildcard) for row in rows for value in row)
    }
    if not uncertain_heads:
        return report
    by_ref: dict[str, tuple[dict[str, Any], dict[str, Any] | None]] = {}
    for fact_type in model.fact_types:
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            by_ref[positional_constraint_ref(str(fact_type.get("id")), index)] = (constraint, fact_type)
    for index, constraint in enumerate(model.constraints):
        by_ref[positional_constraint_ref(None, index)] = (constraint, None)
    changed = False
    verdicts = []
    for verdict in report.verdicts:
        pair = by_ref.get(verdict.constraint_ref)
        if pair is None or verdict.verdict not in {"pass", "vacuous", "fail"}:
            verdicts.append(verdict)
            continue
        constraint, fact_type = pair
        subject = _scope_fact_types(constraint, verdict.constraint_type, model, fact_type)
        if not uncertain_heads.intersection(subject):
            verdicts.append(verdict)
            continue
        if verdict.verdict == "fail" and verdict.constraint_type == "uniqueness":
            # A duplicate among definite rows remains a conclusive failure.
            verdicts.append(verdict)
            continue
        if verdict.verdict == "fail" and verdict.constraint_type == "subset":
            superset = constraint.get("superset_role_seq") or []
            subset = constraint.get("subset_role_seq") or []
            heads = {str(ref.get("fact_type")) for ref in superset}
            if len(heads) == 1 and next(iter(heads)) in uncertain_heads:
                head = next(iter(heads))
                roles = [str(role.get("role_name")) for role in next(
                    ft for ft in model.fact_types if ft.get("id") == head
                ).get("roles") or []]
                patterns = [tuple(row[roles.index(str(ref.get("role")))] for ref in superset)
                            for row in possible[head]]
                try:
                    demands = _role_seq_tuples(model, population, subset)
                    if any(not any(all(_partial_compatible(a, b) for a, b in zip(
                        demand, pattern, strict=True)) for pattern in patterns)
                           for demand in demands):
                        verdicts.append(verdict)
                        continue
                except (TypeError, ValueError):
                    pass
            else:
                verdicts.append(verdict)
                continue
        if verdict.verdict == "pass" and fact_type is not None and verdict.constraint_type == "uniqueness":
            head = str(fact_type.get("id"))
            roles = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
            keys = [tuple(row[roles.index(role)] for role in constraint.get("roles") or [])
                    for row in possible[head]]
            if (all(not isinstance(value, _Wildcard) for key in keys for value in key)
                    and len(set(keys)) == len(keys)):
                verdicts.append(verdict)
                continue
        changed = True
        variant = constraint_variant(constraint, fact_type)
        verdicts.append(ConstraintVerdict(
            constraint_ref=verdict.constraint_ref,
            constraint_type=verdict.constraint_type,
            modality=verdict.modality,
            source=verdict.source,
            status=verdict.status,
            verdict="unchecked",
            message=f"Constraint '{verdict.constraint_ref}' reads a possible-only derived row.",
            reason_code="derived-unknown",
            scope_id=f"snapshot:{verdict.constraint_type}:{variant}:unchecked-derived-unknown",
        ))
    return report.model_copy(update={
        "verdicts": verdicts,
        "admission_projection": report.snapshot_projection,
        "snapshot_projection": None,
    }) if changed else report


def _check_dispatch(model: Model, population: Population) -> CheckReport:
    """Preserve exact-term unavailability instead of consuming an empty relation."""
    report = _partial_constraint_report(
        model, population, check_legacy(model, population)
    )
    if not _model_uses_exact_derivations(model) and not any(
        isinstance(constraint, dict)
        and str(constraint.get("type")) == "guarded"
        and _guarded_term_failure(constraint, population) is not None
        for constraint in model.constraints
    ):
        return report

    calculated = _exact_extension_calculator(model, _base_relations(model, population))
    unavailable = calculated.extensions.unavailable
    effective_view = _constraint_view_dispatch(model, population, calculated.extensions)
    replacements: dict[str, ConstraintVerdict] = {}
    report_verdicts = {verdict.constraint_ref: verdict for verdict in report.verdicts}
    for fact_type in model.fact_types:
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            ref = positional_constraint_ref(str(fact_type.get("id")), index)
            dependency = next(
                (
                    unavailable[subject]
                    for subject in _scope_fact_types(
                        constraint, str(constraint.get("type")), model, fact_type
                    )
                    if subject in unavailable
                ),
                None,
            )
            if dependency is not None:
                replacements[ref] = _term_unavailable_constraint_verdict(
                    constraint, fact_type, ref, dependency
                )
    for index, constraint in enumerate(model.constraints):
        ref = positional_constraint_ref(None, index)
        ordinary_verdict = report_verdicts.get(ref)
        if ordinary_verdict is not None and ordinary_verdict.reason_code == "join-disconnected":
            # The ordinary checker has already refused this antecedent join.
            # Exact-term dependency post-processing must not rejoin it and
            # replace that named refusal with either an exception or a term
            # availability result.
            continue
        dependency_scope = _scope_fact_types(
            constraint, str(constraint.get("type")), model, None
        )
        # Exact-term unavailability is a dependency check, not a change to the
        # antecedent-only subject scope used for guarded vacuity.
        dependency = next(
            (unavailable[subject] for subject in dependency_scope if subject in unavailable),
            None,
        )
        exists_has_no_antecedent_bindings = False
        if str(constraint.get("type")) == "guarded":
            consequent = constraint.get("consequent")
            exists = consequent.get("exists") if isinstance(consequent, dict) else None
            atoms = exists.get("atoms") if isinstance(exists, dict) else None
            if isinstance(atoms, list):
                antecedent = constraint.get("antecedent")
                antecedent_bindings = (
                    _guarded_bindings(antecedent, effective_view)
                    if isinstance(antecedent, list)
                    else []
                )
                exists_has_no_antecedent_bindings = not antecedent_bindings
                exists_sources = [
                    str(atom.get("fact_type"))
                    for atom in atoms
                    if isinstance(atom, dict) and atom.get("fact_type") is not None
                ]
                # The ordinary guarded verdict has already applied vacuity and
                # coverage precedence. Only replace it with source-term
                # unavailability when there are antecedent instances and every
                # existential source is covered.
                if dependency is None and antecedent_bindings and all(
                    subject in population.covers for subject in exists_sources
                ):
                    dependency = next(
                        (unavailable[subject] for subject in exists_sources if subject in unavailable),
                        None,
                    )
        term_dependency = (
            None
            if exists_has_no_antecedent_bindings
            else _guarded_term_failure(constraint, effective_view)
        )
        dependency = dependency or term_dependency
        if dependency is not None:
            replacements[ref] = _term_unavailable_constraint_verdict(
                constraint, None, ref, dependency
            )
    if not replacements:
        _record_aggregate_guarded_outcomes(model, report.verdicts)
        return report
    updated = report.model_copy(
        update={
            "verdicts": [
                replacements.get(verdict.constraint_ref, verdict) for verdict in report.verdicts
            ],
            "admission_projection": report.snapshot_projection or report.admission_projection,
            "snapshot_projection": None,
        }
    )
    _record_aggregate_guarded_outcomes(model, updated.verdicts)
    return updated


def _anchored_verdicts(
    model: Model,
    population: Population,
    anchors: Any,
    document_bytes: bytes | None,
) -> dict[str, ConstraintVerdict]:
    from gnd.extract.anchors import (
        canonical_document_text,
        lexical_ranges,
        recognised_ranges,
        recognition_index,
        recognition_target,
    )
    from gnd.extract.identity import anchor_normalize

    obligations = [
        (fact_type, index, constraint)
        for fact_type in model.fact_types
        for index, constraint in enumerate(fact_type.get("constraints") or [])
        if constraint.get("type") == "anchored"
    ]
    if not obligations:
        return {}
    source = None if document_bytes is None else canonical_document_text(document_bytes)
    records = {}
    if anchors is not None:
        for record in anchors.anchors:
            key = (record["fact_key"]["fact_type"],
                   tuple((name, type(value).__name__, repr(value)) for name, value in sorted(record["fact_key"]["roles"].items())),
                   record["role"])
            records[key] = record
    lexical_wanted: dict[str, set[int]] = {}
    for record in records.values():
        value = record["fact_key"]["roles"][record["role"]]
        if isinstance(value, str):
            lexical_wanted.setdefault(anchor_normalize(value), set()).add(record["occurrence"])
    indexed = (
        lexical_ranges(source, set(lexical_wanted), wanted_occurrences=lexical_wanted)
        if source is not None else {}
    )
    recogniser_kinds = {
        kind for _, _, constraint in obligations for kind in constraint.get("recognise") or []
    }
    recognisers_by_role: dict[tuple[str, str], set[str]] = {}
    for fact_type, _, constraint in obligations:
        if constraint.get("recognise"):
            key = (str(fact_type["id"]), str(constraint["role"]))
            recognisers_by_role.setdefault(key, set()).update(constraint["recognise"])
    recognition_limits: dict[str, dict[Any, int]] = {}
    for record in records.values():
        fact_type = record["fact_key"]["fact_type"]
        role = record["role"]
        value = record["fact_key"]["roles"][role]
        for kind in recognisers_by_role.get((fact_type, role), []):
            target = recognition_target(kind, value)
            cap = recognition_limits.setdefault(kind, {})
            cap[target] = max(cap.get(target, 0), record["occurrence"])
    recognised = (
        recognition_index(source, recogniser_kinds, limits=recognition_limits)
        if source is not None else {}
    )
    recognition_cache: dict[tuple[tuple[str, ...], str, str], list[tuple[int, int]]] = {}
    replacements = {}
    for fact_type, index, constraint in obligations:
        fact_id = str(fact_type["id"])
        reference = positional_constraint_ref(fact_id, index)
        variant = "role" if constraint.get("role") is not None else "all"
        rows = population.facts.get(fact_id, [])
        failed = []
        failed_refs: set[int] = set()
        uncertain = False
        opaque_refs = {
            row_index
            for row_index, row in enumerate(rows)
            for role in fact_type.get("roles") or []
            if constraint.get("role") is None or constraint["role"] == role["role_name"]
            if isinstance(row.get(str(role["role_name"])), dict)
            and set(row[str(role["role_name"])]) == {"$opaque"}
        }
        if opaque_refs:
            verdict, event, reason = "unchecked", "opaque-value", "opaque-value"
            failed_refs.update(opaque_refs)
        elif anchors is None:
            verdict, event, reason = "unchecked", "sidecar-absent", "anchor-sidecar-absent"
        elif not rows:
            verdict, event, reason = "vacuous", "vacuous", None
        else:
            for row_index, row in enumerate(rows):
                for role in fact_type.get("roles") or []:
                    role_name = str(role["role_name"])
                    if constraint.get("role") is not None and constraint["role"] != role_name:
                        continue
                    value = row[role_name]
                    key = (fact_id, tuple((name, type(item).__name__, repr(item)) for name, item in sorted(row.items())), role_name)
                    record = records.get(key)
                    if record is None:
                        failed.append({"fact_type": fact_id, "roles": row})
                        failed_refs.add(row_index)
                        continue
                    span = record["span"]
                    recognisers = constraint.get("recognise") or []
                    if recognisers:
                        cache_key = (tuple(recognisers), type(value).__name__, repr(value))
                        ranges = recognition_cache.get(cache_key)
                        if ranges is None:
                            ranges = sorted({
                                pair for kind in recognisers
                                for pair in recognised_ranges(recognised, kind, value)
                            })
                            recognition_cache[cache_key] = ranges
                    elif isinstance(value, str):
                        ranges = indexed.get(anchor_normalize(value), {})
                    else:
                        uncertain = True
                        continue
                    occurrence = record["occurrence"]
                    selected_range = (
                        ranges.get(occurrence) if isinstance(ranges, dict)
                        else ranges[occurrence] if occurrence < len(ranges) else None
                    )
                    if selected_range is None or not (span["start"] <= selected_range[0] and selected_range[1] <= span["end"]):
                        failed.append({"fact_type": fact_id, "roles": row})
                        failed_refs.add(row_index)
            if failed:
                verdict = "warning" if constraint.get("modality") == "deontic" else "fail"
                event, reason = "violated", None
            elif uncertain:
                verdict, event, reason = "unchecked", "non-lexical", "anchor-non-lexical"
            else:
                verdict, event, reason = "pass", "clean", None
        scope = (
            "applicability:opaque:n-a:opaque-value"
            if event == "opaque-value"
            else f"snapshot:anchored:{variant}:{event}"
        )
        if event == "violated":
            scope += f":{constraint.get('modality', 'alethic')}"
        replacements[reference] = ConstraintVerdict(
            scope_id=scope, constraint_ref=reference, constraint_type="anchored",
            modality=str(constraint.get("modality", "alethic")),
            source=str(constraint["source"]), status=str(constraint["status"]),
            verdict=verdict, reason_code=reason,
            message=f"Source anchor {verdict} for {fact_id}.",
            offending_facts=failed,
            fact_refs=[{"fact_type": fact_id, "index": row_index} for row_index in sorted(failed_refs)],
        )
    return replacements


def check_with_anchors(
    model: Model,
    population: Population,
    *,
    anchors: Any = None,
    document_bytes: bytes | None = None,
) -> CheckReport:
    report = _check_dispatch(model, population)
    replacements = _anchored_verdicts(model, population, anchors, document_bytes)
    if not replacements:
        return report
    return report.model_copy(update={
        "verdicts": [replacements.get(row.constraint_ref, row) for row in report.verdicts],
        "snapshot_projection": None,
        "admission_projection": report.snapshot_projection,
    })


def check(
    model: Model, population: Population, *, references: BoundReferenceContext | None = None
) -> CheckReport:
    if model.reference_populations:
        from gnd.references import bind_population, is_bound_population, resolve_context

        context = resolve_context(model, references)
        if not is_bound_population(model, population, context):
            population = bind_population(model, population, references=context).combined
    return _check_dispatch(model, population)


def check_partial(model: Model, population: Population) -> CheckReport:
    """Evaluate opaque input with the three-valued internal extension view."""
    token = _PARTIAL_OPAQUE.set(True)
    try:
        return check(model, population)
    finally:
        _PARTIAL_OPAQUE.reset(token)


def check_with_anchors_partial(
    model: Model, population: Population, *, anchors: Any = None,
    document_bytes: bytes | None = None,
) -> CheckReport:
    """Use the same opaque semantics when an anchored check is requested."""
    token = _PARTIAL_OPAQUE.set(True)
    try:
        return check_with_anchors(
            model, population, anchors=anchors, document_bytes=document_bytes
        )
    finally:
        _PARTIAL_OPAQUE.reset(token)
