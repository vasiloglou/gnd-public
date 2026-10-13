# ruff: noqa: F401 -- historical namespace imports retained for compatibility facade
"""Deterministic constraint checker with the 5-state verdict lattice.

``check(model, population)`` walks every inline and top-level constraint and
assigns each exactly one verdict from {pass, fail, warning, unchecked, vacuous}:

- Unimplemented constraint families are reported ``unchecked`` — never silently
  passed (D-02).
- A constraint whose subject fact types contain zero facts is ``vacuous``
  (D-12); guarded conjunctions use the stricter any-antecedent-empty rule.
- A violated constraint yields ``fail`` when its modality is alethic and
  ``warning`` when deontic (VER-01 semantics).

Object-type populations follow closed-world semantics (SKELETON.md): the
instance set of object type T is every value playing a T-typed role across all
facts, extended by the explicit ``instances[T]`` roster.

Every verdict message is rendered from the CNL templates in
:mod:`gnd.verbalize`.
"""

from __future__ import annotations

import math
from collections.abc import Iterable, Mapping, Sequence
from dataclasses import dataclass, replace
from datetime import UTC, date, datetime
from graphlib import CycleError, TopologicalSorter
from types import MappingProxyType
from typing import Any, Literal, NamedTuple, Protocol

from pydantic import BaseModel, Field, ValidationInfo, model_validator

from gnd import extensions as extension_core
from gnd import input_policy as _rf7_input
from gnd import verbalize
from gnd.address import (
    derivation_address,  # historical compatibility export
    positional_constraint_ref,
)
from gnd.atoms import (
    atom_bind,
    atom_has_bind,  # historical compatibility export
)
from gnd.branches import (
    UnregisteredBranchError,
    branch,
    constraint_variant,
    record_branch,
    time_relative_operand,
)
from gnd.checker._reports import (
    CheckReport,
    ConstraintVerdict,
    CoverageEntry,
    Phase1Trace,
    Verdict,
    band,
)
from gnd.constraint_families import FAMILIES, resolve_hook
from gnd.documents import Model
from gnd.errors import UnvalidatedPopulationError
from gnd.extensions import (
    DERIVATION_REASON_CODES,  # historical compatibility export
    EXACT_DERIVATION_REASON_CODES,  # historical compatibility export
    DerivationFinding,  # historical compatibility export
    DerivationKind,  # historical compatibility export
    DerivationReason,  # historical compatibility export
    DerivationVerdict,
    DynamicRefreshWork,  # historical compatibility export
    ExtensionCalculator,  # historical compatibility export
    FactPath,  # historical compatibility export
    IdentityCodecVersion,  # historical compatibility export
    JoinDisconnectedError,  # historical compatibility export
    RelationUnavailable,  # historical compatibility export
    RowLineage,  # historical compatibility export
    Scalar,
    StructuredExtensionView,  # historical compatibility export
    VariableResolver,  # historical compatibility export
    constraint_view_legacy,  # historical compatibility export
    derivation_claims_against,  # historical compatibility export
    evaluate_derivations_legacy,  # historical compatibility export
    exact_extension_envelope,  # historical compatibility export
    structured_extension_view,  # historical compatibility export
)
from gnd.extensions import (
    PARTIAL_OPAQUE as _PARTIAL_OPAQUE,  # historical compatibility export
)
from gnd.extensions import (
    PHASE3_LEGACY_CONSTRAINT_VIEW as _PHASE3_LEGACY_CONSTRAINT_VIEW,  # historical compatibility export
)
from gnd.extensions import (
    PHASE3_LEGACY_EVALUATE_DERIVATIONS as _PHASE3_LEGACY_EVALUATE_DERIVATIONS,  # historical compatibility export
)
from gnd.extensions import (
    REFERENCE_PRESENTATION_WORK as _REFERENCE_PRESENTATION_WORK,  # historical compatibility export
)
from gnd.extensions import (
    WITNESS_TRACE as _WITNESS_TRACE,  # historical compatibility export
)
from gnd.extensions import (
    ExactExtensionResult as _ExactExtensionResult,  # historical compatibility export
)
from gnd.extensions import (
    ExactExtensions as _ExactExtensions,  # historical compatibility export
)
from gnd.extensions import (
    ExactJoinWork as _ExactJoinWork,  # historical compatibility export
)
from gnd.extensions import (
    ExtensionResult as _ExtensionResult,  # historical compatibility export
)
from gnd.extensions import (
    FixpointJoinWork as _FixpointJoinWork,  # historical compatibility export
)
from gnd.extensions import JoinWork as _JoinWork  # historical compatibility export
from gnd.extensions import (
    PartialExtensions as _PartialExtensions,  # historical compatibility export
)
from gnd.extensions import (
    PartialTermFailure as _PartialTermFailure,  # historical compatibility export
)
from gnd.extensions import (
    RuledFactView as _RuledFactView,  # historical compatibility export
)
from gnd.extensions import (
    TypedRelation as _TypedRelation,  # historical compatibility export
)
from gnd.extensions import Wildcard as _Wildcard  # historical compatibility export
from gnd.extensions import (
    aggregate_bindings as _aggregate_bindings,  # historical compatibility export
)
from gnd.extensions import (
    aggregate_identity_token as _aggregate_identity_token,  # historical compatibility export
)
from gnd.extensions import (
    apply_negation as _apply_negation,  # historical compatibility export
)
from gnd.extensions import (
    base_relations as _base_relations,  # historical compatibility export
)
from gnd.extensions import (
    binding_lineages as _binding_lineages,  # historical compatibility export
)
from gnd.extensions import (
    clause_bindings as _clause_bindings,  # historical compatibility export
)
from gnd.extensions import (
    component_atoms as _component_atoms,  # historical compatibility export
)
from gnd.extensions import (
    component_product as _component_product,  # historical compatibility export
)
from gnd.extensions import (
    constraint_view as _constraint_view,  # historical compatibility export
)
from gnd.extensions import (
    constraint_view_dispatch as _constraint_view_dispatch,  # historical compatibility export
)
from gnd.extensions import (
    count_term_work as _count_term_work,  # historical compatibility export
)
from gnd.extensions import (
    derivation_obligation as _derivation_obligation,  # historical compatibility export
)
from gnd.extensions import (
    evaluate_derivations as _evaluate_derivations,  # historical compatibility export
)
from gnd.extensions import (
    evaluate_derivations_dispatch as _evaluate_derivations_dispatch,  # historical compatibility export
)
from gnd.extensions import (
    evaluate_stratified_extensions as _evaluate_stratified_extensions,  # historical compatibility export
)
from gnd.extensions import (
    exact_derivation_obligation as _exact_derivation_obligation,  # historical compatibility export
)
from gnd.extensions import (
    exact_extension_calculator as _exact_extension_calculator,  # historical compatibility export
)
from gnd.extensions import (
    extension_fact_map as _extension_fact_map,  # historical compatibility export
)
from gnd.extensions import (
    identity_token as _identity_token,  # historical compatibility export
)
from gnd.extensions import (
    joined_atom_candidates as _joined_atom_candidates,  # historical compatibility export
)
from gnd.extensions import (
    joined_bindings as _joined_bindings,  # historical compatibility export
)
from gnd.extensions import (
    model_uses_exact_derivations as _model_uses_exact_derivations,  # historical compatibility export
)
from gnd.extensions import (
    partial_binding_shape as _partial_binding_shape,  # historical compatibility export
)
from gnd.extensions import (
    partial_bindings as _partial_bindings,  # historical compatibility export
)
from gnd.extensions import (
    partial_clause_rows as _partial_clause_rows,  # historical compatibility export
)
from gnd.extensions import (
    partial_compatible as _partial_compatible,  # historical compatibility export
)
from gnd.extensions import (
    partial_merge as _partial_merge,  # historical compatibility export
)
from gnd.extensions import (
    partial_negation as _partial_negation,  # historical compatibility export
)
from gnd.extensions import (
    partial_row_facts as _partial_row_facts,  # historical compatibility export
)
from gnd.extensions import (
    partial_token as _partial_token,  # historical compatibility export
)
from gnd.extensions import (
    project_extension as _project_extension,  # historical compatibility export
)
from gnd.extensions import (
    project_lineage as _project_lineage,  # historical compatibility export
)
from gnd.extensions import (
    public_refresh_work as _public_refresh_work,  # historical compatibility export
)
from gnd.extensions import (
    python_extension_calculator as _python_extension_calculator,  # historical compatibility export
)
from gnd.extensions import (
    relation_facts as _relation_facts,  # historical compatibility export
)
from gnd.extensions import (
    relation_roles as _relation_roles,  # historical compatibility export
)
from gnd.extensions import (
    requires_fixpoint as _requires_fixpoint,  # historical compatibility export
)
from gnd.extensions import (
    rows_by_identity as _rows_by_identity,  # historical compatibility export
)
from gnd.extensions import (
    rows_from_facts as _rows_from_facts,  # historical compatibility export
)
from gnd.extensions import (
    rule_uses_exact_terms as _rule_uses_exact_terms,  # historical compatibility export
)
from gnd.extensions import (
    scalar_primitive_compatible as _scalar_primitive_compatible,  # historical compatibility export
)
from gnd.extensions import (
    symbolic_value as _symbolic_value,  # historical compatibility export
)
from gnd.extensions import witness as _witness  # historical compatibility export
from gnd.extensions import (
    witness_charge as _witness_charge,  # historical compatibility export
)
from gnd.extensions import witness_row as _witness_row  # historical compatibility export
from gnd.model import (
    AggregateAnalysis,  # historical compatibility export
    BoundReferenceContext,
    _derivation_variable,  # historical compatibility export
    analyze_declared_aggregate,  # historical compatibility export
    body_components,  # historical compatibility export
    derivation_classifications,  # historical compatibility export
    derivation_dependencies,  # historical compatibility export
    derivation_strata,  # historical compatibility export
    iter_derivation_clauses,  # historical compatibility export
)
from gnd.model_index import ModelIndex
from gnd.population import Population
from gnd.proof_bridge import adapt_phase1_slice, phase1_refusal_reason
from gnd.proof_kernel import MAX_SLICE_CONSTRAINTS, SliceInput, SliceVerdict, phase1_decide
from gnd.terms import (
    DEFAULT_LIMITS,  # historical compatibility export
    compare_terms,  # historical compatibility export
    evaluate_term,
    is_function_term,
    materialize_scalar,  # historical compatibility export
    term_variables,  # historical compatibility export
)
from gnd.universe import (
    IMPLEMENTED_FAMILIES,  # historical compatibility export
    resolve_primitive,
    resolve_reference_value_type,  # historical compatibility export
)

#: Constraint families the checker implements (all others -> unchecked, D-02).
#: Combined ring variants -> their component variants (each evaluated).
from gnd.universe import RING_COMPONENTS as _RING_COMPONENTS  # historical compatibility export
from gnd.universe import (
    RING_VARIANTS as _RING_VARIANTS,  # historical compatibility export
)
from gnd.universe import (
    constraint_role_refs as _constraint_role_refs,  # historical compatibility export
)
from gnd.universe import (
    denoting_types as _denoting_types,  # historical compatibility export
)
from gnd.universe import (
    descendant_closure as _descendant_closure,  # historical compatibility export
)
from gnd.universe import (
    fact_type_by_id as _fact_type_by_id,
)
from gnd.universe import (
    instance_values_of as _instance_values_of,
)
from gnd.universe import instances_of as _instances_of
from gnd.universe import (
    is_implemented as _is_implemented,  # historical compatibility export
)
from gnd.universe import kind_of as _kind_of  # historical compatibility export
from gnd.universe import (
    role_object_type as _role_object_type,
)
from gnd.universe import (
    scope_fact_types as _scope_fact_types,
)
from gnd.values import (
    INVALID_LITERAL as _INVALID_LITERAL,
)
from gnd.values import IdentitySet as _IdentitySet
from gnd.values import identity_key as _identity_key
from gnd.values import literal as _literal


