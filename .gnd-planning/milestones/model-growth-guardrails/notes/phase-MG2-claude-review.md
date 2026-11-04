# MG2 diff review (one local reviewer)

Retained text of the reviewer's returned report. **Edited:** the absolute
scratch path is replaced by `<scratch>`; nothing else is changed. One
reviewer is one reviewer. It ran with the repository read-only, could run
targeted tests, probes and mutants, and did not run the docs commands, the
IL6 census or a fresh RF1 recapture. The dispositions are in the spec's
"Review dispositions" section and the phase record, not here.

---

## MG2 adversarial review — additive policy on `gnd evolve`

**Verdict: reject** (two semantic bypasses of the "no new or stronger constraint on a populated fact type" guarantee, both reproduced through `EvolutionService.preview --policy additive`; everything else holds).

### Scope
Read: the MG2 spec with its implementation findings, the full diff (`policy.py`, `models.py`, `service.py`, `cli_service.py`, `commands/evolve.py`, contract, SKILL.md, docs page, release notes, layers map), the fixture, the test file, `evidence/MG2/*`. Ran: `uv run pytest -q tests/test_evolve_additive_policy.py` (70 passed); the spec's gate plus impact selection (19 files, 631 passed, incl. `test_evolve_references` T6, `test_object_type_description` T7, RF1 pins, RF6 query policy, layering, legacy v1/v2 readers, disclosure, skill prose pins); 22 mutants; five probe scripts under `<scratch>/mg2-review/` (`probe_semantics.py`, `probe_cli.py`, `probe_hostile.py`, `probe_order.py`, `run_mutants.py` + `mutant_plugin.py`; outputs in `*.out`, `mutants.txt`). Not run: `tools/run_tutorials.py`, `zensical build`, `check_docs.py`, `test_il6_skill_census.py`, the evidence/census lanes, a fresh RF1 golden recapture.

### Claims confirmed
- Matrix cells and strengthening items as tested: all 70 cases pass; mutants M1, M2, M4, M6, M7, M10, M12, M13, M15–M19 killed.
- Preview with issues is written and exits 3 (`probe_cli` 1a; T3).
- Apply compares options before the retry branch: a live candidate + extra `--populated` exits 3 (`probe_cli` 6b); M21 (check moved after the retry branch) killed by T3a. `--populated` superset exits 3 (4a); order/duplicates irrelevant (4b exits 0).
- Edited `policy_issues` with recomputed digest exits 11 (T3; `probe_cli` 3 with `populated=[]`+`issues=[]` also 11). Removing only `policy_issues` fails the set-together validator (3). Stripping all four fields and applying without `--policy` publishes (1b exit 0) — documented behaviour, confirmed.
- Service re-run: T3b/T3c as claimed; `_evolve_same_review_identity` sees the policy fields (`probe_cli` 7: reviewed stripped vs staged with policy → 11).
- Parity: `parity-before.json` and `parity-after.json` are byte-identical after JSON normalisation (8 fixtures, all `stable: true`); T6/T7 byte pins pass; policy-free preview has no `policy*`/`populated*` keys.
- `--populated` without `--policy` → 3 on both commands; `--policy bogus` → 64; `--policy` twice → last wins (0); `--populated` repeatable.
- Totality: non-string keys, nested lists, bool/float/bigint bounds, `allowed: None`, tuple/list `ranges`, depth 900 all return verdicts without exception. Depth 5000 raises `RecursionError` in `_diff`, but `gnd.input_policy.loads` refuses depth ≥ 900 and non-finite constants before any reader, so it is unreachable from a document (direct-API only).
- Reads: one counted `entry.get("fact_types")`; `ModelIndex` otherwise; RF6/RF1 tests pass with the recorded successor files.
- `detail` strings carry paths and verdict words only (T6 passes; reviewed `_element_modify_detail`/`_constraint_modify_detail`).
- Order dependence (`probe_order`): role ADD before its fact-type ADD is refused by replay (3); hosted constraint spanning a new and the populated FT refused; duplicate-occurrence ADD refused by replay; `allowed`→`ranges` refused.

### Findings

**F1 — blocking. `src/gnd/evolve/policy.py:336`.** A model-hosted constraint MODIFY takes its subjects from `operation.before` only. A constraint whose before-side names only unpopulated fact types can be retargeted onto a populated one, and the MODIFY is then admitted unconditionally (subject "not populated" row). Reproduction (`uv run python …/probe_semantics.py`, section A): before model has `subset order_has_memo.order ⊆ order_has_amount.order`; MODIFY sets `subset_role_seq` to `customer_places_order.order` (populated). Observed: `A hosted-MODIFY retarget onto populated FT -> policy_issues: [] populated: ('customer_places_order',)`; the identical constraint as an ADD: `['constraint.populated.add']`. Refutes the contract line 204 ("subjects are the fact types its role references … name") and O6. Mutant M14 (subjects from `after`) survives the test file. Repair: collect subjects from the union of `before` and `after` for MODIFY (and, for symmetry, DELETE from `before`); add a T2 case "hosted constraint retargeted onto the populated fact type → `constraint.populated.modify`".

