# Reader 2 -- implementability, pins and homes

Retained text of the reader's returned report, lightly edited for layout.
One review round covered both milestones. Scratch paths read `<scratch>`.

**Digest check:** all four snapshots match their stated SHA-256. Checked
against HEAD `1446f909`.

**Verdict:** request-changes. The MG1 parity gate cannot pass as written, and
MG-D2's proposed reading conflicts with an invariant evolve enforces. CT1 is
close: approve-with-fixes.

**Scope.** Cited lines, layer homes in `tools/gnd_layers.json`, the RF6
allow-list, the disclosure table and its tests, the `__all__` pins, RF1 CLI
goldens, evolve, witness and anchor schema versions, the twin schema files.
Probes in `<scratch>/plan-review/reader2/` (`probe_agg.py`, `probe_agg2.py`).
No pytest.

**What holds.** Accurate: `api.py:124` and the four MG1 T6 pins; the
`_derivation_cnl` fallbacks; `anchors.py:105-139`, `:133-135`;
`_core.py:1911-1917`; `evolve/models.py:219-223,545`; apply's gate re-run
`service.py:1574-1577`; seven discover families. Proposed layers are legal;
discover already imports evolve (`discover/output.py:21-29`). Dependency
order is coherent. CT-Q1 is correct.

**Findings.**

**R2-F1 (blocking) -- MG1 T3, Goal.** The line is `_fact_type_cnl(...)` + the
optional `Admission depends on …` + the redaction note + `reading=…
derivation_rule=… canonical=…` (`model_verbalization.py:567-572`), all through
`line_text` (`verbalize.py:125-134`). T3 fails on the whole corpus (code
read). Repair: `text` is `line_text(_derivation_cnl(rule, model))`; T3
asserts the line starts `[fact-type:ID] ` and the text follows `This fact
type is derived: ` immediately, then ` Admission depends on` or ` reading=` /
` Values`.

**R2-F2 (blocking) -- MG1 standing rule 1, `Model | str | Path`.**
`render_model_verbalization(path)` crashes on any model with a structured
aggregate: `_fact_type_cnl(item, model)` (`:570`) receives the raw path and
`analyze_declared_aggregate` calls `.get` on it (`_validation.py:1113`).
Reproduced: `render_model_verbalization("tests/fixtures/v62-phase4/models/aggregates.orm.yaml")`
raises `AttributeError: 'str' object has no attribute 'get'`; a loaded Model
works. Five corpus models fail by path, three of them packaged examples. The
sweep rendered loaded Models only. Repair: coerce first and pass the loaded
model down; a path-input case in T1. Fixing the existing path moves no digest
(it crashes today); record it. **Owner:** fix in MG1, or carry.

**R2-F3 (blocking) -- MG-D2 (a), §2.2, §5.** Versions are tied:
`EvolutionPreview._bindings_match` raises "preview and proposal versions must
match" (`evolve/models.py` ~`:791`); preview (`service.py:1263`) and apply
(`:1561`) accept only `EVOLUTION_SCHEMA_VERSION`; finalize asserts `state ==
preview == proposal` (`:1819-1821`). A v4 preview over a v3 proposal is
invalid; making v4 current breaks v3 apply. The policy sits in a
caller-rewritable preview with a recomputable `preview_sha256`, so dropping
`policy` applies as a no-policy preview; MG2-C3 tests only dropped issues.
Code read. Repair: name the real readings with costs: (i) proposal v4 carrying
the policy, approved by digest; (ii) separate preview and proposal versions
everywhere above; (iii) an `apply --policy` the caller repeats. Define
whether a refusing preview (exit 3) still writes its document. **Owner.**

**R2-F4 (hardening) -- MG1 `api.py` design.** Payloads use `exit_code`
(`api.py:775,818,862`; `witness/service.py:120`); argument-shape errors raise
`TypeError` (`checking_service.py:55-61`, `api.py:672-673`); `failure` is a
closure in `_run_verbalize` (`api.py:817`). Repair: `exit_code` and the
`error` object; state whether a bad `fact_types` raises or returns; fix T5
and the schema.

