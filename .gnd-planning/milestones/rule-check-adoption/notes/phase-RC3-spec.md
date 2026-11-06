# Phase RC3: baseline (new vs standing violations)

## 1. Status

**Owner-decided (2026-11-06); approval pending on the corpus (§11).** The
owner ruled the step-2 asks over r1 (sha256 `30bd7157…bc13c`, commit
0e74261e), answering "How do you rule on RC3's decisions D1-D7?" with
"Approve all as proposed" (o, 2026-11-06). D1 is corpus-first, so no
implementation file is created or edited until the owner approves the
corpus. `auto=false`. Prior status (r1): "Draft, awaiting the owner gate
(process-phase step 2)."

## 2. Provenance

- Plan: [rule-check-adoption-plan.md](rule-check-adoption-plan.md) r6,
  sha256 `6f0056b31b8df7eae5c85d6d32eb09395a8240bc137a7300de85bab71639f138`,
  approved with every §10 proposal ([005-plan.md](../005-plan.md)). So
  RC-D4 (positional key for id-less constraints), RC-D5 (standing-only exits
  0, `acceptance_ready: true`, outcome `accepted`), RC-D6 (alethic unchecked
  in either run exits 4), RC-D9 ("Proceed and warn"), RC-D11 (refuse models
  with structured derivations) and RC-D13 (deontic unchecked does not block,
  counted in `undecided`) are ruled.
- RC1 fixed the version-15 shape whole: `novelty`, `row_novelty` per verdict
  and the top-level `baseline` block (`baseline_v15`: `population`,
  `population_sha256`, `new`, `standing`, `resolved`, `positional_keyed`,
  `undecided`). RC3 fills values and adds no key.
- RC2 made acyclic rows one per in-loop edge, so they are stable keys.
- Records: [006-phase-RC1.md](../006-phase-RC1.md),
  [007-phase-RC2.md](../007-phase-RC2.md). Base: main at `eac81cf8`.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan §4 RC3-C1 | in both runs → `standing`; only head → `new`; only base → counted `resolved` | corpus `mixed`, T1 |
| RC3-C2 | standing-only exits 0, `acceptance_ready: true`, outcome per RC-D5, counts show the standing rows | corpus `standing-only` |
| RC3-C3a | temporal, redaction-policy or reference-population model with `--baseline` → exit 3 `check:rule-ids-unsupported` before either population loads | corpus `refuse-temporal` (absent populations) |
| RC3-C3b | structured-derivation model → exit 3 `check:baseline-unsupported` before either population loads; same model with `--rule-ids` alone accepted | corpus `refuse-derivation`; RC1's `derivation-plain` still green |
| RC3-C3 | base ill-formed exits 3 naming the base; alethic unchecked in either run never yields "no new violations" (exit 4 unless a new alethic fail gives 1); deontic `opaque-value` unchecked with no rows leaves the band and makes `undecided` 1 | corpus `bad-base`, `base-unchecked`, T5 |
| RC3-C4a | within one model revision the key survives inserting and reordering facts in either population | T6 |
| RC3-C4b | across revisions a declared-id key survives inserting a constraint above it; a positional key moves; RC-D9 warns | T7, corpus `positional-warning` |
| RC3-C5 | validation order pinned; comparison of 2,000 rows a side under 0.5 s | T8 (source order), T9 |
| RC3-C6 | row-less alethic failure new in head → exit 1, `novelty: new`, `row_novelty: []`; one standing + one new row → `novelty: new`; only standing rows → `standing`, not exit 1 | corpus `rowless-new`, `mixed`, `standing-only` |
| RC3 harvest item | every snapshot family's v7 offending rows are values only (rule 8) | §6 survey; T10 |
| §2.3 vacuous (F5) | judged on head; base vacuous contributes no rows; base fail + head vacuous → base rows resolved, band 2 | corpus `head-vacuous` |
| §2.3 baseline block | names the base population and its digest; counts new, standing, resolved, positional-keyed rows, and undecided obligations (per verdict, either run, any modality) | every baseline case |
| §0 rule 1 | the base is read by the existing population loader with its caps, never a new reader | M3 |
| §0 rule 2 | comparison is a set difference over canonical keys, linear in rows | M2, T9 |
| §0 rule 3 | order: args (64), model load (3), `check:rule-ids-unsupported` (3), `check:baseline-unsupported` (3), head load (3), base load (3, naming base), evaluation | M4, T8 |
| §0 rule 4 | the key is one function over every family's offending row | M2 |
| §0 rule 7 | no existing variant moves; full suite vs merge-base record | V3 |
| §6 "Band rule duplicated" | RC3 extends `band()`, the one implementation | M1 |
| RC2 record, open question | exact-term derived rings under version 15 | moot under `--baseline` (structured-derivation models are refused, RC-D11); recorded |
| RC1/RC2 records | guard registries record changed bodies; component index updated with the code | V4, V6 |

