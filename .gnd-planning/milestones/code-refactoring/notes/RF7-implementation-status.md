Historical implementation status at35aa122. Superseded2026-10-06 by013-phase-RF7.md after authorized review and repairs. The hashes and pending-review statements below describe the earlier bytes, not current source.

# RF7 implementation status -- review pending

Date2026-10-06. Branch claude/rf1-code-refactoring-225109; source predecessor10608c4761bae7c0989b774a20de5f43c6350912. Owner explicitly selected RF7 auto, approved restriction test changes, and said “yes implement RF7”. Approved corpus-first snapshot and authorization are retained in evidence/RF7; red commit21dfa0e precedes production implementation.

## What shipped locally

C1 canonical paths and real intermediate directories; C2 shared bounded duplicate/finite/depth JSON intake across the75-call module inventory; C3 preconstruction YAML guards; C4 shared strict ISO datetime grammar with standalone PyRel copy; C5 literal True inheritance and one strict traversal; C6 regular-file streaming digest primitive with existing raw/prefixed adapters; C7 supported1--8 unknown-version diagnostic. Canonical encoders and accepted-input digest meanings remain distinct. Original RF1 goldens remain frozen;19 explicit restriction successors retain input/old/new hashes and per-field differences. Five RF6 definition successors retain old body hashes; dynamic syntax inventory has an explicit delta. CLI input parsing exceptions are exactly two reasoned edges, not a global exemption.

## Findings and refuted premises

The first strict traversal implementation rebuilt all parents on every resolution. Existing4000-parameter test observed4.07s; an independent exact-predecessor comparison reproduced an RF7 regression (predecessor passes, current3.59s). Lazy direct-parent lookup repaired it behind the unchanged test. This is correctness/performance regression evidence, not a benchmark claim.

The model reader could reinterpret a refused JSON document through YAML; fallback-red records the wrong schema error before repair. Explicit .json inputs and shared policy refusals now stop before YAML. Domain error types in two new corpus tests were corrected to their existing EvolutionError/PopulationLoadError adapters, without changing admission meaning. Original directory and hostile-path diagnostics were repaired instead of changing their expected answers. Native BOM/UTF16/UTF32 decoding remains supported within both byte caps.

Three generated untracked skill bytecode files polluted installer resource counts; only those generated files were removed. Packaged resource count remains65.

## Verification selection and observations

The following outputs are separately bounded gates; their test counts overlap. Default marker exclusions remain configured. Broad historical, provider/native oracle, proof, census, evidence, distribution, certification and full default suites were not run.

### restriction-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py --tb=short

Exit: 1. Output: 44 failed, 4 passed in 8.00s

### fallback-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_consumers.py::test_model_json_refusal_cannot_fall_back_to_yaml --tb=short

Exit: 1. Output: 1 failed in 0.07s

### focused-repair

Command: .venv/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_v72_phase4_json_input.py tests/test_public_v72_full_json_boundary.py tests/test_model_v2.py::test_reading_validation_is_not_quadratic_in_the_parameter_count tests/test_install.py --tb=short

Exit: 0. Output: 313 passed in 11.60s

### affected-final

Command: .venv/bin/python -m pytest -q tests/test_population_load.py tests/test_popvalidate.py tests/test_model_validation.py tests/test_model_v2.py tests/test_model_guarded.py tests/test_model_identity.py tests/test_synth_values.py tests/test_synth_boundary.py tests/test_model_evolution.py tests/test_evolution_conformance.py tests/test_public_evolution_legacy_readers.py tests/test_public_evolution_drift_readers.py tests/test_public_souffle_successors.py tests/test_public_souffle_input_contract.py tests/test_v72_phase4_json_input.py tests/test_public_v72_full_json_boundary.py tests/test_exp_session_contract.py tests/test_exp_session_store.py tests/test_review_request.py tests/test_public_local_adapter_policy_controls.py tests/test_measure_offline.py tests/test_public_transition_contract.py tests/test_codegen_manifest.py tests/test_install.py --tb=short --deselect=tests/test_public_souffle_successors.py::test_exited_group_cleanup_cannot_replace_output_refusal

