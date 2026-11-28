# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Review same-evaluation semantics, fail-closed dependency coverage, bounded projection and redaction of derived extensions. Test novel legal inputs against the public API.

## The change under review

The work from `3ea6ea74` to the working tree at `87c387f53dc1`. Its diff is `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS2-r1/diff.patch` | `f09140ed205fb13be9d575928cb514b6ef12b7d7222403dedb9ea0498e737f9e` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS2/dynamic-query-successor.json` | `879f84beda850deb122eec7b8cba71a83d391db68c8640a6063ad66937445d63` |
| `dev/components/COMPONENTS.md` | `2cae07e154e06421ef950572ade638806a072913dd02bd1c8da25bc77c752306` |
| `dev/components/graph.md` | `bdab5883dcea89ed1c53e295f02ea8498e666d16ae5a3f53685f8c61a09c3370` |
| `dev/components/modules/_root.md` | `ccddf9cffdbc7f4c359e2fa9cb345f2be8194e9502eaa1df8309b0a34027cbee` |
| `dev/components/modules/checker.md` | `568405cf0473f795f5936f57573715895d4e14b81801ae250a7a4bb138b3e437` |
| `docs/reference/disclosure.md` | `a7d436bfcad6492cdc5a26df2696dfd4e418ba583e54e9f01960ada72d81a54b` |
| `docs/reference/python-api.md` | `f58eebc4a907c45b24dcf800045f3e720b0e89ab5213d091f5cfaac9f13d2a8d` |
| `src/gnd/api.py` | `449a3a377b4827fe7a3c1239dace3c35087b69ae8cecdce7a6c412db0255f8cc` |
| `src/gnd/checker/_core.py` | `fb285d776737426e6b39f1ba0922e013d795022d84cffe0a03dd88c5fcd83b89` |
| `src/gnd/disclosure.py` | `36d042b5c583adc817f0e16effaf1aa8ebae937475e0ae732b267a81b62fd353` |
| `src/gnd/extension_preparation.py` | `41b205be5743e1245d7982f670644e912ea3d266e36e425f3894e0b96f8a9335` |
| `tests/support/pyrel_application_successors.py` | `5cb6c4e2fc4658c9aa04afbf41d2378f8b5968d0f492b7d3280e954063b5fce8` |
| `tests/test_checked_extensions.py` | `ad4447007b4735fb91971098f893b5021941f5807bfba499529622aad82d34bd` |
| `tests/test_public_api.py` | `a4677f6cc0679a021c4d12845c460f22d2f13ee22cb9709667400b7b0b52adfc` |
| `tests/test_v61_phase2_api.py` | `ffea9639c30a19f14b1d615c3db6483daf307e193839fc32b9e67296522e5922` |
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/phase-PS2-spec.md` | `6c3f2457255f13238f4f0b4c7c71f9c47b7514904ba6bc480f691614c98f0fab` |

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
