---
milestone: code-refactoring
station: phase-RF8
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF8
date: 2026-10-06
source_base: de4eed6ec143fdf03a39ab7a64b95a4e4013d24a
verified_source_commit: 5bd3ea2fcda859c3528d4a419d2fdf487fe39fe7
gate:
  command: ".venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_rf8_structure.py tests/test_exp_session_store.py tests/test_public_v72_reader_boundaries.py --tb=short"
  exit: 0
  output: "66 passed, 1 warning in 4.68s"
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Broad default, historical, provider/oracle, evidence/census, proof, distribution and certification suites are outside RF8 focused impact closure."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/013-phase-RF7.md, sha256: 704900b86a2eb2388b97e5a1f75d88fd37f6fa479d2816b716ddcf372bf6c9df}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G1-final.json, sha256: d9227a766cb46e36b6574d38975e53895243b453517419c9b6ed5b767d639d99}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G1-final.txt, sha256: 2dd277d65520271b3324fd5580e0d4df230d337fc471516e8c1f73ecd4fcf5d5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G1-profile.json, sha256: 7eca8c2f46a19828256c4fa3ab96ce31e1d475d15011e15e1a2ae9af68cc5e7c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G1-profile.txt, sha256: 19bb757873c461d6c5b33a890b32987d7bff9c40e4d818f51572697a2e185c6b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-complete-final.json, sha256: 1c9a1a6f8165ad03009423c19b4fd9a9ff9e741d75797ba03b9248bf1c3543f0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-complete-final.txt, sha256: d71b251af9e449463fef7866bc779ab831525faa6da2c5fcd82f9ab0ad64d859}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-final.json, sha256: 4c17c970dd997927f1723f74db164642b47674683475dd7b829c0bfdb3683c1e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-final.txt, sha256: 658e38be6014bcef3f4b0ca51284ce04aff8441aa9a93c61ab4c2e11b0872f61}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-repair.json, sha256: 8e3ae97dd4357a4b1c9711d14adc5b672c82a7c97753ca1c760b9861a64b1130}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-repair.txt, sha256: ad7ef56195a6e4bf2af34057b5d306952ffbb3fe1ffdbd5924c49175f49a37a3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-structure.json, sha256: 27bd0abbe353dbae379f5c263db389a81a37df5cb94ec437f757e812fd9c64a2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G2-structure.txt, sha256: 37c325ad0fbb1522ff16dbe61db7ec9076d105ab4db0ebc91ffe2aafffbb5a43}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G4-consumers.json, sha256: 0b6fe6578e7bc3f54efd398819a2d3f9525a3f6405391f348b0f1c279281f38b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G4-consumers.txt, sha256: a9a7fcf5752b917fa79eed1f1ba9a699067f7ba8ab9b20e558d5700b9209fded}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G4-descendants-permitted.json, sha256: 849c5f828e5b90667490d3b9bc284774482d19655f6dd05f9b93e51ba25da1e3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G4-descendants-permitted.txt, sha256: 8e8b8cf3c6f283db0cecc307e8f28af5c1490ce9fd9b1127af65f05df65b487d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G5-focused-green.json, sha256: 00ce50b71875b4548f9004d0952434abfb43eed8271e89af73cfe3ac7fe24e0c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G5-focused-green.txt, sha256: b31b4972881b26bc1e856de21bfd3922fa1b5b900136a5b8b22d172eacba2aca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G5-pins.json, sha256: a40b08d94cbb3daf84922d662bd266b0e7429ac0851581458d56f65e918a376f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G5-pins.txt, sha256: 493b42db0ecc87331ad3357d7a60b26ef81cada7075c9312df0d5dcf183cd0f8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G6-final-lint.json, sha256: 351e0298a6bba7afd4687f1f0eb4eedb7841a30331b00b50dc8d6336123edd7a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G6-final-lint.txt, sha256: 249d18a80178b8556774ad96b6663fc2e0b1f15c6873c8db6786fa23c9b173b4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G6-lint.json, sha256: 1149c300f3fd68c22d1a0ee9468fd484e42eb0dcdf8ff222010e6192daf939fb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/G6-lint.txt, sha256: 249d18a80178b8556774ad96b6663fc2e0b1f15c6873c8db6786fa23c9b173b4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/amendment-A1.json, sha256: 8caa4f848c964a2d6300a940f175b37302f33f0b066a99cf2dd3d0408e3e513a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/approval.json, sha256: 6b849e7f3f789d10d6a6695e3d9f1367b7b46389d45d0aed01b5454eccdb092b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/approved-spec.md, sha256: c6b419505d8c38d4745edbabadf2fd798bba81dd9ae81844ac80acdb8187294e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-session-corrected.json, sha256: 6fc494d766e3df9402ccc72bdab61febaabb0dcf2b3a19416d794e63d91f7490}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-session-corrected.txt, sha256: 18522c78c14f888628d8ce637ebb378b3ede3fb8ed82b8ccb803263b97de0d49}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-session.json, sha256: 79ec61c55664549cbc9c932ba3b24aa4cf489a87dcc16a3cbd2cb99e4f227e49}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-session.txt, sha256: d216fc8833c6225d8f1fe3f628e6ad8383d2acc3a14df04850ebdeb2f9dad973}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-v3-correct-path.json, sha256: aa98cf3918a66df00c741ac26d0261306837e70a0adc112c6243e9ce78abd82f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/baseline-v3-correct-path.txt, sha256: 45323da87804179f8452e7f3b1893173a97097d1be00c10f6205c33b9afc881b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/budget.json, sha256: 33ea80e1c3cb8030130525a1ced0a7577fdf3d55b61770f86efa2bfc2cb47e66}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/compare-final.json, sha256: afb354c27df906b8a8a5d372e397c2db19fd10139aa1df5ee51561f7e122d17a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/compare-source.json, sha256: 6c8d314c2551901cc240e4b2934945095cd264530fcf3c6992f409f1f4387c75}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/compatibility-final.json, sha256: 09235e9a2235b52447061ec1e4076d397b1b7dd8c7d7ac0a08fd2acd9460639d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/compatibility-final.txt, sha256: 0a2ca1c3fcb9d21cc33de511b9fe4751f5947d4fad471eb306f3e510b400919f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-green.json, sha256: 68a5e623450f3ee65cbb7cf5255859095bc0a32d6319df015d765b3024904096}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-green.txt, sha256: 9256347af80ca227134a12a0ddf5ef814d66724581b7b4d5c3490de71893f978}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-red.json, sha256: 268732f4ccdec6c73033312cc131b2bcac7c70026a01deaa96fe71e54f54ec25}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-red.txt, sha256: b105cc5fb0cae90243fd6d4574718886b296cd1bc7a54b3c252f849ff062201d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-structure.json, sha256: d638834fb9c557cfaa376d3782c4386b9c6063055918043af2ad35f487eb87a9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/direct-structure.txt, sha256: 6c6bd414bdeb4f3874d617116c94eac9d1bef2656c038018278f17fb818c8a93}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/dynamic-query-candidates.json, sha256: d27ae0f44380b6df61cbb6c943c1b76c841e3817d20ec85db887bf752231265f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/dynamic-query-delta.json, sha256: 2bfd0f30b040a728814bd201688de12d485f66b6d4e4129cca1e34ab0a79009a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/empty-reconstruction-red.json, sha256: e94dace8f0adc5231b01c0dfdfcfd82f9cb55dd19e05f9847315b477a4e1f481}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/empty-reconstruction-red.txt, sha256: 67f62d1c95908fa64f833b9a9fd05be48fb92eb40dc71054a5b5e1517b089274}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/frozen-controls.json, sha256: 633603f69199c82cde226e4adef6da1d10018ba27b85a9cd9da8ce5b416703ba}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/lint-repair.json, sha256: 32a408ef4f822cfa9898d1d9f50f80e5e07a1182dd1095be5954bec23d29c5a4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/lint-repair.txt, sha256: a042ade4a7910c2f7a1effe50f5568a4b192d3b77536643925d18feae8ac609b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/manifest-adaptations.json, sha256: bc7baf5078a9ced3082e36bd98709327478084ae006cf4040f58babf72da6ee8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-base.json, sha256: 9f1ff04326a1185f1c8e742a0593d8f7cc0d6e520b5c1e9bb325d6241d1f41aa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-base.py311.json, sha256: e2af1f72d29a84418ebb586c82923aacb6043f33dba1c9357e4c295fbf67e1f9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-base.py313.json, sha256: 86f684cb39bb4a6f9e8fb8d9f38aa8f946ad4ca6310a9b4be68727a93a60c980}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-characterization.json, sha256: fd6eb850df30e61749c65f7aefdb4c921c06fba2f134d1329ed41e27a14e40e3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metadata-characterization.txt, sha256: 9fec9ef525e43c6a9d4cb5cee7da87cb08dccd619d0eeee73d736b0564229e6a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metrics-base.json, sha256: dec6edff3715d8a7c08667f9f014bcac1d1bf80f2b8f782c3a264c6beec485f4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/metrics-final.json, sha256: 8eff0c42b3c5ad7b4e55148bb6586d1f9b163f4ca9c810c2e0cc312782bce875}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-control.json, sha256: 4f474a5e3c6bfc39d37fecd9911b47e96bf6e87d257b949f5a98096a660213ff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-control.txt, sha256: 04c9dd0c24b776e50eb128bf2a5eea883a17b67dedc2756df29f84408ee81568}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-controls-repaired.json, sha256: 969f3f02f6fde96b881b7c4f381db5f2478d84df10aaa2c979cb106b4879d7ae}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-controls-repaired.txt, sha256: 19b4ca07d3f9633013e42f030bf3d41b8bdd74cd982580b2cc561d378e08a164}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-observers-green.json, sha256: 680c472104e2a8995410bfe068bbae1e79984f744080e0679785c31bf702f983}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-observers-green.txt, sha256: ef378907d6f46b7dfcc3b0b77ca0d919a90b320c5cb767ae615a965ab73f2591}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-session.json, sha256: 5049ce44a165e13260ce35e19fb01342ae53cce70875ab71175df972b6d25d8e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/move-session.txt, sha256: fcf3433395726e29d07d9ffba7f38f498ac6179c54e6a15c01e984932414ae44}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/moves-instrument-correction.json, sha256: 3a45652a422c9536ad2dd5912fea4ad45434837e3ab7ee264e913c6c2d69f2c3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/moves-predecessor.json, sha256: 667fc641aae9462c98599d676a7f349eebb17ae0906b635c9f2c511d1fb479c3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/moves.json, sha256: 3e1c740655a74a06733cd6702115cdedd6692859540874515b2d6f01a1489adc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/predecessor-artifact-duplicate.json, sha256: 38e0443d596076f2b0e9f012d94cd448563ae2349e1bae0b493d98efc534cecb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/predecessor-artifact-duplicate.txt, sha256: e809aa80ff389d37bce4b9b4900d5f450e3f8a8d62cd33c014d5861f4bf0e78b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/profile-first.json, sha256: 708c6aa759c2225de941566e1c02e59879e42a8c56cdd5c9bfb61268d798ef71}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/profile-first.txt, sha256: 11c92ef53e8158209e56cadf3ced317413e8a571ad94c99ff8867b02a0d57d84}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/profile-session.json, sha256: 0bc33515a7d2889ed10a39ede6e7f381ae45720ce3ad64a23a8b333c6ecc627f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/profile-session.txt, sha256: e039af12b67a729fcb3c2f974f3f93f2a8bed694807eb7f40f4ae92abf2418a3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-final.json, sha256: 445b69adc0a68421765d89502783f16df9de0c0ada88cbca2b96d05c8d65113a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-final.txt, sha256: 573c789a20aaf6949adfe7afdf7d0641bd1968aec465750ad6f020e73d372746}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-profile-session.json, sha256: 3b591e4d87c5644c2b8268ef24c7d31343845f27c0f671382ca118dd140ae928}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-profile-session.txt, sha256: 288a4b71a71309c186194c410687b14a3da94d33704dc0d4a0541c2a5167b758}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-repair.json, sha256: f3f517636c8fe054c2a373edc5603513b26fb42d90c584b223069244016e67e9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py311-repair.txt, sha256: 931fc71763e1e0e4520f208fb24ece00761b670d38b910fc5a7f00d61c7a1f1b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-final.json, sha256: 00cd9de7b2e9a2238401ea200704366360f3265a5855db55822515e30d809aaf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-final.txt, sha256: 9a8c28042a28a048274d23585cca2c9720ce5a287624d7553af1a42f01e83c2e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-profile-session.json, sha256: 38e815d1f5e4325d183d4fb49a937782c3ba8060770b50903b54046b9b1b3bf9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-profile-session.txt, sha256: 95b3f402776ffa64d99a69aa50693585d461a39c2df66a60b258beaf999a659d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-repair.json, sha256: 05e9096d6f97b99889c1638d303bcc4b1f4baeea8afa7894fbc7102c2f45828d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/py313-repair.txt, sha256: f44f5b6df5228e1456408ede853682b8f7189a9d37242e40f08fe8f8d2152e82}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/reader-base.json, sha256: 6718f5b2cf5098a5b6c45f312e2f37175a12219ae8fc61b1cfbf887c10573a8d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/real-best-identity.json, sha256: d9bf24d2c6175b9a38cf692057cb7376dbe710a2695b1198f30c1afc927776a6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/real-best-identity.txt, sha256: 1afbf1363cae44e6cb45bebff2568fdff5645f4d35ef8c68c87e5568fb8ebd85}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-green-final.json, sha256: 5d7d69c8b98dd4560acd574c2ba89b7b309fdde93c0d187775be9ba24ced1bc2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-green-final.txt, sha256: db2f906695ba748f082485c76dbb6f697cd11be6f6233e599670b63a7c00ede5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-green.json, sha256: f61df9af0575929d16a283331eb39eca0f18598b4520eb34445bbe2bdaf32943}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-green.txt, sha256: 34192204eb9a6bd954dace68db1625ae8f2fe282522e0daccb5d4fbf0033c37d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-prompt.txt, sha256: c6b705b2e0a2333dd4ddbe2f6f1b3719b386d6160154da2f0b41cb8c2d32b8c0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-red.json, sha256: 90695dbe3c1b13ef239cc52cfba4b5ccebfa01daea3b8811b11999049ee7c944}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-red.txt, sha256: c8d6b2b9d679a84339786881c896d43cc07fc3a2a1e4e48336cf50ba6b7af027}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-repair-prompt.txt, sha256: 8562319aaae370eb38de3d62ee54b36c8736c113f75a579adbc2848e6f9e1494}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/review-transmission-block.json, sha256: b0a355aa5a3b5f7a935bbc14d5d0b5289ef7b1a7656168cc8d1e8cd46e4cb354}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/shim-final.json, sha256: a392bc151d0143e24c93f459e5ada5d36d89f172ea10f9ae44667fd408377bb6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/shim-final.txt, sha256: b1af306310bf6fc0063545be793a0e15153845b27bf19f952667ae70b465794e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF8/v7-bindings.json, sha256: 1950b3a5980e8fc604513de9ded9c988f31c869c5d17566643547d4ba75acd91}
  - {path: .gnd-planning/milestones/code-refactoring/notes/RF8-implementation-status.md, sha256: e8105c81fb27aa81553dd65bf31686dddf608b1d9028618462381264c851be77}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF8-codex-repair-review.md, sha256: 6b11945938aeb783b17d8598062fe84bf4cad6d073c0e3f726c4cdec127c7c3a}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF8-codex-review.md, sha256: 33b3cc4c53b1e3f135a11b8f773cf46c1a8de8c60846c6265ec493aa5d111893}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF8-spec.md, sha256: 6b42ff559fb07476d10e64e7b7b3701efe4feeadb2deda7e5a29e406bfee089a}
  - {path: .gnd-planning/milestones/code-refactoring/notes/shim-inventory.md, sha256: b5fe10534ab4a4e80c681e3aa847474fdd7eeaba70a44d5063be6da729c0879c}
  - {path: .gnd-planning/milestones/public-launch/migration/b3-files.json, sha256: ea4106a4252085052840b4eae40fd9c9c8b22bc4fa46553912bc7572685dcf87}
  - {path: src/gnd/exp/close.py, sha256: cdbf9bbb78f8c6c2f692c0298c2fea09d088a293e9fbc0241ddc8e7fcb7105ec}
  - {path: src/gnd/exp/session.py, sha256: fa1229dbd41bb3bc7be0c9bff3e8490a9856c146cc2e47f10cf25c82a4dd7b9e}
  - {path: src/gnd/exp/session_contract.py, sha256: c5b5ac2b9b8994e7f984829289d90bda325668f4f5e5855a644bfe4e9023ec84}
  - {path: src/gnd/exp/session_control.py, sha256: 07e5fee609aa52579f11383661c3fb66d50ace75f3757570e13a46d2af351eb5}
  - {path: src/gnd/exp/session_environment.py, sha256: 434dd3c2e6905455f533f4e1fade7275a1b70cba4f106dcec027decb5fdaf0d0}
  - {path: src/gnd/exp/session_eval.py, sha256: 5731ee21bd17b0062c3bfb367323e36b92e880490ded38c71fef99c2c6f3bd4b}
  - {path: src/gnd/exp/session_judgments.py, sha256: 89ea960f36d4b182431b3c195adeeb1d14f6e04b71bd20382df6b03bb033c437}
  - {path: src/gnd/exp/session_patch.py, sha256: 0cba429fee0cdfb01bf056de020531f30ba8776e85e44bd8d778f3081a5a460c}
  - {path: src/gnd/exp/session_profile.py, sha256: a7d19007ee7b2c26199bbf101f87d6163d928c5b9549b9c6ca638744f58edf6d}
  - {path: src/gnd/exp/session_records.py, sha256: 66effaf2d9a469408120bd5356d7b084f3e02c66a4a9b8d44ec99a96b1a17910}
  - {path: src/gnd/exp/session_replay.py, sha256: ae90b5aa0ae8ae2bc5f035c2e37366c5b9470dfb053315846bf05b30216f7557}
  - {path: src/gnd/exp/session_runtime.py, sha256: fab7def65c678f59b0c3dfc93628470d285b7bdd21143196ed3d18cafef60a97}
  - {path: src/gnd/exp/session_store.py, sha256: a9bf60e73f84eac00b412c5c51599ba08de6d96303de7f45b5a8886ade421b0e}
  - {path: src/gnd/exp/session_v7.py, sha256: 0b4f18e6daf4c6a0476bd36dad6327f85be88fd0db693311fb510c8dfe72ce45}
  - {path: src/gnd/exp/tests_runner.py, sha256: 33b02cf6754daaeb1f16707dab08a6ab71d56aab06efd00d8a9bcf76f8a152f9}
  - {path: tests/support/rf8_sources.py, sha256: a892ea135601cabefde59193b626427683d66cc252eab856df85852ce3c470cd}
  - {path: tests/test_artifacts.py, sha256: 18273d1a949f17e859a4596e9787317046e15e3cbc8134e8a1b166c52296afd4}
  - {path: tests/test_exp_session_evidence_compat.py, sha256: 166f04e534f5879c824251c09bcc5813260ec336beb85d0330b04f2b32c73188}
  - {path: tests/test_public_payload_alias_sites.py, sha256: 6311fc233e79aa274955c367c2e4dc1f2a17ae9e78c4ff758fd9122384a24eb4}
  - {path: tests/test_public_v72_reader_boundaries.py, sha256: eab8ff8a4fcff50887e80006c48d8f3e71c106eae022abafcd406cb989ed9746}
  - {path: tests/test_rf6_query_policy.py, sha256: ca895ef59e3088431d23d62e6733d91e3ea8592055db9c62aef49ba9a3e3119f}
  - {path: tests/test_rf8_sessions.py, sha256: 272ed3cf168c3b6ce0182109c5c3a07cc9fbecda68b69520b66d3fd2fe8b1f48}
  - {path: tests/test_rf8_structure.py, sha256: fcfc70ccdb8f95464966cd963ed2514cf9f56a5f8ec662bf98f3c6bf632144cc}
  - {path: tests/test_v71_phase4_successors.py, sha256: a61bac83ef00b05c9988dc0e51803ebc275121c82d9b4b70cbdd82fb773ae6a4}
  - {path: tools/gnd_layers.json, sha256: bb7d40496fbb0317ee2ce3863aee8eb3c9465801b616c7d4499d0085924298e7}
