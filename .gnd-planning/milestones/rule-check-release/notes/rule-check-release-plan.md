# Rule-check release

r2, 2026-11-07. **Approved by the owner at the plan gate on 2026-11-07
("Approve r2"; [plan-gate record](../001-plan.md)); approves no phase spec.** r1 (sha256
`52797ddb…4f034`, commit dbf98447) was reviewed by one reviewer, Codex
(disposition `revise`, 11 findings; [record](../evidence/plan-review-r1/codex-review.md));
§11 disposes each. **r2 repairs r1 and carries no review opinion of its own**;
it was not re-reviewed. The owner ruled every decision RL-D0 to RL-D9 as
proposed (§10); that is not the plan gate. No phase has a spec approval; no
code is written. `auto=false`. Milestone:
`rule-check-release`. Phase prefix `RR`.

Source: GitHub issue 118, GR-D7, "a release that carries the rule-check
flags", filed by the same development tool that filed the rule-check-adoption
requests. Inspection baseline: main at `12daa5b7` (2026-11-07). Plan
authorship is not approval and not publication authority.

**This milestone prepares a release. It does not publish one.** AGENTS.md:
"Release preparation does not enable a production publisher." Uploading to
PyPI, tagging, creating a GitHub release, creating the `pypi` environment and
registering a PyPI publisher each need a separate, explicit owner request
(§7). The milestone ends with a candidate, its evidence and a hand-over
dossier; issue 118 stays open until a published release is verified.

## Completion predicates

The milestone is complete when, on main after merge:

1. The source version is the number the owner ruled (RL-D1), written once in
   `pyproject.toml`; `uv.lock`, the three plugin manifests and the release
   notes agree with it, and a test fails if any of them drifts (RR1).
2. Every tracked file that names the old version, and every default-lane
   test whose result moves with the version, is listed from a grep inventory
   and a measurement before code, and each is classified (historical or stale)
   and handled by a ruled method (RR1, RL-D9). The opt-in lanes (`evidence`,
   `census`, `distribution`) are not measured by E1; the owner ruled them
   excluded (2026-11-07, RR1 spec D6), so the record lists them as exclusions
   and `tests/test_public_distribution.py` runs at RR2, not RR1 (review P2).
3. A candidate wheel and sdist built from a named main commit install into a
   fresh environment outside the checkout and carry every item of issue 118:
   report version 15, `--rule-ids`, `--baseline`, `--allow-vacuous`, the
   `remedy` field, the acyclic extent, and `source: tool-output` with
   `producer`. The same probes fail or are absent on the published 0.1.0
   (RR2).
4. The existing release acceptance (`tests/test_release_acceptance.py`) passes
   over the retained candidate files, with its verbatim output recorded (RR2).
5. A hand-over dossier states the candidate identity, the evidence, what was
   not measured, and every owner action still needed before publication; the
   post-publication documentation patch is prepared and not applied (RR3).
6. No workflow, environment, repository setting or PyPI configuration was
   changed to enable publication, and nothing was uploaded (all phases). What
   the milestone can audit is stated: repository bytes by `git diff` of
   `.github/` and `docs/releasing.md`'s procedure steps against the base;
   remote state by dated read-only checks at the close (`gh api
   repos/vasiloglou/gnd-public/environments`, `gh run list --workflow
   release.yml`, `gh release list`, the public PyPI JSON listing of versions),
   compared with the baseline of O3 and O5. They need an authenticated `gh`
   with read access and public PyPI; PyPI account settings (publisher
   registration) are not readable by them and are named as not audited
   (review P6).
7. Each phase has an approved spec, a record with verbatim focused-gate
   output and one independent reviewer; the close record disposes every open
   question and leaves issue 118 open with its reason.

## 0. Binding design rules

Inherited from rule-check-adoption §0 where they still bind; restated here:

1. **Prepare, never publish.** No command in any phase uploads to PyPI or
   TestPyPI, dispatches `release.yml` with `publish=true`, creates a tag or a
   GitHub release, or edits `release.yml`, the `pypi` environment or a
   publisher registration. A phase that needs one of these stops for the
   owner.
2. **One home for the version.** `pyproject.toml` is the only place a version
   is written (`gnd/__init__.py`, D-02). Every other site derives from it or
   is checked against it by a test; a new literal copy is a defect.
3. **No instruction names an unpublished version.** README and installation
   text that tells a user to install `get-nick-done==X` change only when X
   exists on PyPI (RL-D4). Release notes call the candidate unpublished until
   then.
4. **Evidence belongs to exact bytes.** A result about a candidate names the
   source commit and the file hashes. Rebuilding makes a new candidate and
   repeats the affected checks (`docs/releasing.md`); an older result is not
   carried over.
