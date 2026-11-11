# Phase RN0: repair main's default lane

## 1. Status

**Awaiting owner review, 2026-11-10.** Draft r1. Decisions D1 to D6 are open.
No implementation file is created or edited.

## 2. Provenance

Derives from [the plan](release-0.3.0-plan.md) §12 (amendment approved by the
owner, "Yes, add RN0", 2026-11-10) and from
[experiment E1](../evidence/e1/README.md). The plan gives RN0 no criteria list
of its own beyond §12's row; this spec names them (§3) and the owner approves
them with it. Baseline: main `2490dd77`. No review has run over these bytes.

The classification in §6 was made in this session by reading each failing
assertion, the guard's test and its policy file, and by running the guards'
own scanners at `2490dd77`. It is this session's reading, not a review.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RN0-C1 | each of the 24 guard failures is classified as a stale pin or a real violation, with the evidence | plan §12 | §6 table |
| RN0-C2 | stale pins are re-recorded with a reason, by the mechanism each guard already uses (successor file, regenerated inventory, count literal) | plan §12 | M1 to M6 |
| RN0-C3 | real violations are repaired in source, or registered as a counted exception where the repository's rules allow one | plan §12; AGENTS.md | M7 to M10, D1 to D3 |
| RN0-C4 | the missing packaging guard is added | plan §12, R5 | M1 |
| RN0-C5 | the base lane shows only the 2 known errors and RN1's two tests (N20, N26) | plan §12 | T3 |
| RN0-C6 | Ossie behavior is unchanged by any source edit | this spec (not in the plan) | T2, D5 |
| AGENTS.md | layer map with zero allowances; exact counted query exceptions, no blanket waiver; `ModelIndex` preferred for shared model queries | AGENTS.md "Refactoring dependency homes", "Model queries and family dispatch" | D1, D2, §4 |
| Plan rule 7 | `release.yml`, its pinned test and the dependency freeze are not edited | plan §0 | §9 |
| Plan rule 8 | pause past 1.5 times the estimate | plan §0 | §10 |
| ossie-interchange close | closure covers the measured scope at the bytes it tested | `ossie-interchange/034-milestone-close.md` | §9 boundary, D5 |
| Historical evidence stays immutable | guards extend by authenticated successor files, never by rewriting `code-refactoring` evidence | `tests/support/pyrel_application_successors.py` docstring | M3, M5 |

## 4. The standing rules, bound to this phase

- Plan rule 1 (prepare, never publish): no build, upload or tag here.
- Plan rule 4 (evidence belongs to exact bytes): M7 to M10 change the Ossie
  modules, so the ossie-interchange opt-in oracle evidence no longer describes
  the bytes on main; D5 decides whether that lane is rerun.
- Plan rule 6 and `project.md` rule 6 (measure): the two query budgets are
  settled by running the guard's own scanner on the changed tree (T1), not by
  argument; §6 gives today's measured numbers.
- Plan rule 7 (frozen surfaces): untouched.
- `project.md` rule 1 (totality): M9 routes the Ossie modules' JSON reads of
  packaged schema files through `gnd.input_policy.loads`, the bounded reader
  the rest of the package uses; no new consumer of untrusted input is added.
- `project.md` rule 4 (one walk): M8 gives each document shape one accessor
  for its role list in place of repeated reads.
- `project.md` rule 5 (one home): identity matching has one home,
  `model_identity_matches` in `gnd.values`; M10 makes the importer use it.
