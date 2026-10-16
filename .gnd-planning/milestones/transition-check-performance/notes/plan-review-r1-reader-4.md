# Plan review: reader 4 of 4

- **Lens:** measurement and test design. Are the gates falsifiable, and do they measure what the milestone promises?
- **Subject bytes (working tree on `claude/transition-check-performance-plan-r3`, HEAD `2d1ff4d`):**
  - `e691348d8f2cfa6656c8eb8ca305fc91605a87ce3ae5b332d531942e086392ab`  `.gnd-planning/milestones/transition-check-performance/notes/transition-check-performance-plan.md` (draft r3)
  - `f0073202b77a6b75a8aaaae59db6a1eba858a7afc2beeee6189647c5e068dd7b`  `.gnd-planning/milestones/transition-check-performance/notes/phase-TP0-spec.md`
- **Environment:** Apple M5 Max, CPython 3.14.3 (the interpreter `uv run` picks by default here), current bytes `2d1ff4d`. No repository file was edited. All scripts and outputs are in `scratchpad/exp/`.
- **Workload:** the anonymized scratch bundle (13 calls), replayed as: load the model once, then for each call `load_population(..., model=model)` followed by `api.transition(model, pop, steps)` or `api.check(model, pop)`.

## Measurements

### M1. Unprofiled wall time (`exp/replay.py time`, `exp/counters.py base`)

```
replay.py time      total 8.792 s  (checks 0.29–0.32 s each, transitions 1.02–1.06 s each)
counters.py base    runs [7.09, 7.34, 7.33] s  (same machine, a few minutes later)
```
Across sessions on one machine the 13-call total moved between 7.1 and 8.8 s. The planning observation records 6.4 and 7.2 s, and the reporter's figure is 3.96 s. So the spread between sessions is about 20% before any code change.

### M2. cProfile of the replay (`exp/replay.py profile`, current bytes)

```
profiled total 23.466 s   (2.7–3.2x the unprofiled time)
_core.py:2052(check)                  ncalls=25        cum=15.309
model_index.py:52(for_model)          ncalls=540       tottime=3.730 cum=7.776
copy.py:110(deepcopy)                 prim=1291 ncalls=2774153  cum=2.106
correspondence.py:1118(correspond_snapshot)   25       cum=9.172
semantic_adapter.py:796(adapt_snapshot_observed) 25   cum=8.994
extension_preparation.py:104(calculate)       81       cum=4.550
population.py:498(load_population_bytes)      43       cum=3.717   (13 explicit + 30 internal)
artifacts.py:173(canonical_json_bytes)        589      cum=0.712
values.py:179(_model_digest)                  212      cum=0.291
```
On current bytes the issue's shape reproduces almost exactly: 25 checker runs, 540 `for_model` calls (the issue reports 535), and 2.77 M deepcopy invocations. All of these happen on the GND side, which answers the plan's open question at §10.

### M3. The workload consists only of single-step transitions, and check *i* is transition *i+1*'s pre-state

```
01..11-transition-steps.json: 1 step each (execute_scan, execute_traverse, execute_filter,
                              execute_aggregate, execute_answer, finish_walk)
shasum: 00-check == 01-transition, 02 == 03, 04 == 05, 06 == 07, 08 == 09, 10 == 11 (byte-identical)
course control plans/attempt-3.steps.json: 3 steps
```
25 = 7 checks + 6 × (1 + 2) checks. No transition in the fixture has n > 1.

### M4. The spec's D1 counter method compared with ground truth (`exp/counters.py spec_counters`)

```
mock.patch.object(gnd.checker._core, 'check', counter)  -> patched_core_check = 0
sys.setprofile on core.check.__code__                     -> true_core_check   = 25
transition.check is core.check original: True ; gnd.checker.check is original: True
for_model = 540, canonical_json_bytes (all callers) = 589, population._model_digest = 180
```

### M5. Deepcopy as the spec counts it compared with ground truth (`exp/counters.py deepcopy`, `exp/dc_truth.py`)

```
spec method (patch copy.deepcopy, caller under src/gnd): 90 calls, all from transition.py
ground truth (code-object profile):  top-level 1291, recursive nodes 2,774,153
   top   nodes      site
   300   2,645,100  model_index.py:fact_types        (95.3% of nodes)
   900      42,075  model_index.py:iter_constraints  (69.7% of top-level calls)
    18      36,156  transition.py:_effective_extension_state
     6      14,625  transition.py:_restore_asserted_state
     1      13,759  model_index.py:__post_init__
     6      11,724  transition.py:evaluate_plan
  27+27     10,286  transition.py:_unavailable/_unknown_precondition_verdicts
     6         428  transition.py:validate_steps_document
```
`model_index.py` does `from copy import deepcopy`, and `copy.py` binds its recursive helper through a default argument. So patching `copy.deepcopy` cannot see either `model_index` site, and it cannot see any recursive node.

