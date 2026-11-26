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
from support.markdown_sections import markdown_blocks, section_blocks
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
    # IS2-A1 item 4 (IS2 spec section 14): a proposal is never written by hand either.
    "R-a": "This skill never applies, confirms or edits a model, and never writes or edits a proposal by hand: "
           "only a gnd command writes one.",
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
#: Absolute POSIX paths that are not part of a URL or a relative link (F11: /srv/... must fail). A path segment
#: is any run of word characters, dots and dashes, in any script (IS1 round 2 F10: /workspace, /Δεδομένα/runs).
ANY_ABSOLUTE = re.compile(r"(?<![\w:/.~-])/[\w.-]+(?:/[\w.-]*)*")
#: An installer, any options, then its install verb (F10: `pip3 --isolated install popper`).
_OPTIONS = r"(?:\s+-{1,2}[\w-]+(?:=\S+)?)*"
INSTALLS = re.compile(rf"\b(?:pip3?|pipx|python3?{_OPTIONS}\s+-m\s+pip|uv{_OPTIONS}\s+pip|brew|conda|mamba|apt-get|apt|npm"
                      rf"|cargo){_OPTIONS}\s+install\b|\buv{_OPTIONS}\s+(?:add|tool{_OPTIONS}\s+install)\b", re.IGNORECASE)
#: A shell variable is read as $NAME or ${NAME} (F10: `${USER}`).
GIT_IDENTITY = re.compile(r"\bgit\s+(?:config|var|log|show|blame)\b|GIT_(?:AUTHOR|COMMITTER)|user\.(?:name|email)"
                          r"|\$\{?(?:USER|LOGNAME|USERNAME)\b|%USERNAME%|\bwhoami\b|\bid\s+-un\b", re.IGNORECASE)
#: An inline link: a label without brackets, a destination without spaces or parentheses, an optional title
#: in double quotes, single quotes or parentheses (IS1 round 2 F8: a titled link escaped the label matcher).
LINK = re.compile(r"\[([^\[\]]+)\]\(([^()\s]+)(?:\s+(?:\"[^\"]*\"|'[^']*'|\([^()]*\)))?\)")
SKILL_LINK = re.compile(r"\.\./(gnd-[a-z-]+)/SKILL\.md")


def _texts(blocks) -> list[str]:
    """Every block's text, a table's header and cells included, in page order."""
    return [part for block in blocks
            for part in ([*block.header, *(cell for row in block.rows for cell in row)] if block.kind == "table"
                         else [block.text])]


def visible(raw: str) -> str:
    """The text a reader sees, read through the shared Markdown reader: no HTML comments and no link reference
    definitions (IS1 round 2 F7: a refusal moved into a definition's title was counted), emphasis markers
    dropped, whitespace collapsed."""
    return re.sub(r"\s+", " ", " ".join(_texts(markdown_blocks(raw))).replace("*", ""))


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
    """A section's visible text: its heading read as Markdown reads it, outside fences, a closing `#` run
    allowed (IS1 round 2 F7: a fenced heading was accepted and `## Learn ##` refused)."""
    raw = skill_raw() if raw is None else raw
    return re.sub(r"\s+", " ", " ".join(_texts(section_blocks(raw, name))).replace("*", "")).strip()


def paragraph(name: str, containing: str) -> str:
    """The one paragraph of a section that holds CONTAINING, as written (whitespace collapsed)."""
    found = [b.text for b in section_blocks(skill_raw(), name) if b.kind == "paragraph" and containing in b.text]
    assert len(found) == 1, (name, containing, found)
    return found[0]


def tables(raw: str) -> list[list[list[str]]]:
    """The visible Markdown tables, outer pipes optional, as body rows of cells (IS1 round 2 F6: a table in a
    comment was read, and one without outer pipes was not)."""
    return [block.rows for block in markdown_blocks(raw) if block.kind == "table"]


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

def reaction_tables(raw: str) -> list[tuple[tuple[str, ...], ...]]:
    return [tuple(map(tuple, b.rows)) for b in markdown_blocks(raw) if b.kind == "table" and b.header == ["Exit", "Reaction"]]


def test_t8_the_reactions_table_is_one_table_with_exactly_its_rows():
    """IS1 round 2 F6: rows with an unfamiliar exit were filtered out before the comparison."""
    assert reaction_tables(skill_raw()) == [REACTIONS]


@pytest.mark.parametrize("edit", [
    lambda raw: raw.replace("| any other |", "| 6 | retry until it passes |\n| any other |", 1),
    lambda raw: raw.replace("| Exit | Reaction |", "<!--\n| Exit | Reaction |", 1).replace(
        "| any other | report verbatim and stop |", "| any other | report verbatim and stop |\n-->", 1),
])
def test_q2_an_extra_or_hidden_reactions_row_is_found(edit):
    edited = edit(skill_raw())
    assert edited != skill_raw() and reaction_tables(edited) != [REACTIONS]