def check_legacy(model: Model, population: Population) -> CheckReport:
    """Check a population against every constraint in the model.

    Precondition (D-02): ``population`` must carry the layer-2 validation marker
    for THIS model object AND still hold the content that was validated, or
    :class:`UnvalidatedPopulationError` is raised.
    """
    # Both halves live in Population.matches_validation_marker: model identity
    # (`is`, never equality — two independent load_model() calls on one file
    # compare equal) AND a re-derived content digest, so a population that was
    # loaded cleanly and then mutated is refused rather than checked against
    # facts layer 2 never saw (CR-01). One predicate, one place, because a
    # precondition split across two call sites is how the first half survives a
    # refactor without the second.
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)

    extensions, derivations = extension_core.evaluate_derivations(model, population)
    constraint_population: Population | extension_core.RuledFactView = population
    if extensions:
        constraint_population = extension_core.constraint_view(model, population, extensions)

    constraint_inputs: dict[str, tuple[dict[str, Any], dict[str, Any] | None]] = {}
    trace_rows: list[tuple[SliceInput, SliceVerdict]] = []
    refusal_rows: list[tuple[str, str]] = []
    aliases: dict[str, str] = {}

    for ref, constraint, fact_type in ModelIndex.for_model(model).iter_constraints():
        constraint_inputs[ref] = (constraint, fact_type)
        _observe_phase1_compatibility(
            constraint, ref, model, constraint_population, fact_type,
            trace_rows, refusal_rows, aliases,
        )

    from gnd.correspondence import correspond_snapshot, project_snapshot

    adapted, decision = correspond_snapshot(
        model,
        population,
        effective_facts=constraint_population.facts,
        effective_lineage=(
            constraint_population.lineages
            if isinstance(constraint_population, extension_core.RuledFactView)
            else None
        ),
        variant_aliases=aliases,
    )
    projection = project_snapshot(decision, adapted.observation)
    from gnd.correspondence import ReferenceJoinLimit, project_reference_limit

    projected_findings = projection.findings
    retained_findings = []
    presentation_refused = False
    verdicts: list[ConstraintVerdict] = []
    for finding in projected_findings:
        constraint, fact_type = constraint_inputs[finding.constraint_id]
        witness = _plain_projected_witness(finding.constraint_type, finding.witness)
        try:
            message = _correspondence_message(
                constraint, fact_type, finding, witness, model, constraint_population
            )
        except ReferenceJoinLimit:
            finding = project_reference_limit(finding, adapted.observation)
            witness = []
            message = "Guarded binding production exceeded reference work ceiling 100000."
            presentation_refused = True
        retained_findings.append(finding)
        verdict_payload = {
            "scope_id": finding.scope_id,
            "constraint_ref": finding.constraint_id,
            "constraint_type": finding.constraint_type,
            "modality": finding.modality,
            "source": str(constraint.get("source", "")),
            "status": str(constraint.get("status", "")),
            "verdict": finding.verdict,
            "message": message,
            "offending_facts": witness,
            "reason_code": finding.reason_code,
        }
        verdicts.append(
            ConstraintVerdict.model_validate(
                verdict_payload,
                context={"branch_already_recorded": True},
            )
        )

    if presentation_refused:
        vocabulary = ("pass", "fail", "warning", "unchecked", "vacuous")
        result_band = 1 if projection.band == 1 else 4
        projection = replace(
            projection,
            findings=tuple(retained_findings),
            counts=tuple(
                (name, sum(row.verdict == name for row in retained_findings)) for name in vocabulary
            ),
            band=result_band,
            acceptance_ready=False,
            semantic_decision="refuse" if result_band == 1 else "indeterminate",
        )

    coverage = {
        str(fact_type.get("id")): CoverageEntry(
            declared=(
                "declared" if str(fact_type.get("id")) in population.covers else "undeclared"
            ),
            facts=len(population.facts.get(str(fact_type.get("id")), [])),
        )
        for fact_type in ModelIndex.for_model(model).iter_fact_types()
    }
    return CheckReport(
        verdicts=verdicts,
        derivations=derivations,
        coverage=coverage,
        phase1_trace=_compatibility_trace(verdicts, trace_rows, derivations, coverage),
        phase1_refusals=tuple(refusal_rows),
        snapshot_projection=projection,
        assurance_input_scope_ids=adapted.observation.applicable_scope_ids,
    )


def _observe_phase1_compatibility(
    constraint: dict[str, Any],
    ref: str,
    model: Model,
    population: _FactView,
    fact_type: dict[str, Any] | None,
    rows: list[tuple[SliceInput, SliceVerdict]],
    refusals: list[tuple[str, str]],
    aliases: dict[str, str],
) -> None:
    """Retain the old evidence trace without giving it snapshot authority."""
    value = adapt_phase1_slice(model, population, constraint, fact_type, ref)
    if value is not None:
        verdict = phase1_decide(value)
        if verdict is not None:
            rows.append((value, verdict))
            aliases[ref] = {
                "mandatory": "phase1-inline",
                "frequency": "phase1-internal",
                "textual-refusal": "phase1",
            }[value.family]
            return
    reason = phase1_refusal_reason(model, population, constraint, fact_type, ref)
    if reason is not None:
        refusals.append((ref, reason))
        record_branch(f"applicability:refusal:n-a:{reason}")


def _plain_projected_witness(constraint_type: str, witness: Sequence[Any]) -> list[Any]:
    """Translate the registered family witness into its public shape."""
    entry = FAMILIES.get(constraint_type)
    hook = entry.witness if entry else '_row_projected_witness'
    return resolve_hook(hook, globals())(witness)


def _correspondence_message(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    finding: Any,
    witness: list[Any],
    model: Model,
    population: _FactView,
) -> str:
    """Render the non-semantic envelope from one authoritative finding.

    This function may inspect admitted data to describe a result; it never
    chooses a verdict, reason, witness, count, or band.
    """
    family = finding.constraint_type
    verdict = finding.verdict
    reason = finding.reason_code
    scope_id = finding.scope_id

    if verdict == "vacuous":
        if scope_id.endswith(":coverage-omission"):
            subjects = _scope_fact_types(constraint, family, model, fact_type)
            return verbalize.coverage_omission_message(
                [subject for subject in subjects if subject not in population.covers]
            )
        if ":no-observable-subjects" in scope_id:
            subject = str(constraint.get("object_type") or constraint.get("supertype") or family)
            return verbalize.no_observable_subjects_message(subject)
        if scope_id.endswith(":zero-row-join"):
            sequences = _joining_subject_sequences(constraint, family, fact_type)
            labels = [", ".join(_ref_labels(sequence)) for sequence in sequences]
            return verbalize.no_joined_rows_message(labels)
        return verbalize.vacuous_message(_scope_fact_types(constraint, family, model, fact_type))

    if verdict == "unchecked":
        consequent = constraint.get("consequent")
        has_exists_consequent = (
            isinstance(consequent, Mapping) and isinstance(consequent.get("exists"), Mapping)
        )
        if family == "guarded" and has_exists_consequent and reason == "guarded-exists-coverage-missing":
            exists = consequent.get("exists") or {}
            missing = list(
                dict.fromkeys(
                    str(atom.get("fact_type"))
                    for atom in exists.get("atoms") or []
                    if isinstance(atom, Mapping)
                    and str(atom.get("fact_type")) not in population.covers
                )
            )
            return (
                "Existential consequent was NOT evaluated — source population coverage is "
                f"missing for witness relation(s): {', '.join(missing)}."
            )
        if family == "guarded" and reason == "reference-join-work-limit":
            return (
                "Guarded join was not evaluated: reference combined work ceiling 100000 exceeded."
            )
        if family == "guarded" and has_exists_consequent and reason == "guarded-exists-work-limit":
            return (
                "Existential consequent was NOT evaluated — deterministic work ceiling "
                f"{200_000} was exceeded."
            )
        if (
            family == "guarded"
            and has_exists_consequent
            and isinstance(reason, str)
            and reason.startswith("term:")
        ):
            return (
                "Existential consequent was NOT evaluated because a reached candidate's "
                f"exact term is unavailable: {reason}; partial witnesses are suppressed."
            )
        if reason == "textual-not-mechanical":
            return verbalize.textual_unchecked_message(str(constraint.get("expression", "")))
        if reason == "family-unimplemented":
            return verbalize.unchecked_message(family)
        if reason == "join-disconnected":
            return verbalize.join_disconnected_message(
                _scope_fact_types(constraint, family, model, fact_type)
            )
        if reason == "join-anchor-ambiguous":
            return (
                "Shared-entity join is ambiguous — reported as unchecked until "
                "an explicit join mapping selects one."
            )
        if reason == "ring-not-binary":
            return verbalize.ring_not_binary_message(
                str(constraint.get("variant")),
                str((fact_type or {}).get("id")),
                len((fact_type or {}).get("roles") or []),
            )
        if reason == "role-unresolved":
            return verbalize.unresolved_role_message(
                str(constraint.get("role")), str((fact_type or {}).get("id"))
            )
        if reason == "subject-type-ambiguous":
            refs = list(constraint.get("role_refs") or [])
            return verbalize.disjunctive_subject_type_message(
                _ref_labels(refs),
                [
                    str(_role_object_type(model, str(ref.get("fact_type")), str(ref.get("role"))))
                    for ref in refs
                ],
            )
        if reason == "xor-disjunctive-undefined":
            sequences = [list(row or []) for row in constraint.get("role_seqs") or []]
            return verbalize.exclusive_or_multirole_unchecked_message(
                [", ".join(_ref_labels(row)) for row in sequences]
            )
        if reason == "no-reference-clock":
            return verbalize.value_comparison_unchecked_message(
                time_relative_operand(constraint, fact_type) or "current time"
            )
        if family == "guarded" and reason in {
            "values-not-comparable",
            "literal-type-ambiguous",
        }:
            atoms = [dict(atom) for atom in constraint.get("antecedent") or []]
            bindings = _guarded_bindings(atoms, population)
            comparison = (constraint.get("consequent") or {}).get("comparison") or {}
            operator = str(comparison.get("operator"))
            left = comparison.get("left")
            right = comparison.get("right")
            variables = (_guarded_variable(left), _guarded_variable(right))
            primitives_by_variable = _guarded_variable_primitives(atoms, model)
            primitives = (
                primitives_by_variable.get(variables[0]) if variables[0] is not None else None,
                primitives_by_variable.get(variables[1]) if variables[1] is not None else None,
            )
            comparison_primitives = [primitives[0], primitives[1]]
            prepared = [left, right]
            if variables[0] is None and variables[1] is not None:
                prepared[0] = _literal(left, primitives[1], legacy=False)
                comparison_primitives[0] = primitives[1]
            if variables[1] is None and variables[0] is not None:
                prepared[1] = _literal(right, primitives[0], legacy=False)
                comparison_primitives[1] = primitives[0]
            if reason == "literal-type-ambiguous":
                literal = left if prepared[0] is _INVALID_LITERAL else right
                primitive = primitives[1] if prepared[0] is _INVALID_LITERAL else primitives[0]
                return verbalize.guarded_literal_unchecked_message(
                    literal, primitive, len(bindings)
                )
            undecidable: list[dict[str, Any]] = []
            offending: list[dict[str, Any]] = []
            for binding in bindings:
                values = [
                    binding[variable] if variable is not None else value
                    for variable, value in zip(variables, prepared, strict=True)
                ]
                outcome = _compare(
                    values[0],
                    operator,
                    values[1],
                    comparison_primitives[0],
                    comparison_primitives[1],
                )
                if outcome is None:
                    undecidable.append(binding)
                elif not outcome:
                    offending.append(binding)
            return verbalize.guarded_not_comparable_message(
                operator, len(bindings), undecidable, offending
            )
        if reason == "values-not-comparable" and family == "value-comparison":
            label_a, label_b, pairs = _value_comparison_message_inputs(
                constraint, fact_type, model, population
            )
            operator = str(constraint.get("operator"))
            undecidable = [
                pair for pair in pairs if _compare(pair[0], operator, pair[1], None, None) is None
            ]
            offending = [
                pair for pair in pairs if _compare(pair[0], operator, pair[1], None, None) is False
            ]
            return verbalize.values_not_comparable_message(
                label_a, operator, label_b, undecidable, offending
            )
        if reason == "bound-type-mismatch" and family == "value":
            object_type = str(constraint.get("object_type"))
            role_ref = constraint.get("role_ref")
            if isinstance(role_ref, dict):
                values = [
                    value
                    for (value,) in _project(
                        population,
                        str(role_ref.get("fact_type")),
                        [str(role_ref.get("role"))],
                    )
                ]
            else:
                values = _instance_values_of(object_type, model, population)
            ranges = list(constraint.get("ranges") or [])
            if not ranges:
                ranges = [constraint.get("range") or {}]
            primitive = resolve_primitive(object_type, model)
            undecidable: list[Any] = []
            offending: list[Any] = []
            for value in values:
                outcomes = [_in_range(value, bounds, primitive) for bounds in ranges]
                if any(outcome is True for outcome in outcomes):
                    continue
                if any(outcome is None for outcome in outcomes):
                    undecidable.append(value)
                else:
                    offending.append(value)
            return verbalize.bound_type_mismatch_message(
                object_type, ranges, undecidable, offending
            )
        if reason == "partition-asserts-nothing":
            return verbalize.subtype_partition_no_assertion_message(
                str(constraint.get("supertype")),
                [str(row) for row in constraint.get("subtypes") or []],
            )
        if reason == "subtype-derivation-only":
            object_types = {str(row.get("id")): row for row in model.object_types}
            for subtype in [str(row) for row in constraint.get("subtypes") or []]:
                declaration = object_types.get(subtype, {})
                if declaration.get("derivation") in {"derived", "semiderived"}:
                    return verbalize.subtype_partition_unchecked_message(
                        subtype, str(declaration.get("derivation_rule", ""))
                    )
        return f"Constraint {family!r} was NOT evaluated — reported as unchecked: {reason}."

    violated = verdict in {"fail", "warning"}
    if family == "guarded" and scope_id.endswith(":clean-zero-bindings"):
        consequent = constraint.get("consequent") or {}
        kind = next(
            (name for name in ("comparison", "atom", "absence", "exists") if name in consequent),
            "guarded",
        )
        return verbalize.guarded_zero_bindings_message(kind)
    entry = FAMILIES.get(family)
    hook = entry.message if entry else '_family_message_default'
    return resolve_hook(hook, globals())(
        constraint, fact_type, finding, witness, model, population,
        family, verdict, scope_id, violated,
    )


