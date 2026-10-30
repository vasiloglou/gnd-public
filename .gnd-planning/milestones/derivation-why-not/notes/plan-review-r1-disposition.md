# Plan review -- round 1 disposition

2026-10-30. Owner-selected instrument (plan WN-D8, quoted: "use four local
reviewer agents for the plan and close review, as in recent milestones. Run plan
review round 1 over r1."). The selection names the instrument only. It does not
approve plan or spec bytes or authorize implementation.

## Subjects and limits

| Subject | SHA-256 | Retained snapshot |
|---|---|---|
| plan r1 as reviewed (WN-D8 recorded) | `77928fb29f34589501843e20fe1db945fab550ca15d3e899fc0b20d3bb84cc70` | `evidence/plan-review-r1/derivation-why-not-plan.md.snapshot` |
| WN1 spec r1 as reviewed | `cbc99f2643350c4eea495142abf26a6f8c715642d74dbda01e80538702081f03` | `evidence/plan-review-r1/phase-WN1-spec.md.snapshot` |

The [manifest](../evidence/plan-review-r1/manifest.json) records the snapshot and
reader-note digests. Snapshots keep a `.snapshot` suffix so their relative links
are not read by the repository's reference check. Line numbers in the reader
notes refer to the snapshots.

The four readers started with fresh context, each with the two digests and one
lens. All four verified both digests. They ran concurrently as local model
agents, not as humans or a provider panel. No paid tools or credentials were
used; the only network read was the issue. Probes ran only in the session
scratchpad (reader 1 wrote two probe scripts there; the others wrote nothing).
No reader wrote to the repository.

## Opinions

| Reader | Lens | Verdict | Blocking | Hardening | Completeness |
|---|---|---|---|---|---|
| [1](plan-review-r1-reader-1.md) | correctness against production semantics | request-changes | 3 | 3 | 1 |
| [2](plan-review-r1-reader-2.md) | implementability, pins and homes | approve-with-fixes | 2 | 5 | 3 |
| [3](plan-review-r1-reader-3.md) | protocol, authority, compatibility, privacy | approve-with-fixes | 1 | 6 | 3 |
| [4](plan-review-r1-reader-4.md) | test design, falsifiability, end-to-end demonstration | request-changes | 4 | 3 | 1 |

Total: 35 findings, 10 blocking. R1-F1, R1-F2 and R3-F1 are one defect (the
unavailable-relation outcome), so there are **8 distinct blocking findings**.
None was refuted.

## Coordinator reproduction

| Finding | Check | Result |
|---|---|---|
| R1-F1, R1-F2, R3-F1 | re-ran reader 1's two probes (read first) with `uv run python -I` | reproduced: single- and two-clause `ok` are `unchecked term:div-zero`; the extension mapping is empty with `ok` and `top` unavailable |
| R1-F3 | read `_evaluate_derivations_dispatch` opaque closure | confirmed by reading; not probed |
| R2-F1 | `tests/test_rf6_query_policy.py:29-39` counts `fact_types`/`roles` reads; witness rows are listed in the RF9 allow-list | confirmed |
| R2-F2 | `EXPECTED_PARSERS = 56` (`test_rf1_cli_pins.py:21`), `len(parsers) == 56` (`test_rf5_commands.py:118`), `commands/witness.py:9,26` hard-code three command names | confirmed |
| R4-F1, R1-F4 | `_witness_charge` reads `_WITNESS_TRACE` only (`extensions.py:457-460`); `WitnessLimits` has no probe field | confirmed |
| R4-F2 | spec T13 accepts either outcome and names no bound | confirmed by reading |
| R4-F3 | `_joined_atom_candidates` over `a, a, 1, 1.0, True` | 5 candidates, 3 distinct `_identity_key` values: reproduced |
| R4-F6 | plan WN3-C2 wording | confirmed by reading |
| R2-F5, R3-F2 | `python-api.md:270-274` (witness API returns raw); `test_public_api.py:18-20` (`unredacted`) | confirmed |
| R3-F5 | `test_v61_phase2_api.py:38` pins `__all__`; "seven-function" at `tour.md:29`, `cli.md:108` | confirmed |
| R3-F4 | `src/gnd/schema/witness*.schema.json`; vendored copy in `gnd-export/references/`; no `gnd-induce` packaged skill | confirmed |
| R4-F4 item 5, R1-F7 | `_rule_derivation_negate_unbound` (`_validation.py:4330`) | confirmed |

## Proposed repairs for r2

Each theme lists the findings it discharges. **These are proposals; nothing is
applied until the owner accepts them.**

- **A. Production decides the status, the walk explains it.** Run the
  production exact evaluation over the target's closure first (under a
  charging trace, theme C). If the head is in `unavailable`, return top-level
  `unavailable` with the production reason, binding and `source_relation`. Decide
  `derived` from the production extension (row: identity membership; rule:
  non-empty). Walk only when production says not derived and available; a walk
  that finds no zero step is an internal defect. A relation in `unavailable` is
  never read as empty. Drop clause status `unavailable`. (R1-F1, R1-F2, R3-F1,
  R2-F7, R4-F5, R4-F4.4)
