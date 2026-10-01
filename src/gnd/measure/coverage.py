"""Coverage as an APPLICABILITY MATRIX, not "all five kinds per family" (C5).

"Every family has all five case kinds" is semantically impossible, and forcing it
would manufacture invalid cases — the exact failure the coverage system exists to
prevent. ``textual`` is never mechanically conforming or violating (the checker
excludes it from ``IMPLEMENTED_FAMILIES`` and always answers ``unchecked``), a
derivation-only ``subtype-partition`` cannot be violated by any population, and
some families have no band-4 route at all.

So every ``(family, case_kind)`` pair is a CELL with one of three statuses:

``covered``
    at least one emitted case lands in it.
``not-applicable``
    the cell cannot exist for this family on this model, WITH A REASON. It leaves
    the numerator AND the denominator.
``missing``
    the cell is applicable and absent — a real gap, and a test failure.

``coverage = covered_applicable_cells / applicable_cells``.

The point of the denominator rule is that an unmeasurable family must read as
unmeasurable, never as covered: counting ``textual``/conforming as covered would
inflate the fraction with a cell no population can ever occupy, and counting it
as missing would make the fraction unreachable and therefore meaningless. Both
failures are the same failure — a coverage number that does not describe what was
measured — and the visible ``not-applicable`` reason is what keeps a reader able
to check.

Every numerator and denominator here is derived from the MODEL document and the
EMITTED sidecars. Nothing is a constant (research assumption A4).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from gnd.checker import IMPLEMENTED_FAMILIES
from gnd.model import Model
from gnd.synth.comparison import _UNTYPEABLE, normalize_operands
from gnd.synth.frontier import SHARED_REASON_CODES, reason_codes_by_family
from gnd.synth.provenance import CASE_KIND_TO_LABEL

__all__ = [
    "CASE_KINDS",
    "Cell",
    "applicability_matrix",
    "coverage_fraction",
    "families_in_model",
]

#: The five case kinds a measurement distinguishes, in canonical order. Derived
#: from the sidecar's own mapping so a sixth kind cannot be added to one place
#: and forgotten in the other.
CASE_KINDS: tuple[str, ...] = tuple(CASE_KIND_TO_LABEL)


@dataclass(frozen=True)
class Cell:
    """One ``(family, case_kind)`` cell of the applicability matrix."""

    family: str
    case_kind: str
    status: str  # covered | not-applicable | missing
    count: int = 0
    reason: str | None = None

    def as_record(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "case_kind": self.case_kind,
            "status": self.status,
            "count": self.count,
            "reason": self.reason,
        }


def families_in_model(model: Model) -> list[str]:
    """Every constraint family the model DECLARES, derived from the document."""
    from gnd.synth.assemble import _constraint_iter_with_ref

    return sorted(
        {str(constraint.get("type")) for _ref, constraint, _ft in _constraint_iter_with_ref(model)}
    )


def _partition_is_derivation_only(model: Model) -> str | None:
    """The mechanism that makes this model's ``subtype-partition`` FAMILY
    unmeasurable, or ``None`` when at least one partition's membership is
    observable.

    The decision is about the FAMILY, so every declared partition is inspected.
    The loop this replaces returned on the FIRST partition it met either way, so
    a model declaring a derivation-only partition BEFORE an observable one marked
    the family's ``violating``, ``boundary`` and ``no-subjects`` cells
    ``not-applicable`` — and ``coverage_fraction`` removes not-applicable cells
    from its denominator, so coverage was flattered by hiding three cells a real
    case could occupy. One observable partition is enough to make the family
    measurable, which is what the ``None`` branch's comment always claimed.

    ``full_vocabulary`` declares a single partition, so the committed numbers are
    unaffected; the rule was wrong for any model with two.
    """
    from gnd.synth.assemble import _constraint_iter_with_ref
    from gnd.synth.boundary import _partition_observability

    mechanisms = [
        _partition_observability(model, constraint, {})
        for _ref, constraint, _ft in _constraint_iter_with_ref(model)
        if str(constraint.get("type")) == "subtype-partition"
    ]
    if not mechanisms or any(mechanism is None for mechanism in mechanisms):
        return None  # no partitions at all, or at least one IS observable
    return mechanisms[0]


def _applicability(model: Model, family: str) -> dict[str, str | None]:
    """``case_kind -> not-applicable reason`` (``None`` means APPLICABLE).

    Every rule below is derived from the checker's own vocabulary or the model
    document, never from a hand-maintained exclusion list.
    """
    out: dict[str, str | None] = dict.fromkeys(CASE_KINDS)

    if family == "anchored":
        mechanism = "anchored verdicts require a bound source document and sidecar; population-only measurement has no source witness"
        out["conforming"] = mechanism
        out["violating"] = mechanism
        out["boundary"] = "anchored declares no numeric boundary; the source span is a binding, not a model bound"
        out["no-subjects"] = None
        return out

    if family not in IMPLEMENTED_FAMILIES:
        # `textual` and any future unimplemented family: the checker answers
        # `unchecked` for EVERY population (checker.IMPLEMENTED_FAMILIES), so no
        # population can make it mechanically conforming, violating, or place it
        # at a bound. Only the decidability frontier exists.
        mechanism = (
            f"family {family!r} is excluded from checker.IMPLEMENTED_FAMILIES, so every "
            f"population over it is `unchecked` — no population can make it mechanically "
            f"{{kind}}"
        )
        out["conforming"] = mechanism.format(kind="conforming")
        out["violating"] = mechanism.format(kind="violating")
        out["boundary"] = (
            f"family {family!r} declares no mechanically-readable bound, so there is no "
            f"frontier to sit at"
        )
        out["no-subjects"] = (
            f"family {family!r} returns `unchecked` at the verdict step and never reaches "
            f"the subject-set step, so it cannot be vacuous "
            f"(01.1-VERIFICATION residual-routes table)"
        )
        return out

    if family == "subtype-partition":
        mechanism = _partition_is_derivation_only(model)
        if mechanism is not None:
            # A derivation-only partition answers `unchecked` BEFORE any
            # subject-set step, so it never reaches vacuity either: the
            # no-subjects cell is unmeasurable here for the same reason the
            # violating and boundary cells are.
            out["violating"] = mechanism
            out["boundary"] = mechanism
            out["no-subjects"] = (
                mechanism
                + " — and because the verdict is settled before the subject-set step, "
                "emptying the supertype universe cannot make it vacuous either"
            )

    owned = reason_codes_by_family().get(family, ())
    if not owned:
        out["unchecked"] = (
            f"the checker declares no band-4 reason code inside its `{family}` branch, so "
            f"the family has no undecidability frontier of its own. The cross-cutting "
            f"guards ({', '.join(SHARED_REASON_CODES)}) are structural model faults any "
            f"family's constraint can reach, not a property of this one"
        )
        return out
    unreachable = _unchecked_shape_reason(model, family, owned)
    if unreachable is not None:
        out["unchecked"] = unreachable
    return out


def _unchecked_shape_reason(
    model: Model, family: str, owned: tuple[str, ...]
) -> str | None:
    """``None`` when this MODEL declares a constraint whose shape reaches one of
    the family's own band-4 routes; otherwise the reason it cannot.

    Every predicate reads the MODEL DOCUMENT — never the checker's output over a
    population, which would make the denominator depend on the observation it is
    supposed to contextualise. A route the model's shapes cannot reach is
    ``not-applicable`` with the shape named, so the reader can see the difference
    between "this family has no undecidable case here" and "we forgot one".
    """
    from gnd.synth.assemble import _constraint_iter_with_ref, _role_object

    role_obj = _role_object(model)
    constraints = [
        (constraint, ft)
        for _ref, constraint, ft in _constraint_iter_with_ref(model)
        if str(constraint.get("type")) == family
    ]

    def shape() -> bool:
        for constraint, ft in constraints:
            if family == "textual":
                return True
            if family == "mandatory":
                names = {str(r.get("role_name")) for r in (ft or {}).get("roles") or []}
                if str(constraint.get("role")) not in names:
                    return True
            elif family == "mandatory-disjunctive":
                oids = {
                    role_obj.get(str(r.get("fact_type")), {}).get(str(r.get("role")))
                    for r in constraint.get("role_refs") or []
                    if isinstance(r, dict)
                }
                if len(oids) > 1:
                    return True
            elif family == "ring":
                if len((ft or {}).get("roles") or []) != 2:
                    return True
            elif family == "exclusive-or":
                seqs = [list(s or []) for s in constraint.get("role_seqs") or []]
                if any(len(s) != 1 for s in seqs):
                    return True
                oids = {
                    role_obj.get(str(s[0].get("fact_type")), {}).get(str(s[0].get("role")))
                    for s in seqs
                    if s
                }
                if len(oids) > 1:
                    return True
            elif family == "value":
                if _value_bound_type_mismatches(model, constraint):
                    return True
            elif family == "value-comparison":
                if _comparison_is_undecidable(model, constraint, ft):
                    return True
            elif family == "subtype-partition":
                if not constraint.get("exclusive") and not constraint.get("exhaustive"):
                    return True
                # Unchecked applicability is per CONSTRAINT. The family-wide
                # predicate above answers whether any partition makes the ordinary
                # conforming/violating cells measurable; using it here lets one
                # observable partition mask a different derived-only partition's
                # real `subtype-derivation-only` route.
                from gnd.synth.boundary import _partition_observability

                if _partition_observability(model, constraint, {}) is not None:
                    return True
        return False

    if shape():
        return None
    return (
        f"the model declares no `{family}` constraint whose shape reaches any of its own "
        f"band-4 routes ({', '.join(owned)}): every one of them resolves cleanly, so this "
        f"model has no undecidable `{family}` case to pin. Another model with the guarded "
        f"shape would make this cell applicable"
    )


def _value_bound_type_mismatches(model: Model, constraint: dict[str, Any]) -> bool:
    """A declared bound whose type does not match the governed role's primitive."""
    from gnd import popvalidate

    primitive = popvalidate.resolve_primitive(str(constraint.get("object_type") or ""), model)
    numeric = primitive in ("Integer", "Float", "Number")
    declared_ranges = []
    if constraint.get("range") is not None:
        declared_ranges.append(constraint["range"])
    declared_ranges.extend(constraint.get("ranges") or [])
    for value_range in declared_ranges:
        for edge in ("min", "max"):
            bound = value_range.get(edge)
            if bound is None:
                continue
            if numeric and (
                isinstance(bound, bool) or not isinstance(bound, (int, float))
            ):
                return True
            if primitive is not None and not numeric and not isinstance(bound, str):
                return True
    return False


