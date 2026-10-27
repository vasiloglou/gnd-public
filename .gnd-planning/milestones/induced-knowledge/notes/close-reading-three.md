# Close reading three: evidence, honesty and privacy

Subject: branch `claude/ik-milestone-close`, diff `6f07035..HEAD` (HEAD `85880f5`), 368 files.
Paths: `<repo>` is the worktree root, `<scratch>` is my readers directory. The repository was not modified
(`git status` shows only the two pre-existing untracked entries). All scratch walks ran under `<scratch>/walk*`
with `<repo>/.venv/bin/gnd`.

## Check 1. Evidence bindings (path + sha256 in record front matter)

Method: `<scratch>/bind.py` parses each record's front matter, recomputes SHA-256 at HEAD, and for every mismatch
searches the path's history for the bound bytes, tests whether the bytes matched at the record's own commit, and
lists the later commits that touched the path.

| Record | Pairs | Match at HEAD | Mismatch | Mismatches explained by a later commit | Bound bytes equal the file at the record's commit |
|---|---|---|---|---|---|
| 001 plan gate (table, 2 digests) | 2 | plan r4 `8afbdcbd` matches HEAD; IK1 spec r4 `3076680b` = spec at `0f339ea` (gate edits after) | 0 | n/a | yes |
| 002 IK1 | 31 | 20 | 11 | 11/11 (IK2, IK1-Q1, IK4-Q2, IK5, IK6, close commits) | 11/11 |
| 003 IK2 | 40 | 28 | 12 | 12/12 | 12/12 |
| 004 amendment IK1-Q1 | 0 | n/a | n/a | n/a | n/a (binds nothing; see F3) |
| 005 IK4 | 42 | 25 | 17 | 17/17 (IK3, IK5, IK6, close) | 17/17 at the record's last commit `bae3526`; 4 of them differ from its first commit `a3bf9a2` because the record was itself updated in `bae3526` (consistent) |
| 006 IK3 | 10 | 10 | 0 | n/a | yes |
| 007 IK5 | 13 | 13 | 0 | n/a | yes |
| 008 amendment IK5-Q1 | 0 | n/a | n/a | n/a | n/a (see F3) |
| 009 IK4-Q2 | 5 | 5 | 0 | n/a | yes |
| 010 IK6 | 7 | 7 | 0 | n/a | yes |

Result: 150 digests, 40 stale at HEAD, every one explained by a later commit and every one equal to the bytes at the
record's own commit. No record claims current-ness ("current" appears only in evolve-domain prose). No finding.

## Check 2. Gate honesty (claimed output vs retained evidence)

| Record | Claimed output | Retained in | Verbatim? | File-count claim |
|---|---|---|---|---|
| 002 IK1 | 2309 passed, 55 deselected in 404.89s | evidence/IK1/final-gate.txt:61 | yes; lint "All checks passed!" also present | 56 files: 56 `tests/` lines in the file |
| 003 IK2 | 4003 passed, 61 deselected, 1 warning in 386.80s | evidence/IK2/final-gate.txt | yes; warning named, earlier red run also retained | 90: gate-files.txt has 90 lines |
| 004 IK1-Q1 | 4009 passed, 61 deselected, 1 warning in 396.49s | **no evidence file contains it** | not verifiable | F3 |
| README IK2 repair | 4366 passed | evidence/IK2-repair/final-gate.txt | yes | 108 lines |
| 005 IK4 | 1 failed, 6640 passed, 234 deselected, 1 warning in 571.72s, exit 1 | evidence/IK4/final-gate.txt | yes; the failing node and its main-also-fails note are retained | 166 lines |
| 006 IK3 | 4360 passed, 66 deselected, 1 warning in 736.13s | evidence/IK3/final-gate.txt | yes | 120 lines |
| 007 IK5 | 4473 passed, 105 deselected in 585.85s | evidence/IK5/final-gate.txt | yes | 94 lines, every file exists |
| 007 IK5 | 17 mutants killed; corpus red 41 failed, 2 passed | evidence/IK5/mutants.txt (17 KILLED lines), corpus-red.txt | yes | |
| 008 IK5-Q1 | 210 passed, 16 deselected in 63.05s | **no evidence file contains it** | not verifiable | F3 |
| 009 IK4-Q2 | 3162 passed, 39 deselected in 264.10s | evidence/IK4-Q2/final-gate.txt:46 | yes | |
| 010 IK6 | 2990 passed, 36 deselected in 257.34s; zensical no issues; 11416 links | evidence/IK6/final-gate.txt | yes, all three | |

