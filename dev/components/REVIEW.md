# Component index review notes

Suggestions only, collected while the index was built from 13 reader proposals; no code was changed. Each group below is one reader's 'Noticed' list, followed by the mechanical leads from `components_index.py review`. Treat every item as unproved until reproduced.

## codegen_conf_discover_extract

- src/gnd/codegen/emit.py:360-367, src/gnd/extract/service.py:140-146 and src/gnd/discover/output.py:35-37 each implement pretty canonical JSON with sorted keys, non-finite numbers refused and a trailing newline. This is a concrete consolidation lead; compare byte contracts before replacing them with the shared artifact serializer.
- src/gnd/codegen/emit.py:413,569,923,1183 combines tool rendering, skill prose, bundle assembly and staged filesystem publication in one large module. It remains one entry because an assigned file cannot be split across entries; its render/publish boundary is a possible future code split.
- src/gnd/codegen/plan.py:430,678,794 combines safe descriptor observation, manifest loading and ownership policy/application. The descriptor machinery and state policy are separable review concerns, not evidence of interchangeable filesystem variants.
- src/gnd/discover/service.py:197,428 combines reusable discovery with CLI argument relationships, judgement reruns and writing. A future command/service split would mirror conformance's existing boundary.
- src/gnd/conformance/structural.py:360 supplies shared SourceObservation/AST collection to architecture checks as well as constructor checking. This is intentional reuse visible in architecture.py imports, but a neutral shared observation home could make its ownership clearer.
- src/gnd/extract/anchors.py:5, src/gnd/extract/identity.py:21, src/gnd/extract/refscheme.py:37 and src/gnd/extract/vocabulary.py:35 are compatibility exports, not duplicate implementations. Keep their module coverage with canonical owners; no retirement is proposed.
- src/gnd/conformance/currency.py:114 and src/gnd/conformance/service.py:361 retain model_digest aliases; these are identity compatibility aliases, not independent hashing implementations.
- src/gnd/conformance/structural.py:464-473 still describes rglob and older parameter collection, while its actual observed_surface at :515-608 walks retained directory descriptors and observe_source_bytes at :407-423 stores positional-only/keyword-only parameters separately. The catalog follows the code; the stale docstring is a follow-up documentation repair.
- src/gnd/conformance/integrity.py:65-70 says the byte bound is imported, but MAX_CONFORMANCE_BYTES is assigned locally. This is a comment/code mismatch, not proof of a current mismatch in numeric caps.
- No unused executable module or wholly untested capability was established. src/gnd/discover/__init__.py:1, src/gnd/codegen/__init__.py:1 and src/gnd/extract/__init__.py:1 are documentation-only package surfaces; lack of direct callers is not dead executable code. Service handlers are exercised through CLI tests even where the draft lists no direct test imports.

## commands_measure_fidelity

- Pure compatibility shim: src/gnd/commands/_output.py:1-76 duplicates no algorithms; retain identity with gnd.output rather than indexing a second output implementation (tests/test_rf9_repairs.py:302).
- File worth splitting by future approved refactoring: src/gnd/commands/checking.py:28 and :844 houses model document validation, checking, diff, coverage, imports, composition and verbalization in one 1,039-line command module. All remain in its one assigned entry.
- Files retaining orchestration within entry layer: src/gnd/commands/exp.py:126 (_cmd_exp_run) and src/gnd/commands/lifecycle.py:130, :208, :315 (doctor/uninstall/install); detailed factoring advice requires reading their remaining bodies.
- Repeated tiny rate helper: src/gnd/measure/score.py:294 and src/gnd/fidelity/match.py:83 both return None for a zero denominator and otherwise numerator/denominator; src/gnd/fidelity/report.py:166 wraps the same calculation with its numerator/denominator. This is a consolidation lead, not evidence that the independent scoring lanes should merge.
- Composite identity join logic is similar in src/gnd/fidelity/match.py:240 and src/gnd/fidelity/doccheck_service.py:190, but differs: matcher requires one distinct normalized component while doccheck gathers mention values. Do not merge without preserving those different obligations.
- Apparent unused exception: src/gnd/fidelity/report.py:99 defines and exports MixedCaseCorpusError; a source/test symbol search found no caller or raise. The service checks mixed model digests directly at src/gnd/fidelity/service.py:245 rather than using it.
- Test-only package call sites in the symbol search: src/gnd/measure/promote.py:247 promote_case is exercised by tests, while production service uses manifest_rows; src/gnd/measure/score.py:196 withholds_acceptance is also directly exercised by tests. Both are public helpers; this is not a deletion recommendation.
- Documentation cites a missing test file at src/gnd/measure/score.py:199: tests/test_measure_projection.py is absent; the actual helper assertions include tests/test_measure_score.py:422 and tests/test_public_tests_mode_corpus.py:986.
- Rendering limitation is visible at src/gnd/fidelity/doccheck_service.py:226: mentions are checked filler by filler, not as relationships. The fidelity report names relation-permutation bias at src/gnd/fidelity/report.py:92.
- No whole assigned implementation was established to lack tests: direct unit tests, command tests or the shared parser/identity tests cover every proposed capability; this was not a coverage measurement.

