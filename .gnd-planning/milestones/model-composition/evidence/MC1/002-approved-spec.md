# Phase MC1: model includes — contract, loader, guards, validate and check

## 1. Status

r4, **delegated approval (auto=true), 2026-11-09**; exact bytes bound in 002-execution-gate.md. The plan gate passed on
2026-11-09 (plan r3 approved, MD1-MD16 as proposed; [record](../001-plan.md)).
D1-D8 are ruled as proposed by delegated approval (auto=true), authorized by
the current owner request for the whole model-composition milestone.
Implementation follows the baseline capture and the ruling in record 002.

## 2. Provenance

Derives from [model-composition-plan.md](model-composition-plan.md) r3 (§2,
§4 MC1, §9). Baseline main `459ca8d2`. r1 and r2 of this spec were reviewed
by Codex together with the plan
([r1 review](../evidence/plan-review-r1/codex-review.md),
[r2 review](../evidence/plan-review-r2/codex-review.md); reviewed bytes
retained beside each). **r3 has not been reviewed**; its bytes carry no
review opinion, and plan §11 records why no third round is proposed. Changes
are tagged `(r1 Pn)` and `(r2 Pn)`. Where a finding turned on a runtime fact,
r3 states the required outcome and a test row rather than a mechanism
(review-convergence.md, "Specify decisions, discover facts"). MD1-MD16 were ruled as
proposed, so the sections tagged `[MDn]` stand.

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
| plan predicate 5, MC1-C10 | activation inventory, one guard and one case per admission point | §6.7; T41 |
| MC1-C11 (r2 P19) | version 5 admits temporal syntax; included temporal vocabulary | §6.2 step 11; T47, T48 |
| O22-O25 (r2) | temporal guard; acyclic `_paths` home; PyRel boundary; census lane | §6.2, §6.10, §6.7, §8 gate |
| plan rule 0.3 (r2 P25) | include-free refusal spellings unchanged | §6.10; T49 |
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
   not a mapping. Direct tests T19 call the functions, not the loader
   (r1 P12), and include `compose` itself, with a valid retained descriptor,
   over malformed own sections, unhashable ids and malformed attachment
   entries (r2 P12). `compose` never iterates or looks up an unvalidated
   shape: own sections pass layer 1 (step 3b) before the collision walk. The
   10 MiB cap is applied to the read.
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
| confined relative path | `components_index.py search reference path confined`; `git grep _relative` | `model/__init__.py` `_relative` | adapt: move to leaf `gnd.model._paths`, alias kept in `gnd.model` (r2 P22) |
| no-follow root and bounded read | `search retained root descriptor` | `retained_root`, `artifacts.read_regular_bounded_at` | `retained_root` moves with `_relative`; the reader is reused, its exception classes unchanged (r2 P25) |
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
second statement of the **envelope shape**, held equal to
`parse_declarations` by T20 on shape cases only. Declaration-level
conditions JSON Schema cannot express (unique include ids) are parser checks,
tested there and excluded from the parity claim (r2 P21).

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
def parse_included(raw: bytes, *, include_id: str, path: str) -> dict[str, Any]: ...
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
2. `declares_includes(document)` is true when the document is a mapping
   with an `includes` key **or** a `fact_type_constraints` key (r2 P26);
   otherwise the existing path, untouched.
3. `parse_declarations`: `version` is 5; `includes` is present and a list of
   1..8 mappings with exactly `id`, `path`, `sha256`, unique ids, valid
   hashes; `fact_type_constraints` is absent or a list of mappings with
   exactly `fact_type` and a nonempty `constraints` list → `include:declaration`.
   An orphan `fact_type_constraints` (no `includes`) is refused here, on both
   the path and the bytes routes (r2 P26). Runs **before** layer 1, so these
   inputs report `include:declaration`, not a `jsonschema:*` id (r1 P2).
3b. layer 1 over the including file as written, under the version-5 schema
   (the envelope already passed): existing `jsonschema:*` refusals for
   malformed own elements, so no later step iterates an unvalidated shape
   (r2 P12).
