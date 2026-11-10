---
milestone: model-composition
station: "MC3 authored evolution and proposal writers"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-MC3
date: 2026-11-10
gates:
  - command: "uv run pytest -q tests/test_mc3_evolution.py tests/test_mc3_source_observations.py tests/test_model_evolution.py tests/test_evolve_loading.py tests/test_evolve_references.py tests/test_evolution_conformance.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_evolve_source_document.py tests/test_evolve_shape_matches.py tests/test_public_evolution_drift_readers.py tests/test_public_evolution_version_graph.py tests/test_public_evolution_legacy_readers.py tests/test_public_legacy_evolution.py tests/test_discover.py tests/test_discover_fact_type_family.py tests/test_discover_type_evidence.py tests/test_discover_type_judgements.py tests/test_induced_provenance.py tests/test_ilp_bridge.py tests/test_ilp_rules.py tests/test_ilp_amie.py tests/test_ilp_asp.py tests/test_ilp_learners.py tests/test_ilp_llm.py --tb=short"
    exit: 0
    result: "1365 passed, 8 deselected in 178.07s (0:02:58)"
  - command: "uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_mc2_consumers.py tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf4_peripheral.py tests/test_rf9_ci_repairs.py tests/test_rf6_packages.py tests/test_rf6_query_policy.py tests/test_rf8_structure.py tests/test_rf1_layering.py tests/test_schema_sync.py tests/test_packaged_skills.py tests/test_skill_prose_sync.py --tb=short -rs"
    exit: 0
    result: "1820 passed in 83.28s (0:01:23)"
  - command: "uv run pytest -q tests/test_rf5_commands.py --tb=short"
    exit: 1
    result: "5 failed, 258 passed in 3.16s"
  - command: "uv run ruff check src tests --output-format json"
    exit: 1
    result: "exact thirteen baseline findings"
  - command: "uv run python scripts/components_index.py --check --strict"
    exit: 0
    result: "generated index current"
  - command: "uv run python scripts/components_index.py changed --base 5a083f469d0a14271c3417401c6ae2fd046a165a --strict"
    exit: 0
    result: "reread: subsystem.check (entry not edited): its members changed: model.loading\nreread: subsystem.synth (entry not edited): its members changed: model.loading\nreread: subsystem.codegen (entry not edited): its members changed: model.loading\nreread: subsystem.conformance (entry not edited): its members changed: model.loading\nreread: subsystem.measure (entry not edited): its members changed: model.loading\nreread: subsystem.evolve (entry not edited): its members changed: cli.evolve_command, evolve.command, evolve.service, model.loading, evolve.policy, evolve.schema\nreread: subsystem.recovery (entry not edited): its members changed: model.loading\nchanged against 5a083f469d0a14271c3417401c6ae2fd046a165a (5a083f4): 132 file(s) differ; 0 to fix, 0 warning(s), 7 to reread"
  - command: "git diff --check 5a083f469d0a14271c3417401c6ae2fd046a165a"
    exit: 0
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  disposition: "not selected for this phase; named final beast-3 default/census authority persists"
evidence:
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC3-spec.md
    sha256: 046883e33f15c43769bd5ec6906923912f3218e153a6bd329eeec2522e936f57
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/completion-source-manifest.json
    sha256: aa6a74276b43b3774c84d6e87cc61dade3d7fb06039b0cb059f6a4ac41712517
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/completion-evidence-manifest.json
    sha256: 0471bdd2306fccc01a1156056e363464a00d2f3aafc712306fe93889a4347d48
  - path: .gnd-planning/milestones/model-composition/evidence/MC3/completion-ruling.json
    sha256: e0a2370c6cf778840cb361b77f1426f1f3f6c4b279b7ebd37d6bcdb042525229
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC3-codex-review.md
    sha256: f96e364aea458f71340794330c189e4d031ac9acadcffc59d9160389b41de6d0
  - path: .gnd-planning/milestones/model-composition/notes/phase-MC3-codex-confirmation.md
    sha256: a722cddeaa2e352c72c130d2b914ac967e7f3e40a9be3fd901b69c74a11be212
  - path: .gnd-planning/milestones/model-composition/015-MC3-gate.md
    sha256: a7c3f738bc57927ed213c7563537176563af25f47a8938e6f56921e47d159c97
  - path: .gnd-planning/milestones/model-composition/018-MC3-owner-resume.md
    sha256: c985d5e61eee7660eb60bf4a6c54bf1d481b8eed19f7cc9b1e2b59a28a9299cc
  - path: .gnd-planning/milestones/model-composition/021-MC3-apply-order-amendment.md
    sha256: e1856af528e6cff973a670fdc18b54cc03f44bcb2ac3c6ca50f744e80a63e3d9
  - path: .gnd-planning/milestones/model-composition/022-MC3-review-repairs.md
    sha256: a31cdff10ad5ddc1e3cf74d3d535cfad1ecc1a545c399ab1531a56ac7827b2b1
