"""The additive policy for ``gnd evolve preview --policy additive`` (MG2).

One walk over a proposal's operations decides, per (locator kind, operation
kind) matrix cell, whether the operation keeps every fact already admitted
under the before-model interpretable. The matrix and the strengthening list
are normative in the packaged evolution contract
(``skills/gnd-model-evolve/references/evolution-contract.md``); this module
is their one implementation, shared by preview and apply (MG-R2, MG-R3).

The walk reads the before-model through ``ModelIndex`` and the proposal's
own ``before``/``after`` dicts, which the service has already checked equal to
the actual elements. It is total over any dict pair: a shape it does not
recognise is a ``neither`` verdict, never a traceback.
"""

from __future__ import annotations

from collections.abc import Iterable
from typing import Any, Final

from gnd.documents import Model
from gnd.model_index import ModelIndex

from .models import (
    EvolutionOperationKind,
    EvolutionProposal,
    PolicyIssue,
)

POLICY_ADDITIVE: Final = "additive"

__all__ = [
    "POLICY_ADDITIVE",
    "additive_policy_issues",
    "effective_populated",
]

_ADD = EvolutionOperationKind.ADD
_MODIFY = EvolutionOperationKind.MODIFY

#: Element MODIFY is an allow-list: the whole element is replaced by the
#: operation, so only a diff confined to these dotted paths is admitted.
_OBJECT_TYPE_MODIFY_KEYS = frozenset({"description", "provenance.rationale"})
_FACT_TYPE_MODIFY_KEYS = frozenset({"provenance.rationale"})

_STRENGTHENING = "strengthening"
_WEAKENING = "weakening"
_NEITHER = "neither"
_ADMITTED = "admitted"


class _PopulatedArgumentError(ValueError):
    """A ``--populated`` id that names no fact type of the before model."""


def _lookup(mapping: Any, key: str) -> Any:
    return mapping.get(key) if isinstance(mapping, dict) else None


def _fact_type_id_of(reference: str) -> str | None:
    """``fact_types[ID]`` or ``fact_types[ID].…`` -> ``ID``; anything else -> None."""
    prefix = "fact_types["
    if not reference.startswith(prefix):
        return None
    end = reference.find("]", len(prefix))
    if end <= len(prefix):
        return None
    return reference[len(prefix):end]


def effective_populated(
    before: Model,
    proposal: EvolutionProposal,
    *,
    populated_args: Iterable[str],
) -> frozenset[str]:
    """The fact types the policy treats as populated (plan MG-D4 (a)+(b)).

    Sample rows on the before model, reference-population ownership, a
    ``population`` artifact locator in the proposal, and the caller's
    ``--populated`` ids. An argument naming no fact type of the before model
    raises ``ValueError`` (spec D4); the result is what the preview records as
    ``populated``.
    """

    index = ModelIndex.for_model(before)
    known: set[str] = set()
    populated: set[str] = set()
    for row in index.iter_fact_types_shared():
        identifier = _lookup(row, "id")
        if identifier is None:
            continue
        known.add(str(identifier))
        rows = _lookup(row, "sample_population")
        if isinstance(rows, list) and rows:
            populated.add(str(identifier))
    for entry in before.reference_populations:
        owned = entry.get("fact_types") if isinstance(entry, dict) else None
        for identifier in owned if isinstance(owned, list) else ():
            if str(identifier) in known:
                populated.add(str(identifier))
    for artifact in proposal.artifacts:
        if artifact.artifact_kind != "population":
            continue
        for reference in artifact.references:
            identifier = _fact_type_id_of(reference)
            if identifier is not None and identifier in known:
                populated.add(identifier)
    for argument in populated_args:
        if argument not in known:
            raise _PopulatedArgumentError(
                f"invalid --populated fact type {argument!r}: the current model declares no such fact type"
            )
        populated.add(argument)
    return frozenset(populated)


def _diff(before: Any, after: Any, prefix: str, out: list[tuple[str, Any, Any]]) -> None:
    """Dotted paths at which two values differ.

    Dicts are descended; lists are compared whole, except ``ranges`` lists of
    equal length, which are compared element-wise so a narrowed range is seen
    as a change to ``ranges[i].min`` rather than to the whole list.
    """

    if isinstance(before, dict) and isinstance(after, dict):
        for key in sorted(set(before) | set(after), key=str):
            path = f"{prefix}.{key}" if prefix else str(key)
            _diff(_lookup(before, key), _lookup(after, key), path, out)
        return
    if (
        prefix.rsplit(".", 1)[-1] == "ranges"
        and isinstance(before, (list, tuple))
        and isinstance(after, (list, tuple))
        and len(before) == len(after)
    ):
        for position, (left, right) in enumerate(zip(before, after, strict=True)):
            _diff(left, right, f"{prefix}[{position}]", out)
        return
    if before != after:
        out.append((prefix, before, after))


def diff_paths(before: Any, after: Any) -> list[tuple[str, Any, Any]]:
    out: list[tuple[str, Any, Any]] = []
    _diff(before, after, "", out)
    return out


