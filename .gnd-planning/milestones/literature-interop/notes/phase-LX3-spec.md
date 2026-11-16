# LX3 · fixed catalogs in composition

Status: delegated approval (auto=true), 2026-11-15. See [008](../008-phase-LX3-spec-gate.md).

## Provenance

The [r4 milestone plan](literature-interop-plan.md) and its
[plan gate](../003-plan-gate.md) assign LX3 the catalog and composed fact
provenance work. LX1 establishes resolver-bound model origins. The [LX2 result](../007-phase-LX2.md) supplies
the rooted witness origin axis and repaired path compatibility. The [LI2 result](../../literature-identity/010-phase-LI2.md)
supplies the existing cross-source resolution contract.

## Obligations

| Source | Obligation | Evidence |
|---|---|---|
| LX3.a | Compose two sources with a declared catalog, including a rename onto a materialized catalog key. Keep catalog rows outside candidate output and lineage. Discriminate catalog-aware check from candidate-only check. | T1–T3 |
| LX3.b | Refuse conflicting and candidate-dependent catalog inputs. Bind catalog and candidate evidence independently in the routes that consume them. Preserve LI2 and override refusal. | T4–T7 |
| LX3.c | Replay a proof containing both origin kinds with independent model, fact and catalog controls. | T8 |
| Plan §§0, 2 and 5 | Reuse bounded reference, source and identity implementations, give the new record one contract home. | Design, T9 |
| Plan §9 | Direct and affected check, composition, reference, witness and resolution gates. | Verification ledger |

## Rules

- **Totality.** The composition record reader bounds the whole read and
  validates the closed catalog roster. Hostile schema, recursion,
  non-finite and wrong-type controls distinguish malformed from stale.
- **Input-bounded work.** Compare existing catalog snapshots in their
  canonical ID order. Use one combined population build per composed
  check and one row provenance lookup per proof occurrence.
- **Validation order.** Pin reference input binding before candidate
  source admission. A syntactically valid composition record must match
  its model, candidate population and catalog snapshot before support is
  examined. The spec corpus has two-defect controls.
- **One policy walk.** The bound context owns catalog populations,
  declarations and row identity. Source merge and resolution continue
  to consume candidate rows only.
- **One home.** The composition reference owns its catalog roster and
  input ordering. The witness contract owns the mixed proof envelope.
- **Measure representation.** An existing rooted dispatch fixture
  with a subset from candidate warehouse to catalog warehouse passed
  with its pinned catalog and failed on the same candidate without it.
  A rooted standalone proof over the same reference vocabulary
  independently produced, referenced and replayed both fact origin
  kinds. Turn these probes into an actual composition corpus.

## Goal

`gnd compose ROOT SOURCES --out POP --record RECORD` exits 0 with two
candidate sources and a fixed catalog. `gnd check ROOT POP --composition
RECORD --sources SOURCES` evaluates those candidates with the bound
catalog. A witness and replay over the same rooted record exit 0. Stale
catalog evidence and forged fact provenance are separately observable.

## Design

| Capability | Existing home | Proposed reuse |
|---|---|---|
| Resolve catalog ownership and digests | `model.loading`, `model.reference_binding` | Use retained-root model and reference binder plus its bound snapshot. |
| Combine and evaluate facts | `model.reference_binding`, `check.service`, `checker.evaluate` | Bind once after exact composition verification and let the existing checker evaluate the combined view. |
| Derive candidate facts and resolution | `model.composition`, `model.anchors` | Preserve source admission, rename and LI2 checks. Catalogs are a separate named input with an exact digested roster. |
| Name proof origins | `witness.service`, `witness.replay`, `witness.schema` | Reuse LX2's exact model origins and the existing candidate/reference occurrence shape. Composition adds candidate source coordinates only. |

### Coordinate and boundary decisions

The authored root owns the declaration and path of each reference file.
The candidate source directories remain the sole source of renamed and
deduplicated rows and the source spans that attest them. Keep the catalog
fixed when a manifest explicitly renames a candidate alias onto an
admitted catalog value. Existing LI2 resolution evidence still governs
candidate cross-source joins.

Use the reference binder's independent structural validation and unique
declared ownership before candidate admission. Before the manifest, reject duplicate values of confirmed alethic internal
uniqueness keys among distinct rows of a catalog fact type. A confirmed
alethic subset with populated reference-owned left relations cannot require
a candidate-owned relation on the right. The corpus authors a reverse
membership constraint to test this dependency. The forward membership
constraint remains part of the later combined check. The binder also
retains its structural, ownership and declared-digest checks.

The proposed reference-bearing composition record uses
`"schema": "gnd-composition/2"` and requires a nonempty, lexically sorted
`references` roster of `{"id":"catalog","raw_sha256":"<sha256>"}`.
The reference-free record keeps exactly version 1 and its current
resolution variant. Verify record roster equality with the resolver's
current bound catalog snapshot. Sources and facts remain candidate only.
Both check and composition writers retain existing source/model output
collision policy and extend its input exemptions to pinned catalogs.

The composed check reconstructs the exact candidate first, then combines
it once with the verified catalog for rule evaluation. Source anchor
verification still observes antecedent spellings before renaming. A
catalog-owned row has independent reference provenance and cannot acquire
a candidate source span. Explicit caller-supplied anchor or reference
overrides retain their existing refusal when composition supplies its
own context.

Proposed witness v4 is catalog-backed composition. It requires a
composition digest and nonempty exact reference bindings. It carries
flattening and model origins whenever the root declares includes, using
LX2 fields. Candidate base nodes have nonempty `sources`. Reference base
nodes have empty `sources` and retain their reference ID and index.
Verify each against the appropriate population and binding before accepting
inference. Include-free catalogs can use the same mixed proof envelope.
Unchanged v1–v3 routes preserve their own fields and bytes.

