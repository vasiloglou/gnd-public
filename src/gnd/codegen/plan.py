"""The six-state classifier, ``--force`` gating, and idempotence ACCOUNTING.

G-06 says regeneration rewrites derived paths, refuses unmanaged or user-owned
paths without ``--force``, and is idempotent in a way that is testable: *a second
run performs zero writes and leaves identical hashes.*

**None of that is inherited.** RESEARCH §1.3 item 2 reproduced the opposite
behaviour in the shipped tree — ``gnd extract`` was handed a hand-edited artifact
and silently overwrote it at exit 0. The six-state classifier exists exactly once
in GND, in ``install.py:784``, and it is scoped to skill placement with its own
manifest schema, its own packaged-resource side, and its own symlink-mode
branch. So this module reuses the **pattern** and not the code: the state
vocabulary, the published-gate discipline, the countable result, and the rule
that a refused operation destroys nothing.

**Ownership maps onto the states like this (G-04/G-05):**

======================================================  ==========
a DERIVED file whose bytes are what this run would emit  ``current``
a DERIVED file whose bytes are what the manifest recorded, and the emission moved on  ``stale``
a DERIVED file whose bytes match NEITHER — a hand edit   ``modified``
a DERIVED file the manifest records and disk does not    ``missing``
a path nothing has ever recorded, occupied               ``collided``
a path nothing has ever recorded, free                   ``create``
======================================================  ==========

**Idempotence is ACCOUNTING, not a claim.** :class:`ApplyResult` counts writes,
which is the only reason "a second run performs zero writes" can be asserted
rather than asserted-about. ``install.py``'s ``ApplyResult`` is the precedent and
the reason PKG-02's equivalent claim survived review.

**A refused write is never adopted into the record.** When a ``modified`` file is
refused, its manifest entry keeps the PREVIOUS digest. Recording the edited bytes
instead would make the next run see ``have == recorded`` and ``have != expected``,
classify it ``stale``, and rewrite it — destroying the edit one run later through
the very mechanism that protected it now. That is a subtle enough failure that it
has its own test.

**Codegen never deletes.** ``install.py`` prunes orphans because an upgrade that
withdraws a skill file would otherwise leave it live in the agent's skills
directory forever (CR-04). A generated project is the USER's tree; a file this
model no longer emits (after a model rename changes the artifact stem, say) is
reported in :attr:`ApplyResult.orphans` and carried in the manifest unchanged, so
it stays claimed and visible without codegen taking on the right to remove files
from a directory the user owns.
"""

from __future__ import annotations

import hashlib
import os
import stat
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from typing import TYPE_CHECKING, Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

from gnd.codegen.manifest import (
    MANIFEST_FILENAME,
    MAX_CODEGEN_MANIFEST_BYTES,
    CodegenManifest,
    CodegenManifestError,
    ManagedFile,
    Ownership,
    build_manifest,
    digest_text,
    read_manifest_bytes,
    render_manifest,
)

if TYPE_CHECKING:
    from gnd.safefs import LeafIdentity

__all__ = [
    "FORCED_STATES",
    "MAX_CLASSIFY_BYTES",
    "WRITABLE_STATES",
    "ActionableCollision",
    "ApplyResult",
    "CodegenPlan",
    "FileState",
    "apply_codegen",
    "classify_file",
    "plan_codegen",
]

#: States :func:`apply_codegen` turns into writes WITHOUT ``--force``.
#:
#: Two exclusions, and both are the point rather than an omission. ``modified``
#: is never here because a user edit is never silently destroyed (``install.py``
#: D-11, and RESEARCH §1.3 item 2's reproduction of what happens when it is).
#: ``collided`` is never here because an unmanaged occupant was not placed by
#: GND and GND does not get to overwrite what it did not write. Both join only
#: under ``--force`` — see :data:`FORCED_STATES`.
#:
#: A third exclusion cuts ACROSS the states: a file whose ownership is
#: ``extension`` is writable in ``create`` and in no other state, ever, with or
#: without ``--force``. G-06 is unconditional there, because a lost dependency
#: list or a lost domain note is unrecoverable while a stale derived file is
#: visible and one command from being fixed.
WRITABLE_STATES: frozenset[str] = frozenset({"create", "stale", "missing"})

