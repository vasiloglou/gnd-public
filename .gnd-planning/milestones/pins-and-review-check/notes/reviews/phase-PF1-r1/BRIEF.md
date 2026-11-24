# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Refute PF1's claims: (1) the packaged-skill inventory (EXPECTED_SKILL_FILE_COUNT, EXPECTED_SKILL_NAMES, EXPECTED_SKILL_FILES) is defined only in tests/test_packaged_skills.py, apart from the named distribution-runtime exception; (2) tests/test_inventory_pin_home.py fails for every way a test module can bind one of those names in module scope, and for no other code; (3) no assertion was weakened: each test in the three edited files still checks what it checked before, against the same values; (4) the guard block edit keeps both project.md copies identical and test_gate_guard_list green. Also judge the out-of-spec commit c1ecb8c1 (inline 70 and 18 in tests/test_public_built_inventory.py): is it correct, and are there other inline restatements of the inventory the name guard cannot see?

## The change under review

The work from `04945d39` to the working tree at `c1ecb8c156c2`. Its diff is `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/diff.patch`.

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pins-and-review-check/notes/reviews/phase-PF1-r1/diff.patch` | `81ccf20cfac978a52439224c4c5e144385544f9d32f456c48bc088fffd646f1a` |
| `.claude/skills/process-phase/references/project.md` | `108f227dbd18635b725576b050e118e9adaa6ffa3c6e5393f85aadc4a5e6b749` |
| `.codex/skills/process-phase/references/project.md` | `108f227dbd18635b725576b050e118e9adaa6ffa3c6e5393f85aadc4a5e6b749` |
| `.gnd-planning/milestones/pins-and-review-check/notes/phase-PF1-spec.md` | `56e53126d6962b48f588c7198aad72da3184ec7cead51334e24950cf48d96703` |
| `tests/test_doctor_uninstall.py` | `95964bc20e62394655ad629badbea316d4ca163fef5d82a8bd220e706d493f99` |
| `tests/test_install.py` | `9fbbb5d182efb1f216cf340b0dac6ab4aeb2bc0affbc9e921758403aaf8a02f8` |
| `tests/test_inventory_pin_home.py` | `27d672998dc33455954a34f8fb2b2842a157e545fbc10087a144218af1a2a2f3` |
| `tests/test_public_built_inventory.py` | `ac6cba98edf0aa5766a6251ea081683b66f04076c19107b6192b70f25c8f8cd7` |
| `tests/test_verification_fixes.py` | `0f88507ab2a9d84dd37add178320f14587ba2758153dec5e8962706f9b5e2bcf` |

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
