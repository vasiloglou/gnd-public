"""Admitted snapshot -> immutable semantic inputs, without verdict evaluation.

The adapter preserves claimed rows, literal syntax, universe membership and
structured dependency data. It does not run joins or calculate rule extensions.
Correspondence and derivation correctness remain separate proof obligations.
"""

from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import date, datetime
from typing import Any

from gnd import checker, semantic_spec
from gnd.address import positional_constraint_ref
from gnd.applicability import applicable_scope_ids
from gnd.atoms import atom_bind, atom_has_bind
from gnd.branches import REGISTRY, constraint_variant, record_branch, time_relative_operand
from gnd.documents import Model
from gnd.errors import UnvalidatedPopulationError
from gnd.model import (
    body_components,
    derivation_dependencies,
    derivation_strata,
    iter_derivation_clauses,
)
from gnd.population import Population
from gnd.semantic_ir import (
    ADAPTER_REFUSALS,
    IRAtom,
    IRConstraint,
    IRDerivation,
    IRFactType,
    IRObjectType,
    IROperand,
    IRRefusal,
    IRRelation,
    IRRole,
    IRRoster,
    Opaque,
    Scalar,
    SnapshotIR,
)
from gnd.universe import resolve_primitive

_FAMILIES = frozenset(row.family for row in REGISTRY if row.surface == "snapshot")
_NUMERIC = ("Integer", "Float", "Number")
_ORDERING = ("<", "<=", ">", ">=")

PRODUCTION_DIMENSIONS = (
    "identifiers",
    "roles",
    "primitive-values",
    "fact-extents",
    "object-rosters",
    "population-covers",
    "declared-state",
    "modality",
    "operation-state",
    "operation-effects",
    "walk-position",
    "derivation-kind",
    "derivation-dependencies",
    "finite-domain-assumptions",
)


@dataclass(frozen=True, slots=True)
class ValueOrigin:
    source: str
    path: tuple[str | int, ...]
    scalar: Scalar
    json_kind: str
    admitted_value: bool | int | float | str | None
    derivation_fact_type: str | None
    dependency_paths: tuple[tuple[str | int, ...], ...]


@dataclass(frozen=True, slots=True)
class SnapshotObservation:
    origins: tuple[ValueOrigin, ...]
    production_dimensions: tuple[str, ...]
    refusals: tuple[IRRefusal, ...]
    applicable_scope_ids: tuple[str, ...]
    fact_occurrences: tuple[tuple[str, int], ...] = ()
    constraint_subjects: tuple[tuple[str, tuple[str, ...]], ...] = ()


@dataclass(frozen=True, slots=True)
class AdaptedSnapshot:
    snapshot: SnapshotIR
    observation: SnapshotObservation


@dataclass(frozen=True, slots=True)
class _ObservedPopulation:
    covers: Sequence[str]
    instances: Mapping[str, Sequence[Any]]
    facts: Mapping[str, Sequence[Mapping[str, Any]]]


def canonical_scalar(value: object, primitive: str | None) -> Scalar | Opaque | None:
    """Exact identity plus optional ordering coordinates; never stringify a type mismatch."""
    if isinstance(value, dict) and set(value) == {"$opaque"}:
        label = value["$opaque"]
        if isinstance(label, str) and label:
            return Opaque(label)
        return None
    if type(value) is bool:
        if primitive in _NUMERIC:
            return None
        return Scalar("boolean", "true" if value else "false", 0, 1, False, "boolean")
    if isinstance(value, (int, float)):
        value = int(value) if isinstance(value, int) else float(value)
        if isinstance(value, float) and not math.isfinite(value):
            return None
        numerator, denominator = value.as_integer_ratio()
        return Scalar(
            "number", f"{numerator}/{denominator}", numerator, denominator, True, "number"
        )
    if isinstance(value, str):
        value = str(value)
        if primitive == "Date":
            try:
                ordinal = date.fromisoformat(value).toordinal()
            except ValueError:
                return None
            return Scalar("date", value, ordinal, 1, True, "string")
        if primitive == "DateTime":
            try:
                parsed = datetime.fromisoformat(
                    value[:-1] + "+00:00" if value[-1:] in ("Z", "z") else value
                )
                offset = parsed.utcoffset()
            except ValueError:
                return None
            microseconds = (
                ((parsed.toordinal() - 1) * 24 + parsed.hour) * 3600
                + parsed.minute * 60
                + parsed.second
            ) * 1_000_000 + parsed.microsecond
            if offset is not None:
                # Integer arithmetic also handles UTC instants outside datetime's
                # representable local-year range; astimezone would overflow.
                microseconds -= (
                    offset.days * 86400 + offset.seconds
                ) * 1_000_000 + offset.microseconds
            return Scalar(
                "datetime-aware" if offset is not None else "datetime-naive",
                value,
                microseconds,
                1,
                True,
                "string",
            )
        return Scalar("string", value, 0, 1, False, "string")
    if value is None:
        return Scalar("null", "null", 0, 1, False, "null")
    return None


