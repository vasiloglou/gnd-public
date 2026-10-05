# RF2 — Consolidate identical helpers

**Status: awaiting owner review (2026-10-05); auto=false.**

## Provenance

Worktree: `.claude/worktrees/rf1-code-refactoring-225109`, branch
`claude/rf1-code-refactoring-225109`, base
`f5a83186f7c2215ac2b2afb0a010c2294eaa433a` (RF1 completion committed).
The effective plan is `notes/code-refactoring-plan.md`, approved r2 plus e1,
SHA-256 `1ffe91ddfd22f9e0fc7102fc6eb27e518d05dad996194e9bab584b58806acac8`.
Read in full: plan §§0–10, records `003-plan-gate.md`, `004-phase-RF0.md`,
`005-plan-erratum.md`, `006-phase-RF1.md`, and `notes/helper-families.md`.
RF1 record SHA-256:
`77d73913a59cd49431e475edb173869c52ac21057ef5521e3b9795c8dddefd21`.
No panel or independent reviewer has reviewed this spec. No code is authorized
by this draft. Earlier public-launch delegation does not apply.

## Obligations — harvest

Paths in this table are relative to this milestone unless prefixed `src/`,
`tests/`, or `tools/`.

| Source | Obligation | Discharge |
|---|---|---|
| Plan RF2 body | Consolidate only proven identical helpers into artifacts; canonical_bytes(v, *, newline, indent), sha256_hex, Sha256, is_sha256_hex | Design A; D2 explicitly resolves the absent identical-byte group and parameterized encoder; D3 resolves Sha256 variants |
| Plan RF2 body; helper-families | Consolidate identical strict-JSON hooks without tightening readers | Design B; T-HOOK; separate duplicate-hook groups |
| Plan RF2 body | All exit-code allocations in exits.py | Design C; T-EXIT; retain existing aliases and allocation prose |
| Plan RF2 body | issues_from_validation_error(err, rule_id) | Design D; T-ISSUE; divergent session and architecture converters excluded |
| Plan RF2 body | Hand-built refs use address.positional_constraint_ref | Design E; T-REF; RF1-OQ1 prerequisites |
| Plan RF2 body | Rename three model_digest functions under RF-D10 | Design F; T-DIGEST; five digest sites retain distinct algorithms |
| RF2-C1 | Each family marked identical has exactly one definition | T-ONE; five groups, 17 → 5 definitions, promotion only after RF1 pin agreement |
| RF2-C2 | No edit to a variant encoder | T-VARIANT; source identity against base; canonical JSON variants untouched |
| RF2-C3 | Old model_digest names importable, inventoried, absent from pinned streams and digest inputs | T-DIGEST; T-SHIM; inspect inputs and preserve RF1 bytes |
| SM1 | Every RF1 pin unchanged | T-PINS; original expected answers and golden manifest frozen |
| SM2 | Old moved names importable; patches observe effect at new location | T-SHIM; exact patch migration ledger |
| SM3 | Source scans and unloaded-module assertions cover introduced modules | T-SCAN; 88 measured sites; no new production module proposed |
| SM4 | New modules mapped; declared clean layers remain clean | T-LAYER; no new production module; preserve strict core xfails |
| Plan §9 | “SM1–SM4; one definition per identical family” | T-PINS, T-SHIM, T-SCAN, T-LAYER, T-ONE |
| Plan §9 starting points | Byte pins, tests/test_checker_families.py, artifact consumers | Verification ledger G1–G5 |
| Plan §0 | RF-R1 through RF-R11 | Standing-rule bindings below |
| Plan §10 | RF-D5 shim retirement; RF-D9 approval instrument | D1 and D5 |
| Plan §5 | Count packaged-skill module-path pin sites at gate; update in move unit | Evidence inventory: 9 citations, no citation to renamed functions; paths remain valid |
| Plan §5; RF0 D4/RF-D3 | Curated manifest adaptation; old release identity unavailable | D7; bounded adaptation only, excluded distribution lane remains unavailable |
| Plan §6 | Byte drift, verdict/order drift, dead patches, shrinking scans, dual authority, variant merge, budget overrun, misleading metrics, stale names | T-PINS, T-VARIANT, T-SHIM, T-SCAN, D6, size gate, measured head/base table; owner strings are RF3 |
| Plan §7 | No features, tightening, release claims, broad-suite repair, source-owned OQs | Out-of-scope section |
| RF0-OQ4 | Audit's identical canonical-byte claim refuted; accept or rule a normalized view | D2; no silent normalized view |
| RF1-OQ1; inventory owed_by=RF2 | Measure and PyRel ref byte pins must land green before routing | T-PRE; dedicated successor pins; original RF1 answers unchanged |
| RF1-OQ7 | Next edit of support module owes token-path unification and declared-input binding | Avoid editing tests/support/rf1_pins.py; if needed, return this boundary to gate |
| Prior records | Source control rests on owner attestation; prior AST evidence not behavior proof; local macOS coverage only | D6; Boundary; pre-move and post-move tests |
| Prior records | RF0-OQ5 (RF3), OQ6 (RF8), RF1-OQ2–6 remain owned by named gates | Out-of-scope and carryovers |