### M6. Upper bounds on TP1–TP3, simulated by monkeypatching (unprofiled, 3 runs each, `exp/counters.py`)

| Mode | Simulation (unsafe, used only as an upper bound) | Runs (s) | Median | vs base |
|---|---|---|---|---|
| base | none | 7.09 7.34 7.33 | 7.33 | 0 |
| tp1 | `for_model` memoized on `id(model)` | 5.23 5.04 5.13 | 5.13 | −30% |
| tp1tp3 | + the first check in each `api.transition` reuses the preceding `api.check` report (6 hits per run, verified) | 4.47 4.44 4.53 | 4.47 | −39% |
| tp12 | tp1 + every `model_index` deepcopy replaced by identity | 4.51 4.55 4.61 | 4.55 | −38% |
| tp123 | all three | 4.05 4.14 4.11 | 4.11 | −44% |

The 13 report digests (sha256 of sorted-key JSON) were identical in all five modes and across separate processes.

Residual after tp123 (one profiled run, 11.3 s profiled): 19 checker runs with 5.8 s cumulative. Inside that, `extension_preparation.calculate` takes 3.6 s (`freeze` 1.6 s), `correspond_snapshot` 2.9 s and `load_population_bytes` 0.55 s. `for_model` falls to 0.014 s and deepcopy to 0.044 s.

### M7. Cost breakdown of one `for_model` hit (`exp/formodel.py`, unprofiled, mean of 20)

```
for_model (hit) 4.04 ms = model_dump 0.47 + container walk 1.52 + canonical_json+sha256 1.13 (+ overhead)
values.model_digest 1.48 ms ; ModelIndex.fact_types (deepcopy) 1.23 ms
540 x 4.04 ms = 2.18 s  (matches the 2.2 s tp1 saving in M6)
```

### M8. CR-01 marker compared with ModelIndex key, per mutated field (`exp/cr01.py`)

```
constraints[0].modality mutated -> marker valid: False | new index: True | api.check exit 70 UnvalidatedPopulationError
operations[0].reading mutated   -> marker valid: True  | new index: True | api.check exit 2
```
`values._model_digest` excludes `operations` (`MODEL_DIGEST_EXCLUDED_FIELDS`) and hashes `repr`. The `ModelIndex` key includes `operations` and hashes canonical JSON. They are two different digests.

### M9. Batch surface (`gnd check steps.orm.json --populations DIR --format json`, DIR = 00 + 02 check populations)

```
exit=2
```
Default `api.check`/`api.transition` payloads contain no `branch`/`trace` keys, no absolute paths and no timing fields (`exp/keys.py`). Branch traces exist only inside `capture_branches()` contexts in `api.py`/`checking_service.py`.

## Answers to the four questions

1. **Do the targets match the dominant costs, and what fraction would TP1–TP3 remove?** At the upper bound, TP1 removes about 30% of wall time, TP2 about 8% more (all of it in `model_index` query copies) and TP3 about 6–9% more. Together that is about 44%, from 7.3 s to 4.1 s. Read against the issue's numbers, the profile's 5.8 s (9.2 s profiled here) in `correspond_snapshot`/`adapt_snapshot_observed` is mostly inclusive time from `for_model` and deepcopy. It falls to 2.9 s profiled once those are gone. Extension preparation and correspondence are still the largest remaining block, and the milestone defers them (TP4). The plan never projects a wall-time outcome or names that residual (F7). The TP2 and TP1 counters as specified do not measure the dominant work (F1, F3). TP3's gate can pass with no end-to-end saving (F2).
2. **Is the parity oracle sufficient?** It is not sufficient for the claims made. The "branch traces kept" promise is empty on default payloads (F5). T6's negative control perturbs the payload, not the runtime (F6). Workload parity cannot see CR-01 regressions at all: M6's identity-keyed memo produced identical digests. So the burden falls on T5/TP1-C2, and those tests lack the discriminating `operations` mutation (F4).
3. **Is every TP0 test falsifiable on the baseline, and does each criterion map to a test?** No. T4 as specified fails on baseline (M4: checker_runs = 0) and names a 5-step transition that does not exist (F8). T3 expects exit 0, but the baseline exits 2 (F9). The CLI single-run surfaces and the conditional admission surface have no test (F10).
4. **Is "wall time informs, counters gate" applied consistently?** Mostly. Timing never gates. But the spec gives no limits: no spread, no cross-session noise, and no profiler inflation. Its interpreter set also leaves out the default dev interpreter (F11). TP0-C4's "far below → reopen D2" would fire spuriously with the spec's deepcopy counter (90 compared with 2.7 M; see F1).

