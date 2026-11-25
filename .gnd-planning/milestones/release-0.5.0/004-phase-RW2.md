---
milestone: release-0.5.0
station: "phase-RW2"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RW2
date: 2026-11-25
candidate_commit: 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7
gates:
  - command: "ruling: owner merged pull request 283 (the probes) on the words 'Merge 283', 2026-11-25; main 85d076ba"
    exit: "n/a -- ruling"
  - command: "ruling: owner said 'go ahead with the builds when the lane is clean', 2026-11-25"
    exit: "n/a -- ruling"
    output: "the builds were already covered by the delegated spec ruling; this is the owner's own word for them"
  - command: "bash e1-shards.sh 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 base (beast-3, six default-lane shards, clean clone)"
    exit: "0, 0, 0, 0, 0, 1"
    output: "22,020 passed, 0 failed, 2 errors, 13 skipped"
    note: "T6, RW2-C0. Shard 5's exit is the two RC-02 setup errors of tests/test_public_optional.py"
  - command: "bash build.sh WORKTREE 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 <home>/gnd-release/0.5.0/85d076ba/candidate PYTHON3.11 (planning machine)"
    exit: 0
    output: "wheel c843909e...0d49, sdist 9576a57d...a8c0, comparison wheel c843909e...0d49"
  - command: "bash accept-beast3.sh SCRATCH 85d076ba384e67b1f992cfd6b9a596ca01b3d4e7 (beast-3): verify the copied bundle, independent build, diff of SHA256SUMS"
    exit: 0
    output: "Independent wheel, sdist and comparison wheel match the retained SHA256SUMS."
    note: "T7, RW2-C2 and the first half of RW2-C3"
  - command: "GND_CANDIDATE_DIR=<home>/gnd-release/0.5.0/85d076ba/candidate uv run --no-sync pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short (beast-3, inside accept-beast3.sh)"
    exit: 0
    output: "33 passed in 1327.51s (0:22:07)"
    note: "T8, RW2-C3 and C4. Python 3.11.18, uv 0.10.10, macOS 27.0.1 arm64; the release wheel and the comparison wheel"
  - command: "uvx --python PYTHON3.11 --from <retained release wheel> gnd --version (beast-3, in scratch outside the checkout)"
    exit: 0
    output: "gnd 0.5.0"
    note: "T9, RW2-C5"
  - command: "uv run pytest -q -m pyrel_oracle tests/test_rp5_literature_rules.py tests/test_rp4_role_value.py tests/test_rp3_number.py tests/test_rp1_external_uniqueness.py tests/test_rp2_anchored.py tests/test_pyrel_rules.py tests/test_pyrel_rules_families.py tests/test_pyrel_rules_derivations.py tests/test_pyrel_rules_plans.py --tb=short -p no:cacheprovider"
    exit: 0
    output: "345 passed, 156 deselected in 397.32s (0:06:37)"
    note: "T10, RW2-C7, opt-in lane on the owner's selection of 2026-11-23; at 85d076ba on the planning machine"
  - command: "GND_OSSIE_ORACLE_ROOT=<scratch> uv run pytest -q -m ossie_oracle tests/test_ossie_external_oracle.py -k 'not consumer' -p no:cacheprovider"
    exit: 0
    output: "91 passed, 1 deselected in 45.30s"
    note: "spec D4, opt-in lane on the owner's selection of 2026-11-25; at 85d076ba on the planning machine. The consumer test was not run"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "not run"
  reason: "not selected. The two oracle lanes above are the only opt-in lanes that ran"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md
    sha256: 56e922ff35d7866a5a31c74cd42324dc6ed0f1b3b496e23dc0ab78fe46962772
  - path: .gnd-planning/milestones/release-0.5.0/003-RW2-pre-freeze.md
    sha256: f9729e4dd9f7ecc975173416d2bf7dd4f17e626ddd7bc02451b6190b6cd74818
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/freeze-summary.md
    sha256: 59b616195cc2d509d8605d34dd077a02bcb9b93c9200be4e0cb728af3f892a6c
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/build.sh
    sha256: 14c9a22bc2ac2f557f5ed6a82b788ff83dcd0be644dfb55131aa2e9ea4a3ea8f
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/build-summary.txt
    sha256: 8f380bb955c11a2db781009230a10d695fa886771a53c719d8d2db23a271cc46
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/accept-beast3.sh
    sha256: 398928f2f06d76f82acf270b5efb3ce3a9d5b4d85937a60ee4c82862ccc30f65
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/acceptance-summary.txt
    sha256: cc8830b238090b701005c940d217aac4e3b172a5d967f4fb59f0904dce741054
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/candidate/SHA256SUMS
    sha256: fefaef011502c8b9e921fe84ba34538c1330dbda2817b4f08b334dfe82d12b64
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/candidate/SOURCE_COMMIT
    sha256: 591576597381bb346c65ddbe612552ee92f49207f5b69ae298809286f4dfe64a
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/candidate/BUILD_PROFILE
    sha256: 4a9a76eb7f68802a0a7e4043b76f417ffc051b80bbcf489bd442daf842ef34a7
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW1/e1-shards.sh
    sha256: 7b9e7634d1b518c585876078664f5f5d19d84ad8247d4b8006d05c640b286ff4
  - path: tests/test_release_acceptance.py
    sha256: 5a1b4056389b8465091e96b3c193be6cff5bd53403510e42b908283541db5984
    note: "the bytes at 85d076ba, which ran"
  - path: "get_nick_done-0.5.0-py3-none-any.whl (retained outside the repository, on the planning machine and beast-3)"
    sha256: c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49
    note: "the declared exception: a release file is not committed. SHA256SUMS above lists it"
  - path: "get_nick_done-0.5.0.tar.gz (retained outside the repository, on the planning machine and beast-3)"
    sha256: 9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0
    note: "the declared exception, as above"
