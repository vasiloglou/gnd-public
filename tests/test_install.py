"""Installer contract: the packaged tree walk, the path guard, plan, apply, manifest.

This is the project's first use of ``tmp_path``. Justifying the new affordance
the way ``tests/conftest.py`` justifies its one helper: ``src/gnd/install.py``
is the first module in the package that *writes*, so it is the first module
whose contract cannot be expressed by loading a fixture and asserting on the
returned object. Every assertion below about idempotence, collision, and
never-overwriting-what-GND-did-not-place is an assertion about the state of a
directory before and after a call. ``tmp_path`` is the only way to make those
observable without a test that can damage the developer's real
``~/.claude/skills``. No test here ever resolves a real user home; the two that
exercise ``resolve_targets`` redirect ``HOME``/``CODEX_HOME`` first.

The *source* side is deliberately NOT a fixture: every plan/apply test reads the
real packaged resource tree through ``files("gnd")``. A synthetic source tree
would prove the algorithm and not the thing D-04 asks for — that the installer
reads bytes out of the installed distribution.

``iter_skill_files`` is re-derived here as ``_walk`` rather than imported. The
production copy lives in ``install.py`` and a third copy lives in
``tests/test_packaged_skills.py``; keeping this one independent means a bug in
the production walk cannot hide behind the test that uses it.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path, PurePosixPath
from typing import Any, NamedTuple

import pytest
from support.digests import sha256_bytes as _digest

from gnd import cli, install

#: The packaged tree ships 48 files (measured, never derived — phase 02.1 took
#: it from 29 to 33 with the gnd-extract / gnd-render-doc round-trip pair, plan
#: 03-04 to 35 with gnd-codegen, plan 03-06 to 37 with gnd-conformance, and
#: Phase 4 to 43 with gnd-model-evolve, gnd-model-from-code and
#: gnd-review-panel, then the panel updater to 46; quick 260816-rjw to 48 with
#: the two loop skills, SKILL.md only each; milestone v1.2 to 50 with
#: gnd-new-project and the milestone-record contract reference).
#: Duplicated deliberately: if a skill file is added, BOTH guards should fail
#: and be updated as one decision.
EXPECTED_SKILL_FILE_COUNT = 65

#: The fifteen directory names the packaged tree carries. The installer discovers
#: them by traversal and never by name (D-06/D-26); this literal exists so a
#: test can say WHICH fourteen were placed, not so the installer can look them up.
EXPECTED_SKILL_NAMES = frozenset(
    {
        "gnd-adopt",
        "gnd-codegen",
        "gnd-conformance",
        "gnd-dev-session",
        "gnd-extract",
        "gnd-export",
        "gnd-model-evolve",
        "gnd-model-from-code",
        "gnd-model-from-text",
        "gnd-new-project",
        "gnd-orm-core",
        "gnd-render-doc",
        "gnd-review-panel",
        "gnd-review-panel-light",
        "gnd-solve",
        "gnd-update-review-panel",
    }
)

#: The top-level directory names GND owns inside a target root today. Discovered
#: at runtime by the installer per D-06 — named here only so the tests can build
#: a collision at a path GND *does* own, which is a different case from an
#: unrelated occupant of the same shared root.
SAMPLE_SKILL = "gnd-orm-core"
SAMPLE_FILE = "gnd-orm-core/SKILL.md"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _walk(root: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    """Independent Traversable walk — see the module docstring for why."""
    for entry in root.iterdir():
        name = entry.name
        if entry.is_dir():
            if name.casefold() == "synced":
                continue
            yield from _walk(entry, f"{prefix}{name}/")
        else:
            yield f"{prefix}{name}", entry


def _packaged_bytes() -> dict[str, bytes]:
    return {rel: res.read_bytes() for rel, res in _walk(install.packaged_skills_root())}


def _snapshot(root: Path) -> dict[str, str]:
    """Every file under ``root`` (symlinks recorded by their target string)."""
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[rel] = f"symlink->{os.readlink(path)}"
        elif path.is_file():
            snapshot[rel] = _digest(path.read_bytes())
    return snapshot


def _target(root: Path, runtime: str = "claude", scope: str = "project") -> Any:
    return install.InstallTarget(runtime=runtime, scope=scope, root=root)


def _install(
    root: Path,
    *,
    mode: str = "copy",
    force: bool = False,
    runtime: str = "claude",
    scope: str = "project",
) -> tuple[list[Any], Any]:
    """One full plan+apply cycle against the real packaged tree."""
    skills = install.packaged_skills_root()
    target = _target(root, runtime, scope)
    manifest = install.read_manifest(root)
    records = install.plan(skills, target, manifest, mode=mode)
    result = install.apply(skills, target, records, mode=mode, force=force, manifest=manifest)
    return records, result


def _states(records: list[Any]) -> dict[str, str]:
    return {record.relpath: record.state for record in records}


def _gnd_argv() -> list[str]:
    """Prefer the console script PKG-01 delivers; never skip if it is absent.

    A ``pytest.skip`` here would let every subprocess-level acceptance criterion
    pass vacuously outside ``uv run``, so the module-execution path is used as a
    fallback instead. Both reach the same ``main()`` and the same exit codes.
    """
    executable = shutil.which("gnd")
    return [executable] if executable else [sys.executable, "-m", "gnd"]


def _run_gnd(args: list[str], cwd: Path, **env: str) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment.pop(install.CODEX_HOME_ENV, None)
    environment.update(env)
    return subprocess.run(
        [*_gnd_argv(), *args],
        cwd=cwd,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )


def _collisions(records: list[Any]) -> list[str]:
    return [record.relpath for record in records if record.state == "collided"]


# --------------------------------------------------------------------------
# the packaged tree walk (D-19)
# --------------------------------------------------------------------------


def test_packaged_skills_root_is_a_directory() -> None:
    root = install.packaged_skills_root()
    assert root.is_dir(), (
        "packaged_skills_root() must return the Traversable for gnd/skills; the "
        "installer reads every byte from the installed distribution (D-04)."
    )


def test_iter_skill_files_yields_every_packaged_file() -> None:
    found = sorted(rel for rel, _ in install.iter_skill_files(install.packaged_skills_root()))
    assert len(found) == EXPECTED_SKILL_FILE_COUNT, (
        f"iter_skill_files yielded {len(found)} entries, expected "
        f"{EXPECTED_SKILL_FILE_COUNT}. A partial walk installs a partial skill "
        f"set, and the 37 cross-skill links only resolve when the set is whole "
        f"(Pitfall 7). Found:\n  " + "\n  ".join(found)
    )


def test_iter_skill_files_agrees_with_an_independent_walk() -> None:
    root = install.packaged_skills_root()
    production = sorted(rel for rel, _ in install.iter_skill_files(root))
    independent = sorted(rel for rel, _ in _walk(root))
    assert production == independent, (
        "the production walk and this module's independent walk disagree; one of "
        "them is wrong and the count assertion alone cannot tell you which."
    )


def test_iter_skill_files_yields_posix_paths_and_no_directories() -> None:
    root = install.packaged_skills_root()
    for rel, resource in install.iter_skill_files(root):
        assert "\\" not in rel, f"{rel!r} carries a backslash; relpaths are POSIX-separated"
        assert not rel.startswith("/"), f"{rel!r} is absolute; relpaths are relative"
        assert not resource.is_dir(), f"{rel!r} is a directory entry; only files are yielded"
        assert resource.read_bytes() is not None


def test_iter_skill_files_reads_bytes_out_of_the_distribution() -> None:
    packaged = _packaged_bytes()
    assert SAMPLE_FILE in packaged
    assert packaged[SAMPLE_FILE].startswith(b"---"), (
        "the packaged SKILL.md should carry its YAML frontmatter; a wrong-length "
        "read here means the resource walk is not reading real bytes."
    )


# --------------------------------------------------------------------------
# target resolution (D-08, D-21)
# --------------------------------------------------------------------------


def test_resolve_targets_claude_global_lives_under_the_user_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    (target,) = install.resolve_targets(["claude"], "global", Path("/does/not/matter"))
    assert target.root == tmp_path / ".claude" / "skills"
    assert target.runtime == "claude"
    assert target.scope == "global"


def test_resolve_targets_claude_project_lives_under_the_project(tmp_path: Path) -> None:
    (target,) = install.resolve_targets(["claude"], "project", tmp_path)
    assert target.root == tmp_path / ".claude" / "skills"


def test_resolve_targets_codex_global_honours_the_codex_home_env_var(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.setenv(install.CODEX_HOME_ENV, str(tmp_path / "elsewhere"))
    (target,) = install.resolve_targets(["codex"], "global", tmp_path)
    assert target.root == tmp_path / "elsewhere" / "skills", (
        "codex-cli 0.144.6 reads $CODEX_HOME/skills; hard-coding ~/.codex would "
        "install where the binary that actually executes is not looking (D-21)."
    )


def test_resolve_targets_codex_global_falls_back_to_the_user_home(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.delenv(install.CODEX_HOME_ENV, raising=False)
    (target,) = install.resolve_targets(["codex"], "global", tmp_path)
    assert target.root == tmp_path / ".codex" / "skills"


def test_resolve_targets_codex_project(tmp_path: Path) -> None:
    (target,) = install.resolve_targets(["codex"], "project", tmp_path)
    assert target.root == tmp_path / ".codex" / "skills"


def test_resolve_targets_builds_one_target_per_runtime(tmp_path: Path) -> None:
    targets = install.resolve_targets(["claude", "codex"], "project", tmp_path)
    assert [t.runtime for t in targets] == ["claude", "codex"]
    assert len({t.root for t in targets}) == 2


def test_resolve_targets_rejects_an_unknown_runtime(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        install.resolve_targets(["emacs"], "project", tmp_path)


def test_standard_targets_covers_both_runtimes_at_both_scopes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    monkeypatch.delenv(install.CODEX_HOME_ENV, raising=False)
    targets = install.standard_targets(tmp_path / "project")
    assert {(t.runtime, t.scope) for t in targets} == {
        ("claude", "global"),
        ("claude", "project"),
        ("codex", "global"),
        ("codex", "project"),
    }


# --------------------------------------------------------------------------
# the path guard (T-01.2-05, ASVS V5) — the phase's live security control
# --------------------------------------------------------------------------


def test_safe_destination_returns_the_joined_path(tmp_path: Path) -> None:
    assert install.safe_destination(tmp_path, "a/b/c.md") == tmp_path / "a" / "b" / "c.md"


HOSTILE_RELPATHS = [
    ("absolute-posix", "/etc/passwd"),
    ("absolute-posix-nested", "/tmp/../etc/passwd"),
    ("parent-component", "../escape.txt"),
    ("parent-component-nested", "gnd-orm-core/../../escape.txt"),
    ("parent-only", ".."),
    ("empty", ""),
    ("whitespace", "   "),
    ("dot-only", "."),
    ("windows-drive", "C:\\Windows\\system32\\drivers\\etc\\hosts"),
    ("windows-drive-relative", "C:payload.txt"),
    ("windows-root-relative", "\\Windows\\System32"),
    ("windows-unc", "\\\\server\\share\\payload"),
    ("windows-parent", "..\\escape.txt"),
    ("backslash-nested-parent", "gnd-orm-core\\..\\..\\escape.txt"),
    ("leading-slash-backslash", "\\etc\\passwd"),
]


@pytest.mark.parametrize("label,relpath", HOSTILE_RELPATHS, ids=[c[0] for c in HOSTILE_RELPATHS])
def test_safe_destination_rejects_hostile_relpaths(
    tmp_path: Path, label: str, relpath: str
) -> None:
    with pytest.raises(install.InstallPathError) as caught:
        install.safe_destination(tmp_path, relpath)
    assert relpath.strip() in str(caught.value) or "empty" in str(caught.value), (
        f"[{label}] the refusal must name the offending path so a corrupted "
        f"manifest entry is diagnosable, got: {caught.value}"
    )


def test_safe_destination_rejects_a_destination_resolving_outside_the_root(
    tmp_path: Path,
) -> None:
    """A symlinked directory inside the root pointing OUT of it.

    The containment check is what fires here: no ``..`` component and no
    absolute path, but ``dest.parent.resolve()`` lands outside the target root.
    """
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "bridge").symlink_to(outside, target_is_directory=True)

    with pytest.raises(install.InstallPathError):
        install.safe_destination(root, "bridge/payload.md")


def test_safe_destination_rejects_a_symlinked_parent_pointing_inside_the_root(
    tmp_path: Path,
) -> None:
    """A symlink that stays inside the root is still refused.

    Distinct from the case above: containment passes, so only the parent-chain
    symlink check can catch it. Both guards must exist — a planted link that
    happens to resolve inside today can be re-pointed tomorrow.
    """
    root = tmp_path / "root"
    (root / "real").mkdir(parents=True)
    (root / "link").symlink_to(root / "real", target_is_directory=True)

    with pytest.raises(install.InstallPathError):
        install.safe_destination(root, "link/payload.md")


def test_safe_destination_allows_a_symlink_at_the_destination_itself(tmp_path: Path) -> None:
    """The guard gates the PARENT chain, not the leaf.

    A symlink AT a destination is a classification verdict (``collided``), not a
    path error — ``os.replace`` onto it replaces the link entry rather than
    writing through it. Conflating the two would make every symlink-mode install
    unclassifiable, which is the seam this test pins.
    """
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "outside.md").write_bytes(b"outside")
    (root / "leaf.md").symlink_to(tmp_path / "outside.md")

    assert install.safe_destination(root, "leaf.md") == root / "leaf.md"


# --------------------------------------------------------------------------
# the five-state classifier — plan() writes nothing
# --------------------------------------------------------------------------


def test_plan_against_an_empty_target_yields_create_for_every_file(tmp_path: Path) -> None:
    target = _target(tmp_path)
    records = install.plan(install.packaged_skills_root(), target, None)

    assert len(records) == EXPECTED_SKILL_FILE_COUNT
    assert {r.state for r in records} == {"create"}
    assert list(tmp_path.iterdir()) == [], "plan() must perform NO writes — it is a dry run"


def test_plan_after_a_successful_install_yields_current_for_every_file(tmp_path: Path) -> None:
    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)
    records = install.plan(install.packaged_skills_root(), _target(tmp_path), manifest)

    assert {r.state for r in records} == {"current"}, _states(records)


def test_plan_yields_stale_when_disk_matches_the_manifest_but_not_the_package(
    tmp_path: Path,
) -> None:
    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)

    # The package "moved on": disk and manifest still agree with each other.
    moved_on = b"# a previous release shipped this\n"
    (tmp_path / SAMPLE_FILE).write_bytes(moved_on)
    skill, rest = SAMPLE_FILE.split("/", 1)
    manifest.skills[skill].files[rest] = install.ManifestFile(
        sha256=_digest(moved_on), size=len(moved_on)
    )
    install.write_manifest(tmp_path, manifest)

    records = install.plan(
        install.packaged_skills_root(), _target(tmp_path), install.read_manifest(tmp_path)
    )
    assert _states(records)[SAMPLE_FILE] == "stale"


def test_plan_yields_modified_when_disk_matches_neither(tmp_path: Path) -> None:
    _install(tmp_path)
    (tmp_path / SAMPLE_FILE).write_bytes(b"# the user edited this\n")

    records = install.plan(
        install.packaged_skills_root(), _target(tmp_path), install.read_manifest(tmp_path)
    )
    assert _states(records)[SAMPLE_FILE] == "modified"


def test_plan_yields_missing_when_a_recorded_file_is_absent(tmp_path: Path) -> None:
    _install(tmp_path)
    (tmp_path / SAMPLE_FILE).unlink()

    records = install.plan(
        install.packaged_skills_root(), _target(tmp_path), install.read_manifest(tmp_path)
    )
    assert _states(records)[SAMPLE_FILE] == "missing"


def test_plan_yields_collided_for_an_unrecorded_file_at_a_gnd_owned_path(
    tmp_path: Path,
) -> None:
    """A real name collision on a name GND owns is still a collision (D-09)."""
    (tmp_path / SAMPLE_SKILL).mkdir(parents=True)
    (tmp_path / SAMPLE_FILE).write_bytes(b"placed by something other than GND\n")

    records = install.plan(install.packaged_skills_root(), _target(tmp_path), None)
    assert _states(records)[SAMPLE_FILE] == "collided"


def test_plan_yields_collided_for_a_symlink_at_a_gnd_owned_path(tmp_path: Path) -> None:
    root = tmp_path / "root"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    (tmp_path / "outside.md").write_bytes(b"outside")
    (root / SAMPLE_FILE).symlink_to(tmp_path / "outside.md")

    records = install.plan(install.packaged_skills_root(), _target(root), None)
    assert _states(records)[SAMPLE_FILE] == "collided"


# --------------------------------------------------------------------------
# the CLOSED enumeration rule (T-01.2-07b) — every target root is shared
# --------------------------------------------------------------------------


def _populate_shared_root(root: Path) -> dict[str, bytes]:
    """A target root that is NOT ours alone: a user skill, a loose file, a dotfile."""
    unrelated = {
        "my-notes-skill/SKILL.md": b"---\nname: my-notes-skill\n---\nmine, not GND's\n",
        "my-notes-skill/references/notes.md": b"deep inside an unrelated skill\n",
        "README.md": b"a loose file the user keeps at the root of their skills dir\n",
        ".some-other-tool.json": b'{"not": "gnd"}\n',
    }
    for rel, data in unrelated.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
    return unrelated


def test_plan_never_enumerates_unrelated_occupants_of_a_shared_root(tmp_path: Path) -> None:
    """The regression lock for the closed-enumeration rule.

    Built on a POPULATED root on purpose: an empty ``tmp_path`` cannot fail this
    and so cannot evidence it. Without the rule, one pre-existing user skill
    makes `uv tool install get-nick-done && gnd install` exit 11 on a clean
    machine — the exact sentence this phase exists to make true.
    """
    unrelated = _populate_shared_root(tmp_path)

    records = install.plan(install.packaged_skills_root(), _target(tmp_path), None)
    enumerated = set(_states(records))

    assert _collisions(records) == [], (
        "an unrelated occupant of a SHARED target root was classified collided; "
        "classification is closed over the packaged relpaths plus the manifest's "
        "own entries and must never discover work by walking the root."
    )
    for rel in unrelated:
        assert rel not in enumerated, f"{rel} is not GND's and must not be enumerated at all"


def test_plan_never_classifies_the_manifest_file_itself(tmp_path: Path) -> None:
    _install(tmp_path)
    assert (tmp_path / install.MANIFEST_NAME).is_file()

    records = install.plan(
        install.packaged_skills_root(), _target(tmp_path), install.read_manifest(tmp_path)
    )
    assert install.MANIFEST_NAME not in _states(records), (
        "the manifest is installer metadata, not a placed asset. It is not a "
        "packaged relpath and never appears as one of its own entries, so the "
        "union rule already excludes it — a later 'check the manifest is intact' "
        "change is exactly how this regresses."
    )
    assert _collisions(records) == []


def test_plan_refuses_a_manifest_entry_that_escapes_the_root(tmp_path: Path) -> None:
    """Traversal, manifest side. A hostile manifest must not become a delete."""
    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)
    manifest.skills[SAMPLE_SKILL].files["../../escape.txt"] = install.ManifestFile(
        sha256=_digest(b""), size=0
    )

    with pytest.raises(install.InstallPathError) as caught:
        install.plan(install.packaged_skills_root(), _target(tmp_path), manifest)
    assert "escape.txt" in str(caught.value), (
        f"the refusal must name the offending entry, got: {caught.value}"
    )


# --------------------------------------------------------------------------
# apply() — writes only deltas, manifest last (D-09, D-23)
# --------------------------------------------------------------------------


def test_apply_into_an_empty_root_writes_every_file_and_one_manifest(tmp_path: Path) -> None:
    records, result = _install(tmp_path)

    assert result.writes == EXPECTED_SKILL_FILE_COUNT, (
        f"expected {EXPECTED_SKILL_FILE_COUNT} writes on a first install, got {result.writes}"
    )
    packaged = _packaged_bytes()
    for rel, data in packaged.items():
        assert (tmp_path / rel).read_bytes() == data

    manifest = install.read_manifest(tmp_path)
    assert manifest is not None
    assert manifest.status == install.STATUS_COMPLETE
    assert manifest.schema_version == install.MANIFEST_SCHEMA
    assert manifest.mode == "copy"
    recorded = manifest.file_entries()
    assert set(recorded) == set(packaged)
    for rel, data in packaged.items():
        assert recorded[rel].sha256 == _digest(data)
        assert recorded[rel].size == len(data)
    assert len(records) == EXPECTED_SKILL_FILE_COUNT


def test_apply_on_an_unchanged_tree_performs_zero_writes(tmp_path: Path) -> None:
    _install(tmp_path)
    before = _snapshot(tmp_path)
    manifest_before = (tmp_path / install.MANIFEST_NAME).read_bytes()

    records, result = _install(tmp_path)

    assert {r.state for r in records} == {"current"}
    assert result.writes == 0, (
        "D-09 asks for ZERO writes on an unchanged second run. Asserting only on "
        "hashes would also pass if every file were rewritten with the same bytes."
    )
    assert _snapshot(tmp_path) == before
    assert (tmp_path / install.MANIFEST_NAME).read_bytes() == manifest_before


def test_apply_writes_only_create_stale_and_missing_records(tmp_path: Path) -> None:
    _install(tmp_path)
    (tmp_path / SAMPLE_FILE).unlink()
    other = "gnd-orm-core/references/halpin-posture.md"
    (tmp_path / other).write_bytes(b"# the user edited this\n")

    _, result = _install(tmp_path)
    assert result.writes == 1, "only the missing file should have been rewritten"
    assert (tmp_path / other).read_bytes() == b"# the user edited this\n", (
        "a user-modified file is never rewritten (D-11)"
    )


def test_apply_refuses_a_collided_record_without_force(tmp_path: Path) -> None:
    (tmp_path / SAMPLE_SKILL).mkdir(parents=True)
    squatter = b"placed by something other than GND\n"
    (tmp_path / SAMPLE_FILE).write_bytes(squatter)

    _, result = _install(tmp_path)

    assert (tmp_path / SAMPLE_FILE).read_bytes() == squatter
    assert [r.relpath for r in result.skipped if r.state == "collided"] == [SAMPLE_FILE]
    assert result.collisions == [SAMPLE_FILE]
    manifest = install.read_manifest(tmp_path)
    assert SAMPLE_FILE not in manifest.file_entries(), (
        "a file GND did not place must not be adopted into the manifest"
    )


def test_apply_with_force_adopts_a_collided_file(tmp_path: Path) -> None:
    (tmp_path / SAMPLE_SKILL).mkdir(parents=True)
    (tmp_path / SAMPLE_FILE).write_bytes(b"placed by something other than GND\n")

    _, result = _install(tmp_path, force=True)

    packaged = _packaged_bytes()
    assert (tmp_path / SAMPLE_FILE).read_bytes() == packaged[SAMPLE_FILE]
    assert result.collisions == []
    manifest = install.read_manifest(tmp_path)
    assert manifest.file_entries()[SAMPLE_FILE].sha256 == _digest(packaged[SAMPLE_FILE])


def test_atomic_write_closes_the_raw_descriptor_when_fdopen_fails(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """WR-01: a failed ownership transfer cannot leak the staging descriptor."""
    root = tmp_path / "root"
    root.mkdir()
    captured: list[int] = []
    real_open = install.os.open

    def recording_open(path, flags, *args, **kwargs):
        fd = real_open(path, flags, *args, **kwargs)
        if flags & os.O_CREAT:
            captured.append(fd)
        return fd

    def failing_fdopen(_fd, _mode):
        raise OSError("injected install fdopen failure")

    monkeypatch.setattr(install.os, "open", recording_open)
    monkeypatch.setattr(install.os, "fdopen", failing_fdopen)

    with pytest.raises(OSError, match="injected install fdopen failure"):
        install._atomic_write(
            root,
            "managed.txt",
            b"staged bytes\n",
            expected=install.LeafIdentity(kind="absent"),
        )

    assert len(captured) == 1
    with pytest.raises(OSError):
        os.fstat(captured[0])
    assert list(root.iterdir()) == []


def test_apply_writes_the_manifest_last(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """D-23: absence of the manifest IS the partial-install signal."""
    order: list[str] = []
    real_atomic_write = install._atomic_write

    def _tracking(
        root: Path,
        relpath: str,
        data: bytes,
        *,
        expected: install.LeafIdentity | None = None,
    ) -> None:
        order.append(PurePosixPath(relpath).name)
        real_atomic_write(root, relpath, data, expected=expected)

    monkeypatch.setattr(install, "_atomic_write", _tracking)
    _install(tmp_path)

    assert order[-1] == install.MANIFEST_NAME, (
        "the manifest must be the LAST write; anything else lets a half-written "
        "manifest claim files it did not place."
    )
    assert order.count(install.MANIFEST_NAME) == 1


def test_a_crashed_install_leaves_files_and_no_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    real_atomic_write = install._atomic_write

    def _crash_before_the_manifest(
        root: Path,
        relpath: str,
        data: bytes,
        *,
        expected: install.LeafIdentity | None = None,
    ) -> None:
        if PurePosixPath(relpath).name == install.MANIFEST_NAME:
            raise OSError("simulated crash between the file writes and the manifest")
        real_atomic_write(root, relpath, data, expected=expected)

    monkeypatch.setattr(install, "_atomic_write", _crash_before_the_manifest)
    with pytest.raises(OSError):
        _install(tmp_path)

    assert (tmp_path / SAMPLE_FILE).is_file(), "the placed files are present"
    assert not (tmp_path / install.MANIFEST_NAME).exists(), (
        "no manifest may exist after a crash — its absence is the signal (D-23)"
    )

    monkeypatch.undo()
    records = install.plan(install.packaged_skills_root(), _target(tmp_path), None)
    assert set(_collisions(records)) == set(_packaged_bytes()), (
        "a subsequent plan must classify every orphaned file as collided — "
        "nothing may imply GND placed them, because no manifest says so."
    )


# --------------------------------------------------------------------------
# traversal, packaged side (T-01.2-05) — asserted at the apply seam
# --------------------------------------------------------------------------


def _sentinel_outside(tmp_path: Path) -> tuple[Path, Path, bytes]:
    root = tmp_path / "root"
    root.mkdir()
    sentinel = tmp_path / "escape.txt"
    payload = b"the installer must never touch this\n"
    sentinel.write_bytes(payload)
    return root, sentinel, payload


def test_apply_refuses_an_escaping_packaged_relpath_before_any_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, sentinel, payload = _sentinel_outside(tmp_path)
    hostile = "../escape.txt"

    class _StubEntry:
        def read_bytes(self) -> bytes:
            return b"payload written outside the root\n"

    monkeypatch.setattr(
        install, "iter_skill_files", lambda root_, prefix="": iter([(hostile, _StubEntry())])
    )

    records = [install.SkillFileState(relpath=hostile, state="create")]
    with pytest.raises(install.InstallPathError):
        install.apply(install.packaged_skills_root(), _target(root), records)

    assert sentinel.read_bytes() == payload
    assert _snapshot(root) == {}, "nothing may be created inside the root either"


def test_plan_refuses_an_escaping_packaged_relpath(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, sentinel, payload = _sentinel_outside(tmp_path)

    class _StubEntry:
        def read_bytes(self) -> bytes:
            return b"payload\n"

    monkeypatch.setattr(
        install,
        "iter_skill_files",
        lambda root_, prefix="": iter([("../escape.txt", _StubEntry())]),
    )

    with pytest.raises(install.InstallPathError):
        install.plan(install.packaged_skills_root(), _target(root), None)
    assert sentinel.read_bytes() == payload


# --------------------------------------------------------------------------
# manifest I/O
# --------------------------------------------------------------------------


def test_read_manifest_returns_none_when_absent(tmp_path: Path) -> None:
    assert install.read_manifest(tmp_path) is None


def test_read_manifest_refuses_a_higher_schema_version(tmp_path: Path) -> None:
    _install(tmp_path)
    path = tmp_path / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["schema"] = install.MANIFEST_SCHEMA + 1
    path.write_text(json.dumps(raw), encoding="utf-8")

    with pytest.raises(install.ManifestSchemaError):
        install.read_manifest(tmp_path)


def test_manifest_paths_are_relative_and_posix(tmp_path: Path) -> None:
    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)
    for skill, entry in manifest.skills.items():
        assert "/" not in skill
        for rel in entry.files:
            assert not rel.startswith("/")
            assert "\\" not in rel


def test_manifest_records_the_framework_and_version(tmp_path: Path) -> None:
    from gnd import DISTRIBUTION, resolve_version

    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)
    assert manifest.framework == DISTRIBUTION
    assert manifest.version == resolve_version()
    assert manifest.runtime == "claude"
    assert manifest.scope == "project"
    assert manifest.installed_at.endswith("Z")


# --------------------------------------------------------------------------
# data-driven discovery (D-06)
# --------------------------------------------------------------------------


def test_a_third_skill_in_the_source_tree_is_planned_with_no_code_change(
    tmp_path: Path,
) -> None:
    """Discovery is a runtime walk, not a table. Adding a skill is a no-op here."""
    synthetic = tmp_path / "source"
    (synthetic / "gnd-future-skill" / "references").mkdir(parents=True)
    (synthetic / "gnd-future-skill" / "SKILL.md").write_bytes(b"---\nname: gnd-future-skill\n---\n")
    (synthetic / "gnd-future-skill" / "references" / "notes.md").write_bytes(b"notes\n")

    root = tmp_path / "root"
    root.mkdir()
    records = install.plan(synthetic, _target(root), None)

    assert _states(records) == {
        "gnd-future-skill/SKILL.md": "create",
        "gnd-future-skill/references/notes.md": "create",
    }


#: The two ``importlib.resources`` escape hatches D-19 forbids, plus the
#: checkout assumption D-04 deletes. Named HERE and nowhere in ``install.py``:
#: the guard below greps that module's source, so a prohibition written as a
#: comment over there would make the count permanently non-zero and force the
#: gate to be "corrected" to a constant that is right for the wrong reason.
FORBIDDEN_IN_INSTALL_SOURCE = ("os.fspath", "as_file", "__file__")


@pytest.mark.parametrize("token", FORBIDDEN_IN_INSTALL_SOURCE)
def test_install_source_carries_no_path_coercion_or_checkout_arithmetic(token: str) -> None:
    """T-01.2-09 / D-04, mechanically.

    ``os.fspath`` raises ``TypeError`` under zipimport and ``as_file`` raises
    ``IsADirectoryError`` on a directory on Python 3.11 — this project's declared
    floor — so neither may appear. ``__file__`` may not appear either: deriving
    the skills path by walking up from the module file works in a checkout and is
    exactly the checkout assumption this phase exists to delete.
    """
    source = Path(install.__file__).read_text(encoding="utf-8")
    assert token not in source, (
        f"src/gnd/install.py mentions {token!r}. Every packaged read must go "
        f"through files('gnd') with iterdir/is_dir/read_bytes only (D-19), and no "
        f"read may be derived from this module's own location (D-04)."
    )


def test_iter_skill_files_skips_the_reserved_synced_directory(tmp_path: Path) -> None:
    """`synced` is reserved by the runtime skill locations, in any capitalisation."""
    source = tmp_path / "source"
    (source / "a-skill").mkdir(parents=True)
    (source / "a-skill" / "SKILL.md").write_bytes(b"x")
    (source / "Synced").mkdir()
    (source / "Synced" / "leaked.md").write_bytes(b"y")

    found = {rel for rel, _ in install.iter_skill_files(source)}
    assert found == {"a-skill/SKILL.md"}


# --------------------------------------------------------------------------
# the CLI (PKG-02, D-08, D-25) — exercised the way a user does
# --------------------------------------------------------------------------


def test_lifecycle_exit_codes_never_collide_with_the_band_contract() -> None:
    """The bands are normative; 5-9 are reserved headroom for future verdicts."""
    lifecycle = {
        "EXIT_DRIFT": cli.EXIT_DRIFT,
        "EXIT_COLLISION": cli.EXIT_COLLISION,
        "EXIT_NO_INSTALL": cli.EXIT_NO_INSTALL,
        "EXIT_IO": cli.EXIT_IO,
    }
    reserved = {0, 1, 2, 3, 4, cli.EXIT_USAGE, cli.EXIT_INTERNAL}
    for name, code in lifecycle.items():
        assert code not in reserved, (
            f"{name}={code} collides with the normative 0-4/64/70 contract; a retry "
            f"loop keying on the bands would misread a lifecycle outcome as a verdict."
        )
        assert code >= 10, (
            f"{name}={code} is below 10; 5-9 are deliberately unallocated so future "
            f"verdict bands have headroom and lifecycle codes stay unmistakable."
        )
        assert code not in range(125, 129), f"{name}={code} is shell/signal reserved"
    assert len(set(lifecycle.values())) == len(lifecycle), "lifecycle codes must be distinct"
    assert (cli.EXIT_DRIFT, cli.EXIT_COLLISION, cli.EXIT_NO_INSTALL, cli.EXIT_IO) == (
        10,
        11,
        12,
        74,
    )


def test_cli_module_declares_the_collision_code_with_its_rationale() -> None:
    source = Path(cli.__file__).read_text(encoding="utf-8")
    assert source.count("EXIT_COLLISION") >= 1
    assert "masquerade" in source, (
        "each lifecycle constant carries a 'would masquerade as X' justification in "
        "cli.py's existing docstring, matching the tone of the band entries."
    )


def test_install_places_both_runtimes_at_project_scope(tmp_path: Path) -> None:
    result = _run_gnd(
        ["install", "--claude", "--codex", "--project"], cwd=tmp_path, HOME=str(tmp_path)
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    packaged = _packaged_bytes()
    for runtime in (".claude", ".codex"):
        root = tmp_path / runtime / "skills"
        assert root.is_dir(), f"{root} was not created"
        placed = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
        assert placed == set(packaged) | {install.MANIFEST_NAME}, (
            f"{root} holds {len(placed)} files; expected {EXPECTED_SKILL_FILE_COUNT} "
            f"skill files plus one manifest"
        )
        assert {d.name for d in root.iterdir() if d.is_dir()} == EXPECTED_SKILL_NAMES
        manifest = install.read_manifest(root)
        assert manifest.status == install.STATUS_COMPLETE
        assert manifest.runtime == runtime.lstrip(".")


def test_install_reports_and_skips_an_unmanaged_file_and_exits_11(tmp_path: Path) -> None:
    root = tmp_path / ".claude" / "skills"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    squatter = b"a file GND did not place\n"
    (root / SAMPLE_FILE).write_bytes(squatter)

    result = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))

    assert result.returncode == cli.EXIT_COLLISION, (
        f"expected {cli.EXIT_COLLISION}, got {result.returncode}\n{result.stdout}\n{result.stderr}"
    )
    assert (root / SAMPLE_FILE).read_bytes() == squatter, "nothing may be destroyed"
    assert SAMPLE_FILE in result.stdout, (
        f"the blocked path must be named on stdout, got:\n{result.stdout}"
    )


def test_install_with_force_adopts_the_unmanaged_file_and_exits_0(tmp_path: Path) -> None:
    root = tmp_path / ".claude" / "skills"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    (root / SAMPLE_FILE).write_bytes(b"a file GND did not place\n")

    result = _run_gnd(
        ["install", "--claude", "--project", "--force"], cwd=tmp_path, HOME=str(tmp_path)
    )

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    packaged = _packaged_bytes()
    assert (root / SAMPLE_FILE).read_bytes() == packaged[SAMPLE_FILE]
    manifest = install.read_manifest(root)
    assert manifest.file_entries()[SAMPLE_FILE].sha256 == _digest(packaged[SAMPLE_FILE])


def test_install_symlink_project_writes_relative_links(tmp_path: Path) -> None:
    result = _run_gnd(
        ["install", "--claude", "--project", "--symlink"], cwd=tmp_path, HOME=str(tmp_path)
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    root = tmp_path / ".claude" / "skills"
    for name in ("gnd-orm-core", "gnd-model-from-text"):
        link = root / name
        assert link.is_symlink(), f"{link} is not a symlink"
        raw = os.readlink(link)
        assert not os.path.isabs(raw), (
            f"a project-scope link must be RELATIVE so a repository's checked-in "
            f"links stay machine-independent; got {raw!r}"
        )
        assert (link / "SKILL.md").read_bytes() == _packaged_bytes()[f"{name}/SKILL.md"]
    manifest = install.read_manifest(root)
    assert manifest.mode == "symlink"


def test_install_symlink_global_writes_absolute_links(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    result = _run_gnd(
        ["install", "--claude", "--global", "--symlink"], cwd=tmp_path, HOME=str(home)
    )
    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"

    link = home / ".claude" / "skills" / "gnd-orm-core"
    assert link.is_symlink()
    raw = os.readlink(link)
    assert os.path.isabs(raw), (
        f"a user-scope link must be ABSOLUTE: a relative path from the user's home "
        f"skills directory into a tool environment is long and fragile. Got {raw!r}"
    )
    assert (link / "SKILL.md").is_file()


def test_install_symlink_mode_is_idempotent(tmp_path: Path) -> None:
    _run_gnd(["install", "--claude", "--project", "--symlink"], cwd=tmp_path, HOME=str(tmp_path))
    root = tmp_path / ".claude" / "skills"
    before = _snapshot(root)

    records = install.plan(
        install.packaged_skills_root(),
        _target(root),
        install.read_manifest(root),
        mode="symlink",
    )
    assert {r.state for r in records} == {"current"}, _states(records)
    assert _snapshot(root) == before


def test_install_symlink_mode_reports_a_dangling_link_as_missing(tmp_path: Path) -> None:
    """D-20's real failure mode for a --symlink dev user, modelled exactly.

    A tool environment lives at ``lib/python3.13/site-packages``. An interpreter
    minor-version change rebuilds it at ``lib/python3.12/...`` — so the packaged
    tree still exists, at a *different* path, and the link placed against the old
    one dangles. Deleting the source and then planning against the deleted path
    would prove nothing (it just raises); the two roots have to coexist.
    """
    root = tmp_path / "root"
    root.mkdir()
    old_env = tmp_path / "lib" / "python3.13" / "skills"
    (old_env / "gnd-future-skill").mkdir(parents=True)
    (old_env / "gnd-future-skill" / "SKILL.md").write_bytes(b"x")

    target = _target(root)
    install.apply(
        old_env, target, install.plan(old_env, target, None, mode="symlink"), mode="symlink"
    )
    assert (root / "gnd-future-skill" / "SKILL.md").is_file()

    new_env = tmp_path / "lib" / "python3.12" / "skills"
    (new_env / "gnd-future-skill").mkdir(parents=True)
    (new_env / "gnd-future-skill" / "SKILL.md").write_bytes(b"x")
    shutil.rmtree(tmp_path / "lib" / "python3.13")

    records = install.plan(new_env, target, install.read_manifest(root), mode="symlink")
    state = next(r for r in records if r.relpath == "gnd-future-skill")
    assert state.state == "missing", (
        f"a dangling link must read as missing, not current — that is the failure a "
        f"--symlink dev user actually hits (D-20). Got {state.state}: {state.detail}"
    )
    assert "dangling" in state.detail, f"the reason must be in the detail: {state.detail!r}"


def test_install_sync_with_no_manifest_anywhere_exits_12(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()

    result = _run_gnd(["install", "--sync"], cwd=project, HOME=str(home))

    assert result.returncode == cli.EXIT_NO_INSTALL, (
        f"expected {cli.EXIT_NO_INSTALL}, got {result.returncode}\n{result.stdout}"
    )
    for expected in (
        str(home / ".claude" / "skills"),
        str(home / ".codex" / "skills"),
        str(project / ".claude" / "skills"),
        str(project / ".codex" / "skills"),
    ):
        assert expected in result.stdout, (
            f"--sync must say WHICH roots it looked at — there is no central registry "
            f"to inspect instead. Missing {expected} from:\n{result.stdout}"
        )


def test_install_sync_refreshes_only_roots_that_carry_a_manifest(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()
    _run_gnd(["install", "--claude", "--project"], cwd=project, HOME=str(home))

    result = _run_gnd(["install", "--sync"], cwd=project, HOME=str(home))

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert str(project / ".claude" / "skills") in result.stdout
    assert not (project / ".codex").exists(), "--sync must not create a root that had no manifest"
    assert not (home / ".claude").exists()


def test_install_refuses_a_mode_switch_without_destroying_anything(tmp_path: Path) -> None:
    _run_gnd(["install", "--claude", "--project", "--symlink"], cwd=tmp_path, HOME=str(tmp_path))
    root = tmp_path / ".claude" / "skills"
    before = _snapshot(root)

    result = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))

    assert result.returncode == cli.EXIT_COLLISION
    assert _snapshot(root) == before, (
        "copying files beneath a symlinked skill directory would write THROUGH the "
        "link, into the distribution itself. Nothing may change."
    )


def test_install_rejects_a_malformed_invocation_with_exit_64(tmp_path: Path) -> None:
    result = _run_gnd(["install", "--claude", "--nonsense"], cwd=tmp_path, HOME=str(tmp_path))
    assert result.returncode == cli.EXIT_USAGE, (
        f"argparse's default SystemExit(2) would masquerade as the 'vacuous "
        f"population' band; _BandSafeParser routes it to 64. Got {result.returncode}"
    )


def test_install_rejects_both_scope_flags_at_once(tmp_path: Path) -> None:
    result = _run_gnd(["install", "--global", "--project"], cwd=tmp_path, HOME=str(tmp_path))
    assert result.returncode == cli.EXIT_USAGE


def test_install_offers_no_format_flag(tmp_path: Path) -> None:
    """D-25: text-only is a decision, and the help text has to say so."""
    rejected = _run_gnd(
        ["install", "--format", "json", "--project"], cwd=tmp_path, HOME=str(tmp_path)
    )
    assert rejected.returncode == cli.EXIT_USAGE

    helped = _run_gnd(["install", "--help"], cwd=tmp_path, HOME=str(tmp_path))
    assert helped.returncode == 0
    assert "--format" not in helped.stdout.split("options:")[-1]
    assert "Text output only" in helped.stdout
    assert "D-25" in helped.stdout, (
        "a user who expects a machine-readable install report must learn from the "
        "help text that its absence is deliberate."
    )


def test_install_defaults_to_both_runtimes_at_user_scope(tmp_path: Path) -> None:
    home = tmp_path / "home"
    home.mkdir()
    result = _run_gnd(["install"], cwd=tmp_path, HOME=str(home))

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert (home / ".claude" / "skills" / install.MANIFEST_NAME).is_file()
    assert (home / ".codex" / "skills" / install.MANIFEST_NAME).is_file()
    assert not (tmp_path / ".claude").exists(), "the default scope is user-level, not project"


def test_install_honours_codex_home_end_to_end(tmp_path: Path) -> None:
    home = tmp_path / "home"
    codex_home = tmp_path / "elsewhere"
    home.mkdir()
    result = _run_gnd(
        ["install", "--codex"], cwd=tmp_path, HOME=str(home), CODEX_HOME=str(codex_home)
    )

    assert result.returncode == 0, f"stdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    assert (codex_home / "skills" / install.MANIFEST_NAME).is_file()
    assert not (home / ".codex").exists(), (
        "hard-coding ~/.codex would install where codex-cli is not looking (D-21)"
    )


# --------------------------------------------------------------------------
# adversarial and idempotence corpus (T-01.2-05 .. T-01.2-10)
#
# Table-driven in the style Phase 01.1 established: one row per case, each
# carrying a `why` string that is printed alongside the failure so a future red
# run explains itself before anyone is tempted to loosen the rule that produced
# it. Several rows are REGRESSION LOCKS on guards written in task 1 rather than
# new discoveries; the ones that are locks say so in their `why`.
# --------------------------------------------------------------------------


def _sentinel_root(tmp_path: Path) -> tuple[Path, Path, bytes]:
    root = tmp_path / "root"
    root.mkdir()
    sentinel = tmp_path / "escape.txt"
    payload = b"the installer must never touch this\n"
    sentinel.write_bytes(payload)
    return root, sentinel, payload


def _case_zero_write_second_run(tmp_path: Path) -> None:
    _, first = _install(tmp_path)
    assert first.writes == EXPECTED_SKILL_FILE_COUNT
    before = _snapshot(tmp_path)
    manifest_before = (tmp_path / install.MANIFEST_NAME).read_bytes()

    _, second = _install(tmp_path)

    assert second.writes == 0, (
        f"second run performed {second.writes} write(s). Hashes alone would ALSO be "
        f"identical if the installer rewrote every file with the same content, which "
        f"is not what D-09 asks for — the write count is the observable."
    )
    assert _snapshot(tmp_path) == before
    assert (tmp_path / install.MANIFEST_NAME).read_bytes() == manifest_before


def _case_traversal_packaged_side(tmp_path: Path) -> None:
    root, sentinel, payload = _sentinel_root(tmp_path)
    hostile = "../../escape.txt"
    outside_before = {p.name for p in tmp_path.iterdir()}

    class _StubEntry:
        def read_bytes(self) -> bytes:
            return b"OWNED\n"

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(
            install, "iter_skill_files", lambda root_, prefix="": iter([(hostile, _StubEntry())])
        )
        with pytest.raises(install.InstallPathError):
            install.plan(install.packaged_skills_root(), _target(root), None)
        with pytest.raises(install.InstallPathError):
            install.apply(
                install.packaged_skills_root(),
                _target(root),
                [install.SkillFileState(relpath=hostile, state="create")],
            )

    assert sentinel.read_bytes() == payload, "the sentinel outside the root was written"
    assert {p.name for p in tmp_path.iterdir()} == outside_before, "something was created outside"
    assert _snapshot(root) == {}, "nothing may be created inside the root either"


def _case_traversal_manifest_side(tmp_path: Path) -> None:
    root, sentinel, payload = _sentinel_root(tmp_path)
    _install(root)
    manifest = install.read_manifest(root)
    hostile = "../../../escape.txt"
    manifest.skills[SAMPLE_SKILL].files[hostile] = install.ManifestFile(sha256=_digest(b""), size=0)

    # Refused at BOTH seams: reading the document back off disk, and planning
    # from an in-memory manifest a library caller supplied.
    (root / install.MANIFEST_NAME).write_text(
        json.dumps(manifest.model_dump(by_alias=True)), encoding="utf-8"
    )
    with pytest.raises(install.InstallPathError) as at_read:
        install.read_manifest(root)
    assert "escape.txt" in str(at_read.value), f"refusal must name the entry: {at_read.value}"

    with pytest.raises(install.InstallPathError) as at_plan:
        install.plan(install.packaged_skills_root(), _target(root), manifest)
    assert "escape.txt" in str(at_plan.value), f"refusal must name the entry: {at_plan.value}"

    assert sentinel.read_bytes() == payload


def _case_symlink_at_destination(tmp_path: Path) -> None:
    outside = tmp_path / "secret.md"
    payload = b"a file the user owns, outside any target root\n"
    outside.write_bytes(payload)
    root = tmp_path / ".claude" / "skills"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    (root / SAMPLE_FILE).symlink_to(outside)

    records = install.plan(install.packaged_skills_root(), _target(root), None)
    assert _states(records)[SAMPLE_FILE] == "collided"

    result = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))
    assert result.returncode == cli.EXIT_COLLISION, (
        f"expected {cli.EXIT_COLLISION}, got {result.returncode}\n{result.stdout}"
    )
    assert outside.read_bytes() == payload, "the file the link points at was written through"
    assert (root / SAMPLE_FILE).is_symlink(), "the link itself must be left in place"


def _case_unmanaged_file_collision(tmp_path: Path) -> None:
    root = tmp_path / ".claude" / "skills"
    (root / SAMPLE_SKILL).mkdir(parents=True)
    squatter = b"a file GND did not place\n"
    (root / SAMPLE_FILE).write_bytes(squatter)

    blocked = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))
    assert blocked.returncode == cli.EXIT_COLLISION, blocked.stdout
    assert (root / SAMPLE_FILE).read_bytes() == squatter
    assert SAMPLE_FILE in blocked.stdout, "the blocked path must be named"
    assert SAMPLE_FILE not in install.read_manifest(root).file_entries(), (
        "a file GND did not place must not be adopted into the manifest"
    )

    forced = _run_gnd(
        ["install", "--claude", "--project", "--force"], cwd=tmp_path, HOME=str(tmp_path)
    )
    assert forced.returncode == 0, forced.stdout
    packaged = _packaged_bytes()
    assert (root / SAMPLE_FILE).read_bytes() == packaged[SAMPLE_FILE]
    assert install.read_manifest(root).file_entries()[SAMPLE_FILE].sha256 == _digest(
        packaged[SAMPLE_FILE]
    )


def _case_user_modified_file(tmp_path: Path) -> None:
    root = tmp_path / ".claude" / "skills"
    _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))
    edit = b"# the user added a note to this skill\n"
    (root / SAMPLE_FILE).write_bytes(edit)

    records = install.plan(
        install.packaged_skills_root(), _target(root), install.read_manifest(root)
    )
    assert _states(records)[SAMPLE_FILE] == "modified"

    result = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))
    assert (root / SAMPLE_FILE).read_bytes() == edit, "a user edit must never be rewritten (D-11)"
    assert SAMPLE_FILE in result.stdout and "modified" in result.stdout, (
        f"install may succeed here, but never SILENTLY: the untouched path has to be "
        f"named on stdout. Got:\n{result.stdout}"
    )
    carried = install.read_manifest(root).file_entries()[SAMPLE_FILE].sha256
    assert carried == _digest(_packaged_bytes()[SAMPLE_FILE]), (
        "the manifest must carry forward the digest GND PLACED, not the user's edit — "
        "recording the edit would make a later uninstall hash-match and delete it"
    )


def _case_partial_install_is_diagnosable(tmp_path: Path) -> None:
    real_atomic_write = install._atomic_write

    def _crash(
        root: Path,
        relpath: str,
        data: bytes,
        *,
        expected: install.LeafIdentity | None = None,
    ) -> None:
        if PurePosixPath(relpath).name == install.MANIFEST_NAME:
            raise OSError("simulated crash between the file writes and the manifest")
        real_atomic_write(root, relpath, data, expected=expected)

    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(install, "_atomic_write", _crash)
        with pytest.raises(OSError):
            _install(tmp_path)

    assert (tmp_path / SAMPLE_FILE).is_file(), "the placed files are present"
    assert not (tmp_path / install.MANIFEST_NAME).exists(), (
        "absence of the manifest IS the partial-install signal (D-23); a half-written "
        "one would claim files it did not place"
    )
    records = install.plan(install.packaged_skills_root(), _target(tmp_path), None)
    assert set(_collisions(records)) == set(_packaged_bytes()), (
        "every orphaned file must classify as collided — nothing may imply GND placed "
        "them, because no manifest says so"
    )


def _case_data_driven_discovery(tmp_path: Path) -> None:
    source = tmp_path / "source"
    for skill in ("gnd-orm-core", "gnd-model-from-text", "gnd-phase-two-skill"):
        (source / skill / "references").mkdir(parents=True)
        (source / skill / "SKILL.md").write_bytes(f"---\nname: {skill}\n---\n".encode())
        (source / skill / "references" / "notes.md").write_bytes(b"notes\n")

    root = tmp_path / "root"
    root.mkdir()
    target = _target(root)
    records = install.plan(source, target, None)
    result = install.apply(source, target, records, manifest=None)

    assert result.writes == 6, f"expected 6 writes across 3 skills, got {result.writes}"
    assert (root / "gnd-phase-two-skill" / "SKILL.md").is_file(), (
        "a skill directory added to the packaged tree must install with ZERO installer "
        "changes and ZERO manifest edits — that is D-06, mechanically"
    )
    assert set(install.read_manifest(root).skills) == {
        "gnd-orm-core",
        "gnd-model-from-text",
        "gnd-phase-two-skill",
    }


def _case_mixed_scope_hazard(tmp_path: Path) -> None:
    home = tmp_path / "home"
    project = tmp_path / "project"
    home.mkdir()
    project.mkdir()

    at_user = _run_gnd(["install", "--claude", "--global"], cwd=project, HOME=str(home))
    assert at_user.returncode == 0, at_user.stdout
    user_root = home / ".claude" / "skills"
    user_snapshot = _snapshot(user_root)

    at_project = _run_gnd(["install", "--claude", "--project"], cwd=project, HOME=str(home))
    assert at_project.returncode == 0, at_project.stdout
    project_root = project / ".claude" / "skills"

    user_manifest = install.read_manifest(user_root)
    project_manifest = install.read_manifest(project_root)
    assert user_manifest.scope == "global" and project_manifest.scope == "project", (
        "each manifest must describe its OWN root; a shared or overwritten receipt is "
        "how a mixed-scope install becomes undiagnosable"
    )
    assert set(user_manifest.skills) == set(project_manifest.skills)
    assert _snapshot(user_root) == user_snapshot, "the project install mutated the user root"
    assert set(_snapshot(project_root)) == set(user_snapshot)


def _case_shared_root_unrelated_occupants(tmp_path: Path) -> None:
    root = tmp_path / ".claude" / "skills"
    root.mkdir(parents=True)
    unrelated = _populate_shared_root(root)
    _install(root)  # a prior run, so a real .gnd-install.json is present too
    assert (root / install.MANIFEST_NAME).is_file()
    for rel in unrelated:
        (root / rel).write_bytes(unrelated[rel])

    for attempt in (1, 2):
        records = install.plan(
            install.packaged_skills_root(), _target(root), install.read_manifest(root)
        )
        assert _collisions(records) == [], (
            f"attempt {attempt}: {_collisions(records)} classified as collided in a SHARED root"
        )
        result = _run_gnd(["install", "--claude", "--project"], cwd=tmp_path, HOME=str(tmp_path))
        assert result.returncode == 0, (
            f"attempt {attempt}: exited {result.returncode}, expected 0\n{result.stdout}"
        )

    for rel, data in unrelated.items():
        assert (root / rel).read_bytes() == data, f"{rel} was modified"
    assert (root / "my-notes-skill").is_dir(), "the unrelated skill directory was removed"


class InstallCase(NamedTuple):
    """One corpus row. ``why`` is printed in the failure message so a future red
    run explains itself before anyone is tempted to loosen the rule."""

    id: str
    why: str
    run: Callable[[Path], None]


#: Ten cases. Several are REGRESSION LOCKS on guards written in task 1 rather
#: than new discoveries; those say so in their ``why``.
INSTALL_CORPUS: list[InstallCase] = [
    InstallCase(
        "zero-write-second-run",
        (
            "D-09 makes idempotence testable rather than asserted. A blind copytree "
            "produces identical hashes while rewriting all 29 files, so only the WRITE "
            "COUNT distinguishes 'did nothing' from 'did everything again'."
        ),
        _case_zero_write_second_run,
    ),
    InstallCase(
        "traversal-escape-packaged-side",
        (
            "T-01.2-05. A relpath from the packaged tree becomes a write destination in a "
            "user-owned directory. If a crafted name can climb out, `gnd install` is an "
            "arbitrary-file-write primitive. It must raise BEFORE any filesystem call."
        ),
        _case_traversal_packaged_side,
    ),
    InstallCase(
        "traversal-escape-manifest-side",
        (
            "T-01.2-05, the harder half: the manifest is read back from a user-writable "
            "directory, so its path strings are untrusted input. A hostile receipt must "
            "not be able to make the lifecycle plan's uninstall delete ~/.ssh/id_rsa."
        ),
        _case_traversal_manifest_side,
    ),
    InstallCase(
        "symlink-at-destination",
        (
            "T-01.2-06. A planted link at a destination would redirect a copy outside the "
            "root. Ownership is decided by manifest provenance, so an unrecorded link is "
            "`collided` and is never opened for writing. Regression lock on task 1."
        ),
        _case_symlink_at_destination,
    ),
    InstallCase(
        "unmanaged-file-collision",
        (
            "T-01.2-07 / D-09. Never overwrite what GND did not place. --force is the only "
            "path that adopts a colliding file, and it must be an explicit act."
        ),
        _case_unmanaged_file_collision,
    ),
    InstallCase(
        "user-modified-file",
        (
            "D-11. An installer that destroys a user's edits is worse than one that leaves "
            "litter. --force deliberately does NOT reach `modified`, and the manifest keeps "
            "the digest GND placed so a later uninstall cannot hash-match the edit."
        ),
        _case_user_modified_file,
    ),
    InstallCase(
        "partial-install-is-diagnosable",
        (
            "T-01.2-08 / D-23. The manifest is written last, so a crash presents as "
            "files-present-manifest-absent. The alternative — a half-written receipt "
            "claiming files it never placed — makes every later diagnosis a lie."
        ),
        _case_partial_install_is_diagnosable,
    ),
    InstallCase(
        "data-driven-discovery",
        (
            "D-06. Discovery is a runtime walk, never a generated table. Phase 2 ships more "
            "skills; if this fails, every later phase pays an installer change to ship one."
        ),
        _case_data_driven_discovery,
    ),
    InstallCase(
        "mixed-scope-hazard",
        (
            "Pitfall 6/7. Claude Code precedence is personal > project, so a --global "
            "install SHADOWS a --project one. Both receipts must stay independently "
            "readable — that is the raw material the lifecycle plan's doctor turns into a "
            "shadowing diagnostic."
        ),
        _case_mixed_scope_hazard,
    ),
    InstallCase(
        "shared-root-unrelated-occupants",
        (
            "T-01.2-07b, the regression lock for the closed-enumeration rule. EVERY target "
            "root is shared with the user's own skills and with the manifest itself. If the "
            "classifier discovers work by walking the root, one pre-existing user skill "
            "classifies as `collided`, the outcome mapper returns 11, and "
            "`uv tool install get-nick-done && gnd install` FAILS on a clean machine — the "
            "sentence this whole phase exists to make true. Built on a POPULATED root on "
            "purpose: a case built under an empty tmp_path passes vacuously and evidences "
            "nothing."
        ),
        _case_shared_root_unrelated_occupants,
    ),
]


@pytest.mark.parametrize("case", INSTALL_CORPUS, ids=[row.id for row in INSTALL_CORPUS])
def test_install_adversarial_case(case: InstallCase, tmp_path: Path) -> None:
    try:
        case.run(tmp_path)
    except AssertionError as failure:
        pytest.fail(f"{case.id}: {failure}\n\nWhy this case exists: {case.why}")


def test_the_corpus_covers_ten_named_cases() -> None:
    assert len(INSTALL_CORPUS) == 10
    assert len({row.id for row in INSTALL_CORPUS}) == 10
    for row in INSTALL_CORPUS:
        assert row.why.strip(), f"{row.id} carries no `why`; a red run would not explain itself"


# --------------------------------------------------------------------------
# D-26 — every skill through ONE generic path
# --------------------------------------------------------------------------


def test_a_clean_install_places_every_skill_through_one_generic_path(
    tmp_path: Path,
) -> None:
    """Whole-lifecycle proof for the current tree: place, own, refuse.

    The three assertions the sibling tests make separately, made together over
    the full skill inventory, because D-26's claim is specifically that
    they hold *as one*: an installer can place 48 files and record 40 of them,
    and every count guard in this suite stays green while `uninstall` silently
    strands eight.

    Nothing here names a skill to the installer. The expected sets are compared
    against what a name-agnostic traversal produced.
    """
    root = tmp_path / "prefix" / ".claude" / "skills"
    root.mkdir(parents=True)

    records, result = _install(root)

    # 1. PLACED — every packaged file, and the ten directories they live in.
    placed = {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}
    packaged = set(_packaged_bytes())
    assert placed == packaged | {install.MANIFEST_NAME}, (
        f"placed set differs from the packaged set.\n"
        f"  missing: {sorted(packaged - placed)}\n"
        f"  extra:   {sorted(placed - packaged - {install.MANIFEST_NAME})}"
    )
    assert {d.name for d in root.iterdir() if d.is_dir()} == EXPECTED_SKILL_NAMES
    assert result.writes == EXPECTED_SKILL_FILE_COUNT
    assert len(records) == EXPECTED_SKILL_FILE_COUNT

    # 2. OWNED — the receipt claims every placed file by identity, not by count.
    #    A receipt that under-claims is F-01's defect: `uninstall` removes only
    #    what the receipt names, so an unclaimed file is permanently unremovable.
    manifest = install.read_manifest(root)
    assert manifest is not None
    assert set(manifest.skills) == EXPECTED_SKILL_NAMES
    entries = manifest.file_entries()
    assert set(entries) == packaged, (
        f"the receipt does not claim what was placed.\n"
        f"  unclaimed: {sorted(packaged - set(entries))}\n"
        f"  phantom:   {sorted(set(entries) - packaged)}"
    )
    for rel, record in entries.items():
        assert record.sha256 == _digest((root / rel).read_bytes()), (
            f"the receipt's digest for {rel} is not the digest of the bytes on disk"
        )

    # 3. REFUSED — collision refusal stays generic across all ten. Re-running
    #    over a tree GND no longer has a receipt for must refuse every file
    #    rather than adopt it (D-09).
    (root / install.MANIFEST_NAME).unlink()
    second_records, second_result = _install(root)
    assert second_result.writes == 0, "an unmanaged tree must be refused, not adopted"
    assert sorted(_collisions(second_records)) == sorted(packaged), (
        "collision refusal is not reaching every skill; it must be decided by "
        "the traversal, not by a list of names"
    )
    assert {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()} == packaged, (
        "a refused run wrote or removed something"
    )


def test_no_installer_control_flow_branches_on_a_skill_name(tmp_path: Path) -> None:
    """D-06/D-26, mechanically: a new skill costs the installer zero lines.

    ``_case_data_driven_discovery`` already proves an unknown skill installs.
    This proves the converse property that makes it durable — the module holds
    no branch keyed to a skill name at all, so the discovery property cannot be
    quietly eroded one special case at a time. Read off the AST rather than by
    grepping the text, because the docstring at ``install.py`` line ~1064 names
    ``gnd-orm-core`` in an example and a text scan would have to either red on
    prose or be loosened until it caught nothing.
    """
    import ast

    source = Path(install.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)

    # Every string literal that is not inside a docstring position.
    docstrings = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Module | ast.ClassDef | ast.FunctionDef | ast.AsyncFunctionDef):
            first = node.body[0] if node.body else None
            if (
                isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)
            ):
                docstrings.add(id(first.value))

    offenders = [
        node.value
        for node in ast.walk(tree)
        if isinstance(node, ast.Constant)
        and isinstance(node.value, str)
        and id(node) not in docstrings
        and node.value in EXPECTED_SKILL_NAMES
    ]
    assert not offenders, (
        f"src/gnd/install.py carries executable references to skill names "
        f"{sorted(set(offenders))}. Discovery is a traversal (D-06): a skill "
        f"that needs an installer branch is a skill the next one will need too."
    )
