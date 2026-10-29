"""AMIE-style mined rules: the typed triple export and the Horn-rule reader (ilp-learners IL4).

Spec: ``.gnd-planning/milestones/ilp-learners/notes/phase-IL4-spec.md`` §6.
Contract page: ``docs/reference/ilp-bridge.md``, "AMIE-style miner".

**Export.** One relation ``f_<fact type>`` per binary asserted fact type the
population covers; each value is spelled ``<object type id>:<value>``, so a
join inside the miner stays typed (IL4-D5 (o)). A type in a subtype
hierarchy is spelled by its family instead (:func:`family`, IL4-Q1), so a
subtype and its supertype meet in a join as the checker's values do. ``amie/facts.tsv`` holds one
sorted ``subject TAB relation TAB object`` line per distinct fact, and
``amie/relations.json`` the population digest, the relations and every skipped
fact type with its reason. No labels.

**Import.** :func:`parse_rules` reads AMIE's printed rule lines (closed, capped,
total); :func:`mapped` turns one into a ``guarded`` constraint with an ``atom``
consequent, refusing every other shape by name in :data:`MAPPING_REFUSALS`
order; :func:`count` counts it over distinct head pairs. Nothing here runs a
learner or evaluates rule text.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

from gnd.exits import EXIT_ILL_FORMED
from gnd.export import ilp as _ilp
from gnd.export.ilp import IlpError

__all__ = [
    "ADAPTER_VERSION", "COUNT_REFUSALS", "EXPORT_REFUSALS", "FORMULA", "MAPPING_REFUSALS",
    "MAX_ATOMS", "MAX_DIGITS", "MAX_JOIN_ROWS", "MAX_RULES", "MAX_TEXT", "Counts", "MinedRule",
    "canonical", "count", "extract_rules", "family", "mapped", "parse_rules", "relation_table", "render",
    "spell",
]

#: "2" spells a subtype hierarchy by its family (IL4-Q1, ILC-D4 (o)); a model with
#: no subtypes renders the same facts as "1".
ADAPTER_VERSION = "2"
#: IL4-D7 (o), fixed before results.
MAX_TEXT = 1024 * 1024
MAX_RULES = 256
MAX_ATOMS = 4
MAX_DIGITS = 18
MAX_JOIN_ROWS = 1_000_000
FORMULA = "std-confidence-head-pairs"
EXPORT_REFUSALS = ("no-relations", "unrepresentable")
#: The mapping's refusals in check order; ``type-confused-join`` is the shared
#: join check (``ilp_rewrite.check_join_types``), called last.
MAPPING_REFUSALS = ("open-world-head", "unknown-predicate", "constant-atom", "reflexive-atom",
                    "recursion", "unbound-head", "disconnected-body", "type-confused-join")
#: The counting's and admission's refusals in check order (D11 (o): holds only).
COUNT_REFUSALS = ("too-large", "covers-nothing", "support-mismatch", "does-not-hold")

_VARIABLE = re.compile(r"\?[a-z]")
_TOKEN = re.compile(r"[!-~]+")
_COUNT = re.compile(rf"[0-9]{{1,{MAX_DIGITS}}}")
_FIGURE = re.compile(rf"-?[0-9]{{1,{MAX_DIGITS}}}(?:\.[0-9]{{1,{MAX_DIGITS}}})?")
_SIZE = re.compile(rf"-1|[0-9]{{1,{MAX_DIGITS}}}")
_FUNCTIONAL = re.compile(r"-1|\?[a-z]")
_ESCAPES = {"\\": "\\\\", "\t": "\\t", "\n": "\\n"}


# -- export ------------------------------------------------------------------

def family(model: Any) -> dict[str, str]:
    """Each object type's family: the least top-type id, in code-point order, of the
    weakly connected component of the subtype graph that holds it (ILC-D1 (o)).

    A type in no subtype relation is its own family. Two types whose ancestor
    closures intersect are always in one family, so the count never separates
    what check 9b joins; types of one family that share no ancestor are refused
    by 9b before any count. Linear in the subtype graph, read through ModelIndex."""
    from gnd.model_index import ModelIndex

    rows = ModelIndex.for_model(model).object_types_by_id()
    parent = {identifier: identifier for identifier in rows}

    def root(identifier: str) -> str:
        while parent[identifier] != identifier:
            parent[identifier] = parent[parent[identifier]]
            identifier = parent[identifier]
        return identifier

    for identifier, row in rows.items():
        for supertype in row.get("subtype_of") or []:
            if supertype in parent:
                parent[root(identifier)] = root(supertype)
    names: dict[str, str] = {}
    for identifier, row in rows.items():
        if not row.get("subtype_of"):
            component = root(identifier)
            names[component] = min(names.get(component, identifier), identifier)
    return {identifier: names.get(root(identifier), identifier) for identifier in rows}


def spell(family_name: str, value: Any, *, where: str) -> str:
    """``<family>:<value>``, the one spelling the export and the count share; the
    family is the object type itself outside a subtype hierarchy (:func:`family`)."""
    value = _ilp.export_value(value, where=where)
    if isinstance(value, bool):
        text = "true" if value else "false"
    elif isinstance(value, int):
        text = str(value)
    else:
        text = "".join(_ESCAPES.get(character, character) for character in value)
        if any(not character.isprintable() for character in text):
            raise IlpError(EXIT_ILL_FORMED, f"unrepresentable: {where} holds a non-printable character "
                           "the triple export cannot spell")
    return f"{family_name}:{text}"


@dataclass(frozen=True)
class Relation:
    """One exported relation: its fact type, its two role names, their object types
    and the families that spell their values."""

    fact_type: str
    roles: tuple[str, str]
    types: tuple[str, str]
    families: tuple[str, str]


def relation_table(model: Any, covers: list[str]) -> tuple[dict[str, Relation], dict[str, Relation],
                                                           list[dict[str, str]]]:
    """Exported relations, uncovered binary relations, and skipped fact types with reasons.

    Names come from the neutral form's own schema, so a name the ILP export
    refuses is refused here too."""
    from gnd.redaction import RedactionPolicy

    shape, columns = _ilp.schema(model, RedactionPolicy.from_model(model).effective_roles)
    object_types = {row["name"]: row["object_type"] for row in shape["types"]}
    families = family(model)
    covered = set(covers)
    exported: dict[str, Relation] = {}
    uncovered: dict[str, Relation] = {}
    skipped = [{"fact_type": fact_type, "reason": "derived"}
               for fact_type in shape["skipped"]["derived_fact_types"]]
    for name, column in columns.items():
        if len(column.role_names) != 2:
            skipped.append({"fact_type": column.fact_type, "reason": "arity"})
            continue
        types = (object_types[column.types[1]], object_types[column.types[2]])
        relation = Relation(column.fact_type, (column.role_names[0], column.role_names[1]), types,
                            (families.get(types[0], types[0]), families.get(types[1], types[1])))
        if column.fact_type in covered:
            exported[name] = relation
        else:
            uncovered[name] = relation
            skipped.append({"fact_type": column.fact_type, "reason": "not-covered"})
    return exported, uncovered, sorted(skipped, key=lambda row: row["fact_type"])


def pairs(relations: Mapping[str, Relation], population: Any) -> dict[str, list[tuple[str, str]]]:
    """Each relation's facts as spelled (subject, object) pairs, in population row order."""
    out: dict[str, list[tuple[str, str]]] = {}
    for name, relation in relations.items():
        rows = []
        for row in population.facts.get(relation.fact_type) or []:
            where = f"fact type {relation.fact_type!r}"
            if not isinstance(row, dict) or not all(role in row for role in relation.roles):
                raise IlpError(EXIT_ILL_FORMED, f"unrepresentable: a {where} fact lacks a role")
            rows.append(tuple(spell(name, row[role], where=where)
                              for role, name in zip(relation.roles, relation.families, strict=True)))
        out[name] = rows
    return out


