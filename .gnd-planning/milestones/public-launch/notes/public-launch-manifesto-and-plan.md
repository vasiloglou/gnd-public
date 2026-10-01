> Public-safe adapted counterpart. Historical proposal/status sentences below
> are retained as history; [owner rulings](owner-rulings.md) establish current
> accepted status. Source originals remain authoritative for migration amendments.
> Original SHA-256: `ee92ef92097edaf9cbb02b27425b4d12102dcf069dc36e7da8560389cc62edb3`.
> Links to private historical records/raw review are replaced by explicit limits
> and public-safe summaries. No panel opinion covers these adapted bytes.

# GND public launch — gradual migration to gnd-public

**Status:** candidate r1, 2026-10-01. The owner requested a public-launch plan,
a new repository named `gnd-public`, gradual migration from this repository,
continued use of the phase system and development skills, and eventual
decommissioning only when the owner decides. This document delivers that plan;
it is not a plan gate, phase approval, publication, or retirement record.

**Inspection baseline:** `ac4be67afdddde0b2b2095a6cd383bc13852758c`.
The latest completed semantic milestone is
v7.2 (private source close, unavailable here), closed on 2026-10-01. The earlier
conversation's v7.1 reference is not a reason to discard v7.2's fixes.
Phase 0 freezes the actual migration baseline. This milestone is named
`public-launch` so repository migration does not consume a semantic version
or silently absorb work already assigned to v7.3. The owner reaffirmed the
`public-launch` name and authorized advancing planning and review on 2026-10-01.
That authorization does not decide the pending license/account/version choices.

The accompanying [source inventory summary](phase-0-summary.md)
records concrete source dependencies and the limits of the planning pass.
No runtime tests, panel, package upload, repository creation or credential
inspection were performed to prepare this draft.

## Thesis and completion predicates

A new contributor should be able to clone `gnd-public`, install GND, see a
meaningful failure and repair, and develop the framework using the same
disciplined phase workflow without access to the old repository. We migrate
reviewable units over time, preserving a working product and one authority
for each unit throughout coexistence.

There are three distinct checkpoints:

1. **Public launch, after P5:** approved public code and docs are accessible;
   a named package release is installable; advertised examples reproduce;
   contributors can follow the phase workflow; release provenance, limitations
   and the maintenance entry point are explicit.
2. **Migration readiness, after P6:** every selected capability, development
   tool and maintenance obligation has transferred or received a named owner
   exclusion; the public repository builds, tests and releases independently;
   the final source-to-target reconciliation has no unaccounted change.
3. **Retirement, P7 only after an explicit owner decision:** old development
   and publishing paths are disabled, redirection and preservation are
   verified, and the old repository is archived rather than deleted.

The **public-launch milestone comprises P0–P5** and can close after P5 plus
its review and owner closure gate. P6–P7 below are the separately tracked
**public-transition successor workstream**, whose activation and governing
record are established before its execution. They retain these identifiers
for traceability and are not hidden launch prerequisites. P6 remains required
follow-up work with an owner and trigger recorded at launch close; P7 remains
unscheduled until the owner chooses retirement. Closing public-launch neither
completes those phases nor asserts that the source repository is retired.

## 0. Binding design rules

The current [phase protocol](../../../../.codex/skills/process-phase/SKILL.md),
[standing rules](../../../../.codex/skills/process-phase/references/standing-rules.md)
and [verification selection](../../../../.codex/skills/process-phase/references/verification-selection.md)
are the development baseline. P1 adapts their repository-specific references
for the target while retaining their actual rules.

