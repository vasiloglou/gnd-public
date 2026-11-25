# Phase SI1: seeded roots through flatten, extract and PyRel export (#292)

## 1. Status

**r3, owner-decided (2026-11-25), approved for implementation.** Written on 2026-11-25 against
main `f7ee3720`; r2 follows the [plan](seeded-routes-and-identifiers-plan.md)
r2 (its §11, A1, A4, A5, A8). No independent spec review was selected. The owner's D1 ruling and the
delegated spec ruling are recorded below.

## 2. Provenance

[#292](https://github.com/vasiloglou/gnd-public/issues/292), reproduced on
main (plan §1, "Measured before writing"); the normative section "An
unattended root that includes a reviewed model" and "Extraction flattening
record" of `src/gnd/skills/gnd-orm-core/references/representation-format.md`;
the reviewed-vocabulary-growth milestone, which made the exemption (VG3);
the include-root-routes milestone, which made the flat routes (IR2, IR3).

## 3. Obligations

| Row | Obligation | Source | Discharged in |
|---|---|---|---|
| SI1-C0 | E1's list of every route that loads an include root or flat bytes again | plan SI1-C0 | E1 |
| SI1-C1 | `gnd flatten` exits 3 with a named rule id for a model its re-entry refuses, never a traceback | #292; plan rule 2 | M1, T1 |
| SI1-C2 | plan predicate 1's (route, input) table, every cell tested | #292; plan predicate 1 | M2, M3, T2, T3, T5, T6 |
| SI1-C3 | plan predicate 2, rule by rule: the included element's exemptions (U8 when confirmed included), every rule for an owned element, and no exemption from input bytes | plan predicate 2 | T4, T5 |
| SI1-C4 | the guide and the normative text say what each route does with a seeded root | #292 "Expected"; plan §5 | M4 |
| SI1-C5 | a notes bullet under `Unreleased:` | plan §5 | M5 |
| R1 | a flat file must not let a host exempt its own elements | plan §6 | D1, T5 |
| R5 | not fitted to the packaged example | plan §6 | T3 |

## 4. Standing rules, bound to this phase

- The exemption has one home, `gnd.model._unattended`, keyed by
  `gnd.model._includes.included_rows` over the loader's origins. No second
  origin test is written.
- Its safety rests on the root's pin (normative text, last paragraph of the
  seeded-root section): GND checks the bytes against the pin. Anything that
  carries the exemption past the root must carry that binding with it.
- No regular expression over model text; documents are read as documents.

## 5. Goal

On the packaged `seeded_growth` root and on that root after its two rounds:
`gnd flatten` writes the flat model and its record (exit 0); `gnd extract`
and the three PyRel modes behave as they do for any include root; every
element the root owns is still checked by U1 to U8; and no route ends in a
traceback.

## 6. Design

### What happens today

`flatten_model` (`src/gnd/model/flattening.py`) serializes the composed model
without `includes` and re-loads those bytes to prove they reproduce it. The
re-entry is an unrooted load: it has no includes, so `included_rows` is empty
and U2 to U6 apply to the seed's elements. `extract`, `export pyrel` and
`flatten` all call `flatten_model`. `export.include_roots` and the extract
service catch the error and exit 3; `extract.flatten_service` catches only
`FlatteningError`, so `gnd flatten` lets `ModelValidationError` escape.

### E1 (before the ruling): where include roots and flat bytes are loaded

