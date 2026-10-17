# TP1 independent diff review (transition-check-performance)

- Reviewer: single independent diff reviewer (one reviewer = one reviewer)
- Date: 2026-10-16. Worktree: `.claude/worktrees/github-issue-24-milestone-55853e`, branch `claude/transition-check-performance-tp1`, HEAD `369f161` plus the uncommitted phase diff
- Subject bytes:
  - `src/gnd/model_index.py`: SHA-256 `a395ded629911dd1d95cec7b6b50ed2ec8b9f80014441e7be6957f7a3b9182c9`
  - `tests/test_tp1_index_scope.py`: SHA-256 `df4cab3b08a2378a445171ede57558d919aee9758d7d678b647a88d1b357b823`
- Contract: `notes/phase-TP1-spec.md` §6 to §8; plan TP-R2 (CR-01) and TP-D1
- No repository file was edited. All scripts and outputs are in this scratch directory.

## What was reproduced

| Check | Command (from the worktree root; `S` is this scratch dir) | Outcome |
|---|---|---|
| TP1 tests unmutated | `uv run pytest -q -p no:cacheprovider tests/test_tp1_index_scope.py` | 9 passed (78 s) |
| Neighbouring pins | `uv run pytest -q tests/test_rf1_layering.py tests/test_rf6_index.py tests/test_transition_report.py tests/test_rf1_helper_pins.py tests/test_rf6_moves.py tests/test_rf3_moves.py tests/test_rf6_query_policy.py tests/test_transition_cost_workload.py` | 203 passed, 2 failed. The 2 failures (`test_rf6_query_policy::test_dynamic_candidate_inventory_is_complete_and_live`, `test_dynamic_duplicate_inventory_row_is_refused`) also fail on a clean `git archive HEAD` copy (`$S/head`), with byte-identical assertion output (`$S/rf6_head.txt` = `$S/rf6_work.txt`). They predate TP1 and are not caused by this diff. |
| Stale-hit oracle (CR-01 premise "GND does not mutate model content while serving a call") | `PYTHONPATH=$S STALE_OUT=$S/stale1.json uv run pytest -p stalecheck_plugin ...` over 18 files (public API, the transition contract, mutations, walks, trace, IR immutability, transition report and corpus, v61 batch and API, plan apps, reference corpus, review-by-reference, v71 reference integrity, v70 transition, checker families, population load, TP1). On every in-scope hit, the plugin re-dumps the live model and compares it with the stored index document. | 22,029 in-scope hits. 13 were stale, and all 13 are inside `test_t3_identity_keyed_mutant_is_caught`, the deliberate mutant. **0 stale hits on any real code path** (786 passed; T1/T4 fail only because the oracle adds its own dumps to the counters). |
| Counters | `uv run python $S/ab_timing.py <root>` | `model_index_key_paths` 540 (scope off) to 26 (scope on). Reproduced. |
| Wall-clock A/B, reporter replay, median of 3, two alternations | same | on 2.92 s / 2.94 s; off 4.04 s / 4.21 s. Ratio about 0.71, matching the claimed 6.93 s to 4.86 s (0.70). Absolute numbers differ by machine load (load average 3.5 to 9). The claim is honest. |
| Batch scope effect | `uv run python $S/batch_probe.py <root>` | `check_population_directory` over the 7 reporter check populations: 1 key path with the decorator, 14 without it. |

## Mutants

Each mutant is applied in-process by `$S/mutant_plugin.py` (a monkeypatch; no source edit). Command:
`MUTANT=<m> PYTHONPATH=$S uv run pytest -q -p mutant_plugin -p no:cacheprovider tests/test_tp1_index_scope.py`
The full log is in `$S/mutants.log`. The `unwrap:` mutants replace every `gnd.*` binding of the decorated function with its `__wrapped__`.

| Mutant | Tests that caught it | Result |
|---|---|---|
| `never_reset`: the scope is never reset, so it outlives the call | T1, T2b, T2a, T2c, T4, T6 | killed |
| `no_finally`: no reset on the exception exit | T6 | killed |
| `no_join`: a nested scope replaces the outer one | T1, T3, T6 | killed |
| `lifo`: evicts the newest older entry instead of the oldest | T4 | killed |
| `no_cap`: no eviction | T4 | killed |
| `global_not_contextvar`: a module-global scope shared across threads | T6 | killed |
| `no_identity_check`: drops `entry[0] is model` | none | survived. **Equivalent**: each entry holds a strong reference to its model, so an `id` cannot be reused while the entry exists. The check is defensive only. |
| `no_store_uncacheable`: does not store `digest is None` snapshots (D3) | none | survived. D3 has no test. |
| `unwrap:_run_check` | none | survived |
| `unwrap:_run_transition` | T1 | killed |
| `unwrap:check_population_directory` | none | survived (the effect is real: 1 vs 14 key paths, from `batch_probe.py`) |
| `unwrap:load_population` | none | survived |
| `unwrap:load_population_bytes` | none | survived |
| `unwrap:_check_dispatch` | none | survived |
| `unwrap:load_population,load_population_bytes` (pair; counted by `$S/count_probe.py`) | reporter 78 key paths, not 26 | T1 would fail |
| `unwrap:_run_check,_check_dispatch` (pair; counted) | reporter 110 key paths, not 26 | T1 would fail |

