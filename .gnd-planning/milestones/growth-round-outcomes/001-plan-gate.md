---
milestone: growth-round-outcomes
station: "plan gate"
skill: "n/a -- repository development, not a gnd-solve station over a domain model; process-milestone auto=true"
scope: plan-gate
date: 2026-11-23
gate:
  command: "ruling: delegated approval (auto=true) of .gnd-planning/milestones/growth-round-outcomes/notes/growth-round-outcomes-plan.md r4 sha256 b107bd366101719a7cc997a6d5d4212dea5dc80f5d121c4dec3fc8b669007431"
  exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/growth-round-outcomes/notes/growth-round-outcomes-plan.md
    sha256: b107bd366101719a7cc997a6d5d4212dea5dc80f5d121c4dec3fc8b669007431
  - path: .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r1/PANEL-REVIEW.md
    sha256: 97e194c06a4afb58f2653fc902f7658ddfa2652d06a384fc15eb8980df06988c
  - path: .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r1/disposition.md
    sha256: 573bd8f21f59cfa9782fce93bc31f14d46e737f82d92eded8f3900d28039a9b1
  - path: .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r2/PANEL-REVIEW.md
    sha256: 9cd9c6fde6187b16e71b8e8260d629a647218240209b3f15b66cc853d018e5f2
  - path: .gnd-planning/milestones/growth-round-outcomes/evidence/plan-review-r2/disposition.md
    sha256: 3feccf376bd18aabcd471f14fe73e13eb5365e6e298811155caf6d8fdad03aa5
---

# Claim

Plan r4 of growth-round-outcomes is approved by **delegated approval
(auto=true)** on 2026-11-23, with D1–D6 and D9 ruled under that delegation
as written below, and D7 and D8 ruled by the owner. The ruling approves the
plan only. Each phase spec has its own gate; GO1's draft spec is not approved
here.

This is a delegated ruling taken by the `process-milestone` session under the
owner's delegation. It is not the owner's personal reading of the plan.

## Authorization

- **Delegation.** The owner asked that growth-round-outcomes "should ... start
  with /process-milestone auto" (relayed to this session by the session that
  started it, 2026-11-23). Scope: this milestone only. It covers plan, spec
  and close rulings and amendments. It does not cover merge, release,
  publication, certification or paid calls beyond the instrument the owner
  selected.
- **D7**, ruled by the owner, relayed by the coordinating session: asked
  which plan and close review growth-round-outcomes and
  literature-reading-reference should use, the owner chose **"Full panel,
  both"**.
- **D8**, ruled by the owner, relayed by the coordinating session: asked how
  each phase diff should be reviewed, the owner chose **"Review helper,
  both"**.
- The owner approved the launch of the panel in this session ("Approve,
  launch it") and ran the round-1 command in the terminal pane.

## Implementability sweep (before the ruling)

Read the whole of r4 against the code at `89ffeee8` (`main` `11a7ebf7` plus
planning commits; nothing under `src`, `tests` or `docs` differs from
`548b9a1d`). Every phase has a homes row, a criteria row, a focused lane and
a start condition. Two contradictions the r4 repairs had introduced were
found and repaired before this ruling (`admitted` defined two ways; GO2-C1
against `unassessed`). The graph is acyclic under D6 as ruled. GO1 needs no
ruling beyond this gate. GO2–GO5 remain outlines whose specs carry the open
questions of §10.

## Rulings recorded

| ID | Ruling | By |
|---|---|---|
| D1 | (a) as r4 writes it: policy, candidate-validation and D-12 refusals, each tied to its operation where the gate can locate the element, collected in one pass; a refusal the gate cannot locate is a whole-proposal refusal and every operation is `unassessed`; `admitted` means every gate ran and none refused | delegated (auto=true) |
| D2 | (a) as r4 writes it: an optional `operation_outcomes` preview field, omitted when unset, no schema version move; a separate outcome report for a candidate that does not validate | delegated (auto=true) |
| D3 | (a): a reply names a reused fact type by its id only; rows for it go under the existing id when the document adds rows | delegated (auto=true) |
| D4 | (a) as r4 writes it: GND computes the summary from the host's round file, the proposal and preview or outcome report, and the evolution record | delegated (auto=true) |
| D5 | (a): a library function beside `candidate_document` | delegated (auto=true) |
| D6 | yes, binding: GO1 ships by its own pull request before VG2 starts | delegated (auto=true) |
| D7 | "Full panel, both": the full maintained GND panel for plan review and close review | owner |
| D8 | "Review helper, both": one reviewer in a different tool per phase diff | owner |
| D9 | out of GO1 (GO1-D4 (b)): the loader's double parse is a maintenance pass of its own, offered to the owner after GO1; GO1 stays inside `gnd evolve` | delegated (auto=true) |

Budget: plan review two rounds, spent. Each phase diff: one reviewer
(D8), at most two rounds under the bounded convergence rules. Close review:
the full panel, one round, a second only if the first blocks.

## Plan review

The instrument was the full GND panel at xhigh effort (D7). Two rounds ran,
both reached quorum. Both are advisory.

- Round 1 read r2 (sha256 `a041b21d…17ba`): five of six seats (Qwen timed
  out). 8 agreed groups, 5 single-reviewer concerns, 5 groups high. All
  reproduced, none rejected; r3 applies them `(p1)`.
- Round 2 read r3 (sha256 `2d9e62f8…8d48`): three of six seats (Gemini and
  Kimi malformed, Qwen timed out). 2 agreed groups, 10 single-reviewer
  concerns; 9 of 12 attack text the r3 repairs created. All reproduced;
  r4 applies them `(p2)`.

**No reviewer has read r4.** Its `(p2)` changes carry no review opinion.
The ones that are more than wording: GO2's outcome report carries the before
model and an `unassessed` verdict for unreached gates; `apply` replays the
outcomes setting; GO3 adds an optional origin field to the proposal; GO5
reads the evolution record for elements added; GO1's write check runs as a
verify mode over the whole GO1 lane.

## Boundary -- what this result did NOT establish

- It is a ruling, not a review opinion. r4 has no reviewer.
- It approves no spec. GO1's draft is next; GO2–GO5 have no spec.
- It grants no merge, release or publication.
- It rules nothing in reviewed-vocabulary-growth, literature-host-interfaces
  or literature-reading-reference. The cross-milestone order belongs to the
  coordinating session; each phase start sends it "READY <phase>".
