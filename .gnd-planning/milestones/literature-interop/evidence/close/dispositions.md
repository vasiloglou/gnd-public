# Close panel dispositions

The [report](PANEL-REVIEW.md) retains all 19 concerns from the six valid
responses. The three requested artifacts bind the review at `14fdc81f`.
The [close delta](../../notes/close-delta.md) was one of those artifacts.
This follow-up adds the requested evidence links and the new close controls.

## Provenance and refusal order

| Boundary | Executable control and observed outcome |
|---|---|
| Include bytes to extraction artifacts | LX1 `test_public_extraction_and_origins` resolves all nine addresses, including the anonymous irreflexive constraint and the two root attachments. `test_index_cannot_authenticate_changed_projection` re-pins altered flat and record bytes and verify exits 3 with `extraction:binding-mismatch`. `test_repinning_a_forged_extraction_schema_does_not_verify` independently re-pins the shape schema and sidecar. [LX1](../../005-phase-LX1.md) |
| Extraction precedence | LX1 `test_stale_coordinates[root]` changes the authored root and flat file together. Verify exits 3 and names the root first. The include variant changes both the pinned include and flat file and yields `include:hash-mismatch`. [LX1](../../005-phase-LX1.md) |
| Flat inputs to witnesses | LX2 `test_public_extract_witness_and_replay` verifies version 3 without a composition record. `test_reference_free_composition_proof` does so with a reference-free record. `test_stale_projection_inputs[flat]` substitutes bytes with the root and artifact record fixed. Production and replay exit 3 with `binding-stale`. `test_each_origin_axis` separately forges model origin and fact occurrence. [LX2](../../007-phase-LX2.md) |
| Replay precedence | LX2 `test_malformed_certificate_precedes_a_stale_include` pairs malformed proof bytes and a stale include and returns 3 with `input-invalid`. A structurally valid forged origin under stale input returns `binding-stale` first in `test_stale_projection_inputs`. [LX2](../../007-phase-LX2.md) |
| Reference and source inputs to composition | LX3 `test_catalog_is_refused_before_invalid_manifest` pairs the bad manifest with stale catalog, key conflict, subset dependence or equality dependence. Compose exits 3 with the applicable catalog diagnostic first. `test_consumers_refuse_independent_stale_bindings` covers changed catalog and source bytes, repinned record catalog roster and record bytes. `test_mixed_proof_origin_axes` independently forges the model origin, the catalog digest and each direction of occurrence origin. [LX3](../../009-phase-LX3.md) |
| Original extraction and checking roots to rebind | LX4 `test_stale_stage_evidence_refuses` changes each root, include, index, rebind, document, original population, extraction sidecar, original anchor, rebound population, rebound anchor, catalog, resolution, composition outputs, witness, edges and dates one at a time. Verify exits 3. The re-pinned variants explicitly assert fixture mismatch for both roots, an include, the catalog and date-role evidence. A re-pinned index is refused by fresh extraction reproduction. Both direct fresh-rebind tests load a separately valid altered checking root, then observe “root vocabulary pins differ” or “root catalog bindings differ”. [LX4](../../011-phase-LX4.md) |
| Rebind precedence and temporal evaluation | LX4 `test_temporal_constraint_distinguishes_checking_model` refreshes rebinds under the larger allowance and observes guarded failure exit 1. The same valid alternate root plus a stale rebind returns exit 3 at `survey/rebind.json` before either check or advice. [LX4](../../011-phase-LX4.md) |
| Rebound source and resolution to composition | LX4 verifies the candidate rebind and re-derives resolution evidence. `test_repinned_composition_cannot_replace_source_rederivation` re-pins a composition record with a forged source coordinate. Product check exits 3 and says “re-derived composition differs from the record at facts”. The example refuses before replay and advice. The LX3 independent source-byte mutation and LI2 unjustified-join control exercise the product loader. [LX3](../../009-phase-LX3.md) |
| Composition to replay and optional advice | LX4 `test_verified_proof_must_name_the_fixture_targets` re-pins a valid alternate proof and its replay artifact. Verification refuses the target mismatch. The composed-witness suite checks changed population bytes. LX3 checks record and witness origin bindings. LX4 `test_report_digest_cannot_replace_advice_rederivation` modifies the reported parent date while the input bindings remain fixed. Verify exits 3 after re-deriving the advisory. [LX4](../../011-phase-LX4.md) |

