# Reader 1 -- correctness against production semantics

Retained text of the reader's returned report, lightly edited for layout.
Scratch paths read `<scratch>`.

Both digests matched: plan `ec9cea0e…db63`, NM1 spec `e3855ca5…b670`.

**Verdict:** request-changes

**Scope.** Read both snapshots, issue #70, the WN2 review and record
(`003-phase-WN2.md`), and `witness/why_not.py`, `view.py`, `service.py`,
`witness/cli.py`, `why-not.schema.json`, `redaction.py` (header, `_project_fact`,
`project_output`, `emitter_specs`), `values._identity_key`,
`extensions._joined_atom_candidates` / `_relation_facts`. Five probes under
`<scratch>/nm-review/reader1/`: `p1_nearmiss.py` (the spec's `_near_misses`
patched onto `_atom_blocker`), `p2_budget.py` (cost growth), `p3_schema.py` and
`p4_schema.py` (what the schema already enforces), `p5_public.py` (public payload
under NM1 with the D1 strip). Not done: repository suites; a full NM2 emitter
audit (only witness-lane parsers and declared-redaction projection); the NM4
inventory.

**What holds.**

- Bound roles are decided from `previous[0]` and every binding in a prefix has
  the same keys (`extensions.py:629-674`; `_store` merges whole bindings), so
  spec D3 holds.
- `_Walk.facts` (`why_not.py:258`) is the row source `_candidates` reads,
  derived extensions included; constant roles compared by `_identity_key` match
  production (`extensions.py:663-666`).
- The issue's shape works: `Acme Corp.` vs `ACME CORP.` gives one pair with
  `roles == ["party"]` (p1 case B).
- Constant roles never near-match (p1 case C); rule-mode first atoms have
  nothing bound, so no near-misses.
- The view's closed allow-list (`view.py:95-117`) drops unknown blocker keys, so
  raw `near_misses` cannot leak through the redacted view even before the
  explicit entry.
- `WhyNotInternalError` is a `RuntimeError` caught by neither
  `service.why_not` (`service.py:162-174`) nor `witness/cli.py:82`, so the
  exactness invariant is a hard crash (hence R1-F1).

## Findings

### R1-F1 -- Repeated free variable makes valid input raise `WhyNotInternalError` (blocking)

- **Where:** plan §2.1 ("Free roles are unconstrained"); spec `_near_misses`
  (index on constants and B only) and exactness invariant; T16, T17.
- **What is wrong:** production drops a row whose repeated variable has two
  values (`extensions.py:667-670`). The index ignores free roles, so a row can
  match the binding exactly on every B role and constant yet never have been a
  candidate; `differing` is empty and the invariant raises. Exit 0 becomes an
  uncaught `RuntimeError`. The oracle, using the same definition, agrees, so T17
  cannot catch it.
- **Reproduction:** p1 case A: body `quote(q=$q, work=$w), pair(work=$w, a=$y,
  b=$y)`, quote `[{q1,w1}]`, pair `[{w1,x,z}]`. Today `blocked`; with the spec's
  algorithm `WhyNotInternalError: a near-miss row matches exactly`.
- **Fix:** consider only rows that pass production's per-row checks except the B
  comparisons (constants exact, repeated free variables consistent), e.g.
  `_joined_atom_candidates` with B terms set aside. Write it into §2.1, give the
  oracle the same clause, add consistent and inconsistent repeated-variable
  cases.

### R1-F2 -- NM1 public-parity gate cannot pass: `work.probes` is public (blocking)

- **Where:** spec D1, T15, D2; plan §9 NM1.
- **What is wrong:** `work.probes` is in the public envelope (`service.py:126`)
  and the redacted view (`view.py:145`); stripping the fields does not undo the
  probes.
- **Reproduction:** p5: 4 of 22 public cases change -- g1-rule-blocked 4→6,
  g2-row-descent 5→7, g14-constant-atom 4→6, g19-aggregate-descent 3→5.
