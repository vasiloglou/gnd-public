---
milestone: release-0.4.0
station: phase-RV1
scope: RV1-implementation-gate
date: 2026-11-17
gates:
  - command: "six E1 default-lane shards on beast-3 after the scratch version bump"
    exit: "1, 1, 1, 0, 1, 1"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.4.0/notes/phase-RV1-spec.md sha256 05ea75eb23cd937bea22ba861c4c03178e3cb52b1096cddf274f7a871bad3049"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/e1-summary.txt
    sha256: 00a84ca2a7762c4b20975a406a3c9f8b08f2d50f2bb38b24150e291e9d120022
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV1/e1-moved-bytes.txt
    sha256: d4641e81af7a1f3590e8e3cd1cc6924c545fa1ad7e74f2dd116cfbf581bafcdf
---

# RV1 measured implementation ruling

> Delegated approval (auto=true), 2026-11-17. Authority is the owner's
> release-0.4.0 auto invocation and the plan gate. Approved RV1 spec r3
> at SHA-256 05ea75eb23cd937bea22ba861c4c03178e3cb52b1096cddf274f7a871bad3049.
> Instrument: measured spec prose. Approve the release-page and synchronized
> field updates, retain the published 0.3.0 pins, and approve test-only
> repairs to the four measured consumers. Preserve all 12 recorded outputs.
> Budget: the focused direct, structure and docs gates, one six-shard
> default-lane verification and one independent phase diff review. The revised
> implementation estimate is 150 lines with a 225-line stop threshold.

The implementability sweep checked that each example output matches with the
existing narrow normalizer. The publication test fixture starts from a
known tagged state and exercises prior behavioral controls without depending
on the release being prepared. No production tool change is needed.

## Boundary

E1 demonstrates the effect of a version-only change. The finished RV1
candidate still owes focused verification, the full default lane and an
independent review.

## Open questions

- RV1 verification must reproduce the previously clean set other than the
  two known optional-wheel errors.
