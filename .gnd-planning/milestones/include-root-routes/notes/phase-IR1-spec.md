# Phase IR1 spec · `gnd judgments check` on an include root

## 1. Status

**Delegated approval (auto=true), 2026-11-21**, over this spec r3 and the
corpus `tests/test_ir1_judgments_includes.py` (sha256 `4db9c9d5186c7d2414545628e544d479d86b80e2da24ecfb5bb52f1c82aa819e`) with
`tests/test_mc1_guards.py` (sha256 `f718bc402971e2b0dec74f5a6ff21571c257f619c1e46e8e4dbd7cc2b9240ab6`). Authorization: the owner's
`/process-milestone include-root-routes auto` in this session, within the
plan approved in `001-plan-gate.md`. Instrument: the corpus (§11). Budget:
one Codex review round over the diff (plan D7). This is the driving agent's
ruling, not the owner's reading. Implementable from this gate's commit.
Prior status, kept: "Draft r3, 2026-11-21, awaiting its delegated spec gate
(`auto=true`). Not implementable until the plan gate (`001-plan-gate.md`)
and this spec's gate are recorded."

## 2. Provenance

- Plan: `notes/include-root-routes-plan.md` r3 (§1 rows H1, H3, H6, H8, H11;
  §2 IR1; §4 IR1-C1 to IR1-C8; §10 D4, D6). No review opinion covers these
  bytes; the plan's panel-light reviews read the plan (r2, then r3), with
  this spec offered as context only.
- r2 of this spec, 2026-11-21 `(p1)`: follows plan r3's repair of the
  composed route (references bound at `--reference-root`, IR1-C8).
- r3, 2026-11-21 `(p2)`: follows plan r4. Round 2 of the plan review read
  this spec's r1 as context (commit `c1d7219b`) and its agreed concern, that
  r1 bound references during composition, is the one r2 had already
  repaired. r3 adds IR1-C9 (T13).
- Code read at `260c4337` on 2026-11-21.
- Feasibility measurement, 2026-11-21 (scratch, not committed): with the two
  include guards patched out and `load_model_bytes` patched to the composed
  loader, `api.judgments` over the interop fixture gave
  `checking.orm.json` outcome 0, admission true; `extraction.orm.json` and
  its flat model, on a population relabelled to the extraction `model_id`,
  outcome 0, admission true on both. On the population built for the
  checking model the extraction root gives `population:model-id-mismatch`,
  so IR1-C2 relabels the population's `model_id` and `model`.

## 3. Obligations

| Source | Obligation | Discharged in |
|---|---|---|
| plan IR1-C1 | temporal root with two includes judges, outcome 0, `error` null | §6 api; §8 T1 |
| plan IR1-C2, R0.4 | direct and flat judgments agree | §8 T2 |
| plan IR1-C3 | include edited without re-pin → `include:hash-mismatch`; edited and re-pinned → "stale judgment subject" | §6; §8 T3, T4 |
| plan IR1-C4, R0.2 | nested include → `include:forbidden-section` | §8 T5 |
| plan IR1-C5, H6, D6 | include refusals validate against `judgment.schema.json` | §6 mapping; §8 T6 |
| plan IR1-C6, H8 | `test_R5_judgments_api` changes; `test_R4_judgments`, `test_R10_session_judgments` stay | §6; §8 T7, T10 |
| plan IR1-C7, R0.6 | a model without includes gives today's report, `model_digest` included | §6 branch; §8 T11 |
| plan IR1-C9 `(p2)` | an orphan `fact_type_constraints` document refuses `include:declaration` | §6 branch predicate `declares_includes`; §8 T13 |
| plan IR1-C8 `(p1)` | an include root with its reference file only under `--reference-root` judges, exit 0 | §6 `bind_references=False`; §8 T12 |
| plan R0.3 | one composition, the loader `gnd check` uses | §6 |
| plan D4 | receipts bind the root's bytes; pins bind includes | §6; §8 T4 |
| plan §5 | includes route list in representation-format.md; `docs/reference/cli.md` row; release note | §6 docs |
| H11 | assertion-admission example keeps refusing include roots | §9 boundary |

## 4. Standing rules bound to this phase

1. **Totality.** The new input surface is the include declarations of a root
   reaching `api.judgments`. Their parser is the existing `compose`
   (`model/_includes.py:181`); this phase adds no parser. Hostile
   declarations through the judgments route — a path escaping the root, an
   absent file, a non-list `includes`, a nested include — each give outcome
   3 with a schema-valid report (T6). No traceback leaves `api.judgments`.
