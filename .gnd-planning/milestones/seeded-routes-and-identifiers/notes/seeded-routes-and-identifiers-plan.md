# Seeded routes and identifiers

r2, 2026-11-25. Milestone `seeded-routes-and-identifiers`, phase prefix `SI`.
**r1 was read by the light GND panel (four of six seats, all "revise"; see
[the panel review](../evidence/plan-r1/PANEL-REVIEW.md)). r2 applies its
eleven fixes, listed in §11; no review has read the r2 bytes.** The plan
gate is recorded in [001](../001-plan-gate.md). It plans three open issues
and a tag-only release:

- [#292](https://github.com/vasiloglou/gnd-public/issues/292): an unattended
  root that includes a reviewed model validates, but `gnd flatten` ends in a
  traceback and `gnd extract` and `gnd export pyrel` refuse it.
- [#279](https://github.com/vasiloglou/gnd-public/issues/279):
  `refscheme.reference_identity` takes the first external uniqueness anchored
  on an entity, whatever its `preferred` flag, status or modality.
- [#280](https://github.com/vasiloglou/gnd-public/issues/280): the Ossie
  ontology export declares no identifier for a unit-based reference or a
  subtype with several supertypes, so the mapping cannot link those
  relationships.

Source: the owner's request of 2026-11-25 ("can we actually reopen and plan
them", then "can you also include 292?"), after the owner reopened #279 and
#280. Inspection baseline: main `f7ee3720`, the merge of the release-0.5.0
close. Plan authorship is not approval and not publication authority.

## Completion predicates

The milestone is complete when, on main after merge:

1. SI1's ruling fills one expectation table, (route, input) to (exit code,
   rule id or none), and a test checks every cell. The routes: `gnd flatten`,
   `gnd extract`, `gnd export pyrel` and both `--rules` modes, plus `gnd
   validate` and `gnd check` for the flat-file input. The inputs: the packaged
   `seeded_growth` root, that root after its two growth rounds, and the flat
   file `gnd flatten` writes for each. No cell is a traceback. `gnd flatten`
   reports the class of models its re-entry refuses (bytes the composition
   accepted and the re-entry did not) with exit 3 and a named rule id, shown
   by a test that injects such a refusal (SI1).
2. An element that came from a reviewed include keeps, on every route SI1's
   ruling admits, each exemption its home (`gnd.model._unattended`) grants it
   today, rule by rule: U2, U3 and U6 do not apply; U4 and U5 are replaced by
   U7 over the documents the root declares; U8 does not apply when the element
   is confirmed; and U1 waits for the first document while the root owns
   nothing. An element the root owns keeps every unattended rule. The
   exemption is computed only from the resolved, pin-checked includes;
   nothing in input bytes grants it, and a test in which a root or a flat file
   lists its own elements as included is refused on every route (SI1).
3. `refscheme.reference_identity` selects the identifier SI2's ruling names,
   judged on built fixtures that separate the readings (a first constraint
   that is not preferred; one preferred but not confirmed; one confirmed but
   deontic; two that qualify, with the tie rule stated), each failing first
   on main. Each caller whose result changes on a tracked model is listed
   before code with the models and entities it affects, and each change is
   either the ruling's intent or repaired. `reference_identity` adds no
   runtime query outside the counted budget (RC-04), as the existing counted
   guard shows (SI2).
4. The Ossie ontology export declares the identifiers SI3's ruling names. Every
   ontology whose bytes change is listed before code with its old and new
   digest; the pinned upstream validator and parser accept the new
   ontologies, and the round trip through `gnd import ossie` holds. The
   mapping's `identification-differs` rows go from 17 to 4 (the
   objectification rows, out of scope), each of the two classes checked on
   its own: the 8 unit-based rows and the 5 multi-supertype rows reach 0. The
   2 `concepts` rows, both objectifications, stay (SI3).
5. 0.5.2 is prepared as a GitHub tag only, under the procedure in
   `docs/releasing.md`. The tag is the owner's act, on the owner's word, and
   the close records it (SI4).
6. Each phase has an approved spec, a record with verbatim gate output and one
   independent reviewer in a different tool; the close has the light GND
   panel, a full default lane and a question sweep.

## 0. Binding design rules

1. AGENTS.md, "General solutions, not pattern-matched ones": each fix repairs
   the rule that failed, never the failing input by name. A matcher states its
   whole grammar.
2. A refusal is a named rule id with an exit code from the existing bands; a
   traceback is a defect (`project.md`).
3. Recorded bytes do not move silently. A phase that changes an exported
   document lists every changed file with old and new digests before code
   (corpus-first for SI3, whose output format changes).
4. The unattended rules' exemption for included elements has one home:
   `gnd.model._unattended` and the "An unattended root that includes a
   reviewed model" section of `representation-format.md`. No second copy.
5. Model queries go through `gnd.model_index.ModelIndex` where it has one; no
   new runtime query outside the counted budget (RC-04).
6. No phase uploads, tags or releases; SI4 prepares and the owner pushes.

## 1. Scope, sources and authority

### Obligations harvested

| Row | Obligation | Source | Phase |
|---|---|---|---|
| O1 | `gnd flatten` must not end in a traceback | #292, "Expected" | SI1 |
| O2 | the flat form of a root `gnd validate` accepts is accepted by `flatten`, `extract` and `export pyrel`, with included elements keeping their exemption, **or** the limit is a named refusal in the unattended-growth guide and the include route list | #292, "Expected" | SI1 (D1) |
| O3 | the reporter tested the packaged root before any round; the grown root is measured here (below) | #292 | SI1 |
| O4 | should `reference_identity` select as the Rmap does (preferred, confirmed alethic, functional)? which callers would see a different identifier, and is each a fix or a break? should the map be built once per model? | #279 | SI2 (D2) |
| O5 | declare `identify_by` for unit-based references and multi-supertype subtypes; it changes ontology bytes for existing models and needs its own spec and a round-trip decision | #280; ossie-relational-bundle close, OB3-Q5 | SI3 (D3) |
| O6 | a tag-only 0.5.2 | the owner's answer, 2026-11-25 | SI4 |
| O7 | the light GND panel for the plan and the close; delegated approval of plan and specs; the owner decides merges and the decisions the specs leave to the owner | the owner's answers, 2026-11-25 | §8 |
| O8 | 98 component-index entries are older than their code (`components_index.py review`) | this plan's harvest | §7: offered, not in scope |

### Measured before writing (inspection, not a phase gate)

**#292**, on a copy of the packaged `seeded_growth` example at main
`f7ee3720`:

| Command | As packaged | After the two growth rounds |
|---|---|---|
| `gnd validate root.orm.yaml` (with both documents and `--require-documents` after the rounds) | exit 0 | exit 0 |
| `gnd flatten root.orm.yaml --out flat` | exit 1, `ModelValidationError` traceback from `flatten_model`'s re-entry | exit 1, the same traceback |
| `gnd extract root.orm.yaml --out ex` | exit 3, U1 to U5 | exit 3, U2 to U5 |
| `gnd export pyrel`, default and both `--rules` modes | exit 3, the same list | exit 3, U2 to U5 |

The rounds remove U1 (the root then declares documents). U2 to U5 remain and
name only the seed's elements. Cause, from the code: the exemption is the
context `_INCLUDED` set by the include loader while it validates the root;
`flatten_model` drops `includes` from the wire and re-loads the flat bytes,
and the re-entry has no includes, so every element is the root's own.

U1 on the packaged root has the same cause (r2, from the panel): a root that
owns nothing may wait for its first document, and `_owns_nothing`
(`_unattended.py`) answers false for a model without `includes`. Passing the
origins into the re-entry is therefore not enough; the re-entry must also
know that the root owns nothing. The rules and what an included element is
spared, from `_rule_unattended`: U1 (documents declared, waived while the
root owns nothing), U2 (no confirmed status), U3 (no human source), U4 and
U5 (spans on object types, fact types and constraints), U6 (spans on sample
rows), U7 (span shape), U8 (no unreviewed alethic). An included element skips
U2, U3 and U6, has U4 and U5 replaced by U7 over the root's documents, and
skips U8 when it is confirmed.

**#279**, over the 436 loadable models tracked in the repository: 9 entities
have a composite `reference_identity`. For 3 of them the Rmap selects no
composite identifier, where `reference_identity` returns one: `assertion` in
the literature `assertions` and `lineage` models (an objectification the Rmap
keys by its own fact type) and `task` in the
`reference_scheme_elicitation` skill example (a component not functional on
the entity). Each of the 9 has exactly one external uniqueness anchored on
it, and that one is preferred, confirmed and alethic. So the case #279 names,
a first constraint that is not the preferred one, occurs in no tracked model;
the 3 differences come from the Rmap's further conditions (components
functional on the entity; an objectification keyed by its own fact type),
not from `preferred` or confirmation. Callers: the model verbalization, the extraction vocabulary,
the fact-type applicability table (`refscheme`), `entity_reference` (used by
`evolve/shapes.py` and `extract/guidelines.py`).

