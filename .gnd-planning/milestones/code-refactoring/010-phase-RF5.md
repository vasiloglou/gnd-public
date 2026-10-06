---
milestone: code-refactoring
station: phase-RF5
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF5
date: 2026-10-05
source_base: 29915d9f7651151d3a6f3c169764c7c84ab0110d
verified_source_commit: 6a57d4e20260b72e0245aedbb0195fbfd4643e6d
gate:
  command: ".venv/bin/python -m pytest -q tests/test_rf5_review_regressions.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf1_layering.py tests/test_gnd_arch.py"
  exit: 0
  output: "426 passed in 12.18s"
  note: "Focused current ownership, routing, compatibility and architecture controls; additional exact gates follow."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Full default, historical, proof, census, evidence, distribution and native lanes were not selected."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/006-phase-RF1.md, sha256: d762dedfce04adf9b72776f61f209b572475775ce061d3aea1bd0cabfb5f6b3e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A1-spec.md, sha256: 3aa67d677c32134d426f8b405f191fc4272004c86dda334297f9b250b2fa7cb4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A2-planned-homes.json, sha256: 5122a08a2c08472c41977742eef9c35a0bb31ae0dc2dd5be4cda0f2e0bcfb1df}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A2-spec.md, sha256: ae47111f0b8dbbe38de72598e10f7467eed803a67941175ab2abf980fbced13e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A3-spec.md, sha256: f00fabca826bdcca85bfb49cdd81524b48082a6b797b03b4d84d92e55aa45956}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A4-spec.md, sha256: 68fb5e6f72b34e450388c0220e6bbf35013dec181b694c18d9c0c9ac3cb84498}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/A5-spec.md, sha256: a7228b3d112eda496173cb530936deb5cdbe2fc6f2183ee9dd47957f8517568d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G1-frozen.json, sha256: f2634327a535fd60bf8b51b892f67cd2b8f04c42d9c7841bece6cdc60130e9fb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G1-frozen.txt, sha256: dbf372a86945e2276f403ad174b31882329ee4321cff3fd43d22104b94e9d236}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G1-impact-mutations.json, sha256: a18f2d233a5087ca2698773150cb856925b2ececc7bf2fd2a2037c892f239b22}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G1-impact-mutations.txt, sha256: ff6bb6bf1f1780025e229a126206ad19c0307cf8192328791506ecdfb4ac11b2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G2-ceiling-control.json, sha256: 56b33c46b2867631f0159e414e5d6b16fd8ffb4198f0247c3fe2be6809ef4dff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G2-ceiling-control.txt, sha256: 304438366512c6a868ac883a4b4b937a9a094aa3afebdef15db157a6c1221088}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G2-final.json, sha256: 11a8f0240569ac1e48fb15c29572b2973f03be79a2a40221cd52ea6aef906efe}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G2-final.txt, sha256: 8446e4ddb0c615c5bddb799a32c0e5a4df1c464973ef22fb6a8e56924a11a828}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py311-repaired.json, sha256: 9f4ec3430f62824bb7c6da148e7388a1ddf0554ea2517e6a4aa763e369631b37}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py311-repaired.txt, sha256: c6c1d325eea5705727e1de4628ed47d7b949ca475e3e787a5ef11af54fda66f3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py311.json, sha256: 084924d7abcd6f269f13f48cc65030b4c40a3d11298642ea70846b12da99aa8d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py311.txt, sha256: e1e0d8a0d15e6293577a16c5e1c38ae550e0724f3b96dd04f84795e8295f6e62}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py313-repaired.json, sha256: f12ba5a036227b0426ef94b7e226c053376002f16786ce820a40cc09cadab8f9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py313-repaired.txt, sha256: 81bdfd556ee464f1ac5666c0df33432206af53368a0de5f506a86adbd33bb84c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py313.json, sha256: 406e3489d237b4d17c0b6c01928cf7efe64461491c595832e48cb5c385cd141f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G4-py313.txt, sha256: 79b30c75c2c5054ae30c6b2604a6027aaf10c4f277c1e091522ef30f89199300}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-controls.json, sha256: 72f27fb84ce7c35da032cfe30b2728909090e6905cf1a93016796e40794daaeb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-controls.txt, sha256: 9cc50fd1fcfce893dfb75880fdcdffc60eb66ec1f90f958285bd9775f91bcaf6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-final-lint.json, sha256: 1a0afc593a68d597f405caa62b908d46564c0e728db35e7912d88f2f18567a93}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-final-lint.txt, sha256: 14173a7aaae93b4ae6abea3530f6e90b73dd8779825f6334d5d1a65d1aea1dc1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-lint.json, sha256: 7feb0c21bb1651ad073994665c95ce09924679baaa15e6855fe882dcacc43335}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/G5-lint.txt, sha256: fe8d96c77a1a3e2a6649ea30cfea088299a1e6f40e0f14e9b5c36449405047e7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/approved-spec.md, sha256: 2dc5f35176f3028bba89a901870fd33179396553456f16f52f911331050b6938}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-compare-repaired.json, sha256: d60c34671dc012fcf3266e66e907efa34ced845f086cb60d2d84db8c7dfba72a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-compare-repaired.txt, sha256: a5ecee9455d131e0224e26e72cf78c561f107507473465bf4e2e74c62f571c44}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-compare.json, sha256: 8ff95d9fa2cd909529b7d37d83cc8c14596647316dae6848075a7d748dfeb696}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-compare.txt, sha256: 01a8c0f6265782f5798414cbe4c977b9bb1127723275540f6f59f40ccd7a8553}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-measure.json, sha256: cbf10d7e04a8be1454ef7617892d117afe83a2dd596cbe458ac257dd86840fd4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/architecture-measure.txt, sha256: 06c673df1ead0c06dec36ddd3cfe5b37ef1e407a6be9f1ad4f5012720b772b64}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/authority-frozen.json, sha256: 40bb817973e602b11d86a7fb84f8e4886d03a01a2ee631a5ad49eb59e64430c0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/baseline-G0.json, sha256: f9cb65e598a8728243a3932f685150d841137e99a2fec8db258f0b24d0d39ff8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/baseline-G0.txt, sha256: 0f67bc5fd73036f84af54641f85dd91f631954c3344c7aafea622476e9436683}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/budget-before-review.json, sha256: 23ece03a94e9d5c3e208596cc53ed0a5fb63bd86252f0a4d52e2e04bac5a638a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/ceiling-py311.json, sha256: cf7bdffea8817cdae7019211f61065e3485715029daf761beeacaffa4d74477c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/ceiling-py311.txt, sha256: d015c7fc1006427c765361b487b3f911ce1eafdfa41fcd8ca0135bf293761bd4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/ceiling-py313.json, sha256: 9f94929734c2554f3d3ed0f43a384b92e90fae8e450aa31b30959ae2a5252808}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/ceiling-py313.txt, sha256: c4d58bba31251973cc528015d6333f9caf2c299de3530cc1622bcd83dd330d09}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-final-imports.json, sha256: 6bffd355d68dc22f2a333e78ed882ae311365ea4260bc32980717e058452b745}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-final-imports.txt, sha256: cc825ba580f0b9363c386028fb5e76dca76f062f2963b400562ad25f9142a578}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-final.json, sha256: 2004cd82bc14730d0a9d5626a87cc1237ec3fa64d67d8e2c1ea3e2fdd0352fd0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-final.txt, sha256: a2d9a5d04f93ccb7c990652f45f7b471ff01cda73b7b58d8778d5f2a910d5a6e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-pre-move-red.json, sha256: 8510c0e4600d2ffd4906400f47d8ebb26b1e266f50a4e8302748bc2ff9a6f715}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/definitions-pre-move-red.txt, sha256: 0f9a83893ab5d72fd29138cb918e6d73126e949d813a189eb25c31c0e29fe5a8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/direct-collection-counts.json, sha256: 80d0b1c3fefb1eebc078fbdab582e580ecad4f192c9ce4d4314becb9e31fa763}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/frozen-inputs.json, sha256: 720724b054dc57d4b5275539c554dc8ec793310b91215cc3d531be75b5aecf4c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/handler-corpus-frozen.json, sha256: bc0fc17a759ad7160eb0b6164c7e0d2f46df8b956021481b046246b31da62b89}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/initial-definition-moves.json, sha256: e3753d42fd367b15042c933caba3e52517ac1bdc0c90cd0503156d70d71bf2f5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/initial-handler-answers.json, sha256: 376d8f2ec0905981841e5feeaec2473a104d17931cb86aaf363d6f12020441b6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/initial-handler-cases.json, sha256: 4a3ce1dbbd994afd31bd07412402dcc06166cde4e308f35f6fa143c0c737abad}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/initial-review-run.json, sha256: 92dae074b609b0b36b519efd1c3256b9b726a2c2475bb8f47cdb8d32ca6150e3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/legacy-lint-dispositions.json, sha256: cd4821e1a67aedd0eef007f0267dfa8304e1b23fa423feee6378492a6ec5f80c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/manifest-adaptation.json, sha256: 05080d084a617debb3c4ed5d261d9ab505e2b5a308afde1d7414a546bc77cedd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-boundary-repaired.json, sha256: e794e0a3aaa973ef8d57c656bd5b710b78cfe744065b4e2392e53f0cd1b13df0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-boundary-repaired.txt, sha256: 29955d48cb6412484c00c07589007634b3ee38a3fb52caf533a74013595b16cc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-guards.json, sha256: 8b77af43ed91ef6472e240d4c808e18b2532c9b75a9f6ce042702d3b216b7b9f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-guards.txt, sha256: 81c5e175ee85683a4247a47f5dca81b0c2d017fea5e5bf41b6d9d47bdb28ac6b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-initial.json, sha256: af6a1dade0058956dfc6ce2a2572b5fe4a4d5830b6d7c6743c4a99d22268405b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-initial.txt, sha256: e43fa560657284af9f9f6669812332a09d6316e44450b29c8c6e129d7402a1fa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-repaired.json, sha256: 70616ff614e0e9972c500bd309c1130440c2ada4c3f2a85b88f40363af8add13}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct-repaired.txt, sha256: b670114a0b968154a7228f30072f4cf25dd35037735ff08c513ba0ce720f2b45}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct.json, sha256: 0350e44103599251a2a580a8c821c706d6e0f38c560078f89a3a7e35267b50c7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-direct.txt, sha256: fda95112af397d7838d995221310f542075a76a19ba3b9b1955477141512ee15}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-handler-pins.json, sha256: 1169810213ab172fb4ac41fdae84ce8106710dae8bef90be38762b60d57e5672}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-handler-pins.txt, sha256: 7384e0df3864347433e6953ad9e303a24482e6e87506e1d2dd1b9c1b31457fd7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-impact.json, sha256: 1cac9c1c1a551552c055dd716f4ed3a30db6d98b3506d2ee68b44f69824bb692}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moved-impact.txt, sha256: 123c9c2fab832fcfca1196c6638fa089510b14e926bd4307141a475462a5296f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/moves.json, sha256: 50cbd903d32e07ff48b1d588c072de9b32fc39eea02a7f6c41dc5fac751dae14}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/mutation-retargets.json, sha256: c350a2b9eb186af935167793aa209a09ae0969543a0cc3c644829a69bc9c19fe}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/mutations/control.txt, sha256: 13399d37edc5cda287c4c90d548c3d39fc2fba12180cfebb89ba0c0ec2a842f1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/mutations/mutation-report.json, sha256: 304e68838f44c268ccf23281c8df691530f2d104835eef2ca29f1082fb1ca298}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/planned-homes.json, sha256: cb5a0225ed09fe249ed9555802674812fd1eb00d3e0fcb5d4ec1c97ffabf4c43}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/pre-phase-replan.json, sha256: 9ef77567eb1dac62adca01a351888fac1cc765cd983570889158ab0529903303}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-cli.py.txt, sha256: cbb5a32c1c315d43fc89c9e04a37f9f4a03a83e12d5cbe7799052b333b877e97}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-final.json, sha256: cae8a02f446eee6fdad00cc9dcec398e2328e4b4624ea9265aea554cc9f2f1d1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-final.txt, sha256: 6afc724c468e440023513de647795de1a6eee6d6e7ffd31a3006d786390a70ff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-pins-repaired.json, sha256: afebad7b2ac73fb1f0317b294bf577a6020a7c9e23f073b5f00b95dd3b4d2b31}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-pins-repaired.txt, sha256: d52078dbd902d59e4f0a1bcbfe67d27b4df11ec5df7129c0607398013a5e7ca8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-pins.json, sha256: 3def549d180b77e7135778f65a64adcd8e11b5b6339771fa5b99fdc0428f4581}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-handler-pins.txt, sha256: 3dd7a7b139aad97a5a0080ad72bec080484ab5bf98133629afb10fd068152d98}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-instrument-repaired.json, sha256: b342f81de3fbf091789e82d2083abf4b73066d9950c4cf5d2236f5b7036068ca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-instrument-repaired.txt, sha256: 21d254a42b0ce482473b21e8d0a563c121372977a1fccbacfa72898343b489e6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-phase2-instrument-red.txt, sha256: 5548c85cab0978b65093caef3b26f971f3f0d68dcb651608270870d9ac61e4e6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/predecessor-signatures.json, sha256: 818a1b03bb3f869f68db8b39e5ce819c2683caf4024b6222141430565431f8fe}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/provider-review-authorization.json, sha256: 9f639868009832795cc507e8ba94580f4e2714713c36d106b7a1f7e7259c9b65}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/provider-review-refusal.json, sha256: b00d9d59c70533ab71396eb46bad8f8f6e2f11f0ead48a3bafea14cea6dbe5bd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/record-controls.json, sha256: ca20b542d8a7a2c89499fae239bf9eaed7cec44a7707e9865c2effbd1a0bac46}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/record-controls.txt, sha256: ff27a8dcc3b3554905b67086aa790e30504bea74343b37570fd43e72a14a9fd5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/remote-ci-after-push.json, sha256: 4af43085dae2de611f3bb7277a76a603dbbfced241d9b97f7c9d2c54dd359960}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/repair-review-prompt.txt, sha256: 6ff8df4c04259f8a44c441549d4f103176e787b3caf4dd63ff530224c5519a4a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/repair-review-run.json, sha256: a3d26f7485b710537704f3924a083307a6e94913146be3379413c146c813c7d5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/repair-source-compare.json, sha256: 11baf22fd1afbcdfcc68aea1b1cfec685341ab4b1eb78f37067129478e4d09d2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/repair-verified-inputs.json, sha256: 8474bef7993a148c6a7fc081de2ffe6bce2ab9660c07939550bfc81e49036a88}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-convergence.json, sha256: 9f55482ba2f5adf2870ec1108474d2e3568aab2c141b845a1daac3449a7796ff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-dispositions.json, sha256: 546646884c6b00df494b83307b5327a42ffd232e59aad6705497147df5af9cf6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-prompt.txt, sha256: e402a9c1af9b88ce0fec86a6ed21c25056242cf8227abb879281bf06ba42060b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-regressions-pre-fix.json, sha256: 7e2cb7588c6f0918e866c62e3447a4d90235e9d3c708cd017e999ece1db2f5a9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-regressions-pre-fix.txt, sha256: a6c51801b80835baad0a07345353bac47e46c930ef0ecd2dbb08aac7ab3e66f7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-compare.json, sha256: 32bf30945ba5e6bbba294a3b5d14871bec3275e21f06865aa52cc3b46615273e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-compare.txt, sha256: 2a86dbc77be648f0034e1edae8bb4ccced329c1d76e004b484e4731ab795dd7f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-controls.json, sha256: b74796e2e858218d853a1acd39005c58f2944a79d240e5340cb8bc188c2fc66b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-controls.txt, sha256: dbb735aadf982c7c693e5270b89225224c01296af3bd86f72dae64936feb7041}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-lint.json, sha256: e00731057719b0aac1878e179655f514efbcfceed7525738b89de55c2c406acd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-lint.txt, sha256: eda995b0a87efe9242c05c45cb86706fcf01625ab9dae9cb9d8bec828ae465b7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-measure.json, sha256: 649841643b4e16fca0567a6f66cbb86c2058c7ef53354703b7c12fe05dd212da}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-measure.txt, sha256: fbde5338cedd6a5833105e6a4b2fa971e6be69f51ca60f63e625880988fcfa6e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-production-unchanged.json, sha256: 0aac3ca1b602f423766106bd60b5ea01ba5562be97d0dc8c0fd30c4d228271c1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-py311.json, sha256: b307cc3b46607d2f0b82dd23728c9b0fb58d85942af83cd39ec381f1fe4bf17a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-py311.txt, sha256: 24e4cf8cab2ada0aed3c04eef3706c9e6dfd5a4715ce1ffee4dd6fd0e5c906af}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-py313.json, sha256: 7f9bc2404078f5dd8aff40da2ef3e7b990ab895631c956478bd70c4e4d8ba621}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-repair-py313.txt, sha256: 9acc714f64dc8a31ad1e0e2314331a56ab4c7da4863eee3422c49f8798df535e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/review-triage-before-fix.json, sha256: 846759a94580cb9843d0b73f3fdb84500d1860d6e4de4369379f2fd97f243d84}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-and-entry.json, sha256: 6298f4290ed3c25bfa65d417f683c6e6f029c3644a82d19b10e41df8fc8ff841}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-and-entry.txt, sha256: db46e1bc7789036c40e892da1eee7403cc15f2c62f0cacf299e7010f1b0bf5d8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-direct-final.json, sha256: b19b6ef8add1fe738680704915718f5e36920e83aa34f69550df1989fde7966d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-direct-final.txt, sha256: 47948b8b3bb427d464aee563e9bc16f1da7efddb218c3bd755c074e82dd59dfd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-entry-repaired.json, sha256: 3a85229a32c03df049b456b2e55a3f2c268a3a52eab1d88e385662dfe0301eb5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-entry-repaired.txt, sha256: ac84900463f0b4ae36fe9f7cc527196f52219c0a1a8673d54bddbf966c303631}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-impact.json, sha256: 82be71c850d47b4c65e1069b85ef5afd99714ab9b5ac930f326d87d8a283161e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-impact.txt, sha256: 8dc852dd2b2c0a84f10855d83b0bf4eccb6289d5429397f267a461e5b7e6a6d3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-initial.json, sha256: e30e7f3e750fe06bc1f74ce9d43f8da47203b5822511049a85bc7544fb451448}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-initial.txt, sha256: 6a5cc38b6db042e12f2b27fe2e9e84d03dc2715249ce6b218f1c97538ec1efeb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-repaired.json, sha256: 87f0f06c576f1fc4e864a77a4b3fcba3ff0ce8370764f3049f005933af8d029f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/routing-repaired.txt, sha256: 695f813aace7f6361c30c1465e6b2aa40f2fb0efbbeaf668ff931d391a0f5c67}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/source-commit.json, sha256: 683de0a442f2ad892ee60797c547ed1a2f131e76ee34c85c093846ef8329e147}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/source-compare.json, sha256: 30b6454adb8280e84aeaeba26c274e6bc6e46a93fca57a63a279eb729023150f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5/verified-inputs.json, sha256: 44d7dc1a0315455bb9bb20f4eb907813762bd9016ed7d75f38920edab50dcb0a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF5-final-budget.json, sha256: 7d615a97a94d96969d624c2cfc2301bed0fb35562fc1804fa96f4ca9accf17a4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF5-base.json, sha256: c59598e87a84e84a21d050672feb3eb876e7168ee8d476ef1b39d5ee94b3f1de}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF5-final.json, sha256: fac31b3603179877e828121530882191aee95ce0cfaf2e1d5eb2dec883239290}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF5-move.json, sha256: e4c352419d8826519c6c7956dec78f3c3ace10d8fdc654dc143c6e3e00100636}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF5-repair.json, sha256: 1eb2a4054629aadb9c798c46f8ac443784a3250ee1d05003b06fd17d4441516a}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-amendments.json, sha256: 9a4cd9616a06cfe6eb346b05d90a38c3e50ffa52eefd00c92cf181aa2ff956bc}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-approval.json, sha256: 5df0c70c69d013ee3dfa93b829fbe42e15ffc470cd3682f11b697fa3de04ca18}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-codex-repair-review.md, sha256: bd81d55bb05610dcb6848799ac8e8e5a3fee0bf6f6107b462bfcb9d616546b07}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-codex-review.md, sha256: ca4380cba2897c9ae6e016c2ed2b8f2dedb793fdf60fa11cd5857754187c7e51}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-pending-review.md, sha256: 26a7762ee9b2fa41998cb6fab1e7d03c308cb58cf6bae930763167e1f903cc18}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF5-spec.md, sha256: a7228b3d112eda496173cb530936deb5cdbe2fc6f2183ee9dd47957f8517568d}
  - {path: .gnd-planning/milestones/public-launch/migration/b3-files.json, sha256: b72b4c3e14a1965d1bf7bad5574627d2711af180453cda5a4cbe294fec02d056}
