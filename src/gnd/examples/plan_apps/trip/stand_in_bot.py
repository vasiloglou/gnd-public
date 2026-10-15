"""A scripted stand-in for the trip-planning bot, so the app runs without a model provider.

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

TRIP, NIGHTS = "lisbon", ["2025-05-12", "2025-05-13", "2025-05-14"]


def main() -> int:
    prompt = json.load(sys.stdin)
    seen = failures(prompt)
    hotel, activities = "palacio", ["tram-28-tour", "fado-night", "sintra-day"]   # first try: the nicest hotel
    if any(f["check"] == "within_budget" for f in seen):
        hotel, activities = "alfama-inn", activities + ["belem-walk"]            # cheaper hotel, so one more outing
    clashes = [row for f in seen if f["check"] == "no_overlap" for row in rows(f["witness"]) if isinstance(row, dict)]
    if clashes:
        activities = [a for a in activities if a != clashes[0]["activity"]] + ["oceanarium"]
    plan = [{"op": "book_hotel", "bindings": {"trip": TRIP, "hotel": hotel, "night": n}} for n in NIGHTS]
    plan += [{"op": "book_activity", "bindings": {"trip": TRIP, "activity": a}} for a in activities]
    print(json.dumps({"steps": plan}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
