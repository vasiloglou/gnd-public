"""Failure controls for the successor audit, independent of historical table totals."""

import ast

import audit
import pytest

from gnd.exp import spec


def test_wrong_wrapper_rule_fails(monkeypatch):
    monkeypatch.setattr(
        spec, "_validation_issues", lambda error: spec.issues_from_validation_error(error, "wrong")
    )
    with pytest.raises(AssertionError):
        audit.bound_rule(
            "gnd.exp.spec._validation_issues",
            "gnd.errors.issues_from_validation_error",
            "(bound SPEC_RULE_ID)",
        )


@pytest.mark.parametrize(
    "expr",
    [
        'mock.patch.object(v, attribute="_HIDDEN", new=1)',
        'monkeypatch.setattr(target="gnd.exp.session_v7._HIDDEN", value=1)',
        'mock.patch.multiple("gnd.exp.session_v7", _HIDDEN=1)',
    ],
)
def test_patch_keywords(expr):
    node = ast.parse(expr, mode="eval").body
    assert "gnd.exp.session_v7._HIDDEN" in audit.patch_targets(node, {"v": "gnd.exp.session_v7"})
