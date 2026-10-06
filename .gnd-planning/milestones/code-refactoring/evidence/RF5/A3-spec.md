# RF5 -- CLI command groups

Status: owner-decided (2026-10-05); delegated approval (auto=true), specification precedes implementation.

## Provenance

Source base29915d9; effective notes/code-refactoring-plan.md §§0,4RF5,5–10, plan-gate003 and erratum005; records006–009. Prior reviews describe prior bytes. No spec panel is selected. Current implementation carries no RF5 independent opinion. Read-only harvest covered full plan, all prior narrative records, all tests Python and packaged skill Markdown/Python; results were checked against present CLI, plan and selected files. No code has moved at this gate.

## Obligations harvested

| Source | Obligation | Discharge |
|---|---|---|
| §4RF5 | commands groups with add_parsers(), set_defaults(handler=), optional check_args(); thin first, medium next, heavy domain services; cli.py remains; shared output home | design/catalog and G2 |
| RF5-C1 | cli.py≤2500 and lower measured ceiling | G2 asserts≤1500 versus9056 baseline; countercheck extra lines |
| RF5-C2 + panel002 qwen-r2 predicate4 | executable entry-point import rule, including CLI boundary and reasoned exceptions | G2 tool function with injected forbidden mapped import; no empty group inventory accepted |
| §9RF5 | “SM1–SM4; cli.py ceiling; entry-point rule”; CLI tests and RF0-counted files patching gnd.cli | G1/G2/G3 |
| SM1/RF1-R3 | unchanged RF1 pins; owed handlers pinned green on pre-move bytes | G1 and successor handler corpus, without editing old answers |
| SM2/RF-R4,R5 | every moved name old import identity, qualified names and effects of retargeted patches; atomic units | catalogue plus G2/G3; retirement RF-D5 remains |
| SM3/RF-R6 | scan actual defining modules, module-unloaded checks cover introduced scope | source guard adaptations and explicit visited-set equality in G2 |
| SM4 | map every new module, all six clean layers remain clean | full-map G2 and layering tests, no allowances |
| §5 | AGENTS/CONTRIBUTING actual command pattern; current skill citations | count nine module citations, zero moved CLI Markdown citations; fallback parser/exit comments remain valid under compatibility |
| §6 drift | two consecutive original ceilings missed; explicit pre-phase re-plan | pre-phase-replan.json delegated ruling, original overruns retained |
| §6 risks | digest/output drift, ineffective patches, shrinking scans, authority, divergent families, rewrites, misleading metrics, stale ownership | G1–G5 plus limits and budgets |
| §7 | no observable changes, new features, tightening, source-owned discharge, certification or broad repairs | out of scope |
| §10RF-D9 | choose approval instrument | D1 prose; byte/exit contracts unchanged, successor pre-move corpus rather than new semantic corpus |
| RF1 record006 | owed handler-byte pins; batch stdout.buffer bypass; support-normalizer debt | successor accepting/refusal cases per moved owed handler; preserve batch emitter as separate byte contract; do not edit original rf1 support |
| RF2/RF3/RF4 | live shims, bounded manifest adaptation, original source attestation boundary, unavailable certificates; RF6/RF8/close ownership | frozen authority files; bounded changed-row adaptation; named carryovers |

## Standing rules

RF-R1 preserve all CLI/API names, messages, refusals, deterministic bytes and exit bands. RF-R2 move canonical and divergent encoder bodies verbatim. RF-R3 pre-move pins precede any surface move. RF-R4 move unit includes aliases, patches and source scans, green selected gates. RF-R5 all old CLI names/import bindings retained and inventoried, no retirement. RF-R6 widen original scans, assert complete scope. RF-R7 frozen units.json and test_public_distribution.py; prior attestation is not a new human attestation. RF-R8 current-byte release identity unavailable, no certificate inheritance. RF-R9 measured9056→1500 and finite budgets below. RF-R10 no feature/tightening. RF-R11 explicit measured impact selection, no full default run.

