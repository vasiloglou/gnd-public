# Phase RC1: declared identity, report version 15

## 1. Status

**Owner-approved (2026-11-06): corpus and spec r8; implementation in
progress.** The owner approved the RC1 corpus (commit 8b2d403a) and
decisions D1-D7 with the words "Approve, implement" on 2026-11-06. Prior
status (r8): "Owner-decided (2026-11-06), approval pending on the corpus
(§11)."

Earlier gate (r7 → r8): The
owner ruled the step-2 asks over r7 (sha256 `21ca59f9…85d2`, commit
6916066f); see §7 D8-D11 and the gate notes below. Approval of the design
is given by reading the corpus (corpus-first); no implementation file is
created or edited until the owner approves the corpus. Prior status (r7):
"Awaiting owner review (step 2), 2026-11-06."

Gate notes (o), 2026-11-06, the owner's answers verbatim:
- Approval instrument (D11): "Corpus-first (Recommended)".
- Review over the spec bytes: "No review (Recommended)".
- D8-D10: "Approve all as proposed (Recommended)".
- RC-D1 timing: "Start now (Recommended)": the merge base is recorded
  first (V1) while PR 99 is open.
- D1-D7 were not asked one by one at this gate; they are put to the owner
  with the corpus, whose cases exercise each of them.

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved 2026-11-06. Sections used: §0, §2.1, §3, §4 RC1, §5, §6, §7, §8,
  §9 RC1 row, §10.
- Request: GR-D1, GitHub issue 92.
- Inspection baseline: `origin/main` 8bfbe417 (also this branch's merge
  base, re-checked 2026-11-06).
- Prior phase records: none; RC1 is the first phase. Inherited boundary:
  the plan-gate record says r6 itself carries no review opinion.
- Review history of these bytes: Codex read spec r3 with plan r3
  ([002-review](../002-review.md)) and re-checked r4 and r5
  ([003-review](../003-review.md), [004-review](../004-review.md)). r6 and
  this r7 carry no review opinion. r7 adds the obligations harvest, the
  verification ledger, five impact findings (help golden, evolve policy,
  index query surface, shared-row freeze, branch registry) and decisions
  D8-D11; tags `(r7)` mark them.
- Component index: `references/project.md` says this repository keeps none
  for the phase protocol; the reuse table below is retained as planning
  evidence (searched with `scripts/components_index.py` after PR 100), not as
  a protocol step.

## 3. Obligations (step 0 harvest)