## evolve_recovery_review

- Coupled CLI helper: src/gnd/recovery/service.py:11 imports _EvolutionCLIError and _evolve_reject_unsafe_spelling from a different lane's command implementation. A shared public filesystem/input boundary may be worth considering; preserve the current distinct exit classifications if moved.
- Multiple jobs in one module: src/gnd/evolve/service.py:730 builds blast-radius reports, src/gnd/evolve/service.py:909 replays operations, and src/gnd/evolve/service.py:1629 owns publication. It is correctly one main orchestration entry here, but these helper capabilities could merit separate homes in a future scoped refactor.
- Multiple jobs in one module: src/gnd/recovery/inventory.py:486 detects dynamic Python constructs and src/gnd/recovery/inventory.py:794 combines directory traversal, format classification, evidence construction, and proposal-marker handling. Separating static observations from traversal could clarify reuse; this proposal does not change code.
- Multiple jobs in one module: src/gnd/review/request.py:737 loads digest-bound inputs while src/gnd/review/request.py:1222 salvages external reviewer responses. They have different callers and could become separate capabilities if the source is split later; the current one-file ownership rule keeps both under review.schema.
- Similar serialization helpers require care: src/gnd/review/request.py:600 and src/gnd/review/report.py:153 both emit sorted compact JSON with a trailing newline, whereas src/gnd/evolve/models.py:75 omits the newline. This is a consolidation lead, not evidence that the evolution identity format is interchangeable with review serialization.
- Deliberate forwarding surfaces, not competing implementations: src/gnd/evolve/__init__.py:3, src/gnd/recovery/__init__.py:5, src/gnd/review/__init__.py:3. Their exports span several proposed entries; each initializer is covered once.
- No proven dead code or entirely untested capability was established in this bounded pass. CLI handlers without direct module-import tests are exercised through gnd.cli in tests/test_model_evolution.py:1119, tests/test_recovery_adversarial.py:199, and tests/test_review_bands.py:363; direct-import absence should not be labeled absence of tests.

## exp1

- File worth splitting: src/gnd/exp/session_eval.py:1571 validates checker payloads, :1959 decides acceptance, :2118 ranks attempts, and :2570 builds feedback, in addition to numerous wire schemas. Keep the current single module assignment while considering future separation.
- File worth splitting: src/gnd/exp/session.py:437 runs trusted verifier subprocesses while :526 orchestrates sessions; the main controller also delegates patch profiles at :564. The opening one-attempt docstring is narrower than the implemented retry/resume loop at :835.
- Cap robustness review lead: src/gnd/exp/frontmatter.py:119 checks stat size, then :129 reads the whole file; growth after stat is not bounded during reading. This is a source observation, not a reproduced exploit.
- Similar cap robustness review lead: src/gnd/exp/session_contract.py:1559-1560 checks initial fstat size, then :1570 reads chunks to EOF without enforcing an observed-byte stop. A later size mismatch rejects the data, but the initial cap does not bound bytes consumed if the file grows.
- Shared rule implemented separately: src/gnd/exp/frontmatter.py:67 explicitly reproduces the YAML alias/event guard for a string block rather than calling the path-oriented model guard. It imports the shared event-budget constant; this is deliberate adaptation, not evidence for duplicate-of status.
- Compatibility surface: src/gnd/exp/session.py:89-140 re-exports moved controller/environment helpers; session_control.py:298-310 and session_environment.py:20 preserve historical qualifications. Keep these identity seams visible when relocating components.
- No standalone unit test found for src/gnd/exp/declared_invocation.py:17 and :44 in the supplied importer inventory; local HTTP integration checks retained invocation evidence in tests/test_v61_phase6_http.py:112-188. This does not imply those functions are untested indirectly.
- Package initializer src/gnd/exp/__init__.py:1 contains documentation and an empty export list; its no-importers inventory result is not dead executable code. No other dead-code conclusion was established.

## exp2

