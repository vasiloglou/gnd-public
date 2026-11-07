# ROF1 corpus: text output for redaction and temporal models (issue 112)

The approval instrument for phase ROF1 of the `report-output-fidelity`
milestone (spec: `.gnd-planning/milestones/report-output-fidelity/notes/phase-ROF1-spec.md`,
section 11). It is committed before any implementation. `tests/test_rof1_projected_text.py`
runs every case from this directory (the paths below are relative to it) with
`--format text` and compares stdout and the exit code with the answer key in
`expected/`. This README tells the stories only; the expected bytes are in
`expected/`, not here.

Today a model with an active redaction policy or with temporal terms prints
its projected JSON for `--format text`. The phase makes `check` and
`validate` print the same layout a plain model prints.

## The models

- `models/contacts-redacted.orm.yaml`: customers and their email addresses.
  The `email` role is marked `redact: true`. `has_email` has two alethic
  uniqueness rules (one email per customer; one customer per email).
  `has_nickname` is not redacted and has a deontic rule (a customer should
  have at most one nickname).
- `models/contacts-invalid.orm.yaml`: the same model with a rule that names
  a role that does not exist, so it does not load.
- `models/service-temporal.orm.yaml`: customers with a service level and a
  contact window, both `Duration` roles (calendar days). No redaction. One
  alethic and one deontic uniqueness rule.
- `models/terms-temporal.orm.yaml`: an exact-arithmetic model (residues
  computed by `mod`) with a `Duration` role added. No redaction.

## The populations

- `contacts-fail`: customer `c-1` has two emails and the email
  `SECRET-EMAIL-271828` belongs to two customers, so both `has_email` rules
  fail; `c-1` also has two nicknames (`OPEN-NICK-…` values), a deontic
  shortfall.
- `contacts-pass`: one fact of each kind; everything holds.
- `contacts-ill-formed`: an integer where an email string is expected.
- `service-pass`: one fact of each kind; everything holds.
- `service-advisory`: `c-1` has two contact windows, a deontic shortfall.
- `terms-unchecked`: a ticket with divisor 0, so the `mod` derivation cannot
  be evaluated.

## The cases

Each runs `gnd <command> … --format text` with this directory as the working
directory. `expected/exits.json` lists the exact arguments and the exit code of
every case.

1. **redacted-fail.** `check` of `contacts-redacted` over `contacts-fail`.
   The redacted role's rules fail and say so without any value; the
   nickname rule is advisory.
2. **redacted-fail-unredacted.** The same with `--unredacted`: the values
   the rules mention may be shown.
3. **redacted-pass.** `check` over `contacts-pass`.
4. **redacted-rule-ids.** `check … --rule-ids` over `contacts-pass`: this
   option is refused for a model with a redaction policy.
5. **redacted-ill-formed.** `check` over `contacts-ill-formed`.
6. **temporal-pass.** `check` of `service-temporal` over `service-pass`.
7. **temporal-advisory.** The same over `service-advisory`.
8. **temporal-derivation.** `check` of `terms-temporal` over
   `terms-unchecked`: rules and derivations that could not be evaluated.
9. **validate-redacted.** `validate models/contacts-redacted.orm.yaml`.
10. **validate-redacted-unredacted.** The same with `--unredacted`.
11. **validate-temporal.** `validate models/service-temporal.orm.yaml`: a
    control; temporal terms alone do not change `validate`'s output today.
12. **validate-invalid.** `validate models/contacts-invalid.orm.yaml`: a
    control; a model that does not load has no redaction policy to project.

Controls 11 and 12 pass today and must keep passing.