## Check 3. Sanitization of the diff

Method: added lines of `git diff 6f07035..HEAD` scanned for `/Users/`, `/private/`, `/home/`, `/var/folders`, `/tmp/`,
drive-letter paths, the owner's username, the owner's email domain and any email address; then the same patterns over
every file the diff touches. Commit messages of the range also scanned.

| Hit | File(s) | Kind | Verdict |
|---|---|---|---|
| macOS per-user temp dir plus a truncated `pytest-of-<username>` | evidence/IK4-Q2/regressions-red.txt:4 | real host path + username | **leak (F1)** |
| full home-directory worktree path, and a scratch path embedding the home-dir name and session id | evidence/IK5/review-brief.md:2, :23 | real host path + username | **leak (F1)** |
| scratch path embedding the home-dir name and session id | notes/phase-IK2-agent-review.md:34, phase-IK3-agent-review.md:49, phase-IK4-agent-review.md:42, phase-IK5-agent-review.md:18 | real host path + username | **leak (F1)** |
| `/private/tmp/claude-501/<session>/...` | notes/phase-IK1-agent-review.md:41 | host temp root with UID, no username | hardening (F1b) |
| `/home/user/x.json`, `C:\data\x.json`, `/home/alice/secret.csv` | IK2 corpus builder and cases.json, IK2 review | synthetic hostile inputs | fine |
| path-pattern samples | tests/test_ik6_walk.py, tests/test_rf1_pin_harness.py | test literals | fine |
| `/private/tmp/gnd-local-ci-...` | tests/test_development_scaffold.py | pre-existing, not in this diff | out of scope |
| email addresses in added lines | none (only `@pytest` decorators) | | fine |
| commit messages in range | 0 username/host-path hits | | fine |

Total: 7 added lines in 6 files carry the owner's username inside a host path. All six files are bound by digest in
records 003, 005, 006, 007 and 009. The same class of leak exists in older milestones' evidence (pre-existing, outside
this diff).

## Check 4. IK-R10 / IK-R11

| Item | Result |
|---|---|
| Refunds example data | synthetic (store-named batch ids, `c-dev`-style customers, small integers) |
| Discover induction blocks (scratch walk) | examples are `ft0#0`-style opaque ids; evidence ref `south.yaml` + digest; no values, no paths |
| Learned proposal induction block | examples are batch ids (`harbor`...); refs relative (`ilp/export.json`) + digests |
| All 11 walk outputs | no absolute path, no scratch dir (grep) |
| Loader refusal of an absolute evidence ref | `/home/u/x.json` as `ref` -> exit 3, `jsonschema:pattern` (reproduced) |
| Loader refusal of a raw value as example id | **not refused**: `555-12-3456` as an example id validates exit 0 (shape-only by design; F5) |
| Downstream names: test hashes | the two DOWNSTREAM digests in tests/test_ik6_walk.py are the lowercase hyphen-joined forms of the two downstream names (verified locally without printing them) |
| Downstream names: whole diff, any case, separators none/space/`_`/`-`/`.`/`/` | **0 hits** in added lines; 0 in commit messages; 0 for the second word alone |
| Token check blind spots | simulated with a placeholder `foo-bar`: catches `foo-bar`, `FOO-BAR`, `(foo-bar)`, `foo-bar/x`; misses `Foo Bar`, `foo_bar`, `FooBar`, `foo.bar`, `foo-bar-repo`, `my-foo-bar`, en-dash form (F4) |
| Token check scope | only `src/gnd/examples/refunds/**` and the two learn-rules pages; release notes, reference pages, records, notes, evidence, fixtures are unscanned (F4) |
| Targeted test nodes | `test_t3_no_downstream_name_in_the_example_or_its_pages`, `test_t3_the_path_patterns_match_real_paths`: 2 passed |