| Rule | Requirement |
|---|---|
| R1 — Preserve the source | Do not rewrite old Git history, delete historical evidence, move the working checkout, or reset ongoing work as a migration shortcut. Retain an immutable source identity for every batch. |
| R2 — Select public content explicitly | Migrate a reviewed allowlist and its dependency closure. Exclude private application/customer material, credentials, caches and machine state. Check nested package data, fixtures and examples, not just the root. |
| R3 — One authority per unit | Every capability and shared dependency has one development authority. Record a handoff before accepting changes in the target as authoritative. No automatic two-way synchronization. |
| R4 — Preserve observable contracts | Preserve distribution/import/CLI names, schemas, exits, deterministic outputs, refusal behavior and documented support unless an explicit compatibility decision changes them. Do not create a smaller checker by silently dropping constraints. |
| R5 — Keep GND independently useful | Generic functionality stays in scope even if text2lean originally requested it. The text2lean application, customer models and private product workflows are not implicitly selected for publication. |
| R6 — Carry tests with their claims | Map each selected old test to retained coverage, a justified current successor, or archived historical evidence. Missing private fixtures cannot become routine skips that make the public suite look green. |
| R7 — Keep evidence honest | Source SHAs, file digests, review opinions, functional results and assurance claims remain distinct. A new Git root does not preserve historical commit availability. Changed or unavailable assurance is reported as unavailable. |
| R8 — Retain development skills | Preserve both discovery roots, the full process-phase references, applicable review tooling, agent guidance, and runnable contributor instructions. Installer-owned links remain installer output. |
| R9 — Focused verification | Apply the reduced v6.3 selection: direct behavior plus affected consumers. Broad suites, external-provider runs and native special lanes need a named selection; certification remains explicit-owner-only. |
| R10 — Separate external actions | An approved phase can authorize its named external operations. Plan authorship alone does not publish code/packages/posts or archive the source. Reuse existing specific authorization; do not ask again for the same approved action. |
| R11 — Keep planning bounded | Track concise plans, specs, decisions, records and small protective fixtures. Put large raw run artifacts in selected durable storage with digests and retention policy; do not recreate the source archive in public Git. |
| R12 — Separate release authority | Exactly one repository may publish the maintained distribution at a time. TestPyPI, local build, GitHub visibility, PyPI release and announcement are separate recorded events. |

## 1. Scope and public product boundary

**Required:** a fresh `gnd-public` Git history with provenance; a functioning
GND package; a classified capability/test/resource inventory; portable phase
and review skills; developer CI; beginner examples and documentation;
controlled release/publication; a migration ledger and retirement procedure.

**Recommended product boundary:** the existing generic framework remains
open and locally useful, including model authoring, checking, synthetic data,
code generation, experiments, conformance, evidence and native export where
supported. Private applications can consume the public package. No commercial
application implementation is part of this migration.

**Recommended names:** GitHub repository `gnd-public`; product `GND`;
distribution `get-nick-done`; Python import and executable `gnd`.
Do not rename the package merely because the repository changes. Current
metadata says `0.1.0`; P0/P4 decide the next available release version after
checking actual package ownership and published versions. Internal v7.2 is
not automatically the public package version.

**Recommended license:** Apache-2.0, pending owner selection and an inventory
of rights, vendored code, licenses and notices. There is no license grant
merely because files have been staged in a target repository.

## 2. Required artifacts and record homes

This source repository initially owns this milestone's plan and phase records.
P1 places a reviewed public-safe copy of the governing plan and protocol in
the target. Cross-repository events use explicit repository identities and
digests; a private source link is not a prerequisite for public development.

Until P6, the source owns governing-plan amendments. Record every public
counterpart's source revision, source/public digests and disclosed adaptations
in an amendment ledger. Before an affected target phase proceeds, carry the
latest accepted ruling into its reviewed public-safe counterpart and record
that synchronization. A copied plan does not acquire independent authority.
Protocol changes follow the same rule until that development unit transfers;
after transfer, target-owned changes may be explicitly backported to the source.

Future execution artifacts, created only in their owning phase:

- `notes/phase-N-spec.md`: harvested obligations, exact cases, decisions,
  measured work limits and verification-selection ledger.
- `migration/units.json`: source revision, selected paths/resources/tests,
  destination paths, current authority and handoff state per migration unit.
- `migration/batches/<batch-id>.json`: source/target base identities, file
  digests and modes, path transformations, approved adaptations, test evidence,
  target commit and reconciled source high-water mark. A manifest that records
  the target commit is stored in a subsequent record, not hashed into itself.
- `migration/coverage.md`: public command/API/skill to behavior tests,
  fixtures, examples, optional dependencies and remaining limits.
- `migration/history-map.md`: retained source artifacts, relocated public
  evidence, external archive references and unavailable claims.
- `migration/decisions.md`: ownership, license, version, support matrix,
  excluded content and external-action decisions.
- `NNN-phase-N.md`: append-only completion records with actual gate results,
  review/refactoring dispositions and evidence identities.
- A release dossier, announcement drafts, adoption observations, final
  reconciliation and eventual retirement record.

