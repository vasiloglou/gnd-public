# Release 0.3.0

r2, 2026-11-10. **Approved by the owner at the plan gate on 2026-11-10
("Approve r2"; [plan-gate record](../001-plan-gate.md)); approves no phase
spec.** r1 (sha256 `f21e6bce…4a77`,
uncommitted) was reviewed by one reviewer, Codex (disposition `revise`, 9
findings; [record](../evidence/plan-review-r1/codex-review.md)); §11 disposes
each. **r2 repairs r1 and carries no review opinion of its own**; it was not
re-reviewed. One reviewer is one reviewer; the project's bar is the panel, and
the owner chose this instrument (RN-D0). No phase has a
spec approval; no code is written. `auto=false`. Milestone: `release-0.3.0`.
Phase prefix `RN`.

Source: the owner's request of 2026-11-10 ("now that we have ossie support can
you cut a new version of gnd"), and two rulings given the same day (§10:
RN-D1, version 0.3.0; RN-D2, the content includes PR 161). Inspection
baseline: main at `2490dd77` (the PR 161 merge). The predecessor is
[rule-check-release](../../rule-check-release/notes/rule-check-release-plan.md),
which cut 0.2.0; this plan follows its phases and cites it instead of
repeating it. Plan authorship is not approval and not publication authority.

**Phases RN1 to RN3 prepare a release and publish nothing.** AGENTS.md:
"Release preparation does not enable a production publisher." The upload to
PyPI, the tag and the GitHub release are the owner's own acts. This plan
proposes (RN-D5) that the milestone stays open through that publication, as a
stage that runs only on the owner's explicit requests, so the close does not
need the amendment the 0.2.0 close needed (predecessor plan §12).

## Completion predicates

The milestone is complete when, on main after merge:

1. The source version is 0.3.0, written once in `pyproject.toml`; `uv.lock`,
   the three plugin manifests and the release notes agree with it, and
   `tests/test_release_version.py` exits 0 (RN1).
2. Every tracked file that names 0.2.0, and every default-lane test whose
   result moves with the version, is listed from a grep inventory and a
   measurement before code, and each is classified and handled by the method
   RN-D7 rules (RN1). Opt-in lanes that are not run are listed as exclusions.
3. The release notes have one 0.3.0 section that describes every user-visible
   change on the candidate commit, Ossie interchange included, and no
   `Unreleased:` section for work the candidate contains (RN1, rechecked at
   the RN2 freeze).
4. A candidate wheel and sdist built from a named main commit install into a
   fresh environment outside the checkout and carry the items RN-D9 selects;
   the same probes are refused or absent on the published 0.2.0 (RN2).
5. `tests/test_release_acceptance.py` exits 0 over the retained candidate
   files, with its verbatim output recorded (RN2).
6. At the RN3 hand-over checkpoint, a dossier states the candidate identity,
   the evidence, what was not measured and every owner action still needed,
   and the post-publication patch is prepared and not applied (RN3). The
   publication stage applies it later; predicate 8 covers that (r1 review P2).
7. No phase uploaded anything, created a tag, a GitHub release or the `pypi`
   environment, or changed `.github/`. The close states what it audited:
   `git diff` of `.github/` against the base, and dated read-only remote
   checks at baseline and close (environments, `release.yml` runs, releases,
   remote tags with their peeled commits, the PyPI simple index). These show
   remote state, not which actor changed it (r1 review P8).
   Repository settings and the PyPI publisher configuration are not readable
   by an agent and are named as not audited.
8. The owner has published (RN-D5, ruled): the served files are compared with
   the retained candidate, a fresh index install is exercised, and the
   post-publication patch is on main. Closing before publication is not a
   branch of this plan; it needs an owner amendment (r1 review P2).
9. Each phase has an approved spec, a record with verbatim focused-gate
   output and one independent reviewer; the close record disposes every open
   question.

## 0. Binding design rules

Rules 1 to 8 of the predecessor plan §0 bind unchanged; the short forms:

1. **Prepare, never publish.** No phase command uploads to PyPI or TestPyPI,
   dispatches `release.yml` with `publish=true`, creates a tag or a GitHub
   release, or edits `release.yml`, the `pypi` environment or a publisher
   registration. The publication stage (§4) is owner acts and read-only
   checks.