#: The two states ``--force`` adds, and the complete list of what ``--force``
#: does. It never widens the extension rule and never reaches a path outside the
#: planned set, so ``gnd codegen --force`` over a directory holding unrelated
#: user work touches none of it.
FORCED_STATES: frozenset[str] = frozenset({"modified", "collided"})

#: Ceiling on a file the classifier will READ from a generated project, taken
#: from ``install.MAX_CLASSIFY_BYTES`` so the two lanes bound untrusted input
#: identically. Over the cap the file is classified from its stat and REPORTED,
#: never hashed (T-03-21, WR-03).
MAX_CLASSIFY_BYTES = 10 * 1024 * 1024

FileStateName = Literal[
    "create", "current", "stale", "missing", "modified", "collided"
]


class FileState(BaseModel):
    """Per-file classification record.

    Shaped after ``install.SkillFileState``, itself shaped after
    :class:`gnd.model.ValidationIssue` — the project's one structured-record
    vocabulary. ``detail`` carries the reason where the state alone is
    ambiguous: a directory and a hand edit are both ``modified``, and only the
    detail says which.
    """

    model_config = ConfigDict(extra="forbid")

    relpath: str
    state: FileStateName
    ownership: Ownership
    detail: str = ""


class CodegenPlan(BaseModel):
    """What :func:`apply_codegen` would do. Produced with ZERO writes.

    The split from apply is load-bearing rather than tidy, for the same reason
    ``emit_project`` is split from ``write_project``: plan 06's conformance
    assertions recompute the expected surface from the model and must be able to
    do that without producing a directory as a side effect.
    """

    model_config = ConfigDict(extra="forbid")

    model_path: str
    files: list[FileState]
    #: Identity of the real output directory classified by this plan. Both are
    #: ``None`` only when the root was absent.
    root_device: int | None = None
    root_inode: int | None = None
    #: For an absent root, the nearest existing parent and the missing path
    #: components below it. Apply reopens this parent by identity and creates
    #: every component relative to its descriptor.
    root_parent_path: str | None = None
    root_parent_device: int | None = None
    root_parent_inode: int | None = None
    root_relative_parts: list[str] = Field(default_factory=list)
    #: Manifest entries this model no longer emits. Reported, never deleted.
    orphans: list[str] = Field(default_factory=list)

    def by_relpath(self) -> dict[str, FileState]:
        return {record.relpath: record for record in self.files}

    @model_validator(mode="after")
    def _root_identity_is_complete(self) -> CodegenPlan:
        if (self.root_device is None) != (self.root_inode is None):
            raise ValueError("root_device and root_inode must be both present or both absent")
        parent_values = (
            self.root_parent_path,
            self.root_parent_device,
            self.root_parent_inode,
        )
        if any(value is None for value in parent_values) != all(
            value is None for value in parent_values
        ):
            raise ValueError("root parent path, device, and inode must be all present or absent")
        if self.root_device is None:
            if self.root_parent_path is None or not self.root_relative_parts:
                raise ValueError("an absent root must retain its nearest existing parent")
        elif self.root_parent_path is not None or self.root_relative_parts:
            raise ValueError("an existing root must not carry an absent-root parent binding")
        return self


class ActionableCollision(BaseModel):
    """One apply-time refusal and the action that can clear it."""

    model_config = ConfigDict(extra="forbid")

    relpath: str
    state: FileStateName
    ownership: Ownership
    previous_ownership: Ownership | None = None
    occupant_kind: Literal["absent", "file", "symlink", "other", "changed"]
    detail: str = ""
    remediation: Literal["force", "remove"]


