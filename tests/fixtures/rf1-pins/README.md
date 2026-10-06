# RF1 characterization pins

This corpus pins the behavior that the code-refactoring milestone's later
phases move or re-route. A pin says that the behavior did not change. It does
not say that the behavior is correct. The spec is
`.gnd-planning/milestones/code-refactoring/notes/phase-RF1-spec.md`.

This file tells the stories and carries no expected values. The answer key is
`goldens/`, captured mechanically from base `e834c6e` and bound by
`goldens.sha256`. It lives apart from this file so that the stories can be read
without seeing the answers.

## Files

| File | Holds |
|---|---|
| `cases.json` | Every input the pins use, as typed descriptors (`json`, `float`, `bytes`, `deep_json` and so on) |
| `inventory.json` | Each surface that RF2–RF8 name, mapped to RF1 nodes, existing tests, or the phase that owes its pins |
| `mutations.json` | The seeded mutations that prove each pin can fail (RF1-C1) |
| `goldens/` | The captured observations, one canonical JSON file per lane and key |
| `goldens.sha256` | The manifest of `goldens/`; its own digest is fixed in `tests/test_rf1_pin_harness.py` |

## The stories

- **CLI.** Every one of the 52 parsers is walked. Its structure, its help
  text, and what happens on `--help` and on an unknown flag are recorded,
  together with every exit-code constant and map in the package.
- **Helper families.** Each site in each family is called on the same inputs:
  ordered and nested objects, non-ASCII text, NaN and infinity, decimals,
  integer keys, a pydantic model, path strings with traversal and backslashes,
  and small trees with symlinks. Its output or refusal is recorded per site, so
  two variants that look the same but behave differently stay visibly apart.
- **Semantics.** The two primitive-resolver readings are told apart by
  non-boolean flags. The datetime sites read one set of edge-case timestamps.
  The checker runs over every model and population pair in the fixture corpus,
  in process and through the CLI in text, JSON and admission form, plus the
  transition, batch and anchored arms; a coverage check requires every
  constraint type to be seen both satisfied and violated, except `textual`,
  which is never evaluated. Verbalization, extraction, diff, assurance blocks
  and the synth oracle are recorded over the same corpus.
- **Agent runner.** A fake executable succeeds, fails, floods each stream,
  vanishes, hangs, and prints a secret; a fake adapter does the same through
  the invocation path.
- **Sessions.** For each contract version 1–8, one session is run from scratch
  with an agent that misses on the first attempt and succeeds on the second
  (tests-mode, v3, has one attempt). Each completed run is then resumed with
  its result removed; v7 and v8 are also reconstructed; versions 0 and 9 are
  refused. Evidence is normalized by the rules in
  `tests/support/rf1_pins.py`, and each fresh run is repeated to prove that
  normalization leaves nothing undeclared.
- **Layering.** Every known wrong-way import pair leaving the model,
  checking and semantics layers is a strict expected failure, and no new
  wrong-way pair may appear in any layer.

## Interpreters

Some goldens depend on the Python minor version: argparse layout, stdlib
JSON and datetime messages, the `mimetypes` table, and pytest's own banner.
Those are stored once per minor version (`*.py311.json`, `*.py313.json`,
`*.py314.json`). Under any other minor version they are skipped with a stated
reason.
