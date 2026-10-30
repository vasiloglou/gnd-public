# Plan gate: ilp-import-hardening r2

Date: 2026-10-29. `auto=false`.

**Owner approval (o).** Asked "Approve plan r2 with the proposed answers?",
the owner answered on 2026-10-29: "Approve as proposed".

The full digests of the bytes the answer covers were checked against the
files before this record was written:

| Artifact | SHA-256 |
|---|---|
| `notes/ilp-import-hardening-plan.md` (r2) | `d7802da69d50ad39e440602f39aa132594208846e2778466f711755d9d919fd0` |
| `notes/phase-IH0-spec.md` (r2) | `ed8dd3dcda7b82b6873918ed5c76ed6d4b3484e5e2cd0325c3333b5327fceeb1` |

**Review history.**
- **Instrument:** one reader over r1 (IH-D5, ruled by the owner), a
  departure from the repository's four-reviewer plan bar.
- **Result:** request-changes, 14 findings, 3 blocking; the blocking three
  were reproduced before repair, and all 14 were applied in r2; see the
  [disposition](notes/plan-review-r1-disposition.md).
- **No opinion on r2:** r2 carries no review opinion, and this approval adds
  none.

**The plan is not edited to record its own approval.** This file is the
record.

## Rulings (o), 2026-10-29

The plan's proposed rows are approved as written in r2:

| Row | Ruling |
|---|---|
| IH-D1 | (b): refuse an own-reference subtype join as `own-reference-join`, after `type-confused-join`; R1's asserted name changes; no golden moves |
| IH-D2 | IL's nine merges, `src/` and `tools/` |
| IH-D3 | IL6-Q3 left out, with the evaluation milestone |
| IH-D4 | (a): four local readers for IH0 |
| IH-D5 | (b): one reader, ruled earlier the same day |
| IH-D6 | (a): four readers for the close |
| IH1-D1 | (a): the import renders and compares the facts digest |
| IH1-D2 | (a): accept that mapping refusals precede counting refusals in `hold()` |

The IH0 spec's decisions are approved as written in r2: IH0-D1 and IH0-D2
(the same rows as IH-D2 and IH-D4), IH0-D3 (counting-path hardening
findings go to IH1) and IH0-D4 (golden-moving fixes batched into one ruling
after triage).

## Selection

No phase has been selected. IH0 runs only when the owner explicitly selects
`process-phase IH0 ilp-import-hardening`. Each later phase needs its own spec
gate.

## Boundary

- **Later phases:** approval of the plan is not approval of IH1's, IH2's or
  the close's spec.
- **IH0-D4:** a fix that moves a golden or bumps an adapter version still
  returns to the owner, as one batched ruling after triage.
- **No learner, solver or model run** is authorized (IH-R1).
- **No merge, release, publication or certification** is authorized.
