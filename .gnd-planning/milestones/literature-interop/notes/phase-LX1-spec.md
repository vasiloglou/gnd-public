# LX1 · digest-bound flattening for extraction

Status: delegated approval (auto=true), 2026-11-15. See [004](../004-phase-LX1-spec-gate.md).

## Provenance

This draft consumes r4 of the [milestone plan](literature-interop-plan.md),
SHA-256 `0b0b8be165233078e7048948eef45266f007165df557fbdd3c629cd106ae5454`,
approved at the [plan gate](../003-plan-gate.md). The first and second panels reviewed r2 and r3.
No review has run on this spec.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| Plan LX1.a, #193 part 5 | Extract over two pinned includes and verify the bundle from the authored root. Provide complete address provenance for anonymous and attached constraints. | Design, T1–T3 |
| Plan LX1.b, §4 chain and §7 | Isolate root, include, flat bytes and record changes. Refuse coordinated flat/record forgery and preserve include admission. | Verification order, T4–T7 |
| Plan LX1.c and LI0 | Match predecessor index and bundle bytes on the include-free route. Preserve LI0 model and witness behavior. | Design, T8 |
| Plan X1 | Prepare the shared wire and verification boundary for LX2. | Wire format, D1 |
| Plan §§0, 5 and 6 | Use one bounded provenance producer, select normative home, pin parser and binding order, and prove re-entry parity. | Standing rules, T2, T6, T9 |
| Plan §9 | Direct tests plus include, extraction and affected verification consumers. Run the project guards. | Verification ledger |
| Plan §7 and MC1 guard inventory | Only enable the supported LX1 path. Keep unrelated consumer refusals and temporal extraction admission. | T7, T10 and Phase boundary |

## Standing rules

- **Totality.** The include-backed bundle validator bounds index, record and
  projected-model reads and rejects duplicate keys, non-finite numbers,
  invalid UTF-8, deep containers, and malformed types. It maps errors at the
  service boundary to a refusal. T9 proves the hostile-input cases.
- **Input-bounded work.** Reuse the resolver's existing root/include limits.
  Build one linear origin map and compare canonical bytes over bounded outputs.
  Time the flattening layer on a predeclared origin-count fixture in T9.
- **Validation order.** The design lists the order per route. T6 pairs defects
  with different diagnostics.
- **One policy walk.** Reuse the resolver's origin walk for all tracked
  element kinds. Compare authored and flattened address targets in T2.
- **One normative home.** Extend the representation-format include section
  with the flat wire, record and binding rules. The user-facing extract guide
  links there.
- **Measure representation.** On the predecessor MC1 component model a
  read-only probe round-tripped the flat wire and retained all eight origin
  entries. Projection, applicability and verbalization matched. T2 repeats
  the equivalence at the new boundary with two include files. T8 pins legacy
  bytes.

## Goal

`gnd extract ROOT --out DIR` exits 0 for the admitted two-include root.
`gnd verify ROOT POPULATION --artifacts DIR --sidecar SIDECAR` accepts its
fresh extraction handoff and exits 3 with the bound coordinate on stale
input. The flat document loads through ordinary model-byte intake, while
the provenance record can be reproduced from the original root and its
pins.

## Design

| Capability | Searches | Reuse decision |
|---|---|---|
| Resolve pinned models and retain origin addresses | `pinned include model origin address`, `compose vocabulary provenance authored model` | Reuse `model.loading`, `model.document` and `model._includes.compose`. Their resolved snapshot already records origin and exact include byte identity. |
| Produce and validate an extraction index | `verify extraction bundle artifact manifest`, `digest index stale projection format` and `rg _artifact_index_issue src/gnd` | Adapt `extract.service` and `extract.bundle`. Reuse naming, header and atomic writing. The codegen manifest owns a different binding and stays separate. |
| Canonical model re-entry and bounded byte reads | `canonical model wire serialization`, `reload flat model JSON` and `rg 'def model_wire\|def canonical_json_bytes' src/gnd` | Reuse LI0's `model_wire` by moving its implementation to the model layer, retaining the witness import as an identity alias. Reuse `infra.artifacts` for canonical bytes and bounded reads. |

### Model projection

Proposed `gnd.model.flattening` owns
`flatten_model(model: Model) -> FlattenedModel`, where `FlattenedModel`
contains `model_bytes: bytes` and `record_bytes: bytes`. It accepts a
resolver-backed model with a root SHA-256 and matching include metadata.
Create the re-entry wire with the shared LI0 serializer, omitting only the
already-resolved `includes` and `fact_type_constraints` fields in addition
to the serializer's existing omissions. Retain root model identity,
operations, version and reference declarations. Resolve any relative
reference paths from the authored root, never the artifact directory.

Pass the projected bytes through the existing model-byte loader. The
flattened document and the loaded authored model agree on every retained
semantic section. Refuse projection that cannot enter the existing model
byte cap. Source hash syntax and canonical encoding follow the existing
artifact primitives. Place the serializer in `gnd.model._documents` and retain
`gnd.witness.io.model_wire` as the same function object. Relocate the LI0
source-scan assertion with the defining function. The updated assertion
requires zero direct model dumps in witness and one serializer at its new
home. The estimate is 110 source lines.

