---
milestone: code-refactoring
station: phase-RF6b
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF6b
date: 2026-10-06
source_base: a3f35a6d3f562aacf325056493a0799412811117
verified_source_commit: 60559aa916d0c156c9de791a110bfc9a2eaa97f3
move_commit: 9e741dd
gate:
  command: ".venv/bin/python -m pytest -q tests/test_rf6_packages.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf1_pin_harness.py --tb=short"
  exit: 0
  output: "402 passed in 24.39s"
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately scoped CI selection"
  reason: "Full default, historical, proof, census, evidence, distribution, native and certification lanes are outside this selected impact closure."
evidence:
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A1-spec.md, sha256: 750ce87e44bc3f0ffd3a136db5ae326aa73f401ee1ba0cc7be7c9ccc90a1c13e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A2-spec.md, sha256: 50d09a93d24bae8d8bb3553936fc463e61b2c5cdf3daa94e575c8fde62b3e296}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A3-spec.md, sha256: 70c87fc3a83e1d6f5b9f212a24b350bb8e4d7c12326a1d356322f4485a26fa45}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A4-spec.md, sha256: 8333544b33de7b5db4b10b9b14f4c810ad68ea898d9b77d0a63448e4d08d4574}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A5-spec.md, sha256: c357ab3eb5da90fc39a2781cbb0bcf4dad1ce8edad5dccdbaf032e6912a9319f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-A6-spec.md, sha256: 7fc20463f2710e702c73eee8b516e1fe6a7379b0cfd7b69458ad5aed6139b072}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G0-green.json, sha256: 90df71e5e69bfa906bfb019e3615b161c02f6ae92a6688f314a33900c0022bc1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G0-green.txt, sha256: 32d84485597e9f59456642514c5faa986732ec9240cfc72a7359bf0ba459d4ed}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-final.json, sha256: 2fa763ecb56054836a78cf738e5fb79467af69770e98622422f6a5063a70ebc3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-final.txt, sha256: 4c867de0203bb9c9def19a09a295e0aa457848ea05e6cf6b14fc6f086c6469e1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-portable.json, sha256: 8057f5acf473f2a49ed54e368c12ec554f3602154300d100b1e5d972952c9772}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-portable.txt, sha256: 85de481b2322f5e0325fcbbd4789e48045898fea36b40fa7ca07cb8d3fa748a7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-ready.json, sha256: 3840b94833b13cf2b786d97c1d17e73e6c37d3524ebeb6ae8c33b9ea55168521}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G1-ready.txt, sha256: 2de9f7deaf7accb4731902d489db01931c204a84cf8cb733453d56ba4f3c7458}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-cache-final.json, sha256: 5ef5e87e64d17f186bcfc032f714c4ccd08203eec029a7246cc28589ea8ad07c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-cache-final.txt, sha256: c900aebf28ed0246becaeefde7f99fb1975b24ab57b28a1c7e13a84bb3d9c584}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-final.json, sha256: b584876df45c604be6f82ebf0d7d65c223c60d36f12dc0be9f75fc263caccf3e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-final.txt, sha256: 49fdcce5378acb9790f25e4a39c61a5bc28b02b9ef94c33149682b621ce94ea3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-ready.json, sha256: 92fb19e79c72d69615ae670bded0fba731fcf4d0726fe45381fb052f683f5ae9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2-ready.txt, sha256: bf9c5c62fa08fd1bf3c996bee43b2303503a14f8511c44ddfceaa79a91d39063}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2.json, sha256: 37209a854fc57bd0511ce254631916d23f8b225306b5949c51487330c507de7f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G2.txt, sha256: 826949f91c3cfefb9f71e09eb051466858cec611da420c79a116f72337876bb0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3-final.json, sha256: 2041dab7186e848b778816a9f53484342e9f4a08c2bcb9b430842f4d5546677d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3-final.txt, sha256: 55a46a273b73825dede8ba44386ff71fb85a13af75f93ea8dc347bc1a3ce654c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3-ready.json, sha256: a017418da978ae7909cb1feffeff0027b50cbc9cf337779741ce2499456c5528}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3-ready.txt, sha256: 49016cb301cd60bf7c558756058415b3b79271d070970191877eaefba335634b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3.json, sha256: 02d7ccafa2d3886259502538a811417d268c691e34d84bb4ecc8e68da5b748b4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-G3.txt, sha256: e32b9dada6dfda3963078865fb543defe33ec35f5b0a1c342cd115a87dfeab74}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-affected-mutations/control.txt, sha256: ec263f811d7fd5db98c626a13f3327db9a3851025f89626c531626b3794b020a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-affected-mutations/mutation-report.json, sha256: 8462ebd72c77ad3c0731c209c14ee51607aa5bfa7d6bafe894afea01175010b9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-affected-mutations.json, sha256: 09ff67cfd68cf2c1f0f689b3d5a8e20e69199f186652ccf29fa6e0f7b3c124ce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-affected-mutations.txt, sha256: 5ecad0ceb1e0561b06a2b93d7a34c6e94d1c77a6cc27de64480388dc9bc13d4d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-amendments.json, sha256: 0ac403917cdb9fb7cce2ac000cad7f12ea4ec56e91df334f36d4c023e65b8689}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-approval.json, sha256: be5fe99cb5ca63078e58c598186951ad5e3fdb82f57f8c00aa9e920fae903a48}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-approved-spec.md, sha256: 9614e074cc3b532a8cec97f0ed8774a13e29c7fa236862a645041ffae197a1de}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-current.json, sha256: 981cc0cfad5432a5c34caeeb1fdc2e2dc98b39a6bba2ed3d277d4f24dbb5246b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-current.txt, sha256: ca51df62ec78e91f48ff646a2f964b56a028a50a05ee8ac8ae7eae4318466f21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-final.json, sha256: cc047e6eebfed25b13842d9197ee6dbd277a89c47e4a4905e0b155e916cec824}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-final.txt, sha256: 081782baa8df905538cf2245b6e665fa9d6085f500f29a8874b48ed389c0c961}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-portable.json, sha256: 5054f81b5988d5a583f10c9565c8cc44f7301bf3b88d9d70816a2b3ae2a78154}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-portable.txt, sha256: ca51df62ec78e91f48ff646a2f964b56a028a50a05ee8ac8ae7eae4318466f21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-ready.json, sha256: f023e8e2479da5462ea05ef57e730fd3a2cd355a77ffb4cc742fd7aa271bfaa9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture-ready.txt, sha256: ca51df62ec78e91f48ff646a2f964b56a028a50a05ee8ac8ae7eae4318466f21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture.json, sha256: 2f5f672f523096f2f0ec6f2343117f7cad4a3c198d4d933611dd560ed581700b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-architecture.txt, sha256: ca51df62ec78e91f48ff646a2f964b56a028a50a05ee8ac8ae7eae4318466f21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-atom-observer-red.json, sha256: fadbaed4e5b5a2afdb2bd93e38723817cc5ee1c5ffbd803dfccab8eea8b9febd}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-atom-observer-red.txt, sha256: 2564d48f7899a9840175d8d782361f7b564f2d209b51e45618e14f4b8414fea6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-binding-homes.json, sha256: 99983c5d80fd3d1c81e76c88e509786b09f56317f4c9be81de6a55e06772ae50}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-final.json, sha256: 48d00d5fdfff4f8e841d83a04c494cec890950f43205c63b60a7f6e8f0614ab6}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-final.txt, sha256: 66a7dd8f527ac1958728944fc0cf4d7bff6cc2e017f3ac8c3cc1396b3bcf2fd0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-lint.json, sha256: f0b5885bab280c4b85f8fb6668d147ba69e5319e154e5ec7ed548f5f7775bb88}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-lint.txt, sha256: e997af51d049032540ea427dbe1037d4fa275681f613f439fcd1d6c906e2422e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-manifest-adaptations.json, sha256: 50e16bd798e4edfaebd8ab4380a3587f4336a440a4128400416630bc4362cb00}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-metric.json, sha256: c91e6409a00dc0fafb9e9a5b54233dbf30e7bc02b7189ecd933f1fcca341ff21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cache-metric.txt, sha256: ca51df62ec78e91f48ff646a2f964b56a028a50a05ee8ac8ae7eae4318466f21}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-final.json, sha256: 5736141c8dce4e461d779d9fead5fdc8b362b5255751b8c450ac45e58141f184}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-final.txt, sha256: 3e1257754ed9b28f1bd077430f56d25c65e198ce81ecb0c9b9ec2a7898b858fa}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-lint.json, sha256: db87a25ab4e8d4573aea4f3151efc8ea064c32defa447db065528f81374b4ed9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-lint.txt, sha256: 2f4005aa6e3f0363ec40fe2231a859686e6a4ccbd82cb95305ad51bfb35c63f4}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-py311.json, sha256: 90617d12997f28535640e491afac268d80e736c0815ed0823c162a8bd723ba53}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-py311.txt, sha256: c242ba4c2037c3f0b7f41431edb4a66d78fed10fc016b365cf901cb2e0b00bf5}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-py313.json, sha256: 85af73c90acdc4f08615cc2ae8884f7af8efc08785d9fe1d9c6628d4f32c3e8c}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-closure-py313.txt, sha256: 2d5582c64eab4dc971362553f01445837f1ac197ce83e51f3cdab30a3b4b400d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cycle-green.json, sha256: f20563493ac5d0eccb440535c8f3441bbfa4d2865c5a6361646cac80daf57de9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cycle-green.txt, sha256: 5cfe942647a834f69c5d4c47465a59bd07aa91a83c9b79040deb5216bd372270}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cycle-red.json, sha256: 043a9158b6fda7e2dddfbdc0909b6fee5a39affbcf86423c0287b1af73777992}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-cycle-red.txt, sha256: 3c95b7ff65101629ae32b521fe7ee886b64795fa68140669a26c9cdc4e03c4df}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-definition-baseline.json, sha256: 204efd34b4a69c60baa020c5304edc9a49b7a1bb5d821ac1802afee339be9913}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-direct-final.json, sha256: 26e3f2f236936de190c6d5d86bfc46e5a562c1e5e5f159136e26e3502ab29778}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-direct-final.txt, sha256: aa5d44fd2374e01ef7ec366c781cbec2d57d90e3aa93087095a19231b8f55192}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-direct.json, sha256: 4d00f9c116ce862474b50cb40a40a07ce693eb938298c1509af56c1f64495808}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-direct.txt, sha256: 05d59009233d12e12fd4e1b23c2ee6709ed145eb1b005f75c65f32bf2731f156}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-dynamic-query-candidates.json, sha256: 3fa6289dbb54785082c9b9ace5be3d57509610349bb1cd1c5c4762aaa7a9ef3f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-final-budget.json, sha256: 40b4367b08bf8a41e277d0ba87afb1d4c8fcf933a778d7ed7735a945931f4a32}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-frozen-authority-and-meanings.json, sha256: 5a11e89621e99531ba874b3563fbdbdb2cc8c8e287a0c0b11707a41b6dca9233}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-import-baseline-py311.json, sha256: b23cb8d91358c8008829a4b158fb167964238393ddb1182693a89f3876380d27}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-import-baseline-py313.json, sha256: 78c7035f07375dc70850f1a5e50a8f4ba8d2f0b16c297f1c3d62d7f460557798}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-import-baseline.json, sha256: 44f3afa597e3b2ead471cdf5967493f235eec220ccea86ce8a3e67380ede5c2e}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-import-consumers.json, sha256: 7cd1136261af9be9ca0dce022f94145171cf42668108b9a93de55087728a0bf3}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-lint-ready.json, sha256: e5f14544443724005e920782b5e90c8a72085f0bf85c8576df3092363ef82f5b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-lint-ready.txt, sha256: 661ca902233de34259feba8adc6743ffe554c546ddfc5de23bad3d474824598f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-lint.json, sha256: 82e227325e95c72e177fe080b8cb620035f96604e7f9f555bc1abf176a4f13fc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-lint.txt, sha256: d6d8d8f6495b6bdadf11b3620b942a21f9ebaa12047424f698d8292ce7cb0af8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-manifest-adaptations.json, sha256: fe06f63fe6a4425963b98336e2d3d0fe623b9955d6123b8a6b02864dcb0efc0f}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-method-metadata-py311.json, sha256: f3b1f6b9291e0608b6ff537897bd3c12a0dfb2249841170177d43e1fb352c479}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-method-metadata-py313.json, sha256: cb23d0b3a6a802fa6398cd28260c9f2cc0530e182bb346b63631d9333f013d75}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-method-metadata.json, sha256: d0b95de7d9bbc5c15e0cd32ee5ecc683c7767f81720a701c2e93aeadbb1ae385}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-module-doc-red.json, sha256: 686a92da2341e96e6ee53b7406e6fccafcd5d57ee5be2b660efb8dbd37477093}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-module-doc-red.txt, sha256: 939365563f5f088453ab5b39ef9e489ce7e4c182a04d8275f8f169fff9e71012}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-module-docs.json, sha256: 01c8bbde67e8c96346783e5648fb18c20773b3e6ef30394dcff45e9745bc929d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-budget.json, sha256: 039a3053760b5d5e165cf64b9109fff215a91d442f9cc1c46bbc50468395d1ef}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-first.json, sha256: 3de0b8e2f3f41ade666866eed5e0fd0a2dee9ae3d58968c1b4b34b4b1e116875}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-first.txt, sha256: de676a9a81a7c8944aaefe071f5c4cfa222ea19221d5e7530e7ddb4b51c0d8b7}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-metrics.json, sha256: 9276f5bb2df016d333ef12099b5cbc2cec26bcc2a97a43fd8ef8c37949c30fd8}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-second.json, sha256: 059dc90951ad8307d6c15e87c7a00565c6f5bbc7f12b1513ca31ac49f8082b36}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-move-second.txt, sha256: 3fc55a0421d4fa61718227469e8ca004ae98030e0c632801597d106d88a40255}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-moves.json, sha256: 3c76da6c2757028cb11f3907b3ade67b22a098325cce25aad3de1081a8a6b641}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-mutation-originals.json, sha256: abbb7ba58a34a84d3fbdca90a47cdbed83b230ee333c6c968670809f2259beb2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-doc-metrics.json, sha256: 1aee139459ebe33c133a5abb8e76883d42394c1ac31806caad352c195a8de0ce}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-pins-final.json, sha256: 1926f5a5905069f8129ad0e538d121d4f755f89623a9acc2395b29155b8f2792}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-pins-final.txt, sha256: 71c01d4f8f220159457a6c4843c790b6cfc4cb6bbaccdfd633013de23868cd95}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-pins.json, sha256: eaf4fa936051400f781c5c5e45bc236152f79ad38e2e25bf4783923bc5bca185}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-pins.txt, sha256: 153d1647f0fdf1f04e5a138eca19d4a8c925d8ec98350b112b1eb5b01049b817}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-pre-portability-metrics.json, sha256: 770ad81796647a6f2ac83b9f5c73f41d0f25af9c6c459e1364d9c2b6b72cd4b0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-predecessor-runtime-differences-py311.json, sha256: b08975d699ffc6e87632a2340eb2a09acd18eeae8f47ae134ac9858e95d7d9bb}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-predecessor-runtime-differences-py313.json, sha256: 920cef3598bc8adc989e6e532295adf1cd3d88c67e57873931338a7c55cd2319}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-predecessor.json, sha256: 2fc90a212f12ad6cc6e143b73cfbcec7e20ff1e2d2acbce5c78bf1809f483245}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-predecessor.txt, sha256: 01d692fae8eb22fd224214fad07bdca28ba08fae8e897c64776b9aaafa7f693b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-preexisting-encoder-red.json, sha256: 6ee04114a7df7b29f32e5811273d6dc8d942bc5c7a0008f97e91db649263a0ea}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-preexisting-encoder-red.txt, sha256: 3947303acec083525f954cb2dc90df3440c44bcb3a50349cb3adbc7c8bdaa1e1}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-prototype-metrics.json, sha256: 3924f37fbe1033fc50657ea130437b04e1423cab3e6f99c9582dc61d11bc011a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311-final.json, sha256: a4809fa760d2e0d24b98e8d398a3120f5e4675dfad2b06c73e42b96a72e7076a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311-final.txt, sha256: be450b982c92e6fb478bf37fd025e85ebee88a9432eaf0106a1db8e68cb35066}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311-ready.json, sha256: a4d9447ff36233112171ea7db8f32ceedc42c1a2301d52144d502852fae0721a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311-ready.txt, sha256: 41589f1b70167564df7456d4bcff8361d2fbb5f2ae842ff156c7463c2b76cff9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311.json, sha256: dd51a2622dc9e7507508909886c9c5ac1f8fcd67d8e6c7fd6d19edbd97741b85}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py311.txt, sha256: 4d64e1044888e73346cc31425143536fa20ad4334d8a47e1e12bff2f2414dd24}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313-final.json, sha256: 81c360a7c8b63edfd5bd3d5b82ef40c1979d53087e69a30cc40812dce0b04c3d}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313-final.txt, sha256: 877e99b82ba6a858108525a32035a49e1b888c9d26c1ae9ab0dbe767f2b1912b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313-ready.json, sha256: 6678f1837c73ab61d28ddfa3d24af1cffed8d9a18ece4eda9984a32ac685f376}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313-ready.txt, sha256: bf39b7780beef55e75e0faf3b1789ade304ab89ee376340d98f635534bf067cc}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313.json, sha256: 0fb1f1d83477a06e56596484985f1475d6bcb18fc16ae16a7f34c9fcd0f39ee2}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-py313.txt, sha256: 736e71f2d00e0cfd49d6ca6c9dbb66ec43c1a450164b12ced0fe05151e6cbfc0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-query-allow-list.json, sha256: aa4121f7d8a94e6eaff260a3115dac0f749ad5d46308b81693a9861a1aad30ed}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-record-scaffold.json, sha256: 43ca93716e3f2edd6d8f8beffff280c1b0ee8788cb633e47b67603ef005d552b}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-record-scaffold.txt, sha256: 03bd4ad4ede4821556d3ffe67c3d9b5f6538018547f41ece57f4ee383a8de982}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-scaffold.json, sha256: 2581cf45ca76599f29aa974ae4e0e84c576a7c0e0ff487c46993f1b2bb8bf612}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-scaffold.txt, sha256: 6bbf62ff8f147675f906bf652ec4847d846f189d7c8d956c48894aa870060bc0}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-split-red.json, sha256: 14862e4207bbf61dd7134c4d4e117fe95744e3c34409fdf75bf57d02b64116e9}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-split-red.txt, sha256: c719e62cab7758e20997106a585a1e6050767ca6b6e7ac398415668cbf3b2740}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/RF6/provider-review-authorization.json, sha256: e3f22c35ee7dda435239f67d57633d8e3da2f687e5f8a8196f4521037ef8ec5a}
  - {path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF6.json, sha256: 850e61afd68a3e9a530ae750b7f5f99437782f513d231136617e521f61f44392}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6b-codex-review.md, sha256: a7775f7b8148cdfb8818c669f4474b469702ba2727c9e57bc868366399099751}
  - {path: .gnd-planning/milestones/code-refactoring/notes/phase-RF6b-spec.md, sha256: 6281f3e1106d4efbf011d47fbe4f391fbd27ad064e65efacecd451a9be90af07}
