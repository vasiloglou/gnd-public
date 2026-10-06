"""Bounded, no-follow artifact reads and publication primitives.

The helpers in this module deliberately know nothing about experiment sessions.
They provide the small filesystem vocabulary shared by session evidence and the
later recovery/evolution workflows: canonical tree identity, expected-identity
leaf replacement, and append-once manifest-last directory publication.
"""

from __future__ import annotations

import ctypes
import hashlib
import json
import os
import secrets
import stat
from collections.abc import Mapping, Sequence
from contextlib import suppress
from decimal import Decimal
from itertools import pairwise
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

__all__ = [
    "ArtifactError",
    "ArtifactIdentityError",
    "LeafSnapshot",
    "Sha256",
    "TrackedRegularEntry",
    "TrackedSymlinkEntry",
    "TrackedTreeEntry",
    "TreeFile",
    "TreeInventory",
    "canonical_json_bytes",
    "canonical_json_text",
    "canonical_report_text",
    "inventory_tree",
    "is_sha256_hex",
    "publish_directory_once",
    "publish_leaf_atomic",
    "read_regular_bounded",
    "read_regular_bounded_at",
    "read_regular_file_bytes",
    "readlink_at",
    "reject_json_constant",
    "reject_json_duplicate_pairs",
    "reject_json_duplicate_pairs_result",
    "remove_regular_if_unchanged",
    "sha256_hex",
    "snapshot_tracked_roster",
    "stat_leaf_at",
    "tree_sha256_from_directory",
    "tree_sha256_from_inventory",
]

DEFAULT_MAX_FILES = 10_000
DEFAULT_MAX_FILE_BYTES = 10 * 1024 * 1024
DEFAULT_MAX_TOTAL_BYTES = 100 * 1024 * 1024
DEFAULT_MAX_DEPTH = 64
FILE_MODE = 0o644
DIRECTORY_MODE = 0o755

Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
NonEmptyString = Annotated[str, StringConstraints(min_length=1)]


class ArtifactError(Exception):
    """An artifact path, identity, bound, or publication invariant failed."""


class ArtifactIdentityError(ArtifactError):
    """A descriptor-bound leaf changed from an identity already budgeted."""


class LeafSnapshot(BaseModel):
    """Stable identity observed while one regular leaf descriptor was open."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    file_type: Literal["regular"] = "regular"
    size_bytes: int = Field(ge=0)
    sha256: Sha256
    mode: int = Field(ge=0)
    device: int = Field(ge=0)
    inode: int = Field(ge=0)
    mtime_ns: int


class TreeFile(BaseModel):
    """One regular leaf in a complete tree inventory."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    file_type: Literal["regular"] = "regular"
    size_bytes: int = Field(ge=0)
    sha256: Sha256
    executable: bool = False


class TrackedRegularEntry(BaseModel):
    """One LISTED regular leaf, observed while its descriptor was open.

    ``executable`` is part of the identity: a mode change is a real change.
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    file_type: Literal["regular"] = "regular"
    size_bytes: int = Field(ge=0)
    sha256: Sha256
    executable: bool = False


class TrackedSymlinkEntry(BaseModel):
    """One LISTED symlink leaf, described by its LEXICAL target, never followed."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    path: NonEmptyString
    file_type: Literal["symlink"] = "symlink"
    target: NonEmptyString


#: The closed leaf union a snapshot observes: a roster names LEAVES only.
TrackedTreeEntry = TrackedRegularEntry | TrackedSymlinkEntry


