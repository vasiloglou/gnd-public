---
milestone: code-refactoring
station: "phase-RF3"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF3
date: 2026-10-05
source_base: 8ff996f7cf0d17bb08f539bca1f4a116ed839fec
verified_commit: 41e69fcdf75f8c8bc603b93e7e9f9343bdd6916d
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf3_moves.py tests/test_rf3_review_regressions.py tests/test_v6_phase2_adapter_mutations.py tests/test_public_adapter_primitive_controls.py --tb=short"
  exit: 0
  output: "146 passed in 6.58s"
  note: "Characterized G1 and affected gates below; production unchanged by review repairs."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately configured CI selection"
  reason: "Full default and historical evidence/census/proof/distribution/native/provider suites are outside the selected impact closure."
prior_records:
  - path: .gnd-planning/milestones/code-refactoring/004-phase-RF0.md
    original_sha256: 87e3be484b7573aed2313a20086b7cd1b77da13d00b8e160699b5942b3a26154
    source_commit: 41e69fcdf75f8c8bc603b93e7e9f9343bdd6916d
  - path: .gnd-planning/milestones/code-refactoring/007-phase-RF2.md
    original_sha256: f9066b17d6ba82a35a2c1cb291947a60b3704a088199e27387ec887131248624
    source_commit: 41e69fcdf75f8c8bc603b93e7e9f9343bdd6916d
