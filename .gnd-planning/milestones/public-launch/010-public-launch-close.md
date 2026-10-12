---
milestone: gnd-public-launch
station: milestone-close
skill: "n/a -- owner-directed repository launch close"
scope: gnd-public-launch-close
date: 2026-10-12
status: closed
owner: vasiloglou
evidence:
  - path: evidence/launch-close/publication.json
    sha256: 78a315b13598736f93659fb910d9d9bb134fe7ad355c6816f6df71f80ad99569
---
# GND public launch — closed

The owner accepted the completed launch and requested closure on 2026-10-12:
“ok then it is time to close the milestone we are done”. This closes the selected
publication scope deferred by [009](009-milestone-close.md). The migration close
and separately scoped refactoring/transition work retain their original status.

## Published result

- Public repository: [vasiloglou/gnd-public](https://github.com/vasiloglou/gnd-public).
  Anonymous GitHub API access was verified after the visibility change.
- Package: [get-nick-done 0.1.0](https://pypi.org/project/get-nick-done/0.1.0/).
- [GitHub release](https://github.com/vasiloglou/gnd-public/releases/tag/v0.1.0)
  and tag: `v0.1.0`, source `75eda93f314e7ef82578ab4ee212d5e6d964fd71`.
- Apache-2.0, with LICENSE, NOTICE and third-party attribution retained.
- Wheel SHA256: `cc91decaf86d081fa023179792646900ac8f23c3cd1758e339006a4dab1ac183`.
- Sdist SHA256: `f47abb4505969ab69a9a7cdf5da9e071ff511b1b50f1b728154699f55c3a8f86`.
- [PR 13](https://github.com/vasiloglou/gnd-public/pull/13): Claude Code and Codex
  marketplace plugins, all 16 canonical skills, and PyPI/agent installation docs.
  Plugins postdate the Python release and install from `main`, not `v0.1.0`.
- [PR 12](https://github.com/vasiloglou/gnd-public/pull/12): opt-in publishing workflow.
- [PR 14](https://github.com/vasiloglou/gnd-public/pull/14): CODEOWNERS and contribution policy.
  PRs 8, 11, 12, 13 and 14 are merged.

## Evidence and validation

The [publication receipt](evidence/launch-close/publication.json) records live
visibility, tag, release assets, current PyPI metadata digests, merged PRs and
repository protections. [Build/tutorial results](evidence/launch-close/results.json)
and [served-file verification](evidence/launch-close/pypi-verification.json)
retain the separate artifact claims.

Both the release and sdist-derived wheel origins passed all 155 executable
tutorial blocks. Identity and changed/missing/extra controls passed four tests.
Served PyPI files were downloaded and matched byte for byte. A fresh index install
passed CLI startup, rejected the invalid dispatch plan and accepted its repair.
At close, current PyPI metadata hashes still match that retained result; no
rebuild or repeat upload occurred.

Claude strict plugin/catalog validation passed without warnings. An actual Codex
plugin install exposed all 16 skills plus LICENSE/NOTICE; its temporary install
was removed. Plugin/documentation/tutorial checks passed 81 tests; a separate
packaging-focused run passed 44 tests. Updated installation docs passed six
focused tests, strict site build, and 6,680 link/asset checks. Governance docs
passed seven focused checks. These results do not claim a new full-suite,
cross-platform, native-runtime or model-provider run.

## Sole-owner contribution control

`vasiloglou` is the only collaborator. Main requires PRs and conversation
resolution; protections apply to administrators. Force pushes and deletion are
blocked. Required approving reviews are zero because GitHub authors cannot
approve their own PRs: the owner's explicit merge action is acceptance. CODEOWNERS
names the owner for all files; required code-owner review is not enabled in this
sole-owner setup. Before adding another write-access account, enable one approving
review and required code-owner review. Agents still need explicit merge authority.

Collaborators-only interactions expire **2027-04-12 00:33 EDT**
(`2027-04-12T04:33:36Z`). Outside PRs, issues and comments are blocked; reading and
forking remain public. Renewal belongs to `vasiloglou`. No recurring automation
was requested or created.

## Scope dispositions and maintenance

| Item | Disposition |
|---|---|
| Reachable-history scan | Owner reported complete before visibility change; no independent new scan claim. |
| Local CI | Owner accepted local results; cloud runs were billing-blocked during the reviewed changes. No required cloud status check is configured at close. |
| Initial upload | Owner-authorized token publication; no credential values are recorded. |
| Trusted Publishing | Workflow shipped, but PyPI identity/environment configuration and production OIDC remain unvalidated. Owner can configure before selecting this route. |
| Exclusive target publishing authority, original P5-C3 | Not mechanically established by manual upload; no claim that old credentials/workflows were disabled. Carried to owner-selected release maintenance. |
| Announcements | No external messages selected or sent; separate owner trigger. |
| Hosted documentation | Owner selected GitHub-hosted docs as sufficient; no site deployed. |
| TestPyPI/user trial/timing/adoption | Omitted or unmeasured; no adoption claim. |
| Close panel/certification | No new opinion or certification produced. This is owner acceptance of selected launch scope, not full original-plan gate conformance. |
| P6/P7 transition/retirement | Separate work, owner `vasiloglou`, trigger an explicit transition/retirement request. |
| Historical carryovers | [Obligations](migration/obligations.md) unchanged; launch does not resolve unrelated questions. |

Historical migration evidence remains in [001](001-phase-1.md), [002](002-phase-2.md),
[003](003-phase-4-preparation.md), [004](004-phase-3.md),
[005](005-phase-4.1-preparation.md), [006](006-phase-4.1-review.md),
[007](007-phase-4.1-runtimes.md), [008](008-phase-4-signoff.md) and
[009](009-milestone-close.md), with its original bytes and bounds.

## Refactoring review

None needed. This close records published artifacts and live settings without
changing runtime code or packaged skills.