---
## What shipped

RF8 completes the session profile and v7 merge on the existing topic branch. Production source is5bd3ea2fcda859c3528d4a419d2fdf487fe39fe7; subsequent documentation does not change those bytes. The effective r2+e1 milestone plan was consumed, not edited. The RF8 auto invocation supplies delegated spec/amendment approval, not a claimed human reading of the artifact. Original approved-spec.md remains bound to approval.json; provider transmission was separately authorized by the owner's approved reply after an automatic rejection.

SessionProfile is an immutable runtime capability table for versions1--8; it is absent from wire dumps and JSON schema. Reader dispatch preserves original equality/unknown-version behavior. Direct construction and model_copy refresh capability selection. The first live SESSION_CONTRACT_VERSION=2 capture remains; the judgment contract version8 literal has a named constant. Legacy feedback/result precedence and v7/v8 launch, feedback, attempt and result axes remain distinct.

session_records holds wire evidence definitions and reader/collector helpers; session_environment is the verifier environment leaf; session_control holds invocation/disposition helpers; session_replay holds reconstruction/evaluation; session_runtime holds execution. These homes remove store/controller/evaluator back edges. session_v7 is a58-line import shim preserving nine original top-level definitions, the same _HIDDEN sentinel and47 imported bindings. Top-level and owned method qualifications remain their original paths; frozen launch-v2 aliases remain qualified separately. SessionStore.best_identity()/best_record() expose reconstruction's identity/record without additional IO; _v7_best retains its original tuple meaning for compatibility.

