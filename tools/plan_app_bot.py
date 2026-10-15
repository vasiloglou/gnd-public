"""A model behind a plan app's bot interface: Claude Code, or a small model on OpenRouter.

A plan app (src/gnd/examples/plan_apps/<example>/app.py) runs a bot as a command. The bot reads
one JSON prompt on stdin (the question, the rules as written, the operations, the current state
and the earlier attempts with the checker's failures) and writes {"steps": [...]} on stdout.
This adapter turns that prompt into one chat message, asks the model once, and passes the
model's plan through. It never repairs or rewrites the model's answer: an answer that is not a
plan is printed as it came, and the app counts it as a failed attempt.

    app.py ask "..." --bot "python tools/plan_app_bot.py --provider claude --model haiku"
    app.py ask "..." --bot "python tools/plan_app_bot.py --provider openrouter --model google/gemma-3-4b-it"

The OpenRouter provider reads OPENROUTER_API_KEY from its own environment; put it there with
tools/agent_with_env_key.py, which reads the key from an env file as data. Claude Code uses its
own login. With --log DIR, each call writes the model's raw reply and usage to a new file there.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"
SECONDS = 300
MAX_TOKENS = 2000
SYSTEM = (
    "You plan changes to a small database for a user. Answer with ONLY one JSON object of the form "
    "{\"steps\": [{\"op\": <operation>, \"bindings\": {<parameter>: <value>, ...}}, ...]}, "
    "with each value written as JSON of its kind, as the state writes it. "
    "No prose and no code fences. Use only the listed operations, bind exactly their parameters, "
    "and use the identifiers that appear in the state. The plan is checked against every rule; "
    "if earlier attempts were refused, their failures say which rule broke and on which facts. "
    "If the request cannot be met in full without breaking a rule, plan the closest thing the rules allow "
    "and add \"note\": \"<what was left out and why>\" to the object. Only if no useful plan exists, "
    "answer {\"steps\": [], \"reason\": \"<why>\"}."
)


def message(prompt: dict) -> str:
    """The app's prompt as one user message: every part the app sent, labelled, nothing added."""
    parts = [f"Question: {prompt['question']}", "Rules:\n" + prompt["rules"],
             "Operations:\n" + json.dumps(prompt["operations"], indent=1),
             "Current state:\n" + json.dumps(prompt["state"], indent=1)]
    for number, attempt in enumerate(prompt.get("attempts", []), 1):
        lines = [f"Attempt {number} was refused.", f"Plan: {json.dumps(attempt['plan'])}", "Why:"]
        lines += [f"- {said(failure)}" for failure in attempt["failures"]]
        parts.append("\n".join(lines))
    parts.append("Answer with the plan as JSON.")
    return "\n\n".join(parts)


def said(failure: dict) -> str:
    """One failure in words (A1: the feedback a small model can use), keeping the checker's facts verbatim."""
    text = f"{failure['where']}: {failure['check']} {failure['status']}"
    if failure.get("witness"):
        text += f"; the facts that break it: {json.dumps(failure['witness'])}"
    if failure.get("message"):
        text += f" ({failure['message']})"
    return text


def ask_claude(model: str, text: str) -> tuple[str, dict]:
    # An empty directory and project-only settings: no project files, no user hooks or settings. Claude Code
    # still adds its own environment context (the host's date among it); the recordings disclose that.
    environment = {k: v for k, v in os.environ.items() if not k.startswith(("ANTHROPIC_", "OPENROUTER_"))}
    with tempfile.TemporaryDirectory(prefix="plan-bot-") as directory:
        chosen = ["--model", model] if model else []
        run = subprocess.run(["claude", "--print", *chosen, "--tools", "", "--no-session-persistence",
                              "--strict-mcp-config", "--setting-sources", "project", "--system-prompt", SYSTEM,
                              "--output-format", "json"],
                             input=text, capture_output=True, text=True, timeout=SECONDS, cwd=directory,
                             env=environment, check=False)  # the owner's login, never an API key
    if run.returncode != 0:
        raise SystemExit(f"claude exited {run.returncode}: {run.stderr.strip()[-300:]}")
    reply = json.loads(run.stdout)
    usage = {"served_model": sorted(reply.get("modelUsage") or {}), "cost_usd": reply.get("total_cost_usd"),
             "usage": reply.get("usage")}
    return reply.get("result") or "", usage


def ask_openrouter(model: str, text: str) -> tuple[str, dict]:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set; run this through tools/agent_with_env_key.py")
    body = {"model": model, "max_tokens": MAX_TOKENS,  # the provider's default temperature, as Claude Code uses
            "messages": [{"role": "system", "content": SYSTEM}, {"role": "user", "content": text}]}
    request = urllib.request.Request(OPENROUTER, data=json.dumps(body).encode(), method="POST",
                                     headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"})
    for wait in (5, 15, 0):
        try:
            with urllib.request.urlopen(request, timeout=SECONDS) as response:
                reply = json.load(response)
            break
        except urllib.error.HTTPError as error:
            if error.code not in (429, 502, 503) or not wait:
                raise SystemExit(f"OpenRouter answered HTTP {error.code}")
            time.sleep(wait)
    if "choices" not in reply:
        raise SystemExit(f"OpenRouter returned no choices: {str(reply.get('error'))[:300]}")
    usage = {"served_model": reply.get("model"), "upstream": reply.get("provider"), "usage": reply.get("usage")}
    return reply["choices"][0]["message"].get("content") or "", usage


def plan_text(reply: str) -> str:
    """The reply as the app reads it. One courtesy only: a JSON object wrapped in a code fence is unwrapped."""
    fenced = re.fullmatch(r"\s*```(?:json)?\s*(\{.*\})\s*```\s*", reply, re.S)
    return fenced.group(1) if fenced else reply


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--provider", choices=["claude", "openrouter"], required=True)
    parser.add_argument("--model", help="the model; Claude Code without it uses the account default")
    parser.add_argument("--log", type=Path, help="a directory for the raw replies")
    args = parser.parse_args()
    if args.provider == "openrouter" and not args.model:
        parser.error("--provider openrouter needs --model")
    prompt = json.load(sys.stdin)
    text = message(prompt)
    attempt = len(prompt.get("attempts", [])) + 1
    started = time.monotonic()
    record = {"attempt": attempt, "provider": args.provider, "requested_model": args.model}
    try:
        reply, usage = (ask_claude if args.provider == "claude" else ask_openrouter)(args.model, text)
    except SystemExit as error:   # a failed call is logged too, then reported to the app as before
        _log(args.log, attempt, {**record, "seconds": round(time.monotonic() - started, 1), "error": str(error)})
        raise
    _log(args.log, attempt, {**record, "seconds": round(time.monotonic() - started, 1), "reply": reply, **usage})
    sys.stdout.write(plan_text(reply))
    return 0


def _log(folder: Path | None, attempt: int, record: dict) -> None:
    """One file per attempt, named by the attempt it answers."""
    if folder is not None:
        folder.mkdir(parents=True, exist_ok=True)
        with (folder / f"reply-{attempt:02d}.json").open("x", encoding="utf-8") as handle:
            json.dump(record, handle, indent=1)

if __name__ == "__main__":
    raise SystemExit(main())
