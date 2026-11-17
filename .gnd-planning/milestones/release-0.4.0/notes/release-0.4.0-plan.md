# Release 0.4.0

r2 plus the §12 close amendment, 2026-11-17. Milestone `release-0.4.0`, phase prefix `RV`.
The standard GND panel reviewed r1. Section 11 amends the r1 clauses below.
The plan gate records the review and the distinct delegated ruling.

Source: the owner's request of 2026-11-16 ("ok now can you create gnd version
0.4.0"), made right after the main CI repair (PR 207) left main's default lane
clean. Inspection baseline: main `cc4c8bf0` (the PR 207 merge). The
predecessor is [release-0.3.0](../../release-0.3.0/notes/release-0.3.0-plan.md).
This plan follows its phases and cites it instead of repeating it. Two things
changed after it: the version bump no longer re-records fixtures (issue 172,
`tests/support/recorded_version.py`), and `tools/release_text.py` makes the
post-publication page edits (issue 176). Plan authorship is not approval and
not publication authority.

**Phases RV1 to RV3 prepare a release and publish nothing.** AGENTS.md says
"Release preparation does not enable a production publisher." The upload, the
tag and the GitHub release form a publication stage. It runs only on the
owner's explicit request at that time (RV-D5).

## Completion predicates

The milestone is complete when, on main after merge:

1. The source version is 0.4.0, written once in `pyproject.toml`. `uv.lock`,
   the three plugin manifests and the release notes agree with it, and
   `tests/test_release_version.py` exits 0 (RV1).
2. Every tracked file that names 0.3.1 or 0.3.0, and every default-lane test
   whose result moves with the version, is listed before code from a grep
   inventory and a measurement (E1). Each one is classified as historical or
   stale and handled. E1 is expected to move no recorded byte because of
   `recorded_version.py`. If it moves any, the spec records each one and the
   owner rules before code (RV1). Opt-in lanes that do not run are listed as
   exclusions.
3. The release notes have one 0.4.0 section that describes every user-visible
   change on the candidate commit since the `v0.3.1` tag. They also say that a
   PyPI user upgrading from 0.3.0 gets the 0.3.1 section too, and there is no
   `Unreleased:` section for work the candidate contains (RV1, rechecked at the
   RV2 freeze).
4. A candidate wheel and sdist, built from a named main commit, install into a
   fresh environment outside the checkout and carry the items RV-D6 selects.
   The same probes are refused or absent on the published 0.3.0 (RV2).
5. `tests/test_release_acceptance.py` exits 0 over the retained candidate
   files, with its verbatim output recorded (RV2).
6. At the RV3 hand-over, a dossier states the candidate identity, the
   evidence, what was not measured and every owner action still needed. The
   `tools/release_text.py publish` invocation is prepared but not run (RV3).
7. No phase uploaded anything or created a tag, a GitHub release or the `pypi`
   environment, and no phase changed `.github/`. The close audits this with a
   `git diff` of `.github/` and dated read-only remote checks at baseline and
   at close: environments, `release.yml` runs, releases, remote tags with their
   peeled commits, and the PyPI simple index.
8. The owner has published (RV-D5). The served files are compared with the
   retained candidate, a fresh index install is exercised, and the
   post-publication page edits are on main.
9. Each phase has an approved spec, a record with the verbatim focused-gate
   output, and one independent reviewer. The close record disposes of every
   open question.

## 0. Binding design rules

Rules 1 to 8 of the predecessor plan §0 bind unchanged, with the version names
moved on. In short:

1. **Prepare, never publish.** No phase uploads to PyPI or TestPyPI. No phase
   dispatches `release.yml` with `publish=true`, creates a tag or a GitHub
   release, or edits `release.yml`, the `pypi` environment or a publisher.
2. **One home for the version**: `pyproject.toml`.
3. **No instruction names an unpublished version.** Install pins stay at 0.3.0
   until 0.4.0 is on PyPI. `tests/test_release_version.py` refuses the other
   order.