- Possible consolidation review, not a duplicate-of finding: version-7/8 runtime directly assembles/publishes attempt, best and terminal artifacts (src/gnd/exp/session_runtime.py:319-410, 433-506), while SessionStore has publish_attempt, publish_best and publish_result (src/gnd/exp/session_store.py:901, 1159, 1992). Their wire coordinates and record shapes differ, so they should not be collapsed merely because both publish evidence.
- File worth splitting later: src/gnd/exp/session_records.py:117, 140, 199, 247, 1088 mixes wire schemas, strict-object intake, descriptor-based evidence writes and candidate-tree collection. These are recorded under its main evidence capability and auxiliary verbs, rather than assigning one module twice.
- File worth splitting later: src/gnd/exp/tests_runner.py:108, 294, 448, 593, 835 contains feedback/result schemas, tree copying, manifests, result-descriptor handling and tests orchestration. Any split should preserve the different symlink policies: tests copying retains symlink text (tests_runner.py:357-358), while candidate evidence intake refuses symlinks (session_records.py:1141-1142).
- Compatibility-only package surface: src/gnd/exp/session_v7.py:1-58 defines no implementation; the supplied importer inventory reports zero package importers, while tests still import the historical path (for example tests/test_public_v71_judgment_successor_guards.py:65). This is not evidence that the shim can be removed.
- Repeated module summaries: src/gnd/exp/session_runtime.py:1 and src/gnd/exp/session_replay.py:1 share the same description despite distinct execution/reconstruction roles; the proposed does lines separate them.
- No verified component without tests was found in this group. Listed tests are subject pointers, not a test coverage audit.

## export

- src/gnd/export/verification_service.py:25 houses a 500-line verify handler in the foreign-export folder; it combines sidecar state, digest checks, population loading, anchor checks, report projection, assurance and output. A clearer future home or decomposition is worth reviewing; do not move it as part of this proposal.
- src/gnd/export/ilp_service.py:189, 298, 541 and 634 combine export commands, two import contracts and reusable mined counting in one module. Keeping one owner follows the brief, but separate service/internal counting homes could improve discoverability if later refactoring is approved.
- src/gnd/export/pyrel_rules.py:1322 onward contains large embedded reporting/execution templates, while 2028 and 2289 handle plan translation and source assembly; this is a large mixed renderer worth reviewing for split seams. Internal semantics in these ranges were not fully audited.
- src/gnd/export/souffle_runtime.py:33 implements bounded process-group execution also used by Lean compilation at src/gnd/export/lean_runtime.py:68; applications instead uses the public gnd.process runner at src/gnd/export/applications.py:121. These are two bounded-execution homes, but consolidation needs a behavior comparison because the native bundle runner also measures output trees and cumulative output.
- src/gnd/export/ilp.py:86 defines deterministic JSON bytes, and src/gnd/export/ilp_amie.py:221 forwards to it; the forwarding function is not an independent capability. Lean uses gnd.artifacts.canonical_json_bytes at src/gnd/export/lean.py:7, while Souffle wire at src/gnd/export/souffle.py:42 has a different encoding contract; do not mark them duplicate-of without checking serialized evidence compatibility.
- src/gnd/export/pyrel_runtime.py:62 defines a separate raw-document ModelIndex, intentionally distinct from the production index used by src/gnd/export/pyrel_rules.py:36. Its standalone no-GND-import boundary makes an automatic deduplication inappropriate.
- src/gnd/export/lean_io.py:8-9 retains compatibility imports while actual binding calls model_module.load_model_bytes_bound at line 39; preserve the compatibility surface and patch the actual lookup when testing.
- src/gnd/export/service.py:103-109 and src/gnd/export/verification_service.py:535 retain historical __module__ values; these qualifications are compatibility metadata, not evidence of duplicate implementations.
- src/gnd/export/lean_cli.py:8 and src/gnd/export/souffle_cli.py:8 have no direct test importers in the provided stubs; they are exercised through the CLI. No assigned substantive component was established to have no tests or no callers; export/__init__.py:1 is a deliberately inert package marker.

## model_checker_assurance

- `src/gnd/model/__init__.py:282,404,648`: one physical module owns bounded model loading, reference-context intake and candidate/reference population composition, plus a large compatibility namespace. Reference intake is a candidate split if done under the repository's shim-retirement rules; `src/gnd/references.py:1-34` is currently the alias surface, not another implementation.
- `src/gnd/model/_validation.py:245,3022,3297,3512,4862,5031`: schema admission, semantic rules, aggregate interpretation, derivation graphs/classification and unattended-span checking share a 5,236-line home. Splitting pure aggregate/graph analyses would make their independent reuse easier to find; this is a suggestion, not an implementation change.
- `src/gnd/checker/_core.py:331,486,1687,1887,2059`: evaluation orchestration, correspondence wording, partial-knowledge post-processing and document-anchor checks share a 2,464-line home. These are separate responsibilities within one assigned capability and potential future split points.
- `src/gnd/assurance/_wire.py:10,104,169,204,264`: wire decoding, artifact/runtime identity and capability construction share a single module. Distinct query vocabulary is included in assurance.identity so the current ownership does not hide the decoder or capability constructor.
- `src/gnd/assurance/transport.py:93-153`: the receipt consumer itself does not remove a consumed receipt or maintain a replay set, despite the module-level single-consumption description. One-use authorization depends on the supervised caller's nonce/path lifecycle; that external lifecycle was not audited here, so the entry claims checks and binding rather than transport-local replay prevention.
- `src/gnd/assurance/__init__.py:3-117`, `src/gnd/checker/__init__.py:20-258`: broad identity-preserving exports can look like repeated implementations to a symbol-only index. Keep them with public capability owners, not duplicate-of entries.
- No uncalled capability or missing-test claim was established. Importer stubs show production callers for every assigned module, and representative tests were found for every proposed entry; this does not establish complete test coverage.

