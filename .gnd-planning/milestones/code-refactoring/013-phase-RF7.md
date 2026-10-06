---
milestone: code-refactoring
station: phase-RF7
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF7
date: 2026-10-06
source_base: 10608c4761bae7c0989b774a20de5f43c6350912
verified_source_commit: d8e5487c9ea17bb1198765b0536281a15b637859
implementation_commit: 35aa1221ef4c725a8ffe857215dffbcc7cf387f4
corpus_first_commit: 21dfa0e
gate:
  command: ".venv/bin/python -m pytest -q tests/test_rf7_review_regressions.py tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf7_structure.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_rf5_commands.py tests/test_model_v2.py::test_reading_validation_is_not_quadratic_in_the_parameter_count --deselect=tests/test_rf3_core.py::test_full_current_and_original_core --tb=short"
  exit: 0
  output: "633 passed, 1 deselected in 16.67s"
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Full default, exhaustive historical, provider/native oracle, proof, census, evidence, distribution and certification suites are outside RF7 focused impact closure."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-current.json, sha256: 05ce60fd528829185b52d2260b7a99b9550ca0af58da39efe9f40d9555e2730a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-current.txt, sha256: ed306c7cfc02261e7ef32a247335dc43f3dd01584aee97226132c1b21b0396fd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-final.json, sha256: d35d08813e3e3eb4b1311584e1dbae2475c840fb48dc9aa0ea4510133ac48e13}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-final.txt, sha256: b3790cec3fff34c1fe22c90fcb4ec9b43f0c79e921b244cbcef03add14e253a5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-repair-focused.json, sha256: 17bb160a17651f7b69efed5edcd4ee9bcde965bf604fe290870c5d0a3e3b8106}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-repair-focused.txt, sha256: 554f3851b9edd5bbe20e1cb0a086d136fa10e3bb139d97cceaeae28b6915f90e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-repair.json, sha256: 00170350e81c32cb95244c11ad055923f0c26be9920de6c3e8dc22c6cbaad3ad}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-repair.txt, sha256: 12cc5899c23416e175b4d7a3fa40b3e2d46dcf0c524dea2d709725c450dc47c0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/affected-selection.txt, sha256: a114a189df254ab2fb1967c2d29b9dd4d6094910637951e18ddc4973dd83087e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/approval.json, sha256: 2d4ee43b08d807f69cb65c2be07f84d2fd657a364d5cd243ecb8e7cef6c18326}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/approved-spec.md, sha256: 7ef824a8c38873897f4bb35e8972914a693e07be77da1f57cb12d2c955abd25e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/architecture-current.json, sha256: 50395e413b8fa79e205c7453227c0920f984ff892ecb00cafc5690ef54784a3c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/architecture-current.txt, sha256: 06eb59ce1cb4c8fa631bc774c1d03ff8b1f637e0ae8fb1a25a6ecae1f1e55adf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/architecture-retry.json, sha256: a85844604f2eba4d6343d405e1edb5250325bda4c519d22d51c3fa245e8795b9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/architecture-retry.txt, sha256: 88086f70e70eb0b1057f373e0a85a7834379fa8144faf5637dabc986786ae97b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/budget-amendment.json, sha256: 5aab73c5bbebe886bd5165d2f28f60d89831341b8e9c2fe7dbd413fbc69cc88d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/budget-current.json, sha256: 16f339dfe3f239dbc266fbe5adcad6f01c0c699caa6b24e5fa1f184070adf149}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/completeness-current.json, sha256: f36728129d3884c24a9571c478e72b9bf2397294b32400b15e49441f4c4648de}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/completeness-current.txt, sha256: 2445f5400988dd7637e496975f98f3f50f337e22fb1a2c4f61c05b574e02789f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/completeness-predecessor.json, sha256: 258bd32f8dcc652320fbe14240474469f0e02adc6a19cec69a3017eb90e6738c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/completeness-predecessor.txt, sha256: 2055e4909224628d55eeee179c1fa6033c8dec84ddc3aa220e82268d88fd4b10}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/current-rf1-repair.json, sha256: 84eb5f6bf59d41b8bf13913a3c0216746f70f87a636fd74af62f31e921070293}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/current-rf1-repair.txt, sha256: dd2ed2a05f46e1fd2e0b85ff1c898b98a56a841238865cb1be0157d5db7869aa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/current-rf1.json, sha256: f7e3b0e01373bf1e6301c8c4bd915d36fbd56bb4249bd3e77feaf0c3b757dc87}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/current-rf1.txt, sha256: 8a17a85a4395d75f5140029de100067beb6f30b88ad260d4af61cc709f4285a0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/definition-successors-before-review.json, sha256: 7803b16e491e61ce89bcd0344a4111aa726a962b14407ef98b686f985caf97bc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/definition-successors.json, sha256: 73d3b3bcc4e7efe5d20c43226ae8baadd695d11b119894f42a4e5f35432914cc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/direct-final.json, sha256: 10a17c2c0c0d16ff9d076e63f30d57ba0aba7e01c7bf808fd48c65468d74e4c3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/direct-final.txt, sha256: ba1639219e872909969f69d7a22cb6d1107308a7fc0cc86e271ddd89b5232046}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/dynamic-query-candidates.json, sha256: 48c8d40cb2ef76c7fe4358bea97de8a4523454db1b8501d801fcc813031b4def}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/dynamic-query-delta.json, sha256: 55625147805763c05558b5e9c0706627cba83cb1c679b882782506d2dd984874}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/dynamic-query-review-delta.json, sha256: 09e48798a0032d82a30e66add9544c5375ca815afdd48e84f4a1766c94af62ac}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/fallback-red.json, sha256: d2eaf69970af8451754952830a881aabbf20cea388195fca4cc0447154d7e37b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/fallback-red.txt, sha256: 747df4089df18170f0d9bbf69dd5226f6efd7d6dccc22dfc085956acec239625}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/focused-repair.json, sha256: f265f34bc40b4fd30929542c84ea8399cd58a97ca7187f74527cfd871dafae93}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/focused-repair.txt, sha256: e7043baf5e12806f2584e1ca9f8a5257c4b86b6fbff8805935c1f4ccb37fbc38}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/json-consumer-inventory.json, sha256: 41be414b40c75432df2056db028c5031a660c8ab7d67e790e6941aec7afaac32}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/json-routing.json, sha256: 094de4feb0d7a94a94fa2f94da20880ce71d8a643daea0bb8e9b980d3769cf3a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-current.json, sha256: 51e70f1ce084b155405054523cd42b59c258ed54853b191c8667b4f0c5482e91}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-current.txt, sha256: c689284c66556a7262c5bff8a0e951fbb32fe7a150e2660076714fa73e44d560}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-final.json, sha256: 557dfb550d3b46f6c4cb44e3dc1335dd22e507e4e50d15bffb1140d485a59d6d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-final.txt, sha256: 525c14b309ed43580d31fa615e65c49258353ac84f4438f79bee65c4e07c2725}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-repair-first.json, sha256: 1a099369ce37a0b35f949c928f526a2b2189d4f3414a36767e7cf4bc63584930}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-repair-first.txt, sha256: b97ec770543fd45732f4e62caf28761b7252a6a2e43a339dd2b344367fba41ac}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-repair.json, sha256: 62aa7c72dd88000c705e19a4253be339cd37677647259b6478ebfd3941eba950}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/lint-repair.txt, sha256: 16096c1e8b7f69027fc5bfb80fabb8925a9d4ef3d444b9c15001a765d3eb2d07}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/manifest-adaptations.json, sha256: 02b9dc7aae6046bb5a1e90d2496b45b7f1d2f16c4cd143f2b8df4889683c654b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/measure-final.json, sha256: a51c1767117a98cfdbb6805140cea3d975982631a436dfcf938b502672deec86}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/measure-final.txt, sha256: 7efd94838e84ddb1239277cbbe6e7f73d25293270e1ab08552c0cf7701fad545}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/measure.json, sha256: a7e974c1bb235b82ab65a9d3a3e3f68d73634e7529cbc35faadf05e0f6123df6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/measure.txt, sha256: 7efd94838e84ddb1239277cbbe6e7f73d25293270e1ab08552c0cf7701fad545}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/metrics-pre-entry-policy.json, sha256: a5066a5dfc3f1bac88572ed49a6787e21c342165a788df82376a2e1ed4e0cc5c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/metrics-repaired.json, sha256: dec6edff3715d8a7c08667f9f014bcac1d1bf80f2b8f782c3a264c6beec485f4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native311-repair.json, sha256: d01a88073545b7be71a52a285385dea3457237bda934748adaaf226be6e1ad84}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native311-repair.txt, sha256: f18215e4377f3827843e59e0d7f049f3022830a2a3159e381108c6830d28634e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native311.json, sha256: 6d7c3ec8222c409e65ddeb8dd4a91b7b7fa63141e4eaad3650b7af8953208cdc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native311.txt, sha256: 1b14302630ebaedea2986f90c30fbb6bde55fc49d4d9089876a514d0c4fe847e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native313-repair.json, sha256: facbf540339d4a27ba39aaa872d2fafa100866ecc0fd270b9b492717aa49372f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native313-repair.txt, sha256: ec9484a778111729ea5fa70a1aafb95690f4a7dc09deb33500a788662e7f8b68}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native313.json, sha256: 2d0034633c30f2824dad8855a7c647fca104d9885f9a0b0e6313d6bd87a3a2cd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/native313.txt, sha256: 0e1e40ad5c8ac299021bc9bc3205f6dfb50d9c915080560d9d797a8e6bea8552}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/original-scope-note.md, sha256: 7c0714ae95a35dd2f7aae76eb69aebf1b440024c4e5c7351cdd00a5f0bc224ff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor-archive-confirmed.json, sha256: 4690f1eac4ab87a143370bde5c96007fd1b258d3db6f2decffa986d66379f82b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor-archive-confirmed.txt, sha256: 095c2ec45f62feb024e14b806f7c4cd14b18b4fc5f99a48749ce7aaa7c7554fc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor-v3-unrestricted.json, sha256: f82a70c7c62dcd46cea4e3463d2a44175e1ff25596ea258793cd0f60c7c80d07}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor-v3-unrestricted.txt, sha256: 626539d1e1a8ed22fedd596b0150abe3bd8f8d7d12d53057626a600ced22e0bf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor.json, sha256: 5c85ae9806f6777b9fc06c00f58ed023c9c331c6df34de01ae6f684105ace592}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/predecessor.txt, sha256: 8b984b59eaf94c45ea0ee7386543d9528be6606154f136a64c03f249a03c0696}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/provider-authorization.json, sha256: 4a3a42549dd5fa95dba1deb07740a65db886e5ae80bc99794861dc0b15f8e06b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/query-repair.json, sha256: acea342a10e37c8f9f468013014f336dffeaea45e73544ed9e3f757de5f5bb19}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/query-repair.txt, sha256: 1d605eae906891b3f525cf903f49f4ccbd20d47a47e6eb5fa6ade2366fc641c8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/restriction-green.json, sha256: cab6a45fd116707b5713ad3c544abb71a351da5c7af92b4e38942973798fd611}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/restriction-green.txt, sha256: 9369a877389c13e063bea1939b8fa0db1b09dab7248af48031247408095a4cc9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/restriction-red.json, sha256: 279b6cc463117deb4e7088efa7c8d541008cbad9dae18a5f91a6c6898ac96e70}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/restriction-red.txt, sha256: 95bba748f9726bdf7af9f3ddbd0d8ab1727f76517839a879fcbd36a99284c1ca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-all-red.json, sha256: d1b4a9d56eca06b263a938c5f47bc539745dd16dcecccf0d4bd7c36ec5f93994}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-all-red.txt, sha256: 9c3aafbee43399e8806d5fef08c4f36c8219750160d654a39514eee556d6ac6b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-green.json, sha256: 12df134faea9ab20e6f7f744c4103cdb67f2cbbe469942b37cd9febfa692a0cd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-green.txt, sha256: bba2443a49f828b65f7a1306fffcb2b05ceb255f3b5171168e647b1f3adb3cc2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-red.json, sha256: 4a7dc6db2ae75480263873b46fffad47b93875a1fb821c3c68959c71ef71d57a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-red.txt, sha256: 99d8c3d7375c883acb17df94b565df0c6d865f128884a58a04211c38e1166005}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/review-status.json, sha256: db6ec96a255e3a81433123863f6826d2c117212366c48f16685a916f686b09f9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/routing-final.json, sha256: 48e6e7d4862e5d7f3fb9d1a2ca152263a228a65a5233961a4bbf2173e53e55d7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/routing-final.txt, sha256: 7bfd808b02f70ffc643b4fc847c055a86edbf1419309189a808df41f401ac524}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/scaffold.json, sha256: 0123a97e7e8a722f6bdca021d31bca6b54cb6d21f9e8eb55951b0a9a3b74e306}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/scaffold.txt, sha256: 9029a01a922a0f55bcd8fd42aa98b211925c746a8771fd74cecf8ab7afada5e1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/standalone-review-red.json, sha256: 09b72ae7a2cd3daea5210358246615e7ec913aff449e5f75e5a0e60def0aa7c9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/standalone-review-red.txt, sha256: 18edea10831e8d183ea70bc8713769c2d7e19c2eca13bf468466c7f4715631a2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-confirmed.json, sha256: a3dcb5b45a9da3e6fc8e37674edb59c7374da2b9c6944b5eb198a072dc39185f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-confirmed.txt, sha256: bb603c1641f82db6bf2a0f23f0dd9486c2f0650edd720fa22a091f951fb56e85}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-final-repaired.json, sha256: a4d1e64e80f9bd7dcad0fb82beaf5368f3d833180e8ea094a749f97cc427e930}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-final-repaired.txt, sha256: 8b1000444b20f1bb0da277e78d1c8b4077b7aeb50470344fac9d12b59fb96fc7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-final.json, sha256: a7019b3cff3aa2e3cf710b31db7dc5385e2bf80a765fac7580ebbfd4911b5fe4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-final.txt, sha256: c939bd64c9e766ea699c4b1da1a2845c5d7d2369f1c00364f0c9e1f6bd53dd78}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-repair.json, sha256: a68e4ebc75de30b62091294ba009763cd6a04b91bcf6a5f68ef46110a8011aca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structure-repair.txt, sha256: c9b5335358c58671472714988f8830109dc9c3282104f25e1d3126ce7373982b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structures.json, sha256: 5974d7906d2d55d866ca089287b96412bdffa2a9fbf2f24319f59c31ca22774d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/structures.txt, sha256: 873ea38cefbc5514c7a0a04f680afeb8d348d313d403bf22dc3290fa16978c75}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successor-capture.json, sha256: 689b34b748de937124bc3aa5561e8fb0822de7eac02f14612e550d9217f34001}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successor-capture.txt, sha256: fe9ae7a831585701b2b7b088ab40e2d14f379f51abf922a606cda550b9e68927}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successors-green.json, sha256: fef6f2d08f7bc652b6c907164121b990a800e33201b0c4c0d842f35599ebcd73}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successors-green.txt, sha256: 254445b21a6abc1a493f6e9e0513564f89a9151ab60c087d96925c92c65f157a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successors-repair.json, sha256: 38ec63fbb026b97030c65f83457460fc984f4fc3faad20a8ba6b025b0b24c41d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/successors-repair.txt, sha256: e5214e4cbe95df3c256cc29a0f6546ddcd378e369b190aae92188be67ab0c25c}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF7-spec.md, sha256: 487ebcc066eb6d5080b3e84596b586f248ef50e12a44bf41423ad65d3566bc7e}
  - {path: .gnd-planning/milestones/code-refactoring/notes/RF7-plan-amendment.md, sha256: 93a2575df51e4b28df9d9e58b43acc186446ed20e8086ed6d5135dd4ebb83bab}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF7-codex-review.md, sha256: a80a488ba1e56e391bbbb951ddc3ebbf4010fb3135d500e3b4f83887a1ebfc4d}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF7-codex-repair-review.md, sha256: 689b069239d7ac37ae99059d649a8642d205ffb62ac249ebd4fb91bae94d9140}
  - {path: tests/fixtures/rf7-restrictions/successors.json, sha256: 24625cee112a9066153232a8cdf0d26640c79cde94357fe45cbd0b6ac7774fb0}
  - {path: tests/support/rf7_pins.py, sha256: d98d2916507c470d1d0b4b2c85bf3e56e8b027a4741acefa5de5fa6454c6ce3d}
  - {path: tests/test_rf7_review_regressions.py, sha256: 6b0ed4361badf564988be72d1107ea0e0323d16725ee862a29b8ff1f5cc0f3ce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/budget-final.json, sha256: 3c5b234278523b0b0f18b0b7f48efdd3a9d93ecf7bd67cdcfdfd7a6bcbdbffd9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/scaffold-final.json, sha256: 0c08e5b317d5e5c4408f772c38c97366ab234ba040bf7e9139ac7de6810dab69}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF7/scaffold-final.txt, sha256: 5d983d5c4933367580b1acfb09ca08235afa1a7f0ab7c604cc2c97abfe8132b3}