def _value_comparison_message_inputs(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    model: Model,
    population: _FactView,
) -> tuple[str, str, list[tuple[Any, Any]]]:
    """Presentation labels and admitted pairs for a value-comparison finding."""
    left = constraint.get("role_a")
    right = constraint.get("role_b")
    if fact_type is None:
        refs = [dict(left or {}), dict(right or {})]
        labels = _ref_labels(refs)
        if refs[0].get("fact_type") == refs[1].get("fact_type"):
            pairs = _project(
                population,
                str(refs[0].get("fact_type")),
                [str(refs[0].get("role")), str(refs[1].get("role"))],
            )
        else:
            pairs = _join_rows(model, population, refs)
        return labels[0], labels[1], [(row[0], row[1]) for row in pairs]

    role_names = {str(role.get("role_name")) for role in fact_type.get("roles") or []}
    operands = [left, right]
    labels: list[str] = []
    pairs: list[tuple[Any, Any]] = []
    for operand in operands:
        if isinstance(operand, str) and operand in role_names:
            labels.append(operand)
        elif isinstance(operand, dict) and operand.get("role") in role_names:
            labels.append(str(operand.get("role")))
        else:
            labels.append(str(operand.get("literal") if isinstance(operand, dict) else operand))
    for fact in population.facts.get(str(fact_type.get("id")), []):
        values: list[Any] = []
        for operand in operands:
            role = (
                str(operand.get("role"))
                if isinstance(operand, dict) and operand.get("role") in role_names
                else operand
                if isinstance(operand, str) and operand in role_names
                else None
            )
            if role is not None:
                if role not in fact:
                    values = []
                    break
                values.append(fact[role])
            else:
                values.append(operand.get("literal") if isinstance(operand, dict) else operand)
        if len(values) == 2:
            pairs.append((values[0], values[1]))
    return labels[0], labels[1], pairs


def _compatibility_trace(
    verdicts: list[ConstraintVerdict],
    rows: list[tuple[SliceInput, SliceVerdict]],
    derivations: list[extension_core.DerivationVerdict],
    coverage: dict[str, CoverageEntry],
) -> Phase1Trace | None:
    """The trace, or None when the checked model is not wholly inside the slice.

    "Wholly" is measured, not assumed: one constraint the slice refused, one
    derivation obligation, or an empty model all withhold the trace, because
    each of them is a result-producing branch the slice did not decide.
    """
    if not verdicts or derivations or len(rows) != len(verdicts):
        return None
    # A14.1 admits at most three constraints, and the in-scope predicate sees
    # one SliceInput at a time, so the count is decided here -- the one place
    # that sees them all (review finding R4: a four-constraint model carried
    # the whole-result claim before this gate existed).
    if len(verdicts) > MAX_SLICE_CONSTRAINTS:
        return None
    return Phase1Trace(
        rows=tuple(rows),
        coverage=tuple(
            (fact_type_id, entry.declared, entry.facts) for fact_type_id, entry in coverage.items()
        ),
        applicable=len(verdicts),
        slice_decided=len(rows),
    )


#: Families whose subjects are an OBJECT TYPE's population rather than a fact
#: type's, and which therefore can reach evaluation with an empty scope. The
#: field naming the subject differs per family, hence the mapping.
_OBJECT_TYPE_SCOPED = {
    "value": "object_type",
    "cardinality": "object_type",
    "subtype-partition": "supertype",
}


def _no_observable_subjects_message(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    population: Population,
) -> str | None:
    """The vacuity message for a constraint whose subject universe is empty.

    Returns ``None`` — meaning "not vacuous, keep the evaluated verdict" —
    whenever the universe holds anything, or whenever the family's subject is
    not an object-type population at all. The universe is
    :func:`_instance_values_of`, the same one walk the family checks read, so
    this can never disagree with what was actually evaluated.
    """
    subject_field = _OBJECT_TYPE_SCOPED.get(constraint_type)
    if subject_field is None:
        return None
    object_type_id = constraint.get(subject_field)
    if object_type_id is None:
        return None
    if _instance_values_of(str(object_type_id), model, population):
        return None
    return verbalize.no_observable_subjects_message(str(object_type_id))


class _JoinSubjectRow(NamedTuple):
    """One family's join-scoped subject description (F-05).

    Every field is required, so a future edit that adds a family but forgets the
    ``quantifier`` fails at table-construction time (a positional NamedTuple
    argument), never with a silent default — the quantifier is DATA, not a
    comment that a later edit can leave stale.
    """

    #: The constraint fields naming this family's subject role sequence(s).
    subject_fields: tuple[str, ...]
    #: ``any`` -> vacuous when the (single) subject sequence yields zero rows;
    #: ``all`` -> vacuous only when EVERY subject sequence yields zero rows.
    quantifier: Literal["any", "all"]
    #: True when the subject fields are single refs assembled into ONE combined
    #: sequence evaluated by a single join (cross-fact ``value-comparison``,
    #: whose cross form is one ``_join_rows([ref_a, ref_b])`` at checker.py:1695).
    combined: bool
    #: Why this family is in the table and with this quantifier.
    reason: str


#: Families that can reach `pass` over a ZERO-ROW JOIN and must be downgraded to
#: `vacuous` (F-05). The table matches the task-1 probe sweep EXACTLY — a family
#: is present iff its probe showed `pass` over a zero-row join. Two deliberate
#: absences, each with the population that established it:
#:
#: - `subset`: ABSENT. `∅ ⊆ X → pass` (checker.py:1242, offending = sub - sup)
#:   is a ratified decided containment — Halpin, and 01.1-VERIFICATION.md's
#:   residual-routes table — proven by the `subset_subject_zero_row` probe. The
#:   SUPERSET-side zero-row case stays `fail`. Adding `subset` here would convert
#:   the legitimate ∅⊆X `pass` into `vacuous` on the multi-fact path while a
#:   single-fact empty subset stayed `pass` — a projection-vs-join split on
#:   identical state, which is the very F-05 shape and a D-13 semantics change.
#:   Plan 03's degeneracy gate is made positive instead of waiting for this
#:   `vacuous`.
#: - `exclusive-or`: ABSENT. The multi-role branch returns `unchecked`
#:   (`xor-disjunctive-undefined`, checker.py) before it can reach `pass`; the
#:   single-role branch quantifies over `_instances_of`, an object-type universe,
#:   not a join.
_JOIN_SUBJECT_SEQS: dict[str, _JoinSubjectRow] = {
    "uniqueness": _JoinSubjectRow(
        ("role_refs",),
        "any",
        False,
        "external UC subject is one joined sequence; an empty join has no tuples "
        "to check for duplicates (top-level form only — inline uses `roles`)",
    ),
    "frequency": _JoinSubjectRow(
        ("role_refs",),
        "any",
        False,
        "external frequency subject is one joined sequence; an empty join has no "
        "occurring groups, so a `min` bound is silently never violated",
    ),
    "value-comparison": _JoinSubjectRow(
        ("role_a", "role_b"),
        "any",
        True,
        "the cross form joins [role_a, role_b] as ONE combined sequence "
        "(checker.py:1695); an empty join has no pairs to compare (C8)",
    ),
    "equality": _JoinSubjectRow(
        ("role_seq_a", "role_seq_b"),
        "all",
        False,
        "equality is decided when either side has rows (only_a/only_b make it "
        "`fail`); vacuous only when BOTH joins are empty",
    ),
    "exclusion": _JoinSubjectRow(
        ("role_seq_a", "role_seq_b"),
        "all",
        False,
        "one empty side is a real decision (∅ ∩ X = ∅ → `pass`, 01.1-ratified); "
        "vacuous only when BOTH joins are empty",
    ),
}


