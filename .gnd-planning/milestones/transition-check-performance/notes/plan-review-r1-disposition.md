# Plan review: disposition (rounds 1 and 2)

**Reviewed bytes:** plan r3 (SHA-256 `e691348d…92ab`) and TP0 spec r3
(SHA-256 `f0073202…dd7b`).
**Instrument:** four local readers, owner-selected (TP-D7), each with its own
lens. Each reader is one reader, not a panel.
**Repairs:** applied in plan r4 and TP0 spec r4, tagged `(p1)`.

Readers' notes, sanitized only to remove downstream request identifiers:
[reader 1](plan-review-r1-reader-1.md), [reader 2](plan-review-r1-reader-2.md),
[reader 3](plan-review-r1-reader-3.md) and [reader 4](plan-review-r1-reader-4.md).

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| 1 | correctness and CR-01 | approve-with-fixes | 0 | 6 | 4 |
| 2 | implementability | revise | 4 | 10 | 2 |
| 3 | protocol and anonymity | approve-with-fixes | 0 | 11 | 11 |
| 4 | measurement design | revise | 1 | 7 | 4 |

The readers reproduced the key runtime facts by experiment on the anonymized
scratch workload, and their measurements agree: 25 checker runs, 540
`for_model` calls, about 2.77 M deep-copied nodes. Facts were settled by
measurement, not argument.

## Blocking (all fixed in r4)

| Finding | Repair |
|---|---|
| R2-1 counters patched at the defining home miss name-bound lookups | The spec installs counters at every lookup owner, found by a module scan. Checker runs are counted at `_check_dispatch`. Deep copies use a profile hook on the code object. |
| R2-2, R3-08, F9 the batch test expected exit 0 | T3 now expects exit 2 with 0 failures. |
| R2-3, F8 there is no 5-step transition | The spec states that all six transitions are 1-step. The `course` 3-step control covers intermediate checks. T4 is rewritten. |
| R2-4 TP3-C2 cited unavailable parity cases | TP3-C2 now uses the workload replay, the `course` control and the existing contract tests with reference populations and dynamic heads. |
| F1 TP2's gate has no unit and misses the main site | The gate counts copied nodes through the profile hook. `ModelIndex.fact_types` is named as the main target, with an internal non-copying view. |

## Hardening

| Finding | Disposition |
|---|---|
| R1-01, R2-14 "failing pre-check" undefined | Fixed. Proposed definition D-p1-1 (exit 1 or band ≥ 3); needs owner confirmation. |
| R1-02, R2-6, F4 marker digest ≠ ModelIndex key | Fixed. TP1 uses the ModelIndex key. T5 and TP1-C2 cover the operations-only mutation. |
| R1-03 operation copies guard `model.operations` | Fixed. They are kept by default, and any replacement needs a guard test (TP2-C2). |
| R1-04, R1-05 receipt bindings incomplete | Fixed. TP-R3 lists the `CheckReport`, the branch set, the ModelIndex key and the population marker. |
| R1-06, R2-11, F2 minting must not cost a check | Fixed. The mint function returns the payload. The gate is the workload total of 25 → 19. |
| R2-5 the literal scan spells the forbidden name | Fixed. T1 is an allowed-values check. |
| R2-7 threading mechanism unstated | Fixed. §2 proposes a `ContextVar` scope owned by `gnd.model_index`. |
| R2-8 the TP1-C2 test can be fooled by the marker refusal | Fixed. The test checks the index directly, and follows mutate, re-load, check. |
| R2-9, F3 the key counter measures 28% of the cost | Fixed. `model_key_paths` counts every model dump, from any caller. |
| R2-10 deep-copy metric not like-for-like | Fixed. Nodes are counted through the profile hook. |
| R2-12, R1-07 path inputs get a fresh model | Fixed. A named refusal is added to TP3-C3. |
| R2-13 T8 cannot fail | Fixed. T8 is dropped, and TP-R5 is argued in §4. |
| R3-01, R3-02 downstream IDs; bare "M3" | Fixed. Neutral descriptions are used, and the in-repo milestone is named in full. |
| R3-03 "Sealed step programs." / "5-step SUM program" | Kept. Both are generic. The owner can veto them at the TP0 gate (D7). |
| R3-04, R3-05 the transform is the agent's proposal; equivalence is thin | Fixed. Spec D7 is marked as an agent proposal. The proof covers exits, counts, counters and digests. |
| R3-06 plan and spec disagree about the driver | Fixed. The driver is not committed, in both documents. |
| R3-07, F10 CLI, with-post and admission surfaces missing | Fixed. They are in the spec's surface table. |
| R3-09 verification-selection ledger missing | Fixed. Spec §8 now has a verification-selection list. |
| R3-10 rules not bound by name | Fixed. Spec §4 binds TP-R1 to TP-R6. |
| R3-11 receipt threat model | Fixed. §2 states it: accidental reuse, not hostile in-process code. |
| F5 default payloads have no branch traces | Fixed. Traces are captured under `capture_branches()` and digested separately. |
| F6 T6 perturbs only the payload | Fixed. T6 adds runtime mutants. |

