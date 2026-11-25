"""induction-skill IS1: the gnd-induce skill's one-home sentences, reactions, boundaries and docs row.

Spec: .gnd-planning/milestones/induction-skill/notes/phase-IS1-spec.md section 8 (T8, T13, T14, T17).
These tests read sentences; a sentence test cannot fail when an agent ignores the
sentence, so nothing here claims the skill is followed (spec section 8, honest limit).
"""

import hashlib
import re
import shutil
import subprocess
from pathlib import Path

import pytest
from test_ik6_walk import ABSOLUTE, DOWNSTREAM
from test_solve_successors import FROZEN_SKILLS

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src/gnd/skills"
SKILL = SKILLS / "gnd-induce/SKILL.md"
AGENTS_INDEX = ROOT / "docs/agents/index.md"
#: The IS1 base commit, named in the spec's delegated ruling (section 13).
IS1_BASE = "1e6083f3554e785aa994422c837fda874d74d1e6"

#: R-a..R-h of spec section 6.1: each lives in gnd-induce/SKILL.md and nowhere else.
ONE_HOME = {
    "R-a": "This skill never applies, confirms or edits a model, and never edits a proposal.",
    "R-b": "It never writes or edits a learner's clauses or run record, and never answers as the learner "
           "itself, except to save a learner's printed program verbatim as CLAUSES and to assemble a Popper "
           "run record as stated below.",
    "R-c": "It never writes, edits or re-binds a label manifest; labels come from the user.",
    "R-d": "It never installs a learner and never runs one the user did not name.",
    "R-e": "Covered sets come only from the learner's output or an evaluation the user selects, never from "
           "a GND verdict: the output of gnd import, gnd check, gnd measure or gnd discover, including "
           "refusal text.",
    "R-f": "After a coverage refusal it never changes the claim and imports again.",
    "R-g": "It never combines measure cells into one accuracy number.",
    "R-h": "It never copies host values or paths into a file it writes or a public page, apart from the "
           "learner artifacts it saves or assembles in the user's working paths; chat read-back may show them.",
}
REACTIONS_HEADER = "| Exit | Reaction |"
COMMANDS = ("gnd measure --labels", "gnd discover", "gnd export ilp", "gnd import ilp-rules",
            "gnd import mined-rules", "gnd check")


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("*", ""))


def packaged_texts(root: Path = SKILLS):
    for path in sorted(root.rglob("*.md")):
        yield path.relative_to(root).as_posix(), flat(path.read_text(encoding="utf-8"))


def homes(sentence: str, texts) -> list[str]:
    return [rel for rel, text in texts if sentence in text]


def skill_text() -> str:
    return flat(SKILL.read_text(encoding="utf-8"))


def section(name: str) -> str:
    raw = SKILL.read_text(encoding="utf-8")
    match = re.search(rf"^## {re.escape(name)}\n(.*?)(?=^## |\Z)", raw, re.MULTILINE | re.DOTALL)
    assert match, f"gnd-induce has no '## {name}' section"
    return flat(match.group(1))


# --- T8: one home per refusal, one reactions table, the ordering sentences ---

@pytest.mark.parametrize("rule", sorted(ONE_HOME))
def test_t8_each_refusal_has_exactly_one_home(rule):
    assert homes(ONE_HOME[rule], list(packaged_texts())) == ["gnd-induce/SKILL.md"], rule


def test_t8_a_seeded_second_home_is_found_by_name(tmp_path):
    seeded = tmp_path / "skills"
    shutil.copytree(SKILLS, seeded)
    other = seeded / "gnd-export/SKILL.md"
    other.write_text(other.read_text(encoding="utf-8") + "\n" + ONE_HOME["R-e"] + "\n", encoding="utf-8")
    assert homes(ONE_HOME["R-e"], list(packaged_texts(seeded))) == ["gnd-export/SKILL.md", "gnd-induce/SKILL.md"]


def test_t8_one_reactions_table_with_the_check_results_row():
    raw = SKILL.read_text(encoding="utf-8")
    assert raw.count(REACTIONS_HEADER) == 1
    table = section("Reactions")
    assert "| 1, 2 or 4 from `gnd check` | report the verdicts verbatim: they are results, not refusals |" in table
    assert "| 3 | report the named refusal or input error verbatim and stop" in table


