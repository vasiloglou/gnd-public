"""The shared core of the plan apps: ask a bot for a plan, check it, feed back, execute.

Every example app (course, clinic, access, trip, lease) is a folder with its rules, model,
state and a stand-in bot, plus a small app.py that calls `main` here. The loop is:

    ask    the bot gets the question, the rules, the operations, the state and the earlier
           attempts' feedback, and answers with a plan (a list of operation steps);
    check  GND (gnd check --pre --steps) or the PyRel program GND generates checks the plan;
    feed   a refused plan's failures go back to the bot: which check, which step, which facts;
    execute an accepted plan's after-state is written to a new file.

A plan may carry a "note" for the user, which the app prints. A bot may decline instead, with
{"steps": [], "reason": ...}, when no useful plan exists; the app prints the reason and stops.

Run from the GND environment. The PyRel backend needs the PyRel interpreter: pass
--pyrel-python PATH or set GND_PYREL_PYTHON.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import shlex
import subprocess
import sys
import tempfile
from pathlib import Path

ATTEMPTS = 5          # most attempts per question
BOT_SECONDS = 600     # most time per bot answer
PYREL_SECONDS = 600   # most time per PyRel check
MAX_STEPS = 100       # most steps in a bot's plan


class Example:
    """One example folder: rules.md, model.orm.json, state.pop.json, stand_in_bot.py."""

    def __init__(self, folder: Path):
        self.folder = Path(folder)
        self.model = self.folder / "model.orm.json"
        self.state = self.folder / "state.pop.json"
        self.rules = (self.folder / "rules.md").read_text(encoding="utf-8")
        self.document = json.loads(self.model.read_text(encoding="utf-8"))

    def digests(self) -> dict:
        from gnd import transition
        from gnd.model import load_model
        loaded = load_model(str(self.model))
        return {"model_digest": transition.transition_model_identity(loaded),
                "operations_digest": transition.operations_digest(loaded.operations)}

    def operations(self) -> list[dict]:
        """What the bot may do: each operation's reading, parameters and preconditions."""
        return [{"op": op["id"], "reading": op.get("reading"),
                 "parameters": {p["name"]: p["object_type"] for p in op.get("parameters", [])},
                 "requires": [pre.get("provenance", {}).get("user_quote", pre["id"]) for pre in op.get("preconditions", [])]}
                for op in self.document.get("operations", [])]


def steps_document(example: Example, steps: list[dict]) -> dict:
    """The bot names operations and bindings; the app adds what ties the plan to this model."""
    return {"steps_schema": 1, "model": example.model.name, **example.digests(),
            "steps": [{"op": s["op"], "bindings": s["bindings"]} for s in steps]}


# ---------------------------------------------------------------- the rules in PyRel

