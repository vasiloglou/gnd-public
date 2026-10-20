# IE0 — Baseline and differential instrument

**Status: awaiting owner review; blocked on plan review/approval and IE0 decisions.**

## 1. Provenance

Derived from draft r1 of [the plan](incremental-evaluation-plan.md), §§0–10,
at inspection commit `058874965c54c19c4a4c34855cc9ca1b789394bf`.
Read the prior [TP0](../../transition-check-performance/002-phase-TP0.md),
[TP1](../../transition-check-performance/003-phase-TP1.md),
[TP2](../../transition-check-performance/004-phase-TP2.md),
[TP3](../../transition-check-performance/005-phase-TP3.md),
[close](../../transition-check-performance/006-milestone-close.md) and
[repairs phase 13](../../analytics-m3-repairs/013-phase-13.md) boundaries.
No independent review has run; neither this draft nor the plan has an approval
digest. The request to start the milestone is planning authorization only.

**Review update (p1), 2026-10-19:** four owner-selected local readers reviewed
the r1 plan with this supporting spec at SHA-256
`d49a5bcc4f06b5f1b500bd231637d54dcedc2bd9778976ba5817edb6a9ba19da`.
The timing design and T7 below are repaired for R4-F1; the preceding paragraph
describes the original draft checkpoint. Current amended bytes carry no new
review opinion. See [disposition](plan-review-r1-disposition.md). No owner
approval or phase spec gate occurred.

## 2. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IE0-C1: fresh source/config/fixture baseline | plan §4 IE0; IE-O1 | Design baseline; T1, T2 |
| IE0-C2: live counters and interleaved timing | plan §4 IE0; IE-O9; close sweep 14 | Counter registry, experiment protocol; T3, T4, T7 |
| IE0-C3: eligibility/dependency matrix, oracle negatives, receipt probe | plan §4 IE0; IE-O4/O6/O12 | Census and boundary stories; T5, T6, T8 |
| IE0-C4: frozen denominators/targets, estimate and input limitations | plan §4 IE0; IE-O3/O16 | Baseline decision output; T2, T9; D2/D3 |
| Exact section 9 story: “Reproducible full oracle; deliberately corrupted payload/trace/origin rejected; body and constraint counters live; no runtime diff” | plan §9 IE0 | T1–T8; explicit-path diff inspection |
| IE-R1..R10 and all standing rules | plan §0; process-phase standing-rules | next section; T3–T9 |
| No proprietary/private workload material | plan IE-O15; prior owner O14 | Existing fixture unchanged; synthetic controls only; T1 and diff review |
| Count actual lookup owners, avoid instrument laundering | prior TP0 record Refactoring review; standing rules | Registry identity census and negative controls, T3/T4/T6 |
| Current baseline rather than old-green inheritance | close Results; plan §9 | Fresh execution identities, no inherited pass claim |
| Public pins and layering selection | close sweep 13; plan IE-O10 | No runtime edit allowed; verification selection and invalidation rule |
| Skill/documentation surfaces | plan §5 | No product or skill change in IE0; census names later owners, T9 |
| Later inherited residuals | plan §4 residual table | Census includes report mutation, reference/outer scope hazards; unrelated completeness stays close-owned |
| Approve and commit spec before code | plan §8; close sweep 17 | Approval instrument and gate; no code now |
| D3/D5/D7/D9 | plan §10 | local D1–D5 decisions below; scheduling estimate output only |

## 3. Standing rules bound to IE0

