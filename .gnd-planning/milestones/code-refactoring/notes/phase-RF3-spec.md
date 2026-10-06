# RF3 spec — break the core cycle

Status: owner-decided (2026-10-05), delegated approval auto=true; implementation follows recorded artifact approval.

## Provenance

Effective approved plan r2+e1, sections 0–10; records 001–007, especially RF0 D10/OQ5, RF1 surface inventory and RF2 instrument amendment. User authorization: “process-phase RF3 auto”. Decisions here are delegated agent rulings, not a claim that the human read these bytes. No optional spec panel. Base: 8ff996f7cf0d17bb08f539bca1f4a116ed839fec.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| §4 RF3 | errors/documents/values/universe leaf responsibilities; explicit two-variant resolver; public effective_view; higher applicability; rename checker rebindings before split; shared derivation ContextVar | Design lanes A–D, G2 |
| RF3-C1 | No runtime multi-module SCC in core, lazy/dynamic included; layering without xfail | G2 structural predicates and dirty controls |
| RF3-C2 | Core private imports strictly better than 64 at base | Target <=60, G6 |
| RF3-C3 | Every semantic_registry owner resolves to function | G2 registry resolution with nonexistent-owner control |
| SM1 | RF1 expected artifacts unchanged | G1, frozen-file identity |
| SM2 | Every moved name shim-importable, new lookup patches observed | Move ledger and G2 effect controls |
| SM3 | Source scans and unloaded guards widen with moves | Measured patch/scan inventory, G2/G4 actual closure visits |
| SM4 | New modules mapped; clean layers remain clean | G2 layering/map controls |
| §9 | “SM1–SM4; layering test without xfail; owner-string resolution” | G1–G4; checker/model/population/references/transition selections |
| 002 F7, RF0 D10 | Core cycle RF3, assurance/synth/api RF4, session RF8; allow-list zero and cannot grow; RF6 package split distinct | G2 zero allowance, no RF6 ModelIndex/registry feature |
| RF0-OQ5 | semantic_spec literal dynamic import of terms counted | G2 graph includes this edge; retain wrapper algorithm |
| §5 | AGENTS/CONTRIBUTING current layer/shim guidance; count skill citations | 9 citations at base; preserve old paths, update only if necessary; twin integrity |
| §6 | Digest/verdict/patch/scan drift, double authority, budgets, measurement and path drift | G1–G6, authority and boundaries |
| §7 | No feature/tightening/certification/broad-history/source-owned OQ changes | Out-of-scope |
| RF2 carryovers | Original goldens and verified per-minor successors; 34 live shims; manifest amendment named scope only | Preserve successor answers and approve separate bounded RF3 manifest disposition |
| RF1 carryovers | Unpaid pins follow RF4/5/6; support OQ7 if original support edited | Original rf1 support unchanged; inherited ownership retained |

## Standing rules

RF-R1 behavior: preserve schemas, exits, issue order, text and identity algorithms. RF-R2: move bodies verbatim; divergent encoders separate. RF-R3: G1 pre-move pins green; unpinned moved surface gets source-base observation before move. RF-R4: rebinding rename unit first; subsequent atomic units include aliases, patches, scans and mapping, each green. RF-R5: explicit shim rows, RF-D5 retirement. RF-R6: real scan visits cover new homes. RF-R7: existing named source handoff persists; source-side control remains owner attestation, no new human attestation invented; source remote unavailable, no ledger/guard edit. RF-R8: prior production/release evidence unavailable over new bytes. RF-R9: base measured target and ceilings below. RF-R10: no feature or tightening. RF-R11: measured focused closure, no full-default replay.

Paid rules: totality and input/algorithm bounds preserved in moved loaders (no new policy); validation order and issue collection pinned; one walk for universe and explicit resolver variants, no divergent merge; normative prose remains one home with references; representation questions decided by observations, not new assertions. Coverage per branch includes truthy versus strict flags, cycle/missing/ambiguous resolver, legacy/exact/opaque effective views, context reset, invalid owners, lazy/dynamic graph edges, stale patches and missing scan homes.

