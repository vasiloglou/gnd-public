---
milestone: rule-check-followups
station: phase-FU1
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-FU1
date: 2026-11-07
gate:
  command: "uv run pytest -q tests/test_fu1_*.py tests/test_schema_sync.py tests/test_report_json.py"
  exit: 0
  output: "108 passed"
  note: >-
    The plan section 9 FU1 row (V2), at f6b9303d. The mutants, the schema
    impact files, the component index check (V6) and the sharded full
    default suite against main 6651e5a4 (V1/V3) are in the body.
evidence:
  - path: src/gnd/report.schema.json
    sha256: d2ac38dafb978c7a16f6e80e526e3c83c438f23245366430a359b6d462c8b5ac
  - path: tests/test_fu1_term_reasons.py
    sha256: 2080991393e45e964e6c7fc600f5f8dccd1596673723d0cff27f766e6683b93b
  - path: tests/fixtures/fu1-term-reasons/expected/answers.json
    sha256: 0f59d80c14f0cfc71c76f71ff264f6d1998231e4a85a8e4bba70cf33b1bbec79
  - path: tests/fixtures/fu1-term-reasons/README.md
    sha256: c2e38840fffaca9a95260d3c1c4e951a840a5c134749ef83da25d2c4b9606fe1
  - path: tests/fixtures/fu1-term-reasons/models/terms.orm.yaml
    sha256: 4779e89b61473fbbc6cf3db38f7a8de7b7247a27f925eb68a3df4d51bc1da529
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU1-spec.md
    sha256: 3afc3fd9a4cb1063e4a4c6b28adce3e0f8f13259a9756e27077b9fba79d2aaff
  - path: .gnd-planning/milestones/rule-check-followups/notes/phase-FU1-codex-review.md
    sha256: 291e3354b634edea119be3d2b3c08778341ee3dfbc9a67b1b8e6e6d3f784c19b
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU1/full-suite-main-6651e5a4.txt
    sha256: 7c5d2cca18cf62b9478c41897e5a863116a0fba5c4cadfc2a5b9b010ebc4a9b7
  - path: .gnd-planning/milestones/rule-check-followups/evidence/FU1/full-suite-fu1-9f938f48.txt
    sha256: 5aa1e12a7287d18b618db2f265fb15f4731803d45ff863a813abbb236a1da0d9
---

# Claim

