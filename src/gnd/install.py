"""Place the packaged skill tree into a runtime's skill directory (PKG-02).

**This is the only module in ``gnd`` that writes to the filesystem.** Every
other module is a pure reader — load, validate, report, exit. Nothing else here
resolves ``Path.home()``, reads an environment variable, creates a directory, or
persists state, and before this file there was no ``hashlib``, ``shutil``,
``os.replace``, ``tempfile``, or ``json.dump`` anywhere in the package. There was
therefore no whole-file analog to adapt: the plan/apply split, the six-state
classifier, target resolution, manifest schema versioning, and the path-traversal
guard are designed here rather than copied. Four seams *are* copied exactly —
packaged-resource reading (``model.py``/``report.py``/``population.py``), the
structured record with a severity-style split (``ValidationIssue``), exit-code
constants carrying a collision rationale (``cli.py``), and content identity by
bytes (``tests/test_schema_sync.py``).

Decisions implemented here: D-04 (read from the installed distribution, never a
repository-relative path), D-06 (discovery is a runtime walk, never a generated
table), D-08 (target roots and the copy default), D-09 (idempotence is
measurable; never overwrite what GND did not place), D-10 (one self-locating
manifest per target root), D-19 (``Traversable``-only traversal), D-23 (manifest
written last, so a partial install is diagnosable), D-24 (``pathlib`` throughout,
no Windows claim).

**Why plan-then-apply rather than "copy the tree over".** ``shutil.copytree``
overwrites unconditionally. That violates D-09's never-overwrite-unmanaged rule
and, worse, makes idempotence *unmeasurable*: after a blind copy every byte is
identical whether the installer wrote nothing or rewrote all 29 files. :func:`plan`
performs no writes at all, so the second run's write count is an observable that
a test can assert on, and ``doctor`` (plan 01.2-04) reuses it verbatim as a dry
run.

**Why the module file's own location is never used to find the skills.**
Walking up from this module's path to a repository-relative ``skills`` directory
happens to work in a checkout, and that checkout assumption is precisely what
this phase exists to delete. Every read below goes through
``importlib.resources.files("gnd")``.

**Traversal vocabulary is constrained (D-19).** ``iterdir()`` / ``is_dir()`` /
``read_bytes()`` and nothing else. Both ``importlib.resources`` escape hatches
that turn a resource handle into a filesystem path are forbidden here: one raises
``TypeError`` under zipimport, the other raises ``IsADirectoryError`` on a
directory on Python 3.11, this project's declared floor. They are named in full,
with the measured 3.11/3.12/3.13 × loader matrix, in
``tests/test_packaged_skills.py`` — and deliberately NOT spelled here, because
``tests/test_install.py`` greps this file's source for those exact tokens and a
prohibition written in a comment would blunt that guard into a constant nobody
can raise an alarm with. Never wrap a ``files()`` result in ``Path()``.

**What the classifier is allowed to look at.** Every target root in D-08 is a
*shared* directory: ``~/.claude/skills/`` holds the user's own skills and GND is
a guest. :func:`plan`'s enumeration is therefore **closed**, never discovered —
it is exactly the union of the relative paths the packaged tree yields and the
relative paths the manifest at this root records, and it never walks the target
root looking for surprises. A pre-existing unrelated skill, a stray ``README.md``
at the root, another tool's dotfile: not enumerated, not classified, not
reported, not counted toward the exit code, never touched. Without that rule,
``uv tool install get-nick-done && gnd install`` — the sentence this phase exists
to make true — exits 11 on a clean machine whose only sin is having one
pre-existing skill.
"""

from __future__ import annotations

import ctypes  # noqa: F401 -- historical compatibility binding
import errno  # noqa: F401 -- historical compatibility binding
import hashlib  # noqa: F401 -- historical compatibility binding
import json
import os
import shutil
import stat
import sys
import tempfile  # noqa: F401 -- historical compatibility binding
from collections.abc import Iterable, Iterator
from contextlib import suppress
from datetime import UTC, datetime
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import (
    Path,
    PurePosixPath,
    PureWindowsPath,  # noqa: F401 -- historical compatibility binding
)
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gnd import DISTRIBUTION, resolve_version
from gnd import input_policy as _rf7_input
from gnd.artifacts import sha256_hex as _sha256
from gnd.safefs import (
    ANCHORED_MUTATION as ANCHORED_MUTATION,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    FILE_MODE as FILE_MODE,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    NO_REPLACE_CONFLICT_ERRNOS as _NO_REPLACE_CONFLICT_ERRNOS,  # noqa: F401 -- compatibility surface
)
from gnd.safefs import (
    O_DESCEND as _O_DESCEND,  # noqa: F401 -- compatibility surface
)
from gnd.safefs import (
    InstallError as InstallError,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    InstallPathError as InstallPathError,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    LeafIdentity as LeafIdentity,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    atomic_write as _atomic_write,
)
from gnd.safefs import (
    descend as _descend,
)
from gnd.safefs import (
    fdopen_owned as _fdopen_owned,  # noqa: F401 -- compatibility surface
)
from gnd.safefs import (
    matches_leaf as _matches_leaf,
)
from gnd.safefs import (
    reject_unsafe_relpath as _reject_unsafe_relpath,
)
from gnd.safefs import (
    rename_noreplace as _rename_noreplace,  # noqa: F401 -- compatibility surface
)
from gnd.safefs import (
    replace_staged_leaf as _replace_staged_leaf,
)
from gnd.safefs import (
    safe_destination as safe_destination,  # noqa: PLC0414 -- compatibility surface
)
from gnd.safefs import (
    temp_name as _temp_name,
)

#: The self-locating install receipt (D-10). One per target root, leading dot so
#: it does not read as a skill directory to either runtime.
MANIFEST_NAME = ".gnd-install.json"

#: Bumped when a field's MEANING changes. A manifest declaring a HIGHER schema is
#: reported and refused, never guessed at — an uninstall driven by a
#: misinterpreted document deletes real files.
MANIFEST_SCHEMA = 2

#: Ceiling on the receipt itself. A 29-file receipt is roughly 5 KB, so 1 MB is
#: about 200x headroom — wide enough that no legitimate install approaches it and
#: narrow enough that a hostile document cannot choose the parser's workload
#: (WR-04). ``tests/test_review_fixes.py`` asserts both ends of that claim.
MAX_MANIFEST_BYTES = 1 * 1024 * 1024

#: Written in the final atomic write. On a FIRST install its ABSENCE is still the
#: partial-install signal (D-23).
STATUS_COMPLETE = "complete"

#: Written BEFORE the file writes of an UPGRADE, and replaced by
#: :data:`STATUS_COMPLETE` after them (WR-02).
#:
#: D-23's guarantee only ever covered a first install. On an upgrade the previous
#: receipt survives a crash with the previous digests, so the files GND itself
#: half-wrote hash-mismatch and used to classify as ``modified`` — "edited since
#: GND placed it" — which ``apply`` never rewrites and which ``--force`` does not
#: add, so there was no repair path at all and the state was sticky. This marker
#: makes the crash distinguishable from an edit, which is the whole of the fix:
#: under it a mismatch is ``stale`` (repairable by ``install``, removable by
#: ``uninstall``) instead of ``modified`` (untouchable by both).
#:
#: It carries the PREVIOUS run's skills map, never a new one, so it can never
#: claim a file it did not place — D-23's property, preserved. It is written only
#: when there is real work to do, so D-09's zero-write idempotence is unaffected.
STATUS_IN_PROGRESS = "in-progress"

#: ``synced`` is a reserved folder name in the enterprise/personal/project skill
#: locations of Claude Code, in any capitalisation. Never a GND skill name, and
#: the installer must not descend into one if it ever appears in the tree.
RESERVED_DIR_NAMES = frozenset({"synced"})

#: codex-cli 0.144.6, quoted from the shipped binary: "default to
#: ``$CODEX_HOME/skills``; when ``CODEX_HOME`` is unset, fall back to
#: ``~/.codex/skills``". The published docs disagree and name ``.agents/skills``;
#: the binary is what executes, so the binary wins (D-21).
CODEX_HOME_ENV = "CODEX_HOME"

#: The Codex skills location GND does **not** write. The published documentation
#: names ``.agents/skills`` and says ``~/.codex/skills`` "is not" the user-level
#: location; the shipped 0.144.6 binary says the opposite, and a live smoke test
#: found BOTH roots discovered. The binary wins (D-21) — but ``doctor`` names
#: this one as a known alternative, so a future documentation-driven change is
#: diagnosable rather than mysterious.
CODEX_ALTERNATE_DIR = ".agents"