class _ShapeError(ValueError):
    pass


class _Refused(ValueError):
    pass


def _text(value: Any) -> str:
    if not isinstance(value, str):
        raise _ShapeError("expected a string")
    return value


def _list(value: Any) -> list:
    if not isinstance(value, list):
        raise _ShapeError("expected a list")
    return value


def _mapping(value: Any) -> dict:
    if not isinstance(value, dict):
        raise _ShapeError("expected an object")
    return value


def _reason(value: Any, primitive: str | None) -> str:
    if isinstance(value, dict) and set(value) == {"$opaque"}:
        return "opaque-value"
    if isinstance(value, float) and not math.isfinite(value):
        return "non-finite-number"
    if type(value) is bool and primitive in _NUMERIC:
        return "boolean-in-numeric-role"
    return "malformed-constraint"


def _refusal(location: str, reason: str) -> IRRefusal:
    if reason not in ADAPTER_REFUSALS:
        raise ValueError("unknown adapter refusal")
    record_branch("applicability:adapter:n-a:" + reason, outcome="refused")
    return IRRefusal(location, reason)


def _scalar(value: Any, primitive: str | None) -> Scalar:
    converted = canonical_scalar(value, primitive)
    if converted is None or isinstance(converted, Opaque):
        raise _Refused(_reason(value, primitive))
    return converted


def _ref(value: Any, model: Model) -> tuple[str, str]:
    value = _mapping(value)
    fact_type, role = _text(value.get("fact_type")), _text(value.get("role"))
    if checker._role_object_type(model, fact_type, role) is None:
        raise _Refused("unresolvable-role")
    return fact_type, role


def _refs(value: Any, model: Model) -> tuple[tuple[str, str], ...]:
    return tuple(_ref(item, model) for item in _list(value))


def _primitive(model: Model, fact_type: str, role: str) -> str:
    object_type = checker._role_object_type(model, fact_type, role)
    if object_type is None:
        raise _Refused("unresolvable-role")
    return resolve_primitive(object_type, model) or ""


def _term(value: Any, primitive: str = "", *, derivation: bool = False) -> IROperand:
    if isinstance(value, str) and value.startswith("$") and (not derivation or len(value) > 1):
        return IROperand("variable", variable=value, primitive=primitive)
    if derivation and canonical_scalar(value, None) is None:
        return IROperand("literal", primitive=primitive, valid=False, refused=_reason(value, None))
    raw = _scalar(value, None)
    literal = canonical_scalar(value, primitive or None) or raw
    return IROperand("literal", literal=literal, raw_literal=raw, primitive=primitive)


def _guarded_term(value: Any, primitives: Mapping[str, str], borrowed: str = "") -> IROperand:
    if isinstance(value, dict) and set(value) in ({"date"}, {"duration_days"}):
        primitive = "Date" if "date" in value else "Duration"
        literal = canonical_scalar(next(iter(value.values())), primitive)
        return IROperand(
            "literal",
            literal=literal,
            raw_literal=literal,
            primitive=primitive,
            tagged=True,
            valid=literal is not None,
        )
    if isinstance(value, dict) and set(value) == {"fn", "args"}:
        function = _text(value.get("fn"))
        arguments = tuple(
            _guarded_term(argument, primitives) for argument in _list(value.get("args"))
        )
        inferred = (
            "Date"
            if function in {"date_add", "date_sub"}
            else (
                "Integer"
                if arguments and all(argument.primitive == "Integer" for argument in arguments)
                else "Number"
            )
        )
        return IROperand(
            "function",
            primitive=inferred,
            function=function,
            arguments=arguments,
            valid=function in {"add", "sub", "mul", "neg", "abs", "mod", "date_add", "date_sub"},
        )
    own = primitives.get(value, "") if isinstance(value, str) else ""
    return _term(value, own or borrowed)


def _atom(value: Any, model: Model, *, derivation: bool = False) -> IRAtom:
    value = _mapping(value)
    fact_type = _text(value.get("fact_type"))
    if not atom_has_bind(value):
        raise _ShapeError("an atom requires bindings")
    bindings = tuple(
        (name, _term(term, _primitive(model, fact_type, name), derivation=derivation))
        for name, term in atom_bind(value).items()
    )
    return IRAtom(fact_type, bindings)


