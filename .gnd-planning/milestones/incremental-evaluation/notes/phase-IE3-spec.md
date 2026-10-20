# IE3 — Selective constraints, public sessions and receipt integrity

Owner-decided under delegated auto approval, 2026-10-20. IE2 accepted in 005 / 46c76ad. Derives from approved plan IE3-C1..C3, IE-O1/
O3/O5/O8/O9/O12/O13 and prior TP3 mutable report carryover. The complete envelope
is a prerequisite; the prerequisite has been met.

One constraint finding is the reuse unit. Extract the existing evaluator loop
body into its defining helper, keep adaptation, correspondence_scope, ordering,
band composition and projection fresh. Inline uniqueness can key its complete
constraint/fact metadata and selected ordered relation (including non-key witness
cells and refusals), alias and finite/mode flags. Other non-effectful constraints
key the complete immutable semantic snapshot. Reference/shared work and clock/
observer modes remain fresh; no missing ownership edge implies eligibility.
FAMILIES remains the sole family registry and existing refusal order remains.

Use the existing bounded fingerprint engine to add trusted gnd dataclass record
support (type identity and every field), rather than introducing another key
serializer. Preserve existing typed primitives/order, cumulative node/character/
depth/cycle limits and bounded failure. Store detached semantic findings, never
public witnesses already projected to stale observation positions. Replay branch
identities and assemble fresh report counts; actual evaluator events remain the
performance instrument. Model/operations bindings and resource/rollback ownership
remain IE1-owned.

Add opt-in api.EvaluationSession above checker/state:
constructor(model: Model, *, max_rows=100000, max_bytes=33554432);
check(population: Population, *, compiled_operations=False, unredacted=False,
anchors=None, document=None, population_bytes=None, admission=False,references=None);
check_with_receipt(population, *, unredacted=False);
transition(pre, steps, post=None, *, unredacted=False,references=None,pre_receipt=None);
reset(), close(), stats(). Loaded inputs only at the facade; call normal public
API orchestration under state transaction. Shared semantic binding between check
and transition avoids accidental reset. Unsupported semantic modes run fresh.
Error/uncheckable payloads discard candidates; completed violations may publish
without making them eligible for TP3 receipts. Closed/busy/foreign ownership
remain named refusals. No cache handle serialization or default API activation.

Mint a separate private deep copy of CheckReport for receipt transition use;
public .report compatibility retained but cannot alter the consumed snapshot.
Private field excluded from repr/equality; clone failure produces a nonreusable
receipt without changing payload. Preserve existing receipt refusal order,
exit0/2/default/nonanchored eligibility and branch replay. Source-owned public
exports and installed-export assertions explicitly acquire EvaluationSession.
Historical IE0 mutation evidence remains old evidence; update the current probe
and its regression expectation to assert protection after repair.

Corpus before code: current receipt mutation RED; facade absent RED; full/session
payload+exit+branches+lineage parity including computed and declared post, marker
loss/model edits/options/references; root/intermediate/post obligations retained;
inline independent/noop evaluator-zero checks, ordered witness origin edits,
roster/coverage/refusal changes for complete-snapshot fallback, returned payload
mutation, tiny bounds, cancellation/reset/close/busy, reference/anchored fallback,
exact reporter <4878 bodies with the same13-call receipt replay. Old special lanes
remain excluded. No receipt exception duplication repair without actual repro;
otherwise explicit named hardening residual.


## Harvest / standing rules

| Source | Discharge |
|---|---|
| IE3-C1, IE-O1/O12; §9 | complete check/transition payload, exit, witness/origin, ordering and branch parity; final aggregation/projection stays fresh |
| IE3-C2, IE-O4/O8/O13 | current typed snapshot/model/operations/options keys; marker/receipt validation never waived; receipt private detached report |
| IE3-C3, completion4, IE-O3/O5 | public opt-in facade, independent/no-op evaluator counters, same13-call reporter strictly <4878 bodies with complete parity |
| §0 IE-R1/R3 | normal API admission/root/intermediate/post checks retained; original refusal order and payload builders |
| IE-R2/R4/R8 | IE1 fresh model scope, private staged generations/clone/caps; error payloads explicitly discard; private consume copies |
| IE-R5 | actual evaluator profiler and separate state stats, logical findings/report counts preserved |
| IE-R6/R9 | same registry/FAMILIES and existing evaluator helper; one bounded fingerprint home with trusted record support; exact source/query/alias controls |
| IE-R7/R10 | explicit constructor only; ordinary API/CLI defaults; no publisher, paid/native/reserved lane or certification |
| §5; public API pin inventory | __all__, public/reference signature tests and installed-export assertion update; no packaged skill selected |
| §6 stale witness/refusal/clock risk | snapshot scope includes all dependency fields or uses fresh fallback; current projection, effectful reference/clock modes fresh |
| §10 D1/D2/D3/D7/D8 | opt-in facade and default fresh modes, current receipt limits, frozen counted target and IE1 memory ownership |
| IE0 003, IE1 004, IE2 005 | historical source identities remain historical; IE0 report-mutation vulnerability repaired here; small-fixture overhead remains IE5-owned |
| prior TP3 close | preserve refusal order and all snapshot checks, separately investigate mint exception duplicate work via reproduction; no invented fix |

Process standing rules: corpus before predicates, explicit metadata/key homes,
actual work rather than labels, shared bounded fingerprint and registry dispatch,
reproduce review findings before repairs, and source/compatibility disposition.

## Design details and decisions

