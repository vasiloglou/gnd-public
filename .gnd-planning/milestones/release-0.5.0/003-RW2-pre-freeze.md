---
milestone: release-0.5.0
station: "phase-RW2, before the freeze"
skill: "n/a -- repository development, not a gnd-solve station over a domain model"
scope: phase-RW2
date: 2026-11-25
implementation_commit: 9f853be4
gates:
  - command: "ruling: owner merged pull request 282 (RW1) on the words 'Merge 282', 2026-11-25; main 8dcfe0e7"
    exit: "n/a -- ruling"
  - command: "ruling: owner chose D2 'Ossie, growth, host', D4 'Yes, run it' and D6 'Leave as written', among the readings of spec section 7, 2026-11-25"
    exit: "n/a -- ruling"
    output: "the owner chose among short descriptions; the owner has not read the spec"
  - command: "ruling: delegated (auto=true) approved .gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md sha256 db60428a4e85883791651c63d9e16bd293cc97a6054232f5b52b6f396bc9c024"
    exit: "n/a -- ruling"
    output: "spec r1 approved for steps 2 to 7 (commit 3dacdba9); the probes pull request's merge and every act of publication stay with the owner"
  - command: "ruling: delegated (auto=true) amended .gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md sha256 56e922ff35d7866a5a31c74cd42324dc6ed0f1b3b496e23dc0ab78fe46962772"
    exit: "n/a -- ruling"
    output: "the review search stopped after round 2 as declared before it; the added-test-lines limit of section 10 raised from 350 to 420 for this pull request"
  - command: "python rehearse_probes.py WORKTREE SCRATCH (the five new probe functions; editable 0.5.0 tree, hash-checked published 0.4.0 wheel, empty sandbox prefix)"
    exit: 0
    output: "5 passed, failures: 0"
    note: "rerun after each of the two repairs with the same result. A rehearsal, not acceptance"
  - command: "python rehearse_probes.py WORKTREE SCRATCH --swap (0.4.0 in the candidate's place)"
    exit: 0
    output: "failures: 5"
    note: "the control: every probe fails on 0.4.0"
  - command: "python -I rehearse_families.py tests/FILE, for the five added families files, from an archive checkout in a Python 3.11 environment with the editable tree, pytest 9.1.1 and duckdb 1.5.5"
    exit: 0
    output: "46, 40, 98, 30 and 22 passed; no skip"
  - command: "uv run pytest -q --collect-only -o addopts='' tests/test_release_acceptance.py"
    exit: 0
    output: "33 tests collected"
    note: "selection only"
  - command: "uv run pytest -q tests/test_acceptance_controls.py tests/test_release_version.py tests/test_release_docs.py tests/test_release_text.py tests/test_ossie_docs.py tests/test_il6_walk.py tests/test_ir1_judgments_includes.py tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_rp5_literature_rules.py tests/test_ossie_relational.py tests/test_vg5_seeded_growth_example.py tests/test_count_certificates.py tests/test_vg3_unattended_includes.py tests/test_go2_operation_outcomes.py tests/test_lh1_reading_host.py tests/test_lh2_reading_replay.py tests/test_lr3_reference_set.py tests/test_pull_request_policy.py --tb=line -p no:cacheprovider"
    exit: 0
    output: "739 passed, 56 deselected in 179.32s (0:02:59)"
  - command: "the project.md structure and inventory guard block (16 files)"
    exit: 1
    output: "1 failed, 865 passed, 2 deselected in 124.17s (0:02:04)"
    note: "the one failure, tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap, comes from an untracked skill mirror in this checkout; it passes in a clean clone (RW1 record)"
  - command: "uv run ruff check"
    exit: 0
    output: "All checks passed!"
  - command: "python3 scripts/components_index.py changed --base origin/main --strict"
    exit: 0
    output: "changed against origin/main (8dcfe0e): 48 file(s) differ; 0 to fix, 0 warning(s), 0 to reread"
  - command: "uv run --group docs zensical build --strict"
    exit: 0
    output: "No issues found"
  - command: "uv run python tools/check_docs.py site"
    exit: 0
    output: "19539 local links/assets/anchors checked"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1 --wait"
    exit: 0
    output: "codex, effort high, read-only: 1 finding, VERDICT: CHANGES_REQUESTED"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py run .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2 --wait"
    exit: 0
    output: "codex, effort high, read-only: 3 findings, VERDICT: CHANGES_REQUESTED"
  - command: "python3 .claude/skills/process-phase/scripts/review_tool.py status (both rounds)"
    exit: 1
    output: "both rounds done, ledgers complete; unreviewed: tests/test_release_acceptance.py, tests/test_acceptance_controls.py and the spec, changed after round 2 read them"