---

# Claim

On beast-3, with Python 3.11.18 and uv 0.10.10, at main `85d076ba`:
`tests/test_release_acceptance.py` exited 0 over the retained 0.5.0
candidate with 33 passed, for the release wheel and the comparison wheel; an
independent build of the same commit produced the same three SHA-256
digests; and `uvx --from <retained wheel> gnd --version` printed `gnd 0.5.0`.
The six-shard default lane at that commit reported 22,020 passed, no failure
and the two RC-02 setup errors. Nothing was uploaded, tagged or released.

## The candidate

| | |
|---|---|
| Source commit | `85d076ba384e67b1f992cfd6b9a596ca01b3d4e7`, main after the owner merged pull request 283 |
| Wheel | `get_nick_done-0.5.0-py3-none-any.whl`, SHA-256 `c843909e6f5f676b19f06522b0e9dffe89b84421e1f7bd5610ee0494b32b0d49` |
| Sdist | `get_nick_done-0.5.0.tar.gz`, SHA-256 `9576a57d735d54aa7cd565b52670f11feb6bf659dd75da40a868942168e8a8c0` |
| Comparison wheel, built from the sdist | the wheel's digest |
| Retained at | `~/gnd-release/0.5.0/85d076ba/candidate/` on the planning machine and on beast-3; `independent/` beside it on beast-3 |
| First build | the planning machine: macOS 26.6.2 arm64, Python 3.11.15, uv 0.10.10 |
| Second build and acceptance | beast-3: macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10 |

The retained [SHA256SUMS](evidence/RW2/candidate/SHA256SUMS),
`SOURCE_COMMIT` and `BUILD_PROFILE` are committed. The files themselves are
not: a rebuild makes a new candidate, and these are the ones acceptance read.

## Spec obligations

| Row | Result |
|---|---|
| RW2-C0 | [freeze-summary.md](evidence/RW2/freeze-summary.md): the notes cover the commit with no row added; 0.5.0 was free on PyPI minutes before the first build; the lane has no failure. Main did not move between the merge and the builds |
| RW2-C1 | the probes reached main by pull request 283, merged by the owner |
| RW2-C2 | two builds of `85d076ba`, one per machine, with equal `SHA256SUMS` |
| RW2-C3 | the copied bundle passed `shasum -c` and its `SOURCE_COMMIT` was compared on beast-3 before the independent build and again before the acceptance run |
| RW2-C4 | probes P1 to P6 passed on both wheels, each with its candidate control and its control on the hash-checked 0.4.0 wheel from PyPI. The four 0.3.0 controls are gone ([pre-freeze record](003-RW2-pre-freeze.md)) |
| RW2-C5 | `gnd 0.5.0` |
| RW2-C6 | one profile observed: macOS 27.0.1 arm64, Python 3.11.18, uv 0.10.10. No other is claimed |
| RW2-C7 | `pyrel_oracle`: 345 passed at the freeze commit. The environment check found `relationalai` 1.30.1 and `duckdb` 1.5.5 |
| spec D4 | `ossie_oracle`: 91 passed, the consumer test deselected |
| installed families (D3) | all five added files passed from the installed wheel with reads of the source checkout denied; none was dropped |

