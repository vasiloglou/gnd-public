# Follow-up spec — evolve loading (IK4-Q3, IK4-Q2-Q1, IK4-Q2-R1, R4, tags)

**Status:** owner-decided (2026-10-27): D1..D5 approved as proposed (§12).

## 1. Provenance

- **Carried by:** the induced-knowledge close,
  [012-milestone-close.md](../012-milestone-close.md) "Open questions carried
  forward", first row: "one evolve-loading follow-up PR (C-D2, CD3, CD5)".
  Owner decisions CD3 and CD5 in
  [011-owner-decisions-close.md](../011-owner-decisions-close.md); acceptance in
  [013-owner-acceptance.md](../013-owner-acceptance.md).
- **Source records:** IK4-Q3 in [005-phase-IK4.md](../005-phase-IK4.md); IK4-Q2-Q1,
  IK4-Q2-R1 and review R4 in [009-phase-IK4-Q2.md](../009-phase-IK4-Q2.md) and
  [phase-IK4-Q2-agent-review.md](phase-IK4-Q2-agent-review.md) item 4; the
  date reproduction in [close-reading-one.md](close-reading-one.md) finding 2;
  the tag case in the close row itself.
- **Base:** main at `63f7f1f`.
- **Protocol:** process-phase, `auto=false`. No panel has read these bytes.

## 2. Reproduction on the base (author's runs, 2026-10-27)

All runs use `tests/fixtures/induced_knowledge/ik4-corpus/staff.orm.yaml` with
one line added, then `gnd discover … --families uniqueness` and
`gnd evolve preview` on the emitted proposal.

