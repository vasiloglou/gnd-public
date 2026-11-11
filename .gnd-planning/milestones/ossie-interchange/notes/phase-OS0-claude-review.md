# OS0 independent review: ossie-interchange

## Decision: changes requested before OS0 completes

The measured outputs I could read are internally consistent. I could not refute the E1, E3/E3b or E5 results. The three criteria are not fully supported as worded, though:

- **OS0-C1** holds for the 14-file census, but that census is narrower than plan predicate 1 and the README doesn't disclose the gap. Four rows also carry dispositions the evidence itself shows to be wrong.
- **OS0-C2** has a recorded result and limits for every experiment, so it holds. The controls behind E4 and E6 are thinner than the README implies.
- **OS0-C3** is solid for OD2 and the `relationalai` target. The OD4 reading half and the E6 modality count carry no information.

I read the worktree copy of `.gnd-planning/…` with Read, Glob and Grep only. My attempt to glob the main checkout was denied, so I didn't use it. Paths below are relative to `.gnd-planning/milestones/ossie-interchange/` unless they start with `src/`.

## Findings

**F1 (High): census scope is narrower than plan predicate 1, and the gap is undisclosed.**
- The census glob is depth-1 `*.orm.yaml` only (`notes/phase-OS0-spec.md:78-80`, `evidence/OS0/reproduce/inventory.py:23-26`). It yields 10 example models plus 4 skill examples (`evidence/OS0/census.txt`).
- `Glob src/gnd/examples/**/*.orm.{yaml,yml,json}` returns 37 files, so 27 packaged example models are outside the census. Glob is not git-aware, so I did not check that each is tracked.
- Plan predicate 1 (`notes/ossie-interchange-plan.md:36-37`) says "every packaged example model".
- The excluded models contain the constructs the inventory reports as unobserved:
  - `subset` at `src/gnd/examples/expense/model.orm.json:287,309,331`, `release_governance/approval-proof/model.orm.json:51,73,95` and `release_governance/policy/model.orm.json:101`.
  - `exclusion` at `plan_apps/access/model.orm.json:186` and `plan_apps/course/model.orm.json:346`.
  - `frequency` at `plan_apps/course/model.orm.json:151`.
  - `dynamic_rules` at `plan_apps/course/model.orm.json:452-625`.
  - `includes` at `expense/teams/sales.orm.json:4`, and the same key in `engineering.orm.json` and `sales-v2.orm.json`.
- The inventory reports zero for `subset`, `exclusion`, `frequency_*` and `dynamic_rule` (`evidence/OS0/inventory.json:34-40,64`), and has no `include:unsupported-route` rows.
- Consequences:
  - "27 absent, census data cannot establish behavior" (`phase-OS0-spec.md:184-186`) is true of the 14-file census only. These constructs do occur in packaged examples.
  - Predicate 7 (include-bearing models) has no measured rows. The `includes` rule at `inventory.py:160-161` is dead code with no assertion.
  - E2 and E6 inherit the same narrowing.
- Fix: either widen the census or state in README and 003 that it covers 14 of 37, with the reason.

**F2 (High): E4's "zero reading-order exceptions" never exercised a census reading.**
- `bound_reading` runs only when `target != prefix` (`inventory.py:138-149`). `reorders` is `[]` (`evidence/OS0/E4.json:56`), so no census reading was ever bound.
- The only evidence for reading binding is the synthetic asserts at `inventory.py:288-301`. `E4.json:58` records the control as a prose string, not a result.
- `reading` pointers are classified `native` unconditionally (`inventory.py:189-195`).
- The census has same-type readings that need role disambiguation in Ossie `{Concept:role}` form: `src/gnd/examples/rule_check/model.orm.yaml:15` (`{Component} imports {Component}`, roles `importer`/`imported`) and `src/gnd/examples/staffing/model.orm.yaml:58` (`{Staff} mentors {Staff}`).
- The README claim (`evidence/OS0/README.md:13`) should be reworded to "no census fact type needs reordering". That is a different claim from "readings survive".
- The two non-prefix exceptions are real and correctly listed (`E4.json:4-55`): `expense_reimbursed`, whose determinant is smaller than n−1, and `employee_works_on_project`. Their reasons live only in README and spec prose, not in the JSON.
- "Inherent in Ossie set semantics" for the second one rests on `ontology.md`, which OS0 did not measure.

