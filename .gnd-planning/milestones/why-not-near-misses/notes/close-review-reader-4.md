# Close reader 4 -- test falsifiability and docs accuracy

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`. The reader ran every mutation in throwaway
`git worktree` copies under `<scratch>/close-review/reader-4/`, removed them
afterwards, and checked everything against eb9839a.

**Verdict: approve.** The one docs error is not blocking; two hardening items,
none holding the close.

Baseline: the 7 milestone test files gave 368 passed; the docs runner groups
`why-not` and `disclosure` gave 4 passed.

## Findings

**1 (hardening, documentation; reproduced). The tie rule in `why-not.md` is
wrong.** The page said identity-equal values show "the one that comes first in
canonical byte order (`1.0` before `1`)". The code and the oracle take the
canonical minimum of the whole projection, so which spelling wins depends on
the other values and the role names; compared alone, `1` sorts before `1.0`.
`two_step("dst", [("a","num"),("z","code")], rows=[{a:1,z:"ACME"},{a:1.0,z:"ACME"}],
src_rows=[{a:1.0,z:"Acme"}])` shows candidate `{"a": 1, "z": "ACME"}`; with
roles `n`/`m` it shows `1.0`. Deterministic for both row orders. T21 covers
only the `n`/`m` layout.

**2 (hardening; by reading). `test_t15_every_row_has_a_discharging_case`
cannot fail on the property it names.** Every branch of its classifier returns
a key of `CASES`, so `assert group in CASES` is a tautology; only the existence
of the named tests is checked. The rows are discharged by T16, T19/T20,
T22-T26 and T30-T33 (mutations B1-B9).

**3 (hardening; reproduced). Mutation B14 is not caught.** Removing
`'GND_DISCLOSURE'` from the env scrub in `tools/run_tutorials.py` left
`test_disclosure_mode.py` green (66 passed). T37/T38 cover the pytest process,
not the runner.

**4 (completeness; by reading).** `test_t3_g20_raw_reports_one_spelling_near_miss`
asserts on the committed golden, not live output; anchored by T5 and
`test_public_why_not` T1, which caught M1, M2, M14 and B10. Not vacuous in
combination.

**5 (completeness; by reading).** The release note "Child processes receive
`GND_DISCLOSURE=customer` only under `customer`" is loose: `_run_child` in
`gnd solve` inherits `os.environ`, so an ambient `internal` reaches stations.
`disclosure.md` words it precisely ("passes nothing").

## Docs claims run from scratch (all matched at eb9839a)

- `why-not.md`: the `--raw` blocker JSON on `spelling-gap.pop.json` matched
  byte for byte; the default-limits ceiling argument holds.
- Refusals: empty `GND_DISCLOSURE` with `--disclosure customer` exit 3;
  `customer` with `witness-view --raw` exit 3, empty stdout, one stderr line; a
  malformed variable on `codegen` ignored (exit 0); `GND_DISCLOSURE=internal`
  with `--disclosure customer --unredacted` exit 3.
- API: under `customer`, `api.why_not` returns `view: redacted` and
  `near_misses: "redacted"`; unset returns raw, no `view`, `gnd-why-not/2`.
- Runner: changed expected outputs in `repair-a-missing-claim.md` and
  `disclosure-mode.md` made the runner fail, so shown outputs are falsifiable.
- Table: dropping a row from the `disclosure.md` table is caught (B6).

## Mutations

45 run, 44 caught. Highlights: M1/M2 (view drops or leaks `near_misses`) by
`test_public_why_not` T1[g20]; M4 (`forward` passes internal) by T30-T33;
M5a-f (each normalization step) by the T1 table; M7-M23 by T11-T25 and the
oracle; B1-B4 (each spawner stops forwarding) by T30-T33; B6 by
`test_page_table_equals_the_code`; B10-B18 by T4-T18, goldens and the oracle.
B14 (runner keeps the ambient variable) was the one not caught. The declared
branch tables in the NM1-NM4 specs each have a failing case under mutation,
except the runner scrub.

## Dispositions (author, at close)

- 1: fixed in `docs/reference/why-not.md`: the pair shows the projection whose
  canonical encoding comes first; the whole projection is compared, so the
  winning spelling can depend on other values and role names. The wrong
  example is removed.
- 2: fixed in the test: the registry check now also asserts every `CASES`
  group is reached by some row, and a comment states that the discharge is
  shown by the named tests. The tautology is acknowledged; the discharge
  evidence is the named tests plus this reader's B1-B9.
- 3: fixed: `test_close_r4_the_tutorial_runner_scrubs_an_ambient_variable`
  runs a one-block page through `run_pages` with `GND_DISCLOSURE=customer`
  set. It fails with the scrub entry removed (B14 re-run) and passes with it.
- 4: accepted as is (anchored in combination).
- 5: fixed in `docs/release-notes.md`: under `customer` children receive the
  variable; otherwise GND adds nothing and a child inherits the caller's
  environment.
