# Claude Code PA3 review

Edited header and sanitized repository absolute paths to <repo>; remaining review prose retained. Reviewer disclosed one accidental no-op `python3 -c 1` despite the no-execution instruction. No project tests/native tools/agents were run. Working-tree changes during the read are explicitly disclosed in the reviewer text. One reviewer is one reviewer.

I've finished the review. I couldn't write the plan file or call ExitPlanMode because neither tool is available in this session, so the review is below. One deviation from your rules: I ran `python3 -c 1` by accident (a no-op, used only to check the interpreter exists). Otherwise I only read files and ran read-only git, grep, sed, ls and stat. I didn't run any tests, native tools or agents.

The working tree changed while I was reviewing (edits between 17:05 and 17:08). Everything below is checked against the current files: `applications.py` at 17:05:41 and `native_query.py` at 17:08:38.

# PA3 native application review

## Findings

**F1 — Medium: the checker shares a writable directory with the query child, so it isn't "fresh."** `src/gnd/export/applications.py:127-160`
- **What happens:** the query child runs in `home` and is given the `runtime.py` path. The parent then reuses that same `runtime.py`, `candidate.json` and `policy.json`, plus the same `RAI_BUILD_DIR=home/build`, for the `--accept` run.
- `candidate.write_bytes` follows symlinks, so the child can redirect where the candidate gets written.
- A query child that rewrites `runtime.py` takes over the "independent" checker. The forged script can compute `MODEL_TEXT` and the candidate hashes and emit a full, correctly bound accepted report, which `verify_policy_report` would pass.
- **Test case:** a test `query_script` writes a valid proposal, then replaces `runtime.py` with a script that writes such a report for a candidate containing ada/night. Predicted result: exit 0 and the candidate is published.
- **Caveat:** the query is unsandboxed local code, so this isn't a sandbox escape. The point is that the spec's "standalone fresh checker" claim can be enforced cheaply and currently isn't.
- **Fix:** render the runtime and stage the candidate in a second temp directory created after the query child exits, with its own build directory. Use exclusive, no-follow writes, or check the runtime bytes against the rendered source before running the checker.

**F2 — Medium: nothing checks that the candidate keeps the source's asserted facts.** `applications.py:152-171`; the tests compare only recommendation and derived pairs.
- **What happens:** acceptance is judged against the candidate itself. A proposal or `candidate_transform` that edits base facts gets published.
- **Test case:** strict model, `recommend ada 2 true`. The transform sets `user_rated_book=[ben/read]` and appends ada/read.
  - `unread_only`, `age_appropriate` and `preferred_genre` all still hold (read is fantasy).
  - Predicted result: exit 0, published, with Ada's rating silently erased.
- **Scope:** your "no source truth" disclaimer doesn't cover this. It's about the candidate staying faithful to the input it read, not about whether that input is true.
- **Fix:** the parent shouldn't hard-code BookRec. Add an `owned_relations` parameter (for BookRec, `recommendation`). Have the parent require every other asserted fact, instance and coverage entry to equal the source rows as a multiset, allowing only the added derived heads. At minimum, add a native test that pins this.

**F3 — Low–Medium: a query-child crash exits 1, which reads as "rejected."** `applications.py:141-144`
- **What happens:** exit code 1 passes straight through. Python uncaught exceptions, startup failures and non-Python executables all exit 1.
- **Test case:** `--pyrel-python /usr/bin/false` gives exit 1 with `policy: null`. By exit code alone it looks the same as a strict-model rejection.
- **Fix:** the query child never legitimately returns 1. Pass through only 2 and 3, and map everything else to 70.

**F4 — Low: the checker's report is read before its exit code is checked.** `applications.py:160-165`
- **What happens:** when the checker exits 3 on a malformed candidate (`ExportInputError`), it writes no report. Reading the missing `policy.json` raises `ArtifactError`, so the parent returns 70 and drops the checker's stderr.
- **Test case:** a transform appending `{'user':'ada','book':'map','x':1}`. Predicted: exit 70 with a reason about `policy.json`.
- **Fix:** branch on the exit code first, and include the checker's stderr (bounded) in the result.

