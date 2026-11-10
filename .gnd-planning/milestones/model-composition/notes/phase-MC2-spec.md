# Phase MC2: consumer support

## 1. Status

r1, delegated approval (auto=true),2026-11-10, exact spec/corpus bound in record010. MC1 is locally complete in records008–009 at55a7d89a. Implementation starts only after the gate record and corpus commit.

## 2. Provenance

Derived from the owner-approved model-composition r3 plan, sections 0–10 and amendment a1; MC1 spec r5 and records002–009. The named milestone's current `auto=true` delegation covers a later exact-byte MC2 ruling. MC1 semantic source remains c7fc66dd; initial full/default had25 failures, including19 test-inventory/cache failures. Corrected test candidate64a42f12 has a passing marked census; its full/default run finished6 failed,18609 passed,801 deselected,1 warning in3941.86s, retaining exactly the six frozen failures. Record008 accepts MC1 locally; record009 retains five trailing-space lines from verbatim run output as an artifact-only residual. This spec has no independent review opinion. The required phase diff review uses one Codex CLI reviewer, prompt on stdin, existing authenticated parent environment; no repository environment file and no reviewer subagent.

## 3. Obligations

| Source | Obligation | Discharge |
|---|---|---|
| MC2-C1, predicate 5, MD7/15 | Every MC1 admission row gets an explicit supports/refuses disposition | §6.1, T1 |
| MC2-C2, risk tempdir half-model | No unaccompanied copy reaches work | Retain copy-route guards; T1 |
| MC2-C3, O6, MD9 | Full composed verbalization plus include header; no include-free output change | §6.2, T2–T4 |
| MC2-C4, rule 0.5, O14 | Positive codegen/conformance currency follows same-run dependency verification or refusal | Keep refusal before currency; T1/T8 |
| §9 MC2 | New tests plus suites for affected consumer rows | §8 ledger |
| §0.1/2/3 | Single resolver; no half-model; frozen include-free variants | §4, §6.3–4, T5–T9 |
| §0.4/5 | Only includer writable; verify dependencies before freshness | This phase writes no model; rooted resolution and private input binding |
| §0.6/7 | Measure outputs; red-first refusals; size stop | §8/10 |
| §5, O11/12/13 | Index updates, zero architecture allowance, ModelIndex and explicit shims | §6.5, T9 |
| prior 003/005/006 | Authentic intake hash after refusal allowed only for closed report metadata; six known suite reds and 13 lint errors remain | Retain batch behavior, §8/9 |
| a1, MD17 | Owner docs checkpoint after MC1 merge; tutorial decision before MC4 | Not discharged here; §9 |
| §7 | No nested includes, overrides, new identity/report version or multi-file publication | §9 |

## 4. Standing rules bound here