| Rule | Application |
|---|---|
| IE-R1 full oracle | Compare normalized complete reports, exit, branch sets and semantic envelope/origins; never normalize counts or verdicts. |
| IE-R2 mutation | Census includes nested model/operations edits, population changes, lost markers and outer scopes. IE0 adds no cache. |
| IE-R3 admission | Driver calls public check/transition routes; no shortcut evaluation substitutes for baseline. |
| IE-R4 private generation | IE0 has no persistent evaluation state; each replay owns fresh loaded objects. Instrument wrappers must restore after errors. |
| IE-R5 counters | Count executed bodies/evaluators, not just API requests; warm-up excluded from measurements; T3/T4 fail for inert counters. |
| IE-R6 layer homes | Instrument existing defining and lookup homes in the tool only. No runtime, registry, layer-map or shim changes. |
| IE-R7 opt-in | New tool/test surface only; CLI/API defaults untouched. |
| IE-R8 bounds | Tool accepts only pinned local fixtures; bounded repeats and hang guards below. Future cache caps are not implemented here. |
| IE-R9 paid-for rules | Each of the six is bound in the following rows. |
| IE-R10 evidence/privacy | Public controls, explicit-path commits and no private imports or approval invention. |
| Totality belongs to function | No general new JSON loader. Reuse existing admitted model/population/step loaders. Tool arguments reject invalid repeats/workload names via argparse, exit 2. Any optional new import must first amend this spec with read caps and total loader cases. |
| Input cap does not bound algorithm | Measure instrument overhead separately; cap repeat count, fixture sizes and test wall guards. No public untrusted-algorithm path added. |
| Validation order | Baseline preserves existing public order; mutation observations do not suppress validation. T6 asserts mismatch before any speed claim. |
| One walk for all kinds | Census walks the existing family/dependency registry; every family gets eligible/ineligible/unresolved with a reason, no copied policy per family. |
| One normative prose home | Product proposal in plan §2; output meanings and IE0 experiment protocol here. Future runtime public contract belongs in API docs after approval. |
| Measurement settles representation | Direct fresh-vs-fresh controls and dirty oracle probes precede any claim about safe reuse. Missing measurements remain missing. |

## 4. Goal

Ship a credential-free measurement instrument and public controls that exit 0
when full-path results match, exit 1 when a semantic comparison fails, and exit 2
for bad invocation. Freeze the counted baseline and eligibility/dirty-component
matrix before optimization. No runtime optimization or downstream latency claim
is part of IE0.

## 5. Design

### `tools/measure_incremental_evaluation.py` (estimated 250–400 lines)

Reuse `tools/measure_transition_cost.py` replay, normalization and fixture logic
through normal Python import. Keep its existing CLI, schemas and files unchanged.
New tool imports must restore module/class descriptors and profiler hooks in
`finally`; never patch the repository on disk for a measurement.

Exact proposed tool-only Python surface:

```python
def replay_full(workload: str, *, receipts: bool) -> list[dict[str, Any]]: ...
def compare_results(expected: dict[str, Any], actual: dict[str, Any]) -> list[str]: ...
def count_work() -> ContextManager[Counter[str]]: ...
def measure_modes(workload: str, *, repeat: int) -> dict[str, Any]: ...  # (p1)
def main(argv: list[str] | None = None) -> int: ...
```

`compare_results` returns sorted mismatch labels from this vocabulary:
`payload`, `exit`, `branches`, `extensions`, `lineage`, `unavailable`, `possible`.
Missing either side's required field is a mismatch, never a successful empty
comparison. Compare canonical JSON for JSON surfaces and existing typed identity
helpers for internal exact scalars; any projection used for an internal surface
must have a discriminator proving it retains the semantic difference.
No caller-reproducible portable cache key or new product interchange is introduced.

Command contract (proposed, not currently executable):

```sh
uv run python tools/measure_incremental_evaluation.py --workload all --repeat 3 --out DIR
```

`--workload` choices: `reporter`, `course`, `localized`, `all`.
`--repeat`: integer 1 through 7; default 3. `--out`: required local output directory.
Write only to that directory and never overwrite the old milestone evidence.
Loader/evaluator operational errors produce exit 1 and a named failure in the
tool summary; argument errors exit 2. Ctrl-C propagates after cleanup.

Outputs are measurement artifacts, not a new versioned product wire:

- `environment.json`: source HEAD, dirty paths/digests for relevant source,
  tool/test/fixture/config hashes, Python/uv/platform and selected mode/order.
