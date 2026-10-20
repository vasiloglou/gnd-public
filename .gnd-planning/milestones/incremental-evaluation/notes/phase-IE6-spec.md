# IE6 — Reduce incremental bookkeeping overhead

Awaiting delegated gate, 2026-10-20. No IE6 production implementation exists.

## Provenance

Effective canonical plan IE6 reopening amendment;009 historical close and008
current measured scope; owner requests Astra review then adds and implements a
phase.002 named auto and CLI transfer authority persists. Amendment review and
its exact digests are recorded separately; no historical reviewer opinion covers
this spec. Spec prose is the approval instrument, with tests authored before code.

## Obligations and discharge

|Source|Obligation|Discharge|
|---|---|---|
|Plan IE6-C1,§9,008|Complete parity and original denominator|Integrated measurement, direct ordered/mutation/receipt controls|
|IE6-C2,004–005|Bounded immutable policy accounting, private clones, live mutation|Design and positive/negative footprint/lookup tests|
|IE6-C3,Astra findings1–4|Reduce repeated work, prioritize measured paths|Visit-count regressions and measured scope; optional setup optimization only if safe|
|IE6-C4,IE-R5,D7|Interleaved same-environment uninstrumented timing, no observer contamination|Baseline/archive protocol below; current integrated tool and counters|
|IE6-C5,§5,IE-O10/14|Source pins/layers/consumer/installed/docs closure|Selection ledger below|
|009,close sweep IE-Q1/Q7/Q8|Keep memory/full-work limits explicit|Boundary and renewed question sweep|
|§10 D1–D9,002|Opt-in, current admission, named auto, review/merge boundaries|No public signature/wire/default change; exact delegated gate|
|§6 risk register|Stale keys, malformed data, bounds, false counters, missing downstream input|Existing mutation/cancel/error controls plus new accounting negatives|
|§7|No semantic eligibility expansion, private data, row-delta recursion/native lanes|Out of scope below|

## Standing rules

IE-R1 complete ordered oracle; IE-R2 fresh current model/options and live guards;
IE-R3 original admission/refusal order; IE-R4 detached atomic state unchanged;
IE-R5 real accounting visit counts with positive and negative controls; IE-R6
existing policy/family homes and zero layers; IE-R7 opt-in defaults unchanged;
IE-R8 same bounds and node/depth/cycle refusal; IE-R9 all six paid rules below;
IE-R10 spec committed first and no private material. Totality: bounded optional
memo keys still fail fresh on unsupported objects. Input versus algorithm caps:
node/depth/bytes retained and work counters bound repeated normalized-key visits.
Validation order: original guards before hits, calculate errors outside setupcatch.
One policy walk: extend existing normalization rather than new family dispatch.
One prose home: API eligibility remains python-api.md, measured results cite evidence.
Contested facts: measured pre-fix RED and final counted/elapsed experiments.

## Goal and design

Reduce repeated policy bookkeeping with identical check/transition outcomes.
Primary home src/gnd/incremental_state.py (estimate80–180 changed lines):
keep `_measure(value, limit)` return contract and `_clone(value)` behavior;
add internal verified immutable policy metadata, built only after bounded
normalization, carrying conservative footprint and reusable hash information.
ReuseState.prepare_policy(policy) and reuse(namespace, unit, snapshot, calculate,
*, policy=(), rows=0) retain public/internal callers. Never replace structural
equality with hash equality. Measurement of enclosing entry must charge policy
storage and all residual content, including actual private clone, node/depth work
and dictionary/proxy/metadata overhead. Functions/code/types remain borrowed handles.
A scalar/container fast path skips dataclass introspection only for exact builtins.

Optional correspondence.py/extensions.py (0–100 lines): use prepared metadata
or context-local dependency planning only if the same live helper/registry/default/
closure and model checks still detect every existing same-transaction mutation.
No new memo lifetime inferred from Python function identity. Defer unsafe or weakly
measured setup refactors rather than expanding eligibility.

