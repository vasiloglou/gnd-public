# IK1 — Object-type descriptions

## 1. Status

**r3 (p2), awaiting plan approval, D1 and the IK1 owner gate.** Not
implementable until all three have happened.

## 2. Provenance

This spec derives from plan r3, §§0–10. Source request:
[issue #34](https://github.com/vasiloglou/gnd-public/issues/34), request 1.

| Revision | SHA-256 | Review |
|---|---|---|
| r1 | `f79d6375…cec0` | plan-review round 1 ([disposition](plan-review-r1-disposition.md)) |
| r2 | `4f4cb8b5…cac1` | confirmation round 2 ([disposition](plan-review-r2-disposition.md)) |

After round 1, the owner accepted the repairs and D8–D13 on 2026-10-23 (o).
The accepted disposition is commit `642cade`.

After round 2:
- the owner confirmed D12's reading (o);
- the owner directed repairs P-1..P-9 as r3, with no further review round (o);
- review stopped by its declared rule.

**r3 bytes carry no review opinion.** No approval digest exists.

Change tags:
- `(p1)` marks r2 changes made in response to round 1.
- `(p2)` marks r3 changes made in response to round 2. These apply P-1, P-4,
  P-5, P-8 and the IK1 rows of P-9.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK1-C1 optional 1–512-char description; twins identical; boundary exits | plan §4 IK1; IK-O1; IK-R4 | §6 schema; T1, T2 |
| IK1-C2 renders escaped and untruncated in verbalization, extraction vocabulary and codegen docstrings; projection unchanged | plan §4; IK-R5; R2-F1, R2-F3 (p1); C2-F1/C4-F2 (p2) | §6 renderers, escaping; T3–T6, T13 |
| IK1-C3 vocabulary digest ignores description; diff v2 only with annotations; both diff schemas | plan §4; D11, D12 (o); R2-F2, R2-F5, R3-F2 (p1); C2-F2 (p2) | §6 anchors, diff; T8, T10, T11, T12 |
| IK1-C4 outputs unchanged against digests captured at IK1's base commit | plan §4; IK-R3; C3-F1/C4-F1, C4-F3 (p2) | §6 baseline capture; T7 |
| IK1-C5 evolve `annotation` surface validates; references updated (review-checked) | plan §4; R2-F4, R3-F8 (p1); C2-F3, C4-F4 (p2) | §6 evolve, references; T9 |
| Request-2 fallback if PR #35 is unmerged at this spec's gate | plan IK-O2 | §7 IK1-D4 |
| No model version bump | plan D1 | §6 schema |
| Standing rules 1–6 | process-phase standing rules; IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |

## 4. Standing rules bound to IK1

| Rule | Application |
|---|---|
| 1 Totality | No new loader. The existing total model loader with schema validation is the only gate, and renderers read validated models. Hostile strings are tested in T3 and T5. |
| 2 Input cap vs algorithm | The schema caps descriptions at 512 characters. Escaping is linear, and its output is at most 512 × the longest escape sequence (` `, 6 characters) = 3,072 characters per description (p2). A work counter adds nothing beyond that, so the rule is argued inapplicable. |
| 3 Validation order | Unchanged: schema validation precedes all rendering. Diff still checks vocabulary identity before any row computation. |
| 4 One walk | One escape walk serves both the capped and uncapped forms (p2). Escape steps 1–2 of `verbalize._neutralize` are factored into `verbalize.neutralize_text(value) -> str`. `_neutralize` calls it and then applies its cap unchanged. Descriptions use `neutralize_text`, so there is no second escaping copy. The codegen delimiter rule is unchanged. |
| 5 One home | Field definition: gnd-orm-core `representation-format.md`. Diff wire: `diff.schema.json`; the `report.schema.json` embedded copy yields to it and T10 holds them identical. Surfaces: `evolution-contract.md`. Vocabulary-digest composition: `representation-format.md` §272, with `constraint-reference.md:47` citing it (p2). |
| 6 Measurement | Byte identity for the absent case is decided by T7 against digests captured at IK1's base commit with the commands in §6, not by argument (p2). |

## 5. Goal

`gnd validate` exits 0 for a model whose object types carry a `description` of 1
or 512 characters. It exits 3 for an empty, non-string or 513-character value.

The description appears escaped and **untruncated**, including when it contains
escapable characters (p2), in three places:
- model verbalization;
- the constraint-blind extraction vocabulary;
- generated tool docstrings.

`gnd diff` of two models that differ only in a description:
- exits as it does for identical models;
- emits `schema_version: "gnd-diff/2"` with an `annotations` list, valid against
  both diff schemas.

`gnd evolve preview` lists the change on surface `annotation`.

For every fixture named in T7, each output listed there hashes to the SHA-256
captured at IK1's base commit (p2).

## 6. Design

**Schema** (`src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, copied
to `src/gnd/schema/orm-meta.schema.json`; ~6 lines). Added to
`$defs/object_type.properties`:

```json
"description": {
  "type": "string",
  "minLength": 1,
  "maxLength": 512,
  "description": "Optional free-text explanation of what one instance of this object type is. Rendered, never interpreted. See representation-format.md."
}
```

There is no `allOf` version gate. The 512 cap bounds input (p2). It does **not**
guarantee that `_neutralize` leaves a description unelided: `_neutralize`
escapes before capping, so `_neutralize("'" * 300)` elides (C2-F1).
Descriptions are therefore rendered with `neutralize_text`, escaped and never
capped.

**Escaping** (`verbalize.py`, ~10 lines) (p2):

```python
def neutralize_text(value: Any) -> str:
    """Escape untrusted text exactly as _neutralize does, without the length cap."""
```

`_neutralize(value)` becomes `neutralize_text(value)` plus the existing cap and
elision. Its output is byte-identical for every input. If an RF definition-body
pin covers `_neutralize`, its successor row is recorded through the existing
`source-successors.json` mechanism, with a reason citing IK1.

**Model verbalization** (`model_verbalization.py::_object_type_cnl`, ~4 lines):
- When present, append ` Description: '<neutralize_text(text)>'.`
- The existing `canonical=` field already carries the raw JSON. The duplication
  is intended: `canonical` is the machine identity, the sentence is for readers.
- When absent, the output is unchanged.

**Extraction vocabulary** (`src/gnd/vocabulary.py::render_verbalization`, ~6 lines):
- When present, append one `neutralize_text` line after the object type's
  sentence.
- The list of read keys lives in the compatibility shim's docstring,
  `src/gnd/extract/vocabulary.py:3–10`; it gains `description` (p2, C2-F4).
- The vocabulary stays constraint-blind.
- `extract/projection.py` and `_ALLOWED_KEYWORDS` are **not changed**.

**Codegen** (`codegen/docstrings.py`, ~10 lines):
- For each role line whose object type has a description, append
  ` — <neutralize_text(description)>` inside the existing `'''` delimiter.
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

The digest is unchanged for every model without descriptions. Consequence
(p2, C1-F5): the vocabulary digest no longer identifies the rendered vocabulary
text, so an extraction sidecar stays bound when only a description changes.
This is intended and pinned by T11.

**Diff** (`diff.py`, `api.py`, `diff.schema.json`, `report.schema.json`,
`diff.reference.md`; ~45 lines) (D12 (o)):
- `diff_models` computes `annotations = [{object_type, before, after}]`, where
  `before` and `after` are a string or `null`, for each object type whose
  description differs.
- **Empty `annotations`:** the payload is byte-identical to today, including the
  existing `"schema_version": "gnd-diff/1",` line, which the RF1 mutation
  `M-SEM-diff-schema` anchors.
- **Non-empty `annotations`:** the payload uses `schema_version = DIFF_SCHEMA_V2`,
  defined on its own line as `DIFF_SCHEMA_V2 = "gnd-diff/2"`, and adds
  `annotations`.
- **Schema shape (p2, C2-F2):** `diff.schema.json` keeps its closed top-level
  `properties` and `additionalProperties: false`, and changes as follows:
  - `schema_version` becomes `{"enum": ["gnd-diff/1", "gnd-diff/2"]}`;
  - `annotations` is added as an optional property;
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
  the key is present.
- Add `"annotation"` to the `BlastRadiusEntry.surface` `Literal`, and a contract
  row.

**References** (review-checked, not test-checked — p2, C4-F4):
- `representation-format.md`: the field, and the vocabulary-digest composition at
  line 272, adding `description` to the excluded keys;
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

Estimated size (p2): ~95 source lines, ~300 test lines, ~70 reference lines.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| IK1-D1 | Length cap | **512** (proposed; same order as the neutralizer) vs 2,000 (r1). With escaped, uncapped rendering (p2) either cap is safe; 512 keeps rendered lines short. Both readings exit 3 above their cap. |
| IK1-D2 | Diff wire | Settled by D12, owner-confirmed 2026-10-23 (o): `gnd-diff/2` only with annotations. Emitting v2 always would change every diff's bytes and break RF1 diff pins. |
| IK1-D3 | Also on fact types and roles? | Object types only (proposed, as requested) vs all elements. The broader scope triples renderer work, and it can follow later additively. |
| IK1-D4 (p2, revised) | Base commit B and request 2 | Proposed: B is `main` after PR #35's disposition, named at this gate. Alternative: fold #35 into IK1, which enlarges IK1's frozen-pin surface. Either way T7 uses B, so no correct implementation fails T7 because of #35. |

## 8. Tests

| ID | File / case | Expected |
|---|---|---|
| T1 | `test_schema_sync.py` passes with the edited twins; a new assertion checks `description` exists in both | pass; fails on a no-op |
| T2 | new `test_object_type_description.py`: lengths 1 and 512 exit 0; empty, non-string and 513 exit 3. The 1 and 512 cases discriminate, since today's schema rejects all five | 0, 0, 3, 3, 3 |
| T3 | model verbalization, vocabulary and docstring each contain the full description with no elision marker, for (a) plain 512 characters and (b) 512 characters of `'`, `\n` and U+2028 (p2) | pass; a capped renderer fails (b) |
| T4 | codegen docstring contains the description inside `'''` | pass |
| T5 | a hostile description (`'`, `'''`, `\n`, U+2028, 512-char mix) cannot break delimiters or forge lines in verbalization, vocabulary or docstring | pass |
| T6 | `render_verbalization` output contains the description line. The `audit_allowlist` assertion is a non-regression guard only, not a discriminator (p2) | pass |
| T7 | rows 1–7 of the §6 baseline table equal `ik1-baseline.json` for every F (p2) | pass; a seeded change that emits `annotations: []` for undescribed models fails |
| T8 | `gnd diff` of two models differing only in a description: exit equals the identical-model exit; `schema_version` is `gnd-diff/2`; `annotations` holds the one add/change/remove; the payload validates against `diff.schema.json`; `annotations` survive `applied` redaction | exit as identical; pass |
| T9 | evolve preview of a description-only modify lists an `annotation` entry that validates in `BlastRadiusEntry`; a model without descriptions lists no `annotation` surface | exit 0 |
| T10 | `report.schema.json` `$defs.diff_reference_report` equals `diff.schema.json` modulo `$id`/title; a reference-population diff with `annotations` validates; `tests/test_conformance_payload.py` passes unchanged (p2) | pass |
| T11 | `vocabulary_digest` is equal with and without a description, and unchanged for all T7 fixtures. A comment names the intended consequence: the digest does not identify the vocabulary text (p2) | pass |
| T12 | RF1 mutation table: `M-SEM-diff-schema` still matches its `old` text exactly once and is still killed | pass |
| T13 (p2) | `_neutralize(x)` equals the capped `neutralize_text(x)` byte for byte on the existing neutralizer test inputs | pass |

Criterion ↔ test mapping (p2):

| Criterion | Tests |
|---|---|
| C1 | T1, T2 |
| C2 | T3, T4, T5, T6, T13 |
| C3 | T8, T10, T11, T12 |
| C4 | T7, T11 |
| C5 | T9 (surface); the reference clause is review-checked only |

Every test maps back to at least one criterion.

## 9. Out of scope for this phase

- descriptions on fact types, roles or constraints;
- any use of descriptions by the checker;
- changes to the projection schema or its allowlist;
- model version changes;
- induced provenance (IK2).

## 10. Size

Estimate (p2): ~95 source lines, ~300 test lines, ~70 reference lines. Measured
at record time.

## 11. Approval instrument

This prose. The change is additive, and its one conditional wire version (D12)
is given as literal schema text above, so a fixture corpus first is not
proposed. T7's baseline file is committed at base commit B before any code
(IK-R12).
