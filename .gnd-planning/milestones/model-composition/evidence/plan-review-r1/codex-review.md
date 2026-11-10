# Plan review over r1 (Codex), retained verbatim

- Instrument: one reviewer in a different tool, selected by the owner (MD0, "Codex review", 2026-11-09). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6.1-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin ([prompt.md](prompt.md)), 182,007 tokens, exit 0.
- Reviewed bytes (uncommitted when reviewed; retained here): `notes/model-composition-plan.md` r1, sha256 bd661eeede495e2c3c82e9fbd81cfa6d79f7d2a8d0f77c4374f20736f6d1597a ([copy](model-composition-plan.r1.md)), and `notes/phase-MC1-spec.md` r1, sha256 b6ebc5db0b9ecaba0992380ff43f05d865d05415a2dbcbebf9016200a4c06dff ([copy](phase-MC1-spec.r1.md)), over main `459ca8d2`.
- The output below is unedited; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: P1
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:175
QUOTE: “It may not redeclare, override or remove an included element”
PROBLEM: The proposed representation cannot attach project-owned inline constraints to included fact types. Ring, mandatory and internal uniqueness constraints are inline-only (`src/gnd/schema/orm-meta.schema.json:1102`, `:1136`); the merge merely concatenates sections. The existing component example places its acyclic rule inside the fact type (`src/gnd/examples/rule_check/model.orm.yaml:14`). Moving that rule to top-level constraints in a read-only probe produced `jsonschema:oneOf` and `jsonschema:unevaluatedProperties`. Redeclaring its host would instead trigger the proposed collision refusal.
FIX: Add an owner-decided representation for project-owned constraints hosted on included fact types, with loader, origin, evolve and discover semantics. Require acyclic and mandatory examples on shipped vocabulary in MC1’s acceptance tests.

ID: P2
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:151
QUOTE: “parse the including file; layer 1 over it as written”
PROBLEM: Layer 1 would pre-empt the promised declaration refusals. Applying §6.1’s schema changes in memory produced `jsonschema:type` for non-list/non-mapping declarations, `jsonschema:additionalProperties` for extra fields, and `jsonschema:maxItems` for nine includes. These inputs never reach step 2 or produce T5’s `include:declaration` (`src/gnd/model/__init__.py:323`, `src/gnd/model/_validation.py:290`). Also, the plan’s §2.1 example omits the still-required `object_types` and `fact_types`; the same probe rejected both omissions (`src/gnd/schema/orm-meta.schema.json:7`).
FIX: Define envelope/declaration validation before full structural validation, or explicitly translate relevant structural issues. Decide whether include-bearing files may omit owned type sections; update the schema, example and tests consistently.

ID: P3
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:161
QUOTE: “checked on the parsed document before step 6's validation”
PROBLEM: Numbered step 7 follows step 6 but explicitly precedes part of it. The plan additionally orders included-model validation before forbidden-section checks (`model-composition-plan.md:263`), while T17 requires the reverse. Parsing and validation are separate boundaries in the current loader (`src/gnd/model/__init__.py:320`). T17’s source-order assertion also cannot establish behavior: hash/parse and collision/semantic failures have different proposed reasons, so behavioral controls can distinguish them. String-order tests alone are explicitly insufficient under `.codex/skills/process-phase/references/standing-rules.md:56`.
FIX: Split parsing from included validation and publish one consistent order. Specify whether precedence is global across includes or applied per entry. Add compound-fault cases asserting the winning reason and that forbidden downstream work was not called.

ID: P4
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:115
QUOTE: “Version 5 also admits every version-4 feature”
PROBLEM: Schema widening does not enable reference populations. Step 11 calls `validate_declarations`, which explicitly refuses any reference-bearing model whose version is not 4 (`src/gnd/model/__init__.py:499`). A probe bypassing structural/semantic checks still raised `ReferenceInputError: reference_populations requires model version 4` for version 5. Consequently MC1-C7/T23 cannot pass with the proposed changes. The bytes-composed route also needs an explicit reference-binding contract; existing `_load_model_no_follow` binds references separately after loading (`:347`).
FIX: Include the runtime version guard and binding paths in MC1’s design. Test version-5 references through both path and composed-bytes entry points, including derived ownership and operation effects on reference-owned fact types.