## Findings

| ID | Class | Severity | Claim | Evidence | Proposed fix |
|---|---|---|---|---|---|
| F1 | blocking | high | The TP2 gate (`≥50% fewer deep copies`) has no defined unit. The spec's counter cannot see the dominant site, so the gate can be met by the wrong work and missed by the right work. | M5: 95.3% of deepcopy nodes come from `model_index.fact_types` (300 top-level calls). The spec's `copy.deepcopy` patch sees 90 calls, none of them from `model_index` (`from copy import deepcopy`; recursion is bound through a default argument). Removing the 54 precondition copies in `transition.py` passes "≥50%" on the spec counter (60% of 90) and saves about 10k of 2.77 M nodes. Removing `fact_types` copies shows 0% on that counter. Separately, `fact_types` sits under O5's detached-value contract, so it may be unremovable under TP2-C3 unless internal callers get a non-copying internal accessor. | Define two counters through a code-object profile hook (`sys.setprofile` on `copy.deepcopy.__code__`, as in `dc_truth.py`): top-level calls per GND site, and recursive nodes. Gate TP2 on **nodes**, with the baseline numbers in the spec (2,774,153 / 1,291). TP2-C1 must rule explicitly on `fact_types`/`iter_constraints`, for example as internal non-copying views that keep the public detached query. |
| F2 | hardening | high | TP3's gate counts checker runs *inside the transition*. With TP-D5(i) (a separate mint API), a caller who also wants the check report can pay one extra check to mint and save one in the transition, a net of 0. The gate passes with no end-to-end benefit. | M3: in this workload every check *i* is byte-identical to transition *i+1*'s pre-state, so the 13-call replay is the natural receipt test. M6: correct reuse saves 6 of 25 runs (0.66 s after TP1). | Add a receipt-variant replay to the TP0 tool, where the mint API replaces call *i*'s check and returns the same report plus the receipt. Gate TP3 on **workload-total** `checker_runs`: 25 → 19 on the fixture, with reports byte-identical. Require the mint API to return the report that `api.check` returns, or to cost 0 extra runs. |
| F3 | hardening | high | The `model_index_keys` counter (`canonical_json_bytes` calls made from inside `for_model`) measures about 28% of the cost TP1 targets. A threaded key computed elsewhere drives it to 0 trivially. | M7: a hit costs 4.04 ms, of which hashing is 1.13 ms. `model_dump` (0.47 ms) and the container walk (1.52 ms) happen before hashing. A TP1 that caches only the hash, or moves it into another helper, satisfies "≤1 key computation" while leaving most of the 2.18 s in place. | Count key-path executions: Model `model_dump` calls plus the container walk (or `for_model` cache-miss and key-path entries), wherever the key is computed, plus every model-digest helper (`values._model_digest`, `reference_model_digest`). State the TP-D6 bound as a number on the fixture (13 public calls + 6 intermediates = 19, and say whether the 30 internal `load_population_bytes` calls count; M2). |
| F4 | hardening | high | The plan's TP1 premise conflates two digests. The CR-01 tests (T5, TP1-C2) mutate "a model dict" without naming the discriminating field, so a TP1 that threads the marker digest as the index key would reuse a stale index and pass. | M8: `values._model_digest` excludes `operations` and hashes `repr`, while the `ModelIndex` key includes `operations` and hashes canonical JSON. Mutating `operations` leaves the marker valid but must yield a new index. M6: workload parity produced identical digests under an unsafe identity-keyed memo, so parity cannot catch this. | T5 and TP1-C2: parametrize the mutation over at least `constraints` (marker invalid → exit 70) and `operations` (marker valid, new index required, transition result reflects the mutation), plus `reference_populations` if any fixture has them. Correct the §2 TP1 sentence so it no longer implies the marker digest is the index key. |
| F5 | hardening | medium | "Branch traces are kept in the digest" (spec §6, plan risk row) is empty on the oracle as designed. Default payloads contain no branch traces. | M9: no `branch`/`trace` keys in `api.check`/`api.transition` payloads. Traces exist only under `capture_branches()`. | Have the tool wrap each call in `gnd.semantic_registry.capture_branches()` and digest the captured trace alongside the payload. Also digest `unredacted=True` payloads, and note `issues_truncated`, so redaction or truncation cannot hide a change. |
| F6 | hardening | medium | T6's negative control perturbs the *payload*. That proves only that SHA-256 is sensitive, not that the oracle captures semantics. Per standing rules, a control that cannot fail on a semantic regression is not a case. | Spec §8 T6 wording. | Add a runtime mutant: monkeypatch one derivation or verdict path (for example, drop one derived row, or flip one constraint's modality in a copy of the model) and assert that the normalized digest changes for the affected call. Also assert `NORMALIZED_FIELDS` is non-empty only where a payload has such fields (M9: api payloads have none). |
| F7 | completeness | medium | The plan does not project the wall-time outcome or say that the deferred extension re-derivation becomes the largest remaining cost. Readers may expect a "much lower" wall time. The plan's reading of the profile's 5.8 s as an independent cost also overstates it, because that figure mostly includes `for_model` and deepcopy time. | M6: upper bound −44% (7.3 → 4.1 s). Residual is led by `extension_preparation.calculate` (3.6 s of 11.3 s profiled) and `correspond_snapshot` (2.9 s). `correspond_snapshot` drops from 9.2 to 2.9 s profiled under simulated TP1+TP2. | Add one sentence to §Proposed outcome and the TP0 baseline note: expected wall reduction is at most about 40–45% on this workload, and extension preparation/correspondence remain the dominant residual, deferred to TP4. Also record `extension_views`/`correspondences` as "must not increase" regression counters across TP1–TP3. |
| F8 | hardening | medium | T4 names "the 5-step transition", but the fixture has none: all 6 transitions have one step. The specified `checker_runs` patch reads 0 of 25 on baseline, so T4 would fail. More broadly, n + 2 and "intermediate checks stay mandatory" (TP3-C2) are never discriminated, because n = 1 everywhere. | M3, M4. Standing rules call this "a rule made unfalsifiable by how the fixtures were built". | Count `checker_runs` with a code-object hook or by patching every lookup owner (`gnd.transition.check`, `gnd.checker.check`, `checker_module.check`). Pin 25 on the fixture. Use the course control (3 steps, so 5 checks) for n ≥ 2 liveness and for TP3's "only pre skipped" case. Fix the "5-step" wording: the 5-step program runs as 6 single-step transitions. |
| F9 | hardening | medium | T3 expects batch check to exit 0. The baseline exits 2. | M9 (`exit=2`), and the planning observation that all 13 calls exit 2. | Pin the measured batch exit code and per-row counts instead of 0. |
| F10 | completeness | medium | Closing predicate 2 lists CLI `check`/`transition` single runs and `api.transition` with `post`, and O12 names admission. TP0 has no test asserting these surfaces run, and admission is conditional ("when the fixture supports admission"), so it can drop silently. | Spec §6 surfaces and §8 T1–T8. | Add a T-row that runs every surface named in predicate 2 (state where the `post` comes from: the next check population) and asserts its pinned exit. Make admission's inclusion or exclusion an explicit, recorded decision. |
| F11 | completeness | low | Timing "limits" are not defined, and the interpreter set (3.11, 3.13) leaves out the default dev interpreter (3.14.3 here). | M1: between-session spread of about 20% (7.1–8.8 s). M2: profiler inflation of 2.7–3.2x. | Record min/median/max, number of sessions, interpreter and machine. State that cross-session noise is about 20%, so no wall-time claim smaller than that is reportable. Never compare profiled with unprofiled figures. |
| F12 | completeness | low | The plan's open question (whether 535 includes caller-side calls) can be answered by measurement now. | M2: 540 on the GND side alone, with 25 checker runs. | Close the question in §10 by citing the TP0 measurement. |

Confirmations (no finding): the workload reproduces the profiled shape (M2), so TP0-C4's shape comparison will pass *if* the counters are fixed per F1/F8. Normalized digests were deterministic across five processes (M6). Under simulated TP1–TP3, report digests were unchanged (M6), which is consistent with TP-R1 being achievable.

## Verdict

**revise.** The fixes are targeted. F1 (the TP2 unit and counter) must be fixed before TP-D6's targets mean anything. F2 to F4 make the TP3 and TP1 gates and the CR-01 test measure what they claim. F5 to F10 are small edits to the TP0 spec. Nothing in the milestone's direction needs to change.
