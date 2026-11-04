# Phase MG4: extraction guidelines

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.** Implementation
follows this approval and the MG3 record.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's "process-milestone model-growth-guardrails auto" in this session.
This is an agent ruling under that delegation, not the owner's personal
reading. Approved bytes: SHA-256
`d0a753ffaef6fca199dbae58c4f1ee0667a51647de3c963d6bb667a1f2849c8e` (before
this tag), after the implementability sweep: the three consumers' CLI
options exist (`gnd verify --artifacts`, `gnd fidelity --artifacts`, `gnd
doccheck --artifacts`), and `ModelIndex.primitive(variant="truthy")` equals
`resolve_primitive` on all 179 loadable corpus models (0 differences, D4).
Rulings: D1 (b) prose, no spec review panel; D2 (a), D3 (a), D4 (a), D5 as
stated. Budget: about 130 source and 300 test lines; no paid calls.
Compatibility: bundles without `--guidelines` unchanged (MG-R1), no exit or
version change. Diff review instrument: one local reviewer agent.

## Provenance

- Plan: [model-growth-guardrails-plan.md](model-growth-guardrails-plan.md) r3,
  approved `(a1)` 2026-11-03: §2.4, §3 (homes), §4 MG4, §9 MG4 row, §10
  MG-D6, MG-D11, MG-D14, MG-D18.
