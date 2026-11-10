---
milestone: model-composition
station: phase-MC2
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MC2
date: 2026-11-10
gates:
  - command: ".venv/bin/pytest -q tests/test_mc2_consumers.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_model_verbalization.py tests/test_composition.py tests/test_ike_q3.py tests/test_v70_phase5_adversarial.py tests/test_v62_phase6_verbalization.py tests/test_evolve_loading.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py::test_all_parser_paths_receive_command_handlers tests/test_rf5_commands.py::test_entrypoint_rule_covers_all_groups_and_rejects_forbidden_imports tests/test_rf6_packages.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_disclosure_mode.py tests/test_rf4_peripheral.py tests/test_rf9_ci_repairs.py tests/test_v61_phase2_api.py tests/test_disclosure_docs.py --tb=short"
    exit: 0
    output: "1908 passed in 128.16s (0:02:08)"
  - command: ".venv/bin/pytest -q tests/test_rf6_query_policy.py tests/test_rf4_peripheral.py tests/test_rf9_ci_repairs.py tests/test_rf5_commands.py::test_entrypoint_rule_covers_all_groups_and_rejects_forbidden_imports tests/test_mc2_consumers.py --tb=short"
    exit: 0
    output: "1062 passed in 43.48s"
  - command: ".venv/bin/pytest -q tests/test_mc2_consumers.py tests/test_composition.py --tb=short"
    exit: 0
    output: "123 passed in 28.39s"
  - command: ".venv/bin/ruff check src tests --output-format json"
    exit: 1
    note: "Exactly13 baseline code/path/line/column findings; not a green lint gate."
  - command: "python3 scripts/components_index.py --no-cache changed --base 55a7d89a12a5500775602e137ee97bf9559c544c --strict"
    exit: 0
    note: "0 to fix,0 warnings,8 descriptions reread and remain accurate."
  - command: "git diff --check"
    exit: 0
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  status: "Not selected for MC2; final candidate/default and named census remain authorized close obligations."
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC2-spec.md
    sha256: a89649fb4e28628d0fbacc856f4093e7ff6a98bbf7c12ea0fa6d3107f73e7bf9
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/completion-source-manifest.json
    sha256: 8761a8a20215476ac3d8131322bcb1218f1339076e0ae4777e567e959a7ebec9
  - path: .gnd-planning/milestones/model-composition/evidence/MC2/completion-evidence-manifest.json
    sha256: a1bce47b204305a16795f2169edb6009d558f9a6afcd5e2c41146b5562c46a8f
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC2-codex-review.md
    sha256: fcc0b9fe736c1f0c35b778d03c17e26b8e65d504b66c76321840e7b2c5f03719
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC2-codex-confirmation.md
    sha256: b094ce86e0fca9dfd51f7478dce2e825c8a3fab24db8a0069367738af3f7784e
  - path: .gnd-planning/milestones/model-composition/010-MC2-gate.md
    sha256: 5d57e37ce9e0c4a9ac425763f11cbb809311eac1f3e7fc4f494910dc12d0be07
  - path: .gnd-planning/milestones/model-composition/012-MC2-amendment.md
    sha256: c10334a31812a812373c7ccb0c5697d00b5059dfbae9afd710109791864caadd
---

# Claim

The MC2 focused gate exited0. Its selected lint gate exited1 with exactly13 frozen baseline findings. One independent Codex CLI reviewer requested two reproduced fixes; its one confirmation approved repaired source07986c53580c6edb3ed48ad01427aad19c974a94. Delegated acceptance (auto=true),2026-11-10, accepts this phase with the explicit baseline boundaries. One reviewer is one reviewer.

## What changed and criteria

MC2-C1: the gated admission inventory re-reads all MC1 rows and explicitly supports rooted composition/replay and complete model review; remaining routes keep their guards. MC2-C2: no tempdir-copy route was enabled, so unaccompanied copies still refuse. MC2-C3: the existing renderer adds ordered include headers; the new public verbalize_model view and verbalize model command expose that same complete text. Frozen include-free text remains equal. One registry marks caller-authored model review every-mode, including authored samples; its single normative disclosure table and exact export/parser consumers agree. MC2-C4: codegen and conformance stay refused before a positive currency claim, including stale included bytes.

