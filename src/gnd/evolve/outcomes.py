"""GO2 (#227): an outcome for every operation of a proposal.

One walk maps each refusal a preview's gates produce (a validation issue, a
D-12 refusal, an additive-policy issue) to the operation that caused it, then
drops with it every later operation that depends on an element it adds. The
verdict words and the outcome report are defined in the evolution contract's
preview section; ``OperationOutcome`` and ``EvolutionOutcomeReport`` in
``models`` are their one schema.
"""

from __future__ import annotations

import functools
import re
from collections.abc import Iterable, Mapping, Sequence
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
#: is read only for a ``.constraints[<index>]`` or ``.roles[<index>]`` step.
_PATH_HEAD = re.compile(r"\$\.([a-z_]+)\[(?:(\d+)|id=([^\]]+))\]")
_CONSTRAINT_STEP = re.compile(r"\.constraints\[(\d+)\]")
#: A role step names its role by position or by ``role_name``, which the
#: meta-schema's identifier grammar (``^[a-z][a-z0-9_]*$``) keeps apart from a position.
_ROLE_STEP = re.compile(r"\.roles\[(?:(\d+)|([a-z][a-z0-9_]*))\]")

Refusals = dict[int, tuple[str, str]]


class _Index:
    """Which operation touches which element, built once per proposal.

    ``body`` holds the operations that change an element's own entry (the
    element and role operations); a constraint operation is located only
    through its constraint. ``constraints`` holds every constraint an operation
    writes: a constraint operation's ``after`` and each constraint embedded in
    an added or modified fact type's ``after``."""

    def __init__(self, operations: Sequence[EvolutionOperation]) -> None:
        self.operations = operations
        self.body: dict[tuple[str, str], list[int]] = {}
        self.roles: dict[tuple[str, str], list[int]] = {}
        self.constraints: dict[tuple[str | None, str], list[int]] = {}
        for index, operation in enumerate(operations):
            locator = operation.locator
            after = operation.after
            if isinstance(locator, ElementLocator):
                self.body.setdefault((locator.collection, locator.element_id), []).append(index)
                if locator.collection == "fact_types" and isinstance(after, Mapping):
                    for constraint in _entries(after.get("constraints")):
                        self._constraint(locator.element_id, constraint, index)
            elif isinstance(locator, RoleLocator):
                self.body.setdefault(("fact_types", locator.fact_type_id), []).append(index)
                self.roles.setdefault((locator.fact_type_id, locator.role_name), []).append(index)
                renamed = after.get("role_name") if isinstance(after, Mapping) else None
                if isinstance(renamed, str) and renamed != locator.role_name:
                    self.roles.setdefault((locator.fact_type_id, renamed), []).append(index)
            elif isinstance(locator, ConstraintLocator) and after is not None:
                self._constraint(None if locator.host == "model" else locator.host_id, after, index)

    def _constraint(self, host: str | None, constraint: Any, index: int) -> None:
        try:
            digest = canonical_sha256(constraint)
        except Exception:  # noqa: BLE001 -- a value canonical JSON cannot spell is unlocatable
            return
        found = self.constraints.setdefault((host, digest), [])
        if not found or found[-1] != index:  # indices arrive in order: one check, not a scan
            found.append(index)

    def for_element(self, collection: str, element_id: Any, role_name: Any = None) -> int | None:
        """The one operation that changed this element; with a role step, the one
        that changed that role. Two candidates and nothing to tell them apart
        locate nothing: an issue is never pinned on a guess."""
        if not isinstance(element_id, str):
            return None
        candidates = self.body.get((collection, element_id), [])
        if len(candidates) == 1:
            return candidates[0]
        if isinstance(role_name, str):
            roles = self.roles.get((element_id, role_name), [])
            if len(roles) == 1:
                return roles[0]
        return None

    def for_constraint(self, host: Any, constraint: Any) -> int | None:
        try:
            digest = canonical_sha256(constraint)
        except Exception:  # noqa: BLE001 -- a value canonical JSON cannot spell is unlocatable
            return None
        found = self.constraints.get((host if isinstance(host, str) else None, digest), [])
        return found[0] if len(found) == 1 else None


def _entries(value: Any) -> list[Any]:
    """A sequence's items; nothing for every other shape (``after`` values are
    arbitrary JSON, frozen on the operation as tuples)."""
    return list(value) if isinstance(value, (list, tuple)) else []


