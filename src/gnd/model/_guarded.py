"""Guarded validation added by the guarded-rule milestones (GW0-GW1, GC1-GC3).

A separate home inside the ``gnd.model`` package so ``_validation`` stays under
its RF6 size ceiling (main CI repair, 2026-11-16). The definitions below moved
verbatim from ``gnd.model._validation``, which imports them back and registers
them in ``_SEMANTIC_RULES`` in their original order. They call seven pinned
``_validation`` helpers through :data:`_registered`, which ``_validation`` fills
at import time, so this module never imports ``_validation`` back (the RF8
graph check forbids the cycle, as for ``gnd.model._unattended``).
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from gnd.atoms import atom_bind
from gnd.errors import ValidationIssue
from gnd.terms import (
    DEFAULT_LIMITS,
    MAX_MEMBERSHIP_ITEMS,
    MEMBERSHIP_OPERATORS,
    NUMERIC_PRIMITIVES,
    analyze_term,
    compile_membership,
    membership_domain,
    term_variables,
    valid_duration,
)
from gnd.universe import supertype_parents as _supertype_parents

#: The pinned ``_validation`` helpers the moved definitions call, registered by
#: ``gnd.model._validation`` once they are defined.
_registered: dict[str, Callable[..., Any]] = {}


def _filter_derivation_term_issues(*args, **kwargs):
    return _registered['_filter_derivation_term_issues'](*args, **kwargs)


def _guarded_literal_matches_primitive(*args, **kwargs):
    return _registered['_guarded_literal_matches_primitive'](*args, **kwargs)


def _guarded_primitives_compatible(*args, **kwargs):
    return _registered['_guarded_primitives_compatible'](*args, **kwargs)


def _iter_guarded_atoms(*args, **kwargs):
    return _registered['_iter_guarded_atoms'](*args, **kwargs)


def _iter_guarded_constraints(*args, **kwargs):
    return _registered['_iter_guarded_constraints'](*args, **kwargs)


def _primitive_maps(*args, **kwargs):
    return _registered['_primitive_maps'](*args, **kwargs)


def _variable_name(*args, **kwargs):
    return _registered['_variable_name'](*args, **kwargs)


def _guarded_alternatives(consequent):
    """Yield each single consequent and its document path suffix."""
    if not isinstance(consequent, dict):
        return
    alternatives = consequent.get("any_of")
    if isinstance(alternatives, list):
        for index, alternative in enumerate(alternatives):
            if isinstance(alternative, dict):
                yield f".consequent.any_of[{index}]", alternative
    else:
        yield ".consequent", consequent


def _iter_guarded_scopes(doc):
    """Use the shared antecedent with one consequent's local variable scope."""
    for path, constraint in _iter_guarded_constraints(doc):
        for prefix, consequent in _guarded_alternatives(constraint.get("consequent")):
            yield path, prefix, {**constraint, "consequent": consequent}


def _iter_guarded_comparisons(consequent, where=None):
    if isinstance(where, list):
        for index, comparison in enumerate(where):
            if isinstance(comparison, dict):
                yield f".where[{index}]", comparison
    for prefix, alternative in _guarded_alternatives(consequent):
        direct = alternative.get("comparison")
        if isinstance(direct, dict):
            yield f"{prefix}.comparison", direct
        exists = alternative.get("exists")
        if isinstance(exists, dict) and isinstance(exists.get("where"), list):
            for index, comparison in enumerate(exists["where"]):
                if isinstance(comparison, dict):
                    yield f"{prefix}.exists.where[{index}]", comparison


def _iter_guarded_memberships(guard):
    for path, comparison in _iter_guarded_comparisons(guard.get("consequent"), guard.get("where")):
        right = comparison.get("right")
        if comparison.get("operator") in MEMBERSHIP_OPERATORS and isinstance(right, list):
            yield comparison.get("left"), right, path


def _iter_guarded_comparison_terms(path, comparison):
    if "left" in comparison:
        yield f"{path}.left", comparison["left"]
    if "right" in comparison:
        right = comparison["right"]
        if comparison.get("operator") in MEMBERSHIP_OPERATORS and isinstance(right, list):
            for index, member in enumerate(right[:MAX_MEMBERSHIP_ITEMS]):
                yield f"{path}.right[{index}]", member
        else:
            yield f"{path}.right", right


