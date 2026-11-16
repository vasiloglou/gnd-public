# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does LD5 enforce independent support verdicts on the published derived claim and require the right revalidation when evidence or its predicate changes?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The independently pinned saved opinion document is bounded and read before candidate evidence. A shared claim, sense decision, rule, definition or interpretation change requires revalidation.
- C2. A changed support occurrence, review, witness, rule or resolution edition invalidates that support independently. An independently valid peer remains available.
- C3. The verified fixture reports two approvals, one approval after rejection, zero approvals, stale previous opinions in the revised edition, and a re-reviewed proof for the same occurrence.
- C4. The replacement proof is independently replayed with exact authenticated LD4 evolution, model, review and edition inputs, and the retained report can be replayed without publishing a new opinion.

## The change under review

The work from `4e0b542f` to the working tree at `2e34530a1bf2`. Its diff is `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD5-r1/diff.patch` | `baa6606b5d26a9f600f2d5ca597080a417fa020278459258b420672cb63dfa2b` |
| `.gnd-planning/milestones/literature-depth/012-phase-LD5-spec-gate.md` | `8e990c62c07b7d31da976b40f06fbcb457070566cd4de5eeb7b9e9df72f9de03` |
| `.gnd-planning/milestones/literature-depth/notes/phase-LD5-spec.md` | `44022b8fa8cba692a5fabcad02dbdcc7a854bbb04cba21dbcc1894613db3d83c` |
| `dev/components/COMPONENTS.md` | `df3821abac6ed7b57bacfe83916df3226d5e6eec8285294652e4320008f25a77` |
| `dev/components/graph.md` | `2e8db5ce8f2fcfb7ce30dc33067301cb8b443bac0b274b1fa1391edc009c5601` |
| `dev/components/modules/examples.md` | `cdf290c0a100d68babfe7feaaed7151d8de129a4f1a31199877da1f20d98f1f6` |
| `src/gnd/examples/literature/README.md` | `7a9a25b51b441a2ab30f2211972f2be75898d19a71ad8054b81fe7310fe9f258` |
| `src/gnd/examples/literature/revision.py` | `d87d6c64e0b9c694831c8e8bd49433e14f10f03a044f2e834f989f1b558cb359` |
| `src/gnd/examples/literature/verdict.py` | `e4a654f9f2751a98e36b03b3438a1d59f394db817b62f6718ad0629119b2e246` |
| `src/gnd/examples/literature/verdict_fixture/README.md` | `6b19454adfc6d98a277c54cb67833d3ed81684ac0f0a287725c305a6a934fd1e` |
| `src/gnd/examples/literature/verdict_fixture/opinions.json` | `096613fa54def036cdeb4c85d137ec84fcfa1fae7b500bd080e56b01824276f2` |
| `tests/fixtures/ld5-verdict/expected.json` | `d7323c9cc5ffcea22768e984e434d683c0b79ab76e7118ce9801549dab8a314a` |
| `tests/test_ld5_verdict.py` | `c309a8ce3cf4110f7c9efbc95cd40ee3a04688672e719951bf2281b905fa72ea` |
| `.gnd-planning/milestones/literature-depth/011-phase-LD4.md` | `e108270204a5e5817e98c14b720f9a9a5aa835816a33e6c365553c6bebe48a75` |
| `.gnd-planning/milestones/literature-depth/notes/literature-depth-plan.md` | `216c7af0576a65a5fcb785773d34449c0e6ce0ce05ab022a21a43e5607d20539` |
| `.gnd-planning/milestones/literature-depth/evidence/LD4/installed-observation.json` | `06227fb624d738f2719b4d01c77f9b3a85c37b4ab910fc5e70e6265b27547b7a` |
| `src/gnd/examples/literature/revision_manifest.py` | `9ca7699f78a1886dfed25ce64fb3299b21d7889b2a2e668f3ea338f95d4c603a` |
| `src/gnd/examples/literature/revision_fixture/release-policy.json` | `af44dfee16ca94f20c560c5e82bb00e59bb86f53c53c7219b30fb6da3ad8bc65` |
| `src/gnd/examples/literature/revision_fixture/review-inputs.json` | `860de5eaab0da246bec9871ae0b8094ef8d1507ee487724f0d7d1e0b925b1a47` |
| `tests/test_ld4_revision.py` | `60061d3a9179c6baa4559714824c9d7a0d94690b86f22bf9536a359d35b128c3` |

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
