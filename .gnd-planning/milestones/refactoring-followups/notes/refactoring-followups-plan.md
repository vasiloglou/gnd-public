# Refactoring follow-ups · issues 297–308

Revision 2, 2026-11-25. The light panel reviewed r1 at commit bf874602. The owner selected delegated approvals (auto=true), light plan/close panels and Claude Code phase-diff reviews. Revision 2 incorporates the dispositions below and carries no separate review opinion.

The [refactoring close](../../code-refactoring/019-milestone-close.md) accepted a set of measured limitations. This successor gives twelve of them an owner, a test or a recorded decision. Completion requires an accepted disposition for every row below, passing evidence for every selected change, a migration story for changed public behavior, and owner acceptance of any residual with a named destination. Deferring a change keeps its issue open.

## 0. Binding design rules

Preserve existing import identities until the RF-D5 retirement gate. Keep layer allowances at zero and register moved modules in `tools/gnd_layers.json`. Preserve caller-specific primitive resolution, refusal order, meaningful variants and the exact model-query exception inventory. Apply the project's six [standing design rules](../../../../.codex/skills/process-phase/references/project.md) in each spec. Historical evidence stays bound to its original bytes.

## 1. Scope, sources and authority

The numbered issues below define scope. The [close sweep](../../code-refactoring/notes/close-question-sweep.md), [amended plan](../../code-refactoring/notes/code-refactoring-plan.md) and [measured close results](../../code-refactoring/notes/close-results.md) supply the historical rulings. The close supersedes the earlier project progress summary. An experiment-claim census measures domain-model claims and cannot establish runtime import, parser or replay behavior. Issue descriptions and close measurements are baseline evidence from their respective authors. Re-measure the affected surface when each phase starts.

## 2. Proposed product contract

Start with the pool error that already has an expected outcome. Protect behavior with independent fixtures before changing routing or shared helpers. Make session recovery explicit by version. Introduce portable evidence only under a new, identifiable contract. Keep exported PyRel programs self-contained. Offer a documented deprecation window before removing public import aliases. These are proposals for owner decision.

## 3. Dependencies and homes

The suggested execution order is F1 through F8. F1 can start after plan and spec gates. F2 builds the characterization support for F3–F7. F4 also uses F1's input-boundary work. F6 uses F3's agreed lookup semantics. F7 waits for F3 and F5 so that target imports and patch sites have settled. F8 can proceed independently once source texts and an owner ruling are available. Closure waits for all eight dispositions.

Use the existing pool and shared input components (`synth.pool`, `infra.input_policy`), model address and export components (`model.address`, `export.pyrel_emit`, `export.pyrel_runtime`), and session replay and judgment components (`exp.session_replay`, `exp.session_judgments`). Check actual call sites when harvesting each phase. The index review flagged 98 descriptions older than their code. A separate index review is available at the owner's discretion.

## 4. Obligations and phase gates