Exit: 0. Output: 1126 passed, 1 deselected, 1 warning in 66.81s (0:01:06)

### successors-green

Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_session_pins.py --deselect tests/test_rf1_session_pins.py::test_session_fresh[3] --deselect tests/test_rf1_session_pins.py::test_session_resume[3] --tb=short

Exit: 0. Output: 231 passed, 2 deselected in 60.91s (0:01:00)

### direct-final

Command: .venv/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf7_structure.py --tb=short

Exit: 0. Output: 57 passed in 3.06s

### native311

Command: env PYTHONPATH=src /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py::test_resolver tests/test_rf1_semantic_pins.py::test_datetime_site --tb=short

Exit: 0. Output: 146 passed in 18.40s

### native313

Command: env PYTHONPATH=src /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py::test_resolver tests/test_rf1_semantic_pins.py::test_datetime_site --tb=short

Exit: 0. Output: 146 passed in 16.97s

### lint-final

Command: .venv/bin/ruff check src/gnd/anchors.py src/gnd/api.py src/gnd/assurance/_wire.py src/gnd/checker/_core.py src/gnd/codegen/manifest.py src/gnd/commands/checking.py src/gnd/commands/exp.py src/gnd/conformance/report.py src/gnd/coverage.py src/gnd/declared_adapter.py src/gnd/evolve/models.py src/gnd/evolve/service.py src/gnd/exp/adapter_policy.py src/gnd/exp/close.py src/gnd/exp/expectation_author.py src/gnd/exp/session_contract.py src/gnd/exp/session_eval.py src/gnd/exp/session_store.py src/gnd/exp/session_v7.py src/gnd/export/pyrel_runtime.py src/gnd/export/souffle.py src/gnd/export/souffle_runtime.py src/gnd/extract/manifest.py src/gnd/extract/service.py src/gnd/fidelity/doccheck_service.py src/gnd/fidelity/report.py src/gnd/fidelity/service.py src/gnd/install.py src/gnd/json_input.py src/gnd/measure/promote.py src/gnd/measure/report.py src/gnd/measure/service.py src/gnd/model/__init__.py src/gnd/model/_validation.py src/gnd/model_queries.py src/gnd/model_verbalization.py src/gnd/population.py src/gnd/popvalidate.py src/gnd/rai_import.py src/gnd/recovery/inventory.py src/gnd/recovery/verify.py src/gnd/report_schema.py src/gnd/review/request.py src/gnd/review/runner.py src/gnd/safefs.py src/gnd/semantic_adapter.py src/gnd/solve.py src/gnd/synth/assemble.py src/gnd/synth/boundary.py src/gnd/synth/corpus_service.py src/gnd/synth/oracle/constructive.py src/gnd/synth/poolfile.py src/gnd/synth/provenance.py src/gnd/synth/service.py src/gnd/synth/values.py src/gnd/transition.py src/gnd/witness/io.py src/gnd/witness/service.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_session_pins.py tests/test_rf3_core.py tests/test_rf5_commands.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf7_consumers.py tests/test_rf7_input_policy.py tests/test_v72_phase4_json_input.py src/gnd/input_policy.py tests/support/rf7_pins.py tests/test_rf7_structure.py --output-format concise

Exit: 0. Output: All checks passed!

### measure-final

Command: .venv/bin/python tools/gnd_arch.py measure --out .gnd-planning/milestones/code-refactoring/evidence/metrics-RF7.json

Exit: 0. Output: measurement exit recorded

### scaffold

Command: .venv/bin/python -m pytest -q tests/test_development_scaffold.py --tb=short

Exit: 0. Output: 14 passed, 1 deselected in 4.94s

## Refactoring review