---

# RF7 -- strict input policy and validator consolidation

The current focused gate exited0 with633passed; the affected repair closure exited0 with708passed, and current RF1 successors exited0 with231passed and2exact predecessor exclusions. These selected gates overlap; no aggregate repository acceptance is claimed.

## Provenance and owner decisions

The whole r2+e1 plan,004--012 carryovers and original RF7 deferral were harvested before corpus-first commit21dfa0e. Owner explicitly selected RF7 auto, approved affected test changes and said “yes implement RF7”. Separate owner-directed RF7-plan-amendment.md supersedes RF-D7 deferral and RF-R1 preservation only for C1--C7/FIFO. Original plan/gates remain unchanged, and no old plan panel opinion covers this amendment. Optional spec panel omitted; independent phase review required. Detailed approval is delegated auto, not a human reading of the new spec.

Owner separately approved the exact RF7 Codex provider disclosure after automatic approval review rejected the initial attempt. Native authentication, stdin prompt, read-only sandbox, initial plus at most one repair review. No project environment or credentials were executed, sourced or printed. Provider authorization and reviewed repair source hashes are retained.

## What shipped

- C1: safefs canonical POSIX relative spelling and real intermediate-directory checks; existing leaf symlink policy retained. Previously refused unsafe paths preserve diagnostic order.
- C2: input_policy loads/load/JSONDecoder applies default10MiB cap, duplicate/nonfinite/floating-overflow refusal and depth64 before decode. Native ordinary numeric types, explicit Decimal/callback hooks and BOM/UTF16/UTF32 interpretation remain supported within both original/decoded byte caps.75-call module inventory routed, with one native proof-stream decoder exemption. Standalone six example and three skill executables are exact named scope exclusions. Encoders remain format-specific.
- C3: evolve model-text and Souffle readers guard YAML byte/event/depth/aliases before node construction; duplicate refusal remains the safe loader's policy. Original other YAML loaders stay unchanged.
- C4: one strict ASCII ISO datetime parser across named GND sites, copied grammar in standalone PyRel runtime. Actual dates/time/offsets enforced; naive values retained.
- C5: literal True reference inheritance, both legacy variant names retained under one strict reference walk. Branch-local visited sets preserve sibling ambiguity and caller-visible visited union; standalone primitive copy follows the same branch policy. Lazy parent lookup avoids whole-map rebuilding on every resolution.
- C6/RF1-OQ5: regular-file nonblocking digest reader refuses FIFO/special files before reading; preserves regular leaf symlink following, raw/prefixed digest adapters and accepted-file bytes. Size/identity checks and descriptor close are exercised. Sidecar reads are bounded with original UTF8 interpretation and SidecarError mapping.
- C7: unknown-version diagnostic lists1--8; version dispatch and live v2 assignment unchanged.

