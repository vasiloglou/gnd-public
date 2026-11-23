"""GO2 (#227): an outcome for every operation of a proposal.

One walk maps each refusal a preview's gates produce (a validation issue, a
D-12 refusal, an additive-policy issue) to the operation that caused it, then
drops with it every later operation that depends on an element it adds. The
verdict words and the outcome report are defined in the evolution contract's
preview section; ``OperationOutcome`` and ``EvolutionOutcomeReport`` in
``models`` are their one schema.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from typing import Any

from .models import (
    OUTCOME_GATES,
    ConstraintLocator,
    ElementLocator,
    EvolutionOperation,
    EvolutionOperationKind,
    OperationOutcome,
    RoleLocator,
    canonical_sha256,
)

#: The validator's issue path: ``$.<collection>[<index>]`` or
#: ``$.<collection>[id=<id>]``, then the rest of the path. This is the whole
#: grammar of the head the validators write (`ValidationIssue.path`); the rest
#: is read only for a ``.constraints[<index>]`` step.
_PATH_HEAD = re.compile(r"\$\.([a-z_]+)\[(?:(\d+)|id=([^\]]+))\]")
_CONSTRAINT_STEP = re.compile(r"\.constraints\[(\d+)\]")

Refusals = dict[int, tuple[str, str]]


class _Index:
    """Which operation touches which element, built once per proposal."""

    def __init__(self, operations: Sequence[EvolutionOperation]) -> None:
        self.operations = operations
        self.element: dict[tuple[str, str], int] = {}
        self.touching: dict[tuple[str, str], list[int]] = {}
        self.constraints: dict[tuple[str | None, str], list[int]] = {}
        for index, operation in enumerate(operations):
            locator = operation.locator
            if isinstance(locator, ElementLocator):
                key = (locator.collection, locator.element_id)
                self.element.setdefault(key, index)
                self.touching.setdefault(key, []).append(index)
            elif isinstance(locator, RoleLocator):
                self.touching.setdefault(("fact_types", locator.fact_type_id), []).append(index)
            elif isinstance(locator, ConstraintLocator):
                host = None if locator.host == "model" else locator.host_id
                if operation.after is not None:
                    self.constraints.setdefault((host, canonical_sha256(operation.after)), []).append(index)
                if host is not None:
                    self.touching.setdefault(("fact_types", host), []).append(index)

    def for_element(self, collection: str, element_id: Any) -> int | None:
        if not isinstance(element_id, str):
            return None
        key = (collection, element_id)
        if key in self.element:
            return self.element[key]
        touching = self.touching.get(key, [])
        return touching[0] if len(touching) == 1 else None

    def for_constraint(self, host: Any, constraint: Any) -> int | None:
        try:
            digest = canonical_sha256(constraint)
        except Exception:  # noqa: BLE001 -- a value canonical JSON cannot spell is unlocatable
            return None
        found = self.constraints.get((host if isinstance(host, str) else None, digest), [])
        return found[0] if len(found) == 1 else None


def locate_validation_issues(
    issues: Iterable[Any], candidate: Any, operations: Sequence[EvolutionOperation]
) -> tuple[Refusals, bool]:
    """The operation each validation issue names, and whether every issue was located.

    ``candidate`` is the parsed candidate document (or ``None`` when it does
    not parse). An issue is located through the element its path names: the
    operation that adds or modifies that element, or, for a constraint step,
    the operation whose ``after`` is that constraint."""
    index = _Index(operations)
    refused: Refusals = {}
    complete = True
    for issue in issues:
        found = _locate_path(str(getattr(issue, "path", "")), candidate, index)
        if found is None:
            complete = False
            continue
        detail = f"{getattr(issue, 'rule_id', 'validation')} at {issue.path}"
        refused.setdefault(found, ("refused-by-validation", detail[:512]))
    return refused, complete


def _locate_path(path: str, candidate: Any, index: _Index) -> int | None:
    head = _PATH_HEAD.match(path)
    if head is None:
        return None
    collection, position, element_id = head.group(1), head.group(2), head.group(3)
    element = None
    if isinstance(candidate, dict):
        entries = candidate.get(collection)
        if isinstance(entries, list):
            if position is not None and int(position) < len(entries):
                element = entries[int(position)]
            elif element_id is not None:
                element = next((e for e in entries if isinstance(e, dict) and e.get("id") == element_id), None)
    if element_id is None and isinstance(element, dict):
        element_id = element.get("id")
    step = _CONSTRAINT_STEP.match(path, head.end())
    if collection == "constraints" and isinstance(element, dict):
        return index.for_constraint(None, element)
    if step is not None and collection == "fact_types" and isinstance(element, dict):
        constraints = element.get("constraints")
        if isinstance(constraints, list) and int(step.group(1)) < len(constraints):
            found = index.for_constraint(element_id, constraints[int(step.group(1))])
            if found is not None:
                return found
    if collection in ("object_types", "fact_types"):
        return index.for_element(collection, element_id)
    return None


def locate_d12_refusals(
    refusals: Iterable[tuple[Any, Any, str]], operations: Sequence[EvolutionOperation]
) -> tuple[Refusals, bool]:
    """The operation each D-12 refusal ``(host, constraint, message)`` names."""
    index = _Index(operations)
    refused: Refusals = {}
    complete = True
    for host, constraint, message in refusals:
        found = index.for_constraint(host, constraint)
        if found is None:
            complete = False
            continue
        refused.setdefault(found, ("refused-by-d12", message[:512]))
    return refused, complete


def _added_element(operation: EvolutionOperation) -> tuple[str, str] | None:
    locator = operation.locator
    if isinstance(locator, ElementLocator) and operation.kind is EvolutionOperationKind.ADD:
        return locator.collection, locator.element_id
    return None


def _depends_on(operation: EvolutionOperation, gone: set[tuple[str, str]]) -> tuple[str, str] | None:
    """The refused element this operation needs, if any (GO2-D5: from locators
    and ``after`` values, never the candidate)."""
    locator = operation.locator
    needed: list[tuple[str, str]] = []
    if isinstance(locator, ConstraintLocator) and locator.host != "model" and locator.host_id:
        needed.append(("fact_types", locator.host_id))
    if isinstance(locator, RoleLocator):
        needed.append(("fact_types", locator.fact_type_id))
    after = operation.after if isinstance(operation.after, dict) else {}
    for role in after.get("roles") or []:
        if isinstance(role, dict) and isinstance(role.get("object_type"), str):
            needed.append(("object_types", role["object_type"]))
    if isinstance(locator, RoleLocator) and isinstance(after.get("object_type"), str):
        needed.append(("object_types", after["object_type"]))
    for parent in after.get("subtype_of") or []:
        if isinstance(parent, str):
            needed.append(("object_types", parent))
    reference = after.get("reference")
    if isinstance(reference, dict) and isinstance(reference.get("value_type"), str):
        needed.append(("object_types", reference["value_type"]))
    return next((key for key in needed if key in gone), None)


def outcomes(
    operations: Sequence[EvolutionOperation],
    refused: Refusals,
    *,
    gates_not_run: Sequence[str] = (),
) -> tuple[OperationOutcome, ...]:
    """One row per operation, in order: its refusal, ``dropped-with`` when it
    needs an element a refused operation adds, otherwise ``admitted`` when
    every gate ran over it, or ``unassessed`` naming the gates that did not."""
    gone: set[tuple[str, str]] = set()
    rows = []
    gates = tuple(sorted(set(gates_not_run), key=OUTCOME_GATES.index))
    for index, operation in enumerate(operations):
        verdict, detail = refused.get(index, (None, ""))
        if verdict is None:
            needed = _depends_on(operation, gone)
            if needed is not None:
                verdict, detail = "dropped-with", f"{needed[0]}[{needed[1]}] is refused"
        if verdict is not None:
            added = _added_element(operation)
            if added is not None:
                gone.add(added)
            rows.append(OperationOutcome(
                operation_index=index, operation_id=operation.operation_id,
                reference=operation.locator.reference(), verdict=verdict, detail=detail))
            continue
        rows.append(OperationOutcome(
            operation_index=index, operation_id=operation.operation_id,
            reference=operation.locator.reference(),
            verdict="unassessed" if gates else "admitted", gates_not_run=gates))
    return tuple(rows)


def gates_after(gate: str, *, policy: bool, ran: Iterable[str] = ()) -> tuple[str, ...]:
    """The gates the preview runs after ``gate`` (the policy only when one was
    requested), less those the outcome pass ran itself."""
    later = OUTCOME_GATES[OUTCOME_GATES.index(gate) + 1:]
    done = set(ran)
    return tuple(g for g in later if g not in done and (policy or g != "policy"))
