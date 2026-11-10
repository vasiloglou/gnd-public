# Phase MC1: model includes — contract, loader, guards, validate and check

## 1. Status

Draft r2, **blocked on the plan gate**: implementable once the owner approves
the plan and rules MD1-MD16 (plan §10), then approves this spec at its own
gate. No code is written before both.

## 2. Provenance

Derives from [model-composition-plan.md](model-composition-plan.md) r2 (§2,
§4 MC1, §9). Baseline main `459ca8d2`. r1 of this spec was reviewed by Codex
together with plan r1 ([review](../evidence/plan-review-r1/codex-review.md);
r1 bytes retained beside it, sha256 `b6ebc5db…2a4c06dff`). **r2 has not been
reviewed**; its bytes carry no review opinion. Changes made for that review
are tagged `(r1 Pn)`. Assumes the plan's proposals for MD1-MD16; any other
ruling reopens the sections tagged `[MDn]`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan predicate 1, MC1-C1 | compose; validate/check agree with the twin outside the allowlist | §6.3, §6.9; T1-T4 |
| plan predicate 2, MC1-C8 | inline constraints on included fact types | §6.1, §6.2 step 10; T30-T33 |
| plan predicate 3, MC1-C2 | each reason, exit 3, as an issue, text and JSON | §6.4; T5-T18 |
| MC1-C2 | direct hostile-shape tests of the new functions | T19, T20 |
| MC1-C3 | one order, phase by phase; compound faults | §6.2; T21 |
| MC1-C4 | scaling with a quadratic mutant | T22 |
| plan predicate 4, MC1-C5 | census over YAML and JSON, five values plus `--identity` | §6.8; T23, T24 |
| MC1-C6 | bytes-only refuses; composed bytes composes | §6.2; T25, T26 |
| MC1-C7 | version-5 references via both routes | §6.2 steps 12-13; T27-T29 |
| MC1-C9 | branch-to-test matrix over every admitted section | §8 matrix; T34-T40 |
| plan predicate 5, MC1-C10 | activation inventory, one guard per row | §6.7; T41 |
| plan §2.4 [MD6] | identity measured | §6.5; T42, T43 |
| plan §2.6 | origin-prefixed diagnostics | §6.6; T44, T45 |
| plan rule 0.1 | one resolver | §6.2; T46 |
| plan rule 0.6 | refusals red first | §8 note |
| O5 | one id namespace | step 10; T15, T16 |
| O11 | component index updated in the commit; `changed --strict` | §6.10 |
| O12 | `_includes.py` in `tools/gnd_layers.json`, allowance zero | §6.10; layer test in the gate |
| O13 | `ModelIndex` unaffected; no family hook | §4 rule 4 |
| O18 | inline-only kinds placed by `fact_type_constraints` | §6.1, step 10 |
| O19 | reference version guard widened | §6.2 step 12 |
| O21 | unattended source refused in included files | step 8; T14 |
| plan §5 | meta-schema and its sync-pinned copy | §6.1; `tests/test_schema_sync.py` |
| plan §3 | normative section in `representation-format.md` | §6.11 |

## 4. Standing rules bound to this phase

1. **Totality.** New consumers of untrusted input:
   `_includes.parse_declarations(document)` (the `includes` and
   `fact_type_constraints` sections as authored), `_includes.parse_included(raw)`
   (included bytes), `_includes.compose(...)` and
   `_includes.declares_includes(document)` (the guard predicate). Each is total
   over arbitrary JSON and arbitrary bytes: non-list and non-mapping entries,
   extra or missing keys, malformed hashes, empty lists, long integers, NaN and
   infinities, deep nesting, non-UTF-8, an included file that is valid YAML but
   not a mapping. Direct tests T19 and T20 call the functions, not the loader
   (r1 P12). The 10 MiB cap is applied to the read.
2. **Cap bounds the algorithm.** The new work is the composition merge, the
   target resolution of `fact_type_constraints` and the collision walk. Each is
   one pass with dicts keyed by id. T22 times increasing workloads (1k, 4k,
   16k composed declarations) against a predeclared ratio (time at 16k ≤ 6×
   time at 4k), and a quadratic mutant of the collision walk (pairwise compare)
   must fail it (r1 P14).
