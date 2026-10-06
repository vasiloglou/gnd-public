"""Public filesystem seams; variants retain predecessor behavior."""
from __future__ import annotations

import ctypes
import errno
import hashlib
import os
import stat
import sys
import tempfile
from contextlib import suppress
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Literal

from pydantic import BaseModel, ConfigDict

from gnd.artifacts import (
    read_regular_file_bytes as read_regular_file_bytes,  # noqa: PLC0414 -- compatibility export
)

FILE_MODE = 0o644


class InstallError(Exception):
    """Base for every failure this module raises."""


class InstallPathError(InstallError):
    """A relative path would resolve outside its target root, or is not relative.

    This is the phase's live security control (T-01.2-05, ASVS V5). The concrete
    attack: a hostile or corrupted ``.gnd-install.json`` names ``../../../.ssh/
    id_rsa`` and a later ``gnd uninstall`` deletes it. Every write and every
    delete in this phase — including the lifecycle plan's uninstall, which reads
    its paths back out of a JSON file sitting in a user-writable directory — goes
    through :func:`safe_destination` first.
    """


def _reject_unsafe_relpath(relpath: str, *, source: str) -> PurePosixPath:
    """String-level half of the guard: reject anything that is not a plain
    relative path, naming the offender so a corrupted manifest is diagnosable.

    Split out from :func:`safe_destination` because it touches no filesystem.
    :func:`plan` runs it over untrusted manifest input — that is *validation of a
    document*, not a symlink verdict, and keeping the two apart is what lets
    :func:`plan` classify a symlink-mode install without refusing every path in
    it (see :func:`plan`).

    Both POSIX and Windows interpretations are checked. ``..\\escape`` has a
    single POSIX component and would sail through a POSIX-only check while being
    a traversal on the platform D-24 leaves unclaimed but does not forbid.
    """
    if not isinstance(relpath, str) or not relpath.strip():
        raise InstallPathError(f"{source}: the relative path is empty or blank ('{relpath}')")
    if "\x00" in relpath:
        raise InstallPathError(f"{source}: the relative path '{relpath}' contains a NUL byte")

    posix = PurePosixPath(relpath)
    windows = PureWindowsPath(relpath)
    if (
        posix.is_absolute()
        or windows.is_absolute()
        or bool(posix.root)
        or bool(windows.root)
        or bool(windows.drive)
        or relpath.startswith(("/", "\\"))
    ):
        raise InstallPathError(
            f"{source}: refusing the absolute path {relpath!r} (as supplied: "
            f"{relpath}). Install destinations are always relative to the target root."
        )
    if ".." in posix.parts or ".." in windows.parts:
        raise InstallPathError(
            f"{source}: refusing '{relpath}' — it contains a '..' component and would "
            f"climb out of the target root."
        )
    if not posix.parts:
        raise InstallPathError(f"{source}: '{relpath}' is empty after normalisation")
    if relpath != relpath.strip() or "\\" in relpath or any(
        part in ("", ".", "..") for part in relpath.split("/")
    ):
        raise InstallPathError(f"{source}: refusing noncanonical relative path '{relpath}'")
    return posix


