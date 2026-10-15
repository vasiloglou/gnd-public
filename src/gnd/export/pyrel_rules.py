"""Render a model's rules as a readable PyRel program, as requirements.

Every supported constraint becomes one :class:`Requirement`: a *domain* (the
facts the rule talks about) and a *check* (what must hold for each of them).
That is PyRel's own shape for a logical rule, ``m.where(<domain>).require(<check>)``.

Two programs are rendered from the same list:

``lqp``
    Each rule is an executable ``require``. A RelationalAI engine (the logic
    reasoner, "LQP") enforces it and reports every violation. Requirements are
    not enforced by the local DuckDB backend, so this program does not check
    anything locally; ``--compile`` shows how PyRel compiled each requirement.

``duckdb``
    Each rule is printed as the same ``require`` and evaluated in its denial
    form, ``m.where(<domain>, <not check>)``: the facts that would violate it.
    The logic reasoner's direct LQP compiler lowers a requirement to that same
    condition (``domain and not check => Error``), so both programs state one rule.

The checker that GND's applications run (``pyrel_runtime.py``) is separate;
``tests/test_pyrel_rules.py`` ties the two by agreement.
"""
from __future__ import annotations

import datetime as _dt
import json
import keyword
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from gnd.errors import ModelLoadError, ModelValidationError
from gnd.model import load_model_bytes
from gnd.model_index import ModelIndex

from .pyrel_runtime import ExportInputError, _parse_document

TARGETS = ("duckdb", "lqp")
PYREL_VERSION = "1.30.1"
# model primitive -> PyRel type; a Duration is a whole number of days (GND has no other durations)
_TYPES = {"String": "String", "Integer": "Integer", "Float": "Float", "Boolean": "Boolean", "Date": "Date",
          "Duration": "Integer"}
_NEGATED = {"<": ">=", "<=": ">", "=": "!=", "!=": "==", ">=": "<", ">": "<="}
_PYOP = {"<": "<", "<=": "<=", "=": "==", "==": "==", "!=": "!=", ">=": ">=", ">": ">"}
_RESERVED = {"m", "not_", "Field", "String", "Integer", "Float", "Boolean", "Model", "Config",
             "rows", "facts", "report", "load", "json", "sys", "os", "re", "tempfile", "found",
             "value", "values", "probe_vars", "instances", "population", "config", "build", "main",
             "read_population", "witnesses", "compile_only", "RULES", "SCHEMA", "LIMIT", "EXPECTED",
             "warnings", "create_config", "argparse", "args", "parser", "problems", "caught", "w",
             "directory", "error", "rule", "name", "hits", "hit", "status", "row", "rows_", "path",
             "document", "relation", "roles", "r", "v", "k", "f", "g", "key", "fact", "seen", "aggregates",
             "std_math", "h_row", "h_a", "h_b", "h_c", "h_x", "Fraction", "Date", "datetime", "std_date", "days"}


@dataclass(frozen=True)
class Atom:
    relation: str
    args: tuple[Any, ...]          # "$name" variables, literals, or None for "any value"


@dataclass(frozen=True)
class Count:
    """``aggregates.count(*of)``, grouped ``.per(*per)`` when ``per`` is given."""
    of: tuple[str, ...]
    per: tuple[str, ...] = ()


@dataclass(frozen=True)
class Compare:
    operator: str
    left: Any
    right: Any


@dataclass(frozen=True)
class Check:
    kind: str                      # holds | absent | compare | same
    atom: Atom | None = None
    compare: Compare | None = None
    pairs: tuple[tuple[str, str], ...] = ()


@dataclass(frozen=True)
class Requirement:
    id: str
    family: str
    modality: str
    quote: str
    domain: tuple[Atom, ...]
    check: Check
    witness: tuple[str, ...]       # variables reported for a violation
    vacuous_when: tuple[str, tuple[str, ...]]   # ("any"|"all", fact types whose emptiness makes it vacuous)
    refs: tuple[str, ...] = field(default=())   # fact types the rule reads
    part: str = ""                 # several requirements may make up one constraint (same id)
    listing: bool = False          # a plain query the DuckDB report needs; not a requirement
    info: tuple[tuple[str, Any], ...] = ()      # family details the report needs (bounds, scope, ...)


class _Model:
    """Model queries go through the read-only ModelIndex snapshot (RF6 query policy)."""

    def __init__(self, doc: dict[str, Any]):
        self.doc = doc
        self.index = ModelIndex(None, doc)
        self.objects = self.index.object_types_by_id()
        self._roles = self.index.role_object_types()
        self.facts = {fact_id: self.index.fact_type(fact_id) for fact_id in self._roles}
        self.helpers: dict[str, dict[str, Any]] = {}
        self.unchecked: list[dict[str, str]] = []   # textual rules: listed, never evaluated (as GND)
        # structured derived heads, lower strata first; each gets <head>_derived (computed) and, when
        # semiderived, <head>_claimed (the claim), while <head> is what constraints read (GND's view)
        self.derived = _strata({f: fact for f, fact in self.facts.items() if isinstance(fact.get("derivation_rule"), dict)})
        self.derived_relations = {f"{head}_derived": head for head in self.derived}
        self.derived_relations.update({f"{head}_claimed": head for head in self.derived
                                       if self.facts[head].get("derivation") == "semiderived"})

    def helper(self, name: str, fields: list[tuple[str, str]], kind: str, **data: Any) -> str:
        """Register a helper relation the rules refer to; rendered once, in registration order."""
        self.helpers.setdefault(name, {"fields": fields, "kind": kind, **data})
        return name

    def roles(self, fact_id: str) -> list[dict[str, Any]]:
        if fact_id not in self._roles:
            raise ExportInputError(f"unknown fact type {fact_id!r}")
        return [{"role_name": name, "object_type": object_id} for name, object_id in self._roles[fact_id].items()]

    def primitive(self, object_id: str) -> str:
        return _TYPES[self.raw_primitive(object_id)]

    def raw_primitive(self, object_id: str) -> str:
        """The model's own primitive (Date, Duration, ...), checked against what the programs support."""
        obj = self.objects.get(object_id)
        if obj is None:
            raise ExportInputError(f"unknown object type {object_id!r}")
        if "primitive" in obj:
            primitive = obj["primitive"]
        else:
            reference = (obj.get("reference") or {}).get("value_type")
            if reference is None:
                raise ExportInputError(f"object type {object_id!r} has no primitive or reference value type")
            primitive = self.primitive(reference)
        if primitive not in _TYPES:
            raise ExportInputError(f"primitive {primitive!r} is not supported by the rules programs yet")
        return primitive

    def raw_role_type(self, fact_id: str, role_name: str) -> str:
        for role in self.roles(fact_id):
            if role["role_name"] == role_name:
                return self.raw_primitive(role["object_type"])
        raise ExportInputError(f"fact type {fact_id!r} has no role {role_name!r}")

    def role_type(self, fact_id: str, role_name: str) -> str:
        for role in self.roles(fact_id):
            if role["role_name"] == role_name:
                return self.primitive(role["object_type"])
        raise ExportInputError(f"fact type {fact_id!r} has no role {role_name!r}")

    def plays(self, object_id: str) -> list[tuple[str, str]]:
        """Every (fact type, role) whose values belong to the object type, with reference widening."""
        found = []
        for fact_id in self.facts:
            for role in self.roles(fact_id):
                role_ot = role.get("object_type")
                reference = (self.objects.get(role_ot, {}).get("reference") or {}).get("value_type")
                if role_ot == object_id or reference == object_id:
                    found.append((fact_id, role["role_name"]))
        return found


def _quote(constraint: dict[str, Any]) -> str:
    provenance = constraint.get("provenance") or {}
    return str(provenance.get("user_quote") or provenance.get("user_note") or constraint.get("id", ""))


def _atom(model: _Model, pattern: dict[str, Any]) -> Atom:
    if set(pattern) != {"fact_type", "bind"} or not isinstance(pattern["bind"], dict):
        raise ExportInputError("atoms need exactly fact_type and bind")
    names = [role["role_name"] for role in model.roles(pattern["fact_type"])]
    unknown = set(pattern["bind"]) - set(names)
    if unknown:
        raise ExportInputError(f"unknown roles {sorted(unknown)} in {pattern['fact_type']}")
    for value in pattern["bind"].values():
        if isinstance(value, dict):
            raise ExportInputError("terms other than variables and literals are a later phase")
    return Atom(pattern["fact_type"], tuple(pattern["bind"].get(name) for name in names))


def _variables(atoms: tuple[Atom, ...]) -> tuple[str, ...]:
    seen: list[str] = []
    for atom in atoms:
        for arg in atom.args:
            if isinstance(arg, str) and arg.startswith("$") and arg not in seen:
                seen.append(arg)
    return tuple(sorted(seen))


def _guarded(model: _Model, c: dict[str, Any]) -> Requirement:
    domain = tuple(_atom(model, a) for a in c.get("antecedent", []))
    if not domain:
        raise ExportInputError(f"{c.get('id')}: a guarded rule needs an antecedent")
    consequent = c.get("consequent") or {}
    if len(consequent) != 1:
        raise ExportInputError(f"{c.get('id')}: one consequent expected")
    (kind, payload), = consequent.items()
    if kind == "atom":
        check = Check("holds", atom=_atom(model, payload))
    elif kind == "absence":
        check = Check("absent", atom=_atom(model, payload))
    elif kind == "comparison":
        if payload.get("operator") not in _NEGATED:
            raise ExportInputError(f"{c.get('id')}: unknown operator {payload.get('operator')!r}")
        types = _atom_types(model, domain)
        left, right = (_typed_term(model, c["id"], payload[side], types, payload["right" if side == "left" else "left"])
                       for side in ("left", "right"))
        check = Check("compare", compare=Compare(payload["operator"], left, right))
    else:
        raise ExportInputError(f"{c.get('id')}: consequent kind {kind!r} is not supported")
    if not _connected(domain):
        raise ExportInputError(f"{c.get('id')}: a disconnected antecedent is left unchecked by GND; "
                               "the rules programs refuse it rather than cross-join it")
    # GND calls the rule vacuous when any antecedent fact type is empty, as the constraint reads it
    antecedents = tuple(dict.fromkeys(a.relation for a in domain))
    refs = tuple(dict.fromkeys([a.relation for a in domain] + ([check.atom.relation] if check.atom else [])))
    temporal = _date_functions(check.compare) if check.compare else []
    info = (("temporal", temporal),) if temporal else ()
    found = [Requirement(c["id"], "guarded", c["modality"], _quote(c), domain, check, _variables(domain),
                         ("any", antecedents), refs, info=info)]
    if temporal:
        # GND leaves the rule unchecked when a computed date leaves years 1..9999 or past 10,000 date
        # applications; the report decides that from every binding, before reading the verdict. The
        # listing comes first: with no bindings the date arithmetic is not run at all (an empty Date
        # relation reaches DuckDB untyped, and NULL + INTERVAL does not bind).
        found.insert(0, Requirement(c["id"], "guarded", c["modality"], _quote(c), domain, Check("none"),
                                    _variables(domain), ("any", antecedents), refs, part="bindings", listing=True,
                                    info=info))
    return found