RF2 has no plan **Residual** paragraph. The explicit prior boundary is retained:
“AST identity is not behavioral identity: D7 requires RF1 byte pins before any merge.”

## Standing rules bound to RF2

| Rule | Binding |
|---|---|
| RF-R1 Behavior-preserving | Preserve names through aliases, schemas, exact messages, exceptions, exits, bytes and digest inputs; stop on any pin drift |
| RF-R2 Bytes are contracts | Copy selected bodies verbatim; keep all diverged canonical encoders, strict readers, file/model digest algorithms separate |
| RF-R3 Pin before move | Existing RF1 corpus plus T-PRE measure/PyRel pins green before the first move |
| RF-R4 Atomic move units | Each move commit includes aliases, affected patch targets, widened scans and a green selected gate; later adaptations in separate commits |
| RF-R5 Shims inventoried | notes/shim-inventory.md records old/new path, phase, retirement trigger; D1 governs retirement |
| RF-R6 Source scans must not shrink | Examine all 88 scan sites against moved definitions; add explicit scope coverage assertions where scans are affected |
| RF-R7 One authority per unit | Work only here; public-launch ledger and its guard unchanged; D6 attestation required at gate |
| RF-R8 Release identity | Changed src/gnd invalidates prior production identity; record unavailable evidence, no recertification |
| RF-R9 Measured budgets | Five groups: 17 → 5 definitions (strictly better); touched-file and moved-line ceilings below; stop on overrun |
| RF-R10 No feature work | Shared utilities only; no new command, flag, schema or semantic family; defects deferred |
| RF-R11 Focused honest verification | Reverse dependency closure measured at 115 modules; use contract-focused gates, no automatic whole-default replay |

Paid-for process rules:

1. **Totality belongs to the function, not the caller:** no new JSON document
   consumer. Existing encoder/reader failures preserved; do not tighten existing
   non-total functions under a refactor. is_sha256_hex has a defined arbitrary-object
   false result, tested with hostile types.
2. **An input cap bounds the document, not the algorithm:** no added traversal
   complexity; hooks retain their single linear walk. Predicate checks length
   before examining characters; large-string and non-string cases bound its work.
3. **Validation order is part of the design:** readers and validation converters
   keep call order and issue ordering; no new guards before old guards.
4. **One walk over N kinds:** shared issue conversion traverses error.errors()
   once; refs keep their existing enumeration order.
5. **Normative prose has one home:** this spec cites the process references;
   existing exit allocation rationale moves with constants to exits.py.
6. **Resolve representation by measurement:** promotion uses equal actual RF1
   observations, not an AST or name claim; non-ASCII, non-finite and newline cases
   remain in the comparison.

Failure coverage: T-ONE has known-dirty duplicate controls; T-HOOK tests both
unique and duplicate pairs, both hook variants and each caller's outer error;
T-ISSUE uses multiple errors and nested locations to expose order/first-match
mistakes; T-REF covers both inline and top-level addresses; T-DIGEST covers all
three meanings including prefixes and reference-population models. No claim of
branch exhaustiveness beyond these moved contracts. Repaired spec bytes require
new review if a panel is subsequently selected. No interchange schema changes.

## Goal

Exit 0 on the selected current-byte controls while replacing the five RF2
identical groups' 17 implementations with five definitions, leaving the RF1
expected corpus and every diverged encoder implementation unchanged. RF2-C1
is scoped to the RF2-owned groups in helper-families.md; RF4/RF6/RF8 groups
remain for their assigned phases.

## Design

No new production module. Existing layer-map entries remain applicable.
Every moved body is copied without edits in its move commit. Names below are
proposed new internal/public utility names, not existing base symbols.