ID: P5
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:180
QUOTE: “JSON output carries the reason as `rule_id`.”
PROBLEM: Inheriting `ModelLoadError` does not provide that mapping. Validate and check catch generic exceptions into `error`, whereas only `ModelValidationError` supplies issues (`src/gnd/api.py:313`, `src/gnd/checking_service.py:306`). `_error_record` emits only type and message (`src/gnd/payloads.py:121`). Injecting the proposed exception into the actual loader lookup produced exit 3 with `issues: []` and `error: {type: IncludeError, message: include:path}` for both commands.
FIX: Specify how include refusals become `ValidationIssue` records or receive an explicit service mapping. Assert the exact text and JSON representation for every reason through both CLI commands.

ID: P6
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:297
QUOTE: “load refuses `include:hash-mismatch`; `repin-include` preview names the broken rule”
PROBLEM: This scenario destroys the input needed for the promised before/after comparison. After vocabulary v1 is overwritten, the includer still pins v1, but no retained v1 bytes are specified. Evolve validates the current model before examining the candidate (`src/gnd/evolve/service.py:1456`); apply and finalization reload it again (`:1984`, `:2310`). The proposed strict loader therefore refuses before re-pin can compute the old composition or its blast radius.
FIX: Decide where authenticated old vocabulary bytes survive: immutable versioned paths, supplied digest-verified snapshots, or retained evolution evidence. Define their use during preview, apply and recovery, and make MC3-C4 exercise that lifecycle.

ID: P7
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:223
QUOTE: “A re-pin that leaves the composition invalid is staged for review”
PROBLEM: Existing evolution evidence cannot represent this state. `_validated_candidate` requires a successful model load and constructs `valid=True` evidence (`src/gnd/evolve/service.py:1360`); `ValidationEvidence.valid` is literally restricted to `True` (`src/gnd/evolve/models.py:675`). Preview validates the candidate before building the blast radius (`service.py:1473`, `:1520`). Furthermore, the current radius compares supplied documents (`:747`), and `breaking` recognizes only rename/delete operation kinds (`:1527`), so changing an include declaration does not automatically expose removed vocabulary or require breaking-change acceptance.
FIX: Add an owner decision for invalid-candidate analysis evidence, separate from publishable validation evidence. Specify composed-document impact analysis, re-pin breaking classification, refusal at publication, and compatible evidence readers.

ID: P8
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:190
QUOTE: “The raw-byte sha256 of the including file is already a complete content identity”
PROBLEM: This is defensible as a commitment to successfully verified dependencies, but it does not establish their current validity or availability. The assertion that mismatch is caught before currency runs is false today: conformance catches an initial `ModelLoadError`, then performs raw-file currency before retrying structural loading (`src/gnd/conformance/service.py:76`, `:196`, `:206`). A probe of `check_currency` returned `()` without invoking the loader (`src/gnd/conformance/currency.py:94`). Likewise, evolve’s final CAS guards only the includer after its last dependency load (`src/gnd/evolve/service.py:2129`, `:2141`).
FIX: State the identity’s conditional scope. Require dependency verification before positive freshness claims, and define snapshot/concurrency guarantees for publication and recovery. Add dependency-change controls between preview, apply, publication and finalization.

