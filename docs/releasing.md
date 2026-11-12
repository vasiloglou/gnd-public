# Release preparation and promotion

The manual `release.yml` workflow builds a release wheel and sdist once, then
builds a comparison wheel from that sdist. It retains SHA256SUMS, the source
revision and tool versions, and runs installed-candidate acceptance on those
exact files. Only `main` can prepare or publish. Preparation is the default;
PRs, tags and ordinary pushes never upload a package.

## Publication routes

A release is published by one of two routes. Choosing one is the owner's
decision; preparing a release configures and runs neither.

**Token upload of retained files.** The owner uploads the release wheel and
sdist that a preparation retained, after `sha256sum -c SHA256SUMS` passes,
with the owner's own PyPI credentials. The uploaded bytes are the bytes that
were validated. Every release through 0.3.0 (0.1.0, 0.2.0 and 0.3.0) was
published this way.

**The workflow with Trusted Publishing.** Sign in to
[PyPI account publishing](https://pypi.org/manage/account/publishing/) and add a
pending GitHub publisher with these exact fields:

- PyPI project: `get-nick-done`
- GitHub owner: `vasiloglou`
- Repository: `gnd-public`
- Workflow filename: `release.yml`
- Environment: `pypi`

Create the matching GitHub `pypi` environment and configure the repository owner
as a required reviewer, with deployment restricted to `main`. Then manually run
`release.yml` on `main` with `publish=true`, and approve the environment after
inspecting that run's retained artifacts and acceptance results. The publisher
checks the source and hashes, then uploads only that run's release wheel and
sdist through OIDC; it never rebuilds or uploads the comparison wheel. No stored
PyPI API token is needed. After upload, the workflow compares both served files
with their local hashes and exercises a fresh PyPI install against an invalid
dispatch plan and its passing repair. That run builds `main` as it is when dispatched, so
its files are a new candidate: its own acceptance run is their evidence, and
the release notes must cover everything on that `main`. A workflow file alone
does not establish a PyPI publisher identity; account and environment setup
must be completed before dispatching publication. A failed post-upload check
does not undo the release; use the incident procedure below.

Under either route, the release dossier records the exact source commit,
independent artifact hashes, observed profiles, selected regression results and
target-only contributor realpaths before publication. Candidate sign-off
requires those results. Rebuilding makes a new candidate and repeats affected
validation; the comparison wheel never replaces the release wheel.

Before publication by either route, confirm package ownership/version
availability immediately before the upload, repository visibility/content/history
review and target-only release authority; for the workflow route, also the
trusted-publishing identity and protected environment. Recheck official service
documentation when configuring them. TestPyPI is omitted by delegated decision;
service correctness and production credentials are untested. In the workflow,
publication is selected only by the manual `publish` input, and the publisher
consumes that run's retained release wheel and sdist after `sha256sum -c
SHA256SUMS`; it does not rebuild.
Missing/mismatched files stop promotion. The local preparation check covers
identity validation; production transport remains untested until the first upload.

After authorized publication, download served files and compare to the signed-off
identities, install them and run the documented examples. The workflow route does
this in its step "Compare served PyPI files and exercise a fresh index install";
after a token upload, run that step's commands by hand with `candidate/release`
holding the uploaded files. On mismatch or failure,
stop announcements, record affected files/version, notify through authorized
support channels, and choose a corrected new version or service-supported yank.
Never claim already distributed bytes were private or silently replace them.
Keep the incident and correction linked; source retirement is a separate action.

## After publication: move the pages

When the served files are confirmed, move the pages from the prepared state to
the published one with one command:

```sh
uv run python tools/release_text.py publish --date YYYY-MM-DD --built COMMIT --profile "OS, Python, uv"
```

`--built` is the first eight digits of the candidate's commit, and `--profile`
is the profile that release acceptance observed. The command moves the install
pins, the release link and wheel name, the tag sentence, the version paragraph
of the compatibility page, the opening and the heading of the release notes,
the support row and `RELEASED` in `tests/test_release_version.py`. It writes
nothing when it cannot make every edit.

It then lists the lines that still describe the earlier state, such as a page
that tells readers to install from a checkout. Those lines were written for
this release, so rewrite each one by hand. Run `uv run python tools/release_text.py check` until
it lists nothing. The default test lane runs the same check
(`tests/test_release_text.py`), so a page cannot return to the earlier wording
between releases.

Release acceptance keeps one negative control. It installs the release before
the candidate from PyPI and shows that each new probe fails there. A release
that adds probes replaces the previous control with one against the release
before it.

Official service references checked during preparation (2026-10-03):
[PyPI publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
and [GitHub workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts).
These describe setup and storage, not a configured or validated production identity.

## Tag-only versions

A version can be released as a GitHub tag alone, with no upload to the package
index; 0.3.1 was released this way. A tag-only version gets none of the
candidate, acceptance and dossier steps above, and the install pins keep naming
the latest version on PyPI. In one pull request:

1. Set the version in `pyproject.toml`, the editable entry of `uv.lock` and the
   three plugin manifests.
2. Add the version to `TAGGED` in `tests/test_release_version.py`. It must be
   above every version in `RELEASED`.
3. Rename the `Unreleased:` section of the release notes to
   `## X.Y.Z (tagged YYYY-MM-DD, not published on PyPI)`, and give in it the
   install command `uv tool install "git+https://github.com/vasiloglou/gnd-public@vX.Y.Z"`.
4. Add the tag sentence to the release notes opening and to the version
   paragraph of the compatibility page. `tools/release_text.py check` prints
   the exact paragraphs it expects.

After the owner merges the pull request, push an annotated tag `vX.Y.Z` on the
merge commit. A later index release that passes the tag-only version drops its
sentence from both paragraphs; `publish` refuses a version that is still in
`TAGGED`.
