Retained Claude Code stdout, 2026-10-13. No text substitutions.
Instrument: Claude Code 2.1.281, opus, high effort, safe mode, plan permissions,
Read/Grep/Glob only, stdin prompt, no session persistence. One reviewer is one
reviewer. Initial OAuth failure produced no opinion; native reauthentication
succeeded before this completed invocation. The reviewer could not run git or
tests; root reproductions and measured gates are separate evidence.

# PA0 independent adversarial diff review (one reviewer)

**Verdict:** I refuted parts of PA0-C1 through C4. Four findings are material. The first should be resolved before PA0 is recorded complete. The second and third should be resolved or explicitly ruled on before PA1.

Several things did hold up:
- **Counts:** 61 obligations = 5 + 5 + 8 + 20 + 23. There are 124 cases (61 positive + 59 negative + 2 missing + 2 extra). 48 guarded targets and 6 derived targets are red, giving 70/124 matched. 128 tests = 1 + 124 + 1 + 2. Fixture lines total 4092 + 1511 + 124 + 8 = 5,735.
- **Model addresses** match the runtime's enumeration order.
- **Modality** matches the three BookRec model files (deontic only in `model.orm.yaml`'s `preferred_genre`).
- **Guarded positives are non-vacuous.** I checked every guarded rule's positive target, and the inclusive cap boundaries (75, 1500, 2000, 3000, 100) are exercised.
- **Successor red is real.** Every mismatch in `successor-red.txt` is either `unsupported` on a guarded rule or a missing derivation verdict. Nothing went red for any other reason.

## Findings

**1. The frozen GND row contradicts the contract's "computed facts feed `all_eligible`" rule (High).**
- In `answers.json:752-776` (`m2-book_is_eligible-extra`), `constraints[3]` (`all_eligible`) is frozen as `fail` with witness `{$b: night, $u: ada}`.
- night/ada is only a *supplied* claim (`m2-book_is_eligible-extra.population.json`). Computed eligibility excludes it: night is adult-rated, ada is a minor, so the pair is blocked.
- So GND fed the forged claim into the completeness check. Spec lines 122-124 say "no supplied derived claim enters the native definitions. Native computed facts feed guarded completeness checks."
- **Consequence:** the obligation-level agreement required by spec lines 136-139 and PA2-C4/PA6-C2 (100% within the denominator) cannot be reached by an implementation that follows the contract. A full-row comparison would instead reward one that trusts the claim.
- No case pins the computed behaviour either. No population omits a computed-eligible pair from both the recommendations and the claims. PA0 records none of this as a known divergence.

**2. The driver's acceptance predicate only checks the target row (Medium).**
- At `tools/measure_pyrel_applications.py:67-75,105`, successor and acceptance modes compare only `verdicts[target]` to one status.
- They ignore: non-target rows, witnesses, overall `status`/`exit_code`/`accepted`, the `binding` hashes, and modality.
- `observed_gnd_exit` is copied into receipts (line 80) but never compared. Spec line 140 says exits *are* compared for the acceptance contract.
- **Consequence:** an implementation that reports `warning` for `m0-r4-negative` but then blocks with exit 1 still counts as matched. That is the plan §6 risk "deontic warnings block". So is a false violation on any non-target rule.

**3. Successor mode can't go green without changing the legacy report (Medium).**
- Successor mode runs the legacy program without `--accept` (line 57). It still expects status `warning` and a `derivations[].derivation_ref` array.
- Spec lines 57-60 freeze the legacy `report_document`/schema-v1 surface, and that surface has no modality (`pyrel_runtime.py:1151-1179`).
- Lines 72-74 are dead code: they recompute exactly the line-71 comparison, despite a comment implying special handling.
- **Consequence:** once PA1/PA2 land in a contract-conforming way, `m0-r4-negative` stays red because of the legacy interface, not because guarded support is missing. That conflicts with spec lines 50-51 and 177 ("1 before PA1/PA2").

**4. The consumer inventory is incomplete (Medium).**
- `matrix.json:1496-1510` omits:
  - `tests/test_rf2_pre_move_pins.py:82-87`, which pins the SHA-256 of the rendered standalone program bytes (that program embeds `pyrel_runtime.py`) under RF9 successor evidence.
  - The rf1-pins helper goldens for `pyrel_runtime.write_new` / `_load_yaml`.
  - `tests/test_pyrel_constraint_oracle.py`, which plan §9 names as a PA0 starting point.
  - `tests/test_public_pyrel_oracle_isolation.py`.
  - `tools/gnd_layers.json` (required by PA-R7).
  - `docs/runtimes/pyrel.md` and `docs/reference/cli.md`.
- **Consequence:** any PA1 edit to `pyrel_runtime.py` breaks pins that PA0 never inventoried, which bypasses the RF9 owner routing that spec line 26 promises.

**5. Frozen witnesses are never checked (Medium-Low).**
- `answers.json` `guarded_witnesses` are not compared to anything by `tests/test_pyrel_application_corpus.py:41-49`, and the driver doesn't read them.
- The "canonical witness" part of the answer key is therefore not executable and can drift silently.

**6. The uniqueness controls only test exact duplicate rows (Medium-Low).**
- All 14 uniqueness negatives repeat an identical tuple. For example, `m0-r0-negative.population.json` lists `cosmos/science` twice.
- No case gives one book two *different* genres, or one expense two different amounts or employees, which is the actual business violation.
- Spec line 87 also says native rows are deduplicated as logical tuples, which is in tension with these expected `fail` answers.

**7. The inventory test misses some broken links (Low).**
- `test_matrix_exhausts_exact_models_and_controls` (lines 33-38) does not check that:
  - each row's positive/negative/extra case targets that row's `ref` and model;
  - the `expected`/`target` values in the matrix agree with those in `answers.json` (the two tests read different copies);
  - the matrix `kind`/`modality`/`id` metadata matches the model.
- I spot-checked the current data and it is consistent. There is just no liveness control for these links.

**8. Some stories are wrong or templated (Low).**
- Positive stories reuse the negative text. For example, `matrix.json:630` says "Duplicate … violates" for a population with no duplicate.
- The finance story ("fails independently of category policies", e.g. `matrix.json:1169`) is contradicted by the frozen row `answers.json:2234` (`constraints[9]` also fails). It can't hold in this model at all: every category cap is ≤ 3000. The same applies to `m4-r21-negative`.

**9. No unknown or vacuous controls exist (Low).**
- All 124 populations cover every relation. GND recorded no `unknown`/`vacuous` verdicts, despite the §6 discharge claim on spec line 21.
- Under the contract, rows with known-empty antecedents (e.g. the team-lead limit in most expense cases) would be `vacuous`, while GND froze `pass`. The normalization mapping between those is undefined.

**10. Driver and receipt hygiene (Low).**
- The documented C2/C4 command (spec line 176) targets the existing `baseline.json`, which carries the stale matrix digest `6e599…`. Because of `open("x")` at line 98, re-running it fails *after* the full native run. The command actually run used `baseline-current.json`, and the spec was not amended.
- The driver uses the internal `render_pyrel` rather than the `gnd export pyrel` CLI, and `write_text` with no encoding.
- The embedded `MODEL_NAME` is an absolute path, so `program_sha256` depends on the machine.
- Hashes are computed by re-reading the files after execution.
- The `assert` gates (lines 45, 63, 102) vanish under `-O`.
- Baseline mode never checks `process_exit` or `error` statuses.

**11. Informational.**
- Every population's `population.model` says `model.orm.yaml` or `model.orm.json`, even when paired with the strict, complete or currency model.
- The three BookRec models share one `model_id`, so model-ID binding can't tell them apart.
- Many positives are byte-identical; for example, all m0 and m1 positives have `population_sha256` `d97d…`. "124 controls" means 124 case entries, not 124 distinct inputs.

## Coverage and limits

- **What I read:** the whole plan, the PA0 spec, `002`, the driver, the test file, `matrix.json`, the README, and roughly 25 population files.
- **Spot-checked:** parts of `answers.json`, the evidence `.txt` receipts, the summaries and `successor-red.json` receipts (by grep), the five model files, `emit.py`, the relevant parts of `pyrel_runtime.py`, and `commands/export.py`.
- **Not executed:** I had only read/search tools, so I ran nothing. I did not recompute any SHA-256 (fixtures, receipts, spec prefix, lock), run git diff to confirm production is unchanged, or re-run pytest or the native driver.
- **Taken from the receipts, not reproduced:** the 128 / 72 pass counts, the runtime versions, and the population hashes. `reference-isolated.txt` doesn't record its command, so it can't be reproduced.