Rooted population compose uses the canonical composed loader, retaining original authored bytes for the record. Replay checks the same loaded Model's private authored-byte SHA before record verification. Private metadata stays absent from both serialization entry points. CLI output exclusions protect the model, every included vocabulary and composition inputs before staging either output; aliases use the existing identity check. Public compose wire shape/signature remains unchanged.

Thirteen corpus meanings were authored before implementation in010, with C03's independently verified comparison correction in012. Rejected runs and their narrower successor controls remain retained. The initial review's dependency overwrite and incorrect source-observation attribution reproduced as seven red tests before fixes. The confirmation checked those repairs and immediate neighbours only; no additional round is authorized by this record.

## Gate output (verbatim)

    1908 passed in 128.16s (0:02:08)
    exit0

    1062 passed in 43.48s
    exit0

    123 passed in 28.39s
    exit0

The primary command was:

    .venv/bin/pytest -q tests/test_mc2_consumers.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_model_verbalization.py tests/test_composition.py tests/test_ike_q3.py tests/test_v70_phase5_adversarial.py tests/test_v62_phase6_verbalization.py tests/test_evolve_loading.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py::test_all_parser_paths_receive_command_handlers tests/test_rf5_commands.py::test_entrypoint_rule_covers_all_groups_and_rejects_forbidden_imports tests/test_rf6_packages.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_disclosure_mode.py tests/test_rf4_peripheral.py tests/test_rf9_ci_repairs.py tests/test_v61_phase2_api.py tests/test_disclosure_docs.py --tb=short

Commands use the checkout's locked .venv; uv run is the canonical project launcher spelling. Default exclusions were retained. Counts overlap and are not summed. The final CLI wording adjustment occurred during the primary process; the final123 selection explicitly reruns its consumers after that edit. Header latency T10 and full captured10MiB authored-byte comparison T11 are bounded controls of the added layers, not host-independent performance guarantees. Full command output is in the JSON evidence. Initial final index check found a stale generated commands page after the last wording edit; regeneration restored strict0. Lint's exact13 findings are retained in review-lint.json and the earlier verbatim lint output.

## Refactoring review

What did this work reveal about existing structure that should change? Refactors EXECUTED: factor the existing population composition implementation behind a private worker that also retains its authenticated input paths. Public compose delegates without changing its output or signature, while the CLI consumes the same snapshot for write exclusions. This avoids a second loader/resolver and was verified by the existing composition consumers plus the confirmation. No other structure change is proposed by this phase.

## Boundary

A completed walk of the phase protocol is not an acceptance claim for the whole milestone. The adversarial review is one reviewer's reading, not a proof. The phase does not establish merge authority, multi-file atomicity, codegen/conformance currency, generic recovery support, MC3 evolution/re-pin support or final documentation acceptance. No broad default suite, marked census, historical/native replay, certification or publication ran for this phase. MC1's exact six baseline default-suite failures and13 lint findings remain explicit; final candidate comparisons are still owed. The five verbatim-log trailing-space lines accepted in009 remain untouched. Size106 runtime/563 test-support gross added Python lines stays below375/600; raw narrated corpus/expected data is separately retained.

## Open questions

- Obtain explicit owner merge authority for PR156's fixed completion head. MC1 PR154 merged at d5ca5d9a under its separate explicit owner authorization.
- MC3 must implement guarded authored evolution, ownership, re-pin analysis/publication/recovery and proposal writers under its own spec/corpus gate. Private loader/Model overlap requires serial implementation.
- Revise the docs checkpoint in PR155 to address the owner's actual request for a higher-level real example, record the reaction in the final MC4 spec, then finish the re-pin half after MC3.
- At close repair the plan's nonexistent pre-MC2 model CLI assumption, disjoint-files premise and all-docs-wait-until-MC4 premise. Preserve the census and guard-order amendments and known-red boundaries from earlier records.
- Final candidate/default and named census comparisons on beast-3, one explicitly selected Codex CLI close review and all on-main exit predicates remain before close/issue95 closure.
