---
milestone: release-0.5.0
station: publication
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: publication
date: 2026-11-25
source_commit: 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
pages_commit: 6e980af9b9374a5cc84222a8fbc1b7f71a22d348
gates:
  - command: "act 1, read-only part: shasum -a 256 -c SHA256SUMS; SOURCE_COMMIT; PyPI version endpoint; git diff 85d076ba origin/main over the shipped paths"
    exit: 0
    output: "three OK lines; 404; no shipped file changed (17:52:04Z)"
  - command: "uvx twine check release/get_nick_done-0.5.0-py3-none-any.whl release/get_nick_done-0.5.0.tar.gz"
    exit: 0
    output: "PASSED, PASSED"
  - command: "uvx twine upload --non-interactive --disable-progress-bar release/get_nick_done-0.5.0-py3-none-any.whl release/get_nick_done-0.5.0.tar.gz"
    exit: 0
    output: "View at: https://pypi.org/project/get-nick-done/0.5.0/ (17:53:28Z)"
    note: "act 2, on the owner's words. The credential was the one in the owner's ~/.pypirc, read by twine; the session did not read, print or type it"
  - command: "compare the PyPI version endpoint and the downloaded wheel and sdist with the retained SHA-256 values"
    exit: 0
    output: "served file matches, twice (17:54:55Z)"
    note: "act 3. A first attempt at 17:53:37Z met a cached 404 and exited 1; the endpoint answered 200 at 17:54:43Z"
  - command: "uv pip install --no-cache --index-url https://pypi.org/simple get-nick-done==0.5.0 in a fresh environment; gnd --version; the packaged dispatch check; gnd export ossie"
    exit: 0
    output: "gnd 0.5.0; rejected the invalid plan and accepted its repair; five Ossie files"
    note: "act 3. Python 3.14.3, uv 0.10.10, macOS 26.6.2 arm64, the planning machine"
  - command: "git tag -a v0.5.0 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7; git push origin refs/tags/v0.5.0; compare the peeled remote ref"
    exit: 0
    output: "refs/tags/v0.5.0^{} is 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 (17:55:59Z)"
    note: "act 4, on the owner's word"
  - command: "gh release create v0.5.0 --verify-tag with three attachments; gh release download; cmp and shasum -c of the attachments"
    exit: 0
    output: "https://github.com/vasiloglou/gnd-public/releases/tag/v0.5.0, published 17:57:29Z; attachments verify"
    note: "act 5, on the owner's word; the body is the RW3 draft, which the owner had not read"
  - command: "uv run python tools/release_text.py publish --date 2026-11-25 --built 85d076ba --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10'"
    exit: 1
    output: "changed 8 files; seven lines left for a person, the ones the RW3 preview lists"
    note: "act 6. Exit 1 is the expected result before the supplemental patch"
  - command: "git apply the RW3 supplemental patch; uv run python tools/release_text.py check; split-phrase-search.py"
    exit: 0
    output: "no page describes the state before 0.5.0 was published; split-phrase search: 0 block(s)"
  - command: "uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "98 passed, 1 deselected in 8.07s"
  - command: "uv run --group docs zensical build --strict; uv run python tools/check_docs.py site"
    exit: 0
    output: "No issues found; 19539 local links/assets/anchors checked"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 118.72s (0:01:58)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, comes from an untracked skill mirror in this checkout; it passes in a clean clone"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (5d90831): 49 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "ruling: owner said 'merge' for the pages pull request while the six-shard default lane at 6e980af9 was still running"
    exit: "n/a -- ruling"
    output: "the lane is not a gate of this record; its result goes in the close record"