3. **Validation order.** §6.2 is the one order, applied phase by phase across
   all includes: every include passes a step before any include enters the
   next (r1 P3). T21's compound-fault cases put two faults in one input and
   assert the winning reason **and** that the later step's function was not
   called (by a counting patch on that function), not by source order.
4. **One walk over N kinds.** The collision walk covers every id-bearing kind
   in one function (`_includes._ids`), reusing the kind list
   `_validation._rule_id_unique` (`_validation.py:343`) walks, imported rather
   than copied. No constraint family gets a hook; `ModelIndex` sees an
   ordinary model.
5. **One home for prose.** The normative contract is the new
   `representation-format.md` section; the meta-schema `description` and the
   plan cite it. The plan's §2 yields to it once written.
6. **Measure contested representation questions.** The identity claim (T42,
   T43), the census (T23) and the JSON-serialization mechanism (D7) are
   measured before MC2 relies on them.

Project failure classes: the discriminating fixture for "every included
element is read-only" is a model whose includer collides only with the
*second* include (T16); for the hash check, a file whose bytes differ only in
a trailing newline (T10); for provenance, anonymous top-level constraints in
an include, which an id-keyed table would miss (T44, r1 P11).

## 5. Goal

On a version-5 model with `includes`, `gnd validate MODEL` and
`gnd check MODEL POP` exit with the same code as on its committed flattened
twin and print equal output outside the allowlist of §6.9, whose fields are
asserted separately. Every malformed, escaping, oversized, mismatched,
unparsable, forbidden, colliding or mistargeted include exits 3 with its own
`rule_id`, in text and JSON. Every route that does not resolve includes
refuses an include-bearing model with exit 3 before output. Every model
without `includes` produces byte-identical dumps, JSON serializations,
identities and `--identity` output to main `459ca8d2`.

## 6. Design

### 6.0 Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| confined relative path | `components_index.py search reference path confined`; `git grep _relative` | `model/__init__.py` `_relative` | reuse (import) |
| no-follow root and bounded read | `search retained root descriptor` | `retained_root`, `artifacts.read_regular_bounded_at` | reuse; add a typed size subclass (r1 P13) |
| model parse and validation | `search model loader validation` | `parse_model_document`, `_layer1_structural`, `semantic_validate` | reuse |
| id walk | `search id namespace unique` | `_validation._rule_id_unique` | adapt: expose the kind list it walks |
| side table on a frozen model | `search private attribute compiled` | `Model._compiled` | reuse the pattern |
| issue route to text and JSON | `git grep ModelValidationError api.py checking_service.py` | `api.py:313`, `checking_service.py:306` | reuse: refusals are `ModelValidationError` (r1 P5) |

### 6.1 Schema and `Model` [MD1, MD2, MD10, MD11]

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
},
"fact_type_constraints": {
  "type": "array", "minItems": 1,
  "items": {
    "type": "object", "additionalProperties": false,
    "required": ["fact_type", "constraints"],
    "properties": {
      "fact_type": {"type": "string", "minLength": 1},
      "constraints": {"type": "array", "minItems": 1,
                      "items": {"$ref": "#/$defs/inline_constraint"}}
    }
  }
}
```

`allOf` gains: `includes` ⇒ `version` const 5; `fact_type_constraints` ⇒
`includes` required; without `includes`, `object_types` and `fact_types`
remain required (the top-level `required` moves into an `if not includes`
branch). The `operations` enum and `reference_populations` const widen to
include 5. The schema checks the envelope, but the loader never reaches
layer 1 with a malformed declaration (§6.2 step 3), so the schema is a
second statement of the shape, held equal to `parse_declarations` by T20.

`documents.Model` gains `includes: list[dict[str, Any]]` and
`fact_type_constraints: list[dict[str, Any]]` (both default empty, kept as
authored), `_provenance: tuple[ElementOrigin, ...]` and
`_included: tuple[IncludedFile, ...]` as private attributes:

```python
@dataclass(frozen=True)
class ElementOrigin:
    origin: str                 # "model" or the include id
    composed_address: str       # "$.fact_types[7]", "$.fact_types[7].constraints[2]"
    original_address: str       # in the origin file, e.g. "$.fact_type_constraints[0].constraints[1]"
    element_id: str | None      # None for an anonymous constraint