- Source: [issue #78](https://github.com/vasiloglou/gnd-public/issues/78)
  (GR-T15).
- Inspection baseline: `9b069e2`; MG3 lands first on the same branch and
  supplies `gnd.refscheme.role_player_signature` (plan §3: "MG4 uses MG3's
  signature helper").
- Prior records: [002-phase-MG1.md](../002-phase-MG1.md),
  [003-phase-MG2.md](../003-phase-MG2.md) and the MG3 record. None leaves an
  open question on the extract lane.
- Authority: the owner's `process-milestone model-growth-guardrails auto`
  (2026-11-04). **This spec's bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #78, plan O10 | Optional guideline artifact: readings, descriptions, reference mode; value constraints per MG-D6 | `render_guidelines`; T1, T2 |
| #78, plan O11 | No constraint that would push an extractor to hide violating facts | MG-D6 (a); T3 injection |
| #78, plan O12 | Guideline digest-bound in `artifacts.json` (recorded, not verified, `(p1)` S) | T1 |
| Plan O20 (IK1 boundary) | A description can restate a constraint; undocumented | MG4-C3 docs; T9 |
| Plan O21 (IK1-Q4) | A description or reading can forge a role line | Escaping; T4 |
| Plan §4 MG4-C1 | `--guidelines` writes the artifact and records its digest; without the flag a recorded before/after table over every extract fixture shows identical bundles; each `_artifact_index_issue` consumer runs on a bundle with the extra file | T1, T5, T6 |
| Plan §4 MG4-C2 | `test_vocabulary_is_constraint_blind` passes; an injection test adds one constraint of every kind, value constraints included, and the guideline bytes do not change | T3 |
| Plan §4 MG4-C3 | Docs state that a description can restate a constraint and that the guideline repeats descriptions | T9 |
| Plan §4 MG4-C4 | A description holding a newline followed by a heading-shaped line is escaped; the structure test finds exactly one section per fact type | T4 |
| Plan §9 MG4 row | "Artifact and digest; flag-off parity; injection; structure"; the gate command | Verification selection |
| Plan MG-R1 | Bundles without the flag byte-identical | T5 table |
| Plan MG-R2 | One guideline generator; the signature helper shared with MG3 | `gnd.extract.guidelines.render_guidelines`; T2b uses `role_player_signature` |
| Plan MG-R3 | Not applicable: the guideline gates nothing and no consumer reads it (`(p1)` S) |
| Plan MG-R4 | Advice never gates: the guideline changes no exit of `extract`, `verify`, `fidelity` or `doccheck` | T6 |
| Plan MG-R5 | Disclosure: `gnd extract` already has its leaf row; guideline text is model content (`value-free`); no sample row or value-constraint literal appears | T7 |
| Plan MG-R6 | Layering and query policy: `gnd.extract.guidelines` in lane `extract`; model reads through `ModelIndex` (`iter_fact_types_shared`, `role_object_types`, `object_type`, `primitive`); zero new counted reads | T8 |
| Plan MG-R7 | Anonymity | T10 |
| Plan MG-R8 | The guideline never presents a constraint as fact | T3; header sentence |
| Plan §10 MG-D6 | Value constraints omitted | Accepted `(a1)`; confirmed MG-D18 |
| Plan §10 MG-D11 | Codegen does not mirror the guideline | T5b: codegen bundle unchanged |
| Plan §5 | `gnd-extract/SKILL.md:41,63` names the optional fourth file; RF1 goldens for `gnd extract`; Unreleased note | Docs; T11 |
| Plan §6 | Constraint bias; description forgery; RF1 drift; names leak | T3; T4; T11; T10 |
| Plan §7 | Verifying the guideline digest in a consumer; value constraints | Out of scope |

## Standing rules bound to this phase

1. **Totality:** `render_guidelines` runs only on a model `load_model`
   accepted; every model string passes through `neutralize_text` (descriptions,
   readings, names) so no input raises or forges a line. T4 feeds control
   characters, U+2028, a heading-shaped description and a backtick.
2. **Input cap bounds the algorithm:** one pass over fact types and their
   roles, one signature bucket index; T12 renders 5,000 fact types under 5 s
   with one `ModelIndex` construction.
3. **Validation order:** the guideline is rendered after the model is loaded
   and projected; a model `extract` refuses today is refused identically with
   the flag (T6b).
4. **One walk:** one generator over all fact types; no per-kind section
   builders.
5. **One home:** the guideline layout is normative in
   `gnd-extract/references/extraction-contract.md` (new "Guideline file"
   section); SKILL.md and the docs page cite it. Reference identity comes
   from `gnd.refscheme.entity_reference`, primitives from `ModelIndex.primitive`
   with the `truthy` variant `render_verbalization` uses (`resolve_primitive`).
6. **Measurement over argument:** T5 is a recorded digest table.

## Goal

`gnd extract MODEL --out DIR --guidelines` exits 0 and writes the four
existing files plus `<stem>.guidelines.md`, recording its SHA-256 under
`artifacts` in `<stem>.artifacts.json`. Without `--guidelines` every bundle
over every corpus model is byte-identical to `9b069e2`, and exits are equal.
The guideline bytes do not change when any constraint of any kind is added to
the model.

## Design

### `src/gnd/extract/guidelines.py` (new, about 110 lines; lane `extract`, layer `lanes`)

```python
GUIDELINES_SUFFIX: Final = ".guidelines.md"

def render_guidelines(model: Model) -> str
```

Layout (normative home: the extraction contract):

```
# Extraction guidelines

Derived mechanically from the ORM model by `gnd extract --guidelines`.
Constraint-blind: readings, role players, object-type descriptions,
reference modes and primitives only. A description is the modeller's prose
and can restate a rule; it is guidance about meaning, never a rule to enforce.

## Fact type `<id>`

- Reading: '<reading>'
- Inverse reading: '<inverse_reading>'          (only when declared)
- Same role players as: `<id>`, `<id>`          (only when another fact type shares the signature)

### Role `<role_name>`

- Object type: '<name>' (`<id>`), <kind>
- Description: '<summary>'                       (each present core key, DESCRIPTION_LABELS order)
- Identified by: <identity sentence>             (entities)
- Primitive: <primitive>                         (when resolvable)
```

Fact types follow the model's order; roles follow each fact type's role
order (`ModelIndex.role_object_types` preserves it). Identity sentences, one
per `entity_reference` kind: `direct`: "the value of `<value_type>`";
`composite`: "a combination of roles (composite reference)"; `unmatchable`:
"no printable reference value". A value type prints no "Identified by" line.
Every model string is rendered through `neutralize_text` inside single
quotes; ids and role names through `neutralize_text` inside backticks, with a
backtick escaped as `\x60`. A heading can therefore only come from the
generator.

### `src/gnd/extract/service.py` (about +10 lines)

`_cmd_extract(model_path, out_dir, *, guidelines: bool = False)`. When true,
`artifacts[f"{stem}.guidelines.md"] = render_guidelines(model)`, inserted
after the applicable set, so the digest index and the staged, index-last
write treat it like the other three. Nothing else changes.

### `src/gnd/commands/extract.py` (about +8 lines)

`--guidelines` (store-true), help naming the file; the description mentions
the optional fifth file.

### Docs (about 50 lines)

`gnd-extract/references/extraction-contract.md` "Guideline file" (normative
layout, O20 sentence); `gnd-extract/SKILL.md` security rule 4 READ list and
the bundle table name the optional file; `docs/reference/cli.md` row; an
Unreleased note; the O20 sentence on the extraction page if one exists.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Approval instrument | (a) corpus-first; (b) this prose: the layout above is the narrated outcome, and the cases mutate one fixture | (b) |
| D2 | What external uniqueness does to the guideline | An external uniqueness that anchors on an entity **is** its composite reference scheme, so adding one changes "Identified by" from "no printable reference value" to "composite". (a) treat it as reference content, as `render_verbalization` does, and exclude anchoring external uniqueness from T3's injection (it injects a non-anchoring one); (b) never print composite identity: loses #78's "reference mode" for composite entities | (a) |
| D3 | "Same role players as" line | (a) include it, from `role_player_signature`: model content that helps an extractor tell same-shaped fact types apart, and the plan's shared-helper premise; (b) omit: the helper is then shared with MG3 only | (a) |
| D4 | Primitive source | (a) `ModelIndex.primitive(id, variant="truthy")`, equal to `resolve_primitive` (T2c asserts equality on the corpus); (b) `resolve_primitive` directly: a model read outside `ModelIndex` | (a) |
| D5 | Codegen bundle (MG-D11) | Accepted at the plan gate: codegen does not emit the guideline | as stated |

## Tests

New file `tests/test_extract_guidelines.py`. Fixture: `tests/fixtures/models/full_vocabulary.orm.yaml`
(the constraint-blindness fixture) and MG2's `evolve-policy/base.orm.yaml`.

| # | Case | Expected |
|---|---|---|
| T1 | `gnd extract MODEL --out DIR --guidelines` | 0; five files; `artifacts.json` records `<stem>.guidelines.md` with the file's SHA-256 |
| T2 | Content on `evolve-policy/base.orm.yaml`: `customer_places_order` section has its reading, three role sections, `customer` with its description summary and "the value of `customer_id`", Integer primitive; `channel` a value type with String and no "Identified by" | as stated |
| T2b | Same role players: a model with two fact types over (order, amount) lists each in the other's section; a fact type with a unique signature prints no such line | as stated |
| T2c | `ModelIndex.primitive(..., variant="truthy")` equals `resolve_primitive` for every object type of every corpus model | equal |
| T2d | Identity kinds: a composite entity (`full_vocabulary` external uniqueness, or a fixture built in-test) and an unmatchable one | each sentence once |
| T3 | Injection: one constraint of every family in `FAMILIES` (value constraints included; uniqueness internal; external uniqueness non-anchoring) added to `full_vocabulary` | guideline bytes unchanged; `test_vocabulary_is_constraint_blind` passes |
| T3b | Mutation control: a mutant that prints the value constraints' `allowed` | T3 fails |
| T4 | Forgery: a description `summary` of `"x\n## Fact type `evil`"`, a reading with U+2028, a role name with a backtick | escaped; the structure parse finds exactly one `## Fact type` heading per fact type and one `### Role` per role |
| T5 | Before/after `(r1-R)`: `gnd extract` without the flag over every `*.orm.yaml` under `tests/fixtures` and `examples` at `9b069e2` and after; `evidence/MG4/parity-{before,after}.json` (exit and SHA-256 of each bundle file) | byte-identical |
| T5b | `gnd codegen` bundle digests for the codegen fixtures unchanged (MG-D11); `tests/test_public_legacy_codegen_pins.py`, `tests/test_fidelity_stub_gate.py` | exit 0 |
| T6 | Each `_artifact_index_issue` consumer on a `--guidelines` bundle: `gnd verify` with `--artifacts` (export/verification_service), `gnd fidelity` and `gnd doccheck` | same exit as on the four-file bundle |
| T6b | An invalid model with `--guidelines` | 3, no file written, same stdout as without |
| T7 | Disclosure: a sample value and a value-constraint literal never appear; `tests/test_disclosure_mode.py`, `test_disclosure_docs.py` | exit 0 |
| T8 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py` | exit 0; `gnd.extract.guidelines` mapped; no counted read added |
| T9 | Docs: the contract's "Guideline file" section contains the O20 sentence; `tools/run_tutorials.py`, `zensical build --strict`, `tools/check_docs.py site`, skill prose pins | exit 0 |
| T10 | Anonymity scan over added and changed files | 0 matches |
| T11 | RF1 goldens for `gnd extract` help recaptured and merged; `MANIFEST_SHA256`; `tests/test_rf1_cli_pins.py` | exit 0 |
| T12 | 5,000 fact types | under 5 s; one `ModelIndex` construction |

### Verification selection

| Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|
| Plan §9 MG4 row | run | `uv run pytest -q tests/test_extract_guidelines.py tests/test_extract_applicable.py tests/test_extract_cli.py tests/test_extract_manifest.py tests/test_extract_projection.py tests/test_extract_vocabulary.py tests/test_public_extract_boundary.py tests/test_public_extract_controls.py tests/test_public_extraction_prose_policy.py tests/test_v51_phase2_extraction_controls.py tests/test_v51_phase2_extraction_scope.py tests/test_fidelity_stub_gate.py tests/test_public_legacy_codegen_pins.py tests/test_rf1_cli_pins.py tests/test_disclosure_mode.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_gnd_arch.py`, exit 0 | extract lane, `refscheme.py`, RF1 goldens | any change |
| Impact closure | run | plus `tests/test_rf1_pin_harness.py tests/test_disclosure_docs.py tests/test_skill_prose_sync.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_rf3_core.py tests/test_rf4_peripheral.py`, and the MG3 gate (shared helper) | same |
| Docs | run | T9 | docs, skill text |
| Parity | run | T5 | corpus models |
| Broad lanes | cadence | on explicit owner request | — |

## Out of scope for this phase

Value constraints in the guideline (MG-D6, MG-D18); a consumer that verifies
the guideline digest (`(p1)` S); codegen mirroring (MG-D11); localized or
templated guideline text.

## Size

About 130 source lines (plan: 160) and 300 test lines (plan: 350).

## Approval instrument

This prose (D1 (b)). No spec review panel.

## Implementation findings

Recorded as found, 2026-11-04. The approved text above is not edited.

- **F1, a fixture without the discriminating case.** Mutant M1 (print each
  fact type's inline value constraint) first survived T3: none of the three
  family fixtures hosts an inline value constraint. MG2's base fixture,
  which does, joined T3's parameters; M1 is now killed.
- **F2, RF1.** The `gnd extract` help and exit-probe goldens are single files
  (interpreter-independent); captured under py311, py313 and py314, byte-equal,
  installed; `tree.json` regenerated from the live parser; `MANIFEST_SHA256`
  `c72e5fb7d9b286377ca803e68f4581e2dc7dd3545842278c16733b120b62125f`.
  `uv run --python X` rebuilds the shared `.venv`; it was left on 3.14.3, as
  before.
- **F3, RF6.** No counted read (364 of 365); the dynamic census successor is
  `evidence/MG4/dynamic-query-successor.json`.

## Review dispositions

One reviewer is one reviewer:
[phase-MG4-claude-review.md](phase-MG4-claude-review.md), verdict
approve-with-fixes, nothing blocking; probes retained in
`evidence/MG4/review-probes/`.

- **R-F1, hardening, fixed in docs.** A flag-free re-extract leaves an older
  guideline unlisted. The contract, SKILL.md rule 4 and the bundle table now
  say to read it only when the index lists it with a matching digest.
  Deleting the stale file would add a filesystem effect to the flag-free
  path (MG-R1); not done.
- **R-F2, completeness, fixed.** A non-anchoring external uniqueness is
  injected (`test_t3_an_external_uniqueness_...`); mutant M8 killed.
- **R-F3, completeness, fixed.** T6 now runs `gnd fidelity`, `gnd doccheck`
  and `gnd verify` on the roundtrip `faithful` case over both bundles.
- **R-F4, docs, fixed.** "any other constraint"; the anchoring exception
  changes only `- Identified by:`.
- **R-F5, hardening, documented.** Raw HTML in a description is not escaped;
  the contract and module docstring state the file is plain text, not to be
  rendered. Escaping would change description text (MG4-Q1).
- **R-F6, hardening, fixed.** `entity_reference` is memoized per render;
  `test_t12_entities_resolve_their_reference_once`, mutant M7. The shared
  `reference_identity` cost on models with many external uniqueness
  constraints remains, and the flag-free verbalization already pays it
  (MG4-Q2).
- **R-F7, completeness, fixed.** T3b asserts sample values stay out; mutant M9.
- **R-F8, nit, fixed.** T4 rewritten: no unreachable branch, no bare except,
  the separator built with `chr(0x2028)`.
- **R-F9, doc nits, fixed.** "as written, escaped onto one line"; the index
  row counts the guideline; the layout no longer nests backticks.

## Open questions raised at implementation

| ID | Question | Target |
|---|---|---|
| MG4-Q1 | Escape raw HTML in guideline descriptions, or keep "plain text, not rendered" | milestone close |
| MG4-Q2 | `reference_identity` scales with entities × external uniqueness constraints for extract as a whole | milestone close |