def pyrel_rules(example: Example) -> list[dict]:
    """The model's rules as the PyRel program GND generates states them, read from that program.

    [{kind: rule | derived | precondition | dynamic, name, sentence, code: [lines]}]. The lines come from the LQP
    program, where each requirement runs as written; the DuckDB program the PyRel backend runs checks the same
    rules as violation queries, built from the same lines.
    """
    import re

    from gnd.export.pyrel_rules import render
    text = render(example.model, "lqp")
    body = text[text.index("    # ---- derived facts") if "    # ---- derived facts" in text else text.index("    # ---- rules"):]
    lines = body.splitlines()
    found: list[dict] = []
    current, operation = None, None
    for line in lines:
        stripped = line.strip()
        derived = re.match(r"# (\w+) \((derived|semiderived)\): (.*)", stripped)
        rule = re.match(r"# ([\w:#-]+) \((must|should)\): (.*)", stripped)
        pre = re.match(r"#   precondition preconditions\[id=(\w+)\]: ", stripped)
        dynamic = re.match(r"#   dynamic-rule dynamic_rules\[(\d+)\]: ", stripped)
        header = re.match(r"# (\w+): \S", stripped)
        if header and not rule and not derived:
            operation = header.group(1)
        if derived:
            current = {"kind": "derived", "name": derived.group(1),
                       "sentence": derived.group(3).replace("{", "").replace("}", ""), "code": []}
            found.append(current)
        elif rule and not rule.group(1).startswith("derivation:"):
            current = {"kind": "rule", "name": rule.group(1), "sentence": f"({rule.group(2)}) {rule.group(3)}", "code": []}
            found.append(current)
        elif pre:
            current = {"kind": "precondition", "name": pre.group(1), "sentence": "", "code": []}
            found.append(current)
        elif dynamic:
            current = {"kind": "dynamic", "name": f"{operation}#{dynamic.group(1)}", "sentence": "", "code": []}
            found.append(current)
        elif stripped.startswith("#") or not stripped:
            if stripped.startswith("# ----") or (rule and rule.group(1).startswith("derivation:")):
                current = None
        elif current is not None and "*h_row" not in stripped and (
                ".require(" in stripped or ".define(" in stripped or "aggregates." in stripped):
            current["code"].append(stripped)
            if current["kind"] in ("rule", "precondition", "dynamic"):
                current = None
    sentences = {pre["id"]: pre.get("provenance", {}).get("user_quote", "") for op in example.document.get("operations", [])
                 for pre in op.get("preconditions", [])}
    dynamics = {f"{op['id']}#{i}": rule for op in example.document.get("operations", [])
                for i, rule in enumerate(op.get("dynamic_rules", []))}
    for entry in found:
        if entry["kind"] == "precondition":
            entry["sentence"] = sentences.get(entry["name"], "")
        if entry["kind"] == "dynamic" and entry["name"] in dynamics:
            rule = dynamics[entry["name"]]
            entry["locator"] = f".dynamic_rules[{entry['name'].partition('#')[2]}]"   # GND's locator names the index
            entry["name"], entry["sentence"] = rule["id"], rule.get("provenance", {}).get("user_quote", "")
    return [entry for entry in found if entry["code"]]


def print_rules(example: Example) -> None:
    print("The rules as PyRel, generated from the model by `gnd export pyrel`. In a plan, every relation also")
    print("takes the state as its first argument: `step` is the state after a step, `before` the state before it.")
    print("These are the LQP program's requirements; the DuckDB program checks the same rules as violation queries.")
    for kind, title in (("derived", "Derived facts"), ("rule", "Rules checked on every state"),
                        ("precondition", "Preconditions, checked on the state before each step"),
                        ("dynamic", "Rules across a step, comparing the state before it with the state after")):
        entries = [e for e in pyrel_rules(example) if e["kind"] == kind]
        if entries:
            print(f"\n{title}")
        for entry in entries:
            print(f"  {entry['name']}: {entry['sentence']}")
            for code in entry["code"]:
                print(f"    {code}")


# ---------------------------------------------------------------- checking

def _constraint_ids(model: Path) -> dict:
    """GND's positional constraint refs ("fact_types[x].constraints[0]") to the rule ids the PyRel program prints."""
    from gnd.model import load_model
    from gnd.model_index import ModelIndex
    ids = {}
    for ref, constraint, fact in ModelIndex.for_model(load_model(str(model))).iter_constraints():
        ids[ref] = constraint.get("id") or (f"{fact.get('id')}#{ref.rpartition('[')[2].rstrip(']')}" if fact else ref)
    return ids


