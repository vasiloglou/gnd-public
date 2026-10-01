"""Bounded, descriptor-relative JUnit reading for tests-mode experiments.

The report is candidate output.  This module therefore treats both its path and
its bytes as hostile: path traversal never leaves a held scratch descriptor,
the byte cap is enforced while reading, and Expat only receives text after a
whole-document DTD/entity scan.
"""

from __future__ import annotations

import ctypes
import errno
import hashlib
import os
import re
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import PurePosixPath, PureWindowsPath
from typing import Literal
from xml.parsers import expat

__all__ = [
    "MAX_JUNIT_BYTES",
    "MAX_JUNIT_DEPTH",
    "MAX_JUNIT_ELEMENTS",
    "MAX_JUNIT_TEXT_UNITS",
    "ChildLifecycle",
    "JUnitDecision",
    "JUnitOutcome",
    "JUnitReadResult",
    "MappedTest",
    "decide_junit_acceptance",
    "read_junit",
    "render_test_id",
]

MAX_JUNIT_BYTES = 8 * 1024 * 1024
MAX_JUNIT_ELEMENTS = 100_000
MAX_JUNIT_DEPTH = 128
MAX_JUNIT_TEXT_UNITS = 4 * 1024 * 1024

_READ_CHUNK_BYTES = 64 * 1024
_PARSE_CHUNK_UNITS = 64 * 1024

RESULTS_PATH_REASON = "tests:results-path-relative"
RESULTS_MISSING_REASON = "tests:results-missing"
RESULTS_SYMLINK_REASON = "tests:results-path-symlink"
RESULTS_TYPE_REASON = "tests:results-path-type"
RESULTS_TOO_LARGE_REASON = "tests:results-too-large"
RESULTS_ENCODING_REASON = "tests:results-encoding"
RESULTS_DTD_REASON = "tests:results-dtd"
RESULTS_XML_LIMIT_REASON = "tests:results-xml-limit"
RESULTS_XML_MALFORMED_REASON = "tests:results-xml-malformed"
JUNIT_COLLISION_REASON = "tests:junit-collision"
JUNIT_DUPLICATE_REASON = "tests:junit-duplicate"
JUNIT_OUTCOME_REASON = "tests:junit-outcome"
JUNIT_SUMMARY_REASON = "tests:junit-summary"
REQUIRED_ABSENT_REASON = "tests:required-absent"
REQUIRED_NOT_PASSING_REASON = "tests:required-not-passing"
VERIFIER_IO_REASON = "tests:verifier-io"

_READ_REASONS = frozenset(
    {
        RESULTS_MISSING_REASON,
        RESULTS_SYMLINK_REASON,
        RESULTS_TYPE_REASON,
        RESULTS_TOO_LARGE_REASON,
        RESULTS_ENCODING_REASON,
        RESULTS_DTD_REASON,
        RESULTS_XML_LIMIT_REASON,
        RESULTS_XML_MALFORMED_REASON,
        JUNIT_COLLISION_REASON,
        JUNIT_DUPLICATE_REASON,
        JUNIT_OUTCOME_REASON,
        JUNIT_SUMMARY_REASON,
        VERIFIER_IO_REASON,
    }
)
_SNAPSHOT_REASONS = frozenset(
    {
        "tests:protected-mutated",
        "tests:directory-snapshot-moved",
        "tests:experiment-dir-moved",
    }
)

_XML_DECLARATION = re.compile(r"\A<\?xml[\t\r\n ]+(?P<body>.*?)\?>", re.DOTALL)
_XML_ENCODING = re.compile(
    r"(?:\A|[\t\r\n ])encoding[\t\r\n ]*=[\t\r\n ]*(['\"])(?P<name>[^'\"]+)\1"
)
_SUMMARY_INTEGER = re.compile(r"[0-9]+\Z")


class JUnitOutcome(StrEnum):
    """The child-element-derived outcome of one unqualified testcase."""

    passed = "pass"
    failure = "failure"
    error = "error"
    skipped = "skipped"


