# Plan review: reader 1

- **Lens:** semantic correctness and the CR-01 mutation-invalidation guarantee
- **Artifacts read (working-tree bytes, 2026-10-16):**
  - `transition-check-performance-plan.md` (draft r3): `e691348d8f2cfa6656c8eb8ca305fc91605a87ce3ae5b332d531942e086392ab`
  - `phase-TP0-spec.md`: `f0073202b77a6b75a8aaaae59db6a1eba858a7afc2beeee6189647c5e068dd7b`
- **Source baseline:** worktree HEAD `2d1ff4d`. Hotspot files match `73ea302` for the sites cited here.
- **Reproduction:** probe scripts are in this scratch directory (`r1_probe*.py`). They ran
  `api.transition` on the 14 packaged `plan_apps` walks (access, clinic, course, lease, trip),
  in plan mode and declared-post mode. No repository file was edited.

## Answers to the four questions

**Q1. Does TP1 ("one key per public call, threaded through") preserve CR-01?**
Between calls, yes, provided each public call computes a fresh key. Within one call, the
model does not change today. On the course walk, the canonical model dump was identical
before and after `api.transition`. The only write during the call is
`model._references = ...` (`api.py:278`), a private attribute that neither digest sees.
That attribute is itself content-bound through the declared sha256 values
(`model/__init__.py:577-606`).

The plan's supporting claim is half right:
- `matches_validation_marker` does compute `_model_digest(model)` when a check starts
  (`checker/_core.py:344` → `population.py:190`).
- It is **not** the ModelIndex key:
  - ModelIndex key: sha256 of `canonical_json_bytes(model_dump(exclude={'warnings'}))`
    (`model_index.py:56,74`). It includes `operations` and `reference_populations`, sorts
    keys, and can fail, which sends the model down the `digest=None` path
    (`model_index.py:75-76`).
  - `_model_digest`: sha256 of `repr(model_dump(exclude=warnings, operations, reference_populations))`
    (`values.py:176-191`). It ignores `operations`, depends on insertion order, and never
    raises. For reference-bearing models it switches to `reference_model_digest`, a
    canonical-JSON digest that *does* include operations (`values.py:186-187, 201-213`).
- Reproduced: mutating `model.operations[0]` changes the index key but leaves
  `_model_digest` unchanged.

So the marker digest cannot simply be "reused" as the index key. Doing so would change
the cache contract (the totality and `digest=None` behaviour pinned by
`tests/test_rf6_index.py:124,209-213`) and would make the index blind to operations. The
plan sentence at plan:164-166 invites exactly that conflation.

**Q2. Is "n steps cost n + 2 full checks" correct?**
It is correct as an upper bound, reached when every intermediate loads:
- pre: `transition.py:1922`
- one check per loaded intermediate: `transition.py:2015-2019`
- post: `transition.py:2045` for `evaluate`, `transition.py:2110` for `evaluate_plan`

Measured on course attempt-3 (n=3): 5 `transition.check` calls in both modes. An
unloadable intermediate (`2016-2017`) or an unloadable computed post (`2093-2096`, plan
mode only) lowers the count.

Arithmetic consequence: the issue's 25 runs over 7 checks + 6 transitions implies Σnᵢ = 6.
That is consistent with single-step transitions, so each transition costs 3 checks.

**Q3. Can skipping only the pre-state check change the report?**
Simulated by substituting a pre-computed `checker.check(model, pre)` for the call at
`transition.py:1922`. Result: byte-identical payloads on all 28 runs (14 walks × 2 modes),
and the branch trace was unchanged on all of them. The M3 `calculation_scope` replays
branches on a hit (`extension_preparation.py:133-138`), so moving the pre-state extension
work from the check to `structured_extension_view(model, pre)` (`transition.py:1928`) does
not change the trace.

The equality is partly incidental, though. Two inputs that the report depends on must be
carried explicitly:
1. **The full internal `CheckReport`**, including excluded fields (`snapshot_projection`,
   `assurance_input_scope_ids`, `phase1_*`). Assurance minting reads them
   (`assurance/core.py:419-455`).
2. **The pre-check's branch set.** The trace feeds `expected <= set(trace)`
   (`assurance/core.py:455`) and the execution identity hash (`"trace": sorted(trace)`,
   `assurance/core.py:478`). Today the intermediates happen to re-record every pre-check
   branch. A walk whose pre-state alone reaches a branch would change the result.

`pre_snapshot_verdicts` (`transition.py:1923`) is computed separately and must not be
skipped.

**Q4. Semantic risks the plan misses.** See the findings below: the `operations` aliasing
under TP2, the meaning of "failing" given an all-exit-2 workload, path inputs, and the cost
of the separate mint API.

## Findings