def _rule_refusals(rule: IRDerivation) -> tuple[IRRefusal, ...]:
    """Attach every unrepresentable term to its retained rule position."""
    locations = [(f"head[{role}]", term) for role, term in rule.head]
    for section, atoms in (("body", rule.body), ("negate", rule.negate)):
        locations.extend(
            (f"{section}[{index}].bindings[{role}]", term)
            for index, atom in enumerate(atoms)
            for role, term in atom.bindings
        )
    return tuple(
        _refusal(f"derivations[{rule.fact_type}].{location}", term.refused)
        for location, term in locations
        if term.refused
    )


def _operand(
    value: Any, model: Model, fact_type: dict | None, other_primitive: str = ""
) -> IROperand:
    if fact_type is None:
        ft, role = _ref(value, model)
        return IROperand("role", fact_type=ft, role=role, primitive=_primitive(model, ft, role))
    ft = _text(fact_type.get("id"))
    names = {role["role_name"] for role in fact_type.get("roles", [])}
    named_role = (
        value.get("role")
        if isinstance(value, dict) and "role" in value
        else value
        if isinstance(value, str) and value in names
        else None
    )
    if named_role is not None:
        named_role = _text(named_role)
        return IROperand(
            "role",
            fact_type=ft,
            role=named_role,
            primitive=_primitive(model, ft, named_role),
            tagged=isinstance(value, dict),
        )
    tagged = isinstance(value, dict) and "literal" in value
    raw = value["literal"] if tagged else value
    raw_scalar = _scalar(raw, None)
    parsed = checker._literal(raw, other_primitive or None, legacy=not tagged)
    valid = parsed is not checker._INVALID_LITERAL
    if not valid and not tagged:
        parsed, valid = raw, True
    literal = (
        canonical_scalar(parsed, other_primitive or None) or _scalar(parsed, None)
        if valid
        else None
    )
    return IROperand(
        "literal",
        literal=literal,
        raw_literal=raw_scalar,
        primitive=other_primitive,
        tagged=tagged,
        valid=valid and literal is not None,
    )


def _bounds(value: Any, primitive: str | None) -> tuple[Scalar | None, Scalar | None, bool, bool]:
    value = _mapping(value)
    lower, upper = value.get("min"), value.get("max")
    inclusive = (value.get("min_inclusive", True), value.get("max_inclusive", True))
    if any(type(flag) is not bool for flag in inclusive):
        raise _ShapeError("inclusive flags must be boolean")
    return (
        _scalar(lower, primitive) if lower is not None else None,
        _scalar(upper, primitive) if upper is not None else None,
        *inclusive,
    )


