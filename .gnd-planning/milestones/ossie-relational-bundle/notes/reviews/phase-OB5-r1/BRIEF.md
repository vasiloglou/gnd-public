# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Do the OB5 changes (the Ossie explanation, the two how-to pages, the gnd-export skill section, the release-note section, the README, index and CLI reference mentions, tests/test_ossie_docs.py, the packaged example binding, and the quoting fix in gnd.export.ossie_relational with its changed corpus answer) meet the approved OB5 spec (notes/phase-OB5-spec.md, with gates 017, 018 and 019)? Is any sentence on a page false against the code or the normative sections 'Relational mapping (Rmap)' and 'Ossie interchange' of representation-format.md, is any rule stated on a page that those sections do not state, does any shown command or output differ from a real run, and is there a table or column name for which the exporter writes an identifier the Ossie normalized-identifier rule (core-spec expression_language.md; the measured class in notes/OB5-oracle-lane-run.md) would not match?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Every statement on docs/explanation/ossie.md, docs/how-to/share-an-ossie-ontology.md, docs/how-to/describe-delivered-tables-for-ossie.md, the Ossie section of src/gnd/skills/gnd-export/SKILL.md and the release-note section is true of the code at this commit; check each against the source and the normative sections, and name any that is false, overstated or stated nowhere normative.
- C2. The pages state no rule of their own: every rule id, reason, limit and exit code they mention is stated in the normative sections, with the same meaning. Look for a rule said twice in different words that could drift.
- C3. tests/test_ossie_docs.py can fail: a page naming an unknown binding: or ossie: id, an Ossie flag missing from the skill, the CLI reference or the normative section, or a wrong exit number in the release note each fail it. Read each new regular expression and string test there as a claim about its input class, build a legal input the tests lack, and report a wrong result.
- C4. is_regular_identifier and _quoted in src/gnd/export/ossie_relational.py write, for every table or column name a model or a schema-valid binding can produce, the identifier Ossie's validator normalizes the declared name to: uppercased for a regular identifier, as written otherwise. The independent restatement normalized() in tests/support/ossie_relational_corpus.py agrees with it on every name. Build names the tests lack (empty, one character, mixed scripts, case-changing-length characters, keywords in other cases) and report any disagreement.
- C5. The quoting fix changes no output for a name that is a regular identifier, so every OB2, OB3 and OB4 corpus answer except physical_binding/V2/expected.mapping.yaml and the census baselines are unchanged, and binding:name-collision still refuses every pair of names the exporter would write as one identifier.
- C6. The packaged example src/gnd/examples/refunds/physical-binding.json is a correct binding of the refunds model, the how-to describes it truthfully, and no public text names a downstream project, customer or reporter.

## The change under review

