# Full default lane, base against GO1 head

Run on beast-3 on 2026-11-23 for the autouse write-check fixture in
`tests/conftest.py`. Six shards per tree (`ls tests/test_*.py | sort`, one
file in six per shard), `uv run pytest -q --tb=line -p no:cacheprovider`
under the default `addopts`. uv 0.13.7 and Python 3.13 on that machine, not
the CI pin.

| Tree | Commit | Passed | Failed + errors |
|---|---|---|---|
| base | `main` `11a7ebf7` | 19,916 | 30 |
| head | `92cc161f` | 19,941 | 30 |

The two failure lists are identical test for test (`diff` empty). The 25
extra passes are GO1's new tests. The list, pre-existing on `main` on that
machine:

```text
ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
FAILED tests/test_doctor_uninstall.py::test_diagnose_reports_every_placed_file_current_after_a_fresh_install
FAILED tests/test_doctor_uninstall.py::test_remove_adversarial_case[symlink-uninstall-never-follows]
FAILED tests/test_doctor_uninstall.py::test_remove_deletes_every_hash_matching_file_and_prunes
FAILED tests/test_doctor_uninstall.py::test_remove_unlinks_a_symlink_install_without_following_it
FAILED tests/test_guarded_clause_exports.py::test_existing_export_bytes_are_stable
FAILED tests/test_install.py::test_a_clean_install_places_every_skill_through_one_generic_path
FAILED tests/test_install.py::test_apply_into_an_empty_root_writes_every_file_and_one_manifest
FAILED tests/test_install.py::test_install_adversarial_case[zero-write-second-run]
FAILED tests/test_install.py::test_iter_skill_files_yields_every_packaged_file
FAILED tests/test_install.py::test_plan_against_an_empty_target_yields_create_for_every_file
FAILED tests/test_ir3_pyrel_includes.py::test_T3_rules_modes_reach_the_flat_models_refusal[checking.orm.json-duckdb]
FAILED tests/test_ir3_pyrel_includes.py::test_T3_rules_modes_reach_the_flat_models_refusal[checking.orm.json-lqp]
FAILED tests/test_ir3_pyrel_includes.py::test_T3_rules_modes_reach_the_flat_models_refusal[extraction.orm.json-duckdb]
FAILED tests/test_ir3_pyrel_includes.py::test_T3_rules_modes_reach_the_flat_models_refusal[extraction.orm.json-lqp]
FAILED tests/test_ir3_pyrel_includes.py::test_T6_include_free_programs_are_byte_identical
FAILED tests/test_rf1_pin_harness.py::test_mutation_table_rows_of_their_own
FAILED tests/test_rf4_peripheral.py::test_graph_predicate_is_live[cycle]
FAILED tests/test_rf4_peripheral.py::test_graph_predicate_is_live[lane-install]
FAILED tests/test_rf4_peripheral.py::test_graph_predicate_is_live[private-oracle]
FAILED tests/test_rf4_peripheral.py::test_graph_predicate_is_live[unmapped]
FAILED tests/test_rf4_peripheral.py::test_graph_predicate_is_live[wrong-way]
FAILED tests/test_rf4_peripheral.py::test_graph_targets
FAILED tests/test_rf5_handler_pins.py::test_original_handler_bytes[install]
FAILED tests/test_verification_fixes.py::test_f01_a_forced_run_over_the_same_root_still_writes_its_receipt
FAILED tests/test_verification_fixes.py::test_f01_a_run_that_placed_nothing_and_owns_nothing_writes_no_receipt
FAILED tests/test_verification_fixes.py::test_f01_doctor_does_not_date_and_version_a_root_gnd_never_wrote
FAILED tests/test_verification_fixes.py::test_f01_the_aliased_install_is_fully_removable_by_uninstall
FAILED tests/test_verification_fixes.py::test_f01_two_targets_aliasing_one_directory_leave_a_receipt_owning_the_files
```