### Wire format

The record has this closed shape, in canonical JSON. Arrays are ordered.
The include list uses authored pin order. Origins sort by composed address.
Each origin uses the resolver's source and address strings verbatim.

```json
{
  "format": "gnd-flattening/1",
  "root_sha256": "<sha256>",
  "includes": [{"id": "vocabulary", "path": "vocabulary.orm.yaml", "sha256": "<sha256>"}],
  "flat_model_sha256": "<sha256>",
  "origins": [{
    "origin": "includes[vocabulary]",
    "original_address": "$.fact_types[0].constraints[0]",
    "composed_address": "$.fact_types[1].constraints[0]",
    "element_id": null
  }]
}
```

A root attachment's origin is `model` and its original address is its
authored attachment address. The flat model's composed address names the
materialized constraint. Omitted semantic fields and extra origin labels
are detectable by re-derivation. The verifier compares exact canonical
record bytes. Treat the stored record as opaque bounded bytes.

### Extraction integration and order

The filename stem is the authored root's normal extract stem. Add
`<stem>.flat.orm.json` and `<stem>.flattening.json` to the existing atomic
bundle publication and artifact index. Use an explicit top-level
`flattening` object in the include-backed index with two fields,
`flat_model` and `record`, naming those respective fixed filenames. The
index's existing `model.sha256` retains its authored-root meaning.
The existing `artifacts` dictionary contains the two new artifact digests.
Keep the 1 MiB index cap and cap each flat or record read at the existing
10 MiB model ceiling. An oversized projection or record exits 3 before
publication. Use bounded path reads for all new binding inputs.

Extract resolves the root with the existing loader before projecting,
applies non-temporal admission before any publication, and binds the
include snapshot captured by model loading. Index validation verifies the
authored root before accepting any output binding. It then re-resolves
the root with pins, compares the resolved root identity to the indexed
identity, and compares fixed artifact paths and bytes to their indexed
digests and the re-derived projection and record. This catches a forged
record and flat model even when the index names both forged digests.
Check root, include, flat model and record in that order. Snapshot classification
comes from the loaded root. An include-bearing root with the flattening marker
or either binding removed refuses. An include-free root cannot opt in by
inserting the marker. Model construction remains bounded and uses retained-root
reads.

Adapt the verifier's extraction handoff to use the verified model snapshot
on the include-backed route. Reading a second model would create a new
unbound input. For legacy bundles, preserve existing paths, output bytes
and normal error precedence. The existing `_artifact_index_issue` alias
keeps its call and result contract for callers that need diagnostics only.
Missing required legacy artifacts keep their current exit band. Missing or
changed include snapshot coordinates in an indexed include-backed bundle
use exit 3. Identify the failing root, flat model or record coordinate
in the diagnostic. An invalid pin preserves the resolver's include ID and
failure code. The verification service keeps its existing
`extraction:binding-mismatch` issue contract for indexed artifacts.

For nested includes, reference declarations in an include, and unattended
included source, keep `include:forbidden-section` and name the forbidden
field or source mode. An invalid standalone model retains the resolver's
`include:invalid-included-model` refusal and a confined-path escape
retains `include:path`. If multiple forbidden sections are present, identify
the first according to the resolver's fixed field order.
Use the same bounded resolver for extract and verify. The estimate is 135
source lines plus docs and component metadata.

## Decisions

| ID | Proposal | Status |
|---|---|---|
| D1 | Place the shared format and producer in the model layer and preserve the LI0 serializer import alias. This keeps LX2 from importing extraction-specific code. | Delegated approval (auto=true), 2026-11-15 |
| D2 | Bind root bytes and compare re-derived flat and record bytes. Validation of mutual equality among stored artifacts alone would accept a coordinated forgery. | Delegated approval (auto=true), 2026-11-15 |
| D3 | Use the existing verify extraction handoff as the LX1 consumer. Keep fidelity and doccheck path enablement for their own phase scope. | Delegated approval (auto=true), 2026-11-15 |
| D4 | Limit flat serialization to the existing model-byte intake ceiling. A larger artifact would pass extract and refuse at the next modeled stage. | Delegated approval (auto=true), 2026-11-15 |

## Tests and verification