def canonical_bytes(document: Any) -> bytes:
    return _ilp.canonical_bytes(document)


def render(model: Any, population: Any, population_sha256: str) -> dict[str, bytes]:
    """``amie/facts.tsv`` and ``amie/relations.json`` for one population."""
    covers = list(getattr(population, "covers", None) or [])
    relations, _uncovered, skipped = relation_table(model, covers)
    if not relations:
        raise IlpError(EXIT_ILL_FORMED, "no-relations: the population covers no binary asserted "
                       "fact type, so there is nothing to mine")
    facts = pairs(relations, population)
    lines = sorted({f"{s}\t{name}\t{o}" for name, rows in facts.items() for s, o in rows})
    if sum(len(line) for line in lines) > _ilp.MAX_FILE_BYTES or len(lines) > _ilp.MAX_FACTS:
        raise IlpError(EXIT_ILL_FORMED, f"too-large: the export exceeds {_ilp.MAX_FACTS} facts")
    index = {
        "population_sha256": population_sha256,
        "relations": [{"name": name, "fact_type": relation.fact_type, "roles": list(relation.roles),
                       "types": list(relation.types), "facts": len(set(facts[name]))}
                      for name, relation in relations.items()],
        "skipped": skipped,
    }
    return {"amie/facts.tsv": "".join(f"{line}\n" for line in lines).encode("utf-8"),
            "amie/relations.json": canonical_bytes(index)}


# -- reader ------------------------------------------------------------------

def _refuse(detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"unparsable: {detail}")


