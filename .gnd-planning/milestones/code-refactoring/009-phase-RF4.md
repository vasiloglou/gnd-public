---
milestone: code-refactoring
station: phase-RF4
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF4
date: 2026-10-05
source_base: 387aada2f5fad7289481bbc2e15c8dba629d8ce0
verified_source_commit: 301e80fb886c7866c9fcfeb5f82671351c1ee35e
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_rf4_review_regressions.py tests/test_public_construction_site_guards.py tests/test_report_json.py tests/test_v61_phase4_projection.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_exact_scope_guards.py tests/test_v62_phase4_assurance.py tests/test_v63_phase2_cache.py --tb=short -x"
  exit: 0
  output: "1126 passed in 46.88s"
  note: "Focused structure, compatibility and affected-consumer controls; additional exact gates follow."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Full default, historical, proof, distribution and native lanes were not selected for this phase."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/006-phase-RF1.md, sha256: 7b79501b17aff3f2296ea9f6e202ab4ece41d97bfb2ba2608604a3128d2cfbb4}
  - {path: .gnd-planning/milestones/code-refactoring/007-phase-RF2.md, sha256: bed4da233f786e2b651135d7d8d01ad11998dd9d831f76a4cb3c350ea8066f6f}
  - {path: .gnd-planning/milestones/code-refactoring/008-phase-RF3.md, sha256: 5d1f4e73277cbefb1fe4ea6a07e8651353271783052520e077b6542d6b8e0c86}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A1-spec.md, sha256: 412bab5a2ff20d9f67a110aab3d6755f16e9dd5e932e5ec6e2c7545d3a0cb767}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A10-spec.md, sha256: c4faca94aaf93696006533de0298c3305e8ba0e150230d68bde9a4ecbd6fac2d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A11-spec.md, sha256: b0a4742e89691ad06aeae0a40f072de5bcf97f53da4789cbcc5bbe05eee042a8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A2-spec.md, sha256: daebbc75134e8c665dc2ee74ce79aa5019f1abf3d8835b0e484991757149207b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A3-spec.md, sha256: 5b0466cd769a52c003a478f40f34ab83f58585e308d60d6a58dd475ec551b2fa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A4-spec.md, sha256: 90a2e871200b586c9c9978c252e6bdd84e6dc966e76a90ef5fc6db56c54668e5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A5-spec.md, sha256: 275f524a766be5a1d98eb23856a47dd9747d606cb2919b6951f5e0abc6303551}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A6-spec.md, sha256: 83a3359217660704a1ced710f32cce337d0ebecd32bda5ccfb2dfb54f2454a9e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A7-spec.md, sha256: 58b8fe9b7a41b62d8f368d82815536b93251372b3857e809dd6e9e9ae40413bf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A8-spec.md, sha256: 744861e9d2e90a3086801c8ca314a8b454bd032e51cec66c6671898fc52bf42b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/A9-spec.md, sha256: 6cd67560a813f86a7093fb04863397a8ccc00fdad88c7309007d40fa56cff092}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/approved-spec.md, sha256: 326792938270a28b64eb418499a4199d0fd7006bf84648e417506097b2c8afa9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/base-surfaces.json, sha256: 78aca3ba85cf536d4c3cd07aae372830522640004991d112c01c9153d61bb68e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/baseline-G1-unsandboxed.json, sha256: 03c06ecb6c6c2712cd6ac8290ce74e2c76e8c02c117cbb7ac8ab8a6e9ae2ca28}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/baseline-G1-unsandboxed.txt, sha256: 9833cfb055a1809877f73279f24ee2d826ba09da6417b708eccafce50349002d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/baseline-G1.json, sha256: 51df1d21cf2d5067fb758a259e69dd777aec94f09084475f9fb00a5706d18380}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/baseline-G1.txt, sha256: 2aa073018cfedc9d08a72116580a8761f785652b428d86a20b9f63d06deb03b5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/cache-stimuli-pre-fix.json, sha256: cfcd592e70680809f2259023ce52348a2a7a289ef496840105008fdbb129e6a8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/cache-stimuli-pre-fix.txt, sha256: 7fdc43ab76ef0062fbb2286551612a091356e46896382bf0997af2153c963219}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/census-base-reproduction.json, sha256: 31952f038d558a535448bb0065f494ff7bd77d639ec6bd1cf1b67a8cd1b09cba}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/census-base-reproduction.txt, sha256: 8749b4d18243cbb097edb49d89c27c8a6b2878d12ac69957dfc1a0e0f04d1a2f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/census-base-root.txt, sha256: 31bac1f22755f339d425dd98415f23724f7fc6b7760af7a29a4ffebeafbc4f48}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/ci-status.json, sha256: 67132133b7b71c8072ce6fd1a53c46f44c8e01b8a84a2dcca6b562ccef7e259d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/construction-site-pre-fix.json, sha256: 9f37b2168edacfe7ef6756d97e248e49edcae4dce55c86cba420a718da7649b7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/construction-site-pre-fix.txt, sha256: 93904976642ab396d0e95cc9b9de18bd3305165b660964f3328ca704556e7b13}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/final-commit-compare.json, sha256: 5278cab1c71612b2f1b3ec3bf57f548deccaec56dbf0c2ee2c161a02f6b7aef9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/final-lint.json, sha256: fd3d354480b7e37034c8478f70cf482b999bd6e2e60b308d82823baac7299071}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/final-lint.txt, sha256: eeb2321df1a300af712c1863578efdb379e947aef553b77646b4926e992090b9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/final-lint2.json, sha256: 3136973c02259227290cb5ce9233781a62f71941e5cbc63b29bb26cb63112558}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/final-lint2.txt, sha256: 1b492c34cfd43d1e889aa278fef0b44f057a7179796d17212580e4a0b84c59b5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/frozen-inputs.json, sha256: b16ed7ff63235b539a961a13f3bf57b32ca4caa8b86924d6cd451ae00500c63a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/legacy-lint-dispositions.json, sha256: bd255cbaf3e41d9f0613ef2715f133d92dc38d9c4b757fb7cffff15d63fd4c64}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/manifest-adaptation.json, sha256: 98675502f096914ffc0d2fa9ecc32da0b4bc50a24158cd4acb160a897d178f6b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-G1.json, sha256: b64855489f36f0728601f0dd0e87c5446a279b368f339d3e8d3e647b21b5afd9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-G1.txt, sha256: eb72b7e09686da458b5d55c73fb8655e2464a0c675a05e29782d20cf8c808b85}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-budget.json, sha256: dd60d9103251f677ed67905bc17e6d8183e7f87792b6a7d6ea5b354949e377d8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure-repaired.json, sha256: bb843b19da8ef81412a33bec5ab3ce1488d6b38ba07672bf9f4bf44994a19fb5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure-repaired.txt, sha256: 58dfc7bf8b3cb741f525996d909dea6e302592dc56c40d1fdb0afb3ba7ef78c8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure-repaired2.json, sha256: 8504920f3304b2434eba081be2eb6d2473a260e9351f524f08fd3415aff85a46}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure-repaired2.txt, sha256: 846a5cd0df2af446649bf68eaf3483788c8c4e66afecf98a02063faab32acb48}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure.json, sha256: 36efa0b7060a3e50bc838ebd170b8ad861eb59d6fe27b44d8da8b8a9ee34062d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-closure.txt, sha256: 8a06879067d3a100706ca19d43c160f9ae9fd7404a06641d293f3e3a1cc6cf9c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-fast-final.json, sha256: f698b6c7e6f4ea51738deaf698c52763477c5b6f9d1d058339278520db729d01}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-fast-final.txt, sha256: 4129ba35925a55cd362564e64a2a5d5ea5165a94da265ff104dfe47098891966}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-fast.json, sha256: 8360acbda17f06c035dc6aa22f8e76bf40f4895399d167620f709d9f526e1d96}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-fast.txt, sha256: 148665dd76a2700418e50b6798a051d17e11b6b3c0fe6e4fb6444391a0962a67}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-after-imports.json, sha256: 0c1658eb0b04999cf156d12b02cebdfc7eb4700e67e7d114c57d08dcaaeca826}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-after-imports.txt, sha256: 9c61587120a833652c0f0d13eff226d0fefbd0b776c3e30ed8e0ca354fb6aaeb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-clean.json, sha256: 7710f70eb65751c02aafaf7d469ca51dd3e3a2d101b933bdf9683d59a6f8eb7f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-clean.txt, sha256: 97534b0c2b27ef119779e06257efdec43faf52e73d610057da435d87991587b7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-final.json, sha256: 3408d1ae11a32c6ba99b7da84a26faca7122353e58f837acb0708a3c7d8931f3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities-final.txt, sha256: 0cd63bc6d006e25ed77066326da7d5b6cb91939f78a10c86b5cf07102708783d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities.json, sha256: abb4a8f37634ca3d281fa3191f9deaad1c59ed3301beabf2952198e488c9807a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-identities.txt, sha256: 828c60b59866c08d075fe36e44181708b1d5413716495585400c7747a7310296}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact.json, sha256: efe459e251128c784d6049a99fad60ef69b13bd83610e98de0d45e2edb8d3bfa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact.txt, sha256: 2bd70078ba89219725e33d1514c24cb784e970fd92cce24adee31264f11d654f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact2.json, sha256: 7baaf30178fd3270878e779c72e24e3552463d4a8a3272e382bbb65f39e58d04}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact2.txt, sha256: fec1763721ab20a5a69410a719afb272c31d9a68af8081c213bb2c21cdbc329e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact3.json, sha256: 298711d0a74f77a195a395413498615733dad9b4bf9519ad8b0bbebc11bad602}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact3.txt, sha256: a9220c69e76867615d424ffc07f787666c252683119f1142efd9e0f06a475469}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact4.json, sha256: 4ff2aa78203b6c72e9a5f2e0fafda7108b2c9beae5fed4c00c009be23d77498b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-impact4.txt, sha256: 602347c0ccf9575cee99c4c16ff6d1784a25aaf9d5691da63e443d875b3d6d6d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-imported-compat.json, sha256: e01c53078c20974815cf28ac54486dfe2ac86c783d41d2a4a87ce571cc8febbd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-imported-compat.txt, sha256: b3a881fc479d015d516c6e817d58b1f3d78c264f22a4c61de26183ab6017f745}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-imported-compat2.json, sha256: 575bae5422ad08067b29b36d35b183ff205ff334b19ecc11e39bffdec440d22c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-imported-compat2.txt, sha256: 995bb30f73320f95334bbb1f881259697158df5bc954e373ba39c0fd98f8991d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-late-consumers.json, sha256: 22371d14b47ccd5879eadc2e4d36d8078ea3b8e62d430f3c3c845c2d66ee9333}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-late-consumers.txt, sha256: bba37b4dc5a78382be37930f8812dfa7ea953341d92d48fe4fabc134faf4f62e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-small.json, sha256: cae01e708da24d62e1bf8ff0d366ce1607d65742e5c9e7b2863dc90d43a5f5cb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/move-small.txt, sha256: 5e18e802bc73dcbef1cbbbd24a6f2a1be3d29c7501be619b49b0ea7b7b3e2ff0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-G1-final.json, sha256: 1e2e2cd2babd0996dbd59b4699a26e2753b2e18eba370b04e7f2e5de44430255}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-G1-final.txt, sha256: f9b603dc7723cc761c8ebe38966febfaf6f72e199cd7ad976dc9011f35a41bef}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-final-G1-and-impact.json, sha256: 06e1e075b96f26eb757432f8986c0377e45aef77829c758321259ee4ca45eca7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-final-G1-and-impact.txt, sha256: f1475b4118394bfbb40be6f9e4565b6da83254407894995d610d1b33861d3fce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-impact-final.json, sha256: c6b3ebd859995cb5ede6f4a7886addf2a7263c14d6dd38dd5fd664faaee691f4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-impact-final.txt, sha256: 8940371972aa7fcac7c8aacb7ae73d81d6c8f5cfc0ead42b0a2b49298e54a7ed}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-late-impact-repaired.json, sha256: abb9e95ee9198990013ed9f2f5c1fee44e0abd3e2dbdade715540e462006bf54}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-late-impact-repaired.txt, sha256: 5321d3995bb7d228f0faf10d2e4cbf08d4686cec6e71ad000937297d4515df32}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-late-impact.json, sha256: 7a0635ecd32ab68f45ee4a72ceef279d44484a79e79ede7fb4c6969d8c64a9df}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-late-impact.txt, sha256: 281f1ce99b65c45ad50a66852df645bf61211f6d4263f44a62d0e8fb694969ac}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-service-controls.json, sha256: 0d4116a790d4547eba63369ef881d2855cc502b2e1bf44feeaf6c29f6654cde5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-service-controls.txt, sha256: ac901becfe7827906d6dc31c85ba5c0ebe0a61102a70f36158e8815131f80778}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-session-patch.json, sha256: 97ea240dfbeb082c7e222082afdc81c82d85a58a675e393821053457f091a444}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moved-session-patch.txt, sha256: 9b963665d450e80f32dc610119733408ecbfdac67f2de2b005a99b8f34ba0329}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/moves.json, sha256: 0d5f684e13e6b1bd2aae78facbd04219850996568f8e7ec6b3bee95097c4f12a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/mutation-controls.json, sha256: 1d418851d29af0b9841d61303d18c0187adfc02c3d7e88d380c3f085099ac580}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/mutation-controls.txt, sha256: 6c7c4697ed7917e64509ec3e630614d8495362d215f58ca694971ab4da57aaa3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/mutation-retargets.json, sha256: fca35ad8afbf0789dcb94e5d0244662bcee638938326d6fbb5db30dc2fc72f7d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/mutations/control.txt, sha256: 950ed1aee518454a48544beeda15d0187f75870eb4b610d0677d96423176313b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/mutations/mutation-report.json, sha256: 616a145a4af118ae56d8db87c4939ec60ddc193adb35270d559ef99d9505de11}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/patch-inventory.json, sha256: fde146caa831628b5402a164b6d3ee004aab9323216d1dadd0eefd0edcb0c87b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/portable-py311.json, sha256: 86ee6e276d61ffdf5c073e2c9e9c62a4c53ccc1ebc3a80ac6417fb0bff838f61}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/portable-py311.txt, sha256: 0ca096d36579604289619740c8ebe8a25af767f3db830cf035838f1713e9b851}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/portable-py313.json, sha256: 1ec5947d32b069ce753edd721667f703f3a3bace2d7cbbe72c0a67daa7c0740d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/portable-py313.txt, sha256: d4c3aac278367e65b1e859f139b043bd5a227823e762fa98be04afb5864de368}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-move-live.json, sha256: d1e918a801bff2067b6b7bac7192114981e931df9f1d83c579a441a1d43f3efd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-move-live.txt, sha256: 0e22248c1ef1841c39127666446ee99d6bed5d47c4157689cb0ae138cb788784}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-move.json, sha256: 07b4f4e03a583fc35597e249cbb1adfc638c2cf7d3b59f87b099e5dda1743fae}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-move.txt, sha256: f49e3737e8a8ca64638f6c0b0221244fb28084f5890a79395b1db47320d6e766}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-service-unsandboxed.json, sha256: 693aecbe8e0fd1a2348150d04450969e63a1b278e3146eac0edcf8844af67ff2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-service-unsandboxed.txt, sha256: 68c1853060e9959be0e09e1358c227178596bc98b3115a94965f8421312a2bb6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-service.json, sha256: 5bf674ea617e7419f8a602bf9d0513ee246136f500850b1c0fbede40e02cfb08}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/pre-service.txt, sha256: 2476650a508d77b9d57ff4a84c96ee889467d6244989e2ece724fe3b4196f276}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/producer-patch-post-fix.json, sha256: 629c7355fd8a952923768aecb16dad29cab6337c4a0c88a70aee049badfb01c3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/producer-patch-post-fix.txt, sha256: fe445894b3616f882f09d657d9e7d670994cd353d4e6758c5daef20da9d5ae1d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/producer-patch-pre-fix.json, sha256: 7e039b0166fec82a28dd88c5e0c8c8ce8eb576fef27ab53974a4563c8cdc229b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/producer-patch-pre-fix.txt, sha256: c78a3eb1b296deed91390ba3269b218f4cef2e25e33393eede18cf69c9dbb12d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-G1-unsandboxed.json, sha256: fffed7c5a6fdbddcbaa46fed8103f7bf831023123888af07d270ca4bed1c1890}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-G1-unsandboxed.txt, sha256: d49df13eb420d50d2d6b56e95d3a45b70a324a1a349e7419b71c150beaaf3d79}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-G1.json, sha256: a2df9dd2bdd782dbc07327da3a73f88850330669591821e537be1f33d63a460d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-G1.txt, sha256: c5f48b994ad049f2a1b9d839d63d976fae54a5fbdb983278272531bfb23cde4f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-commit-compare.json, sha256: 103e69729e67118d91016d62279ebf103b3c7255725d8f0794fe65391a2fc04f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-controls.json, sha256: 16417b5b7ea5b779fdc2e307c884f4d032e1019053f482e5622c2d20c7723ded}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-controls.txt, sha256: 42d24540da69e065f8ab09c1c45476ba97f29fa97832c5131f908a37525a2bdb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-frozen-check.json, sha256: 233c61b58afade188f6cdb4ac12b6ebadf955ae965599d6e414d54fe0ebbaa35}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-lint.json, sha256: 23767d5c7c7790191392143a060c8f625c25cdbcbd86efbabcd4df250967367d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-lint.txt, sha256: 3fc9e37468c0f413773f6d3eb743f7cd4fa70b80d26623123ea5b0a1df4d2530}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-metric-reproducibility.json, sha256: a2b872b03df1de140ca55164139b3fed000d62b796e3ed09dcde8d26c98e7395}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-portable311.json, sha256: 93fabb877f5c3a1305015649f2d8c6549d467ed2a052b4ee0ac53c10bf2633ba}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-portable311.txt, sha256: 50d870586ccef419d8e470880a54d0412feec651e5b9cf278f1ba01cb78fa4cf}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-portable313.json, sha256: 94df651b7492566e14568e8553ca782e1362ecb728299eba8bf260948af54aae}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-portable313.txt, sha256: 1c9b7e64db49e4f4734b92b9b271d9b8a6b4d9d1b03fc860cfa098cd913e3d16}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-scaffold.json, sha256: c0e7f6d4b133d77df102094631a25e7b26ba0bb071f6602ae31acb496e48f173}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/repair-scaffold.txt, sha256: ce8a5de04c5e5cdae967e8abeee5c1494e51175afa98941bd38b714c23f6f94b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/restored-identities.json, sha256: ada56a35751861fe985dea36c2978578e5a9a1eb0bb592cd8300c258cf02ef04}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/restored-identities.txt, sha256: 4d982ad0e3c8b536a0a7118ddcb20c026b6882559e474a5fd2b72fb3e5ff13ca}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/retained-imports.json, sha256: 5aa049ba6652a294b49a0f04f4c28065f8e8086a3609f6051d63fc3355f5185e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-authorization-status.json, sha256: 5e4b221440fa04d6971c17a29f52b29f7acb5f828ab7199c50253c39306056f2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-convergence.json, sha256: 19c605bda968e0e45f4309919e55cf710e9e4d3ef1805a51253f311d4ef57979}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-guards-pre-fix.json, sha256: 8dd9aad5fdd9fd8f892d354f6fc71cbe3ca24fd364edca49a842ff0f595d50e2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-guards-pre-fix.txt, sha256: d6564f46110b3f83af7361da707d408b607fa8e68c8ed5cb99c721d527cc0dd8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-missing-imports-pre-fix.json, sha256: 8145a2258a143b9995490428642353fbd0b511b6e0e4e7ee4b4fca46610547f7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-regressions-post-fix.json, sha256: 97575edc4515777f07fe6c2fa044c178f56668e8448de3133dd44bbca8b81700}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-regressions-post-fix.txt, sha256: cd33d5fdb46690a3f28ac4a5c762a86d9d3f5dca69228827fd4162aea317a92a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-regressions-pre-fix.json, sha256: 5e13e909ad9963a20474a0f5f5f97c35859a7616ec6a2f283b06d189aab4f6da}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/review-regressions-pre-fix.txt, sha256: c4d973a9cf3bd2c4c596f2e968337dc12baf868a4bd3d00f6cc8fb9ae01bb2af}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-controls-final.json, sha256: c1e72d0d28769f3ad6e13d02f7d8d5a4a8733da149e37c1962594300b60a3eff}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-controls-final.txt, sha256: 40b1e29be6521a5b3ef5212fb655e49d66b3c6c48c5063ac7407b61aae5777d9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-controls-repaired.json, sha256: 6ed4d5b8d4e8650154261dfe3b2be017af0d582fb6b8c75789e927d61c7de458}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-controls-repaired.txt, sha256: 6339396a19319498a40553d85b641a2883fc4d78481c0636093cfda56bac4892}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-direct.json, sha256: 83ebd64e67c53bd8eda24e660932de0bcc7c3cc534fac926cd254ff0c057ce61}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-direct.txt, sha256: 3fc5604db5123b4776aa0dd47d6a3d62b34d4ddafbca037e70708962280482ac}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-final-G1.json, sha256: 376f619c230803621ae0e07a616b109b5a45d3aecaffcad6532208e701328db6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-final-G1.txt, sha256: 2929c7b82e3a0adb6c7afa93c4d46033a5328ddf64fb4b660ca095e56eea0ad3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-scaffold-repaired.json, sha256: dac89fa2fc331c6cf41d6fcd12740b39adef2b8223f145909cc2d72b25af1d2e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-scaffold-repaired.txt, sha256: 46084440b8425466f9d5cc618ecfa1961e59521cd3a3c0d4d63e707daf8f0031}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-scaffold.json, sha256: c48521de2c5da6e79c6eafe1dfccb2822179239e8c5d378f0b0165767eceaa0e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/routed-scaffold.txt, sha256: 3f788001bebc8fea5179d447a4b086ccbc9043b8887c7999306cfd20ac3f1268}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/scaffold-base-reproduction.json, sha256: 315b42dabcbe4702b303f313d06d70bf15355322cbc4639cab5b5f8c3ef3d85b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/scaffold-base-reproduction.txt, sha256: 42246d03fee097a4eaf4551eb65ca3e5956ec6c77397cc102928778e4374ac6c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/test-retargets.json, sha256: c703117814461fa0239f5573ef8c2c8216d18fa65ad932a18a607efb8e3acf97}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4/verified-inputs.json, sha256: 077809a742920862bd967e9e50008c9867e5c816f5a2b0d2dca97436333e376f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF4-final-budget.json, sha256: 637f02ee97932cd03b3a36f644e4c4fdc6ee6262f5194814383c3f0f1a686103}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF4-base.json, sha256: 194f1a285527447641aabfce8544ba6c8233cff7399ef703c99eb81d4cfd7b8e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF4-head.json, sha256: 85698d13af8c79524d945bb0873a25efe387de50706faff9f63fae6338bb38b6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF4-move.json, sha256: c350d2a5ac7ee2fe1b3b1c35dcd24d1b10f7ce02f200f8495a4c7a48830de240}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF4-public-move.json, sha256: cb43ee74c579bcc54ee8e04e111261df7e4627ffa726ae150b6c99e913ab0fd5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF4-repair.json, sha256: c59598e87a84e84a21d050672feb3eb876e7168ee8d476ef1b39d5ee94b3f1de}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-amendments.json, sha256: c4059737649422978a81666a68658e1e38d3406ba201be85c928ede85073a7b4}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-approval.json, sha256: 23b1ee1be4aceb22022f0177418249140acf4e0e0a4cd97b996d4349fef6e3e6}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-codex-prompt.txt, sha256: 50be96031ba50ba247f0a38ecc0860310d696a83e59f2ffe91f743f950524802}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-codex-repair-prompt.txt, sha256: 35cc3bab8e09af0181bec258258c20d0bf01d56401a743d2bf3974500bd59ccb}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-codex-repair-review.md, sha256: 0aa57f70afaddac388025052ce271be44c5f9c848b42e178dd17ec9c28725594}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-codex-review.md, sha256: 1a0dc8931e39617e55d66e1d6e8ab343294b7e978a8cd28a8d25c2e37c9260f1}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-pending-review.md, sha256: 360d0c67f44c3772b54c02ec0d95c44296155c8303092de613cda6cad116e7aa}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-review-triage.md, sha256: eefb3485242e32da03963454cf5a845cbfbdffcf3f195c009fc0d8efa3d0e852}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF4-spec.md, sha256: b0a4742e89691ad06aeae0a40f072de5bcf97f53da4789cbcc5bbe05eee042a8}
  - {path: .gnd-planning/milestones/public-launch/migration/b3-files.json, sha256: f6ee1c8e7eda63e788fa971328b71e06cbbe14bfc811a445c21ef482485ef6b1}
