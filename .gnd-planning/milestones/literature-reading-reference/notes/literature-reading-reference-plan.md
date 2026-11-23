# Literature reading reference · plan r1 (outline)

**Status: outline draft, 2026-11-22. Not reviewed and not approved.** This
plan covers [#226](https://github.com/vasiloglou/gnd-public/issues/226).
Phases are outlines; none has a spec yet. `start-milestone` turns this outline
into the full plan and the LR1 draft spec, and the plan review runs then. Code
references were read at `17ab99d2` on 2026-11-22. Rows marked "not read" are
for `start-milestone` to confirm before the plan gate.

## Goal and completion predicates

A host that reads scientific papers with GND's literature stages can tell
whether a low recall is its own loss or the method's. #226 reports about 30 %
recall for every model tried and no reference point to compare with.

- **LR1.** For a source that `gnd verify` fails, a host can list the
  constraints that failed and the rows that violate each. #226 reports
  `verify` failing all 20 sources (3,729 rows) with no way to tell a reading
  error from a constraint too strict for the data.
- **LR2.** The pages state one rule for where a claim's quote may come from:
  the section the model was shown, or anywhere in the declared source. The
  reading example enforces that rule and no other. #226 lost 44 of its 82
  dropped claims to quotes from outside the shown section.
- **LR3.** A labelled set ships with the literature example. A recorded run of
  the reading stages over it reports recall and precision per stage setting,
  and replays with zero producer calls.

## 0. Binding design rules

- **Formats stay.** The anchor and verify formats are unchanged; #226 says
  they work as they are.
- **A reference figure is a measurement of one run.** It names the producer,
  the settings and the labelled set. It is not a claim about other corpora or
  models.
- **No fidelity rate in the `verify` payload.** `gnd verify` keeps saying that
  a checker pass is not proof of faithfulness; the reference figures live in
  the example's own record.
- **Fixture bytes stay.** The packaged reading run and its recorded outputs
  are byte-identical with the defaults.

## 1. Scope, sources and authority

| Source | Obligation | Phase |
|---|---|---|
| #226 request 3 | Why `verify` fails per source: which constraint, on which rows. `gnd verify` composes `popvalidate` and `check` and exits 1 on an alethic failure (its own help text). Which violations and rows its JSON payload already carries: not read | LR1 |
| #226 request 2 | Whether a quote must lie inside the shown section. `reading.py:94-110` validates each roster section's `source`, `span` and `selection`. Where a quote outside the section is refused, and by which stage: not read | LR2 |
| #226 request 1 | A reference recall and precision on a labelled set, with settings. Today the example measures fidelity recall over two held-back facts only (`reading.py:42` `CALIBRATION_FACTS`, `:311-341` `_calibrate` and `_recall`) | LR3 |
| #226 "What we measured" | Best recall 29 of 101 (broad) and 30 of 100 (targeted); 82 claims dropped host-side; 3 of 29 aligned claims agree on the predicate | LR3 comparison rows |
| literature-depth close, row "Host-scale reading and extraction" | The run over a separately selected corpus and provider budget stays carried with the literature-identity follow-up | LR3 (D1 decides whether LR3 is that run or a smaller one) |
| literature-host-interfaces plan, LH1 and LH2 | A public producer protocol, and replay of a live run with zero producer calls | LR3 uses both |

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #226: a way to see why `verify` reports an alethic failure per source | LR1 |
| #226: guidance on whether a quote must lie inside the shown section | LR2 |
| #226: a reference recall and precision with the stage settings | LR3 |

Not in this milestone: raising the recall itself. LR3 gives the figure a host
compares against; a method change follows from what it shows.

## 2–3. Contract sketch and dependencies

- **LR1** may be a document change alone, if the payload already carries the
  violations by constraint and row; the spec decides after reading it. If not,
  it adds a per-constraint summary to the report without changing the format's
  existing fields.
- **LR2** is a document change plus, if the example's behaviour differs from
  the rule the owner picks (D2), a parameter on the reading example.
- **LR3** needs LH1 and LH2 merged: the reference run is a live run driven
  through the public producer protocol and replayed from its folder. It also
  needs a labelled set (D1) and a producer and budget (D3).
- LR1 and LR2 are independent of each other and of LR3.
- **One writer at a time on `examples/literature/reading.py`.**
  literature-host-interfaces LH1 and LH2 edit it; LR2 and LR3 start after
  they merge, or LR2 carries its parameter into LH1's spec.

## 4. Phases

| Phase | Outline criteria |
|---|---|
| LR1 | For a packaged source that fails `verify`, the documented steps list each failing constraint with its violating rows, and a test holds the list. A source that passes lists none |
| LR2 | One rule is stated on the literature page and in the tutorial. A claim quoting text outside the shown section is kept or refused as the rule says, with a named reason when refused, and a test covers both sides |
| LR3 | The labelled set and one recorded run ship with the example. The record gives recall and precision per stage setting and names the producer and settings. Replay from the run folder makes zero producer calls and reproduces the figures. The page shows the figures beside the scoring rule |

## 5. Owner decisions and open questions

| ID | Question | Proposed |
|---|---|---|
| D1 | LR3: the labelled set. (a) A small set written for the example from openly licensed papers. (b) The corpus run the literature-depth close carried. (c) Ask the reporter for a redistributable slice of theirs | (a). It can ship in the package; (b) stays carried |
| D2 | LR2: the rule. (a) A quote must lie inside the shown section. (b) Anywhere in the declared source version, with the section recorded | (b) if the anchor check already binds a quote to the source version; the spec confirms |
| D3 | LR3: the producer and its budget for the recorded run | Owner names one model and a ceiling; the run is recorded once and replayed after |
| D4 | LR3: the scoring rule for "a gold claim is found" | Span overlap plus participant names, as #226 scored, so the figures are comparable; predicate agreement reported beside it |
| D5 | Whether LR1 and LR2 ship as two maintenance passes instead of phases | Phases, so the three replies to #226 go out together |

## 6–9. Surfaces, risks, protocol, verification

- **Surfaces.** The literature examples page, the literature tutorial and the
  `gnd verify` reference page.
- **Risks.**
  - A reference figure could be read as a product claim. Control: §0, and the
    page states the set, producer and settings beside every figure.
  - A labelled set could carry text that cannot be redistributed. Control: D1
    (a), with the licence of each source recorded in the set.
  - A live run needs a provider credential. Control: the recorded run is made
    once under the owner's explicit selection; the gate replays it and calls
    no model.
- **Protocol.** `process-milestone` with the project rules in
  `.codex/skills/process-phase/references/project.md`.
- **Verification.** Each spec names its focused lane from
  `test_ld3_reading_workflow.py`, `test_ld4_revision.py` and
  `test_ld5_verdict.py`, plus the structure and inventory guards.