## Goal

Selected gates exit 0, all RF3 layer edge controls run without xfail, no runtime SCC touches multiple core modules, and core private-import sites <=60 (baseline64).

## Design

A. Before splitting checker: rename the first check implementation to check_legacy, legacy derivation functions to evaluate_derivations_legacy and constraint_view_legacy, dispatch names retain explicit identities. Keep _PHASE3_LEGACY_CHECK/_PHASE3_LEGACY_EVALUATE_DERIVATIONS/_PHASE3_LEGACY_CONSTRAINT_VIEW/_evaluate_derivations/_constraint_view as compatibility aliases. Existing public check remains unchanged. No rebinding of FunctionDef names remains.

B. Leaf data/value responsibilities: errors owns issue/exception types and unchanged text; documents owns Model/DeonticNote and shared parser where needed; values owns scalar identity/literal sentinel and digest/refusal closure; universe owns the explicit resolver entry primitive_for(object_type_id, object_types, *, variant: Literal["truthy", "strict"], seen=None). Preserve both old algorithm branches separately; unknown variant raises ValueError, new interface only. universe owns pure lookup, subtype/denotation/instance and classifier helpers. Derivation-term ContextVar has one shared instance, original name and object-identity cache behavior. Old imports alias exact objects.

C. Break orchestration cycles through actual dependency extraction, never hidden imports. Extension calculation closure moves to extensions below checker, with public effective_view(model, population) supplying precisely current opaque/exact/legacy selection; checker re-exports it. Registry descriptors/branch trace live in branches; applicable_scope_ids(model, population)->tuple[str,...] lives in applicability above extension evaluation. semantic_registry remains compatibility facade; lower consumers import descriptor home directly. Adapter imports universe/values/errors rather than checker. Bridge imports universe. Remove temporal↔correspondence dependency by sharing canonical-row calculation in a lower semantic utility (preserving canonical comparator). Reference loading/validation orchestration may co-locate with model intake, with references as facade; separate identity and document types remove population/model backedges. No full RF6 model package split.

D. Layering collateral: generic anchored-input/identity, vocabulary/reference-scheme and report-schema/path-validation functions move to appropriately lower homes with old aliases. Leaf modules have no higher imports; document/runtime annotations use TYPE_CHECKING where appropriate. Classify proof kernel and declarative IR/spec/registry and pure verbalization at their true lower ranks with named responsibility reasons; do not lower a module that still evaluates upper behavior to evade a gate. Keep all original layer scope modules and zero allow-list. Document every concrete moved symbol, source body and destination in RF3-moves.json before its unit ships.

Exact legacy signatures and bodies are the source-base AST/source segments, bound in move ledger; no schema changes. Public effective_view(model: Model, population: Population) returns the same effective fact view currently selected by applicability. Public resolver exposes explicit variant; caller wrappers pin prior choice. New files estimated errors160, documents250, values350, universe450, extensions3000, branches1450, applicability500, ancillary lower homes900 lines; most relocated, not new code.

## Decisions — delegated approval (auto=true), 2026-10-05

| ID | Ruling and cost |
|---|---|
| D1/RF-D9 | Prose approval: this is move work, existing approved bytes supply answer corpus; new structural predicates have dirty controls rather than serialized-format changes. No optional panel. |
| D2 | Preserve RF-D6 variants, RF-D10 shims, RF-D11 divergent algorithms; explicit new resolver variant only, old callers retain choices. |
| D3 | Target <=60 core private sites from64; no core SCC; allow-list remains0. Baseline count uses sources assigned model/checking/semantics; report both fixed original cohort and current-layer metrics so reclassification cannot conceal regression. |
| D4 | Atomic rename first, then dependency closures with compatibility/patch/scan updates. Moved bodies cannot change within their move commit except explicitly approved FunctionDef name/signature boundary; behavior edits, if needed, later unit. |
| D5 | Production touched files<=90; moved lines<=10000; added non-relocated production<=700; added handwritten test<=1600; non-evidence files<=150. Any overrun receives dated delegated amendment retaining original ceiling and arithmetic. |
| D6 | Bounded RF3 curated-manifest adaptation for existing changed rows only; preserve before/after SHA/bytes/mode and reason. No units.json or distribution guard edits; no release attribution or publisher. RF0-vs-plan reconciliation stays close. |
| D7 | Source authority remains previous approved control/attestation; no reachable source remote provided. If contrary source change evidence appears, stop. No certification selected. |
| D8 | One required independent Codex CLI reviewer as skill step4 (native authenticated provider, stdin prompt, read-only, xhigh); at most initial plus one bounded repair review, triage/reproduce before fix. This invocation selects that required review within RF3 scope. |

