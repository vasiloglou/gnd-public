# Composition and type induction

r3, 2026-11-03. **Approved by the owner `(a1)`** ([gate record](../001-plan-gate.md)).
Milestone: `composition-and-type-induction`.
Sources: [issue #73](https://github.com/vasiloglou/gnd-public/issues/73) (GR-T10),
[#77](https://github.com/vasiloglou/gnd-public/issues/77) (GR-T14), and the
owner's direction of 2026-11-03 to plan them as the successor of
[model-growth-guardrails](../../model-growth-guardrails/notes/model-growth-guardrails-plan.md).
Inspection baseline: `1446f90` (main after PR #79).
Plan authorship is not approval. No phase has a spec approval; no code is
written. CT4 is blocked until MG2 and MG3 merge.

**Revision history and owner rulings.**

- **r1:** first draft. Reviewed in plan review round 1 (four local readers,
  one round over both milestones) as SHA-256
  `48430d1a317c11ee2be83d0d35876fb5c80e22e5d9e7bb678b3bd233c420fa49` (CT1 spec
  `51dd694817fee77650a1154c70865dfad0dd29ee7f339fa54a38c9813a035bb0`); see the
  [round-1 disposition](../../model-growth-guardrails/notes/plan-review-r1-disposition.md).
- **`(o1)` 2026-11-03**, quoted in the predecessor plan's header: rules CT-D1
  (a), four local readers for plan review, provisional for the close review
  until confirmed at the plan gate. It approves no bytes.
- **`(p1)` 2026-11-03**, quoted in the predecessor plan's header: rules the
  round-1 questions as proposed. Here that means J (CT-D4 (b)) and U (CT-D9
  (b')), plus D, the predecessor's evolve version scheme, on which CT4
  depends. It directs r2 and one confirmation round. It approves no bytes.
- **r2:** applies round-1 themes D, H, I, J, L, N, O, P, Q, R, T, U, V, W.
  Sites carry `(r1-X)` tags. Reviewed in the confirmation round as SHA-256
  `506b285d8fa4bba50e877b9c0ce31d25d24970c857a38adb3e68fe64333c9edd` (CT1 spec
  `0a31dad55a52c18a8b498c9d02e46d08fdad759d425de50e9ec303bc7f56a38b`); see the
  [round-2 disposition](../../model-growth-guardrails/notes/plan-review-r2-disposition.md).
  The self-inflicted ratio was 36/43, so the declared stop rule ended plan
  review.
- **r3:** applies round-2 themes R2-F, R2-G and R2-H without another round.
  Sites carry `(r2-X)` tags. One point is proposed for the plan gate
  (CT-D13). **r3 bytes carry no review opinion.**
- **`(a1)` 2026-11-03**, quoted in the predecessor plan's header and gate
  record: approves this plan at r3, SHA-256
  `c670d4522840fd7aee9022498585de3a43ee30638a015e261ae98dc9470a5cc4` (before
  this tag); rules CT-D13 (a); accepts the other §10 proposals as written. It
  does not approve the CT1 spec.

## Problem and completion predicates

**Composition (#73).** An anchor sidecar binds one population to one
document: it carries the raw-byte SHA-256 of each (`anchors.py:48-54,228`),
and `gnd check --anchors --document` checks each anchored value against its
span. A downstream application extracts facts per document, then needs one
population per task, built from many documents, to evaluate derivation rules
over. Merging changes the population digest and can change values, so the
sidecars stop binding, and the application keeps its own provenance map that
GND cannot check. It also needs several spans for one fact role (a definition
and the clause that uses it). The parser refuses that today
(`anchors.py:133-135`), and the checker keeps only the last record per key
(`checker/_core.py:1911-1917`).

**Type induction (#77).** `gnd discover` proposes constraints of seven
families as an evolve proposal for review. When facts land in a generic fact
type ("entity has attribute with value"), a recurring attribute name with a
consistent value type often calls for a dedicated fact type. Nothing proposes
that today. It is the type-level part of the closed
[issue #34](https://github.com/vasiloglou/gnd-public/issues/34).

The milestone can close when:

1. A version-2 sidecar may hold several anchors for one fact role. `gnd check`
   requires every one of them to bind (CT-D2). Every version-1 sidecar checks
   exactly as at `1446f90`, by a recorded table (CT1).
2. `gnd compose` and `gnd.api.compose` build one population from several
   (document, population, sidecar) inputs and an explicit transformation
   manifest, and write a value-free composition record. `gnd check
   --composition` re-verifies every source binding and every composed fact's
   lineage, and checks each anchored value against its source span in its
   source document. A functional conflict between sources is reported by the
   check with both sources' lineage, not refused at composition (CT2).
   `(r1-J, r1-T)`
3. A witness over a composed population (witness version 2) names, for each
   base fact, its source facts, and through their sidecars their document
   spans. `gnd replay --composition` verifies that lineage. Version-1
   witnesses replay unchanged (CT3).
4. `gnd discover --families fact-type` proposes binary fact types from a
   declared generic fact type's rows, above a stated support threshold, as a
   schema-3 additive evolve proposal. The proposal carries the induced
   envelope on a uniqueness constraint, plus a migration report of opaque row
   ids and value digests. The proposal passes `gnd evolve preview --policy
   additive` (MG2), and a shape match (MG3) is reported, not proposed (CT4).
5. Docs dispositions recorded, new pages executed, docs gates exit 0 (CT5).
6. Focused gates, independent diff reviews, the question sweep and a PR are
   recorded. Owner acceptance is separate.

## 0. Binding design rules

| Rule | Requirement |
|---|---|
| CT-R1: Old artifacts keep their meaning | Version-1 sidecars and witnesses, discover runs without the new family, and schema-3 evolve proposals parse, check and replay byte-identically to `1446f90`, by recorded before/after tables `(r1-R)`. |
| CT-R2: Anchors bind values to ranges, nothing more | Neither GND nor the caller claims a span entails a fact. Several anchors add evidence for one role; none of them proves the fact. Docs say so. |
| CT-R3: Composition is explicit and checkable | Every change composition makes (deduplication, renaming, scope tag) is listed in a caller-supplied manifest. GND never infers a merge. The record binds every input by digest and every composed fact to its source facts; a checker re-derives the composed population from the inputs and the manifest and compares bytes. |
| CT-R4: Digests are defined over stated bytes | Each new digest names its input: raw bytes for files a caller writes (sidecars, documents, populations, the manifest), canonical JSON for records GND writes. The canonical form is the existing helper (`canonical_sha256`), not a second implementation. |
| CT-R5: Induction proposes; review admits | The type family emits `source: induced`, `status: proposed`, `modality: deontic`, and never deletes or moves rows. Admission is a reviewed `gnd evolve apply`. |
| CT-R6: No population value enters a model or report without a ruling | A proposed fact type's id is opaque. The attribute value appears in the migration report only as a SHA-256, and as raw text only through `--show-values` as CT-D13 decides it (CT-D9, ruled `(p1)`; CT-D13 proposed `(r2-G)`). Redacted roles never contribute (owner ruling 2026-10-25, `discover/candidates.py:131-132`). |
| CT-R7: Disclosure | `gnd compose` and `api:compose` are `every-mode` rows: they write the caller's own population, as `EvaluationSession.observe` does; the record they also write is value-free (digests, indexes and ids only), and refusal messages never quote values `(r2-G)`. `gnd check --composition` and `gnd replay --composition` follow their existing rows. The site table is keyed by leaf and callable (`test_disclosure_mode.py:213-219`), so `--show-values` cannot have its own row: under CT-D13 (a), proposed, `gnd discover` becomes a `site` leaf and decides `--show-values` with `values_allowed` (`disclosure.py:46-55`); every other discover output is unchanged in every mode, and this supersedes NM-D13 for that option only. |
| CT-R8: Layering, query policy, anonymity, approval | New code joins existing homes with zero new allowances. The composer sits at layer `model` beside `bind_population`; composed-anchor checking at `checking`; API wrappers at `entry`. Model reads through `ModelIndex`; the RF6 allow-list gains no row, and RF6's counted reads do not grow (363 at `1446f90` against a ceiling of 365, so there are two reads of headroom) `(r2-H)`. `auto=false`. Downstream applications unnamed. |

Each phase spec binds every rule above and every rule in
`.codex/skills/process-phase/references/standing-rules.md`, by name or with a
one-sentence argument that it does not apply.

## 1. Scope, sources and authority

| Source | Use |
|---|---|
| Issues #73, #77 | Requests, use cases, workarounds |
| Owner directions `(o1)`, `(p1)` | Rulings |
| `src/gnd/anchors.py:70-72` (1 MiB cap), `:105-139` (`parse_anchor_sidecar`; no JSON Schema exists), `:133-135` (duplicate refusal), `:218-251` (`bind_anchors`), `:228` (raw-byte digests), `:254` (`write_anchor_sidecar`) | Sidecar format and binding (CT1, CT2) |
| `src/gnd/checker/_core.py:1887` (`_anchored_verdicts`), `:1909` (one `document_bytes`), `:1911-1917` (`records[key] = record`), `:1974-2009` (evaluation) | Anchored evaluation (CT1, CT2) |
| `src/gnd/verbalize_population.py:120-136`; `export/verification_service.py:492-511`; `src/gnd/api.py:801` (sidecar objects through the API) | Other sidecar readers (CT1) |
| `src/gnd/commands/checking.py:630-631,739-759`; `checking_service.py:222-223` (anchors with references refused), `:278-289` | CLI and service paths (CT1, CT2) |
| `src/gnd/model/__init__.py:648-725` (`bind_population`, `OccurrenceOrigin`, `BoundPopulationView`); `src/gnd/population.py:470-496` | Union-with-origins precedent (CT2) |
| `src/gnd/schema/witness.schema.json` (`version: {const: 1}`; `base` and `binding` closed) and its twin `src/gnd/skills/gnd-export/references/witness.schema.json`; `skills/gnd-export/references/witness-contract.md`; `witness/io.py:211-232,262-266`; `witness/kernel.py:167-182` | Witness identity and digests (CT3) `(r1-L)` |
| `src/gnd/discover/candidates.py:29` (`FAMILIES`), `:131-165` (redaction ruling), `:253-331` (declared catalogue); `discover/service.py:58-87,153-169,231-257,290-298`; `discover/output.py:21-29,40-153`; `discover/support.py:48,80-145`; `src/gnd/discover.schema.json`; `commands/discover.py:9,56,82` | Discover families, admission, output (CT4) |
| `src/gnd/evolve/models.py:226-240,285-340` (fact-type `ADD`), `:387-425` (`ArtifactLocator`), `:549-560` (no population field) | Proposal shape (CT4) |
| `orm-meta.schema.json` `$defs.fact_type` (no `source`/`status`/`modality`); `model/_validation.py:2029-2042` | Where the induced envelope can sit (CT4) |
| `tests/test_disclosure_mode.py:218` (48 CLI leaves), `:498` (`48 - 15 - 4`); `tests/test_rf1_cli_pins.py`; the four `__all__` pins named in the MG1 spec | Pins (CT2, CT3, CT4) `(r1-N)` |
| Predecessor plan r2: MG2 (additive policy, optional v3 preview fields), MG3 (signature helper, `--shape-report`) | Prerequisites of CT4 `(r1-D)` |
| Induced-knowledge close `012`: "Reader three F6" (alethic induced proposals only warn), IKE-Q3 (discover lets a raw `ArtifactError` escape) | Inherited `(r1-V)` |

A `gnd coverage MODEL` census counts experiment claims; it does not show
whether composition or a discover family exists, so none is run.

### Obligations harvested

| ID | Obligation (source) | Kind | Owner |
|---|---|---|---|
| O1 | Compose several (document, population, sidecar) inputs under an explicit manifest of dedupes, renamings, scope tags (#73.1) | requested | CT2 |
| O2 | A manifest GND can check, each composed fact referring to its source facts and anchors (#73.1) | requested | CT2-C2, C3 |
| O3 | Witnesses over the composed population name source facts and, through them, spans (#73.2) | requested | CT3 |
| O4 | Several anchors per fact role (#73.3) | requested | CT1 |
| O5 | Keep the present guarantee: anchors bind values to ranges (#73) | requested constraint | CT-R2 |
| O6 | Propose a fact type from generic rows sharing a name, a consistent value type, support above a threshold (#77) | requested | CT4-C1, C2 |
| O7 | Include the rows that would migrate (#77) | requested | CT4-C3 |
| O8 | Emit as `induced`, `proposed`, `deontic`; admission stays reviewed (#77) | requested | CT-R5; CT4-C4 |
| O9 | "New object or fact types" from an "attribute or relation name" (#77 title and body) | requested, partly scoped out `(r1-U)` | CT4 covers fact types from attribute names; object types and relation names in §7 |
| O10 | Old artifacts unchanged | cross-cutting | CT-R1 |
| O11 | API, CLI, schema pins; disclosure rows | cross-cutting | each phase; CT-R7 |
| O12 | Docs and release notes | cross-cutting | each phase; CT5 |
| O13 | Downstream anonymity | owner constraint | CT-R8 |
| O14 | Visible checkpoints, docs early | owner preference | CT5 |
| O15 | Inherited: induced alethic proposals only warn (IK close, reader three F6) | inherited | CT4 emits deontic only; the row stays with its IK2 follow-up |
| O16 | Inherited: discover lets a raw `ArtifactError` escape (IKE-Q3) | inherited `(r1-V)` | CT4-C7 |
| O17 | Inherited: RF1 goldens do not reproduce from a fresh capture (NM2-Q3) | inherited `(r1-V)` | each phase changing RF1 goldens recaptures and records |
| O18 | Reporter acceptance in its own pipeline | carried | the reporter, after merge |

## 2. Contract proposal and product behavior

Rulings are marked; everything else is proposed.

### 2.1 Several anchors per fact role (CT1)

Sidecar `schema_version: 2` has the same top-level keys as version 1, still
one population and one document (CT-D12), and replaces the duplicate rule: a
repeated `(fact_key, role, start, end, occurrence)` is refused, while several
anchors per fact role are accepted. The checker groups records per key and
requires every one to bind (CT-D2). Version 1 is parsed and checked as
today. Detail: [phase-CT1-spec.md](phase-CT1-spec.md).

### 2.2 Composition (CT2) `(r1-J, r1-T)`

**Inputs.** A list of sources, each `{id, document, population, sidecar}`
(paths; each sidecar binds its population and document as today), the model,
and a manifest `gnd-composition-manifest/1`:

```json
{
  "schema": "gnd-composition-manifest/1",
  "sources": ["contract-a", "contract-b"],
  "renamings": [{"source": "contract-b", "fact_type": "ft_party", "role": "name",
                  "from": "ACME CORP.", "to": "Acme Corp."}],
  "deduplications": "identical-rows",
  "scope_tags": [{"source": "contract-a", "tag": "2024-agreement"}]
}
```

The manifest is caller-written and digested as raw bytes. `renamings`
rewrite one role value in one source, by exact match; they are the only value
change composition makes. `deduplications: "identical-rows"` (CT-D3) collapses
rows equal after renaming into one composed fact whose lineage lists every
source fact. `scope_tags` attach a tag to every fact from a source and live
only in the record (CT-D5).

**Output.** The composed population (ordinary population JSON) and a
**value-free** record, `gnd-composition/1`, canonical-JSON digested. It
holds:

- the model digest and the manifest's raw-byte digest;
- per source: id, population, document and sidecar raw-byte digests;
- the composed population's raw-byte digest;
- for each composed fact, by position: its source facts as `{source,
  fact_type, fact_index}`, and the renamings applied as **manifest indexes**.

No role value appears in the record. Anchors are not copied: a composed
fact's spans are its source facts' spans, reached through each source's own
sidecar.

**Functional conflicts** (CT-D4, **ruled `(p1)` J: (b)**). Composition does
not check constraints. Two sources giving different values where a
uniqueness requires one compose into two facts. `gnd check --composition`
then reports the violation, and the report names each violating composed
fact's source facts from the record.

**Checking.** `gnd check MODEL COMPOSED --composition RECORD --sources DIR`
runs these steps in order:

1. Re-bind each source sidecar to its population and document (3 on
   mismatch).
2. Re-run composition from the inputs and the manifest, and compare the
   composed bytes and the lineage with the record (3 on mismatch).
3. Run the checker over the composed population.

For `anchored` constraints, each composed fact's role is checked as **source
value against source span in source document**: for each source fact in its
lineage, the source's anchor records for the pre-renaming value are
evaluated against that source's document under CT-D2. This is a named change
to `_anchored_verdicts`, which today takes one `document_bytes`
(`_core.py:1909`). It gains a per-fact resolver from the composed index to a
list of (source id, source fact key, records, document text). Refusal
messages name sources and indexes, never values. `gnd.api.compose` and a
`composition=` keyword on `gnd.api.check` mirror the CLI.

### 2.3 Witness lineage (CT3) `(r1-T)`

**Witness version 2.** The schema's `version` becomes `1 | 2`. Version 2
adds `binding.composition_sha256` and, on each base node, `sources: [{source,
fact_type, fact_index}]` read from the record. `origin.kind` stays
`candidate` (CT-D6). The schema and its twin
`skills/gnd-export/references/witness.schema.json` change together, and so
does `witness-contract.md`.

**Who writes it.** `gnd witness --composition RECORD` and a `composition=`
keyword on `api.witness`. `gnd replay --composition` and `api.replay(...,
composition=)` verify that each node's `sources` equal the record's lineage
for that index; a mismatch exits with replay's existing mismatch code, fixed
in the CT3 spec. Version-1 witnesses replay unchanged. The Souffle witness
export and `why-not` read witnesses. The CT3 spec lists their handling of
version 2: either they read it, or they refuse it with a named message.

### 2.4 Type proposals in discover (CT4) `(r1-D, r1-U)`

**Generic fact type.** A fact type is generic only when declared: its
`provenance` holds `"generic": {"entity": R1, "attribute": R2, "value": R3}`,
naming three roles (CT-D7).

**Family `fact-type`.** Opt-in: not in the default family list. For a
generic fact type, group rows by the attribute role's value. A group yields a
proposal when:

- its **support** (distinct entities, not rows) is at least `--min-support`
  (default 20, CT-D10);
- every value in it has one primitive under `support.identity`;
- the attribute role is not redacted (CT-R6);
- no existing or co-proposed fact type has the same role-player signature
  under MG3's helper. When one does, the group is reported, not proposed.

**Output.** One schema-3 evolve proposal per run, holding `ADD` operations
for new binary fact types (entity, and a value type for the primitive). Each
id is opaque: `ft_<generic id>_induced_<n>`, numbered by group order, with a
placeholder reading for a reviewer to replace (CT-D9 (b'), ruled `(p1)` U).
The induced envelope (`source: induced`, `status: proposed`, `modality:
deontic`, support as numerator and denominator) sits on a uniqueness
constraint the proposal adds on the entity role (CT-D8).

Beside the proposal, a migration report gives, per proposed fact type:

- the opaque row ids (`ft<pos>#<index>`) that would move;
- the SHA-256 of the attribute value;
- the raw value, decided by `values_allowed` under CT-D13 (a), proposed:
  emitted when `--show-values` is passed and the mode is unset, always under
  `internal`, and refused (`DisclosureRefused`) when `--show-values` is passed
  under `customer` `(r2-G)`.

Nothing moves. The proposal passes `gnd evolve preview --policy additive`:
schema 3 is MG2's current version, so no version change is needed.

## 3. Dependencies and artifact homes

CT1 needs nothing. CT2 needs CT1. CT3 needs CT2. Names are appended to
`gnd.api.__all__` in merge order, whichever of MG1 and CT2 merges first
`(r2-H)`. CT4 needs the predecessor's
MG2 and MG3 merged, and is independent of CT1–CT3. CT5 needs CT3 and CT4. If
the predecessor slips, CT1–CT3 proceed and CT4 waits.

| Artifact | Home |
|---|---|
| Plan, specs, records, reviews | `.gnd-planning/milestones/composition-and-type-induction/` |
| Sidecar v2 parser | `src/gnd/anchors.py`; new `src/gnd/anchor-sidecar.schema.json` (CT1) |
| Multi-anchor and per-source evaluation | `src/gnd/checker/_core.py` `_anchored_verdicts` (CT1, CT2) |
| Composer | `src/gnd/composition.py` (new, layer `model`, beside `bind_population`) (CT2) |
| Composed checking | `src/gnd/checking_service.py` (CT2) |
| CLI | `gnd compose` (command group fixed in the CT2 spec); `--composition`, `--sources` on `gnd check`, `gnd witness`, `gnd replay` |
| Schemas | `src/gnd/anchor-sidecar.schema.json` (CT1); `src/gnd/composition-manifest.schema.json`, `src/gnd/composition.schema.json` (CT2), each registered in `tests/support/runtime_schema_inventory.py` and `tests/test_public_built_inventory.py` and checked by `tests/test_conformance_payload.py` `(r2-H)`; `src/gnd/schema/witness.schema.json` and its twin `skills/gnd-export/references/witness.schema.json`, newly pinned by extending `tests/test_schema_sync.py` (its `SCHEMA_PAIRS` covers only orm-meta, population and steps today, from the `gnd-orm-core` directory) (CT3) |
| Type family | `src/gnd/discover/candidates.py`, `output.py`, `discover.schema.json`, `commands/discover.py` (CT4) |
| Docs | each phase's reference page and Unreleased release-note entry; CT5 the rest |

## 4. Phases

### CT1: Several anchors per fact role (#73.3; about 120 source lines, 450 test lines)

Spec: [phase-CT1-spec.md](phase-CT1-spec.md), r2.

- **CT1-C1:** v2 parse; repeated identity refused; v1 refusals unchanged;
  3,500 anchors on one role, in the canonical form `write_anchor_sidecar`
  writes, parse under the 1 MiB cap `(r1-H, r2-F)`.
- **CT1-C2:** every anchor must bind, with a three-anchor fixture (one good,
  two bad) and order independence.
- **CT1-C3:** population verbalization (distinct excerpts per role) and
  export verification on v2.
- **CT1-C4:** schema and parser agree except on parser-only rules P1–P9
  (duplicate identity, `start < end`, the 1 MiB cap, duplicate JSON keys,
  non-JSON constants, integers over 18 digits, nesting over 32, integer-valued
  floats, invalid UTF-8), each with its own case `(r1-I, r2-F)`.
- **CT1-C5:** recorded before/after table for every v1 input.

### CT2: Composition (#73.1; about 420 source lines, 800 test lines)

- **CT2-C1:** manifest and record schemas; parsers total over hostile JSON.
- **CT2-C2:** composer: renamings, deduplication of identical rows, scope
  tags, lineage; deterministic bytes (stable source order, then source fact
  order); the record contains no role value (canary scan).
- **CT2-C3:** checker: re-binding, re-derivation, byte and lineage
  comparison; one refusal case per step, each exit 3; refusal messages
  contain no canary value.
- **CT2-C4:** a cross-source conflict on an **alethic** uniqueness composes
  (exit 0) and `gnd check --composition` exits 1 with both source facts named
  (CT-D4 (b)); the same conflict on a deontic uniqueness exits 0 with a
  warning naming both `(r2-H)`.
- **CT2-C5:** per-source anchored evaluation: a composed fact whose value was
  renamed passes against its source's span; a source anchor out of range
  fails.
- **CT2-C6:** 50 sources × 2,000 facts: row visits and deduplication probes
  counted through a hash index, each ≤ 2 × 100,000.
- **CT2-C7:** API and CLI; the four test `__all__` pins and
  `tools/run_public_acceptance.py:373` (appended in merge order); the two
  schemas in the schema inventories; `python-api.md` count; disclosure table
  (`test_disclosure_mode.py:218` becomes 49 leaves and `:498` its
  arithmetic); RF1 help goldens recaptured (O17).

### CT3: Witness lineage (#73.2; about 160 source lines, 400 test lines)

- **CT3-C1:** witness version 2 in the schema and its twin, the pair added to
  `tests/test_schema_sync.py` `(r2-H)`; recorded
  before/after table showing every version-1 witness replays unchanged.
- **CT3-C2:** `gnd replay --composition`: an edited `sources` list exits with
  the mismatch code; an unedited one exits 0.
- **CT3-C3:** end to end: two documents, a rule joining facts from both, a
  witness whose base nodes trace to spans in each document.
- **CT3-C4:** Souffle witness export and `why-not` on a version-2 witness,
  each with its stated outcome.

### CT4: Type proposals (#77; about 280 source lines, 550 test lines). Blocked on MG2, MG3

- **CT4-C1:** generic declaration parsed and validated; an undeclared fact
  type with the generic shape and high support yields nothing.
- **CT4-C2:** grouping, support threshold and type consistency: support at
  threshold − 1 and at threshold; a group reaching the threshold in rows but
  not in distinct entities; one mixed-type value.
- **CT4-C3:** migration report of opaque row ids and value digests; a canary
  value scan over the proposal bytes and the report (absent without
  `--show-values` under an unset mode); `--show-values` unset (present),
  `internal` without the flag (present), `customer` with the flag (refused,
  asserting the `DisclosureRefused` message); `test_disclosure_mode.py` T26
  arithmetic and the `disclosure.md` table updated `(r2-G)`.
- **CT4-C4:** the emitted proposal passes `preview --policy additive` (exit
  0); it carries the deontic envelope; with `--shape-report`, a group whose
  signature matches an existing fact type is reported, not proposed, while a
  second group in the same run is proposed.
- **CT4-C5:** redacted attribute role skipped and counted.
- **CT4-C6:** without the family, every discover output and the seven-family
  default are unchanged, by a recorded table.
- **CT4-C7:** a discover input that raises `ArtifactError` today exits with a
  stated code (IKE-Q3).

### CT5: Documentation

- **CT5-C1:** dispositions over every page and skill reference naming
  anchors, sidecars, composition, witnesses, replay or discover, including
  the witness contract and the `python-api.md` count.
- **CT5-C2:** checkpoints DC1 (after plan approval) and DC2 (real runs after
  CT3 and CT4).
- **CT5-C3:** one how-to: from several documents to one checked answer
  traced back to each source.
- **CT5-C4:** one Unreleased release-note entry; docs gates exit 0; one
  independent docs reviewer.

### Milestone close (not a feature phase)

Final parity tables, the close review (CT-D1), the question sweep, carryover
O18, and a PR.

### Obligation-to-gate map

| Obligation | Gate |
|---|---|
| O1 | CT2-C1, C2 |
| O2 | CT2-C2, C3, C5 |
| O3 | CT3-C1..C3 |
| O4 | CT1-C1..C3 |
| O5 | CT-R2; CT5 |
| O6 | CT4-C1, C2 |
| O7 | CT4-C3 |
| O8 | CT-R5; CT4-C4 |
| O9 | CT4; §7 |
| O10 | CT-R1; CT1-C5, CT3-C1, CT4-C6 |
| O11 | CT2-C7 and each phase's pins |
| O12 | each phase; CT5 |
| O13 | CT-R8 |
| O14 | CT5-C2 |
| O15 | CT4-C4 |
| O16 | CT4-C7 |
| O17 | each phase changing RF1 goldens |
| O18 | close carryover |

## 5. Documentation, skill and compatibility surfaces

- New: sidecar v2 and a published sidecar schema; two composition schemas;
  one CLI leaf (`gnd compose`) and options on `check`, `witness` and
  `replay`; `gnd.api.compose` and `composition=` keywords on `check`,
  `witness` and `replay`; witness version 2; one discover family and the
  options `--families fact-type`, `--min-support`, `--show-values`.
- Sidecar v2 also reaches the public API through `AnchorSidecar` objects
  (`api.py:801`) and is documented in `python-api.md`.
- **Unchanged without the new inputs:** v1 sidecars, check, witness, replay
  and discover outputs (CT-R1), by recorded tables. Unavoidable changes: the
  root help and RF1 goldens for the new leaf and options; `gnd.api.__all__`
  grows by one name; the `python-api.md` count; the discover help's "seven"
  wording names the opt-in family; the disclosure leaf count becomes 49.
- Packaged skills and twins: `gnd-extract` (sidecar v2), `gnd-orm-core`
  constraint reference (anchored with several anchors), `gnd-export`
  references (witness schema twin and contract), and the discover sections
  that mention families.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| Several anchors read as stronger proof | CT-R2 in docs; CT-D2 names exactly what passes |
| Composition silently merges distinct entities | CT-R3: only manifest renamings change values; dedupe only of identical rows |
| A composed population drifts from its sources | Checker re-derives and compares bytes |
| A renamed value is checked against the wrong span | Source value against source span (§2.2); CT2-C5 |
| Values leak through the record or refusals | Record value-free; canary scans (CT2-C2, C3) |
| Two digest forms confused | CT-R4 |
| Witness format breaks old replays | CT-R1; CT3-C1 table |
| Type proposals leak population values | CT-R6; opaque ids; value digests; `--show-values` only under `internal` |
| Induction proposes a duplicate | MG3 shape check before proposing; CT4-C4 |
| Rows moved without review | CT-R5: report only |
| Prerequisite milestone slips | CT4 blocked explicitly; CT1–CT3 proceed |
| Downstream names leak | CT-R8 |
| Repair rounds introduce defects | §8 stop rule |

## 7. Out of scope

- Inferring merges, entity resolution, fuzzy matching across documents.
- Several documents per sidecar (CT-D12).
- Anchors combined with reference populations (still refused,
  `checking_service.py:222-223`), CT-D11.
- Proposing object types, and proposing fact types from relation names
  rather than attribute names (#77 asks for both; scoped out here) `(r1-U)`.
- Moving rows into proposed fact types; any non-additive evolve operation.
- Structural detection of generic fact types.
- Constraint induction on newly proposed fact types beyond the one uniqueness
  carrying the envelope.
- Publication, release, certification.

## 8. Execution, approval and review protocol

`auto=false`. Each phase follows `process-phase`: spec, owner gate,
implementation and focused tests, an independent diff review, a refactoring
review and a record. No code before recorded spec approval. Plan and close
review: four local readers (CT-D1, `(o1)`).

**Stop rule, declared before round 2** `(r1-W)`: at most one more plan round
after round 1, a confirmation round over r2 restricted to the blocking
themes. Stop after it. Stop early, and apply any repairs without another
round, when the self-inflicted ratio (round-2 findings attacking text r2
created, over all round-2 findings) exceeds one half, or when the same seat's
finding count does not fall from round 1 to round 2 while severity falls.
Work happens on a topic branch, then a PR; merge requires the owner.

## 9. Per-phase verification story

| Phase | Expected result | Focused gate |
|---|---|---|
| CT1 | v2 parse and check; v1 parity | the command in the CT1 spec §Tests |
| CT2 | Compose, re-derive, refuse; conflicts reported by check | CT1 gate plus `tests/test_composition.py`, `tests/test_public_api.py`, `tests/test_v61_phase2_api.py`, `tests/test_public_runtime.py`, `tests/test_why_not_near_misses_public.py`, `tests/test_rf1_cli_pins.py`, `tests/test_disclosure_mode.py` |
| CT3 | Lineage in witness and replay; v1 replay parity | CT2 gate plus `tests/test_witness_composition.py`, `tests/test_schema_sync.py`, and the witness, replay, Souffle-witness and why-not test files the CT3 spec lists by name |
| CT4 | Family proposals; additive pass; parity | `tests/test_discover_fact_type_family.py`, the discover test files the CT4 spec lists by name, `tests/test_evolve_additive_policy.py`, `tests/test_evolve_shape_matches.py`, `tests/test_rf1_cli_pins.py`, `tests/test_disclosure_mode.py` |
| CT5 | Pages executed; checkpoints seen | `uv run python tools/run_tutorials.py`, `zensical build --strict`, `uv run python tools/check_docs.py site` |

## 10. Owner decisions and open questions

| ID | Question | Readings and cost | Ruling or proposal |
|---|---|---|---|
| CT-D1 | Plan and close review instrument | (a) four local readers; (b) six-seat panel | **Ruled `(o1)`: (a)** for plan review; close review confirmed at the plan gate |
| CT-D2 | When does a role with several anchors pass? | (a) every anchor binds: each anchor is a claim, and a false one is an error; (b) any one: one good anchor hides a wrong one | (a) |
| CT-D3 | Deduplication | (a) identical rows collapse with all source facts as lineage; (b) none: functional constraints then fail on harmless repeats | (a) |
| CT-D4 | Conflicting functional values across sources | (a) refuse composition; (b) compose and let `gnd check` report with lineage | **Ruled `(p1)` J: (b)** |
| CT-D5 | Where scope tags live | (a) the record only; (b) a role in the composed population: changes fact shapes | (a) |
| CT-D6 | Witness lineage shape | (a) keep `origin.kind: candidate`, add `sources` (witness version 2); (b) new `origin.kind: source`: the kernel would resolve rows in sources | (a) |
| CT-D7 | How a generic fact type is identified | (a) declared in `provenance.generic`; (b) structural guess: false positives become proposals | (a) |
| CT-D8 | Where the induced envelope sits | (a) on a uniqueness constraint the proposal adds; (b) fact types gain `source`/`status`/`modality`: a model-spec change across validation and evolve | (a) |
| CT-D9 | Naming from an attribute value | (a) id and reading from the value: a population value enters the model; (b') opaque id, value digest in the report, raw value only with `--show-values` under `internal` | **Ruled `(p1)` U: (b')** |
| CT-D10 | Support threshold | (a) `--min-support N` distinct entities, default 20; (b) a fraction: unstable on small populations | (a) |
| CT-D11 | Composition with reference populations | (a) stays refused; (b) supported: reopens a refusal with its own review | (a) |
| CT-D12 | Several documents per sidecar | (a) no, one per sidecar; (b) yes: two ways to say the same thing | (a) |
| CT-D13 | How `--show-values` is decided `(r2-G)` | (a) `gnd discover` becomes a `site` leaf using `values_allowed`: customer refuses the flag, unset emits only with it, internal emits always. That reads `(p1)` U's "raw value only with `--show-values` under `internal`" as GND's standard site behavior, and supersedes NM-D13 for this one option; (b) the literal reading, the raw value only when the flag is passed **and** the mode is `internal`: a custom check unlike every other site, and discover would need its own mode resolution | **Ruled `(a1)`: (a)** |

| ID | Open question | Owner |
|---|---|---|
| CT-Q1 | Tests asserting "duplicate fact-role anchor" | **Closed:** none (CT1 spec) |
| CT-Q2 | Witness digest form (canonical model dump, `witness/io.py:262-266`) against raw-byte sidecar digests | CT3 spec, under CT-R4 |
| CT-Q3 | Replay's mismatch exit code, and Souffle and why-not handling of witness version 2 | CT3 spec |
