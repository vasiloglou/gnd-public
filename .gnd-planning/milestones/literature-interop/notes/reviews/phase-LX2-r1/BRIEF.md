# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where can a rooted v3 witness or replay accept stale inputs, confuse a model origin with a fact occurrence, or regress the legacy wire and guarded intake?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. The rooted verifier re-derives flat bytes, the record binding and model origin entries, independently of proof fact and composition coordinates.
- C2. Malformed or over-budget inputs and stale root, include, artifact or composition bindings refuse in the pinned order.
- C3. V1 and v2 production and replay bytes, disclosure behavior and direct authored include guards remain compatible.

## The change under review

The work from `ac157120` to the working tree at `1274776436b6`. Its diff is `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX2-r1/diff.patch` | `d216fd96948411015f7ae935cb1f391275fd3cef8d63706c05d3d9a4baa1afbc` |
| `.gnd-planning/milestones/literature-interop/006-phase-LX2-spec-gate.md` | `7eb5b012125d8020fa510079611c4429baca0d4e3c90f2e350bc9b6d0c991dde` |
| `.gnd-planning/milestones/literature-interop/evidence/LX2/dynamic-query-successor.json` | `e14ff83d7e3f527dd5a390b5e871720457d0775c146328bcba2e13d40d8e48e7` |
| `.gnd-planning/milestones/literature-interop/notes/phase-LX2-spec.md` | `a221efdedd240abafa0291a9e2bab2cbca837f74e3b869431c9968ccdbbeb6f2` |
| `dev/components/COMPONENTS.md` | `375ed71ac5672882c7eda05e9cbd2648331f84dd78d10ebf2def341202a7342d` |
| `dev/components/graph.md` | `62b85aaf62b96f57cdd0eae0fca5df6f60c7935fe9f917dd23b4dd662528c605` |
| `dev/components/modules/witness.md` | `f739ea3f2f910af2f4206765b10d87c6467a753478ceed3f636bbab9118391de` |
| `src/gnd/schema/witness-result.schema.json` | `68dcfc71c8089fbd09e7f2e3593d773f90de0ce30792adeeb35984804f7f824b` |
| `src/gnd/schema/witness.schema.json` | `b0a08258abf500929e53026ce2322bfea083ef1b8763fa0bd1c4c79eb7e3304d` |
| `src/gnd/skills/gnd-export/references/witness-contract.md` | `5af72b86c97c53c4b3541df4d0d2892ece24ffef49a4246c43e184943aa6bb9e` |
| `src/gnd/skills/gnd-export/references/witness.schema.json` | `b0a08258abf500929e53026ce2322bfea083ef1b8763fa0bd1c4c79eb7e3304d` |
| `src/gnd/witness/cli.py` | `11f790e18aee6919383a88205bad02ffcbfa3b10e8906f2c1c552e9e20434334` |
| `src/gnd/witness/flattening.py` | `c9b5abdcefcc0660738988eeb8fef4e01fad5cb55422f1197e6d9a1b77d8c2a3` |
| `src/gnd/witness/io.py` | `bd4833cdac2ecd1632dec1a5807dc85254e3d76640ceb2132043a4b2495701fc` |
| `src/gnd/witness/kernel.py` | `7911387d2a79cea38c707f7168e1fb5d7bdd9de1cb2bfcf69cf0d9042c0bd674` |
| `src/gnd/witness/service.py` | `35d6d67b4fd86b3746e533e167abd9c64a47d68b12187e1aa39c8b382bacf16e` |
| `tests/fixtures/lx2-witness-flattening/README.md` | `66de950b2d63dc4173b072e0806954b226db88f61868bf60cdcdb61203c17ea7` |
| `tests/fixtures/lx2-witness-flattening/expected.json` | `5eb62aef78678b89f3e5b552444a5d011149a83f5f9505bfb6e77de851bbf578` |
| `tests/support/pyrel_application_successors.py` | `b83f7b06d2c73b25146c3463721204116307fb34510237f1b107c1da45ab1724` |
| `tests/test_li0_witness_wire.py` | `4b9db634335fe4be9850fe1368584e7faa55fe65fe2c8ca69e628762910fb154` |
| `tests/test_lx2_witness_flattening.py` | `9b0dbe4e05dde3b52440a360b0327472c50be58802175a9979c81b68a8cdc406` |
| `tests/test_mc2_consumers.py` | `965391f7ce9800860c136f4537ff8f9ac52e07c9cc7cd0421a89ad3e8767302c` |
| `tests/test_packaged_skills.py` | `43c09a91831bb74cd238cc68f085bcf3dec821d49fb97ccae36cdb066529b140` |
| `tests/test_rf1_cli_pins.py` | `20fbe1431434b28f4ee6c6fadfb0009401b02100d81b8a6b86e1ef1bc6f05427` |
| `tools/gnd_layers.json` | `a0a8ecb54e1f19f4a33f134d12f22db1e0e4b8120ebe8e7655fa7ad4b0ac60e0` |
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
