# Phase 4 — preparation before regression acceptance

**Status: awaiting owner review (2026-10-03), auto=false.**

## 1. Provenance and claim boundary

Owner invocation: `process-phase 4 public-launch auto=false`, explicitly selecting
a gap review and preparation spec, with Phase 3 paused and Phases 1–2 complete.
This is step 1 only. No implementation approval, preparation completion,
regression acceptance, candidate sign-off or publication is recorded.

Effective sources, in precedence order:

| Source | SHA-256 of inspected bytes |
|---|---|
| [r3 amendment](public-launch-plan-r3-amendments.md) | `ece90d1461a320730b524f80e72c0430082e0a1aa1cc46e90664855de6de6514` |
| [r2 amendments](public-launch-plan-r2-amendments.md) | `05d539e9fc72378678a75e71dc110e6993d279e864b5804cee836974d4d3e0ba` |
| [r1 plan](public-launch-manifesto-and-plan.md) | `ee92ef92097edaf9cbb02b27425b4d12102dcf069dc36e7da8560389cc62edb3` |
| [completed P1 target successor](../001-phase-1.md) | `07494dde06fa625b9281338ef6f7433b2e1106bedfe0cb4e4abf000874b0d655` |
| [completed P2 target successor](../002-phase-2.md) | `8df94b9c1ff2e70ed2060b24fb4b885487ea9765d1300974a2c1f9b335e847c6` |

Also read: [owner rulings](owner-rulings.md),
the source P3 pause note (source-only origin citation), and the
the source Phase 4 gap review (source-only origin citation). Its G1–G12 observations are the work inventory,
not acceptance findings. Source HEAD is `3131a974e5e58b4f6d7766ec4ddf82b5df6dbd6a`;
target HEAD is `40bd8958d1df24c0751051e2412535cec53746ce`. Both have existing
uncommitted work; pin the reviewed implementation diff at execution. No panel
has reviewed this spec. Earlier plan opinions do not cover these bytes.

## 2. Obligations harvested from the whole plan

| Source / obligation | Required discharge |
|---|---|
| Thesis and completion predicates | Preparation is not public launch, migration readiness or retirement; §5/§9 retain the order. |
| §0 R1–R12 | Explicit applications in §3; no implicit ownership/acceptance changes. |
| §1 product boundary | Generic framework, CLI/API/skills stay supported; no new semantic family or application product. §5A/C. |
| §2 artifact/amendment ownership; r2 A3/A4 | Source owns migration amendments/records; carry accepted scope to target with origin/adaptations. Target owns ordinary development of accepted public units. Draft release dossier in target, no archive import. §5E. |
| §3 unit authority, coexistence and rollback | Review source/target deltas together, never bulk overwrite; source authority stays until explicit acceptance/handoff. Correction runbook in §5E; no handoff in preparation. |
| §4 P4-C1 | “a fresh user can follow the documented no-key example from published-candidate artifacts”; r2 A5 means prepared artifacts, not public index. §5C/T1 prepare it; P3 verifies final install, then sign-off. |
| §4 P4-C2 | “wheel/sdist/resource and declared-platform checks pass with recorded hashes”; r2 A7 adds separate release/sdist wheels and build-once promotion. §5B/T3/T4 smoke now; final profile/install validation in P3. |
| §4 P4-C3 | “docs distinguish replay, live execution and assurance”. §5C/D, T1/T2/T6; no-key starter has no provider/native prerequisite. |
| §4 P4-C4 | “publication inputs, owner decisions, support routing and announcement drafts are concrete and reviewable”. §5E/T6/D3–D6; no invented trial evidence. |
| r2 A2 P4-C5 | Fresh target-only candidate-wheel contributor exercise, no source/editable dependency, both roots/resolved paths, non-authoritative sample spec/record. §5D/T5 prepare; P3 final clean validation. |
| §4 deliverables | Dispatch failure/repair, software release example, separate advanced guide, README/tutorial/API/support/version notes, build/release CI, demo script, support/correction runbook, trial status: §5B–E. |
| §4 boundary (no Residual paragraph exists) | “a five-minute target and five trial users are targets to measure, not results asserted by the plan.” r2 replaces the upload boundary with no production upload/announcement; this preparation selects no disclosure/upload at all. |
| §5 skill surfaces/pin sites | §5D and §6 enumerate roots, packaged resources, scaffold/installer/launcher pins; measure counts when implementing, not from plan totals. |
| §6 risks | §3 and §8 cover import closure, stale evidence, source dependence, credentials, authority, artifact-copy trigger, size, dual publishing and overstated claims. |
| §7 exclusions | §9: no semantic redesign, archival campaign, broad historical repair, certification or successor activation. |
| §8 execution/review | Spec-before-code and two owner stops; numerical limits §10; implementation later gets independent diff review, reproduced regressions, refactoring review and preparation record. |
| §9 P4 row, quoted | “Exact wheel/sdist artifacts and measured support profiles; reproducible examples, valid public links.” §8 separates focused preparation from r3-deferred final validation. Starting points: “Target-only installed replay; selected packaging/installer and beginner examples”. |
| §10 PL-D5 | Keep names/control already approved; exact release version availability/configuration still pending. D3. |
| §10 PL-D9 | Approved size limits survive r3; exact support/tool profile and actual sizes remain to measure. D4, §10. |
| §10 PL-D10 | No-key dispatch, trial target, launch channels; recipients/disclosure/rehearsal decisions D5/D6, no new messages. |
| r2 A1/A6/A8/A9/A10 | Whole-plan harvest; exact content before disclosure; match existing authorization to action scope; no live-panel claim; P6/P7 separate. §5E/§7/§9. |
| P1 inherited limits | Historical bootstrap conditional; safe review compatibility and twin roots retained. Finish readiness without repeating bootstrap. §5D/T5. |
| P2 inherited limits / OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE | P2 is complete, not a release certificate. Decide beyond measured uv 0.10.10; do not reuse its artifacts as candidate. D4. |
| P3 useful pending work and holds | Preserve pending code/tests for ordinary review. Exhaustive original-definition accounting and evidence packing no longer gate preparation; final test-family decisions belong to paused P3. §5A/§8. |
| r3 + current owner instruction | P4 preparation → P3 acceptance → P4 sign-off → P5. No archival/compression restart, no regression acceptance in this part. |

