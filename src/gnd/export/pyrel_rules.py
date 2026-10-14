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
_TYPES = {"String": "String", "Integer": "Integer", "Float": "Float", "Boolean": "Boolean"}
_NEGATED = {"<": ">=", "<=": ">", "=": "!=", "!=": "==", ">=": "<", ">": "<="}
_PYOP = {"<": "<", "<=": "<=", "=": "==", "==": "==", "!=": "!=", ">=": ">=", ">": ">"}
_RESERVED = {"m", "not_", "Field", "String", "Integer", "Float", "Boolean", "Model", "Config",
             "rows", "facts", "report", "load", "json", "sys", "os", "re", "tempfile", "found", "x",
             "value", "values", "probe_vars", "instances", "population", "config", "build", "main",
             "read_population", "witnesses", "compile_only", "RULES", "SCHEMA", "LIMIT", "EXPECTED",
             "warnings", "create_config", "argparse", "args", "parser", "problems", "caught", "w",
             "directory", "error", "rule", "name", "hits", "hit", "status", "row", "rows_", "path",
             "document", "relation", "roles", "r", "v", "k", "f", "g", "key", "fact", "seen"}


@dataclass(frozen=True)
class Atom:
    relation: str
    args: tuple[Any, ...]          # "$name" variables, literals, or None for "any value"


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
    refs: tuple[str, ...] = field(default=())   # fact types the rule reads (coverage)


class _Model:
    """Model queries go through the read-only ModelIndex snapshot (RF6 query policy)."""

    def __init__(self, doc: dict[str, Any]):
        self.doc = doc
        self.index = ModelIndex(None, doc)
        self.objects = self.index.object_types_by_id()
        self._roles = self.index.role_object_types()
        self.facts = {fact_id: self.index.fact_type(fact_id) for fact_id in self._roles}

    def roles(self, fact_id: str) -> list[dict[str, Any]]:
        if fact_id not in self._roles:
            raise ExportInputError(f"unknown fact type {fact_id!r}")
        return [{"role_name": name, "object_type": object_id} for name, object_id in self._roles[fact_id].items()]

    def primitive(self, object_id: str) -> str:
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
        for side in ("left", "right"):
            if isinstance(payload.get(side), dict):
                raise ExportInputError(f"{c.get('id')}: function terms are a later phase")
        check = Check("compare", compare=Compare(payload["operator"], payload["left"], payload["right"]))
    else:
        raise ExportInputError(f"{c.get('id')}: consequent kind {kind!r} is not supported")
    if not _connected(domain):
        raise ExportInputError(f"{c.get('id')}: a disconnected antecedent is left unchecked by GND; "
                               "the rules programs refuse it rather than cross-join it")
    asserted = tuple(dict.fromkeys(a.relation for a in domain if not _is_derived(model, a.relation)))
    refs = tuple(dict.fromkeys([a.relation for a in domain] + ([check.atom.relation] if check.atom else [])))
    return Requirement(c["id"], "guarded", c["modality"], _quote(c), domain, check, _variables(domain),
                       ("any", asserted), refs)


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
    domain = (Atom(universe, ("$x",)),)
    check = Check("holds", atom=Atom(fact_id, tuple("$x" if r["role_name"] == role else None for r in roles)))
    return Requirement(c.get("id") or f"{fact_id}#mandatory", "mandatory", c["modality"], _quote(c),
                       domain, check, ("$x",), ("any", (fact_id,)), (fact_id,))


def _subset(model: _Model, c: dict[str, Any]) -> Requirement:
    sub, sup = c.get("subset_role_seq") or [], c.get("superset_role_seq") or []
    if len(sub) != len(sup) or not sub:
        raise ExportInputError(f"{c.get('id')}: subset role sequences must have equal length")
    for seq in (sub, sup):
        if len({ref["fact_type"] for ref in seq}) != 1:
            raise ExportInputError(f"{c.get('id')}: role sequences spanning fact types are a later phase")
    names = [f"$k{i}" for i in range(len(sub))]

    def atom_for(seq):
        fact_id = seq[0]["fact_type"]
        position = {ref["role"]: name for ref, name in zip(seq, names)}
        return Atom(fact_id, tuple(position.get(r["role_name"]) for r in model.roles(fact_id)))

    left, right = atom_for(sub), atom_for(sup)
    return Requirement(c["id"], "subset", c["modality"], _quote(c), (left,), Check("holds", atom=right),
                       tuple(names), ("all", (left.relation, right.relation)), (left.relation, right.relation))