def _atoms(tokens: list[str], number: int) -> list[list[str]]:
    if not tokens or len(tokens) % 3:
        raise _refuse(f"line {number}: an atom is a subject, a relation and an object")
    atoms = [tokens[k:k + 3] for k in range(0, len(tokens), 3)]
    for subject, relation, obj in atoms:
        if _VARIABLE.fullmatch(relation) or relation.startswith("?"):
            raise _refuse(f"line {number}: relation {relation!r} is a variable")
        for term in (subject, obj):
            if term.startswith("?") and not _VARIABLE.fullmatch(term):
                raise _refuse(f"line {number}: variable {term!r} is not ?a to ?z")
    return atoms


def parse_rules(text: str) -> list[dict[str, Any]]:
    """AMIE's printed rule lines to rules; anything else is ``unparsable`` (spec §6).

    One rule per ``\\n``-ended line (the last may lack it): the rule, then head
    coverage, standard confidence, PCA confidence, Support, body size, PCA body
    size and the functional variable, tab-separated, as AMIE 4.0.0 prints them
    (IL4-D10 probe). The rule is space-separated triples, ``=>``, one triple.
    Support and body size are read as counts; body size ``-1`` (AMIE computes
    it only with ``-enstd``) is ``None``; the other figures are kept verbatim."""
    if len(text) > MAX_TEXT:
        raise _refuse(f"the rules exceed {MAX_TEXT} characters")
    if not text:
        raise _refuse("no rule")
    lines = text[:-1].split("\n") if text.endswith("\n") else text.split("\n")
    if len(lines) > MAX_RULES:
        raise _refuse(f"more than {MAX_RULES} rules")
    rules, seen = [], set()
    for number, line in enumerate(lines, start=1):
        fields = line.split("\t")
        if len(fields) != 8:
            raise _refuse(f"line {number}: {len(fields)} tab-separated fields, not 8")
        rule, coverage, standard, pca, support, body_size, pca_body, functional = fields
        if not all(_TOKEN.fullmatch(token) for token in rule.split(" ") if token) or not rule.strip():
            raise _refuse(f"line {number}: the rule holds a character outside printable ASCII")
        tokens = rule.split()
        if tokens.count("=>") != 1:
            raise _refuse(f"line {number}: a rule has exactly one =>")
        arrow = tokens.index("=>")
        body, head = _atoms(tokens[:arrow], number), _atoms(tokens[arrow + 1:], number)
        if len(head) != 1:
            raise _refuse(f"line {number}: the head is one atom")
        if len(body) + 1 > MAX_ATOMS:
            raise _refuse(f"line {number}: more than {MAX_ATOMS} atoms")
        for name, value, pattern in (("head coverage", coverage, _FIGURE),
                                     ("standard confidence", standard, _FIGURE),
                                     ("PCA confidence", pca, _FIGURE), ("Support", support, _COUNT),
                                     ("body size", body_size, _SIZE), ("PCA body size", pca_body, _SIZE),
                                     ("functional variable", functional, _FUNCTIONAL)):
            if not value.isascii() or pattern.fullmatch(value) is None:
                raise _refuse(f"line {number}: {name} {value[:40]!r} is not in AMIE's spelling")
        key = canonical(body, head[0])
        if key in seen:
            raise _refuse(f"line {number}: the rule is printed twice")
        seen.add(key)
        rules.append({"body": body, "head": head[0], "support": int(support),
                      "body_size": None if body_size == "-1" else int(body_size),
                      "figures": {"head_coverage": coverage, "std_confidence": standard,
                                  "pca_confidence": pca, "pca_body_size": pca_body,
                                  "functional_variable": functional}})
    return rules


def extract_rules(stdout: str) -> str:
    """The rule lines of AMIE's stdout, shared by the live script and its replay.

    A rule line starts with ``?``; AMIE's settings, header and progress lines do
    not. The lines are kept verbatim and in printed order; an empty result is
    ``""`` (import ``none``)."""
    lines = [line for line in stdout.split("\n") if line.startswith("?")]
    return "".join(f"{line}\n" for line in lines)


def canonical(body: list[list[str]], head: list[str]) -> tuple[tuple[str, str, str], ...]:
    """A rule up to variable renaming and body order: the least renaming over every
    body order, variables numbered by first appearance (review 3, IL4-F10)."""
    from itertools import permutations

    forms = []
    for order in permutations(body):
        names: dict[str, str] = {}

        def name(term: str, names: dict[str, str] = names) -> str:
            return names.setdefault(term, f"?{len(names)}") if term.startswith("?") else term

        forms.append(tuple((name(s), r, name(o)) for s, r, o in [*order, head]))
    return min(forms)


# -- mapping -----------------------------------------------------------------

@dataclass(frozen=True)
class MinedRule:
    """One rule after the mapping: its constraint core and its typed atoms."""

    core: dict[str, Any]
    body: tuple[tuple[str, str, str], ...]
    head: tuple[str, str, str]


