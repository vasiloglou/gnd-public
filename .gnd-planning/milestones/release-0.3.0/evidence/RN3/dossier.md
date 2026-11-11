# Publication hand-over dossier: get-nick-done 0.3.0

Written 2026-11-11 by phase RN3 of milestone release-0.3.0. Nothing here has
been uploaded, tagged or published. Every command below is for the owner to
run; this session runs none of them. The procedure's home is
`docs/releasing.md`; this page cites it.

## A. Candidate identity

Built by phase RN2 ([record](../../004-phase-RN2.md)) from main commit
`4c07c0e6a623263048cb675d237046ebb239cb32` with uv 0.10.10. Retained outside
git at `~/gnd-release/0.3.0/4c07c0e6/candidate/` on the build Mac, with a copy
on beast-3 at `~/gnd-release/0.3.0/4c07c0e6/candidate-b1/`.

| File | Size | sha256 |
|---|---|---|
| `release/get_nick_done-0.3.0-py3-none-any.whl` | 2,948,039 | `143890eed5e30e19619cd5c1106bddae6283c672d5c63200018fb23157c6751b` |
| `release/get_nick_done-0.3.0.tar.gz` | 2,292,882 | `5e40d9e358ef49d335a4b0cf2c0919aff73a029076efa4f7c706b30109034c42` |
| `comparison/get_nick_done-0.3.0-py3-none-any.whl` | 2,948,039 | equal to the release wheel; never uploaded |

`SHA256SUMS`, `SOURCE_COMMIT` and `BUILD_PROFILE` are committed under
`evidence/RN2/candidate/`.

## B. Results

- A second build on beast-3 gave identical files.
- `tests/test_release_acceptance.py` over the retained files, beast-3, macOS
  27.0.1 arm64, Python 3.11.18, uv 0.10.10: 18 passed.
- `uvx --from <wheel> gnd --version` prints `gnd 0.3.0`.
- The default lane at the RN1 tree (`d78e576c`): 19,016 passed, 2 known
  errors. No file that lane selects has changed since.
- Main at `b913d43e` differs from `4c07c0e6` in planning files only.

## C. Not measured, and known at hand-over

- **One profile.** No Ubuntu, Windows or other Python version was observed
  for 0.3.0. The prepare job on GitHub (`publish=false`) would add Ubuntu; it
  runs only on the owner's request.
- **No index install** is possible before publication.
- **Trusted Publishing** has never been configured or validated.
- **The Ossie oracle lane was not rerun** after RN0 changed how the exporter
  reads the model (owner ruling, 2026-11-11). The evidence in its place:
  byte-identical exports and imports over the census before and after, and
  the installed-wheel probe.
- **Notes completeness** rests on one reviewer's read of the diff since
  `v0.2.0` and a check of every added command-line option.
- **Known and undecided, none blocking:**
  - an Ossie export writes constraint literals and descriptions for a fact
    type marked `redact`; the notes and the disclosure reference say so;
  - the Ossie import report's schema name and the `ossie-import` rule names
    are not in the format reference;
  - both query-policy budgets are full (365 of 365, 310 of 310);
  - the structure guards are in no phase's focused gate;
  - the fixtures-refactor issue (owner ruling RN-D7) is not filed.

## D. Owner actions

Observed 2026-11-11 unless stated.