2. **One home for the version**: `pyproject.toml`.
3. **No instruction names an unpublished version.** Install pins stay at 0.2.0
   until 0.3.0 is on PyPI; `tests/test_release_version.py` already refuses the
   other order.
4. **Evidence belongs to exact bytes.** Rebuilding makes a new candidate.
5. **Carrying is shown by running** from the installed wheel, with a control
   on the published 0.2.0.
6. **Measure, don't assert.** The bump's effect on recorded bytes is measured
   (E1) before the spec says how it is handled.
7. **Frozen surfaces.** `release.yml`, its pinned test
   (`tests/test_release_preparation.py`) and the dependency freeze are not
   edited.
8. **Stop rule (size).** A phase pauses for the owner past 1.5 times its
   estimate.

Of the six standing rules of `project.md`, rule 5 (one home: the version, and
`docs/releasing.md` for the procedure) and rule 6 (measure) have subjects
here. Rules 1 to 4 have no new consumer of untrusted input; each spec says so.

## 1. Scope, sources and authority

Authority: the owner's request and rulings of 2026-11-10 in the planning
session, AGENTS.md, `docs/releasing.md`, `docs/compatibility.md`.

### Obligations harvested

Kinds: **O** observed in this session, **I** inherited claim read from a
record, **P** proposed target.

