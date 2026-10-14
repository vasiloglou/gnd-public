# Claude Code PA3 bounded repair review

Edited header; repository absolute paths sanitized to <repo>. Remaining reviewer prose retained. Reviewer reports no Python/tests/native execution or credentials reading. One reviewer is one reviewer; this is the final selected review round.

I couldn't write the plan file or call ExitPlanMode because neither tool is available in this session, so the review is below.

I stayed within your rules: I only read files and ran read-only git, grep, sed, ls, stat and date. I didn't run Python, tests or native tools, and didn't read `.env` or credential files. I did grep the native SDK's source under `tutorials/runtimes/.venv` without executing it. The working tree changed during the review: the README and architecture contract changed at 17:18 and are now modified. I re-checked `applications.py` (228 lines), `native_query.py` (122) and both test files after those edits, and the code I reviewed is the current code.

# PA3 bounded repair review

## Verdict per original finding

- **F1 (checker replacement): repaired.**
  - The runtime is rendered once, before the query runs, and kept in parent memory (`applications.py:175`).
  - The checker directory is a new temporary directory created only after the query child has returned (`:200`).
  - All its files are written with expected-absence regular writes (`publish_leaf_atomic`: no-follow staging, link with no replace).
  - Its build directory is new, and no path the query created is reused.
  - The `--accept` checker uses only the embedded `MODEL_TEXT`. The embedded `MODEL_NAME`, which points into the query directory, is never read on that path (`pyrel_runtime.py:1739-1764`).
  - The native test `test_native_fresh_checker_rejects_query_replacement_attack` is the one that discriminates: it requires exit 1 with `age_appropriate` violated, which proves the real checker ran.
  - The parent version, `test_query_cannot_replace_independent_checker`, uses the dev `sys.executable`. It would also pass if the real checker simply failed to run (for example, a missing SDK gives 70), so it only shows that nothing was published.
- **F2 (asserted-fact erasure): repaired for facts, with one gap in metadata (R1 below).**
  - The library has an `owned_relations=()` option, validated to name distinct asserted, non-derived facts.
  - The CLI passes only `("recommendation",)`.
  - The fact inventory must equal the source facts plus the derived heads.
  - Every fact that is neither owned nor derived must match the source exactly as a multiset (rows compared as type-exact JSON).
  - Coverage must equal the source coverage plus any derived heads it didn't already list.
  - Nothing in the parent names BookRec relations.
- **F3 (query crash read as rejection): repaired.** Only exit codes 2 and 3 pass through; everything else becomes 70 (`:180`). The crash test asserts 70 with `policy is None`.
- **F4 (malformed candidate): repaired.** Checker exit 3 returns the last 300 bytes of its stderr before any attempt to read the report (`:209-211`). For exits 1 and 2, a report must still be readable; a missing one gives 70, which is fail-closed.
- **F5: matches your description.** The dead collision branch is gone. Input equal to output is caught by the existing-output check and refused with 2 (tested). I confirmed in `artifacts.py:1228` that the publisher creates missing parent directories with `mkdir(parents=True)` and refuses a symlinked root.
- **F6: the branches are reached.**
  - Missing interpreter: 70 with the specific reason.
  - Invalid model: 3, `model validation failed`, and the child is never called.
  - Malformed input: 3, `population facts must be a mapping`, raised by the query child.
  - Wrong version: the test double reaches `native_query.py:46-47`. It does not reach the checker's own version check at `pyrel_runtime.py:1676`.
  - Unknown user and limits 0 and 101: reason assertions are present.
  - Empty unknown coverage: asserts `relation-not-covered-or-listed`.
  - The five fault cases each name the exact violated rule or derived head.
- **F7 (child environment): the environment-variable claim holds.** Children get only PATH, LANG, LC_ALL, LC_CTYPE, TMPDIR, TEMP, TMP and SystemRoot, plus a fixed `RAI_BUILD_DIR`. A real child process confirms `PA3_TEST_SECRET` and `RAI_ENGINE` are absent. The limitation is in R4 below.
- **F8 (pessimistic work bound):** unchanged and disclosed. **F9 (stale figure receipt):** handled by the rename to `figure-source-initial.json` plus the new `figure-source-repaired/` data; see R5.