evidence:
  - path: .gnd-planning/milestones/code-refactoring/004-phase-RF0.md
    sha256: 9b1207aca6c00606e8519c00ecda4c623a00543c0b3c80c9c83535a5b6bff25b
  - path: .gnd-planning/milestones/code-refactoring/007-phase-RF2.md
    sha256: bed4da233f786e2b651135d7d8d01ad11998dd9d831f76a4cb3c350ea8066f6f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/baseline-agent.json
    sha256: 96b748c228e9054a92cd937b85d13d47270152c2d776bbe467dfdfe413b1acfb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/baseline-agent.txt
    sha256: 0b2f07d43904fc8918ac3fc986947b3730572ae1169ba6060c421a3c9940a079
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/baseline.json
    sha256: 9fd56b909cf1695b97b8dbf3ad6913a0f3fe8eadaefcd00ae61f750a6c06ede7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/baseline.txt
    sha256: 8ff212035912cfc245029d45bf180d7ba22c3a6cfb71cf68e3af4cfabff58d7d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-first.json
    sha256: 0736b25af74393078b91b01eefb546e9ebd3300be37501ed4cbcfb5d5c6635c0
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-first.txt
    sha256: 33dcb1a3efd494789edb9ae926a8a3dc55aad34c493b97326407c73dc03a3693
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-green.json
    sha256: d6ef55cdf7bd2ab5e079e618ea9e4328afbbae129c6ce77d58a643353a4f3334
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-green.txt
    sha256: 7fecfb06ef7345a5b58073dc5728c1612991b152fea2a5d8122ea01f6249d7da
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-repair.json
    sha256: 949187f4819b41c551b7aa385460cf464cf31d544033d38541c71fcc4a9a2bc4
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/core-repair.txt
    sha256: f0630dd05c02728a226404d776fd6cae65a1544f69eedef9a9f766efbd39998c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-audit.json
    sha256: 9e3de9b3f216164899c9116828eddcadeee6772545cfa4e270c084c29ec46d49
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-audit.txt
    sha256: 6a5f3a9c9b3ca164d7aa2fa6996223086b3834c601e7dfedef47276212b581ea
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py311.json
    sha256: 6d96ddce89309ef25db3f796026f6fa0865b3ee45bb30513877dfce1c34d26f3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py311.txt
    sha256: 36361d4b077146a2789850d308fdf7dc05d10b42d7f4d2585dcc0d9848917250
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py313.json
    sha256: 7ac62bfb15e53a3a9684070001ae4200219cede456550751965874e8aff3f191
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/coverage-py313.txt
    sha256: 54e04552ed4b940006df81f6a0cc26a2493339779ef862f17832f4b3c4e218de
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/final-G2.json
    sha256: f4aa3e510ed051b7be24d0aa08ff25fc9a053b56fb435ca1b559b42dc346297f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/final-G2.txt
    sha256: dce37e0740891db6e102382ee918eac04f1695864fd704de4acc89ee08d5979f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-G1.json
    sha256: 222002fd1fe04185b8ba4d3cc2266394530c2bf174602da23de36d4ff842aefc
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-G1.txt
    sha256: 563867dc4ea774801125697074f94e9a950f21a10bc1fd6398aad86d850e1376
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-exact-repair.json
    sha256: 8cc131df4dbcc516b33c13a1130983cb3bd262a9785138991299bb701a2d837c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-exact-repair.txt
    sha256: fbf7f918c8ba49b39a6f5bfcac27a31d17bad75c26a57bb7f069a5752581e435
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-final-G1.json
    sha256: 075bc62f35627d9dd3ca5f84571806327860238fc5f1fc9acd0b24a644ad9c9d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-final-G1.txt
    sha256: 7a70acd76f314122cce37877fff0d48643e41c5fd9e133b87ea5120a459f4382
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-final-direct.json
    sha256: a1561a034ecac686ca476087f8f1ab282a8d7e4ae5c96aa7f0158301277b69e3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-final-direct.txt
    sha256: e34a821d1c4ba80a65d835c8b79bbba21845e9468113be10ee9ce75add866b22
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-import-repair.json
    sha256: 1a3b5e6ca39fcf00e361570d83328c04fee5c122ff8fc55d442add6c8cfb0f29
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-import-repair.txt
    sha256: 634dda3a74b63407d792cee9da99ec8712a2f9bfe2f5992d2b853314576d5244
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-instrument.json
    sha256: ad4546090f884a551984aa06e692b2172ebd58befabadf830d5c9570017895d7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-instrument.txt
    sha256: f46318c790caa93b69dcf285b4e7713312da9f257bc990333075c93642c1ab6a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-patches-repair.json
    sha256: ddd0e28106eca5b3def35b786d1eb23f0ed53af258283253a53aaacbf4a67aeb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-patches-repair.txt
    sha256: 1fecd88b56bbe02f5315de0dc8b3c7260585940c816744b4bc3e326e3d6a9bb2
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-patches.json
    sha256: 28e9d0bbdb55b6fdafeba0550e3ce0592dfcc53bceff2cb3fdcb62056d88528d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-patches.txt
    sha256: ac000ce389225cc6c01d020294da51a13190a3a70f6cc7227d3a6f5f41a4c12d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-repair.json
    sha256: d091aee1121f61cc3ede32357160efff7c77e1ff912e2f3404a37b5cc77df267
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-repair.txt
    sha256: f6d8e8edab2e251a5891407d58517f4dd0b64d556fdb9c0a44924500d8802aad
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-stable-G1.json
    sha256: 37613869f62fa37c1b67d4778f9049e9c2d78575e572814b312c0441345744ab
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/move-stable-G1.txt
    sha256: 1aa13e985258e6e30de3477d119b1cdc176088898c9302e888f9985fa2e6e3e4
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-complete.json
    sha256: 0c01855784f9299ca949e809280fefdfee007dea8832ede1b87449895d445acb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-complete.txt
    sha256: be93af1649f0cd4fc6fff766cc2ecace8eced7c8bc38f7505ce96301b86d4af9
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-fast-repair.json
    sha256: 7dc1e57e8369e3d2d7635655d1da62a8d72b4f411936214ee5a74e9a2b977b31
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-fast-repair.txt
    sha256: 4e5a1cb8c88c61bc64f177505295cc5cddd359d5128235c88df3436558e85979
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-fast.json
    sha256: 51c72fe78e4423ffc025cffe62ff4efbea75c56b13519241a4f740d0bc0168ff
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved-fast.txt
    sha256: 3e9b7e539d0eca04174f1d017fab493383798caa5e1af91f798241a23ce58df4
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved.json
    sha256: 942458ea68e84c2b105a788bfa4bb94d375baadea0a8402530e170fc5eba29fc
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/moved.txt
    sha256: 73cacf7f8197d5b6ff8a7c5bc248ebcb085e6a99a380e980869b3e00e6bed593
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/mutation-controls.json
    sha256: e5e38ccef0d0cf4fc0eac219c2bf1d52ef798af913aafab7876d7f6fb9e3f41a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/mutation-controls.txt
    sha256: 4381655835b842c433da52a3668da3f8f9fa3d059ccfcb9668521ff5fedd213a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py311.json
    sha256: 0171fa835f631363d049a822a99f858e36c515c107ce20e571d79f30d4c95f2e
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py311.txt
    sha256: b481153088e72d3a1814c039e52b7ddf50ccd417869ab480b519e362666fbd10
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py313.json
    sha256: d4e1266f3e99978985548205fd8dd51af150516ffb06603081d48862480ada34
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/portable-py313.txt
    sha256: 76166556abff2e870b5035abdc02b85930deda14eddfe45b34e80abe54622b86
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/rename-repair.json
    sha256: c563a1501afe5dcbd0401ff2953e829207d59b6c107bcd9ea2eb5d855302417f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/rename-repair.txt
    sha256: 02a8849aef0686ddc146c0f69dbc0d5f8ef26c86ab2985b9660a8cd502c2041f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/rename.json
    sha256: 049661e72d5c9528e3fe4ef69b4327abeb7cce15b9d56e8437a7dd6fd23da19d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/rename.txt
    sha256: 8b40dbe857022b5ceb75d83d838b2c1743857117bb37dae81244f5b076d6d986
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-authorization-status.json
    sha256: 765dfbd1e316298128efba73ab7f49dd2b39514a4d09e8e310715a91e55096ec
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-base-primitive.json
    sha256: c4442dbfcb86458271c9fd27982d0a238283b9fa670b366ea6d2ab657931c181
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-base-primitive.txt
    sha256: 4ff938c528c2df9489d12fc3d28b2dadbf86f84d8c9b9347656a5a13f7be3e16
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-impact.json
    sha256: 16984f050559e793ec728bdc9ab519dd98877eae8e6b7242f25fe5a8775b7ff3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-impact.txt
    sha256: 141b5c5d92cf62dd8a4a648b8c7d706aca30b968b57ddde27da3e3b2403ab2d9
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-lint.txt
    sha256: 119d99aaab822d44344b8c7d959460995f7aa5353187d12a7c0b88f32da87afe
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-post-fix.json
    sha256: bff9abad05c3633c006b262c94928870f1e28765d6bb7e0f5dd4efcfb94df66c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-post-fix.txt
    sha256: f19ce2a1f4867586c02142974b82247ff1dfaa59573b23cacabdb1678957a22d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-pre-fix.json
    sha256: 39824467379b7819220893c30f2c94eb77190186deea6ba27a1bc2db9e5486d6
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-pre-fix.txt
    sha256: 31a7340aaba8033a515d7b93e789b12ff23f933a4b8872bc4c1c98bf69fa4175
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-py311.json
    sha256: 957cc94e1216860b35514cb6830a7ae9a1660e21fb05abf3d9c05a55ec74f417
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-py311.txt
    sha256: 677cfa13a01e69ae30eb199283fd50e6d44cfe36dc14a0493c1cfa4ff178a308
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-py313.json
    sha256: db947fd394ab6eaf03ce690432d63e5915c202227a8d2de4c04607eb6f9bfe07
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-py313.txt
    sha256: 3114fc0ca1fb335de8567aef897b61e893dc8f24622f396c4e4d83cd779e9bc3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-witness.json
    sha256: db6d80e9e990a9300b3655c214855a43a7a38bad8d4f58a52c04c1103a09cc0c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-default-witness.txt
    sha256: 74e1b12e3d943f01ae5d2da3095e7b6a175b4c05ea617dc37344976ed3187e98
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-final-G2.json
    sha256: 934ceb19ba7bcb46c766a0029c7dfcf2d00a106c8240d66bd2fe39c1ed34912b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-final-G2.txt
    sha256: e41780744dbaa99c06cf22b2abe36a9f9bf1e0fa92d057fbc64d547ca23886cc
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-impact.json
    sha256: 5e18daae24fb06de7d2e8ae52b987ade9fcd6623d0f4849920703335cda86522
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-impact.txt
    sha256: 8565ceb78ce40c0f015d93647f13c72c42274d0de4fe3f5b749607e197b8cd11
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-lint.txt
    sha256: 119d99aaab822d44344b8c7d959460995f7aa5353187d12a7c0b88f32da87afe
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-manifest-check.json
    sha256: 656f8558c36c9b95db8be5af6b7c604098caae87ae7f610b41276169b4b829b0
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-model-refusal.txt
    sha256: 627c4d9e2c80ffb920bbef99d6b7cfd7efdf454b0bc9512d8824e1e01f0adfb5
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-post-fix.json
    sha256: f88b4ff5aad25d5f77da339c25d9b4c1b2fa6a52e696118f2687682647207ff2
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-post-fix.txt
    sha256: 1c235c0f457770a0a9ed9126d6edc47849386f3d78314dc599030ccebcc8c062
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-pre-fix-guards.json
    sha256: 5404cc941524e01fa84deac75ecec435842ad3eb72bdbb324e82f3168904991f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-pre-fix-guards.txt
    sha256: 992614bb0acc380aea59349d68e8c5f40e1754e1ae8cc0d14db77d47bb460b02
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-pre-fix-primitive.json
    sha256: c5595a4bff5f39a039e9bddabf65d63ca9c912e08d158109b7ac2a6fc3259d68
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-pre-fix-primitive.txt
    sha256: e614b8aeae64ace85ec8c4b6ed6956ed42b5c62effbb93551556f507432f3008
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-py311.json
    sha256: 8d4b141cd2f8e1eeaf7e16e94e6ba7d44c7c77477ee582bafaa12676c3f590c3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-py311.txt
    sha256: dada9c165fe9f06db4264f4da85e4844aa4769e2b32470fc6bfeb161f356528f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-py313.json
    sha256: 50c8a57e9f65a50a49bc9d23f594a4aedcd4fc655b522cbeecd64e0f4d0f4fbc
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-py313.txt
    sha256: f0f2b670fb0400e2bc8028eacfc2471f49e9c8b93be842151db3c7dc89cd99e6
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-witness-consumers.json
    sha256: 11f03af2d79eaf2400bc0555f300a5bdef397471eee6292be074bb264f06fb1a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/review-witness-consumers.txt
    sha256: d00f171dfa553c5b7ef020ad24dcdb9b196771ad3400832e952ee69cf794f183
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G1.json
    sha256: 1ed96c67868eb1228cca36f1c7ff54e4fda5d23a20e0ad8c59716f1c30887382
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G1.txt
    sha256: ccf49f67870a012a16e92cd083907c262c51113d07d9bbb87fd276aafd725a85
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G3-G4.json
    sha256: da422936b123a6b32806817b17761c44eaf264863ae9adb96fd3c3101f92ce5b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G3-G4.txt
    sha256: dc11a42021f3d840bfd6c695d27463aa206c6e055232f5701ae1b7ce3525886d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G5.json
    sha256: 41163f52c0711d4fac33c223806b6fcce5c84644465d5035520919ebd672ca75
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-G5.txt
    sha256: 510a88cc7de66d6427897c0c6bafe8da8d669af79cf888a6d6814d545f3b06a8
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-direct.json
    sha256: 2e536e80211dfc308321830942e68ce38c681f59e54e3c48448bf1536abd0586
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-direct.txt
    sha256: b41613b6c1985ca314fa7f9474ece51f37deb64d4172c5ed7e365512c1ea5188
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-final-lint.json
    sha256: b9b017fed9cc0e4fe592c2ec9e951418c34bc60a2e455f8348b2275868b57cc2
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-final-lint.txt
    sha256: 9aa5143644f385318b578b1366c2fc23fae855dd092429b2d64434a3aeeffb3b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-lint.json
    sha256: 22fb5947009fb570cfebbf48b08f967e423995a81cc232d39d3d49ec0f252c81
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-lint.txt
    sha256: 13b2f5f354891d503d58ec1f3122dcfbadc6262a53f55b93a5d83f2ff3cedd0a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches-repair.json
    sha256: 911bed67722a045bea585c90aba2ff98c4ea1a982113704a9663ce89390fa280
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches-repair.txt
    sha256: 29dd6b8067a83690f5fe3d3026ce5098e6d622a72684228eee0cc945d49dc05b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches.json
    sha256: 33d98b3336752fbccef9a2a726937bf1f7a63a59036748a569148c45cbd7cf9e
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/routed-patches.txt
    sha256: d0b95f5d5e017dbe089853e3b02cf726651c5a79c7e02ab080adafcf8e767d49
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A1-A2-A3.md
    sha256: bcd41ecb8dcce8e7a9131c1c4f6af4ea05d90467c4605b70d8b564df68c50590
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A4.md
    sha256: ec7082a61710e42a1a49a20d951a4c50c904e9e5fa567f2746058a65d3667f4a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A5.md
    sha256: 1c045b340d1fa0bf411e583832b4e4f6ae9d0b365a48c1b2c9ab9f38f589306d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A6.md
    sha256: dc48fe2c66a38e3e0a47fa8f5a296d1a0d7b7fa352bbc8c143eb1df7097de400
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A7.md
    sha256: e337073ca5b36b15c8a6e5a51166b0cd81ee318ed918cc251c060acdb0df42f9
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A8.md
    sha256: c0f621501e41b172b0852e358eef58fb1c2cbd10ae8e35d3a9b4d62e2a5f6da6
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/A9.md
    sha256: b51b596af8d3e4fe67a2389899e3c5461802a866af47ef15c4548a89d21f3d82
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-approval-snapshots/initial.md
    sha256: 8007e2db1cf9cae09454fb29494d06b654dc1b830bab27414c828ea06509da6c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-budget.json
    sha256: 5b5b8c14a380073868298834e12bba08a12184d85e2e37c53b784d02d60ec57f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-commit-compare.json
    sha256: 17f44c8c1187f78dc0f153ea25012d9f8a2e420c92a47eb51f8fe7b14aae8881
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-document-moves.json
    sha256: c1acf13ffd201aa3c62788d18de3248b78f466ccb6176a8fad861ab3e57b7dbd
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-final-budget.json
    sha256: 8a58676c64f5590e3c0be63845a2ac1532c275544a9f8b1273990ba966d6fbaa
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-final-compare.json
    sha256: e5be29b0eaaea7d678daa6b935fd37c82917bfa39b7dc292e36595d3fbc9e04a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-final-frozen-controls.json
    sha256: de5a7579fc0d309b108cf2e15730caf14f047a3508d8470fb799b0b6ed560097
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-frozen-controls.json
    sha256: 9227fbea48c36b514e2dec78f95df1e991bc960c693500200f19eeb99a87ee12
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-manifest-adaptation.json
    sha256: 8e45d5a4966a980eceaa15aa649823eb7c6054f0f6e809b8fb252621a3773616
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-moves.json
    sha256: 94f26c06a88c38a04f53c3fcb157758384d32248d15bd570650e11a4b7d6fd72
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants/control.txt
    sha256: 91f5045ca794a07a80b42f9680728501b041746b7f786d0d033bc555ea7447f8
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants/mutation-report.json
    sha256: 6851bf26d0c12c5f2d3d9b033a78fc72d23bfca173932cc569c929b356f1292a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-mutation-retargets.json
    sha256: c2efd54e32d8d297319983664267dff932e52b7c4bd9415fdaafdf3e8f0642d7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-reviewed-budget.json
    sha256: 90be56e2507a014a43d74ce254f28554bd81bd1c6f2f5bd77beb39ef54c09bb1
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-reviewed-compare.json
    sha256: a101294297ca78a1b43877c3a4d71af6ae3894f83a026260f3d6447b143d7823
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-reviewed-frozen-controls.json
    sha256: cc19cc2c4fa1836adc77f3b53fdc63b01c25a9623737895031796fb6b9e1d851
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3-twin-controls.json
    sha256: 1af15bcad289ca209610eff9302de5a3317b61dbd85bc43bd4267aaadffcf671
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-base.json
    sha256: 4d0742bfedbb440eb5223b39fbb0e67581263fdd2f67df6d961b8ae3c7b0bb7f
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-final.json
    sha256: 194f1a285527447641aabfce8544ba6c8233cff7399ef703c99eb81d4cfd7b8e
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-head.json
    sha256: beeaa1d30d389064e13920825ed29fc82c52c4c8f723a8c6a4a92fffeca244d0
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-reviewed.json
    sha256: df69e5200e22a757746eb1683d4eac4cb37ad380f9bdf648360aea5c64f106fc
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-amendments.json
    sha256: afd1152a275aab6d703b697dc5f2a3aa2a524f7e10fbf8a66c4062fd30ae4ebd
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-approval.json
    sha256: daf50bd78b9e1021dafa4149f4cf4785d30060854b5d9b37cb2651ff0223af63
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-codex-prompt.txt
    sha256: fb53345f23421881aa2b420a02f9d90653250bcb85bb46fc82741574e8bfdcb1
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-codex-repair-prompt.txt
    sha256: 4e74890e7eccd8e547ebf09df60a1094ae2dcfce3675ec3f0816ee8354fa82de
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-codex-repair-review.md
    sha256: e85200b161b0933b3181ce912294aef604f7c9be42cdad423465f258325d1f49
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-codex-review.md
    sha256: 4ab88388050ef32bd9c6e1b737ac02a192c33f356e49b6b114e2675ce4157902
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-pending-review.md
    sha256: 4cddcd6511ce1ce52e858df5d2038dfba1765a5bc3ef14aee26222ddf89cc1ce
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF3-spec.md
    sha256: b51b596af8d3e4fe67a2389899e3c5461802a866af47ef15c4548a89d21f3d82
  - path: .gnd-planning/milestones/code-refactoring/notes/shim-inventory.md
    sha256: b417b6fe9c2248c848256658fec649332aab1a584cc8e0510f35069adaa76a83
  - path: .gnd-planning/milestones/public-launch/migration/b3-files.json
    sha256: c381403dc896e4286ccab927e28f2819374d7b4a766654114f0dec80e344883d
  - path: tools/gnd_layers.json
    sha256: b76a61ba574e4764d4b0fd50f5a1cd2f07ea4e119e4615aa204c8ba7085c98e7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/final-scaffold.txt
    sha256: cbe7094bb8f2e52a34d8f0330a669735b4b16de268e9729df3965e165c11eba3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF3/final-scaffold.json
    sha256: f8868ee4ead37ba0872d3fdfaa9eec67a6b8bea9ae57dedaf0e25e6c10238e01
