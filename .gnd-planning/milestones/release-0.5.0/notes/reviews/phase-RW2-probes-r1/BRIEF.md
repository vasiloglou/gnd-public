# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the probes added to tests/test_release_acceptance.py do what section 6 of the RW2 spec says, and would each one fail if the installed package lacked the feature it names?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Each of the six probes asserts the candidate result, the candidate behavior control and the 0.4.0 control that the spec's probe table states, and nothing in a probe passes vacuously (an empty list, a loop that never runs, an assertion on a constant).
- C2. Removing the four 0.3.0 controls removed no assertion about the candidate.
- C3. program_constants reads the constants of every exported program the probes pass it, for any model and mode the export supports, without running the program.
- C4. readme_commands fails when the packaged README stops listing a command the probe runs.
- C5. The corrected sentence in the PyRel block of docs/release-notes.md is true of 0.4.0 as evidence/RW2/controls-0.4.0.md measures it.
- C6. No probe reads a file of the source checkout where the spec says the input comes from the installed package.

## The change under review

The work from `d5641d1d` to the working tree at `d5641d1dd9db` with uncommitted changes. Its diff is `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/diff.patch` | `815855dc71e1a478354812602d3c26b9f0d2bfb0fe236d4a61f9009b8a9cffae` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/probes-rehearsal.md` | `ea86cb5289a3417099c6f86503bc014d2089fa7de9417b72b4553bf2426a2a0d` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_families.py` | `2dd669bba9602610e1aa8c83aa73e85412eb0fbc58555a3bb6896b2d231d448e` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_probes.py` | `3783db17e2f4613d954befd972b49d140952a9a9230a592ab1ced8f560d9db00` |
| `docs/release-notes.md` | `7526c08e8ac8281e48d4b6cf8c138f9bb24aa6b4b833f834468c30a1254e1d25` |
| `tests/test_release_acceptance.py` | `1d3fc1ea3ca5a0131e4ebd690dee198c081c021ae24c2eadd8d3d2bd2d699919` |
| `.gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md` | `362bfc12a0d04161dbf4d4f458458e91f7b278c5e9d9f3fa366fa3457bcd9264` |
| `.gnd-planning/milestones/release-0.5.0/evidence/RW2/controls-0.4.0.md` | `db37a9144234705191a2db4309c19f3397814d9374a1da3542008b7d9e2e39c5` |

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
