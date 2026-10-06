# RF4 -- Peripheral layering

Status: owner-decided (2026-10-05), delegated approval (auto=true).

## Provenance

Effective approved r2/e1 plan notes/code-refactoring-plan.md sections0,4(RF4),5--10; records004,006,007,008 and005erratum. Base 387aada2f5fad7289481bbc2e15c8dba629d8ce0. User invocation: process-phase RF4 auto. This is repository development, not a domain-model station. No spec panel selected. Plan opinions cover historical plan bytes, not this spec. Harvest reader rf4_harvest was read-only; rows were checked against cited source bytes. Source-side authority control remains the previously approved attestation; no reachable source remote supplied and no new human attestation invented.

## Obligations

| Source | Obligation | Discharge |
|---|---|---|
| plan279--287 | Public safefs, split process/agents, diff calls checker/admission, public oracle, ordered assurance package | Design lanes F,P,D,S,A |
| plan288--296 | RF4-C1 confirmed assurance/synth/API cycles absent; refuted agent cycle already satisfied | T-ARCH |
| plan290--292 | RF4-C2 lane imports to install absent, including type-only imports | T-ARCH,F |
| plan292--294; RF0baseline31 | RF4-C3 all47 original private boundary-to-mutate sites public oracle | T-ARCH,S |
| plan294--296 | RF4-C4 every map layer covered, remaining edges named | T-ARCH, no allowances |
| plan102--114 | SM1 unchanged RF1 pins; SM2 old names/shims and actual patch effects; SM3 scans include all newhomes; SM4 map complete and ratchet | G1,T-MOVE,T-SCAN,T-ARCH |
| plan425 §9 | “SM1–SM4; confirmed SCCs removed; lane-to-`install` edge rule; layering test over every layer” | G1,G2,G3 |
| plan§5 | CONTRIBUTING/AGENTS describe new surfaces; packaged skill citations counted | T-SCAN; 9 base citations, 0 relevant moved-home citations |
| plan§6 | bytes/verdict drift, lost patch seams, shrinking scans, sourceauthority, variant merging, budget growth, metric laundering, staleowners | G1,G2,G3,negativecontrols and decisions |
| plan§7 | no features/tightening/certification/source-owned discharge/broad repair | Boundary |
| §10 RF-D9 | prose or corpus; RF-D5,D10,D11 established compatibility rulings | D1--D3 |
| 006:195--201 | owed artifacts nested directory_identity changing-stat pin | T-PRE, before F |
| 004 RF0 D10; baseline63 | zeroallowance may not grow | D4: remove8 current wrong-way sites, noallowance |
| 008:387--405 | 3 confirmedRF4cycles; RF3OQ1close wording; remainingRF6/RF8/RF7/sourceowned questions | Boundary and openquestions |
| helper-families22--23,44 | filesystem identical candidates and all16variants move without merge | F; stable bodies and identityaliases |
| shim-inventory | allprior aliases retained until releaseafterRF6 plus separateapproval | T-MOVE |

There is no RF4 Residual paragraph. Prior source-owned OQ-V72-P1-ARTIFACT-COPIES, OQ-V52-CLOSE-CANONJSON-1, OQ-V52-P1-IMPORTWALK-1, OQ-V63-CLOSE-HELPER-TAIL-1 remain source-owned.

## Standing rules

RF-R1 preserve exact exits, issueorder, messages, refusals, deterministic bytes. RF-R2 divergent canonical/digest bodies untouched. RF-R3 run pre-move RF1 and T-PRE; add any discovered missing pins before moving that surface. RF-R4 each atomic move includes alias,patch,scan,map adaptations and green focused gates; algorithm edits separate. RF-R5 explicit namecatalog in shim inventory and move evidence; RF-D5 unchanged. RF-R6 scanner union asserts all actual new modules, existing discrepancy and unloaded checks retained. RF-R7 ledger units.json and distributionguard untouched, priorauthority control above. RF-R8 old production_identity/release evidence unavailable on changed bytes. RF-R9 base metrics below and pre-approved ceilings. RF-R10 nofeatures, strictness or defectrepair in production. RF-R11 measured import/patch/scan impact with direct consumers, no full-default replay.