def _mapping(name: str, index: int, detail: str) -> IlpError:
    return IlpError(EXIT_ILL_FORMED, f"rule {index}: {name}: {detail}")


def mapped(rule: dict[str, Any], index: int, relations: Mapping[str, Relation],
           uncovered: Mapping[str, Relation], shape: dict[str, Any],
           closures: Mapping[str, frozenset[str]]) -> MinedRule:
    """The mapping table of spec §6, in :data:`MAPPING_REFUSALS` order."""
    from gnd.export.ilp_rewrite import check_join_types

    body = [tuple(atom) for atom in rule["body"]]
    head = tuple(rule["head"])
    atoms = [*body, head]
    if head[1] in uncovered:
        raise _mapping("open-world-head", index, f"{head[1]} is outside the population's covers, "
                       "so a missing head fact is not evidence against the rule")
    for _subject, relation, _obj in atoms:
        if relation not in relations:
            raise _mapping("unknown-predicate", index, f"{relation} is not a relation of the export")
    for subject, relation, obj in atoms:
        for term in (subject, obj):
            if not term.startswith("?"):
                raise _mapping("constant-atom", index, f"{relation} holds a constant")
    for subject, relation, obj in atoms:
        if subject == obj:
            raise _mapping("reflexive-atom", index, f"{relation} joins {subject} with itself")
    if any(relation == head[1] for _s, relation, _o in body):
        raise _mapping("recursion", index, f"the head relation {head[1]} is in the body")
    bound = {term for subject, _r, obj in body for term in (subject, obj)}
    for term in (head[0], head[2]):
        if term not in bound:
            raise _mapping("unbound-head", index, f"head variable {term} is not in the body")
    # The checker evaluates a connected antecedent only (review 1): join the body's
    # atoms through shared variables and require one component.
    reached, frontier = set(), [0]
    while frontier:
        atom = frontier.pop()
        if atom not in reached:
            reached.add(atom)
            terms = {body[atom][0], body[atom][2]}
            frontier += [k for k, (s, _r, o) in enumerate(body) if k not in reached and terms & {s, o}]
    if len(reached) != len(body):
        raise _mapping("disconnected-body", index, "the body's atoms share no variable across parts")
    joins = [{"predicate": relation, "args": [{"var": "_"}, {"var": subject}, {"var": obj}]}
             for subject, relation, obj in atoms]
    try:
        check_join_types(joins, [], index, shape, closures=closures)
    except IlpError as error:
        raise IlpError(error.code, str(error).replace(f"clause {index}:", f"rule {index}:", 1)) from None

    def atom(subject: str, relation: str, obj: str) -> dict[str, Any]:
        entry = relations[relation]
        return {"fact_type": entry.fact_type,
                "bind": {entry.roles[0]: "$" + subject[1:], entry.roles[1]: "$" + obj[1:]}}

    core = {"type": "guarded", "antecedent": [atom(*a) for a in body],
            "consequent": {"atom": atom(*head)}}
    return MinedRule(core, tuple(body), head)


# -- counting ----------------------------------------------------------------

@dataclass(frozen=True)
class Counts:
    """Distinct head pairs: those the body reaches (denominator) and those that hold."""

    numerator: int
    denominator: int
    #: The satisfied head pairs, in first-reached order.
    satisfied: tuple[tuple[str, str], ...]


def count(rule: MinedRule, facts: Mapping[str, list[tuple[str, str]]], index: int, *,
          limit: int = MAX_JOIN_ROWS) -> Counts:
    """Numerator and denominator over distinct head pairs (spec §6 "Counting").

    The join's work is bounded by the product of the body relations' sizes,
    refused ``too-large`` above ``limit`` before it runs."""
    sizes = 1
    for _subject, relation, _obj in rule.body:
        sizes *= max(len(facts[relation]), 1)
        if sizes > limit:
            raise IlpError(EXIT_ILL_FORMED, f"rule {index}: too-large: the body's join could reach "
                           f"more than {limit} rows")
    bindings: list[dict[str, str]] = [{}]
    for subject, relation, obj in rule.body:
        extended = []
        for binding in bindings:
            for s, o in facts[relation]:
                joined = dict(binding)
                # setdefault binds a fresh variable and tests a bound one, so an atom
                # whose two ends are one variable needs s == o.
                if joined.setdefault(subject, s) == s and joined.setdefault(obj, o) == o:
                    extended.append(joined)
        bindings = extended
    head_subject, head_relation, head_object = rule.head
    held = set(facts[head_relation])
    reached = list(dict.fromkeys((b[head_subject], b[head_object]) for b in bindings))
    satisfied = tuple(pair for pair in reached if pair in held)
    return Counts(len(satisfied), len(reached), satisfied)
