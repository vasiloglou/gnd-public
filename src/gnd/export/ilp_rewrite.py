"""Clause-to-``guarded`` rewriting for ``gnd import ilp-rules`` (IK5, D8 (o)).

The normative fragment table, its check order and its semantic-difference
rows live in ``docs/reference/ilp-bridge.md``; this module implements checks 1
to 9 and the join check 9b in that order, and the import service runs check 10
(the model validator).
The first failing check refuses the clause with its construct name. A clause
that passes becomes one ``guarded`` constraint by **body rewriting**: the head
variable is dropped, one designated body literal moves into the consequent,
negated, and the remaining atoms form the antecedent. Nothing here evaluates
clause text; it is data from the closed clause form.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export.ilp import Column, IlpError

__all__ = ["NEGATE", "REFUSALS", "check_join_types", "rewrite", "variable"]

NEGATE = {">": "<=", "<=": ">", "<": ">=", ">=": "<", "=": "!=", "!=": "="}
#: Every refusal name, in check order (check 10, ``invalid-guarded``, is the
#: import service's).
REFUSALS = (
    "head-shape", "negation-as-failure", "disjunction", "aggregate", "unknown-predicate",
    "arity", "recursion", "example-variable", "multiple-comparisons", "comparison-type",
    "non-ground-absence", "empty-antecedent", "disconnected-body", "unbound-comparison",
    "constant-spelling", "type-confused-join", "invalid-guarded",
)
_KINDS = {"not": "negation-as-failure", "or": "disjunction", "aggregate": "aggregate"}


def _refuse(name: str, index: int, detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"clause {index}: {name}: {detail}")


def variable(name: str) -> str:
    """An injective spelling of a Prolog variable as a guarded ``$`` variable:
    an upper-case letter becomes its lower case, a lower-case letter is prefixed
    by ``_``, and ``_`` doubles. So ``B`` is ``$v_b`` and ``Ab`` is ``$v_a_b``."""
    out = []
    for character in name:
        if character.isupper():
            out.append(character.lower())
        elif character == "_":
            out.append("__")
        elif character.isalpha():
            out.append("_" + character)
        else:
            out.append(character)
    return "$v_" + "".join(out)


def _vars(terms: list[dict[str, Any]]) -> set[str]:
    return {term["var"] for term in terms if "var" in term and term["var"] != "_"}


def _anonymous(terms: list[dict[str, Any]]) -> bool:
    """An anonymous ``_`` is a fresh variable no other literal can bind."""
    return any(term.get("var") == "_" for term in terms)


def check_join_types(
    atoms: list[dict[str, Any]],
    compares: list[tuple[dict[str, Any], str | None]],
    index: int,
    neutral: dict[str, Any],
    *,
    closures: Mapping[str, frozenset[str]],
) -> int:
    """Check 9b, ``type-confused-join`` (D12 (o), D13 (o)); returns the pairs compared.

    A named variable's sites are the atom positions it occupies and the declared
    type of a comparison predicate it is an operand of. Every pair of their
    object types must have intersecting ancestor ``closures`` -- the predicate
    of ``semantic:op-term-type-compat``. Each ``_`` is its own fresh variable,
    so it has no join to check."""
    object_type = {row["name"]: row["object_type"] for row in neutral["types"]}
    argument_types = {row["name"]: row["types"] for row in neutral["predicates"]}
    sites: dict[str, set[str]] = {}
    for atom in atoms:
        for term, type_name in zip(atom["args"][1:], argument_types[atom["predicate"]][1:],
                                   strict=True):
            if "var" in term and term["var"] != "_":
                sites.setdefault(term["var"], set()).add(object_type[type_name])
    for compare, declared in compares:
        if declared is not None:
            for name in _vars([compare["left"], compare["right"]]):
                sites.setdefault(name, set()).add(object_type[declared])
    pairs = 0
    for name, found in sites.items():
        ordered = sorted(found)
        for position, first in enumerate(ordered):
            for second in ordered[position + 1:]:
                pairs += 1
                if not closures.get(first, frozenset({first})) & closures.get(second, frozenset({second})):
                    raise _refuse("type-confused-join", index,
                                  f"variable {name} joins {first} and {second}")
    return pairs


def rewrite(
    clause: dict[str, Any],
    index: int,
    neutral: dict[str, Any],
    columns: dict[str, Column],
    *,
    closures: Mapping[str, frozenset[str]] | None = None,
    boolean_strings: bool = True,
) -> dict[str, Any]:
    """Checks 1 to 9, the join check 9b and the rewrite; returns ``{type, antecedent, consequent}``.

    ``columns`` are the export's predicates (:func:`gnd.export.ilp.schema`).
    ``closures`` (:func:`gnd.export.ilp.type_closures`) turns on check 9b; the
    import always passes them, and without them the check is skipped.
    ``boolean_strings`` reads a ``"true"``/``"false"`` string on a boolean role
    as the boolean; without it check 9 refuses that string (IL2-D13)."""
    predicates = columns
    comparisons = {row["name"]: row for row in neutral["comparisons"]}
    primitives = {row["name"]: row["primitive"] for row in neutral["types"]}

    # 1. head-shape
    head = clause["head"]
    args = head["args"]
    if head["predicate"] != "wrong" or len(args) != 1 or "var" not in args[0] or args[0]["var"] == "_":
        raise _refuse("head-shape", index, "the head must be wrong(X) with one variable X")
    example = args[0]["var"]

    # 2. only atoms and comparisons
    for literal in clause["body"]:
        kind = next(iter(literal))
        if kind in _KINDS:
            raise _refuse(_KINDS[kind], index, f"the body holds a {kind} literal")

    # Comparison predicates the export declared are comparisons, whatever form wrote them.
    atoms: list[dict[str, Any]] = []
    compares: list[tuple[dict[str, Any], str | None]] = []
    for literal in clause["body"]:
        if "compare" in literal:
            compares.append((literal["compare"], None))
            continue
        atom = literal["atom"]
        if atom["predicate"] in comparisons:
            if len(atom["args"]) != 2:
                raise _refuse("arity", index, f"{atom['predicate']} takes two arguments")
            row = comparisons[atom["predicate"]]
            left, right = atom["args"]
            compares.append(({"operator": row["operator"], "left": left, "right": right},
                             row["type"]))
            continue
        atoms.append(atom)

    # 3. known predicates, arity, no recursion
    for atom in atoms:
        name = atom["predicate"]
        if name == "wrong":
            raise _refuse("recursion", index, "wrong appears in its own body")
        if name not in predicates:
            raise _refuse("unknown-predicate", index, f"{name!r} is not an exported predicate")
        if len(atom["args"]) != len(predicates[name].types):
            raise _refuse("arity", index, f"{name} takes {len(predicates[name].types)} arguments")

    # 4. the example variable is every atom's first argument, and only that
    for atom in atoms:
        first, rest = atom["args"][0], atom["args"][1:]
        if first.get("var") != example or example in _vars(rest):
            raise _refuse("example-variable", index,
                          f"{atom['predicate']} must take {example} first and only there")
    for compare, _type in compares:
        if example in _vars([compare["left"], compare["right"]]):
            raise _refuse("example-variable", index, f"{example} appears in a comparison")

    # 5. at most one comparison, over an integer type, with a variable operand
    if len(compares) > 1:
        raise _refuse("multiple-comparisons", index, "a guarded antecedent holds atoms only")
    role_type: dict[str, set[str]] = {}
    for atom in atoms:
        for term, type_name in zip(atom["args"][1:], predicates[atom["predicate"]].types[1:],
                                   strict=True):
            if "var" in term:
                role_type.setdefault(term["var"], set()).add(type_name)
    if compares:
        compare, declared = compares[0]
        operands = _vars([compare["left"], compare["right"]])
        if not operands:
            raise _refuse("comparison-type", index, "a comparison needs a variable operand")
        types = {declared} if declared else set()
        for name in operands:
            types |= role_type.get(name, set())
        if any(primitives.get(name) != "integer" for name in types):
            raise _refuse("comparison-type", index,
                          f"comparisons are over integer types only, not {sorted(types)}")

    # 6. designation
    designated: dict[str, Any] | None = None
    if not compares:
        for position in range(len(atoms) - 1, -1, -1):
            others = set().union(*(_vars(a["args"][1:]) for i, a in enumerate(atoms) if i != position))
            candidate = atoms[position]["args"][1:]
            if not _anonymous(candidate) and _vars(candidate) <= others:
                designated = atoms[position]
                break
        if designated is None:
            raise _refuse("non-ground-absence", index,
                          "no atom has all its variables bound by the others")
    antecedent = [atom for atom in atoms if atom is not designated]

    # 7. a non-empty, connected antecedent
    if not antecedent:
        raise _refuse("empty-antecedent", index, "nothing is left for the antecedent")
    reached, frontier = {0}, [0]
    while frontier:
        current = _vars(antecedent[frontier.pop()]["args"][1:])
        for position, atom in enumerate(antecedent):
            if position not in reached and current & _vars(atom["args"][1:]):
                reached.add(position)
                frontier.append(position)
    if len(reached) != len(antecedent):
        raise _refuse("disconnected-body", index, "the antecedent atoms are not joined")

    # 8. the consequent is ground
    bound = set().union(*(_vars(atom["args"][1:]) for atom in antecedent))
    if compares:
        operands = [compares[0][0]["left"], compares[0][0]["right"]]
        if _anonymous(operands) or not _vars(operands) <= bound:
            raise _refuse("unbound-comparison", index, "a comparison variable is not bound")
    elif _anonymous(designated["args"][1:]) or not _vars(designated["args"][1:]) <= bound:  # type: ignore[index]
        raise _refuse("non-ground-absence", index, "the absence has an unbound variable")

    # 9. constants guarded would read as variables, then the rewrite itself
    fresh = iter(range(1, 1 << 30))

    def scalar(term: dict[str, Any], type_name: str | None) -> Any:
        if "var" in term:
            return f"$anon{next(fresh)}" if term["var"] == "_" else variable(term["var"])
        value = term["const"]
        if isinstance(value, str):
            if value.startswith("$"):
                raise _refuse("constant-spelling", index,
                              f"the constant {value!r} would read as a variable")
            if not all(character == " " or character.isprintable() for character in value):
                # A control, line-separator, surrogate or other non-printable
                # character does not survive the proposal's YAML round trip
                # (review R4), so the constraint evolve reads would differ.
                raise _refuse("constant-spelling", index,
                              f"the constant {value!r} holds a character YAML does not keep")
            if primitives.get(type_name) == "boolean" and value in ("true", "false"):
                if not boolean_strings:
                    raise _refuse("constant-spelling", index,
                                  f"the string {value!r} is not the boolean {value}")
                return value == "true"
        return value

    def item(atom: dict[str, Any]) -> dict[str, Any]:
        column = predicates[atom["predicate"]]
        return {"fact_type": column.fact_type,
                "bind": {role: scalar(term, type_name) for role, term, type_name in zip(
                    column.role_names, atom["args"][1:], column.types[1:], strict=True)}}

    body = [item(atom) for atom in antecedent]
    if compares:
        compare, _declared = compares[0]
        consequent = {"comparison": {"operator": NEGATE[compare["operator"]],
                                     "left": scalar(compare["left"], None),
                                     "right": scalar(compare["right"], None)}}
    else:
        consequent = {"absence": item(designated)}  # type: ignore[arg-type]

    # 9b. no variable joins object types that share no ancestor
    if closures is not None:
        check_join_types(atoms, compares, index, neutral, closures=closures)
    return {"type": "guarded", "antecedent": body, "consequent": consequent}