These are proposed artifacts, not existing receipts. Keep the public ledger
free of confidential source text; restricted provenance can stay in the old
archive with a public statement of the verification limit. P6 records the
handoff of milestone/planning authority to `gnd-public`; never edit completed
records to pretend they originated there. P6 must transfer P7 specification,
evidence, phase-record and transition milestone-close ownership to `gnd-public`.
After archival, archive-state evidence and the transition close land in that target;
neither requires a new commit to the read-only source repository.

## 3. Sequence and coexistence protocol

Default sequence: **P0 baseline and decisions → P1 target and development
workflow → P2 runtime migration → P3 tests/workflows/evidence → P4 release
candidate and examples → P5 public launch → P6 maintenance handoff →
P7 owner-selected retirement.** P0–P5 belong to `public-launch`; P6–P7
belong to its `public-transition` successor. The launch-close record names the
successor owner and activation trigger rather than reporting it as completed.

Runtime units may move in several numbered batches within P2/P3. Phase 0's
import/resource closure decides their boundaries. The current CLI eagerly
imports many families, so a complete runtime source tree is the likely first
coherent batch; do not split commands by deleting files or rewrite the CLI
merely to make a migration diagram look incremental. Incrementality can be
in acceptance, test transfer, example delivery and ownership handoffs.

For an inseparable runtime closure, P2 stages the implementation and P3
completes its acceptance before the whole closure becomes public-owned.
A truly independent unit may transfer earlier only when its complete gates
already pass. Copying source files never transfers ownership by itself.

For each unit, use these states:

`source-owned → staged → verified → public-owned → source-retained`

1. Pin a source revision, target base, selected paths and dependency closure.
   Stage a curated import into a target branch with an explicit adaptation diff.
2. While staged, the source remains authoritative. Record source changes made
   after the pin and reconcile them before handing off. A staged target is
   not authorized to publish the production distribution.
3. Run the unit's accepted gates in the target without the old checkout on
   `PYTHONPATH`, editable installations, private credentials or unrecorded caches.
   Required runtime resources must be local/publicly retrievable as declared.
4. Record the target commit, coverage, remaining limits and authority handoff.
   Subsequent development for that unit originates in `gnd-public`.
5. If old consumers still need a fix, backport the specific reviewed patch to
   the source and record both identities. Do not overwrite public contributions
   with a later bulk source export. Conflicts are reviewed at the owning unit.

Shared modules transfer with all required callers or retain a documented
single authority until the closure moves. Emergency fixes follow the current
authority, with explicit reconciliation for every still-supported consumer.
Before each handoff, the gate fails for an unaccounted source change, target
conflict, missing dependency, unsupported public claim or unresolved current
regression in the selected surface.

Rollback before publication restores the recorded previous authority and
target base without rewriting retained records. After publication, corrections
use a new commit/release; never overwrite an uploaded version or pretend
published bytes were private. The P4 release runbook defines withdrawal/yank
and correction options for the selected package service.

## 4. Phases

### Phase 0 — Freeze scope, provenance and migration decisions

**Outcome:** a finite answer to what is being moved, from where, and under
which release and ownership rules.

Inventory tracked source, resources, tests, supported CLI/API surfaces,
skills, examples and CI. Classify content as migrate unchanged, adapt with
review, archive with claim mapping, or excluded/private with rationale.
Inspect nested `src/gnd/_assurance_evidence`, vendored skills, fixtures and
embedded transcripts before treating any directory as publicly releasable.
Pin the latest accepted source commit and account for ongoing changes.

Confirm the GitHub owner/account and current source visibility, target-name
availability, package ownership/version, license and notices, private/public
product boundary, baseline support matrix and release operator. Define size
budgets after measurement. Inspect existing obligations without silently
closing or rescheduling them, including the v7.2 artifact-copy carryover.

**Deliverables:** migration unit inventory, dependency/coverage map,
provenance/content classification and recorded owner decisions.

**Criteria:** P0-C1 every selected capability has an owning unit and closure;
P0-C2 every exclusion has a reason and affected public claim; P0-C3 source,
repository, license and package decisions are explicit; P0-C4 each batch has
an authority/reconciliation rule and measurable acceptance scope.

**Boundary:** planning and inspection; no public disclosure or runtime rewrite.

### Phase 1 — Bootstrap gnd-public and its development workflow

**Outcome:** a new contributor can discover and follow the phase system in
the target repository.

