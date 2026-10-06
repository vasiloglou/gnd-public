"""The six-state classifier, ``--force``, and MEASURED zero-write idempotence.

G-06's rule is **not inherited**. RESEARCH §1.3 item 2 reproduced the opposite:
``gnd extract`` was handed a hand-edited artifact and silently overwrote it at
exit 0. The six-state classifier exists only in ``install.py:784``, scoped to
skill placement with its own manifest schema — so the PATTERN transfers here and
the code does not.

Three things in this suite are load-bearing and easy to weaken by accident:

1. **Idempotence is measured, not asserted.** The test demands
   ``ApplyResult.writes == 0`` **and** per-file digest identity across two runs.
   The count alone passes on a run that rewrote every file with identical bytes;
   the digests alone pass on a run that rewrote everything. Both, or the claim
   is weaker than PKG-02's.
2. **The negative control** mutates ONE derived file and asserts exactly that
   file moves to ``modified`` while every sibling stays ``current``. A
   classifier that returned one state for everything would satisfy several of
   the other tests on its own.
3. **A refused write must not be adopted into the manifest.** Recording the
   current bytes of a hand-edited derived file would make the NEXT run classify
   it ``stale`` and rewrite it — destroying the edit one run later, through the
   guard that refused to destroy it now.
"""

from __future__ import annotations

import hashlib
import json
import os
import stat
from dataclasses import dataclass, replace
from pathlib import Path

import pytest

from gnd.cli import EXIT_COLLISION, EXIT_IO, main
from gnd.codegen.emit import emit_project, write_project
from gnd.codegen.manifest import (
    CodegenManifest,
    build_manifest,
    manifest_path,
    read_manifest,
    render_manifest,
    write_manifest,
)
from gnd.codegen.plan import (
    MAX_CLASSIFY_BYTES,
    WRITABLE_STATES,
    ApplyResult,
    CodegenPlan,
    FileState,
    apply_codegen,
    classify_file,
    plan_codegen,
)
from gnd.exp.frontmatter import read_frontmatter
from gnd.model import load_model

REPO_ROOT = Path(__file__).resolve().parent.parent
FULL_VOCABULARY = REPO_ROOT / "tests" / "fixtures" / "models" / "full_vocabulary.orm.yaml"


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------


def _emit(model_path: Path):
    model = load_model(str(model_path))
    return model, emit_project(model, str(model_path))


def _generate(root: Path, model_path: Path = FULL_VOCABULARY):
    """A fresh generated project with its manifest, the way the CLI does it."""
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    manifest = build_manifest(project, str(model_path))
    write_project(project, root, manifest_text=render_manifest(manifest))
    return project


def _states(root: Path, model_path: Path = FULL_VOCABULARY) -> dict[str, str]:
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    manifest = read_manifest(manifest_path(root)) if manifest_path(root).is_file() else None
    plan = plan_codegen(project, root, manifest)
    return {record.relpath: record.state for record in plan.files}


def _rerun(root: Path, *, force: bool = False, model_path: Path = FULL_VOCABULARY):
    model = load_model(str(model_path))
    project = emit_project(model, str(model_path), skill_name=root.resolve().name)
    manifest = read_manifest(manifest_path(root)) if manifest_path(root).is_file() else None
    plan = plan_codegen(project, root, manifest)
    return project, plan, apply_codegen(project, root, plan, force=force)


