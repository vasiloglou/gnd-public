# Phase FU1: version-7 derivation reasons (issue 113)

## 1. Status

**Draft, blocked on the plan gate.** The plan
([rule-check-followups-plan.md](rule-check-followups-plan.md), r1) is not
yet approved, and FD3 is not yet ruled. `auto=false`. No code before this
spec's owner gate.

## 2. Provenance

- Plan r1 §4 FU1, completion predicate 1; FD3.
- Issue 113; rule-check-adoption plan O29 and RC-D17 ("file it as its own
  issue; fixing it changes the frozen version-7 contract").
- Base: main `6651e5a4`.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| plan FU1-C1 | the probe report validates; a case per `term:*` reason the version-7 route can emit | T1, corpus |
| FU1-C2 | no report's bytes move | V3 (full suite) |
| FU1-C3 | every schema branch that references `$defs.derivation_verdict` is listed and tested | T2 |
| plan rule 1 | the schema may accept more, not less | M1 (additive enum only) |
| plan rule 2 | the defect reproduced before code | §6 probe, T1 red |
| AGENTS.md | component index | V6 |

## 4. Goal

A version-7 report (or version 9, a legacy reference report or a temporal
admission report) whose derivations are unchecked for a `term:*` reason
validates against `report.schema.json`.

## 5. Probe (2026-11-07, `6651e5a4`)

`tests/fixtures/v62-phase3/models/exact-terms.orm.yaml` with `redact: true`
removed, population `term-input.pop.yaml`: `gnd check --format json` →
schema_version 7, exit 4, derivations unchecked with `term:mod-zero`,
1 validation error from `jsonschema`; `term-clean.pop.yaml` → 0 errors.

## 6. Design

**Reuse table** (to be searched with `components_index.py search` before
code: `report schema derivation reason`).

**M1. `report.schema.json`, about 10 lines.** `$defs.derivation_verdict
.properties.reason_code.enum` gains the values `derivation_verdict_v15`
already lists that it lacks (FD3): `derived-unknown`, `term:mod-zero`,
`term:exact-value-too-wide`, `term:dependency-unavailable`, `term:div-zero`,
`term:sqrt-negative`, `term:haversine-coordinate-range`,
`term:float-overflow`. Additive only. Any packaged copy of the schema is
kept byte-identical (search at spec time).

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first** (a serialized format): one model and one population per reason the version-7 route can emit, with the expected `reason_code` and "validates" |
| D2 | FD3 (plan) | version 15's set |
| D3 | Review over the spec bytes | none |

## 8. Tests and verification ledger

| T | Case | Expected |
|---|---|---|
| T1 | each corpus case's version-7 report | validates; its `reason_code` is the case's; red before M1 |
| T2 | the branches referencing `derivation_verdict` (v7, v9, legacy reference, temporal admission) | each validates a report with a `term:*` derivation, where the route can produce one; a branch that cannot is named |
| T3 | an unknown reason (`term:not-a-reason`) | still refused |

| # | Obligation | Disposition | Command or evidence |
|---|---|---|---|
| V1 | merge-base record | run before any edit | focused files at `6651e5a4`; full suite on beast-3 |
| V2 | plan §9 FU1 row | run | `uv run pytest -q tests/test_fu1_*.py tests/test_schema_sync.py tests/test_report_json.py` |
| V3 | full suite vs base | run, sharded on beast-3 | failure set equal to the base's |
| V6 | component index | run at record time | `components_index.py changed --base 6651e5a4 --strict` |

## 9. Out of scope

Any change to a report's bytes; new report versions; issue 119 (FU3).

## 10. Size

Plan estimate: about 15 schema and 60 test lines, plus the corpus.

## Implementability sweep (author inspection)

- M1 is additive, so no existing valid report becomes invalid (rule 1).
- Which `term:*` reasons the version-7 route can emit is measured while
  authoring the corpus, not assumed.