---

# RF5 -- CLI command groups

The CLI now registers commands through 18 groups, parses once and invokes the selected handler. cli.py is 667 lines versus 9056 at the phase base and approved 1500 / milestone 2500 ceilings. The 134 historical definitions/constants are aliases; 116 algorithms remain AST-identical. All predecessor imported names remain. Source controls and patch lookups move with their definitions.

## What shipped

Argument classes/converters live in commands._arguments; shared output algorithms live in commands._output. Checking presentation, lifecycle, solve and optional-export wrappers keep exact old adapters. Offline handlers for verification, synthesis, measurement, extraction, generation, conformance, recovery, evolution, document/fidelity checking, review and experiment lifecycle have domain-service homes. commands.exp retains the unchanged live experiment invocation and its exclusive closure by A3 so generation's deterministic import boundary stays offline. No algorithm is rewritten to fit the graph.

All 18 groups expose add_parsers(subparsers, *, command=None) and handle(args, parsers). Per-command calls preserve all 25 top-level registration positions and 52 parser paths. Root defaults propagate to parsed Namespaces; original 43 leaf argv cases explicitly check effective handlers. No new command, flag, schema, version or refusal is introduced. CLI historical helper imports remain for compatibility; their retirement is RF-D5.

The RF0 architecture tool now measures entry-point imports under an explicit policy: the bootstrap plus 18 groups, 13 exact service targets, helpers/exits, and 44 exact reasoned source/target exception pairs. Exceptions cover retained import bindings or original thin presentation, optional adapter, solve/lifecycle and declared-live command boundaries; no wildcard exemption. Injected forbidden mapped imports, omitted/extra groups, and a CLI masquerading as a service are rejected. All 213 modules are mapped; all 6 layers remain clean, wrong-way 0, allowances 0. Only the named RF8 session SCC remains.

