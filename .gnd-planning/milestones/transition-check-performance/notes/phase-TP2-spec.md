# Phase TP2: Remove deep copies of immutable inputs

## 1. Status

**Owner-approved (o5), 2026-10-16** ("TP2 approved"). The approved bytes have SHA-256
`a6cf8f35ceb745418617753a77dfe59c4a0fe4d429d85be553c43facd14201de`. D1–D3 are accepted as proposed. The implementer is Codex CLI. The
spec is append-only from here.

## 2. Provenance

- Plan r5, owner-approved ([plan gate](../001-plan-gate.md)): §2 TP2, §4 TP2-C1..C4,
  TP-D6 and D-p1-2 (gate on copied nodes).
- TP0 and TP1 records ([002](../002-phase-TP0.md), [003](../003-phase-TP1.md)).
- A measurement taken at planning time, on the TP1 branch: each copied node attributed
  to its first caller outside `copy.py`, over the reporter replay. Results below.
- No review has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| TP2-C1 | Inventory every deep-copy site the workloads reach, with a keep or remove ruling and a reason | §6 inventory |
| TP2-C2 | Each removed copy has a guard test that fails if the copy was needed | T2 |
| TP2-C3 | The public detached-value tests pass unchanged | T3 |
| TP2-C4 | `deepcopy_nodes` on the reporter replay is ≤ 1,380,197 (same interpreter), with parity | T1, T4 |
| TP-R1, TP-R2, O5 | Same answers; no stale or corrupted index; the public queries stay detached | T2, T3, T4 |
| TP-R5 | One home; zero layer allowances | §6, layering test |

## 4. Rules bound to TP2

Standing rules:

1. **Totality:** no new input consumer.
2. **Bounds:** no new memo. The work only goes down.
3. **Validation order:** does not apply, because no boundary changes.
4. **One walk:** one internal accessor serves all eight internal readers.
5. **One home:** the accessor's "never mutate" contract is stated once, in its docstring.
6. **Measurement:** the inventory below is measured, not argued.

Plan rules:

- **TP-R1:** T4 checks parity.
- **TP-R2:** T2's frozen guard proves that no internal reader writes into the shared
  index. A write would corrupt the content-keyed cache for every later call.
- **TP-R3:** does not apply.
- **TP-R4:** T1 gates on a counter.
- **TP-R5:** `gnd.model_index` is the one home.
- **TP-R6:** no downstream names.

## 5. Goal

`uv run pytest -q tests/test_tp2_shared_fact_types.py tests/test_tp1_index_scope.py
tests/test_transition_cost_workload.py tests/test_rf6_index.py tests/test_rf1_layering.py
tests/test_public_transition_contract.py` exits 0. On the reporter replay:

- `deepcopy_nodes` ≤ 1,380,197;
- `model_index_key_paths` stays at 26;
- `checker_runs` stays at 25;
- every TP0 digest is unchanged.

## 6. Design

### Inventory (reporter replay, 2,760,394 nodes at TP1)

| Site | Nodes | Share | Ruling |
|---|---|---|---|
| `model_index.py:167` `ModelIndex.fact_types`, reached through `iter_fact_types()` by 8 internal readers | 2,645,100 | 95.8% | **Remove for internal readers.** They read and never write. The public accessor keeps copying. |
| `model_index.py:244` `iter_constraints` | 42,075 | 1.5% | Keep. It is a public query, and the gain is small. |
| `transition.py:1476` `_effective_extension_state` | 36,156 | 1.3% | Keep. It builds a state that is then edited. |
| `transition.py:858` `_restore_asserted_state` | 14,625 | 0.5% | Keep. Its result is edited. |
| `transition.py:2103` `evaluate_plan` | 11,724 | 0.4% | Keep. The document is then edited. |
| `transition.py:1499/1567` (operation copies) | 6,210 | 0.2% | Keep. They are the only guard against the write at line 1951 reaching `model.operations` (plan §2). |
| `transition.py:1512/1589` (obligation copies) | 4,076 | 0.1% | Keep. Their source is the operation, as above. |
| `transition.py:202` `validate_steps_document` | 428 | 0.0% | Keep. The copy is then edited. |

Removing only the first row is predicted to leave about 115,000 nodes, a 96% reduction.
That is far past the 50% target, with the smallest possible diff.

### `src/gnd/model_index.py` (about 10 lines)

```python
def iter_fact_types_shared(self) -> Iterator[dict[str, Any]]:
    """Internal readers only: the index's own fact-type rows, not copied.

    Callers must never mutate a row or anything inside it. The index is shared across
    calls through the content-keyed cache, so a write would corrupt every later caller.
    Public callers use ``iter_fact_types`` / ``fact_types``, which return detached copies.
    """
    return iter(self._document.get('fact_types') or [])
```