## New findings from the repairs

**R1 — Low: metadata and instances are compared with Python `==`, not type-exactly** (`applications.py:134-138`).
- Python treats `1`, `1.0` and `true` as equal, so a value can change type and still pass the check.
- The checker's type checks make this harmless for instances (`Integer` requires an int, `Boolean` a bool). But free-form keys — top-level keys other than facts and population, and population keys other than `covers` and `model_id` — are not validated anywhere.
- **Test case:** a source containing `"population": {"covers": [...], "revision": 1}`, with a transform that sets `revision` to `true` (or `1.0`). Predicted: exit 0, and the published bytes contain the changed value.
- BookRec's seed probably isn't affected, but the general "retain captured metadata" claim is.
- **Fix:** compare canonical `json.dumps(..., sort_keys=True)` forms, as the fact comparison already does.

**R2 — Low: files are staged under the model's own filename, which can collide with fixed names.** All outcomes are refusals; none publish.
- In the checker directory, a model named `candidate.json` or `runtime.py` causes a publication collision and exit 70.
- A JSON model named `policy.json` makes the checker exit 11. The parent then reads the model file as if it were the report, returning 70 with the model document as `policy`.
- In the query directory, a model named `seed.json` is overwritten by the input before `render_pyrel` reads it, giving a misleading exit 3.
- The model copy in the checker directory is only read by the test double (`simulated_child`); production never reads it.
- **Fix:** use a fixed staged name, or don't stage the model for the checker and render from the captured bytes.

**R3 — Low: some tests can pass through the wrong branch.**
- `test_review_source_and_malformed_boundaries` asserts only `exit_code == 3`. It doesn't pin `candidate changed asserted source facts: user_rated_book` for the F2 case, or the checker's stderr text for the F4 case. So "preserves bounded stderr" is implemented but not tested.
- None of these branches has a test:
  - the coverage, instances and metadata checks in `_preserve_source`;
  - validation of `owned_relations` itself;
  - BookRec with the default `owned_relations=()`, which should refuse.

**R4 — Low (claim scope): the children don't get HOME at all.**
- With HOME unset, Python resolves `~` from the user database to the real home directory.
- The native SDK's config discovery mentions `~/.rai/raiconfig.yaml` and `~/.snowflake/config.toml` (`relationalai/config/config.py:105-107, 696-701`).
- I didn't confirm whether passing an explicit `Config(**local_config())` skips that discovery. So "no ambient credentials" holds for environment variables but isn't shown for files.
- **Fix:** set HOME to the private directory, which is cheap.

**R5 — Evidence.**
- 19 native tests are now collected (7 CLI + 5 faults + 1 + 1 + 2 + 2 + 1), but `native-repaired.txt` shows "18 passed". `fresh-checker-native-green.txt` shows "1 passed, 18 deselected", so 19 were collected in that run.
- No single receipt covers all 19. That fits your "ongoing, don't credit" note, but the final run should show 19, or explain why not.
- The README (17:18:38) and architecture contract (17:18:21) were edited after `focused-repaired.txt` and `lint-repaired.txt` (both 17:16). Only `architecture-contract-green.txt` is from 17:18; I didn't compare the seconds.

## Remaining limitation (disclosed, not a finding)

A query child that detaches into its own session (via `setsid` or a double fork) is not covered by `process_group_cleaned`. It could watch for `gnd-native-checker-*` and tamper with that directory. This is within your "trusted local code, not host-sandboxed" statement, and the spec wording "after query group cleanup" is accurate.

## Other claims I confirmed by reading

- **Budgets:**
  - Parent: 228/600.
  - Example source: 138/300 (`native_query.py` 122 + 16 CLI lines).
  - Tests since PA2 (`672bf35`): about 466/500 (186 + 278 + 2).
- **Layers:** the layer registry adds only `gnd.export.applications` in the export lane.
- **Old path:** the old GND CLI path is unchanged.
- **README:** the new text matches the code.

## What I did not check

- I didn't hash anything: the successor/delta JSON, the figure snapshots, or the framework runtime/model/corpus bytes.
- R1, R2 and the R4 home-directory behaviour are predictions from reading the code; I didn't run them.
- I didn't verify the native SDK's runtime behaviour.
