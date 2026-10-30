# Phase WN2 -- `gnd why-not`, `gnd.api.why_not`, schema, pins and docs

## 1. Status

**Draft r1.** Prepared under `/process-milestone derivation-why-not auto`. Per
WN-D10 (approved as proposed) the approval instrument is corpus-first: the
golden payloads, expected exits and refusals of §8 are committed and run red
before any WN2 code. The gate is a delegated approval (auto=true), recorded in
the appended section below; no review opinion covers these bytes until the
phase-diff review.

## 2. Provenance

- Derived from the approved [plan r3](derivation-why-not-plan.md) §2 (command,
  API, payload sketch, exit bands), §3 (homes), §4 WN2 (C1-C6), §5 and §9, and
  the [WN1 record](../002-phase-WN1.md), at WN1's commit on
  `claude/milestone-issue-66-72e872`.
- Rulings applied as approved: WN-D4 (API raw, CLI redacted unless `--raw`),
  WN-D5 (bands), WN-D7 (kernel home), WN-D9 (five samples), WN-D10
  (corpus-first), WN-D11 (one row matching `--fact-type`), WN-D12 (schema
  at `src/gnd/why-not.schema.json`, no skill copy), WN-D13 (fix the stale
  ten-name tuple), WN-D14 (malformed row before unsupported).
- Carried from WN1: WN1-Q3 (a references case) is discharged here by G9.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| WN2-C1, O6, O8, O11 | command and API through the witness input lane; limit projection; hostile inputs exit 3 | §6.1, §6.2; T1, T3 |
| WN2-C2, O3 | schema validates every golden; closed redacted allow-list; leak test; `VENDORED_SCHEMAS` | §6.3, §6.4; T2, T4 |
| WN2-C3, O12 | API, CLI and handler pins | §6.6; T5 |
| WN2-C4, O13 | reference page, nav, `cli.md`, `python-api.md`, `capabilities.md`, one home for the API count, release note | §6.7; T7 |
| WN2-C5, O9 | `check` and `witness` payloads unchanged on existing fixtures | T6 |
| WN2-C6, O10 | counter-based time bounds on target intake and view rendering | T8 |
| WN1-Q3 | a references case | G9 |

## 4. Rules bound to WN2

- **WN-R1 read-only.** No change to `check`, `witness`, `replay` or the report
  schema. T6 runs their existing contract tests unchanged.
- **WN-R5 values.** The API returns raw values like `api.witness`. The CLI
  prints the redacted view unless `--raw`.
- **WN-R6 one home.** `docs/reference/why-not.md` becomes the normative home of
  the step and blocker definition. The kernel docstring and WN1 spec §6.3 then
  point to it.
- **WN-R8 anonymity.** T17 from WN1 covers every file this phase adds.

Standing rules:

1. **Totality.** `api.why_not` returns a payload for every input. A defect
   (`WhyNotInternalError`) is the only exception that escapes; it is not an
   input outcome.
2. **Cap bounds the algorithm.** Intake runs under the projected witness limits
   (§6.2); the kernel's budgets are unchanged. T8 pins intake and view work
   with counters.
3. **Validation order.** Input bytes and structure, model, population, row file
   shape, then the kernel's own order (fact type, derived-ness, row, fragment).
   So a malformed row is refused (3) before an unsupported fragment (2) (G13).
4. **One walk.** The view is one closed selection function applied
   recursively to descent; there is no second payload builder.
5. **One home.** As WN-R6. The API count sentence lives in `python-api.md`
   only; `tour.md` and `cli.md` link to it instead of restating a number.
6. **Measure.** Golden payloads are exact bytes; no prose claims a payload shape.

## 5. Goal

```text
gnd why-not MODEL POPULATION --fact-type ID [--row REQUEST] [--reference-root DIR] [--raw]
```

```python
gnd.api.why_not(model_path, population_path, fact_type, *, row_path=None,
                reference_root=None) -> dict
```

