# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff make gnd check's cost about linear in the number of object types while every walk, table and report answers exactly what the base code answers, for every model the base code accepts, including models built in code?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. VG1-C1: for every model that loads, the tables equal resolve_reference_value_type and the walks descendant_closure, denoting_types, kind_of and universe_types return what their base bodies return.
- C2. R0.1: no check, judgment or verify report changes for any model that loads today.
- C3. VG1-C7: one gnd check builds the supertype map the same number of times at 300 and at 600 extra value types, at most 100.
- C4. The tables cannot be written through by a caller, and a cached index never answers for a model whose content differs.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `125b91ca` to the working tree at `1519ecb8727c`. Its diff is `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/reviews/phase-VG1-r1/diff.patch` | `931ebbc7d81360d0e3b520e3f6e1174ef0f5b5150c28d1f05e28b60eb5d1b6fd` |
| `dev/components/COMPONENTS.md` | `d7b28dd19da92f09a8fd8e0d68231557cfcc0606c1bd53124756ca494d6f3b51` |
| `dev/components/graph.md` | `c39dcc56a2bc1a47d28ffb6c1471bf5179edd139aee78d1b46b2d032d108a583` |
| `dev/components/modules/_root.md` | `827d511e226fbf184370c08ed31e75d4bfff39e6c5f0ce9c76c4dee19b024408` |
| `src/gnd/model_index.py` | `432fae28bf653cb271d26f5b12b8909a8f0819223d4041d8df0b9dcb1d9f69ca` |
| `src/gnd/semantic_adapter.py` | `308dc84557cec6b51e90a36254b5a69d51362dacf7303e6fe3b2577b793399cf` |
| `src/gnd/universe.py` | `0a38d9b37787fde7f31504609770d22f5c114ef2e4c31aa713badd8e19c3da59` |
| `tests/test_ir1_judgments_includes.py` | `2fbea7d5421be9acfdd4110e75ea7d85c42987d3aaa6304ebc5c9a61a98c6793` |
| `tests/test_vg1_object_type_scaling.py` | `ea22413e5a2665a855e642920e027d62d6e7f14079403d4b5cf333835596234c` |
| `.gnd-planning/milestones/reviewed-vocabulary-growth/notes/phase-VG1-spec.md` | `51440b6f7a0283eb144dab0eef1b65cd361d60f4039f6bc01cfee91ff092541f` |

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
