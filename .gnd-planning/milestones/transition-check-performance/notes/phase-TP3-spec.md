# Phase TP3: Opt-in, receipt-bound pre-state reuse

## 1. Status

**Owner-approved (o6), 2026-10-17** ("approve TP3"). The approved bytes have SHA-256
`8f842c6f1532a0c837fa393f8e6b83be43545bfdcdcea9c3be9a1326e20296e7`. D1–D4 are accepted as proposed. The implementer is Codex CLI. The
spec is append-only from here.

## 2. Provenance

- Plan r5, owner-approved ([plan gate](../001-plan-gate.md)): TP-R3, §2 TP3, §4
  TP3-C1..C4, TP-D3, TP-D5, D-p1-1 (exit 2 is not failing) and D-p1-2 (workload total
  25 → 19).
- TP0–TP2 records (002–004).
- Inspection at TP2 head `dc39e4b`:
  - `checking_service._run_check` / `_run_check_raw` build the `api.check` payload from a
    `CheckReport` and accept an `evaluator` hook (`checking_service.py:310`).
  - `transition._evaluate_to_state` runs `check(model, pre)` inside
    `calculation_scope(model, pre)` (`transition.py:1919-1923`).
- No review has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| TP-R3 | Skip only the pre-state check. Explicit opt-in. A GND-minted receipt binding the model object, ModelIndex key, population content digest and marker, options, `CheckReport` and branch set. Never a bare digest or JSON | §6, T3 |
| TP3-C1 | Receipts are minted only by the opt-in function, whose payload is identical to `api.check`'s | §6 mint, T1 |
| TP3-C2 | Reporter replay with receipts totals 19 checker runs instead of 25, with all 13 payloads identical; `course` and the existing contract tests are identical with receipts; a direct branch-set test | T2, T4, T5 |
| TP3-C3 | Named refusal before evaluation for each mismatch | T3 |
| TP3-C4 | Docs and public pins | §6 docs, T6 |
| D-p1-1 | Exit 0 or 2 mints a reusable receipt; exit 1 or ≥ 3 mints a non-reusable one | §6, T3 |
| D-p1-2 | The gate is the workload total, and minting adds no checker run | T1, T2 |
| O6, O7, O11 | Request 3; the earlier repairs-milestone boundary is superseded for this opt-in only (TP-D3); docs | §6, T6 |

## 4. Rules bound to TP3

Standing rules:

1. **Totality:** the receipt argument is checked by type first. Any object that is not a
   GND-minted `CheckReceipt` is refused (`foreign`), and nothing in it is read.
2. **Bounds:** a receipt holds one report and one branch set. Validation costs one key
   path (already counted) and one population digest.
3. **Validation order** is pinned by T3 and by source order in `transition.py`:
   type, then reusable, then options, then model object, then model key, then population
   marker, then population digest. All of these run before any evaluation.
4. **One walk:** one validator function serves the API.
5. **One home:** the receipt contract lives in the `CheckReceipt` docstring.
   `python-api.md` cites it.
6. **Measurement:** T2 measures 25 → 19 directly.

Plan rules:

- **TP-R1:** T2, T4 and T5 compare payload and trace digests with and without receipts.
- **TP-R2:** the model-key and population checks in T3 cover mutation.
- **TP-R4:** counters gate.
- **TP-R5:** no new cache. The receipt is a caller-held value.
- **TP-R6:** no downstream names.

## 5. Goal

Running `uv run pytest -q tests/test_tp3_check_receipts.py tests/test_tp2_shared_fact_types.py
tests/test_tp1_index_scope.py tests/test_transition_cost_workload.py tests/test_public_api.py
tests/test_public_reference_signatures.py tests/test_v61_phase2_api.py tests/test_public_runtime.py
tests/test_public_transition_contract.py tests/test_public_transition_trace.py` exits 0. The
receipt replay measures `checker_runs == 19`. Default behaviour, with no receipt, is unchanged:
25 checker runs and every TP0 digest identical.

## 6. Design

### Public surface (`src/gnd/api.py`, about 90 lines)

```python
class CheckReceipt:                       # opaque; not constructible by callers
    """Proof, held in this process only, that GND checked ``population`` against
    ``model`` with default options. A transition may then skip re-checking that pre-state.
    It binds the model object, the model's ModelIndex key, the population's content digest
    and validation marker, the options, the internal CheckReport and the branch ids that
    check recorded. It cannot be serialized. It is reusable only when the check exited
    0 or 2."""

class ReceiptRefused(ValueError):
    reason: str   # one of the REASONS below

def check_with_receipt(model: Model, population: Population, *,
                       unredacted: bool = False) -> tuple[dict[str, Any], CheckReceipt]: ...

def transition(model, pre, steps, post=None, *, unredacted=False, references=None,
               pre_receipt: CheckReceipt | None = None) -> dict[str, Any]: ...
```

