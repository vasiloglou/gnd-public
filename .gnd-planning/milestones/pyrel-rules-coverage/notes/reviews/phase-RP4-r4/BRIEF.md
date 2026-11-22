# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 4 of the RP4 phase review, scoped to round 3's disposition (phase-RP4-r3/FINDINGS.md): universes are now recorded where the lowering creates them. Is that complete (every site that uses an <type>_any relation records it, plans included), does it change any previously accepted program, and is any valid model still refused or mis-lowered because of a relation name? Prefer reading the source and running the existing tests over generating engine queries.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. r3-F1 fixed: a fact type named <object type>_any is read as that fact type unless the program also generates that universe, in which case the model is refused by name
- C2. Every previously accepted program is byte-identical (573 programs across the fixture and example models)

## The change under review

The work from `f02c58d8` to the working tree at `f02c58d88ce2` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/diff.patch`.
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
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/run.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/any-named-deny.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/any-named-empty-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/any-named-other-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/any-named.orm.json (not tracked yet, so not in the diff: read it whole)
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
- new: tests/fixtures/pyrel-rules-coverage/rp4/universe-name.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-deny.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-empty-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/universe-named-other-role.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp4/universe-named.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp4_role_value.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r4/diff.patch` | `a22302ff3b9629486c25833dc32869c4da3773deae7663df1f0e0f0ad27c6968` |
| `docs/runtimes/pyrel.md` | `014e743eab2890a875dd9617f94183ca5a66df08210f8aa8f45e8dbb9571899d` |
| `src/gnd/export/ossie_formulas.py` | `9f7c4d6f10a4bcb242709251f5f1da7bd2409878823835cb853622b8b167c93a` |
| `src/gnd/export/pyrel_rules.py` | `c9b537b7561d48aed701c14269e1a1178dd51a8e2dd859c24cfe45df2c133565` |
| `tests/support/pyrel_application_successors.py` | `77277babbb9cde455e67d4e0e6b4c6551ee9638c0c6291114fe40ced3431907f` |
| `tests/test_rp2_anchored.py` | `726ac9a3ce5b5593393286eaf555090b4e82392d94052bdf55a1abee8c730c16` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/RP4/dynamic-query-successor.json` | `19df7f6e7ec8be1f71d1806124e5438ec3bf69ae9d475fecddb55d68b4affdf1` |
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
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/BRIEF.md` | `9304962c1a242fe368e19451c6794ce800bbbb9e23990d43fedafa670d960d0b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/FINDINGS.md` | `ea4108d0d15ed10987d833186d898070372ca63fedc9008e8dc2a92ee33efa98` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/brief.json` | `7a62a4068511403ed8966f0e99afaed8d60b4aec2eca0b06609a885911183bed` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/diff.patch` | `7df2e23e01942c93d251331a3326204ad15904eb73a6ccb5131296633713e98c` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.log` | `fea01bd06eb2652c4d34fa933cbb2d8f87e118d1b9b7a1b23937a6fcdd7e130e` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/review.md` | `585f24a4bfe0a0e40348da48c9cb03a7f7c657cd89edc519c11dd5ac91ee98ba` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r1/run.json` | `edc4e801878797b803ed57435514ad1ff91f6c1a8a48a4b5efe6c2582008b396` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/BRIEF.md` | `0fdd472636d8cc3174e5ac462e91a162e442a657b97f10d215dc27cdf57c95e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/FINDINGS.md` | `2388c65e5591109d9093a2fe215ba461fe225ec10e3a236fcb5e69a2b2b3cc4a` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/brief.json` | `60ae36a5cfa6783dfc205f5ac4bb3914ef72fb8e46e666cacbebf093cdafa368` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/diff.patch` | `ae45eba69be70970f6d60a1ac5fc813aa3c6d0324aa3d2a7e9a98425fe5e1825` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.log` | `e2ff39ffe4763efc90d2c4ab6ac7410c2d1eba8a76fa5654f305cd97f99882fc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/review.md` | `3992b39a2e3aba20a0ae7b4e3eafa7a884ef594868f8fc3a8e27e54f3cdfe88b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r2/run.json` | `adc6d7094b28b9519506f60c722311f872c1124dc733ab476be95614acbd399c` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/BRIEF.md` | `9c808c3007930c6a0343f3aa86c261fa6c508e9260a431a15b17f991d4be7b5e` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/FINDINGS.md` | `89c2e1978fd352a9ba66dd5e7575c0744260070d2781658e1b4e00d4d00c2d6e` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/brief.json` | `1376d094b68bb0f771c355383e73ede95c9a7cbbdf2797b63bff8e902995b736` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/diff.patch` | `eeef18c97f0bfbe156b3db4fff28e8e3098e73afd3ad1b8ae95fb178bc6b8295` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.log` | `ab2e91fd3becb81067dde5f1681f0f1d10bdc83fffa9156163a1bbc4e3df3d34` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/review.md` | `7760330ca0daf57fd056f4cfcf237209ae48312aef11f63f1370014006fa7c12` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP4-r3/run.json` | `6c7b48ce8822b0f68dd36b744a2bec7b1bc7a04116ad37bc0be2233733229653` |
| `tests/fixtures/pyrel-rules-coverage/rp4/any-named-deny.population.json` | `b1200a75d39081c206f35a36b70aa98da8f922639ecbf1693d762bfd4d4eac75` |
| `tests/fixtures/pyrel-rules-coverage/rp4/any-named-empty-role.population.json` | `7b55c2be0f3fb653c8877050e5f7329d72a078410b25d15579116af90e9d14a3` |
| `tests/fixtures/pyrel-rules-coverage/rp4/any-named-other-role.population.json` | `2aaa2c4d867bc555b5b35f13e7f0c9842b98a4c504a6dad9f1556c9a21ae22e7` |
| `tests/fixtures/pyrel-rules-coverage/rp4/any-named.orm.json` | `20d4730537e4d6937a20531e61197a38ca062d8cc11d47733f895a8dcdb25e7a` |
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
| `tests/fixtures/pyrel-rules-coverage/rp4/universe-name.orm.json` | `bf83c4ad1a2a4903802db0a14c1c784e11b8162290fd7366cfe1730a45ed66ac` |
| `tests/fixtures/pyrel-rules-coverage/rp4/universe-named-deny.population.json` | `76b2a8e5490280bc3054b38e5cc85bbaa937d21324178986a0f85b1ea5af8e87` |
| `tests/fixtures/pyrel-rules-coverage/rp4/universe-named-empty-role.population.json` | `7badcf77d7957a0357c2157745ab12e81db5ba78845192878d5b38b5e129bd12` |
| `tests/fixtures/pyrel-rules-coverage/rp4/universe-named-other-role.population.json` | `53ddacac6b0c8e735365b4416b8b326c7d44c184f92749768336f25b32ee6968` |
| `tests/fixtures/pyrel-rules-coverage/rp4/universe-named.orm.json` | `063b61f45bad0efa32c5827bf91f8f1f27d2163fb5f6944dab57e204afbf9d5c` |
| `tests/test_rp4_role_value.py` | `89114550bd5d291b6ddee2c143be783c6a4228e5b45c3c122b4b0d43ef2e2f72` |

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
