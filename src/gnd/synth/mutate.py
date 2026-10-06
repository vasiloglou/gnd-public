"""RF4 compatibility surface for mutation oracle."""
from __future__ import annotations

from gnd.synth.oracle.mutations import (
    IMPLEMENTED_FAMILIES as IMPLEMENTED_FAMILIES,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    OPERATORS as OPERATORS,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    RING_COMPONENTS as _RING_COMPONENTS,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    RING_VARIANTS as _RING_VARIANTS,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    XOR_MULTIROLE_MECHANISM as _XOR_MULTIROLE_MECHANISM,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    Any as Any,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    Callable as Callable,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    CheckReport as CheckReport,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    ExpectedState as ExpectedState,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    ExpectedStateData as ExpectedStateData,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    GeneratorError as GeneratorError,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    Mapping as Mapping,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    Model as Model,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    Mutation as Mutation,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    Path as Path,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    PopulationValidationError as PopulationValidationError,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    PredictionMismatch as PredictionMismatch,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    Random as Random,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    Template as _Template,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    ViolatingCase as ViolatingCase,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_add_missing_subset as _applies_add_missing_subset,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_add_out_of_range_new_entity as _applies_add_out_of_range_new_entity,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_add_overlap as _applies_add_overlap,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_add_past_ceiling as _applies_add_past_ceiling,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_add_self_loop as _applies_add_self_loop,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_close_2_cycle as _applies_close_2_cycle,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_close_3_cycle as _applies_close_3_cycle,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_drop_covers as _applies_drop_covers,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_drop_from_group as _applies_drop_from_group,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_drop_joined_below_min as _applies_drop_joined_below_min,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_duplicate_covered as _applies_duplicate_covered,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_duplicate_joined as _applies_duplicate_joined,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_edit_out_of_range as _applies_edit_out_of_range,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_empty_ft as _applies_empty_ft,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_exact_duplicate as _applies_exact_duplicate,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_introduce_distinct as _applies_introduce_distinct,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_invert_vc as _applies_invert_vc,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_new_entity_plays as _applies_new_entity_plays,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_place_two_subtypes as _applies_place_two_subtypes,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_play_both as _applies_play_both,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_play_neither as _applies_play_neither,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_remove_all_subtypes as _applies_remove_all_subtypes,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_remove_disjunctive as _applies_remove_disjunctive,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_remove_equality_side as _applies_remove_equality_side,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_remove_exists_witness as _applies_remove_exists_witness,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    applies_roster_add as _applies_roster_add,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_add_missing_subset as _apply_add_missing_subset,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_add_out_of_range_new_entity as _apply_add_out_of_range_new_entity,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_add_overlap as _apply_add_overlap,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_add_past_ceiling as _apply_add_past_ceiling,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_add_self_loop as _apply_add_self_loop,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_close_2_cycle as _apply_close_2_cycle,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_close_3_cycle as _apply_close_3_cycle,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_drop_covers as _apply_drop_covers,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_drop_from_group as _apply_drop_from_group,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_drop_joined_below_min as _apply_drop_joined_below_min,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_duplicate_covered as _apply_duplicate_covered,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_duplicate_joined as _apply_duplicate_joined,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_edit_out_of_range as _apply_edit_out_of_range,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_empty_ft as _apply_empty_ft,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_exact_duplicate as _apply_exact_duplicate,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_introduce_distinct as _apply_introduce_distinct,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_invert_vc as _apply_invert_vc,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_new_entity_plays as _apply_new_entity_plays,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_place_two_subtypes as _apply_place_two_subtypes,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_play_both as _apply_play_both,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_play_neither as _apply_play_neither,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_remove_all_subtypes as _apply_remove_all_subtypes,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_remove_disjunctive as _apply_remove_disjunctive,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_remove_equality_side as _apply_remove_equality_side,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_remove_exists_witness as _apply_remove_exists_witness,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_remove_last_covering as _apply_remove_last_covering,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    apply_roster_add as _apply_roster_add,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    check as check,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    compare_observed as compare_observed,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    compare_scalar as _compare_scalar,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    compat_all as __all__,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    constraint_iter_with_ref as _constraint_iter_with_ref,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    copy as copy,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    coverage_target_ft as _coverage_target_ft,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    dataclass as dataclass,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    emit_violating as emit_violating,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    enumerate_violating as enumerate_violating,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    equality_side_removal as _equality_side_removal,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    exists_atom_safe_for_removal as _exists_atom_safe_for_removal,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    family_coverage as family_coverage,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    first_implemented_inline_ref as first_implemented_inline_ref,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    frequency_min_gate as _frequency_min_gate,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    governed_ft_with_entity_role as _governed_ft_with_entity_role,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    guarded_antecedent_bindings as _guarded_antecedent_bindings,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    guarded_exists_witness as _guarded_exists_witness,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    guarded_modular_repair_plan as _guarded_modular_repair_plan,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    has_private_exists_sources as _has_private_exists_sources,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    internal_frequency_groups as _internal_frequency_groups,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    invertible_fact as _invertible_fact,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    itertools as itertools,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    json as json,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    key as _key,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    load_population as load_population,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    mandatory_role_type as _mandatory_role_type,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    normalize_comparison_operands as _normalize_comparison_operands,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    operators_for as operators_for,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    other_ft_with_role as _other_ft_with_role,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    pick_disjunctive_member as _pick_disjunctive_member,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    pick_xor_removable as _pick_xor_removable,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    positional_constraint_ref as positional_constraint_ref,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    remove_one_from_min_group as _remove_one_from_min_group,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    ring_components_of as _ring_components_of,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    ring_edges as _ring_edges,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    ring_gate as _ring_gate,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    role_object as _role_object,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    seq_tuples as _seq_tuples,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.mutations import (
    subset_candidate as _subset_candidate,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    subtype_assertions as _subtype_assertions,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    templates_for as _templates_for,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    uniqueness_conflict as _uniqueness_conflict,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    value_occurrence as _value_occurrence,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.mutations import (
    xor_player_sets as _xor_player_sets,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    AMPLIFICATION_CEILING as _AMPLIFICATION_CEILING,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    JOIN_QUANTIFIER as _JOIN_QUANTIFIER,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    MANDATORY_RELEVANT as _MANDATORY_RELEVANT,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    OBJECT_SCOPED as _OBJECT_SCOPED,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    SKIP as _SKIP,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    UNTYPEABLE as _UNTYPEABLE,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    EmptyValueDomain as EmptyValueDomain,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    complete_row as _complete_row,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    constraint_accepts as constraint_accepts,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    direct_subtypes as _direct_subtypes,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    draw_value_for_constraints as draw_value_for_constraints,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    enforce_value_comparisons as _enforce_value_comparisons,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    existing_members as _existing_members,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    expected_state as expected_state,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.state import (
    facts_of as _facts_of,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    fresh_identifier as _fresh_identifier,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    ft_by_id as _ft_by_id,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    governing_value_constraints as governing_value_constraints,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    guarded_atoms_have_derived_source as _guarded_atoms_have_derived_source,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    guarded_exists_has_derived_source as _guarded_exists_has_derived_source,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    guarded_exists_shape_supported as _guarded_exists_shape_supported,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    is_entity as _is_entity,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    join_vacuous as _join_vacuous,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    make_value as make_value,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    out_of_spec_value as _out_of_spec_value,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    popvalidate as popvalidate,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    predict_violations as predict_violations,  # noqa: PLC0414 -- compatibility surface
)
from gnd.synth.oracle.state import (
    resolve as _resolve,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    role_literal_operands as _role_literal_operands,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    scope_fts as _scope_fts,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    structured_derivation_ids as structured_derivation_ids,  # noqa: PLC0414 -- historical imported binding
)
from gnd.synth.oracle.state import (
    subject_sequences as _subject_sequences,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    subtype_partition_witness as _subtype_partition_witness,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    tuple_key as _tuple_key,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    universe as _universe,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    valid_value as _valid_value,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    value_spec_for as _value_spec_for,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    witness as _witness,  # noqa: F401 -- historical imported binding
)
from gnd.synth.oracle.state import (
    witness_ext as _witness_ext,  # noqa: F401 -- compatibility surface
)
from gnd.synth.oracle.state import (
    xor_single_role as _xor_single_role,  # noqa: F401 -- compatibility surface
)
