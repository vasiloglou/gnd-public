---
milestone: release-0.4.0
station: phase-RV2
scope: phase-RV2
date: 2026-11-17
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
source_commit: 648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a
gates:
  - command: "Freeze checks of main, PyPI simple index and six default shards on beast-3"
    exit: "source and index 0; shards 1, 0, 0, 0, 0, 0"
  - command: "First and independent uv 0.10.10 builds using build.sh"
    exit: 0
  - command: "Compare B1/B2 SHA256SUMS; verify preserved SOURCE_COMMIT and SHA256SUMS on beast-3"
    exit: 0
  - command: "GND_CANDIDATE_DIR=<retained> uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short"
    exit: 0
  - command: "uvx --python <beast-3 Python 3.11.18> --from <retained release wheel> gnd --version"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/accept-beast3.sh
    sha256: 043fefc7e6e351417c3a873e41cb1671979b87d7ea530b07204316fee758fa04
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/acceptance-summary.txt
    sha256: 856bf62a980af22fa326de9fcf58bf4d0d37220656dbc0aa62da2f248001e292
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/build-summary.txt
    sha256: 299e785177a1acabac843cba087f3eec8ce7d7dd91a826457529cde15eeb55cb
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/build.sh
    sha256: c155e4a0a2bc3ef64f5e90192a29952828478d24ff45be7b25d57606eb1495e1
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/candidate/BUILD_PROFILE
    sha256: 4a9a76eb7f68802a0a7e4043b76f417ffc051b80bbcf489bd442daf842ef34a7
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/candidate/SHA256SUMS
    sha256: c813c3ad074711e466968448658b8dfcb81e2db033524bf598cea88f6ece9d59
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/candidate/SOURCE_COMMIT
    sha256: 24fb580007edd88258ea4888c86d476e7c8d8446ec2f3d9c09e671a642a7f447
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/freeze-shards.sh
    sha256: 2a1150579a2fe4754fed5293d75abe63ce17fd56d7567413e9daf0cba05f9554
  - path: .gnd-planning/milestones/release-0.4.0/evidence/RV2/freeze-summary.txt
    sha256: 3404e7c96e766b1418a1a34e18b49b37e2e7a456029e1f65bae363f852a3352f
  - path: .gnd-planning/milestones/release-0.4.0/007-RV2-pre-freeze.md
    sha256: c7568a30b6a15bfcc3378658f9dcc4b0171abb5afcae90ee441c19084f79be37
---

# Claim

RV2 built and accepted GND 0.4.0 from main commit
`648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`. The owner approved merging
PR 209 on 2026-11-17. The acceptance checkout was clean and matched the
candidate source receipt.

| Criterion | Result |
|---|---|
| RV2-C0 | No source, dependency, workflow, or docs changes between the RV1 merge and freeze. PR 204 remained an unmerged draft. The PyPI simple index listed releases up to 0.3.0. The full lane completed before the first build with 19,699 passes, 13 skips, the same two setup errors and zero new failures. |
| RV2-C1 | The first build used a Git archive on macOS 26.6.2 arm64, CPython 3.11.15 and uv 0.10.10. The wheel and sdist were retained outside Git. |
| RV2-C2 | The independent beast-3 build used macOS 27.0.1 arm64, CPython 3.11.18 and uv 0.10.10. All three artifact hashes agree. |
| RV2-C3 | Copied files were rehashed before the installed gate. The test archive used the checked `SOURCE_COMMIT`. |
| RV2-C4 | All 23 selected cases passed, covering the former positive regressions, wrong-source and file controls, new feature probes and hash-pinned 0.3.0 controls on both wheel origins. |
| RV2-C5 | `uvx` printed `gnd 0.4.0` from the retained wheel. |
| RV2-C6 | The installed profile is beast-3, macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10. |

The retained directory on both Macs is
`~/gnd-release/0.4.0/648cc6e0/candidate/`. There are two releasable files and
one comparison wheel. The release wheel and the comparison wheel are
3,421,324 bytes each. The sdist is 2,551,056 bytes. The committed
[checksum receipt](evidence/RV2/candidate/SHA256SUMS) binds them.

## Gate output (verbatim selected lines)

    Independent wheel, sdist and comparison wheel match the retained SHA256SUMS.
    release/get_nick_done-0.4.0-py3-none-any.whl: OK
    release/get_nick_done-0.4.0.tar.gz: OK
    comparison/get_nick_done-0.4.0-py3-none-any.whl: OK
    23 passed in 920.19s (0:15:20)
    Installed acceptance exit 0.
    gnd 0.4.0

See the [freeze lane](evidence/RV2/freeze-summary.txt), [first build](evidence/RV2/build-summary.txt),
and [independent build and acceptance](evidence/RV2/acceptance-summary.txt).
The installed command used the explicit RV-D7 distribution selection.
The default full lane kept its exclusions for derivation_oracle,
pyrel_oracle, ossie_oracle, distribution, network, slow, live, review_runner,
proof, evidence and census.

## Review and refactoring

The [pre-freeze checkpoint](007-RV2-pre-freeze.md) retains the independent
Claude Code review of the probe diff, the source-binding repair, and the
rehearsal controls. One reviewer is one reviewer. That round did not review
the subsequent artifact or test-run bytes. The probes reuse the prior
artifact, isolated interpreter, and wheel resource helpers. No production
refactor was required.

## Boundary

The candidate evidence applies to the exact retained files. The later
served-file and index-install checks require publication. GitHub prepare,
Trusted Publishing, additional platforms, and default-excluded lanes were
outside this run. Count certificates from PR 204 were outside the candidate.

## Open questions

- RV3 hands the owner the exact retained identities and a tested scratch
  page update, including the receipts and BookRec guidance identified in RV1.
- The milestone close audits authorized actions after publication.