4. **Evidence belongs to exact bytes.** Rebuilding makes a new candidate.
5. **Carrying is shown by running** from the installed wheel, with a control
   on the published 0.3.0.
6. **Measure, don't assert.** E1 measures the bump before the spec says how it
   is handled.
7. **Frozen surfaces.** No phase edits `release.yml`, its pinned test or the
   dependency freeze.
8. **Stop rule (size).** A phase pauses for the owner once it passes 1.5 times
   its estimate.

Two of the six `project.md` standing rules apply here: rule 5 (one home for
the version and for the procedure) and rule 6 (measure). Rules 1 to 4 have no
new consumer of untrusted input, and each spec says so.

The structure guards of `project.md` (issue 171) are in every phase gate that
changes a file outside `.gnd-planning/`.

## 1. Scope, sources and authority

Authority comes from:

- the owner's request of 2026-11-16;
- AGENTS.md, `docs/releasing.md` and `docs/compatibility.md`;
- the predecessor plan and its close.

### Obligations harvested

Kinds: **O** observed in this session, **I** an inherited claim read from a
record, **P** a proposed target.

| ID | Obligation or fact | Kind | Source | Owner |
|---|---|---|---|---|
| V1 | Create GND version 0.4.0 | I | owner request, 2026-11-16 | RV1 to RV3; publication stage |
| V2 | The version is 0.4.0, a minor bump over the tag-only 0.3.1 | I | the request names it | RV1 |
| V3 | `pyproject.toml` declares 0.3.1. `RELEASED = {"0.1.0", "0.2.0", "0.3.0"}`, `TAGGED = {"0.3.1"}` | O | files at `cc4c8bf0` | RV1 |
| V4 | PyPI serves 0.1.0, 0.2.0 and 0.3.0 (six files). 0.4.0 is free. Published 0.3.0: wheel `143890ee…751b`, sdist `5e40d9e3…4c42` | O | PyPI simple index, 2026-11-16 | RV2 control pin; rechecked at freeze and before upload |
| V5 | Remote tags: `v0.1.0`, `v0.2.0` (peeled `7c0f4d0e`), `v0.3.0` (peeled `4c07c0e6`), `v0.3.1` (peeled `aff85c67`). Environments: `github-pages` only. `release.yml` has no runs | O | `git ls-remote --tags origin`, `gh api .../environments`, `gh run list` | predicate 7 baseline |
| V6 | 131 first-parent commits separate `v0.3.1` from main, and 206 separate `v0.3.0`. Under `src`, `pyproject.toml`, LICENSE and NOTICE, 539 files differ from `v0.3.0` (+48,626 / −900) | O | `git rev-list`, `git diff --shortstat` | RV1 notes |
| V7 | `docs/release-notes.md` has no `Unreleased:` section. Its newest section is 0.3.1, which covers the guarded-rule workflows (PR 184) and fixes up to PR 192. Nothing merged after the `v0.3.1` tag has a note | O | file; `grep -i literature` gives nothing | RV1-C3 |
| V8 | Merged after `v0.3.1` with possible user-visible effect: guarded-rule pages (PR 191); guarded-rule clauses GC1 to GC4 (PR 196: literal set membership, antecedent filters, disjunctive consequents); literature identity LI0 to LI2 (PRs 194, 197, 199 to 201: version-1 models for witness and why-not, the literature regression corpus); literature interop LX1 to LX4 (PR 202: include roots, flat re-entry, fixed reference catalogs, witness and replay over them); literature depth LD1 to LD3 (PR 203: time dimensions, exact decimal replay, reading fixtures); docs (PRs 205, 206); the main CI repair (PR 207: frontier and Phase 3 exclusions; no output change on the drifted goldens). PR 198 syncs dev-tools and ships nothing in the package | O | `git log --first-parent v0.3.1..cc4c8bf0`, `gh pr view` | RV1-C3 (reconciled per user-visible change, not per pull request) |
| V9 | PR 204 (aggregate COUNT certificates, `gnd witness-count` and `gnd replay-count`) is an open draft | O | `gh pr list` | RV-D2 |
| V10 | Version-bearing recorded outputs compare through `tests/support/recorded_version.py`, so a bump moves no recorded byte. The claim is untested for this bump | I | issue 172; memory of the 0.3.1 cut | E1 in RV1 |
| V11 | The post-publication page edits are `tools/release_text.py publish --date … --built … --profile …`, followed by hand-fixing the lines it lists until `check` is clean | I | `docs/releasing.md`; tool docstring | RV3, publication stage |
| V12 | Release acceptance keeps one negative control, against the release before the candidate. For 0.4.0 that is 0.3.0, which replaces the current control | I | memory of the issue-176 change; `tests/test_release_acceptance.py` | RV2 |
| V13 | The default lane at `cc4c8bf0` on beast-3 (six shards): 19,699 passed, 13 skipped, 0 failed, and the 2 known `test_public_optional` errors (uv 0.13.7 on beast-3, while CI pins 0.10.10) | O | this session's run, 2026-11-16 | RV1-C6 baseline |
| V14 | 0.3.0 was published by the session at the owner's explicit request (token in `~/.pypirc`, tag push, GitHub release). 0.3.1 was tag-only at the owner's request | I | `release-0.3.0/006-publication.md`; `docs/releasing.md` "Tag-only versions" | RV-D5 |
| V15 | `docs/compatibility.md`: record breaking changes and migration in the notes, confirm availability before freeze and upload, and never overwrite released files | I | file | RV1, RV2-C0, dossier |
| V16 | Package data added since 0.3.0 includes the literature examples (`src/gnd/examples/literature/…`) and the expense receipts example. No release test exercises them from an installed wheel | O | `git diff --stat v0.3.0 -- src/gnd/examples` | RV2-C4 |

