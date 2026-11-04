# Anchor sidecars

An anchor sidecar binds one population to one source document. Each anchor
says where in the document a role value of one fact can be found. `gnd check
--anchors PATH --document PATH` and `gnd verify` read it to evaluate
`anchored` constraints.

An anchor binds a value to a range of text, nothing more. Neither GND nor the
caller claims that the range entails the fact. Several anchors on one role add
evidence for it; none of them proves it.

The parser, `gnd.anchors.parse_anchor_sidecar`, is the authority for this
format. [`anchor-sidecar.schema.json`](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/anchor-sidecar.schema.json)
describes the part a JSON Schema can express, and a test keeps the two in
step.

## The file

The sidecar sits next to its population as `<population>.anchors.json`:

```json
{
  "schema_version": 2,
  "population_sha256": "<SHA-256 of the population file's raw bytes>",
  "vocabulary_digest": "<digest of the model's vocabulary>",
  "document_sha256": "<SHA-256 of the document's raw bytes>",
  "anchors": [
    {
      "fact_key": {"fact_type": "record_has_label", "roles": {"record": "R-1", "label": "Café Alpha"}},
      "role": "label",
      "span": {"start": 27, "end": 37},
      "occurrence": 0,
      "excerpt_sha256": "<SHA-256 of the UTF-8 bytes of the NFC document slice>"
    }
  ]
}
```

- `fact_key` names one fact by its fact type and every role value.
- `role` is the role whose value the anchor points at.
- `span` is a half-open range of Unicode code points in the NFC-normalized
  document.
- `occurrence` counts matches of the value from zero across the whole
  document; the selected match must lie wholly inside the span.
- `block_id` and `unit_id` are optional, non-empty labels for your own use.

`vocabulary_digest` is the canonical JSON digest of the model's object types
and fact types, leaving out object type descriptions and each fact type's
derivation rule, constraints, sample population and dependencies. The
[constraint reference](https://github.com/vasiloglou/gnd-public/blob/main/src/gnd/skills/gnd-orm-core/references/constraint-reference.md)
gives the matching rules.

## Versions 1 and 2

The two versions have the same keys and still bind one population to one
document. They differ in which anchors count as the same:

| Version | One anchor is identified by | Refused when repeated |
|---|---|---|
| 1 | fact key and role | `duplicate fact-role anchor`: one anchor per fact role |
| 2 | fact key, role, span start and end, occurrence | `duplicate anchor`: several anchors per fact role are allowed |

In version 2, the same range with a different `excerpt_sha256` is still a
duplicate: one range has one excerpt. `gnd extract` writes version 1.

## When a role with several anchors passes

Every anchor on the role must hold: the value's selected occurrence must lie
inside the anchor's span. Each anchor is a claim about the
document, so one wrong anchor fails the role even when another is right. The
failed fact is reported once per role, however many of its anchors fail. The
order of anchors in the file does not change the result.

## What the parser refuses

A malformed sidecar exits 3 with `anchor:sidecar-invalid`. Besides the shape
the schema describes, the parser refuses:

| Rule | Example |
|---|---|
| A repeated anchor identity (per version, above) | the same anchor twice |
| `start` not below `end` | `{"start": 5, "end": 5}` |
| A file over 1 MiB | about 3,500 anchors fit |
| Duplicate JSON keys | `"schema_version"` twice |
| `NaN`, `Infinity` or a number too large for a float | a role value `NaN`, `1e400` |
| Integer literals over 18 characters, sign included | an occurrence of `10**18` |
| Nesting deeper than 32 | |
| Integer-valued floats where integers are required | `"start": 27.0` |
| Invalid UTF-8 | |

A sidecar whose digests do not match the population, the document or the
model, or whose excerpt does not match its span, is refused before any value
is checked, also exit 3. This digest match is the binding; whether each value
is found inside its span is the `anchored` verdict, which can fail (exit 1).
