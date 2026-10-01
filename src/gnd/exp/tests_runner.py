"""Measured tests-mode execution over a copied candidate tree.

ProcessLimits bounds child wall time and retained stream bytes; it does not contain the child.
The runner therefore treats the completed copy, result descriptor, process lifecycle, and two
before/after manifests as separate evidence rather than claiming an isolation boundary.
"""

from __future__ import annotations

import errno
import hashlib
import json
import os
import stat
import tempfile
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, replace
from pathlib import Path, PurePosixPath
from typing import Any, Literal, Self

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from gnd.agent_cli import BoundedProcessResult, ProcessLimits, run_bounded_process
from gnd.artifacts import canonical_json_bytes, sha256_hex
from gnd.exp.junit import (
    JUNIT_COLLISION_REASON,
    RESULTS_MISSING_REASON,
    RESULTS_SYMLINK_REASON,
    RESULTS_TYPE_REASON,
    VERIFIER_IO_REASON,
    ChildLifecycle,
    JUnitDecision,
    JUnitOutcome,
    JUnitReadResult,
    MappedTest,
    decide_junit_acceptance,
    read_junit,
    render_test_id,
)
from gnd.exp.session_contract import (
    CaseId,
    DataDrivenContract,
    ProtectedPath,
    Sha256String,
    TestsAcceptance,
)

__all__ = [
    "MAX_COPY_BYTES",
    "MAX_COPY_DEPTH",
    "MAX_COPY_ENTRIES",
    "TestsAcceptanceFeedback",
    "TestsResultFeedbackRow",
    "TestsRunOutcome",
    "TestsSessionResult",
    "copy_candidate_tree",
    "run_tests_mode",
    "tests_environment",
]

MAX_COPY_BYTES = 256 * 1024 * 1024
MAX_COPY_ENTRIES = 20_000
MAX_COPY_DEPTH = 64
MAX_RETAINED_STREAM_BYTES = 10 * 1024 * 1024

COPY_BYTES_REASON = "tests:copy-bytes"
COPY_ENTRIES_REASON = "tests:copy-entries"
COPY_DEPTH_REASON = "tests:copy-depth"
COPY_SPECIAL_REASON = "tests:copy-special"
RESULTS_PREEXISTING_REASON = "tests:results-preexisting"
PROTECTED_MUTATED_REASON = "tests:protected-mutated"
DIRECTORY_SNAPSHOT_MOVED_REASON = "tests:directory-snapshot-moved"
EXPERIMENT_DIR_MOVED_REASON = "tests:experiment-dir-moved"

_REGISTERED_RUN_REASONS = frozenset(
    {
        COPY_BYTES_REASON,
        COPY_ENTRIES_REASON,
        COPY_DEPTH_REASON,
        COPY_SPECIAL_REASON,
        RESULTS_PREEXISTING_REASON,
        RESULTS_MISSING_REASON,
        RESULTS_SYMLINK_REASON,
        RESULTS_TYPE_REASON,
        "tests:child-timeout",
        "tests:child-signal",
        "tests:child-nonzero",
        "tests:descendant-survived",
        "tests:results-too-large",
        "tests:results-encoding",
        "tests:results-dtd",
        "tests:results-xml-limit",
        "tests:results-xml-malformed",
        "tests:junit-collision",
        "tests:junit-duplicate",
        "tests:junit-outcome",
        "tests:junit-summary",
        "tests:required-absent",
        "tests:required-not-passing",
        PROTECTED_MUTATED_REASON,
        DIRECTORY_SNAPSHOT_MOVED_REASON,
        EXPERIMENT_DIR_MOVED_REASON,
        VERIFIER_IO_REASON,
    }
)


