# IK4 adversarial review

**One reviewer is one reviewer.** One local general-purpose agent reviewed
`git diff 3e1ef3e a6947a4`, the IK4 implementation on top of the approved
corpus. It wrote only to a session scratch directory.

Before fixing, the author reproduced R1, R2 (with its stderr leak), R3, R5 and
R7 directly, and R4 and R6 through the reviewer's fixtures. Each fix has a
regression test in `tests/test_discover.py`. All 18 of them fail when run
against a copy of `a6947a4`'s source and pass afterwards. The R13 tests kill
the reviewer's surviving mutants D1, D3, D7 and D11 (4 of 4), and pass on the
unmutated `a6947a4` copy.

## Disposition

| ID | Class | Disposition | Regression test |
|---|---|---|---|
| R1 | blocking | **fixed:** all discovery identities are the checker's typed identity (F11) | `test_r1_typed_identity_matches_the_checker` |
| R2 | blocking | **fixed:** value rules skip opaque or unrepresentable columns, and defect messages carry no candidate body | `test_r2_opaque_cells_skip_value_candidates_and_never_leak`, `test_r2_repository_opaque_fixture_exits_0_without_canaries` |
| R3 | blocking | **fixed:** references are bound from the model's directory, as loading by path does, and passed to the check run. Previewing such a proposal is refused by evolve itself, which predates IK4 (F12, IK4-Q2) | `test_r3_reference_bearing_models_bind_their_references` |
| R4 | blocking | **fixed:** mandatory rules are skipped on object types a derived fact type plays (F14), and any checker exception is exit 70. The underlying checker defect predates IK4 (F17, IK4-Q4) | `test_r4_derived_rosters_never_crash` (2 fixtures) |
| R5 | blocking (privacy) | **fixed, owner ruling (o):** redacted roles get no value rule and are counted | `test_r5_redacted_roles_never_emit_their_values` |
| R6 | blocking | **fixed:** a size budget, with the excess counted in `skipped.over_budget` (F16) | `test_r6_candidates_past_the_size_budget_are_skipped_and_counted` |
| R7 | blocking | **fixed:** a candidate that JSON cannot spell is written as block YAML, without aliases, and round-trips to evolve's replay. Previewing a date-bearing model is refused by evolve itself, which predates IK4 (F12, IK4-Q3) | `test_r7_yaml_only_model_values_round_trip` |
| R8 | hardening | **fixed:** a blank `--actor` is exit 64 | `test_r8_blank_actor_is_a_usage_error` (2 cases) |
| R9 | hardening | **fixed:** outputs aliasing each other or an input are exit 64. A stale `--out` is documented as left untouched | `test_r9_outputs_must_not_alias_each_other_or_an_input` (3 cases) |
| R10 | hardening | **fixed:** each input is read once through a capped reader (F15) | `test_r10_inputs_are_read_once_through_the_cap` |
| R11 | hardening (spec) | **fixed, owner ruling (o):** the corrected formula is implemented as `work.ceiling` and enforced | `test_r11_work_never_exceeds_the_stated_ceiling` (2 shapes) |
| R12 | completeness | **fixed, owner ruling (o):** a declared frequency of at most 1 feeds `superkey` | `test_r12_superkeys_of_a_declared_frequency_max_1_are_suppressed` |
| R13 | completeness | **fixed:** tests for exact work counts, the 256-example cap, exclusion's both-sides rule and minimal keys. The fast-path parity test now uses `POOL` Number identities. The semiderived skip is recorded as intended (F14) | `test_r13_*` (4), `test_typed_number_identities_match_the_specification` (3) |

## Reviewer report (verbatim)

The reviewer's final message, unedited except that its headings are demoted one
level.

### IK4 adversarial review: `git diff 3e1ef3e a6947a4`

#### 1. Verdict
**Not ready to merge.** The three checker fast paths match `semantic_spec.verdict_of` exactly; I found no divergence (C6 holds). But `gnd discover` crashes (exit 70 or exit 1) on several realistic inputs, including shipped examples and repository fixtures. It also writes values from roles marked `redact: true` into the proposal, the report and stdout.