Protocol rules: totality belongs to function -- no new input consumer; existing arbitrary-input and refusal behavior stays pinned. Input cap bounds document, notalgorithm -- no new untrusted work/complexity. Validation order partofdesign -- moved bodies unchanged, diff equivalence cases for refused/accepted inputs. One policy walk -- sharedalgorithm homes, no newper-kind implementations. One normative prose home -- cite plan/protocol; compatibilitymetadata not duplicate semantics. Contested representation bymeasurement -- exact pins, negativecontrols, bodyidentity, actual dependencygraph.

## Goal

Selected gates exit0 with all RF4 cycles absent (literal dynamic and lazy included), boundary private47→0, laneinstall edges→0, wrong-way8→0 and layering test over all6layers. No test expectation/golden changes.

## Design

The exact base signature catalog is evidence/RF4/base-surfaces.json. Moved names retain the exact argument lists, defaults, decorators and bodies from that catalog; move evidence binds old/new path+name+bodyhash. Public aliases add spellings, not parameter changes.

F -- src/gnd/safefs.py (~650lines). Move installer path/mutation closure (_reject_unsafe_relpath,safe_destination,_descend,_temp_name,_rename_noreplace,LeafIdentity,_matches_leaf,_replace_staged_leaf,_fdopen_owned,_atomic_write and constants/errors) verbatim. Public aliases reject_unsafe_relpath,descend,temp_name,rename_noreplace,matches_leaf,replace_staged_leaf,fdopen_owned,atomic_write. Move InstallError/InstallPathError together to avoid reverse install dependency; preserve exception modulequalification. Re-export old names from install. Route every lane and manifest_path_issue to safefs actual public seams. Keep artifact and domain filesystem variants distinct: safefs public qualified aliases expose their existing canonical defining functions; their closure stays in the owning domain where moving it would introduce reverse dependencies. This visibility-only portion is explicit, not claimed as relocating those bodies. No merge of nested artifact directoryidentity and structural variant. T-PRE pays RF1 debt even though nestedbody stays. Artifact aliases use artifact_ prefix on colliding spellings. Domain-specific safety helpers retain domain homes and public ownership seams rather than merging signatures.

P -- process.py (~700) owns EnvironmentFact,ProcessLimits,BoundedProcessResult and bounded runner/drain/cleanup/redaction closure. agents.py (~350) owns adapter/status,error/invocation models,argv,environment selection,feedback,invoke. agent_cli.py explicitcompatibility facade. Models retain historical __module__ so error/typebytes unchanged. Route runner-only consumers toprocess and adapter consumers toagents. Retarget actualglobals patched by tests in atomicunit.

A -- assurance/_wire.py (~350),core.py (~596),inheritance.py (~470),claims.py (~270),evidence.py (~350),transport.py (~212),__init__.py facade. The dependency arrow in plan denotes ascending dependency order: evidence depends claims, claims inheritance, inheritance core or_wire,core _wire. Shared strictdocument/path/closedfield helpers and production/runtime identity plus AuthenticatedAssuranceEvidence go to_wire so core neverimportsevidence. _closed/_strings movefromclaims to_wire so inheritance neverimportsclaims. Old assurance_* shims export all old names, preserve dataclassqualification and capability/token/cache identity. Noauthentication run/newclaims. Registryproductionownerstrings continue resolving.

S -- synth/oracle/constructive.py (~1700) owns assemble constructive prefix through _build_expectations boundary; state.py (~650) owns mutate expectedstate/prediction prefix; mutations.py (~1600) owns mutationalgorithms, private dependencyclosures are explicit. assemble orchestration stays and importsconstructive/state, mutate compatibilityfacade importsstate/mutations. Oracle publicaliases strip underscores (SKIP included); boundary uses public47names. Old names importable, sameobjects. ExpectedState remains provenance-owned. Checker is observation, neveroracle; independence tests and quarantine sourceassertions remain.

L -- report.py functions moveverbatim to payloads.py (~780), report compatibilityfacade; map payloads semantics. Sessionreportimports routepayloads with no sessionprofile/version changes. Export API wrappers export_souffle,verify_souffle,run_souffle,souffle_witness,export_lean,verify_lean,compile_lean moveverbatim to export/service.py (~110). _witness_inputs,witness,replay moveverbatim to witness/service.py (~90). API retains aliases, lane CLI modulescallservices. These remove remainingwrongways without allowance or RF5CLIrewrite.