@dataclass(frozen=True)
class IncludedFile:
    id: str; path: str; sha256: str
    version: int; model_id: str | None; source: Mapping[str, Any] | None
```

Empty `includes` and `fact_type_constraints` are omitted from **every**
serialization entry point: `model_dump` and `model_dump_json` (r1 P10). The
mechanism is D7, chosen by measurement over the census.

### 6.2 Resolution: `src/gnd/model/_includes.py` (about 260 lines)

```python
REASONS = ("include:declaration", "include:path", "include:unreadable",
           "include:size", "include:hash-mismatch", "include:parse",
           "include:forbidden-section", "include:invalid-included-model",
           "include:unknown-target", "include:collision",
           "include:unresolved", "include:unsupported-route")

def declares_includes(document: object) -> bool: ...
def parse_declarations(document: Mapping[str, Any]) -> Declarations: ...
def parse_included(raw: bytes, *, include_id: str) -> dict[str, Any]: ...
def compose(document: Mapping[str, Any], *, descriptor: int, source: str | Path
            ) -> tuple[dict[str, Any], tuple[ElementOrigin, ...], tuple[IncludedFile, ...]]: ...
def refuse_unsupported(route: str) -> NoReturn: ...
```

Every refusal raises `ModelValidationError([ValidationIssue(path=..., message=..., rule_id=<reason>)])`
with a value-free message (r1 P5).

Normative order (one home here until §6.11 moves it to
`representation-format.md`). Each step runs for every include before any
include enters the next step; the first failing include in declaration order
reports.

1. `parse_model_document` on the including bytes (existing refusals
   unchanged).
2. `declares_includes(document)` is false → the existing path, untouched.
3. `parse_declarations`: `version` is 5; `includes` is a list of 1..8
   mappings with exactly `id`, `path`, `sha256`, unique ids, valid hashes;
   `fact_type_constraints` is absent or a list of mappings with exactly
   `fact_type` and a nonempty `constraints` list → `include:declaration`.
   Runs **before** layer 1, so these inputs report `include:declaration`, not
   a `jsonschema:*` id (r1 P2).
4. each path through `_relative` → `include:path`.
5. each read under the descriptor, no follow → `include:unreadable`; the
   typed size refusal (pre-read oversize or growth past the cap) and the
   32 MiB set total → `include:size` (r1 P13).
6. each raw sha256 against its declaration → `include:hash-mismatch`. A
   mismatched file is never parsed.
7. `parse_included`: UTF-8, the YAML alias and event guard, a mapping →
   `include:parse` (r1 P3, P12).
8. each parsed included document declares `includes`,
   `reference_populations`, `operations`, `rejected_proposals` or
   `fact_type_constraints`, or has a `source` in unattended mode →
   `include:forbidden-section` [MD3, MD16] (r1 P18).
9. each included document, layer 1 and semantic validation as a standalone
   model → `include:invalid-included-model`, with the first issue's rule id and
   path carried in the message.
10. compose (plan §2.3): own elements first at their authored positions; each
    include's elements after, in `includes` order; each
    `fact_type_constraints` entry resolved to an included fact type
    (otherwise `include:unknown-target`, also when it names an own fact type)
    and its constraints appended to that fact type's inline list; then one
    collision walk over every id in the composition → `include:collision`,
    naming the two origins and the id kind [MD5]; provenance built.
11. layer 1 and semantic validation of the composed document (existing rules,
    unchanged); issue paths remapped per §6.6.
12. `Model.model_validate`; `_provenance` and `_included` set;
    `validate_declarations` accepts version 4 or 5 (`model/__init__.py:499`,
    r1 P4); compiled obligations.
13. reference binding: `_load_model_no_follow` as today; the new
    `load_model_bytes_composed(data, *, source, root)` binds under the same
    retained root and returns the model with its context attached.

`load_model_bytes(data, *, source)`: after step 1, if `declares_includes`,
refuse `include:unresolved` before any other include step, so a bytes-only
caller with a malformed declaration also reads "unresolved" (stated, and T25
pins it). The historical symlink fallback of `load_model` admits only
include-free models.

### 6.3 CLI

No new flag. `gnd validate` and `gnd check` load through `load_model(path)`
and already turn `ModelValidationError` issues into the text lines and the
JSON `issues` array. T5-T18 assert the exact text line and the JSON issue
object for each reason through both commands (r1 P5).

### 6.4 Refusal cases

One per reason (T5-T18), each run first against the loader without
`_includes`, where the version-5 file is refused with a different rule id;
that red output goes into the record.

### 6.5 Identity [MD6]

No identity function changes. Measured: T42, an includer's identities equal
those of a document equal to the composed dump (round-trip through
`load_model_bytes`), so they cover exactly composed content plus
declarations; T43, two includers with the same composition and different
include paths have different identities (D4).

### 6.6 Diagnostics

`remap_issue_path(path, provenance)` reads the leading address of an issue
path, in either form the validators emit (`$.fact_types[3]...` or
`$.fact_types[id=X].constraints[2]...`, `_validation.py:316-320`), looks it
up by composed address (and by id for the selector form), and for an element
whose origin is an include replaces it with
`includes[<id>]:<original address><rest>`. Own elements keep their path
unchanged, because they keep their authored positions (r1 P11). Warnings are
remapped the same way.

### 6.7 Activation inventory and guards [MD15] (r1 P16)

The implementation's first step re-reads each site and fills the mechanism
column; the rows below are the known admission points.

| Route | Admission | Guard in MC1 |
|---|---|---|
| validate, check (path) | `load_model` | composes (supported) |
| witness service, judgments, `api.py:1123`, exp session contract / replay / judgments, export Lean / Souffle / PyRel rules / ILP / applications, discover, evolve | `load_model_bytes` | `include:unresolved` (step 2 rule), confirmed per row by a case |
| population compose API (`api.py:980`) | `load_model_bytes`, refusal collapsed to "invalid model" | refuses; the case asserts no composed output is written |
| batch, measure, codegen, conformance, extract, fidelity, doccheck | `load_model(path)` plus a raw hash or copy | `refuse_unsupported` before the hash or copy |
| recovery verify, `gnd import rai-orm`, export applications, exp `session.py` | tempdir copy then `load_model` | `refuse_unsupported` before the copy |
| export `render_pyrel`, `pyrel_runtime._admit_model` | own parse, raw text embedded | `declares_includes` then `refuse_unsupported` |
| witness io (in-memory document) | `model.orm.json` rebuilt | `declares_includes` on the document |
| skill scripts `validate_model.py`, `verify_migration.py` | standalone parse, no gnd import | refuse a document with `includes` by name, exit nonzero, message cites `gnd validate` |
| examples | `json.loads` | none needed: examples ship no includer (T41 asserts) |

T41 is one case per row: an include-bearing model through the route exits 3
(2 for the skill scripts, per their own contract) before writing any output.

### 6.8 Census (r1 P15)

`tests/test_mc1_census.py` enumerates `git ls-files '*.orm.yaml' '*.orm.json'`
(300 and 100 at `459ca8d2`) through `load_model_bytes`, records for each
either a refusal (its rule ids) or `model_dump`, `model_dump_json`,
`_model_digest`, `model_identity` and `reference_model_digest` (references
bound where declared), and compares with a committed baseline produced at
`459ca8d2`. A file added or removed after the baseline fails the census until
the baseline is regenerated by its script, with the counts printed. T24
compares `gnd validate --identity` on every loading member.

### 6.9 Comparison allowlist (r1 P9)

Fields excluded from twin equality: the model path or coordinate, every
model digest and identity (`model_digest`, `model_identity`,
`model_sha256`), and `version`. The test asserts each allowlisted field
separately (the includer's identity per T42; the path equals the argument).
Everything else is compared strictly.

### 6.10 Homes

`tools/gnd_layers.json`: `gnd.model._includes` in the `model` layer.
`artifacts.ArtifactSizeError(ArtifactError)` raised at the existing two cap
sites. Component index: `model.loading` lists `_includes.py`, its does and
verbs updated in the same commit; `python3 scripts/components_index.py changed --base main --strict`
before the PR.

### 6.11 Normative prose

New section "Model includes (version 5)" in
`src/gnd/skills/gnd-orm-core/references/representation-format.md`, after
"Fixed reference populations (version 4)": declaration, `fact_type_constraints`,
what an included file may contain, composition, the order of §6.2, refusals,
identity and its scope. The meta-schema `description` gains one sentence
citing it.

## 7. Decisions

| ID | Question | Readings and cost | Proposal |
|---|---|---|---|
| D1 | Reason spelling | `include:*` vs `model:include-*`; the prefix is what JSON consumers match | `include:*`, like `composition:invalid` |
| D2 | Version-5 file without `includes` | (a) allowed, same semantics as version 4, identities differ by `version` (T40); (b) version 5 requires `includes` | (a) |
| D3 | Diagnostic path spelling | prefixed path (§6.6) vs a new `origin` field on `ValidationIssue`, which changes validate JSON for every model | prefixed path |
| D4 | Identity covers include paths? | (a) whole declaration, like the reference envelope; (b) id and sha256 only, so moving the vocabulary file keeps identity | (a) |
| D5 | Included file's `version` | (a) any of 1-4 whose features fit MD3; (b) must equal 5 | (a) |
| D6 | Included file's `model_id` | ignored in the composition, recorded in `_included` | as proposed |
| D7 (r1 P10) | How empty new fields are omitted from `model_dump_json` | (a) a `model_serializer(mode="wrap")` that drops empty `includes` and `fact_type_constraints` (and so also covers `model_dump`); (b) a `model_dump_json` override delegating to pydantic with `exclude`. Chosen by the census: the first that leaves every member byte-identical | (a), falling back to (b) |
| D8 (r1 P5) | Text output line for a refusal | the existing issue line format with the reason as rule id; no new format | as proposed |

## 8. Tests

Files `tests/test_mc1_model_includes.py`, `tests/test_mc1_census.py`,
`tests/test_mc1_guards.py`; fixtures `tests/fixtures/mc1-includes/`
(vocabulary, includer, flattened twin, one hostile file per reason). The
expected reason per hostile file lives in the test module, not the fixture
README. Every refusal case is run once against the loader without `_includes`
and its red output goes into the record.

| # | Case | Expected |
|---|---|---|
| T1 | `load_model` includer vs twin: composed dump equals twin dump plus `includes`, `fact_type_constraints`, `version` | equal |
| T2 | `gnd validate` includer vs twin, text and JSON | exit 0 both; equal outside §6.9 |
| T3 | `gnd check`, violating population | exit 1 both; same findings |
| T4 | `gnd check`, clean population | exit 0 both |
| T5 | `includes` not a list; entry not a mapping; extra key; missing key; duplicate id; 9 entries; empty list | exit 3 `include:declaration` (not `jsonschema:*`) |
| T6 | malformed sha256 (uppercase, 63 chars, non-hex) | exit 3 `include:declaration` |
| T7 | `fact_type_constraints` malformed; present without `includes` | exit 3 `include:declaration` |
| T8 | path `../x`, absolute, `a//b`, backslash, `C:` | exit 3 `include:path` |
| T9 | path is a symlink; an ancestor is a symlink; a directory; missing | exit 3 `include:unreadable` |
| T10 | hash of a file with an added trailing newline | exit 3 `include:hash-mismatch` |
| T11 | file 10 MiB + 1; set over 32 MiB; file growing past the cap during the read (patched reader) | exit 3 `include:size` |
| T12 | included bytes non-UTF-8; not YAML; a YAML list; an alias | exit 3 `include:parse` |
| T13 | included file declares `includes`; `operations`; `reference_populations`; `rejected_proposals`; `fact_type_constraints` | exit 3 `include:forbidden-section` |
| T14 | included file `source` in unattended mode | exit 3 `include:forbidden-section` |
| T15 | includer redeclares an included fact type id | exit 3 `include:collision` |
| T16 | two includes; includer's constraint id equals an id in the second only | exit 3 `include:collision` naming `includes[second]` |
| T17 | included file invalid alone (NaN value, unknown role reference) | exit 3 `include:invalid-included-model` |
| T18 | `fact_type_constraints` names an own fact type; an unknown id | exit 3 `include:unknown-target` |
| T19 | `parse_declarations`, `parse_included`, `declares_includes` called directly on 40 hostile shapes (generated: every JSON type at every position, long integers, NaN, depth 200, non-UTF-8) | a refusal or a bool; never another exception |
| T20 | the schema and `parse_declarations` agree on every T5-T7 shape | same accept/refuse |
| T21 | compound faults: bad path in include 2 + hash mismatch in include 1 → `include:path`; hash mismatch + unparsable → hash, `parse_included` not called; forbidden section + invalid included model → forbidden, standalone validation not called; collision + composed semantic error → collision, composed validation not called | as stated |
| T22 | compose at 1k, 4k, 16k declarations; quadratic mutant | ratio holds; mutant fails it |
| T23 | census (§6.8) | equal to baseline |
| T24 | `gnd validate --identity` over census members | byte-identical |
| T25 | `load_model_bytes` on includer, including one with a malformed declaration | `include:unresolved` |
| T26 | `load_model_bytes_composed` with root | equals T1 |
| T27 | version-5 includer with a reference population owning an included base fact type, path route; check | binds; exit as on the twin |
| T28 | same through `load_model_bytes_composed` | binds |
| T29 | own operation effect asserting a reference-owned included fact type | refused as today |
| T30 | `fact_type_constraints` acyclic ring on an included binary fact type; cyclic population | exit 1, same finding as twin |
| T31 | same, acyclic population | exit 0 |
| T32 | mandatory constraint via `fact_type_constraints`; missing role | exit 1, same finding as twin |
| T33 | an included fact type's own inline constraint plus an includer's on the same fact type | both checked, order: included then includer's |
| T34 | own operation reading included fact types | loads; compiled obligations equal twin's |
| T35 | own derived fact type whose rule reads included fact types | loads; check equals twin |
| T36 | own subtype of an included object type | loads; check equals twin |
| T37 | includer `rejected_proposals` naming an included element id | loads; behaviour as twin |
| T38 | deontic notes from two includes and the includer | order: own, then includes in order |
| T39 | `model_id` precedence: includer's kept; included `model_id` in `_included` only; includer `source` governs | as stated |
| T40 | version-5 file without `includes` vs the same at version 4 | same exits and findings; identities differ by `version` only |
| T41 | one case per §6.7 row | exit 3 (skill scripts: their nonzero) before output |
| T42 | includer identities equal those of its composed dump reloaded | equal |
| T43 | two includers, same composition, different include path | identities differ |
| T44 | anonymous top-level constraint in an include made invalid by the includer | path `includes[<id>]:$.constraints[<i>]` in the included file |
| T45 | issue inside an included fact type reported by an id-selector path | `includes[<id>]:$.fact_types[id=...]...` |
| T46 | import scan: no module outside `gnd.model` imports `_includes` internals other than the public guard functions | passes |

