"""Install lifecycle: ``gnd doctor`` diagnoses, ``gnd uninstall`` removes (PKG-07).

Two rules are asserted adversarially here because breaking either is worse than
never shipping the commands at all.

1. **``uninstall`` never deletes a file the user modified.** Removal is gated on
   the manifest digest matching the current bytes, so a ``modified`` file is
   retained, reported, and carries a non-zero exit. An uninstaller that eats a
   user's edits is worse than one that leaves litter (D-11).
2. **A manifest entry naming a path outside the target root deletes NOTHING,
   anywhere.** Not "skip the bad entry and proceed" — a manifest carrying one
   hostile entry is evidence the whole document is untrusted, and a
   partially-honoured hostile manifest is a successful attack (T-01.2-15).

``diagnose`` inherits :func:`gnd.install.plan`'s **closed enumeration** from plan
01.2-02 and must not add a directory walk of its own to "be thorough": every
target root is shared, and reporting a user's own skills as GND drift is how a
diagnostic becomes noise nobody reads. ``test_diagnose_is_blind_to_unrelated_...``
is the regression lock, and it is built on a POPULATED root on purpose — a case
built under an empty ``tmp_path`` passes vacuously and evidences nothing.

Every subprocess-level test redirects ``HOME``. ``doctor`` inspects **both**
scopes regardless of the flags it was given (Pitfall 6), so a test that did not
redirect would read the developer's real ``~/.claude/skills`` into its verdict.
"""

from __future__ import annotations

import inspect
import json
import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable, Iterator
from pathlib import Path, PurePosixPath
from typing import Any, NamedTuple

import pytest
from support.digests import sha256_bytes as _digest

from gnd import cli, install

#: The packaged tree ships 59 files across 15 skills — the same duplicated guard
#: ``tests/test_install.py`` keeps, for the same reason.
EXPECTED_SKILL_FILE_COUNT = 65

#: The fifteen packaged skill directories, which is the artifact set in symlink
#: mode: one link per skill. Named rather than counted so a removal that drops
#: one and gains another cannot cancel out.
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
SAMPLE_SKILL = "gnd-orm-core"
SAMPLE_FILE = "gnd-orm-core/SKILL.md"

#: The link targets plan 01 wrote by hand and plan 04's installer must reproduce
#: byte-identically (D-12). Written out rather than read from the repo so the
#: test pins a VALUE: reading the links and comparing them to themselves would
#: pass whatever they became.
#:
#: Four entries became eight when phase 02.1 added gnd-extract and
#: gnd-render-doc, ten when plan 03-04 added gnd-codegen, and twelve when plan
#: 03-06 added gnd-conformance. The checkout's own
#: ``.claude/skills/`` and ``.codex/skills/`` carry one git-tracked symlink per
#: packaged skill, so a new skill is only reachable from a fresh clone once BOTH
#: links exist and are pinned here (D-06/D-21 — the Codex root stays
#: ``.codex/skills/``). A skill nobody linked ships in the wheel and is invisible
#: to anyone working in the checkout.
#:
#: Twelve became eighteen when Phase 4 added gnd-model-evolve,
#: gnd-model-from-code and gnd-review-panel. The three skills shipped in the
#: wheel across plans 04-05..04-11 while the checkout linked six — which is the
#: exact failure this pin names: for six commits an agent working in this
#: repository could not see three of GND's own skills, and every count in the
#: suite was green about it because no count reads the checkout.
#:
#: Eighteen became twenty when the panel updater (gnd-update-review-panel)
#: landed — that move was never appended here — and twenty became twenty-four
#: in quick 260816-rjw with the two loop skills, gnd-dev-session and gnd-solve.
#: Twenty-four became twenty-six in milestone v1.2 with gnd-new-project, the
#: `.gnd-planning/` scaffold, and twenty-six became twenty-eight in milestone
#: v2.0 phase 6a with gnd-adopt, the GSD migration skill.
REPOSITORY_LINK_TARGETS: dict[str, str] = {
    ".claude/skills/gnd-export": "../../src/gnd/skills/gnd-export",
    ".codex/skills/gnd-export": "../../src/gnd/skills/gnd-export",
    ".claude/skills/gnd-adopt": "../../src/gnd/skills/gnd-adopt",
    ".claude/skills/gnd-codegen": "../../src/gnd/skills/gnd-codegen",
    ".claude/skills/gnd-conformance": "../../src/gnd/skills/gnd-conformance",
    ".claude/skills/gnd-dev-session": "../../src/gnd/skills/gnd-dev-session",
    ".claude/skills/gnd-extract": "../../src/gnd/skills/gnd-extract",
    ".claude/skills/gnd-model-evolve": "../../src/gnd/skills/gnd-model-evolve",
    ".claude/skills/gnd-model-from-code": "../../src/gnd/skills/gnd-model-from-code",
    ".claude/skills/gnd-new-project": "../../src/gnd/skills/gnd-new-project",
    ".claude/skills/gnd-orm-core": "../../src/gnd/skills/gnd-orm-core",
    ".claude/skills/gnd-model-from-text": "../../src/gnd/skills/gnd-model-from-text",
    ".claude/skills/gnd-render-doc": "../../src/gnd/skills/gnd-render-doc",
    ".claude/skills/gnd-review-panel": "../../src/gnd/skills/gnd-review-panel",
    ".claude/skills/gnd-review-panel-light": "../../src/gnd/skills/gnd-review-panel-light",
    ".claude/skills/gnd-solve": "../../src/gnd/skills/gnd-solve",
    ".claude/skills/gnd-update-review-panel": "../../src/gnd/skills/gnd-update-review-panel",
    ".codex/skills/gnd-adopt": "../../src/gnd/skills/gnd-adopt",
    ".codex/skills/gnd-codegen": "../../src/gnd/skills/gnd-codegen",
    ".codex/skills/gnd-conformance": "../../src/gnd/skills/gnd-conformance",
    ".codex/skills/gnd-dev-session": "../../src/gnd/skills/gnd-dev-session",
    ".codex/skills/gnd-extract": "../../src/gnd/skills/gnd-extract",
    ".codex/skills/gnd-model-evolve": "../../src/gnd/skills/gnd-model-evolve",
    ".codex/skills/gnd-model-from-code": "../../src/gnd/skills/gnd-model-from-code",
    ".codex/skills/gnd-new-project": "../../src/gnd/skills/gnd-new-project",
    ".codex/skills/gnd-orm-core": "../../src/gnd/skills/gnd-orm-core",
    ".codex/skills/gnd-model-from-text": "../../src/gnd/skills/gnd-model-from-text",
    ".codex/skills/gnd-render-doc": "../../src/gnd/skills/gnd-render-doc",
    ".codex/skills/gnd-review-panel": "../../src/gnd/skills/gnd-review-panel",
    ".codex/skills/gnd-review-panel-light": "../../src/gnd/skills/gnd-review-panel-light",
    ".codex/skills/gnd-solve": "../../src/gnd/skills/gnd-solve",
    ".codex/skills/gnd-update-review-panel": "../../src/gnd/skills/gnd-update-review-panel",
}

#: Owned review compatibility files excluded from installer management.
COMPAT_SKILL_FILES: frozenset[str] = frozenset(
    {
        ".claude/skills/plan-review-panel/SKILL.md",
        ".codex/skills/plan-review-panel/SKILL.md",
    }
)

#: Tracked entries under the skills roots that are OURS but not packaged. A
#: repo-local skill describes how to develop THIS repository; it is not a GND
#: station skill, ships in no wheel, and the installer neither writes nor hashes
#: it. That makes it a third kind of entry, distinct from both an installer link
#: and a vendored third-party tree -- and it is named as its own kind rather than
#: folded into the foreign set, because "foreign" means "someone else's" and a
#: partition that quietly widens is how a pinned-by-value root stops being one.
#:
#: ``process-phase`` carries the milestone execution protocol: the six steps, the
#: spec-note contract, the standing design rules, and the delegation rules.
#:
#: Carried in BOTH discovery roots as a byte-identical real copy, for the reason
#: given on :data:`COMPAT_SKILL_FILES`: an agent developing this repository is
#: as likely to be Codex as Claude, and the execution protocol is the same
#: protocol either way.
LOCAL_SKILL_FILES: frozenset[str] = frozenset(
    {
        ".claude/skills/process-phase/SKILL.md",
        ".claude/skills/process-phase/references/architect-overrides.md",
        ".claude/skills/process-phase/references/agent-delegation.md",
        ".claude/skills/process-phase/references/review-and-record.md",
        ".claude/skills/process-phase/references/review-convergence.md",
        ".claude/skills/process-phase/references/spec-note-contract.md",
        ".claude/skills/process-phase/references/standing-rules.md",
        ".claude/skills/process-phase/references/verification-selection.md",
        ".codex/skills/process-phase/SKILL.md",
        ".codex/skills/process-phase/references/architect-overrides.md",
        ".codex/skills/process-phase/references/agent-delegation.md",
        ".codex/skills/process-phase/references/review-and-record.md",
        ".codex/skills/process-phase/references/review-convergence.md",
        ".codex/skills/process-phase/references/spec-note-contract.md",
        ".codex/skills/process-phase/references/standing-rules.md",
        ".codex/skills/process-phase/references/verification-selection.md",
    }
)

#: Everything tracked under a discovery root that the installer does NOT manage,
#: whoever wrote it. This is the set the tracked-file partition runs against; the
#: two halves stay separately pinned so a change to one cannot be absorbed by the
#: other.
UNMANAGED_SKILL_FILES: frozenset[str] = COMPAT_SKILL_FILES | LOCAL_SKILL_FILES

#: The two native discovery roots an agent working IN this checkout reads, each
#: mapped to the non-GND-managed entries it legitimately carries.
#:
#: The unmanaged half is pinned by VALUE for the same reason the link half is: a
#: root asserted only on its links can accumulate anything at all as long as the
#: links stay put. ``plan-review-panel`` is synthetic unmanaged external skill -- a real
#: directory of real files the installer never wrote, never hashed, and must
#: never adopt. ``process-phase`` is ours and equally unmanaged.
UNMANAGED_ROOT_ENTRIES: dict[str, frozenset[str]] = {
    ".claude/skills": frozenset({"plan-review-panel", "process-phase"}),
    ".codex/skills": frozenset({"plan-review-panel", "process-phase"}),
}

#: A second real packaged skill, used wherever a divergence has to point at
#: something that genuinely resolves. A retarget onto a nonexistent path is
#: caught by "does it dangle?"; a retarget onto a real sibling skill is caught
#: only by identity, which is the property under test.
OTHER_SKILL = "gnd-codegen"

