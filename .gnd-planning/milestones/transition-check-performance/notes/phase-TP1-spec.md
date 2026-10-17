# Phase TP1: Cheap ModelIndex hits under CR-01

## 1. Status

**Owner-approved (o4), 2026-10-16.** The owner replied "approved" to this spec as
written. The approved bytes have SHA-256 `531f801617aa47e8cb706e7d0220cb95cfc80c8bef0ccd340f4aad4338ed56b1`. D1–D5 are accepted as proposed.
The instrument is this prose. The spec is append-only from here.

## 2. Provenance

- Plan r5, owner-approved 2026-10-16 ([plan gate](../001-plan-gate.md)): §2 TP1, §4
  TP1-C1..C4, §9 TP1 row, TP-D1 (a), TP-D6 and D-p1-2.
- [TP0 record](../002-phase-TP0.md) and its baseline (`evidence/TP0/`), which carries the
  exact key-path bound forward to this spec.
- Inspection of `src/gnd/model_index.py`, its 14 `for_model` call sites, `tools/gnd_layers.json`
  and `tests/test_rf6_index.py` at `2d1ff4d` (runtime unchanged through TP0).
- No review has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan TP1-C1 | `model_index_key_paths` at most 1 per public call, plus 1 per loaded intermediate and loaded population; `model_dumps_other` does not increase; TP0's baseline sets the exact numbers | §6 bound, T1 |
| Plan TP1-C2 | A fresh index after three mutation kinds between calls (nested constraint, operation with the marker unchanged, fact type), checked on the index directly; a mutate, re-load, check path; fails on an identity-keyed mutant | T2, T3 |
| Plan TP1-C3 | The cache and scope stay bounded; the key path has a bound test; no scope leaks across threads or calls | T4, T5, T6 |
| Plan TP1-C4 | Parity on every TP0 surface; existing ModelIndex, RF6 and layering tests pass | T7, §8 ledger |
| Plan TP-D1 (a) | One key per public call, reused within the call. The key is ModelIndex's own canonical key, not the marker digest | §6 design |
| Plan TP-R2 | A cache hit never lets a mutated model reuse a stale index | §6 invariant, T2, T3 |
| Plan TP-R5 | One defining home, one invalidation rule, a bounded size, zero layer allowances | §6, T4, T8 |
| Plan §6 risk "stale index after mutation" | Three mutation kinds, plus an identity-keyed mutant | T2, T3 |
| Plan O2, O3, O10 | Request 1, CR-01, layer map | as above |
| TP0 record, carried forward | The exact key-path bound | §6 bound |

## 4. Rules bound to TP1

Standing rules:

1. **Totality:** the scope adds no document consumer. `for_model` keeps its `TypeError`
   for non-`Model` input and its uncacheable-snapshot route for cyclic, non-string-key or
   non-finite content (`test_rf6_index.py` pins both).
2. **Input cap vs algorithm:** the scope's work per hit is a dictionary lookup, with no dump,
   walk or hash. Its size is capped (§6). T4 proves both with counters, which are
   deterministic, instead of a wall-clock bound, consistent with TP-R4. The existing
   `test_large_index_work_is_bounded` time test still covers a cache miss.
3. **Validation order:** the `TypeError` check stays first in `for_model`, before any scope
   lookup. T5 pins this.
4. **One walk:** one scope mechanism serves every caller. The 14 call sites are not edited.
   Only the entry points enter the scope.
5. **One normative home:** the scope's invalidation rule is stated once, in the
   `gnd.model_index` docstring. This spec and the plan cite it.
6. **Measurement over argument:** the bound in §6 is a prediction. T1 measures it, and a
   different number is recorded as a finding, not adjusted silently.

Plan rules:

- **TP-R1:** T7 compares every TP0 surface's payload and trace digests with the committed
  baseline.
