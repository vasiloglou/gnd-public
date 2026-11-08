# Phase FU4: timing tests (issue 117)

## 1. Status

**Approved (2026-11-07).** D1-D3 were ruled over r1 (sha256 `80fab151…`,
commit 1120a690) with "Approve as proposed"; the spec prose is the approval
instrument (D3). `auto=false`. Prior status: "Draft r1, awaiting the owner
gate." The measurements in §5 used an uncommitted probe (retained under
`evidence/FU4/`).

## 2. Provenance

- Plan r3 §4 FU4 (FU4-C1), §9 row FU4, FD4 (ruled: widen, measured
  margins, each checked against its mutant); completion predicate 4.
- Issue 117; rule-check-adoption records 008 (RC3), 009 (RC4), 011 (RC6)
  and the close merge-base run.
- Base: main `df5753bf` (FU3 merged).

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| FU4-C1 (a) | first capture which assertion fails under load | §5 (retained outputs, load probe) |
| FU4-C1 (b) | the driver test's survivor check (`pgrep -f "pathlib.Path"`, machine-wide, `tests/test_public_session_driver.py:387-390`) is scoped to the spawned processes before any margin is widened (review P5) | M1 |
| FD4 | widen the scope walk's ratio and ceiling, and the driver's time margins, to values measured under the six-shard load | M2; §5 shows the driver needs no margin |
| FU4-C1 (c) | each test still fails against a mutant that breaks what it guards: a quadratic walk; a leader-only kill | T2, T4 |
| §9 row | the two tests, alone and under the six-shard run | V2, V3 |
| plan §0 rule 2 | every flake reproduced before it is planned against | §5 |
| plan §0 rule 5 | stop past 1.5 times about 20 test lines (30) | §10 |
| §6 risk | a flaky test "fixed" by asserting nothing | T2, T4 mutants |
| AGENTS.md | component index | V6 |

## 4. Goal

Neither test fails under the six-shard full run for a reason unrelated to
what it guards, and each still fails on its mutant.

## 5. What fails, measured (2026-11-07)

**Retained outputs.** Every recorded failure of the driver test on beast-3
(`rc2-shards/final`, `rc3-shards/base`, `rc4-shards/base`,
`rc6-shards/base`, `close-shards/mergebase`) is the same assertion,
line 390: `descendants survived the bound: [n, n+1]`. The one scope-walk
failure (`rc6-shards/final`, shard 0) was run with `--tb=line` and kept no
message, so which of its two assertions failed is not recorded.

**Load probe** (`evidence/FU4/probe_test_fu4.py.txt`, results
`evidence/FU4/probe-load-df5753bf.jsonl`, sha256 `57173295…`): instrumented
copies of both tests, 60 rounds each, on beast-3 while a six-shard full
suite of `df5753bf` ran beside them (17852 passed, the 2 known errors).

