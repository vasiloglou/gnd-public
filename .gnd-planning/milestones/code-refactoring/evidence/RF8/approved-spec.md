# RF8 — Session profile and v7 strategy merge

Status: owner-decided (2026-10-06), delegated approval (auto=true).

## Provenance
Effective code-refactoring plan r2+e1, sections0–10, RF8; records004–013;
RF7 bounded amendment and semantic successor pins remain binding. Base de4eed6.
No spec panel selected; old plan panels cover their original bytes only.
Harvest readers inspected all prior records and bounded tests/tools/skill references;
primary cross-checked their cited anchors against current source and metrics.

## Obligations
| Source | Obligation | Discharge |
|---|---|---|
| §4 RF8 | SessionProfile built once in DataDrivenContract.model_validate; replace inline mappings and v7/v8 membership; shared run/reconstruct strategies; public best_identity; name v8 literal | Design, G1/G2 |
| e1/RF-D8/RF0 A13 | Preserve first SESSION_CONTRACT_VERSION=2 and V2 capture | T-live-v2 |
| RF8-C1 | every RF1 session replay(version × path) identical normalized bytes/resume | G3, baseline failure disposition below |
| RF8-C2 | session_v7 only strategy hooks or shim | T-shim, moved-source control |
| RF8-C3 | no multi-module SCC among RF0 confirmed session modules | T-graph includes all new session modules, dirty control |
| SM1 | RF1 pins unchanged except already-approved RF2/RF7 successors | G3/G4, frozen original byte check |
| SM2/RF-R4/R5 | all moved names old-path importable; new-home patches observe actual effect | shim inventory, T-metadata/T-patch, focused publication race nodes |
| SM3/RF-R6 | source scanners cover new physical homes | alias, reader, artifacts, dispatcher, RF7 routing scanner adaptations + omission controls |
| SM4 | all new modules mapped; all declared-clean layers remain clean | G2 graph/map controls |
| §9 | “SM1–SM4; replays identical per version and path”; exp session, store, close and judgments controls | G1–G5 |
| RF1-OQ2 | missing terminal result CLI resume refusals v2/v3/v7/v8 | D3 preserve; correctness deferred |
| RF1-OQ4 | absolute contract prompt path affects digests | D4 preserve; successor session portability |
| RF1-OQ7 | original rf1_pins scrub debt if touched | do not touch original support; remains deferred |
| §5 | skill path citations counted at gate; no session home citations in current inventory | metrics-base skills; no skill edit; installer/twin checks G5 |
| §6 | changed bytes/verdicts/patches/source scans; authority/release/budget drift | G1–G5 + budget/frozen controls |
| §7/prior records | no new semantics/CLI/schema, broad replay, certification, release, shim retirement or source authority transfer | Boundary |
| RF7 record | strict JSON/date/path/resolver/digest successors; unknown version1–8 | preserve, G3/G4; no new tightening |
| RF6 query/source policies | inventories and reasoned exceptions remain exact | selected query controls, append-only move retargets |

## Standing rules
Totality: profile lookup handles nonhashable arbitrary JSON version values without new tracebacks;
wire readers retain refusal ordering. Input cap versus algorithm: profile lookup is bounded by8;
no new untrusted-data walk; timing control evaluates repeated profile access, not whole verifier runtime.
Validation order: frozen readers dispatch before normalization; unknown diagnostic stays byte-identical.
One policy walk: a single profile table supplies version capabilities to every consumer.
One prose home: packaged session contracts remain normative wire homes; this note specifies refactoring.
Measure contested representation: exact model_dump/schema/private metadata and replay comparisons.
RF-R1/R2 preserve observables/encoders/digests; R3 baseline pins precede moves; R4 atomic move +patch/scan;
R5 inventoried shims; R6 physical scan coverage; R7 ledger/test frozen against base; R8 manifest
adaptation records changed identity without release claim; R9 targets/budgets below; R10 no feature;
R11 focused impact ledger. Failure classes: dirty graph/scan controls, per-version capability table,
model_copy sibling behavior, actual patch effects and normalized full-tree replay prevent vacuous claims.

