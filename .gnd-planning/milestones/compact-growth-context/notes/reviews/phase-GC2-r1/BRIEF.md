# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Which supported inputs, default paths or reasonable interpretations of the host instructions violate the public growth-view contract?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The agent can change search route, verify direction, widen or defer, and both public surfaces agree.

## The change under review

The work from `342f953d` to the working tree at `342f953d5780` with uncommitted changes. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/diff.patch`.
- new: tests/test_growth_view.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r1/diff.patch` | `a348488b1a6334f253d403cca1e02c2fbd190afacf18033f9e919c2915856f4b` |
| `dev/components/COMPONENTS.md` | `51ac46406a90d46c3edefb93a7063aaead6bbd076cafc05c2d8ba2adcea749a3` |
| `dev/components/modules/_root.md` | `34360c58f418e6fbaeb73347560761ade853dd477f48443f9c15799bf8b7fb38` |
| `dev/components/modules/commands.md` | `33796358cc25effc3dd37e0d36f64e90c9d1ca88228885cb2ea2d2f9152d4b26` |
| `docs/reference/cli.md` | `bb80ffcb802063ebe2df4a92d88ea2f74636b263a9e90c9d195ce7d3cd038508` |
| `docs/reference/disclosure.md` | `d90e3f25760bd2aad97a3e527671622830a1270b503dc52ce8fbad79cb973c72` |
| `docs/reference/python-api.md` | `08d8455e7a38930727249ef3a6ed03c5e55617399634291054c47a9ab299738c` |
| `src/gnd/api.py` | `7c0390cddc2ec4694c6fc5f77a54fef4146a5012316e3579963252845460dbf8` |
| `src/gnd/commands/checking.py` | `7ee7a152a3753cc0c73fddabfd191c66ceede0c245e20dbb6b297d0d193208c5` |
| `src/gnd/examples/seeded_growth/README.md` | `0ebdf47d4623de20b82fb0a1d9112cd9dc8b858ac0f34646a880d406b4d4d8f7` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `21136cab354fa38e18f187e17c24b25ac7b5d6093734ed3b6bb0c3c0a29526fe` |
| `tests/test_public_api.py` | `e04049af8e4250523eed5665a65b5508999b46ca002ea225cb4b1347fb8ac621` |
| `tests/test_rf1_cli_pins.py` | `f77643f55605b749a6d77a4b50c2605cecdc739694bca80634bc07edde89c6e2` |
| `tests/test_v61_phase2_api.py` | `3235dd3dd668f8a9438b5017b9e5302a5c61fc2f0b061cd267f856fd1abacc27` |
| `tests/test_growth_view.py` | `be83b5608f3b0ad427554de85193c1848a146f492dd4c5745794f403380ca875` |
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
