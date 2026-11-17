---
milestone: release-0.4.0
station: phase-RV1
scope: RV1-diagnostic-gate
date: 2026-11-17
gates:
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.4.0/notes/phase-RV1-spec.md sha256 3d0f672bbe9a08b89bec7daecced4fcaf166a88ab4b70a6c12f037168dc3ded1"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/e1-shards.sh
    sha256: 4247e2c666deb57f3be8e3d16571e9ee6417e636a245e9c9ecec26e41fb90caf
---

# RV1 diagnostic ruling

> Delegated approval (auto=true), 2026-11-17. Authority is the owner's
> release-0.4.0 auto invocation and the committed plan gate. Approved
> the RV1 diagnostic protocol at SHA-256 3d0f672bbe9a08b89bec7daecced4fcaf166a88ab4b70a6c12f037168dc3ded1.
> Instrument: spec prose and the digest-bound scratch runner. Budget:
> one six-shard default-lane diagnostic on beast-3 against V13, with
> the installed distribution and historical lanes excluded. Approve
> the proposed diagnostic order and keep published install pins.
> The measured disposition and candidate edits require the second
> RV1 ruling under the same delegation.

## Boundary

This ruling authorizes E1 and the inventory only. RV1 implementation and the
phase diff review follow the measured spec gate.

## Open questions

- E1 supplies measured affected ids and the changed-output disposition.
