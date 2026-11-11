---
milestone: guarded-rule-workflows
station: milestone-close
skill: "n/a -- repository development under process-milestone auto=true"
scope: milestone-close
date: 2026-11-11
gates:
  - command: "python -m pytest -q tests/test_guarded_diagnostics.py tests/test_model_guarded.py tests/test_public_semantic_guarded.py tests/test_public_semantic_guarded_join.py tests/test_public_guarded_consequent_matrix.py tests/test_rule_edition_comparison.py tests/test_rc1_rule_ids.py tests/test_rc3_baseline.py tests/test_rc4_allow_vacuous.py tests/test_report_json.py tests/test_rf5_commands.py tests/test_rf1_cli_pins.py tests/test_public_semantic_boundaries.py tests/test_rf1_layering.py tests/test_rf6_query_policy.py tests/test_development_scaffold.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "836 passed, 1 deselected in 94.26s (0:01:34)"
  - command: "uv run python tools/run_gnd_review_panel.py gw-close-review-request.json --out gw-close-panel --reviewer-timeout 600 --overall-timeout 900"
    exit: 0
  - command: "gnd review finalize gw-close-panel gw-close-synthesis.json --out GW-CLOSE-PANEL-REVIEW.md"
    exit: 0
  - command: "delegated approval (auto=true)"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/guarded-rule-workflows/001-plan-gate.md
    sha256: 2a53bf06e0440e8932af5b1d8e460d55d867148634b61afa25537b62664d772b
  - path: .gnd-planning/milestones/guarded-rule-workflows/003-phase-GW0.md
    sha256: 180a3c213e3177e8f5ad0c484da3e5e3d9b22490354383c17b24db6b58e203b0
  - path: .gnd-planning/milestones/guarded-rule-workflows/005-phase-GW2.md
    sha256: 5d9a90e10d28accb96ed4490d04c94cd44cdcc1b5039fe5e5384c581c0ec8f85
  - path: .gnd-planning/milestones/guarded-rule-workflows/notes/close-outcome.md
    sha256: d3360e1176a781c15578fdfe1c8670bad5080dd50c591c48c3d8f34daa9eda2f
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/close/panel-review.md
    sha256: e357367c057d4c64dd46d3d5af3ce33ac10fc3a28daa7d5e6b03521a2efcd9a0
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW2/installed-smoke.json
    sha256: 766961b9bf72c2da7c81af67a7ac8558c6ab5ea7c2714250b69caa71041112a5
  - path: .gnd-planning/milestones/guarded-rule-workflows/evidence/GW2/installed-smoke-replay.md
    sha256: b01c18af58c90f499f0b4bedddfca6288ca486eacd38cf63449864d2e5a0f6e7
  - path: tests/test_rule_edition_comparison.py
    sha256: d55dfea1e47c7c7f2f5f7c98ec9192859e7b2767d4773d37d42dcdd456f97031
---

# Milestone close

**Delegated close approval (auto=true), 2026-11-11.** The owner's scoped
milestone invocation and standard panel selection authorize this local
close. GW0 and GW2 satisfy the [reviewed plan](notes/guarded-rule-workflows-plan.md).
The phase records are [GW0](003-phase-GW0.md) and [GW2](005-phase-GW2.md).
The candidate runtime is `e02345d375b21361a5aa0633d748043d381e93fe`.
The closing rerun used the same runtime bytes with the additional
repeated-fact-type regression listed in the evidence. It used the workspace
Python with PYTHONPATH set to this checkout's src directory. One selected
test was deselected by the default lane filter.

- **GR-D12.** The installed plain snapshot check exited 0, reporting zero
  bindings and empty atom 0 for the antecedent typo, and one binding for
  the consequent typo. Installed validate exited 0 with a located advisory
  warning for each literal. The E4 parity test
  `test_populated_antecedent_without_coverage_keeps_exact_count` compares
  v15 fields and bands directly. RC1, RC3 and RC4 pin the prior rule-ID,
  population-baseline and vacuity behavior.
- **GR-D9.** The installed comparison exited 0 while both check bands
  were 1, with 42 base-only, one standing and no head-only binding.
  The comparison returns 3 for ill-formed or incompatible input and 4
  for an incomplete comparison. Its controls include malformed data,
  unresolved bindings, work exhaustion and the reversed direction.