- **TP-R2:** §6 invariant; T2 and T3.
- **TP-R3:** does not apply. No receipt is involved.
- **TP-R4:** counters gate (T1, T4). No timing assertion is added.
- **TP-R5:** one home (`gnd.model_index`), one rule, a capped size, zero new allowances (T8).
- **TP-R6:** no downstream names. Approval follows this spec's gate.

## 5. Goal

Running `uv run pytest -q tests/test_transition_cost_workload.py tests/test_tp1_index_scope.py
tests/test_rf6_index.py tests/test_rf1_layering.py tests/test_public_transition_contract.py
tests/test_popvalidate.py` exits 0. The reporter replay then measures:

- `model_index_key_paths` = 26 (baseline 540);
- `model_dumps_other` ≤ 457;
- `checker_runs` = 25;
- every TP0 digest unchanged.

## 6. Design

### `src/gnd/model_index.py` (about 45 added lines)

```python
_SCOPE: ContextVar[dict[int, tuple[Model, ModelIndex]] | None]  # default None
_SCOPE_LIMIT = 8

@contextmanager
def index_scope() -> Iterator[None]:
    """Reuse one ModelIndex per Model object for the duration of one public call.

    Invalidation rule (the one home): a scope lives for exactly one public call; on exit
    every entry is dropped, so the next call recomputes the canonical key and the content-
    keyed cache decides. Inside a scope a Model object is assumed not to change: GND does
    not mutate model content while serving a call. A nested scope joins the outer one.
    """
```

- **`for_model(cls, model)`:** the `TypeError` check stays first. Then, if a scope is active
  and holds `id(model)` with *that same object*, it returns the stored index with no dump.
  Otherwise it computes exactly as today and stores the result in the active scope. Uncacheable
  snapshots (`digest is None`) are stored as well, because the no-mutation-within-a-call
  assumption covers them too. Each entry holds a strong reference to the model, so an `id`
  cannot be reused for another object within the scope.
- **The cap:** `_SCOPE_LIMIT = 8` models per scope. Beyond that, the oldest entry is dropped
  (FIFO). A public call uses one model, or two in `diff`.
- **No public export:** `index_scope` is not added to `gnd.api`, and `api.__all__` is
  unchanged.
- **Outside any scope,** `for_model` behaves exactly as today. All existing `test_rf6_index.py`
  cases call it outside a scope.

### Entry points that open a scope (one `with index_scope():` line each)

| Entry point | Covers |
|---|---|
| `checking_service._run_check` | `api.check`, CLI snapshot check |
| `api._run_transition` | `api.transition`, CLI transition arm (`commands/checking.py` calls it) |
| `batch.check_population_directory` | batch `--populations` |
| `population.load_population` and `load_population_bytes` | loads, including intermediate states inside a transition, which join its scope |
| `checker._core._check_dispatch` | direct internal `checker.check` callers outside the API; joins an outer scope when present |

Each entry point is at or above the `model` layer, so it may import `gnd.model_index` under
`tools/gnd_layers.json`, with zero new allowances.

### The bound (TP1-C1, made exact)

On the reporter replay, each of the 13 population loads happens outside any API call, so
each opens its own scope (1 key path each). Each of the 13 API calls opens one scope
(1 key path each). The intermediate loads inside a transition join that transition's
scope (0). **Predicted `model_index_key_paths` = 26**, within the plan's bound of
13 + 6 + 13 = 32. On the `course` replay (1 load, plus 1 three-step transition), the
prediction is 2. `model_dumps_other` is predicted to stay at 457, because TP1 adds no
dumps.

### Invariant (TP-R2) and its boundary

