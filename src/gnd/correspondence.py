"""Authoritative Phase 3 snapshot decision and public-value projection."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from contextvars import ContextVar
from dataclasses import dataclass, replace
from fractions import Fraction
from functools import cmp_to_key
from typing import Any, Literal

from gnd import semantic_rows, semantic_spec
from gnd.branches import REGISTRY, record_branch, snapshot_branch, violated_branch
from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.documents import Model
from gnd.population import Population
from gnd.semantic_adapter import (
    AdaptedSnapshot,
    SnapshotObservation,
    ValueOrigin,
    adapt_snapshot_observed,
    correspondence_scope,
)
from gnd.semantic_ir import IRConstraint, Scalar, SnapshotIR
from gnd.semantic_origins import OriginIndex, OriginSelection
from gnd.semantic_rows import (
    canonical_rows as _canonical_rows,
)
from gnd.semantic_rows import (
    scalar_identity as _scalar_identity,
)
from gnd.terms import compare_terms

_SPEC_GUARDED_ATOM_STATE = semantic_spec.guarded_atom_state
GUARDED_EXISTS_WORK_LIMIT = 200_000

SemanticDecision = Literal["accept", "refuse", "indeterminate"]
AssuranceLevel = Literal["proof-backed", "partial", "none"]
SnapshotVerdict = Literal["pass", "fail", "warning", "unchecked", "vacuous"]
PublicScalar = bool | int | float | str | None
PublicWitness = tuple[Any, ...]


@dataclass(frozen=True, slots=True)
class CorrespondedFinding:
    scope_id: str
    constraint_id: str
    family: str
    modality: Literal["alethic", "deontic"]
    verdict: SnapshotVerdict
    reason_code: str | None
    witness: tuple[tuple[Scalar, ...], ...]
    witness_keys: tuple[str, ...]
    applicable_scope_ids: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class SnapshotDecision:
    findings: tuple[CorrespondedFinding, ...]
    band: int
    acceptance_ready: bool
    semantic_decision: SemanticDecision


@dataclass(frozen=True, slots=True)
class ProjectedFinding:
    scope_id: str
    constraint_id: str
    constraint_type: str
    modality: Literal["alethic", "deontic"]
    verdict: SnapshotVerdict
    reason_code: str | None
    witness: PublicWitness
    applicable_scope_ids: tuple[str, ...]
    fact_refs: tuple[tuple[str, int], ...] = ()


@dataclass(frozen=True, slots=True)
class SnapshotProjection:
    findings: tuple[ProjectedFinding, ...]
    counts: tuple[tuple[SnapshotVerdict, int], ...]
    band: int
    acceptance_ready: bool
    semantic_decision: SemanticDecision


@dataclass(frozen=True, slots=True)
class CompletedVerifyRoute:
    exit_code: Literal[0, 1, 2, 4]
    extraction_route: Literal["authenticated", "skipped"]
    snapshot_result: SnapshotProjection
    assurance: Any


@dataclass(frozen=True, slots=True)
class RefusedVerifyRoute:
    exit_code: Literal[3]
    failure: Literal["missing-sidecar", "invalid-sidecar", "authentication-failed"]
    snapshot_result: None = None
    assurance: None = None


def _applicability_scope(constraint: IRConstraint, applicability: str) -> str:
    event = applicability.removeprefix("vacuous-")
    if event == "coverage-omission":
        return "applicability:vacuity:n-a:coverage-omission"
    if event == "empty-subject":
        variant = "guarded" if constraint.family == "guarded" else "n-a"
        suffix = "empty-subject-any" if variant == "guarded" else "empty-subject-all"
        return f"applicability:vacuity:{variant}:{suffix}"
    if event == "no-observable-subjects":
        family = "cardinality-object" if constraint.family == "cardinality" else constraint.family
        return f"applicability:vacuity:{family}:no-observable-subjects"
    if event == "zero-row-join":
        family = (
            f"{constraint.family}-external"
            if constraint.family in {"uniqueness", "frequency"}
            else "value-comparison-cross"
            if constraint.family == "value-comparison"
            else constraint.family
        )
        return f"applicability:vacuity:{family}:zero-row-join"
    raise ValueError(f"unknown vacuity applicability {applicability!r}")


def _finding_scope(
    constraint: IRConstraint,
    snapshot: Any,
    verdict: SnapshotVerdict,
    reason_code: str | None,
    applicability: str,
    *,
    variant: str,
    guarded_binding_count: int | None = None,
) -> str:
    if verdict == "vacuous" and variant.startswith("phase1-"):
        return snapshot_branch(
            constraint.family,
            variant,
            "vacuous-" + applicability.removeprefix("vacuous-"),
        )
    if applicability.startswith("vacuous-"):
        return _applicability_scope(constraint, applicability)
    if reason_code == "family-unimplemented" and constraint.family not in {"guarded"}:
        return "applicability:implemented:n-a:family-unimplemented"
    if reason_code == "join-disconnected":
        return (
            "applicability:join:"
            + ("guarded" if constraint.family == "guarded" else "n-a")
            + ":disconnected"
        )
    if reason_code == "join-anchor-ambiguous":
        return "applicability:join:n-a:anchor-ambiguous"
    if reason_code == "opaque-value":
        return "applicability:opaque:n-a:opaque-value"
    if verdict in {"fail", "warning"}:
        return violated_branch(constraint.family, variant, constraint.modality)
    if verdict == "pass":
        if constraint.family == "guarded" and guarded_binding_count == 0:
            if variant == "exists":
                return snapshot_branch("guarded", "exists", "clean-zero-bindings")
            return snapshot_branch("guarded", "n-a", "clean-zero-bindings")
        return snapshot_branch(constraint.family, variant, "clean")
    if verdict == "unchecked":
        candidates = [
            row
            for row in REGISTRY
            if row.surface == "snapshot"
            and row.family == constraint.family
            and row.outcome == "unchecked"
            and row.reason_code == reason_code
        ]
        exact = [row for row in candidates if row.variant == variant]
        if len(exact) == 1:
            return exact[0].scope_id
        if len(candidates) == 1:
            return candidates[0].scope_id
        if constraint.refused:
            return f"applicability:adapter:n-a:{constraint.refused}"
    if verdict == "vacuous" and applicability == "evaluate":
        if constraint.family in {"value", "cardinality", "subtype-partition"}:
            family = (
                "cardinality-object" if constraint.family == "cardinality" else constraint.family
            )
            return f"applicability:vacuity:{family}:no-observable-subjects"
        if constraint.family in {"uniqueness", "frequency"}:
            family = f"{constraint.family}-external"
        elif constraint.family == "value-comparison":
            family = "value-comparison-cross"
        else:
            family = constraint.family
        return f"applicability:vacuity:{family}:zero-row-join"
    raise ValueError(f"cannot identify {constraint.family}/{variant}/{verdict}/{reason_code}")


def _registered_unchecked_reason(
    constraint: IRConstraint,
    reason_code: str | None,
) -> str | None:
    """Keep the kernel reason when the production registry can represent it.

    Some broad Phase 2 fixtures deliberately make unrelated constraints
    inapplicable (for example, by omitting their covered relation).  The pure
    family provider then returns its family-specific fallback reason even
    though no such production branch exists.  Those rows are outside the
    proved slice and must use the registry's generic implemented-family
    refusal instead of inventing an unregistered branch.
    """
    if reason_code is None:
        return None
    if any(
        row.surface == "snapshot"
        and row.family == constraint.family
        and row.outcome == "unchecked"
        and row.reason_code == reason_code
        for row in REGISTRY
    ):
        return reason_code
    if reason_code in {"join-disconnected", "join-anchor-ambiguous"}:
        return reason_code
    return "family-unimplemented"


def _inline_uniqueness_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[SnapshotVerdict, None, tuple[tuple[Scalar, ...], ...]] | None:
    """Evaluate inline uniqueness over canonical IR in linear space.

    The Phase 2 executable specification intentionally uses simple bounded
    loops that its proof generators can erase.  Those loops are quadratic for
    a large, all-distinct relation.  Production correspondence keeps that
    proved source unchanged and indexes the same NS-IDENT-1 keys here.  Only
    duplicate groups are sorted, with the specification's comparator, before
    their original full rows are projected as the exhaustive witness.

    ``None`` preserves the specification's unchecked path when projection is
    structurally invalid; callers invoke this only after applicability has
    selected evaluation rather than vacuity or refusal.
    """
    if constraint.family != "uniqueness" or constraint.variant != "inline":
        return None
    valid, keys, facts = semantic_spec.counting_projection_rows(
        constraint, snapshot, "uniqueness"
    )
    if not valid:
        # A value outside the selected uniqueness roles may be opaque. The
        # specification's full-row witness projection refuses such a row, but
        # distinct selected keys still prove this constraint cleanly.
        fact_index = semantic_spec.snapshot_fact_index(snapshot, constraint.fact_type)
        relation_index = semantic_spec.snapshot_relation_index(snapshot, constraint.fact_type)
        if fact_index >= 0 and relation_index >= 0:
            fact_type = snapshot.fact_types[fact_index]
            columns = [
                semantic_spec.fact_role_index(fact_type, role)
                for role in constraint.roles
            ]
            relation = snapshot.relations[relation_index]
            if columns and all(column >= 0 for column in columns) and all(
                len(row) == len(fact_type.roles)
                and all(row[column] is not None for column in columns)
                for row in relation.rows
            ):
                selected = [
                    tuple((row[column].identity_kind, row[column].token) for column in columns)
                    for row in relation.rows
                ]
                if len(selected) == len(set(selected)):
                    return "pass", None, ()
        return None
    groups: dict[
        tuple[tuple[str, str], ...],
        tuple[tuple[Scalar, ...], list[tuple[Scalar, ...]]],
    ] = {}
    for key, fact in zip(keys, facts, strict=True):
        identity = tuple((value.identity_kind, value.token) for value in key)
        if identity in groups:
            groups[identity][1].append(fact)
        else:
            groups[identity] = (key, [fact])
    duplicates = [group for group in groups.values() if len(group[1]) >= 2]
    if not duplicates:
        return "pass", None, ()

    def compare(
        left: tuple[tuple[Scalar, ...], list[tuple[Scalar, ...]]],
        right: tuple[tuple[Scalar, ...], list[tuple[Scalar, ...]]],
    ) -> int:
        if semantic_spec.row_canonical_less(left[0], right[0]):
            return -1
        if semantic_spec.row_canonical_less(right[0], left[0]):
            return 1
        return 0

    duplicates.sort(key=cmp_to_key(compare))
    witness = tuple(fact for _key, rows in duplicates for fact in rows)
    verdict: SnapshotVerdict = "warning" if constraint.modality == "deontic" else "fail"
    return verdict, None, witness


def _legacy_string_order_result(
    constraint: IRConstraint, snapshot: SnapshotIR
) -> tuple[SnapshotVerdict, None, tuple[tuple[Scalar, ...], ...]] | None:
    """Preserve the established public ordering of two admitted raw strings.

    NS-ORDER-2 deliberately excludes raw-string ordering from the proved
    semantic domain, while its source-review ruling also says that exclusion
    changes no public result.  This correspondence refinement therefore
    handles only pairs whose canonical IR cells are both raw strings. Mixed
    or otherwise unproved domains continue to the specification's structured
    ``values-not-comparable`` result.
    """
    if constraint.family != "value-comparison" or constraint.operator not in {
        "<",
        "<=",
        ">",
        ">=",
    }:
        return None
    valid, pairs = semantic_spec.value_comparison_pairs(constraint, snapshot)
    if not valid or not pairs or any(left.kind != "string" or right.kind != "string" for left, right in pairs):
        return None
    violations: dict[
        tuple[tuple[str, str], ...], tuple[Scalar, Scalar]
    ] = {}
    for left, right in pairs:
        ordered = {
            "<": left.token < right.token,
            "<=": left.token <= right.token,
            ">": left.token > right.token,
            ">=": left.token >= right.token,
        }[constraint.operator]
        if not ordered:
            key = (
                (left.identity_kind, left.token),
                (right.identity_kind, right.token),
            )
            violations.setdefault(key, (left, right))
    rows = list(violations.values())

    def compare(left: tuple[Scalar, ...], right: tuple[Scalar, ...]) -> int:
        if semantic_spec.row_canonical_less(left, right):
            return -1
        if semantic_spec.row_canonical_less(right, left):
            return 1
        return 0

    rows.sort(key=cmp_to_key(compare))
    witness = tuple(tuple(row) for row in rows)
    if not witness:
        return "pass", None, ()
    verdict: SnapshotVerdict = "warning" if constraint.modality == "deontic" else "fail"
    return verdict, None, witness


def _indexed_mandatory_result(constraint: IRConstraint, snapshot: SnapshotIR):
    """Use the specification's cursor and identity with a linear membership index."""
    if constraint.family != "mandatory":
        return None
    cursor = semantic_spec.mandatory_cursor(constraint, snapshot)
    if cursor[0] < 0:
        return None
    members = snapshot.rosters[cursor[3]].members
    players = [row[cursor[1]] for row in snapshot.relations[cursor[2]].rows]
    if any(value is None for value in (*members, *players)):
        return None
    identities = {_scalar_identity(value) for value in players}
    missing = [(value,) for value in members if _scalar_identity(value) not in identities]
    if not missing:
        return "pass", None, ()
    return (
        ("warning" if constraint.modality == "deontic" else "fail"),
        None,
        _canonical_rows(missing),
    )


