---
milestone: guarded-rule-authoring
station: phase-GA2
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GA2
date: 2026-11-11
gates:
  - command: "pytest -q tests/test_discover_guarded_join.py tests/test_discover.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py tests/test_rf1_layering.py -p no:cacheprovider --tb=short"
    exit: 0
    output: "487 passed in 38.53s"
  - command: "pytest -q tests/test_discover_guarded_join.py tests/test_rf1_cli_pins.py tests/test_rf6_query_policy.py tests/test_rf5_commands.py tests/test_rf1_layering.py -p no:cacheprovider --tb=short"
    exit: 0
    output: "442 passed in 19.40s"
  - command: "python3 scripts/components_index.py --no-cache changed --base 6d659d3b --strict"
    exit: 0
    output: "changed against 6d659d3b (6d659d3): 16 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately selected CI"
  reason: "historical evidence lanes are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA2-spec.md
    sha256: 31295650ba952de2f88d2c4cc14dbedf4b1744edcba108c1f2ae702fc86672ad
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA2-codex-review.md
    sha256: aa98c9346d10dbf173010dfbf4e94078006daa914b19e4281f922f8febfa8da7
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA2/dynamic-query-successor.json
    sha256: 37dd1840c219f5e065e08278dfb3102f503d54a2bf549ccbd8abb014cd9dbbaf
  - path: .gnd-planning/milestones/guarded-rule-authoring/corpus/GA2/expected.json
    sha256: 2a38942d2c191e6dff33a2aa7999672e1a4ea1ac666eac6a0484bbbb193db8b2
  - path: tests/test_discover_guarded_join.py
    sha256: adab5e4cd5dcfb28bf061649227df6bf72dc7013cf6b6830bdbc7db33af55384
---

# GA2 result

The red CLI cases at `6d659d3b` exited 64 before the family existed.
The directed `app` to `core` prohibition has one supporting edge.
The reverse direction has one violation in 21 distinct edges. The
same-class implication has one violation in 22 distinct edges. Both
near misses name the original `ft0#20` relation row. The marked rule
passes on its single eligible edge. An all-inside unmarked fixture
passes with 21 distinct edges. Duplicate rows do not inflate support.
The existing evolve preview accepted the generated proposal.

The directed cap and the work limit each identify the first omitted
ordinal. Missing, ambiguous and uncovered classification cases refuse
the family with their reason. The work exhaustion fixture retains
ordinary uniqueness discovery. The out-of-threshold candidate produces
no near miss. The first broad gate tested the candidate before review.
The second gate tested the reproduced review fixes and source controls.

## Independent review and dispositions

Read-only Codex CLI reviewed the public `8032a346` diff and exited 0 with
[changes requested](notes/phase-GA2-codex-review.md). One reviewer is one
reviewer. It read the source and did not run commands or tests. It confirmed
the separate directed cap, typed endpoint classification, first row IDs,
redacted-role refusal, opt-in defaults and work exhaustion behavior.

| Finding | Disposition |
|---|---|
| Verdict and binding count did not verify violations. | Reproduced with a warning of the correct size naming a different edge. Admission now compares violation counts and checks displayed near-miss row IDs against checker witnesses. |
| The service accepted mismatched family and selector settings. | Reproduced both ways. Both service paths now validate the pairing before file reads. |
| Antecedent order affected declared-rule suppression. | Reproduced with reordered atoms and renamed variables. A bounded canonical key over the supported two- and three-atom shapes now suppresses that duplicate. |

## Refactoring review

No further refactor needed. The joined module owns selection, enumeration
and independent counting. The service keeps checker admission, near misses,
advisory envelopes and output publication in their existing homes.

## Boundary and open questions

The family covers explicit binary relation, classifier and optional marker
roles. The phase defers automatic coordinate inference and partial or
non-functional classifications to a future discovery milestone if requested.
The work guard can refuse the joined family before it publishes candidates.
GA3 owns the installed cross-workflow smoke.
