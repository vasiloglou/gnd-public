# Phase OB1: parameters for the Ossie size bounds

## 1. Status

**owner-decided (2026-11-24).** r2 (sha256 `068f24c4…3824`) was approved at the
[OB1 spec gate](../003-OB1-spec-gate.md). This r2.1 adds only this status line
and §12, the implementation findings; §1–§11 are the approved bytes.

## 2. Provenance

- **Plan:** [ossie-relational-bundle plan r2](ossie-relational-bundle-plan.md),
  §1.2, §2.1, §4 OB1, and §10 D3 and D11. r2 is not reviewed and not
  approved.
- **r1 of this spec** (sha256 `1b128bbe…cd1a`) was not a panel subject. The
  panel reviewed plan r1 only. Changes made here for the plan fixes are
  tagged `(p1 Fn)` with the plan fix's rank; they are not a review of this
  spec.
- **Source:** the owner's issue file of 2026-11-24, issue 1 (plan §1.1 I1).
- **Baseline code at `1926e895`:**
  - `src/gnd/export/ossie.py` (`render_ossie`)
  - `src/gnd/commands/export.py` (`_cmd_export_ossie`; parser lines 172–177)
  - `src/gnd/ossie_import.py` (`_read`, `_parse`, `_bounded_model`, the
    loss-report builder near line 642, `plan_ossie_import`)
  - `src/gnd/input_policy.py` (`loads`, `_text`, `guard_yaml`)
  - `src/gnd/commands/checking.py:748` (the import parser)
  - `src/gnd/exits.py` (`EXIT_USAGE = 64`, `EXIT_COLLISION = 11`)

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | I1 Proposal | `--max-output-bytes N` | §6.2 |
| O2 | I1 Proposal | The default stays 10 MiB, and nothing changes without the flag | §6.1, T1 |
| O3 | I1 Proposal | The bound applies equally to the ontology and both sidecars | §6.1, T3 |
| O4 | I1 Acceptance | Byte-identical output without the flag | T1 |
| O5 | I1 Acceptance | `--max-output-bytes 33554432` exports a model above 10 MiB completely | T2 |
| O6 | I1 Acceptance | Tests cover both cases | T1, T2 |
| O7 | Plan §1.2 | It is a refusal, not a truncation, so publication stays all-or-nothing | §6.1, T3 |
| O8 | Plan D3, §2.1 | A ceiling, and argument validation with exit 64 `(p1 F1)` | §6.2, T4 |
| O9 | Plan D3 (b), §1.2 | `gnd import ossie --max-input-bytes N` moves the read, YAML guard, JSON `loads` and loss-size caps, keeps `model-size` and `MAX_MODEL_BYTES`, and is tested at each one `(p1 F5)` | §6.3, T6 |
| O10 | Plan OB1-C2, D11 | Record the output-to-source size ratio `(p1 F8)` | T2, record |
| O11 | project.md rule 2 | A time-bound test for the larger admitted size | T5 |
| O12 | project.md guard list | The issue-171 guard files and `uv run ruff check` in the gate | §8 |

## 4. Standing rules bound to this phase

1. **Totality.** The new inputs are CLI integers. A bounded `type=` callable
   refuses non-integers, `0`, negatives and values above the ceiling. The
   CLI's usage mapping turns that into **exit 64** before any read
   `(p1 F1)`. The import side passes the existing total readers a different
   cap and adds no new parser. `input_policy.loads` gains an optional
   `max_bytes` with the current default, so every other caller is
   unchanged.
2. **Cap bounds the document, not the algorithm.** Raising the bound admits
   larger outputs, while the export source is still capped by
   `MAX_MODEL_BYTES`. The work grows with the model, not with N. T5 bounds
   the time of the large export, and T6 the time of the large import.
