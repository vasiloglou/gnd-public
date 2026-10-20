# Incremental evaluation

r2 (p1), 2026-10-19. **Owner-approved, 2026-10-19.**
Approval-status annotation (o): [plan gate](../001-plan-gate.md) binds the exact
pre-annotation r2 bytes and records D1–D9. It supersedes the pending-plan-approval
and proposed-decision status statements retained below as drafting history;
IE0's concrete spec gate remains pending. No implementation delegation.
Review instrument selected by the owner: four local reviewer agents (D6).
Four-reader review of r1 is complete: three approve, one approve-with-fixes,
no blockers. [Disposition](plan-review-r1-disposition.md) binds opinions to
the retained r1 bytes. The status correction in r2 and supporting IE0 timing
repair carry no new review opinion; no second round was selected.
Milestone: `incremental-evaluation`. `auto=false`.
Inspection baseline: `058874965c54c19c4a4c34855cc9ca1b789394bf` on
`codex/issue-24`, which includes the fetched `origin/main` and the existing
LinkedIn-video work. That unrelated work is not part of this milestone.

## Goal, status and completion predicates

Let a caller check a sequence of related populations without recalculating
every unaffected derivation and constraint after each change. Preserve the full
check's answers, witnesses, refusal precedence and registered branch set.
The first implementation recomputes affected dependency components in full;
it does not promise work proportional only to the number of added rows.

Planning and the first four-reader plan review are complete, not execution.
The first phase's [draft spec](phase-IE0-spec.md) needs owner decisions and
approval; plan approval also remains pending. No implementation, benchmark or
owner approval is claimed by this document.
The new reporter bundle is offered but not supplied. Existing public fixtures
allow IE0 to proceed after its gate; new-workload acceptance remains conditional.

Completion requires:

1. IE0 records a fresh baseline and a falsifiable differential oracle on the
   old issue workload, the packaged course control and localized-change walks.
2. IE1 demonstrates conservative change detection, dependency closure and
   invalidation; unsupported reuse always computes fresh or refuses explicitly.
3. IE2 and IE3 reuse unaffected extensions and constraint evaluations through
   an explicit in-process session, including across `check` and `transition`.
   Every eligible incremental result matches an uncached full evaluation.
4. On a two-independent-component control, changing one component executes
   no derivation bodies or constraint evaluators exclusive to the other;
   a no-op executes neither. On the old reporter replay, actual derivation-body
   work is strictly lower than full evaluation with receipts. IE0 sets and
   freezes the exact denominator before optimization. If the dependency graph
   makes this impossible, return for scope/target amendment, not a green fallback.
5. IE4 supplies a host observation boundary and bounded counts/observations
   feedback, with reproducible attempt ordering and no unverified fact injection.
6. IE5 demonstrates check → transition → observed check → next transition,
   full-path parity, invalidation and bounded lifetime, then documents measured
   gains and fallback rates. Timings inform; counted work and parity gate.
7. Every phase has approval, focused checks, independent diff review,
   refactoring review and a record. Close has four-reviewer evidence, a complete
   question sweep, a PR and separately recorded owner acceptance.

No target delivery date is committed. IE0 supplies the measured dependency
shape, implementation risks and an estimate for an owner scheduling decision.
The 547-program census is a downstream acceptance claim, not an implied local gate.

## 0. Binding design rules

