---
milestone: refactoring-followups
station: phase-F4
scope: phase-F4
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
date: 2026-11-25
gates:
  - command: python -m pytest -q tests/test_refactoring_input_boundaries.py tests/test_model_v2.py tests/test_population_load.py tests/test_rf7_input_policy.py tests/test_review_bands.py tests/test_rf1_helper_pins.py tests/test_go1_evolve_parse_once.py --tb=short
    exit: 0
  - command: python -m pytest -q tests/test_refactoring_input_boundaries.py tests/test_rf1_helper_pins.py tests/test_rf7_input_policy.py --tb=short
    exit: 0
evidence:
  - path: .gnd-planning/milestones/refactoring-followups/notes/F4-Claude-review.md
    sha256: 4e093c4b7e9e6088ec843885de32ce74a5a723518ebe8f8783a8ef0c96ea24ca
---
Delegated acceptance of #301 and the model, population and pool reader portion of #302. The latter remains open. The inventory names component owners and triggers for the remaining readers, validator errors and historical MIME profiles. Tests verified the historical MIME variant and finite canonical output. The writer refuses three nonfinite values. Imported golden bytes remain hash-bound.

    314 passed, 1 deselected in 60.30s (0:01:00)
    127 passed in 19.08s

Claude requested changes. The repaired population error names its source. The golden uses the successor table and fixed bytes, including the older Python 3.11 wording. The current interpreter ran the tests. The two readers retain single-pass early refusal. Delegated clarification of refusal order: the first budget violation wins, even if a later event would previously have triggered another error. Scanning past a known depth violation consumes untrusted input unnecessarily. Both orderings now have regression tests. Files within all budgets retain the prior scanner and construction. The reviewer's surrogate path and pre-existing YAML/JSON fallback cases remain with the relevant component owners under #302. The surrogate path was demonstrated only at function level. No independent review of the repairs. Touched lint passed, component index reported zero fixes. Slow cadence: uv run pytest -q -m "evidence or census".
