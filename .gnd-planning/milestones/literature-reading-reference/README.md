# Literature reading reference

Plan r2, 2026-11-23, for
[issue #226](https://github.com/vasiloglou/gnd-public/issues/226). r2 is the
full plan `start-milestone` wrote from outline r1 of 2026-11-22.
**Not reviewed and not approved.** No plan review has run and no instrument
is selected. `auto=false`.

| Phase | Deliverable | State |
|---|---|---|
| LR1 | A host can see why `gnd verify` fails a source: which constraint, on which rows | [draft spec](notes/phase-LR1-spec.md), awaiting the plan gate, rulings D7 and D8, and the owner's review |
| LR2 | The pages say where a quote may lie: anywhere in the document the anchor sidecar names | outline; waits for ruling D2 |
| LR3 | A labelled reference set for the reading stages, with a recorded recall and precision | outline; needs LH1 and LH2 of [literature-host-interfaces](../literature-host-interfaces/README.md) implemented and merged, and rulings D1, D3, D4 and D9 |

[Plan](notes/literature-reading-reference-plan.md). Listed in the
[roadmap update of 2026-11-22](../../PROJECT.md#open-issues-on-2026-11-22--roadmap-update).

Two things the outline had not read, and what reading them changed:

- `gnd verify --format json` already lists each failing constraint with its
  violating rows. LR1 is therefore a page and a test, unless the owner wants
  the rows in the text output or the constraint's declared id in the report
  (D7).
- The reading example has no quote and refuses none. The claims #226 lost to
  "quote outside the shown section" were dropped by the reporter's own host.
  GND binds a quote to a whole document version, so LR2 documents that rule
  and adds no check.

Decisions waiting for the owner (plan §10): D1 the labelled set; D2 the
quote rule; D3 the producer and budget of the one live run; D4 the scoring
rule; D5 whether LR1 and LR2 ship ahead of LR3; D6 the review instrument;
D7 whether `gnd verify` changes; D8 the home of the new section; D9 what
"stage settings" covers.

Next action, the owner's: select a plan review instrument or waive one, rule
D1–D9 or amend them, then the plan gate. LR1 can start from its spec gate
after that. LR3 waits for literature-host-interfaces.