Create the target with fresh history and approved initial visibility. The
recommended route is private staging until P5, so incomplete imports are not
mistaken for the launch. Establish the minimal README, selected license and
notices, contribution/security/contact guidance, `.gitignore`, `AGENTS.md`,
CI skeleton and `.gnd-planning/` one-pager and milestone layout.

Initial target planning scaffold uses the existing `gnd-new-project` workflow
if selected in the phase spec; that is an explicit workflow handoff, not an
implicit sibling invocation. Its domain/model prompts must describe development
of GND itself, and must not manufacture a recovered domain model or copy private
historical populations. Alternatively, the owner may select an explicitly
documented import of the existing planning scaffold. Neither route may
re-scaffold an existing `.gnd-planning/` tree.

Selecting the scaffold does not select model authoring or any later GND station.

Carry both real `process-phase` directories and all their references; adapt
hardcoded historical paths, test-selection guidance and credential setup.
Include the full normative document closure used by that workflow in P1's
bootstrap allowlist, especially the packaged ORM-core milestone-record format
at its canonical repository-relative path. Check those references before the
P1 exercise; a pinned installed tool alone does not resolve them. P2 reconciles
these early resource bytes into the complete packaged tree without divergence.
Retain `auto=true|auto=false` semantics and the opt-in recertification ruling.
Resolve the legacy `plan-review-panel` credential loader: recommended is a
documented compatibility entry delegating to the maintained packaged panel,
preserving its review/claim boundaries and both discovery-root copies. If
kept as a separate runner, repair and test it before enabling it.

Bootstrap discovery against a pinned migration build or declared source tool
until P2's target wheel exists; record that temporary dependency and remove it
before launch. Installer-managed links are created only by GND's installer,
after their packaged targets exist. No dangling placeholder links.

**Criteria:** P1-C1 fresh target checkout resolves all development instructions
without private docs; P1-C2 unmanaged twins match bytes and executable modes;
P1-C3 review setup rejects missing credentials without sourcing project `.env`
or exposing values; P1-C4 a bounded sample phase-spec/record exercise validates
the protocol and its links without running a paid panel or fabricating approval.

**Boundary:** no mandatory model-provider access for ordinary contributions;
no inherited claim that a copied skill already passed a live provider run.

### Phase 2 — Migrate a coherent runtime and package

**Outcome:** the target builds an independently installable GND package.

Import the selected source dependency closure, schemas, normative packaged
skills and required resources using batch manifests. Keep move-only bytes
separate from adaptations. Preserve the current three base dependencies and
optional-extra policy unless the owner explicitly changes that contract.
Do not silently remove `_assurance_evidence`, schemas or skill resources to
shrink the wheel. Gate any resource change against actual reader behavior.

Migrate focused current runtime tests with their smallest sufficient fixture
closure. Configure a public test harness that does not require old planning
trees or unavailable Git objects. Preserve independent replay/oracle boundaries.
Keep unpublished incomplete intermediate batches explicitly non-releaseable.

**Criteria:** P2-C1 source-to-target differences are exhaustively attributed;
P2-C2 build, CLI import/help, Python API and selected valid/invalid/indeterminate
checks work from a wheel outside both checkouts; P2-C3 declared resources load
and omitted/stale assurance follows the supported unavailable/refusal behavior;
P2-C4 source deltas through the recorded high-water mark are accounted for;
only independently accepted units can transfer, and an inseparable runtime
closure stays source-owned pending P3 acceptance.

**Boundary:** a clean build or working `--help` alone is not functional parity.
No new semantic feature or engine refactor is justified by relocation alone.

### Phase 3 — Transfer behavior coverage, workflows and evidence

**Outcome:** the public feature set is supported by tests and usable workflows
without access to the historical development archive.

Complete coverage transfer for authoring/validation, checking/transition,
synthetic data, extraction/rendering, codegen/conformance, evolution/recovery,
experiments/feedback, judgments/references, derivation witnesses/replay,
exports and advisory review. Inventory actual current commands instead of
treating this prose list as an exhaustive schema. Transfer each applicable
skill/reference with its feature and select small runnable examples.

Separate current behavior from old proof/census/fixed-commit assertions. Retain
historical originals in the archive; public successors test current contracts
and clearly state what they do not reproduce. Refactor test bootstrap only
under its explicit spec: its existing lane map, old wheel materialization and
frozen failure hooks cannot be dropped without a coverage disposition.

