# Phase IR3 spec · `gnd export pyrel` on an include root

## 1. Status

**Delegated approval (auto=true), 2026-11-21**, over this spec r1 and the
corpus `tests/test_ir3_pyrel_includes.py` (sha256 `a314ae291cc9a3d419ce8075a147130f200cefb88a917b5c843e0455c35d465e`), the goldens in
`tests/fixtures/ir3/` and the rewritten pins in `tests/test_mc1_guards.py`
and `tests/test_mc1_review_regressions.py`. Authorization: the owner's
`/process-milestone include-root-routes auto` in this session, within plan
r4 (`001-plan-gate.md`); IR2's record is `003-phase-IR2.md`. Instrument: the
corpus. Budget: one Codex review round. This is the driving agent's ruling,
not the owner's reading. Prior status, kept: "Draft r1, 2026-11-21, awaiting
its delegated spec gate (`auto=true`). Not implementable until that gate is
recorded here and IR2's record exists."

## 2. Provenance

- Plan: `notes/include-root-routes-plan.md` r4, approved in
  `001-plan-gate.md` (§1 H4, H7, H8, H9; §2 IR3; §4 IR3-C1 to IR3-C7; §6;
  §10 D3, D5). No review opinion covers these bytes.
- Code read at `68e426ca` on 2026-11-21; `src/gnd/export/` is unchanged
  since `260c4337`. `origin/main` was still `260c4337` when this spec was
  written: pyrel-rules-coverage RP2 has not merged, which fixes IR3-C3's
  expected outcome below (plan IR3-C3 `(p1)`).
- Measured 2026-11-21 (scratch): the flat model of
  `tests/test_mc1_model_includes.py:write_case`'s root exports with exit 0
  in the default mode and under `--rules duckdb` and `--rules lqp`; the
  interop flat models give the outcomes in plan H7.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan IR3-C1 | default export of `extraction.orm.json` exits 0 and equals its flat model's export except the added constants and `MODEL_NAME` | §6 `render_pyrel`; §8 T1 |
| plan IR3-C2 | `checking.orm.json` in the default mode exits 3 with the temporal message | §8 T2 |
| plan IR3-C3 | under `--rules lqp` and `--rules duckdb` both interop roots give their flat model's exit and message; at `260c4337` that is `paper_names_parent_method#0: family 'anchored'`, exit 3 | §8 T3 |
| plan IR3-C4, D5 | the program records the flattening record's sha256 and each include's pin; a re-pinned include changes the recorded digest | §6 constants; §8 T4, T5 |
| plan IR3-C5, H8, H9 | `test_direct_refusals[R13-pyrel-rules]`, `test_cli_guards[pyrel]`, `test_R7_guard_precedes_temporal_classification` change to the new behaviour | §8 T10 |
| plan IR3-C6, R0.6 | a model without includes exports byte-identically, in every mode | §8 T6 (goldens from the base code) |
| plan IR3-C7 | stale pin and nested include exit 3 with their code in every mode, never 70 | §6 mapping; §8 T7 |
| plan §6 render contract | `render_pyrel`'s one-read promise holds for models without includes | §6; docstring |
| plan §5 | PyRel export page names which mode accepts temporal models; route-list row; release note | §6 docs |

## 4. Standing rules bound to this phase

1. **Totality.** The new consumer is `flatten_for_export` in
   `export/pyrel_runtime.py`. It takes the model path and the bytes already
   read; every exception the composed loader or `flatten_model` can raise
   (`ModelValidationError`, `ModelLoadError`, `ReferenceInputError`,
   `FlatteningError`, `OSError`) becomes `ExportInputError`, so
   `commands/export.py` exits 3. T7 covers a stale pin, a nested include, a
   non-list `includes`, an escaping path and an absent include, in all three
   modes.
2. **Cap bounds the algorithm.** The added layer is one composition and one
   flattening, both linear. T8 runs `flatten_for_export` over the checking
   root with 1,000 extra object types in under 5 s. Rendering itself is
   existing code and is not timed here.
