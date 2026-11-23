# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the packaged example run exactly as its README and the growth page say, and does every page and reply state only what VG1 to VG4 shipped?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. VG5-C1: the example's proposals and judgment inputs rebuild byte-identically, and both rounds preview and apply with exit 0.
- C2. VG5-C2: the grown root passes gnd validate with both documents and --require-documents, gnd check over population.json, and gnd judgments check with the shipped policy and receipts, each exit 0.
- C3. VG5-C3: the include route list names every route that resolves an include root, gnd coverage and gnd evolve included.
- C4. The growth page's new section, the README and the three drafted replies state no rule or behaviour the code and the normative homes do not hold.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `5265f476` to the working tree at `b36b446daa3b`. Its diff is `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG5-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG5-r1/diff.patch` | `971502b5a6b9bc966630b0fd9c5e064317051320fdb4c811ea862cae4ff1e236` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/005-phase-VG4.md` | `c70a1c5d3fcec4c0c48e2ea41cd91e3df1a325f1a48986c8f1dffdfd353c35b3` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/README.md` | `1dff614aa1572fecb5972053e3aa1e1bd22250e1f9defed4f31301e0f6721114` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/issue-replies.md` | `972f2af3dd59fe786220296a247569ab72237510085a9fcf83ae72f2ba612044` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG4-spec.md` | `a54cdea8aace7b060159bcf33b20a48791e61dccf3da284b154bd6adc1e9f847` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/BRIEF.md` | `96e79d60f7ae41c141153883bb7d8e1f2fdddcaa2332318e93b27d2355a664ca` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/FINDINGS.md` | `b818ed63f51df43c0f2ffd242f4043b1ff15e06fd1b20e71596cc9fcc59d8bda` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/brief.json` | `ba3fb0d0acd18cda25136c268e4ddbb73770d41ce5e7343202f2095a05a2b958` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/diff.patch` | `4c2b80603f709d514f0cac1d39354f14473f24075f16baa9334d99d044023994` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/review.log` | `28190a497dee7b37452778a7eb1c5565b352510f8dbee31863bf4dad2c7502c2` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/review.md` | `c0d19198b87fdc71e65118072ec7d73860779d25f268188f563cb1bd1761ba93` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG4-r1/run.json` | `c1d0518c0d50eb850a3f7c5b7b582387487685f30b63bf257391fff3b572a82e` |
| `dev/components/modules/tools.md` | `d16bacb65023ebcccf9c501fee909522c2425ef44d5f839d116d59c3faabc930` |
| `docs/agents/evolve.md` | `f34f04039b56321a841c2e52c2f5e2c852c801b07f3cc538c91c3546322c5486` |
| `docs/agents/model-from-text.md` | `9932f7158d5669ef991df0b8ecc49e7150aafe1b02cc251e570e39a84fe4dbef` |
| `docs/release-notes.md` | `4597ed0f3ff17508bad97cea1240b879ab455817dea8377b3894ef677b92f4c0` |
| `src/gnd/examples/seeded_growth/README.md` | `43aa2f437b0e8a977a51f229781a5dd4f40c29f4e14f0794e5265368ed24c35e` |
| `src/gnd/examples/seeded_growth/policy.json` | `398aed89d9c2a02555489b1f6dfe8667bf262ee96f3d4a78d7d5c2cb36c184e8` |
| `src/gnd/examples/seeded_growth/population.json` | `9f481316d8e86d297b1ba00505fae57e3274d531c9ab2d56f102e9a81ef77ad7` |
| `src/gnd/examples/seeded_growth/receipts.json` | `8b10f217faa3f0e7e4375275a3c67b33e89e5d125038c1d48ea7704294feb360` |
| `src/gnd/examples/seeded_growth/root.orm.yaml` | `5bc77662bebc77c7dbd2ccb7dbf712f21add117d4b4787547da1e026a24a147f` |
| `src/gnd/examples/seeded_growth/round-1.document.txt` | `865f165cf4ebd95adbe10e8b18753c8be981df6558c18f6b18a991b25731d5b9` |
| `src/gnd/examples/seeded_growth/round-1.proposal.json` | `2ca250e77a941120c7e655e6bdf570ee25da91bedba9c536f08f5217e9e5246a` |
| `src/gnd/examples/seeded_growth/round-2.document.txt` | `6ed65c19e20d68329fa38de5632cf1093ba6d2b1f60c848ab33f1aa75e167d23` |
| `src/gnd/examples/seeded_growth/round-2.proposal.json` | `a962864bbe733754e24ab1933c8ab17e26f9ede63fef868058b88f8c0c976d56` |
| `src/gnd/examples/seeded_growth/seed.orm.yaml` | `69c31805fc53de4c2b6717bb10c00ecda1b4e8a523661ffc27428c8e5dc82457` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `3356dd23dae636f79c531d5e372719769e5c7cc7fc834afaaab7a13265832c06` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `7f1bed577edf597776e2110b26123cf6a54606d459925aadb0cc4a055e090282` |
| `tests/test_mc1_guards.py` | `77e89fbb24d01957631757ed2641c83d514df74e93e8d2332035e764c88adc92` |
| `tests/test_packaged_skills.py` | `5edc769a7e68cbfd520ee61e72549d774acd7464140cfae0b6fe88de7aec6409` |
| `tests/test_vg5_seeded_growth_example.py` | `6599886abd32161e8dd2e402b421c4c2a273b76815ebce5f2bacf83738bb3fdb` |
| `tools/build_seeded_growth_example.py` | `6ca03d5a5051ab77fbdd9c188f995a0876b22a7c79415b5b2c23064405efa397` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG5-spec.md` | `dde225e07de8faaf4931f0c72645b68534024d0c68eb4c6da6e9c6ee9753bec0` |

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