### A. src/gnd/artifacts.py — encoding, hash and digest types (~45 added lines)

- Keep canonical_json_bytes(value: object, *, exact_numbers: bool = False) -> bytes
  and canonical_json_text(value: object) -> str byte-for-byte unchanged.
- Move the report group's function verbatim as
  `canonical_report_text(payload: Mapping[str, Any]) -> str`.
  Base homes: conformance.report.canonical, coverage.canonical_payload,
  fidelity.report.canonical (hash 2f5a20a1, three definitions).
  It uses indent=2, ensure_ascii=False, sort_keys=True, allow_nan=False;
  returns text with no appended newline. The family note's word “compact” is
  incorrect; actual source and RF1 bytes govern.
- Existing `sha256_hex(data: bytes) -> str` remains the single body for
  f4d89086 (five definitions). Alias assurance_evidence._sha, diff._digest,
  install._sha256 and recovery.verify._sha256 to it.
- Existing `Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]`
  is the home for identical aliases in recovery.report, exp.session_eval and
  exp.session_store. review.request.Sha256 includes strict=True and stays separate.
- Proposed `is_sha256_hex(value: object) -> bool`: true only for a str of length
  64 with all characters in ASCII 0–9/a–f. No coercion, prefix or whitespace.
  No existing predicate named is_sha256_hex exists at base. Before replacing
  any validation expression, pin its exact accepting/refusing behavior; differing
  predicates stay separate. D3 rules whether to add this utility at all.
- `canonical_bytes(v, *, newline, indent)` has no verbatim identical-byte group
  to move. D2 proposes not introducing it in RF2. Adding it would create a new
  serialization surface rather than consolidate an existing proven identical one.

### B. src/gnd/artifacts.py — strict reader hooks (~30 added lines)

Move the three hook groups separately:

- `reject_json_constant(token: str) -> None`: hash 5bebc70e, four definitions.
- `reject_json_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]`:
  hash d9f0cf8e, three definitions (including review.request's importable helper).
- `reject_json_duplicate_pairs_result(pairs: list[tuple[str, Any]]) -> dict[str, Any]`:
  hash dcbdd645, two definitions; keep separate despite matching messages.

The nested hook names in declared_adapter, adapter_policy, session_eval and
session_store were not externally importable; record their former containing
reader as the compatibility boundary. Remove nested copies and pass imported
functions to the same json.loads arguments. Preserve each outer reader's catches,
limits and messages. Re-export review.request._reject_duplicate_object_pairs.
No new bounded reader or stricter parse policy is introduced.

### C. src/gnd/exits.py and allocation consumers (~65 moved lines)

Move remaining CLI EXIT_* definitions with their allocation rationale, retaining
all cli.EXIT_* names and __all__ in exits. Current remaining allocations are
GENERATOR=5, QUARANTINE=6, CHECKER_DEFECT=6, DRIFT=10, COLLISION=11,
NO_INSTALL=12, MODEL_CODE_DRIFT=13, SESSION_NOT_ACCEPTED=15,
REVIEW_INCONCLUSIVE=16, EVOLUTION_OPERATIONS_GATED=18.
The two names for 6 are intentional. Preserve exit maps and precedence ordering.
Conformance service's private allocations become aliases to exits (including
its 3 ill-formed allocation); solve._EXIT_OK=0 becomes an alias to a named
EXIT_OK in exits. Inventory every runtime allocation at execution, excluding
standalone packaged-skill scripts per RF0 scope. Newly named internal allocations
need pre-move baseline assertions; do not turn dynamic return values into new
allocations. No behavior change or reworded help.

### D. src/gnd/model.py — issue conversion (~15 added lines)

`issues_from_validation_error(err: ValidationError, rule_id: str) -> list[ValidationIssue]`
uses extract.manifest._validation_issues's body verbatim, renaming only parameters
as necessary in a later adaptation commit (the first move retains the old
parameter spelling). It preserves loc joining, entry msg, order and rule id.
exp.spec and exp.conclusions keep old one-argument wrappers supplying their
existing rule constants. extract.manifest keeps its old two-argument name.
The architecture tuple/ArchitectureIssue converter and session_contract's
version-sensitive filtering remain separate. cli._cmd_exp_init is considered
only if its RF1 session byte pins and a direct converter pin demonstrate equality.
Keep this in model beside ValidationIssue; RF3 may move it with that type.

### E. Constraint-reference consumers (~20 adapted lines)

