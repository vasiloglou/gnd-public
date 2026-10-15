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
             "std_math", "h_row", "h_a", "h_b", "h_c", "h_x", "Fraction", "Date", "datetime", "std_date", "days",
             "step", "before", "states", "previous", "stepped"}


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
    model = _Model(doc)
    names_used = {r["role_name"] for f in model.facts for r in model.roles(f)} | {
        p.get("name") for op in doc.get("operations") or [] for p in op.get("parameters") or []}
    if "gnd_step" in names_used or "gnd_before" in names_used:
        raise ExportInputError("a role or parameter named gnd_step or gnd_before clashes with the plan's state field; "
                               "rename it")
    for op in doc.get("operations") or []:
        for rule in op.get("dynamic_rules") or []:
            if rule.get("subject", {}).get("fact_type") in model.derived:
                raise ExportInputError(f"operation {op['id']!r}: a dynamic rule on a derived fact type is a later phase "
                                       "of the rules programs")
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


def _unswap(model: _Model, atoms: list[Atom], seen_order: list[str] | tuple[str, ...] = ()) -> list[Atom]:
    """Read an atom through a reordered copy when it takes variables in a different order than earlier atoms.

    PyRel 1.30.1 cannot compile a join in which two atoms share variables in different orders
    ("reordering loop did not reach a fixpoint"), as in R(x, y), R(y, x) or do(s, c, g), grade(s, g, c).
    A binary atom is read through <relation>_reverse; a wider one through <relation>_as_<permutation>,
    whose fields follow the order in which the variables first appeared. seen_order: variables bound
    before the first atom (an operation's parameters).
    """
    order: list[str] = list(seen_order)
    seen = {(a, b) for i, a in enumerate(order) for b in order[i + 1:]}
    out = []
    for atom in atoms:
        args = atom.args
        names = [a for a in args if isinstance(a, str) and a.startswith("$")]
        clash = any((v, u) in seen for i, u in enumerate(names) for v in names[i + 1:] if u != v)
        if clash and len(args) == 2:
            primitive = _relation_roles(model, atom.relation)[0][1]
            reverse = model.helper(f"{atom.relation}_reverse", [("a", primitive), ("b", primitive)], "reverse",
                                   fact=atom.relation)
            atom = Atom(reverse, (args[1], args[0]))
        elif clash:
            rank = {v: i for i, v in enumerate(order)}
            perm = sorted(range(len(args)), key=lambda i: (0, rank[args[i]]) if args[i] in rank else (1, i))
            fields = _relation_roles(model, atom.relation)
            name = model.helper(f"{atom.relation}_as_{''.join(map(str, perm))}", [fields[i] for i in perm], "permute",
                                fact=atom.relation, perm=perm)
            atom = Atom(name, tuple(args[i] for i in perm))
        names = [a for a in atom.args if isinstance(a, str) and a.startswith("$")]
        seen |= {(u, v) for i, u in enumerate(names) for v in names[i + 1:] if u != v}
        order += [v for v in names if v not in order]
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
        # with operations, every state of a plan lives in one PyRel model: relations get a leading step
        self.step: str | None = "step" if model.doc.get("operations") else None
        self.constant = {f"{c.get('id')}_allowed" for c in model.doc.get("constraints", [])
                         if c.get("type") == "value" and "allowed" in c}

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


def _at(names: _Names, at: str | None = None) -> str:
    """The state argument a relation takes in a plan's model ("" outside plans)."""
    return f"{at or names.step}, " if names.step else ""


def _step_field(names: _Names) -> str:
    return "Field('gnd_step', Integer), " if names.step else ""


def _atom_text(atom: Atom, names: _Names, model: _Model, at: str | None = None) -> str:
    roles = _relation_roles(model, atom.relation)
    args = ", ".join(_term(arg, names, model, primitive) for (_, primitive), arg in zip(roles, atom.args))
    state = "" if atom.relation in names.constant else _at(names, at)
    return f"{names.relation(atom.relation)}({state}{args})"


def _operand(value: Any, names: _Names) -> str:
    if isinstance(value, Count):
        text = f"aggregates.count({', '.join(names.var(v) for v in value.of)})"
        per = ([names.step] if names.step else []) + [names.var(v) for v in value.per]
        return text + (f".per({', '.join(per)})" if per else "")
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
    if req.family == "cardinality" and req.part == "min" and not names.step:
        # no outer domain: with none, the rule still applies to an empty universe, which GND fails
        count = _operand(req.check.compare.left, names)
        return f"m.require({count}.where({domain}) >= {req.check.compare.right!r})"
    check = ", ".join(_check_text(req.check, names, model, negate=False))
    return f"m.where({domain}).require({check})"


def denial_text(req: Requirement, names: _Names, model: _Model) -> str:
    parts = [*(_atom_text(a, names, model) for a in req.domain), *_check_text(req.check, names, model, negate=True)]
    selected = ", ".join(([names.step] if names.step else []) + [names.var(v) for v in req.witness])
    return f"m.where({', '.join(parts)}).select({selected})"