Physical observers follow new homes: payload aliases, reader AST bodies, artifact canonicalizers, environment/publisher patch owners and RF6 query syntax inventory. Listed AST substitutions are exact capability/import replacements, the identity cache extension and the two cache resets in the successful missing-contract empty branch. Arbitrary extra body statements still break hashes. Original golden fixtures and source-owned units/test remain unchanged. Twenty-four migration adaptations retain predecessor rows/hashes/modes and record changed current identity; they confer no installed/release authority.

## Criteria and own branch audit

| Obligation / declared branch | Current falsifiable evidence |
|---|---|
| RF8-C1 / SM1: identical version x path session observations | All28 RF1 session nodes, including v3 fresh/resume, pass after the preedit PATH correction; both supported native minors rerun all28 plus16 direct profile cases |
| RF8-C2 / SM2: shim and moved names | Shim58 <=60, all47 original imports plus10 original definitions/constants, object identity and qualification, hidden-reference projection, actual new-home environment/publisher patch effects |
| RF8-C3 / SM4: no session SCC and complete map | Base221modules/one7-member runtime SCC; current227modules/no runtime or module SCC, no wrong-way/entry violations; dirty cycle/edge/entry/missing-module cases fail |
| SM3: physical observer liveness | Reader/alias/artifact/query observers follow moved homes; dirty reader extra statement and graph/map omission controls refuse; old frozen body fixture remains frozen |
| Profiles1--8, unknown/hostile equality inputs, wire exclusion | Version capability rows, None/0/9/list/dict/string, original True/7.0 equality, immutable mutation, schema/dump exclusion, same/different-version copies |
| Legacy wire precedence and patch axes | All six feedback and four result precedence arms; both v7/v8 four-axis tuples; full normalized wire replay |
| Reconstruction absence/presence/terminal/judgments | Empty1/2/6/7/8, real selected identities7/8 bound to manifest SHA, stale identity/record cleared for empty7/8; consumer terminal/staging/recurrence/close/publication/judgment controls |
| Bounded algorithm claim |100000 profile lookups below5s is a local falsifiable control, not a verifier throughput claim |