---

# RF4 -- Peripheral layering

## What shipped

The installer filesystem closure moved to safefs; process and agents separate bounded execution from adapter policy. The assurance package shares wire capability and identity below core, inheritance, claims, evidence and transport. The synth oracle separates constructive and expected-state calculations from mutations; the47 boundary imports use public names. Report payloads and export/witness service wrappers moved below entry points. Checking_service preserves the original checking/admission/report pipeline, and diff supplies checker.check_partial without importing API. Old moved names and imported compatibility bindings remain identical objects, including twenty additional predecessor imports restored after review.

Three RF4 cycles disappear; the RF8 session cycle remains. All179 modules are mapped, every layer is tested, and wrong-way, lane-to-install and original private boundary-to-mutate edges are zero. Private imports198→124. No allowance was added. The agent cycle was already refuted atRF0.

The filesystem decision deliberately retains artifact and domain/nested bodies at their canonical homes. Safefs exposes artifact algorithms via public aliases; this phase does not claim all16 filesystem variants physically relocated. They remain distinct. The source-base nested artifact directoryidentity refusal pin and its live disabling control discharge RF1's owed pin.

## Criteria

| Criterion | Current evidence |
|---|---|
| SM1 |392 frozen pins pass;434 original input files byte-identical;45 adapted mutants killed at unchanged failure nodes |
| SM2 |479 old/new catalogued name identities plus20 original import-object identities and unchanged moved algorithms; actual adapter, filesystem, mint and report patch controls |
| SM3 |Actual provider scan records visitation of all17new modules; assurance identity stimuli visit core.py and construction-site static/runtime guards visit payloads.py while retaining original registry owner strings |
| SM4 |Complete map, all6layers, no xfail/allowance; clean-before-dirty graph and import-binding negative controls |
| RF4-C1 |All3 confirmedRF4SCCs absent, new package homes included; onlyRF8session SCC remains |
| RF4-C2 |Lane-to-install runtime/type-only edges0 |
| RF4-C3 |Original47private sites replaced with publicoracle imports |
| RF4-C4 |All6map layers covered, wrong-way0, allowance0 |

