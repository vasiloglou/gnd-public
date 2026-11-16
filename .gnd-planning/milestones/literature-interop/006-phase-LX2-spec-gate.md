---
milestone: literature-interop
station: phase-LX2-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LX2-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX2-spec.md sha256 763c8de32f74d90a3b9a2f6cf9dcc13b9cbacdfb1de81a5b1c129904312308ad"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lx2_witness_flattening.py --tb=short"
    exit: 1
evidence:
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX2-spec.md
    sha256: 763c8de32f74d90a3b9a2f6cf9dcc13b9cbacdfb1de81a5b1c129904312308ad
  - path: tests/test_lx2_witness_flattening.py
    sha256: 0c5d88bb6d23255a82f3641bd5334727d130571867ab1c2b102b30613d7cb7ae
  - path: tests/fixtures/lx2-witness-flattening/README.md
    sha256: 66de950b2d63dc4173b072e0806954b226db88f61868bf60cdcdb61203c17ea7
  - path: tests/fixtures/lx2-witness-flattening/expected.json
    sha256: 5eb62aef78678b89f3e5b552444a5d011149a83f5f9505bfb6e77de851bbf578
---

# Claim

Approve the LX2 spec and corpus under the named auto delegation. The
corpus exits 1 against the predecessor, as expected for the absent route.

## Ruling and implementability

ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX2-spec.md sha256 763c8de32f74d90a3b9a2f6cf9dcc13b9cbacdfb1de81a5b1c129904312308ad

**Delegated approval (auto=true), 2026-11-15.** Authority is the owner's
`process-milestone literature-interop auto` instruction. Decisions D1–D4
and the exact corpus are approved. The approval instrument is corpus-first.
The project phase-diff instrument is selected for completion and needs
its own invocation authority. The spec has no paid review.

The existing evaluator proved the successor root's target from the LX1
flat artifact and returned one base node and one rule node. The public
composition route wrote an authentic three-fact reference-free record over
the authored root. V2 producer bytes were equal on two fresh runs. The
LX2 corpus can exercise root and include origins and mutate one axis at a
time without requiring changes to inference or composition.

## Gate output

    12 failed, 1 passed in 6.43s

The phase-base path consumer refuses includes and lacks the paired CLI
options. The exact pre-change v2 producer and replay control passes.

## Boundary

The red harness binds expected outcomes. Runtime verification, independent
review and phase closure remain separate.

## Open questions

- None at the spec gate.
