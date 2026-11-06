# Phase RC1: declared identity, report version 15

## 1. Status

**Draft r4, 2026-11-06 (r2: component-index reuse, D6; r3: follows plan r3,
the whole version-15 shape, refusal by model property; r4: follows plan r4,
Codex findings R1, R2, R3, R4, R6, R8, R10). Blocked on the plan gate** (the plan is unapproved) and on RC-D1 (PR 99). Not approved; no code
written.

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r4, §2.1,
  §4 RC1, §10 RC-D1/RC-D2/RC-D12.
- Request: GR-D1, GitHub issue 92.
- Inspection baseline: main `33d1db49`; reuse table re-read after merging
  `origin/main` 8bfbe417 (PR 100, the component index) on 2026-11-06.
- The panel over plan r2 shaped r3 (fixes F2, F12, F14, F17-F20 land here).
  One reviewer (Codex) read spec r3 with plan r3
  ([record](../002-review.md)); r4 carries no review opinion.

## 3. Obligations

| Row | Source | Discharged in |
|---|---|---|
| O1 declared id in verdict | plan §1, issue 92 | §6 M3, M4; tests T3, T4 |
| O16 reuse addressing | plan §1 | §6 reuse table, M3; T11 |
| O18 version gates | plan §1 | §6 M4, M7; T12 |
| O22 reference wrapper | plan §1 | §6 M5; T9 |
| O24 copying walk | plan §1 | §6 M3; T13 |
| O25 text renderer | plan §1 | §6 M6; T10 |
| O2 author fix text | plan §1, issue 92 | §6 M1; T1, T2, T4 |
| O3 v7 closed shape | `report.schema.json` `$defs.verdict` | §6 M2 (new version); T6 |
| O4 ids unique | `semantic:id-unique` | relied on; T5 |
| RC1-C1 … C9 | plan §4 | T1-T13 |
| Plan rule 4 (one walk) | plan §0 | §6 M3 |
| Plan rule 7 (frozen variants) | plan §0 | T6 |

## 4. Standing rules bound to this phase

1. **Totality.** `remedy` is untrusted model text. It is validated by the
   meta-schema (string, `maxLength` 2000) before any consumer sees it, and
   reaches output through `json.dumps` only. Hostile case: T2.
2. **Cap bounds the algorithm.** M3 is one pass over the model's constraints
   that copies nothing (linear; T13). Inapplicable beyond that; no new untrusted-proportional loop.
3. **Validation order.** `--rule-ids` conflicts are argument errors, decided
   before the model loads: exit 64, no payload, like the existing arm
   conflicts. The model refusal (M5) follows model load and precedes
   population load. Pinned by T7 and T9.
4. **One walk.** Identity is attached in one post-pass keyed by
   `constraint_ref` over `ModelIndex.iter_constraints_shared()` (M3), not at the seven `ConstraintVerdict(...)` sites in
   `checker/_core.py`, `checker/_reports.py`, `compiled_obligations.py` and
   `measure/promote.py`.
5. **One home.** Version-15 shape: `src/gnd/report.schema.json`. `remedy`:
   `src/gnd/schema/orm-meta.schema.json`, with its sync-pinned copy under
   `src/gnd/skills/gnd-orm-core/references/` held by `tests/test_schema_sync.py`.
   Prose for `remedy` lands in RC6 (constraint reference); this spec cites it.
6. **Measure.** RC-D2 (new version vs widen v7) is settled by the schema
   itself: `$defs.verdict` has `additionalProperties: false`, so a v7 payload
   with a new key fails the shipped contract. T6 is the measurement.

## 5. Goal

`gnd check MODEL POP --rule-ids --format json` exits with the same band as
without the flag, emits `schema_version: 15`, and every verdict carries
`address`, `addressing`, `remedy`, `novelty: null` and `row_novelty: null`,
every derivation carries `novelty: null` and `finding_novelty: null`, and
the top level carries `baseline: null` and `allow_vacuous: false`. Without `--rule-ids`,
the full suite matches the merge-base record and the 28 rf1 sem-check
goldens are byte-identical. `--rule-ids` with any other arm exits 64; with a
model whose plain report is not an unwrapped version 7 (temporal terms: 11;
active redaction policy: 9; reference populations: wrapped as 12) it exits
3 (D3).

