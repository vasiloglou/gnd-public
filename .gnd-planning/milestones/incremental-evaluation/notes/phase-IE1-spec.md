# IE1 — Trusted state and conservative invalidation

Status: delegated gate prepared after completed IE0; runtime not implemented.

## Provenance

Approved plan r2 §§0–10, owner gate 001 and execution delegation 002.
IE0 completed in 003 / commit 67e36fa; its strict baseline and 49-test gate passed.
Prior TP1/TP3/repairs phase-13 and prior close boundaries remain as harvested
in the plan. This spec has no review opinion or approval hash yet.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan IE1-C1 / IE-O2 | one dependency walk, SCC closure, polarity and implicit scopes | Dependency contract and corpus C1–C4 |
| IE1-C2 / IE-O4 | model including operations, facts/order/claims, options, references and marker changes cannot stale-hit | Boundary and corpus C5–C9 |
| IE1-C3 / IE-O13 | private detached state, one generation, caps, reset/close, overlap refusal and exception rollback | Transaction contract; C10–C15 |
| IE1-C4 | freeze eligibility/targets before extension code | IE0 evidence prerequisite and branch matrix |
| §9 IE1 | dirty closure covers all dependency kinds; mutation never stale; caps/rollback/isolation | all corpus cases and direct tests |
| §0 IE-R1..R10 | parity/admission, ownership, counted work, layering, opt-in, bounds and protocol | standing-rule bindings below |
| §5 / IE-O10 | public/query policy and source-scan pins | layer map/new home; focused selection |
| §10 D1/D2/D7/D8 | session direction, cross-call permission, targets and cache budget | owner plan gate accepted direction; exact accounting below |
| prior close rows 3/8/13/17 | receipt mutation, outer scope, policy pins and approved spec before code | no receipt reuse yet; fresh model key, selected checks and separate gate commit |

## Standing rules

IE-R1/R3: no evaluation skipped here; admission remains callers' existing check.
IE-R2: compare a fresh content key independent of outer ModelIndex scopes.
IE-R4: private staged/committed generations; caller results cloned by the defining
algorithm's explicit clone function. No public mutable map of cached values.
IE-R5: statistics separate from reports; count reused/recomputed/bypassed units.
IE-R6: new `gnd.incremental_state` is checking-layer support, importing model,
ModelIndex, branches and preparation primitives only, never API/experiment code.
IE-R7: no default activation; a ContextVar exists only during an explicit owner
transaction. IE-R8: one previous generation plus one in-flight candidate; global
sum of retained input/value size bounded, no historical population list.
IE-R9: total fingerprint refusal of arbitrary shapes; bounded tree walks;
validation order below; one dependency graph walk; this spec is its design home;
measure contested size/identity behavior with corpus, not prose assertion.
IE-R10: no private input, broad/native lane, publisher or certification.

## Goal

Direct invalidation and transaction corpus exits 0; deliberately stale/aliased
and unbounded implementations fail. No production evaluator uses the cache yet.

## Design (proposed; implementability subject to IE0 census)

New checking-layer `src/gnd/incremental_state.py` (200–300 lines):

```python
class ReuseState:
    def __init__(self, model: Model, *, max_rows: int = 100_000,
                 max_bytes: int = 32 * 1024 * 1024): ...
    def transaction(self, model: Model, *, options: tuple = ()) -> ContextManager: ...
    def reset(self) -> None: ...
    def close(self) -> None: ...
    def stats(self) -> dict[str, int]: ...

def active_state() -> ReuseState | None: ...
def affected_heads(model: Model, changed: Collection[str]) -> frozenset[str]: ...
```

The runtime protocol is an internal method:
`reuse(namespace, unit, snapshot, calculate, *, policy=(), rows=0)`.
State owns bounded cloning/accounting; the defining algorithm supplies the full
input projection, actual helper policy and an integer row count or row-count
callback. Support state never imports the algorithms it caches.
A unit key is unique within its namespace and current model/options binding.
Inputs include ordered facts and origin coordinates, not only set membership.
Unrepresentable fingerprints bypass, never coerce values/keys or collapse bool/int.