def _universes(model: _Model, reqs: list[Requirement], names: _Names) -> list[str]:
    wanted = sorted({a.relation[: -len("_any")] for r in reqs for a in r.domain if a.relation.endswith("_any")}
                    | {e["create"]["object_type"] for o in model.doc.get("operations") or [] for e in o.get("effects", [])
                       if "create" in e})
    lines = []
    for object_id in wanted:
        primitive = model.primitive(object_id)
        rel = names.relation(f"{object_id}_any")
        lines.append(f"    # every {object_id} mentioned in any fact, plus the population's instances roster")
        lines.append(f"    {rel} = m.Relationship(fields=[{_step_field(names)}Field('member', {primitive})], short_name='{object_id}_any')")
        lines.append(f"    h_x = {primitive}.ref()")
        st = _at(names)
        for fact_id, role_name in model.plays(object_id):
            args = ", ".join("h_x" if r["role_name"] == role_name else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                             for r in model.roles(fact_id))
            lines.append(f"    m.where({names.relation(fact_id)}({st}{args})).define({rel}({st}h_x))")
        rosters = _rosters(model, object_id)
        value = "datetime.date.fromisoformat(value)" if primitive == "Date" else "value"
        if names.step:
            lines.append(f"    for k, value in [(k, v) for k, state in enumerate(states) for key in {rosters!r}")
            lines.append("                     for v in state.get('instances', {}).get(key, [])]:")
            lines.append(f"        m.define({rel}(k, {value}))")
        else:
            lines.append(f"    for value in [v for key in {rosters!r} for v in instances.get(key, [])]:")
            lines.append(f"        m.define({rel}({value}))")
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
        lines.append(f"    {rel} = m.Relationship(fields=[{_step_field(names)}{fields}], short_name={name!r})")
        st = _at(names)
        if spec["kind"] == "reverse":
            primitive = spec["fields"][0][1]
            fact = names.relation(spec["fact"])
            lines.insert(-1, f"    # {spec['fact']} read backwards (joining a relation with itself, swapped, trips a PyRel 1.30.1 bug)")
            lines.append(f"    h_a, h_b = {primitive}.ref(), {primitive}.ref()")
            lines.append(f"    m.where({fact}({st}h_a, h_b)).define({rel}({st}h_b, h_a))")
        elif spec["kind"] == "permute":
            source = names.relation(spec["fact"])
            width = len(spec["perm"])
            kinds = [primitive for _, primitive in _relation_roles(model, spec["fact"])]
            lines.insert(-1, f"    # {spec['fact']} with its fields reordered (two atoms sharing variables in different orders "
                             "trip a PyRel 1.30.1 bug)")
            source_vars = ", ".join(f"h_{i}" for i in range(width))
            lines.append(f"    {source_vars} = {', '.join(f'{kinds[i]}.ref()' for i in range(width))}")
            lines.append(f"    m.where({source}({st}{source_vars})).define({rel}({st}{', '.join(f'h_{i}' for i in spec['perm'])}))")
        elif spec["kind"] == "closure":
            primitive = spec["fields"][0][1]
            fact = names.relation(spec["fact"])
            lines.insert(-1, f"    # every pair connected by a chain of {spec['fact']} facts (recursive)")
            lines.append(f"    h_a, h_b, h_c = {primitive}.ref(), {primitive}.ref(), {primitive}.ref()")
            lines.append(f"    m.where({fact}({st}h_a, h_b)).define({rel}({st}h_a, h_b))")
            lines.append(f"    m.where({rel}({st}h_a, h_b), {fact}({st}h_b, h_c)).define({rel}({st}h_a, h_c))")
        elif spec["kind"] == "plays":
            lines.insert(-1, f"    # every instance that plays one of the roles {[f'{f}.{r}' for f, r in spec['refs']]}")
            for fact_id, role_name in spec["refs"]:
                args = ", ".join("h_x" if r["role_name"] == role_name else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                                 for r in model.roles(fact_id))
                lines.append(f"    h_x = {spec['fields'][0][1]}.ref()")
                lines.append(f"    m.where({names.relation(fact_id)}({st}{args})).define({rel}({st}h_x))")
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
                lines.append(f"    m.where({universe}({st}h_x){''.join(', ' + c for c in conditions)}).define({rel}({st}h_x))")
        else:
            raise ExportInputError(f"unknown helper kind {spec['kind']}")
    return lines