## 3. Standing rules and risk coverage

| Rule | Application |
|---|---|
| R1 Preserve source | Only new planning files now. At execution use explicit-path commits and preserve existing dirty work; no source reset/history rewrite/archive deletion. |
| R2 Explicit selection | Review new example/resource/notices and candidate contents. “Retained-private” does not prove confidentiality or justify removing tests under r3. Credentials/machine state remain excluded. |
| R3 One authority | Reconcile affected source-owned runtime adaptations explicitly; target changes do not silently transfer authority. |
| R4 Observable contracts | Retain names, schemas, exit bands, deterministic behavior, base/optional dependencies. New semantic behavior requires an amendment. |
| R5 Independent utility | Installed package and public instructions supply the starter without old fixtures/paths. |
| R6 Tests with claims | Keep unique supported behavior assertions. P3 owns final keep/consolidate/retire/optional family decisions; no historical-definition denominator gate. |
| R7 Honest evidence | Build results bind actual artifacts; stale assurance unavailable; working-tree parity is not test acceptance. |
| R8 Skills | Both real twins and generated managed links; source-free reference closure and labeled exercises. |
| R9 Focused checks | §8 selects direct/downstream controls, with explicit bounded distribution smoke; full validation deferred. |
| R10 External actions | Local preparation only. No push, access grant, provider call, upload or announcement selected. |
| R11 Bounded planning | Concise Git diff/results/dossier, no per-batch reconstruction archives. Product/public size limits still apply. |
| R12 Release authority | Manual promotion consumes tested artifacts without rebuilding; publisher remains disabled/unselected until the later gate. |

Protocol's six paid-for rules also bind this work:

1. **Totality belongs to the function, not the caller:** pending YAML/report/coverage
   adapters get hostile-input and nested-container controls at their own boundary;
   any new artifact checker must refuse missing/invalid input instead of reporting green.
2. **An input cap bounds the document, not the algorithm:** retain scanner copying
   bounds and time/work controls; no expanding archive traversal as a preparation gate.
3. **Validation order is part of design:** preserve loader/refusal and JSON serialization
   ordering; release promotion validates identities before any upload action.
4. **One policy walk over all kinds:** use the existing resource/installer discovery;
   don't hardcode a second list of skills or duplicate evaluator policy for examples.
