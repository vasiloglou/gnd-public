---
milestone: release-0.3.0
station: "phase RN2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RN2
date: 2026-11-11
source_base: f9f502d9
candidate_commit: 4c07c0e6a623263048cb675d237046ebb239cb32
gates:
  - command: "ruling: owner approved .gnd-planning/milestones/release-0.3.0/notes/phase-RN2-spec.md sha256 9fc68562775878116a2d5463462c5c7cd2789dd5280027770abf49854c835aa3 (r1 at 53785bc8), D1 to D4 and D6 as recommended; D5 not run"
    exit: "n/a -- ruling"
  - command: "GND_CANDIDATE_DIR=<the retained 0.2.0 candidate> uv run pytest -q -o addopts='' tests/test_release_acceptance.py -k test_installed_0_3_0_carries (T3, red first)"
    exit: 1
    output: "2 failed, 16 deselected in 15.08s"
  - command: "uv build --out-dir ../candidate/release; uv build --wheel ../candidate/source/* --out-dir ../candidate/comparison; shasum -a 256 -c SHA256SUMS (B1, this Mac, from git archive 4c07c0e6)"
    exit: 0
    output: "release wheel, sdist and comparison wheel: OK"
  - command: "diff candidate-b1/SHA256SUMS b2/candidate/SHA256SUMS (B2 on beast-3)"
    exit: 0
    output: "B1 and B2 SHA256SUMS identical"
  - command: "GND_CANDIDATE_DIR=<B1 copy> uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short (V4, beast-3, clean checkout at 4c07c0e6, Python 3.11.18, uv 0.10.10)"
    exit: 0
    output: "18 passed in 846.58s (0:14:06)"
  - command: "evidence/RN2/beast3-script.sh as a whole"
    exit: 127
    output: "STOPPED at line 53: uvx: command not found, after V4 exit=0"
  - command: "uv tool run --from <B1 wheel> gnd --version (beast-3, uv 0.10.10); uvx --from <B1 wheel> gnd --version (this Mac)"
    exit: 0
    output: "gnd 0.3.0, both"
  - command: "uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_development_scaffold.py (at 79680fd0)"
    exit: 0
    output: "140 passed, 2 deselected in 19.66s"
  - command: "GET https://pypi.org/simple/get-nick-done/ and /pypi/get-nick-done/0.3.0/json at 2026-11-11T14:52:10Z and 15:08:14Z"
    exit: 0
    output: "versions 0.1.0, 0.2.0; 0.3.0 returns 404, both times"
  - command: "git diff --stat f9f502d9 4c07c0e6 -- .github; git ls-remote --tags origin; gh release list; gh run list --workflow release.yml; gh api .../environments"
    exit: 0
    output: "0 lines; v0.1.0 75eda93f and v0.2.0 d84ad6d5 (peeled 7c0f4d0e); releases v0.1.0, v0.2.0; 0 runs; github-pages"
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (review of f9f502d9..b8afdaa6 -- tests, prompt on stdin)"
    exit: 0
    output: "DISPOSITION: revise; G1 to G7, six applied, one accepted as a limit"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RN-D11, 2026-11-10)"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN2-spec.md
    sha256: ca7de2c4995ab8a0d2ffa31dbb4574de2bd23dd98960025baade52c68811246e
  - path: .gnd-planning/milestones/release-0.3.0/notes/phase-RN2-codex-review.md
    sha256: fb4c9f35906918d27efe04bf8634d8143160baeaa8e5245a7db12093ac8bd2e1
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/candidate/SHA256SUMS
    sha256: c5a94218941a2745ddfae7b6925a8717dd9c73f5126d8a4da3fb124278cfa906
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/candidate/SOURCE_COMMIT
    sha256: f2b2866db1fc8a80a327b8a11e0774cf7f92d81c68030db19b88e759659999bf
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/candidate/BUILD_PROFILE
    sha256: d37ef6f6b5f990b41ab5c0c98b973953aa2b154d64679193d9d755b773c08988
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/beast3-script.sh
    sha256: 858285986a844bfaa3191318663049ffca77c85d40f5208686f324ea0a70065a
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/beast3-run.log
    sha256: 2c9928ed292b3a5a1ff12c609cfe020521025cfb62c23dfe341db018ab260a19
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/t3-red-on-0.2.0.txt
    sha256: 8176f53184c5e770477dba28e67e38a5852f1c6d51ffa14c031a5537d138a304
  - path: tests/test_release_acceptance.py
    sha256: 4d97b705ffff433ad53f0977042d7c92a20b8ba280c2559fb0c5ab58fd94f946
  - path: tests/fixtures/release-acceptance/0.3.0/README.md
    sha256: 812fd988f7dac5335f766a193b50a3ea7d6fe7cb69b2bd414cb34642389679d3
---

# Claim

The 0.3.0 candidate is built from main commit `4c07c0e6` and passes installed
acceptance. It is retained outside git at `~/gnd-release/0.3.0/4c07c0e6/candidate/`
on the build machine, with a copy on beast-3 (`candidate-b1`). These bytes are
not in history; their identities are:

| File | Size | sha256 |
|---|---|---|
| `release/get_nick_done-0.3.0-py3-none-any.whl` | 2,948,039 | `143890eed5e30e19619cd5c1106bddae6283c672d5c63200018fb23157c6751b` |
| `release/get_nick_done-0.3.0.tar.gz` | 2,292,882 | `5e40d9e358ef49d335a4b0cf2c0919aff73a029076efa4f7c706b30109034c42` |
| `comparison/get_nick_done-0.3.0-py3-none-any.whl` | 2,948,039 | `143890eed5e30e19619cd5c1106bddae6283c672d5c63200018fb23157c6751b` |

