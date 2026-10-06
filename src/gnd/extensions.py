"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

import math
from collections.abc import Callable, Collection, Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass, field
from decimal import Decimal
from fractions import Fraction
from types import MappingProxyType
from typing import Any, Literal

from pydantic import BaseModel, Field, model_validator

from gnd import verbalize
from gnd.address import derivation_address
from gnd.atoms import atom_bind
from gnd.branches import UnregisteredBranchError, branch, record_branch
from gnd.documents import Model
from gnd.errors import UnvalidatedPopulationError
from gnd.model import (
    AggregateAnalysis,
    _derivation_variable,
    analyze_declared_aggregate,
    body_components,
    derivation_classifications,
    derivation_dependencies,
    derivation_strata,
    iter_derivation_clauses,
)
from gnd.population import Population
from gnd.terms import (
    DEFAULT_LIMITS,
    compare_terms,
    evaluate_term,
    is_function_term,
    materialize_scalar,
    term_variables,
)
from gnd.universe import resolve_primitive
from gnd.values import identity_key as _identity_key

DerivationKind = Literal[
    "derived-extension-incomplete",
    "derived-extension-unsound",
    "derived-extension-unresolved",
]


DerivationReason = Literal[
    "derivation-not-covered",
    "derivation-rule-opaque",
    "opaque-value",
    "derived-unknown",
    "term:mod-zero",
    "term:exact-value-too-wide",
    "term:dependency-unavailable",
    "term:div-zero",
    "term:sqrt-negative",
    "term:haversine-coordinate-range",
    "term:float-overflow",
]


DERIVATION_REASON_CODES: tuple[DerivationReason, ...] = (
    "derivation-not-covered",
    "derivation-rule-opaque",
    "opaque-value",
    "derived-unknown",
)


EXACT_DERIVATION_REASON_CODES: tuple[DerivationReason, ...] = (
    "derived-unknown",
    "term:mod-zero",
    "term:exact-value-too-wide",
    "term:dependency-unavailable",
    "term:div-zero",
    "term:sqrt-negative",
    "term:haversine-coordinate-range",
    "term:float-overflow",
)


class DerivationFinding(BaseModel):
    """One missing or offending row in a structured derivation claim."""

    kind: DerivationKind
    message: str
    witness: dict[str, Any]


class DerivationVerdict(BaseModel):
    """One alethic comparison obligation for one derived fact type."""

    scope_id: str = Field(exclude=True)
    derivation_ref: str
    fact_type: str
    derivation: Literal["derived", "semiderived"]
    modality: Literal["alethic"] = "alethic"
    verdict: Literal["pass", "fail", "unchecked"]
    message: str
    findings: list[DerivationFinding] = Field(default_factory=list)
    reason_code: DerivationReason | None = None

    @model_validator(mode="after")
    def _closed_shape(self) -> DerivationVerdict:
        if self.derivation_ref != derivation_address(self.fact_type):
            raise ValueError("derivation_ref must address fact_type")
        if self.verdict == "pass" and (self.findings or self.reason_code is not None):
            raise ValueError("pass derivations have neither findings nor a reason")
        if self.verdict == "fail":
            if not 1 <= len(self.findings) <= 3 or self.reason_code is not None:
                raise ValueError("fail derivations have one to three findings and no reason")
            kinds = [finding.kind for finding in self.findings]
            canonical = [
                kind
                for kind in (
                    "derived-extension-incomplete",
                    "derived-extension-unsound",
                    "derived-extension-unresolved",
                )
                if kind in kinds
            ]
            if kinds != canonical or len(kinds) != len(set(kinds)):
                raise ValueError("derivation findings must be unique and canonically ordered")
        if self.verdict == "unchecked" and (
            self.reason_code not in (*DERIVATION_REASON_CODES, *EXACT_DERIVATION_REASON_CODES)
            or (self.findings and (
                self.reason_code != "derived-unknown"
                or len(self.findings) != 1
                or self.findings[0].kind != "derived-extension-unresolved"
            ))
            or (self.reason_code == "derived-unknown" and not self.findings)
        ):
            raise ValueError("unchecked derivations require a closed reason and matching findings")
        row = branch(self.scope_id)
        if (row.surface, row.family) not in {
            ("derivation", "extension"),
            ("experiment-feedback", "verifier-derivation"),
        } or row.variant != self.derivation:
            raise UnregisteredBranchError("derivation branch names another obligation")
        if row.reason_code != self.reason_code:
            raise UnregisteredBranchError("derivation reason disagrees with its branch")
        record_branch(self.scope_id, outcome=self.verdict)
        return self


class JoinDisconnectedError(Exception):
    """The referenced fact types cannot be chained through shared anchor object
    types — evaluating would silently degrade to a cross join and produce
    provably wrong counts/verdicts (CR-02). Surfaced as an ``unchecked``
    verdict by :func:`_verdict_for`, never silently evaluated.
    """

    def __init__(self, fact_type_ids: list[str]):
        self.fact_type_ids = list(fact_type_ids)
        super().__init__(
            "role references span fact types with no shared anchor object type: "
            + ", ".join(self.fact_type_ids)
        )


Scalar = str | int | float | bool


IdentityCodecVersion = Literal["gnd-identity-json/1"]


FactPath = tuple[str | int, ...]


RowLineage = tuple[FactPath, ...]


@dataclass(frozen=True)
class _TypedRelation:
    fact_type: str
    roles: tuple[tuple[str, str | None], ...]
    rows: tuple[tuple[Scalar, ...], ...]
    row_lineage: tuple[RowLineage, ...] = ()
    identity_codec_version: IdentityCodecVersion = "gnd-identity-json/1"


@dataclass
class _JoinWork:
    atom_role_terms_read: int = 0
    positive_candidate_rows_emitted: int = 0
    join_candidates_indexed: int = 0
    join_left_bindings_probed: int = 0
    join_matches_merged: int = 0
    component_product_rows_emitted: int = 0
    negation_rows_indexed: int = 0
    negation_bindings_probed: int = 0
    head_cells_projected: int = 0


@dataclass
class _ExactJoinWork(_JoinWork):
    term_nodes_visited: int = 0
    term_operations: int = 0
    max_exact_value_bits: int = 0
    aggregate_candidate_bindings: int = 0
    aggregate_contribution_terms: int = 0
    aggregate_identity_tokens: int = 0
    aggregate_distinct_contributions: int = 0
    aggregate_group_lookups: int = 0
    aggregate_groups: int = 0
    aggregate_exact_operations: int = 0
    aggregate_maximum_value_bits: int = 0


@dataclass
class _FixpointJoinWork(_ExactJoinWork):
    fixpoint_iterations: int = 0
    canonical_insertions: int = 0


def _count_term_work(work: _ExactJoinWork, result: Any) -> None:
    work.term_nodes_visited += int(getattr(result, "nodes", 0))
    work.term_operations += int(getattr(result, "operations", 0))
    work.max_exact_value_bits = max(
        work.max_exact_value_bits,
        int(getattr(result, "max_value_bits", 0)),
    )


@dataclass(frozen=True)
class _ExtensionResult:
    extensions: Mapping[str, _TypedRelation]
    counted_operations: _JoinWork


@dataclass(frozen=True)
class RelationUnavailable:
    relation: str
    reason: str
    binding: Mapping[str, Scalar]
    source_relation: str | None = None


class _ExactExtensions(dict[str, _TypedRelation]):
    """Extension mapping carrying relation-level unavailability out of band."""

    def __init__(
        self,
        *args: Any,
        unavailable: Mapping[str, RelationUnavailable] | None = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.unavailable = MappingProxyType(dict(unavailable or {}))


@dataclass(frozen=True)
class _Wildcard:
    primitive: str | None
    coordinate: tuple[str, int, str]


class _PartialTermFailure(Exception):
    def __init__(self, reason: str, binding: Mapping[str, Any]) -> None:
        self.reason = reason
        self.binding = MappingProxyType(dict(binding))


class _PartialExtensions(_ExactExtensions):
    """Definite extension rows plus finite possible patterns, kept internal."""

    def __init__(
        self, *args: Any,
        possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]],
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.possible = MappingProxyType(dict(possible))


_PARTIAL_OPAQUE: ContextVar[bool] = ContextVar("gnd_partial_opaque", default=False)


def _symbolic_value(value: Any, primitive: str | None, coordinate: tuple[str, int, str]) -> Scalar | _Wildcard:
    if isinstance(value, dict) and set(value) == {"$opaque"}:
        return _Wildcard(primitive, coordinate)
    return value


def _partial_token(value: Scalar | _Wildcard) -> bytes:
    if isinstance(value, _Wildcard):
        return repr(("wildcard", value.primitive, value.coordinate)).encode()
    return _identity_token(value)


def _partial_compatible(left: Scalar | _Wildcard, right: Scalar | _Wildcard) -> bool:
    if isinstance(left, _Wildcard) and isinstance(right, _Wildcard):
        return left.primitive == right.primitive or None in (left.primitive, right.primitive)
    if isinstance(left, _Wildcard):
        return left.primitive is None or _scalar_primitive_compatible(right, left.primitive)
    if isinstance(right, _Wildcard):
        return right.primitive is None or _scalar_primitive_compatible(left, right.primitive)
    return _identity_token(left) == _identity_token(right)


def _scalar_primitive_compatible(value: Scalar, primitive: str) -> bool:
    if primitive in {"String", "Binary", "Date", "DateTime"}:
        return isinstance(value, str)
    if primitive == "Boolean":
        return isinstance(value, bool)
    if primitive == "Integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if primitive in {"Float", "Number"}:
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    return True


def _partial_merge(left: Scalar | _Wildcard, right: Scalar | _Wildcard) -> Scalar | _Wildcard:
    if isinstance(left, _Wildcard):
        return right if not isinstance(right, _Wildcard) else min((left, right), key=_partial_token)
    return left


def _partial_row_facts(
    roles: tuple[tuple[str, str | None], ...],
    rows: Sequence[tuple[Scalar | _Wildcard, ...]],
) -> tuple[dict[str, Scalar | _Wildcard], ...]:
    return tuple(dict(zip((name for name, _ in roles), row, strict=True)) for row in rows)


def _partial_binding_shape(binding: Mapping[str, Scalar | _Wildcard]) -> tuple[Any, ...]:
    """Equivalent symbolic rows cover the same may-bindings regardless of source cell."""
    names: dict[tuple[str, int, str], int] = {}
    result = []
    for role, value in sorted(binding.items()):
        if isinstance(value, _Wildcard):
            ordinal = names.setdefault(value.coordinate, len(names))
            result.append((role, "wildcard", value.primitive, ordinal))
        else:
            result.append((role, "scalar", _partial_token(value)))
    return tuple(result)