5. **Normative prose has one home:** runtime schemas/CLI remain normative; release
   procedure lives in docs/releasing.md and tutorials link to it. Twin skill edits
   stay byte/mode pinned; historical stage descriptions stay historical.
6. **Resolve representation questions by measurement:** compare both built wheels'
   installed behavior/resources, not presumed archive byte equality. New build-profile
   claims need observations; current historical profile claims are not generalized.

Failure classes: each new accepting check gets a rejecting mutation (T1–T5);
branch coverage includes both wheel origins and both skill roots. Do not count
one exercised half as the whole class. Report/canonicalization fixes preserve
existing key/nonfinite behavior, not a newly invented digest format. Recheck
neighbors after repairs. The future diff record must say “one reviewer is one
reviewer”; this author's static review is not that review.

## 4. Goal

Produce a reviewable prepared tree whose selected T1–T6 checks exit 0, with
observed command exits and build/import smoke evidence, concrete release/docs
artifacts and a concise handoff to P3. No check here awards full-suite acceptance.
After P3 accepts the prepared package, P4 sign-off binds that exact tested commit
and artifacts without another implementation round. Any intervening code/package
change goes back through affected validation.

## 5. Design and work lanes

All implementation paths below are relative to target `gnd-public`, unless
marked source. New files are proposals, not files created by this spec.

### A. Review remaining adaptations (G8–G10)

Review the existing seven-file runtime diff plus `src/gnd/yaml_comments.py`.
Preserve intended current behavior; do not authorize an evaluator rewrite.
Existing surfaces that the review must leave compatible:

- `model.load_model_bytes(data: bytes, *, source: str | Path) -> Model`.
- `population._parse_document_bytes(data: bytes, *, suffix: str, source: str) -> Any`.
- `rai_import.parse_rai_model_bytes(data: bytes, *, source: str) -> MutableMapping[str, Any]`.
- `coverage._declared_arm_errors(error: Any, schema: Mapping[str, Any], document: Mapping[str, Any]) -> list[Any]`.
- Pending `yaml_comments.configure_comment_scanner(yaml)` returns the configured
  YAML instance; safe/round-trip behavior and unsupported stream fallback stay intact.
- Pending `report._serializable_transition_document(report: Any) -> dict[str, Any]`
  normalizes witness containers without mutating input or losing nonfinite refusals.
  Public `build_transition_payload` signature/schema is unchanged.
- Session schema-version gating and semantic-registry owner spelling are review
  items, not new schema versions or permission to change expected results.

Confirm equality and specific changes in both checkouts at execution, including
untracked scanner dependency/notices. Review and retain useful existing tests;
fix a reproduced failure only within the named boundary, otherwise amend this
spec. Do not run or modify the original-definition acceptance/archival pipeline
to claim these adaptations accepted. P3 chooses its successor acceptance role.

### B. Package and release workflow (G4–G6)

Keep `get-nick-done` / import `gnd` / executable `gnd`, Python >=3.11 metadata,
three base dependencies and optional synth separation. Propose uv 0.10.10 for
this candidate; lock/backend compatibility is D4. Add license and repository/docs
metadata to `pyproject.toml`, reconcile `uv.lock` only if needed, and retain
license text/attribution for the scanner adaptation in the shipped resource closure.

Proposed files: `.github/workflows/release.yml`, `docs/releasing.md`, and focused
`tests/test_release_preparation.py`. Release workflow builds the release wheel
and sdist once from a recorded target commit into an immutable artifact set.
A separate job builds a comparison wheel from that sdist in a separate directory;
identical wheel filenames must not overwrite the release wheel. All three hashes,
source identity, Python/uv/backend profile and actual results go in the dossier.

Preparation may run a bounded local build/import/example smoke. Those artifacts
are labeled preparation builds unless retained as the later candidate and validated
in P3. A later candidate rebuild is a new identity. Promotion consumes the recorded
release wheel + sdist and refuses missing/hash-mismatched artifacts; it does not
rebuild. PRs and tag/release events must not upload. Production enablement, OIDC
identity/environment and service rehearsal stay explicit later decisions. Offline
workflow controls mock transport; never contact a package service in these tests.

No new persistent machine-report schema or public runtime API is proposed.
Use ordinary SHA-256 files and a Markdown dossier; if an executable publication
validator or new serialized contract becomes necessary, amend the spec/corpus
before implementation rather than inventing it during release work.

