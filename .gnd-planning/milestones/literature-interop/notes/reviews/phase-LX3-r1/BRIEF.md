# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where can catalog-backed composition or replay accept stale evidence, misattribute a proof occurrence or source coordinate, compute a candidate-only result, or break a prior wire contract?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. LX3.a: Compose renames a candidate alias onto a fixed catalog key, keeps catalog rows outside candidate artifacts and source lineage, and composed checking evaluates the authenticated catalog with the candidate once. Reference-free composition bytes stay compatible.
- C2. LX3.b: Catalog key conflict, candidate dependence, expired pins, forged catalog roster and modified candidate evidence refuse in the specified order and exit bands. LI2 checks candidate cross-source joins and explicit overrides remain refused.
- C3. LX3.c: The replay kernel checks model origin, candidate lineage, catalog binding and candidate/reference occurrence origin independently. The closed schemas and version fences admit only the matching certificate shape.

## The change under review

The work from `6d2ecece` to the working tree at `28dc21b75c42`. Its diff is `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX3-r1/diff.patch` | `075a371d811ba60ee5e58f8fbfbdb9dd6cb27ab473c41bbd08d63d561bda6e89` |
| `.gnd-planning/milestones/literature-interop/008-phase-LX3-spec-gate.md` | `aeaad3e30f5625a5d7e4d9cb71cd07ed76abfd31e96809abe39fa2bc59295bfe` |
| `.gnd-planning/milestones/literature-interop/evidence/LX3/dynamic-query-successor.json` | `0c6ae733681b978f8f7206e3edc032f4203a90886e979acf2ad62cbaf6888330` |
| `.gnd-planning/milestones/literature-interop/notes/phase-LX3-spec.md` | `21ca75acc3ab70f65d7eb6a20b69aa1dd817194e3b046f1cfcc84f87790c12a3` |
| `dev/components/COMPONENTS.md` | `346fa94477e525683aabd5ad06c151e80d3b5d0ef1f124f25804a4fd00e75ac1` |
| `dev/components/graph.md` | `3a9e5c0b48fc20a1a79baa792260874e03bc2f9e983469d6529c299a808b6613` |
| `dev/components/modules/_root.md` | `68cd4b61b5691dc6269cb43df133af1c9f539b13854b0afbc82f3213dc12e1a1` |
| `dev/components/modules/checker.md` | `fe2c315ef7a78520861fde130d2af654646d38c98558501815e8122b9f6d90f2` |
| `dev/components/modules/model.md` | `86aa34208e67379527aa06b6de18d2ef8b66600b663adf5eff8bfd378e6c08a3` |
| `dev/components/modules/witness.md` | `6da5af6b9b9918c1c91ec7d837a9e077f9e36fef5f882684c3cfdb5416c44ad5` |
| `docs/reference/composition.md` | `7e1ac3b1c89aea4bf9a8381a00ad87891e63499d4bede5f0d8734cfda7227c3b` |
| `src/gnd/api.py` | `e9da7643c7f1e2c99a078efd814221c3660ef2778c2b5aade225fecca5c1eae4` |
| `src/gnd/checker/_composed.py` | `27e7c227b66931980bced06b51b7d98ae8fbfb9ecf492d79d48f1572d1ba7d43` |
| `src/gnd/checking_service.py` | `8b0a4a56d5aea378d1b7f2f5a39086fa184dfd8baac2d3c16af704b99bbf9da4` |
| `src/gnd/composition.py` | `2979da66e4df165ddb4f1f023aba360cd4259470996e8424555b0acfacaf37dd` |
| `src/gnd/composition.schema.json` | `8036cc612b7ea106cd9b4f9f91de0add5863ff020621a4ebd08b65c4bf90eb2e` |
| `src/gnd/model/__init__.py` | `b209785df0bf3f4c6dafd131cc383c49ef39992247cc9b8f011f97125293894d` |
| `src/gnd/schema/witness-result.schema.json` | `c3f8cfd922b239a9914bee1aafc61caa0bbec176fe95a21884cce361d399d018` |
| `src/gnd/schema/witness.schema.json` | `4e5ee050eec431d8eb2c7fb9e2f4f6a150da6a0559bddbf4912e1cd390ec9409` |
| `src/gnd/skills/gnd-export/references/witness-contract.md` | `b7652c86396318e57c84bd369a8ff1248718d36b102430e4108e40d6351db5d1` |
| `src/gnd/skills/gnd-export/references/witness.schema.json` | `4e5ee050eec431d8eb2c7fb9e2f4f6a150da6a0559bddbf4912e1cd390ec9409` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `62dade00b1b63cda679f0a432eea40cc64533eb8c8bdb61809128f37f5777db5` |
| `src/gnd/witness/flattening.py` | `c04a881e4dfda700d31e3671e52e33b82c0bd81bf03281dfe75ef7523c961d9e` |
| `src/gnd/witness/io.py` | `daf40df3e737eb283cf369b85a590de11685dc573da0420d2a30a0ce694e2716` |
| `src/gnd/witness/kernel.py` | `17dcb159bbdc0a201ba8afe9b1ff423a8c9c62d7a8b11e6e8ed3e3b34d12b4e6` |
| `src/gnd/witness/service.py` | `ad69d59ee6384f696422e6231f50cd09e0f2fb96505184993a1f5d8b8b5a81c9` |
| `tests/fixtures/lx3-catalog-composition/README.md` | `2da0ca163798174cd1babd9c956d6dea11b96fd485f897811b0495ee881b2d83` |
| `tests/fixtures/lx3-catalog-composition/expected.json` | `c75609385917971e76a6833a7653221f21c8a70f3feb1fd4912cfd4a48445b8e` |
| `tests/support/pyrel_application_successors.py` | `2eea10f7a94328c0d792108732a7ab7226b69fb960d9b50facf9922896268616` |
| `tests/test_lx3_catalog_composition.py` | `31571b9d80a69d8748545041b965fc0eec9e12572e6b3f4d1403dd18c48bff5e` |
| `tests/test_mc2_consumers.py` | `7e34a83e258df2937a340a95a3097c5c6643f6b817e16188c3e6f7f0bd407652` |
| `.gnd-planning/milestones/literature-interop/notes/literature-interop-plan.md` | `0b0b8be165233078e7048948eef45266f007165df557fbdd3c629cd106ae5454` |

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
