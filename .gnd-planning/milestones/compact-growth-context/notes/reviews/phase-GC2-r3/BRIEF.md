# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the small include-provenance repair at 0b0fa734 close the reproduced positional-row defect while preserving valid loader paths?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A changed composed vocabulary cannot reuse the original positional attribution in the growth API.

## The change under review

The work from `51f0d1f2` to the working tree at `dafd95f3029b`. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/diff.patch` | `ca513736aa56cb068cf31d44f26777825634ec9517541d0ed94ca44164438c42` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/BRIEF.md` | `6cc6a1135bab307307853489a5d62b483cd5482756f357af23d7c82d7025e9b9` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/FINDINGS.md` | `09c74e98ccd2621b6b509ab48a2cdccb05d870e34cf3bf28ff9bc46801ed750d` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/brief.json` | `3123b540fd06642b0673674784ebee1288f364ee727030c7d472834278259dc9` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/diff.patch` | `f9e6a4dd233dc7cc526d60b25e0c03e790e5b700180ac04d56fb1bf12084181a` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/review.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/review.md` | `a8465017bbae00a6882f5863a94671f80ae5c23d4857b75e356d93eb9c8e54f9` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r2/run.json` | `2fdaea8b10751d2e080db7e75f6af3e8c139123e164df5a396202370a9e14cc9` |
| `dev/components/modules/_root.md` | `bf3de895b750babb1ccf5fc912212bac5d011658fc34d2b94518da7c5fda5c2d` |
| `dev/components/modules/model.md` | `b2f83e28ff0d7499b5a15fa3c68272efa1b8fd1abada47ddbe21c9677665f7a9` |
| `docs/reference/python-api.md` | `15a16ccf6926079382e2c4d229d78c4427edb1a28ea8d5bc14d6f589d007e48c` |
| `src/gnd/api.py` | `175d5d4ecce3e670a34737a625afca4e153cd9170a4df1336f6d44849242ab51` |
| `src/gnd/documents.py` | `5c2a674b19dcf9aad323b0819c3ceae7b8a1367e6649aa72f1492de7735ad6cd` |
| `src/gnd/model/__init__.py` | `a1882dd01908c5cb5e6395f822468d027eac2540ac43d575f99a5e42daa3c5ed` |
| `tests/test_growth_view.py` | `793ae468aeb4b1d97cce33aed3791b42a10b7213687e9226479798d2d4fae885` |

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
