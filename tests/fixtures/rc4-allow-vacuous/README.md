# RC4 corpus: `gnd check --allow-vacuous`

This corpus is the approval instrument for phase RC4 of the
`rule-check-adoption` milestone (spec:
`.gnd-planning/milestones/rule-check-adoption/notes/phase-RC4-spec.md`, §11).
It is committed before any implementation and fails until RC4 lands.
`tests/test_rc4_allow_vacuous.py` runs every case from this directory. This
README tells each case's story only; the answers are in `expected/`.

Every command runs with this directory as the working directory.

## Why

A rule written ahead of the data it will judge is vacuous: it has nothing
to look at yet, and today the run exits 2 ("inadequate"). A CI gate that
ships rules early then always fails. `--allow-vacuous` says, for the whole
run, that rules with nothing to judge are acceptable: such a run exits 0,
still lists the vacuous rules, and records that the option was used. A real
violation, or a must-hold rule that could not be decided, still fails the
run as before.

## The model

`models/graph.orm.yaml` is RC3's model: a no-loops rule, an id-less rule
that no component is in the `legacy` area, an advisory owner rule, and an
at-least-one-release rule. The legacy rule is vacuous whenever no area is
recorded.

## The cases

1. **vacuous-only.** `gnd check models/graph.orm.yaml
   populations/vacuous-only.pop.yaml --allow-vacuous --format json`. No
   areas are recorded, so the legacy rule is vacuous; everything else
   passes. The run is accepted, the vacuous rule is still listed, and the
   report says the option was used.
2. **vacuous-only-plain.** The same population with `--rule-ids` and no
   option: inadequate, as today, and the report says the option was not
   used.
3. **fail-and-vacuous.** Case 1 plus a loop between `a` and `b`, with the
   option: the loop still fails the run.
4. **unchecked-and-vacuous.** Case 1 where `b` uses an unreadable
   component, with the option: the loop rule cannot be decided, so the run
   is indeterminate, not accepted.
5. **baseline-head-vacuous.** RC3's `head-vacuous` pair (`--baseline`) with
   the option: the base's legacy violation counts as resolved and, since
   the head's only shortfall is the vacuous rule, the run is accepted.
6. **baseline-base-vacuous.** The base records no areas (vacuous); the head
   records them and is clean. The base contributes no violations, and the
   run is accepted.
7. **text-vacuous-only.** Case 1 without `--format json`: the report closes
   with one line saying how many rules were accepted while vacuous.
8. **conflict-populations.** `--allow-vacuous` with `--populations`: a
   usage error before the model is read.