## Decisions

| ID | Decision | Ruling |
|---|---|---|
| D1 | Version 2 composition records for the catalog roster, preserving reference-free bytes. | Delegated (auto=true) |
| D2 | Catalog-backed composition certificate v4 with independent model and fact origin fields. | Delegated (auto=true) |
| D3 | Check evaluates the verified candidate in the model's authenticated catalog context. Preserve override guards. | Delegated (auto=true) |
| D4 | Use pinned dispatch vocabulary and two source documents for the core corpus. Prove key ownership, row validity, and catalog-aware rule evaluation separately. | Delegated (auto=true) |

## Test ledger

- T1 authentic two-source compose with a manifest renaming an alias to the
  catalog warehouse. Output rows and record lineage contain candidate
  occurrences only. Reference-free artifact bytes match a captured control.
- T2 composed check exits 0 and the pinned subset verdict passes. Removing
  catalog rows from the test comparison produces a failing subset.
- T3 source anchor attribution uses candidate source spelling and indices.
  Catalog occurrences have reference origins.
- T4 an internal uniqueness conflict, a directed candidate dependency, and a stale pin
  each exit 3 before candidate input even if a source is malformed too.
- T5 independent catalog, source and record mutations, including a forged
  record roster with valid model pin and unchanged candidate output.
- T6 existing LI2 tests plus a composed catalog case where an unjustified
  candidate cross-source join still refuses. Catalog IDs cannot be forged
  into candidate lineage.
- T7 preserve named explicit override refusal at the API or CLI boundary.
- T8 mixed candidate/reference proof with included and root model origins,
  then separate model-origin, catalog-binding and two fact-origin swap
  mutations. Replay is independent of production trace.
- T9 closed-schema and size controls, measured at the added roster and
  provenance layer. Include-free v1/v2 and rooted reference-free v3
  controls retain their exact payloads.

## Phase boundary

LX4 owns checking-model rebind, the integrated evidence manifest and the
advisory date report. LX3 establishes the product composition, check and
witness routes they need.

## Approval instrument

Corpus-first. Planned entry `tests/fixtures/lx3-catalog-composition/README.md`
with the expected wire and exits in `expected.json`. The directed subset
and mixed proof were prototyped through rooted check and witness. The
approved source documents and candidate occurrences provide separate
origin coordinates. The legacy artifact pair is captured at LX2 close.

## Refusal precedence and verification

1. Compose binds the model and catalog, validates catalog keys and independence,
   then reads the manifest and preserves the LI2 resolution order. A stale pin
   names its raw-hash mismatch. Check and compose use exit 3 for invalid inputs.
2. Check verifies the catalog roster, candidate bytes and original sources,
   then checks rules over one bound candidate-plus-reference view. It presents
   the fixed input roster through the current reference result wrapper.
3. Replay reads certificate shape first, resolves includes and catalog, then
   compares the supplied record's model, candidate and catalog binding. Both
   witness consumers use exit 3 `binding-stale` on changed catalog inputs or
   a valid-shaped stale catalog roster. Structurally valid false provenance
   returns exit 1 `proof-invalid`. Check retains exit 3 and names the mismatch.
   Witness uses the given record. Check re-derives that record from the source
   directory. The existing witness contract has no sources-directory input.

| Gate | Command |
|---|---|
| Direct and affected routes | `uv run pytest -q tests/test_lx3_catalog_composition.py tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_li2_resolution.py tests/test_reference_population_corpus.py tests/test_lx2_witness_flattening.py tests/test_mc2_consumers.py tests/test_public_semantic_composition.py --tb=short` |
| Structure | `uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short` |
| Lint and components | Whole-tree Ruff, changed-file Ruff and `python3 scripts/components_index.py changed --base 6d2ecece --strict`. Compare known full lint diagnostics using the LX2 baseline. |
| Cadence | Default marker filters. Full and historical lanes follow their separate triggers. |

## Candidate verification

The focused gate added the byte-identical schema-copy controls. The
catalog-bound subset passes on the same candidate whose subset fails
without the catalog. The accepting fixture supplies both claimed derived
rows so the checker can verify their extension as well as the subset.
The instrumented check observed one combined-population bind. The
positive reference report validates against the current report schema.

The refused explicit-anchor combination retains CLI usage exit 64. The
explicit API reference override raises the existing ValueError. The old
MC2 catalog-refusal control now proves that the accepted model still
needs a valid source manifest. The unbound model-copy control continues
to refuse. The LX3 catalog authority does not change LI2's candidate
resolution decisions.

```sh
uv run pytest -q tests/test_lx3_catalog_composition.py tests/test_composition.py tests/test_composition_example.py tests/test_witness_composition.py tests/test_li2_resolution.py tests/test_reference_population_corpus.py tests/test_lx2_witness_flattening.py tests/test_mc2_consumers.py tests/test_public_semantic_composition.py tests/test_schema_sync.py --tb=short
uv run pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short
```

    744 passed, 3 deselected in 155.35s (0:02:35)
    679 passed, 2 deselected in 150.43s (0:02:30)

Scoped Ruff passes. Whole-tree Ruff exits 1 with exact equality against the
188 inherited diagnostics by file, line, code and message. The strict
component gate exits 0. The RF6 literal model-query inventory is unchanged.
The successor counts the moved composition walk and new dynamic
lookups. Schema validation checks structural conditions. The reader also
verifies strictly sorted reference IDs and candidate source membership.

The affected replay-admission and architecture extension of the focused gate
ran with host process inspection for the admission harness.

    uv run pytest -q tests/test_public_replay_admission.py tests/test_gnd_arch.py --tb=short
    54 passed in 7.90s

Independent diff review is pending.
