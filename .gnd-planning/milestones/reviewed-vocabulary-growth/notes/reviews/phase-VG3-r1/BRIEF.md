# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff let an unattended root include a reviewed model while every element the root owns keeps every unattended rule, every included claim the include rule refuses is still refused, and every model 0.4.0 already validates keeps its exit, issues, span counts and JSON output?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. R0.4: a root-owned element, including a constraint attached to an included fact type, an operation and an obligation, is checked by U2-U8 exactly as before.
- C2. D13 (a): an included element that is not confirmed and is alethic with source sample, llm-inferred, common-sense or induced is refused by U8.
- C3. D14 (a): an included span is checked by U7, re-hashed and counted exactly when it is a mapping whose document_sha256 names a document the root declares; every other included span is read by no rule and not counted.
- C4. The rule walk and the span walk decide which elements are included by one test, and it cannot mark a root-owned element as included.
- C5. R0.3 and VG3-C10: a model without the mode, with or without includes, and a root that 0.4.0 validates give the same exit, issues, span counts and JSON payload as before; only the text output of an unattended include root gains INCLUDE lines.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `3ea39d7f` to the working tree at `6034a651a1df`. Its diff is `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG3-r1/diff.patch`.
- new: .gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG2-spec.md (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG3-r1/diff.patch` | `9f926f11be4350eaaabf3ae66d182bd3255f90ed5b41b0dcb5034f9f88e844d3` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/evidence/VG3/source-successors.json` | `3cfe99852c33fdcdcfdb2cf46896e2e3bdeb54e85a0186956d905fe4cbefe498` |
| `dev/components/COMPONENTS.md` | `ae48c7797173880d5be3d5647ef1beaed2d611148d50bda280788b5597049d03` |
| `dev/components/modules/commands.md` | `e9281475b3c1cf3f0f3793574d28932ba43f16c636ecd2f7f9cf21c420bd0f96` |
| `dev/components/modules/model.md` | `6d10da706d0efac43080f145e526ab58a617258a1538edf9c527bdb9503176cf` |
| `docs/release-notes.md` | `3202f373c0eea5cb286104ce3a1fa372e34ab7cd96f7f339a027c1df1e2bb858` |
| `src/gnd/commands/checking.py` | `48fee6b3300644a4632ca7966a911f475c6e5cea7fd2f512ae6a291168ec6843` |
| `src/gnd/model/__init__.py` | `4bf2f5ecff9b4ef2371b5b8adcc0e4dda5d4af0c15279d7a9805fb14410b7204` |
| `src/gnd/model/_includes.py` | `4b776a91ff2a743a1867f176e2a5391208c44d4d85d3c6b228e52807a1063346` |
| `src/gnd/model/_unattended.py` | `480f3e31bad81460becaeb5b20290d45bae02a62f2fe66cde6720b4b901559e5` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `a77e4427db612ad496addaadb3a1f3a4400b09338e0018496524e411af12ed9e` |
| `tests/fixtures/vg3/base-outputs.json` | `4a95873c1f51e12707f1d0332f7e2b378e0842418d3896925628221aa4c1b436` |
| `tests/support/rf9_ci_sources.py` | `7408ce353ccce3d5222e2227bc7650ee2aafbd68f1b40f43532aa2b1081fc2a8` |
| `tests/test_mc1_model_includes.py` | `7ea4751a87f6f0efb840b48660292359f0704fbab49c69e90938b3107bdfccba` |
| `tests/test_mc3_source_observations.py` | `f11e551ad1e9f7ad6e576721fb08b2a9f7b5fb06615b268e4a10bd1fe33b8fc3` |
| `tests/test_unattended_span_coverage.py` | `da823611f4649bf4094538a4aeab16751f4e4eb0d1de37864fc8eafbed78abcc` |
| `tests/test_vg3_unattended_includes.py` | `0d6b67ac3764df1dd0ed805f06e44cf8e7f84879461eb0198b22dc0bfb3f7724` |
| `tests/vg3_cases.py` | `73121ddc981b2cf6c878265d812c79124b810ebc13266e329bc6fadd20095cb6` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG2-spec.md` | `17b5988bc456adf72eb976a91ae5efd47eb6b1c42d855610e0ae080a76adc4cf` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG3-spec.md` | `1ef2d85a6feec508c558412571a4014e1119022ba6dc7741baf8dcd6d825c3d1` |

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
