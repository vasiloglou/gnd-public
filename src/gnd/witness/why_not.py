"""Explain why a derivation did not derive a row, beside the finite witness lane.

The production exact evaluation decides whether the target is derived,
unavailable or not derived; this module only walks a clause the evaluator
reported as not derived. The normative definition of a step and of the blocking
step is docs/reference/why-not.md.
"""

from __future__ import annotations

from dataclasses import dataclass, fields
from typing import Any

from gnd import checker
from gnd.artifacts import canonical_json_bytes
from gnd.model import iter_derivation_clauses
from gnd.model_index import ModelIndex
from gnd.references import bind_population
from gnd.witness.io import roster, validate_targets
from gnd.witness.types import WitnessInputError

MAX_DESCENT = 8


class WhyNotInputError(ValueError):
    """The request cannot be explained as given; nothing was evaluated."""


class WhyNotWorkError(ValueError):
    """A fixed ceiling was reached; ``work`` holds the counters at the breach."""

    def __init__(self, message: str, work: dict[str, int]) -> None:
        super().__init__(message)
        self.work = dict(work)


class WhyNotInternalError(RuntimeError):
    """The walk disagreed with the production evaluator; this is a defect."""


@dataclass(frozen=True)
class WhyNotLimits:
    bytes: int = 10 * 1024 * 1024
    container_depth: int = 64
    scalar_bytes: int = 4096
    numeric_digits: int = 128
    pre_joins: int = 200000
    joins: int = 100000
    probes: int = 200000
    binding_cells: int = 400000
    proof_depth: int = 128


DEFAULT_WHY_NOT_LIMITS = WhyNotLimits()


def checked_why_not_limits(limits: WhyNotLimits) -> WhyNotLimits:
    if not isinstance(limits, WhyNotLimits) or any(
        type(getattr(limits, f.name)) is not int
        or getattr(limits, f.name) < 1
        or getattr(limits, f.name) > getattr(DEFAULT_WHY_NOT_LIMITS, f.name)
        for f in fields(WhyNotLimits)
    ):
        raise WhyNotInputError("limits cannot raise the fixed ceilings")
    return limits


@dataclass(frozen=True)
class ClauseExplanation:
    clause_index: int
    steps: tuple[dict, ...]
    blocker: dict
    steps_after_blocker: str | None
    descent: WhyNotResult | None
    descent_stopped: str | None

    def to_dict(self) -> dict:
        return {
            "clause_index": self.clause_index,
            "steps": [dict(step) for step in self.steps],
            "blocker": dict(self.blocker),
            "steps_after_blocker": self.steps_after_blocker,
            "descent": self.descent.to_dict() if self.descent is not None else None,
            "descent_stopped": self.descent_stopped,
        }


@dataclass(frozen=True)
class WhyNotResult:
    fact_type: str
    mode: str
    order: str
    status: str
    reason: str | None
    unavailable: dict | None
    clauses: tuple[ClauseExplanation, ...]
    work: dict

    def to_dict(self) -> dict:
        return {
            "fact_type": self.fact_type,
            "mode": self.mode,
            "order": self.order,
            "status": self.status,
            "reason": self.reason,
            "unavailable": dict(self.unavailable) if self.unavailable is not None else None,
            "clauses": [clause.to_dict() for clause in self.clauses],
            "work": dict(self.work),
        }


class _Budget:
    def __init__(self, limits: WhyNotLimits) -> None:
        self.limits = limits
        self.work = {"pre_joins": 0, "joins": 0, "probes": 0, "binding_cells": 0}

    def charge(self, counter: str, amount: int = 1) -> None:
        self.work[counter] += amount
        if self.work[counter] > getattr(self.limits, counter):
            raise WhyNotWorkError(f"{counter} ceiling", self.work)


