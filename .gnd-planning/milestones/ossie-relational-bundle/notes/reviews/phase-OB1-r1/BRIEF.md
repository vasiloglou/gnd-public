# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does this diff implement the approved OB1 spec's size bounds correctly and completely, and can any legal input make an export or import publish, refuse or round-trip differently from what the spec states?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. Without --max-output-bytes, every census export is byte-identical to the 1926e895 baseline.
- C2. Every artifact the export writes is bounded by --max-output-bytes; above the bound the run exits 3 with ossie:output-size and publishes nothing.
- C3. An invalid --max-output-bytes or --max-input-bytes exits 64 before any read.
- C4. With --max-input-bytes N, gnd import ossie moves its read, YAML guard, JSON decode and loss-size caps to N (2N for loss-size) and keeps the model-size cap.
- C5. input_policy.loads and JSONDecoder keep their 10 MiB default for every other caller.

## The change under review

The work from `a7847f2b` to the working tree at `a7847f2bf736` with uncommitted changes. Its diff is `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB1-r1/diff.patch`.
- new: tests/fixtures/ossie_ob1_baseline.json (not tracked yet, so not in the diff: read it whole)
- new: tests/support/ossie_large.py (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/ossie-relational-bundle/notes/reviews/phase-OB1-r1/diff.patch` | `7eb6a7b43392e1ea39dd8a06fcbd6b6fb6326f1eadc49d0cbab0a525d348a50e` |
| `dev/components/COMPONENTS.md` | `57fb1b0972d9051d9e3dcc366d6302f1a4aa30dfb29f1c73d5734ca743bfd0f4` |
| `dev/components/graph.md` | `16c2c94bf5d5455d16e51fbeb65038d53ffe5bf305711d6f0bd3c6a6294989d1` |
| `dev/components/modules/_root.md` | `605af08337237dd405212a5182e63192b9ef6510cacd147fba366e8545061648` |
| `dev/components/modules/commands.md` | `434218d6e7828ac164fe047be546718f9a21c83e1ac7681617e69113d3e8e091` |
| `dev/components/modules/export.md` | `87e5a4073a192612ac5c8a3b32d787d33c0f57910ae7027aacb793c60ba47500` |
| `src/gnd/commands/_arguments.py` | `69d0943f858d1bdb16b79578a5aaf285e34ad967e66351526d4d55f0415e61ab` |
| `src/gnd/commands/checking.py` | `993f6d4a198a0207f04f55d813fcf3db20f783436526876568529f9a0d5bb4bd` |
| `src/gnd/commands/export.py` | `76a6a1bf27315b9b9266f645dbd57a8dd71cfd30b6e074a5fd99770f5c9a5ae1` |
| `src/gnd/export/ossie.py` | `828a9443bcbb91eeefc5fc52f7a002b381465d5dca3d3247d0fc9f51f869c508` |
| `src/gnd/input_policy.py` | `e6c83e8374eaa1c1b7f290847090d6a9c33cc9440558bcdb2f0e5c54688dde38` |
| `src/gnd/ossie_import.py` | `a7152fc9fe0686c243c747e56fe0b8347cbd34878c4645dc64775688add7262f` |
| `tests/test_ossie_export.py` | `1137a0893c380365c8d87b3b84926ecec08fd9c2df24761012f70a3b510be416` |
| `tests/test_ossie_import.py` | `251f6d613bd72e66d1b23539c1fa7085ce3b273de30d4c1a18e2da1e4344e5a5` |
| `tests/test_rf1_cli_pins.py` | `798f7fc8e8504ac0814907af22c7c2157bd2269fbe49ff43c263b5bd45be5bbf` |
| `tests/fixtures/ossie_ob1_baseline.json` | `2380653ac758335f73d51f48446ea0137a498d7604d4cb4f36c75e3225b02835` |
| `tests/support/ossie_large.py` | `223322bc505b56563d1bc7726a44d63ab9011ed44da6b0ef7aed4f7f3b642f20` |
| `.gnd-planning/milestones/ossie-relational-bundle/notes/phase-OB1-spec.md` | `068f24c4f1368ff0d0c2a5749be953ba1128b58cb1db809465dc1a77c1413824` |

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
