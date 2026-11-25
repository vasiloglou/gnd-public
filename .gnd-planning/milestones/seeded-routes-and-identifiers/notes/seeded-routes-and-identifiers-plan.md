# Seeded routes and identifiers

r1, 2026-11-25. Milestone `seeded-routes-and-identifiers`, phase prefix `SI`.
**Draft. No review has read it, and it has no ruling.** It plans three open
issues and a tag-only release:

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

1. On a copy of the packaged `seeded_growth` example, before and after its two
   growth rounds, `gnd flatten`, `gnd extract`, `gnd export pyrel` and both
   `--rules` modes give the result SI1's ruling names for each route, with an
   exit code and a named rule id. No route ends in a traceback; `gnd flatten`
   on any model it cannot flatten exits 3 with a named refusal (SI1).
2. An element that came from a reviewed include keeps the exemption from U2
   to U6 on every route SI1's ruling admits, and an element the root owns
   keeps every unattended rule there (SI1).
3. `refscheme.reference_identity` selects the identifier SI2's ruling names.
   Each caller whose result changes is listed before code with the measured
   models and entities it affects, and each change is either the ruling's
   intent or repaired (SI2).
4. The Ossie ontology export declares the identifiers SI3's ruling names. Every
   ontology whose bytes change is listed before code with its old and new
   digest; the pinned upstream validator and parser accept the new
   ontologies, the round trip through `gnd import ossie` holds, and the
   mapping's `identification-differs` rows fall by the measured count (SI3).
5. 0.5.2 is prepared as a GitHub tag only, under the procedure in
   `docs/releasing.md`, and the tag waits for the owner's word (SI4).
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

### Conflicting clauses

- **C1 (#292, O2).** The issue offers two outcomes: accept with the
  exemption, or refuse by name and document the limit. They are different
  products. D1 chooses; §2 proposes accepting.
- **C2 (#279).** Selecting as the Rmap does would make `reference_identity`
  return no composite for the 3 measured entities, changing the verbalization
  and the extraction vocabulary of three shipped examples. That is the break
  the Ossie milestone declined to make inside its own scope (record 022).

## 2. Contract proposal and product behavior

- **SI1, #292 (proposal for D1: accept).** The flat form of a seeded root
  keeps the exemption. Proposed mechanism, to be measured in the SI1 spec
  before code: the flat model records which elements came from a reviewed
  include, as one top-level list of element addresses, and the unattended
  rules read it as they read `_INCLUDED` today; the flattening record's
  `origins` already holds the same addresses. `gnd flatten`, `gnd extract`
  and `gnd export pyrel` then accept the packaged root and the grown root.
  Whatever D1 decides, `gnd flatten` reports a model it cannot flatten with
  exit 3 and a named rule id. The alternative reading (refuse by name) keeps
  the 0.4.0 workaround and adds one refusal and one sentence to the guide.
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
  reference (a value relationship to its measure) and, for a subtype with
  several supertypes, the identifier it inherits when the supertypes agree.
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

SI1, SI2 and SI3 touch different modules and can run in any order; SI3 reads
SI2's ruling only if D2 changes how the Ossie export identifies an entity,
which the SI3 spec checks.

| Artifact | Home |
|---|---|
| unattended exemption | `src/gnd/model/_unattended.py`; `representation-format.md`, "An unattended root that includes a reviewed model" |
| flattening | `src/gnd/model/flattening.py`; `extract.flatten_service`; `export.include_roots` |
| reference identity | `src/gnd/refscheme.py` |
| Ossie ontology identifiers | `src/gnd/export/ossie.py`; `representation-format.md`, the Ossie projection table |
| guide | `src/gnd/skills/gnd-model-from-text/references/unattended-growth.md` |
| release | `pyproject.toml` and the files `docs/releasing.md` names |

## 4. Phases

### SI1: seeded roots through flatten, extract and PyRel export (#292)

- SI1-C1: `gnd flatten` exits 3 with a named rule id for every model it
  cannot flatten; a test reproduces today's traceback first.
- SI1-C2: D1's outcome on the packaged and the grown `seeded_growth` root, for
  `flatten`, `extract` and the three PyRel modes, each with a test.
- SI1-C3: an element the root owns keeps every unattended rule on those
  routes; a root element without spans is still refused.
- SI1-C4: the guide and the include route list say what each route does with
  a seeded root.
- SI1-C5: the notes bullet under `Unreleased:`.

### SI2: reference identity selection (#279)

- SI2-C1: the spec measures D2's three readings per caller over the tracked
  models before the ruling.
- SI2-C2: the ruled reading, with a test per changed caller and the old
  behaviour pinned where it stays.
- SI2-C3: if the ruling keeps per-call map building, the reason is stated;
  otherwise the map is built once per model through `ModelIndex`.

### SI3: Ossie identifiers for unit-based references and multi-supertype subtypes (#280)

- SI3-C1: corpus-first: the expected ontology bytes for each affected model,
  approved before code.
- SI3-C2: the export writes them; the pinned validator and parser accept them
  (`ossie_oracle`, on the owner's selection at the spec).
- SI3-C3: `gnd import ossie` restores each changed model as before.
- SI3-C4: the `identification-differs` count falls by what the corpus shows;
  the normative text and `docs/explanation/ossie.md` say what changed.

### SI4: 0.5.2 as a GitHub tag only

- SI4-C1: the tag-only procedure; `tools/release_text.py check` exits 0.
- SI4-C2: the tag `v0.5.2` on the merge commit, on the owner's word.

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
| R1: SI1's marker lets a host exempt its own elements by writing the marker into a flat file | the exemption is honoured only on the routes that produce the flat bytes from the pinned root in-process, or the marker is bound to the flattening record's digests; the spec decides and tests a forged marker |
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
  owner's reading. Decisions D1 to D3 are put to the owner.
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
| D1 | #292: accept a seeded root's flat form with the exemption, or refuse it by name? | accept, with the mechanism the SI1 spec measures | refusing keeps the 0.4.0 workaround for every host that grows from a seed |
| D2 | #279: which identifier does `reference_identity` select? | decided at the SI2 spec, after the per-caller measurement | -- |
| D3 | #280: declare the identifiers, and how the round trip treats them | declare them, corpus-first | not declaring leaves 17 links unmapped |
| D4 | Release | 0.5.2 tag-only (**the owner's choice**) | -- |
| D5 | Phase order | SI1 first (a defect a user reported), then SI2, SI3, SI4 | -- |

Open questions carried: none beyond the rows above.
