"""induction-skill IS2, T9 and T10: the learn-rules tutorial shows gnd-induce prompts and recorded runs.

Spec: .gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md sections 6.4, 6.6 and 15; plan IS2-C4,
IS2-C5 and IS-R7.
"""
import json
import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "docs/tutorials/learn-rules.md"
SESSIONS = ROOT / "src/gnd/examples/refunds/skill-sessions"
REPLAYS = json.loads((ROOT / "docs/assets/replays/replays.json").read_text(encoding="utf-8"))
#: The tutorial's numbered steps and the recorded conversation each one replays (step 6 replays the re-check).
STEPS = {1: "score", 2: "learn", 3: "import", 4: "faulty", 5: "discover", 6: "recheck"}
#: Any fence: three or more backticks or tildes, closed by the same run (review phase-IS2-r1 F11: a
#: four-backtick fence was not read).
FENCE = re.compile(r"^(?P<indent>[ \t]*)(?P<mark>`{3,}|~{3,})[^\n]*\n(?P<body>.*?)^(?P=indent)(?P=mark)[ \t]*$",
                   re.MULTILINE | re.DOTALL)
LEAD = re.compile(r"\*\*You (?:type|answer)\*\*")
SNIPPET = re.compile(r'^\s*--8<-- "[^"]+"\s*$')


def page() -> str:
    return PAGE.read_text(encoding="utf-8")


def flat(text: str) -> str:
    return re.sub(r"\s+", " ", text)


def steps(text: str) -> dict[int, str]:
    found = {}
    for match in re.finditer(r"^## (\d)\. .*?(?=^## |\Z)", text, re.MULTILINE | re.DOTALL):
        found[int(match.group(1))] = match.group(0)
    return found


def lead_fences(text: str) -> list[tuple[str | None, str]]:
    """For every "You type" or "You answer" lead, the body of the first fence after it, as one line of words,
    whatever the fence's length or info string (None when no fence follows before the next lead), and the
    text after that fence up to the next lead."""
    leads = [m.end() for m in LEAD.finditer(text)]
    fences = list(FENCE.finditer(text))
    found = []
    for index, start in enumerate(leads):
        end = leads[index + 1] if index + 1 < len(leads) else len(text)
        fence = next((f for f in fences if start <= f.start() < end), None)
        found.append((None, text[start:end]) if fence is None
                     else (" ".join(fence.group("body").split()), text[fence.end():end]))
    return found


def you_type_fences(text: str) -> list[str | None]:
    return [body for body, _ in lead_fences(text)]


def declared_turns(conversation: str = "*") -> set[str]:
    """The declared user turns of one recorded conversation, or of every one."""
    return {" ".join(turn.split()) for results in SESSIONS.glob(f"{conversation}/claude-*/run-*/results.json")
            for turn in json.loads(results.read_text(encoding="utf-8"))["declared_turns"]}


# --- T10 (IS2-C5): prompts, not commands ------------------------------------------------

def test_t10_every_step_has_a_gnd_prompt():
    found = steps(page())
    assert sorted(found) == sorted(STEPS)
    for number, body in found.items():
        assert re.search(r"^/gnd:gnd-[a-z-]+ ", body, re.MULTILINE), number


def test_t10_the_old_sentences_are_gone():
    text = flat(page())
    assert "There is no skill for this step" not in text
    assert "No prompt on this page is a recording" not in text


def test_t10_every_summary_row_names_a_skill_and_row_6_names_both():
    table = page().split("## What you did", 1)[1].split("\n## ", 1)[0]
    rows = [line for line in table.splitlines() if re.match(r"\|\s*\d\s*\|", line)]
    assert len(rows) == 6
    assert all("gnd-induce" in row or "gnd-model-evolve" in row for row in rows)
    assert "gnd-induce" in rows[5] and "gnd-model-evolve" in rows[5]


def test_t10_step_6_rechecks_through_gnd_induce():
    step = steps(page())[6]
    fences = [" ".join(body.split()) for body in you_type_fences(step)]
    assert any(body.startswith("/gnd:gnd-induce Check batches/market.yaml") for body in fences)