ID: P9
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:74
QUOTE: “print the same lines as on its committed flattened twin”
PROBLEM: This conflicts with the identity contract. Check emits a model digest (`src/gnd/checking_service.py:332`), and the unchanged digest functions include model version and the proposed nonempty `includes` field (`src/gnd/values.py:188`, `:253`). An in-memory prototype of the specified field produced different successful check-report digests for version 4, version 5 without includes, and version 5 with includes. Thus both unrestricted twin equality and T28’s “same outputs” cannot hold. Validate also prints the input pathname (`src/gnd/commands/checking.py:155`).
FIX: Specify an exact comparison allowlist for coordinates and identities, independently verify those fields, and compare all remaining behavior strictly. Make T28 assert equivalent checking semantics while explicitly expecting version-bound identity differences.

ID: P10
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:121
QUOTE: “`model_dump` pops `includes` when empty”
PROBLEM: This preserves the tested dump and digest paths, but not every existing serialized output. Pydantic’s `model_dump_json` does not call this override. A read-only subclass implementing exactly the proposed field and override preserved `model_dump`, `_model_digest` and canonical identity, but changed `model_dump_json` by adding `"includes":[]`. The current class defines no JSON serializer override (`src/gnd/documents.py:63`), and existing consumers/tests use that serialization surface (`tests/test_model_v2.py:113`, `tests/test_compiled_snapshot_obligations.py:145`).
FIX: Preserve empty-field omission across supported serialization entry points, including JSON serialization, and add baseline controls for them. Otherwise obtain an explicit narrowing of the “every output byte” compatibility predicate.

ID: P11
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:120
QUOTE: “element id → include id; own elements absent”
PROBLEM: An id-only table cannot identify every included element or recover its original path. Constraint ids are optional (`src/gnd/schema/orm-meta.schema.json:1033`); anonymous top-level constraints receive positional paths (`src/gnd/model/_validation.py:319`). Removing ids from the example’s top-level constraints remained valid in a probe, while changing the effective source produced issues at `$.constraints[0]` and `[1]`. Neither constraint has a key in `_origins`. Existing semantic paths also use selectors such as `fact_types[id=...]`, rather than uniformly numeric offsets (`:318`).
FIX: Retain section/index or structural-address provenance, original paths and composition offsets, with ids as an additional lookup. Cover anonymous top-level constraints, inline constraints, warnings and multiple includes. Store included model metadata separately from element ownership.

ID: P12
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:45
QUOTE: “Tests T5-T16.”
PROBLEM: These loader/CLI cases do not discharge the promised function-level totality over arbitrary JSON. Many malformed declarations stop at layer 1, so they cannot expose a crash in `parse_declarations`; there are no stated direct hostile-input tests for either new function. Non-UTF-8 input is promised but absent from T10. The parser can raise directly at UTF-8 decoding (`src/gnd/model/__init__.py:294`). The matrix also lacks explicit cases for several admitted branches: project operations, cross-boundary derivations/subtypes, rejected proposals, deontic-note ordering, and model-id precedence. Those sections have distinct behavior (`documents.py:33`, `:44`, `:47`, `:73`; `_validation.py:595`, `:2032`).
FIX: Add direct hostile-shape tests for each new consumer, plus a branch-to-test matrix covering every admitted section and cross-boundary reference. Include malformed hashes, missing fields, empty declarations and non-UTF-8 bytes.

ID: P13
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:154
QUOTE: “read each under the descriptor, no follow → `include:unreadable`”
PROBLEM: The reused bounded reader does not expose a distinct size exception. Non-regular files, pre-existing oversize files and growth beyond the cap all raise `ArtifactError` (`src/gnd/artifacts.py:583`, `:587`, `:594`); symlink/open refusals use the same class (`:642`, `:667`). Probes confirmed identical exception classes for non-regular and oversized inputs. The spec promises distinct unreadable/size reasons without defining a reliable discriminator.
FIX: Specify a stable typed size refusal in the shared reader, preserving predecessor behavior, and map it separately. Test both pre-read oversize and growth during reading; do not distinguish them using untrusted message text or a separate unchecked stat.

