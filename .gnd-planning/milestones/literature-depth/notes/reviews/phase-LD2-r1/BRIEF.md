# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the LD2 selector, fixed-scale witness and tests establish the two triggered quantity requirements without changing unrelated anchor or witness contracts?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Time checking admits equivalent fs, ps and ns mentions and refuses wrong dimensions, partial unit spans, malformed quantities, and sub-femtosecond values.
- C2. Witness and independent replay bind the coefficient, scale and unit for 0.002 ps. Float and fractional Number retain their independent named refusal.
- C3. Selector model admission, scan work, occurrence ordering, anchors, and the exact RF6 inventory are exercised; predecessor compatibility stays under the existing guards.

## The change under review

The work from `cdb6b48b` to the working tree at `e0bf8feb10c3`. Its diff is `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD2-r1/diff.patch` | `0e4af7f96ea448a68404c31b9c180a1d78917d5d9752a21fb228c9561131e827` |
| `.gnd-planning/milestones/literature-depth/005-phase-LD2-spec-gate.md` | `031defa17d15d6cf45aa1a442ea1127af13e90d3d9fbbfa85f607ccfb5cbc55e` |
| `.gnd-planning/milestones/literature-depth/evidence/LD2/dynamic-query-successor.json` | `37c0ef7f89e70b889484d59cf95e0d28d93454119663bd158a1f2c9e5ebe495d` |
| `.gnd-planning/milestones/literature-depth/notes/phase-LD2-spec.md` | `95d352102ae8caad863e7189c47ac3f79bcd3496d9e4d5f9cde0c9e2ecfca350` |
| `dev/components/COMPONENTS.md` | `120f65a9139b834eaad2cfb0bb7aa501ff0f16bfc960619d5154df52e57fc04c` |
| `dev/components/modules/_root.md` | `925239848a19e4dce1f7ffb15784af7bab4dc1a0478308244f7e6aac5a4dd23b` |
| `dev/components/modules/model.md` | `151cd3d0658fbbc1f8ae22b24d3b2188c417f5a727e15a3ecd31a2acbbdb72ad` |
| `src/gnd/anchors.py` | `143bafe6c03f12f7e35c144adb57ea3ae1571d522fa97f28826980c12120b734` |
| `src/gnd/examples/literature/README.md` | `8fbb090c2032acae059c2241eb5be711f02f39f4bbcf57ef769b7699cad3a842` |
| `src/gnd/examples/literature/quantity_fixture/README.md` | `1ee7c035138158e40b0c3e2c347cbe119e5e13b1c721387a3ce54d2529150aed` |
| `src/gnd/examples/literature/quantity_fixture/source.txt` | `b6eb089cd29272137c65a57c40b76070c9e49e8ccd6bd423880c14f6c630db26` |
| `src/gnd/examples/literature/quantity_fixture/time.anchors.json` | `589c428990de044d2af80246a3177f4698b9b791a03e75c907de30df8def391d` |
| `src/gnd/examples/literature/quantity_fixture/time.orm.yaml` | `55f41279bae5ee1477d6f006690ac638c9b11dcc01825bdfa2e687967229bba8` |
| `src/gnd/examples/literature/quantity_fixture/time.population.json` | `c2a4bda7fe82b422146ae9bdf3076d4432388db595e4ed7081316627af20b568` |
| `src/gnd/examples/literature/quantity_fixture/time.targets.json` | `772629861f6408132d4b65f597d17d8f009fe0232a2892775ca718768adc1b16` |
| `src/gnd/model/_validation.py` | `43ca2fce79b694e6b5388145165a08c740d891bbe031316bb43a9838adc98901` |
| `src/gnd/schema/orm-meta.schema.json` | `0cab9e99afbc048afe328d57009062bb46932d8790688f3e4a8f27e75ef0cc62` |
| `src/gnd/skills/gnd-orm-core/references/constraint-reference.md` | `23b60f000b478b99e48b03bd1739e64a06582868c882917462f1b1f8e8dde615` |
| `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` | `0cab9e99afbc048afe328d57009062bb46932d8790688f3e4a8f27e75ef0cc62` |
| `tests/fixtures/ld2-quantities/README.md` | `0142470e66f2f9e759963855be3b6fb8ddea41d7b404647ad4461317e7329757` |
| `tests/fixtures/ld2-quantities/expected.json` | `e9d244adf0a8d550ce29ad4ca0d636fda59d356ddefb92ad05bf68b3fd2b4e75` |
| `tests/support/pyrel_application_successors.py` | `b6ecb642c24dd106760cc61330a8105c1ae8da73e01c469142ef214d650fa254` |
| `tests/test_ld2_quantities.py` | `3cc8a21b8215fbb8826a6bf3c10cccc3fac08ac3be3babccf7a42b6bfd52f1f1` |
| `.gnd-planning/milestones/literature-depth/004-phase-LD1.md` | `5a226ac70ee45cdd4893d6cc4d1ea505aeb9b76a04049dbc1b61382f71bafc69` |

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