1. **Totality belongs to the function:** API compose's new rooted admission remains behind its existing total error adapter; include errors retain value-free reason IDs. Verbalization accepts already validated loader Models; deliberately assembled unresolved include Models are refused before rendering. T3/T6 use malformed and unresolved inputs.
2. **Input cap versus algorithm:** no second resolver or per-element new work. Header rendering is one bounded-declaration walk, maximum eight declarations, with the existing per-datum renderer cap. A direct header-layer timing control performs 1,000 renders of eight maximum-length declaration fields with a three-second ceiling, excluding file loading. The declaration count remains bounded at eight; this is a bounded latency control, not an asymptotic claim.
3. **Validation order:** resolve/verify all vocabulary bytes before population compose/check work. For check replay, initial rooted load precedes rereading the authored file; compare its captured hash before record verification. T6/T7 spy that later work is untouched on refusal. Existing invalid include order is unchanged.
4. **One policy walk:** the existing loader and shared include reason helper remain canonical. Consumer decisions are an admission inventory, not per-kind resolution code. Header iteration has one body for all declarations.
5. **One prose home:** representation-format.md remains normative. The spec describes implementation and links it; it adds no second product-format definition. Header wording follows MD9. No schema change. The source sweep found that the current CLI only exposes `verbalize population`; the plan's model review wording therefore needs a new `verbalize model` target, specified below, rather than pretending an existing command does it.
6. **Measure, don't assert:** retain exact include-free verbalization bytes and compose/check dictionaries before edits; compare independently on the candidate. New refusal regressions are observed red first, with their genuine predecessor behavior recorded.
7. **Milestone single resolution/no half-models:** api.compose invokes only load_model_bytes_composed for include-bearing raw bytes; checking uses only load_model's composed Model. Unrooted copied consumers stay refused.
8. **Frozen variants:** preserve legacy unrooted api.compose loading for include-free inputs (including reference refusals); no runtime program, digest algorithm, report version or public callable signature change. Private Model metadata is omitted from serialization.
9. **Only includer writable:** no writer enabled in MC2; api.compose is read-only and CLI writes only its existing population/record outputs after success.
10. **Freshness:** a path-based composition invocation verifies pinned include bytes during initial loading. A later authored-file hash cannot be paired with an earlier different Model; §6.4 binds them. Codegen/conformance remain refused before positive currency.
11. **Size:** original estimate 250 source /400 test lines; stop at 375 source /600 tests, gross added source including metadata and exact source-pin successors. MC1's exception does not transfer.

## 5. Goal

A loaded or path-based include model verbalizes the full composition with one MD9 header per declared include. Population compose and path-based composition checking consume a rooted, verified composition, returning exit 0 or the existing semantic exit when inputs are valid; invalid include inputs return exit 3 without population/record output. All remaining direct-byte/copy routes retain their explicit include refusal. Include-free public outputs are byte-identical.

## 6. Design

| Capability | Consult searches | Found | Decision |
|---|---|---|---|
| Render model review | `render model verbalization`; `include header review text` | model.verbalization, src/gnd/model_verbalization.py | adapt existing header; no second renderer |
| Compose anchored populations | `compose population lineage`; `merge anchored sources` | model.composition, src/gnd/composition.py and api/checking_service | reuse population algorithm, adapt intake only |
| Register model review at CLI/API boundary | `disclosure output surfaces`; `command value-bearing registry` plus entrypoint-rule source | infra.disclosure, cli.api, cli.dispatch | adapt existing API and exact disclosure table; keep entrypoint import boundary |
| Resolve pinned vocabulary | MC1 source/index reread | model.loading, gnd.model loader | reuse explicit-root bytes loader, no resolver copy |

### 6.1 Admission inventory

Every MC1 row is re-read before the exact-byte gate. Refused rows retain their existing adapters and tests. The inventory below is the intended decision, source-bound by evidence/MC2/admission-reread.json (49 lexical call sites, with explicit segment/file hash conventions). The enclosing definitions and call spellings were checked against current source before the gate.