### The eight call sites switched (one token each)

These eight call `ModelIndex.for_model(model).iter_fact_types()` and change to
`.iter_fact_types_shared()`:

- `checker/_core.py` lines 438, 1669, 1691, 1705, 1797, 1904;
- `compiled_obligations.py:116`;
- `universe.py:335`.

The implementer must confirm, by reading each loop body, that the row is only read. A
site that writes, or that passes a row on to code that writes, keeps
`iter_fact_types()` and is recorded as a finding. `synth/*` and `popvalidate.py` are
unchanged, because they are not on the checking path.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | Scope of removal | Only the 95.8% site (proposed). The alternative also removes transition copies: 4% more, with real aliasing risk. |
| D2 | Guard method | A test-time deep-frozen view (proposed, T2): rows become read-only mappings and tuples, so any write raises. The alternative is to return frozen views in production too, which changes the row types that readers see, so that `isinstance(row, dict)` and JSON paths could change behaviour. |
| D3 | Implementer | Codex CLI, as the owner selected. The session reviews its diff, runs the gates, and records the result. An independent local reader still reviews the final diff. |

## 8. Tests

The new file is `tests/test_tp2_shared_fact_types.py`.

| # | Case | Expected |
|---|---|---|
| T1 | Reporter replay under `counting()`: `deepcopy_nodes <= 1_380_197`, `model_index_key_paths == 26`, `checker_runs == 25`. | pass (fails on TP1: 2,760,394) |
| T2 | Frozen guard. `iter_fact_types_shared` is monkeypatched to yield deep-frozen rows (`MappingProxyType` and tuples, recursively). Then the reporter replay, the `course` walks, and `api.check` with `compiled_operations=True` and with `admission=True` all run with no exception, and their digests equal the TP0 baseline. A negative control writes to one yielded row and raises `TypeError`. | pass |
| T3 | Public detachment. Mutating a row returned by `fact_types` or `iter_fact_types()` leaves the next `iter_fact_types_shared()` unchanged. The existing `test_rf6_index.py` detachment tests pass unchanged. | pass |
| T4 | Parity: every TP0 surface's payload and trace digests, and the CLI digests, equal `evidence/TP0/digests.json` (reuses TP1's T7 helper). | pass |
| T5 | Mutant: if `iter_fact_types_shared` yields `deepcopy` rows (that is, if TP2 is undone), T1 fails. Recorded as evidence, not as a separate test. | killed |

Verification selection:

- **Run:** the §5 command, plus the affected-consumer batches that TP1 used. Run once
  per interpreter (3.14, 3.11, 3.13) at the end of the phase, not after each fix.
- **Slow cadence:** the broad suite, run only on owner selection.

## 9. Out of scope

- The copy sites in `transition.py` and `iter_constraints`.
- Receipts (TP3).
- Any change to a public query's return value.

## 10. Size

About 10 source lines plus 8 one-token edits, and about 120 test lines.

## 11. Approval instrument

This prose. The counters and digests that judge TP2 are already committed.

## Implementation findings, recorded as they were found

1. **Codex implemented §6 exactly:** one method and 8 one-token swaps. It gave a read-only
   reason for each site, and no site was left unchanged. Codex ran through the ChatGPT-
   bundled CLI. The Homebrew CLI 0.156.1 rejected the configured model on this account.
2. **The spec's T2 guard type was wrong.** A `MappingProxyType` row fails the readers'
   `isinstance(row, dict)` checks (`compiled_obligations.py:118`), which changed compiled
   results. That was the D2 risk, showing up in the test itself. Codex asked instead of
   widening the change. The fix is test-only: write-refusing `dict` and `list` subclasses.
   No production code changed for it.
3. **Every shared row frozen across 41 suites:** 756 passed, and 62,026 rows were served
   read-only (`evidence/TP2/tp2_freeze_all.py`). That covers readers the workloads miss.
4. **Measured:** `deepcopy_nodes` went from 2,760,394 to 115,294 (−95.8%, against a ≥50%
   gate). Key paths stay at 26 and checker runs at 25. Every TP0 digest is identical.
   In-process A/B: 2.82 s copying versus 2.59 s shared, −8.4%.
5. **Review (one reader): accept, nothing blocking.** F1 (completeness): T2 never reached
   the partial-report and anchored readers. Fixed with
   `test_review_f1_frozen_rows_on_anchored_and_partial_paths`, which runs their suites
   under the committed plugin `tests/_tp2_freeze_plugin.py` and is killed by a planted
   write (`evidence/TP2/review-mutants.txt`). F2 (hardening, low): a direct
   `dict.__setitem__` bypasses the guard. No reader does that, and T4 parity caught a
   meaningful bypass write. F3 (info): the accessor's name has no underscore, so only its
   docstring marks it internal.
