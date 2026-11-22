# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 3 of the RP5 phase review, scoped to round 2's dispositions (phase-RP5-r2/FINDINGS.md) and the PyRel rules-program section of docs/runtimes/pyrel.md: does any statement there still contradict src/gnd/export/pyrel_rules.py, per target?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. r2-F1 and r2-F2 are fixed; the runtime page's rules-program statements agree with the code

## The change under review

The work from `30643055` to the working tree at `306430558980` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
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
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/run.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp5_literature_rules.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r3/diff.patch` | `2c74e7233f2c1bc304f73842f605ab34ea0db43a0f9b5bf7f7a161c8eb665d63` |
| `docs/runtimes/pyrel.md` | `0ede803ef12cf966a1e5e67c043d405406df6717c3fba35acdb0fb2b1ad2f407` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
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
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/BRIEF.md` | `f533847d5d242c4868027fd0cffae1f8afa2099591c08a3eea044d946841fc09` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/FINDINGS.md` | `64b7019ca1ede73216cfa0890491cae982ead11e71b36d92eb621d9d819c715c` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/brief.json` | `2a3ad945364309fb466670244fada82f5943b7711e76ae6325f620e7f1ea94c3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/diff.patch` | `6b0691023b383991b0f3abb3be7773f02616c41da314c636182796609f3b8ceb` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.log` | `e4ca0c2def1bfa88799d5a3ecf9364edfafb1cc8cc6b06c478b6d47603f5276d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/review.md` | `3c42fd50e34605961cf0e694752aa2dec130f99d16cbbf8d92f5c27b5fe37a32` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r1/run.json` | `c8a5fa71983774803d14fbaafa3a89caa5431672392c7a2aa79b840a909c5e51` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/BRIEF.md` | `29d402d025351b0322f7abc42293f73ae08fb42a9a52d63e99fb0cf4024f8931` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/FINDINGS.md` | `19204364da4850a6b2288adc339d24c4a18be8f6f69243ee790b3bbc882888fe` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/brief.json` | `653d1a2a93e677b2097fa0e988d1c24d33f633448ec6b34937d5709da12de91b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/diff.patch` | `346531e3cec3082ecf55c8bab240d0667514ec2c86b89eb963d194293e5f738b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.log` | `cc7ad08e74abd2ed82c481626055160e4bb6433f8ea1bfc4e2f1509bd1d7c558` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/review.md` | `9f7d64949162b56591dc832310358de74701c261ae55fa5b65b57e96066811c8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP5-r2/run.json` | `e4148804aca89ea5bec401dbde395040d6f408c8911a312a3aa560c58c49fcd6` |
| `tests/test_rp5_literature_rules.py` | `fe35106e4b4f63eb619f99d6bd1be52a1e854bda070aee44950539b33b9bb9aa` |
| `src/gnd/export/pyrel_rules.py` | `449b67805f08b7ca3e43b6706aa41d01a72dd20072acd80ae0cb7369ef9a0da2` |

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
