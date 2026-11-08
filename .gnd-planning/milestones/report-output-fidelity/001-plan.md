---
milestone: report-output-fidelity
station: "plan gate"
skill: start-milestone
scope: plan
date: 2026-11-07
gate:
  command: "ruling: owner approved .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md r3, sha256 421e3d5ef5b96c6167a6f94fd5e8bed2580d00f5485a271044e2a73a80a91fdb"
  exit: n/a -- ruling
evidence:
  - path: .gnd-planning/milestones/report-output-fidelity/notes/report-output-fidelity-plan.md
    commit: 71ee20eb
    sha256: 421e3d5ef5b96c6167a6f94fd5e8bed2580d00f5485a271044e2a73a80a91fdb
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/plan-review-r2/codex-review.md
    sha256: 31af3df66e68feb1e7240423cbc0c5f377ae16a992d7bf1729cbb2c68b1b36ff
  - path: .gnd-planning/milestones/report-output-fidelity/evidence/plan-review-r2/triage.md
---

# Claim

The owner approved plan r3 on 2026-11-07. This approves the milestone plan
only. It approves no phase spec: ROF1's spec (`notes/phase-ROF1-spec.md`, a
draft) needs its approval corpus authored and its own owner gate before any
code is written. `auto=false`.

The only later edits to the plan file are its status line and the D7 ruling
row, which record this gate; the approved bytes are r3 at 71ee20eb.

## Gate output (verbatim)

Ruling, 2026-11-07, owner, answering "Approve plan r3 at the plan gate?":

    Approve r3, D7 (a)

Preceding ruling, 2026-11-07, owner (recorded in the plan's section 10),
answering "How do you rule on RF-D0 and D1–D6 in the plan?":

    Approve as proposed

## Rulings recorded

| ID | Ruling |
|---|---|
| RF-D0 | one Codex review before the plan gate (ran over r2) |
| D1 | 112 chain first, then 111 |
| D2 | omit the empty `REDACTION applied:` header on the temporal-only route |
| D3 | no canonical-identity emission in reports in this milestone; re-ask after ROF4 |
| D4 | `identity_version: 2`, narrowed in r3 (review P2) to models without `reference_populations`; approved with r3 |
| D5 | producer surface decided in the ROF3 spec |
| D6 | no index review |
| D7 | generated Pyrel plans keep the legacy `MODEL_DIGEST`: byte-identical, canonical pins refused by generated plans, documented limitation |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over r2
(plan sha256 `dfc559bc…`) and ROF1 spec r1 (sha256 `f576b349…`), disposition
`block`, 10 findings, all verified and all applied in r3 and spec r2:
[codex-review.md](evidence/plan-review-r2/codex-review.md),
[triage.md](evidence/plan-review-r2/triage.md). The project's plan-review bar
is the maintained panel; the owner selected one reviewer (RF-D0). The
reviewer could not run the suite. r3 and spec r2 were not re-reviewed.

## Boundary

- r3's repairs and spec r2 carry no review opinion.
- No phase spec is approved. Issues 111 and 112 remain open; 111 stays open
  as partially addressed unless ROF5 delivers (plan predicate 4).
- Changes to this plan after the gate take a new record with the next number.
