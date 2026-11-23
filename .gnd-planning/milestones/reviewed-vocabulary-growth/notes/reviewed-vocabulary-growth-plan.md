# Reviewed-vocabulary growth · plan r1

**Status: r1 draft, 2026-11-22. Not reviewed and not approved.** No plan
review has run: `start-milestone` does not select a review instrument, and the
owner has not selected one for this plan (D8). No `auto` delegation exists for
this milestone. Approval is recorded only in a plan-gate record, which does
not exist yet.

This plan covers three open issues that no milestone owns:
[#221](https://github.com/vasiloglou/gnd-public/issues/221),
[#222](https://github.com/vasiloglou/gnd-public/issues/222) and
[#218](https://github.com/vasiloglou/gnd-public/issues/218).

The other four open issues are owned elsewhere and are out of scope here:

| Issue | Owner | State on 2026-11-22 |
|---|---|---|
| [#215](https://github.com/vasiloglou/gnd-public/issues/215), [#216](https://github.com/vasiloglou/gnd-public/issues/216) | [literature-host-interfaces](../../literature-host-interfaces/README.md) | outline r1; its full plan is being written in another session on branch `claude/next-roadmap-milestone-5049b9` |
| [#217](https://github.com/vasiloglou/gnd-public/issues/217) | [include-root-routes](../../include-root-routes/README.md) | delivered on `main` (PR 220), reply posted, not released |
| [#214](https://github.com/vasiloglou/gnd-public/issues/214) | include-root-routes (item 1), [pyrel-rules-coverage](../../pyrel-rules-coverage/README.md) (items 2–4) | delivered on `main` (PR 220, PR 223), not released; the issue carries a reply for item 1 only |

**Provenance.** New in this session; there is no earlier outline. Every code
citation was read at `4ad0d216` (`main`, 2026-11-22). Every measurement
marked "observed" was run on that commit on 2026-11-22, on one laptop, once.
#218 was already planned as a
[maintenance pass](../../../maintenance/2026-11-21-evolve-constraint-sources/README.md);
D1 proposes to carry it here.

## Goal and completion predicates

A host grows several unattended models from one shared, owner-reviewed
vocabulary, at the size such a vocabulary has, and what the growth document
tells the host to write is what `gnd evolve` admits.

- **VG1.** `gnd check` cost grows about linearly with the number of object
  types. The interop fixture with 1,000 extra object types checks in under
  10 s in process (today: 265.74 s, #221), for each of four shapes of extra
  types, and doubling the count costs at most 3 times as much. Every report is
  unchanged. A subtype chain hundreds of types deep stays slow for a separate
  reason and is out of scope (D12).
- **VG2.** A constraint proposal written exactly as `unattended-growth.md`
  says (`sample` for row evidence, `common-sense` for library evidence, always
  `proposed` and `deontic`) is admitted by `gnd evolve`, and rule D-12 and the
  growth document say the same thing (D2).
- **VG3.** A version-5 root with `source.mode: unattended` that includes a
  reviewed, non-unattended model validates, exit 0. The included elements keep
  their own `source`, `status` and `modality`; rules U2–U6 and U8 apply to the
  elements the root owns (D3). Every included element is reported with its
  include.
- **VG4.** That root grows through `gnd evolve preview`, `apply` and
  `finalize`: a round adds root-owned elements and constraints attached to
  included fact types, included elements stay read-only, and the first round
  can declare the first source document (D4).
- **VG5.** One packaged example runs the whole path: a reviewed seed, an
  unattended root that includes it, two growth rounds, then `gnd validate`,
  `gnd check` and `gnd judgments check` on the result. The growth document and
  the representation format describe it, and a reply is drafted for each of
  the three issues.

The milestone is closed when each phase has its record and the close record
cites green focused gates for VG1–VG5, the structure and inventory guards,
`uv run ruff check src tests tools`, the component-index check, the three
drafted replies, and a close review on the instrument D8 selects.

## 0. Binding design rules

- **R0.1 Reports do not move.** VG1 changes cost, never output: every check,
  judgment and verify report is byte-identical for every model that loads
  today.
- **R0.2 One denotation.** Which value type denotes an entity type has one
  definition, `resolve_reference_value_type` (`src/gnd/universe.py:59`). A
  table built from it is a cache of that function, checked equal to it over
  every loadable fixture. The witness oracle's separate walk
  (`src/gnd/synth/oracle/constructive.py:131`) stays separate by design (its
  docstring, "written independently", C1); it never imports the checker's
  table.
- **R0.3 A model without the mode is untouched.** No model without
  `source.mode: unattended` gains or loses a validation issue (MG-R1,
  `src/gnd/model/_unattended.py:11`). VG2 is the one named exception: it
  admits two more sources in `gnd evolve` for every model.
- **R0.4 The root's own claims keep every U rule.** VG3 exempts only elements
  whose origin is an include. An element the root owns, a constraint the root
  attaches to an included fact type included, is checked by U1–U8 exactly as
  today.
- **R0.5 Includes stay as they are.** An included file is a standalone-valid
  model at version 1–4, never unattended, never nested
  (`src/gnd/model/_includes.py:222-237`). No composition rule changes.
- **R0.6 Included elements are read-only to a growth round.** `gnd evolve`
  already refuses to mutate them (evolution contract, "Shared vocabulary
  evolution", lines 618–664). VG4 pins that under the unattended mode; it does
  not relax it.
- **R0.7 One home per rule.** U1–U8 live in "Unattended source" of
  `representation-format.md`; D-12 lives in "Evolve admission (D-12)" of
  `provenance-and-modality.md`. Every other page cites them.

The project's six standing rules
(`.codex/skills/process-phase/references/project.md`) bind every phase; each
spec discharges them by name.

## 1. Scope, sources and authority

Harvested obligations. "Observed" means read or run at `4ad0d216` on
2026-11-22; "inherited" means claimed by a source and not re-measured.

| # | Source | Obligation | Kind | Phase |
|---|---|---|---|---|
| H1 | #221 "Problem" | `gnd check` on the interop fixture with N extra unused value types in one include: 0.49 s at 0, 0.64 s at 100, 2.69 s at 200, 17.69 s at 400 (CLI wall time). The issue's own table gives 265.74 s at 1,000 | observed up to 400; inherited at 1,000 | VG1 |
| H2 | #221 "Where" | profile at 300 extra types: 36.84 of 37.65 s under `universe._denoting_types` (610 calls) → `resolve_reference_value_type` (184,830 calls) → `model_queries._supertype_parents` (184,876 calls) and `ModelIndex.object_map` (185,495 calls). Each call rebuilds two maps over every object type (`universe.py:76-82`, `model_queries.py:21-30`, `model_index.py:173-176`) | observed | VG1 |
| H3 | code | the walk runs twice per object type in `semantic_adapter.adapt_snapshot`: once at `:610-611`, once through `universe_of` at `:707` (`universe.py:299-308`) | observed | VG1 |
| H4 | probe | N/2 entity types each with its own reference value type are superlinear too: 1.60 s at 200, 9.07 s at 400. The cost follows the number of value types: `adapt_snapshot` asks for `denoting_types` only for a value type (`semantic_adapter.py:611`). `_descendant_closure` rebuilds a parents map and runs a fixpoint per call (`universe.py:218-255`); `_kind_of` scans every object type (`:358-363`) | observed | VG1 |
| H4a | probe | one subtype chain with `inherits_reference`, N deep: 0.57 s at 100, 1.67 s at 200. With the three walks replaced (H29) it is still 5.29 s at 400 and 39.09 s at 800, and `gnd validate` alone takes 4.19 s at 400: the cost is the recursion of `model_queries._resolve_reference` (`:46`, 1.36 million calls at 400), which the loader runs too | observed | out of scope (D12) |
| H5 | probe | extra fact types are not superlinear: 0.88 s at 400, 1.25 s at 1,600 | observed | VG1 (control) |
| H6 | probe | `gnd validate`, `flatten`, `export pyrel`, `coverage` and `extract` stay under 1.2 s at 1,600 extra value types | observed | VG1 (boundary) |
| H7 | #221; include-root-routes IR1 spec, finding i1 | `gnd judgments check` runs the checker twice (redacted and unredacted reports) | inherited | VG1 (bound only, D10) |
| H8 | include-root-routes IR1 spec, T9 | the route-level time bound over 1,000 extra types was withdrawn there because it measured the checker; its prior row is kept in that spec | observed by reading | VG1 restores it |
| H9 | include-root-routes close, sweep row 1 | carried: "owner to file an issue; a separate maintenance fix, not a milestone of this roadmap". The issue is #221 | observed by reading | D1 |
| H10 | `synth/oracle/constructive.py:131-157` | the witness oracle has its own `_denoting_types` with the same per-call cost. Not measured | observed by reading | VG1 (D9) |
| H11 | #218; maintenance README of 2026-11-21 | `unattended-growth.md:93-95` and `:289` tell the host to write `sample` and `common-sense`; `_enforce_d12` (`evolve/service.py:402-477`) refuses every source but `llm-inferred`, `user-supplied` and `induced` | observed by reading | VG2 |
| H12 | `provenance-and-modality.md:209-218`; `evolution-contract.md:279-280` | D-12's one home, and its restatement | observed by reading | VG2 |
| H13 | `_unattended.py:56`, `:211-222` | U5 exempts `common-sense` and `induced` from spans; U8 refuses `alethic` for `sample`, `llm-inferred`, `common-sense`, `induced` | observed | VG2 |
| H14 | #222 case 2 | an unattended version-5 root that includes a reviewed version-4 seed: `gnd validate … --document doc.md --require-documents` exits 3 with U2, U3, U4 (three), U5 on the included elements | observed | VG3 |
| H15 | #222 case 1 | the seed itself with `mode: unattended`, `reviewer: none`: exit 3, the same six issues | observed | VG3 (stays refused) |
| H16 | code | composition merges the included elements into the root document (`_includes.py:_merge`), then `_model_warnings` runs `semantic_validate` over the merged document under the root's `source` (`model/__init__.py:299-310`). `_rule_unattended` takes the document alone (`_unattended.py:169`); the origins are known to its caller, not to it | observed | VG3 |
| H17 | probe (H14 output) | U4 issues on included object types are reported at `$.object_types[id=work]` with no `includes[seed]:` prefix; the included fact type and constraint carry it. `remap_issues` maps `$.fact_types[id=…]` selectors only (`_includes.py:245-254`) | observed | VG3 |
| H18 | `representation-format.md:1845-1847` | "Its source mode cannot be `unattended`" speaks of the included file. Nothing says whether an unattended root may include a reviewed file | observed | VG3 |
| H19 | `commands/checking.py:57-120`; `_unattended.py:265-339` | `gnd validate --document` and `--require-documents` walk and count the spans of the composed document | observed by reading | VG3 |
| H20 | #222 case 3 | an unattended root with no documents: `gnd validate` exits 3, U1 "must declare at least one source document"; the issue reports `gnd evolve preview` refusing the same root with "current model validation failed" | observed (validate); inherited (evolve) | VG4 |
| H21 | evolution contract, lines 618–664; `evolve/service.py:262-276`, `:1591-1620` | `gnd evolve` already composes an include root, keeps included elements read-only, and places owned constraints on included fact types through `ConstraintLocator.host: included_fact_type`. "Include-bearing linked-project evolution remains refused" | observed by reading | VG4 |
| H22 | evolution contract, line 258 | `repin-include` is refused by `--policy additive`; without the policy it is admitted | observed by reading | VG4 (D6) |
| H23 | `tests/test_evolve_source_document.py`; unattended-model-growth UG3b | the `source-document` operation adds a declared document in a round. Not exercised on an include root | inherited | VG4 |
| H24 | probe | `gnd coverage` accepts an include root, exit 0. The route list in `representation-format.md:1905-1915` names validate, check, extract, verify, compose, flatten, export pyrel and judgments check, and says every other route refuses. `gnd evolve` (H21) is not listed either | observed | VG5 |
| H25 | #222 "Workaround" | the seed carried as `source: imported`, `proposed`, `deontic`, with the seed file as the root's first document | inherited | VG3 (D3 alternative), VG5 (docs) |
| H26 | `src/gnd/examples/growth/`; `tools/build_growth_example.py`; `tests/test_growth_example.py` | the packaged growth example: one model, two documents, two proposals rebuilt byte-identically | observed by reading | VG5 |
| H27 | include-root-routes close, sweep row 2 | whole-repository `uv run ruff check` is red in dev-tools-delivered scripts; the gate is `uv run ruff check src tests tools` | inherited | all |
| H28 | `project.md`, "Component index" | `python3 scripts/components_index.py changed --base main --strict` before a PR | observed by reading | all |
| H29 | scratch prototype, not the implementation | three per-model tables (resolved value type per object type, its inverse, a children map) patched over `universe._denoting_types`, `_descendant_closure` and `_kind_of`: `gnd check` prints the same text, and takes in process 0.48 s at 1,000 extra value types and 1.04 s at 2,000; 0.64 s and 1.37 s for entity types with their own value types; 0.82 s and 1.69 s for entity types sharing one value type; 0.59 s and 1.27 s for a subtype tree of depth 3; 1.29 s and 3.20 s for N extra value types with N extra fact types over them | observed | VG1 (the bounds are reachable) |

Component index (`dev/components/`), searched 2026-11-22: `check.universe`
(`src/gnd/universe.py`) and `model.query_index` (`ModelIndex`) own VG1's
capability; `model.validation` and `evolve.population_check` are beside
VG2–VG4. Nothing existing computes a per-model denotation table.
`components_index.py review` lists 94 descriptions older than their code; an
index review is offered to the owner (D11) and is not a prerequisite.

`project.md` says in one place that the repository has no component index and
in another where it lives. The index exists and the last two milestones used
it; this plan follows the second statement and reports the first as stale
(D11).

### Issue requests and the phases that discharge them

| Request | Phase |
|---|---|
| #221: `gnd check` not superlinear in the number of object types | VG1 |
| #218: `evolve` and `unattended-growth.md` agree on the sources of a new constraint | VG2 |
| #222: an unattended root builds on a reviewed vocabulary without restating it as unreviewed | VG3 |
| #222: included elements are exempt from U2–U5, attributed to the include, immutable to unattended proposals | VG3 (exempt, attributed), VG4 (immutable) |
| #222: if the current behaviour is intended, document it and the recommended packaging | VG3 (the rule), VG5 (the packaging page) |
| #222 case 3: a root with no documents can take its first `source-document` | VG4 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it says nothing about checker cost or
about which models `gnd validate` admits, so none is read here. The baseline
is the probe rows H1–H6, H14, H15 and H20.

## 2. Contract proposal and product behavior

### VG1 — checker cost in the number of object types

- One table per model answers "which value type denotes this object type"
  and "which object types does this value type denote", built once from
  `resolve_reference_value_type` (R0.2). `_denoting_types`,
  `_descendant_closure` and `_kind_of` read it or an equivalent per-model
  table. Where the table lives is a VG1 spec decision; the proposal is
  `ModelIndex`, which is already shared by one public call
  (`model_index.py:52-71`).
- No report changes (R0.1). No CLI flag, schema or exit code changes.
- The time bounds are tests over the layer changed (standing rule 2): an
  absolute bound at 1,000 extra types and a doubling ratio, per shape (H1,
  H4). The shapes: unused value types; entity types each with its own
  reference value type; entity types sharing one reference value type; a
  subtype tree of depth 3 with `inherits_reference`. The control adds as many
  fact types as value types (H5, H29).
- `gnd judgments check` keeps its two checker runs (D10); it is bounded at
  twice the `gnd check` bound.

### VG2 — sources a new constraint may carry in `gnd evolve`

Proposed under D2 (a): D-12 also admits a new `sample` constraint and a new
`common-sense` constraint when it is `proposed` and `deontic`. `sample` or
`common-sense` with `confirmed` or `alethic` still refuses. The refusal
message names the two new combinations. D-12's home lists them and the
evolution contract's restatement follows. If the owner rules (b), no code
changes and `unattended-growth.md` changes at lines 93–95 and 289; the
maintenance README states both.

### VG3 — an unattended root that includes a reviewed vocabulary

Proposed under D3 (a):

- `gnd validate` admits a version-5 root with `source.mode: unattended` and
  includes. U1 reads the root's `source`. U2–U6 and U8 skip every element
  whose origin is an include; those elements were validated standalone at
  resolution step 8 under their own file's rules. An element the root owns is
  checked as today (R0.4).
- The span walk of `--document` and the counts of `--require-documents`
  cover root-owned elements only. A span an included element carries is not
  the root's claim and names no document the root declares.
- An included file with `mode: unattended` keeps `include:forbidden-section`
  (R0.5). The seed with the mode set on itself keeps U2–U5 (H15).
- Attribution (D5): `gnd validate` prints one line per include of an
  unattended root: its id, sha256, and how many object types, fact types and
  constraints it contributes, with how many of those constraints are
  `confirmed`. Diagnostics on included object types gain the
  `includes[ID]:` prefix the format already promises (H17).
- "Unattended source" becomes the home of the include rule; "Model includes"
  cites it (R0.7, H18).

### VG4 — growth rounds on that root

- `gnd evolve preview`, `apply` and `finalize` accept the VG3 root. A round
  may add root-owned object types, fact types and constraints, attach
  constraints to included fact types, and add a `source-document`. Every
  added element is checked by U1–U8 and D-12.
- An operation that would change an included element refuses as today, with
  a test under the unattended mode (R0.6).
- First document (D4): proposed (a), U1 admits a missing or empty
  `documents` list while the root owns no object type, fact type or
  constraint. Such a root validates, so `gnd evolve` reads it and the first
  round's `source-document` operation declares the first document. Once the
  root owns one element, U1 is as today.
- Include pins (D6): proposed, a `repin-include` on an unattended root is
  refused by `gnd evolve` with or without `--policy additive`. An owner
  re-pins by editing the root.

### VG5 — one example, the pages and the replies

- A packaged example beside `examples/growth/`: a reviewed seed model, an
  unattended root that includes it and declares no document, two documents
  and two proposals built by a tool as `tools/build_growth_example.py` does.
  Round 1 declares the first document and adds elements; round 2 attaches a
  `sample` constraint to an included fact type.
- `unattended-growth.md` gains "Starting from a reviewed vocabulary". The
  route list of "Model includes" names every route that resolves an include
  root, `gnd coverage` and `gnd evolve` included (H24).
- Release notes; drafted replies to #221, #222 and #218.

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| VG1 | nothing | `src/gnd/universe.py`, `src/gnd/model_index.py`, a new `tests/test_vg1_object_type_scaling.py`, `tests/test_ir1_judgments_includes.py` (T9 row restored), `docs/release-notes.md`, `dev/components/` |
| VG2 | D2 ruled | for (a): `src/gnd/evolve/service.py` (`_enforce_d12`), `provenance-and-modality.md` (D-12), `evolution-contract.md:279-280`, a new `tests/test_vg2_evolve_sources.py`, `tests/test_unattended_growth_guidance.py`, `docs/release-notes.md`. For (b): `unattended-growth.md` and the two test files |
| VG3 | D3 ruled (a) | `src/gnd/model/_unattended.py`, `src/gnd/model/__init__.py` (`_model_warnings`), `src/gnd/model/_includes.py` (`remap_issues`), `src/gnd/commands/checking.py`, `representation-format.md` ("Unattended source", "Model includes"), a new `tests/test_vg3_unattended_includes.py`, `tests/test_unattended_mode.py`, `tests/test_mc1_model_includes.py`, `docs/release-notes.md` |
| VG4 | VG3 merged into the branch; D4 and D6 ruled | `src/gnd/evolve/service.py`, `src/gnd/evolve/_includes.py`, `src/gnd/model/_unattended.py` (U1), `evolution-contract.md`, `representation-format.md` (U1 row), a new `tests/test_vg4_seeded_growth_rounds.py`, `tests/test_evolve_source_document.py`, `tests/test_mc3_evolution.py` |
| VG5 | VG1–VG4 | a new example folder under `src/gnd/examples/`, a new builder under `tools/`, `unattended-growth.md`, `representation-format.md` (route list), `docs/agents/model-from-text.md`, `docs/agents/evolve.md`, `docs/release-notes.md`, a new `tests/test_vg5_seeded_growth_example.py`, the packaged-example inventories the guards name, `notes/issue-replies.md` |

Order: VG1, VG2, VG3, VG4, VG5, one at a time on one topic branch. The graph
is acyclic. VG1 needs no ruling beyond the plan gate and is the first ready
phase. VG2 and VG3 each wait for one ruling and do not wait for each other.
VG4 and VG5 are outlines until VG3's spec is approved. If D3 is ruled (b),
VG3 becomes a documentation phase, VG4 shrinks to D4, and VG5's example uses
the imported packaging of H25.

Other writers. literature-host-interfaces changes
`src/gnd/examples/literature/`; no file here overlaps except
`docs/release-notes.md` and `.gnd-planning/PROJECT.md`, where the second
branch to merge rebases. Start condition: `main` at `4ad0d216` or later.

Fixtures. VG1 uses the interop example
(`gnd.examples.literature.interop.build(out)`) grown by its own test helper;
the helper and the four shapes are in the VG1 spec. VG3 and VG4 use the
two-file case of #222, authored in the tests, and the small include case
`tests/test_mc1_model_includes.py:write_case`.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| VG1 | **VG1-C1** for every model that loads under `examples/` and `tests/fixtures/`, `resolve_reference_value_type`, `denoting_types`, `descendant_closure` and `universe_types` return what they return at the base commit, for every object type. **VG1-C2** `gnd check` on the interop checking root with 1,000 extra unused value types gives the exit code and the constraint verdicts it gives with none, in under 10 s in process. **VG1-C3** the same bound for 1,000 extra types as entity types with their own reference value types, as entity types that share one reference value type, and as a subtype tree of depth 3 with `inherits_reference`; and for 1,000 extra value types with 1,000 extra fact types over them. **VG1-C4** for each of the four object-type shapes, 2,000 extra types cost at most 3 times 1,000. **VG1-C5** `gnd judgments check` at 1,000 extra types, under 20 s, and IR1's withdrawn T9 row is restored at the bound it first named. **VG1-C6** the report bytes of the focused checker lane are unchanged | H9; H10 under D9 |
| VG2 | **VG2-C1** a proposal built exactly as `unattended-growth.md` describes, one `sample` and one `common-sense` constraint, `proposed` and `deontic`, previews and applies, exit 0. **VG2-C2** each of the two sources with `confirmed`, and each with `alethic`, exit 3 with the D-12 refusal. **VG2-C3** the D-12 home, its restatement and the growth document name the same combinations; a test reads all three. **VG2-C4** on an unattended model the same proposal passes U5 and U8 | none |
| VG3 | **VG3-C1** the #222 root (H14) validates, exit 0, with `--document` and `--require-documents`. **VG3-C2** the same root with one root-owned `confirmed` constraint, one root-owned `explicit` constraint, one root-owned object type without a span, each alone, exit 3 with U2, U3, U4. **VG3-C3** a constraint the root attaches to an included fact type without a span, exit 3, U5, at its `$.fact_type_constraints[i].constraints[j]` address. **VG3-C4** an included file with `mode: unattended`, exit 3, `include:forbidden-section`; the seed with the mode on itself, exit 3, U2–U5 (H15). **VG3-C5** span counts cover root-owned spans only. **VG3-C6** the attribution lines name each include, its sha256 and its counts. **VG3-C7** a model without the mode, with or without includes, gives byte-identical `gnd validate` output (R0.3). **VG3-C8** an issue on an included object type carries `includes[ID]:` (H17) | H25 if D3 is (b) |
| VG4 | **VG4-C1** a round on the VG3 root adds a root-owned fact type with spans and a constraint attached to an included fact type; preview, apply and finalize exit 0 and the result validates. **VG4-C2** an operation that modifies, renames or deletes an included element exits 3. **VG4-C3** a root with no documents and no owned element validates; its first round declares a document and adds an element; a root with an owned element and no document keeps U1. **VG4-C4** `repin-include` on an unattended root exits 3 with and without `--policy additive` (D6). **VG4-C5** `--check-population` and `--populated` behave on the root as on a model without includes | H23 |
| VG5 | **VG5-C1** the example's proposals rebuild byte-identically and its two rounds apply. **VG5-C2** the grown root passes `gnd validate --require-documents` with both documents, `gnd check` over the example population, and `gnd judgments check`. **VG5-C3** the route list names every route a test shows resolving an include root. **VG5-C4** the three replies are drafted and name what is on `main` and what is not released | H24 |

Each phase also runs the structure and inventory guards,
`uv run ruff check src tests tools`, an independent review of its diff, a
refactoring review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each (R0.7).** U1's first-document rule and the include
  exemption go in "Unattended source". D-12's two new rows go in "Evolve
  admission (D-12)". `unattended-growth.md`, the evolution contract,
  `docs/agents/model-from-text.md` and `docs/agents/evolve.md` cite them.
- **Packaged skills.** `gnd-orm-core`, `gnd-model-evolve` and
  `gnd-model-from-text` reference files change; their manifests are held by
  `tests/test_packaged_skills.py`, in the guard block.
- **Release notes.** One entry per phase under the unreleased heading.
- **Compatibility.** VG1 changes no output. VG2 (a) and VG3 (a) admit inputs
  that 0.4.0 refuses and refuse nothing 0.4.0 admits. VG4 under D6 refuses
  one input 0.4.0 admits: `repin-include` on an unattended root without the
  additive policy; 0.4.0 admits no unattended include root at all (H14), so
  no shipped model is affected. No schema version changes.
- **Issue replies.** The close drafts them; the owner posts them.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A cached table and the function it caches drift apart | VG1-C1, over every loadable fixture, against the base commit |
| The time-bound test is flaky on a loaded machine | the absolute bound is about 26 times under today's cost at 1,000; the ratio test repeats and takes a median, as `tests/test_coverage_scaling.py` does; the VG1 spec says which lane each runs in |
| The fix covers the measured shape and misses another | four shapes in VG1-C2 and VG1-C3, chosen from H4; fact types as the control (H5). The one shape known to stay slow is named, measured and out of scope (H4a, D12) |
| An unattended host writes its own "reviewed" include and so carries `confirmed` claims into an unattended model | the attribution lines of VG3 name every include and its confirmed count on each validate; D6 keeps a round from changing a pin; the growth document says the pins are the owner's. GND cannot know who wrote a file, and the page says so |
| The exemption leaks to a root-owned element | VG3-C2 and VG3-C3, one case per rule and one for an attached constraint (R0.4) |
| Two enforcement sites for the exemption (the rule walk and the span walk) disagree | one origin test shared by both; the VG3 spec names it (standing rule 4) |
| Relaxing U1 lets a model with claims and no documents through | U1 stays whenever the root owns an element (VG4-C3); U4, U5 and U7 already refuse a span that names no declared document |
| D-12 widened too far | VG2-C2: four refusal cases, one per source and failing field |
| The example and its pages state behaviour the tests do not hold | VG5-C1 and VG5-C2 run the example; VG5-C3 reads the route list against live routes |

## 7. Out of scope

- #215 and #216 (literature-host-interfaces); #214 and #217 (delivered, not
  released).
- Release, tag and publication; a 0.5.0 milestone is separate.
- Making `gnd judgments check` run the checker once (D10).
- The witness oracle's walk, unless D9 brings it in.
- A subtype chain hundreds of types deep (H4a): its cost is in the reference
  resolver the loader shares, not in the checker's universe walk (D12).
- Nested includes, more than eight includes, or an unattended included file.
- Include roots on routes that refuse them today (`gnd measure`,
  `gnd codegen`, `gnd witness`, `gnd exp`, the Lean and Souffle exports).
- A curated, non-unattended edition that promotes grown elements to
  `confirmed`: that is `gnd evolve` under a reviewer, as today.
- The whole-repository ruff red (H27) and the stale lines of `project.md`
  (D11): owner policy, outside a phase.

## 8. Execution, approval and review protocol

- Default `auto=false`: the owner approves this plan, then each spec, before
  code. `process-milestone reviewed-vocabulary-growth` runs it; `auto` needs
  the owner's explicit delegation for this milestone.
- Plan review and close review: the project's bar is the maintained GND
  panel (`project.md`, "Plan-review bar"). The owner selects full or light
  (D8). Convergence follows the bounded rules; one round is planned, a second
  only if the first blocks.
- The plan gate is recorded in `001-plan-gate.md` after the review's findings
  are dispositioned.
- Each phase: spec, owner gate, code, focused gates, one independent
  reviewer over the diff (the review helper, one reviewer in a different
  tool), refactoring review, record, commit.
- One pull request from the topic branch to `main`. Merge stays with the
  owner. Before the PR,
  `python3 scripts/components_index.py changed --base origin/main --strict`
  exits 0.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| VG1 | `uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short` | exit 0 |
| VG2 | `uv run pytest -q tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py --tb=short` | exit 0 |
| VG3 | `uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py --tb=short` | exit 0 |
| VG4 | `uv run pytest -q tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py --tb=short` | exit 0 |
| VG5 | `uv run pytest -q tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_unattended_growth_guidance.py tests/test_ir1_judgments_includes.py --tb=short` | exit 0 |
| all | the structure and inventory guard block of `project.md`, and `uv run ruff check src tests tools` | exit 0 |

The lanes name files that exist at `4ad0d216`, plus one new file per phase.
Affected consumers are read again at each spec and may be widened there. No
broad lane (`-m "evidence or census"`) is selected. Whether VG1's ratio test
runs in the default lane or the `slow` lane is a VG1 spec decision; the `slow`
lane is opt-in (`pyproject.toml:79`) and is not a gate unless the owner
selects it.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them.

| ID | Question | Proposed |
|---|---|---|
| D1 | One milestone for #221, #218 and #222, or #222 alone with the other two as maintenance passes, as the roadmap (#218) and the include-root-routes close (#221, H9) first placed them | One milestone. The three serve one reporter and one workflow, and VG5's example needs all three. Cost: #221 and #218 wait for a plan gate they would not need as maintenance passes. If the owner prefers speed, VG1 and VG2 can run as maintenance passes from their specs unchanged |
| D2 | #218: (a) widen D-12 to admit `sample` and `common-sense` when `proposed` and `deontic`, or (b) change the growth document to say `llm-inferred` with the basis in `provenance.rationale_world_fact` | (a), as the maintenance README proposed. (b) hides the basis in free text and loses U5's span exemption for library evidence |
| D3 | #222: (a) an unattended root may include a reviewed model, with included elements exempt from U2–U6 and U8, or (b) keep today's refusal and document the imported, proposed, deontic packaging as the supported route | (a). (b) makes reviewed constraints read as unreviewed in every grown model and needs a second, curated edition to restore them |
| D4 | #222 case 3: (a) U1 admits no documents while the root owns no element; (b) `gnd evolve` alone admits such a root when the proposal's first operation is a `source-document` add, as the issue suggests; (c) document that the root is authored with its first document | (a): one rule in one place, and `gnd validate` and `gnd evolve` agree on the same root. (b) makes `gnd evolve` accept a model `gnd validate` refuses |
| D5 | VG3: what names the include of an included element under an unattended root | one `gnd validate` line per include (id, sha256, element counts, confirmed count), and the `includes[ID]:` prefix on every diagnostic. The exact text is a VG3 spec decision |
| D6 | May a growth round re-pin an include of an unattended root | No: `gnd evolve` refuses `repin-include` on an unattended root with or without the additive policy. Alternative: keep today's rule (refused under the policy only) and say in the growth document that rounds run with it |
| D7 | Phase diff reviewer | the review helper (`.claude/skills/process-phase/scripts/review_tool.py`, subject `phase`), one reviewer in a different tool, as the last two milestones used |
| D8 | Plan review and close review instrument | the GND panel light, as include-root-routes used; the full panel if the owner prefers it, as pyrel-rules-coverage used. Neither is selected yet |
| D9 | The witness oracle's own denotation walk (H10) | VG1 measures `gnd verify` at 1,000 extra types. If it is over the bound, VG1 gives that walk its own table, with no import from the checker; if not, it is recorded and left |
| D10 | `gnd judgments check` runs the checker twice (H7) | Out of scope; bounded at twice the check bound (VG1-C5) and recorded as a successor question |
| D11 | `project.md` says both that there is no component index and where it lives; 94 index descriptions are older than their code | The owner corrects `project.md` outside a phase. An index review (the `components` skill, Review mode) is offered, not required |
| D12 | A subtype chain hundreds of types deep stays slow after VG1 (H4a) | Out of scope: no reported vocabulary has one, and the fix is in `_resolve_reference`, which the loader and the type checks share. Recorded as a successor question with its numbers. Alternative: a sixth phase |

Open questions carried into the specs: VG1, where the table lives and how it
treats a `Model` built in code whose rows `model_dump()` alters (the accepted
limit of the 2026-11-11 query-budget pass); VG3, whether the origin reaches
`_rule_unattended` as an argument, a context variable, or a filter over its
remapped issues, and what U7 does with a span an included element carries;
VG4, whether D6's refusal belongs to the additive-policy table or to the mode.