## Check 5. Claims match bytes (17 spot checks)

| # | Claim (source) | Command | Result |
|---|---|---|---|
| 1 | `gnd validate` prints OK on the copied example (how-to) | copy + validate | match |
| 2 | measure: `fired_on_negative=2/4 ... unchecked=0/8` (how-to) | `gnd measure ... \| grep fired_on` | byte match |
| 3 | stand-in "searched 40 rules; 4 hold..." and the learned clause line (how-to, tutorial "40 simple rules") | stand_in_learner.py | match |
| 4 | import: `IMPORTED 1 ...`, `covers 4 (support 4/4)` exit 0 (how-to) | gnd import ilp-rules | match |
| 5 | overstated claim exits 3, writes no proposal, stderr text (how-to) | faulty import | exit 3, text match, no faulty.proposal.json |
| 6 | discover `EMITTED 10`, `SUPPRESSED declared=1 spanning-uniqueness=3` (how-to) | gnd discover | match |
| 7 | 10 rules = 5 sensible + 2 accidents + 3 file-shape, with the named rules (tutorial table) | read discover-report.json | match (2 uniqueness + 3 mandatory-on-refund; uniqueness on customer and on amount; mandatory on customer/amount/channel) |
| 8 | both previews `breaking: false` (how-to) | gnd evolve preview x2 | match |
| 9 | verbalization `[from induced, proposed; modality=deontic] ... at most 500.` (how-to) | apply + grep | match |
| 10 | market gets a warning on refund 601 for 750 (how-to, tutorial) | gnd check market | match |
| 11 | batch amounts table (tutorial lines 68-75), written rule 1000, north's max 120 | read batches, model | match |
| 12 | every walk-written file equals the IK6 goldens (010, test T2) | sha256 of 11 scratch files vs goldens.json | 11/11 match |
| 13 | seventh provenance source `induced` (release notes) | schema enum | 7 sources, `induced` last |
| 14 | induced enters only proposed/deontic through `gnd evolve` (release notes) | alethic induced proposal | `EVOLUTION PREVIEW REFUSED (3): new induced constraints must be proposed/deontic (D-12)` - match; hand-edit path see F6 |
| 15 | IK1-Q1: level 64 ok, level 65 exit 3 `jsonschema:maxDepth` (004) | nested YAML descriptions | match |
| 16 | IK5-Q1: `MAX_FACTS` and schema `facts.maxItems` 500,000; docs and test say 500000/500006 (008) | grep + schema read | match |
| 17 | corpus sizes: IK2 89 (loader 72 + admission 17), D-12 27 rows, IK3 32, IK4 20, IK6 goldens 11 | read fixtures | match; IK5 see F7 |
| 18 | "No learner ships with GND" (release notes) | `git ls-files src/gnd/examples/refunds`; evidence/IK6/installed.txt | **false as written**: a learner script ships inside the package and runs from the installed wheel (F2) |
| 19 | `gnd measure`, `discover`, `export`, `import` exist (release notes) | `gnd --help` | present |

## Findings