| Row | Source | Obligation | Discharged in |
|---|---|---|---|
| RC1-C1 | plan §4 | `remedy` accepted by `gnd validate`; non-string, empty, 2001-char refused (exit 3) | M1; T1, T2 |
| RC1-C2 | plan §4 | `--rule-ids` emits v15 with `address`, `addressing`, `remedy`, `novelty: null`, `row_novelty: null` per verdict; derivations validate against `derivation_verdict_v15` incl. `term:mod-zero`; top level `baseline: null`, `allow_vacuous: false`; fact-type and top-level constraints | M2, M4, M5; T3, T4, T4b, T4c, T5 |
| RC1-C3 | plan §4 | without `--rule-ids`, full suite matches the merge-base record; rf1 sem-check goldens byte-identical | §8 V1, V3; T8 |
| RC1-C4 | plan §4 | `--rule-ids` with any other arm exits 64 before model load | M6; T7 |
| RC1-C5 | plan §4 | v15 payload validates; v7 payload with `address` added fails | M2; T6 |
| RC1-C6 | plan §4 | temporal, redaction-policy and reference-population models exit 3 `check:rule-ids-unsupported` before population load | M5; T9 |
| RC1-C7 | plan §4 | text output prints address and remedy; unchanged without the flag | M6; T10 |
| RC1-C8 | plan §4 | census addresses unchanged after the move; `gnd coverage` refuses v15 | M3, M7; T11, T12 |
| RC1-C9 | plan §4 | identity walk over 2,000 constraints in one fact type under 0.5 s, no fact-type deep copy | M3; T13 |
| §9 RC1 row | plan §9 | "`uv run pytest -q tests/test_rc1_*.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py`; full suite vs merge-base record" | §8 V2, V3 |
| §8 merge base | plan §8 | existing-suite command and full suite recorded at the merge base before any source change | §8 V1 |
| O1-O4 | plan §1 | declared id; author fix text; v7 closed; ids unique | M1-M5; T1-T6 |
| O16 | plan §1 | reuse the existing addressing pieces | M3; T11 |
| O18 | plan §1 | version gates in `payloads.py`; coverage intake | M4, M7; T12 |
| O22, O23 | plan §1 | reference wrapper; work-limit band route | M5; T9 |
| O24 | plan §1 | copying walk | M3; T13 |
| O25 | plan §1 | text renderer | M6; T10 |
| O29 | plan §1 | v7 derivation reasons too narrow; v15 must not inherit it | M2; T4c |
| RC-D1 | plan §10 (ruled) | gate after PR 99 merges, else merge-base record | §8 V1 |
| RC-D2 | plan §10 (ruled) | v15 behind `--rule-ids`; v7 frozen | M2, M6; T6, T8 |
| RC-D12 | plan §10 (ruled) | `remedy: null` when undeclared | M4; T4 |
| §5 surfaces | plan §5 | CLI help gains `--rule-ids`; sync-pinned meta-schema copy; coverage keeps its versions | M1, M6, M7; T12, T14 |
| §6 risks | plan §6 | an existing variant moves; redacted/temporal/reference keys; a phase grows | V3; T9; §10 |
| §7 out of scope | plan §7 | v15 for other arms and refused model classes; coverage intake | §9 |
| Residual | plan §4 | none: RC1 has no Residual paragraph | — |
| (r7) impact: help golden | `tests/fixtures/rf1-pins/goldens/cli-help/gnd_check.json`, held by `tests/test_rf1_cli_pins.py` | adding the flag changes pinned help bytes | M6; T14 |
| (r7) impact: evolve policy | `constraint_change` (`src/gnd/evolve/policy.py:194`) admits a `rationale` edit and classes any other unknown path `_NEITHER` | a `remedy` edit would be judged a semantic change | M8; T15 |
| (r7) impact: index query surface | AGENTS.md "RF6 query exceptions are live, counted entries"; `tests/test_rf6_index.py` | a new `ModelIndex` method may be counted | M3; V4 |
| (r7) impact: shared-row freeze | `tests/_tp2_freeze_plugin.py` freezes `iter_fact_types_shared` rows | the new shared iterator needs the same guard | M3; V4 |

## 4. Standing rules bound to this phase

1. **Totality.** New untrusted input: the `remedy` string. It is validated
   by the meta-schema (string, 1-2000 chars) in `gnd validate` before any
   consumer reads it, and reaches JSON output through `json.dumps` and text
   output through the existing printer only. Hostile cases: T2 (wrong type,
   empty, over length), T10 (a remedy with a newline and a non-ASCII
   character prints on one indented line, escaped as the printer escapes
   messages).
2. **Cap bounds the algorithm.** The one new pass is M3's identity walk,
   linear in constraints and copy-free. Time-bound test: T13.
3. **Validation order.** Order: arguments (64, no payload) → model load (3)
   → `check:rule-ids-unsupported` (3) → population load (3) → evaluation.
   Pinned by T7 (64 before an unreadable model path is touched) and T9 (the
   refusal is reported for a model whose population path does not exist).
4. **One walk.** Identity is attached by one post-pass keyed by
   `constraint_ref` over `ModelIndex.iter_constraints_shared()` (M3), not at
   the `ConstraintVerdict(...)` construction sites
   (`tests/test_public_construction_site_guards.py` stays green, V4).
5. **One home.** v15 shape: `src/gnd/report.schema.json`. `remedy` field:
   `src/gnd/schema/orm-meta.schema.json`, sync-pinned copy
   `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json` (one
   artifact, `tests/test_schema_sync.py`). Declared addressing:
   `address.declared_constraint_address` (M3), with `coverage.py` yielding
   its private copy. Prose for `remedy` lands in RC6; nothing here restates it.
