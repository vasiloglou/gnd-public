# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This is the whole diff of milestone literature-reading-reference (LR1, LR2, LR3 and the close). The phase reviews and the close panel are context (PANEL-REVIEW.md). Read especially the bytes no reviewer has read: LR1 commit 60306a5c (docs/guides/documents.md step 2, tests T1 and T11), LR2 commit 45551cf1 (tests/test_lr2_quote_scope.py T5), LR3 commit aec93739 and the close fixes 8baf0eda (src/gnd/examples/literature/reference_set.py, reference_fixture/README.md and labels.json, tests/test_lr3_reference_set.py, docs/literature/index.md, notes/issue-reply.md). Do they do what close-results.md says, and does any claim on the pages, in the README or in the reply go beyond the code and the recorded run?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every criterion close-results.md marks met is met by the code and tests at this commit; LR1-C3 is met in part exactly as stated.
- C2. The label scope rule in reference_fixture/README.md is what reference_set.build computes, and score.json is what reference_set.score computes from run/ and labels.json.
- C3. Every departure from the plan is in close-delta.md.
- C4. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `origin/main` to the working tree at `8baf0eda4c2d`. Its diff is `.gnd-planning/milestones/literature-reading-reference/notes/reviews/close-r1/diff.patch`.
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/007-milestone-close.md
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/PANEL-REVIEW.md
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/disposition.md
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/responses/claude/response.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/responses/codex/response.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/responses/glm/response.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/responses/kimi/response.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/review-request.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/run.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/evidence/close-review/synthesis.json
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/close-delta.md
- deleted: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/close-results.md

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/close-r1/diff.patch` | `66e6d3feb1ec9f95467dbaaff9b09ce95a2ee2ffc9e735b579c62b39754b0c19` |
| `.gnd-planning/PROJECT.md` | `d1f4c3585d459375e724a4f2511c7020de720f05714ec6a25d709385a7d305b4` |
| `.gnd-planning/milestones/literature-reading-reference/001-plan-gate.md` | `e351ba13ad7794411f5b64b8e234331094bfb5e8635f77e6e17dac482f97cfc2` |
| `.gnd-planning/milestones/literature-reading-reference/002-phase-LR1.md` | `c5cab5ed35735f750c19746a66c8ec1b87f312c37969d3f7344ebcb438e6b767` |
| `.gnd-planning/milestones/literature-reading-reference/003-phase-LR2.md` | `ee7de414d19e60fd96f0d132dfa5579458d2eb2c477f4bddcbaa52ab906d1b1d` |
| `.gnd-planning/milestones/literature-reading-reference/004-ruling-D3.md` | `fa032b6734cd78e9d2b5a1fb1166694bd78f8955e6f190d820aba81dbc83a708` |
| `.gnd-planning/milestones/literature-reading-reference/005-phase-LR3.md` | `aa375e36f26261d47f5f4f0a79b8443cf2655e3a7948e45ead5d38e4e14ed6cc` |
| `.gnd-planning/milestones/literature-reading-reference/README.md` | `b3b5af7b7f81368e5e0a28d2137c81737d05550085b3fa8a9b69221752292f9e` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/LR1/final-gate.txt` | `c017f680963083f3e61c15fcfeff6098397a68865e5df422dfebb7fcfccf9bbb` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/LR2/final-gate.txt` | `3dc68c393c5bbbfafc13bffdb109854d5322de02cb709515ecfb2f5c3f5ec15b` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/LR3/final-gate.txt` | `b7d46023a5823d14bb68677143cca904ad6ed9c002e3acb4b9543eb58f3ebc18` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/LR3/pr245-replay.txt` | `b3f69dba90db00d5e84163d6b5c5b6609158c1cacad8094ec29cb1bb9648071f` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/PANEL-REVIEW.md` | `56d4fd6709db7be511e679d72186cc745838bc76052f785000cfded30918d9dd` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/request.json` | `cf62b562cceaa8c5e6433af8d0c2dd22c9cc1040c5376ffda31007bbce354927` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/envelope.json` | `259b2a3862cc7e1419fc99719b7d5d7a1790b37565c43fed7e5e06cc3243597f` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/response.json` | `baaa5ae4e67f8397c067730ab913823465c800211eaa9d138014c4cde6f1fb93` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/claude/stdout` | `cae76f2585577a9fff09de4e4f7cd0374347d616d3377987fb7db0da062d94d7` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/capability.stdout` | `df0d864ca2076f7654288c6a1e3394e3eaa2ea8f15021df2524efdd90c70986c` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/envelope.json` | `44fa7f0e4ac03e6e4e87c78d7fc843cb2ed3a2ebbb1f56ecee27d29c96d5f169` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/response.json` | `cb83a8fd7b5121a6b3c8a28dd9d3343b9a58067a40972ba42810a916303a564f` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/stderr` | `2d5c0f3c45831d117761eeb93b2c77f20d26d00b16ebd402cc006a42eaeb96c0` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/codex/stdout` | `93c52170a1b471fd5f0ebd7d34b565627b694b674595665d87ad9cd205eb3d21` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/gemini/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/gemini/capability.stdout` | `b5c6e1af180f48adb3700982e7b06e905f29d2965f047eaeebd0b5c4f676b632` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/gemini/envelope.json` | `a86108995304bee4bb459e89d677d30537d627ac874a7b182e944c096b079f6f` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/gemini/stderr` | `5a566fbdde7eca1c0d518cde0285da16e4061970888883844397ea2ffc920ec3` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/gemini/stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/envelope.json` | `3296626e60f7793c655d164e325102ac4b21f31bc0650f4f3f31fad0f5cddde4` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/response.json` | `2042be8a2f0c4be2ba21d7c586d4a4f63924019429794449046641d31d54d1e1` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/stderr` | `84a7a92addfe6124967bec188da43c69300fa0c093fdc46484e5700bb5091db1` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/glm/stdout` | `54a6c90b7a77551b6e31f26d7755947c0a8abb6198554070c9773a12485e1a89` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/kimi/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/kimi/capability.stdout` | `38366cf8f3a746da0527b722bb8f017d5cdcecd16e6885148a05b19794ef0ca0` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/kimi/envelope.json` | `12fcfdcbd11350a314920273514d54bbe2c65ac5bc2fd2d18e50aa8bab1c6a40` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/kimi/stderr` | `13e5a6323054d09fab415ed08008dc06285516024c7193f4ba220c470056825b` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/kimi/stdout` | `a8352f01acea535389e54ed86ca858a65de6f8e0c55a996488057f04012aad8b` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/capability.stdout` | `a8b68ecacf715b6c89ced11b02c8f25c46d35117f2eee5782882f2232a2d4c66` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/envelope.json` | `d7553cdf3dd44dffb3cc93dc94862f4d1626ea9309d9348ab4ba744069dee02c` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/response.json` | `4a88428e66a6ffec0826c1bbf18db5981aa819ed6021a4f58974ec8f74d4d179` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/stderr` | `7f47e77adae01cdd6d9190bb3a010651b48c47bea02e862f28e3d21f16ac70ab` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/reviewers/qwen/stdout` | `0a5c67b369ee38ee6d68d032891ebf5f28514d09ae33091afef5a3517bf7aa9a` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/panel-run/run.json` | `01db1810bb3dc40be6349acc024c006890bd1c91f966de15ab01c46986e2c885` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/review-request.json` | `d360e59a6d1fb9021d3e528e3e2210e1100935bf5e6d7e0058b12d3a8bba802f` |
| `.gnd-planning/milestones/literature-reading-reference/evidence/close-review/synthesis.json` | `d0898567540e2c35a0bce8d8f9e118cd4ed1d5f8d0c9b273ba3e9bd64847b3c0` |
| `.gnd-planning/milestones/literature-reading-reference/notes/close-delta.md` | `5c8ae9e547bce246778f130649693b72efa86652fca699efc5302eb01a3d05d4` |
| `.gnd-planning/milestones/literature-reading-reference/notes/close-results.md` | `7d6f47ad56f4f60460d42b31bc12ebe7314bb494f0585a8b423d50f591d4c61a` |
| `.gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md` | `c698f5a98bdc739e48fe94e51df59ee3943883bfbe2817e460cc06505659eb2c` |
| `.gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md` | `6dcf10929081330322d385c83cc3c21347a7ab6bc54c270ed44663eef7654098` |
| `.gnd-planning/milestones/literature-reading-reference/notes/phase-LR1-spec.md` | `0b1bdd6166acf0fd064d0cdea1d2510dc999722c375cbdcd0864f0fb4f732285` |
| `.gnd-planning/milestones/literature-reading-reference/notes/phase-LR2-spec.md` | `a40492d71fdb3d7d236f399f133b773835d5ae6d4ee0141516565ccd6674197b` |
| `.gnd-planning/milestones/literature-reading-reference/notes/phase-LR3-spec.md` | `e86e601c9adfe2ebce66da918d28c7c92db87a9459118bc87f52dcf3aab00b2d` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/BRIEF.md` | `4b243f0c3a62b96ccac3dd4a22778e9ff401bf439d3e7cece8758e3fe9b6b874` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/FINDINGS.md` | `df8e3a0b3004fb87f0ba4b04326256ab5ed7ba23b76652a8c61fad62b9e3a0a7` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/brief.json` | `3a3faee733191e0a74a73c1b4856a68694b35e39008d9fb5f94a7781f024cd59` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/diff.patch` | `fd246d1caab2cf284ab9dfee9df81350e2b7ddc9b01f371f0774c3ec0de16e59` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/review.md` | `91ef1396f7b6429f93f41d2c48b499ce8d9fe26af1887e6769820dad680e16fe` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/run.json` | `9fe8a1a98c13c173118dbf2520f209224a94b27787f7d17ffdbacb0a380595ef` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/BRIEF.md` | `231dcbcfab7ed07c086954305de8e38f7cfa33bb390790aee9d5b8681fc792a6` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/FINDINGS.md` | `373105c209645aef29592ad3fe3cb1e7549b8221640b249c42254edb46e9a3c9` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/brief.json` | `03084dc073e57ce24f792374777ceff1392cda2e0457e1684e826cff7d91c8c4` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/diff.patch` | `e0161b50a27568e88ec51aaacbd408ad535acd30f8ea61c6693f4b28325d79bd` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/review.md` | `4b13e9cb8edf91f45329099c3c1f426bc7d59e6cb667f0d281e0f2380b5162fb` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r2/run.json` | `dbaf5200376ca39a5b48049fc4ec3d9d5373fd076070943b75678461d24a89cd` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/BRIEF.md` | `69bb7b67f9fd2c68c890399cf8088e637881501226f093a9807794d944fde991` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/FINDINGS.md` | `31148ac6aa674939597dd392ab1b304ec767b60763fa298f2ea1b99d894a6e78` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/brief.json` | `6e031c848645b4a2390fe8f6b1542c70b50a7a36d70fe3f4cef0c5fdf04f3b98` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/diff.patch` | `664f87ab74416b223359794ba83e27d9553f29f5983fbaddc706b1a2af3026fa` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/review.md` | `facc6e749aa04bfb8504f824dc2634087b067d75cad3936b426f92fc677357fc` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/run.json` | `2cacdd7ff96095f076b4435f492c86f664c03938095fb7efeb0387fb3087e5a3` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/BRIEF.md` | `0e9c57e3ddf877895c0371a324770bf105d216e3e5ed436661d4c27e2c046810` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/FINDINGS.md` | `7c97a8a2d5b2dc7a4749a179030d47fa1d80fec6249d5a07aafe2b8bc066c5d0` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/brief.json` | `581c65006cd7171998afc79851cb1ab52840b354c640c9b81e4e84d4878d580a` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/diff.patch` | `1f84df2c82755dbc66b0e87da173833b59a10d80a9112e9c18814e0059b266c3` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/review.md` | `c24cfd951a84c66a2df2262e33da5f129e6060cc18baf067e13cacffd464fb44` |
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR3-r1/run.json` | `9a1eb9edd1b81372c8c46ad57921250b7cc8623aea702da18c54f6252c10d471` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/README.md` | `82a0413e8b2dca8cc1282c6a1e8991874f29a9a4fb9b39c805551e69a309437a` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviewed-vocabulary-growth-plan.md` | `72710267b2dcdacc82b46014037ba0df74c345439e96f62b4ba5db52617f7ec7` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/PANEL-REVIEW.md` | `3e39b57d57d2a3ee744535dd97e2b0005f0ca3093a631b8e5ba0b67860d686c8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/README.md` | `75b21f93ffaf2dc646d8f97e9121fb6e3418f3f7ce8ab2d0858eb2e38bb0e6e8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/request.json` | `1deaec30d34457cbefbb9169bebf1f5d94525d7c3dfe61a9b70e556364b72775` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/envelope.json` | `21ad4226f4f7021c770f1dbd4d26e87908eaf7b2f92257b274ee9feedd33fda8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/response.json` | `e1d1d1b08bf683fea5ca7550fd5413f6effda4caeee45fd64328ac81623b278c` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/claude/stdout` | `ee766e0d4bcf7e0b870bcf37dc8a3920f04a05b52ad89e7401963a218b779cf3` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/capability.stdout` | `df0d864ca2076f7654288c6a1e3394e3eaa2ea8f15021df2524efdd90c70986c` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/envelope.json` | `8c949c1fef5fed465810d5eefa14cacd2e804e62ed13e32067bd8ad036dc0f81` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/response.json` | `90bf44ea4791752a3bf52945c9799a3d0817b4c56e8abd5a2587e9df0dfee728` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/stderr` | `5e84cd3a2206b8c153871c783d3fcb6c4686dedecfc86ec9f535f753e931db1b` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/codex/stdout` | `0a778448bd0dc67a98dbe26090667cce5eb62d48d78987a790d8ad9a806f78d0` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/gemini/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/gemini/capability.stdout` | `b5c6e1af180f48adb3700982e7b06e905f29d2965f047eaeebd0b5c4f676b632` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/gemini/envelope.json` | `5f62360b93e6fc2612f2c256ba6d4b1a08b28ac9886046990ac41828eaf817a8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/gemini/stderr` | `5a566fbdde7eca1c0d518cde0285da16e4061970888883844397ea2ffc920ec3` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/gemini/stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/envelope.json` | `a5396dfbe3e7e17fd974a210a1675ee12965b615d15a3851d693ba2ed488a654` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/response.json` | `38d9a53627c3dbac032457fecc8da72236d1ed72b5892affdaf2d414ee74960a` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/stderr` | `84a7a92addfe6124967bec188da43c69300fa0c093fdc46484e5700bb5091db1` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/glm/stdout` | `571a26f06c6c9b3d9d1b8f1088b16551e8c8c7698a2efc27323bf9634f37434e` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/capability.stdout` | `38366cf8f3a746da0527b722bb8f017d5cdcecd16e6885148a05b19794ef0ca0` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/envelope.json` | `ad1aae4d354be8cc525e2e5c240d98e658fa275a17ce3a96344c2cc1d849bc18` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/response.json` | `0c8a23a719d1144805b993128abe027684e91be43afcb050f6c16471e2c368ca` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/stderr` | `4dbf74aabe3a90d80bd75c7740a462dc4f76996f7844a6cff8596df3f7070709` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/kimi/stdout` | `1f70a355effad3353567a482693c8b388b17310d3afc441cb2bee9f7b961f5e2` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/capability.stdout` | `a8b68ecacf715b6c89ced11b02c8f25c46d35117f2eee5782882f2232a2d4c66` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/envelope.json` | `06e951a9142fc67cdfa917aacdfabb36bf907058f218d032f01a5655e557fdf6` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/response.json` | `bde10ef8d1117c957827c23bfc196ede1debb3592fa56e10d2d5b984f0b2f886` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/stderr` | `7f47e77adae01cdd6d9190bb3a010651b48c47bea02e862f28e3d21f16ac70ab` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/reviewers/qwen/stdout` | `37e0901fc6d50ea52660ffce747431ef2312228c82eb65141e2af00bd6947b9c` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/panel-run/run.json` | `24c570d4a176390b4eec57b55f95d1844d5e057642e87011f096990d8e7c6ada` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/review-request.json` | `161ff11d0d46b50219e22fdde6b5a9e442dcc28ca5d241b982ff6d87d1ab8c94` |
| `.gnd-planning/reviews/literature-reading-reference-r2-panel/synthesis.json` | `768b7cd91da6b509580c5433c8c4ffc0964fcec8179a0ec031e0af69772db8f3` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/PANEL-REVIEW.md` | `557adc924bcd5a6bee6995a69c3f4a26a41ce92977011f5521ceb360e5c71c60` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/README.md` | `d9a96474247553f2fa772b4c48053a4388756d194e4eb2e01b83943caefc2b63` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/request.json` | `fd8742b12f22a186db77bff9906c78dd43dfd6eca2fd51cabacf2ffea4c47755` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/envelope.json` | `28294b51464b08c84e7b8dade0c0013b8b84b88eea8b81970129fea0b713e8eb` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/response.json` | `79ec6b2975861f8707a299484ed77b98c60e05244a483d178c042d505da256dc` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/claude/stdout` | `c1959689b462fb0730f6ad0cd5968a3ccab81c7eb9c4f9e34ecb2869e965ac8f` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/capability.stdout` | `df0d864ca2076f7654288c6a1e3394e3eaa2ea8f15021df2524efdd90c70986c` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/envelope.json` | `f86bb42fcf005189c82abead4e86d38cb67c9fcd31a93d3e0844b2ab2ee3e0b1` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/response.json` | `4cf6a135dc90e4b580e59bb6fb8eefe331a26dfa2db014b614ffe4d025faf94a` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/stderr` | `dc4977588c6a15bdee31683ecf1fa36d334bce430acab54f8545f0abbb8cd8e0` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/codex/stdout` | `c7d03675e06f46801d163d60c6cc6605edad7c18bfa0f1d1004a08c0caa32bd1` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/gemini/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/gemini/capability.stdout` | `b5c6e1af180f48adb3700982e7b06e905f29d2965f047eaeebd0b5c4f676b632` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/gemini/envelope.json` | `5608c1b39ce06f313088efad3be2f79b9b0879a3d1c473a74bdf6d4bf551cb0a` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/gemini/stderr` | `019de5b03b2b189ddfe56860119b17ef90b58c456eda380317fffbdcd64fc144` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/gemini/stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/capability.stdout` | `5ca3a9dac2026e56c221fdd34380c7d7d45ebbb51c1d01b7c17c75cb076a0be8` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/envelope.json` | `cfaf2d6d30f969437a5af9f4d7524d583617fedd0c0f76ed8e82cb238cfe9626` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/response.json` | `41ff14d30760ed8bba8a2a3b70f2d95510e885dbfd48fd2e3fadb4039de93c1d` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/stderr` | `84a7a92addfe6124967bec188da43c69300fa0c093fdc46484e5700bb5091db1` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/glm/stdout` | `d3a87f31a2a3a68ab106058cde97d62fb0404d9406c613232068d363c6cc84bc` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/kimi/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/kimi/capability.stdout` | `38366cf8f3a746da0527b722bb8f017d5cdcecd16e6885148a05b19794ef0ca0` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/kimi/envelope.json` | `915d9ab3d5eda400c73ca49971b6ced98a6ce8849e2c8b8f249a7f4835eead89` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/kimi/stderr` | `0a98b86156372e4c2a53976e8751910a2c6dda55813718fe34c30a2d6b5f7e7f` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/kimi/stdout` | `66ca4f6e41719b6c7d4be5d55e73853bbf7280b01eacaff5a8b33fabeadadb30` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/qwen/capability.stderr` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/qwen/capability.stdout` | `a8b68ecacf715b6c89ced11b02c8f25c46d35117f2eee5782882f2232a2d4c66` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/qwen/envelope.json` | `a85bce9961a156541e646b289b3416996df30304776ce70c4813966c0f7bad94` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/qwen/stderr` | `c67c47be24784ea5efe92c3a9b44f9e2dcce140a50f328fa1f78ca47f4d47190` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/reviewers/qwen/stdout` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/panel-run/run.json` | `d3ae6e7574339404c8d72ed5969cec5b82731038d4a9744ef7d9bbbd18b9f7e6` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/review-request.json` | `fd1d84247646cf2fc2effcff03b2a78b5ab1375b08d3cd5d6a8efa88b2c3f8e1` |
| `.gnd-planning/reviews/literature-reading-reference-r3-panel/synthesis.json` | `0abc196845ea6f6f1a68f1e6fa2cdfa72b136ae20f0920171daa59c10f794f3c` |
| `dev/components/COMPONENTS.md` | `aebdc62a4a40ab4f4a4395a7ed3aa682ef60e4d305dc2e5f3dd10c971925d1db` |
| `dev/components/graph.md` | `df8328e04315628e2fd65cf59a500946745b2f6bce44d429d928aec37521cbf6` |
| `dev/components/modules/examples.md` | `b3de59106772de37fe21e1576b8d34904f57e5f8edb0bb2a26d8069777a03b7d` |
| `dev/components/modules/tools.md` | `44b230f62a0ae3323c666b7ecdef432c08b330c2040799211b0d27d940332a1c` |
| `docs/guides/documents.md` | `f810f3a70f886c46beba0474f68cb42383c15d4ab61ddea7c4e2c3126103d0a3` |
| `docs/literature/commands.md` | `74bb879bcb1853c4060f251a9270edb28eca4c59cb7aeb23f0cd63720fa539a8` |
| `docs/literature/index.md` | `9ef3f51f42582ac89f18fd64bd82acbb66e4a7b239b771ea759ef00eff303eba` |
| `docs/reference/anchors.md` | `adc5acc80c4f339789f5d6440d2c413b2bcb9f924b5ef84635cc0086b155467f` |
| `docs/release-notes.md` | `0c5b7fc138fc052170910605b42e7e34a42c1bb93258f91e44dd140e0a1c0643` |
| `src/gnd/examples/literature/README.md` | `e1c6de130423cf9af698e147e34721af42b61202d71a24c192a80b0ba0a88f81` |
| `src/gnd/examples/literature/reference_fixture/README.md` | `e8d35d33efc43621ae4e934e16982fd1d2ee94ede83d20559433a3db99d97fe0` |
| `src/gnd/examples/literature/reference_fixture/apinn.txt` | `c7874f2817d05f8d8f7088e1dda4c60edbb974fddcb570d96df9951c5d8f15b3` |
| `src/gnd/examples/literature/reference_fixture/boltz-1.txt` | `1793ae0ee0e958e6dc4d63e05d40c2676d5f9d0f77bda4f35b249c31ce560282` |
| `src/gnd/examples/literature/reference_fixture/corpus.orm.json` | `028966e0415da601e90fcde38515d5931d09895f871bce156499f9e2565519ab` |
| `src/gnd/examples/literature/reference_fixture/flows-review.txt` | `63117900d4dab49ea0e66600ab46076050d707f6638b47d0b85542ab26d9c27c` |
| `src/gnd/examples/literature/reference_fixture/labels.json` | `f3fddf0ea58c7e8cac303b0c0c1d0e5155f830c9e801622626f03feefb8698dc` |
| `src/gnd/examples/literature/reference_fixture/opencap-monocular.txt` | `cdbd542ab0c3ff71466bdfce8db8c1985fa86cf3ffc0a77a0decceb113a89d7f` |
| `src/gnd/examples/literature/reference_fixture/pinn-failure-modes.txt` | `c9fdf5bcd4e55636ebde6eafa76513b4b1db0906184d9ef19e877b7ecb5194cb` |
| `src/gnd/examples/literature/reference_fixture/posex.txt` | `f8842936ae0dc354c0cb164513146383fda8d019d108b4a1210d8b2bd59de56d` |
| `src/gnd/examples/literature/reference_fixture/profile.json` | `c22e5080486c7f0be8f9cb34662eb8d24a2de34ee1dd81888876cafb94ed921b` |
| `src/gnd/examples/literature/reference_fixture/roster.json` | `18eb3ae95da5f02e98d2c75a76440d3954794cc3f51426625e3337655a4e399c` |
| `src/gnd/examples/literature/reference_fixture/run-record.json` | `ba9c72866b1a682f9e8f66acd400f9713437145deefb5c256266008f5cd4956f` |
| `src/gnd/examples/literature/reference_fixture/run/broad.population.json` | `5f43e98c2b4398a8fafe853525de785d275862527b6e0eb741e6da4473437fc4` |
| `src/gnd/examples/literature/reference_fixture/run/coverage.json` | `9d315164152f5b78fe4498c13a857f162d82d2a8ab79b028e85b5e62c12ae8a6` |
| `src/gnd/examples/literature/reference_fixture/run/payload-0.json` | `e52ef91cc4a034d377f7dbd2f25aee203fcc81232568c0344ff80911c879ca33` |
| `src/gnd/examples/literature/reference_fixture/run/payload-1.json` | `2f089f5a7f6d68c0736d521bf9210f65fc120221da04b184f4519bfa67b094eb` |
| `src/gnd/examples/literature/reference_fixture/run/payload-2.json` | `467cc35a6c1ef9b0a8b1208f1d73f1230a79ea71ba8e7e5f16046fb8cd850d21` |
| `src/gnd/examples/literature/reference_fixture/run/payload-3.json` | `d3ae34a6bfb6f89cc3e188a9d17b0583928e923f8e052b746181835766daed23` |
| `src/gnd/examples/literature/reference_fixture/run/payload-4.json` | `7a684d3c760b8f2e70022ab33e02ef72d3d9960529f62b735949c3478a52e441` |
| `src/gnd/examples/literature/reference_fixture/run/payload-5.json` | `2cdda56eac4526d9d22dab9f6d20d45387ac4333fc91db7eb7a8ea3caca2a293` |
| `src/gnd/examples/literature/reference_fixture/run/producer-output-table.json` | `984fac77fdeebce3b89bffe1dc938fcd2096d0dce8a76bef2ee6d92cd8a6b601` |
| `src/gnd/examples/literature/reference_fixture/run/run.json` | `b903f36284000757372c156332f111bfbaf62368b155d790af55a4e10839b192` |
| `src/gnd/examples/literature/reference_fixture/run/stage-0.json` | `03d8a20acf53ef33d635e2145bf2e56ebf380693319916e35fb62ab5f2c11dad` |
| `src/gnd/examples/literature/reference_fixture/run/stage-1.json` | `8bdc72fab86cc7d9cb1be9393efecd40c4c4526cef8230dca33590d19f96c053` |
| `src/gnd/examples/literature/reference_fixture/run/stage-2.json` | `a1d74acfeb9a1461d8f907ca28f43546d0a1132815920f61463f406e45eb48bd` |
| `src/gnd/examples/literature/reference_fixture/run/stage-3.json` | `3be2c7f08b727c4f8c17432fa00cf285de41b8fea8ea0b3faa96b44bc8c7a1eb` |
| `src/gnd/examples/literature/reference_fixture/run/stage-4.json` | `98ae36d34f81b2ce138bcf8cec5573060d6a8d9c3c41b32b689f08a329327eed` |
| `src/gnd/examples/literature/reference_fixture/run/stage-5.json` | `56ab1a875df6c4e2619e881ca0ee217fecdb415da8c10f3d251272b3e068f133` |
| `src/gnd/examples/literature/reference_fixture/run/targeted.population.json` | `356e61d418e703e8d688565a077e505d1bdea8b79e33e9601b431713f2fa9979` |
| `src/gnd/examples/literature/reference_fixture/sbi-frontier.txt` | `36d3292bdfd72d369d772cff6c480d6eab4b15b61346aadbccd1a7cb9b20ac93` |
| `src/gnd/examples/literature/reference_fixture/score.json` | `08c4830c3fefe901f6452aa62af4ceddf86b3a281cc14b264d162adbe3bec2dc` |
| `src/gnd/examples/literature/reference_fixture/sensor-placement.txt` | `cd40b61f0e07fb4417602b2be134222ff20fe435f19317742e60742d2f27d4bc` |
| `src/gnd/examples/literature/reference_fixture/vampnet.txt` | `6445f1d2f55e346d9ceb740a0bceca27ee48ecb14b3fb44ffbafad171b0e7e7f` |
| `src/gnd/examples/literature/reference_fixture/vampnets.txt` | `eb1bd85d000c88ad8852ec49d0f7965d663b57824ee4df29dd0570d318b3c34a` |
| `src/gnd/examples/literature/reference_fixture/wham-pose.txt` | `cb7fc5f6872e104ef56dfddff2759f47e622bb1ecb12c3062be23a6554a0c642` |
| `src/gnd/examples/literature/reference_fixture/wham-whale.txt` | `2808abd557e822b7350717a7b4ad268cc290f50007b26d5ec421b8d95922a021` |
| `src/gnd/examples/literature/reference_set.py` | `0e1e1255309120a9fbed59dbdc59108be43225926aaa1fe405700ed623db9f2e` |
| `src/gnd/skills/gnd-extract/references/extraction-contract.md` | `3af890ab079323e6f6d4a3d11a8a99bcfa253051196e6fa578313f5a1da4ea08` |
| `tests/test_documentation_tutorials.py` | `9dfa5685b9e0e9471b14d9e9cfc8569e2306980db62c9ce04486c5943334257a` |
| `tests/test_lr1_verify_failure_listing.py` | `39f08e5a82f3a5951c30f0edfe4af0ff620bded065dfdc4b7100eee985137156` |
| `tests/test_lr2_quote_scope.py` | `beefa09ac5f8abe8001f008187151014dc504f865760c07fa2290efcaa578e7e` |
| `tests/test_lr3_reference_set.py` | `295351d24510db4391ff8ba58299859a4f4d44481c1a02073abc7a31566514b9` |
| `tools/record_lr3_reference_run.py` | `38ba4fe00ff81e9a78ddd725f29b8c728723d287988a2bd5dacd5c5e292dfb60` |
| `tools/run_tutorials.py` | `06ae7f3a7919b30faf6e67f4a02344aa3aed1e8bb7dfd68edf97d0f20ea1b156` |

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