def _partial_bindings(
    atoms: Sequence[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    work: _FixpointJoinWork,
    *,
    compact: bool = True,
) -> list[dict[str, Scalar | _Wildcard]]:
    bindings: list[dict[str, Scalar | _Wildcard]] = [{}]
    for atom in atoms:
        candidates: list[dict[str, Scalar | _Wildcard]] = []
        binds = atom_bind(atom)
        for fact in facts.get(str(atom.get("fact_type")), ()):
            candidate: dict[str, Scalar | _Wildcard] = {}
            for role, term in binds.items():
                work.atom_role_terms_read += 1
                if role not in fact:
                    break
                value = fact[role]
                variable = _derivation_variable(term)
                if variable is None:
                    if not _partial_compatible(value, term):
                        break
                elif variable in candidate:
                    if not _partial_compatible(candidate[variable], value):
                        break
                    candidate[variable] = _partial_merge(candidate[variable], value)
                else:
                    candidate[variable] = value
            else:
                candidates.append(candidate)
                work.positive_candidate_rows_emitted += 1
        if compact:
            candidates = list({
                _partial_binding_shape(candidate): candidate for candidate in candidates
            }.values())
        joined: list[dict[str, Scalar | _Wildcard]] = []
        seen: set[tuple[Any, ...]] = set()
        shared = tuple(name for name in candidates[0] if name in bindings[0]) if candidates and bindings else ()
        index: dict[tuple[bytes, ...], list[dict[str, Scalar | _Wildcard]]] = {}
        wildcard_candidates: list[dict[str, Scalar | _Wildcard]] = []
        if shared:
            for candidate in candidates:
                if any(isinstance(candidate[name], _Wildcard) for name in shared):
                    wildcard_candidates.append(candidate)
                else:
                    key = tuple(_partial_token(candidate[name]) for name in shared)
                    index.setdefault(key, []).append(candidate)
                    work.join_candidates_indexed += 1
        for left in bindings:
            if shared and all(not isinstance(left[name], _Wildcard) for name in shared):
                key = tuple(_partial_token(left[name]) for name in shared)
                probes = [*index.get(key, ()), *wildcard_candidates]
            else:
                probes = candidates
            work.join_left_bindings_probed += 1
            for right in probes:
                _witness_charge()
                if any(name in left and not _partial_compatible(left[name], value)
                       for name, value in right.items()):
                    continue
                merged = dict(left)
                for name, value in right.items():
                    merged[name] = _partial_merge(merged[name], value) if name in merged else value
                shape = _partial_binding_shape(merged) if compact else ()
                if not compact or shape not in seen:
                    seen.add(shape)
                    joined.append(merged)
                    work.join_matches_merged += 1
        bindings = joined
        if not bindings:
            break
    return bindings


def _partial_negation(
    bindings: list[dict[str, Scalar | _Wildcard]],
    atoms: Sequence[dict[str, Any]],
    blockers: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    *,
    definite: bool,
) -> list[dict[str, Scalar | _Wildcard]]:
    for atom in atoms:
        retained = []
        for binding in bindings:
            blocked = False
            for fact in blockers.get(str(atom.get("fact_type")), ()):
                values: list[tuple[Scalar | _Wildcard, Scalar | _Wildcard]] = []
                for role, term in atom_bind(atom).items():
                    variable = _derivation_variable(term)
                    if role not in fact or (variable is not None and variable not in binding):
                        break
                    values.append((fact[role], binding[variable] if variable is not None else term))
                else:
                    # A concrete blocker excludes a concrete candidate.
                    # A symbolic candidate may still describe other values.
                    if all(_partial_compatible(a, b) for a, b in values) and (
                        definite or all(not isinstance(b, _Wildcard) for _a, b in values)
                    ):
                        blocked = True
                        break
            if not blocked:
                retained.append(binding)
        bindings = retained
    return bindings


_WITNESS_TRACE: ContextVar[Any] = ContextVar("gnd_witness_trace", default=None)


def _witness_charge(amount: int = 1) -> None:
    trace = _WITNESS_TRACE.get()
    if trace is not None:
        trace.charge(amount)


def _witness_row(fact_type, clause, binding, row) -> None:
    trace = _WITNESS_TRACE.get()
    if trace is not None:
        trace.row(fact_type, clause, binding, row)


def _partial_clause_rows(
    model: Model,
    fact_type: dict[str, Any],
    clause: dict[str, Any],
    must_facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    may_facts: Mapping[str, Sequence[Mapping[str, Scalar | _Wildcard]]],
    must_lineages: Mapping[str, tuple[RowLineage, ...]],
    work: _FixpointJoinWork,
    *,
    definite: bool,
) -> list[tuple[tuple[Scalar | _Wildcard, ...], RowLineage]]:
    source = must_facts if definite else may_facts
    bindings = _partial_bindings(clause.get("body") or (), source, work, compact=not definite)
    bindings = _partial_negation(
        bindings, clause.get("negate") or (), may_facts if definite else must_facts,
        definite=definite,
    )
    aggregate = clause.get("aggregate")
    if isinstance(aggregate, dict):
        analysis = analyze_declared_aggregate(model, clause)
        group_names = analysis.group_variables
        result_name = analysis.result_variable or str(aggregate.get("as", "")).removeprefix("$")
        if definite:
            possible_bindings = _partial_negation(
                _partial_bindings(clause.get("body") or (), may_facts, work),
                clause.get("negate") or (), must_facts, definite=False,
            )
            bindings = [
                binding for binding in bindings
                if not any(
                    any(isinstance(value, _Wildcard) for value in candidate.values())
                    and all(_partial_compatible(binding[name], candidate[name]) for name in group_names)
                    for candidate in possible_bindings
                )
            ]
            bindings, failure = _aggregate_bindings(clause, bindings, work, analysis)
            if failure is not None:
                raise _PartialTermFailure(failure.reason, failure.binding)
        else:
            grouped: dict[tuple[bytes, ...], list[dict[str, Scalar | _Wildcard]]] = {}
            for binding in bindings:
                key = tuple(_partial_token(binding[name]) for name in group_names)
                grouped.setdefault(key, []).append(binding)
            collapsed = []
            for members in grouped.values():
                if any(isinstance(value, _Wildcard) for member in members for value in member.values()):
                    representative = {name: members[0][name] for name in group_names}
                    representative[result_name] = _Wildcard(
                        None, (str(fact_type.get("id")), 0, result_name)
                    )
                    collapsed.append(representative)
                else:
                    exact_rows, failure = _aggregate_bindings(clause, members, work, analysis)
                    if failure is not None:
                        raise _PartialTermFailure(failure.reason, failure.binding)
                    collapsed.extend(exact_rows)
            bindings = collapsed
    if clause.get("where"):
        filtered = []
        for binding in bindings:
            keep = True
            for comparison in clause["where"]:
                used = set(term_variables(comparison.get("left"))) | set(term_variables(comparison.get("right")))
                if any(isinstance(binding.get(name), _Wildcard) for name in used):
                    if definite:
                        keep = False
                    continue
                result = compare_terms(
                    str(comparison.get("operator")), comparison.get("left"),
                    comparison.get("right"), binding,
                    bound_cross_product=bool(clause.get("aggregate")),
                )
                if not result.available:
                    raise _PartialTermFailure(str(result.reason), binding)
                if result.available and result.value is not True:
                    keep = False
                    break
            if keep:
                filtered.append(binding)
        bindings = filtered
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or ()]
    proofs = (
        _binding_lineages(clause, bindings, must_facts, must_lineages)
        if definite and not clause.get("aggregate")
        else tuple(() for _ in bindings)
    )
    rows = []
    for binding, proof in zip(bindings, proofs, strict=True):
        row = []
        for role in role_names:
            term = clause["head"][role]
            variable = _derivation_variable(term)
            if variable is not None:
                row.append(binding[variable])
            elif is_function_term(term):
                if any(isinstance(value, _Wildcard) for value in binding.values()):
                    row.append(_Wildcard(_relation_roles(model, fact_type)[len(row)][1],
                                         (str(fact_type.get("id")), 0, role)))
                else:
                    result = evaluate_term(term, binding)
                    if result.available:
                        try:
                            row.append(materialize_scalar(result.value))
                        except ValueError:
                            raise _PartialTermFailure("term:head-non-integral", binding) from None
                    else:
                        raise _PartialTermFailure(str(result.reason), binding)
            else:
                row.append(term)
            work.head_cells_projected += 1
        if len(row) == len(role_names) and (not definite or not any(isinstance(v, _Wildcard) for v in row)):
            if definite:
                _witness_row(fact_type, clause, binding, tuple(row))
            rows.append((tuple(row), proof))
    return rows


@dataclass(frozen=True)
class _ExactExtensionResult:
    extensions: _ExactExtensions
    counted_operations: _JoinWork


ExtensionCalculator = Callable[
    [Model, Mapping[str, _TypedRelation]],
    _ExtensionResult,
]


VariableResolver = Callable[[Any], str | None]


@dataclass(frozen=True)
class _RuledFactView:
    covers: tuple[str, ...]
    instances: Mapping[str, tuple[Scalar, ...]]
    facts: Mapping[str, tuple[Mapping[str, Scalar], ...]]
    lineages: Mapping[str, tuple[RowLineage, ...]]


def _identity_token(value: Scalar) -> bytes:
    """Canonical scalar identity from representation-format.md."""
    import json

    if isinstance(value, bool):
        payload: list[Any] = ["boolean", value]
    elif isinstance(value, int):
        payload = ["number", [value, 1]]
    elif isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("non-finite values have no identity token")
        numerator, denominator = value.as_integer_ratio()
        payload = ["number", [numerator, denominator]]
    elif isinstance(value, str):
        payload = ["string", value]
    else:
        raise TypeError(f"unsupported identity scalar: {type(value).__name__}")
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()