#: A command anywhere in a text, not only at a line's start (a wrapped fence must not hide one).
COMMAND = re.compile(r"(?<![\w/:.-])(?:gnd|python3?|uv|pip) (?=[\w-])")


def test_t10_no_command_in_the_pages_own_fences_or_prose():
    """IS-R7: only a replay's transcript shows the commands the agent ran. A fence holding a recorded turn
    holds the reader's own recorded words, which may name the learner's invocation, as in the recording."""
    text = page()
    turns = declared_turns()
    for match in FENCE.finditer(text):
        lines = [line for line in match.group("body").splitlines() if line.strip()]
        if lines and all(SNIPPET.match(line) for line in lines):
            continue   # a replay transcript, included from its recording
        body = " ".join(" ".join(lines).split())
        if body in turns:
            continue
        assert not COMMAND.search(body), body
    assert prose_commands(text) == []


def prose_commands(text: str) -> list[str]:
    """A command anywhere in the page's prose, in or out of inline code (review phase-IS2-r1 F11), whatever
    its spacing: a run of spaces, a tab or a line break after the program name (issue 318, F13)."""
    return [m.group(0) for m in COMMAND.finditer(" ".join(FENCE.sub("", text).split()))]


def test_t10_a_command_in_prose_is_found():
    assert prose_commands(page() + "\nRun gnd check model.orm.yaml now.\n") == ["gnd "]


@pytest.mark.parametrize("spacing", ["  ", "\t", "\n", " \n  "])
def test_issue_318_f13_a_command_in_prose_is_found_whatever_its_spacing(spacing):
    assert prose_commands(page() + f"\nThen run `gnd{spacing}check model.orm.yaml` again.\n") == ["gnd "]


@pytest.mark.parametrize("body", ["Run it, then\ngnd measure model.orm.yaml", "please run python learner.py now"])
def test_t10_a_command_inside_a_wrapped_fence_is_found(body):
    assert COMMAND.search(" ".join(body.split()))
    assert not COMMAND.search("/gnd:gnd-induce Check batches/market.yaml against the model again.")


def test_t10_the_learner_sentence_stays():
    closing = page().split("## What this does not establish", 1)[1]
    assert "The stand-in is not Popper" in flat(closing)


# --- T9: the prompts are the recorded ones, and every replay is explained ----------------

#: The one visible marker for a step result no IS2 recording holds (plan IS2-C4: a divergence marker).
NOT_RECORDED = "**Not recorded.**"


def unrecorded_prompts(text: str) -> list[str]:
    """Every lead's fence that is not a turn of its own step's recording, except one: step 6's review prompt
    (IS2 records gnd-induce, not gnd-model-evolve), with the marker as the next thing after its fence.
    Review phase-IS2-r1 F11: the exception was honoured in any step. Issue 318 (F13): a step could show
    another step's prompt, and the marker anywhere in step 6 excused every evolve prompt there."""
    wrong, excused = [], 0
    for number, step in steps(text).items():
        turns = declared_turns(STEPS[number])
        for body, after in lead_fences(step):
            if body in turns:
                continue
            if (number == 6 and not excused and body and body.startswith("/gnd:gnd-model-evolve ")
                    and after.lstrip().startswith(NOT_RECORDED)):
                excused += 1
                continue
            wrong.append(f"step {number}: {body}")
    return wrong


def test_t9_every_you_type_fence_is_a_declared_turn():
    assert len(you_type_fences(page())) >= len(STEPS)
    assert unrecorded_prompts(page()) == []


@pytest.mark.parametrize("old, new", [
    ("```text\n/gnd:gnd-induce Score", "````text\n/gnd:gnd-induce Invented. Score"),
    (("```text\n/gnd:gnd-induce Score the written refund rule against the auditors' verdicts in\nlabels.json. "
      "How many flagged weeks does it catch, and does it ever accuse a\nclean week?\n```"),
     "```text\n/gnd:gnd-model-evolve Apply everything now.\n```"),
])
def test_t9_a_fabricated_prompt_is_found_however_it_is_fenced(old, new):
    text = page()
    assert old in text
    mutated = text.replace(old, new, 1)
    if new.startswith("````"):
        mutated = mutated.replace("clean week?\n```", "clean week?\n````", 1)
    assert unrecorded_prompts(mutated) != []


