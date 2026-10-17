> Retained verbatim except one sanitization: the reviewer's label for mutant 10 is written
> `MU10`, so it cannot be read as a downstream milestone ID.

# TP3 independent diff review — transition-check-performance

- Branch: claude/transition-check-performance-tp3 (working tree over HEAD dc39e4b)
- SHA-256 src/gnd/api.py: 2d0ced5ddbb403852b450dc21bf14dc693915bbe12cdb70306d31aa865295465
- SHA-256 tests/test_tp3_check_receipts.py: 5642bbebcfe0985e2307012ee45547f9bb365100894cee61a64e340714c3b663
- SHA-256 src/gnd/transition.py (context): d3883314bfe0101cbd8925d9efd32d6d79d1cdf8abe8894c5302d3c2f47a5302
- Reviewer: single independent reviewer. No repository file edited. Probes and mutant copies live
  only under this scratchpad directory (`probe_*.py`, `mutate.py`, `runm.sh`, `mut/`).
- Baseline: `uv run pytest -q tests/test_tp3_check_receipts.py` -> 8 passed.

## Findings

| ID | Class | Severity | Finding | Reproduction |
|---|---|---|---|---|
| B1 | blocking | medium-high (latent in dev, live wherever release assurance evidence is installed) | **Minting certifies assurance against the wrong trace.** On the direct route, `checker.check` runs *before* `_run_check`. `_run_check_raw` then opens its own `capture_branches() as semantic_trace` around `evaluator=lambda m, p: report`, which records nothing. `_certify_assurance(..., semantic_trace \| projection_trace)` therefore gets a trace without the checker's verdict and report scope ids, so `_mint_execution` computes `complete=False` (`expected <= set(trace)` fails). `derive_assurance_scope` then returns `valid=False`, and `certify_result` passes `guards_valid=False`, so the level is forced to `"none"`. `api.check` on the same inputs has a complete execution with `scope.valid=True`. In this checkout `load_assurance_evidence().available` is False, so both levels are already `"none"` and T1 and T2 pass. In an installed package with release evidence, `check_with_receipt` would report `assurance_level: none` where `api.check` reports `partial`/`proof-backed`. That breaks TP3-C1 ("payload identical to api.check") and makes the docs line "The payload is the same as `check` produces" false. `_RunResult.execution` also differs (complete True vs False). The outer caller trace still matches only because nested captures propagate upward. | `probe_assur.py`: course model, spy on `checking_service._mint_execution`: api.check trace=15 ids, complete=True; check_with_receipt trace=6 ids, complete=False. `probe_assur2.py`: `derive_assurance_scope(...).valid` = [True, False]. Fix (validated as mutant M13, all 8 TP3 tests still pass): replay the stored ids inside the evaluator, e.g. `evaluator=lambda m, p: (_replay(branches), report)[1]` with `record_branch` from `gnd.branches`, or run the pre-check inside `_run_check_raw`'s capture. Add a test that compares `result.execution.complete` / `scope.valid`, or forces evidence availability, between the two routes. |
| H1 | hardening | low | `receipt.report` is a shared, mutable `CheckReceipt` pydantic object. `frozen=True` stops attribute rebinding, but `receipt.report.verdicts.clear()` (no `object.__setattr__` needed) is then accepted and changes the transition result. The docstring scopes the guarantee to accidental reuse, not hostile code, but this is accidental-mutation territory (a caller post-processing the report). | `probe_reuse.py`: after `r.report.verdicts.clear()` the reused transition payload is not equal to a fresh transition. Options: store `report.model_copy(deep=True)` and hand `_evaluate_to_state` a copy, or record a report digest and refuse on mismatch. |
| H2 | hardening | low | If `checker.check` raises on the direct route, minting falls back to `_run_check`, which runs the checker a second time (2 checker runs, against the one-check rule). The failed attempt's branch ids have already reached the caller's outer captures. The receipt is non-reusable either way, so nothing wrong is accepted. | Code reading, api.py `check_with_receipt` `except Exception: direct = False`. Not reproduced with a fixture. |
| C1 | completeness | low | No test covers models with `reference_populations` (embedded references, `references=None`). I probed both reference-corpus fixtures (dispatch, release). Mint payload equals api.check, receipts are reusable, and the transitions are equal, because the checker binds internally (`checker/_core.py:2060`) and the reference file sha256 is pinned in the model. No defect, just no coverage. | `probe_ref.py`, `probe_ref2.py`. |
| C2 | completeness | low | T5 checks that branches are replayed using `_evaluate_to_state` with no steps, and T4 checks it via course trace parity. No test checks the mint-side trace that is fed to assurance certification. That gap is why B1 survives. | See B1. |