slow_cadence:
  command: "bash e1-shards.sh 6e980af9b9374a5cc84222a8fbc1b7f71a22d348 base (beast-3, six default-lane shards)"
  trigger: "started before this record was written; not finished"
  reason: "the owner chose to merge without waiting. The milestone close runs a full default lane and records this one's result with it"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/owner-statements.txt
    sha256: 5549dce1bddf818038bfbe41ce6ca4c81973545cf669cb23909063547a62ab78
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/act1-verification.txt
    sha256: 4e935c417e9071309833d4d752744c5f06f341d03da355b24b8247f47664e534
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/pypi-upload.txt
    sha256: 04a163cd4b5cfa6eb9f06902091de87715eb210c94d8db295be04a4dcf0008f5
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/pypi-served-first-attempt.txt
    sha256: 313cc17acc81cba22f1df7c5e2f4607c219c0313d61ae6c359861d14be4f9115
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/pypi-served.txt
    sha256: 18594b110aa3bd4ad16f2d3a21025ef6220c80c26fb4d03979a5dbdebccc494a
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/pypi-install.txt
    sha256: fd327c907696f27f1625196d9e33115f8b4ca6b578bf3571ac510140c4c8ec80
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/tag.txt
    sha256: 412188ccf1cc03bf48210c15175888bab056af4d177b3bcb281132eaf24545f7
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/github-release.txt
    sha256: a68d72daf02a92546c038d7718aaa620c9c797da57fc059d5f17140d77a54906
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/published-pages.txt
    sha256: d4ebe47dd7f91a90855ebbe7668397162d4666d739ae47090831950546f6229d
  - path: .gnd-planning/milestones/release-0.5.0/evidence/publication/post-publication-state.txt
    sha256: cea6e729cecba6103bd6092b00f7d6dfa8855c157bd8e8d0ed2697b050ebb1b2
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/dossier.md
    sha256: 392b1ca8d38ad5bab93de662ced06d2e67c3521f0603c7efb94c1d63ee1f56c4
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/post-publication-supplement.patch
    sha256: e9a7b4ded7207d412737d5da394053e995754687c82fd39ebe6948aceea920c2
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW3/github-release-notes.md
    sha256: e75450c9e0555894c98823415a5224aaaa6f0f0c110a9599fba19dc8b63046b6
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/candidate/SHA256SUMS
    sha256: fefaef011502c8b9e921fe84ba34538c1330dbda2817b4f08b334dfe82d12b64
  - path: docs/release-notes.md
    sha256: 032faa319e1db07f76a12a9f3f7ae98d25aa059ce9ee8964ce8f1a4f14f07d17
  - path: tests/test_release_version.py
    sha256: 1a01e2ad96a9d117cd9e3203779fff4b187bf36f56ad171b619cc0cf1389cd6a
---

# GND 0.5.0 publication

On 2026-11-25 the two accepted release files were uploaded to PyPI, the
files PyPI serves were compared with them and matched, `v0.5.0` was tagged on
the accepted source commit, and the GitHub release was created with the two
files and their checksums. Each act followed the owner's own words in the
release session, kept in
[owner-statements.txt](evidence/publication/owner-statements.txt).

| Act | The owner's words | Receipt |
|---|---|---|
| 1. The owner's checks and the recheck | "go on"; later "I also confirm get-nick-done is mine." | [The recheck](evidence/publication/act1-verification.txt) at 17:52:04Z: the retained files verify here and on beast-3, the version endpoint answered 404, and main had changed no shipped file. The owner stated ownership of the PyPI project. A review of the repository's content and history was not stated and is not recorded as done |
| 2. Upload | "you have a token to do the push" | [Twine exit 0](evidence/publication/pypi-upload.txt) at 17:53:28Z, after a second recheck at 17:53:25Z |
| 3. Served files and a fresh install | none separate; see below | [Both served files match](evidence/publication/pypi-served.txt) the retained SHA-256 values at 17:54:55Z. [A fresh install](evidence/publication/pypi-install.txt) from the index printed `gnd 0.5.0`, passed the packaged dispatch check and wrote the five Ossie files |
| 4. Tag | "yes" | [The peeled remote ref](evidence/publication/tag.txt) is `85d076ba384e67b1f992cfd6b9a596ca01b3d4e7`, at 17:55:59Z |
| 5. GitHub release | "yes" | [The release](evidence/publication/github-release.txt), published 17:57:29Z with the wheel, the sdist and `SHA256SUMS.txt`; the downloaded attachments verify |
| 6. Pages pull request | "yes", then "merge" | [The helper and the patch](evidence/publication/published-pages.txt): eight files by the helper, seven lines by the patch, `check` at exit 0. The diff has the SHA-256 the RW3 rehearsal recorded, `8a4a5e83…6e8a` |
| 7. Issue comments | not requested | none posted |

## The files

