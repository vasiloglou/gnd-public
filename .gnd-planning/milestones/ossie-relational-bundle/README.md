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
| OB3 | Semantic model and mapping files, with the default per D2 | **merged** (PR #271): [record](011-phase-OB3.md); its four departures accepted ([gate](012-OB3-departures-gate.md)); one review round |
| OB4 | `--physical-binding FILE` | **merged** (PR #272): ([record](015-phase-OB4.md)); one review round; both added rules accepted ([gate](016-OB4-departures-gate.md)) |
| OB5 | Docs and skill | **merged** (PR #273): [record](020-phase-OB5.md); the oracle lane ran and its finding is repaired ([gate](019-OB5-quoting-gate.md)); one review round |

**Next action:** the owner's close ruling. The [close record](021-milestone-close.md) is written except for it; the light panel ran and its concerns are [dispositioned](evidence/close-review/disposition.md). Then: the reporter message and the three issues ([drafts](notes/D10-drafts.md)), each confirmed by the owner first, and the note to the 0.5.0 release session once this merges.
