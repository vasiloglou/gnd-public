---
milestone: unattended-model-growth
station: "phase-UG2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-UG2
date: 2026-11-09
gate:
  command: "uv run pytest -q -p no:cacheprovider <43 modules: the UG2 file, the plan §9 UG1 gate, RF1 CLI pins and harness, layering, arch, RF6 packages and query policy, disclosure, packaged-skill pins, documentation tutorials, and every test module importing gnd.evolve or the RF6 successor chain> --tb=short --junitxml=<scratch>/ug2-junit.xml; uv run ruff check src/gnd/evolve src/gnd/commands/evolve.py tests/test_evolve_population_check.py tests/test_rf1_cli_pins.py tests/support/pyrel_application_successors.py"
  exit: 0
  output: "2071 passed in 614.61s (0:10:14); All checks passed!"
  base: "8eb4fe60 (main after PR 143)"
selection:
  - {obligation: "G-phase: UG2 corpus C01 to C11c, implementation tests, review regressions R1 to R9", disposition: run, command: "the gate above (tests/test_evolve_population_check.py, 71 instances)", exit: 0}
  - {obligation: "G-ug1, G-rf1, G-layers, G-arch, G-rf6, G-disclosure, G-skills, G-docs, G-evolve-consumers (spec §8 ledger)", disposition: run, command: "the gate above", exit: 0}
  - {obligation: "RF1 CLI pins under 3.11, 3.13 and 3.14", disposition: run, command: "uv run --isolated --python 3.11|3.13 pytest -q tests/test_rf1_cli_pins.py; 3.14 in the gate", exit: 0, note: "119 passed under each"}
  - {obligation: "G-components", disposition: run, command: "python3 scripts/components_index.py changed --base main --strict", exit: 0, note: "37 files differ; 0 to fix, 0 warnings, 0 to reread"}
  - {obligation: "G-lint", disposition: run, command: "ruff, in the gate", exit: 0}
  - {obligation: "G-anon", disposition: run, note: "UG1's digest-set method (tests/test_why_not_anonymity.py FORBIDDEN, CONTROL, _hits) over 38 inputs: every file changed since 8eb4fe60 and the commit messages; 0 hits; positive control found"}
  - {obligation: "mutation checks", disposition: run, note: "seven scratch mutants on 2518e8fe in a throwaway worktree, all caught; results below"}
  - {obligation: "phase-diff review", disposition: run, note: "one reviewer, Codex CLI; notes/phase-UG2-codex-review.md"}
  - {obligation: "full default lane; -m 'evidence or census'; distribution lane; certification", disposition: cadence, note: "not selected (verification-selection: no explicit owner request)"}
evidence:
  - {path: src/gnd/evolve/population_check.py, sha256: 5c571c8a3d4cf64be8f611425f018dcd7199a8c4b9db365d6f535603cbd119b7}
  - {path: tests/test_evolve_population_check.py, sha256: 7c90b406a42897caaf160aa10368415a6460424eefd890a8fcb0d983ae8328cd}
  - {path: tests/fixtures/unattended-model-growth/ug2/expected.json, sha256: 622a47a65357689f95e773c03a7f21810544808620389cf1b816abdb28a3f2c4, note: "the approved answer key, unchanged since its approval"}
  - {path: tests/fixtures/check-population-cli/expected.json, sha256: f1006c401b3c0062c540cf099747842e5061ebc8963000173d25ae6e5f2bad2a}
  - {path: .gnd-planning/milestones/unattended-model-growth/evidence/UG2/dynamic-query-successor.json, sha256: 22e5da6c7e988b0efc8fa4321df194a8d59c1a997e61b88fa166f86191f0035f}
  - {path: .gnd-planning/milestones/unattended-model-growth/notes/phase-UG2-codex-review.md, sha256: 4f0b3796de61ac62457395b7667d4cc5a0b9dd598244b3195c3c567f80eb2a27}
  - {path: "junit report of the gate run (scratch, not committed)", sha256: f668baca364a0adec5e03c924355770101e920d624ea3dfb997d50fa86fa388b}
---

# Claim

`gnd evolve preview --policy additive --check-population FILE` admits a new constraint, or a
strengthening-only change to one, on a fact type that already has data, when the constraint is
`proposed` and `deontic`, the population in `FILE` has a fact for every populated subject, no
subject carries sample rows, and that constraint's own checker verdict is `pass` (issue 104
item 5, second option; UG-D2 (b)). Every other refusal stays, with `; population: <outcome>` on
its detail. The preview records `population_check` (the file's digest, the candidate's
`model_id`, the operations it admitted). `apply` repeats the option, refuses changed bytes as
stale (11) before parsing them, and re-checks after candidate validation. Without the option
every preview byte and exit equals `8eb4fe60` (the 12-row parity baseline).

Authority: spec r1 approved `(o)` 2026-11-09 ("Approve all as proposed"), corpus approved `(o)`
the same day ("Approve the corpus"). `auto=false`. Not merged; merge needs the owner.

