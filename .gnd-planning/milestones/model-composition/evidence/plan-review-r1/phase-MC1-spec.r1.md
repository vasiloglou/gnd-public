# Phase MC1: model includes — contract, loader, validate and check

## 1. Status

Draft r1, **blocked on the plan gate**: implementable once the owner approves
the plan and rules MD1-MD7 (plan §10), then approves this spec at its own
gate. No code is written before both.

## 2. Provenance

Derives from [model-composition-plan.md](model-composition-plan.md) r1 (§2.1-2.6,
§4 MC1, §9), unreviewed. Baseline main `459ca8d2`. No review has run over this
spec. Assumes the plan's proposals for MD1-MD7; any other ruling reopens the
affected sections, which are tagged `[MDn]`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan predicate 1, MC1-C1 | `load_model(path)` composes; validate/check match the flattened twin | §6.2, §6.3; tests T1-T4 |
| plan predicate 2, MC1-C2 | each §2.5 reason, exit 3, observed red first | §6.4; T5-T16 |
| MC1-C3 | resolution order pinned | §6.2 order; T17 |
| MC1-C4 | time bound at the caps | T18 |
| plan predicate 3, MC1-C5 | include-free models unchanged: dump, four identities, `--identity` | §6.1 `model_dump`; T19, T20 |
| MC1-C6 | bytes-only route refuses; composed bytes route composes | §6.2; T21, T22 |
| MC1-C7 | references over included base fact types | §6.2 step 11; T23 |
| plan §2.4 [MD6] | identity over composed content plus declarations, measured | §6.5; T24, T25 |
| plan §2.6 | origin-prefixed diagnostic paths | §6.6, D3; T26 |
| plan rule 0.1 | one resolver | §6.2; T27 (import scan) |
| plan rule 0.5 | refusals red first | §8 note |
| O5 | one id namespace | step 9-10; T13, T14 |
| O11 | component index updated in the commit; `changed --strict` | §6.7 |
| O12 | `_includes.py` assigned in `tools/gnd_layers.json`, allowance zero | §6.7; layer test in the focused gate |
| O13 | `ModelIndex` unaffected; no family hook added | §4 rule 4 |
| plan §5 | meta-schema and its sync-pinned skill copy | §6.1; `tests/test_schema_sync.py` |
| plan §3 | normative section in `representation-format.md` | §6.8 |

## 4. Standing rules bound to this phase

1. **Totality.** New consumers of untrusted input: `_includes.parse_declarations`
   (the `includes` list as authored) and `_includes.resolve` (the included
   bytes). Both are total over arbitrary JSON: non-list, non-mapping entries,
   extra keys, long integers, NaN, deep nesting, non-UTF-8, an included file
   that is valid YAML but not a mapping. The 10 MiB cap is applied to the read
   (`read_regular_bounded_at(..., max_bytes=)`), not after. Tests T5-T16.
2. **Cap bounds the algorithm.** The new work is the composition merge and
   the collision check over at most 8 files and the existing entry maximum. Both
   are one pass with a dict keyed by id. T18 times composition at the caps
   against a linear ceiling measured in the spec's experiment note.
3. **Validation order.** §6.2 is the order. Two orderings both reject in two
   places, which T17 pins with a source-order assertion: hash before parse
   (a mismatched file is never parsed), and collision before composed semantic
   validation (a duplicate id reports `include:collision`, not
   `semantic:id-unique`).
4. **One walk over N kinds.** The collision check walks every id-bearing kind
   in one function (`_includes._ids`), reusing the kind list the
   `semantic:id-unique` rule already walks (`_validation.py:343`
   `_rule_id_unique`), imported rather than copied. No constraint family gets
   a hook; `ModelIndex` sees an ordinary model.
5. **One home for prose.** The normative contract is the new
   `representation-format.md` section; the meta-schema `description` and the
   plan cite it. The plan's §2 yields to it once written.
6. **Measure contested representation questions.** MD6's identity claim is
   measured (T19, T24, T25) before MC2 relies on it.