---

# RF6b -- model and checker section packages

## What shipped

RF6a 011 was a hard prerequisite, completed at a3f35a6. Prose instrument and omitted optional spec panel received delegated approval (auto=true), 2026-10-06, under the owner's process-phase RF6 auto instruction. Exact preimplementation spec SHA9614e074cc3b532a8cec97f0ed8774a13e29c7fa236862a645041ffae197a1de and each amendment's preimplementation bytes are retained. This is delegated approval, not a human reading.

Atomic move 9e741dd preserves every 232 original top-level definition/class body including decorators, every 468 predecessor binding (238 model,230 checker), callable qualification, alias identity and pickle identity. The original namespace/module documentation remains literal. Intake remains in model/__init__.py; structural and semantic rules live in model/_validation.py, effects in model/_operations.py. checker/_reports.py holds report dataclasses; checker/_core.py holds checking algorithms and registry hook globals. checker/__init__.py explicitly exposes historical names. Metadata assignments preserve source-defined and GND-qualified generated methods; foreign stdlib methods retain their native metadata. Exact archived-base method inventories69/78/79 and import baselines cover Python3.11/3.13/3.14 without arbitrary-name normalization or per-method skips. Uncaptured runtime metadata evidence reports unavailable; general body, pickle, source, graph and query tests still run.

