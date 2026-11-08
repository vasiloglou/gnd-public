---
milestone: rule-check-release
station: "phase-RR2"
skill: "n/a -- repository development via process-phase auto=false, not a gnd-solve station over a domain model"
scope: phase-RR2
date: 2026-11-08
gates:
  - command: "V1 at C=7c0f4d0e: grep -c '^## Unreleased' docs/release-notes.md; uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py --tb=short; PyPI JSON releases"
    exit: 0
    output: "0 headings; 33 passed, 1 deselected; ['0.1.0']"
  - command: "B1 (this Mac, uv 0.10.10): the M3 build of git archive C, then shasum -a 256 -c SHA256SUMS"
    exit: 0
    output: "release wheel e323c19e…69e4, sdist f85818ea…5104, comparison wheel e323c19e…69e4: OK"
  - command: "B2 (beast-3, uv 0.10.10): the same M3 build of git archive C, then diff against B1's SHA256SUMS"
    exit: 0
    output: "SHA256SUMS identical"
  - command: "V4 (beast-3, clean checkout at C, uv sync --locked --group dev --python 3.11): GND_CANDIDATE_DIR=<B1 copy> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short"
    exit: 0
    output: "14 passed in 803.35s (0:13:23)"
  - command: "V5: uvx --from ./release/get_nick_done-0.2.0-py3-none-any.whl gnd --version"
    exit: 0
    output: "gnd 0.2.0"
  - command: "V7: git diff 12daa5b7 C -- .github; gh api .../environments; gh run list --workflow release.yml; gh release list; PyPI JSON"
    exit: 0
    output: "0 lines; ['github-pages']; []; GND v0.1.0 only; ['0.1.0']"
slow_cadence:
  command: "GND_CANDIDATE_DIR=<retained candidate> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short"
  trigger: "any rebuild of the candidate (a new candidate under plan rule 4), and the prepare job if the owner dispatches it (RL-D6)"
  reason: "the acceptance file is the one addopts override RL-D8 selects; it took 13 minutes on beast-3"
evidence:
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-spec.md
    sha256: ec704b96b26e7ecaa10c3a55fb59011461b6f2faf6b24c8c591ac31c74f71fc4
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-codex-review.md
    sha256: 9682d02af50a7abd0c01fb880334bed3bf7d4a5730bb75df92bfab2141b85127
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-codex-review-impl.md
    sha256: 878e3864d0c9fae4987c26302714c4b30826e1500e57c110ca47d915eb429b08
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/t3-red-on-0.1.0.txt
    sha256: 0642e64025f3ab2acb1374f454c096957aef980e4d1bbf411bb75c2c66cd842a
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/premerge-check.txt
    sha256: 52159aaedf1ff7fd0736bb06444f76f703c1e368c16a3b6ed0da1874297b9804
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/v1-b1-v5-v7.txt
    sha256: e319a713c0355c9d7d7fb119e8058c7704b0a3c00e0403f84e5f9e2769ba8e13
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/beast3-b2-and-v4.log
    sha256: 93f4b019edbc3dec20b623f27bf756b9867d2609713caeb0d6e3128af57aca0d
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/beast3-script.sh
    sha256: 2f4b1078f774e8b8240112b6a1c90c47b56304851be589aa7c3bb74858fe42e0
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/candidate/SHA256SUMS
    sha256: 8a3c7d1e7380bfe7aee6682243dca5c1ac997eba528198177ce0b7ca549ca171
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/candidate/BUILD_PROFILE
    sha256: 4a783cae6484744e53898ff6e0b6b4813716e8803c208222cd9d7ad64c6c18d6
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/candidate/SOURCE_COMMIT
    sha256: c755a6c4d5fec040de31fbbcc1357a4885107ee0d0e5754ea49bd816f8b8820d
  - path: tests/test_release_acceptance.py
    sha256: 5f0de802bbca546a982437220d9b309d5f95cb00330b1fdbefd89a3cbff12ec5
  - path: docs/release-notes.md
    sha256: 48099755bb09a3e0642aa912ae44f08258351011b851fa5fa5cf7682ca5203a1