2. **Cap bounds the algorithm.** The added work is a second composition in
   `evaluate_judgments`' raw-subject check. Composition is already capped
   (10 MiB per file, 32 MiB in total, `compose`); work is linear in bytes.
   T9 times the composition layer, twice as one run composes it, over the
   checking root after 1,000 value object types are added to an include
   (re-pinned), and requires under 5 s. **Corrected (i1), 2026-11-21**, after
   a reproduced implementation finding (below). Prior wording, kept: "T9 times
   the judgments route over the checking root after 1,000 value object types
   are added to an include (re-pinned) and requires it under 20 s on the test
   machine."
3. **Validation order.** Unchanged for models without includes: policy,
   receipts, model, population (`api.py:1158-1164`). For an include root the
   include checks now run at the model step, after the policy and receipts
   are read, where today `guard_path` refused before them. T8 pins it: a
   malformed policy with a stale include reports `reason: "shape"`.
   In `evaluate_judgments` the `model_root`-less include refusal stays the
   first statement (T7).
4. **One walk.** All include refusals map to one `error` shape by prefix
   (`rule_id.startswith("include:")`), not per code. T6 covers five codes.
5. **One home.** The list of routes that resolve an include root lives in
   representation-format.md's includes section; `docs/reference/cli.md`
   cites it. Created here (plan §5).
6. **Measurement.** The feasibility measurement in §2 settled that the
   composed loader admits both roots before any code was written.

## 5. Goal

`gnd judgments check` over the #217 temporal include root exits 0 with a
valid policy and receipts; each include refusal exits 3 with a report that
validates against `judgment.schema.json`; a model without includes produces
the same bytes as at `260c4337`.

## 6. Design

### `src/gnd/api.py` · `judgments` (about 15 lines changed)

```python
def judgments(model_path, population_path, policy_path, receipts_path, *,
              trusted_root, reference_root=None, unredacted=False): ...
```

Signature unchanged. Inside the `try`:

1. Delete `guard_path(model_path, "api.judgments")` and the
   `guard_bytes(mr, ..., route='api:1123')` call.
2. Read policy, receipts, model bytes `mr` and population bytes `pr` in
   today's order.
3. ```python
   from gnd.model._includes import declares_includes
   from gnd.model._validation import parse_model_document
   root = Path(model_path).absolute().parent
   if declares_includes(parse_model_document(mr, source=model_path)):
       model = load_model_bytes_composed(mr, source=model_path, root=root,
                                         bind_references=False)
       model_root = root
   else:
       model = load_model_bytes(mr, source=model_path)
       model_root = None
   ```
   References are then bound by the existing
   `bind_declared_references(model, root=reference_root or Path(model_path).parent)`
   (`api.py:1165`), for both branches `(p1)`.
   `parse_model_document` raises `ModelLoadError` on malformed bytes, which
   the existing `except` maps to `binding`, as `load_model_bytes` does today.
4. Pass `model_root=model_root` to `evaluate_judgments`.
5. The `except ModelValidationError` branch becomes:
   ```python
   code = next((i.rule_id for i in error.issues if i.rule_id.startswith("include:")), None)
   result.update(error={"reason": "binding",
                        "message": code or "invalid bound judgment input"})
   ```
   `reason` is always a member of the schema enum; the include code moves to
   `message` only (D6). Exit stays 3.

`ReferenceInputError` and `ReferenceHashMismatch` from the composed loader
are `ValueError` subclasses and reach the existing `binding` branch.

### `src/gnd/model/__init__.py` · `load_model_bytes_composed` (about 6 lines) `(p1)`

```python
def load_model_bytes_composed(data: bytes, *, source: str | Path, root: str | Path,
                              bind_references: bool = True) -> Model: ...
```

`bind_references=False` skips the `_bind_at` step of `_composed_view`
(`model/__init__.py:371-377`); composition, include authentication and
validation are unchanged. The default keeps every existing caller's
behaviour. The one home of this keyword's meaning is the function's
docstring; representation-format.md's sentence on the rooted bytes entry
point (near line 1892) cites it.

### `src/gnd/judgments.py` · `evaluate_judgments` (about 10 lines changed)

```python
def evaluate_judgments(policy, receipts, *, model, candidate, mechanical_report,
                       model_bytes, population_bytes, trusted_root,
                       references=None, model_root=None): ...
```

- First statement: `if model_root is None: guard_bytes(model_bytes,
  source="model.orm.yaml", route="judgments")` — the refusal stays for every
  caller that names no root, including `exp/session_judgments.py:96`.
- Raw-subject check (`:507`): when `model_root` is not `None` and the bytes
  declare includes, `loaded = load_model_bytes_composed(model_bytes,
  source="model.orm.yaml", root=model_root, bind_references=False)`; otherwise `load_model_bytes`
  as today. The `model_dump()` comparison is unchanged.
- `subject.model_sha256` stays `sha256_hex(model_bytes)` (`:569`): the root's
  bytes (D4).

### Documentation