4. each path through `_relative` → `include:path`.
5. each read under the descriptor, no follow → `include:unreadable`; a read
   refused for size (pre-read oversize, growth past the cap) and the 32 MiB
   set total → `include:size` (r1 P13). How the resolver tells size apart is
   an implementation fact pinned by T11; existing callers observe the same
   exception classes and spellings as before (T49, r2 P25).
6. each raw sha256 against its declaration → `include:hash-mismatch`. A
   mismatched file is never parsed.
7. `parse_included` through the existing suffix-sensitive
   `parse_model_document` with `source` set to the declared path, so a
   `.json` include requires strict JSON exactly as standalone `gnd validate`
   does (r2 P24); any refusal, and a non-mapping result → `include:parse`
   (r1 P3, P12).
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
    with every version gate widened to admit 5: temporal syntax in
    `_rule_temporal_language`, `_validation.py:4586`, r2 P19); issue paths
    remapped per §6.6.
12. `Model.model_validate`; `_provenance` and `_included` set;
    `validate_declarations` accepts version 4 or 5 (`model/__init__.py:499`,
    r1 P4); compiled obligations.
13. reference binding: `_load_model_no_follow` as today; the new
    `load_model_bytes_composed(data, *, source, root)` binds under the same
    retained root and returns the model with its context attached.

`load_model_bytes(data, *, source)`: after step 1, an orphan
`fact_type_constraints` refuses `include:declaration`; otherwise, if
`includes` is present, refuse `include:unresolved` before any other include
step, so a bytes-only caller with a malformed `includes` also reads
"unresolved" (stated; T25 pins both). The historical symlink fallback of `load_model` admits only
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

No identity function changes. Measured, without reloading a composed dump
through an authored-document loader (r2 P20): T42 assembles the expected
loaded content independently (the twin's loaded content plus the
`includes` and `fact_type_constraints` declarations and `version: 5`),
builds each existing identity envelope over it with its existing exclusions
(`warnings` and `operations` for `_model_digest`; also
`reference_populations` for the canonical identity), and compares with the
includer's identities; T42b mutates content (one included fact type's
reading) and declarations (one include path) separately and shows each
mutation moves the identities; T43, two includers with the same composition
and different include paths have different identities (D4).

### 6.6 Diagnostics

`remap_issue_path(path, provenance)` reads the leading address of an issue
path, in either form the validators emit (`$.fact_types[3]...` or
`$.fact_types[id=X].constraints[2]...`, `_validation.py:316-320`), and
resolves the **deepest** matching provenance entry (an inline constraint
before its host fact type; r2 P11), by composed address and by id for the
selector form. An element whose origin is an include is reported as
`includes[<id>]:<original address><rest>`. An own element at its authored
position keeps its path unchanged (r1 P11). An own constraint attached to an
included fact type by `fact_type_constraints` is reported at its authored
address, `$.fact_type_constraints[<i>].constraints[<j>]<rest>`, never under
the include (r2 P11). Warnings are remapped the same way.

### 6.7 Activation inventory and guards [MD15] (r1 P16)

One rule for every guarded route: before it calls any loader, hashes or
copies the model, it reads the authored document (or the bytes it already
holds), calls `declares_includes`, and on true calls
`refuse_unsupported(<route>)`, which raises the route's existing input
refusal carrying `include:unsupported-route`, exit 3, before any output
(r2 P16). The public `load_model_bytes` keeps its own `include:unresolved`
contract for API callers; it is not a route guard. One admission point per
row, each with its own T41 case; the implementation's first step re-reads
each and may add rows, never merge them.

