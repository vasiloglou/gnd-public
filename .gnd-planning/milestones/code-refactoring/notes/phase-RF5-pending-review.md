# RF5 -- CLI command groups

DRAFT: required independent Codex review is pending explicit provider authorization. This is not a completion record.

The CLI now registers commands through18 groups, parses once and invokes the selected handler. cli.py is667 lines versus9056 at the phase base and approved1500 / milestone 2500 ceilings. The134 historical definitions/constants are aliases;116 algorithms remain AST-identical. All predecessor imported names remain. Source controls and patch lookups move with their definitions.

## What shipped

Argument classes/converters live in commands._arguments; shared output algorithms live in commands._output. Checking presentation, lifecycle, solve and optional-export wrappers keep exact old adapters. Offline handlers for verification, synthesis, measurement, extraction, generation, conformance, recovery, evolution, document/fidelity checking, review and experiment lifecycle have domain-service homes. commands.exp retains the unchanged live experiment invocation and its exclusive closure by A3 so generation's deterministic import boundary stays offline. No algorithm is rewritten to fit the graph.

All18 groups expose add_parsers(subparsers, *, command=None) and handle(args, parsers). Per-command calls preserve all25 top-level registration positions and52 parser paths. Root defaults propagate to parsed Namespaces; original43 leaf argv cases explicitly check effective handlers. No new command, flag, schema, version or refusal is introduced. CLI historical helper imports remain for compatibility; their retirement is RF-D5.

The RF0 architecture tool now measures entry-point imports under an explicit policy: the bootstrap plus18 groups,13 exact service targets, helpers/exits, and45 exact reasoned source/target exception pairs. Exceptions cover retained import bindings or original thin presentation, optional adapter, solve/lifecycle and declared-live command boundaries; no wildcard exemption. Injected forbidden mapped imports, omitted/extra groups, and a CLI masquerading as a service are rejected. Every213 modules is mapped; all6 layers remain clean, wrong-way0, allowances0. Only the named RF8 session SCC remains.

Private import sites rise124→319. CLI sites rise18→125 because moved private names acquire cross-module compatibility aliases; relocated command/service closures add further measured coupling. RF5 does not claim a private-import reduction. This cost stays visible rather than being hidden through assignment-style imports.

## Criteria and standing rules

RF5-C1:667≤1500<2500<9056, with an over-ceiling countercheck. RF5-C2: nonempty measured entry-point rule and seeded forbidden-import/scope controls. SM1:392 RF1 pins,43 pre-move byte observations/43 effective disabling controls. SM2:134 same-object aliases,116 unchanged ASTs, original imported bindings and class pickle identity. SM3: complete defining-source scope, omitted-home rejection, current global patches and semantic producer ownership normalization. SM4:213 mapped modules,6 clean layers, no allowances.

RF-R1/R2 preserve observed output/exit and algorithms; RF-R3 successor pins frozen on29915d9before source moves; RF-R4 aliases/patches/source scans travel atomically with definitions; RF-R5 names retained without retirement; RF-R6 whole-file guard scope widened with refusal controls; RF-R7 authority files unchanged, no attestation inferred; RF-R8 prior certificates unavailable for current bytes; RF-R9 pre-approved finite budgets with original predecessor drift retained; RF-R10 no feature/tightening; RF-R11 named affected-consumer selection, no broad replay. Standing totality/caps/order/cost/refusal properties retain predecessor bodies and focused hostile/negative controls. Review reproductions, triage and convergence follow the selected skill.

## Verification selection

G0 predecessor: 340 pass; frozen successor pre-pin: 86 pass, before any production move. G1: all six frozen RF1 files: 392 pass and29 affected original mutants killed with green control. G2: direct 261 checks, successor 86 checks, layering/tool 75 checks:422 pass. G3: the 24 harvested consumer files plus helper's corpus consumer and focused construction guards:1120pass. G4: Python 3.11/3.13 each 546 pass over direct/successor/CLI/helper selection. G5: scaffold/contributor/credential/offline97 pass / 1 deselected, plus explicit changed-path Ruff exit 0. Counts overlap; they are not a combined acceptance universe.

All 434 frozen input hashes remain unchanged. Successor 43 case/answer bytes remain frozen. All 167 original mutation rows retain ID/stimulus/expected-red meanings;28 source file paths alone are retargeted. Original broad/census/evidence/proof/native/distribution lanes remain on explicit-owner or separately selected CI cadence. Changed old certificates and release identity claims remain unavailable; frozen unchanged inputs alone may be inherited.

