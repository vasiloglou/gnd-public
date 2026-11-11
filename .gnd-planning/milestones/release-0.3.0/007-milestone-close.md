---
milestone: release-0.3.0
station: milestone-close
skill: "n/a -- repository development under process-phase and start-milestone, auto=false, not a gnd-solve station over a domain model"
scope: milestone-close
date: 2026-11-11
source_base: 2490dd77
gates:
  - command: "e1-shards.sh close on beast-3: the default lane, six round-robin shards, at main 7d86dc35f5888c3adb1b7386962f88b184b4e31e"
    exit: "1 (the 2 known tests/test_public_optional.py errors only)"
    output: "19016 passed, 0 failed, 2 errors"
  - command: "git diff --stat 2490dd77 origin/main -- .github (origin/main 7d86dc35, 2026-11-11T15:41:04Z)"
    exit: 0
    output: "0 lines"
  - command: "gh api repos/vasiloglou/gnd-public/environments -q \"[.environments[].name]\""
    exit: 0
    output: "[\"github-pages\"]"
  - command: "gh run list --workflow release.yml --json databaseId -q length"
    exit: 0
    output: "0"
  - command: "gh release list"
    exit: 0
    output: "GND v0.3.0 (Latest, 2026-11-11T15:38:27Z), GND v0.2.0, GND v0.1.0"
  - command: "git ls-remote --tags origin"
    exit: 0
    output: "v0.1.0 75eda93f; v0.2.0 d84ad6d5, peeled 7c0f4d0e; v0.3.0 257a8bb3, peeled 4c07c0e6"
  - command: "GET https://pypi.org/simple/get-nick-done/ (JSON) and https://pypi.org/pypi/get-nick-done/0.3.0/json"
    exit: 0
    output: "versions 0.1.0, 0.2.0, 0.3.0, six files; 0.3.0 wheel 143890ee... and sdist 5e40d9e3..., yanked False"
  - command: "git diff --stat 4c07c0e6 origin/main -- src pyproject.toml uv.lock LICENSE NOTICE"
    exit: 0
    output: "0 lines: main's package inputs equal the published candidate's"
  - command: "gh pr list --state open --json number -q length"
    exit: 0
    output: "0"
  - command: "the read-only remote checks rerun for retention at 2026-11-11T16:17:58Z (evidence/close/remote-state-2026-11-11.txt), each with its own exit"
    exit: 0
    output: "same state as the entries above, except 1 open pull request: this close's own"
  - command: "codex exec --ephemeral --config model_reasoning_effort=\"xhigh\" --sandbox read-only --color never --skip-git-repo-check - (close review, prompt on stdin, over f15e0009)"
    exit: 0
    output: "DISPOSITION: revise; L1 to L8, all checked and applied (see Close review)"
  - command: "ruling: owner, close review instrument"
    exit: "n/a -- ruling"
    output: "\"One Codex reviewer\" (2026-11-11, in this session)"
slow_cadence:
  command: 'uv run pytest -q -m "evidence or census"'
  trigger: "explicit owner request"
  reason: "excluded for this milestone by the owner (RN-D11, 2026-11-10); not selected at this close"
