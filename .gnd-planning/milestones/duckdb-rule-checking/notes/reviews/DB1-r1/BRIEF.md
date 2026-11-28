# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the DuckDB-only lowering preserve joint correlation, native coverage, typed bindings and existing export behavior across supported snapshots? Inspect matcher assumptions and quantify any semantic limits.

## The change under review

The work from `a81c9af0` to the working tree at `94fd93779c47`. Its diff is `.gnd-planning/milestones/duckdb-rule-checking/notes/reviews/DB1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/duckdb-rule-checking/notes/reviews/DB1-r1/diff.patch` | `ff32f57850e79fffb703ca510953a18abb7c4fb1c2154b5648328ba309fe63f7` |
| `.gnd-planning/milestones/duckdb-rule-checking/evidence/DB1/query-successor.json` | `59950cfdafba3530736899cfb98156cb0a8f6c7f9dc0811f85a211a3aa53f9ff` |
| `docs/reference/capabilities.md` | `89fd15882e584b9ddf2e4ba03cf47ae8b646a40b9ee4844bafb8aec1350f94ad` |
| `src/gnd/export/pyrel_rules.py` | `d939b2f4a120bc798b30344b3b4d4d75ec87e60226558d368a6b4cdd8d35f771` |
| `tests/fixtures/duckdb-guarded-existence/model.orm.json` | `b2b923a4fc11cdc64418134ac9cb8ceea39b9bbab7acb430a49ccc790fd51982` |
| `tests/support/pyrel_application_successors.py` | `eadbf9a9e5fd1f9b79f5398a40d23fe8f830da51ae5ede65c493560dbf7b3dd4` |
| `tests/test_duckdb_rule_checking_phase1.py` | `196694e8d01d2048a0faf418f2bdfbfb01219e386033a8c091dfe2bcf9d23277` |
| `.gnd-planning/milestones/duckdb-rule-checking/notes/phase-DB1-spec.md` | `c12ad917800ee7cf4f9c25fde6372821b868162535c77e0d7fe98caf4dcda857` |

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
