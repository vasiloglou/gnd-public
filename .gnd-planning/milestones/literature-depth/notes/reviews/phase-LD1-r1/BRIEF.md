# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the LD1 implementation produce each scoped, source-supported competency answer and make its declared comparison, verification, and quantity-trigger predicates independently falsifiable?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Three installed cases use rooted extraction and preserve explicit unknowns. A reported equation is represented separately from scientific correctness.
- C2. Citation and support mutations fail, comparison guards distinguish unknowns and incompatibilities, and stable identity survives a label change.
- C3. Each quantity-axis measurement supports the corresponding conditional LD2 disposition.

## The change under review

The work from `15276393` to the working tree at `da41bc075eea`. Its diff is `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/literature-depth/notes/reviews/phase-LD1-r1/diff.patch` | `2835d3e4aa0d22a9107ef6d8ceefa86d9cc0f0845b051cdbe0a8149d621b8b84` |
| `.gnd-planning/milestones/literature-depth/notes/phase-LD1-spec.md` | `f2e30cb3bc0a58347b28ff2e0100daf20c10bc5888a83b2d3564ae151370f9b9` |
| `dev/components/COMPONENTS.md` | `66c9e841d9fca820126da1f7ff6f72bfe4a127c0a78e0d1a89e999d5bd684505` |
| `dev/components/graph.md` | `9d4bb2298754f4a577a7a2ccda9b90614d287d24e01936545b8f0d3b9c469150` |
| `dev/components/modules/examples.md` | `3575c122f6097bf108dde9d559afa430eb153470ead56a7f8efcd261e0588003` |
| `src/gnd/examples/literature/README.md` | `2fc16d444c2b79ab8aa929216f5f61e3024501bac8439c1ac8f7c767fdc3b38c` |
| `src/gnd/examples/literature/depth.py` | `814a4c56ad355842bc4efe66e1f6322c93800a204edd7ed125b4136779a2671b` |
| `src/gnd/examples/literature/depth_fixture/README.md` | `88d6bed98efc03ed38bcdd98aa1d9b910178e61eddba548789e7aa2be29f9bbc` |
| `src/gnd/examples/literature/depth_fixture/algorithms.facts.json` | `b4c54de6372d477ecd80284fb4f46556dc0a388753d5656fed63b1980747d497` |
| `src/gnd/examples/literature/depth_fixture/algorithms.orm.json` | `12c50787b75f3a4e32bb0d0d10e62378fb351416f1efd5d023c8ec632fae0830` |
| `src/gnd/examples/literature/depth_fixture/algorithms.txt` | `0ad3f94f8a152da3263d1cf1ea42b460b952dc1088240f60034db27924304ebb` |
| `src/gnd/examples/literature/depth_fixture/cases.json` | `3bc3426bf8f1f005d73a0eec93c4d53566a60c6521c243b64e7cea91343e2cec` |
| `src/gnd/examples/literature/depth_fixture/comparison.json` | `545182d38d0a13d40407e7288af19ddf31fe568deacb0fe935e2de256027a933` |
| `src/gnd/examples/literature/depth_fixture/decimal.orm.json` | `552867ad0f2dd1f1e4f43caae7ca5ffa7093e74ef1855c57955829d6b419bc45` |
| `src/gnd/examples/literature/depth_fixture/decimal.population.json` | `0a6ed4999842fc83dd1118b51a236a56b99d3fc0b4da564748f1429c5de2f3b4` |
| `src/gnd/examples/literature/depth_fixture/decimal.targets.json` | `4fcf989fd9ecbc61f8765d54f348ac830f6ac3872fdfd46714d47c0fd29db6fc` |
| `src/gnd/examples/literature/depth_fixture/dynamics.facts.json` | `33fab64e227cc228bff0633e290c9fd1a009eb6ca164bbdc426c438b64df8afc` |
| `src/gnd/examples/literature/depth_fixture/dynamics.orm.json` | `18e54e6d2877d499a4933b89e78ba200be2411fc8b32dfa0569a59e3aeb83fab` |
| `src/gnd/examples/literature/depth_fixture/dynamics.txt` | `e0e1ed49ea2c0f820187f9c4161c582947185587d4b8f021694555556252513f` |
| `src/gnd/examples/literature/depth_fixture/molecular.facts.json` | `c3fa8d67b4798c47291449cf440f28cb2313242698681d40863f1ea9149be334` |
| `src/gnd/examples/literature/depth_fixture/molecular.orm.json` | `0e521ab2d8c4a7eac1e0d61cb977acc0798450b14f775077c19ef7dac44cbf9a` |
| `src/gnd/examples/literature/depth_fixture/molecular.txt` | `1ee50c933858ee2235d611b599186247659f34c26a88864e0e10fdcd72bd878c` |
| `src/gnd/examples/literature/depth_fixture/support.json` | `8d697a5a169d6dfa27a0dacb498df9e86bd78f1ffbd5365ea82f38264333ed59` |
| `src/gnd/examples/literature/depth_fixture/vocabulary.orm.json` | `25ac1974dc8a1686efe5b794ca55d5560f655d23632002bf625a03a2f1bfc796` |
| `tests/test_ld1_competency_examples.py` | `1eab5342b8fb930ab72981743f9c6252734ddd309487cd5e4b48d799a259260f` |
| `tests/fixtures/ld1-competency/expected.json` | `fd7de6ec831ca4c42f44252140af51cc611612d6521fcbc6c13ac623ad66e225` |

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