`api.__all__` gains `check_with_receipt`, `CheckReceipt` and `ReceiptRefused`, appended at
the end so the existing order is kept.

### Minting: one checker run, the same payload as `api.check`

1. Refuse path inputs with a `TypeError`. Only loaded `Model` and `Population` objects are
   accepted.
2. Inside `index_scope()`, `calculation_scope(model, population)` and `capture_branches()`,
   run `report = checker.check(model, population)` and keep the captured branch ids.
3. Build the payload through `_run_check(model, population, unredacted=unredacted,
   evaluator=lambda m, p: report)`. That is the same builder `api.check` uses, and the
   evaluator returns the precomputed report, so no second checker run happens.
4. The receipt is reusable when the payload's exit code is 0 or 2 (D-p1-1).

A model that takes the anchored route, or whose ModelIndex key is `None` (cannot be
cached), gets a non-reusable receipt, because the transition's pre-check is the plain
`checker.check`.

### Use: `api.transition(..., pre_receipt=r)`

`_run_transition` validates `r` before any evaluation, in this order, raising
`ReceiptRefused(reason)` on the first failure:

| Reason | Condition |
|---|---|
| `foreign` | `r` is not a `CheckReceipt` |
| `path-inputs` | the model or pre-state was given as a path |
| `not-reusable` | the minting check exited 1 or ≥ 3, the model is anchored, or the key was `None` |
| `options` | `references` is not `None` |
| `model-object` | `model is not r.model` |
| `model-changed` | `ModelIndex.for_model(model).digest != r.model_key` |
| `population-unvalidated` | `not pre.matches_validation_marker(model)` |
| `population-changed` | `values._content_digest(pre) != r.population_digest` |

A different `Population` object with the same content is accepted (TP2 review N8).

On success, `transition._evaluate_to_state(model, pre, steps, pre_receipt=r)` uses
`r.report` as `pre_snapshot`. It records each id in `r.branches` with `record_branch`, so
captured traces are identical. It skips only `check(model, pre)`. Everything else in the
pre-phase runs unchanged: compiled walk verdicts, state construction, the extension view,
every intermediate check and the post check.

### Docs

- `docs/reference/python-api.md`: a "Reusing a checked pre-state" section that cites the
  `CheckReceipt` docstring, gives the refusal reasons, and states the non-goals: no
  serialization, no CLI, and default options only.
- `docs/reference/capabilities.md`: one row.
- `docs/release-notes.md`: one line.

### Measurement tool

`tools/measure_transition_cost.py` gains `replay("reporter-receipts")`. It mints each check
with `check_with_receipt` and passes that receipt to the next transition.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | What happens with a failing pre-check? | Mint a non-reusable receipt that the transition refuses with `not-reusable` (proposed: explicit and testable). The alternative returns `None`, which makes callers branch, and its refusal case is untestable. |
| D2 | Options supported | Default only: no `compiled_operations`, `admission`, `anchors` or `references` (proposed). Those modes produce different reports, and the transition's pre-check is the default check. |
| D3 | Branch replay | Re-record the minting check's branch ids (proposed). Without it, traces lose ids, and only the direct test notices (plan TP3-C2). |
| D4 | Implementer | Codex CLI, as for TP2. The session reviews the diff, runs the gates, and an independent local reader checks it. |

## 8. Tests

The new file is `tests/test_tp3_check_receipts.py`.