#: Creation mode for every file this module places, MASKED BY THE UMASK by the
#: kernel's ``O_CREAT`` contract — so the effective mode is ``FILE_MODE & ~umask``
#: and the operator's umask is honoured rather than overridden.
#:
#: 0o644 matches the packaged files being copied and the 0o755 directories
#: ``mkdir`` creates around them. It used to be ``tempfile.mkstemp``'s hardcoded
#: 0o600, which ``os.replace`` then preserved, so the installed tree was
#: owner-read-only (WR-06): ``gnd install`` under ``sudo``, or into a root read
#: by an agent running as a different UID — a devcontainer, a mapped-UID mount, a
#: shared build agent — placed files that user could not read, and the failure
#: surfaced as the runtime silently not discovering the skills, which is the
#: exact diagnosis ``doctor`` exists to make easy. The umask is applied by the
#: kernel rather than read here, which avoids the read-then-restore race
#: ``os.umask`` would need.

RUNTIMES: tuple[str, ...] = ("claude", "codex")
SCOPES: tuple[str, ...] = ("global", "project")
MODES: tuple[str, ...] = ("copy", "symlink")

#: States :func:`apply` turns into writes. ``modified`` is never here (D-11: a
#: user edit is never destroyed) and ``collided`` joins only under ``force``.
WRITABLE_STATES: frozenset[str] = frozenset({"create", "stale", "missing"})

#: The two states whose bytes still hash to what the manifest recorded, and
#: therefore the ONLY states this module ever deletes. ``current`` is unchanged
#: since GND placed it; ``stale`` is unchanged since GND placed it and the
#: package has since moved on. ``modified`` and ``collided`` are excluded by
#: construction and there is deliberately no flag that adds them.
#:
#: One constant, two callers: :func:`remove` uses it for every deletion, and
#: :func:`apply` uses it to prune an ORPHAN — a file the receipt records that
#: this version no longer ships (CR-04). Sharing the gate is the point: install
#: may only remove what uninstall would have been allowed to remove.
REMOVABLE_STATES: frozenset[str] = frozenset({"current", "stale"})

#: Ceiling on a file the classifier will READ from a target root, matching the
#: 10 MB stat cap ``model.py`` and ``population.py`` put on untrusted documents.
#: A destination is another program's output sitting in a shared, user-writable
#: directory, so it is untrusted input in exactly the same sense; ``cli.py``
#: states the rule — bound every untrusted-input-proportional resource where it
#: is PRODUCED. Over the cap the file is classified from its stat and reported,
#: never hashed (WR-03).
MAX_CLASSIFY_BYTES = 10 * 1024 * 1024

#: How many per-file records a renderer names before eliding, mirroring
#: ``population.MAX_SUMMARY_ISSUES``. A doctor run over 29 files needs the same
#: cap for the same reason: a report nobody can read is not a report.
MAX_REPORTED_STATES = 20






class ManifestError(InstallError):
    """A manifest on disk could not be read as a manifest."""


class ManifestSchemaError(ManifestError):
    """The manifest declares a schema version this build does not understand."""


# ---------------------------------------------------------------------------
# packaged tree (D-04, D-06, D-19)
# ---------------------------------------------------------------------------


def packaged_skills_root() -> Traversable:
    """The ``Traversable`` for ``gnd/skills`` inside the installed distribution.

    Loaded through ``importlib.resources`` like the model, population, and report
    schemas, so the skills ship *with the installed package* rather than living
    only in the source tree.
    """
    root = files("gnd") / "skills"
    if not root.is_dir():
        raise InstallError(
            "the packaged skill tree gnd/skills is absent from this installation. "
            "It must live under src/gnd/skills/ so it ships inside the wheel and "
            "is visible identically from an editable checkout (D-04, D-05)."
        )
    return root


def iter_skill_files(root: Traversable, prefix: str = "") -> Iterator[tuple[str, Traversable]]:
    """Yield ``(posix-relative-path, resource)`` for every file beneath ``root``.

    ``Traversable``-only (D-19) — see the module docstring. Entries are sorted by
    name so two runs enumerate in the same order and the manifest is diffable.

    ``tests/test_packaged_skills.py`` and ``tests/test_install.py`` each keep an
    independent copy of this walk. That is deliberate: a bug in this one must not
    be able to hide behind the tests that consume it.
    """
    for entry in sorted(root.iterdir(), key=lambda item: item.name):
        name = entry.name
        if entry.is_dir():
            if name.casefold() in RESERVED_DIR_NAMES:
                continue
            yield from iter_skill_files(entry, f"{prefix}{name}/")
        else:
            yield f"{prefix}{name}", entry




# ---------------------------------------------------------------------------
# target resolution (D-08, D-21, D-24)
# ---------------------------------------------------------------------------


class InstallTarget(BaseModel):
    """One resolved destination: which runtime, which scope, which root."""

    model_config = ConfigDict(frozen=True)

    runtime: Literal["claude", "codex"]
    scope: Literal["global", "project"]
    root: Path

    def label(self) -> str:
        return f"{self.runtime}/{self.scope}"


def _claude_root(scope: str, project: Path) -> Path:
    return (Path.home() if scope == "global" else project) / ".claude" / "skills"


def _codex_root(scope: str, project: Path) -> Path:
    if scope != "global":
        return project / ".codex" / "skills"
    configured = os.environ.get(CODEX_HOME_ENV)
    home = Path(configured) if configured else Path.home() / ".codex"
    return home / "skills"


def resolve_targets(runtimes: Iterable[str], scope: str, project: Path) -> list[InstallTarget]:
    """One :class:`InstallTarget` per requested runtime.

    ``pathlib`` throughout so nothing is gratuitously POSIX-only — but D-24
    leaves Windows best-effort and explicitly unclaimed, and no test asserts it.
    """
    if scope not in SCOPES:
        raise ValueError(f"unknown scope {scope!r}; expected one of {SCOPES}")
    project = Path(project)
    targets: list[InstallTarget] = []
    for runtime in runtimes:
        if runtime == "claude":
            root = _claude_root(scope, project)
        elif runtime == "codex":
            root = _codex_root(scope, project)
        else:
            raise ValueError(f"unknown runtime {runtime!r}; expected one of {RUNTIMES}")
        targets.append(InstallTarget(runtime=runtime, scope=scope, root=root))
    return targets


def standard_targets(project: Path) -> list[InstallTarget]:
    """Every root in the standard set — both runtimes, both scopes.

    ``--sync`` (D-10's self-locating property) looks here for manifests rather
    than consulting a central registry, because there is no registry: an unknown
    number of project installs exist on any machine and a registry would drift
    from them silently.
    """
    targets: list[InstallTarget] = []
    for scope in SCOPES:
        targets.extend(resolve_targets(RUNTIMES, scope, project))
    return targets


# ---------------------------------------------------------------------------
# the path guard (T-01.2-05 / T-01.2-06, ASVS V4 + V5 + V12)
# ---------------------------------------------------------------------------






#: Whether this platform can anchor a mutation to a directory file descriptor.
#: When True — every platform GND claims (D-24) — :func:`_descend` walks the
#: destination one component at a time with ``O_NOFOLLOW`` and every mutation is
#: performed relative to the resulting descriptor, so the KERNEL enforces what
#: :func:`safe_destination` asserted. When False the module falls back to
#: re-running the guard immediately before each mutation, which is best-effort
#: only; ``tests/test_review_fixes.py`` asserts this reads True here so the
#: anchored path can never go quietly unused.





















# ---------------------------------------------------------------------------
# manifest (D-10, D-23)
# ---------------------------------------------------------------------------


class ManifestFile(BaseModel):
    """One placed asset. ``size`` is redundant with the digest but makes a
    truncated file diagnosable at a glance."""

    model_config = ConfigDict(extra="forbid")

    sha256: str
    size: int


class ManifestSkill(BaseModel):
    model_config = ConfigDict(extra="forbid")

    files: dict[str, ManifestFile] = Field(default_factory=dict)
    #: Exact value passed to ``symlink(2)`` for this skill. ``None`` is accepted
    #: only to read schema-1 receipts; without the value, ownership of a link
    #: cannot be re-established safely.
    link_value: str | None = None