- `parity.json`: each call identity, explicit compared surfaces, full digests,
  exact exits, mismatch labels and unavailable comparison reasons. A required
  surface marked unavailable fails the local gate; never call that parity.
- `work.json`: per-call and aggregate counters and counter owner inventory.
- `timings.json`: separate uninstrumented samples, ordering, load/evaluation
  split, raw repetitions, median and dispersion; no asserted speedup in IE0.
- `eligibility.md`: existing family/dependency census, proposed reusable unit,
  invalidation inputs, evidence case and unresolved gaps.

Pin concrete emitted shapes in direct tool tests when implementing IE0, without
turning this diagnostic output into a portable handle. If output becomes a
public validation format, return for corpus-first approval instead.

### Counter design and liveness

Keep existing transition counters. Add actual work units:
`derivation_body_evaluations`, `join_candidates`, `constraint_evaluations`,
`fingerprint_nodes`; record the existing exact/partial work measures separately
where their meanings differ. A counter is marked unavailable until an actual
lookup owner and a liveness case are identified; unavailable mandatory body or
constraint counters block IE0-C2. Do not infer executed work from selected heads.

Discover every loaded identity alias of the defining callable, as the existing
tool does. Count nested calculator routes without double-counting the same
body/evaluator execution. For graph census, reuse existing dependencies, labelled
edges, classification and strata. Reading a graph does not prove all implicit
constraint dependencies are included: roster/reference/constraint gaps get rows.

### Controls and census (estimated 100–200 fixture lines plus provenance)

Retain `tests/fixtures/transition_cost/` unchanged. Reuse packaged course attempts
1–3 via the existing helper, including failing attempts. Add small public
`tests/fixtures/incremental_evaluation/` controls with:

1. Two independent base→derived→constraint chains; change only one base.
2. No-op, insert, delete, replacement and row-reorder snapshots.
3. A transitive dependency and recursive component with deletion of the only
   support and deletion with an alternate support.
4. Negation and aggregate changes that change an output even when a positive
   body relation is unchanged.
5. Derived rows whose values remain equal but whose origin positions change.
6. Exact unavailable and partial/opaque cases, with available↔unavailable changes.
7. Object roster change affecting a mandatory constraint; reference/options
   changes and marker invalidation as boundary scenarios.

Use existing validated syntax and minimal model fragments. Each story names its
expected fresh behavior. At this phase all evaluations are full; the desired
future dirty sets are data/expectations, not implemented invalidation.

Produce one census row per supported family/route, with evidence or `unresolved`.
Do not claim complete incremental eligibility from a valid schema or successful
full check. Probe the receipt-report mutation allegation on fresh objects,
record the observed consequence and leave the fix to IE3. Never mutate the
baseline report used as the parity oracle.

### Baseline and experiment, declared before execution

**Timing schedule (p1, R4-F1):** run three named arms in a single interpreter
and environment: A = full stateless, B = receipt-only, C = a second independent
fresh full control. Each arm loads its own model/populations; no receipt or
evaluation state crosses arms or rounds. Future incremental slots are not called
warm hits before they exist. One unmeasured warm-up per arm. `--repeat N` means
N measured rounds, with one complete replay of every arm in each round. For
zero-based round i, use rotation `(ABC, BCA, CAB)[i % 3]`; the default N=3 runs
ABC / BCA / CAB, yielding three samples per arm. The same prefix/repetition rule
applies for every accepted N=1..7; report positional imbalance for N not divisible
by three. Never omit an arm. Counting/profiling and normal wall timing are
separate runs. Report parsing/loading separately from evaluation and report the
complete public-call total as well.

The old replay denominator is exactly 13 public calls: 7 checks and 6 one-step
transitions. Historical counts are 25 checker runs without receipts, 19 with
receipts; verify fresh rather than assume. The course denominator is the named
attempt and its complete walk, not an arbitrary subset of passing steps.
Record body/evaluator work by call and totals; no timing gate and no ratio
formed from profiles. A changed fixture, interpreter or relevant source identity
requires rebaselining before an optimization comparison.