def _joined_atom_candidates(
    atom: dict[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    *,
    variable_of: VariableResolver,
    work: _JoinWork | None,
) -> list[dict[str, Scalar]]:
    """Match one antecedent atom without a seed binding.

    Each returned mapping is one fact's internally consistent variable
    assignment.  In particular, a variable repeated in one atom must have the
    same identity at every role before the fact becomes a candidate.
    """
    fact_type_id = str(atom.get("fact_type"))
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return []
    candidates: list[dict[str, Scalar]] = []
    rows = facts.get(fact_type_id, ())
    for fact in rows:
        if not isinstance(fact, Mapping):
            continue
        candidate: dict[str, Scalar] = {}
        matches = True
        for role_name, term in binds.items():
            if work is not None:
                work.atom_role_terms_read += 1
            if role_name not in fact:
                matches = False
                break
            value = fact[role_name]
            variable = variable_of(term)
            if variable is None:
                if _identity_key(value) != _identity_key(term):
                    matches = False
                    break
            elif variable in candidate:
                if _identity_key(value) != _identity_key(candidate[variable]):
                    matches = False
                    break
            else:
                candidate[variable] = value
        if matches:
            candidates.append(candidate)
            if work is not None:
                work.positive_candidate_rows_emitted += 1
    return candidates


_REFERENCE_PRESENTATION_WORK: ContextVar[Any] = ContextVar(
    "reference_presentation_work", default=None
)


def _joined_bindings(
    atoms: list[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    *,
    variable_of: VariableResolver,
    work: _JoinWork | None,
) -> list[dict[str, Scalar]]:
    """Enumerate one connected atom component with indexed hash joins."""
    if not atoms:
        return []
    variable_order = list(
        dict.fromkeys(
            variable
            for atom in atoms
            for term in atom_bind(atom).values()
            if (variable := variable_of(term)) is not None
        )
    )
    variables = [
        {
            variable
            for term in atom_bind(atom).values()
            if (variable := variable_of(term)) is not None
        }
        for atom in atoms
    ]

    # Choose the earliest atom that connects to the variables bound so far.
    # This preserves declaration order among available atoms while avoiding an
    # intermediate cross product when a later atom is the connecting bridge.
    order = [0]
    bound_variables = set(variables[0])
    remaining = list(range(1, len(atoms)))
    while remaining:
        next_index = next(
            (index for index in remaining if variables[index] & bound_variables),
            None,
        )
        if next_index is None:
            raise JoinDisconnectedError([str(atom.get("fact_type")) for atom in atoms])
        order.append(next_index)
        bound_variables |= variables[next_index]
        remaining.remove(next_index)

    candidates = [
        _joined_atom_candidates(
            atom,
            facts,
            variable_of=variable_of,
            work=work,
        )
        for atom in atoms
    ]
    bindings = candidates[order[0]]
    _witness_charge(len(bindings))
    seen_variables = set(variables[order[0]])
    for atom_index in order[1:]:
        shared = [
            variable
            for variable in atom_bind(atoms[atom_index]).values()
            if variable_of(variable) in seen_variables
        ]
        shared = list(
            dict.fromkeys(
                variable_of(variable) for variable in shared if variable_of(variable) is not None
            )
        )
        index: dict[tuple[tuple[Any, ...], ...], list[dict[str, Any]]] = {}
        for candidate in candidates[atom_index]:
            key = tuple(_identity_key(candidate[variable]) for variable in shared)
            index.setdefault(key, []).append(candidate)
            if work is not None:
                work.join_candidates_indexed += 1

        joined: list[dict[str, Any]] = []
        for binding in bindings:
            if work is not None:
                work.join_left_bindings_probed += 1
            key = tuple(_identity_key(binding[variable]) for variable in shared)
            for candidate in index.get(key, []):
                _witness_charge()
                reference_work = _REFERENCE_PRESENTATION_WORK.get()
                if reference_work is not None:
                    reference_work.charge()
                if any(
                    variable in binding and _identity_key(binding[variable]) != _identity_key(value)
                    for variable, value in candidate.items()
                ):
                    continue
                merged = dict(binding)
                for variable, value in candidate.items():
                    merged.setdefault(variable, value)
                joined.append(merged)
                if work is not None:
                    work.join_matches_merged += 1
        bindings = joined
        seen_variables |= variables[atom_index]
    return [
        {variable: binding[variable] for variable in variable_order if variable in binding}
        for binding in bindings
    ]


def _relation_facts(
    relations: Mapping[str, _TypedRelation],
) -> Mapping[str, Sequence[Mapping[str, Scalar]]]:
    return MappingProxyType(
        {
            fact_type_id: tuple(
                MappingProxyType(
                    {
                        role_name: value
                        for (role_name, _primitive), value in zip(relation.roles, row, strict=True)
                    }
                )
                for row in relation.rows
            )
            for fact_type_id, relation in relations.items()
        }
    )


def _relation_roles(model: Model, fact_type: dict[str, Any]) -> tuple[tuple[str, str | None], ...]:
    roles: list[tuple[str, str | None]] = []
    for role in fact_type.get("roles") or []:
        object_type = str(role.get("object_type"))
        roles.append((str(role.get("role_name")), resolve_primitive(object_type, model)))
    return tuple(roles)


def _rows_from_facts(
    roles: tuple[tuple[str, str | None], ...],
    facts: Sequence[Mapping[str, Scalar]],
) -> tuple[tuple[Scalar, ...], ...]:
    return tuple(tuple(fact[role_name] for role_name, _primitive in roles) for fact in facts)


def _base_relations(model: Model, population: Population) -> Mapping[str, _TypedRelation]:
    relations: dict[str, _TypedRelation] = {}
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        roles = _relation_roles(model, fact_type)
        rule = fact_type.get("derivation_rule")
        rows = (
            ()
            if isinstance(rule, dict)
            else _rows_from_facts(roles, population.facts.get(fact_type_id, ()))
        )
        row_lineage = (
            ()
            if isinstance(rule, dict)
            else tuple((("facts", fact_type_id, index),) for index, _row in enumerate(rows))
        )
        relations[fact_type_id] = _TypedRelation(fact_type_id, roles, rows, row_lineage=row_lineage)
    return MappingProxyType(relations)


def _component_atoms(rule: dict[str, Any]) -> list[list[dict[str, Any]]]:
    components = body_components(rule)
    grouped: list[list[dict[str, Any]]] = [[] for _component in components]
    for index, atom in enumerate(rule.get("body") or []):
        variables = {
            variable
            for term in atom_bind(atom).values()
            if (variable := _derivation_variable(term)) is not None
        }
        if variables:
            component_index = next(
                slot for slot, component in enumerate(components) if variables <= component
            )
        else:
            marker = f"\u0000grounded:.body[{index}]"
            component_index = next(
                slot for slot, component in enumerate(components) if marker in component
            )
        grouped[component_index].append(atom)
    return grouped


def _component_product(
    component_bindings: Sequence[Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    product: list[dict[str, Scalar]] = [{}]
    for component_index, bindings in enumerate(component_bindings):
        next_product: list[dict[str, Scalar]] = []
        for left in product:
            for right in bindings:
                if component_index:
                    _witness_charge()
                if any(
                    variable in left and _identity_key(left[variable]) != _identity_key(value)
                    for variable, value in right.items()
                ):
                    continue
                merged = dict(left)
                merged.update(right)
                next_product.append(merged)
                work.component_product_rows_emitted += 1
        product = next_product
    return product


def _apply_negation(
    bindings: list[dict[str, Scalar]],
    atoms: Sequence[dict[str, Any]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    remaining = bindings
    for atom in atoms:
        binds = atom_bind(atom)
        role_names = tuple(str(role_name) for role_name in binds)
        index: set[tuple[bytes, ...]] = set()
        for fact in facts.get(str(atom.get("fact_type")), ()):
            if all(role_name in fact for role_name in role_names):
                index.add(tuple(_identity_token(fact[role_name]) for role_name in role_names))
                work.negation_rows_indexed += 1
        survivors: list[dict[str, Scalar]] = []
        for binding in remaining:
            values: list[Scalar] = []
            resolvable = True
            for term in binds.values():
                variable = _derivation_variable(term)
                if variable is None:
                    values.append(term)
                elif variable in binding:
                    values.append(binding[variable])
                else:
                    resolvable = False
                    break
            work.negation_bindings_probed += 1
            if not resolvable or tuple(_identity_token(value) for value in values) not in index:
                survivors.append(binding)
        remaining = survivors
    return remaining


def _clause_bindings(
    rule: Mapping[str, Any],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    work: _JoinWork,
) -> list[dict[str, Scalar]]:
    """Retain the production component/product/negation sequence for every caller."""
    components = [
        _joined_bindings(atoms, facts, variable_of=_derivation_variable, work=work)
        for atoms in _component_atoms(rule)
    ]
    bindings = _component_product(components, work)
    return _apply_negation(bindings, rule.get("negate") or [], facts, work)


def _project_extension(
    fact_type: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    work: _JoinWork,
) -> tuple[tuple[Scalar, ...], ...]:
    rule = fact_type["derivation_rule"]
    head = rule["head"]
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
    unique: dict[tuple[bytes, ...], tuple[Scalar, ...]] = {}
    for binding in bindings:
        row: list[Scalar] = []
        for role_name in role_names:
            term = head[role_name]
            variable = _derivation_variable(term)
            row.append(binding[variable] if variable is not None else term)
            work.head_cells_projected += 1
        typed_row = tuple(row)
        unique.setdefault(tuple(_identity_token(value) for value in typed_row), typed_row)
    return tuple(unique[key] for key in sorted(unique))


def _binding_lineages(
    rule: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]],
    fact_lineages: Mapping[str, tuple[RowLineage, ...]],
) -> tuple[RowLineage, ...]:
    """Retain one deterministic, row-exact positive proof for each binding."""
    indexes: list[tuple[dict[str, Any], dict[tuple[bytes, ...], RowLineage]]] = []
    for atom in rule.get("body") or ():
        fact_type_id = str(atom.get("fact_type"))
        binds = atom_bind(atom)
        role_names = tuple(str(role_name) for role_name in binds)
        row_lineages = fact_lineages.get(fact_type_id, ())
        index: dict[tuple[bytes, ...], RowLineage] = {}
        for row_index, fact in enumerate(facts.get(fact_type_id, ())):
            if not all(role_name in fact for role_name in role_names):
                continue
            key = tuple(_identity_token(fact[role_name]) for role_name in role_names)
            lineage = row_lineages[row_index] if row_index < len(row_lineages) else ()
            index.setdefault(key, lineage)
        indexes.append((binds, index))

    result: list[RowLineage] = []
    for binding in bindings:
        support: set[FactPath] = set()
        for binds, index in indexes:
            values: list[Scalar] = []
            for term in binds.values():
                variable = _derivation_variable(term)
                values.append(binding[variable] if variable is not None else term)
            support.update(index[tuple(_identity_token(value) for value in values)])
        result.append(tuple(sorted(support, key=lambda path: tuple(map(str, path)))))
    return tuple(result)


def _project_lineage(
    fact_type: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    binding_lineages: Sequence[RowLineage],
) -> tuple[RowLineage, ...]:
    """Mirror extension de-duplication while retaining its selected proof rows."""
    head = fact_type["derivation_rule"]["head"]
    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
    unique: dict[tuple[bytes, ...], RowLineage] = {}
    for binding, lineage in zip(bindings, binding_lineages, strict=True):
        row = []
        for role_name in role_names:
            term = head[role_name]
            variable = _derivation_variable(term)
            row.append(binding[variable] if variable is not None else term)
        unique.setdefault(tuple(_identity_token(value) for value in row), lineage)
    return tuple(unique[key] for key in sorted(unique))


def _python_extension_calculator(
    model: Model,
    relations: Mapping[str, _TypedRelation],
) -> _ExtensionResult:
    """Evaluate the structured rule language defined in representation-format.md."""
    if _requires_fixpoint(model) or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in relations.values() for row in relation.rows for value in row
    ):
        return _evaluate_stratified_extensions(model, relations, exact=False)
    # Materialize the asserted view once. Each completed stratum then contributes
    # only its own relation. Rebuilding every prior relation for every stratum is
    # quadratic in the number of structured fact types before a single join is
    # evaluated, and that work used to sit outside the advertised counters.
    facts = dict(_relation_facts(relations))
    fact_lineages = {
        fact_type_id: relation.row_lineage for fact_type_id, relation in relations.items()
    }
    extensions: dict[str, _TypedRelation] = {}
    work = _JoinWork()
    fact_types = {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}
    for component in derivation_strata(model.model_dump()):
        fact_type_id = component[0]
        fact_type = fact_types[fact_type_id]
        rule = fact_type["derivation_rule"]
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        binding_lineages = _binding_lineages(rule, bindings, fact_view, fact_lineages)
        projected_rows = _project_extension(fact_type, bindings, work)
        projected_lineage = _project_lineage(fact_type, bindings, binding_lineages)
        relation = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            projected_rows,
            row_lineage=projected_lineage,
        )
        facts[fact_type_id] = _relation_facts({fact_type_id: relation})[fact_type_id]
        fact_lineages[fact_type_id] = relation.row_lineage
        extensions[fact_type_id] = relation
    return _ExtensionResult(MappingProxyType(extensions), work)


def _rule_uses_exact_terms(rule: Any) -> bool:
    if not isinstance(rule, dict):
        return False
    return any(
        "where" in clause or "aggregate" in clause
        or (isinstance(clause.get("head"), dict) and any(
            is_function_term(term) for term in clause["head"].values()
        ))
        for clause in iter_derivation_clauses(rule)
    )


def _aggregate_identity_token(value: Scalar | Fraction) -> bytes:
    """Exact numeric identity for aggregate contributions only.

    The predecessor identity encoder is pinned; aggregate arithmetic also
    produces Fraction values and may encounter integers past Python's decimal
    string conversion guard.
    """
    if isinstance(value, (int, Fraction)) and not isinstance(value, bool):
        rational = Fraction(value)
        return (
            '["number",['
            + str(Decimal(rational.numerator))
            + ","
            + str(Decimal(rational.denominator))
            + "]]"
        ).encode()
    return _identity_token(value)


def _aggregate_bindings(
    rule: dict[str, Any],
    bindings: Sequence[Mapping[str, Scalar]],
    work: _ExactJoinWork,
    analysis: AggregateAnalysis | None = None,
) -> tuple[list[dict[str, Any]], RelationUnavailable | None]:
    """Collapse body bindings into exact aggregate groups.

    The distinct contribution token deliberately contains both the ordered
    ``over`` binding and the evaluated ``of`` value.  It prevents duplicate
    proof paths from changing an aggregate while retaining distinct rows whose
    ``of`` term happens to have the same value.
    """
    aggregate = rule.get("aggregate")
    if not isinstance(aggregate, dict):
        return [dict(binding) for binding in bindings], None
    if analysis is not None and analysis.issue is None:
        over = analysis.over_variables
        result_name = analysis.result_variable or ""
        function = analysis.function or ""
        group_names = analysis.group_variables
    else:
        over = tuple(str(item)[1:] for item in aggregate.get("over", ()) if isinstance(item, str))
        result_name = str(aggregate.get("as", ""))[1:]
        function = str(aggregate.get("fn"))
        head = rule.get("head")
        group_names = tuple(
            sorted(
                {
                    variable
                    for term in head.values()
                    for variable in term_variables(term)
                    if variable != result_name
                }
            )
            if isinstance(head, dict)
            else ()
        )
    groups: dict[tuple[tuple[str, bytes], ...], list[Mapping[str, Scalar]]] = {}

    def too_wide(value: Any) -> bool:
        if isinstance(value, bool):
            return False
        if isinstance(value, int):
            bits = value.bit_length()
        elif isinstance(value, Fraction):
            bits = max(value.numerator.bit_length(), value.denominator.bit_length())
        else:
            return False
        work.max_exact_value_bits = max(work.max_exact_value_bits, bits)
        work.aggregate_maximum_value_bits = max(work.aggregate_maximum_value_bits, bits)
        return bits > DEFAULT_LIMITS.max_value_bits

    for binding in bindings:
        work.aggregate_candidate_bindings += 1
        if any(too_wide(binding[name]) for name in group_names if name in binding):
            return [], RelationUnavailable(
                "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(binding))
            )
        key = tuple(
            (name, _aggregate_identity_token(binding[name]))
            for name in group_names
            if name in binding
        )
        work.aggregate_identity_tokens += len(key)
        work.aggregate_group_lookups += 1
        groups.setdefault(key, []).append(binding)
    work.aggregate_groups += len(groups)

    collapsed: list[dict[str, Any]] = []
    for key in sorted(groups):
        members = groups[key]
        contributions: dict[tuple[bytes, ...], Any] = {}
        for binding in members:
            work.aggregate_contribution_terms += 1
            value = evaluate_term(
                analysis.value_term
                if analysis is not None and analysis.issue is None
                else aggregate.get("of"),
                binding,
            )
            _count_term_work(work, value)
            if not value.available:
                return [], RelationUnavailable(
                    "<aggregate>", str(value.reason), MappingProxyType(dict(binding))
                )
            if too_wide(value.value) or any(too_wide(binding[name]) for name in over):
                return [], RelationUnavailable(
                    "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(binding))
                )
            token = tuple(_aggregate_identity_token(binding[name]) for name in over) + (
                _aggregate_identity_token(value.value),
            )
            work.aggregate_identity_tokens += len(token)
            contributions.setdefault(token, value.value)
        # A contribution is a set member. Fold in canonical token order so
        # population row order cannot change bounded-width availability.
        values = [contributions[token] for token in sorted(contributions)]
        work.aggregate_distinct_contributions += len(values)
        if function == "count":
            result: Any = len(values)
            work.aggregate_exact_operations += 1
        else:
            numbers: list[Fraction] = []
            for value in values:
                if isinstance(value, bool) or not isinstance(value, (int, Fraction)):
                    return [], RelationUnavailable(
                        "<aggregate>",
                        "aggregate:non-integer-input",
                        MappingProxyType(dict(members[0])),
                    )
                numbers.append(Fraction(value))
            if function == "sum":
                result = Fraction()
                for number in numbers:
                    result += number
                    work.aggregate_exact_operations += 1
                    if too_wide(result):
                        return [], RelationUnavailable(
                            "<aggregate>",
                            "term:exact-value-too-wide",
                            MappingProxyType(dict(members[0])),
                        )
            elif function == "min":
                result = min(numbers)
                work.aggregate_exact_operations += max(0, len(numbers) - 1)
            elif function == "max":
                result = max(numbers)
                work.aggregate_exact_operations += max(0, len(numbers) - 1)
            elif function == "avg":
                result = Fraction()
                for number in numbers:
                    result += number
                    work.aggregate_exact_operations += 1
                    if too_wide(result):
                        return [], RelationUnavailable(
                            "<aggregate>",
                            "term:exact-value-too-wide",
                            MappingProxyType(dict(members[0])),
                        )
                result /= len(numbers)
                work.aggregate_exact_operations += 1
            else:
                return [], RelationUnavailable(
                    "<aggregate>", "aggregate:unknown-function", MappingProxyType(dict(members[0]))
                )
            if isinstance(result, Fraction) and result.denominator == 1:
                result = result.numerator
            if too_wide(result):
                return [], RelationUnavailable(
                    "<aggregate>", "term:exact-value-too-wide", MappingProxyType(dict(members[0]))
                )
        representative = {name: members[0][name] for name in group_names}
        representative[result_name] = result
        collapsed.append(representative)
    return collapsed, None


def _model_uses_exact_derivations(model: Model) -> bool:
    return any(_rule_uses_exact_terms(item.get("derivation_rule")) for item in model.fact_types)


def _requires_fixpoint(model: Model) -> bool:
    if any(
        "clauses" in rule
        for item in model.fact_types
        if isinstance(rule := item.get("derivation_rule"), dict)
    ):
        return True
    dependencies = derivation_dependencies(model.model_dump())
    return any(head in children for head, children in dependencies.items()) or any(
        len(component) > 1 for component in derivation_strata(model.model_dump())
    )


def _evaluate_stratified_extensions(
    model: Model,
    relations: Mapping[str, _TypedRelation],
    *,
    heads: Collection[str] | None = None,
    prior_unavailable: Mapping[str, RelationUnavailable] | None = None,
    prior_possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] | None = None,
    observe_partial: Callable[[str, frozenset[tuple[bytes, ...]], frozenset[tuple[bytes, ...]]], None] | None = None,
    exact: bool = False,
) -> _ExactExtensionResult | _ExtensionResult:
    """Evaluate each SCC to its least finite extension from one relation snapshot.

    A selective evaluation recomputes complete requested SCCs from empty
    computed relations. Previously completed lower strata remain available.
    """
    document = model.model_dump()
    strata = derivation_strata(document)
    selected = None if heads is None else {str(head) for head in heads}
    if selected is not None:
        selected = {
            member for component in strata if selected.intersection(component)
            for member in component
        }
    fact_types = {str(row.get("id")): row for row in model.fact_types}
    state = dict(relations)
    extensions: dict[str, _TypedRelation] = {}
    unavailable: dict[str, RelationUnavailable] = dict(prior_unavailable or {})
    work = _FixpointJoinWork()
    partial = any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in state.values() for row in relation.rows for value in row
    ) or any(
        isinstance(value, _Wildcard)
        for rows in (prior_possible or {}).values() for row in rows for value in row
    )
    possible: dict[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] = {}
    if partial:
        for fact_type_id, relation in tuple(state.items()):
            possible[fact_type_id] = tuple(
                tuple(
                    _symbolic_value(value, primitive, (fact_type_id, index, role))
                    for (role, primitive), value in zip(relation.roles, row, strict=True)
                )
                for index, row in enumerate(relation.rows)
            )
            retained = [
                (row, lineage)
                for row, lineage in zip(relation.rows, relation.row_lineage, strict=True)
                if not any(isinstance(value, dict) and set(value) == {"$opaque"} for value in row)
            ]
            state[fact_type_id] = _TypedRelation(
                fact_type_id, relation.roles,
                tuple(row for row, _ in retained),
                row_lineage=tuple(lineage for _, lineage in retained),
            )
        possible.update(prior_possible or {})
    for component in strata:
        if selected is not None and not selected.intersection(component):
            continue
        for head_id in component:
            fact_type = fact_types[head_id]
            state[head_id] = _TypedRelation(head_id, _relation_roles(model, fact_type), ())
            unavailable.pop(head_id, None)
            if partial:
                possible[head_id] = ()
        facts = dict(_relation_facts(state))
        lineages = {head_id: relation.row_lineage for head_id, relation in state.items()}
        for head_id in component:
            facts[head_id] = []
            lineages[head_id] = []
        delta_facts: dict[str, tuple[Mapping[str, Scalar], ...]] = {
            head_id: () for head_id in component
        }
        delta_lineages: dict[str, tuple[RowLineage, ...]] = {
            head_id: () for head_id in component
        }
        accumulated: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {
            head_id: {} for head_id in component
        }
        iteration = 0
        while True:
            work.fixpoint_iterations += 1
            if partial:
                must_facts = dict(_relation_facts(state))
                may_facts = {
                    fact_type_id: _partial_row_facts(state[fact_type_id].roles, rows)
                    for fact_type_id, rows in possible.items()
                }
                must_lineages = {
                    fact_type_id: relation.row_lineage for fact_type_id, relation in state.items()
                }
                next_must: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {}
                next_may: dict[str, dict[tuple[bytes, ...], tuple[Scalar | _Wildcard, ...]]] = {}
                partial_failure: RelationUnavailable | None = None
                for head_id in component:
                    head = fact_types[head_id]
                    next_must[head_id] = {
                        tuple(_partial_token(value) for value in row): (row, lineage)
                        for row, lineage in zip(state[head_id].rows, state[head_id].row_lineage, strict=True)
                    }
                    next_may[head_id] = {
                        tuple(_partial_token(value) for value in row): row
                        for row in possible[head_id]
                    }
                    for clause in iter_derivation_clauses(head["derivation_rule"]):
                        dependency = next((
                            str(atom.get("fact_type"))
                            for key in ("body", "negate")
                            for atom in clause.get(key) or ()
                            if str(atom.get("fact_type")) in unavailable
                        ), None)
                        if dependency is not None:
                            origin = unavailable[dependency]
                            partial_failure = RelationUnavailable(
                                head_id, origin.reason, origin.binding, dependency
                            )
                            break
                        for definite in (True, False):
                            try:
                                produced = _partial_clause_rows(
                                    model, head, clause, must_facts, may_facts, must_lineages,
                                    work, definite=definite,
                                )
                            except _PartialTermFailure as failure:
                                partial_failure = RelationUnavailable(
                                    head_id, failure.reason, failure.binding
                                )
                                break
                            for row, proof in produced:
                                key = tuple(_partial_token(value) for value in row)
                                if definite:
                                    next_must[head_id].setdefault(key, (row, proof))
                                next_may[head_id].setdefault(key, row)
                        if partial_failure is not None:
                            break
                    if partial_failure is not None:
                        break
                if partial_failure is not None:
                    for head_id in component:
                        unavailable[head_id] = RelationUnavailable(
                            head_id, partial_failure.reason, partial_failure.binding,
                            partial_failure.source_relation,
                        )
                        state.pop(head_id, None)
                        possible.pop(head_id, None)
                    break
                changed = False
                for head_id in component:
                    old_must = {
                        tuple(_partial_token(value) for value in row)
                        for row in state[head_id].rows
                    }
                    old_may = {
                        tuple(_partial_token(value) for value in row)
                        for row in possible[head_id]
                    }
                    changed |= old_must != set(next_must[head_id]) or old_may != set(next_may[head_id])
                    ordered_must = [next_must[head_id][key] for key in sorted(next_must[head_id])]
                    state[head_id] = _TypedRelation(
                        head_id, _relation_roles(model, fact_types[head_id]),
                        tuple(row for row, _ in ordered_must),
                        row_lineage=tuple(proof for _, proof in ordered_must),
                    )
                    possible[head_id] = tuple(next_may[head_id][key] for key in sorted(next_may[head_id]))
                    work.canonical_insertions += len(set(next_must[head_id]) - old_must)
                    work.canonical_insertions += len(set(next_may[head_id]) - old_may)
                    if observe_partial is not None:
                        observe_partial(
                            head_id, frozenset(next_must[head_id]), frozenset(next_may[head_id])
                        )
                if not changed:
                    extensions.update({head_id: state[head_id] for head_id in component})
                    break
                iteration += 1
                continue
            additions: dict[str, dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]]] = {
                head_id: {} for head_id in component
            }
            failure: RelationUnavailable | None = None
            for head_id in component:
                fact_type = fact_types[head_id]
                derivation = str(fact_type.get("derivation"))
                for clause in iter_derivation_clauses(fact_type["derivation_rule"]):
                    dependency = next((
                        str(atom.get("fact_type"))
                        for key in ("body", "negate")
                        for atom in clause.get(key) or ()
                        if str(atom.get("fact_type")) in unavailable
                    ), None)
                    if dependency is not None:
                        origin = unavailable[dependency]
                        failure = RelationUnavailable(head_id, origin.reason, origin.binding, dependency)
                        record_branch(f"derivation:extension:{derivation}:exact-origin-propagated")
                        break
                    recursive_atoms = [
                        str(atom.get("fact_type")) for atom in clause.get("body") or ()
                        if str(atom.get("fact_type")) in component
                    ]
                    if (iteration == 0 and recursive_atoms) or (iteration > 0 and not recursive_atoms):
                        continue
                    # One recursive atom reads only the preceding delta. A
                    # multi-recursive body retains the full snapshot until its
                    # atom-specific delta variants are needed.
                    if len(recursive_atoms) == 1:
                        recursive_id = recursive_atoms[0]
                        fact_view = {**facts, recursive_id: delta_facts[recursive_id]}
                        lineage_view = {
                            **lineages, recursive_id: delta_lineages[recursive_id]
                        }
                    else:
                        fact_view = facts
                        lineage_view = lineages
                    bindings = _clause_bindings(clause, fact_view, work)
                    aggregate = isinstance(clause.get("aggregate"), dict)
                    if aggregate:
                        analysis = analyze_declared_aggregate(model, clause)
                        bindings, aggregate_failure = _aggregate_bindings(
                            clause, bindings, work, analysis
                        )
                        if aggregate_failure is not None:
                            failure = RelationUnavailable(
                                head_id, aggregate_failure.reason, aggregate_failure.binding
                            )
                            record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-origin")
                            break
                        if not bindings:
                            record_branch(f"derivation:extension:{derivation}:aggregate-group-absent")
                    filtered = []
                    for binding in bindings:
                        keep = True
                        for comparison in clause.get("where") or ():
                            result = compare_terms(
                                str(comparison.get("operator")), comparison.get("left"),
                                comparison.get("right"), binding, bound_cross_product=aggregate,
                            )
                            _count_term_work(work, result)
                            if not result.available:
                                failure = RelationUnavailable(
                                    head_id, str(result.reason), MappingProxyType(dict(binding))
                                )
                                break
                            if result.value is not True:
                                record_branch(f"derivation:extension:{derivation}:exact-where-false")
                                keep = False
                                break
                        if failure is not None:
                            break
                        if keep:
                            filtered.append(binding)
                    if failure is not None:
                        break
                    proofs = (
                        tuple(() for _ in filtered) if aggregate
                        else _binding_lineages(clause, filtered, fact_view, lineage_view)
                    )
                    role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
                    for binding, proof in zip(filtered, proofs, strict=True):
                        row = []
                        for role_name in role_names:
                            result = evaluate_term(clause["head"][role_name], binding)
                            _count_term_work(work, result)
                            if not result.available:
                                failure = RelationUnavailable(
                                    head_id, str(result.reason), MappingProxyType(dict(binding))
                                )
                                break
                            try:
                                row.append(materialize_scalar(result.value))
                            except ValueError:
                                failure = RelationUnavailable(
                                    head_id, "term:head-non-integral", MappingProxyType(dict(binding))
                                )
                                break
                            work.head_cells_projected += 1
                        if failure is not None:
                            break
                        typed_row = tuple(row)
                        _witness_row(fact_type, clause, binding, typed_row)
                        key = tuple(_identity_token(value) for value in typed_row)
                        if key not in accumulated[head_id]:
                            additions[head_id].setdefault(key, (typed_row, proof))
                    if failure is not None:
                        break
                    if aggregate:
                        record_branch(f"derivation:extension:{derivation}:aggregate-applied")
                if failure is not None:
                    break
            if failure is not None:
                for head_id in component:
                    unavailable[head_id] = RelationUnavailable(
                        head_id, failure.reason, failure.binding, failure.source_relation
                    )
                    state.pop(head_id, None)
                break
            changed = False
            next_delta: dict[str, list[Mapping[str, Scalar]]] = {
                head_id: [] for head_id in component
            }
            next_lineages: dict[str, list[RowLineage]] = {
                head_id: [] for head_id in component
            }
            for head_id in component:
                role_names = [str(role.get("role_name")) for role in fact_types[head_id].get("roles") or []]
                for key, row in sorted(additions[head_id].items()):
                    if key not in accumulated[head_id]:
                        accumulated[head_id][key] = row
                        work.canonical_insertions += 1
                        changed = True
                        values, proof = row
                        next_delta[head_id].append(MappingProxyType(dict(zip(role_names, values, strict=True))))
                        next_lineages[head_id].append(proof)
                facts[head_id].extend(next_delta[head_id])
                lineages[head_id].extend(next_lineages[head_id])
            if not changed:
                for head_id in component:
                    rows = [accumulated[head_id][key] for key in sorted(accumulated[head_id])]
                    state[head_id] = _TypedRelation(
                        head_id, _relation_roles(model, fact_types[head_id]),
                        tuple(row for row, _lineage in rows),
                        row_lineage=tuple(lineage for _row, lineage in rows),
                    )
                extensions.update({head_id: state[head_id] for head_id in component})
                break
            delta_facts = {head_id: tuple(rows) for head_id, rows in next_delta.items()}
            delta_lineages = {head_id: tuple(rows) for head_id, rows in next_lineages.items()}
            iteration += 1
    if partial:
        return _ExactExtensionResult(
            _PartialExtensions(
                extensions, unavailable=unavailable,
                possible={head: possible[head] for head in extensions},
            ),
            work,
        ) if exact else _ExtensionResult(
            _PartialExtensions(
                extensions, possible={head: possible[head] for head in extensions},
            ),
            work,
        )
    if exact:
        return _ExactExtensionResult(_ExactExtensions(extensions, unavailable=unavailable), work)
    return _ExtensionResult(MappingProxyType(extensions), work)