@dataclass(frozen=True, slots=True)
class MappedTest:
    """One required id mapped uniquely from one JUnit testcase."""

    identifier: str
    outcome: JUnitOutcome


@dataclass(frozen=True, slots=True)
class JUnitReadResult:
    """A total read/parse outcome plus bounded-work counters."""

    sha256: str | None = None
    mapped_tests: tuple[MappedTest, ...] = ()
    reason: str | None = None
    exit_code: int = 0
    bytes_read: int = 0
    elements_parsed: int = 0
    max_depth: int = 0
    text_units: int = 0

    @property
    def ok(self) -> bool:
        """Whether one bounded descriptor parsed consistently."""

        return self.reason is None and self.exit_code == 0 and self.sha256 is not None


@dataclass(frozen=True, slots=True)
class ChildLifecycle:
    """The child facts used by precedence row 2."""

    exit_code: int | None
    timed_out: bool = False
    signal_number: int | None = None
    descendant_survived: bool = False


@dataclass(frozen=True, slots=True)
class JUnitDecision:
    """The pure tests-mode acceptance decision."""

    exit_code: int
    reason: str | None
    disposition: Literal["accepted", "not-accepted", "verifier-failure"] | None


@dataclass(slots=True)
class _SuiteFrame:
    declared: dict[str, int]
    computed: dict[str, int]


@dataclass(slots=True)
class _TestcaseFrame:
    mapped_identifier: str | None
    outcomes: list[JUnitOutcome]


@dataclass(frozen=True, slots=True)
class _ParsedJUnit:
    mapped_tests: tuple[MappedTest, ...]
    reason: str | None
    elements: int
    max_depth: int
    text_units: int


class _JUnitRefusal(Exception):
    """A registered refusal deliberately raised from an Expat callback."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class _OpenHow(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_uint64),
        ("mode", ctypes.c_uint64),
        ("resolve", ctypes.c_uint64),
    ]


_OPENAT2_UNAVAILABLE = object()
_RESOLVE_NO_SYMLINKS = 0x04
_RESOLVE_BENEATH = 0x08


def render_test_id(identifier: str) -> tuple[str, str] | None:
    """Render one declared pytest node id as its JUnit identity.

    Invalid declarations return ``None`` rather than guessing a reverse parse.
    Lane A rejects them before a child can be spawned.
    """

    if not isinstance(identifier, str):
        return None
    path, separator, selectors = identifier.partition("::")
    if not separator or not path.endswith(".py") or not selectors:
        return None
    selector_parts = selectors.split("::")
    if any(not selector for selector in selector_parts):
        return None
    module = path[:-3].replace("/", ".")
    if len(selector_parts) > 1:
        module = f"{module}.{'.'.join(selector_parts[:-1])}"
    return module, selector_parts[-1]


def _results_path_is_safe(results_path: object) -> bool:
    if not isinstance(results_path, str) or not results_path:
        return False
    if "\\" in results_path or "\x00" in results_path:
        return False
    windows_path = PureWindowsPath(results_path)
    if (
        PurePosixPath(results_path).is_absolute()
        or windows_path.is_absolute()
        or bool(windows_path.drive)
    ):
        return False
    if any(component in {"", ".", ".."} for component in results_path.split("/")):
        return False
    try:
        os.fsencode(results_path)
    except (TypeError, UnicodeError):
        return False
    return True


def _refusal(
    reason: str,
    *,
    exit_code: int = 15,
    digest: str | None = None,
    bytes_read: int = 0,
    parsed: _ParsedJUnit | None = None,
) -> JUnitReadResult:
    return JUnitReadResult(
        sha256=digest,
        mapped_tests=parsed.mapped_tests if parsed is not None else (),
        reason=reason,
        exit_code=exit_code,
        bytes_read=bytes_read,
        elements_parsed=parsed.elements if parsed is not None else 0,
        max_depth=parsed.max_depth if parsed is not None else 0,
        text_units=parsed.text_units if parsed is not None else 0,
    )


def _openat2_number() -> int | None:
    if sys.platform != "linux" or not hasattr(os, "uname"):
        return None
    machine = os.uname().machine.lower()
    if machine in {
        "aarch64",
        "arm64",
        "armv7l",
        "i386",
        "i486",
        "i586",
        "i686",
        "ppc64",
        "ppc64le",
        "riscv64",
        "s390x",
        "x86_64",
    }:
        return 437
    return None


def _open_with_openat2(root_fd: int, results_path: str) -> int | object:
    """Use Linux's atomic beneath/no-symlink resolver when it is callable."""

    syscall_number = _openat2_number()
    if syscall_number is None:
        return _OPENAT2_UNAVAILABLE
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    how = _OpenHow(
        flags=flags,
        mode=0,
        resolve=_RESOLVE_BENEATH | _RESOLVE_NO_SYMLINKS,
    )
    try:
        libc = ctypes.CDLL(None, use_errno=True)
        syscall = libc.syscall
    except (AttributeError, OSError):
        return _OPENAT2_UNAVAILABLE
    syscall.restype = ctypes.c_long
    descriptor = syscall(
        ctypes.c_long(syscall_number),
        ctypes.c_int(root_fd),
        ctypes.c_char_p(os.fsencode(results_path)),
        ctypes.byref(how),
        ctypes.c_size_t(ctypes.sizeof(how)),
    )
    if descriptor >= 0:
        return int(descriptor)
    error_number = ctypes.get_errno()
    if error_number in {errno.ENOSYS, errno.EINVAL, errno.EPERM}:
        return _OPENAT2_UNAVAILABLE
    raise OSError(error_number, os.strerror(error_number), results_path)


