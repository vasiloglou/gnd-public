The owner can publish exactly the accepted bytes with this dossier, and the scratch patch holds up. I'm still requesting changes: a few snippets can't be run as written, and the retained scratch evidence leaves out records the spec asks for. None of the steps is unsafe.

**Hashes:** all ten files match the brief. `diff.patch` is the empty file (`e3b0…b855`), because everything new is untracked; I read all seven new files in full.

**Side effect:** one probe ran `uv run --no-sync`, and uv created an empty `.venv/` in the review checkout. It is gitignored and `git status` is unchanged. I did not remove it, since this was a read-only review. It is safe to delete.

## Findings

**F1 (medium): the scratch evidence leaves out what RV3-C3 requires.**
- `scratch-verification.txt:1-7` has no commands, exit codes, rehearsal date or tree identity. It also has no `git apply --check` result.
- `tool-only-preview.txt:1-5` has no exit status, though the spec says "Capture its exit".
- Neither file records the required check that the "install from a checkout" guidance is gone from the receipts page and the two BookRec pages, or its negative control.
- The dossier says the helper "exits 1" (`dossier.md:96`), but no retained file shows it.
- "85 passed, 1 deselected" doesn't say which test files ran, and "Build started" doesn't show the build was strict.
- **Consequence:** an auditor can't confirm the C3 gates from the retained files. I reproduced the result independently (see below), so what's missing is the record, not the work.

**F2 (low, fails safe): the snippets aren't runnable as written.**
- `dossier.md:75` uses `$release_notes_file`, and `dossier.md:90-92` use `$publication_date` and `$supplemental_patch`. None of them is ever set.
- Step 4 says to run "in the retained directory", but `github-release-notes.md` isn't there.
- **Consequence:** pasted verbatim, `--date ""` makes the helper exit 2, and `gh` and `git apply` get empty paths. Each fails, so nothing is published by accident, but the steps don't reproduce.
- In step 6 the helper is expected to exit 1 before `git apply`, so a `set -e` paste stops at the first line.

**F3 (low): the release body links to a page that says "not published".**
- `github-release-notes.md:10` links to `blob/v0.4.0/docs/release-notes.md`. The tag points at `648cc6e0`, where that page heads `## 0.4.0 (prepared, not published)` and says "Version 0.4.0 is prepared for PyPI".
- **Consequence:** a reader of the public GitHub release sees a contradiction.
- v0.3.0 had the same issue (I checked `v0.3.0:docs/release-notes.md`), so this is precedent, but it should be a deliberate choice.

**F4 (low): step 6 doesn't give the checks the scratch ran.**
- `dossier.md:86-94` says "Verify … before merge" but omits the four release test files, the strict Zensical build and `tools/check_docs.py site`.
- **Consequence:** the docs update can only be fully reproduced by reading the spec.

**F5 (low): two owner actions have no receipt or verification.**
- The plan (§11) requires dated authorization and execution receipts for each act, and RV-D10 requires checking the attachment identities.
- Steps 3 (tag) and 4 (GitHub release) at `dossier.md:59-76` name no receipt, and step 4 has no command to check the hashes of the uploaded attachments.

**F6 (style): the snapshot has unlabeled lines.**
- In `pre-publication-state.txt`, lines 11 and 12 (`["github-pages"]`, `[]`) say nothing about what they are. The dossier reads line 12 as zero `release.yml` runs.
- Line 16 ("Workflow diff across preparation source refs:") has empty output and names no refs.
- The file doesn't say which Mac rehashed the bundle.

**F7 (style): the first build's profile isn't in the dossier.**
- The dossier never names it (macOS 26.6.2, CPython 3.11.15, uv 0.10.10). That profile is what the retained `BUILD_PROFILE` file records, and RV3-C1 asks for both source and build profiles. It is only reachable through the RV2 link.

## What I checked and found true

**C1 (identity matches RV2):**
- The three dossier hashes and byte sizes match `RV2/candidate/SHA256SUMS` and the RV2 record.
- The source commit `648cc6e0…` matches `SOURCE_COMMIT`.
- All ten evidence hashes in the RV2 frontmatter verify OK.
- The `--profile` string matches RV2-C6.
- The six freeze shards add up to 19,699 passed (13 skipped), the uv 0.13.7 claim matches `freeze-summary.txt`, and the snapshot rehash lines are all OK.
- No product, workflow, test, docs or lock change between `648cc6e0` and HEAD.

**Contributor realpaths:** the 36 symlinks listed (18 each under `.claude/skills` and `.codex/skills`) are exactly the tracked symlinks at `648cc6e0`, and all point to `../../src/gnd/skills/*`.

**C2 (patch fixes the stale wording, no publication action):**
- I ran the helper, then the supplement, then `problems()` entirely in memory, with nothing written to disk.
  - The helper changed the same 8 files as the preview, and its 4 stale lines match `tool-only-preview.txt` exactly.
  - After the supplement, `check` reports 0 problems.
  - None of the receipts, two BookRec or plugin pages still carries the prepared-state install wording.
- The receipts warning is a real miss by the tool: "not in a published package" doesn't match its `STALE` pattern, and 0.3.1 isn't in `RELEASED`.
- `git apply --check` (read-only) passes for the three unchanged pages. The marketplace preimage blob `34cbd95d` equals the helper's output, so that hunk depends on running the helper first, which is how the dossier orders it.
- Link anchors in the new text exist (`installation.md`, `synthetic-data.md#generate-examples-for-guarded-rules`).
- No publication action is in the diff. Main still sits at `648cc6e0` in the snapshot.

**Safety of the steps:**
- Upload names only the two `release/` files; the comparison wheel is never uploaded.
- The tag uses the full accepted commit.
- `git ls-remote --tags origin 'refs/tags/v0.3.0^{}'` does return the peeled commit, so the step 3 check works.
- `--verify-tag` and the repository name match `releasing.md` and the 0.3.0 precedent.

## What I could not check

- **Live state:** PyPI, GitHub releases, environments, runs and the retained directories on either Mac (no network access to them; read-only brief).
- **Scratch rehearsal:** the actual test run, strict docs build and link check (not reproduced, to avoid writing; only their outputs as recorded).
- **Owner-only checks:** account ownership and the content/history review.

VERDICT: CHANGES_REQUESTED
