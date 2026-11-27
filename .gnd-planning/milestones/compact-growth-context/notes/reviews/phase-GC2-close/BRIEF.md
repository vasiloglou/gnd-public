# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the example genuinely test role reversal against source, and can the retained installed-wheel replay reproduce the claimed measurements?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The amended example exercises source-backed role direction on the shipped fixture and makes no requirement on general host search.

## The change under review

The work from `e831b9dc` to the working tree at `54c8a28cd6bc`. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-close/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-close/diff.patch` | `20e9d4ae907c82f376d6224ae10dcd289840ac988f50db3bd9abd623a58df74c` |
| `.gnd-planning/milestones/compact-growth-context/evidence/verify_install.py` | `27c06dd92e8d0e559cc728b6fceb5587d72138c521982ff143a003f28ddabe65` |
| `src/gnd/examples/seeded_growth/README.md` | `f55055fe7d05adfc1ed36427d8beae06fc9bd8a8c7b018ad0cb6a51d1c6a68d4` |
| `tests/test_growth_view.py` | `6c918b733f02e99401c4a4b0a8a6dca503c07d09cb65bbc1ae8e3b5a303f0290` |

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