## 6. Design

**Reuse table** (component index at merge `origin/main` 8bfbe417; index
review over `checker`, `check`, `model.address` reports 0 descriptions older
than their code).

| Capability | Searches | Found | Decision |
|---|---|---|---|
| one walk over every constraint with its positional ref | `constraint id declared lookup ref`; `git grep positional_constraint_ref` | `model.query_index`: `ModelIndex.iter_constraints()` (`src/gnd/model_index.py:279`), which deep-copies the fact type per constraint (quadratic); `iter_fact_types_shared()` (line 204), the non-copying internal-reader pattern | **adapt**: add `iter_constraints_shared()` beside `iter_fact_types_shared()`, same enumeration and refs, no copies, same must-not-mutate contract |
| text rendering of verdicts | `git grep _print_report` | `_print_report(report: CheckReport)` (`src/gnd/output.py:167`), called from `commands/checking.py:276` | **adapt**: optional identity map argument (M6) |
| constraint → declared address, else positional, with a kind | same; `report schema closed variant serialize` | `model.address`: `constraint_address(id)` (no fallback), `Addressing = Literal["declared-id", "positional"]` (`src/gnd/address.py:16,49`); `check.element_coverage`: private `_constraint_address` (`src/gnd/coverage.py:735`, "the one home of constraint addressing for the census") | **adapt**: a new public `declared_constraint_address` in `address.py` absorbs `_constraint_address` and calls `constraint_address`; `coverage.py` calls it |
| report-version gates | `git grep "schema_version in"` | `ReportSchemaVersion` (`src/gnd/payloads.py:76`); `schema_version in {7, 8}` branches in `payloads.py`; `coverage._accepted_schema_versions` (`src/gnd/coverage.py:436`) | **adapt** payloads (M4); coverage **unchanged**, refuses v15 (T12) |
| v15 payload assembly | `constraint verdict report payload version` | `src/gnd/payloads.py` `build_check_payload` | **adapt** |
| exit band | `exit band outcome vacuous` | `checker.reports` `band()` | **reuse**, unchanged |

**M1. `src/gnd/schema/orm-meta.schema.json` (+ skill copy), ~5 lines.**
In `$defs.constraint_common.properties`:

```json
"remedy": { "type": "string", "minLength": 1, "maxLength": 2000 }
```

**M2. `src/gnd/report.schema.json`, ~140 lines.** The whole version-15 shape
is fixed here; RC3 and RC4 fill values and add no key (plan §2.1).

New `$defs.verdict_v15`: a separate closed object, built as `verdict_v10`
is (line 532): it restates the nine version-7 property schemas, each by
`$ref` to the same `#/$defs/verdict/properties/<key>` where that works
under the validator in use, else copied, and never references the closed
`#/$defs/verdict` object as a whole (an `allOf` over it would reject every
new key, R1). Added properties:

```json
"address":     { "type": "string" },
"addressing":  { "enum": ["declared-id", "positional"] },
"remedy":      { "anyOf": [ { "type": "string" }, { "type": "null" } ] },
"novelty":     { "enum": ["new", "standing", null] },
"row_novelty": { "anyOf": [ { "type": "null" },
                 { "type": "array", "items": { "enum": ["new", "standing"] } } ] }
```