Boundary order: reject closed → refuse overlap → require same model object →
compute fresh ModelIndex content key using its uncached-scope lookup → compare
model/options binding and cold-reset if changed → own isolated transaction.
This fresh lookup must not trust a caller-held scope hit. Invalid/no key bypasses
reuse. A callback exception restores the prior committed generation and ContextVar;
no new generation is published. A normal completed operation publishes only the
units actually reached in the candidate. Reuse within the transaction may consult
current candidate first and the one prior committed generation second.

Unknown dependency/shape means recompute. `affected_heads` obtains the existing
positive/negative/aggregate graph; starting at each changed asserted or derived
fact, propagate through reverse edges to all transitive heads and complete SCCs.
This is diagnostic selection, not authorization to ignore unclassified constraints.
Object roster/coverage/options/reference changes invalidate the constraint namespace
in full until IE3 demonstrates a narrower complete scope. Unsupported semantic
modes remain full-evaluation paths; IE1 does not imply their eligibility.

Resource proposal: bounds cover both committed and staged retained representations,
including fingerprints and output values, not just row payloads. A single entry
that cannot be measured/cloned safely is not stored. If a candidate would exceed
its cap, evaluation still completes fresh, candidate storage is disabled, and
oversized state is not retained. Counters expose this bypass; do not evict into a
new hidden history. Exact size projection and cap edge corpus must be fixed before
the gate. The caller never receives a retained mutable value directly.

## Decisions

Pending delegated disposition after IE0:

- D1 corpus-first instrument; separate stories and answer key committed RED
  before runtime, then hash-bound approval under the owner's auto delegation.
- D2 reject overlap rather than serialize shared-session calls; independent sessions allowed.
- D3 model/options change cold-resets; other model object and closed use refuse.
- D4 exact accounting and bypass policy as above, including both retained generations.
- D5 classify only demonstrated reusable modes; all unresolved modes evaluate fresh.

## Corpus and test branches

Entry stories: proposed `tests/fixtures/incremental_evaluation/state-stories.json`;
answer key: separate `state-answers.json`. Both absent until IE0 prerequisite is
satisfied. Direct `tests/test_incremental_state.py` will exercise:

| Case | Expected outcome |
|---|---|
| C1 positive dependency and transitive chain | all dependents dirty |
| C2 negative and aggregate edges | both propagate invalidation |
| C3 recursive SCC from one member | entire SCC and dependents dirty |
| C4 unknown/implicit constraint scope | fresh, no permission from absent edges |
| C5 nested model mutation | no stale hit |
| C6 operations-only change inside outer index scope | fresh content key/cold reset despite old scoped hit |
| C7 facts delete/replace/reorder; claims | changed input key misses; no set-based shortcut |
| C8 rosters/covers/options/references | invalidate relevant namespace or full fallback |
| C9 marker lost | existing public admission still refuses; cache cannot mint validation |
| C10 mutable returned value | subsequent result unchanged |
| C11 exception/cancellation | candidate discarded, prior generation intact |
| C12 reset, close, closed use | entries cleared; closed reuse refused |
| C13 overlapping same session | named refusal, independent sessions unaffected |
| C14 row/byte cap at/below/above edge | bounded retention and fresh fallback |
| C15 unsupported/cyclic/deep input | bounded bypass, no traceback/stale hit |

Every accepting branch needs its rejecting sibling. Time-bound tests exercise
fingerprint/state/dependency walks on bounded inputs and assert cap units. Core
comparison of fresh payloads remains IE0's oracle; IE1 skips no evaluator.

## Verification selection

Exact run commands, before the gate:

- `UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline pytest -q tests/test_incremental_state.py tests/test_rf6_index.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_popvalidate.py` → 0.
- New module assignment/source scan: applicable current RF4/RF6/RF7/RF9 nodes
  must be selected after inspecting their module inventories; exact additions
  unresolved, so no gate approval yet.
- `UV_CACHE_DIR=/private/tmp/gnd-ie-uv-cache uv run --offline ruff check src/gnd/incremental_state.py tests/test_incremental_state.py` → 0.

Boundaries: new state module, layer map, source-scan inventories and direct tests.
Source/policy changes invalidate this selection. Historical full suite stays on
explicit owner/CI cadence; native/provider/certification lanes remain unselected.
No prior test pass is inherited onto changed bytes.

## Out of scope, size and approval

No extension/constraint skipping, API/session wire, receipt fixes or experiment
hooks in IE1. Estimated 200–300 source lines, 250–400 tests and 15 stories.
Corpus-first is required here because invalidation and cache-acceptance predicates
are the deliverable. This draft is not its approval and cannot authorize code.

## Implementability refinement (still draft, no gate or code)

Use a new public-internal `independent_index_scope(model)` in model_index.py:
always enter a fresh ContextVar scope, compute one current ModelIndex and seed
that scope for nested public calls, then restore the previous outer scope.
Existing index_scope/scoped defaults and signatures remain unchanged. This
avoids both stale outer hits and a second key dump inside API evaluation.
The graph reader uses the current index's read-only fact-type rows with the
existing dependency parser, then one reverse-edge worklist. Unknown changed
subjects conservatively dirty every structured head. SCCs close through their
existing reciprocal edges; negative and aggregate edges use the same walk.

The reuse method will be `reuse(namespace, unit, snapshot, calculate, *,
policy=(), rows=0)`. Signatures preserve builtin type/order through the existing
fingerprint function. Reusable values use one bounded state-owned deep-clone
walk over primitives, exact dict/list/tuple/frozenset/MappingProxyType and gnd
dataclasses. Unknown values, cycles or limits bypass; None is a supported immutable value; an unsupported sentinel is distinct from None. No defining-algorithm clone callback may return a caller-owned mutable
container as cache proof. Byte measurement uses bounded object-graph accounting
of owned representation, with declared shallow module/function policy handles;
row accounting is the defining algorithm's internal explicit unit count.
Measure before cloning so oversized output is not copied just to reject it.
Committed and candidate entries are charged together, deduplicating shared entry
objects only. Candidate cap overflow disables storage and publishes no oversized
state, while full evaluation continues. Each namespace/unit keeps only its most
recent candidate signature; different snapshots cannot create a hidden history.

Exact syntax-census additions will be an authenticated successor under this
milestone evidence, chained after the existing maintenance dynamic-query
successor. Extend the test helper's successor list instead of rewriting historical
query evidence. No new raw model-query allowance is needed.

Focused impact additions: test_rf4_peripheral.py, test_rf6_packages.py,
test_rf7_structure.py and test_rf9_ci_repairs.py, in addition to the direct/query/
index/layer/popvalidate files named above. Default lane exclusions remain.

## Final gate refinements and delegated decisions — 2026-10-19

IE0 dependencies are discharged by 003. State C1–C15 stories and their separate
answers are authored, as are direct tests. Before runtime, the selected corpus
pytest invocation exited 2 at collection because gnd.incremental_state does not
exist. This is the expected RED prerequisite, not a passing test or per-case
semantic proof. Commit these bytes before writing runtime.

Delegated approval (auto=true), owner invocation in 002: D1 corpus-first;
D2 nonblocking overlap refusal; D3 model/semantic-options changes cold-reset and
foreign model/closed use refuse; D4 bounded representation accounting below;
D5 unresolved semantic routes remain fresh. Optional spec panel omitted; required
phase diff review remains the authorized Codex CLI stdin/read-only/xhigh harness.