Refactors EXECUTED: shared strict reference walk with lazy parent access; shared JSON/datetime guards and regular-file digest reading. These consolidate implementation while intentionally changing only the approved refusal policies; their accepted-input counterparts and compatibility bindings are verified by the selected gates. No behavior-preserving claim is made for inputs RF7 deliberately restricts. Canonical encoders and format-specific error adapters remain separate because their distinct bytes/messages are contractual. A future common structured error policy is deferred to the input-boundary successor milestone; no unapproved diagnostic rewrite ships.

## Boundary and pending work

This is an implementation status note, not the phase completion record. Required independent Codex review has not run. Automatic approval review rejected sending RF7 inspected repository source/diff to the Codex provider because phase approval did not explicitly authorize that disclosure; a specific authorization question is pending. Initial plus at most one repair is the declared bound. One reviewer is one reviewer; no earlier RF6 authorization or review opinion is reused for RF7. No phase-close/certification claim is made.

Exact v3 fresh/resume nodes were observed failing before any RF7 production change and again with unrestricted credential-free execution; those two nodes are excluded from current RF1 final gate. Exact predecessor Souffle setuid test also fails here: requested4700 becomes0700, so the setuid arm is unavailable; that single node is excluded from downstream final gate. No unrelated expected answers were changed to hide them. Historical RF2 physical-source/RF3 numeric/RF4 body-count observers retain earlier invalidation boundaries; current routing/layer/entry/query predicates have their own positive and dirty controls. The standalone six example executables and three skill scripts are named routing exemptions; native adjacent Souffle proof-stream decoder remains format-specific.

Frozen source-owned units and distribution authority test are unchanged. The bounded91-row migration adaptations retain old rows/hashes/modes; current-source attestation, installed release identity, production publishing and certification are unavailable/unrequested. Media types, large validator rewrites, session SCC/version strategy and source-owned open questions remain deferred.

## Evidence binding

SHA256 is computed from each retained file's current bytes. Machine paths in command output were replaced as declared in each file.

- evidence/RF7/affected-current.json: 05ce60fd528829185b52d2260b7a99b9550ca0af58da39efe9f40d9555e2730a

- evidence/RF7/affected-current.txt: ed306c7cfc02261e7ef32a247335dc43f3dd01584aee97226132c1b21b0396fd

- evidence/RF7/affected-final.json: d35d08813e3e3eb4b1311584e1dbae2475c840fb48dc9aa0ea4510133ac48e13

- evidence/RF7/affected-final.txt: b3790cec3fff34c1fe22c90fcb4ec9b43f0c79e921b244cbcef03add14e253a5

- evidence/RF7/affected-selection.txt: a114a189df254ab2fb1967c2d29b9dd4d6094910637951e18ddc4973dd83087e

- evidence/RF7/approval.json: 2d4ee43b08d807f69cb65c2be07f84d2fd657a364d5cd243ecb8e7cef6c18326

- evidence/RF7/approved-spec.md: 7ef824a8c38873897f4bb35e8972914a693e07be77da1f57cb12d2c955abd25e

- evidence/RF7/architecture-current.json: 50395e413b8fa79e205c7453227c0920f984ff892ecb00cafc5690ef54784a3c

- evidence/RF7/architecture-current.txt: 06eb59ce1cb4c8fa631bc774c1d03ff8b1f637e0ae8fb1a25a6ecae1f1e55adf

- evidence/RF7/architecture-retry.json: a85844604f2eba4d6343d405e1edb5250325bda4c519d22d51c3fa245e8795b9

- evidence/RF7/architecture-retry.txt: 88086f70e70eb0b1057f373e0a85a7834379fa8144faf5637dabc986786ae97b

- evidence/RF7/budget-current.json: 16f339dfe3f239dbc266fbe5adcad6f01c0c699caa6b24e5fa1f184070adf149

