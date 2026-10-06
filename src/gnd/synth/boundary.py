"""The D-06 boundary class: cases derived from the constraint's own parameters.

D-06 is a rule about DRIFT, not about thoroughness. A hand-written boundary set
is wrong the moment the model changes; a set derived from the declared bounds
cannot be. So every case here reads ``range`` / ``bound`` / ``allowed`` /
``variant`` off the constraint and places the population exactly at the bound
(the *inside* case) and exactly one representable step past it (the *outside*
case).

**The uniform phrasing is a lie, and the table says where (RESEARCH §"Boundary
Derivation Table").** ``frequency {min: 1}`` has no reachable case below its
bound: a group of size zero does not occur, and Halpin's occurring-groups
semantics (``constraint-reference.md:360``) make that *satisfied*. A deriver that
emits it anyway manufactures a case labelled violating that the checker correctly
passes — a fabricated false pass in the published report. So an unreachable bound
returns :class:`NotDerivable` with its mechanism named; it is counted under
coverage and never silently dropped.

**ε is the minimal REPRESENTABLE step, never a fixed constant (panel C11).** A
fixed ``1e-9`` rounds back to the original value at large magnitudes and produces
a boundary whose two sides serialize identically — a silent no-op wearing a
boundary label. :func:`boundary_neighbour` uses ``math.nextafter`` for
``Float``/``Number``, ``1`` for ``Integer``, one day for ``Date``, and one
MICROSECOND for ``DateTime`` (stated explicitly: ISO-8601 fractional seconds are
valid, so "one second" mislabels the frontier). Every neighbour is asserted to
differ from its bound AFTER serialization, and the derived neighbour is recorded
in the sidecar's ``epsilon`` field. ``String`` and enum have no ordering: their
frontier is MEMBERSHIP, not a step, and asking for a neighbour raises
:class:`NoOrdering`.

**The prediction is authoritative; the checker observes (C1).** Every case
carries its predicted verdict, derived at the same time as the data by the
INDEPENDENT expected-state engine (:func:`gnd.synth.mutate.expected_state` — the
assembler's constructive witnesses plus a mirror of the normative vacuity rules,
never a call to :func:`gnd.checker.check`). A case whose observed verdict
disagrees with its prediction is QUARANTINED at exit 6 and never relabelled:
the disagreement is a candidate checker defect, and a discarded case is exactly
how such a defect vanishes from its own evaluation corpus.

**Join-scoped boundaries establish a real join first.** For the join-scoped
families a perturbation that empties the join produces a ``vacuous`` verdict
wearing a ``boundary`` label. Those cases return :class:`NotDerivable` (or are
reclassified ``no-subjects`` by :mod:`gnd.synth.frontier`), never a boundary case
carrying a vacuity verdict — the boundary-class analogue of plan 03's positive
non-degeneracy gate.
"""

from __future__ import annotations

import copy
import json
import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta  # noqa: F401 -- historical compatibility binding
from pathlib import Path
from random import Random
from typing import Any

from gnd import input_policy as _rf7_input
from gnd import popvalidate
from gnd.checker import IMPLEMENTED_FAMILIES, CheckReport, check
from gnd.model import Model
from gnd.population import PopulationValidationError, load_population
from gnd.synth.assemble import (
    GeneratorError,
    _constraint_iter_with_ref,
    _direct_subtypes,
    _key,
    _role_object,
    _seq_tuples,
    _universe,
)
from gnd.synth.comparison import _UNTYPEABLE
from gnd.synth.comparison import normalize_operands as _normalize_comparison_operands
from gnd.synth.comparison import role_literal_operands as _role_literal_operands
from gnd.synth.oracle import (
    SKIP as _SKIP,
)
from gnd.synth.oracle import (
    applies_add_missing_subset as _applies_add_missing_subset,
)
from gnd.synth.oracle import (
    applies_add_overlap as _applies_add_overlap,
)
from gnd.synth.oracle import (
    applies_add_past_ceiling as _applies_add_past_ceiling,
)
from gnd.synth.oracle import (
    applies_add_self_loop as _applies_add_self_loop,
)
from gnd.synth.oracle import (
    applies_close_2_cycle as _applies_close_2_cycle,
)
from gnd.synth.oracle import (
    applies_close_3_cycle as _applies_close_3_cycle,
)
from gnd.synth.oracle import (
    applies_drop_covers as _applies_drop_covers,
)
from gnd.synth.oracle import (
    applies_duplicate_covered as _applies_duplicate_covered,
)
from gnd.synth.oracle import (
    applies_duplicate_joined as _applies_duplicate_joined,
)
from gnd.synth.oracle import (
    applies_exact_duplicate as _applies_exact_duplicate,
)
from gnd.synth.oracle import (
    applies_introduce_distinct as _applies_introduce_distinct,
)
from gnd.synth.oracle import (
    applies_new_entity_plays as _applies_new_entity_plays,
)
from gnd.synth.oracle import (
    applies_place_two_subtypes as _applies_place_two_subtypes,
)
from gnd.synth.oracle import (
    applies_play_both as _applies_play_both,
)
from gnd.synth.oracle import (
    applies_play_neither as _applies_play_neither,
)
from gnd.synth.oracle import (
    applies_remove_disjunctive as _applies_remove_disjunctive,
)
from gnd.synth.oracle import (
    applies_roster_add as _applies_roster_add,
)
from gnd.synth.oracle import (
    apply_add_missing_subset as _apply_add_missing_subset,
)
from gnd.synth.oracle import (
    apply_add_overlap as _apply_add_overlap,
)
from gnd.synth.oracle import (
    apply_add_past_ceiling as _apply_add_past_ceiling,
)
from gnd.synth.oracle import (
    apply_add_self_loop as _apply_add_self_loop,
)
from gnd.synth.oracle import (
    apply_close_2_cycle as _apply_close_2_cycle,
)
from gnd.synth.oracle import (
    apply_close_3_cycle as _apply_close_3_cycle,
)
from gnd.synth.oracle import (
    apply_drop_covers as _apply_drop_covers,
)
from gnd.synth.oracle import (
    apply_duplicate_covered as _apply_duplicate_covered,
)
from gnd.synth.oracle import (
    apply_duplicate_joined as _apply_duplicate_joined,
)
from gnd.synth.oracle import (
    apply_exact_duplicate as _apply_exact_duplicate,
)
from gnd.synth.oracle import (
    apply_introduce_distinct as _apply_introduce_distinct,
)
from gnd.synth.oracle import (
    apply_new_entity_plays as _apply_new_entity_plays,
)
from gnd.synth.oracle import (
    apply_place_two_subtypes as _apply_place_two_subtypes,
)
from gnd.synth.oracle import (
    apply_play_both as _apply_play_both,
)
from gnd.synth.oracle import (
    apply_play_neither as _apply_play_neither,
)
from gnd.synth.oracle import (
    apply_remove_disjunctive as _apply_remove_disjunctive,
)
from gnd.synth.oracle import (
    apply_roster_add as _apply_roster_add,
)
from gnd.synth.oracle import (
    complete_row as _complete_row,
)
from gnd.synth.oracle import (
    existing_members as _existing_members,
)
from gnd.synth.oracle import (
    expected_state as expected_state,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle import (
    facts_of as _facts_of,
)
from gnd.synth.oracle import (
    fresh_identifier as _fresh_identifier,
)
from gnd.synth.oracle import (
    ft_by_id as _ft_by_id,
)
from gnd.synth.oracle import (
    internal_frequency_groups as _internal_frequency_groups,
)
from gnd.synth.oracle import (
    resolve as _resolve,
)
from gnd.synth.oracle import (
    ring_components_of as _ring_components_of,
)
from gnd.synth.oracle import (
    ring_edges as _ring_edges,
)
from gnd.synth.oracle import (
    ring_gate as _ring_gate,
)
from gnd.synth.oracle import (
    xor_player_sets as _xor_player_sets,
)
from gnd.synth.oracle import (
    xor_single_role as _xor_single_role,
)
from gnd.synth.provenance import ExpectedState

__all__ = [
    "DATETIME_RESOLUTION",
    "DATE_RESOLUTION",
    "AdmittedBoundaryCase",
    "BoundaryCase",
    "BoundaryPredictionMismatch",
    "NoOrdering",
    "NotDerivable",
    "boundary_neighbour",
    "compare_boundary_observed",
    "derive_boundary_cases",
    "emit_boundary",
    "enumerate_boundary",
    "predict_boundary",
]

#: The minimal representable step for ``Date``. One day: the primitive has no
#: finer resolution in ISO-8601 date form.
DATE_RESOLUTION = timedelta(days=1)

#: The minimal representable step for ``DateTime``, stated EXPLICITLY rather than
#: assumed to be one second (panel C11). ISO-8601 fractional seconds are valid
#: and ``popvalidate._is_datetime`` accepts them, so "one second" would mislabel
#: an inside case as outside. One microsecond is Python's ``datetime``
#: resolution and the finest value that survives ``isoformat()`` round-trip.
DATETIME_RESOLUTION = timedelta(microseconds=1)

#: How many enum members get their own inside case before the rest are folded
#: into one record. The membership frontier is per-member by the D-06 table; the
#: cap keeps a 500-member enum from dominating the corpus.
_ENUM_CASE_CEILING = 4

#: Count-driven derivations are clamped to this many added facts / instances
#: (T-02-22). A declared bound beyond it returns ``NotDerivable`` naming the
#: ceiling rather than attempting the allocation — a ``cardinality {max: 10**9}``
#: must not drive a universe of that size.
_GENERATION_CEILING = 32


class NoOrdering(Exception):
    """The primitive has no ordering, so its frontier is MEMBERSHIP, not a step.

    ``String`` and enum domains reach this: "one below the bound" is undefined
    for them, and a deriver that invented a step would emit a case whose label
    describes something the model never declared.
    """


class NotDerivableError(GeneratorError):
    """Internal control-flow marker used by a deriver to stand a side down."""

    def __init__(self, reason: str) -> None:
        self.reason = reason
        super().__init__(reason)


# --------------------------------------------------------------------------- #
# ε — the minimal representable step (C11)
# --------------------------------------------------------------------------- #


def _serialise(value: Any) -> str:
    """The value exactly as the population file will carry it.

    The inside/outside assertion is made against THIS, not against the in-memory
    object: a boundary whose two sides serialize identically is not a boundary,
    however different the Python values look.
    """
    return json.dumps(value, sort_keys=True, allow_nan=False)


def boundary_neighbour(value: Any, primitive: str | None, direction: int) -> tuple[Any, str]:
    """The value one MINIMAL REPRESENTABLE step from ``value`` (C11).

    ``direction`` is ``+1`` (upward) or ``-1`` (downward). Returns
    ``(neighbour, epsilon_label)`` where ``epsilon_label`` records the actual
    derived step for the sidecar — the plan requires the *derived* neighbour to
    travel with the case, not the name of a constant.

    Raises :class:`NoOrdering` for ``String``/``Boolean`` (membership, not a
    step) and for a float bound with no representable neighbour (``inf``/``nan``).
    Asserts the neighbour differs from the bound AFTER serialization; a step that
    round-trips back to the bound is a silent no-op and is refused loudly.
    """
    if direction not in (1, -1):
        raise ValueError(f"direction must be +1 or -1, got {direction!r}")
    name = str(primitive) if primitive is not None else ""

    if name == "Integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise NoOrdering(
                f"an Integer bound must be an int; {value!r} is {type(value).__name__}"
            )
        neighbour, epsilon = value + direction, "1"
    elif name in ("Float", "Number", "Decimal"):
        try:
            base = float(value)
        except (TypeError, ValueError) as error:
            raise NoOrdering(f"{value!r} is not a finite number bound") from error
        if not math.isfinite(base):
            raise NoOrdering(
                f"{value!r} is not finite; math.nextafter has no representable "
                f"neighbour to step to"
            )
        # nextafter, NOT a fixed 1e-9: a constant delta rounds back to `base` at
        # large magnitudes and yields a boundary case that is a no-op (C11).
        neighbour = math.nextafter(base, math.inf if direction > 0 else -math.inf)
        if not math.isfinite(neighbour):
            raise NoOrdering(
                f"{value!r} has no finite representable neighbour in direction "
                f"{direction:+d}"
            )
        epsilon = repr(abs(neighbour - base))
    elif name == "Date":
        try:
            parsed = date.fromisoformat(str(value))
        except ValueError as error:
            raise NoOrdering(f"{value!r} is not an ISO-8601 date bound") from error
        try:
            neighbour = (parsed + direction * DATE_RESOLUTION).isoformat()
        except OverflowError as error:
            raise NoOrdering(
                f"{value!r} has no representable Date neighbour in direction "
                f"{direction:+d}"
            ) from error
        epsilon = "P1D"
    elif name == "DateTime":
        try:
            parsed = _rf7_input.parse_datetime(value)
        except ValueError as error:
            raise NoOrdering(f"{value!r} is not an ISO-8601 datetime bound") from error
        try:
            neighbour = (parsed + direction * DATETIME_RESOLUTION).isoformat()
        except OverflowError as error:
            raise NoOrdering(
                f"{value!r} has no representable DateTime neighbour in direction "
                f"{direction:+d}"
            ) from error
        epsilon = "PT0.000001S"
    elif name in ("String", "Boolean"):
        raise NoOrdering(
            f"{name} has no ordering, so its boundary is MEMBERSHIP rather than a "
            f"step; derive an in-domain and an out-of-domain value instead"
        )
    else:
        raise NoOrdering(f"no minimal representable step is defined for primitive {name!r}")

    try:
        rendered_neighbour = _serialise(neighbour)
        rendered_value = _serialise(value)
    except (TypeError, ValueError) as error:
        raise NoOrdering(
            f"the derived neighbour of {value!r} cannot be represented as strict JSON"
        ) from error
    if rendered_neighbour == rendered_value:
        raise NoOrdering(
            f"the derived neighbour of {value!r} serializes identically "
            f"({rendered_value}) — a boundary whose two sides are the same "
            f"value is a silent no-op, not a boundary (C11)"
        )
    return neighbour, epsilon


