# The smoke corpus -- owner-approved answer key, authored before the runner

This corpus is the **approval instrument** for v4.0 Phase 3 (owner decision
D-P3.1, corpus-first). It was authored, narrated and committed **RED** before
`src/gnd/archsmoke.py` existed: at its commit every evaluator case fails for
exactly one reason -- there is no runner to import.

## How to read it

Each directory under `cases/` is one self-contained story:

- `case.json` -- the id and the **story**, in prose. Read these first; they are
  what the owner approved.
- `architecture.contract.yaml` -- a loader-valid contract that drives the case.

`base/` holds the shared project the harness copies in: `app.py`, whose
subcommands are the only behaviour any case needs, and `seed.txt`, a relative
fixture that resolves only when cwd is the project root.

`expected.json` is the answer key: per case, the expected status of every row,
the substrings its failure message must contain, and any assertion beyond the
row itself (fresh tmp dirs, no surviving descendants, a bounded capture).

## The two negative controls are the point

A corpus of passing cases proves nothing about a runner that never runs
anything. Two cases exist to red on purpose under a named mutation:

- **S-08** -- make `run_row` return the declared band without spawning. S-03,
  S-06 and S-11 must all go red. If they stay green, the corpus cannot tell a
  working runner from a green-by-accident one.
- **S-14** -- empty the parametrization while the contract still declares rows.
  `test_smoke_declares_rows` must go red, proving the non-vacuity guard is not
  itself vacuous.

## The case the milestone exists for

**S-11.** The row declares `expect_exit: 1` and names an entry point that does
not resolve. Measured on this host, `python -m <missing>` exits 1 -- so a runner
that compares exit codes calls this a **pass**. It must be `did-not-start`, and
that status must never be compared to a declared band. Every other case is
support; this one is the defect class the panel found and the design answers.
