# Phase RR3: publication hand-over

## 1. Status

**Approved (o, 2026-11-08); implementation under way.** The owner approved draft r2 as pushed to PR 131 at commit `6b4644d1` (spec sha256 `75e0926704f52a6801558be1d1a45b8d37cec663aa5b6d71dcb1c7ca6e2a25ce`), answering "Approve the RR3 spec (draft r2) with D1–D6 as recommended?": **"Approve as recommended"**. D1 to D6 are ruled as recommended (rows in §7). It is not a review opinion; the approved bytes carry the Codex review of r1 only. It approves no publication, no route, no tag, no release and no application of any patch. `auto=false`.

Prior status (r2): "Draft r2, awaiting owner review (2026-11-08). Nothing in this spec is approved."

## 2. Provenance

- Plan r2 (approved 2026-11-07): [rule-check-release-plan.md](rule-check-release-plan.md)
  §4 RR3-C1 to RR3-C5, completion predicates 5 and 6, obligations O3 to O8
  and O15, conflict C2, risks R4, R6 and R7, rulings RL-D4, RL-D5 and RL-D6,
  and the plan §10 open questions (the support row, the GitHub release files).
- RR2 record [003-phase-RR2.md](../003-phase-RR2.md). The candidate is main
  `7c0f4d0e`: wheel `e323c19e…69e4`, sdist `f85818ea…5104`. Its open
  questions are routed in §3.
- Base: main `25f58b5e` (the RR2 record merged; FU4 `6ed86d90` is on main,
  and the candidate does not contain it).
- One reviewer (Codex) read r1 (commit `fd4cb5e4`, sha256
  `2bd704397849c6603d8d868db92b6e94e20f50b417567ef4dd8d46894d158125`):
  `revise`, eight findings, all accepted ([record](phase-RR3-codex-review.md),
  dispositions §12). r2 repairs them and **carries no review opinion of its
  own**. Changed sites are tagged `(r1)`.

## 3. Obligations (step 0 harvest)

| Source | Obligation | Discharged by |
|---|---|---|
| RR3-C1 | the dossier lists the candidate identity (commit, hashes, tool versions), the results, and what was not measured (index install, Ubuntu, Trusted Publishing, TestPyPI, external user trial) | M1 §A, §B, §C |
| RR3-C2 | the dossier lists each owner action before publication, with the evidence that it is still open (O3 to O5, O8, O15): ownership, an availability recheck, the route, tag and GitHub release, announcements | M1 §D, V3 |
| RR3-C3 | the post-publication patch exists as a file and is not applied. It covers every instruction that publication makes stale, found by a grep at RR3 time and classified hit by hit. It includes the `RELEASED` edit, with a mutant showing the pin test fails without it | M2, §6.2 inventory, T1 to T4 |
| RR3-C4 | `docs/releasing.md`: the stale phase wording is replaced and the two authorized routes are stated conditionally; neither is configured nor invoked. This is a normative edit, proposed here for the gate | M3, D1, T6 |
| RR3-C5 | the served-file check and the post-publication commands are listed once, citing the workflow's step rather than copying it | M1 §E, M3 |
| predicate 5 | the dossier states candidate identity, evidence, limits and owner actions; the patch is prepared and not applied | M1, M2, V2 |
| predicate 6 | nothing enables publication; the dated read-only remote checks | V3 |
| plan C2, R7 | availability is checked again immediately before any upload | M1 §D action 2 |
| plan R4, O7 | under the workflow route the uploaded bytes are that run's own build | M1 §D action 3, finding F1 (§3.1) |
| plan §10 open question | a support row for the candidate's observed profile | D3 |
| plan §10 open question | the GitHub release for the new tag: attach the files as v0.1.0 did? | D4 |
| RR2 open question | the 0.1.0 control downloads from PyPI on every prepare run | M1 §C (a limit; no change) |
| RR1/RR2 carried | deferred version-independent fixtures refactor; two load-sensitive timing tests | not RR3: routed to the milestone close's question sweep; FU4 (issue 117) has since addressed the timing tests on main, and the close checks that |
| O22 / AGENTS.md | component index | V5 |