| MC1 row | Decision for MC2 | Reason |
|---|---|---|
| R1 validate/check ordinary paths | supports, unchanged | Already rooted in MC1 |
| R2 witness service | refuses | Raw snapshots and evidence binding are not rooted dependency bundles |
| R3 witness io | refuses | In-memory artifact lacks dependency root |
| R4 judgments | refuses | Saved raw model/evidence protocol |
| R5 API judgments | refuses | Same saved artifact protocol |
| R6 population compose API | supports | Explicit original root and same captured raw bytes available; §6.3 |
| R7 exp session tempfile | refuses | Copy would lose dependencies |
| R8 exp session contract | refuses | Contract snapshots need their own dependency bundle design |
| R9 exp replay | refuses | Replays saved snapshots |
| R10 exp judgments | refuses | Saved judgment/model protocol |
| R11 Lean path and raw renderers | refuses | Raw source/identity and standalone outputs need a separate composition contract |
| R12 Souffle path and raw renderers | refuses | Same standalone export boundary |
| R13 PyRel rules | refuses | Exported raw model has independent admission |
| R14 render_pyrel | refuses | Embedded runtime remains frozen |
| R15 oracle runtime entry helpers | refuses | Runtime receives raw document, no GND dependency resolver |
| R16 applications | refuses | Temp copies and independent executable artifact |
| R17 ILP | refuses in MC2 | Authored proposal preservation belongs to MC3 |
| R18 discover | refuses in MC2 | Authored proposal preservation belongs to MC3 |
| R19 evolve | refuses in MC2 | Ownership, repin and CAS belong to MC3 |
| R20 batch | refuses | Closed intake/policy/currency contract is distinct; authentic refusal metadata unchanged |
| R21 checking composition replay | supports for model path; refuses include-bearing in-memory Model | Root and captured authored-file binding needed; §6.4 |
| R22 codegen manifest/emit | refuses | No claimed currency over unverified dependency set |
| R23 conformance currency/service | refuses | Same, before currency comparison |
| R24 extract | refuses | Raw artifact hashes and generated evidence need a dedicated binding contract |
| R25 fidelity/doccheck | refuses | Evidence admission and raw-model identity not widened |
| R26 measure | refuses | Before/after raw hash protocol not widened |
| R27 recovery verify | refuses | Dependency-free temporary copies not enabled |
| R28 RAI import | refuses | Round-trip writer would lose authored ownership |
| R29 standalone skill scripts | refuses, own nonzero adapter | No GND loader dependency; cites gnd validate |
| R31 direct render_lean | refuses | Raw public admission remains explicitly guarded, independent of R11 |
| R32 direct render_souffle | refuses | Raw public admission remains explicitly guarded, independent of R12 |
| R30 raw example scripts | no include input; existing negative scan remains | Tutorial example is MC4's explicit successor, not enabled here |

Newly found call sites inherit their parent row with an explicit test ID. No unrooted loader changes behavior.

### 6.2 model_verbalization.py (about 25 source lines)

Preserve signature `render_model_verbalization(model: Model | str | Path) -> str`. A private `_include_lines(loaded: Model) -> list[str]` owns declaration-metadata admission and this header-only work.
After coercion and JSON-value representability checking, an include-bearing Model must carry matching loader metadata for every declaration; an unresolved manually constructed Model is refused with the ModelValidationError carrying include:unresolved before text. Check orphan attachments before the empty-includes return. Compare declaration count and each ordered id/path/sha256 triple with its IncludedFile metadata, using total dictionary access so malformed manually supplied declaration dictionaries refuse rather than leaking KeyError or TypeError. No filesystem read belongs to this render-layer check.
Add `refuse_unresolved() -> NoReturn` to the existing gnd.model._includes module as a thin public-module hook to the one `_refuse("unresolved")` issue factory. The renderer imports this hook rather than the private issue constructor. No second issue-policy implementation.

Within `=== Header ===`, append in authored declaration order:

    Includes <id> (<path>, sha256 <first12>)

Use existing `path_segment` for untrusted ID/path segments and `line_text` for terminal structure; ordinary safe tokens keep the literal MD9 spelling. Do not sort declarations. Render remaining composed objects, facts and constraints exactly once through existing machinery. Metadata admission prevents accidental rendering of an unresolved constructed Model; it is not an unforgeable proof against trusted Python callers that deliberately replace private attributes. It adds no guarantee over mutation of nested model dictionaries by callers. For empty includes the original lines are unchanged. A fact_type_constraints-only manually constructed Model is unresolved too.

### 6.2a commands/checking.py (about 35 source lines)