Native/optional workflows are documented with exact selected toolchains and
their failure modes when absent. Native functional claims need selected
execution or unchanged-boundary evidence; unrun profiles remain unverified.
Prepare portable developer scripts and selected CI lanes. General contributors
must be able to run the ordinary suite without provider credentials.

**Criteria:** P3-C1 every advertised surface maps to current tests and needed
resources; P3-C2 fixture/harness collection has no undeclared private dependency;
P3-C3 every archived test has a surviving claim/coverage disposition; P3-C4
both discovery roots install/doctor/uninstall correctly in scratch roots;
P3-C5 example, export and review claims match actual selected evidence, and
the complete runtime closure's authority transfers only after its required
acceptance gates and final source-delta reconciliation pass.

**Boundary:** retaining historical evidence does not recertify moved code;
public CI does not silently expand to every historical or live lane.

### Phase 4 — Prepare the release candidate and first-user experience

**Outcome:** one exact release candidate is ready for independent trial and
publication, with clear limitations and maintenance instructions.

Create a five-minute path: install, check an invalid shipping request, inspect
the violated rule, apply the supplied repair, check again. Package all required
inputs and remove manual path-template staging from the introductory path.
Provide a software-release/dependency example next and an advanced evidence/
native-export guide separately. Identify saved proposals and synthetic judgment
receipts explicitly; optional live demonstrations get separate evidence.

Write a concise README, tutorials, support matrix, compatibility/version policy,
release notes and contribution guide. Show the Python API integration alongside
the CLI. Explain GND's public/private application boundary without promising
unimplemented commercial services or universal correctness.

Build wheel and sdist from the target. Install from the sdist-built wheel as
well as the release wheel in fresh environments. Check package metadata,
license/notices, bundled skills and example availability. Test the selected
Linux/macOS/Python profiles; advertise only the measured support matrix.
Prepare a release workflow that builds once and publishes those exact artifacts
with hashes, using an approved trusted-publishing identity where available.

Prepare launch copy, a short demo recording/script, GitHub release text,
support contact and rollback/correction runbook. Recruit a recommended five
external trial users; record observed first-run friction. If participants are
unavailable, do not invent adoption evidence: record the gap for the launch
decision. Outreach messages require explicit authorization before sending.

**Criteria:** P4-C1 a fresh user can follow the documented no-key example from
published-candidate artifacts; P4-C2 wheel/sdist/resource and declared-platform
checks pass with recorded hashes; P4-C3 docs distinguish replay, live execution
and assurance; P4-C4 publication inputs, owner decisions, support routing and
announcement drafts are concrete and reviewable.

**Boundary:** a five-minute target and five trial users are targets to measure,
not results asserted by the plan. No posts or package upload in this phase.

### Phase 5 — Publish and launch

**Outcome:** users can obtain the selected public release and report useful
feedback through a maintained channel.

At the publication gate, record the exact target commit, artifact hashes,
license, visibility change, version, destinations and already granted action
authorization. Reconfirm only missing authorization, not an already approved
phase action. Inspect the whole reachable target history and release artifacts
for unintended private material before making the repository public.

Transfer package-publishing authority before the first production upload:
disable old publishing credentials/workflows as appropriate, enable the target
identity and record the handoff. A GitHub release must not trigger an unintended
second upload. Publish approved artifacts, then install that exact version from
the public index in a fresh environment and run the introductory example.

Publish the GitHub release and approved announcement content. Recommended
initial channels are the owner's professional network, a technical tutorial
and Show HN once the no-signup example is usable. Log publication URLs and
known issues. Start with GitHub issues/discussions rather than requiring a new
community chat service. Paid advertising is outside the initial launch.

**Criteria:** P5-C1 public repository/license/docs match the approved candidate;
P5-C2 public-index installation reproduces the advertised example; P5-C3 only
the target can publish maintained releases; P5-C4 authorized announcements and
support routing are recorded, with actual outcomes and remaining limitations.

**Boundary:** publication is not proof of adoption or completion of migration.
External trial results and support requests remain observations, not marketing
claims generalized beyond their sample.

### Phase 6 — Make public development canonical and reconcile coexistence

**Successor scope:** `public-transition`, activated separately after launch.
The launch close assigns its owner and trigger; this phase is not a launch gate.

**Outcome:** normal GND development and releases continue from `gnd-public`,
and the source repository no longer contains unaccounted public functionality.

