# ossie-relational-bundle

Planning opened 2026-11-24 from the owner's issue file, which holds three
Ossie export issues not yet filed on GitHub.

**Status:** plan r2, draft, not approved. Nothing is implemented.

The maintained light panel reviewed r1 at effort high:

- 4 of 6 seats succeeded (qwen and glm timed out).
- None approved: three asked for revision and one blocked.

The owner directed "Apply fixes as r2". r2 applies all 16 fixes and is not
itself reviewed.

- [Plan r2](notes/ossie-relational-bundle-plan.md)
- [OB1 spec r2 (draft)](notes/phase-OB1-spec.md)
- [Light-panel review of r1](evidence/plan-review-r1/PANEL-REVIEW.md) ([record](001-panel.md))

| Phase | Deliverable | State |
|---|---|---|
| OB1 | `--max-output-bytes N` on export and, per D3, `--max-input-bytes N` on import | spec drafted; blocked on the plan gate and D3 |
| OB2 | Halpin Rmap library `gnd.rmap`, with D5 ruled inside the phase | blocked on D1 |
| OB3 | Semantic model and mapping files, with the default per D2 | blocked on OB2, D2, D4 and D6 |
| OB4 | `--physical-binding FILE` | blocked on OB3, D7 and D8 |
| OB5 | Docs and skill | after OB4 |

**Next action:** the owner rules D1–D11 (plan §10) and decides whether r2
gets a second review round (D9). Then the plan gate.
