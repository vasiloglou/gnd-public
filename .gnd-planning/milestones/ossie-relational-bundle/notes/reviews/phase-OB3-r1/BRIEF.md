# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the OB3 implementation (gnd.export.ossie_relational, the wiring in gnd.export.ossie and gnd.commands.export, and the Rmap changes E3 and E4) implement the approved OB3 spec (r1 with amendment r1.1, sections 6, 7 and 14) and the normative 'Semantic model and mapping' subsection, and is there any model gnd export ossie admits for which the default run raises, writes a semantic model or mapping the pinned schemas or the documents' own cross references reject, names a field, relationship or concept that is not declared, omits a fact type or constraint from the GND extension, changes the three legacy files, or produces bytes that depend on the run or the source path?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every relational file the export writes validates against the vendored core-spec and mapping.json, with cross-document refs resolved offline; validation never opens a connection.
- C2. Every expression names a declared dataset.field; every link mapping names a relationship declared on its concept (or one it extends) at the level its arity calls for; every referent mapping follows the ontology's identify_by. Where the ontology identifies an object type differently from its key columns, nothing is guessed: the fact type is listed in unmapped_links and the concept in concepts with identification-differs.
- C3. Every fact type and constraint of the model appears exactly once in the extension's dispositions; every carried fact type is named by exactly one link tree or listed in unmapped_links.
- C4. The ontology, sidecar and loss report bytes are identical with and without --ontology-only, and equal the OB1 baseline; a collision on any of the five paths exits 11 and publishes nothing; --max-output-bytes bounds each of the five files.
- C5. The Rmap accepts a composite identifier only when every component binary is functional on the entity (E3 a), and RelationalSchema.roles and .identifications are correct for every carried fact type and identified object type under both variants.
- C6. Quoting and uppercasing identifiers (E5) is one rule over the whole identifier grammar, with no reserved-word list; render time is linear in model size.

## The change under review

The work from `39e3d4c3` to the working tree at `5f6873857ff1`. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB3-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB3-r1/diff.patch` | `44eb540fdad0cd27410f009e507aff7e8b0e1644250cb9740e1756fe8bb760cb` |
| `.gnd-planning/milestones/ossie-relational-bundle/evidence/OB3/dynamic-query-successor.json` | `338ec79ac043db3c05084e42b72e21b1e4be8b0706825898412772a511533521` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/OB3-rmap-measurement-after-E3.md` | `42ac0a7dce19ca5763184806e206d9c0d3e3734ac02bf8303af8a40592fc8f38` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB3-spec.md` | `d7247d6251301e1c9c9badf8d18816bca48e2c2917011e763984545f8efe2e61` |
| `dev/components/COMPONENTS.md` | `1b6a35c22699db7bfbeb1e7edd6f93ce96bc60bb67c2b069fa668c248b9ca80f` |
| `dev/components/graph.md` | `719877448380209f8cac0a005386e141cd213bd8a38e52f4f3b1b4b427947140` |
| `dev/components/modules/_root.md` | `55ac16d307800994ad5548c5df55b2e0676b1b5083eebf6cef3e5c3c4e209731` |
| `dev/components/modules/commands.md` | `eb36505316b05d8a155563827ad3be2dc4242344cde3c415d48db8435f21eb5f` |
| `dev/components/modules/export.md` | `b5760197b7950d38c9a37c0077124a95568a291309d25fc858a7d640d8d6701f` |
| `dev/components/modules/tools.md` | `310b0631ce0714430778f9340ab69db2caa79db2c06d2156f1faafa99083f555` |
| `docs/reference/disclosure.md` | `e7889c3bf66d89ad1dda40e5c87221a1c05d8d00f20695107d9b9e2863d31845` |
| `src/gnd/commands/export.py` | `746f27147042a4cd45d884093e2dcc5700fd8dfa13d8f1bfa427b5a12df26110` |
| `src/gnd/export/ossie.py` | `f1aae1625cb7474aeb090f849d552dd38d65a6a08e7283cae48921a004b65fc9` |
| `src/gnd/export/ossie_relational.py` | `56125b14b9b3b978cd2d54a779fa192cf0db52ec4c522a181cec165ef8dd8d6e` |
| `src/gnd/rmap.py` | `e1cc9b5a0731d07449818aa574c5ecd52bce6aa4c388959dd662c6825da276ed` |
| `src/gnd/schema/ossie/PINNED.json` | `e8c51162cb925bd4ada873d71edd0924483a6d3ce1fbe66f8d33eb6739c38f9d` |
| `src/gnd/schema/ossie/mapping.json` | `936118ca7753676c069d1fa615c8dced7e9a9499ab185cc2ddbe8d1c2d4404f3` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `e94b15ef76556c23086b40d0d9f797ce9e3af7fd8ec4834d39908604c6d104a4` |
| `tests/fixtures/ossie_relational/README.md` | `fbeb0ef9ddea5d2ce7f398ea6eb0b6b12aec0f20c29509a696e5360974357c3c` |
| `tests/support/ossie_relational_corpus.py` | `c013b99b72e9e79a3b79010718b22ae9975394e5985903a9657c19a93c83a102` |
| `tests/support/pyrel_application_successors.py` | `ef9e746b6c8f7dd1135ed72d251c8d7960940e6c889f05084b9e83873d7918aa` |
| `tests/test_ossie_export.py` | `e244b53c8125fe2f36f0290b3f69f9b94bcfb4fd51ecdb97d6b54cf04e7e492a` |
| `tests/test_ossie_external_oracle.py` | `6e789feeab73c07d5de52f7ed169eb29494450f29493b63dc12041b4cffc7293` |
| `tests/test_ossie_relational.py` | `1e58e5977069b28bc7f1356f211e76ba9b74a9b135faee220894884058712218` |
| `tests/test_rf1_cli_pins.py` | `1b695b0a94f045f774c10f4092507e15ffcd0321e99a8e90e6b8d51557fac5e3` |
| `tests/test_rmap.py` | `7aab62ed9a7f3c22b8e749d739a89335e9714ec54103fa1582dcddffc7039ce0` |
| `tools/gnd_layers.json` | `b17d243ee86bcf1c6df4b114efbf4900836c02c5b9f618fdf7a050803985ef15` |
| `tools/ossie_oracle.py` | `7190dd76a08571575054ec7a3cf56fb1d641f6a56b0bc2743a05fbf27e0bc1a8` |

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
