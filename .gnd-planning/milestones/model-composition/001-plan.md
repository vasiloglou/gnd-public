---
milestone: model-composition
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-09
gate:
  command: "ruling: owner approved .gnd-planning/milestones/model-composition/notes/model-composition-plan.md r3, sha256 2923a34ec2531abdb0f1b1771bfa6037e88ab26c388247f93aa2f9b3cd1ed9fd"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md
    sha256: 2923a34ec2531abdb0f1b1771bfa6037e88ab26c388247f93aa2f9b3cd1ed9fd
  - path: .gnd-planning/milestones/model-composition/evidence/plan-review-r1/codex-review.md
  - path: .gnd-planning/milestones/model-composition/evidence/plan-review-r2/codex-review.md
---

# Claim

The owner approved plan r3 on 2026-11-09 and ruled MD1-MD16 as proposed.
This approves the milestone plan only. It approves no phase spec: MC1's spec
(`notes/phase-MC1-spec.md`, r3) needs its own owner gate, with D1-D8, before
any code is written. `auto=false`.

The approved bytes are r3, sha256 `2923a34e…1ed9fd`, uncommitted when
approved. The only later edits to the plan file are its status line and the
rulings written into the §10 decision rows; neither changes a proposal.

## Gate output (verbatim)

Ruling, 2026-11-09, owner, answering "How do you rule on MD1–MD16 at the
plan gate?":

    Approve as proposed

Preceding rulings: MD0, answering "How should plan r1 be reviewed before the
gate (MD0)?": `Codex review`; round two, answering "Run a second Codex round
over r2, or take r2 to the plan gate?": `Codex review r2`.

## Rulings recorded

| ID | Ruling |
|---|---|
| MD0 | one Codex reviewer; the owner selected a second round |
| MD1 | `includes:` list of `{id, path, sha256}`, at most 8 |
| MD2 | new model version 5; every version-gated rule widens to admit 5 |
| MD3 | included file: standalone-valid, object types, fact types, constraints, deontic notes only; depth one |
| MD4 | included constraints apply, read-only |
| MD5 | no override: any duplicate id refuses |
| MD6 | no new identity function; identities over composed content, measured in MC1 |
| MD7 | unresolvable routes refuse with `include:unsupported-route` |
| MD8 | evolve operation `repin-include` with blast radius |
| MD9 | verbalization of the composition plus one header line per include |
| MD10 | `fact_type_constraints:` section for inline constraints on included fact types |
| MD11 | include-bearing files may omit `object_types` and `fact_types` |
| MD12 | versioned vocabulary paths, supplied `--previous-include`, snapshots in evolve evidence |
| MD13 | invalid re-pin: analysis-only preview, then a combined valid proposal |
| MD14 | no new aggregate cap unless MC1's scaling test shows superlinear cost |
| MD15 | MC1 ships the route guards |
| MD16 | the includer's `source` governs; no unattended-mode included files |

## Review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only, prompt
on stdin), two rounds over the same seat.

| Round | Reviewed bytes | Disposition | Findings | Applied in |
|---|---|---|---|---|
| 1 | plan r1 `bd661eee…`, spec r1 `b6ebc5db…` | revise | 18 (11 blocking), all reproduced | r2 |
| 2 | plan r2 `2dc91f4e…`, spec r2 `e8f6cf85…` | revise | 13 (5 blocking), all reproduced | r3 |

Reviewed bytes are retained beside each review because they were uncommitted
when reviewed. The project's plan-review bar is the maintained panel; the
owner selected one reviewer (MD0). The convergence stop rule fired after
round two (self-inflicted ratio 0.85; plan §11), and the round budget was not
declared before round two, as recorded there.

## Boundary

- r3's repairs carry no review opinion.
- The MC1 spec r3 is a draft; its decisions D1-D8 are open.
- Nothing in this milestone is committed or published by this record; commit
  and PR follow the repository's branch-and-PR rule.