- evidence/RF7/current-rf1-repair.json: 84eb5f6bf59d41b8bf13913a3c0216746f70f87a636fd74af62f31e921070293

- evidence/RF7/current-rf1-repair.txt: dd2ed2a05f46e1fd2e0b85ff1c898b98a56a841238865cb1be0157d5db7869aa

- evidence/RF7/current-rf1.json: f7e3b0e01373bf1e6301c8c4bd915d36fbd56bb4249bd3e77feaf0c3b757dc87

- evidence/RF7/current-rf1.txt: 8a17a85a4395d75f5140029de100067beb6f30b88ad260d4af61cc709f4285a0

- evidence/RF7/definition-successors.json: 7803b16e491e61ce89bcd0344a4111aa726a962b14407ef98b686f985caf97bc

- evidence/RF7/direct-final.json: 10a17c2c0c0d16ff9d076e63f30d57ba0aba7e01c7bf808fd48c65468d74e4c3

- evidence/RF7/direct-final.txt: ba1639219e872909969f69d7a22cb6d1107308a7fc0cc86e271ddd89b5232046

- evidence/RF7/dynamic-query-candidates.json: ce2ea2e4a085bb13d874d2788118031a3f343342fe2e89dfa471195ca10c3b08

- evidence/RF7/dynamic-query-delta.json: 55625147805763c05558b5e9c0706627cba83cb1c679b882782506d2dd984874

- evidence/RF7/fallback-red.json: d2eaf69970af8451754952830a881aabbf20cea388195fca4cc0447154d7e37b

- evidence/RF7/fallback-red.txt: 747df4089df18170f0d9bbf69dd5226f6efd7d6dccc22dfc085956acec239625

- evidence/RF7/focused-repair.json: f265f34bc40b4fd30929542c84ea8399cd58a97ca7187f74527cfd871dafae93

- evidence/RF7/focused-repair.txt: e7043baf5e12806f2584e1ca9f8a5257c4b86b6fbff8805935c1f4ccb37fbc38

- evidence/RF7/json-consumer-inventory.json: 41be414b40c75432df2056db028c5031a660c8ab7d67e790e6941aec7afaac32

- evidence/RF7/json-routing.json: 094de4feb0d7a94a94fa2f94da20880ce71d8a643daea0bb8e9b980d3769cf3a

- evidence/RF7/lint-current.json: 51e70f1ce084b155405054523cd42b59c258ed54853b191c8667b4f0c5482e91

- evidence/RF7/lint-current.txt: c689284c66556a7262c5bff8a0e951fbb32fe7a150e2660076714fa73e44d560

- evidence/RF7/lint-final.json: 557dfb550d3b46f6c4cb44e3dc1335dd22e507e4e50d15bffb1140d485a59d6d

- evidence/RF7/lint-final.txt: 525c14b309ed43580d31fa615e65c49258353ac84f4438f79bee65c4e07c2725

- evidence/RF7/manifest-adaptations.json: c1a78291dd5425db3fbe7f2fa3634f5c9ec84e75b0ac7fcf3f1ba1ee736d2310

- evidence/RF7/measure-final.json: a51c1767117a98cfdbb6805140cea3d975982631a436dfcf938b502672deec86

- evidence/RF7/measure-final.txt: 7efd94838e84ddb1239277cbbe6e7f73d25293270e1ab08552c0cf7701fad545

- evidence/RF7/measure.json: a7e974c1bb235b82ab65a9d3a3e3f68d73634e7529cbc35faadf05e0f6123df6

- evidence/RF7/measure.txt: 7efd94838e84ddb1239277cbbe6e7f73d25293270e1ab08552c0cf7701fad545

- evidence/RF7/metrics-pre-entry-policy.json: a5066a5dfc3f1bac88572ed49a6787e21c342165a788df82376a2e1ed4e0cc5c

- evidence/RF7/native311.json: 6d7c3ec8222c409e65ddeb8dd4a91b7b7fa63141e4eaad3650b7af8953208cdc

