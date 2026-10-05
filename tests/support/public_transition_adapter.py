"""Immutable admitted-value bridge for Phase 4 transition evidence.

The bridge performs no file I/O and computes no transition verdict.  It freezes
every model, population, and step dimension read by production into canonical,
immutable values so the proof relation and the runtime observation can name the
same input without sharing an evaluator.
"""

from __future__ import annotations

import datetime
import json
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from gnd.model import Model
from gnd.population import Population


def _plain(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _plain(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_plain(item) for item in value]
    if isinstance(value, (datetime.date, datetime.datetime, datetime.time)):
        return value.isoformat()
    return value


def _canonical(value: Any) -> str:
    return json.dumps(
        _plain(value), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    )


def _type_closure(model: Model) -> tuple[tuple[str, tuple[str, ...]], ...]:
    parents = {
        str(row.get("id")): tuple(str(parent) for parent in row.get("subtype_of") or [])
        for row in model.object_types
    }

    def ancestors(identifier: str) -> tuple[str, ...]:
        seen = {identifier}
        pending = list(parents.get(identifier, ()))
        while pending:
            current = pending.pop(0)
            if current in seen:
                continue
            seen.add(current)
            pending.extend(parents.get(current, ()))
        return tuple(sorted(seen))

    return tuple((identifier, ancestors(identifier)) for identifier in sorted(parents))


@dataclass(frozen=True)
class SnapshotIR:
    """One population as canonical immutable values."""

    covers: tuple[str, ...]
    facts_json: str
    instances_json: str


@dataclass(frozen=True)
class OperationIR:
    """Every operation dimension production reads, kept separately."""

    identifier: str
    parameters_json: str
    preconditions_json: str
    effects_json: str
    dynamic_rules_json: str
    frame_modality: str


@dataclass(frozen=True)
class StepIR:
    index: int
    operation: str
    bindings_json: str


@dataclass(frozen=True)
class TransitionIR:
    """The complete admitted-value coordinate for one transition walk."""

    object_types_json: str
    object_type_closure: tuple[tuple[str, tuple[str, ...]], ...]
    fact_types_json: str
    constraints_json: str
    operations: tuple[OperationIR, ...]
    pre: SnapshotIR
    post: SnapshotIR
    steps: tuple[StepIR, ...]


def _snapshot(population: Population) -> SnapshotIR:
    return SnapshotIR(
        covers=tuple(str(item) for item in population.covers or []),
        facts_json=_canonical(population.facts or {}),
        instances_json=_canonical(population.instances or {}),
    )


def freeze_transition(
    model: Model,
    pre: Population,
    post: Population,
    steps: list[dict[str, Any]],
) -> TransitionIR:
    """Freeze one already-admitted walk without evaluating it."""

    operations = tuple(
        OperationIR(
            identifier=str(operation.get("id")),
            parameters_json=_canonical(operation.get("parameters") or []),
            preconditions_json=_canonical(operation.get("preconditions") or []),
            effects_json=_canonical(operation.get("effects") or []),
            dynamic_rules_json=_canonical(operation.get("dynamic_rules") or []),
            frame_modality=str((operation.get("frame") or {}).get("modality", "")),
        )
        for operation in model.operations
    )
    return TransitionIR(
        object_types_json=_canonical(model.object_types),
        object_type_closure=_type_closure(model),
        fact_types_json=_canonical(model.fact_types),
        constraints_json=_canonical(model.constraints),
        operations=operations,
        pre=_snapshot(pre),
        post=_snapshot(post),
        steps=tuple(
            StepIR(
                index=index,
                operation=str(step["op"]),
                bindings_json=_canonical(step["bindings"]),
            )
            for index, step in enumerate(steps, start=1)
        ),
    )
