# ROF2 corpus: text output for walks, admission and verify (issue 112)

The approval instrument for phase ROF2 of the `report-output-fidelity`
milestone (spec: `.gnd-planning/milestones/report-output-fidelity/notes/phase-ROF2-spec.md`,
section 11). It is committed before any implementation.
`tests/test_rof2_projected_text.py` runs every case from this directory (the
paths below are relative to it) with `--format text` and compares stdout and
the exit code with the answer key in `expected/`. This README tells the
stories only; the expected bytes are in `expected/`, not here.

Today, for a model with an active redaction policy (or, for a walk, temporal
terms), `gnd check --pre … --steps …`, `gnd check … --admission` and
`gnd verify` print a `REDACTION` header and then the JSON report as their
text. Phase ROF1 fixed `check` and `validate`; this phase makes these three
routes print the layout a plain model prints.

## The models

- `models/accounts-redacted.orm.yaml`: customers, their email addresses and
  nicknames. The `email` role is marked `redact: true`; the nickname role is
  not. `has_email` has two alethic uniqueness rules (one email per customer;
  one customer per email); `has_nickname` has a deontic one (a customer
  should have at most one nickname). Two operations: `add_email` registers an
  email (its frame is deontic), and `add_nickname` gives a nickname, but only
  to a customer who already has an email (an alethic precondition).
- `models/service-temporal.orm.yaml`: customers with a service level and a
  contact window, both `Duration` roles. No redaction. One operation,
  `set_window`, adds a contact window; a customer should have at most one
  (deontic).
- `models/dynamic.orm.yaml`: a copy of the `v62-phase2` ticket model, whose
  ticket role is redacted and whose operations change derived fact types.

## The populations and walks

- `accounts-start`: customer `c-1` with email `SECRET-EMAIL-314159` and
  nickname `OPEN-NICK-333333`. Everything holds.
- `accounts-end-missing`: a claimed end state that has `c-2`'s new email but
  has lost `c-1`'s email, which no step removed.
- `accounts-fail`: `c-1` has two emails, one email belongs to two customers,
  and `c-1` has two nicknames.
- `accounts-ill-formed`: an integer where an email string is expected.
- `service-start`: `c-1` with a service level and one contact window.
- `pre-open`, `post-resolved`: the ticket model's start and end states.
- `steps/add-email`: `c-2` registers `SECRET-EMAIL-271828`.
- `steps/add-second-email`: `c-1` registers a second email.
- `steps/add-nickname-unregistered`: customer `c-9`, who has no email, takes
  the nickname `OPEN-NICK-555555`.
- `steps/add-email-stale-digest`: the `add-email` walk pinned to a model
  digest that is not this model's.
- `steps/set-window`: `c-1` is given a second contact window.
- `steps/ticket`: the ticket model's three-step walk.

## The cases

Each runs `gnd <command> … --format text` with this directory as the working
directory. `expected/exits.json` lists the exact arguments and the exit code of
every case.

1. **transition-plan.** Walk `add-email` from `accounts-start` with no claimed
   end state, so GND computes it. Nothing fails; the computed end state is
   shown with the redacted email cells hidden.
2. **transition-plan-unredacted.** The same with `--unredacted`.
3. **transition-full.** The same walk, claiming `accounts-end-missing` as the
   end state: the lost email is a frame finding.
4. **transition-full-unredacted.** The same with `--unredacted`.
5. **transition-step-fail.** Walk `add-second-email`: the state after the
   step breaks the one-email rule.
6. **transition-precondition.** Walk `add-nickname-unregistered` from
   `accounts-fail`: the start state already breaks rules, and the step's
   precondition fails.
7. **transition-refused.** Walk `add-email-stale-digest`: refused before the
   walk runs.
8. **transition-temporal.** Walk `set-window` over the temporal model: no
   redaction policy, and the step leaves `c-1` with two contact windows.
9. **transition-derived.** The ticket walk with its claimed end state: steps
   change derived fact types.
10. **admission.** `check … --admission` of `accounts-fail`: which facts may
    be admitted and which are blocked, and by which rule.
11. **admission-unredacted.** The same with `--unredacted`.
12. **verify.** `verify … --no-extraction` of `accounts-fail`.
13. **verify-unredacted.** The same with `--unredacted`.
14. **verify-refused.** `verify … --no-extraction` of `accounts-ill-formed`.