`project.md` says to skip the component-index step, and this plan does. This
is a framework milestone, so a `gnd coverage` census does not describe it.

### Implementability sweep (author inspection, not review)

- **Inputs exist when needed.** RV1 needs only main. RV2 needs RV1 on main,
  plus a clean checkout. RV3 needs RV2's hashes, and the publication stage
  needs the owner. No phase needs a write credential.
- **Tools.** `uv build`, run as `release.yml` runs it. The acceptance run uses
  beast-3 with Python 3.11 and uv 0.10.10, as for 0.3.0.
- **Measurable.** Each predicate has a command or a diff, and predicate 4 has
  a negative control for each probe.
- **Not known at plan time.**
  - whether the bump moves any recorded byte (E1);
  - whether the literature and receipts examples are in the wheel and run from
    it (RV2).

### Conflicting clauses

| ID | Clause A | Clause B | Proposed resolution | Ruling |
|---|---|---|---|---|
| C1 | `project.md`: no `addopts` override in an ordinary gate | `docs/releasing.md`: acceptance runs with `-o addopts=''` | As RN-D8: the RV2 spec approval selects that one file and lane | RV-D7 |
| C2 | AGENTS.md: preparation does not enable a publisher | The request is to create a version, which ends in a publication | The phases prepare, and publication is a separate owner-run stage | RV-D5 |
| C3 | The 0.3.1 notes say "install it from the tag" | A PyPI user upgrading from 0.3.0 skips 0.3.1 | The 0.4.0 section says the 0.3.1 section applies to them as well | RV-D3 |

## 2. Contract proposal and product behavior

No GND command, report, schema or exit band changes. The product is the
package a user installs.

- **Release notes.** One `## 0.4.0 (prepared, not published)` section, with
  one block per user-visible change since `v0.3.1`. It opens with a line
  saying that PyPI users coming from 0.3.0 also get everything in the 0.3.1
  section (RV-D3). The order is guarded-rule clauses, literature identity,
  literature interop, literature depth, then other changes. RV1's spec writes
  the text from each milestone's close record and reference pages.