evidence:
  - path: .gnd-planning/milestones/release-0.3.0/notes/release-0.3.0-plan.md
    sha256: 15b40656bca22f6fafcebe4f7c889ce52cc2415191aa4e9b5346f303eb9aaabb
  - path: .gnd-planning/milestones/release-0.3.0/001-plan-gate.md
    sha256: e51a3835d1593c951e7ff33a3498ad06dde2982e12cb0c420d7b0782eb7c4158
  - path: .gnd-planning/milestones/release-0.3.0/002-phase-RN0.md
    sha256: 5edc52eae76377f33522732231db41411d061cba98fecac3d04995a2a2f8f2e0
  - path: .gnd-planning/milestones/release-0.3.0/003-phase-RN1.md
    sha256: fb9a66e860c51ac76646aed515b4e5fbd73460fb4a03864b9ceabf5f1741e779
  - path: .gnd-planning/milestones/release-0.3.0/004-phase-RN2.md
    sha256: 635d482491a0d46ce85af6a11a994e8079487a0d2de7a2ad965299d064acc78c
  - path: .gnd-planning/milestones/release-0.3.0/005-phase-RN3.md
    sha256: d282de407d629ca5359db235911302b1cdd26c8a020822e4052bc479fc07c9cf
  - path: .gnd-planning/milestones/release-0.3.0/006-publication.md
    sha256: 3a58937d2af8a240c654a77194b87599e7c0550d5d3b13d4db56f87e96dff7f9
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN3/dossier.md
    sha256: a9293370a267d1d4fa437cf13851f8227e8b083f72a49850c0ecd6310086a332
  - path: .gnd-planning/milestones/release-0.3.0/evidence/publication/step-E-served-files.txt
    sha256: 034695116daccebb36cd42957d030f67475cfaa1d2ddc08dee2f1de3446f3104
  - path: .gnd-planning/milestones/release-0.3.0/evidence/close/lane-7d86dc35.txt
    sha256: 35362ee32c1d8cef75137487a8e5f2d9453db7cd4aa376c52aaa26fc28dc1a97
  - path: .gnd-planning/milestones/release-0.3.0/evidence/RN2/candidate/SHA256SUMS
  - path: .gnd-planning/milestones/release-0.3.0/evidence/close/remote-state-2026-11-11.txt
    sha256: 4ec86173548ad5a9921976fb4a306368fa5003482da031281fc79443bb5cd191
  - path: .gnd-planning/milestones/release-0.3.0/notes/close-codex-review.md
    sha256: 711eef7137982407f0ca097886efbaf36caec6f9f90913d02656c3145f5902f2
    sha256: c5a94218941a2745ddfae7b6925a8717dd9c73f5126d8a4da3fb124278cfa906
  - path: docs/release-notes.md
    sha256: f922334a5025974ce8e5913b601859d33e515a02516d7333a5dde5bbeaf66c30
  - path: docs/support.md
    sha256: ec29384cd510dd85dc2a3c047508cbd3f3f0d35713b666dde0e186a7faef6bf8
  - path: docs/installation.md
    sha256: ddfb29ced50ad96b55baa70d8b6b6069157ce66906943671861108ec3064e692
  - path: docs/compatibility.md
    sha256: 9f44d3d26391e79b10b8f54643d3423c6d43524f9f7b710420fad997326c50bb
  - path: README.md
    sha256: 368669d169fea78d6de4d012d2cc98db8b46e57f72004f88c061893bf86397c6
---

# Claim