No declared new branch is shipped on prose alone. Counts overlap and are not an aggregate acceptance result. Earlier original body hashes/signatures remain predecessor observations; current physical controls explicitly bind their successors.

## Review and findings

Initial independent native Codex review of6a08750 found two issues; both triaged blocking before repairs. R1 violated SM2 by omitting the moved _HIDDEN sentinel at the old module path. R2 violated public best accessors by leaving previous caches after a successful empty reconstruction. Primary review-red observed3failed on the pre-fix source: sentinel, cache7, cache8. Repairs restore the exact sentinel object and clear identity/record only on the successful empty path. The final regression/affected-store/readers gate observes66passed; native session/profile gates44passed each and graph/observer gate92passed.

The first repair gate was4failed62passed because the newly written sentinel control supplied an object instead of a hidden-reference set, and the AST observer compared unparse parentheses. These instrument errors were corrected, failed observations retained and successor gate green. They are not hidden product findings or changed approved fixture meanings.

Initial reviewer confirmed capability table, valid-version copy refresh, schema exclusion and absence of cycles among14 inspected session modules using small read-only probes. It did not rerun reported replay or consumer suites. One reviewer is one reviewer; the bounded repair pass is not a panel.

Implementation findings remain retained in the spec: initial runner resolved the Python symlink and selected an interpreter lacking pytest; corrected PATH before source moves made all28 baseline replays green. Old V72 raw body fixture hashes were stale on exactde4; frozen originals remain, exact base AST successor recorded. A frozen launch-v2 alias needed explicit qualification. Profile-edit placement initially omitted a legacy return/misplaced cache assignment; direct empty reconstruction was observed red before repair. Original moves instrumentation hashed two bodies after import retargeting; exact predecessor successor retains the first instrument. Ruff expanded the shim beyond60 before explicit compatibility imports restored58. None is described as an original passing result.