class _ChargeOnlyTrace:
    """Witness-trace stand-in: production charges reach the budget; no row is kept."""

    def __init__(self, budget: _Budget) -> None:
        self.budget = budget

    def charge(self, amount: int = 1) -> None:
        self.budget.charge("pre_joins", amount)

    def row(self, *_args: Any) -> None:
        return None


def _is_opaque(value: Any) -> bool:
    return isinstance(value, dict) and set(value) == {"$opaque"}


def _closure(index: ModelIndex, fact_type_id: str) -> set[str]:
    dependencies = checker.derivation_dependencies(
        {"fact_types": list(index.iter_fact_types_shared())}
    )
    closure, pending = set(), [fact_type_id]
    while pending:
        current = pending.pop()
        if current in closure:
            continue
        closure.add(current)
        pending.extend(sorted(dependencies.get(current, ())))
    return closure


def _identity_row(values) -> tuple[bytes, ...]:
    return tuple(checker._identity_token(value) for value in values)


def _binding_key(binding: dict) -> tuple:
    return tuple(sorted((name, checker._identity_key(value)) for name, value in binding.items()))


def _term_variables(term: Any) -> set[str]:
    variable = checker._derivation_variable(term)
    if variable is not None:
        return {variable}
    if isinstance(term, dict):
        return set().union(*(_term_variables(value) for value in term.values()))
    if isinstance(term, list):
        return set().union(*(_term_variables(value) for value in term))
    return set()


def _canonical(value: Any) -> bytes:
    return canonical_json_bytes(value)


def _status(fact_type_id, mode, status, reason=None, unavailable=None, clauses=(), work=None):
    return WhyNotResult(
        fact_type_id, mode, "declared", status, reason, unavailable, tuple(clauses), dict(work or {})
    )


def explain(
    model,
    candidate,
    fact_type_id: str,
    *,
    row: list[dict] | None = None,
    references=None,
    limits: WhyNotLimits = DEFAULT_WHY_NOT_LIMITS,
) -> WhyNotResult:
    """Explain why ``fact_type_id`` (or one claimed row of it) is not derived."""
    checked_why_not_limits(limits)
    index = ModelIndex.for_model(model)
    target = index.fact_type(fact_type_id) if isinstance(fact_type_id, str) else None
    if target is None:
        raise WhyNotInputError("unknown fact type")
    if target.get("derivation") not in ("derived", "semiderived") or not isinstance(
        target.get("derivation_rule"), (dict, str)
    ):
        raise WhyNotInputError("fact type is not derived")
    mode = "rule" if row is None else "row"
    if row is not None:
        try:
            validate_targets([{"fact_type": fact_type_id, "tuple": row}], model)
            _identity_row(cell["value"] for cell in row)
        except (WitnessInputError, ValueError, TypeError, KeyError, AttributeError) as error:
            raise WhyNotInputError("malformed row") from error
    budget = _Budget(limits)
    rule = target.get("derivation_rule")
    if isinstance(rule, str):
        return _status(fact_type_id, mode, "unsupported", "rule-opaque", work=budget.work)
    if any(isinstance(clause.get("aggregate"), dict) for clause in iter_derivation_clauses(rule)):
        return _status(fact_type_id, mode, "unsupported", "aggregate", work=budget.work)
    closure = _closure(index, fact_type_id)
    combined = (
        bind_population(model, candidate, references=references).combined
        if references is not None
        else candidate
    )
    if any(
        _is_opaque(value)
        for fact_id in closure
        for fact in combined.facts.get(fact_id, ())
        for value in fact.values()
    ):
        return _status(fact_type_id, mode, "unsupported", "opaque-value", work=budget.work)
    # Opaque rows outside the closure cannot reach the target; strip them so
    # the evaluator takes the exact path, as check's dispatch does.
    safe = {
        fact_id: [fact for fact in facts if not any(_is_opaque(v) for v in fact.values())]
        for fact_id, facts in combined.facts.items()
    }
    population = combined.model_copy(update={"facts": safe})
    relations = checker._base_relations(model, population)
    token = checker._WITNESS_TRACE.set(_ChargeOnlyTrace(budget))
    try:
        result = checker._evaluate_stratified_extensions(
            model, relations, heads=closure, exact=True
        )
    finally:
        checker._WITNESS_TRACE.reset(token)
    walk = _Walk(model, index, population, relations, result.extensions, budget)
    return walk.explain(fact_type_id, row, depth=0, path=())


