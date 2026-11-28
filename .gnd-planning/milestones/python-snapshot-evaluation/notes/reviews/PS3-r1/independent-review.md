I'm requesting changes. The negative-evidence and replay core holds up, but two inputs that should be explained as derived come back as "unavailable", and the commit under review leaves two existing tests failing.

**Hashes:** all 25 files matched the brief.

**The tree changed while I was reviewing.** Another session added commit `a2e6f5b9` and an uncommitted edit to `tests/test_why_not_near_misses_public.py`. The `src/gnd/witness/*` bytes did not change. The findings below are about `7c118a72`. My probe scripts went into `/tmp/ps3probe`; I wrote nothing in the repository.

## 1. Findings

**F1 — `src/gnd/witness/why_not.py:277-282, 319-322`: a "not-covered" refusal where the negated relation is derived.**
- **What's wrong:** the new guard lists every negated relation in the target's dependencies that the population doesn't cover. A derived relation never appears in `covers`, so a rule that negates a derived relation always counts as not covered, even when every input under that relation is covered.
- **What you'd see:**
  - The model: `candidate(id)` and `flag(id)` covered; `blocked :- flag(x)`; `eligible :- candidate(x), not blocked(x)`; rows `candidate={a,b}`, `flag={b}`.
  - `api.check_with_extensions` says `eligible` is complete with row `a`.
  - `why_not.explain(...)` on `a` says `derived`.
  - `api.why_not(..., targets=[a])` returns exit 4, `unavailable`, `negative-relation-not-covered`.
- **Why it matters:**
  - Before this change the service returned `derived` here, so the original single-target behaviour has regressed.
  - The public `explain()` and the service now disagree, because `explain()` passes `require_covered_absence=False`.
- **Reproduce:** `/tmp/ps3probe/p1.py`, case P1.

**F2 — `why_not.py:319`: one uncovered negation anywhere marks every derived row as unavailable.**
- **What's wrong:** the guard looks at the target's whole dependency set, not at the clause that actually derived the row.
- **What you'd see:**
  - The model has two clauses: `eligible :- vip(x)` and `eligible :- candidate(x), not blocked(x)`, with `blocked` not covered.
  - For the row `v`, which comes only from the first clause, `api.why_not` returns exit 4 `unavailable`.
  - `api.witness` proves the same row with exit 0.
  - The reported `source_relation` is just the alphabetically first uncovered relation, not the one involved.
- **Reproduce:** `/tmp/ps3probe/p1.py`, case P2.

**F3 — existing tests fail at `7c118a72`.** The `g11-two-targets` golden is now a batch result. `tests/test_why_not_near_misses_public.py::test_t1_census_adds_only_the_version_and_empty_near_misses` still asserts `gnd-why-not/2`, so both of its `g11-two-targets` cases fail. I saw them fail in a serial run (2 failed, 602 passed). The follow-up commit and the uncommitted edit change that test, `test_public_v71_witness_corpus.py` and `test_rf1_cli_pins.py`. So the diff as briefed is incomplete, and those fixes need their own review.

**F4 — test coverage gaps (no failing behaviour shown).**
- The spec asks for an "opaque row" test. Nothing in the new tests covers it, so the opaque branches in `producer.py:122` and `kernel.py:168-169` never run. When I tried `{"$opaque": ...}` in a String role, population validation refused it, so I couldn't reach those branches either.
- No test compares `explain()` against the service's coverage guard, which is how F1 went unnoticed.

## 2. Checked and found true
- **Shared setup:** evaluation runs once per batch (the test counts the calls).
- **Per-target accounting:** each target gets a new budget and its near-miss state is reset. A single target still has the setup work added to its counts, so its result matches the old one.
- **Limit exhaustion:** running out on one target leaves the next target executable (`["refused","derived"]`). Running out during setup marks every target `work-limit`.
- **Single-target compatibility:**
  - One target returns the original envelope, with the same keys; rule mode is unchanged.
  - An empty target list, 257 targets, an unknown key in `limits`, or passing both `targets` and `row_path` are all refused; exactly 256 targets returns a batch.
- **Scalar ceiling:** a 5,000-byte identifier is refused by default, accepted with `scalar_bytes=6000`, and refused at 65,537. The values don't appear in customer mode. The raised ceiling can't leak into the witness lane, because that lane has no public `limits` argument.
- **Correlated two-role negation:**
  - The tested case has one role variable and one role literal (`zone="east"`).
  - The certificate proves the row and replays with exit 0.
  - After adding the blocking row `(a, east)`, witness says `missing`.
  - A certificate forged with the new snapshot binding replays as `invalid`.
- **Other spec cases:**
  - A covered empty relation is proved and replays with exit 0.
  - An uncovered relation gives `uncovered`.
  - A stale certificate is refused.
- **Ungrounded or partial negations:** the producer marks them unsupported. The replay kernel refuses an unbound variable or a missing role as `invalid`. It checks the whole tuple at once, and refuses derived or semiderived negated relations.
- **Code fitted to its examples:** every role value is matched through the role list and the scalar typing, and `$`-prefixed variables are matched the same way the code already did. I found no regex or split over structured text. The `term.startswith("$")` checks are a flat token test, and the literal-role input above exercised them.
- **Tests:** the four focused test files pass (92 tests). Of 604 witness and why-not tests, only the F3 pair fails.

## 3. Not checked
- **Reference inputs during replay:** I only read the code. The producer and the kernel both take the union of `covers` and rows across the candidate and every reference, which is the cautious choice. I built no reference fixture.
- **Opaque-row behaviour:** I couldn't build a valid population with one (see F4).
- **The 691-line JSON schema rewrite:** I only spot-read it.

VERDICT: CHANGES_REQUESTED
