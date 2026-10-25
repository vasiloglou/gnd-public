# IK1 — Object-type descriptions

## 1. Status

**r4 (o), approved by the owner 2026-10-24 (o); see §12.** Plan r4 was approved
in the same act. D1 (no version bump) was ruled by the owner on 2026-10-24 (o).

## 2. Provenance

This spec derives from plan r4, §§0–10. Source request:
[issue #34](https://github.com/vasiloglou/gnd-public/issues/34), request 1.

| Revision | SHA-256 | Review |
|---|---|---|
| r1 | `f79d6375…cec0` | plan-review round 1 ([disposition](plan-review-r1-disposition.md)) |
| r2 | `4f4cb8b5…cac1` | confirmation round 2 ([disposition](plan-review-r2-disposition.md)) |
| r3 | `8114bf6c…3299` | none (owner-directed repairs P-1..P-9) |

After round 1, the owner accepted the repairs and D8–D13 on 2026-10-23 (o).
The accepted disposition is commit `642cade`.

After round 2:
- the owner confirmed D12's reading (o);
- the owner directed repairs P-1..P-9 as r3, with no further review round (o);
- review stopped by its declared rule.

On 2026-10-24 the owner ruled D1 (no bump) and D14: the description is a JSON
object with a fixed core plus extras, replacing r3's 512-character string (o).
r4 applies that ruling.

**r3 and r4 bytes carry no review opinion.** No approval digest exists.

Change tags:
- `(p1)` marks r2 changes made in response to round 1.
- `(p2)` marks r3 changes made in response to round 2. These apply P-1, P-4,
  P-5, P-8 and the IK1 rows of P-9.
- `(r4)` marks r4 changes recording D14. Where r4 rewrites a whole section, the
  section heading carries the tag.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK1-C1 optional description object: core keys plus extras; twins identical; boundary exits (r4) | plan §4 IK1; IK-O1; IK-R4; D14 (o) | §6 schema; T1, T2 |
| IK1-C2 core keys render escaped and untruncated in verbalization, extraction vocabulary and codegen docstrings; extras in no prose; projection unchanged (r4) | plan §4; IK-R5; R2-F1, R2-F3 (p1); C2-F1/C4-F2 (p2); D14 (o) | §6 renderers, escaping; T3–T6, T13, T14 |
| IK1-C3 vocabulary digest ignores description; diff v2 only with annotations; both diff schemas | plan §4; D11, D12 (o); R2-F2, R2-F5, R3-F2 (p1); C2-F2 (p2) | §6 anchors, diff; T8, T10, T11, T12 |
| IK1-C4 outputs unchanged against digests captured at IK1's base commit | plan §4; IK-R3; C3-F1/C4-F1, C4-F3 (p2) | §6 baseline capture; T7 |
| IK1-C5 evolve `annotation` surface validates; references updated (review-checked) | plan §4; R2-F4, R3-F8 (p1); C2-F3, C4-F4 (p2) | §6 evolve, references; T9 |
| Request-2 fallback if PR #35 is unmerged at this spec's gate | plan IK-O2 | §7 IK1-D4 |
| No model version bump | plan D1 (o) | §6 schema |
| Standing rules 1–6 | process-phase standing rules; IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |

## 4. Standing rules bound to IK1

| Rule | Application |
|---|---|
| 1 Totality | No new loader. The existing total model loader with schema validation is the only gate, and renderers read validated models. Hostile strings are tested in T3 and T5; extras of every JSON type in T2 and T14 (r4). |
| 2 Input cap vs algorithm (r4) | Each core string is capped at L characters (IK1-D1). Escaping is linear, and its output is at most L × 6 characters (the longest escape sequence) per core key, so at most 4 × 6 × L per object type. Extras are never escaped or rendered as prose; they are bounded by the model's existing 10 MiB `MAX_MODEL_BYTES` cap and handled only by existing JSON serialization. A work counter adds nothing beyond that, so the rule is argued inapplicable. |
| 3 Validation order | Unchanged: schema validation precedes all rendering. Diff still checks vocabulary identity before any row computation. |
| 4 One walk | One escape walk serves both the capped and uncapped forms (p2). Escape steps 1–2 of `verbalize._neutralize` are factored into `verbalize.neutralize_text(value) -> str`. `_neutralize` calls it and then applies its cap unchanged. Description core keys use `neutralize_text`, so there is no second escaping copy. The codegen delimiter rule is unchanged. |
| 5 One home | Field definition and core-key list: gnd-orm-core `representation-format.md` (r4). Diff wire: `diff.schema.json`; the `report.schema.json` embedded copy yields to it and T10 holds them identical. Surfaces: `evolution-contract.md`. Vocabulary-digest composition: `representation-format.md` §272, with `constraint-reference.md:47` citing it (p2). Core-key render order: one tuple constant `DESCRIPTION_CORE_KEYS` in `verbalize.py`, read by all three renderers (r4). |
| 6 Measurement | Byte identity for the absent case is decided by T7 against digests captured at IK1's base commit with the commands in §6, not by argument (p2). |

## 5. Goal (r4)

`gnd validate` exits 0 for a model whose object types carry a `description`
object with a `summary` and any of `row`, `source`, `notes`, plus any extra
keys. It exits 3 for a string description, an empty object, an object without
`summary`, a core value that is not a non-empty string, and a core value over
its cap.

The core keys appear escaped and **untruncated**, including when they contain
escapable characters (p2), in three places:
- model verbalization (all core keys);
- the constraint-blind extraction vocabulary (all core keys);
- generated tool docstrings (`summary` only).

Extras appear in none of that prose. They are carried unchanged in the model,
in the verbalization's existing `canonical=` machine field, in diff
annotations and on the evolve surface.

`gnd diff` of two models that differ only in a description:
- exits as it does for identical models;
- emits `schema_version: "gnd-diff/2"` with an `annotations` list, valid against
  both diff schemas.

`gnd evolve preview` lists the change on surface `annotation`.

For every fixture named in T7, each output listed there hashes to the SHA-256
captured at IK1's base commit (p2).

## 6. Design

**Schema (r4)** (`src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`,
copied to `src/gnd/schema/orm-meta.schema.json`; ~25 lines). Added to
`$defs/object_type.properties`, with `L` fixed by IK1-D1:

```json
"description": {
  "type": "object",
  "required": ["summary"],
  "properties": {
    "summary": {"$ref": "#/$defs/description_text"},
    "row":     {"$ref": "#/$defs/description_text"},
    "source":  {"$ref": "#/$defs/description_text"},
    "notes":   {"$ref": "#/$defs/description_text"}
  },
  "additionalProperties": true,
  "description": "Optional explanation of what one instance of this object type is. Core keys are rendered, never interpreted; any other key is an extra, carried unchanged and never rendered as prose. See representation-format.md."
}
```

and to `$defs`:

```json
"description_text": {"type": "string", "minLength": 1, "maxLength": L}
```

Meaning of the core keys:
- `summary`: what one instance of the object type is. Required, so every
  description has one readable sentence.
- `row`: what one fact or record about an instance means.
- `source`: where the knowledge came from.
- `notes`: anything else a reader of the model should know.

There is no `allOf` version gate (D1 (o)). The r3 512-character cap is
withdrawn: it was chosen to match `_neutralize`'s output cap, which descriptions
no longer use (C2-F1), so it had no remaining basis. Core strings are rendered
with `neutralize_text`, escaped and never capped.

**Escaping** (`verbalize.py`, ~12 lines) (p2, r4):

```python
DESCRIPTION_CORE_KEYS = ("summary", "row", "source", "notes")

def neutralize_text(value: Any) -> str:
    """Escape untrusted text exactly as _neutralize does, without the length cap."""
```

`_neutralize(value)` becomes `neutralize_text(value)` plus the existing cap and
elision. Its output is byte-identical for every input. If an RF definition-body
pin covers `_neutralize`, its successor row is recorded through the existing
`source-successors.json` mechanism, with a reason citing IK1.

**Model verbalization** (`model_verbalization.py::_object_type_cnl`, ~8 lines) (r4):
- When present, append, for each core key present in `DESCRIPTION_CORE_KEYS`
  order, ` <Label>: '<neutralize_text(text)>'.` with labels `Description`,
  `Row`, `Source`, `Notes`.
- Extras are not rendered in the sentence. The existing `canonical=` field
  already carries the raw JSON of every key, extras included. The duplication of
  core keys is intended: `canonical` is the machine identity, the sentence is
  for readers.
- When absent, the output is unchanged.

**Extraction vocabulary** (`src/gnd/vocabulary.py::render_verbalization`, ~8 lines) (r4):
- When present, append one `neutralize_text` line per core key present, in
  `DESCRIPTION_CORE_KEYS` order, after the object type's sentence. Extras are
  not rendered.
- The list of read keys lives in the compatibility shim's docstring,
  `src/gnd/extract/vocabulary.py:3–10`; it gains `description` core keys (p2,
  C2-F4).
- The vocabulary stays constraint-blind.
- `extract/projection.py` and `_ALLOWED_KEYWORDS` are **not changed**.

**Codegen** (`codegen/docstrings.py`, ~10 lines) (r4):
- For each role line whose object type has a description, append
  ` — <neutralize_text(summary)>` inside the existing `'''` delimiter. Other
  core keys and extras are not rendered, keeping docstrings to one line per
  role.
- The delimiter rule depends only on `'` being escaped, which `neutralize_text`
  preserves.
- When absent, the output is unchanged.

**Vocabulary digest** (`anchors.py::vocabulary_digest`, ~3 lines) (D11 (o)):

```python
"object_types": [
    {key: value for key, value in item.items() if key != "description"}
    for item in objects
]
```

The whole `description` object, extras included, is excluded. The digest is
unchanged for every model without descriptions. Consequence (p2, C1-F5): the
vocabulary digest no longer identifies the rendered vocabulary text, so an
extraction sidecar stays bound when only a description changes. This is
intended and pinned by T11.

**Diff** (`diff.py`, `api.py`, `diff.schema.json`, `report.schema.json`,
`diff.reference.md`; ~45 lines) (D12 (o)):
- `diff_models` computes `annotations = [{object_type, before, after}]`, where
  `before` and `after` are the whole description object or `null`, for each
  object type whose description differs under canonical JSON equality (sorted
  keys), extras included (r4).
- **Empty `annotations`:** the payload is byte-identical to today, including the
  existing `"schema_version": "gnd-diff/1",` line, which the RF1 mutation
  `M-SEM-diff-schema` anchors.
- **Non-empty `annotations`:** the payload uses `schema_version = DIFF_SCHEMA_V2`,
  defined on its own line as `DIFF_SCHEMA_V2 = "gnd-diff/2"`, and adds
  `annotations`.
- **Schema shape (p2, C2-F2):** `diff.schema.json` keeps its closed top-level
  `properties` and `additionalProperties: false`, and changes as follows:
  - `schema_version` becomes `{"enum": ["gnd-diff/1", "gnd-diff/2"]}`;
  - `annotations` is added as an optional property whose items' `before` and
    `after` are `{"type": ["object", "null"]}` (r4);
  - an `if`/`then`/`else` on `schema_version` requires `annotations` with
    `minItems: 1` for `gnd-diff/2`, and requires it absent for `gnd-diff/1`.

  There is no top-level `oneOf`, so `tests/test_conformance_payload.py:652`, which
  indexes `["properties"]["command"]`, keeps working.
  `report.schema.json` `$defs.diff_reference_report` changes identically.
- **Redaction:** the `redaction.py` diff branch redacts only population data and
  is **not edited**. `annotations` pass through, and T8 pins that in `applied`
  mode.
- `diff.reference.md` documents v2.

**Evolve** (`evolve/service.py::_surface_index`, `evolve/models.py`,
`skills/gnd-model-evolve/references/evolution-contract.md`; ~8 lines):
- Add surface `object_types[<id>].description` of kind `annotation`, only when
  the key is present. A change to any key, extras included, is one change on
  that surface (r4).
- Add `"annotation"` to the `BlastRadiusEntry.surface` `Literal`, and a contract
  row.

**References** (review-checked, not test-checked — p2, C4-F4):
- `representation-format.md`: the field, its core keys and their meaning, the
  extras rule (r4), and the vocabulary-digest composition at line 272, adding
  `description` to the excluded keys;
- `constraint-reference.md:47` digest composition sentence;
- `verbalization-patterns.md` sentence form;
- `evolution-contract.md`;
- `diff.reference.md`;
- the gnd-extract skill reference that lists vocabulary content.

**Baseline capture** (p2, C3-F1/C4-F1, C4-F3). **Base commit B** is the commit
named at this spec's owner gate: `main` after PR #35's disposition (merged or
closed). It is never `a22ccde`, unless #35 is closed unmerged.

The capture procedure:
1. Before the first code change, check out B.
2. Run the commands below with `PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=0` from the
   repository root.
3. Commit the SHA-256 values in
   `tests/fixtures/induced_knowledge/ik1-baseline.json` as the approved-spec
   commit's companion.
4. Never regenerate the values from changed code.

Notation:
- `F` ranges over
  `tests/fixtures/models/{full_vocabulary,library,keywords,v2_worked_example}.orm.yaml`.
- `T` is a fresh temporary directory.
- `<T>` normalization replaces the literal temporary-directory path with `<T>`
  before hashing.

| # | Output | Command / call | Hashed bytes and normalization |
|---|---|---|---|
| 1 | model verbalization | `python -c "from gnd.model_verbalization import render_model_verbalization as r; import sys; sys.stdout.write(r(sys.argv[1]))" F` | stdout bytes; none |
| 2 | extraction vocabulary | `python -c "from gnd.model import load_model; from gnd.vocabulary import render_verbalization as r; import sys; sys.stdout.write(r(load_model(sys.argv[1])))" F` | stdout bytes; none |
| 3 | extraction projection | `gnd extract --out T/x F` | `T/x/<stem>.projection.schema.json` raw bytes (e.g. `full_vocabulary.projection.schema.json`); none |
| 4 | codegen tree | `gnd codegen --out T/p F` | `T/p/.gnd-codegen.json` raw bytes after `<T>` normalization |
| 5 | conformance payload | `gnd conformance --format json F T/p` (after row 4) | stdout bytes after `<T>` normalization, with the `gnd_version` value replaced by `<V>` |
| 6 | diff | `gnd diff --format json F F` | stdout bytes; none |
| 7 | evolve preview (once, not per F) | `tests/test_model_evolution.py::_write_cli_workspace` for case `evolution-safe-additive` into T, then `gnd` with `_preview_argv(paths)` (it already passes `--format json`) | `--out` preview file bytes after `<T>` normalization |

If any row is not byte-stable across two runs at B, that is a finding recorded
before implementation. Its fix is a declared normalization added under IK-R12,
never a silent drop.

Estimated size (p2, r4): ~110 source lines, ~340 test lines, ~80 reference lines.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| IK1-D1 (r4) | Core-string cap `L` | Proposed **4,096**, the longest string cap already used in `orm-meta.schema.json` (`path`), so the schema keeps one ceiling for free text. The cap exists only to bound rendering work (rule 2); with uncapped escaped rendering any fixed `L` is safe. Fixed at this gate under IK-R12; values above `L` exit 3. |
| IK1-D2 | Diff wire | Settled by D12, owner-confirmed 2026-10-23 (o): `gnd-diff/2` only with annotations. Emitting v2 always would change every diff's bytes and break RF1 diff pins. |
| IK1-D3 | Also on fact types and roles? | Object types only (proposed, as requested) vs all elements. The broader scope triples renderer work, and it can follow later additively. |
| IK1-D4 (p2, revised) | Base commit B and request 2 | Proposed: B is `main` after PR #35's disposition, named at this gate. Alternative: fold #35 into IK1, which enlarges IK1's frozen-pin surface. Either way T7 uses B, so no correct implementation fails T7 because of #35. |
| IK1-D5 (r4) | Extras placement | As ruled (D14): extras are any other top-level key. Consequence stated for the gate: a misspelled optional core key (e.g. `note`) validates as an extra and is silently not rendered; a misspelled `summary` still fails because `summary` is required. Recorded, not changed: altering it would revisit D14. |
| IK1-D6 (r4) | Non-JSON YAML scalars in extras (e.g. timestamps) | The exit for a YAML value with no JSON form inside an extra is fixed at this gate from the existing loader's behaviour at B, and pinned by T2 as either accepted-and-serialized or exit 3. |

## 8. Tests

| ID | File / case | Expected |
|---|---|---|
| T1 | `test_schema_sync.py` passes with the edited twins; a new assertion checks `description` and `description_text` exist in both (r4) | pass; fails on a no-op |
| T2 (r4) | new `test_object_type_description.py`: accepted — `{summary}` of 1 character; all four core keys at length `L`; `{summary}` plus extras of every JSON type (string, number, boolean, null, list, nested object). Refused — a string description (r3 form); `{}`; `{row}` without `summary`; `summary` empty; `summary` non-string; `notes` at `L + 1`. Plus the IK1-D6 case. Accepted cases discriminate, since today's schema rejects any `description` | accepted cases exit 0; refused cases exit 3 |
| T3 (r4) | model verbalization and vocabulary contain every present core key in full with no elision marker, and the docstring contains `summary` in full, for (a) plain strings of length `L` and (b) strings of length `L` of `'`, `\n` and U+2028 (p2) | pass; a capped renderer fails (b) |
| T4 | codegen docstring contains `summary` inside `'''` | pass |
| T5 | a hostile core value (`'`, `'''`, `\n`, U+2028, length-`L` mix) cannot break delimiters or forge lines in verbalization, vocabulary or docstring | pass |
| T6 | `render_verbalization` output contains the core-key lines. The `audit_allowlist` assertion is a non-regression guard only, not a discriminator (p2) | pass |
| T7 | rows 1–7 of the §6 baseline table equal `ik1-baseline.json` for every F (p2) | pass; a seeded change that emits `annotations: []` for undescribed models fails |
| T8 (r4) | `gnd diff` of two models differing only in a description: exit equals the identical-model exit; `schema_version` is `gnd-diff/2`; `annotations` holds the one add/change/remove with whole objects; a change to an extra alone also yields one annotation; the payload validates against `diff.schema.json`; `annotations` survive `applied` redaction | exit as identical; pass |
| T9 | evolve preview of a description-only modify lists an `annotation` entry that validates in `BlastRadiusEntry`; a model without descriptions lists no `annotation` surface | exit 0 |
| T10 | `report.schema.json` `$defs.diff_reference_report` equals `diff.schema.json` modulo `$id`/title; a reference-population diff with `annotations` validates; `tests/test_conformance_payload.py` passes unchanged (p2) | pass |
| T11 | `vocabulary_digest` is equal with and without a description (extras included), and unchanged for all T7 fixtures. A comment names the intended consequence: the digest does not identify the vocabulary text (p2, r4) | pass |
| T12 | RF1 mutation table: `M-SEM-diff-schema` still matches its `old` text exactly once and is still killed | pass |
| T13 (p2) | `_neutralize(x)` equals the capped `neutralize_text(x)` byte for byte on the existing neutralizer test inputs | pass |
| T14 (r4) | a description whose extras hold a distinctive marker string: the marker appears in no verbalization sentence, vocabulary line or docstring, and does appear in the verbalization `canonical=` field and in the model loaded back | pass; a renderer that walks all keys fails |

Criterion ↔ test mapping (p2, r4):

| Criterion | Tests |
|---|---|
| C1 | T1, T2 |
| C2 | T3, T4, T5, T6, T13, T14 |
| C3 | T8, T10, T11, T12 |
| C4 | T7, T11 |
| C5 | T9 (surface); the reference clause is review-checked only |

Every test maps back to at least one criterion.

## 9. Out of scope for this phase

- descriptions on fact types, roles or constraints;
- any use of descriptions, core or extra, by the checker;
- any interpretation or schema for extras;
- changes to the projection schema or its allowlist;
- model version changes;
- induced provenance (IK2).

## 10. Size

Estimate (p2, r4): ~110 source lines, ~340 test lines, ~80 reference lines.
Measured at record time.

## 11. Approval instrument

This prose. The change is additive, and its one conditional wire version (D12)
and the description schema (D14) are given as literal schema text above, so a
fixture corpus first is not proposed. T7's baseline file is committed at base
commit B before any code (IK-R12).

## 12. Owner gate record (2026-10-24)

**Approval (o).** In chat on 2026-10-24 the owner replied "approved" and then
confirmed that it covers r4 as on the branch, not r3. Approved bytes:

| Artifact | SHA-256 |
|---|---|
| plan r4 `notes/induced-knowledge-plan.md` | `8afbdcbd4a7757053c8775cc4faaade1225534664ccd7cdb6ad22ae5b54cd51a` |
| IK1 spec r4, this file before §12 and the §1 status line | `3076680b3f1486c4ae2dd0256c0718fa065ff3bce8c80611150843ad9fa403ce` |

The approval carries no review opinion. Plan bytes are not edited after approval.

**Instrument (o).** This prose (§11). No spec review panel.

**Decision rulings (o), 2026-10-24.** The owner accepted the proposed readings
with the approval:

| ID | Ruling |
|---|---|
| IK1-D1 | `L` = 4,096 |
| IK1-D2 | settled by D12 |
| IK1-D3 | object types only |
| IK1-D4 | base commit **B = `1d6eee0`**, the merge of PR #35 into `main`. Request 2 shipped in #35, so IK1 has no request-2 fallback work |
| IK1-D5 | recorded as stated: a misspelled optional core key is an extra |
| IK1-D6 | **exit 3**, chosen by the owner from the two readings below |

**IK1-D6 finding and amendment (o).** At B, the model loader parses YAML with
ruamel `typ="safe"`, so an unquoted timestamp becomes a `TimeStamp` object. Every
schema location at B has a JSON type, so such a value always exits 3. For
example, `name: 2026-10-24T10:00:00Z` on an object type fails with
`is not of type 'string' [jsonschema:type]`. r4's literal
`"additionalProperties": true` has no type, so a timestamp extra would pass
validation and then reach JSON serialization (`canonical=`) uncaught. That would
break standing rule 1.

The owner ruled exit 3. §6 is amended as follows (o):

```json
"additionalProperties": {"$ref": "#/$defs/description_extra"}
```

with, in `$defs`:

```json
"description_extra": {
  "type": ["string", "number", "boolean", "null", "array", "object"],
  "items": {"$ref": "#/$defs/description_extra"},
  "additionalProperties": {"$ref": "#/$defs/description_extra"}
}
```

T2 adds an unquoted-timestamp extra, at top level and nested, each expecting
exit 3. Whether non-finite floats (`.nan`, `.inf`) are refused is recorded at
implementation as a finding, not assumed.

**Base-commit capture.** The capture ran at B in a clean detached worktree with
`PYTHONHASHSEED=0 SOURCE_DATE_EPOCH=0`. It ran twice and both runs were
byte-identical. All 25 commands exited 0.

The values are in `tests/fixtures/induced_knowledge/ik1-baseline.json`. The
capture script is
`evidence/IK1/capture_ik1_baseline.py`.

**Normalization finding (IK-R12).** `<T>` is the **resolved** temporary
directory. On macOS, `/var` is a symlink to `/private/var`, and evolve preview
refuses a workspace whose path crosses a symlink: exit 74,
`workspace crosses symlink /var`. This is a declared normalization of row 7's
temporary path, not a dropped row.

## 13. Implementation findings

Recorded as found, 2026-10-24.

- **IK1-F1, non-finite numbers.** With the §12 schema amendment, a YAML
  timestamp or date in an extra, top-level or nested, exits 3. `.nan`, `.inf`
  and `-.inf` still validated, because the JSON Schema `number` type accepts
  them. Reproduced: `render_model_verbalization` then raised a serialization
  error, because `_canonical` uses `allow_nan=False`, which breaks standing
  rule 1. NaN and infinity have no JSON form, so the owner's D6 ruling (exit 3)
  covers them. Fixed in the existing layer-1 screening walk
  (`model/_validation.py::_layer1_structural`), scoped by path to
  `$.object_types[i].description`, with rule id `jsonschema:type` like the
  neighbouring integer screen. Outside descriptions, B's behaviour is unchanged
  and pinned by a test. Tests: T2 `nan`, `nested-inf`, `negative-inf`.
- **IK1-F2, reference site.** `representation-format.md` line 272 is the
  `depends_on` digest-exclusion sentence. The sidecar-composition paragraph
  appears only in `constraint-reference.md:47`. The `description` exclusion is
  stated in the new `description` field bullet and in `constraint-reference.md:47`,
  which now cites `representation-format.md`. That follows the spec's one-home
  intent, not its line number.
- **IK1-F3, pre-existing doc drift (deferred).** The `BlastRadiusEntry` surface
  list in `evolution-contract.md` already omitted the `operation` surface that
  `evolve/models.py` declares. IK1 adds only `annotation`; the `operation` gap is
  an open question for milestone close.
- **IK1-F4, operator error, recovered.** To check T12's kill, the RF1 mutation
  was applied to `diff.py` and reverted with `git checkout`, which also discarded
  the uncommitted IK1 `diff.py` edits. They were restored from a copy taken just
  before the mutation. The restored file has the IK1 additions and one
  `"schema_version": "gnd-diff/1",` anchor. T8, T10 and T12 pass on it. The
  mutation itself made its expected-red test fail, so the anchor is still killed.
- **IK1-F5, review R1/R2 under IK1-D6.** The adversarial review reproduced two
  more description values that validated but were not carried faithfully as
  JSON:
  - a lone surrogate, which crashed `gnd diff` (internal error) and
    `gnd codegen`;
  - an anchored YAML boolean, which ruamel loads as an `int` subclass and which
    was serialized as `1`.

  Both fall under the owner's D6 ruling (exit 3 for a value with no JSON form)
  and D14 (extras are carried unchanged). The layer-1 screen now refuses both
  inside descriptions through one predicate,
  `_description_value_without_json_form`. Hex and anchored integers still
  validate, and a test pins that. Each new T2 case was red before the fix.
- **IK1-F6, refactoring-era inventories.** Two RF guards count source shapes,
  so IK1 registers its successors there:
  - The `gnd.model._layer1_structural` definition-body pin gets an RF6b row in
    `compiled-snapshot-obligations/evidence/CI/source-successors.json`, the home
    PR #35 used.
  - The dynamic-candidate census gets a new chained delta,
    `evidence/IK1/dynamic-query-successor.json` (7 added, 1 removed; type
    annotations and description-key subscripts only), appended to
    `DYNAMIC_SUCCESSORS`.

  An intermediate edit wrongly changed the head file of that chain. The edit
  was restored from `HEAD` before any commit.
- **IK1-F7, deferred to the owner.** Review R3: extras have no declared nesting
  bound. Refusal depends on Python's recursion limit (about depth 243 on
  Python 3.14), and evolve proposals cap JSON depth at 64. A new numeric bound
  needs an owner-recorded amendment under IK-R12, so none was added (IK1-Q1).

