# IE4 — Validated host observations and bounded feedback

Delegated approval (auto=true), 2026-10-20. IE3 accepted in006 / cd61f56.
Implementation begins only after this exact gate is committed. Sources: complete approved plan §§0–10, IE4-C1..C3,
IE-O4/O7/O8/O13/O14/O15, TP3 close carried requests, and IE3 public session.
Owner's named auto delegation permits this explicit D4 detail ruling.

## Contract and decisions

Keep this feature in the explicit in-process EvaluationSession, separate from
persistent gnd exp contracts. Add observe(population, replacements) -> Population
and check_with_feedback(population, *, attempt: int) -> (payload, feedback dict).
No change to existing check/transition result wires or persistent session versions
1–8/feedback1–9. Closed older readers must still reject the new feedback kind.
New helper gnd.evaluation_feedback lives in checking below API, with a layer map
entry, source visitation and zero allowance. It never imports API or exp runtime.

D4a: observations replace whole relations: known fact id -> ordered row list;
omitted relations unchanged, [] deletes, equal replacement is a no-op, duplicates
retained. No implicit identity/upsert/deduplication, and no external truth claim.
Require a current loaded validated base; reject closed/busy session before work.
Build complete normal population document and use load_population_bytes with the
current model and safe synthetic source label. Never copy a validation marker or
use trusted reference-union composition. Apply loader's existing 10MiB cap and
normal schema/structural checks. New snapshot and all nested containers detach
from the caller. Invalid observation leaves old population, generation, feedback
and next attempt unchanged. Observation transaction always discards staging;
next check computes ordinary current-content invalidation.

D4b: feedback is a separate closed strict wire, kind evaluation-session-feedback,
schema_version1. Fields: attempt (strict integer1..1000000), operation check,
exit_code (existing check codes0/1/2/3/4/70), verdict_counts (fixed pass/fail/warning/unchecked/vacuous keys),
rows of fact_type (<=256 characters), asserted_count (0..2147483647 or null), asserted_status available/not-evaluated/overflow,
computed_count (same), computed_status available/unavailable/not-evaluated/overflow,
omitted_entries and truncated. Counts never include values, witnesses, paths,
messages, handles or Python object identities. Derived counts come from existing
structured extension calculation on current validated population, not coverage.
Unavailable is distinct from available empty0. Unsupported reference/partial/error
modes explicitly report not-evaluated. Count overflow reports null/overflow,
never an apparently exact saturated count. At most128 rows and16KiB canonical
UTF8 JSON; deterministic model order and suffix truncation with omissions counted.
Identifier metadata is intentional; no cell-value material is emitted.

D4c: attempt is explicit and exactly last successful feedback attempt+1. Only a
completed returned feedback result advances it; rejected observation/attempt or
feedback construction does not. Completed check error may consume an attempt but
cannot publish cache candidates. reset clears cache while lifetime attempt numbering continues; close releases
cache, rejects all subsequent work. No feedback history retained or serialized.
Existing state transaction provides overlap/cancellation/atomic publish. Full and
incremental feedback use the same builder with identical complete public payload;
cache stats stay out-of-band. Unsupported extra semantic modes are not keywords
on this initial feedback method; use ordinary check for those modes.

## Corpus before predicates

Write explicit stories/answers and new direct controls, observe absent methods
RED before runtime. Cases: duplicate/delete/replace/no-op relation composition;
unknown fact/bad role/type/stale marker rejection; original/replacement/output
alias detachment; closed/busy ordering; no generation publication on observe;
sequential attempt/retry/reset and immutable old bytes; count/row/id/byte bounds,
strict extras/type/version rejection and secret canary exclusion; available0 vs
unavailable vs not-evaluated; two attempts with validated observation and full
payload/feedback parity; unchanged component executes zero bodies/evaluators.
Discriminators must fail deliberately broken composition/count/version variants.
Public demo includes check -> transition -> observed check -> next transition;
IE5 retains complete branch/extension differential and final installed evidence.

## Harvest and standing-rule disposition

IE-R1/R3: ordinary check is sole report oracle; extra counts cannot change check
admission/refusal order, roots/intermediates/posts or report wire. IE-R2/R4/R8:
current marker and model binding, private detached population, transaction discard
on observation and failures, fixed wire/counter/row limits, no history. IE-R5:
actual original calculator work, diagnostics separate; no timing claim. IE-R6/R9:
one existing loader and extension calculator, one count/feedback home, explicit
layer/source metadata and bounded strict total wire. IE-R7/R10: explicit opt-in,
no persistent attempt mutation/provider/native/publisher/certification. Plan §§2,
4–6/9/10 D4 bind asserted-vs-derived distinction, old wires and skill census.
Prior closed milestone artifacts remain history; earlier performance overhead is
IE5-owned. New workload/547 acceptance remains unavailable, reporter-owned.

