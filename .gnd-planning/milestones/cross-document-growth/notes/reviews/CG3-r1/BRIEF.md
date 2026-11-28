# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can group decisions lose samples, role references or source spans, publish an unreviewed change, or produce different outcomes across concurrent or interrupted resumes? Exercise distinct legal inputs and the public terminal workflow.

## The change under review

The work from `1cce6979` to the working tree at `1cce697983f9` with uncommitted changes. Its diff is `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG3-r1/diff.patch`.
- new: src/gnd/evolve/consolidation.py (not tracked yet, so not in the diff: read it whole)
- new: src/gnd/skills/gnd-consolidate/SKILL.md (not tracked yet, so not in the diff: read it whole)
- new: tests/test_consolidation_loop.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/cross-document-growth/notes/reviews/CG3-r1/diff.patch` | `d71e041b6c857789f5a37dd3157bedebc6d06c6be3de73f20dbcf1c36b131608` |
| `AGENTS.md` | `739a1a9bef381ebc4363f7b9f3c0f5504d8bc43aabe60d26afee7bd2453e144a` |
| `dev/components/COMPONENTS.md` | `72492dc82f2cf3c8148da8ffa3e7b80e99b84e146810a1f3126c221037a101b2` |
| `dev/components/graph.md` | `db8714eb018a726c87368f2724fea21e3fe9c432ae02b6ee2d690c722bd36f31` |
| `dev/components/modules/evolve.md` | `404e7701e9117c7490cc4f11faa91903fb1968102dc76962055b098c492a355e` |
| `src/gnd/evolve/population_check.py` | `2df0b8ef85a0c94e506a28904aedf20368ae1d7d7ad9d8820552a432d631313e` |
| `tests/test_packaged_skills.py` | `cfca342fe3b27e51321b3d5cd490e8154fe55072ac86e3b417d71efd5009322e` |
| `tools/gnd_layers.json` | `ad65813543f19ddf26e449d14f1a1719aafb70be08b31a5603cbd3f755fbf5b0` |
| `src/gnd/evolve/consolidation.py` | `62e44beb89f02a5ecf96ddfc7c1076c8bbcdea8fa05a7a4cae48bd6020e05efc` |
| `src/gnd/skills/gnd-consolidate/SKILL.md` | `2339bb8ac12c2023f10410315a95137d9d664d0f6c92b8ea63a95727236c54fa` |
| `tests/test_consolidation_loop.py` | `b33c8eba00bebf1a4cef5af00b5b9d146b2000b522c25cbc5784f3106d3c0b16` |

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
