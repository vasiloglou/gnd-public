# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Review the persistent local worker and tested dependency range, including protocol recovery, invalidation and isolation over valid and malformed requests. Verify scope of the installed-wheel results.

## The change under review

The work from `c6ae3e2d` to the working tree at `5b52e43f18c1`. Its diff is `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/reviews/PS4-r1/diff.patch` | `b4f5d7038575951e227a945bd8aebf064e591aaa73eb42a67856ec54bbcbc542` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS4/independent-host.json` | `83c8cb2b2e4a2e75c7c6916e5edb7f3c6f87884e547d65714011723e646a3bed` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS4/installed_replay.py` | `e36bb1ed3047f4c8096b2aa30608bf0d30790e158192dad783ad50bfc20a4a99` |
| `.gnd-planning/milestones/python-snapshot-evaluation/evidence/PS4/locked-host.json` | `c06f07982df7de4cd1900a6ebf5ee7456bdd59324673e3f9b51235f9ea5c1411` |
| `dev/components/COMPONENTS.md` | `569b65194fc365d819903c454c2487fa3dd670805d27051a02622198c9cb20de` |
| `dev/components/graph.md` | `d2408789804b86381d2eca2516687e6a18881f75ae3de64873876c7e6aac4481` |
| `dev/components/modules/_root.md` | `593c47637f194c2229bf8e27b13b1fcfda8d820d6802c2d66073a3df94488271` |
| `docs/reference/python-api.md` | `65d739bfd21028a1ef6e44f9a557f5168f77f6120640144efcd256be5ee183f8` |
| `pyproject.toml` | `220c87f693598d582f64f2f235a63208745ae4a80759cbc86a504e281e408565` |
| `src/gnd/snapshot_worker.py` | `240f98db1c76432ce5fc5a7702dc675b34378a514ec2bab230aeb1a98eaf813b` |
| `tests/test_public_distribution.py` | `0b71baada27325dc4ce67c48eb2c45fae12a737e0788af86df4bc0097f1801eb` |
| `tests/test_snapshot_worker.py` | `8e7ca421a9b00af8c3be9f958b41491619a7f4ddd7b3abf0c3535e4031b83b9c` |
| `tools/gnd_layers.json` | `708edf9e46db18445e57555816a96b498f749d603b476635f94ca034ab179049` |
| `uv.lock` | `25af245882873d0fa0617f370438c5a4c58e3cd03c26e79cc2d9f1f866f457e1` |
| `.gnd-planning/milestones/python-snapshot-evaluation/notes/phase-PS4-spec.md` | `f9f80258d16e014747e2a3357253d730887f80c6cdfd96282dd1f53d90626532` |

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
