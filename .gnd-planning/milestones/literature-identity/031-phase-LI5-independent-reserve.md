---
milestone: literature-identity
station: phase-LI5-independent-reserve
skill: "n/a -- repository development under process-phase"
scope: phase-LI5-independent-reserve
date: 2026-11-15
gates:
  - command: "uv run --no-sync python -m gnd.examples.literature.lineage_run score MODEL BLIND-RUN LOCAL-KEY"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/literature-identity/evidence/LI5/independent-reserve-v1.json
    sha256: a553f8a67c019bf6700342b3fa212746138fe24d13db579cc4e42f715a3d64ec
---

# Claim

The first score on the fresh, owner-approved LI5 reserve exited 0.
It retained the supported path and excluded both false paths under
the pinned LI5 model, admission and composition routes, and scorer.

## Gate output

The score exited 0. Its retained aggregate is
`"supported": [1, 1], "excluded": [2, 2]`.
The exact local command stdout contains private case IDs. It has
SHA-256 `5a46473f724a9d2c79662c8ed9e2583bdc99440b216c74398cb928daec1d9c0a`
and remains with the original key, source packet and annotation
outputs outside Git. The tracked aggregate removes per-case data.

| Measurement | Supported kept | False excluded | Score exit |
|---|---:|---:|---:|
| Original reserve, first score | 0/1 | 2/2 | 1 |
| Original reserve, post-feedback correction | 1/1 | 2/2 | 0 |
| Fresh reserve, first score | 1/1 | 2/2 | 0 |

## Independence and recovery

The owner approved the [protocol](027-phase-LI5-independent-reserve-spec-gate.md)
and then the exact [sealed corpus](028-phase-LI5-independent-reserve-corpus-gate.md).
The fresh set has four source works that were outside the development
and original reserved sets. Astra used a source-only prompt through an
isolated session with the repository and private custodian directory
unreadable.

The first annotation failed assembly before scoring. The
[refusal record](029-phase-LI5-independent-reserve-assembly.md) preserves
that result. The next annotation omitted one resolution reference that
could never bind to an admitted assertion. Astra received the general
input rule and its own response, with the key, cases and score still
sealed. Comparison against the actual admission output verified that
every original statement and the valid decision stayed fixed.
[Record 030](030-phase-LI5-independent-reserve-freeze.md) binds the
executable annotation and composition before the one score. The frozen
model, path policy, rubric, scorer, and answer key were used unchanged.

## Refactoring review

The work reused the existing admission, composition and witness-based
score commands. It added no product code or public schema.

## Boundary

The first executable fresh-reserve score meets the numerical L1
threshold on this three-case smoke set. It is a separate measurement
from the original key-based failure and correction. The L1 evidence
can now be reviewed for a new milestone ruling. The
[prior close refusal](026-milestone-close.md) remains part of the
record. This measurement grants no acceptance or delivery authority
and supplies no generalization or host-scale evidence.

## Open questions

- Run the authorized independent close review over this distinct
  evidence when selected and record the new close ruling.
