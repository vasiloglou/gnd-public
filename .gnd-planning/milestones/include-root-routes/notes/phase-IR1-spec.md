# Phase IR1 spec · `gnd judgments check` on an include root

## 1. Status

Draft r1, 2026-11-21, awaiting its delegated spec gate (`auto=true`). Not
implementable until the plan gate (`001-plan-gate.md`) and this spec's gate
are recorded.

## 2. Provenance

- Plan: `notes/include-root-routes-plan.md` r2 (§1 rows H1, H3, H6, H8, H11;
  §2 IR1; §4 IR1-C1 to IR1-C7; §10 D4, D6). No review opinion covers these
  bytes; the plan's panel-light review reads the plan, not this spec.
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
| plan IR1-C7, R0.6 | a model without includes gives today's report | §6 branch; §8 T11 |
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
   T9 times the judgments route over a root whose include holds 1,000 object
   types and 1,000 fact types and requires it under 20 s on the test
   machine.
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
       model = load_model_bytes_composed(mr, source=model_path, root=root)
       model_root = root
   else:
       model = load_model_bytes(mr, source=model_path)
       model_root = None
   ```
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
  source="model.orm.yaml", root=model_root)`; otherwise `load_model_bytes`
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
| IR1-D1 | Keep `test_R4_judgments` | (a) keep: `evaluate_judgments` without `model_root` still refuses, pinned; (b) change to accept: a direct caller without a root would need another way to compose. Same exit for the CLI either way | (a) |
| IR1-D2 | Include check order in `api.judgments` | (a) at the model step, after policy and receipts (today's order for other models); (b) before policy, as `guard_path` did. Both exit 3; they differ in `reason` for an input that is wrong twice | (a), pinned by T8 |
| IR1-D3 | `reason` for include refusals (plan D6) | (a) `binding` for all; (b) `unsupported` for `forbidden-section`. Same exit 3 | (a) |
| IR1-D4 | Where the composed route applies | only when the root declares includes; a root without includes keeps `load_model_bytes` so reference binding is unchanged (R0.6) | as stated |

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
| T6 | parametrized: path `../escape.orm.json`, absent file, `includes` not a list, hash mismatch, nested include | each outcome 3 and the report validates against `judgment.schema.json` `$defs.report` with `report.schema.json` registered |
| T7 | `evaluate_judgments(..., model_root=None)` on a root's bytes; same call with `model_root` set | `include:unsupported-route`; then a decision with `admission` true |
| T8 | malformed policy (`{}`) with a stale include | outcome 3, `reason` `shape` |
| T9 | root whose include holds 1,000 object types and 1,000 fact types, empty targets | outcome 0 or 1, under 20 s |
| T10 | `tests/test_mc1_guards.py::test_R5_judgments_api` rewritten: `write_case` root with a stale pin and readable policy and receipts | outcome 3, `message` `include:hash-mismatch` (no longer `include:unsupported-route`) |
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

This prose, under the milestone's `auto=true` delegation.
