# Reviewed-vocabulary growth · plan r6

**Status: r6, 2026-11-23: r4 as approved by the owner ([plan gate](../001-plan-gate.md)) with the close amendments of §11, tagged `(c1)`, and the close review's repairs, tagged `(c2)`.** Prior status of r5: "r4 as approved … with the close amendments of §11, tagged `(c1)`." Prior status line of r4, kept: "Status: r4, 2026-11-23. Reviewed once, at r1; not approved." The owner
selected the GND review panel light for the plan review on 2026-11-23 (D8).
The panel read r1 (sha256
`3d4a06b864a339f55c82a83c2e9dad6cc704d45bf156aeaeb1aaa086fbd4eb7f`, commit
`a04e5624`): four of six seats succeeded at high effort, each with `revise`.
The evidence and the disposition are in
[`evidence/plan-review-r1/`](../evidence/plan-review-r1/disposition.md). r2
applied that round's repairs, at the owner's request of the same day.

A second round read r2 (sha256
`7a2c6bf7e69287aba9b6fcd6472138900e2c80dd14fc0ff2a163540a63e90b9b`, commit
`a4db0773`) and ended below quorum: two of six seats succeeded, so **there is
no panel result for r2**
([record](../evidence/plan-review-r2/disposition.md)). The two reviews that
returned raised four points; r3 repaired them at the owner's request.

A third run read r3 (sha256
`96acc9bf0ad324802f882b863fe75e5c6910bede25f3ac86fa68032f8ae1f7ff`, commit
`28f94c58`) the same day, at the owner's request, and also ended below
quorum, two of six seats: **there is no panel result for r3**
([record](../evidence/plan-review-r3/disposition.md)). The two reviews that
returned raised eight points, none above medium; r4 repairs them at the
owner's request. r4 carries no review opinion of its own, and no further
review run is planned (§8). No `auto` delegation exists for this milestone.
Approval is recorded only in a plan-gate record, which does not exist yet.

Tags mark what changed since r1, at the site of the change: `(p1)` a repair
from panel round 1; `(s2)` a repair from one of the two single reviews of
round 2, which is not a panel finding; `(s3)` the same for the third run;
`(o)` an owner decision; `(m)` a fact
re-read on `main` at `c47dc126`, or a correction by the author that no
reviewer raised. Untagged text is r1.