def safe_destination(root: Path, relpath: str) -> Path:
    """The destination ``root / relpath``, or :class:`InstallPathError`.

    **Gates every write and every delete; never a read.** Classification only
    reads, so it must not run this: in ``--symlink`` mode the placed skill
    directory *is* a symlink, and a per-file classifier that ran this guard would
    refuse every path in a development install and make ``gnd doctor --project``
    at this repository's own root permanently red.

    Four refusals, in order:

    1. the string-level checks of :func:`_reject_unsafe_relpath`;
    2. containment — the destination's parent must resolve INSIDE the resolved
       root, which catches an escape through a symlinked directory that points
       out of the root without any ``..`` appearing in the path;
    3. the parent chain — no element below the root may be an existing symlink,
       which catches a planted link that resolves inside the root today and can
       be re-pointed tomorrow;
    4. (implicitly) the leaf is NOT followed. A symlink standing AT a destination
       is a classification verdict (``collided``), not a path error, and
       ``os.replace`` onto it replaces the directory entry rather than writing
       through it (ASVS V12).
    """
    posix = _reject_unsafe_relpath(relpath, source="install destination")
    root = Path(root)
    dest = root.joinpath(*posix.parts)

    resolved_root = root.resolve()
    try:
        resolved_parent = dest.parent.resolve()
    except OSError as error:  # pragma: no cover - only on a broken filesystem
        raise InstallPathError(
            f"install destination: '{relpath}' could not be resolved under {root}: {error}"
        ) from error
    if not resolved_parent.is_relative_to(resolved_root):
        raise InstallPathError(
            f"install destination: '{relpath}' resolves to {resolved_parent} which is "
            f"outside the target root {resolved_root}. A hostile or corrupted manifest "
            f"must never be able to make a write or a delete land in the user's home."
        )

    current = root
    for part in posix.parts[:-1]:
        current = current / part
        if current.is_symlink():
            raise InstallPathError(
                f"install destination: '{relpath}' crosses an existing symlink at "
                f"{current}. A planted link must not be able to redirect a write out "
                f"of the target root (T-01.2-06)."
            )
        if current.exists() and not current.is_dir():
            raise InstallPathError(f"install destination: parent '{current}' is not a directory")
    return dest


ANCHORED_MUTATION = (
    hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
    and {os.open, os.unlink, os.mkdir, os.rmdir, os.rename, os.symlink} <= os.supports_dir_fd
)


_O_DESCEND = getattr(os, "O_DIRECTORY", 0) | getattr(os, "O_NOFOLLOW", 0) | os.O_RDONLY


