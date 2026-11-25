"""induction-skill IS1: the gnd-induce skill's one-home sentences, reactions, boundaries and docs row.

Spec: .gnd-planning/milestones/induction-skill/notes/phase-IS1-spec.md section 8 (T8, T13, T14, T17).
These tests read sentences; a sentence test cannot fail when an agent ignores the
sentence, so nothing here claims the skill is followed (spec section 8, honest limit).
Review round 1 (notes/reviews/phase-IS1-r1) found that several first versions passed
when the instruction they guard was reversed; each repair names its finding.
"""

import hashlib
import re
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pytest
from test_ik6_walk import ABSOLUTE, DOWNSTREAM
from test_public_packaged_invocation_guards import EXECUTABLE_SNIPPETS
from test_solve_successors import FROZEN_SKILLS

ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "src/gnd/skills"
SKILL = SKILLS / "gnd-induce/SKILL.md"
AGENTS_INDEX = ROOT / "docs/agents/index.md"
#: The IS1 base commit, named in the spec's delegated ruling (section 13).
IS1_BASE = "1e6083f3554e785aa994422c837fda874d74d1e6"

#: R-a..R-h of spec section 6.1: each is said once, in gnd-induce/SKILL.md, and nowhere else.
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
#: The reactions table, row by row (F8: deleting a row must fail).
REACTIONS = (
    ("0", "report what GND printed"),
    ("3", "report the named refusal or input error verbatim and stop; a stale label manifest goes back to the user"),
    ("11", "(discover, export, either import) choose a new output path with the user; delete nothing"),
    ("1, 2 or 4 from `gnd check`", "report the verdicts verbatim: they are results, not refusals"),
    ("any other", "report verbatim and stop"),
)
#: The six command paths the skill documents, as fenced lines (F9: a missing one must fail).
COMMAND_PATHS = Counter({("measure",): 1, ("discover",): 1, ("export", "ilp"): 2, ("import", "ilp-rules"): 1,
                         ("import", "mined-rules"): 1, ("check",): 1})
INDEX_COMMANDS = ["gnd measure --labels", "gnd discover", "gnd export ilp", "gnd import ilp-rules",
                  "gnd import mined-rules", "gnd check"]
#: Absolute POSIX paths that are not part of a URL or a relative link (F11: /srv/... must fail).
ANY_ABSOLUTE = re.compile(r"(?<![\w:/.~-])/(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]*")
INSTALLS = re.compile(r"\b(?:pip3?|pipx|python3? -m pip|uv pip|brew|conda|mamba|apt-get|apt|npm|cargo)\s+install\b"
                      r"|\buv\s+(?:add|tool\s+install)\b", re.IGNORECASE)
GIT_IDENTITY = re.compile(r"\bgit\s+(?:config|var|log|show|blame)\b|GIT_(?:AUTHOR|COMMITTER)|user\.(?:name|email)"
                          r"|\$USER\b|\$LOGNAME\b|\bwhoami\b|\bid\s+-un\b", re.IGNORECASE)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.DOTALL)
FENCE = re.compile(r"^\s*(```|~~~)")


def visible(raw: str) -> str:
    """The text a reader sees: no HTML comments, emphasis markers dropped, whitespace collapsed."""
    return re.sub(r"\s+", " ", HTML_COMMENT.sub("", raw).replace("*", ""))


def skill_raw() -> str:
    return SKILL.read_text(encoding="utf-8")


def occurrences(sentence: str, root: Path = SKILLS) -> Counter:
    found = Counter()
    for path in sorted(root.rglob("*.md")):
        count = visible(path.read_text(encoding="utf-8")).count(sentence)
        if count:
            found[path.relative_to(root).as_posix()] = count
    return found


def section(name: str, raw: str | None = None) -> str:
    raw = skill_raw() if raw is None else raw
    match = re.search(rf"^##[ \t]+{re.escape(name)}[ \t]*\n(.*?)(?=^##[ \t]|\Z)", raw, re.MULTILINE | re.DOTALL)
    assert match, f"gnd-induce has no '## {name}' section"
    return visible(match.group(1)).strip()


def tables(raw: str) -> list[list[list[str]]]:
    """Markdown tables outside fences, as rows of stripped cells (header and rule rows dropped)."""
    found, current, in_fence = [], [], False
    for line in raw.splitlines():
        if FENCE.match(line):
            in_fence = not in_fence
            continue
        if not in_fence and line.strip().startswith("|"):
            current.append([cell.strip() for cell in line.strip().strip("|").split("|")])
        elif current:
            found.append(current)
            current = []
    if current:
        found.append(current)
    return [[row for row in table[2:]] for table in found if len(table) >= 2]


# --- T8: one home per refusal, said once ---------------------------------------

@pytest.mark.parametrize("rule", sorted(ONE_HOME))
def test_t8_each_refusal_is_said_once_and_only_in_gnd_induce(rule):
    assert occurrences(ONE_HOME[rule]) == Counter({"gnd-induce/SKILL.md": 1}), rule


