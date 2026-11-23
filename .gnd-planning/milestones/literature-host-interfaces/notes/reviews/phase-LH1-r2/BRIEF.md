# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do these repairs resolve the four round-1 findings (in the retained review.md) without breaking what the LH1 spec requires, and what input do they still get wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The retained-file cap a caller run records is an upper bound on the size of every file the run writes, for any roster, profile, saved file and answer the run accepts.
- C2. No value a caller's files, producer or reviewer supply makes run() raise anything other than ExampleError or ArtifactError.
- C3. Every refusal that depends only on the caller's files happens before the first producer call.
- C4. Each source's stop reason follows the global stop rule applied to the required questions whose own section belongs to that source.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `83de2846` to the working tree at `72439fa0db62`. Its diff is `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r2/diff.patch`.
- new: .gnd-planning/milestones/literature-host-interfaces/notes/phase-LH2-spec.md (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r2/diff.patch` | `a935e81658c0d708d198f69ad06064edfbee1b6fc1b79be159f8dc431b1dd1d2` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/BRIEF.md` | `23b9adb2b2216593c2691831b79a60e2859c28019faec563675733b0b7603ba6` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/FINDINGS.md` | `ac9b4f12c47d966b651df467dd710c4a4642b5abbaa757635595cc467f7519ec` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/brief.json` | `df9a1bf7c1edf737e6918e8fa7258be46c5317546965b6c513f3aad22f6194ab` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/diff.patch` | `a915724b000c28ba2bf89edb14e48b4337df0da6486420475842d928ca829bb0` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/review.log` | `4fdd52fbf71c878354212782a89daa2622e2634c78c3e377e4a280fbec0d94b8` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/review.md` | `402e117938f29a690a0b415442adc31ee11248714815cd53a35fc8fee70ab4e8` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/reviews/phase-LH1-r1/run.json` | `df4daa409268db6d5322cd3045d679c61a38b4d16d4ff032911b095c613e8019` |
| `src/gnd/examples/literature/reading.py` | `e6b06c18fbb39cf3c65c9a8c138d79c7de2bb9dd458a294b1bc83c9b55480a3e` |
| `tests/test_lh1_reading_host.py` | `d93a340ed5268a4d5eabba373ca14c7d77a8fe9bf718cd5ba71ed7a21556d46a` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH2-spec.md` | `53f533d1e3aa605e279a76381f27ae9b25a203595474a6c16997e9303403222c` |
| `.gnd-planning/milestones/literature-host-interfaces/notes/phase-LH1-spec.md` | `b9e48c65cef90190afb05d7d262cbd06635b56a7fc58b238a612c309f236f25f` |

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
