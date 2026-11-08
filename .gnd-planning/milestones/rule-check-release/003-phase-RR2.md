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
  - command: "B2, run 2 (beast-3, fresh directory, uv 0.10.10 from `uvx --from uv==0.10.10` as D5 ruled, script stops at any failure): the same M3 build of git archive C; shasum -c of the B1 copy; diff of the two SHA256SUMS"
    exit: 0
    output: "B1 copy: 3 x OK; B2: 3 x OK; B1 and B2 SHA256SUMS identical"
  - command: "V4, run 2 (beast-3, clean checkout at C, uv sync --locked --group dev --python 3.11): GND_CANDIDATE_DIR=<B1 copy> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short"
    exit: 0
    output: "14 passed in 791.58s (0:13:11), ended 2026-11-08T05:45:18Z"
  - command: "V5 after V4 (2026-11-08T05:45:53Z, this Mac): uvx --from ./release/get_nick_done-0.2.0-py3-none-any.whl gnd --version"
    exit: 0
    output: "gnd 0.2.0"
  - command: "V7 (2026-11-08T05:45:55Z): git diff 12daa5b7 C -- .github; environments; release.yml runs; GitHub releases; remote tags; PyPI JSON"
    exit: 0
    output: "0 lines; ['github-pages']; 0; ['v0.1.0']; refs/tags/v0.1.0 only; ['0.1.0']"
  - command: "V8 at the record commit: scripts/components_index.py changed --base origin/main; git diff --stat C HEAD -- src pyproject.toml LICENSE NOTICE"
    exit: 0
    output: "changed against origin/main (7c0f4d0): 14 file(s) differ; 0 to fix, 0 warning(s), 0 to reread; packaged-path diff C..HEAD: 0 lines"
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
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/beast3-run2-b2-and-v4.log
    sha256: caddefd26f812f3fe6f2a915f273884ec8b7ed6c450803051c6cdbf2a77f546a
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/beast3-script-run2.sh
    sha256: 97d19dd83b55f54b7289ceaa0800b2d488ce96ea399058b00aa30611ccd0377c
  - path: .gnd-planning/milestones/rule-check-release/evidence/RR2/post-v4-v5-v7.txt
    sha256: 58dd592334fa1cd1be048590ded94923b59391bf9b0411f6db66a678f569c959
  - path: .gnd-planning/milestones/rule-check-release/notes/phase-RR2-codex-review-record.md
    sha256: a50bac6df0570d0915587875c84ce597ca68d8e311931b25cfd4796a4147cd21
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
  exit 0, on beast-3 (macOS 27.0.1, arm64, Python 3.11.18, uv 0.10.10). Two
  runs passed; the second one, with the setup D5 ruled, is the gate of record.
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
| Files | `SHA256SUMS` in `evidence/RR2/candidate/`. The files are kept outside git: at `~/gnd-release/0.2.0/7c0f4d0e/candidate/` on this Mac (`shasum -c` before V5, `evidence/RR2/post-v4-v5-v7.txt`) and at `~/gnd-release/0.2.0/7c0f4d0e/candidate-b1/` on beast-3 (`shasum -c` in run 2's log, and again by V4's own `candidate` fixture) |
| B1 profile | this Mac: macOS 26.6.2 arm64, uv 0.10.10 (Homebrew), `python3` 3.14.4 |
| B2 profile | beast-3: macOS 27.0.1 arm64, uv 0.10.10, the binary that `uvx --from uv==0.10.10` fetched (path in run 2's log), `python3` 3.9.6 |
| Reproducibility (RR2-C2, RL-D7) | B1 equals B2 in all three files; the release wheel equals the comparison wheel. An earlier scratch build of `ea236619` gave the same hashes; the packaged paths did not change between the two |
| Observed acceptance profile (RR2-C6) | beast-3, macOS 27.0.1 arm64, Python 3.11.18 (uv-managed, the workflow's minor version), uv 0.10.10. No other profile is claimed |

## Gate output (verbatim)

V4 run 2 on beast-3, from `evidence/RR2/beast3-run2-b2-and-v4.log`:

    +./rr2-beast2.sh:48> GND_CANDIDATE_DIR=/Users/…/gnd-release/0.2.0/7c0f4d0e/candidate-b1 uv run pytest -q -o 'addopts=' tests/test_release_acceptance.py '--tb=short'
    ..............                                                           [100%]
    14 passed in 791.58s (0:13:11)
    +./rr2-beast2.sh:49> echo 'V4 exit=0'

The other gate outputs are in `evidence/RR2/v1-b1-v5-v7.txt` (V1 and B1, at 05:12Z),
`evidence/RR2/post-v4-v5-v7.txt` (V5 after V4, V7 with the tag audit, FU4) and
the front matter.

## Execution findings

- **Three beast-3 runs; the third is the gate of record.**
  - **Run 1 (not retained):** failed at setup before any test ran. By my
    account the bundle held a commit but no branch, so the clone came out
    empty. Its log was deleted before run 2, so nothing retained verifies
    these details (review R3).
  - **Run 2:** `evidence/RR2/beast3-b2-and-v4.log` and `beast3-script.sh`.
    B2 was identical and V4 passed (14 passed in 803.35s). But the venv step
    for uv failed because run 1 had already created `uv01010`. The script
    then went on with the existing uv 0.10.10 binary, without the pinned
    install, and it did not stop at every failed step (review R1, R2).
  - **Run 3**, kept on beast-3 as `run2/`: `evidence/RR2/beast3-run2-b2-and-v4.log`
    and `beast3-script-run2.sh`. It used a fresh directory, took uv 0.10.10
    from `uvx --from uv==0.10.10` as D5 ruled, and stops at any failed step,
    writing its status last. It logged `shasum -c` of the B1 copy. B2 was
    again identical, and V4 passed (14 passed in 791.58s).
- **FU4 is not in the candidate.** It merged as PR 129 at 05:39Z, after the
  candidate commit `C` was fixed (05:12Z) and built. `C` is an ancestor of the
  FU4 merge. FU4 changed nothing under `src/` or `docs/`, and main has no
  `## Unreleased` heading after it, so RR2-C0 needs no fold-in and leaves no
  separate section (`evidence/RR2/post-v4-v5-v7.txt`). The candidate is
  unaffected.
- The build profile files record `python3 --version`, which does not affect
  the build: `uv build` runs the `uv_build` backend.

## Adversarial review

One reviewer, Codex, read each part; each reviewer is one reviewer.

- **Spec r1:** `revise`, nine findings, all accepted, repaired in r2
  ([review](notes/phase-RR2-codex-review.md)).
- **Part-one diff:** `revise`, findings I1 to I4, all fixed in `cbe5f57a`
  ([review](notes/phase-RR2-codex-review-impl.md); dispositions in spec §14).
  I1's premise was partly refuted.
- **This record and its evidence (at `ceaf36dd`):** `revise`, findings R1
  to R7 ([review](notes/phase-RR2-codex-review-record.md)); dispositions
  below.

The repaired bytes carry no review opinion of their own.

### Dispositions of the record review

| Finding | Disposition | Applied |
|---|---|---|
| R1 uv provenance in run 2 | accepted, confirmed in the log | rerun with `uvx --from uv==0.10.10` in a fresh directory; that run is the gate of record |
| R2 the script did not stop at a failed step | accepted | the new script stops at any failure (`ERR_EXIT`, `PIPE_FAIL`, `ZERR` trap) and writes its status last; the finding text is corrected |
| R3 the run-1 account is unverified | accepted | labelled as an unretained, unverified account |
| R4 V5 was not shown after V4 | accepted | V5 repeated at 05:45:53Z, after V4 ended at 05:45:18Z |
| R5 `shasum -c` of the beast-3 B1 copy not logged | accepted | logged in the new run |
| R6 V8 and the tag audit missing | accepted | V8 in the gates; V7 now lists the remote tags (`v0.1.0` only). The boundary separates what the phase did from what V7 observed |
| R7 "review appended below" was not true | accepted | this table |

The corrected record and the new run carry no review opinion of their own.

## Refactoring review

None executed. See spec §14: the new helpers stay separate from the file's
`run`, because `run` cannot return stderr on an expected nonzero exit.

## Boundary -- what this phase does NOT establish

- **Nothing is published.** This phase ran no upload, tag, release,
  environment, publisher or workflow command. V7 observed, at 05:45:55Z, the
  same state as the plan baseline: no `pypi` environment, no `release.yml`
  run, only the `v0.1.0` tag and release, and PyPI listing only 0.1.0. Publisher
  registration on PyPI's side cannot be read and is not audited.
- **The candidate's evidence is not the evidence for a later publication's
  bytes.** Under the workflow route, publication uploads the publishing run's
  own build (O7, R4). Only a token upload of these retained files would carry
  this identity, and only a comparison of the served files after publication
  establishes it.
- **One acceptance profile was observed** (beast-3, macOS 27, Python 3.11).
  Not observed: Ubuntu, other Python versions, the index install form
  (`get-nick-done==0.2.0`), TestPyPI, and any external user trial.
- **V4 ran over B1's files only.** B2 was compared by hash, not run. V5 ran
  on this Mac (macOS 26.6.2), not on the V4 host.
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
