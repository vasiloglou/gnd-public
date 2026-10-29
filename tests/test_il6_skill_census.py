"""IL6: every packaged skill file appears in the ilp-learners skill census exactly once (spec T7)."""

import re
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / ".gnd-planning/milestones/ilp-learners/skill-census.md"
PHASE = re.compile(r"IL[1-6](?:-Q\d+)?|IL-close")
CURRENT = "IL6"  # the scope an uncommitted edit is credited to
# The milestone's first commit (plan and IL1 spec); its parent is the milestone base.
MILESTONE_FIRST = "07f4d45fcdf8a5c44a69ee5e2dd9fbe2112e1b86"


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


def git_phases(path: str) -> set[str]:
    """The milestone phases whose commit subjects since the base name this file, plus CURRENT
    for an uncommitted edit. Other milestones' commits merged in the window are not counted."""
    subjects = subprocess.run(["git", "log", "--format=%s", f"{MILESTONE_FIRST}^..HEAD", "--", path], cwd=ROOT,
                              check=True, capture_output=True, text=True).stdout
    phases = {m for scope in re.findall(r"\(([^)]*)\)", subjects) for m in PHASE.findall(scope)}
    dirty = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", path], cwd=ROOT, check=False).returncode
    return phases | ({CURRENT} if dirty else set())


def phase_errors(rows: list[tuple[str, str]]) -> list[str]:
    return [f"wrong phase: {path}" for path, changed in rows
            if ({c.strip() for c in changed.split(",")} if changed != "no" else set()) != git_phases(path)]


def test_t7_every_packaged_skill_file_appears_exactly_once():
    packaged = packaged_files()
    assert len(packaged) == 65
    assert census_errors(census_rows(CENSUS.read_text(encoding="utf-8")), packaged) == []


def test_t7_each_cell_names_exactly_the_phases_git_records():
    """A `no` row has no milestone commit; a changed row names exactly the phases that changed it."""
    assert phase_errors(census_rows(CENSUS.read_text(encoding="utf-8"))) == []


def test_t7_a_wrong_phase_fails_by_name():
    rows = [(p, "IL1") if p.endswith("gnd-export/SKILL.md") else (p, c)
            for p, c in census_rows(CENSUS.read_text(encoding="utf-8"))]
    assert phase_errors(rows) == ["wrong phase: src/gnd/skills/gnd-export/SKILL.md"]


def test_t7_an_unmarked_change_fails_by_name():
    rows = [(p, "no") if p.endswith("gnd-model-evolve/SKILL.md") else (p, c)
            for p, c in census_rows(CENSUS.read_text(encoding="utf-8"))]
    assert phase_errors(rows) == ["wrong phase: src/gnd/skills/gnd-model-evolve/SKILL.md"]


@pytest.mark.parametrize("mutate, expected", [
    (lambda rows: rows + [rows[0]], "duplicate: src/gnd/skills/gnd-adopt/SKILL.md"),
    (lambda rows: rows[1:], "missing: src/gnd/skills/gnd-adopt/SKILL.md"),
    (lambda rows: rows + [("src/gnd/skills/gnd-x/SKILL.md", "no")], "unknown: src/gnd/skills/gnd-x/SKILL.md"),
    (lambda rows: [(rows[0][0], "yes")] + rows[1:], "changed cell names no phase: src/gnd/skills/gnd-adopt/SKILL.md"),
])
def test_t7_a_bad_census_fails_by_name(mutate, expected):
    rows = census_rows(CENSUS.read_text(encoding="utf-8"))
    assert census_errors(mutate(rows), packaged_files()) == [expected]


def test_t7_the_two_pin_sites_name_what_the_milestone_shipped():
    export = (ROOT / "src/gnd/skills/gnd-export/SKILL.md").read_text(encoding="utf-8")
    evolve = (ROOT / "src/gnd/skills/gnd-model-evolve/SKILL.md").read_text(encoding="utf-8")
    for target in ("popper", "ilasp", "rules", "amie", "neutral"):
        assert f"`{target}`" in export, target
    assert "`gnd import mined-rules`" in export and "`gnd import ilp-rules`" in export
    assert "`gnd import mined-rules`" in evolve
