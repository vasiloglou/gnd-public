# LX4 r1 phase-diff review

I found three ways to get forged evidence past `interop verify`, so my verdict is changes requested. The core chain holds up: tampering with rebinds, roots, composition, check, witness or replay is refused. What gets through are provenance fields, one indexed artifact, and a stray `dates.json`. The rest of my findings are gaps in measurement and test coverage.

All 36 SHA-256 values in the brief matched the files, so I read the bytes it names. I made no repository changes. I ran the example and the probes in `/private/tmp/lx4rev` and `/private/tmp/lx4probe`.

## 1. Findings

**F1 — Forged provenance in the handoff files passes `verify`.** `src/gnd/examples/literature/interop.py:145-160` writes the extraction sidecar and `document.manifest.json` from fixed values. `verify` (`interop.py:302-339`) never rebuilds those values or compares them to the fixture. It only checks their digests in `interop.json`, which the forger rewrites.
- **Consequence:** a run can claim a different producer and still verify. For example, the sidecar can say `executing_model: "claude-opus-forged"` and `skill_version: "99"` instead of `saved-public-fixture`.
- **Repro:**
  - P2: edit the survey sidecar, recompute `rebind.json` with `interop._rebind`, rebuild `interop.json` with `_manifest`. `verify` exits 0.
  - P3: change `executing_model` and `renderer_skill_version` in `document.manifest.json`, rebuild `interop.json`. `verify` exits 0.
- **Control:** a forged population header is caught by `gnd verify` (P7 exits 3).

**F2 — A tampered indexed artifact passes `verify`.** `artifacts/extraction.orm.verbalization.txt` is listed with a digest in `extraction.orm.artifacts.json`. Neither `interop verify` nor `_verify_artifact_index` checks it, because it is not in the required set (`src/gnd/extract/service.py:108-128`). It is also not in the manifest's `stage_files` (`interop.py:279-281`).
- **Consequence:** the extraction instructions can be replaced while the index still records the old digest, and the run still verifies. This contradicts C3's "binds each cross-stage artifact".
- **Repro (P1):** overwrite the verbalization file, rebuild `interop.json`. `verify` exits 0.

**F3 — A forged `dates.json` can sit in a verified run.** `verify` reads `with_dates` from the recorded manifest (`interop.py:307-309`) and checks `dates.json` only when that flag is true (`interop.py:337-338`). It never checks for files outside the manifest.
- **Consequence:** take a `--dates` run, change the counts in `dates.json` (for example `pass: 3, advisory: 0`, which hides the PINN advisory), and rebuild `interop.json` with `dates=False`. `verify` exits 0 and the forged report stays next to the verified files under its expected name.
- **Repro (P5):** reproduced; exit 0.
- **Note:** the `dates` subcommand recomputes the advice, so only the copy left in the run directory is affected.

**F4 — Most of the copy census is hard-coded.** At `interop.py:296-298`, only `document` is measured (with `samefile`). `extraction_population: 0`, `extraction_sidecar: 0` and the two rebound counts are written as constants.
- **Consequence:** if a later change copied the extraction population or sidecar, the census would still say 0 and `verify` would still pass. The spec asks to measure copies by artifact kind; C3 says "measured layout".
- I found this by reading the code; I did not build a copying variant.

**F5 — Two spec'd test pairings are not done as written.** Both are coverage gaps, not product defects.
- **T4 ordering:** the spec asks to pair an invalid rebind with an input that would fail the temporal clause. `tests/test_lx4_literature_interop.py:145-162` monkeypatches `_check` and `_advice` instead. That does show ordering, but no temporal-failure input is used.
- **T2 allowance control:** `test_lx4_literature_interop.py:250-270` builds the larger-allowance root, then composes and checks sources whose `rebind.json` still names the old checking root. `gnd compose` and `gnd check` accept them, because the population header binds only the model path and model id.
  - So the flip to a failing verdict is real, but it is shown on a run that has stale rebinds, not on one the example verifies. C1's "verified rebinds precede composition" holds inside `interop verify`, not in the product commands.
  - The test's last assertion only checks for exit 3 from `gnd verify`, not the reason.

**F6 — Low: day-precision dates are compared by year only.** `interop_dates.py:94-101` reduces two day-precision dates to their years. A child dated `2020-01-01` and a parent dated `2020-12-31` therefore report `pass`. The README documents year comparison, so this matches the stated scope, but the report gives no reason for that pass.

## 2. What I checked and found true

- `run --dates` and `verify` both exit 0 on this tree.
- The 160 tests I ran pass: LX4, MC1 guards, MC2 consumers, fidelity payload and public fidelity scope.
- **Temporal clause:** it is really evaluated, not vacuously satisfied. Both works have rows (submitted plus 1 day versus published, 57 days apart in each), and an allowance of 3650 days fails.
- **Composition:** `gnd check --composition --sources` re-derives the composition (`checking_service.py:_composition_view`), so a forged composed population or record is caught.
- **Rebind:** it snapshots the inputs, re-hashes them after `gnd verify` runs, and checks root digests against the loaded `_authored_sha256` values. Roots with different pins or catalogs are refused.
- **Advice:**
  - It uses the LI5 policy's chainable and non-chaining lists.
  - It reports two passes and one PINN advisory (2019 to 2021).
  - It reports five unresolved edges, each with its stated reason.
  - The non-chaining edge stays outside the census.
  - "Bayesian PINNs" does not appear in the composed facts.
  - Without `--dates`, the composition, check, witness and replay bytes are identical.
- **Witness:** its targets are checked against `targets.json`, and a valid witness for a different target is refused.
- **Fidelity census:** it requires `ran == 2`, and a failed case with a re-pinned report is refused.
- **Fidelity include guard:**
  - An include root with no `.artifacts.json` still refuses with `include:unsupported-route` (MC1 test R25).
  - A bundle without a flattening binding goes back through `guard_bytes`.
  - The applicable-set bytes are checked against the bundle digest.
- **Other guards:** the `checking_service` `getattr` change only restores the raw include guard for a model object that lacks the attribute. The R30 inventory adds exactly the two new roots.
- Header forgery in the extracted population is caught (P7 exits 3).

## 3. What I could not check

- **Full gates:** I did not run whole-tree Ruff, the structure lane, the component check or the wheel build. These need `uv` or network access, and plan-mode limits applied.
- **Unsupported combinations:** I did not re-run the LX1–LX3 controls for them. No LX4 test covers T8; it rests on those earlier suites.
- **Issue #193:** I did not look up the issue or the DOI years.

VERDICT: CHANGES_REQUESTED
