"""An independent, naive why-not oracle over plain JSON documents (tests only).

It deliberately imports nothing from GND: identity, clause presentation,
derivation fixpoint and the declared-order walk are all re-derived here from
the model's documented semantics, so an agreement with the kernel is not the
kernel agreeing with itself. Comparisons use literal operators over variables
and constants only; function terms are covered against production elsewhere.
"""

from __future__ import annotations

import json
from fractions import Fraction

OPERATORS = {
    "=": lambda a, b: a == b,
    "!=": lambda a, b: a != b,
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    ">": lambda a, b: a > b,
    ">=": lambda a, b: a >= b,
}


def identity(value):
    if isinstance(value, bool):
        return ("b", value)
    if isinstance(value, (int, float)):
        return ("n", Fraction(value))
    return ("s", value)


def is_variable(term):
    return isinstance(term, str) and term.startswith("$")


def clauses(rule):
    if "clauses" not in rule:
        return [rule]
    shared = {key: value for key, value in rule.items() if key != "clauses"}
    result = []
    for clause in rule["clauses"]:
        effective = {**shared, **clause}
        if isinstance(shared.get("where"), list) and isinstance(clause.get("where"), list):
            effective["where"] = [*shared["where"], *clause["where"]]
        result.append(effective)
    return result


def _role_names(document, fact_id):
    for ft in document["fact_types"]:
        if ft["id"] == fact_id:
            return [role["role_name"] for role in ft["roles"]]
    raise KeyError(fact_id)


def _definition(document, fact_id):
    return next(ft for ft in document["fact_types"] if ft["id"] == fact_id)


def _structured(ft):
    return ft.get("derivation") in ("derived", "semiderived") and isinstance(ft.get("derivation_rule"), dict)


def _value(term, binding):
    return binding[term[1:]] if is_variable(term) else term


def _match(atom, fact, binding):
    out = dict(binding)
    for role, term in atom["bind"].items():
        value = fact[role]
        if is_variable(term):
            name = term[1:]
            if name in out and identity(out[name]) != identity(value):
                return None
            out.setdefault(name, value)
        elif identity(term) != identity(value):
            return None
    return out


def _key(binding):
    return tuple(sorted((name, identity(value)) for name, value in binding.items()))


def _distinct(bindings):
    seen = {}
    for binding in bindings:
        seen.setdefault(_key(binding), binding)
    return list(seen.values())


def _join(bindings, atom, rows):
    return _distinct(
        merged for binding in bindings for fact in rows
        if (merged := _match(atom, fact, binding)) is not None
    )


def _ground_key(atom, binding):
    return tuple(identity(_value(term, binding)) for term in atom["bind"].values())


