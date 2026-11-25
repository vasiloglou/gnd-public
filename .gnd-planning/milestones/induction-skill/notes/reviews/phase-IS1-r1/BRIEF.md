# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff implement the IS1 spec r4 as written, and can each new test fail when the behaviour or text it guards is wrong? Report any sentence in the new skill that misstates what a GND command does, any route or pin that a legal edit could break without a test failing, and any place the skill could lead an agent to apply, edit or fabricate a proposal, a learner's claim or a label manifest.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. IS1-C2: every inventory pin moves by the edit the spec names, and the pin edits are red on the pre-IS1 tree
- C2. IS1-C3: ROUTING_MATRIX gains the spec's rows, each regex tied to a sentence that does not exist at the base; RECORD_ROUTES and the denials gain the new skill
- C3. IS1-C4: each one-home refusal sentence R-a to R-h appears exactly once in the packaged tree
- C4. IS1-C5: every fenced gnd line in the new skill passes the invocation guard and the help-option test
- C5. IS1-C9: no FROZEN_SKILLS directory differs from the IS1 base commit, with a seeded negative control
- C6. D21: the skill never answers as its own llm learner

## The change under review

The work from `1e6083f3554e785aa994422c837fda874d74d1e6` to the working tree at `9090e84af803`. Its diff is `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
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
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/diff.patch` | `70d715de9d8367519d6b6159b4bbb384d996c8734bf6c7d038d8a46b76c8b854` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/c0-owner-reaction.txt` | `32b3b9f53a2920fd42f9d3a6516ed4035ed7b37e230e57c7a60056ae77ce1e24` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/gate.txt` | `0fe20fd3b44759e325ff0ee6fc2c6936ab83cddac2cbe862e2849425c06a3592` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/regressions-red.txt` | `fe41a32ce11ac2d2f1e6bebb86a8749b785c9f79eb13cd0cb0d5f93581b220f7` |
| `.gnd-planning/milestones/induction-skill/notes/phase-IS1-spec.md` | `34c5ae689f98153452f31978a6403b5ae0034e1bdb0358bed6551d02030ee8b0` |
| `AGENTS.md` | `f632f6965032305b56dc466a646f77e314c7127949d6fa375c7acd1261cd9829` |
| `docs/agents/index.md` | `a0449ad97c86cf7cacd1c4f412639ae68a2b3b8894c040af06e4d594fe150d29` |
| `src/gnd/skills/gnd-dev-session/SKILL.md` | `5668337384a0b8cb2c30e913902a612d261a54fb4b3a4e323d2bc65a0ad6c54b` |
| `src/gnd/skills/gnd-export/SKILL.md` | `ac7521df273e3e9ecc1c736457b5a0740f53f0568c94ede2882e040518d52b80` |
| `src/gnd/skills/gnd-induce/SKILL.md` | `7757f475e1a536c3df4c541a15468df049d6b9ef41e0277567f27ff63ad756c0` |
| `src/gnd/skills/gnd-model-evolve/SKILL.md` | `9b0e26f5052ebcd72715bf0ad0ab857054e7fca278ba5d573df31f912c34989c` |
| `src/gnd/skills/gnd-orm-core/SKILL.md` | `449987233c2d2116fbbac4896f7b324990b4609f24e1a5fba9d0acaed30f9399` |
| `src/gnd/skills/gnd-orm-core/references/labels.schema.json` | `f3b90f9f1654a3246858c2c28e3ac60f08ed0485182594a7aaef9c7d8deeecf8` |
| `src/gnd/skills/gnd-solve/SKILL.md` | `297869cdfc88500f0ec3ebde3534690e93c7e22f2558626c06a0c3b6af1a3005` |
| `tests/test_doctor_uninstall.py` | `269d244253773f939ad45bd242fca34610f0d95af52670c99b0a6c6ee9b81079` |
| `tests/test_induce_skill.py` | `30bad337cdb1a250461d5985fa161d50bb7595bea03a9a0366f9b223ae7b807b` |
| `tests/test_packaged_skills.py` | `87bdb5730e5be8a158c050b097fe653b756fc8a1983ac631ad47ca9a33f84195` |
| `tests/test_public_distribution.py` | `48062d6a74614053979550bd1a4ca0dba0d90eeeb733166f9a7f1f882ae33502` |
| `tests/test_public_packaged_invocation_guards.py` | `ae2b4b3494903f18ba8ef7be38fb5296eb6d18019fdf292f457f5e8a16b8431a` |
| `tests/test_schema_sync.py` | `494d98531274929cb622b2e38ab57de316851b7e1c6dd0f44e9297bd778c453d` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
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