Focused gate:

```bash
uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_census.py tests/test_mc1_guards.py tests/test_schema_sync.py tests/test_model_validation.py tests/test_model_identity.py tests/test_model_v2.py tests/test_compiled_snapshot_obligations.py tests/test_reference_population_corpus.py tests/test_public_reference_budget.py tests/test_evolve_loading.py --tb=short
```

plus each guarded route's own suite (named in the record per §6.7 row),
`uv run ruff check src tests`, the layer-map test, and the whole suite on
beast-3 against the merge-base run (predicate 4 is a whole-suite claim).

## 9. Out of scope for this phase

Supporting any §6.7 route beyond validate and check (MC2); verbalization
header (MC2); evolve and re-pin (MC3); skill and docs text beyond the
normative section (MC4); nested includes and overrides.

## 10. Size

Estimate: about 450 source lines (`_includes.py` 260, loader, `Model` and
serializer 60, schema 60, guards across the §6.7 rows 50, size error and
layer map 20; normative prose not counted) and 800 test lines plus fixtures
and the census baseline. Stop line (plan rule 0.7): 675 source, 1,200 test.

## 11. Approval instrument

This prose. The fixture corpus is authored during implementation; its answer
key lives in the test module, not in the fixture directory's README, so a
later blind pass is possible.
