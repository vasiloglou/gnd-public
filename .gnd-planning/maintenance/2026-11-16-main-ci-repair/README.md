# Main CI repair, 2026-11-16

The owner asked for this repair after a full local run of the default test lane on
`main` at `3fe7b136` (beast-3, six shards, uv 0.13.7, Python 3.13.18). The run had 278
failures and 2 errors. The same test files pass at v0.3.0 (`257a8bb3`). Running them at
every first-parent merge since then attributes each failure to the merge that introduced
it:

| Merge | Work | New failures |
|---|---|---:|
| PR 184 (`0ff0e9ca`) | guarded-rule workflows (GW) | 18 |
| PR 191 (`ecd12986`) | guarded-rule pages | 3 |
| PR 198 (`09c89840`) | dev-tools handle-issue delivery | 4 |
| PR 196 (`2dd38cf7`) | guarded-rule clauses (GC1–GC4) | 239 |
| PR 202 (`e3431ba1`) | literature interop (LX) | 10 |
| PR 203 (`a7785ffb`) | literature depth (LD) | 2 |
| PR 205 (`3fe7b136`) | expense receipts docs | 2, fixed by PR 206 |

Every failure came from merged work that changed pinned code or behavior without
updating the matching record. Each fix below uses the repository's own mechanism and
names the commit it accounts for. No pin is loosened and no check is removed.

The 2 errors are `tests/test_public_optional.py`. Its fixture requires the CI-pinned
uv 0.10.10, and beast-3 has uv 0.13.7. Both tests pass on a machine with the pinned uv,
and the 0.3.0 baseline recorded the same two errors on beast-3.

| Failure | Cause | Repair (mechanism) |
|---|---|---|
| `test_public_semantic_adapter` ×206 | GC2 (`b4e84af4`) added `SnapshotIR.computed_available`, a `frozenset` | The immutability walk also accepts a `frozenset`, and checks every member is immutable |
| `test_measure_coverage` ×2, `test_measure_derivation`, `test_rf1_semantic_pins::test_synth` ×8, `test_rf2_pre_move_pins::test_measure_output_bytes`, `test_public_measurement_publication` ×2, `test_public_measure_corpus`, `test_tp2_shared_fact_types` | GC2 and GC3 registered `filtered` and `any_of` guarded refusals, which entered the frozen band-4 frontier | **Code fix:** `gnd.synth.frontier` excludes the GC2 filter and GC3 disjunction variants, exactly as it already excluded Phase 6 guarded `exists`. All the drifted goldens reproduce unchanged |
| `test_rf1_semantic_pins::test_assurance_blocks` | The same rows entered the frozen Phase 3 assurance denominator | **Code fix:** `gnd.assurance.core._phase3_target` excludes them, as it already excluded guarded `exists`. The RF4 body successor for `_phase3_target` is recorded |
| `test_rf6_packages::test_original_definition_body_is_verbatim` ×18 | GC1–GC3, GW0, LD2 (`07a2bb06`) and the LX3 review (`9e1c1d29`) changed pinned bodies | Chained RF6b rows in [source-successors.json](source-successors.json), registered in `tests/support/rf9_ci_sources.py`. The two definitions on the model-composition chain get rows in [definition-successors.json](definition-successors.json), chained after MC3; `mc1_definition` now walks that chain |
| `test_rf4_peripheral` ×6, `test_rf9_ci_repairs` ×1 | LX1–LX4 changed `witness`, `_witness_inputs`, `replay`, `_run_check_raw` and `_run_check` | RF4 rows in the same file, each with the predecessor digest as `before` |
| `test_rf6_packages::test_package_size_targets…` | GC and GW took `model/_validation.py` to 5346 lines (ceiling 5000) | **Code move:** the ten unpinned GW/GC guarded validation additions move verbatim to the new `gnd.model._guarded`; it calls seven pinned helpers through a registry that `_validation` fills, as `_unattended` does. `parse_model_document` and `MAX_MODEL_BYTES` move verbatim to the new `gnd.model._parsing`. `_validation` re-exports every name, so lookups resolve as before. It is now 4989 lines. Both modules are in `tools/gnd_layers.json`, the home lists of `test_rf6_packages` and `test_atom_bind`, and the component index |
| `test_rf6_packages::test_new_package_scope…`, `test_atom_bind` | LX1 (`e2ce2ade`) added `model/flattening.py` | Added to both home lists. The measure and generation scans never import it, so a new test checks that the extraction and provider scans read it |
| `test_v6_phase2_adapter_mutations` ×11 | GW0 (`24c72d86`) moved scalar identity and order into `gnd.values`; GC2 rewrote the consequent site | Ten mutants are seeded in `gnd.values` and loaded into the adapter; the consequent mutant names the new site. Every mutant still kills its control |
| `test_public_semantic_guarded_join[comparison-polarity]` | GC2 moved the comparison into `guarded_pair_state` | The mutant names the new function and site |
| `test_rf1_pin_harness::test_mutation_table_rows_of_their_own` | GW0 moved `canonical_scalar` | A retarget row in `code-refactoring/evidence/RF9-ci-repair/mutation-retargets.json`, with the same failure meaning |
| `test_model_validation`, `test_model_v2` | GC1, GC2 and GW1 registered rules whose ids were not in the normative table | Five rows are added to the Layer 2 table in `gnd-orm-core/references/representation-format.md`. The inventory test names the shared ids and the loop-built ids explicitly, and the v2 scan reads every quoted rule id |
| `test_evolve_loading::test_h3…` ×2 | The LX3 review raises `ReferenceHashMismatch`, a subclass of `ReferenceInputError`, on a changed catalog | Two ruled rows beside the IKE-Q3 rows |
| `test_mc1_guards::test_R30…` | LD1, LD3 and PR 205 added include roots | Listed. The LD3 reading root is staged by `reading.py` with its vocabulary, so it is not loaded in place |
| `test_doctor_uninstall` ×4 | PR 198 delivered `handle-issue`, the components rules check and the review tool | The local skill files and root entries are pinned |
| `test_release_text` ×2, `test_pyrel_learning_path::test_short_paragraphs` | PR 191 pages named 0.2.0 and lengthened a list | Version-free wording, and two words shorter |

## Policy and pinned evidence touched (disclosed)

- `mutation-retargets.json` gains one row, which is the only update its reader allows.
- The Layer 2 rule table gains five rows for rules that merged code already registers.
- The layer allow-list stays empty.

Historical records keep their original hashes. They describe the bytes they were written
against. `tools/build_ci_repair_successors.py` rebuilds both successor files from the
current sources.

## Verification

See the PR description for the exact commands and results.