All scratch work is under `S=<scratch>/ik4-review`. Commands below run from the worktree. `ARGS` means `--actor a:b --requested-at 2026-10-24T12:00:00+00:00`. No repository file was modified.

#### 2. Findings

**R1 (blocking): discovery and the checker disagree on what counts as the same value. Falsifies C1 and C3.**
- **Cause:** `support.cell_key` uses `json.dumps`, so `1` and `1.0` are different values. The checker treats them as the same (token `1/1`).
- **Repro:** model `$S/r1/m.orm.yaml` has one `Number` value type played in two fact types. Population `$S/r1/p.population.yaml` has `amount: 1` in one and `amount: 1.0` in the other.
  - `uv run gnd discover $S/r1/m.orm.yaml $S/r1/p.population.yaml --out … --report … ARGS` gives exit 70 with `ERROR: internal: fact_types[a_tagged].constraints[0] passes but discovery counted violations`.
  - `--families subset` and `--families equality` fail the same way, on `constraints[0]`.
  - With `p2.population.yaml` (`1` and `1.0` in one column):
    - the value candidate is emitted with `allowed: [1, 1.0]`, a duplicate;
    - uniqueness on `amount` gets support 2/2 from discovery but a checker `warning`, so the support numbers are wrong and a near-miss there can never be seen.
- **Fix:** key every scan on the checker's typed identity (`semantic_adapter.canonical_scalar(value, primitive)` → `(identity_kind, token)`). Deduplicate `allowed` and count `--max-values` on that identity.
- **Regression test:** a corpus case with `1` / `1.0` across two fact types. Expect exit 0, the mandatory/subset/equality candidates emitted, and a single entry in `allowed`. It fails today with exit 70.

**R2 (blocking): opaque cells give exit 70, and the error leaks redacted values to stderr. Falsifies C1.**
- **Repro 1:** `$S/r1/p7.population.yaml` (`format_version: 2`, `amount: {"$opaque": "secret-1"}`) gives exit 70: `a generated candidate failed validation … 'allowed': [2, {'$opaque': 'secret-1'}]`.
- **Repro 2:** the same happens on the repository's own fixtures: `tests/fixtures/v70-phase5/{private,public,public-shuffled}.pop.json`, `v70-phase3/join-opaque.pop.json`, `v70-phase6/negation-opaque.pop.json` and `pyrel-rules-derivations/review/der-opaque-v2.population.json`.
- **Leak:** for `v70-phase5/private.pop.json`, stderr contains `SECRET-ROLE-CANARY` and `SECRET-OPAQUE-CANARY`. `tests/test_v70_phase5_adversarial.py:80` asserts the first must never reach stderr.
- **Fix:**
  - skip value candidates for a column holding any opaque cell, and count it as skipped;
  - never put a candidate's body into the `DiscoveryDefect` message.
- **Regression test:** discover on `v70-phase5/public.pop.json` exits 0, and no canary appears in stdout, stderr or either output file.

**R3 (blocking): models that use references crash with a traceback (exit 1).**
- **Repro:** `uv run gnd discover src/gnd/examples/dispatch/model.orm.json src/gnd/examples/dispatch/seed.pop.json --out … --report … ARGS` raises `gnd.references.ReferenceInputError: reference-bearing model requires a bound reference context` from `service.py:164` (`check(checked_model, checked_population)`).
- **Contrast:** `gnd check` on the same pair runs normally (exit 1, a violation).
- **Also affected:** `examples/release`, `tests/fixtures/reference-corpus/{dispatch,release}`, `v71/phase2|3/dispatch` and `pyrel-rules-calendar/refonly`.
- **Fix:** resolve and pass the same reference context `gnd check` uses. Map `ReferenceInputError` to exit 3.
- **Regression test:** discover on the dispatch example exits 0 and its preview exits 0.