Docs home docs/agents/dev-session.md describes the separate host loop and
persistent boundary. Inspect/update packaged gnd-dev-session inline scope prose;
measure source file/link census and run packaged-link/surface controls. Discovery
links are installer-managed; no hand edits. Source-owned development twins are
unchanged unless their instructions actually change.

## Verification selection

Direct: tests/test_incremental_observations.py plus IE3 session tests and IE1 state
ownership regressions. Loader: tests/test_popvalidate.py. Compatibility: current
public_session_wire_guards/version_relabel, exp_session_evidence_compat,
exp_feedback_derivation, rf8 session profile axes and public_retained_session_results
nodes selected by collection inventory; never all provider-driven session tests.
Structure: rf1_layering, rf6_query_policy/packages, rf7_structure, rf9_ci_repairs;
add exact authenticated AST successors only if actual rows change, no waiver.
Packaged skill/prose/link tests selected from current collection inventory. Ruff
on changed files. Exact executed commands/results recorded on completion.
One authorized independent xhigh CLI reader and at most one confirmation; findings
need reproduced RED before repairs, no third review. Refactoring review explicit.
Broad historical/native/provider/certification lanes on explicit owner/CI cadence
only. IE5 owns bounded build/install and final docs/performance acceptance.

## Implementability/size

Normal Population.model_dump excludes format_version, so reconstruct that header
explicitly. Schema requires source/instances/covers; preserve complete base fields.
Snapshot marker validation runs before composition. Feedback attempt publication occurs inside the same session ownership boundary after complete construction; rejected construction cannot advance it. Existing structured view owns
relation unavailable/possible status; do not convert unavailable to count0.
Strict Pydantic closed models supply wire validation; deterministic projection and
byte cap remain separate checks. ~180–260 helper lines, ~40 facade lines and
200–350 direct test lines, plus narrow docs/skill metadata. No runtime begun.

Exact focused compatibility selection: tests/test_public_session_wire_guards.py, tests/test_public_session_version_relabel.py, tests/test_exp_session_evidence_compat.py, tests/test_exp_feedback_derivation.py, tests/test_rf8_sessions.py, tests/test_public_retained_session_results.py, tests/test_packaged_skills.py. All are local credential-free controls.

## Corpus-driven amendment (2026-10-20)

Expanded corpus observed two failures before repair: asserted overflow lacked its
explicit status; a valid but indeterminate exact-term check reported all computed
counts not-evaluated instead of preserving actual unavailable state. Add explicit
asserted_status. Valid checks with exits0/1/2/4 may calculate diagnostic structured
counts; exit4 still discards cache candidates under the unchanged session policy.
Input/error exits3/70, references and unsupported calculations remain not-evaluated.
This adds no acceptance or truth claim and does not alter the check report. Full
feedback construction failure must leave generation/attempt unchanged. Byte-bound
reader rejects oversized encoded input before parsing; semantic model validators
also enforce shape/coherence and canonical output bound. No wire was published.

## Independent-review repair contract (2026-10-20)

Three findings reproduced in five RED variants: a cancellation immediately after
feedback computation consumed an unreturned attempt; defaulted discriminators
invented missing tags; duplicate version keys collapsed before strict validation.
Require explicit kind/version/operation and use existing input_policy.loads for
finite/depth/duplicate-key policy before schema parsing, under the16KiB byte cap.

Publish cache entries, binding/size, generation and bounded lifetime attempt
sequence through ONE private committed record/reference in ReuseState. Validate
the optional next sequence under the existing owner lock. A completed feedback
error may publish only the new sequence while retaining old cache generation;
exceptions before that publication point publish neither. Remove the separate
facade counter. Reset/close replace the committed cache record while preserving
lifetime generation/sequence. Keep private compatibility read properties for the
existing bookkeeping fields. Sequence is one bounded control-plane integer, not
retained cache content/history. The state home imports no API/exp modules.
This also removes the prior multi-assignment cache publication window. Add the
existing state isolation/caps/rollback regressions to IE4's final gate and bounded
confirmation scope. No third review. No other milestone scope changes.
