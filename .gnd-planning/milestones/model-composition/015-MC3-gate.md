---
milestone: model-composition
station: "MC3 corpus/spec gate"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: MC3-gate
date: 2026-11-10
gates:
  - command: "ruling: delegated (auto=true) approve MC3 spec sha256 0dd46dc6ca905c32ac907d6a4bc858d8a8f0a64bfbed0e4cd4d52f90a8b96ad8 and corpus answers sha256 a5511a56355b8268bda19c2cb703c0e679738a91329419fba0fc46ef43eb9b54"
    exit: "n/a -- ruling"
  - command: ".venv/bin/python -m gnd check tests/fixtures/mc-vocabulary/project.orm.json tests/fixtures/mc-vocabulary/clean.pop.json --format json"
    exit: 0
    note: "Expected narrated source state; not new evolve behavior."
  - command: ".venv/bin/python -m gnd check tests/fixtures/mc-vocabulary/project.orm.json tests/fixtures/mc-vocabulary/cycle.pop.json --format json"
    exit: 1
    note: "Expected narrated source state; not new evolve behavior."
  - command: ".venv/bin/python -m gnd check tests/fixtures/mc-vocabulary/combined.orm.json tests/fixtures/mc-vocabulary/v2-clean.pop.json --format json"
    exit: 0
    note: "Expected narrated source state; not new evolve behavior."
  - command: ".venv/bin/python -m gnd validate tests/fixtures/mc-vocabulary/repin-only.orm.json --format json"
    exit: 3
    note: "Expected narrated source state; not new evolve behavior."
  - command: ".venv/bin/python -m gnd validate tests/fixtures/mc-vocabulary/flattened-negative.orm.json --format json"
    exit: 0
    note: "Expected narrated source state; not new evolve behavior."
  - command: ".venv/bin/pytest -q 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_evolve_apply]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_evolve_preview]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_cmd_validate]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_evolve_emit_claim]' 'tests/test_rf5_commands.py::test_relocated_algorithm_and_qualification_are_unchanged[_evolve_error_exit]' --tb=short"
    exit: 1
    output: "5 failed in 0.33s"
    note: "Known red at actual phase base, not new failures and not waived by a green gate."
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC3-spec.md
    sha256: 0dd46dc6ca905c32ac907d6a4bc858d8a8f0a64bfbed0e4cd4d52f90a8b96ad8
  - path: tests/fixtures/mc-vocabulary/README.md
    sha256: 2ef28885fc6b703e164f122a6deedacd3538da251e4c7a85fb2a43db8b5769e8
  - path: tests/fixtures/mc-vocabulary/answers.json
    sha256: a5511a56355b8268bda19c2cb703c0e679738a91329419fba0fc46ef43eb9b54
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/gate-manifest.json
    sha256: 83f978bc5eb20caff11399749ba1af804eddf79984f302c371f078ca37e1f3b7
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/baseline-known-red.json
    sha256: 18e9b3e1ca9d3ab9e8d13c1534c2d1f4eee3da83b0679d51525d247392fcd517
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/baseline-known-red-bodies.json
    sha256: 3641cceb35aa13798cdb088b08e278b91b65d5fa30410c242ccd840fe18e9239
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/acceptance-band-controls.json
    sha256: 917762ec9c137b1eddd5f50804965a113727903a16230e8b4ab6991afa98104c
---

# Claim

Delegated approval (auto=true),2026-11-10, approves the exact MC3 spec and sixteen narrated corpus meanings before implementation. D1–D14 are ruled as written: corpus-first, no optional spec review, one independent Codex CLI diff reviewer plus at most one repair confirmation. Existing authenticated environment only; no repository env, panel or reviewer subagent.

## Gate output (verbatim)

    authored 16 stories; 5 existing source-state controls

    5 failed in 0.33s

The actual existing source states are v1 clean0, v1 cycle1, combined candidate check0, re-pin-alone validation3 and standalone flattened validation0. Exact command arguments/output are retained by source-state-controls.json. They establish reachable inputs, not implemented re-pin behavior. Two measured legacy acceptance-adapter controls return11; initial unapproved draft guesses of3 were corrected before this gate.

## Delegated decisions and implementability

Authority: the owner's current process-milestone model-composition auto instruction. This is an agent ruling under that delegation, not a claim the owner personally read these bytes. The named phase scope includes declared source/test/data/catalog and minimal single-home evolution grammar updates. Corpus-first earns its cost at this serialized-format, validation and exit-code boundary. All14 decision rows are ruled, including explicit owned attachment locators, all re-pins conservatively breaking, analysis-only existing radius schema1, authenticated historical overrides only for actual old repinned IDs, current candidate live verification, existing10MiB claim limit, typed input3, linked-project refusal while conformance remains unsupported, and preservation of the known-red historical pins.

The spec has exact private/public boundary signatures, per-boundary order, six standing-rule bindings and a branch test/verification ledger. One canonical resolver is extended; no consumer resolves independently. Include-free variants and old schema graphs remain frozen. Raw authored replay already exists and can reject a valid flattened replacement; an analysis carrier avoids fabricating a valid Model or ValidationEvidence. Corpus proposals are manually authored, with existing canonical JSON used only for identities. The combined attachment order matches deterministic delete/prune/append. Snapshot UTF8, serializer caps, additive/population address consumers and source fidelity were checked against their actual defining homes before approval.

The phase size stop remains600 source/900 test-support Python lines relative to5a083f46, including moved code and successor support. MC1's exception does not transfer. Broad default/census lanes are not selected here; final candidate/default and named census remain separately owner-authorized close obligations. Independent review budget is one first opinion plus one confirmation maximum; repaired bytes carry no earlier opinion by implication.

## Boundary

No MC3 runtime or test implementation existed at the gate. The five original body-pin failures remain failures; no historical evidence is rewritten or xfailed. This ruling supplies no merge authorization for MC2 or MC3, no final docs acceptance, multi-file atomicity, certification, publication, milestone close or issue closure. The adversarial review is one reviewer's reading, not a proof. MC2 is complete locally but its separate explicit merge request remains pending. Revised docs checkpoint014 remains on its own draft branch and awaits the business-page reaction.

## Open questions

- Land the new harness red, implement every admitted branch, run the actual focused consumer closure and retain the known-red comparison plus separate actual-base fidelity controls.
- If actual size exceeds600/900, pause for owner with measured counts before further source/test work.
- At close repair plan disjoint-files/defer-all-docs assumptions and calibrate estimates from actual work; preserve all census/guard and known-red boundaries.
- Final MC4 consumes the actual working re-pin example and both actual owner documentation reactions; final candidate/default+census and the explicitly selected one-reviewer close follow all required merges.
