# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change admit the assertions of a caller-named entity as the LH3 spec writes it, while the packaged admission keeps its bytes, and what model, population or judgment report does it get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every attached row of an admitted assertion is kept, no row naming an assertion that was not admitted is kept by any route, and the rows of followed entities are kept for every followed instance a kept row names.
- C2. An assertion is supported exactly when at least one of its rows is a target and every target among its rows is admitted; a target outside the attached fact types refuses.
- C3. Every refusal of a shaped call publishes nothing and raises Refusal with a value-free reason, for any shape, population, include path or max_rows value.
- C4. The walk is linear in the rows it reads and holds 65,536 rows within its time bound.
- C5. The packaged call, test_li4 and test_li5 are unchanged, and lineage_run.py's imports and call still work.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `fe46095e` to the working tree at `dcd3a61c1bd1`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH3-r1/diff.patch` | `9172b969cc31f29570c02e8f07c5117621a4caf1b1500d0ab3550d7d791435ed` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH3-spec.md` | `f5823c57c5fb585c7677f5cb0a110f8ee70e1dc2dfc5770d4cfa706c299cadc4` |
| `dev/components/COMPONENTS.md` | `88b4926625374028ead03becedebb6c7f62f9c092f4a0c6abd8dd3f5f83896ac` |
| `dev/components/graph.md` | `86c46d85565bec4153bfc58b3bf04bfa51cb99cbfc2462f99e61c262dcd01038` |
| `dev/components/modules/examples.md` | `fa5d4eb1c3685f9b7bdeabff84d96de57b2ed6fa5c1dbeaa04b5e9f32a2827af` |
| `src/gnd/examples/literature/README.md` | `2dfd3fcfa1bcae9a17009a55e7b67a4c9b9abc44ef644d55e3e8987e2e567807` |
| `src/gnd/examples/literature/assertion_admission.py` | `4b4e9431595ca91a574e07eb858be821f0fc66d11ac90a5d864b98685b86c858` |
| `tests/fixtures/lh3-admission/claims.orm.json` | `1518e043a6cb9ae8e5ccac823ca14c8988f04116e2e1153c7888e86811887e15` |
| `tests/fixtures/lh3-admission/evidence/passages.txt` | `99d67d1e1303673d3322dbfa51c7f285193d09da1001a5dc5fe7d02dfb1c6cbe` |
| `tests/fixtures/lh3-admission/terms.orm.json` | `05996ed42c345362ba99884466a7872bbfc11152f7290948c801c87e7dde3370` |
| `tests/test_lh3_admission_shape.py` | `cf566fce030978e3509ee2394b7bfba7edc83a5b5c43de515eb24afeaddc2024` |

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