D -- diff.compare_population calls checker.check_partial,checker.band and admission.build_admission/wire_verdicts directly, builds the exact report projection used by diff's _summary and witness loop. Preserve population-load refusal, anchored checks, reference binding,modelidentity refusal, failclosed70 and derivation/status handling; pre-move paired API observations pin cases that RF1's3diffgoldens miss. No fullAPI clone, diff consumes only its actual report fields. If direct equivalence cannot be met, record finding before repair/amendment.

Each new module enters map. Scope includes original plus newhomes, no reassignment that hides cycles. Curated manifest adaptation selected per D5; frozen release objects not rewritten.

## Decisions -- delegated approval (auto=true), 2026-10-05

| Decision | Ruling and cost |
|---|---|
| D1 RF-D9 instrument | Spec prose, pure move shape, existing RF1 frozen corpus plus pre-move successor pins; no new serialized format/exit/predicate. Existingbytes stay answerkey. Optional specpanel omitted. |
| D2 RF-D10/D11 compatibility | Preserve oldobjects/imports/typequalification; publicaliases accepted; novariantmerge or pinnedname change. |
| D3 numericbudget | Base3RF4SCCs target0; original47boundary edges target0; current8wrongway target0; laneinstall18runtime/typeonlysites in6modules target0. Base198privateedges: final fewer than198; no independent large reduction target beyond fixedcohort. Ceilings130touchedfiles,15000movedproductionlines,2200nonrelocatedproductionaddedlines,1800newtestlines,180nonevidence documentationlines. Metricexception requires pre-edit recordedamendment, originalthreshold retained. |
| D4 zeroallowance | Keep RF0 zeroallowance ruling and eliminate8sites structurally. No planedit or relaxedrankclassification. |
| D5 manifest | Bounded curated sourcepath/hash adaptation with before/afterrowidentity; no unitsledger/distributionguard/frozen release edits. Existingevidence unavailable. |
| D6 review | Required one independent native Codex CLI xhigh read-only/stdin after implementation, maxinitial+oneboundedrepair. RF4 auto selects skillmandated review; previous explicit Codexdestination authorization remains available for same repository reviewworkflow. No providerpanel. |
| D7 authority | Prior named handedoff units remain ownedhere; no reachable source comparison, attestationlimit retained. No newownerhumanreading claimed. |

Approval exactspecSHA and retainedinitialsnapshot recorded separately before production/testimplementation. Amendments append findings and snapshotsha before dependentwork.

## Tests and verification-selection ledger

