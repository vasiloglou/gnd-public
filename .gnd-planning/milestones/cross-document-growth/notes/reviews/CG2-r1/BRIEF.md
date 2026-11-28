# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can discovery misreport signals, lose source evidence, expose sample values, or exceed its declared budgets on a legal model? Exercise an input that differs from the fixtures, including each new regex and slice.

## The change under review

The work from `88227f35` to the working tree at `88227f355477` with uncommitted changes. Its diff is `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG2-r1/diff.patch`.
- new: .gnd-planning/milestones/cross-document-growth/004-CG2-spec-gate.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/cross-document-growth/evidence/CG2/dynamic-query-successor.json (not tracked yet, so not in the diff: read it whole)
- new: src/gnd/evolve/candidates.py (not tracked yet, so not in the diff: read it whole)
- new: tests/test_consolidation_candidates.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG2-r1/diff.patch` | `e3e32fee6c8ae0551e5070a09a710658ce688957fe1d90309e0242e791b55f04` |
| `.gnd-planning/milestones/cross-document-growth/notes/phase-CG2-spec.md` | `0f33fee81a00bb8c7e0e4e45e859b66a6bae5f520c08c8da4ac46fdd5c978f35` |
| `dev/components/COMPONENTS.md` | `d5c7cf0fbfa62ae928e09e3ada8bf8478e20dbee15b87c42f1c3b9f09395fc6f` |
| `dev/components/graph.md` | `47e7ab6c33621cc36032c8ab068628029b25ffa2eb1ff3cd61eb8726b382d26d` |
| `dev/components/modules/commands.md` | `3aedb9cf8bdfe0639fb5171834f1111e2d898963ba02f96ccbf499c94478c7b4` |
| `dev/components/modules/evolve.md` | `d28891b744ecbb0568a461f58f732a2a0536fa6c5fa7a5a173421f7230584a55` |
| `docs/reference/disclosure.md` | `94d45c21fa7fcb3121959c40943dab3b0b7e118ed4ba84ab3544950cadf84424` |
| `src/gnd/cli.py` | `5fb60f4dcdf26fbfc6cd4864096830b044c4c5ba594427bb748d97ad38b36dd9` |
| `src/gnd/commands/discover.py` | `34464b846b0b3c0fd5735e5e7086151dcf8b658c69ca6c9635cd07cc92bfa6c3` |
| `src/gnd/disclosure.py` | `089c5720bff24278782e358fd3f5144a42a10404eab103b598b4adc6ec60bbd3` |
| `tests/support/pyrel_application_successors.py` | `3f26a40f061edf7181a141ebad2b1473b8c0fd5b40f3159fc6c4dd3904dc3f7d` |
| `tests/test_disclosure_mode.py` | `3314e59d453cd3e411cebf026c32ce4845cb34a7cad5ea9ab2183bdfe6936532` |
| `tests/test_rf1_cli_pins.py` | `47a784e667e2d3d5960b31dcb503fb1d8f2a036db2c6675a5869cd1e7e6557ee` |
| `tools/gnd_layers.json` | `0d5cb98b72efe7e4fea5ba7b7d284e6704aaf5855b8556625c6deaae1df17145` |
| `.gnd-planning/milestones/cross-document-growth/004-CG2-spec-gate.md` | `5805d86ccb3990d5d9f8e15ded79ea8ce29bf71f7b5970b907b6970a987e20e3` |
| `.gnd-planning/milestones/cross-document-growth/evidence/CG2/dynamic-query-successor.json` | `5cdbb8729070f501aa9233447ff832baaa96115ad8acff3d9e1df2b2cb74f65e` |
| `src/gnd/evolve/candidates.py` | `efacc5b2e55573d4f929553cfb64ebf047b485aa0abaf21f7c4b0345f9f71fd0` |
| `tests/test_consolidation_candidates.py` | `2946d6e33bdaf301385e3e9d1c1b8a4852233ac693d1b026471d895d25353741` |

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
