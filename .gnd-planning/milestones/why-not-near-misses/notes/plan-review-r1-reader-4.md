# Reader 4 -- test design, falsifiability, end-to-end demonstration

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan `ec9cea0e…db63`, NM1 spec `e3855ca5…b670`.

**Verdict:** request-changes

**Scope.** Read the plan (457 lines) and NM1 spec (172 lines) in full against
`why_not.py`, `view.py`, `service.py`, `extensions._joined_atom_candidates`,
`values._identity_key`, the kernel and oracle tests, public goldens and docs.
Wrote the spec's `_near_misses` as specified and patched it into the kernel at
runtime. Probes under `<scratch>/nm-review/reader4/` (`probe.py`, `probe2.py`,
`probe3.py`, `probe4.py`, pytest plugins `nmplug.py`, `nmplug2.py`). Nothing
written in the repository.

**What holds.**

- Normalization is precise; `str.split()` equals the plan's maximal-isspace-run
  wording (spec:68-71, plan:166-173).
- T5, T6 (row-level vs per-role), T7 and T11 (cap 7→5, full count) each
  discriminate a plausible wrong implementation.
- T12 (literal L+k, L+k−1) catches an uncharged search.
- `Straße`/`STRASSE` separates casefold from lower; full-width `ＡＣＭＥ`
  separates NFKC from NFC.
- The redacted view is a closed allow-list (view.py:96-117).
- D3 holds.
- The oracle imports nothing from GND and its comparison ignores extra keys;
  with the patch only t2, t13b, t13c fail in the kernel and oracle files.

## Findings

### R4-F1 -- NM1 public payload cannot stay byte-identical; a docs gate breaks in NM1 (blocking)

- **Where:** spec:107-111, T15, D2, Goal; plan:81, 252, 304-307.
- **What is wrong:** `work` is in the envelope and both CLI views
  (service.py:126; view.py:145). The `gnd-run` block at
  `docs/how-to/repair-a-missing-claim.md:118` (`"probes": 4`) changes in NM1,
  and NM1's gate does not run the tutorial gate; NM3-C4 assumes only NM3 changes
  it.
- **Reproduction:** probe.py P1: g1 probes 4→6. nmplug2.py (patch plus a
  recursive strip at `_why_not_envelope`): `tests/test_public_why_not.py` has 10
  failures (g1, g2, g9, g14, g19; CLI and API). probe4.py: docs example probes
  4→5.
- **Fix:** (a) T15 = byte-identical except `work.probes`, regenerate goldens and
  the docs block in NM1, list old/new, add `tools/run_tutorials.py` to the NM1
  gate; or (b) `explain(..., near_misses=False)` by default, enabled by the
  service only in NM3, so no strip. Fix predicate 1 to match.

### R4-F2 -- Repeated free variable raises the exactness error (blocking)

- **Where:** spec:82-90; plan:175-185, 69-70.
- **What is wrong:** `_joined_atom_candidates` (extensions.py:629-680) rejects
  rows inconsistent on a repeated variable; the spec offers them, finds
  `differing == []` and raises. Such a row would not join after normalization
  either. The oracle generator (test_why_not_oracle.py:181-195) can produce such
  atoms.
- **Reproduction:** probe.py P2: `listed(case:$c), filed(case:$c, a:$y, b:$y)`,
  rows `listed{c1}`, `filed{c1, x, z}` → `WhyNotInternalError`.
- **Fix:** require consistency on repeated non-B variables; build the index over
  that filter or `_candidates(atom)` projected on B; same rule in the oracle; a
  test expecting count 0.

### R4-F3 -- T16 cannot be written as described (hardening)

- **Where:** T16.
- **What is wrong:** a constant key only widens candidates; an exactly matching
  row would already have joined, so the raise is unreachable, and false pairs
  are emitted silently.
- **Reproduction:** probe.py P4: no raise; bogus pair `{'work': 'w1'} → {'work':
  'w9'}`.
- **Fix:** call `_near_misses` with a hand-built `previous` that matches a row,
  or append that row to `_Walk.facts` after `_join`; expect the error.

### R4-F4 -- "Linear" is false; T12b cannot detect the quadratic case (hardening)

- **Where:** NM-R3 (plan:107), spec:34-35, T12b, plan:400.
- **Reproduction:** probe.py P3, n variants on both sides: n=16 → probes 336,
  count 256; n=32 → 1184, 1024; n=64 → 4416, 4096.
- **Fix:** restate the bound as rows + bindings + inspected pairs, each charged;
  add an n×n literal test that breaches and exits 4; pin T12b's fixture.

### R4-F5 -- T17 oracle agreement is vacuous on the generated corpus (hardening)

- **Where:** T17, NM1-C3; generator domain `code = ["a","b","c"]`
  (test_why_not_oracle.py:162).
- **Reproduction:** probe2.py, 200 seeds: 0 blockers with a non-zero count.
- **Fix:** add spelling variants to the domain; assert a minimum of non-zero and
  capped generated cases.

### R4-F6 -- T1 does not discriminate punctuation semantics or step order (hardening)

- **Reproduction:** probe.py P5: punctuation-to-space and whitespace-first
  variants pass all T1 pairs. Spec: `ACME-CORP` = `ACMECORP`; `Acme . Corp` =
  `Acme Corp`. NBSP is already a space after NFKC.
- **Fix:** add these pairs and a full-width-punctuation-only value; pin the
  user-visible hyphen case (`ACME-CORP` does not near-miss `ACME CORP`).

### R4-F7 -- T8 cannot be built through a validated model (hardening)

- **What is wrong:** a variable cannot span String and Integer roles; non-string
  values can only match exactly.
- **Reproduction:** probe3.py: `ModelValidationError: variable '$k' plays a role
  of type 'int' here and a role of type 'code'`.
- **Fix:** make T8 a key-function unit test (`7`, `"7"`, `True`, `1`, `1.0`);
  add a buildable Number case (`1` and `1.0` join exactly: no blocker).

### R4-F8 -- No discriminator for deduplication (completeness)

- **Reproduction:** probe.py P6: rows `{k:"ACME", v:"1"}`, `{k:"ACME", v:"2"}`
  vs `k="Acme"`: spec count 1, per-row count 2.
- **Fix:** add row-dedup and binding-dedup fixtures with literal counts.

### R4-F9 -- Counters disagree; the to-update test list is wrong (completeness)

- **What is wrong:** NM1-C4 says probes and binding_cells, D2 says probes.
  `test_review_r5_negation_probe_charges_are_exact` is unaffected (negated
  blocker); `test_t13b_twin_completes_at_310_rows` (probes 96_722) and
  `test_t2_second_atom_blocks` (exact blocker dict) are affected but unnamed.
- **Fix:** align NM1-C4 with D2; correct the list.

### R4-F10 -- T10 input unspecified; view change unreachable or breaks the closed schema (hardening)

- **What is wrong:** under D1 the view never sees the fields; adding
  `near_misses: "redacted"` unconditionally changes redacted goldens and fails
  the v1 schema.
- **Fix:** add the fields only when present; T10 passes an enveloped kernel dict
  with a descent directly to `why_not_view` and asserts no T2 value anywhere in
  the serialized output.
