# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the pages this diff changes state one correct rule for where an anchored span may lie, say correctly what it means for a host that shows its model one section at a time, and describe the packaged reading example accurately; and can each test fail when the behaviour it names is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. LR2-C1: the rule is stated once, in docs/reference/anchors.md, and the literature pages cite it.
- C2. LR2-C2: a quote from a source's second section binds when the sidecar names the whole source.
- C3. LR2-C3: the same quote is refused with anchor:binding-mismatch: source span or excerpt differs when the sidecar's document is the first section alone, and the test tells that branch from the digest check.
- C4. LR2-C5: the example README says its verify documents are the joined attempted sections and, for the reported conflict, conflict.txt, each bound by an extraction sidecar and none by an anchor sidecar.
- C5. Every statement the changed pages make about gnd's anchor binding is true of src/gnd/anchors.py for every legal sidecar and document, not only the test's.
- C6. The interim reply draft (notes/issue-reply.md) says nothing the repository does not do.
- C7. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `c17ae2d6` to the working tree at `c17ae2d6f642` with uncommitted changes. Its diff is `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/diff.patch`.
- new: .gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/literature-reading-reference/notes/phase-LR2-spec.md (not tracked yet, so not in the diff: read it whole)
- new: tests/test_lr2_quote_scope.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-reading-reference/notes/reviews/phase-LR2-r1/diff.patch` | `664f87ab74416b223359794ba83e27d9553f29f5983fbaddc706b1a2af3026fa` |
| `docs/literature/commands.md` | `65c59143405af0148fd8effc404203344a5ca09d5c26b81097f75b1986f7b735` |
| `docs/literature/index.md` | `29fb040bbb723af20a679096f355ad61c97a669eefb6180aa4008d737616ef38` |
| `docs/reference/anchors.md` | `adc5acc80c4f339789f5d6440d2c413b2bcb9f924b5ef84635cc0086b155467f` |
| `docs/release-notes.md` | `9a802239153a0d3b8da5284ebb6a4875231b03fb1822397adfd89593d9cd478e` |
| `src/gnd/examples/literature/README.md` | `45f205c57720ee122717a08d8d2ae30c1a2e566e07a6fa6ae42cde0ce52f120c` |
| `.gnd-planning/milestones/literature-reading-reference/notes/issue-reply.md` | `6fe6dabaa8bf53f4b9d529e8edcd228778fd4b599af52ed41e696db89e1fcfef` |
| `.gnd-planning/milestones/literature-reading-reference/notes/phase-LR2-spec.md` | `3ea42e6a3fa2bbf72000701ab5dbc0f3a4d31c1cb09a24945dfe6c5e363e63a2` |
| `tests/test_lr2_quote_scope.py` | `2b3a5a9f7e213e08ec7114059bb2aa59d71105b52a48d8a90f704f75b130935d` |
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
