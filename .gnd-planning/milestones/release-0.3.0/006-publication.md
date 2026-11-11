---
milestone: release-0.3.0
station: "publication stage"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: publication
date: 2026-11-11
source_base: 2165ccf1
gates:
  - command: "ruling: owner, publication of get-nick-done 0.3.0 by this session with the owner's stored credentials"
    exit: "n/a -- ruling"
  - command: "shasum -a 256 -c SHA256SUMS (the retained candidate); GET https://pypi.org/pypi/get-nick-done/0.3.0/json at 2026-11-11T15:36:31Z"
    exit: 0
    output: "three OK; 404"
  - command: "uvx twine check release/get_nick_done-0.3.0-py3-none-any.whl release/get_nick_done-0.3.0.tar.gz"
    exit: 0
    output: "PASSED with warnings: long_description missing (as for 0.2.0)"
  - command: "uvx twine upload --non-interactive --disable-progress-bar release/get_nick_done-0.3.0-py3-none-any.whl release/get_nick_done-0.3.0.tar.gz (2026-11-11T15:36:41Z)"
    exit: 0
    output: "View at: https://pypi.org/project/get-nick-done/0.3.0/"
  - command: "served-file comparison and fresh index install (evidence/publication/step-E-served-files.txt), 2026-11-11T15:37:52Z"
    exit: 0
    output: "both served sha256 equal the retained files; gnd 0.3.0"
  - command: "git tag -a v0.3.0 4c07c0e6a623263048cb675d237046ebb239cb32 -m 'get-nick-done 0.3.0'; git push origin v0.3.0"
    exit: 0
    output: "refs/tags/v0.3.0 257a8bb3, peeled 4c07c0e6"
  - command: "gh release create v0.3.0 --verify-tag --title 'GND v0.3.0' --notes-file evidence/RN3/github-release-notes.md <wheel> <sdist> SHA256SUMS.txt"
    exit: 0
    output: "https://github.com/vasiloglou/gnd-public/releases/tag/v0.3.0, Latest, not a draft"
  - command: "git apply of the three RN3 patches on main 2165ccf1; sh evidence/RN3/stale-text-check.sh token"
    exit: 0
    output: "no stale release-state text (20 allowlisted hits, route token, build 4c07c0e6, published 2026-11-11)"
  - command: "uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py tests/test_plan_app_docs.py tests/test_release_preparation.py tests/test_disclosure_docs.py"
    exit: 0
    output: "152 passed, 1 deselected in 5.90s"
  - command: "uv run --group docs zensical build --strict; uv run python tools/check_docs.py site"
    exit: 0
    output: "No issues found; 16461 local links/assets/anchors checked"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/evidence/publication/step-E-served-files.txt
    sha256: 034695116daccebb36cd42957d030f67475cfaa1d2ddc08dee2f1de3446f3104
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md
    sha256: a9293370a267d1d4fa437cf13851f8227e8b083f72a49850c0ecd6310086a332
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/candidate/SHA256SUMS
    sha256: c5a94218941a2745ddfae7b6925a8717dd9c73f5126d8a4da3fb124278cfa906
  - path: docs/release-notes.md
    sha256: f922334a5025974ce8e5913b601859d33e515a02516d7333a5dde5bbeaf66c30
  - path: docs/compatibility.md
    sha256: 9f44d3d26391e79b10b8f54643d3423c6d43524f9f7b710420fad997326c50bb
  - path: docs/support.md
    sha256: ec29384cd510dd85dc2a3c047508cbd3f3f0d35713b666dde0e186a7faef6bf8
  - path: docs/installation.md
    sha256: ddfb29ced50ad96b55baa70d8b6b6069157ce66906943671861108ec3064e692
  - path: README.md
    sha256: 368669d169fea78d6de4d012d2cc98db8b46e57f72004f88c061893bf86397c6
  - path: tests/test_release_version.py
    sha256: cfbcac41d8adc3be6301619957b3d013ed5a031cd70319bbf3e476489ea45075
