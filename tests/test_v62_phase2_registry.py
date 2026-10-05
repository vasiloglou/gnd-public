from __future__ import annotations

from gnd.semantic_registry import branch

EXPECTED = {'composition:derivation-view:dynamic:applied': 'gnd.checker.structured_extension_view', 'composition:dynamic-refresh:selected:projected': 'gnd.transition._evaluate_to_state', 'composition:dynamic-refresh:no-touch:refused': 'gnd.transition._evaluate_to_state', 'transition:dynamic-rule:derived-untouched:refused': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-no-delta:refused': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-nonfunctional:unchecked': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-no-old:vacuous': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-no-new:vacuous': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-comparison:clean': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-comparison:violated:alethic': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:dynamic-rule:derived-comparison:violated:deontic': 'gnd.transition._evaluate_derived_dynamic_rules', 'transition:derived-change:added:projected': 'gnd.transition._derived_changes', 'transition:derived-change:removed:projected': 'gnd.transition._derived_changes', 'report:transition-derived-changes:n-a:projected': 'gnd.redaction._project_transition'}

def test_r01_every_dynamic_id_is_registered_with_its_owner() -> None:
    for scope_id, owner in EXPECTED.items():
        row = branch(scope_id)
        assert row.production_owner == owner, scope_id

def test_banded_derived_rule_rows_are_verdict_branches() -> None:
    for scope_id in ('transition:dynamic-rule:derived-nonfunctional:unchecked', 'transition:dynamic-rule:derived-no-old:vacuous', 'transition:dynamic-rule:derived-no-new:vacuous', 'transition:dynamic-rule:derived-comparison:violated:alethic', 'transition:dynamic-rule:derived-comparison:violated:deontic'):
        assert branch(scope_id).obligation_kind == 'verdict'

def test_nonbanded_dynamic_records_are_not_verdicts() -> None:
    for scope_id in ('composition:dynamic-refresh:no-touch:refused', 'transition:dynamic-rule:derived-untouched:refused', 'transition:dynamic-rule:derived-no-delta:refused', 'transition:dynamic-rule:derived-comparison:clean', 'transition:derived-change:added:projected', 'transition:derived-change:removed:projected', 'report:transition-derived-changes:n-a:projected'):
        assert branch(scope_id).obligation_kind != 'verdict'