**R4 (blocking): derived and semiderived fact types still feed the mandatory rosters, giving exit 70 or exit 1.**
- **Cause:** discovery skips these fact types as hosts, but its roster (`universe._instance_values_of`) still includes their claimed or computed rows, which the checker's roster does not.
- **Repro, exit 70:** `tests/fixtures/v62-phase1/models/static.orm.yaml` with `populations/pre-clean.pop.yaml` (also `post-exact`, `pre-unrelated-gap`) gives `fact_types[evidence].constraints[0] passes but discovery counted violations`. `pyrel-rules-derivations/review/ring.orm.json` with `ring-claim-other-cycle.population.json` gives the same.
- **Repro, exit 1:** `v62-phase5/models/floats.orm.yaml` with `populations/float-clean.pop.yaml` ends in an uncaught `ValueError: witness for 'snapshot:mandatory:inline:violated:deontic' has no admissible origin`.
  - `$S/find_crash.py` narrows it to the mandatory candidate on `rb_sample.rb`, whose roster includes computed `rate_floor` values.
  - This is a checker bug that already exists at base 3b65d15. Running `gnd check` on the dumped candidate (`$S/r10/cand.orm.json`) gives 70 at both base and head. Discover does not catch the exception.
- **Fix:**
  - take rosters from the checker snapshot, or skip mandatory candidates on object types that derived fact types play;
  - wrap unexpected exceptions from `check` as `DiscoveryDefect` (exit 70);
  - file the checker bug separately.
- **Regression test:** these four fixtures exit 0.

**R5 (blocking, privacy): roles marked `redact: true` leak their raw values.**
- **Repro:** `uv run gnd discover tests/fixtures/v62-phase1/models/static.orm.yaml tests/fixtures/v62-phase1/populations/pre-clean.pop.yaml --families value --format json …` exits 0. `SECRET-ITEM-314159` (from the role `evidence.item`, which is `redact: true`) appears in the proposal (2×), the report (1×) and stdout (1×). `gnd check` on the same inputs prints it 0 times.
- **Context:** IK4-D6 approved raw values in value candidates, but nobody ruled on roles the model itself marks for redaction.
- **Fix:** skip value candidates on redacted roles (count them as skipped), or require an explicit opt-in.
- **Regression test:** grep for the canary across all outputs finds nothing.

**R6 (blocking): the candidate document can exceed the 10 MiB model cap, giving exit 70 with default bounds.**
- **Repro:** `$S/r1/big-tag.population.yaml` is 6.0 MB: 20 distinct strings of about 300 KB of backslashes, which double in size once escaped as JSON. It gives exit 70: `a generated candidate failed validation: model exceeds the 10 MiB input cap`.
- **Same failure by design:** a large `--max-pairs` reaches it too, because every survivor carries up to 256 example ids.
- **Fix:** budget the candidate's serialized size, and count over-budget candidates under `skipped` instead of failing. Alternatively, check the candidates in batches.
- **Regression test:** this population exits 0 and the report says what was skipped.

**R7 (blocking): a valid YAML model with an unquoted date crashes the command (exit 1).**
- **Repro:** the staff model plus `source.created: 2024-01-01` (`$S/r8/d.orm.yaml`). `gnd validate` says OK, but discover raises `TypeError: Object of type date is not JSON serializable` in `output.candidate_text`.
- **Fix:** turn YAML scalars into JSON-safe values the same way evolve canonicalizes, or refuse the model with exit 3.
- **Regression test:** this model exits 0 and its preview exits 0.

**R8 (hardening): `--actor ""` (or whitespace only) crashes with a pydantic `ValidationError` traceback (exit 1), after the whole discovery run.**
- **Fix:** validate the value in argparse, so it exits 64.
- **Regression test:** `--actor ""` exits 64.

**R9 (hardening): output paths are not checked against each other or against the inputs.**
- **Repro, all in `$S/r6`:**
  - `--out X --report X` exits 0. The report overwrites the proposal, yet its `proposal` field still names X.
  - `--out <MODEL>` exits 0 and overwrites the input model with the proposal (the SHA changed).
  - A run with zero candidates leaves a stale file at `--out` while the report says `proposal: null`.
- **Fix:** refuse outputs that resolve to the same path as each other or as an input (64 or 74). On zero emission, remove or refuse an existing `--out`.