Original RF1 fixtures remain frozen. Nineteen approved restriction successors bind original/new hashes and field differences to the original input digest; all unlisted keys use original expectations. Five RF6 changed definitions have explicit body successors; historical import/metadata/pickle/actual-patch controls still run. Dynamic query inventory has named syntax deltas, including the standalone set[str] annotation. Literal query exceptions/ceilings remain unchanged. Exactly two CLI input parsing infrastructure edges are reasoned exceptions. Source-owned units and distribution authority test remain frozen;92 bounded migration adaptations retain original rows/hashes/modes, without current release identity authority.

## Review, reproductions and refuted premises

Initial single reviewer found R1--R3 blocking, R4 hardening, R5 completeness. All five were reproduced before disposition; review-all-red observed7failed6passed on35aa122, and standalone-review-red observed1failed. Four accepted fixes landed with passing/refusing siblings:

| Finding | Red observation | Repair / disposition |
|---|---|---|
| R1 JSON policy callback error falls through YAML | NaN/Infinity/-Infinity accepted as YAML strings for JSON-shaped .yaml model | Fallback only on actual native JSON syntax error, not policy/domain refusal; genuine unquoted YAML flow mapping accepted |
| R2 shared seen hides parent ambiguity | Both ambiguous parents None, common child String; both variants and standalone primitive red | Independent sibling snapshots plus visited union; cycle/initial-seen conventions retained |
| R3 sidecar reads beyond cap and leaks ValueError | Unbounded read followed by raw cap error | Read MAX_BYTES+1 binary bytes, reject before UTF8 decode, map to SidecarError |
| R4 mutating callback erases duplicates | Clearing pairs callback returned{} | Capture duplicate evidence before invoking callback; retain original hook refusal precedence |
| R5 private evolve YAML ParserError | ParserError on current and exact predecessor | Completeness deferred to input-boundary hardening successor; no exposed service route established |

