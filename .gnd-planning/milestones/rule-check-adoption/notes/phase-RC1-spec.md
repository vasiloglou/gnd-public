# Phase RC1: declared identity, report version 15

## 1. Status

**Draft r2, 2026-11-06 (r2: component-index reuse, D6). Blocked on the plan gate** (the plan is unapproved)
and on RC-D1 (PR 99). Not approved; no code written.

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r1, §2.1,
  §4 RC1, §10 RC-D1/RC-D2.
- Request: GR-D1, GitHub issue 92.
- Inspection baseline: main `33d1db49`; reuse table re-read after merging
  `origin/main` 8bfbe417 (PR 100, the component index) on 2026-11-06.
- No review has run over this spec.

## 3. Obligations

| Row | Source | Discharged in |
|---|---|---|
| O1 declared id in verdict | plan §1, issue 92 | §6 M3, M4; tests T3, T4 |
| O16 reuse addressing | plan §1 | §6 reuse table, M3; T11 |
| O2 author fix text | plan §1, issue 92 | §6 M1; T1, T2, T4 |
| O3 v7 closed shape | `report.schema.json` `$defs.verdict` | §6 M2 (new version); T6 |
| O4 ids unique | `semantic:id-unique` | relied on; T5 |
| RC1-C1 … C5 | plan §4 | T1-T8 |
| Plan rule 4 (one walk) | plan §0 | §6 M3 |
| Plan rule 7 (frozen variants) | plan §0 | T6 |

## 4. Standing rules bound to this phase

1. **Totality.** `remedy` is untrusted model text. It is validated by the
   meta-schema (string, `maxLength` 2000) before any consumer sees it, and
   reaches output through `json.dumps` only. Hostile case: T2.
2. **Cap bounds the algorithm.** M3 is one pass over the model's constraints
   (linear). Inapplicable beyond that; no new untrusted-proportional loop.
3. **Validation order.** `--rule-ids` conflicts are argument errors, decided
   before the model loads: exit 64, no payload, like the existing arm
   conflicts. Pinned by T7.
4. **One walk.** Identity is attached in one post-pass keyed by
   `constraint_ref` over `ModelIndex.iter_constraints()` (M3), not at the seven `ConstraintVerdict(...)` sites in
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
`address`, `addressing` and `remedy`. Without `--rule-ids`, every existing output
is byte-identical (the 28 rf1 sem-check goldens pass unchanged).
`--rule-ids` with any other arm, a redaction policy or a temporal model
exits 64 (or 3 for model-dependent refusals, D3).

## 6. Design

**Reuse table** (component index at merge `origin/main` 8bfbe417; index
review over `checker`, `check`, `model.address` reports 0 descriptions older
than their code).

| Capability | Searches | Found | Decision |
|---|---|---|---|
| one walk over every constraint with its positional ref | `constraint id declared lookup ref`; `git grep positional_constraint_ref` | `model.query_index`: `ModelIndex.iter_constraints()` (`src/gnd/model_index.py:279`) | **reuse** |
| constraint → declared address, else positional, with a kind | same; `report schema closed variant serialize` | `model.address`: `constraint_address`, `Addressing = Literal["declared-id", "positional"]` (`src/gnd/address.py:16,49`); `check.element_coverage`: `_constraint_address` (`src/gnd/coverage.py:735`, "the one home of constraint addressing for the census") | **adapt**: move `_constraint_address` to `address.py` as public `declared_constraint_address`; `coverage.py` calls it |
| v15 payload assembly | `constraint verdict report payload version` | `src/gnd/payloads.py` `build_check_payload` | **adapt** |
| exit band | `exit band outcome vacuous` | `checker.reports` `band()` | **reuse**, unchanged |

**M1. `src/gnd/schema/orm-meta.schema.json` (+ skill copy), ~5 lines.**
In `$defs.constraint_common.properties`:

```json
"remedy": { "type": "string", "minLength": 1, "maxLength": 2000 }
```

**M2. `src/gnd/report.schema.json`, ~60 lines.** New `$defs.verdict_v15`:
`allOf` of `#/$defs/verdict` properties plus

```json
"address":    { "type": "string" },
"addressing": { "enum": ["declared-id", "positional"] },
"remedy":     { "anyOf": [ { "type": "string" }, { "type": "null" } ] }
```

