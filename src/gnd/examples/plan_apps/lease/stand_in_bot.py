"""A scripted stand-in for the rent-schedule bot, so the app runs without a model provider.

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

LEASE, RENT, MONTHS = "apt-4b", 1450, 6


def main() -> int:
    prompt = json.load(sys.stdin)
    starts = {row.get("$start") for f in failures(prompt) if f["check"] == "due_after_start" for row in rows(f["witness"])
              if isinstance(row, dict)}
    # first try: a month early; after feedback, from the start date the checker named
    year, month = (int(part) for part in min(starts).split("-")[:2]) if starts else (2025, 1)
    plan = []
    for _ in range(MONTHS):
        plan.append({"op": "schedule_payment", "bindings": {"lease": LEASE, "amount": RENT, "due": f"{year}-{month:02d}-01"}})
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)
    print(json.dumps({"steps": plan}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
