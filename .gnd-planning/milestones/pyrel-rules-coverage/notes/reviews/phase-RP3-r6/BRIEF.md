# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 5 of the RP3 phase review. Read the code: is phase-RP3-r5's finding fixed, and can any accepted model or population still give the generated programs a number that a binary float rounds, in a derived head, an aggregate or its result, a comparison, a cell, a roster, a plan binding, a reference fact or a model constant? Do integer-only derivations still export? Prefer reading the source and running the existing tests over generating engine queries.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. r5-F1 fixed: an aggregate result has its type in the comparison guard, so comparing an Integer result with a Float or Number variable is refused by name
- C2. No accepted model or population gives a Float or Number relation or comparison a value the programs would round

## The change under review

The work from `6b9dc077` to the working tree at `6b9dc0776074` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/evidence/RP3/dynamic-query-successor.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/run.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/BRIEF.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/FINDINGS.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/brief.json (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/diff.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/run.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/arithmetic.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/at-bound.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/boolean.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/compare-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/computed-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/count-into-number.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/duplicate.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/head-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/int-arithmetic.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/nested-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/order-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/pass.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/range-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/reference/empty.population.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/reference/model.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/reference/references/anchors.pop.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/six-line.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/sum-compared.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/sum-into-number.orm.json (not tracked yet, so not in the diff: read it whole)
- new: tests/test_rp3_number.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r6/diff.patch` | `355978ed57ff570902b384f4793e38f907e8a35f5506acdd8f5147de902cfd1d` |
| `docs/runtimes/pyrel.md` | `a76ce7354ca28253e60c6a68ff04fb681d4b1f96bfc9098772a8cc26bac4e747` |
| `src/gnd/export/pyrel_rules.py` | `1118889620d1f42200ed04fa3402e475f96710d52ace03905a417d2430919ca7` |
| `tests/support/pyrel_application_successors.py` | `ab99a0f3d1232d7b78b68d5f31d8d30efee3e30fc4f6180ddc3fe78ee719d6b7` |
| `tests/test_pyrel_rules.py` | `bcc7a1c457a0fd943edbda94e5952c8bdc99ca2ccc06d535af17684f8791eeb8` |
| `tests/test_pyrel_rules_derivations.py` | `77d2d97bf1400e0ad754c3ab19aabbfdfb5160958dabcc9930eec056289cb579` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/evidence/RP3/dynamic-query-successor.json` | `c4ead81606deb9bef17fc06d9d3adbadfab0760e8b9d396c509fa6d8079160fd` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log` | `61b8189d5c3f37a4536085e0f9d30f09b9fa1849c3981f47e659bb26ed802b07` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log` | `d0e90ec94c66fccf5adbf073dd259d5861ac05e98cdfddc8f541ac04242033f8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log` | `05bc3b2eb8c9636dde3db8d5b71a5ba51b59ce06700c4cbc686dcff7c7fe1f45` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/BRIEF.md` | `548192d94078d7d81c90fa879d5d048b63712c0f4b1a5cbc8b939435bd9283fe` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/FINDINGS.md` | `59e0f1728182748e85efeb15afc1d73ce30930a4cd0a2125d68a647831253a39` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/brief.json` | `0bfcf4fdd2701bde382935c6f73bf2a0552c46e6fbed7b9a152533f31432f296` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/diff.patch` | `ff4a4b2fe0ede74ae25c8919fd51d152ce56207f2324a8e72d2390b7d5698037` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.log` | `e83ab190ab34f86b255479d6d528916dd076b2fa03477769811f34c2db0aa699` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/review.md` | `0762c18d8e80cc5572e06ef06c27827a0f9d9ddd58bc81967c217b8798458fa3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/run.json` | `5a49f498dc9813420cb828350646d7bde823deeeb13dbfba040d3c2aa567a21f` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/BRIEF.md` | `70863fe1db8c76ef705d1e190d3ca21d9c5833dbc50d7d27360606466d178bf8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/FINDINGS.md` | `34bfe782a79c5c254ec0b20b26c6242a05027bf412c32072ce3d98cf760bc6ec` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/brief.json` | `df81c57e02331eddf671dba7a07964edf9653f7fd4f62049c975453d4f40f821` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/diff.patch` | `d7f1e8d83d307fb93e70982175542aaa0cab20c8465500045ab2c1c713987b0b` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.log` | `089fe70f90199f11bf7cde276085671f08b8875bf852aa83798d1ffa4f30c3dc` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/review.md` | `388fc6325925ffbf19c72ab525ff6709c062c6e1732982a5ca12f4b880304f48` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r2/run.json` | `2529d07c01712788015156d2cdb3023ab1e07afbb39631dfaa1e5888b81bef68` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/BRIEF.md` | `8e4b2ec53e01eb61dae4c68791363cab47bc4355eeb9101334f8faae5576ec51` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/FINDINGS.md` | `2a18e0e567d4f6fbf9c5d3f872e9a5bc4c8fd9a5f72e985af32081876fe0b178` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/brief.json` | `e3fc24d569fb5fc7196017968aa02a5f6bc15460ea0e95be05d1349795d0fb85` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/diff.patch` | `a145fb1a17bbd4dcbdd380c7cc03dce1db2dc560e02a67d8fcdd9bca312a2f02` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.log` | `60113bbb25a9c8716354f64e817d3858f20eec58237f5887bb49edbb4534f2e3` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/review.md` | `1dd3d195baee2300266fd21344a40b2760edc6098d7ed4f946be60284d1fce08` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r3/run.json` | `e701b13b35ebaeb40b8edba5f24ac4728155319fc1b86c3a38c3bc885e512737` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/BRIEF.md` | `03cc65f2b8ff8b3352f2b9803a0f282e4a329c5ea8e228a628967fdc2f19aeaf` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/FINDINGS.md` | `3e301ba96742cc92ac6d0b073a007fd5f85fd90839b6f07403526b1ac114dd56` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/brief.json` | `307d5d49a4cd4f30934414e51b63fe0a24e7b97d9b0526f7810119e554e48597` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/diff.patch` | `c6928627aa2fd520b8f33acc88baf93143ace5987381f4a3c6aac1c2cd676c75` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/review.log` | `ffa10e00994837a411eb06a46b4c9d5a88c5ae49fb1299a1ca6cc1ef3dbf1eb0` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r4/run.json` | `9b98e9e0f36a7e995790e1fb5057af14fffa924f275ceec574b521f27fd86af5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/BRIEF.md` | `8fc4d3b44fb26ef55f2a3afc871c62b8a31528ed2dd34ac212aca2b43f6b91d4` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/FINDINGS.md` | `59e102ba5ac46cbb55f1a95c371d39d7738faca99d693bc927443cab76774e13` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/brief.json` | `7301b7e49029b3fa64d21f091ac20768399768eb53e36f489d056583edfe99a2` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/diff.patch` | `c6928627aa2fd520b8f33acc88baf93143ace5987381f4a3c6aac1c2cd676c75` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.log` | `f4b07190f8502f9d663092c3f1127e5c65a2ec57a5b8105373069c86d7756579` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/review.md` | `ab7a2fb8ce665b79c8439b66e282e5524f13591cc08f5a990871c14152504c39` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r5/run.json` | `ee5060e5c55d38b40e83167cb0d1653514010371b00b137494fdce1991f007f3` |
| `tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json` | `2575c355fe4ccd2f83bc2476423300bbf5327a06eeed0639e24c174c437563c8` |
| `tests/fixtures/pyrel-rules-coverage/rp3/arithmetic.orm.json` | `b31092be400e78f3f7041b24b6070943ba4edd4d4b0d2bae0c0e3081caf3a643` |
| `tests/fixtures/pyrel-rules-coverage/rp3/at-bound.population.json` | `12cd79553b2b897406e5e95ec9c88dafad316e248659c5301bd197b6627f039f` |
| `tests/fixtures/pyrel-rules-coverage/rp3/beyond.population.json` | `27d6e2c35ba5331560a77ba9e96e4a2f7fb9d9af1ca12f8fdb78a9d3bc7ee702` |
| `tests/fixtures/pyrel-rules-coverage/rp3/boolean.population.json` | `38393e12ee97f26369196be0e7b6b0f30bf46f6fa8a4cdbb3eae5973a7ae42ae` |
| `tests/fixtures/pyrel-rules-coverage/rp3/compare-beyond.orm.json` | `80fb56a869275989629944365fc0a5f7f9da331083432626b3116f8efa4bb779` |
| `tests/fixtures/pyrel-rules-coverage/rp3/computed-beyond.orm.json` | `5488c3748dc840b7e849b164ed413035943b7eb9d75512ad0af431492297131b` |
| `tests/fixtures/pyrel-rules-coverage/rp3/count-into-number.orm.json` | `0fa8a742a93907832b5656ffcc1cd601f0d967c1a1dd328a33ddff27856ffb15` |
| `tests/fixtures/pyrel-rules-coverage/rp3/duplicate.population.json` | `c1605ddab8a000905d28a565cb73d0a7ffedad7e83f3d48b7c08698a9b9e2f22` |
| `tests/fixtures/pyrel-rules-coverage/rp3/float.orm.json` | `ecdb57e13faaba619f167d6618862d058a58a819f0ebafd2616c108f904a2822` |
| `tests/fixtures/pyrel-rules-coverage/rp3/head-beyond.orm.json` | `69f059e275880aed9be4dc6456209c93e42214dea07ce2d2eba6a2f59f3a9bbd` |
| `tests/fixtures/pyrel-rules-coverage/rp3/int-arithmetic.orm.json` | `eaf10ef2dfe8a875e73d90c64f4e566be5a4a36d25854ea6ea278a92171ad60e` |
| `tests/fixtures/pyrel-rules-coverage/rp3/nested-beyond.orm.json` | `ee679d3a118a2eaeab704f93ea912e0c8378a25a3c1639a40f25fd1fb6621e5e` |
| `tests/fixtures/pyrel-rules-coverage/rp3/order-beyond.orm.json` | `79af57f7dd1d1cf82a57ed41471c9bef552f50f1acf8643da753bb1eea64b0a4` |
| `tests/fixtures/pyrel-rules-coverage/rp3/pass.population.json` | `86f49f990c7d5951f566f7bffb2c3810d2ec2bde1d53f18b6674ccd4133ebae4` |
| `tests/fixtures/pyrel-rules-coverage/rp3/range-beyond.orm.json` | `edaaa636d7cc2784afc46d9d27fd4bd332351d77313b54230326f995f6582e33` |
| `tests/fixtures/pyrel-rules-coverage/rp3/reference/empty.population.json` | `5dcdcebedb882943583c4c8291fd90832f73eaa611181e7877ff1356e8eaba3b` |
| `tests/fixtures/pyrel-rules-coverage/rp3/reference/model.orm.json` | `8900d383d92ebfda5a0a1570a3e85f30d1056a061e298173a5dfafb9b2f5eba5` |
| `tests/fixtures/pyrel-rules-coverage/rp3/reference/references/anchors.pop.json` | `ccb5aba04ba3505c5394b214dc293d326e7a9b0529919a2d6ee7c48b28845c6f` |
| `tests/fixtures/pyrel-rules-coverage/rp3/six-line.orm.json` | `d27c126262a79e01d7cc919c56749aef083a6d52d4eccc5b9697399608b98668` |
| `tests/fixtures/pyrel-rules-coverage/rp3/sum-compared.orm.json` | `7e01ba8ecc9fa2e7d324426a50e7f679d5234d26b8c0f3e3a4ef0e42fc029fc4` |
| `tests/fixtures/pyrel-rules-coverage/rp3/sum-into-number.orm.json` | `cc2882bd9140dfc2959c33c2ae61da5543ae10c072631966eddf476a50c987d9` |
| `tests/test_rp3_number.py` | `dd8f7422641d41839ded7d3d965c7a233156f7d60d8c35ebaea3a296e3221812` |
| `tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json` | `f00a0d53b9f7b4220143065540d33ffaa6c263b8284348504616d6adb2528860` |

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
