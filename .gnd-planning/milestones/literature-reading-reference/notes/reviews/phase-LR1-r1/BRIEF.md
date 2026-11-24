# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff make the documented steps in docs/guides/documents.md list exactly the constraints and derivations a gnd verify exit 1 failed, with their rows, for every kind of report a host can receive, while leaving gnd verify's output unchanged; and can each test fail when the behaviour it names is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. LR1-C1: on the reported conflict, the documented steps give exactly one failing constraint, fact_types[subject_label].constraints[0], kind uniqueness, with its two rows.
- C2. LR1-C2: on the broad population they give none, exit 0.
- C3. LR1-C3: every field name the section uses, at report, constraint-verdict or derivation-verdict level, is a property of that level's definition in report.schema.json and a key of the live report at that level.
- C4. LR1-C4: a deontic-only violation is listed as a warning and not as a failure; a redacting model gives the marker and the page says so.
- C5. LR1-C5: the default gnd verify text and JSON for both sources are byte-identical before and after the phase.
- C6. LR1-C6: every exit-1 fixture gives a non-empty listing, including a derivation failure.
- C7. The page's steps are correct for every report gnd verify can emit at exit 1 under this repository's current schema, not only for the fixtures the tests use.
- C8. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `9a10bda1` to the working tree at `9a10bda12d8b` with uncommitted changes. Its diff is `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/diff.patch`.
- new: tests/test_lr1_verify_failure_listing.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR1-r1/diff.patch` | `fd246d1caab2cf284ab9dfee9df81350e2b7ddc9b01f371f0774c3ec0de16e59` |
| `.gnd-planning/milestones/literature-reading-reference/notes/phase-LR1-spec.md` | `bfb5249ee2b075a89df8b5adfb0b893b62fd2508bc50744466d1c31b4a69769b` |
| `dev/components/modules/tools.md` | `6688ebca9c96106092055586d1fd6159c025eb5439ee2c470fa576464cce3170` |
| `docs/guides/documents.md` | `8b546b80e066f2224b0ef38eea3e4a77166f909d903c8b2afce4c9d8407cd5db` |
| `docs/literature/commands.md` | `1b2a12be2af4759d8aecbf8314ccc87e516f51a3cc1ea4c03c20cefef4f0e334` |
| `docs/release-notes.md` | `03fa8b0ea7dba08ea4ce8796613639861bfe51892ffc80feb59c347a58632ffa` |
| `src/gnd/skills/gnd-extract/references/extraction-contract.md` | `3af890ab079323e6f6d4a3d11a8a99bcfa253051196e6fa578313f5a1da4ea08` |
| `tests/test_documentation_tutorials.py` | `9dfa5685b9e0e9471b14d9e9cfc8569e2306980db62c9ce04486c5943334257a` |
| `tools/run_tutorials.py` | `06ae7f3a7919b30faf6e67f4a02344aa3aed1e8bb7dfd68edf97d0f20ea1b156` |
| `tests/test_lr1_verify_failure_listing.py` | `d61b5876a36a815543c926905167f8f1cc01075b6650db96c1a6dd553907fcde` |
| `.gnd-planning/milestones/literature-reading-reference/notes/literature-reading-reference-plan.md` | `b07cf6895adac043d8de451c95c49a44ff0e7aac29eb5c4ab9e3b2ed076aa772` |

You may read anything else in the repository that helps you answer.

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
