"""Record real models answering the five plan apps' questions, every run kept.

Each run is one `app.py ask QUESTION` with a model behind tools/plan_app_bot.py, checked by the
chosen backend, at most 3 attempts. The tool refuses to start without --authorized-by naming the
owner's gate record. It writes, under --out:

    results.json                  one row per run, in recording order, none left out
    manifest.json                 SHA-256 of every recorded file and of the sources that made them
    <model>/<example>/run-N/session.txt     what the app printed (paths redacted to <workspace>)
    <model>/<example>/run-N/reply-NN.json   the model's raw reply to each attempt, with usage

The OpenRouter key is read from --env-file as data by tools/agent_with_env_key.py, in the bot's
process only; it is never printed, and the recorded files are searched for it before they are kept.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import os
import re
import shlex
import shutil
import signal
import subprocess
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPS = ROOT / "src/gnd/examples/plan_apps"
QUESTIONS = {
    "course": "Plan Maya's spring semester. She really wants Machine Learning.",
    "access": "Give Bob access to payroll; Carol approves.",
    "lease": "Set up the rent schedule for this lease.",
    "clinic": "Refill Sam's prescriptions today.",
    "trip": "Plan three days in Lisbon under 900 EUR.",
}
MODELS = {  # the A1 table: name -> (provider, model)
    "claude-haiku": ("claude", "haiku"),
    "claude-default": ("claude", "default"),
    "llama-3.1-8b": ("openrouter", "meta-llama/llama-3.1-8b-instruct"),
    "gemma-3-4b": ("openrouter", "google/gemma-3-4b-it"),
    "llama-3.2-3b": ("openrouter", "meta-llama/llama-3.2-3b-instruct"),
}
ATTEMPTS = 3
RUN_SECONDS = 1800


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def bot_command(name: str, log: Path, env_file: Path) -> str:
    provider, model = MODELS[name]
    adapter = [sys.executable, str(ROOT / "tools/plan_app_bot.py"), "--provider", provider, "--log", str(log)]
    if model != "default":
        adapter += ["--model", model]
    if provider == "openrouter":
        adapter = [sys.executable, str(ROOT / "tools/agent_with_env_key.py"), "--env-file", str(env_file),
                   "--name", "OPENROUTER_API_KEY", "--", *adapter]
    return shlex.join(adapter)


TEMPORARY = re.compile(r"(?:(?:/private)?/var/folders/[^\s\"']+?/T|/tmp)/gnd-plan-[a-z0-9_]+")
LOCAL = ("/Users/", "/private/", "/home/", "/var/folders/", "/tmp/")


def redact(text: str, redactions: list[tuple[str, str]]) -> str:
    """Local paths out: the run's workspace, the repository, the home directory, and the app's temporary plan
    directory (a checker's refusal names the plan file it read)."""
    for old, new in redactions:
        text = text.replace(old, new)
    return TEMPORARY.sub("<tmp>", text)


FAILURE = re.compile(r"^    (states? [\d, -]+|step \d+|plan)  (\S+)  (not checked|\S+)(?:  (.*))?$")
VERDICT = re.compile(r"^  (?:gnd|pyrel) check: exit (\d+)")


def summary(session: str) -> list[dict]:
    """Per attempt, read back from what the app printed: the checker's exit, each distinct (check, status) it
    reported (warnings and unchecked rules included, so an accepted attempt can list some), the refusal codes
    of a malformed plan, and the bot's note or decline. The app prints notes on one line, and the checker's
    verdict is the last verdict line of the block, after anything the bot wrote."""
    attempts = []
    for block in re.split(r"^attempt \d+\n", session, flags=re.M)[1:]:
        lines = block.splitlines()
        verdicts = [VERDICT.match(line) for line in lines if VERDICT.match(line)]
        failures = sorted({(m.group(2), m.group(3)) for m in map(FAILURE.match, lines) if m})
        declined = next((line[len("  the bot made no plan: "):] for line in lines
                         if line.startswith("  the bot made no plan: ")), None)
        note = next((line[len("  the bot says: "):] for line in lines if line.startswith("  the bot says: ")), None)
        attempts.append({"exit": int(verdicts[-1].group(1)) if verdicts else None,
                         "unusable": any(line.startswith("  the bot's answer was not usable") for line in lines),
                         "declined": declined, "note": note,
                         "steps": sum(line.startswith("  plan  ") for line in lines),
                         "failures": [list(pair) for pair in failures],
                         "refusals": sorted(set(re.findall(r"\[(transition:[\w-]+)\]", block)))})
    return attempts


def outcome(row: dict) -> str:
    """first, repaired-rule (refused on a rule, exit 1, before acceptance), repaired-format (only malformed or
    unusable answers before acceptance), declined, refused, or crash."""
    attempts, accepted = row["attempts"], row["accepted_at"]
    if accepted == 1:
        return "first"
    if accepted:
        return "repaired-rule" if any(a["exit"] == 1 for a in attempts[:accepted - 1]) else "repaired-format"
    if any(a["declined"] for a in attempts):
        return "declined"
    return "crash" if row["app_exit"] not in (0, 1) else "refused"


OUTCOMES = ["first", "repaired-rule", "repaired-format", "declined", "refused", "crash"]


def replay_choice(rows: list[dict], example: str | None = None) -> dict | None:
    """A1: the first run in results.json order (model, example, run) refused on a rule, then accepted."""
    return next((r for r in rows if outcome(r) == "repaired-rule" and example in (None, r["example"])), None)


def readme_table(rows: list[dict]) -> list[str]:
    models = list(dict.fromkeys(r["model"] for r in rows))
    examples = list(dict.fromkeys(r["example"] for r in rows))
    lines = ["| Model | " + " | ".join(examples) + " |", "|---|" + "---|" * len(examples)]
    for model in models:
        cells = []
        for example in examples:
            counts = [(k, sum(outcome(r) == k for r in rows if (r["model"], r["example"]) == (model, example)))
                      for k in OUTCOMES]
            cells.append(", ".join(f"{n} {k}" for k, n in counts if n) or "-")
        served = sorted({m for r in rows if r["model"] == model for m in r.get("served_models", [])})
        lines.append(f"| {model} ({', '.join(f'`{m}`' for m in served) or '?'}) | " + " | ".join(cells) + " |")
    return lines


def served_models(folder: Path) -> list[str]:
    found = set()
    for reply in folder.glob("reply-*.json"):
        data = json.loads(reply.read_text(encoding="utf-8"))
        model = data.get("served_model", data.get("model"))
        found.update(model if isinstance(model, list) else [model] if model else [])
    return sorted(found)


def record_one(name: str, example: str, run: int, out: Path, args) -> dict:
    target = out / name / example / f"run-{run}"
    target.mkdir(parents=True)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="plan-rec-") as workspace:
        work = Path(workspace)
        command = [sys.executable, str(APPS / example / "app.py"), "ask", QUESTIONS[example],
                   "--backend", args.backend, "--attempts", str(ATTEMPTS), "--out", str(work / "next.pop.json"),
                   "--bot", bot_command(name, work / "replies", args.env_file)]
        environment = dict(os.environ)
        if args.pyrel_python:
            environment["GND_PYREL_PYTHON"] = str(args.pyrel_python)
        process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=work,
                                   env=environment, start_new_session=True)   # its own group: a timeout kills all
        try:
            stdout, stderr = process.communicate(timeout=RUN_SECONDS)
            code = process.returncode
        except subprocess.TimeoutExpired:
            os.killpg(process.pid, signal.SIGKILL)
            stdout, stderr = process.communicate()
            code, stderr = None, (stderr or "") + f"\n[the run did not finish within {RUN_SECONDS} s]"
        session = (stdout or "") + (f"\n[stderr]\n{stderr}" if stderr else "")
        redactions = [(str(work.resolve()), "<workspace>"), (workspace, "<workspace>"), (str(ROOT), "<repo>"),
                      (str(Path.home()), "<home>")]
        session = redact(session, redactions)
        (target / "session.txt").write_text(session, encoding="utf-8")
        replies = sorted((work / "replies").glob("reply-*.json")) if (work / "replies").exists() else []
        cost = 0.0
        for reply in replies:
            text = redact(reply.read_text(encoding="utf-8"), redactions)
            (target / reply.name).write_text(text, encoding="utf-8")
            cost += json.loads(text).get("cost_usd") or 0.0
    return index_row(name, example, run, args.backend, code, session, target, time.monotonic() - started, cost)


