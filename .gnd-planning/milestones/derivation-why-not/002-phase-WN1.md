---
milestone: derivation-why-not
station: phase-WN1
skill: "n/a -- repository development via process-phase under process-milestone auto=true, not a gnd-solve station over a domain model"
scope: phase-WN1
date: 2026-10-30
gate:
  command: "uv run pytest -q -p no:cacheprovider tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_public_v71_witness_corpus.py tests/test_public_optional_value_witness.py tests/test_derivation_rule.py tests/test_derivation_covers.py tests/test_public_derivation_evaluation_complete.py tests/test_public_derivation_parity_local.py"
  exit: 0
  output: "1676 passed, 11 deselected in 482.32s (0:08:02)"
  note: >-
    The literal focused gate of spec §8 plus the T17 anonymity file. Ruff check
    is clean over the new files. evidence/WN1/final-gate.txt keeps the output.
slow_cadence:
  command: "uv run pytest -q"
  trigger: "explicit owner selection or separately configured CI"
  reason: "outside WN1's impact closure; WN1 adds one module and changes no tracked src file"
evidence:
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN1-spec.md
    sha256: 3ccae8e587e799ac77899678df90f02f2a8d1222d56b8bcc5b28a8f1b99a70f5
  - path: .gnd-planning/milestones/derivation-why-not/notes/phase-WN1-claude-review.md
    sha256: bb6492f46341c0dd2b4b3757eaeaf05e5f0c63048902ef5e98ea37ac654c1b1b
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN1/dynamic-query-successor.json
    sha256: fe02b126eeb860964f64fe511b779bc8c4ceea7b4686d1cbd2baae577e2062b3
  - path: .gnd-planning/milestones/derivation-why-not/evidence/WN1/final-gate.txt
    sha256: 6455c99ff712777b8f0730c4c03df85b3d2d59cc3b1c8166557d128339243324
  - path: src/gnd/witness/why_not.py
    sha256: 5f9b6a0732c07c28451f51967acf46d09fe2863f21655619f48c8477f2492f13
  - path: tests/test_why_not_kernel.py
    sha256: d2a32bbd41a162f0c6b5ca5d035940e967a39f4335bec16c2f70be9fe5bf91b0
  - path: tests/test_why_not_oracle.py
    sha256: c0560113a7c66343fe83b87999de5d41ae1a284f359847eadb2ca4f9445b2639
  - path: tests/why_not_oracle.py
    sha256: 39a8555b4576446e5a383181e950a15cb89422a256ec131b519271624291dde0
  - path: tests/why_not_support.py
    sha256: f291735c22f65d16096a95c0ba2559f269dc2250cf390c90fea4cca3f12890a0
  - path: tests/test_why_not_anonymity.py
    sha256: d8c0c0a3a6b2a23d12d5879a7038a62beb872dca6496a8ad81c37f7b4f666975
---

# Phase WN1 -- the why-not explanation kernel

Spec: [phase-WN1-spec.md](notes/phase-WN1-spec.md), r3 approved by the owner
on 2026-10-30 (SHA-256 `78fbfe88…3faa` at approval). The WN1 gate (base commit,
forbidden-token digests, the restated T13 values) was recorded in the spec's
appended section as a **delegated approval (auto=true)** under the owner's
`/process-milestone derivation-why-not auto` request. The spec's implementation
findings F1-F11 and the WN1 residuals were appended after the gate and carry no
review opinion.

## What shipped