Between public calls, CR-01 holds as before. Each call starts with no scope, so a key is
recomputed, and the content-keyed cache returns a new index for mutated content. That
includes an operations-only mutation, which the marker digest does not see. Within a single
call, a mutation by the *caller* is impossible, because the caller is not running. A
mutation by GND would be a GND defect, and T7's parity would catch any effect it had on a
result.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | Scope entry points | The five rows above (proposed), or only `api` functions. The narrower set leaves CLI batch and direct `checker.check` callers paying the full cost, and changes no exit code. |
| D2 | Should loads open their own scope? | Yes (proposed): the 13 reporter loads cost 1 key path each instead of 5 (65 → 13). No: a smaller diff, with a bound of 13 + 65 = 78. |
| D3 | Store uncacheable snapshots in the scope? | Yes (proposed). Within one call the same object is assumed unchanged, so the snapshot stays valid. No: cyclic models keep paying a full dump per lookup. |
| D4 | Scope cap | 8 models, FIFO (proposed), or unbounded. Unbounded violates standing rule 2. |
| D5 | Counter bound test instead of a wall-clock test for standing rule 2 | Counters (proposed; TP-R4), or a timing test (flaky, and against TP-R4). |

## 8. Tests

The new file is `tests/test_tp1_index_scope.py`. T1 extends `tests/test_transition_cost_workload.py`.

| # | Case | Expected |
|---|---|---|
| T1 | The reporter replay under `counting()` measures `model_index_key_paths == 26`, `model_dumps_other <= 457` and `checker_runs == 25`. The `course` replay measures 2 key paths and 5 checker runs. | pass (fails on baseline: 540) |
| T2 | Three mutations made between two `api.check` calls, one each: (a) a nested constraint field; (b) an operation field, with the marker still valid; (c) a fact-type role. The second call takes a key path (`model_index_key_paths >= 1`), and the index it uses has a different `digest` from the first. For (b), `matches_validation_marker` is still true, so the check runs and is not refused. | pass |
| T3 | Identity-keyed mutant: a monkeypatched module-level scope that persists across calls makes T2(b) fail. The test runs the mutant and asserts that the T2(b) assertion is violated. | pass |
| T4 | Inside one `index_scope()`, 1,000 `for_model(m)` calls give 1 key path and 0 other dumps. Opening scopes on 9 distinct models keeps 8 entries, the first is evicted, and a lookup of the first model re-dumps it. | pass |
| T5 | `for_model("not a model")` raises `TypeError` inside a scope, as it does outside one. | pass |
| T6 | No leaks. After a scope exits normally, after it exits through an exception, and in a second thread running at the same time, no stored index is visible: `for_model` takes a key path. Nested scopes share entries. | pass |
| T7 | Parity: every reporter and `course` surface's `payload_digest` and `trace_digest` equal the committed `evidence/TP0/digests.json`, and the CLI digests equal theirs. | pass |
| T8 | `tests/test_rf1_layering.py` passes, with the allow-list still empty. | pass |
| — | `tests/test_rf6_index.py` (unchanged) passes, covering the mutated-section, bounded-cache and cyclic-snapshot cases outside a scope. | pass |

**Branch walk:**

- The scope hit has cases in T1 and T4; the scope miss in T4 and T6; eviction in T4.
- Exiting through an exception, and isolation between threads, are in T6.
- The outside-scope path is covered by `test_rf6_index.py`.
- The entry points are covered by T1 (the API and load routes), T7 (the CLI and batch
  surfaces), and T1's `course` row (checker dispatch through a transition).
- The stale-index branch is in T2, and its mutant in T3.

**Verification selection:**

- **Run:** the §5 command, plus the TP0 gate.
- **Inherited:** the TP0 counters and digests, as the baseline.
- **Slow cadence:** the broad suite, run only on owner selection.

## 9. Out of scope for TP1

- Deep copies (TP2) and receipts (TP3).
- Any change to the content-keyed cache's key or its 32-entry limit.
- Freezing model content.
- A public scope API.
- Reducing `model_dumps_other`.

## 10. Size

Estimate: about 45 source lines in `model_index.py`, plus 6 entry-point lines, plus about
170 test lines.

## 11. Approval instrument

This prose. The counters and digests that judge TP1 are already committed by TP0, which
fixes the expected values: 26 key paths, and the baseline digests.