## Goal
Selected gates exit0; session runtime SCC count0 (base1 with7 members);
compatibility module at most60 lines (base937); every unchanged replay observation compares equal.

## Design
- exp/session_profile.py (~100 new lines): frozen dataclass SessionProfile;
  profile_for_version(version: object) -> SessionProfile | None; closed versions1–8.
  flags legacy, tests, walk, declared_adapter, patch, judgments; patch wire axes
  launch3/4, feedback8/9, attempt9/10, result6/7. Shared legacy selection methods
  preserve existing walk > redaction > transition > assurance > derivation > base precedence.
- session_contract.py: private _profile, public profile property returning SessionProfile;
  dispatcher reader map preserves original equality acceptance and unknown diagnostic;
  build profile after normalized validation; copy/direct construction resolve a matching profile.
  frozen v1–v8 reader schemas unchanged; JUDGMENT_SESSION_CONTRACT_VERSION=8 replaces contract literal.
- exp/session_records.py (~1350 moved lines): store models/constants/collector/helper bodies
  physically moved verbatim; original qualification retained. Store reexports compatibility bindings.
- exp/session_control.py (~270 moved lines): verifier_environment and invocation/disposition
  helpers moved verbatim, importing only contract/eval/agent/policy dependencies; session reexports.
- exp/session_replay.py (~470 moved lines): v7 evaluation/feedback/reconstruction shared strategy;
  imports records, never store/controller runtime. reconstruct(store, contract, *,
  allow_terminal=False, policy_sha256=None) keeps exact signature.
- exp/session_runtime.py (~400 moved lines): v7 run implementation + copy helper; imports
  replay/store/control. async run(contract, *, contract_sha256, adapter_policy, prompt,
  candidate_root, run_root, verifier, declared_invoker, redaction=None, **unused).
- session_v7.py: old names reexported as listed shims; no implementation bodies remain.
- SessionStore.best_identity() -> BestAttemptIdentity | None names reconstructed identity;
  best_record() exposes the selected record for close; legacy _v7_best remains populated
  as compatibility state. No new disk reads/writes on identity access.
- session_patch/judgments use records collector; tests_runner environment uses control.
  store reconstruction uses replay, removing back edges. Consumer checks use profile flags.
- Tests source observers widened atomically; patch publisher target moves to runtime.
  Original golden fixtures never recaptured. Existing immutable schema reader controls retained.

## Decisions — delegated approval (auto=true),2026-10-06
| ID | Question and cost | Ruling |
|---|---|---|
| D1/RF-D9 | corpus-first versus prose | Prose: pure behavior-preserving move with already committed golden bytes, no new wire/exit/predicate contract. Supplemental characterization first green, not invented new expected bytes. |
| D2 | optional panel | omitted; one independent high-effort native Codex diff review + at most one repair review; external provider authorization remains distinct |
| D3/RF1-OQ2 | change resume refusal versus preserve | preserve characterized refusals; no product correctness claim; carry to session controller successor |
| D4/RF1-OQ4 | normalize prompt path versus preserve | preserve digest-bound prompts; carry to session portability successor |
| D5 | baseline v3 fresh/resume spawn refusal | verify current base pair before edits; report actual red, exclude only two nodes from passing comparison gate; no golden recapture or product fix |
| D6 | budgets | ≤90 touchedfiles,≤4000 movedlines,≤650 nonrelocated source additions,≤1600 test/data additions,≤1600 non-evidence documentation additions; SCC0/shim≤60 strictly improve measured base |
| D7 | authority/identity | handed-off paths remain public-owned; source repository not compared, authority rests on prior owner handoff, no new attestation invented; source-owned ledger/test frozen |

