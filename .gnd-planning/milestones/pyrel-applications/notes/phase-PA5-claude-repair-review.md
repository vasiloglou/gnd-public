Retained one independent Claude Code bounded repair reading; no third pass. No operator paths in reviewer prose; unchanged. Raw output SHA-256 1e27a3004a4bf077f5222b1d3f1f18f7804965f76818cec516f334c6db62e227. Producer owned final repairs and later current-byte gates are separate from this opinion.

# PA5 repair reading (second and final)

Most of the repairs hold. Two don't fully: F1 (word/number spacing) is only partly fixed, and some of the retained "final" evidence was produced before the current bytes. The rest of F2–F11 hold, with small leftover gaps listed under Low.

**How I read.** Read, search, read-only git, `jq`, `shasum` and image viewing only. I ran no Python, tests, native tools, providers or agents, and opened no `.env`, credentials or `.agents/skills/`. I edited nothing. Plan mode gave me no write tool, so there is no plan file; this message is the whole review. The producer's measured tests, native runs and layout checks are their claims. I only compared their transcripts, receipts and timestamps against the current bytes. Nothing changed while I read: I hashed the files at the start and again at 18:31:05 and they matched.

| File | sha256 prefix |
|---|---|
| `docs/bookrec/07-native.md` | `a868e0c9b3b9` |
| `docs/expense/04-native.md` | `3e67bd5eb601` |
| `tools/run_tutorials.py` | `1b4816705c6f` |
| `tests/test_pyrel_tutorial_experience.py` | `1f35966d849f` |
| `tests/test_external_runtime_tutorials.py` | `c7ca07764295` |
| `docs/assets/application-diagrams.js` | `3ce9b9185315` |
| `docs/assets/styles.css` | `e008c90acc02` |
| BookRec / Expense `sources.json` | `c0e67333eb20` / `e21f61135913` |
| `phase-PA5-spec.md` | `a54be2c80c9d` |
| The six SVGs | match the `sha256` values in their manifests |

## Findings

### Medium

**M1. F1 is only partly repaired.** The chapter prose and alt text are now clean of letter-followed-by-digit gluing. The SVGs are not:
- **SVG `<desc>` text is still glued** in all three Expense SVGs. The `<desc>` is what `aria-labelledby` points to when the shipped SVG is opened directly:
  - `expense-currency.svg`: "totals2260", "only103", "so101/102", "report2260 EUR"
  - `expense-flow.svg`: "total2260 EUR"
  - `expense-limits.svg`: "meal60", "meals75", "team-lead100", "Expense102", "travel800", "travel2000", "finance3000"
- **Visible labels still glue at punctuation:**
  - `expense-limits.svg`: "Category PASS:800 ≤ 2000" and "Repair:102 → finance". Both show in `render/expense-1-mobile-default-clean-left.png`.
  - `expense-currency.svg`: "EUR;101/102 missing", "Repair ·101/102/103" and "60 +800 +1400 =2260 EUR"
- **Prose:** `docs/expense/04-native.md:110` has "103;101/102".
- **Why the red regression missed these:** the test (`tests/test_pyrel_tutorial_experience.py:134-137`) only checks Markdown outside code fences, and only for `[A-Za-z][0-9]`. It never reads SVG text or `<desc>`, and doesn't catch digit-then-letter or punctuation gluing.

**M2. Some evidence is older than the current bytes.**
- **Last focused run predates the final edits:** `completion-focused.txt` is from 18:23:40. `docs/expense/04-native.md` changed at 18:23:41 and `tests/test_pyrel_tutorial_experience.py` at 18:24:21 (the same second as `completion-lint.txt`). So no retained focused run covers the current test file, or the prose and region tests against the current Expense chapter.
  - The native bound receipts (18:24) are current: their `page_sha256` values match both chapters now.
- **Frames named "final" show old bytes:**
  - `render/*-top-final.png` are from 18:16, before the prose fix. `expense-mobile-default-top-final.png` still shows "Expense102 costs800".
  - `*-left-final.png` (18:16) predate the SVG edits at 18:18 and 18:20.
  - The current frames are `page-final`, `clean-*`, `render-observations.json` and the keyboard green record, all 18:25–18:27. Rename or annotate the stale ones.
  - `expense-mobile-default-page-final.png` still shows the floating "On this page" overlay. `render-observations.json` explains it as a transient overlay, which is plausible, but the frame itself doesn't show that.

### Low

**L1. F2: the value bindings are real but partial.**
- **Bound now:** five Expense cap and limit numbers, the currency `allowed[0]` value, and the five book genres, each tied to a JSON path in the model or seed file.
- **Still bound only by substring or not at all:**
  - the standalone "75" in the caps table
  - the per-expense amounts in the flow and currency SVGs (60, 800, 1400)
  - the finance ceiling in "800 ≤ 3000" (constraint index 11)
  - the 2000 in "PASS:800 ≤ 2000"