Complete import consumer census449 nodes and11 physical observer files guided actual patch retargeting, full widened scan scopes, six-layer map entries, and physical skill citation changes in the same move. Reference intake patches remain in the historical model namespace; semantic rules and checker dispatch patches target defining globals. A compatibility alias does not forward monkeypatch writes. Every physical home is scanned by the actual applicable observer; injected omission and forbidden-reader controls fail. Active atom readers are four algorithm homes, while passive aliases/report homes remain in the complete raw-read prohibition scope. No model/_intake ships; complete six-home and definition inventories prevent silent scope shrink.

ModelIndex cyclic metadata was discovered after the move. A timed child regression observed a pre-fix TimeoutExpired; A6 approved a separate adjacent bounded-cache repair at 60559aa. Repeated dict/list identity in the dumped document bypasses caching, returning an uncached detached snapshot. Both cycle shapes verify mutated query freshness and retained old snapshot isolation. Canonical encoder, public identity, model admission, historical helper algorithms and moved bodies remain unchanged. This repairs the new RF6a query cache rather than changing an old semantic feature. RF6a 011 remains tied to its old verified bytes, with a dated successor annotation.

RF1 original golden answers remain unchanged. All167 original mutation IDs, stimuli and expect_red answers remain frozen; only four physical file locations adapt, their originals retained. All four affected mutants are killed with a passing green control. Full checker-family, verbalization, semantic adapter, validation, reference/universe and guarded consumers receive selected current-byte controls. Source-owned units.json and tests/test_public_distribution.py remain byte-identical to the phase base. Bounded b3 adaptations retain removed model.py/checker.py rows; no new distribution authority, source-side attestation or release identity is issued.

