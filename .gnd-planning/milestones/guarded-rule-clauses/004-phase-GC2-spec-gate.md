---
milestone: guarded-rule-clauses
station: phase-GC2-spec-gate
skill: gnd:process-phase
scope: phase-GC2-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC2-spec.md sha256 a580b9d778507471df36223230ee32225e63428145177fbeb6435085fe0a5513"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_guarded_antecedent_filters.py --tb=short"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/guarded-rule-clauses/notes/phase-GC2-spec.md
    sha256: a580b9d778507471df36223230ee32225e63428145177fbeb6435085fe0a5513
  - path: tests/test_guarded_antecedent_filters.py
    sha256: 4aa2df5ee05a8099b58dbdecfb9eea5d07f3f4567c233ad46960807d8e0744d4
---

# GC2 spec and corpus gate

**Delegated approval (auto=true), 2026-11-15.** The named milestone
invocation delegates this phase's spec and corpus approval. Accept GC2
under the plan and the completed GC1 record at commit `270303c0`.
Approve the named coverage, precedence, diagnostics, and synthesis contracts
and initial five corpus assertions. The owner selected Claude Code for
independent diff review.

The initial corpus exited 1 with `5 failed in 4.83s`. The baseline
rejects filter fields before evaluating a guarded verdict or reporting the
filter-specific unbound reason.

## Boundary and open work

GC2 still owes implementation, the expanded N1–N4 corpus, the focused
verification ledger, independent review and the phase completion record.