class ApplyResult(BaseModel):
    """What :func:`apply_codegen` did, in numbers a test can assert on.

    ``writes`` counts generated FILES only. The manifest is excluded and tracked
    by ``manifest_written`` instead — it is codegen metadata, not a generated
    artifact, and G-06's zero-write claim is about the project.
    """

    model_config = ConfigDict(extra="forbid")

    writes: int = 0
    written: list[str] = Field(default_factory=list)
    #: Records apply deliberately did not act on: refused ``modified`` and
    #: ``collided`` files, and every non-``create`` state of an extension file.
    skipped: list[FileState] = Field(default_factory=list)
    #: Actionable paths whose write or adoption was blocked. This remains the
    #: sole channel the CLI turns into ``EXIT_COLLISION``.
    collisions: list[str] = Field(default_factory=list)
    #: Apply-time records for ``collisions``, with exact ordered path parity.
    collision_details: list[ActionableCollision] = Field(default_factory=list)
    #: Authored regular extensions preserved by the create-once rule. Purely
    #: informational: this channel never selects an exit.
    extension_skips: list[str] = Field(default_factory=list)
    #: Recorded by the manifest, not emitted by this model. Never deleted.
    orphans: list[str] = Field(default_factory=list)
    manifest_written: bool = False
    manifest: CodegenManifest | None = None

    @model_validator(mode="after")
    def _channels_are_aligned_and_disjoint(self) -> ApplyResult:
        detail_paths = [detail.relpath for detail in self.collision_details]
        if detail_paths != self.collisions:
            raise ValueError(
                "collision_details relpaths must exactly equal collisions in order"
            )
        overlap = set(self.collisions) & set(self.extension_skips)
        if overlap:
            raise ValueError(
                "an apply path cannot be both actionable and informational: "
                f"{sorted(overlap)}"
            )
        return self


def _authored_extension_skip(
    previous: ManagedFile | None,
    observation: _LeafObservation,
    record: FileState,
) -> bool:
    """Whether the exact locked three-conjunct informational route applies."""
    return (
        previous is not None
        and previous.ownership == "extension"
        and observation.kind == "file"
        and record.state == "modified"
    )


def _collision_remediation(
    previous: ManagedFile | None,
    observation: _LeafObservation,
    record: FileState,
    *,
    force: bool,
) -> Literal["force", "remove"]:
    """Classify the next action from the locked force-expanded matrix."""
    if force:
        return "remove"
    if record.ownership == "derived" and observation.kind in {"file", "symlink"}:
        return "force"
    if (
        record.ownership == "extension"
        and previous is None
        and record.state == "collided"
        and observation.kind == "file"
    ):
        return "force"
    return "remove"


def _append_actionable_collision(
    collisions: list[str],
    collision_details: list[ActionableCollision],
    *,
    previous: ManagedFile | None,
    observation: _LeafObservation,
    record: FileState,
    force: bool,
    occupant_kind: Literal["absent", "file", "symlink", "other", "changed"] | None = None,
    remediation: Literal["force", "remove"] | None = None,
) -> None:
    """Append both actionable channels at their single authoritative seam."""
    collisions.append(record.relpath)
    collision_details.append(
        ActionableCollision(
            relpath=record.relpath,
            state=record.state,
            ownership=record.ownership,
            previous_ownership=None if previous is None else previous.ownership,
            occupant_kind=observation.kind if occupant_kind is None else occupant_kind,
            detail=record.detail,
            remediation=(
                _collision_remediation(previous, observation, record, force=force)
                if remediation is None
                else remediation
            ),
        )
    )


def _writable(state: str, ownership: str, *, force: bool) -> bool:
    """The ONE gate, so no caller can decide writability a second way."""
    if ownership == "extension":
        # Create-once. Creating a file that is not there is not "touching an
        # extension file"; everything else about one is.
        return state == "create"
    if state in WRITABLE_STATES:
        return True
    return force and state in FORCED_STATES


def classify_file(
    root: str | Path,
    relpath: str,
    *,
    expected_text: str,
    ownership: Ownership,
    recorded: ManagedFile | None,
) -> FileState:
    """Classify one planned path from one no-follow descriptor observation."""
    return _classify_observation(
        relpath,
        _observe_leaf(Path(root), relpath),
        expected_text=expected_text,
        ownership=ownership,
        recorded=recorded,
    )


