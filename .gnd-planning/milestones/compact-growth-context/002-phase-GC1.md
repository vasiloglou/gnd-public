---
milestone: compact-growth-context
station: phase-GC1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-GC1
date: 2026-11-27
gates:
  - command: "pytest -q tests/test_growth_projection.py tests/test_model_verbalization.py tests/test_rf1_layering.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py --tb=short"
    exit: 0
  - command: "ruff check"
    exit: 0
  - command: "python scripts/components_index.py changed --base c00ac195 --strict"
    exit: 0
evidence:
  - path: src/gnd/model_verbalization.py
    sha256: 606a0b207e17af6d464978b19eb1ad8d6bb51f4cab7a9b7c09393d1d5df5200a
  - path: tests/test_growth_projection.py
    sha256: 2475018268d20ee03312f4564d6730021c93411627027fdd097f36703355213e
  - path: .gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r3/review.md
    sha256: dfc8c0416810fab18e5ce2c89bdeac24517c0daee5257b0dc2b60151fc0e1035
  - path: .gnd-planning/milestones/compact-growth-context/notes/phase-GC2-spec.md
    sha256: 07bd76ef16e2ad8dcc3295459d7561d268e1fc8dda8d677d679e102afaeabe69
---

# GC1 projection accepted

Delegated coordinator ruling (auto=true), 2026-11-27. The composed projection at 5848faf8 retains stable IDs, ordered role players, direct subtypes and constraint signatures. The fixture renders to 8,864 UTF-8 bytes versus 31,742 ordinary and 16,927 source bytes.

## Gate output

    918 passed, 2 deselected in 129.44s (0:02:09)
    All checks passed!
    0 to fix, 0 warning(s), 1 to reread

The recovery subsystem description still applies to its existing consumers. It does not consume the opt-in growth format.

## Independent review
One reviewer is one reviewer. Claude requested changes after reproducing lost object derivation, storage and independence. The fixture assertion failed before the repair and passed after it. Claude approved the repaired diff and independently exercised legal objectification and rule-body cases. The first launcher failed before reading its brief. Its receipt is retained and excluded from reviewer counts. The two subsequent reviews received briefs on stdin.

## Refactoring review
Refactor executed: the ordinary renderer and growth renderer share the include-integrity check. Their output contracts remain distinct.

## Boundary and open questions
Rule bodies and evidence remain in the full model. The format preserves authored optional structural metadata. GC2 carries a focused public test for fact flags. GC1 accepts the plan's measured fixture criterion. This establishes no claim about recall or tokens saved in a complete growth run.