## Gate output (verbatim)

Commands and output below are retained from their individual execution logs. Those files declare machine-path substitutions; output has no invented aggregate acceptance count.

### RF6b-closure-final

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_rf6_packages.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py tests/test_gnd_arch.py tests/test_rf1_pin_harness.py --tb=short
........................................................................ [ 17%]
........................................................................ [ 35%]
........................................................................ [ 53%]
........................................................................ [ 71%]
........................................................................ [ 89%]
..........................................                               [100%]
402 passed in 24.39s

Exit: 0
```

### RF6b-cache-final

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py --tb=short
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
...........................................................              [100%]
275 passed in 10.24s

Exit: 0
```

### RF6b-G2-cache-final

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_checker_families.py tests/test_public_semantic_adapter.py tests/test_rf3_core.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_ring_frozen.py tests/test_vacuity.py tests/test_model_validation.py tests/test_model_v2.py tests/test_model_guarded.py tests/test_model_identity.py tests/test_model_verbalization.py --deselect=tests/test_rf3_core.py::test_full_current_and_original_core --tb=short
........................................................................ [  8%]
........................................................................ [ 17%]
........................................................................ [ 25%]
........................................................................ [ 34%]
........................................................................ [ 43%]
........................................................................ [ 51%]
........................................................................ [ 60%]
........................................................................ [ 69%]
........................................................................ [ 77%]
........................................................................ [ 86%]
........................................................................ [ 94%]
..........................................                               [100%]
834 passed, 1 deselected in 62.04s (0:01:02)

