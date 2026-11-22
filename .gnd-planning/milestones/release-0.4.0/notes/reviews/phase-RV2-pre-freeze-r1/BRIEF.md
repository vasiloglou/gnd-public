# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Which 0.4.0 acceptance probes could pass despite an absent or broken feature, or fail on a valid installed candidate? Review code and its available fixture evidence without building release artifacts.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Both retained candidate wheels exercise the five probes and their behavior and hash-pinned 0.3.0 controls.
- C2. Candidate code only runs from the isolated wheel, and the former positive regressions remain enforced.
- C3. Each expected result is discriminating, and all gate evidence can follow the actual owner-merged commit.

## The change under review

The work from `835ead3d` to the working tree at `835ead3ddedb` with uncommitted changes. Its diff is `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV2-pre-freeze-r1/diff.patch` | `e69d81aae7d052ce4dd99ed153ce99c6767efe0debc9a359e28a25c89521842f` |
| `tests/test_release_acceptance.py` | `377dce0fbd6927bf2b57e9afcec98ef78e8a1de8e5c4cfa8aca0cc73a348ab90` |
| `.gnd-planning/milestones/release-0.4.0/notes/phase-RV2-spec.md` | `e0f186ce11f517cffce99aea21e388300d29b0f921c009ae84e10fe2afa5b8c0` |

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
