# Confirmation round (round 2), reader 1 -- correctness against production semantics

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan r2 `211d9e01…0a665de`, NM1 spec r2 `1b739a57…1d72`.

**Verdict:** approve-with-fixes

**Scope.** Both r2 snapshots, the r1 disposition, reader notes 1 and 2, the
r1→r2 spec diff, against `33c260e`: `witness/why_not.py`,
`extensions._joined_atom_candidates` (629-675), `values._identity_key`,
`witness/service.py:95-178`, `witness/view.py:93-157`, the schema's
`$defs/blocker` and `redacted_clause`, kernel and oracle tests. Probes in
`<scratch>/nm-review2/reader1/`: `probe_spec_r2.py` (r2 algorithm vs a
brute-force count from the row-level definition), `probe_cap_reach.py`
(inspections vs `work.probes`). Themes D-G checked at text level only.

**What holds.** 400-seed fuzz (repeated free, repeated bound, constant and
two-bound shapes; 358 blockers, 104 non-zero): keyed count equals brute force
every time; the invariant never fired. The invariant is sound: an eligible row
whose B-projection equals a binding's passes `extensions.py:648-670`, and
`_join` (`why_not.py:379-406`) indexes on `shared` = B, so it would have joined.
Key equality equals the per-role condition. The r1 worst case gives 262,144 with
1,024 inspections, nothing charged to `work`.

## Theme status

| Theme | Status | Reason |
|---|---|---|
| A | repaired | eligibility by `_identity_key` as `extensions.py:663-670`; T10 count 0; fuzz 0 errors; wording gap C1-F4 |
| B | repaired | flag default off; counter outside `work`; `WhyNotLimits` consumers unaffected; service passes no flag |
| C | repaired | keyed count equals brute force; linear; no exit 4; truncation unreachable at defaults (C1-F1); wording C1-F2, F3, F5 |
| D | repaired | tighten-only, context variable, threat model; fail-closed ordering gap C1-F8 |
| E | repaired | (a) ruled, scope stated |
| F | repaired (text level) | mechanical discovery and known rows |
| G | repaired | ruled, ruling cited; a theme-L edit undercuts it (C1-F7) |

## Findings

### C1-F1 -- Default cap unreachable; predicate 1 asks for truncated reports nothing produces (hardening, self-inflicted)

- Inspections (every row + every binding) equal what the blocker's join already
  charged (`why_not.py:368`, `:400`), so inspections ≤ `work.probes` ≤ 200,000 =
  the default cap; `near_miss_truncated` is always false on the public path.
  Rows before bindings means truncation in the row phase reports count 0.
- **Reproduction:** `probe_cap_reach.py`: n=100/512/2000 → inspections
  200/1024/4000 vs probes 300/1536/6000. `probe_spec_r2.py` case 3: cap 3 →
  `count 0, truncated True` though a matching row was indexed.
- **Fix:** state the invariant; keep the cap as defence in depth; a lowered-cap
  T18b with a floor, or drop "truncated" from predicate 1 and NM1-C3; consider
  bindings before rows; docs say the flag is false at defaults.

### C1-F2 -- Representative of identity-equal values depends on row order (hardening, self-inflicted)

- `1` and `1.0` share `_identity_key` (`values.py:19-20`); first-seen is kept,
  so `candidate` bytes depend on population order; the oracle may differ.
- **Reproduction:** `probe_spec_r2.py` case 2: rows `[{n:1,m:ACME},{n:1.0,m:ACME}]`
  → `{"n":1}`; reversed → `{"n":1.0}`.
- **Fix:** canonical-minimum representative in kernel and oracle, or compare by
  identity as `_samples_identity` does.

### C1-F3 -- Count is over distinct projections; definition and oracle text say (binding, row) (hardening, self-inflicted)

- **Reproduction:** T11b fixture: 2 distinct rows, 1 distinct projection; a
  literal oracle gives 2, the kernel 1.
- **Fix:** define `near_miss_count` over distinct (B-projection of a binding,
  B-projection of an eligible row) pairs; same wording in the oracle paragraph.

### C1-F4 -- Eligibility wording understates the departure for repeated bound variables; T19 cannot check it (hardening, self-inflicted)

- Production (unseeded) checks every repeated variable, bound ones included
  (`extensions.py:667-670`); r2 relaxes that for bound variables (T10c). The
  claim "every per-row check except the bound comparison" is false as written,
  though the invariant still holds. T19 runs only with B empty and compares
  "row sets" with `_candidates`' assignment dicts.
- **Reproduction:** `probe_spec_r2.py` case 1: row `{a:w1, b:W1.}` with `$w`
  bound at both roles: production rejects it as a candidate; r2 reports one pair
  `roles ["b"]`.
- **Fix:** state the relaxation and why; T19 compares binding keys of
  assignments; add a B-non-empty eligibility unit test.

### C1-F5 -- Cost wording disagrees with the spec (completeness, self-inflicted)

- Plan: "eligible rows", "only the reported pairs"; spec: every row inspected, up
  to 25 pairs per key. **Fix:** "every row of the fact type plus every binding";
  "at most 25 pairs per shared key; 5 reported".

### C1-F6 -- NM3-C2 does not say `near_misses` must accept the redacted form (completeness, self-inflicted)

- `$defs/blocker` is closed and serves both views; `samples` is
  `oneOf [array, const "redacted"]`; requiredness must be conditional on
  `kind: atom`; "count below list length" needs per-length `if`/`then`.
- **Fix:** spell out the three shapes.

### C1-F7 -- Forwarding `internal` to `exp run` agents raises exposure to external agents (hardening, self-inflicted)

- An agent's own `gnd check` applies declared redaction today; forwarding
  `internal` lifts it for agents that may be external providers. Also, if the
  spawners count as site-less commands, a malformed value is ignored and a
  mistyped lock is dropped for children.
- **Fix:** forward only `customer`; treat both spawners as disclosure-bearing.

### C1-F8 -- Order of the malformed-environment check and the option unspecified (hardening, self-inflicted)

- `GND_DISCLOSURE=Customer` with `--disclosure internal` reads as "the option
  wins". **Fix:** refuse a malformed variable (exit 3) before applying the option
  on disclosure-bearing commands; add the case to NM2-C1.