- **B. Fragment closure.** `unsupported`/`opaque-value` when any relation in the
  transitive dependency closure has an opaque cell; body predicates with string
  rules are read as base, as production does; name `iter_derivation_clauses` and
  its root-before-clause `where` order; name the identity (`_identity_token` on
  materialized head values). (R1-F3, R1-F7)
- **C. Work bounds by counters.** A charge-only trace over the production
  pre-evaluation; a probe ceiling (new field or an indexed join bounding probes
  by output); T13 rewritten as deterministic counter tests: an over-ceiling
  fixture that must exit at exactly `joins+1`, an under-ceiling twin, a
  zero-output connected join, a derived-predicate blow-up, and linear growth
  across two sizes; wall time secondary. WN2 gets its own time-bound gate. A
  T15b proves the kernel leaves an active witness trace unchanged. (R4-F1, R1-F4,
  R4-F2, R3-F10, R4-F8)
- **D. A discriminating oracle.** The oracle owns its identity table (booleans
  apart from numbers, `1 == 1.0`) and computes derived predicates by naive
  fixpoint; it imports no `gnd.terms` or `gnd.values` helper (comparisons in the
  corpus use literal operators). Hand-built discriminators: identity
  duplicates, `True`/`1`/`"1"`, disconnected atoms bridged later, constant
  roles, repeated variables. A census asserts each is present. T9 compares the
  full blocker record including samples. Seeds and minimum counts stated.
  (R4-F3, R1-F6, R3-F10)
- **E. One case per branch.** Computed-head `head` step in row mode; both
  `head-bind` sub-branches; derived clause beside a blocked clause; rule-mode
  computed head; each ceiling separately; descent agreement. The unreachable
  "not-fully-bound negated atom" sentence is removed and stated as refused by
  validation. T8 defined over rule-derived rows, with `covers` and semiderived
  fixtures. (R4-F4, R4-F5, R1-F7)
- **F. A payload the host can act on.** Per-role term map
  (`{"variable": "$w"}` or `{"constant": …}`) with a `ground` flag; raw samples
  keyed by role; `"steps_after_blocker": "not-evaluated"`. Descent cycles keyed
  on (predicate, canonical row); WN-D3 re-argued as ground-only versus partially
  bound descent; the plan sentence aligned with the spec. (R4-F7, R1-F5)
- **G. Surface contract.** WN-D4 rewritten with three readings: return raw like
  `api.witness`; `unredacted=False` like `check`; or a new `raw`. A closed
  allow-list view in `witness/view.py` that covers descent, the claimed row,
  reasons and errors, with a no-value-leak test. A new decision on targets:
  one target whose `fact_type` must equal `--fact-type` (else exit 3), or per-target
  results with a combining rule. The kernel's `row` type (typed cells) and
  `relations` precondition (base relations of the reference-bound population)
  pinned. (R3-F2, R3-F3, R2-F5, R2-F6)