Add `_cmd_verbalize_model(model_path: str) -> int` and `gnd verbalize model MODEL`. Render only after the entire rooted load succeeds, then write the existing review text to stdout. No output file option or JSON report is introduced. Delegate through the new small `api.verbalize_model` boundary, so command registration does not import checking algorithms or add an entrypoint exception. ModelValidationError prints the existing issue adapter and returns3; ordinary ModelLoadError, YAML parse errors, OSError/ValueError/TypeError/RecursionError refusals return3 without review text; escape control structure in error text with the existing line_text helper. A FileNotFoundError for the named model returns66, including a read race. Included dependency absence is already a structured include refusal and stays3. Unexpected defects retain70. Dispatch model before reading population-only arguments. Keep the existing population target unchanged; additive command help is the intended CLI extension, not frozen old help text. Test real CLI clean/missing/malformed/tampered cases and existing population behavior.

### 6.2b api.py, disclosure.py (about 12 source lines)

Add `verbalize_model(model: str | os.PathLike[str] | Model) -> str`, an explicit new public Python view, and include it in __all__. It uses existing `_check_model_input`, `_resolve_model` and the canonical model renderer; it returns the existing review text, with ordinary renderer/load exceptions preserved. No new dictionary/report wire shape. The CLI calls this API and prints text only after success. The existing `api.verbalize` remains the population view.

Register `gnd verbalize model` and `api:verbalize_model` as Surface(kind='every-mode') in the one disclosure table: this is the caller's own model review, including authored example metadata. It does not claim to redact supplied population facts. No population is an input. Existing population disclosure behavior remains unchanged. Test both ordinary and customer invocation contexts, including a model carrying authored examples, and exact surface inventory coverage. Do not add a new entrypoint exception or relax tools/gnd_arch.py.

### 6.3 api.py population compose (about 30 source lines)

Public `compose(model: str | os.PathLike[str], directory: str | os.PathLike[str]) -> dict[str, Any]` is unchanged.
Read the authored file once with existing capped read. Preserve MC1's shared guard preflight and its malformed-input fallthrough: call guard_bytes; catch only its include:unsupported-route as the signal to use the rooted loader. Other errors retain the existing adapter. This preserves the legacy public loader lookup even for a malformed buffer and introduces no new parser/resolver copy. For include-bearing documents call:

    load_model_bytes_composed(raw, source=model, root=Path(model).parent)

When the shared guard does not identify an include declaration, preserve the old `load_model_bytes(raw, source=model)` variant and its patch lookup. Existing malformed-input fallthrough stays intact. Do not let support accidentally admit reference-bearing models the original population algorithm refuses. Pass selected composed Model and the exact original `raw` to unchanged composition.compose.
Preserve `gnd-compose/1`. Include-specific ModelValidationError uses shared include_reason in existing error.message, exit 3; legacy invalid models still say `invalid model`. The CLI's existing success-only write rule stays unchanged.

### 6.4 documents.py, model/__init__.py, checking_service.py (about 35 source lines)

Add only private metadata:

    _authored_sha256: str | None = PrivateAttr(default=None)

When `_load_model_at(data, *, source, descriptor)` successfully composes an include model, bind hashlib.sha256(data).hexdigest() to its Model. It commits to the captured authored bytes; it is not serialized, a new public identity, or a guarantee about later filesystem state.
For `_run_check_raw`, keep include-bearing in-memory Model refusal when composition is requested; path input goes through existing `_resolve_model` rooted loader without the old blanket path guard.
In `_composition_view`, when `model.includes` is nonempty, require hash of reread `model_raw` to equal model._authored_sha256 before using the record. Mismatch becomes existing CompositionError input refusal; do not run population derivation. Initial load already verifies all include pins in this invocation. Source replacement after snapshot load is not a publication claim; check reports the verified snapshot as of that read. No new positive currency/publication promise.
For include-free Model paths preserve the existing guard for a changed file that has acquired includes. Use shared guard_bytes to refuse that transition before pairing old Model and new raw document. References remain governed by the existing composition algorithm.

### 6.5 Source pins and index (about 20 source/support lines)

