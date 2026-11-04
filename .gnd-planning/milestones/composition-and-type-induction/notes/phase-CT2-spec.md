# Phase CT2: composition

**Status: r1, delegated approval (auto=true) 2026-11-04 `(d1)`.**
Implementation follows this approval and the CT1 record.

`(d1)` **Delegated approval (auto=true)**, 2026-11-04. Authorization: the
owner's "Yes, run it auto" in this session, invoking `process-milestone
composition-and-type-induction auto`. This is an agent ruling under that
delegation, not the owner's personal reading. Approved bytes: SHA-256
`73cafabea2aff8a5a0de258046d72493b2527776341ee3b1e2ab75713336caa9` (before this tag), after the implementability sweep at `f20f5c3`
(CT1 committed): `load_population_bytes`, `bind_anchors`,
`read_regular_path`, `MAX_ENTRIES` (100,000) and
`gnd.artifacts.canonical_json_bytes` exist at the homes named; the composer's
imports (`gnd.population`, `gnd.anchors`, `gnd.artifacts`) are at layers
`model` and `infrastructure`; `canonical_sha256` sits at layer `lanes` (D6).
Rulings: D1 to D6 (a). Budget: about 360 source, 120 schema and 700 test
lines; no paid calls. Compatibility: without the new options every command
is unchanged (CT-R1, T16); new CLI leaf `gnd compose`; `gnd.api.__all__`
gains `compose`; the disclosure leaf count becomes 49. Diff review
instrument: one local reviewer agent.

## Provenance

- Plan: [composition-and-type-induction-plan.md](composition-and-type-induction-plan.md)
  r3, approved `(a1)` 2026-11-03: §2.2, §3 (homes), §4 CT2, §9 CT2 row, §10
  CT-D3, CT-D4 (ruled `(p1)` (b)), CT-D5, CT-D11, CT-D12.
- Source: [issue #73](https://github.com/vasiloglou/gnd-public/issues/73)
  requests 1 and 2 (GR-T10).
- Inspection baseline: `a2e44f8` (main after PR #85) plus the CT1 phase on the
  same branch, which supplies several anchors per role.
- Authority: the owner's "Yes, run it auto" (2026-11-04), invoking
  `process-milestone composition-and-type-induction auto`. **This spec's
  bytes carry no review opinion.**

## Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| #73.1, plan O1 | Compose several (document, population, sidecar) inputs under an explicit manifest | `compose`; T3..T6 |
| #73.1, plan O2 | A record GND can check: each composed fact names its source facts | record; T7..T10 |
| Plan CT-R1 | Without `--composition`, `gnd check` is unchanged | T16 |
| Plan CT-R2 | Anchors bind values to ranges; composition adds no proof | reference page wording |
| Plan CT-R3 | Every change composition makes is in the manifest; GND never infers a merge; the checker re-derives and compares bytes | renamings by exact match only; T4, T8 |
| Plan CT-R4 | Raw-byte digests for caller files, canonical JSON for the record | record fields; T7 |
| Plan CT-R7 | `gnd compose` and `api.compose` are every-mode rows; the record and refusals carry no value | T11, T12, T15 |
| Plan CT-R8 | Homes, layering, RF6, anonymity | T17 |
| Plan CT-D4 `(p1)` (b) | A cross-source conflict composes; check reports it with lineage | T13 |
| Plan CT-D11 | Composition with reference populations stays refused | T14 |

## Standing rules bound to this phase

1. **Totality:** the manifest and record parsers are total over arbitrary
   bytes: every malformed input is exit 3 (CLI) or an `exit_code: 3` payload
   (API) with `composition:invalid`, never a traceback. They reuse the anchor
   parser's strict JSON reader (duplicate keys, constants, depth, oversized
   integers, invalid UTF-8) through one helper, not a copy.
2. **Input cap bounds the algorithm:** the manifest and record are capped at
   1 MiB and 16 MiB; the composed population at the existing 100,000-entry
   limit (`MAX_ENTRIES`). Deduplication keys a dictionary on the row's identity
   key, so composition is linear in input rows (T6).
3. **Validation order:** layout, then manifest parse, then each source in
   manifest order (population parse and validation, sidecar parse, sidecar
   binding), then renamings, then composition.
4. **One walk:** the composer visits each source row once. The checker
   re-derives through the same function, so there is no second composer.
5. **One home:** the composition format's normative prose is
   `docs/reference/composition.md`; the two schemas describe it and a test
   holds the schemas, parser and writer in step.
6. **Measurement over argument:** CT-R1 is a recorded before/after table
   (T16), not a claim about suites.

**Plan rules:** CT-R1 (T16), CT-R2 (reference page), CT-R3 (Design;
T4, T8), CT-R4 (record fields), CT-R5 and CT-R6 not applicable (no
induction), CT-R7 (T11, T12, T15), CT-R8 (T17).

## Goal

`gnd compose MODEL DIR --out COMPOSED --record RECORD` reads the manifest
`DIR/manifest.json` and, per source id, `DIR/<id>/population.json`, its
adjacent sidecar `DIR/<id>/population.json.anchors.json` and the document
`DIR/<id>/document.txt`; it binds each sidecar, applies the manifest's
renamings, collapses identical rows, writes the composed population and a
value-free `gnd-composition/1` record, and exits 0. `gnd check MODEL COMPOSED
--composition RECORD --sources DIR` re-binds every source, re-derives the
composition and compares bytes and lineage (exit 3 on any mismatch), checks
the composed population, evaluates every `anchored` constraint per source
(source value against source span in source document), and names the
lineage of every offending composed fact. Without the new options every
command is byte-identical to `a2e44f8` (T16). The CT2 gate exits 0.

## Design

### Layout of a composition directory (D1)

```
DIR/
  manifest.json
  <id>/population.json
  <id>/population.json.anchors.json
  <id>/document.txt