| ID/obligation | Disposition/command (expected0) | Boundary and invalidation |
|---|---|---|
| G1 SM1/RF-R3 | run: .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_cli_pins.py tests/test_rf1_helper_pins.py tests/test_rf1_semantic_pins.py tests/test_rf1_agent_cli_pins.py tests/test_rf1_session_pins.py tests/test_rf1_pin_harness.py --tb=short | frozen cases/goldens/support, interpreterenv; anymovedconsumer invalidates, runbefore+after |
| T-PRE filesystemowed | run tests/test_rf4_premove.py: stable/change identity refusal and paired directdiff/API cases; .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf4_premove.py --tb=short | runsourcebase beforemove, dirtycontrol disablesidentity comparator and mustred |
| G2 RF4-C1--C4,SM2--4 | run: .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_rf1_layering.py tests/test_rf4_peripheral.py tests/test_rf4_premove.py --tb=short | allsrcgraph,map,catalog,patches/sourcecoverage; graphnegativecontrols mandatory |
| G3 impact | run: .venv/bin/python -m pytest -q -p no:cacheprovider tests/test_install.py tests/test_doctor_uninstall.py tests/test_artifacts.py tests/test_agent_cli.py tests/test_v63_phase2_cache.py tests/test_public_assurance_inheritance.py tests/test_public_assurance_feedback.py tests/test_synth_mutate.py tests/test_synth_boundary.py tests/test_synth_conforming.py tests/test_synth_expectation_independence.py tests/test_synth_false_pass_quarantine.py tests/test_synth_oracle_value_range.py tests/test_synth_tagged_comparison.py tests/test_codegen_emit.py tests/test_codegen_force.py tests/test_codegen_manifest.py tests/test_export_lean.py tests/test_export_souffle.py tests/test_witness.py --tb=short | resolve actual testnames before execution; bounded consumers for moved filesystem,runner,assurance,oracle,wrappers; no exclusions overridden |
| G4 portable | run G2 plus RF1helper/semantic/agent pins under availablePython3.11/3.13 | Pythonminor and targeteditable package, do notclaimLinux |
| G5 scaffold/lint | run selected developmentscaffold+contributorcontrols; .venv/bin/ruff check explicitchangedPythonpaths | no fullrepo lint expansion |
| metrics SM4/R9 | run tools/gnd_arch.py measure atbase/head +compare and deterministicsecondmeasure | sameinterpreter,negativecontrol andgraphlabels; allmodule paths counted |
| RF1/RF2/RF3 frozeninputs | inherit only byteidentity of approvedfixtures/goldens/support and namedpriorfiles; prior testresults notinheritedoverchangedinputs | digests record; successor adaptations taggedseparately |
| historical/full-default/special/native/provider/certification | cadence uv run pytest -q, explicitowner or configuredCIselection | oldclaims unavailable over changedbytes; no broad replay selected |

Impact closure measurement: scan every import/patch/source-scan in RF0tool inventory, select actualaffectedconsumers; broaden focusednodes if newdependency facts require. G3 startinglist may contain historical filenames absenthere; existence sweep substitutes exactcurrentnodes before approval implementation, recorded addendum.

Branchcases: accepted/refusedfilesystempaths and changedidentity; runner success/nonzero/spawnfailure/timeouts/bounds/redaction/versionfailure; assurancecache valid/miss/refuse and proofgraphvalidation; oracle each existingvariant/vacuity/quarantine/independence; diff loads accepted/refused,checkerbandfailures,anchors/references/derivations/admission/projection; shims old/newidentity, actualpatchinterception, scannedhomecoverage; architectural offendingcycle/laneinstall/wrongway/unmappedmodule redcontrols. No untested newsemanticbranch ships.

## Out of scope / boundary

No observablebehaviorchange, tightening, features, newsemanticfamily/schema/version/CLIflag/command, import/executablerename, removingcli.py, performance work, newcertification/assurance/release/publishing claim, broadhistoricalrepair or replay. RF6 modelquery/registry and RF8sessionprofile/versionbehavior remainlater; RF7strictness fullysuccessor. RF3OQ1 andledgerwording onlymilestoneclose. No sourceowned question discharged, no shimretirement. One reviewer is one reviewer, read-only limitations recorded; greenfocusedgates are not a fullrepo or installedcandidate/Linux verdict.

## Size and implementability sweep

Estimates ~10500 relocatedproductionlines, ~500routing/alias lines, ~500newtests, ~80documentationlines. CeilingsD3. Anchors all inspected atbase; safefs.py andpackages intentionallynew. Threecycles canbe removedby independentdependencyclosures, no targetequalbaseline. Zeroallowance achievable via movedpayloads and servicewrappers. Algorithmorder/fields unchanged. T-PRE precedesmoves. Required scopedcurrentcasesnotcachedoldverdicts. Signaturecatalog controls exactarity/decorators. Nooptionalphase prerequisite. Reviewbound max2declared now.

## Implementation findings

None yet.

### A1 -- implementability detail and selected-node resolution (delegated auto, 2026-10-05)

The assurance wire/core boundary also moves CorrespondenceDigests verbatim from core into _wire; otherwise the wire capability type imports core and recreates a cycle. Preserve its gnd.assurance qualification. Actual optional-lane focused successors are tests/test_public_lean_export_successors.py, tests/test_public_souffle_successors.py, tests/test_public_souffle_input_contract.py, tests/test_public_optional_value_witness.py and selected current witness cases; historical absent export/witness test filenames in G3 are superseded here before implementation. Native tests remain excluded. The laneinstall baseline above understated sites: RF0tool base has 18 codegen/evolve/synth sites plus one infrastructure manifest_path_issue site; target0 lane sites remains unchanged. The codegen/evolve/synth modules are five, not six. Initial approval snapshot retains the preliminary inventory wording.