| ID | Rule |
|---|---|
| IE-R1 | Full evaluation is the oracle. Compare complete normalized payloads, exits, ordered verdicts/witnesses, extension availability/possibility and branch sets. Only existing top-level path normalization is allowed. New counters live outside the report. |
| IE-R2 | CR-01 survives across calls. Verify current model content including operations, population content/marker, options and reference identities before reuse. Caller-supplied changed IDs or object identity alone are insufficient. Any unresolved dependency is dirty. |
| IE-R3 | Admission precedes reuse. Root validation, intermediate/post checks, transition frame/compiled-operation obligations and refusal precedence remain mandatory. Incremental evaluation implements those checks; it does not waive them. TP3's explicit pre-receipt skip remains its separate contract. |
| IE-R4 | One session owns one model binding and one committed evaluation generation. Keep private detached state, including lineage, unavailable/possible relations, reports and per-unit branch evidence. Publish a new generation atomically after completion; exceptions and cancellation cannot poison it. |
| IE-R5 | Count actual work at actual lookup owners; distinguish attempted, reused, recomputed and fallback work. Instrumentation has positive and negative controls. Wall measurements are uninstrumented, interleaved on one environment, and never compared across machines as a speedup. |
| IE-R6 | Reuse existing dependency edges/strata, ModelIndex and family registration. Extension computation stays below checker; session orchestration stays above it. Keep layer allowances zero, explicit shim identities and source-scan coverage. No second partial family-dispatch policy. |
| IE-R7 | Opt-in only. Existing API/CLI/batch/experiment-session defaults retain behavior. Receipts and evaluation sessions are in-process and not portable evidence. An evaluation session is distinct from a persistent `gnd exp` session. |
| IE-R8 | Bound retained state and work. Proposed defaults: one prior generation, 100,000 retained fact rows and 32 MiB of canonical cache content, no global history. Exceeding a cache bound computes fresh and retains no oversized state; exceeding an existing evaluation limit keeps the existing refusal. Pin exact accounting in IE1/IE2 specs. |
| IE-R9 | Follow all six paid-for standing rules in the process-phase reference: total boundaries, layer time bounds, validation order, one policy walk, one prose home and measurement of contested runtime facts. Each spec binds them explicitly. |
| IE-R10 | Owner gates and privacy remain binding. Commit approved specs before implementation, keep downstream identities/private material out, do not use repository credentials or reserved/native lanes, and do not claim release or certification. |

These are proposed milestone rules. Existing repository and prior approved
compatibility obligations apply independently of their approval here.

## 1. Scope, sources and authority

This is framework runtime work. A `gnd coverage MODEL` census enumerates
experiment claims; it cannot establish evaluator dependency completeness,
cross-call reuse safety or performance, and does not settle this scope.

