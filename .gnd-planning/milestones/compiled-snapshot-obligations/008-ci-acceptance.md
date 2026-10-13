---
milestone: compiled-snapshot-obligations
station: ci-acceptance
skill: n/a -- owner-selected local CI acceptance
scope: ci-acceptance
date: 2026-10-13
gate:
  command: uv run pytest -q -ra --tb=short
  exit: 0
  output: "14007 passed, 400 deselected, 1 warning in 1867.43s (0:31:07); 14007 passed, 400 deselected, 1 warning in 1805.70s (0:30:05)"
---

# Claim

All selected local CI gates exit 0 on committed runtime and test repairs at
381187e41b1220fbc6a6026512627ad9e945c40c. Both clean macOS checkouts pass the
complete default suite on Python 3.11 and 3.13. Retained candidate installed
acceptance and documentation gates also exit 0. This record adds evidence only.

## Exact local CI results

    14007 passed, 400 deselected, 1 warning in 1867.43s (0:31:07)
    14007 passed, 400 deselected, 1 warning in 1805.70s (0:30:05)
    10 passed in 937.02s (0:15:37)
    10 passed in 905.67s (0:15:05)
    160 passed, 1 deselected in 35.77s
    160 passed, 1 deselected in 34.30s
    155 tutorial blocks passed
    No issues found
    6684 local links/assets/anchors checked

Collection selected 14,007/14,407 cases per interpreter with default marker
exclusions intact. Installer adoption and doctor exited 0 in both clean clones.
The platform subset is the workflow's agent_cli, guarded_corpus,
public_souffle_successors and v70_phase3_successors command. Installed acceptance
uses tests/test_release_acceptance.py with addopts cleared and the retained
candidate path, exercising release and sdist-rebuilt comparison wheels in
fresh target-only installs with macOS source-checkout denial. Candidate build,
strict documentation build, trusted offline tutorials and site checks follow
the workflow. No publisher/deployment step ran. Commands, profiles and raw
installed-log identities are in evidence/CI/local-ci-results.json.

## Artifacts

The release and comparison wheels are byte-identical:
1cc65028a2d5008ce5f2ca686de56c979db4742e3fe6b159fcadfd07d9c2dbbb.
The retained sdist digest is
7f948b413d0c1459bc90c4b220e76b65d9eb994ff23f909586717c4e18fdbe9a.
SOURCE_COMMIT, BUILD_PROFILE and SHA256SUMS copies bind the exact candidate.
Binary artifacts and full installed logs remain outside Git history under the
declared temporary CI root; those exact bytes are checkable only by their holders.
Committed full regression streams and result summaries permit review of the
reported exits without implying a new formal assurance certificate.

## Earlier reds and repair closure

007-ci-integration.md retains the earlier full-suite reds rather than rewriting
them. Its 32-node repair closure and 1,869 affected consumers were green on
both interpreters before this new complete replay. This complete replay now
restores the default-suite claim on the final repaired committed bytes.
Original goldens, prior records and certificates remain historical artifacts.

## Owner policy and merge boundary

The owner explicitly requires local-only CI and explicitly approved repository-
wide disabling of automatic Development and Documentation workflows. Their
states were verified disabled_manually; the active PR run was canceled. The
manual release workflow was not invoked or changed. Main protection retains
required PRs, zero required approving reviews, enforced administrators and no
required cloud status checks. The PR has no unresolved review threads.
Merge follows the owner's request to run local CI before merging and is a
separate action; this record does not itself merge, publish or deploy anything.

## Refactoring review and open questions

None needed: this event records current-byte acceptance of the already-reviewed
repairs. No new source or test behavior changed. App owner adoption and M3
acceptance at the eventual merged commit remain separate; occurrence admission
with compiled mode remains a successor milestone. Original authority and shim
carryovers retain their owners. No new certification is requested or inferred.

## Boundary

Both interpreters ran on this Mac; no local Linux run is claimed. Configured
provider, native, slow, proof, evidence, census and distribution exclusions stay
excluded from the default suite; distribution acceptance was separately selected
and passed as stated above. These gates do not prove full-walk equivalence,
external app acceptance, package release or source authority transfer. The
single serialization warning is from the existing malformed-feedback control,
not a suppressed failure. Opted-in compiled results continue carrying no
proof-backed assurance.

## Artifact identities
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-regression-3.11.log: fa97ee347b9c1f48ba2bc7dbcc290bc89eb9c8b4cd9111cb3c00f89ea7c21c40
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-regression-3.13.log: e2dc55f48e5cd181bfc9a1c6ff455c68e5553c12412d73b44b6b024faa973a46
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-platform-3.11.log: dda50df0f1c4fee6502d79d63980c7a175e144fc70d147b7aa2730b92b4bcbc6
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-platform-3.13.log: d012a4d688b368b5a3aa6b0d565ccceb82a0b3e70b06badef05cd7589bbaa120
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-tutorials.log: c15b38d36eb04bb36ad2d059a27023cc274128e191974611ac3196389858d301
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-docs-build.log: 8019c32740ca0a80699b092a0e079ec0cd1baebb906ee7c2167ccf1848bbeb9b
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-docs-check.log: 65a08ebb87789a024c09084f97065a7fd9facc522ab3e0a10cdb6b639b237c63
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-SOURCE_COMMIT: 87c45857c0ca1e34aa668f771742a17070223d9885348ef1e224be84d82a86e6
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-BUILD_PROFILE: ced0a0dcc0ef31596d907dd47e52e2f265c9b23ceae0e35e4449f5b6287d9890
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/accepted-SHA256SUMS: af707383d138f3b885679d42e686c1df915a11bac0e2d02d75ae46c4f014e413
- .gnd-planning/milestones/compiled-snapshot-obligations/evidence/CI/local-ci-results.json: 210acfb73719cd5b7f2a532de7417c76a95df98ed2333c8faa3a782cbbd99019
- .gnd-planning/milestones/compiled-snapshot-obligations/007-ci-integration.md: 4908e7da6f6a3561fd6af63c2587a0655ed3d4ebf7bfef5e004aa58428b472f1
