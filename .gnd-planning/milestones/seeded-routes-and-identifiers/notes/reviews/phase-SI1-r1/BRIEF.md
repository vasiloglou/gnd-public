# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Where can the seeded route, authenticated ownership, standalone refusal, or existing model compatibility claims be refuted?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Required seeded root routes exit zero and a standalone projection needing exemptions exits three with a named diagnostic.
- C2. Source documents and caller-supplied flat bytes or records cannot grant include exemptions.
- C3. Rooted extraction verification and witness replay derive their projections from checked pins and preserve previous structural and binding checks.
- C4. A validation error on flattening re-entry exits three with the named rule and publishes neither artifact.

## The change under review

The work from `99cf3df2` to the working tree at `99cf3df2aeb8` with uncommitted changes. Its diff is `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/diff.patch`.
- new: tests/test_si1_seeded_routes.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI1-r1/diff.patch` | `347b027b10038a95792c88878543538a4e2989d368168dd6991a0518b24cc060` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI1-spec.md` | `c5907475b33e18e35e4b0d30d3ec276ee4dd8fcca8bf828775ab99344b749506` |
| `dev/components/COMPONENTS.md` | `3e08cb5c253c318f82494979c5218831027a5867714ebff5e1904edaee4af7a7` |
| `dev/components/graph.md` | `827fd6d49c88a738848bd4602a1d531dcaeea62e4ecde080a02fd8e9a937ee8d` |
| `dev/components/modules/export.md` | `8a8b7c1c55afe4dac28500ae95f3a18bfe7c9deed8faa35a210d15a9e4cd2c9c` |
| `dev/components/modules/model.md` | `189eb913cb64bf7ac9da32eecccf9f4415e2b5b05bfd8f5371e96057c04e8247` |
| `dev/components/modules/witness.md` | `3ae856c97a1712b52cadbad67468f231058f3b820fba6ebe991e35b2fd5277ed` |
| `docs/release-notes.md` | `e33e76bafb970e8b4ae06aefa5e884d5e6dc8e32633658ef012732dd4f560508` |
| `src/gnd/export/emit.py` | `422b2b45b74936948515e96b54dbeed95f849321e0eb7133b18fbef73ccf760f` |
| `src/gnd/export/include_roots.py` | `c5dffd7df4f13271f13ea2c1894e02cb398a9ec1df68794b56f30d67f1863ad1` |
| `src/gnd/export/pyrel_rules.py` | `ab20c148cf89bf03ad18f3e87b1c1f8f79026c2d41ee01952f6c95a48bc049f9` |
| `src/gnd/extract/flatten_service.py` | `fd64639c093c94da1d61e3d8d44f251ab57dc47fc51ac8c9370dcf8395824a50` |
| `src/gnd/model/__init__.py` | `d9881751f18708326ec6cab3d9bc4c3e72be6829c8b12ff613991214ee75707d` |
| `src/gnd/model/_unattended.py` | `04609f3fa423434ca32013403c540e49d8fcc069ea0fabf2aff8eafb2abac2c3` |
| `src/gnd/model/flattening.py` | `34540762f3b85940b73ea708d4021130796feeb33ad15cb3aa00b4a01d64073e` |
| `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` | `eb004b90f123ac034ca8553306bffdf6532d20554c0273f15f7728c01f48a309` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `07b04ec25b290a16345f10f83b53049df0ef32a05d714ee8bc6f3b347d2b7d70` |
| `src/gnd/witness/flattening.py` | `3f072528aa6eaa4cf1cb1bd82c2aefb29b72eeb629eb8023b29e08811000c35a` |
| `src/gnd/witness/io.py` | `d65f2cf95e24ef54fda3d44f7ebb7c4c8bb69e325e451cbb46861f15a079de0e` |
| `src/gnd/witness/kernel.py` | `b64b55e066a705b54c027a050633474867cee8d05ac0a48be3e9ecf93e4318b9` |
| `src/gnd/witness/producer.py` | `776d7d3af72e94632bf6eb4b7753d112de2dffe09ee6fc3b30916c246202b464` |
| `src/gnd/witness/service.py` | `453c2956ed2a1c002df75f1377122bd0b44deedd6f5d8c3dc4c3122b1c15aaae` |
| `tests/test_si1_seeded_routes.py` | `cdeefc84ed8ab92a21442835088cb63d36b9892366116a834db938c0be3de12a` |

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