Use existing 600-second per-test hang-guard precedent; a guard firing is a failed
run, not a performance verdict. Run serially. With the default 3 rounds, cap the
measurement invocation at 30 minutes; incomplete modes retain failure/partial
status and cannot supply baseline acceptance. Do not increase the bound silently.

This experiment measures framework evaluation only. It cannot establish SQL
cost, all-547 runtime, sample/full-data scaling or downstream timeouts. The newly
offered bundle remains absent; no private filesystem search is authorized to
find it. IE0 outputs an implementation estimate/risk breakdown for owner scheduling,
with exact reporter-work targets and unresolved eligibility gaps. No calendar
date or target is retrofitted from a favorable run.

## 6. Decisions — all open

| ID | Question / recommended reading | Alternatives and cost |
|---|---|---|
| D1 | Approve prose as IE0 instrument (plan D9)? | Corpus-first would require a separate approved RED answer key before diagnostic tool code; prose keeps IE0 as measurement-only, with oracle negative controls mandatory. |
| D2 | Use old public workload and synthetic controls while new bundle is absent (plan D3)? | Waiting blocks baseline work; proceeding cannot claim new-workload acceptance. |
| D3 | Accept exact counted targets frozen after IE0 census, with any infeasible target returned for amendment (plan D7)? | Inventing a universal speed factor now has no evidence; weakening it after optimization would invalidate the experiment. |
| D4 | Accept repeat/hang/measurement bounds above? | Larger runs cost time, smaller runs reduce timing information; none alter semantic gates. |
| D5 | Keep scheduling decision after IE0 estimate (plan D5)? | A committed date now lacks a measured dependency/eligibility basis. |

No rows have owner marks, dates or artifact approval hashes yet. Plan D1/D2,
D4/D6/D8 remain their plan/later-phase decisions; this spec does not approve them.

## 7. Tests and verification-selection ledger

Proposed direct file: `tests/test_incremental_baseline.py` (250–400 lines).

| Test | Case and expected result | Criterion |
|---|---|---|
| T1 `test_fixture_identity_and_public_provenance` | Existing fixture hashes unchanged; synthetic rows have provenance and admitted shapes; pytest exit 0 | C1 / privacy |
| T2 `test_full_replay_parity_and_denominators` | Fresh-vs-fresh complete parity, 13 calls and verified 25/19 checker counts; course passing/failing exits retained; pytest exit 0 | C1/C4 |
| T3 `test_derivation_counter_liveness` | Known nonempty bodies positive, no-derived control zero; deliberately disable counting and test fails, pytest exit 1 for mutant | C2 |
| T4 `test_constraint_and_alias_counter_liveness` | Direct and imported alias evaluator calls counted; no duplicated events; disabling one lookup owner or increment causes exit 1 | C2 |
| T5 `test_census_has_discriminating_stories` | All seven story groups admitted; polarity/recursive/roster dependencies and gaps explicit; pytest exit 0 | C3 |
| T6 `test_oracle_rejects_corruption` | Independent changes to exit, payload, branch, extension, lineage, unavailable and possible state each produce the matching nonempty label; missing surfaces fail; CLI comparison failure exit 1 | C3 |
| T7 `test_instrument_cleanup_and_timing_order` | Exception restores profiler/descriptors/aliases; for every N=1..7 assert all A/B/C arms, exactly N samples per arm, rotations from the schedule, independent loaded inputs and absence of instrumentation in timing; invalid repeats/workload exit 2 (p1) | C2 |
| T8 `test_receipt_report_mutation_probe` | Reproduce or refute alleged behavior with fresh controls and record outcome; cannot call a failed probe a pass; no production fix | C3 |
| T9 `test_baseline_evidence_completeness` | Source/config/fixture/tool identities and actual counters present, target denominator frozen, missing input labeled, no unsupported result claims; deleting required identity/counter causes exit 1 | C4 |

Exit 0 in the test table means the pytest invocation passes; deliberately faulty
instrument outcomes are isolated negative controls, not a deliberately red gate.
The harness itself must fail when its oracle or a mandatory counter is inert.

