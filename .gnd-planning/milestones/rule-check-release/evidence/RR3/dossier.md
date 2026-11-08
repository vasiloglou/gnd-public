# get-nick-done 0.2.0: publication hand-over dossier

Prepared 2026-11-08 by milestone `rule-check-release`, phase RR3, for issue
118. **This dossier publishes nothing and chooses nothing.** Every action in
section D is the owner's, and each needs its own request. The procedure's one
home is [`docs/releasing.md`](../../../../../docs/releasing.md); this dossier
cites it and does not restate it.

## A. Candidate identity

| Item | Value |
|---|---|
| Source | main `7c0f4d0e320ff7976296d785077280d180ea688e`, the merge commit of PR 125; parents `df5753bf` and `86e5e1f1` |
| Release wheel | `get_nick_done-0.2.0-py3-none-any.whl`, sha256 `e323c19e303f3b7fe9cbe7528e68021d271589ce0b91fd54bd76b2b919a069e4`, 2,857,045 bytes |
| Release sdist | `get_nick_done-0.2.0.tar.gz`, sha256 `f85818ead9cb651ae397ecd3ab50f87fdf5f9f7c7bada58a659cea2cb99e5104`, 2,220,814 bytes |
| Comparison wheel | built from the sdist; identical to the release wheel (same sha256) |
| Identity files | [`SHA256SUMS`, `SOURCE_COMMIT`, `BUILD_PROFILE`](../RR2/candidate/) |
| Build tools | uv 0.10.10 on both builds (the workflow's pin); the `uv_build` backend from `pyproject.toml` |
| Retained copies (outside git) | this Mac: `~/gnd-release/0.2.0/7c0f4d0e/candidate/`; beast-3: `~/gnd-release/0.2.0/7c0f4d0e/candidate-b1/`. Before any upload, run `shasum -a 256 -c SHA256SUMS` in the copy you use |

## B. Results

All from the RR2 record, [`003-phase-RR2.md`](../../003-phase-RR2.md), and its
evidence:

- **Reproducible:** two builds on two hosts (this Mac, macOS 26.6.2; beast-3,
  macOS 27.0.1) gave identical `SHA256SUMS`.
- **Release acceptance passes** over the retained files:
  `tests/test_release_acceptance.py`, 14 passed, exit 0, on beast-3 (macOS
  27.0.1 arm64, Python 3.11.18, uv 0.10.10). This includes:
  - every issue-118 item exercised from the installed wheel (`--rule-ids`,
    `--baseline`, `--allow-vacuous`, `remedy`, the acyclic extent,
    `source: tool-output` with `producer`), each with a behavior control;
  - the PyPI 0.1.0 wheel, on which each item is absent and the plain check
    is unchanged.
- **The index-style local form works:** `uvx --from <wheel> gnd --version`
  printed `gnd 0.2.0`.
- **The notes cover the candidate:** at the candidate commit,
  `docs/release-notes.md` has no `## Unreleased` heading. FU4 (PR 129)
  merged after the candidate commit and changed nothing under `src/` or
  `docs/`.

## C. Not measured

- **Profiles:** Ubuntu, Windows, any Python other than 3.11 on macOS 27, and
  any other machine.
- **The index install** (`get-nick-done==0.2.0` from PyPI): it cannot exist
  before an upload.
- **Trusted Publishing:** the PyPI pending publisher, the `pypi` environment,
  OIDC transport. TestPyPI is not used either.
- **An external user trial.**
- **The served-file comparison:** it exists only after an upload.
- **The 0.1.0 control depends on PyPI:** it downloads 0.1.0 from
  `files.pythonhosted.org` on every prepare run. If 0.1.0 were ever removed,
  that test would fail with its hash or lookup message.

## D. Owner actions

Each line gives the evidence, observed **2026-11-08T06:10Z** unless stated,
that the action is still open.

1. **Package ownership.** Confirm that the account that uploaded 0.1.0 owns
   `get-nick-done`. *Open:* not readable by this session. 0.1.0 was uploaded
   by the owner with a token (public-launch close, lines 81-83).
   1. **Repository review (O8).** Confirm what a release points to: visibility,
      content and history. *Observed:* visibility `public`, default branch
      `main`.
   2. **Release authority (O8).** Confirm that only the owner can publish
      `get-nick-done`. *Open:* not established by 0.1.0's token upload, as the
      public-launch close says, and not auditable here.
   3. **Breaking changes and migration (O15).** Confirm that the 0.2.0 notes
      record every breaking change with its migration. *Starting points, not
      a complete list:*
      - the notes' own refusal and behavior-change entries: "Refusals" in the
        rule-check block;
      - "Migration for `gnd-why-not/1` consumers";
      - `gnd import mined-rules` "refuses a population whose bytes are not
        the run" and "no longer exits 5";
      - "no longer raises on a structured aggregate rule".
   4. **Never overwrite released files (O15).** 0.1.0's files stay as they
      are. A wrong 0.2.0 upload is corrected by a new version or a yank (the
      incident paragraph of `docs/releasing.md`).
2. **Version availability, immediately before the upload.** *Observed:* PyPI
   lists `['0.1.0']`, so 0.2.0 is free. This observation does not carry to
   the upload day.
3. **The route** (RL-D5; the two routes are stated in `docs/releasing.md`,
   "Publication routes"):
   - **(a) Token upload of the retained files** in section A. RR2's evidence
     is about exactly these bytes, and the notes match them. Run `shasum -c`
     first.
   - **(b) `release.yml` with `publish=true`.** *Open preconditions:* a PyPI
     pending publisher (account side, not auditable here) and a protected
     `pypi` environment with the owner as required reviewer. *Observed:*
     environments `["github-pages"]` only, and 0 runs of `release.yml`.
     - The workflow builds `main` as it is when dispatched. Main is already
       past `7c0f4d0e` (FU4, the RR2 and RR3 records), so this is a new build
       with its own source commit and its own acceptance run.
     - Whether its bytes equal section A's is known only by comparing
       hashes. The changes since `7c0f4d0e` are tests and planning files.
     - The notes must cover everything on that `main`; check for any
       `## Unreleased` heading first.
4. **Tag.** `v0.2.0` at the published commit: `7c0f4d0e` under (a), the
   dispatched commit under (b). *Observed:* remote tags `refs/tags/v0.1.0`
   only.
5. **GitHub release.** Create one for `v0.2.0`, and decide whether it carries
   the wheel, sdist and `SHA256SUMS`, as v0.1.0's did. *Observed:* releases
   `v0.1.0` only.
6. **Apply the post-publication patches**, in a PR, once the served files
   match:
   - [`post-publication.patch`](post-publication.patch): always. Replace
     `PUBLICATION_DATE` with the date in `docs/release-notes.md` and
     `docs/compatibility.md`; a test in the patch fails until you do.
   - [`post-publication-tag.patch`](post-publication-tag.patch): if action 4
     happened.
   - [`post-publication-release-files.patch`](post-publication-release-files.patch):
     if action 5 attached the files.
   - Under route (b), drop the patch's new `docs/support.md` row, or reword
     it for the build that was published.
   - Then [`stale-text-check.sh`](stale-text-check.sh) must exit 0 and
     `tests/test_release_version.py` must pass.
   - The patches were made against RR3's commit. If `git apply --check`
     fails later, regenerate the conflicting hunk; the stale-text check
     shows what is left.
7. **Issue 118.** Comment with the published version and the served-file
   result, then close it. *Observed:* open.
8. **Announcements.** None are prepared; they are a separate decision.

## E. After the upload

`docs/releasing.md`'s "After authorized publication" paragraph is the
procedure. The comparison itself is the `release.yml` step "Compare served
PyPI files and exercise a fresh index install".

- Under route (b) the workflow runs that step.
- Under route (a), run the step's commands by hand, with `candidate/release`
  holding the files you uploaded.

On any mismatch, follow the incident paragraph of `docs/releasing.md`, and do
not apply the patches.
