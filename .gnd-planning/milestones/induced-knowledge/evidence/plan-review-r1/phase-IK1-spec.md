# IK1 — Object-type descriptions

**Status: awaiting owner review; blocked on plan approval and D1, IK1-D1..D3.**

## 1. Provenance

Derived from draft r1 of [the plan](induced-knowledge-plan.md), §§0–10, at
inspection baseline `a22ccde`. Source request: [issue #34](https://github.com/vasiloglou/gnd-public/issues/34),
request 1. No review has run; no approval digest exists. The start-milestone
request authorizes planning only.

## 2. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK1-C1 optional bounded description; schema twins identical; invalid values exit 3 | plan §4 IK1; IK-O1; IK-R4 | Design: schema; T1, T2 |
| IK1-C2 verbalization, codegen docstrings, extraction projection render it, neutralized | plan §4; IK-O1; IK-R5 | Design: renderers; T3–T6 |
| IK1-C3 absent ⇒ byte-identical outputs | plan §4; IK-O12; IK-R3 | T7 |
| IK1-C4 diff reports changes; evolve indexes and previews | plan §4; IK-O1 | Design: diff, evolve; T8, T9 |
| No model version bump | plan D1 | Design: schema; IK1-D1 |
| Standing rules 1–6 | process-phase standing rules; IK-R9 | §4 |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |

## 3. Goal

`gnd validate` exits 0 for a model whose object types carry a `description`
string of 1–2,000 characters and exits 3 for an empty, non-string or over-long
one. The description appears, neutralized, in model verbalization, in generated
tool docstrings and in the extraction projection; `gnd diff` and
`gnd evolve preview` report its changes. Every committed fixture without a
description renders byte-identically.

## 4. Standing rules bound to IK1

| Rule | Application |
|---|---|
| 1 Totality | No new loader. Schema validation (existing total model loader) is the only gate; renderers read only validated models. Hostile strings tested in T5. |
| 2 Input cap vs algorithm | Description is length-bounded by schema; rendering is linear in length. No time-bound test needed beyond T5's 2,000-char case; argued inapplicable otherwise. |
| 3 Validation order | Unchanged: schema validation precedes all rendering. |
| 4 One walk | Neutralization reuses `verbalize._neutralize` (verbalization, projection) and the codegen delimiter rule; no per-surface escaping copy. |
| 5 One home | Normative field definition: gnd-orm-core `representation-format.md`; schema description cites it. |
| 6 Measurement | Byte-identity of absent case decided by T7 against committed fixtures, not argument. |

## 5. Design

**Schema** (`src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, copied
to `src/gnd/schema/orm-meta.schema.json`; ~6 lines):

```json
"description": {
  "type": "string",
  "minLength": 1,
  "maxLength": 2000,
  "description": "Optional free-text explanation of what one instance of this object type is. Rendered, never interpreted."
}
```

added to `$defs/object_type.properties`. No `allOf` version gate.

**Model verbalization** (`model_verbalization.py::_object_type_cnl`, ~4 lines):
when present, append ` Description: '<neutralized text>'.` to the object type's
sentence. Absent ⇒ unchanged string.

**Codegen** (`codegen/docstrings.py`, ~10 lines): for each role line whose object
type has a description, append ` — <neutralized description>` inside the
existing `'''` delimiter. Absent ⇒ unchanged.

**Extraction projection** (`extract/projection.py`, ~4 lines): when present,
set `"description"` on that object type's `instance_properties` entry.

**Diff** (`diff.py`, ~25 lines, plus `diff.schema.json`): a new optional
`annotations` list `[{object_type, before, after}]`, emitted only when some
description differs. Semantically neutral: it never changes the existing
implication verdicts or exit codes.

**Evolve** (`evolve/service.py::_surface_index`, ~3 lines): add surface
`object_types[<id>].description` of kind `annotation`.

Estimated size: ~55 source lines, ~150 test lines.

## 6. Decisions

| ID | Question | Readings and cost |
|---|---|---|
| IK1-D1 | Length cap | 2,000 chars (proposed) vs unbounded. Unbounded lets one model inflate every prompt and docstring; exit code differs (3 vs 0) for long text. |
| IK1-D2 | Diff placement | New `annotations` section (proposed) vs no diff support. Without it, request 1's "carried by diff" is unmet. Neither changes diff exit codes. |
| IK1-D3 | Also on fact types and roles? | Object types only (proposed, as requested) vs all elements. Broader scope triples renderer work; can follow later additively. |

## 7. Tests

| ID | File / case | Expected |
|---|---|---|
| T1 | `test_schema_sync.py` unchanged passes with edited twins | pass |
| T2 | new `test_object_type_description.py`: valid, empty, non-string, 2,001-char | `gnd validate` exit 0, 3, 3, 3 |
| T3 | verbalization includes neutralized description | pass |
| T4 | codegen docstring includes it inside `'''` | pass |
| T5 | hostile description (quotes, `'''`, newlines, U+2028) cannot break delimiters in verbalization, projection or docstring | pass |
| T6 | extraction projection carries `description` | pass |
| T7 | full-vocabulary and codegen/conformance fixtures without descriptions byte-identical to baseline | pass |
| T8 | diff reports add/change/remove in `annotations`; exit unchanged vs no-description diff | pass |
| T9 | evolve preview of a description-only modify lists the `annotation` surface | exit 0 |

## 8. Out of scope

Descriptions on fact types, roles or constraints; any use of descriptions by
the checker; model version changes; induced provenance (IK2).

## 9. Size

Estimate: ~55 source, ~150 test lines. Measured at record time.

## 10. Approval instrument

This prose. The change is a small additive field with no new wire semantics
beyond one diff section; a fixture corpus first is not proposed.
