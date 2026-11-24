# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does 'The reply shape' now tell a host, unambiguously and correctly against what gnd evolve's additive policy admits, what a reply carries for an object type or fact type the model already has, and does the guard fail whenever that statement is removed or weakened? Find the reading of the page, or the edit of it, that the guard misses or that the policy contradicts.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. GO4-C1: the page states that a reply names an existing element (its own or included) by id only and never repeats it, routes rows for an existing fact type to open_questions, and the example shows a reused host.
- C2. GO4-C2: the guard fails when any part of the rule is removed or the old wording is restored.
- C3. GO4-C3: the packaged growth examples' proposals add no element their before-model has and change no existing element.
- C4. The statement that the additive policy refuses a changed sample row on an existing fact type matches the evolution contract and src/gnd/evolve/policy.py.
- C5. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `f7ec03b4` to the working tree at `038f64dc0a4f`. Its diff is `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO4-r1/diff.patch` | `e5bba9bdf67db0e5ae398256b46e19d595012e355c753447abca1c8d25e1d287` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO4-spec.md` | `cb5649d8c330b0c42a950394f5785236d0ca9d294fccefb26da99bfbf1950b50` |
| `docs/release-notes.md` | `a5afb61b6f9a6b34ef24a35ad92390179eb76c04b442eb441117f530842a100a` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `4ff79bddae5be153ffdcb7d365578cb64ab018e9e27a51c148ec02828ab8912b` |
| `tests/test_unattended_growth_guidance.py` | `bad7bb1146b7d2d60f492a20e9785a0a55298676a1a47edf6158959c5f3ac032` |

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
