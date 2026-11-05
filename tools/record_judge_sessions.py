"""Record Claude Code running a GND judgement skill over the TS3 fixture, every run kept.

One run is a short, scripted conversation over a workspace holding only the model and one type-evidence
file: never the population, never the answer key. The user's turns are declared below, before any run.
The tool refuses to start without --authorized-by naming the approved TS3 spec. It writes, under --out
(a new directory):

    results.json            the run's turns and every check below, each true or false
    manifest.json           SHA-256 of every recorded file and of the sources that made them
    run-1/turn-NN.jsonl     Claude Code's stream-json for each turn (paths redacted, other output dropped)
    run-1/workspace.json    the workspace's file names before the first turn and after the last
    run-1/<judgements>      the judgements file the skill wrote, when it wrote one
    run-1/discover.txt      gnd discover with the judgements over the real population
    run-1/preview.txt       gnd evolve preview --policy additive on its proposal

The checks run outside the agent, after the conversation (spec TS3 section 6.6).
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

import jsonschema
from record_skill_sessions import ROOT, TOOLS, kept_stream, leaks, redact, sha256

FIXTURE = ROOT / "tests/fixtures/type-judgements/round-two"
GND = str(ROOT / ".venv/bin/gnd")
SKILLS = {   # declared before any run; the TS3 spec (D1) authorizes this one
    "judge-fact-types": {
        "option": "--duplicate-judgements",
        "turns": ["/gnd:gnd-judge-fact-types model.orm.yaml evidence.json",
                  "Group g3 is a different attribute from every candidate: distinct. Write the file."],
        "agree": "Yes, as you propose.",
    },
}
CANARIES = ("dim-k4p1", "hue-k4p2", "mass-k4p3", "tint-k4p4")   # the fixture's attribute names
MAX_TURNS = 4
TURN_SECONDS = 900
COMMON = ["--families", "fact-type", "--actor", "recorder", "--requested-at", "2026-11-05T00:00:00+00:00"]


def _environment() -> dict[str, str]:
    environment = {k: v for k, v in os.environ.items()
                   if not k.startswith(("ANTHROPIC_", "OPENROUTER_")) and k != "GND_DISCLOSURE"}
    environment["PATH"] = f"{ROOT / '.venv/bin'}{os.pathsep}{environment.get('PATH', '')}"
    return environment


def build_evidence(directory: Path) -> Path:
    """The evidence the judge reads: unset disclosure, no --show-values, default --min-support (D6)."""
    for name in ("model.orm.yaml", "items.population.json"):
        shutil.copyfile(FIXTURE / name, directory / name)
    subprocess.run([GND, "discover", "model.orm.yaml", "items.population.json", *COMMON, "--type-evidence",
                    "evidence.json", "--out", "first.proposal.json", "--report", "first.report.json"],
                   cwd=directory, env=_environment(), capture_output=True, check=True, timeout=300)
    for name in ("items.population.json", "first.proposal.json", "first.report.json"):   # review F5
        (directory / name).unlink(missing_ok=True)
    return directory / "evidence.json"


def judgements_in(workspace: Path) -> Path | None:
    for path in sorted(workspace.glob("*.json")):
        try:
            if json.loads(path.read_text(encoding="utf-8")).get("format") == "gnd-type-judgements/1":
                return path
        except (ValueError, AttributeError, OSError):
            continue
    return None


def workspace_digests(workspace: Path) -> dict[str, str]:
    """Each workspace file's SHA-256, so an edited input is seen, not only a new name (review F6)."""
    return {p.name: sha256(p.read_bytes()) for p in sorted(workspace.iterdir()) if p.is_file()}


def forbidden_calls(streams: list[str], needles: list[str]) -> list[str]:
    """Tool inputs naming any needle, read from the raw streams before redaction hides paths (review F5)."""
    found = []
    for stream in streams:
        for line in stream.splitlines():
            try:
                event = json.loads(line)
            except ValueError:
                continue
            for part in (event.get("message") or {}).get("content") or [] if isinstance(event, dict) else []:
                if isinstance(part, dict) and part.get("type") == "tool_use":
                    call = json.dumps(part.get("input"), ensure_ascii=False)
                    if any(needle in call for needle in needles):
                        found.append(call)
    return found