3. **Validation order.** Composition runs first, then the existing order:
   the default mode's temporal refusal and profile refusals, the `--rules`
   refusals. So a temporal include root with a stale pin reports the
   include code, and a valid temporal root reports the temporal message
   (T2, T7). This replaces the order `test_R7` pinned (include guard before
   temporal classification), which no longer has an include guard to order.
4. **One walk.** One function, `flatten_for_export`, serves both
   `render_pyrel` and `pyrel_rules.render`; one function renders the two
   constants, used by both program kinds.
5. **One home.** The constants' meaning is stated once, in the PyRel export
   page (`docs/agents/export-and-review.md`); the route list in
   representation-format.md cites it. That page also becomes the home of
   which mode accepts temporal models (plan §5).
6. **Measurement.** The expected outcomes of T1–T3 were measured on the
   flat models before this spec (plan H7 and §2 above).

## 5. Goal

`gnd export pyrel extraction.orm.json` exits 0 in the default mode; every
mode records the flattening of an include root in two constants; every
include refusal exits 3; a model without includes exports the bytes it
exports at `68e426ca`.

## 6. Design

### `src/gnd/export/pyrel_runtime.py` · `flatten_for_export` (new, about 30 lines)

```python
@dataclass(frozen=True)
class FlatExport:
    model_bytes: bytes          # the flat model, gnd-flattening/1's flat_model
    record_sha256: str          # sha256 of the flattening record bytes
    includes: tuple             # ((id, path, sha256), ...) in pin order

def flatten_for_export(model_path: Path, raw: bytes) -> FlatExport | None: ...
```