Use existing
`address.positional_constraint_ref(fact_type_id: str | None, index: int) -> str`
for the matching f-strings in synth.assemble, synth.mutate, measure.report and
export.pyrel_runtime. Preserve traversal, filters, declared-ID logic and order.
T-PRE must first pin measure's guarded-exists top-level set and PyRel's inline
and top-level entries, plus their exposed artifact bytes. Generated PyRel runtime
is intended to be standalone and is copied verbatim into exported programs.
Embedding a new helper would also change exported source bytes. D4 therefore
proposes retaining export.pyrel_runtime unchanged as an explicit scope amendment,
pinning its addresses/output as the deferred boundary; never add a gnd dependency
to the exported program. The full unamended routing requirement cannot coexist
with exact exported-source-byte preservation. Do not reuse the export's ModelIndex as the planned RF6 index.

### F. Model digest renames (~10 rename/alias lines plus caller imports)

Rename without changing bodies:

| Existing path | New same-module name | Meaning |
|---|---|---|
| conformance.currency.model_digest(model_path: str \| Path) -> str | model_file_sha256 | raw model file bytes, bare hex |
| synth.provenance.model_digest(model: Any) -> str | validated_model_sha256 | population validation identity, bare hex |
| transition.model_digest(model: Model) -> str | transition_model_identity | prefixed sha256: validation identity |

Old names remain aliases, listed in shim inventory. population._model_digest
and references.reference_model_digest keep their existing algorithms/names.
Do not merge repr-derived, file-derived or canonical reference-population identity.
Update internal imports and the measured patch in
`tests/test_conformance_payload.py:834` of conformance.service.model_digest;
retain a compatibility name but patch the new consumer lookup and observe its
refusal through a direct regression control. T-DIGEST checks no name string
was inserted into serialized artifacts or digest inputs.

## Decisions — all OPEN

| ID | Owner decision and proposed ruling | Alternatives / cost |
|---|---|---|
| D1 / RF-D5 | Keep all shims through at least the first public release after RF6; removal requires separately approved phase | Earlier removal breaks import compatibility |
| D2 / RF0-OQ4 | Accept the canonical-byte premise as refuted; consolidate only the three identical indented report-text sites, keep all byte variants, and omit new canonical_bytes | A normalized view would merge RF0-diverged functions and needs renewed proof/ruling; do not silently amend the plan. Record the scope discrepancy for milestone-close plan repair |
| D3 | Unify only non-strict Sha256 aliases; retain strict review variant; add is_sha256_hex only for demonstrated equivalent caller checks | Adding unused utility buys no consolidation; tightening coercion is prohibited |
| D4 | Retain standalone PyRel runtime/source bytes unchanged and record its ref routing as deferred scope; pin current refs/output first | Importing gnd breaks standalone behavior and embedding a helper changes exported bytes; full routing requires plan repair, not an observable-change exception |
| D5 / RF-D9 | Approve this spec prose with the existing RF1 executable corpus plus new pre-move green pins | Corpus-first defaults for new serialization contracts; RF2 changes no format or exit contract, and RF1 already provides approved bytes. A separate RED implementation corpus would fail unchanged code for structural reasons, not define different expected bytes |
| D6 / RF-R7 | Owner attests source repository took no changes to handed-off runtime/test-acceptance paths | No source remote supplied; control remains attestation unless owner supplies reachable source identity for high-water comparison |
| D7 / RF-D3 | Apply RF0's ruled curated-manifest adaptation for changed paths, preserve units.json and its guard, report prior release evidence unavailable | Whole distribution replay/repair is excluded; no new release/assurance claim |
| D8 | Approve target 17 → 5 definitions and budgets below | Miss or overrun stops phase under RF-D13; no relaxed target inferred |
| D9 | Omit optional spec panel; independent adversarial diff review remains required after implementation | A requested panel consumes separate provider budget and requires explicit instrument selection |
| D10 | Require a reproduced green RF1 baseline before any move; authorize focused diagnosis of the ten pre-existing session mismatches as the first approved step | No golden changes inferred; any support-module repair triggers RF1-OQ7 and its owner scope decision. Unresolved failures prohibit claiming SM1 |

No row above is an owner ruling. Implementation begins only after explicit
approval resolving D1–D10, especially the refuted-premise/standalone boundaries.

## Tests and verification selection