def _joining_subject_sequences(
    constraint: dict[str, Any],
    constraint_type: str,
    fact_type: dict[str, Any] | None,
) -> list[list[dict[str, Any]]]:
    """The constraint's SUBJECT role sequences, per :data:`_JOIN_SUBJECT_SEQS`.

    Not every sequence a constraint mentions — only the ones whose emptiness means
    "no subjects". A ``combined`` row assembles its single refs into ONE sequence
    (the cross-fact ``value-comparison`` join); a non-combined row yields one
    sequence per subject field. Inline forms carry no subject field here (inline
    uniqueness/frequency use ``roles``), so they return nothing and never trip the
    join-vacuity clause.
    """
    row = _JOIN_SUBJECT_SEQS.get(constraint_type)
    if row is None:
        return []
    if row.combined:
        sequence = [
            ref
            for subject_field in row.subject_fields
            if isinstance((ref := constraint.get(subject_field)), dict)
        ]
        return [sequence] if sequence else []
    sequences: list[list[dict[str, Any]]] = []
    for subject_field in row.subject_fields:
        value = constraint.get(subject_field)
        if isinstance(value, list):
            sequence = [ref for ref in value if isinstance(ref, dict)]
            if sequence:
                sequences.append(sequence)
    return sequences


def _no_joined_rows_message(
    constraint: dict[str, Any],
    constraint_type: str,
    model: Model,
    population: Population,
    fact_type: dict[str, Any] | None,
) -> str | None:
    """The vacuity message for a join-scoped constraint whose JOIN yielded zero
    rows, or ``None`` — "keep the evaluated verdict" — when a required subject
    sequence produced rows.

    At least one subject sequence must span MORE THAN ONE fact type: this clause
    is about the JOIN universe, and single-fact emptiness alone is
    :func:`_vacuity_message`'s job, decided before evaluation. Every subject
    sequence is evaluated with :func:`_role_seq_tuples` — the SAME function the
    family check ran, never a re-implemented join — so this can never disagree with
    what was actually evaluated. The row's ``quantifier`` decides ANY vs ALL
    emptiness (see :data:`_JOIN_SUBJECT_SEQS`):

    - ``any`` families carry ONE subject sequence, and it is a join — vacuous when
      that join is empty.
    - ``all`` families (``equality``, ``exclusion``) carry two sides — vacuous only
      when EVERY subject sequence is empty. A NON-empty single-fact projection side
      keeps the constraint decided (``∅ ∩ X = ∅`` is a real ``pass``), so the
      single-fact side is counted for emptiness even though it is skipped for the
      "is this a join at all?" gate. Dropping it before the ALL check would demote
      a decided one-empty-side ``pass`` to vacuity — the exact over-correction the
      ``exclusion_one_side_zero_row`` control guards against.
    """
    row = _JOIN_SUBJECT_SEQS.get(constraint_type)
    if row is None:
        return None
    sequences = _joining_subject_sequences(constraint, constraint_type, fact_type)
    spans_join = [
        len({str(ref.get("fact_type")) for ref in sequence}) > 1 for sequence in sequences
    ]
    if not any(spans_join):
        return None
    empties = [not _role_seq_tuples(model, population, sequence) for sequence in sequences]
    vacuous = any(empties) if row.quantifier == "any" else all(empties)
    if not vacuous:
        return None
    labels = [
        ", ".join(_ref_labels(sequence))
        for sequence, joined, empty in zip(sequences, spans_join, empties, strict=True)
        if joined and empty
    ]
    return verbalize.no_joined_rows_message(labels)


# --- scope / vacuity ---


#: Families that quantify universally over object-type instances: for these,
#: omitting a subject fact type from ``covers`` makes the verdict vacuous even
#: when facts are present (D-12 second clause).
_MANDATORY_RELEVANT = {"mandatory", "mandatory-disjunctive"}


def _vacuity_message(
    constraint_type: str, scope: list[str], population: Population
) -> tuple[str, str] | None:
    """The vacuity branch identity and rendered message, or None.

    Two D-12 clauses:
    - Coverage omission: a mandatory-relevant constraint whose subject fact
      type is absent from ``covers`` cannot be evaluated against a population
      that does not claim completeness for it.
    - Empty subject: every subject fact type carries zero facts (declared or
      not — an omitted-and-empty fact type must never yield a silent pass).

    An EMPTY scope is not decided here. "No fact type ranges over this
    constraint" is not the same claim as "this constraint has no subjects": a
    ``value`` constraint on an object type no fact type mentions can still be
    populated by an ``instances:`` roster, and a ``cardinality`` ``min`` bound is
    genuinely decided — and violated — by a universe of zero. Answering vacuous
    here would convert both of those into exit 2. The empty-scope case is
    therefore settled AFTER evaluation, in :func:`_verdict_for`, where the only
    verdict it can overturn is a ``pass`` (F-02).
    """
    if not scope:
        return None
    if constraint_type in _MANDATORY_RELEVANT:
        omitted = [ft for ft in scope if ft not in population.covers]
        if omitted:
            return (
                "applicability:vacuity:n-a:coverage-omission",
                verbalize.coverage_omission_message(omitted),
            )
    empty = [not population.facts.get(fact_type_id) for fact_type_id in scope]
    if (constraint_type == "guarded" and any(empty)) or all(empty):
        scope_id = (
            "applicability:vacuity:guarded:empty-subject-any"
            if constraint_type == "guarded"
            else "applicability:vacuity:n-a:empty-subject-all"
        )
        return scope_id, verbalize.vacuous_message(scope)
    return None


# --- shared machinery: projection, join, instance derivation ---


class JoinAmbiguousError(Exception):
    """A fact type offers multiple same-type candidates for one join anchor."""

    def __init__(self, fact_type_id: str, object_type_id: str, role_names: list[str]):
        self.fact_type_id = fact_type_id
        self.object_type_id = object_type_id
        self.role_names = list(role_names)
        super().__init__(
            f"{fact_type_id} has ambiguous {object_type_id} anchors: {', '.join(role_names)}"
        )


def _project(population: Population, fact_type_id: str, role_names: list[str]) -> list[tuple]:
    """Role-sequence projection over one fact type, preserving duplicates."""
    return [
        tuple(fact[role] for role in role_names)
        for fact in population.facts.get(str(fact_type_id), [])
        if all(role in fact for role in role_names)
    ]


def _identity_counts(values: Iterable[Any]) -> dict[tuple[Any, ...], tuple[Any, int]]:
    counts: dict[tuple[Any, ...], tuple[Any, int]] = {}
    for value in values:
        identity = _identity_key(value)
        original, count = counts.get(identity, (value, 0))
        counts[identity] = (original, count + 1)
    return counts


def _join_rows(
    model: Model, population: Population, role_refs: list[dict[str, Any]]
) -> list[tuple]:
    """Join the referenced fact types on shared-object-type anchor roles.

    Returns one tuple per joined row, holding the referenced role values in
    ``role_refs`` order. Anchor roles are the non-referenced roles of each fact
    type; rows join when anchor values of the same object type are equal (the
    shared-entity join used by external uniqueness/frequency constraints).
    """
    by_fact_type: dict[str, list[tuple[int, str]]] = {}
    order: list[str] = []
    for slot, ref in enumerate(role_refs):
        fact_type_id = str(ref.get("fact_type"))
        if fact_type_id not in by_fact_type:
            by_fact_type[fact_type_id] = []
            order.append(fact_type_id)
        by_fact_type[fact_type_id].append((slot, str(ref.get("role"))))

    _require_joinable(model, by_fact_type, order)

    rows: list[tuple[dict[str, Any], dict[int, Any]]] = [({}, {})]
    for fact_type_id in order:
        fact_type = _fact_type_by_id(model, fact_type_id)
        ref_roles = {role for _, role in by_fact_type[fact_type_id]}
        anchor_roles = [
            (str(role.get("role_name")), str(role.get("object_type")))
            for role in (fact_type or {}).get("roles") or []
            if str(role.get("role_name")) not in ref_roles
        ]
        new_rows: list[tuple[dict[str, Any], dict[int, Any]]] = []
        for anchors, outputs in rows:
            for fact in population.facts.get(fact_type_id, []):
                if any(role not in fact for role, _ in anchor_roles):
                    continue
                if any(role not in fact for _, role in by_fact_type[fact_type_id]):
                    continue
                merged = dict(anchors)
                compatible = True
                for role_name, object_type in anchor_roles:
                    value = fact[role_name]
                    identity = _identity_key(value)
                    if object_type in merged and merged[object_type] != identity:
                        compatible = False
                        break
                    merged[object_type] = identity
                if not compatible:
                    continue
                new_outputs = dict(outputs)
                for slot, role_name in by_fact_type[fact_type_id]:
                    new_outputs[slot] = fact[role_name]
                new_rows.append((merged, new_outputs))
        rows = new_rows

    return [tuple(outputs[slot] for slot in range(len(role_refs))) for _, outputs in rows]


def _require_joinable(
    model: Model,
    by_fact_type: dict[str, list[tuple[int, str]]],
    order: list[str],
) -> None:
    """Raise :class:`JoinDisconnectedError` when the referenced fact types do
    not form one connected component under shared anchor object types.

    The check is structural (model-only, population-independent): fact types
    are nodes; an edge exists when two fact types share at least one anchor
    object type. A disconnected component means at least one fact type would
    contribute a Cartesian product to the join — silently wrong (CR-02).
    """
    if len(order) <= 1:
        return
    anchor_types: dict[str, set[str]] = {}
    for fact_type_id in order:
        fact_type = _fact_type_by_id(model, fact_type_id)
        ref_roles = {role for _, role in by_fact_type[fact_type_id]}
        candidates: dict[str, list[str]] = {}
        for role in (fact_type or {}).get("roles") or []:
            if str(role.get("role_name")) in ref_roles:
                continue
            candidates.setdefault(str(role.get("object_type")), []).append(
                str(role.get("role_name"))
            )
        for object_type_id, role_names in candidates.items():
            if len(role_names) > 1:
                raise JoinAmbiguousError(fact_type_id, object_type_id, role_names)
        anchor_types[fact_type_id] = {
            str(role.get("object_type"))
            for role in (fact_type or {}).get("roles") or []
            if str(role.get("role_name")) not in ref_roles
        }
    component = {order[0]}
    remaining = set(order) - component
    grew = True
    while grew and remaining:
        grew = False
        for fact_type_id in sorted(remaining):
            if any(anchor_types[fact_type_id] & anchor_types[member] for member in component):
                component.add(fact_type_id)
                remaining.discard(fact_type_id)
                grew = True
    if remaining:
        raise extension_core.JoinDisconnectedError(order)


def _role_seq_tuples(
    model: Model, population: Population, seq: list[dict[str, Any]]
) -> list[tuple]:
    """Tuples of a role sequence: projection within one fact type, join across."""
    fact_type_ids = {str(ref.get("fact_type")) for ref in seq}
    if len(fact_type_ids) == 1:
        fact_type_id = next(iter(fact_type_ids))
        return _project(population, fact_type_id, [str(ref.get("role")) for ref in seq])
    return _join_rows(model, population, seq)


def _ref_labels(role_refs: list[dict[str, Any]]) -> list[str]:
    return [f"{ref.get('fact_type')}.{ref.get('role')}" for ref in role_refs]


def _violation_verdict(modality: str) -> Verdict:
    return "fail" if modality == "alethic" else "warning"