def test_q2_a_table_without_outer_pipes_is_read():
    table = skill_raw().split("| Exit | Reaction |", 1)[1].split("\n\n", 1)[0]
    lines = [line.strip().strip("|") for line in ("| Exit | Reaction |" + table).splitlines()]
    assert len(lines) == 7 and reaction_tables("\n".join(lines)) == [REACTIONS]


def handoff_links(raw: str | None = None) -> list[tuple[str, str]]:
    return LINK.findall(section("Hand off", raw))


def test_q2_the_handoff_links_the_review_skill_and_nothing_else():
    """IS1 round 2 F8: changing only the Hand off link passed, since the summary still linked evolve."""
    assert handoff_links() == [("gnd-model-evolve", "../gnd-model-evolve/SKILL.md")]
    for wrong in ("[gnd-export](../gnd-export/SKILL.md)", "[gnd-model-evolve] (../gnd-model-evolve/SKILL.md)"):
        raw = skill_raw().replace("[gnd-model-evolve](../gnd-model-evolve/SKILL.md), which previews", f"{wrong}, which previews", 1)
        assert raw != skill_raw() and handoff_links(raw) != [("gnd-model-evolve", "../gnd-model-evolve/SKILL.md")]


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


#: Whole paragraphs, as written (IS1 round 2 F9: a keyword test passed a reversal that kept its keywords, and a
#: sentence inserted before the stop passed too). A reversal in a paragraph of its own still passes: the honest
#: limit of a sentence test (spec section 8).
PINNED = {
    ("Score", "Report every cell"): (
        'Report every cell GND printed for each rule, as printed, with its numerator and denominator ("fired on 2 '
        'of 4 flagged populations"). The cells differ by mode, and the [measure reference](https://github.com/'
        'vasiloglou/gnd-public/blob/main/docs/reference/measure-labels.md) lists them: a class-mode manifest '
        'scores rules against classes, and an expected-state manifest scores each population against its expected '
        'verdict. In expected-state mode `gnd measure` exits 6 on a checker defect, which you report as printed. '
        'It never combines measure cells into one accuracy number.'),
    ("Discover", "Both judges read"): (
        "Judging the groups gnd discover --families fact-type forms is not this skill: duplicates go to "
        "[gnd-judge-fact-types](../gnd-judge-fact-types/SKILL.md), and multi-valued groups to "
        "[gnd-model-multivalued](../gnd-model-multivalued/SKILL.md). Both judges read a type-evidence file, so "
        "for them run discover with `--type-evidence EVIDENCE` beside `--families fact-type`."),
    ("Learn", "no learner named X"): (
        "Then run the learner, with a stated time limit, and give the user the exact command you ran. It never "
        "installs a learner and never runs one the user did not name. When the named learner is not found, stop "
        'and say, in these words, "no learner named X is installed", and offer the neutral export alone '
        "(`--target neutral`). It holds the learner-neutral form only; a learner run later needs its own "
        "target's files ([the ILP bridge](https://github.com/vasiloglou/gnd-public/blob/main/docs/reference/"
        "ilp-bridge.md))."),
    ("Learn", "A language model as the learner"): (
        "**A language model as the learner** (`--target llm`) needs a run record independent of the model that "
        "answered, so this skill never plays that model. The documented route is an evidence script that builds "
        "the prompt and runs a separate agent, outside this conversation; name it and stop."),
    ("Learn", "admission is all-or-nothing"): (
        "The miner the user named runs between the two commands. GND writes the proposal only if every mined rule "
        "holds for every case on the population: admission is all-or-nothing, so one failing rule means no "
        "proposal at all."),
}


@pytest.mark.parametrize("key", sorted(PINNED))
def test_q2_each_pinned_paragraph_is_as_written(key):
    assert paragraph(*key) == PINNED[key]


@pytest.mark.parametrize("old, new", [
    ("run discover with `--type-evidence", "run discover without `--type-evidence"),
    ("and offer the neutral export alone (`--target neutral`)", "and never offer the neutral export (`--target neutral`)"),
    ("The documented route is", "Answer the prompt in this conversation first. The documented route is"),
    ("admission is all-or-nothing, so one failing rule means no proposal at all.",
     "partial admission is all-or-nothing per rule, so hand off the surviving rules."),
])
def test_q2_a_reversal_that_keeps_the_keywords_is_found(old, new, monkeypatch):
    raw = skill_raw()
    assert old in raw
    monkeypatch.setattr(sys.modules[__name__], "skill_raw", lambda: raw.replace(old, new, 1))
    assert any(paragraph(*key) != PINNED[key] for key in PINNED if key[1] in raw.replace(old, new, 1))


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
    # Read as the reader reads it, so a phrase split over a line break is still found (IS1 round 2 F3).
    flat = visible(skill_raw())
    assert "Every rule it produces is a proposal" in flat and "Every output is a proposal" not in flat
    assert "a cell per rule and label" not in flat
    assert "has not been run on GND's examples" not in flat
    assert "four induction commands" not in flat
    # Round 2 (notes/reviews/phase-IS1-r2): F3, F1 and F2.
    assert "hands every result to review" not in flat and "hands every proposal to review" in flat
    assert "including the cells for vacuous and unchecked results" not in flat
    assert "cells differ by mode" in flat
    assert "its files are what any learner reads" not in flat
    assert "needs its own target's files" in flat