_GUARDED_LITERAL_DOMAIN_WORK = 100_000


def _rule_guarded_literal_domain(doc: dict[str, Any]) -> list[ValidationIssue]:
    """Diagnose literal bindings excluded by a declared role or object domain."""
    from itertools import chain

    from gnd.model_index import ModelIndex
    from gnd.model_queries import _identifying_id, _resolve_reference
    from gnd.semantic_ir import Scalar
    from gnd.semantic_spec import scalar_identical, scalar_range_state
    from gnd.values import canonical_scalar

    guards = list(_iter_guarded_constraints(doc))
    if not guards:
        return []
    fact_types = doc.get("fact_types")
    object_types = doc.get("object_types")
    if not isinstance(fact_types, list) or not isinstance(object_types, list):
        return []
    facts = [
        dict(fact, roles=[role for role in fact["roles"] if isinstance(role, dict)])
        for fact in fact_types
        if isinstance(fact, dict) and isinstance(fact.get("roles"), list)
    ]
    objects = [
        obj for obj in object_types if isinstance(obj, dict)
        and isinstance(obj.get("subtype_of", []), list)
        and isinstance(obj.get("reference", {}), dict)
    ]
    index = ModelIndex(None, {"fact_types": facts, "object_types": objects})
    roles = index.role_object_types()
    objects_by_id = index.object_types_by_id()
    parents = _supertype_parents({"object_types": objects})
    by_role: dict[tuple[str, str], list[tuple[str, dict]]] = {}
    by_type: dict[str, list[tuple[str, dict]]] = {}
    for position, domain in enumerate(doc["constraints"]):
        if not isinstance(domain, dict) or domain.get("type") != "value":
            continue
        target = domain.get("object_type")
        if not isinstance(target, str) or target not in objects_by_id:
            continue
        ref = domain.get("role_ref")
        entry = (f"constraints[{position}]", domain)
        if ref is None:
            by_type.setdefault(target, []).append(entry)
        elif isinstance(ref, dict):
            fact, role = ref.get("fact_type"), ref.get("role")
            if isinstance(fact, str) and isinstance(role, str):
                by_role.setdefault((fact, role), []).append(entry)
    if not by_type and not by_role:
        return []

    remaining = _GUARDED_LITERAL_DOMAIN_WORK
    issues: list[ValidationIssue] = []
    type_domains: dict[str, list[list[tuple[str, dict]]]] = {}
    tested: dict[tuple[str, str, str], bool] = {}

    def charge() -> None:
        nonlocal remaining
        remaining -= 1
        if remaining < 0:
            raise _GuardedLiteralDomainLimit

    def domains_for_type(role_type: str) -> list[list[tuple[str, dict]]]:
        if role_type not in type_domains:
            pending = [role_type]
            if by_type:
                denoting = _resolve_reference(role_type, objects_by_id, parents, set(), _identifying_id)
                if denoting is not None:
                    pending.append(denoting)
            seen = set()
            while pending:
                charge()
                current = pending.pop()
                if current not in seen:
                    seen.add(current)
                    pending.extend(parents.get(current, ()))
            type_domains[role_type] = [
                by_type[target] for target in sorted(seen) if target in by_type
            ]
        return type_domains[role_type]

    def excluded(value: Any, raw: Scalar, domain: dict) -> bool:
        allowed = domain.get("allowed")
        if isinstance(allowed, list) and allowed:
            for item in allowed:
                charge()
                scalar = canonical_scalar(item, None)
                if not isinstance(scalar, Scalar) or scalar_identical(raw, scalar):
                    return False
            return True
        ranges = [domain["range"]] if "range" in domain else domain.get("ranges")
        if not isinstance(ranges, list) or not ranges:
            return False
        primitive = index.primitive(domain["object_type"], variant="truthy")
        scalar = canonical_scalar(value, primitive)
        if not isinstance(scalar, Scalar):
            return False
        for bounds in ranges:
            charge()
            if not isinstance(bounds, dict):
                return False
            lower, upper = bounds.get("min"), bounds.get("max")
            minimum = canonical_scalar(lower, primitive) if lower is not None else None
            maximum = canonical_scalar(upper, primitive) if upper is not None else None
            lo, hi = bounds.get("min_inclusive", True), bounds.get("max_inclusive", True)
            if (minimum is not None and not isinstance(minimum, Scalar)
                or maximum is not None and not isinstance(maximum, Scalar)
                or lower is not None and minimum is None or upper is not None and maximum is None
                or type(lo) is not bool or type(hi) is not bool):
                return False
            if scalar_range_state(scalar, minimum, maximum, lo, hi) != 0:
                return False
        return True

    def literals(guard):
        sites = {}
        for suffix, atom in _iter_guarded_atoms(guard):
            if not isinstance(atom, dict) or not isinstance(atom.get("fact_type"), str):
                continue
            fact = atom["fact_type"]
            for role, value in atom_bind(atom).items():
                variable = _variable_name(value)
                if variable is None:
                    yield f"{suffix}.bind[{role}]", fact, role, value
                elif suffix.startswith(".antecedent[") or ".exists.atoms[" in suffix:
                    scope = "" if suffix.startswith(".antecedent[") else suffix.split(".exists.", 1)[0]
                    sites.setdefault((scope, variable), set()).add((fact, role))
        for left, right, prefix in _iter_guarded_memberships(guard):
            variable = _variable_name(left)
            scope = prefix.split(".exists.", 1)[0] if ".exists." in prefix else ""
            roles_for_left = sorted(sites.get(("", variable), set()) | sites.get((scope, variable), set()))
            for index, member in enumerate(right[:MAX_MEMBERSHIP_ITEMS]):
                if isinstance(member, dict) and set(member) in ({"date"}, {"duration_days"}):
                    member = next(iter(member.values()))
                for fact, role in roles_for_left:
                    yield f"{prefix}.right[{index}]", fact, role, member

    for ref, guard in guards:
        for suffix, fact, role, value in literals(guard):
            role_type = roles.get(fact, {}).get(role)
            if role_type not in objects_by_id or _variable_name(value) is not None:
                continue
            if type(value) not in (bool, int, float, str):
                continue
            raw = canonical_scalar(value, None)
            if not isinstance(raw, Scalar):
                continue
            path = f"{ref}{suffix}"
            try:
                domains = chain(
                    by_role.get((fact, role), ()), chain.from_iterable(domains_for_type(role_type))
                )
                restricting = []
                for domain_ref, domain in domains:
                    charge()
                    key = domain_ref, raw.identity_kind, raw.token
                    if key not in tested:
                        tested[key] = excluded(value, raw, domain)
                    if tested[key]:
                        restricting.append(domain_ref)
            except _GuardedLiteralDomainLimit:
                issues.append(ValidationIssue(
                    path=path, severity="warning",
                    rule_id="semantic:guarded-literal-domain-work-limit",
                    message="Guarded literal domain validation reached its work limit.",
                ))
                return issues
            if restricting:
                issues.append(ValidationIssue(
                    path=path, severity="warning",
                    rule_id="semantic:guarded-literal-outside-domain",
                    message=f"Literal lies outside the value domain declared by {', '.join(restricting)}.",
                ))
    return issues