Private clone/measurement walks have depth 64 and 100,000 visited-node bounds;
unknown, cyclic and nonfinite values bypass storage. Cache budgets are owned
entry/key/signature/value/branch representations (sys.getsizeof graph accounting),
not a claim to cap interpreter/module/model/caller-output memory. Module code/type/
function policy handles are counted shallowly and never recursively traverse globals.
Input/output representation is measured before cloning. One committed generation
and one staged candidate are charged together; the same retained entry reused
in both maps is charged once. A cap overflow disables candidate storage and clears
retained entries on successful completion, while semantic evaluation still runs.

Cache unit identities preserve builtin type/order. Policy keys include calculation
code plus explicit helper/function/code references and typed primitive policy
values; changed helper code cannot masquerade as an old evaluator. Snapshot
fingerprints use the existing single-home preparation primitive. Error order:
closed, busy, foreign model, independent current index binding, scoped candidate.
Only successful normal exit publishes; BaseException discards candidate.
No operation outside an owning active transaction can use retained state.

The exact selected gate is the earlier direct/index/query/layer/popvalidate command
plus `tests/test_rf4_peripheral.py tests/test_rf6_packages.py
tests/test_rf7_structure.py tests/test_rf9_ci_repairs.py`. New module and independent
index scope are their impact surface; default exclusions remain unchanged.
The dynamic syntax census is extended by an exact authenticated successor, not
by changing old counts or granting model query waivers.

Implementability: fresh independent scope can seed nested API lookups once;
reverse dependency traversal uses existing graph extraction; trusted gnd dataclasses
and builtin containers suffice for retained component/finding outputs. All
other outputs may safely miss. Zero default evaluators are skipped in IE1.

## Implementation findings / corpus correction (a1)

The dependency parser's document shape requires a list of fact types; passing
a tuple yielded an empty graph. The live C1–C4 corpus caught it and the graph
projection now uses the required list, without copying or rewriting the parser.

C6 initially tried assigning `m.operations=[]` after construction, but Model's
outer fields are frozen. That fixture premise was invalid, not an invalidation
defect. Delegated amendment (auto=true), 2026-10-19: construct the model with an
operations list before entering the outer scope, then mutate that nested list.
This is the actual CR-01 operations-only case; expected outcome stays unchanged.
The initial RED and subsequent fixture/runtime failures are retained as outcomes,
not claimed passing corpus evidence. No Model immutability rule is relaxed.

Entry accounting includes a conservative 1,024-byte per-entry metadata allowance
for the record and both index slots, in addition to measured owned key/signature/
value/branch graphs. Global function/code/type objects are borrowed 8-byte handles,
never traversed into globals. This is a cache accounting bound, not process RSS.
Unmeasurable/unsupported metadata safely bypasses reuse and cannot change a
completed evaluator result. Exact cap-edge behavior is tested on this accounting.


### Review repairs (2026-10-20, existing auto delegation)

Five independent-review reproductions were observed RED before repairs. Transaction authority now uses a unique live capability scoped to its thread and task; copied expired contexts cannot enter later generations, and expired independent query scopes drop their snapshots. Options and backing container storage are charged to the same byte bound as entries; close releases bindings. Shared policy tuple DAGs refuse reuse before expansion or hashing. Dependency classifications must be complete before diagnostic invalidation selection. These tighten the approved bounds without activating runtime skipping. The retained CLI review and RED evidence identify the exact findings and limitations.

Confirmation repairs (2026-10-20): measure the detached retained clone, charge changed bindings together with committed entries before yielding, and refuse opaque/nonmapping derivation rules. Source walkers iterate dictionary children lazily rather than allocate an unbounded flattened tuple. Three confirmation regressions observed RED then green. Round budget exhausted: three of three confirmation findings concern first-repair bytes (ratio 1.0); no third review under convergence rule. Actual direct gates, not a fabricated reviewer approval, support disposition.
