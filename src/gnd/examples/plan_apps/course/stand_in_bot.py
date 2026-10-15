"""A scripted stand-in for the course-planning bot, so the app runs without a model provider.

It reads the app's prompt on stdin (the question, the rules, the operations, the state and the
earlier attempts with their failures) and answers with a plan on stdout. Like a small model, it
starts from what the student asked for and repairs only from the checker's feedback:

  - a prerequisites_first failure names the courses still needed: take those, defer the wanted one,
    and fill the term with an elective;
  - a pre_offered failure names a course not offered this term: try the next elective.

A real bot (Claude Code, or a small model through tools/openrouter_gateway.py) reads the same prompt.
"""
from __future__ import annotations

import json
import re
import sys

STUDENT, TERM = "maya", "spring"
WANTED = "CS340"                       # "She really wants Machine Learning."
ELECTIVES = ["CS250", "PHIL101"]       # tried in this order to fill the term


def rows(witness):
    """GND lists a rule's bindings; the PyRel program prints one binding per line."""
    if isinstance(witness, list):
        return [w for w in witness if isinstance(w, dict)]
    return [witness] if isinstance(witness, dict) else []


def main() -> int:
    prompt = json.load(sys.stdin)
    failures = [f for attempt in prompt["attempts"] for f in attempt["failures"]]
    needed = sorted({row["$needs"] for f in failures if f["check"] == "prerequisites_first" for row in rows(f["witness"])})
    refused = set()
    for f in failures:
        if "pre_offered" in f["check"]:
            refused |= {row["course"] for row in rows(f["witness"]) if "course" in row}
            refused |= set(re.findall(r"'course': '([^']+)'", f.get("message") or ""))
    if not failures:
        courses = [WANTED, "MATH220", "STAT210"]   # what she asked for, with the courses it needs
    else:
        courses = needed + [next(c for c in ELECTIVES if c not in refused)]
    print(json.dumps({"steps": [{"op": "enroll", "bindings": {"student": STUDENT, "course": c, "term": TERM}}
                                for c in courses]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
