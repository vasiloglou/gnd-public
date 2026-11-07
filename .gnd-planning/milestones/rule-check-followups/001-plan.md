---
milestone: rule-check-followups
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-07
gate:
  command: "ruling: owner approved .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md r3, sha256 3f54277bad78e6ed25352ad49968b7cb803fb9cca8aeb3b6465fa885fbe895fe"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/rule-check-followups/notes/rule-check-followups-plan.md
    commit: a08c29dd
    sha256: 3f54277bad78e6ed25352ad49968b7cb803fb9cca8aeb3b6465fa885fbe895fe
  - path: .gnd-planning/milestones/rule-check-followups/evidence/plan-review-r2/codex-review.md
---

# Claim

The owner approved plan r3 on 2026-11-07. This approves the milestone plan
only. It approves no phase spec: FU1's spec (`notes/phase-FU1-spec.md`)
needs its own owner gate before any code is written. `auto=false`.

The only later edit to the plan file is its status line, which records this
approval; the approved bytes are r3 at a08c29dd.

## Gate output (verbatim)

Ruling, 2026-11-07, owner, answering "Approve plan r3 at the plan gate?":

    Approve r3

Preceding ruling over r1 (commit 3efdd2cd), answering "How do you rule on
the plan's decisions RF-D0 and FD1–FD5?":

    Approve all as proposed

## Rulings recorded

| ID | Ruling |
|---|---|
| RF-D0 | one Codex review before the plan gate (ran over r2) |
| FD1 | issue 111 split out to its own milestone |
| FD2 | issue 112 split out to its own milestone |
| FD3 | FU1 widens the version-7 reason enums to version 15's set |
| FD4 | FU4 widens measured margins (after scoping the survivor check, r3) |
| FD5 | FU5 retires the helpers under RF-D5 |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over r2
(sha256 `6e0d031a…`), disposition `block`, 6 findings, all accurate and all
applied in r3: [codex-review.md](evidence/plan-review-r2/codex-review.md).
The project's plan-review bar is the maintained panel; the owner selected one
reviewer (RF-D0). r3 was not re-reviewed.

## Boundary

- r3's repairs carry no review opinion.
- Issues 111 and 112 remain open, outside this milestone.
