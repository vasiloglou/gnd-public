# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the RP3 diff type GND's Number like Float in both rules programs with GND's admission rule, and refuse by name every integer beyond 2**53 that a binary float would hold inexactly, in population cells, rosters, plan bindings and the model's own constants, without changing the verdict on any input it accepts?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. RP3-C1: #214's six-line model and depth_fixture/decimal.orm.json export under both targets
- C2. RP3-C2: the DuckDB program agrees with gnd check on the decimal population and the six-line pass and duplicate populations; a boolean in a Number role is refused, exit 3, by both
- C3. RP3-C3: arithmetic on a Number value in a derivation is refused by name, as on Float
- C4. RP3-C4/D6: an integer beyond 2**53 in a Number or Float cell is refused with exit 3 by name; 2**53 itself is admitted
- C5. RP3-C5: a model whose allowed values, range bounds or comparison literals hold such an integer in a Number or Float context is refused at export, exit 3
- C6. RP1's deferred review finding (two Float anchors beyond 2**53 merging) is closed by the same refusal
- C7. The comparator's numeric canonicalisation (an integral float equals its integer) is GND's identity and hides no real disagreement

## The change under review

The work from `6b9dc077` to the working tree at `6b9dc0776074` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json (not tracked yet, so not in the diff: read it whole)
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
- new: tests/test_rp3_number.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP3-r1/diff.patch` | `ff4a4b2fe0ede74ae25c8919fd51d152ce56207f2324a8e72d2390b7d5698037` |
| `docs/runtimes/pyrel.md` | `a76ce7354ca28253e60c6a68ff04fb681d4b1f96bfc9098772a8cc26bac4e747` |
| `src/gnd/export/pyrel_rules.py` | `6b77908f23a619089d9f24bc66f45a2e98394b8f46fd6f45853e4a77e87df489` |
| `tests/test_pyrel_rules.py` | `bcc7a1c457a0fd943edbda94e5952c8bdc99ca2ccc06d535af17684f8791eeb8` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r1/review.log` | `61b8189d5c3f37a4536085e0f9d30f09b9fa1849c3981f47e659bb26ed802b07` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r2/review.log` | `d0e90ec94c66fccf5adbf073dd259d5861ac05e98cdfddc8f541ac04242033f8` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP1-r3/review.log` | `05bc3b2eb8c9636dde3db8d5b71a5ba51b59ce06700c4cbc686dcff7c7fe1f45` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/review.log` | `c2bf65c347c1197196e91a95d0bbec8e1b7ed9565d8ddf94b0da0392a58e96e3` |
| `tests/fixtures/pyrel-rules-coverage/rp3/allowed-beyond.orm.json` | `2575c355fe4ccd2f83bc2476423300bbf5327a06eeed0639e24c174c437563c8` |
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
| `tests/test_rp3_number.py` | `0fff60e13a90d9a2c58d31c970304771d48f1bf49fb8df59576110a7968f5b98` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP3-spec.md` | `19564054fe0ac09eca659f0247500328db655ed8021e8dc3e4acfa8f8d2160dd` |
| `tests/fixtures/pyrel-rules-coverage/rp3/anchor-beyond.population.json` | `f00a0d53b9f7b4220143065540d33ffaa6c263b8284348504616d6adb2528860` |
| `tests/fixtures/pyrel-rules-coverage/rp1/numeric-anchor.orm.json` | `b3eddc57affb401533190862e74a6a6149ffb48f5b17e9e596aac81bd30b37da` |

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