Project failure classes: the discriminating fixture for "every included
element is read-only" is a model whose includer redeclares an element of the
*second* include only (T14); for the hash check, a file whose bytes differ
only in a trailing newline (T9).

## 5. Goal

`gnd validate MODEL` and `gnd check MODEL POP` on a version-5 model with
`includes` exit with the same code and print the same lines as on its
committed flattened twin, apart from the spellings of D3 and the verbalization
header (not in this phase). Every malformed, escaping, oversized, mismatched,
forbidden or colliding include exits 3 with its own reason. Every model
without `includes` produces byte-identical outputs and identities to main
`459ca8d2`.

## 6. Design

### 6.0 Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| confined relative path | `components_index.py search reference path confined`; `git grep _relative` | `model/__init__.py` `_relative` | reuse (import) |
| no-follow root and bounded read | `search retained root descriptor` | `retained_root`, `artifacts.read_regular_bounded_at` | reuse |
| model parse and validation | `search model loader validation` | `parse_model_document`, `_layer1_structural`, `semantic_validate` | reuse |
| id walk | `search id namespace unique` | `_validation._rule_id_unique` | adapt: expose the kind list it walks |
| side table on a frozen model | `search private attribute compiled` | `Model._compiled` | reuse the pattern |

### 6.1 Schema and `Model` [MD1, MD2]

`orm-meta.schema.json` (and the skill copy, held identical by
`tests/test_schema_sync.py`):

```json
"version": {"enum": [1, 2, 3, 4, 5]},
"includes": {
  "type": "array", "minItems": 1, "maxItems": 8,
  "items": {
    "type": "object", "additionalProperties": false,
    "required": ["id", "path", "sha256"],
    "properties": {
      "id": {"type": "string", "minLength": 1, "maxLength": 128},
      "path": {"type": "string", "minLength": 1, "maxLength": 4096},
      "sha256": {"type": "string", "pattern": "^[0-9a-f]{64}$"}
    }
  }
}
```

