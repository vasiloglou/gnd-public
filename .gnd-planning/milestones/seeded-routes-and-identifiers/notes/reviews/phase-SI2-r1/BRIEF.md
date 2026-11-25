# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can the preference, tie, fallback, query budget or caller-compatibility claims be refuted?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Only anchored preferred confirmed alethic external uniqueness takes priority; direct and legacy fallback behavior are preserved.
- C2. Tie order is stable, component order is retained, and all 436 tracked reference identity results are byte-equivalent.
- C3. The measured static and dynamic runtime query inventories remain unchanged.

## The change under review

The work from `5699c76a` to the working tree at `5699c76accc6` with uncommitted changes. Its diff is `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/diff.patch`.
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/baseline.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/candidate.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/census.py (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI2-spec.md (not tracked yet, so not in the diff: read it whole)
- new: tests/test_si2_reference_identity.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI2-r1/diff.patch` | `0326614e061698831102fa229b8dbf4cb4120b587334f1f1cad2df7e82439681` |
| `dev/components/COMPONENTS.md` | `e3dfd8936a6a8bbe39185a8e65a1310b86a4937249e2c116eb7c53ad71a797a0` |
| `dev/components/graph.md` | `17b190bba686d3e9f0668270846e0e79e5a13c9dd4fd0a703b74eeacfa74900b` |
| `dev/components/modules/_root.md` | `69c1956e66aa042b672ed3c0f03109a7614689b3692b5445fd5633f2175e55a4` |
| `docs/release-notes.md` | `997c4ae93aedfc42f201e782f7b2d302275c738b3906d271974ccb3bc85fc526` |
| `src/gnd/refscheme.py` | `a0c94fa2b29bce6d47948276f40fb53e829b51adda62c5afa207ff8147d90833` |
| `src/gnd/rmap.py` | `8b4292c72fc86394a6f230cb370c0003df3b8efdccc1f307a463ffdf98578065` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `da6db6b00b846b4f93cae7f20733d463e6f5e72bcaa3fa313838cfa5097ef134` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/baseline.json` | `5f48cdaaabd59515ebad79d1739588c986fb61bac646bc106101b0a34c1e4d6d` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/candidate.json` | `5f48cdaaabd59515ebad79d1739588c986fb61bac646bc106101b0a34c1e4d6d` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI2/census.py` | `e59eace90c54c0d8570c446ab06eab060cff90511ebea7e8be7e5c017381e99b` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI2-spec.md` | `3f0efbeff3f05a41765f1d7fa314ce12bf4dd51216095aa770977687aedd7a49` |
| `tests/test_si2_reference_identity.py` | `b0f49cc33e313cf121ee9f648ddec2c4931ebc40278201367d3a82fe570cca7d` |

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