## Measurements and budget decisions

Measured session_v7 predecessor is976lines, not937 copied into the original goal estimate;58current lines meets the unchanged60 target. Final compare5bd3ea2 versusde4:3248 added,2243 moved,1005 nonrelocated raw source additions. Original650 estimate is missed. A5 delegated retarget1100 retains raw accounting, including303 unmoved blanklines in the initial comparison, rather than silently replacing the metric with nonblank additions. Moved2243 <=4000. Tests/data and non-evidence documentation remain under1600 each; final budget.json binds exact totals.

Original touched90 was missed, A4 raised it to120, and A6 before review repairs raised it to140:116 retained +12 minimum review/regression/native/record paths=128 with12 bounded final-evidence headroom. Final measured touched count is in budget.json. These are phase-scoped delegated evidence amendments and declared original misses; integrate the unchanged plan's estimates at milestone close. Prior RF6b original400 facade miss and RF7 touched ceiling miss retain their own close obligations.

## Refactoring review

What did this phase's work reveal about existing structure that should change? Refactors EXECUTED: split wire records from the store, environment from controller/evaluator, replay from execution, and explicit profile policy from consumer version switches. The same selected green replay and downstream gates preserve behavior. Public best accessors remove production inspection of the old private tuple while preserving compatibility. Explicit shim tables and current physical observers replace stale implicit module ownership. No new registration/string-import edge evasion or blanket layer exemption was introduced.

