# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff let only a seeded root that truly owns nothing skip the document requirement, let its first round declare the document, and keep every included element and every pin out of a growth round's reach?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. D4 (a): U1 omits the documents issue only when the composed root declares at least one include and nothing of its own in any section; every other unattended model keeps U1 exactly as before.
- C2. VG4-C1 and C3: a seeded root's first round declares its first document and adds owned elements and an attached constraint; preview, apply and finalize exit 0 and the result validates.
- C3. D6: repin-include on an unattended root is refused under every policy, before the policy runs; a root without the mode is answered as before.
- C4. R0.6: an operation that modifies, renames or deletes an included element is refused.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `b50593b2` to the working tree at `002dc86e964b`. Its diff is `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/diff.patch` | `4c2b80603f709d514f0cac1d39354f14473f24075f16baa9334d99d044023994` |
| `dev/components/modules/evolve.md` | `f2ca5da4ef4224911369c632d0f520a95f5b7a1f913687c285cde3ba293d87eb` |
| `dev/components/modules/model.md` | `6258ba4298a2a119633bc0b634c790115a0bdf188c4f03b526966387f0c972cb` |
| `docs/release-notes.md` | `cd87a6a42375d7f3035350d42045106e4599241e09a7d0a74944262d9d4b1168` |
| `src/gnd/evolve/_includes.py` | `b0f939fa57c9927a647ade7aa75c914e700b9cee0da45fb32533c430eb5efb5d` |
| `src/gnd/evolve/service.py` | `3e1c4e9923ab8f48deae954098a4d2b0de9058703f5aece2c99ed00313a09531` |
| `src/gnd/model/_unattended.py` | `764fc94ef912d9bc230e4b3f062cfe181608dd2a29f5319b8d5dbf3d24ace51f` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `f67c07c4084f8874d01030dff7964e78c7918e7f0f2995386af72585b29722be` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `939e9ef2d429bdde040001bbd301ee8abbb36badf6a89d15fe77531d8f72e02c` |
| `tests/test_vg4_seeded_growth_rounds.py` | `75cbb0dc7c4f5bc4bda922365b3ce6c3df70412906f163441275878e78f993e9` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG4-spec.md` | `05022d341219cd2a8d262f2f732df2f6abc96cc25b07224443ed07fda6043d90` |

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
