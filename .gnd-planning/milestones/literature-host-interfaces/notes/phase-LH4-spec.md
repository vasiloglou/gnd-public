# LH4 spec · admission rules as data

## 1. Status

Draft, 2026-11-23. Its gate, delegated by the owner's `/process-milestone
literature-host-interfaces auto` (auto=true), follows the LH3 record and the
milestone coordinator's ordering GO.

## 2. Provenance

Derived from [plan r6](literature-host-interfaces-plan.md) (sha256
`2dc760e5…1528`, approved in `001-plan-gate.md`): Goal (LH4), §0 R0.4, §1
H12, H13, H17, H18, §2 "LH4" (with the r6 paragraph "The packaged shape"),
§2 LH3 "Record", §4 LH4-C1 to LH4-C7, §9 LH4 row, and D2, D11, D12, D18.
It builds on LH3 (`dcd3a61c`). No review has run over this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| §2 "Rules" | rules are an ordered list of requirements, each with an ID, an attached fact type, a role, the admissible values and optional reasons; an assertion satisfies one when it has at least one row of that fact type and every such row is admissible; the first failing requirement gives the reason: the declared reason for the offending value, else its ID | §6.1, §6.2; T1, T3 |
| §2 "Default rules", R0.4 | the packaged comparison becomes the default rules, evaluated by the one evaluator: polarity first (`negates` reason `negated`), then attribution (each other value its own reason); the H18 stage table does not move | §6.3; T6 |
| §2 "The packaged shape" (r6) | on the packaged shape a requirement may name only `assertion_statement`; any other fact type refuses | §6.2; T5 |
| §2 "Disposition", D2 | in a `/2` record a supported assertion that fails a requirement is `policy-refused` with that reason; an unsupported one keeps `fail`; `/1` keeps today's statuses | §6.4; T2 |
| §2 "A rule that names nothing refuses" | an unknown fact type or role refuses the call | §6.2; T5 |
| §2 "Target cap", D11, H13 | `max_targets` from 1 to 1,024; a lowered cap refuses a policy over it | §6.1; T4 |
| §2 LH3 "Record", D12, D18 | a call with rules, a shape, `max_targets` or (with a shape) `max_rows` writes `/2`, binding the shape and rules digests and recording `max_targets` and `max_rows`; a rules-only call records the shape `packaged` and `max_rows` `null` | §6.4; T7 |
| LH4-C1 … C7 | each criterion | §8 |
| §5, §3 LH4 row | the admission README section, `docs/literature/commands.md`, `docs/release-notes.md`, `dev/components/` | §6.5 |
| §9 LH4 row | the focused lane, then `uv run python tools/run_tutorials.py --group literature` | §8 ledger |

## 4. Standing rules, bound to this phase

| Rule | Bound here |
|---|---|
| R0.2 packaged bytes | the packaged call with no new argument keeps the four H18 digests (T6) |
| R0.4 one evaluator | `_evaluate_rules` is the only place a requirement is evaluated, for the default rules and a caller's |
| 1 totality | the rules document is untrusted: `_rules` checks every key, type and count before use (T5) |
| 2 time bound | evaluation is one pass over each assertion's rows per requirement; T8 evaluates 64 requirements over the LH3 ceiling run within 60 s |
| 3 validation order | the rules and `max_targets` are checked before the judgment route runs (T5 pins it) |
| 5 one home | the rules format and the `/2` record are described once, in the admission section of the literature README |
| failure class "any versus every" | T3 holds an assertion with one admissible and one inadmissible row, and one with no row |

## 5. Goal

`admit(..., rules=RULES, max_targets=N)`, with or without a shape, admits
the supported assertions that satisfy the rules and records the others as
`policy-refused` with the first failing requirement's reason. The plan §9
LH4 row, the guard block and the whole-repository `uv run ruff check` exit 0.

## 6. Design

### 6.1 Signature

```python
RULES_FORMAT = "literature-admission-rules/1"

def admit(model, raw, policy, receipts, trusted_root, out, *,
          shape=None, rules=None, max_targets=None, max_rows=None) -> dict: ...
```

### 6.2 The rules document

```json
{"format": "literature-admission-rules/1", "requirements": [
  {"id": "positive", "fact_type": "claim_polarity", "role": "polarity",
   "admissible": ["asserts"], "reasons": {"negates": "negated"}}]}
