# ILP-learners skill-surface census

One row per packaged skill file (`git ls-files src/gnd/skills`), 65 files,
measured at IL6 against the milestone base (the parent of `07f4d45`, the first
IL1 commit). "Changed" names every phase of this milestone whose commit changed
the file, or `no`. `tests/test_il6_skill_census.py` asserts that every packaged
file appears here exactly once and that each cell equals what git records;
commits of other milestones merged into the window are not counted.

The milestone added learner adapters to the ILP bridge: `ilasp` (IL2), `rules`
(IL3), `amie` with `gnd import mined-rules` (IL4) and `llm` (IL5), ran Popper
against a real learner (IL1), and compared all of them on committed real runs
(IL6). A file is unchanged when none of these alters the behaviour or format it
documents. The two pin sites the plan names were edited in IL6, and the review (R3) found a third, gnd-solve's Station 6 route.

| Path | Changed | Why, or why no change was needed |
|---|---|---|
| src/gnd/skills/gnd-adopt/SKILL.md | no | GSD migration maps requirements to imported provenance; it reads no learner output and writes no induced proposal |
| src/gnd/skills/gnd-adopt/migration.schema.json | no | GSD migration maps requirements to imported provenance; it reads no learner output and writes no induced proposal |
| src/gnd/skills/gnd-adopt/references/gsd-environment-cleanup.md | no | GSD migration maps requirements to imported provenance; it reads no learner output and writes no induced proposal |
| src/gnd/skills/gnd-adopt/references/gsd-mapping.md | no | GSD migration maps requirements to imported provenance; it reads no learner output and writes no induced proposal |
| src/gnd/skills/gnd-adopt/scripts/verify_migration.py | no | GSD migration maps requirements to imported provenance; it reads no learner output and writes no induced proposal |
| src/gnd/skills/gnd-codegen/SKILL.md | no | generates code from a model; an induced constraint is generated like any other once evolve admits it, and no learner target changes that |
| src/gnd/skills/gnd-codegen/references/architecture-contract.md | no | generates code from a model; an induced constraint is generated like any other once evolve admits it, and no learner target changes that |
| src/gnd/skills/gnd-codegen/references/codegen-contract.md | no | generates code from a model; an induced constraint is generated like any other once evolve admits it, and no learner target changes that |
| src/gnd/skills/gnd-conformance/SKILL.md | no | checks a generated project against its model; the milestone adds no derived file or assertion |
| src/gnd/skills/gnd-conformance/references/conformance-contract.md | no | checks a generated project against its model; the milestone adds no derived file or assertion |
| src/gnd/skills/gnd-dev-session/SKILL.md | no | the session contract binds inputs and a verifier; no learner adapter is a session adapter |
| src/gnd/skills/gnd-dev-session/references/judgment-contract.md | no | the session contract binds inputs and a verifier; no learner adapter is a session adapter |
| src/gnd/skills/gnd-dev-session/references/session-v7-contract.md | no | the session contract binds inputs and a verifier; no learner adapter is a session adapter |
| src/gnd/skills/gnd-export/SKILL.md | IL6 | pin site: names the `popper`, `neutral`, `ilasp`, `rules` and `amie` targets, `--target llm` and `gnd import mined-rules` |
| src/gnd/skills/gnd-export/references/export-contract.md | no | the Lean, witness and Souffle export contracts; the ILP bridge is documented in the skill file and the bridge reference, not here |
| src/gnd/skills/gnd-export/references/witness-contract.md | no | the Lean, witness and Souffle export contracts; the ILP bridge is documented in the skill file and the bridge reference, not here |
| src/gnd/skills/gnd-export/references/witness.schema.json | no | the Lean, witness and Souffle export contracts; the ILP bridge is documented in the skill file and the bridge reference, not here |
| src/gnd/skills/gnd-extract/SKILL.md | no | extracts a population from a document; unaffected by the ILP bridge |
| src/gnd/skills/gnd-extract/references/extraction-contract.md | no | extracts a population from a document; unaffected by the ILP bridge |
| src/gnd/skills/gnd-model-evolve/SKILL.md | IL6 | pin site: a `gnd import mined-rules` proposal is reviewed beside `gnd import ilp-rules` and `gnd discover` ones |
| src/gnd/skills/gnd-model-evolve/references/evolution-contract.md | no | the evolution contract is source-agnostic: a mined-rules proposal uses the same operations, CAS and review as any other |
| src/gnd/skills/gnd-model-from-code/SKILL.md | no | recovers a model from code; it never consumes a learner's output |
| src/gnd/skills/gnd-model-from-code/references/recovery-contract.md | no | recovers a model from code; it never consumes a learner's output |
| src/gnd/skills/gnd-model-from-text/SKILL.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/USAGE.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/README.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/cases.json | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/expected/synthetic_good_user.orm.yaml | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/dialogue.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/evals/reviewability_checklist.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.dialogue.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.orm.yaml | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/movie_catalog.dialogue.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/movie_catalog.orm.yaml | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.dialogue.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.dialogue.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/references/csdp-workflow.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/references/dialogue-patterns.md | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-model-from-text/scripts/validate_model.py | no | authors a model from dialogue; induced rules arrive only through evolve, never here |
| src/gnd/skills/gnd-new-project/SKILL.md | no | scaffolds .gnd-planning; unrelated to the bridge |
| src/gnd/skills/gnd-orm-core/SKILL.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/constraint-inference.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/constraint-reference.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/coverage-and-element-addressing.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/halpin-posture.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/milestone-record-format.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/population-format.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/population.schema.json | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/representation-format.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/steps.schema.json | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md | no | the format library; the milestone adds no provenance source, field or constraint kind (mined rules use the existing induced source and guarded constraints) |
| src/gnd/skills/gnd-render-doc/SKILL.md | no | renders documents from populations; unaffected |
| src/gnd/skills/gnd-render-doc/references/rendering-contract.md | no | renders documents from populations; unaffected |
| src/gnd/skills/gnd-review-panel-light/SKILL.md | no | the lighter panel profile; unchanged for the same reason as the full panel |
| src/gnd/skills/gnd-review-panel/SKILL.md | no | the advisory panel; the milestone changes no seat, input class or contract |
| src/gnd/skills/gnd-review-panel/references/review-contract.md | no | the advisory panel; the milestone changes no seat, input class or contract |
| src/gnd/skills/gnd-solve/SKILL.md | IL6 | Station 6 lists where a proposal may come from; it now names `gnd import mined-rules` beside `gnd discover` and `gnd import ilp-rules` (IL6 review R3) |
| src/gnd/skills/gnd-update-review-panel/SKILL.md | no | maintains reviewer CLIs; unrelated to the bridge |
| src/gnd/skills/gnd-update-review-panel/agents/openai.yaml | no | maintains reviewer CLIs; unrelated to the bridge |
| src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py | no | maintains reviewer CLIs; unrelated to the bridge |
