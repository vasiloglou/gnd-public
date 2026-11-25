# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This diff repairs the twelve findings of round 1 (review.md, FINDINGS.md). Does each repair fix what its finding reported, does any repaired sentence in gnd-induce/SKILL.md misstate what a GND command does, and can each new or changed test fail when the text or behaviour it guards is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Each round-1 finding marked fixed is fixed by this diff
- C2. No repaired skill sentence contradicts the command's --help or the reference page it names
- C3. Each new test fails on a legal edit that breaks what it guards

## The change under review

The work from `983a23b0` to the working tree at `9ded33688fdb`. Its diff is `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log (not tracked yet, so not in the diff: read it whole)
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
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r2/diff.patch` | `c1e54544faaa37ee91dbcff063da2c14adc9d844af4e0e58fe555962ad651dfa` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/gate-after-r1.txt` | `36eef13038f77e01241d49b34010aca37910a6cbbf7269cf5ab007965a50e888` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/regressions-red.txt` | `d99fadff07861395a27af8f74777f20da3cf0704d49c4e0b88a633c4ecb0b574` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/review-r1-mutations.py` | `f8c09a1dd72dc1dbcd0f9a4fc66e2b30e3de10c63e07923e6bb920b3633c397f` |
| `.gnd-planning/milestones/induction-skill/evidence/IS1/review-r1-repairs.txt` | `c7abbb0c7ac8fda9d97de7911692ada03c7886f70e37b60464fff57990eabf11` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/BRIEF.md` | `c34ff3c955d42a0102365ce7301569969d12fce564e1230bb2fe366e0973182f` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/FINDINGS.md` | `e7dd025a7791d96f734941c39452e4248a496c7bc324231a7bafd1b4e35e9643` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/brief.json` | `c93500cc073e14be0c16c38a956d87f97d979df6cca84f3df1736bfdcebca342` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/diff.patch` | `70d715de9d8367519d6b6159b4bbb384d996c8734bf6c7d038d8a46b76c8b854` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.md` | `ada4b7e24c8b6d37ada63e9fe47bd26221ed6f849422ed152c523268744989ec` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/run.json` | `daeb90d0fa1ce1ee0cade0ead5ae632258efabab66b8813697dc42d0ea362e03` |
| `src/gnd/skills/gnd-induce/SKILL.md` | `05b6de8076f5209579cf0e789ca22cdf02738ba926a81df381647966ff690dc0` |
| `tests/test_induce_skill.py` | `eddf7700780917e8055fe21bf40ec6fda6fb94dc44b36f2f0513daa9f6ae2b01` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/induction-skill/notes/reviews/phase-IS1-r1/review.log` | `dfc92cdafada97528e29dd04c0e8216a10d1cd6b7f6655a1da7302664b3a570d` |
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
| `.gnd-planning/milestones/induction-skill/notes/phase-IS1-spec.md` | `34c5ae689f98153452f31978a6403b5ae0034e1bdb0358bed6551d02030ee8b0` |

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
