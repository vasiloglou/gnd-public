---
milestone: code-refactoring
station: "phase-RF2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RF2
date: 2026-10-05
gate:
  command: ".venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py --tb=short"
  exit: 0
  output: "457 passed, 16 xfailed in 70.41s (0:01:10)"
  note: "Same selected nodes exit 0 under Python 3.11 and 3.13; focused consumer gates, source-base controls and mutation results below."
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner request or separately configured CI selection"
  reason: "Full default, historical evidence/census/distribution/native/provider lanes were not selected; RF2 runs focused current-byte controls."
source_base: f5a83186f7c2215ac2b2afb0a010c2294eaa433a
move_commit: 16f08eafdcf27b6373a1a3e8c82e87ad879c75f2
prior_record:
  path: .gnd-planning/milestones/code-refactoring/006-phase-RF1.md
  original_sha256: 77d73913a59cd49431e475edb173869c52ac21057ef5521e3b9795c8dddefd21
  source_commit: f5a83186f7c2215ac2b2afb0a010c2294eaa433a
evidence:
  - path: .gnd-planning/milestones/code-refactoring/006-phase-RF1.md
    sha256: 8c47928fc5a6b4df68377c53352a0ba5b2e38483446cdff6aefbb6299764135a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G1.txt
    sha256: c169a487e99d275f530a70f7d6452eb30323e36cc0e0cfaf78ef13d1b300dce9
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G3.txt
    sha256: e8262f6726e8775ce75b5109d3b758422dbe695ec3a8de6bf3c098ea1e858250
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G4.txt
    sha256: c282cd7b14b5d0d7d3480551b84d8e32dfb7f4cecbd961bec5efe295c1cf0bd7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G5.txt
    sha256: eaf2382ceb378c1be37e1f6f0ec6ddd3f652a682bfd2d89433bbc3bdc2705d89
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G7.txt
    sha256: 85f69d492db54d3b1e1d4b93263db43a2f8e9a5aaaa8bd974ceb17ee21eb5cda
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-G8.txt
    sha256: 10ca8b2751045a9c24f0e0aaa740a540bb25b597d147337ac4596b12c11cc826
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-amended-controls.txt
    sha256: 3b42c80a5ba5073be8ad012253acbb4a7621db969a7fe3f16e68d9f1d7d383bc
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-ast-interpreter-pre-fix.txt
    sha256: 87826c85a64a5c05c3b39d16055eb26b27ad79a32b7a4c8519da1f0ae7ae8dae
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-baseline-green.txt
    sha256: 3fd48295120ae56a60c0dcc37725af194def09a74b207cfce4afa020691af687
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-baseline-pins.txt
    sha256: 838b05eb4aca2e2fde12868ce611a24515821fbcaf08eaa30be93bb00a301e35
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-baseline-session-clean-env.txt
    sha256: 5b3ca92d8568a62c44003d72a8f6e0c96a9bd8915946e7ff71b0b005b092e3fe
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-budget-preview.json
    sha256: 6c5f7cf6e57f47feb8cab55e8398335986f4e987dba5264c2d642533252f1dfa
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-commit-budget.json
    sha256: 6a5b47e333ce035defe2049f8221268f6cae8c8fd5f9f49e84a9515070bd9023
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-commit-compare.json
    sha256: 97055cafba7e8a6e98c236021fb5d133c33b4b66c642b6f2377aa16662e24341
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-digest-predicate-predecessor.txt
    sha256: 7a31e66378c8cfe7c15128f94cc1506ce059a413da978d80115e1e55e5e976e5
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-direct-controls.txt
    sha256: a3872299b77b109eb10442b7ec8a15871b2d460ea87f15d6df83ebaa483043f0
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final-budget.json
    sha256: f9d0807f2e775ef3134055e2a4f65f7e4c67b28d2e0a033c4907865fc66438b3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final-direct-controls-v2.txt
    sha256: b7adf73415974ac9491d90ab35a7c9b7595a556747364f45befd771e4a530b2f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final-direct-controls.txt
    sha256: 94aa33a87f2a9839e5413a2936a70458f70eaf76890157f7a2a7a95a6f4a5b0f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/G7-final-scaffold.txt
    sha256: 5aad25b311ac3e20c40391fbc0c6e9f41af15c12e0d264b8652d0d2daa0f861b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/G7-scaffold.txt
    sha256: 986fdc651756c742c929354ede273276d0662fbfe57a16a136148f6bf0be617e
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/G8-final-lint.txt
    sha256: 58a333ead1f2b986920c1bbdebe378239fc288b75be54d2c60a201252ea84743
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/G8-lint.txt
    sha256: 58a333ead1f2b986920c1bbdebe378239fc288b75be54d2c60a201252ea84743
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/RF2-G1.txt
    sha256: ed9017f9d0b75179a94f094a09253ffb9fe1bce049698174c68bf4666594bb2a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/RF2-G3.txt
    sha256: cdcd1ec5d16c811bec7b8966c82a2ce6ff27ba7e27671d165041f8a3cfc164ad
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/RF2-G4.txt
    sha256: 963cf43faedd31ef70415871b520a981e43271b96d44d93f5977a868ccaa4dc6
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/RF2-G5.txt
    sha256: 57d50eb3ac6bbc917f3e520f9900ca459b7529fbddd9a29015986b09b983995f
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-final/RF2-gates.json
    sha256: 53c63223858c45ca95a2105c8169d6885108e7fc1bcd4d52716d7bc466fb4fa9
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-first-move-controls.txt
    sha256: 5f35e71ef6ed9a8a7fe8a78961b57d166d4390e326ef620c919b9bd7d2560a70
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-gates.json
    sha256: bc582b0dfe098e4f8fedb08ca0dcb3bfdffba1fe3655342dd88f07476323373a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-impact-inventory.json
    sha256: de482710c57549a5df6c7b252507c6da5463e46b9495e3d2bf7e5a3d24f24629
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py311/G1-and-direct.txt
    sha256: 2255db7ebc6b98a786796f3f7f456ce12ff17370523051adda19fabebb338adf
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py311/gates.json
    sha256: 6a5edf03484634829a89660775b5ebf3d9c716b631021160d128707fe964636c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py311/source-base-capture.txt
    sha256: 4052203a885930775308d4af9315d2aa28ec2c1d697a8512332369c0bbe079f3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py311/source-base-replay.txt
    sha256: c76dbb2cb5633e2f061610df8480983f7ad140913e837e67e4c7a38afe82dfda
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py313/G1-and-direct.txt
    sha256: a9697abcfa8d14150b8e532d97e1d8c2fb783376455d07df459b5bce4198e66c
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py313/gates.json
    sha256: 2ca9b5b0473fbc5f080ce2c829d156e915d37862596e5309139a24e4188059fb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py313/source-base-capture.txt
    sha256: ccc2dabd7e92995be5aef251de020f6fff3a3c4c1f486e38f24c8b3179ff8d25
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py313/source-base-replay.txt
    sha256: dcc05ab4c19437f9299faa5ab7a37fa354a1115117ab421bcf159153297f1fcf
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py314/G1-and-direct.txt
    sha256: 39c3006e3f32357a86c441b0a5627fcaddd51224614b61b910ec1f3d5653e364
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py314/gates.json
    sha256: 856335f8a5e00036fee0067f60de2c6f1accc7ac70c0bf85c8673bb9a73521bb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py314/source-base-capture.txt
    sha256: dcc05ab4c19437f9299faa5ab7a37fa354a1115117ab421bcf159153297f1fcf
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-interpreters/py314/source-base-replay.txt
    sha256: 071b9f7d63f17e9e8b17f0033394bd3db6b5c7087df96882cd90c9cf53831592
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-manifest-adaptation.json
    sha256: 9155a8c67f70ffb6c1920257b920f13c8a941ea9a56d2b23421d8b044ff9751d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-mutants/control.txt
    sha256: 73083495e0c37a30f74772e1d5caa6d9fe34784064ebc3c2ee085148a2ac8e8b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-mutants/mutation-report.json
    sha256: 5c6b87cb12ceeced4ad690dcc909e2b32d1f6af7a967038b26f9dd42fad5130b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-mutation-command.txt
    sha256: 71ffd9473aac63aec486b37ca872181e0f81bc05aa62add64f360f762f739ddb
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-mutation-retargets.json
    sha256: e290bce3c5874d8a47f204082d520a8c63612285a2337e441c67719718668d3d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-pre-move-capture.txt
    sha256: 005a2110e74e7bd5a852364c499fba171b176dcebc0f7f6d545dcde053b3c748
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-pre-move-green.txt
    sha256: 4411b877d5771fc1e4342c11d5cada44ce93ed7b3a6de21693ca4dcc3342143b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-pre-move-negative.json
    sha256: 92dd1661b1f3f69157e5d23abf02e7c424819e31ee07540f0d917accb6278de7
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-preflight-notes.txt
    sha256: 7f4056fc7ab29a6113869d3bffc35d36b959502f94804d8e1079d6b067fe2be3
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-review-capture-input-pre-fix.txt
    sha256: a2550e4b9dcdc4eab4bb81480902160c7418e0993b01cce98897a7fa01a09143
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-review-cli-pre-fix.txt
    sha256: cdb48789d5031750557b0310a5408cf46d2983b9ba000acecfb5e8373d0eb5d2
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-review-exit-indirection-pre-fix.txt
    sha256: eff3463fb146ec83eca109ac452876215566a228a0aee3e04aeb09298bb65a19
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-review-post-fix.txt
    sha256: 7558e58b428a8a76fe9a1e75b565a7cc1ce3bc3ac561f8dc622ee04f2a83d7ba
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-review-pre-fix.txt
    sha256: 1e4dc49893f596de0b0ed7509872e6c612cfc2361b4455f9daaf7fee00e74ce2
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-session-diagnostic-capture.txt
    sha256: 29d5f001aad8140574443506f96dc283b28de12c643ec5fcb3e2f222070576c4
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-session-structured-diff.json
    sha256: 31835d228ac9ee8484456e3484647b649b7ab0cd4844927a5e4ceb7fd9d7ad1a
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-source-base-control.json
    sha256: 45599188606406023cf83516f9452a69ba0bc2d1ae2ff701fd060481e14aa41e
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-spec-artifacts.sha256
    sha256: acfde9941f75718cbfbf59718e2817faef0a331d4381e1ea6a0dae0ffd44767d
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-successor-base-capture-311.txt
    sha256: b33f266c49326577e77fad01dfb3cc0257df522f6cb4522153f898e62b96818b
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-successor-base-capture-313.txt
    sha256: b3cd6f550a69ab8b8381518172415201a8777f743dcf0736a375119074300c34
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-successor-base-capture.txt
    sha256: c7fb8c76e4a91cf424c15b844c4477ccf3cd03cdf2cc7477b7b7e3b724829aaf
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-successor-base-replay.txt
    sha256: dcc05ab4c19437f9299faa5ab7a37fa354a1115117ab421bcf159153297f1fcf
  - path: .gnd-planning/milestones/code-refactoring/evidence/RF2-successor-interpreter-pre-fix.txt
    sha256: e3c23492ebd7decba6956d01eb03557f3f6c936469261c4115f9bfa95d152f37
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF2-base.json
    sha256: e49e4e6c5360f5c8102a1ea68773a754e311bd552beee9cd930803c32a14a632
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF2-commit.json
    sha256: 280c89c49efbbc17d3d82c0b0769705eb48e09547bec970f01afe4dd3f1ece20
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF2-final.json
    sha256: af9d40e1e433a30c1316974dab60e325aa7e69c816b951daa860463e67c98352
  - path: .gnd-planning/milestones/code-refactoring/evidence/metrics-RF2-worktree.json
    sha256: 8ddda2f54c405338264a2c6835c0be52298481dfcfaf0611e004b6736f1bfa7a
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF2-codex-review-repair.md
    sha256: 77a02455dadb716829de781eb0c97be83eaac21de35ba23f94683135d35a11f9
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF2-codex-review.md
    sha256: 32a9ad17caf0c7147f8b50027a180ecf7b94f9d6ecd5a6e1f2cc9df02cbe1c16
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF2-instrument-amendment.md
    sha256: 56e476accf53babfd3c2262264bfc47ae4dc73d8929ee679e3437063d4cc98fd
  - path: .gnd-planning/milestones/code-refactoring/notes/phase-RF2-spec.md
    sha256: 6a3694f981bf7b9a0f0839cfcc9760244ec7f8831549f8e87e8f3bd27a2e0574
  - path: .gnd-planning/milestones/code-refactoring/notes/shim-inventory.md
    sha256: 224f3396a6d8e7f25238520f224357a80670d6d6e5957146cfd7cd97405179f1
  - path: .gnd-planning/milestones/public-launch/migration/b3-files.json
    sha256: f55daf5e7cebd67a238eefc7b62d114dfe025db67dd69e3731d53644a3e07737
  - path: src/gnd/admission_validation.py
    sha256: 6fe89e8ed605fe8b4ceff280d0ea7a73e0bf4a2f2b774588990c97a738b06ee1
  - path: src/gnd/api.py
    sha256: cf6af945352ccca5db074e6f44b17acdc04f1e63c92dcc9f1217a2a1013e5d81
  - path: src/gnd/artifacts.py
    sha256: 3b4863142b58c6c61b8ea03608f57e9fdca8e9d6beb8128e45b6fd7b9b7bfbee
  - path: src/gnd/assurance.py
    sha256: 0349a7ea230496649ede29817e5967d4eb5e2d4382b7b4029779fd37d3a16927
  - path: src/gnd/assurance_evidence.py
    sha256: 1427576e1b48b05d0f43535fff54f2a4a08d2163b66c852bbd00d5d2f799f1ec
  - path: src/gnd/cli.py
    sha256: 8f11b133cb0b5d1c2acd674412df185edf634d04bd23a970479633aaa59affe0
  - path: src/gnd/conformance/currency.py
    sha256: f5d0a875b860de5a4fc2f7fb26e287fac1934d93d4898c31adc3d93d2a520ecd
  - path: src/gnd/conformance/report.py
    sha256: 32f1a47e020606a161a2ff9a20269e12af4b709048248d7ce1d8274797a2905f
  - path: src/gnd/conformance/service.py
    sha256: 4687fdf2c4d3d402ef54861ab19ede8ac4218155102f2d971c76126cd2c2216c
  - path: src/gnd/coverage.py
    sha256: 7faa6dbb75b2d172d9002af6a466227e3a113c81170e3d8dc13c31117c9cc746
  - path: src/gnd/declared_adapter.py
    sha256: c481334cece4745dd52d9ab43c98b6db2247a346ba3adef683b2f2ac238c6e82
  - path: src/gnd/diff.py
    sha256: 0d56c218bb7d7c56593c973109a9193b8ca632cdfa137158a25e1df8fabe5189
  - path: src/gnd/exits.py
    sha256: fe895a03a5b403650440955998a18fddf6544c9be298e4c7d08131d051b944d9
  - path: src/gnd/exp/adapter_policy.py
    sha256: 09d4e4ed38ec4ddb4271aae942ba9d82f775fa653d94ff34756e317459fcc21f
  - path: src/gnd/exp/conclusions.py
    sha256: c1fa1bf02507c715957a765c483fb70f1d82d9d6ffe0dbfdfd851b62d074b0bd
  - path: src/gnd/exp/session_eval.py
    sha256: 42a71939bd6f5555c7c3760da86b8c24b1c4824191402828eb9d2d1bc3819508
  - path: src/gnd/exp/session_patch.py
    sha256: c6b607cb5dc1b5ea1f45148d65dc12dbd165df88899b3d28185dbabcdff8be3d
  - path: src/gnd/exp/session_store.py
    sha256: e7c7fd0bbbbafc25923136c41183b33aeec3f9633c5ba64661452d2b9c8190a1
  - path: src/gnd/exp/spec.py
    sha256: 8348d3e3d264de2c22e7f4ebc172694ff37b319ba74f6b27d3b139349ab579e1
  - path: src/gnd/extract/manifest.py
    sha256: da872428fee1d925f79980284b843a3e0740472545cc208d369c8e3155c51d2d
  - path: src/gnd/fidelity/report.py
    sha256: 4cf99a46cdabd65f3603eeb25fa945434e01f3a37e15480b700963dfd78c9cea
  - path: src/gnd/install.py
    sha256: a30f3dbb5c37e6649985caa20769840c126fae6666836d0dfb7160b1ce7d9259
  - path: src/gnd/measure/report.py
    sha256: 414dd74d1ab510eb5404f5b0437d72658559ee60b7b049e6b235838d2394157b
  - path: src/gnd/model.py
    sha256: 5ce32eafd261cdb1b79768d0f8440cd67b2d556f8ddb8519ffb5b50c8260e02c
  - path: src/gnd/recovery/report.py
    sha256: bd866a2cbcee8df6cbc2fc69b894f72171e5f820184e0ced67573316aff4514d
  - path: src/gnd/recovery/verify.py
    sha256: 6ff3a5c7d9ee76edd1ad84fb49cb7ff23277035b6c133efff25ba4007ff462a4
  - path: src/gnd/review/request.py
    sha256: 71955470868c4c518553929fb13bd058acad9284d0b41dfad87ebd3a610534d6
  - path: src/gnd/solve.py
    sha256: 6260748f074680d48480b7f4b74d57f2b14cd2c3f37603810ad11da7f9660601
  - path: src/gnd/synth/assemble.py
    sha256: 88feb46eb10611cdc2ec8026b6ac21dd54ea35b2fae8d5bfb2bca10ec2c74164
  - path: src/gnd/synth/mutate.py
    sha256: d5f69b4ddf6f1a4c8ea0ffff0052c738af6da2da95fa4ba5b46e058cc02e6bd2
  - path: src/gnd/synth/provenance.py
    sha256: a69f9cbd535db6bb6dfa13d8eb498c46f4163862dc367f9bfcb60099321a0981
  - path: src/gnd/transition.py
    sha256: 3756925991641c228ab07e5f0552dd587b398c9ddc315e665b61fe8445a07400
  - path: tests/fixtures/rf1-pins/goldens.sha256
    sha256: 68d9163ee30f32fc03f59294b94c709e52ac569168ac6ecc773eb5dd22a36444
  - path: tests/fixtures/rf1-pins/mutations.json
    sha256: d429148aa99262101622521680ee6a18a9c7a46ef1893696a5055183479b2fdd
  - path: tests/fixtures/rf2-pins/group-bodies.json
    sha256: a4d7b2860fc940c65ea0e595b8c6794ec61c7fe0db2b799d7d7ccce81ec4739d
  - path: tests/fixtures/rf2-pins/pre-move.json
    sha256: 8db54ba304fdd931904bd6fcbc962f8d85c49d4bc94c60a37fc0ffb6bec65a22
  - path: tests/fixtures/rf2-pins/session-successors.json
    sha256: 47d76e43fe8d5abd27dfe96b2afc8b7ecbd8732d1bf739817b469ccd3235457d
  - path: tests/fixtures/rf2-pins/variant-encoders.json
    sha256: 2658b8e9c5de734eb72e931b1ad436a631e8642f80093ac6592e16eb55b9e8c4
  - path: tests/support/rf1_pins.py
    sha256: bc8d818edd867c2fd86c03fd99aaad8ae96a7815ee4a3a1b1627cbcbefc70c1e
  - path: tests/support/rf2_session_pins.py
    sha256: c6cce6599a78ae48e2746b1081c01db6836072043a93454f119ea3d861144892
  - path: tests/test_conformance_payload.py
    sha256: ddef821b72262488776ae8a968334d7d6eb95ad867488c596ff8b0a7e0964711
  - path: tests/test_rf1_cli_pins.py
    sha256: ce4b2cab6249a9a1e7158fc3d80012fad5dcf88f14f51e331d9334c706d03a33
  - path: tests/test_rf1_session_pins.py
    sha256: 9f0eafad9baa361ff53db04edb385d5a2d5adcbbe37174220b92fe5fb11c057e
  - path: tests/test_rf2_digest_predicate.py
    sha256: 646222e7c8b7d81be571a37d36fce4a6d835635099792a559704213b7b231d7b
  - path: tests/test_rf2_helpers.py
    sha256: c6515212104cbc0880b70143d8750a1764364d7b4f1899619f2ed34784e02b44
  - path: tests/test_rf2_instrument.py
    sha256: b48fb040b9b01148e33a65461fdc4cb04645784578e56fc97f369e16f6538fcc
  - path: tests/test_rf2_pre_move_pins.py
    sha256: dffea2fa11bda73647c2eb431bb600224d4b6700b5bf88b0805c0bde4b35ed8f
  - path: tests/test_rf2_review_regressions.py
    sha256: 8bd729fc7d90ad645dabd9c59f87d971175ada6e49af38540164409873c0d89e