class _Candidate:
    """The candidate document's top-level entries, with each collection's id
    map built once (a path may address an entry by ``[id=...]``)."""

    def __init__(self, candidate: Any) -> None:
        self.candidate = candidate if isinstance(candidate, dict) else {}
        self.ids: dict[str, dict[Any, Any]] = {}

    def entry(self, collection: str, position: str | None, element_id: str | None) -> Any:
        entries = self.candidate.get(collection)
        if not isinstance(entries, list):
            return None
        if position is not None:
            return entries[int(position)] if int(position) < len(entries) else None
        if collection not in self.ids:
            ids: dict[Any, Any] = {}
            for entry in entries:
                if isinstance(entry, dict) and isinstance(entry.get("id"), str):
                    ids.setdefault(entry["id"], entry)
            self.ids[collection] = ids
        return self.ids[collection].get(element_id)


def locate_validation_issues(
    issues: Iterable[Any], candidate: Any, operations: Sequence[EvolutionOperation]
) -> tuple[Refusals, bool]:
    """The operation each validation issue names, and whether every issue was located.

    ``candidate`` is the parsed candidate document (or ``None`` when it does
    not parse). An issue is located through the element its path names: the
    operation that adds or modifies that element, or, for a constraint step,
    the operation whose ``after`` is that constraint."""
    index = _Index(operations)
    document = _Candidate(candidate)
    refused: Refusals = {}
    complete = True
    for issue in issues:
        found = _locate_path(str(getattr(issue, "path", "")), document, index)
        if found is None:
            complete = False
            continue
        detail = f"{getattr(issue, 'rule_id', 'validation')} at {issue.path}"
        refused.setdefault(found, ("refused-by-validation", detail[:512]))
    return refused, complete


#: The collections an ``ElementLocator`` addresses.
_ELEMENT_COLLECTIONS = frozenset(ElementLocator.model_fields["collection"].annotation.__args__)


def _locate_path(path: str, document: _Candidate, index: _Index) -> int | None:
    head = _PATH_HEAD.match(path)
    if head is None:
        return None
    collection, position, element_id = head.group(1), head.group(2), head.group(3)
    element = document.entry(collection, position, element_id)
    if element_id is None and isinstance(element, dict):
        element_id = element.get("id")
    if collection == "constraints" and isinstance(element, dict):
        return index.for_constraint(None, element)
    role_name = None
    if collection == "fact_types" and isinstance(element, dict):
        step = _CONSTRAINT_STEP.match(path, head.end())
        if step is not None:
            # A constraint's issue is the constraint's: it is never pinned on
            # an operation that changed only the host around it.
            constraints = element.get("constraints")
            if isinstance(constraints, list) and int(step.group(1)) < len(constraints):
                return index.for_constraint(element_id, constraints[int(step.group(1))])
            return None
        role = _ROLE_STEP.match(path, head.end())
        if role is not None:
            position, role_name = role.group(1), role.group(2)
            roles = element.get("roles")
            if position is not None and isinstance(roles, list) and int(position) < len(roles):
                entry = roles[int(position)]
                role_name = entry.get("role_name") if isinstance(entry, dict) else None
    if collection in _ELEMENT_COLLECTIONS:
        return index.for_element(collection, element_id, role_name)
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


#: The meta-schema properties whose value names a model element (a string or
#: a list of strings). They are read only where the meta-schema declares them,
#: so a sample row or a provenance entry, free-form there, is never read.
_REFERENCE_PROPERTIES = {
    "object_type": "object_types", "value_type": "object_types", "supertype": "object_types",
    "subtype_of": "object_types", "subtypes": "object_types", "objectified_as": "object_types",
    "fact_type": "fact_types", "depends_on": "fact_types",
}
#: The meta-schema node an operation's ``after`` value is, by its locator.
_AFTER_SCHEMA = {
    "object_types": "object_type", "fact_types": "fact_type", "operations": "operation",
    "role": "role", "model": "top_level_constraint", "hosted": "inline_constraint",
}


@functools.cache
def _schema() -> _Schema:
    from gnd.model import _load_meta_schema

    return _Schema(_load_meta_schema())


