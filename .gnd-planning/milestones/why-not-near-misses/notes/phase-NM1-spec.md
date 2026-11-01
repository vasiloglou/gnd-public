# Phase NM1: near-miss search in the why-not kernel

**Status: r3, approved by the owner 2026-11-01 `(s1)`; implementation in progress.**

`(s1)` Owner approval, 2026-11-01, quoted: "approved", in answer to "Do you
approve the NM1 spec as proposed?", whose accept button read: "I approve the NM1
spec r3: prose as the approval instrument, no review panel over it, and D3-D5 as
proposed. Go ahead and implement NM1." Approved bytes: SHA-256
`e5bec805cc092558e57e9114e1aa2762440b310bffb5a4ecd9b6bcdb727dc0c0` (before this
tag). Rulings: approval instrument prose; no spec review panel; D3, D4 (a) and
D5 (a) as proposed; D1 and D2 as ruled in the plan; go-ahead to implement.

## Provenance

- Plan: [why-not-near-misses-plan.md](why-not-near-misses-plan.md) r3, §2.1 and
  §4 NM1.
- r1 of this spec was read in plan review round 1 as SHA-256
  `e3855ca569e890a994f015b64f5c64c651f2416f7b4e7b499ec529737913b670`; r2 in the
  confirmation round as
  `1b739a57ce49f7418936dabd82113a7f35579301c73015bef6a04a5087de1d72`; see the
  [round-1](plan-review-r1-disposition.md) and
  [round-2](plan-review-r2-disposition.md) dispositions. r3 applies round-2
  themes X, Y, Z and AA at the owner's direction `(p2)` (quoted in the plan).
  **r3 bytes carry no review opinion.**
- Inherited: derivation-why-not WN1 spec and record (kernel, oracle, budgets),
  WN-R1..R8.
- `(o1)` covers NM-D3, D4, D5; `(p1)` rules NM-D14 (truncate) and NM-D15 (search
  off on the public path). NM-D6 (positive atoms only) is the plan author's
  proposal.

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O1 | join variables of an empty join | Design: `roles` per pair |
| Plan O2 | values from each side differing by case, whitespace, punctuation | Design: `_normalize`, `_near_misses` |
| Plan O3, NM-R1 | exact matching, statuses, `work` and exits unchanged | Design: eligibility, own counter; T9, T15 |
| NM-R2 | one fixed normalization, one home, Unicode database stated | `_normalize`, standing rule 5; T1; recorded `unidata_version` |
| Plan O4 | spelling gap distinguishable from missing fact | empty vs non-empty report; T2, T3 |
| Plan O5 | covers what host case-folding covers, and more | T1 |
| Plan O9, NM-R3 | bounded, linear, counted | keyed counting, pair bound, cap; T12, T12b, T12c |
| NM1-C1..C5 | phase criteria | T1-T21 |
| NM-R7 | layering, RF6 | T13 |
| NM-R8 | anonymity | T14 |
| Round 1 themes A, B, C, P, Q; round 2 themes X, Y, Z, AA | repairs | eligibility (A, Y); flag off (B); keyed counting and cap (C, X); tests (P, Z); Unicode note (Q); NM-R2 row (AA) |

## Standing rules bound to this phase

1. **Totality:** `_normalize` is total over every value a population can carry;
   non-`str` (including `bool`) returns `None`. T1, T8.
2. **Input cap bounds the algorithm:** the search inspects every row of the fact
   type and every binding once and builds at most 25 pairs per key; its own
   counter is capped, and never exceeds the probes the join already charged.
   T12, T12b, T12c.
3. **Validation order:** unchanged; the search runs only after the blocker is
   fixed and cannot change which step blocks. T9.
4. **One walk:** one `_near_misses` serves every atom blocker at every depth.
   T4.
5. **One home:** the normalization's normative text lives here until NM3 moves
   it to `docs/reference/why-not.md`; this spec then cites that page.
6. **Measurement over argument:** "nothing else changes" is shown by running the
   unchanged suites, not argued (T15).

NM-R4..R6 (disclosure) do not apply: the kernel emits raw values and never
resolves a mode.

## Goal

With `near_misses=True`, every atom blocker in the kernel's result carries
`near_miss_count`, `near_miss_truncated` and `near_misses` as defined below, and
`uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py`
exits 0 with exact oracle agreement on every untruncated hand-written and
generated case and the subset relation on every truncated one. With the default
`near_misses=False`, the kernel's output is byte-identical to `33c260e`, and the
NM1 focused gate in plan §9 (which includes `tests/test_public_why_not.py`)
exits 0 with no golden or existing test changed. No input that exits 0 at
`33c260e` exits otherwise with the search on.