def _comparison_is_undecidable(
    model: Model, constraint: dict[str, Any], ft: dict[str, Any] | None
) -> bool:
    """A reference-clock operand, an untypeable literal, or mismatched operand
    primitives — the three shapes ``_check_value_comparison`` declines to decide."""
    operands = normalize_operands(model, constraint, ft)
    if any(operand.kind in ("clock", "invalid") for operand in operands):
        return True
    if all(operand.kind in ("role", "cross-role") for operand in operands):
        primitive_a, primitive_b = (operand.primitive for operand in operands)
        numeric = {"Integer", "Float", "Number"}
        compatible = primitive_a == primitive_b or {
            primitive_a,
            primitive_b,
        } <= numeric
        if constraint.get("operator") not in ("=", "!=") and not compatible:
            return True
    return any(
        operand.kind == "literal" and operand.value is _UNTYPEABLE
        for operand in operands
    )


def applicability_matrix(
    model: Model, observed: dict[tuple[str, str], int]
) -> list[Cell]:
    """The full ``(family, case_kind)`` grid for one model.

    ``observed`` maps ``(family, case_kind) -> case count`` and comes from the
    corpus's own sidecars.
    """
    cells: list[Cell] = []
    for family in families_in_model(model):
        applicability = _applicability(model, family)
        for case_kind in CASE_KINDS:
            reason = applicability[case_kind]
            count = observed.get((family, case_kind), 0)
            if reason is not None:
                cells.append(Cell(family, case_kind, "not-applicable", count, reason))
            elif count:
                cells.append(Cell(family, case_kind, "covered", count))
            else:
                cells.append(
                    Cell(
                        family,
                        case_kind,
                        "missing",
                        0,
                        f"applicable but absent: no {case_kind} case was emitted for "
                        f"{family!r} — a real gap in the corpus, not a property of the "
                        f"family",
                    )
                )
    return cells