Tests tests/test_incremental_performance.py (estimate150–250 lines): count real
measurement and policy-node visits on repeated distinct units, warm hits and dirty
misses. Builtin fast paths avoid dataclass inspection while custom records still
account storage. Full normalized key content remains counted, including proxy
backing and both generations. Verify cache limits, unsupported/deep/cyclic keys,
changed code/mutable defaults, collision-safe equality, cancellation and detached
results with existing and new controls. Each new optimization has a test observed
RED against d0ffd9a; existing behavior controls must remain GREEN.

## Decisions (proposed delegated rulings)

D6.1: conservative precomputed immutable metadata permitted, no quota relaxation.
D6.2: prose gate exception: no new serialized/exit/validation semantics; existing
validation contracts fixed, new deterministic performance tests written RED first.
D6.3: no required elapsed factor; deterministic bookkeeping reduction and parity
hard gates, same-host elapsed results report success or remaining regression.
D6.4: preserve named auto authority, four local plan/close readers and CLI phase
review transfer; at most initial+one confirmation, no paid/native/broad lanes.
D6.5: update same PR33; merge/publication/certification remain unselected.

## Tests and selection ledger

All commands use UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache, offline uv and
PYTHONPATH=.:tests as necessary; expected exit0 unless explicitly RED below.

|Obligation|Disposition / command|Boundary and invalidation|
|---|---|---|
|C2/C3 optimization corpus|run pytest -q tests/test_incremental_performance.py (RED before code, then0)|New accounting/signature branches; rerun on implementation changes|
|C1/C2/C3 mutation/caps/cancel/clone|run pytest -q tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_prepared_policy.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py tests/test_incremental_sessions.py tests/test_incremental_observations.py tests/test_incremental_session_measurement.py|Selected direct consumers of state and keypolicy, rerun on state/policy edits|
|C1 root/receipt/current context|run pytest -q tests/test_tp3_check_receipts.py tests/test_incremental_session_replay.py tests/test_public_correspondence_runtime.py tests/test_public_semantic_counting.py tests/test_m3_extension_preparation.py|Original report/admission/logical-work consumers; current-byte controls|
|C5 RF/source/API|run pytest -q tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_rf4_peripheral.py::test_current_successor_body_and_import_controls_are_live tests/test_rf4_review_regressions.py::test_transition_source_guard_visits_the_defining_payload_module|Exact source inventory changes get authenticated successors, no waivers|
|C1/C4 integrated|run python tools/measure_evaluation_sessions.py --out /private/tmp/ie6-integrated.json|Current source/fixture identities before/after;ABC/BCA/CAB; no editing while running|
|C4 pre/final session|run temporary recorded driver,3 balanced before/after/full-receipt samples per workload|Archived d0ffd9a src/tools/tests fixtures, same interpreter/cwd per tree, subprocess imports verified; no profiler; no concurrent gates|
|C5 lint|run ruff check declared changed runtime/test/tool/helper paths|Rerun after last edit|
|C5 docs/install|run source-bound wheel build/offline fresh venv/outside-checkout session smoke; doc links|Same bounded public session smoke as IE5, artifact SHA and actual module paths recorded|
|Other prior gates|cadence uv run pytest -q, explicit owner/CI selection|No broad/default/evidence/census/native/provider/certification inference; old claims remain historical|

## Predeclared experiments and limits

Before code, archive d0ffd9a src/tools/tests fixtures and config to temporary
baseline; retain source/fixture identity maps. Profile diagnostics are not timing
claims. Final current integrated oracle compares expected exits, fullpayload,
branches and ordered outermost calculation requests. A separate process driver
loads either baseline or final source (verified actual module paths), with full
receipt control as third arm and rotations ABC/BCA/CAB for3 samples afterwarmup.
Keep counters/profilers off timed runs; separate accounting visit tests must be
live against actual bookkeeping lookup owners. Range/raw samples/environment are
retained; shared host uncontrolled. No claim of downstream547 acceptance or general
elapsed gain. Do not weaken counted/body/correctness targets after measurement.

## Out of scope and size