- **Driver, F1.** 1 of 60 rounds would have failed. Its three "survivors"
  were another test's processes: `/bin/bash -euo pipefail -c python -c
  "import gnd, pathlib, shutil; …"` and its `python -c` child, in another
  process group, none naming this round's temporary directory. In all 60
  rounds the driver's own leader and grandchild were gone when checked,
  the marker was always written, and `drive` returned within 3.02 s of a
  3 s bound. **The flake is the machine-wide `pgrep`, not the kill or a
  time margin.**
- **Scope walk, F2.** Under load the large/small ratio was 3.98-5.29
  (median 4.71) against the bound 6; the large walk took at most 2.2 ms
  against the 5.0 s ceiling. Unloaded, on the author's laptop, the same
  measurement exceeds 6 often: 200 rounds, median of 7 runs, median ratio
  6.01, 100 of 200 above 6, maximum 9.65; with the fastest of 7 runs
  instead, median 5.54, 72 above 6, maximum 8.76, none above 10. The walk
  times are under 2 ms, so the ratio is dominated by noise and by cache
  effects that make the "linear" ratio 4-6 rather than 4. **The flake is
  the ratio bound 6; the ceiling is never near.**
- **Mutant M-Q (quadratic walk):** `structured = list(...)` in
  `extraction_scope.fact_type_scope` makes membership linear: ratio
  17.85-17.96, large walk 1.76-1.83 s (under the 5.0 s ceiling, so only
  the ratio catches it).

## 6. Design

**Reuse table** (searched 2026-11-07: `grep -rn "pgrep" tests`; the two
test files). No component index entry: both changes are inside tests.

| Capability | Found | Decision |
|---|---|---|
| a per-test identity for the spawned processes | the marker path, unique per `tmp_path`, is in both the leader's and the grandchild's argv | **reuse** |
| a process-group filter | `pgrep -g <pgid>` | **reject** (D1): after the leader is reaped its group id can be reused by an unrelated process under load |

**M1. Driver test, about 3 lines.** The survivor check becomes
`pgrep -f <marker path>`: it finds exactly this test's leader and
grandchild, and nothing another test started. No time margin changes
(F1).

**M2. Scope-walk test, about 3 lines.** The ratio bound becomes 10; the
ceiling stays 5.0 s (F2). Per D2, `_timed_scope` takes the fastest of its 7
runs instead of the median.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Scope the driver's survivor check by the marker path, or by process group as the plan's wording says? | **marker path**: same processes, and immune to group-id reuse after the leader is reaped **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU4's D1–D3?"). |
| D2 | The scope walk: widen the ratio bound only (FD4's letter), or also time it by the fastest of 7 runs? | **both**: bound 10 and the fastest run. FD4's "widen" alone needs a bound near 10 with the median and still leaves the unloaded maximum (9.65) within 4% of it; the fastest run moves that maximum to 8.76. The quadratic mutant (about 18) stays far above 10 either way **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU4's D1–D3?"). |
| D3 | Approval instrument and review over the spec | prose (two small test edits, no format); no spec review **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU4's D1–D3?"). |

## 8. Tests and verification ledger

| T | Case | Expected |
|---|---|---|
| T1 | the driver test, unchanged behaviour | passes alone and under load |
| T2 | mutant: `_run_bounded` kills only the leader (`process.kill()` in place of `os.killpg`) | the driver test fails on the survivor assertion |
| T3 | the scope-walk test | passes alone and under load |
| T4 | mutant M-Q (quadratic walk) | the scope-walk test fails on the ratio |
| T5 | the load probe re-run with M1 and M2's assertions | 0 of 60 rounds fail each test |

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V2 | plan §9 row, alone | run | `uv run pytest -q tests/test_public_session_driver.py tests/test_v51_phase2_extraction_scope.py` |
| V3 | plan §9 row, under load; full suite vs base | run, sharded on beast-3 | failure list equal to the base's (sha256 `8261732b…`); T5 beside it |
| V5 | Codex review of the diff | run | `notes/phase-FU4-codex-review.md` |
| V6 | component index | run at record time | `components_index.py changed --base df5753bf --strict` |

## 9. Out of scope

Other timing tests; a serial test lane (FD4 rejected it); the driver
itself (`examples/drive_session.py`), which F1 shows is correct.

## 10. Size

Plan estimate: about 20 test lines. Stop line (rule 5): 30. Expected:
about 6.

## Implementability sweep (author inspection)

- M1: the marker path is in the leader's argv (the spawner string embeds
  it) and the grandchild's; a leader-only kill leaves the grandchild, whose
  argv still names it, so T2 can fail.
- M2: bound 10 sits between the noisiest measured linear ratio (9.65) and
  the quadratic one (about 18). A flake is still possible at some load
  this phase did not measure; the record will say so.

## 11. Implementation findings

- **I1 (M1, M2 at f598ba61).** V2: 24 passed. Mutants: a leader-only kill
  fails the driver test on the survivor assertion; the quadratic walk fails
  the ratio (large 1.71 s, small 0.093 s).

Recorded after the Codex review (2026-11-08; [review](phase-FU4-codex-review.md)).

- **I2 (review R1, R2: the check M1 introduced was a regex).** `pgrep -f`
  reads its pattern as an extended regex, so a marker path holding regex
  metacharacters may fail to match a survivor, and an erroring `pgrep`
  prints nothing and passes. Reproduced: with the marker renamed
  `grandchild[alive]+(1)`, the `pgrep` check, and a leader-only kill, the
  test **passed** while the grandchild ran. The check is now a literal
  substring over `ps -axww -o pid=,command=` with `check=True`, and the
  marker keeps the regex-hostile name as the regression case: unmutated it
  passes; with a leader-only kill it fails (`descendants survived the
  bound`). The R2 half (an erroring process listing) is structural
  (`check=True`) and has no separate case. D1's meaning (match by the
  marker path) is unchanged.
- **I3 (review R3).** The ratio bound is a quadratic-regression guard, not
  a proof of linearity: n log n (about 4.7) and n^1.5 (about 8) pass it,
  as n log n passed the old bound. Stated in the test comment and the
  record boundary; the test name is kept.
- **I4 (review R4, not reproduced).** The RC2 final run does hold the
  driver failure (`beast-3:~/rc2-shards/final/shard3.out:43`); the
  repository summary of that run did not list it. The raw excerpts of all
  six recorded failures are now retained:
  `evidence/FU4/retained-failures.txt`.
- **I5 (review R5).** The load probe recorded the leader PID but not the
  grandchild's; F1's "the driver's own leader and grandchild were gone"
  means only that none of them appeared among the `pgrep` matches. T5
  (the real tests under load) is the independent check.
- **I6 (review R6).** §5's unloaded figures (200 rounds; median 6.01,
  maximum 9.65; fastest run maximum 8.76; mutant 17.85-17.96) were author
  observations from 2026-11-07 and were not retained. A retained re-run on
  the same laptop, quieter (2026-11-08, `evidence/FU4/unloaded-scope-walk.txt`
  with its scripts): median estimator median 4.76, maximum 6.33, 3 of 200
  above 6; fastest run median 4.63, maximum 5.86, none above 6; quadratic
  mutant 14.29-15.75. Bound 10 holds against both sets.
- **I7 (review R7).** The milestone README was stale.