def test_t8_the_stop_names_exit_3_and_the_handoff_names_exit_0():
    assert re.search(r"\| 3 \| [^|]*\bstop\b", section("Reactions"))
    handoff = section("Hand off")
    assert "exited 0 and emitted something" in handoff
    assert "each run record this skill assembled, the evaluation that produced its sets" in handoff
    assert "its `inducer` names the learner, because the program is the learner's" in handoff


def test_t8_the_llm_learner_is_never_played_by_the_skill():
    learn = section("Learn")
    assert "this skill never plays that model" in learn
    assert "evidence script" in learn
    assert "never answers as the learner itself" in learn


def test_t8_the_fact_type_family_routes_to_both_judges():
    text = section("Discover")
    assert "](../gnd-judge-fact-types/SKILL.md)" in text and "](../gnd-model-multivalued/SKILL.md)" in text


def test_t8_every_proposal_command_asks_the_actor_of_the_user():
    inputs = section("Fix the inputs first")
    assert "never a name taken from git, the shell or the environment" in inputs
    assert "Who should the proposal be recorded as" in inputs


def test_t10_the_skill_installs_nothing():
    text = skill_text()
    assert not re.search(r"\b(pip install|uv add|uv tool install|brew install|conda install)\b", text)


# --- T13: no frozen skill differs from the IS1 base --------------------------

def _frozen_diff(root: Path) -> list[str]:
    changed = []
    for name in FROZEN_SKILLS:
        result = subprocess.run(["git", "diff", "--quiet", IS1_BASE, "--", f"src/gnd/skills/{name}"],
                                cwd=root, capture_output=True, check=False)
        if result.returncode == 1:
            changed.append(name)
        elif result.returncode != 0:
            raise AssertionError(f"git diff failed for {name}: {result.stderr.decode(errors='replace')}")
    return changed


def test_t13_no_frozen_skill_differs_from_the_is1_base():
    assert _frozen_diff(ROOT) == []


def test_t13_a_seeded_edit_to_a_frozen_skill_is_named(tmp_path):
    clone = tmp_path / "clone"
    subprocess.run(["git", "clone", "-q", "--no-checkout", str(ROOT), str(clone)], check=True)
    subprocess.run(["git", "checkout", "-q", "--detach", IS1_BASE], cwd=clone, check=True)
    target = clone / "src/gnd/skills" / FROZEN_SKILLS[0] / "SKILL.md"
    target.write_text(target.read_text(encoding="utf-8") + "\nseeded\n", encoding="utf-8")
    assert _frozen_diff(clone) == [FROZEN_SKILLS[0]]


# --- T14: no host path, run directory or downstream name ---------------------

@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t14_no_absolute_path_in_the_skill(pattern):
    assert not re.search(pattern, SKILL.read_text(encoding="utf-8"))


def test_t14_a_seeded_absolute_path_is_found():
    seeded = SKILL.read_text(encoding="utf-8") + "\nsee /Users/someone/runs/x\n"
    assert any(re.search(p, seeded) for p in ABSOLUTE)


def test_t14_no_downstream_name_in_the_skill():
    tokens = set(re.findall(r"[a-z][a-z0-9_-]+", SKILL.read_text(encoding="utf-8").lower()))
    assert [t for t in tokens if hashlib.sha256(t.encode()).hexdigest() in DOWNSTREAM] == []


def test_t14_the_actor_is_never_derived_from_git():
    text = skill_text()
    assert not re.search(r"git config|user\.name|user\.email|\$USER|whoami", text)


# --- T17: the agents index names the skill and its six commands --------------

def test_t17_the_agents_index_has_a_gnd_induce_row():
    rows = [line for line in AGENTS_INDEX.read_text(encoding="utf-8").splitlines()
            if line.startswith("|") and "`gnd-induce`" in line]
    assert len(rows) == 1, rows
    assert all(command in rows[0] for command in COMMANDS), rows[0]