def index_row(name, example, run, backend, code, session, target, seconds, cost) -> dict:
    attempts = summary(session)
    accepted = next((i for i, a in enumerate(attempts, 1) if a["exit"] == 0), None)
    return {"model": name, "provider": MODELS[name][0], "model_id": MODELS[name][1], "example": example, "run": run,
            "question": QUESTIONS[example], "backend": backend, "app_exit": code, "accepted_at": accepted,
            "attempts": attempts, "served_models": served_models(target), "seconds": round(seconds, 1),
            "claude_cost_usd": round(cost, 5) if MODELS[name][0] == "claude" else None}


def preflight_error(args) -> str:
    """Before any model is called: each example's documented first plan gets its documented verdict."""
    environment = dict(os.environ)
    if args.pyrel_python:
        environment["GND_PYREL_PYTHON"] = str(args.pyrel_python)
    for example in args.examples:
        plan = APPS / example / "plans/attempt-1.steps.json"
        done = subprocess.run([sys.executable, str(APPS / example / "app.py"), "check", str(plan), "--backend",
                               args.backend], capture_output=True, text=True, env=environment, timeout=600, check=False)
        if done.returncode != 1 or f"{args.backend} check: exit 1" not in done.stdout:
            return (f"preflight: {example}'s attempt-1 plan did not get its documented verdict (exit 1): "
                    f"exit {done.returncode}: {(done.stdout + done.stderr).strip()[-300:]}")
    return ""


