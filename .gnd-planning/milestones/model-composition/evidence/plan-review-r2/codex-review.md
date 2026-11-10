# Plan review over r2 (Codex), retained verbatim

- Instrument: one reviewer in a different tool, the same seat as round one, selected by the owner ("Codex review r2", 2026-11-09). One reviewer is one reviewer.
- Command: `codex exec --ephemeral --model gpt-6.1-sol --config model_reasoning_effort="xhigh" --sandbox read-only --color never --skip-git-repo-check -`, prompt on stdin ([prompt.md](prompt.md)), 185,817 tokens, exit 0.
- Reviewed bytes (uncommitted when reviewed; retained here): `notes/model-composition-plan.md` r2, sha256 2dc91f4e4aee8279ae5feb9695face7b2820e243ccb56e3db1749b4f73bc438a ([copy](model-composition-plan.r2.md)), and `notes/phase-MC1-spec.md` r2, sha256 e8f6cf85ab0d4ae988727f9143ad52fb6dc38e3f328f4acce32b7cfb6ef4a07f ([copy](phase-MC1-spec.r2.md)), over main `459ca8d2`.
- The output below is unedited; the trailing "codex exit=0" line is the driver's.

## Reviewer output (verbatim)

DISPOSITION: revise

ID: P11
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:272
QUOTE: “Own elements keep their path unchanged, because they keep their authored positions”
PROBLEM: The structural-address repair does not handle project-owned constraints appended inside included fact types. Their authored address is `$.fact_type_constraints[0].constraints[0]`, but validation addresses the composed host. A read-only probe appending a mandatory constraint with an unknown role produced `semantic:string-ref` at `$.fact_types[id=component_imports_component].constraints[0]`. This follows the existing walk at `src/gnd/model/_validation.py:318`. Looking up the leading fact-type address attributes that project rule to the include; leaving an own constraint’s composed path unchanged also loses its authored location. T44–T45 exercise included elements, not this mixed ownership.
FIX: Resolve the deepest applicable provenance entry and map project-owned attached constraints back to their `fact_type_constraints` addresses. Add error and warning cases on an included host containing both included and project-owned constraints.

ID: P12
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:53
QUOTE: “`_includes.compose(...)`”
PROBLEM: The totality obligation names the composer, but T19 directly calls only `parse_declarations`, `parse_included` and `declares_includes`; T20 compares declaration acceptance. The composer remains untested over hostile document shapes. This matters because step 10 walks IDs before step 11 structurally validates owned elements. The existing ID walk uses set membership on supplied IDs (`src/gnd/model/_validation.py:357`); calling it with `{"object_types":[{"id":[]}],"fact_types":[]}` raised `TypeError`. The current loader normally protects that walk with layer 1 (`src/gnd/model/__init__.py:323`).
FIX: Add direct hostile-input tests for `compose`, including malformed owned sections, unhashable IDs and malformed attachment entries, with a valid retained descriptor. Specify stable refusals before unsafe iteration or lookup.

ID: P15
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:305
QUOTE: “either a refusal (its rule ids) or `model_dump`, `model_dump_json`”
PROBLEM: The repaired census still assumes every successful load has every named identity. A read-only census of the specified 400 tracked files produced 334 successful loads, 66 load refusals and one canonical-identity refusal among the successful loads: `tests/fixtures/rof3-model-identity/models/surrogate.orm.json` raises `ModelIdentityError`. Its surrogate is authored at line 110. Canonical identity explicitly permits this refusal (`src/gnd/values.py:261`), and `validate --identity` reports it as exit 3 (`src/gnd/output.py:65`). The proposed success/refusal partition cannot record this member as specified.
FIX: Record success or refusal independently for each serialization and identity observable, including refusal rule and path. Preserve the surrogate fixture’s successful load and refused canonical identity.

