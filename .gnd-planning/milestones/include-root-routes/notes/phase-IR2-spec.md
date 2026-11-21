# Phase IR2 spec · `gnd flatten`

## 1. Status

**Delegated approval (auto=true), 2026-11-21**, over this spec r1 and the
corpus `tests/test_ir2_flatten.py` (sha256 `2714b5a549ea9b9d1ba56317dff102633424b33b173d432ad2b085fafeb82e09`). Authorization: the
owner's `/process-milestone include-root-routes auto` in this session,
within plan r4 (`001-plan-gate.md`); IR1's record is `002-phase-IR1.md`.
Instrument: the corpus (§11). Budget: one Codex review round over the diff.
This is the driving agent's ruling, not the owner's reading. Prior status,
kept: "Draft r1, 2026-11-21, awaiting its delegated spec gate (`auto=true`).
Not implementable until that gate is recorded here and IR1's record exists."

## 2. Provenance

- Plan: `notes/include-root-routes-plan.md` r4, approved in
  `001-plan-gate.md` (§1 H2, H5; §2 IR2; §4 IR2-C1 to IR2-C5; §10 D1, D2).
- Code read at `1e419a88` on 2026-11-21. No review opinion covers these bytes.
- Measured earlier the same day: `flatten_model(load_model("checking.orm.json"))`
  succeeds on the temporal interop root and keeps both root constraints,
  `parent_in_catalog` and `publication_not_before_submission` (plan §1 H5).

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan IR2-C1 | `gnd flatten checking.orm.json --out DIR` exits 0; the two files equal `flatten_model`'s bytes; origins named; temporal rule kept | §6; §8 T1 |
| plan IR2-C2 | `gnd check` parity between the root and `checking.orm.flat.orm.json` in the root's directory | §8 T2 |
| plan IR2-C3 | a model without includes, exit 3; an include refusal, exit 3 with its code | §6 refusals; §8 T3–T5, T12 |
| plan IR2-C4 | either output file present: exit 11, nothing written or changed | §6 publication; §8 T6 |
| plan IR2-C5, R0.6 | `gnd extract` on the temporal include root names `gnd flatten`; the include-free temporal message is unchanged | §6 extract; §8 T8, T9 |
| plan §2 IR2 `(p2)` | reference paths of a flat model written elsewhere | §7 IR2-D2; §8 T11 |
| plan §2 IR2 `(p1)` | registration in `src/gnd/cli.py`, `tools/gnd_entrypoints.json`, `tools/gnd_layers.json` | §6; §8 T15 and the guard block |
| plan §5 | route-list row, flattening subsection, `docs/reference/cli.md`, release note | §6 docs |
| plan D1 | a separate command, `gnd flatten MODEL --out DIR` | §6 |

## 4. Standing rules bound to this phase

1. **Totality.** The new consumer is `flatten_to`. Its inputs are the model
   path (through `load_model`, total over arbitrary bytes today) and the
   `--out` path (through `gnd.synth.paths.safe_output_path`, as extract
   does). Hostile model bytes (T3, T4, T5, T12) and a missing file (T7) exit
   through a refusal band, never a traceback.
2. **Cap bounds the algorithm.** `flatten_model` is one canonical
   serialization and one re-entry load, both linear. T13 flattens the root
   with 1,000 extra object types in under 5 s.
3. **Validation order.** Load and flatten first, then the output checks:
   an invalid model with an existing output reports 3, not 11 (T14).
4. **One walk.** The temporal message hint is added in the one function
   `require_non_temporal` (`terms.py:113`) by an optional argument, not by a
   second copy of the message in `extract/service.py`.
5. **One home.** The record format keeps its home in representation-format.md
   "Extraction flattening record"; `gnd flatten` gets one paragraph there and
   a route-list row; `docs/reference/cli.md` cites it.
6. **Measurement.** The reference-path question (IR2-D2) is settled by T11
   running `gnd check` on a flat model written elsewhere.

## 5. Goal

`gnd flatten checking.orm.json --out DIR` exits 0 and writes the two files
`flatten_model` produces; every refusal exits 3, 11 or 66 as listed; `gnd
extract` on that root still exits 3 and names `gnd flatten`.

## 6. Design

### `src/gnd/extract/flatten_service.py` (new, about 70 lines; layer `lanes`, lane `extract`)

```python
def flatten_to(model_path: str, out_dir: str, *, output_format: str = "text") -> int: ...
```

1. `model = load_model(model_path)`. `FileNotFoundError` → stderr
   `missing input: …`, exit 66. `ModelValidationError` → each issue printed
   as `ERROR at <path>: <message> [<rule_id>]` (extract's
   `_print_issues`), exit 3. `ModelLoadError`, `ReferenceInputError` →
   `ERROR: …`, exit 3.
2. `if not model.includes:` stderr `ERROR at $: flatten needs a model that
   declares includes [include:declaration]`, exit 3. (A version-5 document
   with only `fact_type_constraints` already refused in step 1 with
   `include:declaration`.)
3. `flat = flatten_model(model)`; `FlatteningError` → `ERROR: …`, exit 3.
4. Names: `names = _flattening_names(bundle_stem(model_path))`, so
   `checking.orm.json` gives `checking.orm.flat.orm.json` and
   `checking.orm.flattening.json`. Destinations through
   `safe_output_path(Path(out_dir), name)`; a refused path → exit 74.
5. Publication, both or neither: if either destination exists (or is a
   symlink), stderr `output exists: <path>`, exit 11, nothing written. Both
   files are staged in a temporary directory inside `out_dir` and moved in
   with `os.link` (no replace); a failure of the second link unlinks the
   first, then exit 74.
