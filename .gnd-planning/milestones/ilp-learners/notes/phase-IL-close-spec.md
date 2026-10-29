# IL-close, part A — the close repairs

## 1. Status

**r1, approved by the owner on 2026-10-29** (§12): every proposed ruling,
ILC-D1 to ILC-D9, corpus-first. `auto=false`.

**Base:** `claude/il-close`, branched from `main` at `a75b328` (PR #62, IL6,
merged). All six phases are recorded (`002` to `007`).

**Authority:** the close plan, `notes/close-plan.md` r1. The owner approved
it on 2026-10-29 ("The close plan is approved. Draft the IL-close repair spec
and stop at its owner gate."), over SHA-256
`e636b45237eecfdd14d014154853fd071e32fee2420ff55e95617087845d3d7d`. Its
ruling table fixes **what** is repaired. This spec decides **how**.

**What the gate decides:** ILC-D1 to ILC-D9 (§7). They cover:
- the subtype spelling;
- what the run record binds and whether the AMIE adapter version moves;
- the shape of each new refusal;
- the approval instrument.

## 2. Provenance

- The close plan, Part A table and "what the repair spec must decide" 1–6.
- The open-question rows, by record:

| Record | Rows |
|---|---|
| `002-phase-IL1.md` | IL1-Q1, IL1-Q4, IL1-Q5 |
| `003-phase-IL2.md` | IL2-Q1, IL2-Q3 |
| `005-phase-IL3.md` | IL3-Q2 |
| `006-phase-IL4.md` | IL4-Q1, IL4-Q2, IL4-Q3 |
| `007-phase-IL6.md` | IL6-Q1, IL6-Q2 |

- Each row's review finding, reproduced at its own phase:

| Review file | Finding | Row |
|---|---|---|
| `notes/phase-IL1-agent-review.md` | 3 | IL1-Q1 |
| `notes/phase-IL1-agent-review.md` | 4 | IL1-Q4 |
| `notes/phase-IL1-agent-review.md` | 8 | IL1-Q5 |
| `notes/phase-IL2-agent-review.md` | 5 | IL2-Q3 |
| `notes/phase-IL4-agent-review.md` | 2 | IL4-Q1 |
| `notes/phase-IL4-agent-review.md` | 4 | IL4-Q2 |
| `notes/phase-IL6-agent-review.md` | R6a | IL6-Q1 |
| `notes/phase-IL6-agent-review.md` | R6c | IL6-Q2 |

- The plan, `notes/ilp-learners-plan.md`: §0 (IL-R7, IL-R9, IL-R10) and §9 (the controls every gate runs).

## 3. Obligations — inline harvest

| Obligation | Source | Discharged by |
|---|---|---|
| Subtype joins count as the checker does | IL4-Q1, ruled "Fix it now" | §6.1; ILC-D1, ILC-D2; C1 |
| The mined run record binds the export | IL4-Q2, ruled "Bind it now" (within `/1`; re-derive the retained records) | §6.2; ILC-D3, ILC-D4; C2 |
| The comparison tool fails loudly on an unmappable mined rule | IL6-Q2 | §6.3; C3 |
| An infix comparison joins its two variable operands for check 9b | IL1-Q1 | §6.4; ILC-D5; C4 |
| The ILASP import refuses a comparison constant that is not a rendered threshold | IL2-Q3 | §6.5; ILC-D6; C5 |
| `extract_program` reports, rather than drops, a rule after an interleaved line | IL1-Q4 | §6.6; ILC-D7; C6 |
| The Popper reader reads a bare `true`/`false` as a boolean | IL2-Q1 | §6.7; C7 |
| Missing tests: T5c's pair count, a `type_closures` subtype test, and refusal names per adapter section | IL1-Q5, IL6-Q1 | §6.8; C8 |
| `_threshold_rows` and `_value` become public | IL3-Q2, IL4-Q3 | §6.9; ILC-D8; C9 |
| No run-of-record outcome changes; the comparison table and the walk stay true | close plan, Part A item 6 | C10, C11 |
| Every golden that moves is named (IL-R7) | plan §0 | §8 |
| The evidence stays private-clean (IL-R10) | plan §0 | the existing `test_ilp_learners` T8 |

## 4. Rules bound to this part

**Standing rules.**

| Rule | Binding |
|---|---|
| 1 Totality | The new checks are total over parsed input. The comparison tool's new failure is a named exit, not a traceback. |
| 2 Algorithm bound | The root computation is linear in the subtype graph. The threshold check is linear in comparisons times thresholds (at most 32 per type). |
| 3 Validation order | §6 fixes each new check's position. Earlier refusals keep their precedence (C10). |
| 4 One walk | One spelling function, `ilp_amie.spell`, serves both the export and the count. |
| 5 One home | `docs/reference/ilp-bridge.md` holds each new refusal and binding. |
| 6 Measurement | Each new refusal has a corpus case that exits as stated (C1–C7). |

**Plan rules (IL-R).**

| Rule | Binding |
|---|---|
| IL-R1, IL-R2, IL-R5, IL-R8 | No learner runs and nothing is downloaded. The repairs are GND-side. |
| IL-R3 | Unchanged: one registry and one re-check. |
| IL-R4 | Unchanged. |
| IL-R6 | Unchanged: the readers stay closed. |
| IL-R7 | §8 lists every golden and wire that moves. Any other golden that moves during implementation is a finding, and it returns to the owner gate. |
| IL-R9 | The retained runs are not re-run. ILC-D4 settles the AMIE adapter version. |
| IL-R10 | Re-derived evidence keeps `<scratch>` placeholders. The original bytes are retained beside it. |
| IL-R11 | Unchanged. |

## 5. Goal

Every question the owner ruled "fix" is fixed, and each fix has a falsifiable
case. The fixes change no run-of-record outcome, and the comparison table
stays the same eight rows.

## 6. Design

### 6.1 Subtype joins (IL4-Q1)

**The defect.** Today `ilp_amie.spell` writes a value as
`<role's own object type>:<value>`. Take the model `manager subtype_of staff`
with `manages(manager, team)` and `works_in(staff, team)`. Alice is then
spelled `manager:alice` in one relation and `staff:alice` in the other. A
join on her never matches, so a rule that holds is refused with
`does-not-hold` or `support-mismatch`. This is a false refusal; it never
admits wrongly. Check 9b passes the join, because the two closures intersect.
The checker compares raw values.

**The fix.** Spell every value by its **family**: the weakly connected
component of the subtype graph that contains the role's object type. The
family is named by the least object-type id, in code-point order, among the
component's top types (types with no `subtype_of`).

`ilp_amie.family(model_index) -> dict[str, str]` maps each object-type id to
its family name, and `spell` takes the family name in place of the role's
own type.

**Why a family, not a root set.** Take `manager subtype_of [staff, person]`.
`manager`'s roots are {staff, person}, while `staff`'s root is {staff}, so
root sets cannot agree on a join of the two. The family is one name for the
whole component. It agrees with check 9b in both directions:
- two types whose closures intersect are in the same family;
- two siblings with disjoint closures share a family but are refused by
  9b first, because `mapped` calls `check_join_types` before `count`.

**What it does not change.** A type in no subtype relation is its own family
and is spelled as today. The staffing fixture has no subtypes, so
`amie/facts.tsv` for staffing is byte-identical (C1c).

**Boundary.** A subtype with its own reference scheme
(`inherits_reference: false`) is still compared by raw value. That agrees
with the checker, which is the ruling's aim. Whether raw values identify
entities across such subtypes is a modelling question outside this repair.

### 6.2 Binding the run record (IL4-Q2)

**The ruling.** Within `gnd-mined-run/1`, with the retained records
re-derived.

**ILC-D3** decides which digest is bound; **ILC-D4** decides whether the AMIE
adapter version moves. They interact:
- §6.1 changes the AMIE rendering for subtype models, so IL-R9's letter asks
  for an `adapter_version` bump;
- `export.json` carries `adapter_version`, so a bump moves every AMIE export
  digest, including `d7756509…` that both retained runs read.

**Recommended pair: ILC-D3 (b) with ILC-D4 (a).**
- The record gains a required `facts_sha256`: the SHA-256 of the
  `amie/facts.tsv` the miner read.
- The import re-renders `facts.tsv` from the model and population it is
  given. A different digest is refused with a new input refusal,
  `facts-mismatch`, exit 3. It is checked after `population-mismatch` and
  before any mapping, and it joins `MINED_INPUT_REFUSALS`.
- `facts.tsv` holds every relation name, every role order and every spelled
  value. Binding it binds the model's reading of the population, which is
  finding 4's case: a role swap. The version bump does not move it.

**Re-derivation.**
- The retained records are `evidence/IL4/live/invocation-{1,2}/reported.json`.
  Each one's new bytes add `facts_sha256` = the digest of that invocation's
  retained `facts.tsv`.
- Each original is kept as `reported-r0.json`, and its digest is listed in
  the record.
- The shipped copies in `src/gnd/examples/staffing/learners/{amie,amie-2}/`
  are replaced by the derived bytes.
- The mined proposal's evidence binds `mined/run` by digest, so
  `amie-2.proposal.json` moves (§8).
- No learner runs.

### 6.3 The comparison tool fails loudly (IL6-Q2)

`tools/ilp_comparison.hold()` no longer catches `IlpError` from `mapped` or
`count` and counts the rule as not holding. Instead, a rule GND cannot map or
count makes the tool print `rule K: <refusal>: GND cannot count this rule; the
table does not report it` to stderr and exit 2. That is distinct from exit 1,
which means stale. `build()` raises a `ComparisonError` carrying that text;
`main()` turns it into the exit.

### 6.4 Infix comparisons in check 9b (IL1-Q1)

`check_join_types` treats the two operands of **every** comparison as one join
when both are variables, whether written infix (`C > D`) or as a declared
predicate. The pair must have intersecting closures. Otherwise the import
refuses `type-confused-join`, naming the variables, as it does for the
declared form.
- A variable against a constant adds no join. An infix comparison declares
  no type, so there is nothing to pair the constant with.
- Today `compares` carries `(compare, declared)` with `declared is None` for
  infix. That case now records a variable–variable pair instead of nothing.
- The returned pair count grows by one for each such pair. C8a pins the count.

### 6.5 ILASP comparison constants (IL2-Q3)

`gnd import ilp-rules --target ilasp` checks each comparison atom's constant
against the thresholds the export renders for that type
(`ilp_popper.thresholds`). The import rebuilds the export from `--labels`, as
it does now to compute coverage, so the thresholds are at hand.
- A constant outside the set is refused as `off-threshold` (ILC-D6), naming
  the clause and the constant. Exit 3.
- The check runs after parsing and before the rewrite, so a parse refusal
  still comes first.
- ILASP's retained run is `wrong :- gt_t_amount(V1,500).`. 500 is a rendered
  threshold, so the run still refuses with `empty-antecedent` (C10).

### 6.6 `extract_program` and interleaved lines (IL1-Q4)

**ILC-D7, recommended (a).** Read from the last `SOLUTION_BANNER` to the next
line of 30 stars, or to the end of the log. Keep every `wrong(...)` line in
that block and skip the other lines (`Precision:…`, a `Warning:`).

The program is then never silently truncated. A rule after an interleaved
line is kept and goes through the same parse and re-check. Invocation 3's
retained log extracts the same one-rule program (C6b).

### 6.7 Popper booleans (IL2-Q1)

`ilp_popper._Parser.term` reads a bare `name` token `true` or `false` as a
boolean, the inverse of what the renderer writes. A quoted `'true'` stays a
string. This is a parser-only fix that changes no golden, so per IL-R9 the
Popper adapter version does not move.

### 6.8 Missing tests (IL1-Q5, IL6-Q1)

- **C8a, T5c's pair count:** `check_join_types` returns the number of type
  pairs it compared, for a clause with three sites on one variable.
- **C8b, `type_closures` with a subtype:** `manager subtype_of staff` gives
  `manager`'s closure {manager, staff}.
- **C8c, refusals by adapter section:** each refusal tuple's names appear
  under that adapter's section heading of `ilp-bridge.md`, and not only
  somewhere on the page:

| Refusals | Section |
|---|---|
| `ilp_asp.REFUSALS` | ILASP |
| `ilp_rules.*` | Boolean rule sets |
| `ilp_amie.*` and `MINED_INPUT_REFUSALS` | AMIE-style miner |
| `ilp_rewrite.REFUSALS` | the shared clause section |

### 6.9 Public names (IL3-Q2, IL4-Q3)

| Today | Public name (ILC-D8 (a)) | Callers |
|---|---|---|
| `ilp_popper._threshold_rows` | `ilp_popper.threshold_rows` | `ilp_rules`, `test_ilp_rules` |
| `ilp._value` | `ilp.export_value` | `ilp_amie` |

- Each new name is added to its module's `__all__`.
- The old private names are removed, not aliased: they are private, and no
  public shim covers them.
- The RF6 census and the layer map are updated where they name these
  functions. `api.__all__` is unchanged: these are module names, not package
  API.

## 7. Decisions

| ID | Question | Options | Proposed |
|---|---|---|---|
| ILC-D1 | Spelling for subtype joins | **(a) The family:** the least top-type id in the subtype component (§6.1). **(b)** Refuse a join between different types by name, `subtype-join`. The owner ruled a fix, so (b) is listed only for completeness. **(c) The root set:** fails for several supertypes | (a) |
| ILC-D2 | Where the family is computed | **(a)** `ilp_amie.family` over `ModelIndex`. **(b)** A new `ModelIndex.subtype_family`. That widens a shared query home and needs an RF6 row | (a) |
| ILC-D3 | What the run record binds | **(a) `export_sha256`,** the ruling's literal words: the digest of the export's `export.json`. If D4 bumps the version, the retained runs can no longer be re-derived honestly. **(b) `facts_sha256`,** the bytes the miner read. It binds the model's reading and the population, and survives version bumps | (b) |
| ILC-D4 | AMIE `ADAPTER_VERSION` | **(a) Bump to "2",** per IL-R9: subtype rendering changed. The staffing export digest moves, `d7756509…` → new. The walk page's printed digest and the IL6 walk golden for `export/amie/export.json` move. The retained runs keep the v1 digest, honestly recorded. **(b) Keep "1",** arguing that no run read a subtype model. That breaks IL-R9's letter | (a) with D3 (b). If D3 (a) is chosen, (b) |
| ILC-D5 | IL1-Q1's scope | **(a)** Variable–variable comparisons only. **(b)** Also type a variable against a constant by the constant's primitive. That is a new typing rule | (a) |
| ILC-D6 | The ILASP constant refusal's name and home | **(a) `off-threshold`,** in a new `ilp_asp.IMPORT_REFUSALS` named by the bridge's ILASP section. **(b)** Reuse `unparsable`. Less exact | (a) |
| ILC-D7 | `extract_program` | **(a)** Every rule line from the banner to the closing star line (§6.6). **(b)** Keep the first run and refuse when a rule line follows it (`truncated-program`) | (a) |
| ILC-D8 | Public names | **(a)** `threshold_rows` and `export_value`, with no private aliases. **(b)** Keep the private names as identity aliases | (a) |
| ILC-D9 | Approval instrument | **(a) Corpus-first.** Exit and refusal predicates are a corpus-first shape (review-convergence): `tests/fixtures/ilp_learners/close/cases.json`, with each case's input and narrated expected exit and refusal, committed red before the code. **(b)** Spec prose | (a) |

## 8. What moves (IL-R7)

The table is for the proposed rulings. Anything else that moves is a finding.

| Artifact | Moves because |
|---|---|
| `src/gnd/mined-import.schema.json` (`run` def: `facts_sha256` required) | D3 |
| `evidence/IL4/live/invocation-{1,2}/reported.json` (derived; originals kept as `reported-r0.json`) | D3 |
| `src/gnd/examples/staffing/learners/{amie,amie-2}/reported.json` | D3 |
| `tests/fixtures/ilp_learners/il4/` run records used by `test_ilp_amie` | D3 |
| `evidence/IL4/live/invocation-2/proposal.json` (derived; original kept) and the IL6 walk golden `amie-2.proposal.json` | the proposal binds `mined/run` |
| The staffing AMIE `export.json` digest: walk page block 9 and the IL6 walk golden `export/amie/export.json` | D4 (a) |
| `tests/test_ilp_amie.py` T9 (line 515): today it asserts that the re-made `export.json` equals the run's recorded `export_sha256`. Under D4 (a) it asserts instead that `facts.tsv` is byte-equal (as now), and that `export.json` equals the recorded digest once `adapter_version` is set back to `"1"`. The retained `outcome.json` is not edited | D4 (a) |
| `docs/reference/ilp-bridge.md`: new refusals `facts-mismatch` and `off-threshold`; the family spelling; the infix join rule; the extraction rule | §6 |
| `cli/tree.json` and the RF1 goldens, if any help text names the record's fields | D3; checked by T8 |

**Expected not to move:**
- `comparison.json` (all 8 rows);
- every IK5 and IK6 golden;
- the Popper, ILASP, rules and llm export digests;
- the refunds walk outputs;
- every other run's retained outcome.

C10 and C11 test that.

## 9. Tests

The cases are corpus-first under D9 (a), and each one is committed red first.

| ID | Case | Expected |
|---|---|---|
| C1a | Subtype model, `manages(manager,team)` + `works_in(staff,team)`; a rule joining them that holds on every head pair | exit 0, admitted (was `does-not-hold`) |
| C1b | `manager subtype_of [staff, person]`; a join of manager with person and one with staff | both count; spelling `person:` for the whole family (least top id) |
| C1c | The staffing export | `facts.tsv` byte-identical to `evidence/IL4/live/invocation-1/facts.tsv` |
| C1d | Siblings `a`, `b` of `t` joined | `type-confused-join`, before counting |
| C2a | A run record without `facts_sha256` | exit 3, schema refusal |
| C2b | `based_at`'s roles swapped in the model (IL4 finding 4's case) | exit 3, `facts-mismatch` (was `type-confused-join`) |
| C2c | The re-derived records | both AMIE imports exit as recorded: 3 `does-not-hold` and 0 admitted |
| C3 | A copied evidence tree with a planted rule over an unknown relation | `tools/ilp_comparison.py` exits 2 naming `rule K` |
| C4a | `wrong(A):- f_order_amount(A,B,C),f_order_quantity(A,B,D),C > D.` (IL1 finding 3) | exit 3, `type-confused-join: variable … joins amount and quantity` |
| C4b | The same with `C > 500` | unchanged: no join added |
| C5a | The retained ILASP hypothesis with 500 replaced by 501, which is not a rendered threshold | exit 3, `off-threshold` (the check precedes the rewrite, so it comes before `empty-antecedent`) |
| C5b | The retained hypothesis, unchanged | exit 3, `empty-antecedent`, as recorded |
| C5c | A hypothesis that joins a refund atom with `gt_t_amount(V,500)`, in the reader's own syntax | exit 0, the comparison kept |
| C6a | A log with a `Warning:` line between two rules in the solution block | both rules extracted |
| C6b | `evidence/IL1/live/invocation-3/raw-stderr.txt` | the retained `program.pl`, byte for byte |
| C7 | A Popper clause with bare `true` | the boolean `true`; a quoted `'true'` stays the string |
| C8a–c | §6.8 | pass |
| C9 | The old private names are absent; the new names are in `__all__` | pass |
| C10 | Every retained run replays to its recorded outcome (IL1–IL6 replay tests) | pass |
| C11 | `tools/ilp_comparison.py` exits 0; the learners walk passes 12 blocks | pass |
| T8 | The plan's controls: RF1 pins, RF5, layering, arch, RF6, built inventory, schema sync, API pins | pass |
| T9 | Installed candidate, both wheel origins (shipped files move) | pass |