### Probed and found sound (not findings)

- Model mutated in place, including operations only: `ModelIndex.for_model` recomputes the canonical digest over `model_dump(exclude warnings)`, including operations. The value is not cached on the object, and `_run_transition` opens a new index scope, so the result is `model-changed` (T3 and mutant M1).
- Equal-content model object: `model-object`. Equal-content population object: accepted, which is correct because the report depends only on content (T3 and probes).
- Population mutated: `population-unvalidated` (the marker digest no longer matches) or `population-changed` (a re-validated population with different content). Fields outside the digest: only `warnings`, which the checker does not read.
- Anchored model, uncacheable key, unvalidated population, exit 1 and exit 3 or higher: all non-reusable, so the transition refuses with `not-reusable`.
- `references` set: `options`. Path model or pre-state: `path-inputs`. Validation runs as the first statement of `_run_transition` (inside `@_index_scoped`), before `_run_transition_raw` loads paths or steps, so `checker_runs == 0` on every refusal (T3).
- Order matches the spec table: foreign, path-inputs, not-reusable, options, model-object, model-changed, population-unvalidated, population-changed.
- Declared-post `evaluate` route: equal payloads with and without the receipt (course, exit 1). A receipt reused three times in a row, and with `unredacted=True`, gives payloads equal to fresh ones.
- Forgery: `CheckReceipt()` raises, and `copy.copy`, `copy.deepcopy`, `pickle.dumps` and `dataclasses.replace` all raise TypeError (`__reduce__`). `object.__new__` without the token gives `foreign`. Bypassing these needs deliberate private-attribute access (`gnd.api._RECEIPT_TOKEN`, `object.__setattr__`), which the docstring explicitly excludes.
- Transition-side trace: the receipt's branch ids are re-recorded inside `calculation_scope` and inside `_run_transition_raw`'s `semantic_trace` capture. Transition assurance certification therefore sees the same trace as a fresh walk (T4 and T5 parity hold).
- Public pins: `__all__` keeps the old order with the three names appended. `pre_receipt` is keyword-only, defaults to None, and comes last. The four pin tests and the docs table agree with the code.

## Mutants (each applied to a scratch copy of `src/gnd`, run against tests/test_tp3_check_receipts.py)

| Mutant | Outcome | Caught by |
|---|---|---|
| M1 drop `model-changed` check | killed | test_t3_refusals_and_order |
| M2 drop `population-changed` check | killed | test_t3_refusals_and_order |
| M3 drop `population-unvalidated` check | killed | test_t3_refusals_and_order |
| M4 accept `references` | killed | test_t3_refusals_and_order |
| M5 drop `model-object` check | killed | test_t3_refusals_and_order |
| M6 do not replay receipt branches in `_evaluate_to_state` | killed | test_t4_course_parity, test_t5 |
| M7 run a fresh pre-check anyway | killed | test_t2 (25 != 19), test_t4, test_t5 |
| M8 `reusable` ignores exit code | killed | test_t3_refusals_and_order |
| M9 drop token check (isinstance only) | killed | test_t3_refusals_and_order (forged `object.__new__`) |
| MU10 drop `not-reusable` check | killed | test_t3 x2, test_finding_unvalidated |
| M11 swap not-reusable / options order | killed | test_t3_refusals_and_order |
| M12 anchored models take the direct route | killed | test_t3_anchored_and_uncacheable |
| M13 (fix candidate for B1) replay stored ids inside the mint evaluator | survives, as intended: 8 passed | shows the fix is compatible with the gates |
| (implicit) current B1 behaviour, mint-side assurance trace incomplete | **survives** | no test; see C2 |

## Verdict

**Not converged: one blocking finding (B1).** The reuse guards are sound. I could not
build an accepted-but-wrong transition under the stated threat model: every validation
mutant is killed, and refusals happen before any evaluation. However, `check_with_receipt`
does not produce the same assurance certification as `api.check`, because the checker's
branch ids never reach `_run_check_raw`'s certification trace. The payloads match today
only because this checkout has no release evidence. Fix B1 with the M13-style replay and
add a falsifying test, then re-review. H1 and H2 are optional hardening. C1 and C2 are
test-completeness notes.
