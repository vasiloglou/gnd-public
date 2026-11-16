# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does LD4 refuse incomplete or stale release evidence and reproduce semantic migration, earlier evidence, and both independent supports using the public routes?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. C1. Independent policy and selected snapshot identity fix the required inventory and dependencies before payload reads. Each missing or changed kind propagates only to its descendants.
- C2. C2. The three false ancestry paths disappear and two unaffected paths remain. Old witness replay is independent. Source-qualified occurrence mappings and the ambiguous historical mention can be independently checked.
- C3. C3. The release retains exact LD3 artifacts. The covered absence becomes stale, unrelated coverage remains current, and the migration worklist agrees with LD3.
- C4. C4. Additive preview refuses the predicate edit. The pinned ordinary preview and apply reproduce. A stale judgment and its renewal use the same source and occurrence. The rule-only control has unchanged vocabulary.
- C5. C5. Both current supports bind distinct source occurrences, review evidence, rule and resolution editions. Independently replay each certificate and try removing the other.

## The change under review

The work from `0d35a0b0` to the working tree at `05546dc0c605`. Its diff is `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD4-r1/diff.patch` | `389e0c5dbc2631478f0a65d4a2ea0372b8b8721aa0381953c491d3e2e1efda57` |
| `.gnd-planning/milestones/literature-depth/010-phase-LD4-spec-gate.md` | `8e1007f5d45eb758915b307822a1af805067287b346df0103dc19739f84356e9` |
| `.gnd-planning/milestones/literature-depth/notes/phase-LD4-spec.md` | `b2a9f38c23b5acd3d1ea71a08d93181739b18aec589c0d66bf2aff90253fb638` |
| `dev/components/COMPONENTS.md` | `942bce7847238e70a36a0f25c8e0e9f26d9dd7ef706ab828f270806eb54cd919` |
| `dev/components/graph.md` | `cbaa09faaf450ae5539b88a16a5b116d023e184bf81e7c3bb89c3c6995d6b19e` |
| `dev/components/modules/examples.md` | `9017adfaa5967c8447f376dfc605698166d2f1a36bc8db60471e7f81c32223b1` |
| `src/gnd/examples/literature/README.md` | `bbaeeebecf893777b7011947b892f570a16e809a5376630e034cd30baf317f2b` |
| `src/gnd/examples/literature/revision.py` | `b838b9eff1beb4855bb1106327250a4b2df6100bb05dda0f2e813b7f2c2c68e6` |
| `src/gnd/examples/literature/revision_fixture/README.md` | `d58c7d7bd9b4fb7f2e6d99c47482e13149cfcb8ed211e10eb160a5247d7a25ec` |
| `src/gnd/examples/literature/revision_fixture/comparison/base.orm.json` | `d74953014d1cb2b202d07fed18fafc15babda733f7d949fe4f57dd4b1c1cab4c` |
| `src/gnd/examples/literature/revision_fixture/comparison/head.orm.json` | `59102aa094e725ca4c524993d705e379596937729de82382fba44b796cb155cb` |
| `src/gnd/examples/literature/revision_fixture/comparison/population.json` | `84b100fd6802d4bc00d7e02bcca9536457d0283bb3b779fb3eb984eef65cc3e2` |
| `src/gnd/examples/literature/revision_fixture/corroboration/document.txt` | `7e3da2ebdbb88d3905d1da82fb5623e4ed7b02b0f1fb8abc80bb4583db95a9ee` |
| `src/gnd/examples/literature/revision_fixture/corroboration/population.json` | `83b0ef3d28f7f49df0c4fd0b65ccea850ce63764c18cf9ea6fe461178243c151` |
| `src/gnd/examples/literature/revision_fixture/corroboration/population.json.anchors.json` | `3b65999e2ff302464ffbe79ba5fefd7a591c5df1430a59317d9e7e1c1113a1fc` |
| `src/gnd/examples/literature/revision_fixture/interpretation.json` | `d2e1dd6af05fa046be827eb2ab314bb1049c546f33c9c12a4db4199598630a59` |
| `src/gnd/examples/literature/revision_fixture/proposal.json` | `b0adaf0d29a613732eaead5cb60f9c10295520131907dcecfb0827570407f673` |
| `src/gnd/examples/literature/revision_fixture/release-policy.json` | `555e00b93fde50eae2dc7e9077c9f1a255e2ff169e9916c5b43ce38c0d194df9` |
| `src/gnd/examples/literature/revision_fixture/review-inputs.json` | `426c65553c3f5de4049ee7f6eea0321957ad6eae939410c182ca9a46d45c4568` |
| `src/gnd/examples/literature/revision_fixture/support-targets.json` | `633422d3770d8c26319804621c44575da86146b82d2d85710829011c63e86bf4` |
| `src/gnd/examples/literature/revision_fixture/targets.json` | `4e3ffa7df198388f17520ab7bf1303e44b36624031c1693d51cd3314d31b4a5f` |
| `src/gnd/examples/literature/revision_manifest.py` | `c2fbde3c1ad718d651714ac2e065014ce3ae28d4d884698bb7335505a30aad88` |
| `tests/fixtures/ld4-revision/expected.json` | `1d2a9464cb0596e86e73ba3d15753bdecb60efef3ddee4fb3819cafa847b7230` |
| `tests/test_ld4_revision.py` | `e20ef3851b2c2f078d370a10b630b93e43e01db38a4fae2586436b681dfc5344` |
| `.gnd-planning/milestones/literature-depth/009-phase-LD3.md` | `3637fe884e8a8e08eccb1c0538ed87152d840e5ad0c1b83d0f85cd13b064a9b4` |
| `.gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md` | `216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539` |
| `src/gnd/examples/literature/reading.py` | `bbe5b3318dba5f57743b90fdf238a6764b3dc10b221613ddd20f8ceb933c8b44` |
| `src/gnd/examples/literature/reading_fixture/roster.json` | `0a7d9a271c0c5eadad8f997439eedcea2557c83d0fba7bb137050e971426f418` |
| `src/gnd/examples/literature/resolution/model.orm.yaml` | `b5120440ad128f3853109f247ab928434e59d7ef74cce55edd935f886348f5a4` |
| `src/gnd/examples/literature/resolution/cases/W-flat/manifest.json` | `d17c306da1388ab52a3ca9a4e17454438dd8fcdac6613b3e3694a9ce4b5e498e` |
| `src/gnd/examples/literature/resolution/cases/W-resolved/manifest.json` | `96d787708e7b641408e3072ee9b4faf71305eaafff2b28b6378c544a9a9e1f6d` |
| `src/gnd/examples/literature/resolution/cases/W-resolved/resolution.json` | `8804cfeedffb014c792018ada339c1acf4067b8dda79ccf91494a6cf1eb7db60` |

You may read anything else in the repository that helps you answer.

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
