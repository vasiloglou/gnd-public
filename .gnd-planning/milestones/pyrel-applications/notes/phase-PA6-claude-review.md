Retained one independent initial Claude Code reading. Prose unchanged; no operator paths present. Raw SHA-256 9a825556adbf375fcda5fd214de097bced502a33d6fe7dd479a7a0d888f55afd. Reviewer disclosed one empty no-op Python invocation outside the read-only instruction; no project/native/provider execution. No third review.

# PA6 review: first reading

**Verdict:** None of my findings undermines the acceptance numbers so far. But the receipt as written doesn't bind everything the spec's receipt schema lists (findings 1–3), so it shouldn't be credited until that's repaired. The bounded repair can cover findings 1–5.

**How I read:** read, search, read-only git, `stat`, `shasum` and `unzip -l` on the target wheel. I edited nothing. Plan mode gave me no write or ExitPlanMode tool, so there's no plan file and this message is the whole review. One deviation: I ran `python3 -` once with an empty heredoc. It did nothing, but it was outside the no-Python rule. I didn't open `.env`, credentials, `.agents/skills/` or `.playwright-mcp/`.

## Findings

1. **The receipt misses several artifacts the spec requires (medium-high).** Line 125 only hashes `.json/.yaml/.py/.svg` files inside the four `*-work` folders. These are not bound:
   - The four step receipts (`*-steps.json`), which carry the per-page and per-block hashes and statuses.
   - `isolation.py` and `isolation.json`, so the generated program's SHA and the import-isolation proof are missing.
   - The copied `run_tutorials.py`, `check_docs.py`, `docs/`, `overrides/` and `zensical.toml`.
   - The rendered `site/` and the link-check result. Only stdout/stderr hashes (lines 63, 128) touch these indirectly.

2. **Source identity is captured late and too coarsely (medium).** The commit, the dirty flag and `harness_sha256` are read at the end of the run (lines 127–128), not at the start.
   - The harness file isn't committed, so `source_commit` 1d6c0c6 doesn't contain the code that ran.
   - `source_dirty` is a single true/false, and it will be true because of the edited spec and unrelated untracked folders.
   - Timing: the target folder was created at 18:50:03 and the harness was last modified at 18:50:01, so its current bytes (`a0d90fd8…`) are probably what ran. Nothing in the receipt proves that.
   - The measurement driver already does a start/end self-check (`measure_pyrel_applications.py:252`); the harness should do the same.
   - Fix: capture identity at the start, record a hash of the dirty-path list, and commit the harness before the final run.

3. **A skipped native block would still pass (medium).** `execute_paths` ignores `status: skipped`, and `run_pages` only prints a message. The 7 BookRec and 4 Expense chapter counts and the 5 native (pyrel) blocks aren't pinned either. The current step files show 0 skips in both native-lane runs (52 and 34 blocks); the 2 and 3 skips in the offline runs are the expected native blocks. So this isn't failing today, but the spec's "no skipped native accepted" isn't enforced.

4. **The native environment install differs from the documented one (medium-low).** `docs/runtimes/scenario.md:41,45` tells installed-wheel readers to run `--locked --only-group tutorial-runtimes --python 3.13`. The harness (line 79) uses `--frozen --no-dev --group tutorial-runtimes` with no `--python`.
   - The lock isn't checked against `pyproject.toml`.
   - The Python version is whatever uv finds (3.13.12 this time).
   - The command readers actually follow isn't exercised.

   It matches the spec text, and the first failed run was a harness bug, not a docs gap.

5. **The C2 numbers aren't asserted (low).** Line 118 checks 137/137 only. It doesn't check 2,321 comparable rows or exactly 2 A1 differences. The `agreement()` function and the frozen approval file already bound these, but the spec names them.

6. **The installed GND137 script doesn't check its own completeness (low).** It records matched and denominator but never asserts they're equal. It doesn't check that the matrix and answer case sets are the same, and it doesn't check the approval SHA before using them. The native driver does that check later.

7. **The six-SVG inventory is implicit (low).** The required list comes from scanning the source tree, so deleting an SVG from both source and wheel would pass. Docs/assets twin equality is only pinned by a checkout-side test (`tests/test_pyrel_tutorial_experience.py:23`). `check_docs.py` only checks links that exist; it doesn't assert the six graphic URLs are present.

8. **Environment and dependency hygiene (low).**
   - Credentials: the shell environment, minus five keys, reaches uv, the tutorial blocks (`run_pages` copies `os.environ`), the native blocks and zensical. The measurement driver allowlists `PATH`, `HOME` and `TMPDIR`.
   - The native config is explicitly local DuckDB (`pyrel_runtime.py:1136,1680`), so "no credentials in config" holds. "No credentials in the process environment" isn't enforced.
   - Unlocked dependencies: the base install resolves GND's dependencies without the lock, and zensical's transitive dependencies are also unlocked.
   - Not recorded: the resolved base and docs-tool versions, and the base Python version.

9. **The isolation probe is narrow (low).** It covers the BookRec export only, not Expense. The AST check is a substring heuristic. The `sys.modules` check doesn't catch a bare `tests` module.

10. **The red-first evidence is weak (process).** All eight reds in `install-red.txt` failed because the harness didn't exist yet, not because each refusal discriminated. Nothing tests the 12 MiB cap refusal. `focused-current.txt` (412 passed, 10 deselected) doesn't record the command or what was deselected.

## Claims I checked

- **Diff since 1d6c0c6:** only the 7-line spec note. It matches the `install-initial.txt` failure (`PackageNotFoundError: relationalai`) and the `--group` fix at line 79.
- **Output root:** line 57 refuses an existing path or one inside the checkout, after resolving symlinks.
- **Origin check:** it compares whole path components, rejects a sibling folder, and resolves symlinks and editable installs back into the checkout. The measured origin is under `b/base`.
- **Wheel:** 1,848,435 bytes compressed, 6,665,594 uncompressed, 564 entries (both under the 12 MiB cap). It contains all six SVGs, both `native_query.py` files and the runtime `pyproject.toml` and `uv.lock`, and no `tests/`. SHA `905920994a69…`.
- **Model mirrors:** copied from the installed package (lines 72–78). All 137 cases use the 5 models under BookRec and Expense.
- **Native environment:** `find_spec('gnd')` is None under `-I`; versions are 3.13.12 / 1.30.1 / 1.5.5.
- **Native report:** it binds the runtime, tool, matrix, answers, lock, model, population and program SHAs.
- **Budgets:** harness 134 lines (limit 200), tests 58 lines (limit 100).
- **Layers:** the harness imports only the public `gnd.safefs`.

## What I couldn't establish

The run is still going. At 18:54:40, `native-corpus.json`, `receipt.json` and `site/` didn't exist. The log then moved past the measurement step, but I make no claim that native137, the render or the receipt completed.

I didn't verify the zensical build, the browser review, how the relationalai SDK handles config and environment, the full chapter contents, or the one `.env`-pattern match in `src/gnd/recovery/inventory.py`.

## Refactoring assessment

The harness is within budget and passes lint, but it's dense one-line code. It writes three Python scripts into the target as string literals, and `check_gnd_corpus` copies the logic in `tests/test_pyrel_application_corpus.py:63-70`, so the two can drift. I'd move those into committed target-side tools and pull receipt assembly into its own function that captures identity at the start. This isn't blocking and has no layering impact.
