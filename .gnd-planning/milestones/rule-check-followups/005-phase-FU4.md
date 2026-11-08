---
milestone: rule-check-followups
station: phase-FU4
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU4
date: 2026-11-08
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_public_session_driver.py tests/test_v51_phase2_extraction_scope.py"
  exit: 0
  output: "24 passed in 7.56s"
  note: >-
    The plan section 9 FU4 row alone (V2), at 95dca01d. The row under load
    (T5), the mutants, the component index check (V6) and the sharded full
    default suite against the base failure list (V3) are in the body.
evidence:
  - path: tests/test_public_session_driver.py
    sha256: 25f2a68e7351fd783066de81154ea6ba937e9acba327c6aa9e1211b47c2b2a51
  - path: tests/test_v51_phase2_extraction_scope.py
    sha256: 3860547e9a22771ac4b0de96f03da62ee22761289777f486653a155a106a69e9
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU4-spec.md
    sha256: a8a3d509414c53fe55c58d6ee8ebc81155256c553d7f3a9aa09d7f9b38f4cae5
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU4-codex-review.md
    sha256: 807b7c3ec06dfb73285b3c4179438a9edbdae798b959d55d16dfd948c9625725
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/dist.py.txt
    sha256: 06a4e8518eb6f92b339b9ee82206e1d1a924421e5046bdf2550994a5752b1bff
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/load-95dca01d.txt
    sha256: 188f78707a4277db83e918a4a392a8fa49f20484e2289d2d79af8525f461156e
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/load-f598ba61.txt
    sha256: a32bd8742f772128578b929f4c89e50c402150b29eaef29fe540f678f059b6e2
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/probe-load-df5753bf.jsonl
    sha256: 57173295a2d7e64ffee09f8a1a858f7708796cc6dbee1009bc7c52ac261438e1
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/probe_test_fu4.py.txt
    sha256: 2fe089c795f5d18aadcd7ae447b8aa62675bd383904f182a7b3229981469d521
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/ratio.py.txt
    sha256: c699a1b7ccff750d3148fe7797e92d34a769f4a53921cacc97d8c9859881d862
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/retained-failures.txt
    sha256: 076fc42088a1d2197de3769db232d7da43c9b3bed993c8da9d42e016eaf67550
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/test_fu4_repeat.py.txt
    sha256: cd03c39f4349b3ca43001a2bd33f726f21e799171edf3cc21911b6a7b1cd6dd6
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU4/unloaded-scope-walk.txt
    sha256: b835cf9076012055b4700fed75f9ef98f163e80cf19c5d3442761b85ba04b09c
---

# Claim

At 95dca01d, neither timing test fails under the six-shard full run for a
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

V2, at 95dca01d:

    uv run pytest -q -p no:cacheprovider tests/test_public_session_driver.py tests/test_v51_phase2_extraction_scope.py
    24 passed in 7.56s

Mutants (`uv run pytest -q` on the one test each):

    f598ba61, leader-only kill (process.kill() for os.killpg):           1 failed  descendants survived the bound: ['40289']
    f598ba61, quadratic walk (structured = list(...)):                     1 failed  large 1.709 s, small 0.093 s
    regex marker, pgrep check, leader-only kill (review R1, pre-fix):     1 passed  (the hole)
    regex marker, ps check, unmutated:                                     1 passed
    regex marker, ps check, leader-only kill:                              1 failed  descendants survived the bound: ['52102']

T5, the two real tests 60 rounds each (`evidence/FU4/test_fu4_repeat.py.txt`)
beside a six-shard full run on beast-3:

    f598ba61 (pgrep marker check):     120 passed in 185.56s
    95dca01d (literal ps check):       120 passed in 186.16s

Before FU4, the same load made the driver's old check fail 1 of 60 probe
rounds (spec F1), and it failed in 5 of the recorded full runs.

V6, component index:

    python3 scripts/components_index.py changed --base df5753bf --strict
    changed against df5753bf (df5753b): 14 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    exit=0

V3, full default lane, six round-robin shards on beast-3 (the same run as
T5's load):

    f598ba61: 17852 passed, 2 errors; shards exit 1,0,0,0,0,0
    95dca01d: 17852 passed, 2 errors; shards exit 1,0,0,0,0,0
    failing list at 95dca01d: sha256 8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a (equal to main 6651e5a4's)

The 2 errors are the `tests/test_public_optional.py` uv-version pins.
Evidence: `evidence/FU4/load-*.txt`.

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