## Design

### `src/gnd/witness/why_not.py` (about +120 lines)

**Limits.** `WhyNotLimits` gains `near_miss_inspections: int = 200000`.
`checked_why_not_limits` already checks every field (`fields(WhyNotLimits)`),
so the new ceiling cannot be raised. The service's projection onto
`WitnessLimits` (`service._why_not_intake_limits`) reads named fields only and
is unaffected.

**Entry point.**

```python
def explain(model, candidate, fact_type_id: str, *, row: list[dict] | None = None,
            references=None, limits: WhyNotLimits = DEFAULT_WHY_NOT_LIMITS,
            near_misses: bool = False) -> WhyNotResult:
```

`explain` passes the flag to `_Walk(model, index, population, relations,
extensions, budget, *, near_misses: bool = False)`, which stores it and a
separate counter `self.near_miss_inspections = 0`. The cap is read from
`self.budget.limits.near_miss_inspections`. The counter is not in
`_Budget.work`, which `_Budget.charge` and `WhyNotResult` report, and one
counter serves every clause and descent level of the walk. (gate sweep)

**Normalization.**

```python
def _normalize(value: Any) -> str | None:
    """NFKC, casefold, delete Unicode punctuation (category P*), collapse
    whitespace runs to one space, strip. None for non-str or an empty result.
    Uses the running interpreter's Unicode database."""
```

Normative steps: `unicodedata.normalize("NFKC", v)` → `.casefold()` → keep only
characters `c` with `not unicodedata.category(c).startswith("P")` →
`" ".join(s.split())`. Return `None` if `type(value) is not str` or the result is
`""`.

**Eligibility** (themes A, Y).

```python
def _eligible_rows(self, atom: dict, bound: frozenset[str]) -> list[dict]:
```

From `checker.atom_bind(atom)`: constant roles; `B` = roles whose variable is in
`bound` (the variables of `previous[0]`, as `_atom_blocker` computes); free
roles grouped by variable. A row `f` from `self.facts.get(fact_type, ())` is
eligible when it has every role of the atom, every constant role equals the
constant by `checker._identity_key`, and for each free variable occurring in two
or more roles the identity keys at those roles are equal.

These are the per-row checks of `extensions._joined_atom_candidates`
(`extensions.py:629-680`) except two: the comparison of bound roles with a
binding, and production's in-row consistency check for a bound variable repeated
at several roles (`extensions.py:667-670`). Each occurrence of a repeated bound
variable is instead compared with the binding (exactly or by key). The
exactness invariant survives: a row agreeing exactly with a binding at every
occurrence also passes the in-row check, so it would have joined.
`_eligible_rows` is called for every atom blocker, including `B` empty, so T19
can compare it with production.

**Keys.** `k(v) = ("n", _normalize(v))` if that is not `None`, else
`("x", checker._identity_key(v))`. A bound variable occurring at several roles
contributes one key component per role, each compared with the same binding
value.

**Representatives** (theme Y). Projections are grouped by identity
(`_identity_key` of each value over sorted `B`); each group is represented by
its canonical minimum (smallest `canonical` encoding of the projection), so the
bytes do not depend on row or binding order (`1` versus `1.0`).

**Search.**

```python
def _near_misses(self, previous: list[dict], atom: dict, roles: dict[str, dict]
                 ) -> tuple[int, bool, list[dict]]:
```

1. If `B` is empty: return `(0, False, [])`; no inspections.
2. Before each inspection, if `self.near_miss_inspections` equals
   `limits.near_miss_inspections`, stop: `truncated = True`. Otherwise
   increment it.
3. For each binding in `previous` (bindings first, theme X): one inspection; add
   its `B`-projection (role → `binding[variable]`) to `samples_by_key[K(b)]`,
   grouped by identity, where `K` is the tuple of `k` over sorted `B`.
4. For each row of the fact type: one inspection; if it is in `_eligible_rows`,
   add its `B`-projection to `rows_by_key[K(f)]`, grouped by identity.
5. For each key in both maps: `count += len(samples) * len(rows)` (distinct
   identity groups on each side). Sort each side's representatives by
   `canonical`; take the first 5 of each; form those pairs through one helper
   `_near_miss_pair(sample, candidate, B)`, which computes
   `differing = sorted(r for r in B if identity(sample[r]) !=
   identity(candidate[r]))` and raises
   `WhyNotInternalError("a near-miss row matches exactly")` when it is empty.
