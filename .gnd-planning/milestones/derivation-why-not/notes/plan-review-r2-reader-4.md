# Round 2 reader 4 -- test design, falsifiability and the end-to-end demonstration

Retained text of the reader's returned report. Local edits: scratch paths read
`<scratch>`.

Digests matched: plan `b0308e35…630e`, WN1 spec `d1c87cb1…6f69`.

**Verdict: request-changes**

**Scope.** I read the whole of plan r2 and WN1 spec r2, the r1 disposition and my round-1 note. I checked the repaired text against `extensions.py` (`_witness_charge` at :457, the join charges at :404/:737/:763, the component product at :872), `witness/types.py`, `witness/producer.py` and `values._identity_key`. I ran three probes with `uv run python -I`. The scripts and generated fixtures are in `<scratch>/r2-reader4/`. I wrote nothing in the repository.

## Round-1 findings

| ID | Status | Evidence |
|---|---|---|
| R4-F1 | resolved | §6.7 adds a `probes` ceiling, an indexed walk and a charge-only trace over the pre-evaluation; T13c/T13d added. The test that should exercise them is weak (R4-2-F2). |
| R4-F2 | partly | T13 is now counter-based, but the stated numbers are wrong (R4-2-F1). |
| R4-F3 | partly | The discriminators, the oracle's own identity table and the full blocker comparison are in. One discriminator cannot be built, the import ban has a hole, and the census proves nothing (R4-2-F4). |
| R4-F4 | partly | Items 1, 2, 4, 5 and 8 are fixed. Item 3 is credited to a branch that cannot be reached (R4-2-F5). Item 6's `proof_depth` case conflicts with depth 8 (R4-2-F6). Item 7, the descent-returns-derived raise, has no case: T10 and T11 do not expect it. |
| R4-F5 | resolved as asked | Status-first removes the undefined inputs; D6 and the `covers` fixture are added. But T8 is now circular (R4-2-F3). |
| R4-F6 | partly | WN3-C2 adopts every requested element. Residual vacuity in R4-2-F7. |
| R4-F7 | resolved | §6.3 has the per-role map, `ground`, role-keyed samples and `steps_after_blocker`; WN2 has redacted and `--raw` goldens. |
| R4-F8 | resolved | WN2-C6 is the WN2 time-bound gate; T15b added. |

## New findings

### R4-2-F1 -- blocking, high confidence, self-inflicted (p1-C)
**Where:** spec §8 T13a/T13b, §4 standing rule 6.

**What is wrong.**
- **No walk in either case.** As written, the four-disconnected-atom rule is derived in rule mode. Production also enumerates the product (`_component_product`), so the walk never runs.
- **Probe results.** Charges counted through `_witness_charge`:
  - 17 rows: 88,791 = 17⁴+17³+17²+4·17. The extension is non-empty, so `derived` and no walk.
  - 18 rows: 111,204. The breach happens inside the **pre-evaluation**.
- **T13a.** It therefore measures production's cost, not WN-D2's declared-order cost, which is what standing rule 6 says T13a/b measure. Fully disconnected bodies cost the same in both orders.
- **T13b.** "Final count equals the exact product" is false: the counter reads 88,791, not 83,521.
- **Fixture with a final empty atom (so the walk runs).**
  - Production charges only 68 or 72.
  - The walk stores 17+289+4,913+83,521 = 88,740 (17 rows) or 111,150 (18 rows).
  - With the budget shared, 18 rows breaches at a total of exactly 100,001 (`joins + 1` holds). The 17-row twin totals 88,808, not 83,521.

**Other gaps.**
- §6.7 does not say which counter (`joins`/`bindings` or `probes`) the charge-only trace adds pre-evaluation charges to.
- `work` uses the key `bindings` while the limit field is `joins`.
- WN-R4 withholds partial counts on a breach but names no hook for the test to read the counter.

**Fix.**
- Give the T13a/b body a connecting or bridging shape that production avoids: atoms 1 and 2 disconnected with atom 3 bridging, or a trailing empty atom.
- State the shared-budget totals: pre-evaluation plus walk prefix sums.
- Name the counter the trace charges and how a test reads it on a breach.

### R4-2-F2 -- blocking, high confidence, self-inflicted (p1-C)
**Where:** T13c.