| Added line | `gnd validate` | `gnd discover` | `gnd evolve preview` |
|---|---|---|---|
| `source.created: 2024-01-01` | 0 | 0 | **70** "Object of type date is not JSON serializable" |
| `source.x: 2024-01-01T10:00:00Z` | 0 | 0 | **70** "… TimeStamp …" |
| `source.x: !!binary aGVsbG8=` | 0 | 0 | **70** "… bytes …" |
| `source.x: !!set {a, b}` | 0 | 0 | **70** "… CommentedSet …" |
| `source.x: .inf` | 0 | **1** (traceback in discover's output) | — |
| `source.x: !foo 3` | 0 | **1** (traceback: uncaught EvolutionError) | — |
| `description: {summary: s, extra: !foo {a: 1}}` on `person` | 0 | **1** (same traceback) | 3 "current model is not valid YAML" with a hand-built proposal |

Where the base fails:
- **The 70s** are two crash sites, not one. `render_model_verbalization`'s
  `_canonical` (`src/gnd/model_verbalization.py:34`) runs `json.dumps` over the
  loaded model's `source`. With that bypassed, `_surface_index`
  (`src/gnd/evolve/service.py:387`) hits `canonical_sha256` over the parsed
  document. Every evolve evidence digest is canonical JSON.
- **The tag case** comes from two parsers. `gnd validate` parses with ruamel
  round-trip (`gnd.model.load_model_bytes`), which keeps an unknown tag.
  Evolve's `_parse_model_text` re-parses the same text with ruamel `safe`,
  which refuses it. Discover imports that same `_parse_model_text` and does not
  catch its error.
- **`.json` names** (IK4-Q2-Q1): `_load_model_bytes` renames a `.json` source
  to `.yaml` before loading. So evolve accepts a `.json` model holding YAML
  text, which `gnd validate` refuses (exit 3; reproduced with a copy of the IK5
  corpus model, "model JSON input refused"). `test_r1_…` pins that acceptance.
- **R4:** a binder `ReferenceInputError` is wrapped in a second
  `ReferenceInputError` with the same message, then in `EvolutionError`.

## 3. Obligations (step 0 harvest)

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | IK4-Q3; close-reading-one F2 | a discover proposal on a valid model with a YAML-only value previews, or is refused by name at 3; never 70 | D1, §6.2, E1–E3 |
| O2 | IK4-Q2-Q1 (record 009) | owner ruling: strict JSON for `.json`-named models | D2, §6.1, J1–J3 |
| O3 | IK4-Q2-R1 | one load-then-bind helper | D3, §6.1, H1 |
| O4 | IK4-Q2 review R4 (cosmetic) | no double `ReferenceInputError` wrap | §6.1, W1 |
| O5 | close row, tags | a valid model with a tag in a description extra loads in validate but evolve says "not valid YAML" | D1, §6.1, E3 |
| O6 | record 009 boundary | binder defect stays 3 (R4 parity); reference exits 66/74/3 unchanged | §6.1; existing T3, T4, R2, R3 |
| O7 | IK-R3 additive compatibility | reference-free YAML previews byte-identical | existing T6 golden |
| O8 | IK-R7 / AGENTS.md RF rules | layer map, allowance count zero, RF5/RF6 successors registered for any pinned body that changes | §6.4, gate |
| O9 | IK-R4 / standing rule 5 | the evolve loading rule has one normative home | §6.3 |
| O10 | close CD5 | carried rows are disposed of, none closed silently | §9, record |

## 4. Standing rules, bound here

1. **Totality belongs to the function.** The new loader returns a model and a
   document or raises `EvolutionError`; no `TypeError`/`ValueError` from a
   value escapes to the CLI's 70. The value walk (§6.2) is total over the
   parsed tree.
2. **Caps bound the document.** Unchanged: the 10 MiB model cap and the event
   and alias guards run before any walk. The walk is linear in the parsed tree
   and needs no new ceiling.
3. **Validation order, per boundary.** Read bytes → validate (`load_model_bytes`)
   → bind references → parse document → value-domain walk. The value walk runs
   after validation so `gnd validate`'s verdict comes first: an invalid model
   still reports its validation error.
4. **One walk for N kinds.** One walk refuses every value kind outside the JSON
   data model; no per-kind check at each crash site.
5. **One home.** `evolution-contract.md` §3 (the binding paragraph) gains the
   loading rule; docs cite it.
6. **Measurement over argument.** The table in §2 is the measurement.

## 5. Goal

`gnd evolve preview`, `apply` and `finalize` load every model through one
helper that parses as `gnd validate` parses. A model or candidate that holds a
value outside the JSON data model exits 3 naming the value's path and kind
(D1-A), never 70. Under D2-A a `.json`-named model is parsed as strict JSON,
and YAML text there exits 3. Reference-free YAML previews stay byte-identical
(T6). Reference exits stay 66/74/3.

## 6. Design

### 6.1 One loader (`src/gnd/evolve/service.py`, ~60 changed lines)

```python
def _load_model_document(
    data: bytes, *, label: str, model_path: Path, declared_references: Any = None
) -> tuple[Model, dict[str, Any]]:
```

- Replaces `_load_model_bytes`. Every model load in evolve calls it: preview
  current and candidate; apply current, candidate and staged; finalize staged
  before and candidate. The paired `_parse_model_text(text)` that follows each
  load today is removed; the document comes from the helper.
- `source=model_path`, the real name (D2-A). The `.json` → `.yaml` rename goes.
- The document is parsed by the model loader's own parser (§6.4), then
  converted to plain Python (`dict`, `list`, `str`, `int`, `float`, `bool`,
  `None`) by the value walk (§6.2).
- Binding: a `ReferenceInputError` from `bind_references` is re-raised as it
  is. Anything else is wrapped once as `ReferenceInputError` (R4 parity: a
  binder defect stays 3). Then `EvolutionError(f"{label} validation failed:
  {error}")`, as today.
- `_parse_model_text(text, label)` stays for its other callers (the apply
  replay of preview text, discover, tests). It parses with the same parser and
  converts with the same walk, but **keeps** YAML-only values rather than
  refusing them, so discover's date support (it writes block YAML, exit 0) is
  unchanged.

### 6.2 The value-domain walk (D1-A)

Accepted: mappings with `str` keys, sequences, `str`, `int`, finite `float`,
`bool`, `None`, and nodes whose explicit tag is a core JSON-schema tag
(`!!str`, `!!int`, `!!float`, `!!bool`, `!!null`, `!!map`, `!!seq`).

Refused, at the first one in document order:

| Kind named in the message | Example |
|---|---|
| `date` | `2024-01-01` |
| `timestamp` | `2024-01-01T10:00:00Z` |
| `binary` | `!!binary aGVsbG8=` |
| `set` | `!!set {a, b}` |
| `non-finite float` | `.inf`, `.nan` |
| `tag <tag>` | `!foo {a: 1}`, `!foo 3`, `!!omap`, `!!pairs` |
| `non-string key` | `{1: a}` (validate refuses most; the walk is total anyway) |

Message: `"{label} validation failed: {path} holds a {kind}, which evolve's JSON
evidence cannot represent; quote it or remove it"`. `path` is dotted with
indices, e.g. `source.created`, `object_types[0].description.extra`. It reuses
the CLI's existing `validation failed` marker, so it exits 3 with no new
marker.

### 6.3 Contract prose (`evolution-contract.md` §3, ~4 lines)

After the binding paragraph: evolve parses each model as `gnd validate` does,
including strict JSON for a `.json` name (D2-A). A model or candidate holding a
value JSON cannot represent (a date, timestamp, binary, set, non-finite float,
non-core tag or non-string key) exits `3`, naming its path.

### 6.4 The shared parser (`src/gnd/model/__init__.py`, ~25 moved lines)

`parse_model_document(data: bytes, *, source: str | Path) -> Any` is extracted
verbatim from `load_model_bytes` lines 284–308: the cap, the strict-JSON
branch, and the alias/event guard then round-trip load. `load_model_bytes`
calls it. Behavior-preserving; the existing loader tests pin it. It is
registered in `tools/gnd_layers.json` if the map lists functions (measured at
execution). Any RF5/RF6 pinned body whose digest changes gets a successor row
with a reason, as `evidence/close/update_source_successors.py` and
`build_dynamic_successor.py` did. Counts are measured, not predicted.

## 7. Decisions (open)

| # | Question | Readings and their cost |
|---|---|---|
| **D1** (IK4-Q3, tags) | YAML-only values in an evolved model | **A (proposed): refuse by name at 3** (§6.2). Cost: such a model cannot be evolved until the author quotes the value; `gnd validate` still accepts it. No evidence grammar change; the tag case changes from a misnamed 3 to a named 3. **B: preview them.** Needs a canonical JSON spelling for each kind in every evolve digest and in `render_model_verbalization`, which `gnd recovery verify` shares. A quoted `"2024-01-01"` and a date then hash alike in blast-radius surfaces. Tags have no spelling; they would be dropped silently from discover candidates, or still refused. Exit: 0 instead of 3, plus new normative encoding prose. |
| **D2** (IK4-Q2-Q1) | Strict JSON for `.json`-named models | **A (proposed, as record 009 proposed): yes.** Refuses what main accepts: a `.json` model holding YAML text (`gnd validate` already refuses it, 3) and a YAML-text candidate for a JSON model, both now 3 instead of 0. GND's own producers (discover, `import ilp-rules`) write JSON text candidates, except discover's block-YAML fallback for YAML-only values, which D1-A refuses anyway. **The approved test `test_r1_a_json_named_reference_free_model_previews_as_at_b` inverts:** its successor J1 asserts 3 and J2 adds a genuine JSON model that previews 0. **B: keep main's YAML parse.** R1 stays; the record 009 boundary ("evolve can publish YAML text into a `.json` model, which `gnd validate` then refuses") stays. |
| **D3** (IK4-Q2-R1) | Scope of the helper | **A (proposed): evolve only,** with the parser shared from `gnd.model` (§6.1, §6.4). The record 009 cross-module helper (`api.py` judgments, `export/lean_io.py`, `export/pyrel_rules.py`, discover's `_bind_references`) is re-carried to the refactoring milestone that owns RF5: each has its own root option and wrap rule, none is broken, and converting them changes exits that need their own tests. **B: the five-home `gnd.model.load_model_bytes_bound` now.** About three more consumers and their exit tests in this PR. |
| **D4** | Discover's side effect | **A (proposed): in scope.** Sharing the parser fixes discover's traceback (exit 1) on a tagged model; it then exits 0 and its proposal is refused at preview by D1-A. Test D5 pins it. Discover's separate `.inf` traceback (in its output writer, not the parser) is **not** fixed and is carried. **B: keep discover on the safe parser;** it keeps the traceback. |
| **D5** | Record home | **A (proposed):** this spec plus record `014-followup-evolve-loading.md` and `evidence/evolve-loading/` under the induced-knowledge milestone, since the row lives in its close. **B:** a new milestone directory. |

## 8. Tests (all in `tests/test_evolve_loading.py` unless named)

Committed red first, then turned green. Expected exits are for the fix under
the proposed rulings.

| ID | Case | Base | Expected |
|---|---|---|---|
| E1 | discover proposal on staff + `source.created: 2024-01-01` → preview | 70 | 3; message names `source.created` and `date`; no preview file |
| E2 | the same, parametrized over timestamp, binary, set, `.inf`, `!foo 3` in the current model, with a hand-built one-op proposal | 70 / 3 misnamed | 3, kind named |
| E3 | the close row's exact model (`description: {summary: s, extra: !foo {a: 1}}`): `gnd validate` | 0 | 0 (premise pin) |
| E3b | same model → preview | 3 "not valid YAML" | 3 naming `object_types[0].description.extra` and `tag !foo` |
| E4 | candidate alone holds a date | 3 (replay mismatch) | 3 naming the candidate and `date`, before the replay |
| J1 | `.json` model holding YAML text (R1's model) → preview | 0 | 3 "model JSON input refused"; replaces R1 (D2) |
| J2 | `.json` model holding JSON text, JSON candidate → preview, apply | 0, 0 | 0, 0; published bytes equal the candidate |
| J3 | `.json` JSON model, YAML-text candidate → preview | 0 | 3 |
| W1 | binder raises `ReferenceInputError` (monkeypatched) → the `EvolutionError`'s cause is that same object | fails | passes; exit 3 |
| H1 | every model load in preview, apply and finalize goes through `_load_model_document`; none re-parses with the safe loader (call counts, as R3 does) | fails | passes |
| D5 | `gnd discover` on the E3 model | 1 | 0; its proposal previews 3 (E3b's message) |
| P1 | `parse_model_document` returns what `load_model_bytes` validated (JSON, YAML, flow-mapping YAML, a capped input) | n/a | passes on the base's loader behaviour |

**Branch walk.** Each kind in §6.2's table has a case (E1, E2, E3b; non-string
key is unit-tested on the walk, since validate refuses it first). Current vs
candidate: E1–E3b and E4. `.json` YAML model, JSON model, YAML candidate:
J1–J3. Binder re-raise vs wrap: W1 and the existing R4-parity behaviour via T3.
Every load site: H1. The value walk at apply and finalize cannot be reached
with a refused value through a successful preview; H1's call counts are its
case.

**Verification selection** (reduced v6.3):
- direct: `tests/test_evolve_loading.py`, `tests/test_evolve_references.py`;
- impact closure: `tests/test_*evolve*.py`, `tests/test_discover.py`,
  `tests/test_ik_close.py`, `tests/test_ilp_bridge.py`, `tests/test_model_v2.py`,
  every `tests/test_*.py` naming `load_model_bytes` (measured at execution),
  `tests/test_rf*.py`, `tests/test_gnd_arch.py`, `tests/test_packaged_skills.py`,
  `tests/test_public_binding_prose.py`, `tests/test_public_built_inventory.py`,
  `tests/test_public_distribution_runtime.py` (the contract changes);
- `ruff check` on the touched files;
- the full suite stays slow cadence (explicit owner selection or CI).

## 9. Out of scope

- The cross-module five-home helper (unless D3-B).
- Discover's `.inf` traceback in its output writer; `gnd recovery verify` over
  a date-bearing model, which shares `render_model_verbalization` (not
  reproduced). Both are carried as rows in the record.
- Evolve keeping comments or tags when it rewrites a model; preview evidence
  format; any exit renumbering. Invalid-YAML candidates (IK4-Q2-Q2) were
  already fixed at the close.

## 10. Size

Estimate: src ~90 lines changed (evolve ~60, model ~25 moved, contract ~4);
tests ~220 lines.

## 11. Approval instrument

This prose. The phase is an exit-code contract, where the review-convergence
reference defaults to a corpus, but the branch set is closed and small: each
branch is a row in §6.2 or §8 with its expected exit. No spec panel is
proposed.

## 12. Owner rulings

2026-10-27, relayed verbatim by the session that started this one, after it
recommended approving all five as proposed: "ok go on then with the recs". (o)
Confirmed by the owner directly in this session, the same day: "Approve D1 to
D5 as proposed." (o)

| # | Ruling |
|---|---|
| D1 | **A** -- values outside the JSON data model are refused by name at 3 (o) |
| D2 | **A** -- strict JSON for `.json`-named models; R1 inverts to J1 (o) |
| D3 | **A** -- evolve-only loader sharing `gnd.model.parse_model_document`; the cross-module helper is re-carried (o) |
| D4 | **A** -- discover's tag traceback is fixed here; its `.inf` traceback is carried (o) |
| D5 | **A** -- record 014 and `evidence/evolve-loading/` under induced-knowledge (o) |

The spec bytes approved are r1 at `acf3484`. No panel ran.

## 13. Implementation findings, recorded as found

- **F1 (refutes §2's last table row and §8 E2/E3b's base column).** A tagged
  *current* model exits **70** on the base, not 3: the CLI's malformed markers
  include "candidate model is not" but not "current model is not". The red run
  shows it (`evidence/evolve-loading/tests-red.txt`). The fix's exit, 3, is
  unchanged.
- **F2.** ruamel's safe and round-trip readers give `!!pairs` as a list of
  tuples, so the walk names the first entry: `source.x[0] holds a tag !!pairs`.
  E2's case says so.
- **F3.** E2 builds its candidate from the untouched model, so on the base most
  kinds refuse at the replay ("declared operations do not equal", 3). They are
  red by message, not exit.
- **F4.** Apply now loads the current and candidate models before the declared
  operations replay, so their documents come from the loads (H1). A preview
  that would fail both a load and the replay now reports the load. Both exit 3.
  Apply's operations gate still parses the preview text before any load, as
  before.
- **F5.** Three approved predecessor tests changed with the rulings:
  `test_r1_…` (removed; J1 is its successor, D2-A); `test_ik4_q2_q2_…` in
  `test_ik_close.py` (its tagged text now parses, so invalid YAML carries the
  label case; D3-A/D4-A); `test_the_current_model_is_validated_…` in
  `test_model_v2.py` (the source scan follows the one loader; its order
  assertion holds).
- **F6.** RF controls: `gnd.model.load_model_bytes`'s body digest changed (RF6b
  successor, chained from the frozen RF7 row) and the RF6 dynamic-candidate
  census gained five annotation rows and lost one (chained delta after the
  close's). Scripts: `evidence/evolve-loading/update_definition_successor.py`
  and `build_dynamic_successor.py`.
- **F7 (review).** One reviewer found two blocking regressions (a zoned
  timestamp crashed discover; the YAML guard made valid JSON exit 70) and
  hardening gaps; all fixed with red-first regressions RV1..RV4
  ([agent review](followup-evolve-loading-agent-review.md)). This adds one CLI
  malformed marker ("is not valid YAML") and its RF5 successor.
- **F8 (verification selection).** §8's `tests/test_*evolve*.py` glob missed
  the evolution suites (`tests/test_*evolution*.py`), which the reviewer ran.
  The final gate adds them.
- **F9.** `_parse_model_text` now runs the YAML depth guard after the reader
  builds the document, not before. The reader's own event and alias guards
  still run first, as in `gnd validate`; a JSON document is not re-read as
  YAML (RV2).
