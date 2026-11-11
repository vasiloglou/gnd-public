"""Bounded construction and independent labels for asserted guarded cases."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from itertools import chain
from random import Random
from typing import Any

from gnd.atoms import atom_bind
from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.synth.guarded import _where_holds, _WorkBudget, guarded_atoms_connected, join_atoms
from gnd.synth.identity import scalar_identity
from gnd.synth.value_domain import constraint_accepts, governing_value_constraints
from gnd.synth.values import make_value, predicate_for
from gnd.terms import variable_name

GUARD_WORK = 100_000
RUN_WORK = 1_000_000
ATTEMPTS = 128
PRIMITIVES = frozenset({"String", "Boolean", "Integer", "Float", "Number", "Binary"})
COMPARISON_PAIRS = (
    (0, 0),
    (-1, 1),
    (1, -1),
    ("a", "a"),
    ("a", "b"),
    ("b", "a"),
    (False, False),
    (False, True),
    (True, False),
)
Facts = dict[str, list[dict[str, Any]]]


class SearchLimit(Exception):
    pass


class UnsupportedShape(Exception):
    pass


@dataclass(frozen=True, slots=True)
class Domain:
    primitive: str
    constraints: list[dict[str, Any]]

    def accepts(self, value: Any, budget: _WorkBudget) -> bool:
        if not predicate_for(self.primitive)(value):
            return False
        for constraint in self.constraints:
            # Enumeration membership builds scalar keys. Account for that work
            # before calling the shared predicate, likewise for unions of ranges.
            charge(budget, 1 + len(constraint.get("allowed") or constraint.get("ranges") or ()))
            if not constraint_accepts(value, constraint):
                return False
        return True

    def draw(self, rng: Random) -> Any:
        if not self.constraints:
            return make_value(self.primitive, rng)
        constraint = rng.choice(self.constraints)
        if "allowed" in constraint:
            return rng.choice(constraint["allowed"])
        ranges = constraint.get("ranges") or [constraint["range"]]
        return make_value(self.primitive, rng, value_range=rng.choice(ranges))


@dataclass(frozen=True, slots=True)
class Candidate:
    facts: Facts
    binding_count: int


def charge(budget: _WorkBudget, count: int = 1) -> None:
    if not budget.consume(count):
        raise SearchLimit


def _domains(model, index, atoms, roles, asserted, budget):
    variables: dict[str, list[Domain]] = defaultdict(list)
    literals_legal = True
    domains: dict[tuple[str, str], Domain] = {}
    for atom in atoms:
        ftid = atom["fact_type"]
        if ftid not in asserted:
            raise UnsupportedShape
        for role, term in atom_bind(atom).items():
            charge(budget)
            key = (ftid, role)
            if key not in domains:
                oid = roles[ftid][role]
                primitive = index.primitive(oid, variant="strict")
                if primitive not in PRIMITIVES:
                    raise UnsupportedShape
                domains[key] = Domain(
                    primitive, governing_value_constraints(model, oid, ftid=ftid, role_name=role)
                )
            domain = domains[key]
            name = variable_name(term)
            if name is None:
                literals_legal = domain.accepts(term, budget) and literals_legal
            else:
                variables[name].append(domain)
    return variables, literals_legal


def _preferred(term: Any) -> list[Any]:
    if type(term) is int:
        return [term, term - 1, term + 1]
    if type(term) is float:
        return [term, math.nextafter(term, -math.inf), math.nextafter(term, math.inf)]
    if type(term) is str:
        return [term, "", term + "a"]
    return [term]


def _assignment(domains, comparison, attempt, rng, budget, *, initial=None):
    assignment = dict(initial or {})
    for name, occurrences in domains.items():
        charge(budget)
        if name in assignment:
            value = assignment[name]
        else:
            side = next(
                (key for key in ("left", "right") if variable_name(comparison.get(key)) == name),
                None,
            )
            other = comparison.get("right" if side == "left" else "left")
            other_name = variable_name(other)
            # Sample equality and both orders deliberately. Independent draws
            # almost never meet on equality in a wide numeric domain.
            preferred = []
            if side and other_name is not None:
                preferred = [pair[int(side == "right")] for pair in COMPARISON_PAIRS]
            elif side and other is not None:
                preferred = _preferred(other)
            if attempt < len(preferred):
                value = preferred[attempt]
            elif other_name in assignment and attempt % 2 == 0:
                value = assignment[other_name]
            else:
                try:
                    value = rng.choice(occurrences).draw(rng)
                except (IndexError, OverflowError, ValueError):
                    return None
        if not all(domain.accepts(value, budget) for domain in occurrences):
            return None
        assignment[name] = value
    return assignment


def _facts(atoms, assignment, budget):
    facts: Facts = {}
    keys: dict[str, set[tuple]] = defaultdict(set)
    for atom in atoms:
        ftid = atom["fact_type"]
        bind = atom_bind(atom)
        charge(budget, 1 + len(bind))
        row = {role: assignment.get(variable_name(term), term) for role, term in bind.items()}
        key = tuple((role, scalar_identity(row[role])) for role in sorted(row))
        if key not in keys[ftid]:
            keys[ftid].add(key)
            facts.setdefault(ftid, []).append(row)
    return facts


def _join(facts, atoms, budget, binding=None):
    rows = join_atoms(facts, atoms, binding, budget=budget, scalar_terms=True)
    if rows is None:
        raise SearchLimit
    return rows


def _outcome(facts, antecedent, kind, payload, witnesses, budget):
    bindings = _join(facts, antecedent, budget)
    if not bindings:
        return None
    distinct = {}
    for binding in bindings:
        charge(budget, 1 + len(binding))
        key = tuple(sorted((name, scalar_identity(value)) for name, value in binding.items()))
        distinct.setdefault(key, binding)
    satisfied = True
    for binding in distinct.values():
        charge(budget)
        if kind == "comparison":
            holds = _where_holds([payload], binding, budget=budget)
            if budget.exhausted:
                raise SearchLimit
            if holds is None:
                return None
        else:
            holds = bool(_join(facts, witnesses, budget, binding))
            if kind == "absence":
                holds = not holds
        satisfied = satisfied and holds
    return satisfied, Candidate(facts, len(distinct))


def confirmation_work(pair, guards, budget):
    """Charge an upper bound on the checker's guarded joins."""
    for case in pair:
        for _, guard, _ in guards:
            prefixes = 1
            consequent = guard.get("consequent") or {}
            exists = consequent.get("exists") or {}
            head = consequent.get("atom") or consequent.get("absence")
            witnesses = (head,) if head is not None else exists.get("atoms") or ()
            for atom in chain(guard.get("antecedent") or (), witnesses):
                rows = len(case.facts.get(atom["fact_type"], ()))
                charge(budget, 1 + rows * len(atom_bind(atom)))
                prefixes *= rows
                charge(budget, prefixes)


