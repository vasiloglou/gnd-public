"""Independent, narrow witness helpers for guarded-exists synthesis.

The checker owns production verdicts.  This module supplies the small
model-derived witness used by synthesis, using population rows and the public
exact-term semantics but never calling the checker.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from dataclasses import dataclass
from typing import Any

from gnd.synth.identity import scalar_identity
from gnd.terms import compare_terms

# This deliberately sits below production's 200,000-unit ceiling. The
# independent nested-loop oracle does not count candidate rows, index probes,
# and merged bindings separately, so half the production budget keeps its
# answer conservative near the production refusal boundary.
_EXISTS_ORACLE_WORK_LIMIT = 100_000


@dataclass(slots=True)
class _WorkBudget:
    limit: int = _EXISTS_ORACLE_WORK_LIMIT
    used: int = 0
    exhausted: bool = False

    def consume(self, amount: int = 1) -> bool:
        self.used += amount
        self.exhausted = self.used > self.limit
        return not self.exhausted


def modular_repair_plan(constraint: Mapping[str, Any]) -> dict[str, Any] | None:
    """Describe the one narrow synthesis shape: two joined atoms and a
    positive-modulus equality between an antecedent PCI and an exists PCI.
    """
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    where = exists.get("where") if isinstance(exists, Mapping) else None
    antecedent = constraint.get("antecedent")
    if not isinstance(atoms, list) or len(atoms) != 2 or not isinstance(where, list) or len(where) != 1:
        return None
    if not isinstance(antecedent, list):
        return None

    def variable_only(atoms_to_check: Sequence[object]) -> bool:
        for atom in atoms_to_check:
            if not isinstance(atom, Mapping) or not isinstance(atom.get("bind"), Mapping):
                return False
            if any(
                not isinstance(value, str) or not value.startswith("$")
                for value in atom["bind"].values()
            ):
                return False
        return True

    # join_atoms binds every string to a variable name. Literal role values
    # therefore need identity-aware matching before this mutation is safe.
    if not variable_only(antecedent) or not variable_only(atoms):
        return None
    comparison = where[0]
    if not isinstance(comparison, Mapping) or comparison.get("operator") != "=":
        return None

    def mod_parts(term: object) -> tuple[str, object] | None:
        if not isinstance(term, Mapping) or term.get("fn") != "mod":
            return None
        args = term.get("args")
        if not isinstance(args, list) or len(args) != 2:
            return None
        variable = args[0]
        if not isinstance(variable, str) or not variable.startswith("$"):
            return None
        return variable[1:], args[1]

    left = mod_parts(comparison.get("left"))
    right = mod_parts(comparison.get("right"))
    if left is None or right is None:
        return None
    pairs = ((left, right), (right, left))
    selected: tuple[tuple[str, object], tuple[str, object]] | None = None
    for fixed, free in pairs:
        if (
            isinstance(fixed[1], int)
            and not isinstance(fixed[1], bool)
            and fixed[1] > 0
            and isinstance(free[1], str)
            and free[1].startswith("$")
        ):
            selected = fixed, (free[0], free[1][1:])
            break
    if selected is None:
        return None
    antecedent_variable, divisor = selected[0][0], selected[0][1]
    candidate_variable, candidate_divisor = selected[1]

    antecedent_variables = {
        variable[1:]
        for atom in antecedent
        if isinstance(atom, Mapping) and isinstance(atom.get("bind"), Mapping)
        for variable in atom["bind"].values()
        if isinstance(variable, str) and variable.startswith("$")
    }
    if antecedent_variable not in antecedent_variables or candidate_variable in antecedent_variables or candidate_divisor in antecedent_variables:
        return None
    if candidate_variable == candidate_divisor:
        return None

    atom_variables: list[set[str]] = []
    for atom in atoms:
        if not isinstance(atom, Mapping) or not isinstance(atom.get("bind"), Mapping):
            return None
        atom_variables.append({
            variable[1:]
            for variable in atom["bind"].values()
            if isinstance(variable, str) and variable.startswith("$")
        })
    shared_exists = (atom_variables[0] & atom_variables[1]) - antecedent_variables
    if len(shared_exists) != 1 or not (atom_variables[0] & antecedent_variables):
        return None
    if candidate_variable not in atom_variables[1] or candidate_divisor not in atom_variables[1]:
        return None
    exists_only = set.union(*atom_variables) - antecedent_variables
    if exists_only != shared_exists | {candidate_variable, candidate_divisor}:
        return None
    return {
        "atoms": atoms,
        "antecedent_variable": antecedent_variable,
        "divisor": divisor,
        "candidate_variable": candidate_variable,
        "candidate_divisor": candidate_divisor,
    }


def has_private_exists_sources(model: Any, constraint: Mapping[str, Any]) -> bool:
    """Whether this exists rule alone reads its witness source relations.

    The narrow witness-removal mutation and its constructive baseline both rely
    on being able to edit these relations without changing an antecedent or a
    second constraint. Unrelated model constraints and unrelated inline rules
    do not narrow support.
    """
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    if not isinstance(atoms, list):
        return False
    source_ids = {
        str(atom.get("fact_type"))
        for atom in atoms
        if isinstance(atom, Mapping) and atom.get("fact_type") is not None
    }
    if not source_ids:
        return False

    def references(value: Any, *, omit_exists: bool = False) -> set[str]:
        found: set[str] = set()
        pending = [value]
        while pending:
            current = pending.pop()
            if isinstance(current, Mapping):
                for key, child in current.items():
                    if omit_exists and key == "exists":
                        continue
                    if key == "fact_type" and isinstance(child, str):
                        found.add(child)
                    pending.append(child)
            elif isinstance(current, (list, tuple)):
                pending.extend(current)
        return found

    if source_ids & references(constraint, omit_exists=True):
        return False
    for other in getattr(model, "constraints", None) or []:
        if other is constraint:
            continue
        if source_ids & references(other):
            return False

    for fact_type in getattr(model, "fact_types", None) or []:
        fact_type_id = str(fact_type.get("id"))
        rule = fact_type.get("derivation_rule")
        if fact_type_id in source_ids:
            if (
                fact_type.get("constraints")
                or fact_type.get("derivation") in {"derived", "semiderived"}
                or rule is not None
            ):
                return False
            continue
        if isinstance(rule, str) or source_ids & references(rule):
            # Opaque derivations cannot prove that they leave these relations
            # untouched; structured rules expose their source IDs for this test.
            return False
    for object_type in getattr(model, "object_types", None) or []:
        rule = object_type.get("derivation_rule")
        if isinstance(rule, str) or source_ids & references(rule):
            return False
    return True


def join_atoms(
    facts: Mapping[str, Sequence[Mapping[str, Any]]],
    atoms: Sequence[Mapping[str, Any]],
    initial: Mapping[str, Any] | None = None,
    *,
    budget: _WorkBudget | None = None,
) -> list[dict[str, Any]] | None:
    """Join atom role bindings by ORM scalar identity, independently of checker IR."""
    budget = budget or _WorkBudget()
    partials = [dict(initial or {})]
    for atom in atoms:
        fact_type = atom.get("fact_type")
        role_bindings = atom.get("bind")
        if not isinstance(fact_type, str) or not isinstance(role_bindings, Mapping):
            return []
        rows = facts.get(fact_type, ())
        next_partials: list[dict[str, Any]] = []
        for partial in partials:
            for row in rows:
                if not budget.consume():
                    return None
                candidate = dict(partial)
                valid = True
                for role, variable in role_bindings.items():
                    if not isinstance(role, str) or not isinstance(variable, str):
                        valid = False
                        break
                    if role not in row:
                        valid = False
                        break
                    name = variable.removeprefix("$")
                    value = row[role]
                    if name in candidate and scalar_identity(candidate[name]) != scalar_identity(value):
                        valid = False
                        break
                    candidate[name] = value
                if valid:
                    next_partials.append(candidate)
        partials = next_partials
        if not partials:
            break
    return partials


def antecedent_bindings(
    constraint: Mapping[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    budget: _WorkBudget | None = None,
) -> list[dict[str, Any]] | None:
    antecedent = constraint.get("antecedent")
    if not isinstance(antecedent, list):
        return []
    return join_atoms(facts, antecedent, budget=budget)


def guarded_atoms_connected(atoms: object) -> bool:
    """Whether the variable-only atom list has one connected join graph."""
    if not isinstance(atoms, list) or not atoms:
        return False
    variable_sets: list[set[str]] = []
    for atom in atoms:
        bindings = atom.get("bind") if isinstance(atom, Mapping) else None
        if not isinstance(bindings, Mapping):
            return False
        variables = {
            value[1:]
            for value in bindings.values()
            if isinstance(value, str) and value.startswith("$") and len(value) > 1
        }
        if not variables:
            return False
        variable_sets.append(variables)

    reached = {0}
    while True:
        expanded = reached | {
            index
            for index, variables in enumerate(variable_sets)
            if any(variables & variable_sets[seen] for seen in reached)
        }
        if expanded == reached:
            break
        reached = expanded
    return len(reached) == len(variable_sets)


def exists_witness_shape_supported(constraint: Mapping[str, Any]) -> bool:
    """Whether the independent exists oracle can interpret this shape."""
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    antecedent = constraint.get("antecedent")
    if not isinstance(atoms, list) or not atoms or not isinstance(antecedent, list):
        return False
    for atom in [*antecedent, *atoms]:
        role_bindings = atom.get("bind") if isinstance(atom, Mapping) else None
        if not isinstance(role_bindings, Mapping) or any(
            not isinstance(value, str) or not value.startswith("$") or len(value) == 1
            for value in role_bindings.values()
        ):
            return False
    return guarded_atoms_connected(antecedent)


def _where_holds(
    where: object,
    binding: Mapping[str, Any],
    *,
    budget: _WorkBudget,
) -> bool | None:
    if where is None:
        return True
    if not isinstance(where, list):
        return None
    holds = True
    unavailable = False
    for comparison in where:
        if not isinstance(comparison, Mapping):
            unavailable = True
            continue
        result = compare_terms(
            str(comparison.get("operator")),
            comparison.get("left"),
            comparison.get("right"),
            binding,
            bound_cross_product=True,
        )
        if not budget.consume(max(1, result.nodes + result.operations)):
            return None
        if not result.available:
            unavailable = True
        if result.value is not True:
            holds = False
    return None if unavailable else holds


def exists_witness(
    constraint: Mapping[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Any]]],
    *,
    covered_fact_types: Collection[str] | None = None,
) -> bool | None:
    """Return whether every antecedent binding has a witness, or ``None`` if
    any reached exact-term candidate is unavailable or a role binding is
    outside this narrow variable-only oracle.
    """
    if not exists_witness_shape_supported(constraint):
        return None
    consequent = constraint.get("consequent")
    exists = consequent.get("exists") if isinstance(consequent, Mapping) else None
    atoms = exists.get("atoms") if isinstance(exists, Mapping) else None
    antecedent = constraint.get("antecedent")
    assert isinstance(antecedent, list) and isinstance(atoms, list)
    budget = _WorkBudget()
    bindings = antecedent_bindings(constraint, facts, budget=budget)
    if bindings is None or budget.exhausted:
        return None
    if not bindings:
        return True
    if covered_fact_types is not None and any(
        isinstance(atom, Mapping)
        and isinstance(atom.get("fact_type"), str)
        and atom["fact_type"] not in covered_fact_types
        for atom in atoms
    ):
        return None

    # Production eagerly scans every existential source relation to build
    # candidate lists before it starts joining them. Charge that aggregate
    # scan up front so an empty early relation cannot make this oracle return
    # a decided answer while production exhausts its work ceiling on a later
    # relation. The join below charges its own nested-loop work as well.
    candidate_rows = 0
    for atom in atoms:
        fact_type = atom.get("fact_type") if isinstance(atom, Mapping) else None
        if not isinstance(fact_type, str):
            return None
        rows = facts.get(fact_type, ())
        try:
            candidate_rows += len(rows)
        except TypeError:
            return None
    if not budget.consume(candidate_rows):
        return None

    all_have_witness = True
    unavailable = False
    for antecedent in bindings:
        candidates = join_atoms(facts, atoms, antecedent, budget=budget)
        if candidates is None or budget.exhausted:
            return None
        found = False
        for candidate in candidates:
            where = _where_holds(exists.get("where"), candidate, budget=budget)
            if budget.exhausted:
                return None
            if where is None:
                unavailable = True
            elif where:
                found = True
        if not found:
            all_have_witness = False
    if unavailable:
        return None
    return all_have_witness
