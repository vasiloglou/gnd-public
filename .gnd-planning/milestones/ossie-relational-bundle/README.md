# ossie-relational-bundle

Planning opened 2026-11-24 from the owner's issue file, which holds three
Ossie export issues not yet filed on GitHub.

**Status:** plan r2, **approved by the owner on 2026-11-24** ([plan gate](002-plan-gate.md), sha256 `52d946a4…6e1d`), with D1–D11 ruled as proposed. OB1 is implemented and recorded; OB2 is next.

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
| OB1 | `--max-output-bytes N` on export and, per D3, `--max-input-bytes N` on import | **merged** (PR #266): [record](004-phase-OB1.md), [spec](notes/phase-OB1-spec.md) |
| OB2 | Halpin Rmap library `gnd.rmap`, with D5 ruled inside the phase | **merged** (PR #270): [record](008-phase-OB2.md); D5 = HALPIN ([gate](007-OB2-D5-gate.md)); two review rounds |
| OB3 | Semantic model and mapping files, with the default per D2 | **recorded** ([record](011-phase-OB3.md)); its four departures accepted ([gate](012-OB3-departures-gate.md)); one review round; not pushed |
| OB4 | `--physical-binding FILE` | after OB3 (D7, D8 ruled) |
| OB5 | Docs and skill | after OB4 |

**Next action:** the owner decides on a pull request for OB3, the oracle lane (OB3-Q3) and a second review round (OB3-Q4); OB4 follows. D10 asks the reporter for inputs and files the three issues on GitHub, each confirmed with the owner first. The 0.5.0 release waits for this milestone's close.