| # | Admission point | Today | MC1 |
|---|---|---|---|
| R1 | `gnd validate`, `gnd check` (path) | `load_model` | supported (composes) |
| R2 | witness service `_witness_inputs` | `load_model_bytes` | guard |
| R3 | witness io (in-memory `model.orm.json`) | rebuilt document | guard |
| R4 | judgments (`judgments.py:504`) | `load_model_bytes` | guard |
| R5 | `api.py:1123` | `load_model_bytes` | guard |
| R6 | population compose API (`api.py:980`) | `load_model_bytes`, refusal collapsed to "invalid model" | guard before the load; the refusal message is `include:unsupported-route`, a spelling change only for include-bearing input; no composed output written |
| R7 | exp `session.py` (tempfile) | copy then `load_model` | guard before the copy |
| R8 | exp `session_contract` | `load_model_bytes` | guard |
| R9 | exp `session_replay` | `load_model_bytes` | guard |
| R10 | exp `session_judgments` | `load_model_bytes` | guard |
| R11 | export Lean (`lean_io.py`) | raw bytes, own parse | guard |
| R12 | export Souffle (`souffle_io.py`) | raw bytes, own parse | guard |
| R13 | export PyRel rules (`pyrel_rules.py:2264`) | `load_model_bytes` plus own parse | guard |
| R14 | export `render_pyrel` (`emit.py:22`) | raw text embedded | guard before embedding (r2 P23) |
| R15 | GND-side calls into `pyrel_runtime` (oracle) | runtime's own parse | guard at each GND call site; `pyrel_runtime.py` is not edited, so the runtime still imports no GND module and every exported include-free program is byte-identical (r2 P23) |
| R16 | export applications (`applications.py`) | copies | guard before the copies |
| R17 | export ILP service | capped bytes, hash | guard |
| R18 | discover service | capped bytes, hash | guard (MC3 supports) |
| R19 | evolve `_load_model_document` | `load_model_bytes` | guard (MC3 supports) |
| R20 | batch | hash then `load_model` | guard before the hash |
| R21 | checking-service composition verify | raw bytes | guard |
| R22 | codegen manifest and emit | hash | guard |
| R23 | conformance currency and service | hash, then `load_model` | guard before currency |
| R24 | extract service | hash | guard |
| R25 | fidelity, doccheck services | hash | guard |
| R26 | measure service | hash before and after `load_model` | guard |
| R27 | recovery verify | copy then `load_model` | guard before the copy |
| R28 | `gnd import rai-orm` | copy then `load_model` | guard (its output is a new model; an includer target is refused) |
| R29 | skill scripts `validate_model.py`, `verify_migration.py` | standalone parse, no gnd import | local check for `includes` or `fact_type_constraints`, own nonzero exit, message cites `gnd validate` |
| R30 | examples | `json.loads` | none: examples ship no includer, and T41 asserts it |