**This is a draft; the owner has not ruled on it.** The close review (one
Codex reviewer, the owner's choice) is done and its findings are applied.

GND 0.3.0 is published and main is in its post-publication state. The four
phases (RN0 to RN3) are on main, each with an owner-approved spec, a record
with verbatim gate output, one independent reviewer and an owner-merged pull
request. The owner then asked for publication (RN-D13). The closing default
lane at main `7d86dc35` has no failure: 19,016 passed and the 2 known
`tests/test_public_optional.py` errors.

- PyPI received the retained `4c07c0e6` candidate on 2026-11-11 at 15:36:42Z;
  the served files are byte-identical to it.
- Tag `v0.3.0` (`257a8bb3`, pointing to `4c07c0e6`) and the GitHub release
  exist.
- The install pins, the notes and the support and compatibility pages state
  the published 0.3.0 (PR 167).

## Phases and the publication

| Step | Record | Gate | Review (one reviewer, Codex) | PR |
|---|---|---|---|---|
| plan gate | [001](001-plan-gate.md) | owner: "Approve r2" | `revise`, P1 to P9, all applied | 162 |
| RN0 repair main's lane | [002](002-phase-RN0.md) | 24 red guards to 0; lane at `326a1900` clean but for RN1's two tests | `revise`, K1, K2, fixed | 162 |
| RN1 candidate content | [003](003-phase-RN1.md) | lane at `d78e576c`: 19,016 passed, 2 known errors | `revise`, F1 to F7, fixed | 163 |
| RN2 build and acceptance | [004](004-phase-RN2.md) | acceptance on beast-3, Python 3.11: 18 passed; two builds identical | part-one tests only: `revise`, G1 to G7, six applied, one accepted. Part two, the build and the run, was not reviewed | 164, 165 |
| RN3 hand-over | [005](005-phase-RN3.md) | patched scratch tree: tests and check exit 0; 13 controls fail | `revise`, H1 to H9, fixed | 166 |
| publication | [006](006-publication.md) | served files equal the candidate; index install prints `gnd 0.3.0` | not reviewed | 167 |

## RN-D13: the owner's publication request

Recorded in [006](006-publication.md): "go on and also update pip", then "Yes,
upload it" and "Yes, try both". The session ran the upload, the tag and the
release on that request. No announcement was made.

## Completion predicates

| # | Predicate (plan) | Evidence | Holds |
|---|---|---|---|
| 1 | version written once; lock, manifests and notes agree; the drift test exits 0 | RN1; `tests/test_release_version.py` in the closing lane | yes |
| 2 | version-bearing files and moved tests inventoried and handled by the ruled method; opt-in lanes listed as exclusions | RN1 (E1, moved digests, 0 mismatches) | yes |
| 3 | one 0.3.0 notes section covering every user-visible change, Ossie included; no `Unreleased:` section for work in the candidate | RN1 with review F1 to F5; RN2 V1 | yes, with the limit below: completeness rests on one reviewer and an options audit |
| 4 | candidate installs outside the checkout and carries the RN-D9 items; 0.2.0 refuses them | RN2 (T1, T2) | yes |
| 5 | release acceptance exits 0 over the retained files | RN2 V4: 18 passed | yes |
| 6 | at the RN3 checkpoint: dossier written, patches prepared and not applied | RN3 | yes |
| 7 | no phase uploaded, tagged, released, created `pypi` or changed `.github` | the gates above: `.github` diff empty since `2490dd77`; environments `github-pages` only; 0 `release.yml` runs. The upload, tag and release are the publication stage's | the prohibition holds as written, read with plan §13 (proposed). The audit part is weaker than the plan asked: the baseline observations (plan N6; RN2's V8) and the first closing checks exist only as summaries in the records; one dated verbatim transcript is retained, taken at the close ([remote state](evidence/close/remote-state-2026-11-11.txt)). Repository settings and the PyPI publisher configuration are not audited |
| 8 | published; served files compared; index install exercised; the post-publication patch on main | 006; PR 167 merged as `7d86dc35` | yes |
| 9 | approved spec, verbatim gate and one reviewer per phase; every open question disposed | the records; the sweep below | pending this close's rulings |

## Gate output (verbatim)

The closing lane, from [lane-7d86dc35.txt](evidence/close/lane-7d86dc35.txt):

    close shard0: 3682 passed, 53 deselected in 459.44s (0:07:39) (shard exit=0)
    close shard1: 2940 passed, 152 deselected in 414.79s (0:06:54) (shard exit=0)
    close shard2: 2833 passed, 130 deselected in 321.22s (0:05:21) (shard exit=0)
    close shard3: 4083 passed, 92 deselected in 815.32s (0:13:35) (shard exit=0)
    close shard4: 2652 passed, 282 deselected in 251.24s (0:04:11) (shard exit=0)
    close shard5: 2826 passed, 145 deselected, 1 warning, 2 errors in 583.39s (0:09:43) (shard exit=1)
    ERROR tests/test_public_optional.py::test_base_wheel_refuses_missing_synth_extra_and_still_checks
    ERROR tests/test_public_optional.py::test_declared_synth_extra_is_seeded_and_loader_valid

The read-only remote checks are retained verbatim, each with its exit, in
[remote-state-2026-11-11.txt](evidence/close/remote-state-2026-11-11.txt).
They are a rerun at 16:17:58Z; the first run at 15:41:04Z was summarized in
this record's front matter and its output was not kept. The one difference:
the rerun counts 1 open pull request, this close's own.

Against the base lane of this milestone (E1, main `2490dd77`: 18,971 passed,
26 failed, 2 errors): the 26 failures are gone and no new one appears. The
range also holds no other milestone's merges; every commit since `2490dd77`
is this milestone's.

## Close review