---

# Claim

The 0.2.0 candidate is built from main commit `7c0f4d0e`, the merge of PR 125.
It consists of `get_nick_done-0.2.0-py3-none-any.whl` (sha256
`e323c19e303f3b7fe9cbe7528e68021d271589ce0b91fd54bd76b2b919a069e4`) and
`get_nick_done-0.2.0.tar.gz` (sha256
`f85818ead9cb651ae397ecd3ab50f87fdf5f9f7c7bada58a659cea2cb99e5104`).

- **Reproducible:** two builds on two Macs give identical bytes, and the wheel
  rebuilt from the sdist equals the release wheel.
- **Acceptance:** release acceptance passes over the retained files: 14 passed,
  exit 0, on beast-3 (macOS 27.0.1, arm64, Python 3.11.18, uv 0.10.10).
- **Every issue-118 item works when installed from the wheel:** `--rule-ids`,
  `--baseline`, `--allow-vacuous`, `remedy`, the acyclic extent, and
  `source: tool-output` with `producer`.
- **None of them exists in the published 0.1.0**, and the plain check gives
  the same result on input both releases accept.
- **Nothing is published.**

## What shipped

- **M1** `docs/release-notes.md`: one bullet for FU2, the population-header
  change, in the 0.2.0 rule-check block. FU3 changed only tests and gets no
  entry. At `C` the notes have no `## Unreleased` heading (RR2-C0).
- **M2** `tests/test_release_acceptance.py`: two new tests, plus helpers and a
  fixture.
  - `test_installed_rule_check_carries` (T1) runs from the installed wheel,
    each probe with its control, and checks the version and artifact names.
  - `test_published_0_1_0_lacks_rule_check` (T2) uses the hash-checked PyPI
    0.1.0 wheel for the availability controls and the comparable-default
    comparison.
  - No existing line changed except the imports. Every later prepare run
    repeats both tests.
- **M3**: the candidate build itself, recorded below; no tracked script.
- **Part-one commits**, merged in PR 125: `07fe245d`, `ea236619`, `cbe5f57a`
  (review fixes) and the spec record `86e5e1f1`. Spec §14 has the part-one
  findings.

## The candidate (D1 (b), D2 (a))

