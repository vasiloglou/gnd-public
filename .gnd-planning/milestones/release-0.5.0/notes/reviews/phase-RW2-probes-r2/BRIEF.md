# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 1 found that readme_commands accepted commands the README no longer documents. Does the repaired readme_commands in tests/test_release_acceptance.py, with its controls in tests/test_acceptance_controls.py, now refuse every README change that stops documenting a probed command, and does it still accept the two packaged READMEs for the reason intended?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. readme_commands refuses a README in which a probed command is commented out, given another executable, moved outside a shell fence, placed in a fence of another language, or split so that its tokens differ.
- C2. The controls in tests/test_acceptance_controls.py would fail if readme_commands went back to a substring check.
- C3. The repair changed no probe's assertions other than through readme_commands.

## The change under review

The work from `d5641d1d` to the working tree at `423ab44ffaba` with uncommitted changes. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/diff.patch` | `02d092fe3f722ba1cef68966f34b872bf0d982bfc7d649d330b33fbbc676ade6` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/probes-rehearsal.md` | `ea86cb5289a3417099c6f86503bc014d2089fa7de9417b72b4553bf2426a2a0d` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_families.py` | `2dd669bba9602610e1aa8c83aa73e85412eb0fbc58555a3bb6896b2d231d448e` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_probes.py` | `3783db17e2f4613d954befd972b49d140952a9a9230a592ab1ced8f560d9db00` |
| `.gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md` | `1b33075663a29d1d43a66513306cec03a48a440be3ad67fb1a7eefbfe8302990` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/BRIEF.md` | `e3f9047e24a47063c4d3469e0d2e16397e597a0e2ba2915ae2929cbe08962ac5` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/FINDINGS.md` | `30fba95dfbc5870f9c3db07e52ee79ea4f92bc72d7fedd7578430b304148c3ed` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/brief.json` | `bbd67cc3129aa4d883c521bef84897d5750b370b2b28cb220c3b683ebae655c6` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/diff.patch` | `815855dc71e1a478354812602d3c26b9f0d2bfb0fe236d4a61f9009b8a9cffae` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/review.md` | `829780f97398183ccb3c538f4d18b6c046d8e2411da61f7ba11f77d59dc992bc` |
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/run.json` | `de465725f9787a93f874d3a4fcedcbf622b85549c5ae288cfa6a84f2fe3aba26` |
| `docs/release-notes.md` | `7526c08e8ac8281e48d4b6cf8c138f9bb24aa6b4b833f834468c30a1254e1d25` |
| `tests/test_acceptance_controls.py` | `6fe0a5b635891eaa1e001c1609ead6fc95f2572910a00032ae9092ffe07c12e3` |
| `tests/test_release_acceptance.py` | `9d653ccf383e09204f513d10a8763dc9a15551cdd3ac7909fef9e16f2afdc89c` |
| `tests/support/markdown_sections.py` | `72631253374ac239743a895815bbe6efef32fff26e7077b039cbf6b40bbde3a4` |

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