| ID | Obligation or fact | Kind | Source | Owner |
|---|---|---|---|---|
| N1 | Cut a new version now that Ossie interchange is on main | I | owner request, 2026-11-10 | RN1 to RN3; publication stage |
| N2 | The version is 0.3.0 | I | owner ruling RN-D1 | RN1 |
| N3 | The release includes PR 161 (Ossie on the docs homepage, and the ossie-interchange close record) | I | owner ruling RN-D2 | RN2-C0 |
| N4 | PR 161 is merged: main is `2490dd77`. PR 160 (Ossie interchange) merged as `85f54b55`. No pull request is open | O | `gh pr view 161`, `gh pr list` | RN2-C0 |
| N5 | PyPI serves 0.1.0 and 0.2.0 only (four files); 0.3.0 is free | O | PyPI simple index, 2026-11-11T02:53Z | rechecked at RN2 freeze and before upload |
| N6 | Environments: `github-pages` only; `release.yml` has 0 runs; remote tags `v0.1.0` (`75eda93f`) and `v0.2.0` (`d84ad6d5`, peeled `7c0f4d0e`) | O | `gh api .../environments`, `gh run list`, `git ls-remote --tags origin` | predicate 7 baseline |
| N7 | 213 commits separate `v0.2.0` (`7c0f4d0e`) from main; 109 files under `src`, `pyproject.toml`, LICENSE, NOTICE differ (9170 insertions, 675 deletions) | O | `git rev-list`, `git diff --stat` | RN1 notes |
| N8 | `docs/release-notes.md` has one section "Unreleased: model identity, projected text, and unattended growth" with seven subsections. It does not mention Ossie | O | file, `grep -i ossie` gives nothing | RN1-C3 |
| N9 | Merged since 0.2.0 with user-visible effect: report-output-fidelity ROF1 to ROF4 (issues 111, 112), FU5 (issue 114), unattended-model-growth UG2 to UG4 (issues 74, 104), model-composition MC1 to MC4 (issue 95), ossie-interchange OS0 to OS6, and fixes in PRs 68, 135, 136, 150. Changes with no note today (r1 review P6, reproduced): PR 68 (prepared-policy reuse rechecks hashability on Python 3.14); PR 136 (a null `derivations` read as absent in coverage, in session snapshots and in the redaction diff); and, inside the Ossie work, role names repaired in three packaged `gnd-model-from-text` examples (`issueNumber`, `occurredOn`, `startDate`, `fullName` to snake case) | O | `gh pr list --state merged`; `git diff v0.2.0 HEAD` | RN1-C3 (reconciled per user-visible change, not per pull request) |
| N10 | Ossie ships as `gnd export ossie` and `gnd import ossie`, with package data `src/gnd/schema/ossie/{PINNED,core-spec,ontology}.json` and `src/gnd/ossie-loss-report.schema.json`. No release test exercises them from an installed wheel | O | `git ls-files`, `grep` over the two release tests | RN2-C4, risk R5 |
| N11 | A new opt-in lane `ossie_oracle` is excluded from the default lane | O | `pyproject.toml` `addopts` | exclusions (RN-D11) |
| N12 | 20 tracked files outside planning and the lock name `0.2.0`: `pyproject.toml`, 3 manifests, `README.md`, 6 docs pages, 2 test files, 6 fixtures, 1 skill reference. Compressed fixtures are not counted by this grep (the 0.2.0 bump re-recorded 7 gzip containers) | O | `git grep -l -F 0.2.0` | RN1 inventory and E1 |
| N13 | The 0.2.0 bump moved 47 default-lane tests; 31 files were re-recorded and one pin helper compares `gnd_version` as a placeholder | I | predecessor `002-phase-RR1.md` | RN1 E1 |
| N14 | Deferred refactor, carried by the owner to "the milestone that prepares the release after 0.2.0": record version-bearing fixtures independently of the version | I | predecessor `005-milestone-close.md`, sweep | RN-D7 |
| N15 | `tests/test_release_version.py` holds `RELEASED = {"0.1.0", "0.2.0"}`, refuses a publication claim or an install pin for an unreleased version, and refuses a left `PUBLICATION_DATE` placeholder once released | O | file | RN1, RN3 patch |
| N16 | `tests/test_release_acceptance.py` carries the rule-check probes with a hash-pinned 0.1.0 control downloaded from PyPI | O | file lines 227 to 420 | RN2 (a 0.2.0 control is added beside it) |
| N17 | Published 0.2.0 identities: wheel sha256 `e323c19e303f3b7fe9cbe7528e68021d271589ce0b91fd54bd76b2b919a069e4`, sdist `f85818ead9cb651ae397ecd3ab50f87fdf5f9f7c7bada58a659cea2cb99e5104` | I | predecessor `003-phase-RR2.md` | RN2 control pin |
| N18 | 0.1.0 and 0.2.0 were published by the owner's token upload of retained files; Trusted Publishing has never been configured or validated | I | predecessor close, RL-D10 | RN-D5, dossier |
| N19 | Agent sessions were refused when they tried to push the `v0.2.0` tag and create the GitHub release; the owner did both | I | predecessor close, RL-D10 table | publication stage: commands prepared, run by the owner |
| N20 | `tests/test_plan_app_docs.py::test_plain_short_prose_without_exit_codes[grow-a-model.md]` exits 1 on main (`assert 141 <= 90`) in the default lane | O | run at `2490dd77`: 1 failed, 2 passed; ossie `033`, `034` | RN-D10 |
| N26 | `tests/test_development_scaffold.py::test_reference_closure_and_declared_bootstrap` exits 1 on main: `ossie-interchange/evidence/OS1/spec-r1.md` line 10 links `../006-phase-OS0.md` and `../005-OS0-spec-amendment.md`, which do not exist at that depth. The test stops at the first broken link. The reviewer's full traversal counted four unresolved links in two retained snapshots (three in `OS1/spec-r1.md`, one in `OS0/spec-r4.md`); this session reproduced the first only. `OS1/spec-r1.md` is pinned by `009-phase-OS1.md` at sha256 `b17b7743…3353` (reproduced), so its bytes must not change (r1 review P1) | O | run at `2490dd77`: 1 failed, 83 passed | RN-D10 |
| N21 | ossie-interchange is closed; its residuals are the upstream converter pull request and two documented converter refusals, none a GND defect | I | `ossie-interchange/034-milestone-close.md` | notes wording (RN1) |
| N22 | Full-lane practice: six shards on beast-3 (`~/close-shards`); uv is not on the non-interactive PATH there; a shard bundle needs a `refs/heads` branch | I/O | predecessor close; `ssh beast-3` | RN1-C6, close |
| N23 | Local uv is 0.10.10, the version `release.yml` pins | O | `uv --version`, workflow lines 25 and 88 | RN2 |
| N24 | `docs/compatibility.md`: record breaking changes and migration in the notes; confirm availability before candidate freeze and before upload; never overwrite released files | I | file | RN1, RN2-C0, dossier |
| N25 | The notes already record two reader incompatibilities with 0.2.0 (a preview with `population_check`; a proposal with a source-document operation) | O | `docs/release-notes.md` | RN1-C3 keeps them; dossier lists them |

