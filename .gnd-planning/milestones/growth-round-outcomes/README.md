# Growth round outcomes

Plan r4, 2026-11-23, for
[issue #228](https://github.com/vasiloglou/gnd-public/issues/228) and
[issue #227](https://github.com/vasiloglou/gnd-public/issues/227).
**Approved by delegated ruling (auto=true)** in
[001-plan-gate.md](001-plan-gate.md), after two rounds of the full GND
panel (D7, the owner's "Full panel, both"): [round 1](evidence/plan-review-r1/disposition.md)
over r2, [round 2](evidence/plan-review-r2/disposition.md) over r3. No
reviewer has read r4.

| Phase | Deliverable | State |
|---|---|---|
| GO1 | `gnd evolve` parses each model text once per invocation: 22 parses become at most 3 in `apply` (#228) | done and merged: [002-phase-GO1.md](002-phase-GO1.md); `apply` parses 2 times where it parsed 22 |
| GO2 | `gnd evolve preview` reports an outcome for every operation of a proposal (#227) | done on its branch: [003-phase-GO2.md](003-phase-GO2.md); two review rounds, all findings fixed; pull request for GO2–GO5, not merged |
| GO3 | the admitted part of a proposal as a new proposal, with one call (#227) | done on its branch: [004-phase-GO3.md](004-phase-GO3.md); `gnd.discover.narrow.narrow_proposal`; same pull request |
| GO4 | `unattended-growth.md` says what a reply carries for a fact type it reuses (#227) | done on its branch: [005-phase-GO4.md](005-phase-GO4.md) (records a refuted premise of D3); same pull request |
| GO5 | a per-round growth summary: proposed, mapped onto existing elements, dropped, added (#227) | done on its branch: [006-phase-GO5.md](006-phase-GO5.md); `gnd evolve summary`; one refuted premise of GO5-C1 (spec §13); same pull request |

[Plan](notes/growth-round-outcomes-plan.md). Listed in the
[roadmap update of 2026-11-22](../../PROJECT.md#open-issues-on-2026-11-22--roadmap-update).

What the plan measured for GO1, on a scratch prototype and one laptop: with
each model text parsed once, `gnd evolve apply` on a model of 2,404 object
types takes about 10 s where it takes about 28 s today, and prints the same
bytes. A round still costs time in proportion to the model after GO1.

Rulings (plan §10, [001-plan-gate.md](001-plan-gate.md)): D1–D6 and D9
delegated, D7 and D8 the owner's. GO1 merges by its own pull request before
VG2 starts (D6).

Two files are shared with
[reviewed-vocabulary-growth](../reviewed-vocabulary-growth/README.md):
`evolve/service.py` and `unattended-growth.md`. One writer at a time, in the
roadmap's order: VG1, then GO1, then VG2–VG5, then GO2–GO5 (plan §3).

Closed locally on 2026-11-23: [007-milestone-close.md](007-milestone-close.md), a delegated
ruling (auto=true) after the full panel's close review. Next action: the owner reviews and merges
pull request 261 and posts the replies in [notes/issue-replies.md](notes/issue-replies.md).
