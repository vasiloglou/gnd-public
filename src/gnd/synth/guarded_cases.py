"""Bounded construction and independent labels for asserted guarded cases."""

from __future__ import annotations

import math
from collections import defaultdict
from dataclasses import dataclass
from random import Random
from typing import Any

from gnd.atoms import atom_bind
from gnd.documents import Model
from gnd.model_index import ModelIndex
from gnd.synth.guarded import _where_holds, _WorkBudget, guarded_atoms_connected, join_atoms
from gnd.synth.identity import scalar_identity
from gnd.synth.value_domain import constraint_accepts, governing_value_constraints
from gnd.synth.values import make_value, predicate_for
from gnd.terms import MEMBERSHIP_OPERATORS, prepare_comparisons, variable_name

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
            elif side == "left" and comparison.get("operator") in MEMBERSHIP_OPERATORS:
                members = (other or [])[:ATTEMPTS]
                if any(domain.primitive == "Integer" for domain in occurrences):
                    members = [
                        int(member) if type(member) is float and member.is_integer() else member
                        for member in members
                    ]
                if members:
                    preferred = [*_preferred(members[0]), *members[1:]]
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


def _outcome(facts, antecedent, kind, where, witnesses, budget, *, negate=(), filters=None):
    bindings = _join(facts, antecedent, budget)
    if not bindings:
        return None
    distinct = {}
    for binding in bindings:
        charge(budget, 1 + len(binding))
        if any(_join(facts, [atom], budget, binding) for atom in negate):
            continue
        if filters:
            survives = _where_holds(filters, binding, budget=budget)
            if budget.exhausted:
                raise SearchLimit
            if survives is None:
                return None
            if not survives:
                continue
        key = tuple(sorted((name, scalar_identity(value)) for name, value in binding.items()))
        distinct.setdefault(key, binding)
    if not distinct:
        return None
    satisfied = True
    for binding in distinct.values():
        charge(budget)
        if kind == "any_of":
            states = [_binding_holds(facts, binding, *alternate, budget) for alternate in witnesses]
            holds = True if True in states else None if None in states else False
        else:
            holds = _binding_holds(facts, binding, kind, where, witnesses, budget)
        if budget.exhausted:
            raise SearchLimit
        if holds is None:
            return None
        satisfied = satisfied and holds
    return satisfied, Candidate(facts, len(distinct))


def _binding_holds(facts, binding, kind, where, witnesses, budget):
    if kind == "comparison":
        return _where_holds(where, binding, budget=budget)
    joined = _join(facts, witnesses, budget, binding)
    if kind == "exists" and where:
        outcomes = [_where_holds(where, row, budget=budget) for row in joined]
        return None if None in outcomes else any(outcomes)
    return not joined if kind == "absence" else bool(joined)


def _disjunction_pair(model, index, rule, rng, budget):
    antecedent = rule["antecedent"]
    negate = rule.get("negate") or ()
    raw_filters = rule.get("where") or ()
    roles, asserted = _role_domains(index)
    charge(budget, len(antecedent) ** 3 + sum(len(atom_bind(atom)) for atom in antecedent))
    if len(antecedent) > 1 and not guarded_atoms_connected(antecedent):
        return None, "unsupported-shape"
    domains, reachable = _domains(model, index, antecedent, roles, asserted, budget)
    if not reachable:
        return None, "antecedent-unreachable"
    if negate:
        _domains(model, index, negate, roles, asserted, budget)
    filters = _prepared_guard_filters(raw_filters, budget)
    alternatives = []
    shapes = []
    for alternative in rule["consequent"]["any_of"]:
        charge(budget)
        kind, payload = next(iter(alternative.items()))
        atoms, comparisons = _alternative_parts(kind, payload)
        extension, possible = _domains(model, index, atoms, roles, asserted, budget)
        alternatives.append((kind, _prepared_guard_filters(comparisons, budget), atoms))
        shapes.append((kind, comparisons[0] if comparisons else {}, atoms, extension, possible))

    def evaluate(facts):
        return _outcome(
            facts, antecedent, "any_of", (), alternatives, budget, negate=negate, filters=filters,
        )

    seen = {}
    preferred = [row for row in raw_filters if row.get("operator") in MEMBERSHIP_OPERATORS]
    preferred += [comparison for _, comparison, _, _, _ in shapes if comparison]
    for attempt in range(ATTEMPTS):
        for comparison in preferred or [{}]:
            charge(budget)
            assignment = _assignment(domains, comparison, attempt, rng, budget)
            if assignment is None:
                continue
            base = _facts(antecedent, assignment, budget)
            scenarios = [base]
            forbidden = []
            for kind, witness_comparison, atoms, extension, possible in shapes:
                if not atoms or not possible:
                    continue
                extended = _assignment(
                    extension, witness_comparison, attempt, rng, budget, initial=assignment,
                )
                if extended is not None:
                    evidence = _facts(atoms, extended, budget)
                    scenarios.append(_merge_facts((base, evidence), budget))
                    if kind == "absence":
                        forbidden.append(evidence)
            if len(forbidden) > 1:
                scenarios.append(_merge_facts((base, *forbidden), budget))
            for facts in scenarios:
                result = evaluate(facts)
                if result is not None:
                    seen.setdefault(*result)
                if len(seen) == 2:
                    passing = _pass_with_excluded_binding(
                        seen[True], seen[False], antecedent=antecedent, negate=negate,
                        budget=budget, evaluate=evaluate,
                    )
                    return (seen[False], passing), None
    return None, "search-limit"