Every §8 golden case gives its committed payload bytes and exit through both the
CLI and the API. The schema validates all of them. No population value appears
in any redacted payload.

## 6. Design

### 6.1 Service (`src/gnd/witness/service.py`)

`why_not(model_path, population_path, fact_type, *, row_path=None,
reference_root=None)`:

1. If `fact_type` is not a `str`, return the input-invalid envelope.
2. `row = None`. With a `row_path`, call `load_targets(row_path,
   limits=_intake_limits())`. It must hold exactly one target whose
   `fact_type` equals the argument. Otherwise return input-invalid. Zero
   targets already fail `load_targets`.
3. Call `_witness_inputs(...)` (the existing loader). Then re-enter the
   structural readers as `produce_witness` does: `intake(model.model_dump(mode=
   "json", exclude={"warnings"}), population_wire(candidate), raw_refs,
   limits=_intake_limits())`.
4. Call `explain(model, candidate, fact_type, row=row["tuple"] if row else
   None, references=context)`.
5. Map the outcome to the envelope (§6.3). `WhyNotInputError` and
   `WitnessInputError`, the loader's error classes, `YAMLError`, `OSError`,
   `TypeError` and `RecursionError` give input-invalid. `WhyNotWorkError` gives
   work-limit, carrying its counters.

`_intake_limits()` projects `DEFAULT_WHY_NOT_LIMITS` onto a `WitnessLimits`:
`bytes`, `container_depth`, `scalar_bytes` and `numeric_digits` are copied, and
`targets=1`. Every other field keeps the witness default. T3 pins the
projection field by field.

`why_not.__module__ = "gnd.api"`, as for `witness`.

### 6.2 API (`src/gnd/api.py`)

Re-export `why_not` from the service, as `witness` is. Append `"why_not"` as
the twelfth `__all__` name.

### 6.3 Envelope (raw, the API return value)

```json
{"schema_version": "gnd-why-not/1", "exit_code": 0,
 "status": "blocked", "reason": null,
 "fact_type": "claim", "mode": "row", "order": "declared",
 "unavailable": null, "clauses": [...], "work": {...}}
```

| `status` | `exit_code` | `reason` |
|---|---|---|
| `blocked`, `derived` | 0 | `null` |
| `unsupported` | 2 | `opaque-value`, `aggregate`, `rule-opaque` |
| `refused` | 3 | `input-invalid` |
| `unavailable` | 4 | production's reason (`term:…`) |
| `refused` | 4 | `work-limit` |

A refusal sets `fact_type`, `mode` and `order` to `null` and `clauses` to `[]`.
`unavailable` to `null`. `work` carries the counters for work-limit and is `{}`
for input-invalid. Clause records are the kernel's `ClauseExplanation.to_dict()`
unchanged, with descent nested as an envelope without `schema_version` and
`exit_code`.

### 6.4 Redacted view (`src/gnd/witness/view.py`)

`why_not_view(payload)` is a closed allow-list. It builds a new dict from named
keys and never copies a sub-object:

- top level: every envelope key; `unavailable` keeps `reason` and
  `source_relation`, and its `binding` becomes `"redacted"`;
- steps: `kind`, `index`, `fact_type`, `count`;
- blocker: `kind`, `index`, `fact_type`, `derivation`, `ground`,
  `asserted_not_read`, `reads`, `sample_count`. `roles` maps each role to
  `{"variable", "bound"}` or `{"constant": "redacted"}`. `samples` becomes
  `"redacted"`;
- `steps_after_blocker`, `descent_stopped`; `descent` is viewed recursively.

The CLI adds `"view": "redacted"` at the top level. `--raw` prints the API
payload unchanged with `"view": "raw"`. The schema allows both values of `view`
and its absence (the API).

### 6.5 CLI

