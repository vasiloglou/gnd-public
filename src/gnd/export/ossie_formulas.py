"""Place the reviewed subset of requirement and derivation shapes in Ossie scopes."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any

from gnd.export.pyrel_rules import (
    Atom,
    Count,
    ExportInputError,
    Requirement,
    constraint_context,
    constraint_requirements,
    lower_rule_atom,
    normalize_derivation_clauses,
)

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")
_RESERVED = frozenset(
    [
        "AND",
        "AVG",
        "BY",
        "COUNT",
        "EXISTS",
        "FALSE",
        "GROUP",
        "MAX",
        "MIN",
        "NOT",
        "OR",
        "SUM",
        "TRUE",
        "WHERE",
    ]
)
_SAFE_STRING = re.compile(r"[^'\\\r\n\x00-\x1f\x7f]*\Z")
_SUPPORTED = frozenset(
    {"guarded", "subset", "equality", "exclusion", "ring", "value", "cardinality"}
)
_METADATA = frozenset(
    {"id", "modality", "source", "status", "provenance", "rationale", "remedy", "owner", "allowed_fixes"}
)
_FORMULA = ("requires", "formula", None)


class _Unprojected(ValueError):
    """The original rule remains an extension when its shape is outside the corpus."""


@dataclass(frozen=True)
class ProjectedRelation:
    owner: str
    source_roles: tuple[str, ...]
    projected_roles: tuple[str, ...]
    role_types: dict[str, str]
    target: dict[str, Any]

    def arguments(self, atom: Atom) -> tuple[Any, ...]:
        binding = dict(zip(self.source_roles, atom.args, strict=True))
        return tuple(binding[role] for role in self.projected_roles)

    def path(self) -> str:
        return f"{_identifier(self.owner)}.{_identifier(self.target['name'])}"

    def token(self, position: int) -> str:
        return _identifier(self.owner if position == 0 else self.projected_roles[position])


def _identifier(name: str) -> str:
    if not _IDENTIFIER.fullmatch(name) or name in _RESERVED:
        raise _Unprojected
    return name


def _variable(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("$") and len(value) > 1


def _tuple_domain(req: Requirement, relations: dict[str, ProjectedRelation]):
    if len(req.domain) != 1:
        raise _Unprojected
    atom = req.domain[0]
    rel = relations.get(atom.relation)
    if rel is None:
        raise _Unprojected
    args = rel.arguments(atom)
    if not all(map(_variable, args)) or len(set(args)) != len(args):
        raise _Unprojected
    return rel, args


def _comparison(req, relations, strings, integers):
    relation, args = _tuple_domain(req, relations)
    comparison = req.check.compare
    if (
        req.check.kind != "compare"
        or comparison is None
        or len(args) != 2
        or relation.token(0) == relation.token(1)
    ):
        raise _Unprojected
    first, second = (relation.role_types[role] for role in relation.projected_roles)
    if first not in strings:
        raise _Unprojected
    if req.family == "ring":
        if comparison.operator != "!=" or first != second:
            raise _Unprojected
        if {comparison.left, comparison.right} != set(args):
            raise _Unprojected
        return relation.target, f"{relation.token(0)} != {relation.token(1)}"

    if (
        comparison.operator != "<="
        or comparison.left != args[1]
        or type(comparison.right) is not int
        or second not in integers
    ):
        raise _Unprojected
    return relation.target, f"{relation.token(1)} <= {comparison.right}"


def _membership(req, relations, strings):
    left, args = _tuple_domain(req, relations)
    atom = req.check.atom
    right = relations.get(atom.relation) if atom else None
    if (
        right is None
        or len(args) != 1
        or right.arguments(atom) != args
        or left.role_types[left.projected_roles[0]] not in strings
        or left.role_types[left.projected_roles[0]] != right.role_types[right.projected_roles[0]]
    ):
        raise _Unprojected
    expression = right.path()
    if req.check.kind == "absent":
        expression = f"NOT EXISTS({expression})"
    elif req.check.kind != "holds":
        raise _Unprojected
    return left.target, expression


def _value_enum(constraint, req, components, strings):
    object_id = constraint["object_type"]
    concept = components[object_id]
    choices = constraint.get("allowed")
    if (
        constraint.get("role_ref")
        or object_id not in strings
        or req.check.kind != "holds"
        or not choices
        or not all(isinstance(item, str) and _SAFE_STRING.fullmatch(item) for item in choices)
    ):
        raise _Unprojected
    name = _identifier(concept["concept"])
    return concept, " OR ".join(f"{name} == '{item}'" for item in choices)


def _cardinality(constraint, req, ontology, components, strings):
    check = req.check.compare
    if (
        constraint.get("scope") != "object"
        or constraint.get("object_type") not in strings
        or req.check.kind != "compare"
        or check is None
        or check.operator != "<="
        or not isinstance(check.left, Count)
        or type(check.right) is not int
    ):
        raise _Unprojected
    name = _identifier(components[constraint["object_type"]]["concept"])
    return ontology, f"COUNT[{name}] <= {check.right}"


def _placements(constraint, requirements, ontology, components, relations, strings, integers):
    group = [row for row in requirements if not row.listing]
    if not group:
        raise _Unprojected
    family = constraint["type"]
    if family in {"guarded", "ring"}:
        return [_comparison(req, relations, strings, integers) for req in group]
    if family in {"subset", "equality", "exclusion"}:
        return [_membership(req, relations, strings) for req in group]
    if len(group) != 1:
        raise _Unprojected
    if family == "value":
        return [_value_enum(constraint, group[0], components, strings)]
    return [_cardinality(constraint, group[0], ontology, components, strings)]


def _derived_chain(context, fact, relations, strings):
    rule = fact.get("derivation_rule")
    if fact.get("derivation") != "derived" or not isinstance(rule, dict):
        raise _Unprojected
    relation = relations[fact["id"]]
    if len(relation.projected_roles) != 2:
        raise _Unprojected
    clauses = normalize_derivation_clauses(rule)
    if len(clauses) != 1:
        raise _Unprojected
    (clause,) = clauses
    if len(clause["body"]) != 2 or clause["negate"] or clause["where"] or clause["aggregate"]:
        raise _Unprojected
    first, last = [lower_rule_atom(context, item) for item in clause["body"]]
    if any(
        context.facts[atom.relation].get("derivation", "asserted") != "asserted"
        for atom in (first, last)
    ):
        raise _Unprojected
    first_rel, last_rel = relations[first.relation], relations[last.relation]
    first_args, last_args = first_rel.arguments(first), last_rel.arguments(last)
    if len(first_args) != 2 or len(last_args) != 2:
        raise _Unprojected
    x, join = first_args
    other, y = last_args
    head = tuple(clause["head"].get(role) for role in relation.projected_roles)
    if (
        not all(map(_variable, (x, join, y)))
        or len({x, join, y}) != 3
        or join != other
        or head != (x, y)
    ):
        raise _Unprojected
    first_types = tuple(first_rel.role_types[role] for role in first_rel.projected_roles)
    last_types = tuple(last_rel.role_types[role] for role in last_rel.projected_roles)
    head_types = tuple(relation.role_types[role] for role in relation.projected_roles)
    if first_types[1] != last_types[0] or head_types != (first_types[0], last_types[1]):
        raise _Unprojected
    if not all(player in strings for player in (*first_types, *last_types)):
        raise _Unprojected
    return [f"{first_rel.path()}.{_identifier(last_rel.target['name'])}"]


def _supported_shape(constraint, relations):
    family = constraint.get("type")
    if (
        family not in _SUPPORTED
        or constraint.get("modality") != "alethic"
        or constraint.get("status") != "confirmed"
    ):
        return False
    if family == "guarded":
        atoms = constraint["antecedent"]
        comparison = constraint["consequent"].get("comparison")
        return (
            len(atoms) == 1
            and len(relations[atoms[0]["fact_type"]].projected_roles) == 2
            and isinstance(comparison, dict)
            and comparison.get("operator") == "<="
            and type(comparison.get("right")) is int
        )
    if family == "ring":
        return constraint.get("variant") == "irreflexive"
    if family == "value":
        return bool(
            constraint.get("object_type") and constraint.get("allowed")
        ) and not constraint.get("role_ref")
    if family == "cardinality":
        return constraint.get("scope") == "object"
    return True


def place_formulas(document, ontology, components, relations, mapped):
    """Mutate the ontology and disposition index only after a complete group lowers."""
    context = constraint_context(document)
    objects = context.objects
    parents = {parent for obj in objects.values() for parent in obj.get("subtype_of", ())}
    reviewed = {"String": set(), "Integer": set()}
    for oid, obj in objects.items():
        primitive = obj.get("primitive")
        if (
            obj.get("kind") == "value"
            and primitive in reviewed
            and not obj.get("subtype_of")
            and oid not in parents
        ):
            reviewed[primitive].add(oid)
    strings, integers = reviewed["String"], reviewed["Integer"]

    def place(constraint, path, fact_id=None):
        if not _supported_shape(constraint, relations):
            return
        synthetic = "_ossie_rule_" + "_".join(map(str, path))
        named = {**constraint, "id": constraint.get("id") or synthetic}
        try:
            requirements = constraint_requirements(context, named, fact_id)
            placements = _placements(named, requirements, ontology, components, relations, strings, integers)
        except (ExportInputError, _Unprojected):
            return
        for target, expression in placements:
            target.setdefault("requires", []).append(expression)
        mapped[path] = _FORMULA
        for key in _METADATA & constraint.keys():
            mapped[(*path, key)] = ("extension", "gnd-source", None)

    for i, fact in enumerate(document.get("fact_types", ())):
        for j, constraint in enumerate(fact.get("constraints", ())):
            place(constraint, ("fact_types", i, "constraints", j), fact["id"])
        if "derivation_rule" in fact:
            try:
                expressions = _derived_chain(context, fact, relations, strings)
            except (ExportInputError, _Unprojected):
                continue
            relations[fact["id"]].target["derived_by"] = expressions
            mapped[("fact_types", i, "derivation_rule")] = _FORMULA

    for i, constraint in enumerate(document.get("constraints", ())):
        place(constraint, ("constraints", i))
