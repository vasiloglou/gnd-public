---
milestone: guarded-rule-clauses
station: phase-GC3-spec-gate
skill: gnd:process-phase
scope: phase-GC3-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC3-spec.md sha256 15975815f6882d8c42796d6fd2d935ef0caf300f34267073aa66636e45eb122c"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_guarded_disjunction.py --tb=short"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC3-spec.md
    sha256: 15975815f6882d8c42796d6fd2d935ef0caf300f34267073aa66636e45eb122c
  - path: tests/test_guarded_disjunction.py
    sha256: b2132eb836789c33dd7073d864b9d12730ecc6a6ba6a6dc3bc134ce6f9ec06bf
---

# GC3 spec and corpus gate

**Delegated approval (auto=true), 2026-11-15.** Accept the A1–A4 phase
spec and initial corpus under the named milestone invocation and GC2
completion at 6ebd39a7. The owner selected Claude Code for independent
diff review.

The initial corpus reported 6 failed and 2 passed in 5.47 seconds.
The current schema refuses usable alternatives before checking them and the
opt-in report still selects version 16. Invalid arity and nesting already
produce validation refusals.

Implementation, expanded differential and diagnostics coverage, verification,
independent review and the phase record remain due.
