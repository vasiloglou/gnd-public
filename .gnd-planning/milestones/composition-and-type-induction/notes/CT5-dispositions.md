# CT5 documentation dispositions

Scope: every Markdown page or packaged-skill file that
`grep -rlE "anchors?\.json|--anchors|sidecar|gnd witness|gnd replay|gnd discover|composition" docs src/gnd/skills README.md`
lists (51 files; `README.md` has no match). Files owned by the CT5 example work
(`docs/how-to/compose-documents.md` and its assets) and the generated `site/`
are out of scope. Three matches are not prose (rows at the end of the table). Packaged skills are installed without the docs site, so
their edits name schema files and add no links.

Totals: 11 updated, 40 unchanged (51 rows; corrected after the CT5 review, F7).

| File | What it says about the changed surfaces | Disposition |
|---|---|---|
| docs/agents/documents.md | anchored constraint with `gnd check --anchors --document`; extraction sidecar | updated: one sentence linking the anchor sidecar reference and composition |
| docs/agents/export-and-review.md | `gnd witness` / `gnd replay` over one population | unchanged: single-population example stays true; links to the guide and API reference |
| docs/agents/index.md | "seven stable functions" in `gnd.api`; sidecar and replay in skill tables | updated: count now eleven, the table described as the ones an agent loop uses most |
| docs/guides/data-and-transitions.md | "report composition" (unrelated word use) | unchanged: not about document composition |
| docs/guides/documents.md | extraction sidecar; anchor sidecar with version 2 link | unchanged: CT1 already added the version-2 sentence and link |
| docs/guides/exports.md | `gnd witness` / `gnd replay` commands for one population | unchanged: version-1 flow is unchanged; composition is reached from the CLI and API references |
| docs/guides/synthetic-data.md | synth provenance sidecars | unchanged: synth sidecars, not anchor sidecars |
| docs/how-to/disclosure-mode.md | said `gnd discover` behaves the same in every mode | updated: excepts `--show-values`, which the mode governs |
| docs/how-to/grow-a-model.md | candidate writer shared with `gnd discover` | unchanged: still accurate |
| docs/how-to/learn-rules-commands.md | `gnd discover --families uniqueness,mandatory` run | unchanged: explicit families; default families unchanged |
| docs/how-to/repair-a-missing-claim.md | `gnd witness` over one population | unchanged: version-1 witness unchanged |
| docs/index.md | sidecar and `gnd replay` in the agents table | unchanged: summary rows stay true |
| docs/reference/anchors.md | the anchor sidecar format, versions 1 and 2 | unchanged: written in CT1 |
| docs/reference/cli.md | `gnd compose`, `gnd check --composition`; witness/replay rows without `--composition`; `--anchors` without a format link; discover row without the opt-in family | updated: witness/replay `--composition` row, anchor sidecar link, `--families fact-type` clause on the discover row |
| docs/reference/composition.md | the composition contract, check and witness lineage | unchanged: written in CT2 and CT3 |
| docs/reference/disclosure.md | `gnd compose` row; witness/replay row; discover `--show-values` row | unchanged: CT2 to CT4 already updated it |
| docs/reference/discover.md | synopsis listed only the seven families; "Single-role rules of seven families" | updated: synopsis gains the `--families fact-type [--min-support] [--show-values]` form; the families sentence says "by default" and links the opt-in section |
| docs/reference/formats.md | canonical references table had no anchor sidecar or composition row | updated: rows for anchor sidecars and composition manifests/records with their schemas |
| docs/reference/ilp-bridge.md | the IK2 envelope `gnd discover` writes | unchanged: envelope unchanged |
| docs/reference/measure-labels.md | synth sidecars | unchanged: not anchor sidecars |
| docs/reference/python-api.md | "eleven functions" including `compose`; `compose` section; witness/replay signatures without `composition=` | updated: count left at eleven (correct since CT2); `witness` and `replay` signatures gain `composition=None`, with a link to the composition trace section |
| docs/reference/why-not.md | `gnd witness` as the companion command | unchanged: still accurate |
| docs/release-notes.md | CT1 to CT4 entries | unchanged: written by each phase |
| docs/runtimes/souffle.md | `gnd replay` over a version-1 certificate | unchanged: version 1 unchanged |
| docs/tour.md | extraction sidecar; witness and replay | unchanged: summary stays true |
| src/gnd/skills/gnd-dev-session/SKILL.md | a corpus label sidecar | unchanged: not an anchor sidecar |
| src/gnd/skills/gnd-export/SKILL.md | "certificate schema pins version 1" | updated: pins versions 1 and 2; one sentence on `--composition` for `gnd witness` and `gnd replay` |
| src/gnd/skills/gnd-export/references/export-contract.md | `gnd witness-view` redaction | unchanged: view behaviour unchanged |
| src/gnd/skills/gnd-export/references/witness-contract.md | certificate versions 1 and 2, `--composition` replay outcomes | unchanged: CT3 added the version-2 section |
| src/gnd/skills/gnd-extract/SKILL.md | the extraction sidecar only | updated: one sentence separating it from the anchor sidecar (`gnd/anchor-sidecar.schema.json`, version 1 or 2) and naming what `gnd compose` reads per source; no link added |
| src/gnd/skills/gnd-extract/references/extraction-contract.md | extraction sidecar `schema_version: 1` | unchanged: the extraction sidecar did not change |
| src/gnd/skills/gnd-model-evolve/SKILL.md | said a `gnd discover` proposal adds only induced constraints | updated: notes the opt-in `fact-type` family also adds a placeholder fact type (and value type) and moves no rows |
| src/gnd/skills/gnd-model-from-text/SKILL.md | "over-decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-model-from-text/USAGE.md | "atomic-fact decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/README.md | "decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-model-from-text/evals/fixtures/synthetic_good_user/dialogue.md | "decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-model-from-text/references/csdp-workflow.md | "decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-model-from-text/references/dialogue-patterns.md | "decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-orm-core/SKILL.md | extraction sidecar in the skill routing table | unchanged: still accurate |
| src/gnd/skills/gnd-orm-core/references/constraint-reference.md | anchor sidecar versions 1 and 2, every anchor must bind | unchanged: CT1 updated it and names the schema |
| src/gnd/skills/gnd-orm-core/references/halpin-posture.md | "decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-orm-core/references/milestone-record-format.md | extraction write set with its sidecar | unchanged: extraction sidecar unchanged |
| src/gnd/skills/gnd-orm-core/references/population-format.md | pointer to the source-anchor sidecar section | unchanged: pointer still correct |
| src/gnd/skills/gnd-orm-core/references/provenance-and-modality.md | `induced` source from `gnd discover` | unchanged: fact-type proposals carry the same induced envelope |
| src/gnd/skills/gnd-orm-core/references/representation-format.md | anchored family; vocabulary digest and sidecar binding | unchanged: digest and binding rules unchanged |
| src/gnd/skills/gnd-orm-core/references/verbalization-patterns.md | "over-decomposition" (unrelated) | unchanged: not about composition |
| src/gnd/skills/gnd-render-doc/SKILL.md | judgment contract creates no sidecars | unchanged: still accurate |
| src/gnd/skills/gnd-solve/SKILL.md | `gnd discover` suggests induced, advisory constraints | updated: adds the opt-in fact-type proposals |
| src/gnd/skills/gnd-export/references/witness.schema.json | the version-2 `composition_sha256` and `sources` fields | unchanged: updated in CT3 and pinned to its twin by `tests/test_schema_sync.py` |
| src/gnd/skills/gnd-model-from-text/evals/cases.json | "atomic decomposition" (a word match on *composition*) | unchanged: not about composition |
| src/gnd/skills/gnd-update-review-panel/scripts/update_harnesses.py | "composition of the two halves" in a docstring | unchanged: not about composition |

Explicit checks:

- `docs/reference/python-api.md` count: the page says eleven functions
  (`validate`, `check`, `check_with_receipt`, `transition`, `verbalize`,
  `verbalize_rules`, `diff`, `witness`, `replay`, `why_not`, `compose`),
  matching `gnd.api.__all__`; the one stale count elsewhere
  (`docs/agents/index.md`, "seven") is now eleven.
- Witness contract: `src/gnd/skills/gnd-export/references/witness-contract.md`
  already documents versions 1 and 2 (CT3) and needs no change; its twin
  entry point `src/gnd/skills/gnd-export/SKILL.md` said the schema pins
  version 1 and now says versions 1 and 2.
