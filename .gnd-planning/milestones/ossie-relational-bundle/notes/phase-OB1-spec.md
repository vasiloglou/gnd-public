# Phase OB1: a parameter for the Ossie output bound

## 1. Status

**Draft r1, 2026-11-24, awaiting owner review.** Not reviewed. Can be
implemented once the plan gate passes and D3 is ruled. No code is written.

## 2. Provenance

- Plan: [ossie-relational-bundle plan r1](ossie-relational-bundle-plan.md),
  §2.1, §4 row OB1, §10 D3. The plan is not reviewed and not approved.
- Source: the owner's issue file of 2026-11-24, issue 1 (plan §1.1 I1).
- Baseline code: `1926e895`, `src/gnd/export/ossie.py` (`render_ossie`),
  `src/gnd/commands/export.py` (`_cmd_export_ossie`, parser lines 172–177),
  `src/gnd/ossie_import.py` (`_read`, `_parse`, `_bounded_model`),
  `src/gnd/commands/checking.py:748` (import parser).
- No review has run over these bytes.

## 3. Obligations

| # | Source | Obligation | Discharged in |
|---|---|---|---|
| O1 | I1 Proposal | `--max-output-bytes N` | §6.2 |
| O2 | I1 Proposal | Default stays 10 MiB; nothing changes without the flag | §6.1, T1 |
| O3 | I1 Proposal | Bound applies equally to the ontology and both sidecars | §6.1, T3 |
| O4 | I1 Acceptance | Byte-identical without the flag | T1 |
| O5 | I1 Acceptance | `--max-output-bytes 33554432` exports a model above 10 MiB completely | T2 |
| O6 | I1 Acceptance | Tests cover both | T1, T2 |
| O7 | Plan §1.2 | It is a refusal, not a truncation: keep all-or-nothing publication | §6.1, T3 |
| O8 | Plan D3 | Ceiling and argument validation | §6.2, T4 |
| O9 | Plan D3 (if a) | `gnd import ossie --max-input-bytes N` reads back what was exported | §6.3, T6 |
| O10 | project.md rule 2 | Time-bound test for the larger admitted size | T5 |
| O11 | project.md guard list | Issue-171 guard files and `uv run ruff check` in the gate | §8 |

## 4. Standing rules bound to this phase

1. **Totality.** The new input is a CLI integer. `argparse` with a bounded
   `type=` callable refuses non-integers, `0`, negatives and values above
   the ceiling with exit 2 before any read. No new document consumer is
   added. The import side passes the existing total readers a different cap
   and adds no new parser.
2. **Cap bounds the document, not the algorithm.** Raising the bound admits
   larger outputs, but the input is still capped by `MAX_MODEL_BYTES`. The
   work grows with the model, not with N. T5 bounds the time of the large
   export (the existing `test_pointer_walk_time_bound` and
   `test_projection_time_bound` stay as they are).
3. **Validation order.** Argument validation (exit 2) comes before the model
   read. The size check stays after rendering and before publication, as
   today. A run that is both strict-refused and oversized reports the strict
   refusal first, which is today's order (the strict checks come before the
   size check in `render_ossie`). T3b pins this order.
4. **One walk.** One size check over all artifacts (`max(len(a) for a in
   artifacts)`), extended unchanged when OB3 adds files.
5. **One home.** The flag, its default and its ceiling are stated once in
   `representation-format.md` § "Ossie interchange". Help text cites it.
   Docs follow in OB5.
6. **Measure.** The ratio of output to model size is measured on the generated
   fixture and recorded, rather than assumed.

## 5. Goal

`gnd export ossie MODEL --out OUT` with no new flag exits with the same code
and writes the same bytes as at `1926e895` for every census model.
`--max-output-bytes N` with `10485760 ≤ largest artifact ≤ N` exits 0 and
publishes all three files. If the largest artifact is above N, the run exits 3
with `ossie:output-size` on stderr and publishes nothing. An invalid N exits 2.
Under D3 (a), `gnd import ossie DOC --max-input-bytes N` exits 0 on that
document when N covers it, and exits 3 with the existing `-size` rule when it
does not.

## 6. Design

### Reuse

| Capability | Searches | Found | Decision |
|---|---|---|---|
| Byte bound on artifacts | `components_index.py search "output size"`, `search "byte cap"`; `git grep max_output_bytes` | `review/service.py` `max_output_bytes` (subprocess streams; another subject) | `new` parameter, local to the Ossie export |
| Bounded integer CLI argument | `git grep "type=_positive\|def _bounded_int"` (to be run at implementation) | to fill | `reuse` if found, else a small local validator |
| Create-once publication | `safefs.publish_new_files` | canonical | `reuse`, unchanged |

### 6.1 `src/gnd/export/ossie.py` (about +10 lines)