There is no component index step: `project.md` says to skip it. This is a
framework milestone, so a `gnd coverage` census of experiment claims does not
describe it.

### Implementability sweep (author inspection, not review)

- **Inputs exist when needed.** RN1 needs only main. RN2 needs RN1 on main and
  a clean tracked checkout. RN3 needs RN2's hashes. The publication stage needs
  the owner. No phase needs a write credential.
- **Tools.** `uv build` as `release.yml` runs it; uv 0.10.10 locally (N23).
  The acceptance run uses beast-3 as for 0.2.0.
- **Measurable.** Each predicate has a command or a diff. Predicate 4 has a
  negative control per probe.
- **Not known at plan time.** How many tests the bump moves this time (E1),
  and whether the Ossie package data is in the wheel (RN2 finds out; R5).

### Conflicting clauses

| ID | Clause A | Clause B | Proposed resolution | Ruling |
|---|---|---|---|---|
| C1 | `project.md`: no `addopts` override in an ordinary gate | `docs/releasing.md`: acceptance runs `pytest -o addopts='' tests/test_release_acceptance.py` | As RL-D8: the RN2 spec approval selects that one file and lane | RN-D8 |
| C2 | Predecessor close: the fixtures refactor is carried to this milestone | The owner asked for a release, not a refactor | RN-D7 decides: re-record once more and carry to an issue, or refactor first | RN-D7 |
| C3 | AGENTS.md: preparation does not enable a publisher | The request is to cut a version, which ends in a publication | Phases prepare; publication is a separate owner-run stage inside the milestone | RN-D5 |

## 2. Contract proposal and product behavior

No GND command, report, schema or exit band changes. The product is the
package a user installs.

- **Release notes.** One `## 0.3.0 (prepared, not published)` section. Its
  first block is new text for Ossie interchange (export, import, the loss
  report, the pinned upstream revision, what is out of scope), written from
  `docs/explanation/ossie.md` and the ossie close record. The seven present
  subsections follow in order. A fresh `Unreleased:` section appears only when
  later work needs it (RN-D3).
- **What "carries" means (RN2), proposed set (RN-D9).** From the wheel
  installed outside the checkout:
  1. `gnd export ossie` on the packaged refunds model writes the ontology, the
     GND sidecar and the loss report, and `gnd import ossie` restores a model;
  2. `gnd validate MODEL --identity` prints the identity and its JSON line;
  3. a model with a pinned shared-vocabulary include validates;
  4. `gnd evolve preview --policy additive --check-population` admits the
     constraint the notes describe;
  5. `gnd validate --document --require-documents` exits 3 on an unchecked
     span.
  The five lines above name behaviors, not invocations: as written, items 4
  and 5 exit 64 for missing arguments (r1 review P4). The RN2 spec writes each
  complete command with named inputs, and says how the test writes the model,
  proposal, population and documents into its own scratch directory, since
  the existing corpora live under `tests/` and not in the wheel.
  Expected values come from the phase records of the milestones that shipped
  them and the reference pages, not from the output under test. Each probe has
  two controls, both required (r1 review P5): an availability control on the
  hash-pinned PyPI 0.2.0 wheel (the reviewer observed exit 64 for items 1, 2,
  4 and 5 and exit 3 for item 3 on the retained 0.2.0 wheel), and a named
  behavior control on the candidate: changed ontology or sidecar bytes are
  refused on import; a wrong identity digest does not match; a changed include
  pin is refused; a violating population is not admitted; full document
  coverage exits 0 where an unchecked span exits 3.

## 3. Dependencies and artifact homes

```
RN1 ──> RN2 ──> RN3 ──> publication stage (owner) ──> close
```

