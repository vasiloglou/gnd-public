No claim was refuted. Every file in the brief's table matched its SHA-256, and the checkout is `e2ce2ade32e1` with the tree clean apart from the untracked `notes/reviews/`.

## 1. Findings

**F1 — duplicated helper (style; nothing observable)**
- **Where:** `src/gnd/extract/service.py:242-253`.
- **What's wrong:** the new overlap check is written from scratch. The repository already has one: `gnd.evolve._includes.exclude_input_outputs` (`src/gnd/evolve/_includes.py:339`), which discover uses at `discover/service.py:570`.
- **How the two differ:** the new check also covers the root and the reference files, which is better. But it calls `destination.samefile(dep)` without handling a missing input, while the existing helper skips missing inputs.
- **Can it be reached?** I tried. With the output file already present and the reference file deleted, the second extract stopped at loading with exit 3 ("cat.pop.json could not be inspected"), before the overlap check ran. So the only way in is a file removed between loading and the check.
- **Suggestion:** reuse or extend the existing helper, and record that choice in the component index.

**F2 — record ordering is underspecified (style; nothing observable in LX1)**
- **Where:** `src/gnd/model/flattening.py:50-52`, and the representation-format text "Origins are sorted by composed address".
- **What's wrong:** origins are sorted as plain strings, so `$.object_types[10]` comes before `$.object_types[2]`. Verify compares the record byte-for-byte against one rebuilt by the same function, so LX1 itself can't fail.
- **Why it matters later:** any other producer, such as LX2, would have to copy this string order exactly. The normative text should say "string (code-point) order".

## 2. Checked and found true

I re-ran the four focused test files: `test_lx1_flattening`, `test_mc1_guards`, `test_li0_witness_wire` and `test_mc1_model_includes`. All 210 tests passed. Beyond that I ran public-CLI probes in temporary directories, now deleted.

**C1 — holds.**
- Two-include extract exits 0 and verify exits 0.
- Verify reads the root once with a size cap and checks its hash, then re-resolves it. It confirms the resolved root hash equals the indexed hash (`_authored_sha256 == model_actual`), which closes the gap between reading and loading.
- It then rebuilds the flat model and record from that same snapshot and compares exact bytes.
- When an include changes, verify exits 3 with `$.includes[1]: include:hash-mismatch`.
- When a reference file changes, verify exits 3 with "reference raw hash does not match".
- Reusing an old sidecar against a fresh re-extraction exits 3 on `model_sha256`.

**C2 — holds.**
- **Order:** root, then include, then flat model, then record. All of it happens inside `_verify_artifact_index`, before the model is loaded for checking.
- **Coordinated forgery:** the flat model and record are rebuilt rather than trusted, so a forged pair fails even when the index names both forged digests.
- **Missing binding:** if the marker is removed, `guard_bytes` refuses the include-bearing root. If the marker stays but one of the two digest entries is missing, the read fails with an error and refuses.
- **Opt-in:** an include-free root with an inserted marker exits 3 ("root model does not match the resolved include snapshot").
- **Hostile index JSON:** malformed index input is mapped to `extraction:binding-mismatch`.

**C3 — holds on everything I sampled.**
- I ran the phase base (`183972ea`) and the candidate side by side on 60 fixture models, with and without `--guidelines`, plus a verify against a tampered index. That is 208 cases, 88 of them successful extracts.
- Bundle file digests, stdout, exit codes and verify JSON payloads were identical in every case except `mc-vocabulary/project.orm.json`. That model has includes; the base refused it with `include:unsupported-route` and the candidate now extracts it, which is the intended change.
- The `model_wire` alias (identity is asserted) and the single source-scan owner are in place.

**C4 — holds.**
- An include placed at an output name exits 74 and stays intact.
- A reference population placed at `project.orm.applicable.json` with `--out` set to the root's directory also exits 74 and stays intact.
- Path, standalone, nested, references and unattended refusals keep their codes, now with the field named.
- Temporal include roots exit 3 in extract.
- Fidelity and doccheck still call `guard_path` before reaching the index, so turning on this bundle route doesn't open those commands to include roots.

**Interrupted publication:** the index is written last and binds the root's hash. Any mix of old and new files fails the digest or rebuild checks.

## 3. Could not check, and why

- **Full suites:** I didn't run the full guard suite, Ruff or `components_index.py changed`. I relied on the spec's recorded results for those.
- **Partial publication:** I didn't simulate a failure partway through the `os.replace` sequence. That rests on reading the code: index last, every artifact bound by digest.
- **Legacy reference overwrite:** I didn't confirm whether an include-free root's extract can overwrite one of its own reference files. The fixture I tried is temporal and is refused before publication. This is behaviour from before this phase, and C4's wording only covers include-bearing roots.
- **Not defects, but worth knowing:**
  - Include roots reached through a symlinked directory (e.g. `/tmp`, `/var/folders`) fail with `include:unreadable` in `validate` too, so this comes from the resolver, not LX1.
  - Include-backed bundles are rebuilt by the running GND version, so a version that changes `model_wire` will refuse older include bundles, as D2 intends.
  - The stale-include message names the include by position (`$.includes[1]`), not by its ID (`topics`).

VERDICT: APPROVE
