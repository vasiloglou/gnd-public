"""Review round pr-207-r1, findings F1 and F2: rule ids are read with the parser.

The first half holds the reader itself. The second half replays the reviewer's
two inputs against the guards that use it: a rule id spelled with single
quotes, and a third id emitted from a loop. Each guard passed on that input
while it read rule ids out of the source text with a pattern.
"""
from __future__ import annotations

import pytest
from support.rule_source import (
    computed_keyword,
    keyword_literals,
    rule_id_arguments,
    semantic_literals,
)

from gnd import model as model_module


def _issue(**fields):
    return fields


def _single_quoted(doc):
    issues = [_issue(rule_id="semantic:op-param-ref")]
    issues.append(_issue(rule_id='semantic:op-extra'))
    return issues


def _double_quoted(doc):
    issues = [_issue(rule_id="semantic:op-param-ref")]
    issues.append(_issue(rule_id="semantic:op-extra"))
    return issues


def _looped(doc):
    issues = []
    for name in ("semantic:membership-list",
                 "semantic:membership-duplicate",
                 "semantic:membership-extra"):
        issues.append(_issue(rule_id=name))
    return issues


def _guarded_single_quoted(doc):
    return [_issue(rule_id='semantic:guarded-extra')]


def _mentions_only(doc):
    """Reports "semantic:in-a-docstring" in prose only."""
    # A comment may name "semantic:in-a-comment" without the rule reporting it.
    number = 3
    return [_issue(rule_id=f"semantic:unattended-u{number}", severity='warning')]


def test_a_rule_id_is_read_whichever_quotes_spell_it():
    assert rule_id_arguments(_single_quoted) == ["semantic:op-param-ref", "semantic:op-extra"]
    assert rule_id_arguments(_single_quoted) == rule_id_arguments(_double_quoted)
    assert semantic_literals(_single_quoted) == ["semantic:op-param-ref", "semantic:op-extra"]


def test_ids_a_rule_loops_over_are_all_read():
    assert rule_id_arguments(_looped) == []
    assert computed_keyword(_looped, "rule_id")
    assert semantic_literals(_looped) == [
        "semantic:membership-list", "semantic:membership-duplicate", "semantic:membership-extra"]


def test_prose_and_the_fixed_part_of_an_f_string_are_not_ids():
    assert semantic_literals(_mentions_only) == []
    assert rule_id_arguments(_mentions_only) == []
    assert computed_keyword(_mentions_only, "rule_id")
    assert keyword_literals(_mentions_only, "severity") == ["warning"]


def _standing_in(monkeypatch, name, stand_in):
    """Register ``stand_in`` in place of the rule called ``name``."""
    monkeypatch.setattr(stand_in, "__name__", name)
    rules = type(model_module._SEMANTIC_RULES)(
        stand_in if rule.__name__ == name else rule for rule in model_module._SEMANTIC_RULES)
    assert any(rule is stand_in for rule in rules), name
    monkeypatch.setattr(model_module, "_SEMANTIC_RULES", rules)


def test_the_v2_coverage_guard_sees_a_single_quoted_error_rule(monkeypatch):
    import test_model_v2

    guard = test_model_v2.test_every_error_rule_added_by_this_phase_has_a_rejecting_case
    guard()
    _standing_in(monkeypatch, "_rule_op_param_ref", _single_quoted)
    with pytest.raises(AssertionError, match="semantic:op-extra"):
        guard()


def test_the_inventory_guard_sees_a_single_quoted_rule_id(monkeypatch):
    import test_model_validation

    guard = test_model_validation.test_normative_semantic_rule_inventory_matches_registration_order
    guard()
    _standing_in(monkeypatch, "_rule_op_param_ref", _single_quoted)
    with pytest.raises(AssertionError):
        guard()


def test_the_inventory_guard_sees_a_third_id_in_a_loop(monkeypatch):
    import test_model_validation

    guard = test_model_validation.test_normative_semantic_rule_inventory_matches_registration_order
    _standing_in(monkeypatch, "_rule_derivation_membership", _looped)
    with pytest.raises(AssertionError):
        guard()


def test_the_guarded_coverage_guard_sees_a_single_quoted_error_rule(monkeypatch):
    import test_model_guarded

    guard = test_model_guarded.test_every_registered_guarded_error_rule_has_a_rejecting_case
    guard()
    _standing_in(monkeypatch, "_rule_guarded_comparison_type", _guarded_single_quoted)
    with pytest.raises(AssertionError):
        guard()