| Artifact | Home |
|---|---|
| version | `pyproject.toml` |
| lock entry, manifests, notes | as the predecessor plan §3 |
| carries probes | `tests/test_release_acceptance.py` |
| candidate evidence, dossier, patches | `.gnd-planning/milestones/release-0.3.0/evidence/` |
| procedure (normative) | `docs/releasing.md`, unchanged unless RN3 finds it stale |
| workflow, publisher, environment | unchanged |

## 4. Phases, deliverables, named criteria and inherited residuals

### RN1: Candidate content

Spec: [phase-RN1-spec.md](phase-RN1-spec.md), a blocked draft (it needs E1,
RN-D7 and RN-D10).

- RN1-C1: `pyproject.toml`, the `uv.lock` entry and the three manifests carry
  0.3.0; `uv lock --check` exits 0.
- RN1-C2: E1's list of moved default-lane results and the grep inventory of
  files naming 0.2.0 are in the spec before code; each entry is classified
  (historical, or stale) and handled by the ruled method.
- RN1-C3: the notes read as §2; every user-visible change of N9, counted per
  change and not per pull request, has a note or a stated reason for none,
  shown as a reconciliation table in the phase record; a test fails when the
  0.3.0 section lacks its Ossie block; the two 0.2.0 reader incompatibilities
  stay (r1 review P6, P7).
- RN1-C4: `docs/compatibility.md` and `docs/support.md` say 0.3.0 is prepared
  and not published; install pins stay at 0.2.0; the plugin page gives plugin
  users the repository route until publication. New test cases with mutants
  fail when the support page or the plugin page lacks its statement; the
  existing tests accept an empty support page (r1 review P7).
- RN1-C5: `tests/test_release_version.py` exits 0, and its existing mutants
  still fail.
- RN1-C6: the full default lane at the changed tree has no failure the merge
  base lacks (beast-3, six shards).
- RN1-C7 (RN-D10, ruled "fix"): the `grow-a-model.md` paragraph test and the
  scaffold reference test exit 0. The scaffold repair registers the retained
  snapshots' original homes and digests in `RETAINED_DOCUMENT_ORIGINS`
  (`tests/test_development_scaffold.py`); no retained evidence byte changes
  (r1 review P1).

### RN2: Candidate build and installed acceptance

Outline; the spec is written when RN1 is on main.

- RN2-C0: before any build, the notes cover every change on the candidate
  commit, PR 160 and PR 161 included (N3); 0.3.0 is still free on PyPI.
- RN2-C1 to C3: build, second build compared by hash, acceptance over the
  retained files, as predecessor RR2-C1 to C3.
- RN2-C4: the probes of §2, each with its 0.2.0 control.
- RN2-C5: `uvx --from <wheel> gnd --version` prints 0.3.0.
- RN2-C6: the observed profile is recorded; no other is claimed.

### RN3: Publication hand-over

Outline.

- RN3-C1: the dossier (candidate identity, results, not measured).
- RN3-C2: each owner action with its evidence: ownership, availability
  recheck, route, tag, GitHub release with attachments, announcements.
- RN3-C3: the post-publication patches (pins, `RELEASED`, the notes date,
  compatibility, the support row), not applied, with the stale-text check of
  the predecessor's RR3 adapted.
- RN3-C4: a stale-text inventory of `docs/releasing.md` is recorded with a
  disposition per hit; "no edit" is an outcome only when the inventory is
  empty or every hit is classified historical (r1 review P7).

### Publication stage (owner acts; not a phase)

Runs only under RN-D5 as proposed, and each step only on the owner's explicit
request at that time.

- The owner uploads the retained files with their own token, pushes the tag
  and creates the GitHub release. The session prepares the exact commands
  (N19).
- The session then runs the read-only served-file comparison and a fresh
  index install, and opens the pull request that applies the RN3 patches.

### Milestone close

Close record, question sweep, full default lane against RN1's records, the
read-only remote checks of predicate 7.

### Obligation-to-phase map

