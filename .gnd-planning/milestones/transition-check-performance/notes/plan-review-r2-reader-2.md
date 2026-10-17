# Plan review round 2 (confirmation): reader 2 of 4

- **Lens:** implementability against the actual code and the repository rules.
- **Repository:** HEAD `2d1ff4d`; the runtime under `src/gnd` is unchanged. Nothing in the repository was edited. Experiments ran with `uv run python -I` (CPython 3.14.3) on the scratch anonymized bundle.
- **Artifacts (shasum -a 256):**
  - `9b21a824d8f1d463ee0877ced6640f9880fdac12412afbcb25d9b1e3736a8fdf`  `notes/transition-check-performance-plan.md` (r4)
  - `647311577cc7893584c803343452cc97d31403c9d74fd9f6ed4ae83449d5f45d`  `notes/phase-TP0-spec.md` (r4)
  - `d533d800bd591e3afd3ca49d38ebd087c69f609555f5184fd8a8016f36713549`  `notes/plan-review-r1-disposition.md`

## 1. Round-1 findings: does r4 discharge them?

| ID | Discharged | Evidence |
|---|---|---|
| R2-1 counters missed name-bound lookups | **yes** | Spec §6 counts at every lookup owner. `checker_runs` is counted at `_check_dispatch` and deep copies through a profile hook. Verified by E7: `_check_dispatch` counts 25 on the replay, plus 1 each for `compiled_operations=True` and `admission=True` (27 total), so it covers every route. The profile hook on `copy.deepcopy.__code__` works: 3,000,645 invocations and 1,389 outermost GND-caller calls, including the two extra surfaces and the loads. The new key-path counter is wrong; see N1. |
| R2-2 T3 expected exit 0 | **yes** | Spec T3 now expects exit 2 with 0 failures. Verified in round 1 (E3). |
| R2-3 no 5-step walk, no posts | **partly** | The spec now states that all six transitions are 1-step and T4 is rewritten. The two replacements are defective: the `course` control as specified exits 3 (N2), and "declared post = computed post" yields a failing walk (N3). |
| R2-4 TP3-C2 parity cases unavailable | **yes** | TP3-C2 now cites the workload, `course`, and the existing reference-population and dynamic-head contract tests. The `course` part depends on N2. |
| R2-5 literal scan spelled the forbidden name | **yes** | T1 is an allowed-values check. |
| R2-6 marker digest is not the ModelIndex key | **yes** | Plan §2 and TP-D1 now use the ModelIndex key. T5 covers the operations-only case. Verified by E8: after an operations-only mutation the marker is still True and the key changes. |
| R2-7 threading mechanism unstated | **yes** | Plan §2 proposes a ContextVar scope owned by `gnd.model_index` and entered by `api`, `checking_service`, `transition`, `checker._core` and the population loader. It is layer-legal, as round 1 showed. |
| R2-8 TP1-C2 could be fooled | **yes** | TP1-C2 now checks the index directly, follows mutate, re-load, check, and includes an identity-keyed mutant. |
| R2-9 key counter moves with the code | **partly** | The counter now counts every `Model.model_dump`, so moving the key computation can't hide it. But it over-counts so much that TP1-C1 is unreachable (N1). |
| R2-10 deep-copy metric not like-for-like | **yes** | `deepcopy_nodes` is counted through the profile hook, and TP2-C4 gates on nodes (E7). |
| R2-11 minting must not cost a check | **yes** | The mint function returns the `api.check` payload, and the gate is the workload total 25 → 19. |
| R2-12 path inputs and forged receipts | **yes** | TP3-C3 adds a path-input refusal. The threat model is limited to accidental reuse, which removes the in-process forgery requirement consistently. |
| R2-13 T8 could not fail | **yes** | T8 is dropped, and TP-R5 is argued in spec §4. |
| R2-14 "failing" undefined | **partly** | D-p1-1 proposes exit 1 or band ≥ 3 as failing. It is still pending owner confirmation, which is acceptable. |
| R2-15 stale text and pins | **yes** | TP-D5 and TP-D6 are restated. TP3-C4 lists `test_v61_phase2_api.py`, `test_public_runtime.py` and the `__all__` order. Spec provenance cites r4 and the baseline `2d1ff4d`. Interpreters are recorded. |
| R2-16 fact-type count; admission | **partly** | Admission is now recorded whatever band it lands in (yes). The fact-type count wording is deferred to the phase spec (acceptable). |

