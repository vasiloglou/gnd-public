# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff make one gnd evolve preview or apply parse each model text once per reader without changing any preview, record, published model, message or exit, and without letting a shared parsed document be changed or handed to a caller whose reader would refuse those bytes? Find the input or path where it does not.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. GO1-C1: one gnd evolve apply parses at most 3 times and one preview at most 2, the same at two model sizes and for a YAML and a .json workspace; with the scope off the counts are 22 and 6.
- C2. GO1-C2: for the cases of the focused evolve lane and for an include root, a .json model, a YAML model with a value JSON cannot spell, a policy refusal and a D-12 refusal, every output byte, message and exit is identical with the scope on and off.
- C3. GO1-C3: no remembered document differs at scope close from what the parser built, and the write check (set_parse_scope_verify) detects any write, including one made through a loaded Model, without false positives on values JSON cannot spell.
- C4. GO1-C4: a model file changed between preview and apply is refused as today, a second command in the same process parses again, and nothing remembered outlives its outermost scope or crosses threads.
- C5. R0.2: no validation, guard, digest comparison or refusal is removed or reordered; a parse that raises is never remembered and its refusal names the caller's own source.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `2814d9be` to the working tree at `84c8df0b9772`. Its diff is `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO1-r1/diff.patch` | `1260d693d385349750391d6d4d3c7ca35f6ea0f7a60f80dc9c57de73e0429de5` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO1-spec.md` | `6ba1f929022f8e12a0e0fd05706171b8106ec52357884e3572b60801dcd6b000` |
| `dev/components/COMPONENTS.md` | `7d20f4f65b48c401017cd576348a778ba1d75a3afd91980bdbfb3b79217d0f1d` |
| `dev/components/graph.md` | `c6e97de6d478f5393292ad25c7efadef649a708bc6f01a34aaad7d90e36f335f` |
| `dev/components/modules/commands.md` | `3f8f1e91fe1c0dc17d0666703193d3f0a0e6ee5703a24fbb20191f43fe4e7984` |
| `dev/components/modules/evolve.md` | `b660723360b65e206f09b7364395a612a366cb9a7f50d0eb35a0272a35a9f15e` |
| `dev/components/modules/model.md` | `51e2a79c9fe9c670e36e16f12bf0612e930c29ec75d33cf12c94d047d9088564` |
| `docs/release-notes.md` | `fcc11c43e444fbb43c5f5b6f3f1a2687c44bc55f3c6f3cf15e6bbc8d60b5fbe5` |
| `src/gnd/commands/evolve.py` | `106a045fa89a4439e279b166cf197146fa52e9b8b1330b7186045bb4f5e4874d` |
| `src/gnd/evolve/cli_service.py` | `a1145e7fcee18e93bc59433438117060c4a647eeb00ba1f2f0cb53495cc01835` |
| `src/gnd/evolve/service.py` | `8662e9368bfccc009ced7f86b6dfd1096c901bf11b72c589f56061a7975c2873` |
| `src/gnd/model/_parsing.py` | `d4411dbdf813193ec46660b80c881718a4ca4f849737d582881c2a0bbca50f96` |
| `tests/conftest.py` | `f18fedd4c10f45a4717095c353aab3a4529b51b50a0737ac9f635c5817048249` |
| `tests/test_go1_evolve_parse_once.py` | `fa26af6136af5eb43a3512c375854e748429f63edb3ef8d7bf5e701e8e34fd05` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/growth-round-outcomes-plan.md` | `b107bd366101719a7cc997a6d5d4212dea5dc80f5d121c4dec3fc8b669007431` |

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