How to read the `unwrap` rows: the entry-point decorators cover each other in pairs on the measured workloads. `load_population` reaches the scoped `load_population_bytes`, and every `api.check` index lookup on these routes happens under a load scope or `_check_dispatch`. Removing any single one of five decorators changes no TP1 test, and leaves the reporter count unchanged at 26. A single load measures 1 key path with or without its own decorator. With no scopes at all, it measures 5.

## Hunt results (questions 1 to 3)

1. **CR-01 and stale index.** No scoped entry point returns a generator or lazy object that still holds the scope dict. The scope dict is reachable only through `_SCOPE`, which is reset in `finally`. Lazy `ModelIndex` iterators work on detached copies. No scoped function runs caller code. The one callable parameter, `_run_check(evaluator=...)`, receives only GND checkers (`diff.py:238`, `commands/checking.py:194`). Recursion between entry points only ever joins a scope. The private `model._references` writes (`api.py:173/279/574`, `checking_service.py:219`) are private attributes. They are not in `model_dump` and do not affect the index. The premise held empirically, with 0 stale hits in 22,016 non-mutant hits. I could not construct a failing case in single-threaded use. The one boundary: the spec's "the caller is not running" assumes one thread. Another thread can mutate a shared `Model` during a call. That race predates TP1, which arguably makes the call more consistent (one snapshot per call), so it is wording only (F4).
2. **`id` reuse and eviction.** Strong references are kept. Eviction builds a fresh `next(iter(scope))` on each loop pass and deletes outside iteration, so it is safe. Order is FIFO by insertion. A re-store on the same key cannot happen while the entry exists.
3. **`functools.wraps`.** The identity aliases hold. `checking_service.run_check`, `api._run_check` and the `__module__ = 'gnd.api'` reassignment all name the same wrapper object. `inspect.signature` follows `__wrapped__` (the `test_transition_report` signature pin passes). Pickling by qualname resolves to the wrapper, and the layering test passes with zero allowances. The population validation marker is unaffected: the decorator wraps the call and does not touch the marker. Threads get a fresh `None` context. GND opens no threads or executors inside a scope. `asyncio` tasks would copy the context and share the dict on one thread, which is harmless, and no scoped path creates any.

## Findings

| ID | Class | Severity | Finding | Evidence | Suggested disposition |
|---|---|---|---|---|---|
| F1 | hardening | low | Five of the six entry-point decorators (`_run_check`, `check_population_directory`, `load_population`, `load_population_bytes`, `_check_dispatch`) can each be removed with every TP1 test still green. The spec's branch walk claims "the entry points are covered by T1 (the API and load routes), T7 (the CLI and batch surfaces)". T7 checks output parity only, not scope presence, and T1 only catches pairwise removals. The batch scope's effect (1 vs 14 key paths) is real and has no test. There is no correctness risk: removing a decorator only reverts performance. | the `unwrap` mutants above; `batch_probe.py` | This phase's own deliverable is the thing it hardens, so fix in-phase if cheap. Add counter asserts per route: batch 7 populations → 1 key path; a single `load_population` → 1; `api.check` → 1; a direct `checker.check` → 1. Alternatively, restate the branch-walk sentence. |
| F2 | completeness | low | D3 (store uncacheable snapshots in the scope) has no test. The `no_store_uncacheable` mutant survives. | mutants.log | Defer, or add one cyclic-model case under `index_scope()` asserting 1 key path over repeated lookups. |
| F3 | completeness | info | The `entry[0] is model` check is unreachable as a distinguishing branch. It is an equivalent mutant, because of the strong references. | `no_identity_check` survived | Keep as defence in depth, and optionally say so in a comment. No action needed. |
| F4 | completeness | info | Spec §6 says "a mutation by the caller is impossible, because the caller is not running". That is a single-thread argument. Concurrent mutation from another thread is a pre-existing race that TP1 neither creates nor worsens. | analysis | Optionally add the words "in the calling thread". |
| — | pre-existing (not TP1) | — | The 2 `test_rf6_query_policy` dynamic-inventory failures reproduce on clean HEAD with identical output. | `$S/rf6_head.txt`, `$S/rf6_work.txt` | Track outside TP1. |

No blocking finding survived.

## Verdict

**Approve with hardening (F1 low).** No blocking finding survived reproduction. The CR-01 invariant holds across calls: the never-reset, no-finally and no-join mutants are all killed. Within a call, it held empirically (0 stale in-scope hits across 786 tests). The counter reduction (540 → 26) and the about 30% wall-clock reduction reproduce. The only real gap is test sensitivity to individual entry-point decorators, plus the untested batch scope (F1). That gap carries no correctness risk.