---
# Claim

The selected RF3 gates exited 0. The original fourteen-module core runtime SCC and every new home are acyclic; all sixteen RF3 layering cases run without xfail. The fixed original core-layer private-import cohort fell from64 to20, below the approved target60. The literal dynamic semantic_spec -> terms edge remains measured and no longer closes a core cycle.

## Authority and decisions

The owner requested process-phase RF3 auto on2026-10-05. D1-D8 and amendmentsA1-A9 are explicitly delegated agent approvals, not a claim that the owner read the artifacts. Initial spec SHA8007e2db1cf9cae09454fb29494d06b654dc1b830bab27414c828ea06509da6c was recorded before implementation. Each later exact approval snapshot is retained with its SHA in phase-RF3-amendments.json. Prose and existing frozen behavioral cases are the selected instrument; no optional spec panel. Approval to send the RF3 prompt/source/diff to Codex was separately requested after automatic review refused the external payload; the owner replied approved. Native gpt-6.1-sol was unsupported and returned no review opinion; supported gpt-6-sol/xhigh completed the initial and one bounded repair review, read-only with stdin prompts. No global credential configuration or repository .env was read or executed.

Source authority follows RF0/RF2's named handoff and owner attestation; no reachable source remote was supplied. Current changed source invalidates prior release/certification claims. D6 adapts26 existing curated rows, retaining before/after bytes, modes, digests and reason. The review repair changes no further curated rows. units.json and the distribution guard are unchanged. This does not transfer source-owned questions or enable a publisher.