```

Closed keys; `id` unique, matching `[a-z][a-z0-9-]{0,63}`; `admissible` a
non-empty list of distinct JSON scalars; `reasons` maps an inadmissible value
(as a string key) to a reason matching the same pattern. At most 64
requirements. Under a shape the fact type must be attached and the role one
of its roles; on the packaged shape the fact type must be
`assertion_statement` and the role one of `ROLES`. Anything else refuses
`rules:invalid` or `rules:unknown-fact-type` / `rules:unknown-role`.

### 6.3 One evaluator, two projections

`_evaluate_rules(requirements, rows_of)` returns the first failing
requirement's reason or `None`, where `rows_of(fact_type)` gives one
assertion's rows. The packaged projection calls it with `DEFAULT_RULES`
(polarity, then attribution) on each statement's single row, in place of
the literal comparison at `:122`; the generic projection calls it with the
caller's rules, after support, for each supported assertion.

### 6.4 Statuses and the record

- `/1` (no new argument): unchanged.
- Packaged shape with rules or `max_targets`: `/2`, `shape: "packaged"`,
  `max_rows: null`; the stage table keeps its two stages, with
  `policy-refused` in place of `fail` for a supported statement that fails a
  rule.
- Generic shape: the `semantic-support` stage of LH3, and an
  `admission-rules` stage with one row per assertion: `pass`,
  `policy-refused` with the reason, or `fail` for an unsupported one.
- Every `/2` record carries `shape_sha256` (or `"packaged"`),
  `rules_sha256` (of the canonical rules, or `null` with no rules),
  `max_targets` and `max_rows`.

### 6.5 Documents

The admission README section gains the rules format and the statuses;
`docs/literature/commands.md` gains a short host passage after the
admission example, linking to it; `docs/release-notes.md` gains an
unreleased entry for the admission pair (LH3, LH4).

## 7. Decisions

| ID | Question | Proposed | What the other reading costs | Ruling |
|---|---|---|---|---|
| LH4-D1 | How a value is matched | By JSON equality: `"1"` and `1` differ; reasons are keyed by the value's canonical JSON text | Matching by string form admits a number where a string was declared | open |
| LH4-D2 | The packaged stage names under rules | Keep `semantic-support` and `positive-own-findings` | Renaming breaks `test_li4`'s reading of a `/2` call over the packaged files for no gain | open |

## 8. Tests

`tests/test_lh4_admission_rules.py`, on LH3's fixture with a
`claim_polarity` fact type added to its model.

| ID | Case | Expected | Criterion |
|---|---|---|---|
| T1 | two rules files over the same inputs | two different admitted sets, each stated in the test | C1 |
| T2 | a supported claim failing a rule; an unsupported claim | `policy-refused` with the reason; `fail` | C2 |
| T3 | a claim with one admissible and one inadmissible row; a claim with no row of the named fact type | `policy-refused` each | C3 |
| T4 | `max_targets` below the policy's target count; `max_targets` 1,025, 0 and `True` | refuses each, nothing published | C4 |
| T5 | a requirement naming an unknown fact type, an unknown role, a non-attached fact type; on the packaged shape a requirement naming `assertion_names_work`; each malformed rules document (not an object, a key missing, an extra key, a duplicate id, an empty `admissible`, 65 requirements); the judgment route fails the test if run | exit 3, nothing published | C5 |
| T6 | the packaged call with no argument; with the default rules passed explicitly | the H18 digests and stage table; `/2` with the same reasons and order, `positive-own-findings` statuses `policy-refused` where `/1` has `fail` for supported statements | C6 |
| T7 | `/2` records with each of shape, rules, `max_targets`, `max_rows` changed | each record differs in that field and its digest; a rules-only call records `packaged` and `null` | C7 |
| T8 | 64 requirements over LH3's row-ceiling run | within 60 s | rule 2 |

Verification-selection ledger:

| Obligation | Disposition | Command | Input boundary | Invalidation |
|---|---|---|---|---|
| plan §9 LH4 row | run | `uv run pytest -q tests/test_lh4_admission_rules.py tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short`, then `uv run python tools/run_tutorials.py --group literature`, exit 0 each | `assertion_admission.py`, the fixtures, the docs | any edit to those |
| guard block | run | `project.md`'s twelve-file command | guarded inventories | any scanned file |
| lint | run | `uv run ruff check` | the repository | any Python file |
| component index | run | `python3 scripts/components_index.py changed --base <LH4 base> --strict` | `dev/components/` | a changed module |
| broad lanes | cadence | explicit request only | historical replays | none |

## 9. Out of scope for this phase

Rules over followed fact types (a requirement names an attached fact type
only). A command-line flag. Batching inside `admit()`.

## 10. Size

Estimate: `assertion_admission.py` +110 lines; the test module about 260
lines; the docs about 50 lines.

## 11. Approval instrument

This prose.
