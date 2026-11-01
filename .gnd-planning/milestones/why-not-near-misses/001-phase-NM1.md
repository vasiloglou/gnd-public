---
milestone: why-not-near-misses
station: phase-NM1
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-NM1
date: 2026-11-01
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py"
  exit: 0
  output: "314 passed in 39.30s"
  note: >-
    The plan section 9 NM1 row, as written. The affected-consumer and inventory
    runs of the spec's verification-selection ledger and the ruff check are in
    the body. evidence/NM1/final-gate.txt holds every command and its exit.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection at milestone close (plan section 9)"
  reason: "outside NM1's impact closure; NM1 changes one module behind a default-off flag that no production caller sets"
evidence:
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM1-spec.md
    sha256: 91f0953d56c0287a2dacd86c2aac5e5323aeec4943402f83ee870bd364ce8ee3
  - path: .gnd-planning/milestones/why-not-near-misses/notes/phase-NM1-claude-review.md
    sha256: 0e63c2f6d429ce138c1a5e3d098a7b91e6faf6f68b00fdb1c5d260812b595381
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM1/dynamic-query-successor.json
    sha256: 059eedc06d2de91ba27aa8073379011ff4f9353375907313ff535bde4e9d0120
  - path: .gnd-planning/milestones/why-not-near-misses/evidence/NM1/final-gate.txt
    sha256: 2c4e5091c9e55b3b97c843c33bdb7a216310b91e70a004d3b8cbc15bf94c07b7
  - path: src/gnd/witness/why_not.py
    sha256: 18220ef96a69895548c2a1c90571a4333a71e5fe72f135f84b92da0e1e64ddf4
  - path: tests/test_why_not_kernel.py
    sha256: b05fce7861eb5287b2178a23e09bc5831db26c436d914f10162498a829189028
  - path: tests/test_why_not_oracle.py
    sha256: 120d8406ba112078decbab49b5a8b09312715211029e0c0be44681996d9106c3
  - path: tests/why_not_oracle.py
    sha256: 61be68f1e8d3f8d4f883b2ac30ffe39ec99e920ce524d5e624951f4436bc5fb0
  - path: tests/support/pyrel_application_successors.py
    sha256: 77a99832d391748453f5d6fdd9ece2ca6113ccd26d1569284346b387be21683e
---

# Phase NM1 -- the near-miss search in the why-not kernel

Spec: [phase-NM1-spec.md](notes/phase-NM1-spec.md), r3, approved by the owner on
2026-11-01 `(s1)` (SHA-256 `e5bec805…c0c0` at approval). The owner chose prose
as the approval instrument, ran no review panel over the spec, and accepted
D3, D4 (a) and D5 (a) as proposed. The spec's implementation findings F1 to F4
were appended after approval and carry no review opinion.

## What shipped

- **`src/gnd/witness/why_not.py`** (+133 / −2):
  - `WhyNotLimits.near_miss_inspections = 200000`. `checked_why_not_limits`
    bounds it like every other field (T20).
  - `explain(..., near_misses=False)` passes the flag to `_Walk`, which keeps
    its own inspection counter. That counter is outside `work`, and one counter
    serves the whole walk.
  - `_normalize` is NFKC, then casefold, then deletion of category `P*`, then
    whitespace collapse; it returns `None` for a non-`str` or an empty result.
  - `_near_key`; `_Walk._eligible`, the shared per-row predicate, with
    `_eligible_rows`.
  - `_Walk._near_misses`: keyed counting over identity groups, with canonical
    minimum representatives. Bindings are inspected first, then rows, and the
    cap is checked before each inspection. It forms at most 5 × 5 pairs per key
    through `_near_miss_pair`, which raises the exactness invariant, then
    applies a global canonical sort and keeps 5.
  - `_atom_blocker` adds `near_miss_count`, `near_miss_truncated` and
    `near_misses` only when the flag is set.
- **`tests/why_not_oracle.py`**: its own `normalize`, eligibility and
  representative rule, plus a brute-force pair enumeration with no keys. It
  still imports nothing from `gnd`. Each blocker also carries the full pair list
  (`all_near_misses`) for the truncated subset rule.
- **Tests**:
  - Kernel literals T1–T8, T10–T12c, T16, T19b, T20, T21, D3 and review R1,
    R2, R3, R5, R7.
  - Oracle comparisons T9, T17, T17b (successor, F2), T18, T18b, T19 and
    review R4, R6.
  - The generator gains `domains=`; its existing parametrization is unchanged.
- **Census**: `evidence/NM1/dynamic-query-successor.json` (26 syntax rows, 32
  occurrences, nothing removed), chained after `WN-merge` in
  `tests/support/pyrel_application_successors.py` (F3).

`src/gnd/witness/view.py`, `service.py`, the API, the CLI and every golden are
unchanged. `git diff 33c260e` over the tracked golden files is empty.

## Gate output (verbatim)

```
$ uv run pytest -q -p no:cacheprovider tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py
314 passed in 39.30s
exit 0
$ uv run pytest -q -p no:cacheprovider tests/test_why_not_repair_loop.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_public_api.py tests/test_public_reference_signatures.py tests/test_rf2_pre_move_pins.py
434 passed in 12.90s
exit 0
$ uv run pytest -q -p no:cacheprovider tests/test_public_built_inventory.py tests/test_public_runtime.py tests/test_v61_phase2_api.py
29 passed, 30 deselected in 0.49s
exit 0
$ uv run ruff check src/gnd/witness/why_not.py tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/why_not_oracle.py tests/support/pyrel_application_successors.py
All checks passed!
exit 0
$ uv run python -c import unicodedata, sys; print(unicodedata.unidata_version, sys.version.split()[0])
16.0.0 3.14.3
exit 0
```

