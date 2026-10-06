Status: owner-decided (2026-10-05); delegated approval (auto=true).

# RF6a -- Model queries and constraint-family dispatch

## Provenance and harvested obligations

Base 523cdd1a2ae1ad6ea0e8ca092fe29629dd10607c; effective notes/code-refactoring-plan.md (approved r2 plus e1), sections 0,4,5,6,7,9,10 read in full. 003 gate and 005 erratum retained. Read-only delegated readers covered the plan/reviews, every prior record 004--010 and current production/test/skill tree; their rows were checked at the named anchors. Plan authorship and old panel opinions are not opinions over this spec.

| Source / obligation | Discharge |
|---|---|
| Plan319--325: read-only digest-cached ModelIndex; id, role type, supertype, primitive, canonical constraints; six-hook family registry before split | Design; query and registry branch tests; RF6b follows RF6a record |
| Plan327--335 RF6-C1--C4; SM1--SM4 at105--112 | Exact query-read allow-list; fake extension; mutation/cache cases; RF6b imports and measured split |
| §9 verbatim: RF6 / SM1–SM4; registry extension test; index staleness test; split budget / Checker families, verbalize, semantic adapter controls | G0--G5 below; each part records only its results |
| RF-R1--11 (§0) and six standing rules | Rules below |
| §5 skill sites | Seven literal matches/five files, of which gnd.model_verbalization substring and parser-budget comment are not imports. Real sites: orm-core/SKILL.md52; representation-format810,1295,1391; recovery-contract257. Public aliases retained; split updates physical-file citation atomically. |
| §6 risks | Golden bytes, observed patches, complete scans, graph guard negatives, bounded budgets; stale release identity unavailable |
| §7 all exclusions | Boundary below |
| 002-panel86 + r2 review54,59: exact cache key and range rename | D2,D3 |
| 006:195--211 RF1-OQ1 import pins owed | Before RF6b capture every current model/checker public and private import binding, symbol identity and behavior; negative deletion control |
| 007:533--539 RF2-OQ2 PyRel boundary and shim retirement | D4,D5 |
| 008:387,398 RF3-OQ2 model organization | RF6b preserves reference intake validation/identity order |
| 009:305--338,010:217--223 inheritance | Focused current-byte claims only; old certificates unavailable; source-owned files frozen; RF7/RF8/close ownership retained |

## Standing rules and design rules

RF-R1 preserves names, verdicts, issues/order, bytes/digests/refusals. RF-R2 encoder bodies unchanged, variants never unified. RF-R3 existing observation pins run before routing, new query/registry branches get direct cases. RF-R4 extraction-only move units precede routing edits, aliases and patches/scans travel atomically. RF-R5 every moved/renamed binding inventoried, no retirement. RF-R6 source observers cover complete introduced scope with a negative omission test. RF-R7 frozen units.json and distribution authority test; prior source control is earlier attestation, not a new human attestation. RF-R8 new production identity invalidates historical certificates. RF-R9 measured budgets below. RF-R10 no semantic family shipped; fake family only in isolated test. RF-R11 impact selection measured, not full default replay.

Standing totality: query factory accepts Model only, malformed nested data bypasses caching and keeps historical helper errors rather than adding canonicalization refusals; adapter remains total over arbitrary JSON. Complexity: bounded cache32, linear build plus existing cycle-safe traversal, timed large model test. Validation order: retain common adaptation/refusal prelude and loader order; source-order and behavioral pins. One policy walk: registry chooses family behavior from one entry, with shared prelude/refusals. One normative prose home: existing representation/constraint contracts remain authority. Measurement over argument: pre-move pins, cache mutation cases, negative instrumentation controls and branch coverage.

## Goal and design

RF6a G0--G5 exit0; outside-model query sites decrease from measured320 to at most310, with every retained occurrence separately identified and reasoned. RF6b owns physical package split and module size targets; it gets its own spec approval after RF6a is recorded.