def _open_error_reason(error: OSError, *, known_type: bool = False) -> str:
    if error.errno == errno.ENOENT:
        return RESULTS_MISSING_REASON
    if error.errno in {errno.ELOOP, getattr(errno, "EMLINK", errno.ELOOP), errno.EXDEV}:
        return RESULTS_SYMLINK_REASON
    type_errors = {
        errno.ENOTDIR,
        errno.ENXIO,
        getattr(errno, "ENODEV", errno.ENXIO),
        getattr(errno, "EOPNOTSUPP", errno.ENXIO),
    }
    if known_type or error.errno in type_errors:
        return RESULTS_TYPE_REASON
    return VERIFIER_IO_REASON


def _same_inode(left: os.stat_result, right: os.stat_result) -> bool:
    return left.st_dev == right.st_dev and left.st_ino == right.st_ino


def _open_with_descriptor_chain(root_fd: int, results_path: str) -> tuple[int | None, str | None]:
    """Portable no-follow fallback retaining every traversed directory fd."""

    no_follow = getattr(os, "O_NOFOLLOW", None)
    directory = getattr(os, "O_DIRECTORY", None)
    if no_follow is None or directory is None:
        return None, VERIFIER_IO_REASON

    directory_flags = os.O_RDONLY | directory | no_follow | getattr(os, "O_CLOEXEC", 0)
    final_flags = os.O_RDONLY | os.O_NONBLOCK | no_follow | getattr(os, "O_CLOEXEC", 0)
    components = results_path.split("/")
    current_fd = root_fd
    owned_directories: list[int] = []
    try:
        for component in components[:-1]:
            try:
                before = os.stat(component, dir_fd=current_fd, follow_symlinks=False)
            except OSError as error:
                return None, _open_error_reason(error)
            if stat.S_ISLNK(before.st_mode):
                return None, RESULTS_SYMLINK_REASON
            if not stat.S_ISDIR(before.st_mode):
                return None, RESULTS_TYPE_REASON
            try:
                next_fd = os.open(component, directory_flags, dir_fd=current_fd)
            except OSError as error:
                return None, _open_error_reason(error)
            try:
                after = os.fstat(next_fd)
            except OSError:
                os.close(next_fd)
                return None, VERIFIER_IO_REASON
            if not stat.S_ISDIR(after.st_mode):
                os.close(next_fd)
                return None, RESULTS_TYPE_REASON
            if not _same_inode(before, after):
                os.close(next_fd)
                return None, VERIFIER_IO_REASON
            owned_directories.append(next_fd)
            current_fd = next_fd

        final_component = components[-1]
        try:
            before = os.stat(final_component, dir_fd=current_fd, follow_symlinks=False)
        except OSError as error:
            return None, _open_error_reason(error)
        if stat.S_ISLNK(before.st_mode):
            return None, RESULTS_SYMLINK_REASON
        try:
            result_fd = os.open(final_component, final_flags, dir_fd=current_fd)
        except OSError as error:
            return None, _open_error_reason(
                error,
                known_type=not stat.S_ISREG(before.st_mode),
            )
        try:
            after = os.fstat(result_fd)
        except OSError:
            os.close(result_fd)
            return None, VERIFIER_IO_REASON
        if not _same_inode(before, after):
            os.close(result_fd)
            return None, VERIFIER_IO_REASON
        if not stat.S_ISREG(after.st_mode):
            os.close(result_fd)
            return None, RESULTS_TYPE_REASON
        return result_fd, None
    finally:
        for descriptor in reversed(owned_directories):
            os.close(descriptor)


