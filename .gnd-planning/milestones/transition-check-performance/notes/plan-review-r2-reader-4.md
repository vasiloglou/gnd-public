# Plan review, confirmation round (round 2): reader 4 of 4

- **Lens:** measurement and test design. Are the gates falsifiable, and do they measure what the milestone promises?
- **Subject bytes** (working tree, HEAD `2d1ff4d`):
  - `9b21a824d8f1d463ee0877ced6640f9880fdac12412afbcb25d9b1e3736a8fdf`  `transition-check-performance-plan.md` (r4)
  - `647311577cc7893584c803343452cc97d31403c9d74fd9f6ed4ae83449d5f45d`  `phase-TP0-spec.md` (r4)
  - `d533d800bd591e3afd3ca49d38ebd087c69f609555f5184fd8a8016f36713549`  `plan-review-r1-disposition.md`
- **Environment:** Apple M5 Max, CPython 3.14.3, current bytes. No repository file was edited. Scripts are in `scratchpad/exp/` (`r2.py`, `course.py`, plus round-1 scripts).

## New measurements (round 2)

**R2-M1. Callers of `Model.model_dump` over the 13-call replay** (`exp/r2.py`, profile hook on `Model.model_dump.__code__`):
```
Model.model_dump total 997
    540 model_index.py:for_model
    212 values.py:_model_digest            (marker digest; CR-01 recompute)
     75 applicability.py:applicable_scope_ids
     37 extensions.py:_evaluate_stratified_extensions
     36 extensions.py:structured_extension_view
     25 semantic_adapter.py:adapt_snapshot
     18 transition.py:_effective_extension_state
     12 transition.py:_dynamic_heads_for_step
     6+6+6+6 other transition.py sites
```
457 of the 997 dumps are not ModelIndex key paths.

**R2-M2. Where the `for_model` calls happen, inside or outside a public call:** 65 outside (13 explicit loads × 5), 475 inside, and 150 of those inside internal loads. This confirms the plan's "65 of 540" figure.

**R2-M3. The branch trace is a set** (`src/gnd/branches.py:1360`, `capture_branches() -> Iterator[set[str]]`, `reached.add(scope_id)`). Experiment on call 01: a normal transition reaches 26 branch ids. A transition whose pre-check is replaced by a precomputed report, with no branch replay, also reaches 26. The sets are equal, and the payloads are equal.

**R2-M4. The `course` control, unchanged** (`exp/course.py`):
```
api.transition(model, pop, attempt-N.steps.json)   -> exit 3 (ill_formed), checker_runs 0, for N = 1, 2, 3
  issues: 'steps_schema' / 'model' / 'model_digest' / 'operations_digest' is a required property
same, with path inputs                              -> exit 3, checker_runs 0
with the plan-app header (examples/plan_apps/core.py:50,63: steps_schema 1, model, model_digest, operations_digest):
  attempt-1 exit 1 checker_runs 5 ; attempt-2 exit 1 checker_runs 5 ; attempt-3 exit 0 checker_runs 5
```

**R2-M5. There is no `gnd transition` CLI command:**
```
gnd: error: argument command: invalid choice: 'transition' (choose from witness, replay, ..., check, ...)
gnd check usage: model [population] [--pre PRE] [--steps STEPS] [--post POST] ...
```

**R2-M6. CLI payload compared with API payload for call 00:** `gnd check MODEL POP --format json` exits 2. Its payload differs from `api.check(model_obj, pop_obj)` only in `model` and `population`: the CLI has absolute paths, the API has `None`.

**R2-M7. `_check_dispatch` counter** (patched at its module attribute): 25 on the reporter replay, and 1 per `api.check`. This confirms the r4 target.

**Round-1 numbers reused:** baseline deepcopy nodes are 2,774,153, of which 95.3% come from `ModelIndex.fact_types`. The wall upper bounds were 7.33 → 5.13 → 4.55 → 4.11 s (median of 3). The receipt simulation hit 6 per replay (25 → 19). A profile-hooked replay took about 20 s against about 7 s unhooked.

## 1. Round-1 findings: are they discharged?

