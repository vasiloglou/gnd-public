# Phase OS3 — Import Ossie ontologies

## 1. Status

Ready for delegated spec approval, 2026-11-10. OS1 is closed. OS3 can proceed
independently while OS2's formula diff is reviewed because the sidecar already
retains the original syntax of both core and formula projections.

## 2. Provenance

Plan r3 predicate 5, §§0, 2, 3, 4, 6, 9 and 10. OS0 selects a digest-bound
sidecar and pins the upstream ontology. OS1 establishes the reconstruction
entries and publication order. The [census pointer roster](../evidence/OS3/refused-census-pointers.json)
identifies the eight sources that lose nonempty population subtrees.

## 3. Obligations

| Criterion | Measure |
|---|---|
| OS3-C1 | Hostile YAML, JSON and sidecar tests exercise the capped reader and closed value-free refusal IDs. |
| OS3-C2 | Compound faults distinguish input, schema, name graph, binding, reconstruction and final GND admission order. |
| OS3-C3 | Restore all 38 eligible models. Compare via GND diff after removing exactly the refused population subtrees from the expected source. |
| OS3-C4 | Import the pinned Flights document with traceable imported provenance and explicit loss rows for constructs the projection does not carry. |
| R7–R9 | Use byte-identical pinned schema resources offline, retain every loss disposition and publish through the existing create-once file set. |
| OS1 carryover | Verify sidecar digest before decoding reconstruction entries. Admit a default export loss report only when it binds the same document and agrees with all retained pointers. |

## 4. Standing rules

1. Totality. The input, export-report and sidecar readers cap their reads
   and handle JSON/YAML syntax, duplicates, aliases, nesting, nonfinite or
   unencodable values and structural failure.
2. Work bound. Use indexed concept and pointer maps, a linear topological
   walk and an explicit reference-search budget. Bound reconstructed JSON
   during serialization. Test hostile and scaled cases.
3. Order. Capped bytes, format/JSON value limits, offline vendored schema,
   name graph, sidecar header and document digest, optional report binding,
   pointer restoration, GND admission, output publication.
4. One walk. A foreign projection marks the subtrees it handles, and one
   pointer traversal writes the report. Sidecar entries reconstruct source
   pointers directly, preserving arrays and refused omissions.
5. One home. Representation-format.md defines wire and CLI behavior.
   The vendored ontology's absolute core-schema reference resolves to
   byte-identical data from the same upstream commit.
6. Measure. Use real GND diff on the census. Hostile fixtures pin the
   observed precedence and both directions of the binding decision.

## 5. Goal

Exit 0 for valid GND bundles and supported foreign projections, with a
create-once model and report. Invalid input exits 3 with a value-free rule
ID. An existing output exits 11. No input-controlled network access occurs.

## 6. Design

| Capability | Search and decision |
|---|---|
| Bounded syntax | `bounded YAML JSON parse schema depth limit`; reuse `infra.input_policy`, `infra.safe_filesystem` and the GND model loader. |
| Foreign model admission | `import foreign model artifact provenance role aliases`; reuse the existing GND imported provenance contract. RAI import's dialect transforms are specific to RAI. |
| Sidecar | `digest bound sidecar pointer reconstruction report`; adapt the OS1 wire contract, with no reference to the exporter at runtime. |
| Output | `create once publish group rollback`; reuse `safefs.publish_new_files` with the model as the final marker. |
| External | Use the existing jsonschema/referencing dependencies and ruamel.yaml. Register the pinned core schema only to resolve the ontology schema's existing absolute references. |

`plan_ossie_import(path: Path) -> OssieImportResult` returns canonical JSON
model and report bytes. File content determines the source digest and
portable provenance. Read `FILE.gnd.json` when present. Its closed header
requires `schema`, `model_identity`, `document_sha256` and `elements`.
The exact document hash must match before any entry is interpreted. A
present default `FILE.loss.json` must match the same binding, have unique
valid pointers and agree with retained versus refused entries. Its absence
supports exporters that used a custom report path. The import never
dereferences an artifact path supplied inside a document.

The sidecar decoder indexes canonical RFC 6901 pointers. It refuses
duplicate entries, missing or scalar parents, sparse arrays, invalid
payload shape, excessive depth, and `copy` targets that are not scalars.
Serialization is bounded before GND admission. The original identity is
retained in the output report because a refused reference declaration can
legitimately change the reconstructed model's canonical identity.

Without a sidecar, convert the supported native projection. Allocate safe,
deterministic GND IDs and build object and relation indices from the Ossie
name graph. Map built-in primitives and unambiguous subtype inheritance.
Preserve a first complete verbalization by ordering source roles as read.
Project a direct identifier when a single binary link identifies an entity
by a value type. Composite or otherwise unsupported identifiers, extra
verbalizations, formulas and mapping metadata get refused rows. Retain
stable digest- and pointer-based provenance on foreign objects and facts.
For the exact pinned Flights file, project supported multiplicities as
imported proposed constraints with its verified artifact commit and verbatim
multiplicity token. An unversioned foreign document's multiplicities get
explicit refusals when that provenance is unavailable.

The output report uses `gnd-ossie-import-loss/1` with `schema`,
`document_sha256`, `source_model_identity` (nullable) and
`dispositions`. Foreign pointer rows describe native projection or
refusal. Reconstructed bundles replay available original dispositions.
If the source loss report is absent, their rows cover the retained pointers.

The CLI writes to `--out MODEL` and to `--loss-report FILE` or
`MODEL.loss.json`. Exit 3 prints a stable `ossie-import:<rule>` identifier
without source values. Exit 11 means publication found an existing leaf.
The canonical output model is JSON, including at a YAML-compatible filename.

## 7. Decisions

- D1. Keep both the default export report and sidecar as independently
  validated inputs. The sidecar is sufficient when the exporter used a
  custom report location.
- D2. Give the exact pinned Flights bytes authentic imported multiplicity
  provenance. Arbitrary source provenance records only verifiable facts.
- D3. Separate the phases according to the plan dependency graph. OS3 uses
  the closed OS1 wire contract and does not need a finished OS2 review.

## 8. Tests

Run `tests/test_ossie_import.py`, existing diff tests and the affected CLI
successor characterization. Exercise bound and foreign success, wrong
digest with multiple earlier faults, malformed and dangerous metadata,
collision, work bounds, all exact refused census pointers and authentic
Flights provenance. The ordinary lane consumes the small pinned Flights
fixture locally.

## 9. Out of scope

Formula interpretation on foreign inputs, remote schema resolution and
credentialed tools. The independent OS3 implementation review remains a
separate gate.

## 10. Size

About 500 implementation lines across the reader and foreign projection,
focused tests and small vendored validation data.

## 11. Approval instrument

This spec, the exact refused census pointer list and the OS1 wire evidence.