ID: P16
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:289
QUOTE: “`include:unresolved` (step 2 rule), confirmed per row by a case”
PROBLEM: The activation repair contradicts plan MC1-C10, which requires every unsupported admission point to refuse with `include:unsupported-route` through the shared guard (`model-composition-plan.md:358`). This row instead specifies `include:unresolved`, and the next permits generic “invalid model”. That generic collapse is real (`src/gnd/api.py:980`). Furthermore, one row groups witness, judgments, several exp paths, multiple exporters, discover and evolve; T41’s “one case per row” does not test each promised admission point.
FIX: Specify one route-to-refusal matrix consistent with MC1-C10. Keep the public bytes loader’s `include:unresolved` contract distinct from service guards, and enumerate and test each admission point separately. Any retained generic-error exception needs an explicit contract amendment.

ID: P19
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:342
QUOTE: “allowed, same semantics as version 4”
PROBLEM: Widening the schema and reference guard does not preserve version-4 temporal semantics. `_rule_temporal_language` explicitly admits only versions 3 and 4 (`src/gnd/model/_validation.py:4586`), while step 11 promises unchanged semantic validation. A probe of `tests/fixtures/rc1-rule-ids/models/temporal.orm.yaml` found no semantic errors originally; changing only its version to 5 produced `semantic:temporal-site` at `$.object_types[1]`. Thus D2/T40 fail, and a permitted temporal vocabulary can validate alone yet fail after composition.
FIX: Include the temporal version guard in MC1’s changes and add temporal version-4/version-5 controls, including an included temporal vocabulary. Otherwise obtain an owner ruling explicitly narrowing version-5 capabilities.

ID: P20
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:264
QUOTE: “round-trip through `load_model_bytes`”
PROBLEM: T42 cannot perform this round-trip. The composed dump retains `includes`, so §6.2 expressly requires the bytes loader to refuse it with `include:unresolved`. Using the composed-bytes route instead would resolve and append the vocabulary again. Independently, loaded dumps are not authored-model documents: probing an existing minimal model’s dump against layer 1 produced `jsonschema:additionalProperties` for `warnings` and `jsonschema:type` for `model_id: null` (`src/gnd/documents.py:33`, `:74`; `src/gnd/model/__init__.py:323`). Also, “exactly composed content plus declarations” overlooks the existing operation exclusions (`src/gnd/values.py:176`, `:253`).
FIX: Compare identities against independently assembled expected loaded content using the existing identity envelopes and exclusions. Do not reload a composed dump through an authored-document loader. Add discriminating content mutations alongside declaration/path mutations.

ID: P21
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:153
QUOTE: “held equal to `parse_declarations` by T20”
PROBLEM: The specified schema does not enforce unique include IDs, while step 3 does and T5 includes duplicate IDs. Applying the proposed schema changes in memory admitted two declarations with the same ID and different paths and hashes without any schema error. Therefore T20’s required identical acceptance over every T5–T7 case is false. The existing structural validator directly applies Draft 2020-12 validation (`src/gnd/model/_validation.py:290`); it supplies no property-projection uniqueness check.
FIX: Separate envelope-schema parity from declaration-level semantic checks. Retain duplicate-ID refusal in the declaration parser and test it there, while explicitly excluding that semantic condition from schema-equivalence claims.

ID: P22
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:107
QUOTE: “reuse (import)”
PROBLEM: Importing `_relative` from `gnd.model` into `_includes`, while the loader imports `_includes`, creates a prohibited runtime cycle. `_relative` currently lives in the package initializer (`src/gnd/model/__init__.py:457`). The graph tool counts lazy imports as runtime edges (`tools/gnd_arch.py:46`), and the required graph assertion rejects runtime SCCs (`tests/test_rf8_structure.py:24`). Feeding these two proposed imports into the actual graph visitor and SCC routine returned `[['gnd.model', 'gnd.model._includes']]`.
FIX: Specify an acyclic dependency home for reused parsing/path primitives, or an explicit dependency-injection surface. Preserve moved public lookup identities and required shims, update the layer map, and name the runtime-cycle check in the gate.

