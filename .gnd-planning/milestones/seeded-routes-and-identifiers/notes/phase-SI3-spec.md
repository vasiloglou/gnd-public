# Phase SI3 — Ossie reference identifiers

## 1. Status

Draft on 2026-11-25. The owner decides D3 and the opt-in Ossie validator and
parser lane after the corpus-first gate is ready.

## 2. Provenance

Issue #280, plan r2 §0, §1, §2, §4, §5 and §9, Ossie relational bundle OB3-Q5,
and the OS0 upstream receipt. The SI2 census and the Ossie exporter call path
show that its identity-selection change leaves this corpus's output unchanged.

## 3. Obligations

| Obligation | Evidence |
|---|---|
| SI3-C1 / D3 | Before-code JSON goldens and SHA-256 roster for every affected tracked model. |
| SI3-C2 / R3 | Export comparisons, local schema and name resolution, and owner-selected pinned validator and parser. |
| SI3-C3 / R4 | CLI import of old bundles and new CLI export/import round trips with the bound sidecar. |
| SI3-C4 | Mapping counts by cause and a control for subtypes without `inherits_reference`. |
| O5 / §5 | Normative Ossie projection table, explanation page, and release note. |

## 4. Standing rules

Reuse the existing structured model reader. The projection consumes the
existing reference declarations and identification view. Rmap columns, unit
labels, sidecar identities, and path safety stay governed by their current
contracts. Test the size of the added identifier work through the existing
bounded export. The representation format owns the projected relationship
rule. The phase scope excludes tag operations.

## 5. Expected behavior

A unit-based entity identifies through a single-valued `Decimal` relationship.
GND maps its `Number` identity column to that referent and keeps the source
unit and measure label through the digest-bound sidecar. An inheriting entity
with several supertypes uses the first supertype's identifier in the declared
order. Its own identity, if present, still has precedence. An entity which
declares `inherits_reference: false` retains its own identity. Objectification
fallbacks remain outside SI3.

## 6. Corpus and measurements

The authoring probe patches already-exported canonical JSON with explicit
ontology edits and pins the before and after bytes. It runs source loader and
export admission on the tracked model set. The expected documents each pass
GND's local ontology schema and name graph. This is a preparation result.
The pinned upstream validator and parser run belongs to the selected SI3 gate.

A mapping dry calculation supplies the expected identifiers on the existing
relational projection, using the current Number columns for unit references.
That calculation removes 8 unit-based links and 5 multi-supertype links and
adds none. The expected final totals are 4 unmapped links and 2 concepts for
the retained objectification cause. A mapping comparison after implementation
must re-run the same tracked-model census.

The affected ontology census contains ten unit-based identities and seven
inheriting multi-supertype identities across 17 tracked models. The [corpus manifest](../evidence/SI3/ontology-corpus.json) lists each model's
old and expected SHA-256, identity edits, and expected document.
The JSON artifact is the digest-pinned corpus. The YAML CLI export must parse
to the same ontology and round-trip through a YAML-bound sidecar.

## 7. Decision D3

Proposed (owner): approve the corpus with a numeric Decimal identifier for
unit-based entities, first-supertype identity selection for the inheriting
multi-supertype case, and source-model round-trip through the sidecar. Authorize
the pinned Ossie parser and validator on the changed ontologies. Sidecar-free
foreign import continues to apply its published best-effort general-reference
rules.

## 8. Tests and gates

- Compare canonical JSON output to each approved expected document.
- Exercise YAML output, independent old-bundle import and new bound CLI
  import. Preserve the original model identity and the declared unit and
  supertype information.
- Measure mapping counts by cause. Check an authored non-inheriting subtype
  with a different identity and the first-parent sequence with differing
  supertypes.
- Run focused OSSIE export/import/relational/docs, existing corpus, lint,
  query and architecture controls, and the component-index gate.
- With D3's separate selection, run the pinned validator and parser from the
  OS0 receipt against each new changed ontology. Record the exact checkout
  and oracle pins and machine-observed results.

## 9. Out of scope

Objectifications keyed by their own fact types, a new Rmap key rule, upstream
release changes, and a new standalone unit-interchange wire format.

## 10. Size

Approximately 65 production lines, 130 direct test lines, and the expected
wire corpus. A materially larger implementation needs a recorded spec repair.

## 11. Approval instrument

The preimplementation canonical JSON corpus and its digest manifest. Retain
the pre-edit export digests and verify the named red cases on the base.

### Corpus binding

Manifest SHA-256: `ba2964bb757ad645340cd870b4e848cd1d17af92fc7af97b14b373de7541bb62`. All 17 expected documents passed GND's local schema and name graph. The pinned upstream oracle remains pending the D3 decision.

### Owner decision, 2026-11-25

The owner approved D3 in this chat against the preceding spec bytes at
SHA-256 `a0e8e5dbaa92337e5084c3af9371f7f349dd486f81aa7a7787d2334763e20666` and the corpus manifest bound above. Scope: Decimal
identification for unit-based entities, the declared first supertype's
identifier for inheriting multi-supertype entities, source-model round trip
through the digest-bound sidecar, and the pinned upstream validator and
parser for the changed ontologies. This is the owner's direct ruling.

The delegated implementation gate follows SI2's completion record and the
corpus-first preimplementation checks.

### Approved preimplementation gate

SI2 completed in record 003. Component-index searches for `Ossie ontology`
and `Ossie mapping` found the existing projection, mapping, importer and
oracle components. The implementation adapts those surfaces.

The approved files and manifest retain their original digest. The pinned
validator and parser each accepted all 17 expected JSON documents. The
respective checkouts matched OS0's `ee89dbdc2844d8b7d293ed42c8613928bb99505f`
and `83ddc294c8840f5f497a2bdbec2348a128fc2254`. Raw command results with
paths redacted are retained in `evidence/SI3/oracle-preimplementation.json`.

The default fixture gate at `b6722aee` ran
`.venv/bin/pytest -q tests/test_si3_ossie_identifiers.py --tb=short`
and exited 1 with `37 failed, 1 passed, 34 deselected in 2.48s`. All JSON/YAML
corpus comparisons, the mapping-loss control, the inheriting-subtype control
and the large unit projection were red. The non-inheriting control passed.
The deselected oracle tests are run separately under the owner's selection.
The pre-change bound import probe restored all 17 source documents.

Delegated implementation approval (auto=true), 2026-11-25. SI3 spec
through the preceding gate SHA-256 `1482e16164269f713bb84bba9c68bba9141d5bc4fe3a2cb099c8fe8ac57343e8`. Source: the owner's named
milestone delegation and direct D3 ruling above. Scope: the approved corpus,
unit and multi-supertype projection and mapping, existing source round trip,
and the selected pinned oracle on changed ontologies. Instrument: the
before-code corpus plus the red test gate. Budget: one phase diff review
with Claude Code Opus, with a second only over repairs if needed.