class TreeInventory(BaseModel):
    """Canonical identity of all regular leaves beneath one real directory."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    schema_version: Literal[1] = 1
    files: tuple[TreeFile, ...]
    file_count: int = Field(ge=0)
    total_bytes: int = Field(ge=0)
    tree_sha256: Sha256

    @model_validator(mode="after")
    def _canonical_totals_and_order(self) -> Self:
        paths = [entry.path for entry in self.files]
        if paths != sorted(paths) or len(paths) != len(set(paths)):
            raise ValueError("tree files must have unique paths in sorted order")
        if self.file_count != len(self.files):
            raise ValueError("tree file_count does not match files")
        if self.total_bytes != sum(entry.size_bytes for entry in self.files):
            raise ValueError("tree total_bytes does not match files")
        if self.tree_sha256 != tree_sha256_from_inventory(self.files):
            raise ValueError("tree_sha256 does not match the canonical file inventory")
        return self


def is_sha256_hex(value: object) -> bool:
    """Whether value is an unprefixed lowercase ASCII SHA-256 hex string."""
    return not (
        not isinstance(value, str)
        or len(value) != 64
        or any(c not in "0123456789abcdef" for c in value)
    )


def canonical_json_bytes(value: object, *, exact_numbers: bool = False) -> bytes:
    """Return the one canonical JSON document form every stored digest is over.

    ``exact_numbers`` opts bounded proposal values into lossless Decimal output;
    the default path and its historical bytes are unchanged.

    Sorted keys, ``(",", ":")`` separators, literal non-ASCII, no non-finite
    numbers, and exactly one trailing newline.  A pydantic model is dumped in
    JSON mode first.  Every recorded ``*_sha256`` in this repository is a digest
    of these bytes, so the shape is pinned by assertion in ``tests/test_artifacts.py``
    rather than left to inspection.
    """

    document = value.model_dump(mode="json") if isinstance(value, BaseModel) else value
    if exact_numbers:

        def encode(item):
            if isinstance(item, Decimal):
                if not item.is_finite():
                    raise ValueError("nonfinite exact JSON number")
                return str(item)
            if isinstance(item, dict):
                if any(not isinstance(key, str) for key in item):
                    raise ValueError("exact JSON objects require string keys")
                return "{" + ",".join(encode(k) + ":" + encode(item[k]) for k in sorted(item)) + "}"
            if isinstance(item, list):
                return "[" + ",".join(map(encode, item)) + "]"
            return json.dumps(item, ensure_ascii=False, allow_nan=False, separators=(",", ":"))

        return (encode(document) + "\n").encode()
    return (
        json.dumps(
            document,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        )
        + "\n"
    ).encode("utf-8")


def canonical_json_text(value: object) -> str:
    """Return the canonical JSON form as text, without the trailing newline.

    A thin adapter over :func:`canonical_json_bytes` for the callers that
    compare or embed canonical fragments rather than persist whole documents.
    """

    return canonical_json_bytes(value).decode("utf-8").removesuffix("\n")


def sha256_hex(data: bytes) -> str:
    """Return the lowercase hex content digest of ``data``."""

    return hashlib.sha256(data).hexdigest()


def _safe_fs_coordinate(value: str) -> str:
    """Render a filesystem string without leaving surrogate code points."""

    return value.encode("utf-8", "backslashreplace").decode("utf-8")


def tree_sha256_from_inventory(files: Sequence[BaseModel]) -> str:
    """Return the tree identity of a *declared* file inventory.

    Hashes the canonical JSON of the given entries.  This is not the same
    operation as :func:`tree_sha256_from_directory`, which walks a real root;
    the two carried the same private name in different modules before 04-18.
    """

    return sha256_hex(
        canonical_json_bytes({"files": [entry.model_dump(mode="json") for entry in files]})
    )


def read_regular_file_bytes(
    root: str | Path,
    relative: str,
    *,
    label: str,
    max_bytes: int | None = None,
    expected_root: tuple[int, int] | None = None,
) -> bytes:
    """Read one regular leaf from an explicitly trusted directory anchor.

    Every intermediate component and the leaf are opened descriptor-relative
    with ``O_NOFOLLOW``.  The leaf's pre-open, open, final, and post-read
    identities must agree, and :func:`read_regular_bounded` rebinds the lexical
    root before returning.  ``max_bytes=None`` preserves the historical
    whole-file API while still using the stable descriptor reader.
    """

    cap = (1 << 63) - 1 if max_bytes is None else max_bytes
    try:
        data, _snapshot = read_regular_bounded(
            root,
            relative,
            max_bytes=cap,
            expected_root=expected_root,
        )
        return data
    except ArtifactError as error:
        raise ArtifactError(f"{label} could not be read safely: {error}") from error


def tree_sha256_from_directory(
    root: Path,
    *,
    label: str,
    max_entries: int,
    max_bytes: int,
    relative: str | None = None,
) -> str:
    """Return the tree identity of a real directory root, by walking descriptors.

    Files, directories, and symlink targets are all bound into the digest under
    distinct tags, so a type change at one path is a digest change.  This is the
    directory-walking tree identity; :func:`tree_sha256_from_inventory` hashes a
    declared inventory instead and the two are deliberately separate names.

    When ``relative`` is supplied, ``root`` is the trusted anchor and every
    component of that relative directory is opened with ``O_NOFOLLOW``.  The
    selected directory identity is re-opened after the snapshot so an ancestor
    swap cannot silently redirect the retained lexical coordinate.
    """

    parts = _safe_parts(relative, field=f"{label} locator") if relative is not None else ()
    digest = hashlib.sha256()
    entries = 0
    total_bytes = 0
    anchor_fd = _open_root(root)
    selected_fd = -1
    selected_identity: tuple[int, int, int, int, int] | None = None

    def directory_identity(info: os.stat_result) -> tuple[int, int, int, int, int]:
        return (
            info.st_dev,
            info.st_ino,
            info.st_mode,
            info.st_size,
            info.st_mtime_ns,
        )

    def visit(directory_fd: int, prefix: tuple[str, ...]) -> None:
        nonlocal entries, total_bytes
        before_enumeration = os.fstat(directory_fd)
        try:
            names = sorted(os.listdir(directory_fd), key=os.fsencode)
        except OSError as error:
            raise ArtifactError(
                f"{label} tree could not be read at "
                f"{_safe_fs_coordinate('/'.join(prefix) or '.')}: {error}"
            ) from error
        after_enumeration = os.fstat(directory_fd)
        if directory_identity(after_enumeration) != directory_identity(before_enumeration):
            raise ArtifactError(
                f"{label} directory changed while enumerated: "
                f"{_safe_fs_coordinate('/'.join(prefix) or '.')}"
            )
        for name in names:
            entries += 1
            if entries > max_entries:
                raise ArtifactError(f"{label} exceeds {max_entries} tree entries")
            relparts = (*prefix, name)
            relpath_text = PurePosixPath(*relparts).as_posix()
            relpath_display = _safe_fs_coordinate(relpath_text)
            relpath = b"/".join(os.fsencode(part) for part in relparts)
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as error:
                raise ArtifactError(
                    f"{label} entry could not be inspected: {relpath_display}: {error}"
                ) from error
            if stat.S_ISLNK(info.st_mode):
                try:
                    target = os.fsencode(os.readlink(name, dir_fd=directory_fd))
                    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                except OSError as error:
                    raise ArtifactError(
                        f"{label} symlink could not be read: {relpath_display}: {error}"
                    ) from error
                if (current.st_dev, current.st_ino, current.st_mode) != (
                    info.st_dev,
                    info.st_ino,
                    info.st_mode,
                ):
                    raise ArtifactError(
                        f"{label} symlink changed while read: {relpath_display}"
                    )
                digest.update(b"L\0" + relpath + b"\0" + target)
            elif stat.S_ISDIR(info.st_mode):
                digest.update(b"D\0" + relpath + b"\0")
                flags = (
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                )
                child_fd = -1
                try:
                    child_fd = os.open(name, flags, dir_fd=directory_fd)
                    opened = os.fstat(child_fd)
                    if (opened.st_dev, opened.st_ino, opened.st_mode) != (
                        info.st_dev,
                        info.st_ino,
                        info.st_mode,
                    ):
                        raise ArtifactError(
                            f"{label} directory changed before opening: {relpath_display}"
                        )
                    visit(child_fd, relparts)
                    final = os.fstat(child_fd)
                    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                    if directory_identity(final) != directory_identity(opened) or (
                        directory_identity(current) != directory_identity(opened)
                    ):
                        raise ArtifactError(
                            f"{label} directory changed while read: {relpath_display}"
                        )
                except OSError as error:
                    raise ArtifactError(
                        f"{label} directory could not be opened safely: "
                        f"{relpath_display}: {error}"
                    ) from error
                finally:
                    if child_fd >= 0:
                        os.close(child_fd)
            elif stat.S_ISREG(info.st_mode):
                total_bytes += info.st_size
                if total_bytes > max_bytes:
                    raise ArtifactError(f"{label} exceeds the {max_bytes}-byte snapshot cap")
                digest.update(b"F\0" + relpath + b"\0")
                file_fd = -1
                try:
                    file_fd = os.open(
                        name,
                        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                        dir_fd=directory_fd,
                    )
                    data, snapshot = _read_fd(
                        file_fd,
                        relative=relpath_display,
                        before=info,
                        max_bytes=max_bytes,
                    )
                    current = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
                    if (current.st_dev, current.st_ino) != (snapshot.device, snapshot.inode):
                        raise ArtifactError(
                            f"{label} file changed after read: {relpath_display}"
                        )
                except OSError as error:
                    raise ArtifactError(
                        f"{label} file could not be opened safely: {relpath_display}: {error}"
                    ) from error
                finally:
                    if file_fd >= 0:
                        os.close(file_fd)
                digest.update(data)
            else:
                raise ArtifactError(
                    f"{label} contains unsupported special entry {relpath_display}"
                )
        after_visit = os.fstat(directory_fd)
        if directory_identity(after_visit) != directory_identity(before_enumeration):
            raise ArtifactError(
                f"{label} directory changed while read: "
                f"{_safe_fs_coordinate('/'.join(prefix) or '.')}"
            )

    try:
        selected_fd = _descend(anchor_fd, parts)
        selected = os.fstat(selected_fd)
        selected_identity = directory_identity(selected)
        visit(selected_fd, ())
        anchor_identity = os.fstat(anchor_fd)
        rebound_anchor_fd = _open_root(
            root,
            expected_identity=(anchor_identity.st_dev, anchor_identity.st_ino),
        )
        reopened_fd = -1
        try:
            reopened_fd = _descend(rebound_anchor_fd, parts)
            reopened = os.fstat(reopened_fd)
            if directory_identity(reopened) != selected_identity:
                raise ArtifactError(f"{label} root changed while its tree was read")
        finally:
            if reopened_fd >= 0:
                os.close(reopened_fd)
            os.close(rebound_anchor_fd)
        return digest.hexdigest()
    finally:
        if selected_fd >= 0:
            os.close(selected_fd)
        os.close(anchor_fd)


def _safe_parts(relative: str, *, field: str = "artifact path") -> tuple[str, ...]:
    if not isinstance(relative, str) or not relative.strip():
        raise ArtifactError(f"{field} must be a nonempty relative path")
    if "\x00" in relative:
        raise ArtifactError(f"{field} contains a NUL byte")
    if relative != relative.strip() or "\\" in relative:
        raise ArtifactError(f"{field} must use normalized POSIX spelling")
    posix = PurePosixPath(relative)
    windows = PureWindowsPath(relative)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(posix.root)
        or bool(windows.root)
        or bool(windows.drive)
        or relative.startswith(("/", "\\"))
    ):
        raise ArtifactError(f"{field} must be relative, not {relative!r}")
    if any(part in {"", ".", ".."} for part in posix.parts) or ".." in windows.parts:
        raise ArtifactError(f"{field} contains a parent or non-normal component")
    if not posix.parts:
        raise ArtifactError(f"{field} has no path components")
    if relative != PurePosixPath(*posix.parts).as_posix():
        raise ArtifactError(f"{field} must use normalized POSIX spelling")
    return posix.parts


def _open_root(
    root: Path,
    *,
    expected_identity: tuple[int, int] | None = None,
) -> int:
    try:
        info = root.lstat()
    except OSError as error:
        raise ArtifactError(f"artifact root {root} could not be inspected: {error}") from error
    if stat.S_ISLNK(info.st_mode):
        raise ArtifactError(f"artifact root {root} is a symlink")
    if not stat.S_ISDIR(info.st_mode):
        raise ArtifactError(f"artifact root {root} is not a directory")
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = -1
    try:
        descriptor = os.open(root, flags)
        opened = os.fstat(descriptor)
    except OSError as error:
        if descriptor >= 0:
            os.close(descriptor)
        raise ArtifactError(f"artifact root {root} could not be opened safely: {error}") from error
    if (
        not stat.S_ISDIR(opened.st_mode)
        or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)
    ):
        os.close(descriptor)
        raise ArtifactError(f"artifact root {root} changed before it opened")
    if expected_identity is not None and (
        opened.st_dev,
        opened.st_ino,
    ) != expected_identity:
        os.close(descriptor)
        raise ArtifactError(f"artifact root {root} changed from its expected identity")
    return descriptor


def _descend(directory_fd: int, parts: tuple[str, ...]) -> int:
    current = os.dup(directory_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in parts:
            try:
                info = os.stat(part, dir_fd=current, follow_symlinks=False)
            except OSError as error:
                raise ArtifactError(
                    f"artifact directory component {part!r} could not be inspected: {error}"
                ) from error
            if stat.S_ISLNK(info.st_mode):
                raise ArtifactError(f"artifact directory component {part!r} is a symlink")
            if not stat.S_ISDIR(info.st_mode):
                raise ArtifactError(f"artifact directory component {part!r} is not a directory")
            next_fd = -1
            try:
                next_fd = os.open(part, flags, dir_fd=current)
                opened = os.fstat(next_fd)
            except OSError as error:
                if next_fd >= 0:
                    os.close(next_fd)
                raise ArtifactError(
                    f"artifact directory component {part!r} could not be opened safely: {error}"
                ) from error
            if (
                not stat.S_ISDIR(opened.st_mode)
                or (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino)
            ):
                os.close(next_fd)
                raise ArtifactError(
                    f"artifact directory component {part!r} changed before it opened"
                )
            os.close(current)
            current = next_fd
    except BaseException:
        os.close(current)
        raise
    return current


def _read_fd(
    descriptor: int,
    *,
    relative: str,
    before: os.stat_result,
    max_bytes: int,
) -> tuple[bytes, LeafSnapshot]:
    opened = os.fstat(descriptor)
    if not stat.S_ISREG(opened.st_mode):
        raise ArtifactError(f"artifact {relative} is not a regular file")
    if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
        raise ArtifactIdentityError(f"artifact {relative} changed identity before it opened")
    if opened.st_size > max_bytes:
        raise ArtifactError(
            f"artifact {relative} is {opened.st_size} bytes, over the {max_bytes}-byte cap"
        )
    chunks = bytearray()
    while chunk := os.read(descriptor, min(64 * 1024, max_bytes + 1 - len(chunks))):
        chunks.extend(chunk)
        if len(chunks) > max_bytes:
            raise ArtifactError(f"artifact {relative} grew over the {max_bytes}-byte cap")
    final = os.fstat(descriptor)
    stable_fields = (
        "st_dev",
        "st_ino",
        "st_mode",
        "st_size",
        "st_mtime_ns",
    )
    if any(getattr(opened, field) != getattr(final, field) for field in stable_fields):
        raise ArtifactIdentityError(f"artifact {relative} changed while it was read")
    data = bytes(chunks)
    if len(data) != opened.st_size:
        raise ArtifactIdentityError(f"artifact {relative} changed size while it was read")
    return data, LeafSnapshot(
        path=relative,
        size_bytes=len(data),
        sha256=sha256_hex(data),
        mode=stat.S_IMODE(opened.st_mode),
        device=opened.st_dev,
        inode=opened.st_ino,
        mtime_ns=opened.st_mtime_ns,
    )


def _read_regular_bounded_fd(
    root_fd: int,
    relative: str,
    *,
    max_bytes: int,
    expected: LeafSnapshot | None = None,
    expected_stat: os.stat_result | None = None,
) -> tuple[bytes, LeafSnapshot]:
    """Read one leaf beneath a retained root directory descriptor."""

    if max_bytes < 0:
        raise ValueError("max_bytes must be nonnegative")
    parts = _safe_parts(relative)
    normalized = PurePosixPath(*parts).as_posix()
    parent_fd = -1
    descriptor = -1
    try:
        parent_fd = _descend(root_fd, parts[:-1])
        try:
            before = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        except OSError as error:
            raise ArtifactError(f"artifact {normalized} could not be inspected: {error}") from error
        if stat.S_ISLNK(before.st_mode):
            raise ArtifactError(f"artifact {normalized} is a symlink")
        if not stat.S_ISREG(before.st_mode):
            raise ArtifactError(f"artifact {normalized} is not a regular file")
        if expected_stat is not None:
            stable_fields = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_size",
                "st_mtime_ns",
            )
            if any(
                getattr(before, field) != getattr(expected_stat, field)
                for field in stable_fields
            ):
                raise ArtifactIdentityError(
                    f"artifact {normalized} changed from its expected stat identity"
                )
        try:
            descriptor = os.open(
                parts[-1],
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=parent_fd,
            )
        except OSError as error:
            raise ArtifactError(f"artifact {normalized} could not be opened safely: {error}") from error
        data, snapshot = _read_fd(
            descriptor,
            relative=normalized,
            before=before,
            max_bytes=max_bytes,
        )
        current_parent_fd = _descend(root_fd, parts[:-1])
        try:
            current = os.stat(parts[-1], dir_fd=current_parent_fd, follow_symlinks=False)
        except OSError as error:
            raise ArtifactError(
                f"artifact {normalized} changed after it was read: {error}"
            ) from error
        finally:
            os.close(current_parent_fd)
        if (
            current.st_dev,
            current.st_ino,
            stat.S_IMODE(current.st_mode),
            current.st_size,
            current.st_mtime_ns,
        ) != (
            snapshot.device,
            snapshot.inode,
            snapshot.mode,
            snapshot.size_bytes,
            snapshot.mtime_ns,
        ):
            raise ArtifactIdentityError(f"artifact {normalized} changed after it was read")
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if parent_fd >= 0:
            os.close(parent_fd)
    if expected is not None and snapshot != expected:
        raise ArtifactIdentityError(f"artifact {normalized} changed from its expected identity")
    return data, snapshot


def read_regular_bounded_at(
    root_fd: int,
    relative: str,
    *,
    max_bytes: int,
    expected: LeafSnapshot | None = None,
    expected_stat: os.stat_result | None = None,
) -> tuple[bytes, LeafSnapshot]:
    """Read one leaf beneath a caller-owned retained root descriptor.

    The descriptor remains owned by the caller.  This is the shared primitive
    for multi-assertion checks that must use one root identity throughout the
    complete operation rather than reopen the lexical root per assertion.
    """

    return _read_regular_bounded_fd(
        root_fd,
        relative,
        max_bytes=max_bytes,
        expected=expected,
        expected_stat=expected_stat,
    )


def stat_leaf_at(root_fd: int, relative: str) -> os.stat_result:
    """No-follow stat one leaf beneath a caller-owned root descriptor.

    Every ancestor is descriptor-opened with ``O_NOFOLLOW``. The leaf itself is
    not opened, so callers can distinguish regular files, directories and
    symlinks while aggregate budgets are still in their stat-only phase.
    """

    parts = _safe_parts(relative)
    normalized = PurePosixPath(*parts).as_posix()
    parent_fd = -1
    try:
        parent_fd = _descend(root_fd, parts[:-1])
        try:
            return os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        except OSError as error:
            raise ArtifactError(f"artifact {normalized} could not be inspected: {error}") from error
    except ArtifactError:
        raise
    except OSError as error:
        raise ArtifactError(
            f"artifact {normalized} could not be inspected safely: {error}"
        ) from error
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)


#: The stat fields a leaf's identity is compared on. A symlink has no
#: descriptor to hold open across a read, so its identity is established by
#: re-statting after the read and requiring these to be unchanged.
_LEAF_IDENTITY_FIELDS = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns")


def readlink_at(
    root_fd: int, relative: str, *, expected_stat: os.stat_result | None = None
) -> str:
    """No-follow read of one symlink's VERBATIM target, re-statted after reading.

    A symlink cannot be held open, so identity is established by statting,
    reading and re-statting through ONE parent descriptor: two descents can
    each succeed against a different directory, and would compare two leaves
    and call them one. The target is returned exactly as stored -- nothing
    stripped, resolved or normalized -- and a non-UTF-8 target is refused
    rather than mangled into one that compares equal to a different link.
    """

    parts = _safe_parts(relative)
    normalized = PurePosixPath(*parts).as_posix()
    parent_fd = -1
    try:
        parent_fd = _descend(root_fd, parts[:-1])
        try:
            before = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
            target = os.readlink(parts[-1], dir_fd=parent_fd)
            after = os.stat(parts[-1], dir_fd=parent_fd, follow_symlinks=False)
        except OSError as error:
            raise ArtifactError(f"artifact {normalized} could not be read: {error}") from error
        if not stat.S_ISLNK(before.st_mode):
            raise ArtifactError(f"artifact {normalized} is not a symlink")
        for observation in (expected_stat, after):
            if observation is not None and any(
                getattr(before, field) != getattr(observation, field)
                for field in _LEAF_IDENTITY_FIELDS
            ):
                raise ArtifactIdentityError(
                    f"artifact {normalized} changed while its target was read"
                )
        try:
            target.encode("utf-8")
        except UnicodeEncodeError:
            raise ArtifactError(f"artifact {normalized} has a non-UTF-8 target") from None
        return target
    except ArtifactError:
        raise
    except OSError as error:
        raise ArtifactError(f"artifact {normalized} could not be read safely: {error}") from error
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)


def _bounded(value: str, limit: int = 96) -> str:
    """A refusal quotes caller input, so the quote itself has to be bounded."""

    return value if len(value) <= limit else f"{value[:limit]}..."


def snapshot_tracked_roster(
    root: Path,
    roster: Sequence[str],
    *,
    label: str,
    relative: str | None = None,
    max_entries: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
) -> tuple[tuple[TrackedTreeEntry, ...], str]:
    """Observe exactly the leaves a caller listed, and return their identity.

    THERE IS NO DIRECTORY WALK and ``gnd`` never derives the roster: it does
    not consult Git or any mutable external state, and has no opinion about a
    path the caller did not list (r2 R5). The caps bound the algorithm as well
    as the input. Returns the observed entries and the digest, SHA-256 over
    ``canonical_json_bytes({"entries": [...]})``; an empty roster is legal.
    """

    if max_entries < 0 or max_file_bytes < 0 or max_total_bytes < 0:
        raise ArtifactError(f"{label} snapshot caps must be non-negative")
    if len(roster) > max_entries:
        raise ArtifactError(
            f"{label} roster lists {len(roster)} paths, over the {max_entries}-path cap"
        )
    # Sortedness is REQUIRED, not imposed: reordering would make two different
    # claims hash alike.
    if any(earlier >= later for earlier, later in pairwise(roster)):
        raise ArtifactError(f"{label} roster must be sorted and free of duplicates")
    entries: list[TrackedTreeEntry] = []
    total = 0
    root_fd = _open_root(Path(root))
    selected_fd = -1
    try:
        selected_fd = _descend(root_fd, _safe_parts(relative)) if relative else os.dup(root_fd)
        for path in roster:
            # Caller paths reach the readers' messages verbatim; bound the
            # quote, keeping the refusal's class.
            try:
                observed = stat_leaf_at(selected_fd, path)
                if stat.S_ISLNK(observed.st_mode):
                    entries.append(
                        TrackedSymlinkEntry(
                            path=path,
                            target=readlink_at(selected_fd, path, expected_stat=observed),
                        )
                    )
                    continue
                if not stat.S_ISREG(observed.st_mode):
                    raise ArtifactError(
                        f"{label} roster path {_bounded(path)!r} "
                        "is neither a regular file nor a symlink"
                    )
                total += observed.st_size
                if total > max_total_bytes:
                    raise ArtifactError(
                        f"{label} roster exceeds the {max_total_bytes}-byte aggregate cap"
                    )
                _data, snapshot = read_regular_bounded_at(
                    selected_fd, path, max_bytes=max_file_bytes, expected_stat=observed
                )
                entries.append(
                    TrackedRegularEntry(
                        path=path,
                        size_bytes=snapshot.size_bytes,
                        sha256=snapshot.sha256,
                        executable=bool(snapshot.mode & 0o111),
                    )
                )
            except ArtifactError as error:
                raise type(error)(_bounded(str(error), 200)) from error
    finally:
        if selected_fd >= 0:
            os.close(selected_fd)
        os.close(root_fd)
    document = {"entries": [entry.model_dump(mode="json") for entry in entries]}
    return tuple(entries), sha256_hex(canonical_json_bytes(document))


def read_regular_bounded(
    root: str | Path,
    relative: str,
    *,
    max_bytes: int,
    expected: LeafSnapshot | None = None,
    expected_root: tuple[int, int] | None = None,
) -> tuple[bytes, LeafSnapshot]:
    """Read one contained regular leaf through no-follow descriptors."""

    root_path = Path(root)
    root_fd = _open_root(root_path, expected_identity=expected_root)
    try:
        data, snapshot = _read_regular_bounded_fd(
            root_fd,
            relative,
            max_bytes=max_bytes,
            expected=expected,
        )
        root_current = root_path.lstat()
        root_opened = os.fstat(root_fd)
        if (root_current.st_dev, root_current.st_ino) != (
            root_opened.st_dev,
            root_opened.st_ino,
        ):
            raise ArtifactError(f"artifact root {root} changed while it was read")
        return data, snapshot
    finally:
        os.close(root_fd)


def _inventory_tree_fd(
    root_fd: int,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_depth: int = DEFAULT_MAX_DEPTH,
) -> TreeInventory:
    """Inventory a directory already bound to an open descriptor."""

    root_before = os.fstat(root_fd)
    files: list[TreeFile] = []
    total = 0

    def walk(directory_fd: int, prefix: tuple[str, ...]) -> None:
        nonlocal total
        try:
            names = sorted(os.listdir(directory_fd))
        except OSError as error:
            raise ArtifactError(
                f"artifact directory {'/'.join(prefix) or '.'} changed: {error}"
            ) from error
        for name in names:
            relative_parts = (*prefix, name)
            relative = PurePosixPath(*relative_parts).as_posix()
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as error:
                raise ArtifactError(f"artifact {relative} could not be inspected: {error}") from error
            if stat.S_ISLNK(info.st_mode):
                raise ArtifactError(f"artifact {relative} is a symlink")
            if stat.S_ISDIR(info.st_mode):
                if len(relative_parts) > max_depth:
                    raise ArtifactError(
                        f"artifact directory {relative} exceeds the depth cap {max_depth}"
                    )
                flags = (
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                )
                child_fd = -1
                try:
                    child_fd = os.open(name, flags, dir_fd=directory_fd)
                    child_before = os.fstat(child_fd)
                except OSError as error:
                    if child_fd >= 0:
                        os.close(child_fd)
                    raise ArtifactError(
                        f"artifact directory {relative} could not be opened safely: {error}"
                    ) from error
                if (
                    not stat.S_ISDIR(child_before.st_mode)
                    or (child_before.st_dev, child_before.st_ino)
                    != (info.st_dev, info.st_ino)
                ):
                    os.close(child_fd)
                    raise ArtifactError(
                        f"artifact directory {relative} changed before it opened"
                    )
                try:
                    walk(child_fd, relative_parts)
                    child_after = os.fstat(child_fd)
                    if (
                        child_after.st_dev,
                        child_after.st_ino,
                        child_after.st_size,
                        child_after.st_mtime_ns,
                    ) != (
                        child_before.st_dev,
                        child_before.st_ino,
                        child_before.st_size,
                        child_before.st_mtime_ns,
                    ):
                        raise ArtifactError(
                            f"artifact directory {relative} changed while it was inventoried"
                        )
                finally:
                    os.close(child_fd)
                continue
            if not stat.S_ISREG(info.st_mode):
                raise ArtifactError(f"artifact {relative} is not a regular file")
            if len(files) >= max_files:
                raise ArtifactError(f"artifact tree exceeds the {max_files}-file cap")
            if info.st_size > max_file_bytes:
                raise ArtifactError(
                    f"artifact {relative} exceeds the {max_file_bytes}-byte per-file cap"
                )
            descriptor = os.open(
                name,
                os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
                dir_fd=directory_fd,
            )
            try:
                data, snapshot = _read_fd(
                    descriptor,
                    relative=relative,
                    before=info,
                    max_bytes=max_file_bytes,
                )
            finally:
                os.close(descriptor)
            if total + len(data) > max_total_bytes:
                raise ArtifactError(
                    f"artifact tree exceeds the {max_total_bytes}-byte total cap"
                )
            total += len(data)
            files.append(
                TreeFile(
                    path=relative,
                    size_bytes=snapshot.size_bytes,
                    sha256=snapshot.sha256,
                    executable=bool(snapshot.mode & 0o111),
                )
            )

    walk(root_fd, ())
    root_after = os.fstat(root_fd)
    if (
        root_after.st_dev,
        root_after.st_ino,
        root_after.st_size,
        root_after.st_mtime_ns,
    ) != (
        root_before.st_dev,
        root_before.st_ino,
        root_before.st_size,
        root_before.st_mtime_ns,
    ):
        raise ArtifactError("artifact root changed while it was inventoried")
    files.sort(key=lambda entry: entry.path)
    return TreeInventory(
        files=tuple(files),
        file_count=len(files),
        total_bytes=total,
        tree_sha256=tree_sha256_from_inventory(files),
    )


def inventory_tree(
    root: str | Path,
    *,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    expected_root: tuple[int, int] | None = None,
) -> TreeInventory:
    """Inventory every regular leaf beneath ``root`` in stable POSIX order."""

    if min(max_files, max_file_bytes, max_total_bytes, max_depth) < 0:
        raise ValueError("artifact inventory bounds must be nonnegative")
    root_path = Path(root)
    root_fd = _open_root(root_path, expected_identity=expected_root)
    try:
        inventory = _inventory_tree_fd(
            root_fd,
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            max_depth=max_depth,
        )
        root_after = os.fstat(root_fd)
        root_current = root_path.lstat()
        if (root_current.st_dev, root_current.st_ino) != (
            root_after.st_dev,
            root_after.st_ino,
        ):
            raise ArtifactError("artifact root changed identity while it was inventoried")
        return inventory
    finally:
        os.close(root_fd)


def _write_new_file(
    path: Path,
    data: bytes,
    *,
    root: Path | None = None,
    mode: int = FILE_MODE,
    expected_root: tuple[int, int] | None = None,
) -> None:
    """Write and fsync one new regular leaf; used as an observable test seam."""

    publication_root = path.parent if root is None else root
    try:
        relative = path.absolute().relative_to(publication_root.absolute()).as_posix()
    except ValueError as error:
        raise ArtifactError(f"artifact leaf {path} escapes publication root") from error
    parts = _safe_parts(relative, field="artifact publication member")
    root_fd = _open_root(publication_root, expected_identity=expected_root)
    try:
        _write_new_file_at(root_fd, parts, data, mode=mode)
    finally:
        os.close(root_fd)


def _write_new_file_at(
    root_fd: int,
    parts: tuple[str, ...],
    data: bytes,
    *,
    mode: int = FILE_MODE,
) -> None:
    """Write one new leaf beneath an already-bound directory descriptor."""

    if not parts:
        raise ArtifactError("artifact publication member has no path components")
    parent_fd = _create_parent_at(root_fd, parts[:-1])
    descriptor = -1
    try:
        descriptor = os.open(
            parts[-1],
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            mode,
            dir_fd=parent_fd,
        )
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.fsync(parent_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        os.close(parent_fd)


def _leaf_at_fd(parent_fd: int, name: str, relative: str, cap: int) -> LeafSnapshot:
    try:
        before = os.stat(name, dir_fd=parent_fd, follow_symlinks=False)
    except OSError as error:
        raise ArtifactError(f"artifact {relative} could not be inspected: {error}") from error
    if stat.S_ISLNK(before.st_mode):
        raise ArtifactError(f"artifact {relative} is a symlink")
    descriptor = os.open(
        name,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0),
        dir_fd=parent_fd,
    )
    try:
        _, snapshot = _read_fd(
            descriptor,
            relative=relative,
            before=before,
            max_bytes=cap,
        )
        return snapshot
    finally:
        os.close(descriptor)


def _create_parent_at(root_fd: int, parts: tuple[str, ...]) -> int:
    """Create/open a real directory chain beneath one bound root descriptor."""

    current = os.dup(root_fd)
    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    try:
        for part in parts:
            with suppress(FileExistsError):
                os.mkdir(part, DIRECTORY_MODE, dir_fd=current)
                os.fsync(current)
            next_fd = -1
            try:
                info = os.stat(part, dir_fd=current, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                    raise ArtifactError(
                        f"artifact publication component {part!r} is not a real directory"
                    )
                next_fd = os.open(part, flags, dir_fd=current)
                opened = os.fstat(next_fd)
            except OSError as error:
                if next_fd >= 0:
                    os.close(next_fd)
                raise ArtifactError(
                    f"artifact publication component {part!r} could not be opened: {error}"
                ) from error
            if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                os.close(next_fd)
                raise ArtifactError(
                    f"artifact publication component {part!r} changed before it opened"
                )
            os.close(current)
            current = next_fd
    except BaseException:
        os.close(current)
        raise
    return current


def _create_parent(
    root: Path,
    parts: tuple[str, ...],
    *,
    expected_root: tuple[int, int] | None = None,
) -> int:
    if expected_root is None:
        root.mkdir(parents=True, exist_ok=True, mode=DIRECTORY_MODE)
    root_fd = _open_root(root, expected_identity=expected_root)
    try:
        return _create_parent_at(root_fd, parts)
    finally:
        os.close(root_fd)


def _mkdir_directory_once(parent_fd: int, name: str) -> None:
    """Claim one append-only directory name without a precheck race."""

    try:
        os.mkdir(name, DIRECTORY_MODE, dir_fd=parent_fd)
    except FileExistsError as error:
        raise ArtifactError(
            f"artifact publication collision: {name} already exists"
        ) from error


def _clear_directory_fd(directory_fd: int) -> None:
    """Remove unpublished members through their already-bound parent descriptor."""

    flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0)
    for name in os.listdir(directory_fd):
        info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
        if stat.S_ISDIR(info.st_mode):
            child_fd = os.open(name, flags, dir_fd=directory_fd)
            try:
                opened = os.fstat(child_fd)
                if (opened.st_dev, opened.st_ino) != (info.st_dev, info.st_ino):
                    raise ArtifactError(
                        f"unpublished artifact directory {name!r} changed before cleanup"
                    )
                _clear_directory_fd(child_fd)
            finally:
                os.close(child_fd)
            os.rmdir(name, dir_fd=directory_fd)
        else:
            os.unlink(name, dir_fd=directory_fd)


def _unlink_leaf_at(root_fd: int, parts: tuple[str, ...]) -> None:
    """Unlink and fsync one contained leaf beneath a bound directory."""

    parent_fd = _descend(root_fd, parts[:-1])
    try:
        os.unlink(parts[-1], dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        os.close(parent_fd)


def remove_regular_if_unchanged(
    root: str | Path,
    relative: str,
    *,
    expected: LeafSnapshot,
    expected_root: tuple[int, int] | None = None,
) -> None:
    """Remove one regular leaf only while it has the identity already read.

    The leaf is first renamed to a private sibling through its descriptor-bound
    parent.  Its bytes and filesystem identity are then compared with
    ``expected`` before the private name is unlinked.  A changed leaf is moved
    back instead of being destroyed.  This is the deletion-side counterpart to
    :func:`publish_leaf_atomic`'s expected-identity replacement.
    """

    parts = _safe_parts(relative, field="artifact removal path")
    normalized = PurePosixPath(*parts).as_posix()
    if expected.path != normalized:
        raise ArtifactError("expected leaf identity belongs to a different path")
    root_fd = _open_root(Path(root), expected_identity=expected_root)
    parent_fd = -1
    staging = f".gnd-staging-delete-{parts[-1]}-{secrets.token_hex(8)}"
    staged = False
    try:
        parent_fd = _descend(root_fd, parts[:-1])
        try:
            os.replace(
                parts[-1],
                staging,
                src_dir_fd=parent_fd,
                dst_dir_fd=parent_fd,
            )
            staged = True
            observed = _leaf_at_fd(
                parent_fd,
                staging,
                normalized,
                max(expected.size_bytes, 1),
            )
            if observed != expected:
                raise ArtifactError(
                    f"artifact {normalized} changed from its expected identity"
                )
            os.unlink(staging, dir_fd=parent_fd)
            staged = False
            os.fsync(parent_fd)
        except BaseException:
            if staged:
                os.replace(
                    staging,
                    parts[-1],
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                )
            raise
    except OSError as error:
        raise ArtifactError(f"artifact {normalized} could not be removed safely: {error}") from error
    finally:
        if parent_fd >= 0:
            os.close(parent_fd)
        os.close(root_fd)


def _exchange_paths_atomic(
    first_fd: int,
    first_name: str,
    second_fd: int,
    second_name: str,
) -> None:
    """Atomically exchange two existing directory entries without an absent gap."""

    library = ctypes.CDLL(None, use_errno=True)
    first = os.fsencode(first_name)
    second = os.fsencode(second_name)
    ctypes.set_errno(0)
    if hasattr(library, "renameatx_np"):
        function = library.renameatx_np
        function.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        function.restype = ctypes.c_int
        result = function(first_fd, first, second_fd, second, 0x00000002)
    elif hasattr(library, "renameat2"):
        function = library.renameat2
        function.argtypes = (
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_int,
            ctypes.c_char_p,
            ctypes.c_uint,
        )
        function.restype = ctypes.c_int
        result = function(first_fd, first, second_fd, second, 2)
    else:  # pragma: no cover - claimed POSIX targets expose one primitive above
        raise ArtifactError("atomic leaf exchange is unsupported on this platform")
    if result != 0:
        code = ctypes.get_errno()
        raise OSError(code, os.strerror(code), second_name)


def publish_leaf_atomic(
    root: str | Path,
    relative: str,
    data: bytes,
    *,
    expected: LeafSnapshot | None = None,
    expected_root: tuple[int, int] | None = None,
) -> LeafSnapshot:
    """Publish one complete leaf, requiring absence or an exact prior identity."""

    parts = _safe_parts(relative, field="artifact publication path")
    normalized = PurePosixPath(*parts).as_posix()
    if expected is not None and expected.path != normalized:
        raise ArtifactError("expected leaf identity belongs to a different path")
    parent_fd = _create_parent(
        Path(root),
        parts[:-1],
        expected_root=expected_root,
    )
    name = parts[-1]
    staging = f".gnd-staging-{name}-{secrets.token_hex(8)}"
    backup = f".gnd-staging-previous-{name}-{secrets.token_hex(8)}"
    descriptor = -1
    staging_contains_new = True
    try:
        descriptor = os.open(
            staging,
            os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0),
            FILE_MODE,
            dir_fd=parent_fd,
        )
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = -1
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        if expected is None:
            try:
                os.link(
                    staging,
                    name,
                    src_dir_fd=parent_fd,
                    dst_dir_fd=parent_fd,
                    follow_symlinks=False,
                )
            except FileExistsError as error:
                raise ArtifactError(
                    f"artifact publication collision: {normalized} already exists"
                ) from error
            os.unlink(staging, dir_fd=parent_fd)
        else:
            observed = _leaf_at_fd(
                parent_fd,
                name,
                normalized,
                max(len(data), expected.size_bytes),
            )
            if observed != expected:
                raise ArtifactError(f"artifact {normalized} changed from its expected identity")
            staged_new = _leaf_at_fd(parent_fd, staging, normalized, max(len(data), 1))
            try:
                _exchange_paths_atomic(parent_fd, staging, parent_fd, name)
                staging_contains_new = False
            except FileNotFoundError as error:
                raise ArtifactError(
                    f"artifact {normalized} disappeared from its expected identity"
                ) from error
            try:
                previous = _leaf_at_fd(
                    parent_fd,
                    staging,
                    normalized,
                    max(len(data), expected.size_bytes),
                )
            except BaseException:
                try:
                    live = _leaf_at_fd(
                        parent_fd,
                        name,
                        normalized,
                        max(len(data), 1),
                    )
                except ArtifactError:
                    live = None
                if live == staged_new:
                    _exchange_paths_atomic(parent_fd, staging, parent_fd, name)
                    staging_contains_new = True
                else:
                    os.rename(
                        staging,
                        backup,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                raise
            if previous != expected:
                live = _leaf_at_fd(parent_fd, name, normalized, max(len(data), 1))
                if live == staged_new:
                    _exchange_paths_atomic(parent_fd, staging, parent_fd, name)
                    staging_contains_new = True
                else:
                    os.rename(
                        staging,
                        backup,
                        src_dir_fd=parent_fd,
                        dst_dir_fd=parent_fd,
                    )
                raise ArtifactError(
                    f"artifact {normalized} changed during compare-and-swap publication"
                )
            os.unlink(staging, dir_fd=parent_fd)
        os.fsync(parent_fd)
    finally:
        if descriptor >= 0:
            os.close(descriptor)
        if staging_contains_new:
            with suppress(OSError):
                os.unlink(staging, dir_fd=parent_fd)
        os.close(parent_fd)
    published = read_regular_bounded(
        root,
        normalized,
        max_bytes=max(len(data), 1),
        expected_root=expected_root,
    )[1]
    if published.size_bytes != len(data) or published.sha256 != sha256_hex(data):
        raise ArtifactError(f"artifact {normalized} changed immediately after publication")
    return published


def publish_directory_once(
    root: str | Path,
    relative: str,
    files: dict[str, bytes],
    *,
    manifest_name: str,
    max_files: int = DEFAULT_MAX_FILES,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    expected_root: tuple[int, int] | None = None,
    executable_paths: set[str] | frozenset[str] | None = None,
    empty_directories: tuple[str, ...] = (),
    _published_identity: list[tuple[int, int]] | None = None,
) -> TreeInventory:
    """Publish one descriptor-bound directory, writing its manifest leaf last.

    ``empty_directories`` names direct children that must exist even though
    they hold no file, such as the snapshot of an attempt whose agent left no
    candidate bytes. They are created before any member is written.

    The destination name itself is the atomic no-replace claim.  Every member
    is then written through the claimed directory descriptor, so no pathname
    source can be exchanged between inventory and publication.  The manifest
    is the commit marker: a crash or failure before that final leaf is
    detectable as incomplete evidence.
    """

    destination_parts = _safe_parts(relative, field="artifact directory path")
    manifest_parts = _safe_parts(manifest_name, field="artifact manifest name")
    normalized_manifest = PurePosixPath(*manifest_parts).as_posix()
    if normalized_manifest not in files:
        raise ArtifactError(f"manifest {normalized_manifest!r} is absent from publication")
    if len(files) > max_files:
        raise ArtifactError(f"artifact publication exceeds the {max_files}-file cap")
    total = 0
    normalized_files: dict[str, bytes] = {}
    for relative_file, data in files.items():
        parts = _safe_parts(relative_file, field="artifact directory member")
        normalized = PurePosixPath(*parts).as_posix()
        if len(parts) - 1 > max_depth:
            raise ArtifactError(f"artifact member {normalized} exceeds the depth cap {max_depth}")
        if len(data) > max_file_bytes:
            raise ArtifactError(
                f"artifact member {normalized} exceeds the {max_file_bytes}-byte per-file cap"
            )
        total += len(data)
        if total > max_total_bytes:
            raise ArtifactError(
                f"artifact publication exceeds the {max_total_bytes}-byte total cap"
            )
        if normalized in normalized_files:
            raise ArtifactError(
                f"artifact directory members collide at normalized path {normalized!r}"
            )
        normalized_files[normalized] = data
    member_paths = set(normalized_files)
    for member in member_paths:
        parents = PurePosixPath(member).parents
        if any(parent.as_posix() in member_paths for parent in parents if parent.as_posix() != "."):
            raise ArtifactError(f"artifact member {member} collides with a file parent")

    empty_names: list[str] = []
    for name in empty_directories:
        name_parts = _safe_parts(name, field="artifact empty directory")
        if len(name_parts) != 1:
            raise ArtifactError("artifact empty directories must be direct children")
        if name in empty_names or any(
            member == name or member.startswith(name + "/") for member in member_paths
        ):
            raise ArtifactError(f"artifact empty directory {name!r} collides with a member")
        empty_names.append(name)

    normalized_executable: set[str] = set()
    for executable in executable_paths or ():
        executable_parts = _safe_parts(
            executable,
            field="artifact executable member",
        )
        normalized = PurePosixPath(*executable_parts).as_posix()
        if normalized in normalized_executable:
            raise ArtifactError(
                f"artifact executable members collide at normalized path {normalized!r}"
            )
        normalized_executable.add(normalized)
    unknown_executable = normalized_executable - member_paths
    if unknown_executable:
        raise ArtifactError(
            "artifact executable members are absent from publication: "
            + ", ".join(sorted(unknown_executable))
        )
    expected_files = tuple(
        TreeFile(
            path=name,
            size_bytes=len(normalized_files[name]),
            sha256=sha256_hex(normalized_files[name]),
            executable=name in normalized_executable,
        )
        for name in sorted(normalized_files)
    )
    expected_inventory = TreeInventory(
        files=expected_files,
        file_count=len(expected_files),
        total_bytes=sum(entry.size_bytes for entry in expected_files),
        tree_sha256=tree_sha256_from_inventory(expected_files),
    )

    root_path = Path(root)
    parent_fd = _create_parent(
        root_path,
        destination_parts[:-1],
        expected_root=expected_root,
    )
    destination_name = destination_parts[-1]
    destination_fd = -1
    destination_identity: tuple[int, int] | None = None
    manifest_written = False
    try:
        _mkdir_directory_once(parent_fd, destination_name)
        destination_info = os.stat(
            destination_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        destination_identity = (destination_info.st_dev, destination_info.st_ino)
        destination_fd = os.open(
            destination_name,
            os.O_RDONLY | getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0),
            dir_fd=parent_fd,
        )
        destination_opened = os.fstat(destination_fd)
        if (
            not stat.S_ISDIR(destination_opened.st_mode)
            or (destination_opened.st_dev, destination_opened.st_ino) != destination_identity
        ):
            raise ArtifactError("artifact destination changed before it opened")
        for name in empty_names:
            _mkdir_directory_once(destination_fd, name)
        order = sorted(name for name in normalized_files if name != normalized_manifest)
        for name in order:
            _write_new_file_at(
                destination_fd,
                PurePosixPath(name).parts,
                normalized_files[name],
                mode=0o755 if name in normalized_executable else FILE_MODE,
            )
        current = os.stat(
            destination_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        if (current.st_dev, current.st_ino) != destination_identity:
            raise ArtifactError("artifact destination changed before manifest publication")
        _write_new_file_at(
            destination_fd,
            manifest_parts,
            normalized_files[normalized_manifest],
            mode=(0o755 if normalized_manifest in normalized_executable else FILE_MODE),
        )
        manifest_written = True
        os.fsync(destination_fd)
        inventory = _inventory_tree_fd(
            destination_fd,
            max_files=max_files,
            max_file_bytes=max_file_bytes,
            max_total_bytes=max_total_bytes,
            max_depth=max_depth,
        )
        if inventory != expected_inventory:
            raise ArtifactError("published artifact tree differs from the requested complete tree")
        published = os.stat(
            destination_name,
            dir_fd=parent_fd,
            follow_symlinks=False,
        )
        if (published.st_dev, published.st_ino) != destination_identity:
            raise ArtifactError("published artifact directory changed identity")
        os.fsync(parent_fd)
        if _published_identity is not None:
            _published_identity.append(destination_identity)
        return inventory
    except BaseException:
        if destination_fd >= 0 and manifest_written:
            try:
                _unlink_leaf_at(destination_fd, manifest_parts)
            except (OSError, ArtifactError):
                pass
            else:
                manifest_written = False
        if destination_fd >= 0 and not manifest_written:
            with suppress(OSError, ArtifactError):
                _clear_directory_fd(destination_fd)
            try:
                current = os.stat(
                    destination_name,
                    dir_fd=parent_fd,
                    follow_symlinks=False,
                )
            except OSError:
                pass
            else:
                if (current.st_dev, current.st_ino) == destination_identity:
                    with suppress(OSError):
                        os.rmdir(destination_name, dir_fd=parent_fd)
                        os.fsync(parent_fd)
        raise
    finally:
        if destination_fd >= 0:
            os.close(destination_fd)
        os.close(parent_fd)


def canonical_report_text(payload: Mapping[str, Any]) -> str:
    """The payload as canonical JSON: sorted keys, no NaN, stable separators.

    ``sort_keys`` fixes every object's key order and every list is pre-sorted by
    the builder, so two runs over one unchanged project are byte-identical.
    """
    return json.dumps(
        payload, indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False
    )


def reject_json_constant(token: str) -> None:
    raise ValueError(f"non-finite JSON number {token!r} is forbidden")


def reject_json_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    document: dict[str, Any] = {}
    for key, value in pairs:
        if key in document:
            raise ValueError(f"duplicate JSON key {key!r}")
        document[key] = value
    return document


def reject_json_duplicate_pairs_result(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key {key!r}")
        result[key] = value
    return result