class Oracle:
    def __init__(self, document, facts):
        self.document = document
        self.relations = {}
        for ft in document["fact_types"]:
            asserted = [dict(row) for row in facts.get(ft["id"], ())]
            self.relations[ft["id"]] = [] if _structured(ft) else asserted
        self.asserted = {key: [dict(row) for row in rows] for key, rows in facts.items()}
        self._fixpoint()

    def _clause_bindings(self, clause):
        bindings = [{}]
        for atom in clause.get("body") or ():
            bindings = _join(bindings, atom, self.relations[atom["fact_type"]])
        for atom in clause.get("negate") or ():
            present = {
                tuple(identity(fact[role]) for role in atom["bind"])
                for fact in self.relations[atom["fact_type"]]
            }
            bindings = [b for b in bindings if _ground_key(atom, b) not in present]
        for comparison in clause.get("where") or ():
            op = OPERATORS[comparison["operator"]]
            bindings = [
                b for b in bindings
                if op(_value(comparison["left"], b), _value(comparison["right"], b))
            ]
        return bindings

    def _fixpoint(self):
        derived = [ft for ft in self.document["fact_types"] if _structured(ft)]
        changed = True
        self.rounds = 0
        while changed:
            changed = False
            self.rounds += 1
            for ft in derived:
                roles = [role["role_name"] for role in ft["roles"]]
                known = {tuple(identity(row[r]) for r in roles) for row in self.relations[ft["id"]]}
                for clause in clauses(ft["derivation_rule"]):
                    for binding in self._clause_bindings(clause):
                        row = {role: _value(clause["head"][role], binding) for role in roles}
                        key = tuple(identity(row[r]) for r in roles)
                        if key not in known:
                            known.add(key)
                            self.relations[ft["id"]].append(row)
                            changed = True

    def derived(self, fact_id, row=None):
        roles = _role_names(self.document, fact_id)
        rows = self.relations[fact_id]
        if row is None:
            return bool(rows)
        claimed = tuple(identity(cell["value"]) for cell in row)
        return any(tuple(identity(r[role]) for role in roles) == claimed for r in rows)

    def walk(self, fact_id, row=None):
        """Return the clause records: steps and the blocker, for a target not derived."""
        ft = _definition(self.document, fact_id)
        roles = [role["role_name"] for role in ft["roles"]]
        out = []
        for index, clause in enumerate(clauses(ft["derivation_rule"])):
            out.append(self._walk_clause(fact_id, index, clause, roles, row))
        return out

    def _walk_clause(self, fact_id, clause_index, clause, roles, row):
        steps = []
        bindings = [{}]
        if row is not None:
            seed = {}
            for role, cell in zip(roles, row):
                term = clause["head"][role]
                if is_variable(term):
                    name = term[1:]
                    if name in seed and identity(seed[name]) != identity(cell["value"]):
                        step = {"kind": "head-bind:variable", "index": 0, "count": 0}
                        return {"clause_index": clause_index, "steps": [step], "blocker": step}
                    seed[name] = cell["value"]
                elif not isinstance(term, (dict, list)) and identity(term) != identity(cell["value"]):
                    step = {"kind": "head-bind:constant", "index": 0, "count": 0}
                    return {"clause_index": clause_index, "steps": [step], "blocker": step}
            bindings = [seed]
        for index, atom in enumerate(clause.get("body") or ()):
            previous = bindings
            bindings = _join(previous, atom, self.relations[atom["fact_type"]])
            steps.append({"kind": "atom", "index": index, "fact_type": atom["fact_type"], "count": len(bindings)})
            if not bindings:
                return {
                    "clause_index": clause_index, "steps": steps,
                    "blocker": self._atom_blocker(index, atom, previous),
                }
        for index, atom in enumerate(clause.get("negate") or ()):
            present = {
                tuple(identity(fact[role]) for role in atom["bind"])
                for fact in self.relations[atom["fact_type"]]
            }
            bindings = [b for b in bindings if _ground_key(atom, b) not in present]
            steps.append({"kind": "negated", "index": index, "fact_type": atom["fact_type"], "count": len(bindings)})
            if not bindings:
                return {"clause_index": clause_index, "steps": steps, "blocker": dict(steps[-1])}
        for index, comparison in enumerate(clause.get("where") or ()):
            op = OPERATORS[comparison["operator"]]
            bindings = [
                b for b in bindings
                if op(_value(comparison["left"], b), _value(comparison["right"], b))
            ]
            steps.append({"kind": "comparison", "index": index, "count": len(bindings)})
            if not bindings:
                return {"clause_index": clause_index, "steps": steps, "blocker": dict(steps[-1])}
        return {"clause_index": clause_index, "steps": steps, "blocker": None}

    def _atom_blocker(self, index, atom, previous):
        bound = set(previous[0]) if previous else set()
        roles = {}
        for role, term in atom["bind"].items():
            if is_variable(term):
                roles[role] = {"variable": term, "bound": term[1:] in bound}
            else:
                roles[role] = {"constant": term}
        ft = _definition(self.document, atom["fact_type"])
        samples = {}
        for binding in previous:
            sample = {
                role: binding[spec["variable"][1:]]
                for role, spec in roles.items() if spec.get("bound")
            }
            samples.setdefault(tuple(sorted((k, identity(v)) for k, v in sample.items())), sample)
        return {
            "kind": "atom", "index": index, "fact_type": atom["fact_type"],
            "derivation": ft["derivation"] if _structured(ft) else "base",
            "ground": all("constant" in spec or spec["bound"] for spec in roles.values()),
            "roles": roles,
            "sample_count": len(previous),
            "samples": sorted(samples.values(), key=canonical)[:5],
        }


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