- **What "carries" means (RV2).** The proposed set for RV-D6 is four probes,
  run from the wheel installed outside the checkout:
  1. a guarded rule with a literal set (`in`) and an antecedent filter is
     validated and checked;
  2. `gnd compose` with a resolution file joins two include roots, and
     `gnd check --composition` reads the record;
  3. witness and replay over a fixed reference catalog: a changed catalog is
     refused with `ReferenceHashMismatch`;
  4. the packaged literature example's reference report reproduces.

  Each probe has two controls, and both are required. The availability control
  runs on the hash-pinned PyPI 0.3.0 wheel. The behavior control runs on the
  candidate:
  - a value outside the literal set is flagged;
  - a missing `same` decision is refused;
  - a changed catalog byte is refused;
  - a mutated literature population moves its report.

  RV2's spec writes each command in full, with its named inputs and its scratch
  directory.

## 3. Dependencies and artifact homes

```
RV1 ──> RV2 ──> RV3 ──> publication stage (owner) ──> close
```

| Artifact | Home |
|---|---|
| version | `pyproject.toml` |
| lock entry, manifests, notes | as the predecessor plan §3 |
| carries probes | `tests/test_release_acceptance.py` |
| candidate evidence, dossier | `.gnd-planning/milestones/release-0.4.0/evidence/` |
| retained candidate | `~/gnd-release/0.4.0/<short sha>/candidate/`, copied to beast-3 |
| procedure (normative) | `docs/releasing.md`, unchanged unless RV3 finds it stale |
| workflow, publisher, environment | unchanged |

## 4. Phases, deliverables, named criteria and inherited residuals

### RV1: candidate content

Spec: [phase-RV1-spec.md](phase-RV1-spec.md), a draft. Its E1 runs only after
the owner approves the spec.

- RV1-C1: `pyproject.toml`, the `uv.lock` entry and the three manifests carry
  0.4.0, and `uv lock --check` exits 0.
- RV1-C2: E1 and the grep inventory are in the spec before code, and each
  entry is classified and handled.
- RV1-C3: the notes read as §2. Every user-visible change in V8 has a note or
  a stated reason for none, shown in a reconciliation table in the record. A
  test fails when the 0.4.0 section lacks its literature block.
- RV1-C4: `docs/compatibility.md`, `docs/support.md` and the plugin page say
  0.4.0 is prepared and not published, and the install pins stay at 0.3.0.
- RV1-C5: `tests/test_release_version.py` and `tools/release_text.py check`
  exit 0.
- RV1-C6: the full default lane at the changed tree has no failure that V13
  lacks (beast-3, six shards).

### RV2: candidate build and installed acceptance

This is an outline. The spec is written once RV1 is on main.

- RV2-C0: before any build, the notes cover every change on the candidate
  commit, and 0.4.0 is still free on PyPI.
- RV2-C1 to C3: the build, a second build compared by hash, and acceptance
  over the retained files, as for predecessor RN2.
- RV2-C4: the probes of §2, each with its 0.3.0 control. The 0.3.0 control
  replaces the current one (V12).
- RV2-C5: `uvx --from <wheel> gnd --version` prints 0.4.0.
- RV2-C6: the observed profile is recorded, and no other profile is claimed.

### RV3: publication hand-over

This is an outline.

- RV3-C1: the dossier: candidate identity, results and what was not measured.
- RV3-C2: each owner action with its evidence: ownership, the availability
  recheck, the route, the tag, the GitHub release with its attachments, and
  any announcements.
- RV3-C3: the exact `tools/release_text.py publish` invocation, and the lines
  it is expected to leave for a person, recorded from a dry run on a scratch
  tree. It is not applied.

### Publication stage (owner acts; not a phase)

It runs only under RV-D5, and each step runs only on the owner's explicit
request at that time:

1. upload of the retained files;
2. the tag;
3. the GitHub release;
4. the served-file comparison and a fresh index install;
5. the pull request with the `release_text.py publish` edits.

### Milestone close