### C. Examples and learning path (G1/G3)

Propose canonical package data in `src/gnd/examples/dispatch/` and
`src/gnd/examples/release/`, with model, invalid population, repaired population,
fixed references and any required declared inputs. Reuse reviewed source
v7.1 domain content where suitable; exclude experiment/receipt machinery from the
starter. No new CLI subcommand. Document one runnable Python resource-copy block
using `importlib.resources` into a new user directory, followed by literal CLI
commands in that directory. No manual DOMAIN/ADAPTER/policy-template substitution.

The starter runs validate → invalid check → supplied repair → repaired check.
Use `model.orm.json`, `seed.pop.json`, `repaired.pop.json` and `references/`
from the reviewed source `tests/fixtures/v71/phase8/{dispatch,release}/original/`
as the initial content selection; review their reachable resource closure before
copying. Existing `tests/fixtures/v71/phase8/answers.json` I02 rows establish the
expected contract below, not a current-byte execution result:

| Both domain stories | Exact expected exit / observation |
|---|---|
| `gnd validate model.orm.json --format json` | 0, valid model |
| `gnd check model.orm.json seed.pop.json --admission --format json` | 1, violated `dispatch_deadline` / `release_deadline` respectively |
| `gnd check model.orm.json repaired.pop.json --admission --format json` | 0, repaired mechanical check |
| Same repaired check with required reference removed or changed | 3, reference refusal rather than a semantic violation |

The corpus must retain these discriminating outcomes and their API equivalents; a
nonzero parser/import error cannot satisfy “invalid example”. Missing reference
is a separate refusal case. CLI and public API must agree. Five-minute timing
is measured and recorded, never assumed. Use only the base install, no key/network
or native compiler after installation. The release/dependency example explains the dependency route and its release
deadline failure/repair in its own domain vocabulary. Advanced replay/judgment/native instructions
live in `docs/advanced.md`, labeling saved/synthetic material and unavailable
assurance explicitly; no live/native execution selected.

### D. Contributor workflow and pin sites (G2/G7)

Update README, CONTRIBUTING, AGENTS, `docs/development/bootstrap.md` and the
labeled `docs/development/examples/phase-{spec,record}.md` as needed. Bootstrap
history remains history; current steps must resolve only target/local installed
resources. Preserve ordinary editable development as an option, but the final
P4-C5 isolation exercise uses a target-built installed wheel, not an editable
GND install. It runs in a fresh target-only tree with both roots and sample
exercise, recording module/tool/link realpaths. Preparation adds its controls;
P3 executes the final candidate exercise.

Pin sites inspected: `tests/test_development_scaffold.py` (REQUIRED/bootstrap
text, 16 managed skills, twins/modes, staging README, uv pin); `tests/test_packaged_skills.py`;
`tests/test_public_agents_skill_table.py`; `tests/test_public_installer.py`;
`tests/test_install.py`; `tests/test_doctor_uninstall.py`; `tests/test_review_credential_launcher.py`;
`tests/test_public_distribution.py` (uv/resources/manifest audit); both real
`process-phase` and `plan-review-panel` roots. Measure discovery counts anew if
changed; current observation is 16 links + 2 real directories per root.

Replace obsolete *current-state* staging assertions with executable successor
checks for current setup. Historical fixture/record pins remain historical.
Do not run the scaffold's archive/manifest census just to turn a wording edit
green. Add bounded `tests/test_contributor_preparation.py` for current docs,
twin/link closure and exercises, with broken reference/twin/unlabeled-sample
negative controls. Installer-owned link changes use `gnd install`; no manual
symlink construction. Any real unmanaged skill change is applied to both roots.

### E. Release dossier, support and launch preparation (G11/G12)

Propose `docs/support.md`, `docs/compatibility.md`, `docs/release-notes.md`,
`docs/launch-drafts.md`, `docs/demo-script.md`, and
`.gnd-planning/milestones/public-launch/notes/release-dossier.md` in target.
The dossier records prepared source identity, artifact paths/hashes when built,
observed vs pending support profiles, license/notices, unavailable assurance,
known issues, trial status, release operator and outstanding decisions.
No result placeholders may read as successful executions.

