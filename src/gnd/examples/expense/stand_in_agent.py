"""A scripted stand-in for a coding assistant, for the offline expense session.

GND sends the session prompt on stdin as JSON, with the previous attempt's
closed feedback (if any) in ``feedback_base64``. The stand-in writes
``approvals.population.json`` in its working directory, the candidate folder,
starting from the seed facts in ``../input/seed.population.json``.

Attempt 1 does what the user literally asked: the team lead approves expense
102. Attempt 2 reads the feedback, sees which expense and amount the checker
named, and routes that approval through the finance chain instead. It is
deterministic so the tutorial runs without a model provider. A real session
uses Claude Code, Codex, any declared command or an OpenAI-compatible endpoint
in its place.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

CANDIDATE = "approvals.population.json"
EXPENSE = 102


def named_expenses(feedback: dict) -> set[int]:
    """Every expense id the checker reported inside an offending fact."""
    found = set()
    for case in feedback.get("required", []):
        for violation in case.get("acceptance", {}).get("violations", []):
            for fact in violation.get("offending_facts", []):
                if isinstance(fact, dict) and isinstance(fact.get("$e"), int):
                    found.add(fact["$e"])
    return found


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("gnd-expense-stand-in 1")
        return 0
    message = json.load(sys.stdin)
    encoded = message.get("feedback_base64")
    feedback = json.loads(base64.b64decode(encoded)) if encoded else {}
    seed_path = Path("../input/seed.population.json")
    if not seed_path.is_file():
        sys.exit("stand-in: expected the seed at ../input/seed.population.json next to the candidate directory")
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    # The checker named this expense under the team-lead limit: escalate to finance.
    chain = "finance" if EXPENSE in named_expenses(feedback) else "team-lead"
    seed["facts"]["expense_is_approved"].append({"expense": EXPENSE})
    seed["facts"]["expense_approved_by_chain"].append({"expense": EXPENSE, "chain": chain})
    Path(CANDIDATE).write_text(json.dumps(seed, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