## Gate output (verbatim)

    Shard 0 exit 0
    4344 passed, 49 deselected in 579.41s (0:09:39)
    Shard 1 exit 0
    2849 passed, 238 deselected in 619.25s (0:10:19)
    Shard 2 exit 0
    4204 passed, 219 deselected, 1 warning in 654.17s (0:10:54)
    Shard 3 exit 0
    3649 passed, 13 skipped, 104 deselected in 919.37s (0:15:19)
    Shard 4 exit 0
    3778 passed, 256 deselected in 500.77s (0:08:20)
    Shard 5 exit 1
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid
    3196 passed, 184 deselected, 2 errors in 651.16s (0:10:51)

    Independent wheel, sdist and comparison wheel match the retained SHA256SUMS.
    Python 3.11.18
    uv 0.10.10 (8c730aaad 2026-03-13)
    2026-11-25T16:48:43Z
    .................................                                        [100%]
    33 passed in 1327.51s (0:22:07)
    Installed acceptance exit 0.
    gnd 0.5.0
    2026-11-25T17:10:52Z

    345 passed, 156 deselected in 397.32s (0:06:37)
    91 passed, 1 deselected in 45.30s

The full outputs are in [freeze-summary.md](evidence/RW2/freeze-summary.md),
[build-summary.txt](evidence/RW2/build-summary.txt) and
[acceptance-summary.txt](evidence/RW2/acceptance-summary.txt).

## Review

The probes diff had two review rounds before the merge; they are in the
[pre-freeze record](003-RW2-pre-freeze.md). Nothing was reviewed after it:
this stage changed no tracked file but planning records, and its evidence is
the runs above.

## Refactoring review

None needed. After the probes pull request the phase ran scripts and wrote
records. The two scripts are RV2's with one scratch name and two version
strings changed; the diff is three lines.

## Open questions

- **The Ossie oracle root's origin.** It was found in another session's
  scratch folder, with both upstream repositories at the pinned commits, and
  the lane's `check_pins` accepted it. The session that ran the Ossie
  milestone is archived and was not asked whether it is the same root.
  Target: none needed unless the owner wants the root rebuilt from the
  receipt.
- **The scratch root is not durable.** A later run of `ossie_oracle` needs
  it rebuilt if the folder is cleared. Target: the owner, as maintenance.
- **For RW3's dossier, "what was not measured":** every "none" and "no
  probe" clause of the spec's coverage table; the consumer test of the Ossie
  oracle; any RelationalAI engine run; any profile other than the one above.
- Carried from the pre-freeze record: the `gnd flatten` file names against
  the notes' `<stem>`, and `markdown_blocks` splitting at U+2028.

## Boundary -- what this result did NOT establish

- That 0.5.0 installs or runs on any profile but macOS 27.0.1 arm64 with
  Python 3.11.18 and uv 0.10.10. The default lane ran on Python 3.13.18 with
  uv 0.13.7, on the same machine.
- That the files PyPI would serve are these files. Nothing was uploaded; the
  served-file comparison belongs to the publication stage.
- That a RelationalAI engine enforces an exported program, or that the
  RelationalAI consumer reads the Ossie files. Neither was run.
- That main still equals the candidate. A commit to main after `85d076ba`
  that changes a shipped file makes this candidate stale; RW3 checks it.
- The owner's reading of the spec. The owner ruled three of its decisions
  and merged its pull requests; the spec approval is delegated.
- Publication. The pins, `RELEASED`, the upload, the tag and the GitHub
  release are untouched, and each waits for the owner's request.
