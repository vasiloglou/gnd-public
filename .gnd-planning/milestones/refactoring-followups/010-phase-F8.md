---
milestone: refactoring-followups
station: phase-F8
scope: phase-F8
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: python3 .gnd-planning/milestones/refactoring-followups/evidence/F8/verify_transfers.py ../gnd
    exit: 0
  - command: python -m pytest -q tests/test_development_scaffold.py::test_source_owned_units_and_preserved_question_states --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/open-questions.md
    sha256: f2fe6adb3701f3347653cd1fa5f92e8eb34b423da48ad59d7a887f3b08ecd04e
  - path: .gnd-planning/milestones/refactoring-followups/notes/F8-Claude-review.md
    sha256: 0221f28b4b11158557263aa3066a1fd54d393e16dcc484c4c0425dac72ad938b
---
Accepted for #308. The owner explicitly selected “Authorize the four transfers” when asked to transfer the four named questions to gnd-public and publish their original wording and provenance in PR #310. The public register records the transfer decision for each ID. The historical launch ledger and original source retain the states they recorded.

    OQ-V52-P1-IMPORTWALK-1 open verified
    OQ-V52-CLOSE-CANONJSON-1 open verified
    OQ-V63-CLOSE-HELPER-TAIL-1 carried verified
    OQ-V72-P1-ARTIFACT-COPIES carried verified
    1 passed in 0.13s

Claude verified the original four quotations and source anchors, and requested clearer provenance and triggers. F1: display the source paths and line numbers and disclose restricted access. F2: quote the first-applicable trigger for the three named artifact callers. F3 and F4: record the #308 decision explicitly in every public entry and link the committed owner handoff. The issue link identifies the tracking issue; the register and PR carry the decisions. F5: correct the Authority column label and document the dated precedence. F6: include v6.0 rerouting for the two v5.2 questions. The verifier compares the actual quotes, including the later trigger, and state at the immutable source revision. No additional questions or source units transferred. Slow cadence: uv run pytest -q -m "evidence or census".