**F3 (Medium): E6's OneToOne count excludes implicit reference relationships.**
- `one_to_one: []` (`evidence/OS0/E6.json:3`) counts explicit `fact_types` only (`inventory.py:122`).
- The authored document uses `multiplicity: OneToOne` for every identifying relationship (`evidence/OS0/refunds.yaml:23,32`). The census has 28 `reference` instances (`inventory.json:15`), so the export will emit OneToOne at least that often.
- In E3's output both OneToOne and ManyToOne become `m.Property` (`evidence/OS0/E3-refunds.pyrel.txt:12-14`). The converter does not distinguish them, so "states both, no residue" cannot be checked at the consumer.
- README line 15 ("Add an authored OneToOne control in OS1") understates this: OneToOne is needed for identification in OS1 regardless.

**F4 (Medium): the modality check is true by construction, and the spec's negative control is missing.**
- Everything unproven defaults to `extension` (`inventory.py:196`). Constraint pointers can only be `native` for `type`/`scope`/`roles` (`inventory.py:162-169`). The assert at `inventory.py:205` therefore cannot fail in practice.
- Spec §8 (`phase-OS0-spec.md:156`) requires controls that "detect a missing modality disposition". `inventory.py:278-286` is a positive assert only. No fixture with a missing or native modality is shown to be caught.
- The count cross-check does hold: 73 + 4 = 77 = `constraint_common` 77 = 55 inline + 22 top-level (`inventory.json:25-27`, `evidence/OS0/constraint-census.json`).

**F5 (Medium): "measured disposition" means rule-classified under the proposed mapping.**
- `native` rows come from hard-coded rules in `classify` (`inventory.py:155-196`), derived from plan §2.1. Only `refunds.yaml` was run through the upstream tools.
- What is checked is pointer completeness and uniqueness (`inventory.py:249-262`). The re-walk reuses the same `children` and `pointer` helpers, so it catches omissions but not shared encoding bugs.
- Pointers are of the YAML-parsed document, not the source bytes. Duplicate YAML keys would collapse silently.
- The phrase "measured" in C1 should be qualified.

**F6 (Medium): the source-schema refusals contradict the inventory dispositions.**
- GND's own schema rejects three census models for four camel-case role names: `evidence/OS0/gnd-validation.json:130,154,166` (exit 3). The same errors are in `inventory.json:1611,2204,2451`.
- The corresponding rows are still `native / relationship-role`: `inventory.json:1810` (`issueNumber`), `2377` (`occurredOn`), `2547` (`startDate`) and `2607` (`fullName`).
- Under predicate 3 these pointers should be `refused`, or the models excluded. The plan says export reads only validated models (`notes/ossie-interchange-plan.md:112`).
- Predicate 1 cannot pass for these three models until an example, the schema or the census changes. This is disclosed as a future gate (`phase-OS0-spec.md:180-183`), but no ruling is recorded.
- The consistent figures (3 failing models, 4 errors, 11 of 14 exit 0) are accurate.

**F7 (Medium): E2 probes confound grammar reach with probe wording.**
- `uniqueness-external` fails on an undefined alias `other` (`evidence/OS0/E2.json:41`, `formulas.json:9`).
- `anchored` is built to fail (`formulas.json:42-45`).
- `subtype-partition` fails on `(BookItem OR` (`E2.json:81`), while the `value` probe accepts `OR` (`formulas.json:34`). The `textual` probe fails on `==` after a dotted path (`E2.json:101`), while `value` accepts `==` after a bare name. So these failures are operand-form failures, not kind-level failures.
- The README hedges correctly ("results of those forms only", ring is self-loop only at `formulas.json:25`).
- Scope liveness is adequate: failing probes appear at concept, relationship and top scope.
- Do not carry "fails" kinds into OS2 as "grammar cannot state it".

