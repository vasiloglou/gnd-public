---
milestone: literature-interop
station: phase-LX4-spec-gate
skill: "n/a -- repository development under process-phase"
scope: phase-LX4-spec-gate
date: 2026-11-15
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/literature-interop/notes/phase-LX4-spec.md sha256 73172d93049c4dd6eb2f5f262e081df6b31473a53f810882f82f8b16e989c8bc"
    exit: "n/a -- ruling"
  - command: "uv run pytest -q tests/test_lx4_literature_interop.py --tb=short"
    exit: 1
    output: "23 errors in 0.27s"
evidence:
  - path: .gnd-planning/milestones/literature-interop/notes/phase-LX4-spec.md
    sha256: 73172d93049c4dd6eb2f5f262e081df6b31473a53f810882f82f8b16e989c8bc
  - path: tests/test_lx4_literature_interop.py
    sha256: 523434d357185f59ee061f24b33d02c5bd239f90782b4e4b9e78ef1b1c0dc9c9
  - path: tests/fixtures/lx4-literature-interop/expected.json
    sha256: 9cd0b3812e42d2ac548e766ca04732f6eae5b4107a714c4c91ef436df4a31378
  - path: tests/fixtures/lx4-literature-interop/README.md
    sha256: 5d4eced9650329f7913b493fb65a35a6df87f4ac8ed3d84575ac89ddf37375f7
---

# Claim

The owner authorized delegated rulings with
`process-milestone literature-interop auto`. The ruling approves decisions
D1–D5 and the exact public corpus expectations above. The phase has a separate
independent diff review requirement.

## Implementability

The probe loaded roots with different model IDs and equal shared vocabulary
digests. Extraction passed on the extraction root and refused the checking
root. Composed check, witness v4 and replay passed with the checking root,
and a larger temporal allowance changed check to exit 1 with one violation.
The existing LI2 evidence route stamped the same decision on both source
occurrences with the catalog present. Original-root verify accepted the
document-bound extraction and original anchors. Fidelity's existing kernel
accepted this evidence when the include admission guard was bypassed in a
scratch probe. LX4 routes it through authenticated bundle verification.

## Gate output

    23 errors in 0.27s

All test setups fail on the missing integrated example module at the
LX3 completion commit. The corpus pins expected run artifacts and refusal
controls to make the runtime changes measurable.

## Boundary

This gate authorizes implementation within the stated spec. Product execution
and independent review remain subsequent evidence.

## Open questions

- None at the spec gate.