def build_pair(model: Model, index: ModelIndex, rule: dict, rng: Random, budget: _WorkBudget):
    """Return an independently evaluated failure and active pass, or a reason."""
    antecedent = rule["antecedent"]
    kind, payload = next(iter(rule["consequent"].items()))
    witnesses = []
    if kind in {"atom", "absence"}:
        witnesses = [payload]
    elif kind == "exists" and not payload.get("where"):
        witnesses = payload["atoms"]
    elif kind != "comparison":
        return None, "unsupported-shape"
    if kind == "comparison" and any(isinstance(payload[side], dict) for side in ("left", "right")):
        return None, "unsupported-shape"

    roles = index.role_object_types()
    asserted = {
        ft["id"]
        for ft in index.iter_fact_types_shared()
        if not ft.get("derivation_rule") and (ft.get("derivation") or "asserted") == "asserted"
    }
    try:
        if len(antecedent) > 1:
            charge(budget, len(antecedent) ** 3 + sum(len(atom_bind(atom)) for atom in antecedent))
            if not guarded_atoms_connected(antecedent):
                return None, "unsupported-shape"
        domains, reachable = _domains(model, index, antecedent, roles, asserted, budget)
        if not reachable:
            return None, "antecedent-unreachable"
        extension, possible = _domains(model, index, witnesses, roles, asserted, budget)
        if not possible:
            return None, "no-failing-case" if kind == "absence" else "no-passing-case"
        if witnesses and all(atom in antecedent for atom in witnesses):
            return None, "no-passing-case" if kind == "absence" else "no-failing-case"

        comparison = payload if kind == "comparison" else {}
        seen = {}
        for attempt in range(ATTEMPTS):
            assignment = _assignment(domains, comparison, attempt, rng, budget)
            if assignment is None:
                continue
            base = _facts(antecedent, assignment, budget)
            first = _outcome(base, antecedent, kind, payload, witnesses, budget)
            if first is None:
                continue
            truth, case = first
            if kind == "comparison":
                seen.setdefault(truth, case)
            else:
                # A single antecedent assignment supplies both cases. Check both
                # resulting extensions because witness rows may add new subjects.
                seen = {truth: case}
                expanded = _assignment(extension, {}, attempt, rng, budget, initial=assignment)
                if expanded is not None:
                    second = _outcome(
                        _facts([*antecedent, *witnesses], expanded, budget),
                        antecedent,
                        kind,
                        payload,
                        witnesses,
                        budget,
                    )
                    if second is not None:
                        seen.setdefault(*second)
            if len(seen) == 2:
                return (seen[False], seen[True]), None
    except SearchLimit:
        return None, "search-limit"
    except UnsupportedShape:
        return None, "unsupported-shape"
    return None, "search-limit"