def _open_result(root_fd: int, results_path: str) -> tuple[int | None, str | None]:
    try:
        opened = _open_with_openat2(root_fd, results_path)
    except OSError as error:
        return None, _open_error_reason(error)
    if opened is _OPENAT2_UNAVAILABLE:
        return _open_with_descriptor_chain(root_fd, results_path)

    result_fd = int(opened)
    try:
        result_stat = os.fstat(result_fd)
    except OSError:
        os.close(result_fd)
        return None, VERIFIER_IO_REASON
    if not stat.S_ISREG(result_stat.st_mode):
        os.close(result_fd)
        return None, RESULTS_TYPE_REASON
    return result_fd, None


def _read_bounded(result_fd: int) -> tuple[bytes | None, str | None, str | None, int]:
    document = bytearray()
    digest = hashlib.sha256()
    bytes_read = 0
    while True:
        request_size = min(_READ_CHUNK_BYTES, MAX_JUNIT_BYTES - bytes_read + 1)
        try:
            chunk = os.read(result_fd, request_size)
        except InterruptedError:
            continue
        except OSError:
            return None, None, VERIFIER_IO_REASON, bytes_read
        if not chunk:
            return bytes(document), digest.hexdigest(), None, bytes_read
        bytes_read += len(chunk)
        digest.update(chunk)
        if bytes_read > MAX_JUNIT_BYTES:
            return None, None, RESULTS_TOO_LARGE_REASON, bytes_read
        document.extend(chunk)


def _decode_document(document: bytes) -> tuple[str | None, str | None]:
    if document.startswith(
        (b"\x00\x00\xfe\xff", b"\xff\xfe\x00\x00", b"\x00\x00\x00<", b"<\x00\x00\x00")
    ):
        return None, RESULTS_ENCODING_REASON

    if document.startswith(b"\xef\xbb\xbf"):
        codec = "utf-8"
        encoding = "utf-8"
        payload = document[3:]
    elif document.startswith(b"\xff\xfe"):
        codec = "utf-16-le"
        encoding = "utf-16-le"
        payload = document[2:]
    elif document.startswith(b"\xfe\xff"):
        codec = "utf-16-be"
        encoding = "utf-16-be"
        payload = document[2:]
    elif document.startswith(b"\x00<\x00?"):
        codec = "utf-16-be"
        encoding = "utf-16-be"
        payload = document
    elif document.startswith(b"<\x00?\x00"):
        codec = "utf-16-le"
        encoding = "utf-16-le"
        payload = document
    else:
        codec = "utf-8"
        encoding = "utf-8"
        payload = document

    try:
        text = payload.decode(codec, errors="strict")
    except (LookupError, UnicodeDecodeError):
        return None, RESULTS_ENCODING_REASON

    declaration = _XML_DECLARATION.match(text)
    if declaration is not None:
        declared_match = _XML_ENCODING.search(declaration.group("body"))
        if declared_match is not None:
            declared = declared_match.group("name").upper()
            agreements = {
                "utf-8": {"UTF-8"},
                "utf-16-le": {"UTF-16", "UTF-16LE"},
                "utf-16-be": {"UTF-16", "UTF-16BE"},
            }
            if declared not in agreements[encoding]:
                return None, RESULTS_ENCODING_REASON
    return text, None