| ID | Class | Severity | Claim | Evidence (file:line) | Proposed fix |
|---|---|---|---|---|---|
| R1-01 | hardening | high | TP-D5(ii) says a receipt from a "failing pre-check" cannot be reused, but "failing" is undefined. Every call in the TP0 oracle exits 2 (vacuous) (TP0 spec:21-23, T2). If "failing" means a nonzero band, no receipt is reusable on the oracle workload. TP3-C2's byte-identity gate "on every TP0 transition case" would then be vacuously true, and TP-D6's "−1 checker run" could never be shown on the reporter's workload. | plan:268, 376-377; TP0 spec:21-23, 169; `checker` band mapping in `assurance/core.py:437-439` (0 clean, 1 fail, 2 vacuous, 4 unchecked) | Define "failing" by band in the plan (proposed: bands 1 and 4 refuse, bands 0 and 2 are reusable). Or require TP3 to name a workload where receipts are actually exercised. |
| R1-02 | hardening | medium | TP1 says the marker "already computes `_model_digest`" and that "reusing a single per-call key" removes the other recomputations. These are two different digests. If an implementer re-keys ModelIndex on `_model_digest` to share work: the index stops seeing `operations` (it currently holds them in `_document`), the RF6-pinned `digest=None` behaviour for non-JSON models changes, and `ModelIndex.digest` values shift. If the two stay separate, the bound becomes "≤1 canonical key + the marker digest per check". The plan doesn't say which. | plan:162-166; `model_index.py:56,74-76`; `values.py:176-191`; `population.py:190`; `tests/test_rf6_index.py:124,209-213`; probe: operations mutation changes the key, not `_model_digest` | State that the per-call ModelIndex key keeps the canonical-JSON contract and is computed separately from the marker digest. Or, if sharing is wanted, make it a TP-D1 sub-ruling that covers the operations exclusion and the totality change. |
| R1-03 | hardening | medium | TP2 interacts with CR-01 through `operations`. `_operations_by_id` returns live `model.operations` dicts (`transition.py:290`). Only the deepcopy at `transition.py:1499` (and `1567`) stops the write at `transition.py:1951` from mutating the caller's model. If TP2 removes that copy, the call mutates `model.operations`. That moves `operations_digest`, so the next transition with the same steps document is refused with exit 3. The CR-01 marker cannot detect it because `_model_digest` excludes operations by design. | `transition.py:290, 1499, 1567, 1951`; `values.py:176`; `population.py:202-212` | Make TP2-C2 say explicitly that the guard asserts the *model* (canonical dump including `operations`) and the steps document are unchanged, not only the population. Name 1499/1567 in the TP2 inventory as protecting model state. |
| R1-04 | hardening | medium | The plan says the receipt binds "model object, model digest, population digest, check options". That is not enough for a byte-identical report. It must also carry (a) the full internal `CheckReport`, including excluded fields that assurance reads, and (b) the branch ids recorded during the pre-check, replayed into the active `capture_branches` contexts as `CalculationScope` does. Neither caused a difference in the 28 simulated runs, but the trace feeds assurance `complete` and the execution identity. | `assurance/core.py:419-455, 466-480`; `api.py:374-382, 406-436`; `extension_preparation.py:133-138`; `checker/_reports.py:87-99` | Add both to TP3-C1. Add a TP3 test with a walk whose pre-state alone reaches a branch, and assert assurance and trace parity. |
| R1-05 | hardening | medium | The plan binds the receipt to a population *digest*, not to a population that is still validated. A different `Population` object with equal content but no stamp (for example a copy built from `model_dump`) matches the digest. The pre-check is the step that would raise `UnvalidatedPopulationError`. In the probes, the walk still refused (exit 70) through later marker checks on all 4 tested models, so today's protection is incidental. | `checker/_core.py:344, 1518`; `population.py:168-191`; probe `r1_probe5.py` | Make receipt validation re-assert `pre.matches_validation_marker(model)` (which re-derives both digests anyway) and add an "unstamped equal-content population" case to TP3-C3. |
| R1-06 | hardening | medium | TP-D5(i) mints the receipt through "a separate opt-in API", leaving `api.check` unchanged. If minting requires a check in addition to the caller's `api.check`, the reporter's check-then-transition sequence gains one run and loses one: net zero. TP-D6 measures "per transition that presents a receipt" and would hide this. | plan:376; TP0 spec:81 (alternating 7 checks + 6 transitions) | Require the minting API to return the same payload as `api.check` together with the receipt. Gate on the net checker runs of the whole 13-call sequence, not per transition. |
| R1-07 | completeness | low | `api.transition` accepts path inputs and loads a fresh `Model` and `Population` for them (`api.py:274, 300`), so an object-bound receipt can never match a path input. TP3-C3 lists "wrong model object" but doesn't say what happens with path inputs. Where the receipt refusal sits relative to the TypeError guards and the exit-3 load refusals is also unpinned (standing rule 3). | `api.py:223-302, 745-752`; `checking_service.py:74-83` | The TP3 spec should state that receipts require in-memory `Model` and `Population` inputs and should pin the refusal order with a test. |
| R1-08 | completeness | low | TP0 T5 and TP1-C2 require that a nested model mutation "fails `matches_validation_marker`". A mutation under `operations` (or `warnings`) changes the index key but deliberately leaves the marker true, so a test that picks those fields contradicts its own expectation. | TP0 spec:173; plan:238-240; `values.py:176-191` | Name the mutated field (for example a `fact_types` row). Add an operations-mutation row that asserts a fresh index and an unchanged marker. |
| R1-09 | completeness | low | The n + 2 figure is an upper bound: unloadable intermediates and an unloadable computed post reduce it. "TP1 +1 key per loaded intermediate" is looser than the design needs, because intermediates share the call's model. | `transition.py:2015-2019, 2093-2096`; plan:47-50, 236-237, 377 | Say "at most n + 2". Justify or drop the per-intermediate allowance. |
| R1-10 | completeness | low | "transition.py deep-copies … at 8 sites": there are 10 `copy.deepcopy(` call sites (in 7 functions) on both `73ea302` and `2d1ff4d`. | `transition.py:202, 842, 858, 863, 1476, 1499, 1512, 1567, 1589, 2103` | Recount, or defer to the TP2-C1 inventory. |

No blocking findings survived. The 28 simulated pre-skip runs produced byte-identical
payloads, so TP3 is feasible as scoped. The CR-01 guarantee between calls holds under TP1
design (a) as long as each public call computes the key fresh.

**Verdict: approve-with-fixes.** R1-01 through R1-06 should be fixed in plan text before
approval, because they decide whether TP1 and TP3 can be demonstrated soundly. R1-07
through R1-10 can wait for the phase specs or close.