REPO_ROOT = Path(__file__).resolve().parent.parent


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _walk(root: Any, prefix: str = "") -> Iterator[tuple[str, Any]]:
    for entry in root.iterdir():
        name = entry.name
        if entry.is_dir():
            if name.casefold() == "synced":
                continue
            yield from _walk(entry, f"{prefix}{name}/")
        else:
            yield f"{prefix}{name}", entry


def _snapshot(root: Path) -> dict[str, str]:
    """Every path under ``root``; symlinks recorded by their target string."""
    snapshot: dict[str, str] = {}
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            snapshot[rel] = f"symlink->{os.readlink(path)}"
        elif path.is_file():
            snapshot[rel] = _digest(path.read_bytes())
        else:
            snapshot[rel] = "dir"
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
    skills_root: Any = None,
) -> Any:
    source = skills_root if skills_root is not None else install.packaged_skills_root()
    target = _target(root, runtime, scope)
    manifest = install.read_manifest(root)
    records = install.plan(source, target, manifest, mode=mode)
    return install.apply(source, target, records, mode=mode, force=force, manifest=manifest)


def _diagnose(root: Path, *, runtime: str = "claude", scope: str = "project") -> Any:
    """One-target diagnosis against the real packaged tree."""
    return install.diagnose(install.packaged_skills_root(), [_target(root, runtime, scope)])


def _states(report: Any, root: Path) -> dict[str, str]:
    diagnosis = next(d for d in report.targets if Path(d.target.root) == root)
    return {record.relpath: record.state for record in diagnosis.states}


def _gnd_argv() -> list[str]:
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


def _project_and_home(tmp_path: Path) -> tuple[Path, Path]:
    project = tmp_path / "project"
    home = tmp_path / "home"
    project.mkdir()
    home.mkdir()
    return project, home


def _bump_manifest_schema(root: Path) -> None:
    path = root / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["schema"] = install.MANIFEST_SCHEMA + 1
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


def _plant_escaping_manifest_entry(root: Path, relpath: str = "../escape.txt") -> None:
    path = root / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["skills"][SAMPLE_SKILL]["files"][relpath] = {"sha256": _digest(b"x"), "size": 1}
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


def _drop_manifest_entry(root: Path, relpath: str = SAMPLE_FILE) -> None:
    """Make a file present-on-disk-but-unrecorded: the ``collided`` shape."""
    skill, rest = relpath.split("/", 1)
    path = root / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    del raw["skills"][skill]["files"][rest]
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


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


# --------------------------------------------------------------------------
# diagnose — the five states
# --------------------------------------------------------------------------


def test_diagnose_reports_every_placed_file_current_after_a_fresh_install(
    tmp_path: Path,
) -> None:
    _install(tmp_path)
    report = _diagnose(tmp_path)
    diagnosis = report.targets[0]

    assert diagnosis.installed is True
    assert len(diagnosis.states) == EXPECTED_SKILL_FILE_COUNT
    assert {record.state for record in diagnosis.states} == {"current"}
    assert report.installed_anywhere() is True
    assert report.has_drift() is False
    assert report.has_collision() is False


def test_diagnose_reports_stale_when_the_package_moved_on(tmp_path: Path) -> None:
    _install(tmp_path)
    manifest = install.read_manifest(tmp_path)
    moved_on = b"# a previous release shipped this\n"
    (tmp_path / SAMPLE_FILE).write_bytes(moved_on)
    skill, rest = SAMPLE_FILE.split("/", 1)
    manifest.skills[skill].files[rest] = install.ManifestFile(
        sha256=_digest(moved_on), size=len(moved_on)
    )
    install.write_manifest(tmp_path, manifest)

    report = _diagnose(tmp_path)
    assert _states(report, tmp_path)[SAMPLE_FILE] == "stale"
    assert report.has_drift() is True


def test_diagnose_reports_missing_for_a_recorded_file_that_is_gone(tmp_path: Path) -> None:
    _install(tmp_path)
    (tmp_path / SAMPLE_FILE).unlink()

    report = _diagnose(tmp_path)
    assert _states(report, tmp_path)[SAMPLE_FILE] == "missing"
    assert report.has_drift() is True
    assert report.has_collision() is False


def test_diagnose_reports_modified_for_a_user_edit(tmp_path: Path) -> None:
    _install(tmp_path)
    (tmp_path / SAMPLE_FILE).write_bytes(b"my own notes, appended by hand\n")

    report = _diagnose(tmp_path)
    assert _states(report, tmp_path)[SAMPLE_FILE] == "modified"
    assert report.has_drift() is True


def test_diagnose_reports_collided_for_a_file_no_manifest_records(tmp_path: Path) -> None:
    _install(tmp_path)
    _drop_manifest_entry(tmp_path)

    report = _diagnose(tmp_path)
    assert _states(report, tmp_path)[SAMPLE_FILE] == "collided"
    assert report.has_collision() is True


def test_diagnose_never_reports_create_as_a_state(tmp_path: Path) -> None:
    """``doctor`` describes what IS placed. ``create`` is a plan for the future."""
    report = _diagnose(tmp_path)
    diagnosis = report.targets[0]
    assert diagnosis.states == []
    assert diagnosis.installed is False


# --------------------------------------------------------------------------
# the closed enumeration doctor inherits (T-01.2-07b)
# --------------------------------------------------------------------------


def test_diagnose_is_blind_to_unrelated_occupants_of_a_shared_root(tmp_path: Path) -> None:
    """Regression lock. Every target root is SHARED; GND is a guest in it.

    Wave 2 proved this rule load-bearing by mutation: adding a root walk to
    ``plan()`` produced 4 failures. ``diagnose`` replays ``plan()`` and must not
    add a walk of its own — an unrelated skill must be invisible, not merely
    "reported but not counted".
    """
    unrelated = _populate_shared_root(tmp_path)
    _install(tmp_path)

    report = _diagnose(tmp_path)
    enumerated = set(_states(report, tmp_path))

    for rel in unrelated:
        assert rel not in enumerated, (
            f"{rel} is not GND's and must not be enumerated, classified, reported, "
            f"or counted toward the exit code"
        )
    assert install.MANIFEST_NAME not in enumerated, (
        "the manifest is installer metadata, never a placed asset"
    )
    assert report.has_collision() is False
    assert report.has_drift() is False


def test_diagnose_adds_no_second_classifier(tmp_path: Path) -> None:
    """One five-state decision function, like ``cli._band()``.

    A second classifier inside the diagnostic would have to hash bytes or build
    ``SkillFileState`` records of its own, so the absence of both tokens from the
    diagnostic's whole source — plus the presence of a ``plan(`` call — is a
    guard that a real reimplementation cannot slip past. The private helpers are
    swept in by prefix rather than by name so the guard does not go quiet the
    moment the classification is moved one function down.
    """
    source = "\n".join(
        inspect.getsource(function)
        for name, function in inspect.getmembers(install, inspect.isfunction)
        if name == "diagnose" or name.startswith("_diagnose")
    )
    assert "plan(" in source, "diagnose must REUSE the installer's planner, verbatim"
    for token in ("_sha256(", "read_bytes()", "SkillFileState("):
        assert token not in source, (
            f"diagnose's source contains {token!r} — that is a second classifier "
            f"growing inside the diagnostic. Classification lives in plan()."
        )


# --------------------------------------------------------------------------
# symlink-mode diagnosis (D-20)
# --------------------------------------------------------------------------


def test_diagnose_reports_a_dangling_symlink_as_missing_and_names_it(tmp_path: Path) -> None:
    """A development install links; an interpreter-version change dangles the link.

    Both environments coexist so the classifier really does see a live packaged
    tree and a dead link — deleting the source and planning against the deleted
    path proves nothing (it just raises).
    """
    root = tmp_path / "root"
    root.mkdir()
    old_env = tmp_path / "lib" / "python3.13" / "skills"
    (old_env / "gnd-orm-core").mkdir(parents=True)
    (old_env / "gnd-orm-core" / "SKILL.md").write_bytes(b"x")
    _install(root, mode="symlink", skills_root=old_env)

    new_env = tmp_path / "lib" / "python3.12" / "skills"
    (new_env / "gnd-orm-core").mkdir(parents=True)
    (new_env / "gnd-orm-core" / "SKILL.md").write_bytes(b"x")
    shutil.rmtree(tmp_path / "lib" / "python3.13")

    report = install.diagnose(new_env, [_target(root)])
    record = next(r for r in report.targets[0].states if r.relpath == "gnd-orm-core")
    assert record.state == "missing"
    assert "dangling" in record.detail, f"the reason must be in the detail: {record.detail!r}"
    assert "python3.13" in record.detail, "the detail must NAME the dangling link's target"


def test_diagnose_reports_a_symlink_install_current(tmp_path: Path) -> None:
    """The D-12 dogfood shape: a development install must be able to read clean."""
    root = tmp_path / "root"
    root.mkdir()
    _install(root, mode="symlink")

    report = _diagnose(root)
    assert {record.state for record in report.targets[0].states} == {"current"}
    assert report.has_drift() is False


# --------------------------------------------------------------------------
# corrupt manifests are refused, never interpreted
# --------------------------------------------------------------------------


def test_diagnose_refuses_a_manifest_declaring_a_higher_schema(tmp_path: Path) -> None:
    _install(tmp_path)
    _bump_manifest_schema(tmp_path)

    report = _diagnose(tmp_path)
    diagnosis = report.targets[0]
    assert diagnosis.problem, "an unreadable receipt must be REPORTED, not silently skipped"
    assert diagnosis.states == [], "nothing may be inferred from a manifest we cannot read"
    assert report.has_drift() is True
    assert report.installed_anywhere() is True


def test_diagnose_refuses_a_manifest_carrying_an_escaping_path(tmp_path: Path) -> None:
    _install(tmp_path)
    _plant_escaping_manifest_entry(tmp_path)

    report = _diagnose(tmp_path)
    diagnosis = report.targets[0]
    assert diagnosis.problem
    assert "escape.txt" in diagnosis.problem, "the offending entry must be NAMED"
    assert diagnosis.states == []
    assert report.has_drift() is True


# --------------------------------------------------------------------------
# shadowing (Pitfall 6) and environment facts (Pitfall 5)
# --------------------------------------------------------------------------


def test_diagnose_reports_a_user_scope_install_shadowing_a_project_one(tmp_path: Path) -> None:
    """Runtime precedence is personal > project — the inverse of the intuition."""
    user_root = tmp_path / "home" / ".claude" / "skills"
    project_root = tmp_path / "project" / ".claude" / "skills"
    user_root.mkdir(parents=True)
    project_root.mkdir(parents=True)
    _install(user_root, scope="global")
    _install(project_root, scope="project")

    report = install.diagnose(
        install.packaged_skills_root(),
        [_target(user_root, scope="global"), _target(project_root, scope="project")],
    )

    shadowed = {(row.runtime, row.skill) for row in report.shadowing}
    assert ("claude", SAMPLE_SKILL) in shadowed, (
        "two manifests describing the same skill names at different scopes is the "
        "detectable signature of Pitfall 6"
    )
    assert all(Path(row.shadowing_root) == user_root for row in report.shadowing)
    assert all(Path(row.shadowed_root) == project_root for row in report.shadowing)


