# IK2 — Induced provenance and admission

## 1. Status

**r1, awaiting owner review.** No code exists. Nothing in this file is approved.
Implementation starts only after the owner rules on §7 and approves these bytes.

## 2. Provenance

- **Plan:** r4, approved by the owner on 2026-10-24 (SHA-256
  `8afbdcbd…cd51a`, unchanged since approval). This spec expands §2 "Request 6",
  §4 IK2, §9 IK2 row and the IK-R rules.
- **Source request:** [issue #34](https://github.com/vasiloglou/gnd-public/issues/34),
  request 6.
- **Prior phase:** IK1, recorded in [002-phase-IK1.md](../002-phase-IK1.md).
- **Base commit B:** `ebb1f04`, the IK1 record commit on
  `claude/induced-knowledge-plan`, which is PR #36 (open, not merged).
- **Review:** no review has run over these bytes. Plan approval is not approval
  of this spec ([001-plan-gate.md](../001-plan-gate.md)).

## 3. Obligations — inline harvest

| Obligation | Source | Discharge here |
|---|---|---|
| IK2-C1 source kind and required induction block validate; absolute paths and raw values refused; D-03 table updated in one home | plan §4 IK2; IK-O8, IK-O17; IK-R11 | §6 schema, semantic rules, references; T1–T3 |
| IK2-C2 evolve admits new induced constraints only as proposed/deontic, and confirmed only as a reviewed status change; every other combination and `provenance.induction` under other sources refused with a named reason; existing D-12 outcomes pinned unchanged | plan §4; D2, D9 (o); IK-O10, IK-O16; IK-R1 | §6 gate; T4–T9 |
| IK2-C3 coverage lists induced elements with inducer, support and evidence digests; public coverage goldens byte-identical | plan §4; IK-O8; IK-R3 | §6 coverage; T11, T15 |
| IK2-C4 counterexample cap and block size bounds fixed here, with a loader test at each boundary | plan §4; IK-R12 | §6 bounds table; T3 |
| §9 row: "induced admitted only as specified; old D-12 outcomes pinned; coverage goldens unchanged" | plan §9 | T4, T5, T15 |
| No `gold` source kind; a gold-answer origin is the block's `method` | D3 (o) | §6 schema (`method`) |
| D-03 default modality for induced is deontic | plan §2 request 6 | §6 references; IK2-D4 |
| `confidence` only for methods that define it, with its formula named | plan §2 request 6 | §6 schema; IK2-D7 |
| Every inducer output is gated by D-12; no path to confirmed or alethic without `reviewed_in` | IK-R1 | §6 gate, IK2-D2 |
| Learner and host numbers are claims, not trusted inputs | IK-R2 | §6 "What the loader can and cannot check" |
| Additive compatibility, byte identity at B | IK-R3 | T5, T15 |
| One schema home, twins identical | IK-R4 | T1 |
| Bounds before results | IK-R12 | §6 bounds table; IK2-D6 |
| Layer homes, RF6 ceiling, RF6b body pins | IK-R7; AGENTS.md | §6 registration; T14 |
| Privacy of fixtures | IK-R10 | synthetic fixtures only |
| Standing rules 1–6 | IK-R9 | §4 |
| Inherited: IK1-Q1 (description nesting cap) still open | 002-phase-IK1.md | not discharged here; §9 |

The §5 skill-surface row for IK2 names `provenance-and-modality.md` and the D-03
table. The step-0 harvest also found these pin sites, which are counted at
execution time:
- every "six source" phrase (the schema `source_kind` description, the
  provenance reference, the gnd-model-evolve skill and its evolution contract);
- the closed source `Literal`s in `src/gnd/exp/session_eval.py` (two sites);
- the D-03 default copy in `src/gnd/rai_import.py::_default_modality`;
- the D-12 message markers in `src/gnd/evolve/cli_service.py`.

## 4. Standing rules bound to IK2

| Rule | Application |
|---|---|
| 1 Totality | The model loader stays the one gate for model bytes. Its layer-1 screen for values with no JSON form (IK1-F1) is widened to the `provenance.induction` paths, because JSON Schema's `minimum`/`maximum` accept NaN and its `integer` type accepts a ruamel `ScalarBoolean` (T2 cases). `_enforce_d12` reads documents that apply and finalize parse from text, so its new branch must be total: a hostile-input test feeds `provenance` and `induction` as a list, string, integer and null (T8). |
| 2 Input cap vs algorithm | Matching a confirmed candidate to its proposed predecessor is done through a `Counter` keyed by canonical text, not a pairwise scan, so the gate stays linear in the constraint count. A work-counter test bounds canonical renders at 2 × (before + candidate) constraints (T9). The semantic rule is linear in list lengths that the schema caps. |
| 3 Validation order | At preview, schema and semantic validation run before D-12, as today. Inside `_enforce_d12` the order is: audit-key refusal (unchanged), exact-match pass, then `provenance.induction` under another source, then the per-source branches. A source-order test pins it (T7). |
| 4 One walk | The new semantic rules walk `_iter_provenance_bearing`, the same walk every provenance rule uses. The layer-1 screen reuses IK1's predicate through one tuple of screened paths, not a second copy. The modality-policy warning gains `induced` inside the existing rule. |
| 5 One home | The source taxonomy, the induced provenance block, the source/status rule and the D-03 table live in `provenance-and-modality.md`; the schema is the machine spec. The evolve lifecycle bullets in `evolution-contract.md` §6 cite that file. `rai_import._default_modality` is a second copy of the D-03 table; IK2-D9 rules on whether it yields in this phase. |
| 6 Measurement | "Existing D-12 outcomes unchanged" is decided by a table captured at B before any code (T5), not by argument. |

## 5. Goal

`gnd validate` exits 0 for a constraint with `source: induced` whose `provenance`
is `{induction: {...}}` within the §6 bounds, and for a confirmed one that also
carries `provenance.reviewed_in`. It exits 3 when:
- the block is missing, has an unknown key, or has a value outside a bound;
- an example id, counterexample id or evidence ref is an absolute path, contains
  `..`, a backslash or whitespace, or breaks its grammar;
- the support arithmetic is inconsistent;
- a confirmed induced constraint lacks a non-blank `reviewed_in`;
- `source: induced` appears on an operation, precondition or dynamic rule.

`gnd evolve preview` exits 0 for a new induced constraint that is `proposed` and
`deontic` with no `reviewed_in`. It also exits 0 for a status change of an
existing proposed induced constraint to `confirmed` that adds `reviewed_in` and
changes nothing else (modality per IK2-D4). Every other new or changed induced
constraint, and every new or changed constraint carrying `provenance.induction`
under another source, exits 3 with a named reason. Every D-12 outcome recorded at
B is unchanged.

`gnd coverage` lists each induced constraint with its inducer, method, manifest
digest, support and evidence digests under `schema_version` 5 (or 6 when the
model also declares a derivation). Every model without induced constraints emits
exactly what it emits at B.

## 6. Design

### Schema

Home: `src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json`, copied
byte-for-byte to `src/gnd/schema/orm-meta.schema.json`. About 90 lines.

`$defs.source_kind.enum` gains `"induced"`. Its description changes from "The six
provenance sources" to "The seven provenance sources" and names `induced`.

New `$defs` (bounds per IK2-D6; id grammar per IK2-D5):

```json
"induction_token": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._+-]{0,63}$"},
"induction_example_id": {"type": "string", "pattern": "^[A-Za-z0-9][A-Za-z0-9._:#-]{0,63}$"},
"induction_ref": {
  "type": "string", "maxLength": 256,
  "pattern": "^[A-Za-z0-9_][A-Za-z0-9._-]*(/[A-Za-z0-9_][A-Za-z0-9._-]*)*$"
},
"sha256_hex": {"type": "string", "pattern": "^[0-9a-f]{64}$"},
"induction": {
  "type": "object",
  "additionalProperties": false,
  "required": ["inducer", "method", "manifest_sha256", "examples", "support",
               "counterexamples", "evidence"],
  "properties": {
    "inducer": {
      "type": "object", "additionalProperties": false,
      "required": ["name", "version"],
      "properties": {
        "name": {"$ref": "#/$defs/induction_token"},
        "version": {"$ref": "#/$defs/induction_token"}
      }
    },
    "method": {"$ref": "#/$defs/induction_token"},
    "manifest_sha256": {"$ref": "#/$defs/sha256_hex"},
    "examples": {"type": "array", "maxItems": 256, "uniqueItems": true,
                 "items": {"$ref": "#/$defs/induction_example_id"}},
    "support": {
      "type": "object", "additionalProperties": false,
      "required": ["numerator", "denominator"],
      "properties": {
        "numerator": {"type": "integer", "minimum": 0, "maximum": 9007199254740991},
        "denominator": {"type": "integer", "minimum": 1, "maximum": 9007199254740991}
      }
    },
    "counterexamples": {"type": "array", "maxItems": 32, "uniqueItems": true,
                        "items": {"$ref": "#/$defs/induction_example_id"}},
    "evidence": {
      "type": "array", "minItems": 1, "maxItems": 32,
      "items": {
        "type": "object", "additionalProperties": false,
        "required": ["ref", "sha256"],
        "properties": {"ref": {"$ref": "#/$defs/induction_ref"},
                       "sha256": {"$ref": "#/$defs/sha256_hex"}}
      }
    },
    "confidence": {
      "type": "object", "additionalProperties": false,
      "required": ["value", "formula"],
      "properties": {
        "value": {"type": "number", "minimum": 0, "maximum": 1},
        "formula": {"type": "string", "minLength": 1, "maxLength": 256}
      }
    }
  }
}
```

The `induction_ref` grammar refuses, by construction:
- a leading `/` (absolute POSIX path);
- `\` and `:` (Windows paths and drive letters);
- any segment starting with `.`, so `.`, `..` and hidden names;
- whitespace and empty segments.

Two rules are appended to `$defs.provenance_policy.allOf`:

```json
{"if": {"properties": {"source": {"const": "induced"}}, "required": ["source"]},
 "then": {"required": ["provenance"],
          "properties": {"provenance": {
            "type": "object", "additionalProperties": false,
            "required": ["induction"],
            "properties": {
              "induction": {"$ref": "#/$defs/induction"},
              "reviewed_in": {"type": "string", "minLength": 1, "maxLength": 256}}}}}},
{"if": {"properties": {"source": {"const": "induced"}, "status": {"const": "confirmed"}},
        "required": ["source", "status"]},
 "then": {"required": ["provenance"],
          "properties": {"provenance": {"type": "object", "required": ["reviewed_in"]}}}}
```

An induced constraint's `provenance` is closed to `induction` and `reviewed_in`,
so no other provenance key can carry host data (IK-R11).

Under IK2-D2, the `allOf` of `$defs.obligation`, `$defs.dynamic_rule` and
`$defs.operation` each gain
`{"not": {"properties": {"source": {"const": "induced"}}, "required": ["source"]}}`.

### Layer-1 screen

Home: `src/gnd/model/_validation.py`. About 10 lines.

IK1's `_OBJECT_TYPE_DESCRIPTION_PATH` becomes one tuple `_JSON_FORM_SCREENED_PATHS`.
It holds the description pattern and
`re.compile(r"\$\.(?:fact_types\[\d+\]\.)?constraints\[\d+\]\.provenance\.induction(?:[.\[]|$)")`.
The `_layer1_structural` branch tests `any(p.match(path) for p in ...)` and still
calls `_description_value_without_json_form`, renamed `_value_without_json_form`.
The old name stays as an alias, per the AGENTS.md shim rule. Rule id and exit are
unchanged: `jsonschema:type`, exit 3.

### Semantic rules

Home: `src/gnd/model/_validation.py`. About 60 lines.

- **`semantic:induced-provenance`** (error), walking `_iter_provenance_bearing`,
  for `source == "induced"` with a mapping `provenance.induction`:
  1. `support.numerator <= support.denominator`;
  2. `len(examples) <= support.numerator`;
  3. `len(counterexamples) <= support.denominator - support.numerator`;
  4. `examples` and `counterexamples` are disjoint;
  5. no string anywhere in the block contains a whitespace character (`\s`).
     The schema patterns cannot ensure this, because `jsonschema` matches with
     Python `re.search`, whose `$` also matches before a final newline. So
     `"a\n"` passes `^[A-Za-z0-9_][A-Za-z0-9._-]*$` (sweep finding S1, §12).

  Each failed check gives one issue at its own path.
- **`semantic:induced-confirmed-reviewed`** (error) refuses a confirmed induced
  constraint whose `reviewed_in` is whitespace-only. This mirrors
  `semantic:imported-confirmed-reviewed`.
- **`_rule_modality_policy`** also warns for `source == "induced"`,
  `status == "proposed"`, `modality == "alethic"`. The message for `llm-inferred`
  and `common-sense` is unchanged byte for byte (T10). The induced message is:
  `unconfirmed induced {type} constraint carries modality 'alethic' — induced constraints default to deontic until reviewed (D-03)`.
- `_rule_status_source` is unchanged: induced may be proposed or confirmed.

### What the loader can and cannot check (IK-R2, IK-R11)

- **Checked:** shape, bounds, id and ref grammar, and the four support
  inequalities.
- **Not checked:** whether the support numbers, examples or evidence digests are
  true. A model file has no population to recompute them from. In a model, an
  induction block is a **recorded claim**. IK4 and IK5 make GND compute what they
  write, and say so in their records.
- **Residual (IK2-D5):** under the token grammar, a raw value that is a single
  token, such as `alice` or `42`, cannot be told apart from an opaque id. The
  grammar refuses paths, whitespace and separators, which covers names,
  addresses and free text, but not one-word values. The digest-only alternative
  closes this gap at the cost stated in IK2-D5.

### D-12 gate

Home: `src/gnd/evolve/service.py::_enforce_d12`. About 50 lines.

```python
def _enforce_d12(before: dict[str, Any], candidate: dict[str, Any]) -> None:
    # pass 0 (unchanged): audit keys refused for every candidate constraint
    # pass 1: exact canonical matches consume `before` (unchanged multiset rule)
    # pass 2: each unmatched candidate constraint, in candidate order:
    #   a. provenance.induction present and source != "induced"  -> refuse R-I1
    #   b. source == "induced":
    #        proposed/deontic, no reviewed_in                     -> admit
    #        proposed/deontic, with reviewed_in                   -> refuse R-I2
    #        confirmed, non-blank reviewed_in, and an unconsumed
    #          before constraint b with b.source == "induced",
    #          b.status == "proposed", strip(b) == strip(c)       -> consume b; admit
    #        confirmed otherwise                                  -> refuse R-I3
    #        any other status/modality                            -> refuse R-I4
    #   c. llm-inferred / user-supplied / else: the three existing branches, unchanged
```

`strip(x)` is `x` without `status`, without `modality`, and with
`provenance.reviewed_in` removed. Under IK2-D4 = keep-deontic, `modality` is not
stripped. Matching is location-insensitive, as the existing exact-match rule is.
Before-constraints are indexed once as `Counter(canonical_json_text(strip(b)))`
over the proposed induced constraints left unconsumed after pass 1.

Named reasons, all exit 3. Each message contains a marker added to
`cli_service.malformed_markers`, so none falls through to exit 70:

| ID | Message | Marker |
|---|---|---|
| R-I1 | `provenance.induction is allowed only under source induced (D-12)` | `provenance.induction` |
| R-I2 | `new induced constraints cannot carry provenance.reviewed_in (D-12)` | `new induced constraints` |
| R-I3 | `induced constraints become confirmed only as a reviewed status change of an existing proposed induced constraint (D-12)` | `induced constraints become confirmed` |
| R-I4 | `new induced constraints must be proposed/deontic (D-12)` | `new induced constraints` |

A new constraint from discover or import is never a status change, so R-I2
refuses any such output that carries `reviewed_in` (D9). The gate cannot see
which command produced a proposal; this is the enforceable form of that clause.

Under the existing user-supplied branch, an owner may still rewrite an induced
constraint as `user-supplied`/`confirmed` with no `induction` block. That path
drops the marker. It is an owner rewrite, admitted today, and pinned unchanged by
T5. D9's status change is the path that keeps the marker.

### Coverage

Homes: `src/gnd/coverage.py`, `src/gnd/coverage.schema.json`. About 60 lines.

`build_payload` picks the version from two discriminators: has-derivation and
has-induced.

| has-derivation | has-induced | `schema_version` |
|---|---|---|
| no | no | 3 (unchanged) |
| yes | no | 4 (unchanged) |
| no | yes | 5 |
| yes | yes | 6 |

Versions 5 and 6 add one required top-level key, `induced`, a list in element
address order of:

```json
{"address": "<element address>", "status": "proposed|confirmed",
 "modality": "alethic|deontic",
 "inducer": {"name": "…", "version": "…"}, "method": "…",
 "manifest_sha256": "<hex>",
 "support": {"numerator": 0, "denominator": 1},
 "evidence": [{"ref": "…", "sha256": "<hex>"}]}
```

Example ids, counterexample ids and `confidence` are not copied into coverage.

Schema changes:
- `schema_version.enum` gains 5 and 6;
- top-level `properties` gains `induced` (array of `$defs/induced_row`, closed);
- `oneOf` arms 0–3 each gain `"not": {"required": ["induced"]}`;
- new arms 4 and 5 copy arms 2 and 3 with `"const": 5` / `"const": 6` and
  `"required": ["induced"]`.

`render_coverage` adds an `INDUCED` section after the element sections, only when
the payload has `induced`:
`  <address> <status>/<modality> inducer=<name>@<version> method=<m> support=<n>/<d> manifest=<hex>`,
then one `    evidence <ref> <sha256>` line per item. No section and no line is
emitted for versions 3 and 4.

### Other consumers

- **`src/gnd/exp/session_eval.py`:** both `source: Literal[...]` sites gain
  `"induced"`. Without it, a session over a model with an induced constraint
  fails to build its payload.
- **`src/gnd/rai_import.py::_default_modality`:** per IK2-D9.
- **Report, measure and checker:** carry `source` as a free string. No change.
  The `report.schema.json` `source` description string is not edited, so its
  bytes stay the same.
- **Model verbalization:** already prints `[from {source}, …]` and the canonical
  provenance. No change; T12 pins that the induction block appears there.

### References

- **`provenance-and-modality.md`:**
  - "six" becomes "seven" at each site;
  - a taxonomy row for `induced`;
  - an `induced` required-block section with the bounds table and the residual;
  - a source/status bullet;
  - a D-03 row: `induced` | deontic | per IK2-D4;
  - a short "Evolve admission (D-12)" paragraph stating R-I1–R-I4. This becomes
    the one home of the D-12 lifecycle.
- **`evolution-contract.md` §6:** one bullet citing it, and "a sixth source" is
  reworded.
- **`gnd-model-evolve/SKILL.md`:** "six-source" becomes "seven-source".
- **`coverage-and-element-addressing.md`:** versions 5/6 and the `induced` list.

### Registration (IK-R7)

The changed function bodies get RF6b rows in a new IK2 `source-successors`
delta, as IK1 did:
- `_layer1_structural`;
- `_rule_modality_policy`;
- `_enforce_d12`;
- `build_payload`;
- `render_coverage`;
- `_default_modality` if IK2-D9 = agree.

New semantic rule functions are registered in the existing rule list. Any new
model read is checked against the RF6 census, and a chained dynamic-successor
delta is added if the census moves. No new module, lane or entry point.

### Bounds (IK2-C4, IK-R12)

| Item | Bound | Below / at / above |
|---|---|---|
| `inducer.name`, `inducer.version`, `method` | 1–64 chars, token grammar | 0 and 65 refused; 1 and 64 accepted |
| example and counterexample id | 1–64 chars, id grammar | 65 refused; 64 accepted |
| `examples` | 0–256 items, unique | 257 refused; 256 accepted |
| `counterexamples` | 0–32 items, unique | 33 refused; 32 accepted |
| `evidence` | 1–32 items | 0 and 33 refused; 1 and 32 accepted |
| `evidence[].ref` | 1–256 chars, ref grammar | 257 refused; 256 accepted |
| `support.numerator` | 0 … 2^53 − 1 | −1 and 2^53 refused |
| `support.denominator` | 1 … 2^53 − 1 | 0 and 2^53 refused |
| `confidence.value` | 0 … 1, finite | −0.01, 1.01, NaN, ±inf refused; 0 and 1 accepted |
| `confidence.formula` | 1–256 chars | 0 and 257 refused |
| `reviewed_in` | 1–256 chars, not whitespace-only | 257 and `"  "` refused |

The largest block these bounds admit is about 29 KiB of characters:
- 256 example ids × 64 = 16,384;
- 32 counterexample ids × 64 = 2,048;
- 32 evidence items × (256 + 64) = 10,240;
- tokens, digest and formula ≈ 600.

The model's existing 10 MiB `MAX_MODEL_BYTES` cap bounds the total, so IK2-D6
proposes no separate block byte cap.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IK2-D1 | Approval instrument | **Corpus-first** is the default for exit-code contracts and validation predicates (review-convergence.md): T4's admission table and T2/T3's loader cases become a committed JSON answer key with a narrative README, committed red before code. Costs one extra commit before implementation. **Prose** relies on this spec's tables. | corpus-first for T2–T4; prose for coverage |
| IK2-D2 | Where `source: induced` is allowed | **Constraints only:** operations, preconditions and dynamic rules refuse it at schema level (exit 3). **Everywhere:** an induced operation could be added already `confirmed`, because D-12 reads constraints only and the operations gate admits any additive `add`. That breaks IK-R1. | constraints only |
| IK2-D3 | Where `provenance.induction` under another source is refused | **Gate only:** evolve exits 3 for new or changed constraints; `gnd validate` is unchanged, so any existing model stays valid (IK-R3). **Schema too:** `gnd validate` exits 3 for any model that carries the key under another source, including external models that validate today. | gate only |
| IK2-D4 | May confirmation also flip modality to `alethic`? | **Yes:** the D-03 row is deontic/alethic, like every other inferred source; a confirmed alethic induced rule makes `gnd check` exit 1 on violation. Strip includes `modality`. **No:** confirmed induced stays deontic and `gnd check` never exits 1 for it; making it hard needs a user-supplied rewrite, which drops the marker. | yes |
| IK2-D5 | Example-id grammar | **Token** (`^[A-Za-z0-9][A-Za-z0-9._:#-]{0,63}$`): host ids like `case-0042` work as-is; paths, whitespace and separators are refused; single-token raw values pass (residual). **Digest-only** (`^[0-9a-f]{64}$`): every raw value is refused; hosts must hash their ids, and reviewers need the manifest to read them. | token, with the residual recorded |
| IK2-D6 | Bounds | The §6 bounds table, and no separate block byte cap. Any number may be changed now; after implementation only by owner amendment (IK-R12). | the table as written |
| IK2-D7 | `confidence` | **Optional `{value, formula}`:** carried, never used by GND, and not shown by coverage. **Drop it:** the request's "confidence" field is lost. A closed formula enum is not proposed, because no shipped method defines one yet. | optional `{value, formula}` |
| IK2-D8 | Coverage wire | **Versions 5/6** with a required `induced` list only when induced constraints exist; 3/4 stay byte-identical. Follows the existing no-optional-key rule. **A per-element `induction` field** would change the element shape of every version. | versions 5/6 |
| IK2-D9 | `rai_import._default_modality`, a second copy of the D-03 table | **Agree:** add `induced` beside `imported` (deontic; confirmed needs `reviewed_in`). About 2 lines. **Leave it:** it keeps refusing `induced` with "no D-03 default exists", and the two homes disagree (standing rule 5). | agree |
| IK2-D10 | Branch and base | IK2 runs on `claude/ik2-induced-provenance`, cut from B = `ebb1f04`, as a separate PR stacked on PR #36. **Same branch** would grow PR #36. | separate stacked branch |
| IK2-D11 | `method` vocabulary | **Free token:** `gnd-discover`, `ilp-popper` and `gold-answer` are documented spellings, not an enum. **Closed enum:** a new inducer needs a schema edit. | free token |

## 8. Tests

New file `tests/test_induced_provenance.py` unless stated. "Gate" means a direct
`_enforce_d12(before, candidate)` call; "preview" means a full
`EvolutionService.preview` with the CLI exit mapping.

| ID | File / case | Expected |
|---|---|---|
| T1 | `test_schema_sync.py` passes with the edited twins; an added assertion checks `induced` in `source_kind` and `$defs.induction` in both | pass; fails on a no-op |
| T2 | Loader. **Accepted:** a minimal block (empty examples and counterexamples, one evidence item) proposed/deontic; a maximal block with `confidence`; confirmed with `reviewed_in`. **Refused:** missing `induction`; an unknown key in `induction`; an unknown provenance key; evidence ref `/home/u/x`, `C:\x`, `../x`, `a/../b`, `.hidden`, `a b`; example id `Jane Doe`, `a/b`, empty, `a\n`; evidence ref `a\n`; sha256 with a trailing newline; sha256 uppercase or 63 chars; numerator > denominator; `len(examples)` > numerator; too many counterexamples for the gap; an id in both lists; confirmed without `reviewed_in`; `reviewed_in: "  "`; `source: induced` on an operation, a precondition and a dynamic rule; `confidence.value` `.nan`, `.inf`; an anchored `true` as numerator; an unquoted date as `inducer.version` | accepted exit 0; refused exit 3 with the named rule id |
| T3 | Bounds: every row of the §6 bounds table at, below and above its limit (IK2-C4) | per table |
| T4 | Admission table, gate and preview. **Admitted:** (a) new proposed/deontic induced; (e) status change adding `reviewed_in`; (f) the same with modality to alethic (if IK2-D4 = yes); (k) an unchanged confirmed induced constraint. **Refused:** (b) new proposed/alethic → R-I4; (c) new confirmed → R-I3; (d) new proposed with `reviewed_in` → R-I2; (g) status change plus a rationale edit → R-I3; (i) `induction` under `llm-inferred` → R-I1; (j) under `user-supplied` → R-I1; (l) two candidates confirming one predecessor → second R-I3; (m) predecessor kept unchanged plus a confirmed copy → R-I3; (n) confirmed with blank `reviewed_in` at gate level → R-I3 | admitted: gate passes, preview exit 0; refused: named message, preview exit 3 |
| T5 | D-12 pin: the gate outcome (admitted, or the exact message) for 6 existing sources × 2 statuses × 2 modalities, plus unchanged, audit smuggling and an unknown source, equals `tests/fixtures/induced_knowledge/ik2-d12-baseline.json` captured at B before any code | all 27 rows equal |
| T6 | Each of R-I1–R-I4 maps to exit 3 through `_evolve_service_exit`, not 70 | 3 |
| T7 | Order: a constraint with an audit key and `induction` under `explicit` gives the audit message; a candidate failing schema and D-12 gives the validation message at preview | pinned messages |
| T8 | Hostile gate input: `provenance` as list, string, int, null; `induction` as list or string; `status` missing; every case raises `EvolutionError` or passes, never another exception | no `TypeError`/`AttributeError` |
| T9 | Work counter: `canonical_json_text` calls in `_enforce_d12` ≤ 2 × (before + candidate) constraints, for 2,000 proposed induced constraints all confirmed at once | at or under ceiling |
| T10 | Modality policy: proposed/alethic induced warns with the induced message; the `llm-inferred` and `common-sense` messages equal their B bytes | pass |
| T11 | Coverage: an induced model gives v5 with `induced` rows equal to the expected list, valid against `coverage.schema.json`; induced plus derivation gives v6; text output has the `INDUCED` section; a model without induced gives v3/v4 with no `induced` key and no section. A mutant that always emits `induced: []` fails | pass |
| T12 | Model verbalization of an induced constraint contains `[from induced, proposed; modality=deontic]` and the induction block in `provenance=`; `VerifierVerdict(source="induced", …)` builds; a `gnd check` report over an induced model validates against `report.schema.json` | pass |
| T13 | `rai_import._default_modality` for induced proposed and confirmed (if IK2-D9 = agree) | deontic; alethic with `reviewed_in`, refusal without |
| T14 | RF6b body pins, RF6 census, layering and scaffold tests pass with the IK2 successor deltas | pass |
| T15 | `test_public_coverage_goldens.py`, `test_coverage_payload.py`, `test_coverage_derivation.py`, `test_coverage_cli.py` pass unchanged; IK1's T7 still passes against `ik1-baseline.json` | pass |

Criterion ↔ test mapping:

| Criterion | Tests |
|---|---|
| C1 | T1, T2, T10, T12; the D-03 reference edit is review-checked |
| C2 | T4, T5, T6, T7, T8, T9 |
| C3 | T11, T15 |
| C4 | T3 |

Every test maps to a criterion, except T13 (standing rule 5) and T14 (IK-R7).

Branch walk, checking that every declared branch has a case that can fail it:
- schema rules: T2, T3;
- the four support inequalities: T2;
- the screen paths: T2 (`.nan`, anchored `true`, date);
- gate branches a–c, R-I1–R-I4 and the unchanged branches: T4, T5;
- coverage versions 3, 4, 5, 6: T11, T15;
- the renderer section present and absent: T11.

### Verification selection

- **Direct:** `tests/test_induced_provenance.py`.
- **Impact closure:**
  - `test_schema_sync.py`;
  - `test_model_evolution.py`;
  - the four coverage test files;
  - the model validation and semantic-rule tests;
  - `test_object_type_description.py`;
  - the exp session tests;
  - the rai_import tests;
  - the report schema tests;
  - `test_skill_prose_sync.py` and `test_packaged_skills.py`;
  - `test_public_built_inventory.py` and the runtime schema inventory;
  - the scaffold and docs tests;
  - the RF6/RF6b and layering tests.
- **Selection rule:** the reduced v6.3 focused selection, as in IK1. The broad
  default and historical lanes are not run.

## 9. Out of scope for this phase

- `gnd discover` and ILP import (IK4, IK5), and computing support from a
  population;
- induced object types, fact types, derivation rules or operations;
- a closed `method` or `confidence.formula` vocabulary;
- automatic confirmation;
- text-format `gnd diff` (IK1-Q2) and the description nesting cap (IK1-Q1);
- editing the `report.schema.json` `source` description string.

## 10. Size

Estimate: about 270 source and schema lines, 550 test lines, and 100 reference
lines. Measured at record time.

## 11. Approval instrument

Proposed in IK2-D1: corpus-first for the loader and admission cases (T2–T4).
- **Corpus:** `tests/fixtures/induced_knowledge/ik2-corpus/`. `README.md` narrates
  each case without its answer; the answer key `expected.json` is in a separate
  file.
- **Order:** corpus and T5's B-baseline are committed red before any
  implementation file, and the owner approves by reading them.
- **Rest of the spec:** this prose is the design record.

If the owner chooses prose, T2–T4 are written directly from §8.

## 12. Implementability sweep (author inspection, not review)

Each requirement was checked for whether some implementation can satisfy it as
written. Run at B with the repository's `jsonschema` and `ruamel.yaml`:

| Requirement | Check | Result |
|---|---|---|
| `confidence.value` refuses NaN | `Draft202012Validator({"type":"number","minimum":0,"maximum":1}).is_valid(nan)` | **True**, so the schema alone accepts NaN; the layer-1 screen (§6) is required |
| `support.numerator` refuses an anchored `true` | ruamel `&x true` is a `ScalarBoolean` and passes `{"type":"integer"}` | **passes**, so the same screen is required |
| Id and ref grammars refuse a trailing newline | `"a\n"` against the ref pattern | **accepted** (S1); semantic check 5 is required |
| `uniqueItems` refuses duplicate ids | `["a","a"]` | refused |
| The gate can tell a status change from a new constraint | `_enforce_d12` sees only the before and candidate documents | yes, by content after `strip`; it cannot see which command made the proposal, so R-I2 is the enforceable form of D9's discover/import clause |
| A confirmed induced operation is blocked | the operations gate admits additive `add`s with no provenance check | only through IK2-D2's schema restriction |

**S1** (finding). The trailing-newline behaviour also applies to the five
existing `pattern`s in `orm-meta.schema.json`, for example the `^[0-9a-f]{64}$`
digest. That is pre-existing and out of scope for IK2, and is proposed as an
open question for the milestone close sweep.

## 13. Owner gate record (2026-10-24)

**Approval (o).** The owner was asked in chat: "Do you approve IK2 spec r1 with
all proposed rulings D1–D11, or do you want to change any of them first?" The
owner replied "ok" on 2026-10-24. The approved bytes are spec r1 as committed in
`328061e`, before this section was added:

| Artifact | SHA-256 |
|---|---|
| `notes/phase-IK2-spec.md` (r1) | `e6c399709f0e9d4687306cfa04f84fa7017904be0f0ea45fa17cf074c5e312b8` |

**Rulings (o), each as proposed in §7:**

| ID | Ruling |
|---|---|
| IK2-D1 | corpus-first for T2–T4; prose for coverage |
| IK2-D2 | `induced` is allowed on constraints only |
| IK2-D3 | `provenance.induction` under another source is refused at the gate only |
| IK2-D4 | confirmation may also set `modality: alethic`; `strip` includes `modality` |
| IK2-D5 | token id grammar, with the single-token residual recorded |
| IK2-D6 | the §6 bounds table; no separate block byte cap |
| IK2-D7 | optional `confidence {value, formula}`, never used by GND |
| IK2-D8 | coverage versions 5 and 6 |
| IK2-D9 | `rai_import._default_modality` gains `induced`, matching the D-03 table |
| IK2-D10 | separate branch `claude/ik2-induced-provenance` from B = `ebb1f04`, stacked on PR #36 |
| IK2-D11 | `method` is a free token |

**Next under IK2-D1.** Before any implementation file, two artifacts are
committed red:
- the loader and admission corpus under `tests/fixtures/induced_knowledge/ik2-corpus/`;
- T5's D-12 baseline, captured at B.

The owner approves the corpus by reading its README. Implementation starts after
that approval.

## 14. Approval corpus, committed red (2026-10-24)

Under IK2-D1 the corpus and the D-12 baseline are committed before any
implementation file. **The corpus awaits owner approval.**

| Artifact | SHA-256 |
|---|---|
| `tests/fixtures/induced_knowledge/ik2-corpus/README.md` (stories only) | `114cf1fe0e18a3b32ea6fab5f10973d0e8766424e2840ffa24c1e594d7da6013` |
| `tests/fixtures/induced_knowledge/ik2-corpus/cases.json` | `a348d696bdcfb4165b5ffb71017ce1e69872bbd658f91a813fd21288b5c524c1` |
| `tests/fixtures/induced_knowledge/ik2-corpus/expected.json` (answer key) | `a44a1b77845e63797ffa053d7e4b8b968a39683a7de3e8f0bbf1d99833447061` |
| `tests/fixtures/induced_knowledge/ik2-d12-baseline.json` (T5, captured at B) | `6a8ad5a14db88097fa62e94240695888354fa18c4a4b03f91b3cd33932e4066a` |
| `tests/test_induced_provenance.py` (harness) | `c0bfdb76a029aaf62d47596fd7ec82aff2e02a7d3428ed2df0a8d26e8f4b94f3` |
| `evidence/IK2/build_ik2_corpus.py` | `1f85d391b81d05e2e93397867f21fc3e229e1b961d8e43f2a12c5f4dc3e7aca6` |
| `evidence/IK2/capture_ik2_d12_baseline.py` | `be57524aaf9563e38decf78e240574b9731921ab1a1467811eae87f3b2afb5ea` |
| `evidence/IK2/corpus-red.txt` | `5b32e726cf804fe37a2ca90f8b5f51baab425b214badc68430753503559972a1` |

**Contents:**
- 38 loader cases (L01–L38);
- 34 bounds cases (B01–B34), covering every row of the §6 bounds table;
- 17 admission cases (A01–A17), 13 of them also run through `gnd evolve preview`.

**Red run:** 100 failed, 4 passed. The four passes hold at B by design:
- L37 and A10 pin behaviour IK2 must not change;
- the answer-key coverage check;
- T5, which by definition equals the table captured at B.

**Every failure is for the intended reason:**
- `source: induced` is not in the enum at B;
- or the gate gives today's message instead of R-I1–R-I4;
- or a preview exits 0 where 3 is expected (A08, A09, where B's gate admits an
  induction block under `llm-inferred`/`user-supplied`).

**Capture note.** The baseline records commit `328061e`. Its `src/` and `tests/`
are byte-identical to B = `ebb1f04` (`git diff ebb1f04 328061e -- src tests` is
empty), and two runs were byte-identical.

**Harness findings while authoring (not answer changes):**
- **F1:** a fact-type modify is not breaking, so `preview` refuses an accepted
  blast-radius digest (exit 11). The harness calls `preview` once.
- **F2:** an exit code alone could pass for the wrong reason, because at B every
  induced model fails validation with exit 3. Each preview answer therefore also
  names the refusal text it must carry: the gate reason, or
  `semantic:induced-confirmed-reviewed` for A13.
- **Stories:** two stories gave away their answer and were reworded before
  commit (L04, L37).

## 15. Corpus approval (2026-10-24)

**Approval (o).** The owner was asked: "Do you approve the corpus as committed so
I can start implementing, or do you want to change any answers first?"

Before answering, the owner asked whether IK2 is a generic framework or will be
tested against a real inductive learner. The answer given:
- IK2 is learner-agnostic;
- a real learner enters only in IK5, through recorded Popper fixtures, with a
  live run as optional evidence;
- the block's fit to real Popper output is the author's reading, not a tested
  fact.

An optional scratch Popper check was offered. The owner replied "ok approved",
choosing the corpus as it is, without that check.

The approved corpus is commit `ef39b1a`, with the digests in §14.

**Residual carried forward.** Whether the induction block can represent real
learner output without loss is untested. A shortfall found in IK5 needs an owner
amendment to this phase's schema.

## 16. Implementation findings

Recorded as found. F1 and F2 are the corpus-authoring findings in §14.

- **F3 — spec text versus an approved answer (whitespace scope).** §6 check 5
  said "no string anywhere in the block contains a whitespace character". That
  refuses approved case L02, whose `confidence.formula` is
  `numerator / denominator`. Under the rule that the approved corpus's meanings
  stay stable, the corpus wins. The check now covers the pattern-governed fields
  (tokens, ids, refs, digests), the only place the S1 trailing-newline gap
  exists; the free-text formula is excluded. Review R5 then added a test for
  every one of those fields.
- **F4 — refuted premise: "no new module".** The IK2 rules took
  `gnd/model/_validation.py` to 5,078 lines, past the pinned 5,000-line RF6
  package-size ceiling (`tests/test_rf6_packages.py`). Trimming lines to get
  under it would defeat the ceiling's purpose. The rules moved to a new home,
  `gnd.model._induction`:
  - registered in `tools/gnd_layers.json` and in the closed `split_homes` list;
  - re-exported by `gnd.model` with `__module__ = 'gnd.model'`, like every rule;
  - importing `_iter_provenance_bearing` per call to avoid an import cycle.
  
  `_validation.py` is now 4,986 lines.
- **F5 — stale sentence in §6.** "Under IK2-D4 = keep-deontic, modality is not
  stripped" describes the rejected reading. IK2-D4 was ruled yes (§13), and the
  code strips `modality`.
- **F6 — §6 "matching is location-insensitive", tightened (review R3).** For the
  reviewed status change, a location-insensitive match let one proposal confirm
  an induced rule and move it to another fact type or the top level. A
  confirmed alethic rule could then appear where nothing was ever induced. The
  claimable predecessor is now keyed by its host fact type (top level =
  `None`). The exact-match rule for unchanged constraints is unchanged, so every
  pre-IK2 outcome and the corpus answers stand (A05, A06 confirm in place).
  **Owner attention:** this narrows an approved spec sentence for safety. It is
  not an answer change; a ruling is requested in IK2-Q4.
- **F7 — §5 over-states the `..` refusal (review R6).** The approved grammars
  refuse a `..` *segment* (`../x`, `a/../b`) and any dot-leading segment, but
  accept `..` inside a segment (`a..b`). The grammar stands as approved; the
  provenance reference states the rule as "no dot-leading segment".
- **F8 — RF guards needed registration, as in IK1:**
  - an RF6b successor for `_rule_modality_policy`, and IK1's `_layer1_structural`
    row re-pointed at the current body with its original `before` kept;
  - an RF5 successor for `_evolve_service_exit` (its body carries the message
    markers);
  - a chained dynamic-candidate delta (`evidence/IK2/dynamic-query-successor.json`);
  - coverage's induced view reads constraints through `ModelIndex.iter_constraints`
    and the gate's host walk is a keyword on the existing `_constraints` reader,
    so the RF6 static query census is unchanged.
  
  The scripts that produced each are in `evidence/IK2/`.
- **F9 — refusal order.** A first rewrite of `_enforce_d12` checked audit keys
  for all candidates before any D-12 branch. That changes which refusal a
  multi-defect proposal reports first. The final gate keeps the single in-order
  pass, with claimable predecessors computed up front, and T7 pins both orders.

## 17. Owner ruling on the review fixes (2026-10-24)

**Ruling (o).** After the record (`0f0a55c`), the owner replied "ok I approve
the fixes" on 2026-10-24. This approves the fixes in `6259bc0`:
- R1: float support counts refused;
- R2: the screen scoped to induced constraints;
- R3: a reviewed status change is claimed per host fact type;
- R5: tests added and `minItems: 1` on `induced`.

It rules **IK2-Q4**: a confirmation must stay on its host. This replaces §6's
"matching is location-insensitive" for the status-change path (F6); exact
matching of unchanged constraints is unchanged.

The ruling does not decide **IK2-Q1** (archived induced proposals), which stays
open.

## 18. Owner ruling on IK2-Q1 (2026-10-24)

**Ruling (o).** Asked about archived induced proposals in `rejected_proposals`
(review R4), the owner wrote: "just ask for a review and approval the user and
record it that is all". Offered three readings, the owner selected **"Ruling on
IK2-Q1: no checks"**:
- rejected learned rules get no extra automatic validation;
- the owner's review and recorded approval is the safeguard.

**Consequence.** No code change, and `rejected_proposals` stays schema-light. A
rejected induced proposal may still carry host paths or raw values; the owner
reviewing it is the control. IK2-Q1 is closed.
