---
milestone: refactoring-followups
station: phase-F6
scope: phase-F6
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: uv run pytest -q tests/test_refactoring_pyrel_parity.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_rf2_pre_move_pins.py --tb=short
    exit: 0
  - command: python -m pytest -q tests/test_refactoring_pyrel_parity.py tests/test_guarded_clause_exports.py tests/test_rf2_pre_move_pins.py -k "pyrel or bytes" --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F6-Claude-review.md
    sha256: d6a7fadc938778efc955d26f9d2ab66e97e380bd69fe8e177f6a281d902eceb8
---
Delegated acceptance for #307. The common admitted domain now has paired reference tests over a real CLI export and the production ModelIndex, with declared IDs, positional addresses, absent declarations and malformed top-level and inline lists. The isolated subprocess blocks all GND imports during load, admission and enumeration. The production implementation and generator are unchanged. On the stable relative basics model name the effective RF2 successor pins 98,872 bytes, SHA-256 60a263a116a50f60070fa7d4c5b8affbc8d34ae163e4e4d7e8ef0476df82ea6f. The original RF2 bytes have their own recorded successor chain.

    52 passed in 7.62s
    5 passed, 26 deselected in 24.82s

Claude requested the stable relative model filename on the real CLI route and highlighted limited malformed-input coverage. Both were repaired and the byte pin was rerun alongside the paired tests. The emitted reader admits some invalid declared IDs that the GND validator rejects. They do not share an admission schema; parity here covers the addressing of admitted constraints and the tested list-shape refusals. Native PyRel database execution and unexercised lazy paths are outside this offline reference-routing scope. Touched lint passed. No separate review over repaired bytes. Slow cadence: uv run pytest -q -m "evidence or census".
