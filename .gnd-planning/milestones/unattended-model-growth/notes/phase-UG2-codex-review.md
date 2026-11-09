# UG2 phase diff: Codex CLI review (one reviewer)

2026-11-09. Instrument: one reviewer in a different tool, the instrument UG1 used:
`codex exec --ephemeral --model gpt-6.1-sol -c model_reasoning_effort=xhigh --sandbox read-only`,
prompt on stdin, repository read-only. This is **one reviewer, not a panel**. Subject:
`git diff 8eb4fe60..2518e8fe`.

**This file was edited from the reviewer's output in one way:** the operator's absolute
worktree path was replaced by `<repo>/` (the review-and-record sanitization rule). Nothing
else in the "Reviewer output" section is changed.

**What the reviewer could not do.** Under the read-only sandbox it could not create temporary
files, so it ran 121 tests with capture and caching disabled and reproduced the rest in memory.
Durable publication and record disclosure were not exercised by it.

## Dispositions

Every finding was reproduced by the author before it was believed, and each fix has a
regression test in `tests/test_evolve_population_check.py` shown failing on `2518e8fe`.
Triage follows `review-convergence.md`: blocking and hardening findings on this phase's own
deliverable are fixed in-phase.

| # | Reviewer class | Reproduced | Disposition | Regression test (failed on 2518e8fe) |
|---|---|---|---|---|
| 1 | blocking | yes: op 0 listed as admitted on a violating population | fixed: placements resolved against the final replay tree; a detached object is `not-located` | `test_r1_a_detached_constraint_never_borrows_another_verdict` (`assert [0] == []`) |
| 2 | blocking | yes: `OverflowError` from `popvalidate.py:164` | fixed: `ArithmeticError` mapped to band 3 with a fixed message. The shared numeric validator is not changed here (outside UG2) | `test_r2_a_float_overflow_in_the_population_is_band_3` |
| 3 | blocking | yes: a YAML population exits 3 | fixed: the loader source keeps the file's suffix (`population.yaml`), YAML errors are band 3 | `test_r3_a_yaml_population_is_read_as_yaml` |
| 4 | blocking | yes: 55, 5,050, 500,500 visits for 10, 100, 1,000 (scratch measurement of the old function) | fixed: one identity index per final host list; the test counts visits | `test_r4_placement_lookup_is_linear` (old signature: TypeError; quadratic cost measured separately) |
| 5 | blocking | yes: `[]`, malformed JSON and `other-model.json` each exit 3 at apply | fixed: apply passes the reviewed digest, and a different digest is refused (11) before parsing | `test_r5_changed_population_bytes_exit_11_even_when_invalid` (3 cases) |
| 6 | hardening | yes: the second `service.apply` returned pending | fixed: the option check moved before the retry branch | `test_r6_the_service_retry_branch_checks_the_option` |
| 7 | hardening | yes at the reader (exit 3 for a symlink named `bad-byte cap.json`); not through the CLI at `2518e8fe`, whose path check refused first | fixed: the cap is recognised only by the reader's full sentence naming this exact path | `test_r7_a_filename_cannot_spoof_the_cap_band` (reader leg: `assert 3 == 74`) |
| 8 | hardening | yes: a population outside the workspace exits 74 before a malformed proposal's 3; a stale proposal with `--check-population` and no policy exits 3, not 11 | fixed: the CLI only makes the path absolute (lexically); containment, symlinks and the policy requirement are judged in the service after D-12 | `test_r8a_…`, `test_r8b_…` |
| 9 | hardening | yes: the claim "vacuous is unreachable" (spec F-i7, T4b docstring) is false; `covers: []` reaches it | fixed: a real `vacuous` case added; F-i7 and the T4b docstring corrected | `test_r9_a_vacuous_verdict_leaves_the_refusal` (passes on 2518e8fe: the behavior was right, the branch was untested and the claim false) |

None rejected. The reviewer's "claims checked and found true" are retained below.

## Reviewer output (verbatim, path sanitized)

Found **5 blocking defects and 4 hardening gaps**. No nits. These findings are evidence, not approval.

No files were edited. The read-only sandbox prevented the full suite from creating temporary files. With capture and caching disabled, **121 tests passed**. I also reproduced the findings in memory using real models, proposals, and checker execution, substituting file bytes or staged reads where necessary. Durable publication and record disclosure were not exercised.

1. **Blocking — A constraint can borrow another constraint’s verdict.** [population_check.py:200](<repo>/src/gnd/evolve/population_check.py:200)

   Reproduction: ADD C01’s uniqueness constraint, then MODIFY its whole fact type, reversing the two constraints. Use `violating.json`. The recorder retains the detached, original constraint list and locates the addition at position 1. In the candidate, uniqueness is at position 0 and reports `warning`; position 1 contains the existing value constraint and reports `pass`.

   Observed: operation 0 appears in `population_check.admitted`; only operation 1 retains `fact_types.modify`. The overall proposal remains refused, but the constraint refusal and admission evidence are wrong.

   Minimal fix: resolve identities against the final live replay tree. Detached or replaced objects must yield `not-located`, never a position from an obsolete collection.

