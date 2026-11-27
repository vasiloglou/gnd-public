# GC1 · Complete compact model projection

**Historical first-phase draft.** The revised two-phase scope in the canonical plan supersedes this draft. The owner requested implementation. The packaged guide's Growth view v1 section defines the implemented JSON field names, ordered role pairs, subtype pairs, constraint signatures and encoding. The digest below identifies the earlier plan only.

## 2. Provenance

Draft derived from the canonical [milestone plan](compact-growth-context-plan.md), sections 0–4 and 9, and issue 295 request 1. Source inspection at 6560f440 on 2026-11-27. No review instrument has run over these bytes. This phase delivers the internal projection consumed by GC2.

## 3. Obligations and discharge

| Source | GC1 obligation | Discharge |
|---|---|---|
| Issue 295 request 1; plan §2 | Stable, compact records, including inherited vocabulary | Projection contract and cases A–D |
| Unattended growth guide; plan §0 | Existing elements retain model IDs, roles and subtype relationships | Cases A, C, E |
| Model/include loader; plan §6 | Resolve includes through existing loader and reject unverifiable in-memory composition | Cases C, F |
| Plan §§3, 9; repository layering | One projection home, no private corpus dependency, bounded algorithm | Cases G–H and layer check |

## 4. Standing rules applied

Totality: defined empty inventory and explicit refusal on unresolved composition. Input caps: walk each collection once before canonical sorting, never expand transitive subtype paths. Validation order: use caller's normal validated model path, check composition identity, project rows, then serialize atomically. Coverage of kinds: one central projection for all object, fact and constraint hosts. Normative prose: one version-1 format contract linked by the host guide. Measure contested representation: golden fixtures with multibyte text and ordered role sequences. Parse structured input with the model loader. Keep new module placement and query exceptions within repository layer and ModelIndex rules.

## 5. Goal

The focused pytest command in §8 exits 0 for a complete, replayable, provenance-free inventory of a plain model and an include root. GC2 owns public command behavior.

## 6. Design

| Capability inspected | Existing home | Decision |
|---|---|---|
| Model rendering and CLI dispatch; index searches for verbalize and growth | model.verbalization, cli.api, cli.checking_command | Share loader and include checks. Create an allowlisted projection because the existing review surface deliberately includes authored samples. |
| Include expansion and element queries; search for include and direct source inspection | gnd.model.load_model, ModelIndex.for_model, existing include metadata validation in model_verbalization | Reuse composed snapshot; extract the existing include integrity check if necessary to avoid duplicating it. |
| Stable constraint addresses and role players | gnd.address, gnd.constraint_families, gnd.model_index | Reuse current address/family semantics; keep model-hosted and fact-local constraints distinguishable. |

Proposed internal signature in `src/gnd/growth_view.py`: `render_growth_view(model: Model) -> str`. The caller supplies the validated model. Preserve loader failures on unresolved or mismatched includes. GC2 will own public path resolution. Keep the validated snapshot immutable. Proposed format home: `docs/growth-view.md`.

A minimal empty version-1 view serializes to the following bytes followed by one LF.

```json
{"constraints":[],"fact_types":[],"format":"gnd-growth-view-v1","object_types":[],"subtypes":[]}
```

Object records carry `id`, `kind` and declared `name`, `primitive` and reference mode/value-type identifiers when present. Fact records carry `id`, `reading`, a derived/asserted discriminator and ordered role records with `role_name` and `object_type`. Subtype records carry `subtype` and `supertype`, one per direct declared link. Constraint records carry `host`, `type`, authored ID when present, and the addressable role operand groups. Encode host as a tagged model/fact locator. Preserve operand labels (e.g. subset and superset), role-sequence order, fact-qualified references, and each distinct declaration including anonymous ones. Empty-role families have an empty operand list. Before implementation, enumerate the supported families and their role-bearing fields in the fixture corpus; a new uncovered family fails the coverage test. This is a signature inventory, so it cannot by itself establish constraint equivalence.

Sort JSON keys; UTF-8, unescaped Unicode, compact separators, one trailing newline. Order object and fact records by ID, subtype links by endpoint pair and constraint projections by canonical record bytes. Preserve ordered semantic fields. Serialize projected fields only. Never traverse a generic payload to remove suspicious field names. Do not print source labels, spans, samples, rationale, arbitrary extension payloads, include paths or absolute host paths. GC1 uses a materialized inventory and an ordered sort, with expected O(N log N + emitted bytes) work, where N counts emitted records and role operands.

## 7. Proposed decisions

| ID | Owner ruling requested | Consequence |
|---|---|---|
| GC1-D1 | Freeze the minimal versioned JSON projection and canonical bytes, or use human-oriented lines | JSON gives hosts a testable replay and lookup format. Human-oriented lines would require a separate escaping/parse contract. |
| GC1-D2 | Carry role-bearing constraint signatures, with richer semantics resolved from the model by the host | Full constraint bodies can substantially enlarge context. Document the information available for equivalence decisions. |
| GC1-D3 | Require loader-verified composed input when includes are declared | Unverified in-memory include roots refuse through the established include error path. |

## 8. Tests and evidence

Proposed new tests in `tests/test_growth_view.py`. Focused command: `uv run pytest -q tests/test_growth_view.py tests/test_model_verbalization.py tests/test_include_root_close.py --tb=short`, expected exit 0.

| Case | Falsifiable result |
|---|---|
| A · fixture containing an entity, value, subtype and multi-role fact | Exactly the expected IDs, primitive, reference, direct endpoints and role order appear. |
| B · repeated runs, Unicode and reordered independent declarations | Byte-identical UTF-8 output in fresh processes; swapping ordered operands changes the appropriate output. |
| C · plain vs loader-composed root | Equivalent effective inventories match, included IDs appear once and include paths never appear. |
| D · evidence mutation | Alter nested samples, spans and rationales; output digest stays identical and unique marker strings are absent. Change a fact reading; digest changes. |
| E · constraint inventory | Every registered family has a case; two model-level operand sequences retain their sides; two identical anonymous signatures retain multiplicity. |
| F · invalid/missing/stale include binding | Existing loader/verification refusal, with no partial view. Ordinary verbalization regression cases keep their expected behavior. |
| G · empty model and repeated calls on a mutated copy | Empty arrays match the literal contract; second call observes current schema; original model content unchanged. |
| H · scale | Generated fixtures with 1×, 2× and 4× rows report counts and output sizes, with no duplicate traversal of included documents. Layer allowance count remains zero. |

## 9. Scope

GC2–5 own public API, CLI, subset retrieval, host decisions, documentation of a round and empirical performance. This phase has no provider, scoring or mutation path.

## 10. Size

Proposed 140–240 source lines, 180–300 test lines plus fixtures and format documentation. Record actual counts and justify divergence.

## 11. Approval instrument

Owner gates on this spec and proposed decisions GC1-D1–D3 after the milestone plan gate. The maintained panel for plan review needs explicit selection. No implementation, review or publication approval is recorded.
Canonical plan SHA-256 at draft: bdb7477cbf7061fb5a8289f049fd18a747e0cf442546db5d94003dc3288b2334.