## What shipped

The rename commit eff8693 precedes the verbatim dependency-closure move4415327, followed by routingc9efd66. Review guard repair355e2ae and its captured-default follow-up change tests only. Historical qualified type/callable names and exact alias identities remain pinned; moves and later routing are separate claims.

- errors holds shared exceptions/issues; documents holds Model, DeonticNote and shared parser constants; values holds scalar identity/literal sentinel and separate digests. Divergent algorithms remain separate.
- universe holds lookup/classification and the explicit primitive_for(..., variant="truthy"|"strict") interface. Existing model and population resolver wrappers preserve their different prior choices. One shared derivation-term ContextVar retains identity-based caching, aggregate lookup and finally-reset behavior.
- extensions holds the calculation closure and public effective_view with unchanged ordinary/exact/opaque selection. branches holds registry descriptors/trace; applicability uses the lower actual homes. semantic_registry, checker and references retain compatibility aliases. Model intake and reference orchestration are co-located to remove the backedge without RF6's model-query package split.
- anchor_identity, anchors, refscheme, vocabulary, report_schema, manifest_paths and semantic_rows hold lower dependency closures. Adapter, bridge, transition and rendering consumers use their actual homes. Layer responsibilities are explicit; no allow-list entry was added.
- Source scans cover all fourteen new homes. Frozen packed inference inventory remains intact; the explicit RF3 successor adds extensions and public alias recognition to the actual graph. Actual-home visitation, absent-home refusal and planted direct/transitive imports are discriminated.
- Independent review repaired the stale adapter.checker test lookup and both blind witness evaluator guards. Existing adapter stimuli/expected nodes and primitive assertions remain unchanged. New regressions prove interception of the real effective_view calculator and each moved private/public lookup; prior compatibility and term sentinels remain active.