## Plan §7 refusal matrix

| Unsupported input | Observed result and control |
|---|---|
| Nested include | Extract 3 with `include:forbidden-section` and `includes`. LX1 `test_include_boundaries[nested]`. |
| Reference declaration within an include | Extract 3 with `include:forbidden-section` and `reference_populations`. LX1 `test_include_boundaries[references]`. |
| Unattended source within an include | Extract 3 with `include:forbidden-section` and unattended source. LX1 `test_include_boundaries[unattended]`. The close test `test_relabelled_unattended_metadata_refuses_extraction` first loads the attended input, then re-pins it with unattended span metadata. Extract 3 gives `include:invalid-included-model` and `semantic:unattended-u7`. |
| Temporal extraction model | Extract 3 with `temporal:consumer-unsupported` on the LX4 checking root. LX4 `test_temporal_constraint_distinguishes_checking_model`. |
| Authored includes on the unrooted witness/replay intake | `include:unsupported-route` before witness production or replay inference. The MC1 `test_R2_witness_inputs` and `test_R3_witness_memory` observe the input exception. The LX2 verification selection includes these MC1 admission controls. |
| Composition with explicit anchor or reference override | Check CLI usage 64 naming `--anchors`. The API raises its named `ValueError` for explicit references. Composed witness with an explicit reference root gives usage 64. LX3 `test_composition_override_and_catalog_write_collisions`. |

## Compatibility, layout and advice

- LX1 `test_legacy_bundle_bytes` compares the include-free artifact index,
  applicable set, projection schema and verbalization to the exact hashes
  in `tests/fixtures/lx1-flattening/expected.json`, recorded against the
  pre-LX1 implementation. The legacy v1 witness producer digests are in the LI0
  witness golden fixture. LX2 `test_legacy_composed_bytes_and_replay`
  checks the pre-LX2 v2 certificate digest
  `93776b765d3aefe04d5fdcc0916d0f363f7ce5b2ba266b04a7f3e541152291a7`
  and exit-0 replay. LX3 independently checks pre-LX3 reference-free
  composition record and population bytes. [LX1](../../005-phase-LX1.md),
  [LX2](../../007-phase-LX2.md), [LX3](../../009-phase-LX3.md)
- The delegated ruling adopts the shared per-source example directories.
  Verify and fidelity use the same two original extraction populations and
  extraction sidecars and the same two `document.md` files. Composition
  adds two `document.txt` copies and two checking-bound populations and
  anchor sidecars. Those new bound outputs carry the checking coordinates.
  Their content is distinct from the original extraction handoff. The two
  document copies are the accepted cost of the current reader filenames.
  [Installed observation](../LX4/installed-observation.json)
- The publication table and candidate-edge bytes have their own report
  bindings. The nine input proposals produce eight report rows. The
  excluded predicate is `evaluated-as`. The PINN result names
  `doi:10.1016/j.jcp.2018.10.045` (2019) and
  `doi:10.1016/j.jcp.2020.109913` (2021) under the `publication` role.
  The re-pinned date-role input and independently re-pinned advisory result
  each refuse. Omitting advice leaves all four measured product artifact
  bytes equal. [Installed observation](../LX4/installed-observation.json)

## Evidence scope

The [per-phase audit](phase-review-scope.json) names each original verdict,
reviewed commit, snapshot and amended file. Local regressions establish
the repairs. The [verification scope](verification-scope.json) records
identical source, test, tool, project-file and lockfile objects at the
earlier runtime test and the original close packet. The post-panel changes
add tests and planning evidence. They leave runtime source unchanged.
The retained lint digest comparison establishes equality of all 188
inherited diagnostics. The [close record](../../014-milestone-close.md) names the
deselections and the trigger for broader lanes.

The [plan clarification](../../notes/literature-interop-plan.md#12-close-clarification)
states the reader side of the absent-field rule. The pre-clarification
bytes remain pinned through the close request and original source commit.