No new semanticbranch is authorized. Safefs visibilityaliases preserve existing artifact/domain defining homes; actual installer closure moves. Diff successor answers cover every RF1checkerpair plus invalidpopulation and check/admission70, adding cases for gaps as discovered before routing. Initial+one repair review bound retained.

### A2 -- atomic move and routing gates (delegated auto, 2026-10-05)

Move units run G1 and their selected affected-consumer nodes; end-state graph targets G2 run after the separate routing commit. Imports/dependency homes and compatibilityaliases change in the move unit, algorithm bodies remain verbatim. Qualified import statements inside moved functions may retarget lower homes without changing control/data flow; moveidentity compares algorithms with only the declared import-module substitutions normalized, retaining original/bodydigests and explicit substitutions. Nonimport algorithm changes (diff orchestration) land later behind pre-move answers.

Baseline sandbox result385passed7failed is a measured macOS confstr warning contamination, not a sourcechange. Required G1 reruns outside sandbox with same frozenexpectedbytes before moves. Optional service wrappers are unpinned by RF1; add focused refused/accepted service observations on sourcebase before their move, using explicit currentlocal successors (no nativeprovider).

### A3 -- closure and public compatibility imports (delegated auto, 2026-10-05)

Initial moved gate exposed a late-defined _xor_single_role dependency of expected_state. Move that unchanged helper into state, alias it back from mutations; no body/answerchange. Initial graph has no wrongway/laneinstall edge and only API/diff plus RF8session SCCs, but480privateedges vs198base because explicit compatibilityfacades import private names. Before routing, approve public spellings for moved closure names at their new defining homes (stripped underscore, compat_all for __all__), and have facades import those public names under their oldaliases. Existing private spellings and objectidentities remain. Publicoracle is the RF4 deliverable; this exposes the actual dependencyclosure rather than exempting facades from measurement. Target fewerthan198 remains, originalinterimmeasurement retained.

Patch/scan adaptations are still pending in the uncommitted moveunit; failing141/457 preliminarygate is retained, not accepted as a greenmove. Once amended tests/globalowners are current, run mandatory green gates before committing the move. Source-baseline32 service tests pass outside sandbox; one sandboxprocess refusal differed, retained separately.

### A4 -- preserve the shared report pipeline (delegated auto, 2026-10-05)

A direct reconstruction of diff report fields would duplicate anchor, reference, redaction and fail-closed orchestration. Revised D design moves the eleven-function dependency closure of api._run_check (560 lines) unchanged into checking_service, below entry. Diff supplies checker.check_partial explicitly to its public check_report; that shared domain service invokes admission.build_admission and wire_verdicts. This removes the public API facade from the dependency path while preserving one implementation of the existing report pipeline. API retains every old helper alias and the public check signature. It interprets the plan's direct call as the domain-level path, with no API import, rather than duplicating the existing checking/admission algorithm. All graph and byte targets remain unchanged. No new behavior is authorized.

During the uncommitted move, body identity and focused tests also found two late constructive helpers (_witness_map and _alethic_refs); they moved unchanged with the Builder closure. An initially colliding public _json alias overwrote the json library; decode_json is the noncolliding spelling. Import-only lint cleanup removed unused compatibility aliases, which the identity gate detected; explicit compatibility imports were restored. These are implementation findings, not pre-existing defects or accepted behavior changes. The move remains uncommitted until the selected gates are green. The body comparator removes import nodes, preserving all remaining AST nodes; split imports do not change algorithm identity.

### A5 -- compatibility capture and documentation allowance (delegated auto, 2026-10-05)

Current-byte controls exposed imported-name compatibility gaps and two test lookup owners: RF2 session mint capture must patch checking_service, with the source root anchored to gnd rather than the now-packaged assurance; codegen race controls must patch public safefs.atomic_write and the actual private inner helpers. Retain original inputs, assertions, successor answers, and failure output. Old imported names remain available, catalogued separately from relocated algorithms. The repaired session controls pass28 cases; the prior5failures are retained. These adaptations do not authorize algorithm or answer changes.

