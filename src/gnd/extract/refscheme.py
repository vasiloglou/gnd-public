"""Three-path reference-scheme resolution and the applicable-set artifact (R-10′).

The extractor's matcher needs every entity to have a printable identity — and
measured on the primary model, a third of its fact types touch an entity that
has none directly (``reference.mode`` ``unit-based``/``external`` yield no
``reference.value_type``). This module answers with THREE paths instead of one,
because the alternative is five fact types silently vanishing from every
denominator — the flattered number this phase exists to prevent:

1. **Direct** — ``popular``/``general`` modes and subtypes via
   ``inherits_reference``: :func:`reference_identity` CALLS
   ``popvalidate.resolve_reference_value_type`` — never a second
   reference-scheme walk (``synth/pool.py:16-17`` states the in-repo rule).
2. **Composite** — an ``external``-mode entity whose top-level external
   ``uniqueness`` constraint anchors on it. The identifying sequence lives in
   ``role_refs`` — the research prototype read ``constraint.get("roles")`` and
   silently matched nothing (the PANEL-5-named bug). Each referenced role's
   object type must itself resolve (recursively, cycle-safe with a ``seen``
   set — subtype cycles are not rejected by model validation, T-01.1-07).
3. **Unmatchable** — declared, with a MECHANISM string in
   ``measure/coverage.py:126-136``'s register: what makes the identity
   underivable, never a bare label.

Every disposition is derived from the model document — never a hand-maintained
exclusion list (coverage.py ``_applicability``'s governing rule): a hard-coded
``{"salary"}`` would miss ``booking`` on the next model and mislabel the first
model that widens its pool.

:func:`applicable_set` publishes the result as the first-class JSON artifact
``gnd extract`` writes (``<stem>.applicable.json``) and that doccheck/fidelity
consume fail-closed: an unmeasurable fact type reads as unmeasurable with its
mechanism, never as coverage.
"""

from __future__ import annotations

from typing import Any

from gnd.extraction_scope import fact_type_scope
from gnd.popvalidate import resolve_reference_value_type

__all__ = ["applicable_set", "reference_identity"]


def _object_types_by_id(model: Any) -> dict[str, dict[str, Any]]:
    return {
        str(object_type.get("id")): object_type for object_type in model.object_types
    }


def _fact_types_by_id(model: Any) -> dict[str, dict[str, Any]]:
    return {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}


def _referenced_object_type(role_ref: dict[str, Any], model: Any) -> str | None:
    """The object type playing the role a ``role_ref`` names, or ``None``."""
    fact_type = _fact_types_by_id(model).get(str(role_ref.get("fact_type")))
    if fact_type is None:
        return None
    for role in fact_type.get("roles") or []:
        if str(role.get("role_name")) == str(role_ref.get("role")):
            return str(role.get("object_type"))
    return None


def _anchors_on(role_refs: list[dict[str, Any]], oid: str, model: Any) -> bool:
    """Does this external UC's role sequence identify ``oid``?

    It does when every referenced fact type ALSO plays ``oid`` in a role other
    than the referenced one — the UC then says "the combination of these role
    values is unique", which is precisely a composite identifier for the
    entity those fact types share.
    """
    fact_types = _fact_types_by_id(model)
    for role_ref in role_refs:
        if not isinstance(role_ref, dict):
            return False
        fact_type = fact_types.get(str(role_ref.get("fact_type")))
        if fact_type is None:
            return False
        roles = fact_type.get("roles") or []
        named = str(role_ref.get("role"))
        if not any(str(role.get("role_name")) == named for role in roles):
            return False
        if not any(
            str(role.get("object_type")) == oid
            and str(role.get("role_name")) != named
            for role in roles
        ):
            return False
    return True


def _unmatchable_reason(oid: str, model: Any) -> str:
    """A mechanism, not a label (coverage.py:126-136's register): WHAT makes
    the identity underivable, derived from the model document."""
    object_type = _object_types_by_id(model).get(oid) or {}
    reference = object_type.get("reference") or {}
    mode = reference.get("mode")
    if mode == "unit-based":
        unit = reference.get("unit")
        measure_type = reference.get("measure_type")
        return (
            f"reference.mode='unit-based' declares unit {unit!r} "
            f"(measure_type {measure_type!r}) and no external uniqueness "
            f"constraint anchors on {oid!r} — the pool draws an opaque "
            f"surrogate rather than a measure value, so no reference value "
            f"exists to render or match"
        )
    if mode == "external":
        return (
            f"reference.mode='external' declares no value_type by definition "
            f"and no external uniqueness constraint's role_refs anchor on "
            f"{oid!r}, so no composite identity is derivable"
        )
    if object_type.get("subtype_of"):
        return (
            f"subtype {oid!r} resolves no single inherited reference "
            f"(inherits_reference absent or false, ancestor disagreement, or "
            f"a subtype cycle — resolve_primitive's documented None routes), "
            f"so no reference value exists to render or match"
        )
    return (
        f"object type {oid!r} declares no reference scheme that yields a "
        f"printable value (resolve_reference_value_type returned None), so "
        f"no reference value exists to render or match"
    )