plus `allOf`: `{"if": {"required": ["includes"]}, "then": {"properties": {"version": {"const": 5}}}}`.
Version 5 also admits every version-4 feature (`operations`'s enum and
`reference_populations`' const widen to include 5); the spec's test T28 shows
a version-5 file without `includes` behaves exactly as version 4.

`documents.Model` gains `includes: list[dict[str, Any]] = Field(default_factory=list)`
and `_origins: dict[str, str] = PrivateAttr(default_factory=dict)` (element id
→ include id; own elements absent). `model_dump` pops `includes` when empty,
exactly as it pops `reference_populations`, so every include-free dump is
unchanged (T19).

### 6.2 Resolution: `src/gnd/model/_includes.py` (about 180 lines)

```python
class IncludeError(ModelLoadError):        # exit 3 through the existing mapping
    reason: str                            # one of REASONS, value-free message

REASONS = ("include:declaration", "include:path", "include:unreadable",
           "include:size", "include:hash-mismatch",
           "include:invalid-included-model", "include:forbidden-section",
           "include:collision", "include:unresolved")

def parse_declarations(document: object) -> tuple[Declaration, ...]: ...
def compose(document: Mapping[str, Any], *, descriptor: int,
            source: str | Path) -> tuple[dict[str, Any], dict[str, str]]: ...
```

`load_model_bytes(data, *, source)`: after layer 1, if the document has
`includes`, raise `include:unresolved` (before semantic validation, so the
author is not told their rules name unknown fact types).
New `load_model_bytes_composed(data, *, source, root)` and the existing
`_load_model_no_follow` call `compose` under the retained descriptor. The
historical symlink fallback of `load_model` admits only include-free models,
as it already does for references.

Normative order, one home here and in `representation-format.md`:

1. parse the including file; layer 1 over it as written;
2. `parse_declarations`: shape, unique ids, at most 8 → `include:declaration`;
3. each path through `_relative` → `include:path`;
4. read each under the descriptor, no follow → `include:unreadable`;
   per-file cap 10 MiB on the read, set cap 32 MiB → `include:size`;
5. sha256 of raw bytes against the declaration → `include:hash-mismatch`;
6. `parse_model_document` on the included bytes, then layer 1 and semantic
   validation as a standalone model → `include:invalid-included-model`;
7. included document declares `includes`, `reference_populations`,
   `operations` or `rejected_proposals` → `include:forbidden-section` [MD3];
   (checked on the parsed document before step 6's validation, so a nested
   include is reported as forbidden, not unresolved; T17 pins it);
8. build the composed document: included object types, fact types,
   constraints and deontic notes in `includes` order, then the including
   file's own; `version`, `model_id`, `source` and `includes` from the
   including file [MD4];
9. one walk over every id in the composition → `include:collision`, naming
   the two origins (`includes[<id>]` or `model`) and the id kind, never a
   value [MD5];
10. layer 1 and semantic validation of the composed document (existing
    rules, unchanged); issues inside included elements are prefixed (§6.6);
11. `Model.model_validate`, `_origins` set, `validate_declarations`
    (references may own included base fact types), compiled obligations.

### 6.3 CLI

No new flag. `gnd validate` and `gnd check` already load through
`load_model(path)`; `IncludeError` maps to exit 3 with its reason through the
existing `ModelLoadError` route (the spec's implementation step confirms the
mapping by test, not by reading). JSON output carries the reason as `rule_id`.

### 6.4 Refusal cases

One per reason, each in T5-T16, each red against the unmodified loader first
(a version-5 file is refused by the version enum today, so "red first" for the
cases means: the test exists and fails on the loader without `_includes`
because the refusal reason differs).

### 6.5 Identity [MD6]

No identity function changes. With `includes` in the dump: `_model_digest`,
identity v2, and the reference identity document all cover the composed
content plus the declarations (id, path, sha256). Measured: T24 two includers
with the same composition and different `includes` paths have different
identities (D4 rules whether that is wanted); T25 identity of an includer
equals identity of its flattened twin plus only the `includes` key.

### 6.6 Diagnostics (D3)

`ValidationIssue.path` for an issue whose subject element has an origin is
spelled `includes[<id>]:<path in the included file>`. The included file's own
path is recomputed by subtracting the composed offset, so it points into the
file the author must edit. Include-free models are unchanged.

### 6.7 Homes

`tools/gnd_layers.json`: `gnd.model._includes` in the `model` layer. Component
index: `model.loading` lists `_includes.py`, its does/verbs updated in the
same commit; `python3 scripts/components_index.py changed --base main --strict`
before the PR.

### 6.8 Normative prose

New section "Model includes (version 5)" in
`src/gnd/skills/gnd-orm-core/references/representation-format.md`, after
"Fixed reference populations (version 4)": declaration, what an included file
may contain, composition, the order of §6.2, refusals, identity. The meta-schema
`description` gains one sentence citing it.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Reason spelling | `include:*` (new prefix) vs `model:include-*`. Exit code the same; the prefix is what JSON consumers match | `include:*`, matching `composition:invalid`'s prefix style |
| D2 | Does a version-5 file without `includes` exist? | (a) yes, behaves as version 4 (T28); (b) version 5 requires `includes`. (b) makes 5 mean "has includes" and refuses the empty case | (a) |
| D3 | Diagnostic path spelling | prefixed path (§6.6) vs a new `origin` field on `ValidationIssue`. A field changes the validate JSON shape for every model | prefixed path |
| D4 | Identity covers include paths? | (a) whole declaration, like references bind their path; (b) id and sha256 only, so moving the vocabulary file keeps identity. (a) moves every recorded identity on a file move | (a), for consistency with the reference envelope |
| D5 | Included file's `version` | (a) any version 1-4 whose features fit MD3; (b) must equal the includer's | (a) |
| D6 | Included file's `model_id` | ignored in the composition (the includer's wins) vs must be absent | ignored, and recorded in the origin table only |

## 8. Tests

File `tests/test_mc1_model_includes.py`; fixtures `tests/fixtures/mc1-includes/`
(vocabulary, includer, flattened twin, one hostile file per reason). Every
refusal test is run once against the loader without `_includes` and the red
output is pasted into the record.