**Gate command:** IL6's gate files (`evidence/IL6/gate-files.txt`) plus the
new test file `tests/test_il_close.py`. T9 runs once on the final bytes.

## 10. Out of scope for this part

- Part B, the plan's wording repairs, and Part C, the sweep. Both are in
  the close record.
- The deferred rows: IL5-Q5, IL5-Q6, IL1-Q6, IL2-Q2, IL3-Q3 and IL6-Q3.
- Any learner run. Typing a variable against a constant (D5 (b)).

## 11. Size

Estimate:

| Item | Size |
|---|---|
| Code | ~150 lines over `ilp_amie`, `ilp_service`, `ilp_rewrite`, `ilp_asp`, `ilp_popper`, `ilp` and the comparison tool |
| Corpus | ~20 cases |
| Tests | ~200 lines |
| Docs | ~40 lines |
| Evidence | 3 derived files plus 3 retained originals |

## 12. Owner gate record

**2026-10-29, the owner:** "Go with your recs on ILC-D1 to ILC-D9; implement
the IL-close repairs corpus-first." The approval was given over SHA-256
`17e4e255bf306e19bccf239848b1ebe2c1adbe1863fc4aeacd5b3c5311e87467`, the r1
bytes before this record and the status line.

| ID | Ruling (o) |
|---|---|
| ILC-D1 | (a) the family |
| ILC-D2 | (a) `ilp_amie.family` |
| ILC-D3 | (b) `facts_sha256` |
| ILC-D4 | (a) AMIE `ADAPTER_VERSION` "2" |
| ILC-D5 | (a) variable–variable only |
| ILC-D6 | (a) `off-threshold` in `ilp_asp.IMPORT_REFUSALS` |
| ILC-D7 | (a) every rule line in the solution block |
| ILC-D8 | (a) public names, no aliases |
| ILC-D9 | (a) corpus-first at `tests/fixtures/ilp_learners/close/cases.json` |

