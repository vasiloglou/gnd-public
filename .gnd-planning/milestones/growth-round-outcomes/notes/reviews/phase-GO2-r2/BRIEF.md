# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

This round reads the repair of GO2 diff review r1 (FINDINGS.md lists its eight findings). Does every operation of a proposal now get a correct outcome from gnd evolve preview --operation-outcomes, with no refusal, exit, preview byte or digest changed by the option? Find the proposal or input where an outcome is wrong, a repaired finding still reproduces, or the repair moved a refusal.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. R1 repair: for every finding F1-F8 of round 1, its regression test in tests/test_go2_operation_outcomes.py (test_r1_*) fails on f7ec03b4 and passes here, and the input class each names is handled, not only its example.
- C2. GO2-C2: a refusal is tied only to the one operation that changed the element (or the role) the issue names; when two operations changed it and nothing tells them apart, the row is unassessed, never a guess; dropped-with names exactly the operations that need an element a refused or dropped operation adds, wherever it stands in the proposal.
- C3. _needs is total over arbitrary JSON after values (mappings, tuples, lists, scalars) and reads every key the ORM meta-schema uses to name an element; it never raises.
- C4. GO2-C1/C7: with or without the option, every refusal and exit is byte-identical, an include-analysis refusal included; with --outcome-report the report is written for an include-analysis refusal and its path cannot be an include input.
- C5. The locator is linear in operations and issues, for numeric and [id=...] paths.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `038f64dc` to the working tree at `9bf8bf3ebf14`. Its diff is `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r2/diff.patch` | `1b59ab939b9e697b6adf346dd3d6290af33119d5fea4fd7a8b4ed04003f56eb9` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/dynamic-query-successor.json` | `22be8a72405e832944814221d07b3211400a8c1276625030256a0bef5a5b4fb3` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/query-successor.json` | `5236471cdcca24983d0daf18d9aee5cf487606dcd738b70f0b57429b98aba1bf` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/source-successors.json` | `e44f317a5b436def140efb4769d2bff4dd6f19183fee892c50dc9e616eaae194` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/BRIEF.md` | `4e5c21490b8fe3a174dfa0febad96bbdfc4461f9be48e48b966b5c3de3b8348c` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/FINDINGS.md` | `81ffa2c3e7238eb119efa154624e37e0f575febd9f674189245fa27c8defd363` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/brief.json` | `140ee0ee8c26cadf0bc789c34b06d40522f5e71b80ffbaead17ecfcd51d70f09` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/diff.patch` | `0503db6790bbfedefa3804b2efb72e8f18147a4e8362891b2ec4376284444fe8` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/review.log` | `dc5a44f7ef617ba85d3099b36c056c71d8f30d925c6a7817289ba716ec647324` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/review.md` | `750b243f7ddfe20400a5ab317554e46aef54727dfb4048e058e9c69a33ddd9e9` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/run.json` | `82741e5df2cc34eedfd2d704cd3305f75b5cc0c657dfdbb26b2b40274f9c2fba` |
| `src/gnd/evolve/cli_service.py` | `0a12ad36b80f9089f79e604aee25f01e203b30e799a55492179850cc93c9bc6d` |
| `src/gnd/evolve/outcomes.py` | `af4a2d82ca40b9b1a732d080e7b5a6b423c96984a242151dc9190251503c9d33` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `af9514bdf0a66f3afd8db4ba11b6ecb736c94fe137b500a3f065c2cf7e1f7110` |
| `tests/test_go2_operation_outcomes.py` | `3dfd07a61b155ecf258168360cd3ded4fcdac6f653bb9174fa52b346d02d16af` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO2-spec.md` | `625435615abfd1bc7aea8b7006c569608866d979362d2e973f01000d103c02db` |

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