AGENTS/CONTRIBUTING document layers and shim use. Nine packaged skill module citations remain at their old importable paths. The normative process-phase twins are byte and executable-mode identical and unchanged.

## Criteria and measured budgets

| Criterion | Current-byte result |
|---|---|
| RF3-C1 / SM4 | Original core SCC plus all new homes acyclic; original/current core-layer wrong-way edges absent;16 RF3 layering marks removed; allow-list0. Four peripheral SCCs remain disclosed under RF0 D10. |
| RF3-C2 | Fixed original-layer private imports64 ->20, threshold<=60; all private sites242 ->198; wrong-way27 ->8; modules148 ->162. |
| RF3-C3 | All804 semantic registry owners resolve to functions; nonexistent-owner dirty control rejects. |
| SM1 |454 native characterized pins pass;496 pin/core/move cases pass under3.11 and3.13. Named original goldens, RF1support, RF2successors, frozen v71/v72 archives, units and distribution guard unchanged. |
| SM2 |232 ledger names plus2 document exports remain identity shims; committed move bodies preserve their source segments. Actual moved lookup patches observed; repair regressions red before fix, green after. |
| SM3 |Actual source-home scan coverage and public/private planted inference rejection; twelve existing semantic mutation stimuli retargeted at source locations, ids/expected-red unchanged;12/12 killed. |
| RF0-OQ5 |Literal dynamic import is retained in the graph and acyclic; original-site annotation points here without widening RF0. |

