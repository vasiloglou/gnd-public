"""Offline lowering of explicit finite carriers and positive acyclic models."""

import re
from dataclasses import replace
from datetime import date

from gnd.artifacts import canonical_json_bytes
from gnd.model import derivation_dependencies, iter_derivation_clauses
from gnd.witness import io as witness_io
from gnd.witness.types import DEFAULT_LIMITS as WITNESS_LIMITS

from .lean_types import DEFAULT_LIMITS, LeanResult, checked_limits, refused
from .souffle import INPUT_ERRORS, Unsupported, digest, parse

PROFILE = "lean-finite-acyclic-v1"
PIN = re.compile(r"leanprover/lean4:v[1-9][0-9]*\.[0-9]+\.[0-9]+\Z")
UTILS = """def dateAdd (d n : Nat) : Option Nat :=
  let result := d + n
  if 1 ≤ result && result ≤ 3652059 then some result else none

def dateSub (d n : Nat) : Option Nat :=
  if n < d then some (d - n) else none

def compareDeadline (d n limit : Nat) : Outcome :=
  match dateAdd d n with
  | none => .unchecked
  | some result => if result ≤ limit then .satisfied else .violated

def summarize (outcomes : List Outcome) : Outcome :=
  if outcomes.isEmpty then .vacuous else
  if outcomes.contains .violated then .violated else
  if outcomes.contains .unchecked then .unchecked else .satisfied"""


class WorkLimit(ValueError):
    pass


def scalar(value, primitive):
    if primitive in {"String", "Date"} and type(value) is str:
        if primitive == "Date" and date.fromisoformat(value).isoformat() != value:
            raise Unsupported("date")
        return value
    if primitive == "Boolean" and type(value) is bool:
        return value
    if primitive == "Integer" and type(value) is int:
        return value
    if primitive == "Duration" and type(value) is int and value >= 0:
        return value
    raise Unsupported("primitive value")


def tuple_expr(values):
    return values[0] if len(values) == 1 else "(" + ", ".join(values) + ")"


def list_expr(values):
    return "[" + ", ".join(values) + "]"


def component(name, index, arity):
    return name if arity == 1 else name + ".2" * index + (".1" if index < arity - 1 else "")


def constraints(md):
    rows = [
        (f"/fact_types/{i}/constraints/{n}", c, i)
        for i, f in enumerate(md["fact_types"])
        for n, c in enumerate(f.get("constraints", []))
    ]
    rows += [(f"/constraints/{i}", c, None) for i, c in enumerate(md.get("constraints", []))]
    rows += [
        (f"/rejected_proposals/{i}", c, None)
        for i, c in enumerate(md.get("rejected_proposals", []))
    ]
    return rows