class _GuardedLiteralDomainLimit(Exception):
    """The model-level domain lint budget was exhausted."""


def _rule_guarded_filters(doc: dict[str, Any]) -> list[ValidationIssue]:
    issues = []
    guards = [(path, guard) for path, guard in _iter_guarded_constraints(doc)
              if "negate" in guard or "where" in guard]
    if not guards or not all(isinstance(doc.get(field, []), list)
                             for field in ("fact_types", "object_types")):
        return issues
    role_types, primitives = _primitive_maps(doc)
    for path, guard in guards:
        scopes: dict[str, set[str]] = {}
        for suffix, atom in _iter_guarded_atoms(guard):
            if not suffix.startswith(".antecedent[") or not isinstance(atom, dict):
                continue
            for role, term in atom_bind(atom).items():
                variable = _variable_name(term)
                if variable is not None:
                    object_type = role_types.get(str(atom.get("fact_type")), {}).get(str(role))
                    choices = scopes.setdefault(variable, set())
                    primitive = primitives.get(object_type or "")
                    if primitive is not None:
                        choices.add(primitive)
        types = {
            variable: next(iter(choices)) if len(choices) == 1 else "Number"
            for variable, choices in scopes.items()
            if choices and (len(choices) == 1 or choices <= NUMERIC_PRIMITIVES)
        }
        terms = []
        for suffix, atom in _iter_guarded_atoms(guard):
            if not suffix.startswith(".negate[") or not isinstance(atom, dict):
                continue
            fact_type = str(atom.get("fact_type"))
            for role, term in atom_bind(atom).items():
                location = f"{suffix}.bind[{role}]"
                terms.append((location, term))
                object_type = role_types.get(fact_type, {}).get(str(role))
                primitive = primitives.get(object_type or "")
                variable = _variable_name(term)
                declared = scopes.get(variable, ())
                literal_matches = (valid_duration(term) if primitive == "Duration"
                                   else _guarded_literal_matches_primitive(primitive, term))
                if primitive is not None and (
                    (declared and any(not _guarded_primitives_compatible(primitive, bound) for bound in declared))
                    or (variable is None and not literal_matches)
                ):
                    issues.append(ValidationIssue(
                        path=f"{path}{location}", message="Negative binding has an incompatible primitive.",
                        rule_id="semantic:guarded-binding-type",
                    ))
        for suffix, comparison in _iter_guarded_comparisons(None, guard.get("where")):
            terms.extend(_iter_guarded_comparison_terms(suffix, comparison))
        for suffix, term in terms:
            unbound = set(term_variables(term)) - scopes.keys()
            if unbound:
                issues.append(ValidationIssue(
                    path=f"{path}{suffix}",
                    message=f"Guarded filter variables require a positive binding: {sorted(unbound)}.",
                    rule_id="semantic:guarded-filter-unbound",
                ))
        for suffix, comparison in _iter_guarded_comparisons(None, guard.get("where")):
            if comparison.get("operator") in MEMBERSHIP_OPERATORS:
                issues.extend(_membership_comparison_issues(f"{path}{suffix}", comparison, types))
                continue
            left = analyze_term(comparison.get("left"), types)
            right = analyze_term(comparison.get("right"), types)
            for side, term in (("left", left), ("right", right)):
                if term.issue is not None and not (set(term.variables) - scopes.keys()):
                    issues.append(ValidationIssue(
                        path=f"{path}{suffix}.{side}", message="Invalid guarded filter comparison term.",
                        rule_id=term.issue,
                    ))
            if (left.primitive and right.primitive
                    and not _guarded_primitives_compatible(left.primitive, right.primitive)):
                issues.append(ValidationIssue(
                    path=f"{path}{suffix}", message="Guarded filter operands have incompatible types.",
                    rule_id="semantic:term-comparison-type",
                ))
    return issues


def _membership_comparison_issues(path, comparison, variable_primitives):
    left = analyze_term(comparison.get("left"), variable_primitives, limits=DEFAULT_LIMITS)
    if left.issue is not None:
        yield ValidationIssue(path=f"{path}.left", message=f"membership term is invalid: {left.issue}", rule_id=left.issue)
    right = comparison.get("right")
    members = compile_membership(right)
    domain = membership_domain(left.primitive)
    if members is None or (domain is not None and domain != members.domain):
        yield ValidationIssue(
            path=f"{path}.right",
            message="Membership requires a non-empty homogeneous list of compatible literals.",
            rule_id="semantic:membership-list",
        )
    elif len(members.keys) < len(right):
        yield ValidationIssue(
            path=f"{path}.right",
            message="Membership list contains duplicate values.",
            severity="warning",
            rule_id="semantic:membership-duplicate",
        )


def _rule_derivation_membership(doc: dict[str, Any]) -> list[ValidationIssue]:
    return [
        issue
        for rule in ("semantic:membership-list", "semantic:membership-duplicate")
        for issue in _filter_derivation_term_issues(doc, rule_id=rule)
    ]
