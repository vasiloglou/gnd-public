# Review brief: a phase's diff

You are an independent reviewer, working in a different tool from the one that produced
this work. Nothing here asks you to agree with it. Answer from the files themselves, not
from any summary of them, including this brief's.

## The question

Does the RP2 diff make the rules programs list every anchored constraint as not checked exactly where gnd check (without a sidecar) does, and nowhere else, without changing any other program output, the checker export, or the Ossie export?

## Claims to test

The author claims what follows. For each, try to show where it is false: a claim is
met only if you looked for the case that breaks it and did not find one.

- C1. RP2-C2: every anchored id is in UNCHECKED and in no compiled requirement
- C2. RP2-C3: on the twelve gold populations of the flat literature model the DuckDB program agrees with gnd check (exit 4)
- C3. RP2-C4: in the DuckDB program a textual rule's printed line is byte-identical to before
- C4. RP2-C5: the rules success line counts listed rules; with none, and for the checker export, the line is unchanged
- C5. RP2-C6: the extended comparator represents not-checked rules on both sides and the negative control fails it
- C6. RP2-C7: the LQP program's lqp_report prints the not-checked lines and returns 4 for a listed must-rule, 0 for deontic; --compile prints them
- C7. RP2-C8: an anchored rule over an empty fact list is not checked, exit 4, agreeing with gnd check
- C8. No existing test's meaning was weakened by the comparator change in tests/test_pyrel_rules.py

## The change under review

The work from `bfcd2e2d` to the working tree at `bfcd2e2d2d40` with uncommitted changes. Its diff is `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/diff.patch`.
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log (not tracked yet, so not in the diff: read it whole)
- new: .gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log (not tracked yet, so not in the diff: read it whole)

## What to read

Paths are relative to the repository root, the directory you start in. Before you rely
on a file, check its SHA-256 (`shasum -a 256 <path>`); if one differs, say so first in
your answer: you are not reading the bytes this brief names.

| File | SHA-256 |
|---|---|
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/reviews/phase-RP2-r1/diff.patch` | `ddbdfe096f91f6bb2b1516d9a586f6d8172070815d83644e5ef2a0b2cf44edca` |
| `docs/explanation/rules-as-pyrel.md` | `567fee8a6e009e831afb81b89cf78ec5f2eaa9a572fd6ad9761a1bd46dc3676d` |
| `docs/runtimes/pyrel.md` | `78e50f2054a7f647c6240627a84ed1946bb9f7755d583b14dddd17ecdc5777aa` |
| `src/gnd/commands/export.py` | `cfafa284b490e3305f631f75036b11e7531e5aa9d495a83e9138008bf74b8644` |
| `src/gnd/export/emit.py` | `9b7c78fbee6b1213347022704de5218ac662ee7fc2679651a3338b9af51f5286` |
| `src/gnd/export/pyrel_rules.py` | `4fcbdfed4bfc6bd5fab6da4a65f915e77c8ae2fb886f0a1b364e47d9ca30f654` |
| `tests/fixtures/pyrel-rules-coverage/rp2/anchored-deontic.orm.json` | `74096f3c852f2c6dd1785fbd1e073008214e7b6985fd86b68f67ce961a473f58` |
| `tests/fixtures/pyrel-rules-coverage/rp2/anchored-only.orm.json` | `fe4eeec8ce640acca14e8dd660b69f39fab434cd5d506b07d3a730dc95948084` |
| `tests/fixtures/pyrel-rules-coverage/rp2/empty.population.json` | `0eb7ec7b25185e8d348bba8c6ddde655efd25c0933459b41f7caea93eaba2754` |
| `tests/fixtures/pyrel-rules-coverage/rp2/full.population.json` | `4d4bf2f86d3f8d30f52e8a08db2ac53cbf657a35a8a2cb56fbd042dafb4ff1ba` |
| `tests/test_pyrel_rules.py` | `2de4d990c67ad806078ada52e324fe5a22af2c19049b313d0fe613b54aa2f77b` |
| `tests/test_rp2_anchored.py` | `1eab19333ca2d3c7d063afe20d1d237f8a707143d51f5496d5682ecd4128e8fe` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR1-r1/review.log` | `29e5bb8e3df4449f059bde94dbd0978425590735c205e106fae0f99f46c272ef` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR2-r1/review.log` | `ad6e15580205508df8f33356314f9f7072521cf01bd493151e42dba41e697b48` |
| `.gnd-planning/milestones/include-root-routes/notes/reviews/phase-IR3-r1/review.log` | `5da792cfb6c988e2a9f21c01ad7f4f2d55010781af2f27579e4e03c156c7a5a5` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/phase-RP2-spec.md` | `d3772935a73b707b9e756a6f5addcddd6674757ffaeb4131971ff5f429d7dc2d` |
| `.gnd-planning/milestones/pyrel-rules-coverage/notes/pyrel-rules-coverage-plan.md` | `9a93f4c2aee127cb0608c4f502740c9e123010df70d6fd1963a4737954ae9434` |

You may read anything else in the repository that helps you answer.

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