def _value(model: _Model, c: dict[str, Any]) -> Requirement:
    if "allowed" not in c or not isinstance(c["allowed"], list):
        raise ExportInputError(f"{c.get('id')}: ranges are a later phase")
    object_id = c["object_type"]
    plays = tuple(dict.fromkeys(fact for fact, _ in model.plays(object_id)))
    return Requirement(c["id"], "value", c["modality"], _quote(c), (Atom(f"{object_id}_any", ("$x",)),),
                       Check("holds", atom=Atom(f"{c['id']}_allowed", ("$x",))), ("$x",), ("all", plays), plays)


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
        if obj.get("subtype_of"):
            raise ExportInputError(f"object type {obj['id']!r} is a subtype; subtype universes are a later phase "
                                   "of the rules programs")
    for fact_id, fact in _Model(doc).facts.items():
        if fact.get("derivation_rule") is not None or fact.get("derivation") in {"derived", "semiderived"}:
            raise ExportInputError(f"fact type {fact_id!r} is derived; GND compares claimed derived facts with "
                                   "computed ones, which the rules programs do not reproduce yet (later phase)")


def requirements(doc: dict[str, Any]) -> list[Requirement]:
    """Lower every supported constraint to one requirement, in model order. One walk for all families."""
    model = _Model(doc)
    _refuse_unsupported_model(doc)
    found: list[Requirement] = []
    for fact_id, fact in model.facts.items():
        for index, c in enumerate(fact.get("constraints") or []):
            c = {**c, "id": c.get("id") or f"{fact_id}#{index}"}
            if c["type"] == "mandatory":
                found.append(_mandatory(model, c, fact_id))
            elif c["type"] == "uniqueness":
                lowered = _uniqueness(model, c, fact_id)
                if lowered is not None:
                    found.append(lowered)
            else:
                raise ExportInputError(f"{c['id']}: family {c['type']!r} is a later phase of the rules programs")
    for c in doc.get("constraints", []):
        family = c.get("type")
        if family == "guarded":
            found.append(_guarded(model, c))
        elif family == "subset":
            found.append(_subset(model, c))
        elif family == "value":
            found.append(_value(model, c))
        else:
            raise ExportInputError(f"{c.get('id')}: family {family!r} is a later phase of the rules programs")
    return found


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

    def relation(self, name: str) -> str:
        if name not in self.relations:
            self.relations[name] = _ident(name, self.taken)
            self.taken.add(self.relations[name])
        return self.relations[name]

    def var(self, name: str) -> str:
        return _ident(name, self.taken)


def _types(model: _Model, req: Requirement) -> dict[str, str]:
    types: dict[str, str] = {}
    for atom in (*req.domain, *([req.check.atom] if req.check.atom else [])):
        roles = _relation_roles(model, atom.relation)
        for (role_name, primitive), arg in zip(roles, atom.args):
            if isinstance(arg, str) and arg.startswith("$"):
                types.setdefault(arg, primitive)
    return types


def _relation_roles(model: _Model, relation: str) -> list[tuple[str, str]]:
    if relation in model.facts:
        return [(r["role_name"], model.role_type(relation, r["role_name"])) for r in model.roles(relation)]
    if relation.endswith("_allowed"):
        constraint = next(c for c in model.doc.get("constraints", []) if f"{c.get('id')}_allowed" == relation)
        return [("value", model.primitive(constraint["object_type"]))]
    if relation.endswith("_any"):
        return [("member", model.primitive(relation[: -len("_any")]))]
    raise ExportInputError(f"unknown relation {relation!r}")


def _term(arg: Any, names: _Names, model: _Model, primitive: str) -> str:
    if isinstance(arg, str) and arg.startswith("$"):
        return names.var(arg)
    if arg is None:
        return f"{primitive}.ref()"
    return repr(arg)


