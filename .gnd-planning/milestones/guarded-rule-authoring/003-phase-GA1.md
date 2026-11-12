---
milestone: guarded-rule-authoring
station: phase-GA1
skill: "n/a -- repository development under process-milestone auto=true"
scope: phase-GA1
date: 2026-11-11
gates:
  - command: "pytest -q tests/test_synth_guarded_cases.py tests/test_rf5_commands.py tests/test_rf6_query_policy.py tests/test_rf1_layering.py -p no:cacheprovider --tb=short"
    exit: 0
    output: "319 passed in 20.47s"
  - command: "python3 scripts/components_index.py --no-cache changed --base d0b76a68 --strict"
    exit: 0
    output: "changed against d0b76a68 (d0b76a6): 20 file(s) differ; 0 to fix, 0 warning(s), 1 to reread"
  - command: "gnd synth src/gnd/examples/rule_check/model.orm.yaml --guarded-cases, then gnd measure against the emitted scoped model and ordinary corpus"
    exit: 0
    output: "4 active guard examples; measure scored 15 ordinary populations with zero checker defects"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request or separately selected CI"
  reason: "historical evidence lanes are outside this phase's impact closure"
evidence:
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA1-spec.md
    sha256: ab8fb19a43e91d33cc77ab3c921aa9323900419d4aa0d8a21421e87effe39f30
  - path: .gnd-planning/milestones/guarded-rule-authoring/notes/phase-GA1-codex-review.md
    sha256: 1647921b6fb18ff5f4562146d43f82a4e69577d1662f6de37cc253e7d8a22363
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA1/dynamic-query-successor.json
    sha256: 4649d6488b4c1822ecd8daee69bbaeb372ab1f2f874f89d53d146d623d89e3fd
  - path: .gnd-planning/milestones/guarded-rule-authoring/evidence/GA1/source-successors.json
    sha256: b39612a532b476bbd465062be310e53a63172f9c625e2e41e6872143e186bcad
  - path: tests/test_synth_guarded_cases.py
    sha256: 659b8611031d28691c9715353dd5a38ca554aae679452ed1c6708eff7ee73507
---

# GA1 result

The red corpus at `d0b76a68` reproduced CLI exit 64. The scoped-case command
produces fail/warning and active pass pairs for atom, absence, exists and
comparison. The mixed fixture preserves the literal antecedent in both
fact-based cases. It publishes mandatory and ring violation populations
even with an unserved guard. Measurement accepts the scoped model and
refuses the full model at exit 3. The shipped example's smoke produced
manifest SHA-256
`daf42271496bea96f2b70ff26d4ebfaa368867a685a3b1cc9c97a2743b943a8c`
before the exclusive rename change. The installed smoke follows in GA3.

The pre-review broad synthesis, measure, CLI and query run at `5b562395`
passed 646 tests. A later broad run overlapped the corpus transaction edit,
so two tests observed mixed source and loaded-module bytes. The final
runtime and both affected source guards passed together at `d1bf99ee`.
The final focused fixture covers malformed input, invariant failure, active
and determinate checking, quarantine, individual refusals, atomic
publication and preservation of a completed pair at the run limit.

## Independent review and dispositions

The first Claude Code invocation exited 124 without a review. The read-only
Codex CLI fallback reviewed the public runtime diff at `9e2880b9` and exited
0 with [changes requested](notes/phase-GA1-codex-review.md). One reviewer is
one reviewer. The reviewer inspected the diff and did not run commands or
tests. The review confirmed positive independently counted bindings, target
verdict and count confirmation, deontic warning attribution, collateral
findings, existing-root refusal and a single public JSON document.

| Finding | Disposition |
|---|---|
| Inline guarded rules | Refuted by the model schema and a public CLI regression. An inline guard exits 3 before any output. |
| Empty output root visible during commit | Reproduced at the publication seam, then repaired with the shared exclusive native rename. A separate test verifies preservation of a competing root. |
| Atom and absence omitted from checker work estimate | Reproduced with both branches at the antecedent-only budget, then repaired by charging the witness rows and resulting combinations. |

## Refactoring review

No further refactor needed. The new pair search and confirmation service
have distinct dependencies. Shared joins, scalar identity, value predicates,
corpus staging, exclusive rename and the existing ordinary synth lane own
their existing behavior. The private payload sink lets one CLI operation
reuse ordinary synthesis without duplicating its report or admission logic.

## Boundary and open questions

The supported fragment is asserted scalar facts, without existential
filters, temporal terms or reference-population binding. Construction and
checker preflight can refuse at the recorded search limit. The guarded
manifest supports targeted examples and scoped ordinary measurement.
Guarded-case scoring in the ordinary full-expectation measure lane is
deferred to a future measure extension if requested. The subsystem catalog
reread confirmed its flow remains accurate. GA2, GA3 and milestone close
remain separately gated.
