# Release 0.5.0

r1, 2026-11-23. Milestone `release-0.5.0`, phase prefix `RW`. **Not reviewed
and not approved.** No plan review has run: RW-D0 asks which instrument reads
this plan, and until it runs the plan reads as unreviewed.

Source: the owner's request of 2026-11-23 ("Release 0.5.0"), made after the
three milestones merged since 0.4.0 were recorded as closed. Inspection
baseline: main `0bfded71` (the PR 232 merge). The predecessor is
[release-0.4.0](../../release-0.4.0/notes/release-0.4.0-plan.md). This plan
follows its phases, including its §11 amendments, and cites it instead of
repeating it. Plan authorship is not approval and not publication authority.

**Phases RW1 to RW3 prepare a release and publish nothing.** AGENTS.md says
"Release preparation does not enable a production publisher." The upload, the
tag and the GitHub release form a publication stage. Each of its acts runs
only on the owner's explicit request at that time (RW-D5).

## Completion predicates

The milestone is complete when, on main after merge:

1. The source version is 0.5.0, written once in `pyproject.toml`. `uv.lock`,
   the three plugin manifests and the release notes agree with it, and
   `tests/test_release_version.py` exits 0 (RW1).
2. Every tracked file that names 0.4.0, and every default-lane test whose
   result moves with the version, is listed before code from a grep inventory
   and a measurement (E1). Each one is classified as historical, retained
   install pin, recorded output or stale, and handled under a second
   digest-bound spec ruling (RW1).
3. The release notes have one 0.5.0 section that describes every user-visible
   change on the candidate commit since the `v0.4.0` tag, and no `Unreleased:`
   section for work the candidate contains (RW1, rechecked at the RW2 freeze).
4. A candidate wheel and sdist, built from a named main commit, install into a
   fresh environment outside the checkout and carry the probes RW-D6 selects.
   Each probe's availability control fails on the hash-pinned PyPI 0.4.0
   wheel (RW2).
5. `tests/test_release_acceptance.py` exits 0 over the retained candidate
   files, with its verbatim output recorded (RW2).
6. At the RW3 hand-over, a dossier states the candidate identity, the
   evidence, what was not measured and every owner action still needed. The
   `tools/release_text.py publish` invocation is rehearsed on a scratch tree
   and not applied (RW3).
7. No phase uploaded anything or created a tag, a GitHub release or the `pypi`
   environment, and no phase changed `.github/`. The close audits this with a
   `git diff` of `.github/` and dated read-only remote snapshots at baseline,
   at hand-over and at close.
8. The owner has published (RW-D5). The served files are compared with the
   retained candidate, a fresh index install is exercised, and the
   post-publication page edits are on main. A numbered publication record
   binds the receipts.
9. Each phase has an approved spec, a record with the verbatim focused-gate
   output, and one independent reviewer. The close record disposes of every
   open question.

## 0. Binding design rules

Rules 1 to 8 of the predecessor plan §0 bind unchanged, with the version names
moved on:

1. **Prepare, never publish.** No phase uploads, dispatches `release.yml` with
   `publish=true`, creates a tag or a GitHub release, or edits `release.yml`,
   the `pypi` environment or a publisher.
2. **One home for the version**: `pyproject.toml`.
3. **Install instructions pin a published runtime.** The pins stay at 0.4.0
   until 0.5.0 is on PyPI. The source version, the manifests and the
   prepared-state pages may describe 0.5.0.
4. **Evidence belongs to exact bytes.** Rebuilding makes a new candidate.
5. **Carrying is shown by running** from the installed wheel, with a control
   on the published 0.4.0.
6. **Measure, don't assert.** E1 measures the bump before the spec says how it
   is handled.
7. **Frozen surfaces.** No phase edits `release.yml`, its pinned test or the
   dependency freeze.
8. **Stop rule (size).** A phase pauses for the owner once it passes 1.5 times
   its estimate.

Two of the six `project.md` standing rules apply: rule 5 (one home for the
version and for the procedure) and rule 6 (measure). Rules 1 to 4 have no new
consumer of untrusted input, and each spec says so.

The structure guards of `project.md` are in every phase gate that changes a
file outside `.gnd-planning/`.

## 1. Scope, sources and authority

Authority comes from:

- the owner's request of 2026-11-23;
- AGENTS.md, `docs/releasing.md` and `docs/compatibility.md`;
- the predecessor plan, its close and its
  [carryover register](../../release-0.4.0/notes/close-question-sweep.md#durable-carryover-register).

### Obligations harvested

Kinds: **O** observed in the planning session, **I** an inherited claim read
from a record, **P** a proposed target.

| ID | Obligation or fact | Kind | Source | Owner |
|---|---|---|---|---|
| W1 | Release GND 0.5.0 | I | owner request, 2026-11-23 | RW1 to RW3; publication stage |
| W2 | `pyproject.toml` declares 0.4.0. `RELEASED = {"0.1.0", "0.2.0", "0.3.0", "0.4.0"}`, `TAGGED = {"0.3.1"}` | O | files at `0bfded71` | RW1 |
| W3 | PyPI serves 0.1.0 to 0.4.0 (eight files). 0.5.0 is free. Published 0.4.0: wheel `36288e7a…ea5c`, sdist `2c171ccc…29b6`, equal to the retained [RV2 checksum file](../../release-0.4.0/evidence/RV2/candidate/SHA256SUMS) | O | PyPI simple index, 2026-11-23 | RW2 control pin; rechecked at freeze and before upload |
| W4 | Remote tags: `v0.1.0` (lightweight, `75eda93f`), `v0.2.0` (peeled `7c0f4d0e`), `v0.3.0` (peeled `4c07c0e6`), `v0.3.1` (peeled `aff85c67`), `v0.4.0` (peeled `648cc6e0`). Four GitHub releases; 0.3.1 has none. Environments: `github-pages` only. `release.yml` has no runs | O | `git ls-remote --tags origin`, `gh release list`, `gh api .../environments`, `gh run list` | predicate 7 baseline |
| W5 | 14 first-parent commits separate `v0.4.0` from main. Under `src`, `pyproject.toml`, LICENSE and NOTICE, 29 files differ (+1,256 / −80), all under `src` | O | `git rev-list`, `git diff --shortstat` | RW1 notes |
| W6 | `docs/release-notes.md` has one `Unreleased: include roots on more routes` section with four blocks, all from PR 220. The section says nothing of external uniqueness, `Number`, `gnd witness-count` or `gnd replay-count` | O | file; `grep` | RW1-C3 |
| W7 | Merged after `v0.4.0` with user-visible effect: include-root-routes IR1 to IR3 (PR 220: judgments on include roots, `gnd flatten`, PyRel export of include roots, the include-path refusal); pyrel-rules-coverage RP1 to RP5 (PR 223: external uniqueness, anchored rules listed as not checked, `Number`, role-scoped value rules, the exit and refusal behavior of the rules programs, the `docs/runtimes/pyrel.md` section listing them); aggregate COUNT certificates (PR 204: `gnd witness-count`, `gnd replay-count`, the packaged count example and its contract reference); the literature pages (PR 213: `docs/literature/index.md`, `commands.md`). PRs 219, 224, 225 and 229 to 232 changed planning and delivered development skills; whether any of them changed a shipped file is checked file by file | O for the list, P for the last sentence | `git log --first-parent v0.4.0..0bfded71`, `git diff --stat` | RW1-C3 (reconciled per user-visible change) |
| W8 | The 0.4.0 bump moved 37 default-lane results and 12 generated outputs although `recorded_version.py` was expected to absorb it. RV1 repaired four test consumers and kept the committed bytes | I | [predecessor plan §12](../../release-0.4.0/notes/release-0.4.0-plan.md#12-close-repairs-2026-11-17), RV1 spec §12 | E1 in RW1 |
| W9 | `tests/test_release_acceptance.py` holds the 0.3.0 regression probes, five RV2 probes whose availability control is the hash-pinned 0.3.0 wheel, and a guard that the candidate is 0.4.0. Release acceptance keeps one negative control, against the release before the candidate; for 0.5.0 that is 0.4.0 | O for the file, I for the rule | the file; `docs/releasing.md` | RW2 |
| W10 | No full default lane is recorded on current main. The last one is the 0.4.0 close at `9371d8e3` | O | records of the three milestones merged since | E1 base run in RW1 |
| W11 | `project.md` says the lint gate `uv run ruff check` exits 0. On `0bfded71` it exits 1 with 198 findings; the 0.4.0 close carried 188 as RC-01 | O | `uv run ruff check`, 2026-11-23 | conflict C3; RW1 measures where the ten came from |
| W12 | No installed test covers the COUNT certificate commands. The predecessor plan §11 assigned the gap to a later dossier | I | predecessor plan §11, last bullet | RW2 probe 4 |
| W13 | Carryovers RC-03 (a negative control for the receipts phrase when the publication helper next changes), RC-06 (the token-route sentence of `docs/releasing.md` names releases through 0.3.0) and RC-07 (account-ownership and content/history checks before a later publication, the owner's) | I | predecessor carryover register | RW3 for RC-03 and RC-06; RW-D12 for RC-07 |
| W14 | Carryovers RC-01 (lint findings in dev-tools-delivered scripts), RC-02 (two `test_public_optional` setup errors under uv 0.13.7), RC-04 (query budgets) and RC-05 (Ossie export and redact) are not release work | I | the same register | baseline only; §7 |
| W15 | No RelationalAI engine has run an exported `--rules lqp` program. The programs are verified to compile, and the DuckDB programs are compared with `gnd check` | I | [pyrel-rules-coverage close](../../pyrel-rules-coverage/007-milestone-close.md) | the notes say it (RW1-C3); RW-D11 |
| W16 | The PR 204 integration reran no `pyrel_oracle` lane and no broad lane on the merged tree | I | [main-integration record](../../aggregate-count-certificates/007-main-integration.md) | RW-D8 |
| W17 | Other milestones are planned on main and may merge source before the freeze (reviewed-vocabulary-growth, growth-round-outcomes, literature-host-interfaces) | O | `.gnd-planning/PROJECT.md`, "Open issues on 2026-11-22" | RW-D2, RW2-C0 |
| W18 | Issues 214 and 217 are closed with comments saying the fix is not in a release yet | O | the issues, 2026-11-23 | RW-D10 |
| W19 | `docs/compatibility.md`: record breaking changes and migration in the notes, confirm availability before freeze and upload, never overwrite released files | I | file | RW1, RW2-C0, dossier |

This is a framework milestone, so a `gnd coverage` census does not describe
it. The component index was searched for nothing: the milestone builds no
capability.

### Implementability sweep (author inspection, not review)

- **Inputs exist when needed.** RW1 needs only main. RW2 needs RW1 and the
  acceptance probes on main, plus a clean checkout. RW3 needs RW2's hashes,
  and the publication stage needs the owner. No phase needs a write
  credential.
- **Tools.** `uv build`, run as `release.yml` runs it. The acceptance run uses
  beast-3 with Python 3.11 and the pinned uv 0.10.10, as for 0.4.0. The
  default lane uses beast-3's own uv profile, in six shards.
- **Measurable.** Each predicate has a command or a diff, and predicate 4 has
  a control for each probe.
- **Not known at plan time.**
  - which results and bytes the bump moves (E1);
  - the default-lane baseline on current main (W10);
  - the exact exit and diagnostic of each probe's control on 0.4.0. Issue
    214's table gives them for probe 3; RW2's spec measures the rest;
  - whether the count example and the interop runner work from an installed
    wheel (RW2).

### Conflicting clauses

| ID | Clause A | Clause B | Proposed resolution | Ruling |
|---|---|---|---|---|
| C1 | `project.md`: no `addopts` override in an ordinary gate | `docs/releasing.md`: acceptance runs with `-o addopts=''` | The RW2 spec approval selects that one file and lane | RW-D7 |
| C2 | AGENTS.md: preparation does not enable a publisher | The request is to release a version | The phases prepare, and publication is a separate owner-run stage | RW-D5 |
| C3 | `project.md`: the lint gate exits 0 | It exits 1 with 198 findings on the base (W11) | The lint gate of each phase is "no finding the base lacks", shown by comparing the two finding lists, as RV1 did | RW-D13 |

## 2. Contract proposal and product behavior

No GND command, report, schema or exit band changes. The product is the
package a user installs.

- **Release notes.** The `Unreleased:` section becomes
  `## 0.5.0 (prepared, not published)`. Its blocks, in order: PyRel rules
  programs for literature-style models (the headline, RW1 D4), include roots
  on more routes (the four blocks already written), aggregate COUNT
  certificates, then other changes. RW1's spec writes the two new blocks from
  each milestone's close record and reference pages. The PyRel block says
  that no RelationalAI engine ran the programs (W15).
- **What "carries" means (RW2).** The proposed set for RW-D6 is four probes,
  run from the wheel installed outside the checkout:
  1. **Judging an include root.** The interop example writes its roots from
     installed resources; `gnd judgments check` judges the temporal root with
     exit 0.
  2. **`gnd flatten`.** It writes the flat model and its `gnd-flattening/1`
     record for that root; a second run into the same directory exits 11.
  3. **PyRel rules export.** `gnd export pyrel --rules lqp` exits 0 for the
     packaged `assertions/model.orm.yaml` (external uniqueness), the packaged
     `model.orm.yaml` (anchored), a `Number` model and the include root.
  4. **COUNT certificates.** The commands of the packaged count example's
     README run from a copy of the installed directory; both certificates
     replay with exit 0.

  Each probe has two controls. The availability control runs on the
  hash-pinned PyPI 0.4.0 wheel and asserts the feature-specific exit and
  diagnostic, or that the command or resource is absent. The behavior control
  runs on the candidate:
  - an include edited without a new pin is refused `include:hash-mismatch`;
  - `gnd flatten` never overwrites (the exit 11 above);
  - an external frequency rule is still refused by name;
  - a replay against a population that lost a roster member is refused.

  RW2's spec writes each command in full, with its named inputs, its scratch
  directory and the measured 0.4.0 result. The probes export programs and do
  not run them: running one needs the PyRel runtime, which the wheel does not
  install (RW-D8 selects whether the `pyrel_oracle` lane runs at the freeze).

  The earlier probes stay as positive regressions. The five RV2 probes lose
  their 0.3.0 availability control, because 0.4.0 has those features, and
  keep their candidate behavior controls. The candidate-version guard moves
  to 0.5.0.

## 3. Dependencies and artifact homes

```
RW1 ──> RW2 ──> RW3 ──> publication stage (owner) ──> close
```

| Artifact | Home |
|---|---|
| version | `pyproject.toml` |
| lock entry, manifests, notes | as the predecessor plan §3 |
| carries probes | `tests/test_release_acceptance.py`, inputs under `tests/fixtures/release-acceptance/0.5.0/` |
| candidate evidence, dossier | `.gnd-planning/milestones/release-0.5.0/evidence/` |
| retained candidate | `~/gnd-release/0.5.0/<short sha>/candidate/`, copied to beast-3 |
| procedure (normative) | `docs/releasing.md`; RW3 edits its token-route sentence (RC-06) |
| workflow, publisher, environment | unchanged |

## 4. Phases, deliverables, named criteria and inherited residuals

### RW1: candidate content

Spec: [phase-RW1-spec.md](phase-RW1-spec.md), a draft. Its E1 runs only after
the spec's first ruling.

- RW1-C1: `pyproject.toml`, the `uv.lock` entry and the three manifests carry
  0.5.0, and `uv lock --check` exits 0.
- RW1-C2: E1 and the grep inventory are appended to the spec before code.
  Each entry is classified, and a second digest-bound ruling covers the
  measured handling.
- RW1-C3: the notes read as §2. Every user-visible change in W7 has a note or
  a stated reason for none, shown in a reconciliation table built from
  `git diff v0.4.0 <base> -- src docs` file by file. A test fails when the
  0.5.0 section lacks its headline block.
- RW1-C4: `docs/compatibility.md`, `docs/support.md` and the plugin page say
  0.5.0 is prepared and not published, and the install pins stay at 0.4.0.
- RW1-C5: `tests/test_release_version.py` and `tools/release_text.py check`
  exit 0.
- RW1-C6: the full default lane at the changed tree has no failure the E1
  base run lacks (beast-3, six shards).
- RW1-C7: the lint findings of the changed tree equal the base's (C3), and
  the record says which files hold the ten findings added since 0.4.0.

### RW2: candidate build and installed acceptance

An outline. The spec is written once RW1 is on main.

- RW2-C0: before any build, the notes cover every change on the freeze
  commit, 0.5.0 is still free on PyPI, and the six-shard default lane at the
  freeze commit has no failure RW1's run lacks. A sibling change without a
  note goes through a preparation pull request first.
- RW2-C1 to C3: the acceptance probes land on main through an owner-merged
  pull request; the build and a second build compared by hash, from the same
  named main commit; acceptance over the retained files, with `SOURCE_COMMIT`
  and `SHA256SUMS` verified on the receiving host before the run.
- RW2-C4: the probes of §2, each with its 0.4.0 availability control and its
  candidate behavior control. The 0.3.0 control is retired.
- RW2-C5: `uvx --from <wheel> gnd --version` prints 0.5.0.
- RW2-C6: the observed profile is recorded, and no other profile is claimed.
- RW2-C7, only if RW-D8 selects it: `pytest -m pyrel_oracle` at the freeze
  commit, with its summary line recorded.

### RW3: publication hand-over

An outline.

- RW3-C1: the dossier: candidate identity, results and what was not measured.
- RW3-C2: each owner action with its evidence: the availability recheck, the
  route, the tag on the accepted `SOURCE_COMMIT`, the GitHub release with its
  attachments (RW-D9), and RC-07's checks.
- RW3-C3: the exact `tools/release_text.py publish` invocation, rehearsed on
  a scratch tree, with every prepared-state marker in the notes,
  compatibility, support and plugin pages inventoried and the lines it leaves
  for a person listed. A negative control covers the receipts phrase (RC-03).
- RW3-C4: `docs/releasing.md` names the releases published by token upload
  through 0.4.0 (RC-06). The sentence moves again in the publication pull
  request only if `release_text.py publish` moves it.
- RW3-C5: a dated read-only remote snapshot, compared with W4.

### Publication stage (owner acts; not a phase)

Each step runs only on the owner's explicit request at that time:

1. upload of the retained files;
2. the annotated tag on the accepted `SOURCE_COMMIT`;
3. the GitHub release with its attachments;
4. the served-file comparison and a fresh index install;
5. the pull request with the `release_text.py publish` edits;
6. if RW-D10 selects it, a comment on issues 214 and 217 naming the release.

A numbered publication record binds the receipts.

### Milestone close

The close has a close record, a question sweep, a full default lane, the
remote snapshot of predicate 7 and the review RW-D0 selects for the close.

### Obligation-to-phase map

| Obligations | Phase |
|---|---|
| W1 | RW3, publication stage |
| W2, W8, W10, W11 | RW1 |
| W5, W6, W7, W15 | RW1-C3 |
| W3, W9, W12 | RW2 |
| W16 | RW-D8, RW2-C7 |
| W17 | RW-D2, RW2-C0 |
| W4 | predicate 7, RW3-C5, close |
| W13 | RW3, RW-D12 |
| W14 | §7; baseline lists |
| W18 | RW-D10, publication stage |
| W19 | RW1, RW2-C0, RW3 |

## 5. Documentation, skill and compatibility surfaces

- RW1 edits `docs/release-notes.md`, `docs/compatibility.md`,
  `docs/support.md` and `docs/marketplace-plugins.md`.
- The pins in `README.md`, `docs/installation.md` and `docs/index.md` move at
  publication, by `release_text.py publish`.
- RW3 edits one sentence of `docs/releasing.md`.
- Skills: no text change.
- Plugins: the manifests move in RW1, so the plugin on main is 0.5.0 while
  PyPI still has 0.4.0 (risk R3).

## 6. Risks and required controls

| ID | Risk | Control |
|---|---|---|
| R1 | The bump moves results or recorded bytes, as it did for 0.4.0 | E1 first; RW1-C2 and C6 |
| R2 | A sibling milestone merges source between RW1 and the freeze without a note | RW2-C0; RW-D2 |
| R3 | Main says 0.5.0 before PyPI has it | rule 3; the notes say "prepared, not published" |
| R4 | Candidate evidence is read as evidence for the published file | rule 4; the served-file comparison |
| R5 | The wheel lacks the count example or an interop resource, so a probe works in the checkout and fails when installed | RW2-C4 probes 1 and 4 run from installed resources |
| R6 | A probe also passes on 0.4.0 | the 0.4.0 availability control for each probe |
| R7 | 0.5.0 is taken by upload day | recheck at freeze and before upload |
| R8 | A phase eases a test by editing the workflow | rules 1 and 7; the close's `.github` diff |
| R9 | Main goes red between RW1 and the freeze | RW2-C0 runs the full lane at the freeze commit |
| R10 | The notes read as if RelationalAI enforcement was verified | the PyRel block states the limit (W15); the review of RW1 reads it |
| R11 | Retiring the 0.3.0 control removes a check without a replacement | RW2's spec lists each retired assertion beside the 0.4.0 control that replaces it or the reason it has none |

## 7. Out of scope

- An upload, tag, GitHub release, `pypi` environment or publisher registration
  by a phase.
- Announcements.
- Dispatching the prepare job on GitHub, unless the owner asks.
- Configuring Trusted Publishing.
- A certification or recertification.
- Changing `release.yml`, its pinned test or the dependency freeze.
- New product behavior of any kind.
- Running an exported program on a RelationalAI engine, unless RW-D11 says
  otherwise.
- RC-01, RC-02, RC-04 and RC-05 of the predecessor register.

## 8. Execution, approval and review protocol

`auto=false` unless the owner delegates the milestone's approval rulings, as
for 0.4.0. Each phase runs these steps:

1. spec;
2. owner gate;
3. implementation;
4. focused gate;
5. one independent reviewer in a different tool, with the prompt on stdin;
6. refactoring review;
7. record;
8. commit on a topic branch and pull request.

The owner merges. The project's bar for plan review and close is the
maintained panel; RW-D0 selects the instrument. Merge and each publication
act keep their separate owner authorization under either setting.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| RW1 | `uv run pytest -q tests/test_release_version.py tests/test_recorded_version.py tests/test_release_text.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_package_description.py --tb=short`, plus the consumers E1 names; the structure guards; `uv run python tools/release_text.py check`; the lint comparison of C3; the strict docs build; the full default lane on beast-3 | manifests; notes links; recorded-version fixtures |
| RW2 | `GND_CANDIDATE_DIR=... uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short` on beast-3 (Python 3.11, uv 0.10.10); the full default lane at the freeze commit | the prepare job (same file) |
| RW3 | `uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py tests/test_release_text.py --tb=short`; `release_text.py check` | `docs/releasing.md` links |
| close | full default lane, six shards on beast-3 | whole suite |

Expected results that are known: none of these gates has run for 0.5.0. The
E1 prediction is in the RW1 spec.

## 10. Owner decisions and open questions

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| RW-D0 | Which instrument reviews this plan and the close? | The standard GND panel, as for 0.4.0 | One reviewer in a different tool costs less and is below the project's bar for a plan. An unreviewed plan stays labelled unreviewed |
| RW-D1 | Version | **0.5.0** (the owner's request, 2026-11-23) | -- |
| RW-D2 | What does the cut carry? | Main as it is at the RW2 freeze. No planned milestone gates the cut; anything merged before the freeze is in, with a note | Waiting for reviewed-vocabulary-growth or another milestone delays the two closed issues by an unknown amount |
| RW-D3 | Notes shape | The `Unreleased:` section becomes the 0.5.0 section; the PyRel rules block is the headline | A different headline changes which block `HEADLINE_BLOCK` requires |
| RW-D4 | When do the install pins change? | At publication, through `release_text.py publish` | Moving them earlier names a file that does not exist yet, and the version test refuses it |
| RW-D5 | Publication route and ending | PyPI, by token upload of the retained files, as for 0.2.0 to 0.4.0. The milestone stays open through publication, and each owner act happens on its own request | A tag-only 0.5.0 leaves PyPI at 0.4.0, where issues 214 and 217 still reproduce |
| RW-D6 | Which features get an installed probe with a 0.4.0 control? | The four in §2 | Fewer probes leave a new command unexercised from a wheel |
| RW-D7 | The `addopts` override for release acceptance | The RW2 spec approval selects that one file and lane | Without it, RW2 cannot run the acceptance that the procedure names |
| RW-D8 | Opt-in lanes | `pyrel_oracle` runs once at the freeze commit, because the release advertises the rules programs and the last merge reran none (W16). `evidence`, `census`, `ossie_oracle` and the others are recorded as excluded | Excluding `pyrel_oracle` leaves the merged tree's rules programs compared with `gnd check` only on the pre-merge commits. Running it needs the tutorials runtime environment on the machine |
| RW-D9 | GitHub release attachments | The retained wheel, sdist and `SHA256SUMS`, as v0.4.0 | -- |
| RW-D10 | After publication, a comment on issues 214 and 217 naming the release | Yes, on the owner's request at that time | The reporters learn of the release from PyPI or the notes only |
| RW-D11 | Run an exported `--rules lqp` program on a RelationalAI engine before the release? | No. The notes state the limit | An engine run needs an account and credentials this session does not have; without it, enforcement by `require` on an engine stays unverified in 0.5.0 |
| RW-D12 | RC-07: account-ownership and content/history checks before upload | The owner performs them and the dossier records the dated statement | Without it, the close repeats the predecessor's "unrecorded" boundary |
| RW-D13 | The lint gate reading (C3) | "No finding the base lacks" | Requiring exit 0 puts 198 findings in dev-tools-delivered scripts in the release's way; they are RC-01's |
| RW-D14 | Run the prepare job on GitHub for an Ubuntu result? | Not unless the owner asks | Without it, only the macOS profile is observed |

Open questions carried: none beyond the rows above.