class _Walk:
    def __init__(self, model, index, population, relations, extensions, budget) -> None:
        self.model = model
        self.index = index
        self.population = population
        self.extensions = extensions
        self.unavailable = extensions.unavailable
        self.budget = budget
        self.roles = roster(model)
        view = dict(relations)
        view.update(extensions)
        self.facts = checker._relation_facts(view)

    def explain(self, fact_type_id, row, *, depth, path) -> WhyNotResult:
        mode = "rule" if row is None else "row"
        if fact_type_id in self.unavailable:
            origin = self.unavailable[fact_type_id]
            return _status(
                fact_type_id, mode, "unavailable", origin.reason,
                {
                    "reason": origin.reason,
                    "source_relation": origin.source_relation,
                    "binding": dict(origin.binding),
                },
                work=self.budget.work,
            )
        extension = self.extensions.get(fact_type_id)
        rows = extension.rows if extension is not None else ()
        if row is None:
            if rows:
                return _status(fact_type_id, mode, "derived", work=self.budget.work)
        else:
            claimed = _identity_row(cell["value"] for cell in row)
            if any(_identity_row(values) == claimed for values in rows):
                return _status(fact_type_id, mode, "derived", work=self.budget.work)
        rule = self.index.fact_type(fact_type_id)["derivation_rule"]
        clauses = [
            self._clause(fact_type_id, clause_index, clause, row, depth=depth, path=path)
            for clause_index, clause in enumerate(iter_derivation_clauses(rule))
        ]
        return _status(fact_type_id, mode, "blocked", clauses=clauses, work=self.budget.work)

    def _store(self, bindings: dict, binding: dict) -> None:
        key = _binding_key(binding)
        if key not in bindings:
            self.budget.charge("joins")
            self.budget.charge("binding_cells", max(1, len(binding)))
            bindings[key] = binding

    def _seed(self, fact_type_id, clause, row):
        if row is None:
            return [{}], None
        seed: dict[str, Any] = {}
        for (role, _primitive), cell in zip(self.roles[fact_type_id], row, strict=True):
            term = clause["head"][role]
            variable = checker._derivation_variable(term)
            if variable is not None:
                if variable in seed and checker._identity_key(seed[variable]) != checker._identity_key(cell["value"]):
                    return [], "head-bind:variable"
                seed[variable] = cell["value"]
            elif not isinstance(term, (dict, list)):
                if checker._identity_key(term) != checker._identity_key(cell["value"]):
                    return [], "head-bind:constant"
        return [seed], None

    def _clause(self, fact_type_id, clause_index, clause, row, *, depth, path):
        bindings, failed = self._seed(fact_type_id, clause, row)
        steps: list[dict] = []
        if failed is not None:
            step = {"kind": failed, "index": 0, "count": 0}
            return self._blocked(clause_index, [step], step, [{}], None, depth, path)
        for index, atom in enumerate(clause.get("body") or ()):
            previous = bindings
            bindings = self._join(previous, atom)
            step = {
                "kind": "atom", "index": index,
                "fact_type": str(atom.get("fact_type")), "count": len(bindings),
            }
            steps.append(step)
            if not bindings:
                return self._blocked(clause_index, steps, step, previous, atom, depth, path)
        for index, atom in enumerate(clause.get("negate") or ()):
            previous = bindings
            bindings = self._negate(previous, atom)
            step = {
                "kind": "negated", "index": index,
                "fact_type": str(atom.get("fact_type")), "count": len(bindings),
            }
            steps.append(step)
            if not bindings:
                return self._blocked(
                    clause_index, steps, step, previous, None, depth, path,
                    reads=_term_variables(list(checker.atom_bind(atom).values())),
                )
        for index, comparison in enumerate(clause.get("where") or ()):
            previous = bindings
            bindings = self._compare(previous, comparison)
            step = {"kind": "comparison", "index": index, "count": len(bindings)}
            steps.append(step)
            if not bindings:
                return self._blocked(
                    clause_index, steps, step, previous, None, depth, path,
                    reads=_term_variables([comparison.get("left"), comparison.get("right")]),
                )
        if row is not None:
            previous = bindings
            bindings = self._head(fact_type_id, clause, previous, row)
            step = {"kind": "head", "index": 0, "count": len(bindings)}
            steps.append(step)
            if not bindings:
                return self._blocked(
                    clause_index, steps, step, previous, None, depth, path,
                    reads=_term_variables(list(clause["head"].values())),
                )
        raise WhyNotInternalError(
            f"clause {clause_index} of {fact_type_id!r} walks to a non-empty end "
            "although production did not derive the target"
        )

    def _candidates(self, atom):
        facts = self.facts.get(str(atom.get("fact_type")), ())
        self.budget.charge("probes", len(facts))
        candidates = checker._joined_atom_candidates(
            atom, self.facts, variable_of=checker._derivation_variable, work=None
        )
        # Identity-duplicate rows yield one candidate, so every pair the join
        # visits produces a distinct, charged binding.
        distinct: dict[tuple, dict] = {}
        for candidate in candidates:
            distinct.setdefault(_binding_key(candidate), candidate)
        return list(distinct.values())

    def _join(self, previous, atom):
        candidates = self._candidates(atom)
        bound = set(previous[0]) if previous else set()
        variables = {
            variable for term in checker.atom_bind(atom).values()
            if (variable := checker._derivation_variable(term)) is not None
        }
        shared = sorted(variables & bound)
        produced: dict = {}
        if not shared:
            for left in previous:
                for right in candidates:
                    merged = dict(left)
                    merged.update(right)
                    self._store(produced, merged)
            return list(produced.values())
        index: dict = {}
        for candidate in candidates:
            key = tuple(checker._identity_key(candidate[name]) for name in shared)
            index.setdefault(key, []).append(candidate)
        for left in previous:
            self.budget.charge("probes")
            key = tuple(checker._identity_key(left[name]) for name in shared)
            for right in index.get(key, ()):
                merged = dict(left)
                merged.update(right)
                self._store(produced, merged)
        return list(produced.values())

    def _ground(self, atom, binding):
        values = []
        for term in checker.atom_bind(atom).values():
            variable = checker._derivation_variable(term)
            values.append(binding[variable] if variable is not None else term)
        return _identity_row(values)

    def _negate(self, previous, atom):
        binds = checker.atom_bind(atom)
        role_names = tuple(binds)
        facts = self.facts.get(str(atom.get("fact_type")), ())
        self.budget.charge("probes", len(facts))
        present = {
            _identity_row(fact[name] for name in role_names)
            for fact in facts
            if all(name in fact for name in role_names)
        }
        survivors = []
        for binding in previous:
            self.budget.charge("probes")
            if self._ground(atom, binding) not in present:
                survivors.append(binding)
        return survivors

    def _compare(self, previous, comparison):
        survivors = []
        for binding in previous:
            result = checker.compare_terms(
                str(comparison.get("operator")), comparison.get("left"),
                comparison.get("right"), binding,
            )
            if not result.available:
                raise WhyNotInternalError("a comparison production evaluated is unavailable here")
            if result.value is True:
                survivors.append(binding)
        return survivors

    def _head(self, fact_type_id, clause, previous, row):
        claimed = _identity_row(cell["value"] for cell in row)
        survivors = []
        for binding in previous:
            values = []
            for role, _primitive in self.roles[fact_type_id]:
                result = checker.evaluate_term(clause["head"][role], binding)
                if not result.available:
                    raise WhyNotInternalError("a head term production evaluated is unavailable here")
                values.append(checker.materialize_scalar(result.value))
            if _identity_row(values) == claimed:
                survivors.append(binding)
        return survivors

    def _blocked(self, clause_index, steps, step, previous, atom, depth, path, reads=()):
        blocker = dict(step)
        descent = stopped = None
        if atom is not None:
            blocker, grounded = self._atom_blocker(step, previous, atom)
            descent, stopped = self._descend(atom, blocker, grounded, depth, path)
        else:
            reads = sorted(set(reads) & set(previous[0])) if previous else []
            blocker["reads"] = ["$" + name for name in reads]
            blocker["sample_count"] = len(previous)
            blocker["samples"] = self._samples(previous, {name: name for name in reads})
        return ClauseExplanation(
            clause_index, tuple(steps), blocker, "not-evaluated", descent, stopped
        )

    def _samples(self, previous, projection: dict[str, str]):
        seen: dict[tuple, dict] = {}
        for binding in previous:
            sample = {label: binding[name] for label, name in projection.items() if name in binding}
            seen.setdefault(_binding_key(sample), sample)
        return sorted(seen.values(), key=_canonical)[:5]

    def _atom_blocker(self, step, previous, atom):
        fact_type_id = str(atom.get("fact_type"))
        bound = set(previous[0]) if previous else set()
        roles: dict[str, dict] = {}
        projection: dict[str, str] = {}
        for role, term in checker.atom_bind(atom).items():
            variable = checker._derivation_variable(term)
            if variable is None:
                roles[role] = {"constant": term}
            else:
                roles[role] = {"variable": "$" + variable, "bound": variable in bound}
                if variable in bound:
                    projection[role] = variable
        ground = all("constant" in spec or spec["bound"] for spec in roles.values())
        definition = self.index.fact_type(fact_type_id) or {}
        derivation = (
            str(definition.get("derivation"))
            if definition.get("derivation") in ("derived", "semiderived")
            and isinstance(definition.get("derivation_rule"), dict)
            else "base"
        )
        samples = self._samples(previous, projection)
        grounded = []
        if ground:
            for sample in samples:
                values = [
                    spec["constant"] if "constant" in spec else sample[role]
                    for role, spec in roles.items()
                ]
                grounded.append(dict(zip(roles, values, strict=True)))
        asserted_not_read = False
        if derivation == "semiderived" and grounded:
            asserted = {
                _identity_row(fact.get(role) for role in roles)
                for fact in self.population.facts.get(fact_type_id, ())
            }
            asserted_not_read = any(
                _identity_row(values.values()) in asserted for values in grounded
            )
        blocker = {
            "kind": "atom", "index": step["index"], "fact_type": fact_type_id,
            "derivation": derivation, "ground": ground,
            "asserted_not_read": asserted_not_read, "roles": roles,
            "sample_count": len(previous), "samples": samples,
        }
        return blocker, grounded

    def _descend(self, atom, blocker, grounded, depth, path):
        fact_type_id = blocker["fact_type"]
        if blocker["derivation"] == "base":
            return None, "not-derived"
        if not grounded:
            return None, "not-ground"
        values = grounded[0]
        row = [
            {"primitive": primitive, "value": values[role]}
            for role, primitive in self.roles[fact_type_id]
        ]
        key = (fact_type_id, _canonical(row))
        if key in path:
            return None, "cycle"
        if depth + 1 > MAX_DESCENT:
            return None, "depth"
        if depth + 1 > self.budget.limits.proof_depth:
            raise WhyNotWorkError("proof_depth ceiling", self.budget.work)
        nested = self.explain(fact_type_id, row, depth=depth + 1, path=(*path, key))
        if nested.status == "derived":
            raise WhyNotInternalError("descent derived a row production reported absent")
        return nested, None
