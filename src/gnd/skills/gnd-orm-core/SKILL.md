---
name: gnd-orm-core
description: The ORM-YAML and population format reference library for GND — the single source of truth for the model.orm.yaml spec, constraint vocabulary, provenance/modality policy, verbalization patterns, and population interchange format. Consult when authoring, validating, or checking GND models, or when any skill needs the "ORM YAML format", "model.orm.yaml spec", "population format", "constraint reference", "provenance taxonomy", or "modality policy". References-only — no workflow steps; modeling workflows live in sibling skills (gnd-model-from-text) that link here.
---

# GND ORM Core References

This skill is a **references-only library** (D-07): the single source of truth every GND skill and the `gnd` runtime read for the ORM 2 format, constraint semantics, and population interchange. Other skills link to these files rather than duplicating spec text — a workflow may state its own narrower restriction (which sources it emits, which bands it can return), but the complete vocabulary is stated once, here, and a restated fragment elsewhere is a defect.

There are no workflow steps here. To *build* a model, use `gnd-model-from-text`; to validate or check one, use `gnd validate|check`.
An existing `rai-orm-from-schema` artifact is a dialect-import route, not a
model-authoring workflow: use `gnd import rai-orm MODEL --out OUT_DIR`, then
validate the resulting `model.orm.yaml`.

## Workflow index

Routing only. This skill acquires no workflow steps by listing them, and none of these skills may copy spec text out of `references/` — they link to it, so spec text keeps one home (D-07). Each row names the claim that workflow emits and the authority it does **not** hold, because a reader arriving from here is deciding which workflow to enter.

| Workflow | Enter it when | The claim it emits — and what it never does |
|---|---|---|
| [`../gnd-new-project/SKILL.md`](../gnd-new-project/SKILL.md) | a repository is becoming a GND project and has no `.gnd-planning/` | a one-time scaffold — `.gnd-planning/` with its `PROJECT.md` and first milestone directory, committed. It never re-scaffolds, never writes a station record, and never touches a `.planning/` another framework owns |
| [`../gnd-model-from-text/SKILL.md`](../gnd-model-from-text/SKILL.md) | no model exists yet and the source is natural language | a new `model.orm.yaml` + verbalization. It never edits an existing model — that is evolution |
| [`../gnd-model-evolve/SKILL.md`](../gnd-model-evolve/SKILL.md) | one valid model must change | a staged proposal, an accepted blast-radius report, a model CAS, and an immutable change record — four separate claims. It never regenerates linked code; a conformance drift finding is information, not permission (D-24) |
| [`../gnd-adopt/SKILL.md`](../gnd-adopt/SKILL.md) | a GSD project is migrating to GND | a recovered model whose mapped requirements carry `imported` provenance, a verified `model.migration.json`, and a printed manual cleanup checklist. It never re-runs incrementally, never writes into `.planning/`, and never automates environment cleanup |
| [`../gnd-model-from-code/SKILL.md`](../gnd-model-from-code/SKILL.md) | no model exists and the only source is an existing codebase | a **one-time** recovered model, verbalization, and recovery report. There is no watcher, no background index, and no continuous code-to-model synchronization (D-14) |
| [`../gnd-review-panel/SKILL.md`](../gnd-review-panel/SKILL.md) | a plan, experiment outcome, or spec/results/delta bundle needs independent readers | an **advisory** `PANEL-REVIEW.md`. It never edits a reviewed artifact and never applies a fix (D-22) |
| [`../gnd-review-panel-light/SKILL.md`](../gnd-review-panel-light/SKILL.md) | the same independent review is wanted at `high` or `medium` supported per-run effort | the same **advisory** `PANEL-REVIEW.md`, roster, quorum, evidence, and no-fix boundary as the quality-first panel |
| [`../gnd-update-review-panel/SKILL.md`](../gnd-update-review-panel/SKILL.md) | the five active reviewer CLIs or their fixed model and prompt-transport policy must be refreshed | updated external harnesses plus a validated policy edit. It never runs a panel, changes credentials, or edits a reviewed artifact |
| [`../gnd-codegen/SKILL.md`](../gnd-codegen/SKILL.md) | a validated model must become a runnable project | a generated derived surface plus a digest record. It never authors or changes the model |
| [`../gnd-conformance/SKILL.md`](../gnd-conformance/SKILL.md) | a generated project may have fallen behind its model | a drift finding over the derived surface only. It writes nothing and licenses nothing about extension code |
| [`../gnd-dev-session/SKILL.md`](../gnd-dev-session/SKILL.md) | an agent must be driven against the verifier under a bounded, digest-pinned contract | session evidence under `runs/` and a closed experiment. It never merges the session outcome with a verifier verdict or a conformance result (D-24) and never regenerates anything |
| [`../gnd-extract/SKILL.md`](../gnd-extract/SKILL.md) | a document must become a population | an extracted population plus its digest-bound sidecar, checked by `gnd verify` |
| [`../gnd-render-doc/SKILL.md`](../gnd-render-doc/SKILL.md) | a population must become a document | a rendered document plus its digest-bound manifest, checked by `gnd doccheck` |
| [`../gnd-solve/SKILL.md`](../gnd-solve/SKILL.md) | you want the whole loop walked in order | nothing of its own — every claim belongs to the station skill that produced it. It never runs a sibling on your behalf and stops at an explicit user gate between steps |
| [`../gnd-export/SKILL.md`](../gnd-export/SKILL.md) | explicitly requested tuples need finite proof/replay or a finite Lean definitions with unproved obligations or standalone Souffle program | bounded derivation program export, explicit native execution, grounded witnesses and independent replay; never source truth, completeness or assurance |