# --------------------------------------------------------------------------- #
# the case records
# --------------------------------------------------------------------------- #


@dataclass(frozen=True)
class NotDerivable:
    """A bound with no reachable case, recorded with the mechanism that makes it
    unreachable.

    It is RETURNED, counted and reported — never a silent skip and never an
    emitted case. The applicability matrix reads these to keep an unmeasurable
    cell out of the coverage denominator instead of scoring it covered.
    """

    constraint_ref: str
    family: str
    side: str
    reason: str
    case_kind: str = "boundary"

    def as_record(self) -> dict[str, Any]:
        """The ``index.json`` shape — same keys the mutation layer emits, so one
        reader serves both classes."""
        return {
            "constraint_ref": self.constraint_ref,
            "family": self.family,
            "operator": f"boundary:{self.side}",
            "case_kind": self.case_kind,
            "side": self.side,
            "mechanism": self.reason,
        }


@dataclass
class BoundaryCase:
    """One derived case: the document, which side of the bound it sits on, and
    the derived ε that separates it from its twin."""

    constraint_ref: str
    family: str
    name: str
    side: str
    doc: dict[str, Any]
    description: str
    epsilon: str | None = None
    #: One of the FIVE measurement case kinds. Most derived cases are
    #: ``boundary``; the three whose frontier is DECIDABILITY rather than a bound
    #: (textual, derivation-only subtype-partition, reference-clock comparison)
    #: are ``unchecked``, and the coverage-omission row is ``no-subjects``.
    #: :data:`gnd.synth.provenance.CASE_KIND_TO_LABEL` maps all five onto D-10's
    #: three frozen population-header labels.
    case_kind: str = "boundary"
    bound_value: Any = None
    placed_value: Any = None


@dataclass
class AdmittedBoundaryCase:
    """A boundary case the real checker agreed with."""

    case: BoundaryCase
    predicted: dict[str, ExpectedState]
    predicted_verdict: str | None
    observed_verdict: str | None
    report: CheckReport


class BoundaryPredictionMismatch(Exception):
    """The checker's observed verdict disagrees with the derived prediction.

    Same discipline as plans 03 and 05: the DERIVATION is authoritative, the
    checker observational. The case is quarantined at exit 6 with a typed
    discrepancy and its sidecar keeps the PREDICTION — relabelling it to match
    the observation is the oracle circularity that lets a present-day checker
    defect vanish from its own evaluation corpus.
    """

    def __init__(
        self,
        case: BoundaryCase,
        predicted: dict[str, ExpectedState],
        discrepancies: list[dict[str, Any]],
    ) -> None:
        self.case = case
        self.doc = case.doc
        self.predicted = predicted
        self.discrepancies = discrepancies
        refs = sorted({d["constraint_ref"] for d in discrepancies})
        super().__init__(
            f"{case.name}: the checker disagreed with the derived prediction on "
            f"{refs} — either the derivation is wrong or the CHECKER is; reproduce "
            f"before adjusting the prediction. The case is quarantined, never "
            f"discarded or relabelled (C1)."
        )


# --------------------------------------------------------------------------- #
# prediction and admission
# --------------------------------------------------------------------------- #


def predict_boundary(model: Model, doc: dict[str, Any]) -> dict[str, ExpectedState]:
    """The FULL typed expectation map over one document (C3).

    A boundary case is not a delta: its whole content is "the population sits at
    the bound", so the prediction is the expected state of EVERY constraint over
    the emitted document — computed by the independent oracle, never by the
    checker. Constraints for which no independent oracle exists are omitted, and
    the engine then makes no claim about them.
    """
    children = _direct_subtypes(model)
    predicted: dict[str, ExpectedState] = {}
    for ref, constraint, ft in _constraint_iter_with_ref(model):
        state = expected_state(constraint, ft, doc, model, children)
        if state is None:
            continue
        predicted[ref] = ExpectedState(
            ground_truth=state.ground_truth,  # type: ignore[arg-type]
            expected_verdict=state.expected_verdict,  # type: ignore[arg-type]
            reason=state.reason,
        )
    return predicted


def compare_boundary_observed(
    predicted: dict[str, ExpectedState], report: CheckReport
) -> list[dict[str, Any]]:
    """Every typed prediction/observation discrepancy (empty == admissible).

    Compared over the FULL map rather than a delta: a boundary case's claim is
    about the whole population's standing at the bound, so a constraint the
    derivation did not target but whose verdict the derivation still predicts is
    part of the claim.
    """
    observed = {v.constraint_ref: v.verdict for v in report.verdicts}
    discrepancies: list[dict[str, Any]] = []
    for ref in sorted(predicted):
        expectation = predicted[ref]
        actual = observed.get(ref)
        if actual == expectation.expected_verdict:
            continue
        discrepancies.append(
            {
                "constraint_ref": ref,
                "predicted": expectation.model_dump(),
                "observed_verdict": actual,
                "kind": "prediction-observation-mismatch",
            }
        )
    return discrepancies


def emit_boundary(
    model: Model, case: BoundaryCase, path: str | Path
) -> AdmittedBoundaryCase:
    """Write one boundary case and admit it ONLY after the checker confirms it.

    Mirrors :func:`gnd.synth.mutate.emit_violating` step for step: write, re-load
    through ``load_population`` (a rejection here is a GENERATOR bug at exit 5 —
    a structurally invalid population contributes zero verdicts and therefore
    zero errors), check with the real checker, compare against the derived
    prediction, and raise :class:`BoundaryPredictionMismatch` for the caller to
    quarantine at exit 6.
    """
    doc = case.doc
    doc.setdefault("population", {})["label"] = "boundary"

    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    try:
        population = load_population(str(path), model=model)
    except PopulationValidationError as error:
        raise GeneratorError(
            f"{case.name}: the derived boundary population failed re-admission (a "
            f"GENERATOR bug, exit 5 — it would contribute no verdicts and therefore "
            f"no errors): {error}"
        ) from error

    report = check(model, population)
    predicted = predict_boundary(model, doc)
    discrepancies = compare_boundary_observed(predicted, report)
    if discrepancies:
        raise BoundaryPredictionMismatch(case, predicted, discrepancies)

    target = predicted.get(case.constraint_ref)
    observed = next(
        (v.verdict for v in report.verdicts if v.constraint_ref == case.constraint_ref), None
    )
    return AdmittedBoundaryCase(
        case=case,
        predicted=predicted,
        predicted_verdict=target.expected_verdict if target else None,
        observed_verdict=observed,
        report=report,
    )