Commit comparison8ff996f..41e69fc:38 production files<=90;5948 moved lines<=10000;7935 added minus5948 moved-in=1987 non-relocated<=2200;619 handwritten Python test additions<=1600;74 non-evidence files including completion record<=150. Final record/docs add no production/test lines. Original700 non-relocated ceiling was refuted and amended before routing (A6); blank lines and required aliases/qualified-name assignments account for substantial added scaffolding, with overlapping categories not summed. Metrics and comparison bind committed source; review changes no production bytes fromc9efd66.

## Independent review and regression dispositions

One reviewer is one reviewer. The initial reviewer confirmed the core graph,64->20 cohort, zero allowance, disclosed peripheral cycles,1987 arithmetic, alias identities, committed move body equality,804 owners,26 manifest rows and frozen artifacts. It returned HIGH blocking R1 and MODERATE hardening R2. Both were independently reproduced before acceptance and triaged before repair in F8/A8. The original review is retained verbatim except declared machine-path substitutions. The reviewer could call read-only reproductions but could not run pytest without writable temporary paths; implementation-agent gates supply runtime evidence.

R1: the unchanged dependency-graph mutation control raised AttributeError before assertions. Three neighbouring unchanged primitive tests also failed, while the RF3 source base passed all three. Retarget checker.check and defining extensions calculator/obligation without changing expected answers. R2: both helpers patched a facade alias while actual effective_view still calculated. The two real calculator cases plus eighteen moved-lookup interception cases failed before repair; the R1 regression also failed. The retained pre-fix run has22 failures and28 passes. Post-fix53 cases pass on each interpreter;124 combined core/review controls pass. Existing four B20 independent/comparison cases and336 affected consumer controls pass with strict sentinels. This establishes the observed guard effect; it does not establish all proof behavior.

The single bounded repair review and its checked neighbours are retained separately. It found a remaining captured-default calculator bypass: evaluate_derivations functions retain their calculator object in the default argument, so patching module globals alone cannot intercept them. Twenty-two independently red cases prove the bypass through both facade and defining-home entry points. A9 accepts this within R2’s hardening scope and patches those entry points themselves, preserving production signatures/default objects. Final146 core/review cases and75 focused cases on each portable minor pass; four B20 controls and336 affected consumers also pass. Focused runtime evidence covers the follow-up; no third review is run and the reviewer opinion is not claimed over subsequent bytes. This is the last allowed round under D8; broader questions stay with their named owners.

### Convergence ledger

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| Initial |1|2|2/2 RF3 stale instrumentation|1/2|HIGH|Repair R1 blocking and R2 hardening. |
| Bounded repair, ac0475f..355e2ae |1|1|0/1 newly introduced by355e2ae; captured-default path was omitted from guard coverage|0/1|MODERATE|Extend R2 hardening, reproduce22 red cases, verify runtime; stop at declared two-round bound. |

This is a single-reviewer disposition ledger, not a panel. Both review rounds and A9 runtime verification keep their distinct byte boundaries. No completeness finding is repaired in-phase.

## Refactoring review

**What did this phase's work reveal about existing structure that should change?**

**Refactors EXECUTED:** dependency closures formerly mixed data, lookup, descriptor and evaluator ownership and made the core cyclic. The fourteen homes, explicit resolver variant, public effective view, registry facade and reference co-location separate those responsibilities behind the same characterized/direct gates. The temporal/correspondence canonical-row dependency moved to semantic_rows without merging divergent encoders. Test patch ownership now follows defining homes; observed-effect controls catch alias-only instrumentation drift.

The remaining large model intake/query organization belongs toRF6 (RF3-OQ2). API/diff, assurance and synthesis SCCs belong toRF4; session SCC belongs toRF8. Consolidation of the two witness helper guard implementations is deferred to a separately scoped test-support successor, since broad fixture-helper cleanup is outside RF3; preserve their separate fixture families and answers (RF3-OQ3).

## Boundary -- what this phase did NOT establish

No new semantics, CLI flags/schema, tightening, ModelIndex/constraint-family registry, source-owned OQ transfer, broad historical repair, release/publisher/certification or acceptance claim. RF4 owns peripheral cycles, RF6 owns remaining model-query split and standalone PyRel format decision, RF8 sessions. Pins prove selected preservation, not all-model correctness; local macOS runtimes do not establish other OS results. One reviewer is one reviewer. Required plan/close panels are not replaced by this review. Co-change remains unavailable (RF0 D3). Historical source/release certificates describe older bytes and are unavailable over this refactor.

