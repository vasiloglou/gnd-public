# Phase RN3: publication hand-over

## 1. Status

**Owner-decided (2026-11-11): approved, D1 to D5 as recommended** ("Merge and
approve", answering "Merge PR 165 and approve the RN3 spec as recommended?").
The approved bytes are r1 at commit `6618e643`, sha256 `aa5cbbcf535d741da7b58d17575a5483852113b60c42c79478a72818d752dde7`.
Implementation follows; findings are appended below.

## 2. Provenance

Derives from [the plan](release-0.3.0-plan.md) r2 §4 (RN3-C1 to C4, and the
publication stage), its ruled decisions RN-D4 and RN-D5, the record of
[RN2](../004-phase-RN2.md), and the predecessor phase
[RR3](../../rule-check-release/004-phase-RR3.md), whose dossier, three patches
and stale-text check (`rule-check-release/evidence/RR3/`) this phase adapts.
Baseline: main `4c07c0e6`, the candidate commit. No review has run over these
bytes.

## 3. Obligations (step 0 harvest)

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| RN3-C1 | a dossier with the candidate identity, the results and what was not measured | plan §4 | M1 sections A to C |
| RN3-C2 | each owner action before publication, with the evidence that it is still open: ownership, availability recheck, route, tag, GitHub release with attachments, announcements | plan §4 | M1 section D |
| RN3-C3 | the post-publication patches (pins, `RELEASED`, the notes date, compatibility, the support row), prepared and not applied, with the stale-text check adapted | plan §4 | M2, M3, T1 to T5 |
| RN3-C4 | a stale-text inventory of `docs/releasing.md` with a disposition per hit; "no edit" only if empty or all historical | plan §4 (after review P7) | M4, T6 |
| RN-D5 | the milestone stays open through publication; publication is owner acts, each on its own request; route as for 0.1.0 and 0.2.0 | plan §10 | M1 sections D and E; §9 |
| Predecessor N19 | agent sessions were refused a tag push and a release creation; the owner did both | plan N19 | M1 section D prepares exact commands for the owner |
| RN2 boundary | one profile; the oracle lane not run; evidence is the candidate's, not a published file's | `004-phase-RN2.md` | M1 section C |
| RN0, RN1, RN2 open questions | redaction and Ossie export; the unfiled fixtures-refactor issue; undocumented Ossie literals; full query budgets; structure guards outside focused gates | their records | M1 section C lists them as known at hand-over; none blocks |
| `docs/releasing.md` | before publication: ownership, availability immediately before upload, repository review, release authority; after: compare served files, install, run examples | the page | M1 sections D and E cite it and do not restate it |
| `docs/compatibility.md` | breaking changes and migration in the notes; never overwrite released files | the page | M1 section D item on the notes |
| Predecessor refuted premise | the PyPI JSON version listing lagged on publication day | `rule-check-release/005-milestone-close.md` | M1 section E reads the version endpoint and the simple index |
| Plan rule 1 | no upload, tag, release, environment or publisher change by a phase | plan §0 | §9 |
| Lesson of RN0 to RN2 | run the planning-link test after the last planning file is written | their records | T7 |

## 4. The standing rules, bound to this phase

- Plan rule 1 (prepare, never publish): the patches are files under
  `evidence/RN3/`; T2 shows the tree is unchanged by them.
- Plan rule 3 (no instruction names an unpublished version): the patch that
  moves the pins exists only as a patch; `tests/test_release_version.py` on
  the unpatched tree still refuses a 0.3.0 pin (T5).
- Plan rule 4 (evidence belongs to exact bytes): the dossier names the
  candidate by commit and hashes and says the upload must be those files.
- `project.md` rule 5 (one home): the procedure's home is
  `docs/releasing.md`; the dossier cites its steps.
- Plan rules 5 to 8 and `project.md` rules 1 to 4, 6: no subject; this phase
  adds documents, patches and one shell check, and no consumer of input.

## 5. Goal

`evidence/RN3/` holds a dossier and three patches such that, on a scratch
copy of `4c07c0e6`, each patch applies with `git apply --check`, the patched
tree passes `tests/test_release_version.py` and the stale-text check exits 0,
and the unpatched repository is byte-identical to before.

## 6. Design

### Modules

**M1. `evidence/RN3/dossier.md` (about 160 lines).** Sections as the
predecessor's:

- **A. Candidate identity.** Commit `4c07c0e6`, the three files with sizes and
  sha256, tool versions, where the bytes are retained.
- **B. Results.** RN2's gates, by reference to its record.
- **C. Not measured.** One profile; no Ubuntu; no index install before
  publication; Trusted Publishing never configured; the Ossie oracle lane not
  rerun since RN0; notes completeness rests on one reviewer and an options
  audit; the open questions carried from RN0 to RN2.
- **D. Owner actions**, each with its evidence and the exact command where
  there is one:
  1. Ownership and release authority (account-side; not readable here).
  2. Availability, immediately before the upload (the version endpoint must
     return 404).
  3. Route (RN-D5: the owner's token upload of the retained files, after
     `shasum -a 256 -c SHA256SUMS`). The `twine upload` command line is given
     with the two file paths and no credential.
  4. Tag `v0.3.0` on `4c07c0e6`, and the `git push origin v0.3.0` command.
  5. GitHub release with the wheel, the sdist and `SHA256SUMS.txt`, as
     v0.2.0's, and the `gh release create` command.
  6. The post-publication pull request (M2).
  7. Announcements (not prepared here).
- **E. After the upload.** The served-file comparison and fresh index install,
  citing the workflow step of `docs/releasing.md`; the commands to run by
  hand under the token route.

**M2. Three patch files, not applied.** Scope from the inventory of §12.

| Patch | Applies when | Changes |
|---|---|---|
| `post-publication.patch` | 0.3.0 is on PyPI | install pins to 0.3.0 in `README.md`, `docs/index.md`, `docs/installation.md` (two) and `docs/marketplace-plugins.md`; the plugin page's "prepared and not published" sentence removed; `docs/compatibility.md` says 0.1.0, 0.2.0 and 0.3.0 are published, with the date; the notes' opening and heading carry the date and the "not in any published package" paragraph and "requires the development checkout" sentence go; `docs/support.md` replaces the "prepared" row with the observed profile of the `4c07c0e6` candidate; the two shared-expense pages stop calling the feature unreleased; `RELEASED` in `tests/test_release_version.py` gains `0.3.0` |
| `post-publication-tag.patch` | a `v0.3.0` tag exists | the two sentences that name the `v0.2.0` tag (`docs/installation.md`, `docs/marketplace-plugins.md`) |
| `post-publication-release-files.patch` | a GitHub release carries the files | the release link and the wheel file name in `docs/installation.md` |

The date is written as `PUBLICATION_DATE` in the patch; the existing test
refuses that placeholder once 0.3.0 is in `RELEASED`, so it cannot be merged
unreplaced.

**M3. `evidence/RN3/stale-text-check.sh` (about 80 lines).** The
predecessor's script with the pattern and allowlist for 0.3.0: exit 0 when
every hit of the search over `README.md` and `docs` is allowlisted and the
notes open with the published state; exit 1 on stale text or a left
placeholder; exit 2 on a usage or search error. One argument, `token`, the
ruled route.

**M4. `docs/releasing.md` inventory.** A grep of the page for version
numbers, "0.1.0", "next", "Phase", dates and "TestPyPI", each hit classified
in the phase record as current, historical or stale. The page is edited only
for a stale hit; the edit, if any, is listed for the owner in the record
because the page is normative.

### Normative order

None added. The order of owner actions is `docs/releasing.md`'s.

## 7. Decisions

| ID | Question | Readings and cost | Recommendation |
|---|---|---|---|
| D1 | The support row after publication | (a) one row for the observed 0.3.0 profile (macOS 27 arm64, Python 3.11, uv 0.10.10, candidate `4c07c0e6`), keeping the 0.2.0 row; (b) replace the 0.2.0 row | (a) **Ruled (o, 2026-11-11): as recommended** |
| D2 | The two shared-expense pages that say "unreleased" | (a) the patch rewords them to say the feature is in 0.3.0; (b) leave them, since a checkout still works | (a): after publication the sentence sends users to a checkout they no longer need **Ruled (o, 2026-11-11): as recommended** |
| D3 | `docs/explanation/ossie.md` says an import "restores those details when the sidecar is present" (RN1 open question) | (a) add one sentence now, in this phase, that omitted populations stay omitted: a docs edit on main after the candidate commit, which does not change the package's code but does change the sdist's docs if rebuilt; (b) put it in the post-publication patch; (c) leave it | (b): the candidate's bytes stay the accepted ones and the page is fixed with the other docs **Ruled (o, 2026-11-11): as recommended** |
| D4 | The undocumented Ossie literals (RN2 review G7) and the unfiled fixtures-refactor issue (RN-D7) | (a) the dossier lists both as known; filing issues is the owner's go-ahead at publication; (b) file both issues now | (a) **Ruled (o, 2026-11-11): as recommended** |
| D5 | A review over this spec before implementation? | the owner's call | none; the diff gets one reviewer **Ruled (o, 2026-11-11): as recommended** |

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `git apply --check` of each patch on a scratch copy of `4c07c0e6`; the main patch first, then the other two in either order | exit 0 |
| T2 | `git status --porcelain` in the repository after the phase's checks | only the files this phase adds under `.gnd-planning/` (and `docs/releasing.md` if M4 finds a stale hit) |
| T3 | scratch copy with all three patches and the placeholder replaced by a date: `uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py` | exit 0 |
| T4 | the same scratch copy: `sh stale-text-check.sh token` | exit 0 |
| T5 | controls, each expected to fail: the placeholder left in place (T3's file exits 1 on the placeholder test, T4 exits 1); the main patch without its `RELEASED` hunk (the pin test fails); the unpatched tree (T4 exits 2, "are the patches applied?"); one pin left at 0.2.0 after `RELEASED` moves (the pin test fails) | each fails as stated |
| T6 | the `docs/releasing.md` inventory | every hit has a class; the record lists them |
| T7 | `uv run pytest -q tests/test_development_scaffold.py tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py` on the repository after the last planning file is written | exit 0 |

Branches: T5's four controls are the cases that can fail T3 and T4. The
dossier's commands are text; nothing runs them in this phase, and the record
says so.

Verification selection: direct, T1 to T6; impact closure, T7; the full
default lane is not rerun, since the phase changes no file it selects unless
M4 edits `docs/releasing.md`, in which case the docs tests of T7 and the
strict docs build cover it.

## 9. Out of scope for this phase

Uploading, tagging, creating a release, configuring Trusted Publishing or the
`pypi` environment, announcements, applying any patch, filing issues,
rebuilding the candidate, the Ubuntu profile, any source change.

The publication stage that follows is not a phase. Under RN-D5 each step
runs only on the owner's request at that time: the owner uploads, tags and
creates the release; this session then runs the read-only served-file
comparison and the index install, and opens the pull request that applies
the patches.

## 10. Size

Estimate: a dossier of about 160 lines, three patches of about 260 lines
together, a check script of about 80 lines, a record. No source lines.

## 11. Approval instrument

This prose.

## 12. Inventory for the patches (observed at `4c07c0e6`, 2026-11-11)

`git grep -n -i -E '0\.2\.0|0\.3\.0|not published|prepared|development checkout|next release|not signed off|newer than|unreleased' -- README.md docs`,
outside `docs/release-notes.md` and `docs/development`, classified:

| Hit | Class | Patch |
|---|---|---|
| `README.md:51`, `docs/index.md:153`, `docs/installation.md:13` and `:25`, `docs/marketplace-plugins.md:14`: the `==0.2.0` pins | stale at publication | main |
| `docs/compatibility.md:4` to `:6` | stale at publication | main |
| `docs/marketplace-plugins.md:71` to `:74`: "That is the case now..." | stale at publication | main |
| `docs/support.md:13`: the "prepared 0.3.0" row | stale at publication | main (D1) |
| `docs/how-to/shared-expense-policies-commands.md:5`, `docs/tutorials/shared-expense-policies.md:56`: "unreleased feature", "unreleased example" | stale at publication | main (D2) |
| `docs/installation.md:114`, `docs/marketplace-plugins.md:53`: the `v0.2.0` tag | stale once a tag exists | tag |
| `docs/installation.md:118`: the 0.2.0 wheel file name | stale once a release carries files | release files |
| `docs/support.md:12`: the 0.2.0 profile row | historical | none |
| `docs/explanation/ossie.md:11`: Ossie `0.3.0.dev0` | the upstream format's version | none |
| the nine sentences that offer a checkout "for unreleased work on `main`": three tutorials, three how-to pages, `docs/pyrel-apps.md:40`, `docs/installation.md:67`, `docs/marketplace-plugins.md:10` | true at any time | none |
| `docs/bookrec/*`, `docs/runtimes/souffle.md:195`, `docs/marketplace-plugins.md:105` | the word "prepared" or "development checkout" in another sense | none |

In `docs/release-notes.md`: lines 4, 8, 10, 11 and 57 are stale at
publication (main patch).

## 13. Implementation findings (2026-11-11, appended)

1. **Base.** PR 165 merged as `b913d43e`. `git diff 4c07c0e6 b913d43e`
   outside `.gnd-planning/` is empty, so the patches, made against
   `b913d43e`, apply to the candidate commit's docs as well.
2. **M2.** Three patches under `evidence/RN3/`: the main one touches 11 files
   (29 insertions, 34 deletions with the other two). Differences from §6:
   - the tag patch changes one sentence, not two: `docs/installation.md`
     already says "the latest release tag" and names no version;
   - under D3 (b) the main patch also adds one sentence to
     `docs/explanation/ossie.md` saying that what an export omitted stays
     omitted;
   - the two shared-expense pages are reworded to "GND 0.3.0 and later"; the
     commands page copies its files out of the installed package, so no
     checkout is needed after publication.
3. **M3.** `stale-text-check.sh` takes the one argument `token`. Its
   allowlist is the 19 hits the search gives on the fully patched and dated
   scratch tree, each read and judged right after publication or historical.
   Unlike the predecessor's, it exits 2 when the README has no 0.3.0 pin
   (patches not applied), and exits 1 until all three patches are in.
4. **M1.** The dossier gives the owner's commands for checking the files and
   the version, the upload, the tag and the GitHub release, and a draft
   release body (`github-release-notes.md`) in the shape of v0.2.0's. No
   command was run. The v0.2.0 tag is annotated with the message
   "get-nick-done 0.2.0"; the dossier's tag command follows it.
5. **T1, T3, T4, T5** ([checks.txt](../evidence/RN3/checks.txt)), on a
   scratch clone of `b913d43e`:
   - both apply orders give the same 11-file diff;
   - all three patches with the date replaced: `41 passed`, check exit 0;
   - placeholder left: pytest exit 1, check exit 1;
   - `RELEASED` hunk dropped: pytest exit 1 (3 failed);
   - unpatched tree: check exit 2;
   - one pin left at 0.2.0: pytest exit 1, check exit 1;
   - main patch alone: pytest exit 0, check exit 1 (the 0.2.0 tag and
     release text is still there).
   The first run of these controls printed the exit status of `tail`, not of
   the check; the retained file is the rerun with the real exit codes.
6. **M4, `docs/releasing.md` inventory** (`grep -n -i -E` for version
   numbers, "next", "phase", dates, "TestPyPI", "private", "token"): seven
   hits.

   | Line | Text | Class |
   |---|---|---|
   | 14 | "Token upload of retained files." | current |
   | 17 | "This is how 0.1.0 was published." | historical and true; incomplete, since 0.2.0 went the same way. Not stale; left as is, and listed in the record for the owner |
   | 35 | "PyPI API token is needed" (the Trusted Publishing route needs none) | current |
   | 54 | "TestPyPI is omitted by delegated decision" | current |
   | 65 | "after a token upload, run that step's commands by hand" | current |
   | 69 | "Never claim already distributed bytes were private" | current |
   | 72 | "Official service references checked during preparation (2026-10-03)" | historical |

   No hit is stale, so the page is not edited.