Any exact definition pins over deliberately changed bodies get named MC2 successors with their predecessor retained, not broad allowlists or rewritten historical evidence. RF1's full CLI tree/help/probe coverage is affected by the additive leaf: preserve every historical artifact, approve only the verbalize parent/new model child delta, and test every other parser unchanged. Author expected argparse structure/help from an independent reference parser or literal approved actions, never by overwriting old goldens or capturing the product as its own expected answer. Bind new expectations per supported Python minor where argparse formatting differs; the new leaf's help0/input64 controls remain live. Update descriptions of touched canonical components and regenerate inventories. The additive parser target intentionally changes the exact parser inventory from58 to59, and the disclosure CLI leaf inventory from49 to50 (the generic every-mode namespace count becomes50-16-4); add its exact every-mode disclosure rows and preserve the one registry walk; pin the new count and exercise the new path, preserving handler checks for every old path. Map no new module; verify runtime import graph with zero allowances. Preserve aliases and defining metadata.

## 7. Decisions

D1–D8 ruled as proposed by delegated approval (auto=true),2026-11-10; this is not the owner's personal reading:

| ID | Question/readings and cost | Delegated ruling (2026-11-10) |
|---|---|---|
| D1 | Broader support vs bounded §6.1: broad support requires dependency bundle/runtime/evidence protocols; refusal is exit3 | Bounded support, rows explicit |
| D2 | Compose with rooted loader vs keeping refusal: new supported outcome0 with same original raw hash, no resolver | Support R6 and rooted R21 |
| D3 | Reuse only in-memory Model vs private raw binding: unbound raw reread can pair different snapshots | Bind private authentic SHA, refuse mismatch |
| D4 | Corpus-first vs prose: enabled routes change exit contract; small narrated corpus is reviewable and must be red first | Corpus-first for support/refusal branches, retained expected outputs separate |
| D5 | Spec panel vs implementation review: no concrete unresolved format uncertainty justifies a panel | Omit optional spec review; one independent Codex CLI diff review, max one repair confirmation; reproduce findings |
| D7 | Existing CLI has only population verbalization; direct renderer import also violates the thin-entrypoint rule. New model target with a small API view vs a new entrypoint exception: the view costs about12 source lines and preserves the boundary | Add text-only model target and api.verbalize_model returning str; no new report format or entrypoint exception |
| D8 | Model review may include authored samples: treating it as value-free is inaccurate; redacting full model semantics would change the existing renderer contract | Register caller-model review as every-mode, with no supplied population input; preserve existing population disclosure |
| D6 | Codegen/conformance enable vs refuse: currency proof would expand beyond bounded support | Refuse before positive currency |

## 8. Tests and selection

Author narrated cases and separate answer key under evidence/MC2 before implementation, bind their hashes in the gate. No expected answers inferred from candidate outputs.

| ID | Test file/case | Expected |
|---|---|---|
| T1 | test_mc1_guards.py, updated only R6/R21 successors plus all retained admissions | All retained routes exit3/include:unsupported-route or their documented standalone adapter; next work never called |
| T2 | new test_mc2_consumers.py: fixture path + loaded Model full verbalization, multiple declarations reversed order | Render includes headers in declaration order; included types and owned attached constraint represented once |
| T3 | same: unresolved manually built Model, orphan attachments, mismatching/missing declaration metadata; newline/control ID/path | Refusal before partial text; no forged output line |
| T4 | same: independently retained include-free model verbalization bytes, Path/Model/API/CLI | Exact byte equality through existing renderer and new API; CLI0 |
| T5 | same: split CT2 fixture plus unchanged anchored sources, compose and replay check; flat control | Compose0, replay semantic result matches twin outside existing allowed identity/path fields |
| T6 | same: missing/tampered include and malformed authored input, API and CLI | Exit3, include reason where applicable, no output files; derivation spy untouched |
| T7 | same: authored file replaced between load and replay raw read, plus include-free-to-include transition | Exit3 before verify; unchanged bound case succeeds |
| T8 | same/MC1 guard cases: unchanged includer with changed pinned file through codegen/conformance | Exit3 unsupported before positive currency; no artifacts |
| T9 | private metadata serializers, identity/syntax homes, aliases and source scans | No new serialized fields or identity deltas; zero architecture allowances |
| T10 | bounded header rendering measurement/control | 1,000 header renders of eight maximum-length declarations complete within three seconds; no loading in measured layer; maximum8 remains fixed |