# --------------------------------------------------------------------------- #
# shared derivation helpers
# --------------------------------------------------------------------------- #


def _clone(doc: dict[str, Any]) -> dict[str, Any]:
    return copy.deepcopy(doc)


def _value_target(constraint: dict[str, Any], model: Model) -> tuple[str, str] | None:
    """The ``(fact_type, role)`` a ``value`` constraint governs, from the MODEL
    (so a bound value can be placed even when the baseline carries no occurrence
    of that role yet)."""
    role_ref = constraint.get("role_ref")
    if isinstance(role_ref, dict):
        return str(role_ref.get("fact_type")), str(role_ref.get("role"))
    target = str(constraint.get("object_type"))
    for ft in model.fact_types or []:
        for role in ft.get("roles") or []:
            if str(role.get("object_type")) == target:
                return str(ft.get("id")), str(role.get("role_name"))
    return None


def _reference_targets(constraint: dict[str, Any], model: Model) -> list[tuple[str, str]]:
    """``(fact_type, role)`` pairs whose ENTITY role is identified by the value
    type this constraint governs (F-01).

    ``population-format.md``: an entity value in a fact IS its reference-scheme
    value, so a ``value`` constraint on a reference value type ranges over those
    occurrences too. A boundary set that only populated roles typed to the value
    type would miss exactly the path F-01 closed.
    """
    if constraint.get("role_ref") is not None:
        return []
    target = str(constraint.get("object_type"))
    children = _direct_subtypes(model)
    covered = {target} | _descendant_ids(model, target, children)
    identified = _governed_object_types(model, target, children) - covered
    if not identified:
        return []
    out: list[tuple[str, str]] = []
    for ft in model.fact_types or []:
        for role in ft.get("roles") or []:
            if str(role.get("object_type")) in identified:
                out.append((str(ft.get("id")), str(role.get("role_name"))))
    return out


def _place_value(
    doc: dict[str, Any],
    model: Model,
    ftid: str,
    role: str,
    value: Any,
    rng: Random,
) -> None:
    """Put ``value`` in the first fact carrying ``role``, or mint a row for it."""
    for fact in _facts_of(doc, ftid):
        if role in fact:
            fact[role] = value
            return
    ft = _ft_by_id(model, ftid)
    if ft is None:
        raise NotDerivableError(f"fact type {ftid!r} does not exist in the model")
    row = _complete_row(doc, model, ft, {role: value}, rng)
    _facts_of(doc, ftid).append(row)


def _non_member(allowed: list[Any]) -> Any | None:
    """A value outside an ``allowed`` enum — the membership frontier's far side."""
    if all(isinstance(a, str) for a in allowed):
        candidate = "znot-allowed"
        while candidate in allowed:
            candidate += "-x"
        return candidate
    numbers = [a for a in allowed if isinstance(a, (int, float)) and not isinstance(a, bool)]
    if numbers and len(numbers) == len(allowed):
        return max(numbers) + 1
    return None


def _via_operator(
    model: Model,
    ref: str,
    constraint: dict[str, Any],
    ft: dict[str, Any] | None,
    doc: dict[str, Any],
    rng: Random,
    applies: Any,
    apply: Any,
    *,
    side: str,
    name: str,
    description: str,
    case_kind: str = "boundary",
) -> tuple[BoundaryCase | None, NotDerivable | None]:
    """Build one case through a mutation template, converting its gate into a
    :class:`NotDerivable` record so the shape/semantic distinction survives."""
    family = str(constraint.get("type"))
    outcome = applies(model, constraint, ft, doc)
    if outcome is _SKIP:
        return None, NotDerivable(
            ref, family, side, f"{name}: the template's shape does not match this constraint"
        )
    if outcome is not None:
        return None, NotDerivable(ref, family, side, f"{name}: {outcome}")
    new_doc = apply(_clone(doc), model, ref, rng)
    return (
        BoundaryCase(ref, family, name, side, new_doc, description, case_kind=case_kind),
        None,
    )


def _baseline_case(
    ref: str,
    family: str,
    name: str,
    side: str,
    doc: dict[str, Any],
    description: str,
    *,
    case_kind: str = "boundary",
) -> BoundaryCase:
    """An inside case that IS the baseline: the population already sits exactly
    at the bound, and the case pins that the checker accepts it there."""
    return BoundaryCase(ref, family, name, side, _clone(doc), description, case_kind=case_kind)


# --------------------------------------------------------------------------- #
# family derivers
# --------------------------------------------------------------------------- #


def _derive_value(model, ref, constraint, ft, doc, rng):
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = "value"
    oid = str(constraint.get("object_type") or "")
    primitive = popvalidate.resolve_primitive(oid, model) if oid else None
    target = _value_target(constraint, model)

    if constraint.get("ranges") is not None:
        downs.append(
            NotDerivable(
                ref, family, "both",
                "multi-range (`ranges`) boundary derivation is not implemented; the "
                "frontier is a union of intervals, and a single min/max pair cannot "
                "name it",
            )
        )
        return cases, downs
    # F-01: the universe of a reference value type INCLUDES the entity values
    # that denote instances of the types it identifies. A boundary set that only
    # populated roles typed to the value type would miss exactly the path F-01
    # closed — and on a model like `reference_value_type.orm.yaml` there is no
    # such role at all, so this list is the ONLY way to place the bound.
    reference_targets = _reference_targets(constraint, model)
    if target is None:
        if not reference_targets:
            downs.append(
                NotDerivable(
                    ref, family, "both",
                    "no fact type in the model carries a role typed to this value type "
                    "or to an entity it identifies, so no occurrence can be placed at "
                    "the bound",
                )
            )
            return cases, downs
        target = reference_targets[0]

    ftid, role = target
    allowed = constraint.get("allowed")
    bounds = constraint.get("range")

    if allowed is not None:
        for member in list(allowed)[:_ENUM_CASE_CEILING]:
            work = _clone(doc)
            _place_value(work, model, ftid, role, member, rng)
            cases.append(
                BoundaryCase(
                    ref, family, f"enum-member-{_slugish(member)}", "inside", work,
                    f"membership frontier: {member!r} is an allowed member",
                    epsilon=None, bound_value=member, placed_value=member,
                )
            )
        if len(allowed) > _ENUM_CASE_CEILING:
            downs.append(
                NotDerivable(
                    ref, family, "inside-tail",
                    f"{len(allowed) - _ENUM_CASE_CEILING} further enum members beyond the "
                    f"{_ENUM_CASE_CEILING}-case ceiling carry the same membership frontier; "
                    f"emitting one case each would grow the corpus without adding a distinct "
                    f"frontier",
                )
            )
        outside = _non_member(list(allowed))
        if outside is None:
            downs.append(
                NotDerivable(
                    ref, family, "outside",
                    "the enum mixes value shapes, so no non-member of the same shape is "
                    "derivable without inventing a type the model never declared",
                )
            )
        else:
            work = _clone(doc)
            _place_value(work, model, ftid, role, outside, rng)
            cases.append(
                BoundaryCase(
                    ref, family, "enum-non-member", "outside", work,
                    f"membership frontier: {outside!r} is outside `allowed`",
                    epsilon="membership", bound_value=list(allowed), placed_value=outside,
                )
            )
        return cases, downs

    if bounds is None:
        downs.append(
            NotDerivable(
                ref, family, "both",
                "the constraint declares neither `allowed` nor `range`; there is no "
                "bound to sit at",
            )
        )
        return cases, downs

    # A reference target already serving as the primary target is not a second,
    # distinct path — do not emit the same population twice.
    reference_targets = [t for t in reference_targets if t != target]

    for edge, outward in (("min", -1), ("max", +1)):
        bound = bounds.get(edge)
        if bound is None:
            downs.append(
                NotDerivable(
                    ref, family, edge,
                    f"no {edge} bound declared; there is no {edge} frontier to sit at",
                )
            )
            continue
        # Read the INCLUSIVITY FLAGS; do not assume. An exclusive minimum makes
        # the bound itself the OUTSIDE case and `a + ε` the inside one.
        inclusive = bounds.get(f"{edge}_inclusive", True)
        try:
            outward_neighbour, outward_eps = boundary_neighbour(bound, primitive, outward)
            inward_neighbour, inward_eps = boundary_neighbour(bound, primitive, -outward)
        except NoOrdering as error:
            downs.append(NotDerivable(ref, family, edge, str(error)))
            continue

        if inclusive:
            inside_value, inside_eps = bound, None
            outside_value, outside_eps = outward_neighbour, outward_eps
        else:
            inside_value, inside_eps = inward_neighbour, inward_eps
            outside_value, outside_eps = bound, None

        for side, value, eps in (
            ("inside", inside_value, inside_eps),
            ("outside", outside_value, outside_eps),
        ):
            work = _clone(doc)
            _place_value(work, model, ftid, role, value, rng)
            cases.append(
                BoundaryCase(
                    ref, family, f"range-{edge}-{side}", side, work,
                    f"{edge} bound {bound!r} ({'inclusive' if inclusive else 'exclusive'}); "
                    f"placed {value!r} at {ftid}.{role}",
                    epsilon=eps, bound_value=bound, placed_value=value,
                )
            )
            # F-01: the same bound also governs entity reference values.
            for entity_ftid, entity_role in reference_targets[:1]:
                ref_work = _clone(doc)
                _place_value(ref_work, model, entity_ftid, entity_role, value, rng)
                cases.append(
                    BoundaryCase(
                        ref, family, f"reference-value-{edge}-{side}", side, ref_work,
                        f"{edge} bound {bound!r} placed as the IDENTIFYING value of an "
                        f"entity at {entity_ftid}.{entity_role} — the F-01 path a "
                        f"value-type-only boundary set misses",
                        epsilon=eps, bound_value=bound, placed_value=value,
                    )
                )
    return cases, downs


def _slugish(value: Any) -> str:
    text = str(value).lower()
    return "".join(ch if ch.isalnum() else "-" for ch in text)[:24] or "empty"