All fourteen keys required, `additionalProperties: false`. New
`$defs.derivation_verdict_v15`, built the same way from
`derivation_verdict` (line 991), adds `novelty` (as above) and
`finding_novelty` (null or an array aligned with `findings`); its
`derivation_ref` is already the derivation's stable address. RC1 always
emits null for every novelty field.
`address` is `constraint:<id>` when the constraint declares an id, else its
positional ref; `addressing` says which, spelled as `coverage.schema.json`
and `address.Addressing` already spell it (D6).
New top-level `oneOf` branch `rule_ids_report`: the version-7 key set with
`schema_version: {"const": 15}`, `verdicts.items: verdict_v15`,
`derivations.items: derivation_verdict_v15`, and two more
required keys: `baseline` (`null`, or the RC3 block `$defs.baseline_v15`
defined now: `population`, `population_sha256`, and integer counts `new`,
`standing`, `resolved`, `positional_keyed`, `undecided`) and
`allow_vacuous` (boolean). RC1 always emits `baseline: null` and
`allow_vacuous: false`.
`ReportSchemaVersion` in `src/gnd/payloads.py` gains `15`.

**M3. `src/gnd/address.py`, ~10 lines moved; `src/gnd/coverage.py`, ~5.**

```python
def declared_constraint_address(
    positional: str, constraint: Mapping[str, Any]
) -> tuple[str, Addressing]:
    """A constraint's address: its declared id, else its positional ref."""
```

Moved from `coverage._constraint_address`, which becomes a call to it, so
the census and the report share one home of constraint addressing (rule 5).
No new module; no layer-map change (`address.py` already imports nothing).
The identity map is built in the payload path from
`ModelIndex.for_model(model).iter_constraints_shared()`, a new non-copying
sibling of `iter_constraints()` in `src/gnd/model_index.py` (~10 lines)
yielding the same positional refs over the index's own rows, under the
must-not-mutate contract `iter_fact_types_shared()` already states. The
identity walk only reads `id` and `remedy`. `iter_constraints()` is
unchanged (rule 4; T13).

**M4. `src/gnd/payloads.py`, ~30 lines.** `build_check_payload(...,
declared: Mapping[str, tuple[str, Addressing, str | None]] | None = None)`. When
`schema_version == 15`, each serialized verdict gets `address`,
`addressing` and `remedy` from `declared`, inserted after `constraint_ref`,
then `novelty: null` and `row_novelty: null`; each derivation gets
`novelty: null` and `finding_novelty: null`.
`schema_version == 15` with `declared is None` raises `ValueError` (a
programming error, not a user path). Each `schema_version in {7, 8}` branch
in `payloads.py` is read: where version 15 extends version 7 it becomes
`{7, 8, 15}`; each change is listed in the record.

**M5. `src/gnd/checking_service.py`, ~25 lines.** The plain snapshot path
selects 15 instead of 7 when `rule_ids` is set and passes the map built
from `iter_constraints_shared()` and `declared_constraint_address`.
Refusal (D3): after model load and before population load, a model for
which `current_payload_schema_version(model)` (`src/gnd/payloads.py:735`)
is not 7 (temporal terms select 11, an active redaction policy selects 9),
or which has `reference_populations` (its report would be wrapped as
version 12 by `_reference_wrap`, `checking_service.py:594`, whose `report`
admits no version 15), is refused with issue rule id
`check:rule-ids-unsupported`, exit 3. This also keeps
`reference-join-work-limit` (`checker/_core.py:2379`) out of version 15.