One reference library, and every packaged workflow skill indexed above. No row merges its claim with another's: a verifier verdict, a conformance result, an evolution record, recovery evidence, and a panel synthesis stay separate payloads even when one cites another by digest (D-24). The updater changes maintainer/runtime state and emits no review claim at all.

## Reference index

| Reference | Contains | Primary consumers |
|---|---|---|
| [references/representation-format.md](references/representation-format.md) | The `model.orm.yaml` spec: top-level structure, object types, fact types, constraint placement, provenance blocks, text-first extensions, two-layer validation rules | `gnd-model-from-text` (emission), `gnd` validator; later: synth-data, verifier, codegen skills |
| [references/constraint-reference.md](references/constraint-reference.md) | Every ORM 2 constraint family: description, graphical signal, YAML form, CNL template, and per-family "Checkable by gnd checker" status | `gnd-model-from-text` (Steps 4–6), `gnd` checker messages; later: verifier, synth-data skills |
| [references/constraint-inference.md](references/constraint-inference.md) | Typed common-sense library, ring-pattern matcher, bounded LLM proposal contract (`rationale_world_fact`) | `gnd-model-from-text` Step 6; later: model-evolution skill |
| [references/verbalization-patterns.md](references/verbalization-patterns.md) | Halpin CNL templates for the whole model + text-first additions (dialogue turns, sample facts, user quotes); schema-probe rows reserved for the Phase 4 recovery skill | `gnd-model-from-text` (Steps 6e, 7a), `gnd` verbalize module |
| [references/halpin-posture.md](references/halpin-posture.md) | The ORM 2 mindset: five pillars, ER-to-Halpin vocabulary map, posture-failure recovery | Every modeling skill, before first run |
| [references/provenance-and-modality.md](references/provenance-and-modality.md) | **Normative:** six-source taxonomy with required provenance shapes (including v2 `imported`); alethic/deontic semantics; the D-03 source×status → default-modality table | All skills emitting constraints; `gnd` semantic validator (`semantic:modality-policy`) |
| [references/population-format.md](references/population-format.md) | **Normative:** CORE-02 population interchange — header, closed-world semantics, vacuity clauses, exit-code bands 0/1/2/3/4 (4 = indeterminate), 10 MB cap | Agent-output extraction, synth-data, eval fixtures, `gnd` loader + checker |
| [references/coverage-and-element-addressing.md](references/coverage-and-element-addressing.md) | **Normative:** how a `covers:` row addresses a model element (the three addressable classes, declared-id and legacy positional forms, why positional is reported unstable rather than refused), and the coverage verdict vocabulary — corroborated / claimed / unclaimed, `unclaimed_with_evidence`, why a conclusions document never corroborates, and why the view emits no aggregate number | `gnd coverage`; every workflow skill authoring a `covers:` row |
| [references/milestone-record-format.md](references/milestone-record-format.md) | **Normative:** the `.gnd-planning/` directory, per-station milestone record shape, station commit grammar and staging rule — binds the driving agent, never the `gnd` CLI | Every workflow skill at its record-and-commit step; `gnd-new-project` for the scaffold |
| [references/orm-meta.schema.json](references/orm-meta.schema.json) | **Canonical machine spec** for `model.orm.yaml` (Draft 2020-12) | `gnd.model.load_model` (vendored copy), external validators |
| [references/population.schema.json](references/population.schema.json) | **Canonical machine spec** for population files (Draft 2020-12) | `gnd.population.load_population` (vendored copy), external validators |

## Canonical schemas

The two `.schema.json` files in `references/` are the **canonical** machine specs. The `gnd` package vendors byte-identical copies at `src/gnd/schema/`; `tests/test_schema_sync.py` asserts byte equality. To change a schema: edit the canonical copy here, then regenerate the vendored copy from it — never the other way around.

When the user selects saved external opinions, see the separate [judgment contract](../gnd-dev-session/references/judgment-contract.md); confidence grants no mechanical assurance.