**R10 (hardening): inputs are read whole, before the size cap, and read twice. Breaks the spec's standing rule 1 (inputs only through the capped loaders).**
- **Cause:** `discover()` calls `model_path.read_bytes()` and `population_path.read_bytes()` before the capped loaders, then reads both files again.
- **Repro:** a 419 MB population (`$S/r6/big.population.yaml`) peaks at 486 MB of memory (`/usr/bin/time -l`) before the cap refuses it with exit 3. `gnd check` on the same file peaks at 66 MB.
- **Second effect:** the digest in the proposal and report comes from a different read than the population that was loaded, so a file changing between the reads goes unnoticed.
- **Fix:** read each file once through the capped reader, then use `load_*_bytes` on those bytes.

**R11 (hardening, spec): the IK4-D7 work ceiling is not an upper bound. Falsifies the general form of C4; the corpus fixture N1 still passes.**
- **Cause:** the mandatory, value and frequency scans run once per role, not once per fact type, and the roster charge is not bounded by R (the total fact rows).
- **Repro (`$S/r2`):**
  - one 4-role fact type with 1,000 rows and `--max-pairs 0`: work total 31,000 against a ceiling of 18,000;
  - 300,000 roster instances with 2 fact rows: work total 300,022 against a ceiling of 1,060.
- **Fix:** an owner ruling to correct the formula (per-role terms plus roster terms), or enforce a limit.

**R12 (completeness): superkeys of a key implied by a declared `frequency max:1` are still emitted.**
- **Repro:** `$S/r7` (a 3-role fact type with an alethic `frequency {max:1}` on `a`). It emits uniqueness on `{a,b}` and `{a,c}`.
- **Why:** the `superkey` rule looks only at declared uniqueness constraints. Read literally, the catalogue does not say otherwise, so this needs an owner ruling.
- **Fix:** add the role sets of declared `frequency max:1` constraints to the `superkey` rule's set.

**R13 (completeness): some behaviour has no test.**
- **Mutants that survive `tests/test_discover.py`:**
  - D1: exclusion's "both sides non-empty" rule is removed;
  - D3: the `redundant-superkey` rule is disabled;
  - D7: the roster work charge is dropped;
  - D11: the example cap drops from 256 to 255;
  - D12: the derived/semiderived skip is disabled.
- **Spec drift:** the code also skips `semiderived` fact types, while the spec names only derived ones.
- **Unused test data:** in `tests/test_ik4_indexed_set_families.py`, `POOL` (with True/1/1.0/"1") is declared but never used, and every test value is a string. Typed identities are therefore never exercised, although my own differential found no divergence.

#### 3. What held
- **C6 (fast paths equal the oracle):** no divergences.
  - 9,731 comparisons on snapshots built through the adapter from random models: String, Integer, Float, Number, Boolean and Date roles; single and joined sequences; internal and external frequency; modality flips (`$S/diff_fast.py`).
  - 16,734 comparisons with the IR mutated: variant, refused, bad or invalid bounds, family swaps, dropped sequences or role refs (`$S/diff_ir.py`).
  - The shipped fast-path test kills my fast-path mutants M1–M5.
  - `gnd check` output is identical at base and head, apart from the version, on 120 fixture pairs (`$S/checkdiff.py`).
- **End-to-end fuzz:** 900 random models, including entities with reference schemes, subtypes, 1-, 3- and 5-role fact types, declared constraints at fact-type and top level, and empty or partly covered fact types (`$S/fuzz_e2e.py`).
  - Every run exited 0, and every emitted ref passes `check`.
  - Each ref points at exactly the constraint the report shows, and support equals the T5 oracle.
  - All 246 previews I ran exited 0.
- **Idempotence:** running discover again on the K08 candidate model emits 0 candidates and suppresses the rest.
- **Shipped tests:** the 128 `test_rf*.py` files plus `test_public_built_inventory.py` gave 2384 passed. `test_discover.py` plus the fast-path tests gave 135 passed.
- **Shipped data:** 216 of the 241 example and fixture populations I ran exited 0.

#### 4. What I could not check
- IK2's D-12 gate on its own, apart from `evolve preview`.
- Actually triggering the read race in R10.
- Byte determinism under different `PYTHONHASHSEED` values on fuzzed inputs; only the corpus T13 covers it.
- Run time on the near-cap case.
- Windows or case-insensitive path aliasing for R9.
