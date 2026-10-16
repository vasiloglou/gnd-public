# Per-step transition and check cost

Draft r5, 2026-10-16. Milestone: `transition-check-performance`.
Source: [gnd-public issue #24](https://github.com/vasiloglou/gnd-public/issues/24).
Inspection baseline: `2d1ff4d` (runtime bytes unchanged since `73ea302`).
Planning only. Plan approval, phase execution, implementation and publication
have not occurred.

**Revision history.** Tags mark where a sentence came from:

- **r2 `(o)`:** rulings the owner relayed on 2026-10-16 after a conference with
  the issue's reporter (TP-D1 to TP-D4).
- **r3 `(o2)`:** later the same day, the owner adopted the recommended defaults
  for TP-D5 and TP-D6, selected four local readers for TP-D7, and pointed to
  the reporter's reproduction bundle on this machine.
- **r4 `(p1)`:** repairs for the first plan review, four local readers over r3
  (plan SHA-256 `e691348d…92ab`). See the
  [disposition](plan-review-r1-disposition.md).
- **r5 `(p2)`:** repairs from the confirmation round. Readers 2 and 4 reviewed
  r4 (`9b21a824…8fdf`) and both returned approve-with-fixes. All 17 new findings
  were self-inflicted, so the stop rule ended the review. **Sentences marked
  `(p2)` carry no review opinion of their own.** Rulings on individual decisions are not approval of the plan.

## Problem and completion predicates

Issue #24 reports that a downstream application's imperative plan execution
spends more than 95% of its wall time in GND checks and transitions. The SQL
takes about 1 ms per step. On the issue's pinned GND `8a3a98ba`, the profiled
workload was 13 public calls (7 `api.check`, 6 one-step `api.transition`). It
made 25 checker runs and 535 `ModelIndex.for_model` calls, deep-copied about
2.7 M objects, and spent 5.8 s cumulative in extension correspondence. Those
numbers overlap, because they nest. The reporter timed the 13 calls at 3.96 s.
The issue's 4.6 s figure is the same program measured another way; the
difference is not material here. (p1)

**Planning measurements on current bytes (p1).** These are reader experiments
on an anonymized scratch copy of the reporter's bundle. They are not TP0
evidence.

- **Counts reproduce:** 25 checker runs and 540 `for_model` calls. 65 of the
  540 come from `load_population`, outside any public call. About 2.77 M
  objects are deep-copied, 95% of them by `ModelIndex.fact_types`.
- **Upper bound on the gain:** unsafe simulations of TP1, TP1+TP2 and TP1+TP2+TP3,
  median of 3 runs, moved wall time 7.33 → 5.13 → 4.55 → 4.11 s (−30%, −38%,
  −44%). Report digests were identical in every mode. Under profiling,
  extension re-derivation is then the largest remaining cost (about 3.6 s of
  11.3 s profiled). That work is deferred (TP-D4). **This milestone is expected
  to remove at most about 44% of GND wall time on this workload, not most of
  it.**
- **Timing noise:** runs vary about 20% between sessions. Profiling inflates
  times 2.7 to 3.2 times.

Inspection of current bytes:

- `ModelIndex.for_model` (`src/gnd/model_index.py:52`) dumps the model, walks
  every container, and hashes canonical JSON on **every** call before it looks
  in the 32-entry cache. Its key includes `operations` and excludes `warnings`.
- `Population.matches_validation_marker` (`population.py:167-190`) compares
  `gnd.values._model_digest`. That digest is a different one: it excludes
  `operations` (`values.py:176-191`). Changing only `operations` changes the
  ModelIndex key but not the marker. (p1)
- `transition._evaluate_to_state` checks the pre-state, then each loadable
  intermediate. `evaluate_plan` checks the computed post, and `evaluate` checks
  the declared post. A walk of n steps runs **at most** n + 2 full checks;
  intermediates that cannot be loaded run fewer. (p1)
- GND does not mutate model content during a transition today. The only write
  is the private `_references` attribute (`api.py:278`). The deep copies of
  operations at `transition.py:1499` and `1567` are what keep the write at
  line 1951 from reaching `model.operations`. (p1)
- The earlier repairs milestone (`analytics-m3-repairs`, phase-13 record)
  ruled "no report/verdict/crosscall cache" and kept full intermediate and post
  checks mandatory. That ruling was scoped to that milestone. TP-D3 supersedes
  it for the receipt opt-in only. (p1)

**Outcome:** the same reports, byte for byte, at a lower counted cost. The
milestone ships three things in order:

1. Cheap `ModelIndex` hits that keep the CR-01 mutation guarantee.
2. Fewer deep copies of inputs that no code path mutates.
3. An opt-in, receipt-bound skip of an already-checked pre-state.

Incremental evaluation is deferred (o, TP-D4).

The milestone can close when:

1. The reporter's anonymized workload is committed, and the packaged
   `plan_apps/course` plans run as a control, wrapped with the app's
   `steps_document` helper (`attempt-3` is a 3-step walk). (p2) Its baseline pins
   the counters, the parity digests and informational wall medians. (p1)
2. On those workloads, every default-path public result is byte-identical to
   the baseline after each phase. The surfaces are: `api.check` (default and
   `compiled_operations=True`), `api.transition` without post and with a
   declared post, batch `check --populations`, and both arms of the CLI
   `gnd check`, snapshot and `--pre/--steps/--post` transition. (p2) The branch traces captured under `capture_branches()` must
   also match. (p1)
3. `model_index_key_paths` meets the TP1-C1 bound, and `model_dumps_other`
   does not increase. A model mutated between calls, including an
   operations-only mutation, gets a fresh index. (p1, p2)
4. Each removed deep copy has a guard test that fails if the copy was needed.
   Deep-copied nodes on the workload fall by at least half. (p1)
5. On the workload, using receipts drops the total checker runs from 25 to 19.
   Minting the receipts adds no checker runs. Reports are identical. Forged,
   stale, mutated and other-model receipts are refused with named errors
   before evaluation. (p1)
6. Wall-time results are reported against the about-44% ceiling, with their
   limits, and are not a gate (TP-R4). (p1)
7. Focused gates, independent diff reviews, docs for the new public surface
   and the question sweep are recorded. A PR is submitted. Owner acceptance is
   separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| TP-R1: Same answers | Default-path payloads, verdicts, band precedence, exit codes and captured branch traces stay byte-identical. This is proven by the TP0 parity digests and the existing contract tests. A speedup that changes a result is a semantic change and needs its own ruling. |
| TP-R2: CR-01 stays intact | A cache hit must never let a mutated model or population reuse a stale index, extension or verdict. Mutation of nested content, by any route, invalidates. That includes `operations`, which the ModelIndex key covers and the marker digest does not. A memo keyed on object identity alone is refused (TP-D1). |
| TP-R3: Receipt-bound reuse | (o, p1) Only the pre-state check may be skipped. It needs an explicit caller action and a receipt that GND minted in-process while a check completed. The receipt binds the model object, the ModelIndex key, the population content digest and the population's validation marker, the check options, the complete internal `CheckReport`, and the branch set recorded during that check. A bare digest or caller-supplied JSON is never proof. Intermediate and post checks stay mandatory. |
| TP-R4: Counters gate, wall time informs | Gates assert deterministic counters. The tool counts at every lookup owner, not only at the defining home. Wall medians are evidence, recorded with machine, interpreter and repetitions. No gate depends on timing. |
| TP-R5: One home per cache | Each memo or per-call scope has one defining home, one invalidation rule and a bounded size. Zero new layer allowances (`tools/gnd_layers.json`). Follow the ModelIndex policy in AGENTS.md. |
| TP-R6: Approval and evidence | `auto=false`. Plan authorship is not approval. Preserve existing records and evidence. No inherited certification. Downstream consumers stay anonymous in every artifact. |

Each phase spec binds every rule above and every paid-for rule in
`.claude/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issue #24 (pinned GND `8a3a98ba`) | Problem, profile, requests 1–4 |
| The reporter's reproduction bundle (anonymized on import) | Exact workload |
| `src/gnd/model_index.py`, `population.py`, `values.py`, `documents.py`, `transition.py`, `api.py`, `checker/_core.py`, `checking_service.py`, `batch.py` | Hotspot homes and lookup owners |
| `analytics-m3-repairs` records 008–013 | Same-call preparation sharing and its boundary |
| `code-refactoring` RF6 and RF9 records | Query layer, shim inventory, layer map |
| `compiled-snapshot-obligations` close | `compiled_operations` check mode |
| AGENTS.md, CONTRIBUTING.md | PR, layering and ModelIndex rules |

A `gnd coverage MODEL` census measures experiment claims, not runtime cost, so
it does not decide this framework scope. Caller-side changes belong to the
downstream application. (p1) Three related session requests are recorded in
the reporter's own roadmap: counts and observed facts in session feedback, a
host hook for observed facts between attempts, and an agent-call timeout. The
first two go with deferred request 4. The timeout is unrelated to performance.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Reproducible baseline on current bytes (issue §Reproduction) | proposed target | TP0 |
| O2 | Request 1: cheap `ModelIndex.for_model` hits | requested | TP1 |
| O3 | CR-01 mutation invalidation (`population.py:167-190`, `documents.py:21-24`) | inherited | TP1, TP2, TP3 |
| O4 | Request 2: avoid deep copies of immutable inputs | requested | TP2 |
| O5 | ModelIndex detached-value query contract | inherited | TP2 |
| O6 | Request 3: transition without a full pre-state re-check | requested, ruled TP-D3 | TP3 |
| O7 | Prior repairs-milestone boundary (`analytics-m3-repairs/013`) | inherited, scoped | TP-D3; TP3 spec records it |
| O8 | Request 4 and the two related session requests | deferred, TP-D4 | close carryover |
| O9 | Report parity across all public surfaces | cross-cutting gate | every phase |
| O10 | Layer map, shim inventory, ModelIndex policy | cross-cutting | every phase |
| O11 | Docs for the new public surface | cross-cutting | TP3 |
| O12 | `compiled_operations` and admission results unchanged | inherited | TP0 parity surfaces |
| O13 | Downstream application acceptance | carried | the reporter, after merge |
| O14 | Downstream anonymity in committed artifacts (owner, 2026-10-16) (p1) | owner constraint | TP0 import, every phase |

## 2. Contract proposal and product behavior

**Defaults stay the same.** Only counted internal work changes.

**TP1 (cheap index hits).** Ruled TP-D1 (a): compute the ModelIndex key once
per public call and reuse it for every lookup in that call. The key is
ModelIndex's own canonical key, which includes `operations`. It is **not** the
marker's `_model_digest`. (p1) The proposed mechanism is a per-call scope,
held in a `ContextVar` owned by `gnd.model_index`, entered by the public entry
points (`api`, `checking_service`, `transition`, `checker._core`, and the
population loader). That needs no new layer allowance. The existing
`calculation_scope` cannot be used, because it lives above `model_index`.
Outside any scope, `for_model` behaves exactly as today.

**TP2 (copies).** Remove a deep copy only where nothing mutates the value
downstream, or where GND owns the value frozen. The main target is
`ModelIndex.fact_types`, which accounts for 95% of copied nodes. Its public
query must keep returning detached values (O5). The proposed route is an
internal, read-only, non-copying view for GND's own callers, alongside the
unchanged public accessor. The operation copies at
`transition.py:1499/1567` stay, unless TP2 replaces them with an equivalent
guard that has its own test. (p1)

**TP3 (receipt-bound reuse).** TP-D3 and TP-D5 are ruled. (p1)

- **Minting:** a separate opt-in public function returns the same payload as
  `api.check` *together with* a receipt. Minting costs no extra check.
- **Use:** `api.transition` gets a new keyword-only option that takes the
  receipt.
- **Validation:** the receipt is checked against the model object, the
  ModelIndex key, the population digest and the population marker, and the
  options. If it passes, its stored `CheckReport` and branch set replace the
  pre-state check. If it fails, the call is refused with a named error before
  evaluation. The receipt binds the population by content digest, and requires
  the population object presented to carry a valid marker for the same model.
  It does not require the same population object. (p2)
- **Which checks can mint:** "failing pre-check" (TP-D5 ii) is proposed to
  mean exit 1 (an alethic failure) or a refusal band (≥ 3). Exit 0 and exit 2
  (warnings or vacuity) mint reusable receipts. This needs owner confirmation,
  because every call in the workload exits 2. (D-p1-1)
- **Threat model:** the receipt guards against accidental reuse, meaning stale,
  mutated, other-model or other-option state. It does not guard against
  hostile code in the same process, which can call internal APIs anyway.
- **Not covered:** receipts cannot be serialized, and the CLI gets no
  equivalent.

**TP4:** deferred (o, TP-D4). The phase ID is reserved.

## 3. Dependencies and artifact homes

TP0 → TP1 → TP2 → TP3 → close. TP1 and TP2 may swap order. TP3's gate is
measured after TP1 and TP2. The workload input is available (o2). No phase
depends on provider review, downstream execution, publication or
certification.

| Artifact | Home |
|---|---|
| Plan, specs, records, review notes | `.gnd-planning/milestones/transition-check-performance/` |
| Workload fixture | `tests/fixtures/transition_cost/`: the reporter's model, 13 populations, 6 step documents and `calls.json`, anonymized on import (see the TP0 spec). (p1) The reporter's driver script is **not** committed; its call logic is reimplemented in the tool. |
| Control | packaged `src/gnd/examples/plan_apps/course` (3-step `attempt-3` plan), unchanged |
| Measurement tool | `tools/measure_transition_cost.py` (TP0) |
| Measurements | `evidence/` of this milestone |
| Runtime changes | defining homes: `model_index.py`, `transition.py`, `checker/_core.py`, `checking_service.py`, `population.py`, `api.py` |

## 4. Phases

### TP0: Portable workload, counters and parity baseline

Spec: [phase-TP0-spec.md](phase-TP0-spec.md), awaiting owner review.

- **TP0-C1:** import the reporter's workload, anonymized, with a provenance note
  and a recorded proof that the transform preserves results. Commit the
  `course` control alongside it. (p1)
- **TP0-C2:** counters for checker runs, ModelIndex calls and key-path runs, the
  marker digest, deep-copy calls and nodes, and extension views. Each counter
  is installed at every lookup owner and has a liveness control. Runtime code
  is unchanged. (p1)
- **TP0-C3:** parity digests for every surface in completion predicate 2,
  including captured branch traces. (p1)
- **TP0-C4:** baseline evidence and a shape comparison with the issue.
- **TP0-C5:** counted targets are restated in counter units, from the
  baseline. Any change to the ruled TP-D6 values is re-argued, with the
  arithmetic. (p1)

### TP1: Cheap ModelIndex hits under CR-01

- **TP1-C1:** `model_index_key_paths` (model dumps made by `gnd.model_index`) are
  at most 1 per public call, plus 1 per loaded intermediate and loaded
  population, on both workloads. `model_dumps_other` does not increase. TP0
  sets the exact numbers. (p2)
- **TP1-C2:** each of these mutations between calls yields a fresh index: a
  nested constraint, an operation (marker unchanged), and a fact type. The
  test checks the index directly, because the marker refusal (exit 70) would
  otherwise hide a stale one. It also follows a mutate, re-load, check path.
  It fails on an identity-keyed mutant. (p1)
- **TP1-C3:** the cache and scope stay bounded. A time-bound test covers the
  key path. No scope leaks across threads or calls.
- **TP1-C4:** parity on all TP0 surfaces, plus the existing ModelIndex, RF6
  and layering tests.

### TP2: Remove deep copies of immutable inputs

- **TP2-C1:** an inventory of every deep copy the workloads reach (10 sites in
  `transition.py`, plus `model_index` and the checker homes), with a keep or
  remove ruling and reason for each.
- **TP2-C2:** each removed site has a guard test that mutates the would-be-shared
  value downstream and fails if the copy was needed. That includes the
  operation copies, if they are touched. (p1)
- **TP2-C3:** the public detached-value tests pass unchanged.
- **TP2-C4:** deep-copied nodes on the reporter workload fall by at least 50%,
  with parity. (p1)

### TP3: Opt-in, receipt-bound pre-state reuse

- **TP3-C1:** receipts are minted only by the opt-in check function and bind
  everything listed in TP-R3. The function's payload is identical to
  `api.check`'s.
- **TP3-C2:** replaying the reporter workload with receipts (each check's
  receipt feeds the next transition) totals 19 checker runs instead of 25. All
  13 payloads are identical to the run without receipts. The `course` control
  and the existing transition contract tests with reference populations and
  dynamic heads also produce identical reports with receipts. (p1) A direct
  test shows that the receipt's stored branch set reaches the captured trace:
  a receipt mutant with that set emptied changes the trace digest. Skipping
  the pre-check without replaying its branches leaves the same branch ids, so
  only a direct test can detect it. (p2)
- **TP3-C3:** a named refusal before evaluation for: the wrong model object; a
  mutated model, including operations only; a mutated population; a
  population that lost its marker; different options; a foreign object; a
  receipt from a failing check (as defined in D-p1-1); a receipt passed with path
  inputs, which always load a fresh model object. (p1)
- **TP3-C4:** docs (`docs/reference/python-api.md`, `capabilities.md`, a
  release note) and the public pins: `test_public_api.py`,
  `test_public_reference_signatures.py`, `test_v61_phase2_api.py`,
  `test_public_runtime.py`, and the `api.__all__` order. (p1)

### TP4: Incremental evaluation (deferred (o), TP-D4)

Not executed here. The close record hands request 4 and the two related
session requests to a successor milestone. That milestone must reconcile the
earlier selective-refresh path (`structured_extension_view(previous=…, refresh=…)`)
with CR-01. It is the next-largest cost (see Problem).

### Milestone close (not a feature phase)

Final parity and counter evidence, the four-reader close review (§8), the
question sweep, carryovers (O8 to a successor milestone, O13 to the reporter),
and a PR. Merge and acceptance remain separate owner actions.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1 | TP0-C1..C4 |
| O2 | TP1-C1, C3 |
| O3 | TP1-C2, TP2-C2, TP3-C3 |
| O4 | TP2-C1..C4 |
| O5 | TP2-C3 |
| O6 | TP3-C1..C3 |
| O7 | TP-D3; recorded in the TP3 spec |
| O8 | close carryover |
| O9 | TP0-C3, TP1-C4, TP2-C4, TP3-C2, close |
| O10 | every phase spec §4; layering test |
| O11 | TP3-C4 |
| O12 | TP0-C3 surfaces (`compiled_operations`, admission) |
| O13 | close carryover |
| O14 | TP0 T1 allowed-values check; every phase's diff review |

## 5. Documentation, skill and compatibility surfaces

- TP1 and TP2 need no public docs, only a release-note line at close.
- TP3 adds one public function and one keyword. Docs and pins are listed in TP3-C4.
- Packaged skills: the TP3 spec checks whether `gnd-dev-session` mentions
  transition pre-state checks.
- No compatibility break is planned. Deep-freezing was rejected (TP-D1).

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A stale index after mutation (CR-01) | TP1-C2 three mutation kinds, plus an identity-keyed mutant |
| A removed copy lets evaluation write into caller or model state | TP2-C2 guard tests; operation copies kept by default |
| A receipt reused across changed state | TP3-C3 refusals; receipt binds per TP-R3 |
| Receipts save nothing end to end | TP3-C2 workload total of 25 → 19; minting adds no checks |
| Counters miss work through name-bound imports | TP0 installs at every lookup owner, with liveness controls (T4) |
| Gains are smaller than the reporter expects | Problem section states the ~44% ceiling; extension work deferred |
| Timing noise is misread | TP-R4; variance and profiling inflation recorded |
| Downstream names leak into the repository | O14; TP0 T1 allowed-values check; review lens |
| A repair round introduces defects | §8 round budget and stop rule |

## 7. Out of scope

- Caller-side changes in the downstream application.
- Changing verdict semantics, constraint families, band precedence or default
  check counts.
- Cross-process, serialized or on-disk caches and receipts.
- Changing `analytics-m3-repairs` gates.
- Native, LQP and PyRel runtime performance.
- Publication, release and certification.
- Incremental evaluation, session objects and the three related session
  requests (TP-D4).

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, then the owner gate,
then implementation and focused tests, one independent local diff reader, a
refactoring review and a record. No code is written before recorded spec
approval. Plan and close use four local readers (TP-D7), each with a named lens:
reader 1 correctness and CR-01; reader 2 implementability; reader 3 protocol
and anonymity; reader 4 measurement design. Each reader is one reader, not a
panel.

**Round budget (p1):** plan review round 1 ran over r3. One confirmation
round runs over r4, limited to the blocking findings, read by the two readers
who returned *revise* (readers 2 and 4). After it, the convergence ledger
applies the stop rule from `review-convergence.md`: stop if the self-inflicted
ratio is above one half, or if no blocking finding remains. No third round
without a new owner request.

Work happens on a topic branch, then a PR. Merge requires the owner.

## 9. Per-phase verification story

| Phase | Expected result | Affected consumers and tests |
|---|---|---|
| TP0 | Workload committed; baseline counters, digests and timings retained; no runtime diff | new workload test; measurement tool |
| TP1 | `model_index_key_paths` at the TP1-C1 bound; `model_dumps_other` not increased; parity; three mutation kinds invalidate | `test_rf6_index.py`, other ModelIndex pins, `test_popvalidate.py`, transition contract tests, `test_rf1_layering.py` |
| TP2 | Nodes −50% or more; parity; guard tests | `test_public_transition_ir_immutability.py`, prior repairs-milestone preparation tests |
| TP3 | Workload 25 → 19 checker runs; refusals named; docs and pins | the TP3-C4 pin files; transition contract and trace tests |

Exact focused gate commands are **unresolved** until each phase spec names
them. The broad suite runs on explicit owner selection.

## 10. Owner decisions and open questions

| ID | Question | Ruling |
|---|---|---|
| TP-D1 | Cheap ModelIndex hits under CR-01 | **(o) (a):** one key per public call, reused within the call. (p1) The key is the ModelIndex canonical key, not the marker digest. |
| TP-D2 | Parity workload | **(o):** the reporter's exact files, anonymized on import, plus the `course` control. (o2) Available: 13 calls; 6 operations, 36 constraints, 65 derived fact types; about 360 facts per population. (p1) The driver script is not committed. |
| TP-D3 | Skip the full pre-state check? | **(o):** yes, opt-in and receipt-bound. Intermediate and post checks stay mandatory. This supersedes the earlier repairs-milestone boundary for this opt-in only. |
| TP-D4 | Incremental evaluation here? | **(o):** deferred, with the two related session requests. |
| TP-D5 | Receipt details | **(o2):** a separate opt-in minting API that returns the check payload with the receipt; no reuse after a failing pre-check; in-process only. The definition of "failing" is pending (D-p1-1). |
| TP-D6 | Counted targets | **(o2):** TP1 ≤ 1 key path per call (+1 per intermediate); TP2 ≥ 50% fewer deep copies; TP3 −1 checker run per receipt-bearing transition. (p1, p2) Restated in counter units: TP1 counts `model_index_key_paths`, with `model_dumps_other` not increasing; TP2 counts copied *nodes*; TP3 is the workload total of 25 → 19, with minting adding no checks. These restatements need the owner's confirmation (D-p1-2). |
| TP-D7 | Review instrument | **(o2):** four local readers for plan and close; one local reader per phase diff. |
| D-p1-1 | Does exit 2 (warnings or vacuity) count as a failing pre-check? | **Proposed: no.** Only exit 1 or a refusal band blocks minting. Otherwise TP3 cannot be demonstrated on the reporter's workload, where every call exits 2. |
| D-p1-2 | Accept TP-D6 in counter units (ModelIndex key paths; nodes; workload total 25 → 19)? | **Proposed: yes.** The reviewers showed that the call-count and per-transition readings can pass with no real saving. |

No open questions remain from r3. The `for_model` attribution question is
answered: all 540 calls are GND-side, 65 of them from the population loader.