- `src/gnd/witness/cli.py`: a `why-not` parser with `model`, `population`,
  `--fact-type` (required), `--row`, `--reference-root` and `--raw`. `run`
  dispatches to `api.why_not`, applies the view, and prints canonical sorted
  JSON. It returns `exit_code`. An argparse usage error stays argparse's
  (exit 2, as for every command).
- `src/gnd/commands/witness.py`: register `why-not` beside `witness`,
  `replay` and `witness-view`.

### 6.6 Pins (WN2-C3)

- API: the three `__all__` literals; a separate `why_not` signature
  assertion in `test_public_api.py`; a case in
  `test_public_reference_signatures.py`; the stale tuple at
  `test_public_runtime.py:52`, which becomes the twelve names (WN-D13).
- CLI: `EXPECTED_PARSERS` 56 → 57 in `test_rf1_cli_pins.py` and
  `test_rf5_commands.py:118`. The rf1 goldens are regenerated with
  `tools/rf1_pins.py capture` for each Python version the pins carry, then
  `goldens.sha256`. Add an rf5-handlers case and answer.
- `VENDORED_SCHEMAS` gains `gnd/why-not.schema.json`.
- `witness.cli` keeps importing `gnd.witness.service`, not `gnd.api`.

### 6.7 Documentation

- `docs/reference/why-not.md`: what it answers; the command and API; the
  normative definition of a step and the blocking step (moved from WN1 spec
  §6.3); descent; the semiderived and `covers` notes; exit bands; the redacted
  and raw views; limits. Add a `zensical.toml` Reference nav entry.
- `cli.md`: a table row and an exit sentence.
- `python-api.md`: a `why_not` section with a runnable `gnd-run` block over the
  dispatch example (`seed.pop.json`, an unreachable pair). The function list
  sentence gains `why_not` and becomes the one home of the count.
- `tour.md` and `cli.md` drop "seven-function" and link to it.
- `capabilities.md`: a row.
- `docs/release-notes.md`: an entry naming the surface.

## 7. Decisions

| ID | Question | Proposal (delegated ruling at the gate) |
|---|---|---|
| WN2-D1 | Refusal status spelling | `refused` with the reason distinguishing 3 from 4 |
| WN2-D2 | How a view is marked | `view: redacted\|raw` on CLI output only |
| WN2-D3 | Row file format | the witness request (`version` 1, `targets` with one `{fact_type, tuple}`) |

## 8. Tests

The corpus lives at `tests/fixtures/why_not/`, with `cases.json` (id, argv,
expected exit) and `goldens/<id>.json` (exact CLI stdout). `tests/test_public_why_not.py`
runs it.

| ID | Case | Expected |
|---|---|---|
| G1 | rule mode, second atom empty | 0 `blocked`, redacted and `--raw` goldens |
| G2 | row mode, blocker on a derived predicate, descent one level | 0 `blocked`, nested descent, both views |
| G3 | derived row | 0 `derived` |
| G4 | string-rule target | 2 `rule-opaque` |
| G5 | aggregate target | 2 `aggregate` |
| G6 | opaque value upstream | 2 `opaque-value` |
| G7 | computed head unavailable | 4 `unavailable`, `binding` redacted in the default view |
| G8 | `pre_joins` exceeded by a product inside a derived body predicate | 4 `work-limit` with counters |
| G9 | a model with a declared reference population; the blocker reads a reference relation | 0 `blocked` |
| G10 | unknown fact type; non-derived fact type | 3 |
| G11 | row file: zero targets; two targets; a target for another fact type; a primitive mismatch | 3 |
| G12 | hostile inputs: population with NaN; nesting over 64; a 200-digit integer; a model over 10 MiB | 3 |
| G13 | a malformed row for an aggregate target | 3, not 2 |

- **T1** every case through the CLI equals its golden byte for byte. Through
  the API, the payload equals the `--raw` golden without `view`.