| Source | Authority / use |
|---|---|
| [Issue #24](https://github.com/vasiloglou/gnd-public/issues/24), request 4 and reproduction | Requested dependency-indexed incremental evaluation or a stateful session |
| [New comment](https://github.com/vasiloglou/gnd-public/issues/24#issuecomment-6282368611) | Reporter observations: 599 s sampled vs 595 s full, 10–60-step programs and about five hours for 547 programs; not reproduced here and not proof of data-size independence generally |
| [Prior complete plan](../../transition-check-performance/notes/transition-check-performance-plan.md), §4 TP4, §10 TP-D4 | Deferred request and explicit reconciliation of selective refresh with CR-01; old TP4 remains reserved in that closed milestone |
| [Prior close](../../transition-check-performance/006-milestone-close.md), Results and Open-questions sweep | Extension cost, receipt report mutation, interleaved measurement, consumer pins and spec-before-code carryovers |
| Prior records [TP0](../../transition-check-performance/002-phase-TP0.md), [TP1](../../transition-check-performance/003-phase-TP1.md), [TP2](../../transition-check-performance/004-phase-TP2.md), [TP3](../../transition-check-performance/005-phase-TP3.md) | Existing workloads, marker/index distinctions, shared-row boundary and receipt compatibility |
| [Repairs phase 13](../../analytics-m3-repairs/013-phase-13.md), What shipped and Boundary | Same-call preparation only; no cross-call cache there; root/intermediate/post checks remain |
| `src/gnd/model/_validation.py`: `derivation_dependency_edges`, `derivation_strata`, `derivation_classifications` | Existing signed dependencies, recursive components and asserted-dependency closure |
| `src/gnd/extensions.py`: `structured_extension_view`, calculators and `effective_view`; `extension_preparation.py` | Existing selective refresh and same-call memo; not a trusted cross-call handle |
| `src/gnd/checker/_core.py`, `correspondence.py`, `semantic_adapter.py`, `constraint_families.py` | Constraint evaluation, projection, origin lineage, shared refusal and branch semantics |
| `src/gnd/api.py`, `transition.py`, `checking_service.py`, `population.py`, `model_index.py` | Public admission, receipts, transitions and mutation boundaries |
| `src/gnd/exp/session_runtime.py`, `session_eval.py`, `session_contract.py` | Existing feedback and persistent attempt contracts, distinct from the new cache lifetime |
| `AGENTS.md`, `CONTRIBUTING.md`, process-phase references; `.gnd-planning/PROJECT.md`, `.gnd-planning/open-questions.md` | Binding development rules; current question register has no incremental-evaluation decision to inherit |

### Harvested obligation ownership

| ID | Obligation and source section | Evidence class | Phase / gate |
|---|---|---|---|
| IE-O1 | Current reproducible workload and baseline (issue Reproduction; prior close Results) | required new evidence | IE0-C1..C4 |
| IE-O2 | Request 4; selective refresh reconciled with CR-01 (prior plan TP4) | carried requirement | IE1-C1..C3, IE2-C1..C3 |
| IE-O3 | Actual rule work follows changed dependencies (new comment; request 4) | proposed measurable interpretation | IE2-C4, IE3-C3, IE5-C1 |
| IE-O4 | Mutation, options, references, evidence integrity (TP1/TP3 boundaries) | inherited constraint | IE1-C2, IE3-C2, IE5-C2 |
| IE-O5 | Full root/intermediate/post checks (repairs phase 13; TP-D3) | inherited, must reconcile | IE3-C1 and D2 |
| IE-O6 | Receipt report can be edited (prior close sweep 3) | inherited reported defect, reproduce first | IE0-C3, IE3-C2 |
| IE-O7 | Counts and observed facts in feedback (prior plan §1 / O8; close sweep 1) | carried, details unresolved | IE4-C1..C3; D4 |
| IE-O8 | Host hook between attempts (same source) | carried, details unresolved | IE4-C1..C3; D4 |
| IE-O9 | Interleaved end-to-end tool (close sweep 14) | carried measurement gap | IE0-C2, IE5-C1 |
| IE-O10 | RF4/RF6/RF7/RF9 pin/policy impact closure (close sweep 13) | inherited gate correction | every runtime spec §9 selection |
| IE-O11 | Approved spec committed before code (close sweep 17) | inherited protocol correction | every phase owner gate |
| IE-O12 | Complete lineage/unavailable/possible state (extension and adapter contracts) | inspected correctness dependency | IE0-C3, IE2-C2, IE3-C1 |
| IE-O13 | Bounded cache, exception safety, no aliasing (standing rules; CR-01) | proposed controls | IE1-C3, IE2-C3, IE3-C2 |
| IE-O14 | Docs, API pins, packaging, installed paths, skill-surface census (CONTRIBUTING; new API) | cross-cutting | IE4-C3, IE5-C2..C3 |
| IE-O15 | Anonymity / no proprietary data (prior O14; owner context) | inherited constraint | IE0 import gate, all diff reviews |
| IE-O16 | New pinned workload and downstream measurement (new comment; close sweep 2) | offered input, unavailable locally | IE0 optional import; IE5 conditional result / close carryover |
| IE-O17 | Four-reviewer plan/close bar and explicit instrument (start-milestone Verify) | inherited protocol | D6; plan and close gates |
| IE-O18 | Other prior close residuals | carried limitations | residual table below; no silent closure |

## 2. Contract proposal and product behavior

**Proposed public shape, to freeze in IE3 after IE0/IE1 evidence:**
`api.EvaluationSession(model, ...)`, with `check(population, ...)`,
`transition(pre, steps, post=None, ...)`, `reset()` and `close()`.
Existing stateless functions remain the full evaluator and compatibility oracle.
Exact signatures, result ownership and error vocabulary are deliberately not
frozen before the dependency/admission work. D1 selects this opt-in direction.

The caller supplies loaded, validated snapshots. The session computes the diff
itself, including facts, objects/rosters, order-sensitive witness coordinates,
derivation claims, options and references. Full snapshot comparison remains
O(population size); this milestone does not claim constant-time admission.
An optional host change hint can only widen invalidation, never suppress it.

Dirty propagation covers positive, negative and aggregate dependencies, whole
recursive strongly connected components and transitive dependents. Recompute
the dirty component from current base facts, not by unioning new rows into old
recursive output. This handles deletion and replacement without inventing
retraction semantics. Unchanged rows still need correct current origin paths.
Constraints include implicit/domain/roster dependencies and report ordering;
incomplete classification requires fresh evaluation of the affected unit, or
the whole check when its scope is unknown.

`structured_extension_view` currently accepts prior mappings and reconstructs
some prior row lineage as empty tuples. That is useful machinery, not proof
that it can substitute for checker correspondence. IE2 must preserve or rebuild
the complete semantic envelope, including branch evidence. Exact, partial,
opaque, observer/witness and reference modes are separate eligibility cases.
Unsupported modes keep their full route and record a fallback reason out of band.

The first check is cold. A later check may reuse only matching unaffected units.
An uncheckable input does not advance the generation. Completed reports with
violations may advance only if IE1 proves their internal state complete;
that policy does not broaden TP3 receipt eligibility (only exit 0/2).
Reusing a report must not expose mutable cache internals.

The host observation hook (IE4) accepts facts through normal population
composition/validation before the next check. Feedback distinguishes asserted
observation counts from computed derivation counts and never promotes observation
to external truth. It must not inject changes during an evaluation or alter
prior persistent attempt evidence. D4 resolves wire-version and host-hook scope.

## 3. Dependencies and artifact homes

Ordered DAG: **IE0 → IE1 → IE2 → IE3 → IE4 → IE5 → close**.
Six implementation phases; milestone close is a separate gate. IE0 needs no new
private bundle. IE1 requires IE0's dependency/eligibility matrix; IE2 requires
the approved invalidation contract; IE3 requires a complete reusable envelope;
IE4 requires the public session contract; IE5 requires all direct gates.

| Artifact | Proposed home |
|---|---|
| Plan, specs, records, reviews, measurements | this milestone directory; `notes/`, execution-only `evidence/` |
| Existing public workload | `tests/fixtures/transition_cost/`, retained byte-identical |
| New public controls / optional anonymized import | `tests/fixtures/incremental_evaluation/` (IE0) |
| Differential/counter tool | `tools/measure_incremental_evaluation.py` (IE0), reusing existing driver helpers |
| Dependency/invalidation support | ModelIndex / model dependency homes; new module only with layer assignment (IE1) |
| Reusable extension calculation | `extensions.py` / `extension_preparation.py` or a lower-layer assigned home (IE2) |
| Selective constraints and orchestration | checker/correspondence family homes; session facade above checker and below API entry (IE3) |
| Observation/feedback integration | `exp/session_runtime.py`, `session_eval.py`, `session_contract.py`, matching schemas only as approved (IE4) |
| Public docs and release note | `docs/reference/python-api.md`, `capabilities.md`, `docs/guides/data-and-transitions.md`, `docs/agents/dev-session.md`, `docs/release-notes.md` (IE5) |

Do not extend a low-layer cache to import `api` or a persistent experiment
session. The existing `CalculationScope` stays ephemeral; cross-call ownership
is explicit. No discovery link edits or model evolution are part of this work.

## 4. Phases, criteria and residuals

### IE0 — Baseline, dependency census and differential instrument

First draft spec: [phase-IE0-spec.md](phase-IE0-spec.md).

- **IE0-C1:** pin fixture/source/configuration identities and capture fresh
  stateless and receipt baselines on the old 13-call replay and course control.
- **IE0-C2:** count executed derivation bodies, candidate/join work, constraint
  evaluations, fingerprints and fallback costs at actual lookup owners, with
  positive/negative controls. Supply interleaved uninstrumented timing modes.
- **IE0-C3:** enumerate eligibility/dependencies for existing rule families,
  recursion, negation, aggregates, exact/partial/opaque states, lineage,
  references, admission/options, claims and receipt report mutation. Demonstrate
  oracle rejection of deliberately wrong payload, branch and origin results.
- **IE0-C4:** freeze replay denominators and localized-change control expectations;
  state dirty-component coverage and achievable counted targets before IE1.
  Record optional new-workload absence explicitly and provide an estimate with
  dependencies, not a fabricated date.

### IE1 — Trusted session state and conservative invalidation

- **IE1-C1:** one dependency walk selects affected SCCs and constraints; each
  polarity, roster, implicit constraint and transitive edge has a discriminating case.
- **IE1-C2:** model edits including operations, population edits including reorder,
  delete/replace, options/reference changes and lost markers never yield stale reuse.
  Unknown/incomplete graphs fall back; validation order is pinned.
- **IE1-C3:** private detached state; one generation and explicit resource caps;
  reset/close, interleaved independent sessions, exception/cancellation rollback
  and concurrent-use policy tested. Proposed policy: one active call per session,
  reject overlapping calls, permit independent sessions.
- **IE1-C4:** eligibility and counted targets from IE0 become an approved branch
  matrix and corpus before extension reuse code is written.

### IE2 — Incremental structured extension envelope

- **IE2-C1:** warm dirty-component refresh reuses unrelated components; a recursive
  component refresh starts from current base state and reaches the full fixed point.
- **IE2-C2:** complete relation/lineage/unavailable/possible envelope and branch
  replay match fresh computation, including unavailable→available and reverse.
- **IE2-C3:** mutation, prior-view tampering, unsupported shape and resource-limit
  paths compute fresh or refuse according to approved order; never accept an
  empty relation as a substitute for unavailable or unknown.
- **IE2-C4:** independent-component and no-op body-work gates from completion
  predicate 4; include delete, negation and aggregate dirtying, not append-only cases.

### IE3 — Selective constraints and public check/transition sessions

- **IE3-C1:** dependency-indexed constraint evaluation, report assembly and current
  witnesses equal full checking at root, every loadable intermediate, computed
  post and declared post, including compiled operation obligations and references.
- **IE3-C2:** session results cannot mutate private state. Reproduce then fix the
  carried receipt-report mutation defect before integrating receipt reuse; preserve
  named refusals/eligibility and branch replay. Test references and options explicitly.
- **IE3-C3:** implement the opt-in public facade and show unchanged-component/no-op
  constraint-work gates plus strict reporter derivation-work reduction. Cold and
  fallback runs must remain semantically identical and their costs visible.

### IE4 — Host observations and feedback

- **IE4-C1:** validated host observations between calls/attempts invalidate affected
  state. A bad observation fails without changing the previous generation; duplicate,
  delete, replacement and no-op behavior follow the approved composition contract.
- **IE4-C2:** bounded counts and observation feedback with explicit schema/version
  compatibility, overflow behavior and deterministic retry ordering. Persisted
  artifacts never serialize cache handles; old session contracts replay unchanged.
- **IE4-C3:** demonstrate two attempts with an observation between them and compare
  full vs incremental feedback/results; update dev-session docs and any actually
  affected packaged skill references, with an explicit measured surface census.

### IE5 — End-to-end acceptance, docs and integration

- **IE5-C1:** frozen old/public control replay in cold, warm, receipt-only and
  incremental-plus-receipt modes; complete parity first, counted savings second;
  interleaved timing/peak memory/fallback rates with environment and limits.
- **IE5-C2:** public API/signature/export and source-successor pins, RF policy/layer
  tests, CLI/batch defaults and current focused experiment-session consumers pass.
  Build/install validation is bounded to the new shipped public surfaces; the
  exact installed candidate/module paths and artifact digests are recorded.
- **IE5-C3:** documentation explains eligibility, mutation, lifetime, observations,
  limits, fallback and a runnable example. A mechanism diagram illustrates dirty
  propagation and component reuse; no benchmark extrapolation to all 547 programs.

### Carried limitations and explicit disposition

Source for numbered rows: prior close's Open-questions sweep.

| Prior row | Disposition / owner |
|---|---|
| 1 incremental evaluation + two session requests | IE1–IE4; not a reopening of TP0–TP3 |
| 2 downstream acceptance | IE5 reports if new bundle supplied; otherwise close names reporter-owned follow-up, no downstream success claim |
| 3 mutable receipt report | IE0 reproduction, IE3 fix as integration prerequisite |
| 4 duplicate checker attempt after mint exception | IE3 investigates when touching mint; retain as named hardening carryover if not changed |
| 5 missing reference receipt case | IE3 reference compatibility control |
| 6 anchored evaluator hook | IE3 eligibility decision; full fallback permitted, no claim this refactor shipped |
| 7 shared accessor naming | close completeness sweep; do not rename for speed |
| 8 public outer index scope | IE1 mutation tests include caller-held scope; session verifies current content independently of a stale outer hit |
| 9 receipt repr/hash/equality | close completeness sweep unless it affects session ownership |
| 10 signal exception classification | remains framework maintenance, outside this milestone; rollback tests still required |
| 11–12 CI/build repairs | already resolved by PR #31; do not reopen |
| 13 missing policy/pin selection | IE-O10, every runtime spec |
| 14 interleaved measurement tool | IE0 and IE5 |
| 15 chained timings | already resolved; use current A/B protocol |
| 16 skill check | revisit only changed surface in IE4/IE5 |
| 17 approval hashes absent from history | IE-O11, commit approved spec before code |
| 18 intermittent failure | not established; no invented defect |

## 5. Documentation, skill and compatibility surfaces

IE3 owns public names, exact signatures, `api.__all__`, signature tests and
`tools/run_public_acceptance.py` changes if exports grow. IE4 owns session wire
versions and `src/gnd/skills/gnd-dev-session/SKILL.md` impact inspection. IE5 owns
final docs, mechanism diagram, release note and installed-candidate validation.
Measure affected references at phase execution; do not invent pin counts now.
Packaged links use the installer; development-skill twins change together only
if this work actually changes their protocol. No skill edit is currently required.

## 6. Risks and required controls

| Risk | Required control / owner |
|---|---|
| Most heads depend on every changed fact; little saving | IE0 graph/work census; IE5 reports fallback and dirty coverage; no target weakening after measurement |
| Missing negative, aggregate, roster or transitive dependency | IE1 discriminating cases and conservative dirty fallback |
| Recursive outputs survive deletion incorrectly | IE2 SCC recomputation from current base, deletion and alternate-path cases |
| Correct rows with stale witness origins or branch traces | IE2 full envelope parity; IE3 report/trace differential tests |
| Bad receipt/report contaminates later results | IE0 reproduce; IE3 private state/receipt guard tests |
| Diff/fingerprint overhead erases gains | IE0 counts entire path, IE5 uninstrumented A/B and cold/warm costs |
| Cache grows with step history or failure leaves partial state | IE1 one generation/caps/rollback, IE5 long-walk memory evidence |
| Refactor pins are missed again | IE-O10 plus exact source-successor inventory in phase specs |
| Persistent session hook weakens evidence or leaks facts | IE4 corpus-first wire/ordering review; bounded/redacted feedback |
| Unavailable new workload is mistaken for local acceptance | IE-O16 conditional boundary, no 547-program/date claim |

## 7. Out of scope

SQL optimization, downstream application changes or private datasets; arbitrary
rule-language changes; altered verdict/band/refusal semantics; serialized,
cross-process or persistent evaluator caches; parallel evaluation within one
session; semi-naive row-delta recursion/retractions; agent-call timeouts; automatic
native/PyRel/provider lanes, publication or certification. The completed prior
milestone and its historical evidence remain unchanged.

## 8. Execution, approval and review protocol

`auto=false`. The start-milestone invocation authorizes planning artifacts only.
The owner subsequently selected four local reviewer agents for plan and close
reviews (D6); plan approval and implementation remain pending. Selected lenses: semantics/invalidation, implementation/layers,
protocol/privacy/compatibility, and measurement. The owner
selection authorizes those local reviews; no paid panel is selected. A single
author self-check is not an independent review.

Plan approval follows review and disposition. Each phase follows process-phase:
harvest → detailed spec → owner gate → approved-spec commit → implementation and
focused verification → independent adversarial diff review → refactoring review
→ record and explicit-path commit. Optional per-phase spec panels require selection.
Corpus-first is the proposed instrument for new validation/wire contracts;
IE0's prose exception is justified in its draft spec. No phase is activated here.

For plan/close review, propose at most one initial round and one bounded
confirmation of reproduced blocking findings. Before round two, record the
convergence ledger and apply the exact stop rule in
`.agents/skills/process-phase/references/review-convergence.md`; do not duplicate
its conditions here. Findings need observable consequences and reproduction;
amended bytes receive no inherited review opinion. Stopping review does not
waive approval or authorize execution of an unimplementable contract.

Topic branches and PRs are mandatory. This branch inherited unrelated video
commits: isolate milestone-only changes for a PR against main rather than publish
that unrelated stack as incremental-evaluation work. Owner merge, release,
publication and certification are separate authorizations.

Close is not a feature phase: reconcile all criteria/evidence with exact source
identities, four reviews, final selected verification, docs and residual owners.
Do not create an empty close record or mark the milestone complete during planning.

## 9. Verification story and affected consumers

| Phase | Falsifiable result | Direct and affected consumers |
|---|---|---|
| IE0 | Reproducible full oracle; deliberately corrupted payload/trace/origin rejected; body and constraint counters live; no runtime diff | proposed `test_incremental_baseline.py`; existing `test_transition_cost_workload.py` |
| IE1 | Dirty closure includes every dependency kind; mutation never stale; caps/rollback/isolation enforced | direct invalidation tests; `test_rf6_index.py`, `test_popvalidate.py`, dependency/strata controls |
| IE2 | Selective complete envelope equals fresh full calculation; no work on unrelated component | direct extension differential tests; `test_m3_extension_preparation.py`, composition/fixpoint/aggregate controls |
| IE3 | Every checked snapshot/transition matches full route, receipts cannot corrupt it, fewer counted evaluations | direct session tests; TP3 receipts, public transition/trace/IR immutability, API signatures, semantic/correspondence/compiled-snapshot controls |
| IE4 | Observations validate before advancing; two-attempt feedback parity and old wire compatibility | direct observation tests; current experiment-session feedback/replay/driver consumers and skill surface checks |
| IE5 | Frozen replay parity plus counted savings, honest A/B, installed entry point and docs | integration replay, CLI/batch defaults, API/export pins, docs/example and installed-candidate checks |

All runtime phases include affected `test_rf4*`, `test_rf6*`, `test_rf7*`,
`test_rf9*` and `test_rf1_layering.py` contracts, chosen by current behavior and
registered source changes, without overriding lane exclusions. Exact commands
for IE1–IE5 are unresolved until their specs inventory changed definitions.
IE0's exact focused commands are in its spec. Prior green results are historical
context, not inherited verification of changed bytes. Broad `uv run pytest -q`
is on cadence only after explicit owner/CI selection; no automatic full replay,
native acceptance or recertification is scheduled here.

### Implementability sweep (author inspection, not review)

| Dependency / potential conflict | Proposed resolution and readiness |
|---|---|
| Same-call-only repairs contract vs cross-call reuse | New opt-in owner-approved scope; keep old default and scope boundaries. D2 must rule before IE1. |
| Full intermediate/post checks vs selective work | Preserve full check meaning and results, vary internal work only; full fallback whenever eligibility is unknown. D2. |
| Prior refresh mappings omit original lineage | IE2 complete-envelope prerequisite; cannot wire existing mappings straight into correspondence. |
| `ModelIndex` scoped digest may be stale under caller-held scope | IE1 verifies content at session boundary independently; no identity-only acceptance. |
| Constraint scope metadata not yet proven complete | IE0 inventory then IE1 conservative classification; no promises for unclassified families. |
| New reporter bundle absent | Existing pinned fixture/control permits IE0; new-workload performance claims blocked until supplied and admitted. D3. |
| Feedback/hook change conflicts with frozen attempts | IE4 owns explicit version/ordering migration; legacy replay preserved. D4 must choose detail before its spec. |
| Exact reporter savings unknown | IE0 freezes counts/achievability before optimization; failed feasibility returns to owner, never silently changes denominator. |
| Review instrument selected / release date unknown (p1, R3-F1) | D6 records the owner's four-reader selection; D5 and artifact approval remain pending. No execution-ready claim. |

## 10. Owner decisions and open questions

All rows except D6 are **proposed/open**, not owner-approved. D6 selects only
the review instrument; it does not approve plan/spec bytes. No approval hashes exist.

| ID | Decision / proposed answer | Cost / blocking point |
|---|---|---|
| D1 | Explicit in-process evaluation session; keep stateless defaults | New public surface and lifetime controls; rule before IE1; exact IE3 API after census |
| D2 | Permit cross-call selective evaluation under IE-R1..R4; retain all admission/intermediate/post obligations | Extends earlier scoped no-crosscall boundary, without reopening its milestone; rule before IE1 |
| D3 | Start on old public fixture + synthetic localized controls; admit new bundle when supplied | No 547-program acceptance without it; rule at IE0 gate |
| D4 | Include both carried observation/feedback requests as IE4, with explicit wire/ordering contract | More than a cache-only milestone; detailed host API and version decision before IE4; no silent deferral |
| D5 | No date commitment until IE0 supplies estimate and risk evidence | Reporter asks for date; owner scheduling decision after IE0 |
| D6 | **Owner-selected, 2026-10-19:** four local reviewer agents, as in the prior milestone | Explicit reply to review-instrument question; plan and close reviews use four lenses in §8. No implementation or artifact approval implied |
| D7 | Counted gates in completion predicate 4; timing evidence only | Avoid fabricated factor-of-N promises; exact replay counts frozen in IE0 |
| D8 | Approve provisional cache bounds in IE-R8, finalized with exact accounting before IE2 | Falling back may lose gains; correctness never relaxes to fit budget |
| D9 | IE0 prose approval; later validation/wire work corpus-first by default | IE0 adds a measurement tool, not a new product wire; review its discriminator stories and negative controls |

Next action (p1): owner disposition of the reviewed plan and its open decisions; then explicitly select `process-phase IE0 incremental-evaluation` for its
owner gate. Planning authorship supplies none of those approvals.

## Close reconciliation annotation, 2026-10-20

This annotation supersedes the retained pending/status and auto=false drafting
statements above; it does not rewrite the owner-approved pre-annotation r2 or
claim new owner personal readings.001 binds the original approved bytes;002
subsequently delegates named execution and close under auto=true.003–008 record
all six accepted phases and their concrete spec/amendment gates.009 records
local close with four independent reader opinions, the final question sweep,
PR33 and a separately bound delegated close acceptance.

Completion predicates1–7 are discharged in009. The frozen reporter denominator
remains4878; session bodies179, with complete ordered parity. Reporter median
wall time regresses5.8306→6.7885 seconds; D7 makes timing informational, not a
speedup claim. Constraint primitives remain1365 in both receipt/session reporter
arms. IE-Q1 assigns bookkeeping performance to a future explicitly selected
framework-performance effort. The absent547-program bundle stays reporter-owned.
No delivery date, default activation, production publication, certification or
merge is inferred. Historical TP3 records remain unchanged;006's in-place reasoning
correction is explicitly disclosed and owned by009, not silently treated as
original record bytes. See notes/close-question-sweep.md for all18 inherited rows,
IE-Q1..Q10 and D1–D9 dispositions. No successor execution is selected.


## IE6 reopening amendment, 2026-10-20 (proposed for delegated gate)

The owner explicitly asked to add a phase and implement Astra's performance
recommendations in this named milestone. This reopens incremental-evaluation
under the existing002 auto delegation and review selections; it does not reopen
TP0–TP3 or rewrite009's historical close. Earlier completion/status annotations
remain historical. IE-Q1 is now assigned to IE6 for the bounded work below.
The effective DAG adds **IE5 → IE6 → renewed close** (seven implementation phases).
The existing topic branch and PR33 remain the contribution home.

### IE6 — Reduce policy accounting and cache lookup overhead

Source: owner-requested Astra performance review of d0ffd9a; retained review
summary evidence/IE6/astra-performance-review.md. Instrumented profiles identify
repeated full-policy size walks, fingerprint allocation, signature hashing and
per-constraint policy construction. Diagnostic timings overlap and predict no
wall gain. A process-only builtin fast path improved a three-sample course median
by3.28%;37 focused tests passed, not shipped or general acceptance.

- **IE6-C1:** preserve full payload/exit/branch and ordered complete-calculation
  parity, frozen reporter denominator4878 and strict lower session body count.
  Existing current-content/marker/options/ownership/rollback/caps remain binding.
- **IE6-C2:** remove repeated traversal/hashing of normalized immutable policy
  descriptions using bounded verified metadata; keep exact equality, live code
  and mutable configuration checks on every reuse boundary. Charge all retained
  policy content conservatively and measure actual private clones. No identity-only
  admission, digest-only equality, weakened resource limits or fallback semantics.
- **IE6-C3:** reduce ordinary builtin accounting overhead; investigate per-constraint
  and extension setup only when measured and live mutation controls remain intact.
  Structural visit counters must discriminate pre-fix from optimized behavior.
- **IE6-C4:** fresh serialized current-byte measurements on reporter/course/localized
  and same-host balanced pre-IE6/session versus final/session runs. Gate correctness
  and deterministic bookkeeping reduction; elapsed improvements are measured and
  reported without claiming universal speedup. Do not change D7 after results.
- **IE6-C5:** focused state/prepared-policy/extension/session/observation/receipt/
  correspondence and RF layer/query/source controls, bounded fresh wheel smoke,
  updated performance docs, one independent adversarial diff review, refactoring
  disposition and011 phase record. Renewed close uses four local independent readers.

Inherited residuals: projected cache footprint is not RSS; full admission,
adaptation, projection and compatibility evidence remain fresh; unknown external,
reference/guarded/anchored/opaque cases stay conservative; new547 input remains
absent/reporter-owned; no delivery date, broad/native/provider acceptance,
certification, default activation, publication or merge. New artifact hashes and
selected tests supersede only affected current-byte claims, never historical gates.

Amendment obligations: IE-R1..R10 and§§5–7 remain effective. IE6 owns runtime
incremental_state.py and optionally correspondence.py/extensions.py, their direct
controls, exact source-scan successors, docs/release notes and installed candidate.
No packaged skill, feedback wire, public signature or layer assignment change is
planned. A new runtime home would require explicit map/source-scan closure first.
§9 IE6 row: frozen complete parity, lower bookkeeping visits and bounded accounting;
focused direct/affected tests plus selected installation/docs; broad lanes remain
explicit-owner cadence. §10 IE-Q1: bounded optimization now selected, any remaining
costs retain framework-maintainer ownership. The public workload/date question and
all other009 carryovers remain unchanged.

Implementability: immutable normalized keys can have verified bounded size/hash
metadata while mutable configuration still receives live checks; conservative
accounting may overcount shared storage but cannot undercount it. Product data
and unit outputs remain detached. Baseline source can be archived without importing
or modifying it, and timed in separate serial processes against the same fixtures
and interpreter. There is no mandatory wall-time factor promised before measurement.

Review budget: one initial four-reader amendment review, at most one confirmation
of reproduced blocking issues, using the existing convergence rule by reference.
Phase review uses the previously authorized read-only Codex CLI; renewed close
uses the selected four local reviewers. Optional phase-spec panel omitted.