| Obligations | Phase |
|---|---|
| N1, N18, N19 | RN3, publication stage |
| N2, N12, N13, N15 | RN1 |
| N3, N4, N5 | RN2-C0 |
| N7, N8, N9, N21, N25 | RN1-C3 |
| N10, N16, N17, N23 | RN2 |
| N6 | predicate 7, close |
| N11 | RN-D11 |
| N14 | RN-D7 |
| N20, N26 | RN-D10 |
| N22 | RN1-C6, close |
| N24 | RN1, RN2-C0, RN3 |

## 5. Documentation, skill and compatibility surfaces

- `docs/release-notes.md`, `docs/compatibility.md`, `docs/support.md`,
  `docs/marketplace-plugins.md`: RN1.
- `README.md`, `docs/installation.md`, `docs/index.md` pins: at publication,
  by the RN3 patch.
- Skills: no text change. The sentence "GND 0.2.0 and older refuse a proposal"
  in the `gnd-model-evolve` contract is historical and stays.
- Plugins: manifests move in RN1, so the plugin on main is 0.3.0 while PyPI
  has 0.2.0 until publication (risk R3).

## 6. Risks and required controls

| ID | Risk | Control |
|---|---|---|
| R1 | The bump moves recorded bytes and the lane goes red in unrelated places | E1 first; RN-D7; RN1-C2 and C6 |
| R2 | A sibling change lands between RN1 and the freeze without a note | RN2-C0 |
| R3 | Main says 0.3.0 before PyPI has it | rule 3; the notes say "prepared, not published" |
| R4 | Candidate evidence read as the published file's evidence | rule 4; the served-file comparison |
| R5 | The wheel lacks the Ossie schema files, so export works in the checkout and fails when installed | RN2-C4 probe 1 runs from the installed wheel |
| R6 | A probe passes on 0.2.0 too | the 0.2.0 control per probe |
| R7 | 0.3.0 is taken by upload day | recheck at freeze and before upload |
| R8 | A phase eases a test by editing the workflow | rules 1 and 7; the close's `.github` diff |
| R9 | The main lane is already red by two tests (N20, N26); each hides a new failure in the same test | RN-D10 |

## 7. Out of scope

- Any upload, tag, GitHub release, `pypi` environment or publisher
  registration by a phase. Announcements.
- Dispatching the prepare job on GitHub, unless the owner asks (RN-D6).
- Configuring Trusted Publishing.
- The upstream Ossie converter pull request.
- A certification or recertification.
- Changing `release.yml`, its pinned test or the dependency freeze.
- New product behavior of any kind.

## 8. Execution, approval and review protocol

`auto=false`. Each phase: spec, owner gate, implement, focused gate, one
independent reviewer in a different tool (prompt on stdin), refactoring
review, record, commit on a topic branch, pull request. Merge is the owner's.
The project's bar for plan review and close is the maintained panel; RN-D0
asks which instrument reviews this plan.

## 9. Per-phase verification story

| Phase | Focused gate (exact files in each spec) | Affected consumers |
|---|---|---|
| RN1 | `uv run pytest -q tests/test_release_version.py tests/test_marketplace_plugins.py tests/test_release_docs.py tests/test_release_preparation.py tests/test_rf1_pin_harness.py --tb=short` plus the files E1 names; `uv run ruff check`; full default lane on beast-3 | fixtures that record `gnd_version`; manifests; notes links |
| RN2 | `GND_CANDIDATE_DIR=... uv run pytest -q -o addopts='' tests/test_release_acceptance.py --tb=short` | the prepare job (same file) |
| RN3 | `uv run pytest -q tests/test_release_docs.py tests/test_release_preparation.py tests/test_release_version.py --tb=short`; the stale-text check | `docs/releasing.md` links |
| close | full default lane, six shards on beast-3 | whole suite |

The exact beast-3 invocation is unresolved until RN1's spec names the script
copy it uses.

