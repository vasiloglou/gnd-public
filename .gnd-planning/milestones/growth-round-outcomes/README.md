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
| GO1 | `gnd evolve` parses each model text once per invocation: 22 parses become at most 3 in `apply` (#228) | done on its branch: [002-phase-GO1.md](002-phase-GO1.md); `apply` parses 2 times where it parsed 22; pull request open, not merged |
| GO2 | `gnd evolve preview` reports an outcome for every operation of a proposal (#227) | [spec r1](notes/phase-GO2-spec.md) approved by delegated ruling; code waits for VG2 and VG4 merged on `main` |
| GO3 | the admitted part of a proposal as a new proposal, with one call (#227) | [spec r1](notes/phase-GO3-spec.md) approved by delegated ruling; code needs GO2 |
| GO4 | `unattended-growth.md` says what a reply carries for a fact type it reuses (#227) | [spec r1](notes/phase-GO4-spec.md) approved by delegated ruling (records a refuted premise of D3); code waits for VG2 and VG5 merged on `main` |
| GO5 | a per-round growth summary: proposed, mapped onto existing elements, dropped, added (#227) | [spec r1](notes/phase-GO5-spec.md) approved by delegated ruling; code needs GO2, and VG2 and VG5 merged on `main` |

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

Next action: the owner merges GO1's pull request; then GO2 waits for VG2 and VG4 merged on `main`. Each phase
start is announced to the coordinating session ("READY <phase>").
