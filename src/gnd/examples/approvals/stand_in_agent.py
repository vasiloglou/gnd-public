"""A scripted stand-in for an LLM agent, for the offline session tutorial.

GND sends the session prompt on stdin as JSON, with the previous attempt's
closed feedback (if any) in `feedback_base64`. This stand-in writes steps.json
in its working directory: the naive plan on the first attempt, and the plan
with the missing steps once the feedback reports that a step was violated.
It is deterministic so the tutorial runs without a model provider. A real
session uses Claude Code, Codex, a declared command, or an OpenAI-compatible
endpoint in its place.
"""

from __future__ import annotations

import base64
import json
import shutil
import sys
from pathlib import Path

PLANS = Path(__file__).resolve().parent


def violated_operations(feedback: dict) -> list[str]:
    return [
        step["operation_id"]
        for case in feedback.get("required", [])
        for step in case.get("steps", [])
        if step.get("outcome") == "violated"
    ]


def main() -> int:
    if sys.argv[1:] == ["--version"]:
        print("gnd-approvals-stand-in 1")
        return 0
    message = json.load(sys.stdin)
    encoded = message.get("feedback_base64")
    feedback = json.loads(base64.b64decode(encoded)) if encoded else {}
    if "reimburse_expense" in violated_operations(feedback):
        plan = "plan-draft-2.steps.json"  # add the approval and Workday steps
    else:
        plan = "plan-draft-1.steps.json"  # first try: pay directly
    shutil.copyfile(PLANS / plan, "steps.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