class TestsAcceptanceFeedback(BaseModel):
    """Answer-free tests feedback containing identifiers and one registered reason."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    mode: Literal["tests"] = "tests"
    required: tuple[str, ...]
    present: tuple[str, ...]
    passing: tuple[str, ...]
    reason: str | None = None

    @field_validator("reason")
    @classmethod
    def _reason_is_registered(cls, value: str | None) -> str | None:
        if value is not None and value not in _REGISTERED_RUN_REASONS:
            raise ValueError("tests feedback reason is not registered")
        return value


class TestsResultFeedbackRow(TestsAcceptanceFeedback):
    """One feedback row as ``result.json`` records it: the answer-free
    per-case record plus the case identity the writer prepends."""

    case_id: CaseId
    role: Literal["required", "diagnostic"]


class TestsSessionResult(BaseModel):
    """The tests-mode terminal ``result.json``, read back STRICTLY.

    :func:`_result_document` is the writer; this is its inverse, and the pair
    lives in one module so they cannot drift apart silently (a round-trip test
    pins the agreement). The reader exists for consumers that meet the document
    long after the run that wrote it — the work-kind close gate — where it is
    UNTRUSTED committed metadata: every field is required, unknown fields are
    refused, and the disposition vocabulary is closed, so a document that
    merely looks like a result does not open a gate.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1]
    #: Same closed token charset as case ids; the writer records the run
    #: directory's own name (``run-NNNN``) here.
    run_id: CaseId
    acceptance_modes: tuple[Literal["tests"], ...] = Field(min_length=1)
    disposition: Literal["accepted", "not-accepted", "verifier-failure"]
    reason: str | None
    launch_sha256: Sha256String | None
    feedback: tuple[TestsResultFeedbackRow, ...]

    @field_validator("reason")
    @classmethod
    def _reason_is_registered(cls, value: str | None) -> str | None:
        """The top-level reason obeys the same closed registry as a row's.

        The per-row model has always validated this; the document that carries
        the rows did not, so a result could be refused for a reason no lane can
        emit while every row inside it stayed well-formed.
        """
        if value is not None and value not in _REGISTERED_RUN_REASONS:
            raise ValueError("tests result reason is not registered")
        return value

    @model_validator(mode="after")
    def _acceptance_is_internally_consistent(self) -> Self:
        """An ``accepted`` document must be one the runner could have written.

        Field-level validity is not enough here, and the gap was reachable: a
        schema-valid document reporting ``accepted`` with no launch digest, no
        feedback rows, and a refusal reason was accepted by the reader and
        closed a work experiment that never ran anything. Every field in it was
        individually legal; the COMBINATION was one no run can produce.

        The three conditions are read off the writer's own accepting path: it
        reaches ``accepted`` only after a launch record exists (so the digest
        is present), only with one feedback row per declared case (so the rows
        are non-empty), and only with no refusal reason (so ``reason`` is
        ``None``). Each required test in a required row must also appear in
        that row's ``passing`` set, because "accepted" is exactly the claim
        that they did.
        """
        seen: set[str] = set()
        for row in self.feedback:
            if row.case_id in seen:
                raise ValueError(f"duplicate feedback row for case {row.case_id!r}")
            seen.add(row.case_id)
            # These hold for EVERY disposition: `present` is the required ids
            # the reader found, and `passing` the found ones that passed, so
            # each is a subset of the one before it. A document violating them
            # describes a run that could not have happened, whatever it then
            # claims about acceptance.
            if not set(row.passing) <= set(row.present):
                raise ValueError(
                    f"case {row.case_id!r} reports passing test(s) that are not "
                    f"present in its results"
                )
            if not set(row.present) <= set(row.required):
                raise ValueError(
                    f"case {row.case_id!r} reports present test(s) it never "
                    f"declared as required"
                )

        if self.disposition != "accepted":
            return self
        if self.launch_sha256 is None:
            raise ValueError("an accepted tests result must name its launch record")
        if self.reason is not None:
            raise ValueError("an accepted tests result cannot carry a refusal reason")
        if not self.feedback:
            raise ValueError("an accepted tests result must carry its per-case feedback")
        for row in self.feedback:
            # A per-row refusal reason is how a row records what went wrong.
            # An accepted document carrying one describes a run that both
            # refused and accepted the same case.
            if row.reason is not None:
                raise ValueError(
                    f"case {row.case_id!r} carries refusal reason "
                    f"{row.reason!r} in an accepted result"
                )
            if row.role != "required":
                continue
            missing = set(row.required) - set(row.passing)
            if missing:
                raise ValueError(
                    f"case {row.case_id!r} is accepted while required test(s) "
                    f"{', '.join(sorted(missing))} are not in its passing set"
                )
        return self


@dataclass(frozen=True, slots=True)
class TestsRunOutcome:
    """Published terminal tests-mode result returned to the CLI."""

    exit_code: int
    reason: str | None
    disposition: Literal["accepted", "not-accepted", "verifier-failure"]
    result_bytes: bytes


@dataclass(slots=True)
class _CopyBudget:
    entries: int = 0
    regular_bytes: int = 0


class _CopyRefusal(Exception):
    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(reason)


class _VerifierFailure(Exception):
    pass


class _ManifestChanged(Exception):
    pass


@dataclass(frozen=True, slots=True)
class _Manifest:
    sha256: str
    rows: tuple[dict[str, Any], ...]


