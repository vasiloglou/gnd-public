---
milestone: release-0.3.0
station: "plan gate"
skill: start-milestone
scope: plan-gate
date: 2026-11-10
gates:
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (plan review over r1, prompt on stdin)"
    exit: 0
    output: "DISPOSITION: revise; P1 to P9"
  - command: "ruling: owner approved .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md sha256 45b0685bb069a0e7f9d2ef255e8258ada0cf116b3c3755c55e12f90a98039b8a"
    exit: "n/a -- ruling"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md
    commit: af7d5db4
    sha256: 45b0685bb069a0e7f9d2ef255e8258ada0cf116b3c3755c55e12f90a98039b8a
  - path: .gnd-planning/milestones/release-0.3.0/evidence/plan-review-r1/codex-review.md
    commit: af7d5db4
    sha256: 8b1d53f790cdadaed540fefa0f8a6103bf237781c6ad8e73667d06ec57c9c80d
---

# Claim

The owner approved plan r2 on 2026-11-10. This approves the milestone plan
only. It approves no phase spec: RN1's spec (`notes/phase-RN1-spec.md`) is a
blocked draft and needs experiment E1, the per-file handling ruling after it
and its own owner gate before any file changes. It approves no publication.
`auto=false`.

The only later edit to the plan file is its status line, which records this
approval; the approved bytes are r2 at af7d5db4.

## Gate output (verbatim)

Ruling, 2026-11-10, owner, in this session, answering "Approve plan r2 at the
plan gate?":

    Approve r2

Preceding rulings, each the owner's own message in this session, 2026-11-10:
RN-D1 "0.3.0 (Recommended)"; RN-D2 in part, "make sure you include PR 161 as
well"; RN-D0 and RN-D3 to RN-D11 "Approve as proposed".

## Rulings recorded

| ID | Ruling |
|---|---|
| RN-D0 | one reviewer in a different tool before the plan gate (ran over r1) |
| RN-D1 | version 0.3.0 |
| RN-D2 | the release includes PR 161 (on main at `2490dd77`); that nothing else gates is the approved plan's proposal |
| RN-D3 | one 0.3.0 notes section, Ossie first |
| RN-D4 | install pins stay at 0.2.0 until publication |
| RN-D5 | the milestone closes after publication; publication is owner acts, each on its own request; route as for 0.1.0 and 0.2.0 |
| RN-D6 | no GitHub prepare run unless the owner asks |
| RN-D7 | re-record version-bearing outputs as for 0.2.0; the refactor is carried to an issue; per-file handling ruled in the RN1 spec after E1 |
| RN-D8 | the RN2 spec approval selects the one release-acceptance file and lane |
| RN-D9 | five installed probes, each with a 0.2.0 control and a candidate behavior control |
| RN-D10 | fix both red tests on main in RN1; after the review the link fix registers the retained snapshots and changes no evidence |
| RN-D11 | opt-in lanes recorded as excluded |

## Review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only) over r1
(plan sha256 `f21e6bce…4a77`, spec `70418c41…7b3`). Disposition `revise`, 9
findings, each checked against the repository, all accepted and applied in r2
(plan §11; [retained output](evidence/plan-review-r1/codex-review.md)). The r1
bytes were uncommitted working-tree files and are not in history; the
reviewer's output confirms both digests, and no one else can check them. The
project's plan-review bar is the maintained panel; the owner selected one
reviewer (RN-D0). r2 was not re-reviewed, and its repairs carry no review
opinion.

The reviewer could not write files, run the full suite, or reach PyPI, the
GitHub environments endpoint or beast-3.

## Boundary

- Nothing is bumped, built, published, tagged, uploaded or enabled; no
  workflow, environment, setting or PyPI configuration changed.
- The plan's observed rows are dated 2026-11-10 and 2026-11-11 (UTC); PyPI
  availability of 0.3.0 is rechecked at the RN2 freeze and before upload.
- Two default-lane tests are red on main (plan N20, N26); RN1 owns both.
- The count of four unresolved links in two ossie snapshots (N26) is the
  reviewer's; this session reproduced the first link only.