Paid-for standing rules: totality, caps and algorithm cost are preserved by unchanged bodies and their focused hostile/refusal controls; no new parser/loader policy. Validation order is preserved by original parser statements and dispatch branches. One policy walk: one command registration traversal and one measured import rule cover every group. Normative prose stays in the plan/skill, this note records design decisions only. Contested representations are settled by pre/post byte observations and live negative controls. Each new absence/identity/scan/routing claim has an accepting and disabling control; audit declared criteria rather than relying on reviewer coverage.

## Goal and design

Retain all52 parser paths and exact help/exit/output behavior while making cli.py a ≤1500-line compatibility/bootstrap file. It retains original imported bindings and aliases, console gnd.cli:main and python -m gnd. Parser registration order remains byte-for-byte original; commands with multiple registrations can accept add_parsers(subparsers, *, command: str | None = None), preserving their original positions. Each group sets handler defaults on its parsers; handle(args: argparse.Namespace, parsers: dict[str,argparse.ArgumentParser]) -> int preserves existing conditional routing, argument checks and errors. main(argv: list[str] | None = None) -> int builds _BandSafeParser, preserves version action, registers in original order, parses once and invokes args.handler(args). No new flags/schema/exit bands.

New commands groups: checking (import,validate,diff,coverage,check,verbalize), verify,synth,measure,extract,export,codegen,conformance,recovery,evolve,doccheck,fidelity,review,exp,solve,lifecycle,judgments,witness. Existing export/witness parser/service adapters retain their original lazy boundaries. _arguments owns parser classes, StoreOnce, positive validators and format options. _output owns text/envelope helpers in the semantics layer; batch sys.stdout.buffer stays its separately pinned contract.

Planned-homes.json and predecessor-signatures.json are the exact per-symbol design catalogue (signatures, original AST source and import closure), not pointer-only obligations. Estimates: ~6000 handler/helper body lines across existing lanes, ~1600 parser/dispatch lines, ~300 shared output lines, ~500 thin adapters. Services use actual lower payloads and safefs modules under historical local binding names; report/installer exception objects are identical. _live_assurance keeps its original call through a compatibility alias to checking_service.certify_assurance, allowing unchanged body and no reverse API edge. Every moved function/class retains __module__='gnd.cli' and old identity. No delegation back to cli or dynamic global lookup bridge is introduced.

Heavy service homes include export.verification_service, extract.service, codegen.service, recovery.service, evolve.cli_service, fidelity.doccheck_service/service, review.service, exp.cli_service, synth.service/corpus_service and measure.service. Shared synth index/transaction helpers stay separate from measure to avoid a new cycle. Existing conformance service API stays unchanged; its CLI adapter home is conformance.cli_service. Thin checking/lifecycle/solve/export adapters may keep necessary existing domain imports only in a named per-module allow-list with exact import targets and reasons; the entry rule never admits a wildcard exception. _arguments is infrastructure, _output semantics, command groups entry, services existing lanes. No new architectural allowance or RF8 session rewrite.

Execute one RF5 phase with coherent units: pre-pins/tool negative controls; move definitions/closures with aliases and all dependent patch/scan updates; then parser registration/routing extraction and thin main. Process thin groups before medium then heavy within dependency-safe units; do not leave intermediate commits with broken imported dependencies. Atomic move bodies remain unchanged except explicitly declared module-binding substitutions; routing changes are separately gated against original observations.

## Decisions -- delegated approval (auto=true), 2026-10-05

| Id | Question and cost | Ruling |
|---|---|---|
| D1/RF-D9 | prose versus new semantic corpus | prose, existing serialized/exit semantics unchanged; separate original-source successor byte pins land before move |
| D2 | drift condition covers prior ceiling misses | conservative yes; pre-phase-replan.json is execution re-plan under named RF5 auto, no milestone-plan rewrite; no erased overrun history |
| D3 | part count/coupled closures | one RF5 phase, bounded coherent commits; no fourth numbered part |
| D4 | compatibility versus line reduction | keep every original imported/global name as alias; trim only moved definitions and parser/routing ownership, no shim retirement |
| D5 | entry rule tool promised but absent | record refuted premise now: gnd_arch has no entry-point predicate atbase; add explicit measured rule, allowed-target catalogue and counterchecks, require complete group/parser scope |
| D6 | release manifests and authority | adapt only touched curated rows and newly introduced homes; original row provenance retained; units/distribution test frozen |
| D7 | review | required independent Codex stdin read-only xhigh review, initial plus at most one repair, reproduction/triage/red regression; one reviewer is one reviewer; no spec panel |

