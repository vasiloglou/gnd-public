# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can a caller publish an invalid or stale located append, or lose a legal source occurrence, through preview, apply or recovery? Check ordinary callers and a distinct legal input.

## The change under review

The work from `009d18ca` to the working tree at `009d18caa8af` with uncommitted changes. Its diff is `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG1-r1/diff.patch`.
- new: tests/test_cross_document_growth_phase1.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG1-r1/diff.patch` | `c830e433b00e06e86634088768922347b5bec6adc3f00f56202b995bfa353257` |
| `dev/components/COMPONENTS.md` | `7650e7d644c28aac856150dc4fca858fe07e44a481abd161961b6556bb3478aa` |
| `dev/components/graph.md` | `de3f42f50423163c35530193838e131da0b02ccb0ffdfda9c40ad276fe304c80` |
| `dev/components/modules/commands.md` | `e2e4777444dfb39c921d4340cd6059237d9d8a7abca04f17fefe667d9137d353` |
| `dev/components/modules/evolve.md` | `158b80f44c5b56e54a46b7a900a6a0abcd7d3edbe414a8557868ad046a860d25` |
| `docs/reference/evolve-policy.md` | `d21fc59fb9f6fdced47908b0d6559463cd5ed3b2560e1515256987d588e11323` |
| `src/gnd/commands/evolve.py` | `7cd6bd73e6d8cb40325fde1110c30185a4f71b90f33fb2a3f7a490bfd052dbe2` |
| `src/gnd/evolve/cli_service.py` | `4b2512d5303e9aa67faee3fbdde1352d84028d5ae3372b831d0f52d60c914eef` |
| `src/gnd/evolve/policy.py` | `48ec1743fefbb4f06414eff0345330c16adbd41bb1ea1095af89ddeae31a696c` |
| `src/gnd/evolve/population_check.py` | `9fbabdcd1931cd0ddf9af393523af44969aa2d8b9081a2f5f9f73346f5847dd4` |
| `src/gnd/evolve/service.py` | `6f6a00defa90b62f15a56f28dc7906ecc783d8be0ab1d192fd6c7cf34d502e2e` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `e6c755659327a0fb40cfaeb9bac4ee85d3952528062ee52985dbefa49e87df65` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `d198409a8f38890a6c110fc129db507990db4d5c8d08e6a8353e9ae3ecb417bf` |
| `tests/test_cross_document_growth_phase1.py` | `6b69442d67973690248f0995a059c3c132b63a8773b460461a32332a3f34a04f` |
| `.gnd-planning/milestones/cross-document-growth/notes/phase-CG1-spec.md` | `e4d9c82a7d555dee5ed15dea4ad09457f9479c6e0b4b50c15a3ed9a5a5232fd9` |

You may read anything else in the repository that helps you answer.

## A standing check: code fitted to its examples

Whatever the question above, also look in the code this change adds or changes for a
solution that handles the examples in its tests and fixtures, and not the whole class of
input it is given:

- a regular expression, string split, slice or index over structured text (JSON, YAML,
  TOML, source code, paths, command lines) that a parser or an existing reader in this
  repository already reads;
- a pattern over output this project renders itself (a report, a table, a log line), where
  the code could have been handed the data instead;
- a pattern fitted to the fixtures: it matches every committed example and fails on a
  legal input with other whitespace, quoting, casing, nesting, Unicode or a line break;
- a branch on one literal name, file or message, added to make one case pass;
- a second matcher for something an existing helper already does.

A regular expression is not a finding in itself: one that states the whole grammar of a
flat token (an identifier, a version number, a hex digest) is the right tool. For each
suspect, build a legal input that the tests and fixtures lack and run the code on it.
Report a finding only with that input: what the code returned and what it should have
returned. A suspicion with no breaking input is style: label it so. In your list of what
you checked, name each matcher you tried and the input you tried it with.

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
