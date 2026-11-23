# Phase VG1 · checker cost in the number of object types · spec r3

## 1. Status

**Approved by delegated ruling (auto=true), 2026-11-23** `(d)`: the owner
invoked `process-milestone reviewed-vocabulary-growth auto` on 2026-11-23,
which delegates spec rulings within this milestone. That is the driving
agent's ruling under the delegation, not the owner's reading of the spec.
The ruled bytes are r3 of this file (§7, the ruling paragraph). Prior status,
kept: "Draft, awaiting owner review. Implementable once the plan gate approves
the plan and the owner signs off this spec." Written by `start-milestone`
on 2026-11-22; `process-phase` has not run and no owner gate is recorded. r2
of 2026-11-23 follows plan r2: its changes are tagged `(p1)` where a panel
finding caused them and `(m)` where the author corrected them. Plans r3 and
r4 changed nothing about VG1, so this spec is still r2; only this paragraph
and the first line of §2 name the newer plan.

## 2. Provenance

- Derives from [plan r4](reviewed-vocabulary-growth-plan.md), Goal (VG1), §0
  (R0.1, R0.2), §1 (H1–H10, H27–H29), §2 (VG1), §4 (VG1-C1 to VG1-C8), §9
  (the VG1 lane) and §10 (D9, D10, D12). The plan was reviewed once, at r1.
  The owner approved plan r4 on 2026-11-23
  ([plan gate](../001-plan-gate.md)) `(d)`.