Candidate support proposal: Ubuntu/Python 3.11 and macOS/Python 3.13, uv 0.10.10;
report the actual OS/architecture from validation. Other interpreters/native
profiles are unmeasured until separately selected; >=3.11 is metadata, not a
complete tested matrix. Retain current staging CI while preparing the release
jobs; P3 owns final suite selection and clean CI runs.

Document GitHub issue/security routing, version compatibility, release hashes,
and post-publication correction/new-version/yank choices. Recheck official
service documentation when configuring these service-dependent steps. Prepare
launch text and a timed demo script; don't send them. Trials: desired count five,
actual count unobserved; D5 records none authorized now. Any later disclosure
names recipients/channel/payload/access scope and reviews content/history exposed.
TestPyPI is D6, not implied by a build. Carry r3 and the approved preparation scope
into the target's migration planning home before implementing; record origin and
adaptations concisely, without byte-reconstruction packets.

## 6. Implementability sweep (completed at spec authoring)

- P4 preparation can precede P3 because it claims focused readiness only. Final
  P4-C1/C2/C5 validation is explicitly deferred, not silently dropped.
- Two wheel origins require separate output directories; byte equality is not
  required, comparable installed behavior/resources is. No build-once contradiction.
- Source bootstrap is already absent from selected ordinary setup; current
  contributor successors replace stage-text assertions rather than requiring a
  historical record to stop mentioning its own bootstrap.
- New package examples can live under the existing module-root packaging rule.
  They need no unsupported backend include key or fourth base dependency.
- Dirty runtime dependencies include an untracked scanner with third-party
  attribution; a tracked-files-only build would omit it. Explicit review/staging
  and package smoke can detect this without archival work.
- Existing P2 package/scaffold gates couple useful checks to historical migration
  manifests. Current bounded successors can exercise product boundaries without
  changing old evidence or completing every old definition's disposition.
- External version availability, trial recipients and publishing identity are
  pending facts/decisions, not blockers to drafting the package/workflow locally.
- No timing, trial, support or final acceptance result is asserted in advance.

## 7. Decisions for the owner gate

Previously granted target/account/operator, Apache-2.0 owned-code license,
package names/control and size budgets are preserved, not asked again.
All following proposed choices remain **OPEN**; no delegated approval applies.

| ID | Decision / recommended reading | Alternative and cost |
|---|---|---|
| D1 | Corpus-first for the bounded changed acceptance predicates and example exits; this prose is the preparation design. Author a small story corpus under target `docs/development/examples/release-preparation/`, entry README separate from expected answers, then obtain approval before implementation. | Prose-only avoids a corpus gate but requires an explicit exception rationale under process-phase because exit/validation predicates are involved. |
| D2 | No optional spec panel; use focused implementation controls and the required later independent diff review. | A bounded spec panel adds cost; it is not Phase 3 acceptance or candidate approval. |
| D3 / PL-D5 | Keep 0.1.0 as provisional metadata only, with exact next available release version selected after a current package-service check before candidate freeze. | Select a different explicit version now; still recheck availability, update metadata/lock/dossier, rebuild and validate affected artifacts. No upload selected. |
| D4 / PL-D9 / OQ-PUBLIC-LAUNCH-P2-BUILD-PROFILE | Pin candidate uv 0.10.10, preserve compatible backend lock, prepare Ubuntu 3.11 + macOS 3.13 profiles, measure exact environments in P3; uphold existing size budgets. | Newer uv or a larger matrix adds compatibility/profile checks before any support claim. P2 observed strict ancillary-byte differences on newer uv. |
| D5 / PL-D10 | Prepare launch/trial materials only; record trials unavailable/not recruited. No recipients, outreach or artifact sharing selected. | Named trial recipients/channel/access/payload require concrete disclosure review and separately scoped authorization. |
| D6 / r2 A7 | Omit TestPyPI rehearsal for this candidate, explicitly retaining the untested service boundary. | Select a bounded rehearsal after naming artifact identities and publishing/disclosure authorization; it still cannot prove production configuration. |
| D7 | Accept §10 budgets and review of the enumerated pending runtime/workflow adaptations with focused controls, retaining P3 final suite ownership. | A new semantic family, format or additional runtime boundary returns for amendment, not an opportunistic repair. |

Owner marks/dates and the exact approved spec digest are appended after the
ruling. Approval of an instrument/corpus is separate from the explicit go-ahead
for implementation. No code is authorized by this draft.

## 8. Tests and verification-selection ledger