Seen but deferred: CLI missing-result resume correctness belongs to the session-controller successor; absolute prompt path portability belongs to the session-portability successor. Historical reader raw hashes and broad ownership guard need milestone-close disposition, not silent fixture rewriting. No helper/schema/canonical encoder unification beyond this bounded session dependency change is claimed.

## Boundary -- what this phase does NOT establish

No new semantics, commands, flags, schemas, wire/digest/unknown-version changes; no shim retirement; no old certificate over changed bytes; no source-owned question transfer; no full historical replay, provider panel, certification, milestone close, release or merge. One reviewer is one reviewer. Local normalized replays do not establish unnormalized timing, nonce or producer identity equality, Linux/installed/release acceptance, or correctness of characterized refusals. Reviewer small probes do not independently establish our reported suite counts.

G4 initially1failed515passed because the sandbox denied ps in the existing descendant-drain node. A permitted bounded retry of only that node passed1 without source/test edits. G5 initially1failed427passed1deselected: its packagewide primitive ownership guard flags safefs.read_regular_file_bytes. The exactde4 archive with its original test reproduces that same failure (exit1). The focused successor excludes only that node plus the configured lane,427passed2deselected. No passing original all-green G4/G5 claim follows; the scoped controls and predecessor proof describe these exact observations.

