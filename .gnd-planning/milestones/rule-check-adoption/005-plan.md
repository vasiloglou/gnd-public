---
milestone: rule-check-adoption
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-06
gate:
  command: "ruling: owner approved .gnd-planning/milestones/rule-check-adoption/notes/rule-check-adoption-plan.md sha256 6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/rule-check-adoption/notes/rule-check-adoption-plan.md
    commit: 208f709f
    sha256: 6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138
  - path: .gnd-planning/milestones/rule-check-adoption/001-panel.md
  - path: .gnd-planning/milestones/rule-check-adoption/002-review.md
  - path: .gnd-planning/milestones/rule-check-adoption/003-review.md
  - path: .gnd-planning/milestones/rule-check-adoption/004-review.md
---

# Claim

The owner approved plan r6 as written, with every §10 proposal, on
2026-11-06. This approves the milestone plan only. It approves no phase
spec: RC1 spec r6 (`notes/phase-RC1-spec.md`, sha256
`b418517c074df116c859d8ed3623cd29e98e87602f1e801ab927c3f764d3d851`) still
needs its own owner gate before any code is written. `auto=false`.

## Gate output (verbatim)

Ruling, 2026-11-06, owner, in this planning session, answering the plan-gate
question "How do you rule on plan r6 at the plan gate?":

    Approve r6 as written (Recommended)

and the separate RC-D9 question "what should --baseline do with constraints
that have no declared id?":

    Proceed and warn (Recommended)

Preceding ruling on RC-D16 ("Review r6 before the plan gate?"), same day:

    Go to plan gate

## Rulings recorded

| ID | Ruling |
|---|---|
| RC-D0 | "One reviewer on r3" |
| RC-D1 | approved as proposed: RC1 gate after PR 99 merges, else the merge-base record names inherited failures |
| RC-D2 | approved: version 15 behind `--rule-ids`; version 7 frozen |
| RC-D3 | approved: one row per in-group edge; groups in the message |
| RC-D4 | approved: id-less constraints keyed by positional address |
| RC-D5 | approved: standing-only exits 0, `acceptance_ready: true` |
| RC-D6 | approved: alethic unchecked in either run exits 4, no novelty claim |
| RC-D7 | approved: run-wide `--allow-vacuous` only |
| RC-D8 | approved: `tool-output` with optional `producer` (1-200 chars) |
| RC-D9 | "Proceed and warn" |
| RC-D10 | approved: one shared Tarjan home, both existing callers moved in RC2 |
| RC-D11 | "Commit, r5 with refusal": `--baseline` refuses models with structured derivations |
| RC-D12 | approved: `remedy: null` when undeclared |
| RC-D13 | approved: deontic unchecked does not block; counted in `undecided` |
| RC-D14 | "Codex re-check r4" |
| RC-D15 | "Codex re-check r5" |
| RC-D16 | "Go to plan gate" (r6 not reviewed) |
| RC-D17 | approved: the version-7 schema defect (O29) is fixed outside this milestone; the owner started that work as its own session the same day |

## Plan review

| Revision | Instrument | Reviewed sha256 | Result | Record |
|---|---|---|---|---|
| r2 | full panel, six of six, xhigh | `526d2ff1…610d631f` | 3 block, 3 revise; 9 agreed groups, 13 divergent, 22 fixes; all dispositioned in r3 §11 | [001-panel.md](001-panel.md) |
| r3 | one reviewer, Codex gpt-6-sol xhigh | `f00ffcf3…a59e` | block, 13 findings, all reproduced; dispositioned in r4 §12 | [002-review.md](002-review.md) |
| r4 | Codex re-check | `a69e3d3b…15f2` | block, 4 findings, all reproduced; dispositioned in r5 §13 | [003-review.md](003-review.md) |
| r5 | Codex re-check | `e8a3a154…0a31` | block, 2 findings, both reproduced; dispositioned in r6 §14 | [004-review.md](004-review.md) |
| r6 | none | `6f0056b3…f138` | not reviewed, by the owner's RC-D16 ruling | — |

## Boundary

The approved bytes (r6) carry no review opinion: every review covered an
earlier revision, and the last reviewer verdict on record is `block` over
r5, whose two findings r6 repairs without re-review. The project's
plan-review bar (the maintained panel) was met over r2 only; the owner set
it aside for r3 to r6 by RC-D0, RC-D14, RC-D15 and RC-D16. Approval of the
plan is not approval of the RC1 spec, not merge authority, and not
publication authority.
