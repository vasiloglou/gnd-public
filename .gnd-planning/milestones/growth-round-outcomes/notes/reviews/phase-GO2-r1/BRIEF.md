# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does every operation of a proposal get a correct outcome from gnd evolve preview --operation-outcomes, with no change to any refusal, exit, preview byte or digest when the option is absent? Find the proposal, refusal or input where an outcome is wrong, a refusal moves, or a value leaks into an outcome.

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. GO2-C1/C7: a candidate-validation refusal writes no preview; the outcome report names every operation, the refused one refused-by-validation and the others unassessed with the gates that did not run; the printed refusal and exit are byte-identical to the run without the option.
- C2. GO2-C2: every verdict word is reachable and correct; a refusal is tied only to the operation that adds or changes the element it names, and dropped-with names exactly the operations that need an element a refused operation adds.
- C3. The collecting D-12 walk (_d12_refusals) reports, as its first refusal, exactly the refusal _enforce_d12 raised before, for every constraint list, including IK2's induced confirmation claims and VG2's sample and common-sense branch.
- C4. GO2-C3/C5/C6: a preview made without the option keeps every byte and preview_sha256; apply refuses an outcome report; apply rebuilds outcomes exactly when the reviewed preview carries them, so an edited row is stale.
- C5. GO2-C4: no outcome row carries a constraint or sample value.
- C6. Every regular expression, string split, slice and special-case branch this change adds handles the whole class of input it is given, not only the examples in the tests and fixtures, and none reads structured text that a parser or an existing reader in this repository already reads.

## The change under review

The work from `81760521` to the working tree at `f7ec03b4d8e2`. Its diff is `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/growth-round-outcomes/notes/reviews/phase-GO2-r1/diff.patch` | `0503db6790bbfedefa3804b2efb72e8f18147a4e8362891b2ec4376284444fe8` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/dynamic-query-successor.json` | `4bdcdb81f2c24663fa1c3a2c898e3d7b737eab68bf26bf81b0da204556d93719` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/query-successor.json` | `e841d5e55b5985149fc201b20e86d3fe5f354b18595de5aef1474fe01587e356` |
| `.gnd-planning/milestones/growth-round-outcomes/evidence/GO2/source-successors.json` | `886abb609c8023521deccbedab39674efdfc192fb1cb1caf6a9a0040b60c7cb2` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO2-spec.md` | `625435615abfd1bc7aea8b7006c569608866d979362d2e973f01000d103c02db` |
| `.gnd-planning/milestones/growth-round-outcomes/notes/phase-GO4-spec.md` | `a30f1e9e27f5d13a7f8c2d7e1791b0fe1c73f4a41ecfaad3e898e189d60cadfc` |
| `dev/components/COMPONENTS.md` | `b84079210fea2ccd054e843fecfa73904fd1adab912c1658ca4898ccfb61d4e5` |
| `dev/components/graph.md` | `1f02818a529cd5cac4d6b0321eb046e3f177a8887c5e7244d3bf313c494fa710` |
| `dev/components/modules/commands.md` | `9503ef7751836634cb9998f4c15b8fd7fa66ab73e62978638d732f534ebb9da5` |
| `dev/components/modules/evolve.md` | `3d89ef3c4f3f5b176230cb0dccbbc26f0d182c510e7d980d4a95c7a3a04c764e` |
| `docs/release-notes.md` | `410d0e1b0d480d4aa49b30d520f5da017baa32d9dd172daa6b32118e0b87f8b1` |
| `src/gnd/commands/evolve.py` | `af25ac4f7cb935a66acc2cea5ac6793f325ca898d0a82160c9f81bb6b8c791a8` |
| `src/gnd/evolve/__init__.py` | `95c2e6a8ae839d7310696f6538b3437c4fe2513709dfd13dea3a604c708a165c` |
| `src/gnd/evolve/cli_service.py` | `4742a1c1158db1371001654eb55c8bd872b3ed87fc388446347415df76db5ace` |
| `src/gnd/evolve/models.py` | `660f3baaa9c38affbaa40b314db7486291ac19c0f02186a8858cc2a176cfdb12` |
| `src/gnd/evolve/outcomes.py` | `0d6afe83fde0c9d820096e0553a7bb4cba2e5a6ccc66156bb6580ed63ec80d68` |
| `src/gnd/evolve/service.py` | `b9a0df3cfca1deb9806a5300f4479ac5c52935f67632855a2300a042ebc9da5b` |
| `src/gnd/skills/gnd-model-evolve/references/evolution-contract.md` | `171195e40ea3a5881c2d587c7b687eb0c6b0eac953556faa161cd5fca5381c81` |
| `tests/support/pyrel_application_successors.py` | `8315922b1ff3bfd57bdc08697e42807af3befa6ae744499aa158a0cf458ab326` |
| `tests/support/rf9_ci_sources.py` | `e845f246df8880c114ab62de2330509eb1bd98227869862017f16aaf81ec8144` |
| `tests/test_go2_operation_outcomes.py` | `dafa77371869c97988c7ef0d37cec286f8fce63ab20db7d74e3d768b35bae445` |
| `tests/test_rf1_cli_pins.py` | `3e5049ce7d2d67cadf24bda41883002380b5f178aaa7d7985f2a18a926ae83c6` |
| `tools/gnd_layers.json` | `691b358db51fc3ceaa9647c0f081fc87441653b2a0402b4a7d13a1a5d668308d` |

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