## root1

- src/gnd/api.py:135, src/gnd/api.py:345 and src/gnd/api.py:1133: receipts, transition orchestration and incremental-session facade occupy the same 1221-line module. Worth considering separate implementation homes while preserving the public API; no refactor is proposed here.
- src/gnd/artifacts.py:173, src/gnd/artifacts.py:820 and src/gnd/artifacts.py:1385: canonical JSON, roster observation and atomic publication share a 1757-line infrastructure module. Potential split candidate, subject to dependency-home and identity-alias agreements.
- src/gnd/assurance_claims.py:3, src/gnd/assurance_evidence.py:3, src/gnd/assurance_inheritance.py:3 and src/gnd/assurance_transport.py:3: repeated capabilities are aliases rather than duplicate implementations; do not mark them duplicate-of. RF-D5 retirement is explicitly recorded in each shim.
- src/gnd/agent_cli.py:3 and src/gnd/agent_cli.py:68: adapter and neutral runner names are re-exported together. Treat this as a compatibility surface, not another process implementation.
- src/gnd/anchor_identity.py:16: supplied inventory reports no tests importing this defining module directly; tests/test_extract_manifest.py:294-307 exercises its identity behavior through the historical extraction surface. This is not evidence of missing behavioral tests.
- src/gnd/archsmoke.py:294 and src/gnd/agents.py:230: both run bounded subprocesses but have different mechanisms and contracts; smoke uses synchronous threaded capture and an entry-point startup pipe, whereas trusted adapters delegate to process.py. Consolidation would require a separate behavioral review.
- No module is declared dead solely because the inventory lists no package importer: __main__.py is executable, and generated smoke modules use archsmoke.py.

## root2

- Potential split, not a proposed edit: src/gnd/install.py:261, :481, :816, :1040, :1588, :1712 combines resource discovery/target resolution, manifest handling, placement policy, diagnosis and removal in 1,851 lines. The shared plan and ownership rules justify one lifecycle entry until a separate refactor is selected.
- Potential split, not a proposed edit: src/gnd/extensions.py:348, :683, :1213, :1469, :2117, :2416 combines partial/exact relation machinery, joins, aggregates, stratified execution, selective refresh and derivation-claim obligations in 2,990 lines. Retain one capability owner now, with its public effective_view and structured_extension_view searchable.
- Potential split, not a proposed edit: src/gnd/correspondence.py:401, :842, :1050, :1129 houses indexed guarded evaluation, dispatch/reuse, decision composition and public witness projection. A future extraction should preserve this single decision authority and origin-based projection contract.
- Overlapping low-level checks: src/gnd/json_input.py:25-69 scans depth and duplicates before/inside calls to src/gnd/input_policy.py:33-99, which enforces them again. This is not evidence that either whole module is redundant: json_input retains its own refusal reasons, Decimal conversion and tighter limits.
- Intentional compatibility aliasing, not a duplicate algorithm: src/gnd/install.py:90-137 imports safefs mutation functions under historical names; src/gnd/extensions.py:2779 onward exports historical calculation aliases and sets historical checker identities. Preserve these according to the repository shim-retirement rules.
- Stale module documentation: src/gnd/install.py:3 claims it is the only filesystem writer and that other modules never persist state; src/gnd/declared_adapter.py:155-225 directly writes candidate files. The catalog description follows current behavior rather than that historical claim.
- No unused module or untested capability is asserted: the provided importer stubs show callers for all 18 modules, and subject tests were located for every proposed entry. This pass did not establish absence of unused individual symbols or exhaustive test coverage.

## root3