The original layer-wide no-SCC premise failed for assurance, whose explicit RF0 D10 owner isRF4. A5 narrows only that SCC criterion to the original RF3 core plus new homes; full original/current core-layer wrong-way predicates and fixed private cohort remain enforced, with zero allowance. The remaining cycles are measured, not concealed. Broad default/evidence/census/distribution/native/provider/historical proof suites were not selected; their prior changed-source claims remain unavailable. The required independent Codex review is the one explicitly selected provider operation.

## Open questions

- RF3-OQ1 -> milestone close: reconcile original layer-wide SCC prose with approved RF0 D10's explicit assurance/RF4 assignment and A5. The plan is not rewritten here.
- RF3-OQ2 -> RF6: remaining model intake/query package organization. Preserve reference validation/identity order when splitting.
- RF3-OQ3 -> separately scoped test-support successor: decide whether two fixture-family no_evaluator helpers should share an observed-effect guard primitive.
- RF2-OQ1/3 and RF1-OQ3 -> milestone close: divergent canonical helpers and manifest wording reconciliation. RF2-OQ2 -> RF6 export/model-query gate or successor: standalone PyRel positional-ref runtime/emitted-byte decision.
- RF1-OQ1 unpaid families retain RF4/5/6 owners; RF1-OQ2/4 and RF0-OQ6 -> RF8 or successor; RF1-OQ5/6 -> successor; RF1-OQ7 -> next actual edit of original RF1support (unchanged here).
- RF-D5 -> first public release afterRF6 plus explicit retirement approval: all existing RF2 and new RF3 shims remain live.
- OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1, OQ-V52-P1-IMPORTWALK-1 and OQ-V63-CLOSE-HELPER-TAIL-1 retain their source-owned authority. No automatic sibling execution or certification.

RF0-OQ5 is discharged only for this measured current-byte core graph. RF0's original boundary remains standing.

## Refuted premises

- Initial final-SCC requirement cannot hold before intermediate dependency moves; A1 preserves rename/move ordering and final G2.
- Accumulated shim inventory cannot count all milestone rows asRF2; A2 retains all34RF2 answers while RF3 has its own rows.
- Formatting-sensitive mutation import strings stopped matching; A3 retargets the same signature/refusal and same expected-red nodes. Frozen behavioral answers were not replaced.
- Proposed resolver name collided with the old signature; A4 introduces primitive_for and preserves resolve_primitive compatibility.
- All core-layer SCCs belong toRF3 was contradicted by the assurance SCC and RF0 D10; A5 and RF3-OQ1 retain the failed premise.
- 700 added non-relocated lines underestimated required split compatibility scaffolding; A6 records7935-5948=1987 and revised2200 before routing.
- Frozen inference details automatically cover extensions was false; A7 retains the original scanner and adds an explicit actual-source successor.
- All moved patch sites had been retargeted was false; R1/R2 and independently red controls refute it. A8 repairs actual lookup sites and verifies observed effect. The prior pending-review note remains historical, with a dated discharge annotation.

## Gate output (verbatim)

Commands and summary lines are copied from retained logs. Full outputs are bound above, including failed pre-fix/diagnostic attempts. Log headers declare machine-path substitutions; portable interpreter paths below are the exact executed commands. Configured lane exclusions remain active.

### routed-G1

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py --tb=short
    454 passed in 63.60s (0:01:03)
    Exit: 0

### routed-G3-G4

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_checker_families.py tests/test_model_validation.py tests/test_model_v2.py tests/test_population_load.py tests/test_model_guarded.py tests/test_derivation_rule.py tests/test_derivation_covers.py tests/test_public_semantic_adapter.py tests/test_public_semantic_applicability.py tests/test_public_derivation_evaluator_controls.py tests/test_reference_population_corpus.py tests/test_transition_corpus.py tests/test_transition_report.py tests/test_transition_mapping_totality.py tests/test_model_verbalization.py tests/test_measure_offline.py tests/test_extract_manifest.py tests/test_v70_phase1_adversarial.py --tb=short
    1326 passed, 3 deselected in 65.58s (0:01:05)
    Exit: 0

### portable-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py tests/test_rf3_core.py tests/test_rf3_moves.py --tb=short
    496 passed in 70.84s (0:01:10)
    Exit: 0

### portable-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py tests/test_rf3_core.py tests/test_rf3_moves.py --tb=short
    496 passed in 71.17s (0:01:11)
    Exit: 0

### coverage-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_core.py::test_resolver_reference_modes tests/test_rf3_core.py::test_plain_view_preserves_population_identity tests/test_rf3_core.py::test_analysis_reaches_the_shared_validation_cache --tb=short
    10 passed in 0.15s
    Exit: 0

### coverage-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_core.py::test_resolver_reference_modes tests/test_rf3_core.py::test_plain_view_preserves_population_identity tests/test_rf3_core.py::test_analysis_reaches_the_shared_validation_cache --tb=short
    10 passed in 0.14s
    Exit: 0

### review-default-pre-fix

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_review_regressions.py -k captured_default --tb=short
    22 failed, 21 deselected in 0.20s
    Exit: 1