def _derive_uniqueness(model, ref, constraint, ft, doc, rng):
    """The bound is 1 occurrence per covered tuple — not ``n−1``/``n``."""
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = "uniqueness"
    external = ft is None or constraint.get("scope") == "external"

    if not external:
        _covered, groups = _internal_frequency_groups(constraint, ft, doc)
        if not groups:
            downs.append(
                NotDerivable(
                    ref, family, "inside",
                    "the governed fact type carries no covered tuple in the baseline; "
                    "there is no occurrence sitting at the bound of 1",
                )
            )
        else:
            largest = max(count for _v, count in groups.values())
            if largest != 1:
                downs.append(
                    NotDerivable(
                        ref, family, "inside",
                        f"the baseline's largest covered group already holds {largest} "
                        f"occurrences, so it does not sit at the bound of 1",
                    )
                )
            else:
                cases.append(
                    _baseline_case(
                        ref, family, "occurs-exactly-once", "inside", doc,
                        f"every one of the {len(groups)} covered tuples occurs exactly "
                        f"once — the population sits exactly at the bound of 1",
                    )
                )
        # Two SHAPES of "occurs twice": a proper subset of the roles is covered
        # (duplicate the covered values, vary the rest) or the covered set spans
        # the fact type (duplicate the whole row). Shape dispatch, not a
        # stand-down — trying only one would record a spanning uniqueness as
        # unreachable when it is merely a different shape.
        case = down = None
        for applies, apply in (
            (_applies_duplicate_covered, _apply_duplicate_covered),
            (_applies_exact_duplicate, _apply_exact_duplicate),
        ):
            case, down = _via_operator(
                model, ref, constraint, ft, doc, rng, applies, apply,
                side="outside", name="occurs-twice",
                description="one covered tuple occurs twice — one step past the bound of 1",
            )
            if case is not None:
                down = None
                break
    else:
        seq = [r for r in constraint.get("role_refs") or [] if isinstance(r, dict)]
        rows = _seq_tuples(doc, model, seq) if seq else []
        if not rows:
            downs.append(
                NotDerivable(
                    ref, family, "inside",
                    "the external join yields ZERO rows in the baseline, so a case here "
                    "would be a vacuity case wearing a boundary label (F-05) — the "
                    "boundary-class analogue of the positive non-degeneracy gate",
                )
            )
        else:
            counts: dict[tuple, int] = {}
            for values in rows:
                key = tuple(_key(v) for v in values)
                counts[key] = counts.get(key, 0) + 1
            largest = max(counts.values())
            if largest != 1:
                downs.append(
                    NotDerivable(
                        ref, family, "inside",
                        f"the largest joined tuple already occurs {largest} times; the "
                        f"baseline does not sit at the bound of 1",
                    )
                )
            else:
                cases.append(
                    _baseline_case(
                        ref, family, "joined-tuple-occurs-once", "inside", doc,
                        f"the join yields {len(rows)} row(s) — asserted non-degenerate — "
                        f"and each joined tuple occurs exactly once, the bound",
                    )
                )
        case, down = _via_operator(
            model, ref, constraint, ft, doc, rng,
            _applies_duplicate_joined, _apply_duplicate_joined,
            side="outside", name="joined-tuple-occurs-twice",
            description="one joined tuple occurs twice — one step past the bound of 1",
        )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _grow_internal_group(doc, model, ref, constraint, ft, target: int, rng) -> None:
    """Append facts until the largest covered group holds exactly ``target``."""
    ftid = str(ft.get("id"))
    covered, groups = _internal_frequency_groups(constraint, ft, doc)
    if not groups:
        raise NotDerivableError(
            "the governed fact type is empty in the baseline; there is no group to grow"
        )
    ordered = sorted(groups.items(), key=lambda item: (-item[1][1], repr(item[0])))
    values, count = ordered[0][1]
    needed = target - count
    if needed < 0:
        raise NotDerivableError(
            f"the largest group already holds {count}, past the target of {target}; "
            f"shrinking a group is not a growth derivation"
        )
    if needed > _GENERATION_CEILING:
        raise NotDerivableError(
            f"bound-beyond-generation-ceiling: reaching {target} needs {needed} added "
            f"facts, past the {_GENERATION_CEILING}-fact ceiling (T-02-22)"
        )
    for _ in range(needed):
        fixed = dict(zip(covered, values, strict=True))
        _facts_of(doc, ftid).append(_complete_row(doc, model, ft, fixed, rng, fresh_entities=True))


def _derive_frequency(model, ref, constraint, ft, doc, rng):
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = "frequency"
    bound = constraint.get("bound") or {}
    minimum, maximum = bound.get("min"), bound.get("max")
    internal = ft is not None and bool(constraint.get("roles"))

    if not internal:
        # External frequency: reaching or crossing a joined-group bound requires
        # join-row growth that cascades through the anchor fact types' own
        # constraints, so no mechanical derivation exists here.
        for side, edge in (("inside", "max"), ("outside", "max"), ("inside", "min"), ("outside", "min")):
            declared = bound.get(edge)
            reason = (
                f"no {edge} bound declared; there is no {edge} frontier"
                if declared is None
                else (
                    "external frequency: reaching a joined-group bound requires join-row "
                    "growth that cascades through the anchor fact types' own constraints, "
                    "so no single-fact derivation places the population at the bound"
                )
            )
            downs.append(NotDerivable(ref, family, f"{edge}-{side}", reason))
        return cases, downs

    # ---- min side -------------------------------------------------------- #
    if minimum is None:
        downs.append(
            NotDerivable(ref, family, "min", "no min bound declared; there is no lower frontier")
        )
    else:
        _covered, groups = _internal_frequency_groups(constraint, ft, doc)
        if any(count == minimum for _v, count in groups.values()):
            cases.append(
                _baseline_case(
                    ref, family, "group-at-min", "inside", doc,
                    f"a covered group holds exactly min={minimum} facts — the population "
                    f"sits exactly at the lower bound",
                )
            )
        else:
            downs.append(
                NotDerivable(
                    ref, family, "min-inside",
                    f"no covered group sits at min={minimum} in the baseline, and growing "
                    f"one to the bound would cross the max bound of the same constraint",
                )
            )
        if minimum <= 1:
            # THE trap. At m = 1 the below-bound group simply does not occur, and
            # Halpin's occurring-groups semantics make that satisfied.
            downs.append(
                NotDerivable(
                    ref, family, "min-outside",
                    f"occurring-groups semantics (constraint-reference.md:360): at "
                    f"min={minimum} the below-bound group has size 0, which means the "
                    f"group does not OCCUR, and a non-occurring group is satisfied — "
                    f"emitting the case would manufacture a violating label the checker "
                    f"correctly passes (a fabricated false pass)",
                )
            )
        else:
            work = _clone(doc)
            covered, groups = _internal_frequency_groups(constraint, ft, doc)
            at_min = sorted(
                (key for key, (_v, count) in groups.items() if count == minimum), key=repr
            )
            if not at_min:
                downs.append(
                    NotDerivable(
                        ref, family, "min-outside",
                        f"no group sits at min={minimum}; dropping one fact cannot cross it",
                    )
                )
            else:
                rows = _facts_of(work, str(ft.get("id")))
                for index, fact in enumerate(rows):
                    if all(rn in fact for rn in covered) and (
                        tuple(_key(fact[rn]) for rn in covered) == at_min[0]
                    ):
                        del rows[index]
                        break
                cases.append(
                    BoundaryCase(
                        ref, family, "group-below-min", "outside", work,
                        f"a covered group holds min-1={minimum - 1} facts — one step below "
                        f"the bound, reachable only because min >= 2",
                        epsilon="1 fact", bound_value=minimum, placed_value=minimum - 1,
                    )
                )

    # ---- max side -------------------------------------------------------- #
    if maximum is None:
        downs.append(
            NotDerivable(ref, family, "max", "no max bound declared; there is no ceiling")
        )
        return cases, downs

    work = _clone(doc)
    try:
        _grow_internal_group(work, model, ref, constraint, ft, maximum, rng)
    except NotDerivableError as error:
        downs.append(NotDerivable(ref, family, "max-inside", error.reason))
    else:
        cases.append(
            BoundaryCase(
                ref, family, "group-at-max", "inside", work,
                f"a covered group holds exactly max={maximum} facts — the population sits "
                f"exactly at the ceiling",
                epsilon="1 fact", bound_value=maximum, placed_value=maximum,
            )
        )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_add_past_ceiling, _apply_add_past_ceiling,
        side="outside", name="group-past-max",
        description=f"a covered group holds max+1={maximum + 1} facts — one step past the ceiling",
    )
    if case is not None:
        case.bound_value, case.placed_value, case.epsilon = maximum, maximum + 1, "1 fact"
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _object_scope_members(doc, model, oid) -> list[Any]:
    return _existing_members(doc, model, str(oid))


def _shrink_object_universe(doc, model, oid: str, target: int, children) -> None:
    """Keep exactly ``target`` members of ``oid``, deleting the rosters and facts
    that make the rest observable."""
    if target < 0:
        raise NotDerivableError(
            f"cardinality counts cannot be negative; target {target} for {oid!r} "
            f"has no population representation"
        )
    members = _existing_members(doc, model, oid)
    if len(members) < target:
        raise NotDerivableError(
            f"the baseline holds {len(members)} member(s) of {oid!r}, fewer than the "
            f"target of {target}; shrinking cannot reach the bound"
        )
    keep = {_key(m) for m in members[:target]}
    governed_types = _governed_object_types(model, oid, children)
    role_obj = _role_object(model)
    for ftid, rows in list((doc.get("facts") or {}).items()):
        roles = role_obj.get(ftid, {})
        governed = [rn for rn, rid in roles.items() if str(rid) in governed_types]
        if not governed:
            continue
        doc["facts"][ftid] = [
            fact
            for fact in rows
            if all(rn not in fact or _key(fact[rn]) in keep for rn in governed)
        ]
    for roster_id, values in list((doc.get("instances") or {}).items()):
        if str(roster_id) in governed_types:
            doc["instances"][roster_id] = [v for v in values if _key(v) in keep]