def _relations(model: _Model, names: _Names) -> list[str]:
    lines = []
    for fact_id, fact in model.facts.items():
        fields = _step_field(names) + ", ".join(f"Field({r['role_name']!r}, {model.role_type(fact_id, r['role_name'])})"
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
        rows_text = f"stepped(states, {fact_id!r})" if names.step else f"facts.get({fact_id!r}, [])"
        roles_text = ("gnd_step",) + roles if names.step else roles
        lines.append(f"    load(m, {names.relation(target)}, {rows_text}, {roles_text!r}"
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
        fields = _step_field(names) + ", ".join(f"Field({r['role_name']!r}, {model.role_type(head, r['role_name'])})"
                                                for r in model.roles(head))
        rel = names.relation(f"{head}_derived")
        lines.append(f"    {rel} = m.Relationship(fields=[{fields}], short_name='{head}_derived')")
    clauses = []
    for head in model.derived:
        fact = model.facts[head]
        clauses.append(f"    # {head} ({fact['derivation']}): {fact.get('reading', head)}")
        for clause in _clauses(fact["derivation_rule"]):
            clauses += _clause_lines(model, names, head, clause)
    lines += _helpers(model, names, kinds=("reverse", "permute"))   # registered while lowering the clauses
    lines += clauses
    for head in model.derived:
        semi = model.facts[head]["derivation"] == "semiderived"
        if not semi and not names.step:
            continue
        # constraints read a semiderived head as computed, and in a plan every head from state 1 on;
        # defined only after every clause exists
        args = ", ".join(([names.step] if names.step else []) + [f"{model.role_type(head, r['role_name'])}.ref()"
                                                                   for r in model.roles(head)])
        when = "" if semi else f", {names.step} >= 1"
        lines.append(f"    h_row = [{args}]")
        lines.append(f"    m.where({names.relation(head + '_derived')}(*h_row){when}).define({names.relation(head)}(*h_row))")
        if target == "duckdb":   # the report reads it for vacuity and for witnesses built from facts
            lines.append(f"    found['computed:{head}'] = rows(m.where({names.relation(head + '_derived')}(*h_row)).select(*h_row))")
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
        per = ([names.step] if names.step else []) + [names.var(v) for v in group]
        if per:
            text += f".per({', '.join(per)})"
        lines.append(f"    {names.var(bound)} = {text}   # GND counts each distinct ({', '.join([*over, of])}) once")
    for comparison in clause["where"]:
        parts.append(f"{_expr(comparison['left'], names)} {_PYOP[comparison['operator']]} {_expr(comparison['right'], names)}")
    head_args = ", ".join(_expr(t, names) for t in head_terms)
    lines.append(f"    m.where({', '.join(parts)}).define({names.relation(head + '_derived')}({_at(names)}{head_args}))")
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


def judge(parts, found, facts, computed=()):
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
                    if info['fact'] in computed:   # the constraint reads the computed facts
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
    lines, flags = state_lines(population, found)
    for line in lines:
        print(line)
    return band(flags)


def band(flags):
    return 1 if flags['violated'] else 4 if flags['unchecked'] else 2 if flags['vacuous'] else 0


def state_lines(population, found, computed=None, derivations=True):
    """The report lines for one state. computed: derived fact types read as computed (semiderived ones in a
    snapshot; every derived one in a plan's later states, where GND drops the claims)."""
    computed = SEMIDERIVED if computed is None else computed
    out = []
    print = out.append  # noqa: A001 -- the lines are returned, not printed
    facts = population['facts']
    instances = population.get('instances', {})
    covers = set(population['population']['covers'])
    violated = vacuous = unchecked = False
    groups = {}
    for rule in RULES:
        groups.setdefault(rule['id'], []).append(rule)
    for name, parts in groups.items():
        rule = parts[0]
        if rule['family'] == 'derivation' and not derivations:
            continue
        if rule['family'] == 'derivation' and rule['info']['head'] not in covers:
            print(f'{name}  not checked  (no claim: {rule["info"]["head"]} is not in covers)')
            unchecked = True
            continue
        mode, lists = rule['vacuous_when']
        # a semiderived fact type is read as computed, so its emptiness is the computed relation's
        empty = [not (found.get(f'computed:{ref}') if ref in computed else facts.get(ref)) for ref in lists]
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
            verdict, witness = judge(parts, found, facts, computed)
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
    return out, {'violated': violated, 'unchecked': unchecked, 'vacuous': vacuous}


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

_PLAN_HELPERS = '''

def stepped(states, fact_type):
    """Every state's facts of one type, each row tagged with its state's step."""
    return [dict(row, gnd_step=k) for k, state in enumerate(states) for row in state['facts'].get(fact_type, [])]
'''

_PLAN_MAIN = '''

STEPS_LIMIT = 500   # about 0.35 s per step on local DuckDB (measured)
STEPS_BYTES = 10 * 1024 * 1024


class PlanInputError(ValueError):
    pass


def read_steps(path, pre_raw):
    """Validate a steps document as GND does (gnd.transition), refusing with GND's codes."""
    import hashlib
    with open(path, 'rb') as handle:
        raw = handle.read(STEPS_BYTES + 1)
    if len(raw) > STEPS_BYTES:
        raise PlanInputError(f'[transition:steps-too-large] steps file is over the {STEPS_BYTES}-byte cap')
    try:
        document = json.loads(raw)
    except ValueError as error:
        raise PlanInputError(f'[transition:steps-shape] steps document is not valid JSON: {error}') from error
    shape_error = steps_shape_error(document)
    if shape_error:
        raise PlanInputError(f'[transition:steps-shape] {shape_error}')
    if document['model_digest'] != MODEL_DIGEST:
        raise PlanInputError(f"[transition:model-digest-mismatch] the steps were written for {document['model_digest']}; "
                             f'this model is {MODEL_DIGEST}')
    if document['operations_digest'] != OPERATIONS_DIGEST:
        raise PlanInputError(f"[transition:operations-digest-mismatch] the steps were written for operations "
                             f"{document['operations_digest']}; this model's are {OPERATIONS_DIGEST}")
    if document.get('pre_digest') is not None and document['pre_digest'] != 'sha256:' + hashlib.sha256(pre_raw).hexdigest():
        raise PlanInputError('[transition:pre-digest-mismatch] pre_digest does not match the pre-population')
    if len(document['steps']) > STEPS_LIMIT:
        raise PlanInputError(f'plans of more than {STEPS_LIMIT} steps are refused by the rules programs')
    plan = []
    for index, step in enumerate(document['steps'], 1):
        op, bindings = step.get('op'), step.get('bindings')
        if op not in OPERATIONS:
            raise PlanInputError(f'[transition:unknown-operation] step {index} names operation {op!r}, which this model '
                                 'does not declare')
        params = dict(OPERATIONS[op]['params'])
        if not isinstance(bindings, dict) or set(bindings) != set(params):
            missing = sorted(set(params) - set(bindings or {}))
            raise PlanInputError(f'[transition:bindings-mismatch] step {index} binds {sorted(bindings or {})} for '
                                 f"operation {op!r}, which declares {sorted(params)}; missing {missing}")
        for name, value in bindings.items():
            try:
                check_cell(f'step {index}', name, params[name], value)
            except ValueError as error:
                raise PlanInputError(f'[transition:binding-type] {error}') from error
        plan.append((op, bindings))
    return plan


DIGEST = re.compile(r'sha256:[0-9a-f]{64}')


def steps_shape_error(document):
    """GND's steps.schema.json, checked by hand: exact keys, types and digest shapes."""
    if not isinstance(document, dict):
        return 'a steps document is a JSON object'
    allowed, required = {'steps_schema', 'model', 'model_digest', 'operations_digest', 'pre_digest', 'steps'}, {
        'steps_schema', 'model', 'model_digest', 'operations_digest', 'steps'}
    if set(document) - allowed or required - set(document):
        return f'keys must be {sorted(required)} plus optional pre_digest; got {sorted(document)}'
    if type(document['steps_schema']) is not int or document['steps_schema'] != 1:
        return 'steps_schema must be the integer 1'
    if not isinstance(document['model'], str):
        return 'model must be a string'
    for key in ('model_digest', 'operations_digest', 'pre_digest'):
        if key in document and not (isinstance(document[key], str) and DIGEST.fullmatch(document[key])):
            return f'{key} must be sha256:<64 hex digits>'
    steps = document['steps']
    if not isinstance(steps, list) or not steps:
        return 'steps must be a non-empty list'
    for index, step in enumerate(steps, 1):
        if not isinstance(step, dict) or set(step) != {'op', 'bindings'} or not isinstance(step['op'], str):
            return f'step {index} must be exactly {{"op": name, "bindings": {{...}}}}'
        if not isinstance(step['bindings'], dict) or any(isinstance(v, (dict, list)) for v in step['bindings'].values()):
            return f'step {index} bindings must map parameter names to single values'
    return None


def check_coverage(pre, plan):
    """GND's coverage gates (transition.assert_*_coverage), in GND's order; refused with GND's codes."""
    covered = set(pre['population'].get('covers') or [])
    ops = [COVERAGE['ops'][op] for op, _ in plan]

    def frame():
        gaps = sorted(set().union(*(set(o['frame']) for o in ops)) - covered)
        if gaps:
            raise PlanInputError(f'[transition:frame-coverage] the pre-population does not cover {gaps}, which this '
                                 "walk's operations touch")

    def static():
        required = {d for o in ops for deps in o['static'].values() for d in deps}
        gaps = sorted(required - covered)
        if gaps:
            raise PlanInputError(f'[transition:static-derivation-coverage] the pre-population does not cover {gaps}, '
                                 'which are asserted dependencies of static derivations read by this walk')

    def dynamic():
        selected = set(COVERAGE['standing']).union(*(set(o['dynamic']) for o in ops))
        for head in sorted(selected):
            gaps = sorted(set(COVERAGE['closure'][head]) - covered)
            if gaps:
                raise PlanInputError(f'[transition:dynamic-derivation-coverage] the pre-population omits {gaps} '
                                     f"required for dynamic derivation '{head}'")
    for gate in ((dynamic, frame, static) if COVERAGE['multi_clause'] else (frame, static, dynamic)):
        gate()


def apply_step(state, op, bindings):
    """GND's transition equation: retract selectors read the state before, all retracts precede all asserts."""
    def value(v):
        return bindings[v[1:]] if isinstance(v, str) and v.startswith('$') else v
    facts = {k: list(v) for k, v in state['facts'].items()}
    doomed = {}
    for effect in OPERATIONS[op]['effects']:
        (kind, spec), = effect.items()
        if kind == 'retract':
            selector = {r: value(v) for r, v in spec['bind'].items()}
            doomed.setdefault(spec['fact_type'], set()).update(
                i for i, row in enumerate(state['facts'].get(spec['fact_type'], []))
                if all(row.get(r) == v for r, v in selector.items()))
    for fact_type, indices in doomed.items():
        facts[fact_type] = [row for i, row in enumerate(facts.get(fact_type, [])) if i not in indices]
    slots = {fact_type: sorted(indices) for fact_type, indices in doomed.items()}
    for effect in OPERATIONS[op]['effects']:   # creates add nothing: GND's states are facts only
        (kind, spec), = effect.items()
        if kind != 'assert':
            continue
        row = {r: value(v) for r, v in spec['bind'].items()}
        rows_ = facts.setdefault(spec['fact_type'], [])
        if row in rows_:
            continue   # duplicate asserts collapse
        free = slots.get(spec['fact_type'], [])
        if free:   # GND puts an asserted fact where a retracted one was (a replace keeps its place)
            rows_.insert(min(free.pop(0), len(rows_)), row)
        else:
            rows_.append(row)
    return {'population': state['population'], 'facts': facts, 'instances': {}}


def plan_states(pre, plan):
    """S(0) is the pre-population; later states carry asserted facts only (GND computes derived facts)."""
    states = [pre]
    # GND re-loads each later state from its facts alone: no derived claims and no instance rosters
    current = {'population': pre['population'], 'facts': {k: v for k, v in pre['facts'].items() if k not in DERIVED},
               'instances': {}}
    for op, bindings in plan:
        current = apply_step(current, op, bindings)
        states.append(current)
    return states


def at_state(found, k):
    """The rows of one state, without the step column."""
    return {key: [row[1:] for row in rows_ if row[0] == k] for key, rows_ in found.items() if not key.startswith('step:')}


def step_lines(k, op, bindings, found):
    """GND's step verdicts for step k that do not pass, with GND's locators."""
    out = []
    minted = set()
    for check in (c for c in STEP_CHECKS if c['op'] == op):
        where = f"$.steps[{k}].{check['locator']}"
        if check['kind'] == 'create-freshness':
            value = bindings[check['param']]
            existing = any(r[0] == k for r in found[check['key']])
            if existing or (check['object_type'], json.dumps(value)) in minted:
                out.append((f'{where}  violated  {json.dumps(value)}', 'violated'))
            minted.add((check['object_type'], json.dumps(value)))
            continue
        alethic = check['modality'] == 'alethic'
        status = 'violated' if alethic else 'warning'
        if check['kind'] == 'dynamic-rule':
            if not check['functional']:
                out.append((f'{where}  not checked  (no uniqueness rule makes the value single)',
                            'unchecked' if alethic else None))
                continue
            old = [r for r in found[check['key'] + ':old'] if r[0] == k]
            new = [r for r in found[check['key'] + ':new'] if r[0] == k]
            if not old or not new:
                out.append((f"{where}  vacuous  (no {'old' if not old else 'new'} value)", 'vacuous'))
                continue
            hits = [r for r in found[check['key']] if r[0] == k]
            if hits:
                out.append((f"{where}  {status}  {json.dumps([{'old': r[1], 'new': r[2]} for r in hits])}",
                            'violated' if alethic else None))
            continue
        if any(r[0] == k for r in found[check['key']]):
            if check['kind'] == 'create-freshness':
                witness = bindings[check['param']]
            elif check['kind'] == 'precondition':
                witness = bindings
            else:
                witness = {r: bindings[v[1:]] if isinstance(v, str) and v.startswith('$') else v
                           for r, v in check['selector'].items()}
            out.append((f'{where}  {status}  {json.dumps(witness, sort_keys=True)}', 'violated' if alethic else None))
    return out


def compiled_verdicts(pre, found):
    """GND's compiled precondition obligations on the pre-state, when both fact types are covered."""
    covered = set(pre['population'].get('covers') or [])
    lines, flags = [], {'violated': False, 'unchecked': False, 'vacuous': False}
    for entry in COMPILED:
        if {entry['of'], entry['in']} - covered:
            continue
        rows_ = [dict(zip(entry['roles'], r[1:])) for r in found[entry['key']] if r[0] == 0]
        if rows_:
            alethic = entry['modality'] == 'alethic'
            lines.append(f"{entry['locator']}  {'violated' if alethic else 'warning'}  {json.dumps(rows_, sort_keys=True)}")
            flags['violated'] = flags['violated'] or alethic
    return lines, flags


def report_plan(states, plan, found):
    """Each step's checks, then the state it leads to; only what does not pass is listed."""
    flags = {'violated': False, 'unchecked': False, 'vacuous': False}
    for k, state in enumerate(states):
        if k:
            op, bindings = plan[k - 1]
            print(f"step {k}  {op}({', '.join(f'{n}={v!r}' for n, v in bindings.items())})")
            for line, flag in step_lines(k, op, bindings, found):
                print(f'step {k}  {line}')
                if flag:
                    flags[flag] = True
        lines, state_flags = state_lines(state, at_state(found, k), computed=DERIVED if k else None, derivations=not k)
        if not k:
            compiled_lines, compiled_flags = compiled_verdicts(state, found)
            lines += compiled_lines
            for key in flags:
                flags[key] = flags[key] or compiled_flags[key]
        for key in flags:
            flags[key] = flags[key] or state_flags[key]
        problems = [line for line in lines if not line.endswith('  OK')]
        for line in problems:
            print(f'state {k}  {line}')
        if not problems:
            print(f'state {k}  every rule holds')
    return band(flags)


def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if '--post' in argv:
        print('--post (comparing a plan with a declared after-state, the frame check of GND) is not supported by the rules '
              'programs; run the plan with --pre and --steps', file=sys.stderr)
        return 3
    plan_mode = '--steps' in argv or '--pre' in argv
    if plan_mode:
        flags = dict(zip(argv[::2], argv[1::2]))
        emit_post = flags.pop('--emit-post', None)
        if len(argv) != 4 + (2 if emit_post else 0) or set(flags) != {'--pre', '--steps'}:
            print('usage: python THIS_FILE --pre PRE.json --steps STEPS.json [--emit-post POST.json]   '
                  '(or: python THIS_FILE POPULATION.json)', file=sys.stderr)
            return 64
        population_path, steps_path = flags['--pre'], flags['--steps']
    elif len(argv) != 1:
        print('usage: python THIS_FILE POPULATION.json   (or: python THIS_FILE --pre PRE.json --steps STEPS.json)',
              file=sys.stderr)
        return 64
    else:
        population_path = argv[0]
    try:
        population = read_population(population_path)
        plan = []
        if plan_mode:
            with open(population_path, 'rb') as handle:
                plan = read_steps(steps_path, handle.read(LIMIT + 1))
            check_coverage(population, plan)
    except PlanInputError as error:
        print(f'{steps_path}: refused: {error}', file=sys.stderr)
        return 3
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError) as error:
        print(f'{population_path}: not a readable plan or population ({type(error).__name__}: {error})', file=sys.stderr)
        return 3
    states = plan_states(population, plan) if plan else [population]
    try:
        with tempfile.TemporaryDirectory(prefix='gnd-rules-') as directory:
            os.environ['RAI_BUILD_DIR'] = directory   # explicit local build state; no remote discovery
            from relationalai.config import Config
            config = Config(connections={'local': {'type': 'duckdb', 'path': ':memory:'}},
                            default_connection='local',
                            deployment={'schema': SCHEMA, 'auto_deploy': True})
            found = build(states, plan, config)
    except Exception as error:  # noqa: BLE001 -- a crash must never read as a rule violation (exit 1)
        print(f'PyRel execution failed: {type(error).__name__}: {error}', file=sys.stderr)
        return 70
    if plan:
        exit_code = report_plan(states, plan, found)
        if emit_post:
            try:
                write_post(emit_post, states, found)
            except OSError as error:  # the verdict stands; only the after-state is missing (never exit 1)
                print(f'cannot write the post-state: {error}', file=sys.stderr)
                return 74
        return exit_code
    return report(population, at_state(found, 0))


def write_post(path, states, found):
    """The plan's last state as a population: its asserted facts plus the derived facts PyRel computed for it.

    Written to a fresh file, whatever the verdict; the caller decides whether to publish it.
    """
    last, k = states[-1], len(states) - 1
    facts = {key: list(rows_) for key, rows_ in last['facts'].items()}
    for head in DERIVED:
        roles = [role for role, _ in ROLES[head]]
        facts[head] = [dict(zip(roles, row[1:])) for row in found[f'computed:{head}'] if row[0] == k]
    document = {'population': {'model': last['population'].get('model'), 'model_id': last['population'].get('model_id'),
                               'source': 'synthetic', 'covers': last['population'].get('covers', [])},
                'facts': facts}
    with open(path, 'x', encoding='utf-8') as handle:
        json.dump(document, handle, indent=1, ensure_ascii=False)
        handle.write('\\n')


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
    expected = sum(rule['requires'] for rule in RULES) + PLAN_REQUIRES
    print(f'{len(walker.found)} requirements compiled for {len(RULES)} rules (expected {expected})')
    for node in walker.found:
        print(' '.join(str(node).split()))
    return 0 if len(walker.found) == expected else 1


if __name__ == '__main__':
    raise SystemExit(main())
'''


# ---------------------------------------------------------------- plans (operations)

def _op_params(model: _Model, op: dict[str, Any]) -> list[tuple[str, str]]:
    return [(p["name"], model.raw_primitive(p["object_type"])) for p in op.get("parameters") or []]


def _op_atom(model: _Model, pattern: dict[str, Any], derived: bool) -> Atom:
    """An operation atom; $name binds a parameter, an omitted role is any value."""
    atom = _atom(model, pattern)
    return Atom(_derived_relation(model, atom.relation) if derived else atom.relation, atom.args)


def _functional(model: _Model, fact_id: str, bound: set[str]) -> bool:
    """GND's gate: an internal uniqueness constraint over roles the dynamic rule binds proves one value."""
    return any(c.get("type") == "uniqueness" and set(ModelIndex.constraint_roles(c)) <= bound
               for c in model.facts[fact_id].get("constraints") or [])


def _plan_checks(model: _Model, names: _Names, target: str) -> tuple[list[str], list[dict[str, Any]]]:
    """Every step check of GND's transition walk, as a PyRel query over consecutive states.

    A check's rows name the steps where it fails; the report prints them with GND's locators.
    """
    lines = ["\n    # ---- the plan: one row per step, and which state each step starts from",
             "    previous = m.Relationship(fields=[Field('gnd_step', Integer), Field('gnd_before', Integer)], short_name='previous')",
             ("    load(m, previous, [{'gnd_step': k, 'gnd_before': k - 1} for k in range(1, len(plan) + 1)], "
              "('gnd_step', 'gnd_before'))")]
    table: list[dict[str, Any]] = []
    for op in model.doc.get("operations") or []:
        params = _op_params(model, op)
        do = names.relation(f"do_{op['id']}")
        fields = ", ".join(["Field('gnd_step', Integer)"] + [f"Field({n!r}, {_TYPES[t]})" for n, t in params])
        dates = tuple(n for n, t in params if t == "Date")
        lines.append(f"    # {op['id']}: {op.get('reading', op['id'])}")
        lines.append(f"    {do} = m.Relationship(fields=[{fields}], short_name='do_{op['id']}')")
        lines.append(f"    load(m, {do}, [dict(b, gnd_step=k) for k, (o, b) in enumerate(plan, 1) if o == {op['id']!r}], "
                     f"{tuple(['gnd_step'] + [n for n, _ in params])!r}" + (f", dates={dates!r})" if dates else ")"))
        types = {f"${n}": _TYPES[t] for n, t in params}
        pvars = [names.var(f"${n}") for n, _ in params]
        if pvars:
            lines.append(_declare([f"${n}" for n, _ in params], types, names))
        doing = f"{do}(step, {', '.join(pvars)})" if pvars else f"{do}(step)"
        selected = ", ".join(["step"] + pvars)
        common = {"op": op["id"], "params": [n for n, _ in params]}
        bound = [f"${n}" for n, _ in params]   # variables the do_ atom binds first

        def text(atom, at, bound=bound):
            (atom,) = _unswap(model, [atom], bound)
            return _atom_text(atom, names, model, at=at)

        def add(key, kind, locator, modality, require, denial, common=common, **extra):
            table.append({"key": key, "kind": kind, "locator": locator, "modality": modality, **common, **extra})
            lines.append(f"    #   {kind} {locator}: {require}")
            if target == "lqp":
                lines.append(f"    {require}")
            else:
                lines.append(f"    found[{key!r}] = rows({denial})")

        for pre in op.get("preconditions") or []:
            ordered = _unswap(model, [_op_atom(model, a, True) for a in pre["require"]], bound)
            atoms = [_atom_text(a, names, model, at="before") for a in ordered]
            add(f"step:{op['id']}:pre:{pre['id']}", "precondition", f"preconditions[id={pre['id']}]", pre["modality"],
                f"m.where({doing}, previous(step, before)).require({', '.join(atoms)})",
                f"m.where({doing}, previous(step, before), not_({', '.join(atoms)})).select({selected})",
                atoms=pre["require"])
        for j, effect in enumerate(op.get("effects") or []):
            ((kind, spec),) = effect.items()
            if kind == "retract":
                atom = text(_op_atom(model, spec, False), "before")
                add(f"step:{op['id']}:retract:{j}", "retract-target", f"effects[{j}].retract", "alethic",
                    f"m.where({doing}, previous(step, before)).require({atom})",
                    f"m.where({doing}, previous(step, before), not_({atom})).select({selected})", selector=spec["bind"],
                    fact_type=spec["fact_type"])
            elif kind == "assert":
                atom = text(_op_atom(model, spec, False), "before")
                add(f"step:{op['id']}:assert:{j}", "assert-redundant", f"effects[{j}].assert", "deontic",
                    f"m.where({doing}, previous(step, before)).require(not_({atom}))",
                    f"m.where({doing}, previous(step, before), {atom}).select({selected})", selector=spec["bind"],
                    fact_type=spec["fact_type"])
            elif kind == "create":
                universe = _present(model, names, spec["object_type"], lines)
                value = names.var(f"${spec['param']}")
                add(f"step:{op['id']}:create:{j}", "create-freshness", f"effects[{j}].create", "alethic",
                    f"m.where({doing}, previous(step, before)).require(not_({universe}(before, {value})))",
                    f"m.where({doing}, previous(step, before), {universe}(before, {value})).select({selected})",
                    param=spec["param"], object_type=spec["object_type"])
            else:
                raise ExportInputError(f"operation {op['id']!r}: effect {kind!r} is not supported by the rules programs")
        touched = {next(iter(e.values())).get("fact_type") for e in op.get("effects") or []}
        for j, rule in enumerate(op.get("dynamic_rules") or []):
            subject = rule["subject"]
            fact_id, role = subject["fact_type"], subject["value_role"]
            if fact_id not in touched:
                continue   # GND gives no verdict when the operation leaves the subject alone
            entry = {"key": f"step:{op['id']}:dynamic:{j}", "kind": "dynamic-rule", "locator": f"dynamic_rules[{j}]",
                     "modality": rule["modality"], **common}
            if not _functional(model, fact_id, set(subject.get("bind") or {}) - {role}):
                table.append({**entry, "functional": False})
                continue
            vtype = model.role_type(fact_id, role)
            old, new = f"$old_{role}", f"$new_{role}"
            types = {old: vtype, new: vtype}
            lines.append(_declare([old, new], types, names))

            def subject_atom(value, at, subject=subject, role=role, fact_id=fact_id, text=text):
                bind = {**subject.get("bind", {}), role: value}
                return text(Atom(fact_id, tuple(bind.get(r["role_name"]) for r in model.roles(fact_id))), at)
            was, now = subject_atom(old, "before"), subject_atom(new, "step")
            o, n = names.var(old), names.var(new)
            pinned = (subject.get("bind") or {}).get(role)
            if pinned is not None:   # the subject names its value too: only that value counts, old and new
                value = names.var(pinned) if isinstance(pinned, str) and pinned.startswith("$") else _literal(pinned, vtype)
                was, now = f"{was}, {o} == {value}", f"{now}, {n} == {value}"
            table.append({**entry, "functional": True})
            lines.append(f"    #   dynamic-rule dynamic_rules[{j}]: new {rule['op']} old for {fact_id}.{role}")
            if target == "lqp":
                lines.append(f"    m.where({doing}, previous(step, before), {was}, {now}).require({n} {_PYOP[rule['op']]} {o})")
            else:
                lines.append(f"    found[{entry['key'] + ':old'!r}] = rows(m.where({doing}, previous(step, before), {was}).select(step, {o}))")
                lines.append(f"    found[{entry['key'] + ':new'!r}] = rows(m.where({doing}, {now}).select(step, {n}))")
                lines.append(f"    found[{entry['key']!r}] = rows(m.where({doing}, previous(step, before), {was}, {now}, "
                             f"{n} {_PYOP[_NEGATED[rule['op']]]} {o}).select(step, {o}, {n}))")
    return lines, table


def _present(model: _Model, names: _Names, object_id: str, lines: list[str]) -> str:
    """The values of an object type that appear in a state's facts, in roles of exactly that type.

    That is what GND's freshness check counts as an existing instance (transition._instance_keys):
    neither instance rosters nor reference widening.
    """
    name = f"{object_id}_present"
    if name not in names.relations:
        rel = names.relation(name)
        primitive = model.primitive(object_id)
        lines.append(f"    # every {object_id} that appears in a state's facts (what a create must not repeat)")
        lines.append(f"    {rel} = m.Relationship(fields=[Field('gnd_step', Integer), Field('member', {primitive})], short_name={name!r})")
        lines.append(f"    h_x = {primitive}.ref()")
        for fact_id in model.facts:
            for role in model.roles(fact_id):
                if role["object_type"] != object_id:
                    continue
                args = ", ".join("h_x" if r["role_name"] == role["role_name"] else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                                 for r in model.roles(fact_id))
                lines.append(f"    m.where({names.relation(fact_id)}(step, {args})).define({rel}(step, h_x))")
    return names.relation(name)


def _compiled_checks(model: _Model, loaded: Any, names: _Names, target: str) -> tuple[list[str], list[dict[str, Any]]]:
    """GND compiles some preconditions into standing subset obligations judged on the pre-state
    (every <of> fact has a matching <in> fact). Obligations that read dynamic derived facts are left out,
    as GND leaves them out (transition._compiled_verdicts_for_dynamic_walk)."""
    from gnd import transition
    dynamic = {row.fact_type for row in transition.derivation_classifications(loaded.model_dump())
               if row.stability == "dynamic"}
    lines, table = [], []
    for op in model.doc.get("operations") or []:
        reads_dynamic = {pre["id"] for pre in op.get("preconditions") or []
                         if any(a.get("fact_type") in dynamic for a in pre.get("require") or [])}
        for entry in loaded.compiled_obligations(str(op["id"])):
            subset = entry.get("subset")
            if not subset or entry.get("obligation") in reads_dynamic:
                continue
            pairs = [tuple(pair) for pair in entry["role_pairs"]]
            left_roles = [r["role_name"] for r in model.roles(subset["of"])]
            variables = {left: f"$c_{left}" for left, _ in pairs}
            of = Atom(subset["of"], tuple(variables.get(r) or f"$o_{r}" for r in left_roles))
            right = {right_role: variables[left] for left, right_role in pairs}
            into = Atom(subset["in"], tuple(right.get(r["role_name"]) for r in model.roles(subset["in"])))
            of, into = _unswap(model, [of, into])
            types = {v: t for (_, t), v in zip(_relation_roles(model, of.relation), of.args)}
            key = f"compiled:{entry['locator']}"
            table.append({"key": key, "locator": entry["locator"], "modality": entry["modality"], "of": subset["of"],
                          "in": subset["in"], "roles": left_roles})
            lines.append(f"    #   compiled {entry['locator']}: every {subset['of']} fact has a matching {subset['in']} fact")
            lines.append(_declare(sorted(types), types, names))
            ordered = [names.var(v) for v in of.args]
            if target == "lqp":
                lines.append(f"    m.where({_atom_text(of, names, model)}).require({_atom_text(into, names, model)})")
            else:
                lines.append(f"    found[{key!r}] = rows(m.where({_atom_text(of, names, model)}, "
                             f"not_({_atom_text(into, names, model)})).select(step, {', '.join(ordered)}))")
    return lines, table


def _coverage(model: _Model, loaded: Any) -> dict[str, Any]:
    """What GND's three coverage gates require of the pre-population, per operation (gnd.transition)."""
    from gnd import transition
    rows = transition.derivation_classifications(loaded.model_dump())
    static = {r.fact_type: r for r in rows if r.stability == "static"}
    dynamic = {r.fact_type: r for r in rows if r.stability == "dynamic"}

    def reads(value: Any) -> set[str]:
        if isinstance(value, dict):
            found = {value["fact_type"]} if isinstance(value.get("fact_type"), str) else set()
            return found.union(*(reads(v) for v in value.values()))
        if isinstance(value, list):
            return set().union(*(reads(v) for v in value))
        return set()
    per_op = {}
    for op in loaded.operations:
        pre_reads = reads(op.get("preconditions") or [])
        per_op[op["id"]] = {
            "frame": sorted({e[v]["fact_type"] for e in op.get("effects") or [] for v in ("assert", "retract") if v in e}),
            "static": {h: sorted(static[h].asserted_dependencies) for h in sorted(pre_reads & set(static))},
            "dynamic": sorted(set(transition._dynamic_heads_for_step(loaded, op))
                              | ((pre_reads | reads(op.get("dynamic_rules") or [])) & set(dynamic))),
        }
    standing = set()
    for fact_id, fact_type in model.facts.items():
        if fact_id in dynamic and fact_type.get("constraints"):
            standing.add(fact_id)
        standing |= reads(fact_type.get("constraints") or []) & set(dynamic)
    standing |= reads(loaded.constraints) & set(dynamic)
    return {"ops": per_op, "standing": sorted(standing),
            "closure": {h: sorted({h, *dynamic[h].asserted_dependencies}) for h in dynamic},
            "multi_clause": any(isinstance(f.get("derivation_rule"), dict) and "clauses" in f["derivation_rule"]
                                for f in model.facts.values())}


def _plan_require_count(table: list[dict[str, Any]]) -> int:
    """One Require per statement: each precondition atom, each effect check, each comparable dynamic rule."""
    return sum(len(c.get("atoms") or []) if c["kind"] == "precondition" else (0 if c.get("functional") is False else 1)
               for c in table)


def _plan_constants(model: _Model, loaded: Any, table: list[dict[str, Any]], compiled: list[dict[str, Any]]) -> str:
    from gnd import transition
    operations = {op["id"]: {"params": _op_params(model, op), "effects": op.get("effects") or []}
                  for op in model.doc.get("operations") or []}
    return (f"MODEL_DIGEST = {transition.transition_model_identity(loaded)!r}\n"
            f"OPERATIONS_DIGEST = {transition.operations_digest(loaded.operations)!r}\n"
            f"OPERATIONS = json.loads({json.dumps(operations)!r})\n"
            f"STEP_CHECKS = json.loads({json.dumps(table)!r})\n"
            f"DERIVED = {list(model.derived)!r}\n"
            f"COMPILED = json.loads({json.dumps(compiled)!r})\n"
            f"COVERAGE = json.loads({json.dumps(_coverage(model, loaded))!r})\n")


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
    if reference and doc.get("operations"):
        for head in model.derived:
            if {a["fact_type"] for a in _rule_atoms(model.facts[head]["derivation_rule"])} & set(reference["owned"]):
                raise ExportInputError(f"fact type {head!r} is derived from reference facts in a model with operations; "
                                       "GND's plan walk computes it empty in later states (a checker bug), so there is "
                                       "no verdict to match")
    reqs = requirements(doc, model)
    names = _Names(model)
    plan_lines, step_table = _plan_checks(model, names, target) if names.step else ([], [])
    compiled_lines, compiled_table = _compiled_checks(model, loaded, names, target) if names.step else ([], [])
    plan_lines += compiled_lines
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
         f"REFERENCE = json.loads({json.dumps(reference)!r})\nLIMIT = 1 << 20\n"
         + (_plan_constants(model, loaded, step_table, compiled_table) if names.step else "")
         + f"PLAN_REQUIRES = {_plan_require_count(step_table) + len(compiled_table)}\n"),
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
        ("\ndef build(states, plan, config):\n" if names.step else "\ndef build(population, config):\n")
        + "    from relationalai.semantics import Boolean, Date, Field, Float, Integer, Model, String, not_  # noqa: F401\n"
        "    from relationalai.semantics.std import datetime as std_datetime  # noqa: F401\n"
        "    std_date, days = std_datetime.date, std_datetime.days  # noqa: F841\n"
        "    from relationalai.semantics.std import aggregates  # noqa: F401\n"
        "    from relationalai.semantics.std import math as std_math  # noqa: F401\n"
        "    m = Model(SCHEMA, config=config)\n"
        + ("    step, before = Integer.ref(), Integer.ref()   # a state of the plan, and the one before it\n"
           if names.step else
           "    facts = population['facts']\n"
           "    instances = population.get('instances', {})\n")
        + ("    found = {}\n" if target == "duckdb" else ""),
        "\n    # ---- facts: one relationship per fact type",
        *_relations(model, names),
    ]
    out += _derivations(model, names, target)
    universes = _universes(model, reqs, names) + _allowed(model, reqs, names) + _helpers(model, names, kinds=("reverse", "permute"))
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
    if names.step:
        out += plan_lines
    if target == "duckdb":
        out.append("    return found")
    else:
        first = next(f for f, fact in model.facts.items() if not isinstance(fact.get("derivation_rule"), dict))
        refs = ", ".join((["Integer.ref()"] if names.step else [])
                         + [f"{model.role_type(first, r['role_name'])}.ref()" for r in model.roles(first)])
        out.append(f"    probe_vars = [{refs}]")
        out.append(f"    return m, lambda: rows(m.where({names.relation(first)}(*probe_vars)).select(*probe_vars))")
    main = _DUCKDB_MAIN if target == "duckdb" else _LQP_MAIN
    if names.step:
        main = (main.replace("build({'facts': {}, 'population': {}}, config)", "build([{'facts': {}, 'population': {}}], [], config)")
                    .replace("m, probe = build(population, config)", "m, probe = build([population], [], config)"))
        if target == "duckdb":   # the plan main replaces the snapshot one
            main = main.replace("\nif __name__ == '__main__':\n    raise SystemExit(main())\n", "\n")
        main = _PLAN_HELPERS + main + (_PLAN_MAIN if target == "duckdb" else "")
    out.append(main)
    return "\n".join(out) + "\n"