Configured default markers remain excluded. Full default/exhaustive historical/provider/native oracle/proof/census/evidence/distribution/certification suites run only on explicit owner or separately configured CI cadence. Original source-owned units and authority test are frozen. Current source and changed migration identities do not establish installed/current attestation or release acceptance. Remote required CI must succeed before merge; no merge occurs here.

## Open questions and refuted premises

- RF1-OQ2: preserve characterized v2/v3/v7/v8 CLI missing-result resume refusals; correctness decision remains session-controller successor. RF8 spec made this ruling without altering bytes.
- RF1-OQ4: digest-bound absolute prompts remain; session-portability successor decides relocation policy.
- RF1-OQ7: original RF1 support scrub/declaration debt remains next phase editing that module; its bytes are unchanged.
- RF7 R5 private evolve YAML ParserError remains input-boundary hardening successor; unrelated to this session move.
- RF-D5 shim retirement remains separate explicit approval after the first public release afterRF6.
- Historical V72 raw-reader hashes, original90/650 RF8 estimates and earlier RF6b/RF7 misses -> milestone-close plan/measurement integration. Existing aggregate primitive guard -> milestone-close ownership disposition; red proven on exactbase.
- RF0/source-owned/installed-release/current-attestation obligations keep their named scopes; no new certificate or accepted authority handoff.
- GitHub billing/required CI -> owner/platform before merge, if current-head checks reproduce the existing platform refusal.

Refuted premises: baseline v3 unavoidable refusal was a PATH instrument defect; historical raw reader hashes did not describe exactbase; original937-line estimate did not measure base976; original90/650 budgets underestimated explicit compatibility/retained evidence. Exact unsuccessful observations and explicit successor/amendment paths remain bound below. The profile/merge and session SCC work owed by013 is discharged by this record without widening013's historical gate or closing the distinct RF1-OQ2/OQ4 portability/correctness questions.

## Bounded repair review

The authorized single repair review found no current blocker or hardening issue in the two repairs. It independently probed all47 import identities, nine moved definitions plus sentinel, pre-fix stale cache7/8 versus repaired empty return, refusal/terminal cache retention, and AST dirty-statement sensitivity. It did not run exact pytest nodes, bound-contract normal replay or reported66/44 matrices. One reviewer is one reviewer; two readings are not a panel. No further review round is selected.


## Gate output (verbatim)

Exact commands, summary lines and exits follow; complete sanitized streams are SHA-bound above. Failed intermediate gates remain bound as instruments, not final passing claims. Counts overlap.

### baseline-session

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --tb=short

```text
2 failed, 26 passed in 28.44s
Exit: 1
```

### baseline-v3-correct-path

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py::test_session_fresh[3] tests/test_rf1_session_pins.py::test_session_resume[3] --tb=short

```text
2 passed in 2.49s
Exit: 0
```

### baseline-session-corrected

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --tb=short

```text
28 passed in 31.27s
Exit: 0
```

### direct-red

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py --tb=short

```text
5 failed, 1 passed in 0.22s
Exit: 1
```

### empty-reconstruction-red

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py::test_empty_reconstruction_returns_state_and_public_identity --tb=short

```text
4 failed, 1 passed in 0.46s
Exit: 1
```

### move-session

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py tests/test_rf8_sessions.py::test_old_metadata_is_unchanged --tb=short

```text
29 passed in 29.90s
Exit: 0
```

### move-observers-green

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py::test_old_metadata_is_unchanged tests/test_public_v72_reader_boundaries.py tests/test_public_payload_alias_sites.py tests/test_exp_session_evidence_compat.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_v71_phase4_successors.py --tb=short

```text
69 passed in 19.50s
Exit: 0
```

### G1-final

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_exp_session_contract.py tests/test_exp_session_evidence_compat.py --tb=short

```text
84 passed in 0.99s
Exit: 0
```

### profile-session

Command: .venv/bin/python -m pytest -q tests/test_rf1_session_pins.py --tb=short

```text
28 passed in 28.93s
Exit: 0
```

### G2-complete-final

Command: .venv/bin/python -m pytest -q tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py --tb=short

```text
91 passed in 16.36s
Exit: 0
```

### G4-consumers