The work from `6758d224` to the working tree at `b304e3b4d4b8`. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB5-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB5-r1/diff.patch` | `d356aba2e039eb3874eb25089fa3955b56f96c96777154aca2ecbfb5c4786385` |
| `.gnd-planning/milestones/ossie-relational-bundle/017-OB5-spec-gate.md` | `59baca4c3fcdc7d1187aa3eae1366acca45765f1a506e31f3318a233fd79deb1` |
| `.gnd-planning/milestones/ossie-relational-bundle/018-OB5-checkpoint-gate.md` | `da7e038dd745697b5bafba9907370c87ede4d3bf61e1345b2b0d22dbcac23d71` |
| `.gnd-planning/milestones/ossie-relational-bundle/019-OB5-quoting-gate.md` | `842bf7efedb87b6d87977f52f3788c62da1056ed09d3ade684b43cfc3ca73151` |
| `.gnd-planning/milestones/ossie-relational-bundle/README.md` | `ec818713a884fcb50d3f100d3a5b7cf87e9fc789215b25e87405834de9c821ce` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/OB5-oracle-lane-run.md` | `81bc060db5c92be1c8358814873e1f92c89557091e8d7dcf96cdccf29bab1209` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB5-spec.md` | `7f6eea49e4d8d4906c63e2abff34cdf55a5065c3180cae3ebfc034567de35215` |
| `README.md` | `c326e980aee8e67b6413054e1e38c5801bd4618fb7b3c3a121a78c0a86233d12` |
| `dev/components/COMPONENTS.md` | `279d6e294be4a9bf4d5d3e8a528fdaac42b1848588e1e8b151b0bdf070047c04` |
| `dev/components/modules/export.md` | `dfc9c9c762bd11345febda89833d450fab95040d635d8e57f671c63816dee452` |
| `dev/components/modules/tools.md` | `dc49eb1cbbfa148ad6dd5a814f335ab2fe266b74a27175df822d620f17a62acb` |
| `docs/agents/evolve.md` | `f8d97b9a5ce859cf2f6ecd68093d6328611dcc513ffaab801ab670f7d25ffdff` |
| `docs/agents/model-from-text.md` | `338a01bd5ba52dc73cc668f52793f33ab5de0f07f2761af1dff0b18ba74180b5` |
| `docs/explanation/ossie.md` | `58f6fbed3920298a727b33a534ca5d422006be633448a8725adf13b87174191f` |
| `docs/how-to/describe-delivered-tables-for-ossie.md` | `817976d939649c8e7828d392719d52d7f2c628c9e722a274f2eb40a98f94697a` |
| `docs/how-to/share-an-ossie-ontology.md` | `9005100af91bef89fc03efc585a99ce72e69f4281dcda999163fd32f5329648a` |
| `docs/index.md` | `7b044b4fde0166bcd7c830289f27ac3795a4ba50b8b70ebbbca334ca1f622707` |
| `docs/reference/cli.md` | `88bd6bb953e237b0fe95460c9cb0a84eea1033af19e109230bddf216e832a1d2` |
| `docs/release-notes.md` | `75b7539a71de6ee639e8c4e28900308797979940518c6ce67dc40b6c3cbbd24f` |
| `src/gnd/examples/refunds/physical-binding.json` | `74b253fa1abdb66334283c0dbf2d1070c7db204e0a08f3641a964eac7f66cc6b` |
| `src/gnd/export/ossie_relational.py` | `bf41736815e75f0ad5be7a5190e83ae80e39892b43dd7c13f736b3a5e5d79f8a` |
| `src/gnd/skills/gnd-export/SKILL.md` | `16cf80a5c045f8d67de6ccd7484bbf80683cbeacef5bd83774e7710340bb2478` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `45284f8111733277947d571dec574da72a93da02763f3e477a01f97a3a011d0b` |
| `tests/fixtures/physical_binding/V2/expected.mapping.yaml` | `1afa9b12d5ed20f83a69dc26940651abd100f026c4b239dcb308f0c54d50b199` |
| `tests/support/ossie_relational_corpus.py` | `8f874e497211ac8e01254602e724cbfe73404e4362d1713f59bd2346706fea6c` |
| `tests/test_documentation_tutorials.py` | `2bf430f0947746a36f4cebb5933e27a9e2ba5c346776e2e32152e5d84683e267` |
| `tests/test_ossie_docs.py` | `a365792734f7844079b57d07ba8344c7a59a5028a0842f284047ca8b7318dbbd` |
| `tests/test_ossie_external_oracle.py` | `5bac878064f6273513731210d03f199cf1233a8d8b08963339d6a72c015a138c` |
| `tests/test_ossie_relational.py` | `2359997630be700398307d4a3f724fab6963045446e44b4165498bba3e00f286` |
| `tests/test_physical_binding.py` | `3a828722fa601197c754ad689da77a5f6da1046a65fb1f6564f4ea8f47b88cbb` |
| `tools/ossie_oracle.py` | `05c16866cd2666385428c475112a1bea3a9f8107ca5188468cada43bdea42f5d` |
| `tools/run_tutorials.py` | `10d42c6b750e37715ac8c300793f069edffed91d238a34c72ca1f1a5141154cd` |
| `zensical.toml` | `aceb16144e67d1566b040f792d4fc754a224c8d6e22334ccb9251a7007b72402` |

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