| Case | Coverage and expected outcome |
|---|---|
| T1 | `tests/test_lx1_flattening.py`, two-include public CLI extraction and exact sidecar verification both exit 0. |
| T2 | Every recorded composed address resolves in the canonical flat document and corresponds to the authored root or include element. Include one root attachment and one anonymous nested constraint. Re-entry preserves projection, applicability and verbalization. |
| T3 | Two runs over the same paths and inputs yield the same flat and record bytes. Assert their exact index and root bindings. The wire is directly consumable by model-byte intake. |
| T4 | Independently mutate root, one include, flat bytes and record bytes. Verify exits 3 and identifies each failing coordinate. |
| T5 | Write a different valid flat model, a matching record and updated index digests. Verify exits 3 after re-resolving the original unchanged root. Strip the flattening marker and bindings and verify exit 3 again. |
| T6 | Change root bytes and the flat output together. Root binding wins. Keep root unchanged and pair the stale include and bad flat bytes. Include hash refusal wins. |
| T7 | Confined-path escape, standalone-invalid include, nested include, include reference declaration and unattended source each exit 3 at the public extract entry point with the named refusal and no published index. |
| T8 | Compare every artifact of a legacy extraction against the captured phase-base digests. Run the LI0 wire controls with the serializer identity alias, sole source-scan owner and unchanged model identity. |
| T9 | Feed the include-backed index hostile JSON, wrong containers and cap-plus-one input. Exercise a predeclared 1,000-element provenance census on a valid snapshot, assert full map and a 5-second process timeout on the projection layer. Include a cap refusal for oversized flat wire. |
| T10 | A temporal include-bearing model exits 3 in extraction. Unrelated public MC1 guards remain in the focused suite, with only the newly enabled extraction assertion replaced by T1 and T7. |

| Obligation | Disposition | Command or evidence | Input boundary, justification and invalidation |
|---|---|---|---|
| Direct and downstream | Run, expect 0 | `uv run pytest -q tests/test_lx1_flattening.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_extract_cli.py tests/test_extract_manifest.py tests/test_extract_projection.py tests/test_verify_cli.py tests/test_li0_witness_wire.py --tb=short` | Rerun when model-wire, loaded origin, extract or verification behavior or fixture bytes change. Covers the new producer and consumer plus legacy routes. |
| Project structure guards and Ruff | Run, expect 0 | Use the project hook's exact guard list and `uv run ruff check`. | Covers dependency, query, disclosure, packaging and structure consequences. Run after source/catalog changes. |
| Index | Run, expect 0 | `python3 scripts/components_index.py changed --base <LX1-base-commit> --strict` | Regenerate the index and update component/layer assignments in the source commit. |
| Historical suites and certification | Cadence | `uv run pytest -q -m "evidence or census"` when explicitly selected. | The direct gate establishes current behaviors; historical and certification claims retain their own input bounds and triggers. |

## Phase boundary

LX2 owns witness route enablement. LX3 owns reference composition. LX4
owns the checking split, temporal verification, fidelity fixture and advisory
date report. Direct include byte readers without a trusted root retain
their existing refusal. This spec does not expand the nested, unattended or
reference-in-include model policy.

## Size

Approximately 245 source lines and 240 fixture, test and documentation
lines. The existing layer map acquires one model home and the component
index records the same owner.

## Approval instrument

Corpus-first. Planned fixture root `tests/fixtures/lx1-flattening/` with
`README.md` as the entry point and separate `expected.json` for wire and
exit expectations. Commit the red controls after the exact-byte spec and
corpus rulings. The phase starts implementation after the delegated spec and corpus rulings.

## Implementation findings

- The red harness initially spelled output paths using a `project` stem.
  The existing extraction stem strips `.json` and retains `.orm` for
  `project.orm.json`. The fixture harness now names `project.orm` artifacts.
  The expected wire, origin and exit outcomes in the approved answer file
  are unchanged.
- A pinned include can have the same name as a new output artifact if a
  caller selects its model directory as `--out`. The direct overlap
  regression reproduced exit 0 with the include replaced before the fix.
  Refuse overlap at publication preflight with exit 74, before staging.
- The phase changed three source-pinned historical CLI functions. Preserve
  the identity aliases and add an authenticated RF5 successor for each.
  The RF6 syntax scan gained eight artifact/digest subscriptions and
  annotations and lost one moved index subscription. Record that exact
  delta against the current inventory. The actual model-query policy
  retains its existing budget.
- The shared interpreter's installed version 0.2.0 failed two package
  guards on the untouched baseline and the candidate. The worktree now
  uses its own locked CPython 3.11 environment and its GND 0.3.1 install.

### Lint gate amendment

Delegated approval (auto=true), 2026-11-15. The original verification row
expected exit 0 from whole-tree `uv run ruff check`. The full command still
runs and its actual exit is recorded. The predecessor `8cee22f8` and the
candidate each report the same 188 diagnostics under locked Ruff, compared
by file, code, line and message. Require that equality and exit 0 on the
changed Python files. The workflow-skill diagnostics from the predecessor
remain visible in the full gate.

The component check requested rereads of the shared-loader subsystems and
the extraction and witness subsystems. Their existing flow descriptions
remain accurate. The entries for extraction, verification, model loading,
JSON document handling and witness wire ownership describe the changed
module responsibilities.

### Candidate verification

The locked worktree environment reports GND 0.3.1. The final direct and
affected set in the verification ledger ran with `tests/test_extract_guidelines.py`
also selected because it consumes the extraction index. It exited 0:

    289 passed in 153.46s (0:02:33)

The project structure guard command ran under the default lane filter and
exited 0:

    679 passed, 2 deselected in 290.77s (0:04:50)

The changed-file Ruff check exited 0. Whole-tree Ruff exited 1 with the
188 predecessor diagnostics above. The strict component check and
`git diff --check` exited 0. LX1 awaits its independent diff review and
phase completion record.