**F8 (Low): E3's `require_count` is a fragile counter, but the claim holds.**
- `convert.py:36-38,54` counts only attribute-style `.require(` calls and has no positive control.
- The zero holds on read:
  - `refunds.yaml:40` contains `requires: ["Amount <= 1000"]`.
  - `E3-refunds.pyrel.txt` has no `require` text.
  - `E3-flights.pyrel.txt` has no `require` text either, while `derived_by` does convert (`E3-flights.pyrel.txt:124-127`).
- Observation for OS4: the `Model` concept is emitted as the variable `Model_2` (`E3-flights.pyrel.txt:35`), so declaration matching must key on concept strings.

**F9 (Low): process notes.**
- Spec §5 says to compare `src` and `tests` against d5156595 (`phase-OS0-spec.md:55-56`), but `003-OS0-candidate.md:26` diffs against 54483d03. They are equivalent only if PR #159 touched no `src` or `tests`.
- E3b's raw PyRel is not in the manifest. Only the matching `source_sha256` values and the empty `source_diff` back the "byte-identical" claim (`E3.json:15,138`, `E3b.json:15,126,139,159`). That evidence is adequate but indirect.
- OD2 is ruled correctly by its own terms: concept and relationship are both rejected by the validator and the parser (`E1.json:36-71`). Root-level and role-level extension points were not probed. That is outside the spec but relevant to the sidecar's "keyed by element id" design.

## Claims checked

| Claim | Result |
|---|---|
| 14 census paths, 2,673 pointers, 47 `refused` | Counts match: 47 rows match `population:out-of-scope`, all `sample_population` (growth ×1, movie_catalog ×4); 2,673 rows each carry one disposition. Not re-run. |
| 62 definitions, 35 observed, 27 absent | Plausible from `inventory.json:10-73`, but the 27 depend on the narrow census (F1). |
| 55 inline + 22 top-level = 77 constraints; 73 alethic + 4 deontic | Consistent across `inventory.json`, `constraint-census.json` and `E6.json`. |
| E1: both locations exit 1/1 with a passing baseline | Confirmed (`E1.json`). OD2 sidecar follows. |
| E2: 5 of 9 accepted, malformed fails | Count confirmed. Probe-wording limits per F7. |
| E3/E3b: both convert, zero `require`, identical source digests | Confirmed. `require` is skipped, `derived_by` is emitted. Target 1.39.0 follows the spec's rule. |
| E5: shape errors precede name errors in both tools | Confirmed (`E5.json:51-74`). |
| E4: 65 fact types, 2 non-prefix, 0 reorders | Confirmed. The reading claim is vacuous (F2). |
| E6: OneToOne none, modality 77 | Counts hold. The OneToOne claim excludes reference relationships (F3). Modality is by construction (F4). |
| Census primitives | Only String, Integer and Date appear, so the `Duration` rule (`inventory.py:172-174`) is untested. |

## Gates my read cannot reproduce

- Rerunning `inventory.py`, `formulas.py` and `oracle.py`, or the "11 outputs matched" and independent-traversal claims in `003-OS0-candidate.md:16-25`.
- The SHA-256 values for spec r4 (`47b62ba0…`), the amended spec (`dba50826…`), the manifest (`f790b745…`) and the post-tag plan digest (`f9b2a9c9…`).
- Whether `validator.evolve(schema=<bare $ref branch>)` resolves `#/$defs/…` at `inventory.py:59`. The consistent definition counts (55 + 22 = 77, 29 + 2 = 31) suggest it works, but I can't confirm it.
- The upstream source bytes at the two pinned commits, wheel digests and package versions, since those are in scratch and not in the repo.
- Whether the 27 excluded models are git-tracked, the `git diff` checks, ruff, and the component-index check.
- The E2 acceptances and E5 "exit 0" results, which need the upstream parser at the pin.
- Whether any hand-translation fidelity claim (`refunds.yaml` against the census refunds source) matches what the exporter will emit. I compared by eye only.