def git_identity() -> list[str]:
    """The git user's email and its handle: an agent may copy them into what it writes (audit fields)."""
    email = subprocess.run(["git", "config", "user.email"], capture_output=True, text=True, check=False).stdout.strip()
    return [email, email.split("@")[0]] if "@" in email else []


def leaks(out: Path, env_file: Path | None) -> list[str]:
    """Recorded files that contain a local path or, when an env file is given, the OpenRouter key."""
    needles = [str(Path.home()), *LOCAL, *git_identity()]
    if env_file is not None:
        import importlib.util
        spec = importlib.util.spec_from_file_location("agent_with_env_key", ROOT / "tools/agent_with_env_key.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        needles.append(module.read_key(env_file, "OPENROUTER_API_KEY"))
    return [str(p.relative_to(out)) for p in sorted(out.rglob("*")) if p.is_file()
            and any(n in p.read_text(encoding="utf-8", errors="replace") for n in needles)]


def digests(out: Path) -> dict:
    return {str(p.relative_to(out)): sha256(p.read_bytes()) for p in sorted(out.rglob("*"))
            if p.is_file() and p.name not in ("manifest.json", "README.md", "CAVEATS.md")}


def verified_manifest(out: Path) -> dict:
    """The manifest, after checking that every recorded file still has its recorded digest."""
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    if digests(out) != manifest["files"]:
        raise SystemExit("the recording does not match its manifest; refusing to re-sign it")
    return manifest


def rebind(out: Path, env_file: Path | None) -> int:
    """A redaction added after a recording. The manifest is checked first; a file may change only to its own
    redaction; the changed files and their old and new digests are recorded. Outcomes are not touched."""
    manifest = verified_manifest(out)
    changed = {}
    for path in sorted(out.rglob("*")):
        if path.is_file() and path.name not in ("manifest.json", "results.json", "README.md"):
            text = path.read_text(encoding="utf-8")
            if redact(text, []) != text:
                old = sha256(path.read_bytes())
                path.write_text(redact(text, []), encoding="utf-8")
                changed[str(path.relative_to(out))] = {"before": old, "after": sha256(path.read_bytes())}
    found = leaks(out, env_file)
    if found:
        print("still holding a key or a local path: " + ", ".join(found), file=sys.stderr)
        return 1
    if changed:
        manifest["files"] = digests(out)
        manifest["rebound"] = manifest.get("rebound", []) + [
            {"date": time.strftime("%Y-%m-%d"), "redaction": "temporary plan directory -> <tmp>", "changed": changed}]
        (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    print(f"rebound: {len(changed)} files changed")
    return 0


def reindex(out: Path, drift: list[str]) -> int:
    """Rebuild results.json's per-run index from the recorded session.txt and reply files, which stay as they
    were recorded; then write the README. The manifest is checked first and the reindex is recorded in it.
    --drift SOURCE=WHY names a source that changed since the recording, and why."""
    manifest = verified_manifest(out)
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    for row in results["runs"]:
        folder = out / row["model"] / row["example"] / f"run-{row['run']}"
        session = (folder / "session.txt").read_text(encoding="utf-8")
        fresh = index_row(row["model"], row["example"], row["run"], row["backend"], row["app_exit"], session, folder,
                          row["seconds"], row.get("claude_cost_usd") or 0.0)
        row.update({k: fresh[k] for k in ("accepted_at", "attempts", "served_models")})
    results["order"] = ("results.json order is (model, example, run); the model lanes ran side by side, so it is "
                        "not the order in which runs happened")
    (out / "results.json").write_text(json.dumps(results, indent=1) + "\n", encoding="utf-8")
    for item in drift:
        source, _, why = item.partition("=")
        manifest.setdefault("drift", {})[source] = why
    manifest["files"] = digests(out)
    manifest["reindexed"] = manifest.get("reindexed", []) + [time.strftime("%Y-%m-%d")]
    (out / "manifest.json").write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    write_readme(out)
    print(f"reindexed {len(results['runs'])} runs")
    return 0


def write_readme(out: Path) -> None:
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    caveats = out / "CAVEATS.md"
    rows, chosen = results["runs"], replay_choice(results["runs"])
    text = [
        "# Recorded runs: real models behind the plan apps", "",
        f"Recorded {results['recorded']} under the gate record `{results['gate']}`. Each run is one",
        f"`app.py ask QUESTION --attempts {results['attempts_per_run']} --backend {results['backend']}` with the model "
        "behind `tools/plan_app_bot.py`.", "Every run is listed in `results.json`; none was dropped. "
        "`manifest.json` binds each file by SHA-256.", "",
        f"Outcomes per model and app, over {results['runs_per_model_and_example']} runs "
        "(the served model ids are in brackets):", "",
        "- **first**: accepted at the first attempt;",
        "- **repaired-rule**: refused on a rule (exit 1), then accepted after the feedback;",
        "- **repaired-format**: only malformed plans (exit 3) or unusable answers before acceptance;",
        "- **declined**: the model answered that no useful plan exists, with a reason;",
        "- **refused**: no plan accepted in the attempts allowed;",
        "- **crash**: the run did not finish normally.", "",
        "<!-- --8<-- [start:table] -->", *readme_table(rows), "<!-- --8<-- [end:table] -->", "",
        "## The replayed run", "",
        (f"Replayed run: `{chosen['model']}/{chosen['example']}/run-{chosen['run']}`, the first run in results.json "
         "order (model, example, run) refused on a rule and then accepted (A1 protocol). The model lanes ran side "
         "by side, so this is table order, not the order in which runs happened." if chosen else
         "No run was refused and then accepted."), "",
        "## What a run folder holds", "",
        "- `session.txt`: what the app printed, with paths shortened to `<workspace>` and `<tmp>`;",
        "- `reply-NN.json`: the model's raw reply to attempt NN, with usage.", "",
        f"Claude Code reported ${sum(r.get('claude_cost_usd') or 0 for r in rows):.2f} for its runs; OpenRouter "
        f"reported ${openrouter_cost(out, rows):.4f}.", "",
        "## Sources changed since the recording", "",
        *[f"- `{source}`: {why}" for source, why in sorted(manifest.get("drift", {}).items())], "",
    ]
    if caveats.exists():
        text += ["<!-- --8<-- [start:caveats] -->", caveats.read_text(encoding="utf-8").rstrip(),
                 "<!-- --8<-- [end:caveats] -->", ""]
    (out / "README.md").write_text("\n".join(text), encoding="utf-8")


def openrouter_cost(out: Path, rows: list[dict]) -> float:
    total = 0.0
    for row in rows:
        if row["provider"] == "openrouter":
            for reply in (out / row["model"] / row["example"] / f"run-{row['run']}").glob("reply-*.json"):
                total += (json.loads(reply.read_text(encoding="utf-8")).get("usage") or {}).get("cost") or 0.0
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--authorized-by", required=True, type=Path, help="the owner's gate record for this recording")
    parser.add_argument("--out", required=True, type=Path, help="a new directory for the recordings")
    parser.add_argument("--models", nargs="+", default=list(MODELS), choices=list(MODELS))
    parser.add_argument("--examples", nargs="+", default=list(QUESTIONS), choices=list(QUESTIONS))
    parser.add_argument("--runs", type=int, default=5)
    parser.add_argument("--backend", choices=["gnd", "pyrel"], default="pyrel")
    parser.add_argument("--pyrel-python", type=Path)
    parser.add_argument("--env-file", type=Path, default=ROOT / ".env")
    parser.add_argument("--reindex", action="store_true",
                        help="rebuild results.json's index and the README from the recorded files in --out")
    parser.add_argument("--drift", action="append", default=[], help="with --reindex: SOURCE=what changed since")
    parser.add_argument("--rebind", action="store_true",
                        help="re-apply the redactions to the recording in --out and rewrite its file digests; "
                             "the source digests taken when it was recorded are kept")
    args = parser.parse_args()
    if args.rebind:
        return rebind(args.out, args.env_file.resolve() if "openrouter" in {p for p, _ in MODELS.values()} else None)
    if args.reindex:
        return reindex(args.out, args.drift)
    # absolute, not resolved: a venv's python is a symlink, and resolving it would lose the venv
    args.pyrel_python = args.pyrel_python.absolute() if args.pyrel_python else None  # runs start in a temporary directory
    args.env_file = args.env_file.resolve()
    gate = args.authorized_by.resolve()
    if not gate.is_file() or "PL17" not in gate.read_text(encoding="utf-8"):
        parser.error("--authorized-by must name an existing gate record for PL17")
    if not 1 <= args.runs <= 5:
        parser.error("--runs must be 1 to 5 (the gate's bound)")
    if args.backend == "pyrel" and not (args.pyrel_python or os.environ.get("GND_PYREL_PYTHON")):
        parser.error("--backend pyrel needs --pyrel-python or GND_PYREL_PYTHON")
    preflight = preflight_error(args)
    if preflight:
        parser.error(preflight)
    args.out.mkdir(parents=True)  # a new directory: earlier recordings are never overwritten
    order = [(m, e, r) for m in args.models for e in args.examples for r in range(1, args.runs + 1)]

    def safely(m, e, r):  # one run's failure is reported as a row; it never discards the other runs
        try:
            return record_one(m, e, r, args.out, args)
        except Exception as error:  # noqa: BLE001
            return {"model": m, "provider": MODELS[m][0], "model_id": MODELS[m][1], "example": e, "run": r,
                    "question": QUESTIONS[e], "backend": args.backend, "app_exit": None, "accepted_at": None,
                    "attempts": [], "served_models": [], "seconds": 0.0, "claude_cost_usd": None,
                    "error": f"{type(error).__name__}: {error}"}

    def lane(name):  # one model's runs in (example, run) order; the models' lanes run side by side
        return [safely(m, e, r) for m, e, r in order if m == name]

    with concurrent.futures.ThreadPoolExecutor(max_workers=len(args.models)) as pool:
        lanes = dict(zip(args.models, pool.map(lane, args.models)))
    rows = [row for name in args.models for row in lanes[name]]
    (args.out / "results.json").write_text(json.dumps({
        "gate": str(gate.relative_to(ROOT)) if gate.resolve().is_relative_to(ROOT) else gate.name,
        "attempts_per_run": ATTEMPTS, "runs_per_model_and_example": args.runs, "backend": args.backend,
        "recorded": time.strftime("%Y-%m-%d"), "order": "(model, example, run); the model lanes ran side by side",
        "runs": rows}, indent=1) + "\n", encoding="utf-8")
    found = leaks(args.out, args.env_file if any(MODELS[m][0] == "openrouter" for m in args.models) else None)
    if found:
        shutil.rmtree(args.out)   # nothing holding a key or a local path is left behind
        print("refusing to keep the recording, and removed it: a key or a local path was in " + ", ".join(found),
              file=sys.stderr)
        return 1
    sources = ["tools/plan_app_bot.py", "tools/record_plan_apps.py", "src/gnd/examples/plan_apps/core.py",
               *[f"src/gnd/examples/plan_apps/{e}/{f}" for e in args.examples
                 for f in ("model.orm.json", "state.pop.json", "rules.md")]]
    files = {str(p.relative_to(args.out)): sha256(p.read_bytes()) for p in sorted(args.out.rglob("*"))
             if p.is_file() and p.name != "README.md"}
    (args.out / "manifest.json").write_text(json.dumps({
        "files": files, "sources": {s: sha256((ROOT / s).read_bytes()) for s in sources}}, indent=1) + "\n",
        encoding="utf-8")
    write_readme(args.out)
    for row in rows:
        print(f"{row['model']:15} {row['example']:7} run {row['run']}  {outcome(row)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
