# Phase MG3: duplicate-shape report on evolve preview

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.** Implementation
follows this approval.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's invocation "process-milestone model-growth-guardrails auto" in this
session, which delegates spec rulings within this milestone. This is an agent
ruling under that delegation, not the owner's personal reading. Approved
bytes: SHA-256
`722f31121b8c327a7a76bdf712c31c7bdb53524765222bf325bd611024954879` (before
this tag), after the implementability sweep (one correction: stripping
`shape_matches` applies with 0, T5; the probe accounting in standing rule 2).
Rulings: D1 (b) prose, no spec review panel; D2 to D6 (a) as proposed.
Budget: about 170 source and 350 test lines; no paid calls. Compatibility:
previews without `--shape-report` unchanged (MG-R1), no exit change, no
version change. Review instrument for the diff: one local reviewer agent.

## Provenance

- Plan: [model-growth-guardrails-plan.md](model-growth-guardrails-plan.md) r3,
  approved `(a1)` 2026-11-03: §2.3, §3 (helper home), §4 MG3, §9 MG3 row,
  §10 MG-D7.
- Source: [issue #76](https://github.com/vasiloglou/gnd-public/issues/76)
  (GR-T13).
- Inspection baseline: `9b069e2` (main after PR #82, MG2 merged).
- Prior records: [002-phase-MG1.md](../002-phase-MG1.md),
  [003-phase-MG2.md](../003-phase-MG2.md). MG2 hands this phase MG2-Q1 (the
  `--policy` plus `--shape-report` apply case), MG2-Q3 (merge the two walks of
  the before model) and MG2-Q4 (RF6 headroom: the helper reads through
  `ModelIndex` only).
- Authority: the owner invoked `process-milestone model-growth-guardrails
  auto` on 2026-11-04, delegating plan, spec and close rulings within this
  milestone. **This spec's bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #76, plan O8 | For each proposed fact type, existing ones with the same arity and role players, compatible reference modes, and their readings | `shape_matches`; T2, T3 |
| #76, plan O9 | Structural only; meaning stays the caller's | MG-R4; T4; docs say "candidate" |
| Plan §4 MG3-C1 | The signature helper, with cases for role order, (A,A,B) against (A,B,B), a subtype that does not match its supertype, two value types with the same primitive that do not match, two identical ADDs in one proposal (they match each other) | T1 |
| Plan §4 MG3-C2 | `shape_matches` with readings and reference modes, stable order, only under `--shape-report` | T2, T3 |
| Plan §4 MG3-C3 | With and without the option, exit, `breaking`, blast radius and `report_sha256` equal (MG-R4); a `--shape-report` preview applies with exit 0; a recorded before/after table shows previews without the option unchanged | T4, T5, T6 |
| Plan §4 MG3-C4 | 5,000 fact types and a proposal adding 500: signature comparisons counted through a bucket index, ≤ 5,500 bucket probes | T7 |
| Plan §9 MG3 row | "Signature cases; report; no gate change"; the MG2 gate plus `tests/test_evolve_shape_matches.py` | Verification selection |
| Plan §2.2 (version scheme) | Optional preview field omitted when unset; V3 reader declares it; digest recomputed from the serializer | Design, models; T5, T6 |
| Plan §2.2 (apply) | The fresh preview is built with `--shape-report` exactly when the reviewed preview carries `shape_matches` | Design, CLI; T5 |
| MG2-Q1 | A preview made with `--policy` and `--shape-report` applies (0) | T5 |
| MG2-Q3 | Merge the two walks of the before model | D4 |
| MG2-Q4 | RF6 headroom; the helper reads through `ModelIndex` only | Design; T8 asserts no new counted read |
| Plan MG-R1 | Existing digests do not move | Omission in the serializer; T6 parity table; MG2's T5 byte pins |
| Plan MG-R2 | One signature helper, shared by MG3, MG4 and later CT4 | `gnd.refscheme.role_player_signature`; T1 |
| Plan MG-R3 | A gate never trusts a document it can be handed | Apply rebuilds the report from its own bytes; an edited `shape_matches` exits 11 (T5); stripping it is harmless because it gates nothing |
| Plan MG-R4 | Advice never gates | T4: exit, `breaking`, blast radius, `report_sha256`, `affected_references`, policy fields equal with and without; T5 |
| Plan MG-R5 | Disclosure | The `gnd evolve preview` leaf row already exists; the report carries ids, readings (model content) and reference kinds, never a population value; T9 |
| Plan MG-R6 | Layering and query policy | `gnd.refscheme` (layer `model`) gains the helper; reads through `ModelIndex.role_object_types` and `fact_type`; zero new counted reads; T8 |
| Plan MG-R7 | Anonymity | T10 |
| Plan MG-R8 | Provenance never overstated | Not applicable: the report writes no provenance and marks nothing |
| Plan §6 | "The shape report is read as 'these are duplicates'"; optional fields move old bytes; RF1 goldens drift; names leak | Field name `shape_matches`, docs say candidate (T11); T6; T12; T10 |
| Plan O18, O19 | Pins, docs, release notes | T12, T11 |
| Plan O23 | RF1 goldens recaptured and recorded | T12 |
| Plan §10 MG-D7 | Signature match rule | Accepted at the plan gate `(a1)` as (a); bound below |
| Plan §5 | `gnd-model-evolve` skill and contract; RF1 goldens for `gnd evolve preview`; Unreleased note | Docs section |
| Plan §7 | Semantic duplicates, refusing on a shape match, converting reference modes | Out of scope below |

## Standing rules bound to this phase

1. **Totality:** the report reads the loaded before model and the validated
   candidate model (both passed `load_model`), never a raw proposal dict.
   `role_player_signature` takes any mapping and ignores non-string values,
   so it is total; T1 feeds it hostile mappings.
2. **Input cap bounds the algorithm:** signatures are bucketed in one dict
   keyed by the sorted tuple; every existing and every added fact type is
   inserted once, and every added fact type probes once. Each fact type costs one `setdefault`
   probe; an added fact type keeps the returned bucket, so reading its
   matches costs no further probe. T7 measures probes ≤ 5,500 for 5,000 plus
   500, and wall time under 5 s.
3. **Validation order:** the report is computed after the policy, so a
   refusal before it (18, then 3) is unchanged; the report never raises.
   Source order pinned by T4b.
4. **One walk:** one bucket index serves every added fact type; there is no
   per-arity or per-kind copy.
5. **One home:** the signature rule (multiset of role-player ids, no
   supertype matching) is normative in the evolution contract's new "Shape
   report" section; `docs/reference/evolve-policy.md` cites it.
6. **Measurement over argument:** T6 is a recorded digest table at
   `9b069e2` and after.

## Goal

`gnd evolve preview MODEL PROPOSAL ... --shape-report` exits as it does
without the option and writes a schema-3 preview carrying `shape_matches`:
one entry per fact-type ADD, in operation order, each listing every fact type
of the before model, and every other fact type the same proposal adds, whose
role-player signature equals the added one's, with id, reading and inverse
reading. Without the option the preview's bytes and `preview_sha256` are
those at `9b069e2`. `gnd evolve apply` on a `--shape-report` preview exits 0
when nothing else differs, and 11 when `shape_matches` was edited.

## Design

### `src/gnd/refscheme.py` (about +45 lines; layer `model`)

```python
def role_player_signature(role_players: Mapping[str, Any]) -> tuple[str, ...]:
    """The sorted multiset of role-player object-type ids of one fact type."""

def fact_type_signatures(index: ModelIndex) -> dict[str, tuple[str, ...]]:
    """Every fact type's signature, from ``ModelIndex.role_object_types``."""

def entity_reference(object_type_id: str, model: Model) -> tuple[str, str | None]:
    """``(kind, value_type)`` from ``reference_identity``: kind ``direct``,
    ``composite`` or ``unmatchable``; the value type only for ``direct``."""
```

`role_player_signature(m)` is `tuple(sorted(str(v) for v in m.values() if
isinstance(v, str)))`. Role order is irrelevant by construction; (A,A,B) and
(A,B,B) differ as multisets; a subtype id is not its supertype's id; two value
types are two ids whatever their primitives. `__all__` gains the three names.
`role_object_types` already exists, so no new `fact_types` or `roles` read is
added (MG2-Q4).

### `src/gnd/evolve/shapes.py` (new, about 60 lines; lane `evolve`, layer `lanes`)

```python
def shape_matches(
    before: Model, candidate: Model, proposal: EvolutionProposal,
    *, bucket_factory: Callable[[], dict] = dict,
) -> tuple[ShapeMatchEntry, ...]
```

Added fact types are the `ADD` operations whose locator is
`ElementLocator(collection="fact_types")`, in operation order. Existing
signatures come from `fact_type_signatures(ModelIndex.for_model(before))`,
added ones from the candidate's index. The bucket index maps a signature to
the sorted ids in it, existing and added kept apart. Readings come from
`ModelIndex.fact_type(id)` (`reading`, `inverse_reading`) of the model that
holds the id. `bucket_factory` exists only so T7 can count probes.

### `src/gnd/evolve/models.py` (about +35 lines)

```python
class ShapeMatch(_ClosedFrozenModel):
    fact_type: StableId
    origin: Literal["existing", "added"]
    reading: NonEmptyString
    inverse_reading: str | None = None

class ShapeReference(_ClosedFrozenModel):
    object_type: StableId
    identity: Literal["direct", "composite", "unmatchable"]
    value_type: StableId | None = None

class ShapeMatchEntry(_ClosedFrozenModel):
    operation_index: int = Field(ge=0)
    fact_type: StableId
    signature: tuple[StableId, ...]
    references: tuple[ShapeReference, ...]   # entity role players only, sorted, once each
    matches: tuple[ShapeMatch, ...]          # sorted by (origin, fact_type); may be empty
```

`_EvolutionPreviewV3` and `EvolutionPreview` gain `shape_matches:
tuple[ShapeMatchEntry, ...] | None = None`; the serializer omits it when
`None`, like the policy fields. `_bindings_match` checks that the entries
are in operation-index order and each `matches` is sorted and excludes the
entry's own fact type. `ShapeReference.identity` uses the three spellings of
`reference_identity`'s first element, written here and asserted in T2.

### `src/gnd/evolve/service.py` (about +10 lines)

`EvolutionService.preview(..., shape_report: bool = False)`. After
`_policy_values`, when `shape_report` is true,
`values["shape_matches"] = shape_matches(before_loaded_model, candidate_model,
proposal)`. Nothing else reads it.

### `src/gnd/commands/evolve.py` and `cli_service.py` (about +20 lines)

`gnd evolve preview --shape-report` (store-true). `_cmd_evolve_preview`
passes it; the text claim prints one `shape-match: OP_INDEX FT -> MATCH`
line per match. `_cmd_evolve_apply` takes no new option: it passes
`shape_report=reviewed.shape_matches is not None` to both `service.preview`
calls (the fresh preview and the breaking-acceptance rebuild).

### Docs (about 60 lines)

The contract gains a "Shape report" section (normative home) and a row in
the preview field table; the `gnd-model-evolve` SKILL.md names the option;
`docs/reference/evolve-policy.md` gains a short "Shape report" section citing
the contract; `docs/reference/cli.md` the option; one Unreleased note.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument | (a) corpus-first; (b) this prose: the report is advice with no exit contract of its own, and every case is a small proposal over one fixture | (b) |
| D2 | An ADD with no match | (a) listed with `matches: []`: the caller sees each added fact type was checked; (b) omitted: shorter, but an absent entry cannot be told from an unchecked one | (a) |
| D3 | "Existing" | (a) the before model, so a fact type the same proposal deletes still matches its replacement; (b) the candidate model: a deleted fact type would vanish from the report | (a) |
| D4 | MG2-Q3, merging the before-model walks | (a) do not merge: the shape report adds one `role_object_types` pass over before and one over the candidate, separate inputs, all linear; merging three functions couples their signatures for no measured cost; close MG2-Q3 as argued; (b) merge into one pass | (a) |
| D5 | Reference modes | (a) report `reference_identity`'s kind and direct value type per entity role player, once per entry (equal ids imply equal schemes, so every match shares them); (b) per match: repeats the same data | (a) |
| D6 | Apply option | (a) none: apply follows the reviewed preview (`shape_matches` present or not), since the report never gates; (b) `apply --shape-report` repeated like `--policy`: an option that can only reproduce what the preview already says | (a) |

## Tests

New file `tests/test_evolve_shape_matches.py`. Fixture: MG2's
`tests/fixtures/evolve-policy/base.orm.yaml` plus proposals built in the test
(object types `customer`, `order`, `channel`, `amount`, and a subtype added
in-test where needed).

| # | Case | Expected |
|---|---|---|
| T1 | `role_player_signature`: role order swapped (equal); (A,A,B) vs (A,B,B) (differ); subtype vs supertype (differ); two value types, same primitive (differ); hostile mapping with non-string values (no exception) | as stated |
| T1b | Two identical fact-type ADDs in one proposal | each lists the other with `origin: added` |
| T2 | A fact-type ADD shaped like `customer_places_order` (roles reordered) | one entry; the match carries id and reading; `references` lists `customer` and `order` as `direct` with their value types; `channel` (a value type) absent |
| T2b | An ADD over a subtype of `customer` | no match against `customer_places_order` |
| T2c | An ADD with no match | entry with `matches: []` (D2) |
| T2d | An ADD plus a DELETE of the fact type it mirrors | the deleted one still matches (D3) |
| T3 | Stable order: entries by operation index; matches by (origin, id); run twice | byte-identical previews |
| T3b | Without `--shape-report` | no `shape_matches` key |
| T4 | MG-R4: one proposal with and without the option, with and without `--policy additive` (admitted and refused proposals) | exit, `breaking`, `blast_radius` (whole), `report_sha256`, `affected_references`, policy fields equal |
| T4b | Source order: in `EvolutionService.preview`, `_policy_values` precedes `shape_matches` | asserted by the order of calls on a spy |
| T5 | CLI: `--shape-report` preview applies (0); with `--policy additive` too (0, MG2-Q1); `shape_matches` edited and digest recomputed (11, the fresh/reviewed equality); `shape_matches` stripped and digest recomputed (0: apply then rebuilds without the report, which never gates, MG-R4) | as stated |
| T5b | A breaking proposal under `--shape-report`: apply with the accepted digest | 0 (the acceptance rebuild passes `shape_report`) |
| T6 | Before/after `(r1-R)`: MG2's `capture_parity.py` over the eight evolve fixtures, without the option, at `9b069e2` and after; `evidence/MG3/parity-{before,after}.json` | byte-identical |
| T7 | 5,000 generated fact types, a proposal adding 500, through `shape_matches` with a counting `bucket_factory` | probes ≤ 5,500; under 5 s |
| T8 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0; `gnd.evolve.shapes` in the map; no query successor needed |
| T9 | Disclosure: a fixture sample value (`web`) and a value-constraint literal never appear in `shape_matches`; `tests/test_disclosure_mode.py`, `test_disclosure_docs.py` | exit 0, no table change |
| T10 | Anonymity scan over files added or changed since `9b069e2` | 0 matches |
| T11 | `uv run python tools/run_tutorials.py`, `uv run --group docs zensical build --strict`, `uv run python tools/check_docs.py site`, skill prose pins | exit 0 |
| T12 | RF1 goldens: capture under the available interpreters, merge, update `MANIFEST_SHA256`; `tests/test_rf1_cli_pins.py` | exit 0; diff confined to `gnd_evolve_preview` help, `tree.json` and the manifest |
| T13 | Mutation controls, run once and recorded: (i) signature ignores multiplicity (set instead of sorted list) kills T1; (ii) supertype closure added to the signature kills T2b; (iii) apply drops `shape_report` kills T5; (iv) report changes `breaking` kills T4 | each mutant fails its case |

Every branch: equal and unequal signature (T1); existing and added origin
(T2, T1b); entity and value role player in `references` (T2); with and
without the option (T3b, T4); apply with and without the field, tampered and
not (T5).

### Verification selection

| Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|
| Plan §9 MG3 row | run | the MG2 front-matter gate plus `tests/test_evolve_shape_matches.py`, exit 0 | evolve package, `refscheme.py`, RF1 goldens |
| Impact closure | run | plus `tests/test_extract_refscheme*.py` if present and the tests importing `gnd.refscheme`, `tests/test_il6_skill_census.py` after the commit | same |
| Docs | run | T11, exit 0 | docs, skill text |
| Parity | run | T6 | evolve fixtures |
| Broad lanes | cadence | `uv run pytest -q -m "evidence or census"` on explicit owner request | — |

## Out of scope for this phase

Semantic duplicates (synonym readings), supertype matching, refusing on a
match, reference modes that differ but convert, a shape report on `apply`'s
own output, and MG4's use of the helper.

## Size

About 170 source lines (plan: 110) and 350 test lines (plan: 300); the
excess is the closed preview models and the apply wiring.

## Approval instrument

This prose (D1 (b)). No spec review panel.

## Open questions raised at spec time

None beyond D1..D6.

## Implementation findings

Recorded as found, 2026-11-04. The approved text above is not edited.

- **F1, a test expectation, not a design change.** The spec sorts matches by
  `(origin, fact_type)` as spelled, so `added` sorts before `existing`; the
  first draft of T3 assumed the reverse. The test was corrected to the spec.
- **F2, RF1 recapture drift (plan O23, NM2-Q3).** A fresh capture under
  py311, py313 and py314 differs from the committed goldens in about 60
  files unrelated to MG3 (helpers, sessions, `gnd check`'s compiled
  successor, which `test_cli_tree` inserts itself). Only the six
  `gnd evolve preview` help and exit-probe goldens and the one `tree.json`
  hunk were taken; `tree.json` was regenerated from the live parser with the
  compiled successor removed, and `goldens.sha256` recomputed for those
  seven files. `MANIFEST_SHA256` is
  `983d509747363cd901433a6305cae93b8973eec08431e538d9fc032530ed76cb`.
- **F3, RF6.** No counted read was added (364 of 365). The dynamic syntax
  census gained 31 annotation and keyed-lookup rows, recorded in
  `evidence/MG3/dynamic-query-successor.json` and chained after MG2's.

## Review dispositions

One reviewer is one reviewer:
[phase-MG3-claude-review.md](phase-MG3-claude-review.md), verdict
approve-with-fixes. Every finding was reproduced by the reviewer's probes
(retained in `evidence/MG3/review-probes/`).

- **R-F1, blocking, fixed.** Output was quadratic in a shape bucket: with
  400 existing and 200 added fact types of one shape the preview was
  22.7 MB, over the 10 MiB read cap, and `apply` exited 74, so the advice
  changed an exit (MG-R4). **Amendment r2 `(d2)`**, below, replaces "one
  entry per ADD with its matches" by one group per signature. Regressions:
  `test_t7_a_single_bucket_stays_linear` (5,000 plus 500 in one bucket) and
  `test_t7_a_large_group_previews_and_applies_under_the_read_cap` (the
  reviewer's CLI repro, now exit 0 and under twice the plain preview's
  size); mutant M9 (one group per added member) is killed.
- **R-F2, hardening, fixed.** An ADD later deleted produced a signature-`[]`
  entry with reading `"None"`. Only ADD ids the candidate holds are reported;
  `test_review_f2_...`.
- **R-F3, hardening, fixed.** An existing fact type the proposal MODIFYs is
  now judged in its candidate shape; `test_review_f3_...`, mutant M7.
- **R-F4, doc contradiction, fixed in code.** The retry branch's review
  identity now excludes `shape_matches`; `test_review_f4_...`, mutant M8.
- **R-F5, doc contradiction, fixed.** An id deleted and re-added keeps its
  current shape as an existing member; `test_review_f5_...`.
- **R-F6, hardening, fixed.** The reader checks group order, one group per
  signature, that each `operation_index` adds the named fact type, member
  and reference order, and `value_type` exactly for `direct`; T3d now holds
  twelve hostile edits, mutant M10. Signatures are not recomputed by the
  reader; apply rebuilds them.
- **R-F7, completeness, fixed.** `test_t2_composite_and_unmatchable_references`
  exercises both non-direct branches; the source-grep test was dropped.
- **Outside MG3:** a proposal holding only ADD and DELETE pairs fails in
  `BlastRadiusReport` with a pydantic `too_short` error, with or without the
  option (MG3-Q2).

## Amendment r2 `(d2)`

**Delegated approval (auto=true)**, 2026-11-04, same authorization as
`(d1)`; an agent ruling, not the owner's reading. It amends Design
(`models.py`, `shapes.py`), D2 and D3, retaining `(d1)` for everything else:

- `shape_matches` is a tuple of `ShapeGroup {signature, references, added:
  [ShapeAdded {operation_index, fact_type, reading, inverse_reading}] (≥ 1),
  existing: [ShapeMember {fact_type, reading, inverse_reading}]}`, ordered by
  the first added member's operation index. `ShapeMatch` and
  `ShapeMatchEntry` are withdrawn before any release.
- D2 holds in the new form: an added fact type with no candidate is a group
  with one added member and no existing one.
- D3 is refined per R-F3 and R-F5 as the contract states.

Invalidated claims: the r1 field layout and the r1 RF6 successor (both
replaced before commit). Rechecks: the whole of T1–T13, the parity table,
RF6 and the mutants, rerun on the r2 bytes. The text claim prints one
`shape-group:` line per group.

## Open questions raised at implementation

| ID | Question | Target |
|---|---|---|
| MG3-Q1 | RF1 fresh capture drifts in about 60 unrelated goldens (O23, NM2-Q3 still open) | milestone close |
| MG3-Q2 | A proposal of only ADD/DELETE pairs fails `BlastRadiusReport` validation (`too_short`), independent of MG3 | milestone close, then a named follow-up |
