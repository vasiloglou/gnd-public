# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the change to temporal_nodes in src/gnd/terms.py treat exactly the maps keyed by role name as containers, for every place the model schema puts one, without hiding a temporal term anywhere else; and is the 0.5.1 tag-only bump complete under the procedure in docs/releasing.md?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. A sample row, a bind map and a derivation head are never yielded as nodes, whatever their keys are, and every value inside them that is a temporal term is still yielded.
- C2. No other map in a model document is a role-keyed map, so no other place needs the same treatment; and the change yields every node the old walk yielded except those role-keyed maps.
- C3. The order in which nodes are yielded is unchanged for documents without role-keyed maps, so validation error order does not move.
- C4. The release notes' two bullets state only what the change does; the notes opening, the compatibility paragraph, TAGGED, the version fields and the install-from-tag command meet the tag-only procedure; the install pins still name 0.5.0.

## The change under review

The work from `102110b2` to the working tree at `a8059adc922a`. Its diff is `.gnd-planning/reviews/issue-286-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/reviews/issue-286-r1/diff.patch` | `68b9342072c0413f08875da521651414f7af7b2dc9539f3a75567e03e3d9ac0a` |
| `.claude-plugin/marketplace.json` | `585c84e020e683462b827668de77e97c7401b091364ba2c47896eb7fda29861e` |
| `.claude-plugin/plugin.json` | `bfcfc5dddfe807e1562e9bc77fadd25e9a4f7a6db0e57f9d01a5a8364ec9b1e5` |
| `.codex-plugin/plugin.json` | `4db81f701fcf043f837f9ce8653c2130983aa2c0e91c113e893b1449a9ab3c83` |
| `dev/components/COMPONENTS.md` | `7110bf5d091c2345bc5d718c800cd9782a600dd946258d956943a8cae89a1097` |
| `dev/components/modules/_root.md` | `6cb23a34750f069fecba515a7820e08257e6188551b4b29e83c551aa86e8ed1a` |
| `docs/compatibility.md` | `f1997225a730e83bbb52ffe98f6cdc7e3084b9f2c6c481b0c26d861b532b5915` |
| `docs/release-notes.md` | `3417c2b460d9ac8911635de4e40f130db5ba4cb3beff485f85028ad1aa1be852` |
| `pyproject.toml` | `ad19198871890329fd5eaf64f08fd256dabecca0bbd1ee5e1cb01dd7d2273ab5` |
| `src/gnd/terms.py` | `050641f0a86516e93fccd83b142b4975b0a0a41e835a3a44f0ab719fc3587fda` |
| `tests/test_issue_286_role_keyed_maps.py` | `cafa782a6d72b875d3597692226652c5caab07d3f952b524416e8ec5c8099b8e` |
| `tests/test_release_version.py` | `2c69d01015a3557f7db5dbbf742b6b3773014fbfbe35018dd58aac6554ddc151` |
| `uv.lock` | `93d1735c2dbd70f0625072b77ca1068545f4043688730b9b672feec59888b4ab` |
| `docs/releasing.md` | `59aed07138dfa74427148e3958c0741cc04a81cec8a57406bdca578282ebc30b` |
| `src/gnd/schema/orm-meta.schema.json` | `0cab9e99afbc048afe328d57009062bb46932d8790688f3e4a8f27e75ef0cc62` |

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
