# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the IR2 diff add gnd flatten so that it writes exactly flatten_model's two files for any include root, both or neither and never over an existing file, refuse every invalid input with the stated exit, and leave every other command and every include-free model's output unchanged?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. IR2-C1: gnd flatten checking.orm.json --out DIR exits 0 and writes bytes equal to flatten_model's; the record names origins and the temporal rule survives
- C2. IR2-C2: gnd check verdicts over checking.orm.flat.orm.json in the root's directory equal those over the root
- C3. IR2-C3: a model without includes, an unpinned include edit, a nested include and an orphan attachment each exit 3 with their code
- C4. IR2-C4: an existing flat file or record exits 11 and nothing is written or changed; a failure after the first link leaves neither file
- C5. IR2-C5: gnd extract on a temporal include root exits 3 and names gnd flatten; include-free temporal models keep the historical message byte for byte
- C6. The seven inventory changes in spec finding i1 are each required and none weakens its guard; the CLI successor is independent of src/gnd/commands/flatten.py
- C7. Rule 2: flatten of a root with 1,000 extra object types finishes in under 5 s

## The change under review

The work from `68e426ca` to the working tree at `68e426ca7d70` with uncommitted changes. Its diff is `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: src/gnd/commands/flatten.py (not tracked yet, so not in the diff: read it whole)
- new: src/gnd/extract/flatten_service.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/diff.patch` | `bcf4216c5af8d3e2411bf091d42df941b8f1b2c894e24d2c80ecf5dbaadee4ef` |
| `.gnd-planning/milestones/include-root-routes/notes/phase-IR2-spec.md` | `749290be35f5754e4d2a24a4388605c38c73e0aa1f91fb57c39ab6a91587f1c8` |
| `docs/reference/cli.md` | `6bb30df308c2c84315376879401952a6a662625f2df4b6da979ddea2d8a0ac7b` |
| `docs/reference/disclosure.md` | `4852e4bfd3efa88d5455eab08d56a57a904a48bd059505bf66c1c23a5c6cae24` |
| `docs/release-notes.md` | `225bcbb24dededc28984941f05edd4db30e63dadeee87ebf34141ee1922c565a` |
| `src/gnd/cli.py` | `9f5e190daef5d07361073ed2e1bc25c3ec33846f75ba7f78dc2ca7840cfad751` |
| `src/gnd/disclosure.py` | `5ea62af945857f5855ae0e9845d6a37818fb7d8e0a9d4c892af82e70ed8118e8` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `24b8217eea2d3ba2f13af7045f35f784dc80944aa8cd9d23a51f8a12fa005213` |
| `src/gnd/terms.py` | `465c58e6a9fc104ad8ee5cf27915c3c76ed750671d10c610060812c097997199` |
| `tests/test_disclosure_mode.py` | `6fe735ce4ed9a26067759f6d89ac9c31ce17f5cebf905b51a04db6f69d40542b` |
| `tests/test_rf1_cli_pins.py` | `da90bcd9fb4c9289d13b3d96595fdc791512c7eb9e4818e6a14fda56531580f0` |
| `tests/test_rf5_commands.py` | `fc25498ecc257eb2002aa033d5a91ca2fc60f328cddd7efa421833911bc71845` |
| `tools/gnd_arch.py` | `324efc879a64e5c93f64bcdadf3c7cee935f5c4740dca2e042d8dc3d83af43dd` |
| `tools/gnd_entrypoints.json` | `fe1688657c16135e8d0af32aa71c9a0f93adab447e75687c7828dc8074b4b6b0` |
| `tools/gnd_layers.json` | `c87fb1d297423b91f410bce463e2e7443c3a65834158b5ad85220f91392fa692` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `src/gnd/commands/flatten.py` | `2001fc46743f6f288a023c254c8e463b30686c3805455c37340fbdb0525a8f45` |
| `src/gnd/extract/flatten_service.py` | `681d5f18e77884d0c4195a017d92bbc4ade43988b4a3f03b31c9fac802c85275` |

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