The declared single repair review found no remaining concrete blocker/hardening issue within its five-module scope. It checked model/YAML siblings, shared/standalone traversal ambiguity/cycles/visited state, sidecar caps/UTF8/error adapters/valid boundary case, and callback refusal/finite-number siblings. One reviewer is one reviewer; two passes are not a panel. Reviewer performed small read-only probes, not suites, and did not independently establish our gate counts or broad byte equivalence.

Earlier implementation findings remain in the spec: eager parent-map rebuilding regressed the existing4000-parameter control (4.07s, isolated3.59s, exact predecessor passes); lazy lookup repaired it behind that unchanged test. JSON overflow could fall through into schema validation; fallback-red was observed before the first repair. No benchmark/general performance claim follows. Old directory/hostile-path diagnostics were repaired instead of recaptured, and three generated untracked skill bytecode files were removed to restore the original65-resource count.

A mistaken whole synthesis-module repair selection reached a historical30-seed replay. It was explicitly stopped at exit2 after686passed; this is NOT a passing gate or authorized broad acceptance result. The focused replacement selects named sidecar/model-reader controls and exits0 with708passed. No further broad replay ran.

## Gate output (verbatim)

Commands, selected output summaries and actual exits below; full retained streams are SHA-bound in the frontmatter. Machine paths were substituted as declared in each stream. Counts overlap.