6. **Measure.** RC-D2 was settled by the schema (`verdict` is closed); T6 is
   the measurement. O29 was settled by running the fixture (plan O29).
7. **Frozen variants (plan).** Every existing variant keeps its bytes: V3
   (full suite vs merge base) and T8. The help golden (T14) is not a report
   variant; it moves deliberately and is listed.
8. **Stop rule (plan).** Estimates in §10; past 1.5 times either, or on a
   failed time bound, work pauses for the owner gate.

## 5. Goal

`gnd check MODEL POP --rule-ids --format json` exits with the same band as
without the flag and emits `schema_version: 15`, validated by
`report.schema.json`, in which every verdict carries `address`,
`addressing`, `remedy`, `novelty: null`, `row_novelty: null`, derivations
validate against `derivation_verdict_v15`, and the top level carries
`baseline: null` and `allow_vacuous: false`. Without `--rule-ids`, the full
suite result equals the merge-base record and the 28 rf1 sem-check goldens
are byte-identical. `--rule-ids` with another arm or `--compiled-operations`
exits 64 with no payload; with a temporal, redaction-policy or
reference-population model it exits 3 with `check:rule-ids-unsupported`
before the population is read.

## 6. Design

**Reuse table** (searched 2026-11-06 at 8bfbe417).

| Capability | Searches | Found | Decision |
|---|---|---|---|
| one walk over every constraint with its positional ref | `constraint id declared lookup ref`; `git grep positional_constraint_ref` | `ModelIndex.iter_constraints()` (`src/gnd/model_index.py:279`), deep-copies the fact type per constraint; `iter_fact_types_shared()` (line 204), the non-copying internal-reader pattern | **adapt**: `iter_constraints_shared()` beside it |
| constraint → declared address, else positional | same; `report schema closed variant serialize` | `constraint_address(id)`, `Addressing` (`src/gnd/address.py:16,49`); private `coverage._constraint_address` (`src/gnd/coverage.py:735`) | **adapt**: public `declared_constraint_address` absorbs the private one |
| text rendering | `git grep _print_report` | `_print_report(report: CheckReport)` (`src/gnd/output.py:167`), called at `commands/checking.py:276` | **adapt**: optional `declared` argument |
| report-version gates | `git grep "schema_version in"` | `ReportSchemaVersion` (`payloads.py:76`); `schema_version in {7, 8}` branches; `coverage._accepted_schema_versions` (`coverage.py:436`) | **adapt** payloads; coverage **unchanged** |
| refusal with an issue rule id at exit 3 | `git grep "ValidationIssue("` | `ValidationIssue(path, message, rule_id)` (`src/gnd/errors.py:13`); `build(..., issues=...)` in `checking_service.py` (~line 246) | **reuse** |
| model-then-population seam | read `_run_check_raw` | model resolved, then `_resolve_population` (`checking_service.py:217`, ~302) | **reuse**: the refusal sits between them |
| v15 attachment point in the schema | read the schema's top-level `oneOf` | `legacy_reference_report` (versions 3-11) and wrapper branches (12, 14) | **new** top-level branch `rule_ids_report` |
| exit band | `exit band outcome vacuous` | `band()` (`checker/_reports.py`) | **reuse**, unchanged |

**M1. `src/gnd/schema/orm-meta.schema.json` (+ sync-pinned copy), ~5 lines.**
In `$defs.constraint_common.properties`:

```json
"remedy": { "type": "string", "minLength": 1, "maxLength": 2000 }
```

Constraints load as raw dicts (`Model.constraints: list[dict[str, Any]]`,
`src/gnd/documents.py`), so no Python model class changes.

**M2. `src/gnd/report.schema.json`, ~140 lines.** The whole version-15
shape is fixed here; RC3 and RC4 fill values and add no key.

`$defs.verdict_v15`: a closed object built as `verdict_v10` is (line 532),
restating the nine version-7 properties by `$ref` to
`#/$defs/verdict/properties/<key>`, never referencing the closed `verdict`
object as a whole. Added:

