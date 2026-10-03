"""Untrusted evidence never reaches the release-backed capability."""

import pytest

from gnd.assurance_evidence import (
    AuthenticatedAssuranceEvidence,
    _json,
    _relative,
    load_assurance_evidence,
)


@pytest.mark.parametrize(
    "raw",
    [
        b'{"x":1,"x":2}',
        b'{"x":NaN}',
        b'{"x":1e9999}',
        b"\xff",
        b"[" * 65 + b"]" * 65,
        b'{"x":' + b"9" * 5000 + b"}",
        b"[] trailing",
    ],
)
def test_malformed_or_unbounded_evidence_is_refused(raw):
    with pytest.raises((ValueError, UnicodeError)):
        _json(raw)


@pytest.mark.parametrize(
    "path", ["/etc/passwd", "../source.py", "a/../b", "a//b", "a/./b", "a\\b", ""]
)
def test_evidence_addresses_cannot_escape_or_alias(path):
    with pytest.raises(ValueError):
        _relative(path)


def test_json_depth_ignores_brackets_inside_strings():
    assert _json(b'{"x":"[[[[\\"[[["}') == {"x": '[[[["[[['}


def test_no_bundle_is_an_explicit_unavailable_capability(tmp_path, monkeypatch):
    package = tmp_path / "gnd"
    package.mkdir()
    monkeypatch.setattr("gnd.assurance_evidence.resources.files", lambda _name: package)
    evidence = load_assurance_evidence()
    assert isinstance(evidence, AuthenticatedAssuranceEvidence)
    assert not evidence.available and evidence.digests is None
    assert evidence.covered_scope_ids == frozenset()


def test_caller_cannot_supply_evidence_or_expected_identities():
    with pytest.raises(TypeError):
        load_assurance_evidence("caller.json")
    with pytest.raises(TypeError):
        AuthenticatedAssuranceEvidence(available=True)


def test_digit_bound_does_not_depend_on_the_interpreter_global_setting():
    import sys

    previous = sys.get_int_max_str_digits()
    try:
        sys.set_int_max_str_digits(0)
        with pytest.raises(ValueError, match="integer digit limit"):
            _json(b'{"x":' + b"9" * 5000 + b"}")
    finally:
        sys.set_int_max_str_digits(previous)