## Tests and selection ledger
Every command uses .venv/bin/python, configured default exclusions, clean LANG/LC_ALL/TERM,
PATH prefixed with selected interpreter bin; capture variables absent. Commands below expected0
unless marked baseline diagnostic. Supported3.11/3.13 direct tests and session replay selected separately.
| Gate | Disposition / exact command | Boundary / invalidation |
|---|---|---|
| B1 | run: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --tb=short (diagnostic, actual failure retained) | preedit base/fixtures/subprocess environment; cannot call red green |
| G1 | run: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_exp_session_contract.py tests/test_exp_session_evidence_compat.py --tb=short | profile, wire dumps, dispatcher metadata, hostile values, copy, timing, live-v2, patch checks; change invalidates |
| G2 | run: .venv/bin/python -m pytest -q tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py --tb=short | physical graph/maps/source corpus and dirty controls; move invalidates |
| G3 | run: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --deselect=tests/test_rf1_session_pins.py::test_session_fresh[3] --deselect=tests/test_rf1_session_pins.py::test_session_resume[3] --tb=short | all session version/path observations except independently reproduced launch environment pair |
| G4 | run: .venv/bin/python -m pytest -q tests/test_exp_session_store.py tests/test_exp_session_eval.py tests/test_exp_session_rank.py tests/test_exp_session_recurrence.py tests/test_exp_session_e2e.py tests/test_public_session_wire_guards.py tests/test_public_retained_session_results.py tests/test_public_session_version_relabel.py tests/test_public_v72_session_staging.py tests/test_public_patch_publication_identity.py tests/test_v72_phase5_session_mechanics.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py tests/test_public_payload_alias_sites.py tests/test_public_v72_reader_boundaries.py tests/test_public_v72_ownership_direct.py tests/test_public_v72_status.py tests/test_exp_close_work_gate.py tests/test_exp_close.py --tb=short | controller/store/close/judgment source+fixtures; exact known preexisting reds require base proof before any exclusion |
| G5 | run: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_semantic_pins.py tests/test_artifacts.py tests/test_packaged_skills.py tests/test_development_scaffold.py --tb=short | shared moved helpers, public CLI/semantics, source scan/installer/twins |
| G6 | run: .venv/bin/ruff check changed Python paths; git diff --check | every edited Python/doc; reexecute after edits |
| broad/CI | cadence: configured GitHub required CI/full/evidence/census/proof/distribution/external lanes; explicit owner or separately scoped CI trigger | not phase acceptance; no broad replay or cert selected |
| untouched primitives | inherit: RF7 bound evidence remains historical on unchanged helpers; current G5 compares observable pins, not a new general safety verdict | changes invalidate, exact hashes checked before citing |

New tests by branch: profile rows1–8, unknown0/9/nonhashable/bool/float; instance idempotence;
model_copy same/differentversion; dump/jsonschema profile exclusion; frozen profile mutation;
legacy wire precedence allarms; patch axes7/8; best absent/present; shims identity/qualification;
new-home environment and publisher patches; graph/scan dirty fixtures fail assertions.
All tests exit0 against current behavior; structural new capability assertions first observed red
against base then green after implementation. Characterization expected answers unchanged.

## Implementability sweep
Concrete dependency DAG records -> eval -> tests_runner -> control would cycle if control imports
full eval; therefore environment goes in a separate session_environment.py leaf (~15 movedlines)
and tests_runner imports it. Control may import eval; no evaluator backedge. Replay imports
records, patch and judgments; runtime imports replay andstore; session imports runtime/control.
No dependency evasion through string imports or mutable registration. Each requirement has a
possible implementation and discriminating control; v3 refusal amendment names unmet evidence.

## Boundary / out of scope
No new semantics, commands, flags, schemas, wire/digest/unknown-version changes; no shim retirement;
no old certificate over changedbytes; no source-owned question transfer; no full historical replay,
provider panel, certification, milestone close, release or merge. One reviewer is one reviewer.
Local normalized replays do not establish unnormalized timing, nonce or producer identity equality,
Linux/installed/release acceptance, or correctness of characterized refusals.

## Size / approval instrument
Prose instrument; base measurements retained metrics-base.json. Estimates1350+270+470+400+15
movedlines,≤650 newsource,≤1600 tests. Gate digest/authorization written separately before edits.

## Implementation findings
None yet.