def adapt_constraint(
    constraint: dict[str, Any], fact_type: dict[str, Any] | None, ref: str, model: Model
) -> IRConstraint:
    """Total over constraint JSON shapes; refusals never become empty successful predicates."""
    base = IRConstraint(
        ref=ref if isinstance(ref, str) else "",
        family="",
        variant="n-a",
        modality="",
        fact_type="",
        roles=(),
        role_refs=(),
        sequences=(),
        object_type="",
        subtypes=(),
        flags=(False, False, True, True),
        minimum=None,
        maximum=None,
        allowed=(),
        ranges=(),
        operator="",
        literal=None,
        operands=(),
        consequent_kind="",
        antecedent=(),
        consequent=(),
        scope_fact_types=(),
        expression="",
        refused="",
    )
    try:
        source = _mapping(constraint)
        family = _text(source.get("type"))
        # Preserve an admitted modality even when the family itself must be
        # refused.  The refusal still contributes to the semantic band:
        # dropping ``alethic`` here previously made an unchecked,
        # unimplemented constraint look clean downstream.
        candidate_modality = source.get("modality")
        base = replace(
            base,
            family=family,
            modality=(candidate_modality if candidate_modality in ("alethic", "deontic") else ""),
        )
        if family not in _FAMILIES:
            raise _Refused("unregistered-family")
        modality = _text(source.get("modality"))
        if modality not in ("alethic", "deontic"):
            raise _ShapeError("unknown modality")
        host = _text(fact_type["id"]) if fact_type is not None else ""
        base = replace(base, modality=modality, fact_type=host)
        # Parse structured reference fields before calling the shared variant
        # classifier, whose production callers already have admitted shapes.
        role_refs = _refs(source["role_refs"], model) if "role_refs" in source else ()
        if "role_ref" in source:
            role_refs += (_ref(source["role_ref"], model),)
        sequences = ()
        for pair in (("subset_role_seq", "superset_role_seq"), ("role_seq_a", "role_seq_b")):
            if any(key in source for key in pair):
                sequences = tuple(_refs(source[key], model) for key in pair)
        if "role_seqs" in source:
            sequences = tuple(_refs(sequence, model) for sequence in _list(source["role_seqs"]))
        roles = tuple(_text(role) for role in _list(source["roles"])) if "roles" in source else ()
        if "role" in source:
            roles += (_text(source["role"]),)
        if host:
            for role in roles:
                _primitive(model, host, role)
        object_type = _text(source.get("object_type", source.get("supertype", "")))
        primitive = resolve_primitive(object_type, model) if object_type else None
        subtypes = (
            tuple(_text(item) for item in _list(source["subtypes"])) if "subtypes" in source else ()
        )
        flags = (source.get("exclusive", False), source.get("exhaustive", False), True, True)
        if any(type(flag) is not bool for flag in flags):
            raise _ShapeError("partition flags must be boolean")
        base = replace(
            base,
            roles=roles,
            role_refs=role_refs,
            sequences=sequences,
            object_type=object_type,
            subtypes=subtypes,
            flags=flags,
        )
        if "bound" in source:
            minimum, maximum, lo, hi = _bounds(source["bound"], "Integer")
            base = replace(base, minimum=minimum, maximum=maximum, flags=(*flags[:2], lo, hi))
        if "allowed" in source:
            # Enum identity does not coerce literals into the subject's type.
            base = replace(
                base, allowed=tuple(_scalar(value, None) for value in _list(source["allowed"]))
            )
        raw_ranges = (
            [source["range"]]
            if "range" in source
            else _list(source["ranges"])
            if "ranges" in source
            else []
        )
        if raw_ranges:
            ranges = tuple(_bounds(bounds, primitive) for bounds in raw_ranges)
            base = replace(base, ranges=ranges)
            if len(ranges) == 1:
                lo, hi, left, right = ranges[0]
                base = replace(base, minimum=lo, maximum=hi, flags=(*base.flags[:2], left, right))
        if family == "value-comparison":
            operator = _text(source.get("operator"))
            if operator not in (*_ORDERING, "=", "!="):
                raise _ShapeError("unknown comparison operator")
            left, right = source["role_a"], source["role_b"]
            first = _operand(left, model, fact_type)
            second = _operand(right, model, fact_type, first.primitive)
            if first.kind == "literal":
                first = _operand(left, model, fact_type, second.primitive)
            clock = time_relative_operand(source, fact_type)
            if clock is not None:
                if left == clock:
                    first = replace(first, kind="clock")
                else:
                    second = replace(second, kind="clock")
            base = replace(
                base,
                operator=operator,
                operands=(first, second),
                literal=next(
                    (item.literal for item in (first, second) if item.kind == "literal"), None
                ),
            )
        if family == "guarded":
            atoms = tuple(_atom(value, model) for value in _list(source.get("antecedent")))
            consequent = _mapping(source.get("consequent"))
            kinds = tuple(
                key for key in ("comparison", "atom", "absence", "exists") if key in consequent
            )
            if len(kinds) != 1 or not atoms:
                raise _ShapeError("a guarded constraint needs one consequent")
            kind = kinds[0]
            base = replace(base, consequent_kind=kind, antecedent=atoms)
            if kind not in {"comparison", "exists"}:
                base = replace(base, consequent=(_atom(consequent[kind], model),))
            elif kind == "comparison":
                comparison = _mapping(consequent[kind])
                primitives = {}
                for atom in atoms:
                    for _, term in atom.bindings:
                        if term.kind == "variable":
                            primitives.setdefault(term.variable, term.primitive)
                terms = tuple(comparison[key] for key in ("left", "right"))
                operands = []
                for index, term in enumerate(terms):
                    own = primitives.get(term, "") if isinstance(term, str) else ""
                    other = terms[1 - index]
                    other_primitive = primitives.get(other, "") if isinstance(other, str) else ""
                    # A bound variable keeps its role's primitive, even when
                    # untyped. Only literals borrow the other operand's type.
                    is_bound = isinstance(term, str) and term in primitives
                    converted = _guarded_term(
                        term,
                        primitives,
                        own if is_bound else other_primitive,
                    )
                    if (
                        converted.kind == "literal"
                        and not converted.tagged
                        and isinstance(other, str)
                        and other in primitives
                    ):
                        parsed = checker._literal(term, other_primitive or None, legacy=False)
                        valid = parsed is not checker._INVALID_LITERAL
                        converted = replace(
                            converted,
                            literal=(
                                canonical_scalar(parsed, other_primitive or None)
                                or _scalar(parsed, None)
                            )
                            if valid
                            else None,
                            valid=valid,
                        )
                    operands.append(converted)
                operator = _text(comparison.get("operator"))
                if operator not in (*_ORDERING, "=", "!="):
                    raise _ShapeError("unknown comparison operator")
                base = replace(base, operator=operator, operands=tuple(operands))
            else:
                exists = _mapping(consequent[kind])
                exists_atoms = tuple(_atom(value, model) for value in _list(exists.get("atoms")))
                primitives = {}
                for atom in (*atoms, *exists_atoms):
                    for _, term in atom.bindings:
                        if term.kind == "variable":
                            primitives.setdefault(term.variable, term.primitive)
                where_rows = []
                where_value = exists.get("where")
                where_comparisons = [] if where_value is None else _list(where_value)
                for comparison_value in where_comparisons:
                    comparison = _mapping(comparison_value)
                    operator = _text(comparison.get("operator"))
                    if operator not in (*_ORDERING, "=", "!="):
                        raise _ShapeError("unknown exists where operator")
                    left = _guarded_term(comparison.get("left"), primitives)
                    right = _guarded_term(comparison.get("right"), primitives)
                    where_rows.append((operator, left, right))
                base = replace(
                    base,
                    exists_atoms=exists_atoms,
                    exists_where=tuple(where_rows),
                )
        if family == "textual":
            base = replace(base, expression=_text(source.get("expression", "")))
        elif not checker._is_implemented(source, fact_type):
            raise _ShapeError("constraint has no implemented shape")
        base = replace(
            base,
            variant=constraint_variant(source, fact_type),
            scope_fact_types=tuple(checker._scope_fact_types(source, family, model, fact_type)),
        )
        if base.operator in _ORDERING and any(
            item.kind == "literal"
            and not item.primitive
            and item.literal is not None
            and item.literal.kind == "string"
            for item in base.operands
        ):
            raise _Refused("untyped-string-ordering")
        if (
            raw_ranges
            and primitive is None
            and any(
                value is not None and value.kind == "string"
                for bounds in base.ranges
                for value in bounds[:2]
            )
        ):
            raise _Refused("untyped-string-ordering")
        return base
    except _Refused as error:
        refusal = _refusal(base.ref, str(error))
    except (KeyError, TypeError, ValueError, AttributeError, OverflowError):
        refusal = _refusal(base.ref, "malformed-constraint")
    return replace(base, refused=refusal.reason)