slow_cadence:
  command: "uv run pytest -q -m \"evidence or census\""
  trigger: "not run"
  reason: "not selected. pyrel_oracle and ossie_oracle run at the freeze commit, on the owner's selections of 2026-11-23 and 2026-11-25"
evidence:
  - path: .gnd-planning/milestones/release-0.5.0/notes/phase-RW2-spec.md
    sha256: 56e922ff35d7866a5a31c74cd42324dc6ed0f1b3b496e23dc0ab78fe46962772
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/controls-0.4.0.md
    sha256: db37a9144234705191a2db4309c19f3397814d9374a1da3542008b7d9e2e39c5
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/probes-rehearsal.md
    sha256: ea86cb5289a3417099c6f86503bc014d2089fa7de9417b72b4553bf2426a2a0d
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse.py
    sha256: 8e05cde2819fb9e2308d90db35274f7db5e2baf2c4056affa4b547970f956105
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse-p3.sh
    sha256: ba585932b1e56964f92ff428e45c358ea56ccad78881ad6ffb56802740bc8317
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_probes.py
    sha256: 3783db17e2f4613d954befd972b49d140952a9a9230a592ab1ced8f560d9db00
  - path: .gnd-planning/milestones/release-0.5.0/evidence/RW2/rehearse_families.py
    sha256: 2dd669bba9602610e1aa8c83aa73e85412eb0fbc58555a3bb6896b2d231d448e
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/review.md
    sha256: 829780f97398183ccb3c538f4d18b6c046d8e2411da61f7ba11f77d59dc992bc
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/run.json
    sha256: de465725f9787a93f874d3a4fcedcbf622b85549c5ae288cfa6a84f2fe3aba26
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r1/FINDINGS.md
    sha256: 30fba95dfbc5870f9c3db07e52ee79ea4f92bc72d7fedd7578430b304148c3ed
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/review.md
    sha256: 239246d0e0c1cf0b9571a0c9e81af858c52d73653909cca95e2d76ecd2f91e2a
    note: "sanitized; run.json binds the original"
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/run.json
    sha256: 5fe1ef9182f9f8931a6d92328c3d1fe74d70e62b80524330240058efafd2a420
  - path: .gnd-planning/milestones/release-0.5.0/notes/reviews/phase-RW2-probes-r2/FINDINGS.md
    sha256: d74eb03171fbfab078bb50f8b1b565866670ac2cc632b460defd8c633126489b
  - path: tests/test_release_acceptance.py
    sha256: 5a1b4056389b8465091e96b3c193be6cff5bd53403510e42b908283541db5984
  - path: tests/test_acceptance_controls.py
    sha256: 45ff02eb2cace5951ecb8f56bb5e6692dfa1bf786c0ad2e951b158b567e5b2a3
  - path: docs/release-notes.md
    sha256: 7526c08e8ac8281e48d4b6cf8c138f9bb24aa6b4b833f834468c30a1254e1d25
---

# Claim

At `9f853be4` the five new probe functions of
`tests/test_release_acceptance.py` exited without failure in a rehearsal on
the editable 0.5.0 tree against the hash-checked published 0.4.0 wheel, and
each failed with 0.4.0 in the candidate's place; the focused gate reported
739 passed; `uv run ruff check`, the component-index check, the strict docs
build and the site link check exited 0. No candidate was built, and the
acceptance file has not run against one.

This record covers step 2 of the RW2 spec, the probes pull request. The
freeze, the two builds, the acceptance run and the oracle lanes follow its
merge and get the phase record.

## What the pull request changes

- **Six installed probes (M1).** Judging an include root, `gnd flatten`, the
  PyRel rules export, COUNT certificates, the Ossie relational files and the
  seeded growth example. Each has a control on the candidate and one on the
  published 0.4.0 wheel, with the results
  [measured on 0.4.0](evidence/RW2/controls-0.4.0.md) before the probes were
  written. P1, P2 and the include-root part of P3 share one test function
  and one interop folder, so the file has five new test functions.
- **Installed families.** Five test files join `FAMILIES`.
- **Retired.** The four 0.3.0 availability controls, the `published_0_3_0`
  fixture and the 0.3.0 wheel pin. Round 1 of the review compared the
  assertions before and after: no assertion about the candidate was removed.
- **Moved on.** The version guard requires 0.5.0; Q1 of the 0.3.0
  regressions expects five Ossie files.
- **Notes (M2, D5).** One sentence of the PyRel block: 0.4.0 refused each of
  the four model features by name, not the first three.
- **Controls in the default lane.** `tests/test_acceptance_controls.py`
  gains tests of the two helpers the probes add.

Size: 338 lines added to `tests/test_release_acceptance.py` and 40 removed,
59 added to `tests/test_acceptance_controls.py`, 3 notes lines changed. The
spec estimated about 230 and set a pause at 350; the amendment in the spec's
§7 says why 397 was accepted.