@dataclass(frozen=True, slots=True)
class _HeldResultParent:
    results_path: str
    final_name: str
    descriptor: int


def tests_environment() -> dict[str, str]:
    """Call the shipped verifier allowlist expression at execution time."""

    from gnd.exp.session import verifier_environment

    return verifier_environment()


def _same_inode(left: os.stat_result, right: os.stat_result) -> bool:
    return (left.st_dev, left.st_ino) == (right.st_dev, right.st_ino)


def _copy_regular_file(source: Path, destination: Path, expected: os.stat_result) -> None:
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0)
    source_fd = os.open(source, flags)
    destination_fd = -1
    try:
        opened = os.fstat(source_fd)
        if not stat.S_ISREG(opened.st_mode) or not _same_inode(expected, opened):
            raise _VerifierFailure("regular source changed before copy")
        destination_fd = os.open(
            destination,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            stat.S_IMODE(expected.st_mode),
        )
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            view = memoryview(chunk)
            while view:
                written = os.write(destination_fd, view)
                view = view[written:]
        after = os.fstat(source_fd)
        if not _same_inode(opened, after) or after.st_size != opened.st_size:
            raise _VerifierFailure("regular source changed during copy")
        os.fchmod(destination_fd, stat.S_IMODE(expected.st_mode))
    finally:
        if destination_fd >= 0:
            os.close(destination_fd)
        os.close(source_fd)


def _copy_entry(
    source: Path,
    destination: Path,
    relative: PurePosixPath,
    budget: _CopyBudget,
) -> None:
    depth = len(relative.parts)
    if depth > MAX_COPY_DEPTH:
        raise _CopyRefusal(COPY_DEPTH_REASON)
    if budget.entries >= MAX_COPY_ENTRIES:
        raise _CopyRefusal(COPY_ENTRIES_REASON)

    info = os.lstat(source)
    budget.entries += 1
    mode = info.st_mode
    if stat.S_ISDIR(mode):
        destination.mkdir(mode=stat.S_IMODE(mode))
        os.chmod(destination, stat.S_IMODE(mode), follow_symlinks=False)
        with os.scandir(source) as entries:
            ordered = sorted(entries, key=lambda entry: os.fsencode(entry.name))
        for entry in ordered:
            child_relative = relative / entry.name
            if len(child_relative.parts) > MAX_COPY_DEPTH:
                raise _CopyRefusal(COPY_DEPTH_REASON)
            _copy_entry(source / entry.name, destination / entry.name, child_relative, budget)
        return
    if stat.S_ISREG(mode):
        if info.st_size < 0 or budget.regular_bytes > MAX_COPY_BYTES - info.st_size:
            raise _CopyRefusal(COPY_BYTES_REASON)
        budget.regular_bytes += info.st_size
        _copy_regular_file(source, destination, info)
        return
    if stat.S_ISLNK(mode):
        destination.symlink_to(os.readlink(source))
        return
    if (
        stat.S_ISFIFO(mode)
        or stat.S_ISSOCK(mode)
        or stat.S_ISBLK(mode)
        or stat.S_ISCHR(mode)
    ):
        raise _CopyRefusal(COPY_SPECIAL_REASON)
    raise _CopyRefusal(COPY_SPECIAL_REASON)


def copy_candidate_tree(source: Path, destination: Path) -> tuple[int, int]:
    """Copy one real candidate root without following links under D5's caps."""

    root_info = os.lstat(source)
    if stat.S_ISLNK(root_info.st_mode) or not stat.S_ISDIR(root_info.st_mode):
        raise _VerifierFailure("candidate root is not a real directory")
    destination.mkdir(mode=stat.S_IMODE(root_info.st_mode))
    budget = _CopyBudget()
    with os.scandir(source) as entries:
        ordered = sorted(entries, key=lambda entry: os.fsencode(entry.name))
    for entry in ordered:
        _copy_entry(
            source / entry.name,
            destination / entry.name,
            PurePosixPath(entry.name),
            budget,
        )
    return budget.entries, budget.regular_bytes


def _open_real_directory(path: Path) -> int:
    before = os.lstat(path)
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise _VerifierFailure("directory root is not real")
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or not _same_inode(before, opened):
        os.close(descriptor)
        raise _VerifierFailure("directory root changed before opening")
    return descriptor