Exit: 0
```

### RF6b-G3-ready

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_atom_bind.py tests/test_v2_offline.py tests/test_rf2_helpers.py tests/test_rf2_review_regressions.py tests/test_public_registry_runtime.py tests/test_rf3_core.py tests/test_v71_phase2_successors.py tests/test_v71_phase3_successors.py tests/test_public_derivation_evaluator_controls.py tests/test_public_derivation_evaluation_complete.py tests/test_public_kernel_production.py tests/test_reference_population_corpus.py tests/test_measure_offline.py tests/test_codegen_manifest.py tests/test_public_payload_alias_sites.py --deselect=tests/test_rf3_core.py::test_full_current_and_original_core --deselect=tests/test_rf2_helpers.py::test_diverged_encoder_source_unchanged --tb=short
........................................................................ [ 10%]
........................................................................ [ 20%]
........................................................................ [ 30%]
........................................................................ [ 40%]
........................................................................ [ 50%]
........................................................................ [ 60%]
........................................................................ [ 70%]
........................................................................ [ 80%]
........................................................................ [ 90%]
.....................................................................    [100%]
717 passed, 5 deselected in 67.04s (0:01:07)

Exit: 0
```

### RF6b-py311-ready

```text
Retained output edited to replace machine paths.
Command: /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf6_packages.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py --tb=short
........................................................................ [ 25%]
........................................................................ [ 50%]
........................................................................ [ 75%]
.......................................................................  [100%]
287 passed in 11.39s

Exit: 0
```