### restriction-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py --tb=short

```text
44 failed, 4 passed in 8.00s
Exit: 1
```

### fallback-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_consumers.py::test_model_json_refusal_cannot_fall_back_to_yaml --tb=short

```text
E   gnd.model.ModelValidationError: model validation failed: $: 'version' is a required property; $: 'object_types' is a required property; $: 'fact_types' is a required property; $: Additional properties are not allowed ('x' was unexpected)
1 failed in 0.07s
Exit: 1
```

### review-all-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_review_regressions.py --tb=short

```text
7 failed, 6 passed in 0.10s
Exit: 1
```

### standalone-review-red

Command: .venv/bin/python -m pytest -q tests/test_rf7_review_regressions.py::test_standalone_primitive_shared_ancestor_ambiguity --tb=short

```text
1 failed in 0.06s
Exit: 1
```

### review-green

Command: .venv/bin/python -m pytest -q tests/test_rf7_review_regressions.py tests/test_rf7_input_policy.py tests/test_rf7_consumers.py --tb=short

```text
69 passed in 0.58s
Exit: 0
```

### structure-final-repaired

Command: .venv/bin/python -m pytest -q tests/test_rf7_review_regressions.py tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf7_structure.py tests/test_rf6_query_policy.py tests/test_rf6_packages.py tests/test_rf3_core.py tests/test_rf5_commands.py tests/test_model_v2.py::test_reading_validation_is_not_quadratic_in_the_parameter_count --deselect=tests/test_rf3_core.py::test_full_current_and_original_core --tb=short

