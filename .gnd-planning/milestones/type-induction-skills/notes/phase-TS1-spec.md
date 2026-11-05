# Phase TS1 spec: type evidence from the fact-type family

## 1. Status

**Draft r1, awaiting owner review; blocked until PR #86 merges** (plan
TS-D1). Implementable once the plan is approved, this spec is approved, and
it has been rebased onto the PR #86 merge commit with every cited line
re-read.

## 2. Provenance

- Plan: [type-induction-skills-plan.md](type-induction-skills-plan.md) r1,
  §2.1, §4 TS1, §9 TS1 row. The plan carries no review opinion and no
  approval.
- Code read at `549ebb9` (`claude/process-milestone-composition`):
  `src/gnd/discover/types.py`, `discover/service.py`, `discover/output.py`,
  `commands/discover.py`, `discover.schema.json`, `disclosure.py`.
- Prior records: CT4 record `005` (D5, F2, F3, F4, F10), CT close `007`
  (R2-1, R3-F1, CT-close-Q1, Q2).
- No review has run over these bytes.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| Plan O4 | evidence: signatures, digests, readings, row counts | §6.1, §6.2; TS1-C1, C2 |
| Plan O5, TS-R1 | default unchanged; `--out`/`--report` identical with the option | §6.4; TS1-C6 |
| Plan O6, TS-R5 | value-free unless `values_allowed` | §6.3; TS1-C4 |
| Plan TS1-C3 | `origin` from `provenance.induced_from` | §6.2; T7, T8 |
| Plan TS1-C5 | path rules and exits | §6.4; T10..T13 |
| Plan TS1-C7 | cap and `truncated` | §6.2; T14 |
| CT4 F2 / close R2-1 | written-bytes budget | §6.2 (evidence has its own cap; the proposal budget is untouched) |
| CT4 F4 | redaction | §6.3; T6 |
| TS-R7 | lane `discover`, RF6 ceiling | §4 |
| RF1 pins | `discover` help and exit goldens | §6.4; T15 |

## 4. Standing rules, bound

- **TS-R1:** the evidence builder is a pure function of the family's internal
  grouping; `propose` returns the groups it formed, and `--out`/`--report`
  are written from the same `TypeProposals` as today. T16 compares bytes.
- **TS-R2:** the evidence states `signature_equal`; it never states
  "duplicate".
- **TS-R3:** not yet bound (no judgements in TS1); the evidence's own
  `model_sha256` and `population_sha256` are the raw-byte digests the report
  already uses, so TS2 can bind to them.
- **TS-R4:** no proposal changes in TS1.
- **TS-R5:** §6.3.
- **TS-R6:** no skill in TS1.
- **TS-R7:** `gnd.discover.type_evidence` added to `tools/gnd_layers.json`
  in lane `discover`. Model reads go through `ModelIndex`
  (`iter_fact_types_shared`, `role_object_types`); the spec measures the
  RF6 count after the rebase and records it; the expected growth is zero
  because the module reuses the index already built in `propose`.
- **TS-R8:** no skill links in TS1.
- **Standing rules (process-phase):** each bound in the record at step 3;
  the total-loader rule binds `induced_from` parsing (malformed exits 3, never
  raises).

## 5. Goal

`gnd discover MODEL POP --out P --report R --families fact-type
--type-evidence E` exits 0 and writes `E` conforming to
`src/gnd/type-evidence.schema.json`, while `P` and `R` are byte-identical to
the same run without `--type-evidence`. Every run without the option gives
the baseline outputs, exits and stdout, except the `discover` usage text.
The focused gate exits 0.

## 6. Design

### 6.1 `src/gnd/discover/types.py` (about +30 lines)

`propose(...)` gains no parameter. `TypeProposals` gains
`groups: list[GroupRecord]`, filled for every group in iteration order:

```python
@dataclass(frozen=True)
class GroupRecord:
    generic: str
    attribute_sha256: str
    status: str            # "proposed" | "shape_match" | "multi_valued" |
                           # "below_support" | "mixed_type" | "over_budget"
    signature: str | None  # canonical text of role_player_signature(players); None before typing
    value_primitive: str | None
    entity_object_type: str
    support: int
    rows: int
    multi_entities: int
    multi_max: int
    exact_repeats: int
    row_ids: tuple[str, ...]   # first 32
    attribute: Any             # raw; only the writer decides whether it is emitted
    pairs: frozenset[tuple[Any, Any]]  # typed (entity, value) identities, in memory only
```