- **`src/gnd/witness/why_not.py`** (new, layer `witness`/`lanes`):
  `explain(model, candidate, fact_type_id, *, row=None, references=None,
  limits=DEFAULT_WHY_NOT_LIMITS)` returns a `WhyNotResult`. The status comes
  from production first: the target's dependency closure is pre-evaluated with
  `_evaluate_stratified_extensions(heads=closure, exact=True)` under a
  charge-only trace, so `unavailable` and `derived` are production's verdicts.
  Only a target production does not derive is walked. The walk follows the
  clause in declared order, records each prefix's distinct binding count, and
  stops at the first step that empties it (atom, negated atom, comparison, head
  term, or in row mode a `head-bind` mismatch). An atom blocker reports its
  roles, whether it is ground, up to five identity-distinct samples of the
  bound values, and `asserted_not_read` for a derived predicate with asserted
  rows. A ground blocker over a structured derived predicate is explained
  recursively, up to depth 8, stopping on `not-derived`, `not-ground`, `cycle`
  or `depth`.
- **Refusals before work:** an unknown or non-derived fact type and a
  malformed row raise `WhyNotInputError`; a string rule (`rule-opaque`), an
  aggregate, and an opaque value anywhere in the closure return `unsupported`.
- **Two budgets** (`WhyNotLimits`): `pre_joins` charges production's
  pre-evaluation through the witness charge sites; the walk charges `joins`,
  `probes` and `binding_cells`; `proof_depth` caps descent. A breach raises
  `WhyNotWorkError` carrying the counters. Candidates are deduplicated by
  identity after the charged scan, so duplicate rows cannot multiply uncharged
  work (review WN1-R1).
- **Tests:** `tests/test_why_not_kernel.py` (T1-T8b, T10-T15b and the review
  regressions), `tests/test_why_not_oracle.py` (T9: an AST import ban, named
  discriminators with census properties, a 200-seed generated corpus),
  `tests/why_not_oracle.py` (an oracle with no `gnd` import, its own Fraction
  identity and a naive fixpoint), `tests/why_not_support.py`, and
  `tests/test_why_not_anonymity.py` (T17: digests only).
- **Policy:** `tools/gnd_layers.json` gains `gnd.witness.why_not`; the RF6
  dynamic inventory gains an authenticated successor
  (`evidence/WN1/dynamic-query-successor.json`, 41 rows, chain totals 6800
  distinct rows and 8505 occurrences), appended to `DYNAMIC_SUCCESSORS`.

## Gate output (verbatim)

```
1676 passed, 11 deselected in 482.32s (0:08:02)
```

## Measured T13 values

| Case | Spec | Measured |
|---|---|---|
| (a) 320 rows | `joins` 100,001; cells 199,680; `pre_joins` < 1,000 | as stated |
| (b) 310 rows | counts `[310, 96100, 1, 0]`; `joins` 96,411; cells 192,512 | as stated; `probes` 96,722 |
| (c) zero-output join | `probes` 10,300; `joins` 5,000 | as stated |
| (d) 500 rows | `pre_joins` breach | 200,001 |
| (e) 155 rows | `joins` 24,181 | as stated |

The (b) shape at 310 rows completes inside the 10 s wall cap (asserted).

## Criteria

| Criterion | Result |
|---|---|
| WN1-C1 status first | holds: T1 (four unavailable routes), T7 derived, T14 opaque routes, T8 agreement with `check` over T1-T7, T9, T10 and T14 cases, and the review's 1,894-case probe with 0 mismatches |
| WN1-C2 prefix counts and blocker | holds: T2-T7, both `head-bind` sub-branches, the head-term blocker |
| WN1-C3 independent oracle | holds: T9 named discriminators each assert their property; the generated corpus has at least 150 valid models and 100 blocked targets; samples compared by identity. Residual: non-atom `reads`/`samples` are pinned by T5-T7, not the oracle |
| WN1-C4 descent | holds: T10, T11 (`not-ground`, `cycle`, `depth`); the string-rule stop is unreachable (F2) |
| WN1-C5 budgets | holds: T12 at limit+1 for each ceiling, T13 (a)-(e) with literal values, duplicate-row regression |
| WN1-C6 branch walk | holds: every branch in spec §8 has a case; T1(c) and T11 case 4 are unreachable (F2, F3) |
| WN1-C7 layering and isolation | holds: layer map entry; direct RF6 query rows unchanged; dynamic inventory via the successor (F1); T15b under a derived and a blocked target |
| T17 anonymity | holds: digests only; sub-runs and stripped forms; the planted control passes through the same file listing |