**Summary:** 11 discharged, 5 partly, 0 not discharged.

## 2. New findings

| ID | Self-inflicted | Class | Severity | Claim | Evidence | Proposed fix |
|---|---|---|---|---|---|---|
| N1 | yes | blocking | high | `model_key_paths` = "`Model.model_dump` from any caller" (spec §6) counts many dumps that are not key computations. That makes TP1-C1 ("at most 1 per public call, plus 1 per loaded intermediate and loaded population") and completion predicate 3 unreachable by the TP1 design. On the baseline there are 25 dumps per `api.check`, 124 per transition and 6 per load, but only 13, 64 and 5 come from `for_model`. The others come from `values._model_digest` (the CR-01 marker; 225 over the run, at least one per check by design), `applicability.applicable_scope_ids` (81), `extensions._evaluate_stratified_extensions` (39), `structured_extension_view` (36), `semantic_adapter.adapt_snapshot` (27), and transition helpers (6–18 each). TP1 removes none of them. | E7 dump-site attribution. Plan :94-96 and :246-248; spec :150. | Keep the total dump count as a counter, but gate on a quantity that moving code cannot hide. Option (a): `model_key_paths` = dumps whose caller frame is in `gnd.model_index`, plus a static check that the ModelIndex key function has one home. Option (b): a relative gate, `dumps_total(after) ≤ dumps_total(before) − for_model_dumps(before) + allowance`, where the allowance is the TP-D6 bound. Restate TP1-C1 and predicate 3 in that unit. |
| N2 | yes | blocking | medium | The `course` control is specified as `plans/attempt-3.steps.json`, "unchanged", described as "a 3-step walk, so it exercises intermediate checks". Through both `api.transition` and the CLI it is **refused with exit 3 and 0 checker runs**: the file has only `steps` and lacks `steps_schema`, `model`, `model_digest` and `operations_digest`. The T4 `course` clause cannot hold, and the `course` legs of the TP3-C2 and TP0-C3 parity are vacuous. | E9: `transition:steps-shape` issues. With the envelope from `plan_apps/core.py:61-64` (`steps_document`), the same walk exits 0 with 5 checker runs (n + 2). | The tool builds the `course` step document with the `steps_document` envelope (or an equivalent recorded inline), and pins exit 0 with 5 checker runs. |
| N3 | yes | hardening | medium | The with-post surface uses "the declared post is the computed post of the same call". `computed_post` is a `{population, facts}` dict, and the spec does not say how it becomes a `Population`. Loaded whole, it makes every reporter transition exit **1**, with 29–31 `post_snapshot` derivation failures, because the computed post asserts derived facts. The surface therefore measures a failing-derivation path that the reporter never runs. Using the next check population as the declared post gives exit 2 with 0 failures. | E10 (calls 01, 05, 11) | Use `(NN+1)-check-population.json` as the declared post for transition NN, and pin its exit. |
| N4 | yes | hardening | medium | `gnd transition MODEL PRE STEPS` does not exist (spec surface table and T3; plan predicate 2). The transition arm is `gnd check MODEL --pre PRE --steps STEPS`. An argparse invalid-choice error also exits 2, the same as the pinned exit, so T3's exit half would pass vacuously. Only the digest half would catch it. | `gnd --help` subcommand list; `gnd check --help` | Name the actual command in the plan, the spec and T3. |
| N5 | yes | hardening | low | The installer, "scan every loaded `gnd.*` module for attributes that are that object", does not fit method targets. `ModelIndex.for_model` (a classmethod) and `Model.model_dump` have to be patched on the class. Modules imported after installation bind the wrapper and keep it after uninstall. | `model_index.py:52`; lazy imports such as `_core.py:364` and `compiled_obligations.py:79` | Import every `gnd` module before installing, patch class attributes for methods, and restore with a second scan. |
| N6 | yes | completeness | low | T3 compares CLI and API payload digests. They are equal only when the API receives paths, or when normalization removes the `model` and `population` coordinate fields. Object inputs emit `null` there, while the CLI emits the path. "Removes only absolute paths" is ambiguous on this point. | E11: path-API vs CLI identical; object-API differs only at `/model` and `/population` | `NORMALIZED_FIELDS` names the coordinate fields `model` and `population`, normalized to null. |
| N7 | yes | hardening | low | T4's deep-copy liveness needs a deep copy "from a frame under `src/gnd`", but test code runs under `tests/`. | `model_index.py:39-41` deep-copies exactly once | Name the probe, for example `ModelIndex(None, doc)` built from a known three-level document, with the expected node count. |
| N8 | yes | hardening | low | The receipt binds "the population's validation marker", but the reporter replay loads each transition population as a **separate object** from a byte-identical file. If identity were required, TP3-C2's 25 → 19 replay would be refused. | `00-check` vs `01-transition` populations: byte-identical files, separate `load_population` calls | State that the receipt matches on content digest plus a valid marker against the same model object, not on population identity. |
| N9 | yes | hardening | low | The profile hook slows the replay about 2.8 times (19.8 s against about 7 s). The spec does not say that timing runs exclude instrumentation. | E7 elapsed time | `timings.json` comes from uninstrumented runs. Counters come from a separate instrumented run. |