- Unused helper candidate: src/gnd/proof_currency.py:8 defines record_evidence_not_current; the supplied inventory reports zero package/test/script importers, and a search of tools/tests/scripts found no caller. Do not infer removal is safe for external users.
- Deliberate parallel algorithms: src/gnd/semantic_rows.py:39,133,154,171 implements indexed providers while src/gnd/semantic_spec.py:751,781,821,1098 retains reference scans. Preserve the distinction; tests/test_ik4_indexed_set_families.py compares production answers to the reference.
- Historical and current assurance rules differ: src/gnd/proof_kernel.py:277-289 admits current >= applicable with in_scope for proof-backed, whereas src/gnd/semantic_spec.py:1909-1915 refuses current > applicable and any out-of-scope case. The current checker explicitly observes Phase 1 as compatibility at src/gnd/checker/_core.py:451-475; these should not be consolidated from names alone.
- Broad module worth a separate refactoring review: src/gnd/semantic_spec.py:1-2634 combines scalar identity, family specifications, join refusals, applicability, verdict composition, band and assurance policy. No split is proposed in this read-only task.
- Mixed responsibilities: src/gnd/output.py:279-295 performs live assurance/receipt preparation in a predominantly text-rendering module; src/gnd/refscheme.py:284-307 adds shape signatures to reference identity helpers.
- Filesystem seams are not interchangeable: src/gnd/safefs.py:87 refuses symlink parents for destinations, while open_regular at line 532 follows symlink leaves for caller reads. Aliases at lines 498-525 retain artifact variants.
- No direct test importer in the supplied inventory for src/gnd/manifest_paths.py:7 or src/gnd/report_schema.py:11; their consumers provide indirect coverage, so this is not a claim of zero test coverage.
- Compatibility facade runtime behavior: src/gnd/semantic_registry.py:78-79 checks duplicate branch ids in addition to exports; retain that guard if reorganizing facade ownership.

## root4

- Mixed responsibilities worth considering separately during future code work: src/gnd/values.py:9 defines scalar identity, :49 interprets literals, :101 canonicalizes digest inputs, and :151-214 computes population/model/reference identities. One catalog entry owns the file as required; verbs expose the subsidiary jobs.
- Mixed responsibilities worth considering separately: src/gnd/universe.py:68-116 resolves reference typing, :184-215 dispatches constraint shape/scope, :306-367 collects occurrence universes, and :425-559 defines family hooks. Shared home placement alone does not make these one narrow API.
- Mixed responsibilities worth considering separately: src/gnd/transition.py:158 loads walk files, :568 declares report types, :926 applies one operation step, and :1909 orchestrates the walk. Its pure decision kernel is already separate at src/gnd/transition_kernel.py:10-126.
- Cross-group shim requiring combined catalog ownership, not duplicate status: src/gnd/extract/vocabulary.py:30-44 imports the implementation from src/gnd/vocabulary.py. Values/universe likewise expose identity-preserving compatibility names at src/gnd/values.py:225-241 and src/gnd/universe.py:382-421.
- The guarded operand adapter in src/gnd/terms.py:170 and the temporal boundary in src/gnd/temporal_guarded.py:32 both rebuild term syntax before evaluation. Their input/output contexts differ; no semantic duplication or consolidation recommendation is established here.
- src/gnd/transition_kernel.py:10-126 has no direct test import in the supplied inventory; tests/test_transition_report.py and tests/test_public_phase4_transition_support.py exercise its consumers. This is a direct-import observation, not a claim of missing behavioral coverage.
- No assigned module is import-orphaned in the supplied stubs; no unused-code claim is made from an import graph alone.

## synth

- src/gnd/synth/oracle/constructive.py:545 and :814: independent witness predicates and population construction passes share a 1714-line file; separating the semantic oracle from construction could make independence and reuse easier to inspect, subject to retained alias contracts.
- src/gnd/synth/boundary.py:719 and :2284: a 2376-line family-deriver catalog surrounds a smaller shared admission/dispatch API; family-specific homes could reduce reading costs while preserving public names.
- src/gnd/synth/service.py:218 and :547: _cmd_synth spans 568 lines and nests baseline resolution, sidecar construction, violating emission and quarantine handling. Existing _emit_boundary_corpus at :23 shows one extraction seam; no refactoring is proposed in these entries.
- src/gnd/synth/corpus_service.py:97, :111 and :210: closed index validation, publication transactions and reader-facing path resolution live together; measure imports validation/resolution helpers without using the transaction.
- src/gnd/synth/__init__.py:3: package documentation still describes a value-only layer that never assembles populations, although the same package now holds assembly and corpus generation. GENERATOR_VERSION at :23 is the initializer's actual exported capability.
- src/gnd/synth/paths.py:7 and :24: documentation names install.safe_destination, while the implementation imports the canonical home from gnd.safefs; update the documentation when a separate code/docs change is authorized.
- src/gnd/synth/frontier.py:637: unchecked route discovery observes the production checker, while no-subjects admission uses independent expected_state at :337. Preserve this explicit distinction when summarizing oracle independence.
- src/gnd/synth/oracle/state.py:211: row completion mirrors value-comparison coordination (its own docstring says so), a potential consolidation seam with builder coordination; the builder's full coordination body at constructive.py:1304-1361 was not read, so this is a review lead rather than a verified duplicate.
- src/gnd/synth/identity.py:14: no direct test importer was found in the supplied stubs; consumer tests explicitly cover numeric identity and boolean separation (tests/test_poolfile.py:192-221 and tests/test_synth_conforming.py:383-446). This is not a claim of absent behavioral coverage.
- No assigned module was established to be uncalled, and no whole-module duplicate was verified; the compatibility shims import the same implementation objects rather than reimplementing them.

