# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff admit exactly the new constraints the growth document tells a host to write, and refuse every other sample or common-sense constraint, without changing any other D-12 answer?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. VG2-C1: a proposal built as unattended-growth.md describes, with one sample and one common-sense constraint, proposed and deontic, previews and applies, exit 0.
- C2. VG2-C2: a new sample or common-sense constraint that is confirmed or alethic exits 3 with the named D-12 refusal, on any model.
- C3. No D-12 answer other than the eight sample and common-sense rows changes; a changed constraint is judged as before.
- C4. VG2-C3: the D-12 home, the evolution contract and the growth document state the same admitted combinations.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `11ca75b0` to the working tree at `b2ce8bb02f85`. Its diff is `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG2-r1/diff.patch` | `e80a379fbaa9b78604023b65dfd0460f72fd78a8410fde77113f051c67ed4cc2` |
| `dev/components/modules/evolve.md` | `d195b6f249725e9a3eac51e6c006d943aa0bcf7a35f62281a3bb95b82664574c` |
| `docs/release-notes.md` | `ab1849524cb73d0edd650ad89f16b3ee679de6e31a408226b366905498dcc72e` |
| `src/gnd/evolve/service.py` | `404cd6b224937484106d394660de188d0eb4ad60ffd83e50d2fcf9a8d5520f5e` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `fc234d62acc1cd49015baa2afe9ac800e9467496a48e8a51327e18cbf68fc8eb` |
| `src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md` | `e3eb7ecae2c404f7b123389a115d889f0486d448db666760b7c93260fe7108df` |
| `tests/test_induced_provenance.py` | `8e7b07e51614235f58c17ced3bb4fa85d2bab678326cde8c63d7ad543096b8f3` |
| `tests/test_vg2_evolve_sources.py` | `afbd0338b526a982ede4599535670e4b52bbdcebf81859beadf7dd7172052262` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG2-spec.md` | `ddb0f24913d1cbf5b942fb7c341e2bc9ad261cb9cfef10f62f27f4b34dc5cb4d` |

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
