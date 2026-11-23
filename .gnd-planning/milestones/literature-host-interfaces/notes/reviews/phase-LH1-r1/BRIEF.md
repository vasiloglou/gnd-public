# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this change let a caller's producer drive the reading stages over a caller's root as the LH1 spec writes it, while the packaged runs keep their bytes, and what input does it get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. With no new argument and no profile.json, run() writes byte-identical packaged runs and test_ld3, test_ld4 and test_ld5 pass unedited.
- C2. Every refusal of a caller run (limits, profile, roster, model, step files, saved responses and reviews, retained-file bound) happens before the first producer call, and nothing is written when a run refuses.
- C3. Every value a producer or reviewer returns is validated as bounded plain JSON of the declared shape before the loop uses it, and no exception other than ExampleError or ArtifactError escapes run() for any such value.
- C4. The retained-file cap a caller run records is an upper bound on the size of every file the run writes, so its replay can read every file under that cap.
- C5. The per-document budget omits a section that does not fit and continues, and each source's stop reason follows the global stop rule applied to that source's own questions and sections.
- C6. Every limit is enforced at its ceiling and the work added is linear in the roster, the responses and the inputs.
- C7. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `c5fbaf58` to the working tree at `83de28465d1f`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/diff.patch` | `a915724b000c28ba2bf89edb14e48b4337df0da6486420475842d928ca829bb0` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH1-spec.md` | `b9e48c65cef90190afb05d7d262cbd06635b56a7fc58b238a612c309f236f25f` |
| `dev/components/COMPONENTS.md` | `8243162ca04ce32a39a90b79c62c9b243aae3d2280c1a600ed022b264e09e7cc` |
| `dev/components/graph.md` | `6cc5701a89bafc8373a069e4d39f73f23b758eb34eeba28182a0a9e8415f8df0` |
| `dev/components/modules/examples.md` | `cdf14eac67fd75aaa47938b6aa868540adf5028744b841d2d3d8c2a0ff33e117` |
| `src/gnd/examples/literature/depth.py` | `f50ff0cbd22f73cf151b5985eb207828111e0cbde06cd4213e7c9211b4a798f7` |
| `src/gnd/examples/literature/reading.py` | `4eb351ee3652f5d752af770cb7fbc7c353d5d6c734b60ccba068a721768aed34` |
| `src/gnd/examples/literature/reading_fixture/README.md` | `046790deff8f792fcbdd7c66b603d5d7383f241c92b4aa91e958c8f493e8dd90` |
| `tests/fixtures/lh1-reading/README.md` | `923e92b47281e653d8d41df799b6ad03fe59607330c542dec521174c4b3792cf` |
| `tests/fixtures/lh1-reading/caller/calibration.json` | `a0bb381686ad575c7b3a10dcd14005d9e62ebe1975de9d21b821886883df4e04` |
| `tests/fixtures/lh1-reading/caller/calibration.txt` | `5b6367e0cdb100c9faf97a38f3bce7886df514a9e23bf1636abe25fb74b71112` |
| `tests/fixtures/lh1-reading/caller/closure.json` | `20ae6dfc4679bfaf3ae7fd1f726d9a96e2849968e7073658fc84826ca04acb22` |
| `tests/fixtures/lh1-reading/caller/conflict.json` | `46a923bb87cd1551373429b3ec61105c1afbc23bd2acf17d7b958116578048ce` |
| `tests/fixtures/lh1-reading/caller/conflict.txt` | `67f82f8529a8a007b9c7ba3ea7a531ade2b047edb26e3d1f461a55a804680a04` |
| `tests/fixtures/lh1-reading/caller/gold.json` | `89c232e0c1feed38fbc5ad1d38b32ab0ffe21720d1b9b458996b8ecbe39ef3e8` |
| `tests/fixtures/lh1-reading/caller/profile-declared.json` | `7fc6bbf2c1bf1d14682d19fa87c19c6d485de029ca09a173e9339ccbf1eae730` |
| `tests/fixtures/lh1-reading/caller/profile.json` | `d24ffb2a621dc1d6b68df6832ee351700a68520338cd22c099714a679337640b` |
| `tests/fixtures/lh1-reading/caller/roster.json` | `98d97b789e6cff724354b256c41fd5ea1dc1896613a0dde61c4fb0965c3888ad` |
| `tests/fixtures/lh1-reading/caller/scope.json` | `577fa9b3988a3be340b7096b630cf974364d71fefdbfecee8eeb81cbe8df6f53` |
| `tests/fixtures/lh1-reading/caller/survey-a.txt` | `20f427b067c4e3959ba14393ab896b78168159fab115d8bc95bb33c9ee584bc7` |
| `tests/fixtures/lh1-reading/caller/survey-b.txt` | `e484782f1cd027c85a62cac452c35eff4c04643b82ad292e43000201ce7629e6` |
| `tests/fixtures/lh1-reading/caller/survey.orm.json` | `75048afed04a575f3bf1930e6aa63156c1fbf968fafa91ad36ecf0e4fafc319b` |
| `tests/fixtures/lh1-reading/caller/terms.orm.json` | `2cf8e537670f826622f7255079bcfa6bfedd6d960ca823180d91593add56c3e9` |
| `tests/test_lh1_reading_host.py` | `c5813c5f5a58c42e4559339e3aaa3400e4361c31d5ea2ae3000163c9869324d4` |

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