def coverage_fraction(cells: list[Cell]) -> tuple[int, int, float | None]:
    """``(covered_applicable, applicable, fraction)``.

    ``not-applicable`` cells are OUT of the denominator (C5). A model whose every
    cell is not-applicable yields ``None`` rather than a flattering ``1.0`` — no
    applicable surface means no coverage claim, exactly as a zero denominator
    yields ``None`` for a rate (C2).
    """
    applicable = [c for c in cells if c.status != "not-applicable"]
    covered = [c for c in applicable if c.status == "covered"]
    if not applicable:
        return 0, 0, None
    return len(covered), len(applicable), len(covered) / len(applicable)


def observed_cells(sidecars: list[Any], model: Model) -> dict[tuple[str, str], int]:
    """``(family, case_kind) -> count`` read off the corpus's sidecars.

    A ``conforming`` population has no single target constraint: it satisfies
    EVERY constraint the model declares, so it covers the ``conforming`` cell of
    every declared family. Every other kind names its target, and the family is
    resolved from the constraint that ref points at.
    """
    declared = families_in_model(model)
    out: dict[tuple[str, str], int] = {}
    for sidecar in sidecars:
        case_kind = sidecar.case_kind or (
            "conforming" if sidecar.class_ == "conforming" else sidecar.class_
        )
        if case_kind == "conforming":
            for family in declared:
                out[(family, "conforming")] = out.get((family, "conforming"), 0) + 1
            continue
        target = sidecar.target or sidecar.violates_target
        if target is None:
            continue
        constraint = _resolve_or_none(model, target)
        if constraint is None:
            continue
        _assert_case_kind_invariant(sidecar, target, case_kind)
        family = str(constraint.get("type"))
        out[(family, case_kind)] = out.get((family, case_kind), 0) + 1
    return out