This plan covers three open issues that no milestone owns:
[#221](https://github.com/vasiloglou/gnd-public/issues/221),
[#222](https://github.com/vasiloglou/gnd-public/issues/222) and
[#218](https://github.com/vasiloglou/gnd-public/issues/218).

The other open issues are owned elsewhere and are out of scope here `(m)`:

| Issue | Owner | State on 2026-11-23 |
|---|---|---|
| [#215](https://github.com/vasiloglou/gnd-public/issues/215), [#216](https://github.com/vasiloglou/gnd-public/issues/216) | [literature-host-interfaces](../../literature-host-interfaces/README.md) | outline r1; its full plan is being written in another session |
| [#226](https://github.com/vasiloglou/gnd-public/issues/226) | [literature-reading-reference](../../literature-reading-reference/README.md) | outline r1 |
| [#227](https://github.com/vasiloglou/gnd-public/issues/227), [#228](https://github.com/vasiloglou/gnd-public/issues/228) | [growth-round-outcomes](../../growth-round-outcomes/README.md) | outline r1; it changes two files this plan changes (H36, §3) |
| [#214](https://github.com/vasiloglou/gnd-public/issues/214), [#217](https://github.com/vasiloglou/gnd-public/issues/217) | [include-root-routes](../../include-root-routes/README.md), [pyrel-rules-coverage](../../pyrel-rules-coverage/README.md) | closed on 2026-11-23: delivered on `main` (PR 220, PR 223), not released |

**Provenance.** r1 is the first bytes of this file (its sha256 is above;
merged in PR 230 as `3765f3f5`); there is no earlier outline. r2 is the
bytes round 2 read, and r3 the bytes the third run read. Phase IDs
VG1–VG5, criteria IDs and decisions D1–D12 are kept. r2 adds criteria VG1-C7,
VG1-C8, VG3-C9 and VG3-C10, obligations H30–H36 and decisions D13 and D14.
r4 adds criterion VG3-C11 and obligations H37–H39 `(s3)`.
Every code citation was read at `4ad0d216` (`main`, 2026-11-22); no cited
source, test or reference file differs at `c47dc126` (`main`, 2026-11-23), by
`git diff` `(m)`. Every measurement marked "observed" was run on one laptop,
once, on 2026-11-22 unless its row gives another date.
#218 was already planned as a
[maintenance pass](../../../maintenance/2026-11-21-evolve-constraint-sources/README.md);
D1 proposes to carry it here.

## Goal and completion predicates

A host grows several unattended models from one shared, owner-reviewed
vocabulary, at the size such a vocabulary has, and what the growth document
tells the host to write is what `gnd evolve` admits.

- **VG1.** `gnd check` cost grows about linearly with the number of object
  types. Three gates say so `(p1)`. One check builds the supertype map a
  number of times that does not depend on the size of the model (today
  184,876 times at 300 extra types, H2). Doubling the extra types from 1,000
  to 2,000 costs at most 3 times as much, for each of four shapes. The
  interop fixture with 1,000 extra object types checks in under 10 s in
  process (today: 265.74 s, #221), for each shape. Only the third depends on
  the machine (§6). Every report is unchanged. A subtype chain hundreds of
  types deep stays slow for a separate reason and is out of scope (D12).
- **VG2.** A constraint proposal written exactly as `unattended-growth.md`
  says (`sample` for row evidence, `common-sense` for library evidence, always
  `proposed` and `deontic`) is admitted by `gnd evolve`, and rule D-12 and the
  growth document say the same thing (D2).
- **VG3.** A version-5 root with `source.mode: unattended` that includes a
  reviewed, non-unattended model validates, exit 0. The included elements keep
  their own `source`, `status` and `modality`; rules U2–U8 apply to the
  elements the root owns (D3). What an include must be to earn the exemption
  is D13, and what happens to a span an included element carries is D14
  `(p1)`. `gnd validate` prints one line per include in its text output
  `(s3)`, and a diagnostic on an included element names its include (D5)
  `(p1)`.
- **VG4.** That root grows through `gnd evolve preview`, `apply` and
  `finalize`: a round adds root-owned elements and constraints attached to
  included fact types, included elements stay read-only, and the first round
  can declare the first source document (D4).
- **VG5.** One packaged example runs the whole path: a reviewed seed, an
  unattended root that includes it, two growth rounds, then `gnd validate`,
  `gnd check` and `gnd judgments check` on the result. The growth document and
  the representation format describe it, and a reply is drafted for each of
  the three issues.

The VG3, VG4 and VG5 predicates are written for D3 (a). If the owner rules
D3 (b) they cannot be met as written, and a plan amendment replaces them
before VG3 starts (§3) `(s3)`.

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
  whose origin is an include. An element the root owns is checked by U2–U8
  exactly as today. That covers a constraint the root attaches to an included
  fact type, an operation and an obligation (H32, H33). U1 reads the root's
  `source` as today; its one change is D4's first-document rule `(p1)`.
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
2026-11-22; "inherited" means claimed by a source and not re-measured. Rows
H30–H39 and the new half of H27 were read or run on 2026-11-23.

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
| H13 | `_unattended.py:56-58`, `:211-222`, `:229-234` (citation corrected `(p1)`) | U5 exempts `common-sense` and `induced` from spans (`:211-222`); U8 refuses `alethic` for `sample`, `llm-inferred`, `common-sense`, `induced` (`:58`, `:229-234`) | observed | VG2 |
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
| H27 | include-root-routes close, sweep row 2; probe of 2026-11-23 at `c47dc126` `(p1)` | whole-repository `uv run ruff check` exits 1 with 198 errors, every one under `.codex/skills` or `.claude/skills`, the scripts dev-tools delivers; `uv run ruff check src tests tools` exits 0. `project.md:129-131` says the whole-repository command exits 0 since issue 177; that sentence is the stale one (D11) | observed | all |
| H28 | `project.md`, "Component index" | `python3 scripts/components_index.py changed --base main --strict` before a PR | observed by reading | all |
| H29 | scratch prototype, not the implementation | three per-model tables (resolved value type per object type, its inverse, a children map) patched over `universe._denoting_types`, `_descendant_closure` and `_kind_of`: `gnd check` prints the same text, and takes in process 0.48 s at 1,000 extra value types and 1.04 s at 2,000; 0.64 s and 1.37 s for entity types with their own value types; 0.82 s and 1.69 s for entity types sharing one value type; 0.59 s and 1.27 s for a subtype tree of depth 3; 1.29 s and 3.20 s for N extra value types with N extra fact types over them | observed | VG1 (the bounds are reachable) |
| H30 | probe, 2026-11-23, at `a04e5624` `(p1)` | 0.4.0 admits some unattended include roots. A version-5 unattended root whose included elements are `llm-inferred`, `proposed` and `deontic` and carry spans over a document the root declares: `gnd validate ROOT --document doc.md --require-documents` exits 0. Under that flag one unchecked span is an error, so the included spans were re-hashed | observed | VG3 (D14), §5 |
| H31 | `_includes.py:231-237`, `:239-241`; #222 `(p1)` | composition validates each included file alone and keeps only its errors (`:234`): a warning, such as D-03's on an unconfirmed inferred `alethic` constraint, does not stop an include. The file's own `source` is retained as origin metadata and no rule reads it. The #222 seed is `explicit`, `confirmed` and `alethic` and names no reviewer | observed | VG3 (D13) |
| H32 | `model/_validation.py:2055-2068`; `_unattended.py:193`, `:229`; `_includes.py:222-227` `(p1)` | U2 and U8 walk every provenance-bearing element: constraints, operations and obligations. An included file cannot declare `operations`, so in an include root every operation and obligation is the root's | observed by reading | VG3, VG4 (D4) |
| H33 | `_includes.py:162-167` `(p1)` | a constraint the root attaches through `fact_type_constraints` has origin `model`, although in the composed document it sits inside an included fact type | observed by reading | VG3 (R0.4) |
| H34 | `_unattended.py:204-226` `(p1)` | under the mode U7 has no walk of its own: it is raised inside the U4, U5 and U6 walks, on the spans those rules read | observed by reading | VG3 (D14) |
| H35 | `tests/test_unattended_mode.py:118-122` `(p1)` | five U1 branches are pinned there. Two of them, documents absent and documents empty, are on a model that owns elements | observed by reading | VG4 (D4) |
| H36 | growth-round-outcomes outline r1, lines 88–93; `PROJECT.md`, "Proposed order" (both on `main` since PR 229) `(m)` | that outline's GO1–GO3 change `src/gnd/evolve/service.py` and its GO4 changes `unattended-growth.md`; the roadmap asks for one writer at a time on each and orders VG1, then GO1, then VG2–VG5 | observed by reading | VG2, VG4, VG5 (§3) |
| H37 | `model/__init__.py:299-310`, `:317`; `commands/checking.py:83-93`; `api.py:608` `(s3)` | `remap_issues` has two callers, both in `_model_warnings` (`:302`, `:305`). The issues of the `--document` span walk are built in `_cmd_validate_documents` and go to the report as they are, so one on an included element keeps its composed address and has no `includes[ID]:` prefix. The loaded model holds its origins (`:317`), so the walk's caller can remap them | observed by reading | VG3 (D5) |
| H38 | `payloads.py:137-149`, `:693-718`; `commands/checking.py:145-156` `(s3)` | the `validate` payload "stays on the frozen variants". It has `issues` and `warnings` and no other place for a line about an include. In text output a valid model prints its warnings and then one `OK:` line | observed by reading | VG3 (D5), §5 |
| H39 | `_unattended.py:104-118`, `:284-293` `(s3)` | the span walk counts every span it visits. It re-hashes one only when its document was supplied and its shape is valid, and a span it skips gets no diagnostic of its own there: it is one more in `unattended:spans-unchecked`, whose message says to supply every declared document. Today a malformed span never reaches the walk under the mode, because U7 refuses it at load | observed by reading | VG3 (D14) |

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
| #222: included elements are exempt from U2–U5, attributed to the include, immutable to unattended proposals | VG3 (exempt as D3, D13 and D14 rule; attributed by one line per include and on diagnostics, D5 `(p1)`), VG4 (immutable) |
| #222: if the current behaviour is intended, document it and the recommended packaging | VG3 (the rule), VG5 (the packaging page) |
| #222 case 3: a root with no documents can take its first `source-document` | VG4 |

This is a framework milestone. An experiment-claim census (`gnd coverage`)
counts claims over a domain model; it says nothing about checker cost or
about which models `gnd validate` admits, so none is read here. The baseline
is the probe rows H1–H6, H14, H15, H20 and H30.

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
- Three kinds of test over the layer changed (standing rule 2) `(p1)`. A
  call count, which does not depend on the machine: how many times one check
  builds the supertype map (`model_queries._supertype_parents`), equal at two
  model sizes. A doubling ratio: two sizes run in one test on one machine.
  An absolute bound at 1,000 extra types, per shape (H1, H4): it depends on
  the machine and is judged on the one that ran the base sweep. The shapes:
  unused value types; entity types each with its own reference value type;
  entity types sharing one reference value type; a subtype tree of depth 3
  with `inherits_reference`. The control adds as many fact types as value
  types (H5, H29).
- `gnd verify` is measured at the same size (D9, VG1-C8) `(p1)`. The witness
  oracle's walk changes only if that measurement is over the bound, and then
  inside its own module (R0.2).
- `gnd judgments check` keeps its two checker runs (D10); it is bounded at
  twice the `gnd check` bound.

### VG2 — sources a new constraint may carry in `gnd evolve`

Proposed under D2 (a): D-12 also admits a new `sample` constraint and a new
`common-sense` constraint when it is `proposed` and `deontic`. `sample` or
`common-sense` with `confirmed` or `alethic` still refuses. The refusal
message names the two new combinations. D-12's home lists them and the
evolution contract's restatement follows. If the owner rules (b), no code
changes: `unattended-growth.md` changes at lines 93–95 and 289 to say
`llm-inferred` with the basis in `provenance.rationale_world_fact`, and VG2's
criteria take their (b) reading (§4) `(p1)`. The maintenance README states
both.

### VG3 — an unattended root that includes a reviewed vocabulary

Proposed under D3 (a), with D13 (a) and D14 (a):

- `gnd validate` admits a version-5 root with `source.mode: unattended` and
  includes. U1 reads the root's `source`. U2–U6 skip every element whose
  origin is an include `(p1)`. So does U7, but for the one check D14 keeps
  `(s3)`. U8 skips an included element only when its
  status is `confirmed` (D13) `(p1)`: an unconfirmed `sample`, `llm-inferred`,
  `common-sense` or `induced` claim stays refused as `alethic`, whichever
  file it sits in. An element the root owns is checked as today (R0.4).
- What the exemption rests on `(p1)`. Composition validates each included
  file alone (`_includes.py:231-237`). That proves the file is a valid model.
  It does not prove that anyone reviewed it (H31). The statement of review is
  the pin: the root names each include by id, path and sha256, the owner
  authors the root, and a growth round cannot change a pin (D6). GND checks
  the bytes against the pin and cannot check who wrote them. That is a named
  limit (§6); D13 holds the stricter alternative.
- Spans (D14) `(p1)`. U4–U6 ask nothing of an included element. A span an
  included element carries is the root's business only when it names a
  document the root declares: its `document_sha256` is the sha256 of an
  entry of the root's `source.documents`. Such a span is treated as today
  (H30). U7 still requires it to be well-formed `(s3)`: the four keys, two
  hex digests, integer offsets, `0 <= start < end`. The span walk of
  `--document` re-hashes it and the counts of `--require-documents` include
  it. Without U7's check a malformed one would be counted and never
  re-hashed, and the only message would ask for documents the user already
  supplied (H39). An included span that names any other document is not the
  root's claim: no rule reads it, and it is neither checked nor counted.
- The walk also covers every root-owned span it visits today. It visits the
  spans of object types, fact types, constraints and sample rows; a span on
  an operation or an obligation is neither checked by U7 nor counted, as
  "Unattended source" already says, and VG3 does not change that `(s2)`.
- An included file with `mode: unattended` keeps `include:forbidden-section`
  (R0.5). The seed with the mode set on itself keeps U2–U5 (H15).
- Attribution (D5): the text output of `gnd validate` prints one line per
  include of an unattended root that validates, before its `OK:` line
  `(s3)`: its id, sha256, and how many object types, fact types, sample rows
  `(s3)`, constraints and deontic notes `(s2)` it contributes; and of those
  constraints, how many are `confirmed`, how many are `alethic`, and how
  many are `explicit` or `user-supplied` `(p1)`. The JSON payload does not
  carry the lines: the `validate` payload is frozen and has no field for
  them (H38). D5 holds the alternatives `(s3)`.
- Diagnostics on included object types gain the `includes[ID]:` prefix the
  format already promises (H17). So do the diagnostics of the span walk,
  which bypass the remapping step today (H37): VG3 passes them through
  `remap_issues` with the loaded model's origins `(s3)`. The prefix is part
  of an issue's `path`, so text and JSON output both carry it. `gnd check`
  and `gnd judgments check` print no attribution line; §6 says why `(p1)`.
- "Unattended source" becomes the home of the include rule, the statement
  about the pin and the limit; "Model includes" cites it (R0.7, H18).

### VG4 — growth rounds on that root

- `gnd evolve preview`, `apply` and `finalize` accept the VG3 root. A round
  may add root-owned object types, fact types and constraints, attach
  constraints to included fact types, and add a `source-document`. Every
  added element is checked by U1–U8 and D-12.
- An operation that would change an included element refuses as today, with
  a test under the unattended mode (R0.6).
- First document (D4): proposed (a), U1 admits a missing or empty
  `documents` list while the root declares at least one include `(s3)` and
  makes no claim of its own `(p1)`: it owns
  no object type, no fact type, no constraint wherever it is written (one
  attached through `fact_type_constraints` counts), no operation and no
  obligation. A deontic note is a claim too, and it carries no source,
  status or provenance for a U rule to read, so the rule is written on the
  file `(s2)`: every section of the root other than `version`, `model_id`,
  `source` and `includes` is absent or empty. That covers `deontic_notes`,
  `rejected_proposals` and `reference_populations` with the five kinds
  above. The test is read on the root's own document, as authored, before
  composition merges the included elements into it `(s3)`. It cannot be
  read on the composed document, which the U rules read today (H16): there
  the included elements sit in the same sections. It agrees with
  the origin test VG3 uses (standing rule 4; H32, H33). In the four
  sections composition merges (`_includes.py:33`), an element has origin
  `model` exactly when the root file wrote it, and an include cannot declare
  any other section the rule names (`_includes.py:222-223`). A model that
  declares no include keeps U1 as today, empty or not `(s3)`.
  `reviewer: none` is still required. Such a root
  validates, so `gnd evolve` reads it and the first round's
  `source-document` operation declares the first document. Once the root
  owns one element, U1 is as today.
- Include pins (D6): proposed, a `repin-include` on an unattended root is
  refused by `gnd evolve` with or without `--policy additive`. An owner
  re-pins by editing the root.

### VG5 — one example, the pages and the replies

- A packaged example beside `examples/growth/`: a reviewed seed model, an
  unattended root that includes it and declares no document, two documents
  and two proposals built by a tool as `tools/build_growth_example.py` does.
  Round 1 declares the first document and adds elements; round 2 attaches a
  `sample` constraint to an included fact type (an `llm-inferred` one with a
  span, if D2 is ruled (b)) `(p1)`.
- `unattended-growth.md` gains "Starting from a reviewed vocabulary". The
  route list of "Model includes" names every route that resolves an include
  root, `gnd coverage` and `gnd evolve` included (H24).
- Release notes; drafted replies to #221, #222 and #218.

## 3. Dependencies and artifact homes

| Phase | Needs | Homes it changes |
|---|---|---|
| VG1 | nothing | `src/gnd/universe.py`, `src/gnd/model_index.py`, `src/gnd/semantic_adapter.py` (at most three lines; VG1 spec §6) `(m)`, a new `tests/test_vg1_object_type_scaling.py`, `tests/test_ir1_judgments_includes.py` (T9 row restored), `docs/release-notes.md`, `dev/components/`; `src/gnd/synth/oracle/constructive.py` only if VG1-C8 measures over its bound `(p1)` |
| VG2 | D2 ruled | for (a): `src/gnd/evolve/service.py` (`_enforce_d12`), `provenance-and-modality.md` (D-12), `evolution-contract.md:279-280`, a new `tests/test_vg2_evolve_sources.py`, `tests/test_unattended_growth_guidance.py`, `docs/release-notes.md`. For (b): `unattended-growth.md` and the two test files |
| VG3 | D3 ruled (a); D13 and D14 ruled `(p1)` | `src/gnd/model/_unattended.py`, `src/gnd/model/__init__.py` (`_model_warnings`), `src/gnd/model/_includes.py` (`remap_issues`), `src/gnd/commands/checking.py`, `representation-format.md` ("Unattended source", "Model includes"), a new `tests/test_vg3_unattended_includes.py`, `tests/test_unattended_mode.py`, `tests/test_mc1_model_includes.py`, `docs/release-notes.md` |
| VG4 | VG3 merged into the branch; D4 and D6 ruled | `src/gnd/evolve/service.py`, `src/gnd/evolve/_includes.py`, `src/gnd/model/_unattended.py` (U1), `src/gnd/model/__init__.py` (the root's own document reaches U1) `(s3)`, `evolution-contract.md`, `representation-format.md` (U1 row), a new `tests/test_vg4_seeded_growth_rounds.py`, `tests/test_evolve_source_document.py`, `tests/test_mc3_evolution.py`, `tests/test_unattended_mode.py` and `tests/test_unattended_span_coverage.py` (the U1 branches D4 changes, H35) `(p1)` |
| VG5 | VG1–VG4 | a new example folder under `src/gnd/examples/`, a new builder under `tools/`, `unattended-growth.md`, `representation-format.md` (route list), `docs/agents/model-from-text.md`, `docs/agents/evolve.md`, `docs/release-notes.md`, a new `tests/test_vg5_seeded_growth_example.py`, the packaged-example inventories the guards name, `notes/issue-replies.md` |

Order: VG1, VG2, VG3, VG4, VG5, one at a time on one topic branch. The graph
is acyclic. VG1 needs no ruling beyond the plan gate and is the first ready
phase. VG2 waits for D2, and VG3 for D3, D13 and D14 `(p1)`; they do not
wait for each other. VG4 and VG5 are outlines until VG3's spec is approved.
If D3 is ruled (b), the goal's VG3, VG4 and VG5 predicates and the VG3 and
VG4 criteria cannot be met as written: each requires the include `(s3)`. A
(b) ruling therefore comes with a plan amendment, approved before VG3
starts, that replaces those predicates and criteria and says what is left of
D4, D5, D6, D13 and D14. Its outline: VG3 becomes a documentation phase, VG4
shrinks to the first-document question, and VG5's example uses the imported
packaging of H25. This plan does not write those criteria, because it
proposes (a). VG1 and VG2 do not depend on the ruling. If D2 is ruled (b), VG2
becomes a documentation phase with the (b) criteria of §4, and round 2 of
VG5's example attaches an `llm-inferred` constraint with a span `(p1)`.

Other writers `(m)`. literature-host-interfaces changes
`src/gnd/examples/literature/`; it overlaps this plan only in
`docs/release-notes.md` and `.gnd-planning/PROJECT.md`, where the second
branch to merge rebases. growth-round-outcomes (H36) overlaps in two more
files: `src/gnd/evolve/service.py`, which VG2 and VG4 change here and
GO1–GO3 change there, and `unattended-growth.md`, which VG2 and VG5 change
here and GO4 changes there. One writer at a time on each, in the roadmap's
order: VG1, then GO1, then VG2–VG5, then GO2–GO5. VG1 and GO1 share no file.
If GO1 runs between VG1 and VG2, VG1 merges by its own pull request first
and VG2 starts from a `main` that holds GO1 (§8). Start condition: `main` at
`c47dc126` or later.

Fixtures. VG1 uses the interop example
(`gnd.examples.literature.interop.build(out)`) grown by its own test helper;
the helper and the four shapes are in the VG1 spec. VG3 and VG4 use the
two-file case of #222, authored in the tests, and the small include case
`tests/test_mc1_model_includes.py:write_case`.

## 4. Phases

| Phase | Criteria | Inherited residuals |
|---|---|---|
| VG1 | **VG1-C1** for every model that loads under `src/gnd/examples/` and `tests/fixtures/` (path corrected `(p1)`), and for every object type: the table equals `resolve_reference_value_type`, which VG1 does not change; and `denoting_types`, `descendant_closure`, `kind_of` and `universe_types` return what frozen copies of their bodies at `4ad0d216`, kept in the test file, return `(p1)`. **VG1-C2** `gnd check` on the interop checking root with 1,000 extra unused value types gives the exit code and the constraint verdicts it gives with none, in under 10 s in process. **VG1-C3** the same bound for 1,000 extra types as entity types with their own reference value types, as entity types that share one reference value type, and as a subtype tree of depth 3 with `inherits_reference`; and for 1,000 extra value types with 1,000 extra fact types over them. **VG1-C4** for each of the four object-type shapes, 2,000 extra types cost at most 3 times 1,000. **VG1-C5** `gnd judgments check` at 1,000 extra types, under 20 s, and IR1's withdrawn T9 row is restored at the bound it first named. **VG1-C6** the report bytes of the focused checker lane are unchanged. **VG1-C7** `(p1)` one `gnd check` builds the supertype map the same number of times at 300 and at 600 extra value types, and at most 100 times (today 184,876 at 300, H2); with the old walk patched back in, the count at 300 is over 1,000. **VG1-C8** `(p1)` `gnd verify` at 1,000 extra value types is measured at the base commit and at the phase head, and both figures are in the phase record. Over 10 s at the head: `constructive._denoting_types` gets its own table inside `constructive.py`, importing nothing from `gnd.universe` or `gnd.model_index`, with a test case at that bound. At or under: nothing changes (D9). **Which gate is which** `(p1)`: C1, C6 and C7 read no clock and are the required regression gates; C4 compares two runs on one machine; C2, C3 and C5 are absolute and are judged on the machine that ran the base sweep (§6) | H9; H10 under D9 |
| VG2 | **VG2-C1** a proposal built exactly as `unattended-growth.md` describes, one `sample` and one `common-sense` constraint, `proposed` and `deontic`, previews and applies, exit 0. **VG2-C2** each of the two sources with `confirmed`, and each with `alethic`, exit 3 with the D-12 refusal. **VG2-C3** the D-12 home, its restatement and the growth document name the same combinations; a test reads all three. **VG2-C4** on an unattended model the same proposal passes U5 and U8. **Under D2 (b)** `(p1)`: C1 uses one `llm-inferred`, `proposed`, `deontic` constraint with its `rationale_world_fact`, written as the revised document says, exit 0; C2 pins today's refusal, a new `sample` and a new `common-sense` constraint each exit 3 with the D-12 refusal; C3 is unchanged; C4 uses the same `llm-inferred` constraint, with a span | none |
| VG3 | **VG3-C1** the #222 root (H14) validates, exit 0, with `--document` and `--require-documents`. **VG3-C2** the same root with one root-owned defect, each alone, exits 3 with its rule: a `confirmed` constraint (U2), a `confirmed` operation (U2), an `explicit` constraint (U3), an object type without a span (U4), a fact type whose `sample_spans` miss a row (U6), a span that names an undeclared document (U7) `(p1)`. **VG3-C3** a constraint the root attaches to an included fact type, at its `$.fact_type_constraints[i].constraints[j]` address: without a span, exit 3, U5; as an `alethic` `sample` constraint, exit 3, U8 `(p1)`. **VG3-C4** an included file with `mode: unattended`, exit 3, `include:forbidden-section`; the seed with the mode on itself, exit 3, U2–U5 (H15). **VG3-C5** `(p1)` span counts cover the root-owned spans the walk visits today and included spans that name a root-declared document; a span on a root-owned operation is not counted, as today `(s2)`; an included span that names another document raises no U7 and is not counted; an included span that names a root-declared document and has `start >= end` exits 3 with U7 under `includes[ID]:`, with or without `--document` `(s3)` (D14). **VG3-C6** the attribution lines, in text output, name each include, its sha256 and the counts D5 lists; the JSON payload of the same run has no entry for them `(s3)`. **VG3-C7** a model without the mode, with or without includes, gives byte-identical `gnd validate` output (R0.3); one case is an include root without the mode `(p1)`. **VG3-C8** `(p1)` `remap_issues`, given an issue at `$.object_types[id=X]` where X came from an include, returns it under `includes[ID]:` (H17). This tests the function over a synthetic issue: with the exemption, no rule raises such an issue on a standalone-valid include. **VG3-C9** `(p1)` an include that holds a `proposed`, `llm-inferred`, `alethic` constraint, under the unattended root: exit 3, U8, under `includes[ID]:`; with the same constraint `confirmed` the root validates (D13 (a); D13 gives the (b) reading). **VG3-C10** `(p1)` the root of H30, which 0.4.0 validates: its exit, issues and span counts are what the base commit gives, the attribution lines are the only new text output, and its JSON payload is byte-identical `(s3)` (D14). **VG3-C11** `(s3)` an included span over a root-declared document whose `excerpt_sha256` is wrong: `gnd validate ROOT --document DOC` exits 3 with `unattended:excerpt-mismatch` at an address under `includes[ID]:`, in text and in JSON output (H37) | H25 if D3 is (b) |
| VG4 | **VG4-C1** a round on the VG3 root adds a root-owned fact type with spans and a constraint attached to an included fact type; preview, apply and finalize exit 0 and the result validates. **VG4-C2** an operation that modifies, renames or deletes an included element exits 3. **VG4-C3** a root with no documents and no owned element validates; its first round declares a document and adds an element. Each of these keeps U1 `(p1)`: a root with no documents that owns an object type; one that owns only a constraint attached to an included fact type; one that owns only an operation; and a root with no documents and no owned element whose `reviewer` is absent or is not `none`. So does each of these `(s2)`: a root with no documents that owns only a fact type; only a top-level constraint; only an operation that carries an obligation (an obligation exists only inside an operation); only a deontic note; only a `rejected_proposals` entry; only a `reference_populations` entry. So does an unattended model that declares no include, no document and no element `(s3)`. **VG4-C4** `repin-include` on an unattended root exits 3 with and without `--policy additive` (D6). **VG4-C5** `--check-population` and `--populated` behave on the root as on a model without includes | H23 |
| VG5 | **VG5-C1** the example's proposals rebuild byte-identically and its two rounds apply. **VG5-C2** the grown root passes `gnd validate --require-documents` with both documents, `gnd check` over the example population, and `gnd judgments check`. **VG5-C3** the route list names every route a test shows resolving an include root. **VG5-C4** the three replies are drafted and name what is on `main` and what is not released | H24 |

Each phase also runs the structure and inventory guards,
`uv run ruff check src tests tools`, an independent review of its diff, a
refactoring review and its record.

## 5. Documentation, skill and compatibility surfaces

- **One home each (R0.7).** U1's first-document rule, the include
  exemption, the statement about the pin and its limit `(p1)` go in
  "Unattended source". D-12's two new rows go in "Evolve
  admission (D-12)". `unattended-growth.md`, the evolution contract,
  `docs/agents/model-from-text.md` and `docs/agents/evolve.md` cite them.
- **Packaged skills.** `gnd-orm-core`, `gnd-model-evolve` and
  `gnd-model-from-text` reference files change; their manifests are held by
  `tests/test_packaged_skills.py`, in the guard block.
- **Release notes.** One entry per phase under the unreleased heading.
- **Compatibility.** VG1 changes no output. VG2 (a) and VG3 (a) admit inputs
  that 0.4.0 refuses and refuse nothing 0.4.0 admits. 0.4.0 does admit an
  unattended include root when every included element itself passes U2–U8
  against the root's documents (H30); r1 said it admits none, which was
  false `(p1)`. For such a root that validates, VG3 changes one thing, the
  attribution lines in the text output of `gnd validate`: its exit, span
  counts and JSON payload stay (D14, VG3-C10) `(s3)`. When the span walk
  refuses such a root, for a wrong excerpt say, it still does, and the
  address of the issue gains the `includes[ID]:` prefix (H37, VG3-C11)
  `(s3)`. VG4 under D6 refuses one input 0.4.0 admits on such a root,
  `repin-include` without the additive policy; the release notes name it.
  No schema version and no report variant changes (D5) `(s3)`.
- **Issue replies.** The close drafts them; the owner posts them.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| A cached table and the function it caches drift apart | VG1-C1, over every model that loads under `src/gnd/examples/` and `tests/fixtures/`, against frozen copies of the base bodies kept in the test `(p1)` |
| A time bound passes or fails with the machine, not with the code `(p1)` | the required regression gates read no clock: VG1-C7 counts map builds, VG1-C1 and VG1-C6 compare answers. The ratio (VG1-C4) compares two sizes in one test and takes the minimum of three runs per size (VG1 spec, VG1-D3) `(m)`. The absolute bounds (VG1-C2, C3, C5) do depend on the machine: 10 s is 7.7 times the slowest prototype figure (1.29 s, H29) and about 26 times under today's cost. They are judged on the machine that ran the base sweep and stay in the default lane as coarse guards. A miss there is a failed criterion, not a reason to raise the bound |
| The fix covers the measured shape and misses another | four shapes in VG1-C2 and VG1-C3, chosen from H4; fact types as the control (H5). The one shape known to stay slow is named, measured and out of scope (H4a, D12) |
| An include is trusted by its pin, not by proof of review. A host that can write both the root and an include can carry any claim, `confirmed` and `alethic` ones too `(p1)` | **A named limit, not a control.** GND checks an include's bytes against the pin and cannot know who wrote or reviewed them; "Unattended source" and the growth page say so. Three things narrow it. The root and its pins are the owner's, and a round cannot change a pin (D6). U8 still refuses an unconfirmed inferred `alethic` claim inside an include (D13, VG3-C9). The text output of `gnd validate` prints what each include carries: its element counts, and of its constraints how many are `confirmed`, how many `alethic` and how many `explicit` or `user-supplied` (D5). Those are counts; they do not list each element or each combination `(s2)`. An included fact type brings its sample rows with it: U6 asks nothing of them, and the line counts them `(s3)`. A host that reads only the JSON payload does not see the lines (D5) `(s3)`. D13 (b) is the stricter rule, if the owner wants one |
| A reader of a `gnd check` or `gnd judgments check` report cannot see that claims came through an include `(p1)` | a design choice: attribution is on `gnd validate`, the one route that enforces and reports the U rules. The other two reports already bind the include set: `gnd check` by the composed `model_digest`, and `gnd judgments check` by the root's sha256, which commits to every pin ("Model includes", route table). A line added there would change report bytes for every include root. The growth page names the command that shows the lines |
| A root that 0.4.0 validates changes its output `(p1)` | D14 (a) keeps its span walk; VG3-C10 pins its exit, issues and span counts |
| The exemption leaks to a root-owned element | VG3-C2 and VG3-C3: one root-owned case per rule U2–U8, two of them on an attached constraint (R0.4) `(p1)` |
| Two enforcement sites for the exemption (the rule walk and the span walk) disagree | one origin test shared by both; the VG3 spec names it (standing rule 4). D4's first-document test is read on the root's own document and agrees with it by construction (§2); VG4-C3 holds one case per section `(s3)` |
| Relaxing U1 lets a model with claims and no documents through | U1 stays whenever the model declares no include `(s3)`, or any section of the root other than its header and `includes` holds an entry (VG4-C3, one case per section `(s2)`); U4, U5 and U7 already refuse a root-owned span that names no declared document |
| D-12 widened too far | VG2-C2: four refusal cases, one per source and failing field |
| The example and its pages state behaviour the tests do not hold | VG5-C1 and VG5-C2 run the example; VG5-C3 reads the route list against live routes |
| Two milestones edit `evolve/service.py` and `unattended-growth.md` at once `(m)` | one writer at a time on each, in the roadmap's order (§3, H36) |

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
- The whole-repository ruff red (H27) and the stale lines of `project.md`,
  its lint-gate sentence among them `(p1)` (D11): owner policy, outside a
  phase. `(c2)` At the close the whole-repository command exits 0 (§11,
  amendment 4); the stale `project.md` lines stay the owner's.
- #226, #227 and #228 (literature-reading-reference, growth-round-outcomes)
  `(m)`.

## 8. Execution, approval and review protocol

- Default `auto=false`: the owner approves this plan, then each spec, before
  code. `process-milestone reviewed-vocabulary-growth` runs it; `auto` needs
  the owner's explicit delegation for this milestone.
- Plan review and close review: the project's bar is the maintained GND
  panel (`project.md`, "Plan-review bar"). For the plan review the owner
  selected the light panel on 2026-11-23 `(o)`; the close review's instrument
  is not selected (D8). Convergence follows the bounded rules. r1 planned
  one round, and a second only if the first blocked; the bullets below say
  what ran `(s3)`.
- Round 1 read r1 `(p1)`. Its 22 concerns are dispositioned in
  `evidence/plan-review-r1/disposition.md`: all reproduced, none rejected,
  two of them owner decisions (D13, D14). The panel's own triage calls three
  of them blocking, so r1's condition for a second round was met. The budget
  was two rounds, with this stop rule declared in r2 before round 2 ran:
  stop when more than half of a round's findings attack text the previous
  repair created.
- Round 2 read r2 on the owner's request and ended below quorum, exit 16:
  two of six seats succeeded, so it produced no panel result `(s2)`. The two
  reviews that returned raised four points, each reproduced
  (`evidence/plan-review-r2/disposition.md`), and r3 repairs them. All four
  attack text r2 created, which is over the stop rule's half, counted over
  two seats and not over a panel. Both rounds are spent and no third is
  planned. A new panel would be a new instrument run, and the owner's to
  ask for.
- The owner asked for one ("try again"). The third run read r3 and again
  ended below quorum, exit 16: two of six seats succeeded, three reached the
  600-second reviewer timeout and one returned no JSON `(s3)`. The two
  reviews raised eight points, none above medium, each reproduced
  (`evidence/plan-review-r3/disposition.md`). About five of the eight attack
  text a repair created, again over the stop rule's half, counted over two
  seats. The owner chose the repair over another run ("Repair to r4"), and
  r4 applies all eight. No review has read r4 and no further run is
  planned. Three runs gave one panel result: the plan comes to its gate
  with that result, two pairs of single reviews, and their repairs.
- The plan gate is recorded in `001-plan-gate.md` once the owner rules
  D1–D14 or amends them.
- Each phase: spec, owner gate, code, focused gates, one independent
  reviewer over the diff (the review helper, one reviewer in a different
  tool), refactoring review, record, commit.
- One pull request from the topic branch to `main`, or two if VG1 merges
  ahead of the rest (§3) `(m)`. Merge stays with the owner. Before the PR,
  `python3 scripts/components_index.py changed --base origin/main --strict`
  exits 0.

## 9. Per-phase verification

| Phase | Focused lane | Expected |
|---|---|---|
| VG1 | `uv run pytest -q tests/test_vg1_object_type_scaling.py tests/test_reference_universe.py tests/test_subtype_universe.py tests/test_public_semantic_adapter.py tests/test_tp1_index_scope.py tests/test_ir1_judgments_includes.py tests/test_rf1_semantic_pins.py --tb=short` | exit 0 |
| VG2 | `uv run pytest -q tests/test_vg2_evolve_sources.py tests/test_evolve_additive_policy.py tests/test_evolve_loading.py tests/test_unattended_growth_guidance.py tests/test_unattended_mode.py tests/test_induced_provenance.py --tb=short` | exit 0 |
| VG3 | `uv run pytest -q tests/test_vg3_unattended_includes.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py tests/test_mc1_model_includes.py tests/test_mc1_guards.py tests/test_include_root_close.py --tb=short` | exit 0 |
| VG4 | `uv run pytest -q tests/test_vg4_seeded_growth_rounds.py tests/test_mc3_evolution.py tests/test_evolve_source_document.py tests/test_evolve_additive_policy.py tests/test_evolve_population_check.py tests/test_unattended_model_growth_acceptance.py tests/test_unattended_mode.py tests/test_unattended_span_coverage.py --tb=short` | exit 0; the last two files added `(p1)` |
| VG5 | `uv run pytest -q tests/test_vg5_seeded_growth_example.py tests/test_growth_example.py tests/test_unattended_growth_guidance.py tests/test_ir1_judgments_includes.py --tb=short` | exit 0 |
| all | the structure and inventory guard block of `project.md`, and `uv run ruff check src tests tools` | exit 0 |

The lanes name files that exist at `4ad0d216` and at `c47dc126`, plus one
new file per phase.
Affected consumers are read again at each spec and may be widened there. No
broad lane (`-m "evidence or census"`) is selected. Whether VG1's ratio test
runs in the default lane or the `slow` lane is a VG1 spec decision (VG1-D3
proposes the default lane); the `slow` lane is opt-in (`pyproject.toml:79`)
and is not a gate unless the owner selects it. VG1-C7's call count runs in
the default lane whichever way that is ruled `(p1)`.

## 10. Owner decisions and open questions

All rows are proposals until the plan gate rules them, except the half of
D8 the owner has decided.

| ID | Question | Proposed |
|---|---|---|
| D1 | One milestone for #221, #218 and #222, or #222 alone with the other two as maintenance passes, as the roadmap (#218) and the include-root-routes close (#221, H9) first placed them | One milestone. The three serve one reporter and one workflow, and VG5's example needs all three. Cost: #221 and #218 wait for a plan gate they would not need as maintenance passes. If the owner prefers speed, VG1 and VG2 can run as maintenance passes from their specs unchanged |
| D2 | #218: (a) widen D-12 to admit `sample` and `common-sense` when `proposed` and `deontic`, or (b) change the growth document to say `llm-inferred` with the basis in `provenance.rationale_world_fact` | (a), as the maintenance README proposed. (b) hides the basis in free text and loses U5's span exemption for library evidence |
| D3 | #222: (a) an unattended root may include a reviewed model, with included elements exempt from U2–U6, from U7 as D14 rules `(s3)`, and from U8 as D13 rules `(p1)`, or (b) keep today's refusal and document the imported, proposed, deontic packaging as the supported route | (a). (b) makes reviewed constraints read as unreviewed in every grown model and needs a second, curated edition to restore them. A (b) ruling also needs a plan amendment before VG3 starts, because the VG3–VG5 predicates require the include (§3) `(s3)` |
| D4 | #222 case 3: (a) U1 admits no documents while the root declares at least one include `(s3)` and nothing else but its header (§2) `(p1)` `(s2)`; (b) `gnd evolve` alone admits such a root when the proposal's first operation is a `source-document` add, as the issue suggests; (c) document that the root is authored with its first document | (a): one rule in one place, and `gnd validate` and `gnd evolve` agree on the same root. (b) makes `gnd evolve` accept a model `gnd validate` refuses |
| D5 | VG3: what names the include of an included element under an unattended root | one `gnd validate` line per include (id, sha256, element counts with deontic notes `(s2)` and sample rows `(s3)`, and of its constraints the `confirmed`, `alethic` and `explicit` or `user-supplied` counts `(p1)`), and the `includes[ID]:` prefix on every diagnostic, the span walk's included (H37) `(s3)`. No line per element, and none on `gnd check` or `gnd judgments check` (§6) `(p1)`. Where the lines are carried `(s3)`: (a) text output only. The JSON payload is unchanged, because the `validate` payload is frozen (H38). A host that reads JSON does not see the lines; it does see the prefix, in each issue's `path`. (b) One `warnings` entry per include under a new rule id: both outputs carry it and no report variant changes, but every seeded root then reports warnings that nothing can clear. (c) A new payload field: a new report variant, which §5 excludes. Proposed: (a). The exact text is a VG3 spec decision |
| D6 | May a growth round re-pin an include of an unattended root | No: `gnd evolve` refuses `repin-include` on an unattended root with or without the additive policy. Alternative: keep today's rule (refused under the policy only) and say in the growth document that rounds run with it |
| D7 | Phase diff reviewer | the review helper (`.claude/skills/process-phase/scripts/review_tool.py`, subject `phase`), one reviewer in a different tool, as the last two milestones used |
| D8 | Plan review and close review instrument | Plan review: the GND panel light, selected by the owner on 2026-11-23 `(o)`; round 1 read r1, round 2 read r2 and returned no panel result `(s2)`, and a third run read r3 and returned none either `(s3)`. Close review: not selected; proposed, the same instrument |
| D9 | The witness oracle's own denotation walk (H10) | VG1 measures `gnd verify` at 1,000 extra types (VG1-C8 `(p1)`). If it is over the bound, VG1 gives that walk its own table, with no import from the checker; if not, it is recorded and left |
| D10 | `gnd judgments check` runs the checker twice (H7) | Out of scope; bounded at twice the check bound (VG1-C5) and recorded as a successor question |
| D11 | `project.md` says both that there is no component index and where it lives; it says the whole-repository `uv run ruff check` exits 0 (`:129-131`), and it exits 1 (H27) `(p1)`; 94 index descriptions are older than their code | The owner corrects `project.md` outside a phase. Until then every phase record and the close record name `uv run ruff check src tests tools` as the lint gate and cite this row `(p1)`. An index review (the `components` skill, Review mode) is offered, not required |
| D12 | A subtype chain hundreds of types deep stays slow after VG1 (H4a) | Out of scope: no reported vocabulary has one, and the fix is in `_resolve_reference`, which the loader and the type checks share. Recorded as a successor question with its numbers. Alternative: a sixth phase |
| D13 `(p1)` | What an include of an unattended root must be for its elements to be exempt. Composition proves the file valid, not reviewed (H31) | (a) The pin is the statement of review: the owner authors the root and its pins, a round cannot change them (D6), and the page names the limit (§6). U8 is kept for an included element that is not `confirmed`. The reporter's seed needs no change. (b) (a), and the included file must also say who reviewed it: `source.reviewer` with a value other than `none`, or the root is refused. The statement is then in the file and in the attribution line. It is still self-declared, the #222 seed needs one more line, and a root 0.4.0 validates (H30) is refused until its include names a reviewer; VG3-C9 then tests that refusal too. Proposed: (a) |
| D14 `(p1)` | A span an included element carries, under an unattended root (H30, H34) | (a) U4–U6 ask nothing of it. When it names a document the root declares it is treated as today: U7 requires it to be well-formed `(s3)`, and the span walk re-hashes and counts it. Otherwise no rule reads it and the walk ignores it. Every root 0.4.0 validates keeps its exit, issues and counts. (b) The walk covers root-owned spans only, as r1 said, and U7 asks nothing of an included span: one simpler rule, and the counts of a root 0.4.0 validates drop. Proposed: (a) |

Open questions carried into the specs: VG1, where the table lives and how it
treats a `Model` built in code whose rows `model_dump()` alters (the accepted
limit of the 2026-11-11 query-budget pass); VG3, whether the origin reaches
`_rule_unattended` as an argument, a context variable, or a filter over its
remapped issues, and the attribution lines' exact text `(p1)` (whether JSON
carries them was left to the spec in r3 and is now in D5 `(s3)`); VG4, how
the root's own document reaches U1 `(s3)`, and whether D6's refusal belongs
to the additive-policy table or to the mode. What U7 does with a span an
included element carries was an open question in r1; it is now D14 `(p1)`.

## 11. Amendments at the close `(c1)`

Written at the milestone close, 2026-11-23, from the phase records. Each row
names the record that raised it and keeps the r4 wording it amends. None
changes a goal predicate or a ruling of §10.

| # | Amends | r4 wording, kept | Amended | Raised by |
|---|---|---|---|---|
| 1 | §3, VG2 homes | "for (a): `src/gnd/evolve/service.py` (`_enforce_d12`), `provenance-and-modality.md` (D-12), `evolution-contract.md:279-280`, a new `tests/test_vg2_evolve_sources.py`, `tests/test_unattended_growth_guidance.py`, `docs/release-notes.md`" | adds `src/gnd/evolve/cli_service.py` (`_evolve_service_exit`: the refusal exits 3), `tests/test_induced_provenance.py` (IK2's D-12 table, an explicit eight-row delta), `tests/support/rf9_ci_sources.py` and `evidence/VG2/source-successors.json` (the RF5 successor) | `004-phase-VG2.md` |
| 2 | §3, VG3 homes | "`src/gnd/model/_unattended.py`, `src/gnd/model/__init__.py` (`_model_warnings`), `src/gnd/model/_includes.py` (`remap_issues`), `src/gnd/commands/checking.py`, `representation-format.md` (\"Unattended source\", \"Model includes\"), a new `tests/test_vg3_unattended_includes.py`, `tests/test_unattended_mode.py`, `tests/test_mc1_model_includes.py`, `docs/release-notes.md`" | adds `tests/vg3_cases.py` and `tests/fixtures/vg3/base-outputs.json`; `tests/support/rf9_ci_sources.py` and `evidence/VG3/source-successors.json` (the `_cmd_validate` successor); `tests/test_mc3_source_observations.py` (follows registered successors); `tests/test_unattended_span_coverage.py` (a13's fake) | `003-phase-VG3.md` |
| 3 | §2, VG5; §3, VG5 homes | "The route list of \"Model includes\" names every route that resolves an include root, `gnd coverage` and `gnd evolve` included (H24)"; homes "… `notes/issue-replies.md`" | the route list also names `gnd discover`; homes add `tests/test_mc1_guards.py` (R30, the packaged include roots), `tests/test_packaged_skills.py` (the skill link graph) and `tests/support/markdown_sections.py` | `006-phase-VG5.md` |
| 4 | §1, H27; §10, D11 | H27: "whole-repository `uv run ruff check` exits 1 with 198 errors" | at the close, `main` at `f7fad6a1`, the whole-repository command exits 0; the close records both commands. D11's other stale lines of `project.md` stay the owner's | the close gates |
| 5 | §2, VG1 | "Where the table lives is a VG1 spec decision; the proposal is `ModelIndex`" | the tables live on `ModelIndex` and are built from the canonical JSON form the cache key is a digest of, not from the cached rows (the cache can hold another model's rows); past the routed reader's 10 MB or 64-level caps they read the cached rows, as before VG1 `(c2)` | `002-phase-VG1.md`, refuted premise and boundary |
| 6 `(c2)` | §2, VG4, first-document bullet; §3, VG4 homes | §2: "The test is read on the root's own document, as authored, before composition merges the included elements into it. It cannot be read on the composed document, which the U rules read today (H16)"; §3: "`src/gnd/model/__init__.py` (the root's own document reaches U1)" | the test reads the composed document with VG3's origin set (`_owns_nothing`, `model/_unattended.py`), which equals the root's own document by the argument §2 gives (only included entries are appended to the merged sections; an attachment is the root's; an include declares no other section), measured by VG4 T3's per-section cases; `model/__init__.py` did not change for it | the close review (claude); `005-phase-VG4.md` |
| 7 `(c2)` | §5, Compatibility | "VG2 (a) and VG3 (a) admit inputs that 0.4.0 refuses and refuse nothing 0.4.0 admits" | also: since VG3, `remap_issues` maps `$.object_types[id=…]` for every include root, so an error on an included object type of a root without the mode would carry `includes[ID]:`; a standalone-valid include cannot carry such an error, and the exit is 3 either way. The span walk cannot raise an issue on an included element of a root without the mode, which declares no document | the close review (glm), reproduced in part |

