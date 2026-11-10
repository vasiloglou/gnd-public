---
milestone: model-composition
station: "MC1 repair ruling"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC1-repair-ruling
date: 2026-11-09
gate:
  command: "ruling: delegated (auto=true) amended MC1 spec sha256 f06505f3194bf191d9d3318ad37f007d0dac10b80d3bb0a56fdcaf1d88ee6662"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/model-composition/evidence/MC1/005-approved-spec.md
    sha256: f06505f3194bf191d9d3318ad37f007d0dac10b80d3bb0a56fdcaf1d88ee6662
---

# Claim

Delegated approval (auto=true) adopts MC1 r5's reproduced repairs and explicit
compatibility decisions under the owner's current named milestone delegation.

## Gate output (verbatim)

Delegated ruling, 2026-11-09: Approve R1-R9 repairs and r5's ownership,
clone-refusal, digest-parity and guard/refusal-metadata clarifications.
Retain the 1100-source/1900-test stop, all prior rulings and one remaining
focused independent confirmation. No new report version is selected.

## Boundary

This is a delegated ruling, not the owner's personal reading of r5. The
frozen full baseline and lint gates are nonzero and remain honestly reported;
candidate comparison and independent confirmation are still owed. This record
neither completes MC1 nor authorizes merge, publication or certification.

## Open questions

- Close: repair the plan's guard/hash wording from this record without
  weakening actual positive-currency verification.
- Preserve/dispose baseline known reds separately from phase regressions.
