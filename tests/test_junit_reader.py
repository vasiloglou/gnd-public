"""Independent unit surface for the bounded tests-mode JUnit reader.

These tests exercise reader mechanisms and pure decision inputs directly.  The
owner-approved CLI corpus remains a separate, read-only approval instrument.
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator, Sequence
from contextlib import contextmanager
from pathlib import Path

import pytest

from gnd.exp import junit
from gnd.exp.junit import (
    MAX_JUNIT_BYTES,
    MAX_JUNIT_DEPTH,
    MAX_JUNIT_ELEMENTS,
    MAX_JUNIT_TEXT_UNITS,
    ChildLifecycle,
    JUnitOutcome,
    JUnitReadResult,
    MappedTest,
    decide_junit_acceptance,
    read_junit,
    render_test_id,
)

_REQUIRED = "pkg/test_sample.py::Example::test_value[left-right]"
_IDENTITY = 'classname="pkg.test_sample.Example" name="test_value[left-right]"'


@contextmanager
def _scratch_descriptor(root: Path) -> Iterator[int]:
    descriptor = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
    try:
        yield descriptor
    finally:
        os.close(descriptor)


def _read_document(
    tmp_path: Path,
    document: bytes,
    required: Sequence[str] = (_REQUIRED,),
) -> JUnitReadResult:
    report = tmp_path / "report.xml"
    report.write_bytes(document)
    with _scratch_descriptor(tmp_path) as descriptor:
        result = read_junit(descriptor, report.name, required)
        os.fstat(descriptor)  # The reader never consumes its caller's root descriptor.
        return result


def _passing_document() -> bytes:
    return f"<testsuite><testcase {_IDENTITY}/></testsuite>".encode()


@pytest.mark.parametrize(
    "results_path",
    ["", "/report.xml", "../report.xml", "a/./report.xml", "a//report.xml", "C:/x.xml"],
)
def test_results_coordinate_shape_is_refused_before_root_io(results_path: str) -> None:
    result = read_junit(-1, results_path, (_REQUIRED,))

    assert (result.exit_code, result.reason) == (3, "tests:results-path-relative")


def test_descriptor_fallback_opens_and_verifies_each_component(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    nested = tmp_path / "one" / "two"
    nested.mkdir(parents=True)
    (nested / "report.xml").write_bytes(_passing_document())
    monkeypatch.setattr(
        junit,
        "_open_with_openat2",
        lambda _root_fd, _path: junit._OPENAT2_UNAVAILABLE,
    )
    real_open = os.open
    real_fstat = os.fstat
    opened_flags: list[int] = []
    fstat_calls = 0

    def recording_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        opened_flags.append(flags)
        return real_open(path, flags, *args, **kwargs)

    def recording_fstat(descriptor: int) -> os.stat_result:
        nonlocal fstat_calls
        fstat_calls += 1
        return real_fstat(descriptor)

    monkeypatch.setattr(junit.os, "open", recording_open)
    monkeypatch.setattr(junit.os, "fstat", recording_fstat)
    with _scratch_descriptor(tmp_path) as descriptor:
        result = read_junit(descriptor, "one/two/report.xml", (_REQUIRED,))

    assert result.ok
    path_flags = opened_flags[1:]  # The first call is the fixture's held root descriptor.
    assert len(path_flags) == 3
    assert all(flags & os.O_NOFOLLOW for flags in path_flags)
    assert all(flags & os.O_DIRECTORY for flags in path_flags[:-1])
    assert path_flags[-1] & os.O_NONBLOCK
    assert fstat_calls >= 4  # Root, two opened parents, and the final descriptor.


@pytest.mark.parametrize("symlink_position", ["parent", "leaf"])
def test_descriptor_fallback_never_follows_a_symlink(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    symlink_position: str,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "report.xml").write_bytes(_passing_document())
    if symlink_position == "parent":
        (tmp_path / "results").symlink_to(outside, target_is_directory=True)
        results_path = "results/report.xml"
    else:
        (tmp_path / "report.xml").symlink_to(outside / "report.xml")
        results_path = "report.xml"
    monkeypatch.setattr(
        junit,
        "_open_with_openat2",
        lambda _root_fd, _path: junit._OPENAT2_UNAVAILABLE,
    )

    with _scratch_descriptor(tmp_path) as descriptor:
        result = read_junit(descriptor, results_path, (_REQUIRED,))

    assert result.reason == "tests:results-path-symlink"


def test_non_directory_parent_and_absent_leaf_have_distinct_registered_reasons(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    (tmp_path / "ordinary-file").write_text("not a directory", encoding="utf-8")
    monkeypatch.setattr(
        junit,
        "_open_with_openat2",
        lambda _root_fd, _path: junit._OPENAT2_UNAVAILABLE,
    )

    with _scratch_descriptor(tmp_path) as descriptor:
        wrong_type = read_junit(descriptor, "ordinary-file/report.xml", (_REQUIRED,))
        missing = read_junit(descriptor, "absent/report.xml", (_REQUIRED,))

    assert wrong_type.reason == "tests:results-path-type"
    assert missing.reason == "tests:results-missing"


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="requires POSIX fifo support")
def test_final_fifo_is_classified_without_a_blocking_read(tmp_path: Path) -> None:
    fifo = tmp_path / "report.xml"
    os.mkfifo(fifo)

    with _scratch_descriptor(tmp_path) as descriptor:
        result = read_junit(descriptor, fifo.name, (_REQUIRED,))

    assert result.reason == "tests:results-path-type"
    assert result.bytes_read == 0


def test_byte_budget_hashes_exactly_the_admitted_bytes_and_reads_only_one_over(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    prefix = f"<testsuite><testcase {_IDENTITY}/></testsuite><!--".encode()
    suffix = b"-->"
    document = prefix + (b"x" * (MAX_JUNIT_BYTES - len(prefix) - len(suffix))) + suffix
    at_limit = _read_document(tmp_path, document)

    assert at_limit.ok
    assert at_limit.bytes_read == MAX_JUNIT_BYTES
    assert at_limit.sha256 == hashlib.sha256(document).hexdigest()

    parser_called = False

    def parser_spy(_text: str, _required: Sequence[str]) -> junit._ParsedJUnit:
        nonlocal parser_called
        parser_called = True
        raise AssertionError("over-limit bytes reached Expat")

    monkeypatch.setattr(junit, "_parse_junit", parser_spy)
    over_limit = _read_document(tmp_path, document + b"x")

    assert over_limit.reason == "tests:results-too-large"
    assert over_limit.bytes_read == MAX_JUNIT_BYTES + 1
    assert over_limit.sha256 is None
    assert not parser_called


@pytest.mark.parametrize(
    ("codec", "bom", "declaration"),
    [
        ("utf-8", b"", "UTF-8"),
        ("utf-8", b"\xef\xbb\xbf", "utf-8"),
        ("utf-16-le", b"\xff\xfe", "UTF-16"),
        ("utf-16-be", b"", "UTF-16BE"),
    ],
)
def test_supported_encoding_signals_and_declarations_agree(
    tmp_path: Path, codec: str, bom: bytes, declaration: str
) -> None:
    text = f'<?xml version="1.0" encoding="{declaration}"?>' + _passing_document().decode()

    result = _read_document(tmp_path, bom + text.encode(codec))

    assert result.ok
    assert result.mapped_tests == (MappedTest(_REQUIRED, JUnitOutcome.passed),)


@pytest.mark.parametrize(
    "document",
    [
        b'<?xml version="1.0" encoding="ISO-8859-1"?><testsuite/>',
        b"\xff\xfe" + '<?xml version="1.0" encoding="UTF-16BE"?><testsuite/>'.encode("utf-16-le"),
        b"\x00\x00\xfe\xff\x00\x00\x00<",
        b"\x80",
    ],
)
def test_unsupported_inconsistent_and_undecodable_encodings_are_total(
    tmp_path: Path, document: bytes
) -> None:
    result = _read_document(tmp_path, document)

    assert result.reason == "tests:results-encoding"


def test_whole_decoded_document_is_scanned_before_parser_creation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = (
        '<?xml version="1.0" encoding="UTF-16BE"?><!--'
        + ("x" * 70_000)
        + "<!DOCTYPE conservative-comment-refusal>-->"
        + _passing_document().decode()
    )
    parser_called = False

    def parser_spy(_text: str, _required: Sequence[str]) -> junit._ParsedJUnit:
        nonlocal parser_called
        parser_called = True
        raise AssertionError("DTD-bearing text reached Expat")

    monkeypatch.setattr(junit, "_parse_junit", parser_spy)
    result = _read_document(tmp_path, text.encode("utf-16-be"))

    assert result.reason == "tests:results-dtd"
    assert not parser_called


def test_expat_handlers_reject_dtds_defensively_when_scan_is_bypassed() -> None:
    parsed = junit._parse_junit("<!DOCTYPE testsuite><testsuite/>", ())

    assert parsed.reason == "tests:results-dtd"


def test_expat_syntax_errors_are_registered(tmp_path: Path) -> None:
    result = _read_document(tmp_path, b"<testsuite><testcase></testsuite>")

    assert result.reason == "tests:results-xml-malformed"


def test_element_budget_reaches_the_real_maximum_and_stops_before_element_one_over(
    tmp_path: Path,
) -> None:
    start = f"<testsuite><testcase {_IDENTITY}/>".encode()
    at_document = start + (b"<x/>" * (MAX_JUNIT_ELEMENTS - 2)) + b"</testsuite>"
    over_document = start + (b"<x/>" * (MAX_JUNIT_ELEMENTS - 1)) + b"</testsuite>"

    at_limit = _read_document(tmp_path, at_document)
    over_limit = _read_document(tmp_path, over_document)

    assert at_limit.ok
    assert at_limit.elements_parsed == MAX_JUNIT_ELEMENTS
    assert over_limit.reason == "tests:results-xml-limit"
    assert over_limit.elements_parsed == MAX_JUNIT_ELEMENTS


def test_depth_budget_reaches_the_real_maximum_and_stops_before_level_one_over(
    tmp_path: Path,
) -> None:
    testcase = f"<testcase {_IDENTITY}/>".encode()

    def document(intermediate_levels: int) -> bytes:
        return (
            b"<testsuite>"
            + (b"<level>" * intermediate_levels)
            + testcase
            + (b"</level>" * intermediate_levels)
            + b"</testsuite>"
        )

    at_limit = _read_document(tmp_path, document(MAX_JUNIT_DEPTH - 2))
    over_limit = _read_document(tmp_path, document(MAX_JUNIT_DEPTH - 1))

    assert at_limit.ok
    assert at_limit.max_depth == MAX_JUNIT_DEPTH
    assert over_limit.reason == "tests:results-xml-limit"
    assert over_limit.max_depth == MAX_JUNIT_DEPTH


def test_text_budget_reaches_the_real_maximum_and_never_retains_a_crossing_chunk(
    tmp_path: Path,
) -> None:
    start = f"<testsuite><testcase {_IDENTITY}>".encode()
    end = b"</testcase></testsuite>"

    at_limit = _read_document(tmp_path, start + (b"x" * MAX_JUNIT_TEXT_UNITS) + end)
    over_limit = _read_document(tmp_path, start + (b"x" * (MAX_JUNIT_TEXT_UNITS + 1)) + end)

    assert at_limit.ok
    assert at_limit.text_units == MAX_JUNIT_TEXT_UNITS
    assert over_limit.reason == "tests:results-xml-limit"
    assert over_limit.text_units <= MAX_JUNIT_TEXT_UNITS


def test_arbitrary_single_byte_documents_never_escape_as_exceptions(tmp_path: Path) -> None:
    for value in range(256):
        result = _read_document(tmp_path, bytes([value]), ())
        assert result.exit_code == 15
        assert result.reason in {
            "tests:results-encoding",
            "tests:results-xml-malformed",
        }


def test_render_is_forward_total_for_modules_classes_and_parametrize_text() -> None:
    assert render_test_id("pkg.with.dots/test_mod.py::Suite::test_x[a/b-c]") == (
        "pkg.with.dots.test_mod.Suite",
        "test_x[a/b-c]",
    )
    assert render_test_id("no-selector.py") is None


def test_one_junit_identity_cannot_select_two_required_ids(tmp_path: Path) -> None:
    required = ("pkg/test_mod.py::test_x", "pkg.test_mod.py::test_x")
    document = b'<testsuite><testcase classname="pkg.test_mod" name="test_x"/></testsuite>'

    result = _read_document(tmp_path, document, required)

    assert result.reason == "tests:junit-collision"


def test_one_required_id_cannot_be_emitted_twice(tmp_path: Path) -> None:
    testcase = f"<testcase {_IDENTITY}/>".encode()
    result = _read_document(tmp_path, b"<testsuite>" + testcase + testcase + b"</testsuite>")

    assert result.reason == "tests:junit-duplicate"


def test_outcome_is_only_one_unqualified_direct_child(tmp_path: Path) -> None:
    contradictory = (
        f"<testsuite><testcase {_IDENTITY}><error/><skipped/></testcase></testsuite>".encode()
    )
    lookalikes = (
        f'<testsuite xmlns:n="urn:not-junit"><testcase {_IDENTITY} status="failure">'
        "<wrapper><failure/></wrapper><n:error/></testcase></testsuite>"
    ).encode()

    refused = _read_document(tmp_path, contradictory)
    ignored = _read_document(tmp_path, lookalikes)

    assert refused.reason == "tests:junit-outcome"
    assert ignored.ok
    assert ignored.mapped_tests[0].outcome == JUnitOutcome.passed


def test_suite_summaries_cover_all_descendant_unqualified_testcases(tmp_path: Path) -> None:
    matching = (
        '<testsuite tests="2" failures="1" errors="0" skipped="0">'
        '<testsuite tests="1" failures="1"><testcase classname="other" name="failed">'
        "<failure/></testcase></testsuite>"
        f"<testcase {_IDENTITY}/></testsuite>"
    ).encode()
    inconsistent = matching.replace(b'tests="2"', b'tests="3"', 1)

    accepted_summary = _read_document(tmp_path, matching)
    refused_summary = _read_document(tmp_path, inconsistent)

    assert accepted_summary.ok
    assert refused_summary.reason == "tests:junit-summary"


def test_an_integer_summary_too_large_for_python_conversion_stays_a_junit_refusal(
    tmp_path: Path,
) -> None:
    document = (f'<testsuite tests="{"9" * 5_000}"><testcase {_IDENTITY}/></testsuite>').encode()

    result = _read_document(tmp_path, document)

    assert result.reason == "tests:junit-summary"


def test_namespaced_testcase_cannot_supply_a_required_id(tmp_path: Path) -> None:
    document = f'<testsuite xmlns:n="urn:not-junit"><n:testcase {_IDENTITY}/></testsuite>'.encode()
    read_result = _read_document(tmp_path, document)

    decision = decide_junit_acceptance(ChildLifecycle(0), read_result, (_REQUIRED,))

    assert read_result.ok
    assert read_result.mapped_tests == ()
    assert decision.reason == "tests:required-absent"


def _successful_read(outcome: JUnitOutcome = JUnitOutcome.passed) -> JUnitReadResult:
    return JUnitReadResult(
        sha256="0" * 64,
        mapped_tests=(MappedTest(_REQUIRED, outcome),),
    )


def test_decision_row_1_outranks_every_candidate_controlled_fact() -> None:
    decision = decide_junit_acceptance(
        ChildLifecycle(9, timed_out=True, signal_number=9, descendant_survived=True),
        JUnitReadResult(reason="tests:verifier-io", exit_code=15),
        (_REQUIRED,),
        snapshot_reason="tests:protected-mutated",
    )

    assert decision == junit.JUnitDecision(15, "tests:verifier-io", "verifier-failure")


def test_simultaneous_lifecycle_faults_follow_the_registrys_written_order() -> None:
    decision = decide_junit_acceptance(
        ChildLifecycle(7, timed_out=True, signal_number=9, descendant_survived=True),
        _successful_read(),
        (_REQUIRED,),
    )

    assert decision.reason == "tests:child-timeout"


@pytest.mark.parametrize(
    ("child", "reason"),
    [
        (ChildLifecycle(9, timed_out=True), "tests:child-timeout"),
        (ChildLifecycle(-9, signal_number=9), "tests:child-signal"),
        (ChildLifecycle(7), "tests:child-nonzero"),
        (ChildLifecycle(0, descendant_survived=True), "tests:descendant-survived"),
    ],
)
def test_decision_row_2_lifecycle_facts_gate_sufficient_results(
    child: ChildLifecycle, reason: str
) -> None:
    decision = decide_junit_acceptance(child, _successful_read(), (_REQUIRED,))

    assert (decision.exit_code, decision.reason, decision.disposition) == (
        15,
        reason,
        "not-accepted",
    )


@pytest.mark.parametrize(
    "read_reason",
    ["tests:results-xml-malformed", "tests:junit-summary"],
)
def test_decision_rows_3_and_4_outrank_mapping_and_snapshot_facts(read_reason: str) -> None:
    decision = decide_junit_acceptance(
        ChildLifecycle(0),
        JUnitReadResult(reason=read_reason, exit_code=15),
        (_REQUIRED,),
        snapshot_reason="tests:protected-mutated",
    )

    assert decision.reason == read_reason
    assert decision.disposition == "not-accepted"


def test_decision_rows_5_through_8_are_total_and_ordered() -> None:
    absent = decide_junit_acceptance(
        ChildLifecycle(0),
        JUnitReadResult(sha256="0" * 64),
        (_REQUIRED,),
        snapshot_reason="tests:protected-mutated",
    )
    not_passing = decide_junit_acceptance(
        ChildLifecycle(0),
        _successful_read(JUnitOutcome.skipped),
        (_REQUIRED,),
        snapshot_reason="tests:protected-mutated",
    )
    snapshot = decide_junit_acceptance(
        ChildLifecycle(0),
        _successful_read(),
        (_REQUIRED,),
        snapshot_reason="tests:protected-mutated",
    )
    accepted = decide_junit_acceptance(ChildLifecycle(0), _successful_read(), (_REQUIRED,))

    assert absent.reason == "tests:required-absent"
    assert not_passing.reason == "tests:required-not-passing"
    assert snapshot == junit.JUnitDecision(
        15,
        "tests:protected-mutated",
        "verifier-failure",
    )
    assert accepted == junit.JUnitDecision(0, None, "accepted")
