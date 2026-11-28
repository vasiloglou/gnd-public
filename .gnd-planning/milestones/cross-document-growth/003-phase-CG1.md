---
milestone: cross-document-growth
station: phase-CG1
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-CG1
date: 2026-11-28
gates:
  - command: "pytest -q tests/test_cross_document_growth_phase1.py tests/test_evolve_additive_policy.py --tb=short"
    exit: 0
  - command: "pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py tests/test_install.py tests/test_doctor_uninstall.py tests/test_verification_fixes.py tests/test_inventory_pin_home.py tests/test_mc3_evolution.py tests/test_cross_document_growth_phase1.py --tb=short"
    exit: 0
  - command: "ruff check ."
    exit: 0
  - command: "python3 scripts/components_index.py --no-cache changed --base 009d18ca --strict"
    exit: 0
evidence:
  - path: tests/test_cross_document_growth_phase1.py
    sha256: ae2a2bc04202c6dc5fa3c483cce53730d433044900b1fc603926c151ae0e7778
  - path: .gnd-planning/milestones/cross-document-growth/notes/reviews/CG1-r1/independent-review.md
    sha256: 2b48268479e8468761b20ab7e884cfbfb15f0b3a04a352ba3d4380a36ab28c6e
slow_cadence: 'uv run pytest -q -m "evidence or census"'
---

The delegated ruling accepts the CG1 implementation at 9ffa5a89 against the spec approved in 002-plan-gate. The CLI admitted a new tuple and a disjoint second observation of a previously recorded tuple. It refused overlapping or unsupported citations, changed prior rows, an included target and a conflicting deontic uniqueness result. A refused preview stays refused at the service API. The recovery test preserves previously published bytes.

The independent reviewer verified 15 file hashes and requested changes. The [findings ledger](notes/reviews/CG1-r1/FINDINGS.md) records the original helper invocation failure, the successful direct stdin invocation, two admission fixes and the coverage additions. The repaired bytes have executable regression evidence and no subsequent reviewer opinion. The shared fact modification refusal offers limited diagnostic detail.

Focused result: 99 passed in 10.92s. Guard and composition result: 983 passed, 2 deselected in 133.32s (0:02:13). Nine earlier failures used the host 0.5.1 console script. Rerunning with the 0.5.2 worktree environment first on PATH cleared all nine. The historical public CLI surface suite separately returned 135 passed. The default fast lane was selected.

Refactoring review: source verification, canonical values, model indexing, population evaluation, include ownership and transactional recovery use their existing defining components. Distinct intervals for one typed tuple are sorted to check overlaps, preserving old observations. The counted RF5/RF6 successors record the changed source shapes. Component regeneration passed the strict change check with zero fixes and zero warnings.
