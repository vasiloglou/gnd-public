# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the IR1 diff make gnd judgments check judge a version-5 include root as gnd check composes it, while leaving every model without includes or attachments byte-identical, and does each declared branch have a test that fails if the branch is wrong?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. IR1-C1: the temporal interop root checking.orm.json judges with exit 0, error null, admission true
- C2. IR1-C2: extraction.orm.json judged directly and through its flat model gives equal targets and admission
- C3. IR1-C3: an unpinned include edit refuses include:hash-mismatch; an edited and re-pinned include makes receipts stale (stale judgment subject)
- C4. IR1-C4 and C9: a nested include refuses include:forbidden-section; an orphan fact_type_constraints document refuses include:declaration
- C5. IR1-C5: every include refusal report validates against judgment.schema.json (reason binding, code in message)
- C6. IR1-C6: test_R4_judgments and test_R10_session_judgments still pin the refusal for callers without model_root
- C7. IR1-C7: a model with neither includes nor fact_type_constraints gives a byte-identical judgments report to 1e419a88
- C8. IR1-C8: an include root whose reference file lives only under --reference-root judges with exit 0
- C9. Rule 2: T9 bounds the composition layer IR1 adds; the checker's superlinear cost is pre-existing and outside this diff

## The change under review

The work from `1e419a88` to the working tree at `1e419a881eb6` with uncommitted changes. Its diff is `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/diff.patch` | `86ad785e79384425e88e8118166b6b866998cb100fd2bf0379f5c79721c6d309` |
| `.gnd-planning/milestones/include-root-routes/notes/phase-IR1-spec.md` | `c99b72b98e53b82b4dd9c0d0613f413e0ce5f8d404f356074e4927da5ff70e43` |
| `docs/reference/cli.md` | `fd799385b717972b1763924702d825105a07f266ff318ce27e8edb7b62f7b3bf` |
| `docs/release-notes.md` | `606c73ee6c8249c6df153331b63f3add83afac653f4c4d688d764710cbb38ad2` |
| `src/gnd/api.py` | `076cc0564777fe406dde066973e9b7b541ceef2c6707432eb7bb468a05ca226c` |
| `src/gnd/judgments.py` | `05940960e391335c055cb34cc55914aa60e5597189856eb557e40a711f52b2f9` |
| `src/gnd/model/__init__.py` | `f8a6c6f1bb24194efe17d2fd1f9f33662716581aa3245a9d006762c21883b90d` |
| `src/gnd/model/_includes.py` | `4d68c5f7cff284b3a9c60bb79d006bbe116f29163c29f340e8c008fc26b16122` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `7774abfd669b09fbc975dc734d305e724a081e1a1d3b433e59162de81dbe7d3a` |
| `tests/test_ir1_judgments_includes.py` | `57bf5c700f736140853986662ead467fd94abdf4715aaad9e2c6b44cc2a8f06b` |

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
