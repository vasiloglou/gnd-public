# growth-round-outcomes · close delta

Every departure from plan r4 and the approved specs, and where it is recorded.

| # | Departure | Why | Recorded |
|---|---|---|---|
| D1 | GO1's scope opens on `gnd.commands.evolve.handle`, not the three `_cmd_evolve_*` handlers | the RF5 relocation guard pins those bodies | GO1 spec §13, `002-phase-GO1.md` |
| D2 | GO2's `dropped-with` is a closure over the whole proposal, its needs read by a walk that follows the ORM meta-schema; an issue is located only on the one operation that changed its element or role, otherwise `unassessed` | diff reviews r1 and r2: order-dependent drops, false dependencies from sample rows, wrong blame | GO2 spec §14.7, `phase-GO2-r1/`, `phase-GO2-r2/` FINDINGS |
| D3 | GO4 premise D3(a) refuted; the reply rule routes rows for an existing fact type to `open_questions`; the shape-match bullet changed to agree | the additive policy refuses a changed sample row | GO4 spec r2 and §14, `phase-GO4-r1/FINDINGS.md` |
| D4 | GO5-C1's known-mix round has no `dropped-with` row; that verdict is counted in its own case over an outcome report | a `dropped-with` row needs a refused addition; the additive policy refuses no element addition, so it comes only from a refused candidate, which writes no preview and no shape matches | GO5 spec §13.1, `tests/fixtures/round-summary/README.md` |
| D5 | GO3 refuses by type first, then other outcomes, a preview without rows, the before model, rows that are not the operations in order | a dict cannot be asked for its digest; review GO3–GO5 F1 | GO3 spec §14, the evolution contract |
| D6 | GO5's summary binds every artifact by its own identity and keeps the host's text unstripped | review GO3–GO5 F4, F5 | the evolution contract "Round summary" |
| D7 | The budget's second review round for GO4 and for GO3–GO5 was not run separately; this close review reads those repairs | one panel over the whole diff instead of two more single-reviewer rounds | FINDINGS of `phase-GO4-r1`, `phase-GO3-GO5-r1` |
| D8 | Files outside the plan's §3 lists: `commands/evolve.py`, `disclosure.py` and its page and test, `evolve/__init__.py`, the layer map and component index, the RF1/RF5/RF6 successor and pin files, `tests/support/markdown_sections.py`, the RF9 mutation ledger | guards and registries every new module or leaf touches | pull request 261 description |

Unreviewed by any reviewer before this close: commit `ff67e11d` (the
GO3–GO5 review repairs in `src/gnd/discover/narrow.py`,
`src/gnd/evolve/summary.py`, `tests/support/markdown_sections.py`) and the
mutation-ledger line in `6521dce2`.