## Implementation findings, recorded as they were found

1. **Red first.** Before implementation, 5 of the 8 non-parity tests failed: T1 measured 540
   key paths, and T3 to T6 had no `index_scope` (`evidence/TP1/red.txt`). T2b, T2a and T2c
   passed on the baseline, as expected, because they pin today's between-call behaviour.
2. **The prediction held exactly:** `model_index_key_paths` is 26 on the reporter replay
   and 2 on `course`. `model_dumps_other` stays at 457, `checker_runs` at 25, and
   `deepcopy_nodes` at 2,760,394. Every TP0 payload, trace and CLI digest is identical
   (T7; `evidence/TP1/digests.json` equals the TP0 file byte for byte).
3. **Entry points use a decorator.** `gnd.model_index.scoped` (`functools.wraps`) adds one
   line per entry point instead of re-indenting the long bodies. 421 + 564 affected-consumer
   tests pass, including the public API, the signature pins, and the RF1, RF2, RF6 and RF7
   identity pins.
4. **Separately launched medians are not comparable.** The TP0 baseline median was 5.09 s
   and the TP1 median 4.99 s, which looks like −2%. An in-process A/B
   (`evidence/TP1/ab_scope.py`) alternating the real scope with a no-op scope gives
   6.93 s without the scope and 4.86 s with it, which is −30%. That matches the planning
   simulation. Machine speed drifts between runs: the same TP0 code measured 5.79 s and
   5.09 s on the same day. Wall-time claims for later phases use the in-process A/B.
5. **An intermittent failure: one cause found, one not established.** One run of the §5
   gate on 3.14 reported `1 failed, 171 passed` (132 s total), and its output was not
   retained. A logged loop of four runs then reproduced a failure in run 1, which took
   379 s because the diff reviewer was running tests at the same time. TP0's T7 tool test
   (77 s unloaded) passed the 120 s hang guard, and the guard's `TimeoutError` was raised
   inside GND rule evaluation, which reported "rule is defective". Runs 2–4 passed. Fix:
   the TP0 D5 hang guard is amended from 120 s to 600 s. It is still a hang guard, never a
   performance gate. The first failure's 132 s total makes a single 120 s timeout unlikely,
   so its cause is **not established**.
6. **An observation outside TP1's scope.** An exception delivered by a signal during
   semantic-rule evaluation is reported as a defective rule
   (`ModelValidationError ... raised TimeoutError ... the rule is defective`). That
   mapping predates this milestone. It is recorded as an open question for the
   framework maintainer.
7. **The diff review (one reader) found nothing blocking.** Its main evidence: an oracle
   re-dumped the live model on every in-scope hit across 786 tests (22,029 hits) and found
   0 stale hits on real code paths. The only finding, F1 (hardening, low), was that the
   decorators covered each other in pairs, so removing any single one left every test
   green. The branch walk's claim that "T7 covers the entry points" was overstated, because
   T7 checks parity, not scope. Fix: `test_review_f1_each_entry_point_opens_its_own_scope`
   counts exactly 1 key path per route, and `evidence/TP1/review-mutants.txt` shows each
   decorator's removal failing its route. F2 (completeness): D3 had no case. Fix:
   `test_review_f2_uncacheable_snapshot_is_reused_within_a_scope`, killed by its mutant.
8. **The `load_population` decorator was dropped, a deviation from the §6 entry-point
   table.** `load_population` only reads the file and calls `load_population_bytes`, whose
   scope already covers it, so its decorator was unobservable. The route keeps its
   behaviour test (1 key path). The `api.check` route test uses path inputs, because with
   loaded inputs `_check_dispatch` alone covers `api.check`.
9. **Boundary (review F4).** The "the caller is not running" argument in §6 assumes the
   caller does not mutate a model from *another* thread while a call is in progress.
   Concurrent mutation of a shared model was not supported before TP1 either. Nothing
   locks model content.
