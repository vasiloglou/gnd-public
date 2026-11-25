# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This diff repairs finding F1 of round 1 and changes two tests that read the release notes. Is the repaired sentence in the PyRel block of docs/release-notes.md true of the code at this commit and of 0.4.0, and do the two changed tests still check what they checked before?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The repaired sentence states every export-time refusal that docs/runtimes/pyrel.md lists for inexact numbers, and claims a 0.4.0 difference only where evidence/RW1/old-version-probes.md shows one.
- C2. tests/test_ossie_docs.py reads the same four moved bullets as before, and would fail if the Ossie block lost an exit constant or the byte bound.

## The change under review

The work from `cc8cdb65` to the working tree at `d639461b7841`. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r2/diff.patch` | `12bb3f669aae8a26d84b55bad5447eebb949e1ec9e90e2c3510084998635ba81` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW1/old-version-probes.md` | `373d25a415c374d22a687fdda155623c1b34180723a6796d14840f4ab08049a0` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/BRIEF.md` | `6652f3063bee2dbb77c4221af79e83e56b5947624bed5e5e091b87204b1f17f3` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/FINDINGS.md` | `28576fa81da233c17bd90c21842c64fdc35b7a4c912263294779f3cf9b9eef4e` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/brief.json` | `eb0505593d698ff2c774ff4de4746581624d7715444e963ad3ab5403e8181f4b` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/diff.patch` | `4f92142f2b6c3ab9650d88194dde857ba991f08541cee5220606832d7aa4aab5` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/review.md` | `1fb549ac6c59c059b70b2175cc8015eaaf55172fe5743b3f9266f7d8ce44fb39` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW1-r1/run.json` | `69ae4b0787c665e7f4b66e133c7c1ec997e4b728e595df2ea779d4eef348c59d` |
| `docs/release-notes.md` | `19d658d38e3580f1e816f779d83a311243f3ac69dceefcd0b3fd6bdbb9053e80` |
| `tests/test_ossie_docs.py` | `6635a3d9069a2025df7650593adf69488323e950cc7c02e66bd3e121e065657d` |
| `docs/runtimes/pyrel.md` | `c622ee96a74897cec5330b42920b9ee094795584f454c9dc0c5247bdaafe27a8` |

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