---

# Claim

At move commit 16f08ea the selected RF1 and RF2 controls exited 0 under Python
3.11, 3.13 and 3.14 (457 passed, 16 strict xfails each). Five RF2-owned identical
groups went from 17 definitions to five. G3–G5, scaffold, lint and commit-based
size controls exited 0. All 16 retargeted mutations were killed at their unchanged
call nodes. This is focused preservation evidence under the approved instrument,
not whole-repository acceptance or certification.

## Authority and decisions

The owner approved the RF2 prose spec, D1–D10, source-control attestation and
implementation go-ahead (auto=false), then separately authorized the Codex
provider review and approved the bounded instrument amendment. Their artifact
hashes, dates and dispositions are in the spec and amendment. No optional spec
panel was selected. Source-side control rests on that attestation; no source
remote was supplied and no independent source high-water comparison was possible.

RF2 D7 expressly selected bounded manifest adaptation. Its original claim that
this was RF0's ruling was wrong: RF0 D4(b) chose no edit. RF2's later approved D7
supersedes that choice only for these existing changed rows. Thirty-three rows in
b3-files.json are labelled adaptations; before/after rows are retained. units.json
and test_public_distribution.py are unchanged. No publisher or source-owned unit
transfer was enabled, and prior release/assurance evidence is unavailable over
the changed production bytes.