The owner chose the instrument: "One Codex reviewer" (2026-11-11, in this
session). This replaces the plan's panel bar (§8) for the close, as at the
0.2.0 close.

One reviewer is one reviewer. Codex (gpt-6.1-sol, xhigh, read-only) reviewed
the draft at `f15e0009` with records 001 to 006, the specs and the evidence.
Disposition `revise`, 8 findings, retained verbatim in
[close-codex-review.md](notes/close-codex-review.md). Each was checked against
the cited lines before it was applied. The corrected record was not
re-reviewed.

| Finding | Checked | Applied |
|---|---|---|
| L1 "other Python versions were not observed" is false: Python 3.14 was | yes: 006 and RN2's trial ran on 3.14 | the profile row and the boundary now say what was observed on each |
| L2 predicate 7's remote checks were summaries, not retained output | yes | the checks were rerun into a retained file with each exit; predicate 7's audit part is qualified |
| L3 the RN2 row implied the build and run were reviewed | yes: 004 says part two was not | the cell says so |
| L4 four hand-over questions between phases had no sweep row | yes | four rows added |
| L5 nineteen boundary items had no sweep row | yes | rows added, grouped where the boundary repeats |
| L6 seventeen refuted premises had no sweep row | yes | rows added, grouped by phase, every item named |
| L7 the record format has no `status` field | yes | removed; the draft notice stays in the body |
| L8 the milestone README still opened with "0.2.0 is the latest published version" | yes | the README's opening is rewritten |

The retained review quotes one table row of this record, whose link is
relative to this directory; from `notes/` the planning-link test read it as
broken. The quoted target is allowlisted for that one file in
`tests/test_development_scaffold.py`, as for RN1's retained review. That is
the only tracked file outside `.gnd-planning/` this close changes.

## Open-questions sweep

"Proposed" marks a disposition the owner has not ruled.