Command: .venv/bin/python -m pytest -q tests/test_exp_session_store.py tests/test_exp_session_eval.py tests/test_exp_session_rank.py tests/test_exp_session_recurrence.py tests/test_exp_session_e2e.py tests/test_public_session_wire_guards.py tests/test_public_retained_session_results.py tests/test_public_session_version_relabel.py tests/test_public_v72_session_staging.py tests/test_public_patch_publication_identity.py tests/test_v72_phase5_session_mechanics.py tests/test_v71_phase4_successors.py tests/test_public_v71_judgment_successor_guards.py tests/test_public_payload_alias_sites.py tests/test_public_v72_reader_boundaries.py tests/test_public_v72_ownership_direct.py tests/test_public_v72_status.py tests/test_exp_close_work_gate.py tests/test_exp_close.py --tb=short

```text
1 failed, 515 passed, 1 warning in 48.56s
Exit: 1
```

### G4-descendants-permitted

Command: .venv/bin/python -m pytest -q tests/test_exp_session_eval.py::test_timeout_kills_and_drains_descendants_before_returning --tb=short

```text
1 passed in 4.26s
Exit: 0
```

### G5-pins

Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_semantic_pins.py tests/test_artifacts.py tests/test_packaged_skills.py tests/test_development_scaffold.py --tb=short

```text
1 failed, 427 passed, 1 deselected in 37.94s
Exit: 1
```

### predecessor-artifact-duplicate

Command: .venv/bin/python -m pytest -q /private/tmp/rf8-base/tests/test_artifacts.py::test_no_module_redefines_a_promoted_artifact_primitive --tb=short

```text
1 failed in 0.37s
Exit: 1
```

### G5-focused-green

Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_semantic_pins.py tests/test_artifacts.py tests/test_packaged_skills.py tests/test_development_scaffold.py --deselect=tests/test_artifacts.py::test_no_module_redefines_a_promoted_artifact_primitive --tb=short

```text
427 passed, 2 deselected in 36.75s
Exit: 0
```

### G6-final-lint

Command: .venv/bin/ruff check src/gnd/exp/session.py src/gnd/exp/session_contract.py src/gnd/exp/session_store.py src/gnd/exp/session_eval.py src/gnd/exp/session_replay.py src/gnd/exp/session_runtime.py src/gnd/exp/session_profile.py src/gnd/exp/session_records.py src/gnd/exp/session_control.py src/gnd/exp/session_environment.py src/gnd/exp/session_patch.py src/gnd/exp/session_judgments.py src/gnd/exp/session_v7.py src/gnd/exp/tests_runner.py src/gnd/exp/close.py tests/test_rf8_sessions.py tests/test_rf8_structure.py tests/support/rf8_sources.py tests/test_artifacts.py tests/test_exp_session_evidence_compat.py tests/test_public_payload_alias_sites.py tests/test_public_v72_reader_boundaries.py tests/test_rf6_query_policy.py tests/test_v71_phase4_successors.py

```text
All checks passed!
Exit: 0
```

### real-best-identity

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py::test_best_identity_matches_real_reconstruction --tb=short

```text
2 passed in 1.88s
Exit: 0
```

### review-red

Command: .venv/bin/python -m pytest -q tests/test_rf8_structure.py::test_v7_moved_sentinel_stays_importable tests/test_rf8_sessions.py::test_empty_reconstruction_clears_previous_best --tb=short

```text
3 failed in 0.27s
Exit: 1
```

### review-green

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_rf8_structure.py tests/test_exp_session_store.py tests/test_public_v72_reader_boundaries.py --tb=short

```text
4 failed, 62 passed, 1 warning in 4.25s
Exit: 1
```

### review-green-final

Command: .venv/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_rf8_structure.py tests/test_exp_session_store.py tests/test_public_v72_reader_boundaries.py --tb=short

```text
66 passed, 1 warning in 4.68s
Exit: 0
```

### py311-repair

Command: /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_rf1_session_pins.py --tb=short

```text
44 passed in 32.63s
Exit: 0
```

### py313-repair

Command: /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf8_sessions.py tests/test_rf1_session_pins.py --tb=short

```text
44 passed in 33.78s
Exit: 0
```

### G2-repair

Command: .venv/bin/python -m pytest -q tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py --tb=short

```text
92 passed in 17.02s
Exit: 0
```

### lint-repair

Command: .venv/bin/ruff check src/gnd/exp/session_v7.py src/gnd/exp/session_replay.py tests/support/rf8_sources.py tests/test_rf8_sessions.py tests/test_rf8_structure.py --output-format concise

```text
All checks passed!
Exit: 0
```

Final byte validation: git diff --check exit0; frozen-controls.json all432 unchanged by SHA-256; current metadata/graph controls are in review-green-final/G2-repair. Neither shasum nor collection is a broad acceptance gate.