# --- family checks ---


def _orderable(a: Any, b: Any) -> bool:
    """Whether two operands admit a total order under Python's operators.

    Exactly two families qualify: two numbers, or two strings. Anything else —
    a number against a string, a string against None — has no ordering, and
    Python raises rather than inventing one.

    ``bool`` is excluded from the numeric family DELIBERATELY, and the exclusion
    must not be simplified away: ``isinstance(True, int)`` is ``True`` in
    Python, and ``True == 1``, so without it a boolean would order against a
    numeric bound and land silently INSIDE a ``1..100`` range. That is the
    ``typed-range-bool-for-integer`` defect, which CORE-04 pins at the loader
    (``population:type-mismatch``) and which this guard must not re-open behind
    it. Declining to order a boolean is the honest answer here; deciding
    whether a boolean is a valid Integer is the loader's job, not this one's.

    ``NaN`` is excluded for the same reason and by the same shape (CR-04).
    IEEE 754-2019 §5.11: every ordered comparison involving NaN is *unordered*,
    so ``min <= x <= max`` is false, never true — but ``_in_range`` derives its
    answer from the NEGATION (``not (below or above)``), and both ``nan < min``
    and ``nan > max`` are ``False``, so a NaN came out INSIDE every range and
    the constraint reported "— satisfied" at exit 0. Python does not raise on
    ``nan < 60``, so unlike every other unorderable pairing here this one had no
    crash to notice. ``popvalidate._is_number`` now rejects non-finite values at
    the loader; this is the defense-in-depth twin for the D-05 residual path,
    where the role's object type has no resolvable primitive and no type check
    ever runs. ``inf`` is NOT excluded: it orders totally and correctly against
    finite bounds, so declining to order it would trade a false pass for a false
    ``unchecked``.
    """
    numeric = (int, float)

    def _numeric(value: Any) -> bool:
        return (
            isinstance(value, numeric)
            and not isinstance(value, bool)
            and not (isinstance(value, float) and math.isnan(value))
        )

    return (_numeric(a) and _numeric(b)) or (isinstance(a, str) and isinstance(b, str))


def _in_range(value: Any, bounds: dict[str, Any], primitive: str | None = None) -> bool | None:
    """Whether ``value`` lies within ``bounds`` — or ``None`` when undecidable.

    Defense in depth (D-13 clause 4, T-01.1-15): CORE-04's model-relative type
    validation is what normally prevents an unorderable pairing from reaching
    the checker at all — a String in an Integer-typed role is rejected at load
    with ``population:type-mismatch`` (exit 3) and never arrives here. This
    guard exists for the residual path D-05 deliberately leaves open: when a
    role's object type has NO resolvable primitive (a unit-based or external
    reference mode, an ambiguous multiple inheritance), the type check is
    skipped silently and correctly, and its values arrive intact.

    Returns ``None`` rather than raising because the caller evaluates over a
    COLLECTION: a raise would discard the verdicts for every well-typed value
    alongside the one ill-typed member. Reporting "could not decide" mirrors the
    :class:`JoinDisconnectedError` precedent at a finer grain — when a
    computation is not soundly decidable, say so instead of returning a
    plausible verdict.
    """
    minimum = bounds.get("min")
    maximum = bounds.get("max")
    min_inclusive = bounds.get("min_inclusive", True)
    max_inclusive = bounds.get("max_inclusive", True)
    below = False
    if minimum is not None:
        below = _compare(value, "<" if min_inclusive else "<=", minimum, primitive, primitive)
        if below is None:
            return None
    above = False
    if maximum is not None:
        above = _compare(value, ">" if max_inclusive else ">=", maximum, primitive, primitive)
        if above is None:
            return None
    return not (below or above)


def _find_cycle(pairs: list[tuple]) -> list | None:
    """Cycle members of the directed graph induced by binary pairs, or None.

    Primary path: stdlib ``graphlib.TopologicalSorter`` — its ``CycleError``
    carries the cycle path in ``args[1]`` (RESEARCH A1, confirmed by unit
    test). If that shape ever yields fewer than two members, a ~20-line DFS
    fallback recovers the cycle path.
    """
    graph: dict[Any, set[Any]] = {}
    for a, b in pairs:
        graph.setdefault(a, set()).add(b)
        graph.setdefault(b, set())
    try:
        TopologicalSorter(graph).prepare()
        return None
    except CycleError as error:
        members = list(error.args[1]) if len(error.args) > 1 else []
        if len(set(members)) >= 2:
            return members
        return _dfs_cycle(graph)


def _dfs_cycle(graph: dict[Any, set[Any]]) -> list | None:
    """Iterative DFS fallback returning an explicit cycle path."""
    visiting: set[Any] = set()
    visited: set[Any] = set()
    for start in graph:
        if start in visited:
            continue
        stack: list[tuple[Any, list[Any]]] = [(start, [start])]
        while stack:
            node, path = stack.pop()
            if node in visiting:
                continue
            visiting.add(node)
            for successor in graph.get(node, ()):
                if successor in path:
                    return path[path.index(successor) :] + [successor]
                if successor not in visited:
                    stack.append((successor, path + [successor]))
            visited.add(node)
    return None


def _ring_component_violations(
    component: str, pair_set: set[tuple], elements: set[Any]
) -> list[tuple]:
    """Offending witnesses for one primitive ring variant (Halpin semantics)."""
    if component == "irreflexive":
        return sorted(((a, b) for a, b in pair_set if a == b), key=repr)
    if component == "asymmetric":
        return sorted(((a, b) for a, b in pair_set if (b, a) in pair_set), key=repr)
    if component == "antisymmetric":
        return sorted(((a, b) for a, b in pair_set if a != b and (b, a) in pair_set), key=repr)
    if component == "symmetric":
        return sorted(((a, b) for a, b in pair_set if (b, a) not in pair_set), key=repr)
    if component == "intransitive":
        return sorted(
            (
                (a, b, c)
                for a, b in pair_set
                for b2, c in pair_set
                if b2 == b and (a, c) in pair_set
            ),
            key=repr,
        )
    if component == "transitive":
        return sorted(
            (
                (a, b, c)
                for a, b in pair_set
                for b2, c in pair_set
                if b2 == b and (a, c) not in pair_set
            ),
            key=repr,
        )
    if component == "purely-reflexive":
        return sorted(((a, b) for a, b in pair_set if a != b), key=repr)
    if component == "reflexive":
        return sorted(((a,) for a in elements if (a, a) not in pair_set), key=repr)
    # acyclic
    cycle = _find_cycle(sorted(pair_set, key=repr))
    return [tuple(cycle)] if cycle else []


_COMPARATORS = {
    "<": lambda a, b: a < b,
    "<=": lambda a, b: a <= b,
    "=": lambda a, b: a == b,
    ">=": lambda a, b: a >= b,
    ">": lambda a, b: a > b,
    "!=": lambda a, b: a != b,
}


def _typed_comparison_values(
    value_a: Any,
    value_b: Any,
    primitive_a: str | None,
    primitive_b: str | None,
) -> tuple[Any, Any] | None:
    """Coerce role values into their declared common comparison domain."""
    if primitive_a is None or primitive_b is None:
        return value_a, value_b
    numeric = {"Integer", "Float", "Number"}
    if primitive_a in numeric and primitive_b in numeric:
        return value_a, value_b
    if primitive_a != primitive_b:
        return None
    if primitive_a == "Date":
        try:
            return date.fromisoformat(value_a), date.fromisoformat(value_b)
        except (TypeError, ValueError):
            return None
    if primitive_a == "DateTime":
        try:
            parsed = []
            for value in (value_a, value_b):
                parsed.append(_rf7_input.parse_datetime(value))
        except (TypeError, ValueError):
            return None
        aware = [value.utcoffset() is not None for value in parsed]
        if aware[0] != aware[1]:
            return None
        if aware[0]:
            parsed = [value.astimezone(UTC) for value in parsed]
        return parsed[0], parsed[1]
    return value_a, value_b


def _compare(
    value_a: Any,
    operator: str,
    value_b: Any,
    primitive_a: str | None = None,
    primitive_b: str | None = None,
) -> bool | None:
    """Evaluate one comparison — or return ``None`` when it cannot be decided.

    Equality and inequality stay TOTAL across types and are answered first:
    Python's ``==`` / ``!=`` are well defined for any two objects and never
    raise, so ``1 != "a"`` has a correct answer and must keep getting one. D-14
    targets ORDERING only, which is why this early return survives it.

    For an ordering operator the operands must be orderable. D-14 removed the
    former fallback, which rendered both operands as text and compared those
    instead: it evaluated ``1 < "a"`` as ``"1" < "a"`` and returned ``True`` —
    a CONFIDENT WRONG ANSWER
    indistinguishable to the caller from a real evaluation — strictly worse than
    the crash it was presumably added to avoid. ``None`` is the honest third
    answer, and the caller turns it into an ``unchecked`` verdict carrying
    ``values-not-comparable``.
    """
    if (
        operator in ("=", "!=")
        and primitive_a is not None
        and primitive_b is not None
        and primitive_a != primitive_b
        and not {primitive_a, primitive_b} <= {"Integer", "Float", "Number"}
    ):
        equal = _identity_key(value_a) == _identity_key(value_b)
        return equal if operator == "=" else not equal

    typed = _typed_comparison_values(value_a, value_b, primitive_a, primitive_b)
    if typed is None:
        return None
    value_a, value_b = typed
    comparator = _COMPARATORS[operator]
    if operator in ("=", "!="):
        equal = _identity_key(value_a) == _identity_key(value_b)
        return equal if operator == "=" else not equal
    if primitive_a == primitive_b and primitive_a in ("Date", "DateTime"):
        return bool(comparator(value_a, value_b))
    if not _orderable(value_a, value_b):
        return None
    # Two numbers, or two strings — the latter compare lexically, which is what
    # makes ISO-8601 dates order correctly (and why popvalidate format-checks
    # Date/DateTime values at load).
    return bool(comparator(value_a, value_b))


def _guarded_variable(term: Any) -> str | None:
    """Return a guarded variable name; every other scalar is literal data."""
    return term if isinstance(term, str) and term.startswith("$") else None


# Opt-in capture for finite derivation witnesses. Ordinary checking has no trace.


class _FactView(Protocol):
    covers: Sequence[str]
    instances: Mapping[str, Sequence[Scalar]]
    facts: Mapping[str, Sequence[Mapping[str, Scalar]]]


def _guarded_bindings(atoms: list[dict[str, Any]], population: Population) -> list[dict[str, Any]]:
    """Preserve the guarded disconnection policy through the shared join core."""
    from gnd.correspondence import ReferenceJoinWork

    token = extension_core.REFERENCE_PRESENTATION_WORK.set(
        ReferenceJoinWork() if getattr(population, "_reference_combined", False) else None
    )
    try:
        return extension_core.joined_bindings(
            atoms,
            population.facts,
            variable_of=_guarded_variable,
            work=None,
        )
    finally:
        extension_core.REFERENCE_PRESENTATION_WORK.reset(token)