ID: P23
SEVERITY: blocking
LOCATION: .gnd-planning/milestones/model-composition/notes/model-composition-plan.md:360
QUOTE: “through one shared predicate in `_includes.py`”
PROBLEM: Applying this requirement to `pyrel_runtime._admit_model` violates the existing standalone runtime boundary. That module explicitly imports no GND module and is copied verbatim into exported programs (`src/gnd/export/pyrel_runtime.py:3`; `src/gnd/export/emit.py:31`). Existing export tests reject GND imports at any nesting depth (`tests/test_pyrel_export.py:35`). Even a local added runtime guard changes include-free exported program bytes because the entire runtime is embedded, conflicting with plan rule 0.3’s unrestricted output-byte promise (`model-composition-plan.md:84`).
FIX: Define a standalone boundary exception, with a local refusal using the runtime’s own error type and dedicated isolation tests. Explicitly resolve the generated-program byte compatibility requirement before choosing how changed runtime code is emitted.

ID: P24
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:189
QUOTE: “`def parse_included(raw: bytes, *, include_id: str)`”
PROBLEM: The parser receives no included filename, although filename suffix determines existing parsing semantics. `.json` sources require strict JSON (`src/gnd/model/__init__.py:298`). A probe using identical YAML bytes loaded successfully with source `vocab/base.orm.yaml` but raised `ModelLoadError: model JSON input refused` with source `vocab/base.orm.json`. Step 7’s filename-independent YAML parse can therefore admit an included `.orm.json` that fails standalone `gnd validate`, contradicting plan §2.2 (`model-composition-plan.md:200`).
FIX: Pass the declared included path into parsing and reuse the existing suffix-sensitive parser, mapping its failures to `include:parse` after hash verification. Test YAML-only content under `.json` and valid strict JSON.

ID: P25
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:323
QUOTE: “`artifacts.ArtifactSizeError(ArtifactError)` raised at the existing two cap sites”
PROBLEM: The typed-size repair preserves catch compatibility but changes existing observable refusals. The shared cap sites currently raise `ArtifactError` (`src/gnd/artifacts.py:587`, `:594`), and public diff incorporates the exception’s concrete class name (`src/gnd/api.py:786`). A read-only probe substituting the proposed subclass at `_read_fd` changed an include-free diff refusal from `diff:invalid-model:ArtifactError` to `diff:invalid-model:ArtifactSizeError`. This contradicts the frozen-output rule despite unchanged exception inheritance.
FIX: Preserve predecessor-facing error spellings at existing boundaries while allowing the include resolver to distinguish the internal typed size refusal. Add an oversized include-free diff regression control.

ID: P26
SEVERITY: hardening
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:205
QUOTE: “`declares_includes(document)` is false → the existing path, untouched”
PROBLEM: T7 requires `include:declaration` when `fact_type_constraints` appears without `includes`, but the dispatch contract provides no explicit route for that case into step 3. With ordinary include-key detection it takes the existing structural path instead. An in-memory schema probe with a valid mandatory attachment and no `includes` produced only `jsonschema:required`, as expected from the current structural error mapping (`src/gnd/model/_validation.py:301`).
FIX: Define the predicate precisely and perform orphan-attachment declaration checks before the include-free bypass. Pin the path and bytes-route precedence for this case with direct tests.

ID: P27
SEVERITY: completeness
LOCATION: .gnd-planning/milestones/model-composition/notes/phase-MC1-spec.md:411
QUOTE: “`uv run pytest -q tests/test_mc1_model_includes.py tests/test_mc1_census.py`”
PROBLEM: The mandatory exhaustive compatibility evidence has no executable gate consistent with repository policy. Exhaustive tracked-tree assertions belong to `census`, and fixed-commit retained comparisons belong to `evidence` (`.codex/skills/process-phase/references/project.md:110`). Both lanes are excluded by default (`pyproject.toml:73`), so listing the census module in this command will not execute correctly marked tests. The later unspecified “whole suite” does not establish that those excluded lanes run either.
FIX: Assign the compatibility tests their required markers and specify a separate broad-lane verification command and retained output on beast-3. Keep the ordinary focused gate under its existing default filter.

SUMMARY: R2 makes substantial repairs, but unresolved validation, identity, provenance, compatibility and guard-design contradictions require another revision.
codex exit=0
