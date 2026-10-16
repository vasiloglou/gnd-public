# Per-step transition and check cost

Draft r2, 2026-10-16. Milestone: `transition-check-performance`.
Source: [gnd-public issue #24](https://github.com/vasiloglou/gnd-public/issues/24).
Inspection baseline: `73ea302`. Planning only. Plan review, plan approval,
phase execution, implementation and publication have not occurred.

**r2 (o):** the owner relayed rulings from a conference with the issue's
reporter on 2026-10-16: TP-D1 (a), TP-D2 (the reporter's exact workload files),
TP-D3 (opt-in and receipt-bound), and TP-D4 (deferred). GR-1 to GR-3 have been
located. Sentences changed by r2 carry `(o)`. Rulings on individual decisions
are not approval of the plan.

## Problem and completion predicates

Issue #24 reports that a downstream application's imperative plan execution spends more
than 95% of its wall time in GND checks and transitions. The SQL takes about
1 ms per step. The report pinned GND `8a3a98ba`. A 5-step program on the
packaged `expense` example takes about 4.6 s unprofiled. Under cProfile it ran
25 `checker._core.check` runs, 535 `ModelIndex.for_model` calls (4.5 s
cumulative), 2.7 M `copy.deepcopy` calls (2.0 s), and 5.8 s re-deriving
extensions in `correspond_snapshot`/`adapt_snapshot_observed`. The reporter's
reproduction is in uncommitted downstream code. Its numbers are **external
evidence**, not a measurement performed during planning.

Inspection of current bytes (read-only, no runtime executed):

- `git diff 8a3a98b..73ea302` touches no hotspot file except
  `src/gnd/model_index.py` (+6 lines, a static `constraint_roles` helper). The
  profile's code paths are unchanged.
- `src/gnd/model_index.py:ModelIndex.for_model` runs `model.model_dump()`,
  walks every container, and hashes canonical JSON on **every** call before it
  consults the 32-entry cache. A hit costs the same as computing the key.
- `src/gnd/population.py:Population.matches_validation_marker` re-derives (via `gnd.values.model_digest`)
  `_model_digest(model)` and `_content_digest(population)` on every check. This
  is the deliberate CR-01 guarantee: `Model` is `frozen=True` but its nested
  dicts and lists remain mutable (`src/gnd/documents.py:21-24`), so object
  identity alone cannot detect a mutation.
- `src/gnd/transition.py:_evaluate_to_state` runs a full `check(model, pre)`.
  Every loadable intermediate state gets its own full `check`.
  `evaluate_plan` adds one more full check on the computed post.
  `evaluate` checks the declared post instead. A walk of n steps therefore
  costs n + 2 full checks.
- `ModelIndex.__post_init__` and its query properties `deepcopy` the document
  to hand back detached values. `transition.py` deep-copies operations,
  obligations and states at 8 sites.
- The `analytics-m3-repairs` milestone (phases 8–13, merged in PR #20) already
  shared preparation inside one call. Its phase-13 record says "No
  report/verdict/crosscall cache" and "Root admission and full
  intermediate/post checks remain mandatory". That ruling applied to M3's own
  scope. Requests 3 and 4 below cross it, so they need a fresh owner ruling
  (TP-D3, TP-D4). M3 itself remains open and owns its own gates.

**Proposed outcome:** the same reports, byte for byte, at a much lower counted
cost per check and per transition step. The milestone ships three things in
order:

1. Cheap `ModelIndex` hits that keep CR-01's guarantee: a mutated model
   never reuses a stale index.
2. Fewer deep copies of inputs that no code path mutates.
3. Opt-in reuse of an already-checked pre-state. It needs a semantic ruling
   and an unforgeable, GND-minted check receipt (o).

Incremental (dependency-indexed) evaluation is **deferred** to a successor
milestone (o, TP-D4). The reporter says its own caller-side speedups remove
most of the pressure.

The milestone can close when:

1. A portable in-repo workload reproduces the issue's shape on current bytes:
   a multi-step plan over a packaged example. Its baseline pins counted work
   (checker runs, `for_model` key computations, deep copies), wall-time
   medians (informational) and normalized report digests.
2. On that workload, every default-path public report (`api.check`,
   `api.transition` with and without `post`, CLI `check`/`transition`, batch
   `--populations`) is byte-identical to the baseline after each phase.
3. `for_model` key computations per public call are bounded by an approved
   constant, not by the number of internal lookups. A model mutated between
   calls still gets a fresh index and still fails the population marker.
4. The deep copies that were removed are proven safe by a mutation-guard test
   for each site. Detached-value contracts on public queries keep their tests.
5. (o) A transition given a valid check receipt for its exact pre-state runs
   one fewer full check and produces a report identical to the run without a
   receipt. Post-state checks stay mandatory. Forged, stale, mutated or
   other-model receipts are refused with a named
   error before evaluation.
6. Counted-work reductions meet the targets approved at TP0. Wall-time results
   are reported with their limits and are not the acceptance gate (TP-R4).
7. Focused gates, independent diff review, docs for any new public surface,
   and the milestone question sweep are recorded. A PR is submitted, and owner
   acceptance is recorded separately.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| TP-R1: Same answers | Default-path reports, verdicts, band precedence, branch traces and exit codes stay byte-identical, proven by digest parity on the TP0 workload and existing contract tests. A speedup that changes a report is a semantic change and needs its own ruling. |
| TP-R2: CR-01 stays intact | Cache hits must not let a mutated model or population reuse a stale index, extension or verdict. Mutation of nested model or population content, by any route, still invalidates. A memo keyed on object identity alone is refused unless TP-D1 approves a freezing design that makes identity sufficient. |
| TP-R3: Explicit opt-in for reuse | (o) Any skipped pre-state re-check needs an explicit caller action and a check receipt whose digests match that exact model and pre-state. The receipt must be **minted by GND**. A bare digest is not enough, because any caller can compute one for a state GND never checked. GND never trusts caller-supplied report JSON as proof of a check. Only the pre-state check may be skipped: intermediate and post checks stay mandatory, and defaults keep n + 2 full checks. |
| TP-R4: Counted work gates, wall time informs | Gates assert deterministic counters (checker runs, key computations, deep copies, extension derivations). Wall-time medians are recorded with machine, interpreter and repetition count as evidence only. No gate depends on timing (cf. `tests/test_guarded_timing_batches.py` practice). |
| TP-R5: One home per cache | Each memo has one defining home, one invalidation rule and a bounded size. No per-module ad hoc caches. Follow `tools/gnd_layers.json` (zero allowances) and the ModelIndex policy in AGENTS.md. |
| TP-R6: Approval and evidence | `auto=false`. Plan authorship is not implementation approval. Preserve existing records and M3 evidence. No inherited certification. |

Each phase spec also names, or argues inapplicable, every paid-for rule in
`.codex/skills/process-phase/references/standing-rules.md`. Rule 2
(algorithmic bounds) applies directly: every new memo needs a size bound and a
time-bound test over its layer. Rule 6 (decide by measurement) governs every
contested "is this copy needed" question.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issue #24 body (2026-10, pinned GND `8a3a98ba`) | Problem, profile, requests 1–4, caller-side plans |
| `src/gnd/model_index.py`, `population.py`, `documents.py`, `transition.py`, `api.py`, `checker/_core.py`, `correspondence.py`, `semantic_adapter.py` | Feasibility and hotspot homes |
| `analytics-m3-repairs/008`–`013` records | Prior same-call preparation sharing and its boundaries |
| `code-refactoring` RF6 (ModelIndex/query layer) and RF9 records | Query-layer policy, shim inventory, layer map |
| `compiled-snapshot-obligations` close | `compiled_operations` check mode that must stay consistent |
| AGENTS.md, CONTRIBUTING.md | PR, layering, ModelIndex and family dispatch rules |

This is a framework performance milestone, not a domain model. A
`gnd coverage MODEL` census measures experiment claims, not runtime cost, so it
would not decide this scope. The caller-side changes listed in the issue
(one whole-program transition, model loaded once, parallel processes) belong
to the downstream application and are out of scope here. (o) Requests GR-1 to
GR-3 are recorded in the reporter's own roadmap, not in this repository. GR-1 covers counts and
observed facts in transition-session feedback. GR-2 is a host hook that adds
observed facts between attempts. GR-3 is a configurable agent-call timeout in
session versions 7 and 8. None of them is in this milestone's scope. GR-1 and
GR-2 go with deferred request 4. GR-3 is unrelated to performance.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Reproducible baseline on current bytes (issue "Reproduction"; external numbers only) | proposed target | TP0 |
| O2 | Request 1: cheap `ModelIndex.for_model` hits (issue §Requests 1) | requested | TP1 |
| O3 | CR-01 mutation invalidation (`population.py:167-190`, `documents.py:21-24`) | inherited constraint | TP1, TP2, TP3 |
| O4 | Request 2: avoid deep copies of immutable inputs (issue §Requests 2) | requested | TP2 |
| O5 | ModelIndex detached-value query contract (`model_index.py` docstring) | inherited constraint | TP2 |
| O6 | Request 3: transition without full pre re-check (issue §Requests 3) | requested, needs ruling | TP3 |
| O7 | M3 "no cross-call cache / full checks mandatory" boundary (`analytics-m3-repairs/013`) | inherited, M3-scoped | TP-D3 ruling, TP3 |
| O8 | Request 4: incremental evaluation / session object; GR-1/GR-2 overlap (issue §Requests 4; reporter's roadmap) | (o) deferred by TP-D4 | close carryover to successor milestone |
| O9 | Report parity across all public surfaces | cross-cutting gate | every phase |
| O10 | Layer map zero allowances, shim inventory, ModelIndex/family policy (AGENTS.md) | cross-cutting | every phase |
| O11 | Docs for any new public surface (`docs/reference/python-api.md`, `docs/reference/capabilities.md`) | cross-cutting | TP3 |
| O12 | `compiled_operations` and admission modes remain consistent (CS close) | inherited | TP1–TP3 parity cases |
| O13 | Downstream application acceptance | carried | the reporter, after merge |

## 2. Contract proposal and product behavior

**Defaults stay the same.** Every public entry point returns the same payload
for the same inputs. Only counted internal work changes.

**TP1 (cheap index hits):** the design approved by TP-D1 (o) computes the
model content digest once per public call and threads it through, instead of
once per internal lookup. `matches_validation_marker` already computes
`_model_digest(model)` at check entry. Reusing a single per-call key removes the
other ~500 recomputations without weakening mutation detection between calls.
The alternative is to deep-freeze nested model content at load so that identity
becomes sound. That is cheaper per call, but it changes the type of every nested
container callers can read, so it is a compatibility change.

**TP2 (copies):** remove a `deepcopy` only where the input is never mutated
downstream, or where it is a frozen value that GND owns. The query-facing
detached-value contract stays.

**TP3 (checked-state reuse):** TP-D3 approves an opt-in that is bound to a
receipt (o). The proposed surface, subject to TP-D5, is a new keyword-only
option on `api.transition`. It takes a check receipt that GND mints in-process
when a check completes. The receipt binds the
model object, the model digest, the population content digest and the
check-mode options. If the receipt validates, the pre-state report is reused.
Otherwise `api.transition` raises a named refusal before evaluation. The receipt
is not serializable and not a JSON field. The CLI gets no equivalent unless the
owner asks for one.

**TP4 (incremental):** deferred (o, TP-D4). The phase ID is reserved and
not executed in this milestone.

## 3. Dependencies and artifact homes

(o) TP0 → TP1 → TP2 → TP3 → close. TP1 and TP2 are independent after TP0
and may swap order, because both only reduce internal work. TP3 needs TP0's
parity harness, and its counted gate is measured after TP1–TP2.

TP0 also waits on an input: the reporter has offered the exact
profiled workload files (TP-D2). TP0 implementation cannot start until they
arrive.

No phase depends on optional provider review, downstream execution, publication
or certification. The supplied files are input only. They are committed into
this repository with their source revision and SHA-256 recorded, so that
development and CI stay portable.

| Artifact | Home |
|---|---|
| Plan, specs, records | `.gnd-planning/milestones/transition-check-performance/` |
| Workload fixture | (o) `tests/fixtures/transition_cost/`: the reporter's generated steps metamodel `steps.orm.json` (rendered against the packaged `expense` data), its state populations, the step documents, and the driver script, which calls only `gnd.api`. All of it is built from packaged example data. The fixture keeps a provenance note with the source revision and file digests. The packaged `src/gnd/examples/plan_apps/course` plan stays as a small control. |
| Counter/measurement tool | `tools/measure_transition_cost.py` (proposed, TP0) |
| Baseline and per-phase measurements | `evidence/` of this milestone |
| Runtime changes | actual defining homes: `model_index.py`, `population.py`, `transition.py`, `checker/_core.py`, `api.py` |

## 4. Phases

### TP0: Portable workload, counters and parity baseline

Spec: [phase-TP0-spec.md](phase-TP0-spec.md) (draft, awaiting owner review).

- TP0-C1: (o) the reporter's exact profiled workload (5-step SUM program and,
  if supplied, a 12-step program), imported with recorded provenance,
  exercised through `api.check`, `api.transition` (with and without post) and
  batch check.
- TP0-C2: deterministic counters for full checker runs, `for_model` calls and
  key computations, `deepcopy` calls on GND homes, and extension derivations,
  collected without changing runtime code paths.
- TP0-C3: normalized report digests for every surface, used as the parity
  oracle by TP1–TP3.
- TP0-C4: baseline evidence (counters, digests, 5-run wall medians with
  machine/interpreter) and a statement of how the workload's shape compares
  with the issue's profile (25 checker runs, 535 `for_model` calls). Because the
  files are the profiled ones, a large mismatch points to a measurement or
  environment difference. It is recorded and goes back to the owner.
- TP0-C5: owner ruling on counted targets (TP-D6). TP-D1 and TP-D2 were ruled in r2 (o).

### TP1: Cheap ModelIndex hits under CR-01

- TP1-C1: `for_model` key computations per public `check` and per transition
  step are bounded by the TP-D6 constant (proposed: ≤ 1 per public call plus
  ≤ 1 per loaded intermediate population).
- TP1-C2: nested mutation of a model between two calls yields a new index and
  fails `matches_validation_marker`. The test fails on a mutant that keys
  on identity only.
- TP1-C3: the cache stays bounded (`_LIMIT`). A time-bound test covers the
  key path.
- TP1-C4: report parity on all TP0 surfaces, plus existing ModelIndex, RF6 and
  layering tests.

### TP2: Remove deep copies of immutable inputs

- TP2-C1: a written inventory of every `deepcopy` reached by the TP0
  workload, with a keep/remove ruling for each site and its reason.
- TP2-C2: every removed site has a guard test that mutates the would-be-shared
  value downstream and proves the caller's input is unchanged (or proves the
  value is a frozen value GND owns).
- TP2-C3: public detached-value tests (`tests/test_public_transition_ir_immutability.py`
  and the ModelIndex query tests) still pass unchanged.
- TP2-C4: counted deep-copy reduction meets TP-D6, with report parity.

### TP3: Opt-in, receipt-bound pre-state reuse (TP-D3 ruled (o); TP-D5 open)

- TP3-C1: the receipt is minted only when a GND check completes, and binds the model
  object, model digest, population digest and check options.
- TP3-C2: a valid receipt removes exactly one full checker run (the pre-state)
  per transition. Intermediate and post checks still run. The report is
  byte-identical to the run without a receipt on every TP0 transition
  case, including `compiled_operations`, reference populations and dynamic heads.
- TP3-C3: refusal cases each raise their own named error before evaluation:
  wrong model object, mutated model, mutated population, different check
  options, a foreign object, a forged or self-computed digest, and a receipt from a failed check
  (TP-D5 decides whether a failing pre-check may be reused).
- TP3-C4: `docs/reference/python-api.md` and `capabilities.md` document the
  opt-in, its preconditions and its non-goals.

### TP4: Incremental evaluation (deferred (o), TP-D4)

Not executed in this milestone. The close record hands request 4, GR-1 and
GR-2 to a successor milestone. That milestone's planning must reconcile the M3
selective-refresh path (`structured_extension_view(previous=…, refresh=…)`)
with CR-01.

### Milestone close (not a feature phase)

Final parity and counter evidence on current bytes, the four-reader close bar
(see §8), the open-questions sweep, carryovers (O8 to a successor milestone,
O13 to the reporter), and
a PR. Merge and acceptance remain separate owner actions.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1 | TP0-C1..C4 |
| O2 | TP1-C1, C3 |
| O3 | TP1-C2, TP2-C2, TP3-C3 |
| O4 | TP2-C1..C4 |
| O5 | TP2-C3 |
| O6 | TP3-C1..C3 |
| O7 | TP-D3 ruled 2026-10-16 (o); TP3 spec records it |
| O8 | close carryover (deferred by TP-D4) |
| O9 | TP1-C4, TP2-C4, TP3-C2, close |
| O10 | every phase spec §4 and the layering test |
| O11 | TP3-C4 |
| O12 | parity cases in TP0-C3 include `compiled_operations` and admission |
| O13 | close carryover table |

## 5. Documentation, skill and compatibility surfaces

- TP1 and TP2 have no public surface change and need no docs, except a release
  note line at close.
- TP3 adds one public keyword (and possibly one public receipt type). Docs:
  `docs/reference/python-api.md`, `docs/reference/capabilities.md`, a
  release note, and the `test_public_api` / public-reference-signature pins.
- Packaged skills are unaffected unless TP3 changes what `gnd-dev-session`
  documents about transition sessions. The TP3 spec checks this.
- Compatibility: if TP-D1 picks deep-freezing, nested model containers stop
  being plain `dict`/`list`. That is a compatibility break that needs a
  `docs/compatibility.md` entry and its own owner ruling.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A stale cache hit returns a wrong verdict after mutation (CR-01 regression) | TP1-C2 mutant test; TP-R2 |
| A removed copy lets a caller's input be mutated by evaluation | TP2-C2 per-site guard tests |
| Reuse receipt forged, self-computed or replayed against different content | TP3-C3 refusals; the receipt is GND-minted, in-process and digest-bound |
| Workload unrepresentative of the downstream application; speedups don't transfer | TP0-C4 shape comparison; O13 app acceptance carried |
| Timing noise read as improvement or regression | TP-R4: counters gate, timings inform |
| Memo growth in long-running callers | bounded caches with time-bound tests (standing rule 2) |
| Parity oracle too narrow: digest normalization hides a real change | TP0 spec states normalization fields explicitly; branch traces included |
| Repair rounds introduce new defects | standing rule: re-review neighbours of each repair |

## 7. Out of scope

- The downstream application's caller-side changes and its parallelism.
- Changing verdict semantics, constraint families, band precedence, or the
  default n + 2 check count.
- Cross-process or on-disk caches, and any serialized "already checked" proof.
- Closing or changing `analytics-m3-repairs` gates.
- Native/LQP/PyRel runtime performance.
- Publication, release, and certification.
- Incremental evaluation, session objects, GR-1 to GR-3 (deferred, TP-D4 (o)).

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, then the owner gate,
then implementation with focused tests, independent review, refactoring review
and record. No code is written before the recorded spec approval. Plan review
and milestone close keep the repository's four-reviewer bar
(`process-phase/references/review-convergence.md`). The review instrument
(maintained panel or named local readers) is selected explicitly by the owner
(TP-D7). One reviewer is one reviewer. Work happens on a topic branch, followed
by a PR. Merge only on explicit owner authorization.

## 9. Per-phase verification story

| Phase | Expected result | Affected consumers / tests |
|---|---|---|
| TP0 | Workload runs; baseline counters, digests and timings retained; no runtime diff | new workload test; `tools/` measurement script |
| TP1 | Key computations drop to the TP-D6 bound; parity holds; mutation invalidates | `tests/test_rf*` ModelIndex pins, `test_popvalidate.py`, `test_public_transition_contract.py`, `test_rf1_layering.py` |
| TP2 | Deep copies drop to target; parity; guard tests | `test_public_transition_ir_immutability.py`, M3 preparation tests |
| TP3 | One fewer full check with a receipt; refusals named; docs | `test_public_api.py`, `test_public_reference_signatures.py`, transition contract/trace tests |

Exact focused gate commands are **unresolved** until each phase spec names
them. The broad suite (`uv run pytest -q`) runs on explicit owner selection.

## 10. Owner decisions and open questions

Rulings marked (o) were relayed by the owner on 2026-10-16, after a
conference with the issue's reporter. The rest are proposed. A ruling on a
decision is not approval of the plan.

| ID | Question | Ruling or readings |
|---|---|---|
| TP-D1 | How do `ModelIndex` hits become cheap without breaking CR-01? | **Ruled (o): (a)**, one key per public call, threaded through. The reporter confirms that most of its cost is recomputation inside each call (535 calls across 25 checker runs). Rejected: (b) deep-freeze (a compatibility break) and (c) identity plus version counter (nested mutation can't be enforced). |
| TP-D2 | Which workload forms the parity oracle? | **Ruled (o):** the reporter's exact profiled files (`steps.orm.json`, state populations, step documents, a driver that calls only `gnd.api`), committed with provenance, plus `plan_apps/course` as a control. Pending: the files themselves. |
| TP-D3 | May a transition skip the full pre-state check? | **Ruled (o): yes, opt-in and receipt-bound.** The check is skipped only when the caller presents a check receipt whose digest matches that exact state. Full checks stay the default, and post checks stay mandatory. This supersedes the M3-scoped boundary for this opt-in only. Plan constraint (TP-R3): the receipt must be GND-minted, not a bare digest. |
| TP-D4 | Is incremental evaluation in this milestone? | **Ruled (o): deferred** to a successor milestone, together with GR-1 and GR-2. |
| TP-D5 | Receipt details | Open. (i) Minting surface: changing `api.check`'s dict return type breaks callers, while a separate function or a keyword that returns `(payload, receipt)` does not. (ii) Can a receipt from a failing pre-check be reused? The report is the same, but the trust surface is wider. (iii) Form: an in-process opaque object (proposed: no secret to manage, not serializable) or a serializable receipt with a GND-held MAC (works across processes, which the reporter's parallel processes might want, but needs key management). |
| TP-D6 | Counted targets per phase | Proposed: TP1 ≤ 1 key computation per public call (+1 per loaded intermediate); TP2 ≥ 50% fewer deep copies on the workload; TP3 exactly −1 checker run per transition that presents a receipt. |
| TP-D7 | Review instrument for plan, phases and close | Open: maintained `gnd-review-panel` (provider cost) vs named local readers (as in the CS and PL milestones). |

Open question: whether the issue's 535 `for_model` calls include calls made
from the caller side (TP0-C4 measures the GND side only).