def test_t8_every_proposal_command_asks_the_actor_of_the_user():
    inputs = section("Fix the inputs first")
    assert "never a name taken from git, the shell or the environment" in inputs
    assert "Who should the proposal be recorded as" in inputs


# --- IS2-A1 (IS2 spec section 14): what the first Haiku recordings did not follow ----

def test_a1_outputs_stay_in_the_working_folder():
    inputs = section("Fix the inputs first")
    assert "never in a temporary or scratch folder" in inputs
    assert "Read nothing outside the working folder but this skill's linked references" in inputs


def test_a1_the_actor_is_asked_before_the_first_writing_command():
    inputs = section("Fix the inputs first")
    assert "Ask before the first command that writes anything, and wait for the answer" in inputs
    assert "never a placeholder" in inputs


def test_a1_dont_import_stops_at_the_learner():
    learn = section("Learn")
    assert ("When the user asks for the learner's answer only, or says not to import yet, stop here: report "
            "its claim as unchecked and run no `gnd import`.") in learn


def test_a1_the_handoff_stops_without_starting_review():
    handoff = section("Hand off")
    assert handoff.endswith("This skill never starts gnd-model-evolve, gnd evolve preview or gnd evolve apply "
                            "itself; the user starts the review.")


def test_a1_the_absent_learner_stop_is_said_in_its_words():
    assert 'stop and say, in these words, "no learner named X is installed"' in section("Learn")


# --- T8, D23, F6: every skill link names the skill it opens ------------------------

def skill_links(raw: str) -> list[tuple[str, str]]:
    """Each visible link to a skill, as (label, the skill it opens), titled or not."""
    return [(label.strip("`"), SKILL_LINK.fullmatch(destination).group(1)) for label, destination in
            LINK.findall(visible(raw)) if SKILL_LINK.fullmatch(destination)]


def test_t8_each_skill_link_label_names_its_destination():
    links = skill_links(skill_raw())
    assert links and [(label, target) for label, target in links if label != target] == []


def test_q2_a_titled_link_is_read_by_the_label_matcher():
    raw = skill_raw().replace("[gnd-model-evolve](../gnd-model-evolve/SKILL.md),",
                              '[gnd-model-evolve](../gnd-export/SKILL.md "the review skill"),', 1)
    assert ("gnd-model-evolve", "gnd-export") in skill_links(raw)


def test_q2_a_refusal_in_a_link_definition_title_is_not_visible():
    raw = skill_raw().replace(ONE_HOME["R-c"], "", 1) + f'\n[unused]: https://example.invalid "{ONE_HOME["R-c"]}"\n'
    assert ONE_HOME["R-c"] not in visible(raw)


@pytest.mark.parametrize("heading, found", [("## Learn ##", True), ("```text\n## Learn\n```", False)])
def test_q2_a_section_heading_is_read_as_markdown_reads_it(heading, found):
    raw = skill_raw().replace("## Learn\n", "## Learned\n", 1) + f"\n{heading}\n\nA fenced or closed heading.\n"
    if found:
        assert section("Learn", raw) == "A fenced or closed heading."
    else:
        with pytest.raises(AssertionError, match="no heading"):
            section("Learn", raw)


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


#: The commands that write a proposal (IS1-Q2, round 2 F4; IS2 spec section 6.9).
PROPOSAL_WRITERS = {("discover",), ("import", "ilp-rules"), ("import", "mined-rules")}


def test_q2_every_proposal_command_carries_the_actor_and_time_once():
    writers = [s for s in _induce_snippets() if s.subcommand_path in PROPOSAL_WRITERS]
    assert {s.subcommand_path for s in writers} == PROPOSAL_WRITERS
    for snippet in writers:
        assert snippet.long_options.count("--actor") == 1, snippet.ident
        assert snippet.long_options.count("--requested-at") == 1, snippet.ident


def test_q2_the_amie_export_is_its_own_line():
    """IS1-Q2, round 2 F5: the miner's export is a line of its own with --target amie."""
    exports = [s for s in _induce_snippets() if s.subcommand_path == ("export", "ilp")]
    amie = [s for s in exports if s.tokens[s.tokens.index("--target") + 1] == "amie"]
    assert len(amie) == 1 and "--population" in amie[0].long_options and "--labels" not in amie[0].long_options


def test_t10_the_skill_installs_nothing():
    assert not INSTALLS.search(visible(skill_raw()))


@pytest.mark.parametrize("line", ["pip3 install popper", "uv tool install x", "brew install swi-prolog",
                                  "python -m pip install popper", "pip3 --isolated install popper",
                                  "python3 -I -m pip install popper", "uv --quiet tool install x"])
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


@pytest.mark.parametrize("seed", ["see /srv/reviewer/runs/april", "under /mnt/data/x", "(/etc/gnd/cfg)",
                                  "in /workspace", "under /Δεδομένα/runs"])
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
                                  "git log -1 --format=%an", "use ${USER} as the actor", "--actor \"${LOGNAME}\""])
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
