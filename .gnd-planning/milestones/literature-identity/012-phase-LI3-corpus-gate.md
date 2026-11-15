---
milestone: literature-identity
station: phase-LI3-corpus-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LI3-corpus-gate
date: 2026-11-15
gate:
  command: "ruling: delegated approval (auto=true) of LI3 corpus, exact case outcomes and premeasurement design"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/literature-identity/notes/phase-LI3-spec.md
    sha256: d236004e3cb5bae04f1c5e99f1af89a5f9168336c7af920559db92d9f5bee449
  - path: .gnd-planning/milestones/literature-identity/evidence/LI3/measurement-design.md
    sha256: cbba7d064badfb0aef3f3cf844ebd20bb3d1a19e9ff89b04676c5520f89cdda2
  - path: tests/test_li3_diagnostics.py
    sha256: 15022bb0f4d211e6a06853b606ad70497c630b61f9a70813d3bbe637572c032c
  - path: src/gnd/examples/literature/diagnostics/README.md
    sha256: 3d2d003c86486dfd5655a50ec1d015bb1c0d80814937483206a6735dbdb10ebe
  - path: src/gnd/examples/literature/diagnostics/cases.json
    sha256: f38f07d2e37c91dcc2d0185da30f1a396fb02550f4277bb1ef424b028e7f56c4
  - path: src/gnd/examples/literature/diagnostics/case-outcomes.json
    sha256: d1e243b41cec7ca6f042229428dbb2b088fc456fd97eb4b1ae1cb1346c88fa96
  - path: src/gnd/examples/literature/diagnostics/measurement.json
    sha256: 75aa507694c9b005a39009a8468a4f84c5b41a3887398c950ae61aaca6669305
  - path: src/gnd/examples/literature/diagnostics/labels.json
    sha256: b95f3c72f2c119b5e31d035634fe8261c0d49e551132016d29d743c7d275418f
---

# Claim

**Delegated approval (auto=true), 2026-11-15.** The milestone chat delegates
LI3 corpus and amendment rulings. The four named pairs, flow matching
control and hostile-input exits are approved as declared in the bound
corpus. The synthetic measurement and its separate labels are frozen
before implementation or measurement. The signature clarification in the
bound experiment design applies to the local candidate function only.
The diagnostic report format keeps the original spec contract.

The corpus-first instrument and implementability check cover accepted
originals, a deliberate false-candidate mixture and a malformed input.
The initial run went red with nine failures because the example module was
absent. Review budget is one Claude Code phase-diff reviewer and zero
additional spec or corpus review rounds.

## Boundary

This ruling binds the corpus and the intended grading procedure.
Observed diagnostics and measured false discoveries belong in the phase
record.
