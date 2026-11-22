# Review brief: the milestone close

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

The milestone close panel (evidence/close-review/PANEL-REVIEW.md) raised 17 concerns, dispositioned in evidence/close-review/disposition.md. Are the code repairs correct and complete (the LQP version's disconnected-join vacuity and its refusal over derived fact types; population shape refusals in both versions), did they change any other verdict, and are the record repairs (plan section 11, close-results.md, close-delta.md, the runtime page) accurate against the code and the phase records? Prefer reading the source and running the existing tests over generating engine queries.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The LQP version now gives gnd check's exit on an empty disconnected join (2), and refuses at export a disconnected join over a derived fact type
- C2. A non-object population or a fact list of non-objects exits 3 in both versions
- C3. Plan section 11 quotes the r4 wording verbatim; close-results.md and close-delta.md agree with the phase records

## The change under review

The work from `e99782fe` to the working tree at `e99782fee629` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/PANEL-REVIEW.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/disposition.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/claude.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/codex.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/gemini.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/glm.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/kimi.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/qwen.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/review-request.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/synthesis.json (not tracked yet, so not in the diff: read it whole)
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
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/array.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/bad-row.population.json (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/close-repairs-r1/diff.patch` | `da47eba0cc5d2d117c6cf01eb87277cc7085de03d1f75e19aa3f0555720f38d3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/close-delta.md` | `98afb13af56ea29a50b3a9be9bf1baad18c4864a4619e40fb942c9254d7cfb6d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/close-results.md` | `6333b7a6a88cfee7ece325f40fc6941f293400f86e9428838562ebc2e03cc129` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/pyrel-rules-coverage-plan.md` | `39d0d0a2f1b29e32595be255a8aea87d4be57d134dc20a2e4933391fe3c5db42` |
| `docs/runtimes/pyrel.md` | `a661e35eddcd02084b0255db5e908da51b465b068236deba004cb085c642f31e` |
| `src/gnd/export/pyrel_rules.py` | `321a989c9178c31eab091702e4f4ee45692dff24085044bb6485af6137f9e1d6` |
| `tests/test_rp1_external_uniqueness.py` | `368107e86ed52d5c41c0d0ea0878bcbb2e3faf9a54cc74e1a90f273abe086a4d` |
| `tests/test_rp3_number.py` | `71cb75280fa7c92db0a2036a1a4b8a18ecaf7198a2012c626f92979d15be1623` |
| `tests/test_rp5_literature_rules.py` | `2f7ce0a63b339fcc5d282ad0ec09b6dd9ab0c2683d0cd29a0959edb5b8d4b793` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/PANEL-REVIEW.md` | `bee00b7c8a7d2e754e83f09f6ff3b97848e37cac584c49b19245edb220cf34ae` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/disposition.md` | `c1858dbcef31e7dd71a778400a9dccc29f4bad260009511acfac47ff492aab11` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/claude.json` | `7a311052af276a5aa319c3f464c7e0f7370db2fbaa3a5326d8c7c2f34842e1f6` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/codex.json` | `0134805d7d2044f1a88c6470d5e7de03a4e0d154b9eb3e2c0e3da53705b55de9` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/gemini.json` | `b02e13684330b50e6f5d5779264808d173c9ed99812872520b3460fcc59fc2a1` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/glm.json` | `f221acd030fef42f499e10941240dc986b0ca1487fa41fcce1216971fed9c5ad` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/kimi.json` | `532bc56f30db5bf3c54252e5303742980d2485ec55586ec00a176d331a30aa49` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/responses/qwen.json` | `2f685c5123192eda470d8bba99a2132d09871760649f089ff8df05cd6ee08bd0` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/review-request.json` | `5c413d01b2ef2b31ea7dfcdde0f626b6ce94853293af2e05e85c47ae8e38ae70` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/run.json` | `4304fd11dbf30f8b1b2a48aaa335b6f8b0d41e02ef9bc8e027dce1063bd53025` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/close-review/synthesis.json` | `992a87c8d4db71290a31f0e1faf61bf5a03a44119d0c6fe942357026435b7a92` |
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
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log` | `fea01bd06eb2652c4d34fa933cbb2d8f87e118d1b9b7a1b23937a6fcdd7e130e` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log` | `e2ff39ffe4763efc90d2c4ab6ac7410c2d1eba8a76fa5654f305cd97f99882fc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log` | `ab2e91fd3becb81067dde5f1681f0f1d10bdc83fffa9156163a1bbc4e3df3d34` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/review.log` | `97081678f1accf06646ea5d3c380fdc4dec15b77ff19598ae2f7eb1c077f1962` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r5/review.log` | `6db634fb7408b7c272fc10b1f860ae9e940be4fc8e21e7fc8835dc78de13189b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log` | `e4ca0c2def1bfa88799d5a3ecf9364edfafb1cc8cc6b06c478b6d47603f5276d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log` | `cc7ad08e74abd2ed82c481626055160e4bb6433f8ea1bfc4e2f1509bd1d7c558` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/review.log` | `177140b83b6631167ce6e8e52ad948c70275e43ef28c65331b07414288d70954` |
| `tests/fixtures/pyrel-rules-coverage/rp1/array.population.json` | `b247a5a0003a51a81a3e441a6308dd294a82089427f6e19d70b0c461b4e15669` |
| `tests/fixtures/pyrel-rules-coverage/rp1/bad-row.population.json` | `eae45664589906cf362e133dfeffc0ecd1798897cec9d54c938b74edb1d5e88c` |

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
