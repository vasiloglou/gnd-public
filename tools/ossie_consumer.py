"""Compare Ossie declarations with the pinned consumer's PyRel source AST."""

from __future__ import annotations

import ast
from collections import Counter
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Declarations:
    concepts: Counter
    parents: Counter
    relationships: Counter
    identifiers: Counter

    def difference(self, received: Declarations) -> dict:
        result = {}
        for kind in ("concepts", "parents", "relationships", "identifiers"):
            expected, actual = getattr(self, kind), getattr(received, kind)
            missing = sorted((expected - actual).elements())
            extra = sorted((actual - expected).elements())
            if missing or extra:
                result[kind] = {"missing": missing, "extra": extra}
        return result


def ontology_declarations(document: dict[str, Any]) -> Declarations:
    """Read declaration identities directly from the exported JSON ontology."""
    concepts = document["ontology"]
    return Declarations(
        Counter(item["concept"] for item in concepts),
        Counter((item["concept"], parent) for item in concepts for parent in item.get("extends", ())),
        Counter(
            (item["concept"], relationship["name"])
            for item in concepts for relationship in item.get("relationships", ())
        ),
        Counter(
            (item["concept"], relationship)
            for item in concepts for relationship in item.get("identify_by", ())
        ),
    )


def _assignments(tree: ast.Module):
    for statement in tree.body:
        if (
            isinstance(statement, ast.Assign)
            and len(statement.targets) == 1
            and isinstance(statement.value, ast.Call)
            and isinstance(statement.value.func, ast.Attribute)
        ):
            yield statement.targets[0], statement.value


def _name(node: ast.expr, bindings: dict[str, str]) -> str:
    if not isinstance(node, ast.Name):
        raise TypeError("unsupported name in pinned consumer source")
    return bindings.get(node.id, node.id)


def pyrel_declarations(source: bytes) -> Declarations:
    """Extract names and edges without importing or executing emitted Python."""
    tree = ast.parse(source)
    bindings = {}
    concepts = Counter()
    for target, call in _assignments(tree):
        if call.func.attr == "Concept":
            if not isinstance(target, ast.Name) or not call.args:
                raise ValueError("unsupported concept declaration in pinned consumer source")
            name = ast.literal_eval(call.args[0])
            if not isinstance(name, str):
                raise ValueError("unsupported concept name in pinned consumer source")
            bindings[target.id] = name
            concepts[name] += 1

    parents, relationships, identifiers = Counter(), Counter(), Counter()
    for target, call in _assignments(tree):
        if call.func.attr == "Concept":
            for keyword in call.keywords:
                if keyword.arg == "extends":
                    if not isinstance(keyword.value, (ast.List, ast.Tuple)):
                        raise ValueError("unsupported parents in pinned consumer source")
                    for parent in keyword.value.elts:
                        parents[(_name(target, bindings), _name(parent, bindings))] += 1
        elif call.func.attr in {"Property", "Relationship"}:
            if not isinstance(target, ast.Attribute):
                raise ValueError("unsupported relationship declaration in pinned consumer source")
            relationships[(_name(target.value, bindings), target.attr)] += 1

    for statement in tree.body:
        if not isinstance(statement, ast.Expr) or not isinstance(statement.value, ast.Call):
            continue
        call = statement.value
        if not isinstance(call.func, ast.Attribute) or call.func.attr != "identify_by":
            continue
        owner = _name(call.func.value, bindings)
        for argument in call.args:
            if not isinstance(argument, ast.Attribute):
                raise TypeError("unsupported identifier in pinned consumer source")
            relationship_owner = _name(argument.value, bindings)
            name = argument.attr if relationship_owner == owner else f"{relationship_owner}.{argument.attr}"
            identifiers[(owner, name)] += 1
    return Declarations(concepts, parents, relationships, identifiers)


def call_counts(source: bytes) -> Counter:
    return Counter(
        call.func.attr for call in ast.walk(ast.parse(source))
        if isinstance(call, ast.Call) and isinstance(call.func, ast.Attribute)
    )
