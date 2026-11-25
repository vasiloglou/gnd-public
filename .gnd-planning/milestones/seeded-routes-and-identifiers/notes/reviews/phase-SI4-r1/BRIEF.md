# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the source diff correctly prepare only the 0.5.2 tag and preserve published install pins?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. All five release fields and TAGGED agree, release notes carry SI1–SI3, and release-text and focused release tests pass.
- C2. Package-index install pins and publication metadata remain at 0.5.0.

## The change under review

The work from `a9acbc4d` to the working tree at `a9acbc4d5873` with uncommitted changes. Its diff is `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/diff.patch`.
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI4-spec.md (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI4-r1/diff.patch` | `706f2ab1e5e4fc8fe7b94db90d48439067c35d3e7382ab662e93a0c15f9eed16` |
| `.claude-plugin/marketplace.json` | `01e00a21f2db5ec81130ea1d32136cc6a94f1e1062e3901008c05cb4055211c8` |
| `.claude-plugin/plugin.json` | `1551fd6e7cfe078ee01b75755eb4b75b90b2a9dd6600de850646800ae1fb503e` |
| `.codex-plugin/plugin.json` | `286e0d3b4a41352797b06340148f5cc43e06627d44631aab1f2f612197138ccb` |
| `docs/compatibility.md` | `7557ce453df44b26a0b9b0ae607946db54a6bc27366f4556b1fb1cccbd12139b` |
| `docs/release-notes.md` | `4cd8cca18d8d4f91f4a5543ab4ea675305d80a271f33ba3dfcbdf050338cacb1` |
| `pyproject.toml` | `48ae2383765cec78ff87591f40dbebe8c0b558cebc0394613c2c0292a945d766` |
| `tests/test_release_version.py` | `aa7b6ec975ea944806dff16d12f9980fb4343142021312b4a5d396bd4077f90d` |
| `uv.lock` | `a8bf8a6a367ac116f1ac8531ad19349c22c497b6cbfb2c21bbf47d4c25ee23c1` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI4-spec.md` | `7e64cab6b41534872bc56b479fe1498c2bd042871d417e7dfb7da7c2f60fcbc8` |

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
