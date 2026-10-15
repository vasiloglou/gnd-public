"""Record Claude Code running a GND skill on an example's rules, every run kept.

One run is a short, scripted conversation: the user's turns are declared below, before any run, and
the assistant's turns are recorded as Claude Code stream-json. The tool refuses to start without
--authorized-by naming the owner's gate record. It writes, under --out (a new directory):

    results.json          one row per run: turns taken, whether a model was written, gnd validate's exit
    manifest.json         SHA-256 of every recorded file and of the sources that made them
    <model>/run-N/turn-NN.jsonl     Claude Code's stream-json for each turn (paths redacted)
    <model>/run-N/model.orm.yaml    the model the skill wrote, when it wrote one
    <model>/run-N/validate.txt      gnd validate on it
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
import uuid
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "src/gnd/examples/plan_apps/course"
MODELS = {"claude-haiku": "haiku", "claude-default": None}
TURNS = [
    "/gnd:gnd-model-from-text rules.md",
    "MVP-fast. The rules file is complete: model what it states, including what the registrar does, "
    "and ask me only about what it leaves open.",
]
AGREE = "Yes, as you propose."
MAX_TURNS = 6
TURN_SECONDS = 900
TOOLS = f"Bash(gnd *),Bash({ROOT / '.venv/bin/gnd'} *),Read,Write,Edit,Glob,Grep"  # `which gnd` gives the absolute path
TEMPORARY = re.compile(r"(?:/private)?/var/folders/[^\s\"'\\]+|/private/tmp/claude-\d+/[^\s\"'\\]+"
                       r"|-private-var-folders-[A-Za-z0-9_-]+|/private/tmp\b")   # also Claude Code's mangled names
LOCAL = ("/Users/", "/private/", "/home/", "/var/folders/")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def redact(text: str, workspace: Path) -> str:
    for old, new in ((str(workspace.resolve()), "<workspace>"), (str(workspace), "<workspace>"),
                     (str(ROOT), "<repo>"), (str(Path.home()), "<home>")):
        text = text.replace(old, new)
    return TEMPORARY.sub("<tmp>", text)


def kept_stream(stream: str, workspace_marker: str = "<workspace>") -> str:
    """The transcript as kept: every event, but tool output only where the replay needs it (gnd commands, and
    reads and writes of files in the workspace). Other tool output is replaced by its size, so nothing the agent
    happened to list or read elsewhere on the machine is kept. Claude Code's start event keeps no paths."""
    wanted, lines = set(), []
    for raw in stream.splitlines():
        try:
            event = json.loads(raw)
        except ValueError:
            continue
        if event.get("type") == "system":
            event = {k: event.get(k) for k in ("type", "subtype", "model", "permissionMode") if k in event}
        elif event.get("type") == "assistant":
            message = event.get("message", {})
            event = {"type": "assistant", "message": {"model": message.get("model"), "content": message.get("content", [])}}
            for part in event["message"]["content"]:
                part.pop("signature", None)   # opaque bytes; the reasoning text stays
                if part.get("type") == "tool_use":
                    target = str(part["input"].get("command") or part["input"].get("file_path") or "")
                    first = target.split()[0] if target.split() else ""
                    plain = not any(mark in target for mark in (";", "&&", "||", "|", "$(", "`"))
                    if (first.endswith("gnd") and plain and part["name"] == "Bash") or target.startswith(workspace_marker) or (
                            part["name"] in ("Write", "Edit") and "/" not in target.replace(workspace_marker, "")):
                        wanted.add(part["id"])
        elif event.get("type") in ("rate_limit_event",):
            continue
        elif event.get("type") == "user":
            event = {"type": "user", "message": {"content": event.get("message", {}).get("content")}}
            content = event["message"]["content"]
            if isinstance(content, list):
                for part in content:
                    if part.get("type") == "tool_result" and part.get("tool_use_id") not in wanted:
                        size = len(json.dumps(part.get("content")))
                        part["content"] = f"[{size} bytes of output not kept]"
            event.pop("tool_use_result", None)
        lines.append(json.dumps(event, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def model_file(workspace: Path) -> Path | None:
    found = sorted(p for p in workspace.rglob("model.orm.*") if p.suffix in (".yaml", ".yml", ".json"))
    return found[0] if found else None


def record_run(name: str, run: int, out: Path) -> dict:
    target = out / name / f"run-{run}"
    target.mkdir(parents=True)
    session, started, turns = str(uuid.uuid4()), time.monotonic(), []
    environment = {k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENROUTER_"))}
    environment["PATH"] = f"{ROOT / '.venv/bin'}{os.pathsep}{environment.get('PATH', '')}"
    with tempfile.TemporaryDirectory(prefix="skill-rec-") as directory:
        workspace = Path(directory).resolve()   # gnd validate refuses a model with references through a symlink
        shutil.copyfile(EXAMPLE / "rules.md", workspace / "rules.md")
        for number in range(1, MAX_TURNS + 1):
            said = TURNS[number - 1] if number <= len(TURNS) else AGREE
            command = ["claude", "--print", "--plugin-dir", str(ROOT), "--permission-mode", "acceptEdits",
                       "--allowedTools", TOOLS, "--output-format", "stream-json", "--verbose", "--strict-mcp-config"]
            if MODELS[name]:
                command += ["--model", MODELS[name]]
            command += ["--session-id", session] if number == 1 else ["--resume", session]
            try:
                done = subprocess.run([*command, said], capture_output=True, text=True, timeout=TURN_SECONDS,
                                      cwd=workspace, env=environment, check=False)
                stream, code = done.stdout, done.returncode
            except subprocess.TimeoutExpired as error:
                stream, code = (error.stdout or b"").decode() if isinstance(error.stdout, bytes) else (error.stdout or ""), None
            (target / f"turn-{number:02d}.jsonl").write_text(kept_stream(redact(stream, workspace)), encoding="utf-8")
            result = {}
            for line in stream.splitlines():
                try:
                    event = json.loads(line)
                except ValueError:
                    continue
                if isinstance(event, dict) and event.get("type") == "result":
                    result = event
            turns.append({"user": said, "exit": code, "cost_usd": result.get("total_cost_usd"),
                          "assistant_last": redact((result.get("result") or "")[-600:], workspace)})
            written = model_file(workspace)
            valid = written is not None and subprocess.run(
                [str(ROOT / ".venv/bin/gnd"), "validate", str(written)], capture_output=True, timeout=300,
                check=False).returncode == 0
            turns[-1]["model_valid_after_turn"] = valid
            if code != 0 or valid:   # the user stops answering once the model validates
                break
        written = model_file(workspace)
        row = {"model": name, "run": run, "turns": len(turns), "turn_log": turns,
               "model_written": written.name if written else None, "validate_exit": None,
               "seconds": round(time.monotonic() - started, 1)}
        if written:
            shutil.copyfile(written, target / written.name)
            check = subprocess.run([str(ROOT / ".venv/bin/gnd"), "validate", str(written)], capture_output=True,
                                   text=True, timeout=300, check=False)
            row["validate_exit"] = check.returncode
            (target / "validate.txt").write_text(redact(check.stdout + check.stderr, workspace), encoding="utf-8")
    return row


def leaks(out: Path) -> list[str]:
    home = Path.home()
    machine = Path(tempfile.gettempdir()).resolve().parts   # e.g. /private/var/folders/nb/<id>/T
    needles = [*LOCAL, str(home), home.name, "sk-ant-", "sk-or-", *[p for p in machine if len(p) > 12]]
    return [str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()
            and any(n in p.read_text(encoding="utf-8", errors="replace") for n in needles)]


def finish(out: Path, finished_later: bool = False) -> int:
    """The leak search, then the manifest. On a hit the run folders are removed and only results.json stays."""
    found = leaks(out)
    if found:
        for folder in sorted({out / Path(f).parts[0] for f in found if len(Path(f).parts) > 1}):
            shutil.rmtree(folder, ignore_errors=True)
        print("refusing to keep the recording, and removed the run folders: a local path or key was in "
              + ", ".join(found), file=sys.stderr)
        return 1
    sources = ["tools/record_skill_sessions.py", "src/gnd/examples/plan_apps/course/rules.md",
               "src/gnd/skills/gnd-model-from-text/SKILL.md"]
    manifest = {"files": {str(p.relative_to(out)): sha256(p.read_bytes()) for p in sorted(out.rglob("*"))
                          if p.is_file() and p.name not in ("README.md", "manifest.json")},
                "sources": {s: sha256((ROOT / s).read_bytes()) for s in sources}}
    if finished_later:
        manifest["finished_later"] = {"date": time.strftime("%Y-%m-%d"), "why": "the keep filter for tool output "
                                      "and Claude Code's start event was added after this recording"}
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--authorized-by", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--models", nargs="+", default=list(MODELS), choices=list(MODELS))
    parser.add_argument("--runs", type=int, default=2)
    parser.add_argument("--finish", action="store_true",
                        help="apply the keep filter and redactions to the recording in --out, then the leak search "
                             "and the manifest (for a recording made before the filter existed)")
    args = parser.parse_args()
    if args.finish:
        for path in sorted(args.out.rglob("turn-*.jsonl")):
            path.write_text(kept_stream(TEMPORARY.sub("<tmp>", path.read_text(encoding="utf-8"))), encoding="utf-8")
        for path in sorted(args.out.rglob("validate.txt")):
            path.write_text(TEMPORARY.sub("<tmp>", path.read_text(encoding="utf-8")), encoding="utf-8")
        return finish(args.out, finished_later=True)
    gate = args.authorized_by.resolve()
    if not gate.is_file() or "phase-PL18-skill-recording" not in gate.read_text(encoding="utf-8"):
        parser.error("--authorized-by must name the PL18 skill-recording gate record")
    if not 1 <= args.runs <= 2:
        parser.error("--runs must be 1 or 2 (the gate's bound)")
    args.out.mkdir(parents=True)
    rows = [record_run(name, run, args.out) for name in args.models for run in range(1, args.runs + 1)]
    (args.out / "results.json").write_text(json.dumps({
        "gate": str(gate.relative_to(ROOT)), "skill": "gnd-model-from-text", "example": "course",
        "user_turns": TURNS + [AGREE], "recorded": time.strftime("%Y-%m-%d"), "runs": rows}, indent=1) + "\n",
        encoding="utf-8")
    if finish(args.out):
        return 1
    for row in json.loads((args.out / "results.json").read_text(encoding="utf-8"))["runs"]:
        print(f"{row['model']:15} run {row['run']}  turns {row['turns']}  model {row['model_written']}  "
              f"validate {row['validate_exit']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