def _alternative_parts(kind, payload):
    if kind in {"atom", "absence"}:
        return (payload,), ()
    if kind == "exists":
        return payload["atoms"], payload.get("where") or ()
    return (), (payload,)


def _prepared_guard_filters(comparisons, budget):
    for comparison in comparisons:
        if comparison.get("operator") in MEMBERSHIP_OPERATORS:
            charge(budget, len(comparison["right"]))
    return list(prepare_comparisons(comparisons))


def _role_domains(index):
    roles = index.role_object_types()
    asserted = {
        ft["id"]
        for ft in index.iter_fact_types_shared()
        if not ft.get("derivation_rule") and (ft.get("derivation") or "asserted") == "asserted"
    }
    return roles, asserted


def _merge_facts(sources, budget):
    merged = {}
    for facts in sources:
        for name, rows in facts.items():
            indexed = merged.setdefault(name, {})
            for row in rows:
                charge(budget, 1 + len(row))
                key = tuple((role, scalar_identity(value)) for role, value in sorted(row.items()))
                indexed.setdefault(key, row)
    return {name: list(rows.values()) for name, rows in merged.items()}


def _pass_with_excluded_binding(passing, failing, *, antecedent, negate, budget, evaluate):
    if not negate:
        return passing
    additions = [
        _facts(negate, binding, budget)
        for binding in _join(failing.facts, antecedent, budget)
    ]
    candidate = _merge_facts((passing.facts, failing.facts, *additions), budget)
    outcome = evaluate(candidate)
    if outcome is not None and outcome[0]:
        return outcome[1]
    return passing


def confirmation_work(pair, guards, budget):
    """Charge an upper bound on the checker's guarded joins."""
    for case in pair:
        for _, guard, _ in guards:
            prefixes = 1
            consequent = guard.get("consequent") or {}
            alternatives = consequent.get("any_of")
            if alternatives is None:
                exists = consequent.get("exists") or {}
                head = consequent.get("atom") or consequent.get("absence")
                legacy_atoms = (head,) if head is not None else exists.get("atoms") or ()
            for atom in guard.get("antecedent") or ():
                rows = len(case.facts.get(atom["fact_type"], ()))
                charge(budget, 1 + rows * len(atom_bind(atom)))
                prefixes *= rows
                charge(budget, prefixes)
            for atom in guard.get("negate") or ():
                rows = len(case.facts.get(atom["fact_type"], ()))
                charge(budget, (1 + len(atom_bind(atom))) * (1 + rows + prefixes))
            if guard.get("where"):
                charge(budget, prefixes * len(guard["where"]))
            if alternatives is None:
                for atom in legacy_atoms:
                    rows = len(case.facts.get(atom["fact_type"], ()))
                    charge(budget, 1 + rows * len(atom_bind(atom)))
                    prefixes *= rows
                    charge(budget, prefixes)
                continue
            for alternative in alternatives:
                kind, value = next(iter(alternative.items()))
                witnesses, comparisons = _alternative_parts(kind, value)
                charge(budget, prefixes)
                alternative_prefixes = prefixes
                for atom in witnesses:
                    rows = len(case.facts.get(atom["fact_type"], ()))
                    charge(budget, 1 + rows * len(atom_bind(atom)))
                    alternative_prefixes *= rows
                    charge(budget, alternative_prefixes)
                if comparisons:
                    charge(budget, alternative_prefixes * len(comparisons))