def structured_extension_facts(
    model: Model,
    population: Population,
) -> Mapping[str, tuple[Mapping[str, extension_core.Scalar], ...]]:
    """Return the computed structured extensions as fact-shaped rows.

    This is the transition layer's deliberately small adapter to the checker-owned
    extension calculator.  It keeps one derivation implementation while exposing
    neither the calculator's typed-relation internals nor its proof bookkeeping.
    """
    if not population.matches_validation_marker(model):
        raise UnvalidatedPopulationError(population, model)
    calculated = (
        extension_core.exact_extension_calculator(model, extension_core.base_relations(model, population))
        if extension_core.model_uses_exact_derivations(model)
        else extension_core.python_extension_calculator(model, extension_core.base_relations(model, population))
    )
    return MappingProxyType(
        {
            fact_type_id: tuple(rows)
            for fact_type_id, rows in extension_core.relation_facts(calculated.extensions).items()
        }
    )


# B1: the pinned FunctionDefs above remain byte-identical. Public lookup is
# rebound only through new-key dispatch, and term-free models delegate directly
# to the aliased legacy callables.


def _guarded_variable_primitives(
    atoms: list[dict[str, Any]], model: Model
) -> dict[str, str | None]:
    """Resolve each variable through its first antecedent binding site."""
    primitives: dict[str, str | None] = {}
    for atom in atoms:
        fact_type_id = str(atom.get("fact_type"))
        binds = atom_bind(atom)
        for role_name, term in binds.items():
            variable = _guarded_variable(term)
            if variable is None or variable in primitives:
                continue
            object_type = _role_object_type(model, fact_type_id, str(role_name))
            primitives[variable] = (
                resolve_primitive(object_type, model) if object_type is not None else None
            )
    return primitives


def _guarded_ground_atom(
    atom: dict[str, Any], binding: dict[str, Any]
) -> tuple[str, list[str], tuple[tuple[Any, ...], ...]] | None:
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return None
    role_names: list[str] = []
    values: list[tuple[Any, ...]] = []
    for role_name, term in binds.items():
        variable = _guarded_variable(term)
        if variable is not None:
            if variable not in binding:
                return None
            term = binding[variable]
        role_names.append(str(role_name))
        values.append(_identity_key(term))
    return str(atom.get("fact_type")), role_names, tuple(values)


def _guarded_atom_index(
    atom: dict[str, Any], population: Population
) -> tuple[str, list[str], set[tuple[tuple[Any, ...], ...]]] | None:
    binds = atom_bind(atom)
    if not isinstance(binds, dict):
        return None
    fact_type_id = str(atom.get("fact_type"))
    role_names = [str(role_name) for role_name in binds]
    rows: set[tuple[tuple[Any, ...], ...]] = set()
    facts = population.facts.get(fact_type_id, [])
    if not isinstance(facts, Sequence):
        return fact_type_id, role_names, rows
    for fact in facts:
        if isinstance(fact, Mapping) and all(role_name in fact for role_name in role_names):
            rows.add(tuple(_identity_key(fact[role_name]) for role_name in role_names))
    return fact_type_id, role_names, rows


_PHASE3_LEGACY_CHECK = check_legacy


def _guarded_term_failure(
    constraint: Mapping[str, Any], population: Population | extension_core.RuledFactView
) -> extension_core.RelationUnavailable | None:
    """Return the first exact-term failure in an admitted guarded comparison."""
    consequent = constraint.get("consequent")
    comparison = consequent.get("comparison") if isinstance(consequent, Mapping) else None
    if not isinstance(comparison, Mapping):
        return None
    operands = (comparison.get("left"), comparison.get("right"))
    from gnd.terms import is_temporal_node, temporal_nodes

    if any(is_temporal_node(node) for operand in operands for _, node in temporal_nodes(operand)):
        return None  # The streaming correspondence evaluator owns temporal failures.
    if not any(is_function_term(operand) for operand in operands):
        return None
    antecedent = constraint.get("antecedent")
    if not isinstance(antecedent, list):
        return None
    for binding in _guarded_bindings(antecedent, population):
        exact_binding = {variable.removeprefix("$"): value for variable, value in binding.items()}
        for operand in operands:
            result = evaluate_term(operand, exact_binding)
            if not result.available:
                return extension_core.RelationUnavailable(
                    "<guarded>",
                    str(result.reason),
                    MappingProxyType(dict(exact_binding)),
                )
        record_branch("snapshot:guarded:comparison:exact-success")
    return None


def _term_unavailable_constraint_verdict(
    constraint: dict[str, Any],
    fact_type: dict[str, Any] | None,
    ref: str,
    unavailable: extension_core.RelationUnavailable,
) -> ConstraintVerdict:
    family = str(constraint.get("type"))
    reason = unavailable.reason
    if reason not in extension_core.EXACT_DERIVATION_REASON_CODES:
        reason = "term:dependency-unavailable"
    event = {
        "term:mod-zero": "unchecked-mod-zero",
        "term:exact-value-too-wide": "unchecked-exact-value-too-wide",
        "term:dependency-unavailable": "unchecked-dependency-unavailable",
        "term:div-zero": "unchecked-div-zero",
        "term:sqrt-negative": "unchecked-sqrt-negative",
        "term:haversine-coordinate-range": "unchecked-haversine-coordinate-range",
        "term:float-overflow": "unchecked-float-overflow",
    }[reason]
    return ConstraintVerdict(
        constraint_ref=ref,
        constraint_type=family,
        modality=str(constraint.get("modality")),
        source=str(constraint.get("source", "")),
        status=str(constraint.get("status", "")),
        verdict="unchecked",
        message=(
            f"Constraint '{ref}' is unavailable because exact term evaluation failed: "
            f"{unavailable.reason}; binding={dict(unavailable.binding)!r}."
        ),
        reason_code=reason,
        scope_id=f"snapshot:{family}:{constraint_variant(constraint, fact_type)}:{event}",
    )


def _record_aggregate_guarded_outcomes(model: Model, verdicts: Sequence[ConstraintVerdict]) -> None:
    """Trace guarded verdicts whose antecedent reads an aggregate head."""
    aggregate_heads = {
        str(fact_type.get("id"))
        for fact_type in ModelIndex.for_model(model).iter_fact_types()
        if isinstance((rule := fact_type.get("derivation_rule")), dict)
        and isinstance(rule.get("aggregate"), dict)
    }
    if not aggregate_heads:
        return
    by_ref = {verdict.constraint_ref: verdict for verdict in verdicts}
    for index, constraint in enumerate(model.constraints):
        if constraint.get("type") != "guarded" or not any(
            isinstance(atom, dict) and str(atom.get("fact_type")) in aggregate_heads
            for atom in constraint.get("antecedent") or []
        ):
            continue
        verdict = by_ref.get(positional_constraint_ref(None, index))
        if verdict is not None and verdict.verdict in {"pass", "fail", "unchecked"}:
            record_branch(f"snapshot:guarded:aggregate:{verdict.verdict}")


def _partial_constraint_report(
    model: Model, population: Population, report: CheckReport,
) -> CheckReport:
    if not extension_core.PARTIAL_OPAQUE.get() or not model.constraints and not any(
        fact_type.get("constraints") for fact_type in ModelIndex.for_model(model).iter_fact_types()
    ):
        return report
    calculated = extension_core.evaluate_stratified_extensions(
        model, extension_core.base_relations(model, population), exact=extension_core.model_uses_exact_derivations(model)
    )
    possible = getattr(calculated.extensions, "possible", {})
    uncertain_heads = {
        head for head, rows in possible.items()
        if any(isinstance(value, extension_core.Wildcard) for row in rows for value in row)
    }
    if not uncertain_heads:
        return report
    by_ref: dict[str, tuple[dict[str, Any], dict[str, Any] | None]] = {}
    for fact_type in ModelIndex.for_model(model).iter_fact_types():
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            by_ref[positional_constraint_ref(str(fact_type.get("id")), index)] = (constraint, fact_type)
    for index, constraint in enumerate(model.constraints):
        by_ref[positional_constraint_ref(None, index)] = (constraint, None)
    changed = False
    verdicts = []
    for verdict in report.verdicts:
        pair = by_ref.get(verdict.constraint_ref)
        if pair is None or verdict.verdict not in {"pass", "vacuous", "fail"}:
            verdicts.append(verdict)
            continue
        constraint, fact_type = pair
        subject = _scope_fact_types(constraint, verdict.constraint_type, model, fact_type)
        if not uncertain_heads.intersection(subject):
            verdicts.append(verdict)
            continue
        if verdict.verdict == "fail" and verdict.constraint_type == "uniqueness":
            # A duplicate among definite rows remains a conclusive failure.
            verdicts.append(verdict)
            continue
        if verdict.verdict == "fail" and verdict.constraint_type == "subset":
            superset = constraint.get("superset_role_seq") or []
            subset = constraint.get("subset_role_seq") or []
            heads = {str(ref.get("fact_type")) for ref in superset}
            if len(heads) == 1 and next(iter(heads)) in uncertain_heads:
                head = next(iter(heads))
                roles = [str(role.get("role_name")) for role in next(
                    ft for ft in model.fact_types if ft.get("id") == head
                ).get("roles") or []]
                patterns = [tuple(row[roles.index(str(ref.get("role")))] for ref in superset)
                            for row in possible[head]]
                try:
                    demands = _role_seq_tuples(model, population, subset)
                    if any(not any(all(extension_core.partial_compatible(a, b) for a, b in zip(
                        demand, pattern, strict=True)) for pattern in patterns)
                           for demand in demands):
                        verdicts.append(verdict)
                        continue
                except (TypeError, ValueError):
                    pass
            else:
                verdicts.append(verdict)
                continue
        if verdict.verdict == "pass" and fact_type is not None and verdict.constraint_type == "uniqueness":
            head = str(fact_type.get("id"))
            roles = [str(role.get("role_name")) for role in fact_type.get("roles") or []]
            keys = [tuple(row[roles.index(role)] for role in constraint.get("roles") or [])
                    for row in possible[head]]
            if (all(not isinstance(value, extension_core.Wildcard) for key in keys for value in key)
                    and len(set(keys)) == len(keys)):
                verdicts.append(verdict)
                continue
        changed = True
        variant = constraint_variant(constraint, fact_type)
        verdicts.append(ConstraintVerdict(
            constraint_ref=verdict.constraint_ref,
            constraint_type=verdict.constraint_type,
            modality=verdict.modality,
            source=verdict.source,
            status=verdict.status,
            verdict="unchecked",
            message=f"Constraint '{verdict.constraint_ref}' reads a possible-only derived row.",
            reason_code="derived-unknown",
            scope_id=f"snapshot:{verdict.constraint_type}:{variant}:unchecked-derived-unknown",
        ))
    return report.model_copy(update={
        "verdicts": verdicts,
        "admission_projection": report.snapshot_projection,
        "snapshot_projection": None,
    }) if changed else report