6. Sort all formed pairs by `(canonical(sample), canonical(candidate))`; keep 5.

Return `(count, truncated, pairs)`; each pair is
`{"roles": differing, "sample": sample, "candidate": candidate}`. When
truncated, `count` counts only what was inspected before the stop.

Inspections are every binding plus every row, which the blocker's join already
charged to `work.probes` (`why_not.py:368, 400, 419, 439-441`), so at default
limits the cap cannot be reached; it guards lowered limits.

`_atom_blocker` calls it only when the flag is set and adds
`"near_miss_count"`, `"near_miss_truncated"`, `"near_misses"`. Non-atom blockers
and flag-off output are unchanged.

### `src/gnd/witness/view.py`

Not changed in NM1 (no public path sets the flag; NM3 owns the view and schema).

### `tests/why_not_oracle.py` (about +70 lines)

Its own `normalize` (same four steps, written from this spec, importing only
`unicodedata`), its own eligibility check (constants and repeated free variables
by its own `identity`; repeated bound variables compared per occurrence), its
own representative rule (canonical minimum by its own encoding), and
brute-force enumeration of every (distinct sample, distinct eligible row) pair
with the pair condition checked directly, no keys. It always computes the full,
untruncated answer. No import from `gnd.witness`, `gnd.checker`, `gnd.values`
(existing AST import test).

**Comparison rule** (theme X). Untruncated kernel report: count, flag and pairs
equal the oracle's. Truncated kernel report: `count ≤` the oracle's and every
reported pair is among the oracle's pairs. Exact truncated values are pinned as
kernel literals (T12), never through the oracle.

### `tests/test_why_not_oracle.py` generator

`generate(seed, domains=DOMAINS)` gains an optional argument; the existing
parametrization keeps `DOMAINS` and is unchanged. A new parametrization over
seeds 0..199 uses `SPELLING = {"code": ["a", "A", "a.", " a ", "b", "B-", "c"],
"int": [0, 1, 2, 3]}`, enables near-misses, and asserts exact agreement plus at
least 20 blockers with a non-zero count across the seeds (a liveness floor, fixed
after the first run and recorded; the round-2 reader measured 46). A second pass
over the same seeds sets `near_miss_inspections=3` and asserts the truncated
comparison rule plus a recorded floor of truncated reports. Counts above 5 are
covered by the hand-written T11, since the generated corpus produced none.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Public payload in NM1 | ruled by NM-D15 `(p1-B)`: flag off on every public path | as ruled |
| D2 | Search work accounting | ruled by NM-D14 `(p1-C)`: own counter and cap, not in `work`, truncates | as ruled |
| D3 `(s1)` | A binding missing a `B` variable | cannot happen (every binding in a prefix has the same keys; confirmed by round 1); raise `WhyNotInternalError` if it does | as stated |
| D4 `(s1)` | Truncated count | (a) count of what was inspected (a lower bound); (b) omit the count when truncated: a nullable field | **(a)** |
| D5 `(s1)` | Representative of identity-equal values | (a) canonical minimum; (b) first seen: order-dependent bytes | **(a)** (theme Y) |

## Tests

Inline fixtures in `tests/test_why_not_kernel.py` (as T2-T7 of WN1 are written);
oracle comparisons in `tests/test_why_not_oracle.py`. Every case expects the
kernel to return with `near_misses=True` unless stated. Counts and pairs are
written as literals in the test unless stated.