| Item | Raised | Disposition |
|---|---|---|
| Does the GitHub release attach the wheel, sdist and checksums? | plan §10 | closed: it does (006) |
| RN-D7: the version-independent fixtures refactor, carried to an issue | plan §10, 003 | **proposed: carried** to the next release-preparation milestone; the issue is not filed, and filing it needs the owner's go-ahead. `evidence/RN1/rerecord.py` reduces the cost meanwhile |
| The two red tests on main (N20, N26) | plan, 002 | closed: RN1 (003) |
| The 24 red structure guards | E1, plan §12 | closed: RN0 (002) |
| Structure guards are in no phase's focused gate | 002 | **proposed: carried** to the owner as a rule for `project.md` or a required check; this milestone's own phases ran them by hand after RN0 |
| Both query-policy budgets are full (365 of 365, 310 of 310) | 002 | **proposed: carried**, to be ruled before the next milestone that adds source code: raise the ceilings or refactor |
| The disclosure class of the two Ossie commands (`every-mode`) is not owner-ruled | 002 | **proposed: accepted** as recorded; the rows state what the commands do, and the reference page says so |
| An Ossie export writes constraint literals and descriptions for a fact type marked `redact` | 002, 003, 005 | **proposed: carried** as an issue for a later release; the 0.3.0 notes and the disclosure reference state the behavior |
| The opt-in `ossie_oracle` lane after RN0's edits | 002 D5, 003 D7, 004 D5 | closed by ruling: not run for 0.3.0 ("Skip it for 0.3.0"). **Proposed: accepted residual**, with RN0's byte comparison and the installed probe as the evidence in its place |
| The three files under `src/gnd/schema/ossie/` had no packaging check | 002 | closed: RN2's artifact row reads them from the wheel's file list, and the index install found them (006) |
| The re-record's capture ran under Python 3.14 only | 003 | **proposed: accepted residual**; the moved goldens are not interpreter-keyed, and the closing lane ran on beast-3's Python |
| Notes completeness rests on one reviewer and an options audit | 003, 005 | **proposed: accepted residual**; a missed note can still be added on main |
| `docs/explanation/ossie.md` on what an import restores | 003 | closed: PR 167 |
| The Ossie import report's schema name and the `ossie-import` rule names are not in the format reference | 004 | **proposed: carried** as a docs issue |
| The 0.1.0 control in the acceptance file still downloads from PyPI | 004 D4 | **proposed: carried** to the next release milestone: decide whether to retire the oldest control |
| Installing a wheel in the acceptance tests resolves dependencies from the index | 004 (G5) | **proposed: accepted residual**, as for 0.2.0 |
| Profiles: formal acceptance on macOS 27 arm64 with Python 3.11 (beast-3); a trial acceptance run and the published-package install on macOS 26 arm64 with Python 3.14; no Ubuntu, no Windows | 004, 005, 006 | **proposed: accepted residual**; `docs/support.md` names only the formal acceptance profile |
| `docs/releasing.md` line 17 names only 0.1.0 as published by token upload | 005 | **proposed: carried**, a one-line docs edit for the owner to approve, since the page is normative |
| Repository content and history review; target-only contributor realpaths | 005 (H2) | **proposed: accepted residuals**, as the owner accepted the first for 0.2.0; neither is recorded |
| The stale-text check and the patches are rewritten by hand at each release | 005 | **proposed: carried** to the next release milestone |
| Package ownership and release authority | 005 | accepted as observed: the upload with the stored credentials was accepted by PyPI, which shows upload rights, not ownership |
| The full lane on the patched tree | 006 | closed: the closing lane above |
| `twine check`: the package has no long description | 006 | **proposed: carried**: adding a `readme` to `pyproject.toml` changes package metadata and belongs to the next release |
| Announcements | plan §7, 005, 006 | retired: outside this milestone; none made |
| The owner uploads by hand; an agent session is refused the tag and the release | plan RN-D5, N19 | closed by RN-D13; read by plan §13 (proposed) |
| RN1 had to wait for RN0's merge and take its moved digests on the RN0 tree | 002 | closed: 003 and its spec §13 (digests measured on `d7317d25`) |
| RN2's spec was unwritten and waited for RN1's merge | 003 | closed: 004 |
| RN3 owed the dossier, the patches, the support row and the publication actions | 004 | closed: 005 (dossier, patches); 006 (support row applied, publication) |
| The close owed its record, the sweep and the closing lane | 006 | lane closed above; record and sweep **pending this close's ruling** |
| The plan's reviewed r1 bytes are not in history, and the approved r2 was not re-reviewed | 001 | **proposed: accepted residual**; the reviewer's output confirms both r1 digests |
| The plan reviewer could not run the suite or reach PyPI, GitHub environments or beast-3 | 001 | **proposed: accepted residual**; those rows rested on the session's observations, later repeated in 004 and here |
| The count of four unresolved planning links was the reviewer's; the session had reproduced one | 001 | closed: RN1 measured all four with the test's own walk (003, spec M11) |
| Two count literals changed in RN0 are covered only by the set assertions beside them | 002 | **proposed: accepted residual** |
| Ossie byte equality was shown on the census and two examples, not for every model | 002 | **proposed: accepted residual**; the reviewer found no counterexample |
| Lint: repository-wide `ruff` findings predate the milestone; RN0 and RN1 recorded a narrower lint gate than RN0's spec named | 002 spec, 003 spec | **proposed: accepted residual**; no phase added a finding. The repository-wide count (182) is **proposed: carried** as maintenance |
| Five gzip containers were re-recorded by editing the stored document; equality with live output rests on their owning tests | 003 | **proposed: accepted residual**; those tests pass in the closing lane |
| Version availability was a dated observation needing a recheck immediately before upload | 003, 004 | closed: 006 (404 at 15:36:31Z, upload at 15:36:41Z) |
| The retained candidate lives outside git; history holds its identities, not its bytes | 004 | closed in substance: the same bytes are now on PyPI and attached to the GitHub release, with matching digests |
| Candidate acceptance is not the published files' identity | 004 | closed: step E (006) |
| The installed identity probe pins no independently derived digest | 004 | **proposed: accepted residual**; the format's own vectors test the algorithm |
| RN2's tightened checks have no separate pre-fix red run; the session did not rebuild the reviewer's broken implementations | 004 spec | **proposed: accepted residual** |
| RN2 part two (the build and the run) was not reviewed | 004 | **proposed: accepted residual**; it is commands and retained output |
| Review fixes in RN0, RN1, RN2 part one and RN3 were not re-reviewed | 002, 003, 004, 005 | **proposed: accepted residual**; the closing lane and this close review ran after them |
| The default lanes were single runs on one machine, with uv 0.13.7 on beast-3 | 002, 003 | **proposed: accepted residual**; five lanes on the final trees agree |
| RN3's patches depended on the `b913d43e` tree, the check's allowlist on that text, and the date was a stand-in | 005 | closed: 006 applied all three to `2165ccf1` with the date 2026-11-11; the check exits 0 |
| The first step-E run failed on a cached 404 and its output was not retained | 006 | **proposed: accepted residual**; the rerun is retained. Lesson recorded: poll the version endpoint before comparing |
| RN-D11's other opt-in lanes (`evidence`, `census` and the rest) did not run | plan, all records | closed by ruling: excluded for this milestone (RN-D11) |
| Refuted in RN0: the disclosure failures were missing rows, not a stale count; the first `value-free` class was wrong (a default export does not refuse populations, and populations are not the only values); the focused gate omitted the disclosure docs test; the skill-link repair needed a chained successor, not regeneration; the dynamic inventory gained 133 rows, not 132; the successor's reason miscounted the reads (nine exporter reads replaced, five importer reads consolidated) | 002, RN0 spec | closed: each is corrected in 002 or its spec, with review K1 and K2 |
| Refuted in RN1: two paragraphs were over the limit, not one; the approved notes said an import restores the original model; reconciliation by pull request missed four changes; the planning-link test was twice reported from a run made too early | 003 | closed: each is corrected in 003, with review F1 to F5 |
| Refuted in RN2: the beast-3 script ended at exit 127 on its added last step; the first carries test failed on a missing input before its version check | 004 | closed: V5 run by hand; the version check moved first (004) |
| Refuted in RN3: one tag sentence needed patching, not two; the reworded prerequisite allowed an install route the commands cannot use; the first check passed five kinds of stale text; the first control run printed the wrong exit status; the unpatched tree exits 1, not 2 | 005, RN3 spec | closed: each is corrected in 005 or its spec, with review H1 to H9 |
| Close review instrument | plan §8 | closed: "One Codex reviewer" (owner, 2026-11-11) |