- From [#221](https://github.com/vasiloglou/gnd-public/issues/221) and the
  include-root-routes IR1 spec, finding i1
  (`../../include-root-routes/notes/phase-IR1-spec.md`).
- The plan review of 2026-11-23 had plan r1 as its subject. Five of its 22
  concerns are about VG1 and are answered here and in plan r2. No review has
  had this spec as its subject. Round 2, which had plan r2 as its subject,
  reached no quorum and raised nothing about VG1.
- Every code citation was read at `4ad0d216`. Measurements were run on that
  commit on 2026-11-22, on one laptop, once each unless a row says otherwise.
- r3 `(d)`, 2026-11-23: this spec is executed from `main` at `1f403b07`.
  `git diff 4ad0d216 1f403b07` is empty for `universe.py`, `model_index.py`,
  `model_queries.py` and `semantic_adapter.py`, so every citation holds there.
  The `(d)` changes are the implementability findings and rulings below; no
  review has read them.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H1, H2; #221 | `gnd check` is superlinear in object types; 36.84 of 37.65 s at 300 extra value types is under `universe._denoting_types` | §6 design; T3, T9 |
| plan H3 | the walk runs twice per object type in `adapt_snapshot` (`semantic_adapter.py:610-611`, `:707`) | §6 (both calls read the table); T9 |
| plan H4 | entity types with their own value types are superlinear; `_descendant_closure` and `_kind_of` rebuild or scan per call | §6; T4, T9 |
| plan H5 | extra fact types are not superlinear | T7 (control) |
| plan H6 | validate, flatten, export, coverage and extract are not affected | §9 (not changed, not tested here) |
| plan H7, D10 | `gnd judgments check` runs the checker twice | T8 (bound only); §9 |
| plan H8 | IR1's route-level T9 was withdrawn | T8 restores it in `tests/test_ir1_judgments_includes.py` |
| plan H10, D9 | the witness oracle has its own walk | §7 VG1-D5; the experiment |
| plan H4a, D12 | a deep subtype chain stays slow | §9; the experiment records it |
| plan H29 | the prototype's bounds | §7 VG1-D6 |
| plan R0.1, VG1-C6 | no report changes | T10 |
| plan R0.2, VG1-C1 | the table equals the function it caches | T1, T2 |
| VG1-C2 | 1,000 extra value types, under 10 s in process | T3 |
| VG1-C3 | three more shapes and the fact-type control, same bound | T4, T5, T6, T7 |
| VG1-C4 | 2,000 costs at most 3 times 1,000, four shapes | T11 |
| VG1-C5 | `gnd judgments check` under 20 s at 1,000 | T8 |
| VG1-C7 `(p1)` | one check builds the supertype map the same number of times at two sizes, at most 100 | T9 |
| VG1-C8 `(p1)` | `gnd verify` at 1,000 extra value types is measured at the base commit and at the head; over 10 s, the witness oracle gets its own table | VG1-D5; the experiment, which records both figures |
| plan §4, "Which gate is which" `(p1)` | the gates that read no clock are the required regression gates | T1, T9, T10 (§8, closing paragraph) |
| plan §9 | the VG1 lane, the guard block, `uv run ruff check src tests tools` | §8, closing paragraph |
| plan H28 | component index updated in the same commit | §6, reuse table; §8 |
| `AGENTS.md`, "Refactoring dependency homes" | moved names keep explicit identity aliases; patch the defining home | §6 (`universe.py`: names, aliases and `__module__` lines unchanged) |
| `AGENTS.md`, "Model queries and family dispatch" | prefer the read-only `ModelIndex` snapshot for shared model queries | §6; VG1-D1 |

## 4. The standing rules, bound to this phase

- **Totality (project rule 1).** The table builder reads the rows of a
  loaded `Model`, not untrusted JSON. It is total wherever
  `_descendant_closure`, `_denoting_types` and `_kind_of` are today: a subtype
  cycle (admitted by validation, `universe.py:230-234`), a `subtype_of` that
  names no declared type, an entity type with no reference, a row whose `id`
  is `None`. T2 holds each.
- **A cap bounds the document, not the algorithm (rule 2).** This phase is
  that rule applied late. T3–T8 are time-bound tests over the layer changed.
  T9 pins a call count that must not grow with the model, which does not
  depend on the machine.
- **Validation order (rule 3).** Inapplicable: the phase adds no refusal and
  no validation boundary.
- **One walk for N kinds (rule 4).** The three universe walks read one set
  of tables built in one place. The witness oracle's copy
  (`synth/oracle/constructive.py:131`) is separate by its own contract and
  stays so (plan R0.2).
- **One home for normative prose (rule 5).** No normative page changes.
  `resolve_reference_value_type`'s docstring stays the definition of
  denotation; the table's docstring cites it.
- **Measurement, not argument (rule 6).** Whether the index's dumped rows and
  the model's live rows give the same tables is settled by T1 over every
  loadable fixture, not argued. The bounds come from the prototype (plan
  H29).
- **Plan R0.1** (reports do not move): T10. **R0.2** (one denotation): T1.
  **R0.3–R0.7** concern validation, includes and `gnd evolve`; this phase
  changes none of them.

## 5. Goal

`gnd check` on the interop checking root with 1,000 extra object types, in
each of four shapes, returns the same exit code and the same constraint
verdicts as with none, in under 10 s in process; 2,000 extra types cost at
most 3 times 1,000; the number of times one check builds the supertype map
does not depend on the number of object types. The focused lane, the guard
block and `uv run ruff check src tests tools` exit 0.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| which value type denotes an object type | `components_index.py search "denoting types universe reference value type"`; `git grep -n resolve_reference_value_type src/gnd` | `check.universe`: `universe.resolve_reference_value_type` (`:59`), `_denoting_types` (`:258`) | reuse the function as the definition; adapt `_denoting_types` to read a table |
| a per-model table shared by one public call | `components_index.py search "model index snapshot"`; `git grep -n "index_scope" src/gnd` | `model.query_index`: `ModelIndex`, cached by content digest and by call scope (`model_index.py:52-71`, `:122-170`) | adapt: add the tables to `ModelIndex` (VG1-D1) |
| subtype descendants of an object type | `components_index.py search "subtype closure descendants"`; `git grep -n "_descendant_closure\|supertype_closure" src/gnd` | `universe._descendant_closure` (`:218`); `ModelIndex.supertype_closure` (`:264`, the opposite direction) | adapt `_descendant_closure` to read a children table |

Nothing existing computes these per model. `dev/components/` entries for
`check.universe` and `model.query_index` change in the same commit.

### `src/gnd/model_index.py` (about +55 lines)

Three read-only tables, built on first use and kept on the index. They are
private to the package; the three universe walks are their only readers.

```python
def reference_value_types(self) -> Mapping[str, str | None]:
    """object-type id -> the value type that denotes it, or None.

    A cache of gnd.universe.resolve_reference_value_type, which stays the
    definition: built by the same walk (model_queries._resolve_reference with
    _identifying_id) over one object map and one supertype map."""

def denoted_by(self, value_type_ids: Iterable[str]) -> set[str]:
    """Object types whose resolved value type is one of value_type_ids."""

def subtype_children(self) -> Mapping[str, frozenset[str]]:
    """declared id -> ids that name it in subtype_of (direct children)."""

def kind(self, identifier: str) -> str | None:
    """The kind of the first declared object type with this id, or None."""
```

- The maps are built once per index: one pass over the object types for
  `kind` and `subtype_children`, and one `_resolve_reference` call per object
  type for `reference_value_types`. That last pass costs the number of object
  types times the inheritance depth, which is what makes a deep chain
  expensive (§9).
- Returned mappings are read-only views (`types.MappingProxyType`) and
  `denoted_by` returns a new set, so a caller cannot write into the cache
  (the module's own rule, `model_index.py:102`).
- `kind` keeps `_kind_of`'s first-match reading (`universe.py:358-363`);
  `reference_value_types` keeps the last-duplicate reading of
  `ModelIndex.object_map` (`:173-176`). A loaded model has unique ids, so the
  two agree there; T2 holds both for a `Model` built in code.

### `src/gnd/universe.py` (about 40 lines changed)

Signatures, names, the identity aliases (`:377-388`) and the `__module__`
lines (`:396-429`) do not change.

- `_denoting_types(covered, model)` returns
  `ModelIndex.for_model(model).denoted_by(covered) - covered`.
- `_descendant_closure(object_type_id, model)` walks
  `subtype_children()` from `object_type_id` with a seen set. It returns the
  same set the fixpoint returns, cycles included.
- `_kind_of(object_type_id, model)` returns `kind(object_type_id)`.
- `resolve_reference_value_type` is not changed (VG1-D2).

### `src/gnd/semantic_adapter.py` (0 to 3 lines)

`adapt_snapshot` (`:592`) keeps both calls (`:610-611`, `:707`); each is now a
table read. Under VG1-D4 it also opens `index_scope()` so a direct caller
gets the reuse. `gnd.semantic_adapter` is in the `checking` layer and
`gnd.model_index` in `model` (`tools/gnd_layers.json`), so the import is
downward.

### What does not change

The checker families, `_instance_values_of` (it still walks every fact type
once per object type, `universe.py:343-355`), the witness oracle, every
report and every CLI surface.

## 7. Decisions

Ruled by delegated approval (auto=true) on 2026-11-23 `(d)`, each as
proposed: VG1-D1 (a), VG1-D2 (a), VG1-D3 (a), VG1-D4 (a), VG1-D5 as stated,
VG1-D6 10 s, ratio 3, `gnd judgments check` 20 s. Budget: one diff review
round through the review helper (plan D7). Compatibility: no report, schema,
CLI flag or exit code changes (plan R0.1). Prior line, kept: "Every row is
open."

| ID | Question | Readings and their cost | Proposed |
|---|---|---|---|
| VG1-D1 | Where the tables live | (a) on `ModelIndex`: one cache, shared by a call scope and by content digest; reads the index's dump of the model, which for a `Model` built in code can differ from its live rows (the limit the owner accepted on 2026-11-11, `maintenance/2026-11-11-query-budget-headroom/README.md`). (b) in `universe.py`, keyed by the model object inside a call scope, built from live rows: exact for code-built models, and a second cache with its own lifetime rules | (a). No exit code differs between them for a loaded model; T1 measures it |
| VG1-D2 | Does `resolve_reference_value_type` itself read the table | (a) no: it stays the uncached definition; its other callers (`admission.py:28`, `refscheme.py:133`, `synth/poolfile.py:371`, `:626`, `synth/boundary.py:1189`) keep today's cost. (b) yes: every caller gets the table, and a caller outside a call scope pays one model digest per call (`model_index.py:139-170`), more than today's two map builds | (a). The measured cost is in the universe walks only |
| VG1-D3 | Which lane runs the ratio test T11 | (a) the default lane: about 25 s more, and a ratio over wall time can fail on a loaded machine. (b) the `slow` lane (`pyproject.toml:79`): never a gate unless selected, so the ratio is unguarded in ordinary work | (a), with the minimum of three runs per size and the ceiling at 3 where the prototype measured 2.1 to 2.2. T9's call count is the guard that does not depend on the machine |
| VG1-D4 | Does `adapt_snapshot` open an index scope | (a) yes: a direct caller of the adapter gets one index, not one digest per walk. (b) no: only entry points open scopes, as today | (a); `index_scope` is re-entrant (`:62-71`) |
| VG1-D5 | The witness oracle's walk (plan D9) | measured in the experiment below through `gnd verify`. Over 10 s at 1,000 extra value types: this phase gives `constructive._denoting_types` its own table inside `constructive.py`, importing nothing from `universe` or `model_index`, and adds a case. Under: recorded, not changed | as stated |
| VG1-D6 | The bounds | 10 s at 1,000 and a ratio of 3. The prototype measured 0.48 to 1.29 s at 1,000 and ratios 2.1 to 2.5 (plan H29) on one laptop. A tighter bound fails sooner on a slow runner; a looser one admits a quadratic regression at this size | 10 s and 3; `gnd judgments check` 20 s |

## 8. Tests

New file `tests/test_vg1_object_type_scaling.py`, default lane. A helper
grows the interop example (`gnd.examples.literature.interop.build(out)`): it
appends object types to `vocabulary/chronology.orm.json` and re-pins both
roots. Shapes: `values` (N unused value types); `entities` (N/2 value types
and N/2 entity types, each entity referenced by its own value type);
`shared` (one value type and N entity types referenced by it); `tree` (one
value type, N/100 root entity types, 9 subtypes per root and 10 per subtype,
all with `inherits_reference`); `both` (N value types and N binary fact
types over them).

| # | Case | Expected |
|---|---|---|
| T1 | for every model that loads under `src/gnd/examples/` and `tests/fixtures/`, and every object type: `reference_value_types()[id]` equals `resolve_reference_value_type(id, model)`; `_denoting_types`, `_descendant_closure` and `_kind_of` equal frozen copies of their bodies at `4ad0d216`, kept in the test file; `_universe_types` equals a frozen copy that calls those frozen walks `(m)` | equal; the count of models compared is asserted to be at least 200 |
| T2 | a `Model` with a two-type subtype cycle; one whose `subtype_of` names an undeclared id; an entity type with no reference; a subtype with two supertypes resolved by two value types; a code-built `Model` with a duplicate id | each walk returns what its frozen copy returns; no exception |
| T3 | `values`, N = 1,000: `gnd check` in process on the checking root | exit and constraint verdicts equal to N = 0; under 10 s |
| T4 | `entities`, N = 1,000 | as T3 |
| T5 | `shared`, N = 1,000 | as T3 |
| T6 | `tree`, N = 1,000 | as T3 |
| T7 | `both`, N = 1,000 (control for fact types) | exit 4 as the fixture gives; under 10 s |
| T8 | `values`, N = 1,000: `gnd judgments check` with the policy and receipts of IR1 T1 | outcome 0 or 1; under 20 s. The same case is restored as a route-level row in `tests/test_ir1_judgments_includes.py`, beside the composition-only T9 |
| T9 | `values`, N = 300 and N = 600: count calls of `gnd.model_queries._supertype_parents` during one `gnd check` | the same count at both sizes, and at most 100 (today 184,876 at 300, of which the universe walk makes 184,830 and every other caller 46, by the two profile counts of plan H2). Negative control: with `_denoting_types` patched back to its frozen copy the count at 300 is over 1,000 |
| T10 | the existing focused lane, unmodified: `tests/test_reference_universe.py`, `tests/test_subtype_universe.py`, `tests/test_public_semantic_adapter.py`, `tests/test_rf1_semantic_pins.py` | exit 0, no golden changed |
| T11 | for `values`, `entities`, `shared`, `tree`: the minimum of three in-process runs at N = 2,000 over the minimum of three at N = 1,000 | at most 3.0 |
| T12 | a direct call of each walk outside any index scope, and a second call after the model object is replaced by an equal one | the same answers as inside a scope |
| T13 | the returned mappings refuse item assignment, and mutating the set `denoted_by` returns does not change the next answer | `TypeError`; equal answers |

Branch table. The tables have four branches: a value type (denotes
itself), an entity with its own reference, an entity that inherits, an
unresolvable type. T1 reaches all four on the fixtures (the test asserts each
branch was seen at least once); T2 adds the cycle and the two-supertype
cases, which no loadable fixture is guaranteed to hold.

Gate: the plan §9 VG1 lane with this file, the guard block of `project.md`,
`uv run ruff check src tests tools`, and
`python3 scripts/components_index.py changed --base origin/main --strict`.

### Verification-selection ledger `(d)`

| Obligation | Disposition | Command or evidence | Input boundary | Justification | Invalidation |
|---|---|---|---|---|---|
| VG1-C1, C2, C3, C4, C6, C7; T1–T13 | run | `uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short`, exit 0 | `universe.py`, `model_index.py`, `semantic_adapter.py`, the interop fixture, the loadable fixture models | the plan §9 VG1 lane as written, plus the new file | any change to those modules or to the fixture |
| VG1-C5; plan H8 | run | the same command (T8 lives in `tests/test_ir1_judgments_includes.py`) | as above, and the judgments route | the route the bound names | as above |
| Structure and inventory guards (`project.md`, issue 171) | run | the guard block of `project.md`, exit 0 | every file outside `.gnd-planning/` | the phase changes source files | any source change |
| Lint | run | `uv run ruff check src tests tools`, exit 0 (plan D11) | `src`, `tests`, `tools` | the whole-repository command exits 1 on dev-tools scripts (plan H27) | a change to the excluded scripts or to `pyproject.toml` |
| Component index | run | `python3 scripts/components_index.py changed --base 1f403b07 --strict`, exit 0 | `dev/components/` and the changed modules | plan H28 | any module added, moved or retired |
| VG1-C8; VG1-D5 | run | the experiment below, `gnd verify` row, base and head | the witness oracle and `gnd verify` | plan D9 | a change to `synth/oracle/constructive.py` |
| Other consumers of the three walks (the checker families, the witness and replay routes) | cadence | the default lane at milestone close | `gnd.checker`, `gnd.synth` | T1 holds each walk equal to its frozen body over every loadable model, so a consumer sees the same answers; T10 holds the reports | a change to a walk's answer |

### Implementability findings `(d)`

Found while completing this spec, before any code.

- **T1's count.** 473 files under `src/gnd/examples/` and `tests/fixtures/`
  are named `*.orm.yaml`, `*.orm.yml` or `*.orm.json`; 407 load with
  `load_model` at `1f403b07`, holding 1,810 object types. "At least 200"
  holds.
- **T9's counter.** `universe.py` and other modules bind
  `_supertype_parents` by name at import (`universe.py:28-31`), so patching
  `gnd.model_queries._supertype_parents` would count nothing. T9 counts calls
  of that function's code object with `cProfile`, which sees every binding.
- **Where the absolute bounds are judged.** The experiment's machine is
  amended from "one laptop" to beast-3 (Apple M5 Pro, 18 cores), the
  repository's remote machine. The base sweep was started there before this
  amendment was written; only its first two rows (`values` at N = 0 and 250)
  had been read. T3–T8 are judged by running the VG1 lane on that machine at
  the head. They also run on the laptop. Prior wording of the limit, kept:
  "One laptop."
- **The fixture route.** `gnd check` on a copy of the interop fixture refuses
  with `include:unreadable` when the copy's path goes through a symlink
  (`/var` to `/private/var` on macOS). The helper resolves its directory
  first; pytest's `tmp_path` is already resolved.

Which test is which `(p1)`. T1, T2, T9, T10, T12 and T13 read no clock; T1,
T9 and T10 are the required regression gates of plan §4. T11 compares two
sizes on one machine. T3–T8 are absolute bounds: they depend on the machine,
are judged on the one that runs the sweep below, and stay in the default
lane as coarse guards, 7.7 times or more above the prototype's figures.

## 9. Out of scope for this phase

- A subtype chain hundreds of types deep (plan H4a, D12). After this phase
  it is still slow: the prototype measured 5.29 s at 400 deep and 39.09 s at
  800. The cost is `_resolve_reference`'s recursion, shared with the loader.
- `gnd judgments check` running the checker twice (plan D10).
- The fact-type walk inside `_instance_values_of`: object types times fact
  types. T7 bounds it at 1,000 by 1,000; a role index is not built here.
- `resolve_reference_value_type`'s other callers (VG1-D2).
- The witness oracle, unless VG1-D5's measurement brings it in.
- Any change to a report, a schema, a CLI flag or an exit code.
- VG2–VG5.

## 10. Size

Estimate at write time: about 100 source lines changed (`model_index.py`
+55, `universe.py` 40, `semantic_adapter.py` up to 3), about 330 test lines
in the new file, about 25 in `tests/test_ir1_judgments_includes.py`. The
record states the measured figures.

## 11. Approval instrument

This prose. The expected answers are exits, verdict equality, time bounds
and call counts stated in §8; there is no separate answer key.

## An experiment, recorded before it runs

**Scaling sweep.** Run once at the base commit and once at the phase head,
on the same machine, in process.

- **Measures.** Wall time of `gnd check` on the checking root for each shape
  of §8 at N = 0, 250, 500, 1,000 and 2,000, minimum of three; of
  `gnd judgments check` for `values`; of `gnd verify` for `values` at 1,000
  (VG1-D5); and of the deep chain at 200, 400 and 800. At the base commit,
  sizes whose single run exceeds 120 s are recorded as "over 120 s" and not
  repeated.
- **Cannot measure.** Another machine or a CI runner; a real vocabulary
  whose types are used by facts (the fixture's population is small and the
  extra types hold no facts); population size; memory.
- **Graded in** the phase record, as a table beside the bounds of §5.
- **Liveness.** At `values`, N = 250, the base run must cost at least 5
  times the head run. If it does not, the sweep is not measuring the walk
  this phase changes and its numbers are not reported as evidence.
- **Limits, stated first.** One machine, beast-3 `(d)` (prior: "One laptop"). The bounds of §5 were chosen from
  the prototype before this sweep and do not move after it; a bound that the
  head misses is a failed criterion, not a reason to raise the bound.

## Implementation findings, recorded as they were found `(d)`

2026-11-23, at `1519ecb8`.

1. **The descendant walk moved into `ModelIndex`.** With the walk in
   `universe._descendant_closure`, the guard
   `tests/test_rf6_query_policy.py::test_dynamic_candidate_inventory_is_complete_and_live`
   failed: `children.get(pending.pop(), ())` is a new dynamic lookup outside
   the model modules, and that guard keeps every such lookup in a counted
   inventory. Shared model queries belong on `ModelIndex` (`AGENTS.md`,
   "Model queries and family dispatch"), which the guard exempts, so the
   walk is `ModelIndex.descendants(identifier) -> set[str]` and
   `_descendant_closure` returns it. This adds one method to §6's surface;
   no inventory row was added.
2. **T9's negative control runs at 100 extra value types, not 300.** Under
   the profiler the base walk took 36 s at 300. At 100 it builds the
   supertype map 21,677 times, which is over the 1,000 the row asks for.
   Prior wording, kept: "the count at 300 is over 1,000".
3. **T9's figures.** One `gnd check` builds the supertype map 48 times at
   300 extra value types and 48 times at 600 (base: 184,876 at 300, plan
   H2).
4. **A test-authoring slip, not a spec finding.** T13 first expected
   `denoted_by({"left_id"}) == {"left"}`. A value type denotes itself, so
   the table answers `{"left_id", "left"}`, and `_denoting_types` removes
   the covered ids, as the base body does. The expectation was corrected.
5. **Review r1 (Codex), F1, reproduced and fixed at `7e235d4a`.** The
   content-keyed cache gives a code-built model with a str-enum `kind` and
   the plain loaded model one key, and the tables first read the rows of
   whichever model reached the cache first. After the enum model,
   `_kind_of` answered `K.VALUE` for the plain model, and the reviewer
   showed a range check reading `vacuous` for `fail`. The tables are now
   built from the canonical JSON form the key is a digest of. The collision
   itself predates VG1 and still reaches the index's other readers (record,
   open questions).
6. **Review r1, F2, reproduced and fixed at `7e235d4a`.** The table resolves
   every type, so a code-built `reference` that is a string raised where
   the base body skipped the covered type. Such a type now resolves to None.
7. **The canonical copy is parsed by the routed reader** (`5427e8fe`).
   `tests/test_rf7_structure.py` refuses `json.loads` outside
   `gnd.input_policy`. Past that reader's 10 MB and 64-level caps the
   tables read the cached rows, as before VG1: a residual the record names.