5. **Carrying is shown by running, not by reading the changelog.** Each item
   of issue 118 is exercised from the installed wheel, with a negative control
   on the published 0.1.0.
6. **Measure, don't assert.** The size of the version bump's effect (§1, O9)
   is measured before the design says how to handle it.
7. **Frozen surfaces.** The workflow file, its pinned test
   (`tests/test_release_preparation.py`) and the dependency freeze are not
   edited; a change to one is its own owner ruling.
8. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

The six standing design rules of `project.md` are bound per phase spec; for
this milestone only rule 5 (normative prose has one home: the version, and
`docs/releasing.md` as the home of the procedure) and rule 6 (measure) have
subjects. Rules 1 to 4 (totality, input cap, validation order, one policy walk)
have no new consumer of untrusted input to bind; each spec says so in a
sentence.

## 1. Scope, sources and authority

Authority: the owner's request relayed to this planning session
(2026-11-07), issue 118, and AGENTS.md.

### Obligations harvested

Evidence kinds: **O** observed in this session, **I** inherited claim read from
a record, **P** proposed target.

| ID | Obligation or fact | Kind | Source | Owner |
|---|---|---|---|---|
| O1 | A PyPI release of `get-nick-done` carrying report version 15 (`--rule-ids`, `--baseline`, `--allow-vacuous`, `remedy`, acyclic extent) and `source: tool-output` with `producer` | I | issue 118 | RR1-RR3 prepare; publication out of scope |
| O2 | Release preparation does not enable a production publisher; owner approval precedes implementation; PR only | I | AGENTS.md | §0 rule 1 |
| O3 | PyPI lists exactly one version, 0.1.0 (wheel and sdist uploaded 2026-10-12); 0.2.0 and 0.1.1 are free | O | `pypi.org/pypi/get-nick-done/json`, 2026-11-07 | RR3 rechecks on the day |
| O4 | 0.1.0 was published by an owner-authorized token upload; Trusted Publishing was shipped as a workflow but its PyPI identity and environment were never validated | I | `public-launch/010-public-launch-close.md` lines 81-83 | RR3 dossier (route is the owner's, RL-D5) |
| O5 | GitHub environments of the repository: only `github-pages`; no `pypi` environment; `release.yml` has no recorded run | O | `gh api repos/vasiloglou/gnd-public/environments`; `gh run list --workflow release.yml` | RR3 dossier; not changed here (rule 1) |
| O6 | `release.yml` prepares (build wheel and sdist, rebuild a comparison wheel from the sdist, SHA256SUMS, run `tests/test_release_acceptance.py` over the retained files) and, only with `publish=true` on main, uploads the retained files and then compares served files | O | `.github/workflows/release.yml` | RR2 reproduces the prepare steps locally |
| O7 | The workflow rebuilds on its own runner, so the files a workflow publication uploads are not the local candidate's bytes | O | `release.yml` (`prepare` job feeds `publish` within one run) | RR2 states the limit; RL-D5 |
| O8 | `docs/releasing.md` requires, before production enablement: package ownership and version availability, repository visibility and history review, target-only release authority, trusted-publishing identity, protected environment; after publication: compare served files, install, run the examples | I | `docs/releasing.md` | RR3 dossier |
| O9 | The version is read live into artifacts (`resolve_version()` feeds `gnd_version` in extract, discover, synth, measure, fidelity, review, codegen and coverage outputs); 55 tracked files outside planning and the lock contain the string `0.1.0`: 16 rf1-pins goldens, 13 under `docs` (installation, index, marketplace-plugins, compatibility, development/candidate, pyrel-apps, three how-to and three tutorial pages; review P3), `README.md`, 3 under `tests`, plugin manifests, retained fixtures. **Pre-measurement (scratch copy, 2026-11-07):** with only the version set to 0.2.0 (pyproject and the three manifests) and the environment re-synced, 21 of the 656 test files, chosen because they read those fixtures (715 cases), gave 12 failures in four files (`test_object_type_description.py` 4, `test_fidelity_stub_gate.py` 1, `test_public_extract_controls.py` 5, `test_public_measurement_publication.py` 2); the same four files on the same copy at 0.1.0 passed 85 of 85. The other 635 files were not run | O | `grep`, `src/gnd`, scratch probe | RR1 experiment E1 (the full lane, to complete the list) |
| O10 | Three test files assert the literal `0.1.0`: `tests/test_public_distribution.py` (lines 250, 255, 286, 331), `tests/test_induced_provenance.py`, `tests/test_fidelity_payload.py` | O | `grep tests` | RR1 (the last two to be classified by E1: a fixture's own value or the live one) |
| O11 | `tests/test_marketplace_plugins.py` requires the Claude and Codex plugin manifests to carry `pyproject` version (mutation case `999.0.0`) | O | test file lines 22-29, 54-71 | RR1 |
| O12 | `uv.lock` records `get-nick-done` as editable at `0.1.0` | O | `uv.lock` line 100 | RR1 |
| O13 | `docs/release-notes.md` opens "The development package version remains 0.1.0. Publishing these unreleased changes requires a separate release decision." and holds twelve `Unreleased:` sections, from "opt-in incremental evaluation (2026-10-20)" to "unattended growth procedure (2026-11-06)"; 526 commits separate main from the `v0.1.0` tag | O | file; `git log v0.1.0..HEAD` | RR1 |
| O14 | `README.md:43` and `docs/installation.md` (two places) tell users to install `get-nick-done==0.1.0`; `docs/compatibility.md:3` says "Current 0.1.0 metadata is provisional"; `docs/support.md` profile rows say the package awaits final sign-off | O | files | RR1 (compatibility, support), RR3 patch (pins) |
| O15 | `docs/compatibility.md`: record breaking changes and migration instructions in release notes; confirm ownership and an available version before candidate freeze; never overwrite released files | I | file | RR1, RR3 |
| O16 | The prepare job's acceptance test needs `GND_CANDIDATE_DIR`, the opt-in `distribution` lane, `-o addopts=''`, a git-tracked `HEAD` (`git archive HEAD`) and, on macOS, `sandbox-exec` | O | `tests/test_release_acceptance.py` | RR2 |
| O17 | `project.md`: "Do not override `addopts` or use `-m` to bring the ... distribution ... lanes into an ordinary gate" | I | `project.md` | conflict C1, §10 RL-D8 |
| O18 | rule-check-adoption is closed, RC1-RC6 on main; its close names issues 111-117 and 119 as follow-ups, now milestone rule-check-followups | I | `rule-check-adoption/012-milestone-close.md`; `rule-check-followups/README.md` | RL-D2 |
| O19 | rule-check-followups FU2 (`Population` header integrity, issues 115 and 116) and FU3 (acyclic extent over derived fact types, issue 119) change behavior of two features issue 118 lists; FU5 retires shims "after the first public release" (its FD5) | I | `rule-check-followups-plan.md` §4, §10 | RL-D2 |
| O20 | Every milestone in flight adds an `Unreleased:` section to `docs/release-notes.md` | O | file history | R2 (merge conflicts), RL-D3 |
| O21 | Full-suite comparison practice: `close-shards.sh` on beast-3 (present at `~/close-shards`), six round-robin shards, merge base vs closing tree; two pre-existing uv-pin errors | I | `rule-check-adoption/012-milestone-close.md`; `ssh beast-3 ls ~/close-shards` | RR1 gate, close |
| O22 | Component index: `infra.version` (`resolve_version`) is the one version resolver; this milestone builds no new capability. `components_index.py review` printed 180 leads in 10 groups and 304 of 306 modules assigned (two without a component: `checker/_composed.py`, `model/_unattended.py`); it prints leads to look at, not stale entries, so no index-review offer is made | O | `scripts/components_index.py` | none |

### Implementability sweep (author inspection, not review)

- **Inputs exist when a phase needs them.** RR1 needs only main. RR2 needs
  RR1 on main and a clean tracked checkout (`git archive HEAD`). RR3 needs
  RR2's hashes. No phase needs PyPI write access or a write credential; the read-only remote checks of predicate 6 use an authenticated `gh` and the public PyPI listing.
- **Tools meet the rules.** `uv build` is used exactly as `release.yml` uses it
  (uv 0.10.10 is the pinned version; the local uv version is recorded by RR2
  and a difference is stated). The `distribution` lane is selected by the
  spec, not by habit (C1).
- **Partitions and budgets agree.** The version bump can move recorded
  bytes. The pre-measurement of O9 shows retained goldens and digests that
  embed the live version go red on a bump (12 cases, 4 files, of the 21 files
  tried). The frozen-variants rule of rule-check-adoption concerns report
  variants, not a version string, but a retained golden compared with live
  output fails either way. E1 over the full lane decides the list, not argument.
- **Measurable.** Each completion predicate has a command or a diff as its
  result; the not-measurable items are named in §10 and §7.
- **Falsifiable end to end.** Predicate 3 is the milestone's central claim and
  has a negative control on 0.1.0 for every item.

### Conflicting clauses

| ID | Clause A | Clause B | Proposed resolution | Ruling needed |
|---|---|---|---|---|
| C1 | `project.md`: no `addopts` override or `-m` to bring the distribution lane into an ordinary gate | `release.yml` and `docs/releasing.md`: acceptance is `pytest -o addopts='' tests/test_release_acceptance.py` over retained files | Release acceptance is not an ordinary phase gate; the owner's approval of the RR2 spec is the explicit selection of that one file and lane. Nothing else overrides `addopts` | RL-D8 |
| C2 | `docs/compatibility.md`: confirm version availability "before candidate freeze" | Availability is time-dependent; PyPI could change before upload | Observe at plan time (O3), again at the RR2 candidate freeze (RR2-C0) and in the dossier; the owner's later upload request requires one more check immediately before any upload | none (RR3) |

## 2. Contract proposal and product behavior

No GND command, report, schema or exit band changes. The product behavior of
the milestone is the package a user installs.

- **Version.** Proposed `0.2.0` (RL-D1): a new minor of a 0.x line that adds
  new report versions and many options. `0.1.1` would claim a patch.
- **Release notes.** One section for the new version, opening with the
  rule-check items of issue 118, the earlier `Unreleased:` sections kept
  beneath as dated subsections, and a status line "prepared, not published"
  that publication changes (RL-D3).
- **What "carries" means (RR2).** From a wheel installed in a fresh
  environment outside the checkout, with a model and populations written in
  the test's own scratch directory:
  1. `gnd check M P --rule-ids --format json` writes `schema_version` 15, each
     verdict with `address`, `addressing` and `remedy`;
  2. `--baseline BASE` marks each violation `new` or `standing`, exit 1 only
     for new must-hold violations;
  3. `--allow-vacuous` changes the exit of an otherwise vacuous report as
     `docs/reference/rule-check-report.md` says;
  4. an `acyclic` failure lists the strongly connected edges in its extent;
  5. a population with `source: tool-output` and `producer` loads and checks,
     and `producer` without `tool-output` is refused.
  Expected values are copied from the rule-check-adoption phase records
  (RC1-RC5) and the reference page, not from the output being tested. Each of
  the five probes has two controls, so it separates behavior from mere option
  availability (review P5): (i) availability: on the PyPI 0.1.0 wheel the
  option is refused (exit 2; **corrected 2026-11-08, RR2 spec §13: measured exit 64**, `unrecognized arguments`), which proves only that the flag is new; (ii)
  behavior: a mutant of the candidate that reaches the same code with the
  feature removed or changed (a model without a declared `remedy` or id gives
  `null` and the position address; a baseline file that lists the violation
  gives `standing` where an empty one gives `new`; a ring with a disjoint added
  cycle leaves the extent rows unchanged; `producer` with `source: fixture` is
  refused), and, where the 0.1.0 default output is comparable (report version
  of a plain `gnd check`, population loading without `source`), a comparison
  with it. Each field (`schema_version`, `address`, `addressing`, `remedy`,
  `novelty`, extent edges) has its own expected value.
- **Install forms.** The local form of dev-tools' `uvx --from
  get-nick-done==<version>` is `uvx --from ./get_nick_done-<v>-py3-none-any.whl
  gnd --version`. The index form cannot be tried before publication; the
  dossier says so.

## 3. Dependencies and artifact homes

```
RR1 ──> RR2 ──> RR3 ──> close
 ^
 └ RL-D1 (version), RL-D9 (how moved bytes are handled, after E1)
RR2 starts when the content RL-D2 selects is on main.
```

| Artifact | Home |
|---|---|
| version | `pyproject.toml` `[project] version` (sole home) |
| lock entry | `uv.lock`, regenerated by `uv lock` |
| plugin manifests | `.claude-plugin/plugin.json`, `.codex-plugin/plugin.json`, `.claude-plugin/marketplace.json` |
| release notes | `docs/release-notes.md` |
| procedure (normative) | `docs/releasing.md`; the dossier cites it |
| version consistency test | new `tests/test_release_version.py` |
| carries test | `tests/test_release_acceptance.py` (new test using its `installed` fixture; the prepare job already runs this file) |
| candidate evidence and dossier | `.gnd-planning/milestones/rule-check-release/evidence/` |
| post-publication patch | `evidence/post-publication.patch`, not applied |
| workflow, publisher, environment | unchanged |

## 4. Phases, deliverables, named criteria and inherited residuals

### RR1: Candidate content (about 15 config lines, 60 test lines, 200 notes lines; fixtures per E1)

Spec: [phase-RR1-spec.md](phase-RR1-spec.md), draft r3, awaiting its own owner gate (RL-D1 and RL-D9 are ruled; the spec is not approved).

- RR1-C1: `pyproject.toml` carries the ruled version; `uv lock --check` passes
  and the three manifests carry it.
- RR1-C2: `tests/test_release_version.py` fails for each of four mutants
  (pyproject, lock entry, one manifest, release-notes heading) and passes on
  the tree.
- RR1-C3: no test file names the old version as a literal of its own, except
  the published-versions record `RELEASED` that `tests/test_release_version.py`
  holds on purpose (historical data, exempt; RR3's patch updates it, review
  P4); `tests/test_public_distribution.py` reads the version from
  `pyproject.toml`.
- RR1-C4: E1's measured list of moved default-lane results, plus the grep
  inventory of tracked files naming the old version, is in the spec before
  code; each entry is classified and handled by the ruled method. The claim is
  scoped to what the inventory and E1 cover; unselected opt-in lanes are named
  exclusions (review P2).
- RR1-C5: release notes read as in §2; `docs/compatibility.md` and
  `docs/support.md` state what is true (candidate, not signed off, profiles
  unmeasured). A test, not a reading, gates it: while the version is not in
  `RELEASED`, the version's notes heading contains "not published" and
  `docs/compatibility.md` says so; a mutant heading without it fails (review
  P10).
- RR1-C8: `docs/marketplace-plugins.md` tells a plugin user, while the plugin
  is newer than the published runtime, to install the runtime from the
  repository at a commit (the route the tutorials already give) until
  publication (review P11).
- RR1-C6: the full default lane at the bumped tree has no failure the merge
  base lacks (beast-3, six shards).
- RR1-C7: README and installation pins unchanged (rule 3), with a test or a
  recorded reason that makes the choice visible.

### RR2: Candidate build and installed acceptance (about 60 test lines; no source)

Spec: outline only; written after RR1 merges and RL-D2 is ruled. **Update (2026-11-08):** RR2's draft spec is [phase-RR2-spec.md](phase-RR2-spec.md), written once FU3 reached main and before RR1 merged; its D1 asks the owner which commit is the candidate, given PR 125 is unmerged. **Update (2026-11-08):** RR2 is implemented and recorded ([003-phase-RR2.md](../003-phase-RR2.md)); the candidate is main `7c0f4d0e`.

- RR2-C0: before any build, the notes of every change merged since RR1
  (FU2 and FU3 included) are reconciled into the version's section by a docs
  commit, so the candidate commit carries no `Unreleased:` section for work the
  candidate contains (review P1); the version's availability on PyPI is
  rechecked at this freeze (review P7, C2).
- RR2-C1: from `git archive` of the named main commit, the two `uv build`
  commands of `release.yml` produce wheel, sdist and comparison wheel;
  SHA256SUMS verifies; the tool versions are recorded.
- RR2-C2: a second independent build is compared by hash (reproducibility is
  measured; a difference is explained, RL-D7).
- RR2-C3: `GND_CANDIDATE_DIR=... uv run pytest -q -o addopts=''
  tests/test_release_acceptance.py --tb=short`: verbatim summary line.
- RR2-C4: the five "carries" probes of §2 from the installed wheel, each field
  with its own expected value and each probe with both controls of §2 (a
  0.1.0 availability control and a candidate-behavior mutant); the probes live in
  `tests/test_release_acceptance.py` so every later prepare run repeats them.
- RR2-C5: `uvx --from <wheel>` form works; limits recorded.
- RR2-C6: observed profile (OS, Python, uv) recorded; no other profile is
  claimed (RL-D6).
- RR2-C7: the hidden-input check: the test run does not read the source
  checkout (the file's own sandbox on macOS).

### RR3: Publication hand-over (about 250 record lines, `docs/releasing.md` edits of about 20 lines)

Outline only.

- RR3-C1: the dossier lists the candidate identity (commit, hashes, tool
  versions), results, and what was not measured (index install, Ubuntu,
  Trusted Publishing, TestPyPI, external user trial).
- RR3-C2: the dossier lists each owner action before publication with the
  evidence that it is still open (O3 to O5, O8, O15): ownership, version
  availability recheck, route (token as for 0.1.0, or Trusted Publisher with
  the `pypi` environment), tag and GitHub release, announcements.
- RR3-C3: the post-publication patch exists as a patch file and is not
  applied. It covers every instruction publication makes stale, found by a grep
  at RR3 time for `0.1.0` and for "next release" / "newer than the 0.1.0
  release" over `README.md` and `docs/` and classified hit by hit (historical
  or stale): the pins in `README.md`, `docs/installation.md`, `docs/index.md`
  and `docs/marketplace-plugins.md`; the checkout-until-next-release
  instructions in `docs/pyrel-apps.md`, three tutorials and three how-to pages;
  the compatibility sentence; the release-notes status; the support rows; the
  `v0.1.0` sentence in installation; and the `RELEASED` record in
  `tests/test_release_version.py`, with a mutant showing the pin test fails
  without that edit (review P3, P4).
- RR3-C4: `docs/releasing.md` has its stale phase wording ("After Phase 3
  accepts...") replaced by the current procedure and states the two
  authorized routes conditionally (a token upload as for 0.1.0, or the
  workflow with a validated Trusted Publisher and the `pypi` environment),
  configuring and invoking neither. This is a normative edit and is proposed
  for the RR3 spec's owner gate, not assumed (review P8);
  `tests/test_release_docs.py` passes.
- RR3-C5: the served-file check and the post-publication commands are listed
  once, citing the workflow's step rather than copying it.

### Milestone close (not a feature phase; about 100 record lines)

Close record; question sweep; full default lane against the merge-base record;
issue 118 left open with the reason "prepared, not published"; the owner's
publication request, if made, is recorded as a new decision, not as part of
this close.

### Obligation-to-phase map

| Obligations | Phase |
|---|---|
| O1 | RR2-C4 (carries), RR3 (hand-over); publication: none |
| O2, rule 1 | every phase; the close's no-change diff (R6) |
| O3, O5, O8, O15 | RR3 |
| O4, O7 | RR3-C2; RL-D5 |
| O6, O16, O17 | RR2; C1 |
| O9, O10, O11, O12 | RR1 |
| O13, O14 | RR1 (notes, compatibility, support), RR3 (pins) |
| O18, O19, O20 | RL-D2; risk R2 |
| O21 | RR1-C6, close |
| O22 | none (no new capability) |

## 5. Documentation, skill and compatibility surfaces

- `docs/release-notes.md`, `docs/compatibility.md`, `docs/support.md`: RR1.
- `docs/releasing.md`: RR3-C4.
- `README.md`, `docs/installation.md`: unchanged until publication (rule 3);
  patch prepared in RR3.
- Skills: no text change. The packaged skills' own versions (for example a
  rendered `skill_version` in fixtures) are separate from the package version
  and are classified by E1, not edited by assumption.
- Plugins: the manifests change in RR1 (O11). A user who installs the plugin
  from `main` sees plugin version 0.2.0 while PyPI still has 0.1.0; skills on
  `main` already name options the 0.1.0 runtime lacks, but the plugin-versus-
  runtime version mismatch that `docs/marketplace-plugins.md` tells users to
  avoid is new; RR1-C8 gives plugin users the repository-commit route until
  publication (risk R3, review P11).

## 6. Risks and required controls

| ID | Risk | Control |
|---|---|---|
| R1 | A bump moves retained or golden bytes (`gnd_version` in 16 goldens and other fixtures; E1 measured 47 failures, RR1 spec §12 and §13) and the suite goes red in places unrelated to the release | E1 measures first; RL-D9 chose the method (split (a)+(b)); RR1-C4 and C6 |
| R2 | `docs/release-notes.md` conflicts with every sibling milestone that adds an `Unreleased:` section | RR1 rebases onto main immediately before its PR; after it merges, sibling work adds a fresh `Unreleased:` section above the version's section, and RR2-C0 folds the sections of every change the candidate contains into the version's section before the build; the plan records this for sibling sessions |
| R3 | Main carries version 0.2.0 and plugin manifests at 0.2.0 before PyPI has it | rule 3 keeps install text honest; release notes say "prepared, not published"; RL-D2 can shorten the gap |
| R4 | The candidate's evidence is read as the published file's evidence | rule 4; O7 stated in the dossier; the served-file comparison after publication is the identity that counts |
| R5 | The probes pass because they cannot distinguish releases | 0.1.0 negative control per probe (RR2-C4) |
| R6 | A phase quietly enables publication (for example by editing the workflow to ease a test) | rule 1, rule 7; the close diffs `.github/` and the procedure steps of `docs/releasing.md` against the base and runs the dated read-only remote checks of predicate 6; account-side publisher registration is not auditable and is said so |
| R7 | The version is claimed free but is taken by publication day | C2 recheck in the dossier |
| R8 | The sandboxed acceptance run cannot run on this machine | RR2 records the exact refusal; the run moves to beast-3 or the owner dispatches the prepare job (RL-D6) |

## 7. Out of scope

- Uploading anything to PyPI or TestPyPI; creating a tag, a GitHub release or
  the `pypi` environment; registering a PyPI publisher; dispatching
  `release.yml` with `publish=true`; announcements. Each needs a separate,
  explicit owner request (AGENTS.md; `project.md`).
- Dispatching the prepare job on GitHub with `publish=false` is allowed only
  if the owner asks for it at that time (RL-D6); this plan does not run it.
- dev-tools' installation guide and runner (their repository).
- GR-D4 (issue 95), GR-T17 (issue 104), the rule-check-followups issues, and
  any other milestone's code.
- Changing `release.yml`, its pinned test or the dependency freeze.
- A certification or recertification (not requested).
- Retiring shims after the release (FU5's decision, its own phase).

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implement, focused gate, one
independent reviewer in a different tool (Codex, prompt on stdin), refactoring
review, record, commit on `claude/rule-check-release`, PR. Merge is the
owner's. The plan-review bar is the maintained panel (`project.md`); RL-D0
asks which instrument reviews this plan. The close is held to the same bar.
Phase specs use the provenance tags `(p2)` and `(o)` of `project.md`.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| RR1 | `uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_induced_provenance.py tests/test_fidelity_payload.py --tb=short` plus the files E1 names; `uv run ruff check` | fixtures that record `gnd_version`; plugin manifests; release notes links |
| RR2 | the one explicit command of RR2-C3 over the retained candidate; the new carries test inside it | the prepare job on GitHub (same file) |
| RR3 | `uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py --tb=short` | `docs/releasing.md` links |
| close | full default lane, six shards, `close-shards.sh` on beast-3, at the merge base and the closing tree | whole suite |

The merge-base full-suite record is taken on beast-3 before RR1 changes any
file, with the script's PATH fix (uv on PATH) from the rule-check-adoption
close.

## 10. Owner decisions and open questions

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| RL-D0 | Which instrument reviews this plan? | One reviewer (Codex, prompt on stdin), as for the two predecessor milestones; the panel is the project's bar | The panel costs its budget and needs all six seats' credentials; unreviewed plan stays labelled unreviewed **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). One Codex review runs over the plan, its findings are triaged and accurate repairs applied; then the plan stops at the gate. |
| RL-D1 | Version number | **0.2.0** (a minor of the 0.x line; free on PyPI per O3) | 0.1.1 reads as a patch of 0.1.0 and understates a feature release; any other number needs its reason. **Ruled (o, 2026-11-07): 0.2.0** ("0.2.0", answering "Which version should the release carry?") |
| RL-D2 | Which main content does the release cut carry? | (a) main as of RR1's merge; (b) **wait for rule-check-followups FU2 and FU3**, which fix `Population` copying and the derived-ring extent, features issue 118 lists, then cut; FU4 and FU5 do not gate; (c) wait for every in-flight milestone | (a) is fastest and ships FU2/FU3 defects in the very features it advertises, unfixed until 0.2.1; (c) has no end. RR1 does not depend on the choice; RR2 does. **Ruled (o, 2026-11-07): (b), wait for FU2 and FU3** ("Wait for FU2, FU3", answering "Which main content should the 0.2.0 release carry?"). FU4 and FU5 do not gate; RR2 starts only after FU2 and FU3 are on main |
| RL-D3 | Release-notes shape | one section for the version, rule-check items first, the twelve `Unreleased:` sections kept as dated subsections, status "prepared, not published" | renaming each section in place keeps the history flat but gives a reader no single "what's new" **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). |
| RL-D4 | When do README and installation pins change? | at publication, by the prepared patch (rule 3); until then they name 0.1.0 | flipping now tells users to install a file that does not exist; holding a PR open until publication conflicts with every sibling's edits **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). |
| RL-D5 | Publication route and identity (for the later request) | the dossier states both: token upload of the owner's chosen files, as for 0.1.0, or `release.yml` with a validated Trusted Publisher and the `pypi` environment; the plan chooses neither | Under the workflow route the uploaded bytes are the publication run's own build (O7); under a token upload they can be the retained candidate's **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). **Route ruled (o, 2026-11-08): (a), token upload of the retained `7c0f4d0e` candidate** ("Upload saved candidate", answering "Which publishing route for 0.2.0?", relayed by the session that started this one). The owner uploads by hand with their own token; no agent handles the token or uploads. Pre-upload checks, read-only: `shasum -a 256 -c SHA256SUMS` in the retained copy gives 3 x OK, `SOURCE_COMMIT` is `7c0f4d0e320ff7976296d785077280d180ea688e`, PyPI lists `['0.1.0']` (relayed; repeated by this session at 2026-11-08T15:17:55Z with the same results). Tag, GitHub release, the post-publication patch PR and the issue-118 comment (dossier actions 4 to 7) each wait for their own owner go-ahead. |
| RL-D6 | Run the prepare job on GitHub (`publish=false`) for Ubuntu evidence? | not in this plan; the owner may ask after RR1 merges; without it RR2 claims one observed profile only | A run adds an Ubuntu result and a 30-day artifact; it dispatches a workflow on main, so it needs the owner's request each time **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). |
| RL-D7 | If two local builds differ by hash, does that block? | no; record the difference and its cause (timestamps, paths); the served-file comparison after publication is the identity that counts | Blocking would hold the release on a property `release.yml` does not require **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). |
| RL-D8 | Resolve conflict C1 (`addopts` override for release acceptance) | the RR2 spec approval selects that one file and lane; nothing else overrides `addopts` | Without it RR2 cannot run the acceptance the release procedure itself names **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). |
| RL-D9 | How are version-bearing recorded bytes handled, if E1 finds some move? | decided after E1 and ruled in the RR1 spec: (a) compare with the version normalized, (b) regenerate the recorded bytes, (c) fix the version in the test environment | (b) rewrites retained evidence; (a) and (c) change a test's meaning. RR1 cannot be approved before E1 **Ruled (o, 2026-11-07): as proposed** ("Approve all as proposed (Recommended)", answering "How do you rule on the remaining release-plan decisions RL-D0 and RL-D3 to RL-D9 in PR 125 (RL-D1 = 0.2.0 and RL-D2 = wait for FU2/FU3 are already ruled)?", relayed to this session by the session that started it). RL-D9 stays deferred: it is ruled in the RR1 spec after E1. **Ruled after E1 (o, 2026-11-07): "Split (a)+(b) (Recommended)"** (answering "Release RR1 decision D2 (PR 125): the 0.2.0 bump turns 47 tests red because 32 saved reference outputs record version 0.1.0. How should they be handled?", relayed by the session that started this one): (a) normalize the version in the one RF1 pin helper; (b) regenerate the committed outputs whose purpose is to equal the current command's output, listing every moved digest in the RR1 spec before any code; no (c). The same relay ruled the opt-in lanes (`evidence`, `census`) "Record as excluded (Recommended)". Classification and digests: RR1 spec §13. |

Open questions carried: whether `docs/support.md` should name the new
candidate's observed profile after RR2 (proposed yes, one row); whether the
GitHub release for the new tag should attach the wheel and sdist as v0.1.0's
did (the owner's call at publication).

**Provenance of rulings:** RL-D0 to RL-D9 are ruled (o, 2026-11-07), quoted in their rows (RL-D3 to RL-D9 as one answer relayed by the session that started this one). They rule decisions; they are not the plan gate and approve no bytes. The plan gate was passed separately ("Approve r2", [001-plan.md](../001-plan.md)); RL-D9 was ruled later, after E1.

## 11. Review dispositions (r1 to r2)

One reviewer, Codex, over r1 and the RR1 spec at dbf98447 (verbatim in
[codex-review.md](../evidence/plan-review-r1/codex-review.md)). Each finding was
checked against the repository before it was accepted; `git grep` reproduced
P3 (13 `docs/` files name 0.1.0, plus `docs/index.md:144`,
`docs/marketplace-plugins.md:10` and the checkout instructions at
`docs/pyrel-apps.md:39-41`).

| Finding | Disposition | Applied at |
|---|---|---|
| P1 notes reconciliation | accepted | R2, RR2-C0 |
| P2 E1 cannot cover "every artifact" | accepted: claim narrowed, inventory added | predicate 2, RR1-C4 |
| P3 patch list incomplete, count wrong | accepted, reproduced | O9, RR3-C3 |
| P4 `RELEASED` literal vs RR1-C3 | accepted | RR1-C3, RR3-C3 |
| P5 probes mask behavior | accepted | §2, RR2-C4 |
| P6 git cannot audit remote state | accepted | predicate 6, R6, sweep |
| P7 availability recheck timing | accepted | C2, RR2-C0 |
| P8 `releasing.md` routes | accepted as a proposal for the RR3 gate | RR3-C4 |
| P9 spec status, costs, surface | accepted | spec §6, §7 |
| P10 RR1-C5 not gated | accepted | RR1-C5, spec T7 |
| P11 plugin/runtime mismatch | accepted | §5, RR1-C8 |

The reviewer's "checked and found true" list is retained with the record. r2's
repairs have no review opinion; one reviewer is one reviewer.

## 12. Close amendment (2026-11-09; approved by the owner with the close: "Accept as proposed", 2026-11-09)

Raised by the close record [`005-milestone-close.md`](../005-milestone-close.md),
2026-11-09. r2 was written for a milestone that ends before publication. The
owner then asked for publication (RL-D5's route ruling, 2026-11-08, and the
go-aheads quoted in the close record). As §4's close row requires, the close
records those requests as a new decision, RL-D10, not as part of the plan.
Three clauses describe a state that no longer holds. Their r2 wording is kept
above; this section says how the close reads them.

| Clause | r2 wording (kept above) | Read at the close as |
|---|---|---|
| Predicate 6 | "No workflow, environment, repository setting or PyPI configuration was changed to enable publication, and nothing was uploaded (all phases)" | No phase uploaded anything. The close's read-only checks observe no `.github` change since `12daa5b7`, environments `["github-pages"]` only and 0 `release.yml` runs. Repository settings and the PyPI publisher configuration are not audited (dossier action 1.2; close review L3). The 0.2.0 upload was the owner's own token upload of the retained files, under RL-D10. The tag and the GitHub release were also made by the owner, under RL-D10, and are not phase work. |
| Predicate 7 | "the close record ... leaves issue 118 open with its reason" | Issue 118 is closed as completed. With the owner's go-ahead, the comment recorded the published version and the served-file result. |
| §4, Milestone close | "issue 118 left open with the reason \"prepared, not published\"" | As predicate 7 above. |

The post-publication patches (RR3) were applied in PR 140 under RL-D10, and
not by a phase.