def plan_codegen(
    project: Any,
    out_root: str | Path,
    manifest: CodegenManifest | None,
    *,
    root_fd: int | None = None,
) -> CodegenPlan:
    """Classify every path this emission plans. Writes NOTHING.

    **The enumerated set is closed** and it is the project's own relpaths — the
    tree ``emit_project`` described. The output directory is never walked
    looking for work, so a file the user keeps beside their generated project is
    never classified, never reported and never touched, with or without
    ``--force``.

    Manifest entries this model no longer emits are reported as ``orphans``
    rather than classified: there is no expected content to compare them
    against, and codegen does not delete.
    """
    recorded = manifest.entries() if manifest is not None else {}
    planned = {file.relpath for file in project.files}
    owned_fd = root_fd is None
    descriptor = root_fd
    if descriptor is None:
        try:
            descriptor = _open_codegen_root(Path(out_root))
        except FileNotFoundError:
            descriptor = None
    try:
        if descriptor is None:
            parent_path, root_parts, parent_fd = _bind_codegen_parent(Path(out_root))
            try:
                parent_info = os.fstat(parent_fd)
                parent_device, parent_inode = parent_info.st_dev, parent_info.st_ino
            finally:
                os.close(parent_fd)
            records = [
                _classify_observation(
                    file.relpath,
                    _LeafObservation(kind="absent"),
                    expected_text=file.text,
                    ownership=file.ownership,
                    recorded=recorded.get(file.relpath),
                )
                for file in project.files
            ]
            root_device = root_inode = None
        else:
            root_info = os.fstat(descriptor)
            root_device, root_inode = root_info.st_dev, root_info.st_ino
            parent_path = None
            parent_device = parent_inode = None
            root_parts = ()
            records = [
                _classify_observation(
                    file.relpath,
                    _observe_leaf_at(descriptor, file.relpath),
                    expected_text=file.text,
                    ownership=file.ownership,
                    recorded=recorded.get(file.relpath),
                )
                for file in project.files
            ]
        return CodegenPlan(
            model_path=str(project.model_path),
            files=records,
            root_device=root_device,
            root_inode=root_inode,
            root_parent_path=None if parent_path is None else str(parent_path),
            root_parent_device=parent_device,
            root_parent_inode=parent_inode,
            root_relative_parts=list(root_parts),
            orphans=sorted(rel for rel in recorded if rel not in planned),
        )
    finally:
        if owned_fd and descriptor is not None:
            os.close(descriptor)


@dataclass(frozen=True)
class _LeafObservation:
    kind: Literal["absent", "file", "symlink", "other"]
    sha256: str | None = None
    link_value: str | None = None
    detail: str = ""


def _observe_leaf_at(root_fd: int, relpath: str) -> _LeafObservation:
    """Observe one leaf by descriptor, never by a check-then-pathname read."""
    from gnd.safefs import InstallPathError

    parts = PurePosixPath(relpath).parts
    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    fd = os.dup(root_fd)
    try:
        for part in parts[:-1]:
            try:
                next_fd = os.open(part, directory_flags, dir_fd=fd)
            except FileNotFoundError:
                return _LeafObservation(kind="absent")
            except OSError as error:
                raise InstallPathError(
                    "the parent path could not be opened without following links: "
                    f"{error}"
                ) from error
            os.close(fd)
            fd = next_fd

        name = parts[-1]
        try:
            leaf_fd = os.open(
                name,
                os.O_RDONLY
                | getattr(os, "O_NOFOLLOW", 0)
                | getattr(os, "O_NONBLOCK", 0),
                dir_fd=fd,
            )
        except FileNotFoundError:
            return _LeafObservation(kind="absent")
        except OSError as error:
            # O_NOFOLLOW reports a leaf symlink as ELOOP. Inspecting it after
            # the failed open is classification only: no later pathname open
            # can follow the reported link.
            try:
                info = os.stat(name, dir_fd=fd, follow_symlinks=False)
                if stat.S_ISLNK(info.st_mode):
                    return _LeafObservation(
                        kind="symlink", link_value=os.readlink(name, dir_fd=fd)
                    )
            except OSError:
                pass
            return _LeafObservation(
                kind="other",
                detail=f"the leaf could not be opened without following links: {error}",
            )
        try:
            info = os.fstat(leaf_fd)
            if not stat.S_ISREG(info.st_mode):
                kind = "a directory" if stat.S_ISDIR(info.st_mode) else "a non-regular file"
                return _LeafObservation(
                    kind="other",
                    detail=(
                        f"{kind} (mode {stat.filemode(info.st_mode)}) stands where a "
                        "regular file belongs and was not hashed"
                    ),
                )
            if info.st_size > MAX_CLASSIFY_BYTES:
                return _LeafObservation(
                    kind="other",
                    detail=(
                        f"{info.st_size} bytes exceeds the {MAX_CLASSIFY_BYTES}-byte cap "
                        "and was not hashed"
                    ),
                )
            digest = hashlib.sha256()
            while chunk := os.read(leaf_fd, 64 * 1024):
                digest.update(chunk)
            after = os.fstat(leaf_fd)
            identity_fields = (
                "st_dev",
                "st_ino",
                "st_mode",
                "st_size",
                "st_mtime_ns",
                "st_ctime_ns",
            )
            if any(getattr(info, field) != getattr(after, field) for field in identity_fields):
                return _LeafObservation(
                    kind="other",
                    detail="the regular file changed while its descriptor was hashed",
                )
        finally:
            os.close(leaf_fd)
        return _LeafObservation(kind="file", sha256=digest.hexdigest())
    except InstallPathError as error:
        return _LeafObservation(kind="other", detail=str(error))
    except OSError as error:
        return _LeafObservation(
            kind="other", detail=f"the leaf changed while it was inspected: {error}"
        )
    finally:
        os.close(fd)