Private import sites rise 124→319. CLI sites rise 18→125 because moved private names acquire cross-module compatibility aliases; relocated command/service closures add further measured coupling. RF5 does not claim a private-import reduction. This cost stays visible rather than being hidden through assignment-style imports.

## Criteria and standing rules

RF5-C1:667≤1500<2500<9056, with an over-ceiling countercheck. RF5-C2: nonempty measured entry-point rule and seeded forbidden-import/scope controls. SM1:392 RF1 pins,43 pre-move byte observations/43 effective disabling controls. SM2:134 same-object aliases,116 unchanged ASTs, original imported bindings and class pickle identity. SM3: complete defining-source scope, omitted-home rejection, current global patches and semantic producer ownership normalization. SM4:213 mapped modules,6 clean layers, no allowances.

RF-R1/R2 preserve observed output/exit and algorithms; RF-R3 successor pins frozen on 29915d9 before source moves; RF-R4 aliases/patches/source scans travel atomically with definitions; RF-R5 names retained without retirement; RF-R6 whole-file guard scope widened with refusal controls; RF-R7 authority files unchanged, no attestation inferred; RF-R8 prior certificates unavailable for current bytes; RF-R9 pre-approved finite budgets with original predecessor drift retained; RF-R10 no feature/tightening; RF-R11 named affected-consumer selection, no broad replay. Standing totality/caps/order/cost/refusal properties retain predecessor bodies and focused hostile/negative controls. Review reproductions, triage and convergence follow the selected skill.