| Obligation | Disposition | Command / expected exit | Input boundary | Justification / invalidation |
|---|---|---|---|---|
| IE0 direct tool/control tests and old fixture compatibility | run after approval/implementation | `uv run pytest -q tests/test_incremental_baseline.py tests/test_transition_cost_workload.py` → 0 | tool, tests, fixtures, runtime, pytest configuration and interpreter | Exercises tool consumers; any relevant change reruns it |
| Formatting of new Python files | run after implementation | `uv run ruff check tools/measure_incremental_evaluation.py tests/test_incremental_baseline.py` → 0 | new Python files and lint config | bounded static check; no production lint sweep |
| Baseline evidence | run after direct controls | `uv run python tools/measure_incremental_evaluation.py --workload all --repeat 3 --out .gnd-planning/milestones/incremental-evaluation/evidence/IE0` → 0 | all measured source/config/tool/fixture/interpreter bytes | zero parity mismatches; live counters; exact denominators; no speed claim |
| Production behavior/policy pins | cadence for changed production contracts | IE1–IE5 affected RF4/RF6/RF7/RF9 and layering gates, exact selection in their specs | runtime definitions, exports, registries, layer map | IE0 changes no runtime; any such edit here refutes scope and returns for amendment rather than waiving the gates |
| Historical full suite | cadence, explicit owner/CI selection only | `uv run pytest -q` | whole repo/environment | No broad result inherited or claimed; tool-only impact is bounded above |
| Native/provider/certification | not selected; outside scope | none | external/paid/reserved inputs | No old certificate applied to new bytes |

No `inherit` pass rows: prior records motivate choices but do not verify this tool.
Maintain pytest's default lane exclusions. The new tool and tests do not exist
yet; the commands above are concrete execution contracts, not passing results.

## 8. Out of scope for IE0

Runtime edits, new public session API, cache/invalidation implementation,
receipt fixes, changed session schemas, paid/provider review, private bundle
imports, downstream census, native lanes and certification. Later phase outlines
do not authorize writing their code in IE0.

## 9. Size

Estimated tool 250–400 lines, direct tests 250–400, fixture/provenance 100–200;
runtime lines **0**. Census and measurement artifact size depend on actual route
count, recorded at execution. Growth beyond estimates is disclosed in the record.

## 10. Approval instrument and readiness

Proposed: prose plus the discriminator stories and negative-control test list.
IE0 does not add a product format/validation predicate; its output is an internal
measurement artifact and its comparator has explicit dirty controls. That is
the reason for proposing the prose exception to corpus-first; the owner must
rule on D1, not infer consent from this draft. If the deliverable expands into
a product wire contract, corpus-first is reconsidered before code.

Inputs for local IE0 exist and source homes support instrumentation; no promise
of incremental reuse is needed for its baseline. Missing review/approval and
D1–D5 prevent execution readiness. No spec review panel has been selected.
After approval, commit this exact approved spec separately before implementation;
append findings and amendments with their approvals rather than rewriting history.

## Delegated gate — 2026-10-19 (a1)

Delegated approval (`auto=true`) under the owner's invocation
`process-milestone incremental-evaluation auto`. D1–D5 accepted as proposed:
prose instrument; public/synthetic inputs; targets frozen before optimization;
1..7 rounds, 600-second test guard and 30-minute measurement bound; scheduling
after IE0 evidence. Optional per-spec panel omitted. Required independent phase
diff review uses the installed Codex CLI read-only harness on stdin, xhigh effort,
with its configured default model; plan/close retain four selected local agents.
No paid provider panel, broad suites, native/certification, merge or publication.

Implementability sweep: existing driver supplies replay/paths; profile code-event
observation can count actual body/constraint execution without runtime edits;
existing typed semantic views can supply the differential envelope. All stories
have reachable current fixture syntax. Any missing mandatory counter or envelope
remains a failed gate, not a zero. Commit this spec before implementation.