```text
633 passed, 1 deselected in 16.67s
Exit: 0
```

### affected-repair-focused

Command: .venv/bin/python -m pytest -q tests/test_population_load.py tests/test_model_validation.py tests/test_model_v2.py tests/test_model_guarded.py tests/test_popvalidate.py tests/test_v72_phase4_json_input.py tests/test_public_v72_full_json_boundary.py tests/test_measure_offline.py tests/test_synth_values.py tests/test_synth_boundary.py tests/test_digest_helpers.py tests/test_synth_conforming.py::test_sidecar_round_trips_and_covers_every_constraint tests/test_synth_conforming.py::test_sidecar_rejects_a_stale_population_hash tests/test_synth_conforming.py::test_sidecar_swapped_next_to_a_different_population_is_rejected tests/test_synth_conforming.py::test_sidecar_rejects_an_unknown_field tests/test_synth_conforming.py::test_sidecar_accepts_supported_legacy_schema_versions tests/test_synth_conforming.py::test_sidecar_rejects_an_unsupported_future_schema_version tests/test_synth_conforming.py::test_sidecar_paths_are_relative_not_absolute tests/test_synth_conforming.py::test_sidecar_rejects_an_absolute_or_escaping_pool_path --tb=short

```text
708 passed in 52.73s
Exit: 0
```

### successors-repair

Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_session_pins.py --deselect tests/test_rf1_session_pins.py::test_session_fresh[3] --deselect tests/test_rf1_session_pins.py::test_session_resume[3] --tb=short

```text
231 passed, 2 deselected in 63.14s (0:01:03)
Exit: 0
```

### native311-repair

Command: env PYTHONPATH=src /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf7_review_regressions.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py::test_resolver tests/test_rf1_semantic_pins.py::test_datetime_site --tb=short

```text
166 passed in 19.20s
Exit: 0
```

### native313-repair

Command: env PYTHONPATH=src /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf7_input_policy.py tests/test_rf7_consumers.py tests/test_rf7_review_regressions.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py::test_resolver tests/test_rf1_semantic_pins.py::test_datetime_site --tb=short

```text
166 passed in 17.69s
Exit: 0
```

### query-repair

Command: .venv/bin/python -m pytest -q tests/test_rf6_query_policy.py --tb=short

```text
10 passed in 6.80s
Exit: 0
```

### lint-repair

