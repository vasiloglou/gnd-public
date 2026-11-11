---
milestone: guarded-rule-workflows
station: phase-GW2
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GW2
date: 2026-11-11
gates:
  - command: "pytest -q tests/test_rule_edition_comparison.py tests/test_guarded_diagnostics.py tests/test_rc1_rule_ids.py tests/test_rc3_baseline.py tests/test_rc4_allow_vacuous.py tests/test_report_json.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_public_semantic_boundaries.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "619 passed in 44.68s"
  - command: "pytest -q tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_development_scaffold.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "133 passed, 1 deselected in 31.83s"
  - command: "python3 scripts/components_index.py changed --base 6cbca615 --strict"
    exit: 0
    output: "changed against 6cbca615 (6cbca61): 17 file(s) differ; 0 to fix, 0 warning(s), 2 to reread"
  - command: "installed Python 3.14 candidate smoke from a clean target directory"
    exit: 0
    output: "GW0 check 0, validate 0 with two warnings; GW2 comparison 0 with side bands 1 and 1"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "historical lanes are outside the selected impact closure"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/phase-GW2-spec.md
    sha256: 72be70e4fb08f694ce8369927e424bf8e7e1efbecc8ef5094bf5fd9f97d89965
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/phase-GW2-claude-review.md
    sha256: 100c5cd8d5b0e0dbf36d646ac7dfc210005fb2b95fc71b720df9c066fa1f6d0c
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW2/installed-smoke.json
    sha256: 766961b9bf72c2da7c81af67a7ac8558c6ab5ea7c2714250b69caa71041112a5
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW2/dynamic-query-successor.json
    sha256: ec962a108155a78ea7e1fa06cc43c1107e115727938a115478775625ce70bd3d
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW2/source-successors.json
    sha256: 6bb31f7b9eedd9b7835d2b88428ec99d07aed5ad5662454e1100bcda67511e5e
  - path: tests/test_rule_edition_comparison.py
    sha256: c8b29aa286b02fa9c6737f687a4110d370c05d5ddff47f8f3bb85a9e358c459f
  - path: src/gnd/report.schema.json
    sha256: ab1e14c01145c5dcaa2515274a43a0c031a7b3c2f19dfd538c86e94442f2d989
---

# GW2 result

The new comparison exited 0 on the decisive narrowing and its reverse.
The independent checks exited 1 with 43 and 1 offending bindings. The
narrowing emitted 42 base-only bindings, one standing binding and no
head-only binding. Its reverse emitted 42 head-only and one standing.
The installed candidate reproduced both milestone capabilities. The
[smoke receipt](evidence/GW2/installed-smoke.json) binds the exact wheel,
source commit, site-packages origin and command payload digests.

The red harness at `6cbca615` exited 1 because both controls got option
exit 64. The implementation first landed in `05b56ed5`. The phase's
entrypoint check rejected a direct command-to-service import and an exact
historical RF5 hash needed a successor for GW0. The fix uses the existing
API gateway and records the exact hash successor, then reruns the guarded,
baseline, report and CLI checks. Affected Ruff exited 0. Both catalog
rereads found the entries still accurate after the new API call seam.

## Independent review and dispositions

Tool-disabled Claude Code Opus high read the public `05b56ed5` spec and diff
on stdin and exited 0 with [revise](notes/phase-GW2-claude-review.md). One
reviewer is one reviewer. It read tests and did not run them. Verified
repairs are in `e02345d3`.

| Finding | Disposition and evidence |
|---|---|
| 1 · false standing match | A red control with a different extra variable in each edition returned a standing row. Shared sites must cover every variable of at least one edition. The exact control now exits 4 and leaves the delta null. |
| 2 · false complete outcome | The red helper control returned a delta for an unknown verdict. Unknown and missing observations now withhold deltas. Missing observations retain declared identity. Either ordinary check band 4 also makes the overall comparison incomplete. |
| 3 · rowless against rowed | The guarded red control treated mixed witness shapes as directional changes. The guarded case now returns `binding-shape-unavailable`. An independently decided empty set can still be compared with a rowless failure. |
| 4 · missing operand | The pre-fix control already exited 64 because the existing snapshot parser checks the positional population. |
| 5 · ID removal | The plan explicitly reports declared-ID removal and side-local anonymous rules as separate observations. Text now prints side verdict and modality, alongside pairing and delta counts. |
| 6 · diagnostics and schema | Shared malformed population bytes use `population-ill-formed`. Side-specific admission retains the side. The CLI constrains unexpected checker exits to 70 and validates both success and refusal shapes. The phase exposes directional witnesses in text and both originals for standing in JSON. |

## Refactoring review

No further refactor needed. The edition comparison reuses the shared
typed witness identity and the existing validation, checker and version-15
rule address pipeline. The CLI's API gateway preserves the existing
dependency direction. The alignment and completeness rules belong to
the comparison module.

## Boundary and open questions

The comparison accepts the plain rule-ID scope and same vocabulary.
It preserves ordinary population-header checks, so a deliberately shared
population can omit its optional model ID when the editions use different
IDs. It reports authored rules separately from derivation diagnostics.
Remaining incomparable guard shapes are reported per rule. Rule changes
across vocabularies, the three deferred issues, and release or certification
work stay outside this phase.