## Tests and verification-selection ledger

| Gate/obligation | Disposition/command (expected0) | Boundary/invalidation and justification |
|---|---|---|
| G0 current-base pins | run .venv/bin/python -m pytest -q tests/test_rf1_cli_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_session_pins.py | CLI, handlers, original frozen answers; movement invalidates result |
| G1 SM1 | run all six RF1 pin modules (cli,helper,semantic,agent_cli,session,pin_harness), unchanged answers | final complete392 frozen pins; macOS sandbox warnings retained separately with matching unsandbox baseline gate |
| G1 owed handlers | run tests/test_rf5_handler_pins.py plus independent seeded disabling controls; each actual invoked handler case has deterministic bytes/exit baseline; include25 owed surfaces including judgments/witness wrappers | predecessor snapshot, original argv/artifacts; capture fixture once before moves; no recapture of new answers |
| G2 direct SM2/3/4 and C1/2 | run tests/test_rf5_commands.py tests/test_rf1_layering.py tests/test_gnd_arch.py | alias/signature/class pickle identity, unchanged nonimport AST, complete defining scans/map, observed routing patch, parser order/default handlers, ceiling and forbidden-import disabling controls; any new module/input invalidates |
| G3 measured patch/scan consumers | run the24 selected inventory files (1111 current selected nodes; no broad lane override); plus focused new-service accepting/refusal consumers | includes codegen_force/manifest,coverage_cli,exp_bands/spec,extract_cli,install,measure_negative_control/offline,poolfile,public_derivation_evaluation_complete,public_payload_alias_sites,public_registry_runtime,recovery_adversarial,report_json,review_bands,RF1 cli/session,skeleton_e2e,solve,v63_phase4_helpers,v6_phase3_distribution,verification_fixes,verify_cli; dependent corpus-helper callers also selected if retargeted |
| G4 portable | run current direct command/pin/owner tests on3.11/3.13, same corpus/algorithm/selection | source, fixtures and dependencies same; no Linux/native/installed claim |
| G5 source/docs | run scaffold/contributor/offline/credential controls and explicit changed Python paths Ruff | no borrowed whole-repository lint verdict; new docs/source adaptations invalidate selected inputs |
| Frozen source inputs | inherit only digest-checked unchanged RF1/RF2 input bytes and authority controls, cited evidence fromRF4 | mutated stimuli retain ids/snippets/expected red; moving source file paths invalidates actual runner and requires adapted controls |
| Broader suites | cadence uv run pytest -q only on explicit owner request or separately scoped CI | full default/historical/census/evidence/native/distribution not selected; changed old claims unavailable |

Negative controls: forbidden actual mapped import makes entry rule red; extra CLI lines make ceiling red; removed catalogue alias red; omitted defining module red; handler stub changes its frozen byte observation; wrong routing patch must visibly change exit/output. Reproduce reviewer findings before accepting, triage before fixes, every fix observed red on pre-fix bytes.

## Out of scope and inherited boundaries

No new commands/flags/version/schema/semantics, performance, tightening, merging divergent helpers, broad historical repair, source-owned discharge, installed acceptance, publishing, new certification or native/provider execution beyond the expressly selected required independent review. Old certificates describe old bytes. RF6 model/query/package responsibilities, RF8 session cycle/resume/version meanings, RF7 successor strictness/FIFO/media types remain. Milestone close owns meta-node exemption wording, RF3 SCC scope wording and RF4 visibility-only filesystem/shared-checking wording. Prior source-side control is not a new owner attestation. GitHub's observed billing refusal is infrastructure, no remote acceptance verdict.

## Size and implementability sweep