```python
DEFAULT_MAX_OUTPUT_BYTES = 10 * 1024 * 1024      # equals input_policy.MAX_BYTES today; not aliased
MAX_OUTPUT_BYTES_CEILING = 256 * 1024 * 1024     # D3

def render_ossie(model_path: Path, *, output_format: str, strict: bool = False,
                 max_output_bytes: int = DEFAULT_MAX_OUTPUT_BYTES) -> OssieArtifacts: ...
```

The final check becomes
`if max(len(data), len(sidecar), len(report)) > max_output_bytes: raise OssieInputError("ossie:output-size")`.
`render_ossie` checks `1 <= max_output_bytes <= MAX_OUTPUT_BYTES_CEILING` and
raises `ValueError` otherwise, which is a programming error for library
callers. It does not depend on `input_policy.MAX_BYTES`, so a later change to
input caps cannot move the export default.

### 6.2 `src/gnd/commands/export.py` (about +15 lines)

```text
--max-output-bytes N   largest size in bytes of each written file
                       (default 10485760; at most 268435456)
```

The `type=` callable refuses with a message naming the bounds. The value is
passed to `render_ossie`. The rest of `_cmd_export_ossie` is unchanged.

### 6.3 `src/gnd/ossie_import.py` and `commands/checking.py` (D3 a only; about +25 lines)

`import_ossie(..., max_input_bytes: int = MAX_BYTES)` is threaded to `_read`
(read cap and `-size` rule), to `_parse` (`guard_yaml(data,
max_bytes=max_input_bytes)`) and to the two `_bounded_model` caps (`MAX_BYTES`
and `2 * MAX_BYTES`). The **model** it writes stays capped by
`MAX_MODEL_BYTES`, because a restored model above the loader cap could not be
used anyway. CLI: `--max-input-bytes N`, with the same validator and ceiling.
Exact function names are to be confirmed against the module at implementation.
The spec amends here if they differ.

## 7. Decisions

| ID | Question | Readings and costs |
|---|---|---|
| D3a | Ceiling value | 256 MiB (proposal): artifacts are built in memory, so a run peaks at several times N. Uncapped: one flag can exhaust memory. 64 MiB: covers the reporter's 32 MiB with 2× headroom. |
| D3b | Import flag in OB1 | Yes (proposal): round trip holds for large documents. No: OB1 shrinks by T6 and §6.3, and large exports are one-way (the import's exit 3 `-size` stays). |
| D3c | Library default constant | Separate `DEFAULT_MAX_OUTPUT_BYTES` (proposal). Alias of `MAX_BYTES`: a future input-cap change would silently change export output. |

## 8. Tests

All in `tests/test_ossie_export.py` unless noted.

| ID | Case | Expected |
|---|---|---|
| T1 | Census, no flag: every artifact's sha256 equals a digest list captured from `1926e895` and committed at `tests/data/ossie_ob1_baseline.json` | equal; CLI exit 0 |
| T2 | Generated model (fixture builder in the test, deterministic) whose largest artifact is above 10 MiB, `--max-output-bytes 33554432` | exit 0; three files published; ontology validates; sidecar and report bind its sha256 |
| T2b | The same model, no flag | exit 3, `ossie:output-size`, no file exists |
| T3 | Small census model, N set to 1 byte below its largest artifact, once for each artifact being the largest (each branch of `max`, built by choosing models or formats so each artifact wins once) | exit 3, nothing published |
| T3b | `--strict` with a refused population **and** N below size | strict refusal message (order pin) |
| T4 | `--max-output-bytes` `0`, `-1`, `1.5`, `abc`, `268435457` | exit 2, nothing read |
| T4b | `--max-output-bytes 268435456` on a small model | exit 0 |
| T5 | T2's export completes under a stated bound (set from measurement, recorded in the phase record) | pass |
| T6 | (D3 a) `tests/test_ossie_import.py`: import of T2's document with `--max-input-bytes 33554432` | exit 0, restored model equal to the source per the existing round-trip comparison |
| T6b | (D3 a) same document, no flag | exit 3, existing `-size` rule |
| T6c | (D3 a) invalid `--max-input-bytes` values as T4 | exit 2 |

Branch walk: argument valid or invalid; each artifact as the largest; below,
equal to and above N (T3 uses N = size − 1; add N = size for the equality
branch, expected exit 0); strict before size.

Gate: `uv run pytest -q tests/test_ossie_export.py tests/test_ossie_import.py --tb=short`,
then the issue-171 guard list from `project.md`, then `uv run ruff check`.

## 9. Out of scope

Semantic model and mapping (OB3), Rmap (OB2), streaming, any change to
`input_policy.MAX_BYTES` or `MAX_MODEL_BYTES`, include-bearing models, docs
beyond the normative sentence (OB5).

## 10. Size

Estimate: about 50 source lines and about 150 test lines (the fixture builder
included). The baseline digest file is data.

## 11. Approval instrument

This prose. No fixture corpus is needed: T1's answer key is the captured
baseline digests.