**F1. Blocking: host paths with the owner's username in retained evidence and notes.**
Claim: IK-R11 spirit and the milestone's sanitization rule; other evidence (e.g. evidence/IK6/installed.txt) already
uses `<scratch>`. Reproduction: `git diff 6f07035..HEAD | grep '^+' | grep -iE '<username>|/Users/|/private/var'`
gives 7 lines in evidence/IK4-Q2/regressions-red.txt, evidence/IK5/review-brief.md (2), notes/phase-IK2-, IK3-, IK4-,
IK5-agent-review.md. Disposition: replace with `<repo>`, `<scratch>`, `<tmp>`; because records 003/005/006/007/009 bind
these bytes, record the sanitization in the close record as an old-to-new digest table (the records keep describing
their own bytes). Note that the original bytes remain in the branch's commit history; a merge commit keeps them
reachable, so the owner should decide whether that is acceptable. Add a guard test that scans
`.gnd-planning/milestones/induced-knowledge/**` for home and temp-root paths.
F1b (hardening): notes/phase-IK1-agent-review.md:41 keeps `/private/tmp/claude-501/<session>` (UID, no username);
normalize with the rest.

**F2. Blocking (wording, low severity): "No learner ships with GND" (docs/release-notes.md, Unreleased: induced
knowledge).** `src/gnd/examples/refunds/stand_in_learner.py` is tracked under the package, the how-to copies it from
`gnd.__file__`, and evidence/IK6/installed.txt shows that page passing from an installed wheel. The how-to's own phrase
("the example's stand-in rule learner (not a GND command)") is accurate. Disposition: e.g. "No rule learner ships as a
GND command; the refunds example includes a small stand-in learner, and no real learner has been run in its tests."
The owner may reclassify as hardening.

**F3. Hardening: two amendment gates have no retained evidence.** 004 claims "4009 passed, 61 deselected, 1 warning in
396.49s"; 008 claims "210 passed, 16 deselected in 63.05s". `grep -rF` over evidence/ finds neither, and both records
bind no files (0 digest pairs). Not shown false, only unverifiable. Disposition: say "not retained" in the close record,
or rerun and retain under the current bytes, labelled as a re-run.

**F4. Hardening: the downstream-name check is narrow.** tests/test_ik6_walk.py scans only the example and the two
learn-rules pages, and its token regex lowercases but keeps `-`/`_` inside the token, so it misses space, underscore,
dot, CamelCase, en-dash and affixed forms (simulated with a placeholder). The current diff is clean under all of those
forms (my scan: 0 hits, commit messages 0). Disposition: normalize to `[a-z0-9]` runs and test concatenations, and widen
the scan to docs/, the release notes, the milestone directory and tests/fixtures.

**F5. Hardening (residual): IK-R11 raw values are checked by shape only.** `induction_example_id` is
`^[A-Za-z0-9][A-Za-z0-9._:#-]{0,63}$`; an SSN-shaped string as an example id validates exit 0. The schema description
admits "checks its shape and arithmetic, not its truth". Disposition: record as a named residual in the close record
if not already listed.

**F6. Completeness: the "only as proposed and advisory" claim is scoped to evolve.** A hand-edited
`source: induced, status: proposed, modality: alethic` constraint validates exit 0 with a `semantic:modality-policy`
WARNING, and `gnd check` then reports it BLOCKING (exit 1 on the market week). Evolve refuses it (reproduced). The release
note sentence is true as written ("through `gnd evolve`"); consider stating that the loader only warns.

**F7. Completeness: IK5 record says "the approved 43-case corpus" (007:12) and "the 40-case corpus" (007:248).**
cases.json has 40 cases; corpus-red has 43 tests (41 failed, 2 passed). Both true of different things; align wording
("40 cases, 43 corpus tests").

## What I did not check

- The full or slow suites (forbidden while the gate runs); only two targeted nodes ran.
- Whether gate numbers were true when produced (only that the retained text contains them).
- Pre-milestone files and other milestones' evidence beyond noting the same leak class exists there.
- Binary files in the diff, images in docs (e.g. figure SVG/PNG metadata) for embedded paths.
- GitHub-side text (PR bodies, issue comments, branch names) for downstream names.
- Correctness of the reference pages (discover.md, measure-labels.md, ilp-bridge.md) beyond the bounds in check 5.
- The close spec's own records (no 011 record exists yet at HEAD).
