# IK6 adversarial review (one reviewer)

One reviewer is one reviewer. A single general-purpose subagent reviewed
`git diff 705ad94` plus the untracked IK6 files on 2026-10-26, with no edit
rights. It could not write its findings file, so its report was returned as
text. It is kept below, verbatim apart from a shortened scratch path, followed
by the disposition of each finding. Its evidence files stayed in the session
scratchpad (`review-ik6/`).

## The reviewer's report (verbatim)

I found no blocking defects in IK6. The walk runs, all 11 written files match their goldens, and every number I checked on the tutorial, commands page, README and both SVGs matches a real run or the batch files. What I found is four hardening issues (H1–H4) and five completeness items (C1–C5).

**H1. T3's Windows path pattern never matches a real Windows path.** `tests/test_ik6_walk.py:80`: `r"[A-Za-z]:\\\\"` needs two backslashes after the drive letter. A plain `C:\Users\me` has one, so it is missed. `D:/work`, `/tmp/`, `/var/folders/`, `/opt/` and `~/` are not covered either.

**H2. T3's "opaque id" test cannot fail on the property the spec names.** Spec §8 T3 says the proposals' induction blocks carry opaque batch ids only. The test never opens `learned.proposal.json` or `discovered.json`. `covered <= ids` is true by construction. The path scans cover only the example tree and the two pages, not the files the walk writes. T2 swaps the run directory for `<run>` before hashing, so a run-directory path leaking into a proposal would end up in a regenerated golden unnoticed. The property does hold today.

**H3. The learner's `--also-claim` handling fails silently or prints a false message.** `stand_in_learner.py:83` only checks `sys.argv[3:4] == ["--also-claim"]`. `--also-claim=north` and `--also_claim north` are silently ignored. `--also-claim nort` (unknown batch) and `--also-claim harbor` (already covered) print `deliberate mistake: ...`, but the run record is unchanged, and `gnd import ilp-rules` then accepts it. A missing flag value or missing positional arguments gives an `IndexError` traceback. T8 only checks `covered[0] == "north"`, which holds because north happens to be first in the example order.

**H4. The census test never checks which phase changed a file.** Changing `gnd-solve/SKILL.md | IK4, IK5` to `| IK1` passes both tests. All 16 changed cells are correct today against `git log`. Minor: a reason containing `|` or a back-ticked path is reported as `missing:`. The abbreviated `6f07035` makes the test fail on a shallow clone.

**C1. No test checks the business tutorial's numbers.** After the page split (F1), `docs/tutorials/learn-rules.md` has no runnable blocks. The commands page would fail on an output change while the tutorial goes silently stale.

**C2. "Under 500" is false for south.** The alt text at `learn-rules.md:14` and the `<desc>` in `refunds-weeks.svg` say the clean weeks "stay under 500". South has a refund of exactly 500.

**C3. "Keeps the fewest" overstates the learner,** which does a greedy cover. Separately, the two-atom join space exists in code, but this model produces 0 join candidates, so that code is never run.

**C4. The release notes describe `induced` too narrowly.** `gnd discover` also emits `source: induced` from a single unlabelled population.

**C5. T7 evidence and uncommitted files are outstanding.** The installed-candidate `results.json` is not retained; README, census, tests, goldens and spec §14 are uncommitted; the nav label differs from the page title; spec §1 reads as stale.

**Note on goldens.** `measure.json`, `discover-report.json` and `discovered.json` embed GND version 0.1.0, so the T2 goldens will move on any version bump.

**Checked and sound:** T1 (all 10 blocks, step 6 exits 3); T2 detects a mutated `--requested-at`; all 11 golden digests match an independent `shasum`; the downstream-name hashes are correct; the build script reproduces the batches byte for byte; every batch value, all 21 SVG dots, the measure cells and the discover 10/1/3 counts match; the skill-edit sentences are true; the spec deviations are recorded in §14. 184 passed, 3 skipped across the IK6 and docs suites; 2698 passed and 2 failed in the controls (`test_rf1_session_pins.py::test_session_fresh[3]` and `test_session_resume[3]`, a `python` spawn `FileNotFoundError` under the test's minimal PATH, not attributed to IK6).

## Triage and disposition

| Finding | Reproduced | Class | Disposition |
|---|---|---|---|
| H1 | yes: the pattern needs two backslashes | hardening | fixed; regression `test_t3_the_path_patterns_match_real_paths` |
| H2 | yes: no test reads the written proposals | hardening | fixed: the walk asserts no written file holds the run directory before normalizing, and the learned proposal's induction examples are batch ids; regression `test_t3_the_walk_writes_no_run_directory` |
| H3 | yes: `review-ik6/argv-probe.out` | hardening | fixed: argparse; an unknown or already-covered batch is a usage error; regressions `test_h3_*`, and T8 checks the claimed set equals the true cover plus north |
| H4 | yes: `review-ik6/t4probe.out` | hardening | fixed: each changed cell must equal the phases in the file's commit subjects, plus IK6 for uncommitted edits; full base SHA; regression `test_t4_a_wrong_phase_fails_by_name` |
| C1 | yes | completeness, cheap | fixed: `test_c1_the_tutorial_numbers_match_the_commands_page` pins each tutorial number to the commands page output |
| C2 | yes: south has 500 | completeness, factual | fixed: "never go over 500"; pinned by C1's test |
| C3 | yes | completeness, factual | wording fixed ("a small set, chosen greedily"); the unexercised join space is recorded in the record's boundary |
| C4 | yes | completeness, factual | fixed: "found from data" |
| C5 | yes | completeness | T7 results retained under `evidence/IK6/`; everything committed with the record; nav label aligned; §1 is append-only, so the record states the status |
| goldens note | yes | accepted | the goldens move on a version bump; recorded in the record's boundary |
| rf1 session pins | not reproduced | n/a | passed in the phase gate (`evidence/IK6/final-gate.txt`); the reviewer's sandbox PATH |