def _digests(root: Path) -> dict[str, str]:
    """Every regular file under ``root``, keyed by relpath."""
    return {
        str(path.relative_to(root)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


def _a_derived_relpath(project) -> str:
    return f"{project.package}/tools.py"


@dataclass(frozen=True)
class _RoutingCase:
    id: str
    ownership: str
    recorded: bool
    occupant: str
    state: str
    no_force_exit: int
    force_exit: int
    no_force_route: str
    force_route: str
    no_force_remediation: str | None
    force_remediation: str | None
    no_force_writes: int
    force_writes: int


_ROUTING_CASES = (
    _RoutingCase(
        "derived-recorded-absent", "derived", True, "absent", "missing",
        0, 0, "none", "none", None, None, 1, 1,
    ),
    _RoutingCase(
        "derived-recorded-edited-file", "derived", True, "edited-file", "modified",
        11, 0, "actionable", "none", "force", None, 0, 1,
    ),
    _RoutingCase(
        "derived-recorded-symlink", "derived", True, "symlink", "modified",
        11, 0, "actionable", "none", "force", None, 0, 1,
    ),
    _RoutingCase(
        "derived-recorded-directory", "derived", True, "directory", "modified",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "derived-recorded-fifo", "derived", True, "fifo", "modified",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "derived-unrecorded-absent", "derived", False, "absent", "create",
        0, 0, "none", "none", None, None, 1, 1,
    ),
    _RoutingCase(
        "derived-unrecorded-file", "derived", False, "unmanaged-file", "collided",
        11, 0, "actionable", "none", "force", None, 0, 1,
    ),
    _RoutingCase(
        "derived-unrecorded-symlink", "derived", False, "symlink", "collided",
        11, 0, "actionable", "none", "force", None, 0, 1,
    ),
    _RoutingCase(
        "derived-unrecorded-directory", "derived", False, "directory", "collided",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "derived-unrecorded-fifo", "derived", False, "fifo", "collided",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-absent", "extension", True, "absent", "missing",
        0, 0, "none", "none", None, None, 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-edited-file", "extension", True, "edited-file", "modified",
        0, 0, "informational", "informational", None, None, 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-symlink", "extension", True, "symlink", "modified",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-directory", "extension", True, "directory", "modified",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-fifo", "extension", True, "fifo", "modified",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-unrecorded-absent", "extension", False, "absent", "create",
        0, 0, "none", "none", None, None, 1, 1,
    ),
    _RoutingCase(
        "extension-unrecorded-file", "extension", False, "unmanaged-file", "collided",
        11, 0, "actionable", "none", "force", None, 0, 0,
    ),
    _RoutingCase(
        "extension-unrecorded-symlink", "extension", False, "symlink", "collided",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-unrecorded-directory", "extension", False, "directory", "collided",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-unrecorded-fifo", "extension", False, "fifo", "collided",
        11, 11, "actionable", "actionable", "remove", "remove", 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-current-file", "extension", True, "current-file", "current",
        0, 0, "none", "none", None, None, 0, 0,
    ),
    _RoutingCase(
        "extension-recorded-stale-file", "extension", True, "stale-file", "stale",
        0, 0, "none", "none", None, None, 0, 0,
    ),
)


def _routing_parameters():
    for case in _ROUTING_CASES:
        yield pytest.param(
            case,
            False,
            case.no_force_exit,
            case.no_force_route,
            case.no_force_remediation,
            case.no_force_writes,
            id=f"{case.id}-no-force",
        )
        yield pytest.param(
            case,
            True,
            case.force_exit,
            case.force_route,
            case.force_remediation,
            case.force_writes,
            id=f"{case.id}-force",
        )


def _replace_manifest_entry(
    root: Path,
    relpath: str,
    *,
    ownership: str | None,
) -> None:
    manifest = read_manifest(manifest_path(root))
    files = []
    for entry in manifest.files:
        if entry.relpath != relpath:
            files.append(entry)
        elif ownership is not None:
            files.append(entry.model_copy(update={"ownership": ownership}))
    write_manifest(
        root,
        CodegenManifest(
            **{
                **manifest.model_dump(),
                "files": [entry.model_dump() for entry in files],
            }
        ),
    )


@pytest.mark.parametrize(
    ("case", "force", "expected_exit", "expected_route", "remediation", "writes"),
    tuple(_routing_parameters()),
)
def test_extension_state_routing_matrix(
    tmp_path: Path,
    case: _RoutingCase,
    force: bool,
    expected_exit: int,
    expected_route: str,
    remediation: str | None,
    writes: int,
) -> None:
    """The locked Phase 8 tables, expanded to 44 independent outcomes."""
    root = tmp_path / "project"
    project = _generate(root)
    selected = (
        next(file for file in project.derived if file.relpath == _a_derived_relpath(project))
        if case.ownership == "derived"
        else project.extensions[0]
    )
    target_relpath = selected.relpath
    target = root / target_relpath

    if not case.recorded:
        _replace_manifest_entry(root, target_relpath, ownership=None)

    if case.occupant == "stale-file":
        moved = replace(selected, text=f"{selected.text}\n# template moved\n")
        project = replace(
            project,
            files=tuple(
                moved if file.relpath == target_relpath else file
                for file in project.files
            ),
        )
        selected = moved
    elif case.occupant == "absent":
        target.unlink()
    elif case.occupant in {"edited-file", "unmanaged-file"}:
        target.write_bytes(f"authored occupant for {case.id}\n".encode())

    outside = tmp_path / "outside-sentinel.txt"
    outside_before: bytes | None = None
    if case.occupant == "symlink":
        outside.write_bytes(b"outside target must stay unchanged\n")
        outside_before = outside.read_bytes()
        target.unlink()
        target.symlink_to(outside)
    elif case.occupant == "directory":
        target.unlink()
        target.mkdir()
    elif case.occupant == "fifo":
        if not hasattr(os, "mkfifo"):
            pytest.skip("os.mkfifo is unavailable")
        target.unlink()
        os.mkfifo(target)

    unplanned = root / "unplanned-sentinel.txt"
    unplanned.write_bytes(b"outside the emitted layout\n")
    unplanned_before = unplanned.read_bytes()
    manifest_before = manifest_path(root).read_bytes()
    prior_entries = read_manifest(manifest_path(root)).entries()
    prior_entry = prior_entries.get(target_relpath)
    prior_entry_dump = None if prior_entry is None else prior_entry.model_dump()
    regular_before = (
        target.read_bytes()
        if target.exists() and not target.is_symlink() and stat.S_ISREG(target.lstat().st_mode)
        else None
    )

    plan = plan_codegen(project, root, read_manifest(manifest_path(root)))
    planned = plan.by_relpath()[target_relpath]
    assert planned.state == case.state
    assert planned.ownership == case.ownership

    result = apply_codegen(project, root, plan, force=force)
    observed_exit = EXIT_COLLISION if result.collisions else 0

    assert observed_exit == expected_exit
    assert result.writes == writes
    assert result.written == ([target_relpath] if writes else [])
    assert unplanned.read_bytes() == unplanned_before

    expected_collisions = [target_relpath] if expected_route == "actionable" else []
    expected_information = [target_relpath] if expected_route == "informational" else []
    assert result.collisions == expected_collisions
    assert getattr(result, "extension_skips", []) == expected_information

    collision_details = getattr(result, "collision_details", [])
    assert [detail.relpath for detail in collision_details] == expected_collisions
    if collision_details:
        detail = collision_details[0]
        assert detail.state == case.state
        assert detail.ownership == case.ownership
        assert detail.previous_ownership == (
            case.ownership if case.recorded else None
        )
        assert detail.occupant_kind == {
            "absent": "absent",
            "edited-file": "file",
            "unmanaged-file": "file",
            "current-file": "file",
            "stale-file": "file",
            "symlink": "symlink",
            "directory": "other",
            "fifo": "other",
        }[case.occupant]
        assert detail.detail == next(
            skipped.detail
            for skipped in result.skipped
            if skipped.relpath == target_relpath
        )
        assert detail.remediation == remediation

    if expected_route == "informational":
        assert target_relpath in {record.relpath for record in result.skipped}
        assert result.writes == 0
        assert result.manifest_written is False
        assert manifest_path(root).read_bytes() == manifest_before

    if case.occupant == "absent":
        if writes:
            assert stat.S_ISREG(target.lstat().st_mode)
            assert target.read_text(encoding="utf-8") == selected.text
        else:
            assert not target.exists()
    elif case.occupant == "symlink":
        assert outside_before is not None
        assert outside.read_bytes() == outside_before
        if writes:
            assert not target.is_symlink()
            assert stat.S_ISREG(target.lstat().st_mode)
            assert target.read_text(encoding="utf-8") == selected.text
        else:
            assert target.is_symlink()
    elif case.occupant == "directory":
        assert target.is_dir()
    elif case.occupant == "fifo":
        assert stat.S_ISFIFO(target.lstat().st_mode)
    elif writes:
        assert target.read_text(encoding="utf-8") == selected.text
    else:
        assert regular_before is not None
        assert target.read_bytes() == regular_before

    after_entries = read_manifest(manifest_path(root)).entries()
    after_entry = after_entries.get(target_relpath)
    if case.recorded:
        assert after_entry is not None
        assert after_entry.model_dump() == prior_entry_dump
    elif expected_exit == EXIT_COLLISION:
        assert after_entry is None
    else:
        assert after_entry is not None
        if case.ownership == "extension" and case.occupant == "unmanaged-file":
            assert writes == 0
            assert regular_before is not None
            assert after_entry.sha256 == hashlib.sha256(regular_before).hexdigest()


@pytest.mark.parametrize("force", [False, True], ids=["no-force", "force"])
def test_previous_derived_current_extension_is_not_an_authored_skip(
    tmp_path: Path,
    force: bool,
) -> None:
    root = tmp_path / "project"
    original = _generate(root)
    derived = next(
        file for file in original.derived if file.relpath == _a_derived_relpath(original)
    )
    current_extension = replace(derived, ownership="extension")
    project = replace(
        original,
        files=tuple(
            current_extension if file.relpath == derived.relpath else file
            for file in original.files
        ),
    )
    target = root / derived.relpath
    target.write_bytes(b"regular bytes matching neither manifest nor emission\n")
    before = target.read_bytes()

    plan = plan_codegen(project, root, read_manifest(manifest_path(root)))
    assert plan.by_relpath()[derived.relpath].state == "modified"
    result = apply_codegen(project, root, plan, force=force)

    assert result.collisions == [derived.relpath]
    assert getattr(result, "extension_skips", []) == []
    assert target.read_bytes() == before
    details = getattr(result, "collision_details", [])
    assert [detail.relpath for detail in details] == [derived.relpath]
    detail = details[0]
    assert detail.previous_ownership == "derived"
    assert detail.ownership == "extension"
    assert detail.occupant_kind == "file"
    assert detail.remediation == "remove"


def test_apply_result_rejects_actionable_path_detail_divergence() -> None:
    with pytest.raises(
        ValueError,
        match="collision_details relpaths must exactly equal collisions in order",
    ):
        ApplyResult(collisions=["claimed-without-apply-evidence.txt"])


@pytest.mark.parametrize("force", [False, True], ids=["no-force", "force"])
def test_atomic_write_race_is_actionable_from_the_caught_error(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    force: bool,
) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    target_relpath = _a_derived_relpath(project)
    target = root / target_relpath
    target.unlink()
    plan = plan_codegen(project, root, read_manifest(manifest_path(root)))
    assert plan.by_relpath()[target_relpath].state == "missing"

    import gnd.safefs as install_module

    real_atomic_write = install_module._atomic_write

    def racing_atomic_write(root, relpath, data, *, expected=None):
        if relpath == target_relpath:
            raise install_module.InstallError("leaf identity changed at replacement")
        return real_atomic_write(root, relpath, data, expected=expected)

    monkeypatch.setattr(install_module, "atomic_write", racing_atomic_write)
    result = apply_codegen(project, root, plan, force=force)

    assert result.collisions == [target_relpath]
    assert len(result.collision_details) == 1
    detail = result.collision_details[0]
    assert detail.relpath == target_relpath
    assert detail.state == "modified"
    assert detail.previous_ownership == "derived"
    assert detail.occupant_kind == "changed"
    assert detail.remediation == "remove"
    assert "leaf identity changed at replacement" in detail.detail
    assert not target.exists()


def test_atomic_write_refuses_a_fifo_swapped_into_the_identity_open(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """CR-01: replacement identity is one nonblocking descriptor observation."""
    if not hasattr(os, "mkfifo"):
        pytest.skip("os.mkfifo is unavailable")

    from gnd import safefs as install_module

    root = tmp_path / "root"
    root.mkdir()
    target = root / "managed.txt"
    original = b"recorded bytes\n"
    target.write_bytes(original)
    expected = install_module.LeafIdentity(
        kind="file", sha256=hashlib.sha256(original).hexdigest()
    )

    real_open = install_module.os.open
    swapped_fd: int | None = None
    swapped = False

    def swap_candidate_to_fifo(path, flags, *args, **kwargs):
        nonlocal swapped, swapped_fd
        if (
            isinstance(path, str)
            and path.startswith(".gnd-recovery-")
            and kwargs.get("dir_fd") is not None
            and not flags & os.O_CREAT
            and not flags & os.O_WRONLY
            and not swapped
        ):
            swapped = True
            assert flags & getattr(os, "O_NOFOLLOW", 0)
            assert flags & getattr(os, "O_NONBLOCK", 0)
            os.unlink(path, dir_fd=kwargs["dir_fd"])
            os.mkfifo(path, dir_fd=kwargs["dir_fd"])
            swapped_fd = real_open(path, flags, *args, **kwargs)
            return swapped_fd
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(install_module.os, "open", swap_candidate_to_fifo)

    with pytest.raises(install_module.InstallError, match="changed after planning"):
        install_module._atomic_write(
            root,
            "managed.txt",
            b"replacement bytes\n",
            expected=expected,
        )

    assert swapped
    assert stat.S_ISFIFO(target.lstat().st_mode)
    assert list(root.glob(".gnd-tmp-*")) == []
    assert swapped_fd is not None
    with pytest.raises(OSError):
        os.fstat(swapped_fd)


@pytest.mark.parametrize("matches", [True, False], ids=["publish", "refuse"])
def test_leaf_cas_preserves_a_concurrent_owner_and_the_moved_original(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    matches: bool,
) -> None:
    """CR-01: neither publication nor restoration may clobber a new owner."""
    from gnd import safefs as install_module

    root = tmp_path / "root"
    root.mkdir()
    target = root / "managed.txt"
    original = b"recorded original bytes\n"
    concurrent = b"concurrent owner bytes\n"
    target.write_bytes(original)
    expected = install_module.LeafIdentity(
        kind="file", sha256=hashlib.sha256(original).hexdigest()
    )

    observed = False

    def claim_destination(_fd, _previous, _expected):
        nonlocal observed
        observed = True
        target.write_bytes(concurrent)
        return matches

    monkeypatch.setattr(install_module, "_matches_leaf", claim_destination)

    with pytest.raises(
        install_module.InstallError,
        match="concurrent destination occupant was preserved.*recovery entry",
    ):
        install_module._atomic_write(
            root,
            target.name,
            b"staged replacement bytes\n",
            expected=expected,
        )

    assert observed
    assert target.read_bytes() == concurrent
    recoveries = list(root.glob(".gnd-recovery-*"))
    assert len(recoveries) == 1
    assert recoveries[0].read_bytes() == original
    assert list(root.glob(".gnd-tmp-*")) == []


@pytest.mark.parametrize("replacement", ["symlink", "different-directory"])
def test_apply_refuses_an_output_root_replaced_after_planning(
    tmp_path: Path,
    replacement: str,
) -> None:
    """CR-02: plan/apply bind the real root, not its reusable pathname."""
    from gnd.install import InstallPathError

    root = tmp_path / "project"
    project = _generate(root)
    relpath = _a_derived_relpath(project)
    (root / relpath).write_text("# force would replace this\n", encoding="utf-8")
    plan = plan_codegen(project, root, read_manifest(manifest_path(root)))

    original_root = tmp_path / "planned-root-preserved"
    root.rename(original_root)
    outside = tmp_path / "outside-root"
    outside.mkdir()
    outside_leaf = outside / relpath
    outside_leaf.parent.mkdir(parents=True)
    outside_leaf.write_bytes(b"outside managed-path sentinel\n")
    outside_manifest = outside / ".gnd-codegen.json"
    outside_manifest.write_bytes(b"outside manifest sentinel\n")
    before_leaf = outside_leaf.read_bytes()
    before_manifest = outside_manifest.read_bytes()

    if replacement == "symlink":
        root.symlink_to(outside, target_is_directory=True)
    else:
        root.mkdir()
        replacement_leaf = root / relpath
        replacement_leaf.parent.mkdir(parents=True)
        replacement_leaf.write_bytes(before_leaf)
        (root / ".gnd-codegen.json").write_bytes(before_manifest)

    with pytest.raises(InstallPathError, match="output root.*changed|without following links"):
        apply_codegen(project, root, plan, force=True)

    assert outside_leaf.read_bytes() == before_leaf
    assert outside_manifest.read_bytes() == before_manifest
    if replacement == "different-directory":
        assert (root / relpath).read_bytes() == before_leaf
        assert (root / ".gnd-codegen.json").read_bytes() == before_manifest


@pytest.mark.parametrize("replacement", ["symlink", "different-directory"])
def test_apply_binds_the_parent_of_a_planned_absent_root(
    tmp_path: Path,
    replacement: str,
) -> None:
    """CR-02: programmatic absent-root apply cannot follow a swapped parent."""
    from gnd.install import InstallPathError

    parent = tmp_path / "accepted-parent"
    parent.mkdir()
    root = parent / "project"
    project = emit_project(
        load_model(str(FULL_VOCABULARY)),
        str(FULL_VOCABULARY),
        skill_name=root.name,
    )
    plan = plan_codegen(project, root, None)
    assert plan.root_device is None
    assert plan.root_parent_path == str(parent)
    assert plan.root_relative_parts == [root.name]

    preserved_parent = tmp_path / "preserved-parent"
    parent.rename(preserved_parent)
    outside = tmp_path / "outside-parent"
    outside.mkdir()
    sentinel = outside / "sentinel.txt"
    sentinel.write_bytes(b"outside parent sentinel\n")
    before = sentinel.read_bytes()
    if replacement == "symlink":
        parent.symlink_to(outside, target_is_directory=True)
    else:
        outside.rename(parent)
        sentinel = parent / sentinel.name

    with pytest.raises(InstallPathError, match="output parent.*changed|without following links"):
        apply_codegen(project, root, plan)

    assert sentinel.read_bytes() == before
    assert not (preserved_parent / root.name).exists()
    assert not root.exists()


@pytest.mark.parametrize("replacement", ["symlink", "different-directory"])
def test_fresh_cli_binds_the_parent_before_whole_tree_publication(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    replacement: str,
) -> None:
    """CR-02: the public fresh path publishes only below its retained parent."""
    from gnd.codegen import emit as emit_module

    parent = tmp_path / "accepted-parent"
    parent.mkdir()
    out = parent / "project"
    preserved_parent = tmp_path / "preserved-parent"
    outside = tmp_path / "outside-parent"
    outside.mkdir()
    sentinel = outside / "sentinel.txt"
    sentinel.write_bytes(b"outside parent sentinel\n")
    before = sentinel.read_bytes()

    real_write_project = emit_module.write_project
    swapped = False

    def swap_parent_then_publish(*args, **kwargs):
        nonlocal swapped, sentinel
        swapped = True
        parent.rename(preserved_parent)
        if replacement == "symlink":
            parent.symlink_to(outside, target_is_directory=True)
        else:
            outside.rename(parent)
            sentinel = parent / sentinel.name
        return real_write_project(*args, **kwargs)

    monkeypatch.setattr(emit_module, "write_project", swap_parent_then_publish)

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_IO
    printed = capsys.readouterr().out
    assert swapped
    assert "refused output path" in printed
    assert sentinel.read_bytes() == before
    assert not (preserved_parent / out.name).exists()
    assert not out.exists()


@pytest.mark.parametrize("accepted_empty", [False, True], ids=["absent", "accepted-empty"])
@pytest.mark.parametrize("raced_nonempty", [False, True], ids=["raced-empty", "raced-nonempty"])
def test_fresh_cli_no_clobber_publication_preserves_a_raced_root(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    accepted_empty: bool,
    raced_nonempty: bool,
) -> None:
    """CR-02: the final descriptor-relative rename is an exclusive CAS."""
    from gnd import safefs as install_module

    out = tmp_path / "project"
    if accepted_empty:
        out.mkdir()
    sentinel_bytes = b"concurrent root sentinel\n"
    raced_identity: tuple[int, int] | None = None
    real_rename = install_module._rename_noreplace

    def claim_root_before_publish(src_fd, src, dst_fd, dst):
        nonlocal raced_identity
        if dst == out.name and src.startswith(f".{out.name}.staging-"):
            out.mkdir()
            if raced_nonempty:
                (out / "sentinel.txt").write_bytes(sentinel_bytes)
            info = out.stat()
            raced_identity = (info.st_dev, info.st_ino)
        return real_rename(src_fd, src, dst_fd, dst)

    monkeypatch.setattr(install_module, "rename_noreplace", claim_root_before_publish)

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_COLLISION
    printed = capsys.readouterr().out

    assert raced_identity is not None
    current = out.stat()
    assert (current.st_dev, current.st_ino) == raced_identity
    assert "claimed during fresh publication" in printed
    assert not (out / "SKILL.md").exists()
    if raced_nonempty:
        assert (out / "sentinel.txt").read_bytes() == sentinel_bytes
    else:
        assert list(out.iterdir()) == []
    assert list(tmp_path.glob(f".{out.name}.staging-*")) == []


@pytest.mark.parametrize("failed_barrier", ["staging:.", "publication-parent"])
def test_fresh_cli_maps_directory_barrier_failures_to_exit_74(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    failed_barrier: str,
) -> None:
    """CR-04: durability is part of success, and its I/O band remains 74."""
    from gnd.codegen import emit as emit_module

    out = tmp_path / "project"
    real_fsync_directory = emit_module._fsync_directory

    def failing_fsync(fd, label):
        if label == failed_barrier:
            raise OSError(5, "injected directory barrier failure")
        real_fsync_directory(fd, label)

    monkeypatch.setattr(emit_module, "_fsync_directory", failing_fsync)

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_IO
    printed = capsys.readouterr().out
    assert "injected directory barrier failure" in printed


# --------------------------------------------------------------------------
# the published table
# --------------------------------------------------------------------------


def test_writable_states_is_module_level_data_carrying_its_rationale() -> None:
    """``install.py:158-172``'s shape: the gate is DATA, and it says why.

    ``modified`` is excluded because a user edit is never silently destroyed;
    ``collided`` is excluded because an unmanaged occupant was not placed by
    GND. Both join only under ``--force``, and neither is ever writable for an
    extension file (G-06).
    """
    from gnd.codegen import plan as module

    assert isinstance(WRITABLE_STATES, frozenset)
    assert WRITABLE_STATES == {"create", "stale", "missing"}
    assert "modified" not in WRITABLE_STATES
    assert "collided" not in WRITABLE_STATES

    source = Path(module.__file__).read_text(encoding="utf-8")
    lines = source.splitlines()
    index = next(i for i, line in enumerate(lines) if line.startswith("WRITABLE_STATES"))
    comment = []
    cursor = index - 1
    while cursor >= 0 and lines[cursor].startswith("#:"):
        comment.append(lines[cursor])
        cursor -= 1
    assert comment, "WRITABLE_STATES carries no `#:` rationale block"
    text = " ".join(comment).lower()
    assert "modified" in text and "extension" in text, (
        f"the rationale does not state which states are excluded and why: {comment}"
    )


def test_the_six_states_are_a_closed_vocabulary() -> None:
    from typing import get_args

    field = FileState.model_fields["state"]
    assert set(get_args(field.annotation)) == {
        "create",
        "current",
        "stale",
        "missing",
        "modified",
        "collided",
    }


# --------------------------------------------------------------------------
# one named test per state
# --------------------------------------------------------------------------


def test_a_fresh_directory_classifies_every_file_as_create(tmp_path: Path) -> None:
    _model, project = _emit(FULL_VOCABULARY)
    plan = plan_codegen(project, tmp_path / "absent", None)
    assert plan.files, "the plan is empty"
    assert {record.state for record in plan.files} == {"create"}
    assert len(plan.files) == len(project.files)


def test_apply_over_a_fresh_directory_writes_every_file(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _model, project = _emit(FULL_VOCABULARY)
    plan = plan_codegen(project, root, None)
    result = apply_codegen(project, root, plan)

    assert isinstance(result, ApplyResult)
    assert result.writes == len(project.files)
    assert sorted(result.written) == sorted(project.relpaths)
    assert result.manifest_written is True
    assert manifest_path(root).is_file()
    for file in project.files:
        assert (root / file.relpath).read_text(encoding="utf-8") == file.text


def test_an_unchanged_rerun_classifies_every_file_as_current(tmp_path: Path) -> None:
    root = tmp_path / "project"
    _generate(root)
    assert set(_states(root).values()) == {"current"}


def test_an_unchanged_rerun_performs_zero_writes_and_leaves_identical_digests(
    tmp_path: Path,
) -> None:
    """G-06's headline, measured on BOTH observables.

    The write COUNT alone would pass on a run that rewrote every file with
    identical bytes; the DIGESTS alone would pass on a run that rewrote
    everything from the same model. PKG-02's claim is the conjunction, and so is
    this one. The non-vacuity floor is the third assertion: the compared set is
    the whole emitted project, derived from the model, never an empty mapping.
    """
    root = tmp_path / "project"
    project = _generate(root)
    before = _digests(root)

    _project, plan, result = _rerun(root)

    assert result.writes == 0, (
        f"a second run wrote {result.writes} file(s): {result.written}"
    )
    assert result.written == []
    assert result.manifest_written is False, (
        "the manifest was rewritten on a no-op run, so 'zero writes' is only "
        "true about assets and the record still churns"
    )
    after = _digests(root)
    assert before == after

    # Floor: the comparison covered the whole emitted project plus its manifest,
    # not an empty directory that trivially equals itself.
    assert before, "the digest snapshot is empty"
    assert set(project.relpaths) <= set(before)
    assert {record.state for record in plan.files} == {"current"}


def test_a_changed_model_marks_derived_files_stale_and_rewrites_them(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    _generate(root)

    # Same model, one fact-type reading changed: the derivation moves, the file
    # layout does not.
    edited = tmp_path / "edited.orm.yaml"
    text = FULL_VOCABULARY.read_text(encoding="utf-8")
    edited.write_text(text, encoding="utf-8")

    tools_rel = _a_derived_relpath(_emit(FULL_VOCABULARY)[1])
    # Simulate the derivation moving by rewriting the file to the bytes a
    # PREVIOUS generation left, then recording those bytes as the manifest's
    # truth — which is exactly the shape "the model moved and the code did not"
    # produces from the classifier's point of view.
    manifest = read_manifest(manifest_path(root))
    stale_text = "# an older generation\n"
    (root / tools_rel).write_text(stale_text, encoding="utf-8")
    entries = []
    for entry in manifest.files:
        if entry.relpath == tools_rel:
            entry = entry.model_copy(
                update={"sha256": hashlib.sha256(stale_text.encode()).hexdigest()}
            )
        entries.append(entry)
    from gnd.codegen.manifest import CodegenManifest, write_manifest

    write_manifest(root, CodegenManifest(**{**manifest.model_dump(), "files": [e.model_dump() for e in entries]}))

    assert _states(root)[tools_rel] == "stale"

    _project, _plan, result = _rerun(root)
    assert tools_rel in result.written
    assert (root / tools_rel).read_text(encoding="utf-8") != stale_text


def test_a_hand_edited_derived_file_is_modified_and_refused_without_force(
    tmp_path: Path,
) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    tools_rel = _a_derived_relpath(project)
    edit = "# a human wrote this line\nx = 1\n"
    (root / tools_rel).write_text(edit, encoding="utf-8")

    assert _states(root)[tools_rel] == "modified"

    _project, _plan, result = _rerun(root)
    assert tools_rel not in result.written
    assert tools_rel in result.collisions
    assert (root / tools_rel).read_text(encoding="utf-8") == edit, (
        "the hand edit was destroyed by a run that had no --force"
    )


@pytest.mark.parametrize("planned_state", ["stale", "missing"])
def test_apply_reclassifies_before_overwriting_a_writable_plan_state(
    tmp_path: Path, planned_state: str
) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    tools_rel = _a_derived_relpath(project)
    target = root / tools_rel
    manifest = read_manifest(manifest_path(root))

    if planned_state == "stale":
        old = "# prior generated bytes\n"
        target.write_text(old, encoding="utf-8")
        entries = [
            entry.model_copy(
                update={"sha256": hashlib.sha256(old.encode("utf-8")).hexdigest()}
            )
            if entry.relpath == tools_rel
            else entry
            for entry in manifest.files
        ]
        from gnd.codegen.manifest import CodegenManifest, write_manifest

        write_manifest(
            root,
            CodegenManifest(
                **{
                    **manifest.model_dump(),
                    "files": [entry.model_dump() for entry in entries],
                }
            ),
        )
        manifest = read_manifest(manifest_path(root))
    else:
        target.unlink()

    plan = plan_codegen(project, root, manifest)
    assert plan.by_relpath()[tools_rel].state == planned_state

    user_edit = "# written after planning\nimportant = True\n"
    target.write_text(user_edit, encoding="utf-8")
    result = apply_codegen(project, root, plan)

    assert tools_rel not in result.written
    assert tools_rel in result.collisions
    assert target.read_text(encoding="utf-8") == user_edit


def test_force_rewrites_a_hand_edited_derived_file(tmp_path: Path) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    tools_rel = _a_derived_relpath(project)
    (root / tools_rel).write_text("# a human wrote this\n", encoding="utf-8")

    _project, _plan, result = _rerun(root, force=True)
    assert tools_rel in result.written
    assert result.collisions == []
    expected = next(f.text for f in project.files if f.relpath == tools_rel)
    assert (root / tools_rel).read_text(encoding="utf-8") == expected


def test_a_refused_write_is_never_adopted_into_the_manifest(tmp_path: Path) -> None:
    """The guard behind the guard.

    Refusing to overwrite a hand edit NOW is worthless if the run then records
    the edited bytes as the file's truth: the next run would see
    ``have == recorded`` and ``have != expected``, classify ``stale``, and
    rewrite it — destroying the edit one run later, through the very mechanism
    that protected it.
    """
    root = tmp_path / "project"
    project = _generate(root)
    tools_rel = _a_derived_relpath(project)
    original = read_manifest(manifest_path(root)).entries()[tools_rel].sha256
    (root / tools_rel).write_text("# a human wrote this\n", encoding="utf-8")

    _rerun(root)
    after = read_manifest(manifest_path(root)).entries()[tools_rel].sha256
    assert after == original, (
        "the refused file's edited bytes were adopted into the manifest"
    )
    assert _states(root)[tools_rel] == "modified", (
        "the file drifted to a writable state after one refused run"
    )

    # And a second refused run still refuses, rather than converging on a write.
    _project, _plan, result = _rerun(root)
    assert tools_rel not in result.written


def test_an_extension_file_is_never_written_even_with_force(tmp_path: Path) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    extension = next(f.relpath for f in project.extensions)
    mine = "# my dependencies live here\n"
    (root / extension).write_text(mine, encoding="utf-8")
    before = hashlib.sha256(mine.encode("utf-8")).hexdigest()

    _project, _plan, result = _rerun(root, force=True)

    assert extension not in result.written
    after = hashlib.sha256((root / extension).read_bytes()).hexdigest()
    assert after == before, (
        "regeneration overwrote an EXTENSION file under --force; G-06 says it "
        "never does, because a lost dependency list is unrecoverable"
    )


def test_every_extension_file_survives_a_force_run(tmp_path: Path) -> None:
    """Asserted over ALL extension files, not one sample."""
    root = tmp_path / "project"
    project = _generate(root)
    assert project.extensions, "the emitter produced no extension files"
    for file in project.extensions:
        (root / file.relpath).write_text(f"mine: {file.relpath}\n", encoding="utf-8")
    before = {f.relpath: (root / f.relpath).read_bytes() for f in project.extensions}

    _rerun(root, force=True)

    for relpath, data in before.items():
        assert (root / relpath).read_bytes() == data


def test_an_unmanaged_file_at_a_derived_path_is_collided(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _model, project = _emit(FULL_VOCABULARY)
    tools_rel = _a_derived_relpath(project)
    (root / tools_rel).parent.mkdir(parents=True, exist_ok=True)
    planted = "# not mine, not GND's\n"
    (root / tools_rel).write_text(planted, encoding="utf-8")

    plan = plan_codegen(project, root, None)
    states = {record.relpath: record.state for record in plan.files}
    assert states[tools_rel] == "collided"

    result = apply_codegen(project, root, plan)
    assert tools_rel in result.collisions
    assert tools_rel not in result.written
    assert (root / tools_rel).read_text(encoding="utf-8") == planted


def test_a_deleted_derived_file_is_missing_and_restored(tmp_path: Path) -> None:
    root = tmp_path / "project"
    project = _generate(root)
    tools_rel = _a_derived_relpath(project)
    (root / tools_rel).unlink()

    assert _states(root)[tools_rel] == "missing"

    _project, _plan, result = _rerun(root)
    assert tools_rel in result.written
    expected = next(f.text for f in project.files if f.relpath == tools_rel)
    assert (root / tools_rel).read_text(encoding="utf-8") == expected


# --------------------------------------------------------------------------
# the negative control
# --------------------------------------------------------------------------


def test_mutating_one_derived_file_moves_exactly_that_file_to_modified(
    tmp_path: Path,
) -> None:
    """Proof the classifier can tell the states apart AT ALL.

    A classifier that answered ``modified`` for everything would satisfy the
    hand-edit test; one that answered ``current`` for everything would satisfy
    the idempotence test. Neither survives this: exactly one relpath changes
    state, and it is the one whose bytes changed.
    """
    root = tmp_path / "project"
    project = _generate(root)
    before = _states(root)
    assert set(before.values()) == {"current"}

    target = _a_derived_relpath(project)
    (root / target).write_text("# one byte of difference\n", encoding="utf-8")
    after = _states(root)

    changed = {rel for rel in after if after[rel] != before[rel]}
    assert changed == {target}, (
        f"mutating {target} changed the state of {sorted(changed)}"
    )
    assert after[target] == "modified"
    assert all(after[rel] == "current" for rel in after if rel != target)


# --------------------------------------------------------------------------
# hostile occupants — classified from stat, never opened, never followed
# --------------------------------------------------------------------------


def test_a_symlink_at_a_derived_path_is_never_followed(tmp_path: Path) -> None:
    """T-03-20: a planted symlink inside a generated project is the same threat
    as one inside a skill directory, so the classifier opens with lstat."""
    root = tmp_path / "project"
    project = _generate(root)
    target = _a_derived_relpath(project)
    outside = tmp_path / "outside.txt"
    outside.write_text("secrets\n", encoding="utf-8")

    (root / target).unlink()
    (root / target).symlink_to(outside)

    state = _states(root)[target]
    assert state == "modified", f"a symlink at a recorded path classified {state}"

    _project, _plan, result = _rerun(root)
    assert target not in result.written
    assert (root / target).is_symlink(), "the symlink was replaced without --force"
    assert outside.read_text(encoding="utf-8") == "secrets\n", (
        "the write followed the symlink and clobbered its target"
    )


@pytest.mark.parametrize("replacement", ["symlink", "fifo"])
def test_descriptor_observation_refuses_a_leaf_swapped_during_open_without_reading_it(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    replacement: str,
) -> None:
    """CR-01: the leaf open itself is no-follow and nonblocking.

    The swap occurs inside the patched ``os.open`` call, after the parent is
    descriptor-bound but before the kernel opens the leaf. A symlink whose
    target matches the recorded digest must not be read as current, and a FIFO
    must not wait for a writer.
    """
    if replacement == "fifo" and not hasattr(os, "mkfifo"):
        pytest.skip("os.mkfifo is unavailable")

    root = tmp_path / "project"
    project = _generate(root)
    relpath = _a_derived_relpath(project)
    target = root / relpath
    recorded = read_manifest(manifest_path(root)).entries()[relpath]
    outside = tmp_path / "outside-matching-recorded.py"
    outside.write_bytes(target.read_bytes())
    outside_before = outside.read_bytes()

    from gnd.codegen import plan as plan_module

    real_open = plan_module.os.open
    real_read = plan_module.os.read
    read_calls: list[int] = []
    swapped = False

    def swap_before_open(path, flags, *args, **kwargs):
        nonlocal swapped
        if path == target.name and kwargs.get("dir_fd") is not None and not swapped:
            swapped = True
            assert flags & getattr(os, "O_NOFOLLOW", 0)
            assert flags & getattr(os, "O_NONBLOCK", 0)
            target.unlink()
            if replacement == "symlink":
                target.symlink_to(outside)
            else:
                os.mkfifo(target)
        return real_open(path, flags, *args, **kwargs)

    def watch_read(fd: int, size: int) -> bytes:
        read_calls.append(fd)
        return real_read(fd, size)

    monkeypatch.setattr(plan_module.os, "open", swap_before_open)
    monkeypatch.setattr(plan_module.os, "read", watch_read)

    record = classify_file(
        root,
        relpath,
        expected_text=next(file.text for file in project.files if file.relpath == relpath),
        ownership="derived",
        recorded=recorded,
    )

    assert swapped
    assert record.state == "modified"
    assert read_calls == []
    assert outside.read_bytes() == outside_before
    if replacement == "symlink":
        assert "symlink" in record.detail
    else:
        assert "regular file" in record.detail


def test_an_unrecorded_symlink_at_a_derived_path_is_collided(tmp_path: Path) -> None:
    root = tmp_path / "project"
    root.mkdir()
    _model, project = _emit(FULL_VOCABULARY)
    target = _a_derived_relpath(project)
    (root / target).parent.mkdir(parents=True, exist_ok=True)
    outside = tmp_path / "outside.txt"
    outside.write_text("secrets\n", encoding="utf-8")
    (root / target).symlink_to(outside)

    plan = plan_codegen(project, root, None)
    states = {r.relpath: r.state for r in plan.files}
    assert states[target] == "collided"


def test_a_directory_at_a_derived_path_is_classified_from_its_stat(
    tmp_path: Path,
) -> None:
    """WR-03: everything that is not a REGULAR file is classified from its stat
    alone and never opened — the branch nobody enumerates is the one that
    blocks ``open()`` forever on a FIFO."""
    root = tmp_path / "project"
    project = _generate(root)
    target = _a_derived_relpath(project)
    (root / target).unlink()
    (root / target).mkdir()

    record = next(r for r in plan_codegen(
        project, root, read_manifest(manifest_path(root))
    ).files if r.relpath == target)
    assert record.state == "modified"
    assert "director" in record.detail.lower()


def test_an_oversized_occupant_is_reported_and_never_hashed(tmp_path: Path) -> None:
    """T-03-21: bound every untrusted-input-proportional resource. Asserted
    through ``classify_file`` directly so the test does not have to write ten
    megabytes to disk."""
    root = tmp_path / "project"
    project = _generate(root)
    target = _a_derived_relpath(project)
    manifest = read_manifest(manifest_path(root))

    huge = root / target
    huge.write_bytes(b"\0" * 1024)

    read_fds: list[int] = []
    real_fstat = os.fstat
    huge_inode = huge.lstat().st_ino

    class _FakeStat:
        def __init__(self, real):
            self._real = real

        def __getattr__(self, name):
            if name == "st_size":
                return MAX_CLASSIFY_BYTES + 1
            return getattr(self._real, name)

    def fake_fstat(fd):
        info = real_fstat(fd)
        if info.st_ino == huge_inode:
            return _FakeStat(info)
        return info

    original_read = os.read

    def watching_read(fd, size):
        read_fds.append(fd)
        return original_read(fd, size)

    import gnd.codegen.plan as plan_module

    monkey_fstat = plan_module.os.fstat
    monkey_read = plan_module.os.read
    plan_module.os.fstat = fake_fstat
    plan_module.os.read = watching_read
    try:
        record = classify_file(
            root,
            target,
            expected_text=next(f.text for f in project.files if f.relpath == target),
            ownership="derived",
            recorded=manifest.entries()[target],
        )
    finally:
        plan_module.os.fstat = monkey_fstat
        plan_module.os.read = monkey_read

    assert record.state == "modified"
    assert read_fds == [], "an oversized occupant was hashed anyway"
    assert str(MAX_CLASSIFY_BYTES) in record.detail


def test_max_classify_bytes_matches_the_shipped_untrusted_input_ceiling() -> None:
    from gnd import install

    assert MAX_CLASSIFY_BYTES == install.MAX_CLASSIFY_BYTES


# --------------------------------------------------------------------------
# the CLI band
# --------------------------------------------------------------------------


def test_documented_extension_authoring_workflow_regenerates_at_exit_zero(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Public Step 3 preserves every extension leaf on both rerun branches."""
    from gnd.codegen import plan as plan_module

    out = tmp_path / "project"
    command = ["codegen", str(FULL_VOCABULARY), "--out", str(out)]
    assert main(command) == 0
    capsys.readouterr()

    project = emit_project(
        load_model(str(FULL_VOCABULARY)),
        str(FULL_VOCABULARY),
        skill_name=out.name,
    )
    extension_relpaths = [file.relpath for file in project.extensions]
    assert set(extension_relpaths) == {
        "architecture.contract.yaml",
        "pyproject.toml",
        "references/gnd-full-vocabulary-notes.md",
        "test_architecture_smoke_full_vocabulary.py",
    }
    authored = {
        "architecture.contract.yaml": (
            b"contract_version: 1\nmodules: []\nartifacts: []\n"
            b"entry_points: []\nsmoke: []\n# authored architecture\n"
        ),
        "pyproject.toml": b"[project]\nname = 'authored-dependencies'\n",
        "references/gnd-full-vocabulary-notes.md": (
            b"# Authored domain notes\n\nNever replace these bytes.\n"
        ),
        "test_architecture_smoke_full_vocabulary.py": (
            b'"""Authored smoke module."""\n# these bytes are mine\n'
        ),
    }
    assert len(set(authored.values())) == len(authored)
    for relpath, data in authored.items():
        (out / relpath).write_bytes(data)

    manifest_before = manifest_path(out).read_bytes()
    entries_before = {
        relpath: entry.model_dump()
        for relpath, entry in read_manifest(manifest_path(out)).entries().items()
        if relpath in authored
    }
    captured: list[ApplyResult] = []
    real_apply = plan_module.apply_codegen

    def capture_apply(*args, **kwargs):
        result = real_apply(*args, **kwargs)
        captured.append(result)
        return result

    monkeypatch.setattr(plan_module, "apply_codegen", capture_apply)

    for invocation, force in enumerate((False, True), start=1):
        args = [*command, "--force"] if force else command
        assert main(args) == 0
        printed = capsys.readouterr().out

        assert len(captured) == invocation
        result = captured[-1]
        assert result.collisions == []
        assert result.collision_details == []
        assert result.extension_skips == extension_relpaths
        assert {record.relpath for record in result.skipped} == set(authored)
        assert not set(result.written) & set(authored)
        assert result.writes == 0
        assert result.manifest_written is False
        for relpath in extension_relpaths:
            assert (
                f"NOTE: preserved authored extension {relpath}; left unchanged"
                in printed
            )
            assert (out / relpath).read_bytes() == authored[relpath]

        assert manifest_path(out).read_bytes() == manifest_before
        entries_after = read_manifest(manifest_path(out)).entries()
        assert {
            relpath: entries_after[relpath].model_dump()
            for relpath in authored
        } == entries_before


def test_cli_splits_apply_time_collision_remedies_and_preserves_unsafe_target(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    out = tmp_path / "project"
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0
    capsys.readouterr()

    project = emit_project(
        load_model(str(FULL_VOCABULARY)),
        str(FULL_VOCABULARY),
        skill_name=out.name,
    )
    derived_relpath = _a_derived_relpath(project)
    (out / derived_relpath).write_text("# authored derived edit\n", encoding="utf-8")

    extension_relpath = "pyproject.toml"
    extension = out / extension_relpath
    outside = tmp_path / "outside-extension.toml"
    outside.write_bytes(b"outside target must remain byte-identical\n")
    outside_before = outside.read_bytes()
    extension.unlink()
    extension.symlink_to(outside)

    assert (
        main(["codegen", str(FULL_VOCABULARY), "--out", str(out)])
        == EXIT_COLLISION
    )
    printed = capsys.readouterr().out

    force_heading = "ERROR: force-remediable refusals:"
    force_remedy = (
        "Re-run with --force to overwrite the derived paths or adopt the regular "
        "unmanaged extension paths listed above."
    )
    manual_heading = "ERROR: unsafe occupants requiring manual removal:"
    manual_remedy = (
        "Remove or move the unsafe occupants listed above by hand; --force will "
        "not replace them."
    )
    old_blended = (
        "Re-run with --force to overwrite the derived files above; extension files "
        "are never overwritten, with or without --force."
    )

    assert printed.count(force_heading) == 1
    assert printed.count(force_remedy) == 1
    assert printed.count(manual_heading) == 1
    assert printed.count(manual_remedy) == 1
    assert printed.count("Nothing was destroyed.") == 1
    assert old_blended not in printed

    force_start = printed.index(force_heading)
    manual_start = printed.index(manual_heading)
    assurance_start = printed.index("Nothing was destroyed.")
    force_section = printed[force_start:manual_start]
    manual_section = printed[manual_start:assurance_start]
    assert derived_relpath in force_section
    assert "matches neither the manifest nor what this run emits" in force_section
    assert extension_relpath not in force_section
    assert extension_relpath in manual_section
    assert "a symlink stands where a regular file belongs" in manual_section
    assert derived_relpath not in manual_section

    assert extension.is_symlink()
    assert outside.read_bytes() == outside_before


def test_cli_renders_apply_time_state_consistently_after_an_atomic_write_race(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """WR-01: the status line and remediation use the same final record."""
    out = tmp_path / "project"
    command = ["codegen", str(FULL_VOCABULARY), "--out", str(out)]
    assert main(command) == 0
    capsys.readouterr()

    project = emit_project(
        load_model(str(FULL_VOCABULARY)),
        str(FULL_VOCABULARY),
        skill_name=out.name,
    )
    relpath = _a_derived_relpath(project)
    (out / relpath).unlink()

    import gnd.safefs as install_module

    real_atomic_write = install_module._atomic_write

    def racing_atomic_write(root, candidate, data, *, expected=None):
        if candidate == relpath:
            raise install_module.InstallError("deterministic public CLI leaf race")
        return real_atomic_write(root, candidate, data, expected=expected)

    monkeypatch.setattr(install_module, "atomic_write", racing_atomic_write)

    assert main(command) == EXIT_COLLISION
    printed = capsys.readouterr().out
    status_line = f"  {relpath} [derived] skipped (modified)"
    assert status_line in printed
    assert f"  {relpath} [derived] skipped (missing)" not in printed
    assert "ERROR: unsafe occupants requiring manual removal:" in printed
    assert f"  {relpath} — changed after apply-time reclassification" in printed
    assert "deterministic public CLI leaf race" in printed


@pytest.mark.parametrize("replacement", ["regular", "other"])
def test_cli_manifest_publication_uses_the_identity_of_the_bytes_initially_read(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    replacement: str,
) -> None:
    """CR-03: the final observation cannot rebase manifest publication CAS."""
    out = tmp_path / "project"
    command = ["codegen", str(FULL_VOCABULARY), "--out", str(out)]
    assert main(command) == 0
    capsys.readouterr()

    project = emit_project(
        load_model(str(FULL_VOCABULARY)),
        str(FULL_VOCABULARY),
        skill_name=out.name,
    )
    (out / _a_derived_relpath(project)).unlink()

    from gnd.codegen import plan as plan_module

    real_observe = plan_module._observe_leaf_at
    swapped = False
    concurrent_bytes = b"concurrent manifest owner bytes\n"

    def swap_manifest_before_final_observation(root_fd, relpath):
        nonlocal swapped
        if relpath == ".gnd-codegen.json" and not swapped:
            swapped = True
            manifest_path(out).unlink()
            if replacement == "regular":
                manifest_path(out).write_bytes(concurrent_bytes)
            else:
                manifest_path(out).mkdir()
        return real_observe(root_fd, relpath)

    monkeypatch.setattr(plan_module, "_observe_leaf_at", swap_manifest_before_final_observation)

    assert main(command) == EXIT_COLLISION
    printed = capsys.readouterr().out
    assert swapped
    assert "refused manifest update" in printed
    assert "Nothing was destroyed" in printed
    if replacement == "regular":
        assert manifest_path(out).read_bytes() == concurrent_bytes
    else:
        assert manifest_path(out).is_dir()
    assert list(out.glob(".gnd-tmp-*")) == []


def test_codegen_band_eleven_docstring_enumerates_every_refusal_family() -> None:
    import inspect

    from gnd import cli as cli_module

    doc = cli_module._cmd_codegen.__doc__
    assert doc is not None
    normalized_doc = " ".join(doc.split())
    required = (
        "a hand-edited derived file",
        "an unmanaged regular, symlink, or non-regular occupant at a derived path",
        "an occupied directory without a codegen manifest",
        "an unrecorded regular extension before explicit ``--force`` adoption",
        (
            "a recorded or unrecorded extension path occupied by a symlink, "
            "directory, FIFO, or over-cap leaf"
        ),
        (
            "recorded authored regular extension divergence is an informational "
            "create-once skip at exit 0, not band 11"
        ),
    )
    for text in required:
        assert text in normalized_doc

    source = inspect.getsource(cli_module._cmd_codegen)
    assert "collision_details" in source
    assert ".remediation" in source
    assert "states[relpath].detail" not in source


def test_the_cli_regenerates_an_unchanged_project_at_exit_zero(tmp_path: Path) -> None:
    out = tmp_path / "project"
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0
    before = _digests(out)
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0
    assert _digests(out) == before


def test_the_cli_exits_eleven_over_a_hand_edited_derived_file(tmp_path: Path) -> None:
    out = tmp_path / "project"
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0
    _model, project = _emit(FULL_VOCABULARY)
    target = out / _a_derived_relpath(project)
    edit = "# mine\n"
    target.write_text(edit, encoding="utf-8")

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_COLLISION
    assert target.read_text(encoding="utf-8") == edit

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out), "--force"]) == 0
    assert target.read_text(encoding="utf-8") != edit


def test_the_cli_exits_eleven_over_an_unmanaged_occupied_directory(
    tmp_path: Path,
) -> None:
    """Plan 03's shipped refusal, preserved: an occupied directory that is NOT a
    codegen project is refused outright, and nothing in it is destroyed."""
    out = tmp_path / "occupied"
    out.mkdir()
    planted = out / "user-work.txt"
    planted.write_text("do not lose me", encoding="utf-8")

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_COLLISION
    assert planted.read_text(encoding="utf-8") == "do not lose me"
    assert list(out.iterdir()) == [planted]


def test_the_cli_reports_an_existing_output_file_without_a_traceback(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "occupied"
    out.write_text("user data\n", encoding="utf-8")

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_IO
    printed = capsys.readouterr().out
    assert str(out) in printed
    assert "non-directory" in printed
    assert out.read_text(encoding="utf-8") == "user data\n"


def test_the_cli_binds_skill_name_to_the_output_directory(tmp_path: Path) -> None:
    out = tmp_path / "custom-project"
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0

    mapping, _body = read_frontmatter(out / "SKILL.md")
    assert mapping["name"] == out.name


@pytest.mark.parametrize("dirname", ["bad.name", "Bad-Name", "a" * 65])
def test_the_cli_refuses_invalid_agent_skill_directory_names(
    tmp_path: Path, dirname: str
) -> None:
    out = tmp_path / dirname
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == EXIT_IO
    assert not out.exists()


def test_force_adopts_an_unmanaged_occupied_directory(tmp_path: Path) -> None:
    out = tmp_path / "occupied"
    out.mkdir()
    planted = out / "user-work.txt"
    planted.write_text("do not lose me", encoding="utf-8")

    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out), "--force"]) == 0
    assert planted.read_text(encoding="utf-8") == "do not lose me", (
        "--force destroyed a file at no managed relpath; only planned paths are "
        "ever touched"
    )
    assert manifest_path(out).is_file()


def test_force_adopts_a_regular_extension_into_conformance_scope(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    out = tmp_path / "custom-project"
    out.mkdir()
    extension = out / "pyproject.toml"
    original = "[project]\nname = 'mine'\n"
    extension.write_text(original, encoding="utf-8")

    assert (
        main(
            ["codegen", str(FULL_VOCABULARY), "--out", str(out), "--force"]
        )
        == 0
    )
    assert extension.read_text(encoding="utf-8") == original
    manifest = read_manifest(manifest_path(out))
    entry = manifest.entries()["pyproject.toml"]
    assert entry.ownership == "extension"
    assert entry.sha256 == hashlib.sha256(original.encode("utf-8")).hexdigest()
    assert set(manifest.entries()) == {
        file.relpath
        for file in emit_project(
            load_model(str(FULL_VOCABULARY)),
            str(FULL_VOCABULARY),
            skill_name=out.name,
        ).files
    }

    capsys.readouterr()
    assert (
        main(
            [
                "conformance",
                str(FULL_VOCABULARY),
                str(out),
                "--format",
                "json",
            ]
        )
        == 0
    )
    payload = json.loads(capsys.readouterr().out)
    assert "pyproject.toml" in {
        item["relpath"] for item in payload["unexamined"]
    }


def test_force_refuses_to_adopt_a_symlinked_extension(tmp_path: Path) -> None:
    out = tmp_path / "custom-project"
    out.mkdir()
    outside = tmp_path / "outside.toml"
    outside.write_text("untouched\n", encoding="utf-8")
    (out / "pyproject.toml").symlink_to(outside)

    assert (
        main(
            ["codegen", str(FULL_VOCABULARY), "--out", str(out), "--force"]
        )
        == EXIT_COLLISION
    )
    assert outside.read_text(encoding="utf-8") == "untouched\n"
    manifest = read_manifest(manifest_path(out))
    assert "pyproject.toml" not in manifest.entries()


def test_a_corrupt_manifest_is_refused_at_band_three(tmp_path: Path) -> None:
    out = tmp_path / "project"
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 0
    manifest_path(out).write_text("{ not json", encoding="utf-8")
    assert main(["codegen", str(FULL_VOCABULARY), "--out", str(out)]) == 3


def test_the_plan_touches_no_file(tmp_path: Path) -> None:
    """``plan_codegen`` performs NO writes — plan 06 recomputes the expected
    surface and must be able to do so without a filesystem effect."""
    root = tmp_path / "project"
    _generate(root)
    before = _digests(root)
    _model, project = _emit(FULL_VOCABULARY)
    plan = plan_codegen(project, root, read_manifest(manifest_path(root)))
    assert isinstance(plan, CodegenPlan)
    assert _digests(root) == before


def test_plan_codegen_over_an_absent_root_creates_nothing(tmp_path: Path) -> None:
    root = tmp_path / "never-made"
    _model, project = _emit(FULL_VOCABULARY)
    plan_codegen(project, root, None)
    assert not root.exists()


@pytest.mark.parametrize("mode", [0o400, 0o644])
def test_classify_file_reports_a_regular_file_regardless_of_mode(
    tmp_path: Path, mode: int
) -> None:
    """Permission bits are not ownership: a read-only derived file is still
    derived, and the classifier answers from CONTENT."""
    root = tmp_path / "project"
    project = _generate(root)
    target = _a_derived_relpath(project)
    path = root / target
    original_mode = stat.S_IMODE(path.stat().st_mode)
    path.chmod(mode)
    try:
        record = classify_file(
            root,
            target,
            expected_text=next(f.text for f in project.files if f.relpath == target),
            ownership="derived",
            recorded=read_manifest(manifest_path(root)).entries()[target],
        )
        assert record.state == "current"
    finally:
        path.chmod(original_mode)
