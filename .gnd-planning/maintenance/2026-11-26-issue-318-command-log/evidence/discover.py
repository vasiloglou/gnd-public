"""Issue 318 discovery run: what Claude Code's Bash hooks receive, and where the exit code is.

One scripted conversation of two turns with Claude Code's Haiku, in a throwaway folder, with PreToolUse,
PostToolUse and PostToolUseFailure hooks on Bash that log their whole input (hook.py). The gate record
001-discovery-gate.md beside this folder authorizes it. Run from the repository root:

    uv run python .gnd-planning/maintenance/2026-11-26-issue-318-command-log/evidence/discover.py \
        --authorized-by .gnd-planning/maintenance/2026-11-26-issue-318-command-log/001-discovery-gate.md --out DIR

DIR must be new and outside the repository: the raw stream and hook log hold host paths and stay there.
Only schema.json, the key layout with host values removed, is written for keeping.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT / "tools"))
from record_skill_sessions import last_result, leak_needles, redact, stream_events  # noqa: E402

GATE = HERE.parent / "001-discovery-gate.md"
CEILING_USD = 3.00
TURN_BUDGET_USD = 1.40
TURN_SECONDS = 300
TURNS = [
    ("Use the Bash tool to run each of these commands as its own separate call, exactly as written, one at a "
     "time, and then tell me each one's exit status: `true`, then `false`, then `sh -c 'exit 3'`, then "
     "`true && false`, then `date`. If a command is refused, do not retry it in another form."),
    "Run `sh -c 'exit 5'` once more with the Bash tool and tell me its exit status.",
]
ALLOWED = "Bash(true),Bash(false),Bash(sh -c *)"
#: The fields whose values are kept in schema.json (no path, id or host value is among them).
KEPT_VALUES = {"hook_event_name", "tool_name", "permission_mode", "tool_input.command", "tool_input.description",
               "error", "is_interrupt", "tool_response.interrupted", "tool_response.isImage",
               "tool_response.stdout", "tool_response.stderr", "tool_response.returnCodeInterpretation",
               "tool_response.noOutputExpected", "tool_response.exitCode", "tool_response.exit_code",
               "tool_response.code"}


def shape(value, prefix: str = "") -> dict:
    """Every key path of a JSON value with its type, and its value where KEPT_VALUES names it."""
    out = {}
    if isinstance(value, dict):
        for key, item in value.items():
            out.update(shape(item, f"{prefix}{key}" if not prefix else f"{prefix}.{key}"))
        return out
    entry = {"type": type(value).__name__}
    if prefix in KEPT_VALUES or prefix.startswith("tool_response.") and isinstance(value, (bool, int, float)):
        entry["value"] = value
    return {prefix: entry}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--authorized-by", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    if args.authorized_by.resolve() != GATE:
        parser.error("--authorized-by must name 001-discovery-gate.md")
    tracked = subprocess.run(["git", "ls-files", "--error-unmatch", str(GATE.relative_to(ROOT))], cwd=ROOT,
                             capture_output=True, check=False).returncode == 0
    unchanged = subprocess.run(["git", "diff", "--quiet", "HEAD", "--", str(GATE.relative_to(ROOT))], cwd=ROOT,
                               capture_output=True, check=False).returncode == 0
    if not (tracked and unchanged):
        parser.error("the gate record must be committed and unchanged")
    out = args.out.resolve()
    if out.exists() or out.is_relative_to(ROOT.resolve()):
        parser.error("--out must be a new folder outside the repository")
    out.mkdir(parents=True)
    log = out / "hooks.jsonl"
    hook = f"python3 -I {HERE / 'hook.py'} {log}"
    entry = [{"matcher": "Bash", "hooks": [{"type": "command", "command": hook}]}]
    settings = out / "settings.json"
    settings.write_text(json.dumps({"hooks": {name: entry for name in
                                              ("PreToolUse", "PostToolUse", "PostToolUseFailure")}}, indent=1),
                        encoding="utf-8")
    environment = {k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENROUTER_"))}
    session, spent, turns = str(uuid.uuid4()), 0.0, []
    with tempfile.TemporaryDirectory(prefix="hook-discovery-") as directory:
        workspace = Path(directory).resolve()
        for number, said in enumerate(TURNS, 1):
            if spent + TURN_BUDGET_USD > CEILING_USD:
                print(f"stopping before turn {number}: USD {spent:.3f} spent of {CEILING_USD}", file=sys.stderr)
                break
            command = ["claude", "--print", "--model", "haiku", "--output-format", "stream-json", "--verbose",
                       "--strict-mcp-config", "--setting-sources", "project", "--settings", str(settings),
                       "--permission-mode", "default", "--allowedTools", ALLOWED,
                       "--max-budget-usd", str(TURN_BUDGET_USD),
                       *(["--session-id", session] if number == 1 else ["--resume", session]), said]
            try:
                done = subprocess.run(command, capture_output=True, text=True, timeout=TURN_SECONDS, cwd=workspace,
                                      env=environment, check=False)
                stream, code = done.stdout, done.returncode
            except subprocess.TimeoutExpired as error:
                stream = error.stdout.decode() if isinstance(error.stdout, bytes) else (error.stdout or "")
                code = None
            (out / f"turn-{number:02d}.jsonl").write_text(stream, encoding="utf-8")
            cost = last_result(stream).get("total_cost_usd")
            spent += float(cost) if isinstance(cost, (int, float)) else TURN_BUDGET_USD   # unknown counts in full
            denials = [d.get("tool_input", {}).get("command") for d in last_result(stream).get("permission_denials") or []]
            turns.append({"turn": number, "exit": code, "cost_usd": cost, "denied_commands": denials})
            (out / "turns.json").write_text(json.dumps(turns, indent=1) + "\n", encoding="utf-8")
            if code != 0:
                break
        events = list(stream_events(log.read_text(encoding="utf-8"))) if log.exists() else []
        schema = {"claude_code": subprocess.run(["claude", "--version"], capture_output=True, text=True,
                                                check=False).stdout.strip(),
                  "turns": turns, "spent_usd": round(spent, 4),
                  "events": [shape(event) for event in events]}
        text = redact(json.dumps(schema, indent=1, ensure_ascii=False), workspace) + "\n"
    found = [needle for needle in leak_needles() if needle and needle in text]
    if found:
        print(f"schema.json not written: {len(found)} host value(s) found in it", file=sys.stderr)
        return 1
    (out / "schema.json").write_text(text, encoding="utf-8")
    print(f"{len(events)} hook events, USD {spent:.4f}; schema at {out / 'schema.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