---

# Claim

MC3's four criteria are complete at reviewed source ebec0980005690f6e23e5e4e806fdfc50b96de85. The primary gate exited0 with 1,365 passes/8 configured deselections; compatibility exited0 with 1,820 passes. They overlap and are not summed. The selected RF5 gate exited1 with exactly the five baseline failures and 258 other passes; lint exited1 with exactly the same 13 baseline locations. One Codex CLI reviewer reported two reproduced repairs and its single bounded confirmation approved the repaired source. Delegated acceptance (auto=true),2026-11-10, accepts this phase with these explicit boundaries; it is not the owner's personal reading or merge authorization.

## Criteria and coverage

| Criterion | Measured result |
|---|---|
| MC3-C1: included definitions remain read-only; own rules remain editable | Included element/role/constraint refusals, owned-host replay, identical anonymous constraints, global duplicate occurrences across entries, deterministic append/prune, D12, policy and population placement controls pass. Included-prefix offsets and deletion identity are distinguished. |
| MC3-C2: re-pin, historical evidence, analysis and recovery | Combined re-pin+rule repair previews and publishes; invalid re-pin produces only an existing analysis radius and cannot authorize apply. Exact acceptance, bound raw snapshots, original parser suffix, missing/overwritten old input recovery, unsafe existing path refusal, live untouched/candidate checks, pre-CAS ordering, retry/finalize and linked-route refusal pass. Canonical/pretty/analysis caps and actual near-cap reopen pass without raising limits. |
| MC3-C3: proposal writers retain the authored includer | Actual discover proposal → preview/apply/finalize, class-label ILP export/import → preview, and mined-rule export/import → preview preserve includes, emit own additions and omit copied vocabulary definitions. Unrooted generic loading and all other closed currency routes stay refused. |
| MC3-C4: end-to-end shared vocabulary example | The frozen component corpus checks the old clean/cycle states, names the broken project ring after a re-pin alone, excludes the unaffected owner rule, then repairs the rule in the same accepted re-pin and checks the final population. Exact authored candidate equality and unchanged vocabulary bytes are asserted. The owner-selected higher-level expense story belongs to final MC4. |

The spec's T1–T18 branch table is discharged by the primary/impact selections and their named successors. Hostile rename dictionary identities reproduced70 before the totality repair and now refuse3; list controls remain refusals. The isolated new ownership/dependency layer processes20,000 elements and20,000 operations under its 3-second limit, excluding loading. This is the measured bound on this host, not a general complexity guarantee.

## Review and repairs

One reviewer is one reviewer. Codex CLI 0.163.0 used gpt-6.1-sol/xhigh in an ephemeral read-only session, then one bounded confirmation. The first review independently executed 25 selected checks and small probes. Finding 1 allowed discover's report to target a vocabulary; finding 2 omitted the model CAS path from historical dependency exclusion. Both were reproduced before fixes. Four regressions failed at c93506e2 and passed after reusing the shared exclusion over discover's outputs and adding the model destination to evolution's tuple. Record 022 retains severity versus relevance triage; its command parentheticals label before/after states, while the attached JSON gives the literal commands.

The confirmation approved exact scope c93506e2..ebec0980. Its mocked writer/storage probes compared base and repaired behavior, include-free bytes, aliases, staging, retry/finalize and normal publication. Its four pytest cases failed during fixture setup because the sandbox had no writable temporary directory; those are not independent passes. The reviewer did not rerun the supplied large gates, real filesystem recovery/races or cap fixtures. Parent real-filesystem gates supply that evidence. Two rounds exhaust the phase budget. Later changes are this record, navigation and bound evidence only; reviewed production/test bytes remain unchanged.

## Refactoring review

Refactors EXECUTED:

- Factored the existing warning/structural/semantic validation into _model_warnings so valid loading and invalid analysis share the same policy. The public loader still constructs Models only after successful validation.
- Factored the existing reference-ownership declaration policy into _validate_reference_document in the same defining home. Public validate_declarations keeps its defining identity and delegates; the exact MC1-to-MC3 body successor and dirty controls retain its history.
- Extracted existing candidate ValidationEvidence construction into _validation_for so the canonical include candidate path uses the same warning/evidence shape as the old candidate loader.

The new includes worker owns evolution metadata, attachment replay and output exclusions; canonical resolution remains model.loading. Discover/ILP use the existing writer and replay rather than introducing another renderer or resolver. Population placement reuses the existing identity-based position lookup with one verified prefix/owned-host view. The layer map assigns the new home with zero allowances. No further structural change was needed within this phase's boundary.

Seven subsystem entries were reread against their changed model-loading/evolution members: check, synth, codegen, conformance, measure, evolve and recovery. Their declared component membership, flow and output boundaries remain accurate; the new worker belongs to the existing evolve.service component. All changed module-level entries were updated and regenerated. No unrecorded component exemption was introduced.

## Fidelity and implementation findings

All historical evidence remains retained. The single reference-validator definition successor authenticates MC1's separate definition artifact; it is not incorrectly inserted before that change. Current source/query/CLI/link inventories have dirty controls. Five actual-base body observations are separate from the five deliberately still-red historical RF5 pins. No new ModelIndex exception, runtime layer allowance, identity algorithm or installed discovery-link edit is introduced.

Records 015/016/017/018/021/022 retain the corpus gate, measured locator correction, mandatory size pause, explicit 1,400/1,400 owner ruling, apply-order implementability amendment and reproduced review repairs. Current conservative count is 1,109 source/config lines and 1,218 test/support lines. The old 600/900 stop and 615/251 pause remain historical facts. All 16 corpus meanings remain unchanged; only the two measured locator digests changed in amendment 016. Final normative evolution prose was updated in its one existing home with one exact skill-link edge; workflow/nav/release integration remains MC4.

Intermediate files with names such as final-impact describe their earlier executions; the review-repair-* artifacts bind the final gates to ebec0980. The completion manifests bind all current sources and evidence. The initial sandbox uv-cache build refusal is not a runtime failure; the final selected wheel-build consumer ran with normal cache access. Current local interpreter is Python3.11.15; earlier evidence keeps its own recorded interpreter.

## Boundary

This completes MC3 locally and records delegated phase acceptance. It does not merge a PR, publish a release, certify a model/project or close the milestone. The owner's earlier merge authorizations applied only to PR #154 and PR #156. The six full-default baseline failures remain inherited; this phase directly remeasures the five relevant RF5 failures and does not claim a current full-default comparison. The final named beast-3 default/census run, actual main-branch exit predicates and separate independent close review are still owed. Unselected historical/native/external/certification lanes are not reported as passing.

Only the authored includer is the model CAS leaf. Included paths and aliases are excluded from preview, analysis, model, verbalization and stage outputs as applicable. Historical bytes authenticate only actual old re-pins; untouched and candidate dependencies remain live. Verification is as of captured reads; no multi-file atomicity guarantee is made. Include-bearing linked-project evolution, codegen/conformance currency, generic recovery and unselected routes remain refused.

## Open questions and carryovers

| Row | Disposition / target |
|---|---|
| MC3 merge | Pending explicit owner decision on the completed PR's fixed head; no merge authority inferred from auto. |
| Final MC4 | Use Fable's accepted expense-story direction. The owner's actual reaction was “Yes, this explains it”; record 021 preserves that direction acceptance, not byte/merge approval. Integrate the implemented re-pin workflow, skills, navigation, runnable commands, release notes and exact R30 example successor. PR #155 remains a separate draft until its gates and owner merge decision. |
| Plan repairs | Coordinator at milestone close: corpus digest convention, actual phase overlap/dependencies and same-phase minimum normative updates, component-index premise, measured stops/exceptions, owner-selected expense example and actual documentation reactions. Prior phase records supply the other named repairs; do not rewrite the canonical plan during a phase. |
| Final assurance | Named final candidate/default and census comparison on beast-3, one explicitly selected Codex CLI close reviewer overriding the panel, inherited-question sweep, actual main exit predicates and issue 95 closure only after completion. |
