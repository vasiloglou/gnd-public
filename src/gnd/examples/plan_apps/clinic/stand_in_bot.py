"""A scripted stand-in for the pharmacy-refill bot, so the app runs without a model provider.

It reads the app's prompt on stdin (the question, the rules, the operations, the state and the
earlier attempts with their failures) and answers with a plan on stdout. Like a small model, it
fixes one reported problem at a time, learning only from the checker's feedback. A real bot
(Claude Code, or a small model through tools/openrouter_gateway.py) reads the same prompt.
"""
from __future__ import annotations

import json
import sys


def rows(witness):
    """GND lists a rule's bindings; the PyRel program prints one binding per line."""
    if isinstance(witness, list):
        return [w for w in witness if isinstance(w, (dict, list))]
    return [witness] if isinstance(witness, dict) else []


def failures(prompt):
    return [f for attempt in prompt["attempts"] for f in attempt["failures"]]

PATIENT, TODAY = "sam", "2024-03-10"   # "Refill Sam's prescriptions today."


def add_days(day, days):
    import datetime
    return (datetime.date.fromisoformat(day) + datetime.timedelta(days=days)).isoformat()


def main() -> int:
    prompt = json.load(sys.stdin)
    drugs = [r["drug"] for r in prompt["state"]["facts"]["prescribed"] if r["patient"] == PATIENT]
    when = {drug: TODAY for drug in drugs}
    for attempt in prompt["attempts"]:   # fix the first problem each attempt reported, in order
        problems = [f for f in attempt["failures"] if f["status"] == "violated"]
        if not problems:
            continue
        first = problems[0]
        found = rows(first["witness"])[0] if rows(first["witness"]) else {}
        if first["check"] == "refill_not_early":
            when[found["$d"]] = add_days(found["$last"], found["$n"])
        elif first["check"] == "no_interacting_refills":
            when.pop(found["$a"], None)          # leave one of the pair for another day
    plan = [{"op": "refill_drug", "bindings": {"patient": PATIENT, "drug": d, "on": on}} for d, on in when.items()]
    print(json.dumps({"steps": plan}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