6. If the model declares `reference_populations` and `out_dir` is not the
   model's directory, one stderr line: `note: reference paths in <flat>
   stay relative to <model dir>` (IR2-D2).
7. stdout: text `Flattened <model> to <flat> and <record> (record sha256
   <hex>)`; with `--format json`, canonical JSON
   `{"command": "flatten", "model": {"path", "sha256"}, "flat_model": {"path",
   "sha256"}, "record": {"path", "sha256"}}`. Exit 0.

### `src/gnd/commands/flatten.py` (new, about 30 lines; layer `entry`)

`add_parsers(subparsers, *, command=None)` and `handle(args, parsers)` in the
shape of `commands/judgments.py`: positional `model`, required `--out`,
`--format {text,json}` default `text`; help text lists the exits 0, 3, 11,
64, 66, 74. Registered in `src/gnd/cli.py` beside the other
`add_parsers(subparsers, command=...)` calls (`cli.py:650-676`) as
`command='flatten'`. `tools/gnd_entrypoints.json`: `gnd.commands.flatten`
in `scope`, `gnd.extract.flatten_service` in `service_targets`, and the
binding `gnd.commands.flatten → gnd.extract.flatten_service`.
`tools/gnd_layers.json`: both modules with the layers above.

### `src/gnd/terms.py` · `require_non_temporal` (about 4 lines)

```python
def require_non_temporal(model: Any, consumer: str, *, hint: str | None = None) -> None: ...
```

The message becomes `f"{consumer} does not support temporal models in Phase
1"` plus `f"; {hint}"` when `hint` is given. `extract/service.py:191` passes
`hint="gnd flatten writes the flat model of a temporal include root"` only
when `model.includes` is non-empty. Every other caller and the include-free
extract path keep today's bytes (rf1 goldens).

### Documentation

- representation-format.md, "Extraction flattening record": one paragraph
  saying `gnd flatten MODEL --out DIR` writes the same two files for any
  include root, temporal or not, without the bundle or its index, and that
  reference paths stay relative to the authored root's directory. Route
  list: a `gnd flatten` row.
- `docs/reference/cli.md`: a row for `gnd flatten`.
- `docs/release-notes.md`, unreleased: one entry.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IR2-D1 | Service home | (a) `gnd.extract.flatten_service`, beside `_flattening_names` and `bundle_stem`; (b) `gnd.model.flattening`, which would import output-path code into the model layer | (a) → **ruled (a), delegated 2026-11-21** |
| IR2-D2 | `--out` other than the model's directory when references are declared | (a) allow, with a stderr note; exit 0; (b) refuse, exit 3. They differ in exit. Extract already writes its flat model into another directory with the same coordinate rule | (a) → **ruled (a), delegated 2026-11-21** |
| IR2-D3 | Exit for an existing output | 11 (`EXIT_COLLISION`), as plan IR2-C4 fixes | 11 → **ruled 11, delegated 2026-11-21** |
| IR2-D4 | Where the extract hint lives | (a) an optional `hint` on `require_non_temporal`; (b) a second message in `extract/service.py` | (a) → **ruled (a), delegated 2026-11-21** |

## 8. Tests

New file `tests/test_ir2_flatten.py`; the interop fixture as in IR1.

| # | Case | Expected |
|---|---|---|
| T1 | `gnd flatten checking.orm.json --out OUT` | exit 0; files equal `flatten_model` bytes; record `origins` contains `includes[chronology]`; flat `constraints` ids include `publication_not_before_submission` |
| T2 | flatten into the root's directory; `gnd check` on root and flat with `composed.population.json` | equal exit and equal `report.verdicts` |
| T3 | a version-5 model with no includes (`write_case`'s vocabulary alone) | exit 3, `flatten needs a model that declares includes` |
| T4 | include edited without re-pin | exit 3, `include:hash-mismatch` on stdout |
| T5 | nested include | exit 3, `include:forbidden-section` |
| T6 | the flat file exists; separately, the record exists | exit 11 each; the other file not created; existing bytes unchanged |
| T7 | missing model path | exit 66 |
| T8 | `gnd extract checking.orm.json --out B` | exit 3, message contains `gnd flatten` |
| T9 | control: `tests/test_rf1_semantic_pins.py` (include-free temporal extract goldens) | exit 0 |
| T10 | `--format json` | digests equal the written files' sha256 |
| T11 | flatten into another directory; `gnd check` on that flat model | exit 0 from flatten with the stderr note; `gnd check` there refuses its reference read (exit 3), which is what the note warns of |
| T12 | orphan `fact_type_constraints` | exit 3, `include:declaration` |
| T13 | 1,000 extra object types in `chronology` | exit 0 in under 5 s |
| T14 | invalid model and an existing output | exit 3 (load precedes output checks) |
| T15 | `gnd flatten --help` | exit 0; the guard block's entry-point and layer tests pass |

Focused lane (plan §9 IR2) plus the guard block and `ruff check src tests
tools`.

## 9. Out of scope

Writing an extraction bundle or index; changing `gnd-flattening/1`;
binding references for a flat model written elsewhere; IR3.

## 10. Size

Estimate: source 110 lines, tests 220 lines, docs 20 lines.

## 11. Approval instrument

Corpus-first, as IR1: IR2 adds an exit-code contract. The corpus is
`tests/test_ir2_flatten.py`, committed red before code: on `4e80ec9a` with
only that file added, all 15 cases fail (the command does not exist, exit
64), measured 2026-11-21. T9 is the existing `tests/test_rf1_semantic_pins.py`,
run in the focused lane, not a case in the new file. The IR2-D2 measurement
(rule 6) ran before the gate: a flat model of `checking.orm.json` written to
another folder makes `gnd check` exit 3 on its reference read, and written
into the root's folder it gives the root's exit (4), so T11 and T2 expect
those values.
