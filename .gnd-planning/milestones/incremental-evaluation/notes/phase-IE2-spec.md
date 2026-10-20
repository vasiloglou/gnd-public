# IE2 — Incremental structured extension envelope

Owner-decided under delegated auto approval, 2026-10-20. IE1 accepted in 004 / a90e5a3. Scope: approved plan IE2-C1..C4, IE-R1..R10,
IE-O2/O3/O12/O13, prior TP4/CR-01 and IE0 targets. No public activation here.

Use the existing calculators and strata. Reuse one completed component envelope
at its actual defining lookup, without implementing a second rule interpreter.
For a dirty recursive SCC, run the original fixed point from empty current heads.
Retain ordered typed direct dependency rows, roles, lineage and identity codec;
include upstream unavailable state. Model/options are bound by IE1. Helper/code
and limit policy changes miss. No dependency graph with incomplete classification
may select a cache. Transitive changes propagate through freshly produced upstream
relations; own claimed rows are compared by the existing caller after calculation.

Acyclic ordinary calculator: extract its current per-component calculation into a
bounded callback, restore its relation and logical work delta on hit. Stratified
calculator: invoke the existing implementation with one SCC selected, current base
and completed lower strata; store plain envelope records, rebuild original mapping
classes at the defining home. Sum ordinary logical counts; maxima remain maxima.
Replayed logical counters preserve reports; IE0 code-event counters measure actual
executed body work independently. Branch identities replay through IE1.

Partial/opaque, observed partial, witness tracing, reference presentation and
unsupported identities conservatively execute the original full calculation.
No limit/refusal is relaxed. Full envelope parity is required even on fallback.
No default API change; the hook only runs under an explicit ReuseState transaction.
Private snapshots remain bounded by IE1 and rows count input plus retained output.

Corpus-first cases: ordinary independent components and no-op; insert/delete/
replace/reorder origins; recursive alternate support deletion; exact negation and
aggregate dependencies; unavailable→available and reverse; opaque partial fallback;
returned-envelope tamper; model operations/helper/limits/options mutation; cap
fallback and branch replay. Expected answers are fresh original calculations, with
separate declared expected work assertions. Add exact reporter controls; no claimed
new-workload or wall-time guarantee. Strict reporter <4878 body gate is IE5.

Focused verification: new extension differential corpus, IE1 direct/review tests,
existing extension preparation/composition/fixpoint/aggregate controls, affected
layer/query/source pins. Required independent CLI diff review and refactoring
record before IE2 acceptance. Broad/native/provider tests remain unselected.


## Harvest and standing rules

| Source | Required discharge |
|---|---|
| §4 IE2-C1, IE-O2/3 | full original SCC calculation on dirty dependency; no old SCC seed |
| IE2-C2, IE-O12, §9 | “Selective complete envelope equals fresh full calculation; no work on unrelated component.” Compare ordered rows/roles/codec/lineage, unavailable reason/binding/source, possible coordinates, logical work and branch set. |
| IE2-C3, IE-O13, prior TP4/CR-01 | caps, mutation, current operations/model identity and private result cloning inherited from IE1 and exercised at calculator boundary |
| IE2-C4, completion predicate 4 | direct body profiler, unchanged component zero; no-op zero; deletes/negation/aggregates |
| §0 IE-R1/R3 | same envelope and refusal order; always retain original admission and final claim comparison |
| IE-R2/R4/R8 | IE1 current model binding, detached plain envelopes, row/byte cap on both retained generations |
| IE-R5 | report logical counters replay; actual body execution measured independently |
| IE-R6/R9 | existing extension home, no parallel interpreter, ModelIndex for newly shared queries; zero layer allowances |
| IE-R7/R10 | explicit state only; no new default, network, reserved data, publication or certification |
| §5 and prior close pins | maintain aliases, current source visitation, exact dynamic/query successors; no skill surface changes |
| §6 risks | deletion/alternate support, stale origins, partial/unavailable and callbacks have corpus siblings |
| §10 D1/D2/D7/D8 | freeze in-process opt-in, exact work target and IE1 retained caps; inherited owner plan decisions |
| IE0 003 / IE1 004 | historical baseline stays historical; no new workload claim; IE3 owns report receipt vulnerability and constraints |

