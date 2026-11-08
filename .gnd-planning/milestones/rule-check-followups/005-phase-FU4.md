---
milestone: rule-check-followups
station: phase-FU4
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU4
date: 2026-11-08
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_public_session_driver.py tests/test_v51_phase2_extraction_scope.py"
  exit: 0
  output: "@@V2OUT@@"
  note: >-
    The plan section 9 FU4 row alone (V2), at @@HEAD@@. The row under load
    (T5), the mutants, the component index check (V6) and the sharded full
    default suite against the base failure list (V3) are in the body.
evidence:
---

# Claim

At @@HEAD@@, neither timing test fails under the six-shard full run for a
reason unrelated to what it guards, and each still fails on its mutant
(issue 117). The driver test's survivor check finds only this test's own
processes, by a literal match on its marker path; the scope walk is timed
by its fastest of 7 runs against a ratio bound of 10. No source file
changed.

## What shipped

- **M1** `tests/test_public_session_driver.py`: survivors are the lines of
  `ps -axww -o pid=,command=` (run with `check=True`) that contain the
  marker path as a literal substring; the marker is named
  `grandchild[alive]+(1)` so a regex-based check would miss it (review R1,
  R2).
- **M2** `tests/test_v51_phase2_extraction_scope.py`: `_timed_scope` takes
  the fastest of 7 runs; the ratio bound is 10; the 5.0 s ceiling stays; the
  comment names the bound a quadratic-regression guard (review R3).
- **Evidence** `evidence/FU4/`: the load probe and its results, the
  unloaded measurements and their scripts, the raw excerpts of the six
  recorded failures.

## Gate output (verbatim)

V2, at @@HEAD@@:

    uv run pytest -q -p no:cacheprovider tests/test_public_session_driver.py tests/test_v51_phase2_extraction_scope.py
    @@V2OUT@@

Mutants (`uv run pytest -q` on the one test each):

    f598ba61, leader-only kill (process.kill() for os.killpg):           1 failed  descendants survived the bound: ['40289']
    f598ba61, quadratic walk (structured = list(...)):                     1 failed  large 1.709 s, small 0.093 s
    regex marker, pgrep check, leader-only kill (review R1, pre-fix):     1 passed  (the hole)
    regex marker, ps check, unmutated:                                     1 passed
    regex marker, ps check, leader-only kill:                              1 failed  descendants survived the bound: ['52102']

@@T5@@

V6, component index:

@@V6@@

V3, full default lane, six round-robin shards on beast-3 (the same run as
T5's load):

@@V3@@

## Criteria

| Criterion | Result |
|---|---|
| FU4-C1 (a): which assertion fails | spec §5 and I4: every recorded driver failure is the survivor assertion matching other tests' processes; the scope walk's single failure kept no message, and its ratio bound is the measured fragility |
| FU4-C1 (b): survivor check scoped before any margin | M1; no time margin was changed |
| FD4: measured margins | M2: ratio bound 10 against measured linear ratios up to 9.65 (unretained) and 6.33 (retained), quadratic 14.3-18.0 |
| FU4-C1 (c): each test fails on its mutant | the mutant table above |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff df5753bf f598ba61`, disposition `revise`, seven findings:
[phase-FU4-codex-review.md](notes/phase-FU4-codex-review.md). R1 and R2
(blocking) were right: the `pgrep -f` check M1 first introduced read the
marker as a regex and ignored `pgrep`'s status; reproduced (a leader-only
kill passed with a regex-hostile marker) and fixed with a literal `ps`
match. R3 and R5 are recorded as boundaries, R6 and R7 fixed, R4 not
reproduced. The repairs carry no review opinion.

## Refactoring review

None needed. Both changes are inside one test each. The phase exposed that
the driver test depended on a machine-wide process listing; no other test
uses `pgrep` (`grep -rn pgrep tests` at df5753bf finds only this one), so
there is no shared helper to extract.

## Boundary: what this phase does NOT establish

- The scope walk's ratio bound guards against a quadratic walk only; an
  n log n or n^1.5 regression passes it (review R3).
- A flake is still possible at a load this phase did not measure: the
  noisiest fastest-of-7 ratio measured is 8.76 (unretained; retained
  maximum 5.86), 12% under the bound of 10.
- R2's half (an erroring process listing) has no separate case; it rests
  on `check=True`.
- One reviewer read f598ba61; the repairs after it were checked by the
  gates above, not re-reviewed.

## Open questions

None new.
