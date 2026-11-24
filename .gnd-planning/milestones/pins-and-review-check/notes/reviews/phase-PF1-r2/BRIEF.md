# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 2. Round 1 (notes/reviews/phase-PF1-r1/review.md) found F1-F3 in tests/test_inventory_pin_home.py; commit 'Catch every binding of an inventory name, by the grammar' rewrote the guard around the grammar's binding sites. Refute: (1) inventory_bindings reports every binding of EXPECTED_SKILL_FILE_COUNT, EXPECTED_SKILL_NAMES or EXPECTED_SKILL_FILES in any scope and by any binding form Python 3.11-3.13 has, except an import of that name from test_packaged_skills; (2) it reports nothing that binds no such name; (3) F1-F3 are fixed without a regression. F4 (inline 18 in tests/test_development_scaffold.py and tests/test_marketplace_plugins.py) is deferred to the owner and need not be re-reported.

## The change under review

The work from `04945d39` to the working tree at `02c6bef1db68`. Its diff is `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r2/diff.patch` | `4d67ea3eabb41a330ed2053ae9d7a7a9dbeb492fce94ffcbc9dba23eea954fcd` |
| `.claude/skills/process-phase/references/project.md` | `108f227dbd18635b725576b050e118e9adaa6ffa3c6e5393f85aadc4a5e6b749` |
| `.codex/skills/process-phase/references/project.md` | `108f227dbd18635b725576b050e118e9adaa6ffa3c6e5393f85aadc4a5e6b749` |
| `.gnd-planning/milestones/pins-and-review-check/notes/phase-PF1-spec.md` | `56e53126d6962b48f588c7198aad72da3184ec7cead51334e24950cf48d96703` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/BRIEF.md` | `01cc467ae7dc3f0959f5b68c0abeb4c7851f7542fb2b70f88e58c9d48a66d14c` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/FINDINGS.md` | `0b466dafff3ddeeda0c64fedcb83871c3254fa10dcbdd2a194189ea8801d189d` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/brief.json` | `442b7a9b0b21ae6c68bd18fa49dd8097b0b7d0ec06892b0eb18879a1a9126ac4` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/diff.patch` | `81ccf20cfac978a52439224c4c5e144385544f9d32f456c48bc088fffd646f1a` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/review.log` | `5154d7e54f66ee5357027d5311d6cccf7ecbecc3d35e0b567d20d774a9a71c81` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/review.md` | `5ac61f542b957eef869a9c62c982c22faec062a82c15edcf8663ededc89dd1d7` |
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/run.json` | `183eff4f7766942b1d407dfc63c000c67c1ab13564fa8fdc12ae93e6aeb2168e` |
| `tests/test_doctor_uninstall.py` | `95964bc20e62394655ad629badbea316d4ca163fef5d82a8bd220e706d493f99` |
| `tests/test_install.py` | `9fbbb5d182efb1f216cf340b0dac6ab4aeb2bc0affbc9e921758403aaf8a02f8` |
| `tests/test_inventory_pin_home.py` | `ab405a9bca1c8d884d5b2cb913f70ce9c223bd3244ca01450b5360d8bfeb9c59` |
| `tests/test_public_built_inventory.py` | `ac6cba98edf0aa5766a6251ea081683b66f04076c19107b6192b70f25c8f8cd7` |
| `tests/test_verification_fixes.py` | `0f88507ab2a9d84dd37add178320f14587ba2758153dec5e8962706f9b5e2bcf` |

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