| ID | Discharged? | Evidence in r4 |
|---|---|---|
| F1 (TP2 unit and counter) | **yes** | Spec §6: `deepcopy_nodes` and `deepcopy_calls` come from a profile hook on `copy.deepcopy.__code__`. Plan TP2-C4 gates on nodes ≥50%. §2 names `fact_types` with an internal non-copying view. Consistent with the measurements (95.3% from one site), and falsifiable: removing the `transition.py` copies alone moves nodes by less than 3%. |
| F2 (TP3 end to end) | **yes** | The plan predicate 5 and TP3-C2 gate is the workload total 25 → 19, and minting returns the payload. Consistent with the 6 hits per replay and with the pairing of check *i* with transition *i+1* (byte-identical files). |
| F3 (key counter scope) | **partly** | Moving the key elsewhere can no longer hide it. But the counter now counts **every** `Model.model_dump`, including 457 non-key dumps (R2-M1), so the TP1 bound cannot be met. See N1. |
| F4 (marker ≠ index key) | **yes** | Plan Problem bullets, §2 TP1, TP-R2, TP1-C2 and spec T5 all name the operations-only mutation and check the index directly. |
| F5 (branch traces) | **partly** | Traces are captured under `capture_branches()` and digested separately. But the trace is an unordered set (R2-M3), so it cannot see the "internal reorderings" that spec D3 cites, and it cannot see a missing receipt-branch replay. See N2. |
| F6 (runtime mutant) | **partly** | The verdict-flip runtime mutant is a real negative control. The second mutant ("reorders the recorded branches changes the trace digest") cannot change a digest over a set. See N2. |
| F7 (ceiling, residual) | **yes** | Problem §: "at most about 44%", with 7.33 → 5.13 → 4.55 → 4.11 s and 3.6 of 11.3 s profiled. All of it matches my measurements. The figure is properly an upper bound: the TP1 simulation memoized across calls, which is stronger than the per-call scope, and the simulations were unsafe. |
| F8 (5-step / counter / n ≥ 2) | **partly** | 1-step transitions are stated, `checker_runs` at `_check_dispatch` gives 25 (R2-M7), and the course control was added. But the course plan passed "unchanged" is refused with 0 checker runs (R2-M4). See N3. |
| F9 (batch exit) | **yes** | T3 expects exit 2 with 0 failures, which matches the measured batch exit of 2. |
| F10 (surfaces) | **partly** | The surface table now covers CLI, with-post, admission and `compiled_operations`. But `gnd transition` does not exist (R2-M5, N4), and the CLI/API digest equality needs a precise normalization (R2-M6, N5). |
| F11 (timing limits) | **yes** | Interpreters plus the session default, variance, and the profiling-inflation caveat are recorded (spec §6 baseline, D6). See N6 for a residual instrument interaction. |
| F12 (attribution) | **yes** | §10: 65 of 540 come from the loader, which matches R2-M2. |

Totals: 7 yes, 5 partly, 0 no.

## 2. New findings

