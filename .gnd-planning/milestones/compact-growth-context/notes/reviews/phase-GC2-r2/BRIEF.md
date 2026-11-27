# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the validation and example repairs address F1 and F2 for supported model inputs, with existing default behavior intact?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Invalid in-memory mutations are refused and the packaged example records direct reuse, retry and ambiguous deferral.

## The change under review

The work from `342f953d` to the working tree at `51f0d1f20077`. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/diff.patch` | `f9e6a4dd233dc7cc526d60b25e0c03e790e5b700180ac04d56fb1bf12084181a` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/FINDINGS.md` | `29bdb6a7bb9be58653dd34bc8e93a4d54f654bd1106ad4533d6d1f742fb12498` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r3/FINDINGS.md` | `e45182db29ec89daf7e74d2be447a671bcd4d987bc72cd4d6e281d5107d9fb62` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/BRIEF.md` | `9aa0722f0e59e0c7322f3679f0654f39fd93da819a008a717f9f32722208ba67` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/FINDINGS.md` | `7f19a85c2fa956181c0e3334417b2bbd96433a616ea145d8009d0a1de1ac0cb5` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/brief.json` | `02a5d899dc4e8c70e758deb44734ec5349040a69a8fad6d98b51902247d63027` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/diff.patch` | `a348488b1a6334f253d403cca1e02c2fbd190afacf18033f9e919c2915856f4b` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/review.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/review.md` | `26a835bb153861e99f6077bbb7e5b1f8e415ef974790363bc7d90fe65e5c1d06` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/run.json` | `1c43465c0ad2ac2571e273dfb2c737acda0925a0555cec7745192e7d8aee9dd6` |
| `dev/components/COMPONENTS.md` | `51ac46406a90d46c3edefb93a7063aaead6bbd076cafc05c2d8ba2adcea749a3` |
| `dev/components/modules/_root.md` | `00a7a78aca2c13c86411c231bf53efde48b21370538052b53f64b0252319b2cb` |
| `dev/components/modules/commands.md` | `33796358cc25effc3dd37e0d36f64e90c9d1ca88228885cb2ea2d2f9152d4b26` |
| `docs/reference/cli.md` | `bb80ffcb802063ebe2df4a92d88ea2f74636b263a9e90c9d195ce7d3cd038508` |
| `docs/reference/disclosure.md` | `d90e3f25760bd2aad97a3e527671622830a1270b503dc52ce8fbad79cb973c72` |
| `docs/reference/python-api.md` | `2417c8f9268b7a2338caa80fa03e02e0774cf14ea915cb23e7eaf5f4ee2928ac` |
| `src/gnd/api.py` | `e1ca20936b24ddb0e9fc524ea5a1e3ddb6833362fd2cf3a70f74a1c47884e670` |
| `src/gnd/commands/checking.py` | `7ee7a152a3753cc0c73fddabfd191c66ceede0c245e20dbb6b297d0d193208c5` |
| `src/gnd/examples/seeded_growth/README.md` | `f28c46184e7e1b8aab375366e544b68207950ae63ea66ff4722a0811a67df7ec` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `21136cab354fa38e18f187e17c24b25ac7b5d6093734ed3b6bb0c3c0a29526fe` |
| `tests/test_growth_view.py` | `ad647c943b93b3e3b821a116b8777777c739361916b4eec4882da258e69a0062` |
| `tests/test_public_api.py` | `e04049af8e4250523eed5665a65b5508999b46ca002ea225cb4b1347fb8ac621` |
| `tests/test_rf1_cli_pins.py` | `f77643f55605b749a6d77a4b50c2605cecdc739694bca80634bc07edde89c6e2` |
| `tests/test_v61_phase2_api.py` | `3235dd3dd668f8a9438b5017b9e5302a5c61fc2f0b061cd267f856fd1abacc27` |
| `.gnd-planning/milestones/compact-growth-context/notes/phase-GC2-spec.md` | `07bd76ef16e2ad8dcc3295459d7561d268e1fc8dda8d677d679e102afaeabe69` |

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