def _roster(object_type_id: str, values, model: Model, location: str) -> IRRoster:
    primitive = resolve_primitive(object_type_id, model)
    members, refusals = [], []
    for index, value in enumerate(values):
        scalar = canonical_scalar(value, primitive)
        members.append(None if isinstance(scalar, Opaque) else scalar)
        if scalar is None or isinstance(scalar, Opaque):
            refusals.append(_refusal(f"{location}[{index}]", _reason(value, primitive)))
    return IRRoster(object_type_id, tuple(members), tuple(refusals))


def universe_of(object_type_id: str, model: Model, population: Any) -> IRRoster:
    """The production universe walk, retaining every occurrence and its order."""
    return _roster(
        object_type_id,
        checker._instance_values_of(object_type_id, model, population),
        model,
        f"universe[{object_type_id}]",
    )


def _input_refusals(
    constraints, object_types, fact_types, relations, rosters
) -> list[IRConstraint]:
    """Mark unrepresentable inputs without evaluating a predicate or a join.

    Unresolved typing alone is not a string-ordering refusal: an admitted
    untyped numeric column is still numeric. Index the actual scalar domains
    once and retain all rows, including refused cells.
    """
    by_fact = {row.fact_type: row for row in relations}
    by_roster = {row.object_type: row for row in rosters}
    primitives = {row.id: row.primitive for row in object_types}
    role_types = {}
    string_slots = set()
    for fact in fact_types:
        for index, role in enumerate(fact.roles):
            slot = (fact.id, role.name)
            role_types[slot] = role.object_type
            if not role.primitive and any(
                row[index] is not None and row[index].kind == "string"
                for row in by_fact[fact.id].rows
            ):
                string_slots.add(slot)
    result = []
    for constraint in constraints:
        reason = constraint.refused
        slots = set(constraint.role_refs)
        slots.update((constraint.fact_type, role) for role in constraint.roles)
        slots.update(
            (item.fact_type, item.role) for item in constraint.operands if item.kind == "role"
        )
        slots.update(slot for sequence in constraint.sequences for slot in sequence)
        slots.update(
            (atom.fact_type, role)
            for atom in (*constraint.antecedent, *constraint.consequent, *constraint.exists_atoms)
            for role, _term in atom.bindings
        )
        if not slots:
            slots.update(
                (fact.id, role.name)
                for fact in fact_types if fact.id in constraint.scope_fact_types
                for role in fact.roles
            )
        types = {role_types[slot] for slot in slots if slot in role_types}
        types.update((constraint.object_type, *constraint.subtypes))
        bad = [
            failure
            for ft in constraint.scope_fact_types
            for failure in by_fact[ft].refusals
            if failure.reason != "opaque-value"
            or (ft, failure.location.rpartition(".")[2]) in slots
        ]
        bad += [
            failure
            for target in types
            if target in by_roster
            for failure in by_roster[target].refusals
            if failure.reason != "opaque-value" or not slots
        ]
        if not reason and bad:
            reason = bad[0].reason
        if (
            not reason
            and constraint.operator in _ORDERING
            and all(operand.valid for operand in constraint.operands)
            and not any(operand.kind == "clock" for operand in constraint.operands)
        ):
            for index, operand in enumerate(constraint.operands):
                effective_primitive = operand.primitive
                if constraint.family == "value-comparison" and constraint.fact_type:
                    effective_primitive = (
                        effective_primitive or constraint.operands[1 - index].primitive
                    )
                if effective_primitive:
                    continue
                if operand.kind == "role" and (operand.fact_type, operand.role) in string_slots:
                    reason = "untyped-string-ordering"
                if operand.kind == "variable":
                    first = next(
                        (
                            (atom.fact_type, role)
                            for atom in constraint.antecedent
                            for role, term in atom.bindings
                            if term.kind == "variable" and term.variable == operand.variable
                        ),
                        None,
                    )
                    if first in string_slots:
                        reason = "untyped-string-ordering"
        if not reason and constraint.ranges:
            if constraint.role_refs:
                has_strings = bool(set(constraint.role_refs) & string_slots)
            else:
                target = by_roster.get(constraint.object_type)
                has_strings = (
                    not primitives.get(constraint.object_type)
                    and target is not None
                    and any(item is not None and item.kind == "string" for item in target.members)
                )
            if has_strings:
                reason = "untyped-string-ordering"
        if reason and not constraint.refused:
            _refusal(constraint.ref, reason)
            constraint = replace(constraint, refused=reason)
        result.append(constraint)
    return result