def _shim(tmp_path: Path) -> tuple[Path, Path]:
    """``<bin>/gnd`` as a symlink into a private dir — ``uv tool install``'s layout.

    Returns the directory ON PATH and the one that is not. No real executable is
    needed: ``executable_directory`` reads ``sys.argv[0]`` and the filesystem,
    nothing more.
    """
    private = tmp_path / "tools" / "get-nick-done" / "bin"
    private.mkdir(parents=True)
    (private / "gnd").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    on_path = tmp_path / "toolbin"
    on_path.mkdir()
    (on_path / "gnd").symlink_to(private / "gnd")
    return on_path, private


def test_diagnose_reports_the_directory_the_executable_was_found_in_not_its_target(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """F-02. This assertion used to read ``isinstance(..., bool)`` and could not fail.

    ``uv tool install`` puts a symlink on PATH pointing into a directory it
    deliberately keeps OFF PATH. ``.resolve().parent`` followed the link and
    answered about its target, so ``doctor`` told a correctly-installed user to
    run ``uv tool update-shell`` in the session in which ``gnd`` was on PATH.
    """
    on_path, private = _shim(tmp_path)
    monkeypatch.setattr(sys, "argv", [str(on_path / "gnd"), "doctor"])
    monkeypatch.setenv("PATH", str(on_path))

    report = install.diagnose(install.packaged_skills_root(), [])

    assert Path(report.executable_dir) == on_path.resolve(), (
        f"the question is 'is the directory PATH must contain on PATH?', and that "
        f"is the directory holding the name the shell resolved — not {private}, "
        f"which is a path the user must NOT add to PATH"
    )
    assert report.executable_on_path is True


def test_diagnose_reports_not_on_path_when_the_found_directory_really_is_absent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The complement, so the verdict above cannot be satisfied by always answering yes."""
    on_path, _private = _shim(tmp_path)
    monkeypatch.setattr(sys, "argv", [str(on_path / "gnd"), "doctor"])
    monkeypatch.setenv("PATH", "/usr/bin:/bin")

    report = install.diagnose(install.packaged_skills_root(), [])

    assert Path(report.executable_dir) == on_path.resolve()
    assert report.executable_on_path is False


def test_diagnose_names_the_codex_location_gnd_does_not_write(tmp_path: Path) -> None:
    report = install.diagnose(
        install.packaged_skills_root(),
        [_target(tmp_path / ".codex" / "skills", runtime="codex")],
    )
    alternative = report.targets[0].alternative_root
    assert alternative is not None
    assert Path(alternative).name == "skills"
    assert Path(alternative).parent.name == ".agents", (
        "the published docs and the shipped binary disagree about the Codex root and "
        "both were observed live; naming the one GND does NOT write is what makes a "
        "future documentation-driven change diagnosable rather than mysterious"
    )


def test_diagnose_offers_no_alternative_root_for_claude(tmp_path: Path) -> None:
    report = _diagnose(tmp_path)
    assert report.targets[0].alternative_root is None


# --------------------------------------------------------------------------
# gnd doctor — the CLI surface and its exit codes
# --------------------------------------------------------------------------


def test_doctor_exits_zero_when_everything_is_current(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    assert _run_gnd(["install", "--project"], cwd=project, HOME=str(home)).returncode == 0

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert result.returncode == 0, f"{result.returncode}\n{result.stdout}\n{result.stderr}"
    assert "current" in result.stdout


@pytest.mark.parametrize(
    "mutation,expected_state,expected_code",
    [
        ("delete", "missing", cli.EXIT_DRIFT),
        ("edit", "modified", cli.EXIT_DRIFT),
        ("unrecord", "collided", cli.EXIT_COLLISION),
    ],
    ids=["missing-is-10", "modified-is-10", "collided-is-11"],
)
def test_doctor_maps_each_state_to_its_exit_code(
    tmp_path: Path, mutation: str, expected_state: str, expected_code: int
) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    root = project / ".claude" / "skills"

    if mutation == "delete":
        (root / SAMPLE_FILE).unlink()
    elif mutation == "edit":
        (root / SAMPLE_FILE).write_bytes(b"my own edit\n")
    else:
        _drop_manifest_entry(root)

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert result.returncode == expected_code, (
        f"expected {expected_code}, got {result.returncode}\n{result.stdout}"
    )
    assert expected_state in result.stdout
    assert SAMPLE_FILE in result.stdout


def test_doctor_reports_stale_as_drift(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    root = project / ".claude" / "skills"

    moved_on = b"# a previous release shipped this\n"
    (root / SAMPLE_FILE).write_bytes(moved_on)
    manifest = install.read_manifest(root)
    skill, rest = SAMPLE_FILE.split("/", 1)
    manifest.skills[skill].files[rest] = install.ManifestFile(
        sha256=_digest(moved_on), size=len(moved_on)
    )
    install.write_manifest(root, manifest)

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_DRIFT, f"{result.returncode}\n{result.stdout}"
    assert "stale" in result.stdout


def test_doctor_with_no_manifest_anywhere_exits_12_and_names_every_root(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))

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
            f"there is no central registry to inspect instead, so doctor must say "
            f"WHICH roots it checked. Missing {expected} from:\n{result.stdout}"
        )


def test_doctor_checks_both_scopes_whichever_flag_was_passed(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--global"], cwd=project, HOME=str(home))
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))

    for flag in ("--project", "--global"):
        result = _run_gnd(["doctor", flag], cwd=project, HOME=str(home))
        assert "shadow" in result.stdout.lower(), (
            f"`gnd doctor {flag}` must report the shadowing relationship regardless "
            f"of the scope flag — a user shadowed by an earlier global install is the "
            f"single most common 'I installed it and nothing happened' report.\n"
            f"{result.stdout}"
        )
        assert str(home / ".claude" / "skills") in result.stdout
        assert str(project / ".claude" / "skills") in result.stdout


def test_doctor_prints_the_executable_directory_and_a_path_verdict(tmp_path: Path) -> None:
    """F-02. This used to assert only that ``'on path'`` OR ``'not on path'`` appeared —
    a disjunction over the only two possible verdicts, which cannot fail whichever
    one is produced. It now pins the VALUE: ``gnd`` is invoked here from a
    directory that is on this process's PATH, so the verdict is not open.

    The end-to-end lock through a ``uv tool install`` shaped symlink shim lives in
    ``tests/test_verification_fixes.py``; this one keeps the CLI's own rendering
    honest.
    """
    project, home = _project_and_home(tmp_path)
    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))

    line = next(
        row for row in result.stdout.splitlines() if row.startswith("executable directory:")
    )
    invoked_from = Path(_gnd_argv()[0]).parent.resolve()
    assert str(invoked_from) in line, f"{invoked_from} is where gnd was invoked from\n{line}"
    assert "(on PATH)" in line and "NOT on PATH" not in line, (
        f"a successful install followed by 'command not found' is the most common "
        f"confusing outcome, and this `gnd` was found on PATH by this very "
        f"process.\n{line}"
    )
    assert "uv tool update-shell" not in result.stdout, (
        "the remedy must not be offered against a verdict that does not call for it"
    )


def test_doctor_names_the_alternative_codex_location(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert ".agents" in result.stdout


@pytest.mark.parametrize("corruption", ["schema", "escape"], ids=["higher-schema", "escaping-path"])
def test_doctor_refuses_a_corrupt_manifest_and_exits_10(tmp_path: Path, corruption: str) -> None:
    # A path component is not a reported skill state. Keep this spelling in the
    # real CLI output so a global substring assertion cannot regress unnoticed.
    tmp_path = tmp_path / "current"
    tmp_path.mkdir()
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    # Both project roots, so a healthy sibling cannot supply the `current` the
    # assertion below forbids and make this pass for the wrong reason.
    for root in (project / ".claude" / "skills", project / ".codex" / "skills"):
        if corruption == "schema":
            _bump_manifest_schema(root)
        else:
            _plant_escaping_manifest_entry(root)

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_DRIFT, (
        f"expected {cli.EXIT_DRIFT}, got {result.returncode}\n{result.stdout}"
    )
    assert "REFUSED" in result.stdout, "an untrusted receipt must be reported, not skipped"
    assert not any(
        line.startswith(("  installed (", "  [")) for line in result.stdout.splitlines()
    ), "nothing may be inferred from a manifest this build cannot read"


def test_doctor_elides_a_long_state_list(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    root = project / ".claude" / "skills"
    for rel in list(install.read_manifest(root).file_entries()):
        (root / rel).unlink()

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert "elided" in result.stdout, (
        f"a five-target run over 29 files each must not bury the headline "
        f"(cap {install.MAX_REPORTED_STATES})\n{result.stdout}"
    )


def test_doctor_offers_no_format_flag(tmp_path: Path) -> None:
    """D-25: a decision, not an omission."""
    project, home = _project_and_home(tmp_path)
    result = _run_gnd(["doctor", "--format", "json"], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_USAGE, f"{result.returncode}\n{result.stderr}"


def test_doctor_help_is_available() -> None:
    result = subprocess.run(
        [*_gnd_argv(), "doctor", "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "doctor" in result.stdout


# --------------------------------------------------------------------------
# remove — hash-gated deletion
# --------------------------------------------------------------------------


def _remove(root: Path, *, runtime: str = "claude", scope: str = "project") -> Any:
    target = _target(root, runtime, scope)
    return install.remove(install.packaged_skills_root(), target, install.read_manifest(root))


def test_remove_deletes_every_hash_matching_file_and_prunes(tmp_path: Path) -> None:
    _install(tmp_path)
    result = _remove(tmp_path)

    assert len(result.removed) == EXPECTED_SKILL_FILE_COUNT
    assert result.retained == []
    assert result.manifest_removed is True
    assert not (tmp_path / install.MANIFEST_NAME).exists()
    assert list(tmp_path.iterdir()) == [], (
        f"the root must hold no skill directories, no receipt, and no empty "
        f"leftovers: {sorted(p.name for p in tmp_path.iterdir())}"
    )


def test_remove_retains_a_user_modified_file_byte_identical(tmp_path: Path) -> None:
    """D-11, the rule this whole command is shaped around."""
    _install(tmp_path)
    edit = b"# my own notes, added by hand\n"
    (tmp_path / SAMPLE_FILE).write_bytes(edit)

    result = _remove(tmp_path)

    assert (tmp_path / SAMPLE_FILE).read_bytes() == edit, (
        "an uninstaller that deletes a user's edits is worse than one that leaves litter"
    )
    assert [record.relpath for record in result.retained] == [SAMPLE_FILE]
    assert result.retained[0].state == "modified"
    assert (tmp_path / SAMPLE_SKILL).is_dir(), "the parent directories of a retained file stay"
    assert result.manifest_removed is False, (
        "the receipt is removed only when everything it claimed was removed — "
        "otherwise a later doctor could only classify the survivor as unmanaged"
    )


def test_remove_retains_a_file_the_manifest_never_claimed(tmp_path: Path) -> None:
    _install(tmp_path)
    _drop_manifest_entry(tmp_path)
    before = (tmp_path / SAMPLE_FILE).read_bytes()

    result = _remove(tmp_path)

    assert (tmp_path / SAMPLE_FILE).read_bytes() == before, "not GND's to delete at all"
    assert [record.relpath for record in result.retained] == [SAMPLE_FILE]
    assert result.retained[0].state == "collided"


def test_remove_prunes_only_the_directories_it_emptied(tmp_path: Path) -> None:
    _install(tmp_path)
    keeper = tmp_path / SAMPLE_SKILL / "references" / "mine.md"
    keeper.write_bytes(b"a note I dropped into an installed skill directory\n")

    _remove(tmp_path)

    assert keeper.is_file(), "a directory that still holds a retained file must survive"
    assert not (tmp_path / "gnd-model-from-text").exists(), (
        "a directory the removal emptied must be pruned"
    )


def test_remove_deletes_the_manifest_last(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ordering is a diagnosability contract, the mirror of D-23's manifest-last write.

    Removing the receipt first would leave orphaned files that a later ``doctor``
    could only classify as unmanaged.
    """
    order: list[str] = []
    real_unlink = install._unlink

    def _tracking(
        root: Path,
        relpath: str,
        *,
        expected: install.LeafIdentity | None = None,
    ) -> None:
        order.append(PurePosixPath(relpath).name)
        real_unlink(root, relpath, expected=expected)

    monkeypatch.setattr(install, "_unlink", _tracking)
    _install(tmp_path)
    _remove(tmp_path)

    assert order[-1] == install.MANIFEST_NAME, f"receipt removed out of order: {order[-3:]}"
    assert order.count(install.MANIFEST_NAME) == 1


# --------------------------------------------------------------------------
# remove — total refusal on an untrusted receipt (T-01.2-15, T-01.2-17)
# --------------------------------------------------------------------------


def _hostile_manifest(root: Path, relpath: str) -> Any:
    """A manifest object carrying ``relpath``, built WITHOUT ``read_manifest``.

    ``read_manifest`` refuses a hostile entry at the trust boundary, so a test
    that went through it would prove only the outer guard. ``remove`` must refuse
    on its own — the two layers are asserted separately on purpose.
    """
    raw = json.loads((root / install.MANIFEST_NAME).read_text(encoding="utf-8"))
    raw["skills"][SAMPLE_SKILL]["files"][relpath] = {"sha256": _digest(b"x"), "size": 1}
    return install.Manifest.model_validate(raw)


def test_remove_refuses_an_escaping_entry_and_deletes_nothing_anywhere(tmp_path: Path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    sentinel = tmp_path / "escape.txt"
    payload = b"uninstall must never reach this\n"
    sentinel.write_bytes(payload)
    _install(root)
    before = _snapshot(root)

    with pytest.raises(install.InstallPathError) as failure:
        install.remove(
            install.packaged_skills_root(), _target(root), _hostile_manifest(root, "../escape.txt")
        )

    assert "escape.txt" in str(failure.value), "the offending entry must be NAMED"
    assert sentinel.read_bytes() == payload
    assert _snapshot(root) == before, (
        "the refusal must be TOTAL: deleting the well-formed entries and skipping the "
        "bad one is a partially-honoured hostile manifest, which is a successful attack"
    )


def test_remove_refuses_a_higher_schema_and_deletes_nothing(tmp_path: Path) -> None:
    _install(tmp_path)
    before = _snapshot(tmp_path)
    manifest = install.read_manifest(tmp_path)
    manifest.schema_version = install.MANIFEST_SCHEMA + 1

    with pytest.raises(install.ManifestSchemaError):
        install.remove(install.packaged_skills_root(), _target(tmp_path), manifest)

    assert _snapshot(tmp_path) == before, "refuse rather than delete on a guess"


# --------------------------------------------------------------------------
# remove — symlink mode never follows the link (T-01.2-18)
# --------------------------------------------------------------------------


def test_remove_unlinks_a_symlink_install_without_following_it(tmp_path: Path) -> None:
    packaged_root = Path(str(install.packaged_skills_root()))
    before = {rel: resource.read_bytes() for rel, resource in _walk(install.packaged_skills_root())}
    _install(tmp_path, mode="symlink")
    assert (tmp_path / SAMPLE_SKILL).is_symlink()

    result = _remove(tmp_path)

    assert set(result.removed) == EXPECTED_SKILL_NAMES
    assert not (tmp_path / SAMPLE_SKILL).exists()
    assert not (tmp_path / SAMPLE_SKILL).is_symlink()
    assert result.manifest_removed is True

    after = {rel: resource.read_bytes() for rel, resource in _walk(install.packaged_skills_root())}
    assert after == before, (
        f"following the link would delete the installed framework's own files under "
        f"{packaged_root}; the packaged tree must be byte-identical, file by file"
    )
    assert len(after) == EXPECTED_SKILL_FILE_COUNT


def test_remove_unlinks_a_dangling_link_rather_than_leaving_litter(tmp_path: Path) -> None:
    """The two environments coexist for the reason the doctor test gives: a
    packaged tree deleted outright raises before anything is classified, so it
    would prove nothing about a dangling link."""
    root = tmp_path / "root"
    root.mkdir()
    old_env = tmp_path / "lib" / "python3.13" / "skills"
    (old_env / "gnd-orm-core").mkdir(parents=True)
    (old_env / "gnd-orm-core" / "SKILL.md").write_bytes(b"x")
    _install(root, mode="symlink", skills_root=old_env)

    new_env = tmp_path / "lib" / "python3.12" / "skills"
    (new_env / "gnd-orm-core").mkdir(parents=True)
    (new_env / "gnd-orm-core" / "SKILL.md").write_bytes(b"x")
    shutil.rmtree(tmp_path / "lib" / "python3.13")
    assert (root / "gnd-orm-core").is_symlink() and not (root / "gnd-orm-core").exists()

    result = install.remove(new_env, _target(root), install.read_manifest(root))

    assert not (root / "gnd-orm-core").is_symlink(), (
        "a dangling link is still a placed artifact; unlinking one cannot touch a "
        "target that no longer exists, so leaving it behind is pure litter"
    )
    assert result.manifest_removed is True


# --------------------------------------------------------------------------
# gnd uninstall — the CLI surface
# --------------------------------------------------------------------------


def test_uninstall_removes_a_clean_install_and_exits_zero(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert result.returncode == 0, f"{result.returncode}\n{result.stdout}\n{result.stderr}"
    for runtime in (".claude", ".codex"):
        root = project / runtime / "skills"
        assert list(root.iterdir()) == [], f"{root} still holds {list(root.iterdir())}"


def test_uninstall_retains_a_user_edit_names_it_and_exits_10(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    edit = b"# mine\n"
    for runtime in (".claude", ".codex"):
        (project / runtime / "skills" / SAMPLE_FILE).write_bytes(edit)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert result.returncode == cli.EXIT_DRIFT, (
        f"expected {cli.EXIT_DRIFT}, got {result.returncode}\n{result.stdout}"
    )
    assert SAMPLE_FILE in result.stdout, "the retained file must be NAMED"
    for runtime in (".claude", ".codex"):
        assert (project / runtime / "skills" / SAMPLE_FILE).read_bytes() == edit


def test_uninstall_with_no_manifest_exits_12_and_changes_nothing(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    (project / ".claude" / "skills").mkdir(parents=True)
    _populate_shared_root(project / ".claude" / "skills")
    before = _snapshot(project)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert result.returncode == cli.EXIT_NO_INSTALL, (
        f"expected {cli.EXIT_NO_INSTALL}, got {result.returncode}\n{result.stdout}"
    )
    assert _snapshot(project) == before, "nothing may be created, modified, or deleted"


def test_uninstall_refuses_a_corrupt_receipt_and_deletes_nothing(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    for runtime in (".claude", ".codex"):
        _plant_escaping_manifest_entry(project / runtime / "skills")
    before = _snapshot(project)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert result.returncode == cli.EXIT_IO, (
        f"a receipt this build cannot trust is an I/O-class refusal, not a report "
        f"that files were retained: got {result.returncode}\n{result.stdout}"
    )
    assert "escape.txt" in result.stdout
    assert _snapshot(project) == before


def test_uninstall_only_touches_the_scope_it_was_pointed_at(tmp_path: Path) -> None:
    """``doctor`` inspects both scopes because it only reports. ``uninstall`` acts."""
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--global"], cwd=project, HOME=str(home))
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    before = _snapshot(home)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert result.returncode == 0, f"{result.returncode}\n{result.stdout}"
    assert _snapshot(home) == before, "a project uninstall must not reach the user scope"


def test_uninstall_offers_no_format_flag(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    result = _run_gnd(["uninstall", "--format", "json"], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_USAGE, f"{result.returncode}\n{result.stderr}"


def test_uninstall_help_is_available() -> None:
    result = subprocess.run(
        [*_gnd_argv(), "uninstall", "--help"], capture_output=True, text=True, check=False
    )
    assert result.returncode == 0
    assert "uninstall" in result.stdout


# --------------------------------------------------------------------------
# D-12 — this repository's own skill links are the installer's output
# --------------------------------------------------------------------------


def test_the_repository_carries_exactly_the_pinned_link_targets() -> None:
    """The value half of the D-12 proof.

    Reading the four links and comparing them to themselves would pass whatever
    they became, so :data:`REPOSITORY_LINK_TARGETS` pins the strings plan 01
    wrote by hand and this asserts the checkout still matches them. The
    installer-output half is the next test; together they are what "byte-identical
    to the hand-maintained targets" means.
    """
    for rel, expected in REPOSITORY_LINK_TARGETS.items():
        link = REPO_ROOT / rel
        assert link.is_symlink(), f"{rel} must stay a git-tracked symlink"
        assert os.readlink(link) == expected, f"{rel} points at {os.readlink(link)!r}"


def test_the_repository_links_reach_a_real_skill_md() -> None:
    """D-06's guarantee: a fresh clone works for both runtimes with no bootstrap."""
    for rel in REPOSITORY_LINK_TARGETS:
        entry = REPO_ROOT / rel / "SKILL.md"
        assert entry.is_file(), f"{rel} does not resolve to a skill: {entry}"


def test_a_development_install_reproduces_the_repository_link_targets(tmp_path: Path) -> None:
    """The installer's output, against a faithful copy of this repository's layout.

    The packaged tree is copied to ``<tmp>/src/gnd/skills`` and installed at
    project scope into ``<tmp>/.claude/skills`` and ``<tmp>/.codex/skills`` —
    the same two-levels-up relationship the checkout has. That is what makes the
    produced relative targets comparable to the tracked ones at all: an install
    into an arbitrary temporary directory would link back to the real checkout
    and produce a correct but incomparable path.

    Byte identity of the LINK TARGETS is the assertion, not that the links
    exist. Links pointing anywhere would satisfy the weaker claim while
    silently breaking every one of the 47 sibling-relative cross-skill links.
    """
    layout = tmp_path.resolve()
    source = layout / "src" / "gnd" / "skills"
    source.parent.mkdir(parents=True)
    shutil.copytree(Path(str(install.packaged_skills_root())), source, symlinks=True)

    produced: dict[str, str] = {}
    for runtime in ("claude", "codex"):
        root = layout / f".{runtime}" / "skills"
        root.mkdir(parents=True)
        target = install.InstallTarget(runtime=runtime, scope="project", root=root)
        records = install.plan(source, target, None, mode="symlink")
        install.apply(source, target, records, mode="symlink")
        for link in sorted(root.iterdir()):
            if link.is_symlink():
                produced[f".{runtime}/skills/{link.name}"] = os.readlink(link)

    assert produced == REPOSITORY_LINK_TARGETS, (
        "the installer must reproduce the hand-maintained link targets exactly; "
        "anything else means D-12's swap changed the repository's behaviour"
    )
    for rel in produced:
        assert (layout / rel / "SKILL.md").is_file(), f"{rel} does not resolve"
    for runtime in ("claude", "codex"):
        assert (layout / f".{runtime}" / "skills" / install.MANIFEST_NAME).is_file(), (
            "a development install writes a receipt, which is what makes "
            "`gnd doctor --project` able to say anything about this checkout"
        )


def test_the_repository_install_receipts_are_not_tracked_by_git() -> None:
    """They record an install timestamp and a mode: a file that differs on every
    machine while claiming to describe all of them. The LINKS stay tracked."""
    tracked = subprocess.run(
        ["git", "ls-files", ".claude/skills", ".codex/skills"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.split()
    assert tracked, "git ls-files returned nothing; is this a checkout?"
    assert not [entry for entry in tracked if install.MANIFEST_NAME in entry], (
        f"an install receipt is tracked by git: {tracked}"
    )
    # The skills roots hold TWO kinds of tracked entry and only one of them is
    # GND's. The installer owns the symlinks in REPOSITORY_LINK_TARGETS; a
    # non-GND skill vendored into the checkout (see COMPAT_SKILL_FILES) is a
    # plain file the installer neither writes nor manages. Comparing the raw
    # `git ls-files` output to the link set alone conflated them, so vendoring
    # any third-party skill reddened a test about install receipts.
    #
    # Both sets stay pinned by VALUE. Partitioning without pinning the foreign
    # half would let this root accumulate anything at all — the assertion has to
    # be able to fail on an unexpected addition, not just on a missing link.
    unmanaged = sorted(entry for entry in tracked if entry in UNMANAGED_SKILL_FILES)
    managed = sorted(entry for entry in tracked if entry not in UNMANAGED_SKILL_FILES)
    # This can only fire on a MISSING unmanaged entry — an unexpected one is not
    # in UNMANAGED_SKILL_FILES, so it lands in `managed` and reds the next
    # assertion instead. Describing it as "unexpected" printed an empty list and
    # named the wrong cause.
    assert unmanaged == sorted(UNMANAGED_SKILL_FILES), (
        f"a pinned installer-unmanaged skill file is no longer tracked: "
        f"{sorted(set(UNMANAGED_SKILL_FILES) - set(tracked))}"
    )
    assert managed == sorted(REPOSITORY_LINK_TARGETS)
    # An unmanaged skill must never be a symlink into uv's tool environment — that
    # is the breakage PKG-02 chose copies to avoid, and it would also make the
    # entry indistinguishable from installer output.
    for entry in UNMANAGED_SKILL_FILES:
        assert not (REPO_ROOT / entry).is_symlink(), f"{entry} must be a real file"


# --------------------------------------------------------------------------
# the adversarial corpus for the DELETE path
# --------------------------------------------------------------------------


def _case_user_edit_survives_uninstall(tmp_path: Path) -> None:
    """Regression lock on the hash gate, asserted end-to-end through the CLI."""
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    root = project / ".claude" / "skills"
    deep = SAMPLE_SKILL + "/references/provenance-and-modality.md"
    edit = (root / deep).read_bytes() + b"\n<!-- my own note, three levels down -->\n"
    (root / deep).write_bytes(edit)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert (root / deep).read_bytes() == edit, "the edit must survive byte-identical"
    assert (root / SAMPLE_SKILL / "references").is_dir(), "its parent chain must survive with it"
    assert result.returncode == cli.EXIT_DRIFT, (
        f"a run that left something behind must not report success: {result.returncode}"
    )
    assert deep in result.stdout, "and it must say WHAT it left behind"
    assert (root / install.MANIFEST_NAME).is_file(), (
        "the receipt survives with the file it still describes; removing it would leave "
        "the survivor unattributable to anything"
    )


def _case_traversal_total_refusal(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    sentinel = tmp_path / "id_rsa"
    payload = b"a file no uninstaller has any business reading, let alone deleting\n"
    sentinel.write_bytes(payload)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    # The abort is per-root by design (T-01.2-15 names the root), so both project
    # roots carry the hostile entry: a healthy sibling being removed correctly
    # would otherwise read as a partial honouring of the hostile one.
    for runtime in (".claude", ".codex"):
        _plant_escaping_manifest_entry(project / runtime / "skills", relpath="../../../id_rsa")
    before = _snapshot(project)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert sentinel.read_bytes() == payload
    assert _snapshot(project) == before, (
        "the refusal must be total — not 'delete the good entries, skip the bad one'"
    )
    assert "id_rsa" in result.stdout, "the offending entry must be named"
    assert result.returncode == cli.EXIT_IO


def _case_schema_confusion_refusal(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    _run_gnd(["install", "--project"], cwd=project, HOME=str(home))
    for runtime in (".claude", ".codex"):
        _bump_manifest_schema(project / runtime / "skills")
    before = _snapshot(project)

    result = _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home))

    assert _snapshot(project) == before
    assert result.returncode == cli.EXIT_IO
    assert "schema" in result.stdout.lower(), "and it must say why it refused"


def _case_symlink_uninstall_never_follows(tmp_path: Path) -> None:
    before = {rel: resource.read_bytes() for rel, resource in _walk(install.packaged_skills_root())}
    root = tmp_path / "root"
    root.mkdir()
    _install(root, mode="symlink")

    install.remove(install.packaged_skills_root(), _target(root), install.read_manifest(root))

    after = {rel: resource.read_bytes() for rel, resource in _walk(install.packaged_skills_root())}
    assert len(after) == EXPECTED_SKILL_FILE_COUNT
    assert after == before, "file-by-file byte identity of the packaged tree"
    assert list(root.iterdir()) == []


def _case_shared_root_survives_uninstall(tmp_path: Path) -> None:
    root = tmp_path / "skills"
    root.mkdir()
    unrelated = _populate_shared_root(root)
    _install(root)

    install.remove(install.packaged_skills_root(), _target(root), install.read_manifest(root))

    for rel, data in unrelated.items():
        assert (root / rel).read_bytes() == data, f"{rel} is not GND's and must survive"
    assert not (root / SAMPLE_SKILL).exists()


def _case_uninstall_then_doctor_reports_nothing_installed(tmp_path: Path) -> None:
    project, home = _project_and_home(tmp_path)
    assert _run_gnd(["install", "--project"], cwd=project, HOME=str(home)).returncode == 0
    assert _run_gnd(["uninstall", "--project"], cwd=project, HOME=str(home)).returncode == 0

    result = _run_gnd(["doctor", "--project"], cwd=project, HOME=str(home))
    assert result.returncode == cli.EXIT_NO_INSTALL, (
        f"after a clean uninstall the lifecycle must close: doctor sees no receipt "
        f"and no orphan. Got {result.returncode}\n{result.stdout}"
    )


def _case_planted_parent_symlink_refusal(tmp_path: Path) -> None:
    """The attack the STRING-level guard cannot see.

    ``Manifest.file_entries`` rejects ``..`` and absolute paths, so a receipt
    naming ``../../id_rsa`` never reaches the delete loop. ``planted/id_rsa`` is
    a perfectly well-formed relative path — it escapes only because ``planted``
    is a symlink pointing out of the root, which is a filesystem fact no string
    check can reach. This is the input that makes ``remove``'s own
    ``safe_destination`` pass load-bearing rather than decorative.
    """
    root = tmp_path / "root"
    root.mkdir()
    victim_dir = tmp_path / "ssh"
    victim_dir.mkdir()
    victim = victim_dir / "id_rsa"
    payload = b"-----BEGIN OPENSSH PRIVATE KEY-----\n"
    victim.write_bytes(payload)
    _install(root)

    (root / "planted").symlink_to(victim_dir, target_is_directory=True)
    raw = json.loads((root / install.MANIFEST_NAME).read_text(encoding="utf-8"))
    raw["skills"]["planted"] = {
        "files": {"id_rsa": {"sha256": _digest(payload), "size": len(payload)}}
    }
    hostile = install.Manifest.model_validate(raw)
    before = _snapshot(root)

    with pytest.raises(install.InstallPathError) as failure:
        install.remove(install.packaged_skills_root(), _target(root), hostile)

    assert "planted" in str(failure.value)
    assert victim.read_bytes() == payload, (
        "the delete would have gone THROUGH the planted link into the victim file"
    )
    assert _snapshot(root) == before, "and the refusal is total, as for any other bad entry"


class RemoveCase(NamedTuple):
    """One corpus row. ``why`` is printed on failure so a future red run explains
    itself before anyone is tempted to loosen the rule."""

    id: str
    why: str
    run: Callable[[Path], None]


REMOVE_CORPUS: list[RemoveCase] = [
    RemoveCase(
        "user-edit-survives-uninstall",
        (
            "D-11 / T-01.2-16. Deletion is gated on the manifest digest matching the "
            "current bytes, so a file the user touched is retained and reported. An "
            "uninstaller that eats a user's edits is worse than one that leaves litter, "
            "and there is deliberately no --force that reaches this path."
        ),
        _case_user_edit_survives_uninstall,
    ),
    RemoveCase(
        "traversal-total-refusal",
        (
            "T-01.2-15, the phase's live security control on the DELETE side. The "
            "receipt is JSON read back from a user-writable directory. A manifest "
            "carrying one hostile entry is evidence the whole document is untrusted, so "
            "the refusal is TOTAL — a partially-honoured hostile manifest is a "
            "successful attack, not a near miss."
        ),
        _case_traversal_total_refusal,
    ),
    RemoveCase(
        "schema-confusion-refusal",
        (
            "T-01.2-17. A receipt written by a build we do not understand must not be "
            "acted on by guess. Refusing is always the safe direction when the next "
            "step is deletion."
        ),
        _case_schema_confusion_refusal,
    ),
    RemoveCase(
        "symlink-uninstall-never-follows",
        (
            "T-01.2-18. A development install's links point INTO the installed "
            "distribution. Following one during removal would delete the framework's own "
            "packaged skills — the files every other install reads from."
        ),
        _case_symlink_uninstall_never_follows,
    ),
    RemoveCase(
        "shared-root-survives-uninstall",
        (
            "T-01.2-07b on the delete path. Every target root is shared. The closed "
            "enumeration was proven for classification in wave 2; removal drives off the "
            "receipt, so the same rule has to hold when the operation is destructive "
            "rather than merely noisy. Built on a POPULATED root: an empty one passes "
            "vacuously."
        ),
        _case_shared_root_survives_uninstall,
    ),
    RemoveCase(
        "uninstall-then-doctor-reports-nothing-installed",
        (
            "The lifecycle has to close. If uninstall leaves a receipt, an orphan file, "
            "or an empty skill directory, doctor answers 10 or 11 where the honest answer "
            "is 12 — and the user cannot tell 'removed' from 'half removed'."
        ),
        _case_uninstall_then_doctor_reports_nothing_installed,
    ),
    RemoveCase(
        "planted-parent-symlink-refusal",
        (
            "T-01.2-15 / T-01.2-06 combined, and the case that keeps `remove`'s own "
            "`safe_destination` pass alive. Every OTHER traversal case is caught one "
            "layer earlier by the manifest's string-level validation, so removing the "
            "guard from `remove` passes the rest of this corpus — measured, not assumed. "
            "`planted/id_rsa` is a well-formed relative path that escapes only through a "
            "planted directory symlink, which no string check can see."
        ),
        _case_planted_parent_symlink_refusal,
    ),
]


@pytest.mark.parametrize("case", REMOVE_CORPUS, ids=[row.id for row in REMOVE_CORPUS])
def test_remove_adversarial_case(case: RemoveCase, tmp_path: Path) -> None:
    try:
        case.run(tmp_path)
    except AssertionError as failure:
        pytest.fail(f"{case.id}: {failure}\n\nWhy this case exists: {case.why}")


def test_the_remove_corpus_covers_seven_named_cases() -> None:
    assert len(REMOVE_CORPUS) == 7
    assert len({row.id for row in REMOVE_CORPUS}) == 7
    for row in REMOVE_CORPUS:
        assert row.why.strip(), f"{row.id} carries no `why`; a red run would not explain itself"


# --------------------------------------------------------------------------
# the checkout's discovery roots, read as SETS off the filesystem itself
# --------------------------------------------------------------------------
#
# This section exists because of a specific, measured failure. `gnd-model-evolve`,
# `gnd-model-from-code` and `gnd-review-panel` shipped in the wheel from plan
# 04-05 onward while `.claude/skills/` and `.codex/skills/` linked only six
# skills. For six commits an agent working in this repository could not discover
# three of GND's own skills — and NOT ONE count assertion in the suite noticed,
# because every count read the packaged tree and none read the checkout.
#
# Everything below therefore reads the checkout roots DIRECTLY, with `lstat` and
# `readlink`. Nothing is recomputed from the package and nothing compares a
# surface with itself; where two sides are compared, each is read by its own
# mechanism.


def _checkout_entries(root_rel: str) -> tuple[dict[str, str], set[str]]:
    """``(link name -> literal target, non-link names)`` for one discovery root.

    ``lstat`` rather than ``Path.is_symlink`` so the mode is read from the
    directory entry that is actually there, and ``os.readlink`` rather than
    ``resolve()`` so the assertion is about the string on disk rather than about
    where it happens to land today. The receipt is skipped: it is installer
    metadata, gitignored, and never a placed asset.
    """
    root = REPO_ROOT / root_rel
    links: dict[str, str] = {}
    others: set[str] = set()
    for entry in sorted(root.iterdir()):
        if entry.name == install.MANIFEST_NAME:
            continue
        if stat.S_ISLNK(os.lstat(entry).st_mode):
            links[entry.name] = os.readlink(entry)
        else:
            others.add(entry.name)
    return links, others


def _packaged_skill_names() -> set[str]:
    """The shipped skill names, read from the package by its own traversal."""
    return {entry.name for entry in install.packaged_skills_root().iterdir() if entry.is_dir()}


@pytest.mark.parametrize("root_rel", sorted(UNMANAGED_ROOT_ENTRIES))
def test_each_discovery_root_links_exactly_the_packaged_skills(root_rel: str) -> None:
    """The gate that did not exist while the drift ran, and the one that closes it.

    Both sides are read independently — the left off the checkout with ``lstat``,
    the right off the package with its own traversal — and **neither side is
    :data:`REPOSITORY_LINK_TARGETS`**. That is what makes this fire on the real
    failure: a skill that starts shipping and is linked nowhere reds HERE even if
    the hand-maintained pin was never touched, which is precisely the state that
    survived six commits in silence.
    """
    links, _others = _checkout_entries(root_rel)
    packaged = _packaged_skill_names()
    missing = sorted(packaged - set(links))
    extra = sorted(set(links) - packaged)
    assert set(links) == packaged, (
        f"{root_rel} does not link the skills this build ships.\n"
        f"  shipped but NOT linked ({len(missing)}): {missing}\n"
        f"  linked but not shipped ({len(extra)}): {extra}\n"
        f"a skill nobody linked ships in the wheel and is invisible to anyone "
        f"working in this checkout"
    )


@pytest.mark.parametrize("root_rel", sorted(UNMANAGED_ROOT_ENTRIES))
def test_each_discovery_root_carries_exactly_its_pinned_links_and_foreign_entries(
    root_rel: str,
) -> None:
    """A count is not a set, and a shared root holds two different kinds of entry.

    Mutation M2 of plan 04-12 settled the first half inside this very phase:
    renaming one packaged file left the then-43-file count unchanged and five guards
    stayed green. So the literal target of every link is asserted here, and the
    non-link half is pinned beside it — an assertion that can only fail on a
    MISSING link cannot fail on an unexpected arrival.
    """
    links, others = _checkout_entries(root_rel)
    expected = {
        rel.rsplit("/", 1)[1]: target
        for rel, target in REPOSITORY_LINK_TARGETS.items()
        if rel.rsplit("/", 1)[0] == root_rel
    }
    retargeted = {
        name: (links[name], expected[name])
        for name in sorted(set(links) & set(expected))
        if links[name] != expected[name]
    }
    assert links == expected, (
        f"{root_rel} diverged from the pinned links.\n"
        f"  missing: {sorted(set(expected) - set(links))}\n"
        f"  extra: {sorted(set(links) - set(expected))}\n"
        f"  retargeted (found, pinned): {retargeted}"
    )
    unmanaged = UNMANAGED_ROOT_ENTRIES[root_rel]
    assert others == set(unmanaged), (
        f"{root_rel} holds an unexpected non-link entry: {sorted(others - unmanaged)}; "
        f"missing an expected one: {sorted(unmanaged - others)}. Every entry in a "
        f"discovery root is either a link GND owns or an artifact the installer "
        f"must never touch, and both halves are pinned so neither can grow unobserved."
    )


def test_the_pinned_link_map_cannot_lag_the_packaged_tree() -> None:
    """The pin is hand-maintained, so it gets a gate of its own.

    A D-26 sweep that updated every count but forgot the links would leave a
    perfectly self-consistent :data:`REPOSITORY_LINK_TARGETS` describing a
    checkout that is missing a skill — and the two tests above would agree with
    each other about the wrong answer. Tying the pin to an independent read of
    the package removes that degree of freedom.
    """
    packaged = _packaged_skill_names()
    assert packaged == set(EXPECTED_SKILL_NAMES), (
        f"the packaged tree and the name pin disagree: "
        f"missing {sorted(set(EXPECTED_SKILL_NAMES) - packaged)}, "
        f"extra {sorted(packaged - set(EXPECTED_SKILL_NAMES))}"
    )
    for root_rel in UNMANAGED_ROOT_ENTRIES:
        pinned = {
            rel.rsplit("/", 1)[1]
            for rel in REPOSITORY_LINK_TARGETS
            if rel.rsplit("/", 1)[0] == root_rel
        }
        assert pinned == packaged, (
            f"the pin names {sorted(pinned)} under {root_rel} but the package ships "
            f"{sorted(packaged)}"
        )
    assert len(REPOSITORY_LINK_TARGETS) == len(UNMANAGED_ROOT_ENTRIES) * len(packaged)
    for rel, target in REPOSITORY_LINK_TARGETS.items():
        canonical = f"../../src/gnd/skills/{rel.rsplit('/', 1)[1]}"
        assert target == canonical, (
            f"{rel} is pinned to {target!r}, not the canonical relative target "
            f"{canonical!r}. A link whose target is merely 'somewhere valid' breaks "
            f"every sibling-relative cross-skill link behind it."
        )


def test_every_discovery_link_is_tracked_at_symlink_mode() -> None:
    """Mode 120000 is the whole difference between a link and a text file.

    A checkout made with ``core.symlinks=false``, or a link materialised and
    re-added, is committed at 100644 carrying the target string as its contents.
    Every consumer then finds a one-line text file where a skill directory
    belongs. ``git ls-files`` WITHOUT ``-s`` reports that entry identically to a
    real link, which is why the mode is read here rather than the name.
    """
    listing = subprocess.run(
        ["git", "ls-files", "-s", ".claude/skills", ".codex/skills"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    ).stdout.splitlines()
    assert listing, "git ls-files returned nothing; is this a checkout?"
    modes = {}
    for line in listing:
        meta, _, path = line.partition("\t")
        modes[path] = meta.split()[0]

    for rel in REPOSITORY_LINK_TARGETS:
        assert modes.get(rel) == "120000", (
            f"{rel} is tracked at mode {modes.get(rel)!r}, not 120000 — git is "
            f"carrying it as file content, not as a symlink"
        )
    for rel in UNMANAGED_SKILL_FILES:
        assert rel in modes, f"a pinned unmanaged file is no longer tracked: {rel}"
        assert modes[rel] != "120000", (
            f"{rel} is real content, not installer output; an unmanaged entry "
            f"tracked at 120000 is indistinguishable from a link GND placed"
        )


def test_the_foreign_review_panel_stays_an_unmanaged_real_directory() -> None:
    """``plan-review-panel`` must remain foreign: never linked, never adopted.

    It sits in the same directory as the installer-owned links, which is the
    only reason it is at risk at all — a lifecycle that enumerated the root
    instead of the receipt would sweep it up, and a ``--force`` adoption pass
    that matched on location rather than on identity would claim it.
    """
    contents: set[str] = set()
    for root_rel in UNMANAGED_ROOT_ENTRIES:
        foreign = REPO_ROOT / root_rel / "plan-review-panel"
        assert not stat.S_ISLNK(os.lstat(foreign).st_mode), f"{root_rel}: must be a real directory"
        assert foreign.is_dir()
        contents |= {
            entry.relative_to(REPO_ROOT).as_posix()
            for entry in foreign.rglob("*")
            if not entry.is_dir()
        }
    assert "plan-review-panel" not in EXPECTED_SKILL_NAMES
    assert "plan-review-panel" not in _packaged_skill_names(), (
        "GND does not ship it, so no install of any kind may place it"
    )
    assert not any("plan-review-panel" in rel for rel in REPOSITORY_LINK_TARGETS), (
        "it is outside the managed map, and the managed map is what uninstall drives off"
    )
    assert contents == set(COMPAT_SKILL_FILES), (
        f"the vendored tree changed shape: unexpected {sorted(contents - COMPAT_SKILL_FILES)}, "
        f"absent {sorted(COMPAT_SKILL_FILES - contents)}"
    )
    for rel in COMPAT_SKILL_FILES:
        assert not stat.S_ISLNK(os.lstat(REPO_ROOT / rel).st_mode), f"{rel} must be a real file"


def test_the_local_process_skill_stays_unpackaged_and_unmanaged() -> None:
    """``process-phase`` is ours, and that is exactly why it needs its own pin.

    A vendored tree is obviously not installer output. A skill we wrote, sitting
    in the same directory as the installer's links, is the entry most likely to
    be adopted by a future lifecycle pass that matches on location rather than on
    the receipt. It describes how to develop THIS repository -- it is not a GND
    station skill, it ships in no wheel, and no install of any kind may place it.

    Pinned by VALUE like both other halves of this root: an assertion that can
    only fail on a missing file cannot fail on an unexpected arrival.
    """
    contents: set[str] = set()
    for root_rel in UNMANAGED_ROOT_ENTRIES:
        local = REPO_ROOT / root_rel / "process-phase"
        assert not stat.S_ISLNK(os.lstat(local).st_mode), f"{root_rel}: must be a real directory"
        assert local.is_dir()
        contents |= {
            entry.relative_to(REPO_ROOT).as_posix()
            for entry in local.rglob("*")
            if not entry.is_dir()
        }
        # The open skills standard keys discovery off the frontmatter name, and a
        # name that disagrees with its directory is discoverable under one spelling
        # and referenced under the other. Asserted per ROOT: a copy whose
        # frontmatter drifted is undiscoverable in the runtime that reads it.
        head = (local / "SKILL.md").read_text().split("---")[1]
        assert "name: process-phase" in head, f"{root_rel}: frontmatter name must match directory"
    assert "process-phase" not in EXPECTED_SKILL_NAMES
    assert "process-phase" not in _packaged_skill_names(), (
        "GND does not ship it, so no install of any kind may place it"
    )
    assert not any("process-phase" in rel for rel in REPOSITORY_LINK_TARGETS), (
        "it is outside the managed map, and the managed map is what uninstall drives off"
    )
    assert contents == set(LOCAL_SKILL_FILES), (
        f"the local skill tree changed shape: unexpected {sorted(contents - LOCAL_SKILL_FILES)}, "
        f"absent {sorted(LOCAL_SKILL_FILES - contents)}"
    )
    for rel in LOCAL_SKILL_FILES:
        assert not stat.S_ISLNK(os.lstat(REPO_ROOT / rel).st_mode), f"{rel} must be a real file"


def test_the_two_discovery_roots_carry_identical_unmanaged_skills() -> None:
    """An unmanaged skill is available to BOTH runtimes, and is the same skill.

    The fifteen station skills are one tree behind two links, so their identity
    across roots is structural and needs no gate. The unmanaged skills cannot be
    linked -- every link under a discovery root is installer output pointing into
    the packaged tree, so a link from one root into the other would be
    indistinguishable from a skill GND placed, and the two by-value root pins
    would stop meaning what they say. They are real copies instead, which buys
    the distinguishability at the cost of drift.

    This is the gate that pays that cost back. It compares BYTES, not names: a
    reference file edited under one root and not the other leaves an agent
    working in this checkout following a protocol that depends on which terminal
    it happens to be, which is the failure the whole arrangement exists to
    prevent. Executability is compared too -- ``run_panel.sh`` that lost its
    mode bit in one root is a skill that only half works there.
    """
    claude_root = REPO_ROOT / ".claude" / "skills"
    codex_root = REPO_ROOT / ".codex" / "skills"
    for name in sorted(UNMANAGED_ROOT_ENTRIES[".claude/skills"]):
        left, right = claude_root / name, codex_root / name
        left_files = {e.relative_to(left).as_posix() for e in left.rglob("*") if not e.is_dir()}
        right_files = {e.relative_to(right).as_posix() for e in right.rglob("*") if not e.is_dir()}
        assert left_files == right_files, (
            f"{name} holds different files under the two roots: "
            f"only in .claude {sorted(left_files - right_files)}, "
            f"only in .codex {sorted(right_files - left_files)}"
        )
        for member in sorted(left_files):
            lhs, rhs = left / member, right / member
            assert lhs.read_bytes() == rhs.read_bytes(), (
                f"{name}/{member} has drifted between the two discovery roots; "
                f"an unmanaged skill must be the same skill in either runtime"
            )
            assert os.access(lhs, os.X_OK) == os.access(rhs, os.X_OK), (
                f"{name}/{member} is executable under one root and not the other"
            )


# --------------------------------------------------------------------------
# doctor: `current` requires target, receipt identity AND packaged bytes
# --------------------------------------------------------------------------


def _linked_install(tmp_path: Path) -> tuple[Path, Path]:
    """A symlink install whose target tree is a COPY we are free to perturb.

    The real packaged tree is the installed framework's own files and no test
    writes to it. Copying it first is what makes "the bytes behind the link
    moved on" reachable at all — and the ``<tmp>/src/gnd/skills`` layout
    reproduces the checkout's two-levels-up relationship, so the link values
    produced here are the same shape as the tracked ones.
    """
    source = tmp_path / "src" / "gnd" / "skills"
    source.parent.mkdir(parents=True)
    shutil.copytree(Path(str(install.packaged_skills_root())), source, symlinks=True)
    root = tmp_path / ".claude" / "skills"
    root.mkdir(parents=True)
    _install(root, mode="symlink", skills_root=source)
    return root, source


def test_a_link_reads_current_only_when_target_receipt_and_bytes_all_agree(
    tmp_path: Path,
) -> None:
    """The positive control. Without it the corpus below could pass by never
    reporting ``current`` at all, which is the degenerate way a "never call a
    bad link current" gate stops being able to fail."""
    root, _source = _linked_install(tmp_path)

    report = install.diagnose(install.packaged_skills_root(), [_target(root)])

    assert {record.state for record in report.targets[0].states} == {"current"}
    assert report.has_drift() is False
    assert report.has_collision() is False


def _link_retargeted_to_another_real_skill(root: Path, source: Path) -> None:
    """Resolves, holds a real SKILL.md, dangles nowhere — and is the wrong skill.

    Every liveness check passes. Only the recorded identity disagrees, which is
    what makes this the case that separates "the link works" from "the link is
    the one GND placed".
    """
    link = root / SAMPLE_SKILL
    link.unlink()
    link.symlink_to(f"../../src/gnd/skills/{OTHER_SKILL}", target_is_directory=True)


def _link_replaced_by_a_real_directory(root: Path, source: Path) -> None:
    """Byte-identical content at the right path — but not a link GND placed.

    This is the case that fails if ``current`` is decided on the bytes found at
    the destination. They agree perfectly here; the artifact is still wrong.
    """
    link = root / SAMPLE_SKILL
    link.unlink()
    shutil.copytree(source / SAMPLE_SKILL, link)


def _receipt_disagrees_with_the_placed_link(root: Path, source: Path) -> None:
    """The link on disk is exactly right; the receipt claims a different one."""
    path = root / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    raw["skills"][SAMPLE_SKILL]["link_value"] = f"../../src/gnd/skills/{OTHER_SKILL}"
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")


def _link_dropped_entirely(root: Path, source: Path) -> None:
    """The 04-12 shape, one link at a time."""
    (root / SAMPLE_SKILL).unlink()


def _bytes_behind_the_link_substituted(root: Path, source: Path) -> None:
    """Exact target, exact receipt, substituted content."""
    (source / SAMPLE_FILE).write_bytes(b"# substituted behind an otherwise exact link\n")


def _a_file_behind_the_link_removed(root: Path, source: Path) -> None:
    """Exact target, exact receipt, and the link resolves — to a partial tree."""
    (source / SAMPLE_FILE).unlink()


class LinkDivergence(NamedTuple):
    """One way a link can be wrong, and the state doctor must report for it."""

    id: str
    why: str
    apply: Callable[[Path, Path], None]
    state: str
    detail_contains: str


LINK_DIVERGENCES: list[LinkDivergence] = [
    LinkDivergence(
        "retargeted-to-another-real-skill",
        (
            "T-04-14-01. The link resolves, holds a real SKILL.md and dangles nowhere, "
            "so every liveness check passes. Only the recorded identity disagrees — "
            "and an agent reading this root would silently load the wrong skill."
        ),
        _link_retargeted_to_another_real_skill,
        "modified",
        "retargeted",
    ),
    LinkDivergence(
        "replaced-by-a-real-directory-of-identical-bytes",
        (
            "T-04-14-02, and the case that forbids deciding `current` on the bytes at "
            "the destination: they agree here, byte for byte. A real directory where a "
            "link belongs is an unmanaged artifact that an upgrade must not overwrite "
            "and an uninstall must not delete."
        ),
        _link_replaced_by_a_real_directory,
        "modified",
        "a regular directory stands where a symlink belongs",
    ),
    LinkDivergence(
        "receipt-disagrees-with-the-placed-link",
        (
            "T-04-14-02 from the other side. The link on disk is exactly right; the "
            "receipt claims a different one. A receipt trusted without comparison is a "
            "receipt that can authorize mutating a path GND does not own."
        ),
        _receipt_disagrees_with_the_placed_link,
        "modified",
        "retargeted",
    ),
    LinkDivergence(
        "link-dropped-entirely",
        (
            "The 04-12 shape, one link at a time: the skill ships, the receipt claims "
            "the link, and nothing is there. This is what ran undetected for six "
            "commits across three skills."
        ),
        _link_dropped_entirely,
        "missing",
        "recorded symlink is absent",
    ),
    LinkDivergence(
        "bytes-behind-the-link-substituted",
        (
            "T-04-14-02. Target exact, receipt exact, content swapped. A link whose "
            "target string is correct proves nothing about what is behind it, so the "
            "packaged bytes are the third input `current` depends on."
        ),
        _bytes_behind_the_link_substituted,
        "stale",
        "the bytes behind the link differ",
    ),
    LinkDivergence(
        "a-file-behind-the-link-removed",
        (
            "The partial-tree variant: the link resolves and the directory exists, but "
            "the skill behind it is incomplete. An inventory read that stopped at the "
            "link would call this healthy."
        ),
        _a_file_behind_the_link_removed,
        "missing",
        "is not behind it",
    ),
]


@pytest.mark.parametrize("case", LINK_DIVERGENCES, ids=[row.id for row in LINK_DIVERGENCES])
def test_a_diverging_link_is_never_reported_current(case: LinkDivergence, tmp_path: Path) -> None:
    root, source = _linked_install(tmp_path)
    case.apply(root, source)

    report = install.diagnose(install.packaged_skills_root(), [_target(root)])
    states = {record.relpath: record for record in report.targets[0].states}
    record = states[SAMPLE_SKILL]

    try:
        assert record.state != "current", (
            f"doctor called a diverging link current. Detail: {record.detail!r}"
        )
        assert record.state == case.state, f"expected {case.state}, got {record.state}"
        assert case.detail_contains in (record.detail or ""), (
            f"the reason must be in the detail: {record.detail!r}"
        )
        assert report.has_drift() or report.has_collision(), (
            "a diverging link must reach the exit code, not merely the state list"
        )
        for name in EXPECTED_SKILL_NAMES - {SAMPLE_SKILL}:
            assert states[name].state == "current", (
                f"only {SAMPLE_SKILL} was perturbed, but {name} reads "
                f"{states[name].state} — the divergence must be attributed to the "
                f"link it belongs to, or a real report becomes unreadable"
            )
    except AssertionError as failure:
        pytest.fail(f"{case.id}: {failure}\n\nWhy this case exists: {case.why}")


def test_the_link_divergence_corpus_covers_all_three_inputs() -> None:
    """Each of target, receipt identity and packaged bytes must be able to flip
    the verdict on its own. A corpus that perturbed two of the three would leave
    the untested input free to be dropped from the comparison entirely."""
    assert len(LINK_DIVERGENCES) == 6
    assert len({row.id for row in LINK_DIVERGENCES}) == 6
    for row in LINK_DIVERGENCES:
        assert row.why.strip(), f"{row.id} carries no `why`; a red run would not explain itself"
    assert {row.state for row in LINK_DIVERGENCES} == {"modified", "missing", "stale"}


# --------------------------------------------------------------------------
# an unmanaged collision is never silently adopted
# --------------------------------------------------------------------------


def test_the_installer_refuses_to_adopt_an_unmanaged_directory_at_a_gnd_owned_name(
    tmp_path: Path,
) -> None:
    """The ``plan-review-panel`` hazard, reproduced at a name GND *does* own.

    A foreign directory sitting exactly where a link belongs is the one shape
    that could be adopted by mistake, because location alone looks like
    ownership. It is a collision, and a collision is reported and skipped —
    ``--force`` exists for the documented fresh-clone adoption of already-tracked
    GND links and has to be asked for explicitly.
    """
    source = tmp_path / "src" / "gnd" / "skills"
    source.parent.mkdir(parents=True)
    shutil.copytree(Path(str(install.packaged_skills_root())), source, symlinks=True)
    root = tmp_path / ".claude" / "skills"
    squatter = root / SAMPLE_SKILL
    squatter.mkdir(parents=True)
    payload = b"---\nname: gnd-orm-core\n---\nnot GND's, and not GND's to replace\n"
    (squatter / "SKILL.md").write_bytes(payload)

    target = _target(root)
    records = install.plan(source, target, None, mode="symlink")
    assert {record.relpath: record.state for record in records}[SAMPLE_SKILL] == "collided"

    result = install.apply(source, target, records, mode="symlink")

    assert SAMPLE_SKILL in result.collisions, "the blocked name must be reported"
    assert (squatter / "SKILL.md").read_bytes() == payload, "an unmanaged tree is untouched"
    assert not stat.S_ISLNK(os.lstat(squatter).st_mode), "and it is not converted into a link"
    assert result.manifest is None or SAMPLE_SKILL not in (result.manifest.skills or {}), (
        "a refused collision must not be claimed by the receipt; a receipt that "
        "claims it authorizes a later uninstall to delete it"
    )
    for name in EXPECTED_SKILL_NAMES - {SAMPLE_SKILL}:
        assert (root / name).is_symlink(), (
            f"{name} is unrelated to the collision and must still be placed"
        )


def test_a_legacy_receipt_is_converged_only_by_the_documented_remedy(tmp_path: Path) -> None:
    """A receipt predating the exact-link-value check leaves doctor at 10 forever.

    Found on this checkout: ``gnd-model-from-text`` and ``gnd-orm-core`` carried
    ``link_value: null`` and ``gnd doctor --project`` exited 10 with links that
    were, on disk, exactly right. **Neither documented remedy converges it** —
    ``apply`` never writes a ``modified`` record (D-11) and ``--force`` widens
    only ``collided`` — so a contributor following AGENTS.md would have run both
    commands, seen "nothing placed", and had no next step.

    This pins the shape *and* the remedy: the only way out is to delete the
    gitignored receipt, which returns the root to the fresh-clone ``collided``
    shape that ``--force`` is documented to adopt. If a future change makes
    ``apply`` converge a legacy receipt directly, this test reds and the AGENTS.md
    paragraph it guards should go with it.
    """
    root, source = _linked_install(tmp_path)
    path = root / install.MANIFEST_NAME
    raw = json.loads(path.read_text(encoding="utf-8"))
    for entry in raw["skills"].values():
        entry["link_value"] = None
    path.write_text(json.dumps(raw, indent=2) + "\n", encoding="utf-8")

    def _states_now() -> dict[str, str]:
        records = install.plan(source, _target(root), install.read_manifest(root), mode="symlink")
        return {record.relpath: record.state for record in records}

    assert set(_states_now().values()) == {"modified"}, "the legacy shape itself"

    for force in (False, True):
        records = install.plan(source, _target(root), install.read_manifest(root), mode="symlink")
        result = install.apply(
            source,
            _target(root),
            records,
            mode="symlink",
            force=force,
            manifest=install.read_manifest(root),
        )
        assert result.writes == 0, (
            f"install --force={force} placed {result.writes} record(s); a `modified` "
            f"record is never written, so this cannot be the remedy"
        )
        assert set(_states_now().values()) == {"modified"}

    path.unlink()
    records = install.plan(source, _target(root), None, mode="symlink")
    assert {record.state for record in records} == {"collided"}, (
        "deleting the receipt must reproduce the documented fresh-clone shape"
    )
    install.apply(source, _target(root), records, mode="symlink", force=True)

    report = install.diagnose(install.packaged_skills_root(), [_target(root)])
    assert {record.state for record in report.targets[0].states} == {"current"}
    assert report.has_drift() is False and report.has_collision() is False


def test_uninstall_removes_owned_links_and_leaves_a_foreign_sibling_intact(
    tmp_path: Path,
) -> None:
    """The checkout's own shape: owned links beside one vendored real skill.

    ``_case_shared_root_survives_uninstall`` proves this for a copy install. The
    symlink case is separate because removal there acts on *directory entries*
    rather than on hashed files, and a directory entry is exactly what a foreign
    skill also is.
    """
    root, source = _linked_install(tmp_path)
    foreign = root / "plan-review-panel"
    foreign.mkdir()
    payload = b"#!/bin/sh\n# synthetic unmanaged external skill; not GND's\n"
    (foreign / "run_panel.sh").write_bytes(payload)

    result = install.remove(source, _target(root), install.read_manifest(root))

    assert set(result.removed) == EXPECTED_SKILL_NAMES
    assert (foreign / "run_panel.sh").read_bytes() == payload
    assert foreign.is_dir() and not stat.S_ISLNK(os.lstat(foreign).st_mode)
    for name in EXPECTED_SKILL_NAMES:
        assert not (root / name).is_symlink() and not (root / name).exists()
    assert sorted(entry.name for entry in root.iterdir()) == ["plan-review-panel"], (
        "everything GND owned is gone and everything it did not own remains"
    )


def test_uninstall_retains_a_retargeted_link_and_never_follows_it(tmp_path: Path) -> None:
    """T-04-14-04. The link is no longer the one GND placed, so it is not GND's
    to unlink — and the removal must not travel through it into whatever it now
    names. Both halves matter: unlinking it would destroy evidence of a
    tampered install, and following it would delete a directory GND never owned.
    """
    root, source = _linked_install(tmp_path)
    victim_dir = tmp_path / "ssh"
    victim_dir.mkdir()
    victim = victim_dir / "id_rsa"
    payload = b"-----BEGIN OPENSSH PRIVATE KEY-----\n"
    victim.write_bytes(payload)
    link = root / SAMPLE_SKILL
    link.unlink()
    link.symlink_to(victim_dir, target_is_directory=True)

    result = install.remove(
        install.packaged_skills_root(), _target(root), install.read_manifest(root)
    )

    assert victim.read_bytes() == payload, "removal travelled THROUGH a link GND did not place"
    assert sorted(entry.name for entry in victim_dir.iterdir()) == ["id_rsa"]
    assert [record.relpath for record in result.retained] == [SAMPLE_SKILL]
    assert result.retained[0].state == "modified"
    assert link.is_symlink(), "a link GND did not place is not GND's to unlink either"
    assert result.manifest_removed is False, (
        "the receipt survives with the artifact it still describes"
    )
    assert (source / SAMPLE_FILE).is_file(), "and the copied packaged tree is untouched"
