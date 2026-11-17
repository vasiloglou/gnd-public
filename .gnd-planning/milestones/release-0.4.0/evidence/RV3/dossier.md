# GND 0.4.0 publication hand-over

The [RV2 record](../../008-phase-RV2.md) binds the accepted candidate to
main commit `648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`.
The retained directory on the build Mac and beast-3 is
`~/gnd-release/0.4.0/648cc6e0/candidate/`.

| File | Bytes | SHA-256 |
|---|---:|---|
| `release/get_nick_done-0.4.0-py3-none-any.whl` | 3,421,324 | `36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c` |
| `release/get_nick_done-0.4.0.tar.gz` | 2,551,056 | `2c171ccccc891333a580c3fe01c4b79ac5d3e5098af20827977a6ce455a229b6` |
| `comparison/get_nick_done-0.4.0-py3-none-any.whl` | 3,421,324 | `36288e7a918b17d14ea307b6492acfbad741755e1e83818641836452cee9ea5c` |

Both builds matched. The first build used macOS 26.6.2 arm64, Python
3.11.15 and uv 0.10.10. The independent build and installed acceptance passed 23 cases on beast-3 with
macOS 27.0.1 arm64, Python 3.11.18 and uv 0.10.10. The default lane at the
frozen commit had 19,699 passes, 13 skips and the two baseline optional-wheel
setup errors under uv 0.13.7. `uvx` printed `gnd 0.4.0`. The
[contributor realpaths](contributor-realpaths.txt) bind 36 tracked links to
the target scratch checkout. Installed contributor lifecycle coverage comes
from the wheel acceptance suite.

The [hand-over snapshot](pre-publication-state.txt) records public visibility,
main, the three existing releases, all tag targets and the absence of the
0.4.0 version at the index. The 0.4.0 endpoint returned 404. The existing
environment is `github-pages` and the release workflow has zero runs in this
snapshot. Recheck immediately before upload. Account ownership and release
authority, including the owner's repository content and history review,
remain owner checks.

The observed installed profile is limited to the recorded macOS profile.
Ubuntu and Windows, GitHub Prepare, Trusted Publishing, TestPyPI and the
default-excluded lanes were outside the run. Count certificates from PR 204
were outside this freeze. Served files and a fresh index install are
post-publication evidence.

## Owner actions

Use the [release procedure](../../../../../docs/releasing.md). Each action
requires the owner's explicit authorization under RV-D5.

1. Confirm account ownership and release authority. Rehash the retained
   files, check `SOURCE_COMMIT`, and require HTTP 404 for the version endpoint
   alongside an index recheck.

   ```sh
   cd ~/gnd-release/0.4.0/648cc6e0/candidate
   shasum -a 256 -c SHA256SUMS
   test "$(cat SOURCE_COMMIT)" = 648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a
   cat SOURCE_COMMIT
   curl -sS -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/get-nick-done/0.4.0/json
   ```

2. Upload the wheel and sdist in `release/` with the owner's PyPI token.
   Retain the dated authorization and upload receipt.

   ```sh
   uvx twine upload release/get_nick_done-0.4.0-py3-none-any.whl release/get_nick_done-0.4.0.tar.gz
   ```

3. From a repository checkout, tag the exact accepted source. Verify that the
   remote annotated tag peels to the same full commit. Keep the dated owner
   authorization and the peeled remote ref as the tag receipt.

   ```sh
   (
   set -e
   git fetch origin main
   git tag -a v0.4.0 648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a -m 'get-nick-done 0.4.0'
   git push origin refs/tags/v0.4.0
   peeled=$(git ls-remote --tags origin 'refs/tags/v0.4.0^{}' | awk '{print $1}')
   test "$peeled" = 648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a
   printf '%s\n' "$peeled"
   )
   ```

4. Create the GitHub release with the two accepted files and their checksums
   under RV-D10. Start in a checkout containing this dossier so the
   [release body](github-release-notes.md) is available. Keep the dated
   authorization, release URL, and downloaded attachment checks as receipts.

   ```sh
   (
   set -e
   repo=$(git rev-parse --show-toplevel)
   release_notes_file="$repo/.gnd-planning/milestones/release-0.4.0/evidence/RV3/github-release-notes.md"
   test -r "$release_notes_file"
   cd ~/gnd-release/0.4.0/648cc6e0/candidate
   (cd release && shasum -a 256 get_nick_done-0.4.0-py3-none-any.whl get_nick_done-0.4.0.tar.gz) > SHA256SUMS.txt
   gh release create v0.4.0 --verify-tag --repo vasiloglou/gnd-public --title 'GND v0.4.0' --notes-file "$release_notes_file" release/get_nick_done-0.4.0-py3-none-any.whl release/get_nick_done-0.4.0.tar.gz SHA256SUMS.txt
   attachments=$(mktemp -d)
   gh release download v0.4.0 --repo vasiloglou/gnd-public --dir "$attachments"
   cmp SHA256SUMS.txt "$attachments/SHA256SUMS.txt"
   (cd "$attachments" && shasum -a 256 -c SHA256SUMS.txt)
   )
   ```

5. Compare both served PyPI files with the retained digests. Verify the
   release attachments and lightly test a fresh public-index install
   following the release procedure. Retain dates, the served comparison and
   the install results in a numbered publication record.
6. After the served files match, prepare a separate docs PR. Supply the
   actual publication date from the PyPI upload receipt to the existing helper.
   In the docs PR checkout, which must contain the hand-over evidence, apply the
   [supplemental patch](post-publication-supplement.patch). The supplement
   updates the marketplace instructions, both BookRec pages and the
   receipts page. Verify all four pages as well as the generated notes,
   compatibility, support, and installation text before merge.

   ```sh
   (
   set -e
   cd "$(git rev-parse --show-toplevel)"
   supplemental_patch="$PWD/.gnd-planning/milestones/release-0.4.0/evidence/RV3/post-publication-supplement.patch"
   test -r "$supplemental_patch"
   printf 'Publication date from the upload receipt (YYYY-MM-DD): '
   IFS= read -r publication_date
   publish_exit=0
   uv run python tools/release_text.py publish --date "$publication_date" --built 648cc6e0 --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10' || publish_exit=$?
   test "$publish_exit" = 1
   git apply --check "$supplemental_patch"
   git apply "$supplemental_patch"
   uv run python tools/release_text.py check
   uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short
   uv run --group docs zensical build --strict
   uv run python tools/check_docs.py site
   )
   ```

   The first helper invocation exits 1 for the residuals in the
   [tool-only preview](tool-only-preview.txt). The receipts warning also
   needs the supplement. Reconcile any changed context against the actual
   main tree before applying. Keep the rehearsal date separate from the
   production receipt. Keep the actual source, date and focused test output
   with the separate docs PR and its dated authorization.