| # | Case | Expected |
|---|---|---|
| T1 | `load_model` on includer equals flattened twin's dump plus `includes` | equal |
| T2 | `gnd validate` includer vs twin, text and JSON | exit 0 both, same lines |
| T3 | `gnd check` with a violating population, includer vs twin | exit 1 both, same findings |
| T4 | `gnd check` with a clean population | exit 0 both |
| T5 | `includes` not a list / entry not a mapping / extra key / duplicate id / 9 entries | exit 3 `include:declaration` |
| T6 | path `../x`, absolute, `a//b`, backslash, `C:` | exit 3 `include:path` |
| T7 | path is a symlink; an ancestor is a symlink | exit 3 `include:unreadable` |
| T8 | file 10 MiB + 1 byte; set over 32 MiB | exit 3 `include:size` |
| T9 | hash of file with an added trailing newline | exit 3 `include:hash-mismatch` |
| T10 | included bytes not YAML; YAML list; NaN; deep nesting; long integer | exit 3 `include:invalid-included-model` |
| T11 | included file semantically invalid alone | exit 3 `include:invalid-included-model` |
| T12 | included file declares `includes`; `operations`; `reference_populations`; `rejected_proposals` | exit 3 `include:forbidden-section` |
| T13 | includer redeclares an included fact type id | exit 3 `include:collision` |
| T14 | two includes; includer's constraint id equals an id in the second | exit 3 `include:collision` naming `includes[second]` |
| T15 | composed model semantically invalid (rule names an unknown role) | exit 3 existing rule id, path unprefixed (own element) |
| T16 | included constraint fails composed validation only through the includer's addition | exit 3, path prefixed `includes[<id>]:` |
| T17 | source-order: hash before parse; forbidden-section before included validation; collision before composed semantics | assertion passes |
| T18 | 8 includes at the entry maximum, compose time | under the measured linear ceiling |
| T19 | census: every committed `*.orm.yaml`, dump and four identities equal to values recorded from main `459ca8d2` | equal |
| T20 | `gnd validate --identity` on 10 committed models | byte-identical |
| T21 | `load_model_bytes` on includer | `include:unresolved` |
| T22 | `load_model_bytes_composed` with root | composes, equals T1 |
| T23 | includer declares a reference population owning an included base fact type; check | binds; exit as on the twin |
| T24 | two includers, same composition, different include path | identities differ (per D4) |
| T25 | includer identity vs twin identity | differ only by `includes` (document diff) |
| T26 | issue path inside included element | `includes[<id>]:$.fact_types[...]` pointing into the included file |
| T27 | import scan: no module outside `gnd.model` imports `_includes` internals | passes |
| T28 | version-5 file without `includes` vs same file at version 4 | same outputs |

Focused gate:

```bash
uv run pytest -q tests/test_mc1_model_includes.py tests/test_schema_sync.py tests/test_model_validation.py tests/test_model_identity.py tests/test_reference_population_corpus.py tests/test_public_reference_budget.py tests/test_evolve_loading.py --tb=short
```

plus `uv run ruff check src tests`, the layer-map test, and the whole suite on
beast-3 against the merge-base run (predicate 3 is a whole-suite claim).

## 9. Out of scope for this phase

Every §1.3 consumer other than `load_model`, `gnd validate` and `gnd check`
(MC2); verbalization header (MC2); evolve and re-pin (MC3); skill and docs
text beyond the normative section (MC4); nested includes and overrides.

## 10. Size

Estimate: about 300 source lines (`_includes.py` 180, loader and `Model` 40,
schema 40, error mapping and layer map 20, normative prose ~60 not counted as
source) and 500 test lines plus fixtures. Stop line (plan rule 0.6): 450
source, 750 test.

## 11. Approval instrument

This prose. The fixture corpus is authored during implementation; its answer
key (the expected reason per hostile file) lives in the test module, not in
the fixture directory's README, so a later blind pass is possible.
