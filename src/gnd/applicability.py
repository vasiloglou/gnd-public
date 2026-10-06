"""RF3 shared dependency home; algorithms retain predecessor semantics."""
from __future__ import annotations

from typing import TYPE_CHECKING

from gnd.branches import REGISTRY, Branch, constraint_variant

if TYPE_CHECKING:
    from gnd.documents import Model
    from gnd.population import Population


def applicable_scope_ids(model: Model, population: Population) -> tuple[str, ...]:
    """All outcomes owed by admitted input, independently of any proof declaration.

    This classifies the execution route without calling a verdict evaluator.
    Every outcome of each selected family/variant remains in the denominator,
    including the opposite result from the one the current data would produce.
    Shared applicability, composition and consumer obligations are unconditional.
    Structured semiderived extensions use the same effective fact view as check;
    otherwise a supplied surplus claim could change the selected proof route.
    """
    # Local imports keep the registry's descriptors usable during checker import.
    from gnd.address import positional_constraint_ref
    from gnd.errors import UnvalidatedPopulationError
    from gnd.extensions import effective_view
    from gnd.proof_bridge import adapt_phase1_slice
    from gnd.universe import scope_fact_types

    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)

    def carries_exact_term(value: object) -> bool:
        if isinstance(value, dict):
            if set(value) == {"fn", "args"}:
                return True
            return any(carries_exact_term(item) for item in value.values())
        if isinstance(value, list):
            return any(carries_exact_term(item) for item in value)
        return False

    def carries_float_term(value: object) -> bool:
        # A model using only Phase 3/4 exact functions (mod, add, ...) must
        # NOT mark Phase 5's float-only reasons applicable -- distinct from
        # carries_exact_term, which cannot tell the two families apart.
        from gnd.terms import FLOAT_FUNCTION_ARITY

        if isinstance(value, dict):
            if set(value) == {"fn", "args"} and value.get("fn") in FLOAT_FUNCTION_ARITY:
                return True
            return any(carries_float_term(item) for item in value.values())
        if isinstance(value, list):
            return any(carries_float_term(item) for item in value)
        return False

    from gnd.terms import TEMPORAL_REASONS, uses_temporal

    temporal_terms = uses_temporal(model)
    from gnd.universe import resolve_primitive

    duration_facts = {
        str(ft.get("id"))
        for ft in model.fact_types
        if any(
            resolve_primitive(str(role.get("object_type")), model) == "Duration"
            for role in ft.get("roles") or []
        )
    }
    exact_terms = carries_exact_term(model.model_dump(exclude={"warnings"}))
    float_terms = carries_float_term(model.model_dump(exclude={"warnings"}))
    aggregate_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and isinstance(rule.get("aggregate"), dict)
    }
    exact_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and (
            carries_exact_term({"where": rule.get("where"), "head": rule.get("head")})
            or str(fact_type.get("id")) in aggregate_heads
        )
    }
    changed = True
    while changed:
        changed = False
        for fact_type in model.fact_types:
            fact_type_id = str(fact_type.get("id"))
            rule = fact_type.get("derivation_rule")
            if fact_type_id in exact_heads or not isinstance(rule, dict):
                continue
            dependencies = {
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or []
                if isinstance(atom, dict)
            }
            if dependencies & exact_heads:
                exact_heads.add(fact_type_id)
                changed = True

    float_heads = {
        str(fact_type.get("id"))
        for fact_type in model.fact_types
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and carries_float_term({"where": rule.get("where"), "head": rule.get("head")})
    }
    changed = True
    while changed:
        changed = False
        for fact_type in model.fact_types:
            fact_type_id = str(fact_type.get("id"))
            rule = fact_type.get("derivation_rule")
            if fact_type_id in float_heads or not isinstance(rule, dict):
                continue
            dependencies = {
                str(atom.get("fact_type"))
                for key in ("body", "negate")
                for atom in rule.get(key) or []
                if isinstance(atom, dict)
            }
            if dependencies & float_heads:
                float_heads.add(fact_type_id)
                changed = True

    #: The four Phase 5 float-only reasons. A model that is merely
    #: term-capable (e.g. Phase 3/4's `mod`) must not mark these applicable --
    #: `term_capable` alone cannot distinguish the function family a specific
    #: constraint or derivation actually reads.
    FLOAT_ONLY_REASON_CODES = frozenset(
        {
            "term:div-zero",
            "term:sqrt-negative",
            "term:haversine-coordinate-range",
            "term:float-overflow",
        }
    )

    def applicable_row(
        row: Branch,
        *,
        term_capable: bool = exact_terms,
        aggregate_capable: bool = bool(aggregate_heads),
        float_capable: bool = float_terms,
        temporal_capable: bool = temporal_terms,
    ) -> bool:
        if row.reason_code == "reference-join-work-limit" and not model.reference_populations:
            return False
        if row.reason_code in TEMPORAL_REASONS:
            return temporal_capable
        if row.reason_code in FLOAT_ONLY_REASON_CODES:
            return float_capable
        aggregate_only = (
            row.surface == "derivation"
            and row.family == "extension"
            and row.semantic_branch.startswith("aggregate-")
        ) or (row.surface == "snapshot" and row.family == "guarded" and row.variant == "aggregate")
        if aggregate_only:
            return aggregate_capable
        exact_only = (
            row.surface == "derivation"
            and row.family == "extension"
            and row.semantic_branch.startswith("exact-")
        ) or (
            row.surface == "snapshot"
            and row.family == "guarded"
            and row.semantic_branch == "exact-success"
        )
        if exact_only and not term_capable:
            return False
        return term_capable or row.reason_code is None or not row.reason_code.startswith("term:")

    static_view_scope = "composition:derivation-view:static:applied"
    dynamic_view_scope = "composition:derivation-view:dynamic:applied"

    def dynamic_composition_row(row: Branch) -> bool:
        # Owed only when a step can refresh a dynamic structured head.
        return (row.surface, row.family) in {
            ("composition", "dynamic-refresh"),
            ("transition", "derived-change"),
            ("report", "transition-derived-changes"),
        }

    has_opaque = any(
        isinstance(value, dict) and set(value) == {"$opaque"}
        for rows in population.facts.values() for fact in rows for value in fact.values()
    )
    selected = {
        row.scope_id
        for row in REGISTRY
        if row.surface
        in {"applicability", "composition", "report", "experiment-feedback", "certification"}
        and row.scope_id not in {static_view_scope, dynamic_view_scope}
        and (has_opaque or row.scope_id not in {
            "applicability:adapter:n-a:opaque-value",
            "applicability:opaque:n-a:opaque-value",
        })
        and not dynamic_composition_row(row)
        and applicable_row(row)
    }
    view = effective_view(model, population)
    structured = any(isinstance(ft.get("derivation_rule"), dict) for ft in model.fact_types)
    if structured:
        derivation_variants = {
            str(ft.get("derivation"))
            for ft in model.fact_types
            if ft.get("derivation") in {"derived", "semiderived"}
            and ft.get("derivation_rule") is not None
        }
        exact_derivation_variants = {
            str(ft.get("derivation")) for ft in model.fact_types if str(ft.get("id")) in exact_heads
        }
        aggregate_derivation_variants = {
            str(ft.get("derivation"))
            for ft in model.fact_types
            if str(ft.get("id")) in aggregate_heads
        }
        float_derivation_variants = {
            str(ft.get("derivation")) for ft in model.fact_types if str(ft.get("id")) in float_heads
        }
        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "derivation"
            and row.variant in derivation_variants
            and applicable_row(
                row,
                term_capable=row.variant in exact_derivation_variants,
                aggregate_capable=row.variant in aggregate_derivation_variants,
                float_capable=row.variant in float_derivation_variants,
            )
        )
    if model.operations:
        has_preconditions = any(operation.get("preconditions") for operation in model.operations)
        has_dynamic_rules = any(operation.get("dynamic_rules") for operation in model.operations)
        exact_preconditions = any(
            str(atom.get("fact_type")) in exact_heads
            for operation in model.operations
            for obligation in operation.get("preconditions") or []
            for atom in obligation.get("require") or []
            if isinstance(atom, dict)
        )
        exact_dynamic_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in exact_heads
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        float_preconditions = any(
            str(atom.get("fact_type")) in float_heads
            for operation in model.operations
            for obligation in operation.get("preconditions") or []
            for atom in obligation.get("require") or []
            if isinstance(atom, dict)
        )
        float_dynamic_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in float_heads
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        structured_ids = {
            str(fact_type.get("id"))
            for fact_type in model.fact_types
            if isinstance(fact_type.get("derivation_rule"), dict)
        }
        derived_subject_rules = any(
            isinstance((subject := rule.get("subject")), dict)
            and str(subject.get("fact_type")) in structured_ids
            for operation in model.operations
            for rule in operation.get("dynamic_rules") or []
            if isinstance(rule, dict)
        )
        from gnd.model import derivation_classifications

        classifications = derivation_classifications(model.model_dump())
        dynamic_heads = any(row.stability == "dynamic" for row in classifications)

        def transition_row_is_applicable(row: Branch) -> bool:
            if row.family == "precondition" and not has_preconditions:
                return False
            if row.family == "dynamic-rule" and not has_dynamic_rules:
                return False
            if (
                row.family == "dynamic-rule"
                and row.variant.startswith("derived-")
                and not derived_subject_rules
            ):
                return False
            if dynamic_composition_row(row) and not dynamic_heads:
                return False
            term_capable = (
                exact_preconditions
                if row.family == "precondition"
                else exact_dynamic_rules
                if row.family == "dynamic-rule"
                else False
            )
            float_capable = (
                float_preconditions
                if row.family == "precondition"
                else float_dynamic_rules
                if row.family == "dynamic-rule"
                else False
            )
            return applicable_row(row, term_capable=term_capable, float_capable=float_capable)

        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "transition" and transition_row_is_applicable(row)
        )
        if any(row.stability == "static" for row in classifications):
            selected.add(static_view_scope)
        if dynamic_heads:
            selected.add(dynamic_view_scope)
            selected.update(
                row.scope_id
                for row in REGISTRY
                if row.surface in {"composition", "report"}
                and dynamic_composition_row(row)
                and applicable_row(row)
            )
    constraints = [
        (constraint, ft, positional_constraint_ref(str(ft.get("id")), index))
        for ft in model.fact_types
        for index, constraint in enumerate(ft.get("constraints") or [])
    ] + [
        (constraint, None, positional_constraint_ref(None, index))
        for index, constraint in enumerate(model.constraints)
    ]
    for constraint, ft, reference in constraints:
        family = str(constraint.get("type"))
        modality = str(constraint.get("modality"))
        value = adapt_phase1_slice(model, view, constraint, ft, reference)
        if value is not None:
            variants = {
                "mandatory": {"phase1-inline"},
                "frequency": {"phase1-internal"},
                "textual": {"phase1"},
            }[family]
        else:
            variants = {constraint_variant(constraint, ft)}
            # These are shared family-level guards, not another representation.
            # In particular guarded zero-binding success is independent of the
            # consequent kind and must not disappear with a comparison variant.
            if family in {"ring", "subtype-partition", "guarded"} and not (
                family == "guarded" and constraint_variant(constraint) == "exists"
            ):
                variants.add("n-a")
            if family == "guarded" and any(
                isinstance(atom, dict) and str(atom.get("fact_type")) in aggregate_heads
                for atom in constraint.get("antecedent") or []
            ):
                variants.add("aggregate")
        constraint_term_capable = carries_exact_term(constraint) or bool(
            set(scope_fact_types(constraint, family, model, ft)) & exact_heads
        )
        constraint_float_capable = carries_float_term(constraint) or bool(
            set(scope_fact_types(constraint, family, model, ft)) & float_heads
        )
        selected.update(
            row.scope_id
            for row in REGISTRY
            if row.surface == "snapshot"
            and row.family == family
            and row.variant in variants
            and row.modality in {"any", modality}
            and applicable_row(
                row,
                temporal_capable=uses_temporal(constraint)
                or bool(
                    set(scope_fact_types(constraint, family, model, ft)) & duration_facts
                ),
                term_capable=constraint_term_capable,
                float_capable=constraint_float_capable,
            )
        )
    return tuple(sorted(selected))


applicable_scope_ids.__module__ = 'gnd.semantic_registry'