## What shipped

- artifacts owns the unchanged SHA byte algorithm, the identical indent=2 report
  text encoder, shared non-strict Sha256 alias, three separate strict JSON hook
  bodies, and is_sha256_hex after an equivalent-consumer predecessor table.
  The strict review-request type and all fourteen divergent encoders remain separate.
- exits owns existing CLI allocations and their rationale, plus existing 0/3
  meanings formerly allocated at other homes. Old imports and solve/conformance
  aliases remain. The complete current union and imported compatibility aliases
  are checked alongside the approved historical exit-name projection.
- model owns the verbatim ordered ValidationError conversion. Rule-id adapters
  preserve reader-specific messages and old names; divergent converters remain.
- synth and measure route the selected positional constraint references through
  address.positional_constraint_ref. Standalone PyRel runtime is unchanged;
  its emitted bytes and inline/top-level references have source-base pins.
- Raw file SHA, validated-model SHA and transition-model identity have distinct
  new names, with original aliases retained. CLI provenance and conformance
  lookup patches have real consumer-effect regressions. Wire model_digest fields
  and identity algorithms remain unchanged.
- The shim inventory binds 34 old/new import rows and nested-reader boundaries.
  Retirement remains RF-D5: first public release after RF6, with separately
  approved retirement. No shim was removed and no skill module path moved.