class ReferenceJoinLimit(ValueError):
    """Attempted reference-lane join work exceeded its invocation budget."""


@dataclass
class ReferenceJoinWork:
    attempted: int = 0

    def charge(self) -> None:
        self.attempted += 1
        if self.attempted > 100_000:
            raise ReferenceJoinLimit("reference combined join work exceeds 100000")


def _indexed_guarded_bindings(
    constraint: IRConstraint,
    snapshot: SnapshotIR,
    work: ReferenceJoinWork | None = None,
) -> tuple[bool, tuple[str, ...], tuple[tuple[Scalar, ...], ...]]:
    """Join a connected guarded antecedent by canonical-identity hash indexes."""
    names = semantic_spec.guarded_variable_names(constraint)
    name_positions = {name: position for position, name in enumerate(names)}
    bindings: list[tuple[Scalar | None, ...]] = [tuple(None for _name in names)]
    bound_positions: set[int] = set()

    for atom_index, atom in enumerate(constraint.antecedent):
        fact_position = semantic_spec.snapshot_fact_index(snapshot, atom.fact_type)
        relation_position = semantic_spec.snapshot_relation_index(snapshot, atom.fact_type)
        if fact_position < 0 or relation_position < 0:
            return False, names, ()
        fact = snapshot.fact_types[fact_position]
        relation = snapshot.relations[relation_position]
        if len(atom.bindings) != len(fact.roles):
            return False, names, ()

        terms: list[tuple[int, Any]] = []
        candidate_positions: set[int] = set()
        for role, term in atom.bindings:
            column = semantic_spec.fact_role_index(fact, role)
            if column < 0 or not term.valid:
                return False, names, ()
            terms.append((column, term))
            if term.kind == "variable":
                position = name_positions.get(term.variable)
                if position is None:
                    return False, names, ()
                candidate_positions.add(position)
            elif term.kind != "literal" or term.literal is None:
                return False, names, ()

        candidates: list[tuple[Scalar | None, ...]] = []
        for row in relation.rows:
            if len(row) != len(fact.roles) or any(value is None for value in row):
                return False, names, ()
            candidate: list[Scalar | None] = [None] * len(names)
            matches = True
            for column, term in terms:
                value = row[column]
                if value is None:
                    return False, names, ()
                if term.kind == "literal":
                    if not semantic_spec.scalar_identical(value, term.literal):
                        matches = False
                else:
                    position = name_positions[term.variable]
                    previous = candidate[position]
                    if previous is None:
                        candidate[position] = value
                    elif not semantic_spec.scalar_identical(previous, value):
                        matches = False
            if matches:
                candidates.append(tuple(candidate))

        if atom_index == 0:
            # The seed has no values: candidates already are its merge result.
            if work is not None:
                for _candidate in candidates:
                    work.charge()
            bindings = candidates
            bound_positions = candidate_positions
            continue

        shared = tuple(sorted(bound_positions & candidate_positions))
        index: dict[tuple[tuple[str, str], ...], list[tuple[Scalar | None, ...]]] = {}
        for candidate in candidates:
            key = tuple(
                _scalar_identity(candidate[position])
                for position in shared
                if candidate[position] is not None
            )
            index.setdefault(key, []).append(candidate)

        added = candidate_positions - bound_positions
        joined: list[tuple[Scalar | None, ...]] = []
        for binding in bindings:
            key = tuple(
                _scalar_identity(binding[position])
                for position in shared
                if binding[position] is not None
            )
            for candidate in index.get(key, ()):
                if work is not None:
                    work.charge()
                # The index already established identity at shared positions.
                if not added:
                    joined.append(binding)
                    continue
                merged = list(binding)
                for position in added:
                    merged[position] = candidate[position]
                joined.append(tuple(merged))
        bindings = joined
        bound_positions |= candidate_positions

    complete: list[tuple[Scalar, ...]] = []
    for binding in bindings:
        if any(value is None for value in binding):
            return False, names, ()
        complete.append(tuple(value for value in binding if value is not None))
    return True, names, _canonical_rows(complete)


