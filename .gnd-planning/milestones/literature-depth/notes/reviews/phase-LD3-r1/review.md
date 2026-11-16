# LD3 r1 review

All 27 SHA-256 values listed in the brief match the files, and HEAD is `92086a00f0a2`. I am reading the bytes the brief names. I edited nothing in the repository. My probe scripts are only in `/tmp/ld3probe`, and the only other file I wrote is the planning note this session requires.

`uv run pytest tests/test_ld3_reading_workflow.py tests/test_li1_assurance_report.py`: **89 passed** (6 min 44 s).

## 1. Findings

**F1 (C3 is false; high). The fidelity gate does not measure what the run actually read.**
- **Where:** `src/gnd/examples/literature/reading.py:283-313`, `:356`, `:458-461` and `reading_fixture/calibration.json`.
- **What is wrong:**
  - `_calibrate` scores two candidate populations written by hand in `calibration.json` against `gold.json`. It never uses the facts the producer extracted.
  - It sums recall over `system` and `approximation` only. The predicate the absence claim is about, `alternative_integrator`, is in neither the gold nor the candidates.
- **Consequence:** the absence claim is "qualified" whatever the reader extracted.
- **Reproduction (run):**
  1. Copy the fixture.
  2. Change the `study-methods` approximation in `responses.json` to "Velocity Verlet at 10 K with 5 fs steps". The source says Langevin at 300 K.
  3. Re-pin `facts_sha256` in `reviews.json`, then call `reading.run(...)`.
  4. Result: fidelity is still `{'high': [2,2], 'low': [1,2]}`, absence is `{'status': 'qualified'}`, and the targeted verify and check both exit 0.

This contradicts "qualifying actual fidelity" and the plan's "measure `gnd fidelity` recall on held-back gold for the exercised fixture".

**F2 (C2 is partly false; medium). The reported conflict is never extracted from a source.**
- **Where:** `reading.py:379-388`.
- **What is wrong:** the two conflicting labels and their one-line document are hard-coded in the code. The control source's only saved response (`control-table`) is `"refused"`.
- **What is real:** the verify and check exit 1 are genuine. I ran them and both fail on the `subject_label` uniqueness constraint.
- **What is missing:** the plan's "Reproduce a reported violation through extraction and checking" and the spec's "the synthetic source control returns both conflicting label facts". Changing `control.txt` or `responses.json` cannot affect this result. I confirmed that by reading the code.

**F3 (low–medium). The revisit list is not limited to earlier sections or sections already read.**
- **Where:** `reading.py:155-158` and `:448-449`.
- **What is wrong:** `affected_sections` returns every available section that shares a key. That includes `study-methods`, the same targeted attempt that proposed the key.
- **Reproduction (run, routes stubbed):** give `study-equation` the key `method-family`. The revisit list becomes `['study-opening','study-methods','study-equation']`, even though `study-equation` was never inspected.
- The docstring ("earlier") and the plan ("relevant older source spans") say otherwise.

**F4 (low). A required question that has been superseded blocks the "completed" stop.**
- **Where:** `reading.py:440-443`.
- **What is wrong:** `required <= resolved` never counts a superseded question as resolved.
- **Reproduction (run, routes stubbed):** set `old-method.required = true`. The stop becomes `available-evidence-exhausted`, even though its successor `method` is resolved and nothing was omitted.

**F5 (low). The read denominator reports no unavailable reads while coverage shows one.**
- **Where:** `reading.py:494-499`.
- **What is wrong:** `read_denominator.unavailable` counts only targeted ranges removed by the `unavailable` scenario.
- **Consequence:** in a full run it reports `unavailable: 0`, while the coverage table has `annex-method` → `unavailable`. That may be intended (the section was never scheduled), but the README says unavailable ranges "count in the roster".

**F6 (low, design). Replay depends on the producer's saved-response table.**
- **Where:** `reading.py:28` and `:170-173`.
- **What is wrong:** retained responses are only compared for equality with the fixture's `responses.json`, and that file is a required input. Replay could not work for a producer that has no saved table.
- With this fixture the outcome is the same, so I found no observable failure today.

**F7 (style). One absence-gate binding checks bytes against themselves.**
- **Where:** `reading.py:461`.
- In `_evaluate`, the pins passed to `absence_status` are hashed from the very bytes being checked, so that binding proves nothing on this path. Only closure → `scope_sha256` is an independent binding.

**F8 (style, test gap). Nothing shows a reading run feeding the assurance scorer.**
- **Where:** `assurance_report.py:722-760`.
- The assurance coverage scoring needs LI1 corpus passage IDs and a `coverage: {sha256}` field in the run's `run.json`. A reading run's `run.json` has neither, and no test connects the two.

## 2. Checked and found true

- **C1, order and authentication:**
  - The manifest must be canonical (`:394`), and its file list must be exactly the expected set.
  - The stage records are checked for name, predecessor hash and payload hash before any other file is read. The restricted-read test proves this.
  - Every other file is hashed before payloads are decoded.
  - The re-derived manifest and all evidence files must equal the retained ones byte for byte. A coordinated re-pin of `coverage.json` is still rejected, and a missing file exits 3.
- **C1, no producer calls:** replay passes no producer object, so no producer can be called.
- **C1, counts:** fresh-run producer counts are cross-checked against the attempts recorded in the evidence (`:435`).
- **C2, stop reasons and cost:**
  - Each of the three stop reasons can be reached.
  - Reading cost equals the sum of attempted lengths. I also checked intermediate budgets of 139, 191 and 234 bytes.
- **C2, coverage:**
  - Coverage states are distinct and match the expected file.
  - The approximation fact appears only after the targeted pass.
  - The semantic review blocks stale facts before the public routes run.
- **C3, absence inputs:** removing or altering any one of the four inputs gives "unavailable", and the 1/2 recall case is refused.
- **C3, legacy scoring:** results are unchanged when the coverage stanza is absent from both the run and the answer key. The LI1 goldens differ only in the documented `harness_sha256` rewrite.
- **Assurance adapter:** it refuses when only one side has the stanza, refuses duplicates and fails on omitted rows. `ExampleError` is a subclass of `ValueError`, so its error handling covers coverage-reader errors.

## 3. Not checked

- Installed-wheel runs of the fresh and replay commands (T10). I ran from the worktree only.
- The broader LD1, LD2, extraction and fidelity tests, Ruff, and the component checks. I did not run them.
- Some of my probes replaced the public routes with stubs to save time. Only the F1 probe and the conflict-output check used real GND routes.

VERDICT: CHANGES_REQUESTED