```

An id matches `^[A-Za-z0-9][A-Za-z0-9._-]{0,63}$` and is a path segment. Every
id in the manifest has its three files; extra entries in `DIR` are ignored.
Files are read with `read_regular_path` (no symlinks). The layout is the
whole interface: the manifest names ids only, as the plan's example does.

### Manifest `gnd-composition-manifest/1`

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

- `sources`: one or more distinct ids, in composition order.
- `renamings`: each names a manifest source, a fact type and role the model
  declares, and JSON scalars `from` and `to` of the same JSON type. It rewrites
  every value of that role in that source's facts equal to `from` (same type,
  same value). A renaming that matches no row is refused (D2): an unused
  renaming is a manifest error, not a no-op. Two renamings with the same
  (source, fact type, role, from) are refused. The renamed population must
  still validate against the model; a renaming that breaks a value constraint
  of the role's object type is refused by population validation.
- `deduplications`: `"identical-rows"` only (CT-D3 (a)).
- `scope_tags`: zero or more (source, tag) pairs; a tag is a non-empty string
  of at most 128 characters; it lives only in the record (CT-D5 (a)).

### Composer `src/gnd/composition.py` (new, layer `model`, about 230 lines)

```python
def compose(model, model_raw, directory) -> ComposedResult  # population bytes, record
def parse_manifest(raw) -> Manifest
def parse_record(raw) -> Record
```

For each source in manifest order: read and validate the population against
the model (refusing a model with reference populations, CT-D11), parse its
sidecar, bind it (`bind_anchors` with the raw population and document bytes and
the parsed population: CT1's binder). Then walk each source's fact types in
the population file's key order and each row in order, apply the renamings,
and append the row to its composed fact type unless an identical row (same
identity key, `values.identity_key` over the row's sorted roles) is already
there; either way the source fact `{source, fact_type, fact_index}` is added
to that composed fact's lineage, with the manifest indexes of the renamings
applied to it. Instances are unioned by identity key in source order;
`covers` is the ordered union.

The composed population is ordinary population JSON:
`{"population": {"model", "model_id", "source": "composition", "covers"},
"instances", "facts"}`, `model` copied from the first source's header,
written as canonical JSON bytes plus a newline, so composing twice gives the
same bytes (T5).

### Record `gnd-composition/1` (value-free)

```json
{
  "schema": "gnd-composition/1",
  "model_sha256": "<raw bytes of the model file>",
  "manifest_sha256": "<raw bytes of manifest.json>",
  "population_sha256": "<raw bytes of the composed population>",
  "sources": [{"id": "contract-a", "population_sha256": "...", "sidecar_sha256": "...", "document_sha256": "..."}],
  "scope_tags": [{"source": "contract-a", "tag": "2024-agreement"}],
  "facts": [{"fact_type": "ft_party", "index": 0,
             "sources": [{"source": "contract-a", "fact_type": "ft_party", "fact_index": 0}],
             "renamings": []}]
}
```

`facts` lists every composed fact in composed order (fact type key order, then
index). The record is written as canonical JSON (`gnd.artifacts.canonical_json_bytes`)
and its identity, `record_sha256`, is the SHA-256 of those bytes (CT-R4). The
plan names `canonical_sha256`, but that helper lives in `gnd.evolve.models`
at layer `lanes`, which the composer at layer `model` may not import; the
infrastructure helper gives the one canonical form without a second
implementation (D6). Fact type
ids, source ids and tags are names the caller or model chose; no role value
appears (T11's canary scan).

### Checking (`src/gnd/checking_service.py`, about +70 lines; `src/gnd/checker/_core.py`, about +60 lines)

`gnd check MODEL COMPOSED --composition RECORD --sources DIR`, in order:

1. Parse the record (3 on failure). Check the model's raw-byte digest and the
   composed population's raw-byte digest against the record (3).
2. Re-run `compose` over `DIR` (which re-binds every source sidecar: 3 on a
   mismatch) and compare the composed bytes, the manifest digest, every source
   digest, the scope tags and the lineage with the record (3, naming the first
   differing field, never a value).
3. Run the checker over the composed population, with anchored verdicts from
   `check_with_composed_anchors` (below).

`check_with_composed_anchors(model, population, *, sources, lineage)` beside
`check_with_anchors` (D3): for each source it runs the existing
`_anchored_verdicts(model, source_population, sidecar, document_bytes)` once,
so each source value is checked against its own span in its own document,
before renaming, with CT1's every-anchor rule. A composed fact fails an
anchored constraint when any of its lineage source facts appears in that
source's offending facts for the same constraint (matched by row identity key
within the source fact type). The composed verdict is `fail` (or `warning`
when deontic) with the composed offending facts in composed order; otherwise
`unchecked` with the first unchecked source's reason, in source order;
otherwise `vacuous` when the composed fact type is empty; otherwise `pass`.
The snapshot/admission projection is handled as in `check_with_anchors`.

`--composition` and `--sources` come together (64 otherwise) and exclude
`--anchors`, `--document`, `--references` and `--compiled-operations` (64).

**Lineage in the report (D4).** With `--composition`, the JSON report gains a
top-level `composition` object: `{"record_sha256", "lineage": [{"fact_type",
"index", "sources": [...]}]}`, listing each composed fact named in any
verdict's `offending_facts` (by row identity within its fact type), in
composed order. The report schema's check payload gains this optional key.
Text output adds one line per such fact: `lineage <fact_type>#<index>:
<source>:<fact_type>#<fact_index>, ...`. Without `--composition` the key is
absent and the text is unchanged.

