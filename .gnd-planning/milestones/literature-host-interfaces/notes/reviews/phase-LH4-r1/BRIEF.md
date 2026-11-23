# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change make admission rules data as the LH4 spec writes it, while the packaged admission keeps its bytes, and what rules document, population or call does it get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. An assertion satisfies a requirement exactly when it has at least one row of the named fact type and every such row's value is admissible, and the first failing requirement gives the declared reason for the offending value, else its id.
- C2. The packaged call with no new argument writes the same four outputs as before, and the default rules passed explicitly give the same reasons in the same order, with policy-refused where the /1 record has fail for a supported statement.
- C3. Every bad rules document, rule naming an unknown or non-attached fact type or role, and out-of-range max_targets refuses with a value-free Refusal before the judgment route runs, and publishes nothing.
- C4. Every /2 record binds the shape and rules by digest and records max_targets and max_rows, so changing any one changes the record.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `8fffc161` to the working tree at `a84cff342aa8`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH4-r1/diff.patch` | `7b187abf685828d817ea3b306a30c4dbc2a974ba6bee59c9162d7e33f2a0eadf` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH4-spec.md` | `c78f2578899890ba579db643942724a659ac4eb8455ce528aaedd7a4589d6658` |
| `dev/components/COMPONENTS.md` | `580044aae2fab6ffb622b29ea0bdabb5f0b6668a1858ca96d72f8dd1a8ec4f1c` |
| `dev/components/modules/examples.md` | `9d9c1cf979642325ab2ccac5c0391b561ff8d45a6ddf1e78a3b0eb2a071ab9c7` |
| `docs/literature/commands.md` | `26485303f60ba06c426613f1b275468e6bd7b49b7523e5b9665f50b858252cde` |
| `docs/release-notes.md` | `1fa3010f9d0b60380e4933508250d3f984ef235a3b861c48b56488a1fe24f3bd` |
| `src/gnd/examples/literature/README.md` | `518990cc7568ac9949d2f813b7745a829d7c00b58ed8d07835744bc2de9a0d51` |
| `src/gnd/examples/literature/assertion_admission.py` | `e26e64448c946b8f6d3d15f6cef01ace65576251b06aebaa5097075c6a2ca952` |
| `tests/test_lh3_admission_shape.py` | `8196e84b454028c5cc2fddc5ff13626909e00ccff71642dcb3f2dee4ea80e366` |
| `tests/test_lh4_admission_rules.py` | `289f1979547d67c6cf29002ede33c946c44f7e32ceb700efe1299221f6203921` |

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
