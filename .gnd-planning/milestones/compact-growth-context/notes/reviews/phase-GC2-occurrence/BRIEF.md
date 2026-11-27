# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can an out-of-occurrence citation still pass, or does the receipt still claim automatic direction inference? Check the F1, F2 and F3 reproductions from the preceding review.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The worked fixture rejects the second occurrence, uses the project span convention, and attributes semantic judgment to the agent.

## The change under review

The work from `0a0ad941` to the working tree at `066d2f3dc130` with uncommitted changes. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-occurrence/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-occurrence/diff.patch` | `61a36491a79607dda38afa176ff791900688cfcf21b127c90b25a85066e0e42a` |
| `.gnd-planning/milestones/compact-growth-context/notes/close-replay.md` | `da5117cf6d187492d26a7aef4bcdeef995e374865563df4753864d6886e07830` |
| `src/gnd/examples/seeded_growth/README.md` | `70e550e5e9edc260fc5d14af38c5537a5cba71cd2fdcb02837f7d7f72e151faf` |
| `tests/test_growth_view.py` | `86282308f2cd2280c4b3690e5a1a8371b750753a9ec54a43c694b510f1df2b85` |

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