Returns `None` when `bytes_declare_includes(raw)` is false, so the caller
keeps its one-read path. Otherwise: `load_model(model_path)` (the loader
`gnd check` uses, references bound at the root's directory), checks
`model._authored_sha256 == sha256(raw)` (the bytes read are the bytes
composed; `ExportInputError("include:hash-mismatch")` otherwise), then
`flatten_model(model)`.

```python
def flattening_constants(flat: FlatExport | None) -> str:
    # "" for None; otherwise exactly:
    # "FLATTENING_RECORD_SHA256 = '<64 hex>'\nMODEL_INCLUDES = (('id', 'path', '<64 hex>'), ...)\n"
```

### `src/gnd/export/emit.py` · `render_pyrel` (about 8 lines)

After `text = _read_text(model_path)`: `flat = flatten_for_export(model_path,
text.encode("utf-8"))`; if `flat`, `text = flat.model_bytes.decode("utf-8")`.
Everything after is unchanged and sees the flat text, so `guard_document`
never fires for a resolved root and the temporal refusal applies to the
flat model. The program source adds `flattening_constants(flat)` right after
the `MODEL_NAME` line; `MODEL_NAME` stays the root's path. The docstring
says: one bounded read and no checker import for a model without includes;
an include root is composed and flattened first.

### `src/gnd/export/pyrel_rules.py` · `render` (about 8 lines)

After `raw = Path(model_path).read_bytes()`: `flat = flatten_for_export(...)`;
if `flat`, `raw = flat.model_bytes`. The `guard_bytes(..., route=
'pyrel_rules:2267')` call stays and no longer fires for a resolved root.
`flattening_constants(flat)` is appended after `SCHEMA = ...` in the
constants block. References are still bound by `_bind_reference(loaded,
Path(model_path))`, relative to the root's directory, which is where the
flat model's reference paths point.

### Documentation

- `docs/agents/export-and-review.md`: a short section "Include roots and
  temporal models": an include root is exported through its flat model
  (the bytes `gnd flatten` writes); the two constants and what they bind;
  the default mode refuses temporal models, `--rules` accepts them.
- representation-format.md route list: a `gnd export pyrel` row citing that
  page. `docs/release-notes.md`: one entry. Replies to #214 item 1 are
  drafted at the close.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IR3-D1 | Constant spelling (plan D5) | `FLATTENING_RECORD_SHA256` (a str) and `MODEL_INCLUDES` (a tuple of three-tuples), absent for a model without includes | as stated → **ruled as stated, delegated 2026-11-21** |
| IR3-D2 | Where `flatten_for_export` lives | (a) `export/pyrel_runtime.py`, beside `ExportInputError` and `_read_text`, which both renderers import; (b) a new module, which adds a layer-map row | (a) → **ruled (a), delegated 2026-11-21** |
| IR3-D3 | What replaces `test_R7` | (a) rewrite it to pin the new order: a temporal include root reaches the temporal message, a stale temporal include root the include code; (b) delete it. (b) loses an order pin | (a) → **ruled (a), delegated 2026-11-21** |
| IR3-D4 | `test_cli_guards[pyrel]` | drop the `pyrel` parameter (the route no longer refuses) and add the positive CLI case to the new file | as stated → **ruled as stated, delegated 2026-11-21** |
| IR3-D5 | IR3-C3's expected outcome | fixed from `main` at `260c4337` (RP2 not merged): exit 3, `paper_names_parent_method#0: family 'anchored'` in both `--rules` modes, as the flat models give | as stated → **ruled as stated, delegated 2026-11-21** |

## 8. Tests

New file `tests/test_ir3_pyrel_includes.py`; interop fixture as in IR1, and
`write_case` for the `--rules` digest case.

| # | Case | Expected |
|---|---|---|
| T1 | default export of `extraction.orm.json` and of `extraction.orm.flat.orm.json` written beside it | both exit 0; programs equal after removing the two constant lines and the `MODEL_NAME` line |
| T2 | default export of `checking.orm.json` | exit 3, "PyRel export does not support temporal models in Phase 1" |
| T3 | `--rules lqp` and `--rules duckdb` on both interop roots | exit 3, `paper_names_parent_method#0: family 'anchored'`, equal to the flat model's message |
| T4 | the constants in the default program (extraction root) and in both `--rules` programs (`write_case` root) | `FLATTENING_RECORD_SHA256` equals sha256 of `flatten_model(...).record_bytes`; `MODEL_INCLUDES` equals the root's pins |
| T5 | edit an include validly, re-pin, export again (default, extraction root) | `FLATTENING_RECORD_SHA256` differs |
| T6 | goldens: default program of `extraction.orm.flat.orm.json`, `--rules duckdb` and `--rules lqp` of `write_case`'s flat model, produced by the base code at `68e426ca`, path-normalized; and a negative control | byte-identical; one changed line differs |
| T7 | parametrized over modes × {stale pin, nested include, `includes` not a list, `../` path, absent include} | exit 3 with the include code; never 70 |
| T8 | `flatten_for_export` with 1,000 extra object types | under 5 s |
| T9 | `flatten_for_export` on an include-free model | `None`, and `load_model` is not called (monkeypatched to fail) |
| T10 | rewritten pins: `test_direct_refusals[R13-pyrel-rules]` (now asserts a rendered program), `test_R7_guard_precedes_temporal_classification` (D3), `test_cli_guards` without `pyrel` (D4) | green; each rewritten pin fails on the base code |

Focused lane (plan §9 IR3) plus `tests/test_rf1_cli_pins.py`, the guard
block and `ruff check src tests tools`.

## 9. Out of scope

Temporal models in the default mode; anchored constraints under `--rules`
(pyrel-rules-coverage RP2); detecting a stale program after export.

## 10. Size

Estimate: source 50 lines, tests 250 lines, docs 20 lines.

## 11. Approval instrument

Corpus-first: `tests/test_ir3_pyrel_includes.py` and the rewritten pins,
committed red before code: on `29a1bf09` with only the test bytes added, 29
cases fail; T6 and its negative control pass, as a preservation pin must on
the base. The goldens were produced by the base code at `68e426ca` in a
disposable worktree and equal the head's output byte for byte (measured
2026-11-21). T6 uses `write_case`'s flat model for the two `--rules`
goldens and the extraction flat model for the default one.