def _exact_extension_calculator(
    model: Model,
    relations: Mapping[str, _TypedRelation],
    *,
    heads: Collection[str] | None = None,
    prior_unavailable: Mapping[str, RelationUnavailable] | None = None,
) -> _ExactExtensionResult:
    """Evaluate term-bearing derivations without changing the pinned calculator."""
    if _requires_fixpoint(model) or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for relation in relations.values() for row in relation.rows for value in row
    ):
        return _evaluate_stratified_extensions(
            model, relations, heads=heads, prior_unavailable=prior_unavailable, exact=True
        )
    facts = dict(_relation_facts(relations))
    fact_lineages = {
        fact_type_id: relation.row_lineage for fact_type_id, relation in relations.items()
    }
    extensions: dict[str, _TypedRelation] = {}
    unavailable: dict[str, RelationUnavailable] = dict(prior_unavailable or {})
    work = _ExactJoinWork()
    fact_types = {str(fact_type.get("id")): fact_type for fact_type in model.fact_types}
    selected = None if heads is None else frozenset(str(head) for head in heads)
    if selected is not None:
        for head in selected:
            unavailable.pop(head, None)
    for component in derivation_strata(model.model_dump()):
        fact_type_id = component[0]
        if selected is not None and fact_type_id not in selected:
            continue
        fact_type = fact_types[fact_type_id]
        rule = fact_type["derivation_rule"]
        derivation = str(fact_type.get("derivation"))
        uses_exact = _rule_uses_exact_terms(rule)
        uses_aggregate = isinstance(rule.get("aggregate"), dict)
        if uses_exact:
            record_branch(f"derivation:extension:{derivation}:exact-applied")
        dependency = next(
            (
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or ()
                if str(atom.get("fact_type")) in unavailable
            ),
            None,
        )
        if dependency is not None:
            origin = unavailable[dependency]
            unavailable[fact_type_id] = RelationUnavailable(
                fact_type_id,
                origin.reason,
                origin.binding,
                dependency,
            )
            if uses_exact or dependency in unavailable:
                record_branch(f"derivation:extension:{derivation}:exact-origin-propagated")
            if uses_aggregate:
                record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-propagated")
            continue
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        aggregate_analysis = analyze_declared_aggregate(model, rule) if uses_aggregate else None
        bindings, aggregate_failure = _aggregate_bindings(rule, bindings, work, aggregate_analysis)
        if aggregate_failure is not None:
            unavailable[fact_type_id] = RelationUnavailable(
                fact_type_id,
                aggregate_failure.reason,
                aggregate_failure.binding,
            )
            if uses_aggregate:
                record_branch(f"derivation:extension:{derivation}:aggregate-unavailable-origin")
            continue
        if uses_aggregate and not bindings:
            record_branch(f"derivation:extension:{derivation}:aggregate-group-absent")
        filtered: list[dict[str, Scalar]] = []
        failed: RelationUnavailable | None = None
        for binding in bindings:
            keep = True
            for comparison in rule.get("where") or ():
                result = compare_terms(
                    str(comparison.get("operator")),
                    comparison.get("left"),
                    comparison.get("right"),
                    binding,
                    bound_cross_product=uses_aggregate,
                )
                _count_term_work(work, result)
                if not result.available:
                    failed = RelationUnavailable(
                        fact_type_id,
                        str(result.reason),
                        MappingProxyType(dict(binding)),
                    )
                    break
                if result.value is not True:
                    if uses_exact:
                        record_branch(f"derivation:extension:{derivation}:exact-where-false")
                    if uses_aggregate:
                        record_branch(
                            f"derivation:extension:{derivation}:aggregate-post-filter-false"
                        )
                    keep = False
                    break
            if failed is not None:
                break
            if keep:
                filtered.append(binding)
        if failed is not None:
            unavailable[fact_type_id] = failed
            continue

        binding_lineages = (
            tuple(() for _ in filtered)
            if isinstance(rule.get("aggregate"), dict)
            else _binding_lineages(rule, filtered, fact_view, fact_lineages)
        )
        head = rule["head"]
        role_names = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
        unique_rows: dict[tuple[bytes, ...], tuple[tuple[Scalar, ...], RowLineage]] = {}
        for binding, lineage in zip(filtered, binding_lineages, strict=True):
            row: list[Scalar] = []
            for role_name in role_names:
                result = evaluate_term(head[role_name], binding)
                _count_term_work(work, result)
                if not result.available:
                    failed = RelationUnavailable(
                        fact_type_id,
                        str(result.reason),
                        MappingProxyType(dict(binding)),
                    )
                    break
                try:
                    value = materialize_scalar(result.value)
                except ValueError:
                    failed = RelationUnavailable(
                        fact_type_id,
                        "term:head-non-integral",
                        MappingProxyType(dict(binding)),
                    )
                    break
                row.append(value)
                work.head_cells_projected += 1
            if failed is not None:
                break
            typed_row = tuple(row)
            key = tuple(_identity_token(value) for value in typed_row)
            unique_rows.setdefault(key, (typed_row, lineage))
            if uses_exact:
                record_branch(f"derivation:extension:{derivation}:exact-head-computed")
        if failed is not None:
            unavailable[fact_type_id] = failed
            continue
        ordered = [unique_rows[key] for key in sorted(unique_rows)]
        relation = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            tuple(item[0] for item in ordered),
            row_lineage=tuple(item[1] for item in ordered),
        )
        facts[fact_type_id] = _relation_facts({fact_type_id: relation})[fact_type_id]
        if uses_aggregate:
            record_branch(f"derivation:extension:{derivation}:aggregate-applied")
        fact_lineages[fact_type_id] = relation.row_lineage
        extensions[fact_type_id] = relation
    return _ExactExtensionResult(
        _ExactExtensions(extensions, unavailable=unavailable),
        work,
    )