def _check_dispatch(model: Model, population: Population) -> CheckReport:
    """Preserve exact-term unavailability instead of consuming an empty relation."""
    report = _partial_constraint_report(
        model, population, check_legacy(model, population)
    )
    if not extension_core.model_uses_exact_derivations(model) and not any(
        isinstance(constraint, dict)
        and str(constraint.get("type")) == "guarded"
        and _guarded_term_failure(constraint, population) is not None
        for constraint in model.constraints
    ):
        return report

    calculated = extension_core.exact_extension_calculator(model, extension_core.base_relations(model, population))
    unavailable = calculated.extensions.unavailable
    effective_view = extension_core.constraint_view_dispatch(model, population, calculated.extensions)
    replacements: dict[str, ConstraintVerdict] = {}
    report_verdicts = {verdict.constraint_ref: verdict for verdict in report.verdicts}
    for fact_type in ModelIndex.for_model(model).iter_fact_types():
        for index, constraint in enumerate(fact_type.get("constraints") or []):
            ref = positional_constraint_ref(str(fact_type.get("id")), index)
            dependency = next(
                (
                    unavailable[subject]
                    for subject in _scope_fact_types(
                        constraint, str(constraint.get("type")), model, fact_type
                    )
                    if subject in unavailable
                ),
                None,
            )
            if dependency is not None:
                replacements[ref] = _term_unavailable_constraint_verdict(
                    constraint, fact_type, ref, dependency
                )
    for index, constraint in enumerate(model.constraints):
        ref = positional_constraint_ref(None, index)
        ordinary_verdict = report_verdicts.get(ref)
        if ordinary_verdict is not None and ordinary_verdict.reason_code == "join-disconnected":
            # The ordinary checker has already refused this antecedent join.
            # Exact-term dependency post-processing must not rejoin it and
            # replace that named refusal with either an exception or a term
            # availability result.
            continue
        dependency_scope = _scope_fact_types(
            constraint, str(constraint.get("type")), model, None
        )
        # Exact-term unavailability is a dependency check, not a change to the
        # antecedent-only subject scope used for guarded vacuity.
        dependency = next(
            (unavailable[subject] for subject in dependency_scope if subject in unavailable),
            None,
        )
        exists_has_no_antecedent_bindings = False
        if str(constraint.get("type")) == "guarded":
            consequent = constraint.get("consequent")
            exists = consequent.get("exists") if isinstance(consequent, dict) else None
            atoms = exists.get("atoms") if isinstance(exists, dict) else None
            if isinstance(atoms, list):
                antecedent = constraint.get("antecedent")
                antecedent_bindings = (
                    _guarded_bindings(antecedent, effective_view)
                    if isinstance(antecedent, list)
                    else []
                )
                exists_has_no_antecedent_bindings = not antecedent_bindings
                exists_sources = [
                    str(atom.get("fact_type"))
                    for atom in atoms
                    if isinstance(atom, dict) and atom.get("fact_type") is not None
                ]
                # The ordinary guarded verdict has already applied vacuity and
                # coverage precedence. Only replace it with source-term
                # unavailability when there are antecedent instances and every
                # existential source is covered.
                if dependency is None and antecedent_bindings and all(
                    subject in population.covers for subject in exists_sources
                ):
                    dependency = next(
                        (unavailable[subject] for subject in exists_sources if subject in unavailable),
                        None,
                    )
        term_dependency = (
            None
            if exists_has_no_antecedent_bindings
            else _guarded_term_failure(constraint, effective_view)
        )
        dependency = dependency or term_dependency
        if dependency is not None:
            replacements[ref] = _term_unavailable_constraint_verdict(
                constraint, None, ref, dependency
            )
    if not replacements:
        _record_aggregate_guarded_outcomes(model, report.verdicts)
        return report
    updated = report.model_copy(
        update={
            "verdicts": [
                replacements.get(verdict.constraint_ref, verdict) for verdict in report.verdicts
            ],
            "admission_projection": report.snapshot_projection or report.admission_projection,
            "snapshot_projection": None,
        }
    )
    _record_aggregate_guarded_outcomes(model, updated.verdicts)
    return updated


def _anchored_verdicts(
    model: Model,
    population: Population,
    anchors: Any,
    document_bytes: bytes | None,
) -> dict[str, ConstraintVerdict]:
    from gnd.anchor_identity import anchor_normalize
    from gnd.anchors import (
        canonical_document_text,
        lexical_ranges,
        recognised_ranges,
        recognition_index,
        recognition_target,
    )

    obligations = [
        (fact_type, index, constraint)
        for fact_type in ModelIndex.for_model(model).iter_fact_types()
        for index, constraint in enumerate(fact_type.get("constraints") or [])
        if constraint.get("type") == "anchored"
    ]
    if not obligations:
        return {}
    source = None if document_bytes is None else canonical_document_text(document_bytes)
    records = {}
    if anchors is not None:
        for record in anchors.anchors:
            key = (record["fact_key"]["fact_type"],
                   tuple((name, type(value).__name__, repr(value)) for name, value in sorted(record["fact_key"]["roles"].items())),
                   record["role"])
            records[key] = record
    lexical_wanted: dict[str, set[int]] = {}
    for record in records.values():
        value = record["fact_key"]["roles"][record["role"]]
        if isinstance(value, str):
            lexical_wanted.setdefault(anchor_normalize(value), set()).add(record["occurrence"])
    indexed = (
        lexical_ranges(source, set(lexical_wanted), wanted_occurrences=lexical_wanted)
        if source is not None else {}
    )
    recogniser_kinds = {
        kind for _, _, constraint in obligations for kind in constraint.get("recognise") or []
    }
    recognisers_by_role: dict[tuple[str, str], set[str]] = {}
    for fact_type, _, constraint in obligations:
        if constraint.get("recognise"):
            key = (str(fact_type["id"]), str(constraint["role"]))
            recognisers_by_role.setdefault(key, set()).update(constraint["recognise"])
    recognition_limits: dict[str, dict[Any, int]] = {}
    for record in records.values():
        fact_type = record["fact_key"]["fact_type"]
        role = record["role"]
        value = record["fact_key"]["roles"][role]
        for kind in recognisers_by_role.get((fact_type, role), []):
            target = recognition_target(kind, value)
            cap = recognition_limits.setdefault(kind, {})
            cap[target] = max(cap.get(target, 0), record["occurrence"])
    recognised = (
        recognition_index(source, recogniser_kinds, limits=recognition_limits)
        if source is not None else {}
    )
    recognition_cache: dict[tuple[tuple[str, ...], str, str], list[tuple[int, int]]] = {}
    replacements = {}
    for fact_type, index, constraint in obligations:
        fact_id = str(fact_type["id"])
        reference = positional_constraint_ref(fact_id, index)
        variant = "role" if constraint.get("role") is not None else "all"
        rows = population.facts.get(fact_id, [])
        failed = []
        failed_refs: set[int] = set()
        uncertain = False
        opaque_refs = {
            row_index
            for row_index, row in enumerate(rows)
            for role in fact_type.get("roles") or []
            if constraint.get("role") is None or constraint["role"] == role["role_name"]
            if isinstance(row.get(str(role["role_name"])), dict)
            and set(row[str(role["role_name"])]) == {"$opaque"}
        }
        if opaque_refs:
            verdict, event, reason = "unchecked", "opaque-value", "opaque-value"
            failed_refs.update(opaque_refs)
        elif anchors is None:
            verdict, event, reason = "unchecked", "sidecar-absent", "anchor-sidecar-absent"
        elif not rows:
            verdict, event, reason = "vacuous", "vacuous", None
        else:
            for row_index, row in enumerate(rows):
                for role in fact_type.get("roles") or []:
                    role_name = str(role["role_name"])
                    if constraint.get("role") is not None and constraint["role"] != role_name:
                        continue
                    value = row[role_name]
                    key = (fact_id, tuple((name, type(item).__name__, repr(item)) for name, item in sorted(row.items())), role_name)
                    record = records.get(key)
                    if record is None:
                        failed.append({"fact_type": fact_id, "roles": row})
                        failed_refs.add(row_index)
                        continue
                    span = record["span"]
                    recognisers = constraint.get("recognise") or []
                    if recognisers:
                        cache_key = (tuple(recognisers), type(value).__name__, repr(value))
                        ranges = recognition_cache.get(cache_key)
                        if ranges is None:
                            ranges = sorted({
                                pair for kind in recognisers
                                for pair in recognised_ranges(recognised, kind, value)
                            })
                            recognition_cache[cache_key] = ranges
                    elif isinstance(value, str):
                        ranges = indexed.get(anchor_normalize(value), {})
                    else:
                        uncertain = True
                        continue
                    occurrence = record["occurrence"]
                    selected_range = (
                        ranges.get(occurrence) if isinstance(ranges, dict)
                        else ranges[occurrence] if occurrence < len(ranges) else None
                    )
                    if selected_range is None or not (span["start"] <= selected_range[0] and selected_range[1] <= span["end"]):
                        failed.append({"fact_type": fact_id, "roles": row})
                        failed_refs.add(row_index)
            if failed:
                verdict = "warning" if constraint.get("modality") == "deontic" else "fail"
                event, reason = "violated", None
            elif uncertain:
                verdict, event, reason = "unchecked", "non-lexical", "anchor-non-lexical"
            else:
                verdict, event, reason = "pass", "clean", None
        scope = (
            "applicability:opaque:n-a:opaque-value"
            if event == "opaque-value"
            else f"snapshot:anchored:{variant}:{event}"
        )
        if event == "violated":
            scope += f":{constraint.get('modality', 'alethic')}"
        replacements[reference] = ConstraintVerdict(
            scope_id=scope, constraint_ref=reference, constraint_type="anchored",
            modality=str(constraint.get("modality", "alethic")),
            source=str(constraint["source"]), status=str(constraint["status"]),
            verdict=verdict, reason_code=reason,
            message=f"Source anchor {verdict} for {fact_id}.",
            offending_facts=failed,
            fact_refs=[{"fact_type": fact_id, "index": row_index} for row_index in sorted(failed_refs)],
        )
    return replacements


def check_with_anchors(
    model: Model,
    population: Population,
    *,
    anchors: Any = None,
    document_bytes: bytes | None = None,
) -> CheckReport:
    report = _check_dispatch(model, population)
    replacements = _anchored_verdicts(model, population, anchors, document_bytes)
    if not replacements:
        return report
    return report.model_copy(update={
        "verdicts": [replacements.get(row.constraint_ref, row) for row in report.verdicts],
        "snapshot_projection": None,
        "admission_projection": report.snapshot_projection,
    })


def check(
    model: Model, population: Population, *, references: BoundReferenceContext | None = None,
    compiled_operations: bool = False,
) -> CheckReport:
    if not isinstance(compiled_operations, bool):
        raise TypeError('compiled_operations must be a boolean')
    if model.reference_populations:
        from gnd.model import bind_population, is_bound_population, resolve_context

        context = resolve_context(model, references)
        if not is_bound_population(model, population, context):
            population = bind_population(model, population, references=context).combined
    with extension_core.calculation_scope(model, population):
        token = extension_core.PARTIAL_OPAQUE.set(True) if compiled_operations else None
        try:
            report = _check_dispatch(model, population)
            if compiled_operations:
                from gnd.compiled_obligations import compose
                report = compose(model, population, report)
            return report
        finally:
            if token is not None:
                extension_core.PARTIAL_OPAQUE.reset(token)


def check_partial(model: Model, population: Population) -> CheckReport:
    """Evaluate opaque input with the three-valued internal extension view."""
    token = extension_core.PARTIAL_OPAQUE.set(True)
    try:
        return check(model, population)
    finally:
        extension_core.PARTIAL_OPAQUE.reset(token)


def check_with_anchors_partial(
    model: Model, population: Population, *, anchors: Any = None,
    document_bytes: bytes | None = None,
) -> CheckReport:
    """Use the same opaque semantics when an anchored check is requested."""
    token = extension_core.PARTIAL_OPAQUE.set(True)
    try:
        return check_with_anchors(
            model, population, anchors=anchors, document_bytes=document_bytes
        )
    finally:
        extension_core.PARTIAL_OPAQUE.reset(token)


effective_view = extension_core.effective_view