def _swapped(text: str, first: int, second: int) -> str:
    """The page with the first "You type" fence of two steps exchanged."""
    found = steps(text)
    fences = {n: next(FENCE.finditer(found[n].split("**You type**", 1)[1])).group(0) for n in (first, second)}
    mutated = {n: found[n].replace(fences[n], fences[other], 1) for n, other in ((first, second), (second, first))}
    return text.replace(found[first], mutated[first], 1).replace(found[second], mutated[second], 1)


@pytest.mark.parametrize("first, second", [(1, 5), (2, 3), (4, 6)])
def test_issue_318_f13_a_step_showing_another_steps_prompt_is_found(first, second):
    mutated = _swapped(page(), first, second)
    assert mutated != page()
    assert unrecorded_prompts(mutated) != []


def test_issue_318_f13_the_not_recorded_exception_covers_one_marked_prompt():
    text = page()
    evolve = ("```text\n/gnd:gnd-model-evolve Review learned.proposal.json and discovered.json with me.\n"
              "Preview both, explain each rule in plain English, and apply only the ones I accept.\n```\n")
    assert evolve in text
    second = "**You type**\n\n```text\n/gnd:gnd-model-evolve Apply everything now.\n```\n\n"
    assert unrecorded_prompts(text.replace("**Check the market week again**", second
                                           + "**Check the market week again**", 1)) != []
    marked_later = text.replace(evolve + "\n" + NOT_RECORDED, evolve + "\nAn aside.\n\n" + NOT_RECORDED, 1)
    assert marked_later != text and unrecorded_prompts(marked_later) != []


@pytest.mark.parametrize("number", sorted(STEPS))
def test_t9_each_step_shows_its_recording_with_transcript_and_note(number):
    name = f"refunds-{STEPS[number]}-haiku-run-1"
    step = steps(page())[number]
    assert f'--8<-- "docs/assets/replays/{name}.svg"' in step
    after = step.split(f'replays/{name}.txt"', 1)[1]
    assert "**In this run.**" in after, name
    note = flat(after.split("**In this run.**", 1)[1])
    if "refused by Claude Code" in (ROOT / f"docs/assets/replays/{name}.txt").read_text(encoding="utf-8"):
        assert "permission" in note, name   # an environment refusal, said as one


def test_t9_the_learn_replay_shows_the_first_turn_and_says_the_conversation_went_on():
    """Spec section 15: the second turn was the recorder's, not the step's."""
    assert REPLAYS["refunds-learn-haiku-run-1"]["said"] == json.loads(
        (SESSIONS / "learn/claude-haiku/run-1/results.json").read_text(encoding="utf-8"))["declared_turns"][:1]
    note = flat(steps(page())[2].split("**In this run.**", 1)[1])
    assert "second" in note and "turn" in note


def test_t9_each_replays_said_is_a_prefix_of_its_declared_turns():
    for name, entry in REPLAYS.items():
        if name.startswith("refunds-"):
            run = ROOT / Path(entry["sources"][0]).parent
            declared = json.loads((run / "results.json").read_text(encoding="utf-8"))["declared_turns"]
            assert entry["said"] and entry["said"] == declared[:len(entry["said"])], name


def test_review_f9_f10_the_notes_say_what_the_recordings_show():
    """Review phase-IS2-r1: F9, learn's second turn imported the honest claim and GND refused the faulty one;
    F10, make-it-pass has a third reader message, and the redaction header names coordinates, not values."""
    text = flat(page())
    assert "imported both claims" not in text and "refused the faulty one" in text
    assert "A recording has at most two messages" not in text and "Each replay on this page has at most two" in text
    assert "lists any values GND held back" not in text
    third = json.loads((SESSIONS / "make-it-pass/claude-haiku/run-1/results.json").read_text(encoding="utf-8"))
    assert len(third["declared_turns"]) == 3 and "make-it-pass" not in {n.split("-", 1)[1].rsplit("-haiku", 1)[0]
                                                                      for n in REPLAYS if n.startswith("refunds-")}