| ID | Self-inflicted | Class | Severity | Claim | Evidence | Proposed fix |
|---|---|---|---|---|---|---|
| N1 | yes (spec §6 `model_key_paths`, TP1-C1) | blocking | medium | The TP1 gate cannot be met by the approved TP1 design. `model_key_paths` counts every `Model.model_dump` from any caller, but TP1 removes only ModelIndex key dumps. The CR-01 marker digest is deliberately recomputed, and the other consumers are out of scope. | R2-M1: baseline 997 = 540 key + 212 marker + 245 others. The bound "1 per public call + 1 per loaded intermediate and loaded population" is about 13 + 43 + 6 = 62 on the reporter workload. After a perfect TP1 the counter still reads at least 13 + 457 = 470. | Count key-path executions at their source: put the canonical key in one named function, owned by `model_index` and counted at every lookup owner, and gate it on the bound. Keep "all `Model.model_dump`" as a separate **must-not-increase** counter, with a baseline of 457 non-key dumps, so that moving the key path elsewhere still shows up. |
| N2 | yes (spec §6 parity, D3, T6; TP-R3 branch-set binding) | hardening | high | The branch-trace digest checks only the presence of branch ids. T6's "reorder" mutant cannot change a digest over a set, so T6 fails as written. The trace digest also cannot detect a receipt path that forgets to replay the stored branch set, which leaves that TP-R3 binding without a case. | R2-M3: `capture_branches` yields `set[str]`. Skipping the pre-check with no replay gives 26 = 26 branch ids and an identical payload. | Replace the reorder mutant with a **drop-one-branch-id** mutant. Correct D3's rationale to say presence only, not order. For TP3, add a direct test that the receipt's stored branch set equals the set captured during minting and is re-recorded into the active trace. A mutant that skips the re-record must fail it. Do not rely on the union digest for that. |
| N3 | yes (plan predicate 1, §3 Control, TP3-C2; spec §6 Control, T2, T4) | blocking | high | The `course` control as specified ("unchanged", passed to `api.transition` or the CLI) is refused as ill-formed before any check. So the n ≥ 2 liveness in T4 and the TP3 course parity are empty: a refusal compared with a refusal. | R2-M4: exit 3, 0 checker runs, for path and object inputs. With the plan app's own header (`plan_apps/core.py:50,63`), attempt-3 exits 0 with 5 checker runs (n + 2 = 5), and attempts 1 and 2 exit 1 with 5. | Have the tool build the step header exactly as `plan_apps/core.py` does (or call its helper), and state this in spec §6 and in plan predicate 1. Pin `checker_runs == 5` exactly in T4, not "at most n + 2". Use attempt-1 or attempt-2 (exit 1) as the failing-receipt refusal case for D-p1-1. |
| N4 | yes (spec §6 surface table; plan predicate 2) | hardening | medium | The surface "CLI `gnd transition MODEL PRE STEPS`" does not exist. T3 and T7 cannot run it. | R2-M5. | Use `gnd check MODEL --pre PRE --steps STEPS --format json` (and `--post` for the with-post case). Correct plan predicate 2 to match. |
| N5 | yes (spec T3, `NORMALIZED_FIELDS`) | hardening | low | "CLI payload digests equal those of the API surfaces" holds only if normalization maps the CLI's absolute paths to the API's value. "Removes only absolute paths" does not say whether it deletes the keys or substitutes a placeholder. A placeholder would make T3 fail. | R2-M6: the payloads differ only in `model` and `population` (paths compared with `None`). | Define `NORMALIZED_FIELDS = {"model", "population"}`, with both set to `null` on every surface (or deleted on every surface), and state that the CLI/API equality is asserted after that normalization. |
| N6 | yes (spec §6 deepcopy profile hook; `--repeat` timings in the same tool) | hardening | low | The tool both counts, with wrappers and a `sys.setprofile` hook, and times. If the timing repetitions run while instrumented, the medians are inflated about 3× and cannot be compared with the 7.33 s planning baseline or the 44% ceiling. | Round 1: the hook-instrumented replay took about 20 s against about 7 s plain. | State that timing repetitions run in a separate, uninstrumented pass (fresh process), and that counters come from their own pass. |
| N7 | yes (r4 restatements) | completeness | low | The TP1 bound is worded three ways: predicate 3, TP-D6 and §9 say "+1 per loaded intermediate"; TP1-C1 says "+1 per loaded intermediate **and loaded population**". On this workload the two readings give about 19 and about 62. | Plan lines 94–96, 246–248, 381, 397. | Use one wording in one home (TP1-C1), with the TP0 number, and have the other sites cite it. |
| N8 | yes (spec T4) | completeness | low | T4 deep-copies "a known three-level structure from a frame under `src/gnd`", but the test file is not under `src/gnd`, so the case needs a named GND callable. | Spec T4. | Name the callable, for example `gnd.transition.validate_steps_document` (deep-copies the step document; 6 calls and 428 nodes on the replay), and pin its node delta. |

**Counts:** 8 new findings. All 8 are self-inflicted (they attack text r4 created or changed). 2 are blocking (N1, N3), 4 hardening, 2 completeness.

## Answers to the coordinator's specific questions

- **`model_key_paths` bound:** not consistent with the measurements, and not meetable as defined (N1). Its wording is also inconsistent across the plan (N7).
- **`deepcopy_nodes` −50%:** consistent and falsifiable. One site holds 95.3% of the nodes, and the gate cannot be met by trimming the `transition.py` copies.
- **Workload `checker_runs` 25 → 19:** consistent (6 receipt hits per replay, with check and pre-state files byte-identical) and falsifiable. The counter at `_check_dispatch` was verified at 25. The course-side TP3 parity is empty until N3 is fixed.
- **The ~44% ceiling:** accurately stated, as an upper bound from unsafe simulations, single-session medians of 3, with about 20% between-session noise. A real per-call-scope TP1 will land at or below it.

## 3. Verdict

**approve-with-fixes.** Both blocking items, N1 (count the key function, not every dump) and N3 (build the course step header and pin 5 runs), are one-paragraph definitional repairs inside the TP0 spec and the plan's control description. They can be checked at the TP0 owner gate without another round. Eight of 8 findings are self-inflicted (ratio 1.0 > 0.5), so the plan's stop rule applies: fix and stop, with no third round. N2 should be fixed together with N3, because TP3's branch-set binding otherwise ships without a case.