Reconcile all migration units against a final source high-water mark and the
target's intervening contributions. Resolve every remaining item as transferred,
intentionally private/application-specific, historical archive, or owner-approved
deferred with a named target and trigger. Generic missing functionality cannot
be silently reclassified as private to declare migration complete.

Run at least one real bounded maintenance phase in `gnd-public` using the
portable skills: spec, approval, implementation if needed, focused verification,
diff/refactoring review, record and commit. Do not manufacture a code change
merely for this exercise; a real documentation/fixture issue may suffice.
Complete a target-owned release or approved release rehearsal with the same
pipeline. Record the transfer of planning and open-question ownership, including
the governing-plan amendment ledger and all P7/transition-close artifacts, before
any source archival can be selected.

Measure first-run success/friction, independently authored models, repeat use,
issues and contributions using explicit feedback and public signals; do not add
telemetry to GND implicitly. Publish the maintenance policy and a short public
roadmap. Continued old-consumer support uses the explicit backport ledger.

**Criteria:** P6-C1 all selected units and source deltas have dispositions;
P6-C2 public development/release works without old-repo access; P6-C3 one real
maintenance phase establishes workflow portability; P6-C4 outstanding questions,
support obligations and source-retirement readiness have named owners, with
P7 and transition-close record/evidence authority explicitly in the target.

**Boundary:** the owner may keep the source repository active for residual
work; this phase neither archives it nor transfers private text2lean code.

### Phase 7 — Retire the source repository when the owner decides

**Successor scope:** `public-transition`, conditional on its P6 and the owner trigger.

**Trigger:** explicit owner retirement instruction after P6, with the exact
repository, preserved archive location/access and remaining consumers named.
There is no elapsed-time trigger or automatic archive action at launch.

Prepare the final authority/coverage ledger, backup and recovery instructions.
Verify retained source history and required evidence can be recovered, outstanding
issues have been moved or explicitly dispositioned, and no public release,
CI job, development skill or supported consumer depends on a writable old repo.
Preserve private archive access where appropriate; archiving does not imply
changing visibility. Add the final redirect/maintenance notice and disable
residual writers/jobs before archiving. Do not delete history or the repository.

**Criteria:** P7-C1 retirement instruction and all readiness predicates are
recorded; P7-C2 archive preservation/recovery and zero required old writers are
verified; P7-C3 the old repository is read-only with correct redirection and
the target remains independently usable; P7-C4 final phase and milestone records
retain unresolved claims and separately state launch, migration and retirement.

**Boundary:** archiving retains historical access according to permissions;
old assurance never becomes current evidence by virtue of preservation.

## 5. Development skills and documentation surfaces

| Surface | Target treatment | Owning phase / gate |
|---|---|---|
| `src/gnd/skills/*` | Canonical packaged workflow/reference sources; migrate all selected dependencies together, keep wheel inclusion and relative references. | P2/P3 package/resource and reference checks |
| `.codex/skills/*`, `.claude/skills/*` packaged links | Generate through `gnd install --symlink --project`; preserve tracked link values and fresh-clone adoption instructions. Never copy machine receipts. | P2/P3 installer/doctor controls |
| Both `process-phase/` real directories | Keep full workflow/references and byte/mode equality; replace private-path dependencies with portable selected contracts. | P1 adaptation; P6 real phase |
| Both `plan-review-panel/` real directories | Retain a safe supported entry point or explicitly approved compatibility replacement; do not publish the unsafe credential-loading behavior unchanged. | P1 decision and negative controls |
| `tools/run_gnd_review_panel.py` | Carry/adapt documented credential policy, no arbitrary project-env execution, no embedded keys or user-specific configuration prerequisite. | P1/P3 focused launcher controls |
| `AGENTS.md`, `CONTRIBUTING.md` | Explain source versus installed use, test lanes, record/gate/commit rules, skill ownership and optional reviewer setup. | P1 then P4 fresh-contributor read |
| `.gnd-planning/` | Public-safe governing plan, new specs/records and carried obligations; no wholesale historical archive copy. | P1 scaffold, P6 authority transfer |
| Test lane manifests, helpers, CI | Portable current-behavior selection; no implicit historical wheel reconstruction or network/provider calls on contributor PRs. | P2/P3 focused collection and execution |
| README/tutorials/package metadata | Public paths, actual version and measured support; starter replay and advanced topics separated. | P4/P5 installed examples |