all required, `additionalProperties: false` restated over the twelve keys.
`address` is `constraint:<id>` when the constraint declares an id, else its
positional ref; `addressing` says which, spelled as `coverage.schema.json`
and `address.Addressing` already spell it (D6).
New top-level `oneOf` branch `rule_ids_report`: the version-7 key set with
`schema_version: {"const": 15}` and `verdicts.items: verdict_v15`.
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
`ModelIndex.for_model(model).iter_constraints()`, the existing single
enumeration (rule 4).

**M4. `src/gnd/payloads.py`, ~30 lines.** `build_check_payload(...,
declared: Mapping[str, tuple[str, Addressing, str | None]] | None = None)`. When
`schema_version == 15`, each serialized verdict gets `address`,
`addressing` and `remedy` from `declared`, inserted after `constraint_ref`.
`schema_version == 15` with `declared is None` raises `ValueError` (a
programming error, not a user path).

**M5. `src/gnd/checking_service.py`, ~25 lines.** The plain snapshot path
selects 15 instead of 7 when `rule_ids` is set and passes the map built
from `iter_constraints()` and `declared_constraint_address`. Refusal (D3): a model with an active redaction
policy or temporal terms is refused with issue rule id
`check:rule-ids-unsupported`, exit 3, because those paths re-project to
v10/v13 (`_project_result`).

**M6. `src/gnd/commands/checking.py`, ~25 lines.** `--rule-ids`
(`store_true`, help: "report version 15: each verdict carries the
constraint's declared id and remedy"). Mutual exclusion with `--populations`,
`--pre/--steps/--post`, `--anchors`, `--document`, `--composition`,
`--sources`, `--admission` via `parser.error` (64). Text output under the
flag prints `[fail] constraint:no_import_loops (fact_types[…].constraints[0]): …` and,
when present, an indented `remedy:` line.

Branch registry (`src/gnd/branches.py`): register
`report:check:n-a:rule-ids` for the v15 projection so branch coverage stays
complete.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Field name: `remedy` or `message`? | `message` collides with the verdict's own `message` key | `remedy` |
| D2 | Flag name | `--rule-ids` vs `--report-version 15` (a general selector nobody has yet; widens every arm's contract) | `--rule-ids` |
| D3 | Redaction/temporal models with `--rule-ids` | refuse (exit 3) vs build v10/v13 successors now (doubles the phase) | refuse; plan §7 lists successors as out of scope |
| D4 | Should `remedy` appear in `gnd verbalize`? | yes adds a verbalization golden change | no in RC1; RC6 decides |
| D6 | Bare `constraint_id` (as the request words it) or `address` + `addressing`? | bare id needs a second rule for constraints without one; `address` reuses the census's existing scheme and gives RC3 its key with no extra rule | `address` + `addressing` |
| D5 | Does `remedy` change the model digest? | it is model content, so yes for models that use it; models without it are unaffected | yes; T8 shows the unaffected case |

## 8. Tests (`tests/test_rc1_rule_ids.py` unless noted)

| T | Case | Expected |
|---|---|---|
| T1 | model with `remedy` on a fact-type and a top-level constraint validates | exit 0 |
| T2 | `remedy: 7`, `remedy: ""`, 2001-char remedy | exit 3, `jsonschema:*` issue |
| T3 | `--rule-ids --format json` on a failing ring rule with id | exit 1, v15, `address == "constraint:no_import_loops"`, `addressing == "declared-id"` |
| T4 | constraint without id / without remedy | `address` equals `constraint_ref`, `addressing == "positional"`; `remedy` null |
| T5 | ids for fact-type constraints and top-level constraints both resolve | correct ids |
| T6 | v15 payloads validate; a v7 payload with `address` added fails validation | as stated |
| T7 | `--rule-ids` with each conflicting flag | exit 64, no payload; parser order before model load |
| T8 | without the flag: `tests/test_rf1_semantic_pins.py` unchanged; model digest of a remedy-free model unchanged | pass |
| T9 | redaction-policy model and temporal model with `--rule-ids` | exit 3, `check:rule-ids-unsupported` |
| T10 | text output under the flag prints id and remedy | substring checks on real output |
| T11 | `gnd coverage` census addresses unchanged after the move (`tests/test_coverage_payload.py`, `tests/test_address.py`) | pass |

Branch walk: flag on/off (T3/T8), id present/absent (T3/T4), remedy
present/absent (T3/T4), fact-type vs top-level (T5), each refusal (T7, T9).

## 9. Out of scope for this phase

Acyclic extent (RC2), baseline (RC3), vacuous (RC4), source (RC5), prose
documentation (RC6), v15 for any arm other than plain snapshot.

## 10. Size

About 190 source lines, 350 test lines (estimate).

## 11. Approval instrument

This prose.