### RF6b-py313-ready

```text
Retained output edited to replace machine paths.
Command: /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf6_packages.py tests/test_rf6_index.py tests/test_rf6_registry.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py --tb=short
........................................................................ [ 25%]
........................................................................ [ 50%]
........................................................................ [ 75%]
.......................................................................  [100%]
287 passed in 10.76s

Exit: 0
```

### RF6b-closure-py311

```text
Retained output edited to replace machine paths.
Command: /private/tmp/rf2-py311/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py --tb=short
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
...........................................................              [100%]
275 passed in 11.19s

Exit: 0
```

### RF6b-closure-py313

```text
Retained output edited to replace machine paths.
Command: /private/tmp/rf2-py313/bin/python -m pytest -q tests/test_rf6_index.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py --tb=short
........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
...........................................................              [100%]
275 passed in 10.74s

Exit: 0
```

### RF6b-affected-mutations

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python tools/rf1_pins.py mutate --out .gnd-planning/milestones/code-refactoring/evidence/RF6/RF6b-affected-mutations --jobs 2 --only M-HELP-yaml-guard-gnd-model-yaml-stream-guard-error M-SEM-datetime-model-_temporal_literal_valid M-SEM-datetime-checker-_typed_comparison_values M-SEM-check-coverage-anchored
rows: 4  killed: 4  not killed: 0