The six process standing rules apply through: explicit keyed policy and one defining algorithm, corpus-first expected answers, actual-work gates, bounded freshness/clone helpers, refutation before repair, and recorded compatibility disposition. No duplicate algorithm or handwritten generated artifact is introduced.

## Design surfaces and size

`extensions.py`: ~180–260 new lines including component envelope helper and small calculator hooks. Existing public signatures/aliases remain intact. Proposed internal `_incremental_components(model, relations, calculate, *, exact, fixpoint)` returns an original result or None to select full fallback; `calculate` invokes the original selected-component implementation. Ordinary calculator extracts a per-head relation callback with original `_JoinWork`. `model_index.py` query surface is reused, not forked. New test file ~200–350 lines; no new runtime module. Plain snapshot shape: `(component_ids, ((dependency_id, roles, rows, row_lineage, identity_codec), ...), unavailable_records, policy_modes)`. Retained result shape: `(relations_dict, unavailable_dict, logical_work_dataclass)`. Partial results conservatively bypass, so their existing `possible` envelope is never reconstructed from incomplete data.

## Decisions and implementability

D1 delegated: reuse only complete classified ordinary/exact SCC envelopes, opaque/partial/callback modes fresh. D2 delegated: preserve logical counters using per-unit deltas, maximum counters combined by max; actual work via profiler. D3 delegated: per-unit input+output row accounting and existing IE1 bytes/rollback. D4 delegated: one independent CLI review plus at most one confirmation; reproduce findings before repair, no third round. D5 delegated: no public facade or receipt changes here. All are implementable using original calculators, selected-head path and explicit plain records; unknown inputs can always use original full calculation. No requirement forces a new interpreter or changes public acceptance rules.

## Tests and verification-selection ledger

Corpus stories `extension-stories.json` and separate answers `extension-answers.json` precede runtime; tests compare untouched full calculations outside the explicit state with the active component path. Tests must assert literal expected recursion contents and independent work, so equal empty or stale results cannot pass.

| Obligation | Disposition | Command / boundary / invalidation |
|---|---|---|
| C1–C4 corpus and IE1 ownership | run | `UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline pytest -q tests/test_incremental_extensions.py tests/test_incremental_state.py tests/test_incremental_state_review.py`; exit 0, new fixtures/calculator/state edits invalidate |
| preparation, exact/fixpoint/aggregate/composition parity | run | same prefix `pytest -q tests/test_m3_extension_preparation.py tests/test_v70_phase4_fixpoint.py tests/test_v62_phase4_aggregate.py tests/test_v62_phase4_composition.py`; exit 0, calculator/preparation/fixture edits invalidate |
| lookup owners, aliases and layers | run | same prefix `pytest -q tests/test_rf3_core.py tests/test_rf3_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_rf7_structure.py`; exit 0, production/helper/map/successor edits invalidate |
| current downstream exact owner controls | run | same prefix `pytest -q tests/test_public_derivation_identity.py tests/test_public_derivation_cost_mutations.py`; exit 0, exact dispatch/helper changes invalidate |
| lint | run | same prefix `ruff check src/gnd/extensions.py tests/test_incremental_extensions.py tests/support/pyrel_application_successors.py`; exit 0 |
| historic bytes, full default, native/PyRel/provider | cadence | owner-selected or separately configured CI only; no current assurance claimed from old source hashes |

No current source-successor row names these calculators (mechanical harvest); RF3 move proof deliberately checks historical commit 4415327 and remains unchanged. Exact owner-sensitive query policy and dynamic sites acquire authenticated IE2 successors where actual AST deltas require them, chained after IE1. A raw model query waiver is not a substitute for a shared index.

## Out of scope and residuals

IE3 owns selective constraints/public sessions/report immutability; IE4 observation/retry feedback; IE5 reporter acceptance and installed distributions. The new 547 workload is absent. No timing, RSS, production date, broad-suite, native/provider or certification claim. Historical source evidence is not current-byte acceptance. A full fallback may forgo savings; it cannot change semantics.