### CLI and API

- `gnd compose MODEL DIR --out COMPOSED --record RECORD` (top-level leaf, D5):
  exit 0, 3 (input refusal, `composition:invalid` or an anchor binding
  message), 64 (usage), 74 when an output cannot be written. Both outputs are
  written atomically, the population first; on refusal neither is written.
- `gnd check ... --composition RECORD --sources DIR` as above.
- `gnd.api.compose(model, directory)` returns `{"schema": "gnd-compose/1",
  "exit_code": 0, "population": <composed JSON>, "record": <record>}` or an
  `exit_code: 3` payload with `error: {kind: "input", message}`; it writes
  nothing. `gnd.api.check(..., composition=RECORD, sources=DIR)` mirrors the
  CLI; `composition=` accepts a path or a parsed record dict.
- `gnd.api.__all__` appends `compose` after `verbalize_rules` (merge order,
  plan §3).

### Schemas

`src/gnd/composition-manifest.schema.json` and
`src/gnd/composition.schema.json`, registered in
`tests/support/runtime_schema_inventory.py` and
`tests/test_public_built_inventory.py`, and checked by
`tests/test_conformance_payload.py`.

### Disclosure (CT-R7)

`gnd compose` and `api:compose` join the disclosure table as `every-mode`
rows: they write the caller's own population, as `EvaluationSession.observe`
does. The leaf count assertion at `test_disclosure_mode.py:218` becomes 49 and
`:498` becomes `49 - 15 - 4`. `gnd check --composition` follows `gnd check`'s
existing row; its added `composition` block carries ids and indexes only.
Under `customer` the existing redaction of offending facts applies unchanged.

## Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | How sources are named on the CLI | (a) one directory with a fixed layout and the manifest inside; (b) repeated `--source ID=POP,SIDECAR,DOC` options: separators collide with paths | (a) |
| D2 | A renaming that matches nothing | (a) refuse: an unused renaming is a manifest error; (b) ignore: a typo silently changes nothing | (a) |
| D3 | How per-source anchored evaluation is built | (a) run the existing `_anchored_verdicts` once per source and map offending source facts to composed facts through the lineage; (b) a per-fact resolver inside `_anchored_verdicts` (plan §2.2 wording): a second code path through the evaluation loop | (a): the same result with no change to CT1's loop. This is the plan's "named change" read as a new caller, not a new parameter |
| D4 | Where lineage of a violation appears | (a) a `composition` block in the JSON report and lineage lines in text; (b) lineage inside each offending fact: changes every verdict's shape | (a) |
| D6 | Canonical digest helper | (a) `gnd.artifacts.canonical_json_bytes` (infrastructure); (b) `gnd.evolve.models.canonical_sha256`: an upward import from `model` to `lanes` | (a) |
| D5 | Command group of `compose` | (a) top-level `gnd compose`; (b) under `gnd extract`: compose reads extract's outputs but is not extraction | (a) |

## Tests

New file `tests/test_composition.py` unless noted. Fixture: a small contract
model with an `anchored` constraint and an alethic and a deontic uniqueness,
two sources `contract-a`, `contract-b`, each with a document, population and
v2 sidecar, built by the test from text.

| # | Case | Expected |
|---|---|---|
| T1 | Manifest parse: valid; each missing/extra key; wrong schema; empty `sources`; repeated id; bad id; unknown source in a renaming or tag; type-mismatched `from`/`to`; `deduplications: "none"`; duplicate renaming; tag over 128 characters; and the strict-JSON hostile cases | ok; `composition:invalid` each |
| T2 | Record parse: valid; each hostile and shape case | ok; `composition:invalid` each |
| T3 | Two sources, no renamings | exit 0; composed rows in source order; lineage one source fact each |
| T4 | A renaming in source B makes a B row identical to an A row | one composed fact; lineage both source facts; `renamings` lists the manifest index on B's entry only |
| T5 | Compose twice; swap source order in the manifest | identical bytes; different bytes and lineage |
| T6 | 50 sources × 2,000 facts | row visits and dedupe probes counted, each ≤ 2 × 100,000 |
| T7 | Record digests | each source digest equals the raw-byte SHA-256 of its file; `model_sha256` and `population_sha256` likewise |
| T8 | Check: unedited | exit 0 |
| T9 | Check refusals, one per step: edited record field; edited composed population; edited source document (sidecar no longer binds); edited manifest; edited lineage; missing source file | exit 3 each, message naming the step |
| T10 | Unused renaming; renaming breaking a value constraint; model with reference populations | exit 3 each |
| T11 | Canary: a role value `CANARY-7f3a` in every source | absent from the record bytes and from every refusal message in T9, T10 |
| T12 | `api.compose` and `api.check(composition=, sources=)` | equal to the CLI outputs |
| T13 | A conflict on an alethic uniqueness across A and B | compose exit 0; check exit 1, `composition.lineage` names both source facts; the same on a deontic uniqueness exits 0 with a warning naming both |
| T14 | Option conflicts: `--composition` without `--sources`; with `--anchors` | exit 64 |
| T15 | Per-source anchoring: a value renamed in B passes against B's span; a B anchor out of range fails the composed fact; `GND_DISCLOSURE=customer` | pass; exit 1 with lineage; offending values redacted |
| T16 | Before/after table: `gnd check` and `gnd compose`-free commands over the CT1 parity inputs, recorded at `a2e44f8` and after in `evidence/CT2/parity.json` | identical |
| T17 | `tests/test_rf1_layering.py`, `tests/test_rf6_query_policy.py`, `tests/test_gnd_arch.py`; anonymity scan over added files | exit 0 |
| T18 | Pins: the four `__all__` pins and `tools/run_public_acceptance.py`; `python-api.md` count; disclosure table (49); RF1 goldens for the root help, `check --help`, the new `compose --help`, `tree.json` | updated and passing |

### Verification selection

```
uv run pytest -q tests/test_composition.py tests/test_anchor_sidecar_v2.py \
  tests/test_public_api.py tests/test_v61_phase2_api.py tests/test_public_runtime.py \
  tests/test_why_not_near_misses_public.py tests/test_rf1_cli_pins.py tests/test_rf1_pin_harness.py \
  tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_rf1_layering.py \
  tests/test_rf6_query_policy.py tests/test_gnd_arch.py tests/test_conformance_payload.py \
  tests/test_public_built_inventory.py tests/test_v70_phase1_surfaces.py tests/test_v70_phase5_corpus.py
```

plus T16's recorded table and the docs gates for the new reference page.

## Out of scope for this phase

- Witness lineage (CT3); type proposals (CT4).
- Several documents per sidecar (CT-D12); composition with reference
  populations (CT-D11); inferred merges or fuzzy matching (plan §7).

## Size

About 360 source lines, 120 schema lines, 700 test lines.
