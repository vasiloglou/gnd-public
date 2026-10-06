"""Shared strict reference traversal with compatibility entry points."""
from __future__ import annotations

from collections.abc import Callable
from typing import Any, Literal


def _resolved_primitive(
    object_type_id: str,
    object_types: dict[str, dict[str, Any]],
    seen: set[str] | None = None,
) -> str | None:
    """Compatibility entry for the consolidated strict reference walk."""
    return _resolve_reference(
        str(object_type_id), object_types,
        None,
        set() if seen is None else seen, _identifying_primitive,
    )


def _supertype_parents(doc: dict[str, Any]) -> dict[str, list[str]]:
    """object-type id -> declared direct supertypes (``subtype_of``)."""
    return {
        str(ot.get("id")): [str(s) for s in ot.get("subtype_of") or []]
        for ot in doc.get("object_types") or []
        # `isinstance` BEFORE `.get`: a non-mapping entry is layer 1's finding,
        # and this helper raising would deny every layer-2 rule the chance to
        # report its own. Surfaced by v5.0 Phase 1's hostile-shape sweep.
        if isinstance(ot, dict) and ot.get("id") is not None
    }


def _identifying_primitive(_object_type_id: str, object_type: dict[str, Any]) -> str | None:
    """Extractor: the primitive an identifying value type carries."""
    # The meta-schema guarantees `primitive` is present when kind is value
    # (`$defs/object_type.allOf[1]`).
    primitive = object_type.get("primitive")
    return str(primitive) if primitive is not None else None


def _identifying_id(object_type_id: str, _object_type: dict[str, Any]) -> str | None:
    """Extractor: the id of the identifying value type itself."""
    return str(object_type_id)


def _resolve_reference(
    object_type_id: str,
    by_id: dict[str, dict[str, Any]],
    parents: dict[str, list[str]] | None,
    seen: set[str],
    extract: Callable[[str, dict[str, Any]], str | None],
) -> str | None:
    """Walk an object type to the value type that IDENTIFIES its instances.

    One walk, two extractions (the ``_instance_values_of`` /``_instances_of``
    posture applied to reference resolution). ``extract`` is applied to the value
    type the walk lands on: :func:`_identifying_primitive` yields the primitive
    for layer-2 type checking, :func:`_identifying_id` yields the value type's own
    id for the checker's universe walk. Both answers therefore come from ONE
    notion of "which value type denotes this entity" — the F-01 fix would
    otherwise have been a second, drift-prone copy of this traversal.

    The disjunction at the ``inherits_reference`` branch is over the EXTRACTED
    value, not over the id, which is what preserves the pre-existing primitive
    semantics exactly: two supertypes identified by two distinct value types that
    share one primitive still resolve that primitive, while the id extraction
    correctly declines to pick one of the two.
    """
    if object_type_id in seen:
        # A subtype cycle is NOT rejected by model validation today — a model
        # with `a subtype_of [b]` and `b subtype_of [a]` validates at exit 0 —
        # so the walk cannot assume acyclicity (T-01.1-07).
        return None
    seen.add(object_type_id)

    object_type = by_id.get(object_type_id)
    if object_type is None:
        return None

    if object_type.get("kind") == "value":
        return extract(object_type_id, object_type)

    reference = object_type.get("reference") or {}
    value_type = reference.get("value_type")
    if reference.get("mode") in ("popular", "general") and value_type is not None:
        # `semantic:reference-value-type` (model.py) guarantees this names a
        # value-kind object type, which in turn carries a `primitive`.
        target = by_id.get(str(value_type))
        if target is None:
            return None
        return extract(str(value_type), target)

    direct_parents = (parents.get(object_type_id) if parents is not None
                      else [str(parent) for parent in object_type.get("subtype_of") or []])
    if direct_parents and object_type.get("inherits_reference") is True:
        # Only when the subtype declares that it INHERITS its supertype's
        # identification scheme. `inherits_reference: false` with no reference of
        # its own is unresolvable, and reading through anyway would be a guess.
        resolved = {
            _resolve_reference(parent, by_id, parents, seen, extract)
            for parent in direct_parents
        }
        resolved.discard(None)
        return next(iter(resolved)) if len(resolved) == 1 else None

    return None


def primitive_for(
    object_type_id: str,
    object_types: dict[str, dict[str, Any]],
    *,
    variant: Literal["truthy", "strict"],
    seen: set[str] | None = None,
) -> str | None:
    """Retain both predecessor variant names under the approved strict policy."""
    if variant in ("truthy", "strict"):
        return _resolved_primitive(object_type_id, object_types, seen)
    raise ValueError(f"unknown primitive resolver variant: {variant!r}")