- `src/gnd/skills/gnd-orm-core/references/representation-format.md`,
  includes section after the `load_model(path)` paragraph: a list headed
  "CLI routes that resolve an include root", with `gnd check`, `gnd verify`,
  `gnd compose`, `gnd extract` (non-temporal) and, new, `gnd judgments
  check`: receipts bind the root's sha256, which commits to each include's
  pin. Each existing row is confirmed by its current test before it is
  written; a route that cannot be confirmed is left out.
- `docs/reference/cli.md:90`: the row adds "an include root is resolved as
  `gnd check` resolves it" and links the list.
- `docs/release-notes.md`, unreleased: one entry.

## 7. Decisions

| ID | Question | Readings and cost | Proposed |
|---|---|---|---|
| IR1-D1 | Keep `test_R4_judgments` | (a) keep: `evaluate_judgments` without `model_root` still refuses, pinned; (b) change to accept: a direct caller without a root would need another way to compose. Same exit for the CLI either way | (a) → **ruled (a), delegated 2026-11-21** |
| IR1-D2 | Include check order in `api.judgments` | (a) at the model step, after policy and receipts (today's order for other models); (b) before policy, as `guard_path` did. Both exit 3; they differ in `reason` for an input that is wrong twice | (a), pinned by T8 → **ruled (a), delegated 2026-11-21** |
| IR1-D3 | `reason` for include refusals (plan D6) | (a) `binding` for all; (b) `unsupported` for `forbidden-section`. Same exit 3 | (a) → **ruled (a), delegated 2026-11-21** |
| IR1-D4 | Where the composed route applies | only when the root declares includes; a root without includes keeps `load_model_bytes` so reference binding is unchanged (R0.6) | as stated → **ruled as stated, delegated 2026-11-21** |
| IR1-D5 `(p1)` | How references of an include root are bound | (a) compose without binding, then `bind_declared_references` at `--reference-root` or the model's folder, as for other models; (b) let the composed loader bind at the model's folder, which ignores `--reference-root`. (b) exits 3 where (a) exits 0 for a separate reference root | (a) → **ruled (a), delegated 2026-11-21** |

## 8. Tests

New file `tests/test_ir1_judgments_includes.py`. A module-scoped fixture
builds the interop example once with
`gnd.examples.literature.interop.build(out)`; each test copies it into
`tmp_path`. A helper writes a consumer-pinned policy with two judges and two
approving receipts bound to a named model file, as the §2 measurement did.

| # | Case | Expected |
|---|---|---|
| T1 | `run_main(["judgments", "check", "checking.orm.json", "composed.population.json", ...])` | exit 0, `outcome` 0, `error` null, `judgment_policy.admission` true |
| T2 | extraction root directly and `extraction.flat.orm.json` (from `flatten_model`), population relabelled, receipts bound to each | both outcome 0; `targets` equal after removing `receipt_sha256`; `admission` equal |
| T3 | edit `vocabulary/chronology.orm.json` (append a space), pin unchanged | outcome 3, `reason` `binding`, `message` `include:hash-mismatch` |
| T4 | edit the same include validly and re-pin it in the root; old receipts | outcome 3, `message` "stale judgment subject" |
| T5 | add an `includes` key to an included file and re-pin | outcome 3, `message` `include:forbidden-section` |
| T6 | parametrized: path `../escape.orm.json`, absent file, `includes` not a list, hash mismatch, nested include; and a negative control | each outcome 3 with the include code in `message`, and the report validates against `judgment.schema.json` with `report.schema.json` registered; the control (0.4.0's refusal shape) fails validation |
| T7 | `evaluate_judgments(..., model_root=None)` on a root's bytes; the same call with `model_root` set and no policy | `include:unsupported-route`; then `JudgmentInputError` (the include refusal is skipped and the policy check refuses) |
| T8 | malformed policy (`{}`) with a stale include | outcome 3, `reason` `shape` |
| T9 | (i1) `bytes_declare_includes` and `load_model_bytes_composed(..., bind_references=False)`, twice, over the checking root with 1,000 extra value object types in `chronology`, re-pinned | composes more than 1,000 object types in under 5 s. Prior row, kept: "the checking root with 1,000 extra value object types in `chronology`, re-pinned and re-bound · outcome 0 or 1, under 20 s" |
| T10 | `tests/test_mc1_guards.py::test_R5_judgments_api` rewritten: `write_case` root with a stale pin and readable policy and receipts | outcome 3, `message` `include:hash-mismatch` (no longer `include:unsupported-route`) |
| T13 `(p2)` | the checking root with `includes` removed and an orphan `fact_type_constraints` added | outcome 3, `message` `include:declaration` |
| T12 `(p1)` | the checking root with `reference/catalog.json` moved to a separate folder passed as `--reference-root` | exit 0, `admission` true |
| T11 | control: `tests/test_public_v71_full_judgments.py` and `tests/test_public_v71_judgment_successor_guards.py` unchanged | exit 0 |

Unchanged pins that must stay green: `test_R4_judgments`,
`test_R10_session_judgments`, `test_R21_composition_verify`.

Branch table: composed branch (T1, T2, T4), include-free branch (T11),
`model_root` absent (T7a), present (T7b), each include refusal family (T3,
T5, T6), order (T8), mapping (T6 schema). Each has a case that fails if the
branch is wrong.

Focused gate (plan §9) and the structure and inventory guards, plus
`uv run ruff check`.

## 9. Out of scope

`gnd exp` session judgments; the assertion-admission example (H11: it copies
the model alone and will now refuse an include root with
`include:unreadable` instead of `include:unsupported-route`); a judgments
schema version change; any include rule.

## 10. Size

Estimate: source 30 lines, tests 220 lines, docs 15 lines.

## 11. Approval instrument

Corpus-first: IR1 changes an exit-code and error-shape contract, for which
`review-convergence.md` sets corpus-first as the default. The corpus is
`tests/test_ir1_judgments_includes.py` (T1–T9, T12, T13) and the rewritten
`tests/test_mc1_guards.py::test_R5_judgments_api` (T10), authored before any
implementation and committed red: with only these test bytes added to
`c1d7219b`, 17 cases fail and the T6 negative control passes (measured
2026-11-21; 15 before T12 `(p1)` and 16 before T13 `(p2)` were added). Each test's assertion is its expected answer; there is no
separate answer key, because the cases are expected exits and error objects,
not a blind-reading corpus. The gate is a delegated approval under
`auto=true` over this spec and those test bytes.

## Implementation findings, recorded as they were found

**i1, 2026-11-21: the checker is superlinear in the number of object types;
T9 as first written measured it, not IR1's layer.** With the implementation
in place, the route-level T9 ran 580.9 s (the bound was 20 s). Measured in
scratch on the interop fixture with N extra value object types in one
include:

| N | `load_model` | `gnd check` on the include root | `gnd check` on its flat model |
|---|---|---|---|
| 100 | 0.05 s | 0.78 s | — |
| 300 | 0.12 s | 7.77 s | 7.70 s |
| 1,000 | 0.20 s | 265.74 s | — |

Composition stays linear and fast. `gnd check` is slow by the same amount
with or without includes, so the cost is in existing code that IR1 does not
change. A profile of the 300-type flat model puts 35.3 of 36.0 s under
`universe._denoting_types` (610 calls) → `resolve_reference_value_type`
(184,830 calls) → `model_queries._supertype_parents` (184,866 calls, 14.3 s
own time): one supertype walk per object type, inside a loop over object
types, inside a loop over roles. `judgments check` runs the checker twice
(redacted and unredacted reports), hence about 2 × 266 s.

Disposition: T9 is corrected to time the layer IR1 adds (rule 2 as
written: "a time-bound test over the layer it adds"). The checker scaling is
an open question for the milestone close, carried to a separate fix outside
this milestone: it affects `gnd check` on any model with many object types,
not only include roots.

**i2, 2026-11-21: the include-free branch needs the same parse-tolerance as
`guard_bytes`.** `api.judgments` must not change the refusal of malformed
include-free bytes, so the branch predicate reports unparseable bytes as
declaring nothing and lets `load_model_bytes` refuse them as before. That
logic already lived inside `guard_bytes`; it moved to one function,
`bytes_declare_includes` (`model/_includes.py`), which `guard_bytes`, the
API and `evaluate_judgments` now share.

## Phase review r1 (Codex, read-only), 2026-11-21

`notes/reviews/phase-IR1-r1/`: one reviewer is one reviewer. One finding,
F1 (medium): IR1-C7's byte identity rested on suites that compare selected
observations, not report bytes; the reviewer reproduced a `schema_version`
change that those suites would not catch. Reproduced; class hardening, in
this phase's own deliverable; fixed by T11: a report golden
(`tests/fixtures/ir1/include-free-judgments-report.json`) produced by the
base code at `1e419a88` and equal to the head output byte for byte, with a
negative control that changes one field and must differ. The golden is a
preservation pin, so it passes on the pre-fix code by design; its
falsifiability is the negative control. The reviewer also confirmed by
probe every claim in the brief and measured two compositions at 1,000 types
in 0.283 s; it did not run the suites (read-only).

## Size, measured

Source: 69 lines added, 21 removed across five files (estimate 30). Tests:
`tests/test_ir1_judgments_includes.py` 368 lines plus 19 changed in
`tests/test_mc1_guards.py` (estimate 220). Docs: 25 lines (estimate 15).
About 2.5 times the source estimate: the shared predicate (i2), the
`bind_references` keyword and the error mapping were each larger than the
one-line sketches in §6.
