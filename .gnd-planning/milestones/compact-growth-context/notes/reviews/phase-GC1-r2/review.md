I found two places where the projection drops semantic metadata that the default renderer keeps, so C1 does not hold as claimed. All 13 files match the SHA-256 values in the brief. The r1 round produced no review: its `review.log` holds only a CLI usage error and `review.md` is empty (its hash is the empty-file digest), so this is the first real read of these bytes.

## 1. Findings

**F1: An object type's `derivation`, `derivation_rule` and `storage` are dropped, so a derived subtype looks the same as an asserted one.** (completeness, against C1's "semantic metadata")
- **Where:** `src/gnd/model_verbalization.py`, the object-type allowlist in `render_growth_view` (diff lines +606–609). It keeps `id, kind, name, primitive, precision, scale, reference, inherits_reference`. The meta-schema's `object_type` (`src/gnd/schema/orm-meta.schema.json`, `$defs/object_type`) also defines `derivation`, `derivation_rule` and `storage`.
- **Inconsistency:** fact types do keep `derivation` (the code writes `row["derivation"] = fact.get("derivation", "asserted")`). The ordinary renderer (`render_model_verbalization`, object-type details list around line 668) shows all three fields for object types too.
- **What you see:** this happens on the committed fixture itself. In `tests/fixtures/models/full_vocabulary.orm.yaml`, `contractor_employee` is `derivation: derived` with a `derivation_rule` and `storage: computed`. It projects as `{'id': 'contractor_employee', 'inherits_reference': True, 'kind': 'entity', 'name': 'ContractorEmployee'}`, the same shape as the asserted `permanent_employee`. A host using this view would offer to assert population into a computed subtype.
- **Reproduce (run):**
  1. Parse the fixture with `gnd.model.parse_model_document`.
  2. On `contractor_employee`, set `derivation: asserted` and remove `derivation_rule` and `storage`.
  3. Reload with `load_model_bytes` and run `render_growth_view`.
  4. Result: `derived->asserted same bytes: True`. It should differ.

**F2: An object type's `independent` flag is dropped.** (completeness, against C1)
- **Where:** same allowlist. The schema defines `independent` on `object_type`, and the ordinary renderer shows it. In ORM, an independent object type changes what the mandatory-role semantics require.
- **Reproduce (run):** on the fixture, set `independent: true` on `employee`. `render_growth_view` gives byte-identical output (`independent same bytes: True`).
- **Not reproduced (read only):** `$defs/fact_type` defines `objectification_independent`, and the fact allowlist (`id, reading, inverse_reading, objectified_as`) leaves it out the same way. I did not build an objectified fact to run it.

**Test gap (style, no consequence of its own):** `test_full_inventory_and_size` only checks `set(result["object_types"][0]) <= {...}`. That is a subset check on the first row only, so a missing semantic object-type field can never fail it. The spec's "compare each retained semantic parameter with the source" is done for constraints but not for object types.

## 2. Checked and true

- **Composed identity:** I built a version-5 root that includes `seeded_growth/seed.orm.yaml` by pin, with `fact_type_constraints` attaching `m_root` to the included `work_has_version`.
  - The view lists `m_root` and the seed's `u1`, each exactly once, both under host `work_has_version`. There is no double count from the leftover `model.fact_type_constraints`.
  - IDs are the composed (unique, collision-refused) ones from `_merge`.
- **Unresolved include:** this refuses through the shared `_check_resolved_includes`. The ordinary renderer still makes the same call first, so its refusal order is unchanged.
- **Role order:** `role_object_types()` builds an insertion-ordered dict from the fact's `roles`, so authored order is kept. The test checks this for every fixture fact.
- **Guarded constraints:**
  - `_iter_guarded_atoms` also yields the `negate[i]` atoms with their own paths, so negated atoms appear and stay distinct.
  - Each atom carries a path, its fact type and its role names. Variable sharing is not projected, which the spec allows ("full rule body remains the authority").
- **Duplicate constraint signatures:** sorting with `_canonical` keeps duplicates.
- **Textual constraints:** `expression` is omitted and `formal_language` kept, as the spec states.
- **Constraint allowlist vs. schema:** it covers every family-specific property in the schema except `textual.expression` and `formal_expression` (omitted on purpose) and the guarded body fields.
- **Values that are not JSON:** a YAML date in `allowed` is refused by the schema before rendering. I found no projected field that can hold a date, so the missing `_refuse_values_outside_json` call has no breaking input I could build.
- **Standing check (code fitted to its examples):** the change adds no regular expression, string split or slice over structured text.
  - `entry['sha256'][:12]` in `_include_lines` was already there and slices a hex digest, which is a flat token.
  - `sorted(atom_bind(atom))` uses the existing helper.
  - No branch names a fixture literal.
- **Successor evidence:** the `dynamic-query-successor.json` entries match the new lookups in the diff (`item[key]`, `fact[key]`, `role_players[fact['id']]`, and the moved `entry.get(key)`).

## 3. Not checked

- I did not run the repository test suite, the layering checks or lint. I ran only the probes described above.
- I did not run `objectification_independent` (see F2).
- I did not check whether the ModelIndex cache could hand back stale object rows for two models with the same content key.
- `operations`, `deontic_notes` and `rejected_proposals` are left out of the view. The spec limits it to five sections, so I treated that as in scope and did not test it.

VERDICT: CHANGES_REQUESTED
