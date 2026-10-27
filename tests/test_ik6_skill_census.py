"""IK6: every packaged skill file appears in the milestone's skill census exactly once."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / ".gnd-planning/milestones/induced-knowledge/skill-census.md"
PHASE = re.compile(r"IK[1-6](?:-Q\d+)?|IK-close")
CURRENT = "IK-close"  # the scope an uncommitted edit is credited to
MILESTONE_FIRST = "6f070354b29042b46aaa48e5eafaa6ca75299cde"  # the first IK1 commit; its parent is the milestone base


def census_rows(text: str) -> list[tuple[str, str]]:
    rows = []
    for line in text.splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("| src/gnd/skills/") and len(cells) == 3:
            rows.append((cells[0], cells[1]))
    return rows


def census_errors(rows: list[tuple[str, str]], packaged: list[str]) -> list[str]:
    """Each refusal names its path: a duplicate, a missing row, an unknown path or a bad changed cell."""
    paths = [path for path, _ in rows]
    errors = [f"duplicate: {p}" for p in sorted({p for p in paths if paths.count(p) > 1})]
    errors += [f"missing: {p}" for p in sorted(set(packaged) - set(paths))]
    errors += [f"unknown: {p}" for p in sorted(set(paths) - set(packaged))]
    for path, changed in rows:
        if changed != "no" and not all(PHASE.fullmatch(part.strip()) for part in changed.split(",")):
            errors.append(f"changed cell names no phase: {path}")
    return errors


def packaged_files() -> list[str]:
    out = subprocess.run(["git", "ls-files", "src/gnd/skills"], cwd=ROOT, check=True,
                         capture_output=True, text=True).stdout
    return out.split()


def test_t4_every_packaged_skill_file_appears_exactly_once():
    packaged = packaged_files()
    assert len(packaged) == 65
    assert census_errors(census_rows(CENSUS.read_text(encoding="utf-8")), packaged) == []


def test_t4_the_changed_cells_agree_with_git():
    """A file marked changed is exactly a file that differs from the milestone base."""
    base = subprocess.run(["git", "rev-parse", f"{MILESTONE_FIRST}^"], cwd=ROOT, check=True,
                          capture_output=True, text=True).stdout.strip()
    differs = set(subprocess.run(["git", "diff", "--name-only", base, "--", "src/gnd/skills"], cwd=ROOT,
                                 check=True, capture_output=True, text=True).stdout.split())
    marked = {path for path, changed in census_rows(CENSUS.read_text(encoding="utf-8")) if changed != "no"}
    assert marked == differs


def git_phases(path: str) -> set[str]:
    """The phases whose commit subjects since the milestone base name this file, plus CURRENT for uncommitted edits."""
    subjects = subprocess.run(["git", "log", "--format=%s", f"{MILESTONE_FIRST}^..HEAD", "--", path], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout
    phases = {m for scope in re.findall(r"\(([^)]*)\)", subjects) for m in PHASE.findall(scope)}
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, check=False).returncode
    return phases | ({CURRENT} if dirty else set())


def phase_errors(rows: list[tuple[str, str]]) -> list[str]:
    return [f"wrong phase: {path}" for path, changed in rows
            if changed != "no" and {c.strip() for c in changed.split(",")} != git_phases(path)]


def test_t4_each_changed_cell_names_the_phases_git_records():
    assert phase_errors(census_rows(CENSUS.read_text(encoding="utf-8"))) == []


def test_t4_a_wrong_phase_fails_by_name():
    rows = [(p, "IK1") if p.endswith("gnd-solve/SKILL.md") else (p, c)
            for p, c in census_rows(CENSUS.read_text(encoding="utf-8"))]
    assert phase_errors(rows) == ["wrong phase: src/gnd/skills/gnd-solve/SKILL.md"]


@pytest.mark.parametrize("mutate, expected", [
    (lambda rows: rows + [rows[0]], "duplicate: src/gnd/skills/gnd-adopt/SKILL.md"),
    (lambda rows: rows[1:], "missing: src/gnd/skills/gnd-adopt/SKILL.md"),
    (lambda rows: rows + [("src/gnd/skills/gnd-x/SKILL.md", "no")], "unknown: src/gnd/skills/gnd-x/SKILL.md"),
    (lambda rows: [(rows[0][0], "yes")] + rows[1:], "changed cell names no phase: src/gnd/skills/gnd-adopt/SKILL.md"),
])
def test_t4_a_bad_census_fails_by_name(mutate, expected):
    rows = census_rows(CENSUS.read_text(encoding="utf-8"))
    assert census_errors(mutate(rows), packaged_files()) == [expected]


def test_t5_each_ik6_skill_edit_is_present():
    def text(rel):
        return (ROOT / "src/gnd/skills" / rel).read_text(encoding="utf-8")
    assert "`gnd export ilp` is not a derivation export" in text("gnd-export/SKILL.md")
    assert "`uv run gnd measure MODEL --labels MANIFEST`" in text("gnd-dev-session/SKILL.md")
    assert "description `summary`" in text("gnd-codegen/SKILL.md")