### 3.1 Observations for this draft (2026-11-08)

- **Inventory (r1).** The search is:

  ```sh
  git grep -n -i -E '0\.1\.0|0\.2\.0|next release|not published|not signed off|until 0\.2\.0|newer than|first pypi release|after phase 3' -- README.md docs ':!docs/release-notes.md'
  ```

  It finds 31 lines in 15 files. `docs/release-notes.md` is excluded from the
  search because its subsections are history; its heading and its opening
  paragraph (lines 3 to 9) are classified on their own row. Every hit is
  classified in §6.2.
- **F1. The workflow route cannot publish this candidate as built.**
  `release.yml` builds whatever `main` is when it is dispatched (job condition
  `github.ref == 'refs/heads/main'`, then `actions/checkout` and `uv build`).
  Main is already past the candidate: `25f58b5e` contains FU4 and the RR2
  record. Under that route the upload is a new build, tied to its own source
  commit and its own acceptance run, and RR2's evidence is not its evidence
  (r1). Whether its bytes differ from the retained ones is not known until
  someone compares hashes. The changes since `7c0f4d0e` are tests and
  planning files, so identical package bytes are possible (O-c of RR2). Only the token route can upload the
  retained `7c0f4d0e` files. This sharpens O7; it does not choose a route
  (RL-D5).
- **F2.** `docs/releasing.md` still describes Trusted Publishing as the route
  for "the first PyPI release", and it says "After Phase 3 accepts the
  prepared package…", which refers to the public-launch milestone. 0.1.0 was
  published by a token upload (O4).
- **F3.** No docs test pins the "Before you start" checkout instructions:
  `tests/test_plan_app_docs.py` and `tests/test_pyrel_learning_path.py` have
  no match for `checkout`, `git clone`, `0.1.0` or `newer than`.

## 4. The standing rules, bound to this phase

| Rule | Binding here |
|---|---|
| plan 0.1 prepare, never publish | RR3 writes files under `evidence/` and edits `docs/releasing.md`. It runs no upload, tag, release, environment or publisher command; V3 shows the remote state is unchanged |
| plan 0.2 one home for the version | the patch changes no version literal except `RELEASED` (historical data) and the install pins, both checked by `tests/test_release_version.py` (T2, T3) |
| plan 0.3 no instruction names an unpublished version | the pins move only inside the unapplied patch; T5 shows the RR3 tree still names 0.1.0 and `tests/test_release_version.py` passes on it |
| plan 0.4 evidence belongs to exact bytes | the dossier names `7c0f4d0e` and the three hashes. F1 states that a workflow build is a different candidate |
| plan 0.7 frozen surfaces | `release.yml`, `tests/test_release_preparation.py` and the dependency freeze are unchanged; `docs/releasing.md`'s procedure steps change only as D1 rules |
| plan 0.8 stop rule | estimates in §10 |
| project.md 1 to 4 | inapplicable: no code reads untrusted input; RR3 writes documents and a patch |
| project.md 5 one home | the procedure's home is `docs/releasing.md`. The dossier cites it and the workflow's served-file step, and copies neither (RR3-C5). The post-publication commands live in one place (M3) |
| project.md 6 measurement | the inventory (§6.2) is a grep, rerun as T5 |

## 5. Goal

On the RR3 branch:

- `evidence/RR3/dossier.md` exists, and every owner action in it cites the
  evidence that it is still open, dated.
- `evidence/RR3/post-publication.patch` and
  `evidence/RR3/post-publication-github-release.patch` apply cleanly with
  `git apply --check` (exit 0).
- In a scratch copy with both patches applied, `uv run pytest -q
  tests/test_release_version.py tests/test_release_docs.py
  tests/test_marketplace_plugins.py` exits 0.
- With the `RELEASED` hunk removed, `tests/test_release_version.py` exits 1.
- On the RR3 tree itself, `tests/test_release_version.py`,
  `tests/test_release_docs.py` and `tests/test_release_preparation.py` exit 0.
- `git diff origin/main -- .github` is empty.

## 6. Design

### 6.1 Reuse table