The close has a close record, a question sweep, a full default lane, and the
read-only remote checks of predicate 7.

### Obligation-to-phase map

| Obligations | Phase |
|---|---|
| V1, V14 | RV3, publication stage |
| V2, V3, V10 | RV1 |
| V6, V7, V8 | RV1-C3 |
| V4, V12, V16 | RV2 |
| V5 | predicate 7, close |
| V9 | RV-D2, RV2-C0 |
| V11 | RV3-C3 |
| V13 | RV1-C6, close |
| V15 | RV1, RV2-C0, RV3 |

## 5. Documentation, skill and compatibility surfaces

- RV1 edits `docs/release-notes.md`, `docs/compatibility.md`,
  `docs/support.md` and `docs/marketplace-plugins.md`.
- The pins in `README.md`, `docs/installation.md` and `docs/index.md` move at
  publication, by `release_text.py publish`.
- Skills: no text change.
- Plugins: the manifests move in RV1, so the plugin on main is 0.4.0 while
  PyPI still has 0.3.0 (risk R3).

## 6. Risks and required controls

| ID | Risk | Control |
|---|---|---|
| R1 | The bump moves recorded bytes after all | E1 first; RV1-C2 and C6 |
| R2 | A sibling change, such as PR 204, lands between RV1 and the freeze without a note | RV2-C0; RV-D2 |
| R3 | Main says 0.4.0 before PyPI has it | rule 3; the notes say "prepared, not published" |
| R4 | Candidate evidence is read as evidence for the published file | rule 4; the served-file comparison |
| R5 | The wheel lacks a literature or receipts data file, so an example works in the checkout and fails when installed | RV2-C4 probe 4 runs from the installed wheel |
| R6 | A probe also passes on 0.3.0 | the 0.3.0 control for each probe |
| R7 | 0.4.0 is taken by upload day | recheck at freeze and before upload |
| R8 | A phase eases a test by editing the workflow | rules 1 and 7; the close's `.github` diff |
| R9 | Main goes red again between RV1 and the freeze (as the 276 failures did) | RV2-C0 runs the full lane at the freeze commit |

## 7. Out of scope

- An upload, tag, GitHub release, `pypi` environment or publisher registration
  by a phase.
- Announcements.
- Dispatching the prepare job on GitHub, unless the owner asks.
- Configuring Trusted Publishing.
- A certification or recertification.
- Changing `release.yml`, its pinned test or the dependency freeze.
- New product behavior of any kind, including PR 204 unless RV-D2 says
  otherwise.

## 8. Execution, approval and review protocol

`auto=false`. Each phase runs these steps:

1. spec;
2. owner gate;
3. implementation;
4. focused gate;
5. one independent reviewer in a different tool, with the prompt on stdin;
6. refactoring review;
7. record;
8. commit on a topic branch and pull request.

The owner merges. The project's bar for plan review and close is the
maintained panel. RV-D0 asks which instrument reviews this plan, and until it
runs the plan reads as unreviewed.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| RV1 | `uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py --tb=short`; the structure guards; `uv run python tools/release_text.py check`; `uv run ruff check`; the full default lane on beast-3 | manifests; notes links; recorded-version fixtures |
| RV2 | `GND_CANDIDATE_DIR=... uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short` on beast-3 (Python 3.11, uv 0.10.10) | the prepare job (same file) |
| RV3 | `uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py --tb=short`; `release_text.py check` | `docs/releasing.md` links |
| close | full default lane, six shards on beast-3 | whole suite |

