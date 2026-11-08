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
were validated. This is how 0.1.0 was published.

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

Official service references checked during preparation (2026-10-03):
[PyPI publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
and [GitHub workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts).
These describe setup and storage, not a configured or validated production identity.