class Renderer:
    def __init__(self, md, model, candidate, refs, limits):
        self.md, self.model, self.candidate, self.refs, self.limits = (
            md,
            model,
            candidate,
            refs,
            limits,
        )
        self.types, self.facts = model.object_types, model.fact_types
        self.ti = {t["id"]: i for i, t in enumerate(self.types)}
        self.fi = {f["id"]: i for i, f in enumerate(self.facts)}
        self.owners = {fid: d["id"] for d in model.reference_populations for fid in d["fact_types"]}
        self.fixed_types = {
            self.ti[r["object_type"]]
            for f in self.facts
            if f["id"] in self.owners
            for r in f["roles"]
        }
        self.fixed_types.update(self.ti[tid] for pop in refs.values() for tid in pop.instances)
        self.cs = constraints(md)
        self.active = [
            c.get("status") != "rejected" and not a.startswith("/rejected_proposals/")
            for a, c, _ in self.cs
        ]
        self.clauses = {
            i: list(iter_derivation_clauses(f.get("derivation_rule")))
            for i, f in enumerate(self.facts)
            if f.get("derivation")
        }
        self.rows = {
            i: (refs[self.owners[f["id"]]] if f["id"] in self.owners else candidate).facts.get(
                f["id"], []
            )
            for i, f in enumerate(self.facts)
        }
        self.values = [[] for _ in self.types]
        self.value_sets = [set() for _ in self.types]
        self.value_count = 0
        self.extents = [set() for _ in self.types]
        self.fixed_extents = [set() for _ in self.types]
        self.visits = 0

    def charge(self, n=1):
        self.visits += n
        if self.visits > self.limits.emission_visits:
            raise WorkLimit()

    def add(self, i, v):
        v = scalar(v, self.types[i]["primitive"])
        self.charge()
        if v not in self.value_sets[i]:
            self.value_count += 1
            if self.value_count > self.limits.carrier_values:
                raise ValueError("carrier ceiling")
            self.value_sets[i].add(v)
            self.values[i].append(v)
        return v

    def roles(self, i):
        return self.facts[i]["roles"]

    def rel(self, i, p="p"):
        return (
            f"(r{i} {p})"
            if i in self.clauses or self.facts[i]["id"] in self.owners
            else f"{p}.r{i}"
        )

    def row(self, i, row):
        return tuple_expr(
            [
                str(self.values[self.ti[r["object_type"]]].index(row[r["role_name"]]))
                for r in self.roles(i)
            ]
        )

    def classify(self):
        counts = {
            "object_types": len(self.types),
            "fact_types": len(self.facts),
            "clauses": sum(map(len, self.clauses.values())),
            "constraints": len(self.cs),
            "input_rows": sum(map(len, self.rows.values())),
        }
        if any(v > getattr(self.limits, k) for k, v in counts.items()) or any(
            len(f["roles"]) > self.limits.roles for f in self.facts
        ):
            raise ValueError("shape ceiling")
        if self.model.operations or any(
            t.get("kind") != "value"
            or t.get("derivation")
            or t.get("derivation_rule")
            or t.get("subtype_of")
            or t.get("primitive") not in {"String", "Boolean", "Integer", "Date", "Duration"}
            for t in self.types
        ):
            raise Unsupported("object/transition fragment")
        deps = derivation_dependencies(self.md)
        seen, visiting, order = set(), set(), []

        def walk(fid):
            if fid in visiting:
                raise Unsupported("cycle")
            if fid in seen:
                return
            visiting.add(fid)
            for d in sorted(deps.get(fid, [])):
                walk(d)
            visiting.remove(fid)
            seen.add(fid)
            if self.fi[fid] in self.clauses:
                order.append(self.fi[fid])

        for f in self.facts:
            walk(f["id"])
        self.order = order
        for i, f in enumerate(self.facts):
            pop = self.refs[self.owners[f["id"]]] if f["id"] in self.owners else self.candidate
            if i in self.clauses:
                if (
                    f["derivation"] != "derived"
                    or not isinstance(f.get("derivation_rule"), dict)
                    or not self.clauses[i]
                    or self.rows[i]
                ):
                    raise Unsupported("opaque/asserted derivation")
                for c in self.clauses[i]:
                    if c.get("negate") or c.get("aggregate") or c.get("where"):
                        raise Unsupported("clause fragment")
                    for terms in [c["head"]] + [a["bind"] for a in c["body"]]:
                        if any(isinstance(v, (dict, list)) for v in terms.values()):
                            raise Unsupported("clause terms")
            elif f["id"] not in pop.covers:
                raise Unsupported("partial")
        for active, (_, c, i) in zip(self.active, self.cs):
            if not active:
                continue
            typ = c["type"]
            if typ == "mandatory" and i is not None and c.get("role"):
                continue
            if (
                typ == "uniqueness"
                and i is not None
                and c.get("scope", "internal") == "internal"
                and c.get("roles")
            ):
                continue
            if typ == "subset":
                if any(
                    len({r["fact_type"] for r in c[k]}) != 1
                    for k in ["subset_role_seq", "superset_role_seq"]
                ):
                    raise Unsupported("joined subset")
                continue
            if typ == "guarded" and set(c["consequent"]) == {"comparison"}:
                bindings = self.bindings(
                    c["antecedent"], ["a" + str(n) for n in range(len(c["antecedent"]))]
                )[0]
                self.comparison(c["consequent"]["comparison"], bindings)
                continue
            raise Unsupported("constraint family")
        return counts

    def carriers(self):
        for pop in [self.candidate, *self.refs.values()]:
            for tid, vs in pop.instances.items():
                i = self.ti[tid]
                for v in vs:
                    self.extents[i].add(self.add(i, v))
                    if pop is not self.candidate:
                        self.fixed_extents[i].add(v)
        for i, rs in self.rows.items():
            for row in rs:
                for r in self.roles(i):
                    t = self.ti[r["object_type"]]
                    v = self.add(t, row[r["role_name"]])
                    self.extents[t].add(v)
                    if self.facts[i]["id"] in self.owners:
                        self.fixed_extents[t].add(v)
        for i, cs in self.clauses.items():
            for c in cs:
                for fid, terms in [(self.facts[i]["id"], c["head"])] + [
                    (a["fact_type"], a["bind"]) for a in c["body"]
                ]:
                    for r in self.roles(self.fi[fid]):
                        v = terms[r["role_name"]]
                        if not (type(v) is str and v.startswith("$")):
                            self.add(self.ti[r["object_type"]], v)
        for active, (_, c, _) in zip(self.active, self.cs):
            if active and c["type"] == "guarded":
                for atom in c["antecedent"]:
                    for role in self.roles(self.fi[atom["fact_type"]]):
                        v = atom["bind"][role["role_name"]]
                        if not (type(v) is str and v.startswith("$")):
                            self.add(self.ti[role["object_type"]], v)
        for vs in self.values:
            vs.sort()
        if sum(map(len, self.values)) > self.limits.carrier_values:
            raise ValueError("carrier ceiling")
        self.ext = [
            list_expr([str(vs.index(v)) for v in sorted(es)])
            for vs, es in zip(self.values, self.extents)
        ]
        self.fixed = [
            list_expr([str(vs.index(v)) for v in sorted(es)])
            for vs, es in zip(self.values, self.fixed_extents)
        ]

    def bindings(self, atoms, names):
        bindings, equalities = {}, []
        for atom, name in zip(atoms, names):
            i = self.fi[atom["fact_type"]]
            for n, r in enumerate(self.roles(i)):
                v = atom["bind"][r["role_name"]]
                t = self.ti[r["object_type"]]
                expr = component(name, n, len(self.roles(i)))
                if type(v) is str and v.startswith("$"):
                    if v in bindings:
                        old, ot = bindings[v]
                        if ot != t:
                            raise Unsupported("cross-carrier variable")
                        equalities.append(old + " == " + expr)
                    else:
                        bindings[v] = (expr, t)
                else:
                    scalar(v, self.types[t]["primitive"])
                    # During classification the carrier has not yet been collected.
                    ordinal = self.values[t].index(v) if v in self.values[t] else 0
                    equalities.append(expr + " == " + str(ordinal))
        return bindings, equalities

    def primitive_expr(self, term, bindings, expected=None):
        if type(term) is str and term.startswith("$"):
            e, t = bindings[term]
            p = self.types[t]["primitive"]
            return f"(v{t} {e})", p, None
        if isinstance(term, dict):
            if set(term) == {"date"}:
                value = scalar(term["date"], "Date")
                return str(date.fromisoformat(value).toordinal()), "Date", None
            if set(term) == {"duration_days"}:
                v = scalar(term["duration_days"], "Duration")
                return str(v), "Duration", None
            if term.get("fn") not in {"date_add", "date_sub"} or len(term.get("args", [])) != 2:
                raise Unsupported("guard term")
            a, p, option = self.primitive_expr(term["args"][0], bindings, "Date")
            b, q, _ = self.primitive_expr(term["args"][1], bindings)
            if p != "Date" or q != "Duration":
                raise Unsupported("temporal operands")
            fn = "dateAdd" if term["fn"] == "date_add" else "dateSub"
            expression = f"({a}).bind (fun d => {fn} d {b})" if option else f"{fn} {a} {b}"
            return expression, "Date", "option"
        p = (
            "Boolean"
            if type(term) is bool
            else "Integer"
            if type(term) is int
            else "Date"
            if expected == "Date"
            else "String"
        )
        value = scalar(term, p)
        if p == "String":
            # Pure literals never enter source text: their equalities reduce to
            # rank identities assigned from a deterministic private string set.
            return (
                str(self.string_values.index(value)) if hasattr(self, "string_values") else "0",
                p,
                None,
            )
        return (
            str(date.fromisoformat(value).toordinal())
            if p == "Date"
            else "true"
            if value is True
            else "false"
            if value is False
            else str(value),
            p,
            None,
        )

    def comparison(self, cmp, bindings):
        left, p, lo = self.primitive_expr(cmp["left"], bindings)
        right, q, ro = self.primitive_expr(cmp["right"], bindings, p)
        if type(cmp["left"]) is str and not cmp["left"].startswith("$"):
            left, p, lo = self.primitive_expr(cmp["left"], bindings, q)
        op = cmp["operator"]
        if p != q or (p in {"String", "Boolean"} and op not in {"=", "!="}):
            raise Unsupported("comparison types")
        operator = {"=": "==", "!=": "!=", "<": "<", "<=": "≤", ">": ">", ">=": "≥"}[op]
        if lo or ro:
            clauses = []
            if lo:
                clauses.append(left)
            if ro:
                clauses.append(right)
            expr = (
                f"x {operator} y"
                if lo and ro
                else f"x {operator} {right}"
                if lo
                else f"{left} {operator} x"
            )
            return (
                "match "
                + ", ".join(clauses)
                + " with\n"
                + ("| some x, some y" if lo and ro else "| some x")
                + f" => if {expr} then .satisfied else .violated\n| "
                + ("_, _" if lo and ro else "none")
                + " => .unchecked"
            )
        # Type annotations prevent default Nat interpretation of signed literals.
        typ = {"Integer": "Int", "Boolean": "Bool"}.get(p, "Nat")
        return f"if ({left} : {typ}) {operator} ({right} : {typ}) then .satisfied else .violated"

    def joins(self, atoms, names, leaf, guards):
        wrapped = leaf if leaf.startswith("(") else "(" + leaf + ")"
        expr = (
            ("if " + " && ".join(guards) + " then some " + wrapped + " else none")
            if guards
            else "some " + wrapped
        )
        if not atoms:
            return list_expr([leaf])
        for n in reversed(range(len(atoms))):
            rel = self.rel(self.fi[atoms[n]["fact_type"]])
            name = names[n]
            expr = (
                rel
                + (".filterMap" if n == len(atoms) - 1 else ".flatMap")
                + f" (fun {name} => "
                + expr
                + ")"
            )
        return expr

    def clause(self, i, n, c):
        atoms = c["body"]
        names = [chr(97 + k) if k < 26 else "a" + str(k) for k in range(len(atoms))]
        bindings, guards = self.bindings(atoms, names)
        head = []
        for r in self.roles(i):
            v = c["head"][r["role_name"]]
            t = self.ti[r["object_type"]]
            if type(v) is str and v.startswith("$"):
                expr, ot = bindings[v]
                if ot != t:
                    raise Unsupported("head carrier")
                head.append(expr)
            else:
                head.append(str(self.values[t].index(v)))
        # Identity projection has the exact compact spelling frozen in goldens.
        if (
            len(atoms) == 1
            and not guards
            and tuple_expr(head)
            == tuple_expr([component(names[0], k, len(head)) for k in range(len(head))])
        ):
            return (
                f"def clause{i}_{n} (p : Population) : List {self.relation_type(i)} := "
                + self.rel(self.fi[atoms[0]["fact_type"]]).strip("()")
            )
        expr = self.joins(atoms, names, tuple_expr(head), guards)
        if len(atoms) == 2 and names == ["a", "b"]:
            expr = expr.replace(".flatMap (fun a => ", ".flatMap (fun a => ", 1)
            expr = expr.replace(".filterMap (fun b => ", ".filterMap\n    (fun b => ", 1)
        return f"def clause{i}_{n} (p : Population) : List {self.relation_type(i)} :=\n  " + expr

    def relation_type(self, i):
        types = ["T" + str(self.ti[r["object_type"]]) for r in self.roles(i)]
        return types[0] if len(types) == 1 else "(" + " × ".join(types) + ")"

    def family(self, n, c, i):
        typ = c["type"]
        name = f"def c{n} (p : Population) : Outcome :=\n  "
        if typ in {"mandatory", "uniqueness"}:
            rs = self.roles(i)
            rel = self.rel(i)
            if typ == "mandatory":
                k = next(k for k, r in enumerate(rs) if r["role_name"] == c["role"])
                t = self.ti[rs[k]["object_type"]]
                return (
                    name
                    + f"if p.e{t}.isEmpty then .vacuous else\n  if p.e{t}.all (fun j => {rel}.any (fun r => {component('r', k, len(rs))} == j)) then .satisfied else .violated"
                )
            keys = [k for k, r in enumerate(rs) if r["role_name"] in c["roles"]]
            different = " || ".join(
                f"{component('a.1', k, len(rs))} != {component('b.1', k, len(rs))}" for k in keys
            )
            return (
                name
                + f"if {rel}.isEmpty then .vacuous else\n  if {rel}.zipIdx.all (fun a => {rel}.zipIdx.all (fun b => {different} || a.2 == b.2))\n    then .satisfied else .violated"
            )
        if typ == "subset":
            left, right = c["subset_role_seq"], c["superset_role_seq"]
            a = self.fi[left[0]["fact_type"]]
            b = self.fi[right[0]["fact_type"]]

            def projection(seq, name, idx):
                rs = self.roles(idx)
                return tuple_expr(
                    [
                        component(
                            name,
                            next(k for k, r in enumerate(rs) if r["role_name"] == x["role"]),
                            len(rs),
                        )
                        for x in seq
                    ]
                )

            l = projection(left, "r", a)
            r = projection(right, "s", b)
            rs = self.roles(b)
            sup = (
                self.rel(b) if len(rs) == len(right) == 1 else f"({self.rel(b)}.map (fun s => {r}))"
            )
            return (
                name
                + f"if {self.rel(a)}.isEmpty then .satisfied else\n  if {self.rel(a)}.all (fun r => {sup}.contains {l}) then .satisfied else .violated"
            )
        atoms = c["antecedent"]
        names = (
            ["start", "due", "window"]
            if len(atoms) == 3
            else ["a" + str(k) for k in range(len(atoms))]
        )
        bindings, guards = self.bindings(atoms, names)
        cmp = c["consequent"]["comparison"]
        left = cmp["left"]
        fast = (
            isinstance(left, dict)
            and left.get("fn") == "date_add"
            and cmp["operator"] == "<="
            and type(cmp["right"]) is str
            and cmp["right"] in bindings
            and self.primitive_expr(left["args"][0], bindings, "Date")[2] is None
        )
        if fast:
            expressions = [
                self.primitive_expr(t, bindings)[0] for t in [*left["args"], cmp["right"]]
            ]
            leaf = "compareDeadline " + " ".join(expressions)
        else:
            leaf = "(" + self.comparison(cmp, bindings) + ")"
        expr = self.joins(atoms, names, leaf, guards)
        if len(atoms) == 3:
            expr = expr.replace(".flatMap (fun start => ", ".flatMap (fun start => ", 1)
            expr = expr.replace(".flatMap (fun due => ", ".flatMap (fun due =>\n    ", 1)
            expr = expr.replace(
                ".filterMap (fun window => ", ".filterMap (fun window =>\n      ", 1
            )
            expr = expr.replace(" then some (", "\n      then some (", 1)
            expr = expr.replace(" else none", "\n      else none", 1)
        return name.replace("\n  ", " summarize <|\n  ", 1) + expr

    def render(self):
        self.charge(
            len(self.types) + len(self.facts) + len(self.cs) + sum(map(len, self.rows.values()))
        )
        # Preflight every prospective tuple interpretation and join product;
        # charge before building strings or doing native work, not afterwards.
        bounds = {}
        for i in self.order + [k for k in range(len(self.facts)) if k not in self.clauses]:
            bounds[i] = 1
            for r in self.roles(i):
                bounds[i] *= len(self.values[self.ti[r["object_type"]]])
                if bounds[i] > self.limits.emission_visits:
                    raise WorkLimit()
        for i, cs in self.clauses.items():
            for c in cs:
                amount = 1
                for a in c["body"]:
                    amount *= bounds[self.fi[a["fact_type"]]]
                    if amount > self.limits.emission_visits:
                        raise WorkLimit()
                self.charge(amount)
        for active, (_, c, _) in zip(self.active, self.cs):
            if not active:
                continue
            if c["type"] == "guarded":
                amount = 1
                for a in c["antecedent"]:
                    amount *= bounds[self.fi[a["fact_type"]]]
                    if amount > self.limits.emission_visits:
                        raise WorkLimit()
                self.charge(amount)
        # Literal String comparisons are encoded by ordinal ranks, never text.
        strings = {
            v
            for i, t in enumerate(self.types)
            if t["primitive"] == "String"
            for v in self.values[i]
        }

        def literals(x):
            if isinstance(x, dict):
                for v in x.values():
                    yield from literals(v)
            elif isinstance(x, list):
                for v in x:
                    yield from literals(v)
            elif type(x) is str and not x.startswith("$"):
                yield x

        for active, (_, c, _) in zip(self.active, self.cs):
            if active and c["type"] == "guarded":
                strings.update(literals(c["consequent"]["comparison"]))
        self.string_values = sorted(strings)
        parts = [
            "import Init\n\nnamespace GND\n\ninductive Outcome where\n  | satisfied | violated | vacuous | unchecked\n  deriving DecidableEq, Repr"
        ]
        parts.append("\n".join(f"abbrev T{i} := Fin {len(v)}" for i, v in enumerate(self.values)))
        decoders = []
        needed_strings = set()
        for active, (_, c, _) in zip(self.active, self.cs):
            if active and c["type"] == "guarded":
                bound = self.bindings(
                    c["antecedent"], ["a" + str(n) for n in range(len(c["antecedent"]))]
                )[0]

                def variables(x):
                    if isinstance(x, dict):
                        for v in x.values():
                            yield from variables(v)
                    elif isinstance(x, list):
                        for v in x:
                            yield from variables(v)
                    elif type(x) is str and x.startswith("$"):
                        yield x

                for v in variables(c["consequent"]["comparison"]):
                    _, t = bound[v]
                    if self.types[t]["primitive"] == "String":
                        needed_strings.add(t)
        for i, (t, vs) in enumerate(zip(self.types, self.values)):
            p = t["primitive"]
            if p == "String" and i not in needed_strings:
                continue
            typ = {"Integer": "Int", "Boolean": "Bool"}.get(p, "Nat")
            vals = [
                date.fromisoformat(v).toordinal()
                if p == "Date"
                else self.string_values.index(v)
                if p == "String"
                else v
                for v in vs
            ]
            if p == "Boolean" and vals == [False, True]:
                body = "fun x => x.val != 0"
            elif len(vals) == 1:
                body = "fun _ => " + (
                    "true" if vals[0] is True else "false" if vals[0] is False else str(vals[0])
                )
            else:
                body = (
                    "fun x => "
                    + "".join(
                        f"if x.val == {n} then "
                        + ("true" if v is True else "false" if v is False else str(v))
                        + " else "
                        for n, v in enumerate(vals[:-1])
                    )
                    + (
                        "true"
                        if vals and vals[-1] is True
                        else "false"
                        if vals and vals[-1] is False
                        else str(vals[-1])
                        if vals
                        else "false"
                        if p == "Boolean"
                        else "0"
                    )
                )
            decoders.append(f"def v{i} : T{i} → {typ} := {body}")
        if decoders:
            parts.append("\n".join(decoders))
        variable = [
            i
            for i, f in enumerate(self.facts)
            if i not in self.clauses and f["id"] not in self.owners
        ]
        fields = [f"  e{i} : List T{i}" for i in range(len(self.types))] + [
            f"  r{i} : List {self.relation_type(i)}" for i in variable
        ]
        parts.append("structure Population where\n" + "\n".join(fields) + "\n  deriving Repr")
        relations = []
        for i, f in enumerate(self.facts):
            if f["id"] in self.owners:
                relations.append(
                    f"def r{i} (_ : Population) : List {self.relation_type(i)} := "
                    + list_expr([self.row(i, r) for r in self.rows[i]])
                )
        for i in self.order:
            relations.extend(self.clause(i, n, c) for n, c in enumerate(self.clauses[i]))
            relations.append(
                f"def r{i} (p : Population) : List {self.relation_type(i)} := ("
                + " ++ ".join(f"clause{i}_{n} p" for n in range(len(self.clauses[i])))
                + ").eraseDups"
            )
        if relations:
            parts.append("\n".join(relations))
        wt = [
            f"{fixed}.all (fun n => p.e{i}.contains n)"
            for i, fixed in enumerate(self.fixed)
            if self.fixed_extents[i]
        ]
        for i in sorted(self.fixed_types):
            if len(self.fixed_extents[i]) != len(self.values[i]):
                wt.append(f"p.e{i}.all (fun n => {self.fixed[i]}.contains n)")
        literal_heads = [
            i
            for i, clauses in self.clauses.items()
            if any(
                not (type(v) is str and v.startswith("$"))
                for c in clauses
                for v in c["head"].values()
            )
        ]
        for i in variable + literal_heads:
            rs = self.roles(i)
            relation = self.rel(i)
            wt.append(
                f"{relation}.all (fun r => "
                + " && ".join(
                    f"p.e{self.ti[r['object_type']]}.contains {component('r', k, len(rs))}"
                    for k, r in enumerate(rs)
                )
                + ")"
            )
        parts.append(
            "def wellTyped (p : Population) : Bool :=\n  " + " &&\n  ".join(wt or ["true"])
        )
        parts.append(
            "def nonempty (p : Population) : Bool :=\n  !("
            + " && ".join(
                f"p.e{i}.isEmpty" for i in range(len(self.types)) if i not in self.fixed_types
            )
            + (")" if any(i not in self.fixed_types for i in range(len(self.types))) else "true)")
        )
        parts.append("def holds (o : Outcome) : Bool := o == .satisfied || o == .vacuous")
        added = False
        for n, (active, (_, c, i)) in enumerate(zip(self.active, self.cs)):
            if not active:
                continue
            if c["type"] == "guarded" and not added:
                parts.append(UTILS)
                added = True
            parts.append(self.family(n, c, i))
        if not added:
            parts.append(UTILS)
        hard = [
            n
            for n, (active, (_, c, _)) in enumerate(zip(self.active, self.cs))
            if active and c.get("modality", "alethic") == "alethic"
        ]

        def conjunction(ns):
            return " && ".join(f"holds (c{n} p)" for n in ns) or "true"

        parts.append("def hard (p : Population) : Bool :=\n  " + conjunction(hard))
        parts.append(
            "\n".join(
                f"def without{n} (p : Population) : Bool := "
                + conjunction([k for k in hard if k != n])
                for n, a in enumerate(self.active)
                if a
            )
        )
        extfields = [f"e{i} := {v}" for i, v in enumerate(self.ext)]
        rowfields = [
            f"r{i} := " + list_expr([self.row(i, r) for r in self.rows[i]]) for i in variable
        ]

        def wrap(fields, width=90):
            lines = []
            line = "  "
            for field in fields:
                if len(line + field + ", ") > width and line != "  ":
                    lines.append(line.rstrip())
                    line = "  "
                line += field + ", "
            if line != "  ":
                lines.append(line.rstrip())
            return "\n".join(lines)

        parts.append(
            "def concrete : Population := {\n"
            + wrap(extfields)
            + "\n"
            + wrap(rowfields, 70).rstrip(",")
            + " }"
        )
        obligations = [
            "def concreteWitness : Prop := wellTyped concrete = true ∧ nonempty concrete = true ∧ hard concrete = true",
            "def satisfiability : Prop := ∃ p, wellTyped p = true ∧ nonempty p = true ∧ hard p = true",
        ]
        obligations.extend(
            f"def redundant{n} : Prop := ∀ p, wellTyped p = true → without{n} p = true → holds (c{n} p) = true"
            for n, a in enumerate(self.active)
            if a
        )
        parts.append("\n".join(obligations))
        return "\n\n".join(parts) + "\n\nend GND\n"