## 4. Standing rules bound to this phase

- **Totality (1).** The base population is loaded by `load_population`
  through `_resolve_population`, with the same caps as the head.
- **Input cap (2).** Keys are hashed into sets; comparison is linear.
- **Validation order (3).** Pinned by a source-order test over
  `_run_check_raw` (T8), as RC1 pinned the first four steps.
- **One walk / one key (4).** `baseline_key(address, row)` is the one key
  function; verdict novelty, row novelty and the counts all read it.
- **One band (5, §6).** `band()` gains an optional baseline argument; no
  caller computes a band of its own.
- **Frozen variants (7).** Everything is behind `--baseline`, which implies
  `--rule-ids`; without it no byte moves.

## 5. Goal

`gnd check MODEL HEAD --baseline BASE` judges both populations under MODEL,
marks each failing verdict and each offending row `new` or `standing`,
decides the exit band from new violations only, counts what was resolved,
and refuses to claim "no new violations" when either run left an alethic
obligation undecided.

## 6. Design

**Reuse table** (searched 2026-11-06 at `eac81cf8`; `components_index.py
search` for `compare two check reports baseline`, `diff violations`,
`canonical json`, `exit band`).

| Capability | Found | Decision |
|---|---|---|
| comparing two populations' verdicts | nothing (only `model.diff`, two models) | **new** `gnd.checker` sibling module per plan §3 (M2) |
| canonical JSON of a row | `artifacts.canonical_json_bytes` (sorted keys, compact) | **reuse** for the key |
| exit band | `band()` (`checker/_reports.py:146`) | **adapt** (M1) |
| loading the base | `_resolve_population` / `load_population` | **reuse** |
| refusal rule ids at exit 3 | RC1's `_rule_ids_refusal` route | **reuse**; add `check:baseline-unsupported` |
| structured-derivation test | `documents.structured_derivation_ids` | **reuse** |
| file digest | `hashlib.sha256` over the base bytes the loader read | **reuse** |
| version-15 fields | RC1 `_rule_ids_verdict`, `baseline: null` | **adapt**: fill from the comparison |

**Family survey (harvest item, rule 8).** `constraint_families.FAMILIES`
projects offending rows through two hooks only: `_flat_projected_witness`
(cardinality, mandatory, mandatory-disjunctive, value: one scalar per row)
and `_row_projected_witness` (the other twelve: a list of scalars, or for
`guarded` a map from variable name to scalar). Every value passes through the
origin projection, so a row holds public values, never a `{fact_type,
index}` reference (that shape exists only in the version-10 branch). No
survey result contradicts the plan; rule 8 does not fire. T10 pins it.

**M1. `band(report, baseline=None)`, `checker/_reports.py`, ~25 lines.**
`baseline` is a `BaselineBand(new_alethic_fail: bool, undecided_alethic:
bool)`. With it, the band is 1 if `new_alethic_fail`; else 4 if
`undecided_alethic` (an alethic verdict unchecked in head or in base); else
2 if head has a vacuous verdict; else 0. Without it, unchanged byte for byte.
The precedence 1 > 4 > 2 > 0 is the existing one.

**M2. `src/gnd/checker/_baseline.py` (new, layer `checking`), ~110 lines.**

```python
def baseline_key(address: str, row: object | None) -> tuple[str, bytes | None]
def compare(head: CheckReport, base: CheckReport,
            addresses: Mapping[str, tuple[str, Addressing]]) -> Comparison
```

- A row's key is `(address, canonical_json_bytes(row))`; a failing or
  warning verdict with no rows contributes one key `(address, None)`.
- Keys are collected from `fail` and `warning` verdicts of each report.
  Head keys in base are `standing`, otherwise `new`; base keys not in head
  are `resolved`. A head-vacuous verdict's base keys are resolved (F5).