## Tests and verification-selection ledger

All run entries expect exit0, preserve configured exclusions, and become unavailable when listed inputs change. Tests are serial within this shared checkout; no xdist. Exact commands use .venv/bin/python -m pytest -q -p no:cacheprovider and --tb=short.

| Gate | Disposition/selection | Input boundary and invalidation |
|---|---|---|
| G1 | run: tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py; plus tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py | All existing characterized changed boundaries; frozen expectations; supported interpreter identities; rerun after any move |
| G2 | run: tests/test_rf1_layering.py tests/test_rf3_core.py | Full scope/map/owners/resolver/view/context/shim/scan branch cases; known-dirty controls for each instrument |
| G3 | run: tests/test_checker_families.py tests/test_model_validation.py tests/test_model_v2.py tests/test_population_load.py tests/test_model_guarded.py tests/test_derivation_rule.py tests/test_derivation_covers.py tests/test_public_semantic_adapter.py tests/test_public_semantic_applicability.py tests/test_public_derivation_evaluator_controls.py | Actual model/population/error/universe/derivation/adapter consumers, not full historical proof replay |
| G4 | run: tests/test_reference_population_corpus.py tests/test_transition_corpus.py tests/test_transition_report.py tests/test_transition_mapping_totality.py tests/test_model_verbalization.py tests/test_measure_offline.py tests/test_extract_manifest.py tests/test_v70_phase1_adversarial.py | Reference binds/digest/refusals, transition and render/source-scan dependencies |
| G5 | run: tests/test_development_scaffold.py tests/test_gnd_arch.py; ruff check every changed/new Python path | Packaging scaffold, tools and style |
| G6 | run: .venv/bin/python tools/gnd_arch.py measure --out .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-head.json and compare 8ff996f7cf0d17bb08f539bca1f4a116ed839fec HEAD after move commit; assertion budget/metric controls | Actual committed imports/body identities/map, no inherited changed-source verdict |
| Broad default/evidence/census/proof/distribution/provider/native/history | cadence: explicit owner request or separately configured CI; no local run | Changed shared code invalidates old evidence; focused current-byte controls are narrower claims |

G2 names: no core SCC including dynamic semantic_spec edge; all-layer original core wrong-way absence; owner resolution and dirty unknown owner; old/new object identity; new lookup effect; resolver flags true/false/1/0/string/missing/cycle/ambiguity; effective ordinary/exact/opaque equal predecessor; ContextVar identity/reset; scan home visitation and planted import refusal. Original goldens/support unchanged. Mutation retargeting changes only moved source stimuli, same ids/expect_red; run only affected changed stimuli when required.

## Out of scope and boundaries

No new semantics, CLI/flags/schema, tightening, ModelIndex/constraint-family registry, source-owned OQ transfer, broad historical repair, release/publisher/certification or acceptance claim. RF4 owns peripheral cycles, RF6 owns remaining model-query split and standalone PyRel format decision, RF8 sessions. Pins prove selected preservation, not all-model correctness; local macOS runtimes do not establish other OS results. One reviewer is one reviewer. Original RF1/RF2 open questions remain with named prior owners except RF0-OQ5 discharged by measured dynamic edge cycle removal. Co-change remains unavailable (RF0 D3).

## Size and implementability sweep