Pin sites are inventoried at the spec gate. Preserve both unmanaged skill
copies together. Migrating the development system is required functionality,
not optional documentation polish. Any tooling adaptation affecting public
bytes must be independently reviewed and tested under the same phase protocol.

## 6. Risks and stop conditions

| Risk | Control / stop |
|---|---|
| Source advances while migration runs | Pinned batches, per-unit authority and final high-water reconciliation. Unaccounted deltas stop the handoff. |
| Thin runtime slice fails at import | Static/runtime resource closure; move a larger coherent batch before considering architecture changes. |
| Public tests only work beside private checkout | Clean target-only checkout/install and explicitly classified fixtures. Stop claims for unresolved dependencies. |
| New Git history breaks evidence identities | Preserve original claim identity; add current successors and history mapping. Never synthesize missing old commits as authentic history. |
| Private data buried in package resources | Review allowlist content and full target history/artifacts before visibility change. A filename-only scan is insufficient. |
| Review skill executes an arbitrary env file | Remove/disable that path, require documented trusted credential intake and no-secret controls. |
| Public development forks permanently | One owner per shared unit, reviewed backports, no blind bulk overwrite after public handoff. |
| Artifact-copy defect crosses migrated scripts | Respect v7.2's carryover trigger; inspect exported-byte/newline behavior before changing affected callers. |
| Publishing from both repositories | Explicit release-identity handoff and disabled source release path before target upload. |
| Cleanup becomes a semantic rewrite | Separate move/adaptation diffs, measured numerical change budgets in each spec, explicit amendments for new behavior. |
| Fresh archive grows to the old scale | Tracked-size budget plus digest-addressed external artifact retention; small decisive cases stay in Git. |
| Launch overstates reliability | Publish measured support and failure boundaries; compilation, replay and formal assurance remain separate claims. |

## 7. Out of scope

No new semantic family, rewritten evaluator, private text2lean application,
commercial cloud platform, billing system, automatic synchronization daemon,
automatic historical recertification, rebranding exercise, broad old-suite
repair, deletion of source history, or paid advertising campaign is selected.

Existing carried obligations keep their states unless separately ruled. In
particular, migration does not close old broad-suite questions or reassign
v7.3 work merely because a related file moves. P0 flags overlaps; the owning
phase either waits for the successor or requests a concrete scope amendment.

## 8. Execution and review protocol

This is a milestone plan, not an invocation of `process-phase`. Its first
next step is plan review and the owner plan gate. As in the current repository,
plan and the public-launch close each require at least four complete usable reviewer
responses; the panel runtime quorum of three does not lower this bar. Preserve
failed seats, all dissent, actual independence limits and reviewed-byte identity.
The plan-review result will be recorded separately; writing this candidate
does not establish a panel outcome. A single internal planning read
is not that panel. Follow the existing convergence policy for any rerun budget.

After the gate, each phase follows `process-phase`: harvest obligations from
sections 0/4/5/6/7/9/10 and predecessor records; write exact spec/corpus and
verification ledger; record the owner gate; implement/verify; review the diff;
review refactoring; record and commit under the approved protocol. Default is
`auto=false`. Prior delegation for v7.2 does not grant delegation for this new
milestone. Explicit delegation for this milestone can supply its named gates.

Specs define exact commands, expected exits, numerical work/edit budgets and
the approval instrument before implementation. Plans, specifications, external
publication and closure have separate claims. If prior authorization already
covers an action, record it and proceed rather than repeating the same ask.

Do not import phase records that contain private material merely to satisfy a
public panel. Supply reviewed public-safe successor artifacts, retaining the
originals and identifying redactions/adaptations honestly. Credentials follow
the applicable workflow contract; never read/source project `.env` to obtain
panel keys or publish credential values in evidence.

## 9. Verification selection

