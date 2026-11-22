# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 3 of the RP1 phase review, scoped to round 2's dispositions (phase-RP1-r2/FINDINGS.md): is the repair of r2-F2 (non-finite numbers refused in the population reader before the identity key) correct and complete for both targets and plan mode, and is deferring r2-F1 to phase RP3 (plan D6) stated honestly? Report any new defect the repair introduces.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. r2-F2 fixed: NaN and infinity in any cell are refused with exit 3 by both programs, in snapshot and plan mode, before as_integer_ratio is reached; gnd check exits 3 on the same bytes
- C2. r2-F1 is reproduced and deferred to RP3 with a named regression fixture; RP1 claims nothing about integers beyond 2**53

## The change under review

The work from `6cfeed33` to the working tree at `6cfeed33433a` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP1/dynamic-query-successor.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP3-spec.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/ambiguous.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-empty-join.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/assertions-integer-id.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-empty.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-facts.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-partial.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/disconnected.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/infinite.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline-repeated.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/numeric-repeated-fact.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/renamed-anchor.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/renamed-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way-duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way-pass.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp1/three-way.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/arithmetic.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/at-bound.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/boolean.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/compare-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/pass.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/range-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/six-line.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp1_external_uniqueness.py (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp3_number.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/diff.patch` | `88d2272cfc192c0331221a62dad7b1f7f506e472c3792a3e0395e4a063cc9063` |
| `.gnd-planning/milestones/pyrel-rules-coverage/README.md` | `49819e6f6ab850a173355f48858c1b7a1a3f278e1a0549b7d39b5321c5ab929b` |
| `docs/runtimes/pyrel.md` | `38712ee499852a45d9539c82edbbe915f2b8689a10501e670d57e6caa60daefb` |
| `src/gnd/export/pyrel_rules.py` | `3741a14fb647d673d282d6507d3e847cee0de92a1a6beebb6db81c87038745a1` |
| `tests/support/pyrel_application_successors.py` | `bd6429e6f3fddf231f9dd857c547e1418fbc69c9e0dd993790c25311f5b02006` |
| `tests/test_pyrel_rules_families.py` | `3389b5662e5153c46ef6ee01fa3875e7677dcf98df02770a3d0cfe11d3f01aa1` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/RP1/dynamic-query-successor.json` | `aa180028b0cd2291b8e168aa1a2f82ce1a5a014029a480cb255ca36b0d6a5be6` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP3-spec.md` | `e6d9f314294fa3891d8c2d134c4db1c7cbf70aa52f0704bd00590935f6c4e3bb` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/BRIEF.md` | `db5bd1a54ab5af81b66965312b0cf1b9ad7be62c529f3f066f0217413173b08a` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/FINDINGS.md` | `1c74a215688c64a7d153420a6c909e8ba6b2fe4f37ea6a5ee29e9494697e1ee7` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/brief.json` | `3fa96eb71e551973e9dba82a5400468f7c3b22bb23aeeb58504fa65359724ac7` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/diff.patch` | `dce5ed910fc49e7e445b9a50c569eaa3d72a93dbf2f4328e5e2907b1a2146dc3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log` | `61b8189d5c3f37a4536085e0f9d30f09b9fa1849c3981f47e659bb26ed802b07` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.md` | `af90362ec56fc315e9d9f9ea798a19244ea2e7aa7a9136af05d77434ac6aaf7d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/run.json` | `a9621041e30f46a31d748745dd83ad41bb2416283ef2cddb8ebe84974f96ad5f` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/BRIEF.md` | `7168243f89700aedd3c818ad9baecc34adbc1a95e4ddbcf9a1b4ee382a216f20` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/FINDINGS.md` | `7a072c4cde8c69d199cc2cf2c271d3b032037d9b98da1e783de18aea8a2ced83` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/brief.json` | `ca4172f36722c137fb8d82e65b2e26a5d71fe5f48370cc908cb1c092e911ecee` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/diff.patch` | `23595aa590c286019a45e3a72e579aa9e090c449aab00fc482285999c80055c2` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log` | `d0e90ec94c66fccf5adbf073dd259d5861ac05e98cdfddc8f541ac04242033f8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.md` | `90ee937652aa1dbee7763097cd61eafde25b39824b3b2a7b623406d9da1f8f9f` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/run.json` | `0e30df164b8685adfa13d8c532444bf81f93ef5a8bbaa8801a252448505cc851` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `tests/fixtures/pyrel-rules-coverage/rp1/ambiguous.orm.json` | `f3f03f1637adf5e8b93bfe45235d038a3917de186b4cd7364b3390353aa01e99` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-duplicate.population.json` | `8a5d7f5276f673a6ef11a31dcb78b7ec08a5ff1d42295d5b12cc60dae84e6a60` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-empty-join.population.json` | `baa942110dd260f6cbf432d0fa50130c027e66751b7376202bfa36125ef1ff24` |
| `tests/fixtures/pyrel-rules-coverage/rp1/assertions-integer-id.population.json` | `2a309fb0f0d47e3d6cf13b4a4cec42b138977fe5b33a521d2aac5caba8dc0afe` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-empty.population.json` | `4233be1a90c2bc42a5bc0282280dce817af058bfe1190694f8bf6626d21c2bc3` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-facts.population.json` | `9e2f8da3eba0920f8a85c02799babda5e3fac0c44684981779ec2f6ceb58323f` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-partial.population.json` | `69511dd3fa9360f4a364af91afafa579ca49327fe7f03503d378f022be5ee409` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.orm.json` | `5bc0193aa73074d9ec5707ed028c64b41ab6ce73a504c43b507be514e078975e` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected-semiderived.population.json` | `6ada9ab0584b8d3f8f22f1e1d58bcbdc44a5919982f85584433ea17605efff04` |
| `tests/fixtures/pyrel-rules-coverage/rp1/disconnected.orm.json` | `3d2c1de99b1837846295d5cdd0d62091a62a6d32000e2c0abf5f6679d846273e` |
| `tests/fixtures/pyrel-rules-coverage/rp1/infinite.population.json` | `fb544aca9dae1b6df03b3f268a655eea9e1dde03241843130c926440a62d002a` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json` | `b3eddc57affb401533190862e74a6a6149ffb48f5b17e9e596aac81bd30b37da` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-duplicate.population.json` | `179bf97f2e3a0fe3de23f3c89136d285bc443649f0b9d379af5f9665e315ec4c` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline-repeated.population.json` | `7a801ee030f95b29404b42c95df73a5ebe99cef1c4a2aabfb29d39c6bd87744d` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-inline.orm.json` | `62b3dd24c1d2f45015e1aa95713960b7fe1331422092643b229b0b38855f5a49` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-repeated-fact.population.json` | `105fad723955518127610069299439b35344ff544b6de6b084e5b27c7c3e4096` |
| `tests/fixtures/pyrel-rules-coverage/rp1/renamed-anchor.orm.json` | `6f6d4191965111f29dd891735ae6790183e682bdbe7426ff87a8434ee51639ff` |
| `tests/fixtures/pyrel-rules-coverage/rp1/renamed-duplicate.population.json` | `21d6b09b43d37ee4700b2b8e729324c59b8e8f02dc66cee7ecfe86ef5180e6db` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way-duplicate.population.json` | `459d7f4c776c7eeafe67028edbcd9e2f00a5bc80fa735957eef98c995ff91935` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way-pass.population.json` | `1a96a6509b3471a71d24e3d1638d806dcdc0e529128e33441fe540068b8eccd0` |
| `tests/fixtures/pyrel-rules-coverage/rp1/three-way.orm.json` | `2f683881401a274e9a093e94756772eab373706ddaeb9db366fc74925bc015d9` |
| `tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json` | `2575c355fe4ccd2f83bc2476423300bbf5327a06eeed0639e24c174c437563c8` |
| `tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json` | `f00a0d53b9f7b4220143065540d33ffaa6c263b8284348504616d6adb2528860` |
| `tests/fixtures/pyrel-rules-coverage/rp3/arithmetic.orm.json` | `b31092be400e78f3f7041b24b6070943ba4edd4d4b0d2bae0c0e3081caf3a643` |
| `tests/fixtures/pyrel-rules-coverage/rp3/at-bound.population.json` | `12cd79553b2b897406e5e95ec9c88dafad316e248659c5301bd197b6627f039f` |
| `tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json` | `27d6e2c35ba5331560a77ba9e96e4a2f7fb9d9af1ca12f8fdb78a9d3bc7ee702` |
| `tests/fixtures/pyrel-rules-coverage/rp3/boolean.population.json` | `38393e12ee97f26369196be0e7b6b0f30bf46f6fa8a4cdbb3eae5973a7ae42ae` |
| `tests/fixtures/pyrel-rules-coverage/rp3/compare-beyond.orm.json` | `80fb56a869275989629944365fc0a5f7f9da331083432626b3116f8efa4bb779` |
| `tests/fixtures/pyrel-rules-coverage/rp3/duplicate.population.json` | `c1605ddab8a000905d28a565cb73d0a7ffedad7e83f3d48b7c08698a9b9e2f22` |
| `tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json` | `ecdb57e13faaba619f167d6618862d058a58a819f0ebafd2616c108f904a2822` |
| `tests/fixtures/pyrel-rules-coverage/rp3/pass.population.json` | `86f49f990c7d5951f566f7bffb2c3810d2ec2bde1d53f18b6674ccd4133ebae4` |
| `tests/fixtures/pyrel-rules-coverage/rp3/range-beyond.orm.json` | `edaaa636d7cc2784afc46d9d27fd4bd332351d77313b54230326f995f6582e33` |
| `tests/fixtures/pyrel-rules-coverage/rp3/six-line.orm.json` | `d27c126262a79e01d7cc919c56749aef083a6d52d4eccc5b9697399608b98668` |
| `tests/test_rp1_external_uniqueness.py` | `f193dcc0ee023e0ff22ce6b3ac8fd8edc695fd52500d2f9409572554e37d6c8a` |
| `tests/test_rp3_number.py` | `8fcc57be0aefcc5330e43d5c149625aefd3d04207dc4977c93b11f04afba5e7a` |

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