def reference_identity(
    object_type_id: str, model: Any, *, _seen: set[str] | None = None
) -> tuple[str, Any]:
    """``("direct", value_type_id)`` | ``("composite", resolved_role_refs)`` |
    ``("unmatchable", reason)``.

    Path 1 delegates to ``popvalidate.resolve_reference_value_type`` (call,
    never re-implement). Path 2 consumes ``role_refs`` from a top-level
    external ``uniqueness`` constraint that anchors on this object type, each
    referenced role's object type resolved recursively. Path 3 is an explicit
    refusal carrying its mechanism.
    """
    # Each recursive branch gets its own ancestor set. Completed siblings are
    # not ancestors and must not be mistaken for a cycle when two component
    # roles are played by the same directly identified object type.
    seen = set() if _seen is None else set(_seen)
    oid = str(object_type_id)
    if oid in seen:
        return (
            "unmatchable",
            (
                f"reference resolution for {oid!r} re-entered itself through "
                f"a composite chain — a reference cycle yields no ground "
                f"identity"
            ),
        )
    seen.add(oid)

    value_type = resolve_reference_value_type(oid, model)
    if value_type is not None:
        return ("direct", value_type)

    for constraint in model.constraints:
        if str(constraint.get("type")) != "uniqueness":
            continue
        if constraint.get("scope") != "external":
            continue
        # PANEL-5: the identifying sequence lives in `role_refs`; the research
        # prototype's constraint.get("roles") silently matched nothing.
        role_refs = constraint.get("role_refs") or []
        if not role_refs or not _anchors_on(role_refs, oid, model):
            continue
        resolved: list[dict[str, Any]] = []
        for role_ref in role_refs:
            counterpart = _referenced_object_type(role_ref, model)
            if counterpart is None:
                return (
                    "unmatchable",
                    (
                        f"an external uniqueness constraint anchors on {oid!r} "
                        f"but names an unresolvable role "
                        f"({role_ref.get('fact_type')!r}, "
                        f"{role_ref.get('role')!r})"
                    ),
                )
            kind, payload = reference_identity(counterpart, model, _seen=seen)
            if kind == "unmatchable":
                return (
                    "unmatchable",
                    (
                        f"an external uniqueness constraint anchors on {oid!r} "
                        f"but its referenced role "
                        f"({role_ref.get('fact_type')!r}, "
                        f"{role_ref.get('role')!r}) is played by "
                        f"{counterpart!r}, which itself has no printable "
                        f"reference value: {payload}"
                    ),
                )
            if kind != "direct":
                return (
                    "unmatchable",
                    (
                        f"an external uniqueness constraint anchors on {oid!r} "
                        f"but its referenced role "
                        f"({role_ref.get('fact_type')!r}, "
                        f"{role_ref.get('role')!r}) is played by "
                        f"{counterpart!r}, whose identity is itself composite; "
                        f"nested composite joins are not supported by every "
                        f"applicable-set consumer"
                    ),
                )
            entry: dict[str, Any] = {
                "fact_type": str(role_ref.get("fact_type")),
                "role": str(role_ref.get("role")),
                "object_type": counterpart,
                "path": kind,
            }
            entry["value_type"] = payload
            resolved.append(entry)
        return ("composite", resolved)

    return ("unmatchable", _unmatchable_reason(oid, model))


def applicable_set(model: Any) -> dict[str, Any]:
    """The per-model applicable set as the first-class artifact dict.

    ``object_types``: one row per object type — ``id``, ``path``, and the
    per-path payload (``value_type`` | resolved ``role_refs`` | ``reason``).
    ``fact_types``: one row per fact type — ``id``, ``applicable``, and a
    ``reason`` that is null-when-applicable. A fact type is applicable iff
    EVERY role's object type resolves via direct or composite; the reason for
    an inapplicable row names each offending role and its mechanism, so a
    reader sees "unmeasurable because X", never a silently absent row.
    Rows are sorted by id so the emitted JSON is byte-reproducible.
    """
    dispositions: dict[str, tuple[str, Any]] = {}
    object_rows: list[dict[str, Any]] = []
    for object_type in sorted(
        model.object_types, key=lambda entry: str(entry.get("id"))
    ):
        oid = str(object_type.get("id"))
        kind, payload = reference_identity(oid, model)
        dispositions[oid] = (kind, payload)
        row: dict[str, Any] = {"id": oid, "path": kind}
        if kind == "direct":
            row["value_type"] = payload
        elif kind == "composite":
            row["role_refs"] = payload
        else:
            row["reason"] = payload
        object_rows.append(row)

    scope = fact_type_scope(model)
    fact_rows: list[dict[str, Any]] = []
    for fact_type in sorted(model.fact_types, key=lambda entry: str(entry.get("id"))):
        fact_type_id = str(fact_type.get("id"))
        if scope[fact_type_id] is not None:
            fact_rows.append(
                {
                    "id": fact_type_id,
                    "applicable": False,
                    "reason": scope[fact_type_id],
                }
            )
            continue
        offending: list[str] = []
        for role in fact_type.get("roles") or []:
            oid = str(role.get("object_type"))
            kind, payload = dispositions.get(
                oid, ("unmatchable", f"role names undeclared object type {oid!r}")
            )
            if kind == "unmatchable":
                offending.append(
                    f"role {str(role.get('role_name'))!r} is played by object "
                    f"type {oid!r}, which is unmatchable: {payload}"
                )
        fact_rows.append(
            {
                "id": fact_type_id,
                "applicable": not offending,
                "reason": "; ".join(offending) if offending else None,
            }
        )

    return {"object_types": object_rows, "fact_types": fact_rows}
