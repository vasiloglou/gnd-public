# Close reader 1 -- near-miss correctness

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

**Verdict: approve**, with two hardening findings and one completeness
finding. Nothing blocking: the exactness invariant held throughout;
near-misses never changed status, blocker, counts, `work` or exit; no path
exits 4 from the search; ordering, the count/list tie, schema validity and
redaction held on every generated input.

## Findings

**F1 (hardening, reproduced with the CLI). A near-miss `sample` can show `1`
where the binding was introduced as `1.0`, against the "1.0 before 1" display
rule.** `src/gnd/witness/why_not.py` `_join` (`merged.update(right)`) overwrites
a bound variable with the joined row's spelling; `_near_misses`' `add()` takes
the canonical minimum only across bindings that are still distinct, so
spellings that meet inside one binding are never compared. Fuzz seed 352:
body `r1(c0=$x0), r0(c0=$x1, c1=$x0), r0(c0=$x1, c1=2)`, facts
`r1:[{c0:1}]`, `r0:[{c0:"SS",c1:1}, ...]`, `--row (h0 = 1.0, h1 = "ss")`.
Observed sample `{"c0":"ss","c1":1}` (exit 0); the docs' rule and the test
oracle give `{"c0":"ss","c1":1.0}`. Display only; the committed corpus never
reaches it because its Number domain never mixes `1` and `1.0`. A related case
(two `src` rows `n:1` / `n:1.0`) shows the spelling depends on row order through
first-wins binding dedup, which the oracle copies, so its agreement there is
not evidence. Fix: state in the docs that the sample spelling is the
binding's own, or take the canonical minimum over every spelling that met each
binding, and add a mixed-Number corpus case.

**F2 (completeness, reproduced). The docs do not say the inspection cap is
shared by the whole request.** One counter serves every clause and descent
level (`why_not.py:293`, `:623-627`), as the NM1 record says; the docs say
only "its own ceiling of 200,000 inspections". A two-clause rule with
`near_miss_inspections` 2 or 3 gives clause 1 `(1, false)` and clause 2
`(0, truncated: true)`; at 4 both are `(1, false)`. Acceptable behaviour (a
lower bound; default limits cannot reach it); the docs need the sentence.

**F3 (hardening, from reading). The whitespace rule is wider than Unicode's.**
The code uses `str.split()`, which also splits on U+001C to U+001F (not Unicode
White_Space), so `"a\x1fb"` near-matches `"a b"`. The oracle uses the same
`split()`. Fix: name the definition in the normative text.

## Checked and sound

- Differential fuzz: 1,500 seeds, 3,000 runs, rule and row mode, against the
  oracle and the reader's own invariants, with mixed string and number domains,
  constants, repeated variables and descents. 2,230 blocked runs, 240 blockers
  with a non-zero count (21 inside descents). No internal error, no exactness
  raise; output with the flag, minus the three fields, equalled output without
  it every time; list length `min(5, count)`, canonical order, no duplicates;
  `roles` exactly the differing bound roles, each with equal `N`; no non-string
  or empty-`N` near-match; fields only on atom blockers. The only oracle
  mismatch was F1.
- Schema and redaction through the public service: 3,000 results in both views
  validated with 0 errors and no exit 4; no population or row string leaked in
  redacted clauses at any depth; `near_misses` is `"redacted"` at every depth.
- Inspections stay at or below `probes` at default limits, so the default cap
  is unreachable. Truncation: stopping in the bindings gives count 0 with the
  flag; stopping in the rows gives a lower bound; reaching the cap exactly does
  not set the flag.
- The `quoted_claims` spelling-gap example matches the docs.
- `tests/why_not_oracle.py` imports nothing from `gnd` and counts by brute-force
  pairs; it copies the normalization and first-wins dedup (so it is not
  evidence on F1 or F3).
- `tests/test_why_not_oracle.py`, `test_why_not_kernel.py`,
  `test_why_not_near_misses_public.py`: 212 passed.

## Dispositions (author, at close)

- F1: docs fixed. `why-not.md` now says that within one binding a value keeps
  the spelling of the row that last joined it. Changing the kernel to compare
  every spelling that met a binding is left as a residual (display only).
- F2: docs fixed: one ceiling serves the whole request.
- F3: docs fixed: whitespace is what `str.split()` splits on, including
  U+001C to U+001F.