Base cli9056,179 mapped modules, private124, wrong-way0, no allowances, only RF8 SCC. Final cli≤1500 (strictly below both9056 base and2500 milestone ceiling). Budgets:320 touched files including retained evidence,12000 moved production lines,4000 nonrelocated production lines,3000 total added test code/data,1500 added non-evidence documentation lines. Based on the measured107 definitions plus18constants,~7500 defining/helper lines and1633 main lines,28 patches and~20 source/namespace consumers. Arithmetic and misses are retained if any delegated amendment becomes necessary before dependent work.

Implementability: original parser positions and52path semantics can be preserved with per-command registration; callable handler defaults do not alter existing action values/help. Actual domain closures can be given one home without importing CLI; output can be below lanes with original algorithms and lower alias bindings. Missing tool predicate is supplied as phase tooling, not falsely inherited. Every named criterion has a falsifiable control. Owed handler observations must run green before moves; failure stops that surface. No dependency on optional/native/certification work. Original budget misses trigger the explicit re-plan above rather than a quiet continuation.

## Approval instrument

Spec prose. Delegated approval is the user's “process-phase RF5 auto”, not a human reading of these bytes. Snapshot SHA-256 is recorded in phase-RF5-approval.json before creating implementation or successor tests. Optional spec panel omitted. Corpus answers are captured from frozen base and kept separate from the new fixture README, retaining prior answers on any later amendment.

## Findings recorded before implementation

The RF0 tool does not implement the promised RF5 entry-point import rule. Its existing layering predicate is a different contract. RF5 adds an actual entry rule with full nonempty scope and negative controls; this refutes inherited tool-coverage assumptions without editing the milestone plan. The retained RF4 static source census also misses several CLI guards, so the manual checked inventory is included in G3.

## Amendment A1 -- successor instrument repair before production moves

Delegated approval (auto=true), 2026-10-05, authorization process-phase RF5 auto. The initial43leaf instrument reports74pass/12fail while production remains9056lines unchanged. Export disabling patches named non-called run functions instead of actual dispatch; exp-init id and lifecycle --user flag rejected in parser before handler; judgments disabling stub returned an invalid scalar; doctor PATH differed between capture and gate. Retain initial cases/answers and red gate. Replace only these successor instrument premises: dispatch targets, valid EXP-001-rf5 id, actual --global flag, dict outcome stub and fixed interpreter-bin PATH environment. Recapture only from the original29915d9 production bytes, then freeze the corpus before any move. This is an explicit pre-move successor answer amendment, never an RF1 answer change. Runtime policy remains untouched.

## Amendment A2 -- exact closure census before moves

Delegated approval (auto=true), 2026-10-05, authorization process-phase RF5 auto. The exact AST census is116 definitions plus18 constants (134 names), correcting the107-definition estimate; current CLI remains9056lines. Predecessor G0 is340passed, and final successor handler instrument is86passed, including43effective disabling controls. All production source still equals29915d9. Planned name-reference closure has no SCC. _INDEX_VALIDATOR belongs with _INDEX_SCHEMA in synth.corpus_service; case kind constants belong to fidelity.service; review constants belong to review.service; _stale_smoke_modules belongs to codegen.service. These exact homes are already reflected in the design catalogue. Existing budgets stand. The individual source-source `_live_assurance` call is preserved via the lower checking_service._certify_assurance identity alias; this is a lookup compatibility binding, not a new algorithm.


## A3 -- Preserve the declared-adapter command boundary

Delegated approval (auto=true), 2026-10-05, authorization process-phase RF5 auto. The moved-impact gate observed two generation/offline guard failures: putting _cmd_exp_run beneath gnd.exp makes its unchanged declared_adapter import reachable from the deterministic generation closure. Before relocating further, amend the home of _cmd_exp_run and its exclusively used _next_session_run_root, _run_tests_mode_bridge and _session_result_exit closure to gnd.commands.exp. All four algorithms and historical identities remain unchanged. This is a named heavy command-boundary exception: experiment invocation includes a declared live adapter, while artifact evaluation and other lifecycle services remain offline. No guard is weakened and no provider is invoked. Retain the A2 catalogue, red gate and changed-home evidence; original budgets stand.
