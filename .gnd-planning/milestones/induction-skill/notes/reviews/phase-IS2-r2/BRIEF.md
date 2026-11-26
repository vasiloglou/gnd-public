# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 2 of 2. Do the repairs of round 1's fourteen findings (ledger in notes/reviews/phase-IS2-r1/FINDINGS.md) hold for the class of input each finding names, and did any repair break behaviour the IS2 spec (sections 6, 14 to 17) requires? Report defects with a concrete input that shows each one.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. segments(), outside_words(), PATH_WORD and the done predicates read any legal shell command and stream of their class, and recheck() over the kept runs gives the published results
- C2. gate_ok refuses any file but a committed, unchanged gate record in the milestone folder, and --model admits only haiku
- C3. finish() refuses any recording holding a T3 ABSOLUTE path or the git identity and keeps only a scrubbed results.json with its costs
- C4. render_replay marks every fence run without losing words and pairs results within a turn, and every committed replay re-renders unchanged
- C5. release_text leaves out only rendered replays listed in replays.json
- C6. the learn-rules page's notes are true of their transcripts and meet the plain-prose rule

## The change under review

The work from `f7aebc80` to the working tree at `8743c102ec30` with uncommitted changes. Its diff is `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r2/diff.patch`.
- new: .claude/launch.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/review.log (not tracked yet, so not in the diff: read it whole)
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
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r2/diff.patch` | `7ed424e3859ab571b31e118ae0c25806449c5a33e368a7bf1bb9b93220e8f860` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/attempt-1/rechecked-checks.txt` | `64cd95f23b2536ba5f6cf3fbaa1f12358a9aa572788389cbad80e2328cf7fcad` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/installed.txt` | `13873666aa742a67ad2fc3ef7a2e40d775008bf318a48e6225b07d909321006d` |
| `.gnd-planning/milestones/induction-skill/evidence/IS2/rechecked-checks-attempt-2.txt` | `6432bb5d36bbc8eaeb93ad0b1932110d5cdd21f069f351388dd57e2713f87698` |
| `.gnd-planning/milestones/induction-skill/notes/phase-IS2-spec.md` | `f0fcfa73c7d279fc51e7e62e1df274dd6f0ecfdbf90de3bd5e2250b7995c2bf8` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/BRIEF.md` | `b4657aca4911d14aac897f2d1a290b2316190feafa409aa4440606a4b5eea994` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/FINDINGS.md` | `87679295200bc3d3f0f68604626a10b4c6164efadba92ee0b9700cf59d9d744e` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/brief.json` | `b3196777954e877df435914ffb82319f28065c4c229fac688155234fd00fc237` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/diff.patch` | `82ea2e33ca221a181917b37ed56c83b8f1928aa23aecf128bc8dbfc704824ca9` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/review.md` | `288d2cc3e46b754f8d6309d5205f22927ca1c5570aa213c7c3920eb5b926b94e` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/run.json` | `de01989cb0a61294a09c299f0068fbe924beb8fc0d7bd63a166eb46915ffe5c5` |
| `dev/components/modules/tools.md` | `3e6e0f61a06f96d123421b41d0783e17a8c8b3f07a4d7bbdfa955d033fe2d53c` |
| `docs/tutorials/learn-rules.md` | `ddf0569d791ad1a64a1e489bc98f2e0602db85561bff67beded3d46eac83553b` |
| `tests/test_ik6_walk.py` | `6fbea49c4e2093962e4b23835389d19f9c957d1cf3b537656283e0d2a2dfac2e` |
| `tests/test_learn_rules_page.py` | `3f1d6cee442cfe7b8d3d2071d260cfee88ad87b26ff6884911f7ad831235fab6` |
| `tests/test_record_induce_sessions.py` | `d8375630576533b9f5483ceeabb646687e93747a65510e862c769e7686894ad5` |
| `tests/test_release_text.py` | `b098ac93a30c87e498fb1dfb2c78db6766ef7757996566aff0b4d99c328b5480` |
| `tests/test_replays.py` | `1501200b0009d4771dfbb12a00d70e82e0919fd69b362d954be055ed66059da8` |
| `tools/record_induce_sessions.py` | `71d5383c65ad9c61be70e9c5181e64c30ef7941b56a4d9a35d97766a34ac937d` |
| `tools/record_skill_sessions.py` | `dc1ac3325cfa25051c26f4efc6e65b197d9827a47fb59de10f569f63de70786f` |
| `tools/release_text.py` | `3a0d4df5a1f366e909d232861c6c3dd7310801f2695338b60091004bf09ad503` |
| `tools/render_replay.py` | `2bad2cd856ad88e07da88d00f434d31f72de787868ffdd05d5462774509b6545` |
| `.claude/launch.json` | `d6a799d2bbf773253c5c3d1554a24118e3e04a327efffda181e02eca70733f9e` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log` | `dfc92cdafada97528e29dd04c0e8216a10d1cd6b7f6655a1da7302664b3a570d` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/review.log` | `10f7ec28706af4d71dfac5e72490f18bed2022195f1c27230300a5faafe9d8cc` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS2-r1/review.log` | `3d09c1932480870898a7bacacd0a50f8dee9d840f4ec2adfe4c9fa626d4e155e` |
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
