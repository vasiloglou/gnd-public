# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can the owner publish exactly the accepted 0.4.0 artifacts and reproduce the prepared documentation update using this dossier? Find any missing or unsafe steps and compare the retained evidence. This is a read-only review; do not execute the publication snippets.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The accepted source, profile, attached artifact hashes and owner checks match RV2.
- C2. The scratch patch addresses the residual and receipts warnings, with no publication action.

## The change under review

The work from `6f949db4` to the working tree at `6f949db4f4cb`. Its diff is `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV3-r1/diff.patch`.
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/contributor-realpaths.txt (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/dossier.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/github-release-notes.md (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/post-publication-supplement.patch (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/pre-publication-state.txt (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/scratch-verification.txt (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/release-0.4.0/evidence/RV3/tool-only-preview.txt (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/release-0.4.0/notes/reviews/phase-RV3-r1/diff.patch` | `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/contributor-realpaths.txt` | `b08c3140bfc6316a5666864697c95e33c6744ee5b7b2b3bd17ceca046136f5c3` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/dossier.md` | `8441eef249398db6577c51a443e484bcbfc841442031d0ea6c79913f6d4d86fb` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/github-release-notes.md` | `e564c35bebdd4a4dbc5620baa565487003c069c4585b471c7b0f9c9f88800adf` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/post-publication-supplement.patch` | `e9b4f82ff62d6b3f1ee0a072d9be3cb16ce341fd8148bc60ba664f8cc4b8ae1d` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/pre-publication-state.txt` | `be7ffc8860575ee073171fe76314155a75a9d79b8131a8911460d9baf162fedd` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/scratch-verification.txt` | `a4ef390a3d263dc3ded35e81328339ddf731f284986093d3c5736e34428b8a2a` |
| `.gnd-planning/milestones/release-0.4.0/evidence/RV3/tool-only-preview.txt` | `1bce92039f9f2a1e5d84d959410548d7c9939a6547b541fe07d2451aa6cc47d0` |
| `.gnd-planning/milestones/release-0.4.0/notes/phase-RV3-spec.md` | `476fdfb125d805fb9e47102c9a1e4db2a32e9cd1f62995b2a16b2002397fdb51` |
| `.gnd-planning/milestones/release-0.4.0/008-phase-RV2.md` | `361ccfce855668c338f667dcf6206a8b9a73b879bf3c1514b77c25ae12a6cc04` |

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
