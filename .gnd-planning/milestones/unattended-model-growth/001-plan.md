---
milestone: unattended-model-growth
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-07
gate:
  command: "ruling: owner approved .gnd-planning/milestones/unattended-model-growth/notes/unattended-model-growth-plan.md r1.2, sha256 f099eb2a86c0c3ca273dc19ad093c89283de8e158e7ffc2041e1c8ffe826d634"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/unattended-model-growth/notes/unattended-model-growth-plan.md
    commit: 314dc019
    sha256: f099eb2a86c0c3ca273dc19ad093c89283de8e158e7ffc2041e1c8ffe826d634
  - path: .gnd-planning/milestones/unattended-model-growth/notes/plan-review-r1-disposition.md
    commit: 314dc019
    sha256: 4270b596487114b11186198df47e40c8b2f9f5a4022679c255206a2bce6cdde9
  - path: .gnd-planning/milestones/unattended-model-growth/evidence/plan-review-r1/unattended-model-growth-plan.md.snapshot
    commit: 314dc019
---

# Claim

The owner approved plan r1.2 at the plan gate on 2026-11-07. This approves the
milestone plan only. It approves no phase spec: UG1's spec
(`notes/phase-UG1-spec.md`) needs its own owner gate before any code is
written, and UG2, UG3 and UG4 each need theirs. `auto=false`.

The approved bytes are r1.2 at commit `314dc019`. After this gate the plan file
received only status wording (its first line, the status paragraph, one
"Ready" sentence under UG1 and the revision history); every other byte is as
approved.

## Gate output (verbatim)

Ruling, 2026-11-07, owner, answering "PR 123: approve plan r1.2 at the plan
gate?":

    approved all

Authorization source: relayed to this session by the session that started it
(a cross-session message, 2026-11-07), which quoted the owner's reply. The
reply was not typed to this session and was not seen by it; the record cannot
be stronger than the relay. The question named the PR and the revision, not
the digest; the digest above is the plan file at `314dc019`, which is the
commit the question named.

Preceding rulings over r1.1, relayed the same way and recorded at plan §10
(column "Owner ruling", tag `(o1)`): UG-D2 (b), UG-D9 (b), UG-D3 (c); UG-D0,
UG-D1, UG-D4, UG-D5, UG-D6, UG-D7 and UG-D8 as proposed.

## What "approved all" covers

- The plan at r1.2, including §10's owner rulings as written. UG-D2 (b), UG-D3
  (c) and UG-D9 (b) are carried in the approved bytes; the review round asked
  that this record re-confirm them, and the approval of the revision that
  contains them is the confirmation available. The owner did not re-state them
  in this message.
- The phase order UG1, UG2, UG3, UG4, with UG2 and UG3 landing serially (§3).

## What it does not cover

- UG-Q6 (which statement in `project.md` governs the component index) and
  UG-Q7 (the issue-tracker labels) were not separately ruled and remain open
  owner questions. The plan applies the component-index reading it states;
  the labels stay out of the milestone text. Neither blocks UG1.
- A plan-review confirmation round was not run. Plan review round 1 read r1.1;
  r1.2 holds its repairs and has had no review opinion of its own. This
  approval adds none.

## Review

Instrument: four local reviewer agents (UG-D1 (a), ruled `(o1)`), one lens each,
over r1.1 (plan sha256 `b2678c57e677525771a0eb921cdf1d6e188bbb488aca1c827a09e8f13e7c9946`,
UG1 spec sha256 `e7523244e4ab00a1a85f05590c592228e9a340c6f422e5d413c729b8ae96531e`).
Verdicts: two approve-with-fixes, two request-changes; four blocking text
defects, all accurate and all applied in r1.2. No finding was rejected. The
maintained six-seat panel, which the project states as its bar, was not run.
Full dispositions: [plan-review-r1-disposition.md](notes/plan-review-r1-disposition.md);
the reviewed bytes are retained under `evidence/plan-review-r1/`.

## Boundary

- Approval of the plan is not approval of the UG1 spec or of any later phase's
  spec. Each has its own owner gate; no code before it.
- No commit to `main`, merge, release, publication or certification is
  authorized by this gate. PR 123 stays open; merge needs the owner's own
  authorization.
- No issue is closed or commented on by this record. The owner closes issues
  74, 75, 76 and 104 (UG-D0).
- The record is named `001-plan.md` (scope `plan`), as the shared contract and
  the most recent plan record in this repository do. `project.md` also lists
  `NNN-plan-gate.md`; the two are inconsistent in the repository and this
  milestone follows the contract name.