```json
"address":     { "type": "string" },
"addressing":  { "enum": ["declared-id", "positional"] },
"remedy":      { "anyOf": [ { "type": "string" }, { "type": "null" } ] },
"novelty":     { "enum": ["new", "standing", null] },
"row_novelty": { "anyOf": [ { "type": "null" },
                 { "type": "array", "items": { "enum": ["new", "standing"] } } ] }
```

All fourteen keys required; `additionalProperties: false`.

`$defs.derivation_verdict_v15`: a closed object restating the seven
`derivation_verdict` properties (line 991) and its four pass/fail/unchecked
conditional rules (lines 1044-1149), with `reason_code` (property and
unchecked rule) admitting every `DerivationReason`
(`src/gnd/extensions.py:55-67`), the set `derivation_verdict_v10` lists. No
novelty field (plan RC-D11).

`$defs.baseline_v15` (defined now, emitted by RC3): `population` (string),
`population_sha256` (`^[0-9a-f]{64}$`), integer counts `new`, `standing`,
`resolved`, `positional_keyed` (rows) and `undecided` (obligations), all
required, closed.

New top-level `oneOf` branch `$defs.rule_ids_report`: a closed object with
the version-7 key set and the version-7 property schemas, except
`schema_version: {"const": 15}`, `command: {"const": "check"}`,
`verdicts.items: verdict_v15`, `derivations` null or
`items: derivation_verdict_v15`, plus required `baseline` (null or
`baseline_v15`) and `allow_vacuous` (boolean). RC1 emits `baseline: null`,
`allow_vacuous: false`. `address` spelling: `constraint:<id>` exactly as
`address.constraint_address` writes it; `addressing` spelled as
`address.Addressing` and `coverage.schema.json` spell it.

**M3. `src/gnd/address.py` ~12 lines; `src/gnd/coverage.py` ~-5;
`src/gnd/model_index.py` ~10.**

```python
# src/gnd/address.py
def declared_constraint_address(
    positional: str, constraint: Mapping[str, Any]
) -> tuple[str, Addressing]:
    """A constraint's address: its declared id, else its positional ref."""

# src/gnd/model_index.py
def iter_constraints_shared(
    self,
) -> Iterator[tuple[str, dict[str, Any], dict[str, Any] | None]]:
    """Internal readers only: same refs and order as iter_constraints(), not copied."""
```

`coverage._constraint_address` becomes a call to
`declared_constraint_address` (rule 5). The identity map
`declared: dict[str, tuple[str, Addressing, str | None]]` (positional ref →
address, addressing, remedy) is built once per run from
`ModelIndex.for_model(model).iter_constraints_shared()`, reading only `id`
and `remedy`. `iter_constraints()` is unchanged. If `tests/test_rf6_index.py`
counts `ModelIndex` query methods, the new method is registered there (V4).
(r7) The TP2 freeze plugin (`tests/_tp2_freeze_plugin.py`) serves every
`iter_fact_types_shared` row frozen so a write raises; it wraps
`iter_constraints_shared` the same way, and
`tests/test_tp2_shared_fact_types.py` runs in V4, so the must-not-mutate
contract has a case that fails.

**M4. `src/gnd/payloads.py`, ~35 lines.** `ReportSchemaVersion` gains `15`.
`build_check_payload(..., declared: Mapping[str, tuple[str, Addressing,
str | None]] | None = None)`. When `schema_version == 15`, each verdict gets
`address`, `addressing`, `remedy` after `constraint_ref`, then
`novelty: null`, `row_novelty: null`; derivations serialize as in version 7;
the top level gets `baseline: null`, `allow_vacuous: false`.
`schema_version == 15` with `declared is None` raises `ValueError`. Each
`schema_version in {7, 8}` branch is read; where v15 extends v7 it becomes
`{7, 8, 15}`; the record lists each.