| ID | Case | Expected |
|---|---|---|
| T1 | `_normalize` table: `"ACME CORP."`=`"Acme Corp."`; `"Acme\tCorp"`=`"Acme Corp"`; full-width `"ＡＣＭＥ"`=`"acme"`; `"Straße"`=`"STRASSE"`; `"ACME-CORP"`=`"ACMECORP"` and ≠`"ACME CORP"` (deletion, not replacement); `"Acme . Corp"`=`"Acme Corp"` (punctuation before whitespace); `"℅"`=`"co"` (NFKC before punctuation deletion); `"..."`, `"－－"` (full-width punctuation only) → `None` | as stated |
| T2 | Issue shape: `party` `ACME CORP.` in the row, `Acme Corp.` in the binding | blocker unchanged; count 1; one pair, `roles == ["party"]`; truncated false |
| T3 | Missing fact: no eligible row shares a key | count 0, `[]` |
| T4 | Pair on a blocker inside a descent | nested blocker carries count 1 and the one pair, as literals |
| T5 | Two bound roles, one exact and one near | one pair, `roles` = the near role |
| T6 | Row-level discriminator: one bound role near, the other wholly different | count 0 |
| T7 | Constant role differs from the row | count 0 |
| T8 | Key function: `7`, `"7"`, `True`, `1`, `1.0` give `("x", …)` keys distinct from `("n", "7")`; buildable case: a Number role holding `1` and `1.0` joins exactly, so no blocker | as stated |
| T9 | On every corpus case: flag on vs off, the result is identical except the three keys on atom blockers | equal |
| T10 | Repeated free variable, inconsistent row (`pair(work=$w, a=$y, b=$y)` with `{w1, x, z}`) | count 0, no exception |
| T10b | Repeated free variable, consistent row with a near bound value (`{W1., x, x}`) | count 1 |
| T10c | Repeated bound variable at two roles, one near and one exact | one pair, both roles compared |
| T11 | Cap over two keys: 7 distinct pairs spread over two keys whose canonical order interleaves | count 7, 5 pairs in global canonical order |
| T11b | Dedup by row: rows `{k:"ACME", v:"1"}`, `{k:"ACME", v:"2"}` with `v` free, binding `k="Acme"` | count 1 |
| T11c | Dedup by binding: two bindings differing only outside `B`, same `B` value | count 1 |
| T12 | Truncation: a fixture whose search makes exactly `m` inspections; `near_miss_inspections=m` and `m-1` | truncated false with full count; truncated true with the literal lower-bound count (bindings inspected first); status and exit identical; literal `m` |
| T12b | Linear growth: n = 100, 200, 400 bindings and rows, all sharing one key, rows spelled differently from bindings | count `n²`; inspections observed by bracketing the cap: untruncated at `2n`, truncated at `2n−1`; literal values |
| T12c | The r1 quadratic case (512 × 512 variants of one value, rows spelled differently from bindings), with `_near_miss_pair` patched at its defining home by a counting wrapper | completes with default limits; count 262,144; at most 25 pair constructions; no `WhyNotWorkError` |
| T13 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0, no new allowance |
| T14 | `tests/test_why_not_anonymity.py` | exit 0 |
| T15 | Flag off: `tests/test_why_not_kernel.py`, `tests/test_why_not_oracle.py` (existing cases) and `tests/test_public_why_not.py` unchanged | exit 0 with no edit to any existing test or golden |
| T16 | Exactness invariant: call `_near_misses` with a hand-built `previous` whose binding matches an eligible row exactly | `WhyNotInternalError` |
| T17 | Oracle agreement on every hand-written case above except T12 at `m-1`, T16, T19, T19b, T20 | equal counts, flags and pairs |
| T18 | Oracle agreement over 200 `SPELLING` seeds | equal; at least the recorded floor of non-zero counts |
| T18b | The same seeds with `near_miss_inspections=3` | truncated reports satisfy count ≤ and pairs ⊆ the oracle's; at least the recorded floor of truncated reports |
| T19 | Eligibility equals production with `B` empty, on every corpus atom | `_eligible_rows(atom, frozenset())` projected to each assignment's variables equals the assignments `_candidates(atom)` returns, as sets of binding keys |
| T19b | Eligibility with `B` non-empty: a repeated bound variable spelled two ways in one row; a constant mismatch; a repeated free variable mismatch | first eligible, the other two not |
| T20 | `checked_why_not_limits` refuses `near_miss_inspections` above the default | `WhyNotInputError` |
| T21 | Representatives: rows `[{n:1, m:"ACME"}, {n:1.0, m:"ACME"}]` against a near binding, in both orders | identical bytes |

### Verification selection

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| Plan §9 NM1 row (mandated) | run | `uv run pytest -q tests/test_why_not_kernel.py tests/test_why_not_oracle.py tests/test_public_why_not.py tests/test_why_not_anonymity.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`, exit 0 | `src/gnd/witness/why_not.py`, `tests/why_not_oracle.py`, `tests/why_not_support.py`, the kernel and oracle test files, `tools/gnd_layers.json` | Carries T1-T21 (direct tests), layering and anonymity | any change to those files or to `checker`/`extensions`/`values` helpers the kernel calls |
| Affected consumers of `why_not.py` and `WhyNotLimits` | run | `uv run pytest -q tests/test_why_not_repair_loop.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py tests/test_public_api.py tests/test_public_reference_signatures.py`, exit 0 | `src/gnd/witness/service.py` (the only source importer), why-not goldens, RF1/RF5 pins, public signature pins | The only production importer is `witness/service.py`, which passes no flag and reads named limit fields; these are every test that names why-not outside the gate above, except the inventory and runtime tests below | a change to `service.py`, `view.py`, `api.py` or the why-not schema |
| `tests/test_public_built_inventory.py`, `tests/test_public_runtime.py`, `tests/test_v61_phase2_api.py` | run | `uv run pytest -q` over the three files, exit 0 | the built package inventory and runtime entry points | They mention why-not; cheap to run; no claim is inherited | any packaging change |
| Broad default suite | cadence | milestone close, on explicit owner selection (plan §9) | whole repository | NM1 changes one module behind a default-off flag | an owner selection |