def _observe_leaf(root: Path, relpath: str) -> _LeafObservation:
    """Open a real root once, then delegate to the shared descriptor observer."""
    try:
        root_fd = _open_codegen_root(root)
    except FileNotFoundError:
        return _LeafObservation(kind="absent")
    except OSError as error:
        return _LeafObservation(
            kind="other",
            detail=f"the output root could not be opened without following links: {error}",
        )
    try:
        return _observe_leaf_at(root_fd, relpath)
    finally:
        os.close(root_fd)


def _open_codegen_root(root: Path) -> int:
    """Open one real output root without following a final symlink."""
    from gnd.safefs import InstallPathError

    flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        descriptor = os.open(root, flags)
    except FileNotFoundError:
        raise
    except OSError as error:
        raise InstallPathError(
            f"output root {root} is a non-directory or symlink and could not be "
            f"opened as a real directory without following links: {error}"
        ) from error
    info = os.fstat(descriptor)
    if not stat.S_ISDIR(info.st_mode):
        os.close(descriptor)
        raise InstallPathError(f"output root {root} is not a real directory")
    return descriptor


def _bind_codegen_parent(root: Path) -> tuple[Path, tuple[str, ...], int]:
    """Bind the nearest existing parent of ``root`` without creating anything.

    The returned descriptor is owned by the caller. ``parts`` is the exact
    missing-or-final suffix to reach ``root`` from that parent.
    """
    from gnd.safefs import InstallPathError

    absolute = Path(os.path.abspath(root))
    candidate = absolute.parent
    parts = [absolute.name]
    while True:
        try:
            descriptor = _open_codegen_root(candidate)
        except FileNotFoundError:
            if candidate.parent == candidate:
                raise InstallPathError(
                    f"no existing parent could be bound for output root {root}"
                )
            parts.insert(0, candidate.name)
            candidate = candidate.parent
            continue
        return candidate, tuple(parts), descriptor


