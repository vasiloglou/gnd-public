# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the OB4 implementation (gnd.export.physical_binding, its wiring in gnd.export.ossie, gnd.export.ossie_relational and gnd.commands.export, and the generalized gnd.rmap records) implement the approved OB4 spec (r1 with amendment r1.1, sections 6, 7, 12 and 13) and the normative 'Physical binding' subsection? Is there any binding file, of any bytes, or any schema-valid binding with any admitted model, for which gnd export ossie --physical-binding raises anything but a BindingError with a rule id from RULE_ORDER (or the model's own refusals), reports a later rule while an earlier one applies, writes a semantic model or mapping the pinned schemas or the documents' own cross references reject, maps a role to the wrong columns, omits a fact type or constraint from the listing, or changes any output of a run without the flag?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. read_binding is total over arbitrary bytes, and bind over any schema-valid document and admitted model: only BindingError with a RULE_ORDER rule id is raised, never another exception.
- C2. The checks run in RULE_ORDER, and within a rule the first violation in sorted order is reported, so the message does not depend on the document's member order.
- C3. The semantic model is the binding's tables: datasets sorted by name, fields in document order, keys as given, one relationship per group of equal references with columns paired in table column order, relationship names unique. With no unique_keys member, each confirmed alethic uniqueness bound in one table that is not the primary key becomes a unique key.
- C4. Every role of a bound fact type is mapped from exactly the columns the binding lists, in the entity's identification order; a table.column string is resolved by lookup and never split; role names match by the D8 normalization and nothing else does.
- C5. Every fact type and constraint appears exactly once in the listing with the disposition the normative table states; the Rmap is not run; binding_sha256 is the digest of the file bytes.
- C6. Without --physical-binding every output is byte-identical to main before OB4 (the OB2 and OB3 corpora and the census baseline), and with it the ontology, sidecar and loss report are unchanged.
- C7. The SQL type map is closed and its lexer states the whole grammar it accepts; anything else leaves datatype absent and is never a refusal.

## The change under review

The work from `ba192972` to the working tree at `a8a411300e2c`. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB4-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB4-r1/diff.patch` | `965fd1801fb6396854d7043b07d2c62ae268ad2aedc937caacda0eb5b966b7cf` |
| `.gnd-planning/milestones/ossie-relational-bundle/evidence/OB4/dynamic-query-successor.json` | `39216295f458db0204f76f43ce0415e6acf5cfa4c511b13ad26834fe05053bb5` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB4-spec.md` | `773ba8048166149dd5efc4b5bd8fed7ef46838b972d6fcaf9e20746a2430db79` |
| `dev/components/COMPONENTS.md` | `1272d07a7d849fbf16868bf7a647306a580402bce9c049d7cf67ac860a55ddbe` |
| `dev/components/graph.md` | `d4593bc2e2a5eb96abf2cbf432011dc787fcdbc7af02c40874e8277044efa2b8` |
| `dev/components/modules/_root.md` | `ce95917e9b5879ce9666b3209ad9011661cd8f380baaf1a9887d5573fbc95f0d` |
| `dev/components/modules/commands.md` | `294955cce306fb4bb9dd3d07fe14a5c85eea70176fa471481a93b287341b0f3d` |
| `dev/components/modules/export.md` | `d0c4dbc7a1088d0f75e8c4b192d7281919db49b226d61426d4a08a06ecd2899e` |
| `docs/reference/disclosure.md` | `0691101e8dee674003289534a71d74771f6ab20129e59358aadd6f6b1ad714f9` |
| `src/gnd/commands/export.py` | `33aa22361392eb4bc354b2637bd6425ba2cd6c63d44d8065947ac1d34fa49590` |
| `src/gnd/export/ossie.py` | `08ae0a6bd9673a2e2ec09d1243ccf5df87d64c12d14851f7579fa394e13ecdc3` |
| `src/gnd/export/ossie_relational.py` | `3764698dc7dbc2d3cbd13b29bc7fdb94647a15bb663ce00cb752fc8cf295a18b` |
| `src/gnd/export/physical_binding.py` | `def29fe817347db0c2b7e570e4d2ab2dd4c45a47960413c7d8a138622c518505` |
| `src/gnd/rmap.py` | `35b5ed171bb1ad9bfe070c9ad7be3743b897cbb29a5093ad5fb7e8025d24a176` |
| `src/gnd/skills/gnd-orm-core/references/representation-format.md` | `6a8231a02d448304a56a951eeadbc6ae56be951ebf0a04733a89923e852ef806` |
| `tests/support/binding_large.py` | `b3b686d744f5e85aa0a948f00533870605a6896200ccac7350d1e96412f7d4d6` |
| `tests/support/model_scan.py` | `6a5c0f1c3b5a3d8f838c370cda39adc8982165c86d95e63d9c4dc4d811b9b519` |
| `tests/support/physical_binding_corpus.py` | `e84ae331cfd338a0eb64e866477c0a0a08bf5193efabeb03fe4fd2a052f8eb13` |
| `tests/support/pyrel_application_successors.py` | `7e6df6a48dbea243ead29b1189fddf805bdd9cc9386b98c5feea9aa838cccddb` |
| `tests/test_ossie_external_oracle.py` | `47a482acdc2d734420d8434be41b81ca1e8dbf18c81073b6d77f8aa8f9309295` |
| `tests/test_ossie_relational.py` | `f4a5211570ac2fe55690758d3f2c479603a62fdd8b2c44b03e07c1e2de94f957` |
| `tests/test_physical_binding.py` | `0d74191d1b8f405f17bfc17bfda91ffd3ed3feca5a8ca3f788396e26f02cface` |
| `tests/test_rf1_cli_pins.py` | `09985455e0ab5e156bf541be7d4236d1f9aa1efacf79560688be0808c6d1bf67` |
| `tests/test_rmap.py` | `bf21c53ef117a8c963bbd569310faef48b03fc548e93340e25b0675f23be7ab6` |
| `tools/gnd_layers.json` | `2b714aa3a24277fbd2cf75ee357b30b74155976bca6228bfbc812cccba7c73cb` |
| `src/gnd/schema/physical-binding.schema.json` | `5640b691db86a4a197a0832de83207ab5f78f15053f35be6d225e1263eac9066` |
| `tests/fixtures/physical_binding/README.md` | `e8d33f22ed75ff8ca9a2266234d5192334f890f9111b11fb17579e39dd90d3e0` |
| `tests/fixtures/physical_binding/refusals.json` | `156ecd58e882b023ced39faa1a1c38d74bd0d86ea3e047dba02f4bb7d774bd31` |

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