## Verification selection

G0 predecessor: 340 pass; frozen successor pre-pin: 86 pass, before any production move. G1: all six frozen RF1 files: 392 pass and 29 affected original mutants killed with green control. G2: direct 263 checks, successor 86 checks, layering/tool 73 checks: 422 pass before review. After four reproduced regressions were added, the repaired selection is 426 pass. G3: the 24 harvested consumer files plus helper's corpus consumer and focused construction guards:1120 pass. G4: Python 3.11/3.13 each 546 pass over direct/successor/CLI/helper selection. G5: scaffold/contributor/credential/offline 97 pass / 1 deselected, plus explicit changed-path Ruff exit 0. Counts overlap; they are not a combined acceptance universe.

All 434 frozen input hashes remain unchanged. The original pending draft misstated G2 sub-counts as 261 direct and 75 layering/tool; collection-only evidence measures 263 direct and 73 layering/tool. Its combined 422 test result was correct; the collection count is not an execution verdict. Successor 43 case/answer bytes remain frozen. All 167 original mutation rows retain ID/stimulus/expected-red meanings;28 source file paths alone are retargeted. Original broad/census/evidence/proof/native/distribution lanes remain on explicit-owner or separately selected CI cadence. Changed old certificates and release identity claims remain unavailable; frozen unchanged inputs alone may be inherited.