**R2-F5 (hardening) -- MG1 branch table.** A fifth fallback: non-dict atom
(`:167-168`). Paths that raise: the `date_add` unpack (`:154`), non-dict
`head` (`:189`). Repair: add to the sweep and reasons, or cite the excluding
validator rule.

**R2-F6 (hardening) -- MG-R6, CT-R8 "RF6 gains no row".** RF6 counts reads
per (path, owner function, expression) (`tests/test_rf6_query_policy.py:21-45`).
CT1's move of `record['fact_key']['roles']` from `_anchored_verdicts` (row
count 3) into `_anchor_records` forces a row change in
`code-refactoring/evidence/RF9-repair/query-allow-list.json`. MG1 adds a row
if it iterates `loaded.fact_types`; likewise MG4. Repair: reads through
`ModelIndex` (`iter_fact_types_shared`); state CT1's row-move procedure.

**R2-F7 (hardening) -- MG §1, §2.3, homes.** `reference_identity` is at
`src/gnd/refscheme.py:97` (layer `model`); `extract/refscheme.py` is a lane
shim, and importing it into a model-layer helper violates layering. The
meta-schema is at `src/gnd/schema/orm-meta.schema.json` with a pinned twin at
`skills/gnd-orm-core/references/orm-meta.schema.json`. MG3 does not pin the
`primitive(..., variant=)` variant (`model_index.py:276`); AGENTS.md requires
preserving the caller's variant. Repair: fix paths, name the twin, pin the
variant in MG-D7.

**R2-F8 (hardening) -- CT §2.3, CT3.** The witness schema has `version:
{const: 1}` and closes `base` and `binding`; CT3 needs witness version 2,
unstated. Omitted: the twin `skills/gnd-export/references/witness.schema.json`;
a `--composition` option on `gnd witness` and the API; Souffle witness and
why-not consumers.

**R2-F9 (hardening) -- CT §2.2.** Anchors key on the source row's values
(`_core.py:1979`); after renaming the composed value differs. Unstated which
value is checked and how one composed row maps to several source keys and
documents; anchored evaluation takes one (sidecar, document) but the plan
homes the change only in `checking_service.py`. Repair: "source value against
source span"; name the `_core` change.

**R2-F10 (completeness) -- CT §2.2, CT2-C4 vs CT-D4.** Make them agree.
**Owner.**

**R2-F11 (completeness) -- CT-D9 (b) vs CT4-C3.** A reviewer cannot name the
type without the value; discover is every-mode. **Owner:** where the value
appears and its disclosure row.

**R2-F12 (completeness) -- unnamed pins.** `tests/test_disclosure_mode.py:218`
pins exactly 48 CLI leaves and `:498` pins `48 - 15 - 4`; `gnd compose`
changes both. New `redaction.OutputKind`s need rows. Per-leaf (some
per-Python-version) RF1 help goldens (`gnd_extract.json`, `gnd_validate.json`,
`gnd_check.json`, `gnd_replay.json`, `gnd_discover.json`,
`gnd_evolve_preview.py31{1,3,4}.json`); MG4, MG5, CT1, CT3, CT4 gates omit
`tests/test_rf1_cli_pins.py`. `release-notes.md:56` is prose, not a pin. The
`__all__` tail order across MG1 and CT2 is unstated.

**R2-F13 (completeness) -- CT1 spec.** 80 source lines vs the plan's 120.
`_exact_keys` on top-level keys runs before the version check
(`anchors.py:108-109`), contradicting standing rule 3's "version check
first". "A row fails once" needs per-row dedupe; `failed` is appended per
role (`_core.py:1982,2005`). T7's comparison has no named home.

**R2-F14 (completeness) -- MG4, CT4 end to end.** MG4-C1 does not name which
`artifacts.json` consumers see the extra file; CT4-C4 depends on R2-F3. Both
need a case that fails before the change.