Before the completion record and remaining evidence, increase D3's total touched-file ceiling130 to250 and non-evidence documentation ceiling180 to800. The approved spec already uses approximately180 lines; retaining five dated amendments, the mandatory completion record and review dispositions cannot fit the initial estimate. Retained failed-gate output and independent review add evidence files; no evidence is discarded to fit the count. Production ceilings15000 moved and2200 nonrelocated added and test ceiling1800 remain unchanged. Final exact measurements and original limits will be recorded; this is delegated agent approval, not a human reading.

### A6 -- measured move accounting (delegated auto, 2026-10-05)

Precommit whole-source comparison estimates11833 added,7974 moved and3859 nonrelocated production lines. The2200 ceiling is exceeded: the500-line routing/alias estimate was false. Explicit historical qualifications, public closure spellings, imported-name compatibility and expanded import blocks add physical lines despite unchanged function/class algorithms. Approve a4200 nonrelocated ceiling before the separate routing edits, retaining2200 as the original limit. No metric exemption or moved-line reclassification is introduced; the final committed gnd_arch comparison must satisfy4200,15000 moved and all other limits. This is a budget overrun disclosed and delegated, not a claim that the original budget passed.

A5's approximate180-line spec statement was imprecise: its pre-edit spec measured126 lines. The larger allowance covers the completion record and retained review dispositions as well as the spec; final documentation arithmetic must report actual lines. Existing zero-allowance and fewer-than198-private-edge thresholds remain unchanged.

### A7 -- live lookup audit (delegated auto, 2026-10-05)

The patch inventory found the unreadable-producer refusal control retargeted to evidence instead of _wire, the defining mint lookup. Hardening relevant to SM2: an observed-call assertion is red against the current test (producer-patch-pre-fix,1failed); repair only its patch owner to _wire and retain the original refusal/band/scope assertions. Report warning injection similarly required checking_service.load_population; routed-direct exposed the stale API patch and the corrected current gate passes. Strengthen import-body normalization with preserved binding inventories and a live deletion/rename control; normalize a copy so the negative-control comparison cannot mutate its own input. No production algorithm or frozen answer change.

### A8 -- contributor fixture closure (delegated auto, 2026-10-05)

G5's contributor dirty-copy test fails before its mutant because CONTRIBUTING already links tools/gnd_layers.json and the shim inventory, but the copied boundary omits both. The same failure is reproduced against an isolated complete phase-base387aada snapshot (scaffold-base-reproduction,exit1). Triage: blocking for this selected G5 control, test-fixture hardening only. Copy the two existing link targets into the dirty fixture before its clean control; retain all four mutations and failure predicates. This is not a production fix or a broad historical repair. The original red and exact base are retained.

### A9 -- test data accounting (delegated auto, 2026-10-05)

The committed test diff adds358 Python test lines and3043 fixture/data lines (2996 are the source-base paired diff answers). The original1800 test-line ceiling passes for Python but fails if all test inputs count:3401 total. Approve3600 total added test code/data before review repair or completion edits, with the1800 Python ceiling retained. Report both categories and the original total overrun; never hide answer data as evidence or omit it from touched-file counts. Frozen corpus stimuli and answers remain unchanged; only RF4's explicitly pre-move successor data is new. This amendment changes accounting allowance, not expected answers.

### A10 -- review reproduction scope (delegated auto, 2026-10-05)

The independent review is running; the root separately reproduced20missing imported bindings at old API/install/assemble paths (review-missing-imports-pre-fix.json). Triage: blocking SM2 compatibility, restore only predecessor import bindings after the report. Add regression identities against their original imported objects, observed red before repair. Candidate identity controls target the removed assurance.py; add bounded current-behavior successors for source/missing-source/omitted-roster and assert the actual assurance/core.py member changes. Retain original rejection meanings and cache C18/C20 outcomes. No broad historical, installed-distribution, provider/native or certification run is selected. These reproductions may run now; dependent repairs follow final report and reproduction, with one bounded repair review at most. Production algorithm and frozen answers remain unchanged.