def _digest_regular_path(path: Path, expected: os.stat_result) -> tuple[int, str]:
    descriptor = os.open(
        path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0),
    )
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or not _same_inode(expected, opened):
            raise _VerifierFailure("manifest file changed before opening")
        digest = hashlib.sha256()
        observed = 0
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            observed += len(chunk)
            digest.update(chunk)
        after = os.fstat(descriptor)
        if not _same_inode(opened, after) or observed != opened.st_size:
            raise _VerifierFailure("manifest file changed while reading")
        return observed, digest.hexdigest()
    finally:
        os.close(descriptor)


def _kind(mode: int) -> str:
    if stat.S_ISDIR(mode):
        return "directory"
    if stat.S_ISREG(mode):
        return "regular"
    if stat.S_ISLNK(mode):
        return "symlink"
    if stat.S_ISFIFO(mode):
        return "fifo"
    if stat.S_ISSOCK(mode):
        return "socket"
    if stat.S_ISBLK(mode):
        return "block-device"
    if stat.S_ISCHR(mode):
        return "character-device"
    return "special"


def _manifest(
    root: Path,
    *,
    reserved_paths: frozenset[str] = frozenset(),
    excluded_prefixes: tuple[PurePosixPath, ...] = (),
    bounded: bool = False,
    reference: _Manifest | None = None,
) -> _Manifest:
    rows: list[dict[str, Any]] = []
    stack: list[tuple[Path, PurePosixPath]] = []
    discovered = 0
    regular_bytes = 0
    expected = (
        {row["path"]: row for row in reference.rows if row["kind"] != "absent-before-spawn"}
        if reference is not None
        else None
    )

    def excluded(relative: PurePosixPath) -> bool:
        return (
            relative.as_posix() in reserved_paths
            or any(relative == prefix or prefix in relative.parents for prefix in excluded_prefixes)
            or any(
                part == ".pytest_cache" or part == "__pycache__"
                for part in relative.parts
            )
        )

    def discover(directory: Path, relative_parent: PurePosixPath | None) -> None:
        nonlocal discovered
        with os.scandir(directory) as entries:
            for entry in entries:
                relative = (
                    PurePosixPath(entry.name)
                    if relative_parent is None
                    else relative_parent / entry.name
                )
                if excluded(relative):
                    continue
                relative_text = relative.as_posix()
                if expected is not None and relative_text not in expected:
                    raise _ManifestChanged
                if bounded and discovered >= MAX_COPY_ENTRIES:
                    raise _ManifestChanged
                discovered += 1
                stack.append((directory / entry.name, relative))

    discover(root, None)

    while stack:
        path, relative = stack.pop()
        relative_text = relative.as_posix()
        info = os.lstat(path)
        kind = _kind(info.st_mode)
        row: dict[str, Any] = {
            "kind": kind,
            "mode": stat.S_IMODE(info.st_mode),
            "path": relative_text,
        }
        expected_row = expected.get(relative_text) if expected is not None else None
        if expected_row is not None and any(
            expected_row.get(field) != row.get(field) for field in ("kind", "mode")
        ):
            raise _ManifestChanged
        if kind == "regular":
            if bounded and (
                info.st_size < 0 or regular_bytes > MAX_COPY_BYTES - info.st_size
            ):
                raise _ManifestChanged
            if expected_row is not None and expected_row.get("size_bytes") != info.st_size:
                raise _ManifestChanged
            regular_bytes += info.st_size
            size, digest = _digest_regular_path(path, info)
            row.update({"sha256": digest, "size_bytes": size})
        elif kind == "symlink":
            row["link_text"] = os.readlink(path)
        rows.append(row)
        if kind == "directory":
            if bounded and len(relative.parts) >= MAX_COPY_DEPTH:
                with os.scandir(path) as entries:
                    if next(entries, None) is not None:
                        raise _ManifestChanged
            else:
                discover(path, relative)

    for reserved in reserved_paths:
        rows.append({"kind": "absent-before-spawn", "path": reserved})
    rows.sort(key=lambda row: os.fsencode(row["path"]))
    canonical = canonical_json_bytes(rows)
    return _Manifest(sha256=sha256_hex(canonical), rows=tuple(rows))


def _moved_manifest(reference: _Manifest) -> _Manifest:
    marker = canonical_json_bytes({"changed_from": reference.sha256})
    return _Manifest(sha256=sha256_hex(marker), rows=())