def _atom_text(atom: Atom, names: _Names, model: _Model) -> str:
    roles = _relation_roles(model, atom.relation)
    args = ", ".join(_term(arg, names, model, primitive) for (_, primitive), arg in zip(roles, atom.args))
    return f"{names.relation(atom.relation)}({args})"


def _operand(value: Any, names: _Names) -> str:
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
    domain = ", ".join(_atom_text(a, names, model) for a in req.domain)
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
        lines.append(f"    x = {primitive}.ref()")
        for fact_id, role_name in model.plays(object_id):
            args = ", ".join("x" if r["role_name"] == role_name else f"{model.role_type(fact_id, r['role_name'])}.ref()"
                             for r in model.roles(fact_id))
            lines.append(f"    m.where({names.relation(fact_id)}({args})).define({rel}(x))")
        rosters = [object_id] + sorted(o for o, obj in model.objects.items()
                                       if (obj.get("reference") or {}).get("value_type") == object_id)
        lines.append(f"    for value in [v for key in {rosters!r} for v in instances.get(key, [])]:")
        lines.append(f"        m.define({rel}(value))")
    return lines


def _allowed(model: _Model, reqs: list[Requirement], names: _Names) -> list[str]:
    lines = []
    for c in model.doc.get("constraints", []):
        if c.get("type") == "value" and any(r.id == c["id"] for r in reqs):
            rel = names.relation(f"{c['id']}_allowed")
            primitive = model.primitive(c["object_type"])
            lines.append(f"    # {c['id']}: the declared list of allowed values")
            lines.append(f"    {rel} = m.Relationship(fields=[Field('value', {primitive})], short_name='{c['id']}_allowed')")
            lines.append(f"    m.define(*[{rel}(v) for v in {c['allowed']!r}])")
    return lines


def _relations(model: _Model, names: _Names) -> list[str]:
    lines = []
    for fact_id, fact in model.facts.items():
        fields = ", ".join(f"Field({r['role_name']!r}, {model.role_type(fact_id, r['role_name'])})"
                           for r in model.roles(fact_id))
        lines.append(f"    # {fact.get('reading', fact_id)}")
        lines.append(f"    {names.relation(fact_id)} = m.Relationship(fields=[{fields}], short_name={fact_id!r})")
        if not isinstance(fact.get("derivation_rule"), dict):
            roles = tuple(r["role_name"] for r in model.roles(fact_id))
            lines.append(f"    load(m, {names.relation(fact_id)}, facts.get({fact_id!r}, []), {roles!r})")
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
    if target == "lqp":
        lines.append(f"    {require_text(req, names, model)}")
    else:
        lines.append(f"    #   rule:      {require_text(req, names, model)}")
        lines.append("    #   violation: the facts that match the domain and fail the check")
        lines.append(f"    found[{req.id!r}] = rows({denial_text(req, names, model)})")
    return lines


def _require_count(req: Requirement) -> int:
    """PyRel compiles each statement passed to require() into its own Require node."""
    return len(req.check.pairs) if req.check.kind == "same" else 1


def _rules_table(reqs: list[Requirement]) -> str:
    rows = [{"id": r.id, "family": r.family, "modality": r.modality, "witness": list(r.witness),
             "vacuous_when": [r.vacuous_when[0], list(r.vacuous_when[1])], "requires": _require_count(r)}
            for r in reqs]
    return json.dumps(rows, indent=1)