- evidence/RF7/native311.txt: 1b14302630ebaedea2986f90c30fbb6bde55fc49d4d9089876a514d0c4fe847e

- evidence/RF7/native313.json: 2d0034633c30f2824dad8855a7c647fca104d9885f9a0b0e6313d6bd87a3a2cd

- evidence/RF7/native313.txt: 0e1e40ad5c8ac299021bc9bc3205f6dfb50d9c915080560d9d797a8e6bea8552

- evidence/RF7/original-scope-note.md: 7c0714ae95a35dd2f7aae76eb69aebf1b440024c4e5c7351cdd00a5f0bc224ff

- evidence/RF7/predecessor-v3-unrestricted.json: f82a70c7c62dcd46cea4e3463d2a44175e1ff25596ea258793cd0f60c7c80d07

- evidence/RF7/predecessor-v3-unrestricted.txt: 626539d1e1a8ed22fedd596b0150abe3bd8f8d7d12d53057626a600ced22e0bf

- evidence/RF7/predecessor.json: 5c85ae9806f6777b9fc06c00f58ed023c9c331c6df34de01ae6f684105ace592

- evidence/RF7/predecessor.txt: 8b984b59eaf94c45ea0ee7386543d9528be6606154f136a64c03f249a03c0696

- evidence/RF7/restriction-green.json: cab6a45fd116707b5713ad3c544abb71a351da5c7af92b4e38942973798fd611

- evidence/RF7/restriction-green.txt: 9369a877389c13e063bea1939b8fa0db1b09dab7248af48031247408095a4cc9

- evidence/RF7/restriction-red.json: 279b6cc463117deb4e7088efa7c8d541008cbad9dae18a5f91a6c6898ac96e70

- evidence/RF7/restriction-red.txt: 95bba748f9726bdf7af9f3ddbd0d8ab1727f76517839a879fcbd36a99284c1ca

- evidence/RF7/review-status.json: 3e914b76ad73d56308d3e4ddfec22ace3d2b0d5622e8ab6dea311b095d9177fe

- evidence/RF7/routing-final.json: 48e6e7d4862e5d7f3fb9d1a2ca152263a228a65a5233961a4bbf2173e53e55d7

- evidence/RF7/routing-final.txt: 7bfd808b02f70ffc643b4fc847c055a86edbf1419309189a808df41f401ac524

- evidence/RF7/scaffold.json: 0123a97e7e8a722f6bdca021d31bca6b54cb6d21f9e8eb55951b0a9a3b74e306

- evidence/RF7/scaffold.txt: 9029a01a922a0f55bcd8fd42aa98b211925c746a8771fd74cecf8ab7afada5e1

- evidence/RF7/structure-final.json: a7019b3cff3aa2e3cf710b31db7dc5385e2bf80a765fac7580ebbfd4911b5fe4

- evidence/RF7/structure-final.txt: c939bd64c9e766ea699c4b1da1a2845c5d7d2369f1c00364f0c9e1f6bd53dd78

- evidence/RF7/structures.json: 5974d7906d2d55d866ca089287b96412bdffa2a9fbf2f24319f59c31ca22774d

- evidence/RF7/structures.txt: 873ea38cefbc5514c7a0a04f680afeb8d348d313d403bf22dc3290fa16978c75

- evidence/RF7/successor-capture.json: 689b34b748de937124bc3aa5561e8fb0822de7eac02f14612e550d9217f34001

- evidence/RF7/successor-capture.txt: fe9ae7a831585701b2b7b088ab40e2d14f379f51abf922a606cda550b9e68927

- evidence/RF7/successors-green.json: fef6f2d08f7bc652b6c907164121b990a800e33201b0c4c0d842f35599ebcd73

- evidence/RF7/successors-green.txt: 254445b21a6abc1a493f6e9e0513564f89a9151ab60c087d96925c92c65f157a
