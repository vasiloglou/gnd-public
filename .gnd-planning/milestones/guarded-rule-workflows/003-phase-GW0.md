---
milestone: guarded-rule-workflows
station: phase-GW0
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GW0
date: 2026-11-11
gates:
  - command: "pytest -q tests/test_guarded_diagnostics.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_public_semantic_guarded_join.py tests/test_public_guarded_consequent_matrix.py tests/test_rc1_rule_ids.py tests/test_rc3_baseline.py tests/test_rc4_allow_vacuous.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "210 passed in 35.27s"
  - command: "pytest -q tests/test_guarded_diagnostics.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "16 passed in 6.39s"
  - command: "pytest -q tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_development_scaffold.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "133 passed, 1 deselected in 112.62s (0:01:52)"
  - command: "python3 scripts/components_index.py changed --base 25ff87e9 --strict"
    exit: 0
    output: "changed against 25ff87e9 (25ff87e): 22 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "historical lanes are outside the selected impact closure"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/phase-GW0-spec.md
    sha256: 05700c719cc4d34026dedc465f52d205aff59de6ab32130bdfa06a548b12768b
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/phase-GW0-claude-review.md
    sha256: 5403da39861fe9ce58469bd837bbacf3f67d29d0dc2c097eb070b28a96488a3b
  - path: tests/test_guarded_diagnostics.py
    sha256: b1d07562b2e7e1c8d5efc5a72f623c75a8cf4de4283e8667caba61cf86e36287
  - path: src/gnd/report.schema.json
    sha256: 6b8aa8177103780c4c113e54ba3e01a73784247e971e1247447d649942b5549e
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW0/dynamic-query-successor.json
    sha256: 63d426d9169b5e8686e0fa3300b2405bf61932507cb1b3b1ece374c90c37cc76
---

# GW0 result

The public GW0 diagnostics tests exited 0. The corpus harness first exited 1
with eight failures for the missing option and missing typo findings
(`25ff87e9`). The core implementation is `24c72d86`. The focus gates used the
existing workspace Python and pointed PYTHONPATH at this checkout. Affected
Ruff exited 0. The component index's subsystem reread confirmed the same call
order. The final focused rerun includes the two review follow-up controls.

E1/E2 exercise active, empty, omitted and unavailable observations and the
populated first and later empty atom. E3 exercises both issue typo sites at
the public validate command and probes ranges, role scope and exhaustion.
E4 validates the selected report and compares its underlying verdicts and
baseline outcomes with version 15. The work test counts the indexed join
calls with and without the flag.

## Independent review and dispositions

Codex CLI and the initial Claude Code file-reading pass each exited 124.
A tool-disabled Claude Code Opus high pass over the exact public diff exited
0 and returned [revise](notes/phase-GW0-claude-review.md). One reviewer is one
reviewer. The successful reviewer inspected the diff and spec on stdin and
did not run tests.

| Finding | Verification and disposition |
|---|---|
| 1 · snapshot input | `evaluation_snapshot` replaces only coverage for guarded checks. The indexed join now reads the actual coverage for diagnostics. Its matching inputs remain identical. The guarded join and prior byte controls exited 0. |
| 2 · availability | The spec requires a known count for a completed populated join with explicit or default coverage. Covered empty gives zero and omitted empty gives null. A consequent-only refusal can coexist with a known count. The first branch is keyed by atom index. The focused tests exercise these distinctions. |
| 3 · row order | `build_check_payload` preserves the internal verdict iteration order through serialization and version-15 projection. The pairing is strict and occurs before redaction. Tests exercise interleaved ordinary and guarded verdicts and baseline. |
| 4 · schema | The v15 source definitions have no object-level invariants beyond closed shape and required keys, all preserved in v16. Restored the prior JSON escape spelling. Added a negative schema mutation for a positive binding count carrying an empty-atom index. |
| 5 · canonical scalar | The previous numeric tuple is exactly Integer, Float and Number. The layer test and exact query-policy gate exited 0. The historical adapter name is an identity alias of its defining home. |
| 6 · domain predicate | The input value-constraint schema requires exactly one of allowed, range or ranges. Enumerations compare typed identity, while a range over an incomparable operand supplies no definitive exclusion. This follows the shared scalar predicate. |

## Refactoring review

Refactor executed. `gnd.values.canonical_scalar` now owns the scalar conversion.
`gnd.semantic_adapter.canonical_scalar` retains the exact function as an
identity alias. Static domain lint and snapshot adaptation use the same
conversion. The new report field is built from the existing indexed join.
The legacy message formatter's separate count path stays as compatibility
prose. It can be retired only in a future report compatibility change.

## Boundary and open questions

The selected report is the plain rule-check route. Temporal, redacted and
reference-population report extensions require their own evidence. GW2 owns
the installed-candidate smoke and the edition comparison. The older report
message count remains a separate legacy presentation path.