src/gnd/model_index.py (~230 lines): frozen ModelIndex, snapshot fields private, detached returned dictionaries; classmethod for_model(model: Model) -> ModelIndex, property digest: str, fact_type(id: str) -> dict | None, object_type(id: str) -> dict | None, role_object_type(fact_type_id: str, role_name: str) -> str | None, supertype_closure(id: str) -> frozenset[str], primitive(id: str, *, variant: Literal['truthy','strict']) -> str | None, iter_constraints() -> Iterator[tuple[str,dict,dict | None]], object_types_by_id() -> dict. Each factory request recomputes key; no object-id-only cache. Bound32 LRU over detached snapshots. Key sha256 of existing artifacts.canonical_json_bytes over full model_dump(exclude={'warnings'}), including operations and references; this is an internal marker, not one of three existing public digest contracts. Noncanonical/hostile models take uncached path, preventing new digest errors in callers; original helpers remain for hostile non-dict rows. Returned views never mutate index state. Existing strict/truthy resolver reused, no new resolver semantics.

src/gnd/constraint_families.py (~170 lines): frozen Family entry with adapter, evaluator, witness, message, scope and implemented hooks. Hook names resolve in the caller's defining namespace, or test-only callable supplied directly; no importlib/dynamic invisible dependency. Registry maps admitted families to entries; all production entries and hook resolutions validated. Family-specific branches extracted verbatim into local handlers before dispatch rewiring. Shared adapter and presentation refusal/vacuity order remains before family dispatch. Existing branch evidence registry stays separate. Unknown families preserve predecessor refusal/fallback. Test fake entry must drive all six surfaces by changing only registry, without editing dispatcher inventories.

Existing universe query helpers route only compatible Model inputs through index; historical malformed SimpleNamespace/document helpers preserve shape and policy. Checker constraint walks consume canonical index rows. Identical model lookup families merge only after pre-existing helper pins exit0. value_domain._in_range becomes public in_range with old alias and historical metadata; body unchanged, callers routed afterward.

An exact query allow-list names file, enclosing symbol, expression, occurrence count, reason and removal owner. Retained reasons distinguish raw intake/serialization, IR snapshot reads (different model), standalone emitted PyRel boundary, and deliberately deferred domain traversal. No blanket package exemption outside model/index. Every allowed read must be live; missing/extra counts fail. Negative controls add a read, remove allow-list row and add stale unused entry. Raw subscription/dynamic reads are separately inventoried, not hidden in AST count.

## Decisions -- delegated approval (auto=true), 2026-10-05

Authorization: owner invoked process-phase RF6 auto. These are agent rulings under delegation, not human reading.
D1 prose approval instrument: no new serialized format, exit contract or validation semantics; existing RF1 outputs remain frozen. Pre-routing observation controls plus separately identified red successor tests provide executable instrument; no changed corpus answers authorized silently. Optional spec panel omitted; required independent diff review per part retained, max initial+one repair each, convergence reference applies.
D2 full-model internal canonical digest, separate from public identity meanings; uncached fallback avoids stricter admission. Mutation of operations/references and outputs from index covered, not only fact types.
D3 rename in_range with live old alias under RF-D8/D10; unchanged bytes/message inputs.
D4 preserve standalone PyRel runtime and emitted bytes; consolidation requiring runtime GND dependency deferred to separately scoped export-format successor (RF2-OQ2).
D5 all old shims retained through first public release after RF6 plus separate retirement approval.
D6 no new attestation or certificate fabricated; original source-side control remains bounded as recorded in RF5. Authority bytes frozen.
D7 budgets: RF6a <=120 touched files, <=2500 added test/data lines, <=1500 non-evidence docs lines, <=4000 moved production lines and <=2200 nonrelocated production lines. Numeric query target320→310. Any overrun recorded before expansion; no silent retarget. RF6b later sets current-base budgets.

## Tests and verification selection