- **"EUR only"** isn't checked as a one-element list. Only the file hash protects it, and the mutation test shows a regenerate-and-rehash gets past hash-only checks.
- **Unasserted links that do hold today:**
  - `strict.json` `population_sha256` equals `advisory.candidate.json` (`34a16283…`), which proves the "same candidate" claim.
  - Each refusal report's `population_sha256` equals its pinned input hash.
  - The test only compares population hashes when a row has a `candidate` key, so neither link is checked.

**L2. Keyboard helper** (`docs/assets/application-diagrams.js`):
- It swallows modified arrow keys, such as Alt+Left or Cmd+Left for browser back.
- It swallows Home/End even when the figure doesn't overflow, e.g. on desktop, where Home/End would otherwise scroll the page.
- Suggested fix: return early when `event.altKey`, `event.metaKey`, `event.ctrlKey` or `event.shiftKey` is set, or when `region.scrollWidth <= region.clientWidth`.

**L3. Runner interpreter handling** (`tools/run_tutorials.py`):
- **Relative native path:** the native interpreter isn't required to be absolute. Preflight resolves a relative path from the runner's working directory, but blocks run from the temporary work directory. That fails safely with no row written, but `native_python` at `:91` is recorded raw.
- **Same as base:** the native interpreter may equal the base interpreter. Separation is only visible in receipts. The bound receipts do show two distinct environments, `.venv` and `tutorials/runtimes/.venv`.
- **Dead fallback:** the default in `env.get(..., python)` at `:102` is unreachable unless `require_runtime` is stubbed.
- **"Measured" overstates it:** `runtime_versions` at `:62` are the pinned values returned after preflight passes, not values read from its output.

**L4. Leftover chapter wording:**
- `07-native.md:58` still says "Solid arrows"; the SVG legend was fixed but this caption wasn't.
- The alt text and `<desc>` omit Ben/read.
- `07-native.md:156` says "Native SDK 0"; "an SDK exit 0" would be clearer.
- `04-native.md:167` has "at most50 EUR" in the generated provenance quote.

**L5. Before committing:**
- Operator paths still appear in `reader-prose-red`, `graphic-binding-red`, `interpreter-selection-red`, `receipt-*-red` and the bound receipts. Record the raw digests before sanitizing, as the producer committed to.
- The untracked `.playwright-mcp/` directory should not be committed.

## Confirmed claims

- **F1 (prose and alt text only):** the chapter prose and alt text are clean of letter-digit gluing. "PyRel 1.30.1", "chapter 6" and "Exit 2" are fixed.
- **F2/F11:**
  - Source hashes are compact, with no whole-model copies.
  - Raw model and input bindings are present, and `source_binding` is compared.
  - Candidate hashes equal the policy-binding population hash where a candidate is retained.
  - strict, complete, currency and refusal inputs are pinned.
  - The USD checkpoint captures `unsupported-currency` with `policy: null`.
  - Ben/night is checked in the advisory candidate facts and in the native block (`07-native.md:90`). The advisory and strict selected pairs are asserted at `:88`.
- **F3:** exact witnesses are asserted in native blocks: `[{"$e":102,"$a":800}]` at `04-native.md:88` and `[{"$u":"ada","$b":"read"}]` at `07-native.md:138`.
- **F4:**
  - **Before any work:** an existing, symlinked or parentless receipt path is refused (`:164`).
  - **No overwrite:** publication goes through the public `safefs.artifact_publish_leaf_atomic` (`:183`), which links without replacing and raises `ArtifactError` on collision, so the race test exits 2.
  - **Rows:** they record group, parent/page, page hash, code hash, base/native/block interpreter paths and versions. A page changed during a run is refused (`:125`).
  - **Failures:** a failed run raises before publication.
- **F5:** `GND_TUTORIAL_PYREL_PYTHON` is required. The test double asserts the child's `sys.executable` is the separate symlink path and that the GND variable equals the base `--python`. Existing runtime pages already require the variable.
- **F6:** keyboard red (scrollLeft 0, max 202) is recorded, then green for all 12 region/theme rows (120/82/0/202). The helper is 9 lines.
- **F7, F8, F9, F10:**
  - The 560 px decision is recorded in the spec amendment.
  - The three region names per page are unique.
  - The eligibility SVG has genres, preferences, Ben/read and five arrows matching `complete.json` `eligible_pairs`.
  - The snippet red record states it was replayed against the bcf9126 prefix and disclaims initial authorship.
- **Native runs at current bytes:** the bound receipts pass 52/52 BookRec and 34/34 Expense rows, with page hashes equal to the current chapters. That includes the 50 EUR variant block (45 + 800 + 1400 = 2245).
- **Copies are identical:** the six SVG docs copies and the two query snippets are byte-identical to their packaged sources.
- **Unchanged areas:** no model, corpus or runtime bytes are in the tracked diff.
- **Budgets:**

| Item | Actual | Limit |
|---|---|---|
| Runner additions | +61 | 100 |
| New tests | about 187 | 200 |
| Chapters | 164 / 210 lines | 220 |
| SVGs total | 14.6 KB | 100 KiB |

Not reviewed, as scoped: the wheel and full 137-case run (PA6), broad replay, merge, publication and certification. This was the final repair reading; I won't do a third.