Plan §9 row: “SM1–SM4; confirmed SCCs removed; lane-to-install edge rule; layering test over every layer”.

## Selected gate output (verbatim)

### routed-final-G1

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py --tb=short
    392 passed in 62.22s (0:01:02)
    Exit: 0

### routed-controls-final

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_report_json.py tests/test_v61_phase4_projection.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_exact_scope_guards.py tests/test_v62_phase4_assurance.py tests/test_v63_phase2_cache.py --tb=short -x
    1092 passed in 39.00s
    Exit: 0

### routed-scaffold-repaired

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_review_credential_launcher.py tests/test_measure_offline.py --tb=short -x
    97 passed, 1 deselected in 13.42s
    Exit: 0

### portable-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_v6_phase6_execution.py tests/test_v6_phase6_runtime_identity.py --tb=short -x
    1178 passed in 49.01s
    Exit: 0

### portable-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_v6_phase6_execution.py tests/test_v6_phase6_runtime_identity.py --tb=short -x
    1178 passed in 43.81s
    Exit: 0

### producer-patch-post-fix

    $ .venv/bin/python -m pytest -q tests/test_v6_phase6_execution.py tests/test_v6_phase6_runtime_identity.py tests/test_public_assurance_feedback.py tests/test_public_assurance_feedback_surfaces.py --tb=short
    26 passed in 0.43s
    Exit: 0