def _descendant_ids(model: Model, oid: str, children: dict[str, set[str]]) -> set[str]:
    out: set[str] = set()
    stack = [oid]
    while stack:
        current = stack.pop()
        for child in children.get(current, set()):
            if child not in out:
                out.add(child)
                stack.append(child)
    return out


def _governed_object_types(
    model: Model, oid: str, children: dict[str, set[str]] | None = None
) -> set[str]:
    """Subtype closure plus entities denoted by any covered reference type."""
    children = children if children is not None else _direct_subtypes(model)
    covered = {str(oid)} | _descendant_ids(model, str(oid), children)
    covered |= {
        str(object_type.get("id"))
        for object_type in model.object_types or []
        if object_type.get("id") is not None
        and popvalidate.resolve_reference_value_type(
            str(object_type.get("id")), model
        )
        in covered
    }
    return covered


def _derive_cardinality(model, ref, constraint, ft, doc, rng):
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = "cardinality"
    bound = constraint.get("bound") or {}
    minimum, maximum = bound.get("min"), bound.get("max")
    scope = str(constraint.get("scope") or "")
    children = _direct_subtypes(model)

    if scope == "object":
        oid = str(constraint.get("object_type"))
        current = len(_object_scope_members(doc, model, oid))
    elif scope == "role":
        role_ref = constraint.get("role_ref") or {}
        ftid, role = str(role_ref.get("fact_type")), str(role_ref.get("role"))
        current = len(
            {
                _key(fact[role])
                for fact in (doc.get("facts") or {}).get(ftid, [])
                if role in fact
            }
        )
    else:
        downs.append(
            NotDerivable(ref, family, "both", f"unsupported cardinality scope {scope!r}")
        )
        return cases, downs

    # ---- min side -------------------------------------------------------- #
    if minimum is None:
        downs.append(
            NotDerivable(ref, family, "min", "no min bound declared; there is no floor")
        )
    elif scope != "object":
        downs.append(
            NotDerivable(
                ref, family, "min",
                "role-scoped cardinality: shrinking the set of distinct role players to a "
                "declared floor requires deleting facts whose removal cascades through "
                "the host fact type's own constraints",
            )
        )
    else:
        oid = str(constraint.get("object_type"))
        targets = [("inside", minimum)]
        if minimum == 0:
            downs.append(
                NotDerivable(
                    ref,
                    family,
                    "min-outside",
                    "the declared minimum is zero, and a cardinality count cannot be "
                    "negative; there is no representable lower-outside population",
                )
            )
        else:
            targets.append(("outside", minimum - 1))
        for side, target in targets:
            work = _clone(doc)
            try:
                _shrink_object_universe(work, model, oid, target, children)
            except NotDerivableError as error:
                downs.append(NotDerivable(ref, family, f"min-{side}", error.reason))
                continue
            note = (
                f"the {oid!r} universe holds exactly min={minimum} — the population sits "
                f"exactly at the floor"
                if side == "inside"
                else (
                    f"the {oid!r} universe holds min-1={minimum - 1}. With min>=1 this is a "
                    f"DECIDED FAILURE, not vacuity — corpus case "
                    f"`an-unmet-lower-bound-over-nothing-is-still-a-failure` pins it"
                )
            )
            cases.append(
                BoundaryCase(
                    ref, family, f"universe-{'at' if side == 'inside' else 'below'}-min",
                    side, work, note,
                    epsilon="1 instance", bound_value=minimum, placed_value=target,
                )
            )

    # ---- max side -------------------------------------------------------- #
    if maximum is None:
        downs.append(
            NotDerivable(ref, family, "max", "no max bound declared; there is no ceiling")
        )
        return cases, downs

    needed = maximum - current
    if needed < 0:
        downs.append(
            NotDerivable(
                ref, family, "max-inside",
                f"the baseline already holds {current}, past the ceiling of {maximum}",
            )
        )
    elif needed > _GENERATION_CEILING:
        downs.append(
            NotDerivable(
                ref, family, "max-inside",
                f"bound-beyond-generation-ceiling: reaching max={maximum} needs {needed} "
                f"new instances, past the {_GENERATION_CEILING}-instance ceiling (T-02-22)",
            )
        )
    else:
        work = _clone(doc)
        try:
            _grow_to(work, model, constraint, scope, maximum, rng)
        except NotDerivableError as error:
            downs.append(NotDerivable(ref, family, "max-inside", error.reason))
        else:
            cases.append(
                BoundaryCase(
                    ref, family, "universe-at-max", "inside", work,
                    f"the constrained set holds exactly max={maximum} — the population sits "
                    f"exactly at the ceiling",
                    epsilon="1 instance", bound_value=maximum, placed_value=maximum,
                )
            )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_introduce_distinct, _apply_introduce_distinct,
        side="outside", name="universe-past-max",
        description=f"the constrained set holds max+1={maximum + 1} — one step past the ceiling",
    )
    if case is not None:
        case.bound_value, case.placed_value, case.epsilon = maximum, maximum + 1, "1 instance"
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _grow_to(doc, model, constraint, scope: str, target: int, rng) -> None:
    """Grow the cardinality-constrained set to exactly ``target`` members."""
    if scope == "object":
        oid = str(constraint.get("object_type"))
        needed = target - len(_existing_members(doc, model, oid))
        roster = doc.setdefault("instances", {}).setdefault(oid, [])
        for _ in range(needed):
            roster.append(_fresh_identifier(doc, model, oid, rng))
        return
    role_ref = constraint.get("role_ref") or {}
    ftid, role = str(role_ref.get("fact_type")), str(role_ref.get("role"))
    ft = _ft_by_id(model, ftid)
    if ft is None:
        raise NotDerivableError(f"fact type {ftid!r} does not exist in the model")
    oid = str(_role_object(model).get(ftid, {}).get(role))
    players = {
        _key(fact[role]) for fact in (doc.get("facts") or {}).get(ftid, []) if role in fact
    }
    needed = target - len(players)
    pool = [m for m in _existing_members(doc, model, oid) if _key(m) not in players]
    for index in range(needed):
        player = pool[index] if index < len(pool) else _fresh_identifier(doc, model, oid, rng)
        _facts_of(doc, ftid).append(
            _complete_row(doc, model, ft, {role: player}, rng, fresh_entities=True)
        )


def _derive_mandatory(model, ref, constraint, ft, doc, rng):
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = str(constraint.get("type"))
    cases.append(
        _baseline_case(
            ref, family, "every-observable-instance-plays", "inside", doc,
            "every observable instance of the constrained type plays the mandatory "
            "role — the population sits exactly at the containment edge",
        )
    )
    made = False
    for applies, apply, name in (
        (_applies_roster_add, _apply_roster_add, "one-rostered-instance-does-not-play"),
        (_applies_new_entity_plays, _apply_new_entity_plays, "one-new-player-does-not-play"),
    ):
        case, down = _via_operator(
            model, ref, constraint, ft, doc, rng, applies, apply,
            side="outside", name=name,
            description="exactly one observable instance does not play the mandatory role "
                        "— one step past the edge; the instance stays observable, so the "
                        "closed world cannot self-cancel the case",
        )
        if case is not None and not made:
            cases.append(case)
            made = True
        elif down is not None:
            downs.append(down)
    return cases, downs


def _derive_mandatory_disjunctive(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "mandatory-disjunctive"
    cases.append(
        _baseline_case(
            ref, family, "every-instance-plays-one-listed-role", "inside", doc,
            "every observable instance plays at least one listed role — the containment edge",
        )
    )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_remove_disjunctive, _apply_remove_disjunctive,
        side="outside", name="one-instance-plays-none",
        description="exactly one observable instance plays none of the listed roles",
    )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    # The coverage-omission boundary the D-06 table names beside the disjunctive
    # one: the same population with the host fact type dropped from `covers`,
    # whose predicted verdict is `vacuous` rather than a violation.
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_drop_covers, _apply_drop_covers,
        side="frontier", name="coverage-omission-boundary",
        description="the same population with the subject fact type dropped from `covers` "
                    "— the frontier of EVALUABILITY: predicted `vacuous`, not a violation",
        case_kind="no-subjects",
    )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


# ---- ring ----------------------------------------------------------------- #


def _applies_close_transitive_triple(model, constraint, ft, doc):
    if ft is None or "intransitive" not in _ring_components_of(constraint):
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        for b2, c in edges:
            if _key(b2) == _key(b) and len({_key(a), _key(b), _key(c)}) == 3 and (
                _key(a), _key(c)
            ) not in keys:
                return None
    return "no open 2-edge path exists to close transitively"


