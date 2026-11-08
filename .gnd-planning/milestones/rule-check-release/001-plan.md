---
milestone: rule-check-release
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-07
gate:
  command: "ruling: owner approved .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md r2, sha256 97a94db5296c4b9bac2c3322afac4b664946f0a620df78f8bea39317d7bb4aad"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/rule-check-release-plan.md
    commit: c09dcbcc
    sha256: 97a94db5296c4b9bac2c3322afac4b664946f0a620df78f8bea39317d7bb4aad
  - path: .gnd-planning/milestones/rule-check-release/evidence/plan-review-r1/codex-review.md
    sha256: 40b990996620272a5a72809fb608c48242cc3f79029cfb98d90e009d870c51b6
---

# Claim

The owner approved plan r2 on 2026-11-07. This approves the milestone plan
only. It approves no phase spec: RR1's spec (`notes/phase-RR1-spec.md`) is a
blocked draft and needs experiment E1, the RL-D9 ruling and its own owner
gate before any code is written. It approves no publication of any kind.
`auto=false`.

The only later edit to the plan file is its status line, which records this
approval; the approved bytes are r2 at c09dcbcc.

## Gate output (verbatim)

Ruling, 2026-11-07, owner, answering "Approve plan r2 at the plan gate?":

    Approve r2

Preceding rulings: RL-D1 "0.2.0" and RL-D2 "Wait for FU2, FU3" (each in the
owner's own message here); RL-D0 and RL-D3 to RL-D9 "Approve all as proposed
(Recommended)", relayed by the session that started this one.

## Rulings recorded

| ID | Ruling |
|---|---|
| RL-D0 | one Codex review before the plan gate (ran over r1) |
| RL-D1 | version 0.2.0 |
| RL-D2 | the release waits for rule-check-followups FU2 and FU3; FU4 and FU5 do not gate |
| RL-D3 | one version section in the release notes, earlier sections as subsections |
| RL-D4 | install pins stay at 0.1.0 until publication |
| RL-D5 | the dossier states both publication routes; the plan chooses neither |
| RL-D6 | no GitHub prepare run in this plan; the owner may ask |
| RL-D7 | differing local build hashes do not block |
| RL-D8 | the RR2 spec approval selects the one release-acceptance file and lane |
| RL-D9 | deferred: ruled in the RR1 spec after experiment E1 |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over r1
(sha256 `52797ddb…`, commit dbf98447), disposition `revise`, 11 findings, all
checked against the repository, accepted and applied in r2
([record](evidence/plan-review-r1/codex-review.md)). The project's plan-review
bar is the maintained panel; the owner selected one reviewer (RL-D0). r2 was not
re-reviewed, and its repairs carry no review opinion.

## Boundary

- Nothing is published, tagged, uploaded or enabled; no workflow, environment,
  setting or PyPI configuration changed.
- Issue 118 stays open.
- RR2 does not start until FU2 and FU3 are on main (RL-D2).