## Plan repair

Plan §13 (appended 2026-11-11, proposed) reads RN-D5 and the publication
stage against RN-D13. The earlier amendment, §12, was approved by the owner
("Yes, add RN0").

## Refactoring review

- RN0 executed two behavior-preserving refactors in the Ossie modules (reads
  through `ModelIndex`; one accessor for foreign roles).
- Deferred refactors, each with a sweep row above: the version-independent
  fixtures (RN-D7); the hand-written stale-text check and patches; the
  acceptance file's oldest control.
- The component index check over `2490dd77..HEAD` was run per phase (RN0,
  RN1: 0 to fix); no source file changed after RN0.

## Refuted premises

- The plan assumed main had two red default-lane tests; it had 26.
- The plan assumed the owner would publish by hand and that an agent session
  would be refused the tag and the release.
- Several times in this milestone a check was reported as passing from a run
  made before the last file was written (the planning-link test, twice in
  RN1), or from the wrong process's exit status (RN3's first control run).
  Each was caught by a later run and is in the phase's record.

## Boundary: what this close does NOT establish

- One reviewer for the close, and the corrected record was not re-reviewed.
- One reviewer per phase, and no phase's fixes were re-reviewed.
- The closing lane ran once, on one machine (beast-3, macOS).
- Observed for 0.3.0: formal acceptance on macOS arm64 with Python 3.11; a
  trial acceptance run and the published-package install on macOS arm64 with
  Python 3.14. Ubuntu and Windows were not observed.
- The opt-in lanes did not run; the Ossie oracle lane among them.
- PyPI ownership, publisher registration and repository settings are not
  auditable here.
- Any announcement is the owner's.

## Owner rulings at the close

- **Close review instrument:** "One Codex reviewer" (2026-11-11, in this
  session).
- **Not ruled yet:** the proposed dispositions of the sweep; plan §13; this
  close.