def exact_extension_envelope(model: Model, population: Population) -> dict[str, Any]:
    """Canonical parity envelope for exact relations and unavailability."""
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    calculated = _exact_extension_calculator(model, _base_relations(model, population))
    heads = [
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]
    relations: dict[str, list[list[str]]] = {}
    unavailable: dict[str, dict[str, Any]] = {}
    for head in heads:
        failure = calculated.extensions.unavailable.get(head)
        if failure is not None:
            unavailable[head] = {
                "reason": failure.reason,
                "binding": {
                    "$" + variable: _aggregate_identity_token(value).decode("utf-8")
                    for variable, value in sorted(failure.binding.items())
                },
                "source_relation": failure.source_relation,
            }
            continue
        relation = calculated.extensions.get(head)
        relations[head] = (
            sorted(
                [[_identity_token(value).decode("utf-8") for value in row] for row in relation.rows]
            )
            if relation is not None
            else []
        )
    return {"relations": relations, "unavailable": unavailable}


@dataclass(frozen=True, slots=True)
class DynamicRefreshWork:
    fixpoint_iterations: int = 0
    canonical_insertions: int = 0
    selected_heads: int = 0
    strata_evaluated: int = 0
    body_atoms_evaluated: int = 0
    projected_rows: int = 0
    atom_role_terms_read: int = 0
    positive_candidate_rows_emitted: int = 0
    join_candidates_indexed: int = 0
    join_left_bindings_probed: int = 0
    join_matches_merged: int = 0
    component_product_rows_emitted: int = 0
    negation_rows_indexed: int = 0
    negation_bindings_probed: int = 0
    head_cells_projected: int = 0
    term_nodes_visited: int = 0
    term_operations: int = 0
    max_exact_value_bits: int = 0
    aggregate_candidate_bindings: int = 0
    aggregate_contribution_terms: int = 0
    aggregate_identity_tokens: int = 0
    aggregate_distinct_contributions: int = 0
    aggregate_group_lookups: int = 0
    aggregate_groups: int = 0
    aggregate_exact_operations: int = 0
    aggregate_maximum_value_bits: int = 0


