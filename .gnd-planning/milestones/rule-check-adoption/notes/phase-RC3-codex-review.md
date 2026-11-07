# RC3 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 131,106 tokens, exit 0.
- Reviewed bytes: `git diff eac81cf8 4fffa84d -- src tests tools` (implementation commit 4fffa84d; corpus commit 5f860cb4 inside the range).
- The reviewer ran in a read-only sandbox; it reports measuring the comparison itself, not running the repository's suites. The output below is unedited and contains no local path; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

```text
DISPOSITION: revise

ID: B1
SEVERITY: high
LOCATION: src/gnd/baseline.py:43
QUOTE: return address, None if row is None else canonical_json_bytes(row)
PROBLEM: C4a fails for numerically identical facts with different JSON spellings. With a Number object type and an alethic cardinality maximum of zero, base instances `[1, 1.0]` and head instances `[1.0, 1]` produce the same failed rule, but its reported row changes from `1` to `1.0`. The comparison marks it new, counts the old row resolved, and exits 1 solely because the facts were reordered.
FIX: Make the baseline-visible representative of equivalent numeric values deterministic across fact order, and use that same representative in the reported row and its key.

ID: B2
SEVERITY: medium
LOCATION: src/gnd/checking_service.py:520
QUOTE: warnings = [*model.warnings, *population.warnings]
PROBLEM: Warnings from a valid base disappear. Removing `model_id` from the RC3 standing-only base produces a `population:model-id-absent` loader warning, but the accepted baseline report has `warnings: []`. On a rejected base, its warnings are also emitted without a `baseline:` path prefix.
FIX: Include `base_population.warnings` on success and prefix base warning paths on both success and load failure.

ID: B3
SEVERITY: medium
LOCATION: src/gnd/checking_service.py:534
QUOTE: base_checked = (evaluator or checker_module.check)(model, base_population)
PROBLEM: Base evaluation sits outside the head evaluation’s exception handler. With the standing-only fixtures and an evaluator that delegates on its first call but raises on its second, `_run_check_raw` raises `RuntimeError` instead of returning an exit-70 payload. A checker failure triggered by base data follows the same route.
FIX: Catch failures during base evaluation and comparison and return a structured internal-error result.

CONFIRMED:
C1 distinguishes ordinary JSON-distinct rows and counts resolved keys.
C2 standing-only comparison selects exit 0, `accepted`, and `acceptance_ready: true`.
C3 applies the stated alethic and deontic unchecked band rules.
C3a/C3b refusals run before population loading.
C4b declared addresses remain stable across rule insertion; positional addresses carry a text warning.
C5 validation order is as specified; a 2,000-row-per-side comparison measured 0.0038 s.
C6 row-less new failures and mixed or standing row novelty follow the stated rules.
The base digest is computed from the bytes passed to its loader.
codex exit=0
```

## Triage (driving agent, 2026-11-06)

Every finding was reproduced before it was believed; each fix carries a
regression test in `tests/test_rc3_baseline.py`, run against the pre-fix code
and observed failing for the stated reason.

| ID | Class | Reproduced | Disposition |
|---|---|---|---|
| B1 | blocking | yes, in a simpler form than the reviewer's: one item with amount `1` in base and `1.0` in head (a `Number` value, one fact by NS-IDENT-1) gave exit 1, `novelty: new`, new 1 and resolved 1 | fixed: the key compares each row value by identity, so a number is one key however it is spelled (`{"$number": "n/d"}` inside the key only); booleans and strings stay distinct. The reported row is unchanged (it is the checker's version-7 projection); only the comparison changed. Regression `test_b1_one_number_spelled_two_ways_is_one_key`, red before the fix |
| B2 | hardening | yes: a base without `model_id` lost its `population:model-id-absent` warning | fixed: base warnings join the payload's warnings, and base warnings and issues are both prefixed `baseline:` (one helper). Regression `test_b2_base_warnings_are_reported_and_named`, red before the fix |
| B3 | hardening | yes: an evaluator failing on its second call raised `RuntimeError` out of `_run_check_raw` | fixed: base evaluation and comparison fail into the same exit-70 payload as the head's. Regression `test_b3_a_failing_base_evaluation_is_an_internal_error_payload`, red before the fix |

The fixes were not re-reviewed.
