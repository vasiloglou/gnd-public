# Phase OS1 — Export the core Ossie ontology

## 1. Status

Ready for delegated spec approval, 2026-11-10.

## 2. Provenance

Plan r3 predicates 1–3 and 7, §§0, 2, 4, 5, 6, 9 and 10. OS0's
[phase record](../006-phase-OS0.md) and [census amendment](../005-OS0-spec-amendment.md)
supply the pins, roster and measured controls. The [owner ruling](../004-owner-OD6.md)
confirms default exit 0 with a loss report and exit 3 under strict mode.
No spec review has run.

## 3. Obligations

| Source | Obligation | Evidence |
|---|---|---|
| OS1-C1 | Core concepts, roles, readings, references and multiplicity; schema validates census outputs | All eligible revised census files export in process; three legacy examples repaired and tested |
| OS1-C2 | Pinned external validator and parser | Independent `ossie_oracle` lane validates every eligible document with both tools and checks negative controls |
| OS1-C3 | Byte-stable serialization, sidecar and canonical identity | Same source twice under unrelated paths; compare bytes, source model identity and document digest |
| OS1-C4 | Exactly one loss disposition per RFC 6901 pointer | Independent census check and mixed containers, escaped keys and population refusals |
| OS1-C5 | Include route selected explicitly | Three census include roots and a constructed missing-dependency root refuse with `include:unsupported-route` before resolving dependencies |
| §0, §2.3, F4 | Credential-free, create-once grouped publication | Collision and induced I/O failure on each file, strict, alias and race controls |
| §5 and §9 | CLI parser identity and help | Successor goldens over the changed command and inherited CLI characterization |
| §6, §10 | R7 pins, OD2 sidecar, OD4 role reorder, OD5 Duration, OD6 loss | Schema digest, live role bindings, type extension, default/strict controls |

## 4. Standing rules

1. Totality. The exporter reads a capped buffer and passes it to the existing
   bounded model parser and full loader. The loss-report reader belongs to OS3.
   Invalid document, non-JSON metadata, depth and cap controls exit 3.
2. Input cap. The projection builds lookups once and classifies each pointer
   once. A scaled synthetic model exercises the projection time bound.
3. Order. Bounded read, parse, include guard, full GND admission, project and
   validate output schema, apply strict policy, stage and publish. Collision
   and missing-parent cases exercise refusal order at the CLI.
4. One walk. A map from source pointer to native projection supplies one
   traversal with extension as the fallback and inherited refusal only for
   population subtrees. Every pointer appears once in the loss report.
5. One home. Representation-format.md owns mapping and wire behavior.
   The schema is vendored byte-identical to the OS0 pin.
6. Measure. The adopted OS0 witnesses include a repeated role, reading order
   that differs from declaration order and a OneToOne synthetic control.

## 5. Goal

Exit 0 and publish a complete ontology, sidecar and loss report for each of
38 eligible census inputs after the example spelling correction. The three
include roots exit 3. The external validator and parser each exit 0 on each
eligible output. Strict with a refused population exits 3. Failed publication
leaves no committed document.

## 6. Design

| Capability | Component consult | Decision |
|---|---|---|
| Model admission | `validate model load model schema`, `model schema package JSON resource validate` | Reuse `model.loading`, `model.json_document`, `model.composition` guard and `model.query_index` for admitted object lookup |
| Identity | `canonical JSON stable digest serialization`, `export artifact serialize render` | Reuse `infra.artifacts` canonical JSON and `model.scalar_identity` canonical model identity |
| Group output | `atomic publish multiple files collision`, `transaction stage output rollback write new` | Reuse `infra.safe_filesystem` descriptor anchors. Existing single-leaf publishers cannot stage the entire set, and compose uses overwriting renames. Extend `safefs` with a create-once group primitive |
| Command | `export artifact serialize render`, `CLI export dispatch` | Adapt `cli.export_command` with one parser and branch |
| External | Installed PyYAML, jsonschema, pinned Ossie checkout | Reuse `yaml.safe_dump` and `Draft202012Validator`. Keep upstream parser and validator outside runtime dependencies |

`gnd.export.ossie.render_ossie(model_path: Path, *, output_format: str,
strict: bool = False) -> OssieArtifacts` returns `document`, `sidecar`
and `loss_report` byte fields. It keeps the exact admitted author document
for JSON pointer identity. Names already safe and distinct are preserved.
Ossie built-in names and other collisions get deterministic source-ID aliases,
with the original spelling in the sidecar. Value types extend the matching
built-in. Duration extends Integer with its source primitive retained.
Subtypes use declared source parents. Popular and general references get
generated identifying relationships. Inherited or composite references use
native declarations where their identifying binary relationships are
available with equivalent semantics. Unsupported reference detail stays in
the sidecar. Name allocation reserves fact identifiers within each owner.