### mutation-controls

    $ .venv/bin/python tools/rf1_pins.py mutate --out .gnd-planning/milestones/code-refactoring/evidence/RF4/mutations --jobs 2 --only M-HELP-canonical-json-gnd-assurance-sorted-set M-HELP-canonical-json-gnd-assurance-inheritance-canonical M-HELP-identical-candidate-gnd-synth-assemble-object-types-by-id M-HELP-identical-candidate-gnd-synth-assemble-role-object M-HELP-safe-filesystem-gnd-install-atomic-write M-HELP-safe-filesystem-gnd-install-descend M-HELP-safe-filesystem-gnd-install-descend-create M-HELP-safe-filesystem-gnd-install-reject-unsafe-relpath M-HELP-safe-filesystem-gnd-install-safe-destination M-SEM-datetime-synth-assemble-_instant_pair M-SEM-test-check-fx-checker-misc-orm-yaml-fx-checker-population-misc-pass-yaml M-SEM-test-check-fx-checker-misc-orm-yaml-fx-checker-population-misc-fail-yaml M-SEM-test-check-fx-checker-ring-orm-yaml-fx-checker-population-ring-pass-yaml M-SEM-test-check-fx-checker-ring-orm-yaml-fx-checker-population-ring-fail-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-setfam-pass-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-setfam-fail-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-empty-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-coverage-omission-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-covers-none-yaml M-SEM-test-check-fx-checker-setfam-orm-yaml-fx-checker-population-precedence-yaml M-SEM-test-check-ex-bookrec-model-orm-yaml-ex-bookrec-seed-population-json M-SEM-test-check-ex-bookrec-model-orm-yaml-ex-bookrec-adult-for-minor-population-json M-SEM-test-check-ex-bookrec-model-orm-yaml-ex-bookrec-already-read-population-json M-SEM-test-check-ex-bookrec-model-orm-yaml-ex-bookrec-genre-warning-population-json M-SEM-test-check-ex-bookrec-complete-orm-yaml-ex-bookrec-complete-population-json M-SEM-test-check-ex-expense-model-orm-json-ex-expense-seed-population-json M-SEM-test-check-ex-expense-model-orm-json-ex-expense-approved-population-json M-SEM-test-check-ex-expense-model-orm-json-ex-expense-invalid-chain-population-json M-SEM-test-check-ex-expense-model-orm-json-ex-expense-invalid-meal-population-json M-SEM-test-check-ex-expense-currency-orm-json-ex-expense-currency-population-json M-SEM-test-check-ex-expense-currency-orm-json-ex-expense-currency-missing-population-json M-SEM-test-check-ex-dispatch-model-orm-json-ex-dispatch-seed-pop-json M-SEM-test-check-ex-dispatch-model-orm-json-ex-dispatch-repaired-pop-json M-SEM-test-check-ex-release-model-orm-json-ex-release-seed-pop-json M-SEM-test-check-ex-release-model-orm-json-ex-release-repaired-pop-json M-SEM-check-arms M-SEM-assurance-block M-SEM-inheritance-compare M-SEM-oracle-expected-state M-SEM-synth-emit M-AGENT-argv-print M-AGENT-run-truncated M-AGENT-run-stdout-retained M-AGENT-invoke-version M-AGENT-invoke-version-probe-failed
    rows: 45  killed: 45  not killed: 0
    Exit: 0