**#280**, over the 410 models the Ossie export maps: `unmapped_links` lists 17
fact types with `identification-differs` in 13 models, and `concepts` lists 2.
The issue counted 16 in 14 on an earlier main. 10 entities in 10 models have
a unit-based reference; 7 subtypes in 7 models have more than one supertype.
The normative text names a third cause, an objectification keyed by its own
fact type, which #280 does not ask to change.

Split by cause (r2, from the panel; the cause is that of the role player the
mapping cannot identify, measured with
[cause280.py](../evidence/plan-r1/cause280.py)):

| Cause | `unmapped_links` rows | Models | `concepts` rows |
|---|---|---|---|
| unit-based reference | 8 | 8 | 0 |
| subtype with several supertypes | 5 | 3 | 0 |
| objectification keyed by its own fact type (out of scope) | 4 | 2 | 2 |

In all 7 subtypes with several supertypes, the supertypes carry different
identifiers (each its own `popular` reference), so a rule for supertypes that
agree would cover none of them. The normative text already says which one
applies: an inheriting subtype "is identified as its first supertype is,
composite included" (`representation-format.md`, the Rmap's identification
table).

### Conflicting clauses

- **C1 (#292, O2).** The issue offers two outcomes: accept with the
  exemption, or refuse by name and document the limit. They are different
  products. D1 chooses; §2 proposes accepting.
- **C2 (#279).** Selecting as the Rmap does would make `reference_identity`
  return no composite for the 3 measured entities, changing the verbalization
  and the extraction vocabulary of three shipped examples. That is the break
  the Ossie milestone declined to make inside its own scope (record 022).

## 2. Contract proposal and product behavior

- **SI1, #292 (proposal for D1: accept, in process only).** The routes that
  flatten a seeded root themselves (`flatten`, `extract`, the three PyRel
  modes) keep the exemption while they do it: the re-entry of the flat bytes
  is validated with the origins and the owns-nothing state the root's own
  validation computed from its resolved, pin-checked includes. Nothing is
  written into the flat model to say what was included, and nothing read
  from input bytes grants the exemption. The flat file such a route writes,
  given later as an input on its own, has no pins to check, so it gets one
  named refusal that says to load the root (O2's second branch, for that
  input only). r1 proposed a list of included addresses in the flat model;
  the panel found that a host can write that list, and its digests, itself
  (§11, A1). Whatever D1 decides, `gnd flatten` reports a model it cannot
  flatten with exit 3 and a named rule id. The alternative reading (refuse by
  name) keeps the 0.4.0 workaround and adds one refusal and one sentence to
  the guide.
- **SI2, #279 (no proposal yet; D2).** Three readings: (a) select as the Rmap
  does, accepting the measured changes in three shipped examples; (b) keep
  the first declared, document it, and build the value-type map once per
  model; (c) select the preferred confirmed alethic constraint when one
  exists and fall back to the first otherwise, which changes none of the 9
  measured entities (each has one anchored constraint, already preferred,
  confirmed and alethic). Under (c) the issue's case is fixed for models that
  have it, and no tracked model does; the spec builds such a model to test
  it. The spec measures each reading per caller.
- **SI3, #280 (D3).** The ontology declares `identify_by` for a unit-based
  reference (a value relationship to its measure) and, for an inheriting
  subtype with several supertypes, the identifier of its first supertype, as
  the normative text already identifies it (r1 said "when the supertypes
  agree", which covers none of the 7 measured subtypes; §11, A6). A subtype
  that does not inherit its reference is unchanged, and a test shows it.
  The ontology bytes of the affected models change; the spec is corpus-first
  and lists each changed ontology with its digests, and the round trip
  through `gnd import ossie` and the sidecar is decided there.
- **SI4.** 0.5.2 tag-only: the five version fields, `TAGGED`, a notes section
  with the install-from-tag command, the tag sentence in two paragraphs; the
  install pins stay at 0.5.0.

## 3. Dependencies and artifact homes

```
SI1 ─┐
SI2 ─┼──> SI4 ──> close
SI3 ─┘
```

SI1, SI2 and SI3 touch different modules and can run in any order. D2 cannot
change the ontology bytes SI3 approves: the Ossie export selects its
composite identifier in its own code (`export/ossie.py`, `_add_references`,
which already prefers a `preferred` constraint) and never calls
`reference_identity`. The SI3 spec checks this again before its corpus is
approved.

| Artifact | Home |
|---|---|
| unattended exemption | `src/gnd/model/_unattended.py`; `representation-format.md`, "An unattended root that includes a reviewed model" |
| flattening | `src/gnd/model/flattening.py`; `extract.flatten_service`; `export.include_roots` |
| reference identity | `src/gnd/refscheme.py` |
| Ossie ontology identifiers | `src/gnd/export/ossie.py`; `representation-format.md`, the Ossie projection table |
| guide | `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` |
| include route list | `representation-format.md`, "Model includes (version 5)", the table of CLI routes that resolve an include root |
| release | `pyproject.toml` and the files `docs/releasing.md` names |

## 4. Phases

### SI1: seeded roots through flatten, extract and PyRel export (#292)

- SI1-C0: the spec's E1 lists every route that loads an include root or
  loads flat bytes again, in process or from a written file, with what each
  does today with a seeded root; predicate 1's table ranges over that list.
- SI1-C1: `gnd flatten` exits 3 with a named rule id for a model its re-entry
  refuses; a test reproduces today's traceback first, and a second test
  injects a re-entry refusal after the fix.
- SI1-C2: predicate 1's table, each cell with a test.
- SI1-C3: predicate 2, rule by rule; a root element without spans is still
  refused with U4 or U5; a reviewed include with a confirmed alethic element
  keeps its U8 exemption; a root or flat file that lists its own elements as
  included is refused on every route.
- SI1-C4: the guide and the include route list say what each route does with
  a seeded root.
- SI1-C5: the notes bullet under `Unreleased:`.

### SI2: reference identity selection (#279)

- SI2-C1: the spec measures D2's three readings per caller over the tracked
  models and over the built fixtures of predicate 3 before the ruling.
- SI2-C2: the ruled reading, with a test per changed caller and the old
  behaviour pinned where it stays; the fixtures fail first on main.
- SI2-C3: if the ruling keeps per-call map building, the reason is stated;
  otherwise the map is built once per model through `ModelIndex`. Either
  way, the counted-budget guard (RC-04) passes unchanged.

### SI3: Ossie identifiers for unit-based references and multi-supertype subtypes (#280)

- SI3-C1: corpus-first: the expected ontology bytes for each affected model,
  approved before code.
- SI3-C2: the export writes them; the pinned validator and parser accept them
  (`ossie_oracle`, on the owner's selection at the spec).
- SI3-C3: `gnd import ossie` restores each changed model as before.
- SI3-C4: predicate 4's counts, each class on its own; the normative text and
  `docs/explanation/ossie.md` say what changed.

### SI4: 0.5.2 as a GitHub tag only

- SI4-C1: the tag-only procedure; `tools/release_text.py check` exits 0.
  SI4 is complete on this. The tag `v0.5.2` on the merge commit is the
  owner's act, on the owner's word, and the close records it (r1 listed it as
  SI4-C2; §11, A10).

### Milestone close

The light GND panel over a close candidate, a full default lane on beast-3, a
question sweep and a close record with a delegated ruling.

### Obligation-to-phase map

| Obligation | Phase | Predicate |
|---|---|---|
| O1, O2, O3 | SI1 | 1, 2 |
| O4 | SI2 | 3 |
| O5 | SI3 | 4 |
| O6 | SI4 | 5 |
| O7 | all | 6 |

## 5. Documentation, skill and compatibility surfaces

- `representation-format.md`: the seeded-root section (SI1), the Ossie
  projection table and the `identification-differs` paragraph (SI3).
- `unattended-growth.md`: what the routes do with a seeded root (SI1).
- `docs/explanation/ossie.md` (SI3).
- `docs/release-notes.md`: one bullet per phase under `Unreleased:`, folded
  into the 0.5.2 section at SI4.
- Compatibility: SI3 changes exported ontology bytes; SI2 may change the
  verbalization and extraction vocabulary of three shipped examples. Each is
  stated in the notes as a change a script could notice.

## 6. Risks and required controls

| Risk | Control |
|---|---|
| R1: an unattended host exempts its own elements | the exemption is computed only in process, from includes resolved and checked against their pins in the same run; no marker is written and nothing in input bytes, the flattening record included, grants it (a host can write a list and recompute its digests). Tests: a root and a flat file that list their own elements as included are refused on every route (predicate 2). r1 also allowed binding a marker to the record's digests; withdrawn (§11, A1) |
| R2: SI2 changes shipped verbalizations unannounced | the per-caller measurement before the ruling; a notes bullet |
| R3: SI3's new `identify_by` is rejected upstream | the pinned validator and parser on every changed ontology (SI3-C2) |
| R4: SI3's ontology change breaks the sidecar binding of existing exports | the round trip (SI3-C3); old ontologies stay importable |
| R5: a fix fitted to the `seeded_growth` example | a second seeded root built in the test, with a different include and an owned element |

## 7. Out of scope

- An objectification keyed by its own fact type (the third
  `identification-differs` cause), which #280 does not ask for.
- The 98 stale component-index entries: a review of the index is offered to
  the owner and is not part of this milestone.
- PyPI: 0.5.2 is a tag only.

## 8. Execution, approval and review protocol

- Approvals: the owner delegated plan and spec approval for this milestone on
  2026-11-25 ("Delegate"). Each ruling is recorded as a delegated approval
  with the digest of the bytes it covers and is never described as the
  owner's reading. D1 and D3 are put to the owner, and D2 is when the ruled
  reading changes a shipped example.
- Plan and close review: the light GND panel, the owner's choice of
  2026-11-25.
- Phase diffs: one independent reviewer in a different tool through the review
  helper; the round budget is declared in the spec before round 2.
- Merges and the tag: only on the owner's word.

## 9. Per-phase verification story

| Phase | Focused gate | Affected consumers |
|---|---|---|
| SI1 | the new SI1 tests; `tests/test_vg3_unattended_includes.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_lx1_flattening.py`; the structure guards | every test file that loads include roots |
| SI2 | the SI2 tests; the verbalization, vocabulary and applicability tests the measurement names | the three shipped examples' recorded outputs |
| SI3 | the SI3 tests; `tests/test_ossie_export.py tests/test_ossie_import.py tests/test_ossie_relational.py tests/test_ossie_docs.py`; `ossie_oracle` on the owner's selection | every recorded Ossie ontology |
| SI4 | `tests/test_release_version.py tests/test_release_text.py tests/test_release_docs.py`; `release_text.py check` | -- |
| close | full default lane, six shards on beast-3 | whole suite |

None of these has run. The measurements in §1 are inspection.

## 10. Owner decisions and open questions

| ID | Question | Proposal | Cost of the other reading |
|---|---|---|---|
| D0 | Plan and close review | the light GND panel (**the owner's choice**) | -- |
| D1 | #292: accept a seeded root's flat form with the exemption, or refuse it by name? | accept, in process only: `flatten`, `extract` and the PyRel modes accept the seeded root; the flat file they write, given on its own, gets one named refusal that says to load the root | refusing keeps the 0.4.0 workaround for every host that grows from a seed; a marker in the flat file (r1's mechanism) lets a host exempt its own claims |
| D2 | #279: which identifier does `reference_identity` select? | ruled at the SI2 spec, after the per-caller and fixture measurement; put to the owner if the ruled reading changes a shipped example | (a) as the Rmap: changes the verbalization and extraction vocabulary of three shipped examples, the break record 022 declined; (b) first declared: no change, the #279 case stays unfixed; (c) preferred confirmed alethic, else first: no tracked model changes, shown only on built fixtures |
| D3 | #280: declare the identifiers, and how the round trip treats them | declare them, corpus-first; for several supertypes, the first supertype's, as the normative text says | not declaring leaves 13 links unmapped in 11 models (8 unit-based, 5 multi-supertype) |
| D4 | Release | 0.5.2 tag-only (**the owner's choice**) | -- |
| D5 | Phase order | SI1 first (a defect a user reported), then SI2, SI3, SI4 | -- |

Open questions carried: none beyond the rows above.

## 11. Amendments of r2 (2026-11-25, from the r1 plan panel)

The light GND panel read r1 (SHA-256
`3bd8904535d1d5cfbbe387e14c183235112c0edf21cabee2b80618e9c6923f1f`,
committed at `d316b119`): four of six seats, every one "revise". Its review,
synthesis and the disposition of each concern are in
[evidence/plan-r1](../evidence/plan-r1/). r1's wording stays in git at that
commit; each row below says what r2 changed and where.

| Row | Panel fix | Change in r2 | Where |
|---|---|---|---|
| A1 | `fix-si1-marker-trust` (all four seats) | the flat-model marker and the digest-binding control are withdrawn; the exemption is computed only in process from the pin-checked includes; the written flat file, given on its own, gets one named refusal | §2 SI1, R1, D1, predicate 2 |
| A2 | `fix-si3-count-by-cause` (all four) | the 17 rows split by cause: 8 unit-based, 5 multi-supertype, 4 objectification; predicate 4 becomes 17 to 4, each class checked on its own; D3's cost is 13 links in 11 models | §1, predicate 4, SI3-C4, D3 |
| A3 | `fix-d2-readings-costs` (all four) | D2 carries the three readings and the cost of each | D2 |
| A4 | `fix-si1-route-expectations` (Claude, Qwen, GLM) | predicate 1 is a (route, input) table including the written flat file; §1 records that U1 also depends on the includes; SI1-C1 names its class and an injected test | predicate 1, §1, SI1-C0 to C2 |
| A5 | `fix-si1-exemption-band` (Codex, Qwen) | predicate 2 lists the exemption rule by rule, U8 included; §1 records the band | predicate 2, §1, SI1-C3 |
| A6 | `fix-si3-disagreeing-supertypes` (Claude, Qwen) | measured: the supertypes disagree in all 7; SI3 uses the first supertype, as the normative text does | §1, §2 SI3, D3 |
| A7 | `fix-si2-reading-c-vacuous-predicate` (Qwen) | SI2 is judged on built fixtures that separate the readings, failing first | predicate 3, SI2-C1, SI2-C2 |
| A8 | `fix-include-route-list-unhomed` (Qwen) | the route list has a home; E1 lists every route that loads an include root or flat bytes | §3, SI1-C0 |
| A9 | `fix-si2-si3-corpus-approval-order` (Qwen) | §3 says why D2 cannot change SI3's ontology bytes | §3 |
| A10 | `fix-si4-c2-owner-gated-criterion` (Qwen) | the tag leaves SI4's criteria and is recorded at the close | predicate 5, SI4 |
| A11 | `fix-o4-map-budget-no-predicate` (Qwen) | O4's map question gets a predicate: no runtime query outside RC-04 | predicate 3, SI2-C3 |

No row changes a decision the owner made (D0, D4) or the phase list.

## 12. Close amendments (2026-11-25)

The wording above remains the approved r2 baseline. These amendments record
the phase measurements against it.

| Prior premise and location | Measured correction | Raising record |
|---|---|---|
| §2, D1: “The flat file such a route writes, given later as an input on its own, has no pins to check, so it gets one named refusal that says to load the root”. | The original bytes and a renamed copy show that a standalone file has no authenticated origin. The named `unattended:flat-without-root` hint accompanies include-sensitive unattended validation failures, including a standalone input that needs the root's reviewed-include exemptions. The message is conditional and preserves the underlying diagnostics. Valid standalone input follows ordinary route rules, including the include declaration required by `flatten`. The approved D1b table still expects exit 3 and the named hint for all seven routes on both seeded projections. | [002-phase-SI1.md](../002-phase-SI1.md), Open questions and Boundary |
| §1, C2: “Selecting as the Rmap does would make `reference_identity` return no composite for the 3 measured entities, changing the verbalization and the extraction vocabulary of three shipped examples.” §2 and D2 repeated the three-example count. The verification targets in §5 and §9 inherited that focus. | The alternative changes 13 entities in 9 models. It removes three existing composite identities and adds ten previously uncounted composite identities. Reading C, the ruled preference for confirmed alethic external uniqueness with a first-declared fallback, leaves the measured identities of all 436 admitted tracked models unchanged. | [003-phase-SI2.md](../003-phase-SI2.md), Open questions and Boundary |
| §1, #280: “over the 410 models the Ossie export maps”. | The same 410 paths satisfy the mapping census through the tagged merge. The 414 admitted ontology-only exports include four unchanged models excluded by that census's source or mapping admission. The 17 changed ontology paths and 13 targeted mapping rows measure distinct output units. | [004-phase-SI3.md](../004-phase-SI3.md), Claim and Mapping census, and the [close census](../evidence/close/ossie-corpus-reconciliation.json) |

SI1's re-entry audit also refuted the baseline assumption that every
standalone PyRel mode refused the seeded flat candidate. Baseline default
PyRel's structural intake exported that candidate. The [SI1 spec](phase-SI1-spec.md)
retains the measured before and after route matrices, including both growth
rounds. The approved criteria continue to apply to the final routes.
