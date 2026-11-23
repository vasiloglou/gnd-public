# Growth round outcomes

Plan r2, 2026-11-23, for
[issue #228](https://github.com/vasiloglou/gnd-public/issues/228) and
[issue #227](https://github.com/vasiloglou/gnd-public/issues/227). r2 is the
full plan `start-milestone` wrote from outline r1 of 2026-11-22.
**Not reviewed and not approved.** No plan review has run and no instrument
is selected. `auto=false`.

| Phase | Deliverable | State |
|---|---|---|
| GO1 | `gnd evolve` parses each model text once per invocation: 22 parses become at most 3 in `apply` (#228) | [draft spec](notes/phase-GO1-spec.md), awaiting the plan gate and the owner's review |
| GO2 | `gnd evolve preview` reports an outcome for every operation of a proposal (#227) | outline; waits for rulings D1 and D2, and for its turn on `evolve/service.py` |
| GO3 | the admitted part of a proposal as a new proposal, with one call (#227) | outline; needs GO2 and D5 |
| GO4 | `unattended-growth.md` says what a reply carries for a fact type it reuses (#227) | outline; waits for ruling D3, and for its turn on the growth document |
| GO5 | a per-round growth summary: proposed, mapped onto existing elements, dropped, added (#227) | outline; needs GO2 and D4 |

[Plan](notes/growth-round-outcomes-plan.md). Listed in the
[roadmap update of 2026-11-22](../../PROJECT.md#open-issues-on-2026-11-22--roadmap-update).

What the plan measured for GO1, on a scratch prototype and one laptop: with
each model text parsed once, `gnd evolve apply` on a model of 2,404 object
types takes about 10 s where it takes about 28 s today, and prints the same
bytes. A round still costs time in proportion to the model after GO1.

Decisions waiting for the owner (plan §10): D1 and D2 what a per-operation
outcome covers and where it lives; D3 the reply rule; D4 who computes the
round summary; D5 a library function or a command for the narrowed proposal;
D6 whether GO1 ships alone first; D7 the review instrument; D8 the phase
diff reviewer; D9 whether the loader's own double parse rides with GO1.

Two files are shared with
[reviewed-vocabulary-growth](../reviewed-vocabulary-growth/README.md):
`evolve/service.py` and `unattended-growth.md`. One writer at a time, in the
roadmap's order: VG1, then GO1, then VG2–VG5, then GO2–GO5 (plan §3).

Next action, the owner's: select a plan review instrument or waive one, rule
D1–D9 or amend them, then the plan gate. GO1 can start from its spec gate
after that; it needs no other ruling.