_DATE_FUNCTIONS = {"date_add": "add", "date_sub": "subtract"}


def _atom_types(model: _Model, atoms: tuple[Atom, ...]) -> dict[str, str]:
    """Each variable's model primitive (Date, Duration, Integer, ...), from the roles it fills."""
    types: dict[str, str] = {}
    for atom in atoms:
        for role, arg in zip(model.roles(atom.relation), atom.args):
            if isinstance(arg, str) and arg.startswith("$"):
                types.setdefault(arg, model.raw_role_type(atom.relation, role["role_name"]))
    return types


def _term_type(term: Any, types: dict[str, str]) -> str | None:
    if isinstance(term, str) and term.startswith("$"):
        return types.get(term)
    if isinstance(term, dict):
        if "date" in term:
            return "Date"
        if "duration_days" in term:
            return "Duration"
        if term.get("fn") in _DATE_FUNCTIONS:
            return "Date"
        return "Integer"
    return None


def _typed_term(model: _Model, cid: str, term: Any, types: dict[str, str], other: Any) -> Any:
    """Validate one guarded comparison operand; an untagged ISO string facing a Date becomes a Date literal."""
    if isinstance(term, str) and not term.startswith("$") and _term_type(other, types) == "Date":
        return {"date": term}
    if not isinstance(term, dict):
        return term
    if set(term) in ({"date"}, {"duration_days"}):
        return term
    fn, args = term.get("fn"), term.get("args") or []
    if fn in _DATE_FUNCTIONS:
        if len(args) != 2 or any(isinstance(a, dict) and "fn" in a for a in args):
            raise ExportInputError(f"{cid}: {fn} takes a date and a duration; nested date terms are a later phase")
        return {"fn": fn, "args": [_typed_term(model, cid, args[0], types, {"date": ""}), args[1]]}
    if fn in _ARITHMETIC:
        for v in _term_variables(term):
            if types.get(v) not in ("Integer", "Duration"):
                raise ExportInputError(f"{cid}: arithmetic on {types.get(v)} values is not supported by the rules programs")
        for literal in _term_literals(term):
            if not isinstance(literal, int) or isinstance(literal, bool):
                raise ExportInputError(f"{cid}: arithmetic with the literal {literal!r} is not supported by the rules programs")
        return term
    raise ExportInputError(f"{cid}: the function {fn!r} is not supported in rules programs' comparisons yet")


def _date_functions(compare: Compare) -> list[list[Any]]:
    """Every date_add/date_sub application in a comparison, as [function, date, days]."""
    found = []
    for side in (compare.left, compare.right):
        if isinstance(side, dict) and side.get("fn") in _DATE_FUNCTIONS:
            found.append([side["fn"], *side["args"]])
    return found


def _connected(atoms: tuple[Atom, ...]) -> bool:
    """True when every atom is reachable from the first through shared variables."""
    if len(atoms) <= 1:
        return True
    variables = [{a for a in atom.args if isinstance(a, str) and a.startswith("$")} for atom in atoms]
    reached, frontier = {0}, [0]
    while frontier:
        current = frontier.pop()
        for other, names in enumerate(variables):
            if other not in reached and names & variables[current]:
                reached.add(other)
                frontier.append(other)
    return len(reached) == len(atoms)


def _is_derived(model: _Model, fact_id: str) -> bool:
    return model.facts.get(fact_id, {}).get("derivation") in {"derived", "semiderived"}


def _mandatory(model: _Model, c: dict[str, Any], fact_id: str) -> Requirement:
    role = c.get("role")
    roles = model.roles(fact_id)
    owner = next((r for r in roles if r["role_name"] == role), None)
    if owner is None:
        raise ExportInputError(f"{c.get('id')}: mandatory needs one role of {fact_id}")
    universe = f"{owner['object_type']}_any"
    var = f"${owner['object_type']}"
    domain = (Atom(universe, (var,)),)
    check = Check("holds", atom=Atom(fact_id, tuple(var if r["role_name"] == role else None for r in roles)))
    return Requirement(c.get("id") or f"{fact_id}#mandatory", "mandatory", c["modality"], _quote(c),
                       domain, check, (var,), ("any", (fact_id,)), (fact_id,),
                       info=(("uncovered_vacuous", [fact_id]),))


def _subset(model: _Model, c: dict[str, Any]) -> Requirement:
    sub, sup = c.get("subset_role_seq") or [], c.get("superset_role_seq") or []
    if len(sub) != len(sup) or not sub:
        raise ExportInputError(f"{c.get('id')}: subset role sequences must have equal length")
    for seq in (sub, sup):
        if len({ref["fact_type"] for ref in seq}) != 1:
            raise ExportInputError(f"{c.get('id')}: role sequences spanning fact types are a later phase")
    names = _sequence_names(sub)

    def atom_for(seq):
        fact_id = seq[0]["fact_type"]
        position = {ref["role"]: name for ref, name in zip(seq, names)}
        return Atom(fact_id, tuple(position.get(r["role_name"]) for r in model.roles(fact_id)))

    left, right = atom_for(sub), atom_for(sup)
    return Requirement(c["id"], "subset", c["modality"], _quote(c), (left,), Check("holds", atom=right),
                       tuple(names), ("all", (left.relation, right.relation)), (left.relation, right.relation))


def _value(model: _Model, c: dict[str, Any]) -> Requirement:
    object_id = c["object_type"]
    if c.get("role_ref"):
        raise ExportInputError(f"{c.get('id')}: role-scoped value constraints are a later phase")
    if "allowed" not in c:
        ranges = c.get("ranges") or ([c["range"]] if isinstance(c.get("range"), dict) else None)
        if not ranges:
            raise ExportInputError(f"{c.get('id')}: a value constraint needs allowed, range or ranges")
        model.helper(f"{c['id']}_allowed", [("value", model.primitive(object_id))], "ranges",
                     object_type=object_id, ranges=ranges)
    var = f"${object_id}"
    plays = tuple(dict.fromkeys(fact for fact, _ in model.plays(object_id)))
    # GND evaluates a value rule over every fact and the instances roster; it is vacuous only when
    # both are empty, so the report checks the rosters too (vacuous_when "universe").
    return Requirement(c["id"], "value", c["modality"], _quote(c), (Atom(f"{object_id}_any", (var,)),),
                       Check("holds", atom=Atom(f"{c['id']}_allowed", (var,))), (var,), ("universe", plays), plays,
                       info=(("rosters", _rosters(model, object_id)),))


def _rosters(model: _Model, object_id: str) -> list[str]:
    """The instances keys that populate an object type: its own, and entities it is the reference value of."""
    return [object_id] + sorted(o for o, obj in model.objects.items()
                                if (obj.get("reference") or {}).get("value_type") == object_id)


def _sequence_names(seq: list[dict[str, Any]]) -> list[str]:
    """Readable variables for a role sequence: the role names, numbered only when one repeats."""
    names: list[str] = []
    for ref in seq:
        base = f"${ref.get('role')}"
        name, n = base, 2
        while name in names:
            name, n = f"{base}_{n}", n + 1
        names.append(name)
    return names


def _seq_atom(model: _Model, seq: list[dict[str, Any]], names: list[str], cid: str) -> Atom:
    """One fact-type atom whose listed roles carry the given variables, other roles left open."""
    facts = {ref.get("fact_type") for ref in seq}
    if len(facts) != 1:
        raise ExportInputError(f"{cid}: role sequences spanning fact types are a later phase")
    fact_id = seq[0]["fact_type"]
    position = {ref["role"]: name for ref, name in zip(seq, names)}
    unknown = set(position) - {r["role_name"] for r in model.roles(fact_id)}
    if unknown:
        raise ExportInputError(f"{cid}: unknown roles {sorted(unknown)} in {fact_id}")
    return Atom(fact_id, tuple(position.get(r["role_name"]) for r in model.roles(fact_id)))


def _role_object(model: _Model, fact_id: str, role_name: str) -> str:
    for role in model.roles(fact_id):
        if role["role_name"] == role_name:
            return role["object_type"]
    raise ExportInputError(f"fact type {fact_id!r} has no role {role_name!r}")


def _plays(model: _Model, c: dict[str, Any], refs: list[dict[str, Any]]) -> tuple[str, str]:
    """A helper relation of every instance playing any of the referenced roles; returns (helper, object type)."""
    objects = {_role_object(model, ref["fact_type"], ref["role"]) for ref in refs}
    if len(objects) != 1:
        raise ExportInputError(f"{c['id']}: the roles must be played by one object type")
    (object_id,) = objects
    helper = model.helper(f"{c['id']}_plays", [("member", model.primitive(object_id))], "plays",
                          refs=[(ref["fact_type"], ref["role"]) for ref in refs])
    return helper, object_id