def adapt_snapshot(
    model: Model,
    population: Population,
    *,
    effective_facts: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
) -> SnapshotIR:
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    fact_source = population.facts if effective_facts is None else effective_facts
    effective_population = _ObservedPopulation(
        covers=population.covers,
        instances=population.instances,
        facts=fact_source,
    )
    object_types = []
    for source in model.object_types:
        identity = source["id"]
        closure = checker._descendant_closure(identity, model)
        denoting = checker._denoting_types(closure, model) if source["kind"] == "value" else set()
        rule = source.get("derivation_rule")
        object_types.append(
            IRObjectType(
                identity,
                source["kind"],
                resolve_primitive(identity, model) or "",
                tuple(sorted(closure)),
                tuple(sorted(denoting)),
                source.get("derivation", "asserted"),
                rule if isinstance(rule, str) else "",
            )
        )
    fact_types, relations, constraints, derivations = [], [], [], []
    document = model.model_dump()
    dependencies = derivation_dependencies(document)
    structured = bool(dependencies)
    for source in model.fact_types:
        identity = source["id"]
        roles = tuple(
            IRRole(
                role["role_name"],
                role["object_type"],
                resolve_primitive(role["object_type"], model) or "",
            )
            for role in source.get("roles", [])
        )
        rule = source.get("derivation_rule")
        has_rule = isinstance(rule, dict)
        derivation = source.get("derivation", "asserted")
        selected = (
            "computed-extension"
            if has_rule and derivation == "semiderived"
            else "empty"
            if has_rule and identity not in population.covers
            else "claimed"
        )
        fact_types.append(
            IRFactType(
                identity,
                roles,
                identity in population.covers,
                derivation,
                has_rule,
                selected,
                rule if isinstance(rule, str) else "",
            )
        )
        rows, refusals = [], []
        for index, fact in enumerate(fact_source.get(identity, [])):
            converted = []
            missing_role = False
            for role in roles:
                if role.name not in fact:
                    missing_role = True
                    continue
                value = fact[role.name]
                scalar = canonical_scalar(value, role.primitive or None)
                if isinstance(scalar, Opaque):
                    scalar = None
                converted.append(scalar)
                if scalar is None:
                    refusals.append(
                        _refusal(
                            f"facts[{identity}][{index}].{role.name}",
                            _reason(value, role.primitive or None),
                        )
                    )
            if not missing_role:
                rows.append(tuple(converted))
        relations.append(IRRelation(identity, tuple(rows), tuple(refusals)))
        constraints.extend(
            adapt_constraint(constraint, source, positional_constraint_ref(identity, index), model)
            for index, constraint in enumerate(source.get("constraints", []))
        )
        if has_rule:
            for clause in iter_derivation_clauses(rule):
                derivations.append(
                    IRDerivation(
                        identity,
                        tuple(
                            (name, _term(term, _primitive(model, identity, name), derivation=True))
                            for name, term in clause["head"].items()
                        ),
                        tuple(_atom(atom, model, derivation=True) for atom in clause["body"]),
                        tuple(_atom(atom, model, derivation=True) for atom in clause.get("negate", [])),
                        tuple(sorted(dependencies[identity])),
                        tuple(tuple(sorted(component)) for component in body_components(clause)),
                        (),
                    )
                )
                derivations[-1] = replace(derivations[-1], refusals=_rule_refusals(derivations[-1]))
    constraints.extend(
        adapt_constraint(constraint, None, positional_constraint_ref(None, index), model)
        for index, constraint in enumerate(model.constraints)
    )
    rosters = tuple(universe_of(source.id, model, effective_population) for source in object_types)
    constraints = _input_refusals(constraints, object_types, fact_types, relations, rosters)
    explicit = tuple(
        _roster(identity, values, model, f"instances[{identity}]")
        for identity, values in population.instances.items()
    )
    refusals = tuple(item for owner in (*relations, *rosters, *explicit) for item in owner.refusals)
    refusals += tuple(item for rule in derivations for item in rule.refusals)
    refusals += tuple(
        IRRefusal(constraint.ref, constraint.refused)
        for constraint in constraints
        if constraint.refused
    )
    return SnapshotIR(
        tuple(object_types),
        tuple(fact_types),
        tuple(relations),
        rosters,
        tuple(constraints),
        not any(item.reason == "non-finite-number" for item in refusals),
        tuple(population.covers),
        explicit,
        tuple(derivations),
        tuple(head for component in derivation_strata(document) for head in component) if structured else (),
        refusals,
    )