class _JUnitEventState:
    """Mutable bounded state retained by Expat callbacks."""

    def __init__(self, required_tests: Sequence[str]):
        rendered: dict[tuple[str, str], list[str]] = {}
        for identifier in required_tests:
            identity = render_test_id(identifier)
            if identity is not None:
                rendered.setdefault(identity, []).append(identifier)
        self.rendered = rendered
        self.seen_required: set[str] = set()
        self.mapped_tests: list[MappedTest] = []
        self.names: list[str] = []
        self.suites: list[_SuiteFrame] = []
        self.testcases: list[_TestcaseFrame] = []
        self.elements = 0
        self.depth = 0
        self.max_depth = 0
        self.text_units = 0

    def _refuse(self, reason: str) -> None:
        raise _JUnitRefusal(reason)

    def _candidates_for(self, identity: tuple[str | None, str | None]) -> list[str]:
        """Required identifiers this testcase satisfies, exact match or suffix.

        JUnit's ``classname`` is the module path relative to the rootdir PYTEST
        chose, and a contract cannot know that: with a config file above the
        project root the same module reports ``project.suite.test_row`` where it
        otherwise reports ``suite.test_row`` (measured across §6.4's five
        arrangements). Exact matching therefore silently failed to map a
        required test whenever the rootdir sat above the project, and the
        acceptance saw it as ABSENT -- a non-acceptance owed entirely to the
        reader's directory layout (`OQ-P4-NODEID-1`, v5.1 §6.4).

        A rootdir can only PREPEND components, so a declared module matches when
        it is the whole classname or a dot-bounded suffix of it. The boundary is
        what keeps ``suite.test_row`` from matching ``other_suite.test_row``.
        Ambiguity is still a refusal, not a guess: when two declared ids both
        match one testcase, the caller sees the same collision it saw before.
        """
        classname, case_name = identity
        exact = self.rendered.get(identity, [])
        if exact or classname is None or case_name is None:
            return list(exact)
        matched: list[str] = []
        for (module, name), identifiers in self.rendered.items():
            if name != case_name or module is None:
                continue
            if classname.endswith(f".{module}"):
                matched.extend(identifiers)
        return matched

    def start(self, name: str, attributes: dict[str, str]) -> None:
        next_elements = self.elements + 1
        next_depth = self.depth + 1
        if next_elements > MAX_JUNIT_ELEMENTS or next_depth > MAX_JUNIT_DEPTH:
            self._refuse(RESULTS_XML_LIMIT_REASON)
        self.elements = next_elements
        self.depth = next_depth
        self.max_depth = max(self.max_depth, next_depth)

        parent = self.names[-1] if self.names else None
        self.names.append(name)

        if name == "testsuite":
            declared: dict[str, int] = {}
            for field in ("tests", "failures", "errors", "skipped"):
                if field not in attributes:
                    continue
                value = attributes[field]
                if _SUMMARY_INTEGER.fullmatch(value) is None:
                    self._refuse(JUNIT_SUMMARY_REASON)
                try:
                    declared[field] = int(value)
                except (ValueError, OverflowError):
                    self._refuse(JUNIT_SUMMARY_REASON)
            self.suites.append(
                _SuiteFrame(
                    declared=declared,
                    computed={"tests": 0, "failures": 0, "errors": 0, "skipped": 0},
                )
            )
            return

        if name == "testcase":
            identity = (attributes.get("classname"), attributes.get("name"))
            candidates = self._candidates_for(identity)
            if len(candidates) > 1:
                self._refuse(JUNIT_COLLISION_REASON)
            mapped_identifier = candidates[0] if candidates else None
            if mapped_identifier is not None:
                if mapped_identifier in self.seen_required:
                    self._refuse(JUNIT_DUPLICATE_REASON)
                self.seen_required.add(mapped_identifier)
            self.testcases.append(_TestcaseFrame(mapped_identifier=mapped_identifier, outcomes=[]))
            return

        outcomes = {
            "failure": JUnitOutcome.failure,
            "error": JUnitOutcome.error,
            "skipped": JUnitOutcome.skipped,
        }
        if name in outcomes and parent == "testcase":
            testcase = self.testcases[-1]
            if testcase.outcomes:
                self._refuse(JUNIT_OUTCOME_REASON)
            testcase.outcomes.append(outcomes[name])

    def text(self, data: str) -> None:
        next_text_units = self.text_units + len(data)
        if next_text_units > MAX_JUNIT_TEXT_UNITS:
            self._refuse(RESULTS_XML_LIMIT_REASON)
        self.text_units = next_text_units

    def end(self, name: str) -> None:
        if name == "testcase":
            testcase = self.testcases.pop()
            outcome = testcase.outcomes[0] if testcase.outcomes else JUnitOutcome.passed
            for suite in self.suites:
                suite.computed["tests"] += 1
                outcome_fields = {
                    JUnitOutcome.failure: "failures",
                    JUnitOutcome.error: "errors",
                    JUnitOutcome.skipped: "skipped",
                }
                if outcome in outcome_fields:
                    suite.computed[outcome_fields[outcome]] += 1
            if testcase.mapped_identifier is not None:
                self.mapped_tests.append(
                    MappedTest(identifier=testcase.mapped_identifier, outcome=outcome)
                )
        elif name == "testsuite":
            suite = self.suites.pop()
            for field, declared in suite.declared.items():
                if declared != suite.computed[field]:
                    self._refuse(JUNIT_SUMMARY_REASON)
        self.names.pop()
        self.depth -= 1

    def reject_dtd(self, *_args: object) -> None:
        self._refuse(RESULTS_DTD_REASON)

    def reject_external_entity(self, *_args: object) -> int:
        self._refuse(RESULTS_DTD_REASON)
        return 0

    def parsed(self, reason: str | None = None) -> _ParsedJUnit:
        return _ParsedJUnit(
            mapped_tests=tuple(self.mapped_tests),
            reason=reason,
            elements=self.elements,
            max_depth=self.max_depth,
            text_units=self.text_units,
        )


