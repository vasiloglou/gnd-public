"""Assertion #1 — every DERIVED file still hashes to what the manifest recorded.

The comparison itself is four lines. Everything else in this module is about the
three ways it could ship unable to fail, or able to fail dishonestly.

**It must not speak about extension files (G-08).** ``pyproject.toml`` and the
``references/`` notes carry recorded digests, and comparing them would be easy,
louder, and wrong: those bytes are user- or LLM-authored, GND never promised to
reproduce them, and a mismatch there is a person doing their job. So every
``extension`` entry is recorded as UNEXAMINED and never opened. The partition is
the product of this module, not a by-product.

**It must not trust the manifest's paths (T-03-25).** ``read_manifest`` applies
the lexical rule, and this module applies it AGAIN before any file is opened,
because a caller can construct a :class:`~gnd.codegen.manifest.CodegenManifest`
directly and nothing about "our own reader would have caught it" survives that.
No content-supplied path is ever joined raw.

**It must not be talked into reading something (T-03-24/28).** The tree under
inspection is user-controlled. This module never imports it — importing a
generated module to inspect it would execute arbitrary user code on every CI
run — opens with ``os.lstat`` so a symlink planted at a recorded path is
reported rather than followed, and reports an occupant over
:data:`MAX_CONFORMANCE_BYTES` from its stat rather than hashing it.

**And what it cannot see is published, not implied (RESEARCH §2.5).** A manifest
cannot record its own digest, so this detects a UNILATERAL edit to a derived
file and not a CO-EDIT of that file together with its manifest entry. ``gnd
doctor`` carries the identical bound. It is stated as importable data in
:data:`gnd.codegen.manifest.INTEGRITY_LIMITS` and carried into the payload's
``limits`` block by :mod:`gnd.conformance.report`, so the limitation cannot be
lost by a reader skimming past a docstring.
"""

from __future__ import annotations

import os
import stat
from pathlib import Path

from gnd.artifacts import ArtifactError, read_regular_bounded, read_regular_bounded_at
from gnd.codegen.manifest import (
    MANIFEST_RULE_ID,
    CodegenManifest,
    ManagedFile,
)
from gnd.conformance import (
    UNEXAMINED_REASON,
    ConformanceError,
    ConformanceResult,
    ExaminedFile,
    Finding,
    UnexaminedFile,
)
from gnd.extract.manifest import manifest_path_issue

__all__ = [
    "MAX_CONFORMANCE_BYTES",
    "bind_project_root",
    "check_integrity",
    "open_project_root",
]

#: Byte ceiling on a file this module will HASH. Deliberately equal to
#: ``gnd.codegen.plan.MAX_CLASSIFY_BYTES`` (itself equal to
#: ``install.MAX_CLASSIFY_BYTES``), and imported rather than re-spelled so the
#: three lanes bound untrusted input identically and a future correction lands
#: in all of them. Over the cap the file is reported from its stat and never
#: read (T-03-28).
MAX_CONFORMANCE_BYTES = 10 * 1024 * 1024