- `project.md` rules 2 and 3: no new input-proportional work and no new
  validation boundary; M10 must not change which check refuses first (T2
  includes the importer's refusal cases).

## 5. Goal

At the RN0 tree, the 24 test ids of §6 exit 0, the Ossie test files exit 0
with the same passed count as at `2490dd77`, and the six-shard default lane's
failing list is exactly the 2 known `tests/test_public_optional.py` errors
plus N20 and N26.

## 6. Design

### Classification of the 24 (RN0-C1)

Present since model composition (`54a47612`):

| Tests | Finding | Class |
|---|---|---|
| `test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged` for `_cmd_evolve_apply`, `_cmd_evolve_preview`, `_cmd_validate`, `_evolve_emit_claim`, `_evolve_error_exit` (5) | the function bodies changed after their last recorded successor digest; the range `483b49ea..54a47612` holds UG2, UG3 and MC1 to MC3, which changed these commands on purpose | stale pin |

First present after PR 160:

| Tests | Finding | Class |
|---|---|---|
| `test_conformance_payload.py` (1) | `gnd/ossie-loss-report.schema.json` is not in `VENDORED_SCHEMAS` | missing guard entry. The three files under `src/gnd/schema/ossie/` are outside this guard's glob and have no packaging check at all |
| `test_disclosure_mode.py` (2) | 52 leaves against a pinned 50; 32 checked against `50 - 16 - 4` | stale count, if the two new leaves are in the table; the count assertion fails before the later ones run, so this is confirmed only at implementation |
| `test_packaged_skills.py` (1) | one new link, `gnd-export/SKILL.md` to the representation format's Ossie anchor | stale inventory |
| `test_rf5_commands.py::test_all_parser_paths_receive_command_handlers` (1) | 61 parser paths against a pinned 59 | stale count |
| `test_rf5_commands.py::test_entrypoint_rule...`, `test_rf5_review_regressions.py` (1), `test_rf7_structure.py::test_current_graph...`, `test_rf8_structure.py` (4 in all) | six lazy imports from command modules with no policy row: `gnd.commands.checking` to `gnd.ossie_import` and `gnd.safefs`; `gnd.commands.export` to `gnd.artifacts`, `gnd.errors`, `gnd.export.ossie` and `gnd.safefs` | real: the entry-point rule allows a named service or an exact exception with a reason, and these have neither (D1) |
| `test_rf6_query_policy.py::test_exact_live_query_policy`, `test_literal_subscription...`, `test_rf9_repairs.py` (2) (4 in all) | 13 distinct direct reads of `fact_types` or `roles`, 14 occurrences, in `export/ossie.py` (8), `export/ossie_formulas.py` (1) and `ossie_import.py` (5 distinct, 5 occurrences) | real, and over budget: 378 found against a ceiling of 365 (364 approved) |
| `test_rf6_query_policy.py::test_original_query_metric...` (1) | 315 against `current` 309 and a ceiling of 310 that the test pins as a literal | real, and over budget by 5 |
| `test_rf6_query_policy.py::test_dynamic_candidate_inventory...`, `test_dynamic_duplicate...` (2) | 132 new dynamic-read rows (143 occurrences): `ossie_import.py` 50, `export/ossie.py` 35, `export/ossie_formulas.py` 25, `export/pyrel_rules.py` 12, `safefs.py` 10; 1 approved row no longer found | stale inventory; this guard has no ceiling |
| `test_rf7_structure.py::test_complete_routing...` (1) | `json.loads` called directly: `export/ossie.py:54`, `ossie_import.py:102`, `103`, `106` | real: every module reads JSON through the shared bounded reader |
| `test_rof4_accept_identities.py` (2) | `ossie_import._bounded_model` compares a computed identity with `==`; it and `export/ossie.render_ossie` call `model_identity` directly | real for the importer (the shared matcher is bypassed); the exporter writes the identity into the sidecar, which makes it a producer like `gnd validate --identity` (D3) |

Counts: 5 + 1 + 2 + 1 + 1 + 4 + 4 + 1 + 2 + 1 + 2 = 24.

Of the query reads, the five in `ossie_import.py` (four `.get`, one subscript)
read a foreign Ossie document, whose format has its own `roles` key. They are
not GND model queries; the scanner matches the key name. The eight in the
exporter read the GND model's JSON document, where the exporter records source
paths for the loss report.

### Modules

| ID | Path | Change | Lines (estimate) |
|---|---|---|---|
| M1 | `tests/support/runtime_schema_inventory.py` | add `gnd/ossie-loss-report.schema.json` to `VENDORED_SCHEMAS` | 1 |
| M2 | `tests/test_disclosure_mode.py`, `tests/test_rf5_commands.py` | the count literals 50 to 52 (two sites) and 59 to 61, each with its comment naming the two Ossie commands; any later assertion that then fails is a finding, not a literal to change | 4 |
| M3 | a new successor file under `.gnd-planning/milestones/release-0.3.0/evidence/RN0/` and its registration beside the existing RF5 body successors | the five command bodies: `before` is the last recorded digest, `after` the present one, with a reason per function naming the phase that changed it (found by `git log -L` per function) | about 40 |
| M4 | `tests/test_packaged_skills.py` | regenerate `EXPECTED_RELATIVE_LINKS` as its comment says; the diff must be the one added link | 1 |
| M5 | new `evidence/RN0/dynamic-query-successor.json` and `evidence/RN0/query-successor.json`, registered in `tests/support/pyrel_application_successors.py` | the dynamic inventory delta after M8 and M9 (added rows, the one removed row); the exact query rows that remain after M8 | about 140 rows, generated |
| M6 | `tools/gnd_entrypoints.json` | per D1 | 6 rows |
| M7 | `tools/gnd_layers.json` | no change expected: the three Ossie modules are mapped. `gnd.ossie_import` sits in layer `entry` beside `gnd.rai_import`; left as is | 0 |
| M8 | `src/gnd/export/ossie.py`, `src/gnd/export/ossie_formulas.py`, `src/gnd/ossie_import.py` | per D2: read the model's fact types and roles through `ModelIndex` where the exporter needs model facts, and through one accessor per document shape where it needs document positions or a foreign Ossie relationship | about 40 |
| M9 | the same three files | the four `json.loads` calls on packaged schema resources go through `gnd.input_policy.loads` (the importer already imports it) | 4 |
| M10 | `src/gnd/ossie_import.py`, `tests/test_rof4_accept_identities.py` | per D3 | about 10 |

### Normative order

None added. The rules repaired here keep their homes: the entry-point policy
in `tools/gnd_entrypoints.json`, the query budget in the RF9 allow-list with
its successors, identity matching in `gnd.values`.

## 7. Decisions

| ID | Question | Readings and what each costs | Recommendation |
|---|---|---|---|
| D1 | How do the two Ossie commands satisfy the entry-point rule? | (a) six exact exception rows with reasons, as `gnd.rai_import` and the other thin adapters have: no source change. (b) new service modules (`gnd.export.ossie_service`, and one for import) bound as service targets: about 60 source lines moved, the shape the rule prefers for new work. Neither changes a command's exit code | (a) |
| D2 | The Ossie modules exceed both query budgets (378 against 365; 315 against 310). | (a) reduce the reads in source (M8) until both budgets hold, and record what remains as counted rows. The room is 1 occurrence in each budget, so nearly every read must go; whether that is reachable is not known until it is tried. If it is not, the phase stops and returns to the owner with the measured numbers. (b) raise both ceilings by the measured excess and record all 14 as counted rows: no source change, and the two pinned ceilings (365, and the literal `(310, 320)`) move for the first time. (c) raise the ceilings only for the five foreign-document reads, which are not model queries, and reduce the exporter's eight in source | (a), with the stop stated; (c) is the fallback I would bring back if (a) does not fit |
| D3 | Identity sites in the Ossie modules | (a) the importer compares through `model_identity_matches` and joins the pinned site list (7 to 8); the exporter is added to the producer set beside `_print_model_identity`. The importer would then accept a sidecar bound by either identity. (b) both are added to the exact lists as they are, canonical identity only. The readings differ in behavior: under (a) an import whose sidecar carries the legacy digest verifies; under (b) it does not | (b) for behavior: the Ossie sidecar format says it carries the canonical identity, and widening what an import accepts is a product change this phase should not make. Under (b) no source changes for M10; two test sets gain an entry each, with the reason |
| D4 | Approval instrument | this prose, or a fixture corpus first. The 24 failing guards and the existing Ossie tests are already the corpus; the phase adds no format, exit contract or predicate | prose |
| D5 | Rerun the opt-in `ossie_oracle` lane after the source edits? | The ossie-interchange close rests on that lane for the pinned validator and parser. M8 and M9 change the bytes it tested. Running it needs the lane's pinned inputs on this machine and is an opt-in lane the owner selects. Not running it leaves the 0.3.0 Ossie code checked by the default-lane Ossie tests only | run it once, on the RN0 tree, if its inputs are present offline; if they are not, say so and stop for a ruling |
| D6 | A review over this spec before implementation? | the owner's call; the phase diff gets one independent reviewer either way | none |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | the 24 ids of [failed-base.txt](../evidence/e1/failed-base.txt) other than N20, N26 and the two errors | exit 0. Each was exit 1 on the base: that list is the red-first record |
| T2 | `uv run pytest -q tests/test_ossie_consumer.py tests/test_ossie_export.py tests/test_ossie_external_oracle.py tests/test_ossie_formulas.py tests/test_ossie_import.py tests/test_pyrel_rules.py tests/test_rf1_cli_pins.py tests/test_rf1_layering.py --tb=short` | exit 0 with the passed count measured at `2490dd77` before the first edit (the ossie close recorded 352 for this selection) |
| T3 | six-shard default lane on beast-3 at the RN0 tree | the failing list is the 2 known errors, N20 and N26, and nothing else |
| T4 | export of the packaged refunds model and of every model the Ossie export tests use, before and after M8 and M9 | byte-identical ontology, sidecar and loss report; a deliberate one-character change to a role name in a scratch model changes the output (the comparison can fail) |
| T5 | the guards' own dirty controls, already in the suite (`test_dynamic_duplicate_inventory_row_is_refused`, the entry-point mutants, the routing mutant `new_reader.py`) | exit 0: each control still refuses its injected violation after the new rows are added |
| T6 | `uv run ruff check` | exit 0 |
| T7 (D5) | `uv run pytest -q -m ossie_oracle` over the Ossie test files | exit 0, or a recorded refusal naming the missing input |

Branches: every re-recorded pin has a guard that fails when the pin is wrong
(T1 is those guards). The risk a re-record carries is the opposite one, a pin
moved to bless a defect; T2 and T4 are the checks against that for the source
edits, and M3's per-function reasons are the check for the five command
bodies. M2's count literals are covered only by the later assertions in the
same tests.

Verification selection: plan-mandated, T3; direct, T1; impact closure, T2, T4
and T5; broader lanes (`evidence`, `census`, the others) not selected, as
RN-D11 rules; `ossie_oracle` per D5.

## 9. Out of scope for this phase

N20 and N26 (RN1 owns them); the version bump; any change to what an Ossie
export or import accepts or writes; a packaging check for
`src/gnd/schema/ossie/*.json` beyond the note in §6 (RN2's installed probe
exercises them); `release.yml`; the upstream converter pull request;
rewriting any `code-refactoring` evidence file.

Boundary to carry into the record: T4 shows equal bytes on the models tested,
not on every model; without T7 the pinned validator has not seen the changed
exporter.

## 10. Size

Estimate: about 55 source lines (M8 to M10), about 12 test and support lines,
6 policy rows, about 180 generated evidence rows. Under D2 (b) and D3 (b) the
source figure falls to 4 lines (M9 only). The stop rule applies at 1.5 times
the source figure of the options ruled.

## 11. Approval instrument

This prose (D4).

## Verification commands

```bash
uv run pytest -q tests/test_conformance_payload.py tests/test_disclosure_mode.py tests/test_packaged_skills.py tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py --tb=short
uv run ruff check
```

At `2490dd77` the first command gives `24 failed, 559 passed, 1 deselected`.
Unresolved: the beast-3 shard invocation is the E1 script
(`evidence/e1/README.md`); the `ossie_oracle` inputs' location (D5): the lane reads its pinned checkout
from the `GND_OSSIE_ORACLE_ROOT` environment variable, which is not set in
this session.