- **Installation and impact.** The [smoke replay](evidence/GW2/installed-smoke-replay.md)
  identifies the lock, exact input bytes, wheel build and install commands
  and installed CLI invocations for both workflows. The strict component
  check, Ruff, architecture, query inventories and scaffold checks exited 0.

## Close review and dispositions

The standard close panel reviewed the [close outcome](notes/close-outcome.md)
at commit `620785bd`, SHA-256
`d3360e1176a781c15578fdfe1c8670bad5080dd50c591c48c3d8f34daa9eda2f`.
The [finalized report](evidence/close/panel-review.md) binds run SHA-256
`4c8fbd8b864bd60791490248da538e3c5b780175ca77e64760da24e3f091669d`.
Five of six seats returned complete, valid responses. Codex, Gemini and
GLM approved. Claude and Qwen requested revisions to the evidence.
Kimi's approval contained unread lines and failed validation. Qwen's
warning-severity concern had no measured evidence anchor. The other
nine retained concerns were anchored. The project reviewer bar was met.

| Concern | Disposition |
|---|---|
| Candidate-bound counts, Claude and Qwen | Re-ran the union of both phase selections and impact checks on the final runtime. The first GW0 counts were measured before GW2. GW2 repaired the GW0 RF5 source pin. |
| Installed smoke reproducibility, Claude | Recorded all build, lock, installation and CLI arguments plus input and output hashes. |
| GW2 repair scope, Claude | The independent phase review covered `05b56ed5`. The `e02345d3` repairs were verified by red/green tests and this close review. The repeated-fact-type test reproduces the false standing result on `05b56ed5` and withholds the delta with exit 4 on `e02345d3`. |
| GW0 warning severity, Qwen | The delegated spec selects a located advisory finding. The installed smoke pins the two warnings, check counts and empty-prefix index with exit 0. |
| GW2 exit contract, Qwen | The reference and close record name 0 for completed, 3 for invalid and 4 for incomplete comparisons. Public tests exercise all three. |
| GW0 post-review controls, Qwen | The additional indexed join call-count test and negative schema mutation were added after the phase reviewer read `24c72d86`. The final union includes both. |
| Version-15 compatibility anchor, Qwen | The E4 parity test and RC1/RC3/RC4 pins are identified above and included in the final union. |
| GW0 installation pointer, Qwen | The combined smoke explicitly reports installed GW0 entrypoint behavior, warning locations and the version-16 payload. |
| Deferred tracking, Qwen | The open-question sweep names the original issues and the governing plan scope. |

These dispositions add evidence for existing claims and leave the
reviewed runtime unchanged. The report retains each review concern.
The initial plan-panel launch was rejected by automatic approval review
because it treated the plan as internal. An anonymous GitHub check matched
the exact public plan bytes, and the subsequent approved runs used clones
of the public branch.

## Open-question sweep

| Question | Disposition |
|---|---|
| GW0 report surface and validation budget | Closed for plain rule-ID checks. The opt-in v16 report and 100,000-unit advisory walk are covered by GW0. |
| Legacy guarded message-count path | Carried to a future report-compatibility milestone if selected. The GND maintainers retain ownership. |
| GW2 binding identity and comparison budget | Closed for the supported same-vocabulary scope, with explicit incomplete outcomes for unsupported alignments and exhaustion. |
| Broader guarded report routes and cross-vocabulary edits | Carried to the GND maintainers for a future scoped design if requested. |
| [GR-D8](https://github.com/vasiloglou/gnd-public/issues/179) | Deferred under the approved plan. The issue author retains the generated-case request. |
| [GR-D10](https://github.com/vasiloglou/gnd-public/issues/181) | Deferred under the approved plan. The issue author retains the discovery request until a project asks for it. |
| [GR-D11](https://github.com/vasiloglou/gnd-public/issues/182) | Deferred under the approved plan. The issue author retains the miner-route request. |

## Refactoring review

GW0 consolidated canonical scalar conversion in `gnd.values`, retaining
its previous identity alias. GW2 reuses canonical baseline row identity
and ordinary checker admission through the existing API gateway. No
additional refactor is required for the closing scope.

## Boundary

This is the local milestone close on draft PR #184. Merge, publication and
certification remain separate owner actions. Historical and external
acceptance lanes were outside the selected verification scope.