Commands below run from target using the approved tool profile. Proposed new
test files do not exist yet; their names are intentional, not claimed existing
anchors. All ordinary commands preserve configured pytest exclusions. No broad
run, provider/native lane or certification is selected. Test authoring must pin
exact case exits in the D1 corpus and preserve existing semantics.

| Gate / cases | Disposition; exact command and expected exit | Input boundary / justification / invalidation |
|---|---|---|
| T1 dispatch + release invalid/repair, named cause, missing reference, CLI/API agreement | run after approval: `uv run pytest -q tests/test_release_examples.py --tb=short`, exit 0. Test subprocesses assert §5C exits 0/1/0/3 for each story; wrong error cause or missing packaged input fails test (pytest 1). | Both example trees, loader/check/API/CLI, base dependencies. Changed inputs or outputs require rerun. Supports C1/C3. |
| T2 pending runtime caller closure | run: `uv run pytest -q tests/test_yaml_comment_neighbor.py tests/test_transition_mapping_totality.py tests/test_public_alias_schema_guards.py --tb=short`, exit 0. | Scanner model/population/RAI paths, immutable mapping transitions, nonfinite/key collision behavior. Preserve scanner work bounds and report no-mutation controls. Changed helper/caller/dependency invalidates. |
| T2b remaining adaptation branches | run: `uv run pytest -q tests/test_runtime_preparation.py --tb=short`, exit 0; proposed focused tests cover nested tagged oneOf/$ref and unknown tag, derivation missing-id completeness, session v7/v8 admission gating, registry owner resolution. | Four enumerated pending boundaries. Reuse existing concrete protective cases when found and record exact node replacement; no exhaustive registry census. Must fail on each pre-fix behavior. |
| T3 promotion/workflow/resource predicates | run: `uv run pytest -q tests/test_release_preparation.py --tb=short`, exit 0. Fake promotion accepts exact wheel/sdist; refuses missing/mismatched artifact; no PR/tag upload, no rebuild; both wheel origins retained. | Workflow/build metadata/example resource list/notices; wrong hash, omitted scanner/resource or overwritten comparison wheel must fail. Supports C2/C4. |
| T4 bounded local build/import smoke | run: `uv run pytest -q -o addopts='' tests/test_release_preparation.py::test_two_wheel_build_import_smoke --tb=short`, exit 0. This is an explicitly selected single distribution node, not the entire distribution lane. | New node builds target wheel+sdist, separate sdist wheel, checks metadata/license/resources and CLI import/help using outside-root environments. Strip PYTHONPATH/PYTHONHOME/user-site/project env contamination; assert module paths. Build may fetch pinned build/base deps. Changes invalidate; not final clean-install acceptance. |
| T5 contributor/skill/current setup | run: `uv run pytest -q tests/test_contributor_preparation.py tests/test_review_credential_launcher.py tests/test_public_installer.py --tb=short`, exit 0. | Target instructions/real twins/managed links/installer/launcher. Missing ref, broken link, twin byte/mode drift, source path dependency, unlabeled sample reject. Existing credential no-execution/no-leak refusals remain. Supports C5. |
| T6 docs and dossier consistency | run: `uv run pytest -q tests/test_release_docs.py --tb=short`, exit 0; `git diff --check`, exit 0. | Current docs only, resource links and dossier statuses. Broken local link/false live-or-assurance label fail. External URL availability is pending until named final network check; private target URL is not a public availability success. C3/C4. |
| Completed P1/P2 status | inherit historical completion only at §1 record digests; exact commands/results remain in those records. No functional result inherited for changed runtime/build/docs inputs. | Records unchanged; invalidation of their old test input boundary means present assurance unavailable. Status remains complete under r3. |
| Final behavior-family suite + target-only contributor/install + Linux/macOS CI | cadence: P3 resumed by its own instruction after prepared tree. Select exact family commands in P3 against frozen prepared inputs, including final C1/C2/C5 install/profile checks. | Whole prepared package, lock, CI, docs, supported profiles; any later code/package change invalidates affected results. Not run during P4 preparation. |
| Candidate sign-off | cadence: P4 after P3 acceptance; exact commit/release wheel/sdist and separate sdist wheel evidence, owner version/profile/rehearsal decisions and hashes. | No rebuild during promotion; code/package/artifact changes reopen affected validation. No sign-off now. |
| Historical broad replay / native / providers | cadence: explicit owner or separately selected CI only, no automatic trigger here; no current-byte assurance claimed. | No blanket addopts override, frozen replay, historical archive reconstruction or live panel. Certification is unselected absent a named owner request. |