At f6b9303d, a version-7 report whose derivations are unchecked for a
`term:*` reason validates against `report.schema.json` (issue 113). Both
reason-code enums of `$defs.derivation_verdict` (the property enum and the
unchecked branch's conditional enum) now hold version 15's set (FD3), and
so do version 9, the legacy reference report and the temporal admission
report, which reach their derivation rows through it. The change only adds
enum values: no report's bytes moved, and the full default suite's failure
list equals main's.

## What shipped

- **M1** `src/gnd/report.schema.json` (9f938f48), 17 lines added: both enums
  gain `derived-unknown`, `term:mod-zero`, `term:exact-value-too-wide`,
  `term:dependency-unavailable`, `term:div-zero`, `term:sqrt-negative`,
  `term:haversine-coordinate-range`, `term:float-overflow`. The unchecked
  condition is kept.
- **Corpus** `tests/fixtures/fu1-term-reasons/` (08167666, approved by the
  owner with "Approve, implement"): one model, six populations, one per
  reason a plain version-7 check emits, with narrated answers.
- **Harness** `tests/test_fu1_term_reasons.py`: T1 (six CLI cases), T2
  (each of the 11 reasons on each of four branches, validated through each
  branch's own item pointers since f6b9303d), the version-15 non-regression
  cases and T3 (an unknown reason is refused). 63 cases.

## Gate output (verbatim)

V2, at f6b9303d:

    uv run pytest -q tests/test_fu1_*.py tests/test_schema_sync.py tests/test_report_json.py
    108 passed in 11.96s

Corpus at each stage (`uv run pytest -q tests/test_fu1_term_reasons.py`):

    08167666 (corpus, red):                        38 failed, 25 passed
    9f938f48 (M1):                                 63 passed
    mutant, property enum only widened:            38 failed, 25 passed
    mutant, conditional enum only widened:         38 failed, 25 passed
    f6b9303d, pre-fix schema (6651e5a4):           38 failed, 25 passed
    f6b9303d, route mutant in temporal branch:      7 failed, 56 passed

Schema impact closure: the 48 test files that read `report.schema.json`, a
report schema helper or `derivation_verdict`, at 9f938f48:

    1601 passed, 40 deselected in 191.89s (0:03:11)

V6, component index:

    python3 scripts/components_index.py changed --base 6651e5a4 --strict
    changed against 6651e5a4 (6651e5a): 17 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    exit=0

V1 (main 6651e5a4) and V3 (9f938f48), full default lane, six round-robin
shards on beast-3:

    V1 main 6651e5a4: 17750 passed, 2 errors; shards exit 0,0,0,1,0,0
    V3 fu1 9f938f48:  17813 passed, 2 errors; shards exit 0,0,0,0,1,0
    failing lists: both sha256 8261732b98e252d1e17e491a8480080bafd2434fbd17f8a503aad8390ea9c20a

The 2 errors are the `tests/test_public_optional.py` uv-version pins. The
63 extra passes are the FU1 cases. f6b9303d changes only the FU1 test file
after 9f938f48, which V2 covers. Evidence: `evidence/FU1/full-suite-*.txt`.

## Criteria

| Criterion | Result |
|---|---|
| FU1-C1 | the six reasons a version-7 check emits each have a CLI case: exit 4, version 7, the expected reason, schema-valid. `term:dependency-unavailable` and `derived-unknown` do not reach a version-7 derivation (spec C2) and have schema cases only |
| FU1-C2 | the failing list equals main's; no fixture or recorded report changed |
| FU1-C3 | T2 covers `derivation_verdict`, `derivation_verdict_v9`, `legacy_reference_report` and `temporal_admission_report`, at every location where a branch references one of the first two; version-15 non-regression cases pass |

## Review

One reviewer is one reviewer: Codex (gpt-6-sol, xhigh, read-only) over
`git diff 6651e5a4 9f938f48`, disposition `revise`, two completeness
findings, both reproduced: [phase-FU1-codex-review.md](notes/phase-FU1-codex-review.md).

- **R1, fixed** (f6b9303d): T2 checked that a report branch referenced the
  row definition but then validated a bare row. A narrowing inside a branch
  passed all 63 cases; it now leaves 7 red.
- **R2, deferred**: see Open questions. The reviewer confirmed the six CLI
  answers at 9f938f48, that the change is additive, and that there is no
  other schema copy, current digest or version-7 reason list to update.

## Refactoring review

None needed. The phase changed two enum lists and one test file. The one
structure it exposed is that `derivation_verdict` and
`derivation_verdict_v15` now carry the same reason list twice. Sharing it
through a `$ref` would tie the two versions together, so a later widening
of version 15 would silently widen version 7; the plan's frozen-variant
rule (section 0) wants each version's list stated where it is read. The
duplication is deliberate.

## Boundary: what this phase does NOT establish

- `derived-unknown` cases establish only that the enum admits the value,
  using a row with no findings; that is not a shape the runtime builds (R2).
- `derivation_verdict_v10` has its own reason list and is not a branch of
  this phase (FU1-C3 names the branches through `derivation_verdict`).
- No report variant was added and no report's bytes changed.
- The slow `evidence or census` lane was not run; the phase changes no
  source file it reads beyond the schema, which the impact closure covers.

## Open questions

| Row | Question | Owner / target |
|---|---|---|
| FU1-O1 (R2) | `DerivationVerdict` accepts `derived-unknown` only with one `derived-extension-unresolved` finding (`extensions.py:133-140`); the schema (`derivation_verdict` and `_v15`) refuses that finding kind and any unchecked finding. **Resolved for version 7 by the merge amendment below** (refused there). `derivation_verdict_v15` still admits it with no findings; whether that should change is left to the milestone close | owner; milestone close |

## Amendment: merge with main (2026-11-07)

While PR 121 was open, main gained PR 122 (9c39a5e2, merged as 7cb98a99),
which fixed issue 113 independently: the same two enums gained the seven
`term:*` reasons, and `derived-unknown` stayed off version 7, with a test
(`test_unchecked_term_derivations_validate_on_the_selected_wire`) requiring
its refusal. The merge conflicted on that one value. The owner ruled "Take
main's", answering "How should the merge resolve it?".

- The schema is now byte-identical to main's 7cb98a99; FU1's M1 survives
  only as the seven `term:*` values both sides added.
- The corpus answer for `derived-unknown` changed from accepted to refused
  on the four version-7 branches (`refused_on_version_7`); the approved
  answer is retained under `superseded_answers`. It stays accepted on
  version 15. A new case, `test_a_version_15_only_reason_stays_refused`,
  leaves 4 red against FU1's earlier schema (73e55ea2) and passes on main's.
- On the merged tree: V2 plus the scaffold test, 171 passed; the 48 schema
  impact files, 1607 passed. The full suite above ran at 9f938f48, whose
  schema differs from the merged tree by `derived-unknown` alone; it was
  not rerun.
- Claim above, read with this amendment: version 7 admits the seven
  `term:*` reasons, not `derived-unknown`.