Command: .venv/bin/ruff check src/gnd/anchors.py src/gnd/api.py src/gnd/assurance/_wire.py src/gnd/checker/_core.py src/gnd/codegen/manifest.py src/gnd/commands/checking.py src/gnd/commands/exp.py src/gnd/conformance/report.py src/gnd/coverage.py src/gnd/declared_adapter.py src/gnd/evolve/models.py src/gnd/evolve/service.py src/gnd/exp/adapter_policy.py src/gnd/exp/close.py src/gnd/exp/expectation_author.py src/gnd/exp/session_contract.py src/gnd/exp/session_eval.py src/gnd/exp/session_store.py src/gnd/exp/session_v7.py src/gnd/export/pyrel_runtime.py src/gnd/export/souffle.py src/gnd/export/souffle_runtime.py src/gnd/extract/manifest.py src/gnd/extract/service.py src/gnd/fidelity/doccheck_service.py src/gnd/fidelity/report.py src/gnd/fidelity/service.py src/gnd/input_policy.py src/gnd/install.py src/gnd/json_input.py src/gnd/measure/promote.py src/gnd/measure/report.py src/gnd/measure/service.py src/gnd/model/__init__.py src/gnd/model/_validation.py src/gnd/model_queries.py src/gnd/model_verbalization.py src/gnd/population.py src/gnd/popvalidate.py src/gnd/rai_import.py src/gnd/recovery/inventory.py src/gnd/recovery/verify.py src/gnd/report_schema.py src/gnd/review/request.py src/gnd/review/runner.py src/gnd/safefs.py src/gnd/semantic_adapter.py src/gnd/solve.py src/gnd/synth/assemble.py src/gnd/synth/boundary.py src/gnd/synth/corpus_service.py src/gnd/synth/oracle/constructive.py src/gnd/synth/poolfile.py src/gnd/synth/provenance.py src/gnd/synth/service.py src/gnd/synth/values.py src/gnd/transition.py src/gnd/witness/io.py src/gnd/witness/service.py tests/support/rf7_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_session_pins.py tests/test_rf3_core.py tests/test_rf5_commands.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf7_consumers.py tests/test_rf7_input_policy.py tests/test_rf7_structure.py tests/test_v72_phase4_json_input.py tests/test_rf7_review_regressions.py --output-format concise

```text
All checks passed!
Exit: 0
```

### completeness-current

Command: .venv/bin/python -c from gnd.evolve.service import _parse_model_text
try:
 _parse_model_text("x: [1\n")
except Exception as error:
 print(type(error).__name__)

```text
ParserError
Exit: 0
```

### completeness-predecessor

Command: env PYTHONPATH=/private/tmp/rf7-inheritance-predecessor/src .venv/bin/python -c from gnd.evolve.service import _parse_model_text
try:
 _parse_model_text("x: [1\n")
except Exception as error:
 print(type(error).__name__)

```text
ParserError
Exit: 0
```

### predecessor

Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_session_pins.py --tb=short

```text
2 failed, 231 passed in 58.55s
Exit: 1
```

### predecessor-v3-unrestricted

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py::test_session_fresh[3] tests/test_rf1_session_pins.py::test_session_resume[3] --tb=short

```text
2 failed in 2.12s
Exit: 1
```

### predecessor-archive-confirmed

Command: PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=<predecessor-archive>/src <worktree>/.venv/bin/python -m pytest -q -p no:cacheprovider tests/test_model_v2.py::test_reading_validation_is_not_quadratic_in_the_parameter_count tests/test_public_souffle_successors.py::test_exited_group_cleanup_cannot_replace_output_refusal tests/test_install.py::test_iter_skill_files_yields_every_packaged_file --tb=short

```text
1 failed, 2 passed in 0.77s
Exit: 1
```

### affected-repair

Command: .venv/bin/python -m pytest -q tests/test_population_load.py tests/test_model_validation.py tests/test_model_v2.py tests/test_model_guarded.py tests/test_popvalidate.py tests/test_v72_phase4_json_input.py tests/test_public_v72_full_json_boundary.py tests/test_measure_offline.py tests/test_measure_coverage.py tests/test_synth_conforming.py tests/test_synth_values.py tests/test_synth_boundary.py tests/test_synth_mutate.py tests/test_synth_expectation_independence.py tests/test_digest_helpers.py --tb=short

```text
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! KeyboardInterrupt !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
<worktree>/src/gnd/terms.py:82: KeyboardInterrupt
(to show a full traceback on KeyboardInterrupt use --full-trace)
686 passed in 190.24s (0:03:10)
Exit: 2
```

## Measurements and branch coverage