## Implementation findings and refuted premises

The promised RF0 entry-point predicate did not exist; layering was a different test. RF5 supplies an executable scoped rule with per-command service bindings and leaves normative plan repair to milestone close. Two consecutive prior original-budget misses triggered an explicit delegated pre-phase re-plan, retaining RF3/RF4 misses and their arithmetic.

The initial successor pin instrument targeted non-called export functions, invalid exp/lifecycle argv and an invalid scalar judgment stub. A1 corrected these before moving production, retaining original instrument data/results. A2 corrected the exact closure census to116 definitions / 18 constants. Initial over-bundled imports introduced wrong-way solve edges; filtered closure imports corrected those without algorithm edits. Moved class __module__ preservation means inspect.getsource(class) cannot locate its body through cli.py on Python 3.14; identity/pickle remain historical and algorithm/source tests read the actual defining file. No selected consumer required class-source introspection.

Initial moved-impact gate: 6 failed / 1105 passed: two offline-generation placement defects corrected by A3, one successor lookup intercepted by its own hostile-import guard corrected by resolving already-loaded modules, and three pre-existing phase2instrument defects. The three invalid extension-module patches reproduce from a frozen 29915d9 git archive before correction; retarget only to extension_core, unchanged fixtures/production. Repaired controls pass.

