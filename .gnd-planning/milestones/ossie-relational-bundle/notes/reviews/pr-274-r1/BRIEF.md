# Review brief: a pull request

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this pull request do what it sets out to do, and what does it break? Judge the two code changes, the release-note sentence and the close records against the code and the normative text at the PR's head.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. binding:name-collision compares Ossie's normalized form: two tables that are not regular identifiers and differ only in case, such as fin.cust and FIN.CUST, are accepted as two tables, and two regular names that differ only in case, such as cust and Cust, are still refused.
- C2. _quoted and the collision check share one helper, normalized_identifier, so a pair of names the exporter writes as one identifier is always refused and a pair it writes as two is never refused.
- C3. The size bound covers the two new relational files, so a large model whose three files fitted can now stop with ossie:output-size; the release note says so and names the remedies.
- C4. Plan r3 appends eighteen close amendments in section 11, each naming the record that raised it, and the approved r2 text is kept.
- C5. The close results give, for each completion predicate, evidence that would fail if it were false, and every open question is closed, carried with an owner, or an accepted residual.
- C6. The close record states that the owner has not ruled the close, that external acceptance is missing, that the repairs made after the panel are unreviewed, and that the oracle lane's consumer test was not run.
- C7. No public text in the change names a downstream project, customer or reporter.

## The change under review

Pull request #274, https://github.com/vasiloglou/gnd-public/pull/274, at head `7e968377628c08fcba17b2d87cdaed96243f41f7` (base `f5462783a6f82c444330133491f4075c2696a628`). Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/pr-274-r1/diff.patch`.
Your checkout is at that head, so the files in it are the PR's.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/pr-274-r1/diff.patch` | `8c594f7d0a905770ff9346bbdb945463bfe2b1ba4836c60c52ad10196c01186c` |

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
