# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does gnd.rmap implement the approved OB2 spec (r1 with amendment r1.1) and the normative 'Relational mapping (Rmap)' section, and is there any model the loader admits for which it raises, depends on declaration order or path, places a fact type or constraint differently from the stated rules, or omits one from dispositions?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. map_model never raises for a model the loader admits, under both variants.
- C2. dispositions returns exactly one row for every fact type and every constraint.
- C3. The schema depends only on model content, not on declaration order of object types, fact types or constraints, nor on the path.
- C4. Placement follows rules 0 to 6 in order, with the 1:1 and subtype choices of the selected variant.
- C5. Mapping time grows linearly with the number of fact types and object types.

## The change under review

The work from `e7af6f50` to the working tree at `af34a54e9169`. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/diff.patch` | `392e5bb6c3239cdbf0114e7ec7bf2fd6137adff29bc81dd34f251717f7066ca8` |
| `.gnd-planning/milestones/ossie-relational-bundle/evidence/OB2/dynamic-query-successor.json` | `d44972038eacb7196b4ae582f9290de4ee648307676e8c1f1bb5a6211b2c4e0f` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/OB2-variant-measurement.md` | `d999ed361e04bb61dd52543ad8f2921b813b7deea1fb8b684e463c3f915420be` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB2-spec.md` | `41a2d1b90a32827208b3f3cd08cb6b23560e1ac2d8b712f941dce04ce6faf0fb` |
| `dev/components/COMPONENTS.md` | `97001d43159039e40ee4129f6a6d45ebad753b94c5d37bc1b1a2832097f048b0` |
| `dev/components/graph.md` | `c5734e869ab621d4aff7fbe8b41575170a37f07f933c4d1c023ae279838920e6` |
| `dev/components/modules/_root.md` | `390183f0d016cd83462673fe1d4e66d3e989a483de43dad977e6879df3322cc3` |
| `dev/components/modules/tools.md` | `79abbfdb0d1b9e7c9b422161f47c6f1cff1959ac8aeb55630e72bcf057843a72` |
| `src/gnd/rmap.py` | `9de80e962b0f149f7e40f4eed3b28dde51c0da11fbdd5206f6490438fed4fa5d` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `fba6ac8fe6aa438564e7f12780d2a17ac45c4a34b9804ecdbde44570acabe176` |
| `tests/support/pyrel_application_successors.py` | `088021597e220553ead03afc78054a9bed725a8cf06001602aeafb7544501fc8` |
| `tests/support/rmap_large.py` | `2ad02afe03b94e4e69fffec2f4a60276dfd75591864554b353c23f802adfb36b` |
| `tests/test_rmap.py` | `098a37afbe9e13af0b5bc2fb26d4ed2b649800793c154e85484171fae0732836` |
| `tools/gnd_layers.json` | `1a35d808a91363bbd4e605c350eadefccef31d75b232a1371a33b80bb0507fd2` |
| `tools/rmap_variant_measurement.py` | `c8cc82db8f552c884160adc51e798b1225b1dbd877c258d16c9f497bf88b358e` |
| `tests/fixtures/rmap/answers/README.md` | `84ae2427b49911355dfdb0ea472de54cc8f32286b4074897eba2262412edb2a1` |

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