## Review

One reviewer in a different tool, Codex at effort high, read-only, through
the review helper. The round budget was written into the spec before round
2.

| Round | Seats | Per-seat counts | Self-inflicted / total | Blocking / total | Severity ceiling | Verdicts |
|---|---|---|---|---|---|---|
| r1, the probes diff | codex | 1 | 0 / 1 | 0 / 1 | medium | changes requested |
| r2, with the repair | codex | 3 | 3 / 3 | 0 / 3 | medium | changes requested |

- **r1 F1, reproduced, fixed.** `readme_commands` checked that each probed
  command was a substring of the packaged README, so a command given another
  executable or commented out still counted. It was rewritten to read the
  README's shell fences line by line.
- **r2 F1 to F3, reproduced, fixed at `9f853be4`.** Three inputs the
  line-by-line reader accepted: a `#` glued to a word, a here-document, and
  a Unicode line separator. The helper now reads no line as shell: one `sh`
  or `bash` block of the README must equal the probe's commands as text.
- **The stop.** All three round-2 findings attacked text round 1's repair
  wrote, so the search stopped as declared. The final helper carries no
  review opinion. Its instrument is code: ten README changes on each of two
  READMEs, including every input the two rounds named, are refused in the
  default lane.
- **What r1 checked and found true:** each probe row against the spec's
  table; that no assertion passes vacuously; that `program_constants` reads
  real exported programs in both rules modes and the default mode without
  running them; that the corrected notes sentence agrees with the 0.4.0
  measurements; that probe inputs come from the installed package, apart
  from the two tracked fixtures the spec names.
- **What neither round ran:** the acceptance file against a candidate, the
  published 0.4.0 controls, the installed families with the source denied.

## Gate output (verbatim)

    published 0.4.0: gnd 0.4.0
    candidate stand-in: gnd 0.5.0
    test_installed_rw2_include_roots: passed
    test_installed_rw2_pyrel_rules: passed
    test_installed_rw2_count_certificates: passed
    test_installed_rw2_ossie_relational: passed
    test_installed_rw2_seeded_growth: passed
    failures: 0

    failures: 5

    33 tests collected in 0.07s
    739 passed, 56 deselected in 179.32s (0:02:59)
    FAILED tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap
    1 failed, 865 passed, 2 deselected in 124.17s (0:02:04)
    All checks passed!
    changed against origin/main (8dcfe0e): 48 file(s) differ; 0 to fix, 0 warning(s), 0 to reread
    No issues found
    19539 local links/assets/anchors checked

## Refuted premises

- **"About 230 added test lines" (spec §10).** The probes came to 338 lines
  and the review's controls to 59. The estimate counted one function per
  probe at about 25 lines; the P3 table and the judgment-binding program are
  each longer than that.
- **"A probe ties its commands to the README by a substring check" (the
  first implementation).** Refuted twice by the review; see above.

## Refactoring review

Executed, one: `readme_commands` was reduced to a whole-block comparison
over the existing `markdown_blocks` reader, which removed its own line
reader. Nothing else was needed: the probes reuse the file's `gnd`,
`gnd_json`, `copy_packaged`, `run` and `published_wheel`, and add three
helpers with one use each of a kind the file lacked (`program_constants`,
`readme_commands`, `sha256_file`). No production code changed.

## Open questions

- **`gnd flatten` names its files after the whole file stem.** For
  `checking.orm.json` it writes `checking.orm.flat.orm.json`. The notes
  bullet and the command's help say `<stem>.flat.orm.json`, which a reader
  can take to mean `checking.flat.orm.json`. Not changed (spec D5): the
  bullet is the include-roots milestone's. Target: the owner.
- **`markdown_blocks` splits lines at U+2028** and other separators
  `str.splitlines` knows, where Markdown has only CR and LF. Found by review
  round 2. It is a shared test reader from another milestone and is not
  changed here. Target: the owner, as maintenance.
- **Whether each families file passes from an installed wheel with the
  source denied** is not known until the acceptance run. A file that cannot
  is dropped and named in the phase record (spec §6).

## Boundary -- what this result did NOT establish

- That the acceptance file passes on a candidate. No candidate exists.
- That the wheel carries what the probes need. The rehearsal used an
  editable install.
- Anything on Python 3.11 with uv 0.10.10 for the probe functions: the
  harness ran on the planning machine's interpreter.
- That the default lane is unchanged. The full lane runs at the freeze
  commit (RW2-C0); this pull request ran the focused files only.
- That the final `readme_commands` is right beyond its twenty controls. No
  reviewer read it.
- The owner's reading of the spec. The owner ruled three decisions from a
  short description of each choice; the rest is delegated.
