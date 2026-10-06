# RF3 verification retained — independent review pending

Status: implementation committed; phase completion is not claimed. User authorization is process-phase RF3 auto. Commits eff8693 (rename), 4415327 (verbatim move), c9efd66 (routing) preserve the required ordering. The required independent Codex review did not execute: automatic approval review rejected sending RF3’s prompt and inspected source/diff without explicit authorization for the Codex provider. The authorization question is pending. No review opinion, completion record or broader acceptance is invented.

## Measured result

The original 14-member core runtime SCC and every new home are acyclic, including lazy and literal dynamic imports; all16 RF3 layering cases pass without xfail. Original/current core-layer wrong-way edges are absent. Fixed original-layer private-import cohort:64 →20 (target<=60); all private sites242 →198; wrong-way edges27 →8; modules148 →162; skill citations9 →9; allow-list0. RF0 D10 assigns the four remaining peripheral SCCs to RF4/RF8. The original layer-wide SCC statement is explicitly refuted in F5/A5, with plan reconciliation owed at milestone close.

Commit comparison:38 production files,5948 moved lines,1987 added non-relocated lines (original700 ceiling amended to2200 before routing),509 handwritten test additions at c9efd66 and62 non-evidence files. Ten later explicit coverage cases add only test lines; all remaining ceilings are unchanged. Source metrics bind c9efd66; subsequent coverage changes do not change production source. Historical qualified names, alias identity, separate identity algorithms and original fixture bytes remain pinned. Curated manifest adaptation touches26 existing changed rows, retaining before/after identities; units.json and the distribution guard remain unchanged.

## Gate output

Full retained command/output logs declare path sanitization in their headers. The following commands and summary lines are copied from those artifacts; no broad lane was selected.

### routed-G1

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py --tb=short
    454 passed in 63.60s (0:01:03)
    Exit: 0

### routed-G3-G4

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_checker_families.py tests/test_model_validation.py tests/test_model_v2.py tests/test_population_load.py tests/test_model_guarded.py tests/test_derivation_rule.py tests/test_derivation_covers.py tests/test_public_semantic_adapter.py tests/test_public_semantic_applicability.py tests/test_public_derivation_evaluator_controls.py tests/test_reference_population_corpus.py tests/test_transition_corpus.py tests/test_transition_report.py tests/test_transition_mapping_totality.py tests/test_model_verbalization.py tests/test_measure_offline.py tests/test_extract_manifest.py tests/test_v70_phase1_adversarial.py --tb=short
    1326 passed, 3 deselected in 65.58s (0:01:05)
    Exit: 0

### routed-patches-repair

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_public_v72_semantic_owners.py tests/test_public_derivation_evaluator_controls.py tests/test_public_adapter_derivation.py tests/test_public_applicability_obligations.py tests/test_public_derivation_cost_mutations.py tests/test_reference_population_corpus.py tests/test_rf3_moves.py --tb=short
    336 passed, 3 deselected in 37.67s
    Exit: 0

### routed-G5

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_gnd_arch.py --tb=short
    61 passed, 1 deselected in 8.29s
    Exit: 0

### routed-final-lint

    $ .venv/bin/ruff check src/gnd/admission_validation.py src/gnd/anchor_identity.py src/gnd/anchors.py src/gnd/applicability.py src/gnd/branches.py src/gnd/checker.py src/gnd/correspondence.py src/gnd/documents.py src/gnd/errors.py src/gnd/extensions.py src/gnd/extract/anchors.py src/gnd/extract/identity.py src/gnd/extract/manifest.py src/gnd/extract/refscheme.py src/gnd/extract/vocabulary.py src/gnd/extraction_scope.py src/gnd/judgments.py src/gnd/manifest_paths.py src/gnd/model.py src/gnd/model_verbalization.py src/gnd/population.py src/gnd/popvalidate.py src/gnd/proof_bridge.py src/gnd/redaction.py src/gnd/references.py src/gnd/refscheme.py src/gnd/report.py src/gnd/report_schema.py src/gnd/semantic_adapter.py src/gnd/semantic_registry.py src/gnd/semantic_rows.py src/gnd/temporal_guarded.py src/gnd/terms.py src/gnd/transition.py src/gnd/universe.py src/gnd/values.py src/gnd/verbalize_population.py src/gnd/vocabulary.py tests/support/public_adapter_mutation_controls.py tests/support/rf3_inference_inventory.py tests/test_public_adapter_derivation.py tests/test_public_applicability_obligations.py tests/test_public_derivation_cost_mutations.py tests/test_public_derivation_evaluation_complete.py tests/test_public_derivation_evaluator_controls.py tests/test_public_v72_semantic_owners.py tests/test_reference_population_corpus.py tests/test_rf1_layering.py tests/test_rf2_helpers.py tests/test_rf3_core.py tests/test_rf3_moves.py tests/test_v62_phase4_aggregate.py tests/test_v70_phase1_adversarial.py
    All checks passed!
    Exit: 0

### portable-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py tests/test_rf3_core.py tests/test_rf3_moves.py --tb=short
    496 passed in 70.84s (0:01:10)
    Exit: 0