def _open_protected(root_fd: int, protected: ProtectedPath) -> str | None:
    current_fd = os.dup(root_fd)
    try:
        parts = PurePosixPath(protected.path).parts
        for index, part in enumerate(parts):
            info = os.stat(part, dir_fd=current_fd, follow_symlinks=False)
            final = index == len(parts) - 1
            if stat.S_ISLNK(info.st_mode):
                return None
            expected_kind = stat.S_ISREG if final else stat.S_ISDIR
            if not expected_kind(info.st_mode):
                return None
            flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
            flags |= getattr(os, "O_NONBLOCK", 0) if final else getattr(os, "O_DIRECTORY", 0)
            next_fd = os.open(part, flags, dir_fd=current_fd)
            opened = os.fstat(next_fd)
            if not _same_inode(info, opened):
                os.close(next_fd)
                return None
            os.close(current_fd)
            current_fd = next_fd
        digest = hashlib.sha256()
        while True:
            chunk = os.read(current_fd, 1024 * 1024)
            if not chunk:
                break
            digest.update(chunk)
        return digest.hexdigest()
    except OSError:
        return None
    finally:
        os.close(current_fd)


def _protected_match(root_fd: int, protected: Iterable[ProtectedPath]) -> bool:
    return all(_open_protected(root_fd, entry) == entry.sha256 for entry in protected)


def _path_error_reason(error: OSError) -> str:
    if error.errno == errno.ENOENT:
        return RESULTS_MISSING_REASON
    if error.errno in {errno.ELOOP, getattr(errno, "EMLINK", errno.ELOOP)}:
        return RESULTS_SYMLINK_REASON
    if error.errno in {errno.ENOTDIR, errno.ENXIO, getattr(errno, "ENODEV", errno.ENXIO)}:
        return RESULTS_TYPE_REASON
    return VERIFIER_IO_REASON