def build_pair(model: Model, index: ModelIndex, rule: dict, rng: Random, budget: _WorkBudget):
    """Return an independently evaluated failure and active pass, or a reason."""
    antecedent = rule["antecedent"]
    kind, payload = next(iter(rule["consequent"].items()))
    if kind == "any_of":
        try:
            return _disjunction_pair(model, index, rule, rng, budget)
        except SearchLimit:
            return None, "search-limit"
        except UnsupportedShape:
            return None, "unsupported-shape"
    negate = rule.get("negate") or ()
    raw_filters = rule.get("where") or ()
    witnesses = []
    if kind in {"atom", "absence"}:
        witnesses = [payload]
    elif kind == "exists" and (
        not payload.get("where")
        or any(comparison.get("operator") in MEMBERSHIP_OPERATORS for comparison in payload["where"])
    ):
        witnesses = payload["atoms"]
    elif kind != "comparison":
        return None, "unsupported-shape"
    if kind == "comparison" and any(isinstance(payload[side], dict) for side in ("left", "right")):
        return None, "unsupported-shape"

    roles, asserted = _role_domains(index)
    try:
        if len(antecedent) > 1:
            charge(budget, len(antecedent) ** 3 + sum(len(atom_bind(atom)) for atom in antecedent))
            if not guarded_atoms_connected(antecedent):
                return None, "unsupported-shape"
        domains, reachable = _domains(model, index, antecedent, roles, asserted, budget)
        if not reachable:
            return None, "antecedent-unreachable"
        if negate:
            _domains(model, index, negate, roles, asserted, budget)
        filters = _prepared_guard_filters(raw_filters, budget)
        extension, possible = _domains(model, index, witnesses, roles, asserted, budget)
        if not possible:
            return None, "no-failing-case" if kind == "absence" else "no-passing-case"
        raw_where = []
        if kind == "comparison":
            raw_where = [payload]
        elif kind == "exists":
            raw_where = payload.get("where") or []
        where = _prepared_guard_filters(raw_where, budget)
        if witnesses and not raw_where and all(atom in antecedent for atom in witnesses):
            return None, "no-passing-case" if kind == "absence" else "no-failing-case"

        comparison = raw_where[0] if raw_where else {}
        preferred_filter = next(
            (row for row in raw_filters if row.get("operator") in MEMBERSHIP_OPERATORS),
            comparison,
        )
        left = variable_name(comparison.get("left"))
        if kind == "comparison" and comparison.get("operator") in MEMBERSHIP_OPERATORS:
            domains_for_left = domains.get(left, ())
            if domains_for_left and all(domain.primitive == "Boolean" for domain in domains_for_left):
                outcomes = {
                    _where_holds(where, {left: value}, budget=budget)
                    for value in (False, True)
                    if all(domain.accepts(value, budget) for domain in domains_for_left)
                }
                if budget.exhausted:
                    raise SearchLimit
                if outcomes == {True}:
                    return None, "no-failing-case"
                if outcomes == {False}:
                    return None, "no-passing-case"
        def evaluate(facts):
            return _outcome(facts, antecedent, kind, where, witnesses, budget, negate=negate, filters=filters)

        seen = {}
        for attempt in range(ATTEMPTS):
            assignment = _assignment(domains, preferred_filter, attempt, rng, budget)
            if assignment is None:
                continue
            base = _facts(antecedent, assignment, budget)
            first = evaluate(base)
            if first is None:
                continue
            truth, case = first
            if kind == "comparison":
                seen.setdefault(truth, case)
            else:
                # A single antecedent assignment supplies both cases. Check both
                # resulting extensions because witness rows may add new subjects.
                seen = {truth: case}
                expanded = _assignment(extension, comparison, attempt, rng, budget, initial=assignment)
                if expanded is not None:
                    second = evaluate(_facts([*antecedent, *witnesses], expanded, budget))
                    if second is not None:
                        seen.setdefault(*second)
            if len(seen) == 2:
                passing = _pass_with_excluded_binding(
                    seen[True], seen[False], antecedent=antecedent, negate=negate, budget=budget, evaluate=evaluate
                )
                return (seen[False], passing), None
    except SearchLimit:
        return None, "search-limit"
    except UnsupportedShape:
        return None, "unsupported-shape"
    return None, "search-limit"