def _apply_close_transitive_triple(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        for b2, c in edges:
            if _key(b2) == _key(b) and len({_key(a), _key(b), _key(c)}) == 3 and (
                _key(a), _key(c)
            ) not in keys:
                _facts_of(doc, str(ft.get("id"))).append({from_role: a, to_role: c})
                return doc
    raise GeneratorError("close-transitive-triple: no open path (applies() should have gated)")


def _applies_break_symmetry(model, constraint, ft, doc):
    if ft is None or "symmetric" not in _ring_components_of(constraint):
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        if _key(a) != _key(b) and (_key(b), _key(a)) in keys:
            return None
    return "no mirrored edge pair exists whose reverse could be removed"


def _apply_break_symmetry(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    target = next(
        (a, b) for a, b in edges if _key(a) != _key(b) and (_key(b), _key(a)) in keys
    )
    rows = _facts_of(doc, str(ft.get("id")))
    for index, fact in enumerate(rows):
        if (
            from_role in fact
            and to_role in fact
            and _key(fact[from_role]) == _key(target[1])
            and _key(fact[to_role]) == _key(target[0])
        ):
            del rows[index]
            break
    return doc


def _applies_break_transitivity(model, constraint, ft, doc):
    if ft is None or "transitive" not in _ring_components_of(constraint):
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    for a, b in edges:
        for b2, c in edges:
            if _key(b2) == _key(b) and (_key(a), _key(c)) in keys and len(
                {_key(a), _key(b), _key(c)}
            ) == 3:
                return None
    return "no closed transitive triple exists whose closing edge could be removed"


def _apply_break_transitivity(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    keys = {(_key(a), _key(b)) for a, b in edges}
    target = None
    for a, b in edges:
        for b2, c in edges:
            if _key(b2) == _key(b) and (_key(a), _key(c)) in keys and len(
                {_key(a), _key(b), _key(c)}
            ) == 3:
                target = (a, c)
                break
        if target:
            break
    rows = _facts_of(doc, str(ft.get("id")))
    for index, fact in enumerate(rows):
        if (
            from_role in fact
            and to_role in fact
            and _key(fact[from_role]) == _key(target[0])
            and _key(fact[to_role]) == _key(target[1])
        ):
            del rows[index]
            break
    return doc


def _applies_drop_participant_self_edge(model, constraint, ft, doc):
    """LOCAL reflexivity (Halpin, constraint-reference.md:404-426).

    Only PARTICIPANTS — nodes already playing a role in the ring fact type — are
    constrained. A boundary case built over the whole roster manufactures a false
    failure, so this gate looks only at participants, and the apply removes one
    participant's self-edge while leaving that participant observable.
    """
    components = set(_ring_components_of(constraint))
    if ft is None or not components & {"reflexive", "purely-reflexive"}:
        return _SKIP
    gate = _ring_gate(ft)
    if gate is not None:
        return gate
    _f, _t, edges = _ring_edges(doc, model, ft)
    participants = {_key(a) for a, _b in edges} | {_key(b) for _a, b in edges}
    loops = {_key(a) for a, b in edges if _key(a) == _key(b)}
    # A participant whose self-edge can go while it still participates elsewhere.
    for node in sorted(loops, key=repr):
        others = [
            (a, b) for a, b in edges if _key(a) != _key(b) and node in (_key(a), _key(b))
        ]
        if others:
            return None
    if not participants:
        return "the ring fact type is empty; there are no participants to constrain"
    return (
        "every self-edge belongs to a node that participates ONLY through that "
        "self-edge; removing it would remove the participant too, and a "
        "non-participant is not constrained by LOCAL reflexivity "
        "(constraint-reference.md:404-426) — the case would self-cancel"
    )


def _apply_drop_participant_self_edge(doc, model, ref, rng):
    _constraint, ft = _resolve(model, ref)
    from_role, to_role, edges = _ring_edges(doc, model, ft)
    loops = {_key(a) for a, b in edges if _key(a) == _key(b)}
    target = None
    for node in sorted(loops, key=repr):
        if any(_key(a) != _key(b) and node in (_key(a), _key(b)) for a, b in edges):
            target = node
            break
    rows = _facts_of(doc, str(ft.get("id")))
    for index, fact in enumerate(rows):
        if (
            from_role in fact
            and to_role in fact
            and _key(fact[from_role]) == target
            and _key(fact[to_role]) == target
        ):
            del rows[index]
            break
    return doc


def _derive_ring(model, ref, constraint, ft, doc, rng):
    #: variant component -> the OUTSIDE template that crosses exactly that
    #: frontier. `acyclic` closes a cycle of length >= 3 DELIBERATELY: a 2-cycle
    #: or a self-loop would also cross `asymmetric`/`irreflexive` and lose the
    #: isolation the D-06 table asks for.
    templates: dict[str, tuple[Any, Any, str, str]] = {
        "irreflexive": (
            _applies_add_self_loop, _apply_add_self_loop, "self-loop",
            "one edge (a,a) — the single step past the irreflexive frontier",
        ),
        "asymmetric": (
            _applies_close_2_cycle, _apply_close_2_cycle, "reverse-edge",
            "the reverse of an existing edge — one step past the asymmetric frontier",
        ),
        "antisymmetric": (
            _applies_close_2_cycle, _apply_close_2_cycle, "reverse-edge",
            "the reverse of an existing edge between distinct nodes",
        ),
        "acyclic": (
            _applies_close_3_cycle, _apply_close_3_cycle, "cycle-of-3",
            (
                "a closing edge producing a cycle of length 3 — >= 3 deliberately, so "
                "the case isolates acyclic from asymmetric and irreflexive"
            ),
        ),
        "intransitive": (
            _applies_close_transitive_triple, _apply_close_transitive_triple,
            "transitive-closure-edge",
            "the closing edge (a,c) of an open path a->b->c — one step past intransitivity",
        ),
        "symmetric": (
            _applies_break_symmetry, _apply_break_symmetry, "unmirrored-edge",
            "one edge whose mirror is removed — one step past the symmetric frontier",
        ),
        "transitive": (
            _applies_break_transitivity, _apply_break_transitivity, "open-two-path",
            "an open path a->b->c whose closing edge is removed",
        ),
        "reflexive": (
            _applies_drop_participant_self_edge, _apply_drop_participant_self_edge,
            "participant-missing-self-edge",
            (
                "one PARTICIPANT missing its self-edge; non-participants are untouched, "
                "because LOCAL reflexivity does not constrain them "
                "(constraint-reference.md:404-426)"
            ),
        ),
        "purely-reflexive": (
            _applies_drop_participant_self_edge, _apply_drop_participant_self_edge,
            "participant-missing-self-edge",
            "one participant missing its self-edge (local reading)",
        ),
    }
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    family = "ring"
    variant = str(constraint.get("variant"))
    components = _ring_components_of(constraint)
    if not components:
        downs.append(
            NotDerivable(ref, family, "both", f"unknown ring variant {variant!r}")
        )
        return cases, downs

    cases.append(
        _baseline_case(
            ref, family, f"ring-{variant}-holds", "inside", doc,
            f"the edge set satisfies `{variant}` with no slack to spare — the "
            f"population sits exactly at the structural frontier",
        )
    )
    for component in components:
        entry = templates.get(component)
        if entry is None:
            downs.append(
                NotDerivable(
                    ref, family, f"outside-{component}",
                    f"no derived edge template crosses the `{component}` frontier",
                )
            )
            continue
        applies, apply, name, description = entry
        case, down = _via_operator(
            model, ref, constraint, ft, doc, rng, applies, apply,
            side="outside", name=f"ring-{component}-{name}", description=description,
        )
        if case is not None:
            cases.append(case)
        if down is not None:
            downs.append(down)
    return cases, downs


# ---- set families --------------------------------------------------------- #


def _derive_subset(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "subset"
    sub_seq = [r for r in constraint.get("subset_role_seq") or [] if isinstance(r, dict)]
    sup_seq = [r for r in constraint.get("superset_role_seq") or [] if isinstance(r, dict)]
    sub_rows = _seq_tuples(doc, model, sub_seq) if sub_seq else []
    sup_rows = _seq_tuples(doc, model, sup_seq) if sup_seq else []
    if not sub_rows or not sup_rows:
        downs.append(
            NotDerivable(
                ref, family, "inside",
                f"the subset side yields {len(sub_rows)} row(s) and the superset side "
                f"{len(sup_rows)}; a boundary over an empty side is a vacuity case wearing "
                f"a boundary label, not a containment edge",
            )
        )
    else:
        sub_keys = {tuple(_key(v) for v in t) for t in sub_rows}
        sup_keys = {tuple(_key(v) for v in t) for t in sup_rows}
        cases.append(
            _baseline_case(
                ref, family, "containment-edge", "inside", doc,
                f"the subset side holds {len(sub_keys)} distinct tuple(s), all present in "
                f"the {len(sup_keys)}-tuple superset — the containment edge, with the join "
                f"asserted non-degenerate on both sides",
            )
        )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_add_missing_subset, _apply_add_missing_subset,
        side="outside", name="one-tuple-past-containment",
        description="exactly one subset-side tuple absent from the superset — one step "
                    "past the containment edge",
    )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _equality_removals(model, constraint, doc) -> dict[str, tuple[str, int]]:
    """Per side, a removable row index whose entity values stay observable."""
    facts = doc.get("facts") or {}
    out: dict[str, tuple[str, int]] = {}
    for field_name in ("role_seq_a", "role_seq_b"):
        seq = [r for r in constraint.get(field_name) or [] if isinstance(r, dict)]
        ftids = {str(r.get("fact_type")) for r in seq}
        if len(ftids) != 1:
            continue
        ftid = next(iter(ftids))
        roles = [str(r.get("role")) for r in seq]
        rows = facts.get(ftid, [])
        for index in range(len(rows) - 1, -1, -1):
            fact = rows[index]
            if any(rn not in fact for rn in roles):
                continue
            observable = all(
                any(
                    _key(value) == _key(other_value)
                    for other_ftid, other_rows in facts.items()
                    for row_index, other in enumerate(other_rows)
                    if (other_ftid, row_index) != (ftid, index)
                    for other_value in other.values()
                )
                for value in fact.values()
            )
            if observable:
                out[field_name] = (ftid, index)
                break
    return out


def _derive_equality(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "equality"
    seq_a = [r for r in constraint.get("role_seq_a") or [] if isinstance(r, dict)]
    seq_b = [r for r in constraint.get("role_seq_b") or [] if isinstance(r, dict)]
    rows_a = _seq_tuples(doc, model, seq_a) if seq_a else []
    rows_b = _seq_tuples(doc, model, seq_b) if seq_b else []
    if not rows_a or not rows_b:
        downs.append(
            NotDerivable(
                ref, family, "inside",
                f"side A yields {len(rows_a)} row(s) and side B {len(rows_b)}; an equality "
                f"boundary over an empty side is a vacuity case wearing a boundary label",
            )
        )
    else:
        cases.append(
            _baseline_case(
                ref, family, "projections-identical", "inside", doc,
                f"the two projections are identical at {len(rows_a)} tuple(s) — the "
                f"equality edge, with both sides asserted non-degenerate",
            )
        )
    removals = _equality_removals(model, constraint, doc)
    # TWO directions, TWO cases — the D-06 table is explicit that one is not enough.
    for side_field, label in (("role_seq_a", "a"), ("role_seq_b", "b")):
        entry = removals.get(side_field)
        if entry is None:
            downs.append(
                NotDerivable(
                    ref, family, f"outside-side-{label}",
                    f"side {label.upper()} spans several fact types or carries no removable "
                    f"tuple whose entity values stay observable (removal would self-cancel "
                    f"under the closed world)",
                )
            )
            continue
        ftid, index = entry
        work = _clone(doc)
        del _facts_of(work, ftid)[index]
        cases.append(
            BoundaryCase(
                ref, family, f"one-tuple-removed-from-side-{label}", "outside", work,
                f"exactly one tuple removed from side {label.upper()} — one step past the "
                f"equality edge in the {label.upper()} direction",
                epsilon="1 tuple",
            )
        )
    return cases, downs


def _derive_exclusion(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "exclusion"
    seq_a = [r for r in constraint.get("role_seq_a") or [] if isinstance(r, dict)]
    seq_b = [r for r in constraint.get("role_seq_b") or [] if isinstance(r, dict)]
    rows_a = _seq_tuples(doc, model, seq_a) if seq_a else []
    rows_b = _seq_tuples(doc, model, seq_b) if seq_b else []
    if not rows_a or not rows_b:
        downs.append(
            NotDerivable(
                ref, family, "inside",
                f"side A yields {len(rows_a)} row(s) and side B {len(rows_b)}; with one side "
                f"empty the constraint is trivially satisfied, which is a vacuity case, not "
                f"the exclusion frontier",
            )
        )
    else:
        cases.append(
            _baseline_case(
                ref, family, "both-sides-populated-no-overlap", "inside", doc,
                f"both sides are populated ({len(rows_a)} / {len(rows_b)} tuples) and share "
                f"no tuple — the exclusion edge. Both sides non-empty is what makes this a "
                f"boundary rather than a trivial pass",
            )
        )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_add_overlap, _apply_add_overlap,
        side="outside", name="one-overlapping-tuple",
        description="exactly one tuple present on both sides — one step past the "
                    "exclusion edge",
    )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _multirole_xor_overlap(doc, model, constraint, rng) -> dict[str, Any]:
    """Place ONE tuple in both multi-role sequences.

    Each sequence must live in a single fact type — a sequence spanning several
    fact types has no single row that could create the overlap, and standing that
    down is the honest answer rather than inventing a join.
    """
    seqs = [
        [r for r in (seq or []) if isinstance(r, dict)]
        for seq in constraint.get("role_seqs") or []
    ]
    if len(seqs) < 2:
        raise NotDerivableError("fewer than two role sequences; there is nothing to overlap")
    plans = _multirole_xor_plans(constraint)

    # Build the shared tuple from the first sequence's declared role types, drawn
    # from the existing universe where possible so the overlap is the ONLY change.
    ftid, roles = plans[0]
    ft = _ft_by_id(model, ftid)
    if ft is None:
        raise NotDerivableError(f"fact type {ftid!r} does not exist in the model")
    existing = _seq_tuples(doc, model, seqs[0])
    if existing:
        shared = list(existing[0])
    else:
        row = _complete_row(doc, model, ft, {}, rng)
        _facts_of(doc, ftid).append(row)
        shared = [row[role] for role in roles]
    for plan_ftid, plan_roles in plans:
        plan_ft = _ft_by_id(model, plan_ftid)
        if plan_ft is None:
            raise NotDerivableError(f"fact type {plan_ftid!r} does not exist in the model")
        fixed = dict(zip(plan_roles, shared, strict=True))
        if any(
            all(_key(fact.get(role)) == _key(value) for role, value in fixed.items())
            for fact in (doc.get("facts") or {}).get(plan_ftid, [])
        ):
            continue
        _facts_of(doc, plan_ftid).append(_complete_row(doc, model, plan_ft, fixed, rng))
    return doc


def _multirole_xor_clean(doc, model, constraint, rng) -> dict[str, Any]:
    """Populate every multi-role sequence with tuples DISJOINT across sequences."""
    plans = _multirole_xor_plans(constraint)
    for index, (ftid, roles) in enumerate(plans):
        ft = _ft_by_id(model, ftid)
        if ft is None:
            raise NotDerivableError(f"fact type {ftid!r} does not exist in the model")
        if (doc.get("facts") or {}).get(ftid):
            continue
        # Fresh entities per sequence, so no tuple can appear in two of them.
        row = _complete_row(doc, model, ft, {}, rng, fresh_entities=True)
        del index, roles
        _facts_of(doc, ftid).append(row)
    seen: set[tuple[Any, ...]] = set()
    for seq_index, (ftid, roles) in enumerate(plans):
        for fact in list((doc.get("facts") or {}).get(ftid, [])):
            key = tuple(_key(fact.get(role)) for role in roles)
            if key in seen and seq_index:
                raise NotDerivableError(
                    "the sequences already share a tuple; a clean exclusion half is not "
                    "constructible without removing it, which would empty a side"
                )
            seen.add(key)
    return doc


def _multirole_xor_plans(constraint: dict[str, Any]) -> list[tuple[str, list[str]]]:
    plans: list[tuple[str, list[str]]] = []
    for seq in constraint.get("role_seqs") or []:
        flat = [r for r in (seq or []) if isinstance(r, dict)]
        ftids = {str(r.get("fact_type")) for r in flat}
        if len(ftids) != 1:
            raise NotDerivableError(
                "a multi-role sequence spans several fact types; no single row can "
                "populate it"
            )
        plans.append((next(iter(ftids)), [str(r.get("role")) for r in flat]))
    if len(plans) < 2:
        raise NotDerivableError("fewer than two role sequences")
    return plans


def _derive_exclusive_or(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "exclusive-or"
    refs = _xor_single_role(constraint)
    if refs is None:
        # Multi-role: the disjunctive half is UNDEFINED at arity > 1
        # (constraint-reference.md:319-331), so a clean exclusion half is
        # `unchecked` at band 4 and there is NO inside case to derive.
        downs.append(
            NotDerivable(
                ref, family, "inside",
                "multi-role exclusive-or: the disjunctive half is undefined at arity > 1 "
                "(constraint-reference.md:319-331), so 'plays exactly one' has no tuple "
                "universe and there is no inside case — a clean exclusion half is "
                "`unchecked` at band 4, never `pass`",
            )
        )
        # The CLEAN exclusion half — both sequences populated, no shared tuple —
        # is the band-4 route itself: the exclusion component is satisfied and
        # the disjunctive one has no tuple universe, so the checker answers
        # `unchecked` (`xor-disjunctive-undefined`) rather than `pass`. It is
        # unreachable from an EMPTY baseline, where the vacuity clause fires
        # first, so it needs its own construction.
        try:
            clean = _multirole_xor_clean(_clone(doc), model, constraint, rng)
        except NotDerivableError as error:
            downs.append(NotDerivable(ref, family, "frontier", error.reason))
        else:
            cases.append(
                BoundaryCase(
                    ref, family, "multirole-clean-exclusion-half", "frontier", clean,
                    "both multi-role sequences populated with DISJOINT tuples: the exclusion "
                    "half is clean and the disjunctive half is undefined at arity > 1, so the "
                    "honest verdict is `unchecked` (`xor-disjunctive-undefined`) — never "
                    "`pass`, which is what this branch reported before 01.1 probe #3",
                    case_kind="unchecked",
                )
            )
        try:
            work = _multirole_xor_overlap(_clone(doc), model, constraint, rng)
        except NotDerivableError as error:
            downs.append(NotDerivable(ref, family, "outside", error.reason))
        else:
            cases.append(
                BoundaryCase(
                    ref, family, "multirole-overlapping-tuple", "outside", work,
                    "one tuple present in BOTH multi-role sequences. The exclusion half "
                    "is decidable over tuples and a violation outranks indeterminacy "
                    "(D-08 precedence 1 > 4), so the predicted verdict is a violation "
                    "even though the disjunctive half stays undefined",
                    epsilon="1 tuple",
                )
            )
        return cases, downs

    sets = _xor_player_sets(refs, doc)
    if len(sets) >= 2 and any(sets):
        cases.append(
            _baseline_case(
                ref, family, "plays-exactly-one", "inside", doc,
                "every observable instance plays exactly one listed role — the "
                "exclusive-or edge",
            )
        )
    else:
        downs.append(
            NotDerivable(
                ref, family, "inside",
                "no listed role is played in the baseline; there is no instance sitting "
                "at the exclusive-or edge",
            )
        )
    for applies, apply, name, description in (
        (_applies_play_both, _apply_play_both, "plays-both",
         "one instance plays BOTH listed roles — the first of two outside directions"),
        (_applies_play_neither, _apply_play_neither, "plays-neither",
         (
             "one observable instance plays NEITHER listed role — the second outside "
             "direction; the instance stays observable so the closed world cannot "
             "self-cancel the case"
         )),
    ):
        case, down = _via_operator(
            model, ref, constraint, ft, doc, rng, applies, apply,
            side="outside", name=name, description=description,
        )
        if case is not None:
            cases.append(case)
        if down is not None:
            downs.append(down)
    return cases, downs


# ---- value-comparison / subtype-partition / textual ----------------------- #

def _derive_value_comparison(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "value-comparison"
    operator = str(constraint.get("operator") or "")
    operand_a, operand_b = _normalize_comparison_operands(model, constraint, ft)

    clock = next(
        (operand.raw for operand in (operand_a, operand_b) if operand.kind == "clock"), None
    )
    if clock is not None:
        cases.append(
            _baseline_case(
                ref, family, "clock-operand-frontier", "frontier", doc,
                f"the comparison's operand is the reference-clock form {clock!r}, which is "
                f"`unchecked` BY CONTRACT (reason `no-reference-clock`) — the case is emitted "
                f"and band 4 predicted rather than stood down",
                case_kind="unchecked",
            )
        )
        return cases, downs

    if ft is None:
        downs.append(
            NotDerivable(
                ref, family, "both",
                "the comparison is not an intra-fact role pair; a cross-fact operand pair "
                "needs a join whose row set the perturbation would have to preserve",
            )
        )
        return cases, downs
    if any(
        operand.kind == "literal" and operand.value is _UNTYPEABLE
        for operand in (operand_a, operand_b)
    ):
        cases.append(
            _baseline_case(
                ref, family, "untyped-literal-frontier", "frontier", doc,
                "the tagged literal cannot be interpreted in the compared role's primitive "
                "domain, so the checker must report `unchecked` rather than coerce it",
                case_kind="unchecked",
            )
        )
        return cases, downs
    if operator not in ("<", "<=", ">", ">=", "="):
        downs.append(
            NotDerivable(ref, family, "both", f"operator {operator!r} has no ordered frontier")
        )
        return cases, downs

    ftid = str(ft.get("id"))
    literal_pair = _role_literal_operands(model, constraint, ft)
    if literal_pair is not None:
        role_operand, literal_operand, operator = literal_pair
        role_a, role_b = role_operand.role, None
        anchor = literal_operand.value
        primitive = role_operand.primitive
    elif operand_a.kind == operand_b.kind == "role":
        role_a, role_b = operand_a.role, operand_b.role
        anchor = None
        primitive_a, primitive_b = operand_a.primitive, operand_b.primitive
        numeric = {"Integer", "Float", "Number"}
        compatible = primitive_a == primitive_b or {primitive_a, primitive_b} <= numeric
        if operator not in ("=", "!=") and not compatible:
            cases.append(
                _baseline_case(
                    ref,
                    family,
                    "values-not-comparable-frontier",
                    "frontier",
                    doc,
                    "the compared roles have incompatible declared primitive domains, so "
                    "the checker must report `unchecked` with reason "
                    "`values-not-comparable`; no value is copied across role domains",
                    case_kind="unchecked",
                )
            )
            return cases, downs
        if primitive_a != primitive_b:
            downs.append(
                NotDerivable(
                    ref,
                    family,
                    "both",
                    "the compared roles use different declared primitive domains; even "
                    "compatible numeric domains cannot safely share a boundary value "
                    "without risking a loader-invalid population",
                )
            )
            return cases, downs
        primitive = primitive_a
    else:
        downs.append(
            NotDerivable(
                ref, family, "both",
                "the comparison operands do not normalize to a role pair or a typed "
                "role/literal pair",
            )
        )
        return cases, downs
    assert role_a is not None
    index = None
    for position, fact in enumerate((doc.get("facts") or {}).get(ftid, [])):
        if role_a in fact and (role_b is None or role_b in fact):
            index = position
            break
    if index is None:
        downs.append(
            NotDerivable(
                ref, family, "both",
                "no fact carries the comparison's role operands; there is no occurrence to place at "
                "the equality frontier",
            )
        )
        return cases, downs

    if role_b is not None:
        anchor = (doc.get("facts") or {})[ftid][index][role_b]
    try:
        # Equality is the frontier; the OPERATOR decides which side it falls on.
        if operator in ("<=", ">=", "="):
            inside_value = anchor
            inside_eps = None
            outside_value, outside_eps = boundary_neighbour(
                anchor, primitive, +1 if operator in ("<=", "=") else -1
            )
        else:  # strict < / >
            inside_value, inside_eps = boundary_neighbour(
                anchor, primitive, -1 if operator == "<" else +1
            )
            outside_value, outside_eps = anchor, None
    except NoOrdering as error:
        downs.append(NotDerivable(ref, family, "both", str(error)))
        return cases, downs

    for side, value, eps in (
        ("inside", inside_value, inside_eps),
        ("outside", outside_value, outside_eps),
    ):
        work = _clone(doc)
        work["facts"][ftid][index][role_a] = value
        cases.append(
            BoundaryCase(
                ref, family, f"comparison-{side}", side, work,
                f"operator {operator!r} against operand {anchor!r}: equality is the frontier "
                f"and the operator decides which side it falls on; placed {value!r}",
                epsilon=eps, bound_value=anchor, placed_value=value,
            )
        )
    return cases, downs


def _partition_observability(model, constraint, doc) -> str | None:
    """``None`` when membership is observable; otherwise the mechanism that makes
    it derivation-only."""
    subtypes = [str(s) for s in constraint.get("subtypes") or []]
    by_id = {str(ot.get("id")): ot for ot in model.object_types or []}
    children = _direct_subtypes(model)
    derivation_only = [
        s
        for s in subtypes
        if str((by_id.get(s) or {}).get("derivation") or "") == "derived"
        and not _universe(doc, model, s, children)
    ]
    if not derivation_only:
        return None
    return (
        f"subtype(s) {derivation_only} are DERIVATION-ONLY (`derivation: derived`) "
        f"and have no roster or subtype-typed fact occurrence in this population, so "
        f"`_check_subtype_partition` returns `unchecked` (reason "
        f"`subtype-derivation-only`) here — the "
        f"violating and boundary cells are not measurable here, and counting them "
        f"covered would inflate the coverage fraction"
    )


def _derive_subtype_partition(model, ref, constraint, ft, doc, rng):
    cases, downs = [], []
    family = "subtype-partition"
    mechanism = _partition_observability(model, constraint, doc)
    if mechanism is not None:
        for side in ("inside", "outside"):
            downs.append(NotDerivable(ref, family, side, mechanism))
        cases.append(
            _baseline_case(
                ref, family, "derivation-only-frontier", "frontier", doc,
                "membership is observable only through rosters or subtype-typed roles; "
                "this model's partition is derivation-rule-only, so the predicted verdict "
                "is `unchecked` (reason `subtype-derivation-only`)",
                case_kind="unchecked",
            )
        )
        return cases, downs

    cases.append(
        _baseline_case(
            ref, family, "membership-at-the-edge", "inside", doc,
            "every supertype instance sits in exactly the memberships the partition's "
            "flags demand — the partition edge, observable through subtype-typed roles",
        )
    )
    case, down = _via_operator(
        model, ref, constraint, ft, doc, rng,
        _applies_place_two_subtypes, _apply_place_two_subtypes,
        side="outside", name="instance-in-two-subtypes",
        description="one instance asserted into two subtypes — one step past the "
                    "exclusivity edge",
    )
    if case is not None:
        cases.append(case)
    if down is not None:
        downs.append(down)
    return cases, downs


def _derive_textual(model, ref, constraint, ft, doc, rng):
    """Never mechanically evaluable: ONE case per model, predicting `unchecked`."""
    return (
        [
            _baseline_case(
                ref, "textual", "textual-is-never-mechanical", "frontier", doc,
                "a textual constraint is never mechanically evaluable; exactly ONE case "
                "per model is emitted, predicting `unchecked` (reason "
                "`textual-not-mechanical`) and nothing else",
                case_kind="unchecked",
            )
        ],
        [],
    )


_DERIVERS = {
    "value": _derive_value,
    "uniqueness": _derive_uniqueness,
    "frequency": _derive_frequency,
    "cardinality": _derive_cardinality,
    "mandatory": _derive_mandatory,
    "mandatory-disjunctive": _derive_mandatory_disjunctive,
    "ring": _derive_ring,
    "subset": _derive_subset,
    "equality": _derive_equality,
    "exclusion": _derive_exclusion,
    "exclusive-or": _derive_exclusive_or,
    "value-comparison": _derive_value_comparison,
    "subtype-partition": _derive_subtype_partition,
}


# --------------------------------------------------------------------------- #
# the public derivation entry points
# --------------------------------------------------------------------------- #


def derive_boundary_cases(
    model: Model,
    constraint_ref: str,
    baseline_doc: dict[str, Any],
    rng: Random | None = None,
) -> tuple[list[BoundaryCase], list[NotDerivable]]:
    """The boundary set for ONE constraint, plus its not-derivable records.

    The two lists together account for every constrained parameter the constraint
    declares — that totality is what makes coverage a measurement rather than a
    claim.

    NOTE the signature deviates from the plan's ``(model, constraint_ref,
    baseline_doc, pool)``: a boundary value is derived from the BOUND, never
    drawn from the pool. A pool draw would defeat the derivation — the whole
    point of D-06 is that the value comes from the model. ``rng`` is carried for
    the row-completion helpers that must fill unconstrained companion roles.
    """
    rng = rng if rng is not None else Random(0)
    constraint, ft = _resolve(model, constraint_ref)
    family = str(constraint.get("type"))
    if family == "anchored":
        return [], [NotDerivable(
            constraint_ref, family, "both",
            "source-anchor boundary synthesis requires document and sidecar bytes",
        )]
    if family == "textual":
        return _derive_textual(model, constraint_ref, constraint, ft, baseline_doc, rng)
    if family not in IMPLEMENTED_FAMILIES:
        return [], [
            NotDerivable(
                constraint_ref, family, "both",
                f"family {family!r} is not in checker.IMPLEMENTED_FAMILIES, so every "
                f"population is `unchecked` (reason `family-unimplemented`) and no bound "
                f"is mechanically decidable",
            )
        ]
    if family == "guarded":
        # Guarded evaluation ships before guarded witness synthesis.  Name the
        # post-MVP frontier explicitly instead of letting IMPLEMENTED_FAMILIES
        # turn a missing deriver into an accidental coverage claim.
        return [], [
            NotDerivable(
                constraint_ref,
                family,
                "both",
                "guarded boundary-witness synthesis is a post-MVP frontier; "
                "no boundary deriver is shipped for this family",
            )
        ]
    deriver = _DERIVERS.get(family)
    if deriver is None:
        return [], [
            NotDerivable(
                constraint_ref, family, "both",
                f"no boundary deriver is registered for family {family!r}",
            )
        ]
    try:
        return deriver(model, constraint_ref, constraint, ft, baseline_doc, rng)
    except NotDerivableError as error:
        return [], [NotDerivable(constraint_ref, family, "both", error.reason)]


def enumerate_boundary(
    model: Model, baseline_doc: dict[str, Any], rng: Random | None = None
) -> tuple[list[BoundaryCase], list[NotDerivable]]:
    """Every constraint's boundary set for one model.

    ``textual`` gets exactly ONE case per model (the D-06 table's instruction);
    any further textual constraint records that the first carries the case, so
    the corpus does not fill with identical unchecked populations.
    """
    rng = rng if rng is not None else Random(0)
    cases: list[BoundaryCase] = []
    downs: list[NotDerivable] = []
    textual_carrier: str | None = None
    for ref, constraint, _ft in _constraint_iter_with_ref(model):
        if str(constraint.get("type")) == "textual":
            if textual_carrier is not None:
                downs.append(
                    NotDerivable(
                        ref, "textual", "both",
                        f"exactly one textual case per model (D-06 table); "
                        f"{textual_carrier} carries it",
                    )
                )
                continue
            textual_carrier = ref
        case_list, down_list = derive_boundary_cases(model, ref, baseline_doc, rng)
        cases.extend(case_list)
        downs.extend(down_list)
    return cases, downs
