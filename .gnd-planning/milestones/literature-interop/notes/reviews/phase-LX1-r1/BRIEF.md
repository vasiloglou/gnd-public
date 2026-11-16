# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Which LX1 claims can be refuted through a public entry point, a bounded input, an interrupted publication or a stale binding?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A two-include extraction produces a canonical re-entry document and origin record, and verify authenticates both against the root and pinned includes.
- C2. Mutations, a coordinated flat/record forgery, and a missing flattening binding refuse before evaluation.
- C3. Include-free bundle bytes and the historical LI0 model-wire behavior are preserved.
- C4. Publication refuses overlap with a bound root or dependency and retains legacy include admission and temporal refusals.

## The change under review

The work from `183972ea` to the working tree at `e2ce2ade32e1`. Its diff is `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-interop/notes/reviews/phase-LX1-r1/diff.patch` | `f8ac558485e8e249947079d4f96ebb90c7e9878bf1fa47d3a6400687b796b459` |
| `.gnd-planning/milestones/literature-interop/004-phase-LX1-spec-gate.md` | `e479b236e02eac2ae2f487855d47a296cd51a62e09756f5d70a64fdab0af5999` |
| `.gnd-planning/milestones/literature-interop/evidence/LX1/dynamic-query-successor.json` | `6309a0664fb9dc6411e2c8a71881e717cf26dba63c5d795baa70d1515e316d94` |
| `.gnd-planning/milestones/literature-interop/evidence/LX1/source-successors.json` | `9af4e2fee29626a7e28d1b71afa5450a72d17d29c968d320a7e499c4762fb6a9` |
| `.gnd-planning/milestones/literature-interop/notes/phase-LX1-spec.md` | `9794dae65c4d5d13028b3d59ccdfe40edd3696a47de541ab04788e19d6bb4ae7` |
| `dev/components/COMPONENTS.md` | `623492819897b5983624a2d22a9aacde40b072caae2ca608263468025da2c2d3` |
| `dev/components/graph.md` | `fd39918331929fc241c2c36187e6ed39c800907d80e276743170a11ce78b3420` |
| `dev/components/modules/extract.md` | `9f677dc9985f5e27705fceae41340a91956db2b55473fc8a2df9d6bf401821af` |
| `dev/components/modules/model.md` | `06358c626e14a4ffe30a98cdda34d8b129e726c465bf222425aaeda84e4e6dc9` |
| `dev/components/modules/witness.md` | `9463609b7a113f9404c92cb6700ddfd8c16ab41304d7aa61d25d00202de3e12f` |
| `docs/guides/documents.md` | `4ab5c1c766153d58c46cf84886aad41ca4b2bbcc17caf493968ab4dd2535bf37` |
| `src/gnd/export/verification_service.py` | `7e1c39a696d25337955e4955c6cce4cd4baad41cb75c91fbf0a27ed9e7ef2908` |
| `src/gnd/extract/service.py` | `c3bbb2adea4bd0480a0ac892168bb99c6fa1344d8c8f3a5cb73343173be0766a` |
| `src/gnd/model/_documents.py` | `2d44269b061ef2e2f1397de602fd9f01df99b6f796b101639f61725d3a3124d8` |
| `src/gnd/model/_includes.py` | `5b0835cc6e0477d9c4df8a10609948d27ed688dfee73aea2e90579b66347990a` |
| `src/gnd/model/flattening.py` | `75d50046b53d284ff49e8fb19b8e24178e8e24988bfa14eeac7ad774fa00dfed` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `f508d30af970aaaf9db9774df0cbae7099e4179fb702dc9c0179f934765e4d6a` |
| `src/gnd/witness/io.py` | `d47d3bf34c3d416af210266a2e249bde76b7eb86d204607f7dee86418dad3f26` |
| `tests/fixtures/lx1-flattening/README.md` | `81cf195c66f34617cb6d1e0fdf7a158f94bb7ef6efd15ce38d731074518132c4` |
| `tests/fixtures/lx1-flattening/components.orm.json` | `c1b7802153351c2aa2dc827a191f14a4870d59ec30fbcfcd8fa9f53eb2f67320` |
| `tests/fixtures/lx1-flattening/document.txt` | `953221e526b6a2f6eac34a62dfde4a09056b078725bb8b3ee3dc32ddc3a1f8d1` |
| `tests/fixtures/lx1-flattening/expected.json` | `d3838579e32af331aa4f25bff242d3d21a534180fd60f293dc529e016acc6d09` |
| `tests/fixtures/lx1-flattening/facts.json` | `e0e135cac1f5b567258994e136aebf5820279ea95850ea59dda6e76a435c0484` |
| `tests/fixtures/lx1-flattening/project.orm.json` | `9e7a9e7a5b5f76f6f253a3fc965d386db667b97468737169b93d4320fe99e4bb` |
| `tests/fixtures/lx1-flattening/topics.orm.json` | `7f09b19990e17cf9b6f368150538eab65d22b21e534268711f8b0c4c10a51178` |
| `tests/support/pyrel_application_successors.py` | `3188f7dfa8e5be028f275cef97aecab8e0490bfdb99691a7a4906adcc286e4d4` |
| `tests/support/rf9_ci_sources.py` | `cdd2936a22a1478e258ea8db429980cb7c11b3a25bffb76e792700d0a36320b2` |
| `tests/test_li0_witness_wire.py` | `aa2ace674d2d03b41a3a46e1c7fbd52f22572a4f50f16792a73a8653837c0490` |
| `tests/test_lx1_flattening.py` | `777297adb7a1c3c606db5c696c143275152506df8df2b0bb288bfdfb8188ff8a` |
| `tests/test_mc1_guards.py` | `85a061ac2d46f2550e9b2be2bfc689b66bf4860ec8e4ddd18e1e85d88255e8fd` |
| `tools/gnd_layers.json` | `6ba670447ef1ae3b3c93e3af3d4f709390efb566b9591a33c93c756d668aba83` |
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