**New findings:** 9 total; 9 self-inflicted (all attack text r4 created or changed); 2 blocking (N1, N2).

## 3. Experiment commands and outputs

- **E7.** `uv run python -I scratchpad/plan-review/r2exp/r2.py <bundle>`. It wraps `_core._check_dispatch` and `Model.model_dump` with frame attribution, and installs `sys.setprofile` on `copy.deepcopy.__code__`.
  ```
  compiled dispatch 1 / admission dispatch 1 (exit 2) / elapsed with hook 19.8s
  (0,'check',{'load_dumps':6,'call_dumps':25,'dispatch':1})  (1,'transition',{'load_dumps':6,'call_dumps':124,'dispatch':3})
  TOTAL {'model_dump':1052,'dc_nodes':3000645,'dc_top_gnd':1389,'dispatch':27}
  dump sites: model_index.for_model 572; values._model_digest 225; applicability.applicable_scope_ids 81;
              extensions._evaluate_stratified_extensions 39; extensions.structured_extension_view 36;
              semantic_adapter.adapt_snapshot 27; transition._effective_extension_state 18; ...
  ```
- **E8.** After an operations-only mutation: `marker True`, `key changed True`.
- **E9.** `course`: `api.transition(model, state.pop.json, attempt-3.steps.json)` → exit 3, 0 checker runs. The CLI also exits 3 (`transition:steps-shape`: `steps_schema`, `model`, `model_digest` and `operations_digest` required). With the `steps_document` envelope: exit 0, 5 checker runs.
- **E10.** Declared post = `transition.computed_post` (full dict) → exit 1 with 31, 31 and 29 failures on calls 01, 05 and 11, all `/transition/post_snapshot/derivations[...]`. Declared post = next check population → exit 2 with 0 failures.
- **E11.** CLI JSON vs `api.check(path, path)`: identical. Vs `api.check(Model, Population)`: differs only at `/model` and `/population` (`null` vs path). The transition shows the same pattern at `/model`.

## 4. Verdict

**approve-with-fixes.** All 4 round-1 blockers are discharged or reduced. The counter design is implementable as specified: `_check_dispatch` covers every check route, and the profile hook counts nodes. Two new blockers remain, N1 (an over-counting key-path unit) and N2 (a `course` control refused at load). Both are r4 text with verified, mechanical fixes. Every new finding is self-inflicted (9 of 9), so the declared stop rule applies: fix N1 and N2, optionally N3 and N4, and record them without another round.
