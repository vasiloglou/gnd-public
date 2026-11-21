# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the IR3 diff make gnd export pyrel, in the default mode and under --rules duckdb and --rules lqp, export an include root through exactly its flat model and record the flattening, refuse every include problem with exit 3, and leave every program exported from a model without includes byte-identical?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. IR3-C1: the default export of extraction.orm.json exits 0 and equals its flat model's program except the two constants and MODEL_NAME
- C2. IR3-C2: the default export of the temporal checking.orm.json exits 3 with the temporal message, not an include refusal
- C3. IR3-C3: under both --rules modes each interop root gives its flat model's exit and message (anchored, exit 3, at 260c4337)
- C4. IR3-C4/C5: FLATTENING_RECORD_SHA256 equals the sha256 of flatten_model's record bytes and MODEL_INCLUDES the root's pins, in all three modes; a re-pinned include changes both
- C5. IR3-C6: programs from models without includes are byte-identical to the base 68e426ca in all three modes (T6 goldens), and pyrel_runtime.py, which every default program embeds, is unchanged
- C6. IR3-C7: a stale pin, nested include, non-list includes, escaping path or absent include exits 3 with its include code in every mode, never 70
- C7. Rule 3: composition precedes temporal classification (rewritten test_R7); no import cycle and no new dynamic query

## The change under review

The work from `1c5c0f66` to the working tree at `1c5c0f66f1fe` with uncommitted changes. Its diff is `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: src/gnd/export/include_roots.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/diff.patch` | `463ea707ffb06b3791b7dcb32b880f0aa002653b743c1da37582277cac985829` |
| `.gnd-planning/milestones/include-root-routes/notes/phase-IR3-spec.md` | `ab11dc7c39c5b141569f512cba54c764399a0f93057b6a51d8e039538b141e7d` |
| `docs/release-notes.md` | `fa07685dcf3e668da055e8ea02c0336883f19cdda0514e698b4c52599e6cd3e6` |
| `docs/runtimes/pyrel.md` | `ec5ab52d556ba6edd4171d366b1152c449b294f69ed75ae821ceac0f46d6fca2` |
| `src/gnd/export/emit.py` | `3a6a6eb9033fa199f11f2b2dc626d33226a110d5b76b2b3c5f081e29841cec2e` |
| `src/gnd/export/pyrel_rules.py` | `27c51fe372df1b3d8971ce80b87ccb7b29458ec20cc55c6f43b47889e0942d69` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `465e02c40da27c89e46d1d6e7a3959dc69ec531055e69f7351fad0400dff80bc` |
| `tests/test_ir3_pyrel_includes.py` | `86066413bd8b971c3596c5baf29b5af6e0e5e27ab3635e681ce90a040e46361b` |
| `tools/gnd_layers.json` | `b9bf5421a5b07a27665bc1f6e4ce0c155532ad154be758cf1d6cb85dd95e7763` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `src/gnd/export/include_roots.py` | `5179d0901c919c596fcc52d0e1cd083ae15ba5e913f6cedc21467527112d5aca` |

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