- **Fix:** either T15 = byte-identical except `work.probes` with new values
  listed, or leave the search uncharged in NM1 and charge it in NM3. Either way
  the strip must recurse into `descent`.

### R1-F3 -- The search is quadratic; it can turn exit 0 into exit 4 (hardening)

- **Where:** NM-R1, NM-R3; spec standing rule 2, T12, T12b; NM1-C4 vs spec D2.
- **What is wrong:** every (binding, row) pair sharing a key is enumerated and
  charged before the cap; n×n when all keys coincide. T12 encodes an exit change
  against NM-R1. The plan charges `probes` and `binding_cells`, the spec only
  `probes`.
- **Reproduction:** p2: n=100: probes 300 → 10,500; n=200: 600 → 41,000; n=450:
  1,350 → 200,001, `WhyNotWorkError` where the baseline is `blocked`, exit 0.
- **Fix:** count per normalized key as distinct B-projected samples × distinct
  B-projected rows; build only the 5 smallest canonical pairs (rows + bindings +
  5). Either reword NM-R1 to allow a search-caused `work-limit`, or degrade the
  search's own fields on breach. Make counters agree.

### R1-F4 -- The CLI option overrides a `customer` environment setting (blocking)

- **Where:** §2.2 "Setting it", NM-D2, NM-R6, NM2-C1.
- **What is wrong:** `gnd --disclosure internal why-not … --raw` beats
  `GND_DISCLOSURE=customer` -- exactly the override the plan rejects for the API.
- **Fix:** the flag may only tighten; `--disclosure internal` under a `customer`
  environment exits 3; add the refusal case to NM2-C3.

### R1-F5 -- WN2-R1/R2/R3 treated as open but were fixed in WN2 (hardening)

- **Where:** O8, NM3-C2, §7, close carryovers, §10 last line.
- **What is wrong:** `003-phase-WN2.md:119-122` records R1-R4 fixed; the schema
  applies `redacted_clause`/`redacted_unavailable` when `view == "redacted"`
  (`why-not.schema.json:273-294, 596-660`) and pairs bands with reasons.
- **Reproduction:** p3, p4: a raw golden relabelled `redacted` is rejected;
  `work-limit` with exit 3, `input-invalid` with exit 4, and a refusal with
  `fact_type` set are rejected.
- **Fix:** drop O8 and the carryovers; NM3-C2 extends `redacted_clause` with
  `near_misses: const "redacted"` plus a negative case. `redacted_clause.blocker`
  lacks `additionalProperties`, so the explicit entry is required.

### R1-F6 -- "No population value in customer mode" is unmeetable under declared redaction (hardening)

- **Where:** predicate 3, NM2-C3.
- **What is wrong:** declared redaction projects only declared-sensitive roles
  (`redaction.py:564-569`; diff and verbalization branches 780-800). A customer
  check over a model with no declarations prints every value.
- **Fix:** state the predicate per convention, or rule that customer mode
  redacts all values everywhere.

### R1-F7 -- `witness-view --raw` missing from NM2's sites (hardening)

- **Where:** §1, NM2-C2.
- **What is wrong:** `gnd witness-view CERTIFICATE --raw` (`witness/cli.py:27-30`)
  returns the whole certificate (`view.py:21-28`).
- **Fix:** add it; the table test enumerates every parser defining `--raw` or
  `--unredacted`.

### R1-F8 -- NM-R5 contradicts the milestone's own changes (completeness)

- **Where:** NM-R5; NM1-C5, NM3, NM2-C4.
- **Fix:** scope NM-R5 to disclosure decisions, excepting the enumerated why-not
  payload changes and the root help text.

### R1-F9 -- Normalization depends on the interpreter's Unicode version (completeness)

- **Where:** NM-R2; spec `_normalize`; `requires-python >=3.11`.
- **What is wrong:** `unicodedata.unidata_version` differs across 3.11-3.13; the
  oracle shares the database.
- **Fix:** state that `N` follows the running interpreter's Unicode database;
  keep test inputs stable across 3.11+, or record `unidata_version`.
