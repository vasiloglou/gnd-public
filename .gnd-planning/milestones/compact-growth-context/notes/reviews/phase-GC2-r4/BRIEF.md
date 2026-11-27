# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the shared positional vocabulary digest fix the reference-bearing loader regression without changing historical model digest behavior?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The reproduced nonfinite metadata now loads, while changed included rows still refuse.

## The change under review

The work from `dafd95f3` to the working tree at `21b7286f3bf3`. Its diff is `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r4/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r4/diff.patch` | `39046f20a6633d4394c9ef922d046ce4b098534f967ec2b342e596b1a6f1e97d` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/BRIEF.md` | `90919ff4cd9dfbca69fc3d8ac26952cfde1f3e3978a5f46f81c7649df003de10` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/FINDINGS.md` | `0ff84bc4dd7cff101b848fc5cabad8b355ddf9b92a66fb9ce71fe601742561b3` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/brief.json` | `a1a692ef02d50f276aec862cbb6cc9a5c056fe331f58c53b8c3157b731a2353f` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/diff.patch` | `ca513736aa56cb068cf31d44f26777825634ec9517541d0ed94ca44164438c42` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/review.log` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/review.md` | `e090ac21409624b03767310c5d18454cc5aedd1d758ba917a6abafc448d7d01a` |
| `.gnd-planning/milestones/compact-growth-context/notes/reviews/phase-GC2-r3/run.json` | `65be7cd9d7e7d870fe171f7a6033af2c8d806436f834693ba4fb156c465ee3ea` |
| `dev/components/modules/_root.md` | `8b97a76c7792d502bf5e37f4f514d105d0212420837a16f9b9c67a79a7e2c94e` |
| `src/gnd/api.py` | `55da652f4d1f6f61876aecf63b173415c6fb05a6b6ddf3eaedd67f4775d7f86e` |
| `src/gnd/model/__init__.py` | `b126fe5ae74d39ff4a4068026f2285b2ceb073b8f810f5c971bbe5bdc8a1973f` |
| `src/gnd/values.py` | `8d4ad723d3c1851ee0ecebfcf355cf114949b8e356fba667b40af4ccf97cac14` |
| `tests/test_growth_view.py` | `7e42b22b3db01f9256bd0bbc3435b925dde9b68779e33965bf1f9c16f1fdb72c` |

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
