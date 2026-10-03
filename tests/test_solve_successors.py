"""Solve controls over public skills and independently synthetic workspaces."""
from __future__ import annotations

import ast
import hashlib
import re
import shutil
from pathlib import Path

import pytest
from test_solve import (
    REPO_ROOT,
    SOLVE_SOURCE,
    _allow,
    _fixed_clock,
    _run,
    _station_name_from_capture,
    _walk_file,
    b5_failures,
)

from gnd import solve

FROZEN_SKILLS = ("gnd-codegen", "gnd-conformance", "gnd-extract", "gnd-render-doc", "gnd-review-panel", "gnd-update-review-panel")


def _directory_manifest(root: Path) -> tuple[int, bytes, str]:
    files = sorted(path for path in root.rglob("*") if path.is_file())
    manifest = b"".join(f"{path.relative_to(root).as_posix()} {hashlib.sha256(path.read_bytes()).hexdigest()}\n".encode() for path in files)
    return len(files), manifest, hashlib.sha256(manifest).hexdigest()


FROZEN_SKILL_BASELINE = {name: _directory_manifest(REPO_ROOT / "src/gnd/skills" / name) for name in FROZEN_SKILLS}
PUBLIC_MODEL = REPO_ROOT / "tests/fixtures/public-launch-phase-2/model.orm.yaml"


def test_f12_walkthrough_exit_table_includes_the_walk_halted_band() -> None:
    walkthrough = (REPO_ROOT / "docs/walkthrough.md").read_text(encoding="utf-8")
    assert "| | 17 | a gated station walk halted before completing its selection |" in walkthrough


def test_t13_solve_module_is_a_v2_offline_scan_root() -> None:
    source = (REPO_ROOT / "tests/test_v2_offline.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    root_entries = [node for node in ast.walk(tree) if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div) and isinstance(node.right, ast.Constant) and node.right.value == "solve.py"]
    assert len(root_entries) == 1
    assert SOLVE_SOURCE.is_file()


def test_t14b_ci_walk_uses_real_process_spawn_for_four_non_agent_stations(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    model = workspace / "model.orm.yaml"
    shutil.copy2(PUBLIC_MODEL, model)
    experiment = workspace / "EXP-TEST"
    prior_run = experiment / "runs/run-0001"
    prior_run.mkdir(parents=True)
    (prior_run / "result.json").write_text("{}\n", encoding="utf-8")
    actual_processes: list[str] = []

    def mixed_spawn(request: solve.StationSpawn) -> solve.StationOutcome:
        name = _station_name_from_capture(request.stdout_path)
        if name == "exp-run":
            request.stdout_path.parent.mkdir(parents=True, exist_ok=True)
            request.stdout_path.write_bytes(b'{"run_id":"run-0002"}\n')
            request.stderr_path.write_bytes(b"injected-exp-err\n")
            run_root = experiment / "runs/run-0002"
            run_root.mkdir(parents=True)
            (run_root / "result.json").write_text("{}\n", encoding="utf-8")
            return solve.StationOutcome(0, None)
        actual_processes.append(name)
        return solve._spawn_station(request)

    assert _run(model, workspace, experiment=experiment, adapter="claude", gate=_allow, clock=_fixed_clock, spawn=mixed_spawn) == 0
    assert actual_processes == ["validate", "synth", "codegen", "conformance"]
    assert b5_failures(_walk_file(workspace).read_bytes()) == frozenset()


def test_t16_six_frozen_skills_match_their_whole_directory_baselines(tmp_path: Path) -> None:
    current = {name: _directory_manifest(REPO_ROOT / "src/gnd/skills" / name) for name in FROZEN_SKILLS}
    assert current == FROZEN_SKILL_BASELINE
    assert all(count > 0 and manifest and len(digest) == 64 for count, manifest, digest in current.values())
    source = REPO_ROOT / "src/gnd/skills" / FROZEN_SKILLS[0]
    copied = tmp_path / FROZEN_SKILLS[0]
    shutil.copytree(source, copied)
    before = _directory_manifest(copied)
    skill_file = copied / "SKILL.md"
    skill_file.write_bytes(skill_file.read_bytes() + b"\nnegative-control\n")
    after_edit = _directory_manifest(copied)
    assert after_edit != before
    (copied / "added.txt").write_text("negative control\n", encoding="utf-8")
    after_add = _directory_manifest(copied)
    assert after_add != after_edit
    assert after_add[0] == after_edit[0] + 1


def _integer_station_values() -> list[int]:
    path = REPO_ROOT / "tests/fixtures/public-launch-phase-3/solve-station-records.md"
    return [int(match.group(1)) for line in path.read_text().splitlines() if (match := re.fullmatch(r"station:\s*(\d+)\s*", line))]


def test_t25_integer_station_numbers_still_resolve() -> None:
    skill = (REPO_ROOT / "src/gnd/skills/gnd-solve/SKILL.md").read_text(encoding="utf-8")
    prose_numbers = {int(value) for value in re.findall(r"\bStation (\d+)\b", skill)}
    table_numbers = set(range(1, len(solve.STATIONS) + 1))

    def resolves(value: int) -> bool:
        return value in prose_numbers or value in table_numbers

    values = _integer_station_values()
    assert values
    assert all(resolves(value) for value in values)
    assert not resolves(99)


def test_t42_station_children_do_not_depend_on_console_script_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    import os
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    model = workspace / "model.orm.yaml"
    shutil.copy2(PUBLIC_MODEL, model)
    monkeypatch.setenv("PATH", os.defpath)
    assert _run(model, workspace, start="validate", until="validate", spawn=solve._spawn_station) == 0