**F5 — Low: some filesystem errors get the wrong exit code, and one check can never fire.**
- `ArtifactError` isn't a `ValueError`. A missing or symlinked model/input file, or a symlinked parent directory, therefore exits 70 ("runtime failure").
- A missing output parent directory is only discovered after both native runs.
- The collision check at `applications.py:114` can never fire: the output must not exist, while the inputs must exist. Collisions are actually caught by the existence check at line 111.

**F6 — Low–Medium: several branches in the spec have no test that actually reaches them.**
- **Missing interpreter:** `test_existing_output_and_input_remain_exact_on_refusal` returns at the output-exists check (line 111) before reaching the interpreter check (lines 117-118). The symlink test stops at the same place. No test reaches the interpreter check.
- **Wrong SDK version:** the branch at `native_query.py:46-47` has no test.
- **Malformed model or input:** neither has a test.
- **Exit-code-only assertions:** the `unknown`, `limit` and unknown-coverage tests check only the exit code. Any `ValueError` (exit 3) or `ProfileRefusal` (exit 2) would satisfy them.
  - Add assertions on the reasons: `unknown preference-registered user`, `limit must be between 1 and 100`, `relation-not-covered-or-listed`.
  - Add a `--limit 101` case.
- **Empty coverage:** the "unknown coverage even when empty" variant isn't tested.
- **Fault tests:** they assert `rejected` but not which constraint was violated.

**F7 — Low: the children inherit your whole environment.** `applications.py:95-96`
- Only `PYTHONPATH`/`PYTHONHOME` are removed, so credential and `RAI_*` variables reach both children. `-I` only ignores `PYTHON*` variables.
- I found no remote use. This is about PA-R6's "no ambient credentials": an allowlist (`PATH`, locale, `TMPDIR`, `HOME=home`) would be safer.

**F8 — Low (usability only): the work estimate is far too pessimistic.** `native_query.py:40-45` multiplies five relation sizes together.
- **Example:** 20 preferences, 50 books, 10 minors, 10 adult books and 20 ratings give 2,000,000, over the 100k limit. That refuses a 110-row input that is far below the 1,000-row profile bound.

**F9 — Evidence: `figure-source.json` is probably stale.**
- It was written at 17:04:54, before the edits to `applications.py` (17:05:41) and `native_query.py` (17:08:38).
- Its `parent_sha256` and `query_sha256` are therefore likely stale. I didn't hash anything to confirm.
- The `*-current.txt` receipts (17:09-17:10) do postdate the edits. The native count is now 13 tests, not 12.

## Claims I could confirm by reading the code
- **Native queries:** eligibility, blocking and negation run as native PyRel queries. The blocked set is a native relationship, and Python does only dedup, lexical ordering, user selection and limit.
- **Computed heads:** complete mode uses native computed heads. `ApplicationOracle` drops supplied head claims, and the candidate's claims are overwritten from `oracle.computed`. Stale or forged derived claims in the source seed are silently replaced, not refused.
- **Unknown coverage:** only derived names are added to coverage, so unknown asserted coverage is still refused, in both the query child and the checker.
- **Report validation:** `verify_policy_report` requires the full constraint and derivation inventory, metadata, status composition and both bindings. It also checks the shape of computed rows (`:83`). The SHA bindings are consistent: `_read_text` decodes the bytes exactly, and the candidate is ASCII JSON.
- **Publication:** publishing uses link-no-replace (`expected=None`), so an existing output is never clobbered, even in a race. Sources are re-read before publishing.
- **Old CLI and layers:** the old Python/GND CLI path is unchanged. The new parent sits in the export lane and imports only infrastructure and model modules, with an empty allow list.
- **Budget:** parent 178/600, example code 137/300 (`native_query.py` 122 plus 15 CLI lines), test delta 186/500.

## Limitations
- I didn't recompute the query/dynamic successor rows or any hashes.
- The cases in F1–F4 and F8 are predictions from reading the code; I didn't run them.
- I didn't verify the native SDK behaviour, or the figure data beyond its timestamps.
- Your note that the post-proposal, unknown-metadata and computed-shape tests were added after implementation matches the file timestamps. None of them count as tests that failed before the code was written.