T3's distribution node is marked distribution and excluded from its ordinary
command; T4 explicitly runs that one node. T1–T6 exercise current product
boundaries, not total migration bookkeeping. A zero-test selection is not a pass.
For every new checker use a known-dirty negative control. Retain the exact
command, exit, selected/deselected counts and concise outcome; no extra preservation
framework. An implementation finding may refine downstream nodes but cannot
quietly widen the phase to final acceptance.

## 9. Out of scope and handoff

No final regression/test-family disposition sweep, final clean-install/CI
acceptance, candidate approval, production upload, TestPyPI call, announcement,
trial sharing, access/visibility change, publisher/unit handoff, source retirement,
compression/archive cleanup, per-original accounting, source-history rewrite,
semantic redesign, v7.3 reassignment or certification. Existing archives and
useful pending tests/code remain in place. The owner statement that the source
has no private data supersedes confidentiality assumptions from bookkeeping.

Preparation completion will record actual deltas, focused evidence, unresolved
limitations and a concrete P3 input commit. It must retain “Phase 3 paused” until
a separate resume instruction and “Phase 4 candidate sign-off pending”. P3 then
validates the prepared package. Candidate sign-off later checks the already
validated identities; it is not another round of implementation. P5 remains
separately authorized. P6/P7 are separately activated successor work.

## 10. Size and change limits

Proposed incremental ceilings, excluding pre-existing dirty work from the new-edit
count but including it in review scope: 60 changed/new target files; 250 new/changed
runtime lines beyond the existing adaptations; 500 build/workflow/helper lines;
900 focused test lines; 1,200 documentation/planning lines; at most 30 small example
input files / 200 KiB. These are limits for this preparation part, not goals.
Expected work is documentation/examples and build controls, with little new runtime
code. Record measured final counts; exceeding a limit requires an amendment with
its concrete cause, never dropped assertions or archival compression.

Existing approved product/public-tree budgets: 64 MiB tracked content, 1 MiB
ordinary blob, 12 MiB uncompressed package payload, 2 MiB authored public planning,
subject to reviewed exceptions. Measure changed product/package inputs during
preparation. A real public-size conflict goes to an owner decision; the superseded
source Phase 3 evidence cap cannot restart preservation work or retire tests.

## 11. Approval instrument and next stop

Recommended instrument is D1's small corpus-first acceptance stories plus this
prose design; optional panel omitted under D2. No corpus or implementation file
has been created. First approve/amend this preparation scope and instrument;
then author/review the bounded corpus if selected, with answers separate from
its reader entry. Record every open D-row ruling and exact artifact identity.
Implementation begins only on explicit go-ahead under process-phase steps 1–2.

## Implementation findings

None: implementation has not begun. The gap review records observations only.

## Delegated gate — 2026-10-03

The user's subsequent `process-phase 4 auto` supersedes the historical
awaiting-review status above. D1–D7 are each approved as recommended by
**delegated approval (auto=true)**, not a human reading. Authorization covers
corpus authoring and implementation after its recorded approval. The completed
implementability sweep stands; budgets/compatibility remain §§5/10. Optional
spec panel omitted; required independent diff review retained. Phase 3 stays
paused and final candidate sign-off remains pending. Approved pre-append spec
SHA-256: `3a8dcb88bfd33d78ef066e7d7cecb6198509e3ed0283f589ff967e331d3f2708`.

## Implementation findings and bounded execution amendments — 2026-10-03

- I1: current report wires use `constraints[1]` rather than model IDs for
  deadline failures. The test resolves the approved deadline ID in model data
  and requires exactly one matching guarded failure in both CLI/API. The expected
  0/1/0/3 answers and underlying rules are unchanged. Initial harness failure
  was corrected; it did not justify changing domain inputs.
- I2: the first build smoke reused `release` for its venv and artifact directory.
  It failed before install; venv names now have a venv- prefix. Both artifact
  origins remain separate, even though their measured hashes happen to agree.
- I3: the measured preparation host is macOS arm64/Python 3.11.15/uv 0.10.10.
  This is additional preparation observation, not acceptance of the proposed
  macOS 3.13 or Ubuntu 3.11 support profile; final profiles remain P3 work.