### Implementability sweep (before the gate)

Each requirement was checked against `33c260e`:

- `WhyNotLimits` is a frozen dataclass whose every field `checked_why_not_limits`
  bounds by the default (`why_not.py:57-65`), so T20 holds by construction;
  `_Budget.charge` reads only the counter it charges, so the new field cannot
  reach `work`.
- The only production caller, `witness/service.py:161`, calls `explain` without
  the flag, so T15 is reachable.
- `_atom_blocker(step, previous, atom)` has the bindings and the atom's role
  terms (`why_not.py:481-494`) that `_near_misses` needs; `_Walk` lacked the
  flag, now passed at construction (edit above).
- `B` non-empty iff the join's `shared` is non-empty (both are the atom's
  variables bound in `previous[0]`), and then `_candidates` charged every row
  and `_join` one probe per binding (`why_not.py:366-406`), so inspections ≤
  charged probes holds per blocker, and summed over the walk.
- T12b and T12c need up to 512 distinct strings with one normalized form on each
  side; inserting punctuation and whitespace runs gives as many as needed.
- `_canonical` (`canonical_json_bytes`) and `checker._identity_key` exist in
  the kernel's imports.

No requirement was found that no implementation can satisfy.

## Out of scope for this phase

The schema, the view, the CLI and API payloads, the disclosure mode, docs,
negated or comparison blockers.

## Size

About 120 source lines and 400 test lines.

## Approval instrument

This prose. NM1 changes no shipped byte; the corpus-first instrument belongs to
NM3, which fixes the wire form.

## Recorded at implementation

`unicodedata.unidata_version` of each interpreter the gate runs on, and the T18
and T18b floors.

## Implementation findings

Recorded as found, 2026-11-01.

- **F1 (refines D5's reading; no design change).** The canonical minimum is
  byte order over the canonical encoding, so between `1` and `1.0` it picks
  `1.0` when the value is the last key (`1.0}` sorts before `1}`) and `1` when
  another key follows (`1,` sorts before `1.0,`). D5's property, bytes
  independent of row and binding order, holds and T21 pins it. The DC1 draft's
  "shown in their smallest canonical form" reads as "shortest" and is wrong.
  NM4 must say "the first in canonical byte order". Open-questions row for NM4.
- **F2 (test strength; successor case added).** At `near_miss_inspections=3`,
  none of the 15 truncated generated reports carries a pair, because bindings
  are inspected before rows. Caps 5 to 20 give at most one such report. T18b is
  kept as approved, so the subset half of the comparison rule is exercised with
  content by a successor, **T17b**: T12 at cap 4 and T12b (n = 100) at cap 199,
  against the oracle's full pair list.
- **F3 (refuted premise in the verification ledger).** `tests/test_rf6_query_policy.py`
  keeps a counted syntax census of non-constant subscripts, including type
  annotations. The kernel adds 26 distinct candidates (32 occurrences). Following
  WN1's practice, an authenticated successor
  `evidence/NM1/dynamic-query-successor.json` is chained after `WN-merge` in
  `tests/support/pyrel_application_successors.py`. It is a syntax census, not a
  query exception, so T13's "no new allowance" still holds. The ledger's input
  boundary missed that support file and its other consumer,
  `tests/test_rf2_pre_move_pins.py`, which was added to the consumer run.
- **F4 (implementation shape; no design change).** The search does not call
  `_eligible_rows`. Both call one per-row predicate, `_Walk._eligible`, so the
  search can count one inspection per row while T19 compares the same predicate
  with production. Review R7 confirmed that the B-empty early return was
  untested, and a regression test now covers it.
- **Recorded values.** `unicodedata.unidata_version` 16.0.0 on Python 3.14.3
  (the one interpreter the gate ran on). T18 floor 46 (measured 46), T18b floor
  15 (measured 15).
