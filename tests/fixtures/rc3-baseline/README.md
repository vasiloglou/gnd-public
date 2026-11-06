# RC3 corpus: `gnd check --baseline` (new vs standing violations)

This corpus is the approval instrument for phase RC3 of the
`rule-check-adoption` milestone (spec:
`.gnd-planning/milestones/rule-check-adoption/notes/phase-RC3-spec.md`, §11).
It is committed before any implementation and fails until RC3 lands.
`tests/test_rc3_baseline.py` runs every case from this directory and compares
the result with the answer key in `expected/`. This README tells each case's
story only; the expected bytes and exit codes are in `expected/`.

Every command runs with this directory as the working directory, as
`gnd check models/graph.orm.yaml populations/<case>.head.pop.yaml --baseline populations/<case>.base.pop.yaml --format json`
unless the case says otherwise.

## Why

A project switching the check on for the first time already has violations.
With `--baseline`, the check judges both the project now (head) and a saved
earlier state (base) under the same rules, marks each violation as `new`
(only in head) or `standing` (also in base), counts the ones the change
fixed (`resolved`), and fails the run only for new ones. It never claims "no
new violations" when either run could not decide a must-hold rule.

## The model

`models/graph.orm.yaml`: components use components, sit in areas, have
owners and ship in releases. Four rules:

- `no_import_loops` (must hold): the uses relation has no loop. Each edge
  inside a loop is one violation row.
- an id-less rule (must hold): no component is in the `legacy` area. It has
  no `id`, so it is addressed by position, `constraints[0]`.
- `should_have_owner` (should hold, advisory): every component has an owner.
- `has_release` (must hold): at least one release exists. When it fails there
  is no row to point at; the rule itself is the violation.

## The cases

1. **standing-only.** `a` and `b` use each other in both runs; head adds
   `c -> b`, which closes no loop. The only violation is old: both loop
   edges are standing, nothing is new, and the run passes.
2. **mixed.** Base has loops `a <-> b` and `x <-> y`; head keeps `a <-> b`,
   breaks `x <-> y` (drops `y -> x`) and adds a new loop `c <-> d`. The loop
   rule fails with two standing and two new edges, so the rule's violation is
   new and the run fails. `x <-> y`'s two edges count as resolved. The legacy
   component `old` is in both runs: that rule fails in head, but only with a
   standing row, so on its own it would not fail the run.
3. **rowless-new.** Base ships `a` in release `r1`; head has no release, so
   `has_release` fails only in head. It has no rows; the rule itself is new,
   and the run fails.
4. **head-vacuous.** Base has `b` in the `legacy` area. Head records no areas
   at all, so the legacy rule has nothing to judge in head (vacuous). Base's
   violation counts as resolved, and the run is inadequate, as a plain check
   of head is.
5. **base-unchecked.** Base records `b`'s area as unreadable, so base could
   not decide the legacy rule. Head is clean, but since one run left a
   must-hold rule undecided, the run is indeterminate, not a pass.
6. **text-mixed.** Case 2 without `--format json`. Each failing line says
   whether it is new or standing, and a closing block names the base, the
   counts, and warns that one key uses a positional address (the id-less
   rule), which moves if a rule is inserted above it.
7. **bad-base.** The base uses a role the model does not have. The run is
   ill-formed, and each problem is reported against the base, not the head.
8. **refuse-derivation.** `models/derivations.orm.yaml` has derived fact
   types. `--baseline` refuses it before reading either population
   (`populations/absent.pop.yaml` does not exist). `--rule-ids` alone
   accepts the same model (RC1's corpus).
9. **refuse-temporal.** `models/temporal.orm.yaml` is refused as under
   `--rule-ids`, before reading either population.
10. **conflict-populations.** `--baseline` with `--populations`: a usage
    error before the model is read.
