# IL-close adversarial review (step 4)

One reviewer is one reviewer. A single general-purpose agent reviewed
`git diff 930face 2c4fba9` (the red corpus, then the repairs) on 2026-10-29,
reproducing each finding before reporting it. It wrote only under the session
scratch directory, written `<scratch>` below, and ran no learner. Its report
is retained as returned, with the scratch prefix replaced.

## The report

I reviewed `git diff 930face 2c4fba9` and found 1 blocking defect, 4 hardening
defects and 2 completeness gaps. I reproduced every finding. All scratch files
are under `<scratch>/review/` (called `$S` below). I edited no repository files.
To compare with the old behaviour I extracted `930face:src` to `$S/old/src` and
ran it with `PYTHONPATH=$S/old/src`. `uv run pytest tests/test_il_close.py
tests/test_ilp_amie.py -q` gives 109 passed.

### Findings

**1. Blocking: family spelling lets values of different primitives meet, and the import then crashes with an internal error.**
- **Location:** `src/gnd/export/ilp_amie.py:69-113` (`family`, `spell`); the crash is raised at `ilp_service.py:705`.
- **Repro:** `$S/ownref/model.orm.yaml`, which validates OK, has `staff` referenced by a String code and `manager subtype_of [staff]` with `inherits_reference: false` and its own Integer reference. The population is `manages {manager: 1, team: t1}` and `works_in {staff: "1", team: t1}`; the rule is `?a f_manages ?b => ?a f_works_in ?b`. Run `$S/mined.sh $S/ownref "<rule line>"`; it exports, writes a valid run record and imports.
- **Observed:** the export spells both values as `staff:1`. The import prints `internal: constraints[0] holds by GND's count but the checker says 'warning'` and exits 70. The old code refused it as `rule 0: support-mismatch` (exit 3).
- **Expected:** a named refusal, or a spelling that keeps the checker's distinction between raw values. The spec's §6.1 "Boundary" claim (raw values agree with the checker) is refuted, because the spelling erases the primitive. The miner also sees the merged values.
- **Fix:** include the primitive or value kind in the spelling when a family mixes primitives. Alternatively, keep an own-reference subtype (`inherits_reference: false`) out of its supertype's family, or refuse such a join by name before counting. Add a corpus case.

**2. Hardening: `family()` falls back wrongly on a cyclic subtype graph, so IL4-Q1's false refusal comes back.**
- **Location:** `ilp_amie.py:97`, the `names.get(root(identifier), identifier)` fallback.
- **Repro:** `$S/cyc/model.orm.yaml` is the subtype fixture with `staff subtype_of [manager]` added. `gnd validate` accepts it (exit 0). Then `$S/mined.sh $S/cyc "<C1a rule>"`.
- **Observed:** `family()` maps `{'staff': 'staff', 'manager': 'manager', ...}`. `facts.tsv` holds both `manager:m1` and `staff:m1`, and the import refuses `rule 0: support-mismatch ... GND counts 0 of 2`. Meanwhile `type_closures` joins the two types, which contradicts the docstring ("closures intersect ⇒ one family").
- **Fix:** name a component that has no top type by its least member id, or refuse cyclic hierarchies.

**3. Hardening: `check_thresholds` refuses an undeclared comparison predicate under the wrong name.**
- **Location:** `src/gnd/export/ilp_asp.py:485`.
- **Repro:** `uv run python $S/p_ilasp.py $S` with `wrong :- f_refund_amount(V1,V2), gt_t_bogus(V2,5).`
- **Observed:** `clause 0: off-threshold: gt_t_bogus compares with 5 ...`. The old code said `clause 0: unknown-predicate: 'gt_t_bogus' is not an exported predicate`. Here `types.get` returns None, so the offered threshold set is empty.
- **Fix:** skip predicates that are not in `neutral["comparisons"]`, so the rewrite names them `unknown-predicate`.

**4. Hardening: the new `_amie.render` call can refuse with export-side names before `facts-mismatch`, out of the documented order.**
- **Location:** `ilp_service.py:629`.
- **Repro:** `$S/norel` holds the subtype model with `covers: []`, a valid record and `facts_sha256` set to `"0"*64`.
- **Observed:** new code: `no-relations: the population covers no binary asserted fact type ...` (exit 3). Old code: `rule 0: open-world-head: ...`.
- **Why it matters:** `no-relations` is not among the import's documented refusals; it also hides the facts mismatch; the same path moves `unrepresentable` and `too-large` ahead of the mapping.
- **Fix:** catch an `IlpError` from `render` and report it as `facts-mismatch`, or document these names in the import order.