## witness_examples_skills

- Intentional duplicates: src/gnd/examples/expense/extension.py:35 and project/cli/expense_cli.py:35; native_query.py:16 and project/cli/native_query.py:16; reporting.py:4 and project/cli/reporting.py:4 are byte-identical. tests/test_ready_projects.py:16 pins these twins, so consolidation would require preserving copied-project behavior.
- Repeated reporter: src/gnd/examples/bookrec/rules_in_pyrel.py:120 and src/gnd/examples/expense/rules_in_pyrel.py:162 repeat the findings-to-lines/exit-code implementation. Both scripts are standalone examples, so a shared helper would need a portability decision.
- Repeated bot helpers: src/gnd/examples/plan_apps/access/stand_in_bot.py:14, clinic/stand_in_bot.py:14, lease/stand_in_bot.py:14 and trip/stand_in_bot.py:14 repeat witness normalization, and their :21 failures helpers repeat attempt flattening; course/stand_in_bot.py:24 accepts only dictionaries, so it is not a drop-in identical helper.
- Possible split: src/gnd/examples/plan_apps/core.py:69, :156, :214, :240, :280, :308 and :341 combine emitted-rule extraction, two checker adapters, text parsing, publication and the bot retry loop. The single main job remains the tutorial plan application.
- Possible split: src/gnd/witness/io.py:158, :280 and :378 combine certificate shape, identity and conservative fragment classification; the file has no evaluator but holds several separately useful structural seams.
- Possible split: src/gnd/witness/service.py:42 and :214 combine composition lineage binding and why-not orchestration with witness/replay input handling; keep the public compatibility aliases at :305 in mind if splitting.
- No focused executable test established for src/gnd/examples/expense/prepare_currency.py:18, src/gnd/examples/release_governance/prepare_facts.py:7 or src/gnd/examples/release_governance/pyrel_queries.py:11. tests/test_external_runtime_tutorials.py:113 verifies saved governance checkpoints, which is weaker evidence than executing those helpers.
- No focused test established for src/gnd/examples/approvals/stand_in_agent.py:32; tests/test_pyrel_stand_in_sessions.py:68 parametrizes only BookRec and expense.
- src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py:472 defines _install_native_kimi, which tests call, while the production _apply path at :380 verifies and executes the two halves directly. This is a test-used convenience wrapper, not proof of unused functionality.
- Import inventory alone is misleading for standalone files: launchers, stand-in scripts and bundled skill helpers are invoked by path/subprocess or documented commands, so zero package importers is not evidence that they are dead code.
- src/gnd/witness/types.py:15 and src/gnd/witness/why_not.py:45 intentionally use different limits/envelopes: near-miss truncation and why-not pre-evaluation budgets do not belong to finite certificate proof limits.

## Mechanical leads (components_index.py review)