## Implementation findings and refuted premises

The promised RF0 entry-point predicate did not exist; layering was a different test. RF5 supplies an executable scoped rule and leaves normative plan repair to milestone close. Two consecutive prior original-budget misses triggered an explicit delegated pre-phase re-plan, retaining RF3/RF4misses and their arithmetic.

The initial successor pin instrument targeted non-called export functions, invalid exp/lifecycle argv and an invalid scalar judgment stub. A1corrected these before moving production, retaining original instrument data/results. A2corrected the exact closure census to116definitions/18constants. Initial over-bundled imports introduced wrong-way solve edges; filtered closure imports corrected those without algorithm edits. Moved class __module__ preservation means inspect.getsource(class) cannot locate its body through cli.py onPython3.14; identity/pickle remain historical and algorithm/source tests read the actual defining file. No selected consumer required class-source introspection.

Initial moved-impact gate6failed / 1105 passed: two offline-generation placement defects corrected by A3, one successor lookup intercepted by its own hostile-import guard corrected by resolving already-loaded modules, and three pre-existing phase2instrument defects. The three invalid extension-module patches reproduce from a frozen29915d9git archive before correction; retarget only to extension_core, unchanged fixtures/production. Repaired controls pass.

Parser-local solve labels were initially left in the preceding registration block and caused collection refusal. Move labels with their consumer. A new handler-default test incorrectly inspected a child's local get_default rather than inherited Namespace values; frozen observations were already green, and the corrected control parses all43 original argv. Lint autofix removed four compatibility imports after a misplaced multiline suppression; the unchanged predecessor-binding test caught the loss, and exact imports with line-local dispositions restore it. A4normalizes only successor doctor's interpreter directory for portable runs; no answer or original RF1normalizer change. All red histories remain retained.

## Independent review and convergence

PENDING. One reviewer is one reviewer. Initial review plus at most one repair review; findings must be reproduced and triaged before fixes; each fix must have a specific observed-red regression. No opinion over RF4bytes is borrowed. Review confirmation/limitations and branch-table self-audit will be recorded here after the current review.

## Refactoring review

What did this phase reveal about existing structure that should change? Refactors EXECUTED: one command-registration/dispatch home per group; separate argument/output infrastructure; exact domain-owned handler closures; preserve explicit live invocation at its command boundary; complete source/lookup observers travel with ownership. The same frozen/direct/affected-consumer gates cover them. Renaming/retiring private compatibility handlers is deferred to RF-D5 rather than changing names during a move.

## Boundary -- what this phase does NOT establish

No new commands/flags/version/schema/semantics, performance, tightening, merging divergent helpers, broad historical repair, source-owned discharge, installed acceptance, publishing, new certification or native/provider execution beyond the expressly selected required independent review. Old certificates describe old bytes. RF6 model/query/package responsibilities, RF8 session cycle/resume/version meanings, RF7 successor strictness/FIFO/media types remain. Milestone close owns meta-node exemption wording, RF3 SCC scope wording and RF4 visibility-only filesystem/shared-checking wording. Prior source-side control is not a new owner attestation. GitHub's observed billing refusal is infrastructure, no remote acceptance verdict.

The43successor observations establish selected accepting/refusal leaves, not every internal branch. AST equality does not prove all behavioral equivalence or imported binding semantics. Class source introspection through historical __module__ is a documented limitation; identity/pickle algorithms remain pinned. Same-seat review is bounded disagreement evidence, not a proof or panel. Portable macOS3.11/3.13runs do not establish Linux, installed artifacts or native/provider functionality. Approval marks are delegated agent rulings, not human readings. No source-owned unit is certified or handed off.

## Open questions

RF6 package/query responsibilities, RF7 strictness/safe-filesystem successor questions, RF8 session SCC/resume/version meanings retain named owners. RF1 meta-node exemptions, RF3 SCC scope wording, RF4 filesystem/shared-checking wording and RF5's newly supplied entry predicate are reconciled at milestone close. RF-D5 owns shim/private alias retirement. Source-owned authority/import-walk/helper-tail questions remain source-owned. RF1's original boundary stays standing when its owed RF5 surface observation clause is annotated by this later record.

## Final status -- 2026-10-05

The explicit provider authorization, independent review and current phase record resolve the earlier pending state. See [010-phase-RF5.md](../010-phase-RF5.md) for current claims, dispositions, gate evidence and limits. This note preserves the earlier history.