def check_gnd(example: Example, pre: Path, steps: Path) -> dict:
    """GND's plan walk, as {exit, failures, post}."""
    from gnd import api
    report = api.transition(str(example.model), str(pre), str(steps), unredacted=True)
    report = report.get("report", report)
    transition = report.get("transition") or {}
    if not transition or transition.get("evaluated") is False or report["exit_code"] == 3:
        # refused before any state was judged (unknown operation, bindings, types): each issue is the reason
        failures = [{"where": "plan", "check": issue.get("path") or "refused", "status": "refused", "witness": None,
                     "message": issue.get("message")} for issue in report.get("issues") or []]
        return {"exit": report["exit_code"], "post": None, "failures": failures or [
            {"where": "plan", "check": "refused", "status": "refused", "witness": None,
             "message": f"GND refused the plan (exit {report['exit_code']})"}]}
    ids = _constraint_ids(example.model)
    failures = []

    def snapshot(where, verdicts):
        for v in verdicts or []:
            if v["verdict"] not in ("pass",):
                failures.append({"where": where, "check": ids.get(v["constraint_ref"], v["constraint_ref"]),
                                 "status": _status(v["verdict"]), "witness": v.get("offending_facts"),
                                 "message": v.get("message")})
    snapshot("state 0", (transition.get("pre_snapshot") or {}).get("verdicts"))
    for v in transition.get("pre_snapshot_verdicts") or []:
        if v["verdict"] != "pass":
            failures.append({"where": "state 0", "check": v["locator"], "status": _status(v["verdict"]),
                             "witness": v.get("offending_facts"), "message": v.get("message")})
    for step in transition.get("steps") or []:
        for v in step.get("verdicts") or []:
            if v["verdict"] != "pass":
                failures.append({"where": f"step {step['index']}", "check": v["locator"], "status": _status(v["verdict"]),
                                 "witness": v.get("offending_facts") or None, "message": v.get("message")})
        snapshot(f"state {step['index']}", (step.get("intermediate") or {}).get("verdicts"))
    post = transition.get("computed_post")
    return {"exit": report["exit_code"], "failures": failures, "post": _with_derived(example, post) if post else None}


def _with_derived(example: Example, post: dict) -> dict:
    """GND's computed post-state lists asserted facts only; add the derived facts GND computes for it,
    so the published state is complete and is accepted as the next question's starting state."""
    from gnd.extensions import evaluate_derivations
    from gnd.model import load_model
    from gnd.population import load_population_bytes
    model = load_model(str(example.model))
    population = load_population_bytes(json.dumps(post).encode(), source="post.json", model=model)
    extensions, _ = evaluate_derivations(model, population)
    facts = dict(post["facts"])
    for head in extensions:
        relation = extensions[head]
        roles = [name for name, _ in relation.roles]
        facts[head] = [dict(zip(roles, row)) for row in relation.rows]
    return {**post, "facts": facts}


def _status(verdict: str) -> str:
    return {"fail": "violated", "warning": "warning", "unchecked": "not checked", "vacuous": "vacuous"}.get(verdict, verdict)


def check_pyrel(example: Example, pre: Path, steps: Path, interpreter: str) -> dict:
    """The PyRel program GND generates for the model, run on the plan, as {exit, failures, post}."""
    from gnd.export.pyrel_rules import render
    with tempfile.TemporaryDirectory(prefix="gnd-plan-app-") as directory:
        program = Path(directory) / "rules.py"
        program.write_text(render(example.model, "duckdb"), encoding="utf-8")
        post = Path(directory) / "post.json"
        try:
            run = subprocess.run([interpreter, "-I", str(program), "--pre", str(pre), "--steps", str(steps),
                                  "--emit-post", str(post)], capture_output=True, text=True, timeout=PYREL_SECONDS,
                                 check=False)
        except subprocess.TimeoutExpired:
            return {"exit": 70, "post": None, "failures": [{"where": "plan", "check": "refused", "status": "refused",
                    "witness": None, "message": f"the PyRel check did not finish within {PYREL_SECONDS} s"}]}
        document = json.loads(post.read_text(encoding="utf-8")) if post.exists() else None
        stderr = run.stderr.replace(str(Path(directory)), "<check>").replace(str(steps.parent), "<plan>")
    failures = parse_pyrel_output(run.stdout)
    if run.returncode not in (0, 1, 2, 4):
        failures.append({"where": "plan", "check": "refused", "status": "refused", "witness": None,
                         "message": stderr.strip()[-2000:]})
    return {"exit": run.returncode, "failures": failures, "post": document}


