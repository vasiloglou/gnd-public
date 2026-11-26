# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this phase's diff do what the IS2 spec (notes/phase-IS2-spec.md, sections 6, 8, 14-16) says, and are its tests, checks and docs claims true of the inputs they cover? Report defects with a concrete input or file that shows each one.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. IS2-A1: the six gnd-induce sentence changes are each pinned by a test that fails on the IS1 wording
- C2. The recorder's checks (no_apply_call, no_hand_written_proposal, actor_from_user, no_forbidden_bash, no_outside_path, done) compute what spec 6.2 and findings F4, F6, F8 say, for any legal stream, not only the recorded ones
- C3. spent() counts the example's runs, the evidence attempts and F2, so the USD 10 ceiling is enforced across attempts
- C4. render_replay pairs each tool result with its call by id and marks a flattened code fence, without changing any other existing replay
- C5. The learn-rules page shows no command outside replay transcripts and recorded user turns, every You type fence is a recorded declared turn (step 6's review prompt marked Not recorded), and every In this run note is true of its transcript
- C6. TUTORIAL_CLAIMS' recording column names a string each recording's kept turns actually hold
- C7. release_text's replay exclusion and test_ik6_walk's JSON-decoded scan do not hide a real stale claim or a real absolute path in a page or example file

## The change under review

The work from `a223ac7266967feb4b3f533d535c5a8c9a22c5b5` to the working tree at `f7aebc80a292`. Its diff is `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/diff.patch`.
- new: .claude/launch.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/reviews/issue-286-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/reviews/issue-286-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/reviews/issue-286-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/reviews/pr-289-r1/posted.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/reviews/pr-289-r1/review.log (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/diff.patch` | `82ea2e33ca221a181917b37ed56c83b8f1928aa23aecf128bc8dbfc704824ca9` |
| `.gnd-planning/milestones/induction-skill/003-IS2-recording-gate.md` | `6fe958f2979d3be04f51f1e194ba7bf12a37aa8dab79d3a69723095830339169` |
| `.gnd-planning/milestones/induction-skill/004-IS2-recording-gate.md` | `528099f47e6906a98063e5a1c034748baf4159bad1229324a47e5eebd5602436` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/manifest.json` | `4329d1562194c8f1cf9d83e0b1be35b1f9953ce93c54ea4a63d8f40e7e933f06` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/results.json` | `8087c6b63452b5e8f7b4bbec78aba7943e138ebc461df247b186aa4a4962b56c` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/turn-01.jsonl` | `e4d57b0da3e2d221c04ce2e7f2279397f8fb360bb9394273c2b3553faa61c34c` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/turn-02.jsonl` | `4735ee91519a490268fd8203aa9bc5ea95dafcc93ef4ce81dfd64f3227da2079` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/turn-03.jsonl` | `7099e4c8586874d5dbc6fdd591a5adf5deabe86b6cd2a6a8fe866fe09a12b67e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/turn-04.jsonl` | `e14cf70fb595e66138e40db398bcbe9cb64801ad5f8ea240ff15e3ba120feab3` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/absent-learner/claude-haiku/run-1/workspace.json` | `e31b111502851e3e606368e10c9eecf95ea0301a79cb4c2fcc7ab190311cdd40` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/manifest.json` | `72eb39c79f298df5395988fc6a45771e5b4cd8c3defafd38e85c200a112d7836` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/results.json` | `56c5bdba6f9f558ba27b2bab8d50debfc3efefebc2cac00652bc7b772ec0ab51` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/turn-01.jsonl` | `fad5353450b29777cbe6bb97e06f848214602c249fd321a7d2474f10d65bf204` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/turn-02.jsonl` | `98b8308e7616917fb26011ed5eff760adad5eceb6e80706cb0597ff7e329a4b3` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/turn-03.jsonl` | `a56335aade706347dd3af6cc607fc5c3695518145c1432d397603fc6921292bc` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/turn-04.jsonl` | `e3d76bf601d959fafe6a753ac152dd505538d2e32a3845fc43f77b0f9de57412` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/discover/claude-haiku/run-1/workspace.json` | `e2470b2bd0dbb96ee2b2fb5fc63fce0f399e56c9770b40599d6e19641a70580b` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/manifest.json` | `f60b2e6468a014672535e3f5e8566db3e3d1b8ed569fc1a43cb9b497a0bfb374` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/results.json` | `d7364b0bdb346289e73fdc8daadcec91b0aeacc559e806ed22488eca1595409c` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/turn-01.jsonl` | `d98453d972059e4c3191adfbf9eb560e6c89f8faae5105f6a2ecd9ebc1cc1e1d` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/turn-02.jsonl` | `2db1429f1f3a215f36709b20881e1f7303789061de809463f5ea0b4f9899b286` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/turn-03.jsonl` | `efb347a2e2ab6d19fea86ac84b704c504f681932d27ac96ceb03a6f4e8a4a9b1` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/turn-04.jsonl` | `3aa932d6756dd9a7fd7327f423ff7cccf3d4903ee8ea6515ad8525906ac33381` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/existing-output/claude-haiku/run-1/workspace.json` | `6b3cff3fd83e5e63bfe66bfaa6dbc65c6af1b02b4c04bdc30fe5b619efbf51a2` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/manifest.json` | `a73342094c0ee8e4116fe38e61e33384385f202765f20aafa1e65beab9f28232` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/results.json` | `11dca57cdacdd75e6a98deafc4c325eee4e515bad39630d2ad5a629085b9793d` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/turn-01.jsonl` | `1a50d32149260963f22f10af202ee831c02f7af19740adf6693a14b9573b8561` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/turn-02.jsonl` | `e2514252bb3eb474b667700eae944eb05a6b3d767c5b1b5d6f8a643652f2640e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/turn-03.jsonl` | `2d4131f9c598172bde4519ba2b504b30fe334a6587a3acd3b860f32f3d3e8f7e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/turn-04.jsonl` | `c7ede9cd33c10ca45aed03debe4f3d5ef8276fa4a6cd43be77a3c29a3c8b0f21` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/faulty/claude-haiku/run-1/workspace.json` | `deeee602e960434d63feda3b216ea8e880b6e2ae384e206b6a9aa7cb93d953b8` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/manifest.json` | `632d8c21111083a5d49bd85c5fdd541385e1ce69b6a6ea995ae48f286549d978` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/results.json` | `7284db6dc188d47c7c170aceb4255dfdfb54d7cd83250737e303b558b7e19d62` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/turn-01.jsonl` | `9336299430296d3cc4d496ff7dfe7f57c7964621bb24a1ffb548f16b0f29b9ef` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/turn-02.jsonl` | `cf222ecf062e3ba9bf25773a3a11e6df0350d46e3027bd58704a391d87b56920` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/turn-03.jsonl` | `c7f7510bed57a7011024417bcfa394b942377b46dfa277c99e469f2b23d73e19` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/turn-04.jsonl` | `bef7874c5de9be1c4780224eca44f136a7790d929637891d02b210fe6b44eab7` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/import/claude-haiku/run-1/workspace.json` | `de3ba9cf1b1c9ec4f1f7642a598b86e4831ea5b1b04a67de41b9e7bb41c94324` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/manifest.json` | `2fd7b5a22e03088d8c8fa02ff4f6df2eca3a43680440571b188d6cf724ad95e7` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/results.json` | `8aac0d57ee5cbe2e5af75eb06d9184be152b785cc29c23b803467bdf2ba4d46c` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/turn-01.jsonl` | `4a01953982d1379d1a24a168f59752fe7f6f0f213f499f556137f6121be1dc65` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/turn-02.jsonl` | `1601120cec669020a104dd8be3f05bfe3fcce216cc85c76010f1ce0b0625db87` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/turn-03.jsonl` | `d3c8ea84683c3fc1d6cfbc3c5748183dd278027374533706955a4bcd56419412` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/turn-04.jsonl` | `d866b9a549bb2b3f2ed48f0eba95522a237319d9812b3474322125f334b76b37` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/learn/claude-haiku/run-1/workspace.json` | `26d8234777810a3cea90516d43f2cec448f65819f9aa781cbacc33dade92a9d7` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/manifest.json` | `21446d5ab917041eeb02acf5f513cb9bb2268080059665350e4ea2ff072f8dc4` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/results.json` | `79eb9aa875ca1c2b689831eea42e7cd961e2ab9f18b2c93f70faae37dff36c4e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/turn-01.jsonl` | `db928c91ded57f4e5b9e64aece9006c2c5d12ddd7ee529c78049f9cc1f70f288` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/turn-02.jsonl` | `14e343ce908c577f797cf07f145fea2e4b5d9f23e2665280428e93f65773a06e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/turn-03.jsonl` | `a98a5fbcd98f645b4f9a60daa6a7f1ad36dfe5ff67ee7aa5bac957d1597fa88a` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/turn-04.jsonl` | `49590579a7495b47b8057c1120a4bfb04b8e51d07fa1049e89281e53758f2661` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/make-it-pass/claude-haiku/run-1/workspace.json` | `1927c40e1cb652fff754481007a0f0683053d6b2075138adf1feca85b7c05219` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/recheck/claude-haiku/run-1/results.json` | `b9a1910228e6b4a3df31687f1730d3d066d9ce4a841aec35134b18024dd6ab79` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/rechecked-checks.txt` | `0c8e9e8a5599d3814391799037d6a46c450902d22f8482ef6a0cb104e6e997d7` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/score/claude-haiku/run-1/manifest.json` | `74c7ef1d9f38aefeb5ca0231ace073028db3b80ef0a47babc0d5974fb33f76dd` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/score/claude-haiku/run-1/results.json` | `7965274344e9fe191b1e81b34cc1560487d3840803ba50ff960749b33647e8bc` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/score/claude-haiku/run-1/turn-01.jsonl` | `dbff546da4e2e337e926b81284a9404a371923af72acae6ba3e54eacdeea5207` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/score/claude-haiku/run-1/turn-02.jsonl` | `311b18f016ccb8ce98a6e872f1da67a2ebbf37652f057bde74f86fc4d6d32fb8` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/score/claude-haiku/run-1/workspace.json` | `b45cfe9eeeb47e735cb6a51a8407c3d2fe5ae15e0136ecab1052edb5fff379f5` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements-c1.txt` | `51aaad66cbadc660956a79e253ff88ae53be1349905baf92b1787b760b54e9b7` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/owner-statements-c2.txt` | `eb9e4fcaebf087cbf5005fab76bd46d41d53f184832f73c499ccbc12f7ce996e` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/rechecked-checks-attempt-2.txt` | `25c69ead16fc05a44746e4af6875eba0477241243bed5b311a392bc9ef796d02` |
| `.gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md` | `0e9662ea415eaf91c8f661be1e834a8872bc8e766ffb6ead92d6059bbfbb6d9b` |
| `dev/components/modules/tools.md` | `714e396e69b0e51927ee99e2ed473ccda908f89bc287d94b91dac36e00f7864d` |
| `docs/assets/replays/course-model-evolve-haiku-run-1.svg` | `2ef46aacef077f516182f5149895e548ce9976d7992619755be790e377a7f003` |
| `docs/assets/replays/course-model-evolve-haiku-run-1.txt` | `643ebabd97833524d58ab4c0c8395c1e79a3ea7c0f53386d2940043061fe7dcf` |
| `docs/assets/replays/refunds-discover-haiku-run-1.svg` | `a54f056c166cba4f703bdac9a0d350251850d72ad89ae2369c106212d2baed8d` |
| `docs/assets/replays/refunds-discover-haiku-run-1.txt` | `d8ee5747ae4f9ebe8b67c152321cb1c38af681ba670b6cbad60940bdc2aa53d7` |
| `docs/assets/replays/refunds-faulty-haiku-run-1.svg` | `1d90df88ceba8f882bd1b7604c14ae1bfde715ca727722b6136e9a4516d99401` |
| `docs/assets/replays/refunds-faulty-haiku-run-1.txt` | `35e2526253f36b1bcf8da33f2ccbfd3b44c2267b0a9f9e190231640e0e7146ec` |
| `docs/assets/replays/refunds-import-haiku-run-1.svg` | `95c4a4db8f9f0d67bcdd05fe2b8d105e14568f384e50ef4dc95eeb75e0e0cdc1` |
| `docs/assets/replays/refunds-import-haiku-run-1.txt` | `ce7318f7c70a9b4aec839af42aca70c73bf30e8354e25b534e75c315cb54860c` |
| `docs/assets/replays/refunds-learn-haiku-run-1.svg` | `41d15efadadc3c035a7b0f8cbb59dc897a1250eee977d6793efdda798e36096f` |
| `docs/assets/replays/refunds-learn-haiku-run-1.txt` | `d5d160b6176e11106d66596a137d9cc6ec485d45bdf99a15170b8b2aad3b0277` |
| `docs/assets/replays/refunds-recheck-haiku-run-1.svg` | `0b782e1cdabf989a4098e3b2db3e2f52870a572bc858cd8b520bf5724b99ca35` |
| `docs/assets/replays/refunds-recheck-haiku-run-1.txt` | `84b1bc9f922c5018db661bca8a07bfdcc8fba42b4ff178173dc16c5a37125510` |
| `docs/assets/replays/refunds-score-haiku-run-1.svg` | `51584d22a7de4f48f3d0a55aecaa904e192ba6c135f27406696339757a62b4ed` |
| `docs/assets/replays/refunds-score-haiku-run-1.txt` | `8d1d3c35cfd0a6b4bd21315a4c5565f14a2ea06788cf2042de9d9864de563b5e` |
| `docs/assets/replays/replays.json` | `7f6d3987314ee12e7100bd141965f6ee74948cdd9babf58524f6d5eb03c66a3f` |
| `docs/how-to/learn-rules-commands.md` | `7e202632af736c4c01e566e35af65f39c56a1dc4ae938a3e145e164be49149ed` |
| `docs/release-notes.md` | `d26eb18ca23339946e79ae3ed46349351f93eecf7fe349903b9e3be11fb6f560` |
| `docs/tutorials/learn-rules.md` | `0a225fd80f8b69e9d6c7eb04bbec5f8787ea6c96ba3f987d56d3cd121e561183` |
| `src/gnd/examples/refunds/skill-sessions/absent-learner/claude-haiku/run-1/manifest.json` | `16ef1a582985f1bc109420bcfd1ac2ea42540a5afe41c9ead1a26432195c3080` |
| `src/gnd/examples/refunds/skill-sessions/absent-learner/claude-haiku/run-1/results.json` | `f12d3405be1bcf0779311e1e11d9538376959d5b29a7345ddfc01efeeca45bab` |
| `src/gnd/examples/refunds/skill-sessions/absent-learner/claude-haiku/run-1/turn-01.jsonl` | `3b7d6810050694c22e55fa6dc3dde02cf110dbf6c2e774a6bea2e91bc4ee1e4e` |
| `src/gnd/examples/refunds/skill-sessions/absent-learner/claude-haiku/run-1/turn-02.jsonl` | `1766be659396f14774cd23a930244006a80f3e4f58aeb039bc428d2be1a08d58` |
| `src/gnd/examples/refunds/skill-sessions/absent-learner/claude-haiku/run-1/workspace.json` | `8d4e40f98397ff21364726ef18c42cfe9d48f6fbca19b83c442cc8701c9456eb` |
| `src/gnd/examples/refunds/skill-sessions/discover/claude-haiku/run-1/manifest.json` | `73cf77ef6c5a4d56274511fa94095f4a032ad3d565e1eee56a245634e346b09d` |
| `src/gnd/examples/refunds/skill-sessions/discover/claude-haiku/run-1/results.json` | `83edf25cebbf9bf273449d7b256e3eba80ae53957e73ea9ffbbf877ebddb2c01` |
| `src/gnd/examples/refunds/skill-sessions/discover/claude-haiku/run-1/turn-01.jsonl` | `1a0b2159bc3d470c5bd877abfee8b93f6e477d49151147aadcc4b946e40cd4cb` |
| `src/gnd/examples/refunds/skill-sessions/discover/claude-haiku/run-1/turn-02.jsonl` | `053e4df70cfa5262b5eaee0a1b32e1b6af5f0cbfcbc391b036b35607c23b2f83` |
| `src/gnd/examples/refunds/skill-sessions/discover/claude-haiku/run-1/workspace.json` | `3324b3d074be11d0e4050a99ebd00e59a5501eb8a57edcc4df1d99e3619ce61b` |
| `src/gnd/examples/refunds/skill-sessions/existing-output/claude-haiku/run-1/manifest.json` | `a7912c14d58fdbde5a03b66921c4506f5bbb57a21c3d3f5ca7328c4a7b0ede90` |
| `src/gnd/examples/refunds/skill-sessions/existing-output/claude-haiku/run-1/results.json` | `c757161f06ebbcb83f1e57625b4d3b16a231cf6ed8e366f65c6c4ce69b8f4af2` |
| `src/gnd/examples/refunds/skill-sessions/existing-output/claude-haiku/run-1/turn-01.jsonl` | `b070da1107181a8cde02ffe30d96a731a44111c6412b56bb2e6da589e951aa45` |
| `src/gnd/examples/refunds/skill-sessions/existing-output/claude-haiku/run-1/turn-02.jsonl` | `fc2313d5fa58138586d27b0df12c629323069b73b161ef5353c48794ee54e1f9` |
| `src/gnd/examples/refunds/skill-sessions/existing-output/claude-haiku/run-1/workspace.json` | `831f29a36f7397c93320ec604e517fc167ae348550b6f648214d5a1634009a85` |
| `src/gnd/examples/refunds/skill-sessions/faulty/claude-haiku/run-1/manifest.json` | `94992560ce2ef30e0107c51baca205b942268f516ef9ed9c75c96bd4bf016d47` |
| `src/gnd/examples/refunds/skill-sessions/faulty/claude-haiku/run-1/results.json` | `f243cfb833d763113b57687af58427175895dd863a1c8e2ffb063d79c18beabb` |
| `src/gnd/examples/refunds/skill-sessions/faulty/claude-haiku/run-1/turn-01.jsonl` | `b5de8f677571759ba1125236042f3acbfb2c94654f6ec8d0135d74fda723abea` |
| `src/gnd/examples/refunds/skill-sessions/faulty/claude-haiku/run-1/turn-02.jsonl` | `3b76da9425325c6e23e5624f5de1eb4a611ccb95e9c9693e12cd168e499f2ea6` |
| `src/gnd/examples/refunds/skill-sessions/faulty/claude-haiku/run-1/workspace.json` | `68f8793bffac02e7bd9046233832a23f0cae058494b735e5ab7de2e9fe8df0a9` |
| `src/gnd/examples/refunds/skill-sessions/import/claude-haiku/run-1/manifest.json` | `d16afb9a0dbb150b45e991dde71b3d5c0186da32f2f7c5a88ae23ed1e66bbf9b` |
| `src/gnd/examples/refunds/skill-sessions/import/claude-haiku/run-1/results.json` | `f36e24ce5008ff59781a429acc423064ea7ad9daaf13644da1f8062194514312` |
| `src/gnd/examples/refunds/skill-sessions/import/claude-haiku/run-1/turn-01.jsonl` | `caa503c8a951d67db860fd244a2befe99ef8ce163c3d319796379a6665e813ad` |
| `src/gnd/examples/refunds/skill-sessions/import/claude-haiku/run-1/turn-02.jsonl` | `8c382165123b3086c6ecebc197d5fd7ee7dbb934d336cb2255ba3eff1ae58d80` |
| `src/gnd/examples/refunds/skill-sessions/import/claude-haiku/run-1/workspace.json` | `bbeaa7e96d57588514fb0277fa9e157409925970a7c5de5ca58624953bca5607` |
| `src/gnd/examples/refunds/skill-sessions/learn/claude-haiku/run-1/manifest.json` | `442a01797127f55a57c1b8f02587de0f9487f08b858608ae75802bc68384a926` |
| `src/gnd/examples/refunds/skill-sessions/learn/claude-haiku/run-1/results.json` | `2ed39d72d0f22573488b9d6aeaa33e85251743035e15ba19826acde525fe8e46` |
| `src/gnd/examples/refunds/skill-sessions/learn/claude-haiku/run-1/turn-01.jsonl` | `845bf349ff0db4a2dcc8b4da7771815196328615c5db1d0ad39b6bb27c104221` |
| `src/gnd/examples/refunds/skill-sessions/learn/claude-haiku/run-1/turn-02.jsonl` | `d1814c6e01a7b955c92f176dceb79cbf85e313e0241f453d237e9eada9bc4b26` |
| `src/gnd/examples/refunds/skill-sessions/learn/claude-haiku/run-1/workspace.json` | `475182482739826f6cfcf93a60b0edfcbdca05527bc1cf34528ca556b5797eee` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/manifest.json` | `f5e8df62dc422b1bbc77dfd5db4f66ec84c10bd406c6d0d855fe29a116f5832d` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/results.json` | `da54e4a9b5353d6e8d8547a576861a1eca1ea60d26da59aa4eea5c50afab5300` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/turn-01.jsonl` | `ed2c7ad34944e58a96654d6fb52c869787a68429725d210b3127608e09ed323a` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/turn-02.jsonl` | `f58eee2ff4ed03e05f6b4d9083b92e3fbcebd35fa238672560666c8d44603fab` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/turn-03.jsonl` | `fdbfd3ebce81560850094404f1b6957522117452fd6e6e62daa90dbe91857a99` |
| `src/gnd/examples/refunds/skill-sessions/make-it-pass/claude-haiku/run-1/workspace.json` | `389eacafb8a033090b3c48bf1a85be5e1784bcd5de2aba65e16e8bbb471904cd` |
| `src/gnd/examples/refunds/skill-sessions/recheck/claude-haiku/run-1/manifest.json` | `c9060f17ee8adcb0111bcfc062c1c28a53c831c3a005f64c416c03d6c5ff4f45` |
| `src/gnd/examples/refunds/skill-sessions/recheck/claude-haiku/run-1/results.json` | `7f92b6740beff896d506a17aff9d38decfce5eab42808ac6c8823db7934982f7` |
| `src/gnd/examples/refunds/skill-sessions/recheck/claude-haiku/run-1/turn-01.jsonl` | `e16b7c13c9c01c6aabffa6edfda4c15b5b41a1dcb40946c475951e72cfc5a2bc` |
| `src/gnd/examples/refunds/skill-sessions/recheck/claude-haiku/run-1/turn-02.jsonl` | `67f26094e559c745d9d89808bc31a5838fc65aa3d9940294210e01f598dee8c9` |
| `src/gnd/examples/refunds/skill-sessions/recheck/claude-haiku/run-1/workspace.json` | `c3093d1ec5ee3fef6a00569eede79c61fadf408f57ad716ddc7f661748afc8d2` |
| `src/gnd/examples/refunds/skill-sessions/score/claude-haiku/run-1/manifest.json` | `cc42bd49192e2eb104a55a634570c0d7a6c8f77d3ff8c24484a8ba65823c52de` |
| `src/gnd/examples/refunds/skill-sessions/score/claude-haiku/run-1/results.json` | `625914ae21b745e9eb76c7f3ac5fdb4f93b51023bdca4883f9a0e34ece82b951` |
| `src/gnd/examples/refunds/skill-sessions/score/claude-haiku/run-1/turn-01.jsonl` | `5b5bb2fb1e10bf65e14cd961ee385db3acb15e59df77508f85374db4f41ee2c5` |
| `src/gnd/examples/refunds/skill-sessions/score/claude-haiku/run-1/turn-02.jsonl` | `c5de530379c95b62e5961bb9386d673d6d37159fb6e51980f94ee89282055e27` |
| `src/gnd/examples/refunds/skill-sessions/score/claude-haiku/run-1/workspace.json` | `7d6465625eaef0179d229f0e1877e7270d3a2091b3b709c8225923811086c1ae` |
| `src/gnd/skills/gnd-induce/SKILL.md` | `8517e32d0c10c35f22652e01e2b798bbeca00bd773b47a23980279f734eec5f0` |
| `tests/test_ik6_walk.py` | `1b1d9e5165ae080abdb649595cd05c19563d77bd3d4d48ae69ee717c26b79aae` |
| `tests/test_induce_skill.py` | `4d68d4a8fad039e19659eb611b6af269c62c45bba0fc24cc49d5b339ecabc372` |
| `tests/test_learn_rules_page.py` | `7b1482b967ddb714069ca55ab51b419234bc199d26a5fed47028a3e64a1ff7e4` |
| `tests/test_public_distribution.py` | `6bd5ca49e0f63bdbd2c02d6510dd8e87788efed51a588c43d5bb346e9701f887` |
| `tests/test_record_induce_sessions.py` | `b39b147cba318887d688de429a36b4df56a78b05c5c96accad01bdac49cc700c` |
| `tests/test_release_acceptance.py` | `f105f78ddff7581d8d2525d0fb187818abe7718d98b2ddf9fc43da547d982c68` |
| `tests/test_release_text.py` | `304cd9540a21552c883e73c82a5c442bee424493ed7c21a5a45e30018a152640` |
| `tests/test_replays.py` | `fd01cadddf49fc3573d7d6f5a90b7c80631159b8c0178310e90d1a9854e88979` |
| `tools/check_installed_docs.py` | `3612607a9d4d81a5941798dcedc8052aba4e6fe8ff26fdc0d857dffe01e03f7a` |
| `tools/record_induce_sessions.py` | `f13d2e23c5988aa755bd2974f416392abe9248cc4a25268ddd1c924630ccf23e` |
| `tools/record_skill_sessions.py` | `83eef9d8e19906c21681ddd3471d924f0fcde6b1a8ac86f4f5ab06af2899e468` |
| `tools/release_text.py` | `f9377ed044f8f15afbd36a4be19cdaa671b9f965cf573d130e91296905aaad04` |
| `tools/render_replay.py` | `f2e52d473ed50ac9413605cf6eac793e2b23c967b87da25b7c9f2700234cd498` |
| `.claude/launch.json` | `d6a799d2bbf773253c5c3d1554a24118e3e04a327efffda181e02eca70733f9e` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log` | `dfc92cdafada97528e29dd04c0e8216a10d1cd6b7f6655a1da7302664b3a570d` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/review.log` | `10f7ec28706af4d71dfac5e72490f18bed2022195f1c27230300a5faafe9d8cc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/review.log` | `a19a071baa8ad7afda0e8657be29006518ccae789c6f1bcdfc6d8b840514c553` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log` | `61b8189d5c3f37a4536085e0f9d30f09b9fa1849c3981f47e659bb26ed802b07` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log` | `d0e90ec94c66fccf5adbf073dd259d5861ac05e98cdfddc8f541ac04242033f8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log` | `05bc3b2eb8c9636dde3db8d5b71a5ba51b59ce06700c4cbc686dcff7c7fe1f45` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log` | `e83ab190ab34f86b255479d6d528916dd076b2fa03477769811f34c2db0aa699` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log` | `089fe70f90199f11bf7cde276085671f08b8875bf852aa83798d1ffa4f30c3dc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log` | `60113bbb25a9c8716354f64e817d3858f20eec58237f5887bb49edbb4534f2e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log` | `ffa10e00994837a411eb06a46b4c9d5a88c5ae49fb1299a1ca6cc1ef3dbf1eb0` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log` | `f4b07190f8502f9d663092c3f1127e5c65a2ec57a5b8105373069c86d7756579` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/review.log` | `f23ce9c86169caeaaa8828030900ce41eb63a0180d84beb908b9783827d25a60` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log` | `fea01bd06eb2652c4d34fa933cbb2d8f87e118d1b9b7a1b23937a6fcdd7e130e` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log` | `e2ff39ffe4763efc90d2c4ab6ac7410c2d1eba8a76fa5654f305cd97f99882fc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log` | `ab2e91fd3becb81067dde5f1681f0f1d10bdc83fffa9156163a1bbc4e3df3d34` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/review.log` | `97081678f1accf06646ea5d3c380fdc4dec15b77ff19598ae2f7eb1c077f1962` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/review.log` | `6db634fb7408b7c272fc10b1f860ae9e940be4fc8e21e7fc8835dc78de13189b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log` | `e4ca0c2def1bfa88799d5a3ecf9364edfafb1cc8cc6b06c478b6d47603f5276d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log` | `cc7ad08e74abd2ed82c481626055160e4bb6433f8ea1bfc4e2f1509bd1d7c558` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/review.log` | `177140b83b6631167ce6e8e52ad948c70275e43ef28c65331b07414288d70954` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/review.log` | `6bfa9c92654eeb3ad04e58f243c6d7fe8f005ebdfe1a44919a5eeb85f1fc9d20` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/review.log` | `c5f7b7a60c9dd895ce265e71da07728781fc88556482e4f1607d1ac2410992cf` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/review.log` | `05adb376ca4cab85e3cbd682bd4259ff6a7dc6e606931fcd57a3d3a2f4a69e17` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/review.log` | `64e611dae046275b3dcf16a2150227e44cc7df04c360516264479c659228fd4a` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r1/review.log` | `68bdf1e9e570e41eb7713aa17eff8194240cea2ba713db789280cd977fd05f97` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW3-r2/review.log` | `314b2c697c376c06f8a18557b8b978934d7a1f4f732e6ab8a702ee6e1d203f62` |
| `.gnd-planning/reviews/issue-286-r1/review.log` | `7037c493561f5b3b1ec1192928f52711b791522e8dbd00e33757cf1e1d33ffff` |
| `.gnd-planning/reviews/issue-286-r2/review.log` | `2afc409f5c98dc1a1f1e4ed7730846b88e616c5c6d819436aaa4feeb7d57c8f9` |
| `.gnd-planning/reviews/issue-286-r3/review.log` | `71db7d43c9041498ebb5d233b03cbead691338ce6b96b695567494114dc0f9a6` |
| `.gnd-planning/reviews/pr-289-r1/posted.json` | `d45445840654df8b8ed734969d1d7908a76bdc820bb3bb69d8073644bc2dc5af` |
| `.gnd-planning/reviews/pr-289-r1/review.log` | `0837868e93c1dd56fcdc7e43d504c108b9445739be72e8bfb587a7c24e5b45f1` |

You may read anything else in the repository that helps you answer.

## A standing check: code fitted to its examples

Whatever the question above, also look in the code this change adds or changes for a
solution that handles the examples in its tests and fixtures, and not the whole class of
input it is given:

- a regular expression, string split, slice or index over structured text (JSON, YAML,
  TOML, source code, paths, command lines) that a parser or an existing reader in this
  repository already reads;
- a pattern over output this project renders itself (a report, a table, a log line), where
  the code could have been handed the data instead;
- a pattern fitted to the fixtures: it matches every committed example and fails on a
  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;
- a branch on one literal name, file or message, added to make one case pass;
- a second matcher for something an existing helper already does.

A regular expression is not a finding in itself: one that states the whole grammar of a
flat token (an identifier, a version number, a hex digest) is the right tool. For each
suspect, build a legal input that the tests and fixtures lack and run the code on it.
Report a finding only with that input: what the code returned and what it should have
returned. A suspicion with no breaking input is style: label it so. In your list of what
you checked, name each matcher you tried and the input you tried it with.

## Rules

- Read only. Do not edit, create, stage, commit, push or post anything.
- Do not open `.env` files, keys, tokens, `auth.json` or any other credential file, and do
  not print environment variables. If you need one, name it and go on without it.
- A finding names its file and line and the consequence someone would observe. Run what
  you can to show it; where you only read, say so.

## What to return

1. Findings, each with an id (F1, F2, ...), file and line, what is wrong, the observable
   consequence, and how to reproduce it. A finding with no observable consequence is
   style: label it so.
2. What you checked and found true.
3. What you could not check, and why.
4. A last line: `VERDICT: APPROVE` or `VERDICT: CHANGES_REQUESTED`.
