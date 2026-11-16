# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does LD3 correctly bind its six-stage reader, scoped coverage, exact replay, retained conflicts, and fidelity gate to observable controls?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Replay validates canonical evidence and the stage chain before payloads, then consumes authenticated retained responses without producer calls.
- C2. Methods recovery, coverage and stops, question completeness, revisit targeting, reading cost and the actual reported conflict are observable.
- C3. The stronger absence gate checks closure, scope, coverage and qualifying actual fidelity, while the opt-in assurance adapter keeps legacy scoring results.

## The change under review

The work from `13f05a5a` to the working tree at `92086a00f0a2`. Its diff is `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD3-r1/diff.patch` | `5dcd6f56c777a49506985b53c208e2ed6d1a7711ff7ff5d7e354ebc36cce492c` |
| `.gnd-planning/milestones/literature-depth/007-phase-LD3-spec-gate.md` | `30fbe5dfc0391a3c07375c53f7ce56dfc7b217d0b87ba67f773b5364ec52a3db` |
| `.gnd-planning/milestones/literature-depth/notes/phase-LD3-spec.md` | `e44f4a36bdd608911d75312b8948961c1aae3e361b2833a6974fc99df5ef741a` |
| `dev/components/COMPONENTS.md` | `e533993f02e7adc5a57aaf1d47b5c5262fa6ba48ebf72feabf57f18f4d8dde1d` |
| `dev/components/graph.md` | `92224fe7abdc45d4f31882e49401eb3f2cccd412a76e125e2d81967406bdf8ed` |
| `dev/components/modules/examples.md` | `c817b7e407d9d87116a7e29445dcb8a278665e809eec1e462e4ef7cc26e2520a` |
| `src/gnd/examples/literature/README.md` | `61efb4314926f5e08f092133c1474963b956872979d741d32f4e97007309539e` |
| `src/gnd/examples/literature/assurance_report.py` | `9dc14cdc728d027410c0bfdc1583ddf4ac77022bd1167b09241d4ab26e1cadbf` |
| `src/gnd/examples/literature/reading.py` | `d36355f9083d1dcdc4175a893ae24d218eb68611cf263cc18ed08780043f477b` |
| `src/gnd/examples/literature/reading_fixture/README.md` | `084da092cc4dca1054fc6bfe2af40849c2766e792a35a85733e0e507454a1909` |
| `src/gnd/examples/literature/reading_fixture/annex.txt` | `0b5cdb10ce08818ec6d6d62c90647af85312e36dbb945259df1e9f8e8f61b136` |
| `src/gnd/examples/literature/reading_fixture/calibration.json` | `fa8650ca52bc088bcf4557d05d0f02c31ba263649c7615092258a09c2d495e42` |
| `src/gnd/examples/literature/reading_fixture/closure.json` | `bc66c2876bdfc946163e9217d9f1bd4575f12b9a81bae3c2abb4dbb17e541b0a` |
| `src/gnd/examples/literature/reading_fixture/control.txt` | `e8f025c5f8d82f1cdf578dcf577c5782c5814ce84db871824159eddf7f8c8a1a` |
| `src/gnd/examples/literature/reading_fixture/gold.json` | `115493bdb990c9cfff7f67d08c43fe0ad9d90b45a5ee123ca562c2e865670394` |
| `src/gnd/examples/literature/reading_fixture/reading.orm.json` | `be7752ec6ce48e84a58d0c8f1406f1156a3c20bad05dc4a0c1db7e76da483739` |
| `src/gnd/examples/literature/reading_fixture/responses.json` | `f6f7e9c76ee6b23af0daf9e807efa8b6aeb03c21719fdf211adb39a10829ec10` |
| `src/gnd/examples/literature/reading_fixture/reviews.json` | `f1ebc75de190fb0cafdaf676881df2b037052b549878cf52601966f423abde07` |
| `src/gnd/examples/literature/reading_fixture/roster.json` | `0a7d9a271c0c5eadad8f997439eedcea2557c83d0fba7bb137050e971426f418` |
| `src/gnd/examples/literature/reading_fixture/scope.json` | `d9eba8d1dfb6adfd59adb584e9ae3184d53464b2cea14f7d3a1a3e31a7c2c41c` |
| `src/gnd/examples/literature/reading_fixture/study.txt` | `d334e308267a33d0b3e3f8811f5f1ed725f3f8d14b32c67287d50e5f0bcaf843` |
| `tests/fixtures/ld3-reading/README.md` | `bdffe9d3bf910e0d69cdc0f9fb6f11cd2659fbfe890d348f8d7f346fefd12128` |
| `tests/fixtures/ld3-reading/expected.json` | `7b12e90234e2c364f900c10ebfa50b454095b8ede4149498ddf26235fb234964` |
| `tests/test_ld3_reading_workflow.py` | `a72205ae9226a9ecf24b5ac57804ac019c67774f77c62260728fc71b794f911e` |
| `tests/test_li1_assurance_report.py` | `7b6643b6440198be8f0b19c23c8488f5fcdeeb0dd985b31978b0aeb1ee717611` |
| `.gnd-planning/milestones/literature-depth/006-phase-LD2.md` | `58004fd9ba0a6f4f1d220cb67f48f49e694c5cb6a58d5eb2fede3a7b092b1308` |
| `.gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md` | `216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539` |

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
