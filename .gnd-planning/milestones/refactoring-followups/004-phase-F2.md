---
milestone: refactoring-followups
station: phase-F2
scope: phase-F2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_rf1_pin_harness.py tests/test_rf1_session_pins.py --tb=short
    exit: 0
  - command: uv run pytest -q tests/test_public_v71_witness_corpus.py -k B20 --tb=short
    exit: 0
  - command: .venv/bin/ruff check tests/support/rf1_pins.py tests/support/witness_guard.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/support/public_v71_witness_corpus.py tests/support/v71_witness_cases.py
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F2-Claude-review.md
    sha256: 15e12e46c70a939e71e28809cea578f8c4b23d37a61ae0974a1f61714f508a19
---
Delegated acceptance (auto=true) for #306. The three normalized adapter policies now bind exact declared bytes independent of the file under test. Interpreter paths and prompts are computed from independent expectations. Four historically owed inventory entries and every one of the 35 expected surfaces are matched in both directions. Q3's label corrections appear in the phase spec. Before sharing the guard, each fixture blocked calls to checker.check, extensions.structured_extension_view and terms.evaluate_term. On the candidate each fixture and all four affected public witness branches pass.

    76 passed in 60.39s (0:01:00)
    4 passed, 259 deselected in 0.81s
    All checks passed!

Claude Code reviewed the initial diff and requested changes. Its three findings were reproduced and repaired. The v6 template uses its original ASCII escaping, the inventory test checks extras and owed owners, and the deliberate guard calls cover all three owner modules. Focused tests include a non-ASCII fixture root and one-byte changes. The repairs have test evidence and no separate reviewer opinion. Refactoring review found one shared replacement loop and one guard with preserved entry points. No historical answers were rewritten. Slow cadence: uv run pytest -q -m "evidence or census".