def test_t8_a_seeded_second_home_is_found_by_name(tmp_path):
    seeded = tmp_path / "skills"
    shutil.copytree(SKILLS, seeded)
    other = seeded / "gnd-export/SKILL.md"
    other.write_text(other.read_text(encoding="utf-8") + "\n" + ONE_HOME["R-e"] + "\n", encoding="utf-8")
    assert occurrences(ONE_HOME["R-e"], seeded) == Counter({"gnd-export/SKILL.md": 1, "gnd-induce/SKILL.md": 1})


def test_t8_a_repeat_in_the_same_file_and_a_hidden_copy_are_both_caught(tmp_path):
    """F7: the first version counted files, so a second copy in gnd-induce passed, as did a comment."""
    seeded = tmp_path / "skills"
    shutil.copytree(SKILLS, seeded)
    skill = seeded / "gnd-induce/SKILL.md"
    text = skill.read_text(encoding="utf-8")
    skill.write_text(text + "\n" + ONE_HOME["R-e"] + "\n", encoding="utf-8")
    assert occurrences(ONE_HOME["R-e"], seeded)["gnd-induce/SKILL.md"] == 2
    skill.write_text(text.replace(ONE_HOME["R-c"], f"<!-- {ONE_HOME['R-c']} -->"), encoding="utf-8")
    assert occurrences(ONE_HOME["R-c"], seeded) == Counter()


# --- T8: the reactions table and the ordering sentences --------------------------

def test_t8_the_reactions_table_is_one_table_with_exactly_its_rows():
    raw = skill_raw()
    assert raw.count("| Exit | Reaction |") == 1
    rows = [tuple(row) for table in tables(raw) for row in table if len(row) == 2 and row[0] in dict(REACTIONS)]
    assert tuple(rows) == REACTIONS


def test_t8_the_handoff_is_conditional_on_a_written_proposal():
    """F8: the first version passed with the condition negated."""
    handoff = section("Hand off")
    assert handoff.startswith("Only after the command that wrote a proposal exited 0 and the proposal file "
                              "exists, name each proposal file and route it")
    assert not re.search(r"\b(even if|regardless|whether or not)\b", handoff, re.IGNORECASE)


def test_t8_the_handoff_names_the_proposal_inducer_not_a_run_record_field():
    """F3: the run record has learner; GND writes inducer into the proposal's induction provenance."""
    handoff = section("Hand off")
    assert "each run record this skill assembled, and the evaluation that produced its sets" in handoff
    assert "the proposal's induction provenance names the learner as its inducer" in handoff
    assert "its `inducer`" not in handoff


def test_t8_the_llm_learner_is_named_and_the_skill_stops():
    """D21, F8: the agent never plays the model; the documented route is run separately."""
    learn = section("Learn")
    assert ("The documented route is an evidence script that builds the prompt and runs a separate agent, "
            "outside this conversation; name it and stop.") in learn
    assert not re.search(r"\b(answer|write|construct|assemble)\w* (the|its|a) (prompt|answer|run record)\b[^.]*"
                         r"\bllm\b", learn, re.IGNORECASE)


def test_t8_discovery_hands_off_by_the_written_file_not_by_emitted():
    """F1: with the fact-type family, EMITTED 0 can come with a written proposal (FACT TYPES)."""
    discover = section("Discover")
    assert "hand off by whether the proposal file was written, not by `EMITTED`" in discover
    assert "`FACT TYPES`" in discover
    assert "`--type-evidence EVIDENCE`" in discover


def test_t8_the_miner_import_is_all_or_nothing():
    """F2: one failing mined rule refuses the whole set; no subset is kept."""
    learn = section("Learn")
    assert "admission is all-or-nothing" in learn
    assert "keeps only the rules" not in learn


def test_t8_a_learner_needs_a_class_mode_manifest_and_falls_back_to_neutral():
    """F4: an expected-state manifest has no classes to learn from; the fallback export is neutral."""
    learn = section("Learn")
    assert "class-mode label manifest" in learn
    assert "`--target neutral`" in learn


def test_t8_the_description_and_summary_claim_only_what_gnd_writes():
    """F5: a measure report is not a proposal; measure prints several cells per rule; Popper has run."""
    raw = skill_raw()
    assert "Every rule it produces is a proposal" in raw and "Every output is a proposal" not in raw
    assert "a cell per rule and label" not in raw
    assert "has not been run on GND's examples" not in raw
    assert "four induction commands" not in raw


def test_t8_every_proposal_command_asks_the_actor_of_the_user():
    inputs = section("Fix the inputs first")
    assert "never a name taken from git, the shell or the environment" in inputs
    assert "Who should the proposal be recorded as" in inputs


# --- T8, D23, F6: every skill link names the skill it opens ------------------------

def test_t8_each_skill_link_label_names_its_destination():
    links = re.findall(r"\[`?(gnd-[a-z-]+)`?\]\(\.\./(gnd-[a-z-]+)/SKILL\.md\)", skill_raw())
    assert links and [(label, target) for label, target in links if label != target] == []


