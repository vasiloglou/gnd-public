"""The duplicate-shape report of ``gnd evolve preview --shape-report`` (MG3).

For every role-player signature (``gnd.refscheme.role_player_signature``) that
a fact type the proposal adds has, the report holds one group: the added fact
types with that signature and the fact types of the current model with it.
Each added fact type's candidates are the other members of its group. It is advice: nothing reads it to decide an exit, ``breaking`` or the
blast radius (MG-R4). Whether two readings mean the same thing stays the
caller's call. The normative rule lives in the evolution contract's "Shape
report" section.

Model reads go through ``ModelIndex`` only, so the RF6 query policy gains no
row (MG2-Q4).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.refscheme import entity_reference, fact_type_signatures

from .models import (
    ElementLocator,
    EvolutionOperationKind,
    EvolutionProposal,
    ShapeAdded,
    ShapeGroup,
    ShapeMember,
    ShapeReference,
)


def _added_fact_types(proposal: EvolutionProposal, candidate: dict[str, Any]) -> list[tuple[int, str]]:
    """The fact-type ADDs whose id the candidate holds, in operation order.

    An id the same proposal adds and then deletes or renames is not in the
    candidate, so it has no shape to report (review R-F2)."""
    last: dict[str, int] = {}
    for position, operation in enumerate(proposal.operations):
        if (
            operation.kind is EvolutionOperationKind.ADD
            and isinstance(operation.locator, ElementLocator)
            and operation.locator.collection == "fact_types"
            and operation.locator.element_id in candidate
        ):
            # The last ADD of an id is the one whose shape the candidate
            # holds (close review R1-F2).
            last[operation.locator.element_id] = position
    return sorted((position, fact_type_id) for fact_type_id, position in last.items())


def _readings(index: ModelIndex, fact_type_id: str) -> dict[str, Any]:
    fact_type = index.fact_type(fact_type_id) or {}
    inverse = fact_type.get("inverse_reading")
    return {
        "fact_type": fact_type_id,
        "reading": str(fact_type.get("reading")),
        "inverse_reading": inverse if isinstance(inverse, str) else None,
    }


def _references(index: ModelIndex, model: Model, signature: tuple[str, ...]) -> tuple[ShapeReference, ...]:
    references = []
    for object_type_id in sorted(set(signature)):
        object_type = index.object_type(object_type_id) or {}
        if object_type.get("kind") != "entity":
            continue
        identity, value_type = entity_reference(object_type_id, model)
        references.append(
            ShapeReference(object_type=object_type_id, identity=identity, value_type=value_type)
        )
    return tuple(references)


def shape_matches(
    before: Model,
    candidate: Model,
    proposal: EvolutionProposal,
    *,
    bucket_factory: Callable[[], dict[Any, Any]] = dict,
) -> tuple[ShapeGroup, ...]:
    """One group per signature that an added fact type has (spec r2).

    A fact type of the current model is judged in its candidate shape when the
    candidate still holds it under that id and the proposal does not re-add
    it (review R-F3), and in its current shape otherwise, so a deleted fact
    type still meets its replacement (D3, review R-F5). Every fact type costs
    one ``setdefault`` probe of the bucket index, and the output holds each
    fact type at most once, so both are linear (review R-F1).
    """

    before_index = ModelIndex.for_model(before)
    candidate_index = ModelIndex.for_model(candidate)
    candidate_signatures = fact_type_signatures(candidate_index)
    added = _added_fact_types(proposal, candidate_signatures)
    if not added:
        return ()
    added_ids = {fact_type_id for _position, fact_type_id in added}
    buckets = bucket_factory()
    for fact_type_id, signature in fact_type_signatures(before_index).items():
        if fact_type_id in candidate_signatures and fact_type_id not in added_ids:
            signature, index = candidate_signatures[fact_type_id], candidate_index
        else:
            index = before_index
        buckets.setdefault(signature, ([], []))[1].append((fact_type_id, index))
    groups: list[tuple[tuple[str, ...], tuple[list[Any], list[Any]]]] = []
    for position, fact_type_id in added:
        signature = candidate_signatures[fact_type_id]
        bucket = buckets.setdefault(signature, ([], []))
        if not bucket[0]:
            groups.append((signature, bucket))
        bucket[0].append((position, fact_type_id))
    return tuple(
        ShapeGroup(
            signature=signature,
            references=_references(candidate_index, candidate, signature),
            added=tuple(
                ShapeAdded(operation_index=position, **_readings(candidate_index, fact_type_id))
                for position, fact_type_id in members
            ),
            existing=tuple(
                ShapeMember(**_readings(index, fact_type_id))
                for fact_type_id, index in sorted(existing, key=lambda item: item[0])
            ),
        )
        for signature, (members, existing) in groups
    )


__all__ = ["shape_matches"]