| Phase | Mandatory focused obligation | Starting points; exact commands belong in spec |
|---|---|---|
| P0 | Complete selected-unit classification, identity and dependency closure; decisions are distinguished from approvals. | Tracked-file/source inventory, v7.2 close, CLI/API/skill resource references |
| P1 | Skill twins/reference portability, safe credential intake, phase-spec/record exercise. | `tests/test_doctor_uninstall.py`, launcher controls, process-phase reference checks |
| P2 | Curated diff/closure, wheel resources, CLI/API behavior, stale/missing assurance and authority reconciliation. | Selected current checker/API/transition controls; explicit bounded distribution selection |
| P3 | Current coverage mapping, collection bootstrap, installed skills, workflows and optional dependency refusals. | `tests/conftest.py`, v6.3 lane map, v7.2 successors, skill/export/replay controls |
| P4 | Exact wheel/sdist artifacts and measured support profiles; reproducible examples, valid public links. | Target-only installed replay; selected packaging/installer and beginner examples |
| P5 | Public version and example, release-authority handoff, approved publication scope and reachable-history inspection. | Public-index installation, repository/release settings, release hashes and publication receipts |
| P6 | Zero unexplained source/target deltas, real target-owned phase, independent release/rehearsal and obligation routing. | Migration manifests, target phase records and selected release checks |
| P7 | Recoverable source archive, no required old writers/dependencies, actual archive/redirect state. | Preservation/recovery check, consumer inventory and repository settings |

Each spec records `run`, `inherit` or `cadence`, the exact input boundary,
evidence identity, reason and invalidation trigger. Moving paths, package
contents, CI configuration or Git identity can invalidate historical results;
unchanged source text alone does not establish an unchanged execution boundary.

Ordinary phase tests keep the reduced v6.3 exclusions. Distribution, native,
live-provider or broader lanes require an explicit bounded phase/CI selection;
do not override markers just to obtain a green headline. CI's public selection
is reviewed in P3; it is not the existing broad workflow copied unchanged.
No certification or recertification is selected by this plan. Missing assurance
must remain visible rather than bypassing readers or reusing stale certificates.

The draft itself receives only scoped static checks: relative links, criterion
coverage, phase order, decision status and whitespace. Those are checks of this
plan, not evidence that any proposed migration or product behavior works.

## 10. Owner decisions and open planning questions

The user has selected the new name `gnd-public`, gradual migration, continued
phase/development skills and owner-controlled retirement. These are fixed
inputs. The recommendations below await the plan gate; none is an approval.

| Decision | Proposed default | Resolve by |
|---|---|---|
| PL-D1 — Baseline | Latest accepted v7.2 source at execution, starting from this inspection commit; pin and reconcile later deltas. | P0 |
| PL-D2 — GitHub location/visibility | Owner-selected account; private staging, public at P5; fresh history with attribution/provenance. | P0/P1 |
| PL-D3 — License and notices | Apache-2.0 for owned GND code after rights/third-party inventory; preserve required notices. | P0 |
| PL-D4 — Product boundary | Generic GND capabilities public; text2lean/customer applications remain outside migration. | P0 |
| PL-D5 — Package identity/version | Keep `get-nick-done` / `gnd`; verify ownership and choose the next available release version independently of milestone numbering. | P0/P4 |
| PL-D6 — Runtime batch size | Prefer complete dependency closure over command slicing; measure before committing to batches. | P0/P2 |
| PL-D7 — Development kit | Preserve process-phase and safe review entry points in both roots; adapt the legacy runner or replace with an explicit compatibility route. | P1 |
| PL-D8 — Test/evidence policy | Current behavior in ordinary CI; historical originals archived with coverage mapping; no automatic recertification. | P0/P3 |
| PL-D9 — Support and artifact budgets | Measure and gate concrete OS/Python/native profiles, tracked-size limits and retention/storage costs before release. | P0/P4 |
| PL-D10 — Announcement and trials | No-key dispatch demo first; target five outside trials; approved network/tutorial/Show HN launch, no paid ads. | P4/P5 |
| PL-D11 — Source coexistence | Authority transfers by unit, target-only package publishing from P5; explicit reviewed backports while source consumers remain. | P0/P5/P6 |
| PL-D12 — Retirement | Owner-triggered archive after P6; no deletion or automatic visibility change. | P7 trigger |

New technical questions discovered in execution enter the canonical question
registry under its existing rules. These PL-D decision labels do not mint,
close or change the state of existing technical open questions.

## External publication references

Checked 2026-10-01; recheck service-specific configuration at execution:

- [PyPI trusted publishing](https://docs.pypi.org/trusted-publishers/using-a-publisher/):
  use a configured publishing identity and upload the selected artifacts.
- [GitHub repository archiving](https://docs.github.com/en/repositories/archiving-a-github-repository/archiving-repositories):
  archive preserves a read-only repository; it is a distinct operation from deletion.
- [Show HN guidelines](https://news.ycombinator.com/showhn.html):
  provide something people can actually try with minimal access barriers.

These references explain external operations, not approval to execute them.
