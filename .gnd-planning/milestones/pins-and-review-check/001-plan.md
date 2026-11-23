---
milestone: pins-and-review-check
station: "plan gate"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: plan
date: 2026-11-23
gate:
  command: "ruling: owner approved .gnd-planning/milestones/pins-and-review-check/notes/pins-and-review-check-plan.md sha256 e4a8a65f7a8b410bda24e5710e54027118d0af2d56cfd380d96d873d05e46f3e"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/pins-and-review-check/notes/pins-and-review-check-plan.md
    sha256: e4a8a65f7a8b410bda24e5710e54027118d0af2d56cfd380d96d873d05e46f3e
---

# Claim

Plan r1 of pins-and-review-check is approved by the owner on 2026-11-23,
with D1–D5 ruled as proposed. The ruling approves the plan only. PF1's draft
spec has its own gate and is not approved here.

## Gate output (verbatim)

The owner, in the Code session that wrote the plan, 2026-11-23: "approve the
plan, name the milestones you added on the roadmap".

The plan bytes the ruling binds differ from the bytes the owner read in
[PR 248](https://github.com/vasiloglou/gnd-public/pull/248) at `e3edbd75`
only in the status line and the sentence above the §10 table, which record
this approval.

## Rulings recorded

| ID | Ruling | By |
|---|---|---|
| D1 | yes: one run of the default lane on beast-3 at PF1's base before any edit; red files that are not inventory copies are listed and reported, not repaired | owner, as proposed |
| D2 | (a): `codex` as PF2's reviewer, about eight diffs, one run each | owner, as proposed |
| D3 | one reviewer in a different tool (the review helper) for plan, phase and close review. This waives, for this milestone only, the panel bar `project.md` sets for plan review and milestone close | owner, as proposed |
| D4 | one pull request per phase | owner, as proposed |
| D5 | (a): `tests/test_public_distribution_runtime.py` keeps its pin of a released wheel as a named exception | owner, as proposed |

## Plan review

None ran. No review instrument has read plan r1 at any digest. The owner
approved it unreviewed. D3 selects one reviewer in a different tool for any
later review; none was asked to read the plan before this ruling.

## Boundary -- what this result did NOT establish

- It is a ruling, not a review opinion.
- It approves no spec. PF1's draft is next; PF2 has no spec.
- It grants no merge. Merging PR 248 stays with the owner.
- It does not change `project.md`. The D3 waiver binds this milestone only.
