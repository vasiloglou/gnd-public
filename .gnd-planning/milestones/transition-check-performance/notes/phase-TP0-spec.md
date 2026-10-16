# Phase TP0: Portable workload, counters and parity baseline

## 1. Status

**Awaiting owner review; blocked on input.** Draft only. TP0 implementation
is blocked until (1) the plan is approved, (2) this spec's open D-rows carry
owner rulings, and (3) the reporter delivers the workload files
(TP-D2 (o)). Plan-level TP-D6 (targets) is settled here.

## 2. Provenance

- Plan: [transition-check-performance-plan.md](transition-check-performance-plan.md)
  draft r1, 2026-10-16, §4 TP0 and §10 TP-D2/TP-D6.
- Source: [issue #24](https://github.com/vasiloglou/gnd-public/issues/24),
  pinned GND `8a3a98ba`. Inspection baseline `73ea302`. Hotspot files are
  unchanged between them, apart from a 6-line static helper in `model_index.py`.
- r2 (o), 2026-10-16: workload changed to the reporter's exact profiled files,
  following owner-relayed rulings TP-D1 and TP-D2 (plan r2). No review has run
  over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan TP0-C1 | n-step workload across `api.check`, `api.transition` ± post, batch | §6 workload, §8 T1–T3 |
| Plan TP0-C2 | Deterministic counters without changing runtime code paths | §6 counters, D1, §8 T4–T5 |
| Plan TP0-C3 | Normalized report digests as parity oracle | §6 parity, D3, §8 T6 |
| Plan TP0-C4 | Baseline evidence + shape comparison with the issue | §6 baseline, §8 T7 |
| Plan TP0-C5 / TP-D6 | Counted targets (TP-D2 ruled in plan r2 (o)) | §7 D2, D4 |
| Plan O9, O12 | Parity includes `compiled_operations` and admission modes | §6 surfaces, §8 T6 |
| Plan O10 | Layer map zero allowances | §4 rule R5, §8 T8 |
| Standing rule 2 | Time bounds on added layers | §4 (inapplicable: no runtime layer added) |

## 4. Standing rules bound to TP0

1. **Totality:** the measurement tool reads only the committed fixture files.
   Its loader goes through the public `gnd.api` and model and population
   loaders, which are already total. The tool adds no new document consumer.
   (o) The imported driver is read as data and reviewed before it
   runs. It must call only `gnd.api`. Any private import is a refusal that
   goes back to the reporter.
2. **Input cap vs algorithm:** inapplicable. TP0 adds no runtime work. The
   workload test keeps a generous wall ceiling (D5) only as a hang guard.
3. **Validation order:** inapplicable. TP0 does not change any boundary.
4. **One walk:** the counters cover every public surface through one
   instrumentation harness, not one copy per surface.
5. **One normative home:** the parity normalization fields are defined once,
   in the tool, and the test imports them. The plan cites the tool.
6. **Measurement over argument:** this phase *is* the measurement. Every
   TP1–TP4 "is this needed" question cites TP0 numbers.
- TP-R1 (same answers): TP0 makes no runtime change. `git diff -- src/gnd` is
  empty at record time.
- TP-R2 (CR-01): T5 pins the current mutation-invalidation behavior as the
  baseline that TP1 must preserve.
- TP-R4: counters are gates. Timings are evidence only.

## 5. Goal

`uv run pytest -q tests/test_transition_cost_workload.py` exits 0 on the
baseline. `uv run python tools/measure_transition_cost.py --out <dir>` exits 0
and writes `counters.json`, `digests.json` and `timings.json`. Both files are
retained under `evidence/TP0/`. `git diff 73ea302 -- src/gnd` is empty.

## 6. Design

### Workload fixture: `tests/fixtures/transition_cost/` (o)

Supplied by the reporter (TP-D2) and committed unchanged:

- `steps.orm.json`: the generated steps metamodel rendered against the
  packaged `expense` data (about 36 alethic and deontic rules plus recursive
  derivations, according to the issue).
- The state populations (a few hundred facts each).
- The step documents: the profiled 5-step SUM program, and a 12-step
  program if supplied.
- The driver script, which calls only `gnd.api`.
- `PROVENANCE.md`: source revision, the generator call (`include_step_programs=True`),
  the SHA-256 of each file, and the statement that every file is built from
  packaged example data.

Control: the packaged `src/gnd/examples/plan_apps/course` model with
`plans/attempt-3.steps.json`, unchanged.

### Measurement tool: `tools/measure_transition_cost.py` (~200 lines)

```text
measure_transition_cost.py --out DIR [--repeat N=5] [--workload {fixture,course,all}]
```

Surfaces measured, each with an exit code and a payload:
`api.check(model, pre)`, `api.check(..., compiled_operations=True)`,
`api.check(..., admission=True)` (when the fixture supports admission),
`api.transition(model, pre, steps)`, `api.transition(model, pre, steps, post)`,
and batch `check --populations` over a directory of the pre population plus
each loadable intermediate.

Counters (D1 proposes patch-based counting via `unittest.mock.patch` wrappers
on the *defining* homes, so runtime code stays unchanged):

| Counter key | Wrapped callable |
|---|---|
| `checker_runs` | `gnd.checker._core.check` |
| `model_index_calls` | `gnd.model_index.ModelIndex.for_model` |
| `model_index_keys` | `gnd.artifacts.canonical_json_bytes` calls made from inside `for_model` |
| `model_digests` | `gnd.values.model_digest`, patched at its actual lookup owner `gnd.population._model_digest` |
| `deepcopies_gnd` | `copy.deepcopy` calls whose caller frame is under `src/gnd` |
| `extension_views` | `gnd.extensions.structured_extension_view` |
| `correspondences` | `gnd.correspondence.correspond_snapshot` |

Output `counters.json`:

```json
{"schema": "transition-cost-counters/1", "gnd_commit": "<sha>",
 "workloads": {"fixture-5": {"api.transition": {"exit": 0, "checker_runs": 7, "...": 0}}}}
```

The values shown are illustrative. TP0 records the real ones.

### Parity oracle

`digests.json` maps each workload and surface to the SHA-256 of
`artifacts.canonical_json_bytes(normalized_payload)`. Normalization (D3)
removes only fields that legitimately vary between runs (absolute paths, wall
timings if any are present). The tool lists those fields in one constant,
`NORMALIZED_FIELDS`. Branch traces are kept in the digest.

### Baseline note: `evidence/TP0/README.md`

Machine, interpreter (3.11 and 3.13), repetition count and medians. It also
compares the workload's checker-runs-per-step, `for_model`-calls-per-check and
deep-copy volume with the issue's profile (25 checks, 535 `for_model`, 2.7 M
deep copies for 5 steps). If the fixture's ratios are far below the issue's,
D2 is reopened before TP1.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| D1 | Counting method | (a) test-time `mock.patch` wrappers on defining homes: no runtime diff, but monkeypatch must target the actual lookup owner (AGENTS.md "patch the defining home"); (b) an internal counter hook in runtime: always available to later phases, but changes `src/gnd` in a measurement phase. Proposed: (a). |
| D2 (= TP-D2) | Workload | **Ruled (o) 2026-10-16:** the reporter's exact profiled files plus `course` control. Remaining sub-question: does the imported driver become the measurement tool's workload runner, or only a reference the tool replicates? Proposed: replicate it in the tool and keep the driver as provenance, so the counters wrap one harness (rule 4). |
| D3 | Normalization fields | Minimal list (paths, timings) vs also dropping branch traces. Dropping traces would hide internal reorderings that TP-R1 forbids. Proposed: minimal. |
| D4 (= TP-D6) | Counted targets for TP1–TP3 | As proposed in plan §10. They may be re-argued after TP0 numbers, with the arithmetic recorded (spec contract: ceilings changed after measurement are recorded, not slipped in). |
| D5 | Hang guard ceiling for the workload test | 120 s wall per test (generous, not a perf gate) vs none. |
| D6 | Interpreters for the baseline | 3.11 and 3.13 (as CS close) vs 3.11 only. |