def _open_planned_absent_root(root: Path, plan: CodegenPlan) -> int:
    """Create a planned-absent root relative to its identity-bound parent."""
    from gnd.safefs import InstallPathError

    assert plan.root_parent_path is not None
    assert plan.root_parent_device is not None
    assert plan.root_parent_inode is not None
    anchor_path = Path(plan.root_parent_path)
    expected_root = anchor_path.joinpath(*plan.root_relative_parts)
    if Path(os.path.abspath(root)) != expected_root:
        raise InstallPathError(
            f"output root {root} is not the absent root bound by this plan"
        )
    try:
        anchor_fd = _open_codegen_root(anchor_path)
    except FileNotFoundError as error:
        raise InstallPathError(
            f"output parent {anchor_path} disappeared after planning"
        ) from error
    anchor_info = os.fstat(anchor_fd)
    if (anchor_info.st_dev, anchor_info.st_ino) != (
        plan.root_parent_device,
        plan.root_parent_inode,
    ):
        os.close(anchor_fd)
        raise InstallPathError(
            f"output parent {anchor_path} changed after planning; refusing every write"
        )
    try:
        _assert_root_path_bound(anchor_path, anchor_fd)
        current_fd = os.dup(anchor_fd)
        try:
            for part in plan.root_relative_parts:
                try:
                    os.mkdir(part, dir_fd=current_fd)
                except FileExistsError as error:
                    raise InstallPathError(
                        f"output root {root} was absent during planning but is now occupied"
                    ) from error
                next_fd = os.open(
                    part,
                    os.O_RDONLY
                    | getattr(os, "O_DIRECTORY", 0)
                    | getattr(os, "O_NOFOLLOW", 0)
                    | getattr(os, "O_NONBLOCK", 0),
                    dir_fd=current_fd,
                )
                os.close(current_fd)
                current_fd = next_fd
            return current_fd
        except BaseException:
            os.close(current_fd)
            raise
    finally:
        os.close(anchor_fd)


def _assert_root_path_bound(root: Path, root_fd: int) -> None:
    """Require the public output pathname to still name ``root_fd``."""
    from gnd.safefs import InstallPathError

    expected = os.fstat(root_fd)
    try:
        current_fd = _open_codegen_root(root)
    except (FileNotFoundError, InstallPathError) as error:
        raise InstallPathError(
            f"output root {root} changed after planning; refusing every write: {error}"
        ) from error
    try:
        current = os.fstat(current_fd)
        if (current.st_dev, current.st_ino) != (expected.st_dev, expected.st_ino):
            raise InstallPathError(
                f"output root {root} changed after planning; refusing every write"
            )
    finally:
        os.close(current_fd)


def _read_manifest_at(
    root_fd: int, root: Path
) -> tuple[CodegenManifest | None, LeafIdentity]:
    """Read the manifest and retain the identity of those exact bytes."""
    from gnd.safefs import LeafIdentity

    flags = (
        os.O_RDONLY
        | getattr(os, "O_NOFOLLOW", 0)
        | getattr(os, "O_NONBLOCK", 0)
    )
    try:
        leaf_fd = os.open(MANIFEST_FILENAME, flags, dir_fd=root_fd)
    except FileNotFoundError:
        return None, LeafIdentity(kind="absent")
    except OSError as error:
        raise CodegenManifestError(
            f"{root / MANIFEST_FILENAME} could not be opened safely: {error}"
        ) from error
    try:
        before = os.fstat(leaf_fd)
        if not stat.S_ISREG(before.st_mode):
            raise CodegenManifestError(
                f"{root / MANIFEST_FILENAME} is not a regular file"
            )
        if before.st_size > MAX_CODEGEN_MANIFEST_BYTES:
            raise CodegenManifestError(
                f"{root / MANIFEST_FILENAME} is {before.st_size} bytes, over the "
                f"{MAX_CODEGEN_MANIFEST_BYTES}-byte cap"
            )
        chunks = bytearray()
        while chunk := os.read(
            leaf_fd,
            min(64 * 1024, MAX_CODEGEN_MANIFEST_BYTES + 1 - len(chunks)),
        ):
            chunks.extend(chunk)
            if len(chunks) > MAX_CODEGEN_MANIFEST_BYTES:
                raise CodegenManifestError(
                    f"{root / MANIFEST_FILENAME} grew over the byte cap while read"
                )
        after = os.fstat(leaf_fd)
        stable = ("st_dev", "st_ino", "st_mode", "st_size", "st_mtime_ns", "st_ctime_ns")
        if any(getattr(before, field) != getattr(after, field) for field in stable):
            raise CodegenManifestError(
                f"{root / MANIFEST_FILENAME} changed while it was read"
            )
        data = bytes(chunks)
        if len(data) != before.st_size:
            raise CodegenManifestError(
                f"{root / MANIFEST_FILENAME} changed size while it was read"
            )
        return (
            read_manifest_bytes(data, source=str(root / MANIFEST_FILENAME)),
            LeafIdentity(kind="file", sha256=hashlib.sha256(data).hexdigest()),
        )
    finally:
        os.close(leaf_fd)


