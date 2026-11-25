# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what it sets out to do, and what does it break?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. gnd validate no longer refuses a fact type whose sample rows have a role named date or duration_days (issue 286).
- C2. The walk in src/gnd/terms.py does not read sample rows or an object type's description, and reads bind and head maps as containers keyed by role name, decided by the key that holds them; their values (a head's terms) are still read.
- C3. A date term in a derivation head under a role named source, provenance, bind or head is now refused, as under any other role name.
- C4. The 0.5.1 bump follows the tag-only procedure in docs/releasing.md, and the install pins keep naming 0.5.0.
- C5. The only behaviour change beyond the issue is that a date or duration_days object in a sample value or in a description extra no longer refuses a model, and the release notes say so.

## The change under review

Pull request #289, https://github.com/vasiloglou/gnd-public/pull/289, at head `380928c0f1dd424cf976e959113ace53d1ced0c7` (base `102110b273003f5fced025f6b600d2254336ac17`). Its diff is `.gnd-planning/reviews/pr-289-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/pr-289-r1/diff.patch` | `d6587789aea49284f039639bbfc49dfda555ba0a527f5962a61038d3ab625e5d` |
| `docs/releasing.md` | `59aed07138dfa74427148e3958c0741cc04a81cec8a57406bdca578282ebc30b` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `594ec58970647df4abeca920579f2088b671fdd65f0ee473354c1ebd204ca92a` |

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