Unchanged refused rows inherit the current MC1 full/default execution and retain the direct R-row sentinels; they receive no new source bytes in MC2. Their broad historical suites are not independently reselected. Changed renderer, compose and check replay rows get the focused suites below; new source successors receive their exact dirty controls.

Exact focused gate to finalize after inventory reread:

    uv run pytest -q tests/test_mc2_consumers.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_mc1_review_regressions.py tests/test_model_verbalization.py tests/test_composition.py tests/test_ike_q3.py tests/test_v70_phase5_adversarial.py tests/test_v62_phase6_verbalization.py tests/test_rf1_cli_pins.py tests/test_rf5_commands.py::test_all_parser_paths_receive_command_handlers tests/test_rf5_commands.py::test_entrypoint_rule_covers_all_groups_and_rejects_forbidden_imports tests/test_rf6_packages.py tests/test_rf8_structure.py tests/test_rf6_query_policy.py tests/test_disclosure_mode.py --tb=short

Default lane filter retained. Lint: `uv run ruff check src tests`, compare exact13 known baseline findings. Index: `python3 scripts/components_index.py changed --base 55a7d89a --strict`. Add specific source-pin consumers found during gate sweep; don't launch broad unrelated suites. MC1 candidate full/default and marked census were selected independently and completed in record008. MC2 does not automatically select another full/default or exhaustive census. At milestone close the selected candidate run must cover the final semantic candidate; current MC1 evidence does not attest to later edits.

## 9. Out of scope

No model writer, repin, copied dependency bundle, export runtime change, saved witness/session format, codegen/conformance enablement, identity/report version, schema or normative vocabulary change. MC1's six known default failures and13 lint errors stay explicit. MC3 owns evolve/discover/ILP. MC4 owns shipped tutorial example, docs/skill changes, MD17 disposition and owner docs reaction. Do not merge PR154 without explicit owner authority; the after-merge docs checkpoint remains pending. Certification/publication are not selected.

## 10. Size

Estimate about160 source/support additions plus500 test lines, under original250/400 phase estimate. Conservative stop remains375 source/600 test lines, including moved/copied code and source-pin successor support. The600-test stop counts Python tests/support; raw narrated corpus/expected-data lines are measured separately, as distinct from executable tests. Count at gate and at each semantic lane; stop for owner if exceeded.

## 11. Approval instrument

Proposed corpus-first: prose above plus narrated admission cases and independent expected outcomes. The narrated corpus is evidence/MC2/corpus/README.md with separate answers.json and frozen expected outputs. Record010 binds their exact reviewed meanings and bytes before implementation. Before ruling: re-read every admission site, record its exact definition and retained/refused behavior; assemble corpus; run implementability sweep; hash artifacts; write delegated ruling with source authorization, budget, decisions and one CLI reviewer selection. Only then may MC2 implementation begin after MC1 completion.

## 12. Implementability sweep findings

- 2026-11-10: the assumption that a model-verbalization CLI already existed was refuted by commands/checking.py:_register_verbalize/handle. Only population is registered. §6.2a/D7 makes the required addition explicit before any gate or implementation. Add plan repair at close clarifying the exact command rather than silently broadening an existing target.
- Source context reread inventory: evidence/MC2/admission-reread.json, 49 lexical guard sites; R31/R32 are explicit successor inventory rows from MC1 r5. This count does not prove completeness over arbitrary dynamic callers.