def _hold_result_parent(root_fd: int, results_path: str) -> tuple[_HeldResultParent | None, str | None]:
    components = results_path.split("/")
    current_fd = os.dup(root_fd)
    try:
        for component in components[:-1]:
            try:
                info = os.stat(component, dir_fd=current_fd, follow_symlinks=False)
            except OSError as error:
                return None, _path_error_reason(error)
            if stat.S_ISLNK(info.st_mode):
                return None, RESULTS_SYMLINK_REASON
            if not stat.S_ISDIR(info.st_mode):
                return None, RESULTS_TYPE_REASON
            try:
                next_fd = os.open(
                    component,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0),
                    dir_fd=current_fd,
                )
            except OSError as error:
                return None, _path_error_reason(error)
            opened = os.fstat(next_fd)
            if not stat.S_ISDIR(opened.st_mode) or not _same_inode(info, opened):
                os.close(next_fd)
                return None, VERIFIER_IO_REASON
            os.close(current_fd)
            current_fd = next_fd

        final_name = components[-1]
        try:
            existing = os.stat(final_name, dir_fd=current_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        except OSError as error:
            return None, _path_error_reason(error)
        else:
            if stat.S_ISLNK(existing.st_mode):
                return None, RESULTS_SYMLINK_REASON
            return None, RESULTS_PREEXISTING_REASON
        held = _HeldResultParent(results_path, final_name, current_fd)
        current_fd = -1
        return held, None
    finally:
        if current_fd >= 0:
            os.close(current_fd)


def _open_result_once(parent: _HeldResultParent) -> tuple[int | None, str | None]:
    try:
        before = os.stat(parent.final_name, dir_fd=parent.descriptor, follow_symlinks=False)
    except OSError as error:
        return None, _path_error_reason(error)
    if stat.S_ISLNK(before.st_mode):
        return None, RESULTS_SYMLINK_REASON
    flags = (
        os.O_RDONLY
        | getattr(os, "O_NONBLOCK", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_CLOEXEC", 0)
    )
    try:
        descriptor = os.open(parent.final_name, flags, dir_fd=parent.descriptor)
    except OSError as error:
        return None, _path_error_reason(error)
    try:
        opened = os.fstat(descriptor)
    except OSError:
        os.close(descriptor)
        return None, VERIFIER_IO_REASON
    if not _same_inode(before, opened):
        os.close(descriptor)
        return None, VERIFIER_IO_REASON
    if not stat.S_ISREG(opened.st_mode):
        os.close(descriptor)
        return None, RESULTS_TYPE_REASON
    return descriptor, None


def _read_refusal(reason: str) -> JUnitReadResult:
    return JUnitReadResult(reason=reason, exit_code=15)


def _lifecycle(process: BoundedProcessResult) -> ChildLifecycle:
    descendant_survived = (
        process.spawned
        and process.return_code == 0
        and bool(process.termination_steps)
    )
    return ChildLifecycle(
        exit_code=process.return_code,
        timed_out=process.timed_out and not descendant_survived,
        signal_number=process.signal,
        descendant_survived=descendant_survived,
    )


def _pytest_nodeids(argv: Sequence[str]) -> tuple[str, ...]:
    return tuple(
        word
        for word in argv
        if "::" in word and word.partition("::")[0].endswith(".py")
    )


def _reader_required_ids(
    acceptances: Sequence[TestsAcceptance],
    argv: Sequence[str],
) -> list[str]:
    required: list[str] = []
    for acceptance in acceptances:
        for identifier in acceptance.required_tests:
            path, separator, selectors = identifier.partition("::")
            aliases = [identifier]
            if separator and "/" in path:
                aliases.append(f"{path.rsplit('/', 1)[-1]}::{selectors}")
            for selected in _pytest_nodeids(argv):
                selected_path = selected.partition("::")[0]
                if selected_path == path:
                    aliases.append(selected)
            for alias in aliases:
                if alias not in required:
                    required.append(alias)
    return required


def _project_case_read(
    read_result: JUnitReadResult,
    acceptance: TestsAcceptance,
    argv: Sequence[str],
) -> JUnitReadResult:
    if read_result.reason is not None:
        return read_result
    mapped = {item.identifier: item.outcome for item in read_result.mapped_tests}
    projected = list(read_result.mapped_tests)
    selected = _pytest_nodeids(argv)
    for identifier in acceptance.required_tests:
        if identifier in mapped:
            continue
        path, separator, selectors = identifier.partition("::")
        aliases: list[str] = []
        if separator and "/" in path:
            aliases.append(f"{path.rsplit('/', 1)[-1]}::{selectors}")
        aliases.extend(item for item in selected if item.partition("::")[0] == path)
        outcome = next((mapped[alias] for alias in aliases if alias in mapped), None)
        if outcome is not None:
            projected.append(MappedTest(identifier=identifier, outcome=outcome))
    return replace(read_result, mapped_tests=tuple(projected))


def _feedback(
    required: Sequence[str],
    read_result: JUnitReadResult,
    reason: str | None,
) -> TestsAcceptanceFeedback:
    mapped = {item.identifier: item.outcome for item in read_result.mapped_tests}
    return TestsAcceptanceFeedback(
        required=tuple(required),
        present=tuple(identifier for identifier in required if identifier in mapped),
        passing=tuple(
            identifier
            for identifier in required
            if mapped.get(identifier) is JUnitOutcome.passed
        ),
        reason=reason,
    )


def _write_once(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor = os.open(
        path,
        os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
        0o644,
    )
    try:
        view = memoryview(data)
        while view:
            written = os.write(descriptor, view)
            view = view[written:]
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _result_document(
    run_root: Path,
    *,
    disposition: str,
    reason: str | None,
    feedback: Sequence[tuple[str, str, TestsAcceptanceFeedback]],
    launch_sha256: str | None,
) -> bytes:
    document = {
        "acceptance_modes": ["tests"],
        "disposition": disposition,
        "feedback": [
            {"case_id": case_id, "role": role, **item.model_dump(mode="json")}
            for case_id, role, item in feedback
        ],
        "launch_sha256": launch_sha256,
        "reason": reason,
        "run_id": run_root.name,
        "schema_version": 1,
    }
    return canonical_json_bytes(document)


def _finish_without_launch(
    run_root: Path,
    cases: Sequence[tuple[str, str, TestsAcceptance]],
    *,
    reason: str,
    disposition: Literal["not-accepted", "verifier-failure"],
) -> TestsRunOutcome:
    empty = JUnitReadResult(reason=reason, exit_code=15)
    feedback = [
        (case_id, role, _feedback(acceptance.required_tests, empty, reason))
        for case_id, role, acceptance in cases
    ]
    result_bytes = _result_document(
        run_root,
        disposition=disposition,
        reason=reason,
        feedback=feedback,
        launch_sha256=None,
    )
    _write_once(run_root / "result.json", result_bytes)
    return TestsRunOutcome(15, reason, disposition, result_bytes)


def _experiment_exclusions(experiment_root: Path, run_root: Path) -> tuple[PurePosixPath, ...]:
    relative = PurePosixPath(run_root.relative_to(experiment_root).as_posix())
    return (
        relative / "launches",
        relative / "attempts",
        relative / "best.json",
        relative / "result.json",
    )


async def run_tests_mode(
    contract: DataDrivenContract,
    *,
    argv: Sequence[str],
    candidate_root: Path,
    experiment_root: Path,
    run_root: Path,
    contract_sha256: str,
) -> TestsRunOutcome:
    """Run the seven ordered tests-mode stages and publish one terminal record."""

    # Step 1: Lane A and the CLI have validated shape, caps, coverage, arity, and echo.
    cases = [
        (case.case_id, case.role.value, case.acceptance)
        for case in contract.cases
        if isinstance(case.acceptance, TestsAcceptance)
    ]
    if not cases:
        raise ValueError("run_tests_mode requires at least one tests acceptance")
    run_root.mkdir(parents=True)

    protected_by_path: dict[str, ProtectedPath] = {}
    for _, _, acceptance in cases:
        for protected in acceptance.protected:
            protected_by_path.setdefault(
                protected.path,
                ProtectedPath(path=protected.path, sha256=protected.sha256),
            )
    protected = tuple(protected_by_path.values())
    reserved_paths = frozenset(acceptance.results_path for _, _, acceptance in cases)

    try:
        temporary = tempfile.TemporaryDirectory(prefix="gnd-tests-")
    except OSError:
        return _finish_without_launch(
            run_root,
            cases,
            reason=VERIFIER_IO_REASON,
            disposition="verifier-failure",
        )

    with temporary:
        scratch = Path(temporary.name) / "candidate"
        try:
            # Step 2: copy first, then verify seals against the completed copy.
            copy_candidate_tree(candidate_root, scratch)
            scratch_fd = _open_real_directory(scratch)
        except _CopyRefusal as refusal:
            return _finish_without_launch(
                run_root,
                cases,
                reason=refusal.reason,
                disposition="not-accepted",
            )
        except (OSError, _VerifierFailure):
            return _finish_without_launch(
                run_root,
                cases,
                reason=VERIFIER_IO_REASON,
                disposition="verifier-failure",
            )

        held_parents: dict[str, _HeldResultParent] = {}
        try:
            if not _protected_match(scratch_fd, protected):
                return _finish_without_launch(
                    run_root,
                    cases,
                    reason=VERIFIER_IO_REASON,
                    disposition="verifier-failure",
                )

            # Step 3: hold every unique parent and prove each reserved leaf absent.
            for results_path in sorted(reserved_paths):
                held, reason = _hold_result_parent(scratch_fd, results_path)
                if reason is not None or held is None:
                    disposition = (
                        "verifier-failure" if reason == VERIFIER_IO_REASON else "not-accepted"
                    )
                    return _finish_without_launch(
                        run_root,
                        cases,
                        reason=reason or VERIFIER_IO_REASON,
                        disposition=disposition,
                    )
                held_parents[results_path] = held

            # Step 4: hash the two completed pre-spawn snapshots.
            try:
                scratch_before = _manifest(
                    scratch,
                    reserved_paths=reserved_paths,
                    bounded=True,
                )
                experiment_before = _manifest(
                    experiment_root,
                    excluded_prefixes=_experiment_exclusions(experiment_root, run_root),
                )
            except (OSError, _ManifestChanged, _VerifierFailure):
                return _finish_without_launch(
                    run_root,
                    cases,
                    reason=VERIFIER_IO_REASON,
                    disposition="verifier-failure",
                )

            # Step 5: the exact vector is passed to the shipped bounded process runner.
            process = await run_bounded_process(
                tuple(argv),
                cwd=scratch,
                env=tests_environment(),
                limits=ProcessLimits(
                    timeout_seconds=contract.wall_seconds or 300.0,
                    terminate_grace_seconds=min(1.0, contract.wall_seconds or 300.0),
                    stdin_limit_bytes=0,
                    stdout_limit_bytes=MAX_RETAINED_STREAM_BYTES,
                    stderr_limit_bytes=MAX_RETAINED_STREAM_BYTES,
                    total_output_limit_bytes=MAX_RETAINED_STREAM_BYTES * 2,
                ),
            )
            lifecycle = _lifecycle(process)

            # Step 6: open each result once through its retained parent descriptor.
            acceptances_by_path: dict[str, list[TestsAcceptance]] = {}
            for _, _, acceptance in cases:
                acceptances_by_path.setdefault(acceptance.results_path, []).append(acceptance)
            reads: dict[str, JUnitReadResult] = {}
            for results_path, acceptances in acceptances_by_path.items():
                result_fd, open_reason = _open_result_once(held_parents[results_path])
                if open_reason is not None or result_fd is None:
                    reads[results_path] = _read_refusal(open_reason or VERIFIER_IO_REASON)
                    continue
                try:
                    reads[results_path] = read_junit(
                        scratch_fd,
                        results_path,
                        _reader_required_ids(acceptances, argv),
                        result_fd=result_fd,
                    )
                finally:
                    os.close(result_fd)
                rendered: dict[tuple[str, str], set[str]] = {}
                for acceptance in acceptances:
                    for identifier in acceptance.required_tests:
                        identity = render_test_id(identifier)
                        if identity is not None:
                            rendered.setdefault(identity, set()).add(identifier)
                if any(len(identifiers) > 1 for identifiers in rendered.values()):
                    reads[results_path] = _read_refusal(JUNIT_COLLISION_REASON)

            # Step 7: re-verify in protected, scratch, experiment order before decision.
            snapshot_reason: str | None = None
            verifier_failure = False
            if not _protected_match(scratch_fd, protected):
                snapshot_reason = PROTECTED_MUTATED_REASON
            try:
                scratch_after = _manifest(
                    scratch,
                    reserved_paths=reserved_paths,
                    bounded=True,
                    reference=scratch_before,
                )
            except _ManifestChanged:
                scratch_after = _moved_manifest(scratch_before)
            except (OSError, _VerifierFailure):
                scratch_after = _Manifest(sha256="0" * 64, rows=())
                verifier_failure = True
            try:
                experiment_after = _manifest(
                    experiment_root,
                    excluded_prefixes=_experiment_exclusions(experiment_root, run_root),
                    reference=experiment_before,
                )
            except _ManifestChanged:
                experiment_after = _moved_manifest(experiment_before)
            except (OSError, _VerifierFailure):
                experiment_after = _Manifest(sha256="0" * 64, rows=())
                verifier_failure = True
            if snapshot_reason is None and scratch_after.sha256 != scratch_before.sha256:
                snapshot_reason = DIRECTORY_SNAPSHOT_MOVED_REASON
            if snapshot_reason is None and experiment_after.sha256 != experiment_before.sha256:
                snapshot_reason = EXPERIMENT_DIR_MOVED_REASON

            decisions: list[tuple[str, str, TestsAcceptance, JUnitDecision]] = []
            case_reads: dict[str, JUnitReadResult] = {}
            for case_id, role, acceptance in cases:
                case_read = _project_case_read(
                    reads[acceptance.results_path],
                    acceptance,
                    argv,
                )
                case_reads[case_id] = case_read
                decision = decide_junit_acceptance(
                    lifecycle,
                    case_read,
                    acceptance.required_tests,
                    verifier_failure=verifier_failure,
                    snapshot_reason=snapshot_reason,
                )
                decisions.append((case_id, role, acceptance, decision))

            required_decisions = [item for item in decisions if item[1] == "required"]
            final = next(
                (item[3] for item in required_decisions if item[3].exit_code != 0),
                JUnitDecision(0, None, "accepted"),
            )
            disposition = final.disposition or "not-accepted"
            feedback = [
                (
                    case_id,
                    role,
                    _feedback(
                        acceptance.required_tests,
                        case_reads[case_id],
                        decision.reason,
                    ),
                )
                for case_id, role, acceptance, decision in decisions
            ]
            argv_list = list(argv)
            argv_sha256 = sha256_hex(
                json.dumps(argv_list, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
            )
            launch_document = {
                "argv": argv_list,
                "argv_sha256": argv_sha256,
                "child": process.model_dump(mode="json", exclude={"stdout", "stderr"}),
                "contract_sha256": contract_sha256,
                "experiment_after_sha256": experiment_after.sha256,
                "experiment_before_sha256": experiment_before.sha256,
                "feedback": [
                    {"case_id": case_id, "role": role, **item.model_dump(mode="json")}
                    for case_id, role, item in feedback
                ],
                "reason": final.reason,
                "result_sha256": {
                    path: read.sha256 for path, read in sorted(reads.items())
                },
                "run_id": run_root.name,
                "schema_version": 1,
                "scratch_after_sha256": scratch_after.sha256,
                "scratch_before_sha256": scratch_before.sha256,
            }
            launch_bytes = canonical_json_bytes(launch_document)
            _write_once(run_root / "launches" / "0001.json", launch_bytes)
            launch_sha256 = sha256_hex(launch_bytes)
            result_bytes = _result_document(
                run_root,
                disposition=disposition,
                reason=final.reason,
                feedback=feedback,
                launch_sha256=launch_sha256,
            )
            _write_once(run_root / "result.json", result_bytes)
            return TestsRunOutcome(final.exit_code, final.reason, disposition, result_bytes)
        finally:
            for held in held_parents.values():
                os.close(held.descriptor)
            os.close(scratch_fd)