| Capability | Searches | Found | Decision |
|---|---|---|---|
| state the release procedure | `git grep -l releasing.md`; `components_index.py search release publish procedure` | `docs/releasing.md` (the one home) | adapt (M3) |
| check pins against published versions | — | `tests/test_release_version.py` (`RELEASED`, `PIN_FILES`, `assert_pins_name_published_versions`) | reuse; the patch edits it (M2) |
| compare served files after upload | — | `release.yml`, step "Compare served PyPI files and exercise a fresh index install" | cite it, don't copy (RR3-C5) |

### 6.2 Inventory and classification (the post-publication patch's scope)

| File:line | Text | Class | In the patch |
|---|---|---|---|
| `README.md:43` | `uv tool install get-nick-done==0.1.0` | stale | pin to 0.2.0 |
| `docs/index.md:144` | same | stale | pin to 0.2.0 |
| `docs/installation.md:13`, `:25` | `uv tool install` / `pip install get-nick-done==0.1.0` | stale | pin to 0.2.0 |
| `docs/marketplace-plugins.md:9`, `:15` | "installs the published runtime, 0.1.0. Until 0.2.0 is…"; the pin | stale | pin to 0.2.0; the "until published" sentence is removed |
| `docs/marketplace-plugins.md:72-80` | "Until 0.2.0 is published, the plugin on `main` is newer…" and the checkout route | stale | replaced by one sentence: install the runtime version matching the plugin |
| `docs/compatibility.md:3-6` | "Version 0.1.0 is published. Version 0.2.0 is prepared and not published…" | stale | "Versions 0.1.0 and 0.2.0 are published", with the 0.2.0 publication date (D2) |
| `docs/support.md:11-12` | "…the prepared 0.2.0 package is not signed off and no profile is observed for it" | stale | D3 |
| `docs/release-notes.md:3-9` (r1) | the opening paragraph ("Version 0.1.0 is the published release. Version 0.2.0 is prepared and not published … Until it is published, install commands in these documents name 0.1.0 …") and the heading `## 0.2.0 (prepared, not published)` | stale | the paragraph says 0.2.0 is the published release; the heading becomes `## 0.2.0 (PUBLICATION_DATE)` (D2) |
| `docs/marketplace-plugins.md:10` (r1) | "published, the plugin on `main` is newer than that runtime" | stale | removed with lines 9 and 15 |
| `docs/releasing.md:9`, `:33` (r1) | "To enable the first PyPI release…"; "After Phase 3 accepts the prepared package…" | stale now, not at publication | not in a patch: M3 changes them in RR3 itself (D1), and T7 checks it |
| `tests/test_release_version.py:24` | `RELEASED = {"0.1.0"}` | stale at publication | `{"0.1.0", "0.2.0"}`; plus D5 |
| `docs/pyrel-apps.md:39-41` | "need a GND newer than the 0.1.0 release on PyPI, so install it from a checkout … until the next release" | stale | D6 |
| `docs/tutorials/course-planner.md:38-39`, `learn-rules.md:55-56`, `clinic-refills.md:31-32`, `docs/how-to/access-requests.md:21-22`, `lease-schedule.md:21-22`, `trip-budget.md:21-22` | the same instruction, or a pointer to it | stale | D6 |
| `docs/installation.md:65`, `docs/marketplace-plugins.md:54` | "The `v0.1.0` tag … predates plugin packaging" | stale only once a `v0.2.0` tag exists at the published commit (whichever route) | tag patch (D4, r1) |
| `docs/installation.md:114`, `:118` | "download the wheel and checksums from the v0.1.0 release" | stale only if the v0.2.0 GitHub release carries the files | release-files patch (D4, r1) |
| `docs/development/candidate.md:11` | the 0.1.0 documentation-candidate record | historical | not in the patch |

The release-notes subsections and the `0.1.0` mentions inside
`docs/release-notes.md` are history and stay.

### 6.3 Modules

**M1. `evidence/RR3/dossier.md` (about 150 lines).** Sections:

- **A. Candidate identity:**
  - commit `7c0f4d0e`, the PR 125 merge;
  - the three file names and sha256s, `SOURCE_COMMIT` and `BUILD_PROFILE`;
  - the two retained copies (paths and hosts).