def _family_message_ring(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    variant = str(constraint.get("variant"))
    return verbalize.ring_message(
        variant,
        str((fact_type or {}).get("id")),
        [(variant, tuple(row)) for row in witness] if violated else [],
    )


def _family_message_mandatory(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    role = str(constraint.get("role"))
    object_type = _role_object_type(model, str((fact_type or {}).get("id")), role) or role
    return verbalize.mandatory_message(
        object_type, role, str((fact_type or {}).get("id")), witness if violated else []
    )


def _family_message_mandatory_disjunctive(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    refs = list(constraint.get("role_refs") or [])
    first = refs[0] if refs else {}
    object_type = (
        _role_object_type(model, str(first.get("fact_type")), str(first.get("role")))
        or "object"
    )
    return verbalize.mandatory_disjunctive_message(
        object_type, _ref_labels(refs), witness if violated else []
    )


def _family_message_uniqueness(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    if fact_type is not None:
        roles = [str(row) for row in constraint.get("roles") or []]
        groups = _identity_counts(
            tuple(fact[role] for role in roles)
            for fact in population.facts.get(str(fact_type.get("id")), [])
            if all(role in fact for role in roles)
        )
        offending = [(tuple(value), count) for value, count in groups.values() if count > 1]
        return verbalize.uniqueness_message(roles, str(fact_type.get("id")), offending)
    refs = list(constraint.get("role_refs") or [])
    groups = _identity_counts(_join_rows(model, population, refs))
    offending = [(tuple(value), count) for value, count in groups.values() if count > 1]
    return verbalize.uniqueness_external_message(_ref_labels(refs), offending)


def _family_message_value(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    subject = str(constraint.get("object_type"))
    offending = witness if violated else []
    if constraint.get("allowed") is not None:
        return verbalize.value_enum_message(
            subject, list(constraint.get("allowed") or []), offending
        )
    if constraint.get("ranges") is not None:
        return verbalize.value_ranges_message(
            subject, list(constraint.get("ranges") or []), offending
        )
    bounds = constraint.get("range") or {}
    return verbalize.value_range_message(
        subject, bounds.get("min"), bounds.get("max"), offending
    )


def _family_message_frequency(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    bound = constraint.get("bound") or {}
    if fact_type is not None:
        roles = [str(row) for row in constraint.get("roles") or []]
        values = _project(population, str(fact_type.get("id")), roles)
        subject = f"{', '.join(roles)} in {fact_type.get('id')}"
    else:
        refs = list(constraint.get("role_refs") or [])
        values = _join_rows(model, population, refs)
        subject = ", ".join(_ref_labels(refs))
    groups = _identity_counts(values)
    keys = {_identity_key(tuple(row)) for row in witness}
    offending = [
        (tuple(value), count) for identity, (value, count) in groups.items() if identity in keys
    ]
    return verbalize.frequency_message(subject, bound.get("min"), bound.get("max"), offending)


def _family_message_subset(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    seq_a = list(
        constraint.get("subset_role_seq")
        if family == "subset"
        else constraint.get("role_seq_a") or []
    )
    seq_b = list(
        constraint.get("superset_role_seq")
        if family == "subset"
        else constraint.get("role_seq_b") or []
    )
    tuples = [tuple(row) for row in witness] if violated else []
    if family == "subset":
        return verbalize.subset_message(_ref_labels(seq_a), _ref_labels(seq_b), tuples)
    if family == "exclusion":
        return verbalize.exclusion_message(_ref_labels(seq_a), _ref_labels(seq_b), tuples)
    actual_a = _IdentitySet(_role_seq_tuples(model, population, seq_a))
    only_a = [row for row in tuples if row in actual_a]
    only_b = [row for row in tuples if row not in actual_a]
    return verbalize.equality_message(_ref_labels(seq_a), _ref_labels(seq_b), only_a, only_b)


def _family_message_exclusive_or(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    sequences = [list(row or []) for row in constraint.get("role_seqs") or []]
    labels = [", ".join(_ref_labels(row)) for row in sequences]
    if all(len(row) == 1 for row in sequences):
        refs = [row[0] for row in sequences]
        first = refs[0] if refs else {}
        object_type = (
            _role_object_type(model, str(first.get("fact_type")), str(first.get("role")))
            or "object"
        )
        populations = [
            _IdentitySet(_role_seq_tuples(model, population, row)) for row in sequences
        ]
        both: list[Any] = []
        neither: list[Any] = []
        for row in witness if violated else []:
            value = row[0] if isinstance(row, list) and len(row) == 1 else row
            if sum((value,) in values for values in populations) > 1:
                both.append(value)
            else:
                neither.append(value)
        return verbalize.exclusive_or_message(object_type, labels, both, neither)
    return verbalize.exclusive_or_exclusion_violated_message(
        labels, [tuple(row) for row in witness]
    )


def _family_message_value_comparison(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    left = constraint.get("role_a")
    right = constraint.get("role_b")
    labels = _ref_labels([left, right]) if isinstance(left, dict) else [str(left), str(right)]
    return verbalize.value_comparison_message(
        labels[0],
        str(constraint.get("operator")),
        labels[1],
        [tuple(row) for row in witness] if violated else [],
    )


def _family_message_cardinality(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    bounds = constraint.get("bound") or {}
    if constraint.get("scope") == "object":
        object_type = str(constraint.get("object_type"))
        subject = f"{object_type} instance"
        count = len(_instances_of(object_type, model, population))
    else:
        role_ref = constraint.get("role_ref") or {}
        fact_type_id = str(role_ref.get("fact_type"))
        role_name = str(role_ref.get("role"))
        subject = f"distinct player of {fact_type_id}.{role_name}"
        count = len(_IdentitySet(_project(population, fact_type_id, [role_name])))
    return verbalize.cardinality_message(
        subject, bounds.get("min"), bounds.get("max"), count, violated
    )


def _family_message_subtype_partition(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    subtypes = [str(row) for row in constraint.get("subtypes") or []]
    member_sets = {subtype: _instances_of(subtype, model, population) for subtype in subtypes}
    values = [row[0] for row in witness] if violated else []
    both = [
        value
        for value in values
        if constraint.get("exclusive")
        and sum(value in members for members in member_sets.values()) > 1
    ]
    neither = [value for value in values if value not in both]
    return verbalize.subtype_partition_message(
        str(constraint.get("supertype")),
        subtypes,
        both,
        neither,
    )


def _family_message_guarded(constraint, fact_type, finding, witness, model, population, family, verdict, scope_id, violated):
    kind = next(
        (
            key
            for key in ("comparison", "atom", "absence", "exists")
            if key in (constraint.get("consequent") or {})
        ),
        "consequent",
    )
    from gnd.terms import is_temporal_node, temporal_nodes

    if any(is_temporal_node(node) for _, node in temporal_nodes(constraint.get("consequent"))):
        return verbalize.temporal_guarded_message(kind, witness if violated else [])
    bindings = _guarded_bindings(list(constraint.get("antecedent") or []), population)
    if model.reference_populations and len(bindings) > 100_000:
        from gnd.correspondence import ReferenceJoinLimit

        raise ReferenceJoinLimit("binding producer escaped reference work budget")
    return verbalize.guarded_message(kind, len(bindings), witness if violated else [])


def _flat_projected_witness(witness):
    rows = [dict(row) if isinstance(row, dict) else list(row) for row in witness]
    return [row[0] for row in rows]


def _row_projected_witness(witness):
    return [dict(row) if isinstance(row, dict) else list(row) for row in witness]


def _family_message_default(
    constraint, fact_type, finding, witness, model, population,
    family, verdict, scope_id, violated,
):
    return verbalize.constraint_message(
        family, verdict, fact_type_id=str((fact_type or {}).get('id')) or None,
        detail=(f'witness={witness!r}' if witness else ''),
    )


check_legacy.__module__ = 'gnd.checker'
_observe_phase1_compatibility.__module__ = 'gnd.checker'
_plain_projected_witness.__module__ = 'gnd.checker'
_correspondence_message.__module__ = 'gnd.checker'
_value_comparison_message_inputs.__module__ = 'gnd.checker'
_compatibility_trace.__module__ = 'gnd.checker'
_no_observable_subjects_message.__module__ = 'gnd.checker'
_JoinSubjectRow.__module__ = 'gnd.checker'
_joining_subject_sequences.__module__ = 'gnd.checker'
_no_joined_rows_message.__module__ = 'gnd.checker'
_vacuity_message.__module__ = 'gnd.checker'
JoinAmbiguousError.__module__ = 'gnd.checker'
_project.__module__ = 'gnd.checker'
_identity_counts.__module__ = 'gnd.checker'
_join_rows.__module__ = 'gnd.checker'
_require_joinable.__module__ = 'gnd.checker'
_role_seq_tuples.__module__ = 'gnd.checker'
_ref_labels.__module__ = 'gnd.checker'
_violation_verdict.__module__ = 'gnd.checker'
_orderable.__module__ = 'gnd.checker'
_in_range.__module__ = 'gnd.checker'
_find_cycle.__module__ = 'gnd.checker'
_dfs_cycle.__module__ = 'gnd.checker'
_ring_component_violations.__module__ = 'gnd.checker'
_typed_comparison_values.__module__ = 'gnd.checker'
_compare.__module__ = 'gnd.checker'
_guarded_variable.__module__ = 'gnd.checker'
_FactView.__module__ = 'gnd.checker'
_guarded_bindings.__module__ = 'gnd.checker'
structured_extension_facts.__module__ = 'gnd.checker'
_guarded_variable_primitives.__module__ = 'gnd.checker'
_guarded_ground_atom.__module__ = 'gnd.checker'
_guarded_atom_index.__module__ = 'gnd.checker'
_guarded_term_failure.__module__ = 'gnd.checker'
_term_unavailable_constraint_verdict.__module__ = 'gnd.checker'
_record_aggregate_guarded_outcomes.__module__ = 'gnd.checker'
_partial_constraint_report.__module__ = 'gnd.checker'
_check_dispatch.__module__ = 'gnd.checker'
_anchored_verdicts.__module__ = 'gnd.checker'
check_with_anchors.__module__ = 'gnd.checker'
check.__module__ = 'gnd.checker'
check_partial.__module__ = 'gnd.checker'
check_with_anchors_partial.__module__ = 'gnd.checker'
_family_message_ring.__module__ = 'gnd.checker'
_family_message_mandatory.__module__ = 'gnd.checker'
_family_message_mandatory_disjunctive.__module__ = 'gnd.checker'
_family_message_uniqueness.__module__ = 'gnd.checker'
_family_message_value.__module__ = 'gnd.checker'
_family_message_frequency.__module__ = 'gnd.checker'
_family_message_subset.__module__ = 'gnd.checker'
_family_message_exclusive_or.__module__ = 'gnd.checker'
_family_message_value_comparison.__module__ = 'gnd.checker'
_family_message_cardinality.__module__ = 'gnd.checker'
_family_message_subtype_partition.__module__ = 'gnd.checker'
_family_message_guarded.__module__ = 'gnd.checker'
_flat_projected_witness.__module__ = 'gnd.checker'
_row_projected_witness.__module__ = 'gnd.checker'
_family_message_default.__module__ = 'gnd.checker'
_JoinSubjectRow.__dict__['__new__'].__func__.__module__ = 'namedtuple__JoinSubjectRow'
JoinAmbiguousError.__dict__['__init__'].__module__ = 'gnd.checker'