**F2 — blocking. `src/gnd/evolve/policy.py:206-207`; contract line 229.** `roles` proper superset is classed weakening for every family, but for a frequency constraint with `bound.min > 1` a wider role projection makes finer groups that must each reach the minimum — a strengthening. Reproduction (`probe_semantics.py`, section B): `customer_places_order` with no sample rows, `--populated customer_places_order`, frequency `roles: [customer], bound {min: 2, max: 10}` modified to `roles: [customer, channel]`. Observed: `policy_issues: []`. Checker confirmation on a population with customer 1 placing one web and one phone order: `gnd check before` → `pass=5 fail=0`; `gnd check after` → `[fail] … Each occurrence of (customer, channel …) appears at least 2 … ('1','web') occurs 1 times` (`fail=1`). A population admitted before is refused after an admitted MODIFY. Refutes O6 and the strengthening table. Repair: restrict the `roles` subset rule to `type == "uniqueness"` (the only family where the ORM semantics are monotone in the role set); for frequency treat a `roles` change as neither. Needs the constraint's `type` passed into `constraint_change` (or judged in `_constraint_modify_detail`). Add a T2 case and a T2a control.

**F3 — hardening. `policy.py:95`.** `sample_population: []` is not populated by design, but no fixture pins it: mutant M9 (`and rows` dropped) survives. Add a case with an explicit empty list.

**F4 — hardening. `policy.py:151` and `:131-139`.** Mutants M8 (bool counts as a number) and M11 (`ranges` compared whole) survive: T12 lacks a bool bound and T2 lacks a `ranges[i].min/max` change. Add both (`ranges[0].min` raised → refused; `bound.min: true` → neither).

**F5 — completeness. `policy.py:337`.** `subjects -= added_fact_types` is dead: `effective_populated` reads only the before model, so a same-proposal id can never be in `populated`; mutant M3 is equivalent (survives). Either delete the line or keep it with a comment that it is defensive; the spec sentence "a subject that is a same-proposal fact type is never populated" is already enforced by the populated set.

**F6 — completeness.** Contract line 246 / docs page: apply compares options "before anything else". It actually runs after argument validation, workspace resolution, reading the proposal and preview, and the proposal-identity check (`cli_service.py:625-646`). Harmless; soften to "before the retry branch and the fresh/reviewed equality", which is what the code comment says.

**F7 — completeness.** A fact-type MODIFY of a fact type the same proposal adds is refused (`probe_order` 3: `['fact_types.modify']`) although nothing existing changes. Conservative, consistent with the matrix; worth a sentence in the contract so agents do not file it as a bug.

### Mutants (`tests/test_evolve_additive_policy.py`, `-x`)

| Mutant | Killed | By |
|---|---|---|
| M1 `_subset` subset→weakening | yes | T1[constraint.populated.modify] |
| M2 `_ordered` ignores direction | yes | T2[range.max lowered] |
| M3 drop `subjects -= added_fact_types` | **no** (equivalent, F5) | — |
| M4 drop `provenance.reviewed_in` neutrality | yes | T2[proposed->confirmed] |
| M6 status transition reversed | yes | T2[proposed->confirmed] |
| M7 modality transition reversed | yes | T2[deontic->alethic] |
| M8 bool is a number | **no** (F4) | — |
| M9 empty `sample_population` populated | **no** (F3) | — |
| M10 allow-list not prefix-closed | yes | T1[object_types.modify (confined)] |
| M11 `ranges` compared whole | **no** (F4) | — |
| M12 `min_inclusive` reversed | yes | T2[min_inclusive true->false] |
| M13 added bound is weakening | yes | T2 bound_max_added |
| M14 hosted MODIFY subjects from `after` | **no** (F1) | — |
| M15 role ADD on existing admitted | yes | T1[role.add (existing)] |
| M16 reference-population source dropped | yes | T2c reference-owned |
| M17 population-artifact source dropped | yes | T2c sources |
| M18 populated DELETE refused | yes | T1[constraint.populated.delete] |
| M19 object-type allow-list + `primitive` | yes | T1[object_types.modify] |
| M21 CLI option check after retry branch | yes | T3a |
| M22 CLI `--populated` check dropped | yes | T3 option agreement |
| M23 CLI preview with issues exits 0 | yes | T2c reference-owned (first failing) |
| M24 CLI fresh preview built from reviewed's options | **no** (equivalent: option equality already enforced) | — |

Kill rate 16/22; four survivors are real gaps (M8, M9, M11, M14), two are equivalent.