3. **Validation order.**
   - Argument validation (exit 64) comes before the model read.
   - The size check stays after rendering and before publication, as today.
   - A run that is both strict-refused and oversized reports the strict
     refusal first, which is today's order. T3b pins it.
   - On import, the moved caps keep their current order: read, then parse,
     then model-size, then loss-size.
4. **One walk.** One size check runs over all artifacts
   (`max(len(a) for a in artifacts)`). OB3 extends it unchanged.
5. **One home.** The flags, the default and the ceiling are stated once, in
   `representation-format.md` § "Ossie interchange". The help text cites
   it, and the docs follow in OB5.
6. **Measure.** The output-to-source ratio is measured on the generated
   fixture and recorded, not assumed `(p1 F8)`.

## 5. Goal

**Export:**
- With no new flag, `gnd export ossie MODEL --out OUT` exits with the same
  code and writes the same bytes as at `1926e895` for every census model.
- With `--max-output-bytes N`, a run whose largest artifact is between
  10 MiB and N inclusive exits 0 and publishes all three files.
- If the largest artifact is above N, the run exits 3 with
  `ossie:output-size` on stderr and publishes nothing.
- An invalid N exits 64.

**Import, under D3 (b):** `gnd import ossie DOC --out MODEL
--max-input-bytes N` exits 0 on that document when N covers it. When N does
not cover it, the run exits 3 with the existing rule of the first cap it
hits.

**Scope:** OB1 fixes issue 1 for export sources of at most `MAX_MODEL_BYTES`.
Larger sources are D11.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Byte bound on artifacts | `components_index.py search "output size"` and `search "byte cap"`; `git grep max_output_bytes` | `review/service.py` `max_output_bytes`, which bounds subprocess streams (another subject) | `new` parameter, local to the Ossie export |
| Bounded integer CLI argument | `git grep "type=_positive\|def _bounded_int"` (to run at implementation) | to fill | `reuse` if found, else a small local validator |
| Create-once publication | `safefs.publish_new_files` | canonical | `reuse`, unchanged |
| Parameterized JSON cap | `input_policy.loads` / `_text` | fixed `MAX_BYTES` | `adapt`: add an optional `max_bytes`, default unchanged |

### 6.1 `src/gnd/export/ossie.py` (about +10 lines)

```python
DEFAULT_MAX_OUTPUT_BYTES = 10 * 1024 * 1024      # equals input_policy.MAX_BYTES today; not aliased
MAX_OUTPUT_BYTES_CEILING = 256 * 1024 * 1024     # D3

def render_ossie(model_path: Path, *, output_format: str, strict: bool = False,
                 max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES) -> OssieArtifacts: ...
```

- The final check becomes
  `if max(len(data), len(sidecar), len(report)) > max_output_bytes: raise OssieInputError("ossie:output-size")`.
- `render_ossie` checks `1 <= max_output_bytes <= MAX_OUTPUT_BYTES_CEILING`
  and raises `ValueError` otherwise. For a library caller, that is a
  programming error.
- The default is not tied to `input_policy.MAX_BYTES`, so a later change to
  input caps cannot move it.

### 6.2 `src/gnd/commands/export.py` (about +15 lines)

```text
--max-output-bytes N   largest size in bytes of each written file
                       (default 10485760; at most 268435456)
```

The `type=` callable raises `argparse.ArgumentTypeError` with a message
naming the bounds. GND's parser maps that to `EXIT_USAGE` (64) `(p1 F1)`.
The rest of `_cmd_export_ossie` is unchanged.

### 6.3 Import caps, D3 (b) only (about +35 lines) `(p1 F5)`

