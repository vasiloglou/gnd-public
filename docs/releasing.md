# Release preparation and promotion

The manual release workflow builds a release wheel and sdist once, then builds
a comparison wheel from that sdist in a separate directory. It stores SHA256SUMS
for all three and records the source revision/tool versions. No PR/tag event
publishes, and this workflow has no publisher job, OIDC permission or upload to
an index. Its CI artifact upload only retains preparation files in this repository.

After Phase 3 accepts the prepared package, fill the release dossier with the
exact source commit, independent artifact hashes, observed profiles, selected
regression results and target-only contributor realpaths. Candidate sign-off
requires those results. Rebuilding makes a new candidate and repeats affected
validation; the comparison wheel never replaces the release wheel.

Before production enablement, confirm package ownership/version availability,
repository visibility/content/history review, target-only release authority,
trusted-publishing identity and protected environment. Recheck official service
documentation when configuring them. TestPyPI is omitted by delegated decision;
service correctness and production credentials are untested. No publication is
selected by this preparation. A future approved publisher consumes the retained
release wheel and sdist after `sha256sum -c SHA256SUMS`; it must not rebuild.
Missing/mismatched files stop promotion. The local preparation check covers
identity validation; the future service transport remains unimplemented.

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
