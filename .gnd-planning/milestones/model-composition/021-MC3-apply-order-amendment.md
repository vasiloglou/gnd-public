---
milestone: model-composition
station: "MC3 verified include apply ordering"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC3-apply-order-amendment
date: 2026-11-10
gate:
  command: "delegated approval (auto=true): MC3 a3 implementability sweep and exact spec snapshot"
  exit: "n/a -- delegated ruling before dependent implementation"
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/021-apply-order-gate.json
    sha256: fe4bca25b46ecbdb3c0fa3dc0b7b6f7a897c4b0d63c6ac2cf508620bf8798f44
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/021-approved-spec.md
    sha256: 5e486fdf703085f6aed58ce0c1a96459f3b18f00687b5ed55ad302ac79c75d7a
---

# Claim

The exact a3 spec snapshot was approved under the owner's explicit named milestone auto delegation before its dependent edits. Its snapshot digest was independently reconstructed and matched the saved gate digest before retention. This ruling was written locally before implementation and committed with the candidate; it does not claim an earlier gate commit.

## Decision and implementability

The old raw operations gate cannot establish included ownership without verified dependency provenance. For include-bearing apply, require snapshot/unsupported-route admission, check the live authored CAS, load authenticated old history and live untouched dependencies, check ownership before operations gating, then replay, candidate footprint, validation, D12/policy, snapshot/radius equality and staging. Reverify the candidate after destination checks immediately before CAS. Retry and finalize reverify before a positive return. Include-free ordering and all approved corpus answers stay binding. Prior gates015/016/018 remain immutable; the1400 source/1400 test-support stop and one Codex CLI review plus at most one confirmation remain.

## Owner documentation reaction

The owner answered “Yes, this explains it” to Fable's shared expense policies story. This accepts that direction for final MC4. It is not a merge decision or byte approval; the actual documentation checkpoint and its correction are retained on PR155. Final MC4 must incorporate this reaction.

## Boundary

MC3 is still in execution. This amendment does not establish passing gates, independent review, phase completion, merge, publication or certification. The source, tests and final focused evidence must be audited at the actual candidate.

## Open questions

- Finish MC3 verification/review and submit its fixed head for the owner's merge decision.
- Integrate the accepted expense-story direction into final MC4 and complete the actual milestone exit predicates.