| Cap at baseline | Where | Under `--max-input-bytes N` |
|---|---|---|
| Read cap, rule `<rule>-size` | `ossie_import._read` (lines 66, 78) | moves to N |
| YAML guard | `_parse` → `guard_yaml(data)` default `MAX_BYTES` | moves to N (`guard_yaml(data, max_bytes=N)`) |
| JSON decode | `_parse` → `input_policy.loads` → `_text` fixed `MAX_BYTES` | moves to N, through a new optional `loads(..., max_bytes=)` |
| Restored model, rule `model-size` | `_bounded_model` (line 329), `MAX_BYTES` | **kept**. The restored model must load under `MAX_MODEL_BYTES` anyway, and its source fitted that cap. |
| Import loss report, rule `loss-size` | near line 642, `2 * MAX_BYTES` | moves to `2 * N` |

- **CLI:** `--max-input-bytes N`, with the same validator and ceiling as
  §6.2 (exit 64 on an invalid value).
- **Library:** `plan_ossie_import(path, *, max_input_bytes=MAX_BYTES)`,
  threaded to `_read` and `_parse` and to the loss-report builder.
- **Confirm at implementation:** the function names above. The spec is
  amended if they differ.

## 7. Decisions

| ID | Question | Readings and costs |
|---|---|---|
| D3a | The ceiling value | **256 MiB (proposal):** artifacts are built in memory, so a run peaks at several times N. **Uncapped:** one flag can exhaust memory. **64 MiB:** covers the reporter's 32 MiB with 2× headroom. |
| D3b | Import flag in OB1: plan D3 (a) or (b) | **(b), the proposal:** the round trip holds for large documents. **(a):** OB1 drops T6 and §6.3; large exports are one-way, and the import keeps exiting 3 with `-size`. |
| D3c | The library default constant | **A separate `DEFAULT_MAX_OUTPUT_BYTES` (proposal).** An alias of `MAX_BYTES` would let a future input-cap change silently change export output. |

D11 (the export source cap) is not decided in OB1. OB1 supplies its
measurement (T2).

## 8. Tests

All in `tests/test_ossie_export.py` unless noted.

| ID | Case | Expected |
|---|---|---|
| T1 | Census, no flag. Every artifact's sha256 equals a digest list captured from `1926e895` and committed at `tests/data/ossie_ob1_baseline.json`. | equal; CLI exit 0 |
| T2 | A generated model (a deterministic fixture builder in the test) within `MAX_MODEL_BYTES`, whose largest artifact is above 10 MiB, with `--max-output-bytes 33554432` | exit 0; three files published; the ontology validates; the sidecar and report bind its sha256; the output-to-source ratio is recorded in the phase record `(p1 F8)` |
| T2b | The same model, no flag | exit 3, `ossie:output-size`, no file exists |
| T3 | A small census model with N one byte below its largest artifact, once with each artifact being the largest (models or formats chosen so each one wins once) | exit 3, nothing published |
| T3a | The same, with N equal to the largest artifact | exit 0 |
| T3b | `--strict` with a refused population **and** N below the size | the strict refusal message (order pin) |
| T4 | `--max-output-bytes` set to `0`, `-1`, `1.5`, `abc`, `268435457` | **exit 64** `(p1 F1)`, nothing read |
| T4b | `--max-output-bytes 268435456` on a small model | exit 0 |
| T5 | T2's export completes under a stated bound, set from measurement and recorded | pass |
| T6 | (D3 b) In `tests/test_ossie_import.py`: import T2's document, as YAML and as JSON, with `--max-input-bytes 33554432` | exit 0; the restored model equals the source under the existing round-trip comparison |
| T6a | (D3 b) The same document with no flag | exit 3, rule `input-size` (the read cap; the sidecar and report reads use `sidecar-input-size` and `report-input-size`, and move with it) |
| T6b | (D3 b) Per moved cap, with N chosen so the read passes and that cap is the first to bind: the YAML guard, JSON `loads`, and `loss-size` (a document whose loss report alone exceeds `2 * N`) `(p1 F5)` | exit 3 with that cap's rule |
| T6c | (D3 b) The kept cap: a document whose restored model exceeds `MAX_BYTES`, under a large N | exit 3, `model-size` |
| T6d | (D3 b) Invalid `--max-input-bytes` values, as T4 | exit 64 |
| T6e | `input_policy.loads` with no `max_bytes` refuses at today's limit | unchanged |

