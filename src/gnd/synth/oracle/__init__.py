"""Public independent synthesis oracle and mutation primitives."""

from gnd.synth.oracle.mutations import (
    applies_add_missing_subset as applies_add_missing_subset,
)
from gnd.synth.oracle.mutations import (
    applies_add_overlap as applies_add_overlap,
)
from gnd.synth.oracle.mutations import (
    applies_add_past_ceiling as applies_add_past_ceiling,
)
from gnd.synth.oracle.mutations import (
    applies_add_self_loop as applies_add_self_loop,
)
from gnd.synth.oracle.mutations import (
    applies_close_2_cycle as applies_close_2_cycle,
)
from gnd.synth.oracle.mutations import (
    applies_close_3_cycle as applies_close_3_cycle,
)
from gnd.synth.oracle.mutations import (
    applies_drop_covers as applies_drop_covers,
)
from gnd.synth.oracle.mutations import (
    applies_duplicate_covered as applies_duplicate_covered,
)
from gnd.synth.oracle.mutations import (
    applies_duplicate_joined as applies_duplicate_joined,
)
from gnd.synth.oracle.mutations import (
    applies_exact_duplicate as applies_exact_duplicate,
)
from gnd.synth.oracle.mutations import (
    applies_introduce_distinct as applies_introduce_distinct,
)
from gnd.synth.oracle.mutations import (
    applies_new_entity_plays as applies_new_entity_plays,
)
from gnd.synth.oracle.mutations import (
    applies_place_two_subtypes as applies_place_two_subtypes,
)
from gnd.synth.oracle.mutations import (
    applies_play_both as applies_play_both,
)
from gnd.synth.oracle.mutations import (
    applies_play_neither as applies_play_neither,
)
from gnd.synth.oracle.mutations import (
    applies_remove_disjunctive as applies_remove_disjunctive,
)
from gnd.synth.oracle.mutations import (
    applies_roster_add as applies_roster_add,
)
from gnd.synth.oracle.mutations import (
    apply_add_missing_subset as apply_add_missing_subset,
)
from gnd.synth.oracle.mutations import (
    apply_add_overlap as apply_add_overlap,
)
from gnd.synth.oracle.mutations import (
    apply_add_past_ceiling as apply_add_past_ceiling,
)
from gnd.synth.oracle.mutations import (
    apply_add_self_loop as apply_add_self_loop,
)
from gnd.synth.oracle.mutations import (
    apply_close_2_cycle as apply_close_2_cycle,
)
from gnd.synth.oracle.mutations import (
    apply_close_3_cycle as apply_close_3_cycle,
)
from gnd.synth.oracle.mutations import (
    apply_drop_covers as apply_drop_covers,
)
from gnd.synth.oracle.mutations import (
    apply_duplicate_covered as apply_duplicate_covered,
)
from gnd.synth.oracle.mutations import (
    apply_duplicate_joined as apply_duplicate_joined,
)
from gnd.synth.oracle.mutations import (
    apply_exact_duplicate as apply_exact_duplicate,
)
from gnd.synth.oracle.mutations import (
    apply_introduce_distinct as apply_introduce_distinct,
)
from gnd.synth.oracle.mutations import (
    apply_new_entity_plays as apply_new_entity_plays,
)
from gnd.synth.oracle.mutations import (
    apply_place_two_subtypes as apply_place_two_subtypes,
)
from gnd.synth.oracle.mutations import (
    apply_play_both as apply_play_both,
)
from gnd.synth.oracle.mutations import (
    apply_play_neither as apply_play_neither,
)
from gnd.synth.oracle.mutations import (
    apply_remove_disjunctive as apply_remove_disjunctive,
)
from gnd.synth.oracle.mutations import (
    apply_roster_add as apply_roster_add,
)
from gnd.synth.oracle.mutations import (
    internal_frequency_groups as internal_frequency_groups,
)
from gnd.synth.oracle.mutations import (
    ring_components_of as ring_components_of,
)
from gnd.synth.oracle.mutations import (
    ring_edges as ring_edges,
)
from gnd.synth.oracle.mutations import (
    ring_gate as ring_gate,
)
from gnd.synth.oracle.mutations import (
    xor_player_sets as xor_player_sets,
)
from gnd.synth.oracle.mutations import (
    xor_single_role as xor_single_role,
)
from gnd.synth.oracle.state import (
    SKIP as SKIP,
)
from gnd.synth.oracle.state import (
    complete_row as complete_row,
)
from gnd.synth.oracle.state import (
    existing_members as existing_members,
)
from gnd.synth.oracle.state import (
    expected_state as expected_state,
)
from gnd.synth.oracle.state import (
    facts_of as facts_of,
)
from gnd.synth.oracle.state import (
    fresh_identifier as fresh_identifier,
)
from gnd.synth.oracle.state import (
    ft_by_id as ft_by_id,
)
from gnd.synth.oracle.state import (
    resolve as resolve,
)