def _is_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def _ordered(before: Any, after: Any, *, tightens_when_raised: bool) -> str:
    """Classify a numeric bound change.

    A lower bound tightens when raised, an upper bound when lowered; an added
    bound always tightens and a removed one always loosens.
    """

    if before is None and _is_number(after):
        return _STRENGTHENING
    if _is_number(before) and after is None:
        return _WEAKENING
    if _is_number(before) and _is_number(after):
        raised = after > before
        return _STRENGTHENING if raised == tightens_when_raised else _WEAKENING
    return _NEITHER


def _subset(before: Any, after: Any) -> str:
    # The proposal reader freezes operation dicts, so lists arrive as tuples.
    if not (isinstance(before, (list, tuple)) and isinstance(after, (list, tuple))):
        return _NEITHER
    try:
        left, right = set(before), set(after)
    except TypeError:
        return _NEITHER
    if right < left:
        return _STRENGTHENING
    if right > left:
        return _WEAKENING
    return _NEITHER


def _transition(before: Any, after: Any, strengthening: tuple[Any, Any]) -> str:
    if (before, after) == strengthening:
        return _STRENGTHENING
    if (before, after) == (strengthening[1], strengthening[0]):
        return _WEAKENING
    return _NEITHER


def constraint_change(path: str, before: Any, after: Any, *, family: Any = None) -> str:
    """The closed strengthening/weakening list (plan §2.2, MG-D3 (a), (p1) F).

    ``family`` is the constraint's ``type``: only a uniqueness constraint is
    monotone in its role set (more roles, weaker key). A frequency
    constraint's ``roles`` is a projection, and widening it makes finer groups
    that must each reach ``bound.min``, so its change is neither (review F2).
    """

    leaf = path.rsplit(".", 1)[-1]
    parent = path.rsplit(".", 1)[0] if "." in path else ""
    parent_leaf = parent.rsplit(".", 1)[-1].split("[", 1)[0] if parent else ""
    if path in {"rationale", "remedy"}:
        # Author text: why the rule exists, what to do about a violation.
        return _ADMITTED
    if path == "provenance.reviewed_in":
        # The audit key D-12 strips from a reviewed status change
        # (`_without_review`); the change it accompanies is judged by `status`.
        return _ADMITTED
    if path == "roles":
        return _subset(before, after) if family == "uniqueness" else _NEITHER
    if path == "allowed":
        return _subset(before, after)
    if parent_leaf in {"range", "ranges", "bound"}:
        if leaf == "min":
            return _ordered(before, after, tightens_when_raised=True)
        if leaf == "max":
            return _ordered(before, after, tightens_when_raised=False)
        if leaf == "min_inclusive" or leaf == "max_inclusive":
            return _transition(before, after, (True, False))
        return _NEITHER
    if path == "modality":
        return _transition(before, after, ("deontic", "alethic"))
    if path == "status":
        return _transition(before, after, ("proposed", "confirmed"))
    return _NEITHER


def _constraint_modify_detail(before: Any, after: Any) -> str | None:
    """None when the MODIFY is admitted; otherwise the refusing key and verdict."""

    changes = diff_paths(before, after)
    if not changes:
        return None
    family = _lookup(before, "type")
    for path, left, right in changes:
        verdict = constraint_change(path, left, right, family=family)
        if verdict in (_ADMITTED, _WEAKENING):
            continue
        return f"{path} {verdict}"
    return None


def _element_modify_detail(before: Any, after: Any, allowed: frozenset[str]) -> str | None:
    changes = diff_paths(before, after)
    # A path is admitted when it is an allowed key or lies beneath one, so an
    # edited `description.summary` is a description edit.
    refused = sorted(
        path for path, _left, _right in changes
        if not any(path == key or path.startswith(key + ".") for key in allowed)
    )
    if not refused:
        return None
    return "changed outside the admitted keys: " + ", ".join(refused)


def _role_ref_fact_types(value: Any, out: set[str]) -> None:
    """Every string ``fact_type`` value reachable in ``value``.

    Covers a ``role_ref`` (``{fact_type, role}``), a role sequence and a
    guarded rule's atoms (``{fact_type, bind}``) with one family-agnostic walk;
    an id that names no fact type is harmless, since the caller intersects
    with the populated set.
    """

    if isinstance(value, dict):
        fact_type = _lookup(value, "fact_type")
        if isinstance(fact_type, str):
            out.add(fact_type)
        for item in value.values():
            _role_ref_fact_types(item, out)
    elif isinstance(value, (list, tuple)):
        for item in value:
            _role_ref_fact_types(item, out)