### final-lint2

    $ .venv/bin/ruff check src/gnd/agent_cli.py src/gnd/agents.py src/gnd/api.py src/gnd/assurance/__init__.py src/gnd/assurance/_wire.py src/gnd/assurance/claims.py src/gnd/assurance/core.py src/gnd/assurance/evidence.py src/gnd/assurance/inheritance.py src/gnd/assurance/transport.py src/gnd/assurance_claims.py src/gnd/assurance_evidence.py src/gnd/assurance_inheritance.py src/gnd/assurance_transport.py src/gnd/checking_service.py src/gnd/cli.py src/gnd/codegen/emit.py src/gnd/codegen/manifest.py src/gnd/codegen/plan.py src/gnd/declared_adapter.py src/gnd/diff.py src/gnd/evolve/service.py src/gnd/exp/declared_invocation.py src/gnd/exp/session.py src/gnd/exp/session_eval.py src/gnd/exp/session_store.py src/gnd/exp/session_v7.py src/gnd/exp/tests_runner.py src/gnd/export/lean_cli.py src/gnd/export/service.py src/gnd/export/souffle_cli.py src/gnd/install.py src/gnd/manifest_paths.py src/gnd/payloads.py src/gnd/process.py src/gnd/report.py src/gnd/review/adapters.py src/gnd/review/runner.py src/gnd/safefs.py src/gnd/synth/assemble.py src/gnd/synth/boundary.py src/gnd/synth/mutate.py src/gnd/synth/oracle/__init__.py src/gnd/synth/oracle/constructive.py src/gnd/synth/oracle/mutations.py src/gnd/synth/oracle/state.py src/gnd/synth/paths.py src/gnd/witness/cli.py src/gnd/witness/service.py tests/support/public_probe.py tests/support/rf2_session_pins.py tests/test_agent_cli.py tests/test_codegen_force.py tests/test_contributor_preparation.py tests/test_public_assurance_inheritance.py tests/test_public_exact_scope_guards.py tests/test_public_inheritance_successor_constants.py tests/test_public_inherited_successor_comparison.py tests/test_report_json.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_synth_external_uniqueness.py tests/test_synth_false_pass_quarantine.py tests/test_synth_mutate.py tests/test_v62_phase4_assurance.py tests/test_v63_phase2_cache.py tests/test_v6_phase6_execution.py tests/test_v6_phase6_runtime_identity.py
    All checks passed!
    Exit: 0