## Approved instrument amendment

Original RF1 goldens and goldens.sha256 are unchanged. Source location mutations
were retargeted while keeping every id and expect_red set. Four existing session
nodes route to explicitly labelled RF2 successors per original supported minor.
Their source-base observations first passed the complete original goldens; no
answer was generated from the refactored implementation.

The test-only verifier bootstrap keeps -I, selects the same production source as
the parent, captures the complete mint encoder input and runs the real CLI,
payload and receipt machinery. Each digest is independently recomputed and the
producer is checked against the current production identity. Only the producer
component is normalized in the retained mint input; the two receipt identities
are substituted at exact attempt/receipt paths. Remaining input semantics and
the entire observation compare against the source-base successor. Declared inputs
retain raw text, including JSON whitespace, modulo existing path/identity tokens.
Dual capture is rejected, and RF2 capture compares historical canonical bytes
directly. No blanket wildcard, skip or xfail replaces these four nodes.

A git archive of f5a8318 supplied the baseline package. All 347 extracted files
were checked against their git blobs, with no extra source files. Source-base
capture and replay exited 0 for all four nodes under each supported interpreter;
final captured data equals the committed per-minor successor. The original RF1
support module was not edited; RF1-OQ7 stays with its original owner. New RF2
path normalization has its own escaped-path and changed-input controls.