Proposed new files: `tests/test_rf2_helpers.py`, `tests/test_rf2_pre_move_pins.py`.
New artifacts/goldens live in `tests/fixtures/rf2-pins/`, separate from RF1.
Test names below are planned, not claims of tests already existing.

| ID | Case / file | Expected exit and criterion |
|---|---|---|
| T-PRE | test_rf2_pre_move_pins: measure_guarded_exists_refs, pyrel_inline_and_top_level_refs, measure_output_bytes, standalone_pyrel_output_bytes | pytest 0 on base before moves; RF1-OQ1/RF-R3; seeded address/message mutation must produce nonzero |
| T-ONE | test_rf2_helpers: one_definition_per_promoted_group; known_dirty_duplicate_fails | pytest 0; 17 → 5, each group individually one; duplicate control fails assertion; RF2-C1 |
| T-HOOK | test_rf2_helpers: strict_hook_variants_and_outer_errors | pytest 0; unique/duplicate/empty pairs, NaN/Infinity and malformed input at every affected outer reader; both variants remain distinct |
| T-ISSUE | test_rf2_helpers: issue_conversion_preserves_order_and_rule_id | pytest 0; empty loc, nested string/integer loc, multiple issues, two distinct rule ids; same ValidationIssue payloads; no session filtering merge |
| T-EXIT | test_rf2_helpers: all_exit_allocations_have_one_home_and_old_aliases; maps_unchanged | pytest 0; exact name/value and __all__ checks; duplicate allocation control fails; CLI help/exit pins unchanged |
| T-REF | test_rf2_helpers: ref_routing_preserves_order; standalone_export_remains_importable | pytest 0; top-level+inline, nonzero index, guarded exists/no-exists, standalone output with gnd unavailable; detects dropped/changed refs |
| T-DIGEST | test_rf2_helpers: three_digest_renames_preserve_meaning_and_inputs | pytest 0; RF1 corpus incl reference models, raw-file whitespace identity, old/new equality, observed patch effect, literal names absent from captured bytes and input probes; RF2-C3 |
| T-SHIM | test_rf2_helpers: shim_inventory_covers_moves_and_patch_effects | pytest 0; imports every row; asserts exact moved set; rejects missing row and dead patch; SM2 |
| T-VARIANT | test_rf2_helpers: diverged_encoder_source_unchanged | pytest 0; AST/source segments for every RF0-diverged encoder equal base (including artifacts defaults/exact_numbers); edit negative control fails; RF2-C2 |
| T-SCAN | test_rf2_helpers: affected_scan_scopes_cover_moved_definitions | pytest 0; exact scopes include homes and aliases, removal negative control fails; no-new-provider/import checks retained; SM3 |
| T-LAYER | test_rf1_layering.py and test_gnd_arch.py; new RF2 map coverage control | pytest 0, existing 16 strict xfails remain; SM4; any new wrong-way pair fails |
| T-PINS | all seven tests/test_rf1_*.py files | pytest 0; every expected answer unchanged; SM1 |

G1 baseline uses `env -u LANG -u LC_ALL` before the interpreter and needs a
process environment where the macOS sandbox does not inject launcher warnings.
Those controls do not clear the ten remaining session failures.
Exact commands use this checkout's `.venv/bin/python` because the default uv
cache is sandbox-inaccessible; equivalent uv commands may use a writable cache.
No addopts or lane-marker overrides.