def _assert_case_kind_invariant(sidecar: Any, target: str, case_kind: str) -> None:
    """Reject sidecars whose credited row contradicts their target expectation.

    Coverage is a count of exercised semantic cells, not a count of labels. A
    forged or stale ``case_kind`` must therefore fail input validation instead of
    moving a case into an easier numerator bucket.
    """
    if case_kind not in ("unchecked", "no-subjects"):
        return
    from gnd.measure.score import InconsistentExpectationError

    state = (getattr(sidecar, "expectations", None) or {}).get(target)
    predicted = getattr(sidecar, "predicted_verdict", None)
    population = getattr(sidecar, "population", "<unknown>")
    if case_kind == "unchecked":
        consistent = (
            state is not None
            and state.expected_verdict == "unchecked"
            and bool(state.reason)
            and predicted == "unchecked"
        )
        required = "expected_verdict='unchecked' with a reason"
    else:
        consistent = (
            state is not None
            and state.ground_truth == "no-subjects"
            and state.expected_verdict == "vacuous"
            and predicted == "vacuous"
        )
        required = "ground_truth='no-subjects', expected_verdict='vacuous'"
    if not consistent:
        rendered = state.model_dump() if state is not None else None
        raise InconsistentExpectationError(
            f"sidecar for {population!r} labels target {target!r} as {case_kind!r}, "
            f"but coverage credit requires {required} and matching predicted_verdict; "
            f"recorded expectation={rendered!r}, predicted_verdict={predicted!r}"
        )


def _resolve_or_none(model: Model, ref: str) -> dict[str, Any] | None:
    """The constraint a ref names, or ``None``.

    A ref that no longer resolves contributes NOTHING to coverage rather than
    crashing the report: the corpus and the model have drifted, and the C6
    sidecar binding is where that is caught loudly (exit 3). Silently crediting
    it would be worse than silently dropping it.
    """
    from gnd.measure.truth import ConstraintRefError, resolve_constraint_ref

    try:
        return resolve_constraint_ref(model, ref)
    except (ConstraintRefError, KeyError, IndexError, ValueError):
        return None