_DUCKDB_MAIN = '''

def report(population, found):
    """One line per rule; exit 1 on any must-rule violation, else 2 if a rule was vacuous, else 0.

    A fact list the input does not provide is empty here, as in GND's checker.
    """
    facts = population['facts']
    violated = vacuous = False
    for rule in RULES:
        name = rule['id']
        mode, lists = rule['vacuous_when']
        empty = [not facts.get(ref) for ref in lists]
        if lists and (any(empty) if mode == 'any' else all(empty)):
            print(f'{name}  vacuous  (no facts for it to apply to)')
            vacuous = True
            continue
        hits = witnesses(rule, found[name])
        if not hits:
            print(f'{name}  OK')
        status = 'violated' if rule['modality'] == 'alethic' else 'warning'
        for hit in hits:
            print(f'{name}  {status}  {json.dumps(hit, sort_keys=True)}')
        violated = violated or (bool(hits) and status == 'violated')
    return 1 if violated else 2 if vacuous else 0


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


def render(model_path: Path, target: str) -> str:
    if target not in TARGETS:
        raise ExportInputError(f"target must be one of {TARGETS}")
    raw = Path(model_path).read_bytes()
    try:
        load_model_bytes(raw, source=str(model_path))
    except (ModelLoadError, ModelValidationError) as error:
        raise ExportInputError(f"invalid model: {error}") from error
    doc = _parse_document(raw.decode("utf-8"))
    model = _Model(doc)
    reqs = requirements(doc)
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
                  "reports vacuous rules and exit bands, which this version does not.\n\n"
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
    out = [
        f"# /// script\n# requires-python = \">=3.11,<3.14\"\n# dependencies = [\"relationalai=={PYREL_VERSION}\"]\n# ///",
        header.rstrip("\n").replace("Generated by", spanning_note + "Generated by", 1),
        "from __future__ import annotations\n\nimport json\nimport os\nimport re\nimport sys\nimport tempfile",
        f"\nSCHEMA = {schema!r}\nRULES = json.loads({_rules_table(reqs)!r})\nLIMIT = 1 << 20\n",
        ("\ndef read_population(path):\n"
        "    with open(path, 'rb') as handle:\n"
        "        raw = handle.read(LIMIT + 1)\n"
        "    if len(raw) > LIMIT:\n"
        "        raise ValueError('population larger than 1 MiB')\n"
        "    document = json.loads(raw)\n"
        "    if not isinstance(document.get('facts'), dict):\n"
        "        raise KeyError('facts')\n"
        "    covers = (document.get('population') or {}).get('covers')\n"
        "    if not isinstance(covers, list):\n"
        "        raise ValueError('the population must declare covers: the fact lists it vouches for')\n"
        "    # As in GND's checker, a fact list the input does not cover is treated as empty.\n"
        "    document['facts'] = {name: document['facts'].get(name, []) for name in covers}\n"
        "    for fact_type, rows_ in document['facts'].items():\n"
        "        seen = set()\n"
        "        for row in rows_:\n"
        "            key = json.dumps(row, sort_keys=True)\n"
        "            if key in seen:\n"
        "                raise ValueError(f'duplicate rows in {fact_type}: PyRel relations are sets, so '\n"
        "                                 'repeated facts cannot be checked here; GND reports them')\n"
        "            seen.add(key)\n"
        "    return document\n"),
        ("\ndef load(m, relation, rows, roles):\n"
        "    if rows:\n"
        "        m.define(*[relation(*[row[r] for r in roles]) for row in rows])\n"),
        ("\ndef rows(query):\n"
        "    return sorted(list(row) for row in query.to_df().itertuples(index=False, name=None))\n"),
        "\ndef build(population, config):\n"
        "    from relationalai.semantics import Boolean, Field, Float, Integer, Model, String, not_  # noqa: F401\n"
        "    m = Model(SCHEMA, config=config)\n"
        "    facts = population['facts']\n"
        "    instances = population.get('instances', {})\n"
        + ("    found = {}\n" if target == "duckdb" else ""),
        "\n    # ---- facts: one relationship per fact type",
        *_relations(model, names),
    ]
    universes = _universes(model, reqs, names) + _allowed(model, reqs, names)
    if universes:
        out += ["\n    # ---- helper relations the rules refer to", *universes]
    out.append("\n    # ---- rules: `require` says what must hold")
    for req in reqs:
        out += _rule_block(req, model, names, target)
    for rule_id in spanning:
        out.append(f"    # {rule_id}: spanning uniqueness, broken only by a repeated fact; the input is refused instead")
    if target == "duckdb":
        out.append("    return found")
    else:
        first = next(f for f, fact in model.facts.items() if not isinstance(fact.get("derivation_rule"), dict))
        refs = ", ".join(f"{model.role_type(first, r['role_name'])}.ref()" for r in model.roles(first))
        out.append(f"    probe_vars = [{refs}]")
        out.append(f"    return m, lambda: rows(m.where({names.relation(first)}(*probe_vars)).select(*probe_vars))")
    out.append(_DUCKDB_MAIN if target == "duckdb" else _LQP_MAIN)
    return "\n".join(out) + "\n"