**M5. `src/gnd/checking_service.py`, ~30 lines.** A `rule_ids: bool = False`
keyword on the snapshot path: `_run_check_raw`, `_run_check`, and the
exported `run_check` that `src/gnd/api.py` imports as `_run_check` and the
CLI calls (`commands/checking.py:248`). After the model resolves and before
`_resolve_population`, if `rule_ids` and
(`current_payload_schema_version(model) != 7` or
`model.reference_populations`), return exit 3 with
`issues=[ValidationIssue(path="model", rule_id="check:rule-ids-unsupported",
message=...)]` (D8 fixes the payload's version). Otherwise the snapshot path
selects 15 and passes `declared`.

**M6. `src/gnd/commands/checking.py` ~25 lines; `src/gnd/output.py` ~15.**
`--rule-ids` (`store_true`; help: "report version 15: each verdict carries
the constraint's declared id and remedy"). `parser.error` (64) when combined
with `--populations`, `--pre`, `--steps`, `--post`, `--anchors`,
`--document`, `--composition`, `--sources`, `--admission` or
`--compiled-operations` (r7: the last was missing; it selects
`check_partial` and a different assurance path). `--unredacted` is accepted
and has no effect, because redaction-policy models are refused (D9).
`_print_report(report, declared=None)`: with the map, a verdict line reads
`[fail] constraint:no_import_loops (fact_types[component_uses_component].constraints[0]): <message>`
and, when `remedy` is set, a next line `  remedy: <remedy>`; without it,
output is unchanged (T10).

**M7. `src/gnd/coverage.py`: no intake change.** `gnd coverage` refuses a
version-15 report with its existing version message (T12).

**M8 (r7). `src/gnd/evolve/policy.py`, ~2 lines.** `constraint_change`
returns `_ADMITTED` for `path == "remedy"`, as for `rationale`: author text
with no semantic effect (D10).

**M9 (r7). Branch registry, `src/gnd/branches.py`.** Register
`report:check:n-a:rule-ids` (projection) and the refusal event so
`tests/test_public_branch_runtime.py` and `tests/test_v6_phase2_registry.py`
stay complete (V4).

**M9 amended (r8, corpus finding C1).** No new branch row. A version-7
report's `assurance.uncovered_applicable_scope_ids` lists the applicable
`report:check:n-a:*` projection rows (probe 2026-11-06: 10 `report:` ids
among 65), so a new row in that family would enter every version-7
report's assurance block and move frozen bytes (plan rule 7). The
version-15 projection records only the existing `report:check:n-a:*`
events, and the refusal records no new event. The corpus pins this: its
version-15 goldens carry the version-7 assurance block unchanged.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Field name: `remedy` or `message`? | `message` collides with the verdict's own `message` key | `remedy` **(o) 2026-11-06: approved with the corpus** |
| D2 | Flag name | `--rule-ids` vs `--report-version 15` (a general selector; widens every arm's contract) | `--rule-ids` **(o) 2026-11-06: approved with the corpus** |
| D3 | Redaction (v9), temporal (v11), reference-population (v12) models | refuse (exit 3) vs build successors now (doubles the phase) | refuse; plan §7 **(o) 2026-11-06: approved with the corpus** |
| D4 | `remedy` in `gnd verbalize`? | yes moves verbalization goldens | no in RC1; RC6 decides **(o) 2026-11-06: approved with the corpus** |
| D5 | Does `remedy` change the model digest? | it is model content | yes; T8 shows remedy-free models unchanged **(o) 2026-11-06: approved with the corpus** |
| D6 | Bare `constraint_id` or `address` + `addressing`? | bare id needs a rule for id-less constraints | `address` + `addressing` **(o) 2026-11-06: approved with the corpus** |
| D7 | Undeclared `remedy` | plan RC-D12 (ruled) | null (T4) **(o) 2026-11-06: approved with the corpus** |
| D8 (r7) | Which `schema_version` does the exit-3 refusal payload carry? | 15 (but the model is one v15 cannot describe) vs the version the model selects without the flag (9, 11, or the reference wrapper's 12) | the model's own version, so the payload validates against an existing branch; T9 validates it. **(o) 2026-11-06: approved as proposed** |
| D9 (r7) | `--rule-ids` with `--unredacted` | refuse (64) vs accept as a no-op | accept: redaction models are refused anyway, and a 64 adds a branch with no behaviour. **(o) 2026-11-06: approved as proposed** |
| D10 (r7) | A `remedy` edit under `gnd evolve` | admitted like `rationale` vs `_NEITHER` (today's default for an unknown path, which demands review) | admitted. **(o) 2026-11-06: approved as proposed** |
| D11 (r7) | Approval instrument (§11) | prose vs corpus-first | corpus-first, the default for a serialized format and an exit-code contract. **(o) 2026-11-06: corpus-first** |

## 8. Tests and verification ledger

**Direct tests** (`tests/test_rc1_rule_ids.py` unless noted).

| T | Case | Expected |
|---|---|---|
| T1 | model with `remedy` on a fact-type constraint and a top-level constraint | `gnd validate` exit 0 |
| T2 | `remedy: 7`, `remedy: ""`, 2001-char remedy | exit 3, `jsonschema:*` issue |
| T3 | `--rule-ids --format json`, failing ring rule `id: no_import_loops` with remedy | exit 1, v15, `address == "constraint:no_import_loops"`, `addressing == "declared-id"`, remedy copied |
| T4 | constraint without id or remedy, with a `rationale` | `address == constraint_ref`, `addressing == "positional"`, `remedy` null, novelty fields null, `baseline: null`, `allow_vacuous: false` |
| T4b | structured model with a derivation | accepted; each derivation byte-identical to its v7 serialization; negative schema cases: pass with a finding, fail with none, unchecked with null reason each fail |
| T4c | committed copy of `tests/fixtures/v62-phase3/models/exact-terms.orm.yaml` without `redact: true`, `term-input` population | exit 4; v15 with `term:mod-zero` derivations validates |
| T5 | ids on fact-type and top-level constraints | each verdict's address matches its own constraint |
| T6 | schema: v15 payloads validate; v7 + `address` fails; v15 verdict missing `row_novelty` or with an extra key fails | as stated |
| T7 | `--rule-ids` with each of the ten conflicting flags, model path unreadable | exit 64, empty stdout, no model read |
| T8 | without the flag: `tests/test_rf1_semantic_pins.py` green; a remedy-free model's digest unchanged | pass |
| T9 | redaction, temporal and reference-population models, population path nonexistent | exit 3, issue `check:rule-ids-unsupported`, payload validates at the model's own version (D8) |
| T10 | text: address and remedy lines printed; a remedy with a newline and non-ASCII prints escaped on one line; without the flag, byte-identical to the merge base | substring checks; byte comparison |
| T11 | census addresses unchanged (`tests/test_coverage_payload.py`, `tests/test_address.py`) | pass |
| T12 | `gnd coverage` given a v15 report | refused with its existing version message |
| T13 | 2,000 constraints in one fact type | identity walk under 0.5 s; `deepcopy` patched to raise in `gnd.model_index` is never called; refs equal `iter_constraints()`'s |
| T14 (r7) | `tests/test_rf1_cli_pins.py` with `gnd_check.json` regenerated to include `--rule-ids` | pass; the diff of the golden is the one added option |
| T15 (r7) | `constraint_change("remedy", "a", "b")` (in `tests/test_evolve_additive_policy.py`) | `_ADMITTED` |

Branch walk: flag on/off (T3, T8); id present/absent (T3, T4); remedy
present/absent (T3, T4); fact-type vs top-level (T5); derivation plain vs
exact reason (T4b, T4c); each refusal (T7, T9, T12); text with/without map
(T10); evolve remedy edit (T15). Every branch above has a case that fails
if the branch is wrong.

**Verification-selection ledger.**

| # | Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|---|
| V1 | plan §8 merge-base record (RC-D1) | run, before any source edit | `uv run pytest -q tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py --tb=short` and `uv run pytest -q --tb=short` at 8bfbe417 (or main after PR 99 if merged first); output recorded verbatim; expected: whatever main gives (24 known reds if PR 99 is unmerged) | tracked tree at the base | known reds are told apart from regressions | a new base |
| V2 | plan §9 RC1 focused gate | run | `uv run pytest -q tests/test_rc1_rule_ids.py tests/test_schema_sync.py tests/test_checker_families.py tests/test_rf1_semantic_pins.py tests/test_address.py tests/test_coverage_payload.py tests/test_report_json.py --tb=short`; exit 0, or only V1's known reds | M1-M9 sources, schemas, fixtures | the criteria's direct cases plus the named consumers | any edit to those paths |
| V3 | plan rule 7 full suite vs merge base | run (selected by the approved plan) | `uv run pytest -q --tb=short`; the failure set equals V1's or is a subset | whole default lane | the only gate over every pinned variant 3-14 | any source edit after the run |
| V4 | impact closure | run | `uv run pytest -q tests/test_rf1_cli_pins.py tests/test_evolve_additive_policy.py tests/test_rf6_index.py tests/test_public_construction_site_guards.py tests/test_public_branch_runtime.py tests/test_v6_phase2_registry.py tests/test_packaged_skills.py tests/test_v6_phase6_report.py tests/test_tp2_shared_fact_types.py --tb=short`; exit 0 | help golden, evolve policy, index, TP2 freeze plugin, branch registry, packaged skill copy | consumers of the changed surfaces found in §3 (r7) | an edit to those surfaces |
| V5 | lint | run | `uv run ruff check src tests`; exit 0 | changed Python files | project rule: lint is in the record's gate output | any Python edit |
| V6 | broad lanes `-m "evidence or census"` | cadence: not run in RC1 | owner selection at milestone close, if any | historical bytes, tracked-tree census | RC1 changes no historical artifact; V3 covers current behaviour | owner request |

## 9. Out of scope for this phase

Acyclic extent (RC2), baseline values (RC3), vacuous acceptance (RC4),
population source (RC5), prose documentation (RC6); version 15 for batch,
transition, anchors, composition, admission, compiled-operations,
redaction-policy, temporal and reference-population checks; `gnd coverage`
intake of v15; the version-7 derivation-reason defect (O29, fixed on its own
branch); `remedy` in verbalization (D4).

## 10. Size

Estimate: about 240 source lines and 520 test lines, plus the corpus (§11)
of about 12 small files. Past 1.5 times either figure, work pauses for the
owner gate (plan rule 8). Measured at record time.

## 11. Approval instrument

Proposed (D11): **corpus-first.** RC1's deliverable is a serialized format
(report version 15) and an exit-code contract, the two shapes for which the
project's convergence reference makes a corpus the default. Before code, a
corpus lands RED at `tests/fixtures/rc1-rule-ids/`:

- `README.md`: the entry point, one story per case in plain words (input,
  command, what the reader should expect), with no answers in it;
- `models/`, `populations/`: the case inputs (T3, T4, T4b, T4c, T9 inputs);
- `expected/`: the answer key, split out from the README: one
  `<case>.json` golden per JSON case and `<case>.txt` per text case, each
  with its expected exit in `expected/exits.json`;
- cases: `declared-fail` (exit 1), `positional-pass` (exit 0),
  `derivation-plain` (exit per fixture), `derivation-mod-zero` (exit 4),
  `refuse-temporal`, `refuse-redaction`, `refuse-reference` (exit 3),
  `conflict-populations` (exit 64, empty), `text-declared-fail` (exit 1).

The owner approves by reading the README stories and the goldens; the
harness in `tests/test_rc1_rule_ids.py` runs every case and is red until M1-M9
land. If the owner chooses prose instead, this section becomes "this prose"
and the goldens are written during implementation.

## Corpus findings (r8, recorded while authoring the corpus)

- **C1.** The branch registry feeds the version-7 assurance block; M9
  amended above.
- **C2.** The CLI writes JSON with `ensure_ascii=True` (checked by
  re-encoding four of today's reports byte for byte); the goldens use the
  same encoding.
- **C3.** Today's refusal-path versions for the three refused model kinds,
  with a missing population: redaction 9, temporal 11, reference wrapper 12
  around an inner version-7 report (probe 2026-11-06). D8 keeps these.
- **C4.** The model digest of a model with `remedy` was computed with
  `gnd.values.model_digest` over the loaded model with the `remedy` keys
  restored in source order; the method reproduced a known digest first.
- **C5.** For a positional verdict under `--rule-ids`, the text line is
  unchanged (address equals the ref, so it is not printed twice). The
  corpus's text case has declared ids only; the positional text line is a
  direct test (T10).

- **C6.** The usage-error case already exits 64 today, because
  `--rule-ids` is an unknown flag. The harness also requires the error to
  name `--rule-ids` and not be "unrecognized arguments", so it fails until
  the deliberate conflict check exists.
- **C7.** Corpus RED run, 2026-11-06, before any source change:
  `uv run pytest -q tests/test_rc1_rule_ids.py --tb=no` → 9 failed, 1
  passed (the passing test checks only that the corpus lists every case
  once and that `populations/absent.pop.yaml` does not exist).

## Implementability sweep (step 1, author inspection)

Each requirement was asked "can some implementation satisfy this as
written?" against the code at 8bfbe417:

- **Refusal seam exists**: `_run_check_raw` resolves the model before the
  population, and `ValidationIssue` with a free `rule_id` plus
  `build(..., issues=...)` already carry exit-3 refusals. Satisfiable.
- **Schema attachment**: the top-level `oneOf` takes a new closed branch;
  `verdict_v10` shows the restate-by-`$ref` pattern works under the
  repository's validator. Satisfiable.
- **v15 derivations**: `derivation_verdict_v10.reason_code` already lists
  the full reason set; restating it with the v7 conditional rules is
  mechanical. T4c is reachable with a committed copy of an existing fixture
  (probe run 2026-11-06, plan O29). Satisfiable.
- **Conflicting flags**: all ten exist on `check_parser`
  (`commands/checking.py:683-720`); `parser.error` yields 64 before dispatch.
  r7 found `--compiled-operations` missing from the r6 list; added.
- **Help golden**: `gnd_check.json` must change; T14 makes that a
  deliberate, reviewed byte change rather than a red. Satisfiable.
- **T13's no-copy assertion**: patching `gnd.model_index.deepcopy` is
  observable because the module calls `deepcopy` by its imported name
  (`iter_constraints`, line 279-285). Satisfiable.
- **T9's version (D8)**: an exit-3 payload at version 9 or 11 validates
  today for other exit-3 causes; for the reference wrapper (12) the refusal
  must be built before `_reference_wrap` runs or pass through it; the record
  states which, and T9 validates the result. Satisfiable, with that
  implementation choice left to the code.
- **No requirement mandates contradictory content**: v7 bytes stay frozen
  while v15 is additive; the only pinned bytes that move are the help
  golden (T14), declared above.

## Implementation findings (step 3, recorded as found)

- **I1 (2026-11-06), full suite V3 vs V1.** Same 6-shard layout on beast-3
  for both. Base 8bfbe417: 148 failing ids (143 failed + 5 errors). Final
  dc592a89: 153. No base failure disappeared; five are new, all structural
  guards, none behavioural:
  - `test_rf4_peripheral.py::test_moved_algorithm_preserves_base_body[gnd.report:_base_payload]`
    and `[gnd.report:build_check_payload]`: RF4 pins these bodies; RC1
    changed them (M4) with no successor row.
  - `test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_print_report]`:
    RF5 pins `_print_report`; RC1 changed it (M6).
  - `test_rf6_query_policy.py::test_dynamic_candidate_inventory_is_complete_and_live`
    and `test_dynamic_duplicate_inventory_row_is_refused`: the RF6 dynamic
    read inventory counts every subscription site, including annotations;
    RC1 added about 22.
  The repair is registry rows (`compiled-snapshot-obligations/evidence/CI/source-successors.json`
  for the bodies; the RF6 dynamic inventory for the reads). PR 99, open,
  edits that same registry and adds a dynamic-query successor file, and its
  base already fails neighbouring rows (`_run_check_raw`, `_cmd_check`), so
  the rows RC1 adds depend on PR 99's shape. Not a refuted premise of the
  spec: the spec's V4 impact closure did not name these guard suites; that
  omission is the finding.