## Measured criteria

| Criterion | Measurement | Threshold |
|---|---|---|
| T18 non-zero blockers over 200 SPELLING seeds | 46 | floor 46 (spec: at least 20; the round-2 reader measured 46) |
| T18b truncated reports at cap 3 | 15, none with a pair | floor 15 |
| Review R4: truncated reports with pairs, caps 4 to 6 | 3 | floor 3 |
| T12b inspections | untruncated at 2n, truncated at 2n−1, for n = 100, 200, 400 | exact |
| T12c pair constructions, 512 × 512 | ≤ 25, count 262,144 | ≤ 25 |
| Unicode database | 16.0.0, Python 3.14.3 | recorded |

## Adversarial review

One reviewer is one reviewer. A Claude subagent read the diff with full
repository access, ran the gates and wrote mutation and fuzz scripts:
[phase-NM1-claude-review.md](notes/phase-NM1-claude-review.md), retained with
machine paths sanitized.

- **Findings:** no blocking finding; 5 hardening and 4 completeness findings,
  all reproduced.
- **Fixes:** every hardening finding is fixed with a regression test, each
  observed red against the reviewer's mutant before the fix was accepted:
  - `reset_counter` → R1;
  - `first_seen_top5` → R2;
  - the non-atom mutant → R3, 7 tests red;
  - `no_b_empty_return` → R7.
- **Confirmed true:**
  - spec conformance of the search;
  - correctness of the global top 5, which the reviewer proved;
  - the exactness invariant: no `WhyNotInternalError` over a Unicode fuzz of
    1500 seeds at caps 1 to 13 (12,439 blockers), with oracle agreement on all
    of them;
  - key equivalence with the per-role pair condition;
  - no charge to `work`, and no truncation at default limits;
  - oracle independence;
  - the successor's predecessor hash.

Own coverage audit against the spec's branch table:
- every Tn row has a test, except T13–T15, which are existing files run
  unchanged;
- each branch of `_near_misses` has a case that can fail it: B empty (R7);
  truncation during bindings (T18b) and during rows (T12, T12b); the
  exact-match raise (T16); the missing-variable raise (D3); per-key top 5 on
  each side (R2, and T12b/R6 against the oracle); the cap shared across blockers
  (R1);
- each branch of `_eligible` has one: a missing role, a constant mismatch and a
  repeated free mismatch (T19b, T7, T10, T19);
- **not covered:** a non-`Mapping` row is unreachable through `explain`, since
  relation rows are mapping proxies.

## Refactoring review

**None needed**, argued from what NM1 touched:

- **Per-row checks.** `_Walk._eligible` repeats three of
  `extensions._joined_atom_candidates`'s per-row checks: the role is present,
  constants match, and repeated free variables are consistent. Sharing them
  would mean parameterizing production's hot join loop, which counts
  `atom_role_terms_read` per role, to skip bound roles for one off-path caller.
  The duplication is pinned instead: T19 compares the two over every corpus atom
  with nothing bound. If a third caller appears, that is the trigger to extract
  the checks.
- **Normalization.** The oracle's `normalize` duplicates the kernel's on
  purpose, as the independence requirement.
- **Census.** The census successor follows the established chain and adds no
  mechanism.

## Boundary -- what this phase does NOT establish

- **Not on a public path.** No public path emits near-misses. Every production
  caller passes no flag (NM-D15), so nothing a user sees changes until NM3.
- **No disclosure behaviour.** The kernel emits raw values, and redaction and
  the disclosure mode are NM2/NM3. NM-R4..R6 do not apply.
- **The normalization's limits.** It is only the stated normalization: no fuzzy,
  edit-distance or locale matching. Its results depend on the interpreter's
  Unicode database, which was measured only at 16.0.0 / Python 3.14.3.
- **Oracle agreement is evidence, not proof.** The oracle and the kernel were
  written by one author from one spec, so a shared misreading of the spec would
  agree with itself. The oracle does not walk descents (the nested T4 blocker is
  a kernel literal), and T12c is not run against it.
- **Relaxed eligibility.** A repeated bound variable is compared per occurrence,
  as the spec allows, so a near-miss row may disagree with itself at those
  roles.
- **No flag-on census of the WN2 golden corpus.** That belongs to NM3, which
  changes those payloads (review R5).
- **Not run.** The broad default suite did not run.
- **One reviewer.** The adversarial review was one reviewer.

## Open questions

| ID | Question | Owner |
|---|---|---|
| NM1-Q1 | F1: the docs must describe the representative as the first in canonical byte order, not the "smallest form". The DC1 draft wording is wrong. | NM4 |
| NM1-Q2 | Review R9: `samples` keeps the first-seen value and `near_misses` the canonical minimum, so one blocker can show `1` and `1.0` for the same group. Should the view align them? | NM3 |
| NM1-Q3 | Review R5 remainder: a flag-on inertness census over the WN2 golden corpus | NM3 |

## Refuted premises

- **F3.** The spec's verification ledger named `tools/gnd_layers.json` and the
  kernel files as T13's input boundary. It did not foresee that
  `tests/test_rf6_query_policy.py` keeps a counted syntax census of new
  subscripts. The census needed an authenticated successor, and its support
  module has a second consumer (`tests/test_rf2_pre_move_pins.py`), which was
  added to the consumer run.
