# Phase TP0: Portable workload, counters and parity baseline

## 1. Status

**Awaiting owner review.** This is draft r5. Implementation is blocked until
the owner approves the plan (r4 or later) and rules on this spec's D-rows. The
workload input is available.

## 2. Provenance

- Plan: [transition-check-performance-plan.md](transition-check-performance-plan.md)
  draft r4, §4 TP0. Plan-level rulings TP-D1 to TP-D7 are recorded there.
- Source: [issue #24](https://github.com/vasiloglou/gnd-public/issues/24).
  Baseline `2d1ff4d`.
- Review history:
  - r1 to r3 were drafts.
  - Four local readers reviewed r3 (SHA-256 `f0073202…dd7b`).
  - r4 repairs their findings, marked `(p1)`; see
    [the disposition](plan-review-r1-disposition.md).
  - Readers 2 and 4 ran the confirmation round over r4 (SHA-256 `64731157…f45d`)
    and both returned approve-with-fixes. All 17 of their new findings attack
    text r4 created. Under the declared stop rule, r5 applies their fixes,
    tagged `(p2)`, and the review stops. **r5's repaired sentences carry no
    review opinion of their own.**
- **Planning observations, not TP0 evidence.**
  - Replaying the anonymized copy and the original gave identical exit codes
    and counts on all 13 calls. Every call exits 2 with zero failures.
  - Reader experiments on the copy measured 25 checker runs, 540 `for_model`
    calls (65 of them from `load_population`) and about 2.77 M deep-copied
    nodes. 95% of those nodes come from `ModelIndex.fact_types`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan TP0-C1 | Anonymized workload plus `course` control, with transform-preservation proof | §6 fixture, D7, T1, T2 |
| Plan TP0-C2 | Counters at every lookup owner, each with a liveness control | §6 counters, T4 |
| Plan TP0-C3 | Parity digests for every completion-predicate-2 surface, plus captured branch traces | §6 parity, T3, T6, T7 |
| Plan TP0-C4 | Baseline evidence and shape comparison | §6 baseline, T7 |
| Plan TP0-C5 | Targets restated in counter units | §6 baseline, D4 |
| Plan O9, O12 | `compiled_operations`, admission, CLI and with-post surfaces | §6 surfaces, T3, T6 |
| Plan O14 | No downstream names in committed files | D7, T1 |
| Plan O10 | Layer map unchanged | §4 rule TP-R5 |

## 4. Rules bound to TP0

Standing rules (`standing-rules.md`):

1. **Totality:** the tool reads only the committed fixtures, through the
   public, already-total loaders. It adds no new document consumer.
2. **Input cap vs algorithm:** does not apply, because TP0 adds no runtime
   work. A 120 s wall guard per test (D5) is a hang guard only.
3. **Validation order:** does not apply, because no boundary changes.
4. **One walk:** one installer patches every lookup owner of every counted
   callable, found by one scan of loaded `gnd.*` modules. Counters are not
   patched one call site at a time.
5. **One normative home:** the counter set and the digest normalization are
   defined once, in the tool. The test imports them.
6. **Measurement over argument:** this phase is the measurement.

Plan rules:

- **TP-R1:** TP0 changes no runtime code. `git diff 2d1ff4d -- src/gnd` is
  empty at record time.
- **TP-R2:** T5 pins today's invalidation, including the operations-only case,
  as TP1's baseline.
- **TP-R3:** TP0 creates no receipt. The parity oracle it builds is what TP3's
  identical-report gate uses.
- **TP-R4:** counters are gates. Timings are evidence.
- **TP-R5:** no runtime home and no layer-map entry are added. The tool lives
  under `tools/`, outside the runtime layer scan.
- **TP-R6:** the import transform keeps downstream names out of the repository
  (D7).

## 5. Goal

Two commands exit 0:

- `uv run pytest -q tests/test_transition_cost_workload.py`.
- `uv run python tools/measure_transition_cost.py --out <dir>`. It writes
  schema-tagged `counters.json`, `digests.json` and `timings.json`, which are
  retained under `evidence/TP0/`.

`git diff 2d1ff4d -- src/gnd` is empty.

## 6. Design

### Workload fixture: `tests/fixtures/transition_cost/` (o2, p1)

The reporter's reproduction bundle, imported with an anonymizing transform:

| File | Content |
|---|---|
| `steps.orm.json` | generated steps metamodel: 6 operations, 36 constraints, 65 derived fact types |
| `NN-check-population.json` (7) and `NN-transition-population.json` (6) | the population passed to each call, about 360 facts each |
| `NN-transition-steps.json` (6) | the step document of each transition. Each is a **1-step** walk. |
| `calls.json` | the 13-call sequence, alternating check then transition |
| `PROVENANCE.md` | neutral source description, the transform, and the SHA-256 of every file before and after the transform |

**Transform** (applied once, by a committed script
`tests/fixtures/transition_cost/anonymize.py`, about 40 lines, which contains
no downstream names):

1. Set `model_id` to `urn:gnd-fixture:steps@1` in the model and every
   population.
2. Set every provenance `user_note` to `Sealed step programs.`
3. In each step document, set `model` to `steps.orm.json` and recompute
   `model_digest` and `operations_digest` with `transition_model_identity` and
   `operations_digest`.

The original digests are verified before the transform, and they matched.

**Proof that the transform preserves results**, recorded at import in
`evidence/TP0/import.json`: for all 13 calls, the exit codes, counts, counters
and normalized digests are equal before and after the transform. The original
bytes are not committed.

**Control:** the packaged `src/gnd/examples/plan_apps/course` model and its
`plans/attempt-1..3.steps.json`. These files hold bare step lists, so the tool
wraps each one with the app's own `steps_document` helper
(`plan_apps/core.py:61`), which adds the header that ties the plan to its
model. Passed unwrapped, they are refused with exit 3 and 0 checker runs.
Wrapped, `attempt-3` (3 steps) exits 0 with exactly 5 checker runs and covers
intermediate checks. `attempt-1` and `attempt-2` exit 1, which gives TP3 its
failing-receipt case. (p2)

### Measurement tool: `tools/measure_transition_cost.py` (~250 lines)

```text
measure_transition_cost.py --out DIR [--repeat N=5] [--workload {reporter,course,all}]
```

**Surfaces** (p1). Each surface records an exit code, a normalized payload
digest, and a branch-trace digest taken under `capture_branches()`:

| Surface | Reporter workload | `course` control |
|---|---|---|
| `api.check(model, pop)` | 7 check populations | pre population |
| `api.check(..., compiled_operations=True)` | 7 check populations | pre population |
| `api.check(..., admission=True)` | 7 check populations (the result is recorded whatever band it lands in) | pre |
| `api.transition(model, pre, steps)` | 6 calls | `attempt-3` |
| `api.transition(model, pre, steps, post)` with a declared post | 6 calls; the declared post is the next call's check population (exit 2, 0 failures). The computed post was rejected: it makes every call exit 1. (p2) | — |
| batch `gnd check --populations DIR` | the 7 check populations | — |
| CLI `gnd check MODEL POP --format json` | call 00 | pre |
| CLI `gnd check MODEL --pre PRE --steps STEPS --post POST --format json` (the CLI's transition arm needs all three) | call 01, with call 02's population as post | — |

**Counters** (p1). The installer takes each target callable, scans every loaded
`gnd.*` module for attributes that are that object, and wraps all of them.
That covers name-bound imports such as `from gnd.checker._core import check`.
Classmethods and methods such as `ModelIndex.for_model` and `Model.model_dump`
are patched on their class. (p2)
Deep copies are the exception. CPython's `copy` module binds `deepcopy` as a
default argument for its recursion, so no wrapper sees the recursive calls.
They are counted instead with a profile hook (`sys.setprofile`) that fires on
`copy.deepcopy.__code__`, whatever the binding.

| Counter key | Target | Unit |
|---|---|---|
| `checker_runs` | `gnd.checker._core._check_dispatch` | calls (covers `check`, `check_with_anchors` and the partial variants) |
| `model_index_calls` | `gnd.model_index.ModelIndex.for_model` | calls |
| `model_index_key_paths` | `Model.model_dump` whose caller is in `gnd.model_index` | calls: the ModelIndex key path. About 540 on the baseline: 13 per check, 64 per transition and 5 per load in the readers' census. (p2) |
| `model_dumps_other` | `Model.model_dump` from every other caller (marker digest, applicability, extensions, semantic adapter, transition helpers) | calls. About 457 on the baseline. TP1 must not increase it. (p2) |
| `model_digests` | `gnd.values._model_digest` and every alias (`population._model_digest`, `transition._model_digest`, …) | calls |
| `deepcopy_calls` | profile hook on `copy.deepcopy.__code__`, outermost frames whose caller is under `src/gnd` | top-level calls, per GND call site |
| `deepcopy_nodes` | the same hook, every invocation | nodes copied (about 2.77 M on the reporter replay in planning) |
| `extension_views` | `gnd.extensions.structured_extension_view` and aliases | calls |
| `correspondences` | `gnd.correspondence.correspond_snapshot` and aliases | calls |

`counters.json` has schema `transition-cost-counters/1`. It lists per-workload,
per-surface counts plus whole-workload totals; for example, `checker_runs` for
the reporter replay is expected to be 25.

**Parity.** For each surface, `digests.json` holds the SHA-256 of
`artifacts.canonical_json_bytes(normalized_payload)` and of the captured
branch set. `NORMALIZED_FIELDS` blanks exactly the input-path fields of the
payload: `model`, `population`, and the transition's `pre`, `steps` and `post`
when they are present. Nothing else is removed. CLI and API payloads differ
only in those fields (p2). Default payloads carry no timings. Default payloads carry no branch traces either, which is why
the traces are captured separately. (p1) `capture_branches()` returns an
unordered set, so the trace digest is taken over the sorted ids. (p2)

**Baseline note:** `evidence/TP0/README.md` records:

- the machine and the interpreters: 3.11 and 3.13, plus the session default
  if it differs;
- the repetitions, the medians, and the variance between runs. Timing runs
  are separate, uninstrumented runs, because the deep-copy profile hook slows
  execution about 2.8 times; (p2)
- the profiling-inflation caveat;
- the shape comparison with the issue's figures (25, 535, 2.7 M);
- the targets restated in counter units (TP0-C5).

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | Counting method | (a) test-time wrappers at every lookup owner, as above; no runtime diff. (b) a runtime counter hook: always available, but changes `src/gnd`. **Proposed (a).** Readers verified that a defining-home-only patch counts 0 of 25 checker runs. |
| D2 | Use of the reporter's driver | **Proposed:** reimplement its call logic, about 15 lines, in the tool. Do not commit the driver. One harness carries all counters, and no downstream-authored script lands in the repository. |
| D3 | Normalization | Minimal: absolute paths only, with branch traces digested separately (proposed). The alternative also drops traces, which would hide the internal reorderings TP-R1 forbids. |
| D4 | Targets in counter units | TP-D6 as ruled, measured as `model_index_key_paths` (with `model_dumps_other` not increasing), `deepcopy_nodes` and the `checker_runs` workload total. Confirmed or re-argued after the baseline, with the arithmetic (plan D-p1-2). |
| D5 | Hang guard | 120 s wall per test (proposed), or none. |
| D6 | Interpreters | 3.11 and 3.13, plus the session default, recorded (proposed). |
| D8 | Course control wrapping (p2) | Wrap with the app's `steps_document` helper (proposed). The alternative is to commit wrapped copies, which would duplicate packaged data. |
| D7 | The anonymizing transform | **Agent proposal (p1), not yet ruled.** The three edits listed in §6. The cost is that committed bytes differ from the reporter's. The preservation proof covers exit codes, counts, counters and digests. The alternative is to commit the original bytes, which breaks O14. |

## 8. Tests

All tests are in `tests/test_transition_cost_workload.py`. They pass on
baseline `2d1ff4d`.

| # | Case | Expected |
|---|---|---|
| T1 | The model validates. 13 populations load. 6 step documents parse. Every file's SHA-256 matches the post-transform column of `PROVENANCE.md`. `model_id` equals `urn:gnd-fixture:steps@1`, and every `user_note` belongs to the allowed set `{"Sealed step programs."}` (an allowed-values check, so no forbidden name is spelled in the test). | pass |
| T2 | Replaying `calls.json` gives the pinned exit code and counts for every call (13 rows, all exit 2, zero failures). The wrapped `course` walks give exit 0 (`attempt-3`) and exit 1 (`attempt-1`, `attempt-2`). | pass |
| T3 | Batch `--populations` over the 7 check populations exits **2** with 0 failures. Both CLI arms give the pinned exits, **and** their normalized payload digests equal those of the matching API calls. Comparing digests rather than exits keeps a mistyped command, which also exits 2, from passing. (p2) | pass |
| T4 | Counter liveness, both directions. On the reporter replay, `checker_runs == 25`. An extra `api.check` adds exactly 1. Reading `ModelIndex.for_model(m).fact_types` once on a fixed model adds exactly 1 `deepcopy_calls`, plus the `deepcopy_nodes` computed independently from that model's fact-type tree. (p2) Every other counter is above 0 on the replay. The wrapped `course` `attempt-3` walk records exactly 5 `checker_runs`. (p2) | pass |
| T5 | CR-01 baseline. Mutating a nested constraint after load makes `matches_validation_marker` false. Mutating only an operation leaves the marker true, but changes the ModelIndex key. Both facts are pinned for TP1. | pass |
| T6 | Parity self-check. Two runs give identical `digests.json`. A runtime mutant (a wrapper that flips one constraint verdict in the checker result) changes the payload digest. A mutant that drops one recorded branch changes the trace digest. (p2) A reordering mutant cannot change a set, so it is not used. | pass |
| T7 | `measure_transition_cost.py --repeat 1 --out tmp` exits 0 and writes three schema-tagged files that contain every surface in §6. | pass |

**Branch walk:** every counter has a two-direction liveness case (T4). Both
digests have mutant cases (T6). The CR-01 pins cover both digest kinds (T5).
The anonymity check is an allowed-values test, not a forbidden-string scan
(T1). The old T8 is dropped, because the layer tool does not scan `tools/`, so
it could never fail. TP-R5 is argued in §4 instead.

**Verification selection:**

- Focused gate: the command in §5, plus `tests/test_rf1_layering.py` and
  `tests/test_public_transition_contract.py` as unchanged-runtime controls.
- Slow cadence: the broad suite, run only on explicit owner selection.

## 9. Out of scope for TP0

Any change under `src/gnd`, and meeting the targets. Running the downstream
application. Timing assertions. Committing the reporter's original bytes or
driver.

## 10. Size

Estimate:

- **Fixture:** about 600 KB of JSON in 21 files, plus a provenance note of
  about 40 lines.
- **Code:** a transform script of about 40 lines and a tool of about 250 lines.
- **Tests:** about 220 lines.

Runtime: 0 lines. The real sizes are measured at record time.

## 11. Approval instrument

This prose. The fixture is imported after approval, and it has no answer key
to keep separate. Corpus-first is the default for phases that ship serialized
formats. It is not used here because `counters.json` and `digests.json` are
internal evidence files that no caller consumes, and the pinned exits and
counts are already fixed by the bundle. (p1) Expected results are the pinned exits and counts, plus
counter liveness.
