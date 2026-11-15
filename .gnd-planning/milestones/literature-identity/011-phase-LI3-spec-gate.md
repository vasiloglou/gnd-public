---
milestone: literature-identity
station: phase-LI3-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI3-spec-gate
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of LI3 diagnostic spec"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI3-spec.md
    sha256: d236004e3cb5bae04f1c5e99f1af89a5f9168336c7af920559db92d9f5bee449
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The current milestone chat
authorizes the LI3 spec and corpus rulings. The implementability sweep
covers the finite diagnostic, corpus, sample strata and liveness controls.
D1–D5 of the bound spec are approved as written. Threshold 0.8 and
family minimum 4 define the diagnostic. The per-measured-kind ceiling is
1/5 false discoveries. Sample 100 using uniform sampling within each
predeclared stratum and seed 193, with a census for smaller outputs.
An undersized stratum stays unmeasured.

The approval instrument is corpus-first. A separate corpus record must
bind the data and expected behavior before the diagnostic is implemented.
The review instrument is one Claude Code phase-diff review on stdin.
The spec review budget is zero rounds. This ruling preserves plan D4's
example scope and LI2's precedence and composition contract.

## Open questions

Synthetic corpus design and exact fixture outcomes are bound at the
corpus gate.