### portable-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py tests/test_rf3_core.py tests/test_rf3_moves.py --tb=short
    496 passed in 71.17s (0:01:11)
    Exit: 0

### mutation-controls

    $ .venv/bin/python tools/rf1_pins.py mutate --out .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants --only M-HELP-canonical-json-gnd-extract-anchors-canonical M-HELP-canonical-json-gnd-transition-canonical M-HELP-identical-candidate-gnd-popvalidate-object-types-by-id M-HELP-model-digest-gnd-population-model-digest M-HELP-model-digest-gnd-references-reference-model-digest M-HELP-sha256-hex-gnd-extract-anchors-digest M-HELP-sha256-hex-gnd-population-content-digest M-HELP-validation-issues-gnd-exp-conclusions-validation-issues M-HELP-validation-issues-gnd-exp-spec-validation-issues M-HELP-validation-issues-gnd-extract-manifest-validation-issues M-SEM-check-coverage-anchored M-SEM-resolver-is-true --jobs 2
    rows: 12  killed: 12  not killed: 0
    Exit: 0

### final-G2

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf3_moves.py --tb=short
    71 passed in 5.37s
    Exit: 0

### coverage-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_core.py::test_resolver_reference_modes tests/test_rf3_core.py::test_plain_view_preserves_population_identity tests/test_rf3_core.py::test_analysis_reaches_the_shared_validation_cache --tb=short
    10 passed in 0.15s
    Exit: 0

### coverage-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_core.py::test_resolver_reference_modes tests/test_rf3_core.py::test_plain_view_preserves_population_identity tests/test_rf3_core.py::test_analysis_reaches_the_shared_validation_cache --tb=short
    10 passed in 0.14s
    Exit: 0

## Refactoring review

What did this phase reveal about existing structure that should change? Refactors EXECUTED: dependency closures now have explicit lower homes; reference orchestration co-locates with model intake while identity/data are leaf responsibilities; applicability uses one extension-view policy; caller signatures choose explicit resolver variants; stale patch and unloaded-scan instruments follow actual definitions. The quoted green focused gates cover these changes. The remaining large model intake/query split is assigned to RF6, peripheral cycles/layering to RF4 and session internals to RF8. Distinct canonical encoders are deliberately kept separate under the already approved semantic variants.

## Boundary

No completed phase or acceptance claim yet: process-phase step4 requires adversarial diff review. No full default, historical evidence/census/distribution, provider/native product lane, production publisher, certification or recertification was selected. The intended independent review is a development review, not a provider product gate. One reviewer is one reviewer; an independent opinion is not proof. Original goldens and per-minor successors plus these focused controls do not establish all-model correctness, unsupported minors, Linux/Windows results or the exact prior installed release. Old release/assurance identities remain tied to old bytes. Source authority rests on the prior owner attestation; no independently reachable source remote was supplied. No whole-tree manifest or new source-owned handoff is claimed. The packed historical inference inventory stays unchanged; the separately identified RF3 successor widens its static import filter, not an execution call graph.

## Open work

- Independent Codex review: requires explicit RF3 provider authorization; reproduce and triage any returned finding before repair; at most one bounded repair review.
- Completion record008 and original-site RF0-OQ5 discharge annotation remain owed after review, followed by final record commit and PR update.
- RF3-OQ1 → milestone close: reconcile layer-wide RF3-C1 wording with the explicit prior RF0 D10 peripheral SCC owners.
- RF3-OQ2 → RF6: finish model intake/query organization using the preserved signatures and aliases; this phase does not introduce ModelIndex or a family registry.
- RF-D5 → first public release after RF6 plus explicit retirement approval: all compatibility shims remain live.
- RF2-OQ1/3 and RF1-OQ3 → milestone close; RF2-OQ2 → RF6/export successor; RF1-OQ2/4 and RF0-OQ6 → RF8; RF1-OQ5/6 → successor; RF1-OQ7 → next actual rf1 support edit. All prior boundaries and source-owned OQs retain their ownership.

## Evidence SHA-256