## Gate output (verbatim)

All pytest commands preserve repository marker exclusions. Session commands unset
LANG, LC_ALL and TERM and prepend the selected environment's bin directory to
PATH, avoiding reproduced environment-only baseline differences. No repository
.env was read or sourced. Capture additionally removes GND_RF1_CAPTURE and binds
PYTHONPATH to the verified source base. Absolute machine paths in retained logs
and command indexes were sanitized to placeholders; this edit is disclosed here
and in text headers. One diagnostic's trailing whitespace was trimmed in this
record commit; its failing summary is unchanged. Exact selections and exits live
in RF2-interpreters/*/gates.json, RF2-final/RF2-gates.json and G8-final-lint.txt.

    $ .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_layering.py tests/test_rf1_pin_harness.py tests/test_rf2_instrument.py tests/test_rf2_digest_predicate.py tests/test_rf2_helpers.py tests/test_rf2_pre_move_pins.py tests/test_rf2_review_regressions.py --tb=short
    457 passed, 16 xfailed in 70.41s (0:01:10)
    (exit 0; Python 3.14)

    $ <scratch-env>/rf2-py311/bin/python -m pytest (same exact selected arguments)
    457 passed, 16 xfailed in 72.27s (0:01:12)
    (exit 0)

    $ <scratch-env>/rf2-py313/bin/python -m pytest (same exact selected arguments)
    457 passed, 16 xfailed in 71.51s (0:01:11)
    (exit 0)

    $ .venv/bin/python -m pytest -q tests/test_checker_families.py tests/test_artifacts.py tests/test_address.py tests/test_gnd_arch.py --tb=short
    244 passed in 5.47s
    (exit 0)

    $ .venv/bin/python -m pytest -q tests/test_conformance_payload.py tests/test_conformance_drift.py tests/test_coverage_payload.py tests/test_fidelity_payload.py tests/test_exp_spec.py tests/test_extract_manifest.py tests/test_review_request.py tests/test_recovery_report.py tests/test_recovery_adversarial.py tests/test_exp_session_eval.py tests/test_exp_session_store.py --tb=short
    474 passed, 1 warning in 14.32s
    (exit 0)

    $ .venv/bin/python -m pytest -q tests/test_measure_offline.py tests/test_measure_coverage.py tests/test_measure_derivation.py tests/test_pyrel_export.py tests/test_pyrel_export_boundaries.py tests/test_exp_bands.py tests/test_review_bands.py tests/test_solve.py tests/test_install.py tests/test_doctor_uninstall.py --tb=short
    546 passed in 135.74s (0:02:15)
    (exit 0)

    $ python3 tools/gnd_arch.py compare f5a83186f7c2215ac2b2afb0a010c2294eaa433a HEAD --out .gnd-planning/milestones/code-refactoring/evidence/RF2-commit-compare.json
    (exit 0 at 16f08ea)
    $ python3 tools/gnd_arch.py measure --out .gnd-planning/milestones/code-refactoring/evidence/metrics-RF2-commit.json
    (exit 0)
    $ .venv/bin/python -m pytest -q tests/test_development_scaffold.py
    14 passed, 1 deselected in 3.72s
    (exit 0)

    Command: .venv/bin/ruff check src/gnd/admission_validation.py src/gnd/api.py src/gnd/artifacts.py src/gnd/assurance.py src/gnd/assurance_evidence.py src/gnd/cli.py src/gnd/conformance/currency.py src/gnd/conformance/report.py src/gnd/conformance/service.py src/gnd/coverage.py src/gnd/declared_adapter.py src/gnd/diff.py src/gnd/exits.py src/gnd/exp/adapter_policy.py src/gnd/exp/conclusions.py src/gnd/exp/session_eval.py src/gnd/exp/session_patch.py src/gnd/exp/session_store.py src/gnd/exp/spec.py src/gnd/extract/manifest.py src/gnd/fidelity/report.py src/gnd/install.py src/gnd/measure/report.py src/gnd/model.py src/gnd/recovery/report.py src/gnd/recovery/verify.py src/gnd/review/request.py src/gnd/solve.py src/gnd/synth/assemble.py src/gnd/synth/mutate.py src/gnd/synth/provenance.py src/gnd/transition.py tests/test_conformance_payload.py tests/test_rf1_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf2_pre_move_pins.py tests/test_rf2_helpers.py tests/test_rf2_review_regressions.py tests/test_rf2_digest_predicate.py tests/test_rf2_instrument.py tests/support/rf2_session_pins.py
    All checks passed!
    Exit: 0


    $ git diff --quiet f5a83186f7c2215ac2b2afb0a010c2294eaa433a -- .gnd-planning/milestones/public-launch/migration/units.json tests/test_public_distribution.py tests/fixtures/rf1-pins/goldens tests/fixtures/rf1-pins/goldens.sha256 tests/support/rf1_pins.py
    (exit 0)

Six source-base capture/replay runs each report four passed, exit 0. The focused
mutation command is retained verbatim in RF2-mutation-command.txt and reports:

    rows: 16  killed: 16  not killed: 0
    Exit: 0

The unmutated mutation control names sixteen passing nodes; every reported kill
is a failing call-phase event. The previous RF1 167-row result remains historical;
RF2 ran only the sixteen changed stimuli, not an unselected full mutation replay.

## Criteria and measured budgets

| Criterion | Result |
|---|---|
| RF2-C1 one home per identical RF2 group | Met: 17 → 5; source-base body equality is calculated under each runtime, with a known duplicate negative control |
| RF2-C2 variant encoders unchanged | Met: all fourteen source bodies equal the base SHA-256s; byte/ref successor controls remain green |
| RF2-C3 distinct digest meanings and old imports | Met: three renamed algorithms, old aliases and unchanged wire/input names; real lookup patches verified |
| SM1 | Met under the owner-approved successor instrument; every original golden remains immutable |
| SM2 | Met: shim inventory plus imports, consumer lookup effects and killed retargeted mutants |
| SM3 | Met within moved-helper scopes: real network/provider scan visits, a missing-home negative control and planted network-import refusal; no new production module |
| SM4 | Met: same module map, clean-layer ratchet and sixteen existing strict xfails |

| Measurement | Base | Head |
|---|---:|---:|
| Production modules | 148 | 148 |
| Production lines | 104094 | 104110 |
| Import edges | 842 | 858 |
| Production private-import sites | 242 | 242 |
| Runtime SCCs | 5 | 5 (same memberships) |
| Wrong-way / cross-lane edges | 27 / 54 | 27 / 54 |
| Test patch sites | 464 | 475 |
| Private test-import sites | 609 | 617 |
| Source-scan sites | 88 | 92 |
| Packaged-skill module citations | 9 | 9 |

New common-helper imports and compatibility aliases explain the added import
edges; no cycle or layering improvement is claimed. The head test inventory was
measured after the final instrument repairs, superseding the earlier worktree
snapshot. No citation names a renamed digest function; existing module paths
remain, so no skill source or discovery twin needed editing.

| Budget | Actual | Approved ceiling |
|---|---:|---:|
| Production files | 32 | 40 |
| Moved production lines | 78 | 350 |
| Added production lines | 236 | 300 |
| Removed production lines (reported separately) | 220 | n/a |
| Added handwritten test lines | 718 | 1000 |
| Non-evidence files | 54 including this record and RF1 discharge annotation | 70 |
| New RF2 fixture bytes | 1114331 | 2097152 |

Commit-based G6 equals the production preview. Deduplication is not presented as
all physical movement: additions, removals and moved-line matches are separate.
The additional two closure files contain no production or test change.

## Independent review and regression dispositions

One reviewer is one reviewer. One Codex reviewer inspected the initial diff and
one bounded repair pass inspected the amended instrument. These are not a panel
or a certification. Both outputs are retained with declared path sanitization.
The reviewer did not run the test suite; its opinion applies to inspected bytes,
not automatically to later repairs.

Initial findings (all blocking): CLI provenance still used the old lookup;
scan scope control did not observe the actual guard; allocation control missed
annotated/computed assignments. Five pre-fix cases failed. The final CLI cases
also failed against a copied package with the two old lookups restored.

Repair-pass findings (all blocking): py314-only successors failed other supported
minors; a Name-indirection allocation bypassed the guard; dual capture could
bypass historical comparison; declared JSON projection erased whitespace. Each
was reproduced before its fix. Retained red evidence names the original failing
nodes; final tests cover all three minors, local allocation indirection, dual
capture and whitespace. One further CI instrument defect, interpreter-specific
AST hash matching, was reproduced red and repaired using baseline body fixtures.
No completeness expansion was selected and no third review round was run.

The initial review confirmed the five groups, type split, aliases, conformance
patch, references, fourteen encoder hashes and original frozen files. The repair
review confirmed exact two-field observation substitutions, authenticated full
mint inputs, the sixteen unchanged mutation ids/expect_red sets, optional None
behavior and original three repairs. It could not independently establish the
source-base checkout from terse logs or complete G6 before commit; the subsequent
blob-verified source selection and commit-based metric controls address those
limits with executed evidence, without fabricating a new reviewer opinion.

## Refactoring review

**Refactors EXECUTED**: five identical groups, common issue conversion, centralized
exit allocations/rationale, selected positional references, and the equivalent
SHA predicate moved behind predecessor and current-byte controls. Digest renames
make distinct meanings visible while preserving import compatibility. The two
review-found live CLI lookup sites were retargeted and their real effects tested.

Seen and deferred: parameterized canonical-byte unification lacks an identical
family; standalone PyRel is emitted verbatim and cannot acquire a GND import
without a separately approved format boundary; remaining safe-filesystem, model
query and session families keep RF4/RF6/RF8 ownership. No new structural refactor
was added beyond this phase. RF1-OQ7 remains because its support module was not
edited. See the named open questions below.

## Boundary — what this phase did NOT establish

- AST identity is not behavioral identity. The source-base and focused pins cover
  the declared moved contracts; no branch exhaustiveness beyond these contracts
  or all-model checker correctness is claimed.
- A completed process-phase walk is not an acceptance claim. No full default,
  broad evidence/census/distribution, provider/native lane, production release,
  publisher, certification or recertification run was selected.
- Prior production/release identity changes on every source edit. Old assurance
  and release certificates remain tied to old bytes and are unavailable here.
- One reviewer is one reviewer. The review is evidence, not proof; no agreement
  separates a wrong instrument from a wrong implementation. Repairs have executed
  regression evidence, not an invented later review opinion.
- The four successors use a disclosed test-only subprocess bootstrap to observe
  real mint inputs. They preserve the full original source-base observations,
  but do not claim the untouched production launch path was itself instrumented.
  Other selected session versions retain their original launch path.
- MacOS local runtimes 3.11, 3.13 and 3.14 were exercised. Linux/Windows CI and
  unsupported interpreter minors have not been verified by this record.
- Source authority control rests on approved owner attestation; no source remote
  or independent high-water comparison was available. The public-launch ledger
  and its guarding test remain unchanged.
- Whole-tree manifest attribution is not claimed. D7 adapted existing changed
  rows only; no prior public-launch acceptance or release claim was widened.

## Open questions

- RF2-OQ1 → milestone close: repair the plan's identical canonical_bytes premise
  and the family note's “compact” description. The promoted report group actually
  uses indent=2; fourteen diverged encoders remain separate under D2.
- RF2-OQ2 → RF6 export/model-query gate or separately scoped successor: decide
  how standalone PyRel positional-ref routing can preserve its copied runtime
  and emitted bytes. RF2 D4 explicitly leaves it unchanged, with pins now supplied.
- RF2-OQ3 → milestone close: reconcile the RF0 D4(b) manifest ruling and the plan
  RF-D3 wording with RF2's later explicit D7 bounded adaptation decision.
- RF-D5 → first public release after RF6 plus explicit retirement approval:
  compatibility shim retirement remains owed; all thirty-four rows remain live.
- RF1-OQ1: the RF2 measure/PyRel pin portion is discharged here. Other owed
  families keep their original phase owners; this is not wholesale RF1-OQ1 closure.
- RF1-OQ2/4 → RF8 or successor; RF1-OQ3 → milestone close; RF1-OQ5/6 → successor;
  RF1-OQ7 → next actual edit of tests/support/rf1_pins.py. Boundaries remain standing.
- RF0-OQ5 → RF3 and RF0-OQ6 → RF8, plus source-owned
  **RF0-OQ5 discharge annotation, 2026-10-05: 008-phase-RF3.md measures the
  retained dynamic edge and acyclic original core/new homes. The prior
  boundary and all other ownership below remain standing.**
  OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1,
  OQ-V52-P1-IMPORTWALK-1 and OQ-V63-CLOSE-HELPER-TAIL-1 retain their prior ownership.

## Refuted premises

- A parameterized identical canonical-byte family exists: refuted by baseline
  metrics and separate source bodies; D2 chose the real identical report-text
  family instead. The plan repair belongs at milestone close.
- Whole exit namespaces and fixed mutation source snippets can stay byte-identical
  under the required moves: disproved by the initial six-red G1 result. The owner
  approved an instrument adaptation, preserving every original expected artifact.
- Normalizing top-level producer identity also stabilizes authenticated execution
  identity: all four structured differences isolated the two nested source-bound
  identity fields; verified full-input successors repair that missing transitive
  normalization without erasing remaining semantics.
- One py314 successor and RF0's py314 AST hashes are portable expectations:
  reproduced false under Python 3.11. Per-minor source-base successors and
  runtime-calculated equality against baseline body fixtures now pass all three.
- Calling assert_golden necessarily compares historical bytes during capture, and
  parsing declared JSON preserves bytes: both were reproduced false. Dual capture
  is rejected and raw text/whitespace remains bound.
- RF0 authorized manifest adaptation: its D4(b) did not. The explicit later RF2
  D7 approval is the authority for this bounded edit; original-site wording was
  corrected and the prior ruling remains historical.