No new family eligibility, row-delta recursion, feedback wire, public signature,
default activation, clone removal, marker/model identity shortcut, persistent
cache, new dependency, discovery link/skill edits, broad suite or release/certification.
Expected runtime80–280 changed lines and tests150–250; record actual deviations.

## Approval instrument and implementability

Prose with pre-code deterministic tests, under D6.2 exception. Decisions are
implementable through bounded immutable normalization and conservative accounting;
constraints that cannot preserve live mutation checks remain deferred. No promised
elapsed threshold depends on absent workload. Exact gate hashes and delegated
approval are recorded outside this spec after review and before implementation.


## Pre-gate named cases and initial review disposition

Four independent initial amendment readers accept; responses in evidence/IE6/
plan-{correctness,measurement,structure,protocol}.md. No confirmation required.
Protocol reader requested explicit test names; this author addition has no implied
new reviewer opinion. All cases are in tests/test_incremental_performance.py:

|Case|Pre-code outcome|Final expected|
|---|---|---|
|test_prepared_policy_tree_is_measured_once_for_many_misses|RED25 visits versus1|GREEN1 preparation walk,12 misses retained|
|test_prepared_policy_hash_not_repeated_at_each_lookup|RED12 complete signature hashes|GREEN prepared keyhash once, zero complete signature hashes|
|test_builtin_size_walk_skips_dataclass_introspection|RED builtin introspection|GREEN no builtin reflection|
|test_cached_footprint_charges_full_policy_and_private_values|GREEN|GREEN conservative full retained content|
|test_prepared_policy_metadata_cannot_bypass_enclosing_work_limits[MAX_NODES/MAX_DEPTH]|GREEN both|GREEN both, explicit fallback|
|test_prepared_policy_memory_boundary_is_conservative|GREEN|GREEN exact/under byte caps|
|test_collision_equal_hash_cannot_replace_structural_policy_comparison|GREEN|GREEN changed classpolicy recomputes|
|test_raw_policy_and_unhashable_calculator_remain_safe|GREEN|GREEN rawkey and unhashable fallback|
|test_custom_record_proxy_cycle_and_nonfinite_still_measured|GREEN|GREEN custom and hostile cases|

Initial pre-code command exited1:3 failed,7 passed in0.41s. No source changes.
Preserve logical node/depth accounting in memoized subtrees separately from size;
metadata is transient per prepared context and not added to retained entries, so
entry accounting remains full signature/private clone/branches plus1024 allowance.
Initial primary implementation excludes optional correspondence/extension planning
changes pending actual measurement; those recommendations can remain named debt.


## Implementation findings

Initial metadata implementation passed47 direct cases but exploratory course
latency regressed: raw-policy hits unnecessarily built size metadata that is only
used on admission. The new raw-policy warm-hit test observed5 rootwalks versus1
(RED1failed). Move raw metadata construction after the actual miss/calculation;
live raw normalization/hash still happens on each lookup. Avoid an unnecessary
max() call per measurement node by a direct depth comparison. Neither changes
approved semantics. First CLI review began on initial state SHA256
02bab4efed074221822e4dd9a0ee84c01bbd0c583d071c20425ad848f180ad9d;
its source snapshot is retained outside Git /private/tmp/ie6-initial-reviewed-state.py.
Later fixes carry no initial-opinion claim and are subjects for bounded confirmation.


## Live-hashability repair amendment (delegated auto, 2026-10-20)

Astra CLI's first review identifies a mutable metaclass hashability change.
`test_prepared_policy_rechecks_live_hashability` reproduced RED1failed:hit1 versus
fresh2. Blocking within this phase's guard-preservation promise. Restore original
`hash(signature)` on every lookup, omit new preparation/raw redundant hashes.
The approved `test_prepared_policy_hash_not_repeated_at_each_lookup` expected
answer is explicitly superseded and replaced by this live-hashability regression;
its performance expectation was unsafe. Exact prior test/expectation remains at
e897967. Keep rootwalk/builtin/raw-hit reduction gates and exact equality controls.
This correction has no inherited initial opinion; bounded confirmation checks it.
The original reduced-hash proposal and initial corpus RED are preserved as history.