## Gate output

`2071 passed in 614.61s` over 43 modules, exit 0; ruff `All checks passed!`; components
`changed --base main --strict`: 0 to fix. The 15 approved corpus cases give their approved
answers; the answer key's digest is unchanged since approval.

## Mutation checks (author, scratch worktree on 2518e8fe, not committed)

| Mutant | Result |
|---|---|
| M1 clear a refusal on any outcome | 8 failed |
| M2 ignore eligibility (proposed + deontic, strengthening-only) | 2 failed |
| M3 drop the `uncovered` rule | 3 failed |
| M4 drop the `sample-rows` rule | 1 failed |
| M5 drop the `model_id` requirement | first spelling was a malformed mutant (operator precedence kept the check alive; 0 failed); rewritten to disable the whole condition: 1 failed (C07a) |
| M6 apply ignores a changed digest | 1 failed |
| M7 placement takes the first object | 1 failed |

## Review

Instrument: one reviewer in a different tool (Codex CLI, `gpt-6.1-sol`, reasoning `xhigh`,
read-only sandbox, prompt on stdin), the instrument UG1 used. **One reviewer is one reviewer;
this is not a panel.** It could not create temporary files, so it ran 121 tests and reproduced
the rest in memory. Five blocking and four hardening findings; all nine were reproduced by the
author and fixed, each with a regression test shown failing on `2518e8fe` (finding 9's test
passed there: the behavior was right, the branch untested and the spec's claim about it false).
None rejected. Dispositions and the verbatim output (path sanitized):
[phase-UG2-codex-review.md](notes/phase-UG2-codex-review.md). The fixes were not re-reviewed;
the gate above runs over them.

The review fixes moved one RF6 query read (`document.get('fact_types')` in a new helper). It
was removed by routing the host lookup through the service's existing `_find_fact`, so the
counted query metric is unchanged.

## Refactoring review

Refactors EXECUTED, each behaviour-preserving behind the same gates:

- **`ConstraintSubjects`** (`gnd.evolve.policy`): the "subjects of a constraint operation"
  computation moved out of `additive_policy_issues`'s closure into one class, used by the policy
  walk and the population check, so "populated subject" has one definition (standing rule 4).
  MG2's whole policy suite passes unchanged.
- **The replay's placement recorder** is a keyword-only argument of `_apply_declared_operations`
  (default `None`), so the discover caller is untouched.

Seen and deferred (open questions, below): the shared population numeric validator raises
`OverflowError` on a huge integer for a `Float` role (UG2 maps it to 3 at its own boundary only);
`_evolve_service_exit` still maps most `EvolutionError`s by message substring, the pattern that
finding 7 exploited in the new code (UG2 maps its own errors by type).

## Size

Estimate (spec §10): about 300 source lines, 850 test lines. Measured: 747 Python source lines
added and 65 removed under `src/` (the new module 261), 53 contract lines, 777 test lines added
(the UG2 file 739). Source is about 2.5 times the spec's estimate and above the plan's 400 to
650. That is a finding about the estimate: it omitted the CLI and service plumbing for apply, the
review fixes (placement, digest-first, path deferral, cap matching) and the docstrings the
totality and disclosure rules required.

## Departures from the spec, each recorded in the spec's findings

- F-i4: RF1 CLI pins through a successor fixture, not re-pinned goldens; `goldens.sha256` and
  `MANIFEST_SHA256` unchanged.
- F-i5: population errors carry fixed messages and are mapped by type (UG-R6), not re-raised as
  `EvolutionError`.
- F-i6: the family sweep uses subset instead of ring.
- Review finding 8: the CLI no longer resolves the population path; the service judges
  containment after D-12, so the option's refusals follow every proposal refusal, as §6.4 says.

## Boundary

- UG2 only. The `source.documents` locator and span counts (UG3) and documentation beyond the
  contract, the evolve-policy page, the CLI reference and one release-note entry (UG4) are not
  done. Issue 104 is not commented on or closed.
- The 0.2.0 release note's "remains open" sentence describes a published release and is not
  edited; the Unreleased section says the route now exists.
- The admitted constraint is advisory: the guarantee holds relative to the supplied population.
- Not merged, released or certified.

## Open questions

| ID | Question | Target |
|---|---|---|
| UG2-Q1 | The shared population numeric validator (`popvalidate.py`) raises `OverflowError` on an integer too large for a `Float` role; `gnd check` and other readers may reach a traceback | a maintenance fix or the milestone close sweep |
| UG2-Q2 | `_evolve_service_exit` maps refusals by message substring; operator-controlled text inside a message can move its band | the milestone close sweep (refactoring candidate) |
| UG2-Q3 | UG1's test file still imports private helpers from two test modules (UG1 refactoring note); UG2's file does not add to it | owner's choice |
| UG-Q6, UG-Q7 | carried from the plan | owner |