Current graph:221modules, zero wrong-way layer violations, zero CLI entry violations; input_policy participates in no runtime cycle. The pre-existing session SCC remains RF8 work. No private-edge improvement is claimed; aliases increase that metric. RF7 routing/graph/query/entry controls include omission, new unguarded-reader, added/removed/stale query rows, extra occurrence, duplicate syntax row, cycle, layer, entry and unmapped-module dirty siblings. Reviewed direct cases cover byte/depth/event limits, quoted delimiters, duplicate/callback/Decimal, ISO siblings, literal True/nonboolean flags, diamond/cycle/ambiguity, regular/symlink/FIFO, changing file/close, diagnostic8 and accepted YAML flow/sidecar. No declared new refusal branch relies only on prose.

Original touched-file ceiling180 was exceeded by retained review/native/red/green observations at183. Explicit delegated amendment raised only that ceiling to210, before remaining artifacts, with183+27 arithmetic. Other ceilings stay source4000, test/data5000, non-evidence-doc1800, moved1000. Final measured values are bound in budget-final.json; this record does not claim the old180 ceiling passed. Production scope unchanged; most extra files are required evidence.

Owed session profile/merge/SCC work discharged2026-10-06 by014-phase-RF8.md. This annotation does not widen RF7 verification or discharge RF1-OQ2/OQ4 correctness/portability questions.

## Refactoring review

Refactors EXECUTED: consolidated input validators/reference traversal and regular-file digest reading preserve accepted-policy behavior behind the same direct/downstream gates. Newly restricted inputs are intentional observable changes, not behavior-preserving moves. Lazy parent access and independent sibling state remove needless repeated indexing and traversal coupling. Distinct canonical encoders/newline/preprocessing/digest meanings remain separate because their bytes are contractual. The private YAML error adapter is seen but deferred with its named target below.

## Boundary -- what this phase does NOT establish

A completed protocol walk adds no authority beyond its selected gates. One reviewer is one reviewer, not a panel/certification. Source-owned authority remains frozen; old certificates/release identities describe old bytes, and current-source/installed/release acceptance is unavailable. No publisher, certification, shim retirement, new command/flag/schema/family or broader protocol is enabled.

Default markers stay excluded. Full default/exhaustive historical/provider/native oracle/proof/census/evidence/distribution/certification lanes remain explicit owner or separately scoped CI cadence. The stopped accidental replay is not broad evidence. Exact v3 fresh/resume verifier failures were measured before RF7 and again unrestricted; these two nodes remain excluded from RF1 final checks. Exact106 archive confirms setuid Souffle test failure (4700 becomes0700 here); that one node is excluded from downstream initial closure. Historical RF2 source/RF3 numeric/RF4 body-count assumptions retain their earlier invalidation boundaries. Selected current successors speak only for their named inputs.

JSON parse caps apply before construction; not every original producer's upstream file read has been replaced by bounded IO. This phase specifically bounds the common load interface and repaired provenance sidecar. Standalone example/skill scripts and adjacent proof stream keep their explicitly named format policy. Media types, large validator rewrites, session strategy/SCC, and source-owned open questions are separate. No unmeasured throughput/soundness/acceptance rate is asserted.

At source35aa122, CI run37468958983 attempted four jobs but started none: account failed payments/spending-limit annotations; installed job skipped. This remains an exact old-source CI observation, not a verdict over repaired source or later documentation. Remote required CI must succeed before merge; no merge occurs here.

## Open questions

- R5 -> input-boundary hardening successor: decide uniform private evolve parser exception adapters; current/predecessor ParserError observed, no exposed route established.
- RF1-OQ6 -> successor milestone: interpreter media-type normalization remains deferred.
- RF1-OQ4 and RF8 -> session work: absolute contract path, session profile/merge/version strategy and existing SCC remain.
- RF1-OQ7 remains at the next phase editing its original support module; that module's bytes are unchanged here. New RF7 successor wrapper binds declared input bytes without claiming this old debt discharged.
- Original plan amendment integration/required milestone-close review -> milestone close; this phase does not edit the original plan or claim its old panel covers RF7.
- RF0/RF6 inherited source-owned, installed-release and current-attestation obligations retain their named successor/cadence boundaries.
- GitHub account billing/required CI -> repository owner/platform, before any merge.

RF1-OQ5 is discharged by current timed three-reader FIFO refusals and accepted regular-file counterparts, annotated on006 without widening its historical boundary.

## Final scaffold check

Command: .venv/bin/python -m pytest -q tests/test_development_scaffold.py --tb=short

```text
14 passed, 1 deselected in 4.82s
Exit: 0
```