| Gate | Disposition / exact command (expected exit 0) | Input boundary, justification and invalidation |
|---|---|---|
| G1 baseline and SM1 | run: `.venv/bin/python -m pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py` | RF1 fixture answers frozen; all moved surfaces and interpreter version affect this result; run baseline and each relevant move/end gate |
| G2 direct RF2 and SM2/3 | run: `.venv/bin/python -m pytest -q tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py` | New cases and fixture expectations, actual lookup homes, scan scopes; T-PRE first green on base; changes to hooks/refs/types/renames invalidate |
| G3 plan checker/artifact controls | run: `.venv/bin/python -m pytest -q tests/test_checker_families.py tests/test_artifacts.py tests/test_address.py tests/test_gnd_arch.py` | Model issues, artifact encoder/type, address helper, measurement/map; functional and instrument negative controls; invalidated by any shared helper change |
| G4 direct helper consumers | run: `.venv/bin/python -m pytest -q tests/test_conformance_payload.py tests/test_conformance_drift.py tests/test_coverage_payload.py tests/test_fidelity_payload.py tests/test_exp_spec.py tests/test_extract_manifest.py tests/test_review_request.py tests/test_recovery_report.py tests/test_recovery_adversarial.py tests/test_exp_session_eval.py tests/test_exp_session_store.py` | Report bytes, digest meanings, strict hooks, aliases and validation errors; excluded historical nodes retain cadence; imports and caller adapters invalidate |
| G5 reference/exit/offline consumers | run: `.venv/bin/python -m pytest -q tests/test_measure_offline.py tests/test_measure_coverage.py tests/test_measure_derivation.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_exp_bands.py tests/test_review_bands.py tests/test_solve.py tests/test_install.py tests/test_doctor_uninstall.py` | Runtime routing, standalone template, address order, exit assignments/maps, no-provider graph; changes to generated embedding or exit imports invalidate |
| G6 measurement/budgets | run: `python3 tools/gnd_arch.py measure --out <fresh-head-metrics.json>`; `python3 tools/gnd_arch.py compare f5a83186f7c2215ac2b2afb0a010c2294eaa433a HEAD --out <fresh-compare.json>` | Python 3.14, layer map and src/gnd; bind outputs by SHA-256 and assert targets via T-ONE/size control; tool evidence alone does not assert budget |
| G7 notes/scope | run: `.venv/bin/python -m pytest -q tests/test_development_scaffold.py`; `git diff --quiet f5a83186f7c2215ac2b2afb0a010c2294eaa433a -- .gnd-planning/milestones/public-launch/migration/units.json tests/test_public_distribution.py` | Planning links, authority ledger and unchanged distribution guard; updates invalidate |
| G8 lint | run: `.venv/bin/ruff check <explicit changed Python paths>` | Exact changed paths listed before execution; no autofix of evidence; edits invalidate |
| Full default suite | cadence: `uv run pytest -q`; explicit owner or separately configured CI selection | 115-module reverse closure is broad; focused gates claim moved contract preservation, not whole-repository correctness |
| Excluded historical/evidence/census/distribution/native/provider lanes | cadence: their separately configured CI or expressly selected run | No marker/addopts overrides; prior outcomes unavailable over changed src bytes; bounded current controls above substitute for phase claim only |

Measure and validate selection with collection before approval completion;
collection is evidence of selected nodes, never a green run claim. If affected
consumers outside G1–G5 are found while resolving imports/patches, add a focused
row and return changed scope to owner where required. Do not infer a full replay.

## Out of scope for RF2

All RF7 tightening; safe-filesystem moves (RF4), core-cycle repair (RF3), model
query helpers (RF6), session duplicate bodies (RF8), arithmetic and cross-meaning
pairs not assigned to RF2. No package split, CLI handler extraction, resolver
semantic change, schema version, message repair, performance work, source-owned
open-question transfer, recertification, release acceptance or publisher.
OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1,
OQ-V52-P1-IMPORTWALK-1 and OQ-V63-CLOSE-HELPER-TAIL-1 remain source-owned.
RF1-OQ3 belongs at close; RF1-OQ2/4 at RF8; RF1-OQ5/6 at successor.
RF1 support-module refactoring is excluded unless separately brought to gate.

## Size and measurements

Base measurement: `evidence/metrics-RF2-base.json`, SHA-256
`e49e4e6c5360f5c8102a1ea68773a754e311bd552beee9cd930803c32a14a632`.
Python 3.14: 148 modules, 104,094 source lines, 842 edges, 242 private import
sites, five runtime SCCs. Five RF2 duplicate groups contain 5+3+4+3+2=17
bodies; proposed end target 1+1+1+1+1=5. Nested hooks count as bodies;
compatibility aliases and thin rule-id adapters are inventoried separately,
not used to hide duplicate implementations.

`evidence/RF2-impact-inventory.json` retains every measured patch and scan site.
28 conservative impact modules (including the conditionally excluded PyRel runtime);
runtime reverse-import closure 115/148 modules.
464 patch sites (73 unresolved), 609 private test-import sites, 88 source-scan
sites, 9 packaged-skill citations. The unresolved targets require direct search
before each move; static inventory alone is not a complete patch proof.
One resolved affected rename patch: test_conformance_payload.py:834.
No citation names one of the renamed digest functions. All old module paths
remain, so module-path citations need no edit; remeasure at execution.

