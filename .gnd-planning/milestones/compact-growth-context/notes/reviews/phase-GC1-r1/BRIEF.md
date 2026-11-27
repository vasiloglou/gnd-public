# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Which validated model inputs break the specified projection, encoding, disclosure or composed identity contract?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Schema context includes stable composed IDs, ordered roles and compact family signatures with semantic metadata.

## The change under review

The work from `c00ac195` to the working tree at `c00ac1953953` with uncommitted changes. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/diff.patch`.
- new: .gnd-planning/milestones/compact-growth-context/evidence/dynamic-query-successor.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_growth_projection.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC1-r1/diff.patch` | `953418ef1ae92e4439eb1306a4ce7248dd1e78c00d17c81963b622ec960632e3` |
| `src/gnd/model_verbalization.py` | `6c65a30bcf43c947bc9b33634d6fd4059d14452772fc7179a829d14cb5e25c41` |
| `tests/support/pyrel_application_successors.py` | `6d963332672b96692fa138fa6e413529c1453e038bfe2aec1195ccac5b37d960` |
| `.gnd-planning/milestones/compact-growth-context/evidence/dynamic-query-successor.json` | `4667d94c3325f8958ede574f8fd2e2968caf9412aa59d474aa1829e913849d0b` |
| `tests/test_growth_projection.py` | `6373e722cd81a736bdc74067e035ce43372f06ecb1430cf4fe6fabbbbc7f7252` |
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
