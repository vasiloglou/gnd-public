# Phase GO3 · the admitted part of a proposal as a new proposal · spec r1

## 1. Status

**Draft r1, 2026-11-23, awaiting its gate.** Planning only. GO3 needs GO2
merged into the branch (plan §3) and so waits, with GO2, for
reviewed-vocabulary-growth VG2 and VG4 on `main`.

## 2. Provenance

- Derives from [plan r4](growth-round-outcomes-plan.md) (sha256
  `b107bd36…7431`): Goal (GO3), R0.1, R0.3, §1 H12–H14, §2 GO3, §4 GO3-C1
  to C4, §10 D5 and the GO3 open question; and from the GO2 spec r1 (the
  outcome report and the verdict words).
- From [#227](https://github.com/vasiloglou/gnd-public/issues/227),
  request 1, second half ("or a documented way to apply part of a
  proposal").
- Code read at `92cc161f`. No review has read these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan GO3, D5 (a) | one library call returns the proposal of the operations not refused | §6; T1 |
| plan R0.1 | `apply` stays whole; the narrowed proposal is previewed and applied as any other | §6; T1 |
| plan GO3-C2 | a dependent of a dropped operation is dropped with it and named | §6; T2 |
| plan GO3-C3, R0.3 | own `proposal_id`, origin named in an optional field; a proposal without it keeps its bytes; the original preview behaves as today until the narrowed one is applied, then stale | §6; T3 |
| plan GO3-C4 | nothing kept: no proposal, and a reason | T4 |
| plan H14 | rebuild with `candidate_document` and `candidate_text` | §6 reuse |
| plan open question | whether the narrowed proposal keeps the original operation ids | GO3-D2 |

## 4. The standing rules, bound to this phase

- **Totality (rule 1).** The function reads a preview or an outcome report
  that a host passes back: it accepts only the validated models
  (`EvolutionPreview`, `EvolutionOutcomeReport`) and refuses anything else
  by type; a host file goes through GO2's total reader first (T5).
- **A cap bounds the document (rule 2).** One pass over operations and
  outcomes plus GO2's dependents closure; T6 times 2,000 operations.
- **Validation order (rule 3).** The before model's sha256 is checked
  against the proposal's `expected_model_sha256` before anything is
  replayed; a mismatch is refused first (T5).
- **One walk (rule 4).** The dependents closure is GO2's, imported, not a
  second one.
- **One home (rule 5).** The function's contract lives in the evolution
  contract beside the outcome report; the docstring cites it.
- **Measurement (rule 6).** Whether the narrowed candidate validates is
  measured by previewing it (T1), not inferred.
- **General solutions.** No string handling: ids come from the models.

## 5. Goal

`narrow_proposal(proposal, outcomes)` returns a new `EvolutionProposal` of
the operations whose verdict is `admitted` or `unassessed`, replayed over
the before model the outcomes carry, or `None` with the reason when none is
kept.

## 6. Design

### Reuse

| Capability | Search | Found | Decision |
|---|---|---|---|
| replay operations and write the candidate | `components_index.py search "candidate proposal operations replay"` | `discover.output`: `candidate_document`, `candidate_text`, `proposal` | reuse |
| dependents of a refused operation | GO2 | the locator's closure | reuse |

### `src/gnd/discover/narrow.py` (new, about 70 lines)

```python
def narrow_proposal(
    proposal: EvolutionProposal,
    outcomes: EvolutionPreview | EvolutionOutcomeReport,
) -> tuple[EvolutionProposal | None, tuple[str, ...]]:
    """Keep the operations GO2 did not refuse; see the evolution contract."""
```

1. `outcomes` must bind this proposal: its `proposal_sha256` equals the
   proposal's; refused otherwise.
2. The before model is `outcomes.before_model`; its sha256 must equal
   `proposal.expected_model_sha256` (rule 3).
3. Kept: operations whose row is `admitted` or `unassessed`; dropped:
   `refused-*` and `dropped-with`, plus GO2's closure re-run over the kept
   set (a host may have edited nothing, but the closure is cheap and makes
   the function total over any outcome list).
4. Candidate: `candidate_text(candidate_document(before, kept))`.
5. Proposal: the original's fields with the kept operations (original ids,
   GO3-D2), the new candidate, `proposal_id` `<original>-narrowed`, and
   `narrowed_from: {proposal_id, proposal_sha256}`.
6. Returns the reasons as value-free lines, one per dropped operation:
   index, id, verdict.

### `narrowed_from` on `EvolutionProposal` (`src/gnd/evolve/models.py`)

An optional field, `None` by default and omitted from the serialized
document when unset, under the same rule as `_OPTIONAL_PREVIEW_FIELDS`
(R0.3). No proposal schema version moves; every proposal written today
keeps its bytes and `proposal_sha256` (T3).

### The original preview

Narrowing writes nothing. Until the narrowed proposal is applied, the
original preview applies or is refused exactly as today; after it is
applied, the model's sha256 has moved and the original preview's
`apply` is refused by the model CAS as stale, exit 11 (T3).

### Pages

Evolution contract: "Narrowing a proposal" beside the outcome report.
`docs/release-notes.md`: one entry.

## 7. Decisions

| ID | Question | Readings | Proposed |
|---|---|---|---|
| GO3-D1 | Instrument | prose | prose |
| GO3-D2 | Operation ids (plan open question) | (a) keep the original ids: a host's log joins rounds by id. (b) renumber: ids stay contiguous | (a) |
| GO3-D3 | Keep `unassessed` operations | (a) keep: the narrowed preview assesses them. (b) drop: a narrowed round could lose an operation no gate refused | (a), as plan GO3 rules |
| GO3-D4 | The module | (a) `discover/narrow.py`, beside `discover/output.py`, whose layer already imports the evolve models. (b) inside `output.py`: 900 lines already | (a) |

## 8. Tests

New `tests/test_go3_narrowed_proposal.py`.

| # | Case | Expected |
|---|---|---|
| T1 | GO2-C1's report (GO3-C1) | a proposal of the three kept operations; preview and apply exit 0, or the preview names the fault the first pass masked |
| T2 | a fact type refused, a constraint on it in a later operation (GO3-C2) | both dropped, the constraint named `dropped-with` |
| T3 | an admitted preview with a policy refusal (GO3-C3) | own `proposal_id`, `narrowed_from` set; the original proposal's bytes unchanged; the original preview applies as today before, and exits 11 after the narrowed proposal is applied |
| T4 | every operation refused (GO3-C4) | `None` and one reason per operation |
| T5 | outcomes of another proposal; a before model whose sha256 is not `expected_model_sha256`; a dict in place of a model | each refused by name, in that order |
| T6 | 2,000 operations, half refused | under one second |

Gate: plan §9 GO3 lane, guard block, both lint commands, component check.

## 9. Out of scope

A `gnd evolve narrow` command (D5 (b), until a host asks); partial
`apply`; re-running the narrowed preview inside the function.

## 10. Size

About 100 source lines and 250 test lines.

## 11. Approval instrument

This prose.

## 12. Gate — delegated approval (auto=true)

**Delegated approval (auto=true), 2026-11-23**, of this spec r1, sha256
`35bd3cec9c18296178010c0abf7a6b7ab7ebfb335324cc1b63a183197ae03a41` (the bytes above this section). Authorization: the owner's
delegation of `auto` for growth-round-outcomes, recorded in
`001-plan-gate.md`. An agent ruling under that delegation, not the owner's
reading of the spec. No spec review ran (optional, omitted).

- Rulings: GO3-D1 prose; GO3-D2 (a); GO3-D3 (a); GO3-D4 (a) [delegated].
- Sweep: `candidate_document` and `candidate_text` replay any operation list over a document; `EvolutionProposal` is closed, so `narrowed_from` needs an omit-when-unset rule of its own, modelled on `_OPTIONAL_PREVIEW_FIELDS`. Depends on GO2's report and closure.
- Budget: one diff review round (D8), a second only if the first blocks.
- **Approval is of the design only. Implementation waits** for the
  start condition of plan §3 on `main` and the coordinating session's
  "GO" to "READY GO3". A spec approved now is re-read against `main` at
  that start; a change on `main` that moves a cited line or a premise
  amends this spec before code, with the prior wording retained.