T41 is one case per row R2-R30: an include-bearing model through the route
exits 3 (R29: the scripts' own nonzero) before writing any output. T50
asserts `pyrel_runtime.py`'s bytes are unchanged from `459ca8d2` and the
existing no-GND-import test still passes; T51 renders one include-free PyRel
export and compares it byte for byte with `459ca8d2`'s.

### 6.8 Census (r1 P15)

`tests/test_mc1_census.py`, marked `census` (r2 P27), enumerates
`git ls-files '*.orm.yaml' '*.orm.json'` (300 and 100 at `459ca8d2`). For
each member it records each observable **independently** as a value or a
refusal with its rule id and path (r2 P15): load (through `load_model`, so
references bind where declared), `model_dump`, `model_dump_json`,
`_model_digest`, `model_identity`, `reference_model_digest` and
`gnd validate --identity` (exit and output). The surrogate fixture
(`tests/fixtures/rof3-model-identity/models/surrogate.orm.json`) is the
known member that loads while its canonical identity refuses; the census
records both. The baseline, produced at `459ca8d2` on beast-3 by a committed
script, is compared value for value. A file added or removed after the
baseline fails the census until the baseline is regenerated by that script,
with the counts printed.

### 6.9 Comparison allowlist (r1 P9)

Fields excluded from twin equality: the model path or coordinate, every
model digest and identity (`model_digest`, `model_identity`,
`model_sha256`), and `version`. The test asserts each allowlisted field
separately (the includer's identity per T42; the path equals the argument).
Everything else is compared strictly.

### 6.10 Homes

`tools/gnd_layers.json`: `gnd.model._includes` and `gnd.model._paths` in the
`model` layer. `_relative` and `retained_root` move to the leaf
`gnd.model._paths` (no `gnd.model` import), keep explicit identity aliases
in `gnd.model` listed in the milestone shim inventory, and every patch site
of them in tests is updated to the defining home (AGENTS.md "Refactoring
dependency homes"); `_includes` imports `_paths`, never `gnd.model`, and
`tests/test_rf8_structure.py` (no runtime SCC) is in the gate (r2 P22). No
exception class raised by `artifacts` changes; any size signal the resolver
needs is internal to the include path, and T49 shows an oversized
include-free model through `gnd diff` still reports
`diff:invalid-model:ArtifactError` (r2 P25). Component index: `model.loading` lists `_includes.py`, its does and
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
| T7 | `fact_type_constraints` malformed; present without `includes`, through `load_model`, `gnd validate` and `load_model_bytes` | exit 3 `include:declaration` on every route (r2 P26) |
| T8 | path `../x`, absolute, `a//b`, backslash, `C:` | exit 3 `include:path` |
| T9 | path is a symlink; an ancestor is a symlink; a directory; missing | exit 3 `include:unreadable` |
| T10 | hash of a file with an added trailing newline | exit 3 `include:hash-mismatch` |
| T11 | file 10 MiB + 1; set over 32 MiB; file growing past the cap during the read (patched reader) | exit 3 `include:size` |
| T12 | included bytes non-UTF-8; not YAML; a YAML list; an alias; YAML-only content at a `.orm.json` path | exit 3 `include:parse` (r2 P24) |
| T12b | strict JSON vocabulary at a `.orm.json` path; YAML vocabulary at a `.orm.yaml` path | both compose |
| T13 | included file declares `includes`; `operations`; `reference_populations`; `rejected_proposals`; `fact_type_constraints` | exit 3 `include:forbidden-section` |
| T14 | included file `source` in unattended mode | exit 3 `include:forbidden-section` |
| T15 | includer redeclares an included fact type id | exit 3 `include:collision` |
| T16 | two includes; includer's constraint id equals an id in the second only | exit 3 `include:collision` naming `includes[second]` |
| T17 | included file invalid alone (NaN value, unknown role reference) | exit 3 `include:invalid-included-model` |
| T18 | `fact_type_constraints` names an own fact type; an unknown id | exit 3 `include:unknown-target` |
| T19 | `parse_declarations`, `parse_included`, `declares_includes` and `compose` (with a valid retained descriptor) called directly on generated hostile shapes: every JSON type at every position, long integers, NaN, depth 200, non-UTF-8, malformed own sections, unhashable ids (`{"id": []}`), malformed attachment entries | a refusal or a bool; never another exception (r2 P12) |
| T20 | the schema and `parse_declarations` agree on every T5-T7 **shape** case; duplicate include ids are refused by the parser and admitted by the schema, asserted as such | as stated (r2 P21) |
| T21 | compound faults: bad path in include 2 + hash mismatch in include 1 → `include:path`; hash mismatch + unparsable → hash, `parse_included` not called; forbidden section + invalid included model → forbidden, standalone validation not called; collision + composed semantic error → collision, composed validation not called | as stated |
| T22 | compose at 1k, 4k, 16k declarations; quadratic mutant | ratio holds; mutant fails it |
| T23 | census (§6.8), marked `census`, broad lane | every observable equal to baseline, values and refusals |
| T24 | `gnd validate --identity` over census members (part of T23's observables) | equal to baseline, the surrogate's exit-3 refusal included |
| T25 | `load_model_bytes` on an includer, one with a malformed `includes`, and an orphan `fact_type_constraints` | `include:unresolved`, `include:unresolved`, `include:declaration` |
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
| T41 | one case per §6.7 row R2-R30, each its own test id | exit 3 (R29: their nonzero) before output |
| T42 | includer identities vs envelopes built over independently assembled expected content (§6.5) | equal (r2 P20) |
| T42b | content mutation; declaration mutation | each moves the identities |
| T43 | two includers, same composition, different include path | identities differ |
| T44 | anonymous top-level constraint in an include made invalid by the includer | path `includes[<id>]:$.constraints[<i>]` in the included file |
| T45 | issue inside an included fact type reported by an id-selector path | `includes[<id>]:$.fact_types[id=...]...` |
| T45b | an included host fact type carrying an included inline constraint and a project-owned attached one; an error and a warning in each | included ones under `includes[<id>]:`; project ones at `$.fact_type_constraints[<i>].constraints[<j>]` (r2 P11) |
| T46 | import scan: no module outside `gnd.model` imports `_includes` internals other than the public guard functions; `_includes` and `_paths` do not import `gnd.model`; no runtime SCC | passes (r2 P22) |
| T47 | temporal model at version 4 and the same at version 5 | same exits and findings (r2 P19) |
| T48 | version-5 includer whose included temporal vocabulary is version 3 or 4 | composes; temporal findings as on the twin |
| T49 | oversized include-free model through `gnd diff` | `diff:invalid-model:ArtifactError`, as at `459ca8d2` (r2 P25) |
| T50 | `pyrel_runtime.py` bytes vs `459ca8d2`; existing no-GND-import test | unchanged; passes (r2 P23) |
| T51 | one include-free PyRel export vs `459ca8d2`'s output | byte-identical |

Focused gate:

```bash
uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_schema_sync.py tests/test_model_validation.py tests/test_model_identity.py tests/test_model_v2.py tests/test_compiled_snapshot_obligations.py tests/test_reference_population_corpus.py tests/test_public_reference_budget.py tests/test_evolve_loading.py tests/test_rf8_structure.py tests/test_pyrel_export.py --tb=short
```

under the default lane filter, plus each guarded route's own suite (named in
the record per §6.7 row), `uv run ruff check src tests` and the layer-map
test. Separately, on beast-3, the broad lane for the census, its output
retained in the record (r2 P27):

```bash
uv run pytest -q -m "evidence or census" tests/test_mc1_census.py --tb=short
```

and the whole default suite against the merge-base run (predicate 4 is a
whole-suite claim).

## 9. Out of scope for this phase

Supporting any §6.7 route beyond validate and check (MC2); verbalization
header (MC2); evolve and re-pin (MC3); skill and docs text beyond the
normative section (MC4); nested includes and overrides.

## 10. Size

Estimate: about 500 source lines (`_includes.py` 260, `_paths.py` move and
aliases 20, loader, `Model` and serializer 60, schema 60, temporal gate 5,
guards across the 29 §6.7 rows 80, layer map 15; normative prose not
counted) and 950 test lines plus fixtures and the census baseline. Stop line
(plan rule 0.7): 750 source, 1,425 test.

## 11. Approval instrument

This prose. The fixture corpus is authored during implementation; its answer
key lives in the test module, not in the fixture directory's README, so a
later blind pass is possible.


## 12. Execution amendment r4 and implementability sweep (2026-11-09)

Delegated rulings (auto=true), current owner authorization:
`process-milestone model-composition auto`. D1-D8: adopt every proposal;
D7 remains a measurement choice with the stated fallback. Optional further
spec review omitted: the previous convergence stop stands. One Codex CLI
reviewer is selected for phase diffs by plan section 8; the owner now also
explicitly selects one Codex CLI reviewer for close, overriding the panel
requirement. One reviewer is one reviewer.

Approval instrument: prose, retaining section 11's choice. This departs
from the corpus-first default because the existing spec already fixes T1-T51
and their expected exits, twice-reviewed plan/spec snapshots fix the prior
answers, and MC1 must still retain pre-implementation red refusal evidence.
A separate corpus approval would duplicate those answer decisions; it would
not replace the hostile-shape, compound-fault, identity, scaling-mutant or
compatibility controls. New implementation cases remain separately identified.

The implementability sweep identified two acyclic-home repairs:

- Move `parse_model_document(data: bytes, *, source: str | Path) -> Any`
  verbatim into `gnd.model._validation`, retaining an explicit identity alias
  in `gnd.model`. `_includes.parse_included` imports its defining home.
- Move `ReferenceInputError` unchanged into `gnd.errors`, preserving its
  public `__module__ = "gnd.model"` and explicit alias in `gnd.model`.
  `_paths` imports it from errors. Its model annotation is type-only.

Both moves enter the historical shim inventory and source scan coverage.
They add no new refusal spelling and no runtime import allowance. These
repairs supersede section 6.10 only as to these two defining homes.

Additional sweep decisions: guarded routes retain their existing error
adapters; guards supply a shared `ModelValidationError` issue before work,
and adapters must preserve its reason. No unrelated parser becomes stricter.
The declared-order validation stages remain as section 6.2; included JSON
suffixes retain their parser semantics. Own attachments are validated once
at their authored location and once in the composed target context; the
collision walk counts each active constraint once, at its composed location.
The scaling timing isolates merge/id indexing from existing schema/semantic
validation, with warm-up and repeated medians for each workload and mutant.

All milestone rules 0.1-0.7 are discharged: one loader resolver, admission
inventory guards, census-frozen include-free variants, no included-file
writer, no new freshness claim, measured identities/refusals, and the
750-source/1,425-test stop. No per-phase publication or merge is delegated.
The dependency remains: full baseline and census captured before production
edits; MC2 and MC3 do not begin before MC1's completed record and review.

### Verification-selection ledger

Each run expects exit 0 unless an explicit negative control is named.
No evidence is inherited as a current-byte pass.

| Obligation | Disposition | Command / evidence | Input boundary | Invalidation / justification |
|---|---|---|---|---|
| MC1-C1..C11 direct tests | run | focused command in section 8 | loader, schema, identities, fixtures | rerun for changed behavior; covers every new branch |
| Route consumers | run | `uv run pytest -q tests/test_mc1_guards.py tests/test_evolve_loading.py tests/test_pyrel_export.py tests/test_public_reference_budget.py --tb=short`; add each actual guarded route's direct tests when its adapter is edited | guard predicate and each public adapter | every admission point gets its own parameter id; enumerate any newly found sites in the implementation findings |
| Import layers | run | `uv run pytest -q tests/test_rf8_structure.py::test_graph_and_each_dirty_direction --tb=short` | source modules, tools/gnd_layers.json | no runtime SCC, wrong-way edge or missing home |
| Lint | run | `uv run ruff check src tests` | all source and tests under configured ruff | required project lint; record known-red separately if observed |
| Components | run | `python3 scripts/components_index.py changed --base d2d6309b --strict` | component entries, generated views, changed modules | regenerate with code; reread each changed component |
| MC1-C5 census | run, explicitly selected by owner 2026-11-09 | `uv run pytest -q -m "evidence or census" tests/test_mc1_census.py --tb=short` on beast-3; producer baseline at 459ca8d2 | tracked *.orm.yaml/*.orm.json manifest, per-observable outputs, source and toolchain | compare baseline/candidate values and refusals; dirty negative control must fail |
| Full default compatibility | run, explicitly selected by owner 2026-11-09 | `uv run pytest -q --tb=short` on beast-3 at 459ca8d2 and candidate | locked dependencies, default addopts, all default tests | preserve lane exclusions; compare known reds and new failures; skipped lanes establish no pass |
| Other excluded lanes | cadence | separately selected CI/owner lane | native/provider/distribution/proof/historical data | no selection for unrelated historical or certification work |

The baseline archive uses `git archive 459ca8d2` and a manifest produced by
`git ls-tree -r --name-only 459ca8d2`. The committed producer accepts that
manifest for archive execution (there is no .git inside an archive), retaining
exact relative paths. Candidate collection uses `git ls-files`; only original
baseline members are compared, with new MC1 fixture membership separately
printed and tested. This explicitly amends section 6.8's blanket membership
rule, which otherwise conflicts with section 8's required new *.orm fixtures:
MC1 additions are not historical baseline members. A missing baseline member
still fails. No prior member's expected answer is regenerated on candidate code.

## 13. Implementation findings

- 2026-11-09, preparation: parser and exception initializer dependencies,
  resolved by section 12 before implementation; no source edited at discovery.
- 2026-11-09, preparation: requiring the census's tracked-file set never to
  grow conflicts with the mandatory MC1 *.orm fixtures. Section 12 admits
  separately enumerated new fixtures without weakening comparisons for
  the frozen 400 historical files. Retain this plan-repair row at close.