Parser-local solve labels were initially left in the preceding registration block and caused collection refusal. Move labels with their consumer. A new handler-default test incorrectly inspected a child's local get_default rather than inherited Namespace values; frozen observations were already green, and the corrected control parses all43 original argv. Lint autofix removed four compatibility imports after a misplaced multiline suppression; the unchanged predecessor-binding test caught the loss, and exact imports with line-local dispositions restore it. A4 normalizes only successor doctor's interpreter directory for portable runs; no answer or original RF1 normalizer change. All red histories remain retained.

## Independent review and convergence

One reviewer is one reviewer. The initial review of 29915d9..d8dd49d found two hardening defects in the phase-owned entry verification instrument and no reproduced production behavior regression. Both were reproduced before belief as four specific failing regressions, triaged before fixing, then repaired under delegated A5. Exact per-command service bindings replace global service permission; unused exceptions are refused; measurement can no longer skip the rule when commands.checking disappears. The stale exp-to-solve exception was removed. Production hashes remain unchanged.

The one permitted repair re-review of d8dd49d..6a57d4e reports no new reproduced findings. Its bounded checks confirm 213 mapped modules, 19 entry modules, 25 service binding pairs and 44 exception pairs matching actual edges, zero violations/wrong-way imports, rejected verify-to-synth and stale-exception injections, and missing-group refusal with policy present and absent. It inspected retained 426/267/267 green gate evidence and verified 36 unchanged selected production hashes; it did not rerun pytest, native/provider behavior, installed artifacts, certification or CI. Initial findings remain verbatim with declared path sanitization. The same-seat count is 2→0; final self-inflicted ratio is undefined for 0/0; the two-review limit is exhausted, with no third round.