- I4: direct T2b successors cover nested/ref/unknown tagged unions, malformed
  derivation IDs, successful v7 field absence and real registry owner resolution
  in test_runtime_preparation.py. Existing v8 reconstruction/source-binding
  controls ran separately (14 selected tests with T2b before its scanner additions).
  They remain P3 pending-test evidence, not a broad archive transfer. The v7
  helper's small local fixture closure is explicitly carried with the new tests.
- I5: T5 successor checks replace only obsolete current bootstrap/README pins in
  test_development_scaffold.py; historical ledger/census gates are not selected.
- I6: changed-reference refusal is a separately identified successor case (exit 3),
  adding protection to the approved missing-reference story without changing its
  answer. Scanner StringIO/string and safe/round-trip parity cases complement
  retained short-comment copying bounds; MIT attribution is retained in source
  and NOTICE.

Each amendment above is **delegated approval (auto=true)** under the user's
Phase 4 scope. D1–D7 instrument, compatibility and §10 budgets stand. The approved
corpus answer meanings remain unchanged; no new format/API or semantic rule lands.
T2b uses the direct successor file rather than committing an unrelated registry
module or compressed judgment test closure. T3 identity validation executes the
documented SHA-256 primitive offline over both wheel/sdist; future service
transport is unimplemented and remains a publication prerequisite. The release
workflow prepares and retains artifacts only. Final clean-install/CI acceptance
and candidate sign-off remain deferred per r3.

Verification refinement: include only
test_development_scaffold.py::test_readme_reflects_current_runtime_stage in the
ordinary gate; current contributor link/twin closure lives in T5. Changed skill
counts were measured at 16 managed links and two real directories per root.
No discovery bytes changed. Added tests preserve default lane exclusions; T4
remains the single explicitly selected distribution node.

### Independent review disposition and target adaptation — 2026-10-03

F1/F2 reproduced and triaged blocking before repair: import namespace depended
on unstaged conftest; identity fixture absent from index. Switch to existing
`support` namespace and carry the exact 512-byte identity fixture; expectations
unchanged. F3/F4 reproduced and triaged hardening of this phase's own guards:
matching broken skill references and comparison overwrite both passed. Added
regressions each failed against pre-fix guards (two pytest failures), then
repaired reference closure and actual workflow command parsing.
The reviewer retained four findings; its executable and sandbox limits stand.

Target successor adaptation: links above now resolve to accepted target P1/P2
records and owner rulings. The listed hashes remain explicitly SOURCE record
identities, not hashes of the differently numbered target successors. Source-only
pause/gap artifacts are origin citations, never runtime prerequisites. Source
spec remains canonical design; this target copy declares these adaptations.

All repairs/adaptations have **delegated approval (auto=true)** under `4 auto`.
Corpus expected outcomes, §10 budgets and runtime contracts are unchanged.
Bounded focused independent follow-up: one additional CLI reading, then stop;
maximum two reviews total. Round 1: four findings, two blocking/two hardening,
zero from a previous review repair. Round 2 checks only repairs and neighbors;
no optional spec panel or broad suite selected.

### Preparation gate outcome — 2026-10-03

Selected focused gate: 98 passed, 1 deselected, exit 0. Explicit single-node
two-wheel smoke: 1 passed, exit 0. Index-only package/test/fixture closure:
45 passed, exit 0, with repository root excluded from console-style imports.
The follow-up CLI did not return a review: it started orchestrating another
reviewer and was stopped before nested execution (exit 1). No second opinion
or convergence is claimed; one complete adversarial reviewer is one reviewer.
Both original review hardening regressions were proven red before fixing.
Preparation is complete once its record lands; P3 stays paused and Phase 4
candidate sign-off pending. No additional review retry or external action.

### Completion record budget amendment — delegated approval, 2026-10-03

Retain the original 1,200-line documentation/planning ceiling. Before authoring
the evidence-bound completion record, increase it to 1,400 lines under the
existing Phase 4 auto delegation: 884 measured authored lines plus about 250
record/digest-binding lines, status updates and final measurements leave too
little room at 1,200. The added 200 lines are a calibrated allowance for
proportionate closure evidence, not product scope. All other budgets and
compatibility decisions stand; no archival campaign or tests are dropped.