_STEP_HEADER = re.compile(r"step \d+  \w+\(")


def parse_pyrel_output(stdout: str) -> list[dict]:
    """The PyRel program's report lines as failures: "WHERE  CHECK  STATUS[  WITNESS-OR-MESSAGE]".

    Split at most three times, so a value with two spaces stays whole; step headers ("step 2  enroll(...)")
    and "every rule holds" lines are not failures. A witness that is not JSON is kept as the message."""
    failures = []
    for line in stdout.splitlines():
        if _STEP_HEADER.match(line):
            continue
        parts = line.split("  ", 3)
        if len(parts) < 3:
            continue
        where, check, status = parts[:3]
        rest = parts[3] if len(parts) > 3 else None
        witness = None
        if rest and rest[:1] in '[{"':
            try:
                witness = json.loads(rest)
            except ValueError:
                witness = None
        failures.append({"where": where, "check": check, "status": status, "witness": witness,
                         "message": rest if witness is None else None})
    return failures


def check(example: Example, pre: Path, steps: Path, backend: str, interpreter: str | None) -> dict:
    if backend == "pyrel":
        return check_pyrel(example, pre, steps, _interpreter(interpreter))
    return check_gnd(example, pre, steps)


def _interpreter(given: str | None) -> str:
    chosen = given or os.environ.get("GND_PYREL_PYTHON")
    if not chosen:
        raise SystemExit("--backend pyrel needs the PyRel interpreter: pass --pyrel-python PATH or set GND_PYREL_PYTHON")
    if not (os.path.isfile(chosen) and os.access(chosen, os.X_OK)):
        raise SystemExit(f"the PyRel interpreter {chosen} is not an executable file")
    return chosen