## 13. Findings

Recorded as found.

- **ILC-F1 (refutes §6.1's example and C1d's wording).** Siblings `a`, `b` of
  one type `t` share `t`, so their closures intersect and check 9b passes their
  join; they are not "disjoint". The claim §6.1 makes still holds for types in
  one family that share no ancestor. The corpus keeps C1d's intent with such
  types (`y` under `p`, `z` under `q`, joined through `x` under both) and adds
  C1e: siblings now count, as the checker does. No approved answer changed:
  the corpus was not yet committed.
- **ILC-F2 (corpus, before commit).** C4c's first clause had a disconnected
  antecedent, so it tested `disconnected-body`, not the join. It now joins its
  two amounts through `B`.
- **ILC-F3 (signature).** `ilp_amie.family` takes the model, as
  `ilp.type_closures` does, and reads `ModelIndex` inside; §6.1 wrote
  `family(model_index)`.
- **ILC-F4 (C2a's message).** The run-record schema is a root `oneOf` of the
  record and the report, so a record missing `facts_sha256` was reported only
  as "not valid under any of the given schemas". The mined import now
  validates the record against `$defs/run` alone, so the message names the
  field, as C2a expects. No other import's message changes.
- **ILC-F5 (refutes §6.7's "changes no golden").** IL1's
  `test_ilp_bridge.py::test_r5_boolean_atoms_become_booleans_at_boolean_roles`
  pinned that a bare `true` at a **string** role reads as the string `"true"`.
  Under IL2-Q1 it reads as the boolean. Popper quotes every string it is
  given, so only a constant no export rendered reaches that case. The
  assertion now expects the boolean. **Returned to the owner (IL-R7).**
- **ILC-F6 (§8 omissions, all mechanical consequences of D3 and D4).**
  **Returned to the owner (IL-R7).**
  - `tests/fixtures/ilp_learners/il4/expected/{staffing,north}/export.json`:
    `adapter_version` "1" → "2". Their `facts.tsv` and `relations.json` are
    unchanged.
  - `evidence/IL4/live/invocation-2/import-report.json` binds the run record
    by digest, as the proposal does. It is re-derived, and the original is
    kept as `import-report-r0.json`.
  - The walk page's AMIE export block is block 10, not 9. Its digest moves to
    `fead4b6c…`, and a paragraph now says the runs read version 1.
  - `test_ilp_amie.py` T9 also asserted the run's `adapter_version` equals the
    current one. It now asserts the run's is "1".
  - `evidence/IL4/run_amie.py` writes `facts_sha256`, so a future run's record
    is valid. The retained runs are not re-run.
- **ILC-F7 (IL-R3).** The ILASP threshold check is a registry hook,
  `Learner.vet`, so the import service names no learner.
- **Red run.** `evidence/IL-close/red.txt`: 19 failed, 12 passed. Each failure
  is its case's own defect (for example `support-mismatch … GND counts 0` for
  C1a). The 12 that pass pin behaviour the repairs must keep: C1c, C1d, C4b,
  C4c, C5b, C5c, C6b, C8a, C8b, C11, and C8c for the rule-set and fragment
  sections.