The spellings of `status` match the existing `skipped` keys except
`mixed_type` (`skipped` says `mixed_type_groups`) and `shape_match`
(`shape_matches` list). Both spellings stay as they are; the evidence
schema enumerates its own. Groups dropped later by `drop_last` have their
status rewritten to `over_budget` by `drop_last`.

`group["values"]` already holds distinct values per entity; `exact_repeats`
counts rows whose (entity, value) identity repeats.

### 6.2 `src/gnd/discover/type_evidence.py` (new, about 150 lines)

```python
FORMAT = "gnd-type-evidence/1"
MAX_EVIDENCE_BYTES = 10 * 1024 * 1024

class TypeEvidenceError(ValueError):
    """A malformed provenance.induced_from (exit 3)."""

def build_evidence(
    view: PopulationView,
    proposals: TypeProposals,
    *,
    model_sha256: str,
    population_sha256: str,
    min_support: int,
    show_values: bool,
    redacted_generics: list[str],
) -> dict[str, Any]: ...

def evidence_bytes(document: dict[str, Any]) -> bytes:
    """canonical_json_bytes, after trimming candidates from the tail to the cap."""
```

Document, as literal JSON (fields in this order after canonicalisation):

```json
{"format": "gnd-type-evidence/1",
 "model_sha256": "...", "population_sha256": "...",
 "min_support": 20, "show_values": false,
 "groups": [{
   "generic": "item_has_attribute", "attribute_sha256": "...",
   "status": "shape_match", "signature": "...", "value_primitive": "String",
   "support": 24, "rows": 24, "multi": {"entities": 0, "max": 1},
   "exact_repeats": 0, "row_ids": ["ft3#0"],
   "candidates": [{
     "fact_type": "item_has_attribute_induced_0",
     "readings": ["{Item} has induced item_has_attribute attribute 0 {AttributeValue}"],
     "roles": [{"name": "entity", "object_type": "item"},
               {"name": "value", "object_type": "attribute_value"}],
     "signature_equal": true, "rows": 24,
     "overlap": {"entities": 24, "pairs": 0},
     "origin": {"generic": "item_has_attribute", "attribute_sha256": "..."}
   }]
 }],
 "redacted_generics": ["..."],
 "truncated": 0}
```

`value` appears in a group only when `show_values`. Candidates: every fact
type in which `entity_object_type` plays a role, excluding the generic fact
type itself, in `ModelIndex` order (TS-Q1 / D1). `readings` are the model's
`reading` and `inverse_reading` strings when present. `overlap.entities`
counts the group's entities that appear in the candidate's role played by the
entity type; `overlap.pairs` is computed only for binary candidates whose
other role's primitive matches `value_primitive`, else `null`. `origin` is
`provenance.induced_from` when it is an object with exactly string keys
`generic` and `attribute_sha256` (64 lowercase hex), `null` when absent; any
other value raises `TypeEvidenceError` (exit 3).

Cap: if `evidence_bytes` would exceed `MAX_EVIDENCE_BYTES`, candidates are
dropped from the last group backwards, one at a time, and `truncated` counts
them; if groups alone exceed it, the run exits 70 (an internal defect: the
population cap bounds the group count far below this; argued in the record).

### 6.3 Disclosure

`show_values` is the value `commands/discover.py:131` already computes with
`values_allowed(args.show_values, "--show-values")`; the evidence reuses it.
No new site row: `--type-evidence` is an output of the same leaf. The
`option` convention table in `disclosure.md` gains one sentence; T15's case
map and the T26 arithmetic do not change (no new leaf). Redacted generic
fact types appear only by id. A redacted entity role: candidates are still
listed (ids and counts only), as overlap counts carry no value.

### 6.4 CLI and service (about +40 lines)

- `commands/discover.py`: `--type-evidence PATH`, help "fact-type family:
  also write the type evidence the judgement skills read". Without
  `--families fact-type`, 64 with the existing message extended.
  `--out`, `--report`, `--type-evidence`, MODEL and POPULATION must be five
  different paths (64). Existing file 11, symlink 74, both checked before any
  write, as `--out` is.
