"""Synthetic scratch-root installer lifecycle; never touches the real home."""
from __future__ import annotations

import os
from pathlib import Path

import pytest

from gnd import install


@pytest.mark.parametrize("runtime", ["claude", "codex"])
@pytest.mark.parametrize("scope", ["project", "global"])
@pytest.mark.parametrize("mode", ["copy", "symlink"])
def test_owned_lifecycle_preserves_foreign_content(tmp_path, runtime, scope, mode):
    source = Path(str(install.packaged_skills_root()))
    root = tmp_path / runtime / scope
    target = install.InstallTarget(runtime=runtime, scope=scope, root=root)
    foreign = root / "my-independent-skill"
    foreign.mkdir(parents=True)
    (foreign / "SKILL.md").write_bytes(b"synthetic foreign content")
    records = install.plan(source, target, None, mode=mode)
    assert all(r.state == "create" for r in records)
    placed = install.apply(source, target, records, mode=mode)
    assert placed.writes > 0
    manifest = install.read_manifest(root)
    assert manifest is not None
    current = install.plan(source, target, manifest, mode=mode)
    assert all(r.state == "current" for r in current)
    assert install.apply(source, target, current, mode=mode, manifest=manifest).writes == 0
    report = install.diagnose(source, [target])
    assert not report.has_collision() and not report.has_drift()
    removed = install.remove(source, target, manifest)
    assert removed.removed and not removed.retained and removed.manifest_removed
    assert (foreign / "SKILL.md").read_bytes() == b"synthetic foreign content"
    assert sorted(p.name for p in root.iterdir()) == [foreign.name]


@pytest.mark.parametrize("runtime", ["claude", "codex"])
def test_collision_needs_force_and_modified_copy_survives(tmp_path, runtime):
    source = install.packaged_skills_root()
    root = tmp_path / runtime
    target = install.InstallTarget(runtime=runtime, scope="project", root=root)
    occupied = root / "gnd-orm-core/SKILL.md"
    occupied.parent.mkdir(parents=True)
    occupied.write_bytes(b"foreign synthetic bytes")
    records = install.plan(source, target, None)
    assert any(r.state == "collided" for r in records)
    refused = install.apply(source, target, records)
    assert refused.collisions
    assert occupied.read_bytes() == b"foreign synthetic bytes"
    manifest = install.read_manifest(root)
    records = install.plan(source, target, manifest)
    adopted = install.apply(source, target, records, force=True, manifest=manifest)
    assert not adopted.collisions
    manifest = install.read_manifest(root)
    occupied.write_bytes(b"owned bytes modified by user")
    records = install.plan(source, target, manifest)
    assert any(r.state == "modified" for r in records)
    install.apply(source, target, records, force=True, manifest=manifest)
    assert occupied.read_bytes() == b"owned bytes modified by user"
    removed = install.remove(source, target, manifest)
    assert removed.retained
    assert occupied.read_bytes() == b"owned bytes modified by user"


@pytest.mark.parametrize("runtime", ["claude", "codex"])
def test_retargeted_link_neither_unlinked_nor_followed(tmp_path, runtime):
    source = Path(str(install.packaged_skills_root()))
    root = tmp_path / runtime
    target = install.InstallTarget(runtime=runtime, scope="project", root=root)
    records = install.plan(source, target, None, mode="symlink")
    install.apply(source, target, records, mode="symlink")
    manifest = install.read_manifest(root)
    victim = tmp_path / "outside"
    victim.mkdir()
    (victim / "sentinel").write_bytes(b"synthetic sentinel, no credentials")
    link = root / "gnd-orm-core"
    link.unlink()
    link.symlink_to(victim, target_is_directory=True)
    report = install.diagnose(source, [target])
    assert report.has_drift()
    removed = install.remove(source, target, manifest)
    assert any(r.relpath == "gnd-orm-core" for r in removed.retained)
    assert link.is_symlink() and os.readlink(link) == str(victim)
    assert (victim / "sentinel").read_bytes() == b"synthetic sentinel, no credentials"