def _descend(root: Path | int, parts: tuple[str, ...], *, create: bool) -> int:
    """A descriptor for ``root / *parts``, refusing to follow any symlink below ``root``.

    **This is the fix for the validate-then-act window (CR-01, CWE-367).**
    :func:`safe_destination` is ``lstat``/string-based and every caller runs it in
    a Phase 1 loop over all artifacts, then mutates in a separate Phase 2 loop.
    Carrying plain ``Path`` objects across that window let a directory symlink
    planted in between redirect both a delete and a write outside the target
    root, with no ``..``, no absolute path and no manifest tampering. A second
    validate-then-act pass would reproduce the bug in a new place; only the
    kernel can make the check and the act indivisible, which is what
    ``O_NOFOLLOW`` on every intermediate component does.

    A path ``root`` is opened directly for the ordinary install workflow. A
    descriptor ``root`` is duplicated instead, allowing callers such as codegen
    to retain a previously bound directory identity across plan and apply. In
    both cases every component below that anchor is opened with ``O_NOFOLLOW``.

    The caller owns the returned descriptor and must close it.
    """
    if isinstance(root, int):
        root_label = f"directory descriptor {root}"
        fd = os.dup(root)
    else:
        root = Path(root)
        root_label = str(root)
        if create:
            root.mkdir(parents=True, exist_ok=True)
        fd = os.open(root, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
    try:
        for part in parts:
            if create:
                with suppress(FileExistsError):
                    os.mkdir(part, dir_fd=fd)
            try:
                nxt = os.open(part, _O_DESCEND, dir_fd=fd)
            except OSError as error:
                raise InstallPathError(
                    f"install destination: the component '{part}' under {root_label} is not a "
                    f"directory this operation may descend into ({error.strerror}). A "
                    f"symlink planted after the path was validated must not be able to "
                    f"redirect a write or a delete out of the target root (T-01.2-06, "
                    f"CWE-367)."
                ) from error
            os.close(fd)
            fd = nxt
    except BaseException:
        os.close(fd)
        raise
    return fd


def _temp_name() -> str:
    """A collision-resistant staging name, created with ``O_EXCL`` so it cannot
    be pre-empted by a planted entry."""
    return f".gnd-tmp-{os.urandom(8).hex()}"


_NO_REPLACE_CONFLICT_ERRNOS = frozenset({errno.EEXIST, errno.ENOTEMPTY})


def _rename_noreplace(
    src_dir_fd: int,
    src: str,
    dst_dir_fd: int,
    dst: str,
) -> None:
    """Rename one descriptor-relative entry without replacing ``dst``.

    Python does not expose either claimed platform's exclusive rename flag.
    Bind the native primitive directly and fail closed everywhere else: falling
    back to ``os.rename`` would recreate the check-to-replace window this helper
    exists to close.
    """
    libc = ctypes.CDLL(None, use_errno=True)
    src_bytes = os.fsencode(src)
    dst_bytes = os.fsencode(dst)
    if sys.platform == "darwin":
        rename = getattr(libc, "renameatx_np", None)
        flags = 0x00000004  # RENAME_EXCL
    elif sys.platform.startswith("linux"):
        rename = getattr(libc, "renameat2", None)
        flags = 0x00000001  # RENAME_NOREPLACE
    else:  # pragma: no cover - Darwin and Linux are the claimed platforms
        rename = None
        flags = 0
    if rename is None:
        raise OSError(
            errno.ENOTSUP,
            "descriptor-relative rename-without-replacement is unavailable",
            f"{src} -> {dst}",
        )
    result = rename(
        ctypes.c_int(src_dir_fd),
        ctypes.c_char_p(src_bytes),
        ctypes.c_int(dst_dir_fd),
        ctypes.c_char_p(dst_bytes),
        ctypes.c_uint(flags),
    )
    if result != 0:
        error_number = ctypes.get_errno()
        raise OSError(
            error_number,
            os.strerror(error_number),
            f"{src} -> {dst}",
        )


class LeafIdentity(BaseModel):
    """Leaf identity captured by planning and revalidated at mutation time."""

    model_config = ConfigDict(extra="forbid")

    kind: Literal["absent", "file", "symlink"]
    sha256: str | None = None
    link_value: str | None = None


def _matches_leaf(fd: int, name: str, expected: LeafIdentity) -> bool:
    if expected.kind == "symlink":
        # A portable POSIX descriptor cannot expose a symlink's link text.
        # Compare that text between two no-follow identity observations; this
        # branch never opens the link and therefore cannot follow or block on
        # the occupant. Regular leaves use the single descriptor path below.
        try:
            before = os.stat(name, dir_fd=fd, follow_symlinks=False)
            if not stat.S_ISLNK(before.st_mode):
                return False
            link_value = os.readlink(name, dir_fd=fd)
            after = os.stat(name, dir_fd=fd, follow_symlinks=False)
        except OSError:
            return False
        stable = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        return (
            all(getattr(before, field) == getattr(after, field) for field in stable)
            and link_value == expected.link_value
        )
    try:
        leaf_fd = os.open(
            name,
            os.O_RDONLY
            | getattr(os, "O_NOFOLLOW", 0)
            | getattr(os, "O_NONBLOCK", 0),
            dir_fd=fd,
        )
    except FileNotFoundError:
        return expected.kind == "absent"
    except OSError:
        # O_NOFOLLOW rejects symlinks. Their link text is safe to inspect but
        # cannot authorize replacing a different occupant that raced into the
        # temporary name, so refuse and let the caller restore it.
        return False
    try:
        before = os.fstat(leaf_fd)
        if expected.kind != "file" or not stat.S_ISREG(before.st_mode):
            return False
        digest = hashlib.sha256()
        while chunk := os.read(leaf_fd, 64 * 1024):
            digest.update(chunk)
        after = os.fstat(leaf_fd)
        stable = (
            "st_dev",
            "st_ino",
            "st_mode",
            "st_size",
            "st_mtime_ns",
            "st_ctime_ns",
        )
        return (
            all(getattr(before, field) == getattr(after, field) for field in stable)
            and digest.hexdigest() == expected.sha256
        )
    finally:
        os.close(leaf_fd)


def _replace_staged_leaf(fd: int, staging: str, name: str, expected: LeafIdentity | None) -> None:
    """Install ``staging`` only if ``name`` still has its planned identity."""
    if expected is None:
        os.replace(staging, name, src_dir_fd=fd, dst_dir_fd=fd)
        return
    if expected.kind == "absent":
        try:
            os.link(
                staging,
                name,
                src_dir_fd=fd,
                dst_dir_fd=fd,
                follow_symlinks=False,
            )
        except FileExistsError as error:
            raise InstallError(
                f"install destination '{name}' changed after planning; refusing to overwrite it"
            ) from error
        os.unlink(staging, dir_fd=fd)
        return

    while True:
        previous = f".gnd-recovery-{os.urandom(8).hex()}"
        try:
            _rename_noreplace(fd, name, fd, previous)
        except OSError as error:
            if error.errno in _NO_REPLACE_CONFLICT_ERRNOS:
                continue
            if error.errno == errno.ENOENT:
                raise InstallError(
                    f"install destination '{name}' disappeared after planning; "
                    "refusing the write"
                ) from error
            raise
        break
    try:
        if not _matches_leaf(fd, previous, expected):
            raise InstallError(
                f"install destination '{name}' changed after planning; refusing to overwrite it"
            )
        try:
            _rename_noreplace(fd, staging, fd, name)
        except OSError as error:
            if error.errno in _NO_REPLACE_CONFLICT_ERRNOS:
                raise InstallError(
                    f"install destination '{name}' was claimed during publication; "
                    "refusing to overwrite it"
                ) from error
            raise
    except BaseException as publication_error:
        try:
            _rename_noreplace(fd, previous, fd, name)
        except OSError as restore_error:
            if restore_error.errno in _NO_REPLACE_CONFLICT_ERRNOS:
                detail = "a concurrent destination occupant was preserved"
            else:
                detail = f"restoration failed: {restore_error}"
            raise InstallError(
                f"install destination '{name}' could not be restored because {detail}; "
                f"the moved original is preserved as recovery entry '{previous}'"
            ) from publication_error
        raise
    else:
        os.unlink(previous, dir_fd=fd)


def _fdopen_owned(fd: int, mode: str):
    """Transfer a raw descriptor to ``fdopen`` or close it on setup failure."""
    try:
        return os.fdopen(fd, mode)
    except BaseException:
        os.close(fd)
        raise


def _atomic_write(
    root: Path | int,
    relpath: str,
    data: bytes,
    *,
    expected: LeafIdentity | None = None,
) -> None:
    """Write ``data`` to ``root / relpath`` atomically within one filesystem.

    ``os.replace`` is atomic on POSIX and Windows, and replacing the directory
    ENTRY is also what makes a forced write over a pre-existing symlink safe: the
    link is replaced, never followed. Directory-level rename is deliberately not
    used anywhere in this module — ``os.replace`` on a non-empty target directory
    raises on POSIX, so a "swap the whole tree" design would need a
    delete-then-rename window that is strictly worse than per-file atomic writes.

    Takes ``root`` and a relative path rather than a finished destination so the
    write can be anchored to a descriptor obtained by :func:`_descend` — see
    CR-01 there. The staging file is created with ``O_CREAT | O_EXCL`` and never
    opened through a path, so nothing between here and the ``replace`` can be
    redirected.
    """
    posix = _reject_unsafe_relpath(relpath, source="install destination")
    name = posix.parts[-1]
    if not ANCHORED_MUTATION:  # pragma: no cover - POSIX is the claimed platform
        if isinstance(root, int):
            raise InstallPathError(
                "descriptor-anchored writes require ANCHORED_MUTATION support"
            )
        safe_destination(root, relpath)  # best-effort: re-check immediately before the act
        dest = Path(root).joinpath(*posix.parts)
        dest.parent.mkdir(parents=True, exist_ok=True)
        handle_fd, tmp_name = tempfile.mkstemp(dir=dest.parent, prefix=".gnd-tmp-")
        try:
            with _fdopen_owned(handle_fd, "wb") as handle:
                handle.write(data)
            os.replace(tmp_name, dest)
        except BaseException:
            with suppress(OSError):
                os.unlink(tmp_name)
            raise
        return

    fd = _descend(root, posix.parts[:-1], create=True)
    try:
        staging = _temp_name()
        handle_fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, FILE_MODE, dir_fd=fd)
        try:
            with _fdopen_owned(handle_fd, "wb") as handle:
                handle.write(data)
            _replace_staged_leaf(fd, staging, name, expected)
        except BaseException:
            with suppress(OSError):
                os.unlink(staging, dir_fd=fd)
            raise
    finally:
        os.close(fd)