1. **Package ownership and release authority.** Account-side; not readable
   by this session. 0.1.0 and 0.2.0 were uploaded by the owner with a token.
   1. **Repository review before the upload** (`docs/releasing.md`: "repository
      visibility/content/history review"). *Observed:* visibility `public`,
      default branch `main`. *Open:* a review of what the release points to,
      its content and history, is the owner's and is not recorded here. For
      0.2.0 the owner accepted this as a residual at the close.
   2. **Target-only contributor realpaths** (`docs/releasing.md` asks the
      dossier to record them). *Not recorded:* this dossier lists none, as
      the 0.2.0 dossier listed none. What exists: the acceptance file's
      `test_target_only_contributor_lifecycle` passed for both wheels in
      RN2's run.
2. **Breaking changes are in the notes** (`docs/compatibility.md`). Starting
   points in the 0.3.0 section, not a complete list: "GND 0.2.0 cannot read a
   version 5 model"; "GND 0.2.0 refuses these proposals and previews"; "GND
   0.2.0 cannot read a proposal that declares a source document"; "A preview
   that carries the new `population_check` field is refused by older GND
   readers"; "One rule is stricter"; the role names in three packaged
   examples.
3. **Check the files, then check that the version is free, immediately
   before the upload.** *Observed 15:08:14Z:* PyPI lists 0.1.0 and 0.2.0, and
   the 0.3.0 endpoint returns 404. This does not carry to the upload day.

   ```sh
   cd ~/gnd-release/0.3.0/4c07c0e6/candidate
   shasum -a 256 -c SHA256SUMS
   cat SOURCE_COMMIT
   curl -s -o /dev/null -w '%{http_code}\n' https://pypi.org/pypi/get-nick-done/0.3.0/json
   ```

   Expected: three `OK` lines, the commit `4c07c0e6a623263048cb675d237046ebb239cb32`,
   and `404`.
4. **Upload** (the ruled route: the owner's token upload of the retained
   files). Only the two files under `release/`; the tool asks for the token.

   ```sh
   uvx twine upload release/get_nick_done-0.3.0-py3-none-any.whl release/get_nick_done-0.3.0.tar.gz
   ```

5. **Tag** the candidate commit, annotated as `v0.2.0` is. *Observed:* remote
   tags `v0.1.0` and `v0.2.0` only.

   Run these in a checkout of the repository, not in the candidate
   directory, which is not a git repository:

   ```sh
   git -C <repository checkout> fetch origin
   git -C <repository checkout> tag -a v0.3.0 4c07c0e6a623263048cb675d237046ebb239cb32 -m "get-nick-done 0.3.0"
   git -C <repository checkout> push origin v0.3.0
   ```

6. **GitHub release** with the wheel, the sdist and a checksum file, as
   v0.2.0's. *Observed:* releases `v0.1.0` and `v0.2.0` only. A draft body is
   in [github-release-notes.md](github-release-notes.md).

   ```sh
   cd ~/gnd-release/0.3.0/4c07c0e6/candidate
   (cd release && shasum -a 256 get_nick_done-0.3.0-py3-none-any.whl get_nick_done-0.3.0.tar.gz) > SHA256SUMS.txt
   gh release create v0.3.0 --repo vasiloglou/gnd-public --title "GND v0.3.0" --notes-file <path to github-release-notes.md> release/get_nick_done-0.3.0-py3-none-any.whl release/get_nick_done-0.3.0.tar.gz SHA256SUMS.txt
   ```

7. **Apply the post-publication patches**, in a pull request, once the
   served files match (section E). This session can open that pull request
   on the owner's request.
   - [post-publication.patch](post-publication.patch): always. Replace
     `PUBLICATION_DATE` with the date in `docs/release-notes.md` and
     `docs/compatibility.md`; a test fails until you do.
   - [post-publication-tag.patch](post-publication-tag.patch): once action 5
     is done.
   - [post-publication-release-files.patch](post-publication-release-files.patch):
     once action 6 attached the files.
   - Then, from the repository root,
     `sh .gnd-planning/milestones/release-0.3.0/evidence/RN3/stale-text-check.sh token`
     must exit 0 and `tests/test_release_version.py` must pass. The check
     exits 1 until all three patches are in, because the page text they
     replace names the 0.2.0 tag and release. It also requires the notes'
     opening, the notes' heading and the compatibility page to give the same
     date.
   - The patches were made against main `b913d43e`. If `git apply --check`
     fails later, regenerate the conflicting hunk; the check shows what is
     left.
8. **Announcements.** None are prepared.

## E. After the upload

`docs/releasing.md`, "After authorized publication", is the procedure. The
comparison is the `release.yml` step "Compare served PyPI files and exercise
a fresh index install"; after a token upload its commands are run by hand
with `candidate/release` holding the uploaded files. This session can run
that read-only check on the owner's request.

Read the version endpoint or the simple index, not the JSON listing of all
versions: on the 0.2.0 publication day that listing lagged by minutes.

On any mismatch, follow the incident paragraph of `docs/releasing.md` and do
not apply the patches.
