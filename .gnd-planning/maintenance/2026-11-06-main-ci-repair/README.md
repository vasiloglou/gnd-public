# Main CI repair, 2026-11-06

The owner asked for this repair after a local replay of `.github/workflows/development.yml`
on `main` at `e8a21f0e` (macOS, Python 3.13). The replay found 24 regression failures; the
candidate build, release acceptance and documentation jobs passed. The same test files pass
at `f650d2a9` (PR 80). Every failure comes from work merged since then that changed pinned
code, or added to a size-capped file, without updating the matching record. Each fix below
uses the repository's own mechanism and names the commit it accounts for. No pin is loosened
and no check is removed.

| Failure | Cause | Repair (mechanism) |
|---|---|---|
| `test_plan_app_docs` ×2 (`compose-documents.md`, `grow-a-model.md`) | CT5 (`2bc40473`) and the grow-a-model page (PR 85) have paragraphs over 90 words, three exit codes in prose and one banned term | Six paragraphs are split at a sentence boundary with no word changed; `exit 0`, `exit 1` and `exit 3` leave three result lines (the recorded output beside each still shows the code); "the binding digests" becomes "the digests the witness binds" |
| `test_rf6_packages::test_package_size_targets…` | MG5 (`7961119c`) took `model/_validation.py` to 5236 lines (ceiling 5000); CT2 (`2c25ba4d`) took `checker/_core.py` to 2464 (ceiling 2400) | **Code move:** the MG5 unattended-source rules move verbatim to the new `gnd.model._unattended`, and `check_with_composed_anchors` to the new `gnd.checker._composed`, as IK2 did with `_induction`. Both are added to `tools/gnd_layers.json` and to the home lists in `test_rf6_packages`, `test_rf3_core`, `test_atom_bind`, `test_public_registry_runtime` and `test_public_derivation_parity_local`. `_validation` registers its walks with `_unattended`; `_composed` looks up `_check_dispatch` and `_anchored_verdicts` on `_core` at call time, so patches of the defining home still apply. `gnd.model._validation._rule_unattended`, `gnd.model.unattended_span_issues` and `gnd.checker.check_with_composed_anchors` resolve as before |
| `test_rf4_peripheral` ×5 (`witness`, `replay`, `_run_check_raw`, `_run_check`, live control) | CT2 (`2c25ba4d`) and CT3 (`4584415f`) added the composition keywords after the recorded successors | The four RF4 rows' `after` and `reason` are extended in `compiled-snapshot-obligations/evidence/CI/source-successors.json` |
| `test_rf5_commands` ×8 (handler bodies) | CT2 changed `_cmd_check`; MG2 (`d8e8a3a7`), MG3 (`41be0290`), MG4 (`9e36e70c`) and MG5 changed `_cmd_evolve_apply`, `_cmd_evolve_preview`, `_evolve_emit_claim`, `_evolve_error_exit`, `_evolve_same_review_identity`, `_cmd_extract` and `_cmd_validate` | The `_cmd_check` row is extended and seven RF5 rows are added to the same registry, each with the predecessor digest as `before` |
| `test_rf6_packages[gnd.checker._anchored_verdicts]` | CT1 (`f20f5c38`) allowed several anchors per fact role | The RF6b row's `after` and `reason` are extended in the same registry |
| `test_rf5_commands::test_all_parser_paths…` | CT2 added `gnd compose` | The parser count is 58, with the command named beside it |
| `test_rf5_handler_pins[install]` | TS3 (`51ec0a3a`) and TS4 (`3fe48d2a`) ship four more skill files | The recorded `install` answer says 69 files |
| `test_rf5_commands::test_entrypoint_rule…`, `test_rf5_review_regressions`, `test_rf7_structure` (graph), `test_rf8_structure` | Four command-to-non-service imports: `commands.checking` to `gnd.model._validation` and `gnd.anchors` (MG5) and to `gnd.artifacts` (CT2); `commands.discover` to `gnd.disclosure` (CT4, `077a611d`) | **Code fix:** `commands.checking` imports `unattended_span_issues` from `gnd.model`, an already permitted target. **Policy:** three reasoned exceptions are added to `tools/gnd_entrypoints.json` for the other three edges (disclosed below) |
| `test_rf7_structure::test_complete_routing…` | CT2 `api.compose` and TS1 (`fc38f752`) `discover/type_evidence.py` call `json.loads` directly | **Code fix:** both decode through `gnd.input_policy.loads`. Each input is the package's own canonical JSON, so results are unchanged |
| `test_rf6_query_policy` ×2 (dynamic inventory; caused by this repair's move) | `check_with_composed_anchors` changed file | A new chained, authenticated delta, [dynamic-query-successor.json](dynamic-query-successor.json), whose predecessor is the TS2 delta: nine rows change path only. `tests/support/pyrel_application_successors.py` reads the link |

## Policy and pinned evidence touched (disclosed)

- `tools/gnd_entrypoints.json` gains three exceptions: `gnd.commands.checking` to `gnd.anchors`
  (the document byte cap) and to `gnd.artifacts` (canonical JSON for `gnd compose` output),
  and `gnd.commands.discover` to `gnd.disclosure`. Each records an import that merged code
  already makes. Routing them through a service instead is a design change left to the owner.
- `compiled-snapshot-obligations/evidence/CI/source-successors.json` is pinned by
  `compiled-snapshot-obligations/007`. Six existing rows have `after` and `reason` extended and
  seven rows are added, which are the only updates the registry allows.
- The layer allow-list stays empty.

Historical records keep their original hashes. They describe the bytes they were written
against.

## Verification

See the PR description for the exact commands and results.
