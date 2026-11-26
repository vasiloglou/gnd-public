"""induction-skill IS2, T1 to T6: the gnd-induce recorder, checked without a paid call.

Spec: .gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md sections 6.1 to 6.3 and 8.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import record_induce_sessions as recorder
from record_skill_sessions import kept_stream


def stream(*parts) -> str:
    """A stream-json transcript: one assistant event with the given tool calls, then their results."""
    calls = [{"type": "tool_use", "id": f"t{i}", "name": name, "input": arguments}
             for i, (name, arguments, _) in enumerate(parts)]
    results = [{"type": "tool_result", "tool_use_id": f"t{i}", "content": output}
               for i, (_, _, output) in enumerate(parts)]
    return "\n".join([json.dumps({"type": "assistant", "message": {"content": calls}}),
                      json.dumps({"type": "user", "message": {"content": results}})]) + "\n"


# --- T1: kept_stream keeps the learner's output and gnd's ---------------------------

def test_t1_kept_stream_keeps_a_learner_call_and_a_gnd_call():
    raw = stream(("Bash", {"command": "python stand_in_learner.py ilp learned"}, "searched 40 rules"),
                 ("Bash", {"command": "gnd export ilp model.orm.yaml --labels labels.json --target neutral --out ilp"},
                  "EXPORTED 8 examples"),
                 ("Bash", {"command": "ls -la"}, "secret listing"))
    kept = kept_stream(raw, keep=recorder.LEARNER_FORMS)
    assert "searched 40 rules" in kept and "EXPORTED 8 examples" in kept
    assert "secret listing" not in kept


def test_t1_the_python3_isolated_form_is_kept_and_allowed():
    raw = stream(("Bash", {"command": "python3 -I stand_in_learner.py ilp learned"}, "searched 40 rules"))
    assert "searched 40 rules" in kept_stream(raw, keep=recorder.LEARNER_FORMS)
    assert "Bash(python3 -I stand_in_learner.py *)" in recorder.TOOLS


def test_t4_read_only_commands_are_not_refused(tmp_path):
    result = _checks("score", tmp_path, ("Bash", {"command": "ls -la && cat labels.json"}, ""))
    assert result["no_forbidden_bash"] is True


def test_t1_without_the_keep_rule_the_learner_output_is_dropped():
    raw = stream(("Bash", {"command": "python stand_in_learner.py ilp learned"}, "searched 40 rules"))
    assert "searched 40 rules" not in kept_stream(raw)


# --- T2: no gate record, no run ------------------------------------------------------

def test_t2_the_recorder_refuses_a_missing_or_wrong_gate(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(recorder, "record", lambda *a, **k: pytest.fail("recorded without a gate"))
    for gate in (tmp_path / "absent-IS2-recording-gate.md", tmp_path / "003-IS2-recording-gate.md"):
        if gate.name.startswith("003"):
            gate.write_text("scope: something-else\n", encoding="utf-8")
        with pytest.raises(SystemExit) as stop:
            recorder.main(["--authorized-by", str(gate), "--conversation", "score"])
        assert stop.value.code == 2


def test_t2_a_well_formed_gate_is_accepted(tmp_path):
    gate = tmp_path / "003-IS2-recording-gate.md"
    gate.write_text(f"---\n{recorder.GATE_SCOPE}\n---\n# {recorder.GATE_NAME} recording gate\n", encoding="utf-8")
    assert recorder.gate_ok(gate)


# --- T3: the declared conversations --------------------------------------------------

def test_t3_each_tutorial_conversation_opens_with_its_c0_prompt():
    for conversation in ("score", "learn", "import", "faulty", "discover", "recheck"):
        assert recorder.CONVERSATIONS[conversation]["turns"][0] == recorder.C0[conversation]
    assert all(prompt.startswith("/gnd:gnd-induce ") for prompt in recorder.C0.values())


def test_t3_seeds_name_known_steps_and_every_conversation_has_a_check():
    for conversation, plan in recorder.CONVERSATIONS.items():
        assert set(plan["seed"]) <= set(recorder.SEED_STEPS), conversation
        assert 1 <= len(plan["turns"]) <= recorder.MAX_TURNS
    assert len(recorder.CONVERSATIONS) == 9


def test_t3_the_seed_steps_run_on_the_example(tmp_path):
    import shutil
    workspace = tmp_path / "w"
    shutil.copytree(recorder.EXAMPLE, workspace,
                    ignore=shutil.ignore_patterns("__pycache__", "learners", "skill-sessions"))
    log = recorder.seed(workspace, ["export", "learner", "import", "preview", "apply"])
    assert [row["exit"] for row in log] == [0, 0, 0, 0, 0]
    assert (workspace / "learned.proposal.json").is_file()


# --- T4: each check can fail -----------------------------------------------------------

def _checks(conversation, tmp_path, *parts):
    return recorder.checks(conversation, tmp_path, {}, [stream(*parts)])


@pytest.mark.parametrize(("part", "check"), [
    (("Bash", {"command": "gnd evolve apply model.orm.yaml p.json --preview v.json"}, ""), "no_apply_call"),
    (("Write", {"file_path": "learned/learned.run.json", "content": "{}"}, ""), "no_edit_of_learner_artifacts"),
    (("Bash", {"command": "gnd discover m p --actor operator --out x"}, ""), "actor_from_user"),
    (("Bash", {"command": "pip install popper"}, ""), "no_forbidden_bash"),
    (("Bash", {"command": "git config user.name"}, ""), "no_forbidden_bash"),
    (("Read", {"file_path": "/etc/passwd"}, ""), "no_outside_path"),
])
def test_t4_each_check_turns_false_on_its_violation(tmp_path, part, check):
    assert _checks("score", tmp_path, part)[check] is False


def test_t4_a_clean_conversation_passes_its_general_checks(tmp_path):
    result = _checks("score", tmp_path, ("Bash", {"command": f"gnd measure model.orm.yaml --labels labels.json "
                                                             f"--out measure.json --actor {recorder.ACTOR}"}, ""))
    assert all(result[name] for name in result if name != "done")


def test_t4_the_absent_learner_stop_needs_the_named_sentence(tmp_path):
    named = json.dumps({"type": "result", "result": "Stopping: no learner named popper is installed."})
    silent = json.dumps({"type": "result", "result": "I could not find it."})
    assert recorder.checks("absent-learner", tmp_path, {}, [named])["done"] is True
    assert recorder.checks("absent-learner", tmp_path, {}, [silent])["done"] is False


# --- T5: the leak gate -----------------------------------------------------------------

def test_t5_a_recording_with_a_local_path_is_not_kept(tmp_path, monkeypatch):
    target = tmp_path / "run-1"
    target.mkdir()
    (target / "results.json").write_text("{}", encoding="utf-8")
    (target / "turn-01.jsonl").write_text('{"x": "/Users/someone/work"}\n', encoding="utf-8")
    monkeypatch.setattr(recorder, "ROOT", ROOT)
    assert recorder.finish(target, "0" * 40) == 1
    assert sorted(p.name for p in target.iterdir()) == ["results.json"]


# --- T6: the cost ceiling ----------------------------------------------------------------

def test_t6_spent_sums_the_reported_costs(tmp_path):
    for conversation, costs in (("a", [0.5, 1.0]), ("b", [None, 2.25])):
        run = tmp_path / conversation / "claude-haiku" / "run-1"
        run.mkdir(parents=True)
        (run / "results.json").write_text(json.dumps({"turns": [{"cost_usd": c} for c in costs]}), encoding="utf-8")
    assert recorder.spent(tmp_path) == pytest.approx(3.75)


def test_t6_the_recorder_refuses_at_the_ceiling(tmp_path, monkeypatch, capsys):
    """IS2 finding F2: an earlier version read HOME at import, passed the ceiling and launched a real run."""
    monkeypatch.setattr(recorder.subprocess, "run", lambda *a, **k: pytest.fail("a subprocess was started"))
    run = tmp_path / "x" / "claude-haiku" / "run-1"
    run.mkdir(parents=True)
    (run / "results.json").write_text(json.dumps({"turns": [{"cost_usd": recorder.CEILING_USD}]}), encoding="utf-8")
    monkeypatch.setattr(recorder, "HOME", tmp_path)
    assert recorder.record("score", "haiku", tmp_path / "gate.md", "0" * 40) == 2
    assert "ceiling" in capsys.readouterr().err
    assert not (tmp_path / "score").exists()


# --- IS2 finding F4: the check bugs the first recordings exposed -------------------------

@pytest.mark.parametrize("command", ["ls -la && find . -maxdepth 3 -not -path '*/.git*' | head",
                                     "gnd export ilp model.orm.yaml --labels labels.json --target popper --out x",
                                     "which popper ilasp", "S=out && mkdir -p $S && gnd discover m p --out $S/a",
                                     'ls bin | grep -i -E "popper|ilasp|amie"'])
def test_f4_arguments_that_mention_a_program_are_not_forbidden(tmp_path, command):
    assert _checks("score", tmp_path, ("Bash", {"command": command}, ""))["no_forbidden_bash"] is True


@pytest.mark.parametrize("command", ["cd x && git status", "python -m pip install popper", "uv add popper",
                                     "S=1 curl https://example.com"])
def test_f4_running_a_forbidden_program_is_caught(tmp_path, command):
    assert _checks("score", tmp_path, ("Bash", {"command": command}, ""))["no_forbidden_bash"] is False


def test_f4_a_redacted_temporary_path_counts_as_outside(tmp_path):
    assert _checks("score", tmp_path, ("Write", {"file_path": "<tmp>", "content": "x"}, ""))["no_outside_path"] is False
    assert _checks("score", tmp_path, ("Bash", {"command": "gnd measure m --out <tmp>"}, ""))["no_outside_path"] is False


@pytest.mark.parametrize("command", ["ls <repo>/.venv/bin", "<repo>/.venv/bin/gnd export ilp --help",
                                     "cat <home>/notes.txt"])
def test_f8_a_command_naming_the_repository_or_home_is_outside(tmp_path, command):
    """IS2 finding F8: only <tmp> was looked for in commands, so a run that listed the repository passed."""
    assert _checks("score", tmp_path, ("Bash", {"command": command}, ""))["no_outside_path"] is False


def test_f4_a_hand_written_proposal_is_caught(tmp_path):
    part = ("Write", {"file_path": "<workspace>/south-refund-rules.proposal.json", "content": "{}"}, "")
    assert _checks("discover", tmp_path, part)["no_hand_written_proposal"] is False


def test_f4_done_follows_the_import_out_path_not_a_file_name(tmp_path):
    part = ("Bash", {"command": "gnd import ilp-rules m.yaml c.json --labels l.json --reported-coverage r.json "
                                "--target neutral --out induce/proposal.json --actor reader"}, "")
    result = recorder.checks("import", tmp_path, {}, [stream(part)], after={"induce/proposal.json": "x"})
    assert result["done"] is True
    assert recorder.checks("import", tmp_path, {}, [stream(part)], after={})["done"] is False


def test_f6_reading_a_skill_reference_is_not_outside(tmp_path, monkeypatch):
    """IS2 finding F6: the live checks read the raw stream, where the plugin is an absolute temporary path."""
    class Done:
        returncode = 0
        stdout = ""

    def fake_run(argv, **kwargs):
        if argv and argv[0] == "claude":
            plugin = argv[argv.index("--plugin-dir") + 1]
            reference = f"{plugin}/src/gnd/skills/gnd-orm-core/references/labels.schema.json"
            Done.stdout = stream(("Read", {"file_path": reference}, "{}")) + json.dumps(
                {"type": "result", "result": "ok", "total_cost_usd": 0.0}) + "\n"
        return Done()

    monkeypatch.setattr(recorder, "HOME", tmp_path / "home")
    monkeypatch.setattr(recorder.subprocess, "run", fake_run)
    monkeypatch.setattr(recorder, "finish", lambda target, commit: 0)
    gate = recorder.ROOT / ".gnd-planning/milestones/induction-skill/003-IS2-recording-gate.md"
    recorder.record("score", "haiku", gate, "0" * 40)
    results = json.loads((tmp_path / "home/score/claude-haiku/run-1/results.json").read_text(encoding="utf-8"))
    assert results["checks"]["no_outside_path"] is True


def test_f7_spent_counts_the_earlier_attempts_and_f2(tmp_path, monkeypatch):
    """IS2 finding F7: after attempt-1 moved to evidence, the ceiling would have restarted at zero."""
    monkeypatch.setattr(recorder, "HOME", tmp_path / "home")
    earlier = sum(recorder.spent(folder) for folder in recorder.EARLIER)
    assert earlier > 1.4   # attempt-1: USD 1.446
    assert recorder.spent() == pytest.approx(earlier + recorder.UNRECORDED_USD)
    assert recorder.UNRECORDED_USD == pytest.approx(0.084)


def test_f3_redaction_runs_before_truncation():
    source = __import__("inspect").getsource(recorder.record)
    assert 'redact(result.get("result") or "", workspace)[-600:]' in source


def test_f4_the_recorder_sends_only_the_declared_turns(tmp_path, monkeypatch):
    sent = []

    class Done:
        returncode, stdout = 0, json.dumps({"type": "result", "result": "ok", "total_cost_usd": 0.0}) + "\n"

    def fake_run(argv, **kwargs):
        if argv and argv[0] == "claude":
            sent.append(argv[-1])
        return Done()

    monkeypatch.setattr(recorder, "HOME", tmp_path / "home")
    monkeypatch.setattr(recorder.subprocess, "run", fake_run)
    monkeypatch.setattr(recorder, "finish", lambda target, commit: 0)
    gate = recorder.ROOT / ".gnd-planning/milestones/induction-skill/003-IS2-recording-gate.md"
    assert recorder.record("score", "haiku", gate, "0" * 40) == 0
    assert sent == recorder.CONVERSATIONS["score"]["turns"]
