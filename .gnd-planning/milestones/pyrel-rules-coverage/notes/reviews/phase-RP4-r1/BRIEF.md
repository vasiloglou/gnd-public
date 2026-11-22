# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the RP4 diff lower value constraints scoped to a role (role_ref), at the top level and on a fact type, so that both rules programs give gnd check's verdict and witness on every accepted input, and keep every other value rule's program and verdict? Prefer reading the source and running the existing tests over generating engine queries.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. RP4-C1: a role-scoped value constraint renders at the top level and on a fact type, under both targets
- C2. RP4-C2: a disallowed value in the role is denied (exit 1, GND's witness); the same value only in another role or only in the roster is not; an empty role is vacuous (exit 2), agreeing with gnd check, for allowed lists and ranges
- C3. RP4-C3: quantity_fixture/time.orm.yaml exports under both targets
- C4. A fact-scoped value constraint without role_ref covers the object type's universe, as GND scopes it
- C5. Allowed lists have one home (_Model.allowed_lists); models without fact-scoped value rules render the same allowed lines in the same order; the Ossie export keeps its bytes

## The change under review

The work from `f02c58d8` to the working tree at `f02c58d88ce2` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP4/dynamic-query-successor.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/review.log (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/deny.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/empty-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/fact-plain.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/fact.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/other-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/range-deny.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/range-pass.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/range.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/roster.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/top.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp4_role_value.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/diff.patch` | `7df2e23e01942c93d251331a3326204ad15904eb73a6ccb5131296633713e98c` |
| `docs/runtimes/pyrel.md` | `014e743eab2890a875dd9617f94183ca5a66df08210f8aa8f45e8dbb9571899d` |
| `src/gnd/export/pyrel_rules.py` | `d55721aece9504da4061d1836c33d9b5aa90c5bf6a63de1e21659021ea9d2b1e` |
| `tests/support/pyrel_application_successors.py` | `77277babbb9cde455e67d4e0e6b4c6551ee9638c0c6291114fe40ced3431907f` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/RP4/dynamic-query-successor.json` | `c022ddae35b15cb79d7fd3bca0825c2f44e2aa9da9b05befdbf4bd57340ded78` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log` | `61b8189d5c3f37a4536085e0f9d30f09b9fa1849c3981f47e659bb26ed802b07` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log` | `d0e90ec94c66fccf5adbf073dd259d5861ac05e98cdfddc8f541ac04242033f8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log` | `05bc3b2eb8c9636dde3db8d5b71a5ba51b59ce06700c4cbc686dcff7c7fe1f45` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log` | `e83ab190ab34f86b255479d6d528916dd076b2fa03477769811f34c2db0aa699` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log` | `089fe70f90199f11bf7cde276085671f08b8875bf852aa83798d1ffa4f30c3dc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log` | `60113bbb25a9c8716354f64e817d3858f20eec58237f5887bb49edbb4534f2e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log` | `ffa10e00994837a411eb06a46b4c9d5a88c5ae49fb1299a1ca6cc1ef3dbf1eb0` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log` | `f4b07190f8502f9d663092c3f1127e5c65a2ec57a5b8105373069c86d7756579` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/review.log` | `f23ce9c86169caeaaa8828030900ce41eb63a0180d84beb908b9783827d25a60` |
| `tests/fixtures/pyrel-rules-coverage/rp4/deny.population.json` | `df3afbce412d0e50ee80290679a1ba690bb74f738f44b2b9dce573e2384d71cc` |
| `tests/fixtures/pyrel-rules-coverage/rp4/empty-role.population.json` | `580e61fc60f2ec091bde2b64178920b50594e94c5439835a9df8f5afcce71c78` |
| `tests/fixtures/pyrel-rules-coverage/rp4/fact-plain.orm.json` | `291da941078576734358ee6c2ecf2abfa14eefa1fec652e348a6e3cf44502b2a` |
| `tests/fixtures/pyrel-rules-coverage/rp4/fact.orm.json` | `43b015988335a3eb522be3fb9b8c985a198d85deffbc1d21357a607299bc86a6` |
| `tests/fixtures/pyrel-rules-coverage/rp4/other-role.population.json` | `aaabdd83fc07f181b310851936535fa30e690bd93f76501e352bbe77e56a2b2d` |
| `tests/fixtures/pyrel-rules-coverage/rp4/range-deny.population.json` | `612f53bf66f5383541b4d8940a96215c3947e6610707cc9531f3fc1ba530eabc` |
| `tests/fixtures/pyrel-rules-coverage/rp4/range-pass.population.json` | `24ed55fb7631aa60a63eed52e7ec7b150cb7fd92437bfd07ad77c9058e630a2f` |
| `tests/fixtures/pyrel-rules-coverage/rp4/range.orm.json` | `c50fe4662e9b928d17921ed7d8a6ead59647f6ee4e9d284b9c71cbd525cbd47a` |
| `tests/fixtures/pyrel-rules-coverage/rp4/roster.population.json` | `3c9ff8ec19ee5c23e03dd0aa8625ef5292214395277d445e0f15069a77843422` |
| `tests/fixtures/pyrel-rules-coverage/rp4/top.orm.json` | `1ddb2192321f338d9413e718523abd72c52a6cf8b3a9c5e74097b45f3078a0ee` |
| `tests/test_rp4_role_value.py` | `3012d8da76144ac5a84c2cad2c924a332e8ef6f1bbddb4003164e153f68da7d1` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP4-spec.md` | `8c27d84c579c85df74b7455905409b0c81a4cac4d7ba29c1895b5e326956b26b` |

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
