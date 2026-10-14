"""Constraint family hooks; branch evidence registration remains separate.

Names resolve only against explicitly supplied defining namespaces. This registry
imports no domain algorithms and adds no hidden dynamic import edges.
"""
from __future__ import annotations

from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Any

Hook = str | Callable[..., Any]


@dataclass(frozen=True)
class Family:
    adapter: Hook
    evaluator: Hook
    witness: Hook
    message: Hook
    scope: Hook
    implemented: bool
    shape: Hook = '_family_shape_true'
    scope_before_refs: bool = False
    production: Hook | None = None


def resolve_hook(hook: Hook, namespace: Mapping[str, Any]) -> Callable[..., Any]:
    selected = namespace.get(hook) if isinstance(hook, str) else hook
    if not callable(selected):
        raise RuntimeError(f'constraint family hook is not callable: {hook!r}')  # noqa: TRY004 -- broken registry is a runtime contract error
    return selected


FAMILIES: dict[str, Family] = {
    'anchored': Family('_family_adapt_identity', '_family_result_unknown', '_row_projected_witness', '_family_message_default', '_family_scope_empty', True, shape='_family_implemented_anchored', scope_before_refs=False),
    'cardinality': Family('_family_adapt_identity', '_family_result_cardinality', '_flat_projected_witness', '_family_message_cardinality', '_family_scope_value', True, shape='_family_implemented_cardinality', scope_before_refs=False),
    'equality': Family('_family_adapt_identity', '_family_result_equality', '_row_projected_witness', '_family_message_subset', '_family_scope_empty', True, shape='_family_implemented_equality', scope_before_refs=False),
    'exclusion': Family('_family_adapt_identity', '_family_result_exclusion', '_row_projected_witness', '_family_message_subset', '_family_scope_empty', True, shape='_family_implemented_equality', scope_before_refs=False),
    'exclusive-or': Family('_family_adapt_identity', '_family_result_exclusive_or', '_row_projected_witness', '_family_message_exclusive_or', '_family_scope_empty', True, shape='_family_implemented_exclusive_or', scope_before_refs=False),
    'frequency': Family('_family_adapt_identity', '_family_result_frequency', '_row_projected_witness', '_family_message_frequency', '_family_scope_empty', True, shape='_family_implemented_frequency', scope_before_refs=False),
    'guarded': Family('_family_adapt_guarded', '_family_result_guarded', '_row_projected_witness', '_family_message_guarded', '_family_scope_guarded', True, shape='_family_implemented_guarded', scope_before_refs=True),
    'mandatory': Family('_family_adapt_identity', '_family_result_mandatory', '_flat_projected_witness', '_family_message_mandatory', '_family_scope_empty', True, shape='_family_implemented_mandatory', scope_before_refs=False),
    'mandatory-disjunctive': Family('_family_adapt_identity', '_family_result_mandatory_disjunctive', '_flat_projected_witness', '_family_message_mandatory_disjunctive', '_family_scope_empty', True, shape='_family_implemented_mandatory_disjunctive', scope_before_refs=False),
    'ring': Family('_family_adapt_identity', '_family_result_ring', '_row_projected_witness', '_family_message_ring', '_family_scope_empty', True, shape='_family_implemented_ring', scope_before_refs=False),
    'subset': Family('_family_adapt_identity', '_family_result_subset', '_row_projected_witness', '_family_message_subset', '_family_scope_empty', True, shape='_family_implemented_subset', scope_before_refs=False, production='indexed_subset_verdict'),
    'subtype-partition': Family('_family_adapt_identity', '_family_result_subtype_partition', '_row_projected_witness', '_family_message_subtype_partition', '_family_scope_subtype_partition', True, shape='_family_implemented_subtype_partition', scope_before_refs=False),
    'textual': Family('_family_adapt_textual', '_family_result_unknown', '_row_projected_witness', '_family_message_default', '_family_scope_empty', False, shape='_family_shape_false', scope_before_refs=False),
    'uniqueness': Family('_family_adapt_identity', '_family_result_uniqueness', '_row_projected_witness', '_family_message_uniqueness', '_family_scope_empty', True, shape='_family_implemented_uniqueness', scope_before_refs=False),
    'value': Family('_family_adapt_identity', '_family_result_value', '_flat_projected_witness', '_family_message_value', '_family_scope_value', True, shape='_family_implemented_value', scope_before_refs=False),
    'value-comparison': Family('_family_adapt_value_comparison', '_family_result_value_comparison', '_row_projected_witness', '_family_message_value_comparison', '_family_scope_empty', True, shape='_family_implemented_value_comparison', scope_before_refs=False),
}
