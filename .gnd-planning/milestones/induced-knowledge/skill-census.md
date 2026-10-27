# Induced-knowledge skill-surface census

One row per packaged skill file (`git ls-files src/gnd/skills`), 65 files,
measured at IK6 against the milestone base (the parent of `6f07035`, the first
IK1 commit). "Changed" names every phase whose commit changed the file, or
`no`. `tests/test_ik6_skill_census.py` asserts that every packaged file appears
here exactly once and that each changed cell names a phase.

The milestone added four capabilities: object-type descriptions (IK1), induced
provenance and its admission (IK2), `gnd discover` (IK4) and the ILP bridge
(IK5, with IK4-Q2 binding references in evolve). A file is unchanged when none
of these alters the behaviour or format it documents.

| Path | Changed | Why, or why no change was needed |
|---|---|---|
| src/gnd/skills/gnd-adopt/SKILL.md | no | GSD migration maps requirements to imported provenance; it never emits induced constraints, descriptions or proposals |
| src/gnd/skills/gnd-adopt/migration.schema.json | no | the migration record's schema; no milestone field enters it |
| src/gnd/skills/gnd-adopt/references/gsd-environment-cleanup.md | no | manual GSD cleanup checklist; unrelated to model content |
| src/gnd/skills/gnd-adopt/references/gsd-mapping.md | no | maps GSD ids to model elements; the source list it uses (imported and its dispositions) is unchanged |
| src/gnd/skills/gnd-adopt/scripts/verify_migration.py | no | verifies the mapping's digests; reads no induced or description field |
| src/gnd/skills/gnd-codegen/SKILL.md | IK6 | the tools.py row now says a docstring's role line carries the object type's description summary (behaviour added in IK1) |
| src/gnd/skills/gnd-codegen/references/architecture-contract.md | no | the extension architecture declaration; codegen's derived-file set is unchanged |
| src/gnd/skills/gnd-codegen/references/codegen-contract.md | no | ownership and regeneration rules; descriptions change docstring text, not the contract |
| src/gnd/skills/gnd-conformance/SKILL.md | no | conformance checks digests and structure; no milestone change reaches its four assertions |
| src/gnd/skills/gnd-conformance/references/conformance-contract.md | no | as above |
| src/gnd/skills/gnd-dev-session/SKILL.md | IK6 | names `gnd measure MODEL --labels MANIFEST` beside `--populations` (IK3's label mode) |
| src/gnd/skills/gnd-dev-session/references/judgment-contract.md | no | external-judgment contract; no milestone change touches judgments |
| src/gnd/skills/gnd-dev-session/references/session-v7-contract.md | no | session contract versions; no new contract field |
| src/gnd/skills/gnd-export/SKILL.md | IK6 | one paragraph: `gnd export ilp` is the ILP bridge, not a derivation export, and its import is an evolve proposal |
| src/gnd/skills/gnd-export/references/export-contract.md | no | the Lean and Souffle export boundary; the ILP bridge is documented in docs/reference/ilp-bridge.md, not here |
| src/gnd/skills/gnd-export/references/witness-contract.md | no | the witness certificate contract; unchanged |
| src/gnd/skills/gnd-export/references/witness.schema.json | no | certificate schema version 1; unchanged |
| src/gnd/skills/gnd-extract/SKILL.md | IK1 | the verbalization row names object-type description content |
| src/gnd/skills/gnd-extract/references/extraction-contract.md | no | inspected at IK6: it never states the vocabulary text's contents, so IK1's description keys need no line here |
| src/gnd/skills/gnd-model-evolve/SKILL.md | IK2, IK4, IK5 | the seven-source taxonomy and reviewed admission (IK2); reviewing `gnd discover` proposals (IK4) and `gnd import ilp-rules` proposals (IK5) |
| src/gnd/skills/gnd-model-evolve/references/evolution-contract.md | IK1, IK2, IK4-Q2, IK-close | description changes in a proposal (IK1); induced status changes (IK2); reference binding and its exits (IK4-Q2); the `operation` surface listed (IK-close, IK1-Q5) |
| src/gnd/skills/gnd-model-from-code/SKILL.md | IK2 | recovery emits five of seven sources, and says why induced is not one |
| src/gnd/skills/gnd-model-from-code/references/recovery-contract.md | no | the recovery bundle contract; recovery emits no induced constraint |
| src/gnd/skills/gnd-model-from-text/SKILL.md | IK2 | the seven-source taxonomy reference |
| src/gnd/skills/gnd-model-from-text/USAGE.md | no | usage notes for the dialogue workflow; no new source it emits |
| src/gnd/skills/gnd-model-from-text/evals/README.md | no | eval harness notes; eval cases are unchanged |
| src/gnd/skills/gnd-model-from-text/evals/cases.json | no | eval cases; descriptions are optional, so the expected models stay valid |
| src/gnd/skills/gnd-model-from-text/evals/expected/synthetic_good_user.orm.yaml | no | an expected model; valid unchanged, since every milestone field is optional |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md | no | fixture notes; unchanged |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/dialogue.md | no | fixture dialogue; unchanged |
| src/gnd/skills/gnd-model-from-text/evals/reviewability_checklist.md | no | review checklist; no milestone element to review in dialogue output |
| src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.dialogue.md | no | worked example; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/library_with_subtypes.orm.yaml | no | worked example model; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/movie_catalog.dialogue.md | no | worked example; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/movie_catalog.orm.yaml | no | worked example model; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.dialogue.md | no | worked example; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/objectification_in_enrollment.orm.yaml | no | worked example model; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.dialogue.md | no | worked example; valid unchanged |
| src/gnd/skills/gnd-model-from-text/examples/reference_scheme_elicitation.orm.yaml | no | worked example model; valid unchanged |
| src/gnd/skills/gnd-model-from-text/references/csdp-workflow.md | no | the CSDP steps; dialogue modelling does not induce rules |
| src/gnd/skills/gnd-model-from-text/references/dialogue-patterns.md | no | dialogue patterns; unchanged |
| src/gnd/skills/gnd-model-from-text/scripts/validate_model.py | no | calls gnd validate; validation of new fields lives in GND |
| src/gnd/skills/gnd-new-project/SKILL.md | no | scaffolds .gnd-planning; no model content |
| src/gnd/skills/gnd-orm-core/SKILL.md | IK2 | the seven-source taxonomy reference row |
| src/gnd/skills/gnd-orm-core/references/constraint-inference.md | no | common-sense inference guidance; induced constraints come from commands, not this guidance |
| src/gnd/skills/gnd-orm-core/references/constraint-reference.md | IK1 | the anchor sidecar's vocabulary digest excludes descriptions |
| src/gnd/skills/gnd-orm-core/references/coverage-and-element-addressing.md | IK2 | the coverage payload's induced list |
| src/gnd/skills/gnd-orm-core/references/halpin-posture.md | no | modelling posture; unchanged |
| src/gnd/skills/gnd-orm-core/references/milestone-record-format.md | no | the record format; this milestone's records follow it unchanged |
| src/gnd/skills/gnd-orm-core/references/orm-meta.schema.json | IK1, IK2 | the description object (IK1) and the induced source with its induction block (IK2) |
| src/gnd/skills/gnd-orm-core/references/population-format.md | no | population format; label manifests are documented in docs/reference/measure-labels.md |
| src/gnd/skills/gnd-orm-core/references/population.schema.json | no | population schema; unchanged |
| src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md | IK2 | the seven-source taxonomy and the induced provenance shape |
| src/gnd/skills/gnd-orm-core/references/representation-format.md | IK1, IK2 | the description keys, limits and rendering (IK1); induced in the representation (IK2) |
| src/gnd/skills/gnd-orm-core/references/steps.schema.json | no | plan steps schema; unchanged |
| src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md | IK1 | the description sentence in the verbalization |
| src/gnd/skills/gnd-render-doc/SKILL.md | no | renders documents from the constraint-blind verbalization; description lines flow through it without a workflow change |
| src/gnd/skills/gnd-render-doc/references/rendering-contract.md | no | rendering obligations; unchanged |
| src/gnd/skills/gnd-review-panel-light/SKILL.md | no | review panel; unrelated |
| src/gnd/skills/gnd-review-panel/SKILL.md | no | review panel; unrelated |
| src/gnd/skills/gnd-review-panel/references/review-contract.md | no | review contract; unrelated |
| src/gnd/skills/gnd-solve/SKILL.md | IK4, IK5 | station 8 names discover (IK4) and import ilp-rules (IK5) as proposal sources |
| src/gnd/skills/gnd-update-review-panel/SKILL.md | no | panel maintenance; unrelated |
| src/gnd/skills/gnd-update-review-panel/agents/openai.yaml | no | panel adapter; unrelated |
| src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py | no | panel maintenance; unrelated |

## Gap recorded at IK6

No packaged skill runs `gnd measure --labels`, `gnd discover`, `gnd export ilp`
or `gnd import ilp-rules` as a workflow. They appear only as pointers
(gnd-dev-session, gnd-export, gnd-solve) and as proposal sources that
gnd-model-evolve reviews. The tutorial therefore shows those steps as plain
requests to Claude Code. A skill for this loop would be new scope; it is
recorded as open question IK6-Q1 in the IK6 record.