Branch-table self-audit: 134 historical names and 116 algorithms are covered; all 52 parser paths and 43 original leaf observations have matching controls; the original corpus is unchanged; wrong-lane service permission, unused exception permission, omitted and extra groups, missing policy, missing checking marker, forbidden CLI/checker imports and over-ceiling input have falsifiable cases. Source scans include all 34 introduced production modules plus the bootstrap and reject omissions. The final direct sub-count is measured 263 rather than the pending draft's 261 estimate; combined 422 pre-repair and 426 post-repair outputs stand as executed. Declared broad/native/certification exclusions remain limits, not hidden missing acceptance claims.


## Refactoring review

What did this phase reveal about existing structure that should change? Refactors EXECUTED: one command-registration/dispatch home per group; separate argument/output infrastructure; exact domain-owned handler closures; preserve explicit live invocation at its command boundary; complete source/lookup observers travel with ownership. The same frozen/direct/affected-consumer gates cover them. Renaming/retiring private compatibility handlers is deferred to RF-D5 rather than changing names during a move.

## Boundary -- what this phase does NOT establish

No new commands/flags/version/schema/semantics, performance, tightening, merging divergent helpers, broad historical repair, source-owned discharge, installed acceptance, publishing, new certification or native/provider execution beyond the expressly selected required independent review. Old certificates describe old bytes. RF6 model/query/package responsibilities, RF8 session cycle/resume/version meanings, RF7 successor strictness/FIFO/media types remain. Milestone close owns meta-node exemption wording, RF3 SCC scope wording and RF4 visibility-only filesystem/shared-checking wording. Prior source-side control is not a new owner attestation. GitHub's observed billing refusal is infrastructure, no remote acceptance verdict.

The 43 successor observations establish selected accepting/refusal leaves, not every internal branch. AST equality does not prove all behavioral equivalence or imported binding semantics. Class source introspection through historical __module__ is a documented limitation; identity/pickle algorithms remain pinned. Same-seat review is bounded disagreement evidence, not a proof or panel. Portable macOS 3.11/3.13 runs do not establish Linux, installed artifacts or native/provider functionality. Approval marks are delegated agent rulings, not human readings. No source-owned unit is certified or handed off.

## Open questions

RF6 package/query responsibilities, RF7 strictness/safe-filesystem successor questions, RF8 session SCC/resume/version meanings retain named owners. RF1 meta-node exemptions, RF3 SCC scope wording, RF4 filesystem/shared-checking wording and RF5's newly supplied entry predicate are reconciled at milestone close. RF-D5 owns shim/private alias retirement. Source-owned authority/import-walk/helper-tail questions remain source-owned. RF1's original boundary stays standing when its owed RF5 surface observation clause is annotated by this later record.

## Gate output (verbatim)

The complete retained outputs declare path sanitization in their own headers; commands and summary lines below are exact. Initial reds are retained separately and explained above.

### baseline-G0

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_session_pins.py --tb=short -x
    340 passed in 52.89s
    Exit: 0

### predecessor-handler-final

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf5_handler_pins.py --tb=short
    86 passed in 0.57s
    Exit: 0

### G1-frozen

    $ .venv/bin/python -m pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py
    392 passed in 73.04s (0:01:13)
    Exit: 0

### G1-impact-mutations

    $ .venv/bin/python tools/rf1_pins.py mutate --out .gnd-planning/milestones/code-refactoring/evidence/RF5/mutations --jobs 2 --only M-HELP-canonical-json-gnd-cli-canonical-payload M-HELP-canonical-json-gnd-cli-evolve-json-bytes M-HELP-safe-filesystem-gnd-cli-evolve-reject-unsafe-spelling M-CLI-root-prog M-SEM-extract-indent M-test-session-fresh-1 M-test-session-fresh-2 M-test-session-fresh-3 M-test-session-fresh-4 M-test-session-fresh-5 M-test-session-fresh-6 M-test-session-fresh-7 M-test-session-fresh-8 M-test-session-determinism-1 M-test-session-determinism-2 M-test-session-determinism-3 M-test-session-determinism-4 M-test-session-determinism-5 M-test-session-determinism-6 M-test-session-determinism-7 M-test-session-determinism-8 M-test-session-resume-1 M-test-session-resume-2 M-test-session-resume-3 M-test-session-resume-4 M-test-session-resume-5 M-test-session-resume-6 M-test-session-resume-7 M-test-session-resume-8
    rows: 29  killed: 29  not killed: 0
    Exit: 0

### G2-ceiling-control

    $ .venv/bin/python -m pytest -q tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf1_layering.py tests/test_gnd_arch.py
    422 passed in 7.88s
    Exit: 0

