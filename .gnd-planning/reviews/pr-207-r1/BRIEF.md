# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change do what it sets out to do, and what does it break?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. This PR fixes every failure of the default test lane on main at 3fe7b136.
- C2. Each repair uses the repository's own mechanism. No pin is loosened and no check is removed.
- C3. The unpinned GW/GC guarded validation code moves verbatim to gnd.model._guarded, and parse_model_document and MAX_MODEL_BYTES move to gnd.model._parsing; _validation re-exports every name.
- C4. gnd.synth.frontier and gnd.assurance.core._phase3_target keep the GC2 filtered and GC3 any_of guarded refusals out of the frozen band-4 frontier and the frozen Phase 3 assurance denominator, and every drifted golden reproduces unchanged.

## The change under review

Pull request #207, https://github.com/vasiloglou/gnd-public/pull/207, at head `7df6c0c52adc468415819c12293597ee5c16b3ec` (base `68a311725bfb9bea395a33ab0e3c8d6e79eb17d6`). Its diff is `.gnd-planning/reviews/pr-207-r1/diff.patch`.
Your checkout is not at that head. Read a file as the PR has it with `git show 7df6c0c52adc468415819c12293597ee5c16b3ec:<path>`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/pr-207-r1/diff.patch` | `16f4638214307f1c3415ad1bc187aba15028e7ee5ac47c9988ec8207d26385ea` |

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
