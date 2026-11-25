# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Round 1 found that role-map detection matched keys inside an object type's description. Does stopping the temporal walk at description fix that without hiding authored syntax, and is any other place in a model document still open to the same confusion?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. No authored term syntax can be placed under a key named description in a model document, so stopping the walk there hides no term the temporal rules should see.
- C2. Outside descriptions, provenance, source and rejected proposals, every map keyed by bind or head and every list keyed by sample_population is a role-keyed container in the model schema, wherever it occurs.
- C3. The new notes bullet states exactly the behaviour change of the description rule.

## The change under review

The work from `a8059adc` to the working tree at `79b3cc357113`. Its diff is `.gnd-planning/reviews/issue-286-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/issue-286-r2/diff.patch` | `005f1c0c56e949af511a19e0bfdbed4ded31c9b1e74e232b9d0ea0dc379216a1` |
| `.gnd-planning/reviews/issue-286-r1/BRIEF.md` | `3ea6accf1d0206dc9a87c382c395149080392856c597ff9312d834ab4b404609` |
| `.gnd-planning/reviews/issue-286-r1/FINDINGS.md` | `7ca0f3acffb69e09d5af5ffdb81ac9a0b6ad2848eb393453af2c80b3ce2339b2` |
| `.gnd-planning/reviews/issue-286-r1/brief.json` | `bd83d1087cd051c67a19fc007826690902d8a5dcf6acb1783ed191ef174f847a` |
| `.gnd-planning/reviews/issue-286-r1/diff.patch` | `68b9342072c0413f08875da521651414f7af7b2dc9539f3a75567e03e3d9ac0a` |
| `.gnd-planning/reviews/issue-286-r1/review.md` | `823559ede4d1127e29308d2facb5a110b65960eee1fb99bc7d2fcf7023f5de61` |
| `.gnd-planning/reviews/issue-286-r1/run.json` | `e225334b0ed3085ffbb260687266a941b88f06e72b7c956d174cc42cc2f3d958` |
| `dev/components/modules/_root.md` | `f9bf45397a513f9501bc0664b80b2e0c1fbc7b33551cd7a807f643e9827038c6` |
| `docs/release-notes.md` | `57e1d1877cad11358558bb569f7faf352a47a013dfc720c902eb4226b45ed529` |
| `src/gnd/terms.py` | `4f7ebf46e69ebadf72d9080820881c9ae2ff926572d5b25127ac99a4ff4384f2` |
| `tests/test_issue_286_role_keyed_maps.py` | `a71705e9898da94ef6f72355b0f3354a84bc77dfbca805bec2ad20db2512382c` |
| `src/gnd/schema/orm-meta.schema.json` | `0cab9e99afbc048afe328d57009062bb46932d8790688f3e4a8f27e75ef0cc62` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `594ec58970647df4abeca920579f2088b671fdd65f0ee473354c1ebd204ca92a` |

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