**What is wrong.**
- "`probes` equals left bindings plus rows scanned" checks the implementation's counters against themselves.
- A nested-loop walk scans 5,000×|R| rows and still satisfies the equality. It cannot catch the unindexed join that R4-F1 targeted.
- |R| is unstated, and so is whether atom 0's scan counts.
- Production adds 5,000 more during pre-evaluation (probe: charge 5000, 0 rows) to an unnamed counter.

**Answer to the question:** the exact count cannot be stated before implementation from the current text.

**Fix.** Fix |R| (e.g. 300), say whether each counter is cumulative across pre-evaluation and walk, and write the literal expected numbers. For example, probes = 5,000 lookups + 5,000 + 300 rows scanned (or as defined), and joins/bindings = 5,000 (pre-evaluation) + 5,000 (walk step 1).

### R4-2-F3 -- blocking, high confidence, self-inflicted (p1-A)
**Where:** spec §5, §6.2, T8; plan predicate 1.

**What is wrong.**
- §6.2 copies `derived` and `unavailable` from `_evaluate_stratified_extensions`.
- T8 asserts "top status equals the production classification", which is that same call. It cannot fail except under the monkeypatch.
- The oracle (§6.6) returns steps and blockers only, never a status. So no independent source checks derived-vs-blocked or §6.1's `unsupported`.

**Fix.**
- Define T8 against `gnd check`'s report verdict, which comes from a different entry (`_evaluate_derivations_dispatch`), with the variant-to-status map written out. It must include `unchecked/opaque-value` for §6.1.
- Have the oracle compute derivability by its own fixpoint, and run it on derived cases too.

### R4-2-F4 -- hardening, high confidence, self-inflicted (p1-D)
**Where:** §6.6.

**What is wrong.**
- **One discriminator cannot be built.** Population validation refuses `True`, `1` and `"1"` in one column for both String and Number roles (probe: `PopulationValidationError`). Integer refuses `1.0`. `1, 1.0, 1` loads as a bag on Number.
- **The import ban has a hole.** It omits `gnd.checker`, which re-exports `_identity_key`, `_identity_token`, `_joined_atom_candidates` and `_apply_negation` (probe: `hasattr` true). No test enforces the ban.
- **The census proves nothing.** It only finds named cases. It does not check that each case has its property, for example that declared order differs from `_joined_bindings` order.

**Fix.**
- Replace the unbuildable case with a buildable boolean-vs-number one, or a direct-relation kernel case marked as such.
- Add `gnd.checker` and `gnd.witness` to the ban, enforced by an AST import test.
- Make the census assert each property.

### R4-2-F5 -- hardening, high confidence, self-inflicted (p1-E)
**Where:** §6.4 last paragraph, branch walk "clause `derived` beside a `blocked` clause (T7)".

**What is wrong.** The walk runs only when production says not derived.
- **Row mode:** the head step keeps only bindings equal to the claimed row. Any clause that survives it means production derived the row.
- **Rule mode:** any clause that reaches the end means the extension is non-empty.

So walked clause status `derived` cannot be reached. §6.4's computed-head example contradicts §6.3 step 5. §6.2 step 5 raises only when *every* clause ends non-zero; one such clause is already a production disagreement.

**Fix.** Drop clause `derived`, or define it, and raise `WhyNotInternalError` when any walked clause ends non-zero. Remove the T7 credit.

### R4-2-F6 -- hardening, high confidence, self-inflicted (p1-C)
**Where:** §6.5, §6.7, T11, T12.

**What is wrong.** `proof_depth` defaults to 128 and descent stops at 8 with a recorded `descent_stopped: depth`. At the defaults, T12's `proof_depth` breach cannot be reached. With a lowered `proof_depth` below 8, the spec does not say whether the call raises or records.

**Fix.** State the precedence and the T12 fixture value.

### R4-2-F7 -- hardening, medium confidence, self-inflicted (p1-J)
**Where:** plan WN3-C2.

**What is wrong.** The loop can still pass vacuously:
- If a gap's blocker has every role free, the "extracted" table supplies the whole fact.
- "Previous step's predicate" does not exist when the gap is at index 0, and roles may not carry over between predicates.
- "Blocker unchanged" breaks if it means the full record, because `sample_count` can move.

**Fix.**
- Require that each gap has at least one bound role taken from the raw samples, that the extracted table holds only `free_roles` (assert the two sets are disjoint), and that gap 1's index is at least 1.
- Define "unchanged" as (kind, index, fact_type).
- Name the expected `check` verdict variant.

### Not verified
I did not probe the `covers` derived-predicate path or whether an opaque dict value can reach a validated population.
