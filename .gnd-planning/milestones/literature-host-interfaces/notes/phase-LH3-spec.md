# LH3 spec · admission over a caller-named assertion entity

## 1. Status

owner-decided (2026-11-23) by **delegated approval (auto=true)**: see §7 and
§12. Base commit `f82490cb` (LH2's record), on the branch
`claude/literature-host-interfaces-admission`, the second of the two pull
requests. Prior status: "Draft, 2026-11-23".

## 2. Provenance

Derived from [plan r6](literature-host-interfaces-plan.md) (sha256
`2dc760e5…1528`, approved in `001-plan-gate.md`): Goal (LH3), §0 (R0.4 as
amended by the r4 panel), §1 H12 to H19, §2 "LH3", §3 LH3 row, §4 LH3-C1 to
LH3-C10, §9 LH3 row, and D8, D9 `(o)`, D10 `(o)`, D12, D17 `(o)`, D18. Code
read on 2026-11-23 at `0b330eb5` (`assertion_admission.py` unchanged since
`4ad0d216`). No review has run over this spec.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Goal LH3, §2 "Shape" | `admit()` takes a shape naming the assertion entity type and the entity types to follow; with no shape it writes today's bytes | §6.1; T1, T8 |
| §2 "Attached facts" (p2) | a fact type is attached when one of its roles is played by the assertion entity; every attached row of an admitted assertion is kept, except a row that also names an assertion that was not admitted | §6.3; T1, T4 |
| §2 "Followed facts" `(o)`, D9, D17 | from kept rows, instances of listed entity types bring the rows of every fact type that entity plays a role in; the walk continues; an unlisted entity type is a value only; a row naming a rejected assertion is never kept | §6.3; T1, T10 |
| §2 "Coverage" | `covers` lists the attached fact types and the fact types of the followed entity types | §6.3; T1 |
| §2 "Identity" `(o)`, D10, H14 | the assertion's own handle is its identity; a shape naming an entity that objectifies a fact type refuses, naming the objectification | §6.2; T2 |
| §2 "Judged unit", D8 | targets are rows attached directly to the assertion; supported means at least one target and every target admitted; a target on any other row refuses | §6.3; T3, T6 |
| §2 "Optional facts", H16 | no value reads as absent; the tag vocabularies and the condition rule stay on the packaged shape | §6.3; T7 |
| §2 "Row bound", D18 | `max_rows`, default 16,384, ceiling 65,536, bounds attached and followed rows read; the packaged projection keeps `MAX_TARGETS` | §6.1; T9 |
| §2 "Include roots", H15 | the snapshot copies each declared include beside the root; the record binds each include's sha256 | §6.4; T5 |
| §2 "Record", D12 | a shaped call writes `literature-assertion-admission/2`; the packaged call keeps `/1` | §6.5; T1, T8 |
| R0.4 | the generic projection shares the snapshot, `_judgments`, `_verify_report_inputs`, the target-verdict mapping and the record writer with the packaged one | §6.3 |
| H17 | `lineage_run.py` keeps its imports and its six-argument call | T8 |
| H18, LH3-C8 | the packaged call's four output digests and stage table are unchanged | T8 |
| §9 LH3 row | `uv run pytest -q tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short` | §8 ledger |

## 4. Standing rules, bound to this phase

| Rule | Bound here |
|---|---|
| R0.1 formats stay | `/1` record and outputs unchanged (T8) |
| R0.2 packaged bytes | T8 compares the H18 digests |
| R0.3 example status | the module command line keeps its arguments; no flag is added |
| R0.4 one walk | one generic walk over attached and followed fact types; the packaged projection keeps its own path (D10) and shares every other home |
| R0.7 stable commands judge | `gnd judgments check` judges; the example adds no check of its own on the model or the population |
| 1 totality | the shape and the subject population are untrusted: `_shape` and `_generic_rows` check every key, type and count before use; T6 |
| 2 time bound | the walk indexes each (fact type, role) once and visits each row at most once; T9 runs 1,024 targets and `max_rows` rows within 30 s |
| 3 validation order | shape, `max_rows`, snapshot and includes, judgment route, then projection. T6 pins that a malformed shape refuses before the judgment route runs |
| 4 one walk | as R0.4 |
| 5 one home | the shape, the walk and the `/2` record are described once, in the admission section of `src/gnd/examples/literature/README.md` |
| 6 measurement | T2's refusal and T5's include case are measured against `gnd judgments check` itself |

## 5. Goal

`admit(..., shape=SHAPE)` over a caller's model, population, policy and
receipts publishes the admitted population, the raw population, the
judgment report and a `/2` record, or refuses with a value-free reason and
publishes nothing. The plan §9 LH3 row, the guard block and the
whole-repository `uv run ruff check` exit 0.

## 6. Design

Reuse: `examples.literature_assertion_admission` (adapt); `gnd.model`
`load_model_bytes`, `load_model_bytes_composed` and `gnd.model_index.ModelIndex`
(reuse, as `judgments.py` does) to read the entity and fact types.

### 6.1 Signature

```python
SHAPED_SCHEMA = "literature-assertion-admission/2"
SHAPE_FORMAT = "literature-assertion-shape/1"
MAX_ROWS, MAX_ROWS_CEILING = 16384, 65536

def admit(model, raw, policy, receipts, trusted_root, out, *,
          shape: dict | None = None, max_rows: int | None = None) -> dict: ...
```

`shape` is `{"format": SHAPE_FORMAT, "assertion": ENTITY, "follow": [ENTITY, ...]}`,
closed and required keys, `follow` without duplicates and without the
assertion type. `max_rows` is an int from 1 to 65,536 and needs a shape.

### 6.2 Identity

The assertion type must be an entity type of the model (composed for an
include root). If any fact type has `objectified_as` equal to it, the call
refuses `shape:objectified-assertion`. Each listed follow type must be an
entity type (`shape:unknown-follow`). At least one fact type must be attached
(`shape:no-attached-facts`).

### 6.3 The generic walk

1. Index, once, each row of each attached and followed fact type by the
   values of its entity-typed roles. More than `max_rows` such rows refuses
   `input:row-cap` before any walk.
2. Each attached row belongs to every assertion its assertion-typed roles
   name.
3. Targets come from the judgment report, as today. A target whose fact type
   is not attached refuses `judgments:target-outside-shape`. An assertion
   with no target among its rows is `missing`; one with a target not
   admitted takes that target's reason from the target-verdict mapping
   (`_target_reason`, the target half of today's `_support`); otherwise it
   is supported, and with no rules (LH4) it is admitted.
4. Kept: every attached row whose assertion-typed roles all name admitted
   assertions; then, breadth first from the kept rows, every row of a fact
   type in which a followed type plays a role, for each followed instance a
   kept row names, unless the row names an assertion that was not admitted.
   Each row is kept once.
5. The admitted population is the subject's header with `covers` set to the
   attached and followed fact types in model order, `source`
   `tool-output`, `producer` the `/2` schema, `instances` `{}`, and the kept
   rows of each covered fact type in their original order.

### 6.4 Snapshot and includes

A model that declares includes is an include root: each include path must be
relative, without `..`, and is copied beside the model in the judgment
route's folder under that path. `gnd judgments check` composes and checks
the pins. The record binds `includes: {path: sha256}`.

### 6.5 The `/2` record

```json
{"schema": "literature-assertion-admission/2", "model_sha256": "…", "includes": {},
 "raw_sha256": "…", "policy_sha256": "…", "receipts_sha256": "…",
 "judgment_report_sha256": "…", "admitted_sha256": "…",
 "shape_sha256": "<sha256 of canonical shape>", "max_rows": 16384,
 "stages": {"semantic-support": [{"assertion": "c1", "status": "pass", "reason": null}]}}
```

Assertions are listed in order of first appearance in the attached fact
types. LH4 adds the rules, `max_targets` and the policy stage.

## 7. Decisions

| ID | Question | Proposed | What the other reading costs | Ruling |
|---|---|---|---|---|
| LH3-D1 | How the shape reaches `admit()` | A keyword argument holding the shape document | A file path needs a second reader and a size cap for one small object | as proposed (delegated, auto=true, 2026-11-23) |
| LH3-D2 | The stage table of a `/2` record | One row per assertion, keyed by its handle | One row per target row repeats an assertion's verdict across its rows | as proposed (delegated, auto=true, 2026-11-23) |
| LH3-D3 | `instances` in the admitted population | `{}`, as the packaged projection writes | Copying the subject's instances needs their format, which no caller has asked for | as proposed (delegated, auto=true, 2026-11-23) |

## 8. Tests

`tests/test_lh3_admission_shape.py`, fixture `tests/fixtures/lh3-admission/`
(a claims model with a `claim` entity, an include root, a `quantity` entity
with value and unit rows, a `paper` entity not followed, a claim-to-claim
fact type; raw population, policy, saved receipts and evidence built by the
fixture's own builder script).

| ID | Case | Expected | Criterion |
|---|---|---|---|
| T1 | claims sharing a passage; one with two actors and no object; one with three conditions; one with a quantity (value and unit rows); shape follows `quantity` | every attached row of each admitted claim kept, the quantity's rows kept, no row of another claim; `gnd check` on the admitted population exits 0; `/2` record | C1 |
| T2 | the packaged model with a shape naming `assertion` | exit 3 `shape:objectified-assertion`, nothing published | C2 |
| T3 | a claim with one admitted and one rejected target; one with one admitted target and untargeted rows; one with no target | not admitted; admitted with all its rows; `missing` | C3 |
| T4 | a claim-to-claim row between two admitted claims, and between an admitted and a rejected one | kept; not kept | C4 |
| T5 | the model as an include root; the include edited without a new pin | admits and binds the include; exit 3, nothing published | C5 |
| T6 | each refusal: shape not an object, a key missing, an extra key, an unknown assertion type, a value type as assertion, an unknown follow type, a duplicate follow, no attached fact type, a target outside the shape, an include path with `..`, `max_rows` 0, 65,537, `True`, and `max_rows` without a shape | exit 3 with a value-free reason, nothing published | C6 |
| T7 | a generic row whose condition is `none` | an ordinary value, kept | C7 |
| T8 | the packaged call | the H18 digests and stage table; `test_li4` and `test_li5` pass unedited | C8 |
| T9 | 1,024 targets with attached and followed rows at the `max_rows` ceiling; one row more | within 30 s; refuses `input:row-cap` | C9 |
| T10 | a quantity named by an admitted and a rejected claim; a row reached through a followed entity that names a rejected claim; an unlisted entity type (`paper`) | the quantity's rows kept once, the rejected claim's row not kept; not kept; `paper`'s own rows not copied | C10 |

Verification-selection ledger:

| Obligation | Disposition | Command | Input boundary | Invalidation |
|---|---|---|---|---|
| plan §9 LH3 row | run | `uv run pytest -q tests/test_lh3_admission_shape.py tests/test_li4_assertions.py tests/test_li5_lineage.py --tb=short`, exit 0 | `assertion_admission.py`, the fixtures | any edit to those, or to `gnd judgments check` |
| guard block | run | `project.md`'s twelve-file command, exit 0 | guarded inventories | any scanned file |
| lint | run | `uv run ruff check`, exit 0 | the repository | any Python file |
| component index | run | `python3 scripts/components_index.py changed --base f82490cb --strict`, exit 0 | `dev/components/` | a changed module |
| broad lanes | cadence | explicit request only | historical replays | none |

## 9. Out of scope for this phase

Admission rules, the `policy-refused` status and `max_targets` (LH4). A
command-line flag. Admitting an entity that objectifies a fact type (D10).
Following an unlisted entity type (D17). Batching inside `admit()`.

## 10. Size

Estimate: `assertion_admission.py` +170 lines; the test module about 300
lines; the fixture builder about 150 lines; the README section about 50
lines.

## 11. Approval instrument

This prose.

## 12. Gate

Delegated approval (auto=true), 2026-11-23, under the owner's
`/process-milestone literature-host-interfaces auto`. Instrument: this prose.
Decisions: LH3-D1 to LH3-D3 as proposed (§7). Budget: one review round over
the phase diff with the review helper (plan D13), a second only if the
convergence rules call for it. Compatibility: the packaged call's H18
digests; `lineage_run.py`'s imports and call; `test_li4` and `test_li5`
unedited. Ordering: the milestone coordinator's GO for LH3 (2026-11-23)
approves nothing; the README edit stays inside the admission section.
Spec bytes: the SHA-256 is recorded in the phase record.

Implementability sweep, at `f82490cb`: receipts for the fixture are built
with `gnd.judgments.judgment_fact_digest` and `judgment_receipt_digest`, as
`test_li4` builds its variants, so `gnd judgments check` judges the fixture
as it judges the packaged example. Model structure is read with
`load_model_bytes` and, for an include root, `load_model_bytes_composed`
over the snapshot folder, as `judgments.py` reads it. Every other
requirement maps to the design above.

## Implementation findings (2026-11-23)

1. **The include paths are read from the model document.** `_include_paths`
   parses the root with `gnd.model._parsing.parse_model_document`, the
   parser `bytes_declare_includes` itself uses, rather than a second reader.
   Nested includes are not copied; an include root whose include declares
   includes of its own refuses through the judgment route.
2. **The fixture's cases are built in the test module.** The model, its
   include and the evidence are committed under `tests/fixtures/lh3-admission/`;
   each case's population, policy and receipts are written by `_case()`
   with `gnd.judgments.judgment_fact_digest` and `judgment_receipt_digest`,
   so a case states its own verdicts. No separate builder script.
3. **`venue`**, an entity that plays no role, was added to the include so
   that `shape:no-attached-facts` has a case that can fail it.
4. **T9's time bound.** The row ceiling run (1,024 claims, 65,536 rows,
   1,024 receipts) is held to 60 s, not §8's 30 s: most of its time is the
   stable `gnd judgments check` route, which this phase does not change.
5. **T8 pins all four H18 digests**, not only the two populations.