Exit: 0
```

### RF6b-lint-ready

```text
Retained output edited to replace machine paths.
Command: .venv/bin/ruff check src/gnd/model src/gnd/checker tests/test_rf6_packages.py tests/test_atom_bind.py tests/test_codegen_manifest.py tests/test_measure_offline.py tests/test_public_derivation_evaluation_complete.py tests/test_public_derivation_evaluator_controls.py tests/test_public_derivation_parity_local.py tests/test_public_kernel_production.py tests/test_public_registry_runtime.py tests/test_reference_population_corpus.py tests/test_rf2_helpers.py tests/test_rf2_review_regressions.py tests/test_rf3_core.py tests/test_rf6_moves.py tests/test_rf6_query_policy.py tests/test_v2_offline.py tests/test_v71_phase2_successors.py tests/test_v71_phase3_successors.py --output-format concise
All checks passed!

Exit: 0
```

### RF6b-cache-lint

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m ruff check src/gnd/model_index.py tests/test_rf6_index.py tests/test_rf6_packages.py
All checks passed!

Exit: 0
```

### RF6b-cache-metric

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python tools/gnd_arch.py measure --out .gnd-planning/milestones/code-refactoring/evidence/metrics-RF6.json

Exit: 0
```

### RF6b-scaffold

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_contributor_preparation.py --tb=short
...................                                                      [100%]
19 passed, 1 deselected in 5.10s

Exit: 0
```

### RF6b-record-scaffold

```text
Retained output edited to replace machine paths.
Command: .venv/bin/python -m pytest -q tests/test_development_scaffold.py tests/test_contributor_preparation.py --tb=short
...................                                                      [100%]
19 passed, 1 deselected in 6.46s

Exit: 0
```

## Measured criteria and budget

Full current six-layer graph: 220 mapped modules, zero wrong-way edges and unresolved dynamic imports, no new model/checker SCC. The existing seven-member session SCC belongs to RF8. Private import sites 324→608: explicit historical facade aliases and private section imports account for the increase; no private-import reduction is claimed. Public-name retirement remains separately approved at the first public release after RF6.

Physical lines: model 5385→largest 4893 (ceiling 5000); checker 2469→largest 2365 (ceiling 2400). Checker facade 257<=400. The original model facade 400 target was missed: verbatim intake's original lazy self-import created a new facade↔intake SCC in the prototype. Before changing ownership, A1 delegated the revised model facade 900 ceiling (277 prototype facade +520 intake before deduplication); final 758 meets900. The original miss remains recorded. No largest-home target or line budget was enlarged.

Original query-site instrument320→299<=310; expanded literal-subscript instrument371→350<=361. Exact query allow-list rows retain individual reasons and only physical paths retarget. The query allow-list retains 281 individually reasoned rows. Dynamic inventory remains 5756 rows/7257 syntax candidates: syntax-candidate coverage is not semantic alias resolution. RF6a's policy evidence is retained independently; RF6b successors observe the new homes. Acyclic shared Model.source objects can be duplicated by model_dump and stay cacheable; repeated-container fallback speaks about the dumped document, not every source-object alias. Budgets compare RF6b's a3f35a6 base through final record/review metadata; final values are 169 touched files<=170, 280 test/data added lines<=3000, 1055 non-evidence documentation added lines<=1500, moved upper bound 7854<=9500, and nonrelocated production upper bound2087<=2500. RF6b-final-budget.json binds the accounting. Moved-production upper bound 7854 includes original module lines; verified verbatim definition lines 6608 are subtracted from all production additions to conservatively bound nonrelocated additions. No net-line subtraction disguises added production.

## Independent review and coverage audit

One reviewer is one reviewer. The required native Codex initial review reads the bounded RF6b diff including the separate cache repair, under the owner's explicit provider authorization. Initial plus at most one repair is the declared limit. The first invocation ended with provider-capacity exit 1 without a final report. One same-model technical completion retry exited 0: no actionable blocking, hardening or completeness findings. No repair review was needed. The reviewer executed six focused tests and read-only probes, independently checked 222 moved function/method global references with zero missing names, and matched the 220-module architecture measurement in memory. It reused first-attempt body/binding/pickle/cache probes as observations and read other gate evidence without rerunning it. Exact prompts, hashes, technical-attempt status and final message are retained in notes/phase-RF6b-codex-review.md. Reviewer reading is not suite execution; its actual probes and restrictions are retained in the review note. RF6a's earlier exhausted review limit is not reopened.

