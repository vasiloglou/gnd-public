# TS5 documentation dispositions

Scope: every Markdown page or packaged-skill file that
`grep -rlE "families fact-type|fact-type family|shape_match|shape match|multi_valued|multi-valued|type-evidence|judgements" docs src/gnd/skills README.md`
lists before this phase (14 files, `docs/how-to/compose-documents.md` among
them; `README.md` has no match), plus `docs/reference/capabilities.md`, which
names the family in other words, plus the plan's proposed
`docs/reference/type-judgements.md` (refuted). Review F5 corrected this
sentence, which had counted `compose-documents.md` twice.
The new how-to, its figures, JSON schemas and the generated `site/` are out of
scope. Packaged skills ship without the docs site, so their edits add no links.

Totals: 6 updated, 9 unchanged, 1 refuted (16 rows).

| File | What it says about the changed surfaces | Disposition |
|---|---|---|
| docs/agents/index.md | rows for both skills | unchanged: TS3 and TS4 added them |
| docs/how-to/compose-documents.md (the CT how-to) | `--families fact-type` proposes fact types for generic rows | updated: one sentence linking the new how-to for duplicates and multi-valued attributes |
| docs/how-to/disclosure-mode.md | the family's `--show-values` follows the mode | unchanged: the judgement options follow the same mode, which `disclosure.md` states |
| docs/reference/capabilities.md | discover row: proposes fact types from a generic fact type | updated: renders the two skills' verdicts when given |
| docs/reference/cli.md | discover row names only `--families fact-type` | updated: names `--type-evidence`, `--type-evidence-in` and the two judgement options |
| docs/reference/disclosure.md | evidence and judgement inputs follow the mode | unchanged: written in TS1 and TS2 |
| docs/reference/discover.md | once-per-generic paragraph; D5 sentence | updated (TS5-C3): each says what holds by default and what changes under judgement, and links the skills and the how-to |
| docs/reference/evolve-policy.md | `--shape-report` `shape_matches` | unchanged: the evolve preview's own report, not the family's |
| docs/release-notes.md | TS1, TS2 entries | updated: one entry for the two skills, linking the how-to |
| src/gnd/skills/gnd-judge-fact-types/SKILL.md | the duplicate judge | unchanged: TS3, TS4 |
| src/gnd/skills/gnd-model-multivalued/SKILL.md | the shapes judge | unchanged: TS4 |
| src/gnd/skills/gnd-orm-core/SKILL.md | workflow rows and schema rows for both skills | unchanged: TS3, TS4 |
| src/gnd/skills/gnd-model-evolve/SKILL.md | a discover proposal adds a placeholder fact type per attribute | updated: with judgements it renders their verdicts, including many-to-many |
| src/gnd/skills/gnd-model-evolve/references/evolution-contract.md | `--shape-report` `shape_matches` | unchanged: the preview's report |
| src/gnd/skills/gnd-solve/SKILL.md | a proposal may come from discover with `--families fact-type` | unchanged: still accurate; the skills are reached through orm-core |
| docs/reference/type-judgements.md (plan §3, new) | — | refuted (P6): the contract's one home is `discover.md` "Type judgements" (TS2); not written |