def _mandatory_disjunctive(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    refs = c.get("role_refs") or []
    if len(refs) < 2:
        raise ExportInputError(f"{c['id']}: inclusive-or needs two or more roles")
    helper, object_id = _plays(model, c, refs)
    var = f"${object_id}"
    facts = tuple(dict.fromkeys(ref["fact_type"] for ref in refs))
    return [Requirement(c["id"], "mandatory-disjunctive", c["modality"], _quote(c),
                        (Atom(f"{object_id}_any", (var,)),), Check("holds", atom=Atom(helper, (var,))),
                        (var,), ("all", facts), facts, info=(("uncovered_vacuous", list(facts)),))]


def _two_sequences(model: _Model, c: dict[str, Any]) -> tuple[Atom, Atom, tuple[str, ...]]:
    a, b = c.get("role_seq_a") or [], c.get("role_seq_b") or []
    if not a or len(a) != len(b):
        raise ExportInputError(f"{c['id']}: the two role sequences must have the same, non-zero length")
    names = _sequence_names(a)
    return _seq_atom(model, a, names, c["id"]), _seq_atom(model, b, names, c["id"]), tuple(names)


def _equality(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    left, right, names = _two_sequences(model, c)
    lists = ("all", (left.relation, right.relation))
    return [Requirement(c["id"], "equality", c["modality"], _quote(c), (left,), Check("holds", atom=right),
                        names, lists, (left.relation, right.relation), part="a_not_b"),
            Requirement(c["id"], "equality", c["modality"], _quote(c), (right,), Check("holds", atom=left),
                        names, lists, (left.relation, right.relation), part="b_not_a")]


def _exclusion(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    left, right, names = _two_sequences(model, c)
    return [Requirement(c["id"], "exclusion", c["modality"], _quote(c), (left,), Check("absent", atom=right),
                        names, ("all", (left.relation, right.relation)), (left.relation, right.relation))]


def _exclusive_or(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    seqs = c.get("role_seqs") or []
    if len(seqs) < 2 or any(len(seq) != 1 for seq in seqs):
        raise ExportInputError(f"{c['id']}: exclusive-or over multi-role sequences is checked by GND only for its "
                               "exclusion half (unchecked otherwise); the rules programs refuse it")
    refs = [seq[0] for seq in seqs]
    helper, object_id = _plays(model, c, refs)
    var = f"${object_id}"
    atoms = [_seq_atom(model, seq, [var], c["id"]) for seq in seqs]
    facts = tuple(dict.fromkeys(atom.relation for atom in atoms))
    found = []
    for i in range(len(atoms)):
        for j in range(i + 1, len(atoms)):
            found.append(Requirement(c["id"], "exclusive-or", c["modality"], _quote(c), (atoms[i],),
                                     Check("absent", atom=atoms[j]), (var,), ("all", facts), facts,
                                     part=f"both_{i}_{j}"))
    found.append(Requirement(c["id"], "exclusive-or", c["modality"], _quote(c), (Atom(f"{object_id}_any", (var,)),),
                             Check("holds", atom=Atom(helper, (var,))), (var,), ("all", facts), facts,
                             part="none"))
    return found


def _frequency(model: _Model, c: dict[str, Any], fact_id: str) -> list[Requirement]:
    if c.get("scope", "internal") != "internal":
        raise ExportInputError(f"{c['id']}: external frequency is a later phase of the rules programs")
    keys = ModelIndex.constraint_roles(c)
    roles = [r["role_name"] for r in model.roles(fact_id)]
    if not keys or set(keys) - set(roles):
        raise ExportInputError(f"{c['id']}: frequency roles must belong to {fact_id}")
    others = [r for r in roles if r not in keys]
    if not others:
        raise ExportInputError(f"{c['id']}: frequency over every role counts duplicate rows; GND reports it")
    bound = c.get("bound") or {}
    atom = Atom(fact_id, tuple(f"${r}" for r in roles))
    count = Count(tuple(f"${r}" for r in others), tuple(f"${r}" for r in keys))
    witness = tuple(f"${r}" for r in keys)
    found = []
    for part, operator in (("min", ">="), ("max", "<=")):
        if bound.get(part) is not None:
            found.append(Requirement(c["id"], "frequency", c["modality"], _quote(c), (atom,),
                                     Check("compare", compare=Compare(operator, count, int(bound[part]))),
                                     witness, ("any", (fact_id,)), (fact_id,), part=part))
    if not found:
        raise ExportInputError(f"{c['id']}: a frequency bound needs min or max")
    return found


_RING_COMBINED = {"asymmetric-intransitive": ("asymmetric", "intransitive"),
                  "acyclic-intransitive": ("acyclic", "intransitive"),
                  "symmetric-irreflexive": ("symmetric", "irreflexive"),
                  "symmetric-intransitive": ("symmetric", "intransitive")}


def _ring(model: _Model, c: dict[str, Any], fact_id: str) -> list[Requirement]:
    roles = model.roles(fact_id)
    if len(roles) != 2 or len({model.primitive(r["object_type"]) for r in roles}) != 1:
        raise ExportInputError(f"{c['id']}: a ring constraint needs a binary fact type over one type")
    variant = c.get("variant")
    components = _RING_COMBINED.get(variant, (variant,))
    primitive = model.primitive(roles[0]["object_type"])
    F = lambda a, b: Atom(fact_id, (a, b))
    needs_reverse = {"asymmetric", "antisymmetric", "symmetric"} & set(components)
    if needs_reverse:
        model.helper(f"{fact_id}_reverse", [("a", primitive), ("b", primitive)], "reverse", fact=fact_id)
    if "acyclic" in components:
        model.helper(f"{fact_id}_closure", [("a", primitive), ("b", primitive)], "closure", fact=fact_id)
    R = lambda a, b: Atom(f"{fact_id}_reverse", (a, b))
    table = {
        "irreflexive": ((F("$x", "$y"),), Check("compare", compare=Compare("!=", "$x", "$y")), ("$x", "$y")),
        "asymmetric": ((F("$x", "$y"),), Check("absent", atom=R("$x", "$y")), ("$x", "$y")),
        "antisymmetric": ((F("$x", "$y"), R("$x", "$y")), Check("compare", compare=Compare("=", "$x", "$y")), ("$x", "$y")),
        "symmetric": ((F("$x", "$y"),), Check("holds", atom=R("$x", "$y")), ("$x", "$y")),
        "intransitive": ((F("$x", "$y"), F("$y", "$z")), Check("absent", atom=F("$x", "$z")), ("$x", "$y", "$z")),
        "transitive": ((F("$x", "$y"), F("$y", "$z")), Check("holds", atom=F("$x", "$z")), ("$x", "$y", "$z")),
        "acyclic": ((Atom(f"{fact_id}_closure", ("$x", "$y")),), Check("compare", compare=Compare("!=", "$x", "$y")), ("$x",)),
        "purely-reflexive": ((F("$x", "$y"),), Check("compare", compare=Compare("=", "$x", "$y")), ("$x", "$y")),
        "reflexive": ((F("$x", "$y"),), Check("holds", atom=F("$x", "$x")), ("$x",)),
    }
    found = []
    for component in components:
        if component not in table:
            raise ExportInputError(f"{c['id']}: ring variant {variant!r} is not supported")
        domain, check, witness = table[component]
        found.append(Requirement(c["id"], "ring", c["modality"], _quote(c), domain, check, witness,
                                 ("any", (fact_id,)), (fact_id,), part=component,
                                 info=(("components", list(components)), ("fact", fact_id),
                                       ("roles", [r["role_name"] for r in roles]))))
    return found


def _cardinality(model: _Model, c: dict[str, Any]) -> list[Requirement]:
    bound, scope = c.get("bound") or {}, c.get("scope")
    if scope == "object":
        var = f"${c['object_type']}"
        domain, facts = (Atom(f"{c['object_type']}_any", (var,)),), ()
    elif scope == "role":
        ref = c.get("role_ref") or {}
        var = f"${ref.get('role')}"
        atom = _seq_atom(model, [ref], [var], c["id"])
        domain, facts = (atom,), (atom.relation,)
    else:
        raise ExportInputError(f"{c['id']}: cardinality scope must be object or role")
    info = (("scope", scope), ("min", bound.get("min")), ("max", bound.get("max")))
    found = [Requirement(c["id"], "cardinality", c["modality"], _quote(c), domain, Check("none"), (var,),
                         ("any", facts), facts, part="members", listing=True, info=info)]
    for part, operator in (("min", ">="), ("max", "<=")):
        if bound.get(part) is not None:
            found.append(Requirement(c["id"], "cardinality", c["modality"], _quote(c), domain,
                                     Check("compare", compare=Compare(operator, Count((var,)), int(bound[part]))),
                                     (var,), ("any", facts), facts, part=part, info=info))
    return found



def _uniqueness(model: _Model, c: dict[str, Any], fact_id: str) -> Requirement | None:
    keys = ModelIndex.constraint_roles(c)
    roles = [r["role_name"] for r in model.roles(fact_id)]
    if not keys or set(keys) - set(roles):
        raise ExportInputError(f"{c.get('id')}: uniqueness roles must belong to {fact_id}")
    others = [r for r in roles if r not in keys]
    if not others:
        return None   # spanning: only exact duplicate rows could violate it; sets cannot hold them
    first = Atom(fact_id, tuple(f"${r}" if r in keys else f"${r}_1" for r in roles))
    second = Atom(fact_id, tuple(f"${r}" if r in keys else f"${r}_2" for r in roles))
    pairs = tuple((f"${r}_1", f"${r}_2") for r in others)
    return Requirement(c.get("id") or f"{fact_id}#uniqueness", "uniqueness", c["modality"], _quote(c),
                       (first, second), Check("same", pairs=pairs), _variables((first, second)),
                       ("any", (fact_id,)), (fact_id,))


def spanning_uniqueness(doc: dict[str, Any]) -> list[str]:
    """Uniqueness constraints over every role: only duplicate rows can break them (see the programs' header)."""
    model = _Model(doc)
    found = []
    for fact_id, fact in model.facts.items():
        roles = {r["role_name"] for r in model.roles(fact_id)}
        for index, c in enumerate(fact.get("constraints") or []):
            if c.get("type") == "uniqueness" and set(ModelIndex.constraint_roles(c)) == roles:
                found.append(c.get("id") or f"{fact_id}#{index}")
    return found


def _refuse_unsupported_model(doc: dict[str, Any]) -> None:
    """Constructs whose GND semantics these programs do not reproduce yet are refused by name."""
    if doc.get("operations"):
        raise ExportInputError("operations (plans) are a later phase of the rules programs")
    for obj in doc.get("object_types", []):
        if obj.get("primitive") == "DateTime":
            raise ExportInputError(f"object type {obj['id']!r} is a DateTime; times of day and offsets are a later "
                                   "phase of the rules programs ('DateTime')")
        if obj.get("subtype_of"):
            raise ExportInputError(f"object type {obj['id']!r} is a subtype; subtype universes are a later phase "
                                   "of the rules programs")
    for fact_id, fact in _Model(doc).facts.items():
        rule = fact.get("derivation_rule")
        if rule is None:
            continue
        if not isinstance(rule, dict):
            raise ExportInputError(f"fact type {fact_id!r} has an opaque (text) derivation rule; GND's treatment of "
                                   "those depends on the rest of the model, so the rules programs refuse them")
        if rule.get("aggregate") and fact.get("derivation") == "semiderived":
            raise ExportInputError(f"fact type {fact_id!r} is semiderived with an aggregate; GND's checker stops "
                                   "with an internal error on that combination, so there is no verdict to match")
        if (rule.get("aggregate") or {}).get("fn") == "avg":
            raise ExportInputError(f"fact type {fact_id!r} uses avg; exact averages are a later phase of the rules programs")
        for name in sorted(_functions(rule) - _ARITHMETIC):
            raise ExportInputError(f"fact type {fact_id!r} uses the function {name!r}; only "
                                   f"{', '.join(sorted(_ARITHMETIC))} are supported by the rules programs yet")


_ARITHMETIC = {"add", "sub", "mul", "neg", "abs"}


def _functions(value: Any) -> set[str]:
    """Every function name used anywhere in a derivation rule."""
    if isinstance(value, dict):
        found = {value["fn"]} if isinstance(value.get("fn"), str) and "args" in value else set()
        return found.union(*(_functions(v) for v in value.values()))
    if isinstance(value, list):
        return set().union(*(_functions(v) for v in value))
    return set()


def _rule_atoms(rule: dict[str, Any]) -> list[dict[str, Any]]:
    clauses = rule.get("clauses") or [rule]
    return [a for clause in clauses for a in (*clause.get("body", []), *clause.get("negate", []))]


def _strata(heads: dict[str, dict[str, Any]]) -> list[str]:
    """Derived heads ordered so every head comes after the heads it reads (recursive groups stay together)."""
    reads = {h: [a["fact_type"] for a in _rule_atoms(f["derivation_rule"]) if a["fact_type"] in heads] for h, f in heads.items()}
    order: list[str] = []
    index: dict[str, int] = {}
    low: dict[str, int] = {}
    stack: list[str] = []
    for root in heads:   # Tarjan's algorithm, iterative; components come out dependencies first
        if root in index:
            continue
        work = [(root, 0)]
        while work:
            node, i = work.pop()
            if i == 0:
                index[node] = low[node] = len(index)
                stack.append(node)
            if i < len(reads[node]):
                work.append((node, i + 1))
                nxt = reads[node][i]
                if nxt not in index:
                    work.append((nxt, 0))
                elif nxt in stack:
                    low[node] = min(low[node], index[nxt])
                continue
            if low[node] == index[node]:
                while True:
                    member = stack.pop()
                    order.append(member)
                    if member == node:
                        break
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[node])
    return order


def _unswap(model: _Model, atoms: list[Atom]) -> list[Atom]:
    """Rewrite R(y, x) as R_reverse(x, y) when an earlier atom already joined (x, y) in that order.

    PyRel 1.30.1 cannot compile a join whose second atom takes the same two variables swapped
    ("reordering loop did not reach a fixpoint"); reading through a reversed copy avoids it.
    """
    seen: set[tuple[str, str]] = set()
    out = []
    for atom in atoms:
        args = atom.args
        if len(args) == 2 and all(isinstance(a, str) and a.startswith("$") for a in args) and args[0] != args[1]:
            if (args[1], args[0]) in seen:
                primitive = _relation_roles(model, atom.relation)[0][1]
                reverse = model.helper(f"{atom.relation}_reverse", [("a", primitive), ("b", primitive)], "reverse",
                                       fact=atom.relation)
                atom = Atom(reverse, (args[1], args[0]))
            seen.add((atom.args[0], atom.args[1]))
        out.append(atom)
    return out


def _unswapped(model: _Model, req: Requirement) -> Requirement:
    atoms = _unswap(model, [*req.domain, *([req.check.atom] if req.check.atom else [])])
    domain = tuple(atoms[: len(req.domain)])
    check = req.check if not req.check.atom else Check(req.check.kind, atom=atoms[-1], compare=req.check.compare,
                                                       pairs=req.check.pairs)
    return Requirement(req.id, req.family, req.modality, req.quote, domain, check, req.witness, req.vacuous_when,
                       req.refs, req.part, req.listing, req.info)


def _derivation(model: _Model, head: str) -> list[Requirement]:
    """GND's derivation check as requirements: every computed fact is claimed; every claimed fact is computed."""
    fact = model.facts[head]
    kind = fact["derivation"]
    roles = [r["role_name"] for r in model.roles(head)]
    variables = tuple(f"${r}" for r in roles)
    claims = f"{head}_claimed" if kind == "semiderived" else head
    computed = Atom(f"{head}_derived", variables)
    claimed = Atom(claims, variables)
    info = (("head", head), ("roles", roles), ("kind", kind))
    quote = fact.get("reading", head)
    found = [Requirement(f"derivation:{head}", "derivation", "alethic", quote, (computed,), Check("holds", atom=claimed),
                         variables, ("all", ()), (head,), part="incomplete", info=info)]
    if kind == "derived":   # a semiderived claim may add facts of its own
        found.append(Requirement(f"derivation:{head}", "derivation", "alethic", quote, (claimed,),
                                 Check("holds", atom=computed), variables, ("all", ()), (head,), part="unsound", info=info))
    return found


def requirements(doc: dict[str, Any], model: _Model | None = None) -> list[Requirement]:
    """Lower every supported constraint to requirements, in model order. One walk for all families.

    Helper relations the lowering needs are registered on ``model``; pass the model you render with.
    """
    model = model if model is not None else _Model(doc)
    _refuse_unsupported_model(doc)
    found: list[Requirement] = []
    for fact_id, fact in model.facts.items():
        for index, c in enumerate(fact.get("constraints") or []):
            c = {**c, "id": c.get("id") or f"{fact_id}#{index}"}
            if c["type"] == "mandatory":
                found.append(_mandatory(model, c, fact_id))
            elif c["type"] == "uniqueness":
                if c.get("scope") == "external":
                    raise ExportInputError(f"{c['id']}: external uniqueness is a later phase of the rules programs")
                lowered = _uniqueness(model, c, fact_id)
                if lowered is not None:
                    found.append(lowered)
            elif c["type"] == "frequency":
                if c.get("scope") == "external":
                    raise ExportInputError(f"{c['id']}: external frequency is a later phase of the rules programs")
                found += _frequency(model, c, fact_id)
            elif c["type"] == "ring":
                found += _ring(model, c, fact_id)
            else:
                raise ExportInputError(f"{c['id']}: family {c['type']!r} is a later phase of the rules programs")
    for c in doc.get("constraints", []):
        family = c.get("type")
        if family == "guarded":
            found += _guarded(model, c)
        elif family == "subset":
            found.append(_subset(model, c))
        elif family == "value":
            found.append(_value(model, c))
        elif family == "mandatory-disjunctive":
            found += _mandatory_disjunctive(model, c)
        elif family == "equality":
            found += _equality(model, c)
        elif family == "exclusion":
            found += _exclusion(model, c)
        elif family == "exclusive-or":
            found += _exclusive_or(model, c)
        elif family == "cardinality":
            found += _cardinality(model, c)
        elif family in ("uniqueness", "frequency") and c.get("scope") == "external":
            raise ExportInputError(f"{c.get('id')}: external {family} is a later phase of the rules programs")
        elif family == "textual":
            model.unchecked.append({"id": c["id"], "modality": c["modality"], "expression": c["expression"]})
        else:
            raise ExportInputError(f"{c.get('id')}: family {family!r} is a later phase of the rules programs")
    for head in model.derived:
        found += _derivation(model, head)
    found = [_unswapped(model, r) for r in found]
    _refuse_name_collisions(model, found)
    return found


def _refuse_name_collisions(model: _Model, found: list[Requirement]) -> None:
    """Helper relations share the fact types' namespace, so a fact type may not take a generated name."""
    used = {atom.relation for r in found for atom in (*r.domain, *([r.check.atom] if r.check.atom else []))}
    generated = set(model.helpers) | set(model.derived_relations) | ({f"{o}_any" for o in model.objects} & used) | {
        f"{r.id}_allowed" for r in found if r.family == "value"}
    clash = sorted(generated & set(model.facts))
    if clash:
        raise ExportInputError(f"fact type {clash[0]!r} has the name of a relation the rules programs generate "
                               "(<fact>_reverse, <fact>_closure, <fact>_derived, <fact>_claimed, <id>_plays, <id>_allowed, <type>_any); "
                               "rename it")


# ---------------------------------------------------------------- rendering

def _ident(name: str, taken: set[str]) -> str:
    base = re.sub(r"[^0-9A-Za-z_]", "_", name.lstrip("$")) or "v"
    if base[0].isdigit():
        base = f"v_{base}"
    while keyword.iskeyword(base) or base in _RESERVED or base in taken:
        base = f"{base}_"
    return base


class _Names:
    def __init__(self, model: _Model):
        self.relations: dict[str, str] = {}
        taken: set[str] = set()
        for fact_id in model.facts:
            self.relations[fact_id] = _ident(fact_id, taken)
            taken.add(self.relations[fact_id])
        self.taken = taken
        self.vars: dict[str, str] = {}

    def relation(self, name: str) -> str:
        if name not in self.relations:
            self.relations[name] = _ident(name, self.taken)
            self.taken.add(self.relations[name])
        return self.relations[name]

    def var(self, name: str) -> str:
        """The same Python name for a variable everywhere; distinct variables never share one."""
        if name not in self.vars:
            self.vars[name] = _ident(name, self.taken)
            self.taken.add(self.vars[name])
        return self.vars[name]


def _types(model: _Model, req: Requirement) -> dict[str, str]:
    types: dict[str, str] = {}
    for atom in (*req.domain, *([req.check.atom] if req.check.atom else [])):
        roles = _relation_roles(model, atom.relation)
        for (role_name, primitive), arg in zip(roles, atom.args):
            if isinstance(arg, str) and arg.startswith("$"):
                types.setdefault(arg, primitive)
    return types


def _relation_roles(model: _Model, relation: str) -> list[tuple[str, str]]:
    if relation in model.helpers:
        return list(model.helpers[relation]["fields"])
    if relation in model.facts:
        return [(r["role_name"], model.role_type(relation, r["role_name"])) for r in model.roles(relation)]
    if relation in model.derived_relations:
        return _relation_roles(model, model.derived_relations[relation])
    if relation.endswith("_allowed"):
        constraint = next(c for c in model.doc.get("constraints", []) if f"{c.get('id')}_allowed" == relation)
        return [("value", model.primitive(constraint["object_type"]))]
    if relation.endswith("_any"):
        return [("member", model.primitive(relation[: -len("_any")]))]
    raise ExportInputError(f"unknown relation {relation!r}")


def _iso_date(value: Any) -> bool:
    """GND's date: exactly YYYY-MM-DD and a real Gregorian day (gnd.terms.valid_date)."""
    if not isinstance(value, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value):
        return False
    try:
        _dt.date.fromisoformat(value)
    except ValueError:
        return False
    return True


def _literal(value: Any, primitive: str) -> str:
    """A model literal as Python source for the PyRel type it fills (dates become datetime.date).

    GND compares a string that is not a strict YYYY-MM-DD date with dates as text, so it never equals one,
    and an ordered comparison with it is unchecked; the rules programs refuse such a literal by name.
    """
    if isinstance(value, dict) and set(value) == {"date"}:
        value, primitive = value["date"], "Date"
    if isinstance(value, dict) and set(value) == {"duration_days"}:
        return repr(value["duration_days"])
    if primitive == "Date" and isinstance(value, str):
        if not _iso_date(value):
            raise ExportInputError(f"the date literal {value!r} is not a YYYY-MM-DD date; GND compares it with dates "
                                   "as text, which the rules programs do not reproduce")
        year, month, day = (int(part) for part in value.split("-"))
        return f"datetime.date({year}, {month}, {day})"
    return repr(value)


def _term(arg: Any, names: _Names, model: _Model, primitive: str) -> str:
    if isinstance(arg, str) and arg.startswith("$"):
        return names.var(arg)
    if arg is None:
        return f"{primitive}.ref()"
    return _literal(arg, primitive)


def _atom_text(atom: Atom, names: _Names, model: _Model) -> str:
    roles = _relation_roles(model, atom.relation)
    args = ", ".join(_term(arg, names, model, primitive) for (_, primitive), arg in zip(roles, atom.args))
    return f"{names.relation(atom.relation)}({args})"


def _operand(value: Any, names: _Names) -> str:
    if isinstance(value, Count):
        text = f"aggregates.count({', '.join(names.var(v) for v in value.of)})"
        return text + (f".per({', '.join(names.var(v) for v in value.per)})" if value.per else "")
    if isinstance(value, dict) and value.get("fn") in _DATE_FUNCTIONS:
        when, length = (_operand(a, names) for a in value["args"])
        return f"std_date.{_DATE_FUNCTIONS[value['fn']]}({when}, days({length}))"
    if isinstance(value, dict) and "fn" in value:
        return _FN[value["fn"]].format(*(_operand(a, names) for a in value["args"]))
    if isinstance(value, dict):
        return _literal(value, "")
    return names.var(value) if isinstance(value, str) and value.startswith("$") else repr(value)


def _check_text(check: Check, names: _Names, model: _Model, *, negate: bool) -> list[str]:
    if check.kind == "holds":
        text = _atom_text(check.atom, names, model)
        return [f"not_({text})" if negate else text]
    if check.kind == "absent":
        text = _atom_text(check.atom, names, model)
        return [text if negate else f"not_({text})"]
    if check.kind == "compare":
        op = _NEGATED[check.compare.operator] if negate else check.compare.operator
        return [f"{_operand(check.compare.left, names)} {_PYOP[op]} {_operand(check.compare.right, names)}"]
    if check.kind == "none":
        return []
    if check.kind == "same":
        if negate:
            if len(check.pairs) == 1:
                a, b = check.pairs[0]
                return [f"{names.var(a)} != {names.var(b)}"]
            inner = ", ".join(f"{names.var(a)} == {names.var(b)}" for a, b in check.pairs)
            return [f"not_({inner})"]
        return [f"{names.var(a)} == {names.var(b)}" for a, b in check.pairs]
    raise ExportInputError(f"unknown check kind {check.kind}")


def require_text(req: Requirement, names: _Names, model: _Model) -> str:
    if req.listing:
        return f"(listing for the report) {denial_text(req, names, model)}"
    domain = ", ".join(_atom_text(a, names, model) for a in req.domain)
    if req.family == "cardinality" and req.part == "min":
        # no outer domain: with none, the rule still applies to an empty universe, which GND fails
        count = _operand(req.check.compare.left, names)
        return f"m.require({count}.where({domain}) >= {req.check.compare.right!r})"
    check = ", ".join(_check_text(req.check, names, model, negate=False))
    return f"m.where({domain}).require({check})"


def denial_text(req: Requirement, names: _Names, model: _Model) -> str:
    parts = [*(_atom_text(a, names, model) for a in req.domain), *_check_text(req.check, names, model, negate=True)]
    selected = ", ".join(names.var(v) for v in req.witness)
    return f"m.where({', '.join(parts)}).select({selected})"


def _universes(model: _Model, reqs: list[Requirement], names: _Names) -> list[str]:
    wanted = sorted({a.relation[: -len("_any")] for r in reqs for a in r.domain if a.relation.endswith("_any")})
    lines = []
    for object_id in wanted:
        primitive = model.primitive(object_id)
        rel = names.relation(f"{object_id}_any")
        lines.append(f"    # every {object_id} mentioned in any fact, plus the population's instances roster")
        lines.append(f"    {rel} = m.Relationship(fields=[Field('member', {primitive})], short_name='{object_id}_any')")
        lines.append(f"    h_x = {primitive}.ref()")
        for fact_id, role_name in model.plays(object_id):
            args = ", ".join("h_x" if r["role_name"] == role_name else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                             for r in model.roles(fact_id))
            lines.append(f"    m.where({names.relation(fact_id)}({args})).define({rel}(h_x))")
        rosters = _rosters(model, object_id)
        lines.append(f"    for value in [v for key in {rosters!r} for v in instances.get(key, [])]:")
        lines.append(f"        m.define({rel}({'datetime.date.fromisoformat(value)' if primitive == 'Date' else 'value'}))")
    return lines


def _allowed(model: _Model, reqs: list[Requirement], names: _Names) -> list[str]:
    lines = []
    for c in model.doc.get("constraints", []):
        if c.get("type") == "value" and "allowed" in c and any(r.id == c["id"] for r in reqs):
            rel = names.relation(f"{c['id']}_allowed")
            primitive = model.primitive(c["object_type"])
            lines.append(f"    # {c['id']}: the declared list of allowed values")
            lines.append(f"    {rel} = m.Relationship(fields=[Field('value', {primitive})], short_name='{c['id']}_allowed')")
            # a malformed date in the list can never equal a date value, as in GND: it is left out
            listed = [v for v in c["allowed"] if primitive != "Date" or _iso_date(v)]
            values = ", ".join(_literal(v, primitive) for v in listed)
            lines.append(f"    m.define(*[{rel}(v) for v in [{values}]])")
    return lines


def _helpers(model: _Model, names: _Names, kinds: tuple[str, ...] | None = None) -> list[str]:
    """Render registered helper relations (reverses, closures, role-player sets, ranges), each once."""
    lines = []
    for name, spec in model.helpers.items():
        if (kinds is not None and spec["kind"] not in kinds) or spec.get("rendered"):
            continue
        spec["rendered"] = True
        rel = names.relation(name)
        fields = ", ".join(f"Field({field!r}, {primitive})" for field, primitive in spec["fields"])
        lines.append(f"    {rel} = m.Relationship(fields=[{fields}], short_name={name!r})")
        if spec["kind"] == "reverse":
            primitive = spec["fields"][0][1]
            fact = names.relation(spec["fact"])
            lines.insert(-1, f"    # {spec['fact']} read backwards (joining a relation with itself, swapped, trips a PyRel 1.30.1 bug)")
            lines.append(f"    h_a, h_b = {primitive}.ref(), {primitive}.ref()")
            lines.append(f"    m.where({fact}(h_a, h_b)).define({rel}(h_b, h_a))")
        elif spec["kind"] == "closure":
            primitive = spec["fields"][0][1]
            fact = names.relation(spec["fact"])
            lines.insert(-1, f"    # every pair connected by a chain of {spec['fact']} facts (recursive)")
            lines.append(f"    h_a, h_b, h_c = {primitive}.ref(), {primitive}.ref(), {primitive}.ref()")
            lines.append(f"    m.where({fact}(h_a, h_b)).define({rel}(h_a, h_b))")
            lines.append(f"    m.where({rel}(h_a, h_b), {fact}(h_b, h_c)).define({rel}(h_a, h_c))")
        elif spec["kind"] == "plays":
            lines.insert(-1, f"    # every instance that plays one of the roles {[f'{f}.{r}' for f, r in spec['refs']]}")
            for fact_id, role_name in spec["refs"]:
                args = ", ".join("h_x" if r["role_name"] == role_name else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                                 for r in model.roles(fact_id))
                lines.append(f"    h_x = {spec['fields'][0][1]}.ref()")
                lines.append(f"    m.where({names.relation(fact_id)}({args})).define({rel}(h_x))")
        elif spec["kind"] == "ranges":
            universe = names.relation(f"{spec['object_type']}_any")
            lines.insert(-1, f"    # the values of {spec['object_type']} that fall inside a declared range")
            for bounds in spec["ranges"]:
                conditions = []
                kind = spec["fields"][0][1]
                if bounds.get("min") is not None:
                    conditions.append(f"h_x {'>=' if bounds.get('min_inclusive', True) else '>'} {_literal(bounds['min'], kind)}")
                if bounds.get("max") is not None:
                    conditions.append(f"h_x {'<=' if bounds.get('max_inclusive', True) else '<'} {_literal(bounds['max'], kind)}")
                lines.append(f"    h_x = {spec['fields'][0][1]}.ref()")
                lines.append(f"    m.where({universe}(h_x){''.join(', ' + c for c in conditions)}).define({rel}(h_x))")
        else:
            raise ExportInputError(f"unknown helper kind {spec['kind']}")
    return lines


def _relations(model: _Model, names: _Names) -> list[str]:
    lines = []
    for fact_id, fact in model.facts.items():
        fields = ", ".join(f"Field({r['role_name']!r}, {model.role_type(fact_id, r['role_name'])})"
                           for r in model.roles(fact_id))
        lines.append(f"    # {fact.get('reading', fact_id)}")
        lines.append(f"    {names.relation(fact_id)} = m.Relationship(fields=[{fields}], short_name={fact_id!r})")
        roles = tuple(r["role_name"] for r in model.roles(fact_id))
        target = fact_id
        if fact.get("derivation") == "semiderived" and fact_id in model.derived:
            target = f"{fact_id}_claimed"
            lines.append(f"    # the claimed {fact_id} facts; constraints read the computed ones (as GND does)")
            lines.append(f"    {names.relation(target)} = m.Relationship(fields=[{fields}], short_name={target!r})")
        dates = tuple(r for r in roles if model.raw_role_type(fact_id, r) == "Date")
        lines.append(f"    load(m, {names.relation(target)}, facts.get({fact_id!r}, []), {roles!r}"
                     + (f", dates={dates!r})" if dates else ")"))
    return lines


def _clauses(rule: dict[str, Any]) -> list[dict[str, Any]]:
    """One entry per clause, with the root's where and aggregate applied to each (GND's union of clauses)."""
    clauses = rule.get("clauses") or [rule]
    return [{"body": c.get("body", []), "negate": c.get("negate", []),
             "where": [*c.get("where", []), *rule.get("where", [])] if "clauses" in rule else c.get("where", []),
             "head": c.get("head") or rule["head"], "aggregate": rule.get("aggregate")} for c in clauses]


_FN = {"add": "({} + {})", "sub": "({} - {})", "mul": "({} * {})", "neg": "(-{})", "abs": "std_math.abs({})"}


def _expr(term: Any, names: _Names) -> str:
    if isinstance(term, dict):
        args = [_expr(a, names) for a in term["args"]]
        if term["fn"] == "add" and len(args) > 2:
            return "(" + " + ".join(args) + ")"
        return _FN[term["fn"]].format(*args)
    return names.var(term) if isinstance(term, str) and term.startswith("$") else repr(term)


def _term_variables(term: Any) -> list[str]:
    if isinstance(term, dict):
        return [v for a in term.get("args", []) for v in _term_variables(a)]
    return [term] if isinstance(term, str) and term.startswith("$") else []


def _refuse_inexact(head: str, clause: dict[str, Any], types: dict[str, str]) -> None:
    """GND computes add, sub, mul, neg and abs as exact rationals; PyRel uses binary floats for Float values.

    So arithmetic is admitted only over Integer variables and integer literals, and a where comparison
    may not mix a Float variable with an Integer one (PyRel 1.30.1 cannot ground that comparison).
    """
    terms = [*[t for c in clause["where"] for t in (c["left"], c["right"])], *clause["head"].values()]
    for term in terms:
        if not isinstance(term, dict):
            continue
        floats = [v for v in _term_variables(term) if types.get(v) == "Float"]
        literals = [a for a in _term_literals(term) if isinstance(a, float) and not a.is_integer()]
        if floats or literals:
            raise ExportInputError(f"{head}: arithmetic on Float values ({', '.join(map(str, floats + literals))}) is exact "
                                   "in GND and binary in PyRel; the rules programs refuse it (later phase)")
    for comparison in clause["where"]:
        kinds = {types.get(t) for t in (comparison["left"], comparison["right"]) if isinstance(t, str) and t.startswith("$")}
        if kinds == {"Float", "Integer"}:
            raise ExportInputError(f"{head}: comparing a Float variable with an Integer variable is a later phase of the "
                                   "rules programs")


def _term_literals(term: Any) -> list[Any]:
    if isinstance(term, dict):
        return [v for a in term.get("args", []) for v in _term_literals(a)]
    return [] if isinstance(term, str) and term.startswith("$") else [term]


def _derived_relation(model: _Model, fact_id: str) -> str:
    """Derivation bodies read the computed relation of a derived head, never its claim (GND's strata)."""
    return f"{fact_id}_derived" if fact_id in model.derived else fact_id


def _derivations(model: _Model, names: _Names, target: str) -> list[str]:
    if not model.derived:
        return []
    lines = ["\n    # ---- derived facts: computed from their rules, lower strata first"]
    for head in model.derived:
        fields = ", ".join(f"Field({r['role_name']!r}, {model.role_type(head, r['role_name'])})" for r in model.roles(head))
        rel = names.relation(f"{head}_derived")
        lines.append(f"    {rel} = m.Relationship(fields=[{fields}], short_name='{head}_derived')")
    clauses = []
    for head in model.derived:
        fact = model.facts[head]
        clauses.append(f"    # {head} ({fact['derivation']}): {fact.get('reading', head)}")
        for clause in _clauses(fact["derivation_rule"]):
            clauses += _clause_lines(model, names, head, clause)
    lines += _helpers(model, names, kinds=("reverse",))   # registered while lowering the clauses
    lines += clauses
    for head in (h for h in model.derived if model.facts[h]["derivation"] == "semiderived"):
        # constraints read a semiderived head as computed; defined only after every clause exists
        args = ", ".join(f"{model.role_type(head, r['role_name'])}.ref()" for r in model.roles(head))
        lines.append(f"    h_row = [{args}]")
        lines.append(f"    m.where({names.relation(head + '_derived')}(*h_row)).define({names.relation(head)}(*h_row))")
        if target == "duckdb":   # the report reads it for vacuity and for witnesses built from facts
            lines.append(f"    found['computed:{head}'] = rows(m.where({names.relation(head)}(*h_row)).select(*h_row))")
    return lines

def _clause_lines(model: _Model, names: _Names, head: str, clause: dict[str, Any]) -> list[str]:
    types: dict[str, str] = {}
    atoms = []
    for pattern in clause["body"]:
        atom = _atom(model, pattern)
        for (role_name, primitive), arg in zip(_relation_roles(model, atom.relation), atom.args):
            if isinstance(arg, str) and arg.startswith("$"):
                types.setdefault(arg, primitive)
        atoms.append(Atom(_derived_relation(model, atom.relation), atom.args))
    negated = [_atom(model, pattern) for pattern in clause["negate"]]
    negated = [Atom(_derived_relation(model, a.relation), a.args) for a in negated]
    unswapped = _unswap(model, atoms + negated)
    atoms, negated = unswapped[: len(atoms)], unswapped[len(atoms):]
    _refuse_inexact(head, clause, types)
    lines = []
    if types:
        lines.append(_declare(sorted(types), types, names))
    parts = [_atom_text(a, names, model) for a in atoms] + [f"not_({_atom_text(a, names, model)})" for a in negated]
    aggregate = clause["aggregate"]
    head_terms = [clause["head"][r["role_name"]] for r in model.roles(head)]
    if aggregate:
        of, over, bound = aggregate["of"], list(aggregate["over"]), aggregate["as"]
        if not (isinstance(of, str) and of.startswith("$")):
            raise ExportInputError(f"{head}: an aggregate of a computed term is a later phase of the rules programs")
        group = [v for t in head_terms for v in _term_variables(t) if v != bound]
        group = list(dict.fromkeys(group))
        counted = list(dict.fromkeys([*over, of])) if aggregate["fn"] == "count" else (
            [*[v for v in over if v != of], of] if aggregate["fn"] == "sum" else [of])
        text = f"aggregates.{aggregate['fn']}({', '.join(names.var(v) for v in counted)})"
        if group:
            text += f".per({', '.join(names.var(v) for v in group)})"
        lines.append(f"    {names.var(bound)} = {text}   # GND counts each distinct ({', '.join([*over, of])}) once")
    for comparison in clause["where"]:
        parts.append(f"{_expr(comparison['left'], names)} {_PYOP[comparison['operator']]} {_expr(comparison['right'], names)}")
    head_args = ", ".join(_expr(t, names) for t in head_terms)
    lines.append(f"    m.where({', '.join(parts)}).define({names.relation(head + '_derived')}({head_args}))")
    return lines


def _declare(variables, types, names) -> str:
    left = ", ".join(names.var(v) for v in variables)
    right = ", ".join(f"{types[v]}.ref()" for v in variables)
    return f"    {left} = {right}"


def _rule_block(req: Requirement, model: _Model, names: _Names, target: str) -> list[str]:
    strength = "must" if req.modality == "alethic" else "should"
    types = _types(model, req)
    variables = sorted(types)
    lines = [f"    # {req.id} ({strength}): {req.quote}"]
    if variables:
        lines.append(_declare(variables, types, names))
    key = f"{req.id}::{req.part}" if req.part else req.id
    if target == "lqp":
        if req.listing:
            return lines[:1] + ["    #   (the DuckDB version also lists the members to report them; nothing to require)"]
        lines.append(f"    {require_text(req, names, model)}")
    elif req.listing:
        lines.append("    #   listing the members the report names when the count is out of bounds")
        lines.append(f"    found[{key!r}] = rows({denial_text(req, names, model)})")
    else:
        lines.append(f"    #   rule:      {require_text(req, names, model)}")
        lines.append("    #   violation: the facts that match the domain and fail the check")
        query = f"rows({denial_text(req, names, model)})"
        if dict(req.info).get("temporal"):   # violations come from bindings; with none, skip the date arithmetic
            query = f"{query} if found[{req.id + '::bindings'!r}] else []"
        lines.append(f"    found[{key!r}] = {query}")
    return lines


def _require_count(req: Requirement) -> int:
    """PyRel compiles each statement passed to require() into its own Require node."""
    if req.listing:
        return 0
    return len(req.check.pairs) if req.check.kind == "same" else 1


def _rules_table(reqs: list[Requirement]) -> str:
    rows = [{"id": r.id, "part": r.part, "family": r.family, "modality": r.modality, "witness": list(r.witness),
             "vacuous_when": [r.vacuous_when[0], list(r.vacuous_when[1])], "requires": _require_count(r),
             "info": dict(r.info)}
            for r in reqs]
    return json.dumps(rows, indent=1)


_DUCKDB_MAIN = '''

GROUPED = ('mandatory-disjunctive', 'equality', 'exclusion', 'exclusive-or', 'frequency', 'ring', 'cardinality',
           'derivation')


def scalar_key(value):
    """GND's canonical order for one value: booleans, then numbers by value, then strings, then null."""
    if isinstance(value, bool):
        return (0, int(value), '')
    if isinstance(value, (int, float)):
        return (1, Fraction(value), '')
    if isinstance(value, str):
        return (2, 0, value)
    return (3, 0, '')


def canon(value):
    """Rows compare value by value, a shorter row first when one is a prefix of the other."""
    return tuple(scalar_key(v) for v in value) if isinstance(value, (list, tuple)) else scalar_key(value)


def cycle_witness(pairs):
    """The one cycle GND reports: depth-first from each node in canonical order, successors in fact order.

    The requirement (closure x != y) decides whether the rule is broken; this only picks the same
    witness GND prints (semantic_spec.ring_cycle_witness).
    """
    nodes = sorted({v for pair in pairs for v in pair}, key=scalar_key)
    index = {json.dumps(v): i for i, v in enumerate(nodes)}
    successors = [[] for _ in nodes]
    for a, b in pairs:
        successors[index[json.dumps(a)]].append(index[json.dumps(b)])
    colour, parent = [0] * len(nodes), [-1] * len(nodes)
    for start in range(len(nodes)):
        if colour[start]:
            continue
        colour[start] = 1
        stack = [(start, 0)]
        while stack:
            node, next_index = stack[-1]
            if next_index >= len(successors[node]):
                colour[node] = 2
                stack.pop()
                continue
            stack[-1] = (node, next_index + 1)
            successor = successors[node][next_index]
            if colour[successor] == 0:
                colour[successor], parent[successor] = 1, node
                stack.append((successor, 0))
            elif colour[successor] == 1:
                path = [node]
                while path[-1] != successor:
                    path.append(parent[path[-1]])
                return [nodes[i] for i in reversed(path)] + [nodes[successor]]
    return []


def identity_token(value):
    """GND's identity token for one value (representation-format.md), compared as UTF-8 bytes."""
    if isinstance(value, bool):
        payload = ['boolean', value]
    elif isinstance(value, int):
        payload = ['number', [value, 1]]
    elif isinstance(value, float):
        payload = ['number', list(value.as_integer_ratio())]
    else:
        payload = ['string', value]
    return json.dumps(payload, ensure_ascii=False, separators=(',', ':')).encode()


def first_row(rows_, roles):
    """The one row GND shows for a derivation finding: the least by identity tokens, as {role: value}."""
    row = min(rows_, key=lambda r: tuple(identity_token(v) for v in r))
    return dict(zip(roles, row))


def distinct_sorted(rows_):
    seen = {json.dumps(list(row)): list(row) for row in rows_}
    return sorted(seen.values(), key=canon)


def judge(parts, found, facts):
    """One constraint made of several requirements: (status, witness list) in GND's shape."""
    head = parts[0]
    family, info = head['family'], head['info']
    rows_of = {part['part']: found[f"{part['id']}::{part['part']}" if part['part'] else part['id']] for part in parts}
    if family == 'cardinality':
        members = [row[0] for row in distinct_sorted(rows_of['members'])]
        if not members:
            if info.get('min'):
                return 'fail', []
            return 'vacuous', None
        # the count requirements decide; the member listing supplies GND's witness (every member)
        low, high = bool(rows_of.get('min')), bool(rows_of.get('max'))
        return ('fail', sorted(members, key=canon)) if low or high else ('pass', None)
    if family == 'derivation':
        # GND reports at most one missing and one extra fact, the first of each
        witness = [{label: first_row(rows_of[part], info['roles'])}
                   for part, label in (('incomplete', 'missing'), ('unsound', 'extra')) if rows_of.get(part)]
        return ('fail', witness) if witness else ('pass', None)
    if family == 'mandatory-disjunctive':
        witness = sorted({row[0] for row in rows_of['']}, key=canon)
    elif family == 'equality':
        witness = distinct_sorted(rows_of['a_not_b']) + distinct_sorted(rows_of['b_not_a'])
    elif family == 'exclusion':
        witness = distinct_sorted(rows_of[''])
    elif family == 'exclusive-or':
        both = [row for name, rows_ in rows_of.items() if name.startswith('both_') for row in rows_]
        witness = distinct_sorted(both) + distinct_sorted(rows_of['none'])
    elif family == 'frequency':
        witness = distinct_sorted(rows_of.get('min', []) + rows_of.get('max', []))
    elif family == 'ring':
        witness = []
        for component in info['components']:
            component_rows = rows_of[component]
            if component == 'acyclic':
                if component_rows:
                    first, second = info['roles']
                    if info['fact'] in SEMIDERIVED:   # the constraint reads the computed facts
                        pairs = [tuple(row) for row in found.get(f"computed:{info['fact']}", [])]
                    else:
                        pairs = [(row[first], row[second]) for row in facts.get(info['fact'], [])]
                    witness.append(cycle_witness(pairs))
            else:
                witness += distinct_sorted(component_rows)
    else:
        raise ValueError(f'unknown grouped family {family}')
    return ('fail', witness) if witness else ('pass', None)


def report(population, found):
    """One line per rule. Exit 1 on any must-rule violation, else 4 if a must-rule is not checked,
    else 2 if a rule was vacuous, else 0.

    GND's checker reads every fact list, covered or not; only mandatory roles treat a fact
    list missing from the input's covers as unknown, and report the rule vacuous.
    """
    facts = population['facts']
    instances = population.get('instances', {})
    covers = set(population['population']['covers'])
    violated = vacuous = unchecked = False
    groups = {}
    for rule in RULES:
        groups.setdefault(rule['id'], []).append(rule)
    for name, parts in groups.items():
        rule = parts[0]
        if rule['family'] == 'derivation' and rule['info']['head'] not in covers:
            print(f'{name}  not checked  (no claim: {rule["info"]["head"]} is not in covers)')
            unchecked = True
            continue
        mode, lists = rule['vacuous_when']
        # a semiderived fact type is read as computed, so its emptiness is the computed relation's
        empty = [not (found.get(f'computed:{ref}') if ref in SEMIDERIVED else facts.get(ref)) for ref in lists]
        if mode == 'universe':   # no facts and no roster members: nothing to check
            nothing = all(empty) and not any(instances.get(key) for key in rule['info']['rosters'])
        else:
            nothing = bool(lists) and (any(empty) if mode == 'any' else all(empty))
        uncovered = [ref for ref in rule['info'].get('uncovered_vacuous', []) if ref not in covers]
        if uncovered or nothing:
            print(f'{name}  vacuous  (no facts for it to apply to)')
            vacuous = True
            continue
        status = 'violated' if rule['modality'] == 'alethic' else 'warning'
        if rule['info'].get('temporal'):
            reason = date_reason(rule, found[f'{name}::bindings'])
            if reason:
                print(f'{name}  not checked  ({reason})')
                unchecked = unchecked or rule['modality'] == 'alethic'
                continue
        if rule['family'] in GROUPED:
            verdict, witness = judge(parts, found, facts)
            if verdict == 'vacuous':
                print(f'{name}  vacuous  (no facts for it to apply to)')
                vacuous = True
            elif verdict == 'pass':
                print(f'{name}  OK')
            else:
                print(f'{name}  {status}  {json.dumps(witness)}')
                violated = violated or status == 'violated'
            continue
        hits = witnesses(rule, found[name])
        if not hits:
            print(f'{name}  OK')
        status = 'violated' if rule['modality'] == 'alethic' else 'warning'
        for hit in hits:
            print(f'{name}  {status}  {json.dumps(hit, sort_keys=True)}')
        violated = violated or (bool(hits) and status == 'violated')
    for rule in UNCHECKED:
        print(f"{rule['id']}  not checked  (textual rule: {rule['expression']})")
        unchecked = unchecked or rule['modality'] == 'alethic'
    return 1 if violated else 4 if unchecked else 2 if vacuous else 0


def date_reason(rule, bindings):
    """Why GND would leave a rule with date_add/date_sub unchecked, or None.

    GND evaluates at most 10,000 date functions per rule, and a computed date must stay within
    0001-01-01..9999-12-31. The requirement decides the rule only when both hold for every binding.
    """
    functions = rule['info']['temporal']
    if len(bindings) * len(functions) > 10_000:
        return 'term:temporal-work-limit'
    names = rule['witness']
    for row in bindings:
        values = dict(zip(names, row))
        for function, when, length in functions:
            day = values[when] if isinstance(when, str) and when.startswith('$') else when['date']
            span = values[length] if isinstance(length, str) else length['duration_days']
            ordinal = datetime.date.fromisoformat(day).toordinal() + (span if function == 'date_add' else -span)
            if not 1 <= ordinal <= datetime.date.max.toordinal():
                return 'term:date-out-of-range'
    return None


def witnesses(rule, found):
    """Shape each violating row the way GND's checker reports it."""
    names = rule['witness']
    if rule['family'] == 'guarded':
        return [dict(zip(names, row)) for row in found]
    if rule['family'] in ('mandatory', 'subset'):
        return [list(row) for row in found]
    if rule['family'] == 'value':
        return [row[0] for row in found]
    if rule['family'] == 'uniqueness':
        # GND reports one verdict per rule listing every fact that shares a key with another.
        facts_seen = {}
        for row in found:
            values = dict(zip(names, row))
            key = {k[1:]: v for k, v in values.items() if not re.search(r'_[12]$', k)}
            for suffix in ('_1', '_2'):
                fact = dict(key)
                fact.update({k[1:-2]: v for k, v in values.items() if k.endswith(suffix)})
                facts_seen[json.dumps(fact, sort_keys=True)] = fact
        return [[facts_seen[k] for k in sorted(facts_seen)]] if facts_seen else []
    return [list(row) for row in found]


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if len(argv) != 1:
        print('usage: python THIS_FILE POPULATION.json', file=sys.stderr)
        return 64
    try:
        population = read_population(argv[0])
    except (OSError, ValueError, KeyError, TypeError) as error:
        print(f'{argv[0]}: not a readable population ({type(error).__name__}: {error})', file=sys.stderr)
        return 3
    try:
        with tempfile.TemporaryDirectory(prefix='gnd-rules-') as directory:
            os.environ['RAI_BUILD_DIR'] = directory   # explicit local build state; no remote discovery
            from relationalai.config import Config
            config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                            default_connection='local',
                            deployment={'schema': SCHEMA, 'auto_deploy': True})
            found = build(population, config)
    except Exception as error:  # noqa: BLE001 -- a crash must never read as a rule violation (exit 1)
        print(f'PyRel execution failed: {type(error).__name__}: {error}', file=sys.stderr)
        return 70
    return report(population, found)


if __name__ == '__main__':
    raise SystemExit(main())
'''

_LQP_MAIN = '''

def main(argv=None):
    import argparse
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument('population', nargs='?', help='population JSON to load into the engine')
    parser.add_argument('--compile', action='store_true',
                        help='compile the requirements locally and print them; checks nothing')
    parser.add_argument('--connection', help='a RelationalAI engine connection named in your raiconfig.yaml')
    args = parser.parse_args(argv)
    if args.compile:
        return compile_only()
    if not args.population or not args.connection:
        parser.error('enforcing requirements needs a population and --connection NAME '
                     '(a RelationalAI engine); DuckDB does not enforce require. '
                     'Use --compile to inspect, or the duckdb version of this program to check locally.')
    population = read_population(args.population)
    import warnings
    from relationalai.config import create_config
    # The direct LQP compiler lowers `where(D).require(C)` to `D and not C => Error("Requirements not met", ...)`.
    config = create_config(default_connection=args.connection,
                           compiler={'require_mode': 'report'},
                           reasoners={'logic': {'use_lqp': True, 'lqp': {'compiler': 'direct'}}})
    try:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter('always')
            m, probe = build(population, config)
            probe()   # any query makes the engine evaluate the model, requirements included
    except Exception as error:  # noqa: BLE001 -- a crash must never read as a rule violation (exit 1)
        print(f'PyRel execution failed: {type(error).__name__}: {error}', file=sys.stderr)
        return 70
    problems = [w for w in caught if 'Requirements not met' in str(w.message)]
    for w in problems:
        print(f'violated  {w.message}')
    print(f'{len(problems)} requirement violation report(s) from the engine')
    return 1 if problems else 0


def compile_only():
    """Show how PyRel compiled each requirement. Uses PyRel's front-end compiler (internal API, pinned version)."""
    from relationalai.config import Config
    from relationalai.semantics.frontend.front_compiler import FrontCompiler
    from relationalai.semantics.metamodel.rewriter import Walker
    with tempfile.TemporaryDirectory(prefix='gnd-rules-') as directory:
        os.environ['RAI_BUILD_DIR'] = directory
        config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                        default_connection='local', deployment={'schema': SCHEMA, 'auto_deploy': True})
        m, _ = build({'facts': {}, 'population': {}}, config)
        compiled = FrontCompiler(m).compile_model(m)

    class Requires(Walker):
        def __init__(self):
            super().__init__()
            self.found = []

        def require(self, node):
            self.found.append(node)

    walker = Requires()
    walker(compiled.root)
    expected = sum(rule['requires'] for rule in RULES)
    print(f'{len(walker.found)} requirements compiled for {len(RULES)} rules (expected {expected})')
    for node in walker.found:
        print(' '.join(str(node).split()))
    return 0 if len(walker.found) == expected else 1


if __name__ == '__main__':
    raise SystemExit(main())
'''


def _roster_types(model: _Model) -> dict[str, str]:
    """The primitive each instances roster holds; rosters are checked like fact cells, as GND checks them."""
    found = {}
    for object_id in model.objects:
        try:
            found[object_id] = model.raw_primitive(object_id)
        except ExportInputError:
            continue
    return found


def _bind_reference(loaded: Any, model_path: Path) -> dict[str, Any] | None:
    """Bind the model's reference populations with GND's own binder; the program embeds what it bound.

    GND verifies each file's SHA-256, ownership and identity before checking; a refusal here stops the
    export by name. The snapshot is taken now, so a later edit to a reference file needs a new export.
    """
    declared = list(getattr(loaded, "reference_populations", None) or [])
    if not declared:
        return None
    from gnd.artifacts import ArtifactError
    from gnd.model import ReferenceInputError
    from gnd.references import bind_references
    try:
        context = bind_references(loaded, root=model_path.parent)
    except (ReferenceInputError, ArtifactError, OSError, ValueError) as error:
        raise ExportInputError(f"reference population: {error}") from error
    facts: dict[str, list[dict[str, Any]]] = {}
    instances: dict[str, list[Any]] = {}
    covers: list[str] = []
    for population in context._populations:   # the validated snapshots GND itself checks against
        for fact_type, rows in population.facts.items():
            facts[fact_type] = [dict(row) for row in rows]
        for object_type, values in population.instances.items():
            instances.setdefault(object_type, []).extend(values)
        covers += [f for f in population.covers if f not in covers]
    return {"files": [[d["id"], d["path"], d["sha256"]] for d in declared],
            "owned": sorted(fact_type for fact_type, _ in context._owners),
            "facts": facts, "instances": instances, "covers": covers}


def render(model_path: Path, target: str) -> str:
    if target not in TARGETS:
        raise ExportInputError(f"target must be one of {TARGETS}")
    raw = Path(model_path).read_bytes()
    from gnd.model import ReferenceInputError
    try:
        loaded = load_model_bytes(raw, source=str(model_path))
    except (ModelLoadError, ModelValidationError, ReferenceInputError) as error:
        raise ExportInputError(f"invalid model: {error}") from error
    doc = _parse_document(raw.decode("utf-8"))
    model = _Model(doc)
    reference = _bind_reference(loaded, Path(model_path))   # GND binds references before it checks anything
    reqs = requirements(doc, model)
    names = _Names(model)
    spanning = spanning_uniqueness(doc)
    spanning_note = (f"Spanning uniqueness ({', '.join(spanning)}) can only be broken by duplicate rows. PyRel\n"
                     "relations are sets, so the input is refused if it repeats a fact; GND reports those.\n\n"
                     if spanning else "")
    schema = re.sub(r"[^0-9a-z_]", "_", str(doc.get("model_id", "gnd_rules")).lower())[-40:].strip("_") or "gnd_rules"
    if target == "lqp":
        header = (f'"""{doc.get("model_id")}: the model\'s rules as PyRel requirements (LQP version).\n\n'
                  "Each rule below is an executable `m.where(...).require(...)`. A RelationalAI engine\n"
                  "(the logic reasoner, direct LQP compiler) enforces requirements and reports every\n"
                  "violation. The local DuckDB backend does NOT enforce require, so run this with\n"
                  "--connection NAME, or use --compile to see how PyRel compiled each requirement.\n"
                  "The duckdb version of this program checks the same rules on your laptop, and also\n"
                  "reports vacuous rules and exit bands, which this version does not. It also decides when\n"
                  "GND would leave a date rule unchecked (a date outside years 1 to 9999, or more than\n"
                  "10,000 date calculations); an engine running this version reports such a rule as broken.\n\n"
                  "ENGINE-UNVERIFIED: GND's tests compile this program but have not run --connection\n"
                  "against an engine.\n\n"
                  "Generated by `gnd export pyrel --rules lqp`. Do not edit; change the model instead.\n"
                  '"""\n')
    else:
        header = (f'"""{doc.get("model_id")}: the model\'s rules as PyRel requirements (DuckDB version).\n\n'
                  "Each rule is shown as the requirement it is, `m.where(<domain>).require(<check>)`.\n"
                  "Local DuckDB does not enforce require, so each rule is evaluated in its denial form,\n"
                  "`m.where(<domain>, <not check>)`: the facts that would violate it. The logic reasoner\n"
                  "(direct LQP compiler) lowers a requirement to that same condition; the LQP version of\n"
                  "this program states the same rules for an engine to enforce.\n\n"
                  "Usage: python THIS_FILE POPULATION.json\n"
                  "Generated by `gnd export pyrel --rules duckdb`. Do not edit; change the model instead.\n"
                  '"""\n')
    if reference:
        listed = "".join(f"  {i}  {path}  sha256 {digest}\n" for i, path, digest in reference["files"])
        spanning_note += ("Reference populations, verified and embedded when this program was generated:\n"
                          f"{listed}A changed reference file needs a new export.\n\n")
    out = [
        f"# /// script\n# requires-python = \">=3.11,<3.14\"\n# dependencies = [\"relationalai=={PYREL_VERSION}\"]\n# ///",
        header.rstrip("\n").replace("Generated by", spanning_note + "Generated by", 1),
        "from __future__ import annotations\n\nimport datetime\nimport json\nimport os\nimport re\nimport sys\nimport tempfile"
        + ("\nfrom fractions import Fraction" if target == "duckdb" else ""),
        (f"\nSCHEMA = {schema!r}\nRULES = json.loads({_rules_table(reqs)!r})\n"
         f"SEMIDERIVED = {[h for h in model.derived if model.facts[h]['derivation'] == 'semiderived']!r}\n"
         f"ROLES = {({f: [[r['role_name'], model.raw_role_type(f, r['role_name'])] for r in model.roles(f)] for f in model.facts})!r}\n"
         f"ROSTERS = {_roster_types(model)!r}\n"
         f"UNCHECKED = json.loads({json.dumps(model.unchecked)!r})\n"
         f"REFERENCE = json.loads({json.dumps(reference)!r})\nLIMIT = 1 << 20\n"),
        ("\ndef read_population(path):\n"
        "    with open(path, 'rb') as handle:\n"
        "        raw = handle.read(LIMIT + 1)\n"
        "    if len(raw) > LIMIT:\n"
        "        raise ValueError('population larger than 1 MiB')\n"
        "    document = json.loads(raw)\n"
        "    if not isinstance(document.get('facts'), dict):\n"
        "        raise KeyError('facts')\n"
        "    header = document.setdefault('population', {})\n"
        "    if not isinstance(header, dict):\n"
        "        raise ValueError('population header must be a mapping')\n"
        "    covers = header.setdefault('covers', [])   # absent covers: nothing is vouched for\n"
        "    for object_type, values in (document.get('instances') or {}).items():\n"
        "        for value in values if object_type in ROSTERS else ():\n"
        "            check_cell('instances', object_type, ROSTERS[object_type], value)\n"
        "    if REFERENCE and any(f in REFERENCE['owned'] for f in document['facts']):\n"
        "        raise ValueError('candidate cannot mention a reference-owned fact type')\n"
        "    if not isinstance(covers, list):\n"
        "        raise ValueError('covers must be a list of fact types')\n"
        "    # GND's checker reads every fact list; only mandatory roles consult covers (see report).\n"
        "    for rule in RULES:\n"
        "        head = rule['info'].get('head') if rule['family'] == 'derivation' else None\n"
        "        if head and head not in covers and document['facts'].get(head):\n"
        "            raise ValueError(f'{head} lists derived facts but is not in covers; GND refuses that input')\n"
        "    for fact_type, rows_ in document['facts'].items():\n"
        "        seen = set()\n"
        "        for row in rows_:\n"
        "            for role, primitive in ROLES.get(fact_type, []):\n"
        "                check_cell(fact_type, role, primitive, row.get(role))\n"
        "            key = json.dumps(row, sort_keys=True)\n"
        "            if key in seen:\n"
        "                raise ValueError(f'duplicate rows in {fact_type}: PyRel relations are sets, so '\n"
        "                                 'repeated facts cannot be checked here; GND reports them')\n"
        "            seen.add(key)\n"
        "    if REFERENCE:   # the candidate plus the embedded reference facts, as GND checks them\n"
        "        document['facts'].update(REFERENCE['facts'])\n"
        "        for object_type, values in REFERENCE['instances'].items():\n"
        "            document.setdefault('instances', {}).setdefault(object_type, []).extend(values)\n"
        "        covers += [f for f in REFERENCE['covers'] if f not in covers]\n"
        "    return document\n"),
        ("\ndef check_cell(fact_type, role, primitive, value):\n"
        "    \"\"\"GND refuses a cell of the wrong type (exit 3); so does this program, before PyRel sees it.\"\"\"\n"
        "    if isinstance(value, dict):\n"
        "        raise ValueError(f'{fact_type}.{role} holds an opaque value; the rules programs do not check those')\n"
        "    number = isinstance(value, (int, float)) and not isinstance(value, bool)\n"
        "    ok = {'String': isinstance(value, str), 'Boolean': isinstance(value, bool),\n"
        "          'Integer': number and isinstance(value, int), 'Float': number,\n"
        "          'Duration': number and isinstance(value, int) and 0 <= value <= 1_000_000,\n"
        "          'Date': is_date(value)}[primitive]\n"
        "    if not ok:\n"
        "        raise ValueError(f'{fact_type}.{role} is {value!r}, which is not a valid {primitive}')\n"),
        ("\ndef is_date(value):\n"
        "    \"\"\"A real Gregorian day written YYYY-MM-DD, as GND requires.\"\"\"\n"
        "    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}', value):\n"
        "        return False\n"
        "    try:\n"
        "        datetime.date.fromisoformat(value)\n"
        "    except ValueError:\n"
        "        return False\n"
        "    return True\n"),
        ("\ndef load(m, relation, rows, roles, dates=()):\n"
        "    \"\"\"Define the facts; dates go in as datetime.date (PyRel Date fields reject ISO strings).\"\"\"\n"
        "    if rows:\n"
        "        m.define(*[relation(*[datetime.date.fromisoformat(row[r]) if r in dates else row[r] for r in roles])\n"
        "                   for row in rows])\n"),
        ("\ndef rows(query):\n"
        "    \"\"\"Query rows, sorted, with dates printed as GND prints them (YYYY-MM-DD).\"\"\"\n"
        "    return sorted([v.isoformat() if isinstance(v, datetime.date) else v for v in row]\n"
        "                  for row in query.to_df().itertuples(index=False, name=None))\n"),
        "\ndef build(population, config):\n"
        "    from relationalai.semantics import Boolean, Date, Field, Float, Integer, Model, String, not_  # noqa: F401\n"
        "    from relationalai.semantics.std import datetime as std_datetime  # noqa: F401\n"
        "    std_date, days = std_datetime.date, std_datetime.days  # noqa: F841\n"
        "    from relationalai.semantics.std import aggregates  # noqa: F401\n"
        "    from relationalai.semantics.std import math as std_math  # noqa: F401\n"
        "    m = Model(SCHEMA, config=config)\n"
        "    facts = population['facts']\n"
        "    instances = population.get('instances', {})\n"
        + ("    found = {}\n" if target == "duckdb" else ""),
        "\n    # ---- facts: one relationship per fact type",
        *_relations(model, names),
    ]
    out += _derivations(model, names, target)
    universes = _universes(model, reqs, names) + _allowed(model, reqs, names) + _helpers(model, names, kinds=("reverse",))
    universes += _helpers(model, names)
    if universes:
        out += ["\n    # ---- helper relations the rules refer to", *universes]
    out.append("\n    # ---- rules: `require` says what must hold")
    for req in reqs:
        out += _rule_block(req, model, names, target)
    for rule_id in spanning:
        out.append(f"    # {rule_id}: spanning uniqueness, broken only by a repeated fact; the input is refused instead")
    for rule in model.unchecked:
        out.append(f"    # {rule['id']}: textual rule, not checked by GND or here: {rule['expression']!r}")
    if target == "duckdb":
        out.append("    return found")
    else:
        first = next(f for f, fact in model.facts.items() if not isinstance(fact.get("derivation_rule"), dict))
        refs = ", ".join(f"{model.role_type(first, r['role_name'])}.ref()" for r in model.roles(first))
        out.append(f"    probe_vars = [{refs}]")
        out.append(f"    return m, lambda: rows(m.where({names.relation(first)}(*probe_vars)).select(*probe_vars))")
    out.append(_DUCKDB_MAIN if target == "duckdb" else _LQP_MAIN)
    return "\n".join(out) + "\n"