2. **Blocking — Hostile numeric input escapes the reader and maps to exit 70.** [population_check.py:127](<repo>/src/gnd/evolve/population_check.py:127)

   Reproduction: change the fixture’s `amount` primitive to `Float`; supply an amount of `10**400` as a JSON integer. This is below the integer-token and byte limits.

   Observed: `read_population_for_check` raises `OverflowError: int too large to convert to float`; `_evolve_error_exit` maps it to **70**, outside the promised input bands.

   Minimal fix: handle this numeric conversion failure with a fixed, value-free population error at exit 3. Prefer making the shared numeric validator total as well.

3. **Blocking — Valid YAML populations are always parsed as JSON.** [population_check.py:116](<repo>/src/gnd/evolve/population_check.py:116)

   Reproduction: serialize `clean.json` as ordinary YAML and supply it as `pop.yaml`.

   Observed: the shared loader accepts those bytes with `source="pop.yaml"`, but UG2 returns exit 3 because it hardcodes `source="population.json"`. Consequently, the hostile `bomb.yaml` test exercises JSON syntax rejection, not the YAML alias guard.

   Minimal fix: retain the supplied suffix in a sanitized source name and sanitize YAML parser exceptions through the same population-error boundary.

4. **Blocking — Placement mapping is quadratic; T13 does not measure it.** [population_check.py:201](<repo>/src/gnd/evolve/population_check.py:201), [test_evolve_population_check.py:524](<repo>/tests/test_evolve_population_check.py:524)

   Reproduction: put N recorded constraint objects in one host list and count objects visited by `constraint_placements`.

   Observed: N=10, 100, 1,000 requires **55, 5,050, 500,500 visits**. Each operation rescans the list. T13 counts `_record_placement` calls, which remain N regardless of this quadratic lookup, so its linearity assertion cannot detect the defect.

   Minimal fix: build an identity-to-position index once per final live collection. Count collection visits in T13 and assert a linear bound.

5. **Blocking — Changed population bytes can return 3 instead of 11.** [service.py:1563](<repo>/src/gnd/evolve/service.py:1563), [cli_service.py:748](<repo>/src/gnd/evolve/cli_service.py:748)

   Reproduction: create a clean C01 preview, then replace the population bytes with `[]`, malformed JSON, or `other-model.json` before apply’s reread.

   Observed: each returns a population error at **3**. Loading and checking happen before the digest comparison, so the promised “population changed before apply” exit 11 is never reached.

   Minimal fix: during apply, compare the freshly read raw-byte digest with the reviewed digest before parsing or checking. Apply this ordering to both the CLI fresh-preview path and the service reread.

6. **Hardening — Service retries bypass option mismatch checks.** [service.py:1835](<repo>/src/gnd/evolve/service.py:1835)

   Reproduction: simulate candidate-already-live reads with matching, schema-validated staged preview and pending state. Call `service.apply(population_preview)` without the option; repeat with a population-free preview and the option supplied.

   Observed: both return `pending-finalization`. The mismatch check is below the retry return. The CLI checks this correctly, so this finding concerns direct service callers.

   Minimal fix: move the service’s presence comparison before the retry branch.

7. **Hardening — A filename can spoof the oversize exit band.** [population_check.py:86](<repo>/src/gnd/evolve/population_check.py:86)

   Reproduction: inject a symlink directory entry named `bad-byte cap.json` into the real artifact-reader inspection.

   Observed: the reader reports **3**, “population exceeds the 10485760-byte cap,” instead of the required symlink band **74**. `_over_cap` searches exception text containing the operator-controlled filename.

   Minimal fix: classify cap failures using a structured exception type or reason, rather than message substrings.

8. **Hardening — Population preflight still violates the specified refusal order.** [cli_service.py:581](<repo>/src/gnd/evolve/cli_service.py:581), [service.py:1334](<repo>/src/gnd/evolve/service.py:1334)

   Reproduction: pass `base.orm.yaml` as the invalid proposal. Without the population option, the actual CLI reports invalid proposal, exit 3. Add `--policy additive --check-population <repo>/.venv/bin/python`.

   Observed: exit **74**, “population crosses symlink,” precedes proposal parsing. Separately, a valid proposal with a stale expected digest returns 11 normally but returns 3 when `check_population` is supplied without a policy. The spec places that new option refusal after candidate validation, replay equality, and D-12.

   Minimal fix: defer the new population preflight failures to the specified service boundary.

9. **Hardening — The declared `vacuous` branch is reachable but untested.** [test_evolve_population_check.py:366](<repo>/tests/test_evolve_population_check.py:366)

   Reproduction: ADD a proposed/deontic mandatory constraint on `customer_places_order`; provide `PLACEMENTS`, mark the host populated, and set population `covers: []`.

   Observed: the policy correctly retains `; population: vacuous`. A guarded constraint with an empty unpopulated antecedent also reaches it. Thus the test’s and implementation notes’ “unreachable” claim is false.

   I additionally changed checker `vacuous` verdicts to `pass` in memory: the existing T4b test still passed because it only exercises `uncovered`.

   Minimal fix: add an actual `vacuous` case with assertions on the refusal and empty admissions, and correct the reachability documentation.

No population-value disclosure defect was reproduced in the exercised preview JSON, text, or invalid-population stderr. No flag-free byte regression was found.

Claims checked and found true:

- All **15 corpus preview cases** matched their expected answers.
- All **12 flag-free preview byte hashes and exits** matched the baseline.
- Missing populated-subject coverage, sample rows, and `neither` modifications retained their refusals.
- Mixed pass/warning operations used the correct operation indexes.
- A passing operation that was never refused was absent from `admitted`.