- `discover/service.py`: the run function gains keyword
  `type_evidence: Path | None = None`; it builds the evidence after the
  budget trimming (so statuses are final) and writes it with the same
  create-once publisher as `--out`, after `--report`.
- `discover.schema.json`: unchanged. `src/gnd/type-evidence.schema.json`
  new, Draft 2020-12, closed objects.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 (TS-Q1) | Candidate scope | (a) every fact type the entity type plays: a larger file, but a judge sees fact types with other value types; (b) binaries with equal signature only: smaller, but hides the semantic duplicates whose value type differs, the case the owner's ruling is about | (a) |
| D2 | Overlap for non-binary or type-mismatched candidates | (a) `pairs: null`, entities still counted; (b) omit the candidate | (a) |
| D3 | Evidence when the family writes no `--out` (nothing proposed) | (a) still written: the multi-valued and shape-matched groups are exactly what the skills need; (b) only with `--out`: the CLI's "written only when something is emitted" rule | (a); same exit 0 |
| D4 | Write order | (a) evidence after report, create-once; a failure leaves report without evidence, exit 74; (b) staged all-or-nothing: a new staging path for discover | (a), matching `--out` |
| D5 | `signature` text form | (a) the helper's canonical tuple rendered as canonical JSON; (b) a hash: opaque to a reader | (a) |

## 8. Tests

File `tests/test_discover_type_evidence.py` unless stated. Fixture: a model
with generic `item_has_attribute`, one applied induced fact type
`item_has_attribute_induced_0` carrying `provenance.induced_from`, one
unrelated fact type the item plays, one equal-signature fact type with
disjoint data; a population with attributes `size` (24 entities, functional,
also populated in the induced fact type), `colour` (24, functional), `tag`
(24, multi-valued), `rare` (3), `mixed` (an unvalidated view, as CT4-C2).

| # | Case | Criterion | Expect |
|---|---|---|---|
| T1 | every group once, statuses as the report's skips | TS1-C1 | 0; counts equal |
| T2 | order equals family order | TS1-C1 | 0 |
| T3 | candidates list all three fact types the item plays | TS1-C2 | 0 |
| T4 | `size` vs induced_0: overlap pairs 24; vs disjoint: 0 | TS1-C2 | 0 |
| T5 | `tag`: multi entities and max | TS1-C1 | 0 |
| T6 | redacted attribute role: generic listed by id only | TS1-C4 | 0 |
| T7 | origin read back | TS1-C3 | 0 |
| T8 | malformed `induced_from` (three forms) | TS1-C3 | 3, nothing written |
| T9 | canary value: absent unset/customer, present internal and unset+flag; customer+flag | TS1-C4 | 0 / 0 / 3 |
| T10 | option without family | TS1-C5 | 64 |
| T11 | path equal to `--out`, `--report`, MODEL, POP | TS1-C5 | 64 |
| T12 | existing evidence file | TS1-C5 | 11, nothing written |
| T13 | symlinked evidence path | TS1-C5 | 74 |
| T14 | cap: monkeypatched small cap trims and counts | TS1-C7 | 0; `truncated` > 0 |
| T15 | RF1 `discover` help/exit goldens re-pinned; usage-line diff only | TS1-C6 | gate |
| T16 | `--out`, `--report` bytes equal with/without the option, over every fixture | TS1-C6 | equal |
| T17 | parity script over CT4 cases and IK4 table without the option | TS1-C6 | equal to baseline except E1/E6 usage |
| T18 | schema validation of every written evidence | all | valid |
| T19 | nothing proposed, evidence still written (D3) | D3 | 0, no `--out` |

Gate: `uv run pytest -q tests/test_discover_type_evidence.py
tests/test_discover_fact_type_family.py tests/test_discover.py
tests/test_evolve_additive_policy.py tests/test_evolve_shape_matches.py
tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py
tests/test_disclosure_mode.py tests/test_disclosure_docs.py
tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`
(re-checked against the file list after the rebase).

## 9. Out of scope for TS1

Judgements, rendering, `provenance.induced_from` writing (TS2), skills,
docs pages beyond the `discover.md` option paragraph and release note, a
Python API, digest salting.

## 10. Size

Estimate: about 220 source lines (types +30, type_evidence 150, CLI and
service 40) and 450 test lines; schema about 120 lines.

## 11. Approval instrument

This prose. No fixture corpus first; the fixture is built in the tests.
