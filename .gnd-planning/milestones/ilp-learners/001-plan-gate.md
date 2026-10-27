# Plan gate: ilp-learners r3

Date: 2026-10-27. `auto=false`.

**Owner approval (o).** The owner approved the plan and the IL1 spec in the
session on 2026-10-27: "I approve plan r3 (SHA-256 329449d8…6281) and IL1 spec
r3 (SHA-256 83138d48…0f30)."

The full digests of the approved bytes were checked against the files before
this record was written:

| Artifact | SHA-256 |
|---|---|
| `notes/ilp-learners-plan.md` (r3) | `329449d8e37efe16ffb98f7f25f24c513a7d81c4f61d3b6ed80b100868996281` |
| `notes/phase-IL1-spec.md` (r3) | `83138d4806a8e0086fea8768a75286c7465dfa4773707adf2d72f55d54c10f30` |

**Review history.**
- **Rounds:** round 1 reviewed r1, and the confirmation round reviewed r2.
- **The stop:** review stopped under its declared rule (self-inflicted ratio
  1.0, 0 blocking); see the
  [round-2 disposition](notes/plan-review-r2-disposition.md).
- **r3:** applied the round-2 repairs and D13 at the owner's direction.
- **No opinion on r3:** r3 carries no review opinion, and this approval adds
  none.

**The plan is not edited to record its own approval.** This file is the
record.

## What the approval leaves open

**IL1's own gate decisions.** These are still to be ruled before IL1's
implementation or live run:
- **IL1-D3:** install commands and downloads, each with URL, filename, size and
  SHA-256.
- **IL1-D5:** base commit and branch.
- **IL1-D8:** licences, recorded from upstream before any download.

The spec's other proposed rows (IL1-D1, D2, D4, D6 and D7) are approved as
written in r3.

**The plan's proposed rows** are approved as written: D3 (a), D4, D6, and D7
(out). Leaving neural learners out is approved with them.

**D8, the LLM run,** remains open until the IL5 gate.

## Selection

No phase has been selected. Execution starts only when the owner explicitly
selects `process-phase IL1 ilp-learners`. Each later phase needs its own spec
gate.

## Boundary

- **Later phases:** approval of the plan is not approval of any later phase's
  spec.
- **Installs:** none is authorized by this record beyond D2's terms. Each
  download is still approved at its gate.
- **No merge, release, publication or certification** is authorized.
