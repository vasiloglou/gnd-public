"""A scripted stand-in for the access-request bot, so the app runs without a model provider.

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

EMPLOYEE, SYSTEM = "bob", "payroll"     # "Give Bob access to payroll; Carol approves."
APPROVERS = ["carol", "erin"]           # Carol, as asked; Erin, the other senior manager


def main() -> int:
    prompt = json.load(sys.stdin)
    seen = failures(prompt)
    if not seen:
        plan = []                                                   # first try: just grant it
    else:
        refused = {row[1] for f in seen if f["check"] == "approver_outside_the_chain" for row in rows(f["witness"])
                   if isinstance(row, list)}
        approver = next(a for a in APPROVERS if a not in refused)
        plan = [{"op": "approve", "bindings": {"approver": approver, "employee": EMPLOYEE, "system": SYSTEM}}]
    plan.append({"op": "grant", "bindings": {"employee": EMPLOYEE, "system": SYSTEM}})
    print(json.dumps({"steps": plan}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