**M6. `src/gnd/commands/checking.py`, ~25 lines.** `--rule-ids`
(`store_true`, help: "report version 15: each verdict carries the
constraint's declared id and remedy"). Mutual exclusion with `--populations`,
`--pre/--steps/--post`, `--anchors`, `--document`, `--composition`,
`--sources`, `--admission` via `parser.error` (64). Text output: the text
path renders the internal `CheckReport` through `_print_report`
(`src/gnd/output.py:167`), not the payload (R10), so `_print_report` gains
an optional `declared` map (~15 lines in `output.py`), passed from
`commands/checking.py` only under the flag. With it, a verdict prints
`[fail] constraint:no_import_loops (fact_types[…].constraints[0]): …` and,
when present, an indented `remedy:` line; without it, output is unchanged.

**M7. `src/gnd/coverage.py`: no change.** `gnd coverage` keeps its accepted
versions and refuses a version-15 report with its existing message (T12;
plan §7).

Branch registry (`src/gnd/branches.py`): register
`report:check:n-a:rule-ids` for the v15 projection so branch coverage stays
complete.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Field name: `remedy` or `message`? | `message` collides with the verdict's own `message` key | `remedy` |
| D2 | Flag name | `--rule-ids` vs `--report-version 15` (a general selector nobody has yet; widens every arm's contract) | `--rule-ids` |
| D3 | Redaction (v9) and temporal (v11) models with `--rule-ids` | refuse (exit 3, after model load) vs build v9/v11 successors now (doubles the phase) | refuse; plan §7 lists successors as out of scope |
| D4 | Should `remedy` appear in `gnd verbalize`? | yes adds a verbalization golden change | no in RC1; RC6 decides |
| D6 | Bare `constraint_id` (as the request words it) or `address` + `addressing`? | bare id needs a second rule for constraints without one; `address` reuses the census's existing scheme and gives RC3 its key with no extra rule | `address` + `addressing` |
| D5 | Does `remedy` change the model digest? | it is model content, so yes for models that use it; models without it are unaffected | yes; T8 shows the unaffected case |
| D7 | Undeclared `remedy`: null or `rationale`? | plan RC-D12 | null (T4) |

## 8. Tests (`tests/test_rc1_rule_ids.py` unless noted)

| T | Case | Expected |
|---|---|---|
| T1 | model with `remedy` on a fact-type and a top-level constraint validates | exit 0 |
| T2 | `remedy: 7`, `remedy: ""`, 2001-char remedy | exit 3, `jsonschema:*` issue |
| T3 | `--rule-ids --format json` on a failing ring rule with id | exit 1, v15, `address == "constraint:no_import_loops"`, `addressing == "declared-id"` |
| T4 | constraint without id / without remedy (with a `rationale`) | `address` equals `constraint_ref`, `addressing == "positional"`; `remedy` null; `novelty` and `row_novelty` null; top level `baseline: null`, `allow_vacuous: false` |
| T4b | structured model with a derivation, `--rule-ids` | each derivation has `novelty: null`, `finding_novelty: null`; payload validates |
| T5 | ids for fact-type constraints and top-level constraints both resolve | correct ids |
| T6 | v15 payloads validate; a v7 payload with `address` added fails validation; a v15 verdict missing `row_novelty` or with an extra key fails | as stated |
| T7 | `--rule-ids` with each conflicting flag | exit 64, no payload; parser order before model load |
| T8 | without the flag: `tests/test_rf1_semantic_pins.py` unchanged; model digest of a remedy-free model unchanged; full suite matches the merge-base record | pass |
| T9 | redaction-policy model, temporal model and reference-population model with `--rule-ids` | exit 3, `check:rule-ids-unsupported`; an unreadable population path is not reported (refusal precedes population load) |
| T10 | text output under the flag prints address and remedy; without the flag, text output is byte-identical to the merge base | substring checks and a byte comparison on real output |
| T11 | `gnd coverage` census addresses unchanged after the move (`tests/test_coverage_payload.py`, `tests/test_address.py`) | pass |
| T12 | `gnd coverage` given a version-15 check report | refused with its existing version message |
| T13 | model with 2,000 constraints in one fact type | identity walk under 0.5 s; `deepcopy` patched to raise is never called; refs equal `iter_constraints()`'s |

Branch walk: flag on/off (T3/T8), id present/absent (T3/T4), remedy
present/absent (T3/T4), fact-type vs top-level (T5), each refusal (T7, T9,
T12).

Before any RC1 source change, the existing-suite command of plan §8
(without `tests/test_rc1_*.py`, which does not exist yet) and the full suite
run at the merge base and are recorded verbatim (plan §8, RC-D1, R6). The
full focused gate runs after this phase adds `tests/test_rc1_rule_ids.py`.

## 9. Out of scope for this phase

Acyclic extent (RC2), baseline (RC3), vacuous (RC4), source (RC5), prose
documentation (RC6), v15 for any arm other than plain snapshot.

## 10. Size

About 230 source lines, 480 test lines (estimate). Past 1.5 times either,
work pauses for the owner gate (plan rule 8).

## 11. Approval instrument

This prose.