## 14. Owner amendment: IK1-Q1 description nesting cap (2026-10-24)

**Ruling (o).** The recommendation offered to the owner was: "Rule IK1-Q1 with a
nesting limit of 64. It's the last open decision, it's small, and 64 matches
the limit evolve already enforces". The owner replied "ok go on" on 2026-10-24.
Under IK-R12 this is a new numeric bound, fixed by owner amendment.

**Arithmetic:**
- The description object is level 1, and each nested object or array adds 1.
- A container at level 65 or deeper is refused at layer 1, exit 3, rule
  `jsonschema:maxDepth`.
- The cap is checked in the existing iterative layer-1 walk, so it applies
  before `jsonschema`'s recursive descent. Before the cap, YAML refusal began
  near 243 levels as a caught `RecursionError`.

**Correction to the recommendation.** "64 matches the limit evolve already
enforces" was imprecise. `input_policy.MAX_DEPTH = 64` counts a whole JSON
document. An evolve proposal carries an object type in an operation's `after`,
so a description starts about five levels down. A description at roughly levels
60–64 therefore validates but cannot pass through an evolve proposal. A cap of
about 59 would close that window; changing the number needs a new owner ruling.
Two related limits:
- JSON model files already stop at whole-document depth 64, about 60 levels of
  description.
- Past roughly 240 levels, the YAML loader still refuses first, at exit 3,
  without the named rule.