- Draft sweep: every new CLI leaf must enter the exact disclosure inventory. The renderer can carry authored samples, so §6.2b selects every-mode rather than asserting a value-free output. commands.checking may not import model_verbalization directly under the RF5 entrypoint rule; a small public API view reuses its already allowed dependency boundary.
- Draft sweep: MC2 authored-byte binding and MC3 historical snapshot retention both extend private loader/Model metadata. The plan's disjoint-files premise cannot justify parallel implementation; coordinator execution remains serial, and close records the overlap as a plan repair if MC3 adopts the snapshot design.

- The source-inspection draft did not state a reproducible function-hash convention. Before gating, all49 source calls were revalidated and their file/definition hashes regenerated with an explicit ast.get_source_segment convention. No opaque draft hash is used as approval evidence.

## 13. Declared writes and gate readiness

Runtime: src/gnd/model_verbalization.py, src/gnd/model/_includes.py, src/gnd/commands/checking.py, src/gnd/api.py, src/gnd/disclosure.py, src/gnd/documents.py, src/gnd/model/__init__.py, src/gnd/checking_service.py. No new runtime module.

Tests/support: tests/test_mc2_consumers.py; bounded successors in tests/test_mc1_guards.py, tests/test_rf1_cli_pins.py, tests/test_rf5_commands.py, tests/test_disclosure_mode.py, tests/test_rf6_packages.py and tests/support/rf9_ci_sources.py only where their exact current inputs change; test pin fixtures beneath evidence/MC2. Keep historical predecessor bytes and dirty controls. Unchanged consumers inherit record008's actual default execution plus retained direct guard sentinels. New test/support source counts toward600.

Catalog: dev/components/COMPONENTS.md and its mechanically generated views for touched capabilities. Planning: this spec, MC2 corpus/evidence/review notes, next numbered gate/phase records and milestone README. Normative product-format/schema bytes are unchanged.

Readiness sweep: the existing renderer and API/CLI boundaries can satisfy the admitted view; explicit-root byte loading already resolves all pins and references; existing composition accepts the composed Model and original raw bytes and refuses references. Private authored-byte binding fits the frozen Model serialization contract. Every newly enabled/retained boundary has a discriminating narrated case. The full CLI pin surface was found and added before gate. No unmet optional dependency or new report version is required. MC1 completion is committed; merge is a separate pending owner gate and is not an MC2 prerequisite.

## 14. Implementation findings

- The first review-lane run had18 passes and one harness overstatement: C10's array-shaped model correctly uses the approved existing structured issue printer on stdout, while the harness required stdout to be empty. The approved answer says no review text, not no diagnostics. The successor asserts absence of the review header and presence of the existing error diagnostic; the exit3 answer is unchanged. The original red corpus remains retained. Two import-style lint findings in the new test were corrected without semantic changes.
- The owner reacted to the early docs checkpoint: requested a higher-level real example demonstrating the functionality's value. This is an actual reaction, not byte/merge approval; the separate docs branch must be revised and the reply recorded in the MC4 spec. MC2 implementation remains independent.

### a1: measured replay comparison correction (2026-11-10)

The composed replay succeeds, but C03's draft comparison guessed model_sha256/model_identity/model_version fields and omitted the actual model_digest plus the record's derivative SHA. The composition record commits to the includer's authored raw bytes, so its SHA must differ from the plain model's record. The failing harness output is retained; no production fix is indicated. Preserve the original thirteen answers in010-approved-answers.json. The exact successor narrows the allowlist to top-level model/population coordinates and model_digest plus composition.record_sha256. Compare every remaining field, including full lineage, unchanged. Verify coordinates exactly, plain digest against the frozen replay answer, included model digest independently from the pre-MC2 frozen composed document, and each record SHA over independently canonicalized frozen record bytes (sorted keys, compact separators, literal Unicode, no nonfinite values, one terminal newline). No broad composition exclusion is admitted. Delegated approval (auto=true) in record012 binds the corrected answer/spec; review budget and size stops are unchanged.
