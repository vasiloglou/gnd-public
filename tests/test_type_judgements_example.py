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


def recorded_text() -> str:
    """Every assistant text and user turn of the two recordings behind the page, whitespace folded."""
    parts = []
    for recording in ("TS3/recording-2", "TS4/recording"):
        parts += json.loads((EVIDENCE / recording / "results.json").read_text(encoding="utf-8"))["user_turns"]
        for stream in sorted((EVIDENCE / recording / "run-1").glob("turn-*.jsonl")):
            for line in stream.read_text(encoding="utf-8").splitlines():
                event = json.loads(line)
                for part in (event.get("message") or {}).get("content") or []:
                    if isinstance(part, dict) and part.get("type") == "text":
                        parts.append(part["text"])
    return " ".join(" ".join(parts).split())


def quoted_fragments() -> list[str]:
    fragments = []
    for line in PAGE.read_text(encoding="utf-8").splitlines():
        if not line.startswith(">"):
            continue
        body = line.lstrip("> ").removeprefix("- ").strip()
        fragments += [f.strip() for f in body.split("...") if len(f.strip()) > 3]
    return fragments


def test_every_quoted_replay_line_is_in_the_recordings():
    corpus, fragments = recorded_text(), quoted_fragments()
    assert len(fragments) >= 10
    assert [f for f in fragments if " ".join(f.split()) not in corpus] == []


def test_a_paraphrased_quote_is_found():
    assert "The skill decided everything at once." not in recorded_text()
