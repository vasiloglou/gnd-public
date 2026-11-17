---
milestone: release-0.4.0
station: publication
scope: publication
date: 2026-11-17
source_commit: 648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a
gates:
  - command: "Twine upload of the two retained release files to https://upload.pypi.org/legacy/"
    exit: 0
  - command: "Compare the PyPI version endpoint and downloaded wheel and sdist against accepted SHA-256 values"
    exit: 0
  - command: "git push origin refs/tags/v0.4.0:refs/tags/v0.4.0 and verify the remote peeled commit"
    exit: 0
  - command: "gh release create v0.4.0 --verify-tag with three attachments, then download and compare all three"
    exit: 0
  - command: "Install get-nick-done==0.4.0 from public PyPI and check the packaged dispatch inputs"
    exit: 0
  - command: "uv run --no-sync python tools/release_text.py publish --date 2026-11-17 --built 648cc6e0 --profile 'macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10'"
    exit: 1
  - command: "git apply --check and git apply the RV3 supplemental patch; uv run --no-sync python tools/release_text.py check"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short"
    exit: 0
  - command: "uv run --no-sync pytest -q tests/test_rf5_commands.py tests/test_rf5_review_regressions.py tests/test_rf6_query_policy.py tests/test_rf7_structure.py tests/test_rf8_structure.py tests/test_rf9_repairs.py tests/test_rof4_accept_identities.py tests/test_disclosure_mode.py tests/test_disclosure_docs.py tests/test_packaged_skills.py tests/test_conformance_payload.py tests/test_development_scaffold.py --tb=short"
    exit: 0
  - command: "uv run --no-sync --group docs zensical build --strict; uv run --no-sync python tools/check_docs.py site"
    exit: 0
  - command: "uv run --no-sync ruff check --output-format json"
    exit: 1
  - command: "uv run --no-sync ruff check tests/test_release_version.py"
    exit: 0
evidence:
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/github-release.txt
    sha256: 4ec83a1af5aefcde54a75479613d2d68d2091e2d5991e4deb2ff61d1107cc36d
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/published-pages-docs.txt
    sha256: 47cc395e3a913017f8efe4f5db3ecae11bd501986f6efa0d71f0fd27fbd995f7
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/published-pages-guards.txt
    sha256: ae0ea9c0d3520c85f3934ff9bb8a43ebf7f94e35b3c91aaa3fc6ad9c65b1a397
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/published-pages-tests.txt
    sha256: 72a7d06606ac649ded753cb69f97216e37268637cea2bae75766d0d8495c77c9
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/published-pages-tool.txt
    sha256: 1bce92039f9f2a1e5d84d959410548d7c9939a6547b541fe07d2451aa6cc47d0
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/pypi-install.txt
    sha256: e9d1e7a6c5f011d10d3ec1b694cd9a10f0363366507d71960ee44d4620e1a07c
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/pypi-served.txt
    sha256: 0cc616abec4a34f3544629c327aaee145f2bc1c88a8034fe0cc99ae06374bd90
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/pypi-upload.txt
    sha256: 6f0aafcaa63eb4c15d62475adf87a7f12e74a73dcdf7c13b716a0dd041b4ca57
  - path: .gnd-planning/milestones/release-0.4.0/evidence/publication/tag.txt
    sha256: 68c7402b2b208c6d0d679c85fa9286803712e5fb2ace79cd5ab5e4e5111762b4
---

# GND 0.4.0 publication

The owner authorized each act separately in the release chat on 2026-11-17.
Each recorded reply was “authorized” to the immediately preceding request
identifying the action.

| Authorized act | Observed receipt |
|---|---|
| Upload the two accepted files to PyPI | [Twine exit 0](evidence/publication/pypi-upload.txt) at 15:09:38Z. The prior availability check found HTTP 404 and no 0.4.0 simple-index entries. |
| Annotate and push the source tag | [Remote tag verification](evidence/publication/tag.txt) at 15:21:15Z shows tag object `a6ad5b534bc5c668079fa309bc74f69a67c22852` peeling to `648cc6e07fc6ea0e4d8791a2a33a0d005f4e106a`. |
| Publish the GitHub release with three assets | [Release and attachment checks](evidence/publication/github-release.txt) show publication at 15:23:59Z and equality of the wheel, sdist and checksum file upon download. |
| Exercise a fresh install from PyPI | [Install and dispatch smoke](evidence/publication/pypi-install.txt) completed at 15:27:13Z with CLI version 0.4.0, invalid input exit 1 and repaired input exit 0. |
| Open the publication documentation PR | This record accompanies the topic PR based on `2f1930e5`. Merge is separately authorized. |

The [served PyPI files](evidence/publication/pypi-served.txt) match the accepted
candidate byte for byte. The production actions required neither a GitHub
release workflow dispatch nor a publisher configuration change. The upload
used the documented local PyPI credential configuration.

The automatic documentation helper produced its expected residual exit 1.
The reviewed RV3 supplement removed those residuals and the separately
identified receipts wording. The resulting product-page diff SHA-256 is
`3f0b4e33bce19b7db039d53387c62143c56081e6c46b765f4b88c0562eb837cf`,
identical to the recorded RV3 rehearsal.

## Gate output (verbatim selected lines)

    Both served PyPI files match the accepted candidate.
    All three GitHub release attachments match the originals.
    gnd 0.4.0
    dispatch/seed.pop.json: exit 1
    dispatch/repaired.pop.json: exit 0
    no page describes the state before 0.4.0 was published
    85 passed, 1 deselected in 0.56s
    679 passed, 2 deselected in 97.08s (0:01:37)
    No issues found
    18347 local links/assets/anchors checked
    Full Ruff exit 1: the same 188 baseline diagnostics.
    All checks passed!

## Boundary

The install smoke used macOS 26.6.2 arm64, Python 3.11.15 and uv 0.10.10.
The actual release acceptance profile remains the one in the RV2 record.
Publication used the retained accepted files. Final documentation merge and
milestone close remain separate.

## Open questions

- Record the owner-authorized documentation PR merge, then perform the
  close lane, remote audit and standard GND panel review.