def _classify_observation(
    relpath: str,
    observation: _LeafObservation,
    *,
    expected_text: str,
    ownership: Ownership,
    recorded: ManagedFile | None,
) -> FileState:
    def record(state: FileStateName, detail: str = "") -> FileState:
        return FileState(
            relpath=relpath, state=state, ownership=ownership, detail=detail
        )

    if observation.kind == "absent":
        if recorded is None:
            return record("create")
        return record("missing", "recorded by the manifest but absent on disk")
    if observation.kind == "symlink":
        return record(
            "collided" if recorded is None else "modified",
            "a symlink stands where a regular file belongs",
        )
    if observation.kind == "other":
        return record(
            "collided" if recorded is None else "modified", observation.detail
        )

    have = observation.sha256
    if recorded is None:
        return record(
            "collided",
            "present on disk and recorded by no manifest — gnd codegen did not place it",
        )
    expected = digest_text(expected_text)
    if have == expected:
        detail = "" if have == recorded.sha256 else "matches this emission; the record was behind"
        return record("current", detail)
    if have == recorded.sha256:
        return record("stale", "matches the manifest; the derivation moved on")
    return record(
        "modified",
        "matches neither the manifest nor what this run emits — treated as a user edit",
    )


def _expected_identity(observation: _LeafObservation):
    from gnd.safefs import LeafIdentity

    if observation.kind == "absent":
        return LeafIdentity(kind="absent")
    if observation.kind == "file":
        return LeafIdentity(kind="file", sha256=observation.sha256)
    if observation.kind == "symlink":
        return LeafIdentity(kind="symlink", link_value=observation.link_value)
    return None


