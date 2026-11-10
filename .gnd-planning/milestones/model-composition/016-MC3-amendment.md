---
milestone: model-composition
station: "MC3 measured corpus locator correction"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC3-amendment
date: 2026-11-10
gate:
  command: "ruling: delegated (auto=true) approve exact two-input correction bound by amendment manifest sha256 cfc836aca6b3d3abbe559e6195d9403e33142ca55d61d8b32a6adc2b48d0cd4b"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/model-composition/015-MC3-gate.md
    sha256: a7c3f738bc57927ed213c7563537176563af25f47a8938e6f56921e47d159c97
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/016-amendment-manifest.json
    sha256: cfc836aca6b3d3abbe559e6195d9403e33142ca55d61d8b32a6adc2b48d0cd4b
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/016-corpus-locator-red.json
    sha256: b267d22f3db18d804209e5b232795dc0448837aa301fc18fac972a22d819b9fc
  - path: tests/fixtures/mc-vocabulary/answers.json
    sha256: a5511a56355b8268bda19c2cb703c0e679738a91329419fba0fc46ef43eb9b54
---

# Claim

Delegated approval corrects only the two authored DELETE locators' canonical before hashes. The existing evolution digest algorithm and all sixteen approved outcome meanings are unchanged.

## Gate output and reproduction

Both original combined/flattened proposals refuse at operations.1: constraint locator does not bind the canonical before value. The exact input snapshots, observed parser messages and successor bytes are retained. Both corrected inputs parse after adding the new schema graph; no service/publication result is claimed.

## Refuted premise

The corpus author used the canonical artifact-file producer for an evolution constraint identity. That producer includes a final newline; the existing evolution identity producer does not. The schema reproduced the mistaken interchange assumption. The correction uses the existing canonical_sha256 function, preserving its historical convention rather than changing product code or teaching the validator to accept the wrong hash.

## Boundary

Authority is the named milestone auto delegation, not a personal owner reading. Record015, its gate manifest and approved spec/answer snapshots are unchanged; this append-only successor binds the two changed inputs. Candidate and vocabulary bytes, operation order, sixteen answers, single-review/one-confirmation budget and600/900 stop remain. No phase completion, merge, currency or milestone close is established. Partial schema source is still uncommitted and outside this correction commit.

## Open questions

- Implement and verify every admitted evolution/writer branch using the exact corrected inputs; retain the original red harness result as its own observed pre-implementation attempt.
- Review immediate neighbours of the eventual schema/service repairs within the already selected budget.