**5. Hardening: `tools/ilp_comparison.py` still exits 1 with a traceback when a rules file is unparsable, and exit 1 is the documented "stale" code.**
- **Location:** `tools/ilp_comparison.py:138` and `:159`; only `ComparisonError` is caught (`:232`).
- **Repro:** copy the evidence, il4, il6 golden and bridge into `$S/cmp`, append `garbage line` to `IL4/live/invocation-1/rules.txt`, then run `uv run python tools/ilp_comparison.py --root $S/cmp`.
- **Observed:** `Traceback ... IlpError: unparsable: line 9: 1 tab-separated fields, not 8`, exit 1.
- **Fix:** convert `IlpError` from `parse_rules`, `_mined_inputs` and `pairs` into `ComparisonError`, so it exits 2.

**6. Completeness: the order of `facts-mismatch` among the input refusals is untested.**
- **Location:** `tests/test_il_close.py:159` only compares the tuple; the T5 cases keep `facts_sha256` valid.
- **Repro:** a mutant (`$S/mut/src`) moves the facts check before `learner-mismatch`. `PYTHONPATH=$S/mut/src uv run pytest tests/test_il_close.py tests/test_ilp_amie.py -k "c1_c2 or t5 or c2_ or facts"` gives 25 passed. The mutant is confirmed live: with the `$S/ord` record (wrong learner and wrong facts) it prints `facts-mismatch` where HEAD prints `learner-mismatch`.
- **Fix:** add a case with both population and facts mismatched (expect `population-mismatch`), and one with both learner and facts mismatched.

**7. Completeness: the docs disagree with the code on when facts are checked.**
- **Location:** `docs/reference/ilp-bridge.md`, AMIE section: a model that reads the population differently "is refused before any rule is read".
- **Repro:** unparsable `rules.txt` plus a mismatched `facts_sha256` (`$S/ord`) gives `unparsable: line 1: ...`, exit 3. The rules are parsed before the run record is even read.
- **Fix:** change the wording to "before any rule is mapped".

### Not reproduced / not a defect
- I did not mutation-test the `vet` hook's position after the run-record bindings (`export-mismatch` before `off-threshold`).
- In `hold()`, the fallback for an `IlpError` without the `rule K:` prefix appears unreachable: every mapping and count error carries the prefix. If it were reached, the message would still name `rule K`.
- A bare `true` at an Integer role is admitted by the rewrite as `quantity: true`. That is not new: the old code admitted the string `"true"` there. The checker keeps `True` distinct from `1` (`$S/boolchk`: `true` passes, `1` warns), so nothing wrong is admitted. The string-role change is ILC-F5, already returned to the owner.
- A clause refused at the rewrite is now outranked by a later clause's `off-threshold` (two clauses: the new code reports `clause 1: off-threshold`, the old reported `clause 0: unknown-predicate`). This follows the spec's "before the rewrite" and the docs, but refusals are no longer reported in clause order.

### What held
- Infix join: an operand only in the comparison gives `unbound-comparison`; the chain `C > E, E > D` gives `multiple-comparisons`; `D < C`, `>=` and `=` are all refused `type-confused-join`; an entity comparison gives `comparison-type`.
- `check_thresholds`: a negative constant is refused `off-threshold`; `lt_` with a rendered threshold passes; a NAF literal is left to `negation-as-failure`.
- `extract_program`: multiple banners use the last block; with no closing line it reads to the end of the log; no banner or an empty block gives `""`; rules after the closing line are dropped.
- A missing supertype is refused by model validation.
- C1b–C1e behaviour, the `$defs/run` validation message, and the evidence: both `reported.json` equal r0 plus the `facts_sha256` of the retained `facts.tsv`, the shipped copies are byte-equal, and the r0 digests match the test's `R0`.
- Focused tests: 109 passed.

## Reproduction and triage (the author)

Every finding was reproduced from the reviewer's scratch inputs before any
fix. Each fix has a regression test in `tests/test_il_close.py` (R1 to R6),
shown red against `2c4fba9` in `evidence/IL-close/review-red.txt`. R6 passes
on `2c4fba9`, whose order is right; it is shown red against the reviewer's
mutant instead (3 failed).

| # | Class | Disposition |
|---|---|---|
| 1 | blocking | **fixed, R1**: a subtype joins its supertype's family only when it inherits the reference (option 2 of the reviewer's fix). An own-reference subtype's join is then refused `support-mismatch`, as before IL-close: a false refusal, never an admission or exit 70. ILC-F8 records the refuted §6.1 "Boundary" |
| 2 | hardening | **fixed, R2**: a component with no top type is named by its least member |
| 3 | hardening | **fixed, R3**: an undeclared comparison is left to the fragment table |
| 4 | hardening | **fixed, R4**: a re-render refusal is `facts-mismatch`, naming the export's reason |
| 5 | hardening | **fixed, R5**: any `IlpError` reading the staffing rows is exit 2 |
| 6 | completeness | **fixed, R6** |
| 7 | completeness | **fixed**: "before any rule is mapped" |
| not-reproduced 4 | — | **accepted as specified**: the threshold check runs over every clause before the rewrite (§6.5), so a later clause's `off-threshold` outranks an earlier clause's rewrite refusal. Both refuse the set (exit 3); recorded in the record's boundary |