@dataclass(frozen=True, slots=True)
class StructuredExtensionView:
    facts: Mapping[str, tuple[Mapping[str, Scalar], ...]]
    recomputed: tuple[str, ...]
    work: DynamicRefreshWork
    unavailable: Mapping[str, RelationUnavailable] = field(
        default_factory=lambda: MappingProxyType({})
    )
    possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] = field(
        default_factory=lambda: MappingProxyType({})
    )


def _public_refresh_work(
    work: _JoinWork,
    *,
    selected_heads: int,
    strata_evaluated: int,
    body_atoms_evaluated: int,
    projected_rows: int,
) -> DynamicRefreshWork:
    return DynamicRefreshWork(
        fixpoint_iterations=int(getattr(work, "fixpoint_iterations", 0)),
        canonical_insertions=int(getattr(work, "canonical_insertions", 0)),
        selected_heads=selected_heads,
        strata_evaluated=strata_evaluated,
        body_atoms_evaluated=body_atoms_evaluated,
        projected_rows=projected_rows,
        atom_role_terms_read=work.atom_role_terms_read,
        positive_candidate_rows_emitted=work.positive_candidate_rows_emitted,
        join_candidates_indexed=work.join_candidates_indexed,
        join_left_bindings_probed=work.join_left_bindings_probed,
        join_matches_merged=work.join_matches_merged,
        component_product_rows_emitted=work.component_product_rows_emitted,
        negation_rows_indexed=work.negation_rows_indexed,
        negation_bindings_probed=work.negation_bindings_probed,
        head_cells_projected=work.head_cells_projected,
        term_nodes_visited=int(getattr(work, "term_nodes_visited", 0)),
        term_operations=int(getattr(work, "term_operations", 0)),
        max_exact_value_bits=int(getattr(work, "max_exact_value_bits", 0)),
        aggregate_candidate_bindings=int(getattr(work, "aggregate_candidate_bindings", 0)),
        aggregate_contribution_terms=int(getattr(work, "aggregate_contribution_terms", 0)),
        aggregate_identity_tokens=int(getattr(work, "aggregate_identity_tokens", 0)),
        aggregate_distinct_contributions=int(getattr(work, "aggregate_distinct_contributions", 0)),
        aggregate_group_lookups=int(getattr(work, "aggregate_group_lookups", 0)),
        aggregate_groups=int(getattr(work, "aggregate_groups", 0)),
        aggregate_exact_operations=int(getattr(work, "aggregate_exact_operations", 0)),
        aggregate_maximum_value_bits=int(getattr(work, "aggregate_maximum_value_bits", 0)),
    )


def _extension_fact_map(
    extensions: Mapping[str, _TypedRelation],
) -> Mapping[str, tuple[Mapping[str, Scalar], ...]]:
    return MappingProxyType(
        {fact_type_id: tuple(rows) for fact_type_id, rows in _relation_facts(extensions).items()}
    )


def structured_extension_view(
    model: Model,
    population: Population,
    *,
    previous: Mapping[str, tuple[Mapping[str, Scalar], ...]] | None = None,
    previous_unavailable: Mapping[str, RelationUnavailable] | None = None,
    previous_possible: Mapping[str, tuple[tuple[Scalar | _Wildcard, ...], ...]] | None = None,
    refresh: Collection[str] | None = None,
) -> StructuredExtensionView:
    """Compute all structured rows or selectively refresh named strata.

    Selective evaluation starts from asserted relations plus the prior complete
    extension map. Requested heads are replaced in dependency order; every
    unrequested structured relation remains byte-for-byte equivalent to the
    supplied prior view.
    """
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    classifications = {row.fact_type: row for row in derivation_classifications(model.model_dump())}
    strata = derivation_strata(model.model_dump())
    ordered = tuple(head for component in strata for head in component)
    if any(row.stability == "dynamic" for row in classifications.values()):
        record_branch("composition:derivation-view:dynamic:applied")

    if _requires_fixpoint(model) or previous_possible or any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for rows in population.facts.values() for row in rows for value in row.values()
    ):
        exact = _model_uses_exact_derivations(model)
        requested = set(ordered) if refresh is None else {str(head) for head in refresh}
        unknown = requested - set(ordered)
        if unknown:
            raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
        incomplete = sorted(head for head in requested if not classifications[head].complete)
        if incomplete:
            raise ValueError(f"incomplete structured refresh head(s): {incomplete}")
        if refresh is not None and previous is None:
            raise ValueError("selective structured refresh requires a previous complete view")
        missing_prior_heads = set(ordered) - set(previous or {}) - set(previous_unavailable or {})
        if refresh is not None and missing_prior_heads:
            raise ValueError(
                "selective structured refresh received an incomplete prior envelope; "
                f"missing structured head(s): {sorted(missing_prior_heads)}"
            )
        selected = {
            head for component in strata if requested.intersection(component) for head in component
        }
        if refresh is not None and not selected:
            return StructuredExtensionView(
                facts=MappingProxyType(dict(previous or {})), recomputed=(),
                work=DynamicRefreshWork(),
                unavailable=MappingProxyType(dict(previous_unavailable or {})),
                possible=MappingProxyType(dict(previous_possible or {})),
            )
        relations = dict(_base_relations(model, population))
        fact_types = {str(row.get("id")): row for row in model.fact_types}
        for head, rows in (previous or {}).items():
            if head in fact_types and head in ordered:
                roles = _relation_roles(model, fact_types[head])
                relations[head] = _TypedRelation(
                    head, roles, _rows_from_facts(roles, rows),
                    row_lineage=tuple(() for _row in rows),
                )
        calculated = _evaluate_stratified_extensions(
            model, relations, heads=selected if refresh is not None else None,
            prior_unavailable=previous_unavailable, prior_possible=previous_possible,
            exact=exact,
        )
        facts = dict(previous or {})
        computed = _extension_fact_map(calculated.extensions)
        for head in selected:
            if head in computed:
                facts[head] = computed[head]
            else:
                facts.pop(head, None)
        possible = dict(previous_possible or {})
        for head in selected:
            possible.pop(head, None)
        possible.update(getattr(calculated.extensions, "possible", {}))
        return StructuredExtensionView(
            facts=MappingProxyType(facts),
            recomputed=tuple(head for head in ordered if head in selected),
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(selected), strata_evaluated=len(selected),
                body_atoms_evaluated=sum(
                    len(clause.get("body") or []) + len(clause.get("negate") or [])
                    for head in selected
                    for clause in iter_derivation_clauses(fact_types[head]["derivation_rule"])
                ),
                projected_rows=sum(len(computed.get(head, ())) for head in selected),
            ),
            unavailable=getattr(calculated.extensions, "unavailable", MappingProxyType({})),
            possible=MappingProxyType(possible),
        )

    if refresh is None:
        calculated = (
            _exact_extension_calculator(model, _base_relations(model, population))
            if _model_uses_exact_derivations(model)
            else _python_extension_calculator(model, _base_relations(model, population))
        )
        facts = _extension_fact_map(calculated.extensions)
        return StructuredExtensionView(
            facts=facts,
            recomputed=ordered,
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(ordered),
                strata_evaluated=len(ordered),
                body_atoms_evaluated=sum(
                    len((fact_type.get("derivation_rule") or {}).get("body") or [])
                    + len((fact_type.get("derivation_rule") or {}).get("negate") or [])
                    for fact_type in model.fact_types
                    if str(fact_type.get("id")) in classifications
                ),
                projected_rows=sum(len(rows) for rows in facts.values()),
            ),
            unavailable=getattr(calculated.extensions, "unavailable", MappingProxyType({})),
        )

    if _model_uses_exact_derivations(model):
        requested = frozenset(str(head) for head in refresh)
        unknown = requested - set(classifications)
        if unknown:
            raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
        incomplete = [head for head in requested if not classifications[head].complete]
        if incomplete:
            raise ValueError(f"incomplete structured refresh head(s): {sorted(incomplete)}")
        if previous is None:
            raise ValueError("selective structured refresh requires a previous complete view")
        missing_prior_heads = set(ordered) - set(previous)
        if missing_prior_heads and previous_unavailable is None:
            raise ValueError(
                "selective exact refresh requires previous_unavailable when the prior "
                f"fact view omits structured head(s): {sorted(missing_prior_heads)}"
            )
        incomplete_prior_heads = missing_prior_heads - set(previous_unavailable or {})
        if incomplete_prior_heads:
            raise ValueError(
                "selective exact refresh received an incomplete prior envelope; "
                f"missing structured head(s): {sorted(incomplete_prior_heads)}"
            )
        if not requested:
            return StructuredExtensionView(
                facts=MappingProxyType(dict(previous)),
                recomputed=(),
                work=DynamicRefreshWork(),
                unavailable=MappingProxyType(dict(previous_unavailable or {})),
            )
        fact_types = {str(row.get("id")): row for row in model.fact_types}
        relations = dict(_base_relations(model, population))
        for head in ordered:
            if head not in previous:
                continue
            fact_type = fact_types[head]
            roles = _relation_roles(model, fact_type)
            relations[head] = _TypedRelation(
                head,
                roles,
                _rows_from_facts(roles, previous[head]),
            )
        calculated = _exact_extension_calculator(
            model,
            relations,
            heads=requested,
            prior_unavailable=previous_unavailable,
        )
        current = dict(previous or {})
        exact_facts = _extension_fact_map(calculated.extensions)
        for head in requested:
            if head in exact_facts:
                current[head] = exact_facts[head]
            else:
                current.pop(head, None)
        return StructuredExtensionView(
            facts=MappingProxyType(current),
            recomputed=tuple(head for head in ordered if head in requested),
            work=_public_refresh_work(
                calculated.counted_operations,
                selected_heads=len(requested),
                strata_evaluated=len(requested),
                body_atoms_evaluated=sum(
                    len((fact_type.get("derivation_rule") or {}).get("body") or [])
                    + len((fact_type.get("derivation_rule") or {}).get("negate") or [])
                    for fact_type in model.fact_types
                    if str(fact_type.get("id")) in requested
                ),
                projected_rows=sum(len(exact_facts.get(head, ())) for head in requested),
            ),
            unavailable=calculated.extensions.unavailable,
        )

    requested = frozenset(str(head) for head in refresh)
    unknown = requested - set(classifications)
    if unknown:
        raise ValueError(f"unknown structured refresh head(s): {sorted(unknown)}")
    incomplete = [head for head in requested if not classifications[head].complete]
    if incomplete:
        raise ValueError(f"incomplete structured refresh head(s): {sorted(incomplete)}")
    if previous is None:
        raise ValueError("selective structured refresh requires a previous complete view")
    missing_previous = set(classifications) - set(previous)
    if missing_previous:
        raise ValueError(f"previous structured view omits head(s): {sorted(missing_previous)}")
    if not requested:
        return StructuredExtensionView(
            facts=MappingProxyType(
                {head: tuple(rows) for head, rows in previous.items() if head in classifications}
            ),
            recomputed=(),
            work=DynamicRefreshWork(),
        )

    fact_types = {str(row.get("id")): row for row in model.fact_types}
    relations = dict(_base_relations(model, population))
    for head in ordered:
        fact_type = fact_types[head]
        roles = _relation_roles(model, fact_type)
        relations[head] = _TypedRelation(
            head,
            roles,
            _rows_from_facts(roles, previous[head]),
        )
    facts = dict(_relation_facts(relations))
    work = _JoinWork()
    recomputed: list[str] = []
    body_atoms_evaluated = 0
    projected_rows = 0
    for head in ordered:
        if head not in requested:
            continue
        fact_type = fact_types[head]
        rule = fact_type["derivation_rule"]
        fact_view = MappingProxyType(facts)
        bindings = _clause_bindings(rule, fact_view, work)
        rows = _project_extension(fact_type, bindings, work)
        relation = _TypedRelation(head, _relation_roles(model, fact_type), rows)
        relations[head] = relation
        facts[head] = _relation_facts({head: relation})[head]
        recomputed.append(head)
        body_atoms_evaluated += len(rule.get("body") or []) + len(rule.get("negate") or [])
        projected_rows += len(rows)

    extension_relations = MappingProxyType({head: relations[head] for head in ordered})
    return StructuredExtensionView(
        facts=_extension_fact_map(extension_relations),
        recomputed=tuple(recomputed),
        work=_public_refresh_work(
            work,
            selected_heads=len(requested),
            strata_evaluated=len(recomputed),
            body_atoms_evaluated=body_atoms_evaluated,
            projected_rows=projected_rows,
        ),
    )


