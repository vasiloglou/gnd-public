"""TS5: the type-judgements example is the fixtures and the recorded judgements, byte for byte (spec section 5.2)."""

import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/type_judgements"
EVIDENCE = ROOT / ".gnd-planning/milestones/type-induction-skills/evidence"
SOURCES = {
    "duplicates/model.orm.yaml": ROOT / "tests/fixtures/type-judgements/round-two/model.orm.yaml",
    "duplicates/items.population.json": ROOT / "tests/fixtures/type-judgements/round-two/items.population.json",
    "duplicates/duplicates.judgements.json": EVIDENCE / "TS3/recording-2/run-1/duplicates.judgements.json",
    "multi-valued/model.orm.yaml": ROOT / "tests/fixtures/type-judgements/multi-valued/model.orm.yaml",
    "multi-valued/items.population.json": ROOT / "tests/fixtures/type-judgements/multi-valued/items.population.json",
    "multi-valued/shapes.judgements.json": EVIDENCE / "TS4/recording/run-1/shapes.judgements.json",
}


@pytest.mark.parametrize("name", sorted(SOURCES))
def test_each_example_file_is_its_source(name):
    assert (EXAMPLE / name).read_bytes() == SOURCES[name].read_bytes()


def test_the_example_holds_nothing_else():
    files = {p.relative_to(EXAMPLE).as_posix() for p in EXAMPLE.rglob("*") if p.is_file()}
    assert files == {*SOURCES, "README.md"}


@pytest.mark.parametrize("recording", ["TS3/recording-2", "TS4/recording"])
def test_the_recorded_runs_behind_the_example_wrote_their_file_after_asking(recording):
    run = json.loads((EVIDENCE / recording / "results.json").read_text(encoding="utf-8"))["run"]
    assert run["checks"]["asked_before_writing"] is True and run["checks"]["verdicts_match_key"] is True


PAGE = ROOT / "docs/how-to/judge-induced-fact-types.md"
SECTIONS = (("## Judge the duplicates", "TS3/recording-2"), ("## The multi-valued round", "TS4/recording"))
ELISION = " ... "


def fold(text: str) -> str:
    return " ".join(text.split())


def recording(name: str) -> tuple[list[str], str]:
    """A recording's user turns and its assistant text, whitespace folded."""
    turns = json.loads((EVIDENCE / name / "results.json").read_text(encoding="utf-8"))["user_turns"]
    parts = []
    for stream in sorted((EVIDENCE / name / "run-1").glob("turn-*.jsonl")):
        for line in stream.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            for part in (event.get("message") or {}).get("content") or []:
                if isinstance(part, dict) and part.get("type") == "text":
                    parts.append(part["text"])
    return turns, fold(" ".join(parts))


def sections(page: str) -> list[tuple[str, str]]:
    """Each replay section's text with the recording it quotes, cut at the next section."""
    starts = [page.index(heading) for heading, _ in SECTIONS] + [len(page)]
    return [(page[starts[i] : starts[i + 1]], name) for i, (_, name) in enumerate(SECTIONS)]


def typed_turns(section: str) -> list[str]:
    """The text block that follows each **You type.** or **You answer.** paragraph."""
    turns, lines, pending = [], section.splitlines(), False
    for n, line in enumerate(lines):
        if "**You type.**" in line or "**You answer.**" in line:
            pending = True
        elif pending and line.strip() == "```text":
            end = lines.index("```", n + 1)
            turns.append("\n".join(lines[n + 1 : end]))
            pending = False
    return turns


def quotes(section: str) -> list[str]:
    """Each quoted line, indented or not, with its list markers removed."""
    out = []
    for line in section.splitlines():
        body = line.strip()
        if body.startswith(">"):
            body = body.lstrip("> ").removeprefix("- ").strip()
            if body:
                out.append(body)
    return out


def replay_defects(page: str) -> list[str]:
    """Every typed turn or quoted line of the page that its own recording does not hold, in order."""
    defects = []
    for section, name in sections(page):
        turns, corpus = recording(name)
        typed = typed_turns(section)
        if typed != turns[: len(typed)] or len(typed) < 2:
            defects.append(f"{name}: typed turns {typed!r}")
        at = 0
        for line in quotes(section):
            for fragment in fold(line).split(ELISION.strip()):
                fragment = fragment.strip()
                found = corpus.find(fragment, at)
                if not fragment or found < 0:
                    defects.append(f"{name}: {line!r}")
                    break
                at = found + len(fragment)
    return defects


def test_every_typed_turn_and_quote_is_in_its_own_recording_in_order():
    page = PAGE.read_text(encoding="utf-8")
    assert sum(len(quotes(section)) for section, _ in sections(page)) >= 10
    assert replay_defects(page) == []


@pytest.mark.parametrize(
    "change",
    [
        ("distinct. Write the file.", "distinct. Write it."),
        ("Only g2 is rendered", "Only g3 is rendered"),
        ("> - **g3 (S4,", "  > - **g3 (S5,"),
        ("the other 23 have one. ... Is", "the other 23 have one. ... Only g2 is rendered ... Is"),
    ],
    ids=["typed-turn", "quote", "indented-quote", "inserted-fragment"],
)
def test_a_changed_replay_is_caught(change):
    page = PAGE.read_text(encoding="utf-8")
    assert change[0] in page
    assert replay_defects(page.replace(change[0], change[1], 1)) != []


def test_a_quote_from_the_other_recording_is_caught():
    page = PAGE.read_text(encoding="utf-8")
    ts3 = next(line for line in page.splitlines() if line.startswith("> I haven't written a judgements file."))
    ts4 = next(line for line in page.splitlines() if line.startswith("> Only g2 is rendered as a proposal"))
    moved = page.replace(ts3, ts4, 1)
    assert replay_defects(moved) != []