### review-default-post-fix

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf3_core.py tests/test_rf3_moves.py tests/test_rf3_review_regressions.py tests/test_v6_phase2_adapter_mutations.py tests/test_public_adapter_primitive_controls.py --tb=short
    146 passed in 6.58s
    Exit: 0

### review-default-impact

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_public_v72_semantic_owners.py tests/test_public_derivation_evaluator_controls.py tests/test_public_adapter_derivation.py tests/test_public_applicability_obligations.py tests/test_public_derivation_cost_mutations.py tests/test_reference_population_corpus.py tests/test_rf3_moves.py --tb=short
    336 passed, 3 deselected in 38.37s
    Exit: 0

### review-default-witness

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_public_v71_witness_corpus.py -k B20 --tb=short
    4 passed, 259 deselected in 0.30s
    Exit: 0

### review-default-py311

    $ /private/tmp/rf2-py311/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_review_regressions.py tests/test_v6_phase2_adapter_mutations.py tests/test_public_adapter_primitive_controls.py --tb=short
    75 passed in 0.85s
    Exit: 0

### review-default-py313

    $ /private/tmp/rf2-py313/bin/python -m pytest -q -p no:cacheprovider tests/test_rf3_review_regressions.py tests/test_v6_phase2_adapter_mutations.py tests/test_public_adapter_primitive_controls.py --tb=short
    75 passed in 0.85s
    Exit: 0

### mutation-controls

    $ .venv/bin/python tools/rf1_pins.py mutate --out .gnd-planning/milestones/code-refactoring/evidence/RF3-mutants --only M-HELP-canonical-json-gnd-extract-anchors-canonical M-HELP-canonical-json-gnd-transition-canonical M-HELP-identical-candidate-gnd-popvalidate-object-types-by-id M-HELP-model-digest-gnd-population-model-digest M-HELP-model-digest-gnd-references-reference-model-digest M-HELP-sha256-hex-gnd-extract-anchors-digest M-HELP-sha256-hex-gnd-population-content-digest M-HELP-validation-issues-gnd-exp-conclusions-validation-issues M-HELP-validation-issues-gnd-exp-spec-validation-issues M-HELP-validation-issues-gnd-extract-manifest-validation-issues M-SEM-check-coverage-anchored M-SEM-resolver-is-true --jobs 2
    Exit: 0

### review-default-lint

    $ .venv/bin/ruff check src/gnd/admission_validation.py src/gnd/anchor_identity.py src/gnd/anchors.py src/gnd/applicability.py src/gnd/branches.py src/gnd/checker.py src/gnd/correspondence.py src/gnd/documents.py src/gnd/errors.py src/gnd/extensions.py src/gnd/extract/anchors.py src/gnd/extract/identity.py src/gnd/extract/manifest.py src/gnd/extract/refscheme.py src/gnd/extract/vocabulary.py src/gnd/extraction_scope.py src/gnd/judgments.py src/gnd/manifest_paths.py src/gnd/model.py src/gnd/model_verbalization.py src/gnd/population.py src/gnd/popvalidate.py src/gnd/proof_bridge.py src/gnd/redaction.py src/gnd/references.py src/gnd/refscheme.py src/gnd/report.py src/gnd/report_schema.py src/gnd/semantic_adapter.py src/gnd/semantic_registry.py src/gnd/semantic_rows.py src/gnd/temporal_guarded.py src/gnd/terms.py src/gnd/transition.py src/gnd/universe.py src/gnd/values.py src/gnd/verbalize_population.py src/gnd/vocabulary.py tests/support/public_adapter_mutation_controls.py tests/support/public_v71_witness_corpus.py tests/support/rf3_inference_inventory.py tests/support/v71_witness_cases.py tests/test_public_adapter_derivation.py tests/test_public_adapter_primitive_controls.py tests/test_public_applicability_obligations.py tests/test_public_derivation_cost_mutations.py tests/test_public_derivation_evaluation_complete.py tests/test_public_derivation_evaluator_controls.py tests/test_public_v72_semantic_owners.py tests/test_reference_population_corpus.py tests/test_rf1_layering.py tests/test_rf2_helpers.py tests/test_rf3_core.py tests/test_rf3_moves.py tests/test_rf3_review_regressions.py tests/test_v62_phase4_aggregate.py tests/test_v70_phase1_adversarial.py
    All checks passed!
    Exit: 0

### routed-G5

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_gnd_arch.py --tb=short
    61 passed, 1 deselected in 8.29s
    Exit: 0

### G6 committed metrics and comparison

    $ .venv/bin/python tools/gnd_arch.py measure --out .gnd-planning/milestones/code-refactoring/evidence/metrics-RF3-final.json
    Exit: 0
    $ .venv/bin/python tools/gnd_arch.py compare 8ff996f7cf0d17bb08f539bca1f4a116ed839fec HEAD --out .gnd-planning/milestones/code-refactoring/evidence/RF3-final-compare.json
    Exit: 0

Measure ran at 41e69fcdf75f8c8bc603b93e7e9f9343bdd6916d; compare output binds that exact commit. Source files are unchanged fromc9efd66. Twelve selected semantic mutations:12 controls passed,12 mutants killed, no survivor. Budget assertions all hold; arithmetic is bound in RF3-final-budget.json.

### Final G5 after record and discharge annotations

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_development_scaffold.py tests/test_gnd_arch.py --tb=short
    61 passed, 1 deselected in 9.23s
    Exit: 0