- `Comparison` carries, per positional ref: `row_novelty` (aligned with the
  head verdict's rows; `[]` for a row-less verdict), `novelty` (`new` if any
  row is new or the row-less key is new, else `standing`; null for
  pass/vacuous/unchecked), the five counts, and the `BaselineBand` inputs.
- `positional_keyed` counts head keys (new or standing) whose address is
  positional; `undecided` counts verdicts unchecked in head or base, by
  positional ref, either modality (S4).

**M3. Service, `checking_service._run_check_raw(..., baseline=...)`, ~45
lines.** After the RC1 refusal: refuse `check:baseline-unsupported` when
`structured_derivation_ids(model)` (D-order step 4); load head as today,
then the base with `name="baseline"`; a base load failure exits 3 with the
base's own issues, each path prefixed `baseline:` (D3). Check the base with
the same evaluator, compare, compute `band(head, baseline=…)`, and pass the
comparison to the payload builder.

**M4. Payload, ~25 lines in `payloads.py`.** Version 15 with a comparison:
each verdict's `novelty` and `row_novelty` from it; `baseline` = `{population,
population_sha256, new, standing, resolved, positional_keyed, undecided}`;
`exit_code`, `outcome` and `acceptance_ready` follow the baseline band
(RC-D5: exit 0 → `accepted`, `acceptance_ready: true`).

**M5. Assurance under `--baseline` (D5).** The certified assurance path
attests the plain decision for the plain band. Under `--baseline` the band is
a different claim, so the payload carries `AssuranceBlockV1(
semantic_decision_for_band(baseline band))` at level `none`, uncertified,
and `_certify_assurance` is not called.

**M6. CLI, `commands/checking.py`, ~25 lines.** `--baseline BASE` implies
`--rule-ids` and joins its conflict set (64). Text output (D6): each
non-pass verdict line gains its novelty (`[fail, new]`, `[fail,
standing]`), and a closing `BASELINE` block prints the base path, the five
counts and, when `positional_keyed > 0`, the RC-D9 warning:
`warning: N baseline keys use positional addresses; they move if a constraint is inserted above them.`

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first** (exit-code contract and serialized format) **Ruled (o, 2026-11-06): as proposed.** |
| D2 | Row-less failing verdict's key | `(address, None)`: one key per verdict, so RC3-C6 holds **Ruled (o, 2026-11-06): as proposed.** |
| D3 | How an ill-formed base is reported | exit 3, version 15, the base's own issues with paths prefixed `baseline:`; `population` stays the head path **Ruled (o, 2026-11-06): as proposed.** |
| D4 | Warning verdicts (deontic fail) | compared like failures (novelty shown, counted), but as today they never decide the band **Ruled (o, 2026-11-06): as proposed.** |
| D5 | Assurance under `--baseline` | uncertified block for the baseline band, level `none` (M5) **Ruled (o, 2026-11-06): as proposed.** |
| D6 | Text output | novelty on each non-pass line; a `BASELINE` block with the counts and the RC-D9 warning **Ruled (o, 2026-11-06): as proposed.** |
| D7 | Review over the spec bytes | none **Ruled (o, 2026-11-06): as proposed.** |

## 8. Tests and verification ledger

**Corpus** (`tests/fixtures/rc3-baseline/`, §11) plus direct tests in
`tests/test_rc3_baseline.py`:

| T | Case | Expected |
|---|---|---|
| T1 | `compare` on hand-built reports: in both / head only / base only | standing / new / resolved |
| T5 | base with an alethic unchecked verdict, head clean | exit 4; with a new alethic fail in head, exit 1 |
| T6 | head and base with facts reordered and extra unrelated facts inserted | same keys, same novelty |
| T7 | two model revisions: a constraint inserted above a declared-id rule and above a positional rule | declared key stable; positional key moves; warning printed |
| T8 | source order of `_run_check_raw` | the seven steps in rule 3's order |
| T9 | 2,000 failing rows a side | `compare` under 0.5 s |
| T10 | one failing case per family | every row JSON-serializes to scalars, lists or maps of scalars; no `fact_type`/`index` keys |
| T11 | `--baseline` with each conflicting arm | exit 64 before the model is read |
| T12 | `band()` without `baseline` | every existing band test unchanged (V4) |

**Verification-selection ledger.**

| # | Obligation | Disposition | Command or evidence | Invalidation |
|---|---|---|---|---|
| V1 | merge-base record | run before any source edit | focused list below at `eac81cf8`; full-suite base from the RC2 record (main c5fe86bb) unless main moved in tested code | a new base |
| V2 | plan §9 RC3 row | run | `uv run pytest -q tests/test_rc3_baseline.py tests/test_rc2_acyclic_extent.py tests/test_rc1_rule_ids.py tests/test_exp_bands.py --tb=short -p no:cacheprovider` | any RC3 edit |
| V3 | full suite vs base | run, sharded on beast-3 as in RC2 | failure set equal to the base's | any source edit after the run |
| V4 | impact closure | run | RC2's V4 list (guards, `test_rf6_packages`, `test_public_registry_runtime`) plus `tests/test_rf1_cli_pins.py tests/test_v6_phase6_report.py tests/test_public_branch_runtime.py tests/test_v6_phase2_registry.py` and every test file that calls `band(` | edits to those surfaces |
| V5 | lint | run | changed Python files clean | any Python edit |
| V6 | component index | run at record time | `components_index.py changed --base eac81cf8 --strict` | any edit |
| V7 | broad lanes | cadence: not run | milestone close if selected | owner request |

## 9. Out of scope for this phase

`--allow-vacuous` (RC4: here a head-vacuous run exits 2); comparing
derivation findings (RC-D11 refuses those models); baseline over batch,
transition, anchors, composition, admission, redaction, temporal or
reference models; a baseline given as a previous report instead of a
population.

## 10. Size

Plan estimate: about 320 source and 550 test lines; rule 8 pauses past 480
source or 825 test lines. This design: about 255 source lines (M1 25, M2
110, M3 45, M4 25, M5 10, M6 25, layer map and index rows) and about 450
test lines plus the corpus.

## 11. Approval instrument

Proposed (D1): **corpus-first** at `tests/fixtures/rc3-baseline/`, landing
red before code. Model `models/graph.orm.yaml`: an `acyclic` rule with an id,
an id-less positional mandatory rule, a deontic rule, and a cardinality
minimum (for a row-less failure). Cases, each with a README story and a
golden:

- `standing-only`: the same loop in base and head → exit 0, all standing;
- `mixed`: one loop standing, one new edge in another loop, one loop
  resolved → exit 1; per-row novelty; counts;
- `rowless-new`: the cardinality minimum fails only in head → exit 1,
  `novelty: new`, `row_novelty: []`;
- `head-vacuous`: base fails a rule whose head is vacuous → exit 2, rows
  resolved;
- `base-unchecked`: an alethic rule unchecked in base only → exit 4;
- `bad-base`: an ill-formed base → exit 3 naming it;
- `refuse-derivation`, `refuse-temporal`: exit 3 before either population
  loads;
- `positional-warning` (text): the warning line;
- `conflict`: `--baseline` with `--populations` → exit 64.

## Findings (step 0/1, recorded as found)

- **F1.** `band()` returns the snapshot projection's band when one is
  attached (`checker/_reports.py:146-152`), so the baseline path must not
  take that shortcut; M1 decides from the comparison inputs and the head's
  vacuous verdicts instead.
- **F2.** The payload builder raises when the assurance block's decision
  differs from the band's (`payloads.py`, "assurance does not describe this
  report band"); a baseline band that differs from the plain band would
  trip it through the certified path. D5 avoids certifying.

## Implementability sweep (step 1, author inspection)

- Every criterion has a case that can fail (§3).
- All inputs exist: version-15 fields (RC1), stable acyclic rows (RC2),
  canonical JSON, the loader, `structured_derivation_ids`.
- The base check runs the same evaluator, so its rows are produced exactly
  as the head's; the cost is one extra check run (about 1 s on the
  2,047-edge fixture, O21).
- No new dependency or report version.

## Corpus findings (recorded while authoring the corpus, 2026-11-06)

- **C1.** An unreadable value needs `format_version: 2` in the population
  document; without it the loader refuses `{ "$opaque": … }` at exit 3
  (`jsonschema:type`). The `base-unchecked` base declares it.
- **C2.** The corpus model needs no derivations, so the refusal case uses a
  copy of RC1's `exact-terms` model (`models/derivations.orm.yaml`), whose
  plain report is version 7: the `check:baseline-unsupported` refusal is
  reported at version 7, as RC1's D8 does for its own refusal.
- **C3.** Every answer was computed by an oracle script from the head's and
  base's `--rule-ids` reports at eac81cf8, applying the spec's rules; none
  was read from an implementation.
- Red at commit: 10 failing (every case), 1 passing (the case list).