## 10. Owner decisions and open questions

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| RN-D0 | Which instrument reviews this plan? | One reviewer in a different tool, as for the two predecessor release plans | The panel is the project's bar; it costs its budget and needs all six seats' credentials. An unreviewed plan stays labelled unreviewed **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D1 | Version | **Ruled (o, 2026-11-10): 0.3.0** ("0.3.0 (Recommended)", answering "Which version number should the next GND release carry?") | -- |
| RN-D2 | Which main content does the cut carry? | **Ruled in part (o, 2026-11-10): "make sure you include PR 161 as well"**. PR 161 is on main (N4). Proposed for the rest: main as it is at the RN2 freeze; nothing else gates | Waiting for other work has no end |
| RN-D3 | Notes shape | one 0.3.0 section, Ossie first, the present subsections after it | Renaming in place gives no single "what's new" **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D4 | When do install pins change? | at publication, by the prepared patch | Flipping earlier names a file that does not exist; the existing test refuses it **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D5 | Does the milestone end at hand-over or after publication? | after publication: a stage of owner acts and read-only checks, each on its own request; route proposed as for 0.1.0 and 0.2.0 (the owner's token upload of the retained files) | Ending at hand-over repeats the 0.2.0 close amendment if the owner then publishes **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D6 | Run the prepare job on GitHub for an Ubuntu result? | not unless the owner asks | Without it one profile is observed **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D7 | Version-bearing recorded bytes (N14) | re-record with the method ruled for 0.2.0, after E1, and carry the refactor to an issue | Refactoring first removes the cost from every later release and delays this one by a phase; it also changes what those tests compare **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D8 | The `addopts` override for release acceptance | the RN2 spec approval selects that one file and lane | Without it RN2 cannot run the acceptance the procedure names **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D9 | Which features get an installed probe with a 0.2.0 control? | the five of §2 | Ossie alone is the smallest set that answers the request; fewer probes leave shipped features unexercised from a wheel **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D10 | The two red default-lane tests on main (N20 prose length, N26 broken planning links) | fix both in RN1, each as its own commit, so the candidate's lane has no known failure of its own | Accepting them as known failures keeps the lane red by two and R9 open; the 0.2.0 local CI stopped on the same scaffold test (predecessor close, PR 137) **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |
| RN-D11 | Opt-in lanes (`evidence`, `census`, `ossie_oracle`, others) | recorded as excluded, as for 0.2.0 | Running them costs lane time and may add sites to RN1 **Ruled (o, 2026-11-10): as proposed** ("Approve as proposed", answering "How do you rule on the open plan decisions RN-D0 and RN-D3 to RN-D11?") |

Open questions carried: whether the GitHub release attaches the wheel, the
sdist and `SHA256SUMS.txt` as v0.2.0's did (the owner's call at publication).

**Provenance of rulings:** RN-D1 and the quoted part of RN-D2 are the owner's
words of 2026-11-10 in the planning session. RN-D0 and RN-D3 to RN-D11 were
ruled as proposed by one answer the same day, quoted in each row. The rest of
RN-D2 (nothing else gates) is still a proposal. RN-D7 chooses the method; the
per-file handling is ruled in the RN1 spec after E1. These rule decisions;
they are not the plan gate and approve no bytes.

## 11. Review dispositions (r1 to r2)

One reviewer, Codex (gpt-6.1-sol, xhigh, read-only), over r1 and the RN1 spec
r1 (verbatim in [codex-review.md](../evidence/plan-review-r1/codex-review.md)).
Each finding was checked before it was accepted.

| Finding | Reproduced | Disposition | Applied at |
|---|---|---|---|
| P1 M11 would change evidence pinned by a record | yes: `009-phase-OS1.md` pins `b17b7743…3353`, and `shasum` gives it; `RETAINED_DOCUMENT_ORIGINS` exists at `tests/test_development_scaffold.py:73`. The count of four links is the reviewer's, not reproduced | accepted | N26, RN1-C7, spec M11 |
| P2 predicates 6 and 8 conflict; RN-D5 against a pre-publication close | yes, by reading | accepted | predicates 6 and 8 |
| P3 spec decisions left open after the plan rulings | yes: the spec was written before the rulings | accepted | spec §1, §7 |
| P4 two probe lines are not runnable commands | yes: `gnd validate --help` and `gnd evolve preview --help` show the required arguments | accepted | §2 |
| P5 the behavior control was optional | yes, by reading | accepted | §2 |
| P6 reconciliation per pull request misses changes | yes: commits `1a7411a8`, `fdaf156a`, `588abb74`; the example diff shows the four role names | accepted | N9, RN1-C3, spec §6 |
| P7 RN1-C3, RN1-C4 and RN3-C4 have no failing check | the reviewer ran the helpers; this session read them (`assert_no_publication_claim` rejects claims and requires nothing of the support page) | accepted | RN1-C3, RN1-C4, RN3-C4, spec T9, T10 |
| P8 no remote tag inventory | yes: predecessor `003-phase-RR2.md` R6; `git ls-remote --tags origin` | accepted | predicate 7, N6 |
| P9 plan rules 4, 5 and 8 unbound in the spec | yes | accepted | spec §4 |