# Historical qualifications are serialized by existing callers.
InstallError.__module__ = 'gnd.install'
InstallPathError.__module__ = 'gnd.install'
_reject_unsafe_relpath.__module__ = 'gnd.install'
safe_destination.__module__ = 'gnd.install'
_descend.__module__ = 'gnd.install'
_temp_name.__module__ = 'gnd.install'
_rename_noreplace.__module__ = 'gnd.install'
LeafIdentity.__module__ = 'gnd.install'
_matches_leaf.__module__ = 'gnd.install'
_replace_staged_leaf.__module__ = 'gnd.install'
_fdopen_owned.__module__ = 'gnd.install'
_atomic_write.__module__ = 'gnd.install'

reject_unsafe_relpath = _reject_unsafe_relpath
descend = _descend
temp_name = _temp_name
rename_noreplace = _rename_noreplace
matches_leaf = _matches_leaf
replace_staged_leaf = _replace_staged_leaf
fdopen_owned = _fdopen_owned
atomic_write = _atomic_write

from gnd import artifacts as _artifacts

artifact_safe_fs_coordinate = _artifacts._safe_fs_coordinate
artifact_open_root = _artifacts._open_root
artifact_descend = _artifacts._descend
artifact_write_new_file = _artifacts._write_new_file
artifact_write_new_file_at = _artifacts._write_new_file_at
artifact_read_regular_bounded = _artifacts.read_regular_bounded
artifact_read_regular_bounded_at = _artifacts.read_regular_bounded_at
artifact_read_regular_file_bytes = _artifacts.read_regular_file_bytes
artifact_tree_sha256_from_directory = _artifacts.tree_sha256_from_directory
artifact_publish_leaf_atomic = _artifacts.publish_leaf_atomic
artifact_publish_directory_once = _artifacts.publish_directory_once
artifact_stat_leaf_at = _artifacts.stat_leaf_at
artifact_readlink_at = _artifacts.readlink_at
artifact_inventory_tree = _artifacts.inventory_tree
artifact_remove_regular_if_unchanged = _artifacts.remove_regular_if_unchanged