**Branch walk:**
- the argument is valid or invalid;
- each artifact is the largest in turn;
- below N, equal to N, and above N;
- strict before size;
- on import, each moved cap binds first once, and the kept cap binds once.

**Gate:**
1. `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py --tb=short`
2. the issue-171 guard list from `project.md`
3. `uv run ruff check`

## 9. Out of scope

- The semantic model and mapping (OB3), and the Rmap (OB2).
- Streaming.
- Any change to `input_policy.MAX_BYTES` or `MAX_MODEL_BYTES`. The export
  source cap is D11.
- Include-bearing models.
- Docs beyond the normative sentence (OB5).

## 10. Size

Estimate: about 70 source lines and about 220 test lines, including the
fixture builders. The baseline digest file is data.

## 11. Approval instrument

This prose. No fixture corpus is needed, because T1's answer key is the
captured baseline digests.

## 12. Implementation findings (r2.1, recorded during OB1)

| # | Finding | Effect |
|---|---|---|
| IF1 | **Refuted premise (plan §1.2).** "No test covers this branch" was false. `tests/test_ossie_import.py::test_export_bounds_all_import_envelopes` already covered `ossie:output-size`, by patching `gnd.export.ossie.MAX_BYTES`. | That test and `test_restored_output_size_caps` were moved to the new parameters (`max_output_bytes`, `max_bytes`) with their assertions unchanged. |
| IF2 | **A sixth import cap.** `input_policy.JSONDecoder.raw_decode` re-checks `_text` at the default 10 MiB, after `loads` has checked it. | `JSONDecoder` takes `max_bytes`, and `loads` passes it on. T6 failed with `report-syntax` until this was fixed. |
| IF3 | **T6b is unreachable for two caps.** The YAML guard and the JSON decode caps equal the read cap N over the same bytes, so neither can bind before the read. | Those two caps are covered by T6, which fails unless both move (IF2 shows it). T6b keeps the reachable `loss-size` cap, using the flights fixture at N = its size. |
| IF4 | **T6a's rule.** On a large bundle, the file above 10 MiB is the loss report, so the default refusal is `report-input-size`, not `input-size`. | T6a asserts `report-input-size`. |
| IF5 | **T6c by seam.** A restored model above 10 MiB needs a foreign source of about 5.5 MB, which takes minutes to build. | T6c lowers `ossie_import.MAX_BYTES` and passes a large N. The kept cap still refuses, which shows it is independent of the flag. |
| IF6 | **Ceiling home.** `ossie_import` (layer `entry`) does not import the export lane. | The ceiling is `input_policy.MAX_BYTES_CEILING`, and `MAX_OUTPUT_BYTES_CEILING` names it in the export. |
| IF7 | **Missed affected consumers.** `tests/test_rf1_cli_pins.py` pins the CLI help text and exit probes, and `tests/test_rf7_input_policy.py` lowers `MAX_BYTES` through the module seam. | The CLI pins declare both new flags as successors. Defaults in `input_policy` resolve `MAX_BYTES` at call time (review finding F1). Both files join the gate. |
| IF8 | **Baseline path.** `tests/data/` does not exist in this repository. | The baseline is at `tests/fixtures/ossie_ob1_baseline.json`. |
| IF9 | **Measured ratio (OB1-C2, for D11).** A 5,000-fact model of 1.83 MB gives a 10.95 MB JSON loss report (about 6×), a 7.34 MB sidecar and a 0.87 MB ontology. The export takes about 3 s; the import about 7 s (JSON) and 8.5 s (YAML). | At this ratio, a 32 MiB export needs a source of about 5.3 MB, within `MAX_MODEL_BYTES`. The reporter's models differ in shape, so this is an estimate only. |
