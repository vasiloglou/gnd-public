# The rendering contract

Normative reference for [`../SKILL.md`](../SKILL.md). Every obligation below is discharged by `gnd doccheck` over the manifest — this file restates the contract, it does not create it.

## 1. The two files you write

| Path | Content | Loaded by |
|---|---|---|
| `document.md` | the rendered prose document | `gnd doccheck` (read for mention and distractor checks) |
| `document.manifest.json` | the document manifest (§2) | `gnd doccheck`, strictly, before any obligation is checked |

Paths inside the manifest resolve against the **manifest's own directory**. Keep the document, the source population and the manifest in one case directory and every path is a bare filename.

## 2. Manifest fields

Every field is REQUIRED. The loader forbids unknown fields (an unexpected key is a rejection naming the key), requires every digest, and refuses any path that is absolute or contains `..` — under both POSIX and Windows path rules, because this file crosses machines. Reads are byte-capped.

| Field | Type | Value |
|---|---|---|
| `schema_version` | integer | `1` |
| `document` | string | RELATIVE path to the rendered document (typically `document.md`) |
| `document_sha256` | string | `shasum -a 256` of the document bytes |
| `model` | string | the model reference as an opaque ID string — recorded, never dereferenced |
| `model_sha256` | string | `shasum -a 256` of the model file |
| `source_population` | string | RELATIVE path to the population you rendered (typically `source.population.json`) |
| `source_population_sha256` | string | `shasum -a 256` of the population bytes |
| `applicable_sha256` | string | `shasum -a 256` of `<stem>.applicable.json`; also readable from `<stem>.artifacts.json` |
| `renderer_skill` | string | `gnd-render-doc` |
| `renderer_skill_version` | string | the version of this skill you are running |
| `executing_model` | string | your own model ID string, truthfully — the full identifier the runtime reports, never a family label |
| `distractors` | array | one entry per planted distractor (§3); all three kinds required |

Shape:

```json
{
  "schema_version": 1,
  "document": "document.md",
  "document_sha256": "…",
  "model": "full_vocabulary.orm.yaml",
  "model_sha256": "…",
  "source_population": "source.population.json",
  "source_population_sha256": "…",
  "applicable_sha256": "…",
  "renderer_skill": "gnd-render-doc",
  "renderer_skill_version": "1",
  "executing_model": "…",
  "distractors": [
    { "kind": "out-of-model", "text": "The offsite was rained out." },
    { "kind": "near-miss-entity", "text": "a note from Ada Lovelacé in facilities" },
    {
      "kind": "absent-fact",
      "text": "There was talk of putting Grace on the glass project.",
      "fact_type": "employee_works_on_project",
      "roles": { "employee": 140892, "project": "glass" }
    }
  ]
}
```

**The digest IS the binding.** `doccheck` recomputes `document_sha256`, `source_population_sha256` and `applicable_sha256` from the actual bytes and compares. Digest every file after its last write, then write the manifest.

`applicable_sha256` binds the applicable-set artifact you honoured, so the obligation is enforced over the **same scope** you were given. A manifest bound to a different applicable set is a mismatch, not a courtesy.

## 3. The distractor vocabulary

The kind vocabulary is CLOSED. A kind outside this set is rejected when the manifest loads, not when the check runs.

| `kind` | Required extra fields | What `doccheck` verifies |
|---|---|---|
| `out-of-model` | — | `text` appears in the document |
| `near-miss-entity` | — | `text` appears in the document |
| `absent-fact` | `fact_type`, `roles` | `text` appears in the document AND the named fact is genuinely absent from the source population under the matcher's identity rules |

- `text` is the exact wording you wrote into the document. `doccheck` looks it up; a recorded distractor that was never written is a violation, and a planted distractor that was never recorded is invisible to every reader of the manifest.
- `roles` maps role name → value, using the same role names the fact type declares.
- An `absent-fact` entry without `fact_type` AND `roles` **fails to load**. The obligation is that absence is *proved*, and a distractor that cannot be checked is an unverified claim about your own output.

At least one of each kind, in every document. This is not a quality target; it is the condition under which precision can come out below 1.0 at all. A stub extractor that emits every entity it sees must lose precision on your document — that is the mutation check this rule exists to satisfy.

## 4. The mention obligation

For every fact type with `applicable: true`, every role filler in the source population must be mentioned in the document by its reference value, under **lexical** normalization only: case folding and whitespace collapse. Nothing semantic, no fuzzy matching, no aliases.

| Reference path | What must appear |
|---|---|
| `direct` | the reference value itself (`140891`, `glass`, `2026-08-13`) |
| `composite` | the identifying component values, together — the components are listed in the object type's `role_refs` |
| `unmatchable` | nothing; the fact type is `applicable: false` and exempt |

The `object_types` rows of `<stem>.applicable.json` tell you which path each object type takes and, for composites, which `(fact_type, role)` pairs identify it. Read them rather than inferring.

Inapplicable fact types stay listed in the artifact with a `reason` naming the mechanism — an exemption you can read, not a silence. On the primary fixture model exactly one of sixteen fact types is inapplicable, because its object type's reference is unit-based with no anchoring external uniqueness constraint, so no reference value exists to render or match.

## 5. `doccheck` obligations and what each violation means

| Obligation | Violation looks like | Repair |
|---|---|---|
| 1. binding | a recorded digest does not match the file bytes | recompute after the last write and rewrite the manifest |
| 2. rendering | a named entity of an applicable fact type is not mentioned | add the reference value to the prose — verbatim, not paraphrased |
| 3. distractors | a kind is missing, a recorded `text` is not in the document, or an `absent-fact` is actually present in the population | plant the missing kind, write the recorded text, or pick a fact that is genuinely absent |
| 4. renderer identity | `renderer_skill`, `renderer_skill_version` or `executing_model` is empty | fill it truthfully |

Exit 66 means the applicable-set artifact or a manifest-named file could not be found. It is deliberately outside the 0-4 verdict bands: a missing input is not a verdict, and an obligation that cannot be checked is never skipped.

## 6. What is out of scope

- **Editing the source population** to make an obligation pass. The population is the input and the ground truth. If it cannot be rendered, that is a finding about the model or the population and it belongs in your report.
- **Reading `model.orm.yaml`.** The constraint-blind verbalization is the renderer's only model context, so a document cannot silently repair a violation the population carries.
- **Templates.** See the rule at the top of [`../SKILL.md`](../SKILL.md): a templated document measures the template.
- **Unbounded retrying.** Three `doccheck` attempts, then an honest report of what still fails.
- **Cross-family rendering and the same-family delta** (rendering with one model family and extracting with another to bound self-consistency inflation) — deferred; it is a meta-measurement, and the fidelity payload already declares itself uncalibrated.

When explicitly selected, saved source opinions use the separate [judgment contract](../../gnd-dev-session/references/judgment-contract.md); source hashes do not establish truth or grant assurance.
