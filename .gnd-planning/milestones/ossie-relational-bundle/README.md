# ossie-relational-bundle

Planning opened 2026-11-24 from the owner's issue file, which holds three
Ossie export issues not yet filed on GitHub.

**Status:** closed by the owner on 2026-11-25 ([ruling](022-close-ruling.md); [close record](021-milestone-close.md)). The three requests are issues [#276](https://github.com/vasiloglou/gnd-public/issues/276), [#277](https://github.com/vasiloglou/gnd-public/issues/277) and [#278](https://github.com/vasiloglou/gnd-public/issues/278), closed as delivered; the two carried design questions are open as [#279](https://github.com/vasiloglou/gnd-public/issues/279) and [#280](https://github.com/vasiloglou/gnd-public/issues/280). **Still outside the repository:** the [message to the reporter](notes/D10-drafts.md) is the owner's to send, and external acceptance waits for the reporter's run.

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

**Status:** closed by the owner on 2026-11-25 ([ruling](022-close-ruling.md); [close record](021-milestone-close.md)). **Still outside the repository:** the reporter message and five issue texts ([drafts](notes/D10-drafts.md)) wait for the owner's confirmation of each text, and external acceptance waits for the reporter's run.