Measured base has148 modules, 14-member core runtime SCC,64 original-core private sites,27 wrong-way edges,9 skill citations. Target60<64. Sizes are estimates; budgets D5 apply actual diff. Every criterion has a falsifiable gate: aliases alone cannot remove cycles, so imports must reroute to real lower dependency closures. Full current core scope is retained; no allowance can hide an edge. No pin answer change is authorized by pretending it is a move; structural/source-location instruments may be amended under delegated scope with original answer retained. Compiler/runtime facts are tested.

## Approval instrument

Spec prose and existing frozen source-base corpora. Exact pre-approval artifact SHA recorded separately in phase-RF3-approval.json before any implementation edit.

## Implementation findings

None yet.

### F1 — pre-move environment, 2026-10-05

Initial sandboxed G1: 447 passed,7 failed, all seven caused by macOS confstr warning appended to subprocess stderr. The unchanged agent module rerun without filesystem sandbox:13 passed,exit0. This is environment evidence, not production repair. Final subprocess gates use that environment.

### Delegated implementation clarification A1

Before split, the rename unit runs the complete G1; intermediate move units run G1 and their direct/affected controls while existing layering failures retain their prior strict markers. Final RF3 requires G2 with all16 RF3 markers removed. Requiring final no-SCC predicates before the moves that remove those SCCs is impossible; no intermediate unit claims RF3 completion. Body moves preserve source segments, then import-routing/explicit-interface edits land in subsequent commits.

### F2/A2 — accumulated shim inventory

Rename G1 had453 passed/one failed because RF2 test counted all milestone shim rows as RF2. Delegated amendment scopes its34-row assertion to RF2 rows; retains all34 expected names and identity/effect assertions, while RF3 has its own complete new-row guard. No behavior-golden answer changed.

### F3 — dependency closures and identity

Split controls reproduced missing registry globals/ring constants, historical exception module-name changes, duplicate reference-context classes after a mistaken facade restore, and a module alias shadowed by the local extensions variable. Each was corrected before its move commit. Original body hashes and old/new object identity controls now pass; no expected behavior artifact was changed. Imported checker helper bindings used by the owner-characterization consumers are retained as explicit historical exports.

### F4/A3 — formatting-sensitive mutation and lint repair

Delegated amendment (auto=true), 2026-10-05: the anchored mutation now matches the same unique function signature and injects the same refusal before its imports. Import sorting had invalidated its source-location match; original id and expected-red node remain unchanged, with before/after retained. A reduced lint selection accidentally removed pre-existing suppressions for excluded rules; original annotations and moved bodies were restored, and verification uses the full configured lint selection. The dynamic inference guard now patches the actual extensions globals. The move-body guard binds this unit verbatim; later routing changes will check that committed snapshot rather than claim the final edited bodies remain verbatim.

### A4 — concrete routing interface, 2026-10-05

Delegated approval (auto=true): use universe.primitive_for with the explicit variant keyword, preserving universe.resolve_primitive(id, Model) as the existing strict-signature compatibility entry. This corrects the initially specified name collision and assigns object-type lookup to universe. The original proposed signature above is retained in the pre-approval artifact at eff8693. Move shared MAX_YAML_EVENTS and structured_derivation_ids into documents verbatim, with model aliases and explicit rows. Check the 232 original move bodies at commit 4415327, independently of subsequent routing changes. G4 replaces nonexistent test_extract_anchors.py with actual anchor controls in test_extract_manifest.py plus test_v70_phase1_adversarial.py; no expected answers change.

### F5/A5 — refuted layer-wide SCC premise

The first structural control failed because assurance is in the baseline semantics layer. RF0 D10 (notes/phase-RF0-spec.md:260), approved by the owner, explicitly assigns that SCC to RF4. Delegated approval (auto=true), 2026-10-05: RF3-C1 tests the original RF0/RF3 core SCC plus every new home; all original/current model/checking/semantics wrong-way edges must still disappear, and the original full-layer private cohort remains fixed. The original all-layer-SCC prose above was too broad; it is refuted, not retroactively claimed green. The unchanged assurance SCC remains visible with the other RF4/RF8 work, no allow-list growth or layer reclassification. RF3-OQ1 assigns reconciliation of the plan’s layer-wide wording with D10 to milestone close.