def open_project_root(
    project_root: str | Path,
    *,
    expected: tuple[int, int] | None = None,
) -> int:
    """Open one real project root and transfer descriptor ownership to caller."""

    root = Path(project_root)
    try:
        before = root.lstat()
    except OSError as error:
        raise ConformanceError("generated project root could not be inspected") from error
    if stat.S_ISLNK(before.st_mode) or not stat.S_ISDIR(before.st_mode):
        raise ConformanceError("generated project root is not a real directory")
    descriptor = -1
    try:
        descriptor = os.open(
            root,
            os.O_RDONLY
            | getattr(os, "O_DIRECTORY", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        opened = os.fstat(descriptor)
    except OSError as error:
        if descriptor >= 0:
            os.close(descriptor)
        raise ConformanceError("generated project root could not be opened safely") from error
    identity = (opened.st_dev, opened.st_ino)
    if identity != (before.st_dev, before.st_ino):
        os.close(descriptor)
        raise ConformanceError("generated project root changed before it opened")
    if expected is not None and identity != expected:
        os.close(descriptor)
        raise ConformanceError("generated project root changed during conformance")
    return descriptor


def bind_project_root(
    project_root: str | Path,
    *,
    expected: tuple[int, int] | None = None,
) -> tuple[int, int]:
    """Bind one real project root without following its pathname."""

    descriptor = open_project_root(project_root, expected=expected)
    try:
        opened = os.fstat(descriptor)
        return opened.st_dev, opened.st_ino
    finally:
        os.close(descriptor)


def _safe_target(project_root: Path, entry: ManagedFile) -> Path:
    """The entry's path under ``project_root``, or refuse.

    Re-applies the manifest's LEXICAL rule (POSIX- and Windows-absolute, drive
    letters, ``..``) before anything is joined. ``read_manifest`` already does
    this — and this is not redundant, because :class:`CodegenManifest` is a
    plain pydantic model any caller can construct without going through the
    reader.
    """
    issue = manifest_path_issue("relpath", entry.relpath, MANIFEST_RULE_ID)
    if issue is not None:
        raise ConformanceError(
            f"the manifest names an unsafe path and conformance refused to open "
            f"it: {issue.message}"
        )
    return project_root / entry.relpath


def _finding_for_derived(
    project_root: Path,
    entry: ManagedFile,
    *,
    expected_root: tuple[int, int] | None,
    root_fd: int | None,
) -> tuple[
    Finding | None, str | None
]:
    """``(finding, actual_digest)`` for one derived entry.

    Returns a finding rather than raising for every state that is a fact ABOUT
    THE PROJECT — absent, not a regular file, over the cap, different bytes.
    Raising would abort the check over every other file in the tree, so one
    deleted module would deny the answer for the other eight.
    """
    _safe_target(project_root, entry)

    try:
        if root_fd is None:
            _data, snapshot = read_regular_bounded(
                project_root,
                entry.relpath,
                max_bytes=MAX_CONFORMANCE_BYTES,
                expected_root=expected_root,
            )
        else:
            _data, snapshot = read_regular_bounded_at(
                root_fd,
                entry.relpath,
                max_bytes=MAX_CONFORMANCE_BYTES,
            )
    except ArtifactError as error:
        cause: BaseException | None = error
        missing = False
        while cause is not None:
            if isinstance(cause, FileNotFoundError):
                missing = True
                break
            cause = cause.__cause__
        if missing:
            return (
                Finding(
                    kind="derived-file-missing",
                    target=entry.relpath,
                    message=(
                        f"{entry.relpath} is recorded in the manifest (sha256 "
                        f"{entry.sha256[:12]}…) and is not on disk; regenerate to "
                        f"restore it"
                    ),
                    recorded_sha256=entry.sha256,
                    actual_sha256=None,
                ),
                None,
            )
        detail = str(error)
        if detail == f"artifact {entry.relpath} is a symlink":
            message = (
                f"{entry.relpath} is a symlink, not the regular file codegen wrote "
                f"(recorded sha256 {entry.sha256[:12]}…); it was reported from its "
                "own stat and never followed"
            )
        elif detail == f"artifact {entry.relpath} is not a regular file":
            message = (
                f"{entry.relpath} is not a regular file, so the recorded sha256 "
                f"{entry.sha256[:12]}… cannot be compared against anything"
            )
        elif detail.startswith(f"artifact {entry.relpath} is ") and "over the" in detail:
            message = (
                f"{detail}; it was reported from its stat and never read (T-03-28). "
                f"Its recorded sha256 is {entry.sha256[:12]}…"
            )
        else:
            raise ConformanceError(
                f"{entry.relpath} could not be read (cause: file-io)"
            ) from error
        return (
            Finding(
                kind="derived-file-modified",
                target=entry.relpath,
                message=message,
                recorded_sha256=entry.sha256,
                actual_sha256=None,
            ),
            None,
        )
    actual = snapshot.sha256

    if actual != entry.sha256:
        return (
            Finding(
                kind="derived-file-modified",
                target=entry.relpath,
                message=(
                    f"{entry.relpath} does not match the manifest: recorded "
                    f"sha256 {entry.sha256[:12]}…, actual {actual[:12]}…. It is "
                    f"a derived file, so regeneration is the repair — but "
                    f"`gnd codegen` will refuse it at exit 11 until you pass "
                    f"--force, and nothing here has destroyed the edit"
                ),
                recorded_sha256=entry.sha256,
                actual_sha256=actual,
            ),
            actual,
        )
    return None, actual


def check_integrity(
    project_root: str | Path,
    manifest: CodegenManifest,
    *,
    expected_root: tuple[int, int] | None = None,
    root_fd: int | None = None,
) -> ConformanceResult:
    """Assertion #1 over ``manifest``'s entries, rooted at ``project_root``.

    A pure function of a directory and a record: no argv, no CLI, no global
    state, and nothing written. The same property :func:`check_currency` is
    designed for, for the same reason — a check that only the CLI can perform
    is a check no other entry point can reuse.

    Every entry lands in exactly one of ``examined`` and ``unexamined``, and the
    ``findings`` are drawn only from ``examined``. Raises
    :class:`~gnd.conformance.ConformanceError` only when conformance could not
    be performed at all — a refused path, or a file that exists and cannot be
    read — because that is the one case where "no findings" would be a lie.
    """
    root = Path(project_root)
    findings: list[Finding] = []
    examined: list[ExaminedFile] = []
    unexamined: list[UnexaminedFile] = []

    for entry in sorted(manifest.files, key=lambda item: item.relpath):
        if entry.ownership != "derived":
            # Not leniency, and not an omission: see UNEXAMINED_REASON. The
            # path is still validated so a hostile relpath cannot ride into the
            # payload unchecked just because nothing opens it.
            _safe_target(root, entry)
            unexamined.append(
                UnexaminedFile(
                    relpath=entry.relpath,
                    ownership=entry.ownership,
                    reason=UNEXAMINED_REASON,
                )
            )
            continue

        finding, actual = _finding_for_derived(
            root,
            entry,
            expected_root=expected_root,
            root_fd=root_fd,
        )
        if finding is not None:
            findings.append(finding)
        examined.append(
            ExaminedFile(
                relpath=entry.relpath,
                recorded_sha256=entry.sha256,
                actual_sha256=actual,
            )
        )

    return ConformanceResult(
        findings=tuple(findings),
        examined=tuple(examined),
        unexamined=tuple(unexamined),
    )