The SI1 spec's one measurement: every route that loads an include root, and
every place that loads a flat model again, in process or from a written file
(the CLI routes of the include route list, verbalization, evolve and shapes,
import, the export variants and both `--rules` modes), with what each does
today with a seeded root and what the normative text promises for it ("The
flat model is canonical JSON accepted by unrooted model-byte intake"). For
each: whether it has the root's resolved, pin-checked includes at hand. The
list is the row set of plan predicate 1's table and decides D1b's
detection.

#### E1 baseline, 2026-11-25

Measured at `99cf3df2` using the checkout's source on `PYTHONPATH` with the
existing development environment. The grown case applies the two packaged
proposals using the example README. The packaged check/discover population
contains the seed fact and roster only (removed the grown author fact,
roster and coverage entry from the packaged population).

Both flatten commands fail before writing. The candidate columns below use
the exact pre-re-entry bytes: `model_wire(load_model(root))`, dropping
`includes` and `fact_type_constraints`, then `canonical_json_bytes`.
Validate on a byte-identical renamed copy returned the same result for each
candidate. These are prospective bytes, before any flatten artifact exists.

| Command | Packaged root | Grown root | Packaged candidate flat bytes | Grown candidate flat bytes |
|---|---|---|---|---|
| `validate` | 0 | 0 | 3, U1–U5 | 3, U2–U5 |
| `check` | 0 | 0 | 3, U1–U5 | 3, U2–U5 |
| `flatten` | 1, traceback | 1, traceback | 3, U1–U5 | 3, U2–U5 |
| `extract` | 3, U1–U5 | 3, U2–U5 | 3, U1–U5 | 3, U2–U5 |
| `export pyrel` | 3, U1–U5 messages | 3, U2–U5 messages | 0 | 0 |
| `export pyrel --rules duckdb` | 3, U1–U5 messages | 3, U2–U5 messages | 3, U1–U5 messages | 3, U2–U5 messages |
| `export pyrel --rules lqp` | 3, U1–U5 messages | 3, U2–U5 messages | 3, U1–U5 messages | 3, U2–U5 messages |
| `verbalize model` | 0 | 0 | 3, U1–U5 | 3, U2–U5 |
| `coverage` | 0 | 0 | 3, U1–U5 | 3, U2–U5 |
| `discover` | 70, generated candidate fails U1 | 0 | 3 | 3 |

U1–U5 denote `semantic:unattended-u1` through `semantic:unattended-u5`.
The PyRel error text carries the issues' messages without their IDs. Grown
`validate --require-documents` with both documents and `judgments check` with
the shipped policy and receipts also exited 0. Both rounds' evolve preview
and apply exited 0.

Source-level route inventory supplements the command matrix:

| Route or intake | Root and pin context | Flat-byte behavior or boundary |
|---|---|---|
| Validate/check, compose, coverage, judgments check, discover, evolve preview/apply/finalize | Rooted model intake verifies pins. Discover also validates its generated candidate, and evolve validates authored candidates. Judgments binds before checking. | Ordinary validation consumes a standalone model without include context. The packaged discover failure is on a generated candidate that adds to a document-less root, independent of flattening. |
| Model and population verbalization, evolve shapes | Model verbalization loads the root directly. Population verbalization uses the model/population service. Evolve shapes compares the loaded model and candidate inside evolve. | No separate flatten re-entry. `shapes` is a service, not an evolve CLI verb. |
| Flatten, extract, verify | All three have the authenticated root when calling `flatten_model`. Verify also checks the derived flat/record pair against the extraction index. | All depend on flattening's internal reload. A valid seeded extraction bundle is unavailable on this baseline, so the verify row is a source observation. |
| Default PyRel | Export resolves and checks pins before flattening a root. | The emitter and generated runtime parse the bytes for their own structural admission, which explains its exit 0 on standalone candidate bytes. |
| DuckDB and LQP rule exporters | Both use the same pinned-root export path. | The rules renderer calls `load_model_bytes` again after flattening. Fixing only the first reload leaves both rule exporters refusing. |
| Rooted witness/replay, with or without a composition record | `resolved_projection` authenticates the root and derives the flat pair. An optional supplied pair is compared against those bytes. A witness probe exited 3 with `input-invalid` for each seeded root. | Witness subsequently calls `load_flat_model` for evaluation. Independent replay parses the projected bytes for certificate checking. Neither obtains authority from the supplied record. |
| Ossie and ILP exports, import adapters, standalone skill scripts, other guarded routes | These use their existing format or route guards. Ossie and why-not returned `include:unsupported-route` on both roots. | No path in these adapters obtains authenticated flat provenance from a standalone model. Keep their existing route boundaries. |

The wire keeps `source.mode: unattended` but carries no origin or ownership
field. A consumer of those bytes alone has no way to distinguish the same
bytes authored directly from bytes flattened from a reviewed seed. A file
suffix is only a naming convention. A flattening record can supply a caller
hint but cannot prove the exemption independently of resolving the root
and pins. D1b must account for this limitation. If D1 selects in-process
acceptance, the default PyRel command also needs an explicit admission
check at its standalone unattended input boundary to enforce the plan's
refusal predicate. Its generated runtime receives the already admitted
projection.

The E1 inventory extends the focused affected-consumer selection to
`tests/test_lx2_witness_flattening.py`, `tests/test_pyrel_export_boundaries.py`,
`tests/test_extract_cli.py`, and `tests/test_include_root_close.py` in
addition to T7. The expectations under the adopted D1 ruling follow below.

### D1: what a seeded root's flat form does

| Reading | What it does | Cost |
|---|---|---|
| (a) **in-process exemption** (proposed) | `flatten_model` re-enters the flat bytes with the root's origins and its owns-nothing state, so the re-entry check uses the same `included_rows` and the same U1 waiver the root's validation used (`_owns_nothing` answers false for a model without `includes`, so origins alone would leave U1 on the packaged root). `flatten`, `extract` and the PyRel exports accept the seeded root. The written flat file, loaded later on its own, has no pins: it is refused, under D1b | one parameter through the re-entry; the flat file of a seeded root is not standalone-loadable, which the normative text must say |
| (b) marker in the flat file | the flat model lists the addresses of included elements, and the unattended rules read it | an unrooted file then exempts whatever it lists: a host could exempt its own claims by writing the list (R1). Binding the list to the record's digests needs the record at load time, which is (a) with more format |
| (c) refuse by name | the three routes refuse a seeded unattended root with one named rule and the guide says so | keeps the 0.4.0 workaround (copy the seed into the root) for every host that grows from a seed |

**D1b, under (a): the written flat file of a seeded unattended root, loaded
on its own.** Proposed: one named refusal in place of today's U2 to U5 list,
for example `unattended:flat-without-root`, at `$.source`, saying the file is
the flat form of a root with reviewed includes and that the root is the file
to load. The normative text's "accepted by unrooted model-byte intake" gains
that exception. The alternative is to leave today's U2 to U5 list, which
names the seed's elements and reads like the host's error.

### Modules (under (a) and D1b as proposed)

| ID | Path | Change |
|---|---|---|
| M1 | `src/gnd/extract/flatten_service.py`, `src/gnd/commands/flatten.py` | a model `flatten_model` cannot re-enter is a refusal with exit 3 and the validation issues, as the other two routes already report it |
| M2 | `src/gnd/model/flattening.py`, `src/gnd/model/__init__.py`, `src/gnd/model/_unattended.py` | the re-entry validates with the root's origins and owns-nothing state; the loader's existing `_INCLUDED` context is set from `model._provenance`, through `included_rows`; nothing is read from the flat bytes to grant it |
| M3 | `src/gnd/model/_unattended.py` | D1b's named refusal for an unrooted load of a flat model whose record says it had reviewed includes, if E1 shows the flat file carries enough to know that; otherwise D1b is the normative sentence only. Whatever it reads can only turn today's U-rule list into this one refusal, never grant an exemption, so a forged signal costs the host nothing it could gain |
| M4 | `representation-format.md` (the two sections), `unattended-growth.md` (the include route list) | what each route does with a seeded root |
| M5 | `docs/release-notes.md` | a bullet under `Unreleased:` |

### Adopted design (o)

| Capability | Index searches and disposition |
|---|---|
| Root admission and flattening | `flatten model`, `resolved model flattening`, `unattended source`; adapt `model.loading` and `extract.flatten_service`. |
| PyRel admission | `PyRel export`, `flatten model`; adapt `export.include_roots`, `export.pyrel_emit` and `export.pyrel_rules`. |
| Rooted witnesses | `witness replay`, `witness flattening`; adapt the existing projection consumer in `witness.service`. |

`_model_warnings(doc, origins, *, flat_root=False)` uses the same
`included_rows` and validation order for a loader-derived projection.
Its private, reset-on-exit context lets `_owns_nothing` recognize a flat
projection of a root, with ownership evaluated from the projected elements.
`flatten_model` returns the reopened model with the unchanged canonical
flat and record bytes. Rules export and witness evaluation reuse that model.
The standalone default PyRel emitter additionally validates unattended input
with the GND model loader, before its usual profile admission.

**D1b diagnostic.** The byte stream has no distinguishing signal. When
unrooted unattended validation refuses and at least one error is from a rule
with a reviewed-include exemption, add the single named diagnostic
`unattended:flat-without-root` at `$.source`, directing callers to load the
root if this is a flattened seeded model. Preserve the underlying rule IDs
and paths for directly authored input. No input marker, path suffix or
adjacent record is interpreted as proof. Unrooted input that passes ordinary
validation is admitted as usual. A structural failure stays first.

**Expected route matrix.** For each packaged and twice-grown root,
`validate`, `check`, `flatten`, `extract` and the three PyRel modes exit 0.
For each written flat file loaded directly, the same seven routes exit 3 with
`unattended:flat-without-root`; repeat after renaming the file. A validation
refusal after flatten re-entry yields exit 3 with `flattening:re-entry` and
the originating diagnostics. Extraction verification and witness evaluation
with the root rederive the flat projection from the pins.

**Standing-rule and implementability sweep.** Existing bounded model
parsers are used at the intake and malformed input still goes through
structural validation before semantic rules. Ownership uses one existing
origin walk across element kinds. A large seeded projection gets a time-bound
control for the added validation work. The representation format owns the
policy, with a link from the guide. The E1 renamed-file and default PyRel
probes settle the contested detection and admission questions. No wire format
or model query changes, and this phase has no tag step. Existing reference
path coordinates and the independently checked witness/verify bindings
remain part of the contract.

## 7. Decisions

| ID | Question | Readings | Ruling |
|---|---|---|---|
| D1 | a seeded root's flat form | (a), (b), (c) above | (a), owner ruling 2026-11-25 (o) |
| D1b | the written flat file loaded on its own, under (a) | a named refusal, or today's U2 to U5 list | Named conditional diagnostic with the underlying rule IDs (o); see adopted design |
| D2 | the round budget for the review | one round, a second only over a repair, then stop | One diff review, a second only over a repair; no spec review |

Rulings are appended below this line, each with its date, source and the
SHA-256 of the spec bytes it covers.

## 8. Tests

| ID | Case | Expected |
|---|---|---|
| T1 | `gnd flatten` on the packaged seeded root on main; then, after M1, a re-entry refusal injected at `flatten_model`'s re-entry seam | today: exit 1 and a traceback (the regression is shown first); after M1: exit 3 and the named rule id for the injected refusal |
| T2 | the packaged seeded root: `flatten`, `extract`, `export pyrel`, `--rules duckdb`, `--rules lqp` | exit 0 each under (a) |
| T3 | a second seeded root built in the test: a different reviewed include, two includes, and an owned element with spans | exit 0 on each route |
| T4 | that root with an owned element missing its spans; and a reviewed include holding a confirmed alethic element from an otherwise restricted source | the first: each route refuses it with the owned element's U4 or U5 id, naming no seed element; the second: accepted on each route (U8 exemption kept) |
| T5 | the written flat file of the packaged and of the grown seeded root, given on its own to `gnd validate`, `gnd check`, `gnd extract` and the three PyRel modes; a flat file and a root edited to list an owned element as included | the flat file: D1b's named refusal on each route; the edited files: the owned element's U-rule ids on each route, never exempted |
| T6 | the grown root after both rounds | as T2 |
| T7 | every existing include-root and flattening test | unchanged: `tests/test_ir2_flatten.py tests/test_ir3_pyrel_includes.py tests/test_lx1_flattening.py tests/test_vg3_unattended_includes.py tests/test_vg4_seeded_growth_rounds.py tests/test_vg5_seeded_growth_example.py` |

### Verification selection

Focused: `tests/test_si1_seeded_routes.py` for T1 to T6, plus T7 and the structure guards of `project.md`. Impact closure:
every test file that loads an include root or a flat model. Broad: the full
default lane on beast-3 before the pull request. No opt-in lane.

### Implementability

- Every test has a command that can fail; T1 fails on main today.
- T5's edited-file case is the control for R1.
- E1 runs before the ruling; if it finds a route that loads the written flat
  file of a seeded root with no record at hand and must accept it, (a) needs
  a second look and the spec says so before any code.

## 9. Out of scope

- Unattended roots whose includes are themselves unattended (VG3 refuses
  them today).
- Temporal include roots: the existing route rules apply unchanged.

## 10. Size

Draft estimate: 40 production lines, 120 test lines and 20 documentation lines.
E1 found the second PyRel and witness reloads and the standalone PyRel admission
gap. Revised estimate: 80 production lines, 145 test lines and 20 documentation
lines. The twice-estimate stop rule applies to the revised estimate.

## 11. Approval instrument

This prose, E1's result, and the expected exit matrix above. Existing canonical
wire bytes give a comparison baseline. The new exit-3 diagnostic is pinned by
the matrix and the injected re-entry control; this phase proposes no new wire
format.

### Approval record

Owner decision (o), 2026-11-25, on E1 draft SHA-256 `02b304a94130036d7d6694d18586937a785328586b9f2703a20317806f5f7ef5`.
The owner's message in this chat approved D1: accept seeded roots in process
and give standalone flat files that need the exemptions a named refusal
directing users to load the root. The owner also renewed `auto=true`.

Delegated approval (auto=true), 2026-11-25. Approved SI1 r3 through the
previous paragraph, SHA-256 `3b38ff5baca25146b7817314a904243ef97c8541d43bcf2d62b0b8c9cc63897b`. Source: the owner's D1 ruling
and renewed milestone execution delegation in this chat. Scope: SI1 spec,
D1b implementation and compatibility, and focused verification. Instrument:
spec prose, E1 command results, and the route matrix. Budget: one independent
phase diff review via the project's review helper, a second only over a
repair. Optional spec review omitted. Owner merge and reserved milestone
decisions retain their own gates.

Scope clarification and instrument selection, 2026-11-25. The owner selected
Claude Code with Opus for the independent phase diffs in this milestone.
Start the helper through its existing Claude login. The rooted witness
producer and verifier also run a bounded structural intake. That reader
retains its existing checks and compares the model bytes it consumes against
the model already validated from the root and pins in the current invocation.
The witness/replay fixture exercises this path and the extraction verifier
rederives its bundle in the same fixture. The full default lane on beast-3
is a milestone close gate under plan §9. Per-phase verification uses the
focused default lane with the project's standing exclusions.

### Diff review amendments, 2026-11-25

F1: assign `flattening:re-entry` at the shared flat re-entry boundary,
so all five flat routes report the same event and publish no output. The
injected failure now runs on all five routes for both packaged and grown
inputs. F2: the normative paragraph names rooted witness and replay.
F3: the timing fixture projects 2,002 object types, 1,001 facts and
1,001 constraints within the existing 10-second ceiling.

The initial review helper run failed before receiving a brief because the
installed Claude Code consumed the prompt as an `--add-dir` value. A local
adapter passed only the brief pointer on stdin. One adapter invocation had
a shell arithmetic error and produced no review of the diff. The retained
run used the corrected adapter with the same model and read-only plan
mode. The review found three issues.

Delegated amendment (auto=true), 2026-11-25. Scope: the review repairs above
and their controls. Approved SI1 spec through the preceding paragraph at
SHA-256 `d245442b5b68f5f27015287043b57ecf4b7d727ef2aeeb8d4698dc30844467d7`; pre-amendment SHA-256 `c5907475b33e18e35e4b0d30d3ec276ee4dd8fcca8bf828775ab99344b749506`.
Source: renewed milestone delegation in the D1 message. Instrument: the
existing spec and discriminating regression cases. The review opinion
remains bound to its original bytes. The repairs are covered by the focused
gate, with one independent round and no second round requested.
