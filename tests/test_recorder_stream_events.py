"""Issue 318, item 2's sibling readers: every session recorder reads Claude Code's stream-json one line per
newline, so a JSON string holding U+2028 (or another separator str.splitlines() breaks at) keeps its event.
Checked without a paid call."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import record_judge_sessions as judge
import record_skill_sessions as skill

#: Every separator str.splitlines() breaks at that json.dumps(ensure_ascii=False) leaves unescaped (the
#: controls below U+0020 it escapes).
SEPARATORS = [c for c in map(chr, range(0x110000)) if len(f"a{c}b".splitlines()) == 2 and c in json.dumps(c, ensure_ascii=False)]


def test_the_separators_are_the_known_three():
    assert SEPARATORS == ["\x85", "\u2028", "\u2029"]


@pytest.mark.parametrize("separator", SEPARATORS)
def test_the_skill_recorder_keeps_each_turns_cost(tmp_path, monkeypatch, separator):
    class Done:
        returncode = 0
        stdout = json.dumps({"type": "result", "result": f"alpha{separator}beta", "total_cost_usd": 0.24},
                            ensure_ascii=False) + "\n"

    monkeypatch.setattr(skill.subprocess, "run", lambda argv, **k: Done())
    row = skill.record_run("claude-haiku", 1, tmp_path / "out")
    assert row["turns"] == skill.MAX_TURNS   # no model is ever written, so every turn is sent
    assert [turn["cost_usd"] for turn in row["turn_log"]] == [0.24] * skill.MAX_TURNS
    assert all(turn["assistant_last"] == f"alpha{separator}beta" for turn in row["turn_log"])


@pytest.mark.parametrize("separator", SEPARATORS)
def test_the_judge_recorder_sees_a_call_whose_input_holds_a_separator(separator):
    call = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t0", "name": "Bash", "input": {"command": f"echo a{separator}b; gnd evolve apply"}}]}}
    streams = [json.dumps(call, ensure_ascii=False) + "\n"]
    assert judge.forbidden_calls(streams, ["evolve apply"]) != []
    assert judge.outside_calls([streams[0].replace("echo", f"cat {ROOT}/README.md; echo")], []) != []


@pytest.mark.parametrize("separator", SEPARATORS)
def test_the_judge_recorder_lists_the_kept_calls(tmp_path, separator):
    call = {"type": "assistant", "message": {"content": [
        {"type": "tool_use", "id": "t0", "name": "Read", "input": {"file_path": f"notes{separator}one.md"}}]}}
    (tmp_path / "turn-01.jsonl").write_text(skill.kept_stream(json.dumps(call, ensure_ascii=False) + "\n"),
                                            encoding="utf-8")
    assert judge.tool_calls(tmp_path) == [json.dumps({"file_path": f"notes{separator}one.md"}, ensure_ascii=False)]


def test_the_shared_reader_skips_what_is_not_an_object_and_keeps_order():
    text = '{"type": "a"}\n[1, 2]\nnot json\n"text"\n{"type": "result", "n": 1}\r\n\n{"type": "result", "n": 2}'
    assert [e["type"] for e in skill.stream_events(text)] == ["a", "result", "result"]
    assert skill.last_result(text) == {"type": "result", "n": 2}
    assert skill.last_result('{"type": "assistant"}\n') == {}
