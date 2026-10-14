# M3 phase09: Count compiled subset work once per required projection

Status: scoped ready contract,2026-10-13; runtime edits not started.

## Obligations and new observed finding

| Source | Obligation | Acceptance |
|---|---|---|
| M3 plan follow-up/roadmap6.5, phase05 agreement gate | compiled native checks cannot spend all budget on empty operation subsets | empty_subset_no_required_work; native_compiled_admission |
| PR19 bounded compiled snapshot contract | actual role-cell work stays bounded and visible | budget_preserved; required_projection_shared |
| Source/current snapshots | typed matching, ordering and scope/refusal precedence unchanged | typed_pair_parity; compiled_public_controls |
| Protocol/app boundaries | source-owned RED/review/record and app preview | corpus_first; independent_review; hash_identity |

After phase08, candidate dw_5162/513629919376 compiled check over42782 real rows
returns4 with3 compiled-obligation-work-limit findings for unused filter_pattern,
order_result and limit_result. Public default check/full native start still2.
Diagnostic partial profile also exposes quadratic witness-coordinate scans;
that is a separate possible follow-up, not silently included here. Original15s
complete-question and all109agreement gates remain unchanged; held-out/test unread.

## Exact design and semantic ruling

In compiled_obligations.py create one ephemeral prepared subset-row view per compose,
bound to that call's effective facts and existing shared WorkBudget. Cache required
row identity sets by (required facttype, ordered required role names) within this
view only. Each required role projection is counted/built once; each actual left
row's role cells are counted when matched. Preserve typed identity_key, pair order,
repeated roles, original offending-row order and complete multi-role matching.
Standalone offending_rows signature/meaning remains unchanged: it creates its own
prepared view. No global/population/model cache, retained context or new public API.

If the known left relation is empty, return[] without indexing required rows or
charging role-cell work. Existing compose coverage and unavailable/opaque guards,
metadata possible-row accounting and metadata_exhausted precedence remain ahead of
matching. Do not infer absence from unavailable/possible/opaque relation data.
The existing vacuous branch then applies; scope IDs/messages/count projection stay
at their current homes. MAX_COMPILED_WORK stays100000 and active over-budget work
still refuses. Cache identity includes right role order so unrelated projections
cannot share a set. New view each compose prevents cross-call/pop/model mutation
reuse; source model/current-operation edit controls remain mandatory.

D9 delegated ruling: correct only budget-related output differences when earlier
work was redundant preparation. Empty known/covered/available subset is vacuous,
not work-limit solely because unused required rows were scanned. This changes the
native3 unrelated work-limit outcomes to their valid computed outcomes, rather than
preserving a censored answer or raising the cap. Exact ordering/types/warnings and
all already completed noncensored decisions must remain unchanged. No rule/gate
waiver or golden regeneration without declared expected differences.

## Corpus-first acceptance and coverage

New source tests/test_m3_compiled_work.py, using existing compiled-snapshot
numeric/pre/model fixtures and existing typed-role matching scalar controls.
No new domain population/model fixture or invented source rows.
empty_subset_no_required_work: existing projected required rows, leftrows removed
in the algorithm-unit view; WorkBudget0, zero visits,[]; old implementation fails
by preparing right rows. required_projection_shared: prepare one existing active
entry twice, right projection counted once and each left pass counted; expected
visits = right_role_cells + 2*left_role_cells, not twice both. Different right-role
order uses separate sets. budget_preserved: actual active over-budget projection
raises/refuses; old nonempty MAX0 publiccontrol retained. Public native full current
candidate must lose only actual redundant-work refusals, without missing evaluations.

Focused source gate: uv run pytest -q tests/test_m3_compiled_work.py
 tests/test_compiled_snapshot_obligations.py tests/test_m3_population_schema.py
 tests/test_m3_generated_json.py tests/test_m3_indexed_subset.py
 tests/test_public_transition_contract.py tests/test_public_transition_trace.py
 tests/test_transition_report.py tests/test_public_transition_api_guards.py
 tests/test_public_transition_ir_immutability.py tests/test_v70_phase4_transition.py
 tests/test_rf1_layering.py. Ruff affected source/tests. Default exclusions remain;
no historical/proof/certification/provider replay. Source broad cadence only
explicit owner/CI. Independent own Codex CLI read-only stdin review required.
App90 affected controls repeat candidateoverlay; pin unchanged.

Native measurement before run: full same real candidate/public compiledcheck,
normal3 repeats cap60, APIadmission/completion, count/warning/refusal/report hashes,
exact source/model/state/candidate population identities. Baseline phase09 profile
8.142s is profiled, not a normal speedratio; take fresh normal baseline on accepted
phase08 source65b6de0 and compare. Default native root remains baseline8.302s with
unchanged report; no claimed effect unless measured. Complete tuning question
cap8/top3/workers1 wall120 once to decide next work. No final held-out gate here.
Algorithm controls demonstrate actual counted-work bound, using existing scalar
rows; native timelimit bounds actual added layer, no flaky tiny-time CI assertion.

## Standing rules, approval and remaining boundaries

Totality: internal prepared view consumes the same typed compiler entry/validated
fact view as existing matcher; no new untrusted JSON/document consumer. Input cap
vs algorithm: cached required projections and empty-left short circuit, samebudget
counted actual work; unit bound and native60s controls. Validation order: coverage/
unavailable/metadata guards retained ahead of matching, parser/markers untouched.
One policy walk: one shared matching view, no per-operation cloned algorithm.
Normative prose: same compiled subset semantics; only redundant work removed.
Representation by measurement: exact completed-result/counterfactual native controls.

Delegated auto=true2026-10-13, owner M3auto/make fixes part of M3/go ahead and plan
required follow-up clause. Corpus-first; cost0; no new synthetic domain data,
source merge/release/certification approval. Hash approval before implementation.
Source governance topic/PR/explicit owner merge retained; app directmain.
Phase09 required before05, no changed latency/agreement targets. If reporting/index
or further public context reuse is still required, scope it separately before edits.