- .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py311.json: 6d96ddce89309ef25db3f796026f6fa0865b3ee45bb30513877dfce1c34d26f3
- .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py311.txt: 36361d4b077146a2789850d308fdf7dc05d10b42d7f4d2585dcc0d9848917250
- .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py313.json: 7ac62bfb15e53a3a9684070001ae4200219cede456550751965874e8aff3f191
- .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py313.txt: 54e04552ed4b940006df81f6a0cc26a2493339779ef862f17832f4b3c4e218de
- .gnd-planning/milestones/code-refactoring/evidence/RF3/final-G2.json: f4aa3e510ed051b7be24d0aa08ff25fc9a053b56fb435ca1b559b42dc346297f
- .gnd-planning/milestones/code-refactoring/evidence/RF3/final-G2.txt: dce37e0740891db6e102382ee918eac04f1695864fd704de4acc89ee08d5979f
- .gnd-planning/milestones/code-refactoring/evidence/RF3/mutation-controls.json: e5e38ccef0d0cf4fc0eac219c2bf1d52ef798af913aafab7876d7f6fb9e3f41a
- .gnd-planning/milestones/code-refactoring/evidence/RF3/mutation-controls.txt: 4381655835b842c433da52a3668da3f8f9fa3d059ccfcb9668521ff5fedd213a
- .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py311.json: 0171fa835f631363d049a822a99f858e36c515c107ce20e571d79f30d4c95f2e
- .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py311.txt: b481153088e72d3a1814c039e52b7ddf50ccd417869ab480b519e362666fbd10
- .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py313.json: d4e1266f3e99978985548205fd8dd51af150516ffb06603081d48862480ada34
- .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py313.txt: 76166556abff2e870b5035abdc02b85930deda14eddfe45b34e80abe54622b86
- .gnd-planning/milestones/code-refactoring/evidence/RF3/review-authorization-status.json: 86b68ae4dd1262dfa7f5560e04360b03de5ff5faa48b6b333bb337532780ad4c
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G1.json: 1ed96c67868eb1228cca36f1c7ff54e4fda5d23a20e0ad8c59716f1c30887382
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G1.txt: ccf49f67870a012a16e92cd083907c262c51113d07d9bbb87fd276aafd725a85
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G3-G4.json: da422936b123a6b32806817b17761c44eaf264863ae9adb96fd3c3101f92ce5b
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G3-G4.txt: dc11a42021f3d840bfd6c695d27463aa206c6e055232f5701ae1b7ce3525886d
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G5.json: 41163f52c0711d4fac33c223806b6fcce5c84644465d5035520919ebd672ca75
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G5.txt: 510a88cc7de66d6427897c0c6bafe8da8d669af79cf888a6d6814d545f3b06a8
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-final-lint.json: b9b017fed9cc0e4fe592c2ec9e951418c34bc60a2e455f8348b2275868b57cc2
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-final-lint.txt: 9aa5143644f385318b578b1366c2fc23fae855dd092429b2d64434a3aeeffb3b
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches-repair.json: 911bed67722a045bea585c90aba2ff98c4ea1a982113704a9663ce89390fa280
- .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches-repair.txt: 29dd6b8067a83690f5fe3d3026ce5098e6d622a72684228eee0cc945d49dc05b
- .gnd-planning/milestones/code-refactoring/evidence/RF3-budget.json: 5b5b8c14a380073868298834e12bba08a12184d85e2e37c53b784d02d60ec57f
- .gnd-planning/milestones/code-refactoring/evidence/RF3-commit-compare.json: 17f44c8c1187f78dc0f153ea25012d9f8a2e420c92a47eb51f8fe7b14aae8881
- .gnd-planning/milestones/code-refactoring/evidence/RF3-document-moves.json: c1acf13ffd201aa3c62788d18de3248b78f466ccb6176a8fad861ab3e57b7dbd
- .gnd-planning/milestones/code-refactoring/evidence/RF3-frozen-controls.json: 9227fbea48c36b514e2dec78f95df1e991bc960c693500200f19eeb99a87ee12
- .gnd-planning/milestones/code-refactoring/evidence/RF3-manifest-adaptation.json: 8e45d5a4966a980eceaa15aa649823eb7c6054f0f6e809b8fb252621a3773616
- .gnd-planning/milestones/code-refactoring/evidence/RF3-moves.json: 94f26c06a88c38a04f53c3fcb157758384d32248d15bd570650e11a4b7d6fd72
- .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants/control.txt: 91f5045ca794a07a80b42f9680728501b041746b7f786d0d033bc555ea7447f8
- .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants/mutation-report.json: 6851bf26d0c12c5f2d3d9b033a78fc72d23bfca173932cc569c929b356f1292a
- .gnd-planning/milestones/code-refactoring/evidence/RF3-mutation-retargets.json: c2efd54e32d8d297319983664267dff932e52b7c4bd9415fdaafdf3e8f0642d7
- .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-base.json: 4d0742bfedbb440eb5223b39fbb0e67581263fdd2f67df6d961b8ae3c7b0bb7f
- .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-head.json: beeaa1d30d389064e13920825ed29fc82c52c4c8f723a8c6a4a92fffeca244d0
- .gnd-planning/milestones/code-refactoring/notes/phase-RF3-amendments.json: 215821c44962a89f3643c7c251362b2306c7ddb450f7a3a8e3198df0f3157310
- .gnd-planning/milestones/code-refactoring/notes/phase-RF3-approval.json: daf50bd78b9e1021dafa4149f4cf4785d30060854b5d9b37cb2651ff0223af63
- .gnd-planning/milestones/code-refactoring/notes/phase-RF3-spec.md: e337073ca5b36b15c8a6e5a51166b0cd81ee318ed918cc251c060acdb0df42f9


## Dated discharge annotation — 2026-10-05

The owner subsequently approved the Codex provider payload. The initial and one bounded repair review completed; reproduced R1/R2 findings and the captured-default bypass received test-only repairs and red/green evidence. Completion is recorded in ../008-phase-RF3.md. The pending statement above describes ac0475f’s historical state; it is not rewritten as prior completion.