# Public dependency and compatibility spellings; same predecessor objects.
NO_REPLACE_CONFLICT_ERRNOS = _NO_REPLACE_CONFLICT_ERRNOS
O_DESCEND = _O_DESCEND
atomic_write = _atomic_write
descend = _descend
fdopen_owned = _fdopen_owned
matches_leaf = _matches_leaf
reject_unsafe_relpath = _reject_unsafe_relpath
rename_noreplace = _rename_noreplace
replace_staged_leaf = _replace_staged_leaf
temp_name = _temp_name

# Unqualified public read seams retain the artifact-specific algorithm.
read_regular_bounded = _artifacts.read_regular_bounded
read_regular_bounded_at = _artifacts.read_regular_bounded_at


def file_sha256(path: str | Path) -> str:
    """Stream a stable regular leaf; never block waiting for a FIFO writer."""
    fd = os.open(path, os.O_RDONLY | getattr(os, 'O_NONBLOCK', 0))
    try:
        before = os.fstat(fd)
        if stat.S_ISDIR(before.st_mode):
            raise IsADirectoryError(21, 'Is a directory', str(path))
        if not stat.S_ISREG(before.st_mode):
            raise ValueError('digest input is not a regular file')
        hasher = hashlib.sha256()
        size = 0
        while chunk := os.read(fd, 1024 * 1024):
            hasher.update(chunk)
            size += len(chunk)
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns) != (
            after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns
        ) or size != after.st_size:
            raise ValueError('digest input changed while reading')
        return hasher.hexdigest()
    finally:
        os.close(fd)