| File | SHA-256 | PyPI upload time |
|---|---|---|
| `get_nick_done-0.5.0-py3-none-any.whl` | `c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49` | 2026-11-25T17:53:25Z |
| `get_nick_done-0.5.0.tar.gz` | `9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0` | 2026-11-25T17:53:27Z |

They are the files of the [RW2 record](004-phase-RW2.md), built from
`85d076ba` and accepted on beast-3.

## What differed from the dossier

- **Act 3 ran without a separate request.** `docs/releasing.md` requires the
  served-file comparison and the install after an upload and before
  anything is announced; both only read from PyPI and write to scratch. The
  owner was told afterwards.
- **The first comparison failed.** Nine seconds after the upload the version
  endpoint still answered 404, a cached answer to the availability check
  made seconds before the upload. It answered 200 about a minute later and
  the comparison then passed.
  [The failed attempt](evidence/publication/pypi-served-first-attempt.txt) is
  kept.
- **The upload used `--non-interactive --disable-progress-bar`**, as the
  0.3.0 and 0.4.0 uploads did, so a missing credential would fail and not
  prompt. The dossier's command lacked the two options.
- **The fresh install ran on Python 3.14.3**, the interpreter uv chose on
  the planning machine, not on the acceptance profile.
- **The pages pull request was merged before the full default lane at its
  commit finished**, on the owner's word. The focused release tests, the
  docs build, the link check and the guards ran first.

## The remote state after publication

[post-publication-state.txt](evidence/publication/post-publication-state.txt),
18:01:56Z, against the [pre-publication snapshot](evidence/RW3/pre-publication-state.txt):
one new tag, `v0.5.0`, peeling to `85d076ba`; one new GitHub release, not a
draft and not a prerelease; PyPI lists 0.5.0 as the latest version with the
two files above, neither yanked. The environments (`github-pages` only) and
the `release.yml` runs (none) are unchanged. `main` was `5d908318`.

## Gate output (verbatim)

    2026-11-25T17:53:25+00:00 PyPI simple index has no 0.5.0 file; version endpoint HTTP 404; retained release digests verified; main has not changed a shipped file.
    Uploading distributions to https://upload.pypi.org/legacy/
    Uploading get_nick_done-0.5.0-py3-none-any.whl
    Uploading get_nick_done-0.5.0.tar.gz
    View at:
    https://pypi.org/project/get-nick-done/0.5.0/
    2026-11-25T17:53:28+00:00 Twine exit 0

    served file matches: get_nick_done-0.5.0-py3-none-any.whl c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49 uploaded 2026-11-25T17:53:25.974630Z yanked False
    served file matches: get_nick_done-0.5.0.tar.gz 9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0 uploaded 2026-11-25T17:53:27.418240Z yanked False

    gnd 0.5.0
    Fresh PyPI install rejected the invalid plan and accepted its repair.

    5d99a45a48ea7a5561c9251241e4c59941f00b88	refs/tags/v0.5.0
    85d076ba384e67b1f992cfd6b9a596ca01b3d4e7	refs/tags/v0.5.0^{}

    no page describes the state before 0.5.0 was published
    98 passed, 1 deselected in 8.07s

## Open questions

- **The repository content and history review (RC-07)** was not stated by
  the owner. It stays the owner's, as in the 0.4.0 close.
- **The token-route sentence of `docs/releasing.md`** names releases through
  0.4.0. 0.5.0 was published the same way. The plan said the sentence moves
  in this pull request only if the helper moves it, and it does not. Target:
  the next edit of the procedure, or the close.
- **Issue comments** (RW3 spec D5): the owner's choice; none posted.
- **The GitHub release body** is the RW3 draft. The owner may edit it on the
  release page.
- **The owner's `~/.pypirc` is readable by other users of the machine.** The
  session reported it and did not change it.
- **The full default lane at `6e980af9`** was running when this record was
  written. The close records its result.

## Boundary -- what this result did NOT establish

- That 0.5.0 installs or runs on any platform but the ones observed: the
  acceptance profile of RW2 and one fresh install on the planning machine.
- That the published pages build and deploy on the documentation site. The
  strict build and the link check ran locally.
- That the default lane is unchanged by the pages pull request. Its run had
  not finished.
- Anything about a RelationalAI engine, or the residuals the dossier lists
  under "what was not measured".
- That every reader of the release pages was told. No announcement and no
  issue comment was made.