```text
## Descriptions older than their code (not computed: the catalog has no git history here) (0)

## Retired components that are still called (0)

## Components that import each other (2)
check.applicability <-> check.branches: check.applicability imports check.branches in 1 place(s): src/gnd/applicability.py -> src/gnd/branches.py; check.branches imports check.applicability in 1 place(s): src/gnd/semantic_registry.py -> src/gnd/applicability.py
exp.service <-> exp.session_runtime: exp.service imports exp.session_runtime in 1 place(s): src/gnd/exp/session.py -> src/gnd/exp/session_runtime.py; exp.session_runtime imports exp.service in 1 place(s): src/gnd/exp/session_runtime.py -> src/gnd/exp/session_control.py

## Retired components nothing calls (ready to remove?) (0)

## Components nothing in the package imports (an entry point, or unused?) (18)
cli.dispatch (defines main)
agent.architecture_smoke
assurance.claims
semantics.proof_currency
examples.session_agents (defines main)
examples.book_recommendations (defines main)
examples.book_rules (defines main)
examples.expense_application (defines main)
examples.expense_reports
examples.expense_evolution (defines main)
examples.expense_rules (defines main)
examples.plan_apps (defines main)
examples.refund_learning (defines main)
examples.governance_facts (defines main)
examples.governance_reports (defines main)
skills.migration_verify (defines main)
skills.model_structure (defines main)
skills.harness_update (defines main)

## Modules nothing in the package imports, inside a component that is used (3)
src/gnd/agent_cli.py (agent.invocation)
src/gnd/assurance_inheritance.py (assurance.inheritance)
src/gnd/exp/session_v7.py (exp.session_runtime)

## The same public name in two or three components (a duplicate?); 4 name(s) defined in four or more modules are left out (24)
band (same signature): src/gnd/checker/_reports.py (checker.reports), src/gnd/transition.py (semantics.transitions)
refused (same signature): src/gnd/export/lean_types.py (export.lean_lowering), src/gnd/export/souffle_types.py (export.souffle_lowering)
write_manifest (same signature): src/gnd/codegen/manifest.py (codegen.manifest), src/gnd/install.py (install.skill_lifecycle)
yaml_stream_guard_error (same signature): src/gnd/model/_validation.py (model.validation), src/gnd/skills/gnd-model-from-text/scripts/validate_model.py (skills.model_structure)
ApplyResult: src/gnd/codegen/plan.py (codegen.regenerate), src/gnd/install.py (install.skill_lifecycle)
Manifest: src/gnd/composition.py (model.composition), src/gnd/install.py (install.skill_lifecycle)
ManifestError: src/gnd/extract/manifest.py (extract.manifest), src/gnd/install.py (install.skill_lifecycle)
ModelIndex: src/gnd/export/pyrel_runtime.py (export.pyrel_runtime), src/gnd/model_index.py (model.query_index)
VerdictCounts: src/gnd/evaluation_feedback.py (check.evaluation_feedback), src/gnd/exp/session_eval.py (exp.acceptance)
Work: src/gnd/discover/support.py (discover.population_view), src/gnd/export/ilp.py (export.ilp_neutral)
calculate: src/gnd/examples/bookrec/extension/bookrec/native_query.py (examples.book_recommendations), src/gnd/examples/expense/native_query.py (examples.expense_application), src/gnd/examples/expense/project/cli/native_query.py (examples.expense_application)
checked_limits: src/gnd/export/lean_types.py (export.lean_lowering), src/gnd/export/souffle_types.py (export.souffle_lowering), src/gnd/witness/types.py (witness.schema)
digest: src/gnd/export/souffle.py (export.souffle_lowering), src/gnd/judgments.py (semantics.saved_judgments)
evaluate: src/gnd/exp/session_judgments.py (exp.session_judgments), src/gnd/transition.py (semantics.transitions)
identity: src/gnd/discover/support.py (discover.population_view), src/gnd/witness/io.py (witness.schema)
integer: src/gnd/judgments.py (semantics.saved_judgments), src/gnd/witness/io.py (witness.schema)
load: src/gnd/examples/expense/rules_in_pyrel.py (examples.expense_rules), src/gnd/examples/refunds/stand_in_learner.py (examples.refund_learning), src/gnd/input_policy.py (infra.input_policy)
parse: src/gnd/export/souffle.py (export.souffle_lowering), src/gnd/judgments.py (semantics.saved_judgments)
prepare: src/gnd/exp/session_judgments.py (exp.session_judgments), src/gnd/export/souffle_runtime.py (export.souffle_runtime)
publish: src/gnd/examples/bookrec/extension/bookrec/cli.py (examples.book_recommendations), src/gnd/examples/plan_apps/core.py (examples.plan_apps)
read_manifest: src/gnd/codegen/manifest.py (codegen.manifest), src/gnd/install.py (install.skill_lifecycle)
replay: src/gnd/exp/session_judgments.py (exp.session_judgments), src/gnd/witness/service.py (witness.service)
report: src/gnd/examples/bookrec/rules_in_pyrel.py (examples.book_rules), src/gnd/examples/expense/rules_in_pyrel.py (examples.expense_rules), src/gnd/examples/release_governance/pyrel_queries.py (examples.governance_reports)
run: src/gnd/exp/session_runtime.py (exp.session_runtime), src/gnd/export/pyrel_runtime.py (export.pyrel_runtime), src/gnd/witness/cli.py (witness.command)

## Modules listed under more than one component (0)

## Components that cover more than 12 modules (more than one capability?) (0)

## Components with no tests listed (3)
semantics.proof_currency
examples.governance_facts
examples.governance_reports

## Test files that import one component only and are not in its tests (31)
agent.invocation: tests/test_rf1_agent_cli_pins.py
assurance.evidence: tests/test_public_assurance_inputs_support.py, tests/test_public_corpus_matrix.py, tests/test_v6_phase6_evidence_reader.py, tests/test_v6_phase6_runtime_identity.py
assurance.policy: tests/test_public_corpus_finite_support.py, tests/test_public_policy_separation.py
check.branches: tests/test_v62_phase2_registry.py
check.incremental_reuse: tests/test_incremental_performance.py
checker.evaluate: tests/test_public_derivation_identity.py
cli.api: tests/test_agent_recordings.py, tests/test_bookrec_tutorial.py, tests/test_expense_tutorial.py, tests/test_external_runtime_tutorials.py, +25 more
cli.dispatch: tests/test_doccheck.py, tests/test_fidelity_stub_gate.py, tests/test_public_extract_boundary.py, tests/test_public_fidelity_scope.py, +3 more
conformance.report: tests/test_public_expense_current.py
evolve.schema: tests/test_public_binding_graphs.py
exp.acceptance: tests/test_exp_feedback_derivation.py, tests/test_exp_payload_derivation.py
exp.close: tests/test_public_floor_lifecycle.py
exp.frontmatter: tests/test_public_frontmatter_declarations.py, tests/test_public_planning_frontmatter_local.py
exp.schema: tests/test_public_walk_floor_contract.py, tests/test_v61_phase5_contract.py, tests/test_v61_phase6_contract.py
exp.session_store: tests/test_v72_phase5_session_mechanics.py
export.applications: tests/test_bookrec_pyrel_application.py, tests/test_expense_pyrel_application.py, tests/test_pyrel_stand_in_sessions.py
export.pyrel_runtime: tests/test_pyrel_export_boundaries.py
infra.artifacts: tests/test_public_binding_rosters_scaling.py, tests/test_public_v71_full_judgments.py, tests/test_public_v72_full_json_boundary.py
infra.exit_codes: tests/test_rf2_instrument.py
infra.report_payloads: tests/test_public_admission_schema_mutations.py, tests/test_public_book_boundaries.py, tests/test_public_book_identity.py, tests/test_public_book_skills.py, +4 more
infra.version: tests/test_public_book_workflow.py, tests/test_public_payload_alias_sites.py, tests/test_rf4_review_regressions.py
install.skill_lifecycle: tests/test_public_installer.py
model.address: tests/test_coverage_derivation.py
model.architecture: tests/test_public_architecture_smoke_ids.py
model.loading: tests/test_derivation_rule.py, tests/test_public_aggregation_admission_layers.py, tests/test_public_guarded_temporal_coverage.py, tests/test_v62_phase1_classification.py, +5 more
model.verbalization: tests/test_v62_phase6_verbalization.py
review.adapters: tests/test_skill_prose_sync.py
semantics.phase1_slice: tests/test_v6_phase1_kernel.py
semantics.saved_judgments: tests/test_ike_q3.py
semantics.snapshot_adapter: tests/test_public_semantic_foundation_local.py
semantics.transitions: tests/test_public_phase4_observations.py

## Flow steps that no earlier step imports (wrong order, or reached another way?) (0)

## Entries marked as checked in part (59)
codegen.emit
codegen.regenerate
conformance.structural
conformance.architecture
conformance.report
discover.service
cli.checking_command
cli.exp_command
cli.lifecycle_command
evolve.service
evolve.schema
evolve.command
recovery.inventory
recovery.schema
recovery.verify
recovery.command
review.schema
review.service
exp.schema
exp.service
exp.acceptance
exp.close
exp.session_store
exp.tests_runner
export.pyrel_runtime
export.pyrel_rules
export.lean_lowering
model.validation
checker.evaluate
infra.artifacts
check.branches
check.service
cli.api
cli.dispatch
assurance.claims
semantics.extensions
check.snapshot_decision
semantics.saved_judgments
check.element_coverage
install.skill_lifecycle
model.population_loading
model.verbalization
model.reference_schemes
check.population_structure
model.population_shape
infra.safe_filesystem
infra.bounded_process
infra.report_payloads
semantics.phase1_slice
model.rai_import
infra.report_redaction
semantics.snapshot_adapter
semantics.snapshot_spec
semantics.transitions
agent.solve
infra.verdict_prose
synth.constructive
synth.mutations
synth.boundary

## Modules with no docstring (the search cannot describe them) (21)
src/gnd/batch.py
src/gnd/commands/checking.py
src/gnd/commands/codegen.py
src/gnd/commands/conformance.py
src/gnd/commands/discover.py
src/gnd/commands/doccheck.py
src/gnd/commands/evolve.py
src/gnd/commands/exp.py
src/gnd/commands/export.py
src/gnd/commands/extract.py
src/gnd/commands/fidelity.py
src/gnd/commands/judgments.py
src/gnd/commands/lifecycle.py
src/gnd/commands/measure.py
src/gnd/commands/recovery.py
src/gnd/commands/review.py
src/gnd/commands/solve.py
src/gnd/commands/synth.py
src/gnd/commands/verify.py
src/gnd/commands/witness.py
src/gnd/synth/corpus_service.py

## Modules with no component (0)

review: 161 lead(s) in 8 group(s), from 238 component(s) and 302 module(s); each is a place to look in the code, not a finding
```