def _parse_junit(text: str, required_tests: Sequence[str]) -> _ParsedJUnit:
    state = _JUnitEventState(required_tests)
    parser = expat.ParserCreate(namespace_separator="}")
    parser.StartElementHandler = state.start
    parser.EndElementHandler = state.end
    parser.CharacterDataHandler = state.text
    parser.StartDoctypeDeclHandler = state.reject_dtd
    parser.EntityDeclHandler = state.reject_dtd
    parser.ExternalEntityRefHandler = state.reject_external_entity
    try:
        for offset in range(0, len(text), _PARSE_CHUNK_UNITS):
            parser.Parse(text[offset : offset + _PARSE_CHUNK_UNITS], False)
        parser.Parse("", True)
    except _JUnitRefusal as refusal:
        return state.parsed(refusal.reason)
    except (expat.ExpatError, ValueError):
        return state.parsed(RESULTS_XML_MALFORMED_REASON)
    return state.parsed()


def read_junit(
    scratch_root_fd: int,
    results_path: str,
    required_tests: Sequence[str],
    *,
    result_fd: int | None = None,
) -> JUnitReadResult:
    """Safely read and interpret one candidate-owned JUnit report.

    ``scratch_root_fd`` remains owned by the caller.  Every ordinary exception
    arising from candidate bytes or path state becomes a registered refusal.
    """

    if not _results_path_is_safe(results_path):
        return _refusal(RESULTS_PATH_REASON, exit_code=3)
    try:
        root_stat = os.fstat(scratch_root_fd)
        if not stat.S_ISDIR(root_stat.st_mode):
            return _refusal(VERIFIER_IO_REASON)
        opened_here = result_fd is None
        if opened_here:
            result_fd, open_reason = _open_result(scratch_root_fd, results_path)
        else:
            open_reason = None
            supplied_info = os.fstat(result_fd)
            if not stat.S_ISREG(supplied_info.st_mode):
                return _refusal(RESULTS_TYPE_REASON)
        if open_reason is not None or result_fd is None:
            return _refusal(open_reason or VERIFIER_IO_REASON)
        try:
            document, digest, read_reason, bytes_read = _read_bounded(result_fd)
        finally:
            if opened_here:
                os.close(result_fd)
        if read_reason is not None or document is None or digest is None:
            return _refusal(read_reason or VERIFIER_IO_REASON, bytes_read=bytes_read)

        text, encoding_reason = _decode_document(document)
        if encoding_reason is not None or text is None:
            return _refusal(
                encoding_reason or RESULTS_ENCODING_REASON,
                digest=digest,
                bytes_read=bytes_read,
            )
        if "<!DOCTYPE" in text or "<!ENTITY" in text:
            return _refusal(RESULTS_DTD_REASON, digest=digest, bytes_read=bytes_read)

        parsed = _parse_junit(text, required_tests)
        if parsed.reason is not None:
            return _refusal(
                parsed.reason,
                digest=digest,
                bytes_read=bytes_read,
                parsed=parsed,
            )
        return JUnitReadResult(
            sha256=digest,
            mapped_tests=parsed.mapped_tests,
            bytes_read=bytes_read,
            elements_parsed=parsed.elements,
            max_depth=parsed.max_depth,
            text_units=parsed.text_units,
        )
    except (OSError, OverflowError, TypeError, ValueError):
        return _refusal(VERIFIER_IO_REASON)