### repair-G1-unsandboxed

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py --tb=short
    392 passed in 60.76s (0:01:00)
    Exit: 0

### repair-controls

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_rf4_review_regressions.py tests/test_public_construction_site_guards.py tests/test_report_json.py tests/test_v61_phase4_projection.py tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_exact_scope_guards.py tests/test_v62_phase4_assurance.py tests/test_v63_phase2_cache.py --tb=short -x
    1126 passed in 46.88s
    Exit: 0

### repair-portable311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf4_review_regressions.py tests/test_public_construction_site_guards.py tests/test_v63_phase2_cache.py --tb=short -x
    81 passed in 22.05s
    Exit: 0

### repair-portable313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf4_review_regressions.py tests/test_public_construction_site_guards.py tests/test_v63_phase2_cache.py --tb=short -x
    81 passed in 23.77s
    Exit: 0

### repair-scaffold

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_contributor_preparation.py tests/test_review_credential_launcher.py tests/test_measure_offline.py --tb=short -x
    97 passed, 1 deselected in 16.02s
    Exit: 0

### repair-lint

    $ .venv/bin/ruff check src/gnd/agent_cli.py src/gnd/agents.py src/gnd/api.py src/gnd/assurance/__init__.py src/gnd/assurance/_wire.py src/gnd/assurance/claims.py src/gnd/assurance/core.py src/gnd/assurance/evidence.py src/gnd/assurance/inheritance.py src/gnd/assurance/transport.py src/gnd/assurance_claims.py src/gnd/assurance_evidence.py src/gnd/assurance_inheritance.py src/gnd/assurance_transport.py src/gnd/checking_service.py src/gnd/cli.py src/gnd/codegen/emit.py src/gnd/codegen/manifest.py src/gnd/codegen/plan.py src/gnd/declared_adapter.py src/gnd/diff.py src/gnd/evolve/service.py src/gnd/exp/declared_invocation.py src/gnd/exp/session.py src/gnd/exp/session_eval.py src/gnd/exp/session_store.py src/gnd/exp/session_v7.py src/gnd/exp/tests_runner.py src/gnd/export/lean_cli.py src/gnd/export/service.py src/gnd/export/souffle_cli.py src/gnd/install.py src/gnd/manifest_paths.py src/gnd/payloads.py src/gnd/process.py src/gnd/report.py src/gnd/review/adapters.py src/gnd/review/runner.py src/gnd/safefs.py src/gnd/synth/assemble.py src/gnd/synth/boundary.py src/gnd/synth/mutate.py src/gnd/synth/oracle/__init__.py src/gnd/synth/oracle/constructive.py src/gnd/synth/oracle/mutations.py src/gnd/synth/oracle/state.py src/gnd/synth/paths.py src/gnd/witness/cli.py src/gnd/witness/service.py tests/public_site_census.py tests/support/public_probe.py tests/support/rf2_session_pins.py tests/test_agent_cli.py tests/test_codegen_force.py tests/test_contributor_preparation.py tests/test_public_assurance_inheritance.py tests/test_public_construction_site_guards.py tests/test_public_exact_scope_guards.py tests/test_public_inheritance_successor_constants.py tests/test_public_inherited_successor_comparison.py tests/test_report_json.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py tests/test_rf4_review_regressions.py tests/test_synth_external_uniqueness.py tests/test_synth_false_pass_quarantine.py tests/test_synth_mutate.py tests/test_v62_phase4_assurance.py tests/test_v63_phase2_cache.py tests/test_v6_phase6_execution.py tests/test_v6_phase6_release_reader.py tests/test_v6_phase6_runtime_identity.py
    All checks passed!
    Exit: 0