---

# Claim

**get-nick-done 0.3.0 is published.** PyPI received the retained `4c07c0e6`
candidate on 2026-11-11 at 15:36:42Z (wheel) and 15:36:44Z (sdist). The
served files are byte-identical to it. Tag `v0.3.0` (`257a8bb3`, pointing to
`4c07c0e6`) is on the remote, and the GitHub release "GND v0.3.0" carries the
wheel, the sdist and `SHA256SUMS.txt`. The post-publication patches are
applied on this branch.

## RN-D13: the owner's publication request (a new decision)

The plan's RN-D5 said publication is owner acts and that the owner uploads by
hand. On 2026-11-11 the owner asked this session to do it. Quoted, in this
session:

| Request | Answer |
|---|---|
| the owner's message | "go on and also update pip" |
| "By 'go on and also update pip', do you want me to publish get-nick-done 0.3.0 to PyPI myself? ..." | "Yes, upload it" |
| "After the upload, should I also push the v0.3.0 tag and create the GitHub release ...?" | "Yes, try both" |

This replaces "the owner uploads by hand" for 0.3.0 only. The upload used the
credentials already stored on the owner's machine (`~/.pypirc`); this session
did not read, print or type them.

## What was done, in order

1. The retained files verified against `SHA256SUMS`; the version endpoint
   returned 404 at 15:36:31Z.
2. `twine upload` of exactly the release wheel and the sdist, at 15:36:41Z,
   exit 0. The comparison wheel was not uploaded.
3. Step E, from [the retained output](evidence/publication/step-E-served-files.txt):

        info.version 0.3.0 | files served: ['get_nick_done-0.3.0-py3-none-any.whl', 'get_nick_done-0.3.0.tar.gz']
        get_nick_done-0.3.0-py3-none-any.whl | served sha256 == retained 143890eed5e30e19619cd5c1106bddae6283c672d5c63200018fb23157c6751b | size 2948039 | uploaded 2026-11-11T15:36:42.218661Z | yanked False
        get_nick_done-0.3.0.tar.gz | served sha256 == retained 5e40d9e358ef49d335a4b0cf2c0919aff73a029076efa4f7c706b30109034c42 | size 2292882 | uploaded 2026-11-11T15:36:44.297911Z | yanked False
        gnd 0.3.0
        source_identity_verified: True

   A fresh environment installed `get-nick-done==0.3.0` from the index with
   no cache; `gnd --help` exits 0; the four Ossie schema files are present;
   an Ossie export and import of the packaged refunds model succeed.
4. The annotated tag and the GitHub release (Latest; assets: wheel
   `sha256:143890ee…751b`, sdist `sha256:5e40d9e3…4c42`, `SHA256SUMS.txt`).
5. The three patches applied to main `2165ccf1` with the date 2026-11-11.

## Boundary -- what this record does NOT establish

- The first run of step E failed: the version endpoint still answered 404
  sixteen seconds after the upload, while the simple index already listed
  0.3.0. It answered 200 at 15:37:38Z and the rerun is the retained output.
  The failed run's output is not retained.
- The index install ran on one machine (macOS arm64, Python 3.14).
- `twine check` warned that the package has no long description, as for
  0.2.0; the PyPI project page therefore shows no README text.
- The full default lane has not run on the patched tree; the patches change
  docs and one literal in `tests/test_release_version.py`.
- No announcement was made.
- This is not the milestone close.

## Open questions

- The milestone close: its record, the question sweep and the closing lane.
- Carried, unchanged: redaction and Ossie export; undocumented Ossie
  literals; full query budgets; structure guards outside focused gates; the
  unfiled fixtures-refactor issue; `docs/releasing.md` line 17.

## Refuted premises

- The dossier and the plan assumed the owner would run the upload, the tag
  and the release by hand, and that an agent session would be refused the
  tag push and the release creation as for 0.2.0. Neither was refused.