- **T2** `why-not.schema.json` validates every golden and every API payload.
- **T3** the `_intake_limits()` projection, field by field.
- **T4** leak test. For each redacted golden, no scalar value in the
  population, the reference population or the row file appears in the payload
  text or in any refusal text. Fixtures use values that cannot collide with
  identifiers (`val-` prefixes, numbers above 1000).
- **T5** pins (§6.6) pass.
- **T6** parity: `test_public_v71_witness_corpus.py` and the check contract
  files of the WN1 gate pass unchanged.
- **T7** docs: `test_documentation_tutorials.py` runs the `gnd-run` block. The
  `cli.md` route probe sees the row.
- **T8** counter time bounds. Intake of a 1,000-target row file stops at the
  first target over the ceiling (`targets=1`), counted by the loader's target
  count rather than wall time. View rendering visits each clause and step once:
  a counting wrapper over a 50-clause payload gives exactly 50 clause visits.

Focused gate (plan §9): the WN1 gate, plus `tests/test_public_why_not.py
tests/test_public_api.py tests/test_v61_phase2_api.py
tests/test_public_reference_signatures.py tests/test_rf1_cli_pins.py
tests/test_rf5_commands.py tests/test_rf5_handler_pins.py
tests/test_documentation_tutorials.py tests/test_public_acceptance_runner.py`.
`test_public_built_inventory.py` and `test_public_runtime.py` are distribution
lanes and run only on owner selection (`slow_gate`), so their pin edits stay
unexecuted here.

## 9. Out of scope

The two-gap example and how-to (WN3), skill routes (WN3-C4), a `check`
report field, and any change to the kernel's semantics.

## 10. Size

About 250 lines of service, view and CLI code, a schema of about 200 lines,
13 golden cases, and docs.

## 11. Approval instrument

Corpus-first (WN-D10): the §8 corpus is committed red before WN2 code.
Delegated approval (auto=true) records the gate. One local reviewer reads the
phase diff (WN-D8).

## WN2 gate -- delegated approval (auto=true), 2026-10-30

- **Authority:** the owner's `/process-milestone derivation-why-not auto`
  request in this session. This is a delegated approval under that request, not
  the owner's own reading of the spec.
- **Bytes approved:** spec r1 above this section, SHA-256
  `8665b031764ca97960be2d76b9f6bc8eef02927a409f74eaa5eba0a5ca829e27`.
- **Base:** WN1 commit `26e36c8` on `claude/milestone-issue-66-72e872`.
- **Decisions:** WN2-D1, D2 and D3 as proposed in §7.
- **Instrument:** corpus-first (WN-D10); one local reviewer over the phase
  diff (WN-D8). Budget: no paid calls; the distribution lanes stay
  owner-selected.

Implementability sweep, run before this ruling against the WN1 kernel and the
corpus inputs written by `evidence/WN2/build_inputs.py`:

- **S1.** An atom blocker carries no `count`; only non-atom blockers copy
  their step. The schema requires `count` on steps only.
- **S2.** `unsupported` results keep `fact_type`, `mode` and `order` from the
  kernel. Only `refused` sets them to `null` (§6.3 stands).
- **S3.** `_witness_inputs` reads with the witness default limits, whose byte,
  depth, scalar and digit ceilings equal the why-not defaults. The projection
  therefore changes only `targets` (to 1) for the row file and the re-run
  intake.
- **S4.** G9 uses the packaged dispatch example. `dispatch_leg` is owned by
  its reference population, and the row (WH-A, DEST-E) descends three levels
  through `dispatch_reachable`. This discharges WN1-Q3.
- **S5.** G8 breaches `pre_joins` at 200,001 (500 x 500 inside `pair`).
- **S6.** Python 3.11, 3.13 and 3.14 are installed for `tools/rf1_pins.py
  capture`.
- **S7.** The goldens' clause bodies and `work` counters come from the WN1
  kernel, which was reviewed in WN1. The envelope and the redaction are written
  out in `evidence/WN2/build_goldens.py` from §6.3 and §6.4 alone, before any
  service, view or CLI code exists.