def _not_accepted(reason: str) -> JUnitDecision:
    return JUnitDecision(exit_code=15, reason=reason, disposition="not-accepted")


def decide_junit_acceptance(
    child: ChildLifecycle,
    read_result: JUnitReadResult,
    required_tests: Sequence[str],
    *,
    verifier_failure: bool = False,
    snapshot_reason: str | None = None,
) -> JUnitDecision:
    """Apply section 6.3.2's eight precedence rows without side effects."""

    invalid_read_reason = (
        read_result.reason is not None
        and read_result.reason not in _READ_REASONS
        and read_result.reason != RESULTS_PATH_REASON
    )
    invalid_snapshot_reason = (
        snapshot_reason is not None and snapshot_reason not in _SNAPSHOT_REASONS
    )
    invalid_success = read_result.reason is None and not read_result.ok
    if (
        verifier_failure
        or read_result.reason == VERIFIER_IO_REASON
        or invalid_read_reason
        or invalid_snapshot_reason
        or invalid_success
    ):
        return JUnitDecision(15, VERIFIER_IO_REASON, "verifier-failure")

    if child.timed_out:
        return _not_accepted("tests:child-timeout")
    if child.signal_number is not None or (child.exit_code is not None and child.exit_code < 0):
        return _not_accepted("tests:child-signal")
    if child.exit_code is not None and child.exit_code != 0:
        return _not_accepted("tests:child-nonzero")
    if child.descendant_survived:
        return _not_accepted("tests:descendant-survived")
    if child.exit_code is None:
        return JUnitDecision(15, VERIFIER_IO_REASON, "verifier-failure")

    if read_result.reason is not None:
        if read_result.reason == RESULTS_PATH_REASON and read_result.exit_code == 3:
            return JUnitDecision(3, RESULTS_PATH_REASON, None)
        return JUnitDecision(15, read_result.reason, "not-accepted")

    mapped: dict[str, JUnitOutcome] = {}
    for testcase in read_result.mapped_tests:
        if testcase.identifier in mapped:
            return _not_accepted(JUNIT_DUPLICATE_REASON)
        mapped[testcase.identifier] = testcase.outcome
    if any(identifier not in mapped for identifier in required_tests):
        return _not_accepted(REQUIRED_ABSENT_REASON)
    if any(mapped[identifier] != JUnitOutcome.passed for identifier in required_tests):
        return _not_accepted(REQUIRED_NOT_PASSING_REASON)

    if snapshot_reason is not None:
        return JUnitDecision(15, snapshot_reason, "verifier-failure")
    return JUnitDecision(0, None, "accepted")