### routing-impact

    $ .venv/bin/python -m pytest -q tests/test_codegen_force.py tests/test_codegen_manifest.py tests/test_coverage_cli.py tests/test_exp_bands.py tests/test_exp_spec.py tests/test_extract_cli.py tests/test_install.py tests/test_measure_negative_control.py tests/test_measure_offline.py tests/test_poolfile.py tests/test_public_derivation_evaluation_complete.py tests/test_public_payload_alias_sites.py tests/test_public_registry_runtime.py tests/test_recovery_adversarial.py tests/test_report_json.py tests/test_review_bands.py tests/test_rf1_cli_pins.py tests/test_rf1_session_pins.py tests/test_skeleton_e2e.py tests/test_solve.py tests/test_v63_phase4_helpers.py tests/test_v6_phase3_distribution.py tests/test_verification_fixes.py tests/test_verify_cli.py tests/test_public_corpus_integration.py tests/test_public_construction_site_guards.py
    1120 passed in 121.06s (0:02:01)
    Exit: 0

### G4-py311-repaired

    $ /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py
    546 passed in 20.31s
    Exit: 0

### G4-py313-repaired

    $ /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py
    546 passed in 18.25s
    Exit: 0

### ceiling-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf5_commands.py::test_bootstrap_ceiling_and_single_parse_dispatch
    1 passed in 0.17s
    Exit: 0

### ceiling-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf5_commands.py::test_bootstrap_ceiling_and_single_parse_dispatch
    1 passed in 0.18s
    Exit: 0

### G5-controls

    $ .venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_review_credential_launcher.py tests/test_measure_offline.py
    97 passed, 1 deselected in 16.91s
    Exit: 0

### G5-lint

    $ .venv/bin/ruff check src/gnd/checking_service.py src/gnd/cli.py src/gnd/codegen/service.py src/gnd/commands/__init__.py src/gnd/commands/_arguments.py src/gnd/commands/_output.py src/gnd/commands/checking.py src/gnd/commands/codegen.py src/gnd/commands/conformance.py src/gnd/commands/doccheck.py src/gnd/commands/evolve.py src/gnd/commands/exp.py src/gnd/commands/export.py src/gnd/commands/extract.py src/gnd/commands/fidelity.py src/gnd/commands/judgments.py src/gnd/commands/lifecycle.py src/gnd/commands/measure.py src/gnd/commands/recovery.py src/gnd/commands/review.py src/gnd/commands/solve.py src/gnd/commands/synth.py src/gnd/commands/verify.py src/gnd/commands/witness.py src/gnd/conformance/cli_service.py src/gnd/evolve/cli_service.py src/gnd/exp/cli_service.py src/gnd/export/verification_service.py src/gnd/extract/service.py src/gnd/fidelity/doccheck_service.py src/gnd/fidelity/service.py src/gnd/measure/service.py src/gnd/recovery/service.py src/gnd/review/service.py src/gnd/synth/corpus_service.py src/gnd/synth/service.py tests/public_site_census.py tests/support/rf5_sources.py tests/test_codegen_manifest.py tests/test_coverage_cli.py tests/test_exp_bands.py tests/test_exp_spec.py tests/test_extract_cli.py tests/test_install.py tests/test_measure_offline.py tests/test_poolfile.py tests/test_public_corpus_integration_support.py tests/test_public_derivation_evaluation_complete.py tests/test_public_payload_alias_sites.py tests/test_public_registry_runtime.py tests/test_recovery_adversarial.py tests/test_rf1_session_pins.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_skeleton_e2e.py tests/test_solve.py tests/test_verify_cli.py tools/gnd_arch.py
    All checks passed!
    Exit: 0

### G5-final-lint

    $ .venv/bin/ruff check src/gnd/cli.py tests/support/rf5_sources.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tools/gnd_arch.py
    All checks passed!
    Exit: 0

### record-controls

    $ .venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_review_credential_launcher.py
    47 passed, 1 deselected in 4.40s
    Exit: 0

### review-repair-controls

    $ .venv/bin/python -m pytest -q tests/test_rf5_review_regressions.py tests/test_rf5_commands.py tests/test_rf5_handler_pins.py tests/test_rf1_layering.py tests/test_gnd_arch.py
    426 passed in 12.18s
    Exit: 0

### review-repair-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf5_review_regressions.py tests/test_rf5_commands.py
    267 passed in 7.21s
    Exit: 0

### review-repair-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf5_review_regressions.py tests/test_rf5_commands.py
    267 passed in 6.36s
    Exit: 0

### review-repair-lint

    $ .venv/bin/ruff check tools/gnd_arch.py tests/test_rf5_review_regressions.py
    All checks passed!
    Exit: 0

## Measured budget

Production comparison is bound to source-compare.json (and repair-source-compare.json when applicable); final file/test/document counts and exact limits are bound to RF5-final-budget.json. Original RF3/RF4 misses remain in the pre-phase re-plan and their records. No evidence lines are counted as documentation.
