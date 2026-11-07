# RC4 diff review (Codex), retained verbatim

- Instrument: one reviewer in a different tool. One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin (codex-cli 0.163.0), 97,228 tokens, exit 0.
- Reviewed bytes: `git diff 4713fc8a 745507dc -- src tests tools` (implementation commit 745507dc; corpus commit 938716c9 inside the range).
- The reviewer ran in a read-only sandbox and ran no suites. The output below is unedited and contains no local path; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

```text
DISPOSITION: revise

ID: V1
SEVERITY: medium
LOCATION: tests/test_rc4_allow_vacuous.py:109
QUOTE: plain = json.loads(run_main(["check", MODEL, "populations/fail-and-vacuous.pop.yaml", "--rule-ids",
PROBLEM: T3 promises to compare a run with no vacuous verdicts, but this population has a vacuous verdict. A regression that changes a clean run’s assurance or output under `--allow-vacuous` would pass T3. The existing `base-vacuous.head.pop.yaml` is a concrete clean input.
FIX: Run both sides of T3 against `base-vacuous.head.pop.yaml` and assert its vacuous count is zero.

ID: V2
SEVERITY: low
LOCATION: tests/test_rc4_allow_vacuous.py:88
QUOTE: SimpleNamespace(new_alethic_fail="fail" in verdicts, undecided_alethic="unchecked" in verdicts)
PROBLEM: T1 ties a baseline’s `new_alethic_fail` to whether the head contains any failure. It cannot test a standing failure alongside a vacuous head verdict, where `new_alethic_fail` is false and the baseline band moves from 2 to 0 with the option.
FIX: Parameterize the comparison flags independently of the head verdicts and add that case.

CONFIRMED: The reviewed band routes change a computed band of 2 to 0 with the option and leave the default call unchanged.
CONFIRMED: Failures and alethic unchecked verdicts retain precedence in the reviewed snapshot, derivation, and baseline paths.
CONFIRMED: Version 15 records `allow_vacuous`; verdicts and counts remain present. Refusals projected onto older versions do not acquire the key.
CONFIRMED: The reviewed baseline comparison excludes vacuous base rows and treats base failures absent from a vacuous head as resolved.
CONFIRMED: A vacuous run accepted by the option takes the uncertified assurance path; the other reviewed paths retain their prior assurance handling.
CONFIRMED: The text line follows the spec’s condition of an enabled option and a positive vacuous count; CLI arm conflicts are checked before model loading.
codex exit=0
```

## Triage (driving agent, 2026-11-06)

Both findings are test gaps, not defects; each was confirmed by reading the
test, and the strengthened test was shown able to fail.

| ID | Class | Confirmed | Disposition |
|---|---|---|---|
| V1 | completeness | yes: `fail-and-vacuous` has a vacuous verdict, so T3 never ran a clean input | closed: T3 runs a clean population (`base-vacuous.head`) and the failing one, asserts neither is band 2, and that the option changes only its own key |
| V2 | completeness | yes: the baseline flags were derived from the head verdicts, so a standing failure beside a vacuous head (flags false, band 2 → 0) was never tried | closed: T1 takes the two flags independently (no baseline plus four flag pairs, 35 cases). A mutant that also cleared band 4 fails 9 of them (checked, then reverted) |

No source changed. The test changes were not re-reviewed.
