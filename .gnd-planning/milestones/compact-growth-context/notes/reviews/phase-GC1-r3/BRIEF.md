# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the repaired object and fact metadata projections meet GC1, and are any previously reported correctness defects still present?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Derived and independent objects retain their structural distinctions without disclosing rule bodies.

## The change under review

The work from `c00ac195` to the working tree at `9810d182698b`. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r3/diff.patch` | `f633f28a7ab0b7b1f7ae2c4fb8591cdae577b5405a3b4faaddb6e46ad78cf058` |
| `.gnd-planning/milestones/compact-growth-context/evidence/dynamic-query-successor.json` | `4667d94c3325f8958ede574f8fd2e2968caf9412aa59d474aa1829e913849d0b` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/BRIEF.md` | `6708eea30ea960022bf5655f75b12db58f7116440fafe949dd31213c1e95750c` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/FINDINGS.md` | `f370ebb155cb02eb40fbd69b6a73fb6508f612ca4972c3c247e67c77b5f4083f` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/brief.json` | `9405c4dac565e0547a70ba24b161e44252ad3124144086e1c62b9d1c7125313d` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/diff.patch` | `953418ef1ae92e4439eb1306a4ce7248dd1e78c00d17c81963b622ec960632e3` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/review.log` | `2122456c9827a04aff9792c1149505097ac016d61c330a0df0dd73976358987c` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/review.md` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/run.json` | `85cb1617a8e76d3db2e20e14d1f7d6934669065e58db724215e8f5e2d1acbcdf` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/BRIEF.md` | `cf124119bcb4b1de1cb50a80d939f5d0cb8d4a68abf5c1bb1d8df1d1832fcee6` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/FINDINGS.md` | `77052e5d08524e1477d37db592179a3cac042e93aa6c25a1ac3f75cf025db5e1` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/brief.json` | `9b925b8f4f55ca65dbc230f79100567562144c9965c693cf89833d4d48932c2f` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/diff.patch` | `953418ef1ae92e4439eb1306a4ce7248dd1e78c00d17c81963b622ec960632e3` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/review.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/review.md` | `8c0f1dbfab26c03a3355902e89a5989365d4afe3a036fd580b1a56d690902c2f` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r2/run.json` | `bb923adb3bcb5754108086af13f87eadf9cbdcc7f49fa4f5e1c2b95da60b5999` |
| `src/gnd/model_verbalization.py` | `606a0b207e17af6d464978b19eb1ad8d6bb51f4cab7a9b7c09393d1d5df5200a` |
| `tests/support/pyrel_application_successors.py` | `6d963332672b96692fa138fa6e413529c1453e038bfe2aec1195ccac5b37d960` |
| `tests/test_growth_projection.py` | `2475018268d20ee03312f4564d6730021c93411627027fdd097f36703355213e` |
| `.gnd-planning/milestones/compact-growth-context/notes/phase-GC1-spec.md` | `438be1e40fb319d069c4a6b57737fb1f94a071e645ce8ec185a9c99c11e08edd` |

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