| Phase and issue | Source in the close | Deliverable and acceptance criterion |
|---|---|---|
| F1 · [#300](https://github.com/vasiloglou/gnd-public/issues/300) | C64, RF9 CI repair | Oversized pools raise the domain exception with one input finding. Exercise the exact limit, one byte over and malformed JSON. See [first spec](phase-F1-spec.md). |
| F2 · [#306](https://github.com/vasiloglou/gnd-public/issues/306) | C21/C23/C24/C32 | Reconcile the two RF1 normalizers with before/after fixtures. Bind declared-input bytes so a changed input fails the check. Compare a separately derived list of plan surfaces with the pins and report each omission. Exercise both no-evaluator fixtures with a deliberately observed call before deciding whether to share their guard. Correct Q3's two hex-validator labels and distinguish the file hasher in successor documentation. |
| F3 · [#298](https://github.com/vasiloglou/gnd-public/issues/298) | C-D1 | Measure both import graphs. Propose breaking the three core package-initializer cycles, test cold imports and public re-exports, enforce zero core cycles and list each of the four remaining lane groups by name. Record any changed baseline. |
| F3 · [#305](https://github.com/vasiloglou/gnd-public/issues/305) | C39/C40 | Enumerate exact allowed domain, raw and IR reads. Pin each caller's result and resolver before migration, route through ModelIndex or model_queries, remove only its own exemption. Exercise two-parent closure plus committed rejected_proposals and deontic_notes. Record any irreducible site and reason. |
| F4 · [#301](https://github.com/vasiloglou/gnd-public/issues/301) | C24/Q2 | Trace the three review-service calls to the canonical writer. Test NaN and both infinities at the writer and each reachable public boundary. Propose strict refusal, preserve finite output bytes and verify callers' failure paths. Document any unreachable case. |
| F4 · [#302](https://github.com/vasiloglou/gnd-public/issues/302) | B4/C20 | Inventory readers by path and cap. Prioritize bounded reads before parse and YAML limits before construction. For each selected reader test normal input and limit crossings. Compare media-type results across differing host tables before choosing a deterministic mapping. Record a per-validator error-policy decision and scope any larger rewrite separately. |
| F5 · [#299](https://github.com/vasiloglou/gnd-public/issues/299) | C-D2 and RF1 session replays | Rule separately on the rate helpers, sorted-set/canonical pair, three validation overrides, and two session-entry helpers. Pin each site, including exceptional results, before consolidation. Require a common semantic contract for every merger and an RF-D10 ruling for a rename. |
| F5 · [#303](https://github.com/vasiloglou/gnd-public/issues/303) | C16/F12 | Test CLI resume for v2, v3, v7 and v8 with the completed result present and removed. Propose retaining explicit refusal where replay cannot reconstruct the result faithfully. A recovery ruling requires byte-equivalent results and no duplicate work on retry. |
| F5 · [#304](https://github.com/vasiloglou/gnd-public/issues/304) | C18/RF8 D4 | Compare two directory roots containing the same experiment. Propose a content digest for identity and an experiment-relative locator where the runner needs a filename. Verify equal new prompt/evidence digests across roots, changed identity for changed contract bytes, and replay of old sessions under their recorded rules. |
| F6 · [#307](https://github.com/vasiloglou/gnd-public/issues/307) | C27/RF2 D4 | Feed GND and the emitted runtime the same declared and positional references, including absent and malformed cases. Compare routed results/refusals, run the export in isolation and verify identical generated bytes on fixed inputs. Any required generator change goes back for a release ruling. |
| F7 · [#297](https://github.com/vasiloglou/gnd-public/issues/297) | A5/RF-D5 | Give every row of the [shim inventory](../../code-refactoring/notes/shim-inventory.md) a canonical replacement, consumer/patch-site audit, release and disposition. Exercise old import identity during deprecation, target lookup sites in patch tests and exercise new imports after approved retirement. Require a separately approved retirement phase and migration notes naming each removal. |
| F8 · [#308](https://github.com/vasiloglou/gnd-public/issues/308) | C66 | Retrieve the original text and provenance for OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1, OQ-V52-P1-IMPORTWALK-1 and OQ-V63-CLOSE-HELPER-TAIL-1. Obtain a transfer or retirement ruling per ID. For transfers preserve wording and owner in the [public register](../../../open-questions.md). For retirements record authority and rationale. Missing originals remain explicit open dependencies. |

## 5. Documentation and compatibility

F1 owns the loader contract, F2 the test inventory, F3 the architecture and query exceptions, F4 the accepted input/error tables, F5 session recovery and format guidance, F6 export compatibility, F7 the migration guide and release notes, F8 the question register. Update component descriptions alongside changed code. Adjust a packaged skill only when its user-facing instructions change.

## 6. Risks and controls

A green module graph can hide package initialization cycles. Measure each graph separately. Equal outputs on session replays can hide unreachable paths. Include a direct fixture per helper. Re-recording goldens could conceal a compatibility break. Compare old and new outputs and identify every intended delta. A timestamp, host path or local MIME database can introduce machine-specific behavior. Use controlled pairs that vary only the relevant input.

## 7. Scope boundaries

Other close residuals, production publication, historical evidence regeneration and global validator redesign require separate scope. F7 may span releases. The first release after RF6 satisfied a timing condition only. The owner still selects removals and timing.

## 8. Execution and review

The start-milestone workflow leaves this plan and its first spec for review. Select the maintained plan-review instrument explicitly and record the reviewed digest, findings and owner gate. Each implementation phase requires its own spec, approval, focused tests, independent diff review, refactoring review and record. Use topic PRs. The close uses the project's plan-review bar and a separate close record. Merge, release and certification require their own owner authority.

## 9. Verification and close evidence

| Phase | Evidence the record must retain |
|---|---|
| F1 | Focused pytest summary, observed exception class and findings, valid pool identity and boundary controls. |
| F2 | Normalization parity, changed-byte and evaluator-call negative controls, missing/extra surface comparison, corrected terminology. |
| F3 | Before/after graph memberships and exact exception inventory, cold-import results and per-consumer parity. |
| F4 | Caller reachability and finite-byte comparisons, reader-by-reader budgets and refusal order, MIME controls and deferred validators. |
| F5 | Per-site helper tests, CLI exit/result/state matrix for four versions, two-root and legacy digest fixtures. |
| F6 | Paired routing results and isolated standalone import check, before/after emitted digests. Record unavailable native execution separately. |
| F7 | Release-specific migration table, patch lookup tests, retained/removed import matrix and owner decision. |
| F8 | Four original IDs reconciled to four signed dispositions and corresponding register entries. |

Use default-lane focused pytest and ruff for changed code. Select later exact nodes and time budgets at each spec gate. Closure reconciles all twelve issues, links the eight records and identifies the owner and trigger for any accepted deferral. No live provider budget is needed for the proposed engineering tests.

## 10. Owner decisions

Open decisions, in execution order, include F1's byte-count contract, F3's core-only cycle gate, F4's input and validator scope, F5's semantic mergers, recovery policy and evidence version, F6's generated-byte policy, F7's release window and F8's four ownership rulings. Proposed defaults appear beside their acceptance tests in §4. The first decision is detailed in [F1](phase-F1-spec.md).

## Plan-review disposition and governing amendments · r2

| Finding | Ruling and evidence due |
|---|---|
| Reader selection and input policy | F4 must cover the public model and population YAML entry points and the pool file intake. For each, inventory byte, event, depth and alias behavior where applicable, demonstrate already-effective controls and implement missing applicable controls under its phase gate. Inventory other loaders, separately disposition each with reason and target. Include the MIME variance experiment and validator error inventory even if compatibility warrants deferral. |
| Shim timing | F7 delivers the audited inventory, patch migration and release guidance. Remove aliases only if the release and retirement gate have been selected. Otherwise retain the aliases, name the release trigger and owner, and leave #297 open. |
| Source records | All four original mints are indexed by the archived source register. Require four dispositions, or an explicitly accepted and tracked residual naming the missing mint and recovery owner. |
| Review status and closure counts | Record the plan gate in 002-plan-gate.md. Close reconciles twelve issue dispositions across eight phase records. A deferral needs an owner, trigger and open issue. |
| Model queries and dependencies | Preserve exact *accounting* while shrinking exceptions per verified migration. ModelIndex owns model snapshot access, model_queries owns applicable pure routing operations. F6 consumes the pinned positional reference resolution. F2 supplies normalization parity, the surface manifest and deliberate guard-failure controls before later phases change pins. |
| Historical counts, layering and test selection | Capture phase-start denominators. Document each added or removed site relative to the issue and apply the same criterion to all live sites in scope. For moves run the live layer-map and wrong-way-edge tests and cold imports for affected public entry points. Repository policy specifies focused consumers. A full historical-suite gate exceeds the selection. |
| Owner decisions and provenance | F1 counts on-disk bytes. F2 shares guards only if both deliberate observed-call controls fail as intended. Issue #299 itself specifies the three overrides. F5 enumerates supported versions and runs recovery controls for the four named versions plus controls for other supported paths affected by its implementation. Later exact policy decisions belong to the phase spec before edits. |

Reviewed r1 SHA-256 6ca733e30bffb9637b1534800adf2ebf72df84af381bcd7ea2ffc8bdb1d384be. See [the finalized advisory report](../evidence/plan-panel/PANEL-REVIEW.md). One review round, then verify these repaired criteria against implementation and fixtures.

## Close amendments · r3, 2026-11-25

The r2 wording above is retained as the plan the phases executed. The following dated rulings govern its exit criteria. [Measured results](close-results.md) and [decisions and remaining work](close-delta.md) give the cross-phase evidence.

- F3 supersedes the proposed zero core-initializer count with a membership limit for the three existing core groups and cold-import controls. All three depend on implicit parent edges that sibling imports already create. Thirteen lookup sites migrated. The model/query maintainers own the remaining exact list under #305. [F3 ruling](../005-phase-F3.md).
- F4 keeps single-pass, first-crossing depth refusal. If an alias or syntax error comes later in the same input, depth wins. The named public readers and writer are covered. Wider intake and MIME contract changes remain with the named component owners under #302. [F4 ruling](../006-phase-F4.md).
- F5 preserves older session profiles and offers a digest-bound portable prompt in v6–v8. The tests and later integration checks cover both formats. [F5 ruling](../007-phase-F5.md).
- F6 confines pairwise agreement to positional references in the common admitted domain. The two readers' full malformed-ID policies differ. [F6 ruling](../008-phase-F6.md).
- F7 retains live shims for the first public release carrying the notice. The release owner selects later removals in a separate phase under #297. FU5 already retired three helpers. [F7 ruling](../009-phase-F7.md).
- The owner authorized all four F8 transfers and publication in PR #310. The source historical states and later triggers stay visible in the public register. [F8 ruling](../010-phase-F8.md).

This close candidate awaits its separate light panel and delegated acceptance record. Eight phase records cover twelve issues.
