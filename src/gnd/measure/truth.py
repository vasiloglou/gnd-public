"""Ground-truth states, constraint-ref resolution, and the typed expectation join.

The measurement lane never re-derives ground truth at scoring time — it READS
the constructive witness the generator wrote into the sidecar (C1/C3). This
module holds the three pieces that read make requires:

- :data:`GroundTruth` — the three states a constraint's subject universe can be
  in over one population: ``satisfied`` / ``violated`` / ``no-subjects``. The
  third exists because it is the state the F-02/F-05 defect family lives in — a
  zero-subject universe a naive checker calls a clean pass.
- :func:`resolve_constraint_ref` — parse the two locked ref forms the checker
  emits (``fact_types[<id>].constraints[<index>]`` and ``constraints[<index>]``)
  and return the constraint dict, so the report can join ``source`` and
  ``status`` onto every row (the D-12 provenance join: a reader must be able to
  see whether false passes cluster in ``llm-inferred`` constraints).
- :func:`expectation_for` — read the typed :class:`~gnd.synth.provenance.ExpectedState`
  the sidecar carries for a constraint ref. A constraint absent from the map is
  a GENERATOR defect, not a default: a silent default is exactly how a case
  leaks out of the accounting.

**The cardinality-min-over-empty exception is labelled at derivation time, not
here.** A ``cardinality {min: N>=1}`` over an empty universe is a *decided
failure* — the count of zero IS the evidence — so its ground truth is
``violated`` and ``fail`` is CORRECT. The generator writes
``{violated, fail, ...}`` into the sidecar for that case (corpus case
``an-unmet-lower-bound-over-nothing-is-still-a-failure``); this module simply
trusts the label rather than re-deriving a rule that would get the exception
wrong. :func:`expectation_for` returns whatever the sidecar recorded.
"""

from __future__ import annotations

import re
from typing import Any

from gnd.model import Model
from gnd.synth.provenance import ExpectedState, GroundTruth, Sidecar

__all__ = [
    "ConstraintRefError",
    "ExpectationMissingError",
    "GroundTruth",
    "expectation_for",
    "resolve_constraint_ref",
]

#: ``fact_types[<id>].constraints[<index>]`` — an inline constraint. The id is
#: an opaque model token (any non-``]`` run); the index is the constraint's
#: position in that fact type's ``constraints`` list.
_INLINE_REF = re.compile(r"^fact_types\[(?P<ft>[^\]]+)\]\.constraints\[(?P<idx>\d+)\]$")
#: ``constraints[<index>]`` — a top-level constraint.
_TOPLEVEL_REF = re.compile(r"^constraints\[(?P<idx>\d+)\]$")


class ConstraintRefError(Exception):
    """A constraint ref did not parse, or named a fact type / index that does
    not exist in the model. Loud by design: a ref the report cannot resolve
    would join no provenance and silently drop a row's ``source``/``status``."""


class ExpectationMissingError(Exception):
    """A scored constraint has no :class:`ExpectedState` in the sidecar (C3).

    A missing expectation is a GENERATOR defect — the sidecar owner promises one
    entry per model constraint — so it is raised rather than defaulted. A
    default ``{satisfied, pass}`` would score every unlabelled constraint
    ``correct`` and quietly improve every rate, which is the exact leak the
    partition invariant exists to prevent.
    """


def _fact_type_constraints(fact_type: dict[str, Any]) -> list[dict[str, Any]]:
    return list(fact_type.get("constraints") or [])


def resolve_constraint_ref(model: Model, ref: str) -> dict[str, Any]:
    """Return the constraint dict named by ``ref`` (D-12 provenance join).

    ``ref`` is one of the two forms :func:`gnd.checker.check` emits. A ref that
    does not parse, names an unknown fact type, or indexes past the constraint
    list raises :class:`ConstraintRefError` — the report joins ``source`` and
    ``status`` off the constraint this resolves, so an unresolvable ref is a
    loud failure, not a blank column.
    """
    # v5.0 Phase 3 (D-P3.6): a derivation obligation is not a constraint and
    # carries no sidecar expectation — synth refuses structured models at the
    # generator band, so no shipped corpus can label one. Refused by NAME so a
    # future caller learns the boundary, not the generic two-forms error.
    if ref.startswith("derivation:"):
        raise ConstraintRefError(
            f"ref {ref!r} names a derivation obligation, which is outside the "
            f"constraint expectation contract: derivation verdicts ride the "
            f"report's derivations[] block, and the measurement lane makes no "
            f"claim about them (v5.0 Phase 3, D-P3.6)."
        )

    inline = _INLINE_REF.match(ref)
    if inline is not None:
        ft_id = inline.group("ft")
        index = int(inline.group("idx"))
        for fact_type in model.fact_types or []:
            if str(fact_type.get("id")) == ft_id:
                constraints = _fact_type_constraints(fact_type)
                if 0 <= index < len(constraints):
                    return constraints[index]
                raise ConstraintRefError(
                    f"constraint ref {ref!r} indexes position {index} but fact "
                    f"type {ft_id!r} declares {len(constraints)} constraint(s)."
                )
        raise ConstraintRefError(
            f"constraint ref {ref!r} names fact type {ft_id!r}, which is not in "
            f"the model."
        )

    toplevel = _TOPLEVEL_REF.match(ref)
    if toplevel is not None:
        index = int(toplevel.group("idx"))
        constraints = list(model.constraints or [])
        if 0 <= index < len(constraints):
            return constraints[index]
        raise ConstraintRefError(
            f"constraint ref {ref!r} indexes top-level position {index} but the "
            f"model declares {len(constraints)} top-level constraint(s)."
        )

    raise ConstraintRefError(
        f"constraint ref {ref!r} matches neither "
        f"'fact_types[<id>].constraints[<index>]' nor 'constraints[<index>]' — "
        f"the two forms gnd.checker.check emits."
    )


def expectation_for(sidecar: Sidecar, constraint_ref: str) -> ExpectedState:
    """The typed :class:`ExpectedState` the sidecar recorded for ``constraint_ref``.

    Raises :class:`ExpectationMissingError` when the ref is absent — a generator
    defect, never a default (C3). The returned state carries the constructive
    ground truth, the verdict a correct checker should emit, and the reason the
    two diverge (``textual-not-mechanical``, ``subtype-derivation-only``), which
    is what lets an expected-unchecked-by-design constraint score ``correct``
    rather than a mislabelled ``undecided``.
    """
    try:
        return sidecar.expectations[constraint_ref]
    except KeyError as error:
        raise ExpectationMissingError(
            f"the sidecar for {sidecar.population!r} carries no expectation for "
            f"constraint {constraint_ref!r} — a generator defect (C3): every "
            f"model constraint must be labelled at derivation time, and a missing "
            f"label cannot be defaulted without leaking the case out of every "
            f"rate."
        ) from error