## 10. Owner decisions and open questions

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| RV-D0 | Which instrument reviews this plan? | One Codex reviewer, as for the three earlier release plans | The panel is the project's bar. It costs its budget and needs all six seats' credentials. An unreviewed plan stays labelled unreviewed |
| RV-D1 | Version | **0.4.0** (the owner's request, 2026-11-16) | -- |
| RV-D2 | What does the cut carry? | Main as it is at the RV2 freeze. PR 204 does not gate the cut: if it merges before the freeze it is in, with a note, and if not, it waits for 0.4.1 or 0.5.0 | Waiting for PR 204 delays the release by an unknown amount |
| RV-D3 | Notes shape | One 0.4.0 section for changes since `v0.3.1`, opening with a pointer to the 0.3.1 section for PyPI users coming from 0.3.0 | Folding 0.3.1 into 0.4.0 rewrites a tagged release's notes |
| RV-D4 | When do the install pins change? | At publication, through `release_text.py publish` | Moving them earlier names a file that does not exist yet, and the version test refuses it |
| RV-D5 | Publication route and ending | PyPI, by token upload of the retained files, as for 0.3.0. The milestone stays open through publication, and each owner act happens on its own request | A tag-only 0.4.0 (like 0.3.1) skips RV2's index checks and leaves PyPI at 0.3.0 |
| RV-D6 | Which features get an installed probe with a 0.3.0 control? | The four in §2 | Fewer probes leave the new examples unexercised from a wheel |
| RV-D7 | The `addopts` override for release acceptance | The RV2 spec approval selects that one file and lane | Without it, RV2 cannot run the acceptance that the procedure names |
| RV-D8 | Opt-in lanes (`evidence`, `census`, `ossie_oracle`, others) | Recorded as excluded, as for 0.3.0 | Running them costs lane time |
| RV-D9 | Run the prepare job on GitHub for an Ubuntu result? | Not unless the owner asks | Without it, only one profile is observed |

Open question carried: whether the GitHub release attaches the wheel, the
sdist and `SHA256SUMS.txt`, as v0.3.0's did.


## 11. Amendments after the standard panel, 2026-11-17

These rulings replace the corresponding r1 language above. The previous
wording is retained at commit `9458c0a1`. The [panel report](../evidence/plan-r1/PANEL-REVIEW.md)
accounts for every retained concern.

- **§8 and RV-D0.** The owner's `process-milestone release-0.4.0 auto`
  delegates milestone approval rulings. The owner selected the standard GND
  panel for the plan and the eventual close. The per-phase diff uses an
  independent reviewer in a different tool. Merge and each publication act
  retain separate owner authorization.
- **Predicate 2, §0 rules 3 and 6, and RV1-C2.** Install instructions pin a
  published runtime. The source version, plugin manifests and prepared-state
  pages may describe 0.4.0. The first RV1 spec ruling approves the scratch E1
  protocol. Append the results, classify each inventory entry as historical,
  retained install pin, recorded output or stale, and rule on the measured
  handling in a second digest-bound spec ruling before candidate edits.
  Include the version-bound distribution test as an RV2 carryover outside E1.
- **Predicate 3 and RV1-C3.** Reconcile the candidate's changes against
  `v0.3.1` and check the `v0.3.0..v0.3.1` range against the existing 0.3.1
  notes. Put any missing user-visible carryover in the 0.4.0 section and
  preserve the tagged section. Record both reconciliations.
- **§2, predicates 4–5, RV2-C4 and RV-D6.** Retain the four proposed probes
  and add an installed expense-receipts probe. The catalog happy path must
  create a witness and verify it through replay on the unchanged catalog.
  The mutant must exercise the typed catalog mismatch. Compare the
  literature report against its committed reference, using the existing
  recorded-version helper for version-bearing output. Run the receipts
  walkthrough from installed resources, compare findings against the
  reference page, and verify the documented missing-decision refusal.
  Each availability control asserts the feature-specific exit and diagnostic
  or verifies the installed resource is absent. Guarded rules are absent in
  0.3.0, so candidate mutations distinguish the new clause semantics.
  Keep prior positive probes as regressions, migrate the 0.3.0 candidate
  version guard and retire the 0.2.0 availability control. Obtain full 0.3.0
  hashes from RN2's retained checksum file and verify the wheel served by
  PyPI. Record the overridden default exclusions alongside the
  acceptance-only command. The distribution test is excluded by the default
  filter, so its selected run supplies the acceptance evidence.
- **§3, §4 and §9, RV2-C0 through C3 and R9.** Land the acceptance probes on
  main through an owner-merged PR before freezing. Build and run from the
  same named main commit containing those probes. Before the first build,
  run the six-shard default lane at the freeze commit and compare against
  V13. Route missing sibling notes through an RV2 preparation PR and rerun
  RV1-C5 before freezing. For acceptance, reuse RN2's beast-3 pinned uv
  binary setup, record the actual Python and uv versions, and verify
  `SOURCE_COMMIT` and `SHA256SUMS` at the receiving host immediately before
  running against the copied files. The default-lane baseline uses its
  separate observed uv profile.
- **Predicates 7–8, RV3 and the publication stage.** Preserve dated
  read-only snapshots at baseline, hand-over before publication, and close.
  Record all prior tag targets, including the lightweight v0.1.0 commit.
  Expect the authorized 0.4.0 tag, release and two matching PyPI files.
  Expect zero preparation workflow changes, publisher environments or
  release workflow runs attributable to this milestone. Document unrelated
  activity independently. Snapshots show remote state. Dated authorization
  and execution receipts establish when the publication acts occurred.
  Tag the exact accepted `SOURCE_COMMIT` and verify the peeled remote target.
  RV-D10 selects the retained wheel, sdist and checksum file as release
  attachments and verifies their identities. RV3 inventories every
  prepared-state marker in the notes, compatibility, support and plugin pages
  and checks the scratch edit. A numbered publication record binds the
  served-file and index-install evidence, final page PR and publication
  receipts. The milestone close panel reviews that evidence.
- **Remaining decisions.** RV-D2 through D4 and D7 through D9 follow the
  proposed readings, subject to the controls above. RV-D5 selects the PyPI
  route and keeps the milestone open through publication. A tag-only route
  would require an amendment to the completion predicates. PR 204, if
  merged at the freeze, receives a note. The RV3 dossier names any resulting
  count-certificate feature that lacked installed coverage.


## 12. Close repairs, 2026-11-17

The closing record binds this amendment. The prior plan bytes remain at
SHA-256 `e9828d47fcf6429f85a9869e29972d75e8efb706dd5d2e0d0f0fb6062b3be7ed`
in the history preceding the close branch.

- V10 and the RV1 prediction that version-aware comparisons would all remain
  green were refuted by E1. The [measured gate](../003-RV1-implementation-gate.md)
  records 37 failures and twelve generated outputs that changed in scratch.
  The [RV1 record](../005-phase-RV1.md) binds the comparison repairs. Committed
  example artifacts retained their bytes.
- RV1's draft outline named LI0–LI2 and LD1–LD3. The
  [tag-range reconciliation](../evidence/RV1/notes-reconciliation.md) identified
  LI3–LI5 and LD4–LD5 as part of the frozen source. The published notes cover
  all of them. The version inventory now identifies the prepared-state
  guidance carried through RV3 and changed in the publication PR.
- The proposal's four probes became five under §11 and the RV2 spec. Four
  parametrized test functions exercise them because composition and catalog
  share one function. The final accepted suite has 23 cases across both
  wheel origins and includes the wrong-source control added after review.
- The publication text checker missed the receipts wording. RV1 carried the
  observed defect to RV3. The [rehearsal](../evidence/RV3/scratch-verification.txt)
  supplies a negative marker control and checks the supplemental patch.
  PR 211 merged those exact publication edits after the served-file check.
- The shared-tool lint baseline was 188 findings despite the project rule's
  historical zero claim. The [RV1 checkpoint](../004-RV1-verification.md)
  reproduced the exact findings on the base. This milestone preserved them.
  The close sweep assigns maintenance to the dev-tools source owner.

The owner separately authorized the publication actions and PR 211 merge,
then requested this milestone close. The close standard panel supplies
independent advisory evidence. Delegated acceptance retains the bounded
platform profiles, baseline setup errors, and the explicitly excluded lanes.
