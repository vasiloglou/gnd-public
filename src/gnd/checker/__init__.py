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
from gnd.checker._core import _COMPARATORS as _COMPARATORS
from gnd.checker._core import _INVALID_LITERAL as _INVALID_LITERAL
from gnd.checker._core import _JOIN_SUBJECT_SEQS as _JOIN_SUBJECT_SEQS
from gnd.checker._core import _MANDATORY_RELEVANT as _MANDATORY_RELEVANT
from gnd.checker._core import _OBJECT_TYPE_SCOPED as _OBJECT_TYPE_SCOPED
from gnd.checker._core import _PARTIAL_OPAQUE as _PARTIAL_OPAQUE
from gnd.checker._core import _PHASE3_LEGACY_CHECK as _PHASE3_LEGACY_CHECK
from gnd.checker._core import _PHASE3_LEGACY_CONSTRAINT_VIEW as _PHASE3_LEGACY_CONSTRAINT_VIEW
from gnd.checker._core import (
    _PHASE3_LEGACY_EVALUATE_DERIVATIONS as _PHASE3_LEGACY_EVALUATE_DERIVATIONS,
)
from gnd.checker._core import _REFERENCE_PRESENTATION_WORK as _REFERENCE_PRESENTATION_WORK
from gnd.checker._core import _RING_COMPONENTS as _RING_COMPONENTS
from gnd.checker._core import _RING_VARIANTS as _RING_VARIANTS
from gnd.checker._core import _WITNESS_TRACE as _WITNESS_TRACE
from gnd.checker._core import DEFAULT_LIMITS as DEFAULT_LIMITS
from gnd.checker._core import DERIVATION_REASON_CODES as DERIVATION_REASON_CODES
from gnd.checker._core import EXACT_DERIVATION_REASON_CODES as EXACT_DERIVATION_REASON_CODES
from gnd.checker._core import FAMILIES as FAMILIES
from gnd.checker._core import IMPLEMENTED_FAMILIES as IMPLEMENTED_FAMILIES
from gnd.checker._core import MAX_SLICE_CONSTRAINTS as MAX_SLICE_CONSTRAINTS
from gnd.checker._core import UTC as UTC
from gnd.checker._core import AggregateAnalysis as AggregateAnalysis
from gnd.checker._core import Any as Any
from gnd.checker._core import BaseModel as BaseModel
from gnd.checker._core import BoundReferenceContext as BoundReferenceContext
from gnd.checker._core import CycleError as CycleError
from gnd.checker._core import DerivationFinding as DerivationFinding
from gnd.checker._core import DerivationKind as DerivationKind
from gnd.checker._core import DerivationReason as DerivationReason
from gnd.checker._core import DerivationVerdict as DerivationVerdict
from gnd.checker._core import DynamicRefreshWork as DynamicRefreshWork
from gnd.checker._core import ExtensionCalculator as ExtensionCalculator
from gnd.checker._core import FactPath as FactPath
from gnd.checker._core import Field as Field
from gnd.checker._core import IdentityCodecVersion as IdentityCodecVersion
from gnd.checker._core import Iterable as Iterable
from gnd.checker._core import JoinAmbiguousError as JoinAmbiguousError
from gnd.checker._core import JoinDisconnectedError as JoinDisconnectedError
from gnd.checker._core import Literal as Literal
from gnd.checker._core import Mapping as Mapping
from gnd.checker._core import MappingProxyType as MappingProxyType
from gnd.checker._core import Model as Model
from gnd.checker._core import ModelIndex as ModelIndex
from gnd.checker._core import NamedTuple as NamedTuple
from gnd.checker._core import Population as Population
from gnd.checker._core import Protocol as Protocol
from gnd.checker._core import RelationUnavailable as RelationUnavailable
from gnd.checker._core import RowLineage as RowLineage
from gnd.checker._core import Scalar as Scalar
from gnd.checker._core import Sequence as Sequence
from gnd.checker._core import SliceInput as SliceInput
from gnd.checker._core import SliceVerdict as SliceVerdict
from gnd.checker._core import StructuredExtensionView as StructuredExtensionView
from gnd.checker._core import TopologicalSorter as TopologicalSorter
from gnd.checker._core import UnregisteredBranchError as UnregisteredBranchError
from gnd.checker._core import UnvalidatedPopulationError as UnvalidatedPopulationError
from gnd.checker._core import ValidationInfo as ValidationInfo
from gnd.checker._core import VariableResolver as VariableResolver
from gnd.checker._core import _aggregate_bindings as _aggregate_bindings
from gnd.checker._core import _aggregate_identity_token as _aggregate_identity_token
from gnd.checker._core import _anchored_verdicts as _anchored_verdicts
from gnd.checker._core import _apply_negation as _apply_negation
from gnd.checker._core import _base_relations as _base_relations
from gnd.checker._core import _binding_lineages as _binding_lineages
from gnd.checker._core import _check_dispatch as _check_dispatch
from gnd.checker._core import _clause_bindings as _clause_bindings
from gnd.checker._core import _compare as _compare
from gnd.checker._core import _compatibility_trace as _compatibility_trace
from gnd.checker._core import _component_atoms as _component_atoms
from gnd.checker._core import _component_product as _component_product
from gnd.checker._core import _constraint_role_refs as _constraint_role_refs
from gnd.checker._core import _constraint_view as _constraint_view
from gnd.checker._core import _constraint_view_dispatch as _constraint_view_dispatch
from gnd.checker._core import _correspondence_message as _correspondence_message
from gnd.checker._core import _count_term_work as _count_term_work
from gnd.checker._core import _denoting_types as _denoting_types
from gnd.checker._core import _derivation_obligation as _derivation_obligation
from gnd.checker._core import _derivation_variable as _derivation_variable
from gnd.checker._core import _descendant_closure as _descendant_closure
from gnd.checker._core import _dfs_cycle as _dfs_cycle
from gnd.checker._core import _evaluate_derivations as _evaluate_derivations
from gnd.checker._core import _evaluate_derivations_dispatch as _evaluate_derivations_dispatch
from gnd.checker._core import _evaluate_stratified_extensions as _evaluate_stratified_extensions
from gnd.checker._core import _exact_derivation_obligation as _exact_derivation_obligation
from gnd.checker._core import _exact_extension_calculator as _exact_extension_calculator
from gnd.checker._core import _ExactExtensionResult as _ExactExtensionResult
from gnd.checker._core import _ExactExtensions as _ExactExtensions
from gnd.checker._core import _ExactJoinWork as _ExactJoinWork
from gnd.checker._core import _extension_fact_map as _extension_fact_map
from gnd.checker._core import _ExtensionResult as _ExtensionResult
from gnd.checker._core import _fact_type_by_id as _fact_type_by_id
from gnd.checker._core import _FactView as _FactView
from gnd.checker._core import _family_message_cardinality as _family_message_cardinality
from gnd.checker._core import _family_message_default as _family_message_default
from gnd.checker._core import _family_message_exclusive_or as _family_message_exclusive_or
from gnd.checker._core import _family_message_frequency as _family_message_frequency
from gnd.checker._core import _family_message_guarded as _family_message_guarded
from gnd.checker._core import _family_message_mandatory as _family_message_mandatory
from gnd.checker._core import (
    _family_message_mandatory_disjunctive as _family_message_mandatory_disjunctive,
)
from gnd.checker._core import _family_message_ring as _family_message_ring
from gnd.checker._core import _family_message_subset as _family_message_subset
from gnd.checker._core import _family_message_subtype_partition as _family_message_subtype_partition
from gnd.checker._core import _family_message_uniqueness as _family_message_uniqueness
from gnd.checker._core import _family_message_value as _family_message_value
from gnd.checker._core import _family_message_value_comparison as _family_message_value_comparison
from gnd.checker._core import _find_cycle as _find_cycle
from gnd.checker._core import _FixpointJoinWork as _FixpointJoinWork
from gnd.checker._core import _flat_projected_witness as _flat_projected_witness
from gnd.checker._core import _guarded_atom_index as _guarded_atom_index
from gnd.checker._core import _guarded_bindings as _guarded_bindings
from gnd.checker._core import _guarded_ground_atom as _guarded_ground_atom
from gnd.checker._core import _guarded_term_failure as _guarded_term_failure
from gnd.checker._core import _guarded_variable as _guarded_variable
from gnd.checker._core import _guarded_variable_primitives as _guarded_variable_primitives
from gnd.checker._core import _identity_counts as _identity_counts
from gnd.checker._core import _identity_key as _identity_key
from gnd.checker._core import _identity_token as _identity_token
from gnd.checker._core import _IdentitySet as _IdentitySet
from gnd.checker._core import _in_range as _in_range
from gnd.checker._core import _instance_values_of as _instance_values_of
from gnd.checker._core import _instances_of as _instances_of
from gnd.checker._core import _is_implemented as _is_implemented
from gnd.checker._core import _join_rows as _join_rows
from gnd.checker._core import _joined_atom_candidates as _joined_atom_candidates
from gnd.checker._core import _joined_bindings as _joined_bindings
from gnd.checker._core import _joining_subject_sequences as _joining_subject_sequences
from gnd.checker._core import _JoinSubjectRow as _JoinSubjectRow
from gnd.checker._core import _JoinWork as _JoinWork
from gnd.checker._core import _kind_of as _kind_of
from gnd.checker._core import _literal as _literal
from gnd.checker._core import _model_uses_exact_derivations as _model_uses_exact_derivations
from gnd.checker._core import _no_joined_rows_message as _no_joined_rows_message
from gnd.checker._core import _no_observable_subjects_message as _no_observable_subjects_message
from gnd.checker._core import _observe_phase1_compatibility as _observe_phase1_compatibility
from gnd.checker._core import _orderable as _orderable
from gnd.checker._core import _partial_binding_shape as _partial_binding_shape
from gnd.checker._core import _partial_bindings as _partial_bindings
from gnd.checker._core import _partial_clause_rows as _partial_clause_rows
from gnd.checker._core import _partial_compatible as _partial_compatible
from gnd.checker._core import _partial_constraint_report as _partial_constraint_report
from gnd.checker._core import _partial_merge as _partial_merge
from gnd.checker._core import _partial_negation as _partial_negation
from gnd.checker._core import _partial_row_facts as _partial_row_facts
from gnd.checker._core import _partial_token as _partial_token
from gnd.checker._core import _PartialExtensions as _PartialExtensions
from gnd.checker._core import _PartialTermFailure as _PartialTermFailure
from gnd.checker._core import _plain_projected_witness as _plain_projected_witness
from gnd.checker._core import _project as _project
from gnd.checker._core import _project_extension as _project_extension
from gnd.checker._core import _project_lineage as _project_lineage
from gnd.checker._core import _public_refresh_work as _public_refresh_work
from gnd.checker._core import _python_extension_calculator as _python_extension_calculator
from gnd.checker._core import (
    _record_aggregate_guarded_outcomes as _record_aggregate_guarded_outcomes,
)
from gnd.checker._core import _ref_labels as _ref_labels
from gnd.checker._core import _relation_facts as _relation_facts
from gnd.checker._core import _relation_roles as _relation_roles
from gnd.checker._core import _require_joinable as _require_joinable
from gnd.checker._core import _requires_fixpoint as _requires_fixpoint
from gnd.checker._core import _ring_component_violations as _ring_component_violations
from gnd.checker._core import _role_object_type as _role_object_type
from gnd.checker._core import _role_seq_tuples as _role_seq_tuples
from gnd.checker._core import _row_projected_witness as _row_projected_witness
from gnd.checker._core import _rows_by_identity as _rows_by_identity
from gnd.checker._core import _rows_from_facts as _rows_from_facts
from gnd.checker._core import _rule_uses_exact_terms as _rule_uses_exact_terms
from gnd.checker._core import _RuledFactView as _RuledFactView
from gnd.checker._core import _scalar_primitive_compatible as _scalar_primitive_compatible
from gnd.checker._core import _scope_fact_types as _scope_fact_types
from gnd.checker._core import _symbolic_value as _symbolic_value
from gnd.checker._core import (
    _term_unavailable_constraint_verdict as _term_unavailable_constraint_verdict,
)
from gnd.checker._core import _typed_comparison_values as _typed_comparison_values
from gnd.checker._core import _TypedRelation as _TypedRelation
from gnd.checker._core import _vacuity_message as _vacuity_message
from gnd.checker._core import _value_comparison_message_inputs as _value_comparison_message_inputs
from gnd.checker._core import _violation_verdict as _violation_verdict
from gnd.checker._core import _Wildcard as _Wildcard
from gnd.checker._core import _witness as _witness
from gnd.checker._core import _witness_charge as _witness_charge
from gnd.checker._core import _witness_row as _witness_row
from gnd.checker._core import adapt_phase1_slice as adapt_phase1_slice
from gnd.checker._core import analyze_declared_aggregate as analyze_declared_aggregate
from gnd.checker._core import annotations as annotations
from gnd.checker._core import atom_bind as atom_bind
from gnd.checker._core import atom_has_bind as atom_has_bind
from gnd.checker._core import body_components as body_components
from gnd.checker._core import branch as branch
from gnd.checker._core import check as check
from gnd.checker._core import check_legacy as check_legacy
from gnd.checker._core import check_partial as check_partial
from gnd.checker._core import check_with_anchors as check_with_anchors
from gnd.checker._core import check_with_anchors_partial as check_with_anchors_partial
from gnd.checker._core import compare_terms as compare_terms
from gnd.checker._core import constraint_variant as constraint_variant
from gnd.checker._core import constraint_view_legacy as constraint_view_legacy
from gnd.checker._core import dataclass as dataclass
from gnd.checker._core import date as date
from gnd.checker._core import datetime as datetime
from gnd.checker._core import derivation_address as derivation_address
from gnd.checker._core import derivation_claims_against as derivation_claims_against
from gnd.checker._core import derivation_classifications as derivation_classifications
from gnd.checker._core import derivation_dependencies as derivation_dependencies
from gnd.checker._core import derivation_strata as derivation_strata
from gnd.checker._core import effective_view as effective_view
from gnd.checker._core import evaluate_derivations_legacy as evaluate_derivations_legacy
from gnd.checker._core import evaluate_term as evaluate_term
from gnd.checker._core import exact_extension_envelope as exact_extension_envelope
from gnd.checker._core import extension_core as extension_core
from gnd.checker._core import is_function_term as is_function_term
from gnd.checker._core import iter_derivation_clauses as iter_derivation_clauses
from gnd.checker._core import materialize_scalar as materialize_scalar
from gnd.checker._core import math as math
from gnd.checker._core import model_validator as model_validator
from gnd.checker._core import phase1_decide as phase1_decide
from gnd.checker._core import phase1_refusal_reason as phase1_refusal_reason
from gnd.checker._core import positional_constraint_ref as positional_constraint_ref
from gnd.checker._core import record_branch as record_branch
from gnd.checker._core import replace as replace
from gnd.checker._core import resolve_hook as resolve_hook
from gnd.checker._core import resolve_primitive as resolve_primitive
from gnd.checker._core import resolve_reference_value_type as resolve_reference_value_type
from gnd.checker._core import structured_extension_facts as structured_extension_facts
from gnd.checker._core import structured_extension_view as structured_extension_view
from gnd.checker._core import term_variables as term_variables
from gnd.checker._core import time_relative_operand as time_relative_operand
from gnd.checker._core import verbalize as verbalize
from gnd.checker._reports import CheckReport as CheckReport
from gnd.checker._reports import ConstraintVerdict as ConstraintVerdict
from gnd.checker._reports import CoverageEntry as CoverageEntry
from gnd.checker._reports import Phase1Trace as Phase1Trace
from gnd.checker._reports import Verdict as Verdict
from gnd.checker._reports import band as band