Each fact type supplies a relationship. GND's forward placeholders are
positional. A qualified inverse uses role names. A bare binary inverse
reverses the two bindings. Ossie places the first role on the owner and
qualifies explicitly named additional roles. Choose OneToOne for both
binary uniqueness directions. Otherwise use ManyToOne for an n−1
determinant, preserving source order when possible and reordering only when
the reading binding is retained. Additional uniqueness, constraints,
derivations, objectification and GND metadata remain in the sidecar during OS1.
Existing explicit relationships and reference declarations retain their source
identity for a later round trip.

Loss report `gnd-ossie-loss/1` has `schema`, `model_identity`,
`document_sha256` and `dispositions`. Each row has `pointer`,
`disposition` (native, requires, extension, refused) and `reason` (closed
schema vocabulary). OS1 emits native, extension and refused. The sidecar
`gnd-ossie-sidecar/1` has `schema`, `model_identity`,
`document_sha256`, and `elements` keyed by the nearest element ID, or the
empty string for document-level entries. A pointer-keyed entry describes
a retained container as `{"kind":"array"}` or `{"kind":"object"}`, a native
projection by `{"kind":"copy","from":"/ontology/..."}` or a spelling/value
whose exact source form needs the sidecar as `{"kind":"literal","value":...}`.
The one pointer traversal writes both artifacts. Arrays and object keys
remain addressable in the original source order. No refused value is emitted
in either metadata artifact.

`gnd export ossie MODEL --out FILE [--loss-report FILE] [--format yaml|json]
[--strict]` defaults to YAML, `FILE.gnd.json` and `FILE.loss.json`.
`publish_new_files(outputs: Sequence[tuple[Path, bytes]]) -> None` stages
every file under its retained destination parent. Hard links publish
companions first and the document last, exclusively. On a synchronous
publication failure it rolls back its own published entries. The document is
the completion marker. Multiple arbitrary paths cannot be committed in a
single filesystem operation. A process or machine interruption before the
marker can leave uncommitted companions. The helper preserves concurrent
callers' files and refuses paths whose parent cannot be retained.

## 7. Decisions

| ID | Ruling |
|---|---|
| D1 | Explicit OD6 owner confirmation. Default exit 0 on a population refusal; strict exits 3. |
| D2 | Select include refusal under predicate 7. The CLI does not compose includes. |
| D3 | Repair issueNumber, occurredOn, startDate and fullName in the three shipped skill examples only. The original OS0 baseline remains archived. |
| D4 | Keep source-keyed reconstruction in the bound sidecar and use the ontology as the publication marker. |
| D5 | Keep the independent upstream lane opt-in, separate from ordinary pytest. |

## 8. Tests

- `tests/test_ossie_export.py`: focused command, all 41 current census
  sources, deterministic output, strict and malformed exits, exact pointer
  accounting, Duration, OneToOne, reordered roles, collision and rollback.
- `tests/test_ossie_external_oracle.py`: pinned validator and parser census
  plus a malformed control. Successful collection alone is insufficient.
- CLI successor characterization, affected PyRel CLI and layer/index checks.
- Existing bounded model intake and publication failure controls exercise
  every distinct refusal outcome used by the new command.

## 9. Out of scope

Formula rendering, Ossie import, third-party PyRel output equivalence,
runtime provider dependencies and certification.

## 10. Size

About 400 implementation lines including grouped publication and about
250 focused test and harness lines, plus schema, CLI snapshots and index.

## 11. Approval instrument

This prose, the revised OS0 evidence and the explicit OD6 ruling. The
phase diff needs one independent reviewer in a different tool. The external
oracle lane and any new authenticated review send require their own selection.

## Implementation findings

- All 38 eligible census models now render locally after repairing the four
  role spellings. The three include roots take the existing route guard.
- The base package ships ruamel.yaml rather than PyYAML. The YAML writer uses
  the installed ruamel.yaml safe emitter, and the ordinary package dependency
  gate keeps the runtime dependency set unchanged. PyYAML stays in the
  scratch oracle environments.
- Two census value concepts spell their name Date, which Ossie reserves.
  The projection aliases both to gnd_date and preserves their source spelling.
- The sidecar retains pointer locations and array order. Its canonical JSON
  sorts object keys. The reconstruction test compares every copy and literal
  entry against the admitted source value.
- The focused test corpus includes version 3 Duration, inherited direct
  identifiers, a composite identifier, and both binary multiplicity
  directions. Group publication controls cover a failing link at each
  position and concurrent create-once calls.
- The external oracle harness prepends the pinned parser's source path within
  its isolated interpreter. The external gate needs a separate selection.