def test_t8_the_fact_type_family_routes_each_kind_to_its_judge():
    discover = section("Discover")
    assert "duplicates go to [gnd-judge-fact-types](../gnd-judge-fact-types/SKILL.md)" in discover
    assert "multi-valued groups to [gnd-model-multivalued](../gnd-model-multivalued/SKILL.md)" in discover


# --- T7 for this skill, F9: the six command paths, and option names in full ---------

def _induce_snippets():
    return [s for s in EXECUTABLE_SNIPPETS if s.skill == "gnd-induce"]


def test_t7_the_skill_documents_exactly_its_command_paths():
    assert Counter(s.subcommand_path for s in _induce_snippets()) == COMMAND_PATHS


@pytest.mark.parametrize("path", sorted(COMMAND_PATHS), ids=lambda p: "-".join(p))
def test_t7_every_option_is_a_full_option_name_of_its_command(path):
    help_text = subprocess.run([sys.executable, "-m", "gnd", *path, "--help"], capture_output=True, text=True,
                               check=True).stdout
    options = set(re.findall(r"(?<![\w-])--[a-z][a-z0-9-]*", help_text))
    used = {option for s in _induce_snippets() if s.subcommand_path == path for option in s.long_options}
    assert used - options == set(), sorted(used - options)


def test_t7_every_actor_is_the_placeholder():
    """F11: a fixed --actor would record one name for every user."""
    actors = [s.tokens[s.tokens.index("--actor") + 1] for s in _induce_snippets() if "--actor" in s.tokens]
    assert actors and set(actors) == {"ACTOR"}


def test_t10_the_skill_installs_nothing():
    assert not INSTALLS.search(visible(skill_raw()))


@pytest.mark.parametrize("line", ["pip3 install popper", "uv tool install x", "brew install swi-prolog",
                                  "python -m pip install popper"])
def test_t10_the_install_pattern_catches_each_installer(line):
    assert INSTALLS.search(line)


# --- T13: no frozen skill differs from the IS1 base --------------------------------

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


# --- T14: no host path, run directory, downstream name or git-derived actor ----------

@pytest.mark.parametrize("pattern", ABSOLUTE)
def test_t14_no_absolute_path_in_the_skill(pattern):
    assert not re.search(pattern, skill_raw())


def test_t14_no_absolute_path_of_any_root():
    assert ANY_ABSOLUTE.findall(skill_raw()) == []


@pytest.mark.parametrize("seed", ["see /srv/reviewer/runs/april", "under /mnt/data/x", "(/etc/gnd/cfg)"])
def test_t14_a_seeded_absolute_path_is_found(seed):
    assert ANY_ABSOLUTE.search(skill_raw() + "\n" + seed + "\n")


def test_t14_urls_and_relative_links_are_not_paths():
    assert ANY_ABSOLUTE.findall("[x](../gnd-x/SKILL.md) https://github.com/a/b/blob/main/c.md src/gnd/x.json") == []


def test_t14_no_downstream_name_in_the_skill():
    tokens = set(re.findall(r"[a-z][a-z0-9_-]+", skill_raw().lower()))
    assert [t for t in tokens if hashlib.sha256(t.encode()).hexdigest() in DOWNSTREAM] == []


def test_t14_the_actor_is_never_derived_from_git():
    assert not GIT_IDENTITY.search(visible(skill_raw()))


@pytest.mark.parametrize("line", ["git var GIT_AUTHOR_IDENT", "git config user.name", "echo $USER",
                                  "git log -1 --format=%an"])
def test_t14_the_identity_pattern_catches_each_source(line):
    assert GIT_IDENTITY.search(line)


# --- T17: the agents index row names the skill and exactly its six commands ----------

def test_t17_the_agents_index_has_a_gnd_induce_row():
    """F10: the row must be a table row outside any fence, and its commands compared in full."""
    rows = [row for table in tables(AGENTS_INDEX.read_text(encoding="utf-8")) for row in table
            if any(cell == "`gnd-induce`" for cell in row)]
    assert len(rows) == 1, rows
    commands = [cell for cell in rows[0] if "`gnd " in cell]
    assert len(commands) == 1
    assert [c.strip().strip("`") for c in commands[0].split(",")] == INDEX_COMMANDS


def test_t17_a_row_inside_a_fence_or_a_wrong_command_is_refused():
    row = next(line for line in AGENTS_INDEX.read_text(encoding="utf-8").splitlines() if "`gnd-induce`" in line)
    header = "| Task | Skill | Writes | Commands | Refusal |\n|---|---|---|---|---|\n"
    assert not [r for t in tables("```text\n" + header + row + "\n```\n") for r in t]
    wrong = row.replace("`gnd check`", "`gnd checker`")
    cells = next(c for table in tables(header + wrong + "\n") for r in table for c in r if "`gnd " in c)
    assert [c.strip().strip("`") for c in cells.split(",")] != INDEX_COMMANDS