class _Schema:
    """The meta-schema's property and item nodes, every ``$ref``, ``allOf``,
    ``anyOf`` and ``oneOf`` arm merged, computed once per node."""

    def __init__(self, document: dict[str, Any]) -> None:
        self.definitions = document.get("$defs", {})
        self._properties: dict[int, dict[str, list[Any]]] = {}
        self._items: dict[int, list[Any]] = {}

    def node(self, name: str) -> Any:
        return self.definitions.get(name, {})

    def _arms(self, node: Any) -> list[Any]:
        arms, stack, seen = [], [node], set()
        while stack:
            current = stack.pop()
            if not isinstance(current, dict) or id(current) in seen:
                continue
            seen.add(id(current))
            arms.append(current)
            reference = current.get("$ref")
            if isinstance(reference, str) and reference.startswith("#/$defs/"):
                stack.append(self.definitions.get(reference.removeprefix("#/$defs/")))
            for key in ("allOf", "anyOf", "oneOf"):
                stack.extend(current.get(key) or ())
        return arms

    def properties(self, node: Any) -> dict[str, list[Any]]:
        if id(node) not in self._properties:
            merged: dict[str, list[Any]] = {}
            for arm in self._arms(node):
                for key, value in (arm.get("properties") or {}).items():
                    merged.setdefault(key, []).append(value)
            self._properties[id(node)] = merged
        return self._properties[id(node)]

    def items(self, node: Any) -> list[Any]:
        if id(node) not in self._items:
            self._items[id(node)] = [arm["items"] for arm in self._arms(node) if isinstance(arm.get("items"), dict)]
        return self._items[id(node)]


def _needs(operation: EvolutionOperation) -> list[tuple[str, str]]:
    """Every element this operation needs (GO2-D5: from its locator and its
    ``after`` value, never the candidate). The ``after`` value is walked
    beside its meta-schema node; total over arbitrary JSON."""
    locator = operation.locator
    needed: list[tuple[str, str]] = []
    if isinstance(locator, ConstraintLocator) and locator.host != "model" and locator.host_id:
        needed.append(("fact_types", locator.host_id))
    if isinstance(locator, RoleLocator):
        needed.append(("fact_types", locator.fact_type_id))
    if isinstance(locator, ElementLocator):
        root = _AFTER_SCHEMA.get(locator.collection)
    elif isinstance(locator, RoleLocator):
        root = _AFTER_SCHEMA["role"]
    elif isinstance(locator, ConstraintLocator):
        root = _AFTER_SCHEMA["model" if locator.host == "model" else "hosted"]
    else:
        root = None
    schema = _schema()
    stack = [] if root is None else [(operation.after, schema.node(root))]
    while stack:
        value, node = stack.pop()
        if isinstance(value, (list, tuple)):
            stack.extend((item, child) for item in reversed(value) for child in schema.items(node))
            continue
        if not isinstance(value, Mapping):
            continue
        declared = schema.properties(node)
        for key, item in value.items():
            children = declared.get(key)
            if not children:
                continue
            collection = _REFERENCE_PROPERTIES.get(key)
            if collection is not None and isinstance(item, str):
                needed.append((collection, item))
            elif collection is not None and isinstance(item, (list, tuple)):
                needed.extend((collection, name) for name in item if isinstance(name, str))
            if isinstance(item, (Mapping, list, tuple)):
                stack.extend((item, child) for child in children)
    added = _added_element(operation)
    return [key for key in needed if key != added]


def outcomes(
    operations: Sequence[EvolutionOperation],
    refused: Refusals,
    *,
    gates_not_run: Sequence[str] = (),
) -> tuple[OperationOutcome, ...]:
    """One row per operation, in order: its refusal, ``dropped-with`` when it
    needs an element a refused or dropped operation adds (wherever in the
    proposal that operation stands), otherwise ``admitted`` when every gate
    ran over it, or ``unassessed`` naming the gates that did not."""
    adders: dict[tuple[str, str], list[int]] = {}
    for index, operation in enumerate(operations):
        added = _added_element(operation)
        if added is not None:
            adders.setdefault(added, []).append(index)
    dependents: dict[tuple[str, str], list[int]] = {}
    for index, operation in enumerate(operations):
        if index in refused:
            continue
        for key in dict.fromkeys(_needs(operation)):
            if key in adders:
                dependents.setdefault(key, []).append(index)
    verdicts: dict[int, tuple[str, str]] = dict(refused)
    queue = [_added_element(operations[index]) for index in sorted(refused) if index < len(operations)]
    seen: set[tuple[str, str]] = set()
    while queue:
        key = queue.pop(0)
        if key is None or key in seen:
            continue
        seen.add(key)
        for index in dependents.get(key, ()):
            if index not in verdicts:
                verdicts[index] = ("dropped-with", f"{key[0]}[{key[1]}] is refused")
                queue.append(_added_element(operations[index]))
    gates = tuple(sorted(set(gates_not_run), key=OUTCOME_GATES.index))
    rows = []
    for index, operation in enumerate(operations):
        verdict, detail = verdicts.get(index, (None, ""))
        if verdict is not None:
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