## 8. Tests

All tests live in `tests/test_transition_cost_workload.py` unless named
otherwise. Expected exits are on baseline `73ea302`.

| # | Case | Expected |
|---|---|---|
| T1 | Fixture model validates; state populations load; step documents parse; every file's SHA-256 matches `PROVENANCE.md` | pass |
| T2 | `api.transition` without post on the supplied programs returns the computed post that the supplied driver reports for the same files | pass |
| T3 | Batch check over pre plus intermediates exits 0 | pass |
| T4 | Counter liveness: each counter is > 0 on the 5-step transition, and an artificial extra `api.check` call raises `checker_runs` by exactly 1 (the instrument can score both ends) | pass |
| T5 | CR-01 baseline: nested mutation of a model dict after loading makes `matches_validation_marker` false and the check refuses | pass |
| T6 | Parity self-check: two consecutive runs produce identical `digests.json`, and a deliberately perturbed payload produces a different digest (liveness) | pass |
| T7 | `measure_transition_cost.py --repeat 1 --out tmp` exits 0 and writes the three schema-tagged files | pass |
| T8 | `tests/test_rf1_layering.py` with `tools/measure_transition_cost.py` excluded from runtime layers (tools are not runtime) | pass |

Branch walk: every counter has a liveness case (T4). The parity digest has a
liveness case (T6). The CR-01 pin has a case that would fail if identity-only
matching were introduced (T5 mutates nested content without replacing the
object).

## 9. Out of scope for TP0

Any change under `src/gnd`. Performance targets being met. Running the
downstream application. Timing-based assertions. TP1–TP4 design choices beyond recording
the numbers they need.

## 10. Size

Estimate: fixture imported (size set by the reporter), provenance note ~30 lines,
tool ~200, tests ~180. Runtime source: 0. To be measured at record time.

## 11. Approval instrument

This prose. The fixture is imported after approval. It has no answer key to
keep apart from it. Expected results are "admits cleanly" plus
counter liveness, not graded verdicts.
