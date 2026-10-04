from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class NodeObservation:
    nodeid: str
    lane: str
    outcome: str
    exception_type: str | None
    duration_bucket: str

@dataclass(frozen=True)
class NodeDelta:
    nodeid: str
    field: str
    before: object
    after: object

def compare_nodes(before: Mapping[str, NodeObservation], after: Mapping[str, NodeObservation]) -> tuple[NodeDelta, ...]:
    differences: list[NodeDelta] = []
    for nodeid in sorted(before.keys() | after.keys()):
        old = before.get(nodeid)
        new = after.get(nodeid)
        if old is None or new is None:
            differences.append(NodeDelta(nodeid, 'nodeid', old, new))
            continue
        for field in ('lane', 'outcome', 'exception_type', 'duration_bucket'):
            old_value, new_value = (getattr(old, field), getattr(new, field))
            if old_value != new_value:
                differences.append(NodeDelta(nodeid, field, old_value, new_value))
    return tuple(differences)
