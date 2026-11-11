# Close review (Codex), retained verbatim

- Instrument: one reviewer, the owner's choice ("One Codex reviewer", 2026-11-11). One reviewer is one reviewer; the project's bar for a close is the maintained panel.
- Command: `codex exec --ephemeral --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin, exit 0. Model: gpt-6.1-sol (the tool's configured default).
- Reviewed bytes: `007-milestone-close.md` and plan §13 at commit f15e0009, with records 001 to 006, the specs and the evidence.
- What the reviewer could not do: write files, reach PyPI, rerun builds, acceptance or the lane (its own list at the end).
- The output below is unedited (it contains no home-directory path); the trailing "codex exit" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: L1
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:214
QUOTE: "Ubuntu, Windows and other Python versions were not observed for 0.3.0."
PROBLEM: Python 3.14 was observed. Record 006-publication.md:111 identifies the fresh published-package installation as macOS arm64, Python 3.14. Its retained step-E output records successful installation, help, schema discovery, export and import. RN2's spec also records an 18-test trial acceptance run on Python 3.14 at lines 306–310. The sweep's “One profile observed” row at line 172 needs the same qualification.
FIX: Say that formal candidate acceptance was recorded on macOS/Python 3.11, with additional Python 3.14 trial acceptance and published-package smoke observations; Ubuntu and Windows remain unobserved.

ID: L2
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:121
QUOTE: "yes as read by plan §13 (proposed)"
PROBLEM: Predicate 7 includes an evidence obligation as well as the prohibition on phase publication. The plan requires dated baseline and closing remote checks. The close supplies abbreviated output fields, but no retained remote-state transcript or digest. Its “Gate output (verbatim)” section contains only the closing test lane. For example, “GND v0.3.0 (Latest, 2026-11-11T15:38:27Z), GND v0.2.0, GND v0.1.0” is a reformatted summary, not verbatim “gh release list” output. The combined PyPI GET entry likewise supplies a summary rather than either response. This does not demonstrate the required evidence retention or verbatim-output contract. It does not establish that the reported remote values are false.
FIX: Retain and bind the actual dated remote outputs, with their individual exits. If the original outputs were not retained, disclose that and distinguish fresh checks from historical observations. Qualify predicate 7's audit component until repaired.

ID: L3
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:101
QUOTE: "| RN2 build and acceptance | [004](004-phase-RN2.md) | acceptance on beast-3, Python 3.11: 18 passed; two builds identical | `revise`, G1 to G7, six applied, one accepted | 164, 165 |"
PROBLEM: The table gives the build-and-acceptance step an unqualified review entry. Record 004-phase-RN2.md:146–147 explicitly says: “Part two (the build and the run) is commands and their output; it was not reviewed.” Codex reviewed the part-one test diff, not the retained candidate build and acceptance evidence.
FIX: Change the review cell to “part-one tests only: revise, G1–G7; part-two build and run not reviewed.”

ID: L4
SEVERITY: high
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:150
QUOTE: "## Open-questions sweep"
PROBLEM: Explicit questions concerning later work have no sweep row. Within this milestone, these are:

- 002-phase-RN0.md:218–219: RN1 must wait for the merge and supply moved digests measured on the RN0 tree. This was subsequently satisfied in record 003 and its spec, but has no closed row.
- 003-phase-RN1.md:243: RN2's spec remained unwritten and awaited the merge. Record 004 supplies the subsequent outcome, but no sweep row closes this question.
- 004-phase-RN2.md:181–183: RN3's dossier, post-publication patches, support row and publication actions. Publication actions appear in other rows; the dossier and prepared-patch hand-over obligation itself has no disposition row.
- 006-publication.md:121: the milestone close's record, question sweep and closing lane. Line 177 disposes the lane, and line 181 leaves the instrument open, but neither disposes completion of the close record and sweep.

These omissions remain omissions even where the phase table or predicate table supplies evidence elsewhere. The record format explicitly requires sweep rows.
FIX: Add closed rows citing the subsequent records for the first three obligations, and a pending close-completion row for the fourth. Keep predicate 9 pending until the sweep and owner ruling are complete.

ID: L5
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:154
QUOTE: "| Item | Raised | Disposition |"
PROBLEM: The following distinct boundary items also have no disposition row. Source filenames below are relative to this milestone:

- 001-plan-gate.md:66–71: the reviewed r1 bytes are absent from history, and approved r2 was not re-reviewed.
- 001-plan-gate.md:73–74: the plan reviewer could not exercise the suite or independently check PyPI, GitHub environments or beast-3.
- 001-plan-gate.md:83–84: the four-link count was initially the reviewer's observation; the driving session reproduced only the first link. RN1 later measured all four, but that closure has no row.
- 002-phase-RN0.md:168–171: two changed count literals have only adjacent set assertions as their controls.
- 002-phase-RN0.md:185–187: equal Ossie bytes were established on the census and two examples, not universally; equivalence was not proved.
- notes/phase-RN0-spec.md:240–244 and notes/phase-RN1-spec.md:349–351: pre-existing lint findings remained, including the substitution of a narrower lint result for RN0's originally specified repository-wide exit-0 gate.
- 003-phase-RN1.md:220–222: five gzip containers were edited internally rather than regenerated; equality to live output rests on their owning tests.
- 003-phase-RN1.md:215–217 and 004-phase-RN2.md:169–170: version availability was only a dated observation and required another check immediately before upload. Record 006 records that later check, but the sweep does not close this obligation.
- 004-phase-RN2.md:71–74: the retained candidate files live outside git; history contains their identities, not their bytes.
- 004-phase-RN2.md:163–165: candidate acceptance alone does not establish the identity of published files. Step E subsequently supplies that identity, but there is no sweep disposition for this boundary.
- 004-phase-RN2.md:173–174: the installed identity probe pins no independently derived digest.
- notes/phase-RN2-spec.md:298–300: the driving session did not independently reproduce the reviewer's broken implementations or obtain separate pre-fix red runs for the tightened checks.
- 004-phase-RN2.md:146–147: part-two build and acceptance evidence was not reviewed.
- Records 002, 003 and 005: fixes were not re-reviewed. The close repeats this in its boundary, but supplies no sweep disposition.
- Records 002 and 003: default-lane observations were single-machine runs, using beast-3's uv 0.13.7. The sweep's acceptance-profile row addresses Python 3.11/uv 0.10.10, not these separate lane observations.
- 005-phase-RN3.md:140–145: patch applicability depended on the b913d43e tree, the check's allowlist depended on that text, and its publication date was a stand-in. Record 006 subsequently applied and dated the patches, but these boundaries have no closed row.
- 006-publication.md:107–110: the first step-E attempt failed because the version endpoint still returned 404, and its output was not retained.
- 006-publication.md:111: the published-package index observation was confined to one macOS/Python 3.14 machine; it is not represented accurately by the existing profile row.
- RN-D11's excluded lanes other than ossie_oracle are named in the records and close boundary, but have no sweep row recording their disposition.

FIX: Add explicit rows, grouping repeated instances of the same boundary. Cite subsequent evidence for resolved obligations; label proposed acceptance of residual limits as proposed. Existing rows for the oracle, notes completeness and dependency resolution do not dispose these different limits.

ID: L6
SEVERITY: medium
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:199
QUOTE: "## Refuted premises"
PROBLEM: Several refutations are summarized here or in phase reviews but never receive sweep rows. Missing items are:

- 002-phase-RN0.md:223–224: the disclosure failures were missing command rows, not merely a stale count.
- 002-phase-RN0.md:225–227 and notes/phase-RN0-spec.md:267–273: the initial value-free classification was false; non-strict export does not refuse populations, and populations are not the only disclosed values.
- 002-phase-RN0.md:228–229: the focused gate omitted the disclosure documentation mirror test and therefore missed an actual phase regression.
- notes/phase-RN0-spec.md:221–224: the skill-link repair needed an appended successor chain rather than regeneration of the original pinned set.
- notes/phase-RN0-spec.md:230–232: the dynamic-inventory addition was 133 rows, not the expected 132.
- notes/phase-RN0-spec.md:265: the successor explanation's thirteen removed exporter reads were actually nine, with five importer reads consolidated separately.
- 003-phase-RN1.md:247–248: two prose paragraphs exceeded the limit, not one.
- 003-phase-RN1.md:249: the owner-approved notes falsely promised restoration of the original model after an Ossie round trip.
- 003-phase-RN1.md:250–251: reconciliation by existing notes and pull-request list missed four changes within already-noted pull requests.
- 003-phase-RN1.md:252–253: scaffold success was twice claimed before the final planning file existed.
- 004-phase-RN2.md:191–192: the supposedly successful overall build script actually exited 127 because uvx was absent from PATH.
- 004-phase-RN2.md:193–195: the initial negative acceptance test failed on missing input before reaching its intended version assertion.
- 005-phase-RN3.md:161–162: only one tag sentence required patching, not two.
- 005-phase-RN3.md:163–165: the proposed shared-expense installation prerequisite allowed an installation route that could not run the documented commands.
- 005-phase-RN3.md:166–167: the initial stale-text checker accepted five classes of stale input.
- notes/phase-RN3-spec.md:228–229: the first control run reported tail's status instead of the check's status.
- notes/phase-RN3-spec.md:270–272: the unpatched-tree result was corrected from exit 2 to exit 1.

The rows concerning red tests, disclosure classification, notes completeness and manual publication do not explicitly disposition these separate refutations.
FIX: Add closed sweep rows naming each correction and its phase record or retained evidence. Related checker corrections can share a row if every constituent item is named.

ID: L7
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/007-milestone-close.md:7
QUOTE: "status:"
PROBLEM: The cited record format explicitly excludes a status field at lines 115–117. The body already clearly states that this is an unruled draft, so removing the field would not obscure its authority.
FIX: Remove the front-matter status field and retain the draft notice and pending owner-rulings section.

ID: L8
SEVERITY: low
LOCATION: .gnd-planning/milestones/release-0.3.0/README.md:4
QUOTE: "0.2.0 is the latest published version;"
PROBLEM: The milestone's current index still opens with this statement and “nothing here is published”; its bold Status paragraph also says “No phase spec is approved.” These conflict with its later publication paragraph and the close's post-publication account. This is outside the root README/docs stale-text check, so that check cannot detect it.
FIX: Mark the opening and initial status explicitly as historical, or replace them with the current publication and draft-close status.

Checked and found true

- All 16 evidence hashes in the close match the checked-out files.
- Historical plan and four phase-spec approval hashes match their named commits.
- PRs 162–167 were merged by vasiloglou; their recorded merge commits agree with git and GitHub.
- The remote main commit is 7d86dc35. Its package-input diff against 4c07c0e6 is empty, as is the milestone's .github diff.
- Tag v0.3.0 is 257a8bb3 and peels to 4c07c0e6. The GitHub release date, attached filenames, sizes and wheel/sdist hashes agree with the records.
- The closing shard counts sum to 19,016 passed; the quoted shard lines and two error IDs match the retained output.
- RN2's retained log records 18 passed, followed separately by the script's exit 127.
- RN3's retained checks contain 13 nonzero invocations, including the usage error.
- Predicates 1–6 and 8 have supporting repository or retained evidence, subject to their stated limits. Predicate 9 is correctly pending.
- Predicate 7's prohibition holds as written: RN0–RN3 are preparation phases; publication is a separate stage. Section 13 honestly identifies the session as the actor under RN-D13. This does not repair L2's evidence-retention gap.
- The owner publication quotations agree with record 006. The close and section 13 consistently identify their proposed rulings as pending.
- Root README/docs install pins name 0.3.0; RELEASED includes it; the notes heading and compatibility statement use 2026-11-11. A read-only reproduction of the stale-text predicates found 20 allowlisted hits and no problems.
- No release.yml runs appeared in the complete 104-run GitHub listing.
- No files were edited.

Could not check

- Execute stale-text-check.sh itself: it creates temporary files, prohibited by the read-only sandbox. Its checks were reproduced in memory instead.
- Independently retrieve PyPI responses or re-hash served distributions: browsing returned cache misses and shell access could not resolve pypi.org. Publication facts were checked against retained step-E evidence and GitHub asset hashes.
- Re-run installed acceptance, builds or the beast-3 lane: these require writable environments and external retained artifacts.
- Independently authenticate owner chat quotations: only the committed records contain the authorization exchanges.
- Recover the original remote-check stdout/stderr, historical environment configuration, repository settings or PyPI publisher configuration: the necessary retained outputs or access were unavailable.
codex exit 0