## Review

One local reviewer agent read the WN1 working tree against `f2f83de` and ran
13 probes plus a mutation harness, all under scratch. The report is kept as
[phase-WN1-claude-review.md](notes/phase-WN1-claude-review.md).

| Finding | Severity | Disposition |
|---|---|---|
| WN1-R1 duplicate rows multiply uncharged walk work | blocking | fixed: candidates deduplicated by identity (first kept); regression proven red first |
| WN1-R2 samples deduplicated by canonical JSON | hardening | fixed: identity key, canonical sort; mixed `1`/`1.0` regression |
| WN1-R3 non-finite row values raise a bare `ValueError` | hardening | fixed: `malformed row`; T14 cases for nan and inf |
| WN1-R4 depth precedence off by one | hardening | fixed: the depth stop is checked before `proof_depth`; `proof_depth=8` pinned |
| WN1-R5 branch tests that cannot fail | completeness | fixed for M1, M2, M6, M7, the T8 extension, T15b blocked, limit+1, the wall cap; M11 and two oracle gaps accepted as residuals |
| WN1-R6 anonymity matches whole tokens only | hardening | fixed: sub-runs and stripped forms |
| WN1-R7 model read outside §6.8 | completeness | fixed: `ModelIndex.iter_fact_types_shared` |

Each regression test was run red against the unfixed kernel before the fix.

## Refactoring review

**Executed:** the dependency document is built from the shared `ModelIndex`
snapshot rather than a `model_dump` (R7), matching `_build_incremental_context`.

**Not refactored, argued:**
- **The walk reimplements a join** rather than calling production's
  `_joined_bindings`. Production reorders atoms by connectivity and does not
  report per-prefix counts, which are the whole product. Status, the only
  semantic claim, still comes from production (WN1-C1).
- **`_Walk` is one class** holding the budget, the relations and the descent
  stack; splitting it would thread the same three values through every helper.

## Boundary -- what this phase does NOT establish

- **One reviewer is one reviewer.** The review was one local agent over the
  pre-fix tree. The fixes and the tests added for R1-R7 carry no review opinion.
- **No public surface yet.** There is no CLI, API export or schema; WN2 owns
  them. Nothing here is user-visible.
- **References** (`references=`) are passed through `bind_population` but no
  WN1 test uses them.
- **The broad historical lane did not run** (`slow_cadence`).
- **Timing.** The B24 wall-time check in the witness corpus missed its 10 s
  cap once (10.5 s) under concurrent load; run alone it passes on this branch
  and at the base commit. WN1 changes no tracked `src/` file.

## Open questions

| ID | Question | Origin | Target |
|---|---|---|---|
| WN1-Q1 | Should the oracle compare `reads`/`samples` for non-atom blockers and emit `head` steps? | review R5 | derivation-why-not close |
| WN1-Q2 | Should the "declared order differs" discriminator compute production's order instead of restating it? | review R5 | derivation-why-not close |
| WN1-Q3 | A references case for `explain` | this record | WN2 (the API takes `reference_root`) |

## Refuted premises

1. **"RF6 query policy unchanged, no new query rows"** (spec §6.8, T16). The
   dynamic candidate inventory counts every non-literal subscript; the kernel
   adds 41. Discharged by an authenticated successor (F1).
2. **"A string-rule predicate stops descent"** (spec §6.1 row 6, T11 case 4).
   Validation refuses a structured rule that depends on a string-rule type, so
   the case cannot be built (F2).
3. **"A non-integral head makes the target unavailable"** (T1(c)). A
   non-Integer computed head must use `round`, so the case cannot be built
   (F3).
