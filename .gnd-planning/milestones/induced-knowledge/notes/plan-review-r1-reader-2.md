# Reader 2 — implementability, dependency homes and layers

Reviewed plan SHA-256 `26fa91632e5ee637b1949ad4e8dd6ba25daac57180280328e3d04c1e050a1814`
and IK1 spec SHA-256 `f79d6375630e8706a9a3fe88af7669b3f0a81fcbb446ec0e1d55d4df22b8cec0`
— both match at `0e2ba79`.

**Verdict: request-changes** within the implementability/dependency-homes/layers lens.

Scope: full plan and IK1 spec; `model_verbalization.py`, `verbalize.py`,
`codegen/docstrings.py`, `extract/projection.py`, `anchors.py`, `diff.py`,
`diff.schema.json`, `report.schema.json`, `api.py` diff path, `evolve/service.py`,
`evolve/models.py`, `process.py`, `constraint_families.py`, `population.py`,
`tools/gnd_layers.json`, `tools/gnd_arch.py`, `gnd_entrypoints.json`,
`test_schema_sync.py`, `test_rf6_query_policy.py`, rf1/rf2 pin fixtures. Read-only
`uv run gnd validate` and short `python -I` probes. Disclosed side effects: two
temporary YAML models in the session scratchpad (`r2tmp/`, outside the repository);
`uv run` may have used the gitignored `.venv`/`__pycache__`. No tracked file touched.

## Findings

- **R2-F1** (blocking, high): The extraction projection refuses a `description`
  key. Spec 68–69 sets `"description"` on the object type's `instance_properties`
  entry, but `project()` runs a fail-closed allowlist audit before returning
  (extract/projection.py:306–329) and `_ALLOWED_KEYWORDS` (43–54) excludes
  `description`. Every model with a description raises `ProjectionGateError`;
  T5/T6 cannot pass. Changing it touches the published PANEL-4 table and the
  "shape-only" doctrine, which the spec does not decide; the likelier home is the
  constraint-blind vocabulary (extract/vocabulary.py). Reproduce: add `description`
  to one instance property of `_build_projection(load_model('tests/fixtures/models/full_vocabulary.orm.yaml'))`
  and call `audit_allowlist` → `('…instances.properties.employee','description','not on the published _ALLOWED_KEYWORDS table…')`.
- **R2-F2** (blocking, high): `gnd diff` refuses before it can report a
  description change. Spec 71–74 / T8 expect `annotations` with unchanged exits,
  but `vocabulary_digest` hashes the whole `object_types` list (anchors.py:193–199)
  and `diff_models` raises `diff:vocabulary-mismatch` when digests differ
  (diff.py:280–282; duplicated api.py:716–717), mapped to exit 3
  (commands/checking.py:260–261). Any description add/change/remove exits 3.
  Excluding `description` from `vocabulary_digest` changes the extraction/anchor
  sidecar binding contract and needs its own decision. Reproduce: digests of
  `{'object_types':[{'id':'a','kind':'entity'}],'fact_types':[]}` with and without
  `'description':'x'` differ.
- **R2-F3** (hardening, medium): IK1-D1's 2,000-char cap (spec 53, 85) does not
  survive `_neutralize`, which truncates at `MAX_RENDERED_VALUE_CHARS = 512` with an
  elision marker (verbalize.py:34, 57–59); T5's 2,000-char case renders truncated.
  The verbalization line already embeds the full object type via
  `canonical={_canonical(item)}` (model_verbalization.py:519–525), so the
  description appears twice (full JSON and truncated sentence).
- **R2-F4** (completeness, medium): `BlastRadiusEntry.surface` is a closed
  `Literal` (evolve/models.py:635–651) and the evolution contract enumerates
  surfaces (skills/gnd-model-evolve/references/evolution-contract.md:190–192).
  Emitting `"annotation"` fails pydantic validation in preview; T9 fails unless
  models.py and the packaged skill change, neither named in the spec (spec 76
  estimates ~3 lines).
- **R2-F5** (completeness, medium): `report.schema.json` `$defs.diff_reference_report`
  (line 3186) duplicates diff.schema.json with `additionalProperties:false` and no
  sync test; a reference-population diff envelope (schema_version 12) carrying
  `annotations` fails report-schema validation. Also unnamed: redaction's
  `kind == "diff"` branch (redaction.py:775), diff.reference.md, and keeping
  `gnd-diff/1` while adding a field — RF1 mutation M-SEM-diff-schema anchors that
  literal (tests/fixtures/rf1-pins/mutations.json:1318).
- **R2-F6** (completeness, medium): IK4/IK5 homes ignore the closed lane list and
  RF5 entry-point policy. Plan 160 says new `gnd/discover/` "layer-assigned", but
  `lanes` in gnd_layers.json is a closed list of 12 and lanes-layer modules must
  carry a known lane (gnd_arch.py:155–156); a new command group must join
  hard-coded `RF5_COMMAND_GROUPS` (gnd_arch.py:802–806) and gnd_entrypoints.json
  scope/service targets/bindings; service targets must be lanes-layer `*.service`
  modules (gnd_arch.py:825–828; test_rf5_commands.py). New `fact_types`/`roles`
  reads count against the exact RF6 ceiling. None of this is in §3 or IK6-C3.
- **R2-F7** (hardening, low): Plan 148 serialises IK2 → IK3 → IK4, but IK3 does not
  use induced provenance, and IK4 takes `MODEL POPULATION` without labels (129–136),
  computing support from the checker. IK2 → IK4 and IK3 → IK5 are real; IK1
  independence holds. IK1 and IK2 both edit the orm-meta twins and
  evolve/service.py, so parallel execution needs merge sequencing.
- **R2-F8** (hardening, low): "Per fact type" (plan 61, 131) does not fit
  subset/equality/exclusion (and D6's same-object-type pairs), which span fact
  types; the whole population is parsed in memory anyway (population.py:507–553),
  so the claim provides no memory bound. The cap is 10 MiB.

## Reasons

- Two IK1 deliverables (C2 extraction, C4 diff) cannot work as designed against
  current gates (F1, F2).
- Verified true: extra object-type property exits 3 from `gnd validate`;
  `object_type` `additionalProperties:false`; twin sync covered by
  test_schema_sync; `gnd.process.run_bounded_process` exists (infrastructure layer);
  `ModelIndex` (model layer) and `FAMILIES` exist; `classify`/`score_constraint`,
  `Sidecar`, `_enforce_d12` behave as described; no test re-checks the schema digest.
- Description-absent byte identity is plausible: verbalization, docstrings and
  surfaces change only when the key is present; no RF1/RF2 pin anchors code IK1 must
  change.
- The ~55-line estimate omits models.py, report.schema.json, the
  anchors/vocabulary decision, the allowlist and reference prose.

## Limits

No test suite run; IK2–IK5 semantics assessed only for layers/dependencies; PR #35
state and issue text not checked; findings rest on static reading plus three
reproductions.