def _indexed_guarded_verdict(
    constraint: IRConstraint,
    snapshot: SnapshotIR,
    names: tuple[str, ...],
    bindings: tuple[tuple[Scalar, ...], ...],
) -> tuple[SnapshotVerdict, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Evaluate a guarded join using representation-format.md scalar identity."""
    malformed = (
        constraint.family != "guarded"
        or constraint.variant not in {"comparison", "atom", "absence"}
        or constraint.consequent_kind != constraint.variant
        or constraint.refused != ""
        or not constraint.antecedent
    )
    if constraint.variant == "comparison":
        malformed = malformed or (
            len(constraint.operands) != 2
            or bool(constraint.consequent)
            or constraint.operator not in {"<", "<=", "=", ">=", ">", "!="}
        )
    else:
        malformed = malformed or len(constraint.consequent) != 1 or bool(constraint.operands)
    if malformed:
        return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()

    consequent_index: set[tuple[tuple[str, str], ...]] | None = None
    consequent_terms: tuple[tuple[int, Any], ...] = ()
    if constraint.variant != "comparison":
        atom = constraint.consequent[0]
        fact_position = semantic_spec.snapshot_fact_index(snapshot, atom.fact_type)
        relation_position = semantic_spec.snapshot_relation_index(snapshot, atom.fact_type)
        if fact_position < 0 or relation_position < 0:
            return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
        fact = snapshot.fact_types[fact_position]
        relation = snapshot.relations[relation_position]
        if len(atom.bindings) != len(fact.roles):
            return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
        prepared: list[tuple[int, Any]] = []
        for role, term in atom.bindings:
            column = semantic_spec.fact_role_index(fact, role)
            if column < 0 or not term.valid:
                return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
            prepared.append((column, term))
        consequent_terms = tuple(prepared)
        consequent_index = set()
        for row in relation.rows:
            if len(row) != len(fact.roles) or any(value is None for value in row):
                return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
            consequent_index.add(
                tuple(_scalar_identity(value) for value in row if value is not None)
            )

    violations: list[tuple[Scalar, ...]] = []
    undecidable = False
    for binding in bindings:
        if constraint.variant == "comparison":
            left = semantic_spec.guarded_operand_value(constraint.operands[0], names, binding)
            right = semantic_spec.guarded_operand_value(constraint.operands[1], names, binding)
            state = (
                -1
                if left is None or right is None
                else semantic_spec.comparison_pair_state(left, right, constraint.operator)
            )
        else:
            if semantic_spec.guarded_atom_state is not _SPEC_GUARDED_ATOM_STATE:
                state = semantic_spec.guarded_atom_state(
                    constraint.consequent[0], names, binding, snapshot
                )
            else:
                ground: list[Scalar | None] = [None] * len(consequent_terms)
                for column, term in consequent_terms:
                    value = semantic_spec.guarded_operand_value(term, names, binding)
                    if value is None or ground[column] is not None:
                        undecidable = True
                        break
                    ground[column] = value
                if undecidable or any(value is None for value in ground):
                    state = -1
                else:
                    key = tuple(_scalar_identity(value) for value in ground if value is not None)
                    state = int(key in consequent_index) if consequent_index is not None else -1
            if constraint.variant == "absence" and state >= 0:
                state = 1 - state
        if state < 0:
            undecidable = True
        elif state == 0:
            violations.append(binding)

    if undecidable:
        return "unchecked", semantic_spec.unchecked_reason_of(constraint, snapshot), ()
    witness = _canonical_rows(violations)
    if not witness:
        return "pass", None, ()
    verdict: SnapshotVerdict = "warning" if constraint.modality == "deontic" else "fail"
    return verdict, None, witness


def _ir_scalar_value(value: Scalar) -> Any:
    if value.kind == "number":
        rational = Fraction(value.num, value.den)
        return rational.numerator if rational.denominator == 1 else rational
    if value.kind == "boolean":
        return value.token == "true"
    return value.token


def _ir_term_syntax(operand: Any) -> Any:
    if operand.kind == "variable":
        return operand.variable
    if operand.kind == "literal":
        return _ir_scalar_value(operand.literal) if operand.literal is not None else None
    if operand.kind == "function":
        return {
            "fn": operand.function,
            "args": [_ir_term_syntax(argument) for argument in operand.arguments],
        }
    return None


def _indexed_guarded_exists_verdict(
    constraint: IRConstraint,
    snapshot: SnapshotIR,
    names: tuple[str, ...],
    bindings: tuple[tuple[Scalar, ...], ...],
    declared_covers: tuple[str, ...],
    *,
    work_counts: dict[str, int] | None = None,
    reference_work: ReferenceJoinWork | None = None,
) -> tuple[SnapshotVerdict, str | None, tuple[tuple[Scalar, ...], ...]]:
    """Evaluate a bounded joint exists join over the original covered relations."""
    if (
        constraint.family != "guarded"
        or constraint.variant != "exists"
        or constraint.consequent_kind != "exists"
        or constraint.refused
        or not constraint.exists_atoms
    ):
        return "unchecked", "malformed-constraint", ()
    # Vacuity is settled by the guarded checker before this evaluator is
    # called. Keep the direct evaluator total as well: no binding means the
    # implication has no consequent instances to check.
    if not bindings:
        return "pass", None, ()
    if any(
        not isinstance(binding, (tuple, list))
        or len(binding) != len(names)
        or any(not isinstance(value, Scalar) for value in binding)
        for binding in bindings
    ):
        return "unchecked", "malformed-constraint", ()
    missing = tuple(
        dict.fromkeys(
            atom.fact_type
            for atom in constraint.exists_atoms
            if atom.fact_type not in declared_covers
        )
    )
    if missing:
        return "unchecked", "guarded-exists-coverage-missing", ()

    facts_by_id = {row.id: row for row in snapshot.fact_types}
    relations_by_id = {row.fact_type: row for row in snapshot.relations}
    work = 0
    counts = work_counts if work_counts is not None else {}
    for name in (
        "candidate_rows",
        "index_probes",
        "merged_bindings",
        "term_nodes",
        "term_operations",
        "maximum_value_bits",
    ):
        counts.setdefault(name, 0)

    def consume(amount: int = 1, *, category: str | None = None) -> bool:
        nonlocal work
        if reference_work is not None and category == "merged_bindings":
            reference_work.charge()
        work += amount
        if category is not None:
            counts[category] = counts.get(category, 0) + amount
        counts["total_work"] = work
        return work <= GUARDED_EXISTS_WORK_LIMIT

    candidates_by_atom: list[list[dict[str, Scalar]]] = []
    variable_order: list[str] = list(names)
    for atom in constraint.exists_atoms:
        fact = facts_by_id.get(atom.fact_type)
        relation = relations_by_id.get(atom.fact_type)
        if fact is None or relation is None or len(atom.bindings) != len(fact.roles):
            return "unchecked", "malformed-constraint", ()
        for _role, term in atom.bindings:
            if term.kind == "variable" and term.variable not in variable_order:
                variable_order.append(term.variable)
        columns: list[tuple[int, Any]] = []
        for role, term in atom.bindings:
            column = semantic_spec.fact_role_index(fact, role)
            if column < 0 or not term.valid:
                return "unchecked", "malformed-constraint", ()
            columns.append((column, term))
        candidates: list[dict[str, Scalar]] = []
        seen_candidates: set[tuple[tuple[str, str], ...]] = set()
        for row in relation.rows:
            if not consume(category="candidate_rows"):
                return "unchecked", "guarded-exists-work-limit", ()
            if len(row) != len(fact.roles) or any(value is None for value in row):
                return "unchecked", "malformed-constraint", ()
            candidate: dict[str, Scalar] = {}
            matches = True
            for column, term in columns:
                value = row[column]
                if value is None:
                    return "unchecked", "malformed-constraint", ()
                if term.kind == "literal":
                    if term.literal is None or not semantic_spec.scalar_identical(value, term.literal):
                        matches = False
                elif term.kind == "variable":
                    previous = candidate.get(term.variable)
                    if previous is None:
                        candidate[term.variable] = value
                    elif not semantic_spec.scalar_identical(previous, value):
                        matches = False
                else:
                    return "unchecked", "malformed-constraint", ()
            if matches:
                key = tuple(
                    (name, *_scalar_identity(value))
                    for name, value in sorted(candidate.items())
                )
                if key not in seen_candidates:
                    seen_candidates.add(key)
                    candidates.append(candidate)
        candidates_by_atom.append(candidates)

    index_specs: list[
        tuple[
            tuple[str, ...],
            dict[tuple[tuple[str, str], ...], list[dict[str, Scalar]]],
        ]
    ] = []
    bound_names = set(names)
    for candidates in candidates_by_atom:
        candidate_names = set(candidates[0]) if candidates else set()
        shared = tuple(
            name for name in variable_order if name in bound_names and name in candidate_names
        )
        index: dict[
            tuple[tuple[str, str], ...], list[dict[str, Scalar]]
        ] = {}
        for candidate in candidates:
            key = tuple(_scalar_identity(candidate[name]) for name in shared)
            index.setdefault(key, []).append(candidate)
        index_specs.append((shared, index))
        bound_names.update(candidate_names)

    violations: list[tuple[Scalar, ...]] = []
    undefined_bindings: list[tuple[Scalar, ...]] = []
    undefined = False
    undefined_reason: str | None = None
    for antecedent in bindings:
        initial = {name: value for name, value in zip(names, antecedent, strict=True)}
        partials = [initial]
        for shared, index in index_specs:
            joined: list[dict[str, Scalar]] = []
            for partial in partials:
                if not consume(category="index_probes"):
                    return "unchecked", "guarded-exists-work-limit", ()
                key = tuple(_scalar_identity(partial[name]) for name in shared)
                for candidate in index.get(key, ()):
                    if not consume(category="merged_bindings"):
                        return "unchecked", "guarded-exists-work-limit", ()
                    merged = dict(partial)
                    merged.update(candidate)
                    joined.append(merged)
            partials = joined
            if not partials:
                break
        witnessed = False
        for assignment in partials:
            python_binding = {
                name.removeprefix("$"): _ir_scalar_value(value)
                for name, value in assignment.items()
            }
            satisfies = True
            assignment_undefined = False
            for operator, left, right in constraint.exists_where:
                result = compare_terms(
                    operator,
                    _ir_term_syntax(left),
                    _ir_term_syntax(right),
                    python_binding,
                    bound_cross_product=True,
                )
                counts["term_nodes"] += result.nodes
                counts["term_operations"] += result.operations
                counts["maximum_value_bits"] = max(
                    counts["maximum_value_bits"], result.max_value_bits
                )
                if not consume(
                    max(1, result.nodes + result.operations)
                ):
                    return "unchecked", "guarded-exists-work-limit", ()
                if not result.available:
                    undefined = True
                    assignment_undefined = True
                    undefined_reason = undefined_reason or result.reason or "term:dependency-unavailable"
                    satisfies = False
                elif result.value is not True:
                    satisfies = False
            if assignment_undefined:
                undefined_bindings.append(
                    tuple(assignment[name] for name in variable_order if name in assignment)
                )
            if satisfies:
                witnessed = True
        if not witnessed:
            violations.append(antecedent)

    if undefined:
        return (
            "unchecked",
            undefined_reason or "term:dependency-unavailable",
            _canonical_rows(undefined_bindings),
        )
    witness = _canonical_rows(violations)
    if not witness:
        if constraint.exists_where:
            record_branch("snapshot:guarded:exists:exact-success")
        return "pass", None, ()
    verdict: SnapshotVerdict = "warning" if constraint.modality == "deontic" else "fail"
    return verdict, None, witness


def evaluate_snapshot(
    adapted: AdaptedSnapshot,
    *,
    variant_aliases: Mapping[str, str] | None = None,
    reference_work: ReferenceJoinWork | None = None,
) -> SnapshotDecision:
    # A whole-snapshot refusal suppresses proof-backed assurance, but it does
    # not suppress the ordinary unchecked findings needed by callers.  The
    # certification walk consumes this same scope predicate later.
    correspondence_scope(adapted)
    aliases = variant_aliases or {}
    findings: list[CorrespondedFinding] = []
    for constraint in adapted.snapshot.constraints:
        semantic_snapshot = adapted.snapshot
        if constraint.family not in {"mandatory", "mandatory-disjunctive"}:
            # `covers` is an epistemic input for mandatory participation.  The
            # production checker has always evaluated other declared families
            # over admitted facts even when a caller omitted the optional
            # coverage assertion.  Give the pure provider that same admitted
            # relation view without altering the observation or public
            # coverage report.
            semantic_snapshot = replace(
                adapted.snapshot,
                covers=tuple(row.id for row in adapted.snapshot.fact_types),
            )
        from gnd.temporal_guarded import evaluate_temporal_guard

        temporal = evaluate_temporal_guard(constraint, semantic_snapshot)
        applicability = (
            "evaluate"
            if temporal is not None
            else semantic_spec.applicability_of(constraint, semantic_snapshot)
        )
        guarded_bindings: tuple[tuple[Scalar, ...], ...] | None = None
        guarded_names: tuple[str, ...] = ()
        guarded_valid = False
        work_exceeded = False
        if constraint.family == "guarded" and temporal is None:
            try:
                guarded_valid, guarded_names, guarded_bindings = _indexed_guarded_bindings(
                    constraint, semantic_snapshot, reference_work
                )
            except ReferenceJoinLimit:
                work_exceeded = True
        if work_exceeded:
            applicability = "evaluate"
            verdict, reason, witness = "unchecked", "reference-join-work-limit", ()
        elif temporal is not None:
            verdict, reason, witness = temporal
        elif guarded_bindings == () and guarded_valid and not applicability.startswith("vacuous-"):
            # NS-ORDER-OF-RESOLUTION-1: an implication with no antecedent
            # bindings is clean before an unused consequent is type-checked.
            applicability = "evaluate"
            verdict, reason, witness = "pass", None, ()
        else:
            indexed = None
            if applicability == "evaluate":
                if (
                    constraint.family == "guarded"
                    and guarded_valid
                    and guarded_bindings is not None
                ):
                    if constraint.variant == "exists":
                        try:
                            indexed = _indexed_guarded_exists_verdict(
                                constraint,
                                semantic_snapshot,
                                guarded_names,
                                guarded_bindings,
                                adapted.snapshot.covers,
                                reference_work=reference_work,
                            )
                        except ReferenceJoinLimit:
                            indexed = ("unchecked", "reference-join-work-limit", ())
                    else:
                        indexed = _indexed_guarded_verdict(
                            constraint,
                            semantic_snapshot,
                            guarded_names,
                            guarded_bindings,
                        )
                if indexed is None:
                    indexed = _indexed_mandatory_result(constraint, semantic_snapshot)
                if indexed is None:
                    indexed = _inline_uniqueness_result(constraint, semantic_snapshot)
                if indexed is None:
                    indexed = _legacy_string_order_result(constraint, semantic_snapshot)
                entry = FAMILIES.get(constraint.family)
                if indexed is None and entry is not None and entry.production is not None:
                    indexed = resolve_hook(entry.production, vars(semantic_rows))(
                        constraint, semantic_snapshot
                    )
            verdict, reason, witness = (
                indexed
                if indexed is not None
                else semantic_spec.verdict_of(constraint, semantic_snapshot)
            )
        if constraint.refused == "opaque-value" and temporal is None:
            verdict, reason, witness = "unchecked", "opaque-value", ()
        if verdict == "unchecked" and reason != "opaque-value":
            reason = _registered_unchecked_reason(constraint, reason)
        variant = aliases.get(constraint.ref, constraint.variant)
        witness_keys: tuple[str, ...] = ()
        if constraint.family == "guarded":
            witness_keys = semantic_spec.guarded_variable_names(constraint)
            if (
                constraint.variant == "exists"
                and verdict == "unchecked"
                and reason is not None
                and reason.startswith("term:")
            ):
                ordered = list(witness_keys)
                for atom in constraint.exists_atoms:
                    for _role, term in atom.bindings:
                        if term.kind == "variable" and term.variable not in ordered:
                            ordered.append(term.variable)
                witness_keys = tuple(ordered)
        elif constraint.family == "uniqueness" and constraint.variant == "inline":
            fact_index = semantic_spec.snapshot_fact_index(adapted.snapshot, constraint.fact_type)
            if fact_index >= 0:
                witness_keys = tuple(
                    role.name for role in adapted.snapshot.fact_types[fact_index].roles
                )
        scope_id = _finding_scope(
            constraint,
            semantic_snapshot,
            verdict,
            reason,
            applicability,
            variant=variant,
            guarded_binding_count=(
                len(guarded_bindings) if guarded_bindings is not None and guarded_valid else None
            ),
        )
        record_branch(scope_id, outcome=verdict)
        findings.append(
            CorrespondedFinding(
                scope_id=scope_id,
                constraint_id=constraint.ref,
                family=constraint.family,
                modality=constraint.modality,
                verdict=verdict,
                reason_code=reason,
                witness=witness,
                witness_keys=witness_keys,
                applicable_scope_ids=(scope_id,),
            )
        )
    band = semantic_spec.band_of(tuple((row.modality, row.verdict) for row in findings))
    if band != 1 and any(row.reason_code == "reference-join-work-limit" for row in findings):
        band = 4
    decision = semantic_spec.decision_of(band)
    if decision not in {"accept", "refuse", "indeterminate"}:
        raise ValueError(f"semantic composer returned no decision for band {band}")
    return SnapshotDecision(
        findings=tuple(findings),
        band=band,
        acceptance_ready=band == 0,
        semantic_decision=decision,
    )


def _same_scalar(left: Scalar, right: Scalar) -> bool:
    return semantic_spec.scalar_identical(left, right)


_MISSING = object()


_ORIGIN_INDEX: ContextVar[OriginIndex | None] = ContextVar("gnd_origin_index", default=None)
_ORIGIN_SELECTION: ContextVar[OriginSelection | None] = ContextVar(
    "gnd_origin_selection", default=None
)


def _origin_value(
    value: Scalar,
    origins: Sequence[ValueOrigin],
    used: set[int],
    *,
    witness_key: str | None = None,
) -> PublicScalar | object:
    selection = _ORIGIN_SELECTION.get()
    if selection is None or selection.index.origins is not origins or selection.used is not used:
        selection = OriginSelection(OriginIndex(origins), used)
    found, raw = selection.value(value, witness_key)
    return raw if found else _MISSING


def _subject_occurrences(
    constraint_id: str, observation: SnapshotObservation
) -> tuple[tuple[str, int], ...]:
    subjects = dict(observation.constraint_subjects).get(constraint_id, ())
    return tuple(node for node in observation.fact_occurrences if node[0] in subjects)


def project_reference_limit(
    finding: ProjectedFinding, observation: SnapshotObservation
) -> ProjectedFinding:
    scope = "snapshot:guarded:n-a:unchecked-reference-join-work-limit"
    return replace(
        finding,
        scope_id=scope,
        verdict="unchecked",
        reason_code="reference-join-work-limit",
        witness=(),
        applicable_scope_ids=(scope,),
        fact_refs=_subject_occurrences(finding.constraint_id, observation),
    )


def project_finding(
    finding: CorrespondedFinding,
    observation: SnapshotObservation,
) -> ProjectedFinding:
    index = _ORIGIN_INDEX.get()
    if index is None or index.origins is not observation.origins:
        index = OriginIndex(observation.origins)
    coordinates: set[tuple[str, int]] = set()
    if finding.verdict == "unchecked" and finding.reason_code in {
        "opaque-value",
        "reference-join-work-limit",
    }:
        coordinates.update(_subject_occurrences(finding.constraint_id, observation))
    elif finding.verdict in {"fail", "warning"}:
        coordinates.update(index.coordinates(finding.witness))
    rows: list[Any] = []
    used_origins: set[int] = set()
    token = _ORIGIN_SELECTION.set(OriginSelection(index, used_origins))
    try:
        for row in finding.witness:
            projected: list[PublicScalar] = []
            for position, scalar in enumerate(row):
                witness_key = (
                    finding.witness_keys[position] if position < len(finding.witness_keys) else None
                )
                value = _origin_value(
                    scalar,
                    observation.origins,
                    used_origins,
                    witness_key=witness_key,
                )
                if value is _MISSING:
                    raise ValueError(
                        f"witness for {finding.scope_id!r} has no admissible origin"
                    )
                projected.append(value)
            if finding.family == "guarded" or finding.witness_keys:
                rows.append(dict(zip(finding.witness_keys, projected, strict=True)))
            else:
                rows.append(tuple(projected))
    finally:
        _ORIGIN_SELECTION.reset(token)
    return ProjectedFinding(
        finding.scope_id,
        finding.constraint_id,
        finding.family,
        finding.modality,
        finding.verdict,
        finding.reason_code,
        tuple(rows),
        finding.applicable_scope_ids,
        tuple(sorted(coordinates)),
    )


def project_snapshot(
    decision: SnapshotDecision,
    observation: SnapshotObservation,
) -> SnapshotProjection:
    token = _ORIGIN_INDEX.set(OriginIndex(observation.origins))
    try:
        findings = tuple(project_finding(row, observation) for row in decision.findings)
    finally:
        _ORIGIN_INDEX.reset(token)
    vocabulary: tuple[SnapshotVerdict, ...] = ("pass", "fail", "warning", "unchecked", "vacuous")
    counts = tuple((name, sum(row.verdict == name for row in findings)) for name in vocabulary)
    return SnapshotProjection(
        findings=findings,
        counts=counts,
        band=decision.band,
        acceptance_ready=decision.acceptance_ready,
        semantic_decision=decision.semantic_decision,
    )


def correspond_snapshot(
    model: Model,
    population: Population,
    *,
    effective_facts: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    effective_lineage: Mapping[
        str, Sequence[tuple[tuple[str | int, ...], ...]]
    ]
    | None = None,
    variant_aliases: Mapping[str, str] | None = None,
) -> tuple[AdaptedSnapshot, SnapshotDecision]:
    adapted = adapt_snapshot_observed(
        model,
        population,
        effective_facts=effective_facts,
        effective_lineage=effective_lineage,
    )
    return adapted, evaluate_snapshot(
        adapted,
        variant_aliases=variant_aliases,
        reference_work=ReferenceJoinWork() if model.reference_populations else None,
    )