def apply_codegen(
    project: Any,
    out_root: str | Path,
    plan: CodegenPlan,
    *,
    force: bool = False,
    root_fd: int | None = None,
) -> ApplyResult:
    """Write only what ``plan`` says is writable, then the manifest, LAST.

    Refuses rather than executes where the rules conflict, following
    ``install.py``'s precedent that a refused operation destroys nothing: a
    blocked file is skipped and reported, the writable ones still land, and the
    caller turns a non-empty ``collisions`` list into ``EXIT_COLLISION``.

    The manifest is written after every artifact — ``_cmd_extract``'s
    index-last ordering — and only when something changed. Writing it
    unconditionally would make G-06's "a second run leaves identical hashes"
    false by construction, which is the same trap ``install.apply`` documents
    for ``installed_at``.
    """
    from gnd.safefs import InstallPathError

    root = Path(out_root)
    owned_fd = root_fd is None
    descriptor = root_fd
    if descriptor is None:
        if plan.root_device is None:
            descriptor = _open_planned_absent_root(root, plan)
        else:
            try:
                descriptor = _open_codegen_root(root)
            except FileNotFoundError as error:
                raise InstallPathError(
                    f"output root {root} disappeared after planning"
                ) from error
    elif plan.root_device is None:
        raise InstallPathError(
            f"output root {root} was absent during planning but is now occupied"
        )
    assert descriptor is not None
    expected_root = (plan.root_device, plan.root_inode)
    actual_root_info = os.fstat(descriptor)
    actual_root = (actual_root_info.st_dev, actual_root_info.st_ino)
    if plan.root_device is not None and actual_root != expected_root:
        if owned_fd:
            os.close(descriptor)
        raise InstallPathError(
            f"output root {root} changed after planning; refusing every write"
        )
    try:
        _assert_root_path_bound(root, descriptor)
    except BaseException:
        if owned_fd:
            os.close(descriptor)
        raise

    try:
        on_disk, manifest_identity = _read_manifest_at(descriptor, root)
        previous = {} if on_disk is None else on_disk.entries()

        written: list[str] = []
        skipped: list[FileState] = []
        collisions: list[str] = []
        collision_details: list[ActionableCollision] = []
        extension_skips: list[str] = []
        entries: list[ManagedFile] = []

        for file in project.files:
            previous_entry = previous.get(file.relpath)
            observation = _observe_leaf_at(descriptor, file.relpath)
            record = _classify_observation(
                file.relpath,
                observation,
                expected_text=file.text,
                ownership=file.ownership,
                recorded=previous_entry,
            )
            if _writable(record.state, record.ownership, force=force):
                expected_identity = _expected_identity(observation)
                if expected_identity is None:
                    skipped.append(record)
                    _append_actionable_collision(
                        collisions,
                        collision_details,
                        previous=previous_entry,
                        observation=observation,
                        record=record,
                        force=force,
                    )
                    if previous_entry is not None:
                        entries.append(previous_entry)
                    continue
                try:
                    from gnd.safefs import InstallError
                    from gnd.safefs import atomic_write as _atomic_write

                    _atomic_write(
                        descriptor,
                        file.relpath,
                        file.text.encode("utf-8"),
                        expected=expected_identity,
                    )
                except InstallError as error:
                    refused = record.model_copy(
                        update={
                            "state": "modified" if previous_entry else "collided",
                            "detail": (
                                "changed after apply-time reclassification; refusing to "
                                f"overwrite it: {error}"
                            ),
                        }
                    )
                    skipped.append(refused)
                    _append_actionable_collision(
                        collisions,
                        collision_details,
                        previous=previous_entry,
                        observation=observation,
                        record=refused,
                        force=force,
                        occupant_kind="changed",
                        remediation="remove",
                    )
                    if previous_entry is not None:
                        entries.append(previous_entry)
                    continue
                written.append(file.relpath)
                entries.append(
                    ManagedFile(
                        relpath=file.relpath,
                        sha256=digest_text(file.text),
                        ownership=file.ownership,
                    )
                )
                continue

            if record.state != "current":
                skipped.append(record)
                if (
                    record.ownership == "extension"
                    and record.state == "collided"
                    and force
                    and observation.kind == "file"
                    and observation.sha256 is not None
                ):
                    # Explicit --force adopts a pre-existing regular extension
                    # without writing it. Its actual digest records what was
                    # observed, while conformance reports the path as unexamined.
                    entries.append(
                        ManagedFile(
                            relpath=file.relpath,
                            sha256=observation.sha256,
                            ownership="extension",
                        )
                    )
                    continue
                if _authored_extension_skip(previous_entry, observation, record):
                    extension_skips.append(record.relpath)
                elif record.state in FORCED_STATES:
                    _append_actionable_collision(
                        collisions,
                        collision_details,
                        previous=previous_entry,
                        observation=observation,
                        record=record,
                        force=force,
                    )

            if record.state == "current":
                entries.append(
                    ManagedFile(
                        relpath=file.relpath,
                        sha256=digest_text(file.text),
                        ownership=file.ownership,
                    )
                )
            elif previous_entry is not None:
                # A REFUSED file keeps its previous entry. Adopting its current
                # bytes would classify it `stale` next run and rewrite it — the edit
                # destroyed one run later, through the guard that saved it.
                entries.append(previous_entry)
            # Otherwise unrecorded and unwritten (a collision): it stays unmanaged
            # and appears in ``collisions`` above, so no planned path can vanish
            # from both the manifest and the command outcome.

        for orphan in plan.orphans:
            carried = previous.get(orphan)
            if carried is not None:
                entries.append(carried)

        manifest = build_manifest(project, plan.model_path, entries=entries)
        manifest_text = render_manifest(manifest)
        manifest_observation = _observe_leaf_at(descriptor, MANIFEST_FILENAME)
        rendered = manifest_observation.sha256 != hashlib.sha256(
            manifest_text.encode("utf-8")
        ).hexdigest()
        manifest_written = False
        if written or rendered:
            from gnd.safefs import atomic_write as _atomic_write

            _atomic_write(
                descriptor,
                MANIFEST_FILENAME,
                manifest_text.encode("utf-8"),
                expected=manifest_identity,
            )
            manifest_written = True

        return ApplyResult(
            writes=len(written),
            written=written,
            skipped=skipped,
            collisions=collisions,
            collision_details=collision_details,
            extension_skips=extension_skips,
            orphans=list(plan.orphans),
            manifest_written=manifest_written,
            manifest=manifest,
        )
    finally:
        if owned_fd:
            os.close(descriptor)