def render_lean(
    model_bytes,
    candidate_bytes,
    *,
    toolchain,
    model_format="json",
    candidate_format="json",
    reference_inputs=(),
    limits=DEFAULT_LIMITS,
):
    try:
        checked_limits(limits)
        if not isinstance(toolchain, str) or not PIN.fullmatch(toolchain):
            raise ValueError("pin")
        md, pd = (
            parse(model_bytes, model_format, limits),
            parse(candidate_bytes, candidate_format, limits),
        )
        if type(md) is not dict or type(md.get("version", 1)) is not int:
            raise ValueError("model version")
        wl = replace(
            WITNESS_LIMITS,
            bytes=limits.document_bytes,
            container_depth=limits.container_depth,
            scalar_bytes=limits.scalar_bytes,
            numeric_digits=limits.numeric_digits,
        )
        model, candidate, refs = witness_io.intake(md, pd, reference_inputs, limits=wl)
        r = Renderer(md, model, candidate, refs, limits)
        counts = r.classify()
        r.carriers()
        definitions = r.render().encode()
        carriers = [
            {
                "object_type": t["id"],
                "primitive": t["primitive"],
                "symbol": f"T{i}",
                "values": [{"ordinal": n, "value": v} for n, v in enumerate(r.values[i])],
            }
            for i, t in enumerate(r.types)
        ]
        cd = digest(canonical_json_bytes(carriers))
        sm = {
            "version": 1,
            "kind": "lean-source-map",
            "encoding": "lean-ordinal-v1",
            "carriers": carriers,
            "relations": [
                {"address": f"/fact_types/{i}", "symbol": f"r{i}"} for i in range(len(r.facts))
            ],
            "clauses": [
                {
                    "address": f"/fact_types/{i}/derivation_rule/"
                    + (f"clauses/{n}" if "clauses" in f["derivation_rule"] else "body"),
                    "symbol": f"clause{i}_{n}",
                }
                for i, f in enumerate(r.facts)
                for n, _ in enumerate(r.clauses.get(i, []))
            ],
            "constraints": [
                {"address": a, "symbol": f"c{i}"} for i, (a, _, _) in enumerate(r.cs) if r.active[i]
            ],
            "origins": [],
        }
        for i, f in enumerate(r.facts):
            for n, _ in enumerate(r.rows[i]):
                owner = r.owners.get(f["id"])
                sm["origins"].append(
                    {
                        "fact_type": f["id"],
                        "source_ordinal": n,
                        "origin": {
                            "kind": "reference" if owner else "candidate",
                            "reference_id": owner,
                            "fact_index": n,
                        },
                    }
                )
        entries = []
        for n, (a, c, _) in enumerate(r.cs):
            active = r.active[n]
            entries.append(
                {
                    "address": a,
                    "id": c.get("id"),
                    "type": c["type"],
                    "modality": c.get("modality", "alethic"),
                    "activity": "active" if active else "inactive",
                    "predicate": f"c{n}" if active else None,
                    "query_kind": (
                        "alethic-redundancy"
                        if c.get("modality", "alethic") == "alethic"
                        else "deontic-policy-entailment"
                    )
                    if active
                    else None,
                    "proposition": f"redundant{n}" if active else None,
                    "status": "unproved" if active else "not-applicable",
                }
            )
        ob = {
            "version": 1,
            "kind": "lean-obligations",
            "support_profile": PROFILE,
            "carrier_sha256": cd,
            "concrete_witness": {
                "symbol": "witness_obligation",
                "proposition": "concreteWitness",
                "status": "unproved",
            },
            "satisfiability": {
                "symbol": "satisfiability_obligation",
                "proposition": "satisfiability",
                "status": "unproved",
            },
            "constraints": entries,
        }
        stubs = (
            "import Definitions\n\nnamespace GND\n\n-- Every theorem below is an UNPROVED template. Successful elaboration is not discharge.\ntheorem witness_obligation : concreteWitness := by sorry\ntheorem satisfiability_obligation : satisfiability := by sorry\n"
            + "".join(
                f"theorem constraint_obligation{n} : redundant{n} := by sorry\n"
                for n, a in enumerate(r.active)
                if a
            )
            + "\nend GND\n"
        )
        files = {
            "Definitions.lean": definitions,
            "ProofObligations.lean": stubs.encode(),
            "source-map.json": canonical_json_bytes(sm),
            "obligations.json": canonical_json_bytes(ob),
            "lean-toolchain": (toolchain + "\n").encode(),
            "inputs/model.json": model_bytes,
            "inputs/candidate.json": candidate_bytes,
        }
        for n, (_, raw) in enumerate(sorted(reference_inputs)):
            files[f"inputs/reference-{n}.json"] = raw
        binding = witness_io.identity(model, candidate, reference_inputs)
        binding.update(
            model_raw_sha256=digest(model_bytes), candidate_raw_sha256=digest(candidate_bytes)
        )
        manifest = {
            "version": 1,
            "kind": "lean-finite-model",
            "support_profile": PROFILE,
            "assurance": "none",
            "toolchain": toolchain,
            "binding": binding,
            "input_formats": {"model": model_format, "candidate": candidate_format},
            "carrier_sha256": cd,
            "files": [
                {"path": k, "bytes": len(v), "sha256": digest(v)} for k, v in sorted(files.items())
            ],
            "limits": vars(limits),
            "proof_status": "unproved",
        }
        files["manifest.json"] = canonical_json_bytes(manifest)
        if sum(map(len, files.values())) > limits.bundle_bytes:
            raise ValueError("bundle ceiling")
        counts.update(carrier_values=sum(map(len, r.values)), emission_visits=r.visits)
        return LeanResult(counts=counts, files=files)
    except WorkLimit:
        return refused(4, "work-limit")
    except Unsupported:
        return refused(2, "fragment-unsupported")
    except INPUT_ERRORS:
        return refused()