Own branch audit covers all predecessor imports/metadata and232 bodies; missing-binding and omitted-home controls; original module docs; pickle identity; effective semantic registry/checker dispatch patches and existing reference-intake patch controls; complete actual source scopes and active/passive raw-reader distinctions; overflow size negative; full layer graph and injected cycle negative; original RF1 semantic/helper expected answers and affected mutant disabling controls; registry six-hook extension; cache mutation/digest/snapshot and timed dict/list-cycle branches; uncaptured metadata-baseline availability negative. Criteria and dispositions remain in the approved spec and amendment ledger.

## Refactoring review

What did this phase's work reveal about existing structure that should change?

Refactors EXECUTED: six explicit section homes with historical aliases/metadata; atomic observed-patch and source-scan ownership updates; native baseline evidence separated by interpreter; physical mutation and skill-citation adaptation. These preserve original bodies and expected answers behind the recorded gates. The adjacent bounded-cache correction is a separately reproduced fix, not a move-only claim. No further refactor was needed for this bounded split. The remaining large validation/checker sections, procedural family bodies and primitive variant distinctions await RF7; session SCC/version/resume belongs to RF8.

## Boundary -- what this phase does NOT establish

One reviewer is one reviewer; native review findings do not replace executed tests or establish panel consensus. The selected controls cover named current-byte contracts, not all possible import/dynamic patch sites, full-suite acceptance, performance, a semantic proof, a provider/census/evidence lane, installed artifacts or another OS. The class inspect.getsource path through historical module qualification remains unavailable; actual-home AST bodies and pickle identity are the established controls. __file__/__package__ reflect package layout. Native metadata evidence is limited to captured Python3.11/3.13/3.14; no unsupported interpreter acceptance claim.

Historical RF3 numeric-scope assertion was independently reproduced on archived523cdd1 source with its own tests; it expects64 against actual242. Historical RF2 physical encoder observer likewise failed independently on archived523cdd1's own bytes. Exactly these nodes are explicitly deselected, configured lane exclusions stay intact, and complete current-body/scope successors replace their stale physical assumptions. Prototype overlapping ownership-edit runs are observations, not final-byte verdicts. Original known red logs and archive evidence remain retained; no broad historical repairs were attempted.

Source-owned control and prior source-side attestation remain unavailable for new bytes; units.json and the distribution authority test stay frozen. Earlier certificates and release identities cover their original bytes only. No certificate, certification/recertification, accepted ownership handoff, publisher, release or main-branch merge follows this phase. Standalone PyRel's no-GND-import boundary and distinct strict/truthy primitives remain unchanged (RF2-OQ2). RF6a's prior record and all earlier boundaries remain standing.

## Open questions

| Owner | Obligation / disposition |
|---|---|
| RF1-OQ1 / RF6 | Complete pre-move import/binding/body pins and failing successor/omission controls supplied; dated006 annotation cites this record without widening RF1's original claim. |
| RF3-OQ2 / RF6 | Existing reference intake order/identity preserved with verbatim bodies and current selected reference corpus; directed ownership amendment keeps intake in historical namespace. |
| RF7 | Tightening, primitive variant consolidation and remaining procedural normalization are deferred; this split changes no original algorithm. |
| RF8 | Existing seven-member session SCC, version/resume/open CLI responsibilities remain. |
| Milestone close | Repair normative ideal facade wording using the observed self-import/400-target refutation; source-owned ownership/authority open questions keep original owners. |
| Release owner | Shim retirement: first public release after RF6 plus separate approval; no retirement performed. |

## Refuted premises

The proposed intake section could be split into a directed standalone module with a 400-line model facade: refuted by the preserved lazy self-import and prototype SCC. A1 records the ownership and pre-expansion900 ceiling ruling; original target miss stands for milestone-close plan repair.

All passive new section files should call the canonical atom reader: refuted by a reproduced failing source-observer control; A2 retains complete raw-read scans and pins four actual reader homes.

Generated method/import metadata is identical across Python runtimes: refuted by native import failures and exact archived-base differences; A3/A4 retain native 69/78/79 inventories and all468 binding answers.

The original facade module documentation survived header assembly: refuted by observed model.__doc__ None; A5 restores literal predecessor docstrings before the move.

The bounded new ModelIndex cache prewalk handled cyclic metadata: refuted by timed pre-fix regression; A6 supplies a separate cache successor and dated011 annotation. No prior certificate or opinion is extended to this fix.