def _json_kind(value: Any) -> str:
    if value is None:
        return "null"
    if type(value) is bool:
        return "boolean"
    if isinstance(value, (int, float)):
        return "number"
    return "string"


def adapt_snapshot_observed(
    model: Model,
    population: Population,
    *,
    effective_facts: Mapping[str, Sequence[Mapping[str, Any]]] | None = None,
    effective_lineage: Mapping[str, Sequence[tuple[tuple[str | int, ...], ...]]] | None = None,
) -> AdaptedSnapshot:
    """Retain the exact value origins beside the immutable semantic snapshot."""
    fact_source = population.facts if effective_facts is None else effective_facts
    snapshot = adapt_snapshot(model, population, effective_facts=effective_facts)
    fact_types = {str(row.get("id")): row for row in model.fact_types}
    relations = {row.fact_type: row for row in snapshot.relations}
    origins: list[ValueOrigin] = []
    for fact_type_id, facts in fact_source.items():
        fact_type = fact_types.get(str(fact_type_id), {})
        role_rows = tuple(fact_type.get("roles") or ())
        role_names = tuple(str(role.get("role_name")) for role in role_rows)
        rule = fact_type.get("derivation_rule")
        # ``effective_facts=None`` is the admitted population by contract, even
        # for a semiderived fact type.  Only the explicit effective extension
        # passed by checker.check may create derived origins.
        derived = (
            effective_facts is not None
            and isinstance(rule, dict)
            and fact_type.get("derivation") == "semiderived"
        )
        if derived and effective_lineage is None:
            raise ValueError("derived origin lineage is required with effective facts")
        lineage_rows = (
            tuple(effective_lineage.get(str(fact_type_id), ()))
            if effective_lineage is not None
            else ()
        )
        relation = relations.get(str(fact_type_id))
        relation_index = 0
        for index, fact in enumerate(facts):
            if relation is None or any(role_name not in fact for role_name in role_names):
                continue
            if relation_index >= len(relation.rows):
                raise ValueError(f"origin relation drift for {fact_type_id!r}")
            relation_row = relation.rows[relation_index]
            relation_index += 1
            dependency_paths = lineage_rows[index] if index < len(lineage_rows) else ()
            if derived and not dependency_paths:
                raise ValueError(f"derived origin lineage missing for {fact_type_id!r}[{index}]")
            for role_index, role_name in enumerate(role_names):
                value = fact[role_name]
                scalar = relation_row[role_index]
                if scalar is None or isinstance(scalar, Opaque):
                    continue
                origins.append(
                    ValueOrigin(
                        source="derived" if derived else "admitted",
                        path=("facts", str(fact_type_id), index, role_name),
                        scalar=scalar,
                        json_kind=_json_kind(value),
                        admitted_value=value,
                        derivation_fact_type=str(fact_type_id) if derived else None,
                        dependency_paths=dependency_paths if derived else (),
                    )
                )
    for object_type_id, values in population.instances.items():
        primitive = resolve_primitive(str(object_type_id), model)
        for index, value in enumerate(values):
            scalar = canonical_scalar(value, primitive)
            if scalar is None or isinstance(scalar, Opaque):
                continue
            origins.append(
                ValueOrigin(
                    source="admitted",
                    path=("instances", str(object_type_id), index),
                    scalar=scalar,
                    json_kind=_json_kind(value),
                    admitted_value=value,
                    derivation_fact_type=None,
                    dependency_paths=(),
                )
            )
    # Value-comparison witnesses intentionally retain both operands.  A
    # literal operand is admitted model input rather than a population cell;
    # preserve that exact JSON token here so projection never reconstructs it
    # from the canonical numeric coordinate.
    constraint_sources: dict[str, tuple[dict[str, Any], tuple[str | int, ...]]] = {}
    for fact_type in model.fact_types:
        fact_type_id = str(fact_type.get("id"))
        for index, source in enumerate(fact_type.get("constraints") or ()):
            constraint_sources[positional_constraint_ref(fact_type_id, index)] = (
                source,
                ("fact_types", fact_type_id, "constraints", index),
            )
    for index, source in enumerate(model.constraints):
        constraint_sources[positional_constraint_ref(None, index)] = (
            source,
            ("constraints", index),
        )
    for constraint in snapshot.constraints:
        if constraint.family != "value-comparison":
            continue
        source_row = constraint_sources.get(constraint.ref)
        if source_row is None:
            continue
        source, base_path = source_row
        for field, operand in zip(("role_a", "role_b"), constraint.operands, strict=True):
            if operand.kind != "literal" or operand.literal is None:
                continue
            raw = source.get(field)
            tagged = isinstance(raw, dict) and set(raw) == {"literal"}
            if tagged:
                raw = raw["literal"]
            admitted = checker._literal(raw, operand.primitive or None, legacy=not tagged)
            if admitted is checker._INVALID_LITERAL:
                if tagged:
                    continue
                # Legacy untagged operands that are not role names are literal
                # strings even when the opposite operand has a numeric type.
                # Mirror _operand's admitted fallback exactly so projection can
                # recover the original model token without reconstructing it.
                admitted = raw
            origins.append(
                ValueOrigin(
                    source="admitted",
                    path=(*base_path, field),
                    scalar=operand.literal,
                    json_kind=_json_kind(admitted),
                    admitted_value=admitted,
                    derivation_fact_type=None,
                    dependency_paths=(),
                )
            )
    observation_refusals = list(snapshot.refusals)
    applicable = set(applicable_scope_ids(model, population))
    for constraint in snapshot.constraints:
        if (
            constraint.family != "value-comparison"
            or constraint.operator not in _ORDERING
            or not any(operand.primitive == "" for operand in constraint.operands)
        ):
            continue
        valid, pairs = semantic_spec.value_comparison_pairs(constraint, snapshot)
        if valid and any(left.kind == "string" or right.kind == "string" for left, right in pairs):
            observation_refusals.append(IRRefusal(constraint.ref, "untyped-string-ordering"))
            applicable.add("applicability:adapter:n-a:untyped-string-ordering")
    return AdaptedSnapshot(
        snapshot=snapshot,
        observation=SnapshotObservation(
            origins=tuple(origins),
            production_dimensions=PRODUCTION_DIMENSIONS,
            refusals=tuple(observation_refusals),
            applicable_scope_ids=tuple(sorted(applicable)),
            fact_occurrences=tuple(
                (str(fact_type_id), index)
                for fact_type_id, rows in population.facts.items()
                for index in range(len(rows))
            ),
            constraint_subjects=tuple(
                (constraint.ref, constraint.scope_fact_types)
                for constraint in snapshot.constraints
            ),
        ),
    )


def correspondence_scope(
    adapted: AdaptedSnapshot,
) -> tuple[str, tuple[IRRefusal, ...]]:
    """Fail closed when any admitted value needed by the snapshot was refused."""
    refusals = adapted.observation.refusals
    return ("refused" if refusals else "in-scope", refusals)