Proposed estimates / stop ceilings (not approved): production files 28 / 40;
production lines moved 180 / 350; added/adapter production lines 180 / 300;
handwritten test lines 600 / 1,000; total changed non-evidence files 48 / 70.
Golden outputs are separate from handwritten lines; RF2 golden byte budget 2 MiB.
Moved-line counts use the RF0 compare tool; also report deletions/additions to
avoid presenting identical deduplication as an atomic physical move.
Private imports and SCCs have no RF2 improvement claim; report changes and
explain any worsening. Budget violations stop at the owner gate.

## Approval instrument and implementability sweep

Proposed: spec prose, with existing RF1 approved executable answers and separate
pre-move green successor pins. This costs no new format-design corpus and keeps
RF1 answers unchanged. D5 needs an explicit owner ruling; optional spec panel
is also an explicit owner choice (D9). Corpus-first remains the alternative.

Sweep (2026-10-05): five helper bodies can be moved verbatim, all homes already
exist and are mapped; strict Sha256 cannot replace non-strict aliases without
behavior change; session/architecture issue converters cannot share the simple
converter; no canonical-byte identical group exists; standalone generated PyRel
cannot depend on installed gnd, and any runtime source edit changes its exported
source bytes. Retaining it unchanged requires D4 scope approval. D2–D4 explicitly isolate those contradictory or
conditional readings. No claimed solution depends on an optional earlier phase.
RF1 is committed; RF-D2 is already satisfied by e1. The source attestation (D6)
and scope rulings remain gate prerequisites. No implementation has been written.

## Implementation findings

None: specification stage only. Reproduced pre-implementation facts are recorded
in Design A, D and E and in D2–D4; they are not hidden implementation repairs.

## Preflight evidence

`evidence/RF2-preflight-notes.txt` retains the unsuccessful sandbox baseline
(23 failed, 372 passed, 16 xfailed) and its environment-dependent differences.
G4/G5 consumer collection selected 1,020 nodes under default exclusions.
The environment-controlled unsandboxed baseline is recorded separately in
`evidence/RF2-baseline-pins.txt`: exit 1, **10 failed, 385 passed, 16 xfailed
in 62.80s**. All failures are fresh/resume session versions 1–5. Agent pins
and v7/v8 session pins are green in this run. The remaining session mismatches
are reproduced but their cause is not yet established; D10 requires diagnosis
and a green base before moves. This is not a passing prerequisite.
Planning scaffold check: exit 0, 14 passed, 1 deselected in 4.29s.
No expected answer has been regenerated or edited.

## Owner gate — 2026-10-05

**Status: owner-decided (2026-10-05).** The owner replied “approved” to the
spec approval request and source-repository attestation. This is explicit
approval of D1–D10 and go-ahead within that scope, not delegated auto approval.
Approved spec SHA-256 before this append:
`2871be06fbbbefe076744ab6f03ea53425ed168cfcc07428cde731f565fedd0a`.
Owner marks: D1 approved; D2 approved; D3 approved (conditional equivalent
caller checks only); D4 approved; D5 prose approved; D6 attested; D7 approved;
D8 target and ceilings approved; D9 optional spec panel omitted; D10 baseline
diagnosis authorized, green baseline still required before moves. All marks
are dated 2026-10-05. No RF1 expected answer change or support-module repair
is approved implicitly; an amendment remains necessary if diagnosis needs it.

### Finding RF2-F1 — environment-dependent baseline (resolved)

2026-10-05: comparing a scratch observation to the correct Python 3.14 golden
located an extra inherited TERM entry in v1 session invocation metadata. Removing
TERM along with LANG/LC_ALL reduced the session failures to v3 fresh/resume.
Those failures reported spawn_error=FileNotFoundError for the literal `python`
verifier: direct .venv/bin/python invocation did not put .venv/bin on PATH.
Adding the virtualenv to PATH reproduces the complete frozen baseline:
395 passed, 16 xfailed, exit 0, 64.05s. Evidence: RF2-baseline-green.txt.
No source, support module or expected answer repair was necessary; RF1-OQ7
remains deferred. G1 and subsequent subprocess gates use the controlled environment
`env -u LANG -u LC_ALL -u TERM PATH="$PWD/.venv/bin:$PATH"` and execute outside
macOS's sandbox where it adds warnings to synthetic subprocess stderr.

Pre-move measure/PyRel predecessor answers were captured with unchanged src/gnd,
then compared green (four tests). New answers are isolated in
`tests/fixtures/rf2-pins/pre-move.json`; RF1 goldens and manifest are unchanged.