def _object_scoped_types(value: Any) -> set[str]:
    """The object types a model-hosted constraint ranges over without a role.

    A `value` or `cardinality` constraint with an `object_type` and no
    `role_ref` constrains every instance of that object type, and a
    `subtype-partition` constrains its `supertype` and `subtypes`. Their
    subjects are then every fact type such an instance plays a role in
    (close review R1-F1); a role-scoped constraint keeps its role refs.
    """

    if not isinstance(value, dict):
        return set()
    named: set[str] = set()
    if _lookup(value, "role_ref") is None and isinstance(_lookup(value, "object_type"), str):
        named.add(_lookup(value, "object_type"))
    if isinstance(_lookup(value, "supertype"), str):
        named.add(_lookup(value, "supertype"))
    subtypes = _lookup(value, "subtypes")
    if isinstance(subtypes, (list, tuple)):
        named.update(item for item in subtypes if isinstance(item, str))
    return named


def additive_policy_issues(
    before: Model,
    proposal: EvolutionProposal,
    *,
    populated: frozenset[str],
) -> tuple[PolicyIssue, ...]:
    """Every operation the additive policy refuses, in proposal order.

    ``before`` is the current model; ``populated`` is ``effective_populated``'s
    result. Operations on the ``operations`` collection are the operations
    gate's (exit 18) and are admitted here. The policy walks the proposal once
    and never reads a population.
    """

    index = ModelIndex.for_model(before)
    existing_fact_types = {
        str(_lookup(row, "id")) for row in index.iter_fact_types_shared() if _lookup(row, "id") is not None
    }
    added_fact_types: set[str] = set()
    issues: list[PolicyIssue] = []
    players: dict[str, set[str]] | None = None

    def playing(object_types: set[str]) -> set[str]:
        """Fact types with a role played by one of `object_types` or a subtype of one."""
        nonlocal players
        if players is None:
            players = {}
            # A value type that identifies an entity constrains that entity's
            # reference values, so the entity's roles count too.
            identifies: dict[str, set[str]] = {}
            for object_type_id, row in index.object_types_by_id().items():
                reference = _lookup(row, "reference")
                value_type = _lookup(reference, "value_type") if isinstance(reference, dict) else None
                if isinstance(value_type, str):
                    identifies.setdefault(object_type_id, set()).add(value_type)
            for fact_type_id, roles in index.role_object_types().items():
                for player in roles.values():
                    kinds = {player, *index.supertype_closure(player)}
                    for kind_of in set(kinds):
                        kinds |= identifies.get(kind_of, set())
                    for kind_of in kinds:
                        players.setdefault(kind_of, set()).add(fact_type_id)
        found: set[str] = set()
        for object_type in object_types:
            found |= players.get(object_type, set())
        return found

    def refuse(position: int, operation: Any, cell: str, detail: str) -> None:
        issues.append(
            PolicyIssue(
                operation_index=position,
                operation_id=operation.operation_id,
                reference=operation.reference(),
                cell=cell,
                detail=f"{operation.reference()}: {detail}",
            )
        )

    for position, operation in enumerate(proposal.operations):
        locator = operation.locator
        kind = operation.kind
        locator_kind = locator.locator_kind
        if locator_kind == "element":
            collection = locator.collection
            if collection == "operations":
                continue
            if kind is _ADD:
                if collection == "fact_types":
                    added_fact_types.add(locator.element_id)
                continue
            if kind is _MODIFY:
                allowed = _OBJECT_TYPE_MODIFY_KEYS if collection == "object_types" else _FACT_TYPE_MODIFY_KEYS
                detail = _element_modify_detail(operation.before, operation.after, allowed)
                if detail is not None:
                    refuse(position, operation, f"{collection}.modify", detail)
                continue
            refuse(position, operation, f"{collection}.{kind.value}", f"{kind.value} refused")
            continue
        if locator_kind == "role":
            if kind is _ADD and locator.fact_type_id in added_fact_types:
                continue
            if kind is _ADD and locator.fact_type_id not in existing_fact_types:
                # Neither existing nor added here: the replay refuses it (3)
                # before the policy; admitted so the policy stays total.
                continue
            refuse(position, operation, f"role.{kind.value}", f"{kind.value} refused on an existing fact type")
            continue
        if locator_kind == "constraint":
            if locator.host == "fact_type":
                subjects = {locator.host_id} if locator.host_id is not None else set()
            else:
                # Before AND after: a constraint spanning only unpopulated fact
                # types must not be re-pointed at a populated one (review F1).
                subjects = set()
                _role_ref_fact_types(operation.before, subjects)
                _role_ref_fact_types(operation.after, subjects)
                subjects |= playing(_object_scoped_types(operation.before) | _object_scoped_types(operation.after))
            # `populated` is computed from the before model, so a same-proposal
            # fact type is never in it; no subtraction is needed (review F5).
            if not (subjects & populated):
                continue
            if kind is _ADD:
                refuse(position, operation, "constraint.populated.add", "new constraint on a populated fact type")
            elif kind is _MODIFY:
                detail = _constraint_modify_detail(operation.before, operation.after)
                if detail is not None:
                    refuse(position, operation, "constraint.populated.modify", detail)
            # DELETE: removing a constraint cannot invalidate an admitted fact.
            continue
        if locator_kind == "model-identity":
            refuse(position, operation, "model_identity.modify", "model identity change refused")
    return tuple(issues)