The reviewer could not run the suite, reach PyPI, GitHub environments or
beast-3; N5, part of N6 and N22 stand on this session's observations only.
r2's repairs have no review opinion.

## 12. Amendment after E1 (2026-11-11 UTC; approved by the owner: "Yes, add RN0", 2026-11-10 local)

Raised by experiment E1 ([results](../evidence/e1/README.md)). The approved r2
wording is kept above; this section changes nothing until the owner rules.

**Finding.** N20 and N26 said main has two red default-lane tests. The base
lane at `2490dd77` has 26 failures and the 2 known errors. None existed at the
0.2.0 close (`483b49ea`); 6 are present after the model-composition close
(`54a47612`); 20 more after PR 160 and PR 161. Twenty-four of the 26 are the
structure and inventory guards of AGENTS.md: the layer map, the command pins,
the exact query-policy list, the disclosure leaf table, the skill routing
inventory, the identity-site list, and the wheel packaging guard, which says
`gnd/ossie-loss-report.schema.json` has no guard (risk R5 made concrete).

**What is not known.** Which of the 24 are stale pins that need re-recording
and which are real violations of the rule a guard protects (for example,
direct model reads in the Ossie modules where AGENTS.md prefers `ModelIndex`,
or imports the layer map forbids). E1 did not examine that.

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| RN-D12 | Does 0.3.0 wait for main's default lane to be repaired? | Yes: a new phase RN0, before RN1, with its own spec and owner gate. It classifies each of the 24 as stale pin or real violation, re-records the first kind with the reason, repairs the second kind or registers a counted exception where the repository's rules allow one, and adds the missing packaging guard. RN1 keeps M10 and M11 and its approved scope. RN2 does not build until the base lane shows only the 2 known errors | Releasing with the guards red ships code the repository's own checks reject, leaves R5 without its guard, and makes every later lane comparison start from 26 failures. Folding the repair into RN1 mixes source-structure work into a phase approved for content only |

**Ruled (o, 2026-11-10): "Yes, add RN0"**, answering "Should 0.3.0 wait for
a repair phase (RN0) that gets main's test lane green first?". The phase order
is RN0, RN1, RN2, RN3, publication stage, close. RN0's spec is
[phase-RN0-spec.md](phase-RN0-spec.md) and needs its own owner gate.

RN1 stays blocked until RN0 is on main: the digests it must list are taken on
a base that RN0 changes.

## 13. Close amendment (2026-11-11; approved by the owner with the close: "Accept and merge", 2026-11-11)

Raised by the draft close record
[`007-milestone-close.md`](../007-milestone-close.md). The wording above is
kept; this section says how the close reads it.

| Clause | Wording (kept above) | Read at the close as |
|---|---|---|
| RN-D5 | "a stage of owner acts and read-only checks, each on its own request; route proposed as for 0.1.0 and 0.2.0 (the owner's token upload of the retained files)" | The owner asked this session to publish (RN-D13, [publication record](../006-publication.md)). The upload, the tag and the GitHub release were run by the session on that request, with the credentials stored on the owner's machine. The route is unchanged: the retained files, by token. |
| §4, publication stage | "The owner uploads the retained files with their own token, pushes the tag and creates the GitHub release. The session prepares the exact commands (N19)." | As above. N19's expectation that an agent session would be refused the tag and the release did not hold. |
| Predicate 7 | "No phase uploaded anything, created a tag, a GitHub release or the `pypi` environment, or changed `.github/`." | Holds as written: RN0 to RN3 did none of these. The publication stage is not a phase. |
