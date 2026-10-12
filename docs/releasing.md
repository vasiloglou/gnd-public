# Release preparation and promotion

The manual `release.yml` workflow builds a release wheel and sdist once, then
builds a comparison wheel from that sdist. It retains SHA256SUMS, the source
revision and tool versions, and runs installed-candidate acceptance on those
exact files. Only `main` can prepare or publish. Preparation is the default;
PRs, tags and ordinary pushes never upload a package.

To enable the first PyPI release, sign in to
[PyPI account publishing](https://pypi.org/manage/account/publishing/) and add a
pending GitHub publisher with these exact fields:

- PyPI project: `get-nick-done`
- GitHub owner: `vasiloglou`
- Repository: `gnd-public`
- Workflow filename: `release.yml`
- Environment: `pypi`

Create the matching GitHub `pypi` environment and configure the repository owner
as a required reviewer, with deployment restricted to `main`. Once configured,
manually run the workflow on `main` with `publish=true`. Approve the environment
after inspecting the retained artifacts and successful acceptance results.
The publisher checks the source and hashes, then uploads only the retained
release wheel and sdist through OIDC; it never rebuilds or uploads the comparison
wheel. No stored PyPI API token is needed. After upload, the workflow compares
both served files with their local hashes and exercises a fresh PyPI install
against an invalid dispatch plan and its passing repair.

A workflow file alone does not establish a PyPI publisher identity. Account and
environment setup must be completed before dispatching publication. A failed
post-upload check does not undo the release; use the incident procedure below.

After Phase 3 accepts the prepared package, fill the release dossier with the
exact source commit, independent artifact hashes, observed profiles, selected
regression results and target-only contributor realpaths. Candidate sign-off
requires those results. Rebuilding makes a new candidate and repeats affected
validation; the comparison wheel never replaces the release wheel.

Before production enablement, confirm package ownership/version availability,
repository visibility/content/history review, target-only release authority,
trusted-publishing identity and protected environment. Recheck official service
documentation when configuring them. TestPyPI is omitted by delegated decision;
service correctness and production credentials are untested. Publication is selected only by the manual `publish` input. The publisher
consumes the retained release wheel and sdist after `sha256sum -c SHA256SUMS`;
it does not rebuild.
Missing/mismatched files stop promotion. The local preparation check covers
identity validation; production transport remains untested until the first upload.

After authorized publication, download served files and compare to the signed-off
identities, install them and run the documented examples. On mismatch or failure,
stop announcements, record affected files/version, notify through authorized
support channels, and choose a corrected new version or service-supported yank.
Never claim already distributed bytes were private or silently replace them.
Keep the incident and correction linked; source retirement is a separate action.

Official service references checked during preparation (2026-10-03):
[PyPI publisher setup](https://docs.pypi.org/trusted-publishers/adding-a-publisher/)
and [GitHub workflow artifacts](https://docs.github.com/en/actions/concepts/workflows-and-actions/workflow-artifacts).
These describe setup and storage, not a configured or validated production identity.