| # | Case | Expected |
|---|---|---|
| T1 | For each of the 7 reporter check populations and the `course` pre-state, `check_with_receipt`'s payload digest and trace digest equal `api.check`'s. Minting runs exactly 1 checker run. | pass |
| T2 | Reporter receipt replay: `checker_runs == 19`. Its 13 payload digests and trace digests equal the replay without receipts. The replay without receipts still measures 25. | pass |
| T3 | Each refusal reason is raised, with `.reason` set, and no checker run happens (`checker_runs == 0` during the refused call): a foreign object; path inputs; not-reusable (a population edited to exit 1, and an anchored-model case if a fixture exists, otherwise argued in the record); `references` set; another model object; an operation edited after minting; a population that lost its marker; a population edited after minting. Also checked: a different `Population` object with equal content is accepted. | pass |
| T4 | `course`: the `attempt-3` transition with a receipt from the pre check gives an identical payload and trace, and one fewer checker run (5 → 4). | pass |
| T5 | Direct branch-set test: a receipt mutant whose `branches` is emptied changes the transition's trace digest. A mutant whose `report` has one verdict's modality flipped changes the payload digest. | pass |
| T6 | Public pins: `test_public_api.py`, `test_public_reference_signatures.py`, `test_v61_phase2_api.py` and `test_public_runtime.py` are updated for the three new names and the keyword. The `__all__` order is kept with the new names appended. | pass |
| — | Existing transition contract and trace suites pass unchanged, without receipts. | pass |

**Verification selection:**

- **Run:** the §5 command, plus TP1's affected-consumer batches. Run once per
  interpreter (3.14, 3.11, 3.13) at the end of the phase.
- **Slow cadence:** the broad suite, run only on owner selection.

## 9. Out of scope

- Serialized or cross-process receipts.
- A CLI flag.
- Receipts for `compiled_operations`, `admission`, anchors or references.
- Skipping intermediate or post checks.
- Incremental evaluation (TP4, deferred).

## 10. Size

About 90 lines in `api.py`, about 15 in `transition.py`, about 20 in the tool, about 40 lines
of docs, and about 220 lines of tests.

## 11. Approval instrument

This prose. Its gate values are 19 checker runs, identical digests, and one refusal
reason per mismatch.

## Implementation findings, recorded as they were found

1. **The spec's anchored-model minting was not implementable as written.** Codex found
   this before editing anything. `_run_check_raw` ignores the `evaluator` hook on the
   anchored route (`checking_service.py:293`), so pre-running `checker.check` and then
   building the payload would run two checks, which breaks TP3-C1's one-check rule.
   Resolution: when the model has anchored constraints, minting skips the pre-run, builds
   the payload through the normal `_run_check` path (one anchored check), and returns a
   non-reusable receipt. Anchored receipts were already non-reusable (§6), so no approved
   outcome or expected test value changes: one checker run per mint, and `not-reusable` for
   anchored models. No file outside the approved list is touched. This is flagged to the
   owner in the session report.
2. **A second spec gap, also found by Codex.** A population that has lost its validation
   marker gets a refusal payload (exit 70) from `api.check`, but the direct pre-run raises
   `UnvalidatedPopulationError`. Resolution (session): the direct route runs only when the
   model is not anchored **and** the marker is valid. Any other case, or a pre-run that
   raises, takes the normal `_run_check` route with a non-reusable receipt, so the payload
   always equals `api.check`'s. No approved outcome changes. Test:
   `test_finding_unvalidated_population_mints_like_api_check`.
3. **Receipts were already immutable.** `CheckReceipt` is a frozen dataclass. An attempt to
   add `__setattr__` was reverted. `test_finding_receipt_is_immutable` pins the behaviour.
4. **Review B1 (blocking, fixed).** Minting ran `checker.check` before the `api.check`
   builder, so the builder's certification trace lacked the checker's branch ids
   (6 ids instead of 15, `complete=False`). Wherever release assurance evidence is
   installed, receipts would have reported `assurance_level: none` while `api.check`
   reported a higher level. Fix: the evaluator hook re-records the pre-run's branch ids
   inside the builder's capture. `test_review_b1_mint_certifies_against_the_same_trace_as_api_check`
   compares the certification trace and the execution's completeness between the two
   routes. It is killed by the pre-fix evaluator (`evidence/TP3/review-mutants.txt`).
5. **A regression found by the consumer gate (fixed).** `api.transition` passed
   `pre_receipt=None` to `transition.evaluate` and `evaluate_plan` on every call, which
   broke `test_public_transition_api_guards.py::test_transition_internal_fault_returns_70`.
   That test substitutes a positional-only `evaluate`. The keyword is now passed only
   when a receipt is given, so the default call shape is the same as before TP3.
6. **Review, accepted as boundaries.**
   - H1 (low): `receipt.report` is a mutable `CheckReport`. Reaching in and editing it
     changes a later transition, which is outside the threat model of accidental reuse.
   - H2 (low): a pre-run that raises is followed by the normal route, so two checker
     attempts run, both on a non-reusable path.
   - C1: there is no reference-population receipt test. The reviewer probed two
     reference corpora and found no defect.
   All three are recorded as open questions for milestone close.