### F6/A6 — measured size ceiling amendment

Delegated approval (auto=true), 2026-10-05: retain original D5 ceiling 700 added non-relocated production lines as an underestimated premise. The worktree preview of the unchanged RF0 comparison algorithm is 7935 added minus 5948 moved-in = 1987 (includes 865 added blank lines, 179 historical module-name assignments, 227 compatibility-export annotations and 231 simple private-name alias assignments; categories overlap and are not summed). The split’s 234 aliases and preserved qualified type identities are required by SM1/SM2, not new behavior. Set this one ceiling to 2200; all other ceilings remain 90 production files / 10000 moved lines / 1600 handwritten test additions / 150 non-evidence files. Final commit-based arithmetic must fit 2200 and is separately bound; preview is not final evidence. This amendment precedes the routing commit.

### Routing gate observations

G2 first controls exposed test-instrument assumptions: Branch uses production_owner, effective facts are the historical _RuledFactView rather than a serializable Population, and the architecture reader uses binary Path.open rather than read_text. Corrected the controls at their original sites, with failing runs retained. The dirty lazy-cycle test now asserts the actual binary reader was intercepted before it asserts refusal. Final core/layer/move controls:61 passed, exit0. Focused downstream G3/G4:1326 passed,3 deselected,exit0. Routing G1:454 passed,exit0. No original expected behavior bytes changed. Source qualified names are retained for errors and moved callables; the old model resolver signature now explicitly selects truthy while the population resolver selects strict.

### F7/A7 — unloaded inference scanner successor

The routing patch suite reproduced two stale assertions that the witness import closure must include checker. It now includes universe and terms, with the checker backedge removed. Inspection also found the frozen packed inventory’s details filter recognizes checker/terms/producer but cannot recognize extensions. Delegated amendment (auto=true), 2026-10-05: leave the packed bytes and answers unchanged; add an explicit RF3 successor scanner over the actual original graph that widens details to extensions and recognizes both original private names and public aliases. Retain the original predecessor result separately. Require actual visitation of every new home, direct and transitive planted imports through checker and extensions (private/public), and an absent-home refusal. Correct the live closure assertion to universe/terms; this is a source-location instrument change, not a behavioral golden change.


### F8/A8 — independently reproduced review findings, 2026-10-05

The owner explicitly approved sending the RF3 prompt and inspected source/diff to the Codex provider. The native supported gpt-6-sol/xhigh read-only reviewer returned two findings, retained verbatim (declared machine-path substitutions) in phase-RF3-codex-review.md. One reviewer is one reviewer; this is not a panel opinion.

| Finding | Reproduction before repair | MVP disposition and authorized repair |
|---|---|---|
| R1 stale adapter.checker lookup | review-pre-fix-guards: dependency-graph mutation control fails AttributeError; review-pre-fix-primitive: three unchanged primitive tests fail AttributeError, while review-base-primitive proves all three pass against RF3 base | Blocking SM2: retarget checker.check and moved extensions calculator/obligation at actual lookup sites, keeping inputs/assertions/mutation ids and outcomes unchanged. |
| R2 blind witness evaluator guards | review-pre-fix-guards: both no_evaluator helpers fail to intercept a real effective_view calculator; eighteen direct old/public calculator/term lookup controls also fail | Hardening required by SM2/SM3: retain old checker/terms sentinels and additionally patch the defining extensions globals and public aliases, including borrowed term globals. No proof semantics repair or broad replay. |

Delegated approval (auto=true), process-phase RF3 auto: A8 expands focused impact closure to test_rf3_review_regressions.py, test_v6_phase2_adapter_mutations.py, test_public_adapter_primitive_controls.py and the existing affected witness/adapter controls. Each regression is already red against the pre-fix bytes; retain logs. Preserve all approved expected answers, frozen packed corpus, the 28 adapter mutant stimuli/expected nodes, production source, budgets and prior boundaries. The three adjacent primitive failures are the same independently reproduced lookup defect. One bounded repair review will inspect only these fixes and neighbours, as D8 already declared.
