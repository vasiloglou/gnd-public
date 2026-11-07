# Phase FU1: version-7 derivation reasons (issue 113)

## 1. Status

**Approved (2026-11-07); implemented.** The owner approved the corpus
(commit 08167666) with "Approve, implement", answering "Do you approve the
FU1 corpus answers?". D1 and D3 were ruled over r1 (sha256 `55c9a2ad…`,
commit 476c36ed) with "Approve as proposed". `auto=false`. Prior status:
"Owner-decided (2026-11-07); approval pending on the corpus."

## 2. Provenance

- Plan r3 §4 FU1, completion predicate 1; FD3.
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

**Reuse table** (searched 2026-11-07 at `6651e5a4`:
`components_index.py search "report schema derivation reason code"`,
`"report schema contract"`; `git ls-files | grep report.schema.json`).

| Capability | Found | Decision |
|---|---|---|
| the reason set | `$defs.derivation_verdict_v15.properties.reason_code.enum` | **reuse** its values (FD3) |
| the schema | `src/gnd/report.schema.json`, the only tracked copy; `tests/test_schema_sync.py` excludes it (review of r2) | **adapt** |
| a report to validate | `tests/fixtures/v62-phase3/models/exact-terms.orm.yaml` and its populations | **reuse** as the corpus's source |

**M1. `report.schema.json`, about 20 lines.** Both reason-code enums of
`$defs.derivation_verdict` gain (review P1): the property enum and the
unchecked branch's conditional `then.properties.reason_code.enum`
(`report.schema.json:1108-1113`); a probe that widened only the property
enum left the report invalid. Each gains the values `derivation_verdict_v15`
already lists that it lacks (FD3): `derived-unknown`, `term:mod-zero`,
`term:exact-value-too-wide`, `term:dependency-unavailable`, `term:div-zero`,
`term:sqrt-negative`, `term:haversine-coordinate-range`,
`term:float-overflow`. Additive only; the unchecked condition is kept. There is no packaged copy to keep in step.

## 7. Decisions (owner rules at step 2)

| D | Question | Proposal |
|---|---|---|
| D1 | Approval instrument | **corpus-first** (a serialized format): one model and one population per reason the version-7 route can emit, with the expected `reason_code` and "validates" **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU1's decisions D1 and D3?"). |
| D2 | FD3 (plan) | version 15's set **Ruled at the plan level (o, 2026-11-07): FD3 as proposed.** |
| D3 | Review over the spec bytes | none **Ruled (o, 2026-11-07): as proposed** ("Approve as proposed", answering "How do you rule on FU1's decisions D1 and D3?"). |

## 8. Tests and verification ledger

| T | Case | Expected |
|---|---|---|
| T1 | each corpus case's version-7 report | validates; its `reason_code` is the case's; red before M1, and red if either enum is left narrow |
| T2 | the branches whose reason-code enum comes from `derivation_verdict` (v7, v9, legacy reference, temporal admission) | a direct schema case for each validates a `term:*` derivation, whether or not a CLI route emits it; plus a version-15 non-regression case (review P2) |
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

## Corpus findings (recorded while authoring the corpus, 2026-11-07)

- **C1.** Six of version 15's eight added reasons reach a plain version-7
  derivation, each measured with its own population (`mod`, `div`, `sqrt`,
  `haversine`, a float overflow from 10^400, an exact product past 65,536
  bits): exit 4, schema_version 7, exactly one schema error each.
- **C2.** `term:dependency-unavailable` does not reach a version-7
  derivation: a derivation over an unchecked derivation carries the original
  reason (probe: `twice_mod` over `out_mod` reports `term:mod-zero`).
  `derived-unknown` is a constraint reason on the anchored route
  (`checker/_core.py:1768`). Both are covered by direct schema cases only.
- **C3.** T2 validates a derivation row against `derivation_verdict` and
  `derivation_verdict_v9` directly; `legacy_reference_report` and
  `temporal_admission_report` are checked to reference one of them for their
  derivation rows.
- Red at commit: 38 failing (6 CLI cases, 32 schema cases), 25 passing (the
  three older reasons on each branch, the version-15 non-regression cases,
  the two refusals). Answers were derived from the reports at 6651e5a4 and
  FD3's set, not from an implementation.