ID: P14
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:47
QUOTE: “the existing entry maximum”
PROBLEM: No such model-entry maximum is identified or enforced. Object types, fact types and constraints have no `maxItems` (`src/gnd/schema/orm-meta.schema.json:29`). The nearby `MAX_ENTRIES = 100_000` bounds reference-population facts and instances, not model declarations (`src/gnd/model/__init__.py:396`, `:560`, `:574`). A schema inspection confirmed that only references and the proposed includes array have top-level item caps. T18 therefore has no defined “entry maximum,” and one fixed-size timing cannot establish the claimed scaling behavior.
FIX: Define the composition workload and aggregate bounds explicitly, obtaining an owner ruling for any new input limit. Specify increasing workloads, a predeclared timing/ratio criterion and a quadratic mutant control over the merge/collision layer.

ID: P15
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:258
QUOTE: “every committed `*.orm.yaml`, dump and four identities”
PROBLEM: This cannot be the stated complete compatibility census. `git ls-files` found 300 matching YAML files and 100 `.orm.json` files, including shipped models such as `src/gnd/examples/expense/model.orm.json`. The YAML population also contains intentionally invalid models: a bytes-loader census produced 64 YAML validation refusals, so not every member has a dump or identities to compare. For example, `tests/fixtures/models/invalid/duplicate_role_names_cross_type.orm.yaml` raises `semantic:role-names-distinct`. The plan’s §1.2 counts do not state their selection method.
FIX: Define a reproducible tracked-file census covering YAML and JSON. Record successful-load dumps/identities and expected refusal outcomes separately, name the four identities precisely, and publish the selection/counts alongside the baseline.

ID: P16
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:280
QUOTE: “Every §1.3 consumer other than `load_model`, `gnd validate` and `gnd check`”
PROBLEM: Deferring all other boundaries allows MC1 to expose silent half-model readers. The independent PyRel admission ignores `includes` (`src/gnd/export/pyrel_runtime.py:990`); a probe admitted a version-5 includer as a model with zero object/fact types. `render_pyrel` then embeds that raw text (`src/gnd/export/emit.py:22`). Although PyRel is inventoried, no MC1 refusal protects it. The inventory also omits the public population-compose loading path at `src/gnd/api.py:980`, which currently collapses loader refusals into generic “invalid model”; that is separate from checking-service composition verification.
FIX: Add the missing route and a complete activation inventory. Require minimum refusal guards when MC1 enables includes, or explicitly prevent MC1 from landing independently until the consumer sweep is complete.

ID: P17
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:331
QUOTE: “a case that the included file's bytes are unchanged after every evolve”
PROBLEM: This control cannot detect flattening into the including file: the vocabulary can remain untouched while the project file loses its split. Evolve publishes the supplied candidate text directly (`src/gnd/evolve/service.py:2141`); discover likewise renders whatever document it receives (`src/gnd/discover/output.py:99`, `:140`). The current evolve loader deliberately returns both the loaded model and the separately parsed authored document (`service.py:245`, `:251`), a distinction composition must preserve.
FIX: Require assertions on the written includer: preserved declarations, only owned edits, no copied vocabulary definitions, and successful recomposition. Apply these controls to evolve, discover, ILP and interrupted-operation recovery, including a deliberate flattened-candidate negative control.

ID: P18
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:165
QUOTE: “`version`, `model_id`, `source` and `includes` from the including file”
PROBLEM: Selecting `source` is a behavioral policy decision missing from the owner-decision table. Source mode activates unattended validation and its document/span requirements (`src/gnd/model/_unattended.py:169`, `:192`, `:204`). Replacing source metadata in a probe changed errors on otherwise unchanged constraints. Discarding an included file’s `source.documents` can therefore invalidate retained provenance, while replacing its unattended mode can disable checks. Standalone validity does not settle the composed policy.
FIX: Add an explicit owner decision for effective source mode and document provenance across includes. Define preservation or refusal rules and test both mode directions, document-bound spans and anonymous included constraints.

SUMMARY: The drafts need revisions to rule attachment, validation/refusal boundaries, evolution evidence, compatibility tests and consumer activation before approval.
codex exit=0
