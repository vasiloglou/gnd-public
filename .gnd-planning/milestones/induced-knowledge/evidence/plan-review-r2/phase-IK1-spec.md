# IK1 — Object-type descriptions

## 1. Status

**r2 (p1), awaiting confirmation round, plan approval, D1 and the IK1 owner gate.**
Not implementable until all four have happened.

## 2. Provenance

This spec derives from plan r2, §§0–10, at inspection baseline `a22ccde`.
- Source request: [issue #34](https://github.com/vasiloglou/gnd-public/issues/34), request 1.
- r1 (SHA-256 `f79d6375…cec0`) was reviewed in plan-review round 1. See the
  [disposition](plan-review-r1-disposition.md).
- The owner accepted the proposed repairs and D8–D13 on 2026-10-23 (o).
- This r2 applies findings R2-F1..F5, R3-F2, R3-F3, R3-F7, R3-F8, R4-F7, R4-F8
  and R4-F9. Changed sites carry `(p1)`.
- **r2 bytes carry no review opinion** until the confirmation round reports.
- No approval digest exists.

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK1-C1 optional 1–512-char description; twins identical; boundary exits | plan §4 IK1; IK-O1; IK-R4 | §6 schema; T1, T2 |
| IK1-C2 renders in verbalization, extraction vocabulary, codegen docstrings, untruncated; projection unchanged | plan §4; IK-O1; IK-R5; R2-F1, R2-F3 (p1) | §6 renderers; T3–T6 |
| IK1-C3 vocabulary digest ignores description; diff v2 only with annotations; both diff schemas | plan §4; D11, D12; R2-F2, R2-F5, R3-F2 (p1) | §6 anchors, diff; T8, T10 |
| IK1-C4 pinned `a22ccde` digests unchanged for named fixtures across seven outputs | plan §4; IK-R3; R3-F3, R4-F7, R4-F8 (p1) | §6 baseline capture; T7 |
| IK1-C5 evolve `annotation` surface validates; references updated | plan §4; R2-F4, R3-F8 (p1) | §6 evolve, docs; T9, T11 |
| Request-2 fallback if PR #35 is unmerged at this spec's gate | plan IK-O2 (p1) | §7 IK1-D4 |
| No model version bump | plan D1 | §6 schema; §7 |
| Standing rules 1–6 | process-phase standing rules; IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |

## 4. Standing rules bound to IK1

| Rule | Application |
|---|---|
| 1 Totality | No new loader. The existing total model loader with schema validation is the only gate, and renderers read validated models. Hostile strings tested in T5. |
| 2 Input cap vs algorithm | Schema caps the description at 512 characters, and every renderer is linear in its length. A work counter adds nothing beyond T5's 512-character case, so this rule is argued inapplicable (p1). |
| 3 Validation order | Unchanged: schema validation precedes all rendering; diff still checks vocabulary identity before any row computation. |
| 4 One walk | Neutralization reuses `verbalize._neutralize` and the codegen delimiter rule; no per-surface escaping copy. |
| 5 One home | Normative field definition: gnd-orm-core `representation-format.md` (edited in this phase, p1). Diff wire: `diff.schema.json`. The `report.schema.json` embedded copy yields to it and is held identical by new test T10. Surfaces: `evolution-contract.md`. |
| 6 Measurement | Absent-case byte identity is decided by T7 against digests captured at `a22ccde`, not by argument (p1). |

## 5. Goal

`gnd validate` validates a model whose object types carry a `description`:
- it exits 0 when the description is 1 or 512 characters long;
- it exits 3 when the description is empty, a non-string, or 513 characters long.

The description appears neutralized and untruncated in three places:
- model verbalization;
- the constraint-blind extraction vocabulary;
- generated tool docstrings.

`gnd diff` of two models that differ only in a description behaves as follows:
- it exits as it does for identical models;
- it emits `schema_version: "gnd-diff/2"` with an `annotations` list;
- both diff schemas validate the result.

`gnd evolve preview` lists the change on surface `annotation`.

For every fixture named in T7, the SHA-256 of each output listed there equals the
value captured at `a22ccde`.

## 6. Design

**Schema** (`src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, copied
to `src/gnd/schema/orm-meta.schema.json`; ~6 lines), added to
`$defs/object_type.properties`:

```json
"description": {
  "type": "string",
  "minLength": 1,
  "maxLength": 512,
  "description": "Optional free-text explanation of what one instance of this object type is. Rendered, never interpreted. See representation-format.md."
}
```

The cap of 512 equals `verbalize.MAX_RENDERED_VALUE_CHARS`, so `_neutralize`
never elides a description (p1). There is no `allOf` version gate.

**Model verbalization** (`model_verbalization.py::_object_type_cnl`, ~4 lines).
- When a description is present, append ` Description: '<_neutralize(text)>'.`
  to the sentence. The existing `canonical=` field already carries the raw JSON;
  that duplication is intended, because `canonical` is the machine identity and
  the sentence is for readers (p1).
- When absent, the output is unchanged.

**Extraction vocabulary** (`src/gnd/vocabulary.py::render_verbalization`,
~6 lines) (p1).
- When a description is present, append one neutralized line after the object
  type's sentence. The module docstring's list of read keys gains `description`.
- The vocabulary stays constraint-blind: a description is not a constraint.
- `extract/projection.py` and `_ALLOWED_KEYWORDS` are **not changed**.

**Codegen** (`codegen/docstrings.py`, ~10 lines). For each role line whose object
type has a description, append ` — <_neutralize(description)>` inside the existing
`'''` delimiter. When absent, the output is unchanged.

**Vocabulary digest** (`anchors.py::vocabulary_digest`, ~3 lines) (p1, D11):

```python
"object_types": [
    {key: value for key, value in item.items() if key != "description"}
    for item in objects
]
```

- For any model without descriptions the projection is equal, so every existing
  digest is unchanged.
- The digest is shared with `extract/anchors` and the `api.py` diff path; both
  inherit this.

**Diff** (`diff.py`, `api.py`, `diff.schema.json`, `report.schema.json`,
`diff.reference.md`; ~45 lines) (p1, D12).
- `diff_models` computes `annotations = [{object_type, before, after}]`, with
  `before`/`after` being a string or `null`, for each object type whose
  description differs.
- When `annotations` is empty, the payload is byte-identical to today, including
  the existing `"schema_version": "gnd-diff/1",` line. The RF1 mutation
  `M-SEM-diff-schema` anchors that exact text, so the line stays as-is.
- When `annotations` is non-empty, the payload is built with
  `schema_version` = module constant `DIFF_SCHEMA_V2 = "gnd-diff/2"`, defined on
  its own line, plus `annotations`.
- `diff.schema.json` becomes a `oneOf` of two closed shapes: v1, unchanged, and
  v2 = v1 + required `annotations`. `report.schema.json`
  `$defs.diff_reference_report` changes identically.
- The redaction `kind == "diff"` branch (`redaction.py`) redacts only
  population data (offending facts, witnesses, derivation tuples). It is not
  edited. `annotations` carry model text and pass through unredacted, like the
  rest of the model-derived diff content. T8 pins that pass-through in
  `applied` mode.
- `diff.reference.md` documents v2.

**Evolve** (`evolve/service.py::_surface_index`, `evolve/models.py`,
`skills/gnd-model-evolve/references/evolution-contract.md`; ~8 lines) (p1).
- Add surface `object_types[<id>].description` of kind `annotation`, **only when
  the key is present**.
- Add `"annotation"` to the `BlastRadiusEntry.surface` `Literal`.
- Add a row to the contract's surface list.

**References** (p1). Update these, as the one home of the field and its
consumer notes:
- `representation-format.md` (field definition);
- `verbalization-patterns.md` (sentence form);
- the gnd-extract skill reference that lists vocabulary content.

**Baseline capture** (p1). Before the first code change, the implementer runs
the pinned commands at `a22ccde`. The resulting SHA-256 values are committed in
`tests/fixtures/induced_knowledge/ik1-baseline.json`. That commit is the
approved-spec commit's companion, and the values are never regenerated from
changed code.

Estimated size (p1, re-estimated): ~85 source lines, ~260 test lines, ~60
reference lines.

## 7. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| IK1-D1 (p1, revised) | Length cap | **512** (proposed, matches the neutralizer) vs 2,000 (r1). With 2,000, rendered text is silently truncated at 512 (R2-F3). Both readings exit 3 above their cap. |
| IK1-D2 (p1) | Diff wire | Settled by D12 (o): v2 only with annotations. The alternative of always emitting v2 would change every existing diff's bytes and break RF1 diff pins. |
| IK1-D3 | Also on fact types and roles? | Object types only (proposed, as requested) vs all elements. Broader scope triples renderer work; it can follow later additively. |
| IK1-D4 (p1) | Request 2 fallback | If PR #35 is unmerged at this spec's gate, either merge it first (proposed) or fold its two commits into IK1. Folding enlarges IK1's frozen-pin surface. Exit codes are the same either way. |

## 8. Tests

| ID | File / case | Expected |
|---|---|---|
| T1 | `test_schema_sync.py` passes with edited twins, and a new assertion that `description` exists in both | pass; fails on a no-op change (p1) |
| T2 | new `test_object_type_description.py`: lengths 1 and 512 → `gnd validate` exit 0. Empty, non-string, 513 → exit 3. The 1- and 512-character cases are the discriminators, since today's schema rejects every case (p1) | 0, 0, 3, 3, 3 |
| T3 | model verbalization contains the 512-char description in full, with no elision marker (p1) | pass |
| T4 | codegen docstring contains it inside `'''` | pass |
| T5 | hostile description cannot break delimiters or forge lines in verbalization, vocabulary or docstring. Hostile cases: `'`, `'''`, `\n`, U+2028, and a 512-character mix (p1) | pass |
| T6 | `render_verbalization` output contains the description line. `audit_allowlist` over the unchanged projection still passes for a described model (p1) | pass |
| T7 | for `tests/fixtures/models/{full_vocabulary,library,keywords,v2_worked_example}.orm.yaml`, the SHA-256 of seven outputs equals `ik1-baseline.json`. The outputs: model verbalization, `render_verbalization`, extraction projection, codegen tree manifest, conformance payload, `gnd diff` of the model with itself, and `gnd evolve preview` of the `evolution-safe-additive` case in `tests/fixtures/phase4_reference/evolution.json` (p1) | pass; a seeded change that emits `annotations: []` for undescribed models fails |
| T8 | `gnd diff` of two models differing only in a description: exit equals the identical-model exit; `schema_version` is `gnd-diff/2`; `annotations` holds the one add, change or remove; the payload validates against `diff.schema.json` (p1) | exit as identical; pass |
| T9 | evolve preview of a description-only modify lists an `annotation` entry that validates in `BlastRadiusEntry`. A model without descriptions lists no `annotation` surface (p1) | exit 0 |
| T10 (p1) | `report.schema.json` `$defs.diff_reference_report` equals `diff.schema.json` modulo `$id`/title, and a reference-population diff with `annotations` validates | pass |
| T11 (p1) | `vocabulary_digest` equal with and without a description; unchanged for all T7 fixtures | pass |
| T12 (p1) | RF1 mutation table: `M-SEM-diff-schema` still applies (exactly one `old` match) and is still killed | pass |

Every criterion maps to tests:

| Criterion | Tests |
|---|---|
| C1 | T1, T2 |
| C2 | T3–T6 |
| C3 | T8, T10, T11 |
| C4 | T7, T11 |
| C5 | T9, T12, plus reference diffs in the review |

Every test maps back to at least one criterion.

## 9. Out of scope for this phase

- descriptions on fact types, roles or constraints;
- any use of descriptions by the checker;
- changes to the projection schema or its allowlist (p1);
- model version changes;
- induced provenance (IK2).

## 10. Size

Estimate (p1): ~85 source lines, ~260 test lines, ~60 reference lines. Measured
at record time.

## 11. Approval instrument

This prose. The change is additive, with one conditional wire version (D12)
whose shape is given as literal schema text above, so writing a fixture corpus
first is not proposed. T7's baseline file is committed before code under IK-R12.