Over those files, `tests/test_release_acceptance.py` exits 0 on beast-3 with
Python 3.11.18: 18 passed. A second, independent build on beast-3 produced
identical files. Nothing is uploaded, tagged or published.

## What shipped

- Part one (PR 164, merged as `4c07c0e6`): two tests and one fixture in
  `tests/test_release_acceptance.py`; inputs under
  `tests/fixtures/release-acceptance/0.3.0/`.
- Part two (this record): the candidate, its identity files
  (`evidence/RN2/candidate/`), the beast-3 script and its log.

## What the acceptance run shows

From the installed wheel, outside the checkout, under the macOS sandbox that
denies reads of the source tree:

- the wheel lists the four Ossie schema files, and an Ossie export and import
  of the packaged refunds model work: three files written, `refund_by` is
  many-to-one in the YAML, the restored model has the source's identity, and
  a changed ontology is refused with nothing written;
- `gnd validate --identity` prints a digest equal to the sha256 of the
  document it prints, and a renamed type or a changed rule moves it;
- a packaged version 5 model with an include validates, and a wrong pin is
  refused with `include:hash-mismatch`;
- `--check-population` admits a new rule on clean data and refuses it on
  violating data, and without the option the rule is refused;
- `--require-documents` exits 3 on an unchecked span, the same span is a
  warning without it, and full coverage exits 0;
- the published 0.2.0 wheel (hash-pinned) refuses each of those: exit 64 for
  the four new commands and options, exit 3 for the version 5 model;
- the fourteen earlier tests of the file, the 0.1.0 controls among them,
  pass on the 0.3.0 candidate.

## Gate output (verbatim)

Rulings, owner, 2026-11-11, in this session: "Skip it for 0.3.0" (the Ossie
oracle lane, D5); "Approve, start RN2" (the spec, D1 to D4 and D6); "Merge PR
164" (the candidate commit).

From [beast3-run.log](evidence/RN2/beast3-run.log):

    B1 and B2 SHA256SUMS identical
    Python 3.11.18
    ..................                                                       [100%]
    18 passed in 846.58s (0:14:06)
    V4 exit=0
    ./script.sh:53: command not found: uvx
    STOPPED at line 53 (exit 127)

V5, run afterwards by hand on beast-3 with the script's uv 0.10.10 binary:

    gnd 0.3.0

## Adversarial review

One reviewer is one reviewer: Codex (gpt-6.1-sol, xhigh, read-only) over
`f9f502d9..b8afdaa6 -- tests`, disposition `revise`, 7 findings
([retained output](notes/phase-RN2-codex-review.md)); dispositions in the
spec §13. Six were applied before the merge; G5 (installing a wheel resolves
its dependencies from the index) is accepted as a limit. The reviewer
confirmed all eight fixture digests, the proposal file's bytes against the
harness, the answer-key values, and that each probe's control catches the
broken implementation it describes, with the two exceptions it reported (G3,
G4, since tightened). The tightened tests were not re-reviewed. Part two (the
build and the run) is commands and their output; it was not reviewed.

## Refactoring review

None needed, argued from what the phase touched: it added tests and inputs to
one test file and built files from an existing recipe. The acceptance file is
now about 640 lines with two generations of probes (0.1.0 to 0.2.0, 0.2.0 to
0.3.0). **Deferred, with a target:** at the next release, decide whether the
oldest generation's control (the 0.1.0 download) is retired; this phase kept
it (D4).

## Boundary -- what this phase does NOT establish

- **One profile is observed:** macOS 27.0.1 arm64, Python 3.11.18, uv
  0.10.10 (beast-3), plus a trial on macOS 26.6.2 with Python 3.14. Ubuntu,
  Windows and other Python versions are not observed for 0.3.0 (RN-D6).
- **The candidate's evidence is not the published file's evidence.** Nothing
  is published; the served-file comparison after an upload is the identity
  that counts.
- The opt-in Ossie oracle lane did not run (owner ruling): the pinned upstream
  validator and parser have not seen the exporter since RN0's edits. RN0's
  byte comparison over the census and probe Q1 are the evidence in its place.
- The 0.3.0 version was free at 15:08:14Z on 2026-11-11; that says nothing
  about a later day.
- The tests need the package index: for each wheel's dependencies and for the
  0.1.0 and 0.2.0 control wheels (hash-checked).
- The identity probe shows consistency and sensitivity to two changes; it
  pins no independently derived digest.
- The full default lane was not rerun in this phase; no file it selects
  changed since RN1's clean lane at `d78e576c`.
- One reviewer is one reviewer; part two was not reviewed.

## Open questions

- RN3: the dossier, the post-publication patches (pins, `RELEASED`, the notes
  date, compatibility, a support row for this profile) and the owner's
  publication actions.
- The Ossie import report's schema name and the `ossie-import` rule names are
  not in the format reference (review G7).
- Carried: the fixtures-refactor issue (RN-D7) is not filed; redaction and
  Ossie export is undecided.

## Refuted premises

- The beast-3 script was expected to end `passed`. Its added V5 step called
  a command that was not on its PATH.
- The first version of the carries test was expected to fail on 0.2.0 at the
  version check; it failed earlier, on a missing packaged example, until the
  check was moved first.