class Manifest(BaseModel):
    """``<target-root>/.gnd-install.json``.

    Paths are always relative and always POSIX-separated, so the file is readable
    on the machine that wrote it and diffable across platforms. ``installed_at``
    records when the recorded CONTENT was last placed, not when ``install`` last
    ran — see :func:`apply` for why that distinction is load-bearing for D-09.
    """

    model_config = ConfigDict(extra="forbid", populate_by_name=True)

    schema_version: int = Field(default=MANIFEST_SCHEMA, alias="schema")
    framework: str
    version: str
    installed_at: str
    mode: Literal["copy", "symlink"]
    runtime: str
    scope: str
    #: Only ever ``STATUS_COMPLETE`` on the write side. Typed as a free string on
    #: the read side so a manifest another version wrote is *reported*, not a
    #: crash.
    status: str
    skills: dict[str, ManifestSkill] = Field(default_factory=dict)

    def link_entries(self) -> list[str]:
        """Recorded skill names, validated. The artifact set in ``symlink`` mode."""
        names: list[str] = []
        for skill in self.skills:
            _reject_unsafe_relpath(skill, source=f"manifest skill name '{skill}'")
            if "/" in skill or "\\" in skill:
                raise InstallPathError(
                    f"manifest skill name '{skill}' contains a path separator; skill "
                    f"names are single directory names at the target root."
                )
            names.append(skill)
        return names

    def file_entries(self) -> dict[str, ManifestFile]:
        """Recorded relpaths flattened to ``<skill>/<rest>``, every one validated.

        This is where an untrusted manifest is refused rather than classified: a
        crafted entry becomes an :class:`InstallPathError` naming the offender
        before it can become a destination.
        """
        entries: dict[str, ManifestFile] = {}
        for skill in self.link_entries():
            for rel, record in self.skills[skill].files.items():
                full = f"{skill}/{rel}"
                _reject_unsafe_relpath(full, source=f"manifest entry '{full}'")
                entries[full] = record
        return entries


def read_manifest(root: Path) -> Manifest | None:
    """The manifest at ``root``, or ``None`` when there is none.

    ``None`` is the partial-install signal of D-23 as much as it is "never
    installed" — the two are told apart by whether any placed file is present,
    which is what :func:`plan` reports.
    """
    path = Path(root) / MANIFEST_NAME
    if path.is_symlink():
        raise ManifestError(
            f"{path} is a symlink; the install receipt must be a regular file at the "
            f"root it describes (D-10)."
        )
    if not path.is_file():
        return None
    # WR-04: bound the receipt before parsing it, like every other untrusted
    # loader in this package. This module's own prose calls the receipt "a JSON
    # file sitting in a user-writable directory" and "untrusted input in exactly
    # the sense the model documents are" — and it was the only such loader
    # without a cap, so a large or deeply-nested document stalled or OOM'd every
    # lifecycle command BEFORE any guard ran.
    size = path.stat().st_size
    if size > MAX_MANIFEST_BYTES:
        raise ManifestError(
            f"{path} is {size} bytes, exceeding the {MAX_MANIFEST_BYTES}-byte cap "
            f"for an install receipt. A 29-file receipt is a few kilobytes; refusing "
            f"to parse this one rather than letting an untrusted document decide how "
            f"much memory and time the parser spends."
        )
    try:
        raw: Any = _rf7_input.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ManifestError(f"{path} could not be read as JSON: {error}") from error
    if not isinstance(raw, dict):
        raise ManifestError(f"{path} is not a JSON object")

    declared = raw.get("schema")
    if not isinstance(declared, int) or isinstance(declared, bool):
        raise ManifestError(f"{path} declares no integer 'schema' version")
    if declared > MANIFEST_SCHEMA:
        raise ManifestSchemaError(
            f"{path} declares schema {declared}; this build understands "
            f"{MANIFEST_SCHEMA}. Refusing to guess at a newer document — an "
            f"uninstall driven by a misread manifest deletes real files. Upgrade "
            f"with `uv tool upgrade {DISTRIBUTION}`."
        )
    try:
        manifest = Manifest.model_validate(raw)
    except ValidationError as error:
        raise ManifestError(f"{path} is not a valid schema-{declared} manifest: {error}") from error

    manifest.file_entries()  # validate every recorded path at the trust boundary
    return manifest