Single-constraint helper in correspondence (~150 moved / 50–100 new lines):
`_evaluate_constraint(adapted, constraint, aliases, reference_work)` returns the
existing `CorrespondedFinding`. Reuse happens at the caller loop; direct defaults
run the same helper. Key the selected complete fact/relation plus constraint and
finite/refusal metadata for inline uniqueness; all other demonstrated non-effectful
units use full SnapshotIR. ReferenceJoinWork and guarded clock/effectful units
select fresh; unsupported key/clone falls back under IE1. Bind actual helpers,
registry entries and alias at defining lookup homes. No second family dispatch.
Final correspondence_scope and band/projection run even on all hits.

Fingerprint change (~15–25 lines) extends existing _Fingerprint.freeze for trusted
gnd dataclass instances, preserving class identity and all fields under the same
node/character/depth/cycle guard. Foreign or malformed records refuse safely.
No separate serializer or magic repr identity. Semantic records are not authority.

API facade (~100–160 lines) calls existing check/check_with_receipt/transition;
loaded Model/Population only, steps retain existing mapping/path support. Exact
method keywords are those listed above, forwarded without relaxing validation.
`stats()` returns existing integer counters/entries/rows/bytes/generation; reset
and close preserve IE1 refusal/lifetime rules. Unsupported references/anchoring/
observation modes execute through a deliberately disabled cache transaction,
retaining busy/closed/rollback policy. Default check/receipt/transition share one
semantic binding; compiled/admission/options changes reset or fall back. A normal
payload with exit0/1/2 may publish reached units; error/uncheckable exits discard.

Receipt (~20–35 lines): mint deep private report copy excluded from repr/equality.
Consumer obtains another detached copy so even a direct transition report cannot
expose private authoritative storage. A mint copy failure yields nonreusable receipt;
a consume copy failure computes the ordinary pre-check fresh. Public .report
remains mutable for compatibility but cannot affect consumed state. Branch replay
and existing eligibility/refusal order remain, not a new bypass.

D1 delegated: optimize inline uniqueness precisely, complete-key other safe units;
unknown/effectful scopes fresh. D2 delegated: explicit loaded-input facade above
checker. D3 delegated: private report copy and detached consumption with fresh
fallback. D4 delegated: existing dataclass fingerprint engine extension only.
D5 delegated: required one CLI reader plus at most one confirmation; code-based
reproduction, no third review. No optional paid/panel review selected.

Implementability sweep: all finding outputs are existing frozen GND records that
IE1 can clone; complete semantic IR is finite and acyclic under existing adapters.
Fresh snapshot keys conservatively cover otherwise unclassified scopes. Per-call
API orchestration remains intact. Loaded mutation errors can be detected from the
returned payload and explicitly abort staging. No requirement implies reusing an
unvalidated population or omitting a root/intermediate/post check.

## Corpus / verification selection

Stories: session-stories.json; separate answers: session-answers.json. Existing
RED corpus has absent-facade, mutable-receipt consumption and unsupported trusted
IR key controls. Further branches are declared in stories before implementation;
all must obtain actual discriminating controls before IE3 acceptance.

| Obligation | Disposition | Exact selection / invalidation boundary |
|---|---|---|
| facade/constraint/receipt new predicates | run | `UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline pytest -q tests/test_incremental_sessions.py tests/test_incremental_state.py tests/test_incremental_state_review.py tests/test_incremental_extensions.py tests/test_incremental_extensions_review.py`; exit0; source, new corpus and fixture changes invalidate |
| receipt and public signatures | run | same prefix `pytest -q tests/test_tp3_check_receipts.py tests/test_public_api.py tests/test_public_reference_signatures.py`; exit0; api/transition/exports/receipt changes invalidate |
| current correspondence, applicability and projections | run | same prefix `pytest -q tests/test_public_correspondence_runtime.py tests/test_public_correspondence_projection.py tests/test_public_semantic_applicability.py tests/test_public_semantic_counting.py tests/test_public_semantic_mandatory_union.py tests/test_public_semantic_guarded_join.py`; exit0; evaluator/fingerprint/IR changes invalidate |
| compiled/root/intermediate/post controls | run | same prefix `pytest -q tests/test_compiled_snapshot_obligations.py tests/test_compiled_snapshot_boundaries.py tests/test_public_transition_contract.py tests/test_public_transition_api_guards.py tests/test_public_transition_review_controls.py`; exit0; transition/check orchestration changes invalidate |
| layer/query/alias/registry/fingerprint consumers | run | same prefix `pytest -q tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf3_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf7_structure.py tests/test_rf9_ci_repairs.py tests/test_m3_extension_preparation.py`; exit0; source/helper/successor changes invalidate |
| current mutation-probe/IE0 discriminator | run | focused baseline mutation test nodes and new integrated reporter differential; update current expectation, preserve old artifact bytes; exit0 |
| lint | run | same prefix `ruff check` on changed runtime/test/tool helper paths; exit0 |
| full/historical/native/provider/installed broad | cadence | explicit owner/selected CI only; IE5 owns bounded installed candidate/public assertion; no inherited current certification claim |

Current source-successor inventory has no pins on these four main definitions;
checking_service._run_check[_raw] would require successors if touched (not planned).
Exact dynamic successor chains after IE2; raw model-query rows move only with
honest owner deltas or existing ModelIndex (no new blanket allowance).

## Size / out of scope

~200–320 new runtime lines plus ~150 moved, 300–500 new/expanded direct test lines.
Measure actuals at acceptance. IE4 observation contract/feedback and IE5 profile/
installed/docs remain separate mandatory phases. Existing overhead is an explicit
IE5 performance question, not an elapsed-time success. No 547 workload, delivery
date, certification, publication, paid/provider/native acceptance or merge.