def publish(document: dict, output: Path) -> None:
    """Write the after-state to a fresh file, atomically; an existing file is never replaced."""
    output = Path(output)
    if output.exists():
        raise SystemExit(f"{output} already exists; choose a fresh path")
    descriptor, name = tempfile.mkstemp(prefix=".plan-app-", suffix=".json", dir=output.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(document, stream, indent=1, ensure_ascii=False)
            stream.write("\n")
        os.link(name, output)   # fails if output appeared meanwhile
    finally:
        os.unlink(name)


def out_problem(output: Path | None) -> str:
    """Why --out cannot take the new state, checked before any bot is asked; empty when it can."""
    if output is None:
        return ""
    if output.exists():
        return f"{output} already exists; choose a fresh path"
    if not output.parent.is_dir():
        return f"{output.parent} is not a directory"
    return ""


# ---------------------------------------------------------------- the loop

def ask_bot(bot: list[str], prompt: dict) -> tuple[list[dict] | None, str]:
    """One bot answer: a list of {op, bindings} with the bot's note, if any; an empty list with the bot's
    reason when it declines; or None with the reason the answer could not be used."""
    try:
        run = subprocess.run(bot, input=json.dumps(prompt), capture_output=True, text=True, timeout=BOT_SECONDS,
                             check=False)
    except subprocess.TimeoutExpired:
        return None, f"the bot did not answer within {BOT_SECONDS} s"
    if run.returncode != 0:
        return None, f"the bot exited {run.returncode}: {run.stderr.strip()[-500:]}"
    return parse_answer(run.stdout)


def parse_answer(text: str) -> tuple[list[dict] | None, str]:
    """A bot's stdout as ask_bot returns it: (steps, note), ([], reason) for a decline, or (None, why not)."""
    not_a_plan = ("the bot's answer is not a plan: expected {\"steps\": [{\"op\": ..., \"bindings\": {...}}, ...]}, "
                  "or {\"steps\": [], \"reason\": ...} to decline")
    try:
        answer = json.loads(text)
    except ValueError:
        return None, not_a_plan
    steps = answer.get("steps") if isinstance(answer, dict) else None
    if steps == [] and isinstance(answer.get("reason"), str) and answer["reason"].strip():
        return [], answer["reason"].strip()   # the bot declines: no useful plan exists
    if not (isinstance(steps, list) and steps and all(
            isinstance(s, dict) and isinstance(s.get("op"), str) and isinstance(s.get("bindings"), dict) for s in steps)):
        return None, not_a_plan
    if len(steps) > MAX_STEPS:
        return None, f"the plan has {len(steps)} steps; a plan has at most {MAX_STEPS} steps"
    note = answer.get("note")
    return steps, note.strip() if isinstance(note, str) else ""


def ask(example: Example, question: str, bot: list[str], backend: str, interpreter: str | None, output: Path | None,
        attempts: int = 3, state: Path | None = None) -> int:
    state = Path(state or example.state)
    history = []
    rules, shown = pyrel_rules(example), set()
    for attempt in range(1, attempts + 1):
        prompt = {"question": question, "rules": example.rules,
                  "operations": example.operations(), "state": json.loads(state.read_text(encoding="utf-8")),
                  "attempts": history}
        steps, reason = ask_bot(bot, prompt)
        print(f"attempt {attempt}")
        if steps is None:
            print(f"  the bot's answer was not usable: {reason}")
            history.append({"plan": None, "failures": [{"where": "plan", "check": "format", "status": "refused",
                                                        "witness": None, "message": reason}]})
            continue
        if not steps:
            print(f"  the bot made no plan: {_one_line(reason)}")
            print("no plan was made")
            return 1
        if reason:
            print(f"  the bot says: {_one_line(reason)}")
        for step in steps:
            print(f"  plan  {step['op']}({', '.join(f'{k}={v!r}' for k, v in step['bindings'].items())})")
        with tempfile.TemporaryDirectory(prefix="gnd-plan-") as directory:
            path = Path(directory) / "plan.steps.json"
            path.write_text(json.dumps(steps_document(example, steps)), encoding="utf-8")
            result = check(example, state, path, backend, interpreter)
        print(f"  {backend} check: exit {result['exit']}" + (" (accepted)" if result["exit"] == 0 else ""))
        for where, failure in grouped(result["failures"]):
            print(f"    {_line(where, failure)}")
            rule = _rule_for(failure["check"], rules)
            if rule and rule["name"] not in shown:
                shown.add(rule["name"])
                print(f"      the rule in PyRel: {rule['code'][-1]}")
        if result["exit"] == 70:   # the checker failed, not the plan: nothing to feed back to the bot
            print("the checker could not check the plan; stopping")
            return 70
        if result["exit"] == 0:
            if output and result["post"]:
                publish(result["post"], output)
                print(f"  executed: the new state is in {output}")
            return 0
        history.append({"plan": steps, "failures": result["failures"]})
    print(f"no plan was accepted in {attempts} attempts")
    return 1


def _one_line(text: str) -> str:
    """The bot's words on one line, so nothing it writes can read as the checker's output."""
    return " ".join(text.split())


def grouped(failures: list[dict]) -> list[tuple[str, dict]]:
    """Each distinct failure once, in order of first appearance, with every state it holds in ("states 1-3")."""
    order: list[tuple] = []
    seen: dict[tuple, tuple[list[int], list[str], dict]] = {}
    for failure in failures:
        detail = json.dumps(failure["witness"], sort_keys=True) if failure["witness"] else failure["message"]
        key = (failure["check"], failure["status"], detail)   # GND's messages vary by state; the facts do not
        if key not in seen:
            seen[key] = ([], [], failure)
            order.append(key)
        kind, _, number = failure["where"].partition(" ")
        if kind == "state":
            seen[key][0].append(int(number))
        else:
            seen[key][1].append(failure["where"])
    result = []
    for key in order:
        states, others, failure = seen[key]
        where = [*others]
        if states:
            where.append(("state " if len(states) == 1 else "states ") + _ranges(states))
        result.append((", ".join(where), failure))
    return result


def _ranges(numbers: list[int]) -> str:
    numbers, parts, start = sorted(set(numbers)), [], None
    for i, n in enumerate(numbers):
        start = n if start is None else start
        if i + 1 == len(numbers) or numbers[i + 1] != n + 1:
            parts.append(str(start) if start == n else f"{start}-{n}")
            start = None
    return ", ".join(parts)


def _line(where: str, failure: dict) -> str:
    message = failure["message"] or ""
    if message.startswith("Textual constraint"):
        message = "a textual rule: no checker can check it, so it is listed as not checked"
    witness = json.dumps(failure["witness"]) if failure["witness"] else message
    return f"{where}  {failure['check']}  {failure['status']}  {witness}"


def _rule_for(check: str, rules: list[dict]) -> dict | None:
    """The PyRel rule a failure names: a rule id, or a precondition locator like ...preconditions[id=X]."""
    for rule in rules:
        if rule["kind"] == "rule" and rule["name"] == check:
            return rule
        if rule["kind"] == "precondition" and f"[id={rule['name']}]" in check:
            return rule
    dynamic = [rule for rule in rules if rule["kind"] == "dynamic" and rule.get("locator", "?") in check]
    if len(dynamic) == 1:    # the step's operation is not in the locator, so only an unambiguous index names a rule
        return dynamic[0]
    return None


def main(folder: Path, argv: list[str] | None = None) -> int:
    example = Example(folder)
    parser = argparse.ArgumentParser(description=f"The {folder.name} plan app.")
    parser.add_argument("command", choices=["ask", "check", "execute", "rules"])
    parser.add_argument("text", nargs="?", help="ask: the question. check, execute: a plan (steps.json)")
    parser.add_argument("--backend", choices=["gnd", "pyrel"], default="gnd")
    parser.add_argument("--pyrel-python", help="the PyRel interpreter (or set GND_PYREL_PYTHON)")
    parser.add_argument("--bot", help="the bot command (default: this example's stand-in bot)")
    parser.add_argument("--state", type=Path, default=example.state, help="the starting state")
    parser.add_argument("--out", type=Path, help="where to write the state after an accepted plan")
    parser.add_argument("--attempts", type=int, default=3)
    args = parser.parse_args(argv)
    if not 1 <= args.attempts <= ATTEMPTS:
        parser.error(f"--attempts must be 1 to {ATTEMPTS}")
    if args.command == "rules":
        print_rules(example)
        return 0
    if not args.text:
        parser.error(f"{args.command} needs a question" if args.command == "ask" else f"{args.command} needs a plan")
    if args.command in ("ask", "execute") and out_problem(args.out):
        parser.error(out_problem(args.out))
    if args.command == "execute" and not args.out:
        parser.error("execute needs --out PATH for the new state")
    if args.command == "ask":
        bot = shlex.split(args.bot) if args.bot else [sys.executable, str(example.folder / "stand_in_bot.py")]
        return ask(example, args.text, bot, args.backend, args.pyrel_python, args.out, args.attempts, args.state)
    plan = Path(args.text)
    if not plan.is_file():
        parser.error(f"{plan} is not a file")
    steps, reason = parse_answer(plan.read_text(encoding="utf-8"))
    if not steps:
        parser.error(f"{plan} is not a plan: {reason}")
    with tempfile.TemporaryDirectory(prefix="gnd-plan-") as directory:
        path = Path(directory) / "plan.steps.json"
        path.write_text(json.dumps(steps_document(example, steps)), encoding="utf-8")
        result = check(example, args.state, path, args.backend, args.pyrel_python)
    print(f"{args.backend} check: exit {result['exit']}")
    for where, failure in grouped(result["failures"]):
        print(f"  {_line(where, failure)}")
    if args.command == "execute" and result["exit"] == 0:
        publish(result["post"], args.out)
        print(f"executed: the new state is in {args.out}")
    return result["exit"]
