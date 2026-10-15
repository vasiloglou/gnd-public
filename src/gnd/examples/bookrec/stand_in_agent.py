"""A scripted stand-in for a coding assistant, for the offline BookRec session.

GND sends the session prompt on stdin as JSON, with the previous attempt's
closed feedback (if any) in ``feedback_base64``. The stand-in writes
``recommendation.population.json`` in its working directory, the candidate
folder, starting from the seed facts in ``../input/seed.population.json``.

Attempt 1 does what the user literally asked: Ada liked the look of ``night``,
so it adds that recommendation. Attempt 2 reads the feedback, drops every
recommendation the checker named as an offending fact, and recommends
``cosmos`` to Ada instead. It is deterministic so the tutorial runs without a
model provider. A real session uses Claude Code, Codex, any declared command
or an OpenAI-compatible endpoint in its place.
"""
from __future__ import annotations

import base64
import json
import sys
from pathlib import Path

CANDIDATE = "recommendation.population.json"


def offending_pairs(feedback: dict) -> set[tuple[str, str]]:
    """Every (user, book) pair the checker reported as an offending fact."""
    pairs = set()
    for case in feedback.get("required", []):
        for violation in case.get("acceptance", {}).get("violations", []):
            for fact in violation.get("offending_facts", []):
                if isinstance(fact, dict) and "$u" in fact and "$b" in fact:
                    pairs.add((str(fact["$u"]), str(fact["$b"])))
    return pairs


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("gnd-bookrec-stand-in 1")
        return 0
    message = json.load(sys.stdin)
    encoded = message.get("feedback_base64")
    feedback = json.loads(base64.b64decode(encoded)) if encoded else {}
    seed_path = Path("../input/seed.population.json")
    if not seed_path.is_file():
        sys.exit("stand-in: expected the seed at ../input/seed.population.json next to the candidate directory")
    seed = json.loads(seed_path.read_text(encoding="utf-8"))
    # What the user asked for: the seed recommendations plus night for Ada.
    rows = [*seed["facts"]["recommendation"], {"user": "ada", "book": "night"}]
    named = offending_pairs(feedback)
    if named:
        # Repair: drop every pair the checker named, then pick another book for Ada.
        rows = [r for r in rows if (r["user"], r["book"]) not in named]
        rows.append({"user": "ada", "book": "cosmos"})
    seed["facts"]["recommendation"] = rows
    Path(CANDIDATE).write_text(json.dumps(seed, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
