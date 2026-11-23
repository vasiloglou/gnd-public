# Phase GO1 · one parse per model text in `gnd evolve` · spec r3

## 1. Status

**Draft r3, awaiting its gate.** r1 was written by `start-milestone` on
2026-11-23. r2 applied the GO1 findings of the plan's panel round 1 (the
reader key, the snapshot of T3, the timed test outside the focused lane),
tagged `(p1)`. r3 applies round 2's (the write check over the whole lane,
the `.json` parse counts, the consequence of a failed T8), tagged `(p2)`,
and derives from plan r4 (sha256 `b107bd36…7431`), approved in
`001-plan-gate.md`. Under the owner's `auto` delegation for this milestone the
gate is a delegated ruling, recorded in the phase record.

## 2. Provenance

- Derives from [plan r4](growth-round-outcomes-plan.md), Goal (GO1), §0
  (R0.2, R0.3, R0.5), §1 (H1–H9, H22–H24), §2 (GO1), §4 (GO1-C1 to GO1-C6),
  §9 (the GO1 lane) and §10 (D6, D9). The plan is approved by delegated
  ruling (auto=true) in `001-plan-gate.md`; D9 is ruled out of GO1.
- From [#228](https://github.com/vasiloglou/gnd-public/issues/228).
- r1 and r2 were offered to the plan's panel rounds as context; no review
  has read r3.
- Every code citation was read at `548b9a1d`. Measurements were run on that
  commit on 2026-11-23, in process, on one laptop under other load, once
  each.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan H1; #228 | a round costs time in proportion to the whole model; `apply` is two thirds of it | §6; T8; the experiment |
| plan H2, H4 | `apply` parses 22 times and `preview` 6, two distinct texts, at every size | §6; T1 |
| plan H3 | `_load_model_document` parses its bytes three times (`service.py:264`, `:277`, `:291`) | §6 (all three read the scope) |
| plan H5 | the parse depends on the bytes and on the reader the name selects | §6 (the key); T5 |
| plan H6 | the prototype's figures: 2 parses, identical output, `apply` 0.31 of its cost at 604 object types | GO1-D5; T8 |
| plan H7 | a copy per caller costs more than the parse | GO1-D2 |
| plan H8 | the YAML guard scans the same text 4 times in one `apply` | GO1-D3 |
| plan H9, D9 | `load_model` parses twice in every command | GO1-D4 |
| plan H22 | `index_scope()` is the existing pattern for a per-call cache | §6 |
| plan R0.2 | no validation, guard or digest comparison is removed | §6 ("What does not change"); T2, T4 |
| plan R0.3, GO1-C2 | every record keeps its bytes | T2 |
| plan R0.5, GO1-C4 | keyed by content, alive for one call | §6; T4, T7 |
| GO1-C1 | at most 3 parses in `apply`, 2 in `preview`, the same at two sizes; 22 and 6 with the scope off | T1 |
| GO1-C3; plan §2 GO1 (p2) | no remembered document differs at scope close, checked over the whole GO1 lane; loaded `Model`s hold nested references | §6 verify mode; T3 |
| plan Goal, GO1-C1 (p2) | once per text and reader; a `.json` workspace too | T1 |
| GO1-C5 | `apply` with the scope at most 0.6 of `apply` without, at 604 object types | T8 |
| GO1-C6 | the #228 table measured again at the head | the experiment |
| plan §9 | the GO1 lane, the guard block, `uv run ruff check src tests tools` | §8, closing paragraph |
| plan H23 | component index updated in the same commit | §6, reuse table; §8 |
| `AGENTS.md`, "Refactoring dependency homes" | new homes in `tools/gnd_layers.json`; allowance count stays zero | §6 (no new module; the import is downward) |
| `AGENTS.md`, "General solutions, not pattern-matched ones" | no new matcher over structured text | §4 |

## 4. The standing rules, bound to this phase

- **Totality (project rule 1).** The scope adds no consumer of untrusted
  bytes: `parse_model_document` stays the only reader, with its cap applied
  before the read is decoded (`_parsing.py:31-32`). The lookup hashes bytes
  the caller already holds. A refusal is never remembered, so the hostile
  cases of the loader keep their refusals; T5 holds three of them inside a
  scope.
- **A cap bounds the document, not the algorithm (rule 2).** This phase is
  that rule applied to `gnd evolve`: the work per command stays linear in the
  model but stops being 22 times it. T1 pins the count, which does not depend
  on the machine; T8 is the time-bound test over the layer changed.
- **Validation order (rule 3).** No refusal is added and none moves. The
  include guard, the loader, the document parse and the YAML guard run in
  the order of `service.py:262-297` as today; T2 compares the message and
  exit of each refusal with the scope on and off.
- **One walk for N kinds (rule 4).** One scope serves every caller of
  `parse_model_document`. There is no second cache for the include guard,
  the loader or `_parse_model_text`.
- **One home for normative prose (rule 5).** No normative page changes. The
  scope's docstring is the one statement of what is remembered and for how
  long.
- **Measurement, not argument (rule 6).** Whether sharing one document is
  safe is settled by T3 over every case of T2, not argued. Whether to copy
  was settled by the prototype (plan H7).
- **General solutions (`AGENTS.md`).** The phase adds no regular expression,
  split or special-case branch. The reader selection in the key is the
  parser's own test, called and not restated (§6).
- **Plan R0.2, R0.3, R0.5:** T2, T4, T7. **R0.1, R0.4, R0.6** concern
  `apply`'s wholeness, preview values and pages; this phase changes none.

## 5. Goal

One `gnd evolve apply` calls the model parser at most 3 times and one
`gnd evolve preview` at most 2, at any model size; every preview, pending
state, record, published model, message and exit is byte-identical to what
the same command gives with the scope switched off. The focused lane, the
guard block and `uv run ruff check src tests tools` exit 0.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| parse one model text | `components_index.py search "parse model document yaml"`; `git grep -n "parse_model_document(" src/gnd` | `model.loading`; `model/_parsing.py:25` and its callers in `model/__init__.py`, `model/_includes.py`, `evolve/service.py`, `evolve/models.py:1109` | reuse the parser unchanged; add the scope beside it |
| a cache that lives for one public call | `components_index.py search "model index snapshot scope"`; `git grep -n "index_scope" src/gnd` | `model.query_index`: `index_scope`, `scoped` (`model_index.py:52-71`) | adapt the pattern; it caches by model object, this one by content |
| a content digest of bytes | `git grep -n "sha256_hex" src/gnd/model src/gnd/evolve` | `sha256_hex`, which `evolve/service.py` uses (`:238`) | reuse it if the model layer may import its home; otherwise `hashlib.sha256` directly. The spec's process-phase run names which |

Nothing existing remembers a parsed document. The `dev/components/` entry
for `model.loading` changes in the same commit.

### `src/gnd/model/_parsing.py` (about +35 lines)

```python
@contextmanager
def parse_scope() -> Iterator[None]:
    """Remember each document parse_model_document builds, for one public call.

    Keyed by the sha256 of the bytes and by the reader the source name selects.
    Re-entrant: an inner scope shares the outer one. Dropped when the outermost
    scope exits. A parse that raises is not remembered. The remembered document
    is shared by reference and must not be written to."""
```

- `parse_model_document(data, *, source)` keeps its signature. Inside a
  scope it returns the remembered document for `(sha256(data), reader)`;
  otherwise it parses and, on success, remembers.
- `reader` is whether the source name selects the strict JSON reader, the
  `.json` suffix (`_parsing.py:37`), moved into one private function that
  both the parser and the key call. It is the only way the name changes a
  successful parse: text starting with `{` under another name tries JSON and
  falls back to YAML, and under a `.json` name the same text is refused, so
  a key that also read "starts with `{`" would hand a YAML-built document to
  a `.json` caller (p1). The key never restates the test.
- Outside a scope nothing is remembered and two calls return two documents,
  as today.
- The scope is a `ContextVar`, as `index_scope` is, so it does not cross
  threads or leak into a later call.
- **Verify mode (p2).** A module-level switch, off by default, makes every
  scope keep a type-preserving copy of each document it remembers
  (`copy.deepcopy`, which keeps `CommentedMap`, dates and tags) and, when the
  outermost scope exits, compare each remembered document with its copy by a
  walk that compares type and value at every node. A difference raises an
  `AssertionError` naming the source. The switch is set by an autouse fixture
  in `tests/conftest.py`, so the check runs in every test that opens a scope,
  the whole GO1 lane included, and not only in GO1's own cases. Shared
  documents need the check because a loaded `Model` keeps the document's
  nested lists and mappings: `_finish_model` copies only the top level
  (`model/__init__.py:315`) and a frozen `Model` leaves nested content
  mutable (`documents.py:40-41`). T8 turns the switch off.

### `src/gnd/evolve/cli_service.py` and `service.py` (about 10 lines)

- `_cmd_evolve_preview` (`cli_service.py:592`) and `_cmd_evolve_apply`
  (`:684`) run inside `parse_scope()`. `apply` at the command line runs
  `preview`, `apply` and `finalize` in one scope, which is what takes 22
  parses to 2.
- `EvolutionService.preview`, `apply` and `finalize` (`service.py:1520`,
  `:2110`, `:2377`) open the scope too, for a library caller. It is
  re-entrant, so the command-line path opens it once.

### A home outside the plan's list

`tests/conftest.py` gains the autouse fixture that switches verify mode on
(p2). The plan's §3 GO1 row does not name it; the pull request says so.

### What does not change

`_load_model_document` keeps its three calls and their order; each is now a
lookup after the first. Semantic validation, reference binding, the YAML
guard, every digest comparison and the model CAS run as often as today.
`gnd.evolve` is above `gnd.model` in `tools/gnd_layers.json`, so the import
is downward and the map gains no row.

## 7. Decisions

Every row is open.

| ID | Question | Readings and their cost | Proposed |
|---|---|---|---|
| GO1-D1 | Where the scope opens | (a) the two command handlers and the three service methods, re-entrant: 2 parses per command, and a library caller of one method gets its own share. (b) the service methods only: `apply` at the command line still parses in three separate scopes, about 6 times | (a) |
| GO1-D2 | What a second caller receives | (a) the same document object: fastest, and a caller that wrote into it would corrupt the next; T3 is the control. (b) a deep copy: measured slower than parsing at size (plan H7: `apply` 41.3 s against 28.43 s unchanged at 2,404 object types). (c) restructure `_load_model_document` to parse once and pass the document down, with no scope: 22 parses become 8, no shared state between loads, and three loader signatures change | (a). No exit code differs between them |
| GO1-D3 | Does the scope also remember the YAML guard's verdict (plan H8) | (a) yes, by the same key: 4 scans become 1 in `apply`; the one measurement suggests 9.95 s → 8.04 s at 2,404 object types, across two series whose unchanged runs differed by 12 %. A remembered verdict of a safety guard is one more thing to get wrong. (b) no: the guard scans as often as today | (b). The request is the parses; the gain is inside the noise measured |
| GO1-D4 | The loader's own double parse (plan H9, D9) | (a) in this phase: `_load_model_at` passes its parsed document to the loader in place of the bytes, about 2 lines in `model/__init__.py`; `gnd validate` on 2,404 object types 4.30 s → 2.34 s with one parse; it touches every command that loads a model, so the report-golden lanes join the gate. (b) a maintenance pass of its own, after this phase. (c) leave it | (b). GO1 stays inside `gnd evolve`; the owner may rule (a) |
| GO1-D5 | The ratio bound of T8 | 0.6 at 604 object types. The prototype measured 0.31 there and 0.35 at 2,404. A tighter bound fails on a loaded machine; a looser one admits a return to about 10 parses | 0.6 |

## 8. Tests

New file `tests/test_go1_evolve_parse_once.py`, default lane. A helper
builds the unattended fixture plus N groups (one entity type, its reference
value type, one more value type and one binary fact type, each citing a span
of one declared document) and a one-round proposal, with the helpers of
`tests/test_unattended_model_growth_acceptance.py` and
`tests/test_unattended_growth_guidance.py`. A second helper runs a command
with the scope switched off, by replacing `parse_scope` with a context
manager that remembers nothing.

| # | Case | Expected |
|---|---|---|
| T1 | count calls that reach the real parser during one `preview` and one `apply`, at N = 10 and N = 40, for a `model.orm.yaml` workspace and for a `model.orm.json` workspace (p2) | `preview` at most 2 and `apply` at most 3, equal at both sizes. For the `.json` workspace `apply` parses the current text under two readers, which is within the bound (p2). Negative control: scope off, 6 and 22 |
| T2 | scope on against scope off, for: the one-round proposal; a proposal the additive policy refuses; a D-12 refusal; an include root (the case of `tests/test_mc3_evolution.py`); a model named `model.orm.json`; a YAML model holding an unquoted date; a candidate that is not valid YAML | preview bytes, pending state, record, published model, stdout, stderr and exit equal in each pair |
| T3 | verify mode on (the autouse fixture) for every case of T2, a type-preserving snapshot of each remembered document when the scope closes against the same snapshot taken when the parser returned it: the round-trip YAML dump for a YAML document, which keeps dates and tags canonical JSON cannot spell, and canonical JSON for a JSON document (p1) | equal, including on the YAML-date case. Liveness: a write into a nested list of a `Model` loaded in the scope, and a change of `1` to `True`, each make the scope close raise (p2) |
| T4 | preview, then the model file is rewritten, then `apply` | the refusal `apply` gives today for a model changed since its preview, same message and exit as with the scope off (the neighbouring stale case is `test_t3_populated_set_change_before_apply_is_stale`, `tests/test_evolve_additive_policy.py:788`) |
| T5 | inside one scope: the same bytes under `model.orm.json` and under `model.orm.yaml`; YAML-flow bytes that start with `{` and are not JSON, first under `model.orm.yaml` and then under `model.orm.json` (p1); a text over the 10 MiB cap twice; malformed YAML twice | two parses for the two names; the `.yaml` parse succeeds and the `.json` request is still refused as strict JSON; the cap refusal and the YAML refusal raised both times with the caller's label |
| T6 | `parse_model_document` twice outside any scope; twice inside nested scopes | two distinct objects; one object, and none remembered after the outer scope exits |
| T7 | two `preview` commands in one process on two workspaces with equal model bytes | each parses its texts; the second reads nothing from the first |
| T8 | N = 200 (604 object types): the minimum of two `apply` runs with the scope over the minimum of two with it off. The test is marked `slow`, which the default `addopts` excludes; it is run once with `-m slow` for the record (p1) | at most 0.6, recorded |
| T9 | the existing lane, unmodified: `tests/test_evolve_additive_policy.py`, `tests/test_evolve_source_document.py`, `tests/test_evolve_loading.py`, `tests/test_mc3_evolution.py`, `tests/test_unattended_model_growth_acceptance.py` | exit 0, no golden changed |

Branch table. The lookup has four branches: no scope; a scope and a first
sight of the key; a scope and a remembered key; a parse that raises. T6
reaches the first three, T5 the fourth and the two-reader case. Every branch
has a case that fails if the branch returns the wrong object.

Gate: the plan §9 GO1 lane with this file, the guard block of `project.md`,
`uv run ruff check src tests tools`, and
`python3 scripts/components_index.py changed --base origin/main --strict`.

Which test is which. T1 to T7 and T9 read no clock and are the required
regression gates. T8 compares two runs on one machine, is excluded from the
focused lane and is recorded; a ratio over 0.6 is a failed criterion stated
in the record (p1) and stops GO1 for a ruling before its pull request (p2).
The rest of the lane runs with verify mode on, so every existing evolve test
is also a write check (p2).

## 9. Out of scope for this phase

- Remembering a loaded `Model`, a validation result or a reference binding.
  They read files beside the model, so remembering them would skip a read;
  this phase remembers a pure function of bytes only.
- The YAML guard's repeated scan (GO1-D3) and the loader's double parse
  (GO1-D4), unless the owner rules them in.
- `gnd validate` and every command other than `gnd evolve`.
- A round that validates only what changed (plan §7). After this phase
  `apply` still costs about 10 s at 2,404 object types on the prototype.
- Any change to a record, a schema, a flag, a message or an exit code.
- GO2–GO5.

## 10. Size

Estimate at write time: about 70 source lines (`_parsing.py` +60 with verify mode, `tests/conftest.py` +8,
`cli_service.py` and `service.py` about 10) and about 280 test lines in the
new file. The record states the measured figures.

## 11. Approval instrument

This prose. The expected answers are parse counts, byte equality, refusal
text and one ratio, stated in §8; there is no separate answer key.

## An experiment, recorded before it runs

**Round sweep.** Run once at the base commit and once at the phase head, on
the same machine.

- **Measures.** CLI wall time of `gnd validate --document … --require-documents`,
  `gnd evolve preview --policy additive --shape-report` and
  `gnd evolve apply --policy additive` for the round of §8 at 34, 304, 604,
  1,204 and 2,404 object types, the sizes of #228, and the parse count of
  each command.
- **Cannot measure.** Another machine or a CI runner; a real vocabulary; a
  model with includes or reference populations; a round that adds more than
  one fact type; memory.
- **Graded in** the phase record, as the #228 table with a head column.
- **Liveness.** At 604 object types the base `apply` must cost at least 1.5
  times the head `apply`. If it does not, the sweep is not measuring the
  parses this phase removes and its numbers are not reported as evidence.
- **Limits, stated first.** One laptop, one run per cell. The bound of T8
  was chosen from the prototype before this sweep and does not move after
  it; a bound the head misses is a failed criterion, not a reason to raise
  the bound.

## 12. Gate — delegated approval (auto=true)

**Delegated approval (auto=true), 2026-11-23**, of this spec r3, sha256
`601e8f46f18d333d5de63b51637e59038a892c6709b9b78573b12a016b4ddcb0` (the bytes
above this section). Authorization: the owner's delegation of `auto` for
growth-round-outcomes ("they should both start with /process-milestone
auto"), recorded in `001-plan-gate.md`. This is an agent ruling under that
delegation, not the owner's reading of the spec.

- **Approval instrument:** this prose. GO1 is not one of the three shapes
  for which corpus-first is the default (it adds no serialized format, exit
  code or validation predicate); its expected answers are counts, byte
  equality and refusal text, stated in §8.
- **Spec review:** none. The plan's two full-panel rounds read r1 and r2 as
  context; no reviewer has read r3. The diff review (D8, one reviewer in a
  different tool) is the phase's review.
- **Rulings:** GO1-D1 (a) [delegated]; GO1-D2 (a) [delegated]; GO1-D3 (b)
  [delegated]; GO1-D4 (b) [delegated, as plan D9]; GO1-D5 0.6 [delegated].
- **Compatibility:** no record, schema, flag, message or exit code changes
  (R0.3); `tests/conftest.py` is a home outside the plan's list (§6).
- **Budget:** one diff review round, a second only if the first blocks.
- **Ordering, stated:** the ruling was taken at the coordinating session's
  "GO GO1", before any GO1 code was written; this section was written after
  the code was drafted. The approved bytes are the sha256 above, which the
  code did not change.

## 13. Implementation findings

Recorded as found.

1. The write check's first run over the existing lane reported a write on
   `test_e2_each_value_outside_json_is_named[x: .nan-non-finite float]`. Not a
   write: `NaN != NaN`. `_same` now treats two NaNs as the same value; T3's
   second case parses `.nan` inside a checked scope.
2. The size cap is checked before the key is hashed, so an oversized buffer is
   refused without being hashed (standing rule 1, cap on the read).
3. **Deviation from §6, stated.** §6 opens the scope on the three
   `_cmd_evolve_*` handlers. Their bodies are pinned by the RF5 relocation
   guard (`tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged`),
   which went red on the decorators. The scope now opens one level up, on
   `gnd.commands.evolve.handle`, the one dispatcher of `preview`, `apply` and
   `finalize`, through the decorator `parse_scoped`; the command module
   reaches it through its own domain service (`gnd.evolve.cli_service`
   re-exports it), because the entry-point rule lets a command module import
   only that service (`tests/test_rf5_review_regressions.py`). The three
   service methods carry the decorator too, for library callers. Same
   reading (a) of GO1-D1, same counts; `src/gnd/commands/evolve.py` is a
   home outside the plan's list.
4. Measured parse counts (T1): with the scope, `preview` 2 and `apply` 2 for
   a YAML workspace at N = 10 and N = 40; without it, 6 and 22, as #228
   measured. The bound of 3 holds with one to spare.
5. With the write check on, the existing evolve lane (418 tests, seven
   files) passed unchanged: no evolve path writes into a parsed document.