def write_manifest(root: Path, manifest: Manifest) -> Path:
    """Serialize the manifest through the same atomic writer every asset uses."""
    dest = safe_destination(Path(root), MANIFEST_NAME)
    payload = manifest.model_dump(by_alias=True)
    _atomic_write(
        Path(root),
        MANIFEST_NAME,
        (json.dumps(payload, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
    )
    return dest


# ---------------------------------------------------------------------------
# the classifier (D-11) — plan() performs NO writes
# ---------------------------------------------------------------------------


class SkillFileState(BaseModel):
    """Per-artifact classification record.

    Shaped after :class:`gnd.model.ValidationIssue` — the project's single
    structured-record vocabulary — so a future JSON payload is consistent at zero
    extra cost. ``detail`` carries the reason a state was reached where the state
    alone is ambiguous (a dangling symlink is ``missing``, but only the detail
    says why).
    """

    model_config = ConfigDict(extra="forbid")

    relpath: str
    state: Literal["create", "current", "stale", "missing", "modified", "collided"]
    detail: str = ""


class ApplyResult(BaseModel):
    """What :func:`apply` did, in numbers a test can assert on."""

    model_config = ConfigDict(extra="forbid")

    #: Placed skill assets only. The manifest is NOT counted here — it is
    #: installer metadata, and D-09 asks about the assets.
    writes: int = 0
    written: list[str] = Field(default_factory=list)
    #: Records apply deliberately did not act on: ``modified`` (never destroy a
    #: user edit), ``collided`` without force, and orphans whose bytes no longer
    #: match what GND placed.
    skipped: list[SkillFileState] = Field(default_factory=list)
    #: Orphans removed: recorded by the receipt, byte-identical to what GND
    #: placed, and no longer shipped by this version. Without this, install
    #: could never converge with doctor after an upgrade that drops a file
    #: (CR-04). Counted separately from ``writes`` so D-09's zero-write
    #: idempotence claim keeps meaning exactly what it meant.
    pruned: list[str] = Field(default_factory=list)
    #: Collisions that BLOCKED a write. Empty under ``force``.
    collisions: list[str] = Field(default_factory=list)
    manifest_written: bool = False
    manifest: Manifest | None = None


def _skill_of(relpath: str) -> tuple[str, str]:
    head, _, rest = relpath.partition("/")
    if not rest:
        raise InstallError(
            f"'{relpath}' sits directly at the skills root. Every packaged asset must "
            f"live under a skill directory, because the manifest is skill-keyed and "
            f"both runtimes discover skills as directories."
        )
    return head, rest


def _classify_file(
    root: Path,
    relpath: str,
    packaged_digest: str | None,
    recorded: ManifestFile | None,
    *,
    interrupted: bool = False,
) -> SkillFileState:
    dest = root.joinpath(*PurePosixPath(relpath).parts)
    try:
        info: os.stat_result | None = dest.lstat()
    except (OSError, ValueError):
        info = None
    is_link = info is not None and stat.S_ISLNK(info.st_mode)

    if info is None:
        if recorded is None:
            return SkillFileState(relpath=relpath, state="create")
        return SkillFileState(
            relpath=relpath, state="missing", detail="recorded by the manifest but absent on disk"
        )

    if is_link:
        # Never opened for writing and never read through (T-01.2-06). Ownership
        # is decided by manifest provenance alone, so an UNRECORDED planted link
        # is still `collided` — the traversal guard is not weakened by this.
        if recorded is None:
            return SkillFileState(
                relpath=relpath,
                state="collided",
                detail="a symlink stands here and no manifest records it",
            )
        return SkillFileState(
            relpath=relpath,
            state="modified",
            detail="a symlink stands where the manifest records a regular file",
        )

    # WR-03: everything that is not a REGULAR file is classified from its stat
    # alone and never opened. The classifier used to rule out symlinks and
    # directories and then read whatever was left — so a FIFO at a GND relpath
    # blocked `open()` forever, with no timeout and no output, in `plan()`, which
    # every one of install / doctor / uninstall routes through. A directory is
    # folded into the same test rather than kept as its own branch, because the
    # branch that mattered was the one nobody enumerated.
    if not stat.S_ISREG(info.st_mode):
        kind = "a directory" if stat.S_ISDIR(info.st_mode) else "a non-regular file"
        return SkillFileState(
            relpath=relpath,
            state="collided" if recorded is None else "modified",
            detail=(
                f"{kind} (mode {stat.filemode(info.st_mode)}) stands where a file "
                f"belongs; it was classified from its type and never opened"
            ),
        )
    if info.st_size > MAX_CLASSIFY_BYTES:
        return SkillFileState(
            relpath=relpath,
            state="collided" if recorded is None else "modified",
            detail=(
                f"{info.st_size} bytes exceeds the {MAX_CLASSIFY_BYTES}-byte cap for "
                f"reading an untrusted file at a GND relpath, so it was not hashed"
            ),
        )

    have = _sha256(dest.read_bytes())
    if recorded is None:
        return SkillFileState(
            relpath=relpath,
            state="collided",
            detail="present on disk and not recorded by any manifest — GND did not place it",
        )
    if have != recorded.sha256:
        if interrupted and packaged_digest is not None and have == packaged_digest:
            # Atomic replacement leaves either the recorded bytes or the complete
            # incoming bytes. Seeing the latter means this leaf was placed before
            # the interrupted run stopped; only the receipt still needs repair.
            return SkillFileState(
                relpath=relpath,
                state="current",
                detail=(
                    "matches the incoming package after an interrupted install; "
                    "repairing the receipt does not rewrite it"
                ),
            )
        return SkillFileState(
            relpath=relpath,
            state="modified",
            detail=(
                "matches neither the receipt nor the incoming package — treated as "
                "a user edit and never rewritten"
                if interrupted
                else "edited since GND placed it — never rewritten"
            ),
        )
    if packaged_digest is None:
        return SkillFileState(
            relpath=relpath,
            state="modified",
            detail=(
                "recorded only by the untrusted receipt; this version does not ship "
                "it, so the receipt alone cannot prove GND ownership"
            ),
        )
    if have == packaged_digest:
        return SkillFileState(relpath=relpath, state="current")
    return SkillFileState(
        relpath=relpath, state="stale", detail="matches the manifest; the package moved on"
    )


def _classify_link(
    root: Path,
    name: str,
    packaged: dict[str, bytes] | None,
    recorded: ManifestSkill | None,
) -> SkillFileState:
    """Classify a ``--symlink`` install at LINK granularity.

    A symlink-mode install records the placed *link* as the artifact, so this
    never walks per-file destinations through a link the manifest itself
    recorded. Doing so would classify GND's own placement as an intrusion, and
    ``gnd doctor --project`` at this repository's root — a symlink install, per
    the lifecycle plan's dogfood — could never exit 0.
    """
    link = root / name
    if not link.is_symlink():
        if not link.exists():
            if recorded is None:
                return SkillFileState(relpath=name, state="create")
            return SkillFileState(
                relpath=name, state="missing", detail="recorded symlink is absent"
            )
        return SkillFileState(
            relpath=name,
            state="collided" if recorded is None else "modified",
            detail="a regular directory stands where a symlink belongs",
        )

    if recorded is None:
        return SkillFileState(
            relpath=name,
            state="collided",
            detail="an unrecorded symlink stands where GND would place one",
        )
    current_value = os.readlink(link)
    if recorded.link_value is None:
        return SkillFileState(
            relpath=name,
            state="modified",
            detail="the legacy receipt does not record the exact link value GND placed",
        )
    if current_value != recorded.link_value:
        return SkillFileState(
            relpath=name,
            state="modified",
            detail=(
                f"symlink retargeted from {recorded.link_value!r} to {current_value!r} — "
                "never replaced or removed"
            ),
        )
    if not link.exists():
        return SkillFileState(
            relpath=name,
            state="missing",
            detail=(
                f"dangling symlink -> {current_value}. A tool environment is "
                f"rebuilt on upgrade and removed on uninstall, so a link into one "
                f"dangles after an interpreter-version change or an uninstall (D-20)."
            ),
        )
    if packaged is None:
        return SkillFileState(
            relpath=name,
            state="modified",
            detail=(
                "recorded only by the untrusted receipt; this version does not ship "
                "that skill, so the receipt alone cannot prove GND ownership"
            ),
        )
    for rel, want in packaged.items():
        behind = link.joinpath(*PurePosixPath(rel).parts)
        if not behind.is_file():
            return SkillFileState(
                relpath=name,
                state="missing",
                detail=f"the link resolves but {rel} is not behind it",
            )
        if behind.read_bytes() != want:
            return SkillFileState(
                relpath=name, state="stale", detail=f"the bytes behind the link differ at {rel}"
            )
    return SkillFileState(relpath=name, state="current")


def _packaged_index(skills_root: Traversable) -> dict[str, Traversable]:
    """Validated ``relpath -> resource`` for the whole packaged tree.

    Validation happens here so a hostile relpath is refused once, at the seam
    where the packaged tree becomes destination strings, rather than at each of
    the several places that consume it.
    """
    index: dict[str, Traversable] = {}
    for rel, resource in iter_skill_files(skills_root):
        _reject_unsafe_relpath(rel, source=f"packaged skill tree entry '{rel}'")
        _skill_of(rel)
        index[rel] = resource
    return index


def plan(
    skills_root: Traversable,
    target: InstallTarget,
    manifest: Manifest | None = None,
    *,
    mode: str = "copy",
) -> list[SkillFileState]:
    """Classify every GND-owned artifact at ``target.root``. Writes nothing.

    **The enumerated set is the union of two closed lists** — the relative paths
    the packaged tree yields, and the relative paths the manifest at this root
    records. Nothing else is ever classified, and the target root is never walked
    looking for work. Every relpath in both lists is GND-owned by construction:
    the packaged list is the tree GND ships, and the manifest list is the record
    of what GND itself placed.

    **The manifest file is never classified.** It is installer metadata, not a
    placed asset; it is not a packaged relpath and it never appears as one of its
    own entries, so the union rule already excludes it. Said out loud here
    because a later "let's also check the manifest is intact" change is exactly
    how this regresses.

    **A name collision on a name GND owns is still a collision.** If
    ``gnd-orm-core/SKILL.md`` exists and no manifest records it, that is
    ``collided`` and D-09's never-overwrite rule applies, whether it arrived from
    a crashed install, a hand copy, or something else.

    ``mode`` selects the granularity of the packaged side: ``copy`` enumerates
    files, ``symlink`` enumerates skill directories. The manifest side always
    uses ITS OWN recorded mode, so a mode switch surfaces the previously-placed
    artifacts as still-owned rather than vanishing. When the two disagree the
    caller should refuse the switch (``cli._cmd_install`` does) — this function
    reports rather than decides.
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
    root = Path(target.root)
    packaged = _packaged_index(skills_root)

    packaged_by_skill: dict[str, dict[str, bytes]] = {}
    if mode == "symlink":
        for rel, resource in packaged.items():
            skill, rest = _skill_of(rel)
            packaged_by_skill.setdefault(skill, {})[rest] = resource.read_bytes()

    recorded_files: dict[str, ManifestFile] = {}
    recorded_skills: dict[str, ManifestSkill] = {}
    # WR-02: a receipt that does not say `complete` records an install that
    # never finished, so a hash mismatch under it is GND's own half-written file.
    interrupted = manifest is not None and manifest.status != STATUS_COMPLETE
    manifest_mode = manifest.mode if manifest is not None else mode
    if manifest is not None:
        if manifest.mode == "symlink":
            recorded_skills = {name: manifest.skills[name] for name in manifest.link_entries()}
        else:
            recorded_files = manifest.file_entries()

    # Ordered, de-duplicated union of the two closed lists.
    artifacts: dict[tuple[str, str], None] = {}
    if mode == "symlink":
        for skill in sorted(packaged_by_skill):
            artifacts[("link", skill)] = None
    else:
        for rel in packaged:
            artifacts[("file", rel)] = None
    if manifest_mode == "symlink":
        for name in recorded_skills:
            artifacts[("link", name)] = None
    else:
        for rel in recorded_files:
            artifacts[("file", rel)] = None

    digests: dict[str, str] = {}

    def packaged_digest(rel: str) -> str | None:
        resource = packaged.get(rel)
        if resource is None:
            return None
        if rel not in digests:
            digests[rel] = _sha256(resource.read_bytes())
        return digests[rel]

    records: list[SkillFileState] = []
    for granularity, key in artifacts:
        if granularity == "link":
            records.append(
                _classify_link(root, key, packaged_by_skill.get(key), recorded_skills.get(key))
            )
        else:
            records.append(
                _classify_file(
                    root,
                    key,
                    packaged_digest(key),
                    recorded_files.get(key),
                    interrupted=interrupted,
                )
            )
    return records


# ---------------------------------------------------------------------------
# apply (D-09, D-23)
# ---------------------------------------------------------------------------


def _link_target(skills_root: Traversable, name: str) -> Path:
    """The real filesystem directory a ``--symlink`` install points at.

    Obtained by TYPE-CHECKING the resource handle rather than coercing it: the
    filesystem-path coercion of a ``Traversable`` raises under zipimport (D-19),
    so the honest move is to detect that the distribution is not unpacked and say
    so, rather than to try the coercion and interpret its exception.
    """
    entry = skills_root / name
    if not isinstance(entry, Path):
        raise InstallError(
            "--symlink needs a real filesystem path for the link target, and this "
            "distribution is not unpacked (the packaged skill tree is not a "
            f"pathlib.Path but a {type(entry).__name__}). Use the default copy mode."
        )
    return entry.resolve()


def _place_symlink(
    root: Path,
    relpath: str,
    points_at: Path,
    *,
    relative: bool,
    expected: LeafIdentity | None = None,
) -> None:
    """Create or replace the link at ``root / relpath``.

    Project-scope links are written RELATIVE to the link's own directory so a
    repository's checked-in links stay machine-independent; user-scope links are
    written absolute, because a relative path from the user's home skills
    directory into a tool environment is long, fragile, and breaks the moment
    either end moves. The asymmetry is deliberate.

    Anchored to a descriptor like every other mutation here (CR-01).

    **Both sides of the relative form are resolved (CR-02).** ``points_at`` comes
    back from :func:`_link_target` fully symlink-resolved, and
    ``os.path.relpath`` is pure lexical arithmetic on two strings — so
    relativising it against an UNRESOLVED link directory produces the wrong
    ``..`` count wherever a symlink on the link's own path changes that path's
    depth, and the link lands nowhere. The kernel resolves ``..`` against the
    real directory tree, never against the lexical path the caller used, so the
    link directory's resolved path is the only correct base.

    **The placement is then verified.** ``os.symlink`` returning says nothing
    about whether the link resolves, and reporting ``placed N file(s)`` over
    links that point at nothing is a success claim about work not done.
    """
    posix = _reject_unsafe_relpath(relpath, source="install destination")
    name = posix.parts[-1]
    link = Path(root).joinpath(*posix.parts)
    base = link.parent.resolve()
    value = os.path.relpath(points_at, start=base) if relative else str(points_at)
    if link.exists() and not link.is_symlink():
        raise InstallError(
            f"{link} is a real directory, not a symlink GND placed. Refusing to remove "
            f"it — move it aside and re-run."
        )
    if not ANCHORED_MUTATION:  # pragma: no cover - POSIX is the claimed platform
        safe_destination(root, relpath)  # best-effort: re-check immediately before the act
        staging_path = link.parent / f".gnd-tmp-link-{name}"
        with suppress(FileNotFoundError):
            staging_path.unlink()
        os.symlink(value, staging_path, target_is_directory=True)
        try:
            os.replace(staging_path, link)
        except BaseException:
            with suppress(OSError):
                staging_path.unlink()
            raise
        _assert_link_resolves(link, value)
        return

    fd = _descend(root, posix.parts[:-1], create=True)
    try:
        staging = _temp_name()
        with suppress(FileNotFoundError):
            os.unlink(staging, dir_fd=fd)
        os.symlink(value, staging, target_is_directory=True, dir_fd=fd)
        try:
            _replace_staged_leaf(fd, staging, name, expected)
        except BaseException:
            with suppress(OSError):
                os.unlink(staging, dir_fd=fd)
            raise
    finally:
        os.close(fd)
    _assert_link_resolves(link, value)


def _assert_link_resolves(link: Path, value: str) -> None:
    """Refuse to report a placement that landed nowhere (CR-02).

    Kept as its own seam so the check is visible at every call site and cannot be
    lost inside a branch. Removing it turns "placed N file(s)" back into a claim
    about ``os.symlink`` returning rather than about the filesystem.
    """
    if not link.exists():
        raise InstallError(
            f"{link} -> {value} does not resolve. Refusing to report a placement "
            f"that landed nowhere: a dangling link is discovered by neither runtime, "
            f"and a receipt written over it would claim assets nothing can reach."
        )


def _timestamp() -> str:
    return datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _build_skills_map(entries: dict[str, ManifestFile]) -> dict[str, ManifestSkill]:
    skills: dict[str, ManifestSkill] = {}
    for rel in sorted(entries):
        skill, rest = _skill_of(rel)
        skills.setdefault(skill, ManifestSkill()).files[rest] = entries[rel]
    return skills


def apply(
    skills_root: Traversable,
    target: InstallTarget,
    records: list[SkillFileState],
    *,
    mode: str = "copy",
    force: bool = False,
    manifest: Manifest | None = None,
) -> ApplyResult:
    """Write only the deltas ``records`` names, then the manifest, last.

    **Install is all-or-nothing per target.** Every destination is validated
    through :func:`safe_destination` and every source byte read BEFORE the first
    write, so an escaping relpath raises before any filesystem call rather than
    after a partial placement. The cross-skill links are sibling-relative by
    design (D-07) and only co-location makes them true, so a partial skill set
    would leave 37 links and the bundled validator's schema lookup pointing
    nowhere — which is also why there is no per-skill selection flag.

    ``modified`` is never written (D-11). ``collided`` is skipped and reported
    unless ``force``, in which case the file is replaced and adopted into the
    manifest.

    **Install prunes its own withdrawn files (CR-04).** An orphan — a relpath
    the receipt records that this version no longer ships — is deleted when its
    bytes still hash to what GND placed, and dropped from the rewritten receipt.
    "Install never deletes" sounds safer than it is: without this, an upgrade
    that retires a file left that file live in the agent's skills directory and
    still claimed by the receipt, permanently, with ``install`` exiting 0
    "already current" and ``doctor`` exiting 10 forever and no command able to
    reconcile them. The gate is :data:`REMOVABLE_STATES`, the same content
    identity ``uninstall`` uses, so install can only remove what uninstall would
    have been allowed to remove; an orphan the user edited is ``modified``, is
    not writable, and is never touched.

    The manifest is written **last** and only when something changed. Writing it
    unconditionally would refresh ``installed_at`` on a no-op run and make D-09's
    "byte-identical" claim false by construction; ``installed_at`` therefore
    means "when the recorded content was last placed".
    """
    if mode not in MODES:
        raise ValueError(f"unknown mode {mode!r}; expected one of {MODES}")
    root = Path(target.root)
    packaged = _packaged_index(skills_root)
    by_relpath = {record.relpath: record for record in records}

    previous_files: dict[str, ManifestFile] = {}
    previous_skills: dict[str, ManifestSkill] = {}
    if manifest is not None:
        if manifest.mode == "symlink":
            previous_skills = {name: manifest.skills[name] for name in manifest.link_entries()}
        else:
            previous_files = manifest.file_entries()

    packaged_by_skill: dict[str, dict[str, bytes]] = {}
    for rel, resource in packaged.items():
        skill, rest = _skill_of(rel)
        packaged_by_skill.setdefault(skill, {})[rest] = resource.read_bytes()

    available = set(packaged) if mode == "copy" else set(packaged_by_skill)

    actionable: list[SkillFileState] = []
    skipped: list[SkillFileState] = []
    prunable: list[str] = []
    disowned: set[str] = set()
    collisions: list[str] = []
    for record in records:
        writable = record.state in WRITABLE_STATES or (record.state == "collided" and force)
        if not writable:
            if record.state != "current":
                skipped.append(record)
            if record.state == "collided":
                collisions.append(record.relpath)
            continue
        if record.relpath not in available:
            # An ORPHAN: the receipt records it and this version no longer ships
            # it. Skipping it used to be the whole story, and the result was a
            # drift state install could not repair — exit 0 "already current"
            # forever against doctor's exit 10 forever, with the withdrawn file
            # left live in the agent's skills directory and still claimed by the
            # receipt (CR-04). It is pruned instead, gated on REMOVABLE_STATES,
            # which is the same content-identity gate `uninstall` uses: install
            # may only remove what uninstall would have been allowed to remove.
            # A `modified` orphan never reaches here at all — it is not writable
            # — so a user edit is still untouchable (D-11).
            if record.state in REMOVABLE_STATES:
                prunable.append(record.relpath)
                disowned.add(record.relpath)
            elif record.state == "missing":
                # Recorded, already gone, no longer shipped. Nothing to delete;
                # the only repair is to stop claiming it.
                disowned.add(record.relpath)
            else:  # pragma: no cover - unreachable while WRITABLE_STATES holds
                skipped.append(record)
            continue
        actionable.append(record)

    # Phase 1 — validate EVERY destination before touching the filesystem, so an
    # escaping relpath raises before any filesystem call and install stays
    # all-or-nothing per target. The RESULT is deliberately discarded: Phase 2
    # re-derives each destination from the descriptor it opens, because carrying
    # a resolved Path across this window is what made the guard bypassable
    # (CR-01). This pass exists for the diagnostic and the ordering, not as the
    # containment control.
    for record in actionable:
        safe_destination(root, record.relpath)
    for rel in prunable:
        safe_destination(root, rel)
    contents: dict[str, bytes] = {}
    link_targets: dict[str, Path] = {}
    if mode == "copy":
        contents = {record.relpath: packaged[record.relpath].read_bytes() for record in actionable}
    else:
        link_targets = {
            record.relpath: _link_target(skills_root, record.relpath) for record in actionable
        }

    # Phase 1b — mark an UPGRADE as in progress before touching any file (WR-02).
    # Only when a previous COMPLETE receipt exists and there is real work to do:
    # on a first install the receipt's absence is still the partial-install
    # signal (D-23) and writing one here would let it claim files not yet placed,
    # and on a no-op run this costs nothing, so D-09 is unaffected. The map
    # carried is the PREVIOUS one, so this receipt claims exactly what the last
    # completed run placed and not one file more.
    if manifest is not None and manifest.status == STATUS_COMPLETE and (actionable or prunable):
        root.mkdir(parents=True, exist_ok=True)
        write_manifest(root, manifest.model_copy(update={"status": STATUS_IN_PROGRESS}))

    # Phase 2 — write. Every mutation is anchored to a directory descriptor
    # opened O_NOFOLLOW (CR-01): the Phase 1 validation above is what produces a
    # good diagnostic, but it is the kernel that enforces containment at the
    # moment of the act, so a symlink planted inside this window raises rather
    # than redirects.
    root.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for record in actionable:
        if mode == "copy":
            expected = None
            if record.state in {"create", "missing"}:
                expected = LeafIdentity(kind="absent")
            elif record.state == "stale" and record.relpath in previous_files:
                expected = LeafIdentity(
                    kind="file", sha256=previous_files[record.relpath].sha256
                )
            _atomic_write(
                root,
                record.relpath,
                contents[record.relpath],
                expected=expected,
            )
        else:
            expected = None
            previous = previous_skills.get(record.relpath)
            if record.state == "create" or (
                record.state == "missing" and "dangling symlink" not in record.detail
            ):
                expected = LeafIdentity(kind="absent")
            elif previous is not None and previous.link_value is not None:
                expected = LeafIdentity(kind="symlink", link_value=previous.link_value)
            _place_symlink(
                root,
                record.relpath,
                link_targets[record.relpath],
                relative=target.scope == "project",
                expected=expected,
            )
        written.append(record.relpath)

    # Phase 2b — prune the orphans, then the directories they emptied. Same
    # anchored seam as every other mutation, and the pruning of empty parents is
    # `rmdir`-enforced, so a directory still holding a retained file survives
    # without any explicit check.
    pruned: list[str] = []
    for rel in prunable:
        _unlink(root, rel)
        pruned.append(rel)
    for rel in pruned:
        _prune_empty_parents(root, rel)

    # Phase 3 — the manifest, last (D-23).
    written_set = set(written)
    if mode == "copy":
        owned: dict[str, ManifestFile] = {}
        for rel in packaged:
            record = by_relpath.get(rel)
            if rel in written_set:
                data = contents[rel]
                owned[rel] = ManifestFile(sha256=_sha256(data), size=len(data))
            elif record is not None and record.state == "current":
                data = packaged[rel].read_bytes()
                owned[rel] = ManifestFile(sha256=_sha256(data), size=len(data))
            elif record is not None and record.state == "modified" and rel in previous_files:
                # Carry the digest GND PLACED forward, never the user's edit —
                # otherwise a later `uninstall` would hash-match the edit and
                # delete it, which is exactly what D-11 forbids.
                owned[rel] = previous_files[rel]
        for rel, entry in previous_files.items():
            record = by_relpath.get(rel)
            if rel in disowned:
                # Pruned, or already gone. Carrying it forward is what made the
                # drift permanent (CR-04).
                continue
            if rel not in packaged and record is not None and record.state != "collided":
                owned[rel] = entry
        skills_map = _build_skills_map(owned)
    else:
        skills_map = {}
        for name in sorted(packaged_by_skill):
            record = by_relpath.get(name)
            keep = name in written_set or (
                record is not None and record.state in {"current", "stale", "modified"}
            )
            if not keep:
                continue
            if record is not None and record.state == "modified" and name in previous_skills:
                skills_map[name] = previous_skills[name]
            else:
                skills_map[name] = ManifestSkill(
                    files={
                        rest: ManifestFile(sha256=_sha256(data), size=len(data))
                        for rest, data in sorted(packaged_by_skill[name].items())
                    },
                    link_value=os.readlink(root / name),
                )
        for name, entry in previous_skills.items():
            if name in disowned:
                continue
            if name not in packaged_by_skill and name not in skills_map:
                skills_map[name] = entry

    version = resolve_version()
    content_unchanged = manifest is not None and manifest.skills == skills_map
    unchanged = (
        manifest is not None
        and not written
        and not pruned
        and manifest.mode == mode
        and content_unchanged
        and manifest.status == STATUS_COMPLETE
        # WR-07: a version bump is a change to what the receipt CLAIMS, even when
        # no byte moved. Without this, `uv tool upgrade` to a release whose skill
        # bytes are identical left `version` at the old number and `gnd doctor`
        # kept printing it — the single fact an operator reads doctor to learn.
        and manifest.version == version
    )
    # F-01: a receipt is a claim of OWNERSHIP, and `unchanged` above cannot
    # express "there was nothing to claim". Its first conjunct is
    # `manifest is not None`, so the whole short-circuit collapsed to False
    # whenever no prior receipt existed — regardless of `written` and `pruned`
    # being empty — and a run over a root where EVERY record was `collided`
    # wrote `status: complete` with `skills: {}`. That document asserted an
    # install of this version, at a timestamp, at a root GND had never written a
    # byte to: `doctor` printed `installed (… placed <ts>)` for it, and in the
    # aliased-root case it replaced a receipt recording 29 real files, stranding
    # them beyond the reach of `uninstall`.
    #
    # This is deliberately NOT folded into `unchanged`. `unchanged` means "the
    # receipt on disk already says this"; this means "there is nothing to say".
    # A prior receipt is excluded because an existing claim must still be
    # rewritten when it is retracted — an install that prunes every file it
    # owned legitimately writes an empty skills map.
    establishes_nothing = manifest is None and not written and not pruned and not skills_map

    result_manifest = manifest
    manifest_written = False
    if not unchanged and not establishes_nothing:
        result_manifest = Manifest(
            schema=MANIFEST_SCHEMA,
            framework=DISTRIBUTION,
            version=version,
            # `installed_at` means "when the recorded CONTENT was last placed",
            # which is what makes D-09's byte-identity claim true. A rewrite
            # driven only by the version bump must therefore carry it forward
            # rather than restamp it.
            installed_at=(
                manifest.installed_at
                if (manifest is not None and content_unchanged and not written and not pruned)
                else _timestamp()
            ),
            mode=mode,
            runtime=target.runtime,
            scope=target.scope,
            status=STATUS_COMPLETE,
            skills=skills_map,
        )
        write_manifest(root, result_manifest)
        manifest_written = True

    return ApplyResult(
        writes=len(written),
        written=written,
        skipped=skipped,
        pruned=pruned,
        collisions=collisions,
        manifest_written=manifest_written,
        manifest=result_manifest,
    )


# ---------------------------------------------------------------------------
# diagnose (D-11, PKG-07) — the dry run doctor reports, writes NOTHING
# ---------------------------------------------------------------------------

#: The states that mean "GND placed this and it is no longer what GND placed".
#: ``collided`` is deliberately absent: it is a distinct outcome with its own
#: exit code, because nothing was destroyed and the repair is different.
DRIFT_STATES: frozenset[str] = frozenset({"stale", "missing", "modified"})


class TargetDiagnosis(BaseModel):
    """What one target root looks like right now.

    ``problem`` is non-empty only when the receipt could not be trusted. When it
    is set, ``states`` is empty **by construction** — refusing to interpret is
    always the safe direction, because the next command the user runs is likely
    to be the one that deletes.
    """

    model_config = ConfigDict(extra="forbid")

    target: InstallTarget
    #: True when a receipt exists at this root (readable or not), or when GND-owned
    #: assets are present without one — D-23's partial install is still an install.
    installed: bool = False
    mode: str = ""
    version: str = ""
    installed_at: str = ""
    skills: list[str] = Field(default_factory=list)
    states: list[SkillFileState] = Field(default_factory=list)
    problem: str = ""
    #: Named, never written. Codex only — see :data:`CODEX_ALTERNATE_DIR`.
    alternative_root: Path | None = None

    def counts(self) -> dict[str, int]:
        tally: dict[str, int] = {}
        for record in self.states:
            tally[record.state] = tally.get(record.state, 0) + 1
        return tally

    def has_collision(self) -> bool:
        return any(record.state == "collided" for record in self.states)

    def has_drift(self) -> bool:
        return bool(self.problem) or any(record.state in DRIFT_STATES for record in self.states)


class Shadowing(BaseModel):
    """A user-scope install of a skill name that a project-scope install also has.

    Runtime skill precedence is personal > project — the inverse of most people's
    intuition — so this is reported as its own diagnostic rather than folded into
    a state. A user who installs into a project and sees no effect is usually
    being shadowed by an earlier user-level install.
    """

    model_config = ConfigDict(extra="forbid")

    runtime: str
    skill: str
    shadowing_root: Path
    shadowed_root: Path


class DoctorReport(BaseModel):
    """Per-target diagnoses plus the two environment facts that explain most
    "it did not work" reports (Pitfalls 5 and 6)."""

    model_config = ConfigDict(extra="forbid")

    targets: list[TargetDiagnosis] = Field(default_factory=list)
    shadowing: list[Shadowing] = Field(default_factory=list)
    executable_dir: Path
    executable_on_path: bool

    def installed_anywhere(self) -> bool:
        return any(diagnosis.installed for diagnosis in self.targets)

    def has_collision(self) -> bool:
        return any(diagnosis.has_collision() for diagnosis in self.targets)

    def has_drift(self) -> bool:
        return any(diagnosis.has_drift() for diagnosis in self.targets)


def executable_directory() -> Path:
    """The directory the running ``gnd`` was **found in** — never where it points.

    ``uv tool install`` puts the console script in a bin directory that is NOT on
    the default macOS PATH, so a successful install followed by "command not
    found" is a common and confusing outcome (Pitfall 5). ``sys.argv[0]`` is the
    console script itself on the supported path; the interpreter's directory is
    the honest answer under ``python -m gnd``, which is a development
    convenience rather than the documented entry point (D-03).

    **The directory is resolved; the executable is not** (F-02). Every branch
    below takes ``.parent`` *before* ``.resolve()``, and reversing the two is the
    whole of the defect this docstring exists to prevent recurring. ``uv tool
    install`` writes a SYMLINK at the bin directory — ``~/.local/bin/gnd``, the
    thing on PATH — pointing into the tool environment's private
    ``…/tools/<name>/bin/gnd``, which uv deliberately never puts on PATH.
    ``.resolve().parent`` followed that link and answered about its target, so
    the one diagnostic PKG-04 offers against uv's most common pitfall inverted on
    uv's own default layout: a user who had followed the README exactly was told
    their executable directory was NOT on PATH, and instructed to run
    ``uv tool update-shell`` in the same session in which ``gnd`` had just been
    found on PATH. A venv's ``bin/python`` is a symlink to the real interpreter
    for the same reason, so the ``sys.executable`` fallback needs the same
    ordering.

    The question this answers is "is the directory PATH must contain on PATH?",
    and that is by definition the directory holding the name the shell resolved.
    Reporting the link's target instead would additionally print a path the user
    must NOT add to PATH.
    """
    argv0 = sys.argv[0] if sys.argv else ""
    if argv0:
        candidate = Path(argv0)
        # A bare `gnd` with no separator would make `.parent` the CWD, which is
        # not where anything was found. Such an argv0 falls through to `which`.
        if candidate.name.startswith("gnd") and candidate.parent != Path(".") and candidate.exists():
            return candidate.parent.resolve()
    found = shutil.which("gnd")
    if found:
        return Path(found).parent.resolve()
    return Path(sys.executable).parent.resolve()


def directory_is_on_path(directory: Path, path_value: str | None = None) -> bool:
    """Whether ``directory`` appears in ``PATH``, compared as resolved paths.

    String comparison would report ``~/.local/bin`` and ``/Users/x/.local/bin``
    as different directories and turn the one diagnostic that explains "command
    not found" into a false alarm.
    """
    raw = os.environ.get("PATH", "") if path_value is None else path_value
    wanted = Path(directory).resolve()
    for entry in raw.split(os.pathsep):
        if not entry:
            continue
        try:
            if Path(entry).resolve() == wanted:
                return True
        except OSError:  # pragma: no cover - only on a broken filesystem
            continue
    return False


def _alternative_root(target: InstallTarget) -> Path | None:
    """The Codex location GND does not write, or ``None`` for other runtimes."""
    if target.runtime != "codex":
        return None
    return Path(target.root).parent.parent / CODEX_ALTERNATE_DIR / "skills"


def _placement_shape(skills_root: Traversable, root: Path) -> str:
    """The granularity a RECEIPT-LESS root was placed at (WR-01).

    Falling back to ``copy`` unconditionally was wrong for the single most
    common receipt-less shape there is: a fresh clone of this repository, whose
    four skill symlinks are git-tracked while the two receipts are gitignored.
    Every per-file path then resolved *through* the tracked link, so 29 files per
    root reported ``collided`` where 2 link-level collisions actually exist — and
    the 20-item cap elided the rest, leaving the operator with 20 lines of noise
    and no signal.

    **This does not walk the target root.** It asks one question per PACKAGED
    skill name — a closed list, exactly like :func:`plan`'s enumeration — so an
    unrelated occupant of a shared skills directory is still invisible here.

    ``copy`` remains the answer when no such link exists, which keeps D-23's
    partial install (regular files, no receipt) reported per file, as writing the
    receipt last exists to make possible.
    """
    for entry in skills_root.iterdir():
        if not entry.is_dir() or entry.name.casefold() in RESERVED_DIR_NAMES:
            continue
        if (root / entry.name).is_symlink():
            return "symlink"
    return "copy"


def _diagnose_target(skills_root: Traversable, target: InstallTarget) -> TargetDiagnosis:
    root = Path(target.root)
    alternative = _alternative_root(target)
    receipt = root / MANIFEST_NAME
    receipt_present = receipt.is_symlink() or receipt.exists()

    def refused(reason: str) -> TargetDiagnosis:
        return TargetDiagnosis(
            target=target, installed=True, problem=reason, alternative_root=alternative
        )

    try:
        manifest = read_manifest(root)
    except ManifestSchemaError as error:
        return refused(f"unreadable receipt: {error}")
    except InstallPathError as error:
        return refused(f"corrupt receipt: {error}")
    except (ManifestError, OSError) as error:
        return refused(f"corrupt receipt: {error}")

    mode = manifest.mode if manifest is not None else _placement_shape(skills_root, root)
    try:
        records = plan(skills_root, target, manifest, mode=mode)
    except InstallPathError as error:
        return refused(f"corrupt receipt: {error}")
    except (InstallError, OSError) as error:
        return refused(f"unreadable target: {error}")

    # `create` is a plan for the future, not a state of something placed. doctor
    # describes what IS there, so it is dropped rather than renamed.
    states = [record for record in records if record.state != "create"]
    return TargetDiagnosis(
        target=target,
        installed=manifest is not None or receipt_present or bool(states),
        mode=manifest.mode if manifest is not None else "",
        version=manifest.version if manifest is not None else "",
        installed_at=manifest.installed_at if manifest is not None else "",
        skills=sorted(manifest.skills) if manifest is not None else [],
        states=states,
        alternative_root=alternative,
    )


def _shadowing(diagnoses: list[TargetDiagnosis]) -> list[Shadowing]:
    by_scope: dict[tuple[str, str], TargetDiagnosis] = {}
    for diagnosis in diagnoses:
        if diagnosis.installed and diagnosis.skills:
            by_scope[(diagnosis.target.runtime, diagnosis.target.scope)] = diagnosis

    found: list[Shadowing] = []
    for runtime in RUNTIMES:
        above = by_scope.get((runtime, "global"))
        below = by_scope.get((runtime, "project"))
        if above is None or below is None:
            continue
        for skill in sorted(set(above.skills) & set(below.skills)):
            found.append(
                Shadowing(
                    runtime=runtime,
                    skill=skill,
                    shadowing_root=Path(above.target.root),
                    shadowed_root=Path(below.target.root),
                )
            )
    return found


def diagnose(skills_root: Traversable, targets: Iterable[InstallTarget]) -> DoctorReport:
    """Report the state of every GND-owned asset at every ``targets`` root.

    **Writes nothing, and adds no classifier.** Every state below comes from
    :func:`plan`, which is already a pure dry run — so ``doctor`` and ``install``
    can never disagree about what ``stale`` means. Three things are layered on
    top, none of which is classification:

    * ``create`` records are dropped, because doctor describes what *is* placed;
    * an untrusted receipt is refused wholesale rather than partly interpreted;
    * both scopes are compared for the shadowing relationship of :class:`Shadowing`.

    Dangling links need no special case here: a ``--symlink`` install records the
    placed link as the artifact, and :func:`_classify_link` already reports a link
    whose target has gone as ``missing`` with the reason — and the link's target —
    in its detail.
    """
    diagnoses = [_diagnose_target(skills_root, target) for target in targets]
    directory = executable_directory()
    return DoctorReport(
        targets=diagnoses,
        shadowing=_shadowing(diagnoses),
        executable_dir=directory,
        executable_on_path=directory_is_on_path(directory),
    )


# ---------------------------------------------------------------------------
# remove (D-11, PKG-07) — deletion gated on content identity
# ---------------------------------------------------------------------------

class RemoveResult(BaseModel):
    """What :func:`remove` did, in terms a report can name."""

    model_config = ConfigDict(extra="forbid")

    removed: list[str] = Field(default_factory=list)
    #: Left on disk on purpose: a user edit, or something GND never placed.
    #: Non-empty means the run must not report success.
    retained: list[SkillFileState] = Field(default_factory=list)
    #: Recorded, already gone before this run. Not a failure and not a removal.
    absent: list[str] = Field(default_factory=list)
    pruned: list[str] = Field(default_factory=list)
    manifest_removed: bool = False


def _unlink(
    root: Path,
    relpath: str,
    *,
    expected: LeafIdentity | None = None,
) -> None:
    """The single deletion seam, mirroring :func:`_atomic_write` on the write side.

    Every unlink in this module goes through here, so the ORDER of deletions is
    observable in one place — which is what lets "the receipt is removed last" be
    a tested property rather than a claim. Unlinking a symlink removes the link,
    never the file it points at.

    Takes ``root`` and a relative path, and anchors the unlink to a descriptor
    from :func:`_descend`, for the reason CR-01 gives there: a directory symlink
    planted after :func:`safe_destination` ran made this delete a file outside
    the target root.
    """
    posix = _reject_unsafe_relpath(relpath, source="install destination")
    if not ANCHORED_MUTATION:  # pragma: no cover - POSIX is the claimed platform
        safe_destination(root, relpath).unlink()  # best-effort: re-check before the act
        return
    fd = _descend(root, posix.parts[:-1], create=False)
    try:
        name = posix.parts[-1]
        if expected is None:
            os.unlink(name, dir_fd=fd)
            return
        staging = _temp_name()
        os.replace(name, staging, src_dir_fd=fd, dst_dir_fd=fd)
        try:
            if not _matches_leaf(fd, staging, expected):
                raise InstallError(
                    f"install destination '{relpath}' changed after planning; "
                    "restored it instead of deleting it"
                )
        except BaseException:
            os.replace(staging, name, src_dir_fd=fd, dst_dir_fd=fd)
            raise
        os.unlink(staging, dir_fd=fd)
    finally:
        os.close(fd)


def _prune_empty_parents(root: Path, relpath: str) -> list[str]:
    """Remove the directories ``relpath``'s deletion emptied, stopping at ``root``.

    ``rmdir`` refuses a non-empty directory, so a directory still holding a
    retained file survives without any explicit check — the filesystem enforces
    the rule that matters. Anchored like every other mutation (CR-01): each level
    is removed BY NAME relative to a descriptor for its own parent, so pruning
    can never climb out through a planted link.
    """
    posix = _reject_unsafe_relpath(relpath, source="install destination")
    parts = list(posix.parts[:-1])
    pruned: list[str] = []
    while parts:
        if not ANCHORED_MUTATION:  # pragma: no cover - POSIX is the claimed platform
            try:
                safe_destination(root, "/".join(parts)).rmdir()
            except (OSError, InstallPathError):
                break
        else:
            try:
                fd = _descend(root, tuple(parts[:-1]), create=False)
            except (OSError, InstallPathError):
                break
            try:
                os.rmdir(parts[-1], dir_fd=fd)
            except OSError:
                break
            finally:
                os.close(fd)
        pruned.append("/".join(parts))
        parts.pop()
    return pruned


def remove(
    skills_root: Traversable,
    target: InstallTarget,
    manifest: Manifest,
) -> RemoveResult:
    """Delete only what the manifest claims AND still owns. Two hard rules.

    **1. Deletion is gated on content identity, never on a filename or on the
    manifest's mere assertion.** A file is deleted only when its current bytes
    hash to what the manifest recorded — the ``current`` and ``stale`` states of
    :func:`plan`, which is reused here so removal and diagnosis can never disagree
    about what "unchanged" means. A file that no longer matches is a user edit:
    retained, reported, and carried into a non-zero exit by the caller. An
    uninstaller that deletes a user's edits is worse than one that leaves litter
    (D-11, T-01.2-16). A file the manifest never claimed is not GND's to delete at
    all.

    **2. Every path out of the manifest passes :func:`safe_destination` before any
    unlink, and one failure aborts the WHOLE removal for this root.** The manifest
    is JSON read back from a user-writable directory — untrusted input in exactly
    the sense the model documents are. The concrete attack this stops: a receipt
    naming ``../../../.ssh/id_rsa``. Do **not** relax this into "delete the
    well-formed entries and skip the bad one": a manifest containing one hostile
    entry is evidence the whole document is not to be trusted, and a
    partially-honoured hostile manifest is a successful attack (T-01.2-15). The
    same reasoning covers an unrecognised schema version — refuse rather than
    delete on a guess (T-01.2-17).

    **Ordering is a diagnosability contract**: files, then the directories those
    files emptied, then the receipt. Removing the receipt first would leave
    orphaned files a later ``doctor`` could only classify as unmanaged.

    **Symlink mode unlinks the placed link and never traverses into it.** The
    link's target is the installed distribution, so following it would delete the
    framework's own packaged skills (T-01.2-18). Unlinking a symlink cannot touch
    its target, which is why a *dangling* recorded link is removed too rather than
    left as litter.
    """
    root = Path(target.root)
    if manifest.schema_version > MANIFEST_SCHEMA:
        raise ManifestSchemaError(
            f"{root / MANIFEST_NAME} declares schema {manifest.schema_version}; this "
            f"build understands {MANIFEST_SCHEMA}. Refusing to delete anything on a "
            f"guess about a document written by a newer build."
        )

    symlink_mode = manifest.mode == "symlink"
    # Raises InstallPathError, naming the offender, before anything is deleted.
    recorded = set(manifest.link_entries() if symlink_mode else manifest.file_entries())

    records = plan(skills_root, target, manifest, mode=manifest.mode)
    packaged = _packaged_index(skills_root)

    # Phase 1 — validate EVERY recorded path, then decide. No filesystem
    # mutation has happened yet and none may until this loop has completed.
    destinations = {rel: safe_destination(root, rel) for rel in sorted(recorded)}
    manifest_destination = safe_destination(root, MANIFEST_NAME)

    deletable: list[str] = []
    retained: list[SkillFileState] = []
    absent: list[str] = []
    for record in records:
        if record.relpath not in recorded:
            # Never claimed by the receipt, so never ours to delete. `collided`
            # is reported; `create` is a path nothing has been placed at.
            if record.state == "collided":
                retained.append(record)
            continue
        if symlink_mode:
            # The artifact IS the link. `missing` here means the link dangles —
            # still a placed directory entry, and unlinking it cannot reach the
            # target that has gone.
            if destinations[record.relpath].is_symlink() and record.state in (
                REMOVABLE_STATES | {"missing"}
            ):
                deletable.append(record.relpath)
            elif record.state == "missing":
                absent.append(record.relpath)
            else:
                retained.append(record)
            continue
        if record.state in REMOVABLE_STATES:
            deletable.append(record.relpath)
        elif record.state == "missing":
            absent.append(record.relpath)
        else:
            retained.append(record)

    # Phase 2 — delete files, then the directories they emptied. Every unlink is
    # anchored to a directory descriptor opened O_NOFOLLOW (CR-01), so the Phase
    # 1 pass above supplies the diagnostic while the kernel supplies the
    # guarantee. A refusal here means an attacker raced the window and is raised,
    # not swallowed: the files already removed are GND's own, and stopping is
    # strictly safer than continuing through a filesystem that changed under us.
    removed: list[str] = []
    pruned: list[str] = []
    for rel in deletable:
        if symlink_mode:
            link_value = manifest.skills[rel].link_value
            expected = LeafIdentity(kind="symlink", link_value=link_value)
        else:
            record = next(item for item in records if item.relpath == rel)
            digest = manifest.file_entries()[rel].sha256
            if record.state == "current" and rel in packaged:
                digest = _sha256(packaged[rel].read_bytes())
            expected = LeafIdentity(kind="file", sha256=digest)
        _unlink(root, rel, expected=expected)
        removed.append(rel)
    for rel in removed:
        pruned.extend(_prune_empty_parents(root, rel))

    # Phase 3 — the receipt, last, and only when everything it claimed is gone.
    manifest_removed = False
    if not retained and manifest_destination.exists():
        _unlink(root, MANIFEST_NAME)
        manifest_removed = True

    return RemoveResult(
        removed=removed,
        retained=retained,
        absent=absent,
        pruned=sorted(set(pruned)),
        manifest_removed=manifest_removed,
    )
