## Verification selection and limits

G1 frozen compatibility is run before and after moves/routing. G2 current graph, alias, algorithm, observed-patch and scan controls run. G3 affected installation, artifacts, processes, assurance cache, synth, codegen and optional wrapper consumers run; the635-pass prefix and the1484-pass repaired combined move gate are separate retained outcomes, not a summed acceptance count. G4 selected portable gates run on3.11/3.13. G5 contributor/offline controls and explicit changed-path Ruff run. Frozen identity is inherited only for434 unchanged files and the frozen authority/distribution/selection/toolchain tools. Old gate results are unavailable for changed inputs.

Full default/historical/evidence/census/proof/distribution/native/provider suites retain uv run pytest -q cadence only on explicit owner request or separately configured CI selection. No recertification is selected. Baseline/macOS sandbox metadata and setuid refusal differences are retained with successful unsandboxed controls, not relabelled as product fixes.

## Measured budgets

Committed production comparison at301e80f adds11948, removes9100, moves7977 and adds3971 nonrelocated lines. Original2200 ceiling exceeded; explicitly delegatedA6 ceiling4200 passes. Original15000 moved ceiling passes. Python test additions472 pass1800, while3043 data lines make3515 total: original1800 total exceeded; explicitly delegatedA9 ceiling3600 passes. Touched and documentation counts are bound to the final record bytes in RF4-final-budget.json, with original130/180 and A5 ceilings250/800 retained.