def tool_calls(target: Path) -> list[str]:
    """Every tool input the agent sent, as text, from the kept streams."""
    calls = []
    for path in sorted(target.glob("turn-*.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            event = json.loads(line)
            for part in (event.get("message") or {}).get("content") or []:
                if isinstance(part, dict) and part.get("type") == "tool_use":
                    calls.append(json.dumps(part.get("input"), ensure_ascii=False))
    return calls


def check(target: Path, judgements: Path | None, evidence: Path, option: str) -> dict:
    """The checks of spec section 6.6, run in a fresh directory with the real population."""
    key = json.loads((FIXTURE / "answer-key.json").read_text(encoding="utf-8"))["groups"]
    schema = json.loads((ROOT / "src/gnd/type-judgements.schema.json").read_text(encoding="utf-8"))
    result = {"written": judgements is not None, "schema_valid": False, "discover_exit": None,
              "verdicts_match_key": False, "preview_exit": None}
    if judgements is None:
        return result
    document = json.loads(judgements.read_text(encoding="utf-8"))
    try:
        jsonschema.validate(document, schema)
        result["schema_valid"] = True
    except jsonschema.ValidationError:
        return result
    got = {v["group"]: (v["verdict"], v.get("of")) for v in document["verdicts"]}
    result["verdicts_match_key"] = got == {g: (k["verdict"], k.get("of")) for g, k in key.items()}
    with tempfile.TemporaryDirectory(prefix="judge-check-") as directory:
        here = Path(directory).resolve()
        for name in ("model.orm.yaml", "items.population.json"):
            shutil.copyfile(FIXTURE / name, here / name)
        shutil.copyfile(evidence, here / "evidence.json")
        shutil.copyfile(judgements, here / "judgements.json")
        run = subprocess.run([GND, "discover", "model.orm.yaml", "items.population.json", *COMMON,
                              "--type-evidence-in", "evidence.json", option, "judgements.json",
                              "--out", "proposal.json", "--report", "report.json"],
                             cwd=here, env=_environment(), capture_output=True, text=True, timeout=300, check=False)
        result["discover_exit"] = run.returncode
        (target / "discover.txt").write_text(redact(run.stdout + run.stderr, here), encoding="utf-8")
        if run.returncode == 0:
            preview = subprocess.run([GND, "evolve", "preview", "model.orm.yaml", "proposal.json", "--workspace",
                                      ".", "--records", "records", "--out", "preview.json", "--policy", "additive"],
                                     cwd=here, env=_environment(), capture_output=True, text=True, timeout=300,
                                     check=False)
            result["preview_exit"] = preview.returncode
            (target / "preview.txt").write_text(redact(preview.stdout + preview.stderr, here), encoding="utf-8")
    return result


def record_run(skill: str, model: str, out: Path) -> dict:
    plan = SKILLS[skill]
    target = out / "run-1"
    target.mkdir(parents=True)
    session, started, turns = str(uuid.uuid4()), time.monotonic(), []
    with tempfile.TemporaryDirectory(prefix="judge-rec-") as directory, \
            tempfile.TemporaryDirectory(prefix="judge-evidence-") as evidence_directory, \
            tempfile.TemporaryDirectory(prefix="skill-plugin-") as plugin_directory:
        workspace, plugin = Path(directory).resolve(), Path(plugin_directory).resolve()
        evidence = build_evidence(Path(evidence_directory).resolve())
        shutil.copytree(ROOT / ".claude-plugin", plugin / ".claude-plugin")   # the plugin and its skills only
        shutil.copytree(ROOT / "src/gnd/skills", plugin / "src/gnd/skills")
        shutil.copyfile(FIXTURE / "model.orm.yaml", workspace / "model.orm.yaml")
        shutil.copyfile(evidence, workspace / "evidence.json")
        before = workspace_digests(workspace)
        asked, raw = None, []
        for number in range(1, MAX_TURNS + 1):
            said = plan["turns"][number - 1] if number <= len(plan["turns"]) else plan["agree"]
            command = ["claude", "--print", "--plugin-dir", str(plugin), "--permission-mode", "acceptEdits",
                       "--allowedTools", TOOLS, "--output-format", "stream-json", "--verbose", "--strict-mcp-config",
                       "--model", model, *(["--session-id", session] if number == 1 else ["--resume", session])]
            try:
                done = subprocess.run([*command, said], capture_output=True, text=True, timeout=TURN_SECONDS,
                                      cwd=workspace, env=_environment(), check=False)
                stream, code = done.stdout, done.returncode
            except subprocess.TimeoutExpired as error:
                stream = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
                code = None
            raw.append(stream)
            (target / f"turn-{number:02d}.jsonl").write_text(
                kept_stream(redact(stream.replace(str(plugin), "<plugin>"), workspace)), encoding="utf-8")
            result = {}
            for line in stream.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if isinstance(event, dict) and event.get("type") == "result":
                    result = event
            written = judgements_in(workspace)
            turns.append({"user": said, "exit": code, "cost_usd": result.get("total_cost_usd"),
                          "assistant_last": redact((result.get("result") or "")[-600:], workspace),
                          "judgements_after_turn": written is not None})
            if number == 1:
                asked = written is None   # R4: the skill must ask about g3 before writing anything
            if code != 0 or (written is not None and number >= len(plan["turns"])):
                break
        written = judgements_in(workspace)
        after = workspace_digests(workspace)
        (target / "workspace.json").write_text(json.dumps({"before": before, "after": after}, indent=1) + "\n",
                                               encoding="utf-8")
        if written is not None:
            shutil.copyfile(written, target / written.name)
        checks = check(target, written, evidence, plan["option"])
        checks["asked_before_writing"] = asked
        new = sorted(set(after) - set(before))
        checks["only_judgements_new"] = new == ([written.name] if written else []) and all(
            after.get(name) == digest for name, digest in before.items())
        checks["no_apply_call"] = not forbidden_calls(raw, ["evolve apply"])
        checks["no_population_access"] = not forbidden_calls(
            raw, ["population", "answer-key", str(FIXTURE), str(evidence.parent), str(ROOT / "tests")])
        kept = [p.read_text(encoding="utf-8", errors="replace") for p in sorted(target.rglob("*")) if p.is_file()]
        checks["no_canary"] = not any(canary in text for canary in CANARIES for text in kept)
        return {"model": model, "turns": len(turns), "turn_log": turns, "judgements": written.name if written else None,
                "checks": checks, "seconds": round(time.monotonic() - started, 1)}


def passed(checks: dict) -> bool:
    """Every check holds: each exit is 0 and every other check is True (False == 0 must not pass)."""
    return all(value == 0 and value is not False if name.endswith("_exit") else value is True
               for name, value in checks.items())


def finish(out: Path) -> int:
    """The leak search, then the manifest. On a hit the run folder is removed and only results.json stays."""
    found = leaks(out)
    if found:
        shutil.rmtree(out / "run-1", ignore_errors=True)
        print("refusing to keep the recording, and removed the run folder: a local path or key was in "
              + ", ".join(found), file=sys.stderr)
        return 1
    sources = ["tools/record_judge_sessions.py", "src/gnd/skills/gnd-judge-fact-types/SKILL.md",
               *(str((FIXTURE / name).relative_to(ROOT)) for name in ("model.orm.yaml", "items.population.json",
                                                                       "answer-key.json"))]
    manifest = {"files": {str(p.relative_to(out)): sha256(p.read_bytes()) for p in sorted(out.rglob("*"))
                          if p.is_file() and p.name not in ("README.md", "manifest.json")},
                "sources": {s: sha256((ROOT / s).read_bytes()) for s in sources}}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--authorized-by", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--skill", choices=list(SKILLS), default="judge-fact-types")
    args = parser.parse_args()
    gate = args.authorized_by.resolve()
    text = gate.read_text(encoding="utf-8") if gate.is_file() else ""
    if "# Phase TS3 spec" not in text or "approved by the owner `(a3)`" not in text:
        parser.error("--authorized-by must name the approved TS3 spec")
    args.out.mkdir(parents=True)
    row = record_run(args.skill, args.model, args.out)
    (args.out / "results.json").write_text(json.dumps({
        "gate": str(gate.relative_to(ROOT)), "skill": f"gnd-{args.skill}", "fixture": "round-two",
        "user_turns": SKILLS[args.skill]["turns"] + [SKILLS[args.skill]["agree"]],
        "recorded": time.strftime("%Y-%m-%d"), "run": row}, indent=1) + "\n", encoding="utf-8")
    if finish(args.out):
        return 1
    print(json.dumps(row["checks"], indent=1))
    return 0 if passed(row["checks"]) else 1


if __name__ == "__main__":
    raise SystemExit(main())
