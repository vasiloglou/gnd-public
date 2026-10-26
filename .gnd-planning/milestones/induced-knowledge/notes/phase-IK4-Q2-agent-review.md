# IK4-Q2 adversarial review: one local reviewer agent

**One reviewer is one reviewer.** One local reviewer agent read the working-tree
diff against B = `8f89af4` (the IK4-Q2 fix, before the review fixes), with the
spec, `evolve/service.py`, `evolve/cli_service.py`, `gnd.model` and the test
file. The author then reproduced each finding before believing it. The
disposition follows the report.

The report keeps the agent's findings, numbering, severities, reproductions and
verdicts. Its layout was set as markdown, and its scratch paths are shortened to
`$S` (a session scratch directory, not retained). It is not a byte copy.

## Report

No blocking defect: nothing tried made a reference-bearing model exit 70
through the binder. Two hardening and four completeness findings.

1. **Completeness: reference-free behaviour changes for `.json`-named models.**
   `load_model_bytes` picks its parser from `Path(source).suffix`. The source
   was a temporary `model.orm.yaml`; it is now the real workspace path, so a
   `*.json` model and its candidate are parsed as strict JSON. A reference-free
   `orders.json` holding YAML text previews at 0 on B and at 3 now ("current
   model validation failed: model JSON input refused"). A JSON model with a YAML
   candidate gives 0 on B and 3 now. The new behaviour is arguably the correct
   one: B published YAML bytes into a `.json` model that `gnd validate` then
   refuses. But the change is undisclosed, spec §5 says there is none, and T6
   cannot catch it.
2. **Hardening: a candidate with different reference declarations is bound
   before the replay check.** `_validated_candidate`, which now binds, runs
   before the comparison with the replayed operations. A candidate whose
   reference path is changed to `references/other.pop.json` (digest recomputed)
   gives 66, "candidate model validation failed: artifact
   references/other.pop.json could not be inspected". The same tamper without a
   reference change gives 3, "declared operations do not equal the canonical
   candidate model". Expected: 3. A proposal can make preview read any regular
   file under the model directory, within the binder's caps, before it is
   refused. Never 70; read-only and confined.
3. **Completeness: binding is untested at 5 of the 7 load sites.** With a
   mutant in which only the "current model" and "current model at apply" loads
   bind, `tests/test_evolve_references.py` gives 8 passed. Finalize can be
   observed: with the reference removed after publication, finalize gives 66;
   restored, 0. T2 does not assert the record exists, though exit 0 implies the
   chained finalize ran.
4. **Hardening: `except Exception` around `bind_references` reports an
   internal binder defect as 3.** A monkeypatched `TypeError` gives "exit 3 ...
   current model validation failed: simulated internal defect in the binder".
   This matches `load_model`'s `_load_model_no_follow`, so it is parity, not a
   regression. An error that is already a `ReferenceInputError` is wrapped in a
   second one with the same message (cosmetic).
5. **Completeness: invalid YAML in a candidate still exits 70 (pre-existing).**
   Candidate text `version: 1\nmodel_id: [unclosed\n` gives 70 on B and now:
   ruamel's `YAMLError` is not caught. Outside IK4-Q2's literal scope, but this
   phase rewrote the loader.
6. **Completeness (docs): the contract sentence covers three outcomes.**
   Observed, none 70:
   - 74: a reference that is a directory, a fifo, mode 000, a dangling link, or
     whose `references/` directory is a link;
   - 66: the `references/` directory is missing;
   - 3: an absolute or `..` declared path, an invalid population with a valid
     digest, a file over the 10 MiB cap.

   The spec names the parameter `reference_root`; the code uses `model_path`.
   Same meaning.

**Tried with no defect found:**
- empty, garbage, non-UTF-8, bad-JSON and duplicate-key reference files: 3;
- a model in a nested subdirectory: 0; a hard link: 0, as `gnd validate`;
- the exit mapping checks causes first; no binder message carries a stale
  marker;
- apply after a removed, linked or changed reference: 66, 74, 3, model
  unchanged; finalize re-run after restoring: 0, then 0 again;
- swapping the model directory between reads: the declared digest still binds;
- removing `tempfile` is safe; nothing patches it or `service.load_model`;
- `.orm.yaml`, `.yml` and extensionless models: preview bytes identical to B;
- the test file: 7 fail and T6 passes on B; all 8 pass with the fix;
- impact suite: 3144 passed.

## Disposition

Each finding was reproduced with the reviewer's harness before it was acted on.

| # | Class | Disposition |
|---|---|---|
| 1 | completeness | **Fixed for parity.** The loader parses as B did: a `.json` name does not select the strict JSON parser. Regression `test_r1_a_json_named_reference_free_model_previews_as_at_b` previews a `.json`-named copy of T6's model to the same golden bytes; red before the fix (3). Whether evolve should instead parse as `gnd validate` does is **IK4-Q2-Q1**, for the owner. |
| 2 | hardening | **Fixed.** A candidate whose reference declarations differ from the current model's is refused (3) before binding, at preview and apply. Regression `test_r2_...`; red before the fix (66). |
| 3 | completeness | **Fixed with tests.** `test_r3_every_load_site_binds` counts binds (2 at preview, 9 through apply and finalize; apply first rebuilds the preview). `test_r3_finalize_binds_the_staged_models` pins finalize (66, then 0). Both fail on the reviewer's mutant. |
| 4 | hardening | **Kept, for parity** with `load_model`. Recorded in the boundary. |
| 5 | completeness | **Deferred** as **IK4-Q2-Q2** (pre-existing, B gives 70 too). |
| 6 | completeness | **Fixed.** The contract sentence names every observed class. The parameter name is recorded in the record. |
