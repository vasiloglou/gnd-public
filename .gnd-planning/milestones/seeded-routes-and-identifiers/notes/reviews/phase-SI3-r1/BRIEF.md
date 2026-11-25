# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Can native, relational or sidecar identity of a unit reference or inheriting multi-supertype subtype be refuted?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Exactly the 17 approved model ontologies change, with first-parent and authored-name collision controls.
- C2. The mapped links close by 8 unit and 5 multiple-supertype cases, retaining 4 objectification links and 2 concepts.
- C3. The selected upstream validator and parser admit the outputs in both formats, and bound CLI import restores the source model.

## The change under review

The work from `b6722aee` to the working tree at `813987524a4b` with uncommitted changes. Its diff is `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/diff.patch`.
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/mapping-census.txt (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/observed-ontology-digests.json (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/reviews/phase-SI3-r1/diff.patch` | `c93c78fa7b5635575d906598ed1ef7efc073f54cd5ed47f0e0c3f776b3e31e54` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/01.json` | `6fe2525e8aec64846cfbf5ae7b5221a9b5b0a028702edde8b18c27ee84beaede` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/02.json` | `4903fe7150bce5343fde628402478f4bb820548ac95870acd13c132b1f87c015` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/03.json` | `8b4d14a9f93d4309a2591f50d03ece3350c36151192e56c09addfe5acdd1f654` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/04.json` | `1393dfcd54ed1c8c5ca1f8e97a2328f694c57815cbcb0c01186e98bd6c7cbdb7` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/05.json` | `d2a5005be4119222532929f157d444b820cfe13afa5780163486c7acb32ec7d5` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/06.json` | `c0e1c96d5379d201a34e58f1bddda8b6cf91d8872c6aba1a2f36ef818f6c9ac7` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/07.json` | `9f848181e59d7953db726802772d865c7c7484bf604ac4e54ef53cf8b4c542df` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/08.json` | `330d9d1dc4c3ef18ccdbebc742735f0b2603c6918f32a3dbc6dd78c00e92eb4e` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/09.json` | `34aec2ef9894996dfdb368358557fe2161c14c936977b85521a21154d5914874` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/10.json` | `e01f6c2881ddade20b7e3343f9ed53d2ba1423826b515c44f1cc887786221ffe` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/11.json` | `2417cd96729e1d4576c34f1e2fd67b5128cc45ce9e1168b037171c0b62aeb7d2` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/12.json` | `bdc6b86573c41c20dee528c1f991a408cf12fd77063d3aee56c9d7229e615e5a` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/13.json` | `8b4d14a9f93d4309a2591f50d03ece3350c36151192e56c09addfe5acdd1f654` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/14.json` | `4903fe7150bce5343fde628402478f4bb820548ac95870acd13c132b1f87c015` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/15.json` | `73cd099f6e3fa28236d9d242576ff435d769a074bacdf78638f08f55a97d3f10` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/16.json` | `1393dfcd54ed1c8c5ca1f8e97a2328f694c57815cbcb0c01186e98bd6c7cbdb7` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/expected/17.json` | `73cd099f6e3fa28236d9d242576ff435d769a074bacdf78638f08f55a97d3f10` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/ontology-corpus.json` | `ba2964bb757ad645340cd870b4e848cd1d17af92fc7af97b14b373de7541bb62` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/oracle-preimplementation.json` | `deedd1c5d2a2751e83183cd3726390593cff91cd11b9a9bff4a47a5fb0a5ab22` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/notes/phase-SI3-spec.md` | `0c5a972d51fc5a4c2a1a597ba3371356ef8668f5f86303df12767bcc29131797` |
| `dev/components/modules/export.md` | `34c2fa855c1aeb58caed40e857855600b92d72228f79e3d6e8a6519cbb706e00` |
| `docs/explanation/ossie.md` | `bce9d33e059b5abe1b1bfa2843b6e27149c70972ef5ce4a3a33d8993a49f2110` |
| `docs/release-notes.md` | `d3273aadb5f63b48534ad539f5ff3332a3698ad36c911b3c3c3a33a1d7d14711` |
| `src/gnd/export/ossie.py` | `9e6b8a1f02d117f7f565d01a7dbbe4c1973c8d818912ca00c69eade4be4cfada` |
| `src/gnd/export/ossie_relational.py` | `693ecbc7088b39d715dd4aa4e64c1f4f7b20bfb8080a145f79ef64c39c7c3455` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `25771b0d9d9d6173736abf8f7dbbec04d572c248112cf21259cb9804e1dbed14` |
| `tests/test_ossie_relational.py` | `f63db073d6d1f4ac45e385b9a0b0dd0acb3381a307104e7a5f77f5037d9a5bec` |
| `tests/test_si3_ossie_identifiers.py` | `db873c6ddef39ea3cab7f097125a5ac3187c710d09585fe07e12e965a4ff87b3` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/mapping-census.txt` | `6a22c1c255a947fec93e752989d8c10bbf5655c805d53daa09593fa6e4155899` |
| `.gnd-planning/milestones/seeded-routes-and-identifiers/evidence/SI3/observed-ontology-digests.json` | `c45327dd9434a48adca912f7469a52ae909ae8495f9b54ebae0be9333db6ff33` |

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