## Completeness

Cheap and stale-text items were fixed in r4, because leaving them stale would
mislead the gate reader:

- R2-15, R3-12, R3-14, R3-21: stale restatements of TP-D5 and TP-D6, and
  the PROJECT.md status.
- R3-13: plan revision cited in the spec provenance.
- R3-15: wrong rule reference in the obligations table.
- R3-16: "both files" for three outputs.
- R3-18: readers unnamed, no round budget.
- R3-19: baseline commit mismatch.
- R3-20: the 4.6 s and 3.96 s figures.
- R1-09: n + 2 as an upper bound.
- R1-10: 10 deep-copy sites, not 8.
- F7: the wall-time ceiling, now projected in the Problem section.
- F11: interpreters and variance.
- F12: the attribution question, answered.
- R3-22: admission parity now records whatever band results.

Others are deferred to the phase specs, where their exact values are set:

- R1-08: which field T5 mutates.
- R2-16: the fact-type count wording.
- R3-17: the approval-instrument rationale, now stated in spec §11.

## Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| 1 (r3) | 4 | 10 / 16 / 22 / 12 | n/a (first round) | 5 / 60 | high | 2 approve-with-fixes, 2 revise |
| 2 (r4) | 2 (readers 2, 4) | 9 / 8 | 17 / 17 | 2 distinct / 17 | high | 2 approve-with-fixes |

**Stop rule:** the self-inflicted ratio is 17/17, above one half. The review
stops after r5 applies the round-2 fixes, and no third round runs (plan §8).
r5's repaired sentences, marked `(p2)`, carry no review opinion of their own.

## Round 2: confirmation over r4

Reviewed: plan r4 (`9b21a824…8fdf`) and spec r4 (`64731157…f45d`). Notes:
[reader 2](plan-review-r2-reader-2.md) and [reader 4](plan-review-r2-reader-4.md).

Status of the round-1 findings:

- **Reader 2:** 11 of 16 discharged, 5 partly (all five are covered by r5).
- **Reader 4:** 7 of 12 discharged, 5 partly (all five are covered by r5).
- None is undischarged.

| Finding (reader) | Class | Repair in r5 |
|---|---|---|
| N1 (2 and 4) `model_key_paths` counts every dump (997), so TP1 can never meet its bound | blocking | Split into `model_index_key_paths` (dumps made by `gnd.model_index`, about 540) and `model_dumps_other` (must not increase). Plan TP1-C1, predicate 3 and TP-D6 updated. |
| N2 (2) / N3 (4) `course` steps lack the document header, so they exit 3 | blocking | Wrapped with `plan_apps/core.py:steps_document`. `attempt-3` exits 0 with exactly 5 checker runs; `attempt-1` and `attempt-2` exit 1, giving the failing-receipt case. Spec D8. |
| N2 (4) `capture_branches` returns a set, so a reorder mutant is vacuous; the receipt branch binding is untestable via parity | hardening | Trace digest taken over sorted ids. T6 uses a drop-one mutant. TP3-C2 adds a direct emptied-branch-set receipt test. |
| N3 (2) a computed post as declared post makes every call exit 1 | hardening | The declared post is the next check population. |
| N4 (2, 4) there is no `gnd transition` command | hardening | The CLI transition arm is `gnd check --pre --steps --post`. T3 compares digests, not only exits. |
| N5 (2, 4) normalization undefined | hardening | `NORMALIZED_FIELDS` is defined exactly: the input-path fields. |
| N6 (4) / N9 (2) timings instrumented | hardening | Timing runs are separate and uninstrumented. |
| N7 (4) TP1 bound worded inconsistently | completeness | Reworded the same way in predicate 3, TP1-C1, §9 and TP-D6. |
| N8 (4) / N7 (2) T4 frame unnamed | completeness | T4 deep-copies through `ModelIndex.fact_types`. |
| N5 (2) classmethods need class patching | completeness | Stated in spec §6. |
| N8 (2) receipts must not require the same population object | hardening | Plan §2: binding by content digest plus a valid marker on the presented object. |
