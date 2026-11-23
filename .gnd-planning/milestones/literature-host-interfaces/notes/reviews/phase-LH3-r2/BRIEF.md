# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do these repairs resolve the four round-1 findings (in the retained review.md) without breaking what the LH3 spec requires, and what input do they still get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Two handles are one assertion exactly when the checker would treat the two values as one, for every value a population may hold, and every followed instance is keyed the same way.
- C2. Every refusal of a shaped call is a Refusal with a value-free reason and publishes nothing.
- C3. The walk and covers are linear in the rows and fact types they read.
- C4. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `dcd3a61c` to the working tree at `2d468b57282e`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r2/diff.patch`.
- new: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH4-spec.md (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r2/diff.patch` | `e48ec98ed93b3ce96b90aaecec3164d47eb212364ca2b3fd032a64656f8f8bb2` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/BRIEF.md` | `ed1776f11abca70f99b14852b3e4e1df5e999b640e89ad8579676c369985020e` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/FINDINGS.md` | `cf70e90666253ab1d7a4cc7b61f0eab04d5ba3a261be90f69819a634801e8f05` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/brief.json` | `93323ffea2f5e90136bac4cc91896059fc722fdba3fb5c4ff83412586b8d339a` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/diff.patch` | `9172b969cc31f29570c02e8f07c5117621a4caf1b1500d0ab3550d7d791435ed` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/review.log` | `ab47691910577a574bad7ee0971f12bc7349749d731235e9fe2fb273404a3bee` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/review.md` | `aab6cc702b70aff9b4276bfc664ccb41add101465ddddd585dea4bf94b268662` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/run.json` | `25a4c21f2094c1e924abfd0c0d089b89364fd28c73e2f7a36a151baecde30421` |
| `dev/components/COMPONENTS.md` | `60995a6849e00449cfe040e88b03ebb4fef01938ae11039ff1bfe3eae69596c4` |
| `dev/components/graph.md` | `f1ffc5a33cddb20d3234d93a4dcd125b6a922e893cdce49e368e2df1b2b7d63b` |
| `dev/components/modules/examples.md` | `ae1ed6aa5285c5b5106c60770f474394cc7c6415aa708c735f40c6d1677859f5` |
| `src/gnd/examples/literature/assertion_admission.py` | `8b96c9b18009e067e129a3f5f67e696446876a9c5237ab2c312df18cefb69688` |
| `tests/test_lh3_admission_shape.py` | `11bd0f8a0929837f0b0153af7943816a7d314e435df4987939eb968c852d6a66` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH4-spec.md` | `346960a79afe17dd7ee201659b99aa7089440cc3754af6fd6342e87d84f6499b` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH3-spec.md` | `f5823c57c5fb585c7677f5cb0a110f8ee70e1dc2dfc5770d4cfa706c299cadc4` |

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
