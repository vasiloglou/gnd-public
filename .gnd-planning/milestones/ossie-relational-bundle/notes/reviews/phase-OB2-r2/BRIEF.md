# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the review-round-1 repairs (commit 4b50f740, spec §14 RR1-RR9) correctly fix findings F1-F9 recorded in notes/reviews/phase-OB2-r1/FINDINGS.md, without breaking the approved corpus or other rules in the normative 'Relational mapping (Rmap)' section, and is there any model the loader admits for which gnd.rmap now raises, depends on declaration order or path, places a fact type or constraint differently from the stated rules, or omits one from dispositions? Under D5 = HALPIN (007-OB2-D5-gate.md), check both variants still.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Composite identification uses the confirmed, alethic, preferred external uniqueness anchored on the entity, with the smallest sorted role references winning a tie, independent of declaration order (RR1, F1).
- C2. Duplicate uniqueness constraints form one key, preferred if any is, and share one disposition; unique keys sort by column position (RR2, RR3).
- C3. An external uniqueness whose columns lie in one table is a unique key, and an objectified uniqueness narrower than the key is a unique key (RR4, RR5).
- C4. Under ALTERNATE an inheriting subtype keeps its foreign key to its supertype's table; a role played by a value type with a table is a foreign key; an absorbed unary column is nullable (RR6-RR8).
- C5. map_model never raises for a model the loader admits, dispositions has exactly one row per fact type and constraint, and mapping time stays linear, including composite identification (C1, C2, C5, F9).

## The change under review

The work from `af34a54e` to the working tree at `24f284130f1d`. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r2/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r2/diff.patch` | `e88cc2a8dc67ce317385079937a0ffd5101229d10b318e7c00849507a2a4f86d` |
| `.gnd-planning/milestones/ossie-relational-bundle/007-OB2-D5-gate.md` | `769a582738383a1e115b9e41b7becff992afa2669938cc34f63c8f1175e611eb` |
| `.gnd-planning/milestones/ossie-relational-bundle/008-phase-OB2.md` | `34a0b5b97a840bd78f8b65ceb2795fc5a48d3eb231088737de7dac3ae08ae5b0` |
| `.gnd-planning/milestones/ossie-relational-bundle/README.md` | `4853d859e2bc34cf84a2c6a7b55e8eeadb429bbffd94c4c6f8b5ab09f03b0884` |
| `.gnd-planning/milestones/ossie-relational-bundle/evidence/OB2/dynamic-query-successor.json` | `deaa829cc2a4442849fca747d8cbff2fa4a5936a88364981c344a086506aedb4` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/OB2-variant-measurement.md` | `90d7d0d39feb384c427b59911245d16fadb2a6d2d7109f39e909179a270ab36d` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB2-spec.md` | `80ef7b68e6ae0bb9c07590201d8a07c8273e995d2a3018a29eb279e8b8676743` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/BRIEF.md` | `2e2e32ff31a4d2763ed04fb5c65d3c884d860dca60c87735b591fbd32191dfc4` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/FINDINGS.md` | `7d0f36b01140df8ea85d12876b5e4e84aeb6f87cf099825a991e0f1e0a7c534e` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/SANITIZATION.md` | `26941c7f96caefc9e67fce2c3f803d55d25111e2d3b7adf2993e99f6e802bbd9` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/brief.json` | `4710fe89ef610dceceeb55086aa3dd6218e39f933f05cdeaee98153c8838deb5` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/diff.patch` | `392e5bb6c3239cdbf0114e7ec7bf2fd6137adff29bc81dd34f251717f7066ca8` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/review.log` | `62114185b5ee347ea2e5e9388b122fcba883cc2888f782f70ad34935407af7fb` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/review.md` | `8ecc9256423dc0158b32c834b64a0157f3ec9641ab0dbeeff46d9c9469824c93` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB2-r1/run.json` | `572ecbd7851d620478732bdf5b8c9b30f2a6f7dbd470584c87d056c0976d7fec` |
| `dev/components/COMPONENTS.md` | `ee0c9e052475c1c571bf34df5ccdd586645555b43bfec13625ea0c028777b1b9` |
| `dev/components/graph.md` | `dd0249add8bb75d856108d25f4ca67a5987411de89c0476206bd901fe6080299` |
| `dev/components/modules/_root.md` | `f8c9f51cfe00ff73d6e52224dcd322ce8c0a939ea4389ed8882b6c497e1b55bd` |
| `src/gnd/rmap.py` | `414a891733d63d1b5ef4040fc2552e0ab0f04110e89e0f1a79c70d752adbc67e` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `dd67d53b65fdac6f2b53443f39365621f52768d4a57fe2012e5ccb7a6d0f786f` |
| `tests/test_rmap.py` | `5c893a4cc219bed7c8dea00daefa3db48f32173c01dec232c3f8972f0de18d89` |

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