def derivation_claims_against(
    model: Model,
    claimed: Population,
    computed_from: Population,
) -> list[DerivationVerdict]:
    """Compare one population's claims with another population's extension."""
    if not claimed.matches_validation_marker(model):
        raise UnvalidatedPopulationError(claimed, model)
    if not computed_from.matches_validation_marker(model):
        raise UnvalidatedPopulationError(computed_from, model)
    calculated = (
        _exact_extension_calculator(model, _base_relations(model, computed_from))
        if _model_uses_exact_derivations(model)
        else _python_extension_calculator(model, _base_relations(model, computed_from))
    )
    return [
        _exact_derivation_obligation(
            fact_type,
            claimed,
            calculated.extensions.get(str(fact_type.get("id"))),
            getattr(calculated.extensions, "unavailable", {}).get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]


def _rows_by_identity(relation: _TypedRelation) -> dict[tuple[bytes, ...], tuple[Scalar, ...]]:
    return {tuple(_identity_token(value) for value in row): row for row in relation.rows}


def _witness(
    relation: _TypedRelation,
    row: Sequence[Scalar],
) -> dict[str, Scalar]:
    return {
        role_name: value for (role_name, _primitive), value in zip(relation.roles, row, strict=True)
    }


def _derivation_obligation(
    fact_type: dict[str, Any],
    population: Population,
    computed: _TypedRelation | None,
    possible: tuple[tuple[Scalar | _Wildcard, ...], ...] | None = None,
) -> DerivationVerdict:
    import json

    fact_type_id = str(fact_type.get("id"))
    derivation = str(fact_type.get("derivation"))
    common: dict[str, Any] = {
        "derivation_ref": derivation_address(fact_type_id),
        "fact_type": fact_type_id,
        "derivation": derivation,
    }
    if fact_type_id not in population.covers:
        return DerivationVerdict(
            **common,
            verdict="unchecked",
            message=f"No derivation claim was made for '{fact_type_id}'.",
            reason_code=DERIVATION_REASON_CODES[0],
            scope_id=f"derivation:extension:{derivation}:unchecked-not-covered",
        )
    if computed is None:
        return DerivationVerdict(
            **common,
            verdict="unchecked",
            message=f"The derivation rule for '{fact_type_id}' is opaque.",
            reason_code=DERIVATION_REASON_CODES[1],
            scope_id=f"derivation:extension:{derivation}:unchecked-rule-opaque",
        )

    claimed = _TypedRelation(
        fact_type_id,
        computed.roles,
        _rows_from_facts(computed.roles, population.facts.get(fact_type_id, ())),
    )
    computed_rows = _rows_by_identity(computed)
    opaque_claims = [row for row in claimed.rows if any(isinstance(v, dict) for v in row)]
    claim_patterns = [
        tuple(_symbolic_value(value, primitive, (fact_type_id, index, role))
              for (role, primitive), value in zip(claimed.roles, row, strict=True))
        for index, row in enumerate(opaque_claims)
    ]
    concrete_claimed = _TypedRelation(
        fact_type_id, claimed.roles,
        tuple(row for row in claimed.rows if not any(isinstance(v, dict) for v in row)),
    )
    claimed_rows = _rows_by_identity(concrete_claimed)
    missing = sorted(
        key for key in set(computed_rows) - set(claimed_rows)
        if not any(all(_partial_compatible(a, b) for a, b in zip(
            computed_rows[key], pattern, strict=True)) for pattern in claim_patterns)
    )
    surplus = sorted(
        key for key in set(claimed_rows) - set(computed_rows)
        if possible is None or not any(
            all(_partial_compatible(left, right) for left, right in zip(claimed_rows[key], pattern, strict=True))
            for pattern in possible
        )
    )
    unresolved = sorted(
        key for key in set(claimed_rows) - set(computed_rows)
        if possible is not None and any(
            all(_partial_compatible(left, right) for left, right in zip(claimed_rows[key], pattern, strict=True))
            for pattern in possible
        )
    )
    findings: list[DerivationFinding] = []
    if missing:
        record_branch(f"derivation:finding:{derivation}:incomplete")
        witness = _witness(computed, computed_rows[missing[0]])
        rendered = json.dumps(witness, ensure_ascii=False, separators=(",", ":"))
        findings.append(
            DerivationFinding(
                kind="derived-extension-incomplete",
                message=verbalize.derivation_incomplete_message(fact_type_id, rendered),
                witness=witness,
            )
        )
    if surplus and derivation == "derived":
        record_branch("derivation:finding:derived:unsound")
        witness = _witness(claimed, claimed_rows[surplus[0]])
        rendered = json.dumps(witness, ensure_ascii=False, separators=(",", ":"))
        findings.append(
            DerivationFinding(
                kind="derived-extension-unsound",
                message=verbalize.derivation_unsound_message(fact_type_id, rendered),
                witness=witness,
            )
        )
    if unresolved or opaque_claims:
        record_branch(f"derivation:finding:{derivation}:unresolved")
        witness = (_witness(claimed, claimed_rows[unresolved[0]]) if unresolved
                   else {role: None if isinstance(value, dict) else value
                         for (role, _primitive), value in zip(
                             claimed.roles, opaque_claims[0], strict=True)})
        findings.append(
            DerivationFinding(
                kind="derived-extension-unresolved",
                message=f"The claimed row in '{fact_type_id}' may follow from the derivation: "
                        + json.dumps(witness, ensure_ascii=False, separators=(",", ":")),
                witness=witness,
            )
        )
    if findings:
        if all(finding.kind == "derived-extension-unresolved" for finding in findings):
            return DerivationVerdict(
                **common,
                verdict="unchecked",
                message=f"The derivation claim for '{fact_type_id}' has unresolved membership.",
                findings=findings,
                reason_code="derived-unknown",
                scope_id=f"derivation:extension:{derivation}:unchecked-derived-unknown",
            )
        return DerivationVerdict(
            **common,
            verdict="fail",
            message=f"The derivation claim for '{fact_type_id}' differs from its extension.",
            findings=findings,
            scope_id=f"derivation:extension:{derivation}:violated:alethic",
        )
    return DerivationVerdict(
        **common,
        verdict="pass",
        message=f"The derivation claim for '{fact_type_id}' matches its extension.",
        scope_id=f"derivation:extension:{derivation}:clean",
    )


def evaluate_derivations_legacy(
    model: Model,
    population: Population,
    *,
    calculator: ExtensionCalculator = _python_extension_calculator,
) -> tuple[Mapping[str, _TypedRelation], list[DerivationVerdict]]:
    structured = [
        fact_type
        for fact_type in model.fact_types
        if isinstance(fact_type.get("derivation_rule"), dict)
    ]
    if not structured:
        return MappingProxyType({}), []
    calculated = calculator(model, _base_relations(model, population))
    obligations = [
        _derivation_obligation(
            fact_type,
            population,
            calculated.extensions.get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]
    return calculated.extensions, obligations


def constraint_view_legacy(
    model: Model,
    population: Population,
    extensions: Mapping[str, _TypedRelation],
) -> _RuledFactView:
    facts: dict[str, tuple[Mapping[str, Scalar], ...]] = {}
    lineages: dict[str, tuple[RowLineage, ...]] = {}
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        rule = fact_type.get("derivation_rule")
        if not isinstance(rule, dict):
            selected = population.facts.get(fact_type_id, ())
            selected_lineage = tuple(
                (("facts", fact_type_id, index),) for index, _row in enumerate(selected)
            )
        elif fact_type.get("derivation") == "semiderived":
            selected = _relation_facts({fact_type_id: extensions[fact_type_id]})[fact_type_id]
            selected_lineage = extensions[fact_type_id].row_lineage
        elif fact_type_id in population.covers:
            selected = population.facts.get(fact_type_id, ())
            selected_lineage = tuple(
                (("facts", fact_type_id, index),) for index, _row in enumerate(selected)
            )
        else:
            selected = ()
            selected_lineage = ()
        facts[fact_type_id] = tuple(MappingProxyType(dict(row)) for row in selected)
        lineages[fact_type_id] = selected_lineage
    instances = MappingProxyType(
        {object_type: tuple(values) for object_type, values in population.instances.items()}
    )
    return _RuledFactView(
        tuple(population.covers),
        instances,
        MappingProxyType(facts),
        MappingProxyType(lineages),
    )


_PHASE3_LEGACY_EVALUATE_DERIVATIONS = evaluate_derivations_legacy


_PHASE3_LEGACY_CONSTRAINT_VIEW = constraint_view_legacy


def _exact_derivation_obligation(
    fact_type: dict[str, Any],
    population: Population,
    computed: _TypedRelation | None,
    unavailable: RelationUnavailable | None,
) -> DerivationVerdict:
    fact_type_id = str(fact_type.get("id"))
    if unavailable is None or fact_type_id not in population.covers:
        return _derivation_obligation(fact_type, population, computed)
    derivation = str(fact_type.get("derivation"))
    event = {
        "term:mod-zero": "unchecked-mod-zero",
        "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
        "term:dependency-unavailable": "unchecked-dependency-unavailable",
        "term:div-zero": "unchecked-div-zero",
        "term:sqrt-negative": "unchecked-sqrt-negative",
        "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
        "term:float-overflow": "unchecked-float-overflow",
    }.get(unavailable.reason, "unchecked-dependency-unavailable")
    reason = unavailable.reason
    if reason not in EXACT_DERIVATION_REASON_CODES:
        reason = "term:dependency-unavailable"
    return DerivationVerdict(
        derivation_ref=derivation_address(fact_type_id),
        fact_type=fact_type_id,
        derivation=derivation,
        verdict="unchecked",
        message=(
            f"The derivation for '{fact_type_id}' is unavailable: {unavailable.reason}; "
            f"binding={dict(unavailable.binding)!r}."
        ),
        reason_code=reason,
        scope_id=f"derivation:extension:{derivation}:{event}",
    )


def _evaluate_derivations_dispatch(
    model: Model,
    population: Population,
    *,
    calculator: ExtensionCalculator = _python_extension_calculator,
) -> tuple[Mapping[str, _TypedRelation], list[DerivationVerdict]]:
    opaque_sources = {
        fact_type_id
        for fact_type_id, rows in population.facts.items()
        if any(
            isinstance(value, dict) and set(value) == {"$opaque"}
            for row in rows for value in row.values()
        )
    }
    if opaque_sources and _PARTIAL_OPAQUE.get():
        calculated = (
            _exact_extension_calculator(model, _base_relations(model, population))
            if _model_uses_exact_derivations(model)
            else _python_extension_calculator(model, _base_relations(model, population))
        )
        possible = getattr(calculated.extensions, "possible", {})
        unavailable = getattr(calculated.extensions, "unavailable", {})
        obligations = []
        for fact_type in model.fact_types:
            if fact_type.get("derivation") not in ("derived", "semiderived") or fact_type.get("derivation_rule") is None:
                continue
            head = str(fact_type.get("id"))
            if head in unavailable:
                obligations.append(_exact_derivation_obligation(
                    fact_type, population, calculated.extensions.get(head), unavailable[head]
                ))
            else:
                obligations.append(_derivation_obligation(
                    fact_type, population, calculated.extensions.get(head), possible.get(head, ())
                ))
        return calculated.extensions, obligations
    if opaque_sources:
        dependencies = derivation_dependencies(model.model_dump())
        affected = set(opaque_sources)
        while True:
            new = {
                head for head, sources in dependencies.items()
                if sources & affected
            } - affected
            if not new:
                break
            affected.update(new)
        safe_facts = {
            fact_type_id: [
                row for row in rows
                if not any(
                    isinstance(value, dict) and set(value) == {"$opaque"}
                    for value in row.values()
                )
            ]
            for fact_type_id, rows in population.facts.items()
        }
        safe_population = population.model_copy(update={"facts": safe_facts})
        safe_extensions, safe_verdicts = _evaluate_derivations_dispatch(
            model, safe_population, calculator=calculator,
        )
        verdicts: list[DerivationVerdict] = []
        for verdict in safe_verdicts:
            if verdict.fact_type not in affected:
                verdicts.append(verdict)
                continue
            verdicts.append(DerivationVerdict(
                derivation_ref=verdict.derivation_ref,
                fact_type=verdict.fact_type,
                derivation=verdict.derivation,
                verdict="unchecked",
                message=f"The derivation for '{verdict.fact_type}' read an opaque role.",
                reason_code="opaque-value",
                scope_id=f"derivation:extension:{verdict.derivation}:unchecked-opaque-value",
            ))
        return MappingProxyType({
            key: value for key, value in safe_extensions.items() if key not in affected
        }), verdicts
    if not _model_uses_exact_derivations(model):
        return evaluate_derivations_legacy(
            model,
            population,
            calculator=calculator,
        )
    calculated = _exact_extension_calculator(model, _base_relations(model, population))
    obligations = [
        _exact_derivation_obligation(
            fact_type,
            population,
            calculated.extensions.get(str(fact_type.get("id"))),
            calculated.extensions.unavailable.get(str(fact_type.get("id"))),
        )
        for fact_type in model.fact_types
        if fact_type.get("derivation") in ("derived", "semiderived")
        and fact_type.get("derivation_rule") is not None
    ]
    return calculated.extensions, obligations


def _constraint_view_dispatch(
    model: Model,
    population: Population,
    extensions: Mapping[str, _TypedRelation],
) -> _RuledFactView:
    unavailable = getattr(extensions, "unavailable", {})
    if not unavailable:
        return constraint_view_legacy(model, population, extensions)
    completed = dict(extensions)
    fact_types = {str(item.get("id")): item for item in model.fact_types}
    for fact_type_id in unavailable:
        fact_type = fact_types[fact_type_id]
        completed[fact_type_id] = _TypedRelation(
            fact_type_id,
            _relation_roles(model, fact_type),
            (),
        )
    return constraint_view_legacy(model, population, MappingProxyType(completed))


_evaluate_derivations = _evaluate_derivations_dispatch


_constraint_view = _constraint_view_dispatch


ExactExtensionResult = _ExactExtensionResult
ExactExtensions = _ExactExtensions
ExactJoinWork = _ExactJoinWork
ExtensionResult = _ExtensionResult
FixpointJoinWork = _FixpointJoinWork
JoinWork = _JoinWork
PARTIAL_OPAQUE = _PARTIAL_OPAQUE
PHASE3_LEGACY_CONSTRAINT_VIEW = _PHASE3_LEGACY_CONSTRAINT_VIEW
PHASE3_LEGACY_EVALUATE_DERIVATIONS = _PHASE3_LEGACY_EVALUATE_DERIVATIONS
PartialExtensions = _PartialExtensions
PartialTermFailure = _PartialTermFailure
REFERENCE_PRESENTATION_WORK = _REFERENCE_PRESENTATION_WORK
RuledFactView = _RuledFactView
TypedRelation = _TypedRelation
WITNESS_TRACE = _WITNESS_TRACE
Wildcard = _Wildcard
aggregate_bindings = _aggregate_bindings
aggregate_identity_token = _aggregate_identity_token
apply_negation = _apply_negation
base_relations = _base_relations
binding_lineages = _binding_lineages
clause_bindings = _clause_bindings
component_atoms = _component_atoms
component_product = _component_product
constraint_view = _constraint_view
constraint_view_dispatch = _constraint_view_dispatch
count_term_work = _count_term_work
derivation_obligation = _derivation_obligation
evaluate_derivations = _evaluate_derivations
evaluate_derivations_dispatch = _evaluate_derivations_dispatch
evaluate_stratified_extensions = _evaluate_stratified_extensions
exact_derivation_obligation = _exact_derivation_obligation
exact_extension_calculator = _exact_extension_calculator
extension_fact_map = _extension_fact_map
identity_token = _identity_token
joined_atom_candidates = _joined_atom_candidates
joined_bindings = _joined_bindings
model_uses_exact_derivations = _model_uses_exact_derivations
partial_binding_shape = _partial_binding_shape
partial_bindings = _partial_bindings
partial_clause_rows = _partial_clause_rows
partial_compatible = _partial_compatible
partial_merge = _partial_merge
partial_negation = _partial_negation
partial_row_facts = _partial_row_facts
partial_token = _partial_token
project_extension = _project_extension
project_lineage = _project_lineage
public_refresh_work = _public_refresh_work
python_extension_calculator = _python_extension_calculator
relation_facts = _relation_facts
relation_roles = _relation_roles
requires_fixpoint = _requires_fixpoint
rows_by_identity = _rows_by_identity
rows_from_facts = _rows_from_facts
rule_uses_exact_terms = _rule_uses_exact_terms
scalar_primitive_compatible = _scalar_primitive_compatible
symbolic_value = _symbolic_value
witness = _witness
witness_charge = _witness_charge
witness_row = _witness_row

DerivationFinding.__module__ = 'gnd.checker'

DerivationVerdict.__module__ = 'gnd.checker'

JoinDisconnectedError.__module__ = 'gnd.checker'

_TypedRelation.__module__ = 'gnd.checker'

_JoinWork.__module__ = 'gnd.checker'

_ExactJoinWork.__module__ = 'gnd.checker'

_FixpointJoinWork.__module__ = 'gnd.checker'

_count_term_work.__module__ = 'gnd.checker'

_ExtensionResult.__module__ = 'gnd.checker'

RelationUnavailable.__module__ = 'gnd.checker'

_ExactExtensions.__module__ = 'gnd.checker'

_Wildcard.__module__ = 'gnd.checker'

_PartialTermFailure.__module__ = 'gnd.checker'

_PartialExtensions.__module__ = 'gnd.checker'

_symbolic_value.__module__ = 'gnd.checker'

_partial_token.__module__ = 'gnd.checker'

_partial_compatible.__module__ = 'gnd.checker'

_scalar_primitive_compatible.__module__ = 'gnd.checker'

_partial_merge.__module__ = 'gnd.checker'

_partial_row_facts.__module__ = 'gnd.checker'

_partial_binding_shape.__module__ = 'gnd.checker'

_partial_bindings.__module__ = 'gnd.checker'

_partial_negation.__module__ = 'gnd.checker'

_witness_charge.__module__ = 'gnd.checker'

_witness_row.__module__ = 'gnd.checker'

_partial_clause_rows.__module__ = 'gnd.checker'

_ExactExtensionResult.__module__ = 'gnd.checker'

_RuledFactView.__module__ = 'gnd.checker'

_identity_token.__module__ = 'gnd.checker'

_joined_atom_candidates.__module__ = 'gnd.checker'

_joined_bindings.__module__ = 'gnd.checker'

_relation_facts.__module__ = 'gnd.checker'

_relation_roles.__module__ = 'gnd.checker'

_rows_from_facts.__module__ = 'gnd.checker'

_base_relations.__module__ = 'gnd.checker'

_component_atoms.__module__ = 'gnd.checker'

_component_product.__module__ = 'gnd.checker'

_apply_negation.__module__ = 'gnd.checker'

_clause_bindings.__module__ = 'gnd.checker'

_project_extension.__module__ = 'gnd.checker'

_binding_lineages.__module__ = 'gnd.checker'

_project_lineage.__module__ = 'gnd.checker'

_python_extension_calculator.__module__ = 'gnd.checker'

_rule_uses_exact_terms.__module__ = 'gnd.checker'

_aggregate_identity_token.__module__ = 'gnd.checker'

_aggregate_bindings.__module__ = 'gnd.checker'

_model_uses_exact_derivations.__module__ = 'gnd.checker'

_requires_fixpoint.__module__ = 'gnd.checker'

_evaluate_stratified_extensions.__module__ = 'gnd.checker'

_exact_extension_calculator.__module__ = 'gnd.checker'

exact_extension_envelope.__module__ = 'gnd.checker'

DynamicRefreshWork.__module__ = 'gnd.checker'

StructuredExtensionView.__module__ = 'gnd.checker'

_public_refresh_work.__module__ = 'gnd.checker'

_extension_fact_map.__module__ = 'gnd.checker'

structured_extension_view.__module__ = 'gnd.checker'

derivation_claims_against.__module__ = 'gnd.checker'

_rows_by_identity.__module__ = 'gnd.checker'

_witness.__module__ = 'gnd.checker'

_derivation_obligation.__module__ = 'gnd.checker'

evaluate_derivations_legacy.__module__ = 'gnd.checker'

constraint_view_legacy.__module__ = 'gnd.checker'

_exact_derivation_obligation.__module__ = 'gnd.checker'

_evaluate_derivations_dispatch.__module__ = 'gnd.checker'

_constraint_view_dispatch.__module__ = 'gnd.checker'


def effective_view(model: Model, population: Population) -> Population | _RuledFactView:
    """Validated effective facts for applicability, using the checker policies."""
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    if not any(isinstance(ft.get("derivation_rule"), dict) for ft in model.fact_types):
        return population
    has_opaque = any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for rows in population.facts.values() for fact in rows for value in fact.values()
    )
    if has_opaque:
        derived, _verdicts = _evaluate_derivations_dispatch(model, population)
        calculated = _ExtensionResult(derived, 0)
    elif _model_uses_exact_derivations(model):
        calculated = _exact_extension_calculator(model, _base_relations(model, population))
    else:
        calculated = _python_extension_calculator(model, _base_relations(model, population))
    return _constraint_view_dispatch(model, population, calculated.extensions)
