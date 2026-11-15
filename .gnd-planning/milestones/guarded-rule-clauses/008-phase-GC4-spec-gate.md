---
milestone: guarded-rule-clauses
station: phase-GC4-spec-gate
skill: gnd:process-phase
scope: phase-GC4-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC4-spec.md sha256 5090aeb767d22a67a34c0c7aa41a41fa83a668be3ef79b33bb7dcada4b2fc238"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_guarded_clause_exports.py --tb=short"
    exit: 1
    output: "8 failed in 0.36s"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC4-spec.md
    sha256: 5090aeb767d22a67a34c0c7aa41a41fa83a668be3ef79b33bb7dcada4b2fc238
  - path: tests/test_guarded_clause_exports.py
    sha256: b036583f10f6fb17781d85419db1f380f55aff3bcd5be1ef65901acd72c60536
---

# GC4 spec and corpus gate

**Delegated approval (auto=true), 2026-11-15.** The named milestone
invocation approves the E1–E3 spec and initial corpus after GC3 at
883c3029. Claude Code remains selected for independent diff review.

The pre-change corpus reproduced refusal of both supported readable rule
examples, publication of embedded scripts for all three unsupported forms,
and omission of the corresponding Ossie loss reasons. The smoke requires
the original shipped-code rule's vacuous outcome when its exception applies.

Implementation, verification, independent review and phase acceptance remain due.