## Review and findings

One reviewer is one reviewer. The initial review independently inspected algorithms, identities, graph, paired diff observations, frozen inputs and manifest changes; portable and mutation outcomes were read, not rerun. It found three defects, independently reproduced and triaged before repair: twenty missing import bindings (blocking compatibility); stale assurance release/cache path stimuli (SM3 hardening); and a report source guard visiting its shim (SM3 hardening). Observed-red regressions precede each repair, with current-byte controls passing. The base forwarder assertion was also reproduced against exact387aada before its focused observer mapping adaptation. The retained review and before-fix triage record exact details. Initial plus one bounded repair review, no third round.

The bounded repair review over c61dd7b..301e80f returned no reproduced residual findings. It confirmed all20 restored import identities, current assurance mutation paths and payload/extension source/runtime owner mapping; it found no alias impersonation or owner-matching regression. It inspected retained results and did not rerun them. Same-seat count3→0, self-inflicted ratio undefined for0/0 in round2, two-review limit exhausted; no third round.

Self-audit defects were repaired: late oracle closure helpers, lost imported aliases, colliding JSON alias, stale cache/codegen/mint/report patch sites, and an import normalizer that mutated its negative-control input. The producer control is observed red pre-fix and26 controls pass after retargeting. Contributor dirty-copy fixture failed at the phase base too; the isolated387aada reproduction is retained, the missing link targets are copied, and all4mutation meanings remain. No production algorithm or approved answer changed as a repair.

## Refactoring review

What did this phase reveal about existing structure that should change? Refactors EXECUTED: separate process/adapter ownership; shared ordered assurance capabilities/identity; constructive/state/mutation oracle ownership; payload and thin service closures below entry; one checking/admission/report orchestration shared by API and diff. The same green focused gates cover these structural changes. The filesystem variants stay separate by approved decision rather than being merged.

## Boundary -- what this phase does NOT establish

No feature, tightening, new semantic family/schema/version/CLI command, performance, certification, assurance-release or publishing claim. No broad replay, installed candidate or Linux verdict. Remote CI at c61dd7b did not start candidate/regression/phase2 jobs because of the recorded GitHub payment/spending-limit refusal; installed was skipped. This is an infrastructure refusal, not a product or later-byte verdict. Historical certificates describe old bytes. No source-owned question is discharged and no shim retired. The prior source-side attestation limit remains; no reachable source remote or new human attestation is invented. Approval marks are delegated agent rulings, not owner reading. Plan amendments are reserved to milestone close.

## Open questions

RF5 CLI ownership, RF6 model query/index, RF7 strictness, RF8 session SCC remain their named phase targets. RF3-OQ1 scope wording and RF1 meta-node exemption wording remain milestone-close items. Source-owned artifact/canonical-JSON/import-walk/helper-tail questions remain source-owned. Reconcile the approved visibility-only filesystem and shared-domain checking decisions with the plan's move/direct-call wording at milestone close; no silent claim of literal all-body relocation. Shim retirement remains RF-D5.

## Refuted premises

The prior claim that all imported compatibility bindings survived was false: the twenty-object inventory and observed-red identity checks refute it. The assurance source/omission and cache mutations did not exercise their intended byte/member branches at the new homes; the transition source guard visited the shim. Their original arguments remain in dated spec/review history, corrected by A10/A11 and current-site controls.


The initial500-line routing/alias estimate and2200 physical nonrelocated ceiling did not fit explicit compatibility. The initial1800 total test ceiling did not account for paired successor answer data. Both original overruns are retained with dated delegated amendments. The contributor dirty-copy fixture did not contain its actual linked dependency boundary; the failure predatesRF4 and is reproduced against its exact source base.