- **H. Exit bands.** WN-D5 re-argued with a reading that separates `derived`
  from `unsupported`, and a band for `unavailable` (2 or 4), each with its
  host-loop cost; a why-not sentence in the `cli.md` exit paragraph. (R3-F6,
  R1-F1)
- **I. Pins and homes.** Model reads through `ModelIndex` or `witness.io.roster`,
  with `test_rf6_query_policy.py` in the WN1 gate; CLI pins (`EXPECTED_PARSERS`,
  tree and help goldens for all three interpreters, `test_rf5_commands.py`,
  rf5 handler cases) and `src/gnd/commands/witness.py`; API pins
  (`test_public_api.py`, `test_v61_phase2_api.py`, a new signature case, and an
  explicit choice about the stale tuple in `test_public_runtime.py`); schema home
  decided between `src/gnd/` and `src/gnd/schema/`, with `VENDORED_SCHEMAS` and an
  optional `gnd-export` vendored copy; docs: runnable `python-api.md` block,
  `cli.md` help probe, `zensical.toml` nav, installed-docs example list; one home
  for the stable-API count sentence; release note moved to WN2; `gnd-export` added
  to WN3-C4 and `gnd-induce` noted as not yet packaged; the "eighth function"
  explanation corrected (docs count functions, `__all__` counts names). (R2-F1..F4,
  R2-F8, R3-F4, R3-F5)
- **J. A repair loop that cannot pass vacuously.** WN3's test builds the fact only
  from payload fields plus an explicit extracted table for free roles; runs in row
  mode; asserts absence and the `check` verdict before repair; has two negative
  controls (previous step's predicate; right predicate, wrong bound value); covers
  two gaps in sequence; ends with `witness` exit 0. (R4-F6)
- **K. Protocol.** Blocked-on decision lists made identical in plan §4, spec §1 and
  spec §7; an approval-instrument decision (prose for WN1 with its reason;
  corpus-first for WN2); the per-phase reader marked proposed in §8; r1 digests
  beside the WN-D8 ruling; focused gate commands named; size re-estimated at
  400-500 source and 700+ test lines; T17 replaced by a mechanical denylist test
  whose names come from owner configuration. (R3-F7..F10, R2-F9, R2-F10)

## New owner decisions surfaced

| ID | Question | From |
|---|---|---|
| WN-D3 (re-argued) | Descent: ground atoms only, or partially bound descent | R1-F5 |
| WN-D4 (re-argued) | API value default: raw (as `witness`), `unredacted=False` (as `check`), or `raw=False` | R2-F5, R3-F2 |
| WN-D5 (re-argued) | Exit bands, including `unavailable` and separating `derived` from `unsupported` | R1-F1, R3-F6 |
| WN-D10 | Approval instrument: prose for WN1, corpus-first for WN2 | R3-F7 |
| WN-D11 | Target cardinality: one target matching `--fact-type`, or many with a combining rule | R3-F3, R2-F6 |
| WN-D12 | Schema home (`src/gnd/` or `src/gnd/schema/`) and whether `gnd-export` vendors a copy | R2-F4, R3-F4 |
| WN-D13 | The stale ten-name tuple in `test_public_runtime.py`: fix it in WN2 or leave it | R2-F3, R3-F5 |

## Convergence

The plan's round budget (§8) allows one confirmation round over r2, limited to
the blocking themes (A, B, C, D, I, J), then the stop rule from
`review-convergence.md`. All 35 findings attack r1's original text; none is
self-inflicted, because no repair round has run. A confirmation round therefore
has work to do.

Next action: the owner accepts, amends or rejects themes A-K and rules or defers
the new decisions; the accepted themes are then applied as r2.