| Gate / disposition | Exact command and expected exit | Input boundary / invalidation |
|---|---|---|
| G0 run before production | .venv/bin/python -m pytest -q tests/test_rf1_semantic_pins.py tests/test_checker_families.py tests/test_public_semantic_adapter.py tests/test_rf3_core.py --tb=short; 0 | pre-routing semantic bytes, helper and adapter behavior; any dependency changed invalidates |
| G1 run | .venv/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_query_policy.py --tb=short; 0 | direct new branches, negatives, cache/staleness, six-hook extension and time bound |
| G2 run | .venv/bin/python -m pytest -q tests/test_rf1_semantic_pins.py tests/test_checker_families.py tests/test_public_semantic_adapter.py tests/test_rf3_core.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_ring_frozen.py tests/test_vacuity.py --tb=short; 0 | current-byte downstream semantic/query consumers; no excluded override |
| G3 run | .venv/bin/python -m pytest -q tests/test_rf1_pin_harness.py tests/test_rf1_layering.py --tb=short; 0 | frozen golden identities and complete six-layer graph; negative controls |
| G4 run | .venv/bin/ruff check <explicit changed Python files>; 0; .venv/bin/python tools/gnd_arch.py measure --out <fresh phase metric path>; 0 | map, AST/source inputs and budgets, changed docs/discovery controls where affected |
| G5 run | focused current affected consumers discovered by import/query inventory, explicit node/file list retained before execution; 0 | changed implementation dependencies; reconsider on each lane |
| inherit | frozen encoder bodies and prior source-owned authority are byte-checked, prior verdicts describe prior bytes only | any change removes inheritance; selected current controls run |
| cadence | full default, evidence/census, proof/distribution/native/external, certification and exhaustive v5.1 replay; explicit owner request or separately scoped CI | old results unavailable over changed inputs; none selected by this invocation |

Direct branch table: cache hit/miss/equal distinct models/all nested sections mutated; index output mutation; duplicate ids first-vs-last legacy lookup; missing ids/roles; cycle/multiple inheritance; truthy vs strict; constraint inline/top-level order/ref; malformed/noncanonical fallback; bounded eviction; unknown primitive variant; all existing families six-hook resolution; fake all-six extension; unknown family; unimplemented/textual; empty/refused/common prelude; stale allow-list/missing scope/new read; instrument dirty controls. Expected exits0 except deliberately observed pre-implementation red cases and negative controls internally asserting refusal.

## Implementability sweep

Every criterion has satisfiable implementation: digest covers all query inputs, fallback avoids new raw-shape admission; exact allow-list permitted by RF6-C1 retains distinct IR/standalone/raw serialization reads, central query routes yield strict reduction; local named hooks avoid backward graph edges; package split follows index/registry, aliases cover all imported symbols. Fake family tests are internal, not public schema extension. Required native review may technically refuse; no subagent substitutes independence.

## Boundary

No new semantics/commands/flags/schema/version, strictness, performance claim, variant merger, broad historical repair, new acceptance/certification/publishing or source-owned transfer. One reviewer is one reviewer. Local selected results do not establish other OS/installed acceptance. RF7 strictness, RF8 sessions, milestone-close wording/helper questions and source-owned OQs remain owned there. Prior source control is not a new human attestation. Original corpus meanings/bytes stay unchanged.

## Implementation findings

Append findings and amendments here as observed; no original approved requirement rewritten silently.

### A1 -- pre-production corpus literal and historical metric, delegated 2026-10-05

G0 observed509passed/1failed: RF3 original scope/private-count predicate expects64, current baseline evaluates242 before RF6. The exact failure was reproduced from git archive of base523cdd1 with its own src PYTHONPATH; no historical repair selected. G0/G2 use all other RF3 controls and current full layer/map/SCC successor in G3. Initial novel index cases11red because module absent. Before production, corrected expected inline address F.constraints[0] to existing positional_constraint_ref's fact_types[F].constraints[0]; original answer retained in index-red output. This is an authored successor-test defect, not a change to any RF1 golden. Delegated amendment applies before implementation.

### A2 -- source location successors, delegated 2026-10-05

G2 observed639passed/1failed/1deselected. The failure is the original mutation source snippet precondition after query routing: 167 row identities/expected-red meanings are retained. M-SEM-resolver-is-true moves its file to model_queries.py with old/new snippets identical. Two exception-injection helper rows now anchor their original unique function header (same inserted rf1-mutant raise) because dispatch precedes the historical return comprehension. Original complete rows retained in mutation-retarget-originals.json; no golden/expected-red answer changed. Query source observer initially refused a new index module not yet reachable; routing made it reachable. Primitive move had13lint findings; import-only repairs preserve historical imports and source bodies, then lint exits0.