- **B. Results:** each with a link to `003-phase-RR2.md` and its evidence:
  - B1 equals B2;
  - V4 gave 14 passed (beast-3, macOS 27.0.1, Python 3.11.18, uv 0.10.10);
  - V5 printed `gnd 0.2.0`;
  - the 0.1.0 controls.
- **C. Not measured:**
  - the index install, Ubuntu, Windows, other Python versions;
  - Trusted Publishing and the `pypi` environment;
  - TestPyPI;
  - an external user trial;
  - the served-file comparison, which only exists after an upload;
  - the 0.1.0 control's dependency on PyPI keeping 0.1.0 served.
- **D. Owner actions before and at publication**, numbered. Each has the
  evidence, dated, that it is still open:
  1. **Package ownership:** confirm the account that uploaded 0.1.0 owns
     `get-nick-done` (O4; not readable by this session).
  1a. **Repository review (O8, r1):** confirm the repository's visibility, and
     review its content and history for what a release would point to. Record
     the visibility observed by `gh api` on the day.
  1b. **Release authority (O8, r1):** confirm that only the owner can publish
     `get-nick-done`, whichever route is used. Not established by 0.1.0's
     token upload (the public-launch close says so); not auditable here.
  1c. **Breaking changes and migration (O15, r1):** confirm the 0.2.0 notes
     record every breaking change with migration instructions. The dossier
     lists the notes' own statements that a change is opt-in or leaves
     existing output unchanged, as a starting point; it does not claim the
     list of breaking changes is complete.
  1d. **Never overwrite released files (O15, r1):** 0.1.0's files stay as
     they are. A failed or wrong 0.2.0 upload is corrected with a new version
     or a yank, as `docs/releasing.md`'s incident paragraph says.
  2. **Version availability**, checked immediately before the upload (C2,
     R7). The last observation was 2026-11-08T05:45:55Z: only `0.1.0`.
  3. **The route** (RL-D5, the owner's):
     - (a) A token upload of the retained `7c0f4d0e` files. The RR2
       evidence applies to these bytes, and the notes match them.
     - (b) `release.yml` with `publish=true`. This first needs a PyPI pending
       publisher (account side, not auditable here) and a protected `pypi`
       environment with the owner as required reviewer (O5: none exists on
       2026-11-08). It builds main at dispatch, so per F1 it is a new build:
       the notes must cover everything on that main (RR2-C0 again), and its
       own acceptance run, not RR2's, is its evidence (r1).
  4. **The tag:** `v0.2.0` at `7c0f4d0e` (under route a), or at the commit
     the workflow built (route b).
  5. **The GitHub release** and whether it carries the wheel, sdist and
     `SHA256SUMS`, as v0.1.0's did (D4).
  6. **Apply the post-publication patches** in a PR (M2), after the served
     files match: the main patch always; the tag patch if action 4 happened;
     the release-files patch if action 5 attached the files (r1).
  7. **Issue 118:** comment and close once the served files are verified.
  8. **Announcements:** none are prepared; they are a separate decision.
- **E. After the upload:**
  - The served-file comparison and fresh index install are the
    `release.yml` step "Compare served PyPI files and exercise a fresh index
    install". Under route (a) the owner runs that step's two commands by
    hand, with `candidate/release` pointing at the retained files. The
    dossier cites the step and gives only the substitution.
  - On a mismatch, follow `docs/releasing.md`'s incident paragraph.

**M2. Three patch files (about 100 diff lines in total) (r1).**

- `evidence/RR3/post-publication.patch`: every "stale" row of §6.2 that does
  not depend on a tag or a GitHub release, plus the `RELEASED` edit and the
  D2 and D5 test additions.
- `evidence/RR3/post-publication-tag.patch`: the two "v0.1.0 tag predates
  plugin packaging" sentences. They are applied once a `v0.2.0` tag exists at
  the published commit.
- `evidence/RR3/post-publication-release-files.patch`: the release-artifact
  section. It is applied only if the GitHub release carries the files.

All three are made with `git diff` against the RR3 commit and are not
applied. Each applies on its own and in any combination with the others (T1).

**M4 (r1). `evidence/RR3/stale-text-check.sh` (about 25 lines).** It runs the
§3.1 search and the notes-opening check, then compares each hit with an
allowlist in the same file (the rows classified historical in §6.2). It
exits 1 on any hit not in the allowlist and prints that hit. T5 runs it.
Date placeholders: per D2, the patch writes `PUBLICATION_DATE` where the
date goes, and the dossier's action 6 says to replace it. T4 fails while the
placeholder is unreplaced, as a safeguard.

**M3. `docs/releasing.md` (about 20 changed lines, D1).**

- Replace "To enable the first PyPI release…" and "After Phase 3 accepts the
  prepared package…" with route-neutral wording.
- State the two routes conditionally, each with its precondition and what it
  uploads (F1). This home configures and invokes neither.
- Keep the incident paragraph and the service references unchanged.

## 7. Decisions

| ID | Question | Readings | Cost of each |
|---|---|---|---|
| D1 | May RR3 rewrite `docs/releasing.md`'s procedure text (RR3-C4, a normative edit)? | (a) **Yes, as M3**: route-neutral, both routes conditional, F1 stated, incident text unchanged. (b) Only the stale phase sentence is replaced; the Trusted-Publishing-first wording stays | (a) the procedure's one home agrees with the dossier and with how 0.1.0 shipped. (b) a reader of `releasing.md` is sent to a route that is not configured (O5) and that cannot publish the tested bytes (F1). Neither changes an exit code **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |
| D2 | How does the patch handle the publication date? | (a) **A `PUBLICATION_DATE` placeholder** in the notes heading and the compatibility sentence, replaced on the day; a check refuses the placeholder (T4). (b) No date: `## 0.2.0` | (a) one more step on the day, guarded. (b) the notes lose the date 0.1.0's entry has **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |
| D3 | `docs/support.md` after publication | (a) **The patch adds one row**, "macOS 27, Python 3.11, uv 0.10.10: observed in the RR2 acceptance of the 0.2.0 candidate (7c0f4d0e)", and drops "not signed off" from the two 0.1.0 rows. (b) It only removes the "not signed off" text | (a) names the one profile with evidence; under route (b) that row would describe a different build and must be dropped (the dossier says so). (b) the support page claims nothing for 0.2.0 **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |
| D4 | Tag and GitHub-release text (r1) | (a) **Two separate patches**: one for the tag sentences, applied once a `v0.2.0` tag exists at the published commit; one for the release-artifact section, applied only if the release carries the files. (b) Fold both into the main patch | (a) each text changes exactly when its condition holds, whichever route and whichever commit. (b) one patch, but wrong if no tag is made or no files are attached **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |
| D5 | Should the patch also make the pin test require that, once the declared version is released, every pin names it? | (a) **Yes**: a new assertion in `tests/test_release_version.py`, with a mutant (an old pin after publication fails). (b) No: pins may name any published version not newer than the declared one | (a) a forgotten pin fails the suite on publication day. (b) today's rule lets 0.1.0 pins survive a publication silently (T3 shows this) **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |
| D6 | The seven "newer than the 0.1.0 release … install from a checkout" instructions (r1) | (a) **Versionless**: "Install GND from PyPI as the [installation page](…) shows; to use work on `main` that is newer than the latest release, install from a checkout" followed by the existing checkout commands. No version literal. (b) Pin each to `get-nick-done==0.2.0` and add the seven pages to `PIN_FILES` | (a) no edit at the next release, and no version literal outside the checked files (plan rule 2). (b) seven more pins to move each time, though checked **Ruled (o, 2026-11-08): (a), as recommended** ("Approve as recommended") |

## 8. Tests

| ID | Check | Expected |
|---|---|---|
| T1 | `git apply --check` of each patch on the RR3 tree | exit 0 |
| T2 | scratch copy, both patches applied, `PUBLICATION_DATE` replaced by a test date: `uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_marketplace_plugins.py --tb=short` | exit 0 |
| T3 | scratch copy, main patch without the `RELEASED` hunk | `tests/test_release_version.py` exit 1, `test_install_pins_name_a_published_version` failing |
| T3b (D5) | scratch copy, main patch with one pin left at 0.1.0 | exit 1, the new assertion failing; on the RR3 tree today it passes, so it is not vacuous |
| T4 | scratch copy, both patches applied, placeholder **not** replaced | exit 1 (the D2 guard: a test in the patch refuses `PUBLICATION_DATE` once the version is in `RELEASED`) |
| T5 (r1) | `evidence/RR3/stale-text-check.sh`: on the RR3 tree (no patch applied), then on a scratch copy with all three patches applied | exit 1 on the RR3 tree, printing the stale hits (liveness); exit 0 with all three patches applied. With only the main patch applied, it exits 1 and prints exactly the hits the tag and release-files patches cover |
| T6 | the RR3 tree: `uv run pytest -q tests/test_release_version.py tests/test_release_docs.py tests/test_release_preparation.py --tb=short` | exit 0 |
| T7 (r1) | a new `tests/test_release_docs.py::test_releasing_procedure_states_both_routes`: `docs/releasing.md` contains neither "After Phase 3 accepts" nor "To enable the first PyPI release", and it names both routes (a token upload of retained files, and `release.yml` with `publish=true`) | exit 0 on the RR3 tree; exit 1 on the base `docs/releasing.md` (mutant: the old text restored in a scratch copy) |

## 9. Out of scope for this phase

- Any upload, tag, GitHub release, environment, publisher registration,
  workflow dispatch or announcement, and applying either patch.
- Choosing the route (RL-D5).
- `release.yml` and its pinned test.
- The milestone close (its own record and question sweep).

## 10. Size

About 150 dossier lines, 90 patch lines (two files), 20 changed lines in
`docs/releasing.md`, 15 test lines inside the patch (D2, D5), and about 120
record lines. The plan estimated about 250 record lines and 20 lines of
`releasing.md`.

## 11. Approval instrument

This prose. The inventory in §6.2 is the patch's scope. Its classification
can be checked against T5's output.

## Verification commands

- **V1**: T1 to T6.
- **V2**: both patch files are committed under `evidence/RR3/`, and none of
  their hunks is in the tree: every `PIN_FILES` file still names 0.1.0 and
  `RELEASED` is `{"0.1.0"}`.
- **V3** (r1), dated and read-only, against the fixed pre-milestone base
  `12daa5b7`:
  - `git diff 12daa5b7 HEAD -- .github` is empty.
  - `git diff 12daa5b7 HEAD -- docs/releasing.md` shows only M3's edits as D1
    rules, reviewed in V4.
  - Each remote listing is compared with the baseline O3/O5 observed:
    - environments `['github-pages']`;
    - `release.yml` runs: 0;
    - GitHub releases and remote tags: `v0.1.0` only;
    - PyPI releases `['0.1.0']`.
  - PyPI account-side publisher registration is named as not audited.
- **V4**: one Codex review of the diff.
- **V5**: `scripts/components_index.py changed --base origin/main` reports 0
  to fix.

## 12. Review dispositions (r1 to r2)

One reviewer, Codex (`gpt-6-sol`, xhigh, read-only, prompt on stdin), over r1.

| Finding | Disposition | Applied at |
|---|---|---|
| Q1 inventory misses the notes opening, `releasing.md`'s versionless wording, and the stated search | accepted, reproduced: the precise search gives 31 lines in 15 files | §3.1, §6.2 rows (r1) |
| Q2 F1 claims different bytes | accepted | F1 reworded |
| Q3 O8 and O15 actions missing | accepted | M1 §D 1a to 1d, 3(b) |
| Q4 D6's sentence names 0.2.0 | accepted | D6 (a) is versionless |
| Q5 T5 cannot fail | accepted | M4 script with an allowlist; T5 has a liveness run |
| Q6 V3 diffs against `origin/main` | accepted | V3 uses the fixed base `12daa5b7` and the O3/O5 baseline |
| Q7 one patch for two independent conditions | accepted | three patches (M2), D4 |
| Q8 nothing checks M3's meaning | accepted | T7 with a mutant |