| Item | Value |
|---|---|
| Source | main `7c0f4d0e320ff7976296d785077280d180ea688e`, the merge commit of PR 125. Its parents are `df5753bf` and `86e5e1f1`, and its tree equals `86e5e1f1`'s |
| Files | `SHA256SUMS` in `evidence/RR2/candidate/`. The files are kept outside git, at `~/gnd-release/0.2.0/7c0f4d0e/candidate/` on this Mac and `~/gnd-release/0.2.0/7c0f4d0e/candidate-b1/` on beast-3 (both verified with `shasum -c`) |
| B1 profile | this Mac: macOS 26.6.2 arm64, uv 0.10.10 (Homebrew), `python3` 3.14.4 |
| B2 profile | beast-3: macOS 27.0.1 arm64, uv 0.10.10 (installed from PyPI into an isolated venv), `python3` 3.9.6 |
| Reproducibility (RR2-C2, RL-D7) | B1 equals B2 in all three files; the release wheel equals the comparison wheel. An earlier scratch build of `ea236619` gave the same hashes; the packaged paths did not change between the two |
| Observed acceptance profile (RR2-C6) | beast-3, macOS 27.0.1 arm64, Python 3.11.18 (uv-managed, the workflow's minor version), uv 0.10.10. No other profile is claimed |

## Gate output (verbatim)

V4 on beast-3, from `evidence/RR2/beast3-b2-and-v4.log`:

    + GND_CANDIDATE_DIR=/Users/…/gnd-release/0.2.0/7c0f4d0e/candidate-b1 uv run pytest -q -o 'addopts=' tests/test_release_acceptance.py '--tb=short'
    ..............                                                           [100%]
    14 passed in 803.35s (0:13:23)
    + echo 'V4 exit=0'

The other gate outputs are in `evidence/RR2/v1-b1-v5-v7.txt` and in the front matter.

## Execution findings

- **The first beast-3 run failed at setup, before any test ran.** The git
  bundle named a commit but no branch, so the clone was empty; the build and
  the tests found no project, and the run exited at once. The bundle was
  remade with a branch, and the script now stops at the first failed setup
  step (`evidence/RR2/beast3-script.sh`). The failed log was deleted before
  the rerun and is not retained; this paragraph is its only record.
- The build profile files record `python3 --version`, which does not affect
  the build: `uv build` runs the `uv_build` backend.

## Adversarial review

One reviewer, Codex, read each part; each reviewer is one reviewer.

- **Spec r1:** `revise`, nine findings, all accepted, repaired in r2
  ([review](notes/phase-RR2-codex-review.md)).
- **Part-one diff:** `revise`, findings I1 to I4, all fixed in `cbe5f57a`
  ([review](notes/phase-RR2-codex-review-impl.md); dispositions in spec §14).
  I1's premise was partly refuted.
- **This record and its evidence:** the part-two review is appended below.

The repaired bytes carry no review opinion of their own.

## Refactoring review

None executed. See spec §14: the new helpers stay separate from the file's
`run`, because `run` cannot return stderr on an expected nonzero exit.

## Boundary -- what this phase does NOT establish

- **Nothing is published.** No upload, tag, GitHub release, `pypi`
  environment, publisher registration or workflow dispatch (V7). Publisher
  registration on PyPI's side cannot be read and is not audited.
- **The candidate's evidence is not the evidence for a later publication's
  bytes.** Under the workflow route, publication uploads the publishing run's
  own build (O7, R4). Only a token upload of these retained files would carry
  this identity, and only a comparison of the served files after publication
  establishes it.
- **One acceptance profile was observed** (beast-3, macOS 27, Python 3.11).
  Not observed: Ubuntu, other Python versions, the index install form
  (`get-nick-done==0.2.0`), TestPyPI, and any external user trial.
- **V4 ran over B1's files only.** B2 was compared by hash, not run.
- **The sandbox (RR2-C7)** is macOS `sandbox-exec` with one profile. It
  denies reads of the checkout's parent directory; it is not a general proof
  of isolation.
- **T3 failed earlier than the spec predicted** (spec §14). T1's P1 assertion
  is shown to fail on 0.1.0 through T2, not by T1's own red run.
- **D4 (a): `tests/test_public_distribution.py` was not run.** Its four
  `VERSION` lines remain unexecuted; T1 asserts the same facts on the
  candidate files.
- **PyPI availability of 0.2.0 was observed at 2026-11-08T05:12Z.** It must
  be checked again immediately before any upload (plan C2, R7).

## Open questions

- RR3: the dossier, the post-publication patch (pins, `RELEASED`, the
  compatibility text, the support row with this observed profile) and the
  `docs/releasing.md` wording each need RR3's spec and owner gate.
- The 0.1.0 control downloads from `files.pythonhosted.org` on every prepare
  run (D3); if PyPI ever removed 0.1.0, T2 would fail with the hash or lookup
  message.
- Carried from RR1, unchanged: the deferred version-independent fixtures
  refactor (target: the next release-prep milestone, owner to name it), and
  the two load-sensitive timing tests (the close records whether they recur).

## Refuted premises

- Plan §2 said 0.1.0 refuses the new options with exit 2; it exits 64
  (spec §13; the plan sentence is corrected at its site).
- Spec §8 said T3 would fail at the first `gnd_json`; it fails earlier, at
  `copy_example`, because 0.1.0 ships no `rule_check` example (spec §14).
- Review I1's premise, that the outer test process must not read the source
  checkout, is refuted. The file reads it by design, both through
  `git archive HEAD` and through its `test_packaged_skills` import (spec §14).
